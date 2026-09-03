/**
 * Variation B — the Health design language.
 *
 * The conceit: Hozz is about Apple Health, so the site is built in Health's own
 * visual idiom — gradient category tiles, ambient hue washes, white cards on
 * grey, one typeface at many weights. That is an argument, not decoration. The
 * grid on this page is the shape of what Health holds; Hozz's whole job is
 * getting a copy of it somewhere you own.
 *
 * Nothing here depicts the Hozz app. Hozz’s UI is not public,
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

/** Things Hozz refuses to do, as a grouped list. */
export const PROMISE_ROWS = [
  { icon: 'ph:cloud-slash', tint: '#F26B78', title: 'No hosted relay', body: 'No Hozz-hosted service routes or stores records.' },
  { icon: 'ph:user-circle-dashed', tint: '#FF8A3D', title: 'No account', body: 'Nothing to sign up for today.' },
  { icon: 'ph:chart-line-down', tint: '#5DBF48', title: 'No analytics', body: 'No tracking, telemetry or ads.' },
  { icon: 'ph:code', tint: '#4FB6D8', title: 'Open source', body: 'GPL-3.0 with an App Store distribution exception.' },
  { icon: 'ph:cloud-x', tint: '#6E6CE4', title: 'No default destination', body: 'You choose where every copy goes.' },
  { icon: 'ph:lock-simple', tint: '#8A72EC', title: 'Credentials on device', body: 'Destination secrets stay in Keychain.' },
];

export const STEP_ROWS = [
  {
    n: '1',
    tint: '#F26B78',
    title: 'Choose what it reads',
    body: 'Grant only the Health permissions you want.',
  },
  {
    n: '2',
    tint: '#C960E8',
    title: 'Resume safely',
    body: 'Each type resumes from a durable cursor. Retries may repeat, never skip.',
  },
  {
    n: '3',
    tint: '#5DBF48',
    title: 'Choose where it writes',
    body: 'Nothing leaves until you confirm a destination.',
  },
];

export const DESTINATION_ROWS = [
  {
    icon: 'ph:file-arrow-down',
    tint: '#4A9AF0',
    title: 'A file you keep',
    body: 'Parts and a manifest expose interrupted exports.',
  },
  {
    icon: 'ph:hard-drives',
    tint: '#4FB6D8',
    title: 'A server you run',
    body: 'TLS first. Credentials stay scoped to one destination.',
  },
  {
    icon: 'ph:table',
    tint: '#5DBF48',
    title: 'CSV and GPX',
    body: 'Lossy projections, labelled before export.',
  },
];

/** The three states Apple's API actually permits an app to tell apart. */
export const COVERAGE_ROWS = [
  { state: 'Allowed', tone: 'good', body: 'You granted it, and every object HealthKit returned is accounted for.' },
  { state: 'Denied or empty', tone: 'unknown', body: 'Apple will not say which. Hozz will not guess, so it reports both.' },
  { state: 'Not supported yet', tone: 'flat', body: 'Hozz cannot read it correctly yet, so it says so instead of skipping it quietly.' },
];
