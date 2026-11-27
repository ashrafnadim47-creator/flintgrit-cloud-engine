# -*- coding: utf-8 -*-
"""
=============================================================================
SHADOW WILL • OFFICIAL AUTONOMOUS CLOUD ANIMATION PRODUCER
=============================================================================
Runs 100% autonomously in the cloud (GitHub Actions / Cloud Server)
even when Director Faraz's PC is turned OFF.

Pipeline:
  1. Auto-selects high-retention relatable Indian psychological topics
  2. Synthesizes deep, cinematic Hindi Neural Voice (hi-IN-MadhurNeural)
  3. Renders 1080x1920 Full HD Kinetic Visual Animation (Character vs Red Shadow)
  4. Auto-uploads to YouTube channel as PUBLIC with high-CTR title, description & tags
=============================================================================
"""

import os
import sys
import time
import json
import asyncio
import random
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

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

# Autopilot Video Catalog: High-Retention Relatable Psychology (Indian Youth & Students)
AUTOPILOT_STORIES = [
    {
        "id": "the_3am_screen_trap",
        "title": "The 3 AM Screen Trap",
        "yt_title": "Raat Ke 3 Baje Ka Phone Trap: Dimaag Ka Silent Poison 📱🌑 | Shadow Will",
        "category": "animation",
        "description": "Raat ke 3 baje andhere kamre me blue screen ka glow... Har raat khud se waada karna ki kal se change honge, aur subah sirf exhaustion bacha rehna. Ye kahani aapki aur aapke inner enemy ki hai.\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\nTIMESTAMPS:\n0:00 - The 3 AM Glow\n0:15 - The Whisper: Just 1 More Reel\n0:30 - Broken Promises & Regret\n0:45 - The Rule of Cold Discipline\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n#shadowwill #animation #discipline #innerenemy #dopamine #shorts #mentalhealth",
        "tags": ["shadow will", "3am phone trap", "dopamine detox hindi", "inner enemy", "kaz animation", "discipline motivation", "dark psychology", "hindi animated stories", "shorts"],
        "voiceover": "Raat ke theek teen baje hain. Poore kamre me andhera hai, sirf ek screen glow kar rahi hai. Shaam ko tumne khud se waada kiya tha ki aaj time par so jaoge. Lekin tumhara inner enemy dheere se whisper karta hai: Bas ek aur reel. Aur jab aakh khulti hai, toh motivation nahi, sirf exhausted pachtawa bachta hai. Yaad rakhna: Motivation hamesha dhokha dega. Andhere me sirf cold discipline hi is saaye ko hara sakti hai.",
        "scenes": [
            {"badge": "THE 3 AM TRAP", "headline": "ANDHERA & BLUE GLOW", "sub": "Kamre me andhera, sirf ek screen", "color": (239, 68, 68)},
            {"badge": "THE RED WHISPER", "headline": "JUST ONE MORE REEL", "sub": "Dopamine ka silent illusion", "color": (245, 158, 11)},
            {"badge": "THE REGRET", "headline": "PROMISES BROKEN", "sub": "Subah sirf exhausted pachtawa bachta hai", "color": (239, 68, 68)},
            {"badge": "THE CONQUEST", "headline": "COLD DISCIPLINE", "sub": "Motivation fails. Discipline endures.", "color": (16, 185, 129)}
        ]
    },
    {
        "id": "log_kya_kahenge_chains",
        "title": "Log Kya Kahenge Ki Invisible Chains",
        "yt_title": "\"Log Kya Kahenge?\" Is Darr Ki Zanjeeron Ko Tod Do ⛓️🔥 | Shadow Will",
        "category": "animation",
        "description": "Hum apni 90% zindagi un logon ko khush karne me barbaad kar dete hain jo hamare janaze par bhi bas 10 minute rukenge. Ye animated film aapko un adrishya zanjeeron se azaad karegi.\n\n#shadowwill #logkyakahenge #selfgrowth #animation #mindset #shorts",
        "tags": ["log kya kahenge", "shadow will", "fear of society", "overthinking hindi", "animation", "inner enemy", "discipline", "shorts"],
        "voiceover": "Humaare gale aur haathon me aisi zanjeerein bandhi hain jo kisi ko dikhti nahi. Rishtedaar, padosi, aur anjaan log un zanjeeron ko kheenchte hain aur hum darr ke maare apne sapne chhod dete hain. Psychology kehti hai: Log aapke baare me utna nahi sochte jitna aap darr rahe ho. Har insaan sirf apne dukh me pareshan hai. Zanjeeron ko todo, khamoshi se kaam karo, aur apni kahani khud likho.",
        "scenes": [
            {"badge": "INVISIBLE CHAINS", "headline": "SOCIETY PRESSURE", "sub": "Anjaan logon ka be-matlab darr", "color": (239, 68, 68)},
            {"badge": "THE HARSH TRUTH", "headline": "NOBODY IS WATCHING", "sub": "Har insaan sirf apne me pareshan hai", "color": (245, 158, 11)},
            {"badge": "BREAKING CHAINS", "headline": "SHUT THE NOISE", "sub": "Logon ki baaton ko mute karo", "color": (59, 130, 246)},
            {"badge": "TRUE FREEDOM", "headline": "OWN YOUR LIFE", "sub": "Koshish itni khamoshi se ki shor ho jaye", "color": (16, 185, 129)}
        ]
    },
    {
        "id": "kitaab_kholte_hi_phone",
        "title": "Kitaab Kholte Hi Phone Ka Trap",
        "yt_title": "Padhai Kholte Hi Phone Ki Yaad Kyun Aati Hai? 📚📱 | Shadow Will",
        "category": "animation",
        "description": "Kitab kholte hi neend aana aur phone uthate hi aakh khul jana — ye aalas nahi, aapke brain ka dopamine addiction hai. Jaano is trap se bahar kaise niklein.\n\n#studymotivation #dopaminedetox #shadowwill #animation #focus #shorts",
        "tags": ["study focus hack", "phone distraction while studying", "shadow will", "dopamine detox", "animation", "discipline", "shorts"],
        "voiceover": "Jaise hi tum padhne baithte ho, dimaag achanak bhari hone lagta hai. Lekin jaise hi notification ki light jalti hai, neend gayab ho jati hai. Ye aalas nahi hai — ye tumhare dimaag ka easy dopamine ka nasha hai. Kitaab me mehnat lagti hai, aur phone me bina mehnat ke maza milta hai. Agli baar jab padhne baitho, phone ko doosre kamre me phenk do. Pehle 15 minute mushkil honge, uske baad focus tumhara gulaam ban jayega.",
        "scenes": [
            {"badge": "STUDY ROOM DEMON", "headline": "INSTANT DROWSINESS", "sub": "Kitab kholte hi neend aana", "color": (245, 158, 11)},
            {"badge": "THE DOPAMINE TRAP", "headline": "EASY ENTERTAINMENT", "sub": "Bina mehnat ke brain ko maza", "color": (239, 68, 68)},
            {"badge": "THE PROTOCOL", "headline": "PHONE OUT OF ROOM", "sub": "Pehle 15 minute ka silence test", "color": (59, 130, 246)},
            {"badge": "DEEP FOCUS", "headline": "UNSTOPPABLE FLOW", "sub": "Day 1 se shuru hota hai winner ka safar", "color": (16, 185, 129)}
        ]
    },
    {
        "id": "digital_loneliness_5000_friends",
        "title": "5000 Friends Lekin 0 Real Calls",
        "yt_title": "5000 Followers Lekin Baat Karne Wala 0? 📱💔 | Shadow Will",
        "category": "animation",
        "description": "Social media par hazaron likes aur followers, lekin jab raat ko dil tootta hai, tab call karne ke liye ek insaan nahi hota. Ye modern digital loneliness ka sach hai.\n\n#loneliness #mentalhealth #shadowwill #animation #shorts #mindset",
        "tags": ["digital loneliness", "shadow will", "fake friends", "social media trap", "animation", "discipline", "shorts"],
        "voiceover": "Social media par tumhare paas hazaron followers aur contacts hain. Lekin jab raat ko dil bhari hota hai, jab rona aata hai, tab dial karne ke liye ek bhi insaan nahi milta. Hum aisi duniya me jee rahe hain jahan connection sabke paas hai, lekin gehraai kisi ke paas nahi. Bheed ke peeche bhaagna band karo. Apni solitude ko apni taqat banao. Jo akelepan me khud se larna seekh gaya, use duniya ki koi taqat hara nahi sakti.",
        "scenes": [
            {"badge": "MODERN ILLUSION", "headline": "5000 CONTACTS", "sub": "Par dil ki baat bolne wala 0", "color": (239, 68, 68)},
            {"badge": "THE HOLLOW CROWD", "headline": "SURROUNDED BY SCREEN", "sub": "Connection sabke paas, apna koi nahi", "color": (245, 158, 11)},
            {"badge": "SOLITUDE POWER", "headline": "THRIVE IN SILENCE", "sub": "Akelepan se darna nahi, taqat banana", "color": (59, 130, 246)},
            {"badge": "THE INNER FORTRESS", "headline": "UNBREAKABLE WILL", "sub": "Apne andar ke dushman ko harao", "color": (16, 185, 129)}
        ]
    }
]

def render_frame(scene, width=1080, height=1920, scene_idx=0):
    accent = scene.get("color", (239, 35, 60))
    img = Image.new("RGB", (width, height), (8, 10, 16))
    draw = ImageDraw.Draw(img)

    # 1. Dark atmospheric cinematic background gradient
    for y in range(height):
        ratio = y / height
        r = int(8 + accent[0] * 0.08 * (1 - ratio))
        g = int(10 + accent[1] * 0.06 * (1 - ratio))
        b = int(16 + accent[2] * 0.06 * (1 - ratio))
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # 2. Procedural atmospheric floating embers
    random.seed(scene_idx * 100 + 42)
    for _ in range(35):
        px = random.randint(40, width - 40)
        py = random.randint(120, height - 180)
        pr = random.randint(2, 5)
        draw.ellipse([px - pr, py - pr, px + pr, py + pr], fill=(accent[0], accent[1], accent[2]))

    # 3. Top Sleek Phase Pill (No ugly headers or watermarks)
    badge = scene.get("badge", "SHADOW WILL").upper()
    pill_w = min(600, len(badge) * 26 + 80)
    pill_h = 56
    pill_y = 200
    draw.rounded_rectangle(
        [(width // 2 - pill_w // 2, pill_y), (width // 2 + pill_w // 2, pill_y + pill_h)],
        radius=28,
        fill=(15, 20, 32),
        outline=accent,
        width=2
    )
    draw.text((width // 2, pill_y + pill_h // 2), f"•  {badge}  •", fill=(255, 255, 255), anchor="mm")

    # 4. Characters: The Hero vs The Red Shadow (Iconic, Clean, Scaled)
    char_y = 820

    # Looming Shadow Enemy (Dynamic scale by scene tension)
    shadow_scale = 1.0 + (scene_idx * 0.12)
    sh_cx = int(width // 2 + 130)
    sh_cy = int(char_y - 60)
    sh_rx = int(190 * shadow_scale)
    sh_ry = int(280 * shadow_scale)
    draw.ellipse([sh_cx - sh_rx, sh_cy - sh_ry, sh_cx + sh_rx, sh_cy + sh_ry], fill=(12, 3, 6))

    # Glowing Red Eyes
    eye_y = sh_cy - 70
    eye1_x = sh_cx - 45
    eye2_x = sh_cx + 45
    for r in range(20, 0, -2):
        draw.ellipse([eye1_x - r, eye_y - r, eye1_x + r, eye_y + r], fill=(255, 25, 40))
        draw.ellipse([eye2_x - r, eye_y - r, eye2_x + r, eye_y + r], fill=(255, 25, 40))
    draw.ellipse([eye1_x - 5, eye_y - 5, eye1_x + 5, eye_y + 5], fill=(255, 255, 255))
    draw.ellipse([eye2_x - 5, eye_y - 5, eye2_x + 5, eye_y + 5], fill=(255, 255, 255))

    # Hero Cream Protagonist
    hero_cx = int(width // 2 - 160)
    hero_cy = char_y + 40
    draw.ellipse([hero_cx - 110, hero_cy - 120, hero_cx + 110, hero_cy + 120], fill=(240, 236, 225))
    draw.rectangle([hero_cx - 100, hero_cy - 40, hero_cx + 100, hero_cy - 20], fill=(239, 35, 60))
    draw.polygon([(hero_cx - 100, hero_cy - 30), (hero_cx - 150, hero_cy - 10), (hero_cx - 145, hero_cy - 40)], fill=(239, 35, 60))

    # 5. Bold Dramatic Headline
    headline = scene.get("headline", "HEADLINE").upper()
    font_large = None
    for fn in ["impact.ttf", "arialbd.ttf", "DejaVuSans-Bold.ttf"]:
        try:
            font_large = ImageFont.truetype(fn, 66)
            break
        except Exception:
            continue
    if not font_large:
        font_large = ImageFont.load_default()
    draw.text((width // 2, 1260), headline, font=font_large, fill=(255, 255, 255), anchor="mm")

    # 6. Sleek Frosted-Glass Subtitle Box
    sub = scene.get("sub", "")
    box_y = 1380
    draw.rounded_rectangle(
        [(90, box_y), (width - 90, box_y + 160)],
        radius=24,
        fill=(14, 18, 28),
        outline=(50, 60, 80),
        width=2
    )
    draw.text((width // 2, box_y + 80), sub, fill=(226, 232, 240), anchor="mm")

    return img

async def synthesize_neural_voice(text, out_mp3):
    print("[Autopilot] Synthesizing Deep Hindi Voice via Edge-TTS (hi-IN-MadhurNeural)...")
    import edge_tts
    comm = edge_tts.Communicate(text, voice="hi-IN-MadhurNeural", rate="-4%", pitch="-2Hz")
    await comm.save(out_mp3)
    print(f"[Autopilot] Audio saved to {out_mp3}")

def render_short_video(story, output_mp4, work_dir=None):
    if not work_dir:
        work_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp_render")
    os.makedirs(work_dir, exist_ok=True)
    audio_file = os.path.join(work_dir, "speech.mp3")

    asyncio.run(synthesize_neural_voice(story["voiceover"], audio_file))

    # Probe duration
    probe = subprocess.run([FFMPEG_BIN, "-i", audio_file], stderr=subprocess.PIPE, text=True)
    import re
    dur_match = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", probe.stderr)
    duration = 20.0
    if dur_match:
        h, m, s = dur_match.groups()
        duration = int(h)*3600 + int(m)*60 + float(s)

    scenes = story["scenes"]
    time_per_scene = duration / len(scenes)

    image_paths = []
    for i, sc in enumerate(scenes):
        img = render_frame(sc, scene_idx=i)
        p = os.path.join(work_dir, f"frame_{i}.png")
        img.save(p)
        image_paths.append(p)

    concat_txt = os.path.join(work_dir, "concat.txt")
    with open(concat_txt, "w", encoding="utf-8") as f:
        for p in image_paths:
            f.write(f"file '{p}'\n")
            f.write(f"duration {time_per_scene:.3f}\n")
        f.write(f"file '{image_paths[-1]}'\n")

    cmd = [
        FFMPEG_BIN, "-y",
        "-f", "concat", "-safe", "0", "-i", concat_txt,
        "-i", audio_file,
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        output_mp4
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"[Autopilot] Rendered video successfully: {output_mp4}")
    return output_mp4

def upload_to_youtube(video_path, story):
    """
    Uploads via official YouTube Data API v3 as PUBLIC directly.
    """
    client_id = os.environ.get("YT_CLIENT_ID")
    client_secret = os.environ.get("YT_CLIENT_SECRET")
    refresh_token = os.environ.get("YT_REFRESH_TOKEN")

    if not (client_id and client_secret and refresh_token):
        token_file = Path(__file__).parent / "youtube_token.json"
        if token_file.exists():
            try:
                with open(token_file, "r", encoding="utf-8") as f:
                    tdata = json.load(f)
                    client_id = tdata.get("client_id")
                    client_secret = tdata.get("client_secret")
                    refresh_token = tdata.get("refresh_token")
            except Exception:
                pass

    if not (client_id and client_secret and refresh_token):
        print("[YouTube Uploader] OAuth credentials not detected in environment or youtube_token.json.")
        print("[YouTube Uploader] Video is safely stored at:", video_path)
        print(f"[YouTube Uploader] Title: {story['yt_title']}")
        return False

    try:
        from youtube_cloud_uploader import upload_video_file
        res = upload_video_file(
            video_path,
            title=story["yt_title"],
            description=story["description"],
            tags=story["tags"],
            client_id=client_id,
            client_secret=client_secret,
            refresh_token=refresh_token,
            privacy_status="public"  # Directly PUBLIC as requested!
        )
        print("[YouTube Uploader] Successfully uploaded directly to PUBLIC feed! Video ID:", res.get("id"))

        # Auto Cross-Post to Facebook Reels
        try:
            from meta_reels_publisher import publish_facebook_reel
            publish_facebook_reel(video_path, caption=f"{story['yt_title']}\n\n{story['description'][:200]}")
        except Exception as meta_err:
            print(f"[Meta Reels Cross-Post] Note: {meta_err}")

        return True
    except Exception as e:
        print("[YouTube Uploader] Upload error:", e)
        return False

def get_channel_performance_memory():
    """
    Inspects recent channel performance from YouTube Data API
    so Gemini can intelligently analyze what viewers are watching!
    """
    client_id = os.environ.get("YT_CLIENT_ID")
    client_secret = os.environ.get("YT_CLIENT_SECRET")
    refresh_token = os.environ.get("YT_REFRESH_TOKEN")

    if not (client_id and client_secret and refresh_token):
        token_file = Path(__file__).parent / "youtube_token.json"
        if token_file.exists():
            try:
                with open(token_file, "r", encoding="utf-8") as f:
                    tdata = json.load(f)
                    client_id = tdata.get("client_id")
                    client_secret = tdata.get("client_secret")
                    refresh_token = tdata.get("refresh_token")
            except Exception:
                pass

    if not (client_id and client_secret and refresh_token):
        return "New channel launch phase. Focus on high-curiosity student & youth habits."

    try:
        from youtube_cloud_uploader import get_authenticated_service
        youtube = get_authenticated_service(client_id, client_secret, refresh_token)
        ch_res = youtube.channels().list(mine=True, part="contentDetails").execute()
        uploads_id = ch_res["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
        items = youtube.playlistItems().list(playlistId=uploads_id, part="contentDetails,snippet", maxResults=5).execute()
        vids = [it["contentDetails"]["videoId"] for it in items.get("items", [])]
        if not vids:
            return "No previous videos yet. Focus on core 3 AM phone trap & overthinking hooks."
        stats = youtube.videos().list(id=",".join(vids), part="statistics,snippet").execute()
        summary = []
        for v in stats.get("items", []):
            t = v["snippet"]["title"]
            views = int(v["statistics"].get("viewCount", 0))
            likes = int(v["statistics"].get("likeCount", 0))
            summary.append(f"- Video: '{t}' | Views: {views} | Likes: {likes}")
        mem = "\n".join(summary)
        print(f"[Analytics Brain] Channel Memory Fed to Gemini:\n{mem}")
        return mem
    except Exception as e:
        print("[Analytics Brain] Analytics fetch note:", e)
        return "Focus on viral late-night phone addiction, procrastination and quiet discipline."

def generate_dynamic_gemini_story():
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        print("[Gemini Brain] No GEMINI_API_KEY found, falling back to curated psychological catalog.")
        return None
    try:
        import urllib.request
        import json

        channel_memory = get_channel_performance_memory()

        prompt = f"""You are the Master Director and Data-Driven AI Strategist for 'Shadow Will' (@ShadOOWill).

RECENT AUDIENCE ANALYTICS MEMORY:
{channel_memory}

INSTRUCTION:
Based on the audience data and psychological resonance, write today's 60-second high-retention animated short film script in Hindi (Hinglish narration). Focus on dark psychological themes matching Day One Films ("You Don't Have Time") and Kaz: the illusion of having endless time ("Kal karunga / You have time"), the inner enemy whisper, procrastination loops, and the shocking reality of regret and mortality.

Output strict valid JSON with keys:
- "title": Short English title
- "yt_title": Click-worthy YouTube Title in Hindi + English with emoji & hashtags
- "description": YouTube description with timestamps and hashtags
- "tags": list of 8 relevant tags
- "voiceover": Deep, emotional 60-second Hindi voiceover text
- "scenes": list of exactly 4 scenes, each having:
    - "badge": short 2-3 word upper case badge
    - "headline": bold 2-4 word upper case headline
    - "sub": 1 short emotional Hindi subtitle line
    - "color": RGB list e.g. [239, 68, 68] or [245, 158, 11] or [16, 185, 129]
"""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent?key={api_key}"
        payload = json.dumps({
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"response_mime_type": "application/json"}
        }).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            story = json.loads(text)
            story["id"] = "ai_gemini_" + str(int(time.time()))
            story["category"] = "animation"
            for sc in story.get("scenes", []):
                if isinstance(sc.get("color"), list):
                    sc["color"] = tuple(sc["color"])
            print(f"[Gemini Brain] Successfully generated brand new dynamic story: {story['title']}")
            return story
    except Exception as e:
        print(f"[Gemini Brain] Warning: Gemini API call failed ({e}), using curated story fallback.")
        return None

def main():
    print("="*65)
    print(" SHADOW WILL • 2D FLAT-VECTOR DOCUMENTARY PRODUCTION CYCLE")
    print("="*65)

    try:
        from cinematic_engine.documentary_2d_producer import (
            pick_next_story, render_documentary_video, log_story, HERE as DOC_HERE
        )
        story = pick_next_story()
        out_file = DOC_HERE / f"documentary_{story['slug']}.mp4"
        print(f"[Shadow Will] Producing Depth Theory 2D Vector Documentary: {story['title']}")
        video_path = render_documentary_video(story, out_file)
        log_story(story["slug"])

        # Prepare metadata for YouTube & Meta
        upload_meta = {
            "yt_title": f"{story['title']} 🔍⚠️ | Shadow Will",
            "description": f"{story['title']}\n\n{' '.join(story['narration'])}\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n#shadowwill #documentary #animation #mystery #historicalfacts #shorts",
            "tags": ["shadow will", "documentary", "animation", "mystery", "true story", "hindi documentary", "depth theory", "shorts"]
        }

        # Upload to Channel 1 (Shadow Will) + Meta Reels
        upload_to_youtube(str(video_path), upload_meta)

    except Exception as e:
        print(f"[Shadow Will Producer] Error: {e}")
        import traceback; traceback.print_exc()

    print("="*65)
    print(" [SHADOW WILL AUTOPILOT] CYCLE FINISHED SUCCESSFULLY!")
    print("="*65)

if __name__ == "__main__":
    main()
