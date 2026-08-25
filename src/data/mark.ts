/**
 * The family face.
 *
 * Rasterised out of the three shipped marks — Plozz's TV, Mozz's disc and
 * Twozz's bubble — rather than eyeballed.
 *
 * What is actually fixed across the family is the **ZZ eyes**: two 4-wide Zs
 * with a 2-pixel gap, identical in all three. What varies is the smile and the
 * spacing under the eyes, because Plozz's mark is busy and its smile had to
 * give the bezel room. So this module keeps the eyes constant and lets a
 * concept choose how much room the smile takes.
 *
 * The other thing all three agree on: the face is 10 pixels wide at x 11–20,
 * so its centre is x = 16.0 — and it is centred on the container's own optical
 * middle, not on the 32-box. Plozz centres it in the TV *screen* (16, 18);
 * Mozz centres it in the disc (16, 16.5).
 *
 * An earlier version of this file recorded the centre as 15.5, the midpoint of
 * the pixel *indices* rather than of the drawn area. Everything built against
 * it came out half a pixel left, which is visible, and is why this exists.
 */

/** Rows as [startX, endX] runs, relative to the face's left edge. */
type Row = [number, number][];

/** Identical in Plozz, Mozz and Twozz. This is the family signature. */
const EYES: Row[] = [
  [[0, 3], [6, 9]],
  [[2, 3], [8, 9]],
  [[1, 2], [7, 8]],
  [[0, 1], [6, 7]],
  [[0, 3], [6, 9]],
];

/** Mozz and Twozz: 10 across, 4 rows. The most open, happiest reading. */
const SMILE_WIDE: Row[] = [
  [[0, 0], [9, 9]],
  [[0, 1], [8, 9]],
  [[1, 8]],
  [[2, 7]],
];

/** Plozz: 8 across, 3 rows. For containers with detail to protect. */
const SMILE_COMPACT: Row[] = [
  [[1, 1], [8, 8]],
  [[1, 2], [7, 8]],
  [[2, 7]],
];

/** 6 across, 2 rows. For small or crowded containers, or a quieter face. */
const SMILE_SMALL: Row[] = [
  [[1, 1], [8, 8]],
  [[2, 7]],
];

export type Smile = 'wide' | 'compact' | 'small';

const SMILES: Record<Smile, Row[]> = {
  wide: SMILE_WIDE,
  compact: SMILE_COMPACT,
  small: SMILE_SMALL,
};

/** The face is always 10 wide, because the eyes are. */
export const FACE_W = 10;

/** The grid every mark is drawn on. */
export const GRID = 32;

/**
 * The drawable area. Every sibling is a 28×28 shape inset by 2, so a Hozz mark
 * that breaks this will not sit right next to them on a home screen.
 */
export const SAFE = { x0: 2, y0: 2, x1: 29, y1: 29, size: 28 } as const;

export interface FaceOpts {
  /** Optical centre of the container. Default (16, 16) — the middle of a 28 shape. */
  cx?: number;
  cy?: number;
  /** Smile width. Match it to how much room the container has. */
  smile?: Smile;
  /** Rows between the eyes and the smile. 2 is the family default; 1 tightens it. */
  gap?: number;
}

function rows(smile: Smile, gap: number): Row[] {
  return [...EYES, ...Array.from({ length: gap }, () => [] as Row), ...SMILES[smile]];
}

/** Total face height for a given smile and gap. */
export function faceHeight({ smile = 'wide', gap = 2 }: FaceOpts = {}): number {
  return EYES.length + gap + SMILES[smile].length;
}

/**
 * Face paths, centred on (cx, cy).
 *
 * Snapped to whole pixels, so an odd-height face lands half a pixel off its
 * centre — biased low, exactly as Mozz does it.
 */
export function facePaths(opts: FaceOpts = {}): string[] {
  const { cx = 16, cy = 16, smile = 'wide', gap = 2 } = opts;
  const h = faceHeight({ smile, gap });
  const top = Math.round(cy - h / 2);
  const left = Math.round(cx - FACE_W / 2);
  const out: string[] = [];
  rows(smile, gap).forEach((runs, i) => {
    for (const [a, b] of runs) {
      const w = b - a + 1;
      out.push(`M${left + a} ${top + i}h${w}v1h-${w}z`);
    }
  });
  return out;
}

/** Where the face lands, so a container can be built around it rather than over it. */
export function faceBox(opts: FaceOpts = {}) {
  const { cx = 16, cy = 16 } = opts;
  const h = faceHeight(opts);
  const top = Math.round(cy - h / 2);
  const left = Math.round(cx - FACE_W / 2);
  return { x: left, y: top, w: FACE_W, h, right: left + FACE_W - 1, bottom: top + h - 1 };
}

/** The siblings, for palette and placement reference. Read off the shipped marks. */
export const FAMILY = [
  { app: 'Plozz', what: 'TV', smile: 'compact', centre: [16, 18], ink: '#000000', mid: '#00a4dc', light: '#97e3fe', deep: '#007aaf' },
  { app: 'Mozz', what: 'disc', smile: 'wide', centre: [16, 16.5], ink: '#ffffff', mid: '#b00023', light: '#e34b4b', deep: '#3e0606' },
  { app: 'Twozz', what: 'speech bubble', smile: 'wide', centre: [16, 14.5], ink: '#ffffff', mid: '#8f52f6', light: '#ad84ec', deep: '#7243c3' },
] as const;

/* ---------------------------------------------------------------------------
   Smaller faces.

   The first set of marks all felt cramped, and the cause is arithmetic: a
   10-wide face on a 28-wide container leaves only 9 clear either side, and any
   container detail eats into that immediately. A 3-wide Z gives the face room
   to sit in its own space instead of pressing on the edges.

   Use `size="md"` or `"sm"` on anything with a busy container, and `"lg"` only
   when the container is a plain open field.
   --------------------------------------------------------------------------- */

/** 3 wide, 4 tall. Same letter, one step less diagonal. */
const EYES_SM: Row[] = [
  [[0, 2]],
  [[1, 2]],
  [[0, 1]],
  [[0, 2]],
];

/** Smiles scaled to an 8-wide face. */
const SM_WIDE: Row[] = [
  [[0, 0], [7, 7]],
  [[0, 1], [6, 7]],
  [[1, 6]],
];

const SM_COMPACT: Row[] = [
  [[1, 1], [6, 6]],
  [[2, 5]],
];

/** Smiles scaled to a 7-wide face. */
const XS_WIDE: Row[] = [
  [[0, 0], [6, 6]],
  [[1, 5]],
];

export type FaceSize = 'lg' | 'md' | 'sm';

interface Spec {
  eyes: Row[];
  w: number;
  gap: number;
  smiles: Partial<Record<Smile, Row[]>>;
}

const SPECS: Record<FaceSize, Spec> = {
  /** 10 wide. The shipped family size — for plain, open containers only. */
  lg: { eyes: EYES, w: 10, gap: 2, smiles: { wide: SMILE_WIDE, compact: SMILE_COMPACT, small: SMILE_SMALL } },
  /** 8 wide. Two extra pixels of air either side. The sensible default. */
  md: { eyes: EYES_SM, w: 8, gap: 2, smiles: { wide: SM_WIDE, compact: SM_COMPACT } },
  /** 7 wide, tighter gap. For genuinely busy containers. */
  sm: { eyes: EYES_SM, w: 7, gap: 1, smiles: { wide: XS_WIDE, compact: XS_WIDE } },
};

export interface FaceOpts2 extends FaceOpts {
  size?: FaceSize;
  /** `none` draws the eyes alone — two Zs read as a content face on their own. */
  smile?: Smile | 'none';
}

function specRows(size: FaceSize, smile: Smile | 'none', gap: number): Row[] {
  const sp = SPECS[size];
  const eyeRows = size === 'lg'
    ? sp.eyes
    : sp.eyes.map((r) => r.flatMap(([a, b]) => [[a, b], [a + sp.w - 3, b + sp.w - 3]] as [number, number][]));
  if (smile === 'none') return eyeRows;
  const sm = sp.smiles[smile] ?? sp.smiles.wide!;
  return [...eyeRows, ...Array.from({ length: gap }, () => [] as Row), ...sm];
}

/** Face paths at a chosen size, centred on (cx, cy). */
export function facePathsAt(opts: FaceOpts2 = {}): string[] {
  const { cx = 16, cy = 16, size = 'md', smile = 'wide' } = opts;
  const sp = SPECS[size];
  const gap = opts.gap ?? sp.gap;
  const rows = specRows(size, smile, gap);
  const top = Math.round(cy - rows.length / 2);
  const left = Math.round(cx - sp.w / 2);
  const out: string[] = [];
  rows.forEach((runs, i) => {
    for (const [a, b] of runs) {
      const w = b - a + 1;
      out.push(`M${left + a} ${top + i}h${w}v1h-${w}z`);
    }
  });
  return out;
}

/** Where a sized face lands. */
export function faceBoxAt(opts: FaceOpts2 = {}) {
  const { cx = 16, cy = 16, size = 'md', smile = 'wide' } = opts;
  const sp = SPECS[size];
  const gap = opts.gap ?? sp.gap;
  const rows = specRows(size, smile, gap);
  const top = Math.round(cy - rows.length / 2);
  const left = Math.round(cx - sp.w / 2);
  return { x: left, y: top, w: sp.w, h: rows.length, right: left + sp.w - 1, bottom: top + rows.length - 1 };
}

export const FACE_SIZES: Record<FaceSize, number> = { lg: 10, md: 8, sm: 7 };
