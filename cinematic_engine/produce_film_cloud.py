#!/usr/bin/env python3
"""
=============================================================================
1-CLICK CLOUD DOCUMENTARY FILM PRODUCER (FULL-LENGTH 8-10 MINUTE EDITION)
=============================================================================
Runs on GitHub Actions (Ubuntu Cloud Runners):
- 0% CPU on user's laptop
- Autonomous pipeline: Ingest -> Archival Photos -> 5-Chapter Narration -> 
  Ken Burns 1080p Visual Stream -> Ambient Soundscape -> High-CTR Thumbnail -> MP4
=============================================================================
"""

import os
import sys
import json
import shutil
import pathlib
import subprocess

HERE = pathlib.Path(__file__).resolve().parent

def build_cloud_documentary(project_dir=None):
    from documentary_longform_engine import produce_todays_full_documentary
    
    print("============================================================")
    print(" STARTING CHRONICLE VAULT 8-10 MINUTE FULL DOCUMENTARY ENGINE")
    print("============================================================")
    
    meta = produce_todays_full_documentary()
    video_path = pathlib.Path(meta["video_file"])
    
    print("\n============================================================")
    print(f" [SUCCESS] 1080P FULL DOCUMENTARY READY: {video_path.name}")
    print(f" Title: {meta['title']}")
    print(f" Size: {video_path.stat().st_size / (1024*1024):.2f} MB")
    print("============================================================")
    return video_path

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else None
    build_cloud_documentary(target)
