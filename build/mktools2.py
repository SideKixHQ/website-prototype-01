import os
import sys, json, html; sys.path.insert(0,'/home/claude/build')
from shell import page


SITE="https://sidekixhq.com"
DESC=("Four free calculators for people starting something: startup costs, breakeven point, "
      "hourly rate and product pricing. Nothing saved, nothing sent.")
def e(s): return html.escape(s,quote=True)

schema={"@context":"https://schema.org","@type":"WebApplication",
 "name":"SideKix Business Calculators","url":f"{SITE}/tools.html",
 "applicationCategory":"BusinessApplication","operatingSystem":"Any","isAccessibleForFree":True,
 "description":DESC,"offers":{"@type":"Offer","price":"0","priceCurrency":"USD"},
 "publisher":{"@id":f"{SITE}/#organization"},
 "featureList":["Startup cost estimator","Breakeven calculator","Hourly rate calculator","Product pricing calculator"]}
faqs=[("Do these calculators cost anything?","Yes. There is no account, no email and no payment. Everything runs in your browser."),
 ("Is my data saved or sent anywhere?","No. Nothing you type leaves the page and nothing is stored. Closing the tab clears it."),
 ("How do I work out my breakeven point?","Divide your fixed costs by the contribution each sale makes, which is your price minus the variable cost of delivering it. The breakeven calculator on this page does that arithmetic and shows the revenue figure it corresponds to."),
 ("How do I set a freelance hourly rate?","Start from the income you want, add your business costs, then divide by the hours you can actually bill, which is always fewer than the hours you work. The hourly rate calculator shows both the raw figure and what it becomes once unbillable time is accounted for.")]
faqschema={"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
 {"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in faqs]}
crumbs={"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
 {"@type":"ListItem","position":1,"name":"Home","item":f"{SITE}/"},
 {"@type":"ListItem","position":2,"name":"Resources","item":f"{SITE}/resources.html"},
 {"@type":"ListItem","position":3,"name":"Calculators","item":f"{SITE}/tools.html"}]}

def row(lab,cid,val,unit="$",hint=""):
    return (f'<div class="crow"><label for="{cid}">{lab}'
            f'{f"<span class=chint>{hint}</span>" if hint else ""}</label>'
            f'<span class="cin"><span class="cu">{unit}</span>'
            f'<input id="{cid}" type="number" inputmode="decimal" min="0" step="any" value="{val}"></span></div>')
def out(oid,label,dts,k):
    dl="".join(f'<dt>{a}</dt><dd id="{b}"></dd>' for a,b in dts)
    return (f'<aside class="cout"><p class="col">{label}</p>'
            f'<p class="cov" id="{oid}_out"></p><p class="cos" id="{oid}_sub"></p>'
            f'<dl>{dl}</dl>'
            f'<button class="ccopy kx-mag" type="button" data-k="{k}">Copy this result</button></aside>')

CSS="""
/* calculators — own namespace, nothing here matches a theme script selector */
/* an author display rule outranks the browser rule for [hidden] */
.calcs [hidden]{display:none !important}
.calcs .cbackrow{display:flex;justify-content:center;margin:0 0 22px}
.calcs .cback{display:inline-flex;align-items:center;gap:8px;min-height:44px;text-decoration:none;
  font-family:var(--util);font-size:10.5px;letter-spacing:.18em;text-transform:uppercase;
  color:var(--grey);transition:color .25s}
.calcs .cback:hover{color:var(--gold-pale)}
.calcs .cback svg{width:15px;height:15px;fill:none;stroke:currentColor;stroke-width:2;
  stroke-linecap:round;stroke-linejoin:round}

/* jump chips: same metrics as the blog index filter chips */
.calcs .cjumps{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin:0 auto 34px;max-width:860px}
.calcs .cjump{font-family:var(--util);font-size:10.5px;letter-spacing:.16em;text-transform:uppercase;
  cursor:pointer;background:none;border:1px solid rgba(212,168,86,.32);color:#B9B4AB;
  border-radius:999px;padding:0 16px;min-height:44px;
  transition:background .3s,color .3s,border-color .3s}
.calcs .cjump:hover{border-color:var(--gold);color:#F3E4A8}
.calcs .cjump:focus-visible{outline:3px solid var(--gold-pale);outline-offset:3px}
.calcs .cjump[data-c="#F0855A"]{--c:#F0855A;color:#F0855A;border-color:color-mix(in srgb,#F0855A 40%,transparent)}
.calcs .cjump[data-c="#F0855A"]:hover{border-color:#F0855A;background:color-mix(in srgb,#F0855A 12%,transparent)}
.calcs .cjump[data-c="#F0855A"][aria-pressed="true"]{background:#F0855A;border-color:#F0855A;color:#0b0b0c;font-weight:700}
.calcs .cjump[data-c="#FFE7A6"]{--c:#FFE7A6;color:#FFE7A6;border-color:color-mix(in srgb,#FFE7A6 40%,transparent)}
.calcs .cjump[data-c="#FFE7A6"]:hover{border-color:#FFE7A6;background:color-mix(in srgb,#FFE7A6 12%,transparent)}
.calcs .cjump[data-c="#FFE7A6"][aria-pressed="true"]{background:#FFE7A6;border-color:#FFE7A6;color:#0b0b0c;font-weight:700}
.calcs .cjump[data-c="#5FB6A6"]{--c:#5FB6A6;color:#5FB6A6;border-color:color-mix(in srgb,#5FB6A6 40%,transparent)}
.calcs .cjump[data-c="#5FB6A6"]:hover{border-color:#5FB6A6;background:color-mix(in srgb,#5FB6A6 12%,transparent)}
.calcs .cjump[data-c="#5FB6A6"][aria-pressed="true"]{background:#5FB6A6;border-color:#5FB6A6;color:#0b0b0c;font-weight:700}
.calcs .cjump[data-c="#B18BE4"]{--c:#B18BE4;color:#B18BE4;border-color:color-mix(in srgb,#B18BE4 40%,transparent)}
.calcs .cjump[data-c="#B18BE4"]:hover{border-color:#B18BE4;background:color-mix(in srgb,#B18BE4 12%,transparent)}
.calcs .cjump[data-c="#B18BE4"][aria-pressed="true"]{background:#B18BE4;border-color:#B18BE4;color:#0b0b0c;font-weight:700}

/* each calculator carries the colour of its jump chip */
.calcs .calc[id="startup"]{--c:#F0855A}
.calcs .calc[id="breakeven"]{--c:#FFE7A6}
.calcs .calc[id="hourly"]{--c:#5FB6A6}
.calcs .calc[id="pricing"]{--c:#B18BE4}
.calcs .calc .col{color:color-mix(in srgb,var(--c,#D4A856) 78%,#947c4a)}
.calcs .calc .cov{color:var(--c,#F3E4A8)}
.calcs .calc:hover{border-color:color-mix(in srgb,var(--c,#D4A856) 45%,transparent)}

/* hub tiles, matching .hubs and .hub */
.calcs .chubs{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px;
  max-width:900px;margin:56px auto 0}
.calcs .chub{color:#E3DED2;border:1px solid rgba(212,168,86,.4);border-radius:16px;padding:26px;text-decoration:none;
  display:block;background:linear-gradient(180deg,rgba(26,20,8,.5),rgba(8,8,9,.7));
  transition:transform .3s,border-color .3s}
.calcs .chub:hover{transform:translateY(-3px);border-color:var(--gold)}
.calcs .chub b{display:block;font-family:var(--display);font-size:26px;color:#FFF8E8;margin-bottom:4px}
.calcs .chub span{font-family:var(--util);font-size:10.5px;letter-spacing:.18em;text-transform:uppercase;
  color:var(--gold-mid)}
.calcs .calc{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,318px);gap:34px;
  align-items:start;padding:30px;margin:0 auto 16px;max-width:1180px;border-radius:14px;
  border:1px solid rgba(205,170,99,.32);background:linear-gradient(180deg,#0d0b06,#070706)}
.calcs .calc h2{font-family:var(--display);font-weight:600;font-size:clamp(24px,3.1vw,34px);
  line-height:1.12;color:#FFF8E8;margin:0 0 8px;text-align:left}
.calcs .cdek{font-size:15.5px;line-height:1.62;color:#B9B4AB;margin:0 0 22px;max-width:54ch}
.calcs .crow{display:flex;align-items:center;gap:14px;flex-wrap:wrap;padding:7px 0}
.calcs .crow label{flex:1 1 210px;font-size:15px;line-height:1.45;color:#CFC9BE}
.calcs .chint{display:block;font-family:var(--util);font-size:10.5px;letter-spacing:.04em;
  color:var(--grey);margin-top:2px}
.calcs .cin{display:inline-flex;align-items:center;flex:0 0 162px;min-height:46px;overflow:hidden;
  border:1px solid rgba(205,170,99,.32);border-radius:10px;background:#070706}
.calcs .cin:focus-within{border-color:var(--gold);outline:2px solid rgba(212,168,86,.32);outline-offset:1px}
.calcs .cu{font-family:var(--util);font-size:12px;color:#947c4a;padding:0 2px 0 13px}
.calcs .cin input{width:100%;min-height:44px;border:0;background:transparent;color:#FFF8E8;
  font-family:var(--body);font-size:16px;padding:0 12px 0 6px}
.calcs .cin input::-webkit-outer-spin-button,
.calcs .cin input::-webkit-inner-spin-button{-webkit-appearance:none;margin:0}
.calcs .cin input:focus{outline:none}
.calcs .cout{border:1px solid rgba(212,168,86,.34);border-radius:14px;padding:22px;
  background:linear-gradient(160deg,rgba(26,20,8,.62),rgba(8,8,9,.72))}
.calcs .col{font-family:var(--util);font-size:9.5px;letter-spacing:.2em;text-transform:uppercase;
  color:#947c4a;margin:0 0 6px}
.calcs .cov{font-family:var(--display);font-weight:600;font-size:clamp(30px,4vw,42px);line-height:1.04;
  color:var(--gold-pale);margin:0 0 4px;word-break:break-word}
.calcs .cos{font-size:13.5px;line-height:1.55;color:#B9B4AB;margin:0 0 16px}
.calcs .cout dl{margin:0 0 16px;padding-top:14px;border-top:1px solid rgba(212,168,86,.22)}
.calcs .cout dt{font-family:var(--util);font-size:10.5px;letter-spacing:.07em;color:var(--grey);margin-top:9px}
.calcs .cout dd{margin:1px 0 0;font-size:16px;font-weight:600;color:#FFF8E8;min-height:20px}
.calcs .ccopy{width:100%;min-height:44px;cursor:pointer;border-radius:999px;font-weight:600;font-size:13.5px;
  font-family:var(--body);border:1px solid rgba(212,168,86,.45);color:var(--gold-pale);
  background:rgba(212,168,86,.08);transition:border-color .3s,color .3s}
.calcs .ccopy:hover{border-color:var(--gold);color:#FFF8E8}
.calcs .ccopy.ok{background:rgba(212,168,86,.24);color:#FFF8E8}
.calcs .cfaq{max-width:62ch;margin:56px auto 0;text-align:left}
.calcs .cfaq h2{font-family:var(--display);font-weight:600;font-size:28px;color:#FFF8E8;margin:0 0 12px;text-align:center}
.calcs .cfaq details{border-bottom:1px solid rgba(205,170,99,.2);padding:13px 0}
.calcs .cfaq summary{cursor:pointer;font-weight:600;color:#FFF8E8;font-size:15.5px;min-height:32px}
.calcs .cfaq p{margin:9px 0 0;color:#B9B4AB;font-size:15px;line-height:1.62}
@media(max-width:900px){.calcs .calc{grid-template-columns:1fr;gap:22px;padding:22px}}
/* ---- mobile ---- */
@media(max-width:760px){
  .calcs .cjumps{gap:6px}
  .calcs .cjump{min-height:44px;font-size:11px;padding:0 14px}
  .calcs .calc{padding:20px 16px;border-radius:12px}
  .calcs .calc h2{font-size:23px}
  .calcs .cdek{font-size:15px;margin-bottom:16px}
  /* label above the field, so the number is never squeezed */
  .calcs .crow{gap:6px 12px;padding:9px 0;border-bottom:1px solid rgba(212,168,86,.08)}
  .calcs .crow label{flex:1 1 100%;font-size:14.5px}
  .calcs .cin{flex:1 1 100%;min-height:52px}
  .calcs .cin input{min-height:50px;font-size:16px}
  .calcs .cout{position:sticky;bottom:8px;padding:18px;
    background:linear-gradient(160deg,rgba(26,20,8,.96),rgba(8,8,9,.97));
    -webkit-backdrop-filter:blur(8px);backdrop-filter:blur(8px)}
  .calcs .cov{font-size:30px}
  .calcs .ccopy{min-height:48px}
  .calcs .chub{padding:22px}
  .calcs .chub b{font-size:22px}
  .calcs .cfaq summary{min-height:44px;display:flex;align-items:center}
}
@media(max-width:400px){
  .calcs .cjump{padding:0 12px;letter-spacing:.1em}
  .calcs .calc{padding:18px 13px}
}
@media print{.calcs .cjumps,.calcs .ccopy{display:none}}
"""

JS = r"""
(function(){
  var root=document.querySelector('.calcs'); if(!root) return;
  function n(id){var e=document.getElementById(id);var v=e?parseFloat(e.value):0;return isFinite(v)&&v>0?v:0;}
  function raw(id){var e=document.getElementById(id);var v=e?parseFloat(e.value):0;return isFinite(v)?v:0;}
  var DASH='\u2014';
  function M(x){return isFinite(x)?('$'+Math.round(x).toLocaleString('en-US')):DASH;}
  function P(x){return isFinite(x)?((Math.round(x*10)/10)+'%'):DASH;}
  function set(id,t){var e=document.getElementById(id); if(e) e.textContent=t;}

  function startup(){
    var one=n('s_reg')+n('s_equip')+n('s_web')+n('s_stock')+n('s_pro');
    var mo=n('s_rent')+n('s_tools')+n('s_ins')+n('s_mkt')+n('s_other');
    var mos=n('s_months')||6, total=one+mo*mos;
    set('s_out',M(total)); set('s_one',M(one)); set('s_mo',M(mo)); set('s_run',M(mo*mos));
    set('s_sub','One-time setup plus '+mos+' month'+(mos===1?'':'s')+' of running costs.');
    window.__s='Startup cost estimate: '+M(total)+' total. One-time setup '+M(one)+', monthly running costs '+
      M(mo)+', covering '+mos+' months ('+M(mo*mos)+').';
  }
  function breakeven(){
    var f=n('b_fixed'), p=n('b_price'), v=n('b_var'), c=p-v;
    if(p<=0||c<=0){
      set('b_out',DASH);
      set('b_sub', p<=0?'Add a price to see the breakeven point.'
        :'Your variable cost is at or above your price, so no number of sales breaks even.');
      set('b_units',DASH); set('b_rev',DASH); set('b_margin',DASH); window.__b=''; return;
    }
    var u=Math.ceil(f/c);
    set('b_out',u.toLocaleString('en-US')+' sales');
    set('b_sub','Per month, at '+M(p)+' each, to cover '+M(f)+' of fixed costs.');
    set('b_units',u.toLocaleString('en-US')); set('b_rev',M(u*p)); set('b_margin',P(c/p*100));
    window.__b='Breakeven: '+u+' sales a month at '+M(p)+' each ('+M(u*p)+' revenue). Fixed costs '+
      M(f)+', contribution per sale '+M(c)+', contribution margin '+P(c/p*100)+'.';
  }
  function hourly(){
    var want=n('h_income'), costs=n('h_costs'), wk=n('h_weeks')||46, hrs=n('h_hours')||30, bill=n('h_bill')||60;
    var b=wk*hrs*(bill/100);
    if(b<=0){ set('h_out',DASH); set('h_sub','Add your working weeks and hours.');
      set('h_bh',DASH); set('h_day',DASH); set('h_need',DASH); window.__h=''; return; }
    var need=want+costs, rate=need/b;
    set('h_out',M(rate)+'/hr');
    set('h_sub','To take home '+M(want)+' after '+M(costs)+' of business costs.');
    set('h_bh',Math.round(b).toLocaleString('en-US')+' hrs'); set('h_day',M(rate*8)); set('h_need',M(need));
    window.__h='Hourly rate: '+M(rate)+' an hour. Target income '+M(want)+' plus '+M(costs)+' costs = '+
      M(need)+', across '+Math.round(b)+' billable hours a year ('+wk+' weeks x '+hrs+' hrs at '+bill+
      '% billable). Day rate about '+M(rate*8)+'.';
  }
  function pricing(){
    var mat=n('p_mat'), lab=n('p_lab'), ov=n('p_over'), mg=raw('p_margin'), fee=raw('p_fee');
    var unit=mat+lab+ov;
    if(unit<=0||mg<=0||mg>=100){
      set('p_out',DASH);
      set('p_sub', unit<=0?'Add your unit costs to see a price.':'Enter a target margin between 1 and 99.');
      set('p_unit',M(unit)); set('p_profit',DASH); set('p_net',DASH); window.__p=''; return;
    }
    var price=unit/(1-mg/100);
    var hasFee=(fee>0&&fee<100);
    if(hasFee) price=price/(1-fee/100);
    var feeAmt=hasFee?price*(fee/100):0, net=price-feeAmt-unit;
    set('p_out',M(price));
    set('p_sub','Unit cost '+M(unit)+' at a '+mg+'% target margin.');
    set('p_unit',M(unit)); set('p_profit',M(net)); set('p_net',P(net/price*100));
    window.__p='Suggested price: '+M(price)+'. Unit cost '+M(unit)+' (materials '+M(mat)+', labor '+M(lab)+
      ', overhead '+M(ov)+'), target margin '+mg+'%, payment fees '+fee+'%. Profit per sale about '+
      M(net)+' ('+P(net/price*100)+').';
  }
  var RM=!!(window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches);
  var wash=document.getElementById('reswash');
  if(!wash){ wash=document.createElement('div'); wash.id='reswash'; document.body.appendChild(wash); }
  var off=null;
  function washTo(c){ clearTimeout(off); wash.style.setProperty('--wash',c); wash.classList.add('on'); }
  function washOff(){ off=setTimeout(function(){ wash.classList.remove('on'); },260); }
  if(!RM){
    var CM={startup:'#F0855A',breakeven:'#FFE7A6',hourly:'#5FB6A6',pricing:'#B18BE4'};
    [].slice.call(root.querySelectorAll('.calc')).forEach(function(el){
      el.addEventListener('pointerenter',function(){ washTo(CM[el.id]||'#D4A856'); });
      el.addEventListener('pointerleave',washOff);
    });
    [].slice.call(root.querySelectorAll('.cjump')).forEach(function(el){
      el.addEventListener('pointerenter',function(){ washTo(el.getAttribute('data-c')||'#D4A856'); });
      el.addEventListener('pointerleave',washOff);
    });
  }

  var jumps=[].slice.call(root.querySelectorAll('.cjump'));
  jumps.forEach(function(b){
    b.addEventListener('click',function(){
      var t=document.getElementById(b.getAttribute('data-go')); if(!t) return;
      jumps.forEach(function(x){ x.setAttribute('aria-pressed', x===b ? 'true':'false'); });
      t.scrollIntoView({behavior:RM?'auto':'smooth',block:'start'});
      var f=t.querySelector('input'); if(f) f.focus({preventScroll:true});
    });
  });

  var all=[startup,breakeven,hourly,pricing];
  root.addEventListener('input',function(){ all.forEach(function(f){f();}); });
  all.forEach(function(f){f();});
  root.addEventListener('click',function(ev){
    var b=ev.target.closest && ev.target.closest('.ccopy'); if(!b) return;
    var txt=window['__'+b.getAttribute('data-k')]||''; if(!txt) return;
    var done=function(){ var o=b.textContent; b.textContent='Copied'; b.classList.add('ok');
      setTimeout(function(){ b.textContent=o; b.classList.remove('ok'); },1500); };
    if(navigator.clipboard&&navigator.clipboard.writeText){ navigator.clipboard.writeText(txt).then(done,function(){}); }
    else { var ta=document.createElement('textarea'); ta.value=txt; ta.style.position='absolute';
      ta.style.left='-9999px'; document.body.appendChild(ta); ta.select();
      try{ document.execCommand('copy'); done(); }catch(err){} document.body.removeChild(ta); }
  });
})();
"""

MAIN=f"""<main id="maincontent">
<section class="wrap res calcs">
  <p class="kx-backrow"><a class="kx-bk" href="resources.html">
    <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M15 5l-7 7 7 7"/></svg>
    Back to resources</a></p>
  <span class="eyebrow">Calculators</span>
  <h1>Four numbers worth knowing early.</h1>
  <p class="lede">Nothing to sign up for, nothing saved, nothing sent. Change a figure and the answer
  moves. Copy any result to paste into your own notes.</p>

  <div class="cjumps" role="group" aria-label="Jump to a calculator">
    <button type="button" class="cjump" data-go="startup" data-c="#F0855A">Startup cost</button>
    <button type="button" class="cjump" data-go="breakeven" data-c="#FFE7A6">Breakeven</button>
    <button type="button" class="cjump" data-go="hourly" data-c="#5FB6A6">Hourly rate</button>
    <button type="button" class="cjump" data-go="pricing" data-c="#B18BE4">Product pricing</button>
  </div>

  <div class="calc" id="startup">
    <div><h2>What will it cost to start?</h2>
    <p class="cdek">One-time setup costs, plus the running costs to cover before revenue arrives. The months figure is the cushion you are planning for.</p>
    {row("Registration, licenses and permits","s_reg","500")}
    {row("Equipment and hardware","s_equip","1200")}
    {row("Website and branding","s_web","800")}
    {row("Initial stock or materials","s_stock","0")}
    {row("Legal and accounting setup","s_pro","600")}
    {row("Rent or workspace","s_rent","0","$","per month")}
    {row("Software and subscriptions","s_tools","120","$","per month")}
    {row("Insurance","s_ins","60","$","per month")}
    {row("Marketing","s_mkt","200","$","per month")}
    {row("Everything else","s_other","150","$","per month")}
    {row("Months of runway to plan for","s_months","6","#","before revenue covers costs")}
    </div>
    {out("s","Total to get started",[("One-time setup","s_one"),("Monthly running costs","s_mo"),("Runway subtotal","s_run")],"s")}
  </div>

  <div class="calc" id="breakeven">
    <div><h2>When do you break even?</h2>
    <p class="cdek">The number of sales a month that covers your fixed costs. Contribution is what each
    sale leaves behind once the cost of delivering it is paid.</p>
    {row("Fixed costs","b_fixed","3000","$","per month, regardless of sales")}
    {row("Price per sale","b_price","150")}
    {row("Variable cost per sale","b_var","45","$","materials, fees, delivery")}
    </div>
    {out("b","Breakeven",[("Sales needed each month","b_units"),("Revenue at that point","b_rev"),("Contribution margin","b_margin")],"b")}
  </div>

  <div class="calc" id="hourly">
    <div><h2>What should you charge an hour?</h2>
    <p class="cdek">Billable hours are always fewer than working hours. Admin, sales and unpaid revisions
    all come out of the same week, which is why the percentage matters more than the total.</p>
    {row("Income you want to take home","h_income","70000","$","per year")}
    {row("Business costs","h_costs","9000","$","per year")}
    {row("Weeks you will work","h_weeks","46","#","allowing for time off")}
    {row("Hours a week","h_hours","30","#")}
    {row("Share of those hours you can bill","h_bill","60","%")}
    </div>
    {out("h","Your rate",[("Billable hours a year","h_bh"),("Day rate at 8 hours","h_day"),("Total to bill","h_need")],"h")}
  </div>

  <div class="calc" id="pricing">
    <div><h2>What should you price a product at?</h2>
    <p class="cdek">Works back from the margin you want rather than guessing a number. Payment fees are
    added on top so the margin survives the checkout.</p>
    {row("Materials per unit","p_mat","12")}
    {row("Labor per unit","p_lab","18")}
    {row("Overhead per unit","p_over","6")}
    {row("Target gross margin","p_margin","55","%")}
    {row("Payment processing fees","p_fee","3","%")}
    </div>
    {out("p","Suggested price",[("Cost per unit","p_unit"),("Profit per sale","p_profit"),("Margin after fees","p_net")],"p")}
  </div>

  <div class="chubs">
    <a class="chub" href="glossary.html"><b>Glossary</b><span>59 terms, plainly</span></a>
    <a class="chub" href="resources.html"><b>Resources</b><span>Everything, all of it</span></a>
    <a class="chub" href="join.html"><b>Early access</b><span>Join the list</span></a>
  </div>

  <div class="cfaq">
    <h2>Frequently asked questions</h2>
    {"".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q,a in faqs)}
  </div>
</section>
</main>"""

out_html=page("tools.html",
  "Free Business Calculators: Startup Cost, Breakeven | SideKix",
  DESC, MAIN, extra_css=CSS, extra_js=JS, schema=(schema,faqschema,crumbs))
open("/home/claude/site/tools.html","w",encoding="utf-8").write(out_html)
print("tools.html rebuilt on the site theme:",len(out_html)//1024,"KB")
