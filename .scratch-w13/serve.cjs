const http=require('http'),fs=require('fs'),path=require('path');
const ROOT=path.resolve(__dirname,'..','dist');
const T={'.html':'text/html','.css':'text/css','.js':'text/javascript','.woff2':'font/woff2','.svg':'image/svg+xml','.png':'image/png','.xml':'application/xml','.json':'application/json','.ico':'image/x-icon','.webmanifest':'application/manifest+json'};
http.createServer((q,s)=>{let u=decodeURIComponent(q.url.split('?')[0]);let f=path.join(ROOT,u);
 try{if(fs.statSync(f).isDirectory())f=path.join(f,'index.html');}catch(e){if(!path.extname(f))f+='.html';}
 fs.readFile(f,(e,d)=>{if(e){s.writeHead(404);return s.end('nf');}s.writeHead(200,{'Content-Type':T[path.extname(f)]||'application/octet-stream','Cache-Control':'no-store'});s.end(d);});
}).listen(5177,'127.0.0.1',()=>console.log('up'));
