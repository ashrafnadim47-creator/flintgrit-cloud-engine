"""Light original music bed, generated from a seed: plucked melody, soft pad, bass, light percussion.

sections: [{ "t": seconds, "mood": "curious|playful|tense|wonder|calm", "energy": 0..1 }]
Each mood picks a scale, chord loop and instrument balance; the seed varies melody and voicing,
so every short gets its own tune in the same family.
"""
import numpy as np
from .synth import SR, osc, karplus, noise, lp, hp, env_adsr, env_exp, reverb, midi, soft_clip
from .sfx import drum

MOODS = {
    # root midi, scale, chord loop (scale degrees), bpm, swing
    "curious": dict(root=57, scale=[0, 2, 3, 5, 7, 8, 10], loop=[0, 5, 3, 4], bpm=104, perc=0.6, pad=0.5),
    "playful": dict(root=60, scale=[0, 2, 4, 5, 7, 9, 11], loop=[0, 4, 5, 3], bpm=116, perc=0.9, pad=0.35),
    "tense": dict(root=55, scale=[0, 1, 3, 5, 7, 8, 10], loop=[0, 0, 5, 4], bpm=96, perc=0.4, pad=0.7),
    "wonder": dict(root=62, scale=[0, 2, 4, 6, 7, 9, 11], loop=[0, 3, 4, 0], bpm=92, perc=0.3, pad=0.8),
    "calm": dict(root=60, scale=[0, 2, 4, 7, 9, 11, 12], loop=[0, 5, 3, 4], bpm=88, perc=0.2, pad=0.7),
}


def chord(scale, deg):
    return [scale[(deg + k) % 7] + 12 * ((deg + k) // 7) for k in (0, 2, 4)]


def render_music(duration, sections, seed=1, base_mood="curious"):
    rng = np.random.default_rng(seed)
    n = int(duration * SR) + SR
    out = np.zeros(n)
    sections = sorted(sections or [{"t": 0, "mood": base_mood, "energy": 0.6}], key=lambda s: s["t"])
    if sections[0]["t"] > 0:
        sections.insert(0, {"t": 0, "mood": base_mood, "energy": 0.6})
    bpm = MOODS[sections[0]["mood"]]["bpm"] + rng.integers(-4, 5)
    beat = 60.0 / bpm
    motif = rng.integers(0, 5, size=8)
    total_beats = int(duration / beat) + 2
    for b in range(total_beats):
        t = b * beat
        sec = [s for s in sections if s["t"] <= t + 1e-6][-1]
        M = MOODS[sec.get("mood", base_mood)]
        energy = float(sec.get("energy", 0.6))
        bar, pos = divmod(b, 4)
        deg = M["loop"][bar % len(M["loop"])]
        ch = chord(M["scale"], deg)
        root = M["root"]
        # bass on beats 1 and 3
        if pos in (0, 2):
            f = midi(root - 24 + ch[0])
            d = beat * 1.8
            x = lp(osc(f, d, "tri") + 0.3 * osc(f * 2, d), 900) * env_adsr(int(d * SR), 0.01, 0.1, 0.7, 0.2)
            _add(out, x * 0.32, t)
        # pad once per bar
        if pos == 0 and M["pad"] * energy > 0.1:
            d = beat * 4.2
            x = sum(lp(osc(midi(root + c) * (1 + 0.003 * k), d, "saw"), 1400) for k, c in enumerate(ch))
            _add(out, x * env_adsr(int(d * SR), 0.4, 0.3, 0.7, 0.8) * 0.05 * M["pad"], t)
        # plucked melody, 8th notes with rests
        for half in (0, 1):
            if rng.random() < 0.35 - 0.2 * energy:
                continue
            step = motif[(b * 2 + half) % len(motif)] + (bar % 2) * rng.integers(0, 2)
            note = root + 12 + M["scale"][int(step) % 7]
            d = beat * 0.9
            x = karplus(midi(note), d, rng, 0.993, 0.6) * env_exp(int(d * SR), 0.35)
            _add(out, x * (0.18 + 0.12 * energy), t + half * beat / 2)
        # percussion
        p = M["perc"] * energy
        if p > 0.15:
            if pos in (0, 2):
                _add(out, drum(rng, "kick") * 0.35 * p, t)
            if pos in (1, 3) and p > 0.4:
                _add(out, drum(rng, "snare") * 0.18 * p, t)
            for q in range(2):
                _add(out, drum(rng, "hat") * (0.12 if q == 0 else 0.07) * p, t + q * beat / 2)
    out = reverb(hp(out, 40), rng, 1.6, 0.16)
    out = soft_clip(out / (np.abs(out).max() + 1e-9) * 0.8, 1.2)
    return out[: int(duration * SR)]


def _add(dst, x, t):
    i = int(round(t * SR))
    if i >= len(dst):
        return
    m = min(len(x), len(dst) - i)
    dst[i:i + m] += x[:m]
