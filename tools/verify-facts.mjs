/**
 * Checks the documentation's facts against the Hozz app's own source.
 *
 *   npm run verify:facts                       # against the app repo's main
 *   npm run verify:facts -- --ref some-branch  # against another ref
 *   HOZZ_REPO=~/Development/hozz npm run verify:facts   # against a checkout
 *
 * Why a verifier rather than a generator
 * -------------------------------------
 * The two repositories are separate, so anything cross-repo has to be a real
 * mechanism rather than a relative path that works on one machine. The obvious
 * shape is to generate the documentation from the app, but a generator that
 * turns Swift into prose is a thing nobody can maintain, and prose is most of
 * the value here.
 *
 * So the pages stay hand-written and the *lists* are checked: the destination
 * presets, the two format enums, the thirteen MCP tool names and the analysis
 * thresholds are read out of Swift and compared with src/data/docs.ts. Drift is
 * detected mechanically without anything being generated.
 *
 * It reads enum declarations, not documentation prose, because an enum case is
 * a stable thing to parse and a paragraph is not.
 */
import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

import {
  DESTINATIONS,
  DELIVERY_FORMATS,
  EXPORT_FORMATS,
  MCP,
  MCP_TOOLS,
  REQUIREMENTS,
  SOURCE_REF,
  SYNC,
} from '../src/data/docs.ts';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');

const args = process.argv.slice(2);
const refFlag = args.indexOf('--ref');
const ref = refFlag === -1 ? 'main' : args[refFlag + 1];
const localRepo = process.env.HOZZ_REPO;

const FILES = {
  preset: 'Sources/HozzDeliver/DestinationPreset.swift',
  destination: 'Sources/HozzDeliver/Destination.swift',
  exportFormat: 'Sources/HozzHealth/HealthExportFormat.swift',
  mcpServer: 'Sources/HozzMCP/MCPServer.swift',
  statistics: 'Sources/HozzMCP/HealthStatistics.swift',
  credentials: 'Sources/HozzDeliver/DestinationCredentials.swift',
  sharedReceiver: 'Sources/HozzDeliver/SharedReceiverStore.swift',
  probe: 'Sources/HozzDeliver/DeliveryProbe.swift',
  syncEngine: 'Sources/HozzHealth/HealthSyncEngine.swift',
  storeLocation: 'Sources/HozzStore/StoreLocation.swift',
  scheduler: 'App/BackgroundExportScheduler.swift',
  manualExporter: 'Sources/HozzHealth/HealthKitManualExporter.swift',
  stdio: 'Sources/HozzMCP/MCPStdioTransport.swift',
  readme: 'README.md',
  typeRegistry: 'Sources/HozzHealth/HealthKitTypeRegistry.swift',
};

const problems = [];
const notes = [];

function compare(label, expected, actual) {
  const a = [...expected].sort();
  const b = [...actual].sort();
  const missing = b.filter((x) => !a.includes(x));
  const extra = a.filter((x) => !b.includes(x));
  if (missing.length || extra.length) {
    problems.push(
      `${label}\n` +
        (missing.length ? `    in the app but not in the docs: ${missing.join(', ')}\n` : '') +
        (extra.length ? `    in the docs but not in the app: ${extra.join(', ')}\n` : '')
    );
  } else {
    notes.push(`${label} — ${a.length} matching`);
  }
}

function equal(label, expected, actual) {
  if (String(expected) !== String(actual)) {
    problems.push(`${label}\n    docs say ${expected}, the app says ${actual}\n`);
  } else {
    notes.push(`${label} — ${expected}`);
  }
}

/**
 * Asserts that `source` contains `needle`.
 *
 * The list checks above compare a list in the app with a list in the docs. The
 * privacy page is not a list — it is a set of sentences about where a secret
 * lives and what is written down — so what is checked is that the mechanism the
 * sentence names is still the mechanism in the source. If somebody changes the
 * Keychain accessibility, or gives the app a default destination, this fails and
 * the sentence gets revisited rather than quietly becoming untrue.
 */
function contains(label, source, needle, why) {
  if (source.includes(needle)) {
    notes.push(`${label}`);
  } else {
    problems.push(`${label}\n    could not find ${JSON.stringify(needle)} — ${why}\n`);
  }
}

function absent(label, source, needle, why) {
  if (source.includes(needle)) {
    problems.push(`${label}\n    found ${JSON.stringify(needle)}, which ${why}\n`);
  } else {
    notes.push(`${label}`);
  }
}

async function load(name) {
  const path = FILES[name];
  if (localRepo) {
    return readFile(join(localRepo.replace(/^~/, process.env.HOME), path), 'utf8');
  }
  const url = `https://raw.githubusercontent.com/thatcube/hozz/${ref}/${path}`;
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`${url} → HTTP ${response.status}`);
  }
  return response.text();
}

/** Enum case names inside one `enum Name: ... { ... }` declaration. */
function enumCases(source, name) {
  const start = source.indexOf(`enum ${name}`);
  if (start === -1) throw new Error(`enum ${name} not found`);
  const open = source.indexOf('{', start);
  let depth = 0;
  let end = open;
  for (let i = open; i < source.length; i += 1) {
    if (source[i] === '{') depth += 1;
    if (source[i] === '}') {
      depth -= 1;
      if (depth === 0) {
        end = i;
        break;
      }
    }
  }
  const body = source.slice(open, end);
  // `case foo` at the start of a line — a declaration, not a switch arm, which
  // is always indented further inside a `switch`.
  return [...body.matchAll(/^ {4}case ([a-zA-Z]\w*)/gm)].map((m) => m[1]);
}

console.log(
  localRepo
    ? `Checking the docs against ${localRepo}\n`
    : `Checking the docs against thatcube/hozz@${ref}\n`
);

try {
  const [
    preset,
    destination,
    exportFormat,
    mcpServer,
    statistics,
    credentials,
    sharedReceiver,
    probe,
    syncEngine,
    storeLocation,
    scheduler,
    manualExporter,
    stdio,
    readme,
    typeRegistry,
  ] = await Promise.all([
    load('preset'),
    load('destination'),
    load('exportFormat'),
    load('mcpServer'),
    load('statistics'),
    load('credentials'),
    load('sharedReceiver'),
    load('probe'),
    load('syncEngine'),
    load('storeLocation'),
    load('scheduler'),
    load('manualExporter'),
    load('stdio'),
    load('readme'),
    load('typeRegistry'),
  ]);

  // --- Destinations -------------------------------------------------------
  // The Mac is a destination a user can choose but is not a preset: the picker
  // discovers it over Bonjour. It is excluded here rather than expected to be
  // in the enum.
  compare(
    'Destination presets',
    DESTINATIONS.filter((d) => d.preset).map((d) => d.preset),
    enumCases(preset, 'DestinationPreset')
  );

  // --- Delivery formats ---------------------------------------------------
  compare(
    'Delivery formats',
    DELIVERY_FORMATS.map((f) => f.id),
    enumCases(destination, 'DeliveryFormat')
  );

  // --- Export formats -----------------------------------------------------
  compare(
    'Export formats',
    EXPORT_FORMATS.map((f) => f.id),
    enumCases(exportFormat, 'HealthExportFormat')
  );

  // `isLossy` is written as a comparison rather than a switch, so read the
  // names out of the expression.
  const lossyLine = exportFormat.match(/var isLossy: Bool \{\s*([^}]*)\}/);
  if (lossyLine) {
    const lossyInApp = [...lossyLine[1].matchAll(/\.([a-zA-Z]\w*)/g)].map((m) => m[1]);
    compare(
      'Formats marked lossy',
      EXPORT_FORMATS.filter((f) => f.lossy).map((f) => f.id),
      lossyInApp
    );
  } else {
    problems.push('Formats marked lossy\n    could not find isLossy in HealthExportFormat.swift\n');
  }

  // --- MCP ----------------------------------------------------------------
  // The tool names are the strings the dispatcher switches on, which is the
  // one place every tool must appear.
  const dispatch = mcpServer.match(/switch name \{([\s\S]*?)\n {8}\}/);
  const toolNames = dispatch
    ? [...dispatch[1].matchAll(/case "([a-z_]+)":/g)].map((m) => m[1])
    : [...mcpServer.matchAll(/^ {8}case "([a-z_]+)":/gm)].map((m) => m[1]);

  compare(
    'MCP tools',
    MCP_TOOLS.map((t) => t.name),
    [...new Set(toolNames)]
  );

  equal(
    'MCP protocol version',
    MCP.protocolVersion,
    (mcpServer.match(/"(\d{4}-\d{2}-\d{2})"/) ?? [])[1]
  );

  for (const [key, label] of [
    ['minimumTrendDays', 'Minimum days for a trend'],
    ['minimumCorrelationDays', 'Minimum shared days for a correlation'],
    ['minimumBaselineDays', 'Minimum baseline days for anomalies'],
  ]) {
    const match = statistics.match(new RegExp(`${key} = (\\d+)`));
    equal(label, MCP[key], match ? Number(match[1]) : 'not found');
  }

  // The MCP server talks over a pipe to a process the assistant launched. If it
  // ever grew a listener, "it opens no network port" would need retracting.
  contains(
    'MCP server speaks over stdio',
    stdio,
    'FileHandle.standardInput',
    'the docs say the server opens no port and is launched as a subprocess'
  );

  // --- Privacy ------------------------------------------------------------
  // These are sentences rather than lists, so what is checked is the mechanism
  // each sentence names. See `contains` above for why.

  contains(
    'Destination secrets are device-only in the Keychain',
    credentials,
    'kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly',
    'the privacy page names this constant and says a destination secret never leaves the device'
  );

  contains(
    'Synchronised items relax to AfterFirstUnlock',
    credentials,
    'kSecAttrAccessibleAfterFirstUnlock\n',
    'a synchronising item cannot be ThisDeviceOnly, which is what makes the receiver token the exception'
  );

  contains(
    'The receiver token syncs through iCloud Keychain',
    sharedReceiver,
    'synchronizable: true',
    'the privacy page says the Mac receiver token is the deliberate exception and syncs'
  );

  contains(
    'The receiver token is confined to an access group',
    sharedReceiver,
    'accessGroup',
    'the privacy page says the token is restricted to a shared Keychain group as well as synced'
  );

  contains(
    'A connection test carries no Health data',
    probe,
    'hozzConnectionTest',
    'the privacy page quotes this probe payload as proof a test sends nothing real'
  );

  contains(
    'There is no default destination',
    destination,
    'no default destination',
    'the whole privacy argument starts with nothing leaving until a destination exists'
  );

  contains(
    'Health-derived files are excluded from backups',
    storeLocation,
    'isExcludedFromBackup',
    'the privacy page says the store is kept out of device backups'
  );

  contains(
    'The store carries file protection',
    storeLocation,
    'completeUnlessOpen',
    'the privacy page names this protection class'
  );

  // Read-only access to Health is the claim the app can least afford to break.
  contains(
    'Health is asked for read access only',
    manualExporter,
    'toShare: nil',
    'the privacy page says Hozz never requests permission to write to Health'
  );

  absent(
    'Nothing is written back to Health',
    manualExporter,
    'HKHealthStore().save',
    'would mean Hozz writes samples into Health, which the docs say it never does'
  );

  // --- What bounds a sync pass -------------------------------------------
  // The honesty about a first backfill rests on these two numbers.
  const recordLimit = syncEngine.match(/batchRecordLimit = ([\d_]+)/);
  equal(
    'Records per sync pass',
    SYNC.batchRecordLimit,
    recordLimit ? Number(recordLimit[1].replace(/_/g, '')) : 'not found'
  );

  const byteLimit = syncEngine.match(/batchByteLimit = (\d+) \* 1_024 \* 1_024/);
  equal(
    'Megabytes per sync pass',
    SYNC.batchMegabyteLimit,
    byteLimit ? Number(byteLimit[1]) : 'not found'
  );

  const refresh = scheduler.match(/scheduleRefresh\(after delay: TimeInterval = (\d+) \* 60\)/);
  equal(
    'Minutes before the next refresh is requested',
    SYNC.refreshMinutes,
    refresh ? Number(refresh[1]) : 'not found'
  );

  // --- What you need to build it -----------------------------------------
  // Getting started names two tool versions. They are the app README's to
  // change, so they are read from it rather than remembered here.
  const xcode = readme.match(/Xcode (\d+) or newer/);
  equal('Xcode version required', REQUIREMENTS.xcode, xcode ? Number(xcode[1]) : 'not found');

  const xcodegen = readme.match(/XcodeGen\]\([^)]*\) ([\d.]+) or newer/);
  equal('XcodeGen version required', REQUIREMENTS.xcodegen, xcodegen ? xcodegen[1] : 'not found');

  // Two areas on Data coverage are annotated with the OS that introduced them.
  const stateOfMind = typeRegistry.match(/#available\(iOS (\d+)\.\d+, \*\)[\s\S]{0,120}?stateOfMindType/);
  equal(
    'iOS version State of Mind needs',
    REQUIREMENTS.stateOfMindIOS,
    stateOfMind ? Number(stateOfMind[1]) : 'not found'
  );

  contains(
    'iOS version medication doses need',
    typeRegistry,
    `#available(iOS ${REQUIREMENTS.medicationsIOS}.0, *)`,
    'Data coverage says medication doses need this iOS version'
  );
} catch (error) {
  problems.push(`Could not read the app's source\n    ${error.message}\n`);
}

for (const note of notes) console.log(`  ok    ${note}`);

if (problems.length) {
  console.log('');
  for (const problem of problems) console.log(`  DRIFT ${problem}`);
  console.log(
    `${problems.length} difference(s) between the documentation and the app.\n` +
      'Either the app changed and the docs need updating, or the docs are wrong.\n' +
      `src/data/docs.ts was last verified against ${SOURCE_REF.slice(0, 12)}.`
  );
  process.exit(1);
}

console.log(`\nNo drift. ${notes.length} checks passed.`);
