# -*- coding: utf-8 -*-
import os, sys, json, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from toolgen import page, crumbs, webapp, faqpage, SITE
def e(s): return html.escape(str(s), quote=True)

CSS = """
/* ---- start here ---- */
.th-start{margin:0 0 26px}
.th-start h2{font-family:var(--util);font-size:11px;letter-spacing:.22em;
  text-transform:uppercase;color:#BDB4A4;font-weight:600;margin:0 0 12px}
.th-startrow{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}
.th-startrow a{display:flex;flex-direction:column;gap:6px;padding:16px 18px;
  border-radius:14px;text-decoration:none;border:1px solid rgba(212,168,86,.3);
  background:rgba(212,168,86,.06);min-height:44px}
.th-startrow a:hover{border-color:#D4A856;background:rgba(212,168,86,.13)}
.th-startrow b{color:#FFF8E8;font-size:15.5px;line-height:1.3;font-weight:600}
.th-startrow em{font-style:normal;font-family:var(--util);font-size:10px;
  letter-spacing:.16em;text-transform:uppercase;color:#D4A856}
@media(max-width:720px){.th-startrow{grid-template-columns:1fr}}

/* ---- filter ---- */
.th-find{position:relative;margin:0 0 22px}
.th-find input{width:100%;background:#0C0B08;border:1px solid rgba(212,168,86,.3);
  border-radius:12px;color:#F5EACE;font-family:var(--body);font-size:16px;
  padding:15px 16px;min-height:52px;outline:none;
  transition:border-color .25s,box-shadow .25s}
.th-find input::placeholder{color:#8A8378}
.th-find input:focus{border-color:#D4A856;box-shadow:0 0 0 3px rgba(212,168,86,.16)}
.th-find input:focus-visible{outline:3px solid #F3E4A8;outline-offset:2px}
.th-count{margin:9px 0 0;font-family:var(--util);font-size:11px;
  letter-spacing:.14em;text-transform:uppercase;color:#BDB4A4;min-height:16px}
.th-c[hidden],.th-g[hidden]{display:none !important}
.th-none{margin:18px 0 0;color:#BDB4A4;font-size:15.5px}

/* ---- the tools hub ----
   Fourteen cards that were all the same box in the same three column grid, so
   the eye had nothing to catch on and a calculator looked exactly like a
   checklist. Three things fix that without leaving the palette.

   One: every card ends on the quantity it actually deals in. Fifty states,
   seven rows, twelve endings, twenty eight steps. Each of those numbers is
   counted from the page it points at, so the grid reads as fourteen different
   things rather than fourteen paragraphs.

   Two: each group carries its own accent, set once as --a on the section and
   used only for the label, the figure and the hover edge. Body copy stays
   cream everywhere, so the page gains zones without gaining a rainbow.

   Three: the column count follows the group size. Groups of four sit two up
   and groups of three sit three up, so no row is ever left with an orphan
   card and two empty slots beside it. */
.th{max-width:1120px;margin:0 auto}
.th-g{--a:#D4A856;--aq:212,168,86;margin:0 0 60px}
.th-g:last-child{margin-bottom:0}
.th{padding-bottom:0}
.th-g.g2{--a:#6FB3A6;--aq:111,179,166}
.th-g.g3{--a:#B07FE0;--aq:176,127,224}
.th-g.g4{--a:#DA9367;--aq:218,147,103}
.th-g.g5{--a:#8FA9D8;--aq:143,169,216}

/* ---- the first group is the front door ----
   The assessment is the only thing here that reads you rather than a figure,
   so it takes a wider card and carries the twelve animals across the top. The
   strip is decorative and marked as such: the card's own words say what it is.
   Nothing about it moves until a pointer is on it, and even then only the
   opacity, so it costs nothing at rest and stops under reduced motion. */
.th-g.n2 .th-c{grid-column:span 3}
.th-g.g1 .th-c:first-child{grid-column:span 4}
.th-g.g1 .th-c:last-child{grid-column:span 2}
.th-hero{border-color:rgba(243,228,168,.34) !important;
  background:
    radial-gradient(120% 130% at 12% 0,rgba(212,168,86,.14),transparent 58%),
    linear-gradient(180deg,rgba(26,22,14,.94),rgba(12,11,8,.94)) !important}
.th-hero:hover{border-color:rgba(243,228,168,.75) !important}
.th-hero b{color:#FFF6DC}
.th-zoo{display:flex;gap:6px;align-items:flex-end;margin:0 0 16px;
  height:52px;overflow:hidden}
.th-zoo img{height:100%;width:auto;object-fit:contain;opacity:.55;
  filter:saturate(.75);transition:opacity .45s ease,filter .45s ease,transform .45s ease}
.th-hero:hover .th-zoo img{opacity:1;filter:saturate(1)}
.th-hero:hover .th-zoo img:nth-child(2n){transform:translateY(-3px)}
.th-hero:hover .th-zoo img:nth-child(3n){transform:translateY(2px)}
@media(prefers-reduced-motion:reduce){
  .th-zoo img{transition:none}
  .th-hero:hover .th-zoo img{transform:none}
}
.th-g > h2{display:flex;align-items:center;gap:14px;
  font-family:var(--util);font-size:11px;letter-spacing:.2em;text-transform:uppercase;
  color:var(--a);margin:0 0 6px;font-weight:400}
.th-g > h2::after{content:"";flex:1;height:1px;
  background:linear-gradient(90deg,rgba(var(--aq),.45),transparent)}
.th-g > p{color:#9C968D;font-size:15px;line-height:1.7;margin:0 0 22px;max-width:62ch}

.th-cards{display:grid;gap:16px;grid-template-columns:repeat(6,minmax(0,1fr))}
.th-g.n4 .th-c{grid-column:span 3}
.th-g.n3 .th-c{grid-column:span 2}

.th-c{position:relative;display:flex;flex-direction:column;min-width:0;text-decoration:none;
  border:1px solid rgba(var(--aq),.22);border-radius:16px;padding:24px 24px 18px;
  background:
    radial-gradient(140% 110% at 8% 0,rgba(var(--aq),.075),transparent 62%),
    linear-gradient(180deg,rgba(20,18,13,.9),rgba(11,10,7,.92));
  transition:border-color .3s,transform .3s,box-shadow .3s}
.th-c:hover{border-color:rgba(var(--aq),.62);transform:translateY(-3px);
  box-shadow:0 14px 40px -18px rgba(var(--aq),.5)}
.th-c:focus-visible{outline:3px solid var(--a);outline-offset:3px}
/* the index sits behind the title rather than beside it, so it gives the card
   a corner without taking a line of its own */
.th-c::before{content:attr(data-n);position:absolute;top:14px;right:18px;
  font-family:var(--display);font-size:30px;line-height:1;color:rgba(var(--aq),.22);
  transition:color .3s}
.th-c:hover::before{color:rgba(var(--aq),.5)}
.th-c b{display:block;font-family:var(--display);font-size:24px;line-height:1.15;
  color:#FFF8E8;margin:0 44px 9px 0}
.th-c span{display:block;font-size:15px;line-height:1.66;color:#A7A196}
.th-c .th-s{margin-top:auto;padding-top:15px;display:flex;align-items:baseline;gap:11px;
  border-top:1px solid rgba(var(--aq),.18)}
.th-c em{font-style:normal;font-family:var(--display);font-size:40px;line-height:.9;
  color:var(--a);font-weight:600;letter-spacing:-.01em;
  text-shadow:0 0 26px rgba(var(--aq),.3)}
.th-c i{font-style:normal;font-family:var(--util);font-size:10px;letter-spacing:.17em;
  text-transform:uppercase;color:#948D81;line-height:1.5}
/* the stat row needs air above it when the copy is short */
.th-c span{margin-bottom:14px}

.th-note{position:relative;border-left:2px solid rgba(212,168,86,.5);border-radius:0;
  padding:4px 0 4px 20px;font-size:14.5px;line-height:1.75;color:#9C968D;margin:0 0 48px;
  max-width:74ch}
.th-note b{color:#E8DEC4;font-weight:600}

@media(max-width:900px){
  .th-g.n4 .th-c,.th-g.n3 .th-c,
  .th-g.g1 .th-c:first-child,.th-g.g1 .th-c:last-child{grid-column:span 3}
}
@media(max-width:620px){
  .th-cards{grid-template-columns:1fr;gap:13px}
  .th-g.n4 .th-c,.th-g.n3 .th-c,.th-g.n2 .th-c,
  .th-g.g1 .th-c:first-child,.th-g.g1 .th-c:last-child{grid-column:span 1}
  .th-zoo{height:44px;gap:4px}
  .th-g{margin-bottom:44px}
  .th-c{padding:22px 20px 18px}
  .th-c b{font-size:21px;margin-right:38px}
  .th-c::before{font-size:26px;top:12px;right:16px}
  .th-c em{font-size:34px}
}
"""

ZOO = ["lion","dragon","phoenix","octopus","dolphin","unicorn",
       "gorilla","panda","cat","goat","highland","possum"]

# Named for the question the visitor already has, not for what the tool does
# mechanically. The old names were "Work out where you are", "Work out a
# number" and "Work something out about yourself", which is three openings out
# of five that begin the same way and two that mean the same thing.
#
# Fields are (href, title, description, minutes, what you get).
GROUPS = [
 ("What will this cost me?",
  "Four calculators. Change a figure and the answer moves. Nothing is saved and nothing is sent.",
  [("startup-cost-calculator.html","What will it cost to start?","One-off costs to open plus the months of running costs you need behind you.","4","a number you can plan against"),
   ("breakeven-calculator.html","When do you break even?","Fixed costs divided by what each sale contributes, in units and in revenue.","2","units and revenue"),
   ("hourly-rate-calculator.html","What should you charge an hour?","Worked back from the income you want and the hours you can actually bill.","3","an hourly rate"),
   ("product-pricing-calculator.html","What should you price a product at?","From the margin you want, with materials, labour, overhead and payment fees taken out.","3","a price and a margin")]),
 ("What do I have to file?",
  "Reference built from primary sources, with a link back to every one of them.",
  [("state-filing.html","What do you file in your state?","The office, the document, the fee, the name search, the registered agent rule and the annual report. Every state also has its own page.","2","all 50 states"),
   ("business-structures.html","Sole proprietor, LLC or S corp","What actually differs, side by side. No recommendation, because that turns on facts a web page does not have.","5","7 rows compared"),
   ("domain-search.html","Is the name still available?","Checked at once against the registries themselves, so the answer is the register's own.","1","12 endings checked")]),
 ("Where am I, and what is next?",
  "Three readings on yourself rather than on a number. All run in the browser and none keep anything.",
  [("assessment.html","The Energy Discovery","Forty eight statements on how you actually behave, and a distribution across all twelve energies rather than a label. Everyone runs on all of them; the question is the proportions.","10","your 12 energies"),
   ("founder-diagnostic.html","Where are you, actually?","Five questions and a straight read on the stage you are at, plus what fits it.","2","your stage"),
   ("business-idea-where-to-start.html","You have an idea. Now what?","Five steps in the order that costs least to be wrong about, and the four places people actually get stuck.","6","a first move")]),
 ("How do I say it?",
  "Answer a few questions, get something back you can use.",
  [("positioning-statement.html","Say what you do in one sentence","The full statement, a bio line, and the version for when somebody asks at a party.","4","3 drafts"),
   ("outreach-email.html","Reach out without the cringe","Six questions and a draft that could only have been sent to one person.","5","an email in your voice")]),
 ("How do I keep going?",
  "The paper worksheets, made fillable. Everything stays in your own browser, so you can close the tab and come back to it.",
  [("weekly-check-in.html","Weekly check-in","Wins, key numbers, what got in the way, next week's top three.","15","saved as you type"),
   ("90-day-goals.html","90-day goals","Reflect, set the vision, pick three priorities, build the weekly rhythm.","25","saved as you type"),
   ("startup-checklist.html","Startup checklist","Five phases ordered by risk, not by paperwork. Progress is remembered.","10","28 steps"),
   ("support-system-checklist.html","Support system checklist","Five kinds of support, fifteen honest questions, and a plan for the gaps.","10","15 questions")]),
]


# Words people type that are not in a title. Without these the filter only
# matches text that happens to be on the card, so "price" finds one tool and
# "tax" finds none.
KEYWORDS = {
 "startup-cost-calculator.html": "cost costs money budget start capital expenses savings how much",
 "breakeven-calculator.html": "breakeven break even profit margin price pricing units volume sales",
 "hourly-rate-calculator.html": "rate price pricing charge hourly freelance day rate salary income tax",
 "product-pricing-calculator.html": "price pricing margin markup cost profit product",
 "state-filing.html": "llc file filing state registration fee articles agent annual report incorporate",
 "business-structures.html": "llc s corp corporation sole proprietor structure entity tax compare legal",
 "domain-search.html": "name domain url website available trademark brand",
 "assessment.html": "quiz test energy energies personality animals discovery strengths",
 "founder-diagnostic.html": "quiz stage where start diagnostic assessment",
 "business-idea-where-to-start.html": "idea start first step stuck beginning validate",
 "positioning-statement.html": "positioning pitch elevator bio describe explain one liner brand",
 "outreach-email.html": "email outreach cold message sales networking contact",
 "weekly-check-in.html": "weekly review check in habit routine tracker",
 "90-day-goals.html": "goals quarter 90 day planning priorities okr targets",
 "startup-checklist.html": "checklist steps launch todo list start",
 "support-system-checklist.html": "support help network people community mentor advisor lonely",
}

# Someone arriving for the first time faces sixteen equal doors. These three
# are the ones that make sense before you know what you are looking for.
START = ["founder-diagnostic.html", "startup-cost-calculator.html", "state-filing.html"]

TRAY = '<div class="hubdiscs"><a class="hubdisc" href="library.html"><span aria-hidden="true" class="hd-disc"><i class="hd-mouth"></i></span><span class="hd-nm">Blogs</span></a><a class="hubdisc" href="resources.html"><span aria-hidden="true" class="hd-disc"><i class="hd-mouth"></i></span><span class="hd-nm">Resource library</span></a><a class="hubdisc on" aria-current="page" href="tools.html"><span aria-hidden="true" class="hd-disc"><i class="hd-mouth"></i></span><span class="hd-nm">Tools</span></a><a class="hubdisc" href="glossary.html"><span aria-hidden="true" class="hd-disc"><i class="hd-mouth"></i></span><span class="hd-nm">Glossary</span></a><a class="hubdisc" href="faq.html"><span aria-hidden="true" class="hd-disc"><i class="hd-mouth"></i></span><span class="hd-nm">FAQs</span></a><a class="hubdisc" href="market-data.html"><span aria-hidden="true" class="hd-disc"><i class="hd-mouth"></i></span><span class="hd-nm">Market data</span></a></div>'

body = [TRAY, '<div class="th">']
# Start here, for someone who has not been to the site before.
_by_href = {c[0]: (c[1], c[3]) for g in GROUPS for c in g[2]}
body.append('<section class="th-start"><h2>New here? Start with one of these</h2>'
            '<div class="th-startrow">'
            + "".join('<a href="%s"><b>%s</b><em>%s min</em></a>'
                      % (e(h), e(_by_href[h][0]), e(_by_href[h][1])) for h in START)
            + '</div></section>')

# Sixteen tools is the point where typing beats scrolling.
body.append('<div class="th-find"><label class="sr-only" for="thq">Filter the tools</label>'
            '<input id="thq" type="search" autocomplete="off" '
            'placeholder="Filter, for example price, LLC or goals"/>'
            '<p class="th-count" id="thcount" role="status"></p></div>')

body.append('<p class="th-note"><b>All of it is open and none of it asks for an email.</b> '
            'The calculators and generators keep nothing at all. The worksheets and checklists save '
            'what you type in your own browser so you can come back to them, which also means they '
            'stay on the device you filled them in on and nobody else can see them.</p>')
n = 0
for gi, (name, blurb, cards) in enumerate(GROUPS):
    cls = "th-g g%d n%d" % (gi + 1, len(cards))
    body.append('<section class="%s"><h2>%s</h2><p>%s</p><div class="th-cards">'
                % (cls, e(name), e(blurb)))
    for href, title, desc, fig, unit in cards:
        n += 1
        zoo = ""
        if href == "assessment.html":
            zoo = ('<span aria-hidden="true" class="th-zoo">'
                   + "".join('<img alt="" decoding="async" height="200" loading="lazy" '
                             'src="assets/energies/%s-sm.webp" width="200"/>' % a for a in ZOO)
                   + '</span>')
        body.append('<a class="th-c%s" data-n="%02d" href="%s" '
                    'data-find="%s">%s<b>%s</b><span>%s</span>'
                    '<span class="th-s"><em>%s min</em><i>%s</i></span></a>'
                    % (" th-hero" if zoo else "", n, e(href),
                       e((title + " " + desc + " " + name + " " + KEYWORDS.get(href, "")).lower()), zoo,
                       e(title), e(desc), e(fig), e(unit)))
    body.append("</div></section>")
body.append("</div>")

count = sum(len(g[2]) for g in GROUPS)
# Counted from GROUPS rather than typed, because a hand written count goes
# wrong the first time a tool is added and nobody notices.
WORDS = {11:"Eleven",12:"Twelve",13:"Thirteen",14:"Fourteen",15:"Fifteen",
         16:"Sixteen",17:"Seventeen",18:"Eighteen",19:"Nineteen",20:"Twenty"}
_n = sum(len(g[2]) for g in GROUPS)
_word = WORDS.get(_n, str(_n))
DESC = ("%s tools for people starting something: calculators, a fifty state filing "
        "lookup, a domain checker, and worksheets that save your progress." % _word)
items = [{"@type":"ListItem","position":i+1,"url":f"{SITE}/{h}","name":t}
         for i,(h,t,_,_,_) in enumerate([c for g in GROUPS for c in g[2]])]
sch = ({"@context":"https://schema.org","@type":"CollectionPage",
        "@id":f"{SITE}/tools.html#page","url":f"{SITE}/tools.html","name":"Tools",
        "description":DESC,"isPartOf":{"@id":f"{SITE}/#website"},
        "mainEntity":{"@type":"ItemList","numberOfItems":count,"itemListElement":items}},
       faqpage([
        ("Do these tools cost anything?","No. There is no account, no email step and no payment. Everything runs in your browser."),
        ("Is anything I type saved or sent?","The calculators and generators keep nothing at all. The worksheets and checklists save your answers in your own browser so you can return to them, which means they stay on that device and nothing is sent anywhere."),
        ("Can I use these on a phone?","Yes. Every tool works on a phone, and the worksheets print and download from there as well.")]),
       {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"Home","item":f"{SITE}/"},
        {"@type":"ListItem","position":2,"name":"Resources","item":f"{SITE}/library.html"},
        {"@type":"ListItem","position":3,"name":"Tools","item":f"{SITE}/tools.html"}]})

JS = r"""
var q = document.getElementById('thq');
var count = document.getElementById('thcount');
if(q){
  var cards = [].slice.call(document.querySelectorAll('.th-c'));
  var groups = [].slice.call(document.querySelectorAll('.th-g'));
  var start = document.querySelector('.th-start');
  var total = cards.length;

  function apply(){
    var term = q.value.trim().toLowerCase();
    var shown = 0;
    cards.forEach(function(c){
      var hit = !term || (c.getAttribute('data-find') || '').indexOf(term) > -1;
      c.hidden = !hit;
      if(hit) shown++;
    });
    /* a group with nothing left in it should not leave its heading behind */
    groups.forEach(function(g){
      g.hidden = !g.querySelector('.th-c:not([hidden])');
    });
    if(start) start.hidden = !!term;
    count.textContent = term
      ? (shown ? shown + ' of ' + total + ' tools' : 'Nothing matches ' + term)
      : '';
  }
  q.addEventListener('input', apply);
  q.addEventListener('search', apply);
  /* Escape clears, which is what the native search field implies */
  q.addEventListener('keydown', function(ev){
    if(ev.key === 'Escape'){ q.value = ''; apply(); }
  });
}
"""

BACK = ('<p class="kx-backrow"><a class="kx-bk" href="library.html">'
        '<svg aria-hidden="true" focusable="false" viewbox="0 0 24 24">'
        '<path d="M15 5l-7 7 7 7"></path></svg> Back to Resources</a></p>')

n = page("tools.html", "Business Tools: Calculators, Worksheets and Lookups | SideKix",
         DESC, "Tools", "%s things that <em>do the work</em>." % _word,
         "Calculators that give you a number, lookups that tell you what applies where you are, "
         "and worksheets that remember what you wrote. No account, no email, nothing sent anywhere.",
         "".join(body), css=CSS, js=JS, schema=sch, back=BACK)
print("tools.html %.0f KB, %d tools in %d groups" % (n/1024, count, len(GROUPS)))
