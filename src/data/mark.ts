/**
 * The canonical family face.
 *
 * Lifted pixel-for-pixel out of `plozz-website/public/logo.svg` — not redrawn,
 * not traced, not eyeballed. Plozz, Mozz and Twozz all carry this exact face,
 * and Hozz has to as well or it is not a sibling.
 *
 * The grid, for anyone checking against the mark:
 *
 *   13  ####..####
 *   14  ..##....##
 *   15  .##....##.
 *   16  ##....##..
 *   17  ####..####
 *   18  ..........
 *   19  ..........
 *   20  .#......#.
 *   21  .##....##.
 *   22  ..######..
 *
 * Note the face is centred on x = 15.5 in a 32-wide box, a half-pixel left of
 * true centre. That asymmetry is in the original and is deliberate here.
 *
 * Every concept imports these paths. Nothing redeclares them, so a concept
 * physically cannot drift from the family.
 */

/** Left eye, right eye, then the smile. 32×32 coordinate space. */
export const FACE_PATHS = [
  // Left Z
  'M11 13h4v1h-4z',
  'M13 14h2v1h-2z',
  'M12 15h2v1h-2z',
  'M11 16h2v1h-2z',
  'M11 17h4v1h-4z',
  // Right Z
  'M17 13h4v1h-4z',
  'M19 14h2v1h-2z',
  'M18 15h2v1h-2z',
  'M17 16h2v1h-2z',
  'M17 17h4v1h-4z',
  // Smile
  'M12 20h1v2h-1z',
  'M13 21h1v2h-1z',
  'M14 22h4v1h-4z',
  'M18 21h1v2h-1z',
  'M19 20h1v2h-1z',
] as const;

/** Where the face sits, so a container can be built around it rather than over it. */
export const FACE_BOX = { x: 11, y: 13, w: 10, h: 10, cx: 15.5, cy: 17.5 } as const;

/** The grid every mark is drawn on. */
export const GRID = 32;

/**
 * The siblings, for palette reference. Values read off the shipped marks.
 * Hozz has to sit in this family without repeating any of them.
 */
export const FAMILY = [
  { app: 'Plozz', what: 'TV', ink: '#000000', mid: '#00a4dc', light: '#97e3fe', deep: '#007aaf' },
  { app: 'Mozz', what: 'disc', ink: '#ffffff', mid: '#c62828', light: '#e34b4b', deep: '#7f1d1d' },
  { app: 'Twozz', what: 'speech bubble', ink: '#ffffff', mid: '#7c4dff', light: '#a98bff', deep: '#4a25b8' },
] as const;
