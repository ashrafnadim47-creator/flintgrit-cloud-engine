"""Optional gentle speed-up of a slow voice, keeping the pitch.

Usage:  python pace_voice.py <voice.wav> <words.json> <out.wav> <out words.json>

The reference voice runs at about 3.3-3.9 words per second. The plugin does not have to match that, but when the
voice is slower than 3.2 words per second it is sped up with FFmpeg's pitch-preserving tempo filter, by at most
1.15x (the limit stays far under 1.2x because a clean voice matters more than the pace). Word times are scaled by the
same factor. If the speed-up cannot be done, the original voice is kept. Prints a JSON report.
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

SLOW_BELOW = 3.2
TARGET = 3.4
MAX_FACTOR = 1.15


def main():
    if len(sys.argv) != 5:
        raise SystemExit(__doc__)
    wav, wj, out_wav, out_words = sys.argv[1:]
    words = json.loads(Path(wj).read_text(encoding="utf-8"))
    if len(words) < 2:
        raise SystemExit("words.json is empty")
    span = words[-1]["end"] - words[0]["start"]
    wps = len(words) / max(span, 1e-6)
    factor = 1.0
    if wps < SLOW_BELOW:
        factor = round(min(MAX_FACTOR, TARGET / wps), 3)
    applied = False
    if factor > 1.005:
        r = subprocess.run(["ffmpeg", "-hide_banner", "-nostdin", "-y", "-i", wav, "-filter:a", f"atempo={factor}", "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "1", out_wav], capture_output=True, text=True)
        applied = r.returncode == 0 and Path(out_wav).exists()
    if not applied:
        factor = 1.0
        if Path(wav).resolve() != Path(out_wav).resolve():
            shutil.copyfile(wav, out_wav)
        scaled = words
    else:
        scaled = [{"text": w["text"], "start": round(w["start"] / factor, 3), "end": round(w["end"] / factor, 3)} for w in words]
    Path(out_words).write_text(json.dumps(scaled, indent=1), encoding="utf-8")
    new_span = scaled[-1]["end"] - scaled[0]["start"]
    print(json.dumps({"words_per_second_before": round(wps, 2), "speed_up_factor": factor, "applied": applied,
                      "words_per_second_after": round(len(scaled) / max(new_span, 1e-6), 2)}))


if __name__ == "__main__":
    main()
