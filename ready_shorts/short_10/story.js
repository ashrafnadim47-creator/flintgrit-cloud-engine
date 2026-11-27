import words from "./words.js";

export default {
  seed: 512,
  words,
  light: "night",
  build({ W, kit, cast, fx, makeLook, rand, clock, aim, aerial, THREE }) {
    const { at } = clock;

    // Distant underground vault walls
    kit.hills(W, { color: "#0f172a", dist: 80 });

    // ========================================================
    // SET 1 (x: 0, z: 0) - ANTWERP DIAMOND VAULT EXTERIOR & STEEL DOOR
    // ========================================================
    kit.ground(W, { kind: "slabs", color: "#1e293b" });
    kit.room(W, { x: 0, z: -1, w: 9, d: 8, h: 4.5, wallColor: "#334155", floor: "slabs", floorColor: "#0f172a" });
    kit.lamp(W, { x: -3.6, z: -1.0, on: true });
    kit.lamp(W, { x: 3.6, z: -1.0, on: true });
    kit.bench(W, { x: 3.2, z: 1.5 });
    kit.rock(W, { x: -2.2, z: 3.2, s: 0.35 });
    kit.rock(W, { x: 2.2, z: 3.2, s: 0.35 });
    if (W.colliders.length > 0) W.colliders.at(-1).foreground = true;

    // Massive Steel Vault Door & Combination Dial
    const vaultGroup = new THREE.Group();
    const steelMat = new THREE.MeshBasicMaterial({ color: 0x475569 });
    const dialMat = new THREE.MeshBasicMaterial({ color: 0xf1f5f9 });
    const door = new THREE.Mesh(new THREE.CylinderGeometry(2.2, 2.2, 0.4, 24), steelMat);
    door.rotation.x = Math.PI / 2;
    door.position.set(0, 2.2, -4.5);
    const dial = new THREE.Mesh(new THREE.CylinderGeometry(0.5, 0.5, 0.1, 16), dialMat);
    dial.rotation.x = Math.PI / 2;
    dial.position.set(0, 2.2, -4.2);
    vaultGroup.add(door, dial);
    W.add(vaultGroup);

    // ========================================================
    // SET 2 (x: 35, z: 0) - INFRARED SENSOR & HAIRSPRAY CAN
    // ========================================================
    kit.room(W, { x: 35, z: -1, w: 9, d: 8, h: 4.5, wallColor: "#1e293b", floor: "slabs", floorColor: "#0f172a" });
    kit.table(W, { x: 35, z: -1.0, w: 2.8, d: 1.2, h: 0.9, cloth: "#334155" });
    kit.lamp(W, { x: 31.5, z: -1.0, on: true });
    kit.lamp(W, { x: 38.5, z: -1.0, on: true });
    kit.bench(W, { x: 38.5, z: 1.5 });
    kit.rock(W, { x: 33, z: 3.2, s: 0.35 });
    if (W.colliders.length > 0) W.colliders.at(-1).foreground = true;

    // Ceiling Infrared Heat Sensor & Hairspray Spray Can
    const sensorGroup = new THREE.Group();
    const sensorMat = new THREE.MeshBasicMaterial({ color: 0xef4444 });
    const sensor = new THREE.Mesh(new THREE.CylinderGeometry(0.25, 0.25, 0.4, 12), sensorMat);
    sensor.position.set(35, 3.5, 0);
    const canMat = new THREE.MeshBasicMaterial({ color: 0xec4899 });
    const sprayCan = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.12, 0.6, 12), canMat);
    sprayCan.position.set(34.8, 2.8, 0.2);
    sensorGroup.add(sensor, sprayCan);
    W.add(sensorGroup);

    // ========================================================
    // SET 3 (x: -35, z: 0) - VAULT DEPOSIT BOXES & DIAMOND PILES
    // ========================================================
    kit.room(W, { x: -35, z: 0, w: 10, d: 8, h: 4.5, wallColor: "#0f172a", floor: "slabs", floorColor: "#020617" });
    kit.table(W, { x: -35, z: -1.0, w: 2.8, d: 1.2, h: 0.9, cloth: "#1e293b" });
    kit.barrel(W, { x: -38, z: -1.8 });
    kit.crate(W, { x: -38, z: 0.8 });
    kit.rock(W, { x: -36, z: 3.0, s: 0.45 });
    kit.rock(W, { x: -33, z: 2.8, s: 0.4 });
    if (W.colliders.length > 0) W.colliders.at(-1).foreground = true;

    // Deposit Boxes Wall & Sparkling Diamond Cache
    const boxGroup = new THREE.Group();
    const boxMat = new THREE.MeshBasicMaterial({ color: 0x94a3b8 });
    const gemMat = new THREE.MeshBasicMaterial({ color: 0x38bdf8 });
    for (let r = 0; r < 3; r++) {
      for (let c = -1; c <= 1; c++) {
        const b = new THREE.Mesh(new THREE.BoxGeometry(0.8, 0.4, 0.5), boxMat);
        b.position.set(-35 + c * 0.9, 1.8 + r * 0.6, -2.5);
        boxGroup.add(b);
      }
    }
    const gemPile = new THREE.Mesh(new THREE.ConeGeometry(0.6, 0.5, 8), gemMat);
    gemPile.position.set(-35, 1.0, -1.0);
    boxGroup.add(gemPile);
    W.add(boxGroup);

    // ========================================================
    // SET 4 (x: 0, z: 35) - MIDNIGHT ESCAPE WITH DUFFEL BAGS
    // ========================================================
    kit.ground(W, { kind: "slabs", color: "#0f172a" });
    kit.room(W, { x: 0, z: 35, w: 12, d: 8, h: 4.5, wallColor: "#020617", floor: "slabs", floorColor: "#0f172a" });
    kit.barrel(W, { x: -4.5, z: 33.5 });
    kit.crate(W, { x: -4.5, z: 35.5 });
    kit.rock(W, { x: 4.5, z: 36.0, s: 0.4 });
    if (W.colliders.length > 0) W.colliders.at(-1).foreground = true;

    // ========================================================
    // CHARACTERS
    // ========================================================
    const leo = cast.add({
      name: "leo",
      look: makeLook(rand.fork(1), "adult", {
        torso: "#0f172a", // Black stealth turtleneck
        pants: "#1e293b",
        skin: "#fde047",
        hair: "#0f172a",
        hairStyle: "short",
        build: 1.05
      }),
      pos: [0, 0.8],
      h: 1.76
    });

    const guard = cast.add({
      name: "guard",
      look: makeLook(rand.fork(2), "adult", {
        torso: "#1e3a8a", // Belgian Security Police
        pants: "#172554",
        skin: "#f8fafc",
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

    // SCENE 1: VAULT HOOK [0.00s - 6.50s]
    leo.place(0, [0, 0.8]);
    leo.face(0, "determined").arms(0, "hold");
    leo.turn(0, "left");

    leo.face(at("hairspray."), "smug").arms(at("hairspray."), "point");
    leo.hop(at("hairspray."), 0.2);
    fx.add("stars", at("hairspray."), at("hairspray.") + 1.8, [0, 2.2, 0.8], { size: 0.7, color: "#38bdf8" });

    // SCENE 2: TEN LAYERS OF SECURITY [6.50s - 12.00s]
    leo.face(at("Antwerp,"), "neutral").arms(at("Antwerp,"), "think");
    leo.face(at("radar."), "worried").arms(at("radar."), "armsUp");

    // SCENE 3: HAIRSPRAY COATING SENSOR [12.00s - 18.00s]
    leo.place(at("bypass") - 0.1, [34.2, 0.8]);
    leo.face(at("bypass"), "determined").arms(at("bypass"), "reach");
    leo.turn(at("bypass"), "right");
    fx.emit("dust", at("coated"), at("vision."), [35, 3.2, 0.1], { size: 0.3, spread: 0.4, count: 12, color: "#ec4899" });

    // SCENE 4: ALUMINUM TAPE ON MAGNETIC SENSORS [18.00s - 23.50s]
    leo.face(at("taped"), "smug").arms(at("taped"), "hold");
    leo.hop(at("open."), 0.2);

    // SCENE 5: EMPTIED 100 BOXES & DIAMONDS [23.50s - 29.50s]
    leo.place(at("emptied") - 0.1, [-34.8, 0.8]);
    leo.face(at("emptied"), "grin").arms(at("emptied"), "reach");
    leo.turn(at("emptied"), "left");

    leo.face(at("diamonds"), "laugh").arms(at("diamonds"), "armsUp");
    leo.hop(at("diamonds"), 0.25);
    fx.add("stars", at("diamonds"), at("diamonds") + 2.0, [-34.8, 2.2, -0.8], { size: 0.9, color: "#38bdf8" });

    // SCENE 6: WALKING OUT CLEAN [29.50s - end]
    leo.place(at("walked") - 0.1, [0, 35.8]);
    leo.face(at("walked"), "smug").arms(at("walked"), "wave");
    leo.turn(at("walked"), "right");

    guard.show(at("history.") - 0.1);
    guard.place(at("history.") - 0.1, [-2.5, 35.8]);
    guard.face(at("history."), "facepalm").arms(at("history."), "facepalm");
    fx.add("sweat", at("history."), at("history.") + 2.0, [-2.5, 2.2, 35.8], { size: 0.6, color: "#38bdf8" });

    // ========================================================
    // CAMERA CHOREOGRAPHY
    // ========================================================
    const camera = [
      // Shot 1: Vault Hook
      {
        t: 0,
        pos: [0, 1.6, 4.2],
        look: [0, 1.4, 0.8],
        fov: 38,
        move: "push",
        push: 0.0022,
        light: "night"
      },
      // Shot 2: High-Tech Security
      {
        t: at("Antwerp,"),
        pos: [0, 1.8, 4.8],
        look: [0, 1.3, -2.5],
        fov: 40,
        move: "push",
        push: 0.0018,
        light: "night",
        transition: "whip"
      },
      // Shot 3: Hairspray Blinding Lens
      {
        t: at("bypass"),
        pos: [35, 2.2, 3.8],
        look: [35, 2.4, 0.2],
        fov: 34,
        move: "push",
        push: 0.0020,
        light: "night",
        transition: "flash"
      },
      // Shot 4: Aluminum Tape
      {
        t: at("taped"),
        pos: [35, 1.6, 4.2],
        look: [35, 1.3, 0.8],
        fov: 36,
        move: "push",
        push: 0.0018,
        light: "interior",
        transition: "whip"
      },
      // Shot 5: Emptying Boxes & Diamonds
      {
        t: at("emptied"),
        pos: [-35, 1.6, 4.0],
        look: [-35, 1.2, -1.0],
        fov: 36,
        move: "push",
        push: 0.0022,
        light: "interior",
        transition: "flash"
      },
      // Shot 6: Cleanest Diamond Heist
      {
        t: at("walked"),
        pos: [0, 1.8, 39.8],
        look: [0, 1.5, 35.8],
        fov: 38,
        move: "pull",
        push: -0.0020,
        light: "night",
        transition: "whip"
      }
    ];

    const kicks = [
      { t: at("hairspray."), amp: 0.06 },
      { t: at("diamonds"), amp: 0.07 },
      { t: at("history."), amp: 0.07 }
    ];

    return { camera, kicks };
  }
};
