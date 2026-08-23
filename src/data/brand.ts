/**
 * The family.
 *
 * Four apps, one suffix. **ZZ is the identity** — it is the only thing every
 * product name shares, and it is what a system has to carry. The pixel smiley
 * was one expression of that, not the thing itself.
 *
 * Each direction renders all four apps so cohesion can actually be judged. A
 * mark that only works for one of them has not solved the problem.
 */

export interface App {
  key: 'plozz' | 'mozz' | 'twozz' | 'hozz';
  name: string;
  what: string;
  /** What the mark should evoke, if it evokes anything beyond the ZZ. */
  motif: string;
  /** Established hue. Plozz, Mozz and Twozz ship these; Hozz is open. */
  hue: string;
  deep: string;
  light: string;
}

export const APPS: App[] = [
  {
    key: 'plozz',
    name: 'Plozz',
    what: 'Media player for Jellyfin, Plex and Emby',
    motif: 'watching — a screen, a frame, play',
    hue: '#00a4dc',
    deep: '#00506d',
    light: '#7fd6f5',
  },
  {
    key: 'mozz',
    name: 'Mozz',
    what: 'Music for Plex and Jellyfin',
    motif: 'sound — a disc, a wave, a groove',
    hue: '#e0243f',
    deep: '#6d0f1e',
    light: '#f58a99',
  },
  {
    key: 'twozz',
    name: 'Twozz',
    what: 'Live streams and chat on Apple TV',
    motif: 'live — a signal, a bubble, presence',
    hue: '#8f52f6',
    deep: '#3d1d75',
    light: '#c9a9fb',
  },
  {
    key: 'hozz',
    name: 'Hozz',
    what: 'Apple Health export to destinations you own',
    motif: 'keeping — a vessel, a copy, breath',
    hue: '#12b39a',
    deep: '#08574b',
    light: '#82e5d3',
  },
];

export const APP_BY_KEY = Object.fromEntries(APPS.map((a) => [a.key, a])) as Record<App['key'], App>;
export type AppKey = App['key'];
