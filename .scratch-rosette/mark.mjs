const EYES = [
  [[0, 3], [6, 9]],
  [[2, 3], [8, 9]],
  [[1, 2], [7, 8]],
  [[0, 1], [6, 7]],
  [[0, 3], [6, 9]]
];
const SMILE_WIDE = [
  [[0, 0], [9, 9]],
  [[0, 1], [8, 9]],
  [[1, 8]],
  [[2, 7]]
];
const SMILE_COMPACT = [
  [[1, 1], [8, 8]],
  [[1, 2], [7, 8]],
  [[2, 7]]
];
const SMILE_SMALL = [
  [[1, 1], [8, 8]],
  [[2, 7]]
];
const SMILES = {
  wide: SMILE_WIDE,
  compact: SMILE_COMPACT,
  small: SMILE_SMALL
};
const FACE_W = 10;
const GRID = 32;
const SAFE = { x0: 2, y0: 2, x1: 29, y1: 29, size: 28 };
function rows(smile, gap) {
  return [...EYES, ...Array.from({ length: gap }, () => []), ...SMILES[smile]];
}
function faceHeight({ smile = "wide", gap = 2 } = {}) {
  return EYES.length + gap + SMILES[smile].length;
}
function facePaths(opts = {}) {
  const { cx = 16, cy = 16, smile = "wide", gap = 2 } = opts;
  const h = faceHeight({ smile, gap });
  const top = Math.round(cy - h / 2);
  const left = Math.round(cx - FACE_W / 2);
  const out = [];
  rows(smile, gap).forEach((runs, i) => {
    for (const [a, b] of runs) {
      const w = b - a + 1;
      out.push(`M${left + a} ${top + i}h${w}v1h-${w}z`);
    }
  });
  return out;
}
function faceBox(opts = {}) {
  const { cx = 16, cy = 16 } = opts;
  const h = faceHeight(opts);
  const top = Math.round(cy - h / 2);
  const left = Math.round(cx - FACE_W / 2);
  return { x: left, y: top, w: FACE_W, h, right: left + FACE_W - 1, bottom: top + h - 1 };
}
const FAMILY = [
  { app: "Plozz", what: "TV", smile: "compact", centre: [16, 18], ink: "#000000", mid: "#00a4dc", light: "#97e3fe", deep: "#007aaf" },
  { app: "Mozz", what: "disc", smile: "wide", centre: [16, 16.5], ink: "#ffffff", mid: "#b00023", light: "#e34b4b", deep: "#3e0606" },
  { app: "Twozz", what: "speech bubble", smile: "wide", centre: [16, 14.5], ink: "#ffffff", mid: "#8f52f6", light: "#ad84ec", deep: "#7243c3" }
];
const EYES_SM = [
  [[0, 2]],
  [[1, 2]],
  [[0, 1]],
  [[0, 2]]
];
const SM_WIDE = [
  [[0, 0], [7, 7]],
  [[0, 1], [6, 7]],
  [[1, 6]]
];
const SM_COMPACT = [
  [[1, 1], [6, 6]],
  [[2, 5]]
];
const XS_WIDE = [
  [[0, 0], [6, 6]],
  [[1, 5]]
];
const SPECS = {
  /** 10 wide. The shipped family size — for plain, open containers only. */
  lg: { eyes: EYES, w: 10, gap: 2, smiles: { wide: SMILE_WIDE, compact: SMILE_COMPACT, small: SMILE_SMALL } },
  /** 8 wide. Two extra pixels of air either side. The sensible default. */
  md: { eyes: EYES_SM, w: 8, gap: 2, smiles: { wide: SM_WIDE, compact: SM_COMPACT } },
  /** 7 wide, tighter gap. For genuinely busy containers. */
  sm: { eyes: EYES_SM, w: 7, gap: 1, smiles: { wide: XS_WIDE, compact: XS_WIDE } }
};
function specRows(size, smile, gap) {
  const sp = SPECS[size];
  const eyeRows = size === "lg" ? sp.eyes : sp.eyes.map((r) => r.flatMap(([a, b]) => [[a, b], [a + sp.w - 3, b + sp.w - 3]]));
  if (smile === "none") return eyeRows;
  const sm = sp.smiles[smile] ?? sp.smiles.wide;
  return [...eyeRows, ...Array.from({ length: gap }, () => []), ...sm];
}
function facePathsAt(opts = {}) {
  const { cx = 16, cy = 16, size = "md", smile = "wide" } = opts;
  const sp = SPECS[size];
  const gap = opts.gap ?? sp.gap;
  const rows2 = specRows(size, smile, gap);
  const top = Math.round(cy - rows2.length / 2);
  const left = Math.round(cx - sp.w / 2);
  const out = [];
  rows2.forEach((runs, i) => {
    for (const [a, b] of runs) {
      const w = b - a + 1;
      out.push(`M${left + a} ${top + i}h${w}v1h-${w}z`);
    }
  });
  return out;
}
function faceBoxAt(opts = {}) {
  const { cx = 16, cy = 16, size = "md", smile = "wide" } = opts;
  const sp = SPECS[size];
  const gap = opts.gap ?? sp.gap;
  const rows2 = specRows(size, smile, gap);
  const top = Math.round(cy - rows2.length / 2);
  const left = Math.round(cx - sp.w / 2);
  return { x: left, y: top, w: sp.w, h: rows2.length, right: left + sp.w - 1, bottom: top + rows2.length - 1 };
}
const FACE_SIZES = { lg: 10, md: 8, sm: 7 };
export {
  FACE_SIZES,
  FACE_W,
  FAMILY,
  GRID,
  SAFE,
  faceBox,
  faceBoxAt,
  faceHeight,
  facePaths,
  facePathsAt
};
