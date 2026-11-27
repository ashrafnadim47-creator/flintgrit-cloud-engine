"""Automatic self-check of a rendered short (run after every render; stop as soon as it is clean).

Usage:  python qa.py <final.mp4> <out_qa_dir> [--mix mix.wav] [--stems <audio/stems dir>] [--words words.json] [--times 1.5,8,20]

Measures and checks (numbers in qa/thresholds.json):
- picture: size (1080x1920 or 1440x2560), 30 fps, black / white / long frozen spans, single-frame pops
- editing: hard cuts per 10 s (isolated spikes in frame difference), median shot length, cut clusters (long shorts)
- captions: centre height (70.6 % from the top) and visible outline width (about 8 px at 1080 wide)
- colour: FFmpeg signalstats over every frame of the mp4: YAVG (mean 8-bit luma of the video's Y plane,
  limited range 16-235) and SATAVG (mean 8-bit chroma saturation, sqrt(U^2 + V^2) around 128); hue spread
  per still, pure black
- soft focus or fast movement share of frames
- audio: integrated loudness (-14.5 LUFS), true peak (<= -1 dBTP), voice above music and sound effects (stems), long silences,
  A/V length and sync against mix.wav; first word time and long pauses from words.json
Writes qa_report.json, stills/*.jpg and contact.jpg. Exit code 0 always; read "ok" and "problems".
"""
import json
import re
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
TH = json.loads((HERE.parent / "qa" / "thresholds.json").read_text())


def run(args):
    return subprocess.run(args, capture_output=True)


def probe(mp4):
    r = run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height,r_frame_rate,duration:format=duration", "-of", "json", mp4])
    return json.loads(r.stdout)


def frames_small(mp4, w=135, h=240):
    """all frames, small, RGB uint8 (about 100 KB per frame)"""
    r = run(["ffmpeg", "-v", "error", "-i", mp4, "-vf", f"scale={w}:{h}:flags=area", "-pix_fmt", "rgb24", "-f", "rawvideo", "-"])
    return np.frombuffer(r.stdout, np.uint8).reshape(-1, h, w, 3)


def frames_every(mp4, step, w=540, h=960):
    """every `step`-th frame at analysis size, streamed"""
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", mp4, "-vf", f"select='not(mod(n\\,{step}))',scale={w}:{h}:flags=area", "-fps_mode", "passthrough",
                          "-pix_fmt", "rgb24", "-f", "rawvideo", "-"], stdout=subprocess.PIPE)
    n = w * h * 3
    while True:
        b = p.stdout.read(n)
        if len(b) < n:
            break
        yield np.frombuffer(b, np.uint8).reshape(h, w, 3)
    p.wait()


def signalstats(mp4):
    """mean YAVG and SATAVG over all frames (FFmpeg signalstats on the encoded video, 8-bit values)"""
    r = run(["ffmpeg", "-v", "error", "-i", mp4, "-vf", "signalstats,metadata=print:file=-", "-f", "null", "-"])
    t = r.stdout.decode(errors="ignore")
    y = [float(v) for v in re.findall(r"signalstats\.YAVG=([\d.]+)", t)]
    sa = [float(v) for v in re.findall(r"signalstats\.SATAVG=([\d.]+)", t)]
    return (float(np.mean(y)) if y else 0.0, float(np.mean(sa)) if sa else 0.0)


def caption_measure(rgb):
    """white text with a dark outline in the lower-middle band -> (centre from top, outline px at 1080 wide) or None"""
    from scipy import ndimage
    H, W = rgb.shape[:2]
    y0 = int(0.45 * H)
    band = rgb[y0:int(0.85 * H)].astype(np.int16)
    white = band.min(axis=2) > 232
    dark = band.max(axis=2) < 50
    m = white & ndimage.binary_dilation(dark, iterations=3)
    if m.sum() < 60:
        return None
    lab, n = ndimage.label(ndimage.binary_dilation(m, iterations=4))
    if n == 0:
        return None
    sizes = ndimage.sum(m, lab, range(1, n + 1)); k = int(np.argmax(sizes)) + 1
    if sizes[k - 1] < 60:
        return None
    region = lab == k
    letters = white & ndimage.binary_dilation(region, iterations=2)
    ys, _ = np.where(letters)
    # outline: grow the letters ring by ring and add up how dark each ring is (anti-aliased edges count
    # partly); the background level (median of the outer rings) is subtracted. Checked on renders with a
    # known outline: 5.5 px reads 4.7, 8 px reads 8.8.
    prev, fr = letters, []
    for r in range(1, 13):
        grown = ndimage.binary_dilation(letters, iterations=r)
        ring = grown & ~prev
        fr.append(float(dark[ring].mean()) if ring.any() else 0.0)
        prev = grown
    base = float(np.median(fr[-3:]))
    width = sum(max(0.0, f - base) for f in fr)
    return ((ys.min() + ys.max()) / 2 / H + y0 / H, width * 1080 / W)


def sharp_ratio(rgb):
    from scipy import ndimage
    f = rgb.astype(np.float32) / 255
    L = 0.2126 * f[..., 0] + 0.7152 * f[..., 1] + 0.0722 * f[..., 2]
    H = L.shape[0]
    mask = np.ones_like(L, bool); mask[int(0.55 * H):int(0.80 * H)] = False
    gf = ndimage.gaussian_filter(L, 0.7); gc = ndimage.gaussian_filter(L, 3.0)
    mf = np.hypot(ndimage.sobel(gf, 1), ndimage.sobel(gf, 0)); mc = np.hypot(ndimage.sobel(gc, 1), ndimage.sobel(gc, 0))
    ee = (mc > 0.06) & mask
    return float(np.median(mf[ee] / (mc[ee] + 1e-6))) if ee.any() else 2.0


def frame_rgb(mp4, t):
    r = run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", mp4, "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"])
    info = probe(mp4)["streams"]
    v = [s for s in info if s["codec_type"] == "video"][0]
    return np.frombuffer(r.stdout, np.uint8).reshape(v["height"], v["width"], 3)


def loudness(mp4):
    r = run(["ffmpeg", "-hide_banner", "-nostats", "-i", mp4, "-af", "ebur128=peak=true", "-f", "null", "-"])
    txt = r.stderr.decode(errors="ignore")
    summ = txt[txt.rfind("Summary:"):]
    I = re.search(r"I:\s+(-?[\d.]+) LUFS", summ)
    P = re.search(r"Peak:\s+(-?[\d.]+) dBFS", summ)
    return (float(I.group(1)) if I else None, float(P.group(1)) if P else None)


def silences(mp4, thr, dmin):
    r = run(["ffmpeg", "-hide_banner", "-i", mp4, "-af", f"silencedetect=noise={thr}dB:d={dmin}", "-f", "null", "-"])
    t = r.stderr.decode(errors="ignore")
    s = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", t)]
    e = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", t)]
    return list(zip(s, e + [None] * (len(s) - len(e))))


def audio_of(mp4, sr=8000):
    r = run(["ffmpeg", "-v", "error", "-i", mp4, "-ac", "1", "-ar", str(sr), "-f", "s16le", "-"])
    return np.frombuffer(r.stdout, np.int16).astype(np.float32) / 32768


def wav_mono(p, sr=8000):
    r = run(["ffmpeg", "-v", "error", "-i", str(p), "-ac", "1", "-ar", str(sr), "-f", "s16le", "-"])
    return np.frombuffer(r.stdout, np.int16).astype(np.float32) / 32768


def sync_ms(a, b, sr=8000, max_ms=300):
    n = min(len(a), len(b), sr * 20)
    a, b = a[:n] - a[:n].mean(), b[:n] - b[:n].mean()
    L = int(max_ms / 1000 * sr)
    best, lag = -1e9, 0
    for k in range(-L, L + 1, 4):
        v = np.dot(a[max(0, k):n + min(0, k)], b[max(0, -k):n - max(0, k)])
        if v > best:
            best, lag = v, k
    return lag / sr * 1000


def look_numbers(rgb, cap_band=None):
    a = rgb.astype(np.float32) / 255
    L = 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]
    m = np.ones_like(L, bool)
    H, W = L.shape
    if cap_band:
        m[int(cap_band[0] * H):int(cap_band[1] * H), :] = False
    c = int(min(H, W) * 0.18)
    corners = np.mean([L[:c, :c].mean(), L[:c, -c:].mean(), L[-c:, :c].mean(), L[-c:, -c:].mean()])
    centre = L[H // 2 - c // 2:H // 2 + c // 2, W // 2 - c // 2:W // 2 + c // 2].mean()
    pure_black = ((a.max(axis=2) < 0.02) & m).mean()
    mx, mn = a.max(axis=2), a.min(axis=2)
    sat = np.where(mx > 1e-3, (mx - mn) / (mx + 1e-6), 0)
    hue = np.arctan2(np.sqrt(3) * (a[..., 1] - a[..., 2]), 2 * a[..., 0] - a[..., 1] - a[..., 2])
    sm = (sat > 0.25) & m & (mx > 0.15)
    hue_spread = float(1 - abs(np.mean(np.exp(1j * hue[sm])))) if sm.sum() > 100 else 0.0
    return {"median_luma": round(float(np.median(L[m])), 3), "p1_luma": round(float(np.percentile(L[m], 1)), 3),
            "pure_black_fraction": round(float(pure_black), 5), "corner_to_centre": round(float(corners / max(centre, 1e-3)), 2),
            "saturation": round(float(sat[m].mean()), 3), "hue_spread": round(hue_spread, 3)}


def main():
    args = sys.argv[1:]
    if len(args) < 2:
        raise SystemExit(__doc__)
    mp4, out = args[0], Path(args[1])
    opt = {args[i]: args[i + 1] for i in range(2, len(args) - 1, 2)}
    out.mkdir(parents=True, exist_ok=True); (out / "stills").mkdir(exist_ok=True)
    problems, rep = [], {}
    info = probe(mp4)
    vs = [s for s in info["streams"] if s["codec_type"] == "video"]
    au = [s for s in info["streams"] if s["codec_type"] == "audio"]
    dur = float(info["format"]["duration"])
    rep["video"] = {"width": vs[0]["width"], "height": vs[0]["height"], "fps": vs[0]["r_frame_rate"], "seconds": round(dur, 3)}
    if vs[0]["r_frame_rate"] != "30/1":
        problems.append(f"frame rate is {vs[0]['r_frame_rate']}, expected 30/1")
    if not au:
        problems.append("no audio stream in the mp4")
    if [vs[0]["width"], vs[0]["height"]] not in TH["sizes_allowed"]:
        problems.append(f"size {vs[0]['width']}x{vs[0]['height']} is not 1080x1920 or 1440x2560")
    if not (TH["duration_min_s"] <= dur <= TH["duration_max_s"]):
        problems.append(f"duration {dur:.1f} s is outside {TH['duration_min_s']}-{TH['duration_max_s']} s")
    if au:
        ad = float(au[0].get("duration") or dur); vd = float(vs[0].get("duration") or dur)
        rep["av_duration_gap_s"] = round(abs(ad - vd), 3)
        if abs(ad - vd) > 0.1:
            problems.append(f"audio and video lengths differ by {abs(ad - vd):.2f} s")

    # ---- frames ----
    RGB = frames_small(mp4)
    F = (0.2126 * RGB[..., 0] + 0.7152 * RGB[..., 1] + 0.0722 * RGB[..., 2]).astype(np.float32) / 255.0
    means = F.mean(axis=(1, 2))
    diffs = np.abs(np.diff(F, axis=0)).mean(axis=(1, 2))
    fps = TH["fps"]
    black = np.where(means < TH["black_luma_max"])[0].tolist()
    white = np.where(means > TH["white_luma_min"])[0].tolist()
    frozen, run_start = [], None
    for i, d in enumerate(np.append(diffs, 1.0)):
        if d < TH["frozen_diff_max"]:
            run_start = i if run_start is None else run_start
        else:
            if run_start is not None and i - run_start + 1 >= TH["frozen_min_frames"]:
                frozen.append([run_start, i])
            run_start = None
    pops = []
    for i in range(1, len(F) - 1):
        both = np.abs(F[i - 1] - F[i + 1]).mean()
        if diffs[i - 1] > TH["pop_jump_min"] and diffs[i] > TH["pop_jump_min"] and both < TH["pop_neighbour_max"]:
            pops.append(i)
    # hard cuts: isolated spikes in frame difference (merged when closer than 3 frames)
    d = np.concatenate([[0.0], diffs])
    raw = [i for i in range(1, len(d) - 1) if d[i] > 0.10 and d[i] > 1.8 * max(d[i - 1], d[i + 1], 1e-4)]
    cuts = []
    for c in raw:
        if not cuts or c - cuts[-1] >= 3:
            cuts.append(c)
    bounds = [0] + cuts + [len(F)]
    shots = [(b - a) / fps for a, b in zip(bounds[:-1], bounds[1:])]
    med_shot = float(np.median(shots)) if shots else 0.0
    rep["frames"] = {"count": int(len(F)), "black": black[:20], "white": white[:20], "frozen_spans": frozen, "pops": pops[:20]}
    rep["editing"] = {"cuts": len(cuts), "cut_times_s": [round(c / fps, 2) for c in cuts], "shots": len(shots),
                      "median_shot_s": round(med_shot, 2), "shots_under_1s": sum(1 for x in shots if x < 1.0), "holds_over_5s": sum(1 for x in shots if x >= 5.0),
                      "shot_lengths_s": [round(x, 2) for x in shots]}
    if black: problems.append(f"{len(black)} black frames (first at frame {black[0]})")
    if len(white) > TH["white_allowed_frames"]: problems.append(f"{len(white)} white frames (first at frame {white[0]}; flash wipes explain at most a few)")
    for a_, b_ in frozen: problems.append(f"picture completely still for frames {a_}-{b_} ({(b_ - a_ + 1) / fps:.1f} s)")
    for p in pops[:10]: problems.append(f"single-frame pop at frame {p}")
    per10 = len(cuts) / max(dur, 1e-6) * 10
    rep["editing"]["hard_cuts_per_10s"] = round(per10, 2)
    if not (TH["hard_cuts_per_10s_min"] <= per10 <= TH["hard_cuts_per_10s_max"]): problems.append(f"{len(cuts)} hard cuts = {per10:.1f} per 10 s (rule {TH['hard_cuts_per_10s_min']}-{TH['hard_cuts_per_10s_max']}; nearby places are reached with a camera glide)")
    if not (TH["shot_median_min_s"] <= med_shot <= TH["shot_median_max_s"]): problems.append(f"median shot {med_shot:.2f} s (rule {TH['shot_median_min_s']}-{TH['shot_median_max_s']} s)")
    if dur >= TH["cluster_check_min_duration_s"] and rep["editing"]["shots_under_1s"] < 3: problems.append("no cluster of quick cuts (rule for long shorts: 3-4 shots of 0.4-1.0 s in a row at least once)")

    # colour over all frames: FFmpeg signalstats YAVG / SATAVG (the same method the targets were measured with)
    yavg, satavg = signalstats(mp4)
    sub = RGB[::3].astype(np.float32) / 255.0
    mx, mn = sub.max(axis=3), sub.min(axis=3)
    hsv_sat = float(np.where(mx > 1e-3, (mx - mn) / (mx + 1e-6), 0).mean() * 100)
    rep["colour"] = {"brightness_yavg": round(yavg, 1), "saturation_satavg": round(satavg, 1),
                     "info_hsv_saturation_pct": round(hsv_sat, 1),
                     "note": "YAVG/SATAVG = FFmpeg signalstats, 8-bit; HSV saturation is shown for information only (about 2.3x SATAVG on these videos)"}
    if not (TH["brightness_yavg_min"] <= yavg <= TH["brightness_yavg_max"]): problems.append(f"mean brightness YAVG {yavg:.0f} (rule {TH['brightness_yavg_min']}-{TH['brightness_yavg_max']}, FFmpeg signalstats)")
    if not (TH["saturation_satavg_min"] <= satavg <= TH["saturation_satavg_max"]): problems.append(f"mean saturation SATAVG {satavg:.0f} (rule {TH['saturation_satavg_min']}-{TH['saturation_satavg_max']}, FFmpeg signalstats)")
    del RGB, sub

    # captions and soft focus on every 6th frame at analysis size
    caps, soft = [], []
    cutset = set(cuts)
    for k, rgb in enumerate(frames_every(mp4, 6)):
        fi = k * 6
        c = caption_measure(rgb)
        if c:
            caps.append(c)
        fast = fi > 0 and fi < len(diffs) and diffs[fi - 1] > 0.035 and fi not in cutset and (fi - 1) not in cutset
        soft.append(sharp_ratio(rgb) < 1.02 or fast)
    if caps:
        cy = float(np.median([c[0] for c in caps])); ow = float(np.median([c[1] for c in caps]))
        rep["captions"] = {"frames_with_caption": len(caps), "centre_from_top": round(cy, 3), "outline_px_1080": round(ow, 1)}
        if abs(cy - TH["caption_centre_from_top"]) > TH["caption_centre_tolerance"]: problems.append(f"captions centred at {cy * 100:.1f} % from the top (rule {TH['caption_centre_from_top'] * 100:.1f} %)")
        if not (TH["caption_outline_min_px"] <= ow <= TH["caption_outline_max_px"]): problems.append(f"caption outline about {ow:.0f} px (rule about 8 px at 1080 wide)")
    else:
        rep["captions"] = {"frames_with_caption": 0}
    sf = float(np.mean(soft)) if soft else 0.0
    rep["soft_or_fast_share"] = round(sf, 3)
    if not (TH["soft_or_fast_share_min"] <= sf <= TH["soft_or_fast_share_max"]): problems.append(f"soft focus or fast movement in {sf * 100:.0f} % of frames (rule about 15-67 %, estimate)")

    # ---- audio ----
    if au:
        I, TP = loudness(mp4)
        rep["audio"] = {"integrated_lufs": I, "true_peak_dbtp": TP}
        if I is None or not (TH["lufs_min"] <= I <= TH["lufs_max"]): problems.append(f"loudness {I} LUFS (target {TH['lufs_target']}, window {TH['lufs_min']}..{TH['lufs_max']})")
        if TP is None or TP > TH["true_peak_max_dbtp"]: problems.append(f"true peak {TP} dBTP above {TH['true_peak_max_dbtp']}")
        sil = [(s, e) for s, e in silences(mp4, TH["audio_silence_db"], TH["audio_silence_max_s"]) if s < dur - 0.6]
        rep["audio"]["long_silences"] = sil
        for s, e in sil: problems.append(f"silence from {s:.2f} s to {e} s")
        if "--mix" in opt:
            lag = sync_ms(audio_of(mp4), wav_mono(opt["--mix"]))
            rep["audio"]["sync_offset_ms"] = round(lag, 1)
            if abs(lag) > TH["sync_max_ms"]: problems.append(f"audio is offset by {lag:.0f} ms against mix.wav")
    if "--stems" in opt:
        st = Path(opt["--stems"])
        v, m = wav_mono(st / "voice.wav", 16000), wav_mono(st / "music.wav", 16000)
        n = min(len(v), len(m)); v, m = v[:n], m[:n]
        win, hop = 6400, 800
        idx = np.arange(0, max(1, n - win), hop)
        cv = np.concatenate([[0.0], np.cumsum(v.astype(np.float64) ** 2)]); cm = np.concatenate([[0.0], np.cumsum(m.astype(np.float64) ** 2)])
        vd = 10 * np.log10((cv[idx + win] - cv[idx]) / win + 1e-12); md = 10 * np.log10((cm[idx + win] - cm[idx]) / win + 1e-12)
        speaking = vd > np.percentile(vd, 90) - 25
        margin = (vd - md)[speaking]
        share = float(np.mean(margin >= TH["voice_over_music_min_db"])) if margin.size else 1.0
        rep["voice_over_music"] = {"median_db": round(float(np.median(margin)), 1) if margin.size else None, "share_at_least_6db": round(share, 3)}
        if share < TH["voice_over_music_share_min"]: problems.append(f"music comes within {TH['voice_over_music_min_db']} dB of the voice in {100 - share * 100:.0f} % of speech (voice must stay on top)")
    if "--stems" in opt and (Path(opt["--stems"]) / "sfx.wav").exists():
        st = Path(opt["--stems"])
        v, fx_ = wav_mono(st / "voice.wav", 16000), wav_mono(st / "sfx.wav", 16000)
        if np.any(np.abs(fx_) > 1e-4):
            vpk = float(np.abs(v).max()); fpk = float(np.abs(fx_).max())
            n = min(len(v), len(fx_)); vr = float(np.sqrt(np.mean(v[:n].astype(np.float64) ** 2) + 1e-12)); fr = float(np.sqrt(np.mean(fx_[:n].astype(np.float64) ** 2) + 1e-12))
            under = 20 * np.log10(vr / fr)
            rep["sfx"] = {"peak_vs_voice_peak": round(fpk / max(vpk, 1e-9), 3), "rms_under_voice_db": round(float(under), 1)}
            if fpk / max(vpk, 1e-9) > TH["sfx_peak_vs_voice_peak_max"]: problems.append(f"sound effect peaks reach {fpk / vpk:.2f} x the voice peak (rule at most {TH['sfx_peak_vs_voice_peak_max']})")
            if under < TH["sfx_under_voice_min_db"]: problems.append(f"sound effects are only {under:.1f} dB under the voice (rule at least {TH['sfx_under_voice_min_db']} dB)")
    if "--words" in opt:
        w = json.loads(Path(opt["--words"]).read_text())
        gaps = [w[i + 1]["start"] - w[i]["end"] for i in range(len(w) - 1)]
        long_p = [g for g in gaps if g > 0.30]
        speech = w[-1]["end"] - w[0]["start"] if w else 0
        rep["speech"] = {"words": len(w), "words_per_second": round(len(w) / speech, 2) if speech else None, "first_word_s": w[0]["start"] if w else None,
                         "pauses_over_0.3s": len(long_p), "longest_pause_s": round(max(gaps), 2) if gaps else 0}
        if w and w[0]["start"] > TH["first_word_max_s"]: problems.append(f"voice starts late ({w[0]['start']:.2f} s)")
        if len(long_p) > TH["long_pauses_max"]: problems.append(f"{len(long_p)} pauses longer than 0.3 s (rule: at most {TH['long_pauses_max']} dramatic pauses)")
        if gaps and max(gaps) > TH["pause_max_s"]: problems.append(f"a pause of {max(gaps):.2f} s")
        if w and dur - w[-1]["end"] > 0.8: problems.append(f"video runs {dur - w[-1]['end']:.2f} s past the last word")

    # ---- stills for the visual self-check ----
    times = sorted(set([round(x, 2) for x in np.linspace(0.5, dur - 0.5, 16)] + [float(x) for x in opt.get("--times", "").split(",") if x]))
    looks, thumbs = [], []
    for t in times:
        rgb = frame_rgb(mp4, t)
        Image.fromarray(rgb).resize((rgb.shape[1] // 2, rgb.shape[0] // 2)).save(out / "stills" / f"t{t:06.2f}.jpg", quality=86)
        n = look_numbers(rgb, cap_band=(0.50, 0.80)); n["t"] = t; looks.append(n)  # both caption positions masked
        thumbs.append(Image.fromarray(rgb).resize((180, 320)))
    rep["look"] = looks
    for n in looks:
        if n["pure_black_fraction"] > TH["pure_black_fraction_max"]:
            problems.append(f"pure black pixels at {n['t']} s ({n['pure_black_fraction'] * 100:.2f} %)")
        if n["hue_spread"] > TH["hue_spread_median_max"] + 0.12:
            problems.append(f"too many unrelated colours at {n['t']} s (hue spread {n['hue_spread']}; one dominant colour + one accent per scene)")
    med = lambda k: float(np.median([n[k] for n in looks]))
    rep["look_median"] = {k: round(med(k), 3) for k in ("median_luma", "p1_luma", "saturation", "hue_spread", "corner_to_centre")}
    if med("hue_spread") > TH["hue_spread_median_max"]: problems.append(f"palette too spread: median hue spread {med('hue_spread'):.2f} (max {TH['hue_spread_median_max']})")
    cols = 8; rows = (len(thumbs) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * 180, rows * 320), (20, 18, 28))
    for i, im in enumerate(thumbs):
        sheet.paste(im, ((i % cols) * 180, (i // cols) * 320))
    sheet.save(out / "contact.jpg", quality=85)
    rep["problems"] = problems
    rep["ok"] = not problems
    (out / "qa_report.json").write_text(json.dumps(rep, indent=1))
    print(json.dumps({"ok": rep["ok"], "problems": problems, "report": str(out / "qa_report.json"), "contact": str(out / "contact.jpg")}, indent=1))


if __name__ == "__main__":
    main()
