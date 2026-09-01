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
let stats={jsonld:0,faq:0,article:0,breadcrumb:0,org:0,howto:0,speakable:0};
for(const f of pages){
  const html=fs.readFileSync(f,"utf8");
  const dom=new JSDOM(html,{virtualConsole:new VirtualConsole()});
  const d=dom.window.document;
  const n=f.replace(ROOT+"/","");
  const noindex=/noindex/.test((d.querySelector('meta[name="robots"]')||{}).content||"");

  const t=(d.title||"").trim();
  if(!t) add("no <title>",n);
  else if(t.length>62) add(`title over 62 chars (${t.length})`,n);
  else if(t.length<20) add(`title under 20 chars (${t.length})`,n);

  const desc=((d.querySelector('meta[name="description"]')||{}).content||"").trim();
  if(!desc) add("no meta description",n);
  else if(desc.length>160) add(`description over 160 chars (${desc.length})`,n);
  else if(desc.length<70) add(`description under 70 chars (${desc.length})`,n);

  if(!d.querySelector('link[rel="canonical"]')) add("no canonical",n);
  if(!d.querySelector('meta[property="og:title"]')) add("no og:title",n);
  if(!d.querySelector('meta[property="og:image"]')) add("no og:image",n);
  if(!d.querySelector('meta[name="twitter:card"]')) add("no twitter card",n);
  if(!d.querySelector("h1") && !noindex) add("no h1",n);
  if(d.querySelectorAll("h1").length>1) add("more than one h1",n);

  // structured data
  const ld=[...d.querySelectorAll('script[type="application/ld+json"]')];
  if(!ld.length && !noindex) add("no structured data at all",n);
  ld.forEach(s=>{
    stats.jsonld++;
    let j; try{ j=JSON.parse(s.textContent); }catch(e){ add("structured data will not parse",n); return; }
    // schema can nest inside @graph, which the old counter never looked at
    let arr=Array.isArray(j)?j:[j];
    arr=arr.flatMap(o=>o&&o["@graph"]?o["@graph"]:[o]);
    arr.forEach(o=>{
      const ty=o["@type"];
      if(ty==="FAQPage") stats.faq++;
      if(ty==="Article"||ty==="BlogPosting") stats.article++;
      if(ty==="BreadcrumbList") stats.breadcrumb++;
      if(ty==="Organization") stats.org++;
      if(ty==="HowTo") stats.howto++;
      if(o.speakable) stats.speakable++;
    });
  });

  // images
  d.querySelectorAll("img").forEach(i=>{
    // alt="" is correct for a decorative image. only a MISSING alt is a fault.
    if(i.getAttribute("alt")===null) add("image with no alt attribute at all",n);
    // an image with no src is a placeholder filled in by script. it has no
    // intrinsic size to declare.
    if((i.getAttribute("src")||"") && (!i.getAttribute("width")||!i.getAttribute("height")))
      add("image with no width/height, causes layout shift",n);
    if(!i.getAttribute("loading")) add("image with no loading attribute",n);
  });
  dom.window.close();
}
console.log(`pages: ${pages.length}\n`);
console.log("structured data across the site:");
Object.entries(stats).forEach(([k,v])=>console.log(`   ${k.padEnd(12)} ${v}`));
console.log("\nissues:");
const keys=Object.keys(issues).sort((a,b)=>issues[b].length-issues[a].length);
if(!keys.length) console.log("   none");
keys.forEach(k=>{
  console.log(`   ${String(issues[k].length).padStart(3)}x  ${k}`);
  [...new Set(issues[k])].slice(0,3).forEach(x=>console.log(`          ${x}`));
});
process.exit(0);
