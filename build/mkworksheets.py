import io, os, sys, json, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from toolgen import page, crumbs, webapp, faqpage, SITE
from wsparse import parse

WS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "worksheets")
def e(s): return html.escape(str(s), quote=True)

CSS = """
/* ---- fillable worksheets ----
   The paper versions in assets/worksheets are the source. Every prompt, every
   section and every blank here comes from those files, so the page and the
   printout say the same thing in the same order. What the page adds is that
   the blanks accept typing, the boxes remember being ticked, and the whole
   thing comes back when you return. */
.ws{max-width:820px;margin:0 auto}
.ws-bar{position:sticky;top:64px;z-index:20;display:flex;flex-wrap:wrap;gap:10px;
  align-items:center;justify-content:space-between;
  padding:14px 18px;margin:0 0 26px;border-radius:14px;
  border:1px solid rgba(212,168,86,.28);
  background:rgba(10,10,10,.92);-webkit-backdrop-filter:blur(6px);backdrop-filter:blur(6px)}
.ws-status{font-family:var(--util);font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:#9C968D}
.ws-status b{color:var(--gold);font-weight:600}
.ws-acts{display:flex;gap:8px;flex-wrap:wrap}
.ws-btn{font-family:var(--util);font-size:10.5px;letter-spacing:.16em;text-transform:uppercase;
  padding:10px 16px;min-height:40px;border-radius:999px;cursor:pointer;
  border:1px solid rgba(212,168,86,.45);background:none;color:var(--gold);
  transition:background .25s,border-color .25s,color .25s}
.ws-btn:hover{background:var(--gold);border-color:var(--gold);color:#1B1400}
.ws-btn:focus-visible{outline:3px solid #F3E4A8;outline-offset:3px}
.ws-btn.ws-danger{border-color:rgba(255,120,110,.4);color:#FF8A80}
.ws-btn.ws-danger:hover{background:#8F4E4C;border-color:#8F4E4C;color:#fff}
.ws-meter{flex:1 1 160px;height:5px;border-radius:99px;background:rgba(212,168,86,.16);overflow:hidden;min-width:120px}
.ws-meter i{display:block;height:100%;width:0;border-radius:99px;
  background:linear-gradient(90deg,#A1853E,#F3E4A8);transition:width .45s cubic-bezier(.16,1,.3,1)}
.ws-sec{margin:0 0 40px}
.ws-sec > h2{font-family:var(--util);font-size:11px;letter-spacing:.2em;text-transform:uppercase;
  color:var(--gold);margin:0 0 6px;padding-bottom:10px;border-bottom:1px solid rgba(212,168,86,.22)}
.ws-hint{color:#9C968D;font-size:14.5px;margin:12px 0 6px;font-style:italic}
.ws-note{color:#CEC9BC;font-size:15px;margin:12px 0 6px}
.ws-f{margin:18px 0 0}
.ws-f > label{display:block;font-size:15px;color:#E8DEC4;margin:0 0 8px}
.ws-f textarea{width:100%;box-sizing:border-box;resize:vertical;
  font-family:var(--body);font-size:15.5px;line-height:1.75;color:#F1ECE2;
  background:rgba(255,255,255,.03);border:1px solid rgba(212,168,86,.22);
  border-radius:10px;padding:12px 14px}
.ws-f textarea:focus{outline:none;border-color:var(--gold);background:rgba(255,255,255,.05)}
.ws-check{display:flex;align-items:flex-start;gap:12px;padding:11px 0;
  border-bottom:1px solid rgba(255,255,255,.05);cursor:pointer}
.ws-check:last-child{border-bottom:none}
.ws-check input{flex:none;width:20px;height:20px;margin:2px 0 0;accent-color:#D4A856;cursor:pointer}
.ws-check span{font-size:15.5px;line-height:1.6;color:#CEC9BC;transition:color .25s}
.ws-check input:checked + span{color:#8E8A82;text-decoration:line-through;
  text-decoration-color:rgba(212,168,86,.5)}
.ws-table{width:100%;border-collapse:collapse;margin:16px 0 0;font-size:15px}
.ws-table th{text-align:left;font-family:var(--util);font-size:10px;letter-spacing:.16em;
  text-transform:uppercase;color:var(--gold);font-weight:400;padding:0 8px 8px 0}
.ws-table td{padding:0 8px 8px 0;vertical-align:top}
.ws-table input{width:100%;box-sizing:border-box;font-family:var(--body);font-size:15px;
  color:#F1ECE2;background:rgba(255,255,255,.03);border:1px solid rgba(212,168,86,.22);
  border-radius:8px;padding:10px 12px;min-height:44px}
.ws-table input:focus{outline:none;border-color:var(--gold);background:rgba(255,255,255,.05)}
.ws-tw{overflow-x:auto}
@media(max-width:640px){
  .ws-bar{position:static;top:auto}
  .ws-table,.ws-table tbody,.ws-table tr,.ws-table td{display:block;width:100%}
  .ws-table thead{display:none}
  .ws-table tr{margin:0 0 14px;padding:0 0 10px;border-bottom:1px solid rgba(255,255,255,.06)}
  .ws-table td::before{content:attr(data-c);display:block;font-family:var(--util);font-size:10px;
    letter-spacing:.16em;text-transform:uppercase;color:var(--gold);margin:0 0 6px}
}
@media print{
  #kx-nav,.kx-nav,#kx-orbnav,#kx-orbcue,.sk-footer,.ws-bar,.kx-backrow,
  #kx-cursor,#kx-ring,#kx-desat,#kx-progress,.hubdiscs{display:none !important}
  html,body{background:#fff !important;color:#000 !important}
  .ws-f textarea,.ws-table input{border:1px solid #999 !important;background:#fff !important;color:#000 !important}
  .ws-sec > h2{color:#000 !important;border-bottom-color:#999 !important}
  .ws-check span,.ws-f > label,.ws-hint,.ws-note{color:#000 !important}
  h1,.lede{color:#000 !important}
  .ws-sec{break-inside:avoid}
}
"""

JS = r"""
(function(){
  var root=document.querySelector('.ws'); if(!root) return;
  var KEY='sk:ws:'+location.pathname.replace(/^.*\//,'');
  var fields=[].slice.call(root.querySelectorAll('[data-f]'));
  var boxes=fields.filter(function(el){return el.type==='checkbox';});

  /* localStorage is per browser and can throw outright in a private window or
     with site data blocked, so every read and write is guarded and the page
     works exactly the same when it fails: you just do not get the saving. */
  function load(){
    var raw=null; try{ raw=localStorage.getItem(KEY); }catch(err){ return false; }
    if(!raw) return false;
    var data; try{ data=JSON.parse(raw); }catch(err){ return false; }
    fields.forEach(function(el){
      var v=data[el.getAttribute('data-f')];
      if(v===undefined) return;
      if(el.type==='checkbox') el.checked=!!v; else el.value=v;
    });
    return !!data.__t;
  }
  var saveTimer=null;
  function save(){
    clearTimeout(saveTimer);
    saveTimer=setTimeout(function(){
      var data={__t:Date.now()};
      fields.forEach(function(el){
        data[el.getAttribute('data-f')] = el.type==='checkbox' ? el.checked : el.value;
      });
      try{ localStorage.setItem(KEY, JSON.stringify(data)); }catch(err){}
      paint();
    }, 400);
  }
  function grow(el){ if(el.tagName==='TEXTAREA'){ el.style.height='auto'; el.style.height=(el.scrollHeight+2)+'px'; } }

  var meter=root.querySelector('.ws-meter i'), status=root.querySelector('.ws-status');
  function paint(){
    if(boxes.length){
      var done=boxes.filter(function(b){return b.checked;}).length;
      if(meter) meter.style.width=(done/boxes.length*100)+'%';
      if(status) status.innerHTML='<b>'+done+'</b> of '+boxes.length+' done';
    } else if(status){
      var filled=fields.filter(function(f){return (f.value||'').trim();}).length;
      status.innerHTML= filled ? '<b>'+filled+'</b> of '+fields.length+' filled, saved in this browser'
                               : 'Nothing saved yet. Everything stays in this browser.';
    }
  }

  fields.forEach(function(el){
    el.addEventListener('input',function(){ grow(el); save(); });
    el.addEventListener('change',save);
  });
  load(); fields.forEach(grow); paint();

  var pr=root.querySelector('[data-ws="print"]');
  if(pr) pr.addEventListener('click',function(){ window.print(); });

  var dl=root.querySelector('[data-ws="download"]');
  if(dl) dl.addEventListener('click',function(){
    var out=[], t=document.querySelector('h1');
    out.push((t?t.textContent:document.title).toUpperCase());
    out.push(''); out.push('SideKix  |  sidekixhq.com');
    out.push(new Date().toLocaleDateString());
    out.push('='.repeat(58)); out.push('');
    [].slice.call(root.querySelectorAll('.ws-sec')).forEach(function(sec){
      var h=sec.querySelector('h2');
      if(h) out.push('-- '+h.textContent.trim()+' '+'-'.repeat(Math.max(3,52-h.textContent.length)));
      out.push('');
      [].slice.call(sec.querySelectorAll('[data-f]')).forEach(function(el){
        if(el.type==='checkbox'){
          out.push('['+(el.checked?'x':' ')+'] '+(el.closest('.ws-check').querySelector('span')||{textContent:''}).textContent.trim());
        } else {
          var lab=el.getAttribute('data-label')||'';
          var v=(el.value||'').trim();
          if(lab) out.push(lab);
          out.push(v||'__________________________________________________________');
          out.push('');
        }
      });
      out.push('');
    });
    out.push('='.repeat(58));
    out.push('SideKix  |  Talent is everywhere. Opportunity is for all.');
    out.push('sidekixhq.com');
    var blob=new Blob([out.join('\n')],{type:'text/plain;charset=utf-8'});
    var a=document.createElement('a');
    a.href=URL.createObjectURL(blob);
    a.download=location.pathname.replace(/^.*\//,'').replace('.html','')+'.txt';
    document.body.appendChild(a); a.click(); document.body.removeChild(a);
    setTimeout(function(){ URL.revokeObjectURL(a.href); },1000);
  });

  var cl=root.querySelector('[data-ws="clear"]');
  if(cl) cl.addEventListener('click',function(){
    if(!confirm('Clear everything on this worksheet? This cannot be undone.')) return;
    fields.forEach(function(el){ if(el.type==='checkbox') el.checked=false; else el.value=''; });
    try{ localStorage.removeItem(KEY); }catch(err){}
    fields.forEach(grow); paint();
  });
})();
"""

def render(doc, has_checks):
    o = ['<div class="ws">']
    o.append('<div class="ws-bar">')
    if has_checks:
        o.append('<span class="ws-meter"><i></i></span>')
    o.append('<span class="ws-status" aria-live="polite"></span>')
    o.append('<span class="ws-acts">'
             '<button class="ws-btn" data-ws="print" type="button">Print</button>'
             '<button class="ws-btn" data-ws="download" type="button">Download</button>'
             '<button class="ws-btn ws-danger" data-ws="clear" type="button">Clear</button>'
             '</span></div>')
    n = 0
    for si, sec in enumerate(doc["sections"]):
        o.append('<section class="ws-sec">')
        if sec["name"]:
            o.append('<h2>%s</h2>' % e(sec["name"].title()))
        for it in sec["items"]:
            if it["t"] == "hint":
                o.append('<p class="ws-hint">%s</p>' % e(it["text"]))
            elif it["t"] == "note":
                o.append('<p class="ws-note">%s</p>' % e(it["text"]))
            elif it["t"] == "check":
                n += 1
                o.append('<label class="ws-check"><input data-f="c%d" type="checkbox"/>'
                         '<span>%s</span></label>' % (n, e(it["text"])))
            elif it["t"] == "write":
                n += 1
                lab = it.get("label", "")
                o.append('<div class="ws-f">')
                if lab:
                    o.append('<label for="f%d">%s</label>' % (n, e(lab)))
                o.append('<textarea data-f="f%d" data-label="%s" id="f%d" rows="%d"%s></textarea>'
                         % (n, e(lab), n, max(2, it["lines"]),
                            '' if lab else ' aria-label="%s"' % e(sec["name"].title() or "Notes")))
                o.append('</div>')
            elif it["t"] == "table":
                cols = it["cols"]
                o.append('<div class="ws-tw"><table class="ws-table"><thead><tr>')
                for c in cols:
                    o.append('<th scope="col">%s</th>' % e(c))
                o.append('</tr></thead><tbody>')
                for r in range(it["rows"]):
                    o.append('<tr>')
                    for c in cols:
                        n += 1
                        o.append('<td data-c="%s"><input aria-label="%s, row %d" data-f="f%d" '
                                 'data-label="%s" type="text"/></td>' % (e(c), e(c), r + 1, n, e(c)))
                    o.append('</tr>')
                o.append('</tbody></table></div>')
        o.append('</section>')
    o.append('</div>')
    return "\n".join(o)

SHEETS = [
 dict(src="weekly-business-check-in-template", file="weekly-check-in.html",
      title="Weekly Business Check-In: Fillable Worksheet | SideKix",
      name="Weekly Business Check-In",
      eyebrow="Weekly check-in",
      h1="Fifteen minutes, <em>same time every week</em>.",
      lede="The check-in that keeps a week from disappearing. Fill it in here and it stays in your browser, so next week you open it and last week is still there. Print it or download it whenever you want it on paper.",
      desc="A fillable weekly business check-in. Wins, key numbers, progress, what got in the way and next week's top three. Saves in your browser, prints, downloads.",
      feats=["Fillable in the browser","Saved between visits","Printable","Downloads as a text file"],
      faqs=[("Where is my worksheet saved?","In your own browser, on the device you filled it in on. Nothing is sent anywhere and nobody else can see it, which also means it will not follow you to another device."),
            ("How long should a weekly check-in take?","Fifteen minutes is the point. It is short enough to actually happen every week, which matters far more than doing a thorough one occasionally.")]),
 dict(src="90-day-goal-setting-template-small-business", file="90-day-goals.html",
      title="90-Day Goals: Fillable Worksheet | SideKix",
      name="90-Day Goal-Setting Worksheet",
      eyebrow="90-day goals",
      h1="Reflect, then pick <em>three things</em>.",
      lede="Ninety days is long enough to finish something and short enough to stay honest. Reflect on the last quarter, set the vision, choose three priorities, and build the weekly rhythm that gets you there.",
      desc="A fillable 90-day goal-setting worksheet. Reflect, set a vision, pick three priorities and build the weekly rhythm. Saves in your browser, prints, downloads.",
      feats=["Fillable in the browser","Saved between visits","Printable","Downloads as a text file"],
      faqs=[("Why three priorities and not ten?","Because ten priorities is none. Three is the number most people can hold and still finish inside a quarter, and each one here needs a definition of done so you can tell whether it happened."),
            ("Where is my worksheet saved?","In your own browser, on the device you filled it in on. Nothing is sent anywhere.")]),
 dict(src="business-startup-checklist", file="startup-checklist.html",
      title="Business Startup Checklist: Tick and Track | SideKix",
      name="Business Startup Checklist",
      eyebrow="Startup checklist",
      h1="Five phases, ordered by <em>risk</em>.",
      lede="Not by paperwork. Each phase exists to stop you spending time or money on the next one before you should, and each has an exit condition. Tick as you go and the page remembers where you got to.",
      desc="An interactive business startup checklist in five phases ordered by risk: decide, validate, set up, build, sell. Remembers your progress in your browser.",
      feats=["Progress remembered between visits","Five phases with exit conditions","Printable","Downloads as a text file"],
      faqs=[("What order should I start a business in?","Risk order rather than paperwork order. Decide whether it is the right thing to build, find out whether anyone wants it, and only then spend money making it legal and real. This checklist is arranged that way."),
            ("Is my progress saved?","Yes, in your own browser on this device. Nothing is sent anywhere and no account is involved.")]),
 dict(src="support-system-checklist-entrepreneur", file="support-system-checklist.html",
      title="Support System Checklist for Founders | SideKix",
      name="Support System Checklist",
      eyebrow="Support system",
      h1="Who is <em>actually</em> in your corner?",
      lede="Five kinds of support, fifteen honest questions. Tick what you have, see what is missing, then write one step to close each gap. Your answers stay in this browser.",
      desc="An interactive support system checklist for founders: personal, peer, expertise, resource and community support, with a gap plan. Saves in your browser.",
      feats=["Progress remembered between visits","Five kinds of support","Gap action plan","Printable"],
      faqs=[("Why does a support system matter to a business?","Working alone is the most common reason people stop, and it rarely announces itself as the reason. Naming who covers each kind of support makes the gaps visible while they are still easy to close."),
            ("Is my progress saved?","Yes, in your own browser on this device. Nothing is sent anywhere.")]),
]

for sh in SHEETS:
    doc = parse(os.path.join(WS, sh["src"] + ".txt"))
    has_checks = any(it["t"] == "check" for s in doc["sections"] for it in s["items"])
    body = render(doc, has_checks)
    sch = (webapp(sh["name"], sh["file"], sh["desc"], sh["feats"]),
           faqpage(sh["faqs"]), crumbs(sh["name"], sh["file"]))
    n = page(sh["file"], sh["title"], sh["desc"], sh["eyebrow"], sh["h1"], sh["lede"],
             body, css=CSS, js=JS, schema=sch)
    nf = body.count('data-f=')
    print("%-32s %6.0f KB  %2d sections  %3d fields  checks=%s"
          % (sh["file"], n/1024, len(doc["sections"]), nf, has_checks))
