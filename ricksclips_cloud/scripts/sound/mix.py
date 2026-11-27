"""Make the full soundtrack: final voice + generated music bed + generated sound effects.

Usage:  python -m sound.mix <sound.json> <final_voice.wav> <out_dir>
        (run from the plugin's scripts/ folder, or: python <plugin>/scripts/make_sound.py ...)

sound.json
{
  "seed": 7,
  "music": { "mood": "curious", "sections": [ {"t": 0, "mood": "curious", "energy": 0.5}, ... ], "under_voice_db": 8 },
  "sfx":   [ {"t": 1.20, "kind": "whoosh", "gain_db": 0}, {"t": 3.05, "kind": "pop", "pitch": 1.2}, ... ],
  "tail": 0.25
}
Times are seconds on the final voice timeline (the same clock as words.json and the picture).
Output: mix.wav (48 kHz stereo, exact length), stems/voice.wav, stems/music.wav, stems/sfx.wav, sound_report.json
Targets: integrated -14.5 LUFS, true peak <= -1.0 dBTP, music+sfx 5-10 dB under the voice overall, the
music never closer than 6 dB to the voice in any 400 ms window where the voice speaks (voice always on top),
sound effects at least 6 dB under the voice with peaks at most 0.7 x the voice peak.
"""
import json
import sys
import wave
from pathlib import Path

import numpy as np
from scipy import signal

from .synth import SR, undb, db
from .sfx import sfx as make_sfx
from .music import render_music


# ---------- loudness (ITU-R BS.1770 K-weighting, gated integrated loudness) ----------
def _kweight(x):
    b1, a1 = [1.53512485958697, -2.69169618940638, 1.19839281085285], [1.0, -1.69065929318241, 0.73248077421585]
    b2, a2 = [1.0, -2.0, 1.0], [1.0, -1.99004745483398, 0.99007225036621]
    return signal.lfilter(b2, a2, signal.lfilter(b1, a1, x, axis=0), axis=0)


def lufs(x):
    x = np.atleast_2d(x.T).T if x.ndim == 1 else x
    y = _kweight(x)
    blk, hop = int(0.4 * SR), int(0.1 * SR)
    if len(y) < blk:
        return -70.0
    ms = np.array([np.mean(y[i:i + blk] ** 2, axis=0).sum() for i in range(0, len(y) - blk + 1, hop)])
    lk = -0.691 + 10 * np.log10(ms + 1e-12)
    g = ms[lk > -70]
    if not len(g):
        return -70.0
    rel = -0.691 + 10 * np.log10(g.mean()) - 10
    g2 = ms[(lk > -70) & (lk > rel)]
    return float(-0.691 + 10 * np.log10(g2.mean() + 1e-12))


def true_peak_db(x):
    up = signal.resample_poly(x, 4, 1, axis=0)
    return db(np.abs(up).max())


def limiter(x, ceiling_db=-1.1, look=0.005, release=0.25):
    """Look-ahead peak limiter working on a 4x oversampled peak estimate."""
    c = undb(ceiling_db)
    peak = np.abs(signal.resample_poly(x, 4, 1, axis=0)).max(axis=1).reshape(-1, 4).max(axis=1)[: len(x)]
    peak = np.pad(peak, (0, len(x) - len(peak)))
    need = np.minimum(1.0, c / np.maximum(peak, 1e-9))
    L = int(look * SR)
    need = _min_filter(need, L)  # start reducing gain `look` seconds before a peak
    g = np.empty_like(need); cur = 1.0; rel = np.exp(-1 / (release * SR))
    for i, v in enumerate(need):
        cur = v if v < cur else cur * rel + v * (1 - rel)
        g[i] = cur
    return x * g[:, None]


def _min_filter(v, L):
    from scipy.ndimage import minimum_filter1d
    return minimum_filter1d(v, size=2 * L + 1, origin=0)


def envelope(x, attack=0.03, release=0.25):
    a, r = np.exp(-1 / (attack * SR)), np.exp(-1 / (release * SR))
    e = np.abs(x); out = np.empty_like(e); cur = 0.0
    for i, v in enumerate(e):
        cur = a * cur + (1 - a) * v if v > cur else r * cur + (1 - r) * v
        out[i] = cur
    return out


def window_db(x, win=0.4, hop=0.05):
    n, h = int(win * SR), int(hop * SR)
    if len(x) < n:
        return np.array([-120.0]), h
    idx = np.arange(0, len(x) - n + 1, h)
    c = np.concatenate([[0.0], np.cumsum(x * x)])
    ms = (c[idx + n] - c[idx]) / n
    return 10 * np.log10(ms + 1e-12), h


def voice_on_top(v, music, margin_db=6.0):
    """Gain curve for the music so it stays at least margin_db under the voice wherever the voice speaks."""
    vd, h = window_db(v); md, _ = window_db(music)
    speaking = vd > (np.percentile(vd[vd > -100], 90) - 25 if np.any(vd > -100) else -60)
    need = np.where(speaking, np.minimum(0.0, (vd - margin_db) - md), 0.0)
    from scipy.ndimage import minimum_filter1d, uniform_filter1d
    need = uniform_filter1d(minimum_filter1d(need, 9), 3)  # look a little ahead/behind, then smooth
    g = undb(np.interp(np.arange(len(music)), np.arange(len(need)) * h + int(0.2 * SR), need))
    return g


def read_mono(p):
    with wave.open(str(p)) as w:
        if w.getframerate() != SR or w.getsampwidth() != 2:
            raise SystemExit("voice must be 48 kHz 16-bit wav (trim_silence.py writes that)")
        x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float64) / 32768
        if w.getnchannels() > 1:
            x = x.reshape(-1, w.getnchannels()).mean(axis=1)
    return x


def write(p, x):
    x = np.clip(x, -1, 1)
    if x.ndim == 1:
        x = x[:, None]
    with wave.open(str(p), "wb") as w:
        w.setnchannels(x.shape[1]); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((x * 32767).astype(np.int16).tobytes())


def main():
    if len(sys.argv) != 4:
        raise SystemExit(__doc__)
    spec = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    voice = read_mono(sys.argv[2])
    out = Path(sys.argv[3]); (out / "stems").mkdir(parents=True, exist_ok=True)
    seed = int(spec.get("seed", 1))
    rng = np.random.default_rng(seed)
    tail = float(spec.get("tail", 0.25))
    n = len(voice) + int(tail * SR)
    dur = n / SR
    v = np.zeros(n); v[: len(voice)] = voice
    v *= undb(-16.0 - lufs(voice))  # voice to -16 LUFS before the bed is set against it
    vl = lufs(v)

    # music: set its loudness relative to the voice, then duck it under speech
    m_spec = spec.get("music", {})
    music = np.zeros(n)
    if m_spec is not None and m_spec.get("enabled", True):
        mm = render_music(dur, m_spec.get("sections"), seed, m_spec.get("mood", "curious"))
        music[: len(mm)] = mm
        under = float(m_spec.get("under_voice_db", 8))
        music *= undb((vl - under + 3.0) - lufs(music))  # +3 dB because ducking takes about 3-4 dB off under speech
        e = envelope(v)
        speaking = np.clip(e / (np.percentile(e[e > 1e-4], 60) if np.any(e > 1e-4) else 1), 0, 1)
        music *= undb(-4.0 * speaking)
        music *= voice_on_top(v, music, margin_db=8.0)
        fade = int(0.3 * SR)
        music[-fade:] *= np.linspace(1, 0, fade)

    # effects
    fx = np.zeros(n)
    vpeak = np.percentile(np.abs(v[np.abs(v) > 1e-3]), 99.5) if np.any(np.abs(v) > 1e-3) else 0.5
    words_file = Path(sys.argv[2]).parent.parent / "words.json"
    words_data = []
    if words_file.exists():
        try:
            words_data = json.loads(words_file.read_text(encoding="utf-8"))
        except Exception:
            pass

    for c in spec.get("sfx", []):
        kind = c.get("kind") or c.get("preset", "hit")
        t = float(c.get("t", 0.0))
        if "t" not in c and "word" in c and words_data:
            target_w = c["word"].lower().strip(".,!?\"")
            for w in words_data:
                if w.get("word", "").lower().strip(".,!?\"") == target_w:
                    t = float(w.get("start", 0.0))
                    break
        params = {k: c[k] for k in c if k not in ("t", "kind", "preset", "gain_db", "word", "gain")}
        s = make_sfx(kind, np.random.default_rng(seed * 1000 + int(t * 1000)), **params)
        g = vpeak * 0.55 * undb(float(c.get("gain_db", 0)))
        i = int(round(t * SR))
        if i < n:
            m = min(len(s), n - i); fx[i:i + m] += s[:m] * g

    # effects stay well under the voice: peaks at most 0.7x the voice peak, and the effects bed at least 6 dB under the voice
    if np.any(fx):
        fpk = np.abs(fx).max()
        if fpk > 0.7 * vpeak:
            fx *= 0.7 * vpeak / fpk
        fl = lufs(fx)
        if fl > vl - 6.0:
            fx *= undb(vl - 6.0 - fl)

    # stereo: voice centre, music slightly wide, effects centre
    left = v + music * 0.95 + fx
    right = v + music * 1.0 + fx
    wide = 0.12 * np.concatenate([np.zeros(int(0.011 * SR)), music])[:n]
    mix = np.stack([left + wide, right - wide], axis=1)
    mix *= undb(-14.5 - lufs(mix))
    mix = limiter(mix, -1.1)
    mix *= undb(-14.5 - lufs(mix))
    mix = limiter(mix, -1.1)
    write(out / "mix.wav", mix)
    write(out / "stems" / "voice.wav", v)
    write(out / "stems" / "music.wav", music)
    write(out / "stems" / "sfx.wav", fx)
    bed = music + fx
    rep = {
        "seconds": round(n / SR, 3), "integrated_lufs": round(lufs(mix), 2), "true_peak_dbtp": round(true_peak_db(mix), 2),
        "voice_lufs": round(vl, 2), "bed_lufs": round(lufs(bed), 2) if np.any(bed) else None,
        "bed_under_voice_db": round(vl - lufs(bed), 2) if np.any(bed) else None, "sfx_count": len(spec.get("sfx", [])),
        "sfx_under_voice_db": round(vl - lufs(fx), 2) if np.any(fx) else None,
        "sfx_peak_vs_voice_peak": round(float(np.abs(fx).max() / max(vpeak, 1e-9)), 3) if np.any(fx) else None,
    }
    try:  # loudness range as FFmpeg measures it (EBU R128 LRA)
        import re, subprocess
        r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(out / "mix.wav"), "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True)
        m = re.search(r"LRA:\s+(-?[\d.]+) LU", r.stderr[r.stderr.rfind("Summary:"):])
        rep["lra_lu"] = float(m.group(1)) if m else None
    except Exception:
        rep["lra_lu"] = None
    (out / "sound_report.json").write_text(json.dumps(rep, indent=1))
    print(json.dumps(rep))


if __name__ == "__main__":
    main()
