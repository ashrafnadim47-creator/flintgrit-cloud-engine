"""
Curated Multi-Story Library for Shadow Will Merged Engine (Version 6 + RicksClips 3D Props).
Each story has a unique ID, title, description, tags, mood, script, and complete Three.js + Bean-Head story.js.
"""
from pathlib import Path

SOLDIER_STORY_PATH = Path(__file__).resolve().parent / "soldier_story.js"

CHOCOLATE_HEIST_JS = r"""
export const FPS = 30, TOTAL = 600, DECK = 0;
export const SHOTS = [
  { id: 'hook', a: 0, b: 149, light: 'night' },
  { id: 'plan', a: 150, b: 299, light: 'interior' },
  { id: 'vault', a: 300, b: 449, light: 'night' },
  { id: 'escape', a: 450, b: 599, light: 'golden' },
];
export const shotAt = (f) => SHOTS.find((s) => f >= s.a && f <= s.b) || SHOTS[SHOTS.length - 1];
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
export const smooth = (t) => { t = clamp(t); return t * t * t * (t * (t * 6 - 15) + 10); };
const lerp = (a, b, t) => a + (b - a) * t;
const lerp3 = (a, b, t) => a.map((v, i) => lerp(v, b[i], t));
const ramp = (f, a, b) => clamp((f - a) / (b - a));

export const LIGHTS = {
  night: { az: 120, el: 35, sky: '#1e293b', ground: '#0f172a', hemi: 0.9, sun: '#93c5fd', sunI: 1.6, fog: '#0f172a', fogNear: 25, fogFar: 180,
    skyTop: '#020617', skyHor: '#1e293b', sat: 1.15, waterDeep: '#0f172a', waterShal: '#1e293b', glint: '#60a5fa', vig: 0.35, shadowExt: 16 },
  interior: { az: 60, el: 55, sky: '#fde68a', ground: '#451a03', hemi: 1.2, sun: '#fffbeb', sunI: 2.1, fog: '#292524', fogNear: 20, fogFar: 120,
    skyTop: '#292524', skyHor: '#44403c', sat: 1.1, waterDeep: '#111', waterShal: '#222', glint: '#fff', vig: 0.28, shadowExt: 14 },
  golden: { az: 15, el: 14, sky: '#fed7aa', ground: '#7c2d12', hemi: 1.1, sun: '#fb923c', sunI: 2.4, fog: '#fdba74', fogNear: 30, fogFar: 220,
    skyTop: '#4338ca', skyHor: '#fb923c', sunDisc: '#fef08a', sunSize: 0.004, sat: 1.18, waterDeep: '#1e3a8a', waterShal: '#f59e0b', glint: '#fde047', vig: 0.25, shadowExt: 18 },
};
export const lightFor = (S, f) => ({ ...LIGHTS[S.light] });

let diaObj = null;
export function buildWorld({ THREE, M, world, add, tbox, box, toon, props }) {
  props.roomBox(world, 14, 5, 14, M.stone, M.marble);
  props.vaultDoor(world, 0, 0, -5.8, 0, 0.35);
  diaObj = props.diamondDisplay(world, 0, 0, -1.5);
  props.goldStack(world, -3.2, 0, -3.8, 6);
  props.desk(world, 3.2, 0, 1.5, -0.4);
  props.chair(world, 3.2, 0, 2.5, -0.4);
  props.streetLamp(world, -4.5, 0, 4.5);
  props.crateStack(world, -4.2, 0, -1.2);
}

const CAMS = {
  hook: [
    { f: 0, pos: [0, 2.2, 4.6], look: [0, 1.35, -1.5], fov: 38 },
    { f: 149, pos: [1.4, 2.0, 3.4], look: [0, 1.35, -1.5], fov: 34 },
  ],
  plan: [
    { f: 150, pos: [5.5, 2.1, 4.2], look: [3.2, 1.2, 1.5], fov: 36 },
    { f: 299, pos: [4.2, 1.9, 3.6], look: [3.2, 1.2, 1.5], fov: 33 },
  ],
  vault: [
    { f: 300, pos: [-2.6, 2.1, 2.5], look: [0, 1.5, -4.5], fov: 40 },
    { f: 449, pos: [-0.8, 1.8, 1.2], look: [0, 1.4, -2.5], fov: 36 },
  ],
  escape: [
    { f: 450, pos: [3.2, 2.3, 5.2], look: [-1.0, 1.2, 0], fov: 42 },
    { f: 599, pos: [1.5, 2.6, 6.2], look: [-2.0, 1.2, -1.0], fov: 40 },
  ],
};
export const camAt = (f) => {
  const S = shotAt(f), K = CAMS[S.id];
  const t = smooth((f - K[0].f) / Math.max(1, K[K.length - 1].f - K[0].f));
  return { pos: lerp3(K[0].pos, K[1].pos, t), look: lerp3(K[0].look, K[1].look, t), fov: lerp(K[0].fov, K[1].fov, t), roll: 0, flash: 0 };
};
export const dofAt = () => ({ focus: 5, cinf: 4, near: 1 });
export const worldAt = (f) => { if (diaObj && diaObj.diamond) diaObj.diamond.rotation.y = f * 0.05; return {}; };
export const fxAt = () => [];
export const actorsAt = (f, T) => {
  const S = shotAt(f);
  if (S.id === 'hook') return [
    { key: `g_${(f/6)|0}`, x: -1.8, y: 0, z: -2.2, s: 1.0, draw: (p) => T.romanFront(p, 'guard', { seed: 11, expr: 'stern', step: ((f % 20) / 20) }) },
  ];
  if (S.id === 'plan') return [
    { key: `r_${(f/4)|0}`, x: 3.0, y: 0, z: 2.2, s: 1.0, draw: (p) => T.romanFront(p, 'robber', { seed: 22, expr: 'grin', L: 'point', headTilt: Math.sin(f * 0.2) * 3 }) },
  ];
  if (S.id === 'vault') return [
    { key: `rv_${(f/4)|0}`, x: lerp(-2.2, 0.2, ramp(f, 300, 420)), y: 0, z: -1.2, s: 1.0, draw: (p) => T.romanFront(p, 'robber', { seed: 22, expr: 'stubborn', step: ((f % 20) / 20) }) },
  ];
  return [
    { key: `re_${(f/4)|0}`, x: lerp(0, -3.5, ramp(f, 450, 599)), y: 0, z: 1.5, s: 1.0, draw: (p) => T.romanFront(p, 'robber', { seed: 22, expr: 'grin', step: ((f % 12) / 12), bob: Math.abs(Math.sin(f * 0.4)) * 0.03 }) },
  ];
};
"""

FAKE_PILOT_JS = r"""
export const FPS = 30, TOTAL = 600, DECK = 0;
export const SHOTS = [
  { id: 'tarmac', a: 0, b: 149, light: 'day' },
  { id: 'office', a: 150, b: 299, light: 'interior' },
  { id: 'flight', a: 300, b: 449, light: 'golden' },
  { id: 'busted', a: 450, b: 599, light: 'day' },
];
export const shotAt = (f) => SHOTS.find((s) => f >= s.a && f <= s.b) || SHOTS[SHOTS.length - 1];
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
export const smooth = (t) => { t = clamp(t); return t * t * t * (t * (t * 6 - 15) + 10); };
const lerp = (a, b, t) => a + (b - a) * t;
const lerp3 = (a, b, t) => a.map((v, i) => lerp(v, b[i], t));
const ramp = (f, a, b) => clamp((f - a) / (b - a));

export const LIGHTS = {
  day: { az: 140, el: 48, sky: '#bae6fd', ground: '#64748b', hemi: 1.2, sun: '#fffbeb', sunI: 2.4, fog: '#e0f2fe', fogNear: 40, fogFar: 260,
    skyTop: '#0284c7', skyHor: '#bae6fd', sat: 1.1, waterDeep: '#0369a1', waterShal: '#38bdf8', glint: '#fff', vig: 0.18, shadowExt: 20 },
  interior: { az: 60, el: 50, sky: '#e2e8f0', ground: '#475569', hemi: 1.25, sun: '#ffffff', sunI: 1.9, fog: '#cbd5e1', fogNear: 25, fogFar: 140,
    skyTop: '#334155', skyHor: '#94a3b8', sat: 1.05, waterDeep: '#111', waterShal: '#222', glint: '#fff', vig: 0.22, shadowExt: 16 },
  golden: { az: 10, el: 12, sky: '#fed7aa', ground: '#78350f', hemi: 1.05, sun: '#fb923c', sunI: 2.6, fog: '#fdba74', fogNear: 35, fogFar: 240,
    skyTop: '#4f46e5', skyHor: '#fb923c', sunDisc: '#fef08a', sunSize: 0.004, sat: 1.15, waterDeep: '#1e3a8a', waterShal: '#f59e0b', glint: '#fde047', vig: 0.22, shadowExt: 22 },
};
export const lightFor = (S) => ({ ...LIGHTS[S.light] });

let planeObj = null;
export function buildWorld({ M, world, add, tbox, props }) {
  add(tbox(60, 0.2, 16, 2), M.stone, 0, 0, -4, world, { cast: false });
  planeObj = props.airplane(world, 0, 0.2, -5.5, 0.35);
  props.desk(world, 8, 0, 4, -0.3);
  props.monitor(world, 8, 0.8, 3.8, -0.3, '#38bdf8');
  props.chair(world, 8, 0, 5, -0.3);
  props.crateStack(world, -6, 0, -2);
}

const CAMS = {
  tarmac: [
    { f: 0, pos: [4.2, 2.4, 3.8], look: [0, 1.5, -4], fov: 42 },
    { f: 149, pos: [2.2, 2.1, 2.6], look: [0, 1.4, -3.5], fov: 38 },
  ],
  office: [
    { f: 150, pos: [10.6, 2.0, 6.8], look: [8, 1.2, 4.0], fov: 36 },
    { f: 299, pos: [9.8, 1.8, 6.0], look: [8, 1.2, 4.0], fov: 34 },
  ],
  flight: [
    { f: 300, pos: [-5.5, 3.2, 2.0], look: [0, 1.8, -5.5], fov: 44 },
    { f: 449, pos: [-2.5, 2.8, 1.0], look: [0, 1.8, -5.5], fov: 40 },
  ],
  busted: [
    { f: 450, pos: [3.2, 1.9, 3.8], look: [0, 1.2, -1], fov: 36 },
    { f: 599, pos: [1.8, 1.8, 2.8], look: [0, 1.2, -1], fov: 34 },
  ],
};
export const camAt = (f) => {
  const S = shotAt(f), K = CAMS[S.id];
  const t = smooth((f - K[0].f) / Math.max(1, K[1].f - K[0].f));
  return { pos: lerp3(K[0].pos, K[1].pos, t), look: lerp3(K[0].look, K[1].look, t), fov: lerp(K[0].fov, K[1].fov, t), roll: 0, flash: 0 };
};
export const dofAt = () => ({ focus: 6, cinf: 3, near: 1 });
export const worldAt = (f) => {
  if (planeObj) planeObj.position.y = f >= 300 && f < 450 ? 0.2 + Math.sin(f * 0.08) * 0.25 : 0.2;
  return {};
};
export const fxAt = () => [];
export const actorsAt = (f, T) => {
  const S = shotAt(f);
  if (S.id === 'tarmac') return [
    { key: `p_${(f/4)|0}`, x: lerp(-2, 1.2, ramp(f, 0, 149)), y: 0.1, z: -0.5, s: 1.0, draw: (p) => T.romanFront(p, 'pilot', { seed: 31, expr: 'grin', step: ((f % 20) / 20) }) },
  ];
  if (S.id === 'office') return [
    { key: `po_${(f/5)|0}`, x: 8, y: 0, z: 4.9, s: 1.0, draw: (p) => T.romanFront(p, 'pilot', { seed: 31, expr: 'grin', L: 'hip', headTilt: Math.sin(f * 0.2) * 3 }) },
  ];
  if (S.id === 'flight') return [
    { key: `pf_${(f/5)|0}`, x: 0, y: 0.1, z: -1.5, s: 1.0, draw: (p) => T.romanFront(p, 'pilot', { seed: 31, expr: 'grin', L: 'point' }) },
  ];
  return [
    { key: `pb_${(f/4)|0}`, x: -0.7, y: 0.1, z: -1, s: 1.0, draw: (p) => T.romanFront(p, 'pilot', { seed: 31, expr: 'shock', L: 'cheek', R: 'cheek' }) },
    { key: `g_${(f/4)|0}`, x: 0.9, y: 0.1, z: -1, s: 1.0, draw: (p) => T.romanFront(p, 'guard', { seed: 11, expr: 'stern', L: 'point', facing: -1 }) },
  ];
};
"""

NASA_TYPO_JS = r"""
export const FPS = 30, TOTAL = 600, DECK = 0;
export const SHOTS = [
  { id: 'lab', a: 0, b: 149, light: 'interior' },
  { id: 'code', a: 150, b: 299, light: 'interior' },
  { id: 'launch', a: 300, b: 449, light: 'golden' },
  { id: 'crash', a: 450, b: 599, light: 'night' },
];
export const shotAt = (f) => SHOTS.find((s) => f >= s.a && f <= s.b) || SHOTS[SHOTS.length - 1];
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
export const smooth = (t) => { t = clamp(t); return t * t * t * (t * (t * 6 - 15) + 10); };
const lerp = (a, b, t) => a + (b - a) * t;
const lerp3 = (a, b, t) => a.map((v, i) => lerp(v, b[i], t));
export const LIGHTS = {
  interior: { az: 60, el: 52, sky: '#e2e8f0', ground: '#334155', hemi: 1.25, sun: '#ffffff', sunI: 2.0, fog: '#cbd5e1', fogNear: 25, fogFar: 140,
    skyTop: '#1e293b', skyHor: '#64748b', sat: 1.1, waterDeep: '#111', waterShal: '#222', glint: '#fff', vig: 0.2, shadowExt: 16 },
  golden: { az: 20, el: 16, sky: '#fed7aa', ground: '#7c2d12', hemi: 1.1, sun: '#fb923c', sunI: 2.5, fog: '#fdba74', fogNear: 30, fogFar: 220,
    skyTop: '#312e81', skyHor: '#fb923c', sunDisc: '#fef08a', sunSize: 0.004, sat: 1.15, waterDeep: '#1e3a8a', waterShal: '#f59e0b', glint: '#fde047', vig: 0.25, shadowExt: 18 },
  night: { az: 110, el: 30, sky: '#1e293b', ground: '#0f172a', hemi: 0.9, sun: '#f87171', sunI: 1.8, fog: '#0f172a', fogNear: 22, fogFar: 180,
    skyTop: '#020617', skyHor: '#450a0a', sat: 1.2, waterDeep: '#000', waterShal: '#111', glint: '#f87171', vig: 0.35, shadowExt: 16 },
};
export const lightFor = (S) => ({ ...LIGHTS[S.light] });

let rocket = null;
export function buildWorld({ THREE, M, world, add, toon, props }) {
  props.roomBox(world, 12, 5, 12, M.plaster, M.marble);
  props.desk(world, -1.5, 0, -1.5, 0);
  props.monitor(world, -1.5, 0.8, -1.7, 0, '#22d3ee');
  props.desk(world, 1.8, 0, -1.5, 0);
  props.monitor(world, 1.8, 0.8, -1.7, 0, '#f43f5e');
  props.chair(world, -1.5, 0, -0.5, 0);
  props.chair(world, 1.8, 0, -0.5, 0);
  rocket = new THREE.Group(); rocket.position.set(0, 0, -8); world.add(rocket);
  add(new THREE.CylinderGeometry(0.6, 0.7, 5.5, 14), toon({ color: '#f8fafc' }), 0, 2.75, 0, rocket);
  add(new THREE.ConeGeometry(0.6, 1.6, 14), toon({ color: '#ef4444' }), 0, 6.3, 0, rocket);
}

const CAMS = {
  lab: [
    { f: 0, pos: [0, 2.2, 4.2], look: [0, 1.2, -1.5], fov: 40 },
    { f: 149, pos: [-1.2, 2.0, 3.2], look: [-1.5, 1.2, -1.5], fov: 36 },
  ],
  code: [
    { f: 150, pos: [2.8, 1.9, 2.5], look: [1.8, 1.2, -1.5], fov: 34 },
    { f: 299, pos: [2.2, 1.7, 1.8], look: [1.8, 1.2, -1.5], fov: 30 },
  ],
  launch: [
    { f: 300, pos: [4.5, 2.8, -2.5], look: [0, 3.5, -8], fov: 44 },
    { f: 449, pos: [5.5, 4.2, -1.5], look: [0, 5.5, -8], fov: 46 },
  ],
  crash: [
    { f: 450, pos: [0, 2.1, 3.8], look: [0, 1.2, -1.5], fov: 38 },
    { f: 599, pos: [0, 2.3, 4.5], look: [0, 1.2, -1.5], fov: 40 },
  ],
};
export const camAt = (f) => {
  const S = shotAt(f), K = CAMS[S.id];
  const t = smooth((f - K[0].f) / Math.max(1, K[1].f - K[0].f));
  return { pos: lerp3(K[0].pos, K[1].pos, t), look: lerp3(K[0].look, K[1].look, t), fov: lerp(K[0].fov, K[1].fov, t), roll: 0, flash: 0 };
};
export const dofAt = () => ({ focus: 5, cinf: 3, near: 1 });
export const worldAt = (f) => {
  if (rocket) {
    if (f >= 300 && f < 450) { rocket.position.y = (f - 300) * 0.08; rocket.rotation.z = Math.sin(f * 0.2) * 0.08; }
    else { rocket.position.y = 0; rocket.rotation.z = 0; }
  }
  return {};
};
export const fxAt = () => [];
export const actorsAt = (f, T) => {
  const S = shotAt(f);
  if (S.id === 'crash') return [
    { key: `sc_${(f/4)|0}`, x: -0.8, y: 0, z: -0.2, s: 1.0, draw: (p) => T.romanFront(p, 'scientist', { seed: 41, expr: 'shock', L: 'cheek', R: 'cheek' }) },
    { key: `su_${(f/4)|0}`, x: 1.0, y: 0, z: -0.2, s: 1.0, draw: (p) => T.romanFront(p, 'suit', { seed: 42, expr: 'stern', L: 'point', facing: -1 }) },
  ];
  return [
    { key: `sc1_${(f/5)|0}`, x: -1.5, y: 0, z: -0.4, s: 1.0, draw: (p) => T.romanFront(p, 'scientist', { seed: 41, expr: 'neutral', headTilt: Math.sin(f * 0.15) * 2 }) },
    { key: `sc2_${(f/5)|0}`, x: 1.8, y: 0, z: -0.4, s: 1.0, draw: (p) => T.romanFront(p, 'suit', { seed: 42, expr: 'stern', L: 'hip', facing: -1 }) },
  ];
};
"""

CURATED_STORIES = [
    {
        "id": "soldier_never_left",
        "title": "The Roman Soldier Who Guarded a Bridge for 30 Years #shorts",
        "description": "A Roman soldier stood guard at a bridge for 30 years refusing to leave. When workers finally removed his helmet, they found a shocking message carved inside.\n\n#shorts #storytime #animation #shadowwill",
        "tags": ["shorts", "animation", "storytime", "roman history", "shadow will"],
        "mood": "epic",
        "script": (
            "A Roman soldier stood guard at a bridge for 30 years, refusing to leave his post. "
            "Even when the empire collapsed, he stayed. People called him crazy. "
            "But when workers finally removed his helmet, they discovered a message carved inside: "
            "The bridge is not safe. Beneath it, the wooden supports had been slowly rotting for centuries."
        ),
        "story_js_path": str(SOLDIER_STORY_PATH),
    },
    {
        "id": "chocolate_diamond_heist",
        "title": "He Stole $100M in Diamonds Using Chocolate Keys! 🍫💎 #shorts",
        "description": "How one mastermind thief bypassed an unbreakable Antwerp diamond vault using chocolate molds and patience.\n\n#shorts #heist #animation #storytime #shadowwill",
        "tags": ["shorts", "heist", "diamond heist", "animation", "shadow will"],
        "mood": "heist",
        "script": (
            "In 2007, a charming regular customer walked into a heavily guarded Antwerp bank every single week. "
            "He brought expensive Belgian chocolates to the vault guards to earn their trust. "
            "Secretly, he pressed wax molds against their master keys and froze duplicate keys out of dark chocolate and metal dust. "
            "One quiet weekend, he walked straight past the sensors and vanished with 100 million dollars in diamonds."
        ),
        "story_js": CHOCOLATE_HEIST_JS,
    },
    {
        "id": "fake_pilot_250_flights",
        "title": "The Fake Pilot Who Flew 250 Flights With Zero License! ✈️😱 #shorts",
        "description": "For 13 years, a man with zero aviation training flew commercial passenger jets across Europe using forged papers.\n\n#shorts #truecrime #aviation #animation #shadowwill",
        "tags": ["shorts", "fake pilot", "aviation", "animation", "shadow will"],
        "mood": "mystery",
        "script": (
            "For thirteen years, William Street flew commercial passenger planes across Europe without ever passing a single flight exam. "
            "He printed fake licenses on a home desk and wore a crisp uniform with total confidence. "
            "Over 250 flights and thousands of passengers later, he finally made one small radio mistake in Amsterdam. "
            "Investigators checked his file and realized the captain had never been a pilot at all."
        ),
        "story_js": FAKE_PILOT_JS,
    },
    {
        "id": "nasa_80m_typo",
        "title": "How ONE Missing Hyphen Cost NASA $80,000,000! 🚀💥 #shorts",
        "description": "In 1962, a single missing punctuation mark in flight guidance code destroyed Mariner 1 seconds after liftoff.\n\n#shorts #nasa #space #animation #shadowwill",
        "tags": ["shorts", "nasa", "space history", "animation", "shadow will"],
        "mood": "mystery",
        "script": (
            "In 1962, NASA launched Mariner 1 on a historic mission to Venus worth 80 million dollars. "
            "Everything looked perfect until 293 seconds after liftoff, when the rocket suddenly veered violently off course. "
            "Mission control had to hit the self-destruct button over the Atlantic Ocean. "
            "The culprit? One programmer had accidentally left out a single hyphen in the guidance equation."
        ),
        "story_js": NASA_TYPO_JS,
    },
]
