"""Word timestamps with faster-whisper (OpenAI Whisper turbo, or the small English model on small machines).

Usage:  python whisper_words.py <voice.wav> <model dir> <out transcript.json>
        python whisper_words.py --selftest <model dir>
Writes [{"text", "start", "end"}] per recognised word (CPU, int8). The model folder is the one setup downloaded.
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np


def load(model_dir):
    import os
    from faster_whisper import WhisperModel
    name = model_dir if os.path.exists(model_dir) else "small.en"
    return WhisperModel(name, device="cpu", compute_type="int8")


def decode(wav):
    # decode with FFmpeg ourselves (16 kHz mono float), so faster-whisper never needs PyAV's file reader
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", wav, "-ac", "1", "-ar", "16000", "-f", "s16le", "-"], capture_output=True)
    if r.returncode != 0:
        raise SystemExit("FFmpeg could not read " + wav)
    return np.frombuffer(r.stdout, np.int16).astype(np.float32) / 32768.0


def main():
    a = sys.argv[1:]
    if len(a) == 2 and a[0] == "--selftest":
        model = load(a[1])
        t = np.arange(16000, dtype=np.float32) / 16000
        audio = (0.1 * np.sin(2 * np.pi * 440 * t)).astype(np.float32)
        segs, _ = model.transcribe(audio, language="en", word_timestamps=True, vad_filter=False)
        list(segs)
        print(json.dumps({"selftest": "ok"}))
        return
    if len(a) != 3:
        raise SystemExit(__doc__)
    wav, model_dir, out = a
    model = load(model_dir)
    audio = decode(wav)
    segments, _info = model.transcribe(audio, language="en", word_timestamps=True, vad_filter=False, beam_size=5, condition_on_previous_text=False)
    words = []
    for seg in segments:
        for w in seg.words or []:
            words.append({"text": w.word, "start": round(float(w.start), 3), "end": round(float(w.end), 3)})
    Path(out).write_text(json.dumps(words, indent=1), encoding="utf-8")
    print(json.dumps({"engine": "faster-whisper", "words": len(words), "out": out}))


if __name__ == "__main__":
    main()
