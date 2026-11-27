// Where the user's work folder is. Order: --work <folder>, the RICKSCLIPS_WORK environment variable,
// the one-line pointer file ~/.ricksclips-work (written by setup only when the user picked another folder),
// then the default ~/RicksClips.
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

export const POINTER = path.join(os.homedir(), ".ricksclips-work");
export const DEFAULT_WORK = path.join(os.homedir(), "RicksClips");
export function workFolder(argv = process.argv.slice(2)) {
  const i = argv.indexOf("--work");
  if (i >= 0 && argv[i + 1]) return path.resolve(argv[i + 1]);
  if (process.env.RICKSCLIPS_WORK) return path.resolve(process.env.RICKSCLIPS_WORK);
  try { const p = fs.readFileSync(POINTER, "utf8").trim(); if (p) return path.resolve(p); } catch { /* no pointer */ }
  return DEFAULT_WORK;
}
export const venvPython = (engine) => process.platform === "win32" ? path.join(engine, ".venv", "Scripts", "python.exe") : path.join(engine, ".venv", "bin", "python");
// A browser the user already has (or a path set for testing) can replace the one Remotion downloads.
export const browserOverride = () => {
  if (process.env.RICKSCLIPS_BROWSER && fs.existsSync(process.env.RICKSCLIPS_BROWSER)) {
    return process.env.RICKSCLIPS_BROWSER;
  }
  const candidates = [
    "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
    "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
    "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
    "C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium-browser",
    "/usr/bin/chromium"
  ];
  for (const c of candidates) {
    if (fs.existsSync(c)) return c;
  }
  return null;
};
