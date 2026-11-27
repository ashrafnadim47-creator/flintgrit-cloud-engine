
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
