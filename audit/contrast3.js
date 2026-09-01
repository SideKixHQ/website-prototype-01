const {JSDOM,VirtualConsole}=require("jsdom"),fs=require("fs"),path=require("path");
// the pages live at the repository root; this script sits in audit/
const ROOT=require("path").resolve(__dirname,"..");
// build templates and the patch history are not deliverable pages
const SKIP=/(^|[\\/])(build|patches|audit|node_modules|host-configs|\.github)([\\/]|$)/;
function walk(d,o=[]){for(const f of fs.readdirSync(d)){const p=path.join(d,f);
  if(SKIP.test(p))continue; fs.statSync(p).isDirectory()?walk(p,o):(f.endsWith(".html")&&o.push(p));}return o;}
const parse=s=>{if(!s)return null;s=s.trim();
  let m=s.match(/^#([0-9a-f]{3})$/i); if(m) return m[1].split("").map(c=>parseInt(c+c,16)).concat([1]);
  m=s.match(/^#([0-9a-f]{6})$/i); if(m) return [0,2,4].map(i=>parseInt(m[1].substr(i,2),16)).concat([1]);
  m=s.match(/rgba?\(\s*([\d.]+)[,\s]+([\d.]+)[,\s]+([\d.]+)(?:[,\s/]+([\d.]+))?\s*\)/i);
  if(m) return [+m[1],+m[2],+m[3], m[4]===undefined?1:+m[4]];
  return null;};
const lum=c=>{const s=c.slice(0,3).map(v=>{v/=255;return v<=.04045?v/12.92:Math.pow((v+.055)/1.055,2.4);});
  return .2126*s[0]+.7152*s[1]+.0722*s[2];};
const ratio=(a,b)=>{const A=lum(a),B=lum(b);return (Math.max(A,B)+.05)/(Math.min(A,B)+.05);};
const blend=(top,base)=>{const a=top[3]===undefined?1:top[3];
  return [0,1,2].map(i=>Math.round(top[i]*a+base[i]*(1-a))).concat([1]);};

(async()=>{
const pages=walk(ROOT).sort();
const fails=[]; let checked=0;
for(const f of pages){
  let html=fs.readFileSync(f,"utf8");
  html=html.replace(/<link(?=[^>]*rel="stylesheet")[^>]*href="([^"]+)"[^>]*>/g,(m,href)=>{
    if(/^https?:/.test(href)) return m;
    const p=path.normalize(path.join(path.dirname(f),href.split("?")[0]));
    return fs.existsSync(p) ? "<style>"+fs.readFileSync(p,"utf8")+"</style>" : m; });
  const dom=new JSDOM(html,{virtualConsole:new VirtualConsole()});
  const d=dom.window.document,w=dom.window;
  const vars={};
  [...d.querySelectorAll("style")].forEach(s=>{
    (s.textContent.match(/:root\s*\{([^}]*)\}/g)||[]).forEach(b=>{
      [...b.matchAll(/(--[\w-]+)\s*:\s*([^;}]+)/g)].forEach(x=>vars[x[1]]=x[2].trim()); }); });
  const resolve=(v,n=0)=>{ if(!v||n>5) return v;
    const m=v.match(/var\((--[\w-]+)(?:\s*,\s*([^)]*))?\)/);
    return m ? resolve(v.replace(m[0], vars[m[1]] || m[2] || ""), n+1) : v; };

  // composite the full ancestor stack, honouring alpha at every layer
  const bgOf=el=>{
    const chain=[]; let n=el;
    while(n && n.nodeType===1){ chain.unshift(n); n=n.parentElement; }
    let bg=[5,5,5,1];
    for(const node of chain){
      const cs=w.getComputedStyle(node);
      const c=parse(resolve(cs.backgroundColor||""));
      if(c && c[3]>0) bg=blend(c,bg);
      const bi=cs.backgroundImage;
      if(bi && bi!=="none"){
        const stops=[...resolve(bi).matchAll(/#[0-9a-f]{6}|#[0-9a-f]{3}|rgba?\([^)]*\)/gi)]
          .map(m=>parse(m[0])).filter(Boolean);
        if(stops.length){
          // the worst case for text is whichever stop lands furthest from it
          const blended=stops.map(s=>blend(s,bg));
          bg=blended.reduce((a,b)=>lum(a)<lum(b)?a:b);
        } } }
    return bg; };

  d.querySelectorAll("p,li,span,a,h1,h2,h3,h4,h5,h6,td,th,dd,dt,summary,button,label,figcaption,strong,b,em").forEach(el=>{
    const txt=(el.textContent||"").trim();
    if(!txt || el.querySelector("p,li,div,h1,h2,h3,h4")) return;
    if(el.closest('[aria-hidden="true"]')) return;
    if(el.classList.contains("skip-link")||el.classList.contains("sr-only")) return;
    if(el.closest(".sr-only")) return;
    const cs=w.getComputedStyle(el);
    if(cs.display==="none"||cs.visibility==="hidden"||el.closest("[hidden]")) return;
    if(cs.position==="absolute" && (parseFloat(cs.width)===1||cs.clip&&cs.clip!=="auto")) return;
    const fgRaw=resolve(cs.color||""); const fg=parse(fgRaw);
    if(!fg || fg[3]===0) return;
    const bg=bgOf(el);
    const size=parseFloat(resolve(cs.fontSize))||16;
    const wt=parseInt(cs.fontWeight)||400;
    const need=(size>=24||(wt>=700&&size>=18.66))?3:4.5;
    const r=ratio(blend(fg,bg),bg);
    checked++;
    if(r<need) fails.push([f.replace(ROOT+"/",""),txt.slice(0,30),fgRaw,`rgb(${bg.slice(0,3)})`,size,r.toFixed(2),need]);
  });
  dom.window.close();
}
console.log(`text nodes measured: ${checked}`);
console.log(`below WCAG AA     : ${fails.length}\n`);
const seen=new Set();
fails.forEach(x=>{ const k=x[2]+"|"+x[3]+"|"+x[4]; if(seen.has(k))return; seen.add(k);
  const n=fails.filter(y=>y[2]+"|"+y[3]+"|"+y[4]===k).length;
  console.log(`  ${x[5]}:1 need ${x[6]}  ${n}x  ${x[2]} on ${x[3]} @${x[4]}px   "${x[1]}"  ${x[0]}`); });
process.exit(0);
})();
