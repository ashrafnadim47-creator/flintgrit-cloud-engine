import React, { useEffect, useRef } from "react";
import { Composition, registerRoot, useVideoConfig } from "remotion";

// Tiny WebGL page: draws one frame and logs the GPU name, so setup can tell hardware from software rendering.
const Probe = () => {
  const { width, height } = useVideoConfig();
  const ref = useRef(null);
  useEffect(() => {
    const gl = ref.current.getContext("webgl2");
    if (!gl) { console.log("RC_GL:no webgl2"); return; }
    const ext = gl.getExtension("WEBGL_debug_renderer_info");
    console.log("RC_GL:" + (ext ? gl.getParameter(ext.UNMASKED_RENDERER_WEBGL) : gl.getParameter(gl.RENDERER)));
    gl.clearColor(0.2, 0.3, 0.6, 1); gl.clear(gl.COLOR_BUFFER_BIT);
  }, []);
  return <canvas ref={ref} width={width} height={height} style={{ width, height, display: "block" }} />;
};

const Root = () => (
  <>
    <Composition id="probe" component={Probe} width={540} height={960} fps={30} durationInFrames={30} />
    <Composition id="probe2k" component={Probe} width={1440} height={2560} fps={30} durationInFrames={30} />
  </>
);
registerRoot(Root);
