
import { chromium } from '/Users/brandon/Development/amazon-subscription-canceller/node_modules/playwright/index.mjs';
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 620, height: 780 }, deviceScaleFactor: 3 });
await p.goto('file:///Users/brandon/Development/copilot-worktrees/hozz-website/thatcube-curly-dollop/.scratch-t11/p.html');
await p.screenshot({ path: '/Users/brandon/Development/copilot-worktrees/hozz-website/thatcube-curly-dollop/.scratch-t11/p.png', fullPage: true });
await b.close();
