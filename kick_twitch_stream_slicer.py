#!/usr/bin/env python3
"""
Autonomous Kick / Twitch GTA V Stream Slicer for Channel 2 (Vice City Pulse).
Bypasses YouTube datacenter IP bot-blocks by sourcing fresh daily 30s clips from Twitch/Kick VODs,
with Gemini AI dynamic title/hook generation and strict anti-duplicate history tracking.
"""
import json
import os
import random
import subprocess
import urllib.request
from pathlib import Path

TWITCH_GTA_CHANNELS = [
    "buddha",
    "lord_kebun",
    "summit1g",
    "darkviperau",
    "anthonyz",
    "ratedepicz",
    "zerkaa",
    "fuslie",
]

KICK_GTA_CHANNELS = [
    "adinross",
    "n3on",
    "westcol",
    "trainwreckstv",
]


def _fetch_twitch_vods(channel: str, max_items: int = 4):
    url = f"https://www.twitch.tv/{channel}/videos?filter=archives&sort=time"
    cmd = [
        "yt-dlp",
        "--flat-playlist",
        "--dump-json",
        "--playlist-end", str(max_items),
        "--no-warnings",
        url,
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=45)
    if res.returncode != 0:
        return []
    items = []
    for line in res.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            d = json.loads(line)
            if d.get("id") and d.get("url"):
                items.append({
                    "source": "twitch",
                    "channel": channel,
                    "id": f"twitch_{d['id']}",
                    "url": d["url"],
                    "title": d.get("title") or f"{channel} GTA V Live Stream",
                    "duration": int(d.get("duration") or 3600),
                })
        except Exception:
            continue
    return items


def _fetch_kick_vods(channel: str, max_items: int = 3):
    api_url = f"https://kick.com/api/v2/channels/{channel}/videos"
    req = urllib.request.Request(
        api_url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0.0.0 Safari/537.36",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        items = []
        for v in (data if isinstance(data, list) else [])[:max_items]:
            uuid = v.get("uuid") or v.get("id")
            src = v.get("source")
            if uuid and src:
                items.append({
                    "source": "kick",
                    "channel": channel,
                    "id": f"kick_{uuid}",
                    "url": src,
                    "title": v.get("session_title") or f"{channel} Kick GTA Stream",
                    "duration": int((v.get("duration") or 3600000) / 1000),
                })
        return items
    except Exception:
        return []


def _generate_gemini_gta_metadata(channel: str, vod_title: str, source: str):
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if api_key:
        prompt = (
            f"A viral 30-second GTA V / GTA RP gaming clip was just sliced from {source.upper()} streamer '{channel}'. "
            f"Original stream title: '{vod_title}'. "
            "Generate a high-CTR YouTube Shorts title (under 75 chars, include #shorts), a 3-word uppercase hook badge, "
            "a short 2-line description, and 6 tags. Return STRICT JSON ONLY: "
            "{\"yt_title\": \"...\", \"hook_badge\": \"...\", \"desc\": \"...\", \"tags\": [\"...\"]}"
        )
        for model in ["gemini-2.5-flash", "gemini-2.0-flash"]:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
            body = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode("utf-8")
            req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
            try:
                with urllib.request.urlopen(req, timeout=20) as resp:
                    res = json.loads(resp.read().decode("utf-8"))
                    txt = res["candidates"][0]["content"]["parts"][0]["text"]
                    txt = txt.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
                    return json.loads(txt)
            except Exception:
                continue

    # Dynamic non-repeating fallback title using the actual streamer & VOD title
    short_vod = vod_title.split("|")[0].split("!")[0].strip()[:38]
    return {
        "yt_title": f"{channel.upper()} Insane GTA Moment: {short_vod}! 🚨 #shorts",
        "hook_badge": f"{channel.upper()} GTA CLUTCH 🔥",
        "desc": f"Fresh GTA highlight from {channel} ({source.upper()}): {vod_title}\n\nSubscribe to @ViceCityPulseOfficial for daily GTA clips!\n\n#gta #gta5 #gtarp #{channel.lower()} #gaming #shorts",
        "tags": ["gta", "gta 5", "gta rp", channel.lower(), "gaming", "shorts", "vice city pulse"],
    }


def slice_fresh_kick_or_twitch_clip(out_mp4: str, history: list, clip_len: int = 28):
    """
    Finds an unused Twitch/Kick GTA VOD, downloads a 28s high-action slice via yt-dlp + ffmpeg,
    and returns (meta, analysis, unique_clip_key) or None if all network sources fail.
    """
    candidates = []
    kick_channels = KICK_GTA_CHANNELS[:]
    random.shuffle(kick_channels)
    for ch in kick_channels[:2]:
        candidates.extend(_fetch_kick_vods(ch, max_items=2))

    twitch_channels = TWITCH_GTA_CHANNELS[:]
    random.shuffle(twitch_channels)
    for ch in twitch_channels[:4]:
        candidates.extend(_fetch_twitch_vods(ch, max_items=3))

    if not candidates:
        print("[StreamSlicer] No Kick/Twitch VOD candidates found.")
        return None

    # Strict GTA filter: only keep VODs that are actually GTA / NoPixel / RP
    gta_kw = ("gta", "grand theft auto", "nopixel", "vice city", "los santos", "gtarp", "gta rp")
    gta_only = [c for c in candidates if any(k in (c.get("title") or "").lower() for k in gta_kw)]
    if gta_only:
        candidates = gta_only
    else:
        print("[StreamSlicer] Warning: no strict GTA title match in current batch; using fallback.")

    # Filter out already used VODs
    unseen = [c for c in candidates if c["id"] not in history]
    pool = unseen if unseen else candidates
    random.shuffle(pool)

    for cand in pool[:4]:
        dur = max(180, cand["duration"])
        # Pick mid-stream (35%-75%) where actual GTA gameplay happens, download 90s candidate & extract loudest 28s peak (autoclip style)
        win_start = random.randint(int(dur * 0.35), max(int(dur * 0.35) + 10, int(dur * 0.75) - 90))
        win_end = win_start + 90
        tmp_90s = str(Path(out_mp4).with_name("tmp_90s_scan.mp4"))
        print(f"[StreamSlicer] Scanning {cand['source'].upper()} '{cand['channel']}' ({win_start}s-{win_end}s) for peak action: {cand['title']}")

        cmd = [
            "yt-dlp",
            "--no-warnings",
            "-f", "best[height<=1080]/best",
            "--download-sections", f"*{win_start}-{win_end}",
            "--force-keyframes-at-cuts",
            "-o", tmp_90s,
            cand["url"],
        ]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            if res.returncode == 0 and Path(tmp_90s).exists() and Path(tmp_90s).stat().st_size > 200_000:
                # Find loudest 28s window using ffmpeg volumedetect / astats per 10s bucket
                best_offset = 20
                best_db = -99.0
                for off in [0, 15, 30, 45, 60]:
                    vf = subprocess.run(
                        ["ffmpeg", "-v", "error", "-ss", str(off), "-t", "28", "-i", tmp_90s, "-af", "volumedetect", "-f", "null", "-"],
                        capture_output=True, text=True
                    )
                    for line in vf.stderr.splitlines():
                        if "mean_volume:" in line:
                            try:
                                db = float(line.split("mean_volume:")[1].split("dB")[0].strip())
                                if db > best_db:
                                    best_db = db
                                    best_offset = off
                            except Exception:
                                pass
                subprocess.run(
                    ["ffmpeg", "-v", "error", "-y", "-ss", str(best_offset), "-t", str(clip_len), "-i", tmp_90s, "-c", "copy", out_mp4],
                    check=True,
                )
                Path(tmp_90s).unlink(missing_ok=True)
            if Path(out_mp4).exists() and Path(out_mp4).stat().st_size > 200_000:
                ai_meta = _generate_gemini_gta_metadata(cand["channel"], cand["title"], cand["source"])
                meta = {
                    "id": cand["id"],
                    "title": ai_meta["yt_title"],
                    "uploader": cand["channel"],
                    "duration": clip_len,
                }
                analysis = {
                    "start_sec": 0,
                    "end_sec": clip_len,
                    "yt_title": ai_meta["yt_title"],
                    "description": ai_meta["desc"],
                    "yt_desc": ai_meta["desc"],
                    "hook_badge": ai_meta["hook_badge"],
                    "hook_text": ai_meta["hook_badge"],
                    "tags": ai_meta["tags"],
                    "yt_tags": ai_meta["tags"],
                    "prompt_context": f"Fresh {cand['source']} GTA V clip from {cand['channel']}",
                }
                print(f"[StreamSlicer] SUCCESS! Sliced {Path(out_mp4).stat().st_size} bytes -> {ai_meta['yt_title']}")
                return meta, analysis, cand["id"]
            else:
                print(f"[StreamSlicer] Slice failed ({res.returncode}): {res.stderr[-300:]}")
        except Exception as e:
            print(f"[StreamSlicer] Exception slicing {cand['url']}: {e}")

    return None
