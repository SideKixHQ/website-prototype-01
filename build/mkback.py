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

# The series runs in issue order. Issue 2 has not been drawn yet, so the
# numbers skip rather than renumber: the issue number is printed inside the
# artwork and cannot be changed after the fact.
SERIES = [
 (1, "the-first-step", "The First Step",
  "Marcus has a notebook full of ideas and a shift that ends at 7:43. "
  "The revolution does not begin with capital."),
 (3, "built-together", "Built Together",
  "The market is growing, and growth brings people who would rather it did not. "
  "We are not competing. We are building."),
 (4, "built-to-last", "Built to Last",
  "Four questions every movement has to answer, and the difference between "
  "something that works and something that matters."),
 (5, "new-weapon-same-mission", "New Weapon. Same Mission.",
  "Synth joins, Operation Blackout begins, and the counterattack is not the one "
  "they were expecting."),
]

# One-shots. Same world, no running plot, readable in any order.
STRIPS = [
 ("ideas-are-easy", "Ideas are easy. Next steps are hard.",
  "One person, a wall of questions, and the difference a plan makes."),
 ("real-people-real-moments", "Real people. Real moments.",
  "Four people at four different starting points, and the same support under all of them."),
 ("start-where-you-stand", "Start where you stand.",
  "Eight panels from a first idea to a coffee cart that opened."),
]

COMICS = [(k, t, d) for _, k, t, d in SERIES] + STRIPS

body = ['<div class="br">']

# ---- the declaration, first thing on the page
body.append(
 '<section class="br-s br-decl br-lead"><h2>The declaration</h2>'
 '<a class="br-declcard" href="declaration.html">'
 '<img alt="" decoding="async" height="960" fetchpriority="high" '
 'src="assets/declaration/declaration-640.webp" width="640"/>'
 '<div><b>There is another way.</b>'
 '<span>Written for anyone who has decided to stop waiting for permission. '
 'Read it, and if it says what you would have said, put your name to it.</span>'
 '<em>Read and sign it &rarr;</em></div></a></section>')

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
def card(k, t, d, issue=None):
    n = len(PANELS[k])
    unit = "pages" if issue else "panels"
    num = ('<b class="br-iss">Issue %d</b>' % issue) if issue else ""
    return ('<figure class="br-comic%s">'
            '<button aria-label="Read %s, %d %s" class="br-open" data-key="%s" type="button">'
            '%s<img alt="%s" decoding="async" height="1536" loading="lazy" '
            'src="assets/comics/%s.webp" width="1024"/>'
            '<span aria-hidden="true" class="br-read">Read it</span></button>'
            '<figcaption><b>%s</b><span>%s</span>'
            '<em>%d %s</em></figcaption></figure>'
            % (" br-serial" if issue else "", e(t), n, unit, e(k), num,
               e(t + ". " + d), e(k), e(t), e(d), n, unit))

serial = "".join(card(k, t, d, i) for i, k, t, d in SERIES)
strips = "".join(card(k, t, d) for k, t, d in STRIPS)

DATA = {}
for n, (i, k, t, d) in enumerate(SERIES):
    DATA[k] = {"title": "Issue %d: %s" % (i, t), "panels": PANELS[k], "unit": "Page"}
    if n + 1 < len(SERIES):
        DATA[k]["next"] = SERIES[n + 1][1]
for k, t, d in STRIPS:
    DATA[k] = {"title": t, "panels": PANELS[k], "unit": "Panel"}

body.append(
 '<section class="br-s br-comics"><h2>The comics</h2>'
 '<h3 class="br-h3">The series</h3>'
 '<p class="br-b">One story, running across issues. Marcus starts with a notebook '
 'and ends up with a market, and the people who would rather he did not are paying '
 'attention. Read them in order. Issue 2 is still being drawn, which is why the '
 'numbers skip.</p>'
 '<div class="br-cgrid br-cserial">%s</div>'
 '<h3 class="br-h3">One-shots</h3>'
 '<p class="br-b">Same world, no running plot. Read these in any order.</p>'
 '<div class="br-cgrid">%s</div>'
 '<script id="br-panels" type="application/json">%s</script>'
 '</section>' % (serial, strips,
                 json.dumps(DATA, ensure_ascii=False).replace("</", "<\\/")))

body.append("</div>")

CSS = """
.br-h3{font-family:var(--util,inherit);font-size:11.5px;letter-spacing:.18em;
  text-transform:uppercase;color:#D4A856;font-weight:700;margin:38px 0 10px}
.br-h3:first-of-type{margin-top:8px}
.br-iss{position:absolute;top:12px;left:12px;z-index:2;
  font-family:var(--util,inherit);font-size:10px;letter-spacing:.24em;
  text-transform:uppercase;font-weight:500;color:#F3E4A8;
  background:rgba(8,7,4,.82);border:1px solid rgba(212,168,86,.55);
  padding:6px 12px;border-radius:999px;backdrop-filter:blur(3px)}
.br-comic.br-serial .br-open{position:relative}
.br-view.at-end .br-ctl.br-next{border-color:#D4A856;color:#FFF6DC;
  background:rgba(212,168,86,.18)}

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
.br-comic figcaption b{display:block;font-family:var(--display);font-size:19px;color:#FFF8E8;
  line-height:1.25;margin:0 0 5px}
.br-comic figcaption span{display:block;font-size:14px;line-height:1.6;color:#948D81}

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
.br-stagewrap{flex:1;position:relative;overflow:hidden;
  touch-action:none;            /* the reader handles pan and pinch itself */
  cursor:grab;user-select:none;-webkit-user-select:none}
.br-stagewrap:active{cursor:grabbing}
.br-img{position:absolute;left:0;top:0;transform-origin:0 0;
  will-change:transform;image-rendering:auto;max-width:none;
  -webkit-user-drag:none;user-select:none}
.br-ctl.br-fit[aria-pressed="true"]{border-color:#D4A856;color:#FFF6DC;
  background:rgba(212,168,86,.18)}
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
.br-read{position:absolute;left:50%;bottom:16px;transform:translateX(-50%) translateY(6px);
  display:inline-flex;align-items:center;justify-content:center;
  font-family:var(--util);font-size:11px;letter-spacing:.18em;text-transform:uppercase;
  font-weight:700;line-height:1;
  color:#1B1400 !important;background:linear-gradient(180deg,#D7C582,#A1853E);
  min-height:44px;padding:0 26px;border-radius:999px;
  box-shadow:0 10px 34px rgba(231,182,70,.34);
  opacity:0;transition:opacity .3s,transform .3s;white-space:nowrap}
.br-open:hover .br-read,.br-open:focus-visible .br-read{opacity:1;transform:translateX(-50%) translateY(0)}
@media(pointer:coarse){ .br-read{opacity:1;transform:translateX(-50%) translateY(0)} }
.br-comic em{display:block;font-style:normal;font-family:var(--util);font-size:10px;
  letter-spacing:.16em;text-transform:uppercase;color:var(--gold);margin-top:7px}

/* ---- the declaration, leading the page ----
   A slow glow rather than a flash: it draws the eye without competing with
   the artwork inside the card, and it stops entirely for anyone who has asked
   the system to reduce motion. */
@keyframes brGlow{
  0%,100%{box-shadow:0 0 0 1px rgba(212,168,86,.34), 0 0 30px -6px rgba(231,182,70,.30)}
  50%    {box-shadow:0 0 0 1px rgba(212,168,86,.72), 0 0 66px -4px rgba(231,182,70,.62)}
}
.br-lead{margin:0 0 56px}
.br-lead .br-declcard{
  border-radius:18px;
  animation:brGlow 3.4s ease-in-out infinite;
  transition:transform .35s cubic-bezier(.16,1,.3,1)}
.br-lead .br-declcard:hover,
.br-lead .br-declcard:focus-visible{
  animation-play-state:paused;
  box-shadow:0 0 0 1px #D4A856, 0 0 78px -4px rgba(231,182,70,.75);
  transform:translateY(-3px)}
@media(prefers-reduced-motion:reduce){
  .br-lead .br-declcard{animation:none;
    box-shadow:0 0 0 1px rgba(212,168,86,.6), 0 0 40px -8px rgba(231,182,70,.45)}
}

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
    '<div class="br-stagewrap"><img class="br-img" alt="" draggable="false"/>'+
      '<p class="br-hint">Pinch or double tap to zoom, drag to move</p>'+
      '<div class="br-prog"><i></i></div>'+
    '</div>'+
    '<div class="br-nav">'+
      '<button class="br-ctl br-prev" type="button" aria-label="Previous page">&#8592;</button>'+
      '<button class="br-ctl br-fit" type="button" aria-label="Fit the whole sheet">FIT</button>'+
      '<button class="br-ctl br-next" type="button" aria-label="Next page">&#8594;</button>'+
    '</div>';
  document.body.appendChild(view);

  var img=view.querySelector('.br-img'),
      stage=view.querySelector('.br-stagewrap'),
      titleEl=view.querySelector('.br-title'), countEl=view.querySelector('.br-count'),
      progEl=view.querySelector('.br-prog i'), hintEl=view.querySelector('.br-hint'),
      prevB=view.querySelector('.br-prev'), nextB=view.querySelector('.br-next'),
      wholeB=view.querySelector('.br-whole'), closeB=view.querySelector('.br-close'),
      fitB=view.querySelector('.br-fit');

  var key=null, panels=[], at=0, whole=false, last=null;

  var unitWord='Panel', sheetWord='page', nextKey='';
  /* ---- pan and zoom, rather than fit-a-page-to-the-screen ----
     A page inside one of these sheets is about 315 by 364 pixels. Filling a
     phone screen with it is a 3.7x upscale in device pixels, which is why the
     old reader looked soft: it was magnifying, every time, by default.

     So the default is the whole sheet fitted, which is a downscale and
     therefore sharp, and moving to a page zooms only as far as MAXDEV device
     pixels per source pixel. Past that the reader stops on its own. Anyone who
     wants closer can pinch, and softness they chose reads completely
     differently from softness the page imposed. */
  var MAXDEV = 2.2;                 /* auto zoom ceiling, device px per source px */
  var k=1, tx=0, ty=0;              /* current scale and translation */
  var fitK=1;                       /* scale at which the whole sheet fits */
  var dpr = window.devicePixelRatio || 1;

  function metrics(){
    var r = stage.getBoundingClientRect();
    return {VW:r.width, VH:r.height, IW:img.naturalWidth, IH:img.naturalHeight};
  }

  function paint(){
    img.style.transform = 'translate3d('+tx+'px,'+ty+'px,0) scale('+k+')';
  }

  function clamp(){
    var m = metrics();
    var w = m.IW*k, h = m.IH*k;
    /* keep the sheet in view: centre it while it is smaller than the stage,
       and stop it being dragged off screen once it is bigger */
    if(w <= m.VW) tx = (m.VW - w)/2; else tx = Math.min(0, Math.max(m.VW - w, tx));
    if(h <= m.VH) ty = (m.VH - h)/2; else ty = Math.min(0, Math.max(m.VH - h, ty));
  }

  function fit(){
    var m = metrics();
    if(!m.IW) return;
    fitK = Math.min(m.VW/m.IW, m.VH/m.IH) * 0.96;
    k = fitK; clamp(); paint();
    whole = true; label();
  }

  /* centre the view on one page, at a scale that stays sharp */
  function show(i){
    var m = metrics();
    if(!m.IW) return;
    at = Math.max(0, Math.min(panels.length-1, i));
    var b = panels[at];
    var want = Math.min(m.VW/(b[2]*m.IW), m.VH/(b[3]*m.IH)) * 0.94;
    k = Math.min(want, MAXDEV/dpr);          /* the ceiling that keeps it sharp */
    k = Math.max(k, fitK);                   /* never end up smaller than fitting */
    tx = m.VW/2 - (b[0] + b[2]/2) * m.IW * k;
    ty = m.VH/2 - (b[1] + b[3]/2) * m.IH * k;
    clamp(); paint();
    whole = false; label();
  }

  function label(){
    countEl.textContent = whole ? ('Whole '+sheetWord) : (at+1)+' / '+panels.length;
    progEl.style.width = whole ? '100%' : (((at+1)/panels.length)*100)+'%';
    prevB.disabled = !whole && at===0;
    var atEnd = !whole && at===panels.length-1;
    nextB.disabled = atEnd && !nextKey;
    view.classList.toggle('at-end', atEnd && !!nextKey);
    nextB.setAttribute('aria-label', atEnd && nextKey
      ? 'Next issue' : 'Next '+unitWord.toLowerCase());
    wholeB.textContent = whole ? unitWord.toUpperCase()+'S' : sheetWord.toUpperCase();
    wholeB.setAttribute('aria-label', whole
      ? ('Go to the first '+unitWord.toLowerCase())
      : ('Show the whole '+sheetWord));
    fitB.setAttribute('aria-pressed', String(whole));
  }

  function frame(){ if(whole) fit(); else show(at); }

  function go(n){
    /* from the fitted sheet, forward means the first page rather than the
       second: 'at' is still 0 because nothing has been visited yet */
    if(whole){ show(n > at ? 0 : panels.length-1); return; }
    if(n >= panels.length && nextKey){ openKey(nextKey); return; }
    show(n);
  }

  /* ---- the user's own zoom, which is deliberately not capped ---- */
  function zoomAt(cx, cy, factor){
    var m = metrics();
    var nk = Math.min(Math.max(k*factor, fitK), fitK*10);
    if(nk === k) return;
    /* keep the point under the fingers where it is */
    tx = cx - (cx - tx) * (nk/k);
    ty = cy - (cy - ty) * (nk/k);
    k = nk;
    whole = Math.abs(k - fitK) < 0.001;
    clamp(); paint(); label();
  }
  function open(btn){
    last=btn; openKey(btn.getAttribute('data-key'));
  }
  function openKey(k){
    key=k;
    var d=DATA[key]; if(!d) return;
    panels=d.panels; at=0; whole=true;
    unitWord  = d.unit || 'Panel';
    sheetWord = unitWord==='Page' ? 'sheet' : 'page';
    nextKey   = d.next || '';
    titleEl.textContent=d.title;
    view.hidden=false;
    document.documentElement.style.overflow='hidden';
    document.documentElement.classList.add('br-reading');
    hintEl.hidden=false; hintEl.style.opacity='1';
    setTimeout(function(){ hintEl.style.opacity='0'; }, 2600);
    img.onload=fit;
    img.src='assets/comics/'+key+'.webp';
    img.alt=d.title;
    if(img.complete) fit();
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
  wholeB.addEventListener('click', function(){ if(whole) show(0); else fit(); });
  fitB.addEventListener('click', fit);
  closeB.addEventListener('click', close);
  window.addEventListener('resize', function(){ if(!view.hidden) frame(); });

  /* ---- gestures ----
     One finger drags. Two fingers pinch. A short one finger swipe with no
     movement of the image behind it still turns the page, so the old habit
     keeps working. */
  var pts = {}, startDist = 0, startK = 1, startMid = null;
  var downX = 0, downY = 0, downT = 0, dragged = false, lastTap = 0;

  function pointerList(){ var a=[]; for(var id in pts) a.push(pts[id]); return a; }
  function localXY(ev){
    var r = stage.getBoundingClientRect();
    return {x: ev.clientX - r.left, y: ev.clientY - r.top};
  }

  stage.addEventListener('pointerdown', function(ev){
    if(ev.pointerType === 'mouse' && ev.button !== 0) return;
    stage.setPointerCapture(ev.pointerId);
    pts[ev.pointerId] = localXY(ev);
    var list = pointerList();
    if(list.length === 1){
      downX = list[0].x; downY = list[0].y; downT = Date.now(); dragged = false;
    } else if(list.length === 2){
      startDist = Math.hypot(list[0].x-list[1].x, list[0].y-list[1].y) || 1;
      startK = k;
      startMid = {x:(list[0].x+list[1].x)/2, y:(list[0].y+list[1].y)/2};
    }
  });

  stage.addEventListener('pointermove', function(ev){
    if(!pts[ev.pointerId]) return;
    var prev = pts[ev.pointerId];
    var now = localXY(ev);
    pts[ev.pointerId] = now;
    var list = pointerList();

    if(list.length === 2 && startMid){
      var d = Math.hypot(list[0].x-list[1].x, list[0].y-list[1].y) || 1;
      var nk = Math.min(Math.max(startK * (d/startDist), fitK), fitK*10);
      tx = startMid.x - (startMid.x - tx) * (nk/k);
      ty = startMid.y - (startMid.y - ty) * (nk/k);
      k = nk; whole = Math.abs(k - fitK) < 0.001;
      clamp(); paint(); label();
      dragged = true;
      ev.preventDefault();
      return;
    }
    if(list.length === 1){
      var dx = now.x - prev.x, dy = now.y - prev.y;
      if(Math.abs(now.x-downX) > 6 || Math.abs(now.y-downY) > 6) dragged = true;
      tx += dx; ty += dy;
      clamp(); paint();
      ev.preventDefault();
    }
  });

  function endPointer(ev){
    var had = pointerList().length;
    delete pts[ev.pointerId];
    if(pointerList().length < 2) startMid = null;
    if(had !== 1) return;

    var p = localXY(ev);
    var dx = p.x - downX, dy = p.y - downY, dt = Date.now() - downT;

    /* a flick down on the fitted sheet closes, the way a sheet dismisses */
    if(whole && dy > 110 && Math.abs(dy) > Math.abs(dx)*1.6){ close(); return; }

    if(!dragged && dt < 400){
      var now = Date.now();
      if(now - lastTap < 320){          /* double tap: into a page, or back out */
        lastTap = 0;
        if(whole){
          var m = metrics();
          var fx = (p.x - tx) / (m.IW * k), fy = (p.y - ty) / (m.IH * k);
          var hit = 0;
          for(var i=0;i<panels.length;i++){
            var b = panels[i];
            if(fx>=b[0] && fx<=b[0]+b[2] && fy>=b[1] && fy<=b[1]+b[3]){ hit=i; break; }
          }
          show(hit);
        } else { fit(); }
        return;
      }
      lastTap = now;
      /* single tap on the left or right third turns the page */
      if(!whole){
        var r = stage.getBoundingClientRect();
        if(p.x < r.width*0.33) { go(at-1); }
        else if(p.x > r.width*0.67) { go(at+1); }
      }
    }
  }
  stage.addEventListener('pointerup', endPointer);
  stage.addEventListener('pointercancel', endPointer);

  /* desktop: wheel zooms, which is what people try first */
  stage.addEventListener('wheel', function(ev){
    if(view.hidden) return;
    ev.preventDefault();
    var p = localXY(ev);
    zoomAt(p.x, p.y, ev.deltaY < 0 ? 1.12 : 1/1.12);
  }, {passive:false});

  document.addEventListener('keydown', function(ev){
    if(view.hidden) return;
    if(ev.key==='Escape'){ close(); return; }
    if(ev.key==='ArrowRight'||ev.key==='PageDown'){ ev.preventDefault(); go(at+1); return; }
    if(ev.key==='ArrowLeft'||ev.key==='PageUp'){ ev.preventDefault(); go(at-1); return; }
    if(ev.key==='Home'){ ev.preventDefault(); go(0); return; }
    if(ev.key==='End'){ ev.preventDefault(); go(panels.length-1); return; }
    if(ev.key==='0'){ ev.preventDefault(); fit(); return; }
    if(ev.key==='+'||ev.key==='='){ ev.preventDefault();
      var m0=metrics(); zoomAt(m0.VW/2, m0.VH/2, 1.25); return; }
    if(ev.key==='-'||ev.key==='_'){ ev.preventDefault();
      var m1=metrics(); zoomAt(m1.VW/2, m1.VH/2, 1/1.25); return; }
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
LEDE  = ("Ideas come from curiosity. Perspective. Play. People. Sometimes from wandering "
         "somewhere you didn't mean to go. That's what this room is for.")

SCHEMA = (
  crumbs("The Back Room", "back-room.html"),
  {"@context":"https://schema.org","@type":"CollectionPage",
   "@id":f"{SITE}/back-room.html#page","url":f"{SITE}/back-room.html",
   "name":"The Back Room","description":DESC,
   "publisher":{"@type":"Organization","name":"SideKix","url":SITE}},
)

n = page("back-room.html", TITLE, DESC, "The Back Room",
         "Go ahead. <em>Get distracted.</em>",
         LEDE, "".join(body), css=CSS, js=JS, schema=SCHEMA,
         wrapcls="wrap res br-page", back=BACK)
print(f"back-room.html {n//1024} KB")
