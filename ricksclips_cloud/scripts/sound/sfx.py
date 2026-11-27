"""Cartoon sound effects, all synthesized. sfx(kind, rng, **params) -> mono float array at 48 kHz.

Kinds: whoosh, swish, pop, boing, thud, impact, crash, click, tick, ding, sparkle, splash, step,
creak, rumble, zap, slide_up, slide_down, drum, gulp, bubble, chime, buzz, clang, wind, riser.
"""
import numpy as np
from .synth import (SR, t_axis, env_adsr, env_exp, osc, noise, lp, hp, bp, sweep_lp, karplus, reverb, soft_clip, midi)


def _norm(x, peak=0.9):
    m = np.abs(x).max()
    return x * (peak / m) if m > 0 else x


def whoosh(rng, dur=0.45, up=True, bright=1.0):
    n = noise(dur, rng, "pink")
    x = sweep_lp(n, 300 * bright, 5000 * bright) if up else sweep_lp(n, 5000 * bright, 300 * bright)
    e = np.sin(np.pi * np.linspace(0, 1, len(x))) ** 1.6
    return _norm(hp(x, 120) * e, 0.7)


def swish(rng, dur=0.22):
    x = bp(noise(dur, rng), 1500, 7000) * env_adsr(int(dur * SR), 0.03, 0.05, 0.6, dur * 0.6)
    return _norm(x, 0.6)


def pop(rng, pitch=1.0):
    d = 0.09; t = t_axis(d)
    f = 900 * pitch * np.exp(-t * 30) + 250 * pitch
    x = osc(f, d) * env_exp(len(t), 0.02) + bp(noise(d, rng), 2000, 6000) * env_exp(len(t), 0.004) * 0.4
    return _norm(x, 0.8)


def boing(rng, pitch=1.0, dur=0.6):
    t = t_axis(dur)
    f = 180 * pitch * (1 + 0.6 * np.sin(2 * np.pi * 9 * t) * np.exp(-t * 4)) * (1 + 0.8 * np.exp(-t * 10))
    x = osc(f, dur, "tri") * env_exp(len(t), 0.22)
    return _norm(x, 0.75)


def thud(rng, pitch=1.0):
    d = 0.35; t = t_axis(d)
    x = osc(110 * pitch * np.exp(-t * 8) + 45 * pitch, d) * env_exp(len(t), 0.08)
    x += lp(noise(d, rng), 600) * env_exp(len(t), 0.03) * 0.6
    return _norm(soft_clip(x, 1.5), 0.9)


def impact(rng, pitch=1.0):
    x = thud(rng, pitch * 0.9)
    d = len(x) / SR
    x += bp(noise(d, rng), 800, 5000) * env_exp(len(x), 0.05) * 0.5
    return _norm(reverb(x, rng, 0.8, 0.15), 0.95)


def crash(rng, dur=1.4):
    n = noise(dur, rng)
    x = hp(n, 400) * env_exp(len(n), 0.35)
    for k in range(5):
        st = int(rng.uniform(0, 0.25) * SR)
        part = karplus(rng.uniform(300, 1400), dur, rng, 0.985, 0.9) * 0.3
        x[st:] += part[: len(x) - st]
    th = thud(rng, 0.8)
    x[: len(th)] += th[: len(x)]
    return _norm(reverb(x, rng, 1.2, 0.2), 0.9)


def click(rng):
    d = 0.03
    return _norm(hp(noise(d, rng), 2500) * env_exp(int(d * SR), 0.003), 0.6)


def tick(rng):
    d = 0.05; t = t_axis(d)
    x = osc(2400, d) * env_exp(len(t), 0.006)
    c = click(rng)
    x[: len(c)] += c * 0.5
    return _norm(x, 0.5)


def ding(rng, note=84, dur=1.4):
    t = t_axis(dur); f = midi(note)
    x = sum(osc(f * h, dur) * env_exp(len(t), 0.6 / h) * a for h, a in [(1, 1), (2.76, 0.4), (5.4, 0.2), (8.9, 0.1)])
    return _norm(reverb(x, rng, 1.5, 0.2), 0.6)


def chime(rng, root=79):
    out = np.zeros(int(1.6 * SR))
    for i, m in enumerate([0, 4, 7, 12]):
        d = ding(rng, root + m, 1.2) * 0.6
        s = int(i * 0.07 * SR)
        out[s:s + len(d)] += d[: len(out) - s]
    return _norm(out, 0.6)


def sparkle(rng, dur=0.9):
    out = np.zeros(int(dur * SR))
    for i in range(10):
        f = rng.uniform(2500, 6000); d = 0.12
        s = int(rng.uniform(0, dur - d) * SR)
        g = osc(f, d) * env_exp(int(d * SR), 0.03)
        out[s:s + len(g)] += g * rng.uniform(0.3, 0.8)
    return _norm(reverb(out, rng, 1.0, 0.3), 0.45)


def splash(rng, dur=0.9):
    n = noise(dur, rng)
    x = bp(n, 300, 6000) * env_adsr(len(n), 0.01, 0.1, 0.5, 0.6)
    for k in range(14):
        s = int(rng.uniform(0.05, dur * 0.8) * SR)
        b = bubble(rng, rng.uniform(0.6, 1.8)) * 0.3
        x[s:s + len(b)] += b[: len(x) - s]
    return _norm(x, 0.8)


def bubble(rng, pitch=1.0):
    d = 0.08; t = t_axis(d)
    return osc(500 * pitch * (1 + 2 * t / d), d) * env_exp(len(t), 0.02)


def step(rng, surface="stone"):
    d = 0.09
    lo, hi = (300, 3000) if surface == "stone" else (150, 1200)
    x = bp(noise(d, rng), lo, hi) * env_exp(int(d * SR), 0.015)
    x += osc(90 + rng.uniform(-10, 10), d) * env_exp(int(d * SR), 0.02) * 0.4
    return _norm(x, 0.5)


def creak(rng, dur=0.8):
    t = t_axis(dur)
    f = 120 + 60 * np.sin(2 * np.pi * 1.3 * t) + rng.uniform(-5, 5)
    pulses = (np.sin(2 * np.pi * np.cumsum(f) / SR) > 0.97).astype(float)
    x = bp(pulses, 300, 2500) * env_adsr(len(t), 0.05, 0.1, 0.8, 0.2)
    return _norm(x, 0.5)


def rumble(rng, dur=1.5):
    n = noise(dur, rng, "brown")
    return _norm(lp(n, 140) * env_adsr(len(n), 0.2, 0.2, 0.8, 0.5), 0.8)


def zap(rng):
    d = 0.3; t = t_axis(d)
    return _norm(osc(2000 * np.exp(-t * 12) + 200, d, "square") * env_exp(len(t), 0.1) * 0.6, 0.6)


def slide(rng, up=True, dur=0.5):
    t = t_axis(dur)
    f = np.geomspace(400, 1600, len(t)) if up else np.geomspace(1600, 300, len(t))
    vib = 1 + 0.02 * np.sin(2 * np.pi * 7 * t)
    return _norm(osc(f * vib, dur, "sine") * env_adsr(len(t), 0.02, 0.05, 0.8, 0.08), 0.5)


def drum(rng, kind="kick"):
    if kind == "kick":
        d = 0.3; t = t_axis(d)
        return _norm(osc(150 * np.exp(-t * 25) + 45, d) * env_exp(len(t), 0.09), 0.9)
    if kind == "snare":
        d = 0.2
        return _norm(bp(noise(d, rng), 1000, 8000) * env_exp(int(d * SR), 0.05) + osc(190, d) * env_exp(int(d * SR), 0.03) * 0.5, 0.7)
    d = 0.06
    return _norm(hp(noise(d, rng), 6000) * env_exp(int(d * SR), 0.012), 0.35)  # hat


def gulp(rng):
    d = 0.18; t = t_axis(d)
    return _norm(lp(osc(300 * (1 - 0.5 * t / d), d, "tri"), 1200) * env_adsr(len(t), 0.01, 0.05, 0.6, 0.05), 0.5)


def buzz(rng, dur=0.4):
    return _norm(lp(osc(110, dur, "saw"), 1800) * env_adsr(int(dur * SR), 0.01, 0.05, 0.8, 0.05), 0.5)


def clang(rng):
    d = 1.2; t = t_axis(d)
    x = sum(osc(f, d) * env_exp(len(t), 0.4) * a for f, a in [(523, 1), (1187, 0.6), (1943, 0.4), (2760, 0.3)])
    return _norm(reverb(x, rng, 1.2, 0.25), 0.7)


def wind(rng, dur=2.0):
    n = noise(dur, rng, "pink")
    x = sweep_lp(n, 400, 900) * env_adsr(len(n), 0.5, 0.2, 0.8, 0.6)
    return _norm(x, 0.4)


def riser(rng, dur=1.2):
    t = t_axis(dur)
    x = osc(np.geomspace(200, 900, len(t)), dur, "saw") * 0.3 + sweep_lp(noise(dur, rng, "pink"), 200, 6000) * 0.7
    return _norm(lp(x, 7000) * np.linspace(0, 1, len(t)) ** 2, 0.6)


KINDS = {
    "whoosh": lambda r, p: whoosh(r, p.get("dur", 0.45), p.get("up", True)),
    "swish": lambda r, p: swish(r),
    "pop": lambda r, p: pop(r, p.get("pitch", 1.0)),
    "boing": lambda r, p: boing(r, p.get("pitch", 1.0)),
    "thud": lambda r, p: thud(r, p.get("pitch", 1.0)),
    "impact": lambda r, p: impact(r, p.get("pitch", 1.0)),
    "crash": lambda r, p: crash(r),
    "click": lambda r, p: click(r),
    "tick": lambda r, p: tick(r),
    "ding": lambda r, p: ding(r, p.get("note", 84)),
    "chime": lambda r, p: chime(r),
    "sparkle": lambda r, p: sparkle(r),
    "splash": lambda r, p: splash(r),
    "step": lambda r, p: step(r, p.get("surface", "stone")),
    "creak": lambda r, p: creak(r),
    "rumble": lambda r, p: rumble(r, p.get("dur", 1.5)),
    "zap": lambda r, p: zap(r),
    "slide_up": lambda r, p: slide(r, True),
    "slide_down": lambda r, p: slide(r, False),
    "drum": lambda r, p: drum(r, p.get("drum", "kick")),
    "gulp": lambda r, p: gulp(r),
    "bubble": lambda r, p: _norm(bubble(r, p.get("pitch", 1.0)), 0.5),
    "buzz": lambda r, p: buzz(r),
    "clang": lambda r, p: clang(r),
    "wind": lambda r, p: wind(r, p.get("dur", 2.0)),
    "riser": lambda r, p: riser(r, p.get("dur", 1.2)),
}


def sfx(kind, rng, **params):
    if kind not in KINDS:
        kind = "impact"
    return KINDS[kind](rng, params)
