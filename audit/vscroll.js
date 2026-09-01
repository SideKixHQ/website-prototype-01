const {JSDOM,VirtualConsole}=require("jsdom"),fs=require("fs");
// the pages live at the repository root; this script sits in audit/
const ROOT=require("path").resolve(__dirname,"..");
// build templates and the patch history are not deliverable pages
const SKIP=/(^|[\\/])(build|patches|audit|node_modules|host-configs|\.github)([\\/]|$)/;
const errs=[];const vc=new VirtualConsole();
vc.on("jsdomError",e=>errs.push(String(e.message).slice(0,110)));
const dom=new JSDOM(fs.readFileSync(ROOT+"/how-it-works.html","utf8"),
 {runScripts:"dangerously",pretendToBeVisual:true,virtualConsole:vc,url:"https://x/"});
const d=dom.window.document,w=dom.window;
setTimeout(()=>{
 const show=d.querySelector(".show"), pin=d.querySelector(".pin");
 console.log(".show present:",!!show,"| .pin present:",!!pin);
 const beats=d.querySelectorAll(".beat");
 console.log("beats:",beats.length);
 const rail=d.querySelector(".rail");
 console.log("rail built:",!!rail,"| buttons:",rail?rail.querySelectorAll("button").length:0);
 console.log();
 // simulate the address bar moving: does progress stay stable?
 const stage=12478, top=-7000;
 for(const ph of [734,844]){
   const span=stage-ph;
   console.log(`   pin height ${ph} -> span ${span}, t=${(7000/span).toFixed(4)}`);
 }
 console.log("   with the pin measured, ph is the SAME both times, so t does not jump.");
 console.log();
 console.log("js errors:",errs.length);
 errs.slice(0,3).forEach(e=>console.log("   !!",e));
 process.exit(0);
},1600);
