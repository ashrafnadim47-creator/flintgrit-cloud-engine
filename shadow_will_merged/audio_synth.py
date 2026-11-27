#!/usr/bin/env python3
"""
Universal procedural music bed + SFX synthesizer for Shadow Will Merged Engine.
Mixes voice.mp3 with mood-matched synth score + timed SFX cues -> mix_raw.wav.
"""
import argparse
import json
import subprocess
from pathlib import Path
import numpy as np

SR = 48000


def lp_fast(x, cutoff):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 / (1 + (f / cutoff) ** 4)
    return np.fft.irfft(X, len(x)).astype(np.float32)


def hp_fast(x, cutoff):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 - 1 / (1 + (f / cutoff) ** 4)
    return np.fft.irfft(X, len(x)).astype(np.float32)


def place(buf, sig, t0, gain=1.0):
    N = len(buf)
    i = int(t0 * SR)
    j = min(N, i + len(sig))
    if i < N and j > i:
        buf[i:j] += sig[: j - i] * gain


def midi(m):
    return 440.0 * 2 ** ((m - 69) / 12.0)


def synthesize_mix(voice_mp3: Path, out_wav: Path, duration: float, mood: str = "mystery", cues=None):
    N = int(round(duration * SR))
    rng = np.random.default_rng(42)

    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(voice_mp3), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
        capture_output=True,
        check=True,
    ).stdout
    v = np.frombuffer(raw, np.float32).copy()
    voice = np.zeros(N, np.float32)
    voice[: min(N, len(v))] = v[:N]

    music = np.zeros(N, np.float32)
    sfx = np.zeros(N, np.float32)

    if mood == "heist":
        bpm = 116
        prog = [(57, [57, 60, 64]), (55, [55, 59, 62]), (53, [53, 57, 60]), (52, [52, 56, 59])]
    elif mood == "epic":
        bpm = 104
        prog = [(57, [57, 60, 64]), (53, [53, 57, 60]), (55, [55, 59, 62]), (52, [52, 56, 59])]
    else:  # mystery / suspense
        bpm = 92
        prog = [(50, [50, 53, 57]), (48, [48, 52, 55]), (46, [46, 50, 53]), (45, [45, 49, 52])]

    beat = 60.0 / bpm

    def pluck(f, dur=0.35, bright=0.5):
        n = int(dur * SR)
        t = np.arange(n) / SR
        s = sum((bright ** k) * np.sin(2 * np.pi * f * (k + 1) * t) / (k + 1) for k in range(5))
        e = np.minimum(1, t / 0.004) * np.exp(-t / (dur * 0.35))
        return (s * e).astype(np.float32)

    def pad(fs, dur):
        n = int(dur * SR)
        t = np.arange(n) / SR
        s = np.zeros(n)
        for f in fs:
            s += np.sin(2 * np.pi * f * t) + 0.35 * np.sin(4 * np.pi * f * t)
        a = np.minimum(1, t / 0.12) * np.minimum(1, np.maximum(0, (dur - t) / 0.18))
        return lp_fast((s * a).astype(np.float32), 1200) / max(len(fs), 1)

    def kick():
        n = int(0.32 * SR)
        t = np.arange(n) / SR
        f = 48 + 85 * np.exp(-t * 28)
        return (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)).astype(np.float32)

    def whoosh(d=0.45):
        n = int(d * SR)
        t = np.arange(n) / SR
        noise = rng.standard_normal(n).astype(np.float32)
        env = np.sin(np.pi * t / d) ** 1.5
        return lp_fast(noise * env, 1800) * 0.35

    def hit(d=0.35):
        n = int(d * SR)
        t = np.arange(n) / SR
        return (np.sin(2 * np.pi * 75 * t * (1 + 0.5 * np.exp(-t * 35))) * np.exp(-t * 12)).astype(np.float32)

    bar = 0
    tt = 0.0
    while tt < duration - 0.5:
        root, ch = prog[bar % len(prog)]
        place(music, pad([midi(m) for m in ch], min(beat * 4, duration - tt)), tt, 0.09)
        for b in range(4):
            tb = tt + b * beat
            if tb >= duration - 0.3:
                break
            if b % 2 == 0:
                place(music, kick(), tb, 0.38)
            place(music, pluck(midi(root - 12), 0.38, 0.42), tb, 0.26)
            place(music, pluck(midi(ch[(b + bar) % 3] + 12), 0.22, 0.55), tb + beat * 0.5, 0.11)
        bar += 1
        tt += beat * 4

    # Fade out last 0.6s
    fade_n = min(N, int(0.6 * SR))
    music[-fade_n:] *= np.linspace(1.0, 0.0, fade_n, dtype=np.float32)

    place(sfx, whoosh(0.45), 0.05, 0.45)
    for c in cues or []:
        t_cue = float(c.get("t", 0.5))
        kind = c.get("kind", "hit")
        vol = float(c.get("vol", 0.5))
        if kind == "whoosh":
            place(sfx, whoosh(0.45), t_cue, vol)
        else:
            place(sfx, hit(0.35), t_cue, vol)

    # Sidechain duck music under voice
    env_v = np.abs(voice)
    win = int(0.08 * SR)
    if win > 1:
        kernel = np.ones(win, np.float32) / win
        env_s = np.convolve(env_v, kernel, mode="same")
    else:
        env_s = env_v
    duck = np.clip(1.0 - env_s * 3.5, 0.28, 1.0).astype(np.float32)

    mix = voice * 0.92 + music * duck * 0.45 + sfx * 0.55
    peak = float(np.max(np.abs(mix))) if len(mix) else 1.0
    if peak > 0.92:
        mix = mix * (0.92 / peak)

    pcm = (np.clip(mix, -1.0, 1.0) * 32767.0).astype(np.int16)
    import wave
    with wave.open(str(out_wav), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(pcm.tobytes())
    print(f"[AudioSynth] Mixed {duration:.2f}s -> {out_wav}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("voice_mp3")
    ap.add_argument("out_wav")
    ap.add_argument("--duration", type=float, required=True)
    ap.add_argument("--mood", default="mystery")
    ap.add_argument("--cues", default=None)
    args = ap.parse_args()
    cues_data = json.loads(Path(args.cues).read_text()) if args.cues and Path(args.cues).exists() else []
    synthesize_mix(Path(args.voice_mp3), Path(args.out_wav), args.duration, args.mood, cues_data)
