const {JSDOM,VirtualConsole}=require("jsdom"),fs=require("fs"),path=require("path");
// the pages live at the repository root; this script sits in audit/
const ROOT=require("path").resolve(__dirname,"..");
// build templates and the patch history are not deliverable pages
const SKIP=/(^|[\\/])(build|patches|audit|node_modules|host-configs|\.github)([\\/]|$)/;
function walk(d,o=[]){for(const f of fs.readdirSync(d)){const p=path.join(d,f);
  if(SKIP.test(p))continue; fs.statSync(p).isDirectory()?walk(p,o):(f.endsWith(".html")&&o.push(p));}return o;}
const bad=[];
for(const f of walk(ROOT)){
  let html=fs.readFileSync(f,"utf8");
  if(!html.includes("<img")) continue;
  // inline linked stylesheets or the audit cannot see how images are sized
  html=html.replace(/<link(?=[^>]*rel="stylesheet")[^>]*href="([^"]+)"[^>]*>/g,(m,h)=>{
    if(/^https?:/.test(h)) return m;
    const p=path.normalize(path.join(path.dirname(f),h.split("?")[0]));
    return fs.existsSync(p)?"<style>"+fs.readFileSync(p,"utf8")+"</style>":m;});
  const dom=new JSDOM(html,{virtualConsole:new VirtualConsole()});
  const d=dom.window.document,w=dom.window;
  for(const i of d.querySelectorAll("img")){
    const cs=w.getComputedStyle(i);
    const aw=parseInt(i.getAttribute("width")||0);
    // an image with no computed size will render at intrinsic size
    const noW = cs.width==="auto"||cs.width==="";
    const noH = cs.height==="auto"||cs.height==="";
    if(noW && noH && aw>400){
      bad.push([f.replace(ROOT+"/",""), aw, (i.className||i.getAttribute("alt")||"").slice(0,26)]);
    }
  }
  dom.window.close();
}
console.log("images with NO computed size that will draw at intrinsic size:");
const seen=new Set();
bad.forEach(([f,w,c])=>{
  const k=f+c; if(seen.has(k))return; seen.add(k);
  console.log(`   ${f.padEnd(26)} ${String(w).padStart(5)}px wide   ${c}`);
});
console.log(`\n${bad.length} instances across ${new Set(bad.map(b=>b[0])).size} pages`);
