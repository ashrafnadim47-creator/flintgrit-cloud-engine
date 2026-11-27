import React from "react";
import { Composition } from "remotion";
import { Scene } from "./Scene.jsx";
import meta from "./project.json";

// One composition per short. Size and length come from project.json (written by scripts/project.mjs).
export const Root = () => (
  <Composition
    id="main"
    component={Scene}
    width={meta.W}
    height={meta.H}
    fps={30}
    durationInFrames={Math.max(30, Math.round(meta.duration * 30))}
  />
);
