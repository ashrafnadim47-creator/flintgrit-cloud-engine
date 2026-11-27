#!/usr/bin/env node
// Renders one short with Remotion, with the right settings for this machine.
//   node render.mjs video  <shortDir> [--work <folder>] [--out <file.mp4>] [--draft] [--frames 0-90]
//   node render.mjs stills <shortDir> --at 1.5,8,20 [--out <dir>]      (single frames for the look check)
// 2K is the default. When the machine cannot do 2K (not enough memory, no graphics acceleration, a failed
// 2K test frame, or a 2K render that fails) the project is switched to 1080p by itself, without asking.
// Workers follow the memory and cores. Prints JSON: seconds, quality used, GPU or software, output path, engine lines.
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { workFolder, browserOverride } from "./lib/work.mjs";
import { engineRequire, bundleOverride, probeWebGL, decideQuality, browserStatus } from "./lib/browser.mjs";

const argv = process.argv.slice(2);
const mode = argv[0];
const arg = (n, d) => { const i = argv.indexOf(n); return i >= 0 ? argv[i + 1] : d; };
const shortDir = path.resolve(argv[1] || ".");
const WORK = workFolder(argv);
const ENGINE = fs.existsSync(path.join(WORK, ".engine")) ? path.join(WORK, ".engine") : WORK;
const proj = path.join(shortDir, "project");
const SIZES = { "1080p": [1080, 1920], "2k": [1440, 2560] };
// Remotion and the browser console are very chatty; only our own JSON goes to the output.
const print = (s) => process.stdout.write(s + "\n");
const fail = (m, extra = {}) => { process.stderr.write(JSON.stringify({ ok: false, error: m, ...extra }) + "\n"); process.exit(1); };
console.log = console.info = console.warn = console.error = () => {};
if (!["video", "stills"].includes(mode)) fail("usage: node render.mjs video|stills <shortDir> ...");
if (!fs.existsSync(path.join(ENGINE, "node_modules", "@remotion", "renderer"))) fail("Remotion is not installed. Setup has to finish first.");
if (!fs.existsSync(path.join(proj, "src", "index.jsx"))) fail("No project at " + proj);
const metaFile = path.join(proj, "src", "project.json");
const meta = () => JSON.parse(fs.readFileSync(metaFile, "utf8"));
const setQuality = (q) => { const m = meta(); [m.W, m.H] = SIZES[q]; m.quality = q; fs.writeFileSync(metaFile, JSON.stringify(m, null, 2)); };

const st = fs.statfsSync(shortDir);
const freeGb = (st.bavail * st.bsize) / 2 ** 30;
if (freeGb < 3) fail(`Only ${freeGb.toFixed(1)} GB free on disk; rendering needs at least 3 GB. Free some space.`);

process.chdir(ENGINE); // the bundler writes its cache under the current folder: keep it in the work folder, never in the plugin
const req = engineRequire(ENGINE);
const { bundle } = req("@remotion/bundler");
const R = req("@remotion/renderer");
const browserExecutable = browserOverride() || undefined;

// machine profile: probed once, then reused while the machine looks the same
const PROFILE = path.join(WORK, "render-profile.json");
const fingerprint = `${os.platform()}-${os.arch()}-${Math.round(os.totalmem() / 2 ** 30)}gb-${os.cpus().length}c`;
async function profile() {
  try { const p = JSON.parse(fs.readFileSync(PROFILE, "utf8")); if (p.fingerprint === fingerprint && p.probe && !p.probe.error) return p; } catch { /* probe again */ }
  const bs = await browserStatus(ENGINE);
  if (!bs.ok) fail("The render browser is not installed. Setup has to finish first.");
  const probe = await probeWebGL(ENGINE);
  const p = { fingerprint, probe, at: new Date().toISOString() };
  fs.writeFileSync(PROFILE, JSON.stringify(p, null, 2));
  return p;
}
const machine = () => ({ ram_gb: +(os.totalmem() / 2 ** 30).toFixed(1), ram_free_gb: +(os.freemem() / 2 ** 30).toFixed(1) });
const workers = () => Math.max(1, Math.min(4, Math.floor(Math.min(os.freemem() / 2 ** 30 / 3, os.cpus().length / 2))));

const prof = await profile();
let gl = prof.probe.gl || "angle";
let wanted = meta().quality || "2k";
const decision = decideQuality(wanted, machine(), prof.probe);
let notes = [];
if (decision.quality !== wanted) { setQuality(decision.quality); notes.push(`Rendering at 1080p instead of 2K: ${decision.reason}.`); wanted = decision.quality; }

const engineLines = new Set();
const onBrowserLog = (l) => { if (l.text && l.text.startsWith("[rc]")) engineLines.add(l.text.slice(0, 300)); };
const common = () => ({
  browserExecutable,
  chromiumOptions: {
    gl,
    args: ["--no-sandbox", "--disable-gpu-sandbox", "--disable-dev-shm-usage"]
  },
  logLevel: "error",
  timeoutInMilliseconds: 900000,
  onBrowserLog
});
async function prepare() {
  const serveUrl = await bundle({ entryPoint: path.join(proj, "src", "index.jsx"), publicDir: path.join(proj, "public"), webpackOverride: bundleOverride(ENGINE), outDir: path.join(shortDir, ".bundle") });
  const composition = await R.selectComposition({ serveUrl, id: "main", ...common() });
  return { serveUrl, composition };
}

async function doStills() {
  const times = String(arg("--at", "0")).split(",").map(Number).filter((x) => Number.isFinite(x));
  const outDir = path.resolve(arg("--out", path.join(shortDir, "qa", "stills")));
  fs.mkdirSync(outDir, { recursive: true });
  const { serveUrl, composition } = await prepare();
  const files = [];
  for (const t of times) {
    const frame = Math.min(composition.durationInFrames - 1, Math.max(0, Math.round(t * 30)));
    const file = path.join(outDir, `t${t.toFixed(2).padStart(6, "0")}.jpg`);
    await R.renderStill({ serveUrl, composition, frame, output: file, imageFormat: "jpeg", jpegQuality: 92, ...common() });
    files.push(file);
  }
  return { files };
}

async function doVideo() {
  const draft = argv.includes("--draft");
  const out = path.resolve(arg("--out", path.join(shortDir, draft ? "draft.mp4" : "final.mp4")));
  const range = arg("--frames", null);
  const { serveUrl, composition } = await prepare();
  let frameRange = null;
  if (range) { const [a, b] = range.split("-").map(Number); frameRange = [a, Math.min(b, composition.durationInFrames - 1)]; }
  let last = -1;
  await R.renderMedia({
    serveUrl, composition, codec: "h264", outputLocation: out, frameRange,
    imageFormat: "jpeg", jpegQuality: 85, crf: 20, pixelFormat: "yuv420p", colorSpace: "bt709",
    audioCodec: "aac", audioBitrate: "192k", x264Preset: "ultrafast",
    concurrency: Math.min(2, os.cpus().length || 1), muted: false, ...common(),
    onProgress: ({ progress }) => { const p = Math.floor(progress * 10); if (p !== last) { last = p; process.stderr.write(`render ${p * 10} %\n`); } },
  });
  return { files: [out] };
}

const t0 = Date.now();
let result;
try { result = mode === "stills" ? await doStills() : await doVideo(); }
catch (e) {
  if (wanted === "2k") {
    // a failed 2K render (usually memory) falls back to 1080p once, by itself
    notes.push(`2K render failed (${String(e.message || e).split("\n")[0].slice(0, 160)}). Retrying at 1080p.`);
    setQuality("1080p"); wanted = "1080p";
    try { result = mode === "stills" ? await doStills() : await doVideo(); }
    catch (e2) { fail("Render failed: " + String(e2.message || e2).slice(0, 800), { notes }); }
  } else fail("Render failed: " + String(e.message || e).slice(0, 800), { notes });
}
const secs = (Date.now() - t0) / 1000;
const m = meta();
print(JSON.stringify({ ok: true, mode, files: result.files, seconds: +secs.toFixed(1), width: m.W, height: m.H, quality: wanted, webgl: prof.probe.hardware ? "gpu" : "software", gpu: prof.probe.renderer, workers: workers(),
  notes, engine_lines: [...engineLines].slice(0, 80) }, null, 2));
try { fs.rmSync(path.join(shortDir, ".bundle"), { recursive: true, force: true }); } catch { /* temp */ }
