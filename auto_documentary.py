import base64
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

BRIDGE_URL = os.environ["DRIVE_BRIDGE_URL"]
BRIDGE_SECRET = os.environ.get("DRIVE_BRIDGE_SECRET", "")
DRIVE_FOLDER_ID = os.environ.get("DOC_DRIVE_FOLDER_ID", "1KfsTib0zr1vRYJc_xEXjNod8hyReCa0e")
TTS_VOICE = os.environ.get("TTS_VOICE", "en-US-AndrewNeural")
WORKDIR = Path("doc_build")


def bridge_params(extra=None):
    params = dict(extra or {})
    if BRIDGE_SECRET:
        params["secret"] = BRIDGE_SECRET
    return params


def list_drive_files():
    if not BRIDGE_URL:
        print("[AutoDoc] Notice: DRIVE_BRIDGE_URL is not set.", flush=True)
        return []
    try:
        resp = requests.get(BRIDGE_URL, params=bridge_params({"action": "list"}), timeout=60)
        resp.raise_for_status()
        data = resp.json()
        return data.get("files", [])
    except Exception as e:
        print(f"[AutoDoc] Notice when querying Drive Bridge: {e}", flush=True)
        return []


def download_drive_file(name: str, dest: Path):
    resp = requests.get(
        BRIDGE_URL,
        params=bridge_params({"action": "get_base64", "name": name}),
        timeout=120,
    )
    resp.raise_for_status()
    payload = resp.json()
    if "error" in payload:
        raise RuntimeError(payload["error"])
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(base64.b64decode(payload["base64"]))


def upload_drive_resumable(src: Path, mime_type: str):
    refresh_token = os.environ.get("DRIVE_REFRESH_TOKEN") or os.environ.get("YT_REFRESH_TOKEN", "")
    if not refresh_token:
        print("No refresh token available for Drive resumable upload.", flush=True)
        return None
    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.environ["YT_CLIENT_ID"],
        client_secret=os.environ["YT_CLIENT_SECRET"],
        scopes=["https://www.googleapis.com/auth/drive.file"],
    )
    drive = build("drive", "v3", credentials=creds)
    media = MediaFileUpload(str(src), mimetype=mime_type, chunksize=8 * 1024 * 1024, resumable=True)
    request = drive.files().create(
        body={"name": src.name, "parents": [DRIVE_FOLDER_ID]},
        media_body=media,
        fields="id, webViewLink",
    )
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Drive upload: {int(status.progress() * 100)}%", flush=True)
    print(f"Drive backup ID: {response['id']}", flush=True)
    return response


def upload_drive_file(src: Path, mime_type: str):
    size_mb = src.stat().st_size / (1024 * 1024)
    if size_mb > 35:
        print(f"{src.name} is {size_mb:.1f} MB (>35 MB); using Drive Resumable Upload API.", flush=True)
        return upload_drive_resumable(src, mime_type)
    b64 = base64.b64encode(src.read_bytes()).decode("ascii")
    resp = requests.post(
        BRIDGE_URL,
        params=bridge_params(),
        json={"name": src.name, "mimeType": mime_type, "base64": b64},
        timeout=300,
    )
    resp.raise_for_status()
    return resp.json()


def run_cmd(cmd, cwd=WORKDIR):
    print("+", " ".join(str(c) for c in cmd), flush=True)
    subprocess.run(cmd, cwd=cwd, check=True)


def generate_tts(script_path: Path, out_mp3: Path):
    for attempt in range(1, 4):
        try:
            run_cmd([
                "edge-tts",
                "--voice", TTS_VOICE,
                "--file", script_path.name,
                "--write-media", out_mp3.name,
            ])
            if out_mp3.exists() and out_mp3.stat().st_size > 1000:
                return
        except subprocess.CalledProcessError as exc:
            print(f"edge-tts attempt {attempt} failed: {exc}", flush=True)
            if attempt < 3:
                time.sleep(5)
    raise RuntimeError("edge-tts failed after 3 attempts.")


def upload_to_youtube(video_path: Path, meta: dict):
    creds = Credentials(
        token=None,
        refresh_token=os.environ["YT_REFRESH_TOKEN"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.environ["YT_CLIENT_ID"],
        client_secret=os.environ["YT_CLIENT_SECRET"],
        scopes=["https://www.googleapis.com/auth/youtube.upload"],
    )
    youtube = build("youtube", "v3", credentials=creds)
    body = {
        "snippet": {
            "title": meta.get("title", "AI Geek Documentary"),
            "description": meta.get("description", ""),
            "tags": meta.get("tags", ["documentary", "history", "geopolitics"]),
            "categoryId": meta.get("categoryId", "27"),
        },
        "status": {"privacyStatus": meta.get("privacyStatus", "public")},
    }
    media = MediaFileUpload(str(video_path), mimetype="video/mp4", chunksize=8 * 1024 * 1024, resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"YouTube upload: {int(status.progress() * 100)}%", flush=True)
    print(f"Uploaded video ID: {response['id']}", flush=True)
    return response["id"]


def main():
    WORKDIR.mkdir(parents=True, exist_ok=True)
    files = list_drive_files()
    valid_files = [
        f for f in files
        if not f.get("mimeType", "").startswith("application/vnd.google-apps.")
        and not f["name"].startswith("archive_")
    ]
    names = {f["name"] for f in valid_files}
    print("Drive files:", sorted(names), flush=True)

    if "script.txt" not in names:
        print("No script.txt found in Documentary_Auto; exiting cleanly.")
        sys.exit(0)

    skip = {"final_documentary.mp4", "voiceover.mp3"}
    for fname in sorted(names):
        if fname in skip:
            continue
        download_drive_file(fname, WORKDIR / fname)

    vo_mp3 = WORKDIR / "voiceover.mp3"
    generate_tts(WORKDIR / "script.txt", vo_mp3)
    try:
        upload_drive_file(vo_mp3, "audio/mpeg")
    except Exception as exc:
        print("Drive voiceover upload warning:", exc, flush=True)

    if (WORKDIR / "align_timing.py").exists():
        run_cmd(["python3", "align_timing.py"])
    if (WORKDIR / "board_engine.py").exists():
        run_cmd(["python3", "board_engine.py"])
    if (WORKDIR / "vintage_engine.py").exists():
        run_cmd(["python3", "vintage_engine.py"])
    if (WORKDIR / "splice.sh").exists() and (WORKDIR / "board_raw.mp4").exists() and (WORKDIR / "vintage_insert.mp4").exists():
        run_cmd(["bash", "splice.sh"])
    if (WORKDIR / "sound_bed.py").exists() and (WORKDIR / "cues.json").exists():
        run_cmd(["python3", "sound_bed.py"])
    if (WORKDIR / "mix_and_mux.sh").exists():
        run_cmd(["bash", "mix_and_mux.sh"])

    final_mp4 = WORKDIR / "final_documentary.mp4"
    if not final_mp4.exists():
        alt = WORKDIR / "final.mp4"
        if alt.exists():
            alt.rename(final_mp4)
        else:
            raise FileNotFoundError("final_documentary.mp4 was not produced.")

    meta = {}
    if (WORKDIR / "metadata.json").exists():
        meta = json.loads((WORKDIR / "metadata.json").read_text(encoding="utf-8"))
    if os.environ.get("YT_REFRESH_TOKEN"):
        upload_to_youtube(final_mp4, meta)

    # Auto Cross-Post to Facebook & Instagram
    try:
        from meta_reels_publisher import publish_facebook_reel, publish_instagram_reel
        cap = f"{meta.get('title', 'Chronicle Vault Documentary')}\n\n{meta.get('description', '')[:200]}"
        publish_facebook_reel(final_mp4, caption=cap)
        publish_instagram_reel(final_mp4, caption=cap)
    except Exception as me:
        print("[Meta Cross-Post] Note:", me, flush=True)

    try:
        upload_drive_file(final_mp4, "video/mp4")
    except Exception as exc:
        print("Drive video backup skipped:", exc, flush=True)


if __name__ == "__main__":
    main()