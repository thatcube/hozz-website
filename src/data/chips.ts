/**
 * Chips for the visualisation lab.
 *
 * Friendly name for the reader, real HealthKit identifier underneath, and the
 * category hue Apple already uses for it. Every identifier here is real, so the
 * pictures stay checkable even while they are only sketches.
 */
export interface Chip {
  /** What a person calls it. */
  name: string;
  /** What HealthKit calls it. */
  id: string;
  /** Category hue variable, without the `--h-` prefix. */
  cat: string;
}

export const CHIPS: Chip[] = [
  { name: 'Heart Rate', id: 'heartRate', cat: 'heart' },
  { name: 'Resting Heart Rate', id: 'restingHeartRate', cat: 'heart' },
  { name: 'Steps', id: 'stepCount', cat: 'activity' },
  { name: 'Active Energy', id: 'activeEnergyBurned', cat: 'activity' },
  { name: 'Sleep', id: 'sleepAnalysis', cat: 'sleep' },
  { name: 'Weight', id: 'bodyMass', cat: 'body' },
  { name: 'Blood Oxygen', id: 'oxygenSaturation', cat: 'respiratory' },
  { name: 'Respiratory Rate', id: 'respiratoryRate', cat: 'respiratory' },
  { name: 'Walking Speed', id: 'walkingSpeed', cat: 'mobility' },
  { name: 'Mindful Minutes', id: 'mindfulSession', cat: 'mind' },
  { name: 'VO₂ Max', id: 'vo2Max', cat: 'respiratory' },
  { name: 'Blood Glucose', id: 'bloodGlucose', cat: 'vitals' },
  { name: 'Protein', id: 'dietaryProtein', cat: 'nutrition' },
  { name: 'Headphone Audio', id: 'headphoneAudioExposure', cat: 'hearing' },
];

/** Names only, for the wheel. Enough to read as "all of it, not a dozen". */
export const TYPE_NAMES: string[] = [
  'Heart Rate', 'Resting Heart Rate', 'Heart Rate Variability', 'Walking Heart Rate',
  'Electrocardiogram', 'Blood Oxygen', 'Respiratory Rate', 'VO₂ Max', 'Steps',
  'Active Energy', 'Exercise Minutes', 'Stand Hours', 'Workouts', 'Walking Speed',
  'Step Length', 'Stair Speed', 'Sleep', 'Time in Daylight', 'Mindful Minutes',
  'State of Mind', 'Weight', 'Body Fat', 'Lean Body Mass', 'Height',
  'Blood Pressure', 'Blood Glucose', 'Body Temperature', 'Protein', 'Water',
  'Vitamin D', 'Medications', 'Symptoms', 'Cycle Tracking', 'Headphone Audio',
];

/** The four things you can do once a copy is yours. */
export const OUTCOMES = [
  { key: 'keep', title: 'Keep it', body: 'A file you hold. NDJSON, CSV or JSON.', cat: 'other' },
  { key: 'ask', title: 'Ask it', body: 'A read-only MCP server your assistant reads.', cat: 'mind' },
  { key: 'build', title: 'Build on it', body: 'Your own charts, your own dashboard.', cat: 'nutrition' },
  { key: 'run', title: 'Run it', body: 'Home Assistant, MQTT, any endpoint you own.', cat: 'mobility' },
];
