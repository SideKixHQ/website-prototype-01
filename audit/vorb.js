const {JSDOM,VirtualConsole}=require("jsdom"),fs=require("fs");
// the pages live at the repository root; this script sits in audit/
const ROOT=require("path").resolve(__dirname,"..");
// build templates and the patch history are not deliverable pages
const SKIP=/(^|[\\/])(build|patches|audit|node_modules|host-configs|\.github)([\\/]|$)/;
for(const f of [ROOT+"/market-data.html",ROOT+"/membership.html",ROOT+"/events.html"]){
  const dom=new JSDOM(fs.readFileSync(f,"utf8"),{virtualConsole:new VirtualConsole()});
  const d=dom.window.document,w=dom.window;
  const g=(sel,p)=>{const e=d.querySelector(sel);return e?w.getComputedStyle(e)[p]:"(none)"};
  const cta=d.querySelector("#kx-nav .kx-mag");
  const orb=d.getElementById("kx-orbnav");
  console.log(f.replace(ROOT+"/",""));
  console.log("   old CTA display :",cta?w.getComputedStyle(cta).display:"(gone from markup)");
  console.log("   orb position    :",g("#kx-orbnav","position"),
              "top:",g("#kx-orbnav","top"),"bottom:",g("#kx-orbnav","bottom"),
              "right:",g("#kx-orbnav","right"));
  console.log("   orb z-index     :",g("#kx-orbnav","zIndex"),"| nav z-index:",g("#kx-nav","zIndex"));
  console.log("   button size     :",g("#kx-orbmaster","width"),"x",g("#kx-orbmaster","height"));
  console.log("   tray direction  :",g("#kx-orbtray","flexDirection"),
              "justify:",g("#kx-orbtray","justifyContent"));
  console.log("   nav right pad   :",g("#kx-nav","paddingRight"));
  console.log();
  dom.window.close();
}
