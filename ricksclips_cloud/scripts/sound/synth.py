"""Synthesis building blocks (numpy/scipy only). All functions are deterministic for a given seed."""
import numpy as np
from scipy import signal

SR = 48000


def t_axis(dur):
    return np.arange(int(dur * SR)) / SR


def env_adsr(n, a=0.005, d=0.08, s=0.6, r=0.1, hold=None):
    """ADSR envelope of n samples. hold = sustain length in seconds (default: whatever is left)."""
    A, D, R = int(a * SR), int(d * SR), int(r * SR)
    H = n - A - D - R if hold is None else int(hold * SR)
    H = max(0, H)
    e = np.concatenate([np.linspace(0, 1, max(A, 1)), np.linspace(1, s, max(D, 1)), np.full(H, s), np.linspace(s, 0, max(R, 1))])
    return np.pad(e, (0, max(0, n - len(e))))[:n]


def env_exp(n, tau):
    return np.exp(-np.arange(n) / (tau * SR))


def osc(freq, dur, kind="sine", phase=0.0):
    """freq may be a number or an array (sweep). Band-limited saw/square via additive partials."""
    n = int(dur * SR)
    f = np.full(n, float(freq)) if np.isscalar(freq) else np.asarray(freq, float)[:n]
    ph = 2 * np.pi * np.cumsum(f) / SR + phase
    if kind == "sine":
        return np.sin(ph)
    if kind == "tri":
        return 2 / np.pi * np.arcsin(np.sin(ph))
    top = max(1, int(SR / 2 / max(f.max(), 1)))
    out = np.zeros(n)
    for k in range(1, min(top, 40) + 1):
        if kind == "square" and k % 2 == 0:
            continue
        out += np.sin(k * ph) / k
    return out * (2 / np.pi if kind == "saw" else 4 / np.pi)


def noise(dur, rng, color="white"):
    n = int(dur * SR)
    w = rng.standard_normal(n)
    if color == "pink":
        b, a = [0.049922035, -0.095993537, 0.050612699, -0.004408786], [1, -2.494956002, 2.017265875, -0.522189400]
        w = signal.lfilter(b, a, w) * 3.5
    elif color == "brown":
        w = signal.lfilter([1], [1, -0.995], w)
        w = w / (np.abs(w).max() + 1e-9)
    return w


def lp(x, fc, order=2):
    b, a = signal.butter(order, min(fc, SR * 0.45) / (SR / 2), "low")
    return signal.lfilter(b, a, x)


def hp(x, fc, order=2):
    b, a = signal.butter(order, max(fc, 10) / (SR / 2), "high")
    return signal.lfilter(b, a, x)


def bp(x, lo, hi, order=2):
    b, a = signal.butter(order, [max(lo, 10) / (SR / 2), min(hi, SR * 0.45) / (SR / 2)], "band")
    return signal.lfilter(b, a, x)


def sweep_lp(x, f0, f1, steps=48):
    """Time-varying low-pass by crossfading short blocks (good enough for whooshes)."""
    n = len(x); out = np.zeros(n); blk = max(1, n // steps)
    fs = np.geomspace(max(f0, 20), max(f1, 20), steps + 1)
    for i in range(steps + 1):
        a, b = i * blk, min(n, (i + 1) * blk + blk)
        if a >= n:
            break
        seg = lp(x[max(0, a - blk):b], fs[i])[min(a, blk):]
        w = np.hanning(len(seg)) if len(seg) > 2 else np.ones(len(seg))
        out[a:a + len(seg)] += seg * w
    return out / 0.75


def karplus(freq, dur, rng, damp=0.996, bright=0.5):
    """Plucked string."""
    n = int(dur * SR); N = max(2, int(SR / freq))
    buf = rng.uniform(-1, 1, N) * bright + lp(rng.uniform(-1, 1, N), 3000) * (1 - bright)
    out = np.zeros(n); idx = 0
    for i in range(n):
        out[i] = buf[idx]
        nxt = (idx + 1) % N
        buf[idx] = damp * 0.5 * (buf[idx] + buf[nxt])
        idx = nxt
    return out


def reverb(x, rng, time=1.2, mix=0.18, pre=0.012):
    """Convolution with a generated decaying noise tail (stereo-agnostic, mono in/out)."""
    n = int(time * SR)
    ir = rng.standard_normal(n) * np.exp(-np.arange(n) / (time * SR / 6.9))
    ir = lp(ir, 6000); ir[: int(pre * SR)] = 0
    ir /= np.sqrt(np.sum(ir ** 2)) + 1e-9
    wet = signal.fftconvolve(x, ir)[: len(x)]
    return x * (1 - mix) + wet * mix


def soft_clip(x, drive=1.0):
    return np.tanh(x * drive) / np.tanh(drive)


def place(dst, src, start_s, gain=1.0):
    i = int(round(start_s * SR))
    if i >= len(dst) or i + len(src) <= 0:
        return
    a = max(0, -i); b = min(len(src), len(dst) - i)
    dst[i + a:i + b] += src[a:b] * gain


def db(g):
    return 20 * np.log10(max(g, 1e-12))


def undb(d):
    return 10 ** (d / 20)


def midi(m):
    return 440.0 * 2 ** ((m - 69) / 12)
