# -*- coding: utf-8 -*-
"""The Back Room.

Everything SideKix makes that will not help anyone run a business. A game, the
comics, and a declaration worth putting your name to. It earns its place by
being the only part of the site with no work in it, which is also why it is
the part somebody might send to a friend.

The game is embedded on a click rather than on load, the same way the film is
handled elsewhere: a poster and a button, so a page nobody plays on costs
nothing to open.
"""
import os, sys, io, json, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from toolgen import page, crumbs, SITE
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def e(s): return html.escape(str(s), quote=True)

BACK = ('<p class="kx-backrow"><a class="kx-bk" href="index.html">'
        '<svg aria-hidden="true" focusable="false" viewbox="0 0 24 24">'
        '<path d="M15 5l-7 7 7 7"></path></svg> Back to SideKix</a></p>')

GAME = "https://sidekixhq.github.io/runkixrun/"

PANELS = json.load(io.open(os.path.join(ROOT, "assets", "comics", "panels.json"),
                           encoding="utf-8"))

COMICS = [
 ("ideas-are-easy", "Ideas are easy. Next steps are hard.",
  "One person, a wall of questions, and the difference a plan makes."),
 ("real-people-real-moments", "Real people. Real moments.",
  "Four people at four different starting points, and the same support under all of them."),
 ("start-where-you-stand", "Start where you stand.",
  "Eight panels from a first idea to a coffee cart that opened."),
]

body = ['<div class="br">']

# ---- the game
body.append(
 '<section class="br-s br-game"><h2>The game</h2>'
 '<div class="br-gamebox">'
 '<div class="br-gamestage" id="br-stage">'
 '<div class="br-gameface">'
 '<b>Run Kix Run</b>'
 '<p>Every founder meets the same obstacles. Collect coins, pick up advisors, '
 'and see how far you get before one of them stops you.</p>'
 '<button class="kxcta kxcta-lead" id="br-play" type="button">Play it here</button>'
 '<p class="br-alt"><a href="%s" rel="noopener" target="_blank">Open it in its own tab instead</a></p>'
 '</div></div></div></section>' % e(GAME))

# ---- the comics
cards = "".join(
 '<figure class="br-comic">'
 '<button aria-label="Read %s, %d panels" class="br-open" data-key="%s" type="button">'
 '<img alt="%s" decoding="async" height="840" loading="lazy" '
 'src="assets/comics/%s-sm.webp" width="560"/>'
 '<span aria-hidden="true" class="br-read">Read it</span></button>'
 '<figcaption><b>%s</b><span>%s</span>'
 '<em>%d panels</em></figcaption></figure>'
 % (e(t), len(PANELS[k]), e(k), e(t + ". " + d), e(k), e(t), e(d), len(PANELS[k]))
 for k, t, d in COMICS)
DATA = {k: {"title": t, "panels": PANELS[k]} for k, t, d in COMICS}
body.append(
 '<section class="br-s br-comics"><h2>The comics</h2>'
 '<p class="br-b">Three pages. Open one and it walks you through panel by '
 'panel, which is the only way a full page is readable on a phone. Arrow keys '
 'or swipe to move, and the whole page is one tap away.</p>'
 '<div class="br-cgrid">%s</div>'
 '<script id="br-panels" type="application/json">%s</script>'
 '</section>' % (cards, json.dumps(DATA, ensure_ascii=False).replace("</", "<\\/")))

# ---- the declaration
body.append(
 '<section class="br-s br-decl"><h2>The declaration</h2>'
 '<a class="br-declcard" href="declaration.html">'
 '<img alt="" decoding="async" height="960" loading="lazy" '
 'src="assets/declaration/declaration-640.webp" width="640"/>'
 '<div><b>There is another way.</b>'
 '<span>Written for anyone who has decided to stop waiting for permission. '
 'Read it, and if it says what you would have said, put your name to it.</span>'
 '<em>Read and sign it &rarr;</em></div></a></section>')

body.append("</div>")

CSS = """
/* the same call to action rules membership uses, so a button looks the
   same wherever it appears on the site */
.br-page .kxcta{
  display:inline-flex !important;
  align-items:center !important;
  justify-content:center !important;
  gap:8px;
  min-height:48px !important;
  padding:0 26px !important;
  border-radius:999px !important;
  font-family:var(--util) !important;
  font-size:11px !important;
  letter-spacing:.18em !important;
  text-transform:uppercase !important;
  text-decoration:none !important;
  border-bottom:0 !important;
  background:none !important;
  cursor:pointer;
  white-space:nowrap;
  transition:background .22s ease,border-color .22s ease,color .22s ease}
.br-page .kxcta-lead{
  border:1px solid #A1853E !important;
  color:#E8DEC4 !important;
  margin:34px auto 0 !important}
.br-page .kxcta-lead:hover{
  background:#2F2613 !important;
  border-color:#F3E4A8 !important;
  color:#FFF8E8 !important}
.br-page .kxcta-quiet{
  border:1px solid rgba(161,133,62,.55) !important;
  color:#BDB49F !important;
  margin:14px auto 0 !important}
.br-page .kxcta-quiet:hover{
  background:rgba(212,168,86,.08) !important;
  border-color:#A1853E !important;
  color:#E8DEC4 !important}
.br-page .kxcta:focus-visible{
  outline:3px solid #FFD166 !important;
  outline-offset:3px !important}
@media(max-width:560px){
  .br-page .kxcta{
    white-space:normal;
    min-height:52px !important;
    padding:12px 20px !important;
    letter-spacing:.12em !important;
    line-height:1.35}
}
@media(prefers-reduced-motion:reduce){
  .br-page .kxcta{transition:none}
}

.br-page .kxcta{font-family:var(--body) !important;font-size:17px !important;
  letter-spacing:normal !important;text-transform:none !important;
  min-height:58px !important;padding:0 34px !important;font-weight:700 !important;margin:0 !important}
.br-page .kxcta-lead{background:linear-gradient(180deg,#D7C582,#A1853E) !important;
  border:none !important;color:#1B1400 !important}
.br-page .kxcta-lead:hover{background:linear-gradient(180deg,#E6D89A,#B8974A) !important}

/* ---- the back room ----
   Three things and nothing else, each given the whole width, because this is
   the one page where nobody is scanning for an answer. */
.br{max-width:1000px;margin:0 auto}
.br-s{margin:0 0 62px}
.br-s:last-child{margin-bottom:0}
.br-s > h2{font-family:var(--util);font-size:11px;letter-spacing:.2em;text-transform:uppercase;
  color:var(--gold);margin:0 0 14px;font-weight:400}
.br-b{color:#A7A196;font-size:15.5px;line-height:1.7;margin:0 0 22px;max-width:62ch}

/* the game loads on a click, not on arrival */
.br-gamestage{position:relative;border:1px solid rgba(212,168,86,.28);border-radius:18px;
  overflow:hidden;background:
    radial-gradient(120% 130% at 20% 0,rgba(212,168,86,.13),transparent 60%),
    linear-gradient(180deg,rgba(22,19,13,.95),rgba(11,10,7,.95));
  min-height:clamp(340px,52vh,540px);display:flex;align-items:center;justify-content:center}
.br-gameface{text-align:center;padding:44px 26px;max-width:52ch}
.br-gameface b{display:block;font-family:var(--display);font-size:clamp(34px,5vw,54px);
  line-height:1.05;color:#FFF8E8;margin:0 0 14px}
.br-gameface p{color:#A7A196;font-size:16px;line-height:1.7;margin:0 0 26px}
.br-alt{margin:18px 0 0 !important;font-size:14px !important}
.br-alt a{color:#BDB4A4}
.br-alt a:hover{color:var(--gold-pale)}
.br-gamestage iframe{width:100%;height:clamp(420px,72vh,720px);border:0;display:block}
.br-gamestage.on{min-height:0;padding:0}

/* the comics */
.br-cgrid{display:grid;gap:18px;grid-template-columns:repeat(3,minmax(0,1fr))}
.br-comic{margin:0}
.br-open{display:block;width:100%;padding:0;border:1px solid rgba(212,168,86,.22);
  border-radius:12px;overflow:hidden;background:none;cursor:zoom-in;
  transition:border-color .3s,transform .3s}
.br-open:hover{border-color:rgba(212,168,86,.65);transform:translateY(-3px)}
.br-open img{display:block;width:100%;height:auto}
.br-comic figcaption{padding:14px 2px 0}
.br-comic b{display:block;font-family:var(--display);font-size:19px;color:#FFF8E8;
  line-height:1.25;margin:0 0 5px}
.br-comic span{display:block;font-size:14px;line-height:1.6;color:#948D81}

/* ---- the reader ----
   A full comic page on a phone is 1024px of artwork in a 390px hole, which is
   not reading, it is squinting. The reader shows one panel at a time, scaled
   to whatever room the screen has, and the whole page is one tap away for
   anyone who wants to see the shape of it. */
.br-view{position:fixed;inset:0;z-index:600;background:#070604;
  display:flex;flex-direction:column}
/* the site nav is fixed at z-index 500, so it sat on top of the reader's own
   bar and swallowed taps meant for it. While the reader is open the nav is
   out of the way entirely. */
html.br-reading #kx-nav{display:none !important}
.br-view[hidden]{display:none}
.br-stagewrap{flex:1;position:relative;overflow:hidden;touch-action:pan-y pinch-zoom}
.br-clip{position:absolute;overflow:hidden;border-radius:6px;
  box-shadow:0 18px 60px rgba(0,0,0,.6)}
.br-clip img{position:absolute;left:0;top:0;max-width:none;display:block}
.br-view.zoomed .br-clip{transition:left .32s cubic-bezier(.4,0,.2,1),
  top .32s cubic-bezier(.4,0,.2,1),width .32s cubic-bezier(.4,0,.2,1),
  height .32s cubic-bezier(.4,0,.2,1)}
.br-view.zoomed .br-clip img{transition:left .32s cubic-bezier(.4,0,.2,1),
  top .32s cubic-bezier(.4,0,.2,1),width .32s cubic-bezier(.4,0,.2,1)}
.br-bar{display:flex;align-items:center;gap:14px;padding:12px 16px;
  border-bottom:1px solid rgba(212,168,86,.2);background:rgba(11,10,6,.9)}
.br-bar b{font-family:var(--display);font-size:18px;color:#FFF8E8;font-weight:600;
  margin-right:auto;line-height:1.2}
.br-count{font-family:var(--util);font-size:11px;letter-spacing:.14em;color:#948D81;
  font-variant-numeric:tabular-nums;white-space:nowrap}
.br-ctl{min-width:48px;min-height:48px;border:1px solid rgba(212,168,86,.45);
  border-radius:999px;background:rgba(11,10,6,.85);color:#EBD08C;font-size:17px;
  cursor:pointer;line-height:1;display:grid;place-items:center;padding:0 14px;
  font-family:var(--util);letter-spacing:.1em}
.br-ctl:hover:not(:disabled){border-color:var(--gold);color:#FFF6DC;
  background:rgba(212,168,86,.12)}
.br-ctl:disabled{opacity:.32;cursor:default}
.br-nav{display:flex;align-items:center;gap:12px;justify-content:center;
  padding:12px 16px calc(12px + env(safe-area-inset-bottom,0px));
  border-top:1px solid rgba(212,168,86,.2);background:rgba(11,10,6,.9)}
.br-prog{position:absolute;left:0;right:0;bottom:0;height:2px;
  background:rgba(212,168,86,.16)}
.br-prog i{display:block;height:100%;background:var(--gold);
  transition:width .3s ease;width:0}
.br-hint{position:absolute;left:50%;bottom:16px;transform:translateX(-50%);
  font-family:var(--util);font-size:10px;letter-spacing:.16em;text-transform:uppercase;
  color:#8C867B;background:rgba(11,10,6,.72);padding:7px 13px;border-radius:999px;
  pointer-events:none;transition:opacity .5s}
.br-hint[hidden]{display:none}
@media(max-width:560px){
  .br-bar b{font-size:15px}
  .br-ctl{padding:0 11px;font-size:15px}
}

/* the covers say what they are */
.br-open{position:relative}
.br-read{position:absolute;left:50%;bottom:14px;transform:translateX(-50%) translateY(6px);
  font-family:var(--util);font-size:10px;letter-spacing:.18em;text-transform:uppercase;
  color:#1B1400;background:linear-gradient(180deg,#D7C582,#A1853E);
  padding:9px 18px;border-radius:999px;opacity:0;transition:opacity .3s,transform .3s;
  white-space:nowrap}
.br-open:hover .br-read,.br-open:focus-visible .br-read{opacity:1;transform:translateX(-50%) translateY(0)}
@media(pointer:coarse){ .br-read{opacity:1;transform:translateX(-50%) translateY(0)} }
.br-comic em{display:block;font-style:normal;font-family:var(--util);font-size:10px;
  letter-spacing:.16em;text-transform:uppercase;color:var(--gold);margin-top:7px}

/* the declaration */
.br-declcard{display:grid;grid-template-columns:200px 1fr;gap:26px;align-items:center;
  text-decoration:none;border:1px solid rgba(212,168,86,.24);border-radius:18px;
  padding:24px;background:linear-gradient(180deg,rgba(20,18,13,.9),rgba(11,10,7,.92));
  transition:border-color .3s,transform .3s}
.br-declcard:hover{border-color:rgba(212,168,86,.62);transform:translateY(-3px)}
.br-declcard img{display:block;width:100%;height:auto;border-radius:8px}
.br-declcard b{display:block;font-family:var(--display);font-size:clamp(26px,3.2vw,36px);
  line-height:1.1;color:#FFF8E8;margin:0 0 10px}
.br-declcard span{display:block;font-size:16px;line-height:1.7;color:#A7A196;margin:0 0 16px}
.br-declcard em{font-style:normal;font-family:var(--util);font-size:11px;letter-spacing:.18em;
  text-transform:uppercase;color:var(--gold)}

@media(max-width:820px){
  .br-cgrid{grid-template-columns:repeat(2,minmax(0,1fr))}
  .br-declcard{grid-template-columns:1fr;gap:18px}
  .br-declcard img{max-width:260px}
}
@media(max-width:560px){
  .br-cgrid{grid-template-columns:1fr}
}
"""

JS = ("""
/* the game arrives on a click, so a visitor who never plays never loads it */
var stage=document.getElementById('br-stage'), play=document.getElementById('br-play');
if(stage && play){
  play.addEventListener('click', function(){
    var f=document.createElement('iframe');
    f.src="__GAME_URL__";
    f.title='Run Kix Run';
    f.setAttribute('allow','fullscreen; autoplay');
    f.setAttribute('loading','lazy');
    stage.innerHTML=''; stage.classList.add('on'); stage.appendChild(f);
    f.focus();
  });
}

/* ---- the comic reader ----
   One dialog, driven by the panel map in the page. Each panel is framed by
   scaling the whole page image so that panel fills the stage, which keeps one
   decoded image in memory instead of thirty crops and makes the move between
   panels a transform rather than a load.

   Arrow keys, swipe, and the buttons all do the same thing. Escape closes it,
   focus is trapped while it is open and handed back to the cover that opened
   it. */
var covers=[].slice.call(document.querySelectorAll('.br-open'));
var dataEl=document.getElementById('br-panels');
if(covers.length && dataEl){
  var DATA=JSON.parse(dataEl.textContent);

  var view=document.createElement('div');
  view.className='br-view'; view.hidden=true;
  view.setAttribute('role','dialog'); view.setAttribute('aria-modal','true');
  view.innerHTML=
    '<div class="br-bar">'+
      '<b class="br-title"></b>'+
      '<span class="br-count"></span>'+
      '<button class="br-ctl br-whole" type="button" aria-label="Show the whole page">PAGE</button>'+
      '<button class="br-ctl br-close" type="button" aria-label="Close">&#10005;</button>'+
    '</div>'+
    '<div class="br-stagewrap"><div class="br-clip"><img alt=""/></div>'+
      '<p class="br-hint">Swipe or use the arrow keys</p>'+
      '<div class="br-prog"><i></i></div>'+
    '</div>'+
    '<div class="br-nav">'+
      '<button class="br-ctl br-prev" type="button" aria-label="Previous panel">&#8592;</button>'+
      '<button class="br-ctl br-next" type="button" aria-label="Next panel">&#8594;</button>'+
    '</div>';
  document.body.appendChild(view);

  var img=view.querySelector('img'), clip=view.querySelector('.br-clip'),
      stage=view.querySelector('.br-stagewrap'),
      titleEl=view.querySelector('.br-title'), countEl=view.querySelector('.br-count'),
      progEl=view.querySelector('.br-prog i'), hintEl=view.querySelector('.br-hint'),
      prevB=view.querySelector('.br-prev'), nextB=view.querySelector('.br-next'),
      wholeB=view.querySelector('.br-whole'), closeB=view.querySelector('.br-close');

  var key=null, panels=[], at=0, whole=false, last=null;

  function frame(){
    if(!img.naturalWidth) return;
    var IW=img.naturalWidth, IH=img.naturalHeight;
    var r=stage.getBoundingClientRect(), VW=r.width, VH=r.height;
    var box = whole ? [0,0,1,1] : panels[at];
    var pad = whole ? 0.94 : 0.98;
    var sc = Math.min(VW/(box[2]*IW), VH/(box[3]*IH)) * pad;
    var w=IW*sc, h=IH*sc;                       /* the whole page at this scale */
    var cw=box[2]*w, ch=box[3]*h;               /* the panel's own box on screen */
    clip.style.width=cw+'px'; clip.style.height=ch+'px';
    clip.style.left=Math.round((VW-cw)/2)+'px';
    clip.style.top =Math.round((VH-ch)/2)+'px';
    img.style.width=w+'px'; img.style.height=h+'px';
    img.style.left=(-box[0]*w)+'px'; img.style.top=(-box[1]*h)+'px';
    countEl.textContent = whole ? 'Whole page' : (at+1)+' / '+panels.length;
    progEl.style.width = whole ? '100%' : (((at+1)/panels.length)*100)+'%';
    prevB.disabled = whole || at===0;
    nextB.disabled = whole || at===panels.length-1;
    wholeB.textContent = whole ? 'PANELS' : 'PAGE';
    wholeB.setAttribute('aria-label', whole ? 'Back to panel by panel' : 'Show the whole page');
    view.classList.add('zoomed');
  }
  function go(n){
    if(whole){ whole=false; }
    at=Math.max(0, Math.min(panels.length-1, n));
    frame();
  }
  function open(btn){
    last=btn; key=btn.getAttribute('data-key');
    var d=DATA[key]; if(!d) return;
    panels=d.panels; at=0; whole=false;
    titleEl.textContent=d.title;
    view.hidden=false;
    document.documentElement.style.overflow='hidden';
    document.documentElement.classList.add('br-reading');
    hintEl.hidden=false; hintEl.style.opacity='1';
    setTimeout(function(){ hintEl.style.opacity='0'; }, 2600);
    img.onload=frame;
    img.src='assets/comics/'+key+'.webp';
    img.alt=d.title;
    if(img.complete) frame();
    closeB.focus();
  }
  function close(){
    view.hidden=true; view.classList.remove('zoomed');
    img.removeAttribute('src');
    document.documentElement.style.overflow='';
    document.documentElement.classList.remove('br-reading');
    if(last) last.focus();
  }

  covers.forEach(function(b){ b.addEventListener('click', function(){ open(b); }); });
  prevB.addEventListener('click', function(){ go(at-1); });
  nextB.addEventListener('click', function(){ go(at+1); });
  wholeB.addEventListener('click', function(){ whole=!whole; frame(); });
  closeB.addEventListener('click', close);
  window.addEventListener('resize', function(){ if(!view.hidden) frame(); });

  /* a swipe moves a panel; a flick down closes */
  var sx=0, sy=0, moved=false;
  stage.addEventListener('touchstart', function(ev){
    var t=ev.changedTouches[0]; sx=t.clientX; sy=t.clientY; moved=false;
  }, {passive:true});
  stage.addEventListener('touchend', function(ev){
    var t=ev.changedTouches[0], dx=t.clientX-sx, dy=t.clientY-sy;
    if(Math.abs(dx)>44 && Math.abs(dx)>Math.abs(dy)){ go(at + (dx<0?1:-1)); moved=true; }
    else if(dy>90 && Math.abs(dy)>Math.abs(dx)){ close(); moved=true; }
  });
  /* tapping the right or left of the stage also moves, which is what a reader
     expects and costs nothing to support */
  stage.addEventListener('click', function(ev){
    if(moved || whole) return;
    var r=stage.getBoundingClientRect();
    go(at + ((ev.clientX - r.left) > r.width*0.5 ? 1 : -1));
  });

  document.addEventListener('keydown', function(ev){
    if(view.hidden) return;
    if(ev.key==='Escape'){ close(); return; }
    if(ev.key==='ArrowRight'||ev.key==='PageDown'){ ev.preventDefault(); go(at+1); return; }
    if(ev.key==='ArrowLeft'||ev.key==='PageUp'){ ev.preventDefault(); go(at-1); return; }
    if(ev.key==='Home'){ ev.preventDefault(); go(0); return; }
    if(ev.key==='End'){ ev.preventDefault(); go(panels.length-1); return; }
    if(ev.key!=='Tab') return;
    /* keep focus inside the dialog */
    var f=[].slice.call(view.querySelectorAll('button')).filter(function(b){ return !b.disabled; });
    var i=f.indexOf(document.activeElement);
    ev.preventDefault();
    f[(i + (ev.shiftKey ? -1 : 1) + f.length) % f.length].focus();
  });
}
""".replace("__GAME_URL__", GAME))

TITLE = "The Back Room: A Game, Comics and a Declaration | SideKix"
DESC  = ("Everything SideKix makes that will not help you run a business. Run Kix Run, "
         "three comics, and a declaration worth putting your name to.")
LEDE  = ("Nothing in here will help you run a business. That is the point of it. A game, "
         "three comics, and a declaration worth putting your name to.")

SCHEMA = (
  crumbs("The Back Room", "back-room.html"),
  {"@context":"https://schema.org","@type":"CollectionPage",
   "@id":f"{SITE}/back-room.html#page","url":f"{SITE}/back-room.html",
   "name":"The Back Room","description":DESC,
   "publisher":{"@type":"Organization","name":"SideKix","url":SITE}},
)

n = page("back-room.html", TITLE, DESC, "The Back Room",
         "Nothing in here will<br/>help you <em>run a business</em>.",
         LEDE, "".join(body), css=CSS, js=JS, schema=SCHEMA,
         wrapcls="wrap res br-page", back=BACK)
print(f"back-room.html {n//1024} KB")
