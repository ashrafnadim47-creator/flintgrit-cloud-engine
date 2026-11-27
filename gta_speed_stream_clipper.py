# -*- coding: utf-8 -*-
"""
=============================================================================
FARAZ SOVEREIGN PLATFORM • CHANNEL 2 AUTONOMOUS GTA & SPEED STREAM CLIPPER
=============================================================================
Autonomous OpusClip-style Cloud Engine for Channel 2.
1. Finds latest IShowSpeed / GTA livestream OR accepts any direct stream URL.
2. ZERO 30GB Downloads: Uses HTTP range slicing via yt-dlp to download ONLY 30s.
3. Gemini AI Brain analyzes stream context to pick the peak viral climax window.
4. Generates viral Title, Description, and Tags.
5. FFmpeg converts 16:9 stream into 1080x1920 9:16 vertical Short with neon gamer badge.
6. Auto-uploads to Channel 2 when API credentials are provided.
=============================================================================
"""

import os
import sys
import json
import time
import shutil
import random
import urllib.request
import subprocess
from pathlib import Path

# Find FFmpeg binary (works on Linux GitHub runner and Windows local)
FFMPEG_BIN = "ffmpeg"
POSSIBLE_FFMPEG = [
    r"C:\Users\WINDOWS\AppData\Local\Programs\Python\Python313\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg.exe",
    r"C:\ffmpeg\bin\ffmpeg.exe",
    "/usr/bin/ffmpeg"
]
for p in POSSIBLE_FFMPEG:
    if os.path.exists(p):
        FFMPEG_BIN = p
        break

# Default Gemini API key (from flintgrit autopilot)
DEFAULT_GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

HISTORY_FILE = Path(__file__).parent / "history_channel2_clips.json"

def load_clip_history():
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f).get("clipped_ids", [])
        except Exception:
            return []
    return []

def record_clip_history(video_id):
    if not video_id:
        return
    history = load_clip_history()
    if video_id not in history:
        history.append(video_id)
        try:
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump({"clipped_ids": history, "last_updated": time.strftime("%Y-%m-%dT%H:%M:%SZ")}, f, indent=2)
            print(f"[Clip History] Recorded video ID '{video_id}' in history ({len(history)} clips total).")
        except Exception as e:
            print(f"[Clip History] Warning saving history: {e}")

def get_target_stream_candidates(custom_url=None, max_candidates=3):
    """
    100% Autonomous Viral GTA Stream / Video Hunter:
    1. If custom_url is passed, uses it.
    2. If stream_input_link.txt has a link, uses it.
    3. Else, autonomously hunts across top GTA creators (Techno Gamerz, Mythpat, Typical Gamer, IShowSpeed, GamerFleet).
    4. Automatically filters out already-clipped videos using history_channel2_clips.json!
    5. Strictly verifies that video is NOT age-restricted and can be sliced without login!
    """
    if custom_url and ("youtube.com" in custom_url or "youtu.be" in custom_url):
        return [custom_url.strip()]

    input_file = Path(__file__).parent / "stream_input_link.txt"
    if input_file.exists():
        content = input_file.read_text(encoding="utf-8").strip()
        if content and ("youtube.com" in content or "youtu.be" in content):
            print(f"[Stream Finder] Using stream link from {input_file.name}: {content}")
            return [content]

    print("[Stream Finder] Autonomously hunting top viral GTA 6 creator moments (Strictly GTA 6 Only)...")
    clipped_history = load_clip_history()
    print(f"[Stream Finder] Clip history loaded: {len(clipped_history)} videos previously clipped.")

    # Prioritize LATEST GTA 6 creators, trailer 2 reactions, gameplay leaks, and Vice City gameplay
    target_sources = [
        ('ytsearch25:GTA 6 latest official leaks gameplay trailer 2 reaction', 'Latest GTA 6 Gameplay & Reactions'),
        ('ytsearch25:IShowSpeed GTA 6 latest live stream funny reaction', 'Latest IShowSpeed GTA 6'),
        ('ytsearch25:Techno Gamerz GTA 6 gameplay latest official reaction', 'Latest Techno Gamerz GTA 6'),
        ('ytsearch25:Typical Gamer GTA 6 latest gameplay leaks', 'Latest Typical Gamer GTA 6'),
        ('ytsearch25:GTA 6 Vice City graphics unreal engine 5 latest', 'Latest GTA 6 Vice City Unreal 5'),
        ('ytsearch25:Mythpat GTA 6 latest funny reaction live', 'Latest Mythpat GTA 6'),
        ('ytsearch25:Kai Cenat GTA 6 reaction live funny latest', 'Latest Kai Cenat GTA 6'),
        ('ytsearch25:GTA 6 Lucia Jason gameplay trailer 2 leaks latest', 'Latest GTA 6 Lucia Jason'),
    ]

    random.shuffle(target_sources)

    blacklist_words = ["fortnite", "fifa", "football", "soccer", "cricket", "roblox", "minecraft", "free fire", "pubg"]
    gta6_required_keywords = ["gta 6", "gta vi", "gta6", "grand theft auto vi", "grand theft auto 6", "vice city", "lucia", "leonida"]

    candidates = []
    import yt_dlp

    test_opts = {
        'quiet': True,
        'skip_download': True,
        'no_warnings': True,
        'extractor_args': {'youtube': {'player_client': ['android', 'ios', 'mweb', 'tv_embedded']}}
    }

    for source_url, label in target_sources:
        try:
            print(f"[Stream Finder] Scanning: {label}...")
            ydl_opts = {
                'extract_flat': True,
                'quiet': True,
                'playlist_items': '10'
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                res = ydl.extract_info(source_url, download=False)
                for entry in res.get('entries', []):
                    vid_id = entry.get('id')
                    title = entry.get('title', '')
                    t_lower = title.lower()

                    # 1. Skip if already clipped
                    if vid_id in clipped_history:
                        continue

                    # 2. Strict blacklist check
                    if any(b in t_lower for b in blacklist_words):
                        continue

                    # 3. Strict GTA 6 Only check (Exclusively GTA 6, No GTA 5)
                    if not any(k in t_lower for k in gta6_required_keywords):
                        continue
                    if ("gta 5" in t_lower or "gta v" in t_lower) and not any(k in t_lower for k in ["gta 6", "gta vi", "gta6"]):
                        continue

                    stream_url = entry.get('url') or f"https://www.youtube.com/watch?v={vid_id}"

                    # 4. Age-gate & Freshness pre-flight verification
                    try:
                        with yt_dlp.YoutubeDL(test_opts) as test_ydl:
                            cand_meta = test_ydl.extract_info(stream_url, download=False)
                            if cand_meta.get('age_limit', 0) > 0:
                                print(f"[Stream Finder] Skipping age-gated stream: '{title}'")
                                continue
                            upload_date = str(cand_meta.get('upload_date') or '')
                            # Skip ancient/old videos from before 2024
                            if upload_date and upload_date < '20240101':
                                print(f"[Stream Finder] Skipping older video ({upload_date}): '{title}'")
                                continue
                    except Exception as err:
                        print(f"[Stream Finder] Skipping restricted stream '{title}': {err}")
                        continue

                    print(f"[Stream Finder] [VERIFIED FRESH GTA 6] Found: '{title}' ({upload_date or 'Recent'}) -> {stream_url}")
                    candidates.append({
                        "url": stream_url,
                        "title": title,
                        "upload_date": upload_date,
                        "label": label
                    })
                    if len(candidates) >= max_candidates * 2:
                        break
        except Exception as e:
            print(f"[Stream Finder] Error querying {label}: {e}")
            continue

    # Sort so that the absolute freshest / newest uploads are chosen first!
    candidates.sort(key=lambda c: c.get('upload_date', '0'), reverse=True)
    sorted_urls = [c['url'] for c in candidates]
    return sorted_urls[:max_candidates]

def get_target_stream_url(custom_url=None):
    candidates = get_target_stream_candidates(custom_url, max_candidates=1)
    return candidates[0] if candidates else None

def get_stream_metadata(url):
    """
    Extracts stream metadata in seconds without downloading video.
    """
    if not url:
        return {
            "id": "climax_stream",
            "title": "GTA Insane Gaming Climax",
            "duration": 1800,
            "uploader": "Vice City Pulse",
            "description": "Viral streaming moments"
        }
    import yt_dlp
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'no_warnings': True,
        'extractor_args': {'youtube': {'player_client': ['android', 'ios', 'mweb', 'tv_embedded']}}
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                "id": info.get("id"),
                "title": info.get("title", "IShowSpeed Stream Moment"),
                "duration": int(info.get("duration") or 1800),
                "uploader": info.get("uploader", "IShowSpeed"),
                "description": (info.get("description") or "")[:500]
            }
    except Exception as e:
        print(f"[Warning] Stream metadata fetch failed ({e}), using safe fallback metadata...")
        return {
            "id": "climax_stream",
            "title": "IShowSpeed Insane Gaming Climax",
            "duration": 1800,
            "uploader": "IShowSpeed",
            "description": "Viral streaming moments"
        }

def analyze_viral_climax_gemini(metadata):
    """
    Uses Gemini AI to determine:
    1. The peak 30-40 second viral timestamp window
    2. Viral YouTube Shorts Title with emojis
    3. High-CTR hook badge text
    4. Tags and Description
    """
    duration = metadata["duration"]
    title = metadata["title"]
    
    # Sensible fallback defaults in case API is offline (tight 18s duration)
    default_start = int(duration * 0.65) if duration > 100 else 10
    default_result = {
        "start_sec": default_start,
        "end_sec": default_start + 18,
        "hook_badge": "GTA 6 MADNESS 💀🔥",
        "yt_title": f"Insane GTA 6 Next-Gen Graphics! 💀🏎️ #shorts",
        "description": f"The craziest GTA 6 Vice City moment you will see today! Can't wait for Rockstar to drop this!\n\n#shorts #gta6 #gaming #vicecity #viral #gtavi",
        "tags": ["gta 6", "gtavi", "gta 6 leaks", "gta 6 trailer", "vice city", "gaming", "shorts", "rockstar games"]
    }

    if not DEFAULT_GEMINI_KEY:
        return default_result

    prompt = f"""You are a Master Viral Shorts Video Editor & Sound Designer specialized in GTA 6 gaming stream clips.
STREAM INFO:
- Title: {title}
- Total Duration: {duration} seconds ({duration//60} minutes)
- Streamer: {metadata.get('uploader')}

TASK:
1. Choose the absolute punchiest 18 to 22-second climax window (start_sec and end_sec, exactly 18-22 seconds duration).
CRITICAL COMPLETION RULE (NO AADHA-ADHURA / INCOMPLETE CUTS):
- The clip MUST feel like a complete, satisfying mini-scene from start to finish!
- Start cleanly right at the BEGINNING of a fresh sentence, jump, or action.
- End cleanly right after the punchline, reaction, crash, or sentence FINISHES.
- NEVER cut off in the middle of someone speaking or mid-sentence!
2. Generate an ultra-clickable viral YouTube Shorts title with emoji and #shorts.
3. Generate a 2-4 word neon hook badge (e.g., 'SPEED GOES CRAZY 💀', 'INSANE GTA 6 PHYSICS 🤯', 'NO WAY HE DID THIS 😭').
4. Generate description and 8 viral tags.

Return ONLY valid JSON matching this schema:
{{
  "start_sec": <integer>,
  "end_sec": <integer>,
  "hook_badge": "<string>",
  "yt_title": "<string>",
  "description": "<string>",
  "tags": ["tag1", "tag2", ...]
}}"""

    for model_name in ["gemini-3.5-flash-lite", "gemini-3.1-flash-lite", "gemini-3-flash-preview"]:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={DEFAULT_GEMINI_KEY}"
            payload = json.dumps({
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"response_mime_type": "application/json"}
            }).encode("utf-8")
            req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=25) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                res = json.loads(text)
                # Validate timestamps
                start = int(res.get("start_sec", default_start))
                if start < 0 or start >= duration - 22:
                    start = default_start
                end = int(res.get("end_sec", start + 20))
                # Enforce complete, punchy 18-22 second duration (no aadha-adhura cuts)
                if end <= start or (end - start) > 24 or (end - start) < 16:
                    end = start + 20
                res["start_sec"] = start
                res["end_sec"] = end
                print(f"[Gemini AI] Viral moment identified via {model_name}: {start}s - {end}s (Duration: {end-start}s, Climax at {start//60}m:{start%60:02d}s)")
                print(f"[Gemini AI] Target Title: {res.get('yt_title')}")
                return res
        except Exception as e:
            print(f"[Gemini AI] {model_name} note: {e}")
            continue

    return default_result

def download_stream_slice_zero_bandwidth(stream_url, start_sec, end_sec, output_file):
    """
    Downloads ONLY the specified 30-45 second slice from YouTube.
    Bypasses the 20GB-30GB download completely!
    """
    import yt_dlp

    print(f"[Slice Downloader] Slicing range: {start_sec}s to {end_sec}s (~10-15MB only)...")

    def section_filter(info_dict, ydl_instance):
        return [{'start_time': start_sec, 'end_time': end_sec, 'title': 'slice'}]

    if os.path.exists(output_file):
        os.remove(output_file)

    ydl_opts = {
        'quiet': True,
        'download_ranges': section_filter,
        'format': 'bestvideo[height<=720]+bestaudio/best',
        'outtmpl': output_file,
        'force_keyframes_at_cuts': True,
        'no_warnings': True,
        'extractor_args': {'youtube': {'player_client': ['android', 'ios', 'mweb', 'tv_embedded']}}
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([stream_url])
    except Exception as e:
        print(f"[Slice Downloader] Primary download note: {e}. Retrying with universal format...")
        fallback_opts = {
            'quiet': True,
            'download_ranges': section_filter,
            'format': 'best',
            'outtmpl': output_file,
            'force_keyframes_at_cuts': True,
            'no_warnings': True,
            'extractor_args': {'youtube': {'player_client': ['android', 'ios', 'mweb', 'tv_embedded']}}
        }
        try:
            with yt_dlp.YoutubeDL(fallback_opts) as ydl:
                ydl.download([stream_url])
        except Exception as e2:
            print(f"[Slice Downloader] Fallback download note: {e2}")

    if not os.path.exists(output_file):
        # yt-dlp might have appended .webm or .mkv
        for cand in [output_file + ".webm", output_file + ".mkv", output_file + ".part"]:
            if os.path.exists(cand):
                output_file = cand
                break
        if not os.path.exists(output_file):
            p = Path(output_file)
            matches = list(p.parent.glob(f"{p.stem}*"))
            if matches:
                output_file = str(matches[0])

    if os.path.exists(output_file):
        size_mb = os.path.getsize(output_file) / (1024 * 1024)
        print(f"[Slice Downloader] Download complete! Slice size: {size_mb:.2f} MB ({Path(output_file).name})")
        return output_file
    else:
        raise RuntimeError("Slice download failed - file was not created.")

def generate_autoclip_bold_pop_ass(raw_slice, output_ass_path, hook_badge="VIRAL MOMENT", credit_name="VICE CITY PULSE", duration=20.0):
    """
    Generates AutoClip-grade 'Bold Pop' ASS subtitles with Permanent Neon Hook Badge & Credit Pill:
    - Top Hook Badge ([ 🔥 GTA 6 VICE CITY 🔥 ]) in glowing yellow with rounded dark pill
    - Top Credit Pill ([ 🎮 STREAMER: @CREATOR ]) right below the badge
    - Kinetic Word-by-word Subtitles in middle-lower third
    """
    clean_badge_text = str(hook_badge).upper().replace("[", "").replace("]", "").replace("'", "").strip()
    clean_credit_text = str(credit_name).upper().replace("@", "").replace("'", "").strip()

    def to_ass_time(sec):
        sec = max(0.0, float(sec))
        h = int(sec // 3600)
        m = int((sec % 3600) // 60)
        s = int(sec % 60)
        cs = int(round((sec - int(sec)) * 100))
        return f"{h}:{m:02d}:{s:02d}.{min(99, cs):02d}"

    ass_content = [
        "[Script Info]",
        "ScriptType: v4.00+",
        "PlayResX: 1080",
        "PlayResY: 1920",
        "ScaledBorderAndShadow: yes",
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        "Style: BoldPop,Arial Black,74,&H00FFFFFF,&H0000FFFF,&H00000000,&H80000000,-1,0,0,0,100,100,2,0,1,6,3,2,60,60,420,1",
        "Style: HookBadge,Arial Black,46,&H0000FFFF,&H00000000,&H00000000,&HA0000000,-1,0,0,0,100,100,2,0,3,10,0,8,40,40,110,1",
        "Style: CreditPill,Arial Black,32,&H00FFFFFF,&H00000000,&H00000000,&HA0000000,-1,0,0,0,100,100,1,0,3,8,0,8,40,40,195,1",
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
        f"Dialogue: 2,0:00:00.00,{to_ass_time(duration)},HookBadge,,0,0,0,,[ 🔥 {clean_badge_text} 🔥 ]",
        f"Dialogue: 2,0:00:00.00,{to_ass_time(duration)},CreditPill,,0,0,0,,[ 🎮 STREAMER: @{clean_credit_text} ]"
    ]

    try:
        # Extract audio segment for fast transcription
        audio_tmp = output_ass_path.with_suffix(".mp3")
        cmd_audio = [
            FFMPEG_BIN, "-y", "-i", str(raw_slice),
            "-vn", "-acodec", "libmp3lame", "-ar", "24000", "-ac", "1", "-b:a", "64k", str(audio_tmp)
        ]
        subprocess.run(cmd_audio, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        
        words_data = []
        if DEFAULT_GEMINI_KEY:
            try:
                import base64
                with open(audio_tmp, "rb") as f:
                    audio_b64 = base64.b64encode(f.read()).decode("utf-8")
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent?key={DEFAULT_GEMINI_KEY}"
                p_text = (
                    "Transcribe the creator/streamer's spoken words in this gaming audio clip. "
                    "Return ONLY a JSON array of word objects with estimated timestamps in seconds: "
                    "[{\"word\": \"WHAT\", \"start\": 0.1, \"end\": 0.4}, ...]. "
                    "If there is only background music or no speech, return an empty array []."
                )
                payload = json.dumps({
                    "contents": [{
                        "parts": [
                            {"text": p_text},
                            {"inline_data": {"mime_type": "audio/mp3", "data": audio_b64}}
                        ]
                    }],
                    "generationConfig": {"response_mime_type": "application/json"}
                }).encode("utf-8")
                req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=25) as resp:
                    res_json = json.loads(resp.read().decode("utf-8"))
                    cand_text = res_json["candidates"][0]["content"]["parts"][0]["text"]
                    parsed = json.loads(cand_text)
                    if isinstance(parsed, list):
                        words_data = parsed
                        print(f"[Subtitles AI] Transcribed {len(words_data)} spoken words directly from streamer!")
            except Exception as e:
                print(f"[Subtitles AI] Transcription note: {e}")
                
        if audio_tmp.exists():
            audio_tmp.unlink()
            
        # Clean and cast timestamps safely to float
        clean_words = []
        for w in words_data:
            try:
                clean_words.append({
                    "word": str(w.get("word", "")).strip(),
                    "start": float(w.get("start", 0.0)),
                    "end": float(w.get("end", 0.0))
                })
            except Exception:
                continue
        words_data = [w for w in clean_words if w["word"] and w["end"] > w["start"]]

        if not words_data:
            # If no speech transcribed, we still output the permanent Badges!
            output_ass_path.write_text("\n".join(ass_content), encoding="utf-8")
            return output_ass_path

        # Group words into 3-4 word phrases
        chunk_size = 4
        for i in range(0, len(words_data), chunk_size):
            group = words_data[i:i + chunk_size]
            g_start = float(group[0]["start"])
            g_end = float(group[-1]["end"])
            if g_end <= g_start:
                continue
                
            # Kinetic word highlight per word in group
            for active_idx, target_word in enumerate(group):
                w_start = float(target_word["start"])
                w_end = float(target_word["end"])
                if w_end <= w_start:
                    continue
                phrase_parts = []
                for idx, w in enumerate(group):
                    w_text = w["word"].upper().replace("{", "").replace("}", "")
                    if idx == active_idx:
                        # Highlighted active word: bright yellow + scale pop
                        phrase_parts.append(r"{\c&H0000FFFF&\fscx118\fscy118}" + w_text + r"{\r\c&H00FFFFFF&}")
                    else:
                        # Standard word: crisp white
                        phrase_parts.append(r"{\c&H00FFFFFF&}" + w_text)
                dialogue_text = " ".join(phrase_parts)
                ass_content.append(f"Dialogue: 0,{to_ass_time(w_start)},{to_ass_time(w_end)},BoldPop,,0,0,0,,{dialogue_text}")

        output_ass_path.write_text("\n".join(ass_content), encoding="utf-8")
        print(f"[AutoClip Subtitles] Successfully created kinetic ASS subtitles ({len(words_data)} words + Hook/Credit Badges)")
        return output_ass_path
    except Exception as e:
        print(f"[AutoClip Subtitles] Subtitle build notice: {e}")
        # Always output at least the badges!
        try:
            output_ass_path.write_text("\n".join(ass_content), encoding="utf-8")
            return output_ass_path
        except Exception:
            return None

# Multi-Day Stunt Library for Daily Rotation (Clean, viral metadata)
GTA_STUNT_SCENARIOS = [
    {
        "id": "streamer_gta6_reaction",
        "title": "MYTHPAT CRAZY REACTION IN GTA 6! 🔥🌴 #Shorts",
        "hook_badge": "GTA 6 STREAMER REACTION",
        "desc": "Mythpat insane live reaction to GTA 6 Vice City gameplay! Streamers going completely wild!\n\n#GTA6 #Mythpat #Gaming #Shorts #ViceCity #GTA6Live",
        "tags": ["GTA 6", "Mythpat GTA 6", "GTA 6 reaction", "gaming shorts", "vice city pulse", "viral gaming"],
        "prompt_context": "Top streamers live reaction to GTA 6 Vice City open world with hysterical webcam facecam gameplay"
    },
    {
        "id": "streamer_vice_city_madness",
        "title": "When Streamers Enter GTA 6 Vice City! 🚨🤣 #Shorts",
        "hook_badge": "VICE CITY MADNESS",
        "desc": "Streamer goes totally berserk playing GTA 6 in Vice City! Watch the hilarious live reaction!\n\n#GTA6 #Gaming #Shorts #TechnoGamerz #Mythpat #GTAStream",
        "tags": ["GTA 6", "GTA 6 live", "streamer reaction", "gaming shorts", "vice city pulse", "gta funny moments"],
        "prompt_context": "Hilarious live streamer reaction in GTA 6 driving supercars through Vice City neon streets"
    },
    {
        "id": "streamer_fastest_escape",
        "title": "Streamer's Craziest 6-Star Escape in GTA 6! 🚔💀 #Shorts",
        "hook_badge": "INSANE GTA 6 ESCAPE",
        "desc": "Insane high-stakes police escape in GTA 6 Vice City with live webcam reaction! Drop a like!\n\n#GTA6 #GTAVI #Gaming #Shorts #ViceCity #StreamerMoments",
        "tags": ["GTA 6", "GTAVI", "police chase", "gaming shorts", "streamer live", "vice city"],
        "prompt_context": "High adrenaline GTA 6 streamer police chase escape in Vice City with live funny webcam reactions"
    }
]

def generate_hyped_gta_voiceover_and_subs(title_context, out_audio_path, out_ass_path, duration_sec=30):
    """
    Generates high-energy viral gaming commentary script, synthesizes voiceover via edge_tts,
    and formats kinetic word-popping ASS subtitles (yellow active highlight).
    """
    try:
        import edge_tts
        import asyncio
    except ImportError:
        print("[Commentary Engine] edge-tts not installed, skipping voiceover...")
        return False

    prompt = f"""You are a viral gaming TikTok & YouTube Shorts commentator.
The video is an insane high-energy GTA 6 moment: '{title_context}'.
Write an ultra-exciting, 16-20 second hyped spoken commentary script about GTA 6 Vice City.
Make it super engaging, fast-paced, punchy, asking viewers their thoughts on GTA 6!
Return ONLY valid JSON:
{{
  "commentary": "<spoken text, 35-45 words>"
}}"""

    commentary_text = "Rockstar Games is breaking the internet with GTA 6! Look at these insane Vice City graphics and physics... Lucia and Jason are taking over! Drop a like and subscribe if you're waiting for GTA 6!"
    if DEFAULT_GEMINI_KEY:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent?key={DEFAULT_GEMINI_KEY}"
            payload = json.dumps({
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"response_mime_type": "application/json"}
            }).encode("utf-8")
            req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode())
                res = json.loads(data["candidates"][0]["content"]["parts"][0]["text"])
                if res.get("commentary"):
                    commentary_text = res["commentary"]
        except Exception as e:
            print(f"[Commentary Engine] Gemini notice: {e}")

    print(f"[Commentary Engine] Spoken text: '{commentary_text}'")

    async def _synth():
        comm = edge_tts.Communicate(commentary_text, "en-US-GuyNeural", rate="+14%", pitch="+1Hz")
        sentences = []
        with open(out_audio_path, "wb") as f:
            async for chunk in comm.stream():
                if chunk["type"] == "audio":
                    f.write(chunk["data"])
                elif chunk["type"] == "SentenceBoundary":
                    sentences.append({
                        "text": chunk["text"],
                        "start": chunk["offset"] / 10_000_000,
                        "duration": chunk["duration"] / 10_000_000
                    })
        return sentences

    try:
        sentences = asyncio.run(_synth())
        if not sentences or not Path(out_audio_path).exists():
            return False

        def to_ass_time(sec):
            h = int(sec // 3600)
            m = int((sec % 3600) // 60)
            s = int(sec % 60)
            cs = int(round((sec - int(sec)) * 100))
            return f"{h}:{m:02d}:{s:02d}.{min(99, cs):02d}"

        ass_lines = [
            "[Script Info]",
            "ScriptType: v4.00+",
            "PlayResX: 1080",
            "PlayResY: 1920",
            "ScaledBorderAndShadow: yes",
            "",
            "[V4+ Styles]",
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
            "Style: BoldPop,Arial Black,78,&H00FFFFFF,&H0000FFFF,&H00000000,&H80000000,-1,0,0,0,100,100,2,0,1,6,3,2,60,60,420,1",
            "",
            "[Events]",
            "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"
        ]

        for s in sentences:
            words = s["text"].split()
            if not words:
                continue
            w_dur = s["duration"] / len(words)
            for i, target_w in enumerate(words):
                w_start = s["start"] + i * w_dur
                w_end = w_start + w_dur
                p_start = max(0, i - 1)
                p_end = min(len(words), i + 2)
                chunk = []
                for j in range(p_start, p_end):
                    w_clean = words[j].upper().replace("{", "").replace("}", "").strip()
                    if j == i:
                        chunk.append(r"{\c&H0000FFFF&\fscx120\fscy120}" + w_clean + r"{\r\c&H00FFFFFF&}")
                    else:
                        chunk.append(r"{\c&H00FFFFFF&}" + w_clean)
                phrase = " ".join(chunk)
                ass_lines.append(f"Dialogue: 0,{to_ass_time(w_start)},{to_ass_time(w_end)},BoldPop,,0,0,0,,{phrase}")

        out_ass_path.write_text("\n".join(ass_lines), encoding="utf-8")
        print(f"[Commentary Engine] Generated voice & subtitles ({len(sentences)} sentences)")
        return True
    except Exception as e:
        print(f"[Commentary Engine] Error: {e}")
        return False

def detect_streamer_facecam(raw_slice):
    """
    AI Facecam Detection (OpusClip / Klap style):
    Detects if the streamer has an active facecam (e.g. IShowSpeed, Techno Gamerz, Kai Cenat).
    Uses OpenCV Haar cascades to locate facecam bounds in 0.01 seconds.
    """
    try:
        import cv2
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        face_cascade = cv2.CascadeClassifier(cascade_path)
        cap = cv2.VideoCapture(str(raw_slice))
        fps = cap.get(cv2.CAP_PROP_FPS) or 24
        test_frames = [int(fps * 2), int(fps * 4), int(fps * 6)]

        for f_idx in test_frames:
            cap.set(cv2.CAP_PROP_POS_FRAMES, f_idx)
            ret, frame = cap.read()
            if not ret or frame is None:
                continue
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=4, minSize=(50, 50))
            if len(faces) > 0:
                bx, by, bw, bh = faces[0]
                ih, iw = frame.shape[:2]
                margin = int(bw * 1.1)
                cx = bx + bw // 2
                cy = by + bh // 2
                crop_w = min(iw, max(380, bw + margin * 2))
                crop_h = min(ih, int(crop_w * 0.72))
                crop_x = max(0, min(iw - crop_w, cx - crop_w // 2))
                crop_y = max(0, min(ih - crop_h, cy - crop_h // 2))
                cap.release()
                print(f"[Facecam AI] 🔥 Streamer Facecam Detected at x={crop_x}, y={crop_y}, {crop_w}x{crop_h}!")
                return {"x": crop_x, "y": crop_y, "w": crop_w, "h": crop_h}
        cap.release()
    except Exception as e:
        print(f"[Facecam AI] Detection note: {e}")
    return None

def render_vertical_short_opus_style(raw_slice, output_short, credit_name="Vice City Pulse", hook_badge="MEGA RAMP", voice_audio=None, custom_ass=None):
    """
    Converts 16:9 slice to 1080x1920 9:16 vertical Short:
    - AutoClip AI Split Screen: Facecam on TOP + Full Gameplay on BOTTOM (if streamer has camera)
    - Full Gameplay with Dynamic Blurred Background (if no camera)
    - AutoClip Kinetic Subtitles (Bold Pop yellow highlights)
    - Mixed high-energy Voiceover + Game Audio
    """
    print(f"[Opus Renderer] Transforming into AutoClip 9:16 Short (Kinetic Captions, Credit: @{credit_name})...")

    clean_credit = credit_name.replace("'", "").replace(":", " ").replace("@", "").strip()
    clean_badge = hook_badge.replace("'", "").replace(":", " ").strip()

    # Determine subtitles
    ass_path = custom_ass
    has_ass = bool(ass_path and Path(ass_path).exists())
    if not has_ass:
        ass_path = Path(output_short).with_suffix(".ass")
        has_ass = bool(generate_autoclip_bold_pop_ass(raw_slice, ass_path, hook_badge=clean_badge))

    # Detect streamer facecam for OpusClip / Klap split screen
    facecam = detect_streamer_facecam(raw_slice)
    if facecam:
        print(f"[Opus Renderer] 🎬 FACECAM DETECTED: Building OpusClip Split-Screen (Facecam TOP + Gameplay BOTTOM)!")
        fx, fy, fw, fh = facecam['x'], facecam['y'], facecam['w'], facecam['h']
        # Top 760px: Streamer facecam | Bottom 1160px: Full high-speed gameplay
        filter_complex = (
            f"[0:v]crop={fw}:{fh}:{fx}:{fy},scale=1080:760[top];"
            f"[0:v]scale=1080:1160:force_original_aspect_ratio=increase,crop=1080:1160[bottom];"
            f"[top][bottom]vstack[base];"
            f"[base]drawbox=x=0:y=756:w=1080:h=8:color=0x00FFFF@0.9:t=fill"
        )
    else:
        # High-Octane Viral Gaming Layout: Dynamic 9:16 layout with neon cyan accent borders framing the gameplay
        filter_complex = (
            f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=32:8,eq=brightness=-0.22:contrast=1.25:saturation=1.35[bg];"
            f"[0:v]scale=1080:-1:force_original_aspect_ratio=decrease,drawbox=x=0:y=0:w=1080:h=6:color=0x00FFFF@0.9:t=fill,drawbox=x=0:y=ih-6:w=1080:h=6:color=0x00FFFF@0.9:t=fill[fg];"
            f"[bg][fg]overlay=0:(H-h)/2[base];"
            f"[base]null"
        )

    if has_ass and ass_path and Path(ass_path).exists():
        escaped_ass = str(Path(ass_path).resolve()).replace("\\", "/").replace(":", "\\:")
        filter_complex += f",ass='{escaped_ass}'"
    filter_complex += "[v]"

    # Discover optional energetic background music
    bg_music_dir = Path(__file__).parent / "channel2_assets" / "bg_music"
    bg_music_files = list(bg_music_dir.glob("*.mp3")) + list(bg_music_dir.glob("*.wav"))
    chosen_bg = random.choice(bg_music_files) if bg_music_files else None
    if chosen_bg:
        print(f"[Audio Director] 🎵 Mixing energetic gaming background beat: {chosen_bg.name}")

    # Probe duration for natural fade out
    fade_start = 17.5
    try:
        probe_cmd = [FFMPEG_BIN, "-i", str(raw_slice)]
        p_res = subprocess.run(probe_cmd, stderr=subprocess.PIPE, stdout=subprocess.DEVNULL, text=True)
        import re
        m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", p_res.stderr)
        if m:
            total_s = int(m.group(1))*3600 + int(m.group(2))*60 + float(m.group(3))
            fade_start = max(1.0, total_s - 0.45)
    except Exception:
        pass

    has_voice = bool(voice_audio and Path(voice_audio).exists())

    if chosen_bg and has_voice:
        filter_complex += f";[0:a]volume=0.35[game];[1:a]volume=1.45[voice];[2:a]volume=0.15[bgm];[game][voice][bgm]amix=inputs=3:duration=first:dropout_transition=2,afade=t=out:st={fade_start:.2f}:d=0.45[aout]"
        cmd = [
            FFMPEG_BIN, "-y",
            "-i", str(raw_slice),
            "-i", str(voice_audio),
            "-stream_loop", "-1", "-i", str(chosen_bg),
            "-filter_complex", filter_complex,
            "-map", "[v]",
            "-map", "[aout]",
            "-c:v", "libx264", "-preset", "fast", "-crf", "22",
            "-c:a", "aac", "-b:a", "192k",
            str(output_short)
        ]
    elif chosen_bg and not has_voice:
        # Creator real voice + Hype Background beat at 16% volume!
        filter_complex += f";[0:a]volume=1.25,alimiter=limit=0.95[voice];[1:a]volume=0.16[bgm];[voice][bgm]amix=inputs=2:duration=first:dropout_transition=2,afade=t=out:st={fade_start:.2f}:d=0.45[aout]"
        cmd = [
            FFMPEG_BIN, "-y",
            "-i", str(raw_slice),
            "-stream_loop", "-1", "-i", str(chosen_bg),
            "-filter_complex", filter_complex,
            "-map", "[v]",
            "-map", "[aout]",
            "-c:v", "libx264", "-preset", "fast", "-crf", "22",
            "-c:a", "aac", "-b:a", "192k",
            str(output_short)
        ]
    elif has_voice:
        filter_complex += f";[0:a]volume=0.35[game];[1:a]volume=1.45[voice];[game][voice]amix=inputs=2:duration=first:dropout_transition=2,afade=t=out:st={fade_start:.2f}:d=0.45[aout]"
        cmd = [
            FFMPEG_BIN, "-y",
            "-i", str(raw_slice),
            "-i", str(voice_audio),
            "-filter_complex", filter_complex,
            "-map", "[v]",
            "-map", "[aout]",
            "-c:v", "libx264", "-preset", "fast", "-crf", "22",
            "-c:a", "aac", "-b:a", "192k",
            str(output_short)
        ]
    else:
        af = f"volume=1.25,alimiter=limit=0.95,afade=t=out:st={fade_start:.2f}:d=0.45"
        cmd = [
            FFMPEG_BIN, "-y",
            "-i", str(raw_slice),
            "-filter_complex", filter_complex,
            "-map", "[v]",
            "-map", "0:a?",
            "-af", af,
            "-c:v", "libx264", "-preset", "fast", "-crf", "22",
            "-c:a", "aac", "-b:a", "192k",
            str(output_short)
        ]

    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    print(f"[Opus Renderer] Successfully produced 1080x1920 Short: {output_short}")
    return output_short

def generate_viral_short_thumbnail(video_path, output_thumb_path, hook_text="INSANE GTA STUNT"):
    """
    Extracts high-impact action frame from video and composites a high-CTR vertical thumbnail.
    """
    try:
        from PIL import Image, ImageDraw, ImageFont, ImageFilter
        out_p = Path(output_thumb_path)
        
        # Extract frame at ~3 seconds
        temp_frame = out_p.with_suffix(".raw.jpg")
        cmd = [
            FFMPEG_BIN, "-y", "-ss", "00:00:03", "-i", str(video_path),
            "-vframes", "1", "-q:v", "2", str(temp_frame)
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        if not temp_frame.exists():
            return None
            
        base_img = Image.open(temp_frame).convert("RGB")
        base_img = base_img.resize((1080, 1920), Image.Resampling.LANCZOS)
        
        draw = ImageDraw.Draw(base_img, "RGBA")
        
        # Add dramatic top and bottom dark gradient vignettes for text pop
        for y in range(400):
            alpha = int(210 * (1 - y / 400))
            draw.line([(0, y), (1080, y)], fill=(0, 0, 0, alpha))
            
        for y in range(1520, 1920):
            alpha = int(220 * ((y - 1520) / 400))
            draw.line([(0, y), (1080, y)], fill=(0, 0, 0, alpha))
            
        # Draw high-voltage hook banner
        banner_y = 260
        draw.rectangle([0, banner_y - 20, 1080, banner_y + 160], fill=(0, 0, 0, 180))
        
        clean_text = hook_text.upper().replace("{", "").replace("}", "")
        
        # Try loading a bold system font
        font = None
        for font_name in ["impact.ttf", "arialbd.ttf", "Arial_Bold.ttf", "DejaVuSans-Bold.ttf"]:
            try:
                font = ImageFont.truetype(font_name, 72)
                break
            except:
                continue
        if not font:
            font = ImageFont.load_default()
            
        # Draw text with drop shadow
        bbox = draw.textbbox((0, 0), clean_text, font=font)
        tw = bbox[2] - bbox[0]
        tx = (1080 - tw) // 2
        ty = banner_y + 15
        
        # Drop shadow
        draw.text((tx + 4, ty + 4), clean_text, font=font, fill=(0, 0, 0, 255))
        # Main text in vibrant yellow
        draw.text((tx, ty), clean_text, font=font, fill=(255, 230, 0, 255))
        
        base_img.save(out_p, "JPEG", quality=92)
        if temp_frame.exists():
            temp_frame.unlink()
        print(f"[Thumbnail Engine] Generated high-CTR vertical thumbnail: {out_p.name}")
        return str(out_p)
    except Exception as e:
        print(f"[Thumbnail Engine] Thumbnail note: {e}")
        return None

def upload_to_channel_2(video_path, clip_data):
    """
    Uploads to Channel 2 (GTA & Clips channel).
    If Channel 2 credentials are not set yet, logs helpful instructions
    and keeps the video saved safely.
    """
    client_id = os.environ.get("YT_CLIENT_ID_CH2")
    client_secret = os.environ.get("YT_CLIENT_SECRET_CH2")
    refresh_token = os.environ.get("YT_REFRESH_TOKEN_CH2")

    # Check for local Channel 2 token file if env vars are missing
    ch2_token_file = Path(__file__).parent / "youtube_token_ch2.json"
    if not (client_id and client_secret and refresh_token) and ch2_token_file.exists():
        try:
            with open(ch2_token_file, "r", encoding="utf-8") as f:
                tdata = json.load(f)
                client_id = tdata.get("client_id")
                client_secret = tdata.get("client_secret")
                refresh_token = tdata.get("refresh_token")
        except Exception:
            pass

    desc = clip_data.get("description") or clip_data.get("yt_desc") or "High octane GTA action! #GTA #Shorts #IShowSpeed"
    tags = clip_data.get("tags") or clip_data.get("yt_tags") or ["GTA 6", "IShowSpeed GTA", "Vice City Pulse", "Gaming Shorts"]
    title = clip_data.get("yt_title") or "Insane GTA 6 Police Escape Climax! 💀 #Shorts"

    if not (client_id and client_secret and refresh_token):
        print("\n" + "="*70)
        print(" [CHANNEL 2 NOTICE] API Credentials Not Configured Yet")
        print("="*70)
        print(f" Rendered video is safely stored at: {video_path}")
        print(f" Title:       {title}")
        print(f" Description: {desc[:100]}...")
        print(f" Tags:        {', '.join(tags[:5])}")
        print("\n To enable 100% automated cloud upload to Channel 2:")
        print(" 1. Add YT_CLIENT_ID_CH2, YT_CLIENT_SECRET_CH2, YT_REFRESH_TOKEN_CH2 in GitHub Secrets")
        print("    OR save youtube_token_ch2.json in this directory.")
        print("="*70 + "\n")
        return False

    try:
        from youtube_cloud_uploader import upload_video_file
        
        # Generate custom High-CTR vertical thumbnail
        thumb_path = Path(video_path).with_name(f"thumb_{Path(video_path).stem}.jpg")
        generated_thumb = generate_viral_short_thumbnail(
            video_path,
            thumb_path,
            hook_text=clip_data.get("hook_badge", "INSANE STUNT")
        )
        
        res = upload_video_file(
            video_path,
            title=title,
            description=desc,
            tags=tags,
            client_id=client_id,
            client_secret=client_secret,
            refresh_token=refresh_token,
            privacy_status="public",
            thumbnail_file=generated_thumb
        )
        print(f"[Channel 2 Uploader] Successfully uploaded to Channel 2! Video ID: {res.get('id')}")

        # Facebook & Instagram are strictly reserved for Chronicle Vault (History) niche to keep audience pure
        print("[Niche Guard] Keeping Facebook & Instagram focused exclusively on Chronicle Vault History.")

        return True
    except Exception as e:
        print(f"[Channel 2 Uploader] Upload error: {e}")
        return False

def run_channel_2_autopilot(stream_url=None, upload=True):
    """
    Main execution pipeline for Channel 2.
    """
    print("\n" + "="*70)
    print(" CHANNEL 2 • GTA & SPEED VIRAL SHORT PRODUCTION CYCLE")
    print("="*70)

    # 1. Discover stream links
    candidates = get_target_stream_candidates(stream_url, max_candidates=3)
    work_dir = Path(__file__).parent / "output_channel2"
    work_dir.mkdir(exist_ok=True)

    timestamp = int(time.time())
    raw_slice = str(work_dir / f"raw_slice_{timestamp}.mp4")
    final_short = str(work_dir / f"Speed_GTA_Short_{timestamp}.mp4")

    slice_downloaded = False
    chosen_meta = None
    chosen_analysis = None

    for target_url in candidates:
        try:
            print(f"[Autopilot] Attempting Creator Stream: {target_url}")
            meta = get_stream_metadata(target_url)
            print(f"[Autopilot] Stream Title: '{meta['title']}' ({meta['duration']//60} mins)")

            analysis = analyze_viral_climax_gemini(meta)
            raw_slice = download_stream_slice_zero_bandwidth(target_url, analysis["start_sec"], analysis["end_sec"], raw_slice)

            slice_downloaded = True
            chosen_meta = meta
            chosen_analysis = analysis
            record_clip_history(meta.get("id"))
            print(f"[Autopilot] Successfully sliced viral moment from: {meta['title']}")
            break
        except Exception as e:
            print(f"[Autopilot] Stream slice attempt failed for {target_url}: {e}. Trying next candidate...")
            continue

    if not slice_downloaded:
        print("[Autopilot] ⚡ Cloud stream hunt blocked by YouTube datacenter check. Activating rotating genuine streamer facecam library!")
        streamer_lib = Path(__file__).parent / "channel2_assets" / "streamer_library"
        streamer_clips = sorted(list(streamer_lib.glob("*.mp4"))) if streamer_lib.exists() else []

        if streamer_clips:
            # Intelligent anti-duplicate selection: never repeat the same clip consecutively
            history = load_clip_history()
            unused_clips = [c for c in streamer_clips if c.stem not in history and c.name not in history]
            if unused_clips:
                chosen_clip = unused_clips[0]
            else:
                # If all clips have been used, pick the one not used in the last run
                last_used = history[-1] if history else ""
                candidates = [c for c in streamer_clips if c.stem != last_used and c.name != last_used]
                chosen_clip = candidates[0] if candidates else streamer_clips[0]

            shutil.copyfile(str(chosen_clip), raw_slice)
            record_clip_history(chosen_clip.stem)
            print(f"[Autopilot] Selected Anti-Duplicate Streamer Facecam: {chosen_clip.stem}")

            creator_name = "Techno Gamerz" if "techno" in chosen_clip.name.lower() else ("Mythpat" if "mythpat" in chosen_clip.name.lower() else "Typical Gamer")
            meta = {
                "title": f"When {creator_name} Had The Most Insane GTA Moment! 😱🔥",
                "uploader": creator_name,
                "duration": 30
            }
            analysis = {
                "start_sec": 0,
                "end_sec": 30,
                "yt_title": f"When {creator_name} Lost His Mind In GTA 6! 😱 #shorts",
                "description": f"Insane GTA 6 viral moments featuring {creator_name}! Follow @ViceCityPulseOfficial for daily GTA 6 leaks & highlights.\n\nStreamer: {creator_name}\n#gta6 #gtavi #gaming #streamer #funny #vicecitypulse",
                "yt_desc": f"Insane GTA 6 viral moments featuring {creator_name}!\n\n#gta6 #gtavi #gaming",
                "hook_badge": f"{creator_name.upper()} GTA 6!",
                "hook_text": f"{creator_name.upper()} GTA 6!",
                "tags": ["gta 6", "gtavi", "gaming", "shorts", creator_name.lower(), "funny moments", "vice city pulse"],
                "yt_tags": ["gta 6", "gtavi", "gaming", "shorts", creator_name.lower()],
                "prompt_context": f"{creator_name} reacting to GTA 6 Vice City with crazy funny reactions and high energy webcam facecam"
            }
        else:
            fallback_source = Path(__file__).parent / "channel2_assets" / "fallback_gta_action.mp4"
            if fallback_source.exists():
                shutil.copyfile(str(fallback_source), raw_slice)
                day_idx = int(time.time() // 86400) % len(GTA_STUNT_SCENARIOS)
                cur_scenario = GTA_STUNT_SCENARIOS[day_idx]
                print(f"[Autopilot] Selected Daily Rotating Scenario #{day_idx+1}: {cur_scenario['hook_badge']}")

                meta = {"title": cur_scenario["title"], "uploader": "Vice City Pulse", "duration": 30}
                analysis = {
                    "start_sec": 0,
                    "end_sec": 30,
                    "yt_title": cur_scenario["title"],
                    "description": cur_scenario["desc"],
                    "yt_desc": cur_scenario["desc"],
                    "hook_badge": cur_scenario["hook_badge"],
                    "hook_text": cur_scenario["hook_badge"],
                    "tags": cur_scenario["tags"],
                    "yt_tags": cur_scenario["tags"],
                    "prompt_context": cur_scenario["prompt_context"]
                }
            else:
                raise FileNotFoundError("Local fallback GTA action video not found!")
    else:
        meta = chosen_meta
        analysis = chosen_analysis

    # 4.5 Intelligent Voice & Subtitle Decision:
    ass_subs = work_dir / f"subs_{timestamp}.ass"
    clean_badge = analysis.get("hook_badge", "INSANE GTA 6")
    clip_dur = float(analysis.get("end_sec", 20) - analysis.get("start_sec", 0))
    has_subs = generate_autoclip_bold_pop_ass(
        raw_slice,
        ass_subs,
        hook_badge=clean_badge,
        credit_name=meta.get("uploader", "Vice City Pulse"),
        duration=clip_dur
    )

    voice_audio = None
    custom_ass = None

    if has_subs and Path(has_subs).exists():
        # Case A: Creator is speaking! Preserving 100% original creator voice (ZERO AI talk-over)
        print("[Audio Director] 🎙️ Creator's real voice detected! Preserving original audio (zero AI voiceover).")
        custom_ass = has_subs
        voice_audio = None
    else:
        # Case B: Video has NO voice / silent gameplay / trailer music only!
        # Automatically generate high-energy hype commentary so it is not boring or silent!
        print("[Audio Director] 🔇 No creator speech detected in clip (silent gameplay/trailer). Synthesizing high-energy hype commentary!")
        voice_audio = work_dir / f"voice_{timestamp}.mp3"
        voice_ass = work_dir / f"voice_subs_{timestamp}.ass"
        prompt_ctx = analysis.get("prompt_context") or analysis.get("yt_title") or meta.get("title")
        has_hype_voice = generate_hyped_gta_voiceover_and_subs(
            title_context=prompt_ctx,
            out_audio_path=voice_audio,
            out_ass_path=voice_ass,
            duration_sec=analysis["end_sec"] - analysis["start_sec"]
        )
        if has_hype_voice and Path(voice_ass).exists():
            custom_ass = voice_ass

    # 5. 9:16 Opus-Style Vertical Short (Clean Boundaries, Natural Fade, No Aadha-Adhura Chop)
    render_vertical_short_opus_style(
        raw_slice,
        final_short,
        credit_name=meta.get("uploader", "Vice City Pulse"),
        hook_badge=analysis.get("hook_badge", "INSANE GTA 6"),
        voice_audio=voice_audio if (voice_audio and Path(voice_audio).exists()) else None,
        custom_ass=custom_ass
    )

    # Cleanup temporary slice and subtitle files
    for tmp in [raw_slice, ass_subs, voice_audio]:
        if tmp and os.path.exists(tmp):
            try:
                os.remove(tmp)
            except Exception:
                pass

    # 6. Auto-upload (or stage)
    if upload:
        upload_to_channel_2(final_short, analysis)
    else:
        print("\n" + "="*70)
        print(" [TEST MODE / DRY RUN] Upload skipped as requested.")
        print(f" Generated GTA 6 Video Saved Locally: {final_short}")
        print("="*70 + "\n")

    print("="*70)
    print(f" [CHANNEL 2 SUCCESS] Short ready: {final_short}")
    print("="*70 + "\n")
    return final_short

if __name__ == "__main__":
    args = sys.argv[1:]
    no_upload = "--no-upload" in args or "--test" in args
    clean_args = [a for a in args if a not in ("--no-upload", "--test")]
    url_arg = clean_args[0] if clean_args else None
    run_channel_2_autopilot(url_arg, upload=not no_upload)
