import io, os, sys, json, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from toolgen import page, crumbs, webapp, faqpage, SITE

HERE = os.path.dirname(os.path.abspath(__file__))
data = json.load(open(os.path.join(HERE, "state-filings.json")))
states = data["states"]

# Trimmed for the page: the full record with its whole source list stays in the
# repository, but the page carries two sources per state rather than six.
slim = {}
for k, v in states.items():
    r = dict(v)
    r["sources"] = (v.get("sources") or [])[:2]
    slim[k] = r

DESC = ("What you file to start an LLC in any US state: the office, the form, the fee, the name search and the annual report. Every figure linked to its source.")

CSS = """
/* ---- state filing lookup ----
   Every value on this page was read from a state government source, and every
   value links back to the page it came from. Where a figure could not be
   confirmed the page says so rather than showing a number, because a wrong
   filing fee is worse than a missing one. */
.sf{max-width:880px;margin:0 auto}
.sf-pick{display:flex;flex-wrap:wrap;gap:12px;align-items:center;margin:0 0 30px}
.sf-pick label{font-family:var(--util);font-size:11px;letter-spacing:.16em;
  text-transform:uppercase;color:#9C968D}
.sf-pick select{flex:1 1 260px;min-height:52px;padding:0 16px;border-radius:12px;
  font-family:var(--body);font-size:16.5px;color:#F1ECE2;
  background:rgba(255,255,255,.04);border:1px solid rgba(212,168,86,.4);cursor:pointer}
.sf-pick select:focus{outline:none;border-color:var(--gold)}
.sf-card{border:1px solid rgba(212,168,86,.24);border-radius:18px;padding:30px 28px;
  background:radial-gradient(120% 120% at 50% 0,rgba(33,26,10,.55),rgba(12,11,8,.75))}
.sf-card h2{font-family:var(--display);font-size:clamp(26px,3.4vw,36px);color:#FFF8E8;
  margin:0 0 4px;line-height:1.1}
.sf-agency{font-size:15px;color:#9C968D;margin:0 0 24px}
.sf-agency a{color:var(--gold);text-decoration:none;border-bottom:1px solid rgba(212,168,86,.35)}
.sf-agency a:hover{color:#F3E4A8}
.sf-rows{display:grid;gap:2px;margin:0}
.sf-row{display:grid;grid-template-columns:minmax(140px,180px) minmax(0,1fr);gap:16px;
  padding:16px 0;border-top:1px solid rgba(255,255,255,.07)}
.sf-row dt{font-family:var(--util);font-size:10.5px;letter-spacing:.16em;text-transform:uppercase;
  color:var(--gold);margin:3px 0 0}
.sf-row dd{margin:0;font-size:15.5px;line-height:1.7;color:#CEC9BC}
.sf-row dd b{color:#F1ECE2;font-weight:600}
.sf-row dd a{color:#EBD08C;text-decoration:none;border-bottom:1px solid rgba(212,168,86,.3)}
.sf-row dd a:hover{color:#FFF6DC;border-bottom-color:var(--gold)}
.sf-fee{font-family:var(--display);font-size:30px;color:#FFF8E8;line-height:1}
.sf-none{color:#9C968D;font-style:italic}
.sf-tag{display:inline-block;font-family:var(--util);font-size:9.5px;letter-spacing:.16em;
  text-transform:uppercase;padding:4px 10px;border-radius:99px;margin-left:8px;
  border:1px solid rgba(212,168,86,.4);color:var(--gold)}
.sf-checked{font-family:var(--util);font-size:10px;letter-spacing:.14em;text-transform:uppercase;
  color:#7E7A73;margin:24px 0 0;padding-top:16px;border-top:1px solid rgba(255,255,255,.07)}
.sf-checked a{color:#9C968D}
.sf-warn{border:1px solid rgba(255,150,90,.3);background:rgba(255,140,80,.06);
  border-radius:12px;padding:14px 16px;margin:20px 0 0;font-size:14.5px;color:#E4BFA0}
@media(max-width:640px){
  .sf-row{grid-template-columns:1fr;gap:4px}
  .sf-card{padding:24px 18px}
}
"""

JS = """
(function(){
  var DATA=JSON.parse(document.getElementById('sf-data').textContent);
  var sel=document.getElementById('sf-state'), card=document.getElementById('sf-card');
  if(!sel||!card) return;
  function esc(s){ return String(s==null?'':s).replace(/[&<>"]/g,function(c){
    return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]; }); }
  function money(n){ return n==null ? null : '$'+Number(n).toLocaleString('en-US',{maximumFractionDigits:2}); }
  function link(url,text){ return url ? '<a href="'+esc(url)+'" rel="noopener nofollow" target="_blank">'+esc(text)+'</a>' : esc(text); }
  function row(k,v){ return '<div class="sf-row"><dt>'+k+'</dt><dd>'+v+'</dd></div>'; }
  var UNKNOWN='<span class="sf-none">Not confirmed from an official source. Check the agency page.</span>';

  function paint(name){
    var d=DATA[name]; if(!d){ card.innerHTML=''; return; }
    var ar=d.annual_report||{};
    var h='<h2>'+esc(name)+'</h2>';
    h+='<p class="sf-agency">'+link(d.agency_url,d.agency||'')+'</p>';
    h+='<dl class="sf-rows">';
    h+=row('What you file', d.llc_filing_name ? link(d.llc_filing_url,d.llc_filing_name) : UNKNOWN);
    h+=row('Filing fee', d.llc_fee_usd!=null
        ? '<span class="sf-fee">'+money(d.llc_fee_usd)+'</span>' : UNKNOWN);
    h+=row('Name search', d.name_search_url ? link(d.name_search_url,'Check a name in '+name) : UNKNOWN);
    var ra = d.registered_agent_required===true ? '<b>Required.</b> '
           : d.registered_agent_required===false ? '<b>Not required in the usual form.</b> ' : '';
    h+=row('Registered agent', ra + esc(d.registered_agent_note||''));
    if(ar.required===false){
      h+=row('Annual report','<b>None.</b> '+esc(ar.due||'This state does not ask an LLC for a periodic report.'));
    } else {
      var cad = ar.cadence ? '<span class="sf-tag">'+esc(ar.cadence)+'</span>' : '';
      var fee = ar.fee_usd!=null ? ' Fee '+money(ar.fee_usd)+'.' : '';
      h+=row('Annual report','<b>'+esc(ar.name||'Annual report')+'</b>'+cad+'<br>'+esc(ar.due||'')+fee
             +(ar.url?'<br>'+link(ar.url,'Filing page'):''));
    }
    h+='</dl>';
    if(d.llc_fee_usd==null||!d.llc_filing_name){
      h+='<p class="sf-warn">Something on this state could not be confirmed from a government source in the last check, '
       + 'so it is left blank rather than guessed. The agency link above is the place to confirm it.</p>';
    }
    h+='<p class="sf-checked">Checked '+esc(d.checked||'')
      +(d.sources&&d.sources.length?' &middot; Sources: '+d.sources.map(function(u,i){
          return '<a href="'+esc(u)+'" rel="noopener nofollow" target="_blank">'+(i+1)+'</a>'; }).join(' '):'')
      +'</p>';
    card.innerHTML=h;
    try{ history.replaceState(null,'','?state='+encodeURIComponent(name)); }catch(err){}
  }
  sel.addEventListener('change',function(){ paint(sel.value); });
  var qs=(location.search.match(/[?&]state=([^&]*)/)||[])[1];
  var start = qs ? decodeURIComponent(qs.replace(/\\+/g,' ')) : '';
  if(!DATA[start]) start='North Carolina';
  sel.value=start; paint(start);
})();
"""

opts = "".join('<option value="%s">%s</option>' % (html.escape(k, True), html.escape(k))
               for k in sorted(slim))
SF_MORE_CSS = """
.sf-more{margin:26px 0 0;font-size:15px;line-height:1.7;color:#BDB4A4}
.sf-more a{color:#F3E4A8;text-decoration:underline;text-underline-offset:3px}
.sf-more a:hover{color:#FFF6DC}
"""

body = ('<div class="sf">'
        '<div class="sf-pick"><label for="sf-state">Pick a state</label>'
        '<select id="sf-state">' + opts + '</select></div>'
        '<div class="sf-card" id="sf-card"></div>'
        '<script id="sf-data" type="application/json">'
        + json.dumps(slim, ensure_ascii=False).replace("</", "<\\/") +
        '</script>'
        # One state has a full walkthrough rather than a card. Linked here so
        # it is reachable from the page people land on looking for it.
        '<p class="sf-more">North Carolina has a longer version with the order '
        'to do things in, what each step costs and the official pages: '
        '<a href="start-a-business-in-north-carolina.html">starting a business '
        'in North Carolina</a>.</p>'
        '</div>')

nofee = sorted(k for k, v in slim.items() if v.get("llc_fee_usd") is None)
faqs = [
 ("What do I need to file to start an LLC?",
  "In every state it is one formation document filed with the office that keeps the business register, usually the Secretary of State. The document has different names in different places: Articles of Organization in most, Certificate of Formation or Certificate of Organization elsewhere. This page gives the name, the fee and a link to the filing page for whichever state you pick."),
 ("How much does it cost to form an LLC?",
  "It ranges widely between states, and the formation fee is rarely the whole cost, because most states also charge for a periodic report. Both figures are on this page for each state, taken from that state's own published schedule."),
 ("Do I need a registered agent?",
  "Almost everywhere, yes, though the rules differ: some states require the agent to live in the state, some allow the company to act for itself, and a couple record a registered office instead of an agent. The rule for each state is on this page."),
 ("How current are these figures?",
  "Each state's record carries the date it was checked and a link to the government page it was read from. Fees and deadlines change, so the source link is the thing to trust at the moment you file, not the number on this page."),
]

sch = (webapp("State Filing Lookup", "state-filing.html", DESC,
              ["All 50 states","Formation document and fee","Name search link",
               "Registered agent rule","Annual report cadence, deadline and fee"]),
       faqpage(faqs), crumbs("State filing lookup", "state-filing.html"))

n = page("state-filing.html",
         "What Do I File in My State? LLC Lookup for All 50 | SideKix",
         DESC, "State filing",
         "What do you file <em>in your state</em>?",
         "Pick a state and see the office, the document, the fee, the name search, the registered agent rule and the annual report. Every figure came from that state's own pages and links back to them, because these change and the source is the only thing worth trusting on the day you file.",
         body, css=CSS + SF_MORE_CSS, js=JS, schema=sch)
print("state-filing.html %.0f KB, %d states, %d without a confirmed fee: %s"
      % (n/1024, len(slim), len(nofee), ", ".join(nofee)))
