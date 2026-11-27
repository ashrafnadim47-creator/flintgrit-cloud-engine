"""Entry point: python make_sound.py <sound.json> <final_voice.wav> <out_dir>  (see sound/mix.py)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sound.mix import main  # noqa: E402

if __name__ == "__main__":
    main()
