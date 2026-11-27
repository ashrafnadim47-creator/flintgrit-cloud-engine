import os
import sys
import json
import time
import urllib.request
import urllib.parse
from pathlib import Path

def publish_instagram_reel(video_path, caption="", ig_user_id=None, access_token=None):
    """
    Publishes a vertical video as an Instagram Reel using Instagram Graph API (Resumable Upload).
    """
    ig_user_id = ig_user_id or os.environ.get("IG_USER_ID", "17841417559445496")
    access_token = access_token or os.environ.get("META_PAGE_TOKEN")

    if not access_token or not ig_user_id:
        print("[Instagram Publisher] Skipping: META_PAGE_TOKEN or IG_USER_ID missing.")
        return None

    video_path = Path(video_path)
    if not video_path.exists():
        print(f"[Instagram Publisher] Video not found: {video_path}")
        return None

    file_size = video_path.stat().st_size
    print(f"
[Instagram Publisher] Initiating Instagram Reel Upload: '{video_path.name}' ({file_size / (1024*1024):.2f} MB)...")

    try:
        # Step 1: Create Resumable Container
        init_url = f"https://graph.facebook.com/v19.0/{ig_user_id}/media"
        init_payload = urllib.parse.urlencode({
            "media_type": "REELS",
            "upload_type": "resumable",
            "caption": caption,
            "access_token": access_token
        }).encode("utf-8")

        req_init = urllib.request.Request(init_url, data=init_payload)
        with urllib.request.urlopen(req_init, timeout=30) as resp:
            init_res = json.loads(resp.read().decode())
            container_id = init_res.get("id")
            upload_url = init_res.get("uri")

        print(f"[Instagram Publisher] Step 1 Success: Container ID: {container_id}")

        # Step 2: Upload Video Bytes
        print(f"[Instagram Publisher] Step 2: Uploading {file_size} bytes to Instagram...")
        with open(video_path, "rb") as f:
            video_bytes = f.read()

        req_upload = urllib.request.Request(
            upload_url,
            data=video_bytes,
            headers={
                "Authorization": f"OAuth {access_token}",
                "offset": "0",
                "file_size": str(file_size)
            }
        )
        with urllib.request.urlopen(req_upload, timeout=120) as resp:
            print("[Instagram Publisher] Step 2 Success: Video data sent.")

        # Step 3: Wait for Processing
        print("[Instagram Publisher] Step 3: Waiting for Instagram video processing...")
        for _ in range(15):
            time.sleep(5)
            status_url = f"https://graph.facebook.com/v19.0/{container_id}?fields=status_code&access_token={access_token}"
            req_status = urllib.request.Request(status_url)
            with urllib.request.urlopen(req_status, timeout=15) as resp:
                status_data = json.loads(resp.read().decode())
                code = status_data.get("status_code")
                print(f"[Instagram Publisher] Processing status: {code}")
                if code == "FINISHED":
                    break
                elif code == "ERROR":
                    raise RuntimeError("Instagram processing failed with ERROR status.")

        # Step 4: Publish
        publish_url = f"https://graph.facebook.com/v19.0/{ig_user_id}/media_publish"
        publish_payload = urllib.parse.urlencode({
            "creation_id": container_id,
            "access_token": access_token
        }).encode("utf-8")

        req_pub = urllib.request.Request(publish_url, data=publish_payload)
        with urllib.request.urlopen(req_pub, timeout=30) as resp:
            pub_res = json.loads(resp.read().decode())
            media_id = pub_res.get("id")

        print("=" * 70)
        print(f" [SUCCESS] REEL PUBLISHED TO INSTAGRAM!")
        print(f" Media ID: {media_id}")
        print("=" * 70 + "\n")
        return {"media_id": media_id}

    except Exception as e:
        print(f"[Instagram Publisher Note] Direct API publishing note: {e}")
        print("[Instagram Publisher] If direct Graph API is restricted, ensure Meta Accounts Center has 'Share across profiles' enabled.")
        return None


def publish_facebook_reel(video_path, caption="", page_id=None, access_token=None):
    """
    Publishes a vertical video as a Facebook Reel using Meta Graph API (3-phase resumable upload)
    and then triggers Instagram publishing.
    """
    page_id = page_id or os.environ.get("FB_PAGE_ID", "1268457389686940")
    access_token = access_token or os.environ.get("META_PAGE_TOKEN")
    
    if not access_token:
        print("[Meta Publisher] Warning: META_PAGE_TOKEN is missing. Skipping Facebook upload.")
        return None

    video_path = Path(video_path)
    if not video_path.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")

    file_size = video_path.stat().st_size
    print(f"\n[Meta Publisher] Initiating Facebook Reel Upload: '{video_path.name}' ({file_size / (1024*1024):.2f} MB)...")

    # Phase 1: Start
    start_url = f"https://graph.facebook.com/v19.0/{page_id}/video_reels"
    start_payload = json.dumps({
        "upload_phase": "start",
        "access_token": access_token
    }).encode("utf-8")

    req_start = urllib.request.Request(
        start_url,
        data=start_payload,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req_start, timeout=30) as resp:
        res_data = json.loads(resp.read().decode())
        video_id = res_data.get("video_id")
        upload_url = res_data.get("upload_url")

    print(f"[Meta Publisher] Phase 1 Success: Session opened. Video ID: {video_id}")

    # Phase 2: Binary Video Stream Transfer
    print(f"[Meta Publisher] Phase 2: Transferring {file_size} bytes to Meta Cloud...")
    with open(video_path, "rb") as f:
        video_bytes = f.read()

    req_upload = urllib.request.Request(
        upload_url,
        data=video_bytes,
        headers={
            "Authorization": f"OAuth {access_token}",
            "offset": "0",
            "file_size": str(file_size)
        }
    )
    with urllib.request.urlopen(req_upload, timeout=120) as resp:
        upload_res = json.loads(resp.read().decode())
        print(f"[Meta Publisher] Phase 2 Success: Video data transferred.")

    # Phase 3: Finish & Publish
    print(f"[Meta Publisher] Phase 3: Finalizing and publishing Reel...")
    finish_payload = json.dumps({
        "upload_phase": "finish",
        "access_token": access_token,
        "video_id": video_id,
        "video_state": "PUBLISHED",
        "description": caption
    }).encode("utf-8")

    req_finish = urllib.request.Request(
        start_url,
        data=finish_payload,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req_finish, timeout=30) as resp:
        finish_res = json.loads(resp.read().decode())
        print(f"[Meta Publisher] Phase 3 Success: Reel Published! Response: {finish_res}")

    reel_url = f"https://www.facebook.com/reel/{video_id}"
    print(f"======================================================================")
    print(f" [SUCCESS] REEL PUBLISHED TO FACEBOOK!")
    print(f" Watch URL: {reel_url}")
    print(f"======================================================================\n")

    # Dual Publish: Trigger Instagram Reel Publishing
    publish_instagram_reel(video_path, caption=caption, access_token=access_token)

    return {"video_id": video_id, "url": reel_url}

if __name__ == "__main__":
    test_file = sys.argv[1] if len(sys.argv) > 1 else None
    if test_file:
        publish_facebook_reel(test_file, caption="Viral Gaming Stunt! #shorts #gaming #reels")
    else:
        print("Usage: python meta_reels_publisher.py <video_file>")
