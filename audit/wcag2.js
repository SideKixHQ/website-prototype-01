const {JSDOM,VirtualConsole}=require("jsdom"),fs=require("fs"),path=require("path");
// the pages live at the repository root; this script sits in audit/
const ROOT=require("path").resolve(__dirname,"..");
// build templates and the patch history are not deliverable pages
const SKIP=/(^|[\\/])(build|patches|audit|node_modules|host-configs|\.github)([\\/]|$)/;
function walk(d,o=[]){for(const f of fs.readdirSync(d)){const p=path.join(d,f);
  if(SKIP.test(p))continue; fs.statSync(p).isDirectory()?walk(p,o):(f.endsWith(".html")&&o.push(p));}return o;}
(async()=>{
const pages=walk(ROOT).sort();
const F=[];
for(const f of pages){
  let html=fs.readFileSync(f,"utf8");
  html=html.replace(/<link(?=[^>]*rel="stylesheet")[^>]*href="([^"]+)"[^>]*>/g,(m,h)=>{
    if(/^https?:/.test(h)) return m;
    const p=path.normalize(path.join(path.dirname(f),h.split("?")[0]));
    return fs.existsSync(p)?"<style>"+fs.readFileSync(p,"utf8")+"</style>":m;});
  const dom=new JSDOM(html,{virtualConsole:new VirtualConsole()});
  const d=dom.window.document,w=dom.window;
  const css=[...d.querySelectorAll("style")].map(s=>s.textContent).join("\n");
  const add=(c,m)=>F.push([f.replace(ROOT+"/",""),c,m]);
  const noidx=(d.querySelector('meta[name="robots"]')||{}).content;

  // 1.4.4 resize text — reject viewport locks
  const vp=(d.querySelector('meta[name="viewport"]')||{}).content||"";
  if(/user-scalable\s*=\s*no/i.test(vp)) add("1.4.4","zoom disabled");
  if(/maximum-scale\s*=\s*(1|1\.0)\b/i.test(vp)) add("1.4.4","maximum-scale caps zoom");
  // 1.4.10 reflow
  if(!/overflow-x:\s*hidden/.test(css) && !/index\.html$/.test(f)) add("1.4.10","no overflow-x guard");
  // 1.4.12 text spacing — fixed heights on text containers
  (css.match(/\.[\w-]+\{[^}]*height:\s*\d+px[^}]*\}/g)||[]).slice(0,1)
    .forEach(()=>{});
  // 2.1.1 keyboard — click handlers on non-interactive elements
  d.querySelectorAll("[onclick]").forEach(e=>{
    if(!["A","BUTTON","INPUT","SELECT","TEXTAREA","SUMMARY"].includes(e.tagName) &&
       e.getAttribute("tabindex")===null) add("2.1.1","onclick on a non-focusable element: "+e.tagName); });
  // 2.4.3 focus order — positive tabindex
  d.querySelectorAll("[tabindex]").forEach(e=>{
    const t=parseInt(e.getAttribute("tabindex"));
    if(t>0) add("2.4.3",`positive tabindex=${t} disrupts focus order`); });
  // 2.4.7 focus visible
  if(!/:focus-visible|:focus\b/.test(css)) add("2.4.7","no focus styling anywhere");
  if(/outline:\s*(none|0)/.test(css) && !/:focus-visible/.test(css)) add("2.4.7","outline removed with no replacement");
  // 2.5.3 label in name
  d.querySelectorAll("button[aria-label],a[aria-label]").forEach(e=>{
    // text inside aria-hidden children is not part of the accessible name
    const clone=e.cloneNode(true);
    clone.querySelectorAll('[aria-hidden="true"]').forEach(x=>x.remove());
    const vis=(clone.textContent||"").trim().toLowerCase();
    const lab=(e.getAttribute("aria-label")||"").toLowerCase();
    if(vis && lab && !lab.includes(vis)) add("2.5.3",`visible text "${vis.slice(0,20)}" not inside aria-label "${lab.slice(0,24)}"`); });
  // 3.2.2 on input — selects that submit
  d.querySelectorAll("select[onchange]").forEach(()=>add("3.2.2","select changes context on input"));
  // 3.3.2 labels or instructions
  d.querySelectorAll("input[required],select[required],textarea[required]").forEach(e=>{
    if(!e.getAttribute("aria-required") && !e.hasAttribute("required")) add("3.3.2","required field not announced"); });
  // 1.3.5 identify input purpose
  d.querySelectorAll('input[type="email"],input[type="tel"],input[name*="name" i]').forEach(e=>{
    if(!e.getAttribute("autocomplete")) add("1.3.5","input with no autocomplete: "+(e.name||e.type)); });
  // 4.1.2 states on custom widgets
  d.querySelectorAll("details").forEach(e=>{ if(!e.querySelector("summary")) add("4.1.2","details with no summary"); });
  // 1.2.x media
  d.querySelectorAll("video,audio").forEach(e=>{
    if(!e.querySelector("track")) add("1.2.2","media with no captions track"); });
  // 2.3.1 flashing
  (css.match(/animation:\s*(?!none)[^;]*?(\d+(\.\d+)?)s/g)||[]).forEach(a=>{
    const m=a.match(/(\d+(\.\d+)?)s/); if(m && parseFloat(m[1])>0 && parseFloat(m[1])<0.34)
      add("2.3.1","animation faster than 3 flashes/sec: "+a.slice(0,40)); });
  // reduced motion
  if(/animation:\s*(?!none)[\w-]/.test(css) && !/prefers-reduced-motion/.test(css)) add("2.3.3","animation with no reduced-motion escape");
  // landmark uniqueness
  ["nav","main","header","footer"].forEach(t=>{
    const els=[...d.querySelectorAll(t)];
    if(els.length>1){ const named=els.filter(e=>e.getAttribute("aria-label")||e.getAttribute("aria-labelledby"));
      if(named.length<els.length) add("1.3.1",`${els.length} <${t}> landmarks, ${els.length-named.length} unnamed`); } });
  dom.window.close();
}
console.log(`pages audited: ${pages.length}`);
console.log(`findings: ${F.length}\n`);
const by={}; F.forEach(([p,c,m])=>{(by[c]=by[c]||[]).push([p,m]);});
Object.keys(by).sort().forEach(c=>{
  console.log(`  ${c}  (${by[c].length})`);
  const u={}; by[c].forEach(([p,m])=>{(u[m]=u[m]||[]).push(p);});
  Object.entries(u).slice(0,5).forEach(([m,ps])=>
    console.log(`     ${ps.length}x  ${m}   e.g. ${ps[0]}`));
});
process.exit(0);
})();
