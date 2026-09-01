const {JSDOM,VirtualConsole}=require("jsdom"),fs=require("fs"),path=require("path");
// the pages live at the repository root; this script sits in audit/
const ROOT=require("path").resolve(__dirname,"..");
// build templates and the patch history are not deliverable pages
const SKIP=/(^|[\\/])(build|patches|audit|node_modules|host-configs|\.github)([\\/]|$)/;
const pages=fs.readdirSync(ROOT).filter(f=>f.endsWith(".html")&&!SKIP.test(f)).map(f=>ROOT+"/"+f);
console.log("nav z-index vs orb z-index on every page with both:\n");
let bad=[];
for(const f of pages){
  const html=fs.readFileSync(f,"utf8");
  if(!html.includes("kx-orbnav")) continue;
  const dom=new JSDOM(html,{virtualConsole:new VirtualConsole()});
  const d=dom.window.document,w=dom.window;
  const nav=d.getElementById("kx-nav"), orb=d.getElementById("kx-orbnav");
  const nz=nav?parseInt(w.getComputedStyle(nav).zIndex)||0:0;
  const oz=orb?parseInt(w.getComputedStyle(orb).zIndex)||0:0;
  const ok=oz>nz;
  if(!ok) bad.push([f.replace(ROOT+"/",""),nz,oz]);
  console.log(`   ${f.replace(ROOT+"/","").padEnd(22)} nav ${String(nz).padStart(4)}  orb ${String(oz).padStart(4)}  ${ok?"orb on top":"NAV COVERS THE ORB"}`);
  dom.window.close();
}
console.log(`\n${bad.length} page(s) where the nav would cover the orb`);
