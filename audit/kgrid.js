const {JSDOM,VirtualConsole}=require("jsdom"),fs=require("fs");
// the pages live at the repository root; this script sits in audit/
const ROOT=require("path").resolve(__dirname,"..");
// build templates and the patch history are not deliverable pages
const SKIP=/(^|[\\/])(build|patches|audit|node_modules|host-configs|\.github)([\\/]|$)/;
const errs=[];const vc=new VirtualConsole();
vc.on("jsdomError",e=>errs.push(String(e.message).slice(0,120)));
const dom=new JSDOM(fs.readFileSync(ROOT+"/market-data.html","utf8"),
 {runScripts:"dangerously",pretendToBeVisual:true,virtualConsole:vc,url:"https://sidekixhq.com/market-data.html"});
const d=dom.window.document,w=dom.window;
setTimeout(()=>{
 const kg=d.getElementById("kgrid");
 console.log("#kgrid present:",!!kg);
 if(kg){
   console.log("  dots built:",kg.children.length,"(script says N=300)");
   const on=[...kg.children].filter(c=>c.classList.contains("on")).length;
   console.log("  dots lit   :",on);
   const cs=w.getComputedStyle(kg);
   console.log("  display    :",cs.display,"| columns:",cs.gridTemplateColumns.slice(0,30));
 }
 const rd=d.getElementById("rdots");
 console.log("\n#rdots present:",!!rd,"(the script looks for it)");
 const dots=d.getElementById("dots");
 console.log("#dots present :",!!dots,"| children:",dots?dots.children.length:0);
 console.log("\njs errors:",errs.length);
 errs.slice(0,3).forEach(e=>console.log("   !!",e));
 process.exit(0);
},1600);
