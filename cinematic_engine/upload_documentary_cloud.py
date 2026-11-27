#!/usr/bin/env python3
"""
=============================================================================
DOCUMENTARY CLOUD UPLOADER FOR CHANNEL 3 (CHRONICLE VAULT)
=============================================================================
Uploads completed 1080p documentary videos directly to YouTube using OAuth.
- Sets category: Education (27), custom description, tags, and public status.
- Automatically generates and uploads custom 1280x720 high-CTR thumbnail!
=============================================================================
"""

import os
import sys
import json
import pathlib
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

HERE = pathlib.Path(__file__).resolve().parent
REPO_ROOT = HERE.parent

# Import thumbnail generator
sys.path.insert(0, str(HERE))
try:
    from generate_thumbnail import generate_thumbnail
except Exception:
    generate_thumbnail = None

def get_auth_service():
    client_id = os.environ.get("YT_CLIENT_ID_DOC")
    client_secret = os.environ.get("YT_CLIENT_SECRET_DOC")
    refresh_token = os.environ.get("YT_REFRESH_TOKEN_DOC")

    # Local token file fallback
    token_file = REPO_ROOT / "youtube_token_documentary.json"
    if not (client_id and client_secret and refresh_token) and token_file.exists():
        try:
            with open(token_file, "r", encoding="utf-8") as f:
                td = json.load(f)
                client_id = td.get("client_id")
                client_secret = td.get("client_secret")
                refresh_token = td.get("refresh_token")
        except Exception as e:
            print(f"[Uploader] Error reading local token: {e}")

    if not (client_id and client_secret and refresh_token):
        print("[Uploader] ERROR: Missing YT_CLIENT_ID_DOC, YT_CLIENT_SECRET_DOC, or YT_REFRESH_TOKEN_DOC!")
        return None

    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube"]
    )
    creds.refresh(Request())
    return build("youtube", "v3", credentials=creds)

def upload_documentary(project_dir):
    proj = pathlib.Path(project_dir).resolve()
    print(f"\n[Uploader] Scanning for rendered 1080p video in {proj.parent}...")

    title = "The Secret Flight That Changed Modern Civilization | Full Documentary"
    description = "A forensic deep-dive exploration by Chronicle Vault (@ChronicleVaultDoc)."
    tags = ["documentary", "history", "chronicle vault", "investigation"]
    candidate = None
    thumb_file = proj / "thumbnail_1280x720.jpg"

    # Priority 1: Check publish_meta.json first (from longform engine)
    pub_meta = proj / "publish_meta.json"
    if pub_meta.exists():
        try:
            with open(pub_meta, "r", encoding="utf-8") as f:
                pm = json.load(f)
                if "title" in pm: title = pm["title"]
                if "description" in pm: description = pm["description"]
                if "tags" in pm: tags = pm["tags"]
                if "video_file" in pm and pathlib.Path(pm["video_file"]).exists():
                    candidate = pathlib.Path(pm["video_file"])
                if "thumbnail_file" in pm and pathlib.Path(pm["thumbnail_file"]).exists():
                    thumb_file = pathlib.Path(pm["thumbnail_file"])
                print(f"[Uploader] Loaded longform publish metadata: '{title}'")
        except Exception as e:
            print(f"[Uploader] Note reading publish_meta: {e}")

    # Priority 2: Look for {proj.name}_1080p.mp4 or rendered_raw.mp4
    if not candidate:
        if (proj.parent / f"{proj.name}_1080p.mp4").exists():
            candidate = proj.parent / f"{proj.name}_1080p.mp4"
        elif (proj / "out" / "rendered_raw.mp4").exists():
            candidate = proj / "out" / "rendered_raw.mp4"
        else:
            mp4s = list((proj / "out").glob("*.mp4")) + list(proj.glob("*.mp4")) + list(proj.parent.glob(f"{proj.name}*.mp4"))
            if mp4s:
                candidate = mp4s[0]

    if not candidate or not candidate.exists():
        print(f"[Uploader] ERROR: No completed video found for {proj.name}!")
        return False

    # 1. Generate or locate custom thumbnail
    if not thumb_file.exists() and generate_thumbnail:
        try:
            thumb_file = generate_thumbnail(proj)
        except Exception as e:
            print(f"[Uploader] Warning generating thumbnail: {e}")

    youtube = get_auth_service()
    if not youtube:
        print("[Uploader] Skipping upload because YouTube service could not be authenticated.")
        return False

    # HARD SECURITY LOCK: Verify exact target channel before uploading
    EXPECTED_CH_ID = "UCZkMJVw4XsoOCGhL2lDfi3w"
    try:
        ch_resp = youtube.channels().list(part="id,snippet", mine=True).execute()
        actual_id = ch_resp["items"][0]["id"]
        actual_name = ch_resp["items"][0]["snippet"]["title"]
        print(f"[Security Guard] Connected Channel: \"{actual_name}\" (ID: {actual_id})")
        if actual_id != EXPECTED_CH_ID:
            print(f"[SECURITY ALERT] Target channel mismatch! Expected {EXPECTED_CH_ID}, but got {actual_id}. ABORTING UPLOAD IMMEDIATELY TO PREVENT CROSS-UPLOADS!")
            return False
    except Exception as e:
        print(f"[Security Guard] Warning checking channel info: {e}")

    print(f"[Uploader] Uploading {candidate.name} ({candidate.stat().st_size / (1024*1024):.2f} MB)...")
    print(f"[Uploader] Title: {title}")

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": "27"  # 27 = Education
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False
        }
    }

    media = MediaFileUpload(str(candidate), chunksize=10*1024*1024, resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"[Uploader] Upload progress: {int(status.progress() * 100)}%")

    video_id = response.get("id")
    print("\n" + "="*70)
    print(f" [SUCCESS] DOCUMENTARY UPLOADED TO CHRONICLE VAULT!")
    print(f" Watch Live: https://youtu.be/{video_id}")
    print("="*70)

    # 2. Upload Custom Thumbnail if available
    if thumb_file and thumb_file.exists():
        try:
            print(f"[Uploader] Uploading Custom High-CTR Thumbnail: {thumb_file.name}...")
            tmedia = MediaFileUpload(str(thumb_file), mimetype="image/jpeg")
            youtube.thumbnails().set(videoId=video_id, media_body=tmedia).execute()
            print("[Uploader] [SUCCESS] Custom Thumbnail Set Successfully on YouTube!")
        except Exception as e:
            print(f"[Uploader] Thumbnail upload note (phone verification required for custom thumbs): {e}")

    # 3. Update history_documentaries.json
    try:
        hist_file = HERE / "history_documentaries.json"
        if hist_file.exists():
            with open(hist_file, "r", encoding="utf-8") as hf:
                hdata = json.load(hf)
            if proj.name not in hdata.get("covered_slugs", []):
                hdata.setdefault("covered_slugs", []).append(proj.name)
                with open(hist_file, "w", encoding="utf-8") as hf:
                    json.dump(hdata, hf, indent=2)
                print(f"[Uploader] Logged '{proj.name}' to history_documentaries.json")
    except Exception as he:
        print(f"[Uploader] Note logging history: {he}")

    return True

if __name__ == "__main__":
    pdir = sys.argv[1] if len(sys.argv) > 1 else str(HERE / "assets" / "wright-flyer")
    upload_documentary(pdir)
