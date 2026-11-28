#!/usr/bin/env python3
"""
=============================================================================
CHANNEL 5: DAILY CARTOON SHORTS GOOGLE DRIVE -> YOUTUBE AUTO-UPLOADER
Reads ready .mp4 videos from Google Drive (Daily Cartoon Shorts)
Folder ID: 1sIaO2WhNeef3g7u-_OpzOO4DJVazAQmU
Uploads to YouTube Channel 5 with Auto-Deduplication History
=============================================================================
"""

import os
import sys
import json
import base64
import re
import datetime
from pathlib import Path
import requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

CARTOON_FOLDER_ID = os.environ.get("CARTOON_FOLDER_ID", "1sIaO2WhNeef3g7u-_OpzOO4DJVazAQmU")
BRIDGE_URL = os.environ.get("DRIVE_BRIDGE_URL", "")
HISTORY_FILE = Path("history_cartoon_shorts.json")

def load_history():
    if HISTORY_FILE.exists():
        try:
            return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []

def record_history(file_id: str, file_name: str, yt_video_id: str):
    hist = load_history()
    hist.append({
        "drive_file_id": file_id,
        "file_name": file_name,
        "yt_video_id": yt_video_id,
        "uploaded_at": str(datetime.datetime.now(datetime.timezone.utc))
    })
    HISTORY_FILE.write_text(json.dumps(hist[-100:], indent=2), encoding="utf-8")

def get_youtube_service():
    client_id = os.environ.get("YT_CLIENT_ID_CH5") or os.environ.get("YT_CLIENT_ID")
    client_secret = os.environ.get("YT_CLIENT_SECRET_CH5") or os.environ.get("YT_CLIENT_SECRET")
    refresh_token = os.environ.get("YT_REFRESH_TOKEN_CH5") or os.environ.get("YT_REFRESH_TOKEN")

    if not (client_id and client_secret and refresh_token):
        print("[CartoonUploader] YouTube API secrets missing for Channel 5.", flush=True)
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

def format_clean_title(filename: str) -> str:
    # Example: Great-Emu-War-1932-Hindi.mp4 -> The Great Emu War 1932 (Hindi) #shorts
    stem = Path(filename).stem
    stem = stem.replace("-", " ").replace("_", " ").strip()
    words = stem.split()
    clean_words = []
    for w in words:
        if w.lower() == "hindi":
            clean_words.append("(Hindi)")
        else:
            clean_words.append(w.capitalize())
    clean_title = " ".join(clean_words)
    return f"{clean_title} #shorts #animation"

def list_drive_cartoon_videos():
    if not BRIDGE_URL:
        print("[CartoonUploader] Error: DRIVE_BRIDGE_URL is not set.", flush=True)
        return []
    try:
        r = requests.get(
            BRIDGE_URL,
            params={"action": "list", "folderId": CARTOON_FOLDER_ID},
            timeout=60
        )
        r.raise_for_status()
        data = r.json()
        files = data.get("files", [])
        # Only return .mp4 files
        mp4s = [f for f in files if f.get("name", "").lower().endswith(".mp4")]
        return mp4s
    except Exception as e:
        print(f"[CartoonUploader] Error querying Drive folder: {e}", flush=True)
        return []

def download_video_from_bridge(file_id: str, dest_path: Path):
    print(f"[CartoonUploader] Downloading {dest_path.name} from Google Drive (ID: {file_id})...", flush=True)
    # Direct Google Drive export download
    try:
        direct_url = f"https://drive.google.com/uc?export=download&id={file_id}"
        r = requests.get(direct_url, stream=True, timeout=180)
        if r.status_code == 200:
            with open(dest_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=65536):
                    f.write(chunk)
            if dest_path.stat().st_size > 1000:
                print(f"[CartoonUploader] Direct download success: {dest_path.stat().st_size} bytes -> {dest_path}", flush=True)
                return
    except Exception as e:
        print(f"[CartoonUploader] Direct download fallback triggered: {e}", flush=True)
    
    # Bridge fallback
    r = requests.get(
        BRIDGE_URL,
        params={"action": "get_base64", "id": file_id, "name": dest_path.name},
        timeout=300
    )
    r.raise_for_status()
    data = r.json()
    b64 = data.get("base64")
    if b64:
        dest_path.write_bytes(base64.b64decode(b64))
    print(f"[CartoonUploader] Downloaded {dest_path.stat().st_size} bytes -> {dest_path}", flush=True)

def main():
    print("=== DAILY CARTOON SHORTS (GOOGLE DRIVE -> YOUTUBE) ===")
    history = load_history()
    uploaded_file_ids = {h.get("drive_file_id") for h in history}
    uploaded_names = {h.get("file_name") for h in history}

    files = list_drive_cartoon_videos()
    print(f"[CartoonUploader] Found {len(files)} total video files in Daily Cartoon Shorts folder.")

    pending = [f for f in files if f["id"] not in uploaded_file_ids and f["name"] not in uploaded_names]
    if not pending:
        print("[CartoonUploader] No new pending videos found. Everything is up-to-date!")
        return

    # Pick the newest pending video
    target = pending[-1]
    file_id = target["id"]
    file_name = target["name"]
    print(f"[CartoonUploader] Processing new video: {file_name} (ID: {file_id})")

    local_path = Path("cartoon_build") / file_name
    local_path.parent.mkdir(parents=True, exist_ok=True)
    download_video_from_bridge(file_id, local_path)

    yt = get_youtube_service()
    if not yt:
        print("[CartoonUploader] Skipping YouTube upload (credentials not configured yet).")
        return

    title = format_clean_title(file_name)
    description = (
        f"Daily Animated Story: {title}\n\n"
        "Subscribe for daily animated shorts and stories!\n\n"
        "#shorts #animation #animatedstories #viral #cartoon"
    )
    tags = ["shorts", "animation", "cartoon", "story", "animated short", "history", "hindi"]

    body = {
        "snippet": {
            "title": title[:100],
            "description": description,
            "tags": tags,
            "categoryId": "1",  # Film & Animation
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False,
        },
    }

    media = MediaFileUpload(str(local_path), mimetype="video/mp4", resumable=True)
    req = yt.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    while response is None:
        status, response = req.next_chunk()
        if status:
            print(f"[CartoonUploader] Upload progress: {int(status.progress() * 100)}%", flush=True)

    video_id = response.get("id")
    live_url = f"https://youtube.com/watch?v={video_id}"
    print(f"[CartoonUploader] SUCCESS! Video live at: {live_url}")

    record_history(file_id, file_name, video_id)
    print(f"[CartoonUploader] Recorded in history. File cleanup complete.")

if __name__ == "__main__":
    main()
