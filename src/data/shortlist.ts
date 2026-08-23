/**
 * The shortlist.
 *
 * Fifty marks is more than anyone can judge, and a board that shows them all
 * as equals is not a board, it is a pile. These are the ones worth looking at
 * first, picked by rendering every concept and looking at it — not from what
 * the agents reported about their own work, which has been unreliable.
 *
 * Kept here rather than as a flag in each `.meta.ts` because those files belong
 * to the agents and get rewritten; this one does not.
 */
export interface Pick {
  slug: string;
  why: string;
}

export const SHORTLIST: Pick[] = [
  {
    slug: 'tw07',
    why: 'The best thing on the board. The face repeats as a receding echo, which is what a chat looks like when one emote gets spammed — no other app in the family could use this.',
  },
  {
    slug: 'tw08',
    why: 'The same idea held to a single face. An emote reacts rather than sits there, and this is the only mark in the set with a real expression.',
  },
  {
    slug: 'h00',
    why: 'The ZZ is cut out of what the jar is holding, not out of its glass — so the letters only exist inside the fill.',
  },
  {
    slug: 'm00',
    why: 'The spindle hole is the gap between the two Zs, so the record itself sets the letterspacing.',
  },
  {
    slug: 'p00',
    why: 'A thin panel with the ZZ punched through it. The letters have no fill of their own; the ground comes through them.',
  },
  {
    slug: 'p02',
    why: 'A curved screen that keeps a mouth, so it stays a face rather than becoming a wordmark.',
  },
  {
    slug: 'm01',
    why: 'The groove does the work a bevel could not — one repeating texture says record without any other detail.',
  },
  {
    slug: 'm03',
    why: 'Two discs overlapping, which gives real depth from geometry rather than from a gradient.',
  },
  {
    slug: 'tw01',
    why: 'The safe option: the shipped bubble, drawn cleanly, with the smile kept.',
  },
  {
    slug: 'h07',
    why: 'The fill line is a wave rather than a rule, so the vessel reads as holding something that moves. The letters sit in the fill, not on the glass.',
  },
  {
    slug: 'h03',
    why: 'A barrel where each hoop is one bar of the letters — slide a hoop and its bar goes with it. The swell at the middle is what gives the diagonals their room.',
  },
];

export const SHORTLIST_SLUGS = SHORTLIST.map((p) => p.slug);
