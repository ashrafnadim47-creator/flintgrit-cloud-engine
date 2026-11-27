"""Step 1 of the voice: decode the user's file and normalise its loudness.

Usage:  python prep_voice.py <voice file (mp3, wav, m4a, aac, flac, ogg)> <out voice_norm.wav>

- Decodes with FFmpeg to 48 kHz mono 16-bit.
- Removes DC offset and sets the integrated loudness to -16 LUFS (ITU-R BS.1770), with a peak limiter at
  -1.5 dBTP. The final mix sets the delivery loudness (-14.5 LUFS) later.
- Prints a JSON report (input loudness, gain, length).
"""
import json
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sound.mix import lufs, limiter, true_peak_db  # noqa: E402
from sound.synth import SR, undb  # noqa: E402


def main():
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    src, out = sys.argv[1], sys.argv[2]
    tmp = Path(tempfile.mkdtemp(prefix="ricksclips_")) / "dec.wav"
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostdin", "-y", "-i", src, "-ac", "1", "-ar", str(SR), "-c:a", "pcm_s16le", str(tmp)], capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("FFmpeg could not read the voice file: " + r.stderr[-400:])
    with wave.open(str(tmp)) as w:
        x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float64) / 32768.0
    if len(x) < SR:
        raise SystemExit("The voice file is shorter than one second.")
    x = x - np.mean(x)
    before = lufs(x)
    gain = -16.0 - before
    y = limiter((x * undb(gain))[:, None], -1.5)[:, 0]
    with wave.open(out, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())
    print(json.dumps({"input_lufs": round(before, 2), "gain_db": round(gain, 2), "output_lufs": round(lufs(y), 2),
                      "true_peak_dbtp": round(true_peak_db(y), 2), "seconds": round(len(y) / SR, 3)}))


if __name__ == "__main__":
    main()
