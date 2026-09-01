const {JSDOM,VirtualConsole}=require("jsdom"),fs=require("fs"),path=require("path");
// the pages live at the repository root; this script sits in audit/
const ROOT=require("path").resolve(__dirname,"..");
// build templates and the patch history are not deliverable pages
const SKIP=/(^|[\\/])(build|patches|audit|node_modules|host-configs|\.github)([\\/]|$)/;
function walk(d,o=[]){for(const f of fs.readdirSync(d)){const p=path.join(d,f);
  if(SKIP.test(p))continue; fs.statSync(p).isDirectory()?walk(p,o):(f.endsWith(".html")&&o.push(p));}return o;}
(async()=>{
const pages=walk(ROOT).sort();
const findings=[];
for(const f of pages){
  const dom=new JSDOM(fs.readFileSync(f,"utf8"),{virtualConsole:new VirtualConsole()});
  const d=dom.window.document;
  const add=(c,m)=>findings.push([f.replace(ROOT+"/",""),c,m]);
  const rb=d.querySelector('meta[name="robots"]');
  const noidx=rb&&/noindex/.test(rb.content);

  // 1.1.1 non-text content
  d.querySelectorAll("img").forEach(i=>{ if(i.getAttribute("alt")===null) add("1.1.1","img with no alt"); });
  d.querySelectorAll("svg").forEach(s=>{
    if(!s.getAttribute("aria-hidden") && !s.querySelector("title") && !s.getAttribute("aria-label"))
      add("1.1.1","svg neither hidden nor labelled"); });
  // 1.3.1 info and relationships
  const hs=[...d.querySelectorAll("h1,h2,h3,h4,h5,h6")].map(h=>+h.tagName[1]);
  for(let i=1;i<hs.length;i++) if(hs[i]-hs[i-1]>1){ add("1.3.1",`heading jump h${hs[i-1]} to h${hs[i]}`); break; }
  if(d.querySelectorAll("h1").length!==1 && !/index\.html$/.test(f)) add("1.3.1",`h1 count ${d.querySelectorAll("h1").length}`);
  d.querySelectorAll("input,select,textarea").forEach(i=>{
    if(i.type==="hidden") return;
    const lab = (i.id && [...d.querySelectorAll("label[for]")].some(l=>l.getAttribute("for")===i.id))
      || i.getAttribute("aria-label") || i.getAttribute("aria-labelledby") || i.closest("label");
    if(!lab) add("1.3.1","form control with no label: "+(i.id||i.type)); });
  d.querySelectorAll("table").forEach(t=>{ if(!t.querySelector("th")) add("1.3.1","table with no header cells"); });
  // 2.4.1 bypass blocks
  if(!d.querySelector("main") && !noidx && !d.getElementById("kx-root")) add("2.4.1","no main landmark");
  const sk=d.querySelector("a.skip-link");
  if(sk){const t=sk.getAttribute("href"); if(t&&t.startsWith("#")&&!d.getElementById(t.slice(1))) add("2.4.1","skip link target missing");}
  // 2.4.2 page titled
  if(!d.title || !d.title.trim()) add("2.4.2","no title");
  // 2.4.4 link purpose
  d.querySelectorAll("a[href]").forEach(a=>{
    const n=((a.textContent||"").trim()||a.getAttribute("aria-label")||a.getAttribute("title")||
             (a.querySelector("img")&&a.querySelector("img").getAttribute("alt"))||"").trim();
    if(!n) add("2.4.4","link with no accessible name: "+a.getAttribute("href"));
    else if(/^(here|click here|read more|more|link)$/i.test(n)) add("2.4.4",`vague link text "${n}"`); });
  // 3.1.1 language
  if(!d.documentElement.getAttribute("lang")) add("3.1.1","no lang attribute");
  // 4.1.2 name role value
  d.querySelectorAll("button").forEach(b=>{
    if(!((b.textContent||"").trim()||b.getAttribute("aria-label")||b.getAttribute("title")))
      add("4.1.2","button with no accessible name"); });
  ["aria-expanded","aria-pressed","aria-selected","aria-hidden"].forEach(at=>{
    d.querySelectorAll("["+at+"]").forEach(e=>{
      const v=e.getAttribute(at);
      if(!["true","false"].includes(v)) add("4.1.2",`${at}="${v}" is not true/false`); }); });
  d.querySelectorAll("[role=tab]").forEach(t=>{
    if(!t.getAttribute("aria-controls")) add("4.1.2","role=tab without aria-controls"); });
  d.querySelectorAll("[aria-labelledby],[aria-controls],[aria-describedby]").forEach(e=>{
    ["aria-labelledby","aria-controls","aria-describedby"].forEach(at=>{
      const v=e.getAttribute(at); if(!v) return;
      v.split(/\s+/).forEach(id=>{ if(id && !d.getElementById(id)) add("4.1.2",`${at} points at missing #${id}`); }); }); });
  // 4.1.1 parsing: duplicate ids
  const seen={}; d.querySelectorAll("[id]").forEach(e=>{ seen[e.id]=(seen[e.id]||0)+1; });
  Object.entries(seen).filter(([,v])=>v>1).forEach(([k,v])=>add("4.1.1",`duplicate id "${k}" x${v}`));
  dom.window.close();
}
console.log(`pages audited: ${pages.length}`);
console.log(`findings: ${findings.length}\n`);
const byCrit={};
findings.forEach(([p,c,m])=>{ (byCrit[c]=byCrit[c]||[]).push([p,m]); });
Object.keys(byCrit).sort().forEach(c=>{
  console.log(`  ${c}  (${byCrit[c].length})`);
  const uniq=[...new Set(byCrit[c].map(x=>x[1]))];
  uniq.slice(0,6).forEach(m=>{
    const n=byCrit[c].filter(x=>x[1]===m).length;
    const eg=byCrit[c].find(x=>x[1]===m)[0];
    console.log(`     ${n}x  ${m}   e.g. ${eg}`); });
});
process.exit(0);
})();
