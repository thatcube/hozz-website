import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path';
const root = path.resolve('dist');
const types = {'.html':'text/html','.css':'text/css','.js':'text/javascript','.svg':'image/svg+xml','.png':'image/png','.woff2':'font/woff2','.xml':'application/xml','.json':'application/json'};
http.createServer((req,res)=>{
  let f = path.join(root, decodeURIComponent(req.url.split('?')[0]));
  if (fs.existsSync(f) && fs.statSync(f).isDirectory()) f = path.join(f,'index.html');
  if (!fs.existsSync(f)) { res.writeHead(404); return res.end('nope'); }
  res.writeHead(200, {'content-type': types[path.extname(f)] || 'application/octet-stream'});
  fs.createReadStream(f).pipe(res);
}).listen(4861, ()=>console.log('4861'));
