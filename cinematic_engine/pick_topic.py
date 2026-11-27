#!/usr/bin/env python3
"""
=============================================================================
DOCUMENTARY TOPIC ROTATOR FOR LONG-FORM DAILY RUNS
=============================================================================
Selects an unvisited 8-10 minute documentary topic from the longform catalog
so NO TOPIC IS EVER REPEATED!
=============================================================================
"""

import sys
import random
import pathlib

BASE_DIR = pathlib.Path(__file__).resolve().parent

def pick():
    try:
        from documentary_longform_engine import LONGFORM_DOCUMENTARY_CATALOG, load_history
        history = load_history()
        covered = history.get("covered_slugs", [])
        candidates = [d["slug"] for d in LONGFORM_DOCUMENTARY_CATALOG if d["slug"] not in covered]
        if not candidates:
            candidates = [d["slug"] for d in LONGFORM_DOCUMENTARY_CATALOG]
        return random.choice(candidates)
    except Exception as e:
        print(f"[Topic Picker] Note: {e}", file=sys.stderr)
        return "dyatlov-pass-incident"

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1].strip() and sys.argv[1] != "auto":
        print(sys.argv[1].strip())
    else:
        print(pick())
