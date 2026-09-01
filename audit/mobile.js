const {JSDOM,VirtualConsole}=require("jsdom"),fs=require("fs"),path=require("path");
// the pages live at the repository root; this script sits in audit/
const ROOT=require("path").resolve(__dirname,"..");
// build templates and the patch history are not deliverable pages
const SKIP=/(^|[\\/])(build|patches|audit|node_modules|host-configs|\.github)([\\/]|$)/;
function walk(d,o=[]){for(const f of fs.readdirSync(d)){const p=path.join(d,f);
  if(SKIP.test(p))continue; fs.statSync(p).isDirectory()?walk(p,o):(f.endsWith(".html")&&o.push(p));}return o;}
const pages=walk(ROOT).sort();
const issues={};
const add=(k,m)=>{(issues[k]=issues[k]||[]).push(m)};
for(const f of pages){
  const html=fs.readFileSync(f,"utf8");
  const dom=new JSDOM(html,{virtualConsole:new VirtualConsole()});
  const d=dom.window.document;
  const css=[...d.querySelectorAll("style")].map(s=>s.textContent).join("\n");
  const n=f.replace(ROOT+"/","");
  const vp=(d.querySelector('meta[name="viewport"]')||{}).content||"";
  if(!vp) add("no viewport meta",n);
  if(/user-scalable\s*=\s*no/i.test(vp)) add("pinch zoom disabled",n);
  if(/maximum-scale\s*=\s*(1|1\.0)\b/i.test(vp)) add("zoom capped at 1x",n);
  if(!/width=device-width/i.test(vp)) add("viewport not device-width",n);
  // blog pages get the guard from article.css, which is linked not inlined
  const linked=[...d.querySelectorAll('link[rel=stylesheet]')].map(l=>l.getAttribute("href")||"");
  let extern="";
  linked.forEach(h=>{ if(/^https?:/.test(h)) return;
    const p=path.normalize(path.join(path.dirname(f),h.split("?")[0]));
    if(fs.existsSync(p)) extern+=fs.readFileSync(p,"utf8"); });
  if(!/overflow-x:\s*hidden/.test(css+extern) && !d.getElementById("kx-root")) add("no overflow-x guard",n);
  if(!/prefers-reduced-motion/.test(css) && /animation:\s*(?!none)[\w-]/.test(css)) add("animation with no reduced-motion escape",n);
  // 16px floor on inputs, or iOS zooms the page on focus
  const strip=css.replace(/@media[^{]*\{(?:[^{}]|\{[^{}]*\})*\}/g,"");
  const m=strip.match(/(input|textarea|select)[^{}]*\{[^}]*font-size:\s*(\d+(?:\.\d+)?)px/g)||[];
  m.forEach(r=>{const v=parseFloat(r.match(/font-size:\s*(\d+(?:\.\d+)?)px/)[1]);
    if(v<16) add("input under 16px, iOS will zoom on focus",n)});
  // fixed widths wider than the narrowest phone
  (strip.match(/(?<!max-)(?<!min-)width:\s*(\d{3,})px/g)||[]).forEach(r=>{
    const v=parseInt(r.match(/(\d+)/)[1]); if(v>320) add(`fixed width ${v}px wider than a 320px screen`,n)});
  // a wide table inside overflow-x:auto is the correct pattern, not a fault
  (strip.match(/[^{}]*\{[^}]*min-width:\s*(\d{3,})px[^}]*\}/g)||[]).forEach(r=>{
    const v=parseInt(r.match(/min-width:\s*(\d+)/)[1]);
    if(v<=320) return;
    if(/overflow-x:\s*auto/.test(css)) return;
    add(`min-width ${v}px with no scroll wrapper`,n)});
  dom.window.close();
}
console.log(`pages checked: ${pages.length}\n`);
const keys=Object.keys(issues);
if(!keys.length) console.log("  no mobile issues found");
keys.forEach(k=>{
  const v=issues[k];
  console.log(`  ${v.length}x  ${k}`);
  [...new Set(v)].slice(0,4).forEach(x=>console.log(`        ${x}`));
});
process.exit(0);
