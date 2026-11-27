"""Clean and refine word timings for the normalised voice (before the pauses are shortened).

Usage:  python fix_words.py <voice.wav> <transcript.json> <script.md|script.txt> <out words.json> [--digits]

What it does
1. Reads the word list from transcribe.mjs (Whisper through faster-whisper) and joins sub-word pieces back
   into whole words ("▁" / leading-space starts a word, "##" or a piece glued to the previous one
   continues it).
2. Re-spells the words exactly as in the script (capitals, punctuation, numbers written the script's way),
   using a sequence alignment, so captions show the script's own text.
3. Snaps each word start to a clear energy rise in the audio when there is a real dip before it
   (search window -100 ms .. +60 ms). Connected speech without a dip is left alone.
4. Forces order: start < end, no overlaps, no gaps longer than the audio, first word >= 0.
5. With --digits (the final pass) numbers that the script spells as words are shown as digits in the captions:
   "text" is the caption text ("50"), "spoken" keeps the script's own words ("fifty"). Numbers from ten up, and any
   number followed by a unit (feet, minutes, percent, dollars...), become digits; one to nine stay words otherwise.
6. Writes words.json: [{"text", "start", "end"}] in seconds, plus a report on stdout.
"""
import json
import re
import sys
import wave
import difflib
from pathlib import Path

import numpy as np


def load_audio(path):
    with wave.open(str(path)) as w:
        sr, ch, sw = w.getframerate(), w.getnchannels(), w.getsampwidth()
        raw = w.readframes(w.getnframes())
    if sw != 2:
        raise SystemExit("fix_words.py needs 16-bit PCM wav (convert with ffmpeg -c:a pcm_s16le)")
    x = np.frombuffer(raw, dtype=np.int16).astype(np.float64) / 32768.0
    if ch > 1:
        x = x.reshape(-1, ch).mean(axis=1)
    return x, sr


def envelope_db(x, sr, hop=0.005, win=0.012):
    h, n = int(sr * hop), int(sr * win)
    frames = max(1, (len(x) - n) // h)
    idx = np.arange(frames)[:, None] * h + np.arange(n)[None, :]
    e = np.sqrt(np.mean(x[idx] ** 2, axis=1) + 1e-12)
    return 20 * np.log10(e), hop


def join_pieces(raw):
    """Sub-word pieces -> whole words. Works for sentencepiece ("▁word"), wordpiece ("##ing"), and
    whisper-style lists where a word starts with a space and continuation pieces do not."""
    spaced = any(r["text"].startswith((" ", "\u2581")) for r in raw)
    out = []
    for r in raw:
        t = r["text"]
        cont = t.startswith("##") or (spaced and not t.startswith((" ", "\u2581")) and out
                                       and not re.match(r"^[\"'(\[]", t) and r["start"] - out[-1]["end"] < 0.06)
        clean = t.replace("\u2581", " ").lstrip("#").strip()
        if not clean:
            continue
        if cont and out:
            out[-1]["text"] += clean
            out[-1]["end"] = max(out[-1]["end"], r["end"])
        else:
            out.append({"text": clean, "start": r["start"], "end": r["end"]})
    return out


def load_words(path):
    d = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(d, dict):
        d = d.get("words") or d.get("segments") or []
    raw = []
    for w in d:
        t = w.get("text") if w.get("text") is not None else w.get("word", "")
        if not t or not t.strip() or w.get("type") in ("spacing", "audio_event"):
            continue
        raw.append({"text": t, "start": float(w["start"]), "end": float(w["end"])})
    return join_pieces(raw)


def norm(s):
    return re.sub(r"[^a-z0-9']", "", s.lower().replace("’", "'"))


def script_tokens(path):
    txt = Path(path).read_text(encoding="utf-8")
    m = re.search(r"```(?:text)?\n(.*?)```", txt, re.S)  # script.md keeps the script in one code block
    if m:
        txt = m.group(1)
    return [t for t in re.split(r"\s+", txt) if norm(t)]


ONES = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split()
TENS = "_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()


def num_words(n, year_style=False):
    if year_style and 1100 <= n <= 1999 or year_style and 2010 <= n <= 2099:
        hi, lo = divmod(n, 100)
        return num_words(hi) + (["hundred"] if lo == 0 else (["oh"] + num_words(lo) if lo < 10 else num_words(lo)))
    if n < 20:
        return [ONES[n]]
    if n < 100:
        t, o = divmod(n, 10)
        return [TENS[t]] + ([ONES[o]] if o else [])
    if n < 1000:
        h, r = divmod(n, 100)
        return [ONES[h], "hundred"] + (num_words(r) if r else [])
    if n < 1_000_000:
        th, r = divmod(n, 1000)
        return num_words(th) + ["thousand"] + (num_words(r) if r else [])
    m, r = divmod(n, 1_000_000)
    return num_words(m) + ["million"] + (num_words(r) if r else [])


def spoken(tok):
    """How a token is spoken, as a list of plain words ("1831," -> eighteen thirty one, "seventy-four" -> seventy four)."""
    out = []
    for part in re.split(r"[-\u2013\u2014/]", tok):
        t = part.replace(",", "") if re.fullmatch(r"[\d,]+[.!?;:]*", part.strip("\"'()")) else part
        digits = re.fullmatch(r"\W*(\d+)(st|nd|rd|th|s)?\W*", t)
        if digits:
            n = int(digits.group(1))
            out += num_words(n, year_style=len(digits.group(1)) == 4)
        else:
            k = norm(part)
            if k:
                out.append(k)
    return out or [norm(tok)]


def respell(words, tokens):
    """Give the script's spelling to the timed words. Both sides are compared in spoken form, so
    "1831" in the script matches "eighteen thirty one" from the recogniser and keeps the real times."""
    units, owner = [], []
    for ti, tok in enumerate(tokens):
        for u in spoken(tok):
            units.append(u); owner.append(ti)
    heard, htime = [], []
    for w in words:
        sp = spoken(w["text"])
        L = sum(len(x) for x in sp) or 1
        t = w["start"]
        for x in sp:
            d = (w["end"] - w["start"]) * len(x) / L
            heard.append(x); htime.append((t, t + d)); t += d
    sm = difflib.SequenceMatcher(a=units, b=heard, autojunk=False)
    times = [None] * len(units)
    for i, j, n in sm.get_matching_blocks():
        for k in range(n):
            times[i + k] = htime[j + k]
    # unmatched units: fill between the known neighbours
    known = [i for i, t in enumerate(times) if t]
    for i in range(len(units)):
        if times[i]:
            continue
        prev = max([k for k in known if k < i], default=None)
        nxt = min([k for k in known if k > i], default=None)
        s = times[prev][1] if prev is not None else 0.0
        e = times[nxt][0] if nxt is not None else s + 0.25 * (i - (prev or 0))
        gap = [k for k in range(prev + 1 if prev is not None else 0, nxt if nxt is not None else len(units))]
        pos = gap.index(i)
        times[i] = (s + (e - s) * pos / len(gap), s + (e - s) * (pos + 1) / len(gap))
    out = []
    for ti, tok in enumerate(tokens):
        idx = [i for i, o in enumerate(owner) if o == ti]
        out.append({"text": tok, "start": float(times[idx[0]][0]), "end": float(times[idx[-1]][1])})
    return out, sm.ratio()


# ---------- captions show numbers as digits ----------
_ONES = {w: i for i, w in enumerate("zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split())}
_TENS = {w: i * 10 for i, w in enumerate("_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()) if w != "_"}
_SCALE = {"hundred": 100, "thousand": 1000, "million": 1000000}
_UNITS = set("feet foot inch inches minute minutes second seconds hour hours mile miles percent dollar dollars buck bucks pound pounds yard yards year years day days week weeks month months kilometer kilometers metre metres meter meters kilogram kilograms degrees cents am pm oclock".split())


def _parts(tok):
    """'Seventy-four,' -> (['seventy', 'four'], trailing punctuation, leading punctuation) or None if not number words."""
    m = re.fullmatch(r"([\"'(\[]*)([A-Za-z]+(?:[-\u2013][A-Za-z]+)*)([.,!?;:\"')\]]*)", tok)
    if not m:
        return None
    ws = [w.lower() for w in re.split(r"[-\u2013]", m.group(2))]
    if not all(w in _ONES or w in _TENS or w in _SCALE for w in ws):
        return None
    return ws, m.group(3), m.group(1)


def _value(ws):
    total, cur = 0, 0
    for w in ws:
        if w in _ONES:
            cur += _ONES[w]
        elif w in _TENS:
            cur += _TENS[w]
        elif w == "hundred":
            cur = (cur or 1) * 100
        else:
            total += (cur or 1) * _SCALE[w]; cur = 0
    return total + cur


def to_digits(words):
    """Merge number words into digits for the caption text. Keeps the script's words in 'spoken'."""
    out, i, n = [], 0, len(words)
    while i < n:
        p = _parts(words[i]["text"])
        if not p:
            out.append(words[i]); i += 1; continue
        group, ws_all, j = [words[i]], list(p[0]), i
        trail = p[1]
        while not trail and j + 1 < n:
            bridge = 0
            if re.sub(r"[^a-z]", "", words[j + 1]["text"].lower()) == "and" and not re.search(r"[.,!?;:]$", words[j + 1]["text"]) and ws_all[-1] in _SCALE and j + 2 < n:
                bridge = 1  # "three hundred AND five": the "and" belongs to the number
            q = _parts(words[j + 1 + bridge]["text"])
            if not q:
                break
            nxt = q[0]
            # a number phrase continues only in a valid way: tens + ones, "<n> hundred/thousand", scale + smaller
            last = ws_all[-1]
            ok = (last in _TENS and len(nxt) == 1 and nxt[0] in _ONES and 0 < _ONES[nxt[0]] < 10) \
                or (nxt[0] in _SCALE) \
                or (last in _SCALE and (nxt[0] in _ONES or nxt[0] in _TENS) and _ONES.get(nxt[0], 1) != 0) \
                or (last in _ONES and nxt[0] in _SCALE)
            if not ok:
                break
            ws_all += nxt; group += words[j + 1:j + 2 + bridge]; trail = q[1]; j += 1 + bridge
        val = _value(ws_all)
        nxt_tok = re.sub(r"[^a-z]", "", words[j + 1]["text"].lower()) if j + 1 < n else ""
        a_prefix = out and out[-1]["text"].lower() == "a" and ws_all[0] in _SCALE
        if val >= 10 or nxt_tok in _UNITS or a_prefix:
            if a_prefix:
                prev = out.pop(); group = [prev] + group
            text = f"{p[2]}{val:,}{trail}"
            out.append({"text": text, "spoken": " ".join(g["text"] for g in group), "start": group[0]["start"], "end": group[-1]["end"]})
        else:
            out.extend(group)
        i = j + 1
    return out


def snap(words, db, hop):
    moved = 0
    for w in words:
        s = w["start"]
        a, b = int((s - 0.10) / hop), int((s + 0.06) / hop)
        a, b = max(a, 1), min(b, len(db) - 2)
        if b <= a:
            continue
        seg = db[a:b]
        j = int(np.argmin(seg))
        lo = seg[j]
        peak = db[a + j: min(len(db), a + j + int(0.10 / hop))].max()
        if peak - lo < 9.0:  # no clear dip: connected speech, keep the recogniser's time
            continue
        k = a + j
        while k < len(db) - 1 and db[k] < lo + 0.5 * (peak - lo):
            k += 1
        k = max(a + j, k - int(0.015 / hop))  # a few ms before the half-way rise
        ns = k * hop
        if abs(ns - s) > 0.004:
            moved += 1
        w["start"] = ns
    return moved


def tidy(words, dur):
    for i, w in enumerate(words):
        w["start"] = max(0.0, min(w["start"], dur))
        if i:
            w["start"] = max(w["start"], words[i - 1]["start"] + 0.02)
            words[i - 1]["end"] = min(words[i - 1]["end"], w["start"])
            words[i - 1]["end"] = max(words[i - 1]["end"], words[i - 1]["start"] + 0.02)
    if words:
        words[-1]["end"] = min(max(words[-1]["end"], words[-1]["start"] + 0.05), dur)
    for w in words:
        w["start"], w["end"] = round(w["start"], 3), round(w["end"], 3)
        w.pop("spread", None)
    return words


def main():
    args = [a for a in sys.argv[1:] if a != "--digits"]
    if len(args) != 4:
        raise SystemExit(__doc__)
    wav, tr, script, out = args
    x, sr = load_audio(wav)
    dur = len(x) / sr
    words = load_words(tr)
    tokens = script_tokens(script)
    fixed, ratio = respell(words, tokens)
    db, hop = envelope_db(x, sr)
    moved = snap(fixed, db, hop)
    fixed = tidy(fixed, dur)
    if "--digits" in sys.argv:
        fixed = to_digits(fixed)
    Path(out).write_text(json.dumps(fixed, indent=1), encoding="utf-8")
    spread = len(fixed) - sum(1 for _ in fixed)
    print(json.dumps({
        "words": len(fixed), "script_tokens": len(tokens), "match_ratio": round(ratio, 3),
        "starts_snapped": moved, "audio_seconds": round(dur, 3),
        "words_per_second": round(len(fixed) / max(dur, 1e-6), 2),
        "warning": None if ratio > 0.9 else "transcript differs a lot from the script: listen and check",
    }))


if __name__ == "__main__":
    main()
