import * as THREE from "three";
import words from "./words.js";
import { prop } from "./engine/world/props.js";
import { glow, mat } from "./engine/world/shade.js";
import { box, cyl } from "./engine/world/kit.js";

export default {
  seed: 101,
  words,
  light: "interior",
  build({ W, kit, cast, fx, makeLook, rand, clock }) {
    const { at } = clock;

    // ==========================================
    // 1. FLOOR & ENVIRONMENT
    // ==========================================
    kit.ground(W, { kind: "slabs", color: "#e2e8f0" });
    kit.hills(W, { color: "#94a3b8", dist: 60 });

    const floorMat = mat("stone", { color: "#0f172a" });
    const studioFloor = new THREE.Mesh(
      new THREE.PlaneGeometry(16, 18).rotateX(-Math.PI / 2),
      floorMat
    );
    studioFloor.position.set(0, 0.015, 0);
    studioFloor.userData.ink = "ground";
    W.add(studioFloor, { collide: false });

    const wallM = mat("flat", { color: "#1e293b" });
    const glassM = new THREE.MeshBasicMaterial({
      color: new THREE.Color(0.4, 0.7, 1.0),
      transparent: true,
      opacity: 0.35,
    });

    W.add(box(16, 3.2, 0.15, wallM, { x: 0, y: 1.6, z: -8.5 }));
    W.add(box(0.15, 3.2, 18, wallM, { x: -8, y: 1.6, z: 0 }));
    W.add(box(0.15, 3.2, 18, wallM, { x: 8, y: 1.6, z: 0 }));

    W.add(box(0.08, 2.8, 14, glassM, { x: -2.5, y: 1.4, z: -1 }));
    W.add(box(0.08, 2.8, 14, glassM, { x: 2.5, y: 1.4, z: -1 }));
    W.add(box(6, 2.8, 0.08, glassM, { x: -5, y: 1.4, z: -2.5 }));
    W.add(box(6, 2.8, 0.08, glassM, { x: 5, y: 1.4, z: -2.5 }));

    const frameM = mat("flat", { color: "#38bdf8" });
    W.add(box(1.4, 2.4, 0.1, frameM, { x: -2.5, y: 1.2, z: 2.5 }));
    W.add(box(1.4, 2.4, 0.1, frameM, { x: 2.5, y: 1.2, z: 2.5 }));

    // ==========================================
    // 2. DEPARTMENT 1: VIDEO EDITING BAY [X: -5.2, Z: 0]
    // ==========================================
    prop.desk(W, { x: -5.2, z: 0, ry: Math.PI / 2, w: 1.8, d: 0.9 });
    prop.officeChair(W, { x: -4.3, z: 0, ry: -Math.PI / 2 });

    const mon1 = new THREE.Group();
    mon1.add(box(0.7, 0.42, 0.03, mat("#111111"), { y: 0.25 }));
    mon1.add(box(0.66, 0.38, 0.01, glow([0.2, 1.8, 2.4]), { y: 0.25, z: 0.018 }));
    mon1.position.set(-5.15, 0.78, -0.38);
    mon1.rotation.y = Math.PI / 2 + 0.22;
    W.add(mon1, { collide: false });

    const mon2 = new THREE.Group();
    mon2.add(box(0.7, 0.42, 0.03, mat("#111111"), { y: 0.25 }));
    mon2.add(box(0.66, 0.38, 0.01, glow([2.4, 0.6, 1.8]), { y: 0.25, z: 0.018 }));
    mon2.position.set(-5.15, 0.78, 0.38);
    mon2.rotation.y = Math.PI / 2 - 0.22;
    W.add(mon2, { collide: false });

    W.add(box(0.38, 0.02, 0.14, mat("#222222"), { x: -4.7, y: 0.78, z: 0 }));
    W.add(box(0.06, 0.02, 0.09, mat("#38bdf8"), { x: -4.7, y: 0.78, z: 0.22 }));
    prop.mug(W, { x: -4.7, y: 0.78, z: -0.3, color: "#f59e0b" });
    prop.filingCabinet(W, { x: -7.2, z: -1.8, ry: Math.PI / 2 });
    prop.waterCooler(W, { x: -7.2, z: 1.8, ry: Math.PI / 2 });

    // ==========================================
    // 3. DEPARTMENT 2: SCRIPT & DEV LAB [X: 5.2, Z: 0]
    // ==========================================
    prop.desk(W, { x: 5.2, z: 0, ry: -Math.PI / 2, w: 1.8, d: 0.9 });
    prop.officeChair(W, { x: 4.3, z: 0, ry: Math.PI / 2 });

    for (let i = -1; i <= 1; i++) {
      const devMon = new THREE.Group();
      devMon.add(box(0.35, 0.55, 0.03, mat("#111111"), { y: 0.3 }));
      devMon.add(box(0.32, 0.51, 0.01, glow([0.4, 2.2, 0.8]), { y: 0.3, z: 0.018 }));
      devMon.position.set(5.15, 0.78, i * 0.45);
      devMon.rotation.y = -Math.PI / 2 - i * 0.25;
      W.add(devMon, { collide: false });
    }

    prop.whiteboard(W, { x: 7.9, y: 1.6, z: 0, ry: -Math.PI / 2, w: 2.6 });
    prop.bookPile(W, { x: 4.8, y: 0.78, z: -0.32 });
    prop.plant(W, { x: 7.2, z: 2.2 });

    // ==========================================
    // 4. DEPARTMENT 3: HIGH-TECH SERVER ROOM [X: -5.2, Z: -5.5]
    // ==========================================
    for (let r = 0; r < 4; r++) {
      const rack = new THREE.Group();
      rack.add(box(0.9, 2.5, 0.9, mat("#090d16"), { y: 1.25 }));
      for (let k = 0; k < 8; k++) {
        const isCyan = (r + k) % 2 === 0;
        const led = box(
          0.72,
          0.04,
          0.02,
          glow(isCyan ? [0.2, 2.0, 2.8] : [0.2, 2.8, 0.8]),
          { y: 0.35 + k * 0.26, z: 0.46 }
        );
        rack.add(led);
      }
      rack.position.set(-6.5 + (r % 2) * 1.6, 0, -4.5 - Math.floor(r / 2) * 1.8);
      W.add(rack, { collide: true });
    }
    prop.vent(W, { x: -5.5, y: 2.8, z: -8.4 });

    // ==========================================
    // 5. DEPARTMENT 4: SIR KA EXECUTIVE OFFICE [X: 5.2, Z: -5.5]
    // ==========================================
    prop.desk(W, { x: 5.2, z: -5.5, ry: 0, w: 2.2, d: 1.0 });
    prop.officeChair(W, { x: 5.2, z: -6.4, ry: 0 });
    prop.armchair(W, { x: 4.2, z: -4.4, ry: 0.6 });
    prop.armchair(W, { x: 6.2, z: -4.4, ry: -0.6 });

    const laptop = new THREE.Group();
    laptop.add(box(0.36, 0.015, 0.25, mat("#cbd5e1"), { y: 0.008 }));
    laptop.add(box(0.36, 0.25, 0.015, mat("#cbd5e1"), { y: 0.13, z: -0.12, rx: -0.2 }));
    laptop.add(box(0.34, 0.22, 0.005, glow([1.5, 1.8, 2.5]), { y: 0.13, z: -0.115, rx: -0.2 }));
    laptop.position.set(5.2, 0.78, -5.5);
    W.add(laptop, { collide: false });

    const playButton = new THREE.Group();
    playButton.add(box(0.6, 0.75, 0.04, mat("#0f172a"), {}));
    playButton.add(box(0.46, 0.36, 0.02, mat("#e2e8f0"), { y: 0.1, z: 0.025 }));
    playButton.add(box(0.12, 0.12, 0.02, mat("#ef4444"), { y: 0.1, z: 0.038 }));
    playButton.position.set(5.2, 1.8, -8.4);
    W.add(playButton, { collide: false });

    prop.noticeBoard(W, { x: 7.9, y: 1.7, z: -5.5, ry: -Math.PI / 2 });

    // ==========================================
    // 6. CENTRAL ATRIUM: HOLOGRAPHIC AI BRAIN (JARVIS HUD)
    // ==========================================
    const holoCore = new THREE.Group();
    holoCore.add(cyl(0.7, 0.9, 0.8, mat("#0f172a"), { y: 0.4, seg: 24 }));
    holoCore.add(cyl(0.8, 0.8, 0.05, glow([0.4, 1.8, 2.8]), { y: 0.82, seg: 24 }));

    const aiSphere = new THREE.Mesh(
      new THREE.SphereGeometry(0.55, 32, 32),
      glow([0.3, 2.2, 3.2])
    );
    aiSphere.position.y = 1.75;
    holoCore.add(aiSphere);

    const ring1 = new THREE.Mesh(
      new THREE.TorusGeometry(0.9, 0.025, 16, 64),
      glow([0.4, 2.5, 3.0])
    );
    ring1.position.y = 1.75;
    ring1.rotation.x = Math.PI / 3;
    holoCore.add(ring1);

    const ring2 = new THREE.Mesh(
      new THREE.TorusGeometry(1.15, 0.02, 16, 64),
      glow([2.5, 0.8, 2.0])
    );
    ring2.position.y = 1.75;
    ring2.rotation.y = Math.PI / 4;
    holoCore.add(ring2);

    holoCore.position.set(0, 0, 0);
    W.add(holoCore, { collide: false });

    // ==========================================
    // 7. CAST: LIVING CHARACTERS & AGENTS
    // ==========================================
    const sir = cast.add({
      name: "sir",
      look: makeLook(rand.fork(7), "adult", { outfit: "suit", top: "#0f172a", hairStyle: "short", hair: "#1e293b", build: 1.05 }),
      pos: [5.2, -6.1],
      h: 1.78,
    });

    const editor = cast.add({
      name: "editor",
      look: makeLook(rand.fork(11), "adult", { outfit: "tee", top: "#0284c7", hairStyle: "curly", hair: "#000000", build: 1.0 }),
      pos: [-4.4, 0],
      h: 1.72,
    });

    const coder = cast.add({
      name: "coder",
      look: makeLook(rand.fork(19), "adult", { outfit: "hoodie", top: "#10b981", hairStyle: "parted", hair: "#475569", build: 0.98 }),
      pos: [4.4, 0],
      h: 1.74,
    });

    // ==========================================
    // 8. ANIMATIONS & ACTING
    // ==========================================
    sir.face(0, "smug").arms(0, "hold");
    editor.face(0, "determined").arms(0, "point");
    coder.face(0, "thinking").arms(0, "think");

    sir.face(at("company"), "grin").arms(at("company"), "armsUp");
    fx.add("sparkle", at("studio!"), at("studio!") + 1.5, [0, 2.2, 0], { size: 0.8, color: "#38bdf8" });

    editor.face(at("desk"), "determined")
      .arms(at("desk"), "hold")
      .face(at("editor"), "grin")
      .hop(at("editor"), 0.15)
      .arms(at("monitors"), "point");

    coder.face(at("scriptwriting"), "thinking")
      .arms(at("scriptwriting"), "think")
      .face(at("hooks"), "laugh")
      .arms(at("hooks"), "armsUp")
      .hop(at("hooks"), 0.2);

    fx.add("exclaim", at("brain"), at("brain") + 1.5, [0, 2.5, 0], { size: 0.9, color: "#38bdf8" });

    sir.face(at("Zero"), "laugh")
      .arms(at("Zero"), "wave")
      .hop(at("Zero"), 0.15);

    sir.face(at("run"), "smug")
      .arms(at("company?"), "hold")
      .hop(at("company?"), 0.2);

    // ==========================================
    // 9. DYNAMIC CINEMATIC CAMERA CHOREOGRAPHY
    // ==========================================
    return {
      camera: [
        { t: 0, pos: [0, 1.8, 8.5], look: [0, 1.6, 1.0], fov: 45, light: "interior", move: "push", push: 0.18 },
        { t: at("studio!") - 0.2, pos: [0, 5.0, 7.5], look: [0, 1.3, -1.0], fov: 56, light: "interior", transition: "whip", whipDir: 1 },
        { t: at("desk") - 0.1, pos: [-3.4, 1.5, 0.4], look: [-5.2, 1.1, 0], fov: 38, light: "interior", transition: "whip", whipDir: -1, move: "push", push: 0.12 },
        { t: at("scriptwriting") - 0.1, pos: [3.4, 1.5, 0.4], look: [5.2, 1.1, 0], fov: 38, light: "interior", transition: "whip", whipDir: 1, move: "push", push: 0.12 },
        { t: at("server") - 0.1, pos: [-5.6, 1.1, -2.4], look: [-5.6, 1.3, -5.2], fov: 46, light: "night", transition: "whip", whipDir: -1, move: "push", push: 0.15 },
        { t: at("center") - 0.2, pos: [0, 2.0, 3.2], look: [0, 1.7, 0], fov: 42, light: "interior", transition: "flash", tframes: 6, move: "push", push: 0.1 },
        { t: at("Zero") - 0.1, pos: [0, 6.2, 8.2], look: [0, 1.0, -1.5], fov: 60, light: "interior", transition: "whip", whipDir: 1 },
        { t: at("run") - 0.1, pos: [5.2, 1.5, -3.8], look: [5.2, 1.4, -6.0], fov: 42, light: "interior", transition: "whip", whipDir: -1, move: "push", push: 0.08 }
      ],
      kicks: [
        { t: at("studio!"), amp: 0.06 },
        { t: at("editor"), amp: 0.05 },
        { t: at("hooks"), amp: 0.05 },
        { t: at("brain"), amp: 0.08 },
        { t: at("company?"), amp: 0.07 }
      ],
      onFrame(t, ctx) {
        ring1.rotation.z = t * 1.8;
        ring2.rotation.x = t * 1.4;
        aiSphere.rotation.y = t * 0.9;
        const pulse = 1.0 + Math.sin(t * 6) * 0.08;
        aiSphere.scale.set(pulse, pulse, pulse);
      }
    };
  }
};
