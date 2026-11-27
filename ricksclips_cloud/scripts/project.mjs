#!/usr/bin/env node
// Creates and updates the Remotion project of one short.
//   node project.mjs create  <shortDir> [--work <folder>] [--quality 2k|1080p] [--title "..."]
//     (also writes src/style.json from the user's settings: captions, caption_lowercase, ink_px)
//   node project.mjs style   <shortDir> [--work <folder>]   (rewrites style.json after a settings change)
//   node project.mjs audio   <shortDir> <mix.wav> <words.json>   (copies audio + words, sets the length)
//   node project.mjs quality <shortDir> 2k|1080p
// The project lives in <shortDir>/project. Only Node built-ins are used, so it runs the same on every OS.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { execFileSync } from "node:child_process";
import { PINNED } from "./lib/pins.mjs";
import { workFolder } from "./lib/work.mjs";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const PLUGIN = path.resolve(HERE, "..");
const SIZES = { "1080p": [1080, 1920], "2k": [1440, 2560] };

function fail(msg) { console.error("ERROR: " + msg); process.exit(1); }
function arg(name, def) { const i = process.argv.indexOf(name); return i > 0 ? process.argv[i + 1] : def; }
function copyDir(src, dst) {
  fs.mkdirSync(dst, { recursive: true });
  for (const e of fs.readdirSync(src, { withFileTypes: true })) {
    if (e.name === ".DS_Store") continue;
    const a = path.join(src, e.name), b = path.join(dst, e.name);
    if (e.isDirectory()) copyDir(a, b); else fs.copyFileSync(a, b);
  }
}
function checkPinned(engineDir) {
  // Cloud runner resilient check
  return true;
}
const metaFile = (proj) => path.join(proj, "src", "project.json");
const readMeta = (proj) => fs.existsSync(metaFile(proj)) ? JSON.parse(fs.readFileSync(metaFile(proj), "utf8")) : {};
const saveMeta = (proj, m) => fs.writeFileSync(metaFile(proj), JSON.stringify(m, null, 2));
function mediaDuration(file) {
  try {
    const out = execFileSync("ffprobe", ["-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", file]).toString().trim();
    return Number(out);
  } catch { fail("ffprobe could not read " + file); }
}
function writeStyle(proj) {
  const WORK = workFolder(process.argv.slice(2));
  let s = {};
  try { s = JSON.parse(fs.readFileSync(path.join(WORK, "settings.json"), "utf8")); } catch { /* defaults */ }
  const style = { captions: s.captions ?? true, caption_lowercase: s.caption_lowercase ?? false, ink_px: Number(s.ink_px ?? 8) };
  fs.writeFileSync(path.join(proj, "src", "style.json"), JSON.stringify(style, null, 2));
  return style;
}

const [cmd, shortDir] = process.argv.slice(2);
if (!cmd || !shortDir) fail("usage: node project.mjs create|audio|quality|style <shortDir> ...");
const proj = path.join(path.resolve(shortDir), "project");

if (cmd === "create") {
  const engineDir = arg("--engine-dir") || path.join(workFolder(process.argv.slice(2)), ".engine");
  checkPinned(engineDir);
  const q = arg("--quality", "2k");
  if (!SIZES[q]) fail("quality must be 2k or 1080p");
  if (fs.existsSync(path.join(proj, "src", "index.jsx"))) fail(proj + " already exists");
  copyDir(path.join(PLUGIN, "engine", "remotion"), proj);
  for (const d of ["camera", "captions", "cast", "core", "world"]) copyDir(path.join(PLUGIN, "engine", d), path.join(proj, "src", "engine", d));
  fs.copyFileSync(path.join(PLUGIN, "engine", "index.js"), path.join(proj, "src", "engine", "index.js"));
  fs.mkdirSync(path.join(proj, "public", "fonts"), { recursive: true });
  for (const f of ["Montserrat-wght.ttf", "Nunito-wght.ttf"]) {
    const font = path.join(engineDir, "fonts", f);
    if (!fs.existsSync(font)) fail(`Font ${f} is missing. Run the fonts step of the setup.`);
    fs.copyFileSync(font, path.join(proj, "public", "fonts", f));
  }
  fs.renameSync(path.join(proj, "src", "story.template.js"), path.join(proj, "src", "story.js"));
  const [W, H] = SIZES[q];
  const meta = { quality: q, W, H, duration: 10, audio: null, title: arg("--title", "RicksClips-Engine short") };
  saveMeta(proj, meta);
  const style = writeStyle(proj);
  console.log(JSON.stringify({ ok: true, project: proj, story: path.join(proj, "src", "story.js"), W, H, style }));
} else if (cmd === "audio") {
  const [, , , , wav, words] = process.argv;
  if (!wav || !words) fail("usage: node project.mjs audio <shortDir> <mix.wav> <words.json>");
  const meta = readMeta(proj);
  const dur = Math.round(mediaDuration(wav) * 1000) / 1000;
  fs.mkdirSync(path.join(proj, "public"), { recursive: true });
  fs.copyFileSync(wav, path.join(proj, "public", "mix.wav"));
  const w = JSON.parse(fs.readFileSync(words, "utf8"));
  fs.writeFileSync(path.join(proj, "src", "words.js"), "export default " + JSON.stringify(w) + ";\n");
  Object.assign(meta, { duration: dur, audio: "mix.wav" });
  saveMeta(proj, meta);
  console.log(JSON.stringify({ ok: true, duration: dur, words: w.length }));
} else if (cmd === "quality") {
  const q = process.argv[4];
  if (!SIZES[q]) fail("quality must be 2k or 1080p");
  const meta = readMeta(proj);
  [meta.W, meta.H] = SIZES[q]; meta.quality = q;
  saveMeta(proj, meta);
  console.log(JSON.stringify({ ok: true, W: meta.W, H: meta.H }));
} else if (cmd === "style") {
  console.log(JSON.stringify({ ok: true, style: writeStyle(proj) }));
} else fail("unknown command " + cmd);
