export const SITE = 'https://hozz.brando.page';
export const GITHUB_URL = 'https://github.com/thatcube/hozz';
export const DONATE_URL = 'https://github.com/sponsors/thatcube';
export const LICENSE_URL = 'https://github.com/thatcube/hozz/blob/main/LICENSE';

/**
 * Hozz colours data by what the data is about. These hues are the site's whole
 * palette — every accent on the page is one of them, so scrolling the page
 * walks the same spectrum the app organises data with.
 */
export const CATEGORIES = [
  { key: 'heart', label: 'Heart', hue: '#DD6558', note: 'Rate, variability, ECG and averages' },
  { key: 'activity', label: 'Activity', hue: '#E8863A', note: 'Steps, distance, energy, exercise minutes, workouts' },
  { key: 'nutrition', label: 'Nutrition', hue: '#B8901F', note: 'Food, drink and nutrients' },
  { key: 'mobility', label: 'Mobility', hue: '#6C9F45', note: 'Walking speed, step length, asymmetry, stair speed' },
  { key: 'respiratory', label: 'Respiratory', hue: '#3F9E9E', note: 'Blood oxygen, respiratory rate, peak flow, VO₂ max' },
  { key: 'body', label: 'Body', hue: '#4A8FC0', note: 'Weight, height, body fat, lean mass, temperature' },
  { key: 'sleep', label: 'Sleep', hue: '#7477CB', note: 'Sleep stages and overnight readings' },
  { key: 'mind', label: 'Mind', hue: '#A173C4', note: 'Mindful minutes, state of mind, time in daylight' },
  { key: 'cycle', label: 'Cycle', hue: '#D5749B', note: 'Tracking, symptoms, basal temperature, test results' },
  { key: 'hearing', label: 'Hearing', hue: '#BC8049', note: 'Headphone and environmental audio exposure' },
] as const;

export type CategoryKey = (typeof CATEGORIES)[number]['key'];

/**
 * Real HealthKit identifiers, not invented ones. Showing the actual API names is
 * the honest version of "it reads a lot of things": anyone who knows HealthKit
 * can check the claim, and anyone who doesn't still reads the breadth. The
 * readings beside them are examples, and the page says so.
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
    { category: 'activity', id: 'appleStandTime', sample: '11 h' },
    { category: 'body', id: 'leanBodyMass', sample: '145.9 lb' },
    { category: 'heart', id: 'walkingHeartRateAverage', sample: '91 bpm' },
    { category: 'cycle', id: 'menstrualFlow', sample: 'light' },
    { category: 'mind', id: 'stateOfMind', sample: 'pleasant' },
    { category: 'mobility', id: 'stairAscentSpeed', sample: '0.5 m/s' },
    { category: 'nutrition', id: 'dietaryVitaminD', sample: '18 µg' },
    { category: 'sleep', id: 'appleSleepingBreathingDisturbances', sample: 'low' },
  ],
];

/** Three steps, in the order you actually do them. Kept to one line each. */
export const STEPS = [
  {
    category: 'heart' as CategoryKey,
    title: 'Add a destination',
    body: 'Choose your Mac, a folder, Home Assistant, InfluxDB, a URL or MQTT.',
  },
  {
    category: 'body' as CategoryKey,
    title: 'Pick types and a schedule',
    body: 'Choose what it receives and when.',
  },
  {
    category: 'mobility' as CategoryKey,
    title: 'Let it run',
    body: 'Each destination keeps its own queue position.',
  },
];

/**
 * The five real destinations, each anchored by a fact you could check: a
 * Bonjour service type, a port, a protocol. No invented ones.
 */
export const DESTINATIONS = [
  {
    category: 'mind' as CategoryKey,
    icon: 'mac',
    title: 'Your Mac',
    body: 'The companion app receives, stores and charts records.',
    fact: '_hozz._tcp · :54330',
  },
  {
    category: 'body' as CategoryKey,
    icon: 'folder',
    title: 'Folder',
    body: 'iCloud Drive, Dropbox, OneDrive, Google Drive, SMB, or on the device.',
    fact: 'Files picker',
  },
  {
    category: 'nutrition' as CategoryKey,
    icon: 'house',
    title: 'Home Assistant',
    body: 'Send metrics to a webhook or the REST API.',
    fact: 'Metrics JSON',
  },
  {
    category: 'respiratory' as CategoryKey,
    icon: 'globe',
    title: 'Web address',
    body: 'POST to any endpoint you run.',
    fact: 'POST · NDJSON / JSON / CSV / Metrics / line protocol',
  },
  {
    category: 'sleep' as CategoryKey,
    icon: 'globe',
    title: 'InfluxDB',
    body: 'Write line protocol directly.',
    fact: '/api/v2/write · 1.8 /write',
  },
  {
    category: 'heart' as CategoryKey,
    icon: 'broadcast',
    title: 'MQTT',
    body: 'Publish to your own broker.',
    fact: 'mqtt:// · mqtts:// · QoS 0',
  },
];

/** Genuinely tabular, so the page renders it as a table. */
export const FORMATS = [
  { name: 'NDJSON', use: 'Streaming and archives.', note: 'Lossless for encoded fields' },
  { name: 'SQLite', use: 'Queries and charts.', note: 'Lossless; each row keeps its raw record' },
  { name: 'JSON', use: 'One document.', note: 'Lossless' },
  { name: 'CSV', use: 'Spreadsheets.', note: 'Lossy; drops metadata and nested detail' },
  { name: 'Markdown', use: 'Daily notes.', note: 'Lossy; keeps summaries, not records' },
  { name: 'GPX', use: 'One track per workout with GPS, for maps.', note: 'A filter, not a projection — routes only' },
  { name: 'Metrics JSON', use: 'Dashboards and automation.', note: 'Values over time' },
];

/** Why an interruption can repeat work but cannot skip records. */
export const DURABILITY = [
  {
    title: 'Anchors, not date windows',
    body: 'Each type advances only after durable staging.',
    fact: 'HKAnchoredObjectQuery',
  },
  {
    title: 'Resumable',
    body: 'Manual exports resume from their last checkpoint.',
    fact: 'checkpointed',
  },
  {
    title: 'Retries are safe',
    body: 'Content-derived ids identify repeated batches.',
    fact: 'Idempotency-Key',
  },
  {
    title: 'Nothing is quietly dropped',
    body: 'Unreadable records are quarantined for a newer version.',
    fact: 'quarantine · promotion',
  },
];

/**
 * The states Apple's API actually lets an app report. The second one is the
 * entire reason the honesty section exists.
 */
export const COVERAGE_STATES = [
  { state: 'allowed', tone: 'good', body: 'Read and delivered.' },
  { state: 'denied or empty', tone: 'unknown', body: 'Apple will not say which. Hozz will not guess.' },
  { state: 'unavailable', tone: 'flat', body: 'Not readable now.' },
  { state: 'unsupported', tone: 'flat', body: 'Not handled yet.' },
  { state: 'failed', tone: 'bad', body: 'The read failed.' },
];

/**
 * What the Mac app's read-only MCP server covers. The exact tool list lives in
 * the repository's docs/mcp.md and moves, so this describes the ground it
 * covers rather than pinning a count that will go stale.
 */
export const MCP_TOOLS = [
  'types and overview',
  'aggregate buckets',
  'individual samples',
  'ECG waveforms',
  'audiograms',
  'mood entries',
  'medication adherence',
  'workouts',
  'trends and comparisons',
  'anomaly checks',
];

/** Written as refusals, because each one is a thing the app will not do. */
export const PROMISES = [
  { category: 'heart' as CategoryKey, title: 'Open source', body: 'GPL-3.0 with an App Store distribution exception.' },
  { category: 'activity' as CategoryKey, title: 'No account', body: 'No sign-in.' },
  { category: 'mobility' as CategoryKey, title: 'No analytics', body: 'No telemetry, ads or remote crash reports.' },
  { category: 'respiratory' as CategoryKey, title: 'No hosted relay', body: 'No Hozz server in the middle.' },
  { category: 'sleep' as CategoryKey, title: 'No default destination', body: 'Nothing leaves until you add one.' },
  { category: 'mind' as CategoryKey, title: 'Credentials on device', body: 'Destination keys stay in the device Keychain.' },
];

/** Early alpha: it works, and coverage is partial. Both halves are the truth. */
export const WORKING = [
  'Automatic export to six destinations',
  'Resumable manual export',
  'NDJSON, SQLite, JSON, CSV, Markdown and GPX',
  'ECG waveforms, audiograms, routes and moods',
  'Deletions carried as tombstones',
  'Mac app: receives, stores, charts',
  'Read-only MCP server for assistants',
  'Shortcuts and a home-screen widget',
  '520 XCTest tests',
];

export const NOT_YET = [
  'Every Health type',
  'Clinical records — compiled out of the default build',
  'Writing anything back into Apple Health, ever',
  'Handover between two devices',
  'Accessibility and localisation pass',
  'App Store release',
];

/** Question-shaped, so the answers can be marked up as an FAQPage. */
export const FAQ = [
  {
    q: 'Is Hozz open source?',
    a: 'Yes. Hozz is licensed under GPL-3.0 with an App Store distribution exception.',
  },
  {
    q: 'Where does my health data go?',
    a: 'Only to destinations you add and confirm. Hozz has no default destination or hosted relay.',
  },
  {
    q: 'Does it export in the background?',
    a: 'Yes, when iOS allows it. Most types are capped near hourly, and Health may be unreadable while the phone is locked.',
  },
  {
    q: 'Can I ask an AI about my data?',
    a: 'Yes, through the Mac app’s read-only MCP server. A cloud assistant may upload what it reads.',
  },
  {
    q: 'Can Hozz put data back into Apple Health?',
    a: 'No. Importing would replace the original source with Hozz and could duplicate records.',
  },
  {
    q: 'Why is there no progress percentage?',
    a: 'Health does not reveal a total without reading every record. Hozz reports completed types and date coverage instead.',
  },
];

export const SIBLINGS = [
  { name: 'Plozz', href: 'https://plozz.app', body: 'Jellyfin, Plex and Emby on Apple TV' },
  { name: 'Mozz', href: 'https://github.com/thatcube/Mozz', body: 'Your music, wherever it lives' },
  { name: 'Twozz', href: 'https://github.com/thatcube/Twozz', body: 'Twitch on Apple TV' },
];

/**
 * The site's two surfaces, and the chrome that has to agree about them.
 *
 * The header, the footer and the 404 page all read this, so "the marketing
 * page and the documentation" is one list rather than three that drift. Each
 * surface names the other: from anywhere on the homepage the way into the
 * documentation is one link, and from anywhere in the documentation the way
 * back out is one link. `label` is what the chrome says; `badge` is the word
 * that sits beside the wordmark while you are inside that surface.
 */
export const SURFACES = {
  home: { href: '/', label: 'Home', badge: undefined },
  docs: { href: '/docs/', label: 'Docs', badge: 'Docs' },
} as const;

export type SurfaceKey = keyof typeof SURFACES;

/**
 * The homepage's own sections, in the order they appear on it.
 *
 * The header shows them where there is room and the footer lists them where
 * there is not, so a phone can still jump down the page rather than only
 * scroll it.
 */
export const HOME_SECTIONS = [
  { href: '#data', label: 'What it reads' },
  { href: '#destinations', label: 'Destinations' },
  { href: '#formats', label: 'Formats' },
  { href: '#how', label: 'How it works' },
  { href: '#status', label: 'Status' },
];
