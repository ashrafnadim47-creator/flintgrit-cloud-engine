"""
RicksClips Cloud Runner for GitHub Actions
Renders vertical 9:16 animated story shorts in the cloud and publishes directly to YouTube.
"""
import os
import sys
import json
import shutil
import asyncio
import argparse
import subprocess
from pathlib import Path

try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
sys.path.insert(0, str(REPO_ROOT))
import youtube_cloud_uploader

def run_cmd(cmd, cwd=None, env=None):
    print(f"[CloudRunner CMD] {cmd}")
    run_env = os.environ.copy()
    if env:
        run_env.update(env)
    res = subprocess.run(
        cmd,
        shell=True,
        cwd=str(cwd or HERE),
        env=run_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    print(res.stdout)
    if res.returncode != 0:
        raise RuntimeError(f"Command failed with code {res.returncode}:\n{res.stdout}")
    return res.stdout

async def generate_voice(script_text, out_mp3):
    import edge_tts
    communicate = edge_tts.Communicate(script_text, "en-US-ChristopherNeural", rate="+6%")
    await communicate.save(str(out_mp3))
    print(f"[CloudRunner] Voiceover generated: {out_mp3}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--short", default="auto", help="Short number or 'auto'")
    parser.add_argument("--no-upload", action="store_true", help="Skip YouTube upload, just render and preserve video")
    args = parser.parse_args()

    short_dir = HERE / "current_short"
    short_dir.mkdir(parents=True, exist_ok=True)

    # AUTO-PILOT ENGINE SELECTION:
    history_file = REPO_ROOT / "history_shadow_will.json"
    history = []
    if history_file.exists():
        try:
            history = json.loads(history_file.read_text(encoding="utf-8"))
        except Exception:
            history = []

    use_preauthored = False
    candidate_dir = None

    if str(args.short).isdigit():
        req_dir = REPO_ROOT / "ready_shorts" / f"short_{args.short}"
        if req_dir.exists() and (req_dir / "script.md").exists():
            candidate_dir = req_dir
            use_preauthored = True
    elif args.short == "auto":
        ready_root = REPO_ROOT / "ready_shorts"
        if ready_root.exists():
            avail_shorts = sorted(list(ready_root.glob("short_*")), key=lambda p: int(p.name.split("_")[-1]) if p.name.split("_")[-1].isdigit() else 999)
            unvisited_shorts = [s for s in avail_shorts if s.name not in history and s.name != "short_auto"]
            if unvisited_shorts:
                candidate_dir = unvisited_shorts[0]
                use_preauthored = True
                print(f"[AutoPilot] Selected Unvisited 3D Story from Ready Shorts Queue: {candidate_dir.name}")

    if use_preauthored and candidate_dir and candidate_dir.exists():
        for f in ["script.md", "seo.md", "story.js"]:
            if (candidate_dir / f).exists():
                shutil.copy2(candidate_dir / f, short_dir / f)
        if (candidate_dir / "audio" / "sound.json").exists():
            (short_dir / "audio").mkdir(exist_ok=True, parents=True)
            shutil.copy2(candidate_dir / "audio" / "sound.json", short_dir / "audio" / "sound.json")

        if candidate_dir.name not in history:
            history.append(candidate_dir.name)
            try:
                history_file.write_text(json.dumps(history, indent=2), encoding="utf-8")
                print(f"[AutoPilot] Recorded '{candidate_dir.name}' into history_shadow_will.json")
            except Exception as e:
                print(f"[AutoPilot Note] Could not save history: {e}")

        print(f"[AutoPilot] Successfully staged 3D Short {candidate_dir.name} into current_short!")
    else:
        print("[AutoPilot] Activating Upgraded Autonomous Gemini 3D Architect Engine...")
        sys.path.insert(0, str(HERE / "scripts"))
        import gemini_architect

        VIRAL_TOPICS = [
            "The Man Who Stole $100M in Diamonds by Making Keys Out of Chocolate",
            "How One Typo Cost NASA $80,000,000 on a Mission to Venus",
            "The Bank Robbers Who Dug a 250ft Underground Tunnel Straight into the Vault",
            "The Fake Pilot Who Flew 250 Commercial Flights Without Any Aviation License",
            "The Man Who Sold the Eiffel Tower Twice for Millions in 1925",
            "How Two Thieves Stole a 200-Ton Iron Bridge Overnight in Russia",
            "The World War 2 Soldier Who Fought With a Scottish Broadsword and Longbow",
            "The Computer Genius Who Beat Las Vegas Casinos Using a Microchip in His Shoe",
            "The Great Canadian Maple Syrup Heist: Stealing $18M of Liquid Gold",
            "The Incredible True Story of the Greenbrier Secret Bunker for US Congress"
        ]

        unvisited = [t for t in VIRAL_TOPICS if t not in history]
        if not unvisited:
            unvisited = VIRAL_TOPICS

        chosen_topic = os.environ.get("RICKSCLIPS_TOPIC") or unvisited[0]
        print(f"[AutoPilot] Selected Viral Story Topic: '{chosen_topic}'")

        bundle = gemini_architect.generate_short_with_gemini(chosen_topic)
        if not bundle:
            raise RuntimeError(f"Gemini Architect could not generate story for: {chosen_topic}")

        # Record topic in history
        if chosen_topic not in history:
            history.append(chosen_topic)
            try:
                history_file.write_text(json.dumps(history, indent=2), encoding="utf-8")
                print(f"[AutoPilot] Recorded '{chosen_topic}' into history_shadow_will.json")
            except Exception as e:
                print(f"[AutoPilot Note] Could not save history: {e}")

        (short_dir / "script.md").write_text(bundle["script"], encoding="utf-8")
        (short_dir / "story.js").write_text(bundle["story_js"], encoding="utf-8")

        seo_md = f"## Title\n{bundle.get('title', chosen_topic)} #shorts\n\n## Description\n{bundle.get('description', '')}\n\n## Tags\n{', '.join(bundle.get('tags', ['shorts', 'animation', 'ricks clips']))}\n"
        (short_dir / "seo.md").write_text(seo_md, encoding="utf-8")

        sound_json = {
            "music": {"track": "synth_pulse", "vol": 0.22, "duck": 0.08},
            "cues": [{"t": 0.1, "kind": "whoosh", "vol": 0.5}]
        }
        for sfx in bundle.get("sound_effects", []):
            sound_json["cues"].append({
                "word": sfx.get("word", "the"),
                "kind": sfx.get("preset", "click"),
                "vol": sfx.get("volume", 0.5)
            })
        (short_dir / "audio").mkdir(parents=True, exist_ok=True)
        with open(short_dir / "audio" / "sound.json", "w", encoding="utf-8") as f:
            json.dump(sound_json, f, indent=2)

        print(f"[AutoPilot] Dynamic 3D story, script, and sound cues generated successfully for Short #{args.short}!")

    script_file = short_dir / "script.md"
    if not script_file.exists():
        raise FileNotFoundError(f"Missing script.md in {short_dir}")

    script_text = script_file.read_text(encoding="utf-8").strip()

    voice_dir = short_dir / "voice"
    voice_dir.mkdir(parents=True, exist_ok=True)
    audio_dir = short_dir / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)

    voice_mp3 = voice_dir / "voice.mp3"
    voice_norm = voice_dir / "voice_norm.wav"
    transcript1 = voice_dir / "transcript1.json"
    words_raw = voice_dir / "words_raw.json"
    trimmed = voice_dir / "trimmed.wav"
    words_shifted = voice_dir / "words_shifted.json"
    final_wav = voice_dir / "final.wav"
    words_paced = voice_dir / "words_paced.json"
    transcript2 = voice_dir / "transcript2.json"
    words_json = short_dir / "words.json"
    mix_wav = audio_dir / "mix.wav"
    sound_json = audio_dir / "sound.json"
    final_mp4 = short_dir / "final.mp4"

    if "RICKSCLIPS_BROWSER" not in os.environ:
        chrome_cand = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
        if chrome_cand.exists():
            os.environ["RICKSCLIPS_BROWSER"] = str(chrome_cand)
            print(f"[CloudRunner] Auto-detected Chrome at {chrome_cand}")

    print("=== STEP 1: GENERATE VOICEOVER ===")
    asyncio.run(generate_voice(script_text, voice_mp3))

    print("=== STEP 2: NORMALIZE AUDIO ===")
    run_cmd(f'"{sys.executable}" "{HERE}/scripts/prep_voice.py" "{voice_mp3}" "{voice_norm}"')

    print("=== STEP 3: TRANSCRIBE INITIAL VOICE ===")
    run_cmd(f'"{sys.executable}" "{HERE}/scripts/whisper_words.py" "{voice_norm}" "small.en" "{transcript1}"')

    print("=== STEP 4: ALIGN WORDS TO SCRIPT ===")
    run_cmd(f'"{sys.executable}" "{HERE}/scripts/fix_words.py" "{voice_norm}" "{transcript1}" "{script_file}" "{words_raw}"')

    print("=== STEP 5: TRIM SILENCE ===")
    run_cmd(f'"{sys.executable}" "{HERE}/scripts/trim_silence.py" "{voice_norm}" "{words_raw}" "{trimmed}" "{words_shifted}"')

    print("=== STEP 6: PACE AUDIO ===")
    run_cmd(f'"{sys.executable}" "{HERE}/scripts/pace_voice.py" "{trimmed}" "{words_shifted}" "{final_wav}" "{words_paced}"')

    print("=== STEP 7: TRANSCRIBE PACED AUDIO ===")
    run_cmd(f'"{sys.executable}" "{HERE}/scripts/whisper_words.py" "{final_wav}" "small.en" "{transcript2}"')

    print("=== STEP 8: FINAL WORDS SNAP ===")
    run_cmd(f'"{sys.executable}" "{HERE}/scripts/fix_words.py" "{final_wav}" "{transcript2}" "{script_file}" "{words_json}" --digits')

    print("=== STEP 9: CREATE REMOTION PROJECT ===")
    proj_dir = short_dir / "project"
    if proj_dir.exists():
        shutil.rmtree(proj_dir)

    env = {"RICKSCLIPS_WORK": str(HERE)}
    run_cmd(f'node "{HERE}/scripts/project.mjs" create "{short_dir}" --quality 1080p --engine-dir "{HERE}"', env=env)

    # Copy our crafted story.js into project/src/story.js
    custom_story = short_dir / "story.js"
    dest_story = proj_dir / "src" / "story.js"
    if custom_story.exists():
        shutil.copy2(custom_story, dest_story)
        print(f"[CloudRunner] Copied custom story.js into {dest_story}")

    print("=== STEP 10: SYNTHESIZE PROCEDURAL MUSIC & SFX ===")
    run_cmd(f'"{sys.executable}" "{HERE}/scripts/make_sound.py" "{sound_json}" "{final_wav}" "{audio_dir}"')

    print("=== STEP 11: ATTACH MIX AUDIO & WORDS ===")
    run_cmd(f'node "{HERE}/scripts/project.mjs" audio "{short_dir}" "{mix_wav}" "{words_json}"', env=env)

    print("=== STEP 12: RENDER 1080P VIDEO IN CLOUD ===")
    run_cmd(f'node "{HERE}/scripts/render.mjs" video "{short_dir}"', env=env)

    if not final_mp4.exists():
        raise FileNotFoundError(f"Render finished but {final_mp4} was not produced!")

    print(f"[CloudRunner] Video rendered successfully! Size: {final_mp4.stat().st_size} bytes")

    # Preserve into saved shorts directory
    saved_dir = REPO_ROOT / "ready_shorts" / f"short_{args.short}"
    saved_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(final_mp4, saved_dir / "final.mp4")
    if (short_dir / "script.md").exists():
        shutil.copy2(short_dir / "script.md", saved_dir / "script.md")
    if (short_dir / "seo.md").exists():
        shutil.copy2(short_dir / "seo.md", saved_dir / "seo.md")
    print(f"[CloudRunner] Preserved video and metadata into: {saved_dir}")

    if args.no_upload:
        print("=" * 60)
        print(f"[CloudRunner COMPLETE] Video rendered and saved safely for Short #{args.short}!")
        print(f"[CloudRunner COMPLETE] Path: {saved_dir / 'final.mp4'}")
        print("[CloudRunner COMPLETE] YouTube upload skipped per user request (will upload tomorrow).")
        print("=" * 60)
        return

    print("=== STEP 13: PUBLISH DIRECTLY TO YOUTUBE ===")
    seo_file = short_dir / "seo.md"
    title = f"Mindblowing True Story #{args.short} #shorts"
    description = "A bizarre true story animated in minimalist Ricks Clips style."
    tags = ["shorts", "history", "facts", "animation", "ricks clips"]

    if seo_file.exists():
        seo_text = seo_file.read_text(encoding="utf-8")
        for block in seo_text.split("##"):
            block = block.strip()
            if block.startswith("Title"):
                title = block.replace("Title", "").strip().split("\n")[0].strip()
            elif block.startswith("Description"):
                description = block.replace("Description", "").strip()
            elif block.startswith("Tags"):
                tag_line = block.replace("Tags", "").strip().split("\n")[0].strip()
                tags = [t.strip() for t in tag_line.split(",") if t.strip()]

    cid = os.environ.get("YT_CLIENT_ID") or os.environ.get("YOUTUBE_CLIENT_ID")
    csec = os.environ.get("YT_CLIENT_SECRET") or os.environ.get("YOUTUBE_CLIENT_SECRET")
    rtoken = os.environ.get("YT_REFRESH_TOKEN") or os.environ.get("YOUTUBE_REFRESH_TOKEN")

    if cid and csec and rtoken:
        creds = {"client_id": cid, "client_secret": csec, "refresh_token": rtoken}
    else:
        token_file = REPO_ROOT / "youtube_token.json"
        if token_file.exists():
            with open(token_file, "r") as f:
                creds = json.load(f)
        else:
            creds = {"client_id": cid, "client_secret": csec, "refresh_token": rtoken}

    res = youtube_cloud_uploader.upload_video_file(
        video_file=str(final_mp4),
        title=title,
        description=description,
        tags=tags,
        client_id=creds["client_id"],
        client_secret=creds["client_secret"],
        refresh_token=creds["refresh_token"],
        privacy_status="public"
    )

    vid_id = res.get("id")
    print("=" * 60)
    print(f"[CloudRunner COMPLETE] Video ID: {vid_id}")
    print(f"[CloudRunner COMPLETE] Live URL: https://youtube.com/watch?v={vid_id}")
    print("=" * 60)

if __name__ == "__main__":
    main()
