/**
 * Facts about Hozz that live in the app's source, mirrored here for the docs.
 *
 * Everything in this file is checkable against Swift in the Hozz repository,
 * and `npm run verify:facts` does exactly that — it reads the enums out of the
 * app's source and fails if this file disagrees. See tools/verify-facts.mjs.
 *
 * Prose belongs in the pages. This file holds only the things that are a list
 * in the app and would quietly go stale here: destination presets, formats,
 * MCP tool names, and the analysis thresholds.
 */

/** The app-repo commit these facts were last verified against. */
export const SOURCE_REF = 'b5b430a56494e0ea22898f0e8c6bf0833c6e6f0a';

export const APP_REPO = 'https://github.com/thatcube/hozz';

/* -------------------------------------------------------------------------
   Destinations

   `DestinationPreset` has five cases. The Mac is a sixth thing a user can
   pick, but it is not a preset: the picker discovers computers over Bonjour
   and writes a REST destination for you, so it is listed here with
   `preset: null` rather than pretended into the enum.
   Source: Sources/HozzDeliver/DestinationPreset.swift, App/DestinationPickerView.swift
   ------------------------------------------------------------------------- */

export type Destination = {
  slug: string;
  /** The `DestinationPreset` case, or null for the discovered-Mac flow. */
  preset: string | null;
  /** `DestinationPreset.displayName`, or the picker's own wording. */
  name: string;
  /** `DestinationPreset.summary`, verbatim where one exists. */
  summary: string;
  /** The `DeliveryFormat` this destination starts with. */
  defaultFormat: string;
  /** `DestinationKind` underneath. */
  kind: 'folder' | 'restAPI' | 'mqtt';
  /** True for the one Hozz recommends first. */
  recommended: boolean;
  /** Who this is actually for, in our words rather than the app's. */
  who: string;
};

export const DESTINATIONS: Destination[] = [
  {
    slug: 'mac',
    preset: null,
    name: 'Your Mac',
    summary:
      'Sends batches to the Hozz Mac app over your local network. Hozz finds the computer and sets up the address and token for you.',
    defaultFormat: 'ndjson',
    kind: 'restAPI',
    recommended: false,
    who: 'You want the data charted, searchable, and available to an AI assistant, without running anything yourself.',
  },
  {
    slug: 'folder',
    preset: 'folder',
    name: 'Folder',
    summary:
      'Syncs to your computer through iCloud, Dropbox, or any folder. No server needed.',
    defaultFormat: 'ndjson',
    kind: 'folder',
    recommended: true,
    who: 'You want files you can open, back up, and keep — with nothing to run and no ports to open.',
  },
  {
    slug: 'home-assistant',
    preset: 'homeAssistant',
    name: 'Home Assistant',
    summary: 'Sends metrics straight into Home Assistant as sensors.',
    defaultFormat: 'metrics',
    kind: 'restAPI',
    recommended: false,
    who: 'You already run Home Assistant and want Health data to trigger automations.',
  },
  {
    slug: 'influxdb',
    preset: 'influxDB',
    name: 'InfluxDB',
    summary:
      'Writes line protocol straight into InfluxDB, ready to chart in Grafana.',
    defaultFormat: 'influx',
    kind: 'restAPI',
    recommended: false,
    who: 'You want Grafana dashboards, and you do not want to run a translator container to get them.',
  },
  {
    slug: 'web',
    preset: 'restAPI',
    name: 'Web address',
    summary: 'Posts to any endpoint you run.',
    defaultFormat: 'ndjson',
    kind: 'restAPI',
    recommended: false,
    who: 'You are writing the receiving end yourself, or pointing Hozz at something that already accepts a POST.',
  },
  {
    slug: 'mqtt',
    preset: 'mqtt',
    name: 'MQTT',
    summary: 'Publishes to an MQTT broker on your network.',
    defaultFormat: 'metrics',
    kind: 'mqtt',
    recommended: false,
    who: 'You have a broker at the centre of your home setup and want Health data on it like everything else.',
  },
];

/* -------------------------------------------------------------------------
   Delivery formats — what an automatic destination receives.
   Source: Sources/HozzDeliver/Destination.swift, enum DeliveryFormat
   ------------------------------------------------------------------------- */

export type DeliveryFormatFact = {
  id: string;
  name: string;
  contentType: string;
  fileExtension: string;
  lossless: boolean;
  /** What it is for, and what it drops when it drops something. */
  note: string;
};

export const DELIVERY_FORMATS: DeliveryFormatFact[] = [
  {
    id: 'ndjson',
    name: 'NDJSON',
    contentType: 'application/x-ndjson',
    fileExtension: 'ndjson',
    lossless: true,
    note: 'One record per line. The default, and the only shape that streams at any size.',
  },
  {
    id: 'json',
    name: 'JSON',
    contentType: 'application/json',
    fileExtension: 'json',
    lossless: true,
    note: 'The same records as one array, for tools that want a single JSON value.',
  },
  {
    id: 'csv',
    name: 'CSV',
    contentType: 'text/csv',
    fileExtension: 'csv',
    lossless: false,
    note: 'One flat table. Metadata, device, workout detail and route points do not fit a grid and are not included.',
  },
  {
    id: 'metrics',
    name: 'Metrics JSON',
    contentType: 'application/json',
    fileExtension: 'json',
    lossless: false,
    note: 'Grouped by metric rather than by sample. What Home Assistant, MQTT subscribers and dashboards want. Drops metadata, device and workout detail.',
  },
  {
    id: 'influx',
    name: 'InfluxDB line protocol',
    contentType: 'text/plain; charset=utf-8',
    fileExtension: 'lp',
    lossless: false,
    note: 'Ingested directly by InfluxDB and Telegraf. Drops metadata, workout detail, and device detail beyond its name.',
  },
];

/* -------------------------------------------------------------------------
   Export formats — what a manual export produces.
   Source: Sources/HozzHealth/HealthExportFormat.swift
   ------------------------------------------------------------------------- */

export type ExportFormatFact = {
  id: string;
  name: string;
  /** `HealthExportFormat.fileExtension`. */
  fileExtension: string;
  /** `HealthExportFormat.isLossy`. */
  lossy: boolean;
  /** `HealthExportFormat.coversRoutesOnly`. */
  routesOnly: boolean;
  /** Whether the format picker offers it. `raw` is engine-only. */
  inPicker: boolean;
  good: string;
  keeps: string;
};

export const EXPORT_FORMATS: ExportFormatFact[] = [
  {
    id: 'ndjson',
    name: 'NDJSON',
    fileExtension: 'zip',
    lossy: false,
    routesOnly: false,
    inPicker: true,
    good: 'Keeping everything, and feeding another tool.',
    keeps: 'Every field Hozz encodes. The default, and the format the export is built from.',
  },
  {
    id: 'sqlite',
    name: 'SQLite',
    fileExtension: 'sqlite',
    lossy: false,
    routesOnly: false,
    inPicker: true,
    good: 'Asking questions without an import step.',
    keeps: 'Everything. Typed columns for querying, plus the original record kept verbatim in a raw column.',
  },
  {
    id: 'json',
    name: 'JSON',
    fileExtension: 'zip',
    lossy: false,
    routesOnly: false,
    inPicker: true,
    good: 'Smaller exports, and tools that want one JSON value.',
    keeps: 'Every field Hozz encodes, as a single array.',
  },
  {
    id: 'csv',
    name: 'CSV',
    fileExtension: 'zip',
    lossy: true,
    routesOnly: false,
    inPicker: true,
    good: 'Opening in Excel, Numbers or Sheets.',
    keeps: 'Values, dates, units and source. Metadata and nested workout detail are dropped.',
  },
  {
    id: 'markdown',
    name: 'Markdown',
    fileExtension: 'zip',
    lossy: true,
    routesOnly: false,
    inPicker: true,
    good: 'Obsidian, and daily journals.',
    keeps: "A day's totals and extremes with YAML front matter. The records behind them are dropped.",
  },
  {
    id: 'gpx',
    name: 'GPX',
    fileExtension: 'zip',
    lossy: true,
    routesOnly: true,
    inPicker: true,
    good: 'Maps, and self-hosted fitness tools.',
    keeps: 'One GPX 1.1 track per workout that has GPS, and nothing else at all.',
  },
  {
    id: 'raw',
    name: 'Raw NDJSON',
    fileExtension: 'ndjson',
    lossy: false,
    routesOnly: false,
    inPicker: false,
    good: 'Piping straight into something else.',
    keeps: 'The same as NDJSON, uncompressed. Supported by the export engine rather than offered in the picker.',
  },
];

/* -------------------------------------------------------------------------
   Sync cadences.
   Source: Sources/HozzDeliver/Destination.swift, enum SyncCadence
   ------------------------------------------------------------------------- */

export const CADENCES = [
  {
    id: 'whenDataArrives',
    name: 'When new data arrives',
    floor: 'at most one delivery every 5 minutes',
  },
  { id: 'hourly', name: 'About every hour', floor: 'at most one delivery every 55 minutes' },
  { id: 'daily', name: 'About once a day', floor: 'at most one delivery every 23 hours' },
  { id: 'manual', name: 'Only when I ask', floor: 'never on its own' },
] as const;

/* -------------------------------------------------------------------------
   Delivery states — what the dashboard can say about a destination.
   Source: Sources/HozzDeliver/Destination.swift, enum DeliveryState
   ------------------------------------------------------------------------- */

export const DELIVERY_STATES = [
  { id: 'idle', healthy: true, meaning: 'Nothing has been attempted yet.' },
  {
    id: 'waitingForSystem',
    healthy: true,
    meaning: 'There is data to send and Hozz is waiting for iOS to run it.',
  },
  { id: 'delivering', healthy: true, meaning: 'A delivery is in flight.' },
  {
    id: 'delivered',
    healthy: true,
    meaning: 'Everything staged has been accepted by the destination.',
  },
  {
    id: 'waitingForUnlock',
    healthy: true,
    meaning: 'The device was locked, so Health could not be read. Resolves itself.',
  },
  {
    id: 'retrying',
    healthy: false,
    meaning: 'The destination rejected the data or could not be reached. Will retry.',
  },
  {
    id: 'needsAttention',
    healthy: false,
    meaning: 'Something you have to fix, such as a folder that was moved.',
  },
] as const;

/* -------------------------------------------------------------------------
   The MCP server.
   Source: Sources/HozzMCP/MCPServer.swift, Sources/HozzMCP/HealthStatistics.swift
   ------------------------------------------------------------------------- */

export const MCP = {
  protocolVersion: '2024-11-05',
  serverName: 'hozz',
  serverVersion: '1.0.0',
  binary: '/Applications/Hozz.app/Contents/MacOS/hozz-mcp',
  dataDir:
    '/Users/YOUR_USERNAME/Library/Containers/com.thatcube.Hozz.mac/Data/Library/Application Support/Hozz/Received',
  /** HealthStatistics.minimumTrendDays */
  minimumTrendDays: 14,
  /** HealthStatistics.minimumCorrelationDays */
  minimumCorrelationDays: 28,
  /** HealthStatistics.minimumBaselineDays */
  minimumBaselineDays: 14,
} as const;

export type McpTool = {
  name: string;
  group: 'Orientation' | 'Retrieval' | 'Analysis';
  answers: string;
};

export const MCP_TOOLS: McpTool[] = [
  {
    name: 'summarise_health_data',
    group: 'Orientation',
    answers:
      'What is here at all: record count, types, date range, the largest types, and the person’s own characteristics.',
  },
  {
    name: 'list_health_types',
    group: 'Orientation',
    answers: 'Which types have arrived, with counts and date ranges.',
  },
  {
    name: 'aggregate_health_data',
    group: 'Retrieval',
    answers:
      'One type bucketed by hour, day, week or month, with sum, average, minimum, maximum and count per bucket.',
  },
  {
    name: 'list_health_samples',
    group: 'Retrieval',
    answers: 'Individual samples, when the readings themselves matter.',
  },
  {
    name: 'list_workouts',
    group: 'Retrieval',
    answers:
      'Workouts with what Health computed about each: heart rate, energy, distance, and each leg of a multi-sport workout separately.',
  },
  {
    name: 'list_electrocardiograms',
    group: 'Retrieval',
    answers:
      'Every ECG reading, with what the Watch classified it as, average heart rate, symptom status, and whether the full waveform has arrived.',
  },
  {
    name: 'get_electrocardiogram_voltages',
    group: 'Retrieval',
    answers: 'One reading’s waveform as time/volt pairs.',
  },
  {
    name: 'list_audiograms',
    group: 'Retrieval',
    answers: 'Hearing tests, with the threshold at each frequency for each ear.',
  },
  {
    name: 'list_mood_entries',
    group: 'Retrieval',
    answers: 'State of Mind entries with their classification, kind, labels and associations.',
  },
  {
    name: 'summarise_medication_adherence',
    group: 'Retrieval',
    answers: 'Dose events per medicine, counted by status.',
  },
  {
    name: 'analyse_health_trend',
    group: 'Analysis',
    answers: 'Is this drifting up or down, and can that be said at all?',
  },
  {
    name: 'compare_health_types',
    group: 'Analysis',
    answers: 'Do these two move together day to day?',
  },
  {
    name: 'find_health_anomalies',
    group: 'Analysis',
    answers: 'Did anything genuinely unusual happen?',
  },
];

/* -------------------------------------------------------------------------
   Error and status strings the app actually shows.

   Copied verbatim so that searching the words on your screen finds the page
   that explains them. Source files are named on each entry.
   ------------------------------------------------------------------------- */

export type AppMessage = {
  text: string;
  source: string;
  means: string;
  fix: string;
};

export const APP_MESSAGES: AppMessage[] = [
  {
    text: 'Health data is locked. Unlock this iPhone and Hozz will continue.',
    source: 'Sources/HozzHealth/HealthKitFailure.swift',
    means:
      'iOS woke Hozz while the phone was locked. Health is encrypted until first unlock, so there was nothing to read.',
    fix: 'Nothing. Unlock the phone and the next pass continues from where it stopped. No records are skipped.',
  },
  {
    text: 'Health returned no data. Apple does not let Hozz tell a denied type from an empty one.',
    source: 'Sources/HozzHealth/HealthKitFailure.swift',
    means:
      'Either you did not grant this type, or you genuinely have none of it. HealthKit answers both cases identically and deliberately.',
    fix: 'Check the type in Settings → Health → Data Access & Devices → Hozz. If it is on, you have no data of that type.',
  },
  {
    text: 'Health data is unavailable or restricted on this device.',
    source: 'Sources/HozzHealth/HealthKitFailure.swift',
    means: 'HealthKit itself is off — Screen Time restrictions, or a device without Health.',
    fix: 'Check Screen Time content restrictions.',
  },
  {
    text: 'Hozz could not reach that folder. It may have been moved, renamed, or signed out.',
    source: 'Sources/HozzDeliver/Destination.swift',
    means:
      'The security-scoped bookmark no longer resolves. Usually a renamed folder, or a cloud drive that signed out.',
    fix: 'Edit the destination and pick the folder again.',
  },
  {
    text: 'Hozz no longer has permission to write to that folder.',
    source: 'Sources/HozzDeliver/Destination.swift',
    means: 'The folder resolves but iOS refused the write.',
    fix: 'Edit the destination and pick the folder again to re-grant access.',
  },
  {
    text: 'The destination refused the data (HTTP …).',
    source: 'Sources/HozzDeliver/Destination.swift',
    means:
      'Your endpoint answered with something other than 2xx. 408, 429 and 5xx are treated as “try again”; anything else stops and waits for you.',
    fix: 'Check the endpoint’s own logs. Hozz deliberately does not log the response body, because a server rejecting a batch often echoes the record back.',
  },
  {
    text: 'Hozz could not reach the destination: …',
    source: 'Sources/HozzDeliver/Destination.swift',
    means: 'A transport failure — wrong host, no route, TLS refused, or nothing listening.',
    fix: 'Confirm the phone can reach the address on this network. Use Send a test, which reports what came back.',
  },
  {
    text: 'This destination is not finished being set up.',
    source: 'Sources/HozzDeliver/Destination.swift',
    means: 'A required field, such as the address or the folder, is still empty.',
    fix: 'Open the destination and complete it.',
  },
  {
    text: 'The delivery was stopped before it finished.',
    source: 'Sources/HozzDeliver/Destination.swift',
    means: 'iOS ended the background window, or the app was closed mid-delivery.',
    fix: 'Nothing. The cursor did not advance, so the next pass resends the same records.',
  },
  {
    text: 'Offline — open Hozz on it',
    source: 'App/DestinationPickerView.swift',
    means:
      'A Mac you have used before did not answer a probe just now. Hozz will not offer a computer that cannot accept data.',
    fix: 'Open Hozz on that Mac and make sure both devices are on the same network.',
  },
  {
    text: 'Hozz needs permission to see this network',
    source: 'App/DestinationPickerView.swift',
    means: 'Local Network access was declined, so Bonjour cannot look for your Mac.',
    fix: 'Settings → Hozz → Local Network. You can also add the Mac by web address instead.',
  },
];

/**
 * What bounds a single background sync pass.
 *
 * These are the numbers behind "a first backfill takes days or weeks": a pass
 * is capped, and iOS decides how many passes a day you get. They live here so
 * the sentence on the background sync page and the check in
 * tools/verify-facts.mjs read the same value.
 */
export const SYNC = {
  /** HealthSyncEngine.batchRecordLimit */
  batchRecordLimit: 5_000,
  /** HealthSyncEngine.batchByteLimit, in megabytes. */
  batchMegabyteLimit: 4,
  /** BackgroundExportScheduler.scheduleRefresh's default delay, in minutes. */
  refreshMinutes: 15,
};

/**
 * A small number as an English word.
 *
 * The pages say "Seven formats" rather than "7 formats" because that is the
 * voice, but a hand-typed "Seven" beside a list that is checked mechanically is
 * the same trap as a hand-typed test count: the list gains an entry, the
 * verifier is satisfied, and the sentence is quietly wrong. Counting through
 * here means the word and the list cannot disagree.
 *
 * Above twelve it gives up and returns digits, which is where spelling numbers
 * out stops reading well anyway.
 */
const WORDS = [
  'zero',
  'one',
  'two',
  'three',
  'four',
  'five',
  'six',
  'seven',
  'eight',
  'nine',
  'ten',
  'eleven',
  'twelve',
  'thirteen',
];

export function spell(n: number): string {
  return WORDS[n] ?? String(n);
}

/** The same word with its first letter capitalised, for the start of a sentence. */
export function Spell(n: number): string {
  const word = spell(n);
  return word[0].toUpperCase() + word.slice(1);
}

/** Counts the pages quote, each derived from the list it describes. */
export const COUNTS = {
  destinations: DESTINATIONS.length,
  deliveryFormats: DELIVERY_FORMATS.length,
  exportFormats: EXPORT_FORMATS.length,
  lossyExportFormats: EXPORT_FORMATS.filter((f) => f.lossy).length,
  mcpTools: MCP_TOOLS.length,
  deliveryStates: DELIVERY_STATES.length,
  presets: DESTINATIONS.filter((d) => d.preset).length,
};

/**
 * What you need on the machine to build the app, and the platform versions the
 * pages name.
 *
 * The two toolchain versions are quoted from the app repository's README, and
 * the platform versions from the availability checks in its source, so
 * tools/verify-facts.mjs can hold both to it rather than trusting this file.
 */
export const REQUIREMENTS = {
  /** README: "Xcode N or newer". */
  xcode: 27,
  /** README: "XcodeGen N.NN or newer". */
  xcodegen: '2.46',
  /** #available(iOS N, *) around State of Mind. */
  stateOfMindIOS: 18,
  /** #available(iOS N, *) around medication doses. */
  medicationsIOS: 26,
};
