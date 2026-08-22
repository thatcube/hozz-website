/* Reads a Hozz export entirely inside the browser.
 *
 * Nothing is uploaded. There is no server to upload to — this page is static
 * files on GitHub Pages, and the parsing below runs on your own machine. That
 * is not a promise you have to take on faith: open the network tab and watch it
 * stay empty, or read this file.
 */

/** Locates the single NDJSON entry inside a Hozz Zip64 archive. */
function findZipEntries(bytes) {
  const view = new DataView(bytes.buffer, bytes.byteOffset, bytes.byteLength);
  const u16 = (o) => view.getUint16(o, true);
  const u32 = (o) => view.getUint32(o, true);
  const u64 = (o) => Number(view.getBigUint64(o, true));

  // Walk backwards for the Zip64 locator; Hozz always writes Zip64 because a
  // real export exceeds the 4 GiB the classic header can express.
  let locator = -1;
  for (let i = bytes.length - 4; i >= 0; i--) {
    if (u32(i) === 0x07064b50) { locator = i; break; }
  }
  if (locator < 0) throw new Error('This does not look like a Hozz export.');

  const zip64End = u64(locator + 8);
  if (u32(zip64End) !== 0x06064b50) throw new Error('The archive index is damaged.');

  const count = u64(zip64End + 32);
  let cursor = u64(zip64End + 48);
  const entries = [];

  for (let n = 0; n < count; n++) {
    if (u32(cursor) !== 0x02014b50) break;
    const nameLength = u16(cursor + 28);
    const extraLength = u16(cursor + 30);
    const commentLength = u16(cursor + 32);
    const name = new TextDecoder().decode(
      bytes.subarray(cursor + 46, cursor + 46 + nameLength)
    );

    const extra = cursor + 46 + nameLength;
    if (u16(extra) !== 0x0001) throw new Error('Unexpected archive layout.');
    const uncompressed = u64(extra + 4);
    const compressed = u64(extra + 12);
    const header = u64(extra + 20);

    // Re-derive the payload position from the local header so a wrong offset
    // in either record is caught rather than silently misread.
    if (u32(header) !== 0x04034b50) throw new Error('An entry is damaged.');
    const start = header + 30 + u16(header + 26) + u16(header + 28);

    entries.push({ name, start, compressed, uncompressed });
    cursor = extra + extraLength + commentLength;
  }
  return entries;
}

/** Inflates a raw deflate stream using the browser's own decompressor. */
async function inflateRaw(slice) {
  const stream = new Blob([slice])
    .stream()
    .pipeThrough(new DecompressionStream('deflate-raw'));
  return new Uint8Array(await new Response(stream).arrayBuffer());
}

/** Turns a file into NDJSON text, whichever shape it arrived in. */
export async function readExport(file, onProgress) {
  const bytes = new Uint8Array(await file.arrayBuffer());

  // A bare .ndjson or .json file needs no unpacking.
  if (!file.name.endsWith('.zip')) {
    return new TextDecoder().decode(bytes);
  }

  onProgress?.('Opening the archive…');
  const entries = findZipEntries(bytes);
  const entry =
    entries.find((e) => e.name.endsWith('.ndjson')) ??
    entries.find((e) => e.name.endsWith('.json'));
  if (!entry) {
    throw new Error(
      'This archive has no NDJSON inside. A CSV export cannot be charted here.'
    );
  }

  onProgress?.('Decompressing…');
  const slice = bytes.subarray(entry.start, entry.start + entry.compressed);
  return new TextDecoder().decode(await inflateRaw(slice));
}

/** Folds records into per-type daily totals and averages. */
export function summarise(text, onProgress) {
  const types = new Map();
  let records = 0;
  let deletions = 0;
  let lineStart = 0;

  const handle = (line) => {
    if (!line) return;
    let record;
    try { record = JSON.parse(line); } catch { return; }

    const kind = record.kind;
    if (kind === 'deletion') { deletions++; return; }
    if (!record.type || !record.startDate) return;
    if (kind !== 'quantity' && kind !== 'category' && kind !== 'workout') return;

    records++;
    const day = record.startDate.slice(0, 10);
    const value = record.quantity?.value ?? record.value ?? null;

    let type = types.get(record.type);
    if (!type) {
      type = {
        name: record.type,
        unit: record.quantity?.unit ?? '',
        kind,
        days: new Map(),
        count: 0,
        first: day,
        last: day,
      };
      types.set(record.type, type);
    }
    type.count++;
    if (day < type.first) type.first = day;
    if (day > type.last) type.last = day;

    if (value !== null && Number.isFinite(value)) {
      const existing = type.days.get(day) ?? { sum: 0, n: 0, min: value, max: value };
      existing.sum += value;
      existing.n++;
      existing.min = Math.min(existing.min, value);
      existing.max = Math.max(existing.max, value);
      type.days.set(day, existing);
    }
  };

  for (let i = 0; i < text.length; i++) {
    if (text.charCodeAt(i) === 10) {
      handle(text.slice(lineStart, i));
      lineStart = i + 1;
      if (records % 200000 === 0 && records > 0) {
        onProgress?.(`Read ${records.toLocaleString()} records…`);
      }
    }
  }
  handle(text.slice(lineStart));

  return { types: [...types.values()].sort((a, b) => b.count - a.count), records, deletions };
}

/** Human-readable name for a HealthKit identifier. */
export function friendlyName(identifier) {
  const stripped = identifier
    .replace(/^HKQuantityTypeIdentifier/, '')
    .replace(/^HKCategoryTypeIdentifier/, '')
    .replace(/^HKWorkoutTypeIdentifier$/, 'Workout');
  return stripped
    .replace(/([a-z0-9])([A-Z])/g, '$1 $2')
    .replace(/([A-Z]+)([A-Z][a-z])/g, '$1 $2') || identifier;
}

/** Whether a daily figure should be a total or an average. */
export function aggregationFor(identifier) {
  const cumulative = [
    'StepCount', 'DistanceWalkingRunning', 'DistanceCycling', 'DistanceSwimming',
    'ActiveEnergyBurned', 'BasalEnergyBurned', 'FlightsClimbed', 'AppleExerciseTime',
    'AppleStandTime', 'DietaryEnergyConsumed', 'DietaryWater', 'DietaryProtein',
    'DietaryCarbohydrates', 'DietaryFatTotal', 'AppleMoveTime', 'SwimmingStrokeCount',
  ];
  return cumulative.some((name) => identifier.includes(name)) ? 'sum' : 'avg';
}
