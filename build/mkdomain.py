import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from toolgen import page, crumbs, webapp, faqpage

DESC = ("Check a business name across a dozen domain endings at once. Runs against the "
        "registries themselves through RDAP, so the answer is the register's answer. "
        "No account and nothing stored.")

CSS = """
/* ---- domain search ----
   The lookup goes to rdap.org, which is the IANA bootstrap service in front of
   each registry's own RDAP server. A 404 means no registration record exists,
   which is as close to "available" as anything outside a registrar's checkout
   can tell you. A 200 means there is a record, so it is taken. Anything else is
   reported as unknown rather than guessed at, because a timeout is not an
   answer.

   Registries answer at very different speeds. In testing .io came back in 2ms
   and .app took 16.5 seconds, so every lookup runs in parallel with its own
   abort timer rather than in sequence behind the slowest one. */
.dm{max-width:820px;margin:0 auto}
.dm-form{display:flex;flex-wrap:wrap;gap:12px;margin:0 0 12px}
.dm-form input{flex:1 1 280px;min-height:56px;padding:0 18px;border-radius:14px;
  font-family:var(--body);font-size:17px;color:#F1ECE2;
  background:rgba(255,255,255,.04);border:1px solid rgba(212,168,86,.4)}
.dm-form input:focus{outline:none;border-color:var(--gold);background:rgba(255,255,255,.06)}
.dm-form button{min-height:56px;padding:0 30px;border-radius:999px;border:none;cursor:pointer;
  font-family:'Poppins',system-ui,sans-serif;font-size:16px;font-weight:700;color:#1B1400;
  background:linear-gradient(180deg,#D7C582,#A1853E);box-shadow:0 10px 34px rgba(231,182,70,.28)}
.dm-form button:disabled{opacity:.5;cursor:default;box-shadow:none}
.dm-note{font-family:var(--util);font-size:10.5px;letter-spacing:.14em;text-transform:uppercase;
  color:#7E7A73;margin:0 0 28px}
.dm-list{display:grid;gap:2px;margin:0}
.dm-r{display:flex;align-items:center;gap:14px;padding:15px 4px;
  border-top:1px solid rgba(255,255,255,.07)}
.dm-n{flex:1 1 auto;min-width:0;font-family:var(--body);font-size:16.5px;color:#E8DEC4;
  overflow-wrap:anywhere}
.dm-s{flex:none;font-family:var(--util);font-size:10px;letter-spacing:.16em;text-transform:uppercase;
  padding:6px 12px;border-radius:99px;border:1px solid transparent}
.dm-s.free{color:#A6E0B4;border-color:rgba(166,224,180,.4);background:rgba(166,224,180,.08)}
.dm-s.taken{color:#9C968D;border-color:rgba(255,255,255,.12)}
.dm-s.wait{color:var(--gold);border-color:rgba(212,168,86,.3)}
.dm-s.err{color:#E4BFA0;border-color:rgba(255,150,90,.3)}
.dm-go{flex:none;font-family:var(--util);font-size:10px;letter-spacing:.16em;text-transform:uppercase;
  color:var(--gold);text-decoration:none;border-bottom:1px solid rgba(212,168,86,.35);padding-bottom:2px}
.dm-go:hover{color:#F3E4A8}
.dm-empty{color:#9C968D;font-size:15.5px;margin:26px 0 0}
.dm-caveat{border:1px solid rgba(212,168,86,.22);border-radius:12px;padding:16px 18px;
  margin:30px 0 0;font-size:14.5px;line-height:1.7;color:#9C968D}
.dm-caveat b{color:#E8DEC4;font-weight:600}
@media(max-width:560px){
  .dm-r{flex-wrap:wrap;gap:8px}
  .dm-n{flex:1 1 100%}
}
"""

JS = r"""
(function(){
  var form=document.getElementById('dm-form'), input=document.getElementById('dm-q'),
      list=document.getElementById('dm-list'), btn=document.getElementById('dm-go');
  if(!form) return;
  var TLDS=['com','co','io','net','org','app','xyz','biz','us','dev','ai','shop'];

  function slug(s){
    return String(s||'').toLowerCase().normalize('NFKD')
      .replace(/[^a-z0-9\s-]/g,'').trim().replace(/\s+/g,'-').replace(/-+/g,'-')
      .replace(/^-|-$/g,'');
  }
  function esc(s){ return String(s).replace(/[&<>"]/g,function(c){
    return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]; }); }

  /* One lookup, with its own timeout. rdap.org answers 404 when no registration
     record exists and 200 when one does. Anything else is not an answer, so it
     is reported as such. */
  function check(domain, ms){
    var ctl = ('AbortController' in window) ? new AbortController() : null;
    var timer = setTimeout(function(){ if(ctl) ctl.abort(); }, ms||9000);
    return fetch('https://rdap.org/domain/'+encodeURIComponent(domain),
                 ctl ? {signal:ctl.signal} : {})
      .then(function(r){
        clearTimeout(timer);
        if(r.status===404) return 'free';
        if(r.status===200) return 'taken';
        return 'unknown';
      })
      .catch(function(){ clearTimeout(timer); return 'unknown'; });
  }

  function render(name){
    list.innerHTML='';
    TLDS.forEach(function(t){
      var d=name+'.'+t;
      var row=document.createElement('div');
      row.className='dm-r';
      row.innerHTML='<span class="dm-n">'+esc(d)+'</span>'
                   +'<span class="dm-s wait" data-s>Checking</span>';
      list.appendChild(row);
      check(d).then(function(state){
        var s=row.querySelector('[data-s]');
        if(state==='free'){
          s.className='dm-s free'; s.textContent='No record';
          var a=document.createElement('a');
          a.className='dm-go'; a.target='_blank'; a.rel='noopener nofollow';
          a.href='https://www.namecheap.com/domains/registration/results/?domain='+encodeURIComponent(d);
          a.textContent='Register';
          row.appendChild(a);
        } else if(state==='taken'){
          s.className='dm-s taken'; s.textContent='Registered';
        } else {
          s.className='dm-s err'; s.textContent='No answer';
        }
      });
    });
  }

  form.addEventListener('submit',function(ev){
    ev.preventDefault();
    var name=slug(input.value);
    if(!name){ list.innerHTML='<p class="dm-empty">Type a name to check.</p>'; return; }
    btn.disabled=true;
    render(name);
    setTimeout(function(){ btn.disabled=false; }, 900);
  });
})();
"""

body = ('<div class="dm">'
        '<form class="dm-form" id="dm-form">'
        '<input aria-label="Business name to check" autocapitalize="none" autocomplete="off" '
        'autocorrect="off" id="dm-q" placeholder="your business name" spellcheck="false" type="text"/>'
        '<button id="dm-go" type="submit">Check</button>'
        '</form>'
        '<p class="dm-note">Twelve endings, checked at the same time. Nothing is stored.</p>'
        '<div class="dm-list" id="dm-list"></div>'
        '<p class="dm-caveat"><b>What this can and cannot tell you.</b> It asks each registry '
        'whether a registration record exists. No record is a good sign and not a promise: a name '
        'can be reserved, held back by the registry, premium priced, or taken between this check '
        'and your checkout. A registered domain also says nothing about whether the trademark is '
        'free. Anything that does not answer in time is marked so, rather than counted as '
        'available.</p>'
        '</div>')

faqs = [
 ("How do I check whether a domain name is available?",
  "This page asks the domain registries directly through RDAP, the protocol that replaced WHOIS, and reports whether a registration record exists for each ending. No record means nobody has registered it. A registrar's checkout is still the only place that can hold a name for you."),
 ("Does an available domain mean the business name is free to use?",
  "No. Domain registration and trademark are separate things. A name can be free as a domain and already owned as a mark in your industry, or registered as a domain by somebody with no claim to the name at all. Checking the trademark register is a separate step."),
 ("Why do some endings take longer to answer?",
  "Each ending is run by a different registry and they answer at very different speeds. In testing one came back in two milliseconds and another took over sixteen seconds. Every ending here is checked at the same time rather than in a queue, so a slow one does not hold up the rest."),
]

sch = (webapp("Business Name and Domain Checker", "domain-search.html", DESC,
              ["Twelve endings at once","Live registry lookup over RDAP","No account","Nothing stored"]),
       faqpage(faqs), crumbs("Domain search", "domain-search.html"))

n = page("domain-search.html",
         "Business Name Domain Checker: 12 Endings at Once | SideKix",
         DESC, "Domain search",
         "Is the name <em>actually free</em>?",
         "Type a business name and this checks a dozen domain endings at the same time, against the registries themselves rather than a reseller's list. No account, nothing stored, and no upsell.",
         body, css=CSS, js=JS, schema=sch)
print("domain-search.html %.0f KB" % (n/1024))
