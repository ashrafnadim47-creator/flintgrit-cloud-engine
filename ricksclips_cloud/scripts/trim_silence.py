"""Remove the silent parts of the voice: shorten pauses using the word timings, keep up to four dramatic pauses.

Usage:  python trim_silence.py <voice_norm.wav> <words.json> <out final.wav> <out words_final.json>
            [--max-pause 0.26] [--pause 0.28] [--no-dramatic]

Rules
- A pause between two words that is longer than 0.26 s becomes 0.28 s. Shorter pauses stay as they are,
  so words never run into each other.
- Up to four dramatic pauses keep their natural length (capped at 1.2 s): after the hook (end of the first
  or second sentence, whichever pause is longer), before the pivot (the sentence with "you see"), before
  the twist (the second-to-last sentence) and before the last line (the last sentence).
- A pause is the longest quiet run (level 30 dB under the speech level) between two word starts, found in the
  audio itself (recognisers often give word ends that touch the next word). Only that quiet core is
  removed, with 10 ms crossfades, so breaths stay and word tails and starts are never cut.
- The voice starts 0.03 s before the first word and ends 0.12 s after the last one.
- Word times are moved by exactly the removed amounts and written to words_final.json.
Prints a JSON report, including the real words per second.
"""
import json
import re
import sys
import wave
from pathlib import Path

import numpy as np

SR = 48000
HOP = 0.005


def read_wav(p):
    with wave.open(str(p)) as w:
        if w.getframerate() != SR or w.getsampwidth() != 2:
            raise SystemExit("trim_silence.py needs the 48 kHz 16-bit wav written by prep_voice.py")
        x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float64) / 32768.0
        if w.getnchannels() > 1:
            x = x.reshape(-1, w.getnchannels()).mean(axis=1)
    return x


def write_wav(p, x):
    with wave.open(str(p), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())


def level_db(x):
    h, n = int(SR * HOP), int(SR * 0.02)
    frames = max(1, (len(x) - n) // h)
    idx = np.arange(frames)[:, None] * h + np.arange(n)[None, :]
    return 20 * np.log10(np.sqrt(np.mean(x[idx] ** 2, axis=1) + 1e-12))


def sentences(words):
    """index of the first word of every sentence"""
    starts = [0]
    for i, w in enumerate(words[:-1]):
        if re.search(r"[.!?][\"')\]]*$", w["text"]):
            starts.append(i + 1)
    return starts


def dramatic_gaps(words, gap_len):
    """gap index g = pause between words[g] and words[g + 1]"""
    st = sentences(words)
    keep = {}
    gap = lambda g: gap_len[g]
    if len(st) >= 2:
        cands = [s - 1 for s in st[1:3]]
        g = max(cands, key=gap); keep[g] = "after the hook"
    for k, s in enumerate(st):
        if k == 0:
            continue
        sent = " ".join(w["text"] for w in words[s:(st[k + 1] if k + 1 < len(st) else len(words))]).lower()
        if re.search(r"\byou see\b", sent):
            keep.setdefault(s - 1, "before the pivot"); break
    if len(st) >= 3:
        keep.setdefault(st[-2] - 1, "before the twist")
    if len(st) >= 2:
        keep.setdefault(st[-1] - 1, "before the last line")
    return {g: why for g, why in keep.items() if 0 <= g < len(words) - 1}


def longest_run(q):
    best, run_s, bs, be = 0, None, 0, 0
    for k, v in enumerate(np.append(q, False)):
        if v and run_s is None:
            run_s = k
        elif not v and run_s is not None:
            if k - run_s > best:
                best, bs, be = k - run_s, run_s, k
            run_s = None
    return bs, be


def main():
    a = sys.argv[1:]
    if len(a) < 4:
        raise SystemExit(__doc__)
    src, wj, out_wav, out_words = a[:4]
    max_pause = float(a[a.index("--max-pause") + 1]) if "--max-pause" in a else 0.26
    target = float(a[a.index("--pause") + 1]) if "--pause" in a else 0.28
    x = read_wav(src)
    words = json.loads(Path(wj).read_text(encoding="utf-8"))
    if not words:
        raise SystemExit("words.json is empty")
    db = level_db(x)
    speech_db = float(np.percentile(db[db > -80], 90)) if np.any(db > -80) else -20.0
    quiet = db < speech_db - 30

    # measure every pause from the audio: longest quiet run between this word's start and the next start
    pauses = []
    for g in range(len(words) - 1):
        a0 = int((words[g]["start"] + 0.06) / HOP)
        a1 = int(words[g + 1]["start"] / HOP)
        q = quiet[max(0, a0):min(len(quiet), a1)]
        if len(q) == 0 or not q.any():
            pauses.append(None); continue
        bs, be = longest_run(q)
        pauses.append(((a0 + bs) * HOP, (a0 + be) * HOP))
        # a word ends where its trailing silence starts (better caption timing than touching ends)
        if (a0 + be) * HOP >= words[g + 1]["start"] - 0.05:
            words[g]["end"] = min(words[g]["end"], round((a0 + bs) * HOP + 0.02, 3)) if words[g]["end"] > (a0 + bs) * HOP else words[g]["end"]
    gap_len = [0.0 if p is None else p[1] - p[0] for p in pauses]
    drama = {} if "--no-dramatic" in a else dramatic_gaps(words, gap_len)

    cuts = []  # (start_sample, end_sample) to remove
    head = max(0.0, words[0]["start"] - 0.03)
    if head > 0:
        cuts.append((0, int(head * SR)))
    kept = []
    for g, p in enumerate(pauses):
        if p is None:
            continue
        run_len = p[1] - p[0]
        if run_len <= max_pause:
            continue
        limit = 1.2 if g in drama else target
        if g in drama:
            kept.append({"after_word": words[g]["text"], "why": drama[g], "seconds": round(min(run_len, 1.2), 2)})
        amt = run_len - limit
        if amt <= 0.01:
            continue
        mid = (p[0] + p[1]) / 2
        cuts.append((int((mid - amt / 2) * SR), int((mid + amt / 2) * SR)))
    tail_end = min(len(x), int((words[-1]["end"] + 0.12) * SR))
    if tail_end < len(x):
        cuts.append((tail_end, len(x)))

    cuts.sort()
    fade = int(0.010 * SR)
    pieces, cur = [], 0
    for c0, c1 in cuts:
        if c0 > cur:
            seg = x[cur:c0].copy()
            if pieces and len(seg) > fade:
                seg[:fade] *= np.linspace(0, 1, fade)
            if c1 < len(x) and len(seg) > fade:
                seg[-fade:] *= np.linspace(1, 0, fade)
            pieces.append(seg)
        cur = max(cur, c1)
    if cur < len(x):
        seg = x[cur:].copy()
        if pieces and len(seg) > fade:
            seg[:fade] *= np.linspace(0, 1, fade)
        pieces.append(seg)
    y = np.concatenate(pieces) if pieces else x
    write_wav(out_wav, y)

    def shift(t):
        s = int(t * SR)
        removed = sum(min(c1, s) - c0 for c0, c1 in cuts if c0 < s)
        return round(max(0.0, (s - removed) / SR), 3)
    final = [{"text": w["text"], "start": shift(w["start"]), "end": shift(w["end"])} for w in words]
    dur = len(y) / SR
    final[-1]["end"] = min(final[-1]["end"], round(dur, 3))
    Path(out_words).write_text(json.dumps(final, indent=1), encoding="utf-8")
    wps = len(final) / max(1e-6, final[-1]["end"] - final[0]["start"])
    print(json.dumps({
        "input_seconds": round(len(x) / SR, 3), "final_seconds": round(dur, 3), "removed_seconds": round((len(x) - len(y)) / SR, 3),
        "pauses_shortened": len([c for c in cuts if c[0] > 0 and c[1] < len(x)]), "dramatic_pauses_kept": kept,
        "words": len(final), "words_per_second": round(wps, 2),
        "first_word_s": final[0]["start"],
    }))


if __name__ == "__main__":
    main()
