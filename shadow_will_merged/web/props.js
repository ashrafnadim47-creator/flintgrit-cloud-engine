// Merged RicksClips + Version 6 Painted Toon 3D Props Library
// Every prop uses MeshToonMaterial + tbox/Cylinder/Sphere so it receives the Version 6 Ink Pass & Shadows cleanly.

export function createProps(THREE, add, tbox, box, toon, M) {
  const mat = (c) => toon({ color: c });

  function desk(parent, x = 0, y = 0, z = 0, ry = 0) {
    const g = new THREE.Group(); g.position.set(x, y, z); g.rotation.y = ry; parent.add(g);
    add(tbox(1.8, 0.08, 0.9, 1.2), M.wood, 0, 0.76, 0, g);
    for (const sx of [-0.82, 0.82]) for (const sz of [-0.38, 0.38])
      add(box(0.07, 0.74, 0.07), M.iron, sx, 0.37, sz, g);
    return g;
  }

  function chair(parent, x = 0, y = 0, z = 0, ry = 0, col = '#2f3a4a') {
    const g = new THREE.Group(); g.position.set(x, y, z); g.rotation.y = ry; parent.add(g);
    const m = mat(col);
    add(box(0.54, 0.07, 0.52), m, 0, 0.46, 0, g);
    add(box(0.54, 0.56, 0.07), m, 0, 0.76, -0.23, g);
    for (const sx of [-0.23, 0.23]) for (const sz of [-0.22, 0.22])
      add(box(0.05, 0.45, 0.05), M.iron, sx, 0.225, sz, g);
    return g;
  }

  function monitor(parent, x = 0, y = 0.8, z = 0, ry = 0, screenCol = '#38bdf8') {
    const g = new THREE.Group(); g.position.set(x, y, z); g.rotation.y = ry; parent.add(g);
    add(box(0.08, 0.16, 0.08), M.iron, 0, 0.08, 0, g);
    add(box(0.24, 0.03, 0.18), M.iron, 0, 0.015, 0, g);
    add(box(0.68, 0.42, 0.04), M.iron, 0, 0.36, 0, g);
    add(box(0.62, 0.36, 0.01), mat(screenCol), 0, 0.36, 0.022, g, { cast: false });
    return g;
  }

  function vaultDoor(parent, x = 0, y = 0, z = 0, ry = 0, openAngle = 0) {
    const g = new THREE.Group(); g.position.set(x, y, z); g.rotation.y = ry; parent.add(g);
    add(tbox(3.4, 3.6, 0.5, 2), M.stone, 0, 1.8, 0, g);
    const hinge = new THREE.Group(); hinge.position.set(-1.1, 1.7, 0.26); hinge.rotation.y = openAngle; g.add(hinge);
    const door = add(new THREE.CylinderGeometry(1.15, 1.15, 0.28, 24), mat('#6c757d'), 1.1, 0, 0, hinge);
    door.rotation.x = Math.PI / 2;
    const wheel = add(new THREE.TorusGeometry(0.36, 0.05, 8, 20), M.bronze, 1.1, 0, 0.17, hinge);
    return g;
  }

  function goldStack(parent, x = 0, y = 0, z = 0, count = 6) {
    const g = new THREE.Group(); g.position.set(x, y, z); parent.add(g);
    const goldM = mat('#f5c542');
    for (let i = 0; i < count; i++) {
      const row = Math.floor(i / 3), col = i % 3;
      add(box(0.32, 0.14, 0.16), goldM, (col - 1) * 0.36, 0.07 + row * 0.15, 0, g);
    }
    return g;
  }

  function diamondDisplay(parent, x = 0, y = 0, z = 0) {
    const g = new THREE.Group(); g.position.set(x, y, z); parent.add(g);
    add(tbox(0.9, 1.1, 0.9, 1.5), M.marble, 0, 0.55, 0, g);
    const dia = add(new THREE.OctahedronGeometry(0.26, 0), mat('#7dd3fc'), 0, 1.42, 0, g);
    return { group: g, diamond: dia };
  }

  function streetLamp(parent, x = 0, y = 0, z = 0) {
    const g = new THREE.Group(); g.position.set(x, y, z); parent.add(g);
    add(new THREE.CylinderGeometry(0.07, 0.11, 4.4, 8), M.iron, 0, 2.2, 0, g);
    add(box(0.8, 0.08, 0.08), M.iron, 0.35, 4.35, 0, g);
    add(new THREE.SphereGeometry(0.22, 10, 8), mat('#ffeaa7'), 0.7, 4.18, 0, g, { cast: false });
    return g;
  }

  function crateStack(parent, x = 0, y = 0, z = 0) {
    const g = new THREE.Group(); g.position.set(x, y, z); parent.add(g);
    add(tbox(1.1, 1.1, 1.1, 1.2), M.wood, 0, 0.55, 0, g);
    add(tbox(0.9, 0.9, 0.9, 1.2), M.plank, 0.95, 0.45, 0.2, g);
    add(tbox(0.8, 0.8, 0.8, 1.2), M.beam, 0.2, 1.5, 0.05, g);
    return g;
  }

  function airplane(parent, x = 0, y = 0, z = 0, ry = 0) {
    const g = new THREE.Group(); g.position.set(x, y, z); g.rotation.y = ry; parent.add(g);
    const bodyM = mat('#f1f5f9'), wingM = mat('#cbd5e1'), accentM = mat('#dc2626');
    const fuse = add(new THREE.CylinderGeometry(0.65, 0.55, 7.5, 16), bodyM, 0, 1.2, 0, g);
    fuse.rotation.z = Math.PI / 2;
    add(new THREE.ConeGeometry(0.65, 1.6, 16), bodyM, 4.55, 1.2, 0, g).rotation.z = -Math.PI / 2;
    add(box(1.6, 0.12, 8.2), wingM, 0.4, 1.1, 0, g);
    add(box(1.2, 1.6, 0.14), accentM, -3.2, 2.2, 0, g);
    add(box(0.9, 0.1, 2.8), wingM, -3.2, 1.4, 0, g);
    return g;
  }

  function car(parent, x = 0, y = 0, z = 0, ry = 0, col = '#e11d48') {
    const g = new THREE.Group(); g.position.set(x, y, z); g.rotation.y = ry; parent.add(g);
    const m = mat(col);
    add(box(3.6, 0.72, 1.65), m, 0, 0.56, 0, g);
    add(box(1.9, 0.58, 1.42), m, -0.15, 1.15, 0, g);
    add(box(1.65, 0.44, 1.46), mat('#1e293b'), -0.15, 1.15, 0, g, { cast: false });
    for (const wx of [-1.05, 1.05]) for (const wz of [-0.82, 0.82]) {
      const w = add(new THREE.CylinderGeometry(0.32, 0.32, 0.22, 12), mat('#111827'), wx, 0.32, wz, g);
      w.rotation.x = Math.PI / 2;
    }
    return g;
  }

  function roomBox(parent, w = 12, h = 5, d = 12, wallMat = M.plaster, floorMat = M.plank) {
    const g = new THREE.Group(); parent.add(g);
    add(tbox(w, 0.3, d, 2), floorMat, 0, -0.15, 0, g, { cast: false });
    add(tbox(w, h, 0.3, 2.5), wallMat, 0, h / 2, -d / 2, g);
    add(tbox(0.3, h, d, 2.5), wallMat, -w / 2, h / 2, 0, g);
    add(tbox(0.3, h, d, 2.5), wallMat, w / 2, h / 2, 0, g);
    return g;
  }

  return { desk, chair, monitor, vaultDoor, goldStack, diamondDisplay, streetLamp, crateStack, airplane, car, roomBox, mat };
}
