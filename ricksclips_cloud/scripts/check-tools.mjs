#!/usr/bin/env node
// Silent tool check. Prints one JSON report: this computer, every tool needed for this operating system only,
// what is missing, the install plan for this OS, and notes.
//   node check-tools.mjs [--work <folder>] [--gpu]
// (Node itself must exist to run this; the skill checks `node --version` first.)
import { spawnSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { PINNED, MIN, FONTS, TURBO, SMALL, TURBO_MIN_RAM_GB } from "./lib/pins.mjs";
import { workFolder, venvPython } from "./lib/work.mjs";
import { browserStatus, probeWebGL, decideQuality } from "./lib/browser.mjs";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const argv = process.argv.slice(2);
const WORK = workFolder(argv);
const ENGINE = path.join(WORK, ".engine");
const OS = process.platform === "darwin" ? "macos" : process.platform === "win32" ? "windows" : "linux";
const isWin = OS === "windows";

function run(cmd, args, opts = {}) {
  // shell only for bare command names on Windows (npm.cmd and PATH lookups); full paths run directly
  const r = spawnSync(cmd, args, { encoding: "utf8", shell: isWin && !path.isAbsolute(cmd), timeout: opts.timeout || 60000, cwd: opts.cwd });
  return { ok: r.status === 0, out: (r.stdout || "") + (r.stderr || ""), status: r.status };
}
const ver = (s) => (s.match(/(\d+)\.(\d+)(?:\.(\d+))?/) || []).slice(1, 4).map((x) => Number(x || 0));
const atLeast = (v, min) => { for (let i = 0; i < 3; i++) { if ((v[i] || 0) > min[i]) return true; if ((v[i] || 0) < min[i]) return false; } return true; };

// Package manager of this OS (the installer for the system tools).
const PM = {};
if (OS === "macos") PM.homebrew = run("brew", ["--version"]).ok;
if (OS === "windows") { PM.winget = run("winget", ["--version"]).ok; PM.choco = run("choco", ["--version"]).ok; }
if (OS === "linux") { PM.apt = run("apt-get", ["--version"]).ok; PM.dnf = run("dnf", ["--version"]).ok; PM.pacman = run("pacman", ["--version"]).ok; }
const manager = OS === "macos" ? (PM.homebrew ? "homebrew" : null) : OS === "windows" ? (PM.winget ? "winget" : PM.choco ? "chocolatey" : null) : (PM.apt ? "apt" : PM.dnf ? "dnf" : PM.pacman ? "pacman" : null);

// Install commands per OS (official sources: nodejs.org, nvm, formulae.brew.sh, winget-pkgs, Debian/Ubuntu/Fedora packages).
const NEEDS_NVM = "Node 22 or newer from the system package list is often too old on Linux, so nvm is used.";
const INSTALL = {
  homebrew: { macos: ['/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'] },
  winget: { windows: ["Install \"App Installer\" from the Microsoft Store (it provides winget), or install Chocolatey from https://chocolatey.org/install, then run setup again."] },
  node: {
    macos: ["brew install node"],
    windows: { winget: ["winget install --id OpenJS.NodeJS.LTS -e"], chocolatey: ["choco install nodejs-lts -y"] },
    linux: ["curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.8/install.sh | bash", '\\. "$HOME/.nvm/nvm.sh"', "nvm install 24"],
  },
  ffmpeg: {
    macos: ["brew install ffmpeg"],
    windows: { winget: ["winget install --id Gyan.FFmpeg -e"], chocolatey: ["choco install ffmpeg -y"] },
    linux: { apt: ["sudo apt update", "sudo apt install -y ffmpeg"], dnf: ["sudo dnf install -y ffmpeg-free"], pacman: ["sudo pacman -S --noconfirm ffmpeg"] },
  },
  python: {
    macos: ["brew install python@3.13"],
    windows: { winget: ["winget install --id Python.Python.3.13 -e"], chocolatey: ["choco install python -y"] },
    linux: { apt: ["sudo apt update", "sudo apt install -y python3 python3-venv python3-pip"], dnf: ["sudo dnf install -y python3 python3-pip"], pacman: ["sudo pacman -S --noconfirm python python-pip"] },
  },
};
function plan(tool) {
  const t = INSTALL[tool]?.[OS];
  if (!t) return null;
  if (Array.isArray(t)) return t;
  return t[manager] || (OS === "windows" ? INSTALL.winget.windows : null);
}

const report = { os: OS, arch: process.arch, work: WORK, package_manager: manager, tools: {}, machine: {}, missing: [], install_plan: {}, notes: [] };
const tool = (name, data) => { report.tools[name] = data; if (!data.ok) report.missing.push(name); };

report.machine.cpu_type = process.arch === "arm64" ? (OS === "macos" ? "Apple Silicon (arm64)" : "ARM (arm64)") : process.arch === "x64" ? "Intel/AMD (x64)" : process.arch;
if (OS === "windows" && process.arch === "arm64") report.notes.push("Windows on ARM: Python packages for speech may not have ARM builds. Install the x64 versions of Node and Python (they run under emulation). This combination is untested.");
if (OS === "macos" && !manager) { report.tools.homebrew = { found: false, ok: false, needed_for: "installing Node, FFmpeg and Python", install: INSTALL.homebrew.macos, needs_user: "Homebrew asks for your password: run the command in your own terminal." }; report.missing.push("homebrew"); }
if (OS === "windows" && !manager) { report.tools.winget = { found: false, ok: false, needed_for: "installing Node, FFmpeg and Python", install: INSTALL.winget.windows }; report.missing.push("winget"); }
if (OS === "macos" && manager) report.tools.homebrew = { found: true, ok: true };
if (OS === "windows" && manager) report.tools[manager] = { found: true, ok: true };

// Node + npm
const nodeV = ver(process.version);
tool("node", { found: true, version: process.version, min: "22.0.0", ok: atLeast(nodeV, MIN.node), install: plan("node"), fix: "Install Node 22 or newer, then open a new terminal so the new version is on PATH.", note: OS === "linux" ? NEEDS_NVM : null });
const npm = run(isWin ? "npm.cmd" : "npm", ["--version"]);
tool("npm", { found: npm.ok, version: npm.ok ? npm.out.trim() : null, ok: npm.ok, install: plan("node"), fix: "npm comes with Node." });
// FFmpeg / ffprobe
for (const name of ["ffmpeg", "ffprobe"]) {
  const r = run(name, ["-version"]);
  const v = r.ok ? ver(r.out) : [0, 0, 0];
  tool(name, { found: r.ok, version: r.ok ? r.out.split("\n")[0] : null, min: "6.0", ok: r.ok && atLeast(v, MIN.ffmpeg), install: plan("ffmpeg"), fix: isWin ? "After installing, open a new terminal (PATH changes only reach new terminals)." : "Install with the command above." });
}
// Python (system): the venv is made from it. Windows uses `python` or the `py -3` launcher, macOS and Linux use `python3`.
const pyCmds = isWin ? [["python"], ["py", "-3"]] : [["python3"], ["python"]];
let py = null;
for (const c of pyCmds) { const r = run(c[0], [...c.slice(1), "--version"]); if (r.ok && /Python 3\./.test(r.out)) { py = { cmd: c.join(" "), v: ver(r.out), raw: r.out.trim() }; break; } }
tool("python", { found: !!py, command: py?.cmd || null, version: py?.raw || null, min: "3.12", ok: !!py && atLeast(py.v, MIN.python), install: plan("python"),
  fix: isWin ? "Use the real Python from winget or python.org (the Microsoft Store 'python' shim is not enough). Open a new terminal after installing." : "Install Python 3.12 or newer with venv support." });

// machine: RAM, disk, cores, chosen speech model
const total = os.totalmem(), free = os.freemem();
report.machine.ram_gb = +(total / 2 ** 30).toFixed(1);
report.machine.ram_free_gb = +(free / 2 ** 30).toFixed(1);
report.machine.cores = os.cpus().length;
report.machine.cpu = os.cpus()[0]?.model || "unknown";
report.machine.workers = Math.max(1, Math.min(4, Math.floor(Math.min(report.machine.ram_free_gb / 3, report.machine.cores / 2))));
report.machine.whisper_model = report.machine.ram_gb >= TURBO_MIN_RAM_GB ? TURBO.name : SMALL.name;
report.machine.whisper_download_gb = report.machine.whisper_model === TURBO.name ? TURBO.approx_gb : SMALL.approx_gb;
try {
  const st = fs.statfsSync(fs.existsSync(WORK) ? WORK : os.homedir());
  report.machine.disk_free_gb = +((st.bavail * st.bsize) / 2 ** 30).toFixed(1);
  if (report.machine.disk_free_gb < 10) report.notes.push(`Only ${report.machine.disk_free_gb} GB of disk space is free. Setup needs about 5 GB, and each short needs 2-3 GB while rendering.`);
} catch { report.machine.disk_free_gb = null; }

// workspace parts
const venvPy = venvPython(ENGINE);
let pkgs = false;
if (fs.existsSync(venvPy)) { const r = run(venvPy, ["-c", "import numpy, scipy, PIL, faster_whisper; print(numpy.__version__, scipy.__version__, PIL.__version__, faster_whisper.__version__)"]); pkgs = r.ok; report.tools.python_packages = { found: r.ok, version: r.ok ? r.out.trim() : null, ok: r.ok, venv: venvPy }; }
else report.tools.python_packages = { found: false, ok: false, venv: venvPy };
if (!pkgs) report.missing.push("python_packages");
for (const [pkg, v] of Object.entries(PINNED)) {
  const pj = path.join(ENGINE, "node_modules", pkg, "package.json");
  const got = fs.existsSync(pj) ? JSON.parse(fs.readFileSync(pj, "utf8")).version : null;
  tool(pkg, { found: !!got, version: got, pinned: v, ok: got === v, fix: got && got !== v ? `Installed ${got}, but RicksClips-Engine needs exactly ${v}.` : null });
}
const fontsOk = Object.keys(FONTS).every((f) => fs.existsSync(path.join(ENGINE, "fonts", f)));
tool("fonts", { found: fontsOk, ok: fontsOk, files: Object.keys(FONTS), fix: "Run the fonts setup step." });
const chosen = (() => { try { return JSON.parse(fs.readFileSync(path.join(WORK, "settings.json"), "utf8")).whisper_model; } catch { return null; } })() || report.machine.whisper_model;
const modelDir = path.join(ENGINE, "models", chosen === TURBO.name ? TURBO.dir : SMALL.dir);
const modelOk = fs.existsSync(path.join(modelDir, "model.bin"));
tool("speech_model", { found: modelOk, ok: modelOk, name: chosen === TURBO.name ? "OpenAI Whisper turbo (large-v3-turbo)" : "Whisper small.en", approx_gb: chosen === TURBO.name ? TURBO.approx_gb : SMALL.approx_gb, dir: modelDir, fix: "Run the speech setup step." });
if (fs.existsSync(path.join(ENGINE, "node_modules", "@remotion", "renderer"))) {
  const b = await browserStatus(ENGINE);
  tool("render_browser", { found: b.ok, ok: b.ok, path: b.path || null, approx_mb: 190, fix: "Run the browser setup step." });
} else tool("render_browser", { found: false, ok: false, approx_mb: 190 });

// GPU probe: render one small and one 2K test frame; decide 2K or 1080p for this machine
if (argv.includes("--gpu") && report.tools.render_browser.ok && report.tools["@remotion/bundler"].ok) {
  const t0 = Date.now();
  const p = await probeWebGL(ENGINE);
  report.machine.webgl = p.gl ? (p.hardware ? "gpu" : "software") : "unknown";
  report.machine.gpu_name = p.renderer;
  report.machine.gl_mode = p.gl;
  report.machine.probe_ms = Date.now() - t0;
  report.machine.test_2k_frame_ok = p.ok2k;
  if (p.error) report.notes.push("WebGL probe: " + p.error);
  if (p.gl && !p.hardware) report.notes.push("WebGL runs in software (no graphics acceleration). Renders are about 9 times slower. Updating the graphics driver, closing remote-desktop sessions, or using a computer with a GPU fixes this.");
  let wanted = "2k"; try { wanted = JSON.parse(fs.readFileSync(path.join(WORK, "settings.json"), "utf8")).quality || "2k"; } catch { /* default */ }
  report.machine.quality_decision = decideQuality(wanted, report.machine, p);
}
report.ok = report.missing.length === 0;
console.log(JSON.stringify(report, null, 2));
