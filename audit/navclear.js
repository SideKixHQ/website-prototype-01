const {JSDOM,VirtualConsole}=require("jsdom"),fs=require("fs"),path=require("path");
// the pages live at the repository root; this script sits in audit/
const ROOT=require("path").resolve(__dirname,"..");
// build templates and the patch history are not deliverable pages
const SKIP=/(^|[\\/])(build|patches|audit|node_modules|host-configs|\.github)([\\/]|$)/;
// a real check: does anything sit under the fixed nav bar?
const pages=fs.readdirSync(ROOT).filter(f=>f.endsWith(".html")&&!SKIP.test(f)).map(f=>ROOT+"/"+f);
let bad=[];
for(const f of pages){
  const html=fs.readFileSync(f,"utf8");
  if(!html.includes('id="kx-nav"')) continue;
  const dom=new JSDOM(html,{virtualConsole:new VirtualConsole()});
  const d=dom.window.document,w=dom.window;
  const main=d.querySelector("main");
  if(!main) continue;
  // the first element in flow needs clearance from somewhere
  let el=main, pad=0, hops=0;
  const first=main.children[0];
  if(first){
    let n=first, total=0;
    while(n && n!==main && hops++<4){
      const p=parseFloat(w.getComputedStyle(n).paddingTop)||0;
      const m=parseFloat(w.getComputedStyle(n).marginTop)||0;
      total+=p+m; n=n.parentElement;
    }
    total+=parseFloat(w.getComputedStyle(main).paddingTop)||0;
    const raw=html;
    const hasClamp=/padding:\s*clamp\([^)]*\)/.test(raw);
    if(total<80 && !hasClamp) bad.push([f.replace(ROOT+"/",""),total,first.tagName+"."+(first.className||"")]);
  }
  dom.window.close();
}
console.log("pages whose first content may sit under the fixed nav:");
if(!bad.length) console.log("   none");
bad.forEach(([f,t,el])=>console.log(`   ${f.padEnd(24)} clearance ${t}px   first: ${el}`));
