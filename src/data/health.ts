/**
 * Variation B — the Health design language.
 *
 * The conceit: Hozz is about Apple Health, so the site is built in Health's own
 * visual idiom — gradient category tiles, ambient hue washes, white cards on
 * grey, one typeface at many weights. That is an argument, not decoration. The
 * grid on this page is the shape of what Health holds; Hozz's whole job is
 * getting a copy of it somewhere you own.
 *
 * Nothing here depicts the Hozz app. Hozz is pre-alpha and has no shipped UI,
 * and a mock of one would be the single dishonest thing on a site about
 * honesty. Every surface below describes the *source* of the data.
 *
 * Gradients are read off the real Browse screen so the categories stay
 * recognisable to anyone who has opened Health.
 */

export interface HealthCategory {
  key: string;
  label: string;
  icon: string;
  from: string;
  to: string;
  /** What the category actually holds, in plain words. */
  note: string;
}

export const HEALTH_CATEGORIES: HealthCategory[] = [
  { key: 'activity', label: 'Activity', icon: 'ph:fire', from: '#FF8A3D', to: '#F04E23', note: 'Steps, distance, energy, exercise minutes, workouts and their routes' },
  { key: 'body', label: 'Body Measurements', icon: 'ph:person-arms-spread', from: '#C960E8', to: '#B32DD6', note: 'Weight, height, body fat, lean mass, waist, temperature' },
  { key: 'cycle', label: 'Cycle Tracking', icon: 'ph:circles-three', from: '#6B6AE2', to: '#8A75EA', note: 'Tracking, symptoms, basal temperature, test results' },
  { key: 'hearing', label: 'Hearing', icon: 'ph:ear', from: '#5BA4F5', to: '#3B87E8', note: 'Headphone and environmental audio exposure, audiograms' },
  { key: 'heart', label: 'Heart', icon: 'ph:heart', from: '#F26B78', to: '#E8455F', note: 'Rate, variability, ECG, resting and walking averages' },
  { key: 'medications', label: 'Medications', icon: 'ph:pill', from: '#74C8EC', to: '#4FB3DC', note: 'What you take, when you took it, and what you skipped' },
  { key: 'mind', label: 'Mental Wellbeing', icon: 'ph:brain', from: '#63CDB4', to: '#45BCA0', note: 'Mindful minutes, state of mind, time in daylight' },
  { key: 'mobility', label: 'Mobility', icon: 'ph:arrows-left-right', from: '#F5AC5C', to: '#E88F3C', note: 'Walking speed, step length, asymmetry, stair speed' },
  { key: 'nutrition', label: 'Nutrition', icon: 'ph:bowl-food', from: '#84D169', to: '#5DBF48', note: 'Everything you log to eat and drink, down to the micronutrient' },
  { key: 'respiratory', label: 'Respiratory', icon: 'ph:wind', from: '#74C9E6', to: '#4FB6D8', note: 'Blood oxygen, respiratory rate, peak flow, VO₂ max' },
  { key: 'sleep', label: 'Sleep', icon: 'ph:bed', from: '#6E6CE4', to: '#6A63E0', note: 'Every stage, every night, from wherever you record it' },
  { key: 'symptoms', label: 'Symptoms', icon: 'ph:person-simple-circle', from: '#8A72EC', to: '#6D57DE', note: 'Everything you have ever noted feeling, and when' },
  { key: 'vitals', label: 'Vitals', icon: 'ph:pulse', from: '#F0616E', to: '#E63E52', note: 'Blood pressure, glucose, body temperature, oxygen' },
  { key: 'other', label: 'Other Data', icon: 'ph:plus', from: '#4A9AF0', to: '#2F80E8', note: 'Everything Apple files nowhere else, and lab results' },
];

export const CATEGORY_BY_KEY = Object.fromEntries(
  HEALTH_CATEGORIES.map((c) => [c.key, c]),
) as Record<string, HealthCategory>;

/**
 * The detail panel. Real HealthKit identifiers with plausible readings — the
 * numbers are illustrative, the type names are not. Anyone who knows HealthKit
 * can check every one of them.
 */
export interface DetailRow {
  name: string;
  identifier: string;
  value: string;
  unit: string;
  time: string;
  /** Relative bar heights, 0–1, newest last. */
  spark: number[];
}

export const HEART_ROWS: DetailRow[] = [
  {
    name: 'Heart Rate',
    identifier: 'heartRate',
    value: '62',
    unit: 'BPM',
    time: '2:29 PM',
    spark: [0.5, 0.72, 0.4, 0.86, 0.55, 0.34, 0.68, 0.44, 0.62],
  },
  {
    name: 'Heart Rate Variability',
    identifier: 'heartRateVariabilitySDNN',
    value: '48',
    unit: 'ms',
    time: '6:02 AM',
    spark: [0.42, 0.55, 0.68, 0.5, 0.74, 0.6, 0.38, 0.66, 0.52],
  },
  {
    name: 'Resting Heart Rate',
    identifier: 'restingHeartRate',
    value: '54',
    unit: 'BPM',
    time: 'Today',
    spark: [0.6, 0.58, 0.63, 0.55, 0.5, 0.57, 0.48, 0.52, 0.46],
  },
  {
    name: 'Electrocardiogram',
    identifier: 'electrocardiogram',
    value: 'Sinus rhythm',
    unit: '',
    time: 'Jul 28',
    spark: [],
  },
];

/** Things Hozz refuses to do, as a grouped list. */
export const PROMISE_ROWS = [
  { icon: 'ph:cloud-slash', tint: '#F26B78', title: 'No server of mine', body: 'No relay, no database, no cloud. Nothing in the middle to trust.' },
  { icon: 'ph:user-circle-dashed', tint: '#FF8A3D', title: 'No account', body: 'Nothing to sign up for, because there is nothing to sign up to.' },
  { icon: 'ph:chart-line-down', tint: '#5DBF48', title: 'No analytics', body: 'No tracking, no telemetry, no crash reports with your health in them.' },
  { icon: 'ph:currency-dollar-simple', tint: '#4FB6D8', title: 'No subscription', body: 'No paywall, no Pro tier. Hozz has nothing to sell you later.' },
  { icon: 'ph:cloud-x', tint: '#6E6CE4', title: 'Nothing put in iCloud', body: 'Where a copy lands is your call, never a default of mine.' },
  { icon: 'ph:lock-simple', tint: '#8A72EC', title: 'Credentials stay put', body: 'Keys for your own server live in that device’s Keychain, unsynced.' },
];

export const STEP_ROWS = [
  {
    n: '1',
    tint: '#F26B78',
    title: 'You decide what it reads',
    body: 'iOS asks, not Hozz. Tick what you want to take with you and leave the rest closed.',
  },
  {
    n: '2',
    tint: '#C960E8',
    title: 'It keeps up quietly',
    body: 'Each type resumes from where it stopped, so nothing arrives twice and nothing is skipped.',
  },
  {
    n: '3',
    tint: '#5DBF48',
    title: 'It writes where you say',
    body: 'A file you keep or a server you run. Nothing leaves until you set up a destination and confirm it.',
  },
];

export const DESTINATION_ROWS = [
  {
    icon: 'ph:file-arrow-down',
    tint: '#4A9AF0',
    title: 'A file you keep',
    body: 'Written in parts with a manifest, so an interrupted export can never look finished.',
  },
  {
    icon: 'ph:hard-drives',
    tint: '#4FB6D8',
    title: 'A server you run',
    body: 'TLS first, credentials scoped to one destination and never handed to an off-host redirect.',
  },
  {
    icon: 'ph:table',
    tint: '#5DBF48',
    title: 'CSV and GPX',
    body: 'Labelled lossy projections, because that is what they are. The full record stays whole.',
  },
];

/** The three states Apple's API actually permits an app to tell apart. */
export const COVERAGE_ROWS = [
  { state: 'Allowed', tone: 'good', body: 'You granted it, and every object HealthKit returned is accounted for.' },
  { state: 'Denied or empty', tone: 'unknown', body: 'Apple will not say which. Hozz will not guess, so it reports both.' },
  { state: 'Not supported yet', tone: 'flat', body: 'Hozz cannot read it correctly yet, so it says so instead of skipping it quietly.' },
];

export const MILESTONE_ROWS = [
  { id: 'M0', name: 'Contract', state: 'done', body: 'Every HealthKit family classified; privacy and threat models written down.' },
  { id: 'M1', name: 'Foundation', state: 'now', body: 'Swift 6 targets build, and fault tests prove a retry cannot skip past data.' },
  { id: 'M2', name: 'Catalogue', state: 'next', body: 'The full type list, with the awkward authorization flows kept separate.' },
  { id: 'M3', name: 'Canonical model', state: 'next', body: 'Byte-identical output whatever your locale or time zone.' },
  { id: 'M4', name: 'Acquisition', state: 'next', body: 'Millions of changes survive cancellation and injected crashes.' },
  { id: 'M5', name: 'Files', state: 'next', body: 'Manifests that verify every part and disclose every limitation.' },
  { id: 'M6', name: 'Background', state: 'next', body: 'Tested on real devices through lock, reboot and lost network.' },
  { id: 'M7', name: 'Delivery', state: 'next', body: 'Idempotent batches reconciled against an open-source reference receiver.' },
  { id: 'M8', name: 'Multi-device', state: 'next', body: 'One writer at a time, with an explicit handover between your devices.' },
  { id: 'M9', name: 'Release', state: 'next', body: 'Accessibility, localisation, and a multi-year endurance run.' },
];
