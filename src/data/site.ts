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
    body: 'Your Mac, a folder, Home Assistant, InfluxDB, a URL, or MQTT. Test it before you trust it.',
  },
  {
    category: 'body' as CategoryKey,
    title: 'Pick types and a schedule',
    body: 'Per destination: which Health types, and how often — on arrival, hourly, daily or manual.',
  },
  {
    category: 'mobility' as CategoryKey,
    title: 'Walk away',
    body: 'New records go on their own. Each destination keeps its own place in the queue.',
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
    body: 'Run the companion Mac app and your phone finds it on your own network — no address to type.',
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
    body: 'Metrics land on your own dashboard as a webhook or REST call.',
    fact: 'Metrics JSON',
  },
  {
    category: 'respiratory' as CategoryKey,
    icon: 'globe',
    title: 'Web address',
    body: 'Your endpoint, your format. Hozz posts and retries safely.',
    fact: 'POST · NDJSON / JSON / CSV / Metrics / line protocol',
  },
  {
    category: 'sleep' as CategoryKey,
    icon: 'globe',
    title: 'InfluxDB',
    body: 'Line protocol written straight in, so Grafana needs no translator.',
    fact: '/api/v2/write · 1.8 /write',
  },
  {
    category: 'heart' as CategoryKey,
    icon: 'broadcast',
    title: 'MQTT',
    body: 'Published to your own broker for anything else you run.',
    fact: 'mqtt:// · mqtts:// · QoS 0',
  },
];

/** Genuinely tabular, so the page renders it as a table. */
export const FORMATS = [
  { name: 'NDJSON', use: 'The default. One record per line, streamable.', note: 'Lossless for encoded fields' },
  { name: 'SQLite', use: 'Query it in Datasette, DuckDB, pandas or Grafana.', note: 'Lossless — every row keeps its original record in raw' },
  { name: 'JSON', use: 'One document, whole records.', note: 'Lossless' },
  { name: 'CSV', use: 'Spreadsheets and quick charts.', note: 'Lossy — a grid cannot hold metadata or nested workout detail' },
  { name: 'Markdown', use: 'One note a day, for Obsidian and journals.', note: 'Lossy — a day’s totals, never the records behind them' },
  { name: 'GPX', use: 'One track per workout with GPS, for maps.', note: 'A filter, not a projection — routes only' },
  { name: 'Metrics JSON', use: 'Dashboards, Home Assistant and MQTT.', note: 'Values over time' },
];

/** Why an interruption can repeat work but cannot skip records. */
export const DURABILITY = [
  {
    title: 'Anchors, not date windows',
    body: 'Each type has its own opaque anchor, advanced only once records are durably staged.',
    fact: 'HKAnchoredObjectQuery',
  },
  {
    title: 'Resumable',
    body: 'Quit it, reboot, background it. A manual export carries on from its last checkpoint.',
    fact: 'checkpointed',
  },
  {
    title: 'Retries are safe',
    body: 'Content-derived ids mean the same record twice is still one record.',
    fact: 'Idempotency-Key',
  },
  {
    title: 'Nothing is quietly dropped',
    body: 'A record this version cannot parse is quarantined, then added once a newer one can read it.',
    fact: 'quarantine · promotion',
  },
];

/**
 * The states Apple's API actually lets an app report. The second one is the
 * entire reason the honesty section exists.
 */
export const COVERAGE_STATES = [
  { state: 'allowed', tone: 'good', body: 'Granted, read, and delivered.' },
  { state: 'denied or empty', tone: 'unknown', body: 'Apple will not say which. Hozz will not guess.' },
  { state: 'unavailable', tone: 'flat', body: 'Not readable right now — a locked phone, for one.' },
  { state: 'unsupported', tone: 'flat', body: 'Not handled correctly yet, so it says so.' },
  { state: 'failed', tone: 'bad', body: 'It tried and it did not work. Named, not buried.' },
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
  { category: 'heart' as CategoryKey, title: 'No subscription', body: 'Nothing held back for a Pro tier.' },
  { category: 'activity' as CategoryKey, title: 'No account', body: 'Nothing to sign up to.' },
  { category: 'mobility' as CategoryKey, title: 'No analytics', body: 'No telemetry, no ads, no crash payloads.' },
  { category: 'respiratory' as CategoryKey, title: 'No server of mine', body: 'No relay in the middle.' },
  { category: 'sleep' as CategoryKey, title: 'No default destination', body: 'Nothing leaves until you add one.' },
  { category: 'mind' as CategoryKey, title: 'No synced credentials', body: 'Your keys stay in that device’s Keychain.' },
];

/** Early alpha: it works, and coverage is partial. Both halves are the truth. */
export const WORKING = [
  'Automatic export to six kinds of destination',
  'Manual export, resumable after a crash',
  'NDJSON, SQLite, JSON, CSV, Markdown and GPX',
  'ECG waveforms, audiograms, routes and moods',
  'Deletions carried as tombstones',
  'Mac app: receives, stores, charts',
  'Read-only MCP server for assistants',
  'Shortcuts and a home-screen widget',
  '475 XCTest tests',
];

export const NOT_YET = [
  'Every Health type — coverage is partial',
  'Clinical records — compiled out of the default build',
  'Writing anything back into Apple Health, ever',
  'Handover between two devices',
  'Accessibility and localisation pass',
  'App Store release',
];

/** Question-shaped, so the answers can be marked up as an FAQPage. */
export const FAQ = [
  {
    q: 'Is Hozz free?',
    a: 'Yes. Free and open source under GPL-3.0, with no subscription, no account and no paid tier planned.',
  },
  {
    q: 'Where does my health data go?',
    a: 'Only where you send it. There is no default destination and no server of mine — nothing leaves your phone until you add a destination and confirm it.',
  },
  {
    q: 'Does it export in the background?',
    a: 'Yes. iOS decides when background work runs, so most types land near hourly, and Health cannot be read while your phone is locked.',
  },
  {
    q: 'Can I ask an AI about my data?',
    a: 'On your Mac, yes. Hozz ships a read-only MCP server that reads the database your phone keeps current, so a question costs a lookup rather than re-parsing a stale XML export. It cannot change or delete anything — but a cloud assistant may upload whatever it reads, which is the assistant’s behaviour, not Hozz’s.',
  },
  {
    q: 'Can Hozz put data back into Apple Health?',
    a: 'No, and it never will. Health stamps every sample with the app that wrote it, so a reading your Watch took in 2019 would come back indistinguishable from one Hozz invented — which destroys the provenance an archive exists to protect. HealthKit also has no way to say “store this unless it is already there”, so importing twice would silently double everything.',
  },
  {
    q: 'Why is there no progress percentage?',
    a: 'Because it would be invented. Health will not say how many records a type holds without reading all of them, so Hozz reports how many types are complete and how far back they reach, and never shows a fraction it cannot know.',
  },
];

export const SIBLINGS = [
  { name: 'Plozz', href: 'https://plozz.app', body: 'Jellyfin, Plex and Emby on Apple TV' },
  { name: 'Mozz', href: 'https://github.com/thatcube/Mozz', body: 'Your music, wherever it lives' },
  { name: 'Twozz', href: 'https://github.com/thatcube/Twozz', body: 'Twitch on Apple TV' },
];

export const NAV_LINKS = [
  { href: '#export', label: 'How to export' },
  { href: '#destinations', label: 'Destinations' },
  { href: '#honest', label: 'Honesty' },
  { href: '#status', label: 'Status' },
];
