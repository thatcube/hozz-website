import { faceBoxAt, facePathsAt } from '../src/data/mark.ts';

const disc = { top: 2, bottom: 23 };
for (const smile of ['wide', 'compact']) {
  for (const gap of [1, 2, 3, 4]) {
    const b = faceBoxAt({ cx: 16, cy: 13, size: 'md', smile, gap });
    const off = b.y - 13;
    console.log(`md ${smile} gap${gap}: h=${b.h} topOffset=${off} w=${b.w} x=${b.x}..${b.right} y=${b.y}..${b.bottom}`);
  }
}
