#!/usr/bin/env python3
import sys
import os
import asyncio
import argparse
import subprocess
import tempfile
import pathlib
import edge_tts

async def synth(txt, out_mp3):
    comm = edge_tts.Communicate(txt, "en-US-ChristopherNeural", rate="-2%")
    await comm.save(out_mp3)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("txt")
    ap.add_argument("out")
    args = ap.parse_args()

    content = pathlib.Path(args.txt).read_text(encoding="utf-8").strip()
    lines = [p.strip() for p in content.split("\n\n") if p.strip()]
    if not lines:
        lines = [p.strip() for p in content.splitlines() if p.strip()]
    if not lines:
        lines = [content]

    with tempfile.TemporaryDirectory() as tmp:
        td = pathlib.Path(tmp)
        clips = []
        silence = td / "silence.wav"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono", "-t", "0.75", str(silence)], check=True)
        
        for idx, line in enumerate(lines):
            mp3 = td / f"l_{idx}.mp3"
            wav = td / f"l_{idx}.wav"
            asyncio.run(synth(line, str(mp3)))
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(mp3), "-ar", "48000", "-ac", "1", str(wav)], check=True)
            clips.append(str(wav))
            if idx < len(lines) - 1:
                clips.append(str(silence))
                
        lst = td / "list.txt"
        lst.write_text("".join(f"file '{c}'\n" for c in clips), encoding="utf-8")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", args.out], check=True)

if __name__ == "__main__":
    main()
