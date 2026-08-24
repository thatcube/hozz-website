import { faceBoxAt } from '../src/data/mark.ts';
for (const size of ['md','lg']) for (const smile of ['compact','wide','curl']) for (const gap of [1,2,3,4]) {
  try { const b = faceBoxAt({cx:16, cy:12, size, smile, gap});
    console.log(size, smile, 'gap'+gap, 'w='+b.w, 'h='+b.h, 'yOff='+(b.y-12)); } catch(e) { console.log(size,smile,gap,'ERR',e.message); }
}
