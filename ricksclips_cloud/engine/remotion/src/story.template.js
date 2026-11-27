// story.js for one short. Claude writes this file per story (see skills/ricksclips-engine/references/engine-api.md).
// Times come from the word clock: at("word") = start of that word in the final voice.
import words from "./words.js";

export default {
  seed: 1,
  words,
  light: "day",
  build({ W, kit, mat, cast, fx, makeLook, rand, clock, aim, aerial }) {
    const { at } = clock;
    // ---- world ----
    kit.ground(W, { kind: "grass", color: "#7aa84c" });
    kit.hills(W, {});
    // ---- cast ----
    // const hero = cast.add({ name: "hero", look: makeLook(rand.fork(1), "adult"), pos: [0, 0] });
    // const cat = cast.animal({ name: "cat", species: "cat", pos: [1.2, 0.4] });
    // ---- camera: one key per shot ----
    return {
      camera: [
        { t: 0, pos: [0, 1.6, 8], look: [0, 1.2, 0], light: "day" },
      ],
      kicks: [],
    };
  },
};
