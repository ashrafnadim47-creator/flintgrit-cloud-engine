#!/usr/bin/env node
// Sets up the RicksClips-Engine work folder. Run only after the user approved the install list.
//   node init-workspace.mjs <step> [--work <folder>] [--python <python command>]
// steps: folders | npm | venv | fonts | browser | speech
// Everything goes inside <work>/.engine (no global installs). Every download is pinned or recorded
// (see lib/pins.mjs). Prints one JSON line per step.
import { spawnSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import crypto from "node:crypto";
import { fileURLToPath } from "node:url";
import { PINNED, NO_NEWER_THAN, PIP_VERSION, FONT_COMMIT, FONTS, TURBO, SMALL, TURBO_MIN_RAM_GB } from "./lib/pins.mjs";
import { workFolder, DEFAULT_WORK, POINTER, venvPython } from "./lib/work.mjs";
import { downloadBrowser, browserStatus } from "./lib/browser.mjs";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const PLUGIN = path.resolve(HERE, "..");
const argv = process.argv.slice(2);
const step = argv[0];
const arg = (n, d) => { const i = argv.indexOf(n); return i >= 0 ? argv[i + 1] : d; };
const WORK = workFolder(argv);
const ENGINE = path.join(WORK, ".engine");
const isWin = process.platform === "win32";

function fail(stepName, error, extra = {}) { console.error(JSON.stringify({ ok: false, step: stepName, error, ...extra })); process.exit(1); }
function run(cmd, args, opts = {}) {
  const r = spawnSync(cmd, args, { encoding: "utf8", stdio: opts.quiet ? "pipe" : "inherit", shell: isWin && !path.isAbsolute(cmd), cwd: opts.cwd, timeout: opts.timeout || 45 * 60000, env: { ...process.env, ...(opts.env || {}) } });
  if (r.status !== 0 && !opts.allowFail) fail(opts.step, (r.stderr || r.error?.message || `exit code ${r.status}`).slice(-800), { command: [cmd, ...args].join(" ") });
  return r;
}
const done = (o) => console.log(JSON.stringify({ ok: true, ...o }));

async function download(url, file, check, stepName) {
  const res = await fetch(url);
  if (!res.ok) fail(stepName, `download failed (${res.status}) ${url}`);
  const tmp = file + ".part";
  const out = fs.createWriteStream(tmp);
  const sha256 = crypto.createHash("sha256");
  let size = 0;
  for await (const chunk of res.body) { sha256.update(chunk); size += chunk.length; if (!out.write(chunk)) await new Promise((r) => out.once("drain", r)); }
  await new Promise((r) => out.end(r));
  if (check.size && size !== check.size) { fs.rmSync(tmp, { force: true }); fail(stepName, `size mismatch for ${path.basename(file)}: ${size} bytes, expected ${check.size}`); }
  if (check.sha256 && sha256.digest("hex") !== check.sha256) { fs.rmSync(tmp, { force: true }); fail(stepName, `checksum mismatch for ${path.basename(file)}`); }
  if (check.gitsha1) {
    const buf = fs.readFileSync(tmp);
    const blob = crypto.createHash("sha1").update(`blob ${buf.length}\0`).update(buf).digest("hex");
    if (blob !== check.gitsha1) { fs.rmSync(tmp, { force: true }); fail(stepName, `checksum mismatch for ${path.basename(file)}`); }
  }
  fs.renameSync(tmp, file);
}

function folders() {
  fs.mkdirSync(ENGINE, { recursive: true });
  const settings = path.join(WORK, "settings.json");
  if (!fs.existsSync(settings)) {
    const s = JSON.parse(fs.readFileSync(path.join(PLUGIN, "skills", "ricksclips-engine", "references", "settings.default.json"), "utf8"));
    s.work_folder = WORK;
    s.whisper_model = os.totalmem() / 2 ** 30 >= TURBO_MIN_RAM_GB ? TURBO.name : SMALL.name; // the speech model follows the machine's memory
    fs.writeFileSync(settings, JSON.stringify(s, null, 2));
  }
  // remember a non-default work folder for later sessions (one line in the home folder)
  if (path.resolve(WORK) !== path.resolve(DEFAULT_WORK)) fs.writeFileSync(POINTER, WORK + "\n");
  done({ step: "folders", work: WORK, settings, whisper_model: JSON.parse(fs.readFileSync(settings, "utf8")).whisper_model });
}

function npm() {
  fs.mkdirSync(ENGINE, { recursive: true });
  const pkg = { name: "ricksclips-engine-tools", private: true, version: "3.0.0", description: "Pinned render tools for RicksClips-Engine", dependencies: { ...PINNED } };
  fs.writeFileSync(path.join(ENGINE, "package.json"), JSON.stringify(pkg, null, 2));
  // --before keeps indirect dependencies to releases made before the cutoff as well
  run(isWin ? "npm.cmd" : "npm", ["install", "--save-exact", "--no-audit", "--no-fund", `--before=${NO_NEWER_THAN}`], { cwd: ENGINE, step: "npm" });
  for (const [p, v] of Object.entries(PINNED)) {
    const pj = path.join(ENGINE, "node_modules", p, "package.json");
    const got = fs.existsSync(pj) ? JSON.parse(fs.readFileSync(pj, "utf8")).version : null;
    if (got !== v) fail("npm", `${p} ${got} installed, ${v} required`);
  }
  done({ step: "npm", pinned: PINNED, no_newer_than: NO_NEWER_THAN });
}

function venv() {
  const py = (arg("--python", isWin ? "python" : "python3")).split(" ");
  const vdir = path.join(ENGINE, ".venv");
  if (!fs.existsSync(vdir)) run(py[0], [...py.slice(1), "-m", "venv", vdir], { step: "venv" });
  const vpy = venvPython(ENGINE);
  run(vpy, ["-m", "pip", "install", "--disable-pip-version-check", "-q", `pip==${PIP_VERSION}`], { step: "venv" });
  for (const req of ["requirements.txt", "requirements-speech.txt"])
    run(vpy, ["-m", "pip", "install", "--disable-pip-version-check", "-q", "--only-binary=:all:", `--uploaded-prior-to=${NO_NEWER_THAN}`, "-r", path.join(PLUGIN, "scripts", req)], { step: "venv" });
  done({ step: "venv", python: vpy });
}

async function fonts() {
  const dir = path.join(ENGINE, "fonts"); fs.mkdirSync(dir, { recursive: true });
  for (const [name, f] of Object.entries(FONTS)) {
    const file = path.join(dir, name);
    if (fs.existsSync(file) && crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex") === f.sha256) continue;
    await download(`https://raw.githubusercontent.com/google/fonts/${FONT_COMMIT}/${f.src}`, file, { sha256: f.sha256 }, "fonts");
  }
  done({ step: "fonts", dir, fonts: Object.keys(FONTS), license: "SIL Open Font License 1.1" });
}

async function browser() {
  try { const s = await downloadBrowser(ENGINE); done({ step: "browser", path: s.path, source: s.type }); }
  catch (e) { fail("browser", String(e.message || e).slice(0, 600)); }
}

// The speech model. turbo: OpenAI Whisper large-v3-turbo (faster-whisper format), downloaded with huggingface_hub; the
// revision that was downloaded is recorded next to it. small.en: pinned files checked by size and checksum.
// Then a one-second self-test, so a computer where the model does not load is found now, not in the middle of a short.
async function speech() {
  const vpy = venvPython(ENGINE);
  if (!fs.existsSync(vpy)) fail("speech", "Run the venv step first.");
  let model = TURBO.name;
  try { model = JSON.parse(fs.readFileSync(path.join(WORK, "settings.json"), "utf8")).whisper_model || model; } catch { /* default */ }
  const models = path.join(ENGINE, "models"); fs.mkdirSync(models, { recursive: true });
  let dir;
  if (model === TURBO.name) {
    dir = path.join(models, TURBO.dir);
    const code = [
      "import json, sys", "from huggingface_hub import snapshot_download, HfApi",
      `repo, out = ${JSON.stringify(TURBO.repo)}, sys.argv[1]`,
      "snapshot_download(repo_id=repo, local_dir=out, allow_patterns=['config.json','model.bin','tokenizer.json','vocabulary.*','preprocessor_config.json'])",
      "try:\n    sha = HfApi().model_info(repo).sha\nexcept Exception:\n    sha = None",
      "json.dump({'repo': repo, 'revision': sha}, open(out + '/downloaded.json', 'w'))",
    ].join("\n");
    run(vpy, ["-c", code, dir], { step: "speech" });
  } else {
    dir = path.join(models, SMALL.dir); fs.mkdirSync(dir, { recursive: true });
    for (const [name, f] of Object.entries(SMALL.files)) {
      const file = path.join(dir, name);
      if (fs.existsSync(file) && fs.statSync(file).size === f.size) continue;
      await download(`https://huggingface.co/${SMALL.repo}/resolve/${SMALL.revision}/${name}`, file, f, "speech");
    }
  }
  const t = run(vpy, [path.join(HERE, "whisper_words.py"), "--selftest", dir], { step: "speech", quiet: true, allowFail: true, timeout: 20 * 60000 });
  done({ step: "speech", model, dir, self_test: t.status === 0 ? "ok" : "failed", detail: t.status === 0 ? null : ((t.stderr || "") + (t.stdout || "")).slice(-400) });
}

const steps = { folders, npm, venv, fonts, browser, speech };
if (!steps[step]) fail(step || "none", `unknown step. Steps: ${Object.keys(steps).join(", ")}`);
await steps[step]();
