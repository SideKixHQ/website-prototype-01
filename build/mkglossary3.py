import os
import sys, json, html, collections; sys.path.insert(0,'/home/claude/build')
from terms import TERMS, CATS
from shell import page



COL={"Legal":"#6FB0E0","Money":"#A6E0B4","Funding":"#FFE7A6","Metrics":"#B18BE4",
     "Planning":"#5FB6A6","Marketing":"#F2933F","Sales":"#F0855A","Operations":"#84D0C6"}
T=sorted(TERMS,key=lambda t:t[0].lower())
used=[c for c in CATS if any(x[1]==c for x in T)]
SITE="https://sidekixhq.com"
DESC=(f"A plain-language glossary of {len(T)} business terms for people starting something: "
      "LLC, EIN, runway, margin, MRR, cap table and more. Copy any definition.")
def e(s): return html.escape(s,quote=True)

# group alphabetically, the way a glossary actually reads
groups=collections.OrderedDict()
for term,cat,d in T: groups.setdefault(term[0].upper(),[]).append((term,cat,d))
letters=list(groups.keys())

secs=[]
for L,items in groups.items():
    rows=[]
    for term,cat,d in items:
        tid="t-"+"".join(ch.lower() if ch.isalnum() else "-" for ch in term).strip("-")
        rows.append(
          f'<div class="grow" data-cat="{cat}" id="{tid}">'
          f'<dt class="gtermname"><span class="gtermtext">{e(term)}</span>'
          f'<span class="gcatdot" aria-hidden="true"></span>'
          f'<span class="gcatname">{cat}</span></dt>'
          f'<dd class="gdef">{e(d)}'
          f'<button class="gcopy" type="button" data-copy="{e(term+": "+d)}" '
          f'aria-label="Copy the definition of {e(term)}">Copy</button></dd></div>')
    secs.append(f'<section class="gsec" data-letter="{L}" id="letter-{L}">'
                f'<h2 class="gsecmark" aria-label="Terms beginning with {L}">{L}</h2>'
                f'<dl class="gdl-list">{"".join(rows)}</dl></section>')

alpha="".join(f'<a class="gletter" href="#letter-{L}">{L}</a>' for L in letters)
pills=('<button class="gfilt" data-cat="all" aria-pressed="true">Everything</button>'
       + "".join(f'<button class="gfilt" data-cat="{c}" aria-pressed="false">{c}</button>' for c in used))

schema={"@context":"https://schema.org","@type":"DefinedTermSet","@id":f"{SITE}/glossary.html#set",
 "name":"SideKix Business Glossary","url":f"{SITE}/glossary.html","description":DESC,
 "publisher":{"@id":f"{SITE}/#organization"},
 "hasDefinedTerm":[{"@type":"DefinedTerm","name":t,"description":d,
   "inDefinedTermSet":f"{SITE}/glossary.html#set"} for t,c,d in T]}
crumbs={"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
 {"@type":"ListItem","position":1,"name":"Home","item":f"{SITE}/"},
 {"@type":"ListItem","position":2,"name":"Resources","item":f"{SITE}/resources.html"},
 {"@type":"ListItem","position":3,"name":"Business glossary","item":f"{SITE}/glossary.html"}]}

CSS='''
/* an author display rule outranks the browser rule for [hidden] */
.gloss [hidden]{display:none !important}
.gloss .sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;
  overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap;border:0}

/* the fog lifts off the word when you reach for it */
.gloss .fog{position:relative;display:inline-block;color:var(--gold);font-style:italic}
.gloss .fogw{position:relative;z-index:2;display:inline-block;
  filter:blur(2.4px);opacity:.8;
  transition:filter .6s cubic-bezier(.2,.8,.2,1),opacity .6s ease}
.gloss .fog::after{content:attr(data-word);position:absolute;left:0;top:0;z-index:1;
  color:#FFF6DC;font-style:italic;pointer-events:none;
  filter:blur(10px);opacity:.7;transform:translate(0,0) scale(1);
  transition:transform 1.15s cubic-bezier(.16,1,.3,1),opacity .85s ease,filter .85s ease}
.gloss h1:hover .fogw,.gloss .fog:focus-within .fogw{filter:blur(0);opacity:1}
.gloss h1:hover .fog::after,.gloss .fog:focus-within::after{
  transform:translate(34px,-14px) scale(1.18);opacity:0;filter:blur(22px)}
@media(hover:none){.gloss .fogw{filter:none;opacity:1}.gloss .fog::after{display:none}}
@media(prefers-reduced-motion:reduce){
  .gloss .fogw{filter:none;opacity:1;transition:none}
  .gloss .fog::after{display:none}}

/* back link */
.gloss .gbackrow{display:flex;justify-content:center;margin:0 0 22px}
.gloss .gback{display:inline-flex;align-items:center;gap:8px;min-height:44px;text-decoration:none;
  font-family:var(--util);font-size:10.5px;letter-spacing:.18em;text-transform:uppercase;
  color:var(--grey);transition:color .25s}
.gloss .gback:hover{color:var(--gold-pale)}
.gloss .gback svg{width:15px;height:15px;fill:none;stroke:currentColor;stroke-width:2;
  stroke-linecap:round;stroke-linejoin:round}

/* search and filters, on the theme's chip metrics */
.gloss .gsearch{max-width:min(520px,100%);margin:0 auto 22px}
.gloss .gsearch input{width:100%;min-height:48px;padding:0 20px;border-radius:999px;
  border:1px solid rgba(212,168,86,.32);background:linear-gradient(180deg,#0d0b06,#070706);
  color:#FFF8E8;font-family:var(--body);font-size:16px;transition:border-color .3s}
.gloss .gsearch input::placeholder{color:#8a8378}
.gloss .gsearch input:hover{border-color:rgba(212,168,86,.5)}
.gloss .gsearch input:focus{outline:3px solid var(--gold-pale);outline-offset:3px;border-color:var(--gold)}
.gloss .gfilters{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin:0 auto 20px;
  max-width:min(860px,100%)}
.gloss .gfilt{flex:0 0 auto;max-width:100%;font-family:var(--util);font-size:10.5px;letter-spacing:.16em;text-transform:uppercase;
  cursor:pointer;background:none;border:1px solid rgba(212,168,86,.32);color:#B9B4AB;
  border-radius:999px;padding:0 16px;min-height:44px;
  transition:background .3s,color .3s,border-color .3s}
.gloss .gfilt:hover{border-color:var(--gold);color:#F3E4A8}
.gloss .gfilt[aria-pressed="true"]{background:var(--gold);border-color:var(--gold);color:#1a1400;font-weight:700;
  box-shadow:0 6px 22px color-mix(in srgb,var(--c,#D4A856) 30%,transparent)}
.gloss .gfilt:focus-visible{outline:3px solid var(--gold-pale);outline-offset:3px}
.gloss .gfilt .n{font-size:9px;opacity:.65;margin-left:7px;letter-spacing:.08em}

/* the A to Z rail */
.gloss .galpha{display:flex;flex-wrap:wrap;gap:3px;justify-content:center;margin:0 auto 8px;
  max-width:min(700px,100%)}
.gloss .gletter{display:inline-flex;align-items:center;justify-content:center;
  min-width:34px;min-height:34px;border-radius:8px;text-decoration:none;
  font-family:var(--util);font-size:11px;letter-spacing:.06em;color:var(--grey);
  border:1px solid transparent;transition:color .25s,border-color .25s,background .25s}
.gloss .gletter:hover{color:#1a1400;background:var(--gold);border-color:var(--gold)}
.gloss .gletter:focus-visible{outline:3px solid var(--gold-pale);outline-offset:2px}
.gloss .gletter[hidden]{display:none}
.gloss .gcount{text-align:center;font-family:var(--util);font-size:10.5px;letter-spacing:.2em;
  text-transform:uppercase;color:var(--grey-dim);margin:14px 0 34px}

/* the index itself: a reference work, not a card wall */
.gloss .gindex{max-width:min(860px,100%);margin:0 auto;text-align:left}
.gloss .gsec{margin:0 0 10px;scroll-margin-top:110px}
.gloss .gsec[hidden]{display:none}
.gloss .gsecmark{font-family:var(--display);font-weight:600;font-size:15px;line-height:1;
  color:var(--gold);margin:0 0 6px;padding:0 0 8px;text-align:left;
  border-bottom:1px solid rgba(212,168,86,.28);letter-spacing:.12em}
.gloss .gdl-list{margin:0 0 26px}
.gloss .grow{display:grid;grid-template-columns:minmax(150px,210px) minmax(0,1fr);
  gap:8px 26px;align-items:baseline;padding:13px 10px 13px 0;
  border-bottom:1px solid rgba(212,168,86,.1);position:relative;
  transition:background .28s,border-color .28s}
.gloss .grow:hover{background:linear-gradient(90deg,
  color-mix(in srgb,var(--c,#D4A856) 7%,transparent),transparent 72%);
  border-color:color-mix(in srgb,var(--c,#D4A856) 34%,transparent)}
.gloss .grow[hidden]{display:none}
.gloss .gtermname{font-family:var(--body);font-weight:600;font-size:16.5px;line-height:1.35;
  color:#FFF8E8;margin:0;min-width:0;display:flex;align-items:baseline;gap:9px;flex-wrap:wrap}
.gloss .gtermtext{display:inline;overflow-wrap:anywhere}
.gloss .gcatdot{width:7px;height:7px;border-radius:99px;flex:none;
  background:var(--c,#D4A856);box-shadow:0 0 9px color-mix(in srgb,var(--c,#D4A856) 65%,transparent)}
.gloss .gcatname{font-family:var(--util);font-size:9px;letter-spacing:.18em;text-transform:uppercase;
  color:color-mix(in srgb,var(--c,#D4A856) 62%,#8a8378);transition:color .28s}
.gloss .grow:hover .gcatname,.gloss .grow:focus-within .gcatname{color:var(--c,#D4A856)}
.gloss .gdef{margin:0;min-width:0;overflow-wrap:anywhere;font-size:15.5px;line-height:1.62;color:#B9B4AB;position:relative;padding-right:70px}
.gloss .gcopy{position:absolute;right:0;top:-2px;cursor:pointer;opacity:0;
  border:1px solid rgba(212,168,86,.32);background:rgba(8,8,9,.7);color:var(--grey);
  font-family:var(--util);font-size:9px;letter-spacing:.16em;text-transform:uppercase;
  border-radius:999px;padding:0 11px;min-height:30px;
  transition:opacity .25s,color .25s,border-color .25s,background .25s}
.gloss .grow:hover .gcopy,.gloss .grow:focus-within .gcopy,
.gloss .gcopy:focus{opacity:1}
.gloss .gcopy:hover{color:#F3E4A8;border-color:var(--gold)}
.gloss .gcopy:focus-visible{outline:3px solid var(--gold-pale);outline-offset:2px}
.gloss .gcopy.ok{opacity:1;color:#1a1400;background:var(--gold);border-color:var(--gold);font-weight:700}
.gloss .gnone{text-align:center;color:var(--grey);font-style:italic;padding:34px 0 0}
.gloss mark{background:color-mix(in srgb,var(--gold) 26%,transparent);color:#FFF8E8;border-radius:3px;padding:0 2px}

/* download tiles, matching .hubs */
.gloss .gdlrow{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(260px,100%),1fr));gap:16px;
  max-width:min(900px,100%);margin:56px auto 0}
.gloss .gdl{color:#E3DED2;border:1px solid rgba(212,168,86,.4);border-radius:16px;padding:26px;text-decoration:none;
  display:block;background:linear-gradient(180deg,rgba(26,20,8,.5),rgba(8,8,9,.7));
  transition:transform .3s,border-color .3s}
.gloss .gdl:hover{transform:translateY(-3px);border-color:var(--gold)}
.gloss .gdl b{display:block;font-family:var(--display);font-size:26px;color:#FFF8E8;margin-bottom:4px}
.gloss .gdl span{font-family:var(--util);font-size:10.5px;letter-spacing:.18em;text-transform:uppercase;
  color:var(--gold-mid)}
/* ---- mobile ---- */
@media(max-width:760px){
  .gloss .gsecmark{position:sticky;top:64px;z-index:3;background:var(--ink);
    padding:8px 0;margin:0 0 2px}
  .gloss .galpha{gap:4px}
  .gloss .gletter{min-width:44px;min-height:44px;font-size:12px;
    border-color:rgba(212,168,86,.22)}
}
@media(max-width:640px){
  .gloss .grow{grid-template-columns:1fr;gap:5px;padding:15px 0}
  .gloss .gtermname{font-size:17px}
  .gloss .gdef{padding-right:0;font-size:15.5px}
  .gloss .gcopy{position:static;opacity:1;margin-top:12px;min-height:44px;
    display:block;width:max-content;line-height:42px;padding:0 18px;font-size:10px;text-align:center}
  .gloss .gfilt{min-height:44px;font-size:11px;padding:0 14px}
  .gloss .gsearch input{min-height:52px;font-size:16px}
  .gloss .gdl{padding:22px}
  .gloss .gdl b{font-size:22px}
}
@media(max-width:400px){
  .gloss .gfilters{gap:6px}
  .gloss .gfilt{padding:0 12px;letter-spacing:.1em}
  .gloss .gletter{min-width:36px}
}
@media print{.gloss .gfilters,.gloss .gsearch,.gloss .galpha,.gloss .gdlrow,
  .gloss .gcopy,.gloss .gbackrow{display:none}}
__CATCOLORS__
'''
_cc=[]
for _c,_h in COL.items():
    _cc.append(f'.gloss .grow[data-cat="{_c}"]{{--c:{_h}}}')
    _cc.append(f'.gloss .gfilt[data-cat="{_c}"]{{--c:{_h};color:{_h};'
               f'border-color:color-mix(in srgb,{_h} 40%,transparent)}}')
    _cc.append(f'.gloss .gfilt[data-cat="{_c}"]:hover{{border-color:{_h};'
               f'background:color-mix(in srgb,{_h} 12%,transparent)}}')
    _cc.append(f'.gloss .gfilt[data-cat="{_c}"][aria-pressed="true"]{{background:{_h};'
               f'border-color:{_h};color:#0b0b0c}}')
CSS=CSS.replace("__CATCOLORS__","\n".join(_cc))

JS='''
(function(){
  var root=document.querySelector('.gloss'); if(!root) return;
  var rows=[].slice.call(root.querySelectorAll('.grow')),
      secs=[].slice.call(root.querySelectorAll('.gsec')),
      lets=[].slice.call(root.querySelectorAll('.gletter')),
      btns=[].slice.call(root.querySelectorAll('.gfilt')),
      input=root.querySelector('#gq'),
      count=root.querySelector('#gcount'),
      none=root.querySelector('#gnone'),
      cat='all';
  var per={};
  rows.forEach(function(r){ var k=r.getAttribute('data-cat'); per[k]=(per[k]||0)+1; });
  btns.forEach(function(b){
    var k=b.getAttribute('data-cat');
    var n = k==='all' ? rows.length : (per[k]||0);
    if(!b.querySelector('.n')) b.insertAdjacentHTML('beforeend','<span class="n">'+n+'</span>');
  });

  /* highlight the matched text without touching the copy payload */
  function mark(el,q){
    var raw=el.getAttribute('data-raw');
    if(raw===null){ raw=el.textContent; el.setAttribute('data-raw',raw); }
    if(!q){ el.textContent=raw; return; }
    var i=raw.toLowerCase().indexOf(q);
    if(i<0){ el.textContent=raw; return; }
    el.textContent='';
    el.appendChild(document.createTextNode(raw.slice(0,i)));
    var m=document.createElement('mark'); m.textContent=raw.slice(i,i+q.length);
    el.appendChild(m);
    el.appendChild(document.createTextNode(raw.slice(i+q.length)));
  }

  function apply(){
    var q=(input.value||'').trim().toLowerCase(), n=0;
    rows.forEach(function(r){
      var okc = cat==='all' || r.getAttribute('data-cat')===cat;
      var name=r.querySelector('.gtermtext'),
          def=r.querySelector('.gdef');
      var hay=(name.textContent+' '+def.textContent).toLowerCase();
      var on = okc && (!q || hay.indexOf(q)>-1);
      r.hidden=!on; if(on) n++;
      mark(name,on&&q?q:'');
    });
    var live={};
    secs.forEach(function(s){
      var any=[].slice.call(s.querySelectorAll('.grow')).some(function(r){ return !r.hidden; });
      s.hidden=!any; live[s.getAttribute('data-letter')]=any;
    });
    lets.forEach(function(a){ a.hidden=!live[a.textContent]; });
    count.textContent = (cat==='all'&&!q) ? ('All '+n+' terms, A to Z')
                      : ('Showing '+n+' of '+rows.length+' terms');
    none.hidden = n>0;
  }

  /* the topic colour washes behind the page, as on the blog index */
  var COLJS=__COLJS__;
  var RM=!!(window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches);
  var wash=document.getElementById('reswash');
  if(!wash){ wash=document.createElement('div'); wash.id='reswash'; document.body.appendChild(wash); }
  var off=null;
  function washTo(c){ clearTimeout(off); wash.style.setProperty('--wash',c); wash.classList.add('on'); }
  function washOff(){ off=setTimeout(function(){ wash.classList.remove('on'); },260); }
  if(!RM){
    rows.concat(btns).forEach(function(el){
      el.addEventListener('pointerenter',function(){ washTo(COLJS[el.getAttribute('data-cat')]||'#D4A856'); });
      el.addEventListener('pointerleave',washOff);
    });
  }

  input.addEventListener('input',apply);
  btns.forEach(function(b){
    b.addEventListener('click',function(){
      cat=b.getAttribute('data-cat');
      btns.forEach(function(x){ x.setAttribute('aria-pressed', x===b?'true':'false'); });
      apply();
    });
  });
  root.addEventListener('click',function(ev){
    var b=ev.target.closest && ev.target.closest('.gcopy'); if(!b) return;
    var txt=b.getAttribute('data-copy');
    var done=function(){ var o=b.textContent; b.textContent='Copied'; b.classList.add('ok');
      setTimeout(function(){ b.textContent=o; b.classList.remove('ok'); },1500); };
    if(navigator.clipboard&&navigator.clipboard.writeText){
      navigator.clipboard.writeText(txt).then(done,function(){});
    } else {
      var ta=document.createElement('textarea'); ta.value=txt; ta.setAttribute('readonly','');
      ta.style.position='absolute'; ta.style.left='-9999px'; document.body.appendChild(ta);
      ta.select(); try{ document.execCommand('copy'); done(); }catch(err){}
      document.body.removeChild(ta);
    }
  });
  apply();
})();
'''
JS=JS.replace("__COLJS__",json.dumps(COL))

MAIN=f'''<main id="maincontent">
<section class="wrap res gloss">
  <p class="kx-backrow"><a class="kx-bk" href="resources.html">
    <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M15 5l-7 7 7 7"/></svg>
    Back to resources</a></p>
  <span class="eyebrow">Business glossary</span>
  <h1>The words, without the <span class="fog" data-word="fog."><span class="fogw">fog.</span></span></h1>
  <p class="lede">{len(T)} terms you will meet while starting something, each explained in one sentence.
  Copy any definition, or take the whole thing offline.</p>

  <div class="gsearch">
    <label class="sr-only" for="gq">Search the glossary</label>
    <input id="gq" type="search" placeholder="Search terms, for example runway or EIN" autocomplete="off">
  </div>
  <div class="gfilters">{pills}</div>
  <nav class="galpha" aria-label="Jump to a letter">{alpha}</nav>
  <p class="gcount" id="gcount">All {len(T)} terms, A to Z</p>

  <div class="gindex">{"".join(secs)}</div>
  <p class="gnone" id="gnone" hidden>Nothing matches that. Try a shorter word.</p>

  <div class="gdlrow">
    <a class="gdl" href="assets/worksheets/sidekix-business-glossary.pdf" download>
      <b>Take it offline</b><span>Download the glossary, 3 pages</span></a>
    <a class="gdl" href="tools.html"><b>Calculators</b><span>Four numbers, worked out</span></a>
    <a class="gdl" href="resources.html"><b>Resources</b><span>Everything, all of it</span></a>
  </div>
</section>
</main>'''

out=page("glossary.html",
  f"Business Glossary: {len(T)} Terms Explained Plainly | SideKix",
  DESC, MAIN, extra_css=CSS, extra_js=JS, schema=(schema,crumbs))
open("/home/claude/site/glossary.html","w",encoding="utf-8").write(out)
print("glossary rebuilt as an A to Z index:",len(out)//1024,"KB |",len(T),"terms |",len(groups),"letters")
