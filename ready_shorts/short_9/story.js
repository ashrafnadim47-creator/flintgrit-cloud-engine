import words from "./words.js";

export default {
  seed: 412,
  words,
  light: "night",
  build({ W, kit, cast, fx, makeLook, rand, clock, aim, aerial, THREE }) {
    const { at } = clock;

    // Distant dark San Francisco bay hills
    kit.hills(W, { color: "#091e3a", dist: 80 });

    // ========================================================
    // SET 1 (x: 0, z: 0) - ALCATRAZ PRISON CELL & SPOON HOLE
    // ========================================================
    kit.ground(W, { kind: "slabs", color: "#334155" });
    kit.room(W, { x: 0, z: -1, w: 9, d: 8, h: 4.5, wallColor: "#334155", floor: "slabs", floorColor: "#1e293b" });
    kit.table(W, { x: 2.5, z: -1.2, w: 2.2, d: 1.1, h: 0.9, cloth: "#475569" });
    kit.lamp(W, { x: -3.6, z: -1.0, on: true });
    kit.lamp(W, { x: 3.6, z: -1.0, on: true });
    kit.bench(W, { x: 3.2, z: 1.5 });
    kit.rock(W, { x: -2.2, z: 3.2, s: 0.35 });
    kit.rock(W, { x: 2.2, z: 3.2, s: 0.35 });
    if (W.colliders.length > 0) W.colliders.at(-1).foreground = true;

    // Iron Prison Bars (Front)
    const cellBars = new THREE.Group();
    const ironMat = new THREE.MeshBasicMaterial({ color: 0x1e293b });
    for (let x = -3.5; x <= 3.5; x += 0.5) {
      if (Math.abs(x) > 1.0) {
        const bar = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.05, 4.5, 8), ironMat);
        bar.position.set(x, 2.25, 2.8);
        cellBars.add(bar);
      }
    }
    // Spoon Digging Vent Hole in Wall
    const ventMat = new THREE.MeshBasicMaterial({ color: 0x020617 });
    const ventHole = new THREE.Mesh(new THREE.BoxGeometry(1.2, 0.8, 0.2), ventMat);
    ventHole.position.set(0, 0.8, -4.8);
    cellBars.add(ventHole);
    W.add(cellBars);

    // ========================================================
    // SET 2 (x: 35, z: 0) - DECOY DUMMY HEAD BED CELL
    // ========================================================
    kit.room(W, { x: 35, z: -1, w: 9, d: 8, h: 4.5, wallColor: "#1e293b", floor: "slabs", floorColor: "#0f172a" });
    kit.table(W, { x: 35, z: -1.0, w: 2.8, d: 1.2, h: 0.9, cloth: "#334155" });
    kit.lamp(W, { x: 31.5, z: -1.0, on: true });
    kit.lamp(W, { x: 38.5, z: -1.0, on: true });
    kit.bench(W, { x: 38.5, z: 1.5 });
    kit.rock(W, { x: 33, z: 3.2, s: 0.35 });
    if (W.colliders.length > 0) W.colliders.at(-1).foreground = true;

    // Bed with Blanket & Dummy Head
    const bedGroup = new THREE.Group();
    const bedMat = new THREE.MeshBasicMaterial({ color: 0x475569 });
    const dummyMat = new THREE.MeshBasicMaterial({ color: 0xfde047 });
    const hairMat = new THREE.MeshBasicMaterial({ color: 0x18181b });

    const bed = new THREE.Mesh(new THREE.BoxGeometry(2.4, 0.6, 3.6), bedMat);
    bed.position.set(35, 0.6, -1.0);
    const pillow = new THREE.Mesh(new THREE.BoxGeometry(1.8, 0.25, 1.0), new THREE.MeshBasicMaterial({ color: 0xf1f5f9 }));
    pillow.position.set(35, 0.95, -2.2);
    const dummyHead = new THREE.Mesh(new THREE.SphereGeometry(0.38, 12, 12), dummyMat);
    dummyHead.position.set(35, 1.2, -2.1);
    const realHair = new THREE.Mesh(new THREE.SphereGeometry(0.35, 12, 12), hairMat);
    realHair.position.set(35, 1.35, -2.2);
    bedGroup.add(bed, pillow, dummyHead, realHair);
    W.add(bedGroup);

    // ========================================================
    // SET 3 (x: -35, z: 0) - ROCKY ISLAND SHORE & RAINCOAT RAFT
    // ========================================================
    kit.room(W, { x: -35, z: 0, w: 10, d: 8, h: 4.5, wallColor: "#0f172a", floor: "slabs", floorColor: "#020617" });
    kit.barrel(W, { x: -38, z: -1.8 });
    kit.crate(W, { x: -38, z: 0.8 });
    kit.rock(W, { x: -36, z: 3.0, s: 0.45 });
    kit.rock(W, { x: -33, z: 2.8, s: 0.4 });
    if (W.colliders.length > 0) W.colliders.at(-1).foreground = true;

    // Green Inflatable Raincoat Raft
    const raftGroup = new THREE.Group();
    const raftMat = new THREE.MeshBasicMaterial({ color: 0x15803d });
    const paddleMat = new THREE.MeshBasicMaterial({ color: 0x78350f });

    const raft = new THREE.Mesh(new THREE.CylinderGeometry(1.5, 1.5, 0.35, 16), raftMat);
    raft.position.set(-35, 0.3, 0.5);
    const paddle1 = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.06, 2.0, 8), paddleMat);
    paddle1.position.set(-36.2, 0.4, 0.5);
    const paddle2 = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.06, 2.0, 8), paddleMat);
    paddle2.position.set(-33.8, 0.4, 0.5);
    raftGroup.add(raft, paddle1, paddle2);
    W.add(raftGroup);

    // ========================================================
    // SET 4 (x: 0, z: 35) - SAN FRANCISCO FREEZING BAY & FBI SEARCH
    // ========================================================
    kit.ground(W, { kind: "slabs", color: "#082f49" });
    kit.room(W, { x: 0, z: 35, w: 12, d: 8, h: 4.5, wallColor: "#0f172a", floor: "slabs", floorColor: "#082f49" });
    kit.barrel(W, { x: -4.5, z: 33.5 });
    kit.crate(W, { x: -4.5, z: 35.5 });
    kit.rock(W, { x: 4.5, z: 36.0, s: 0.4 });
    if (W.colliders.length > 0) W.colliders.at(-1).foreground = true;

    // Distant Lighthouse Searchlight Beacon
    const lightGroup = new THREE.Group();
    const towerMat = new THREE.MeshBasicMaterial({ color: 0xe2e8f0 });
    const beamMat = new THREE.MeshBasicMaterial({ color: 0xfef08a, transparent: true, opacity: 0.35 });
    const tower = new THREE.Mesh(new THREE.CylinderGeometry(0.4, 0.6, 5.0, 10), towerMat);
    tower.position.set(4.0, 2.5, 31.0);
    const beam = new THREE.Mesh(new THREE.ConeGeometry(2.0, 7.0, 16), beamMat);
    beam.position.set(2.0, 2.5, 33.0);
    beam.rotation.z = Math.PI / 3;
    lightGroup.add(tower, beam);
    W.add(lightGroup);

    // ========================================================
    // CHARACTERS
    // ========================================================
    const frank = cast.add({
      name: "frank",
      look: makeLook(rand.fork(1), "adult", {
        torso: "#e2e8f0", // Convict stripe shirt
        pants: "#475569",
        skin: "#f8fafc",
        hair: "#1e293b",
        hairStyle: "short",
        build: 1.05
      }),
      pos: [0, 0.8],
      h: 1.76
    });

    const guard = cast.add({
      name: "guard",
      look: makeLook(rand.fork(2), "adult", {
        torso: "#1e3a8a", // Navy Guard uniform
        pants: "#172554",
        skin: "#fde047",
        hat: "cap",
        hatColor: "#1e3a8a",
        mustache: true,
        build: 1.15
      }),
      pos: [36.2, 0.8],
      h: 1.82
    });

    // ========================================================
    // TIMELINE & CHOREOGRAPHY
    // ========================================================

    guard.hide(0);

    // SCENE 1: PRISON CELL HOOK [0.00s - 6.50s]
    frank.place(0, [0, 0.8]);
    frank.face(0, "determined").arms(0, "hold");
    frank.turn(0, "left");

    frank.face(at("spoons."), "smug").arms(at("spoons."), "point");
    frank.hop(at("spoons."), 0.2);
    fx.add("stars", at("spoons."), at("spoons.") + 1.8, [0, 2.2, 0.8], { size: 0.7, color: "#38bdf8" });

    // SCENE 2: SCRAPING CONCRETE WITH SPOON [6.50s - 12.50s]
    frank.face(at("straight"), "neutral").arms(at("straight"), "reach");
    frank.face(at("concrete"), "determined").arms(at("concrete"), "hold");
    fx.emit("dust", at("scraped"), at("vents."), [0, 0.9, -4.5], { size: 0.4, spread: 0.5, count: 8, color: "#94a3b8" });

    // SCENE 3: DUMMY HEAD BED & NIGHT PATROL GUARD [12.50s - 19.50s]
    frank.hide(at("guards") - 0.1);
    guard.show(at("guards") - 0.1);
    guard.place(at("guards"), [33.5, 0.8]);
    guard.face(at("guards"), "neutral").arms(at("guards"), "lantern");
    guard.turn(at("guards"), "right");

    guard.face(at("toilet"), "thinking").arms(at("toilet"), "think");
    guard.face(at("barber"), "neutral").arms(at("barber"), "nod");

    // SCENE 4: SLIPPING INTO CORRIDOR [19.50s - 25.50s]
    guard.hide(at("stuffing") - 0.1);
    frank.show(at("stuffing") - 0.1);
    frank.place(at("stuffing") - 0.1, [-34.2, 0.8]);
    frank.face(at("stuffing"), "neutral").arms(at("stuffing"), "reach");
    frank.turn(at("stuffing"), "right");

    frank.face(at("corridor"), "determined").arms(at("corridor"), "run");
    frank.hop(at("roof."), 0.2);

    // SCENE 5: RAFT ON SHORELINE [25.50s - 31.50s]
    frank.place(at("shoreline,") - 0.1, [-35.0, 0.8]);
    frank.face(at("shoreline,"), "determined").arms(at("shoreline,"), "hold");
    frank.face(at("raincoats."), "smug").arms(at("raincoats."), "armsUp");
    fx.add("burst", at("raincoats."), at("raincoats.") + 1.5, [-35.0, 1.4, 0.5], { size: 0.8, color: "#22c55e" });

    // SCENE 6: FREEZING BAY & FBI HUNT [31.50s - end]
    frank.hide(at("vanished") - 0.1);
    guard.show(at("vanished") - 0.1);
    guard.place(at("vanished") - 0.1, [0, 35.8]);
    guard.face(at("vanished"), "surprised").arms(at("vanished"), "facepalm");
    guard.turn(at("vanished"), "left");

    guard.face(at("FBI"), "worried").arms(at("FBI"), "lookout");
    fx.add("sweat", at("hunting"), at("hunting") + 2.0, [0, 2.2, 35.8], { size: 0.6, color: "#38bdf8" });

    guard.face(at("impossible."), "surprised").arms(at("impossible."), "armsUp");

    // ========================================================
    // CAMERA CHOREOGRAPHY
    // ========================================================
    const camera = [
      // Shot 1: Prison Cell Hook
      {
        t: 0,
        pos: [0, 1.6, 4.2],
        look: [0, 1.4, 0.8],
        fov: 38,
        move: "push",
        push: 0.0022,
        light: "night"
      },
      // Shot 2: Scraping Vent Hole
      {
        t: at("straight"),
        pos: [0, 1.2, 2.8],
        look: [0, 0.9, -2.5],
        fov: 35,
        move: "push",
        push: 0.0018,
        light: "night",
        transition: "whip"
      },
      // Shot 3: Decoy Head Bed & Guard
      {
        t: at("guards"),
        pos: [35, 1.7, 4.4],
        look: [35, 1.4, 0.8],
        fov: 38,
        move: "push",
        push: 0.0018,
        light: "interior",
        transition: "whip"
      },
      // Shot 4: Slipping to Corridor
      {
        t: at("stuffing"),
        pos: [-35, 1.6, 4.2],
        look: [-35, 1.3, 0.8],
        fov: 36,
        move: "push",
        push: 0.0020,
        light: "night",
        transition: "flash"
      },
      // Shot 5: Raft on Shoreline
      {
        t: at("shoreline,"),
        pos: [-35, 1.5, 4.0],
        look: [-35, 1.2, 0.5],
        fov: 38,
        move: "push",
        push: 0.0022,
        light: "night",
        transition: "whip"
      },
      // Shot 6: FBI Hunt on San Francisco Bay
      {
        t: at("vanished"),
        pos: [0, 1.8, 39.8],
        look: [0, 1.5, 35.8],
        fov: 38,
        move: "pull",
        push: -0.0020,
        light: "night",
        transition: "flash"
      }
    ];

    const kicks = [
      { t: at("spoons."), amp: 0.06 },
      { t: at("impossible."), amp: 0.07 }
    ];

    return { camera, kicks };
  }
};
