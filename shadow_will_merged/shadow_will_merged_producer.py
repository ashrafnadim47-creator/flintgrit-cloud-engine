#!/usr/bin/env python3
"""
Shadow Will Merged Super Engine Producer
Combines:
- Skill 2 (cartoon-short-kit Version 6): Playwright WebGL Ink + DOF + Painted Toon + Bean-Head Cast + Audio Synth
- Skill 1 (ricksclips-engine): Modular 3D Props, Edge-TTS Voiceover, Gemini Story Architect, Anti-Duplicate Queue, YouTube Uploader
"""
import argparse
import asyncio
import json
import os
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
WEB_DIR = HERE / "web"
WORK_DIR = HERE / "work"
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(HERE / "stories"))

from curated_stories import CURATED_STORIES
from render_frames import render_frames
from audio_synth import synthesize_mix

try:
    import youtube_cloud_uploader
except Exception:
    youtube_cloud_uploader = None


def load_history():
    hfile = REPO_ROOT / "history_shadow_will.json"
    if not hfile.exists():
        return hfile, []
    try:
        data = json.loads(hfile.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return hfile, list(data.get("covered_ids", []))
        if isinstance(data, list):
            return hfile, data
    except Exception:
        pass
    return hfile, []


def save_history(hfile: Path, history: list, item_id: str):
    if item_id not in history:
        history.append(item_id)
    hfile.write_text(json.dumps(history, indent=2), encoding="utf-8")
    print(f"[ShadowWillMerged] Recorded '{item_id}' in {hfile.name}")


async def generate_tts(text: str, out_mp3: Path, voice: str = "en-US-ChristopherNeural"):
    import edge_tts
    comm = edge_tts.Communicate(text, voice, rate="+5%")
    await comm.save(str(out_mp3))


def get_duration(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    return float(out)


def build_ass_subtitles(phrases_json: Path, out_ass: Path, width: int, height: int):
    data = json.loads(phrases_json.read_text(encoding="utf-8"))
    phrases = data.get("phrases", [])
    margin_v = int(height * 0.16)
    font_size = int(width * 0.056)
    header = (
        "[Script Info]\nScriptType: v4.00+\n"
        f"PlayResX: {width}\nPlayResY: {height}\n\n"
        "[V4+ Styles]\n"
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, "
        "Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
        "Alignment, MarginL, MarginR, MarginV, Encoding\n"
        f"Style: Default,DejaVu Sans,{font_size},&H00FFFFFF,&H0000FFFF,&H00000000,&H80000000,"
        f"-1,0,0,0,100,100,0,0,1,4,2,2,40,40,{margin_v},1\n\n"
        "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
    )

    def fmt(sec: float) -> str:
        h = int(sec // 3600)
        m = int((sec % 3600) // 60)
        s = sec % 60
        return f"{h}:{m:02d}:{s:05.2f}"

    lines = [header]
    for p in phrases:
        txt = p["text"].replace("\n", " ").strip()
        if not txt:
            continue
        lines.append(f"Dialogue: 0,{fmt(p['s'])},{fmt(p['e'])},Default,,0,0,0,,{txt}\n")
    out_ass.write_text("".join(lines), encoding="utf-8")


def try_gemini_story(history: list):
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        return None
    topics = [
        "The Man Who Sold the Eiffel Tower Twice in 1925",
        "How Two Thieves Stole a 200-Ton Iron Bridge Overnight",
        "The Computer Genius Who Beat Las Vegas Using a Shoe Microcomputer",
        "The Bank Robbers Who Dug a 250ft Tunnel Into a Vault",
        "The Great Canadian Maple Syrup Heist Worth $18 Million",
    ]
    unseen = [t for t in topics if t not in history] or topics
    topic = unseen[0]

    prompt = (
        f"Write a gripping 60-word YouTube Shorts narration script (4 punchy sentences) about: {topic}. "
        "Return STRICT JSON ONLY: {\"title\": \"... #shorts\", \"description\": \"...\", \"tags\": [\"shorts\"], \"mood\": \"heist\", \"script\": \"...\"}"
    )
    for model in ["gemini-1.5-flash", "gemini-2.0-flash-exp", "gemini-1.5-pro"]:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        body = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode("utf-8")
        req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=25) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                txt = res["candidates"][0]["content"]["parts"][0]["text"]
                txt = txt.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
                meta = json.loads(txt)
                # Pair Gemini script with a matching 3D world template from our curated set
                base = CURATED_STORIES[1] if meta.get("mood") == "heist" else CURATED_STORIES[2]
                return {
                    "id": topic,
                    "title": meta["title"],
                    "description": meta["description"],
                    "tags": meta.get("tags", ["shorts", "animation"]),
                    "mood": meta.get("mood", "mystery"),
                    "script": meta["script"],
                    "story_js": base["story_js"],
                }
        except Exception as e:
            print(f"[Gemini Story] {model} skipped: {e}")
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--format", default="short", choices=["short", "long"])
    ap.add_argument("--no-upload", action="store_true")
    ap.add_argument("--story-id", default=None)
    args = ap.parse_args()

    width, height = (1080, 1920) if args.format == "short" else (1920, 1080)
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    frames_dir = WORK_DIR / "frames"
    if frames_dir.exists():
        shutil.rmtree(frames_dir)
    frames_dir.mkdir(parents=True, exist_ok=True)

    hfile, history = load_history()

    story = None
    if args.story_id:
        story = next((s for s in CURATED_STORIES if s["id"] == args.story_id), None)
    if not story:
        story = try_gemini_story(history)
    if not story:
        unvisited = [s for s in CURATED_STORIES if s["id"] not in history]
        story = unvisited[0] if unvisited else CURATED_STORIES[len(history) % len(CURATED_STORIES)]

    print(f"[ShadowWillMerged] Producing '{story['id']}' ({width}x{height})")

    # Stage story.js into web/story.js
    dest_story = WEB_DIR / "story.js"
    if "story_js_path" in story and Path(story["story_js_path"]).exists():
        shutil.copy2(story["story_js_path"], dest_story)
    else:
        dest_story.write_text(story["story_js"], encoding="utf-8")

    # 1. Generate Voiceover
    voice_mp3 = WORK_DIR / "voice.mp3"
    script_txt = WORK_DIR / "script.txt"
    script_txt.write_text(story["script"], encoding="utf-8")
    asyncio.run(generate_tts(story["script"], voice_mp3))
    dur = get_duration(voice_mp3)
    total_frames = int(round(dur * 30))

    # Update TOTAL in story.js if needed so video matches voice duration cleanly
    s_text = dest_story.read_text(encoding="utf-8")
    if "TOTAL =" in s_text:
        import re
        s_text = re.sub(r"TOTAL\s*=\s*\d+", f"TOTAL = {total_frames}", s_text, count=1)
        dest_story.write_text(s_text, encoding="utf-8")

    # 2. Align Word/Phrase Timings
    subprocess.run(
        [sys.executable, str(HERE / "timing.py"), str(voice_mp3), str(script_txt), "--out", str(WORK_DIR)],
        check=True,
    )
    ass_path = WORK_DIR / "subs.ass"
    build_ass_subtitles(WORK_DIR / "phrases.json", ass_path, width, height)

    # 3. Synthesize Music + SFX + Loudnorm
    mix_raw = WORK_DIR / "mix_raw.wav"
    mix_wav = WORK_DIR / "mix.wav"
    synthesize_mix(voice_mp3, mix_raw, dur, mood=story.get("mood", "mystery"))
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-i", str(mix_raw), "-af", "loudnorm=I=-14:TP=-1.5:LRA=7", "-ar", "48000", "-ac", "2", str(mix_wav)],
        check=True,
    )

    # 4. Render WebGL Frames via Playwright
    render_frames(WEB_DIR, frames_dir, start_f=0, end_f=total_frames - 1, step=1, quality=0.98, width=width, height=height)

    # 5. Encode Final MP4 with Burned-in ASS Captions (High-Quality Ultra-Sharp Settings)
    out_mp4 = REPO_ROOT / f"shadow_will_{args.format}_{story['id'][:24]}.mp4"
    ass_escaped = str(ass_path).replace("\\", "/").replace(":", "\\:")
    subprocess.run(
        [
            "ffmpeg", "-v", "error", "-y",
            "-framerate", "30",
            "-i", str(frames_dir / "f%04d.jpg"),
            "-i", str(mix_wav),
            "-vf", f"ass='{ass_escaped}'",
            "-map", "0:v:0", "-map", "1:a:0",
            "-c:v", "libx264", "-preset", "slow", "-crf", "15", "-b:v", "8M", "-maxrate", "12M", "-bufsize", "16M", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "256k", "-shortest", "-movflags", "+faststart",
            str(out_mp4),
        ],
        check=True,
    )
    print(f"[ShadowWillMerged] SUCCESS! Rendered {out_mp4} ({out_mp4.stat().st_size} bytes)")

    save_history(hfile, history, story["id"])

    if not args.no_upload and youtube_cloud_uploader and os.environ.get("YT_REFRESH_TOKEN"):
        youtube_cloud_uploader.upload_video_file(
            str(out_mp4),
            story["title"],
            story["description"],
            story.get("tags", ["shorts", "animation"]),
            os.environ["YT_CLIENT_ID"],
            os.environ["YT_CLIENT_SECRET"],
            os.environ["YT_REFRESH_TOKEN"],
            privacy_status="public",
        )


if __name__ == "__main__":
    main()
