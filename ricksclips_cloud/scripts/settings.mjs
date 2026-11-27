#!/usr/bin/env node
// Read or change the user's settings file (<work>/settings.json). Keys:
//   quality: "2k" | "1080p"           2k = 1440x2560 (default). Render falls back to 1080p by itself when the machine cannot do 2K.
//   captions: true | false            caption_lowercase: true | false
//   ink_px: outline width of characters, props and animals in pixels at 1080 wide (default 8, 2-16)
//   whisper_model: "turbo" | "small.en" (set by setup from the machine's memory)      work_folder: set by setup
// Usage: node settings.mjs get [--work <folder>]
//        node settings.mjs set <key> <value> [--work <folder>]
//        node settings.mjs next-short [--work <folder>]   (prints the next free short-N folder)
import fs from "node:fs";
import path from "node:path";
import { workFolder } from "./lib/work.mjs";

const argv = process.argv.slice(2);
const WORK = workFolder(argv);
const FILE = path.join(WORK, "settings.json");
const bool = (v) => v === "true" ? true : v === "false" ? false : null;
const ALLOWED = {
  quality: (v) => ["1080p", "2k"].includes(v) ? v : null,
  captions: bool,
  caption_lowercase: bool,
  ink_px: (v) => { const n = Number(v); return Number.isFinite(n) && n >= 2 && n <= 16 ? n : null; },
  whisper_model: (v) => ["turbo", "small.en"].includes(v) ? v : null,
};
const DEFAULTS = { quality: "2k", captions: true, caption_lowercase: false, ink_px: 8, whisper_model: "turbo", work_folder: WORK };
const read = () => ({ ...DEFAULTS, ...JSON.parse(fs.readFileSync(FILE, "utf8")) });
const [cmd, key, value] = argv;
if (!fs.existsSync(FILE)) { console.error(`No settings file at ${FILE}. Setup has not run yet.`); process.exit(1); }
if (cmd === "get") console.log(JSON.stringify(read(), null, 2));
else if (cmd === "set") {
  if (!(key in ALLOWED)) { console.error(`Unknown setting "${key}". Allowed: ${Object.keys(ALLOWED).join(", ")}`); process.exit(1); }
  const v = ALLOWED[key](value);
  if (v === null) { console.error(`Bad value "${value}" for ${key}`); process.exit(1); }
  const s = read(); s[key] = v;
  fs.writeFileSync(FILE, JSON.stringify(s, null, 2));
  console.log(JSON.stringify(s, null, 2));
} else if (cmd === "next-short") {
  let n = 1; while (fs.existsSync(path.join(WORK, `short-${n}`))) n++;
  console.log(JSON.stringify({ next: n, folder: path.join(WORK, `short-${n}`) }));
} else { console.error("usage: node settings.mjs get | set <key> <value> | next-short"); process.exit(1); }
