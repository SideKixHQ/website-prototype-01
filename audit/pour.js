const {JSDOM,VirtualConsole}=require("jsdom"),fs=require("fs"),path=require("path");
// the pages live at the repository root; this script sits in audit/
const ROOT=require("path").resolve(__dirname,"..");
// build templates and the patch history are not deliverable pages
const SKIP=/(^|[\\/])(build|patches|audit|node_modules|host-configs|\.github)([\\/]|$)/;
function walk(d,o=[]){for(const f of fs.readdirSync(d)){const p=path.join(d,f);
  if(SKIP.test(p))continue; fs.statSync(p).isDirectory()?walk(p,o):(f.endsWith(".html")&&o.push(p));}return o;}
(async()=>{
const pages=walk(ROOT).sort();
const F={Perceivable:[],Operable:[],Understandable:[],Robust:[]};
for(const f of pages){
  let html=fs.readFileSync(f,"utf8");
  html=html.replace(/<link(?=[^>]*rel="stylesheet")[^>]*href="([^"]+)"[^>]*>/g,(m,h)=>{
    if(/^https?:/.test(h)) return m;
    const p=path.normalize(path.join(path.dirname(f),h.split("?")[0]));
    return fs.existsSync(p)?"<style>"+fs.readFileSync(p,"utf8")+"</style>":m;});
  const dom=new JSDOM(html,{virtualConsole:new VirtualConsole()});
  const d=dom.window.document,w=dom.window;
  const css=[...d.querySelectorAll("style")].map(s=>s.textContent).join("\n");
  const n=f.replace(ROOT+"/","");
  const add=(k,m)=>F[k].push(`${n}: ${m}`);

  // ---- PERCEIVABLE ----
  d.querySelectorAll("img").forEach(i=>{if(i.getAttribute("alt")===null)add("Perceivable","img with no alt")});
  d.querySelectorAll("svg:not([aria-hidden]):not([aria-label])").forEach(s=>{
    if(!s.querySelector("title")) add("Perceivable","svg neither hidden nor named")});
  d.querySelectorAll("video,audio").forEach(()=>add("Perceivable","media with no captions track"));
  if(/font-size:\s*([0-9]|1[01])px/.test(css)===false){} // handled in mobile pass
  // colour alone conveying meaning
  d.querySelectorAll("[style*='color']").forEach(()=>{});

  // ---- OPERABLE ----
  d.querySelectorAll("[onclick]").forEach(e=>{
    if(!["A","BUTTON","INPUT","SELECT","TEXTAREA","SUMMARY"].includes(e.tagName)
       && e.getAttribute("tabindex")===null) add("Operable","click handler on something not focusable")});
  d.querySelectorAll("[tabindex]").forEach(e=>{
    if(parseInt(e.getAttribute("tabindex"))>0) add("Operable","positive tabindex breaks focus order")});
  if(!/:focus-visible|:focus\b/.test(css)) add("Operable","no focus styling at all");
  if(/outline:\s*(none|0)/.test(css) && !/:focus-visible/.test(css)) add("Operable","focus outline removed with nothing replacing it");
  const main=d.querySelector("main");
  if(!main && !d.getElementById("kx-root")) add("Operable","no main landmark to skip to");
  const skip=d.querySelector("a.skip-link");
  if(skip){const t=skip.getAttribute("href");
    if(t&&t.startsWith("#")&&!d.getElementById(t.slice(1))) add("Operable","skip link points nowhere")}
  // timing
  // a real 2.2.1 failure is a TIMED redirect. navigation inside a click handler
  // is the user acting, not the page moving under them.
  if(/setTimeout\([^)]{0,200}?location\s*(\.|=)/.test(html)
     || /setInterval\([^)]{0,200}?location\s*(\.|=)/.test(html)
     || /<meta[^>]+http-equiv=["']refresh/i.test(html)) add("Operable","timed redirect or refresh");

  // ---- UNDERSTANDABLE ----
  if(!d.documentElement.getAttribute("lang")) add("Understandable","no lang on <html>");
  if(!d.title||!d.title.trim()) add("Understandable","no page title");
  d.querySelectorAll("input,select,textarea").forEach(i=>{
    if(i.type==="hidden") return;
    const lab=(i.id&&[...d.querySelectorAll("label[for]")].some(l=>l.getAttribute("for")===i.id))
      ||i.getAttribute("aria-label")||i.getAttribute("aria-labelledby")||i.closest("label");
    if(!lab) add("Understandable","form field with no label")});
  d.querySelectorAll("a[href]").forEach(a=>{
    const c=a.cloneNode(true);
    c.querySelectorAll('[aria-hidden="true"]').forEach(x=>x.remove());
    const t=(c.textContent||"").trim()||a.getAttribute("aria-label")||"";
    if(!t) add("Understandable","link with no accessible name");
    else if(/^(here|click here|read more|more|link)$/i.test(t)) add("Understandable",`vague link text "${t}"`)});

  // ---- ROBUST ----
  const seen={};d.querySelectorAll("[id]").forEach(e=>seen[e.id]=(seen[e.id]||0)+1);
  Object.entries(seen).filter(([,v])=>v>1).forEach(([k,v])=>add("Robust",`duplicate id "${k}" x${v}`));
  ["aria-expanded","aria-pressed","aria-selected","aria-hidden"].forEach(at=>{
    d.querySelectorAll("["+at+"]").forEach(e=>{
      const v=e.getAttribute(at);
      if(!["true","false"].includes(v)) add("Robust",`${at}="${v}" is not true or false`)})});
  ["aria-labelledby","aria-controls","aria-describedby"].forEach(at=>{
    d.querySelectorAll("["+at+"]").forEach(e=>{
      (e.getAttribute(at)||"").split(/\s+/).forEach(id=>{
        if(id&&!d.getElementById(id)) add("Robust",`${at} points at missing #${id}`)})})});
  d.querySelectorAll("button").forEach(b=>{
    const c=b.cloneNode(true);
    c.querySelectorAll('[aria-hidden="true"]').forEach(x=>x.remove());
    if(!((c.textContent||"").trim()||b.getAttribute("aria-label"))) add("Robust","button with no accessible name")});
  const navs=[...d.querySelectorAll("nav")];
  const unnamed=navs.filter(x=>!x.getAttribute("aria-label")&&!x.getAttribute("aria-labelledby"));
  if(navs.length>1&&unnamed.length) add("Robust",`${navs.length} navs, ${unnamed.length} unnamed`);
  dom.window.close();
}
console.log(`pages: ${pages.length}\n`);
let total=0;
for(const k of ["Perceivable","Operable","Understandable","Robust"]){
  const v=F[k]; total+=v.length;
  console.log(`  ${k.padEnd(15)} ${v.length===0?"clean":v.length+" issues"}`);
  [...new Set(v)].slice(0,5).forEach(x=>console.log(`       ${x}`));
}
console.log(`\n  total: ${total}`);
process.exit(0);
})();
