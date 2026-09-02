/**
 * A toolkit for **drawing** Zs. Not a font, and not a fixed mark.
 *
 * Every previous attempt failed the same way: a Z was taken from a typeface,
 * recoloured, and dropped on top of a shape. The give-away is stroke contrast.
 * A text Z has one weight — its bars and its diagonal are the same mass, because
 * a type designer already balanced them for a page of running text. A *drawn* Z
 * can make the diagonal heavier than the bars, or lighter, shear its
 * terminals to match a container edge, to lose a bar into the object it sits in.
 *
 * So this module exposes the variables, not a glyph:
 *
 *   bar       thickness of the two horizontals
 *   diag      horizontal thickness of the diagonal band  <- the design decision
 *   cap       how the outer ends of the bars are cut
 *   slant     shear of the whole letter
 *
 * `diag` is the important one. Set it equal to `bar` and you have reinvented a
 * font. Set it well above or below and the letter starts to have a voice.
 *
 * Nothing here positions a Z for you and nothing here draws two of them. Where
 * the Zs go, how they overlap, whether one is cut out of a screen or formed by
 * a groove in a disc — that is the concept's job, and it is the only part that
 * matters.
 */

export interface ZSpec {
  /** Left edge of the letter's bounding box. */
  x: number;
  /** Top edge. */
  y: number;
  /** Width of the bounding box. */
  w: number;
  /** Height of the bounding box. */
  h: number;
  /** Thickness of the top and bottom bars. */
  bar: number;
  /**
   * Horizontal thickness of the diagonal band. Defaults to `bar`, which is the
   * font-like answer — pick something else.
   */
  diag?: number;
  /**
   * How the outer ends of the bars are cut.
   * - `flat`   vertical, the neutral choice
   * - `angled` sheared parallel to the diagonal, which knits the letter together
   * - `open`   the bar runs past the box and is left to be clipped by the container
   */
  cap?: 'flat' | 'angled' | 'open';
  /** Shear, in x units across the full height. Positive leans right. */
  slant?: number;
  /** Radius applied to the four outer corners. 0 keeps it sharp. */
  round?: number;
}

const n = (v: number) => (Math.round(v * 1000) / 1000).toString();

/**
 * The filled outline of one Z, as an SVG path `d`.
 *
 * Ten points, walked clockwise from the top-left. The diagonal is a
 * parallelogram whose right edge drops from the underside of the top bar to the
 * top of the bottom bar, and whose left edge is `diag` behind it.
 */
export function zPath(spec: ZSpec): string {
  const { x, y, w, h, bar } = spec;
  const diag = spec.diag ?? bar;
  const cap = spec.cap ?? 'flat';
  const slant = spec.slant ?? 0;
  const round = spec.round ?? 0;

  // Shear is applied per-point: the further down the letter, the less it moves.
  const sx = (px: number, py: number) => px + slant * (1 - (py - y) / h);

  const yTopIn = y + bar; // underside of the top bar
  const yBotIn = y + h - bar; // top of the bottom bar

  // `open` lets the bars run past the box so a container can clip them.
  const over = cap === 'open' ? bar * 0.9 : 0;
  const xL = x - over;
  const xR = x + w + over;

  // `angled` shears the outer terminals to sit parallel to the diagonal.
  const shear = cap === 'angled' ? (w - diag) * (bar / (h - 2 * bar)) : 0;

  const pts: [number, number][] = [
    [xL + shear, y], //          0  top-left
    [xR, y], //                  1  top-right
    [x + w, yTopIn], //          2  under the top bar, right end — diagonal starts
    [x + diag, yBotIn], //       3  foot of the diagonal's right edge
    [xR, yBotIn], //             4  right along the top of the bottom bar
    [xR - shear, y + h], //      5  bottom-right
    [xL, y + h], //              6  bottom-left
    [xL, yBotIn], //             7  up the left end of the bottom bar
    [x + w - diag, yTopIn], //   8  up the diagonal's left edge
    [xL, yTopIn], //             9  left along the underside of the top bar
  ];

  // The three points that define the diagonal's edges must stay sharp —
  // rounding them collapses the letter. Everything else may take a radius.
  const sharp = new Set([2, 3, 8]);
  const shaped = pts.map(([px, py]) => [sx(px, py), py] as [number, number]);

  if (round <= 0) {
    return (
      shaped.map(([px, py], i) => `${i === 0 ? 'M' : 'L'}${n(px)} ${n(py)}`).join('') + 'Z'
    );
  }

  let d = '';
  for (let i = 0; i < shaped.length; i++) {
    const prev = shaped[(i - 1 + shaped.length) % shaped.length];
    const cur = shaped[i];
    const next = shaped[(i + 1) % shaped.length];

    if (sharp.has(i)) {
      d += `${d ? 'L' : 'M'}${n(cur[0])} ${n(cur[1])}`;
      continue;
    }

    const [ax, ay] = trim(cur, prev, round);
    const [bx, by] = trim(cur, next, round);
    d += `${d ? 'L' : 'M'}${n(ax)} ${n(ay)}Q${n(cur[0])} ${n(cur[1])} ${n(bx)} ${n(by)}`;
  }
  return d + 'Z';
}

/** Walk `r` from `from` toward `to`, never past the midpoint. */
function trim(
  from: [number, number],
  to: [number, number],
  r: number,
): [number, number] {
  const dx = to[0] - from[0];
  const dy = to[1] - from[1];
  const len = Math.hypot(dx, dy) || 1;
  const t = Math.min(r, len / 2) / len;
  return [from[0] + dx * t, from[1] + dy * t];
}

/**
 * The centreline of a Z, for concepts that want a monoline drawn with
 * `stroke-width` — a groove cut in a disc, a cable, a trace on a screen.
 * Returns three points; set `stroke-linejoin` and `stroke-linecap` yourself,
 * because those joints are a design decision too.
 */
export function zSpine(spec: Pick<ZSpec, 'x' | 'y' | 'w' | 'h' | 'slant'>): string {
  const { x, y, w, h } = spec;
  const slant = spec.slant ?? 0;
  const sx = (px: number, py: number) => px + slant * (1 - (py - y) / h);
  return (
    `M${n(sx(x, y))} ${n(y)}` +
    `L${n(sx(x + w, y))} ${n(y)}` +
    `L${n(sx(x, y + h))} ${n(y + h)}` +
    `L${n(sx(x + w, y + h))} ${n(y + h)}`
  );
}

/**
 * The bounding box a Z actually occupies, once `slant` and `open` caps are
 * taken into account. Use it to check the letter has room, rather than assuming.
 */
export function zBox(spec: ZSpec): { x: number; y: number; w: number; h: number } {
  const over = (spec.cap ?? 'flat') === 'open' ? spec.bar * 0.9 : 0;
  const slant = spec.slant ?? 0;
  const left = spec.x - over + Math.min(0, slant);
  const right = spec.x + spec.w + over + Math.max(0, slant);
  return { x: left, y: spec.y, w: right - left, h: spec.h };
}
