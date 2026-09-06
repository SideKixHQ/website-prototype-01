# -*- coding: utf-8 -*-
"""The press page.

A press page for a pre-launch company is usually three empty headings under a
logo, which tells a journalist that nobody has written about you. This one is
built the other way round: it leads with the things that are true today and
useful to a writer on deadline. The boilerplate they can paste, the facts they
can check, the figures they can quote with a federal source behind each one,
and a person who answers.

PODCASTS, ARTICLES, COVERAGE and EVENTS render only when they have entries.
An empty list produces no heading at all, so the page never advertises a gap.
"""
import os, sys, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from toolgen import page, crumbs, SITE
def e(s): return html.escape(str(s), quote=True)

BACK = ('<p class="kx-backrow"><a class="kx-bk" href="index.html">'
        '<svg aria-hidden="true" focusable="false" viewbox="0 0 24 24">'
        '<path d="M15 5l-7 7 7 7"></path></svg> Back to SideKix</a></p>')

# ---------------------------------------------------------------- the content
# Each list below renders a section. Leave one empty and its heading does not
# appear. Format is (title, outlet, date, url) with date as "March 2026".
RELEASES = [
 ("177 million Americans have a business idea. Most never take the first step.",
  "SideKix HQ", "5 September 2026", "assets/press/sidekix-launch-release.pdf"),
]

PODCASTS = []      # shows James has been a guest on
ARTICLES = []      # pieces James has written elsewhere
COVERAGE = []      # anyone writing about SideKix
EVENTS   = []      # (name, date, place, url) company events coming up

BOILER = ("SideKix is a business operating system for people building something. It blends "
          "AI guidance with human advisors, turning a person's goals and challenges into a "
          "path they can actually follow. SideKix is a product of Character Limit LLC, doing "
          "business as SideKix, based in Wilmington, North Carolina. The company is pre-launch.")

FACTS = [
 ("Legal entity", "Character Limit LLC, doing business as SideKix"),
 ("Headquarters", "Wilmington, North Carolina, United States"),
 ("Stage", "Pre-launch. Membership tiers are published but not yet selling."),
 ("Trademark", "SideKix is a pending US federal trademark application."),
 ("Advertising", "The site publishes no sponsored content and runs no advertising."),
 ("Founder", "James Martucci, Founder and Chief Executive Officer"),
]

FIGURES = [
 ("174 million", "Americans aged 15 and over who have had an idea for a business",
  "market-data.html", "US Census Bureau and SBA Office of Advocacy, compiled on our market data page"),
 ("3 in 100", "of them who act on one in a given year",
  "market-data.html", "The same page, with the derivation shown"),
 ("50 states", "of LLC filing requirements, each figure linked to the state's own page",
  "state-filing.html", "Read from each Secretary of State, with the date it was checked"),
]

def sec(cls, title, blurb, inner):
    return ('<section class="pr-s %s"><h2>%s</h2>%s%s</section>'
            % (cls, e(title), '<p class="pr-b">%s</p>' % e(blurb) if blurb else '', inner))

def linklist(rows, kind):
    if not rows: return ""
    out = []
    for r in rows:
        if kind == "event":
            name, date, place, url = r
            meta = "%s &middot; %s" % (e(date), e(place))
        else:
            name, date, place, url = r[0], r[2], r[1], r[3]
            meta = "%s &middot; %s" % (e(place), e(date))
        out.append('<li><a href="%s" rel="noopener" target="_blank"><b>%s</b>'
                   '<span>%s</span></a></li>' % (e(url), e(name), meta))
    return '<ul class="pr-list">%s</ul>' % "".join(out)

body = ['<div class="pr">']

# what a writer on deadline needs first
body.append(
 '<div class="pr-now">'
 '<a class="pr-card" href="#pr-kit"><b>The press kit</b>'
 '<span>Wordmark, the artwork, the founder photograph and this page as a document.</span></a>'
 '<a class="pr-card" href="#kx-support"><b>An interview</b>'
 '<span>Tell us the outlet and the deadline. A person answers, usually the same day.</span></a>'
 '<a class="pr-card" href="market-data.html"><b>Figures you can quote</b>'
 '<span>Federal data on US business formation, every number linked to the agency that published it.</span></a>'
 '</div>')

body.append(sec("pr-boiler", "The paragraph you can paste",
  "Written to be quoted whole. Nothing in it needs checking against us.",
  '<blockquote class="pr-quote" id="pr-boiler">%s</blockquote>'
  '<button class="kxcta kxcta-quiet" data-copy="pr-boiler" type="button">Copy the boilerplate</button>'
  % e(BOILER)))

body.append(sec("pr-facts", "Fast facts", "",
  '<dl class="pr-dl">%s</dl>' % "".join(
    "<div><dt>%s</dt><dd>%s</dd></div>" % (e(k), e(v)) for k, v in FACTS)))

body.append(sec("pr-figs", "Numbers with a source behind them",
  "Everything on our market data page comes from a US federal or state agency. Works of the "
  "federal government are in the public domain and facts cannot be copyrighted, so these are "
  "yours to use. Follow the link for the release rather than trusting a page to be current.",
  '<div class="pr-figs-g">%s</div>' % "".join(
    '<a class="pr-fig" href="%s"><em>%s</em><b>%s</b><span>%s</span></a>'
    % (e(u), e(n), e(t), e(s)) for n, t, u, s in FIGURES)))

body.append(sec("pr-kit", "The press kit", "",
  '<p class="pr-b" id="pr-kit">The kit holds the wordmark in light and dark, the twelve energies '
  'artwork, a founder photograph, the boilerplate above and the brand colours. Ask and it comes '
  'back as one file.</p>'
  '<div class="pr-acts">'
  '<a class="kxcta kxcta-lead" href="#kx-support">Request the press kit</a>'
  '<a class="kxcta kxcta-quiet" href="mailto:support@sidekixhq.com'
  '?subject=Press%20enquiry">Email us directly</a></div>'))

if RELEASES:
    rows = "".join(
      '<li><a href="%s"><b>%s</b><span>%s &middot; %s &middot; PDF</span></a></li>'
      % (e(u), e(t), e(o), e(d)) for t, o, d, u in RELEASES)
    body.append(sec("pr-rel", "Releases", "",
      '<ul class="pr-list">%s</ul>' % rows))

if PODCASTS:
    body.append(sec("pr-pods", "Conversations", "Shows James has been a guest on.",
                    linklist(PODCASTS, "pod")))
if ARTICLES:
    body.append(sec("pr-arts", "Written elsewhere", "Pieces by James, published by other people.",
                    linklist(ARTICLES, "art")))
if COVERAGE:
    body.append(sec("pr-cov", "Written about SideKix", "", linklist(COVERAGE, "cov")))
if EVENTS:
    body.append(sec("pr-ev", "Where we will be", "", linklist(EVENTS, "event")))

body.append(sec("pr-contact", "Who to ask", "",
  '<p class="pr-b">James Martucci answers press directly. Say what you are writing and when it '
  'is due, and you will get a straight answer or a straight no, not a maybe.</p>'
  '<p class="pr-b"><a class="pr-mail" href="mailto:support@sidekixhq.com'
  '?subject=Press%20enquiry">support@sidekixhq.com</a></p>'))
body.append("</div>")

CSS = """
/* the same call to action rules membership uses, so a button looks the
   same wherever it appears on the site */
.press .kxcta{
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
.press .kxcta-lead{
  border:1px solid #A1853E !important;
  color:#E8DEC4 !important;
  margin:34px auto 0 !important}
.press .kxcta-lead:hover{
  background:#2F2613 !important;
  border-color:#F3E4A8 !important;
  color:#FFF8E8 !important}
.press .kxcta-quiet{
  border:1px solid rgba(161,133,62,.55) !important;
  color:#BDB49F !important;
  margin:14px auto 0 !important}
.press .kxcta-quiet:hover{
  background:rgba(212,168,86,.08) !important;
  border-color:#A1853E !important;
  color:#E8DEC4 !important}
.press .kxcta:focus-visible{
  outline:3px solid #FFD166 !important;
  outline-offset:3px !important}
@media(max-width:560px){
  .press .kxcta{
    white-space:normal;
    min-height:52px !important;
    padding:12px 20px !important;
    letter-spacing:.12em !important;
    line-height:1.35}
}
@media(prefers-reduced-motion:reduce){
  .press .kxcta{transition:none}
}

/* the same alignment the Energy Discovery got: filled gold is the primary
   action everywhere else on the site, so it is the primary action here */
.press .kxcta{font-family:var(--body) !important;font-size:16px !important;
  letter-spacing:normal !important;text-transform:none !important;
  min-height:56px !important;padding:0 32px !important;font-weight:700 !important}
.press .kxcta-lead{background:linear-gradient(180deg,#D7C582,#A1853E) !important;
  border:none !important;color:#1B1400 !important;margin:0 !important}
.press .kxcta-lead:hover{background:linear-gradient(180deg,#E6D89A,#B8974A) !important}
.press .kxcta-quiet{border:1px solid rgba(212,168,86,.55) !important;
  color:#EBD08C !important;font-weight:600 !important;margin:0 !important}
.press .kxcta-quiet:hover{background:rgba(212,168,86,.1) !important;
  border-color:#D4A856 !important;color:#FFF6DC !important}

/* ---- the press page ----
   A writer on deadline wants three things in the first screen: something to
   paste, something to check, and someone to ask. That is the order. */
.pr{max-width:900px;margin:0 auto}
.pr-now{display:grid;gap:14px;grid-template-columns:repeat(3,minmax(0,1fr));margin:0 0 54px}
.pr-card{display:block;text-decoration:none;border:1px solid rgba(212,168,86,.24);
  border-radius:16px;padding:22px 20px;
  background:linear-gradient(180deg,rgba(20,18,13,.9),rgba(11,10,7,.92));
  transition:border-color .3s,transform .3s}
.pr-card:hover{border-color:rgba(212,168,86,.62);transform:translateY(-3px)}
.pr-card b{display:block;font-family:var(--display);font-size:21px;color:#FFF8E8;margin:0 0 7px}
.pr-card span{display:block;font-size:14.5px;line-height:1.6;color:#A7A196}
.pr-s{margin:0 0 52px}
.pr-s > h2{font-family:var(--util);font-size:11px;letter-spacing:.2em;text-transform:uppercase;
  color:var(--gold);margin:0 0 14px;font-weight:400}
.pr-b{color:#A7A196;font-size:15.5px;line-height:1.75;margin:0 0 18px;max-width:66ch}
.pr-quote{margin:0 0 18px;padding:22px 24px;border-left:2px solid rgba(212,168,86,.5);
  background:rgba(212,168,86,.05);color:#D8D2C4;font-size:16.5px;line-height:1.8}
.pr-dl{margin:0;display:grid;gap:0}
.pr-dl > div{display:grid;grid-template-columns:minmax(140px,200px) 1fr;gap:18px;
  padding:15px 0;border-top:1px solid rgba(212,168,86,.14)}
.pr-dl > div:last-child{border-bottom:1px solid rgba(212,168,86,.14)}
.pr-dl dt{font-family:var(--util);font-size:10.5px;letter-spacing:.16em;text-transform:uppercase;
  color:#948D81;margin:2px 0 0}
.pr-dl dd{margin:0;color:#D8D2C4;font-size:15.5px;line-height:1.6}
.pr-figs-g{display:grid;gap:14px;grid-template-columns:repeat(3,minmax(0,1fr))}
.pr-fig{display:block;text-decoration:none;border:1px solid rgba(212,168,86,.2);
  border-radius:14px;padding:20px 18px;transition:border-color .3s}
.pr-fig:hover{border-color:rgba(212,168,86,.55)}
.pr-fig em{display:block;font-style:normal;font-family:var(--display);font-size:34px;
  line-height:1;color:var(--gold);margin:0 0 8px}
.pr-fig b{display:block;font-weight:400;font-size:15px;line-height:1.55;color:#D8D2C4;margin:0 0 10px}
.pr-fig span{display:block;font-size:12.5px;line-height:1.55;color:#8C867B}
.pr-list{list-style:none;margin:0;padding:0}
.pr-list li{border-top:1px solid rgba(212,168,86,.14)}
.pr-list li:last-child{border-bottom:1px solid rgba(212,168,86,.14)}
.pr-list a{display:flex;flex-wrap:wrap;align-items:baseline;gap:6px 16px;
  padding:17px 0;text-decoration:none}
.pr-list b{font-weight:400;font-family:var(--display);font-size:20px;color:#FFF8E8}
.pr-list span{font-family:var(--util);font-size:10.5px;letter-spacing:.14em;
  text-transform:uppercase;color:#948D81}
.pr-list a:hover b{color:var(--gold-pale)}
.pr-acts{display:flex;flex-wrap:wrap;gap:12px}
.pr-mail{color:var(--gold-pale);font-size:17px}
.pr-copied{margin:10px 0 0;font-size:14px;color:#948D81}
@media(max-width:820px){
  .pr-now,.pr-figs-g{grid-template-columns:1fr}
  .pr-dl > div{grid-template-columns:1fr;gap:5px}
  .pr-acts .kxcta{flex:1 1 100%}
}
"""

JS = """
/* one copy button, and it says so out loud for anyone not watching the button */
var btn=document.querySelector('[data-copy]');
if(btn){
  var say=document.createElement('p');
  say.className='pr-copied'; say.setAttribute('aria-live','polite'); say.hidden=true;
  btn.parentNode.insertBefore(say, btn.nextSibling);
  btn.addEventListener('click',function(){
    var src=document.getElementById(btn.getAttribute('data-copy'));
    if(!src) return;
    var t=src.textContent.trim();
    function done(ok){
      say.hidden=false;
      say.textContent = ok ? 'Copied.' : 'Copying was blocked. Select the paragraph and copy it.';
    }
    if(navigator.clipboard && navigator.clipboard.writeText){
      navigator.clipboard.writeText(t).then(function(){done(true);},function(){done(false);});
    } else { done(false); }
  });
}
"""

TITLE = "Press: Facts, Figures and a Press Kit | SideKix"
DESC  = ("What SideKix is, the boilerplate you can paste, federal figures on US business "
         "formation you can quote, and a person who answers press enquiries.")
LEDE  = ("Everything a writer needs in one place: what the company is, a paragraph you can quote "
         "whole, numbers with a federal source behind each one, and someone who answers.")

SCHEMA = (
  crumbs("Press", "press.html"),
  {"@context":"https://schema.org","@type":"WebPage",
   "@id":f"{SITE}/press.html#page","url":f"{SITE}/press.html",
   "name":"Press","description":DESC,
   "publisher":{"@type":"Organization","name":"SideKix","url":SITE,
                "legalName":"Character Limit LLC",
                "address":{"@type":"PostalAddress","addressLocality":"Wilmington",
                           "addressRegion":"NC","addressCountry":"US"}}},
)

n = page("press.html", TITLE, DESC, "Press",
         "The facts, the figures,<br/>and someone to <em>talk to</em>.",
         LEDE, "".join(body), css=CSS, js=JS, schema=SCHEMA,
         wrapcls="wrap res press", back=BACK)
print(f"press.html {n//1024} KB")
