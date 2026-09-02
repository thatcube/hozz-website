/**
 * The documentation's shape.
 *
 * One list, in reading order, so the sidebar, the previous/next links and the
 * index page all come from the same place and cannot disagree about what
 * exists. A page missing from here is a page nobody can navigate to.
 */

import { COUNTS, Spell, spell } from './docs';

export type DocPage = {
  /**
   * Path, always with a trailing slash to match Astro's directory routes.
   *
   * Nearly all of these live under /docs/. Privacy is the exception: it sits at
   * /privacy/ because that is where an App Store listing, a repository and the
   * site's own header already point, and a privacy policy that answers on a
   * redirect is a worse answer than one that does not.
   */
  href: string;
  /** Sidebar label — short. */
  nav: string;
  /**
   * The <h1>. Deliberately separate from `title`: search wants the words
   * someone types, and a reader wants a heading that fits on a phone.
   */
  heading: string;
  /** <title>, before the site suffix. */
  title: string;
  /** <meta name="description">. Search is a large part of why this exists. */
  description: string;
  /** The one line under the page heading. */
  lede: string;
};

export type DocSection = {
  title: string;
  pages: DocPage[];
};

export const DOC_SECTIONS: DocSection[] = [
  {
    title: 'Start here',
    pages: [
      {
        href: '/docs/getting-started/',
        heading: 'Getting started',
        nav: 'Getting started',
        title: 'Getting started with Hozz — export your Apple Health data',
        description:
          'Install Hozz, grant Health access, choose a destination, and run your first Apple Health export. Includes what iOS will and will not let a background app do.',
        lede: 'Four steps to your first export, and an honest account of what happens after it.',
      },
      {
        href: '/privacy/',
        heading: 'Privacy',
        nav: 'Privacy',
        title: 'Hozz privacy — what leaves your device, and when',
        description:
          'Nothing leaves your iPhone until you add a destination and confirm it. Where credentials live, what Hozz never logs, and what it cannot promise once data reaches a destination you chose.',
        lede: 'What leaves the device, when, and to where. This is the whole argument for the app.',
      },
      {
        href: '/docs/open-source/',
        heading: 'Open source',
        nav: 'Open source',
        title: 'Hozz is open source — inspect the privacy claims',
        description:
          'Hozz is licensed under GPL-3.0 with an App Store distribution exception. Read the code behind its data movement, credentials, logging and destinations.',
        lede: 'The source is public so the app’s privacy claims can be checked instead of merely trusted.',
      },
    ],
  },
  {
    title: 'Destinations',
    pages: [
      {
        href: '/docs/destinations/',
        heading: 'Choosing a destination',
        nav: 'Choosing one',
        title: 'Apple Health export destinations — which one to choose',
        description:
          'Hozz can send Apple Health data to a Mac, a folder, Home Assistant, a web endpoint, MQTT or InfluxDB. What each is for, and how to choose.',
        lede: `${Spell(COUNTS.destinations)} places Hozz can send your data, and how to tell which one you want.`,
      },
      {
        href: '/docs/destinations/mac/',
        heading: 'Your Mac',
        nav: 'Your Mac',
        title: 'Send Apple Health data to your Mac — the Hozz receiver',
        description:
          'Set up the Hozz Mac app to receive Apple Health data from your iPhone over the local network. Bonjour discovery, tokens, the folder watcher, and how to tell it is working.',
        lede: 'The Mac app receives what the phone sends, stores it in SQLite, charts it, and can hand it to an assistant.',
      },
      {
        href: '/docs/destinations/folder/',
        heading: 'A folder',
        nav: 'Folder',
        title: 'Export Apple Health data to a folder — iCloud, Dropbox, OneDrive',
        description:
          'Write Apple Health export files to any folder the Files app can reach: iCloud Drive, Dropbox, OneDrive, Google Drive, SMB, or on-device storage. No server and no open ports.',
        lede: 'The recommended destination, because it needs no server, no ports and no VPN.',
      },
      {
        href: '/docs/destinations/home-assistant/',
        heading: 'Home Assistant',
        nav: 'Home Assistant',
        title: 'Apple Health to Home Assistant — webhook and REST setup',
        description:
          'Send Apple Health metrics into Home Assistant as sensors, using a webhook trigger or the REST API. Exact addresses, the token format, the payload, and how to confirm it arrived.',
        lede: 'Metrics JSON to a webhook or the REST API, with the payload written out in full.',
      },
      {
        href: '/docs/destinations/influxdb/',
        heading: 'InfluxDB',
        nav: 'InfluxDB',
        title: 'Apple Health to InfluxDB — line protocol, no translator needed',
        description:
          'Write Apple Health data straight into InfluxDB 1.8, 2.x or 3.x as line protocol, ready to chart in Grafana. Measurement names, tags, fields, timestamp precision and escaping.',
        lede: 'Line protocol written directly, so there is no translator container in the diagram.',
      },
      {
        href: '/docs/destinations/web/',
        heading: 'Your own endpoint',
        nav: 'Web address',
        title: 'Apple Health to your own endpoint — POST, headers and idempotency',
        description:
          'Point Hozz at any endpoint that accepts a POST. Every header Hozz sends, which status codes it retries, and how the idempotency key is derived.',
        lede: `Any endpoint that accepts a POST, in whichever of the ${spell(COUNTS.deliveryFormats)} formats you pick.`,
      },
      {
        href: '/docs/destinations/mqtt/',
        heading: 'MQTT',
        nav: 'MQTT',
        title: 'Apple Health to MQTT — topics, retained messages and QoS',
        description:
          'Publish Apple Health data to an MQTT broker. Topic layout, retained per-metric topics, QoS, and the one thing MQTT cannot do that a folder can.',
        lede: 'Retained per-metric topics for anything already listening to your broker.',
      },
    ],
  },
  {
    title: 'The data',
    pages: [
      {
        href: '/docs/formats/',
        heading: 'Export formats',
        nav: 'Export formats',
        title: 'Apple Health export formats — NDJSON, CSV, JSON, SQLite, Markdown, GPX',
        description:
          'Every format Hozz can export Apple Health data to, what each is good for, and exactly which ones lose detail. CSV, Markdown and GPX are lossy and say so.',
        lede: `${Spell(COUNTS.exportFormats)} formats. ${Spell(COUNTS.lossyExportFormats)} of them lose detail on purpose, and this page says which and what.`,
      },
      {
        href: '/docs/delivery-schema/',
        heading: 'Delivery schema',
        nav: 'Delivery schema',
        title: 'Hozz delivery schema — Apple Health export JSON reference',
        description:
          'Field-by-field reference for every format Hozz delivers: NDJSON, JSON, CSV, Metrics JSON and InfluxDB line protocol, with a worked example payload for each.',
        lede: 'What arrives at your endpoint, field by field, so you can build against Hozz without reading the source.',
      },
      {
        href: '/docs/data-coverage/',
        heading: 'Data coverage',
        nav: 'Data coverage',
        title: 'What Apple Health data Hozz exports — and what it does not',
        description:
          'Which Apple Health types Hozz exports today: quantity and category samples, workouts, routes, ECGs, audiograms, State of Mind, medications and characteristics — and what is not covered.',
        lede: 'What Hozz keeps, what it cannot keep, and the one join it refuses to make up.',
      },
    ],
  },
  {
    title: 'Going further',
    pages: [
      {
        href: '/docs/mcp/',
        heading: 'The MCP server',
        nav: 'The MCP server',
        title: 'Apple Health MCP server — query live Health data from an AI assistant',
        description:
          `Hozz ships a read-only MCP server over a local SQLite database your phone keeps current — not the stale bulk XML export. ${Spell(COUNTS.mcpTools)} tools, and analysis that refuses to overstate.`,
        lede: `${Spell(COUNTS.mcpTools)} read-only tools over a database your phone keeps current, built to refuse the claims it cannot support.`,
      },
      {
        href: '/docs/switching-from-health-auto-export/',
        heading: 'Switching from Health Auto Export',
        nav: 'Switching from HAE',
        title: 'Switching from Health Auto Export to Hozz — field mapping',
        description:
          'Hozz has an opt-in Health Auto Export compatibility mode so existing Home Assistant automations and scripts keep working. What maps to what, and what it does not claim.',
        lede: 'A compatibility mode for automations already keyed to the other app’s field names.',
      },
    ],
  },
  {
    title: 'When something is wrong',
    pages: [
      {
        href: '/docs/background-sync/',
        heading: 'Why your export didn’t run',
        nav: 'Background sync',
        title: 'Why didn’t my Apple Health export run? iOS background limits explained',
        description:
          'iOS decides when a background app runs, most Health types are capped at hourly, and Health cannot be read while the phone is locked. What Hozz can promise and what it cannot.',
        lede: 'Your 8am export did not run at 8am. That is usually iOS, and it is worth understanding why.',
      },
      {
        href: '/docs/troubleshooting/',
        heading: 'Troubleshooting',
        nav: 'Troubleshooting',
        title: 'Hozz troubleshooting — exports, sync and the Mac receiver',
        description:
          'The Mac not appearing, a first backfill that looks stalled, an empty export, and background sync that is not running. Every message Hozz shows, and what it means.',
        lede: 'Every message Hozz can show you, what it actually means, and what to do about it.',
      },
    ],
  },
];

/** Every page, flattened, in reading order. */
export const DOC_PAGES: DocPage[] = DOC_SECTIONS.flatMap((section) => section.pages);

/** The page before and after `href`, for the foot of each page. */
export function neighbours(href: string): { prev?: DocPage; next?: DocPage } {
  const index = DOC_PAGES.findIndex((page) => page.href === href);
  if (index === -1) return {};
  return {
    prev: index > 0 ? DOC_PAGES[index - 1] : undefined,
    next: index < DOC_PAGES.length - 1 ? DOC_PAGES[index + 1] : undefined,
  };
}

/** The entry for `href`, so a page never restates its own title and lede. */
export function page(href: string): DocPage {
  const found = DOC_PAGES.find((entry) => entry.href === href);
  if (!found) throw new Error(`No entry in DOC_SECTIONS for ${href}`);
  return found;
}

/**
 * The section `href` belongs to, for the breadcrumb.
 *
 * Derived rather than passed in by each page: a page that names its own section
 * can be moved in this file and go on claiming the old one, which is a wrong
 * breadcrumb nobody notices until a reader does.
 */
export function sectionOf(href: string): string | undefined {
  return DOC_SECTIONS.find((section) => section.pages.some((entry) => entry.href === href))?.title;
}
