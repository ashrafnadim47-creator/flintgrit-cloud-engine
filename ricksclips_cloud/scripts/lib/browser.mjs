// Helpers that use the pinned Remotion in <work>/.engine: load it, find the render browser, probe WebGL.
import { createRequire } from "node:module";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { browserOverride } from "./work.mjs";

const HERE = path.dirname(fileURLToPath(import.meta.url));
export const PLUGIN = path.resolve(HERE, "..", "..");

export function engineRequire(engineDir) {
  return createRequire(path.join(engineDir, "package.json"));
}

// "ok" | "missing"
export async function browserStatus(engineDir) {
  const req = engineRequire(engineDir);
  let R; try { R = req("@remotion/renderer"); } catch { return { ok: false, why: "Remotion is not installed" }; }
  const override = browserOverride();
  if (override && fs.existsSync(override)) {
    return { ok: true, path: override, source: "browserOverride" };
  }
  try {
    const s = await R.ensureBrowser({ logLevel: "info" });
    return { ok: !!s.path, path: s.path || null, source: s.type };
  } catch (e) {
    return { ok: false, why: String(e.message || e).slice(0, 200) };
  }
}

export async function downloadBrowser(engineDir) {
  const R = engineRequire(engineDir)("@remotion/renderer");
  const override = browserOverride();
  const s = await R.ensureBrowser({ logLevel: "info", browserExecutable: override || undefined });
  return s;
}

export function bundleOverride(engineDir) {
  const nm = path.join(engineDir, "node_modules");
  return (config) => ({ ...config, resolve: { ...config.resolve, modules: [nm, "node_modules"] } });
}

// Render two small test frames (540x960 and 1440x2560) of a WebGL page and read the GPU name from the page log.
// Returns { gl: "angle" | "swangle", renderer, hardware, ok2k, ms2k, error }.
export async function probeWebGL(engineDir) {
  const req = engineRequire(engineDir);
  const { bundle } = req("@remotion/bundler");
  const R = req("@remotion/renderer");
  const entry = path.join(PLUGIN, "engine", "probe", "index.jsx");
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "ricksclips-gl-"));
  const cwd = process.cwd(); process.chdir(engineDir); // keep the bundler cache in the work folder
  const result = { gl: null, renderer: null, hardware: false, ok2k: false, ms2k: null, error: null };
  try {
    const serveUrl = await bundle({ entryPoint: entry, webpackOverride: bundleOverride(engineDir), outDir: path.join(tmp, "bundle") });
    for (const gl of ["angle", "swangle"]) {
      let log = "";
      const base = {
        serveUrl,
        browserExecutable: browserOverride() || undefined,
        chromiumOptions: {
          gl,
          args: ["--no-sandbox", "--disable-gpu-sandbox", "--disable-dev-shm-usage"]
        },
        logLevel: "error",
        timeoutInMilliseconds: 120000,
        onBrowserLog: (l) => { log += l.text + "\n"; }
      };
      try {
        const comp = await R.selectComposition({ id: "probe", ...base });
        await R.renderStill({ composition: comp, frame: 0, output: path.join(tmp, "p.png"), imageFormat: "jpeg", ...base });
        const m = log.match(/RC_GL:(.*)/);
        const renderer = m ? m[1].trim() : null;
        // this mode gave no WebGL2 at all: try the next one (software WebGL through ANGLE and SwiftShader)
        if (!renderer || /^no webgl/i.test(renderer)) { result.error = `WebGL2 is not available with gl=${gl}`; continue; }
        result.error = null;
        result.gl = gl; result.renderer = renderer;
        result.hardware = !/swiftshader|llvmpipe|software|softpipe|microsoft basic render/i.test(renderer);
        const comp2 = await R.selectComposition({ id: "probe2k", ...base });
        const t0 = Date.now();
        try { await R.renderStill({ composition: comp2, frame: 0, output: path.join(tmp, "p2.png"), imageFormat: "jpeg", ...base }); result.ok2k = true; } catch (e) { result.error = String(e.message || e).slice(0, 300); }
        result.ms2k = Date.now() - t0;
        break;
      } catch (e) { result.error = String(e.message || e).slice(0, 300); }
    }
  } catch (e) { result.error = String(e.message || e).slice(0, 300); }
  process.chdir(cwd);
  try { fs.rmSync(tmp, { recursive: true, force: true }); } catch { /* temp */ }
  return result;
}

// 2K only when the machine can do it without trouble; otherwise 1080p, decided here, never asked.
export function decideQuality(wanted, machine, probe) {
  if (wanted === "1080p") return { quality: "1080p", reason: null };
  const why = [];
  if (machine.ram_gb < 6) why.push(`only ${machine.ram_gb} GB of memory`);
  if (machine.ram_free_gb < 2.5) why.push(`only ${machine.ram_free_gb} GB of free memory right now (closing other apps may allow 2K)`);
  if (probe && probe.gl && !probe.hardware) why.push("no graphics acceleration (WebGL runs in software)");
  if (probe && !probe.ok2k) why.push("a 2K test frame could not be rendered");
  return why.length ? { quality: "1080p", reason: why.join("; ") } : { quality: "2k", reason: null };
}
