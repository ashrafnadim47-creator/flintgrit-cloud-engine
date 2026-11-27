#!/usr/bin/env python3
"""
Playwright Chromium headless WebGL renderer for Shadow Will Merged Engine.
Renders frames from web/index.html + web/story.js using SwiftShader (no GPU needed).
"""
import argparse
import base64
import functools
import http.server
import os
import socketserver
import threading
import time
from pathlib import Path
from playwright.sync_api import sync_playwright


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass


def start_server(web_dir: Path):
    handler = functools.partial(QuietHandler, directory=str(web_dir))
    httpd = socketserver.TCPServer(("127.0.0.1", 0), handler)
    port = httpd.server_address[1]
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    return httpd, port


def render_frames(web_dir: Path, out_dir: Path, start_f: int = 0, end_f: int = None, step: int = 1, quality: float = 0.94, width: int = 1080, height: int = 1920):
    out_dir.mkdir(parents=True, exist_ok=True)
    httpd, port = start_server(web_dir)
    url = f"http://127.0.0.1:{port}/index.html"
    t0 = time.time()
    rendered = 0
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                args=[
                    "--use-angle=swiftshader",
                    "--enable-unsafe-swiftshader",
                    "--ignore-gpu-blocklist",
                    "--no-sandbox",
                ]
            )
            page = browser.new_page(viewport={"width": width, "height": height})
            errors = []
            page.on("pageerror", lambda err: errors.append(str(err)))
            page.on("console", lambda msg: print(f"[PAGE {msg.type}] {msg.text}") if msg.type == "error" else None)

            page.goto(url, wait_until="domcontentloaded")
            page.wait_for_function("() => window.ready || window.err", timeout=120000)

            page_err = page.evaluate("() => window.err")
            if page_err:
                raise RuntimeError(f"Page error during engine init: {page_err}")

            total = page.evaluate("() => window.TOTAL")
            if end_f is None or end_f >= total:
                end_f = total - 1

            print(f"[Renderer] Engine ready! TOTAL={total}, rendering {start_f}..{end_f} (step={step}) at {width}x{height}")

            for f in range(start_f, end_f + 1, step):
                frame_path = out_dir / f"f{f:04d}.jpg"
                data_url = page.evaluate(
                    "([f, q]) => { window.renderFrame(f); return document.getElementById('c').toDataURL('image/jpeg', q); }",
                    [f, quality],
                )
                b64 = data_url.split(",", 1)[1]
                frame_path.write_bytes(base64.b64decode(b64))
                rendered += 1
                if rendered % 60 == 0 or f == end_f:
                    elapsed = time.time() - t0
                    fps_r = rendered / max(elapsed, 0.01)
                    print(f"[Renderer] Frame {f}/{end_f} ({rendered} done, {fps_r:.2f} fps)")

            browser.close()
    finally:
        httpd.shutdown()

    elapsed = time.time() - t0
    print(f"[Renderer] Completed {rendered} frames in {elapsed:.1f}s ({elapsed / max(rendered, 1):.2f} s/frame)")
    return rendered


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--web", default=str(Path(__file__).parent / "web"))
    ap.add_argument("--out", required=True)
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--end", type=int, default=None)
    ap.add_argument("--step", type=int, default=1)
    ap.add_argument("--quality", type=float, default=0.94)
    ap.add_argument("--width", type=int, default=1080)
    ap.add_argument("--height", type=int, default=1920)
    args = ap.parse_args()
    render_frames(Path(args.web), Path(args.out), args.start, args.end, args.step, args.quality, args.width, args.height)
