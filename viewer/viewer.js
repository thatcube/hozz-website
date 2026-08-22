import { readExport, summarise, friendlyName, aggregationFor } from './parse.js';

const drop = document.getElementById('drop');
const input = document.getElementById('file');
const status = document.getElementById('status');
const intro = document.getElementById('intro');
const results = document.getElementById('results');
const charts = document.getElementById('charts');
const search = document.getElementById('search');

let summary = null;

function setStatus(text, isError = false) {
  status.hidden = !text;
  status.textContent = text ?? '';
  status.classList.toggle('error', isError);
}

drop.addEventListener('click', () => input.click());
drop.addEventListener('keydown', (event) => {
  if (event.key === 'Enter' || event.key === ' ') {
    event.preventDefault();
    input.click();
  }
});
input.addEventListener('change', () => {
  if (input.files?.[0]) load(input.files[0]);
});

for (const name of ['dragenter', 'dragover']) {
  drop.addEventListener(name, (event) => {
    event.preventDefault();
    drop.classList.add('over');
  });
}
for (const name of ['dragleave', 'drop']) {
  drop.addEventListener(name, (event) => {
    event.preventDefault();
    drop.classList.remove('over');
  });
}
drop.addEventListener('drop', (event) => {
  const file = event.dataTransfer?.files?.[0];
  if (file) load(file);
});

document.getElementById('reset').addEventListener('click', () => {
  results.hidden = true;
  intro.hidden = false;
  input.value = '';
  setStatus(null);
});

search.addEventListener('input', () => render(search.value.trim().toLowerCase()));

async function load(file) {
  setStatus('Reading the file…');
  try {
    // Yield once so the status paints before the main thread is busy.
    await new Promise((resolve) => setTimeout(resolve, 16));
    const text = await readExport(file, setStatus);
    setStatus('Sorting the records…');
    await new Promise((resolve) => setTimeout(resolve, 16));

    summary = summarise(text, setStatus);
    if (summary.records === 0) {
      setStatus('No health records were found in that file.', true);
      return;
    }

    document.getElementById('stat-records').textContent =
      summary.records.toLocaleString();
    document.getElementById('stat-types').textContent =
      summary.types.length.toLocaleString();
    document.getElementById('stat-deletions').textContent =
      summary.deletions.toLocaleString();

    const first = summary.types.reduce(
      (a, t) => (t.first < a ? t.first : a), '9999');
    const last = summary.types.reduce(
      (a, t) => (t.last > a ? t.last : a), '0000');
    document.getElementById('stat-span').textContent =
      first === '9999' ? '—' : `${first.slice(0, 4)}–${last.slice(0, 4)}`;

    intro.hidden = true;
    results.hidden = false;
    setStatus(null);
    render('');
  } catch (error) {
    setStatus(error.message ?? 'That file could not be read.', true);
  }
}

function render(query) {
  charts.textContent = '';
  const matches = summary.types.filter((type) =>
    !query || friendlyName(type.name).toLowerCase().includes(query)
  );

  if (matches.length === 0) {
    const empty = document.createElement('p');
    empty.className = 'empty';
    empty.textContent = 'Nothing matches that search.';
    charts.append(empty);
    return;
  }

  // Charting every one of 190 types at once would take seconds and help
  // nobody; the list is sorted by volume, so the useful ones are first.
  for (const type of matches.slice(0, 60)) {
    charts.append(card(type));
  }
}

function card(type) {
  const element = document.createElement('article');
  element.className = 'card';

  const title = document.createElement('h3');
  title.textContent = friendlyName(type.name);
  element.append(title);

  const days = [...type.days.entries()].sort((a, b) => (a[0] < b[0] ? -1 : 1));
  const mode = aggregationFor(type.name);
  const points = days.map(([day, stats]) => ({
    day,
    value: mode === 'sum' ? stats.sum : stats.sum / stats.n,
  }));

  const meta = document.createElement('p');
  meta.className = 'meta';
  if (points.length === 0) {
    meta.textContent = `${type.count.toLocaleString()} records · no numeric value`;
    element.append(meta);
    return element;
  }

  const latest = points.at(-1);
  const unit = type.unit ? ` ${type.unit}` : '';
  const label = mode === 'sum' ? 'latest day' : 'latest average';
  meta.textContent =
    `${format(latest.value)}${unit} ${label} · ${type.count.toLocaleString()} records`;
  element.append(meta);

  element.append(sparkline(points));

  const axis = document.createElement('div');
  axis.className = 'axis';
  const from = document.createElement('span');
  from.textContent = points[0].day;
  const to = document.createElement('span');
  to.textContent = latest.day;
  axis.append(from, to);
  element.append(axis);

  return element;
}

/** A dependency-free sparkline. Inline SVG keeps this page free of libraries. */
function sparkline(points) {
  const width = 300;
  const height = 90;
  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  svg.setAttribute('viewBox', `0 0 ${width} ${height}`);
  svg.setAttribute('preserveAspectRatio', 'none');
  svg.setAttribute('role', 'img');

  // More days than pixels would draw the same column repeatedly, so the series
  // is reduced to at most one point per horizontal pixel.
  const stride = Math.max(1, Math.ceil(points.length / width));
  const sampled = points.filter((_, index) => index % stride === 0);
  if (sampled.at(-1) !== points.at(-1)) sampled.push(points.at(-1));

  const values = sampled.map((p) => p.value);
  const min = Math.min(...values);
  const max = Math.max(...values);
  const span = max - min || 1;
  const step = sampled.length > 1 ? width / (sampled.length - 1) : 0;

  const coords = sampled.map((point, index) => {
    const x = index * step;
    const y = height - ((point.value - min) / span) * (height - 8) - 4;
    return `${x.toFixed(1)},${y.toFixed(1)}`;
  });

  const area = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
  area.setAttribute('class', 'spark-fill');
  area.setAttribute('points', `0,${height} ${coords.join(' ')} ${width},${height}`);

  const line = document.createElementNS('http://www.w3.org/2000/svg', 'polyline');
  line.setAttribute('class', 'spark-line');
  line.setAttribute('points', coords.join(' '));

  svg.append(area, line);
  svg.setAttribute(
    'aria-label',
    `${sampled.length} points, from ${format(min)} to ${format(max)}`
  );
  return svg;
}

function format(value) {
  if (!Number.isFinite(value)) return '—';
  if (Math.abs(value) >= 1000) return Math.round(value).toLocaleString();
  if (Math.abs(value) >= 10) return value.toFixed(0);
  return value.toFixed(1);
}
