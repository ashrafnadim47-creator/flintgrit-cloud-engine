#!/usr/bin/env node
// Word timestamps for the voice with OpenAI Whisper (turbo, or the small English model on small machines).
//   node transcribe.mjs <voice.wav> <out transcript.json> [--work <folder>]
// The output is a plain word list; fix_words.py joins sub-word pieces and respells it to the script.
import { spawnSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { workFolder, venvPython } from "./lib/work.mjs";
import { TURBO, SMALL } from "./lib/pins.mjs";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const argv = process.argv.slice(2);
const [wav, out] = argv;
const fail = (m) => { console.error(JSON.stringify({ ok: false, error: m })); process.exit(1); };
if (!wav || !out) fail("usage: node transcribe.mjs <voice.wav> <out transcript.json>");
const WORK = workFolder(argv), ENGINE = path.join(WORK, ".engine");
let settings = {}; try { settings = JSON.parse(fs.readFileSync(path.join(WORK, "settings.json"), "utf8")); } catch { /* defaults */ }
const model = settings.whisper_model || TURBO.name;
const dir = path.join(ENGINE, "models", model === TURBO.name ? TURBO.dir : SMALL.dir);
const vpy = venvPython(ENGINE);
if (!fs.existsSync(path.join(dir, "model.bin"))) fail(`The speech model is not installed (${dir}). Setup has to finish first.`);
const r = spawnSync(vpy, [path.join(HERE, "whisper_words.py"), wav, dir, out], { encoding: "utf8", timeout: 45 * 60000, maxBuffer: 64 * 2 ** 20 });
if (r.status !== 0 || !fs.existsSync(out)) fail("Speech recognition failed: " + ((r.stderr || "") + (r.stdout || "")).slice(-600));
const words = JSON.parse(fs.readFileSync(out, "utf8"));
if (!words.length) fail("No words were recognised. Check that the voice file contains speech.");
console.log(JSON.stringify({ ok: true, engine: "whisper-" + model, words: words.length, out }));
