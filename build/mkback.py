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
import os, sys, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from toolgen import page, crumbs, SITE
def e(s): return html.escape(str(s), quote=True)

BACK = ('<p class="kx-backrow"><a class="kx-bk" href="index.html">'
        '<svg aria-hidden="true" focusable="false" viewbox="0 0 24 24">'
        '<path d="M15 5l-7 7 7 7"></path></svg> Back to SideKix</a></p>')

GAME = "https://sidekixhq.github.io/runkixrun/"

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
 '<button aria-label="Open %s at full size" class="br-open" data-src="assets/comics/%s.webp" '
 'data-title="%s" type="button">'
 '<img alt="%s" decoding="async" height="840" loading="lazy" '
 'src="assets/comics/%s-sm.webp" width="560"/></button>'
 '<figcaption><b>%s</b><span>%s</span></figcaption></figure>'
 % (e(t), e(k), e(t), e(t + ". " + d), e(k), e(t), e(d))
 for k, t, d in COMICS)
body.append(
 '<section class="br-s br-comics"><h2>The comics</h2>'
 '<p class="br-b">Three pages, drawn the way the story actually goes. Tap one to read it.</p>'
 '<div class="br-cgrid">%s</div></section>' % cards)

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

/* the reader */
.br-view{position:fixed;inset:0;z-index:400;background:rgba(6,5,3,.95);
  display:flex;align-items:center;justify-content:center;padding:26px}
.br-view[hidden]{display:none}
.br-view img{max-width:min(1024px,94vw);max-height:92vh;width:auto;height:auto;
  border-radius:8px;box-shadow:0 30px 90px rgba(0,0,0,.7)}
.br-close{position:absolute;top:18px;right:18px;min-width:48px;min-height:48px;
  border:1px solid rgba(212,168,86,.5);border-radius:999px;background:rgba(11,10,6,.9);
  color:#EBD08C;font-size:19px;cursor:pointer;line-height:1}
.br-close:hover{border-color:var(--gold);color:#FFF6DC}

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

JS = """
/* the game arrives on a click, so a visitor who never plays never loads it */
var stage=document.getElementById('br-stage'), play=document.getElementById('br-play');
if(stage && play){
  play.addEventListener('click', function(){
    var f=document.createElement('iframe');
    f.src=%(game)r;
    f.title='Run Kix Run';
    f.setAttribute('allow','fullscreen; autoplay');
    f.setAttribute('loading','lazy');
    stage.innerHTML=''; stage.classList.add('on'); stage.appendChild(f);
    f.focus();
  });
}

/* the comic reader: one dialog, opened from any cover, closed by escape,
   the backdrop or the button, and it hands focus back where it came from */
var covers=[].slice.call(document.querySelectorAll('.br-open'));
if(covers.length){
  var view=document.createElement('div');
  view.className='br-view'; view.hidden=true;
  view.setAttribute('role','dialog'); view.setAttribute('aria-modal','true');
  view.innerHTML='<button class="br-close" type="button" aria-label="Close">&#10005;</button><img alt=""/>';
  document.body.appendChild(view);
  var img=view.querySelector('img'), closeBtn=view.querySelector('.br-close'), last=null;

  function open(btn){
    last=btn;
    img.src=btn.getAttribute('data-src');
    img.alt=btn.getAttribute('data-title')||'';
    view.setAttribute('aria-label', btn.getAttribute('data-title')||'Comic');
    view.hidden=false;
    document.documentElement.style.overflow='hidden';
    closeBtn.focus();
  }
  function close(){
    view.hidden=true; img.removeAttribute('src');
    document.documentElement.style.overflow='';
    if(last) last.focus();
  }
  covers.forEach(function(b){ b.addEventListener('click', function(){ open(b); }); });
  closeBtn.addEventListener('click', close);
  view.addEventListener('click', function(ev){ if(ev.target===view) close(); });
  document.addEventListener('keydown', function(ev){
    if(view.hidden) return;
    if(ev.key==='Escape'){ close(); return; }
    /* only two things are focusable in here, so the trap is this small */
    if(ev.key==='Tab'){ ev.preventDefault(); closeBtn.focus(); }
  });
}
""" % {"game": GAME}

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
