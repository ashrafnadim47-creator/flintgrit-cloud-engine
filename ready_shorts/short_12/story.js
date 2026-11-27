import words from "./words.js";

export default {
  seed: 712,
  words,
  light: "golden",
  build({ W, kit, cast, fx, makeLook, rand, clock, aim, aerial, THREE }) {
    const { at } = clock;

    // Distant snowy Quebec pine trees
    kit.hills(W, { color: "#064e3b", dist: 80 });

    // ========================================================
    // SET 1 (x: 0, z: 0) - GIANT WAREHOUSE WITH WHITE BARRELS
    // ========================================================
    kit.ground(W, { kind: "slabs", color: "#334155" });
    kit.room(W, { x: 0, z: -1, w: 10, d: 8, h: 5.0, wallColor: "#475569", floor: "slabs", floorColor: "#1e293b" });
    kit.lamp(W, { x: -3.6, z: -1.0, on: true });
    kit.lamp(W, { x: 3.6, z: -1.0, on: true });
    kit.bench(W, { x: 3.2, z: 1.5 });
    kit.rock(W, { x: -2.2, z: 3.2, s: 0.35 });
    kit.rock(W, { x: 2.2, z: 3.2, s: 0.35 });
    if (W.colliders.length > 0) W.colliders.at(-1).foreground = true;

    // Stacks of White Maple Syrup Barrels
    const barrelStack = new THREE.Group();
    const whiteBarrelMat = new THREE.MeshBasicMaterial({ color: 0xf8fafc });
    const ringMat = new THREE.MeshBasicMaterial({ color: 0x0284c7 });
    for (let row = 0; row < 3; row++) {
      for (let col = -2; col <= 2; col++) {
        const b = new THREE.Mesh(new THREE.CylinderGeometry(0.35, 0.35, 0.9, 12), whiteBarrelMat);
        b.position.set(col * 0.85, 0.5 + row * 0.95, -2.5);
        const r = new THREE.Mesh(new THREE.CylinderGeometry(0.36, 0.36, 0.1, 12), ringMat);
        r.position.set(col * 0.85, 0.5 + row * 0.95, -2.5);
        barrelStack.add(b, r);
      }
    }
    W.add(barrelStack);

    // ========================================================
    // SET 2 (x: 35, z: 0) - DRAINING INTO VATS & WATER REFILL
    // ========================================================
    kit.room(W, { x: 35, z: -1, w: 9, d: 8, h: 4.5, wallColor: "#1e293b", floor: "slabs", floorColor: "#0f172a" });
    kit.table(W, { x: 35, z: -1.0, w: 2.8, d: 1.2, h: 0.9, cloth: "#b45309" });
    kit.lamp(W, { x: 31.5, z: -1.0, on: true });
    kit.lamp(W, { x: 38.5, z: -1.0, on: true });
    kit.bench(W, { x: 38.5, z: 1.5 });
    kit.rock(W, { x: 33, z: 3.2, s: 0.35 });
    if (W.colliders.length > 0) W.colliders.at(-1).foreground = true;

    // Plastic Vat of Amber Maple Syrup
    const vatGroup = new THREE.Group();
    const vatMat = new THREE.MeshBasicMaterial({ color: 0xe2e8f0 });
    const syrupMat = new THREE.MeshBasicMaterial({ color: 0xb45309 });
    const vat = new THREE.Mesh(new THREE.CylinderGeometry(1.2, 1.2, 1.2, 16), vatMat);
    vat.position.set(35, 0.7, -1.0);
    const liquid = new THREE.Mesh(new THREE.CylinderGeometry(1.15, 1.15, 0.2, 16), syrupMat);
    liquid.position.set(35, 1.25, -1.0);
    vatGroup.add(vat, liquid);
    W.add(vatGroup);

    // ========================================================
    // SET 3 (x: -35, z: 0) - INSPECTOR FALLING ON EMPTY BARREL
    // ========================================================
    kit.room(W, { x: -35, z: 0, w: 10, d: 8, h: 4.5, wallColor: "#0f172a", floor: "slabs", floorColor: "#020617" });
    kit.barrel(W, { x: -38, z: -1.8 });
    kit.crate(W, { x: -38, z: 0.8 });
    kit.rock(W, { x: -36, z: 3.0, s: 0.45 });
    kit.rock(W, { x: -33, z: 2.8, s: 0.4 });
    if (W.colliders.length > 0) W.colliders.at(-1).foreground = true;

    // Single Tipped-Over Empty White Barrel
    const emptyBarrelGroup = new THREE.Group();
    const emptyB = new THREE.Mesh(new THREE.CylinderGeometry(0.4, 0.4, 1.0, 12), whiteBarrelMat);
    emptyB.rotation.z = Math.PI / 2;
    emptyB.position.set(-35, 0.4, -0.5);
    emptyBarrelGroup.add(emptyB);
    W.add(emptyBarrelGroup);

    // ========================================================
    // SET 4 (x: 0, z: 35) - POLICE CATCHING MAPLE MAFIA
    // ========================================================
    kit.ground(W, { kind: "slabs", color: "#1e1b4b" });
    kit.room(W, { x: 0, z: 35, w: 12, d: 8, h: 4.5, wallColor: "#0f172a", floor: "slabs", floorColor: "#1e1b4b" });
    kit.barrel(W, { x: -4.5, z: 33.5 });
    kit.crate(W, { x: -4.5, z: 35.5 });
    kit.rock(W, { x: 4.5, z: 36.0, s: 0.4 });
    if (W.colliders.length > 0) W.colliders.at(-1).foreground = true;

    // ========================================================
    // CHARACTERS
    // ========================================================
    const thief = cast.add({
      name: "thief",
      look: makeLook(rand.fork(1), "adult", {
        torso: "#b91c1c", // Canadian red flannel plaid shirt
        pants: "#1e293b",
        skin: "#fde047",
        hat: "beanie",
        hatColor: "#1e293b",
        mustache: true,
        build: 1.15
      }),
      pos: [0, 0.8],
      h: 1.78
    });

    const inspector = cast.add({
      name: "inspector",
      look: makeLook(rand.fork(2), "adult", {
        torso: "#e2e8f0", // White lab coat / inspector
        pants: "#475569",
        skin: "#f8fafc",
        glasses: true,
        build: 1.05
      }),
      pos: [36.2, 0.8],
      h: 1.74
    });

    // ========================================================
    // TIMELINE & CHOREOGRAPHY
    // ========================================================

    inspector.hide(0);

    // SCENE 1: HOOK [0.00s - 6.50s]
    thief.place(0, [0, 0.8]);
    thief.face(0, "smug").arms(0, "hips");
    thief.turn(0, "left");

    thief.face(at("history."), "laugh").arms(at("history."), "armsUp");
    thief.hop(at("history."), 0.25);
    fx.add("stars", at("history."), at("history.") + 1.8, [0, 2.2, 0.8], { size: 0.8, color: "#f59e0b" });

    // SCENE 2: QUEBEC STRATEGIC RESERVE [6.50s - 12.00s]
    thief.face(at("Quebec,"), "neutral").arms(at("Quebec,"), "point");
    thief.face(at("supply."), "smug").arms(at("supply."), "hold");

    // SCENE 3: DRAINING LIQUID GOLD & TAP WATER REFILL [12.00s - 18.00s]
    thief.place(at("Over") - 0.1, [34.0, 0.8]);
    thief.face(at("Over"), "grin").arms(at("Over"), "reach");
    thief.turn(at("Over"), "right");

    thief.face(at("water,"), "laugh").arms(at("water,"), "hold");
    fx.emit("dust", at("water,"), at("back."), [35, 1.4, -0.8], { size: 0.3, spread: 0.3, count: 8, color: "#38bdf8" });

    // SCENE 4: INSPECTOR FALLING [18.00s - 24.50s]
    thief.hide(at("scheme") - 0.1);
    inspector.show(at("scheme") - 0.1);
    inspector.place(at("scheme") - 0.1, [-35.0, 0.8]);
    inspector.face(at("scheme"), "neutral").arms(at("scheme"), "think");
    inspector.turn(at("scheme"), "left");

    inspector.face(at("fell"), "surprised").arms(at("fell"), "facepalm");
    inspector.hop(at("fell"), 0.3);
    fx.add("sweat", at("fell"), at("fell") + 2.0, [-35.0, 2.2, 0.8], { size: 0.7, color: "#38bdf8" });

    // SCENE 5: TEN THOUSAND BARRELS SUCKED DRY [24.50s - 30.50s]
    inspector.face(at("Nearly"), "worried").arms(at("Nearly"), "armsUp");
    inspector.face(at("mafia."), "facepalm").arms(at("mafia."), "facepalm");

    // SCENE 6: ABSURD MULTI-MILLION HEIST [30.50s - end]
    thief.show(at("remains") - 0.1);
    thief.place(at("remains") - 0.1, [0, 35.8]);
    thief.face(at("remains"), "smug").arms(at("remains"), "armsUp");
    thief.hop(at("recorded."), 0.25);
    fx.add("stars", at("recorded."), at("recorded.") + 2.5, [0, 2.2, 35.8], { size: 1.0, color: "#f59e0b" });

    // ========================================================
    // CAMERA CHOREOGRAPHY
    // ========================================================
    const camera = [
      // Shot 1: Warehouse Hook
      {
        t: 0,
        pos: [0, 1.8, 4.4],
        look: [0, 1.4, 0.8],
        fov: 38,
        move: "push",
        push: 0.0022,
        light: "golden"
      },
      // Shot 2: Strategic Reserve Barrels
      {
        t: at("Quebec,"),
        pos: [0, 1.6, 4.2],
        look: [0, 1.3, -1.5],
        fov: 38,
        move: "push",
        push: 0.0018,
        light: "interior",
        transition: "whip"
      },
      // Shot 3: Draining Liquid Gold
      {
        t: at("Over"),
        pos: [35, 1.7, 4.0],
        look: [35, 1.3, 0.8],
        fov: 36,
        move: "push",
        push: 0.0020,
        light: "interior",
        transition: "flash"
      },
      // Shot 4: Inspector Leaning on Empty Barrel
      {
        t: at("scheme"),
        pos: [-35, 1.6, 4.0],
        look: [-35, 1.2, 0.5],
        fov: 36,
        move: "push",
        push: 0.0022,
        light: "interior",
        transition: "whip"
      },
      // Shot 5: Sucked Dry
      {
        t: at("Nearly"),
        pos: [-35, 1.5, 3.8],
        look: [-35, 1.2, 0.5],
        fov: 36,
        move: "push",
        push: 0.0018,
        light: "cold",
        transition: "flash"
      },
      // Shot 6: Most Absurd Heist
      {
        t: at("remains"),
        pos: [0, 1.8, 39.8],
        look: [0, 1.5, 35.8],
        fov: 38,
        move: "pull",
        push: -0.0020,
        light: "golden",
        transition: "flash"
      }
    ];

    const kicks = [
      { t: at("syrup"), amp: 0.06 },
      { t: at("fell"), amp: 0.08 },
      { t: at("recorded."), amp: 0.07 }
    ];

    return { camera, kicks };
  }
};
