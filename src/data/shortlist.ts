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
    slug: 'tw08',
    why: 'The best thing on the board. A head tilted mid-laugh with the mouth wide open — the only mark in the whole set that has an actual expression, and expression is what a chat app is for.',
  },
  {
    slug: 'tw15',
    why: 'The head is not a circle, which is where the character came from. A jaw with real corners, and the grin cut straight out of it.',
  },
  {
    slug: 'tw07',
    why: 'The face repeats as a receding echo — what a chat looks like when one emote gets spammed. No other app in the family could use this.',
  },
  {
    slug: 'tw13',
    why: 'The repeat is the mark rather than decoration behind it: the face is bored once through a pile of three, so the letters belong to no single copy. The step and the fade are both taken from the Z\u2019s own diagonal.',
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
    why: 'The panel is turned away from you, so it has a front face and a foreshortened side. The letters turn with it, which is why they cannot be lifted off.',
  },
  {
    slug: 'm01',
    why: 'The cut runs wider than the record and is stopped by the rim, so the disc decides where the letters end.',
  },
  {
    slug: 'm03',
    why: 'The record is raked away and the slot rakes with it — depth from geometry rather than from a gradient.'
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
