import asyncio
import base64
import json
import math
import os
import subprocess
import sys
from pathlib import Path

import requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

BRIDGE_URL = os.environ.get("DRIVE_BRIDGE_URL", "")
BRIDGE_SECRET = os.environ.get("DRIVE_BRIDGE_SECRET", "")
TTS_VOICE = os.environ.get("TTS_VOICE", "en-US-ChristopherNeural")
BUILD_DIR = Path("history_build")


def bridge_params(extra=None):
    params = dict(extra or {})
    if BRIDGE_SECRET:
        params["secret"] = BRIDGE_SECRET
    return params


def get_pending_script():
    if not BRIDGE_URL:
        print("Error: DRIVE_BRIDGE_URL is not set.", flush=True)
        return None
    try:
        r = requests.get(
            BRIDGE_URL,
            params=bridge_params({"action": "get_script"}),
            timeout=60,
        )
        r.raise_for_status()
        res = r.json()
        if res.get("found"):
            return res
    except Exception as e:
        print("Notice when querying get_script:", e, flush=True)
    return None


def get_pending_mp4():
    if not BRIDGE_URL:
        return None
    try:
        r = requests.get(
            BRIDGE_URL,
            params=bridge_params({"action": "get_mp4"}),
            timeout=180,
        )
        r.raise_for_status()
        res = r.json()
        if res.get("found"):
            return res
    except Exception as e:
        print("Notice when querying get_mp4:", e, flush=True)
    return None


def upload_mp3_to_bridge(folder_id: str, mp3_path: Path):
    if not (BRIDGE_URL and mp3_path.exists()):
        return False
    b64 = base64.b64encode(mp3_path.read_bytes()).decode("ascii")
    payload = {
        "action": "upload_mp3",
        "folderId": folder_id,
        "mp3Base64": b64,
    }
    if BRIDGE_SECRET:
        payload["secret"] = BRIDGE_SECRET
    r = requests.post(BRIDGE_URL, json=payload, timeout=120)
    r.raise_for_status()
    print("Uploaded voiceover.mp3 to Drive subfolder:", r.json(), flush=True)
    return True


def mark_uploaded_on_bridge(folder_id: str, youtube_url: str):
    if not BRIDGE_URL:
        return False
    payload = {
        "action": "mark_uploaded",
        "folderId": folder_id,
        "youtubeUrl": youtube_url,
    }
    if BRIDGE_SECRET:
        payload["secret"] = BRIDGE_SECRET
    r = requests.post(BRIDGE_URL, json=payload, timeout=60)
    return r.ok


def get_youtube_service():
    client_id = (
        os.environ.get("CHRONICLE_CLIENT_ID")
        or os.environ.get("YT_CLIENT_ID")
        or os.environ.get("YOUTUBE_CLIENT_ID")
    )
    client_secret = (
        os.environ.get("CHRONICLE_CLIENT_SECRET")
        or os.environ.get("YT_CLIENT_SECRET")
        or os.environ.get("YOUTUBE_CLIENT_SECRET")
    )
    refresh_token = (
        os.environ.get("CHRONICLE_REFRESH_TOKEN")
        or os.environ.get("YT_REFRESH_TOKEN")
        or os.environ.get("YOUTUBE_REFRESH_TOKEN")
    )
    if not (client_id and client_secret and refresh_token):
        print("YouTube API secrets missing; skipping upload to Chronicle Vault.", flush=True)
        return None

    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=["https://www.googleapis.com/auth/youtube.upload"],
    )
    return build("youtube", "v3", credentials=creds)


def upload_short_to_youtube(video_path: Path, meta: dict, topic_title: str):
    youtube = get_youtube_service()
    if not youtube:
        return None

    title = meta.get("title") or f"{topic_title} #shorts #history"
    description = (
        meta.get("description")
        or f"Historical 2.5D Animated Short: {topic_title}.\n\nSubscribe to Chronicle Vault for daily animated history stories."
    )
    tags = meta.get("tags") or ["history", "shorts", "animation", "map", "documentary", "chronicle vault"]

    body = {
        "snippet": {
            "title": title[:100],
            "description": description,
            "tags": tags,
            "categoryId": "27",
        },
        "status": {
            "privacyStatus": meta.get("privacyStatus", "public"),
            "selfDeclaredMadeForKids": False,
        },
    }
    media = MediaFileUpload(str(video_path), mimetype="video/mp4", chunksize=-1, resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"YouTube upload progress: {int(status.progress() * 100)}%", flush=True)
    video_id = response.get("id")
    yt_url = f"https://youtu.be/{video_id}"
    print(f"Successfully uploaded to Chronicle Vault YouTube Channel: {yt_url}", flush=True)
    return yt_url


def upload_to_meta_short(video_path, meta, title):
    token = os.environ.get("META_ACCESS_TOKEN") or os.environ.get("META_PAGE_TOKEN")
    if not token:
        print("[Meta Reels] Skipping: No META_ACCESS_TOKEN or META_PAGE_TOKEN found.", flush=True)
        return
    ig_id = os.environ.get("INSTAGRAM_ACCOUNT_ID") or os.environ.get("IG_USER_ID", "17841417559445496")
    fb_id = os.environ.get("FACEBOOK_PAGE_ID") or os.environ.get("FB_PAGE_ID", "1268457389686940")
    caption = f"{meta.get('title', title)}\n\n{' '.join(['#' + t for t in meta.get('tags', ['Shorts', 'History', 'ChronicleVault'])])}"
    print("Meta credentials detected. Auto-dispatching cross-post to Instagram & Facebook...", flush=True)
    try:
        from meta_reels_publisher import publish_facebook_reel, publish_instagram_reel
        if fb_id:
            print(f"[Facebook Reels] Publishing Reel to Page ({fb_id})...", flush=True)
            publish_facebook_reel(video_path, caption=caption, page_id=fb_id, access_token=token)
        if ig_id:
            print(f"[Instagram Reels] Publishing Reel to Instagram ({ig_id})...", flush=True)
            publish_instagram_reel(video_path, caption=caption, ig_user_id=ig_id, access_token=token)
    except Exception as e:
        print(f"[Meta Cross-Post Error]: {e}", flush=True)


def main():
    BUILD_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Check for ready final_short.mp4 first
    mp4_res = get_pending_mp4()
    if mp4_res and mp4_res.get("found"):
        print(f"Found ready final_short.mp4 for topic: {mp4_res.get('folderName')}", flush=True)
        final_mp4 = BUILD_DIR / "final_short.mp4"
        final_mp4.write_bytes(base64.b64decode(mp4_res["mp4Base64"]))

        topic_title = mp4_res.get("folderName", "History").split("_", 1)[-1].replace("-", " ").replace("_", " ").strip()
        meta = mp4_res.get("meta") or {}
        yt_url = upload_short_to_youtube(final_mp4, meta, topic_title)
        upload_to_meta_short(final_mp4, meta, topic_title)
        if yt_url:
            mark_uploaded_on_bridge(mp4_res["folderId"], yt_url)
        return

    # 2. Check for pending script to generate voiceover
    script_res = get_pending_script()
    if not (script_res and script_res.get("found")):
        print("No pending script.txt or final_short.mp4 found in HistoryShorts_Auto; exiting cleanly.", flush=True)
        sys.exit(0)

    folder_id = script_res["folderId"]
    folder_name = script_res.get("folderName", "History_Short")
    script_text = script_res["script"]
    print(f"Processing script for: {folder_name}", flush=True)

    script_file = BUILD_DIR / "script.txt"
    script_file.write_text(script_text, encoding="utf-8")

    # 3. Generate voiceover.mp3 via edge-tts
    vo_path = BUILD_DIR / "voiceover.mp3"
    print(f"Generating voiceover via edge-tts ({TTS_VOICE})...", flush=True)
    subprocess.run([
        "edge-tts",
        "--voice", TTS_VOICE,
        "--file", str(script_file),
        "--write-media", str(vo_path),
    ], check=True)

    # 4. Upload voiceover.mp3 back to that specific Drive subfolder
    upload_mp3_to_bridge(folder_id, vo_path)
    print("Voiceover step complete. Subfolder is ready for video rendering.", flush=True)


if __name__ == "__main__":
    main()
