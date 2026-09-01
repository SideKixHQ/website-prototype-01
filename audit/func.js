const {JSDOM,VirtualConsole}=require("jsdom"),fs=require("fs");
// the pages live at the repository root; this script sits in audit/
const ROOT=require("path").resolve(__dirname,"..");
// build templates and the patch history are not deliverable pages
const SKIP=/(^|[\\/])(build|patches|audit|node_modules|host-configs|\.github)([\\/]|$)/;
const load=async f=>{const errs=[];const vc=new VirtualConsole();
  vc.on("jsdomError",e=>errs.push(e.message));vc.on("error",(...a)=>errs.push(String(a[0]).slice(0,80)));
  const dom=new JSDOM(fs.readFileSync(f,"utf8"),{runScripts:"dangerously",pretendToBeVisual:true,
    virtualConsole:vc,url:"https://sidekixhq.com/x.html"});
  await new Promise(r=>setTimeout(r,700));
  return {d:dom.window.document,w:dom.window,errs:errs.filter(e=>!/\[light\]/.test(e)),dom};};
const ok=(c,m)=>console.log(`   ${c?"PASS":"FAIL"}  ${m}`);
(async()=>{

console.log("== market-data.html ==");
{const {d,w,errs}=await load(ROOT+"/market-data.html");
 const vis=()=>[...d.querySelectorAll(".rcard")].filter(c=>!c.hidden).length;
 ok(d.querySelectorAll(".rcard").length===29,"29 resource cards render");
 const q=d.getElementById("rq");
 q.value="ein";q.dispatchEvent(new w.Event("input",{bubbles:true}));
 ok(vis()===3,"search narrows to 3 for 'ein'");
 ok(d.getElementById("rcount").textContent==="3 matches","count reads '3 matches'");
 q.value="zzzz";q.dispatchEvent(new w.Event("input",{bubbles:true}));
 ok(vis()===0&&!d.getElementById("rnone").hidden,"empty state shows when nothing matches");
 q.value="";q.dispatchEvent(new w.Event("input",{bubbles:true}));
 const counts={Advice:8,Registration:5,Money:6,Data:6,"North Carolina":4};
 let allf=true;
 for(const [t,n] of Object.entries(counts)){
   d.querySelector(`.rfilt[data-type="${t}"]`).dispatchEvent(new w.MouseEvent("click",{bubbles:true}));
   if(vis()!==n) allf=false;}
 ok(allf,"all five category filters return the right count");
 d.querySelector('.rfilt[data-type="all"]').dispatchEvent(new w.MouseEvent("click",{bubbles:true}));
 ok(vis()===29,"Everything restores all 29");
 ok(d.querySelector("h1").textContent==="Help yourself.","heading is back");
 ok(d.querySelectorAll(".msec").length===3,"three sections, all open");
 ok([...d.querySelectorAll(".msec")].map(x=>x.dataset.t).join(",")==="apps,surv,who","sections in the right order");
 const b=d.querySelector(".rmore"),p=d.getElementById(b.getAttribute("aria-controls"));
 b.dispatchEvent(new w.MouseEvent("click",{bubbles:true}));
 const opened=!p.hidden&&b.getAttribute("aria-expanded")==="true";
 b.dispatchEvent(new w.MouseEvent("click",{bubbles:true}));
 ok(opened&&p.hidden&&b.getAttribute("aria-expanded")==="false","Details opens and closes with correct aria");
 ok(d.querySelectorAll(".rsave").length===0&&!d.getElementById("rtray"),"save feature fully removed");
 const exp={1:["79.6%",80],2:["69.1%",69],5:["50.2%",50],10:["34.7%",35]};
 let allm=true;
 for(const [y,[pct,lit]] of Object.entries(exp)){
   d.querySelector(`.oddb[data-y="${y}"]`).dispatchEvent(new w.MouseEvent("click",{bubbles:true}));
   await new Promise(r=>setTimeout(r,1100));
   if(d.getElementById("oddspct").textContent!==pct) allm=false;
   if([...d.getElementById("dots").children].filter(x=>x.classList.contains("lit")).length!==lit) allm=false;}
 ok(allm,"all four survival milestones show the right % and dot count");
 const nc=d.querySelector('.mtab[data-set="nc"]');
 nc.dispatchEvent(new w.MouseEvent("click",{bubbles:true}));
 const ncOn=w.getComputedStyle(d.querySelector('[data-panel="nc"]')).display!=="none"
          && w.getComputedStyle(d.querySelector('[data-panel="us"]')).display==="none";
 d.querySelector('.mtab[data-set="us"]').dispatchEvent(new w.MouseEvent("click",{bubbles:true}));
 const usBack=w.getComputedStyle(d.querySelector('[data-panel="us"]')).display!=="none";
 ok(ncOn&&usBack,"US / North Carolina toggle swaps panels both ways");
 ok(d.querySelectorAll(".kdot").length===300&&d.querySelectorAll(".kdot.on").length===10,"K field of 300 drawn, 10 lit at rest");
 ok(!!d.querySelector(".unum")&&d.querySelector(".unum").textContent==="168 million","the 168 million headline is present");
 ok(d.querySelectorAll(".turnbits li").length===7,"the seven pieces appear once, in the survival section");
 ok(d.querySelectorAll(".opbits").length===0,"the duplicate set is gone");
 ok([...d.querySelectorAll(".msec h2")].map(h=>h.textContent).join(" | ")==="Potential Entrepreneurs | Failing over time | Existing Entrepreneurs","sections carry the new names");
 ok(d.querySelectorAll(".potyr").length===5,"five time horizons offered");
 ok(!!d.querySelector("#turn")&&/does\u2019?n.t have to/.test(d.querySelector("#turn").textContent),"the statement is present");
 ok(errs.length===0,"no JS errors");}

console.log("\n== glossary.html ==");
{const {d,w,errs}=await load(ROOT+"/glossary.html");
 ok(d.querySelectorAll(".grow").length===59,"59 terms render");
 ok(d.querySelectorAll(".gsec").length===19,"19 letter sections");
 const q=d.getElementById("gq");
 q.value="runway";q.dispatchEvent(new w.Event("input",{bubbles:true}));
 ok([...d.querySelectorAll(".grow")].filter(r=>!r.hidden).length===1,"search finds 'runway'");
 ok(d.querySelectorAll("mark").length===1,"match is highlighted");
 ok([...d.querySelectorAll(".gsec")].filter(s=>!s.hidden).length===1,"empty letter sections hide");
 q.value="";q.dispatchEvent(new w.Event("input",{bubbles:true}));
 ok(d.querySelectorAll("mark").length===0&&d.querySelectorAll(".gcatdot").length===59,
    "clearing search restores every category dot");
 d.querySelector('.gfilt[data-cat="Legal"]').dispatchEvent(new w.MouseEvent("click",{bubbles:true}));
 ok([...d.querySelectorAll(".grow")].filter(r=>!r.hidden).length===12,"Legal filter returns 12");
 ok(w.getComputedStyle(d.querySelector(".gcatname")).opacity==="1","category name is always visible (1.4.1)");
 ok(errs.length===0,"no JS errors");}

console.log("\n== tools.html ==");
{const {d,w,errs}=await load(ROOT+"/tools.html");
 const g=id=>d.getElementById(id).textContent;
 ok(g("s_out")==="$6,280"&&g("b_out")==="29 sales"&&g("h_out")==="$95/hr"&&g("p_out")==="$82",
    "all four calculators compute the defaults correctly");
 const i=d.getElementById("b_price");i.value="200";i.dispatchEvent(new w.Event("input",{bubbles:true}));
 ok(g("b_out")==="20 sales"&&g("b_rev")==="$4,000","breakeven recalculates on input");
 const v=d.getElementById("b_var");v.value="500";v.dispatchEvent(new w.Event("input",{bubbles:true}));
 ok(/at or above your price/.test(g("b_sub")),"impossible input explains itself instead of breaking");
 ok(d.querySelectorAll(".cjump").length===4,"four jump chips");
 ok(errs.length===0,"no JS errors");}

console.log("\n== a template article (worksheet strip) ==");
{const {d,w,errs}=await load(ROOT+"/blog/weekly-business-check-in-template/index.html");
 ok(!!d.querySelector(".grab"),"worksheet strip present");
 ok(/\.pdf$/.test(d.querySelector(".gdlbtn").getAttribute("href")),"PDF link present");
 ok(d.querySelector(".gdlbtn").hasAttribute("download"),"download attribute set");
 ok(d.getElementById("wsrc").textContent.length>1000,"copy-as-text payload embedded");
 ok(d.querySelectorAll("#toc-list li").length===d.querySelectorAll(".body h2").length,"contents rail matches headings");
 ok(errs.length===0,"no JS errors");}

console.log("\n== resources.html ==");
{const {d,w,errs}=await load(ROOT+"/resources.html");
 const cards=d.querySelectorAll("article.card").length;
 ok(cards===63,`grid holds ${cards} cards`);
 ok(/Showing all 63 pieces/.test(d.body.innerHTML),"the count line matches the grid");
 ok([...d.querySelectorAll(".hubs a")].every(a=>!/sidekixhq\.com/.test(a.getAttribute("href"))),
    "hub tiles no longer point at WordPress");
 ok(errs.length===0,"no JS errors");}
process.exit(0);
})();
