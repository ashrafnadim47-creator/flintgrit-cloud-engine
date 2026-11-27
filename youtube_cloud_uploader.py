# -*- coding: utf-8 -*-
"""
=============================================================================
OFFICIAL YOUTUBE DATA API v3 CLOUD RESUMABLE UPLOADER
=============================================================================
Uploads MP4 video directly to YouTube channel using official OAuth2 Refresh Token.
Requires 0 passwords, 0 user interactions, and works with PC completely OFF.
=============================================================================
"""

import os
import sys
import json
import httplib2
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

def get_authenticated_service(client_id, client_secret, refresh_token):
    token_uri = "https://oauth2.googleapis.com/token"
    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri=token_uri,
        client_id=client_id,
        client_secret=client_secret,
        scopes=["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube"]
    )
    if not creds.valid:
        creds.refresh(Request())
    return build("youtube", "v3", credentials=creds)

def upload_video_file(video_file, title, description, tags, client_id, client_secret, refresh_token, privacy_status="public", thumbnail_file=None):
    if not os.path.exists(video_file):
        raise FileNotFoundError(f"Video file not found: {video_file}")

    youtube = get_authenticated_service(client_id, client_secret, refresh_token)
    try:
        ch_info = youtube.channels().list(part="snippet", mine=True).execute()
        dest_title = ch_info["items"][0]["snippet"]["title"]
        dest_id = ch_info["items"][0]["id"]
        print(f"[YouTube Cloud Uploader] Target Verified: \"{dest_title}\" (ID: {dest_id})")
    except Exception:
        pass

    body = {
        "snippet": {
            "title": title[:100],
            "description": description,
            "tags": tags,
            "categoryId": "27"  # Education / How-to
        },
        "status": {
            "privacyStatus": privacy_status,
            "selfDeclaredMadeForKids": False
        }
    }

    media = MediaFileUpload(video_file, chunksize=-1, resumable=True, mimetype="video/mp4")
    request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=media
    )

    print(f"[YouTube Cloud Uploader] Uploading '{video_file}' as '{title}'...")
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"[YouTube Cloud Uploader] Uploaded {int(status.progress() * 100)}%...")

    vid_id = response.get("id")
    print(f"[YouTube Cloud Uploader] Video uploaded successfully! Video ID: {vid_id}")
    print(f"[YouTube Cloud Uploader] Live URL: https://youtube.com/watch?v={vid_id}")

    # Set Custom Thumbnail if provided
    if thumbnail_file and os.path.exists(thumbnail_file):
        try:
            print(f"[YouTube Cloud Uploader] Setting custom high-CTR thumbnail from {thumbnail_file}...")
            thumb_media = MediaFileUpload(thumbnail_file, mimetype="image/jpeg")
            youtube.thumbnails().set(videoId=vid_id, media_body=thumb_media).execute()
            print("[YouTube Cloud Uploader] Custom Thumbnail successfully published!")
        except Exception as e:
            print(f"[YouTube Cloud Uploader] Thumbnail upload note (requires phone verification on channel): {e}")

    return response
