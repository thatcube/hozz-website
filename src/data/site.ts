export const SITE = 'https://hozz.brandomoore.com';
export const GITHUB_URL = 'https://github.com/thatcube/hozz';
export const DONATE_URL = 'https://github.com/sponsors/thatcube';
export const LICENSE_URL = 'https://github.com/thatcube/hozz/blob/main/LICENSE';

/**
 * Hozz colours data by what the data is about. These hues are the site's whole
 * palette — every accent on the page is one of them, so scrolling the page
 * walks the same spectrum the app organises data with.
 */
export const CATEGORIES = [
  { key: 'heart', label: 'Heart', hue: '#DD6558', note: 'Rate, variability, ECG, resting and walking averages' },
  { key: 'activity', label: 'Activity', hue: '#E8863A', note: 'Steps, distance, energy, exercise minutes, workouts' },
  { key: 'nutrition', label: 'Nutrition', hue: '#B8901F', note: 'Everything you log to eat and drink, down to the micronutrient' },
  { key: 'mobility', label: 'Mobility', hue: '#6C9F45', note: 'Walking speed, step length, asymmetry, stair speed' },
  { key: 'respiratory', label: 'Respiratory', hue: '#3F9E9E', note: 'Blood oxygen, respiratory rate, peak flow, VO₂ max' },
  { key: 'body', label: 'Body', hue: '#4A8FC0', note: 'Weight, height, body fat, lean mass, temperature' },
  { key: 'sleep', label: 'Sleep', hue: '#7477CB', note: 'Every stage, every night, from wherever you record it' },
  { key: 'mind', label: 'Mind', hue: '#A173C4', note: 'Mindful minutes, state of mind, time in daylight' },
  { key: 'cycle', label: 'Cycle', hue: '#D5749B', note: 'Tracking, symptoms, basal temperature, test results' },
  { key: 'hearing', label: 'Hearing', hue: '#BC8049', note: 'Headphone and environmental audio exposure' },
] as const;

export type CategoryKey = (typeof CATEGORIES)[number]['key'];

/**
 * Real HealthKit identifiers, not invented ones. Showing the actual API names is
 * the honest version of "it reads a lot of things": anyone who knows HealthKit
 * can check the claim, and anyone who doesn't still reads the breadth.
 */
export const STREAM_LANES: { category: CategoryKey; id: string; sample: string }[][] = [
  [
    { category: 'heart', id: 'heartRateVariabilitySDNN', sample: '48 ms' },
    { category: 'activity', id: 'stepCount', sample: '8,241' },
    { category: 'sleep', id: 'sleepAnalysis', sample: '7h 12m' },
    { category: 'body', id: 'bodyMass', sample: '178.4 lb' },
    { category: 'respiratory', id: 'oxygenSaturation', sample: '97%' },
    { category: 'mind', id: 'mindfulSession', sample: '10 min' },
    { category: 'nutrition', id: 'dietaryProtein', sample: '112 g' },
    { category: 'mobility', id: 'walkingAsymmetryPercentage', sample: '1.2%' },
  ],
  [
    { category: 'activity', id: 'activeEnergyBurned', sample: '612 kcal' },
    { category: 'heart', id: 'restingHeartRate', sample: '54 bpm' },
    { category: 'hearing', id: 'headphoneAudioExposure', sample: '68 dB' },
    { category: 'cycle', id: 'basalBodyTemperature', sample: '97.9°F' },
    { category: 'respiratory', id: 'vo2Max', sample: '44.1' },
    { category: 'body', id: 'bodyFatPercentage', sample: '18.2%' },
    { category: 'sleep', id: 'appleSleepingWristTemperature', sample: '+0.3°F' },
    { category: 'activity', id: 'appleExerciseTime', sample: '38 min' },
  ],
  [
    { category: 'mobility', id: 'walkingSpeed', sample: '3.1 mph' },
    { category: 'heart', id: 'electrocardiogram', sample: 'sinus rhythm' },
    { category: 'nutrition', id: 'dietaryWater', sample: '2.4 L' },
    { category: 'mind', id: 'timeInDaylight', sample: '96 min' },
    { category: 'activity', id: 'workoutRoute', sample: '6.2 mi' },
    { category: 'respiratory', id: 'respiratoryRate', sample: '14 br/min' },
    { category: 'hearing', id: 'environmentalAudioExposure', sample: '71 dB' },
    { category: 'body', id: 'bodyTemperature', sample: '98.4°F' },
  ],
  [
    { category: 'sleep', id: 'appleSleepingBreathingDisturbances', sample: 'low' },
    { category: 'body', id: 'leanBodyMass', sample: '145.9 lb' },
    { category: 'heart', id: 'walkingHeartRateAverage', sample: '91 bpm' },
    { category: 'cycle', id: 'menstrualFlow', sample: 'light' },
    { category: 'mind', id: 'stateOfMind', sample: 'pleasant' },
    { category: 'mobility', id: 'stairAscentSpeed', sample: '0.5 m/s' },
    { category: 'nutrition', id: 'dietaryVitaminD', sample: '18 µg' },
    { category: 'activity', id: 'appleStandTime', sample: '11 h' },
  ],
];

/**
 * Written as promises rather than features, because every one of them is a thing
 * the app refuses to do. Taken from the repository's product promise.
 */
export const PROMISES = [
  {
    category: 'heart' as CategoryKey,
    title: 'No subscription',
    body: 'No paywall, no Pro tier, no feature held back. Hozz has nothing to sell you later.',
  },
  {
    category: 'activity' as CategoryKey,
    title: 'No account',
    body: 'Nothing to sign up for, because there is nothing on the other end to sign up to.',
  },
  {
    category: 'mobility' as CategoryKey,
    title: 'No analytics',
    body: 'No tracking, no telemetry, and no crash reports with your health inside them.',
  },
  {
    category: 'respiratory' as CategoryKey,
    title: 'No server of mine',
    body: 'No relay, no database, no cloud. There is nothing in the middle for you to trust.',
  },
  {
    category: 'sleep' as CategoryKey,
    title: 'Nothing put in iCloud',
    body: 'Hozz never stores your Health data there. Where a copy lands is your call, not a default.',
  },
  {
    category: 'mind' as CategoryKey,
    title: 'Credentials stay put',
    body: 'Anything you use to reach your own server lives in the Keychain on that device, unsynced.',
  },
];

export const STEPS = [
  {
    category: 'heart' as CategoryKey,
    title: 'You decide what it can read',
    body:
      'iOS asks, not Hozz. Tick the data you want to take with you and leave the rest closed. ' +
      'Change your mind whenever you like.',
  },
  {
    category: 'body' as CategoryKey,
    title: 'It keeps up quietly',
    body:
      'Hozz reads each kind of data from where it last stopped, so nothing arrives twice and nothing ' +
      'gets skipped. Close it mid-export and it picks the thread back up.',
  },
  {
    category: 'mobility' as CategoryKey,
    title: 'It writes where you say',
    body:
      'A file you save, a server you run, a computer on your desk. Nothing leaves until you have set ' +
      'up a destination and confirmed it.',
  },
];

export const DESTINATIONS = [
  {
    category: 'body' as CategoryKey,
    icon: 'ph:file-arrow-down-duotone',
    title: 'A file you keep',
    body: 'Written in parts with a manifest, so an export that was interrupted can never look finished.',
  },
  {
    category: 'respiratory' as CategoryKey,
    icon: 'ph:hard-drives-duotone',
    title: 'A server you run',
    body: 'TLS first, with credentials scoped to one destination and never handed to a redirect off-host.',
  },
  {
    category: 'nutrition' as CategoryKey,
    icon: 'ph:table-duotone',
    title: 'CSV and JSON',
    body: 'Labelled as lossy projections, because that is what they are. The full record stays whole.',
  },
  {
    category: 'mind' as CategoryKey,
    icon: 'ph:desktop-duotone',
    title: 'Your own Mac',
    body: 'A companion app receives straight from your phone over your own network, and finds it without an address to type.',
  },
  {
    category: 'heart' as CategoryKey,
    icon: 'ph:sparkle-duotone',
    title: 'An AI you choose',
    body: 'Your Mac can answer questions about your own data through the Model Context Protocol, reading locally.',
  },
];

/**
 * The three states Apple's API actually lets an app tell apart. The middle one
 * is the entire reason the honesty section exists.
 */
export const COVERAGE_STATES = [
  {
    state: 'allowed',
    tone: 'good',
    body: 'You granted it, and every object HealthKit returned is accounted for.',
  },
  {
    state: 'denied or empty',
    tone: 'unknown',
    body: 'Apple will not say which of the two it is. Hozz will not guess, so it reports both.',
  },
  {
    state: 'not supported yet',
    tone: 'flat',
    body: 'Hozz cannot read it correctly yet, so it says so rather than quietly skipping it.',
  },
];

export const MILESTONES = [
  { id: 'M0', name: 'Contract', state: 'done', body: 'Every HealthKit family classified; privacy and threat models written down.' },
  { id: 'M1', name: 'Foundation', state: 'done', body: 'The Swift 6 targets build, and fault tests prove a retry cannot skip past data.' },
  { id: 'M2', name: 'Catalogue', state: 'done', body: 'The full type list, with the awkward authorization flows kept separate.' },
  { id: 'M3', name: 'Canonical model', state: 'done', body: 'Byte-identical output whatever your locale or time zone.' },
  { id: 'M4', name: 'Acquisition', state: 'done', body: 'Millions of changes survive cancellation and injected crashes.' },
  { id: 'M5', name: 'Files', state: 'done', body: 'Archives that verify every part and disclose every limitation.' },
  { id: 'M6', name: 'Background', state: 'now', body: 'Automatic sync ships and survives lock, reboot and lost network. The long endurance run on real devices is still under way.' },
  { id: 'M7', name: 'Delivery', state: 'done', body: 'Idempotent batches reconciled against an open-source reference receiver, plus a Mac app that receives them directly.' },
  { id: 'M8', name: 'Multi-device', state: 'next', body: 'One writer at a time, with an explicit handover between your devices.' },
  { id: 'M9', name: 'Release', state: 'next', body: 'Accessibility, localisation, and a multi-year endurance run.' },
];

export const SIBLINGS = [
  { name: 'Plozz', href: 'https://plozz.app', body: 'Jellyfin, Plex and Emby on Apple TV' },
  { name: 'Mozz', href: 'https://github.com/thatcube/Mozz', body: 'Your music, wherever it lives' },
  { name: 'Twozz', href: 'https://github.com/thatcube/Twozz', body: 'Twitch on Apple TV' },
];

export const NAV_LINKS = [
  { href: '#promise', label: 'The promise' },
  { href: '#how', label: 'How it works' },
  { href: '#honest', label: 'Honesty' },
  { href: '#status', label: 'Status' },
];
