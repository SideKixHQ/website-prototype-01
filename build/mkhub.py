# -*- coding: utf-8 -*-
import os, sys, json, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from toolgen import page, crumbs, webapp, faqpage, SITE
def e(s): return html.escape(str(s), quote=True)

CSS = """
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

GROUPS = [
 ("Work out where you are",
  "Two ways to get a reading on yourself rather than on a number. Both run in the browser and neither keeps anything.",
  [("assessment.html","The Energy Discovery","Forty eight statements on how you actually behave, and a distribution across all twelve energies rather than a label. Everyone runs on all of them; the question is the proportions.","12","energies"),
   ("founder-diagnostic.html","Where are you, actually?","Five questions and a straight read on the stage you are at, plus what fits it.","5","questions")]),
 ("Work out a number",
  "Four calculators. Change a figure and the answer moves. Nothing is saved and nothing is sent.",
  [("startup-cost-calculator.html","What will it cost to start?","One-off costs to open plus the months of running costs you need behind you.","11","inputs"),
   ("breakeven-calculator.html","When do you break even?","Fixed costs divided by what each sale contributes, in units and in revenue.","3","inputs"),
   ("hourly-rate-calculator.html","What should you charge an hour?","Worked back from the income you want and the hours you can actually bill.","5","inputs"),
   ("product-pricing-calculator.html","What should you price a product at?","From the margin you want, with materials, labour, overhead and payment fees taken out.","5","inputs")]),
 ("Find out what applies to you",
  "Reference built from primary sources, with a link back to every one of them.",
  [("state-filing.html","What do you file in your state?","The office, the document, the fee, the name search, the registered agent rule and the annual report.","50","states"),
   ("business-structures.html","Sole proprietor, LLC or S corp","What actually differs, side by side. No recommendation, because that turns on facts a web page does not have.","7","rows compared"),
   ("domain-search.html","Is the name still available?","Checked at once against the registries themselves, so the answer is the register's own.","12","endings"),
   ("business-idea-where-to-start.html","You have an idea. Now what?","Five steps in the order that costs least to be wrong about, and the four places people actually get stuck.","5","steps")]),
 ("Work something out about yourself",
  "Answer a few questions, get something back you can use.",
  [("positioning-statement.html","Say what you do in one sentence","The full statement, a bio line, and the version for when somebody asks at a party.","3","drafts"),
   ("outreach-email.html","Reach out without the cringe","Six questions and a draft that could only have been sent to one person.","1","email that sounds like you")]),
 ("Fill it in and keep it",
  "The paper worksheets, made fillable. Everything stays in your own browser, so you can close the tab and come back to it.",
  [("weekly-check-in.html","Weekly check-in","Wins, key numbers, what got in the way, next week's top three. Fifteen minutes.","31","fields, saved as you type"),
   ("90-day-goals.html","90-day goals","Reflect, set the vision, pick three priorities, build the weekly rhythm.","32","fields, saved as you type"),
   ("startup-checklist.html","Startup checklist","Five phases ordered by risk, not by paperwork. Progress is remembered.","28","steps"),
   ("support-system-checklist.html","Support system checklist","Five kinds of support, fifteen honest questions, and a plan for the gaps.","15","questions")]),
]

TRAY = '<div class="hubdiscs"><a class="hubdisc" href="library.html"><span aria-hidden="true" class="hd-disc"><i class="hd-mouth"></i></span><span class="hd-nm">Blogs</span></a><a class="hubdisc" href="resources.html"><span aria-hidden="true" class="hd-disc"><i class="hd-mouth"></i></span><span class="hd-nm">Resource library</span></a><a class="hubdisc on" aria-current="page" href="tools.html"><span aria-hidden="true" class="hd-disc"><i class="hd-mouth"></i></span><span class="hd-nm">Tools</span></a><a class="hubdisc" href="glossary.html"><span aria-hidden="true" class="hd-disc"><i class="hd-mouth"></i></span><span class="hd-nm">Glossary</span></a><a class="hubdisc" href="faq.html"><span aria-hidden="true" class="hd-disc"><i class="hd-mouth"></i></span><span class="hd-nm">FAQs</span></a><a class="hubdisc" href="market-data.html"><span aria-hidden="true" class="hd-disc"><i class="hd-mouth"></i></span><span class="hd-nm">Market data</span></a></div>'

body = [TRAY, '<div class="th">']
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
        body.append('<a class="th-c%s" data-n="%02d" href="%s">%s<b>%s</b><span>%s</span>'
                    '<span class="th-s"><em>%s</em><i>%s</i></span></a>'
                    % (" th-hero" if zoo else "", n, e(href), zoo,
                       e(title), e(desc), e(fig), e(unit)))
    body.append("</div></section>")
body.append("</div>")

count = sum(len(g[2]) for g in GROUPS)
DESC = ("Fourteen tools for people starting something: calculators, a fifty state filing lookup, "
        "a domain checker, and worksheets that save your progress.")
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

BACK = ('<p class="kx-backrow"><a class="kx-bk" href="library.html">'
        '<svg aria-hidden="true" focusable="false" viewbox="0 0 24 24">'
        '<path d="M15 5l-7 7 7 7"></path></svg> Back to Resources</a></p>')

n = page("tools.html", "Business Tools: Calculators, Worksheets and Lookups | SideKix",
         DESC, "Tools", "Fourteen things that <em>do the work</em>.",
         "Calculators that give you a number, lookups that tell you what applies where you are, "
         "and worksheets that remember what you wrote. No account, no email, nothing sent anywhere.",
         "".join(body), css=CSS, schema=sch, back=BACK)
print("tools.html %.0f KB, %d tools in %d groups" % (n/1024, count, len(GROUPS)))
