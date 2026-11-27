// Every external download RicksClips-Engine makes at setup time, pinned. Nothing listed here ships inside the plugin.
// All versions were released at least 14 days before NO_NEWER_THAN (the npm and pip date filters use it
// for indirect dependencies too).
export const NO_NEWER_THAN = "2026-10-24T00:00:00Z";
export const PINNED = {
  remotion: "4.0.538",
  "@remotion/bundler": "4.0.538",
  "@remotion/renderer": "4.0.538",
  react: "19.2.9",
  "react-dom": "19.2.9",
  three: "0.186.1",
  postprocessing: "6.39.5",
};
export const PIP_VERSION = "26.2.1"; // first pip with --uploaded-prior-to is 26.0
export const MIN = { node: [22, 0, 0], ffmpeg: [6, 0, 0], python: [3, 12, 0] };

// Fonts from the Google Fonts repository at one fixed commit (SIL Open Font License 1.1), checked by SHA-256.
export const FONT_COMMIT = "76fca9fd0bb4ea46583f92e978660f3984ab9442";
export const FONTS = {
  "Montserrat-wght.ttf": { src: "ofl/montserrat/Montserrat%5Bwght%5D.ttf", sha256: "0f7b311b2f3279e4eef9b2f968bcdbab6e28f4daeb1f049f4f278a902bcd82f7" },
  "Montserrat-OFL.txt": { src: "ofl/montserrat/OFL.txt", sha256: "8b7141c03fa4f8d44e6345d5d4931709290f0f67875e452e95ac1fd3a027802e" },
  "Nunito-wght.ttf": { src: "ofl/nunito/Nunito%5Bwght%5D.ttf", sha256: "bb55a5ca5c2042335b3991af27c4d0705d0ef41cac6164ac737fd8f2a1e85207" },
  "Nunito-OFL.txt": { src: "ofl/nunito/OFL.txt", sha256: "580df76c95a1ec5ab878ceb25bb3d85c6a076804e9c970c8c6972aea775fdf65" },
};

// Speech to text: OpenAI Whisper "turbo" (large-v3-turbo) through faster-whisper on the CPU.
// The model is chosen from the machine's memory: turbo when at least TURBO_MIN_RAM_GB of RAM, otherwise the small
// English model, which is pinned to one revision and checked file by file.
export const TURBO = { name: "turbo", repo: "mobiuslabsgmbh/faster-whisper-large-v3-turbo", approx_gb: 1.6, dir: "whisper-turbo" };
export const TURBO_MIN_RAM_GB = 6;
export const SMALL = {
  name: "small.en", dir: "faster-whisper-small.en", approx_gb: 0.5,
  repo: "Systran/faster-whisper-small.en",
  revision: "d1d751a5f8271d482d14ca55d9e2deeebbae577f",
  files: {
    "config.json": { size: 2657, gitsha1: "ced3fd5bbb3e9f7664658065d2d36164712cf1d5" },
    "tokenizer.json": { size: 2128466, gitsha1: "15d7bdf9ba25718ca2504eec6a8f02bc55af0a6a" },
    "vocabulary.txt": { size: 422309, gitsha1: "ee695b8d3e3c10d488304e04468efec4ca27554a" },
    "model.bin": { size: 483545366, sha256: "62b2a45b05ee59acb4a5341b33ee35e041395d378d418a18acfe4c9e768ee37a" },
  },
};
