import words from "./words.js";

export default {
  seed: 612,
  words,
  light: "golden",
  build({ W, kit, cast, fx, makeLook, rand, clock, aim, aerial, THREE }) {
    const { at } = clock;

    // Distant tropical horizon
    kit.hills(W, { color: "#14532d", dist: 80 });

    // ========================================================
    // SET 1 (x: 0, z: 0) - EMPTY DESERT DUST & FAKE RUNWAY SIGN
    // ========================================================
    kit.ground(W, { kind: "sand", color: "#d97706" });
    kit.room(W, { x: 0, z: -1, w: 9, d: 8, h: 4.5, wallColor: "#78350f", floor: "sand", floorColor: "#b45309" });
    kit.lamp(W, { x: -3.6, z: -1.0, on: true });
    kit.lamp(W, { x: 3.6, z: -1.0, on: true });
    kit.bench(W, { x: 3.2, z: 1.5 });
    kit.rock(W, { x: -2.2, z: 3.2, s: 0.35 });
    kit.rock(W, { x: 2.2, z: 3.2, s: 0.35 });
    if (W.colliders.length > 0) W.colliders.at(-1).foreground = true;

    // Wooden Billboard "ABUJA INTERNATIONAL AIRPORT - UNDER CONSTRUCTION"
    const signGroup = new THREE.Group();
    const woodMat = new THREE.MeshBasicMaterial({ color: 0x78350f });
    const boardMat = new THREE.MeshBasicMaterial({ color: 0xfef08a });
    const post1 = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.08, 3.5, 8), woodMat);
    post1.position.set(-1.5, 1.75, -2.5);
    const post2 = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.08, 3.5, 8), woodMat);
    post2.position.set(1.5, 1.75, -2.5);
    const board = new THREE.Mesh(new THREE.BoxGeometry(3.6, 1.8, 0.1), boardMat);
    board.position.set(0, 2.5, -2.5);
    signGroup.add(post1, post2, board);
    W.add(signGroup);

    // ========================================================
    // SET 2 (x: 35, z: 0) - BRAZILIAN BANK BOARDROOM
    // ========================================================
    kit.room(W, { x: 35, z: -1, w: 9, d: 8, h: 4.5, wallColor: "#1e3a8a", floor: "planks", floorColor: "#172554" });
    kit.table(W, { x: 35, z: -1.0, w: 3.2, d: 1.4, h: 0.9, cloth: "#1e293b" });
    kit.lamp(W, { x: 31.5, z: -1.0, on: true });
    kit.lamp(W, { x: 38.5, z: -1.0, on: true });
    kit.bench(W, { x: 38.5, z: 1.5 });
    kit.rock(W, { x: 33, z: 3.2, s: 0.35 });
    if (W.colliders.length > 0) W.colliders.at(-1).foreground = true;

    // Golden Telephone & Fake Wire Transfer Docs
    const phoneGroup = new THREE.Group();
    const phoneMat = new THREE.MeshBasicMaterial({ color: 0xf59e0b });
    const phone = new THREE.Mesh(new THREE.BoxGeometry(0.4, 0.25, 0.3), phoneMat);
    phone.position.set(34.8, 0.98, -1.0);
    phoneGroup.add(phone);
    W.add(phoneGroup);

    // ========================================================
    // SET 3 (x: -35, z: 0) - SWISS BANK ACCOUNTS & CASH STACKS
    // ========================================================
    kit.room(W, { x: -35, z: 0, w: 10, d: 8, h: 4.5, wallColor: "#0f172a", floor: "slabs", floorColor: "#020617" });
    kit.table(W, { x: -35, z: -1.0, w: 2.8, d: 1.2, h: 0.9, cloth: "#166534" });
    kit.barrel(W, { x: -38, z: -1.8 });
    kit.crate(W, { x: -38, z: 0.8 });
    kit.rock(W, { x: -36, z: 3.0, s: 0.45 });
    kit.rock(W, { x: -33, z: 2.8, s: 0.4 });
    if (W.colliders.length > 0) W.colliders.at(-1).foreground = true;

    // Giant Stacks of Cash
    const cashGroup = new THREE.Group();
    const cashMat = new THREE.MeshBasicMaterial({ color: 0x22c55e });
    for (let i = 0; i < 4; i++) {
      const c = new THREE.Mesh(new THREE.BoxGeometry(0.8, 0.3, 0.5), cashMat);
      c.position.set(-35, 1.05 + i * 0.32, -1.0);
      cashGroup.add(c);
    }
    W.add(cashGroup);

    // ========================================================
    // SET 4 (x: 0, z: 35) - AUDITORS LOOKING AT EMPTY WORLD MAP
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
    const emmanuel = cast.add({
      name: "emmanuel",
      look: makeLook(rand.fork(1), "adult", {
        torso: "#ffffff", // Pure white sharp business suit
        pants: "#ffffff",
        skin: "#78350f",
        hair: "#0f172a",
        hairStyle: "short",
        glasses: true,
        build: 1.1
      }),
      pos: [0, 0.8],
      h: 1.78
    });

    const banker = cast.add({
      name: "banker",
      look: makeLook(rand.fork(2), "adult", {
        torso: "#1e3a8a", // Navy banker suit
        pants: "#172554",
        skin: "#fde047",
        mustache: true,
        build: 1.15
      }),
      pos: [36.2, 0.8],
      h: 1.82
    });

    // ========================================================
    // TIMELINE & CHOREOGRAPHY
    // ========================================================

    banker.hide(0);

    // SCENE 1: HOOK [0.00s - 6.50s]
    emmanuel.place(0, [0, 0.8]);
    emmanuel.face(0, "smug").arms(0, "hips");
    emmanuel.turn(0, "left");

    emmanuel.face(at("dollars."), "laugh").arms(at("dollars."), "armsUp");
    emmanuel.hop(at("dollars."), 0.25);
    fx.add("stars", at("dollars."), at("dollars.") + 1.8, [0, 2.2, 0.8], { size: 0.8, color: "#f59e0b" });

    // SCENE 2: CALLING THE BANKER [6.50s - 12.00s]
    emmanuel.place(at("Emmanuel") - 0.1, [34.0, 0.8]);
    emmanuel.face(at("Emmanuel"), "neutral").arms(at("Emmanuel"), "point");
    emmanuel.turn(at("Emmanuel"), "right");

    banker.show(at("Emmanuel") - 0.1);
    banker.place(at("Emmanuel"), [36.2, 0.8]);
    banker.face(at("Emmanuel"), "thinking").arms(at("Emmanuel"), "nod");
    banker.turn(at("Emmanuel"), "left");

    // SCENE 3: PROMISING KICKBACKS [12.00s - 17.50s]
    emmanuel.face(at("promising"), "grin").arms(at("promising"), "reach");
    banker.face(at("kickbacks."), "laugh").arms(at("kickbacks."), "armsUp");
    banker.hop(at("kickbacks."), 0.2);
    fx.add("burst", at("kickbacks."), at("kickbacks.") + 1.5, [36.2, 1.4, 0.8], { size: 0.8, color: "#22c55e" });

    // SCENE 4: WIRING 242 MILLION [17.50s - 23.50s]
    banker.hide(at("Over") - 0.1);
    emmanuel.place(at("Over") - 0.1, [-34.8, 0.8]);
    emmanuel.face(at("Over"), "smug").arms(at("Over"), "hold");
    emmanuel.turn(at("Over"), "left");

    emmanuel.face(at("accounts."), "laugh").arms(at("accounts."), "armsUp");
    emmanuel.hop(at("accounts."), 0.25);
    fx.add("stars", at("accounts."), at("accounts.") + 2.0, [-34.8, 2.2, -0.8], { size: 0.9, color: "#22c55e" });

    // SCENE 5: AUDITORS LOOKING FOR AIRPORT ON MAP [23.50s - 30.50s]
    emmanuel.hide(at("scam") - 0.1);
    banker.show(at("scam") - 0.1);
    banker.place(at("scam") - 0.1, [0, 35.8]);
    banker.face(at("scam"), "worried").arms(at("scam"), "facepalm");
    banker.turn(at("scam"), "left");

    banker.face(at("map."), "surprised").arms(at("map."), "armsUp");
    fx.add("sweat", at("map."), at("map.") + 2.0, [0, 2.2, 35.8], { size: 0.6, color: "#38bdf8" });

    // SCENE 6: THIRD LARGEST FRAUD [30.50s - end]
    emmanuel.show(at("history.") - 0.1);
    emmanuel.place(at("history.") - 0.1, [2.5, 35.8]);
    emmanuel.face(at("history."), "smug").arms(at("history."), "hips");
    emmanuel.hop(at("history."), 0.25);
    fx.add("stars", at("history."), at("history.") + 2.5, [2.5, 2.2, 35.8], { size: 1.0, color: "#f59e0b" });

    // ========================================================
    // CAMERA CHOREOGRAPHY
    // ========================================================
    const camera = [
      // Shot 1: Desert Hook
      {
        t: 0,
        pos: [0, 1.6, 4.2],
        look: [0, 1.4, 0.8],
        fov: 38,
        move: "push",
        push: 0.0022,
        light: "golden"
      },
      // Shot 2: Boardroom Call
      {
        t: at("Emmanuel"),
        pos: [35, 1.7, 4.4],
        look: [35, 1.4, 0.8],
        fov: 38,
        move: "push",
        push: 0.0018,
        light: "interior",
        transition: "whip"
      },
      // Shot 3: Instant Kickbacks
      {
        t: at("promising"),
        pos: [35, 1.6, 4.0],
        look: [35, 1.3, 0.8],
        fov: 36,
        move: "push",
        push: 0.0020,
        light: "interior",
        transition: "flash"
      },
      // Shot 4: Swiss Cash Stacks
      {
        t: at("Over"),
        pos: [-35, 1.6, 4.0],
        look: [-35, 1.2, -1.0],
        fov: 36,
        move: "push",
        push: 0.0022,
        light: "interior",
        transition: "whip"
      },
      // Shot 5: Map Auditors
      {
        t: at("scam"),
        pos: [0, 1.7, 39.8],
        look: [0, 1.4, 35.8],
        fov: 38,
        move: "push",
        push: 0.0018,
        light: "cold",
        transition: "flash"
      },
      // Shot 6: Third Largest Fraud
      {
        t: at("history."),
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
      { t: at("dollars."), amp: 0.06 },
      { t: at("kickbacks."), amp: 0.06 },
      { t: at("history."), amp: 0.07 }
    ];

    return { camera, kicks };
  }
};
