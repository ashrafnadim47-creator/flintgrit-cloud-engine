# -*- coding: utf-8 -*-
"""
=============================================================================
SHADOW WILL • MASTER AI ANIMATION STUDIO (TRUE GEMINI VISUAL ARCHITECT)
=============================================================================
Gemini AI Brain is NOT just a text rewriter.
Gemini generates the ENTIRE visual film:
- 15 Authentic Visual Sets (street_rain, gym, stairs, hill, city, desk, mirror, etc.)
- Character physical motion & poses (sprint in rain, heavy bag punch, curl, stand, climb)
- Weather & lighting (midnight rain, dawn fog, sunset aura, sparks)
- Dynamic day counters & red shadow whispers
- Real broadcast-grade piano & sub-bass ambient score!
=============================================================================
"""

import os
import sys
import copy
import time
import json
import urllib.request
import pathlib
import subprocess

BASE_DIR = pathlib.Path(__file__).resolve().parent
KAZ_DIR = BASE_DIR / "kaz_engine"
RENDER_SCRIPT = KAZ_DIR / "scripts" / "render.py"
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

VALID_SETS = ["bedroom", "couch", "desk", "mirror", "gym", "city", "stairs", "hill", "street_rain", "clock_closeup", "spotlight"]
VALID_PALETTES = ["night", "cold", "dawn", "sunset", "warm", "rain", "black", "cyberpunk", "emerald", "golden", "ice", "crimson_abyss", "tokyo_neon", "thunder"]
VALID_POSES = ["walk", "run", "punch", "slump", "lie", "sit", "stand", "curl", "on_stairs", "pushup"]

def build_dynamic_gemini_film():
    """
    Empowers Gemini AI to design the FULL film: visuals, sets, poses, and narrative.
    """
    print("[AI Director] Gemini Brain is designing a brand new, unseen visual story from scratch...")
    
    prompt = f"""You are the Master Visual Film Director for 'Shadow Will' (@ShadOOWill).
Your job is to architect an original 2-minute 2D psychological animated short film matching 'Day One Films' and 'Last Soul'.
NO SPOKEN VOICEOVER. Pure visual storytelling through deep cinematic scenes, physical metaphors, day counters, captions, and glowing shadow whispers.

CRITICAL VISUAL DIRECTIVE:
DO NOT make every scene black and red or in a bedroom!
You have rich visual palettes:
- "cyberpunk": neon violet & electric cyan
- "emerald": misty deep jade forest & obsidian
- "golden": warm sunrise & amber horizon of triumph
- "ice": arctic glacial teal & navy frost
- "crimson_abyss": dramatic charcoal & crimson red horizon
- "tokyo_neon": midnight blue & hot magenta
- "thunder": stormy dark navy & silver lightning
- "dawn", "sunset", "cold", "rain", "night"

VARY the environments across the 16 scenes:
(e.g., Scene 1: "street_rain", Scene 2: "desk", Scene 3: "mirror", Scene 4: "gym", Scene 5: "stairs", Scene 6: "city", Scene 7: "hill"). DO NOT repeat the same set consecutively!

DAY ONE FILMS PHYSICAL METAPHORS (USE THEM CREATIVELY!):
1. "price_tag": Floating retail value tag showing self-worth or transactional human nature.
   Examples:
   - {{"price": "$100", "strike": "$80"}} (compromise)
   - {{"price": "$60", "strike": "$40"}} (getting cheaper)
   - {{"price": "FREE"}} (taken for granted)
   - {{"price": "NOT FOR SALE"}} (regained self-respect)
2. "phone_popup": Late-night phone notification UI showing distraction, toxic ex/friends asking favors:
   - {{"sender": "Sara", "message": "u up? need a ride", "time": "2:07 AM"}}
   - {{"sender": "Group Chat", "message": "party tonight bro pull up", "time": "11:45 PM"}}
3. "dropped_bag": Heavy luggage/burden dropped on the floor:
   - {{"x": 600}}
4. MULTI-CHARACTERS: You can have multiple characters in a scene by setting "hero" as a list:
   - Protagonist: {{"x": 420, "pose": "stand", "mood": "determined"}}
   - Brother/Friend/Bully: {{"x": 640, "pose": "slump", "cap_color": [255, 45, 45], "scale": 0.88}}

VARY the shadow entity's glow color ("glow_color") based on the psychological state:
- [255, 45, 45] (Crimson Anger / Aggression)
- [180, 50, 255] (Toxic Phantom Purple / Comfort / Doubt)
- [40, 220, 255] (Ice Blue / Emptiness / Anxiety)
- [255, 175, 20] (Golden Greed / False Hope)
- [30, 240, 120] (Spectral Emerald / Envy)

CRITICAL STORYTELLING RULE (TOPIC-SPECIFIC METAPHORS):
DO NOT cram every prop or element into every video! Pick ONLY the visual metaphor that serves today's specific topic:
- Theme: Self-Respect / Transactional People -> Use "price_tag" ($100 -> $80 -> FREE -> NOT FOR SALE). No phone needed.
- Theme: Dopamine Trap / Late-Night Overthinking -> Use "phone_popup" (2:07 AM texts) & "clock_closeup". No price tag needed.
- Theme: Comparison / Envy / Family -> Use Multi-Character (Hero vs Brother with red cap).
- Theme: Quiet Grind / Solitude -> Use "street_rain", "stairs", "dropped_bag", "gym", and "golden" victory palette.

CHOOSE ONE UNIQUE, UNFORGETTABLE PSYCHOLOGICAL THEME TODAY:
(e.g., The Price of Being Too Available, The Brother Who Had It Easy, When Silence Speaks Louder Than Words, Breaking The Dopamine Chain, The Weight We Carry For Others, Cold Solitude vs Fake Company).

Design a 16-scene visual storyboard.
For each scene, choose from these visual components:
- "set": One of {VALID_SETS}
- "palette": One of {VALID_PALETTES}
- "duration": 5.0 to 7.0 seconds (Total must be 110-130 seconds)
- "day": Optional string e.g. "DAY 1", "DAY 15", "DAY 60", "DAY 120"
- "caption": 1 powerful, emotional Hindi line (short, poetic, relatable, philosophical)
- "whisper": Optional chilling typewriter text (what the inner shadow whispers)
- "hero": dict or list of character dicts with "pose" (one of {VALID_POSES}), "mood" ("tired", "sad", "determined", "angry", "happy"), optional "cap_color": [R,G,B], "headband": true
- "price_tag": optional dict {{"price": "$100", "strike": "$80"}} or {{"price": "FREE"}}
- "phone_popup": optional dict {{"sender": "...", "message": "...", "time": "..."}}
- "dropped_bag": optional dict {{"x": 600}}
- "shadow": dict with "scale" (0.5 to 1.7), "glow_color": [R, G, B], optional "behind": true, "eyes": true
- "weather": optional "rain": true, or "sparks": true, or "aura": [255, 180, 50]

Return STRICT JSON with keys:
- "title": English title (e.g. "Self Respect: The Cost of Being Free")
- "yt_title": Viral Click-worthy YouTube Title in Hindi & English (e.g. "Jab Log Muft Samajhne Lage | Day One Animated Film")
- "description": High-retention description with timestamps and story summary (NO #shorts)
- "tags": 8-10 SEO tags
- "scenes": Array of 16 scene objects as described above.
"""

    if not GEMINI_KEY:
        print("[AI Director] No API key, using diverse fallback story.")
        return None

    story = None
    for model_name in ["gemini-3.5-flash-lite", "gemini-3.1-flash-lite", "gemini-3-flash-preview"]:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GEMINI_KEY}"
            payload = json.dumps({
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"response_mime_type": "application/json"}
            }).encode("utf-8")
            req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=35) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                story = json.loads(text)
                print(f"[AI Director] Successfully architected storyboard via {model_name}!")
                break
        except Exception as e:
            print(f"[AI Director] {model_name} note: {e}, trying next model...")
            story = None

    if not story:
        return None

    try:
        # Validate and sanitize all scenes
        sanitized_scenes = []
        for sc in story.get("scenes", []):
            s_set = sc.get("set", "city")
            if s_set not in VALID_SETS:
                s_set = "city"
            s_pal = sc.get("palette", "night")
            if s_pal not in VALID_PALETTES:
                s_pal = "night"
            
            # Support single hero dict OR multi-character list
            raw_hero = sc.get("hero", {"pose": "stand", "x": 500})
            if isinstance(raw_hero, list):
                clean_heroes = []
                for h in raw_hero:
                    if isinstance(h, dict):
                        h_copy = dict(h)
                        if h_copy.get("pose") not in VALID_POSES:
                            h_copy["pose"] = "stand"
                        clean_heroes.append(h_copy)
                hero = clean_heroes if clean_heroes else [{"pose": "stand", "x": 500}]
            elif isinstance(raw_hero, dict):
                hero = dict(raw_hero)
                if hero.get("pose") not in VALID_POSES:
                    hero["pose"] = "stand"
                hero["x"] = hero.get("x", 500)
            else:
                hero = {"pose": "stand", "x": 500}
            
            shadow = sc.get("shadow", {})
            if not isinstance(shadow, dict):
                shadow = {"scale": 1.2, "x": 800}
            else:
                shadow["scale"] = max(0.4, min(1.8, float(shadow.get("scale", 1.2))))
                shadow["x"] = shadow.get("x", 800)
                if "glow_color" in shadow:
                    shadow["glow_color"] = shadow["glow_color"]
                elif "color" in shadow:
                    shadow["color"] = shadow["color"]
                
            dur = max(4.0, min(8.5, float(sc.get("duration", 6.0))))
            
            clean_sc = {
                "set": s_set,
                "palette": s_pal,
                "duration": dur,
                "caption": sc.get("caption", ""),
                "hero": hero,
                "shadow": shadow
            }
            # Preserve Day One Films dynamic props & metaphors!
            if sc.get("price_tag"):
                clean_sc["price_tag"] = sc["price_tag"]
            if sc.get("phone_popup"):
                clean_sc["phone_popup"] = sc["phone_popup"]
            if sc.get("dropped_bag"):
                clean_sc["dropped_bag"] = sc["dropped_bag"]
            if sc.get("props"):
                clean_sc["props"] = sc["props"]
            if sc.get("day"):
                clean_sc["day"] = str(sc["day"])
            if sc.get("whisper"):
                clean_sc["whisper"] = str(sc["whisper"])
            if sc.get("whisper_color"):
                clean_sc["whisper_color"] = sc["whisper_color"]
            if sc.get("clock"):
                clean_sc["clock"] = str(sc["clock"])
            if sc.get("meter"):
                clean_sc["meter"] = sc["meter"]
            if sc.get("big_text"):
                clean_sc["big_text"] = sc["big_text"]
            if sc.get("weather"):
                if isinstance(sc["weather"], dict):
                    clean_sc.update(sc["weather"])
            sanitized_scenes.append(clean_sc)

        if len(sanitized_scenes) >= 10:
            story["scenes"] = sanitized_scenes
            story["id"] = "ai_orig_" + str(int(time.time()))
            print(f"[AI Director] Gemini successfully architected a 100% ORIGINAL visual film: '{story['title']}' ({len(sanitized_scenes)} scenes, diverse sets)")
            return story
    except Exception as e:
        print(f"[AI Director] Sanitization note: {e}")

    return None

def produce_animated_film(story):
    work_dir = BASE_DIR / "temp_kaz_render"
    work_dir.mkdir(exist_ok=True)

    story_json_path = work_dir / "storyboard.json"
    with open(story_json_path, "w", encoding="utf-8") as f:
        json.dump({"title": story["title"], "scenes": story["scenes"]}, f, indent=2)

    total_duration = sum(s["duration"] for s in story["scenes"])
    print(f"[Kaz Animation Studio] Total Storyboard Duration: {total_duration:.1f}s ({total_duration/60:.2f} mins) across {len(story['scenes'])} scenes")

    # 1. Synthesize Real Cinematic Score (Piano + 55Hz Sub-Bass Drone + Impacts)
    music_file = work_dir / "cinematic_score.wav"
    try:
        from kaz_engine.scripts.build_cinematic_music import generate_ambient_score
        generate_ambient_score(total_duration=total_duration, output_wav=music_file)
    except Exception as e:
        print(f"[Music Notice] Music build note: {e}")

    # 2. Render Full 2D Animated Film
    output_film = str(BASE_DIR / f"Film_{story['id']}_{int(time.time())}.mp4")
    print(f"[Kaz Animation Studio] Rendering authentic Pure Cinema 2D film to: {output_film}...")

    render_cmd = [
        sys.executable,
        str(RENDER_SCRIPT),
        str(story_json_path),
        "-o", output_film,
        "--res", "720",
        "--fps", "12"
    ]
    if music_file.exists():
        render_cmd.extend(["--music", str(music_file)])

    subprocess.run(render_cmd, check=True)
    print(f"[Kaz Animation Studio] Film rendered successfully! Size: {os.path.getsize(output_film)} bytes")
    return output_film

def generate_high_ctr_thumbnail(story, output_thumb):
    from PIL import Image, ImageDraw, ImageFont
    font_bold = KAZ_DIR / "assets" / "fonts" / "Poppins-Bold.ttf"
    img = Image.new("RGB", (1280, 720), (18, 20, 28))
    draw = ImageDraw.Draw(img)

    for y in range(720):
        ratio = y / 720.0
        r = int(28 + 20 * (1 - ratio))
        g = int(20 + 15 * (1 - ratio))
        b = int(38 + 18 * (1 - ratio))
        draw.line([(0, y), (1280, y)], fill=(r, g, b))

    char_x, char_y = 280, 420
    draw.ellipse([(char_x - 85, char_y - 85), (char_x + 85, char_y + 85)], fill=(245, 240, 225))
    draw.rectangle([(char_x - 80, char_y - 25), (char_x + 80, char_y - 8)], fill=(255, 45, 45))

    sh_x, sh_y = 920, 360
    draw.ellipse([(sh_x - 140, sh_y - 170), (sh_x + 140, sh_y + 170)], fill=(225, 25, 45))
    draw.ellipse([(sh_x - 45, sh_y - 35), (sh_x - 15, sh_y - 5)], fill=(255, 255, 255))
    draw.ellipse([(sh_x + 15, sh_y - 35), (sh_x + 45, sh_y - 5)], fill=(255, 255, 255))

    # Bold Title
    title_words = story["title"].split(":")
    line1 = title_words[0].upper().strip()
    line2 = title_words[1].strip() if len(title_words) > 1 else "DO NOT GIVE UP"

    try:
        f_large = ImageFont.truetype(str(font_bold), 72)
        f_sub = ImageFont.truetype(str(font_bold), 36)
    except Exception:
        f_large = f_sub = ImageFont.load_default()

    draw.text((60, 60), line1, font=f_large, fill=(255, 215, 0))
    draw.text((65, 155), line2[:35], font=f_sub, fill=(240, 240, 240))

    img.save(output_thumb, quality=95)
    print(f"[Thumbnail Studio] Thumbnail saved: {output_thumb}")
    return output_thumb

def upload_film_to_channel_1(video_path, story, thumbnail_path=None):
    client_id = os.environ.get("YT_CLIENT_ID")
    client_secret = os.environ.get("YT_CLIENT_SECRET")
    refresh_token = os.environ.get("YT_REFRESH_TOKEN")

    if not (client_id and client_secret and refresh_token):
        token_file = BASE_DIR / "youtube_token.json"
        if token_file.exists():
            try:
                with open(token_file, "r") as f:
                    tdata = json.load(f)
                    client_id = tdata.get("client_id")
                    client_secret = tdata.get("client_secret")
                    refresh_token = tdata.get("refresh_token")
            except Exception:
                pass

    if not (client_id and client_secret and refresh_token):
        print("[YouTube Uploader] OAuth credentials not detected.")
        return False

    from youtube_cloud_uploader import upload_video_file
    print(f"[YouTube Publisher] Publishing '{story['yt_title']}' as PUBLIC Long-Form Film to Channel 1...")
    res = upload_video_file(
        video_path,
        title=story["yt_title"],
        description=story["description"],
        tags=story["tags"],
        client_id=client_id,
        client_secret=client_secret,
        refresh_token=refresh_token,
        privacy_status="public",
        thumbnail_file=thumbnail_path
    )

    try:
        from meta_reels_publisher import publish_facebook_reel
        print("[Meta Publisher] Cross-publishing film to Instagram & Facebook Reels...")
        publish_facebook_reel(video_path, caption=story.get("description", ""))
    except Exception as me:
        print(f"[Meta Publisher] Meta upload note: {me}")

    return res

def get_daily_kaz_story():
    """
    Selects a fresh, non-repeating 2D animated psychological film storyboard.
    Tracks history in history_shadow_will.json to ensure zero repetitive content!
    """
    history_file = BASE_DIR / "history_shadow_will.json"
    covered = []
    if history_file.exists():
        try:
            with open(history_file, "r", encoding="utf-8") as f:
                covered = json.load(f).get("covered_ids", [])
        except Exception:
            covered = []

    # Try building fresh film via Gemini AI first
    dynamic_story = build_dynamic_gemini_film()
    if dynamic_story and dynamic_story.get("id") not in covered:
        covered.append(dynamic_story["id"])
        with open(history_file, "w", encoding="utf-8") as f:
            json.dump({"covered_ids": covered}, f, indent=2)
        return dynamic_story

    # Core Architectural Storyboards Catalog (Diverse, High-Retention Kaz Masterpieces)
    catalog = [
        {
            "id": "the_3am_glow",
            "file": KAZ_DIR / "examples" / "the-3am-glow.json",
            "yt_title": "Raat Ke 3:00 AM Ka Phone Trap: Dimaag Ka Silent Poison 📱🌑 | Shadow Will",
            "desc": "Raat ke 3 baje blue screen ka glow... Har raat khud se waada karna ki kal se change honge, aur subah sirf exhaustion bacha rehna. Ye kahani aapki aur aapke inner enemy ki hai.\n\n#shadowwill #animation #discipline #innerenemy #dopamine #shorts #mentalhealth",
            "tags": ["shadow will", "3am phone trap", "dopamine detox", "inner enemy", "kaz animation", "discipline motivation", "dark psychology"]
        },
        {
            "id": "the_5am_lie",
            "file": KAZ_DIR / "examples" / "the-5am-lie.json",
            "yt_title": "Subah 5:00 AM Ka Sabse Bada Jhooth: 'Bas 5 Minute Aur' ⏰💀 | Shadow Will",
            "desc": "Alarm bajta hai aur dimaag dheere se whisper karta hai: 'Bas 5 minute aur, kal se pakka uthenge.' Ye 5 minute aapke sapno ko roz murder karte hain. Tod do is saaye ko.\n\n#shadowwill #5amclub #discipline #innerenemy #morningmotivation #shorts",
            "tags": ["shadow will", "5am motivation", "alarm snooze trap", "discipline vs motivation", "stoic hindi", "inner enemy"]
        },
        {
            "id": "the_cost_of_later",
            "file": KAZ_DIR / "examples" / "the-cost-of-later.json",
            "yt_title": "\"Baad Me Karunga\" — Zindagi Barbaad Karne Ka Silent Loop ⏳🔥 | Shadow Will",
            "desc": "Hum sochte hain hamare paas bohot waqt hai. 'Kal karunga, agle hafte karunga.' Aur ek din aakh khulti hai to jawani nikal chuki hoti hai. Time waits for no one.\n\n#shadowwill #procrastination #timeisrunningout #regret #discipline #shorts",
            "tags": ["procrastination hindi", "shadow will", "the cost of later", "stop wasting time", "inner enemy", "stoicism"]
        }
    ]

    # Select candidate that hasn't been recently covered
    candidates = [c for c in catalog if c["id"] not in covered]
    if not candidates:
        covered = [] # Reset history cycle
        candidates = catalog

    chosen = candidates[0]
    with open(chosen["file"], "r", encoding="utf-8") as f:
        story_data = json.load(f)

    story_data["id"] = chosen["id"]
    story_data["yt_title"] = chosen["yt_title"]
    story_data["description"] = chosen["desc"]
    story_data["tags"] = chosen["tags"]

    covered.append(chosen["id"])
    with open(history_file, "w", encoding="utf-8") as f:
        json.dump({"covered_ids": covered}, f, indent=2)

    print(f"[Story Rotator] Selected fresh unrepeated story: '{story_data['title']}' (ID: {chosen['id']})")
    return story_data

def main():
    print("="*70)
    print(" SHADOW WILL • PRODUCING DYNAMIC ORIGINAL AI ANIMATED FILM")
    print("="*70)

    story = get_daily_kaz_story()
    film_path = produce_animated_film(story)
    thumb_path = str(BASE_DIR / f"Thumb_{story['id']}.jpg")
    generate_high_ctr_thumbnail(story, thumb_path)
    upload_film_to_channel_1(film_path, story, thumbnail_path=thumb_path)

    print("\n" + "="*70)
    print(" [SHADOW WILL PRODUCTION CYCLE COMPLETE!]")
    print("="*70)

if __name__ == "__main__":
    main()
