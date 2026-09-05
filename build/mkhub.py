# -*- coding: utf-8 -*-
import os, sys, json, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from toolgen import page, crumbs, webapp, faqpage, SITE
def e(s): return html.escape(str(s), quote=True)

CSS = """
/* ---- the tools hub ----
   A card per tool, grouped by what you are trying to do rather than by what
   kind of thing it is, because somebody arriving here knows their problem and
   not our taxonomy. */
.th{max-width:1060px;margin:0 auto}
.th-g{margin:0 0 52px}
.th-g > h2{font-family:var(--util);font-size:11px;letter-spacing:.2em;text-transform:uppercase;
  color:var(--gold);margin:0 0 4px}
.th-g > p{color:#9C968D;font-size:15px;margin:0 0 20px;max-width:60ch}
.th-cards{display:grid;gap:14px;grid-template-columns:repeat(auto-fit,minmax(min(300px,100%),1fr))}
.th-c{position:relative;display:block;min-width:0;text-decoration:none;
  border:1px solid rgba(212,168,86,.22);border-radius:16px;padding:24px 22px 22px;
  background:radial-gradient(120% 120% at 50% 0,rgba(33,26,10,.5),rgba(12,11,8,.72));
  transition:border-color .3s,transform .3s}
.th-c:hover{border-color:rgba(212,168,86,.6);transform:translateY(-3px)}
.th-c:focus-visible{outline:3px solid #F3E4A8;outline-offset:3px}
.th-c b{display:block;font-family:var(--display);font-size:23px;line-height:1.15;
  color:#FFF8E8;margin:0 0 8px}
.th-c span{display:block;font-size:15px;line-height:1.65;color:#9C968D}
.th-c i{display:inline-block;font-style:normal;font-family:var(--util);font-size:9.5px;
  letter-spacing:.16em;text-transform:uppercase;color:var(--gold);
  border:1px solid rgba(212,168,86,.3);border-radius:99px;padding:4px 10px;margin:14px 0 0}
.th-note{border:1px solid rgba(212,168,86,.2);border-radius:13px;padding:18px 20px;
  font-size:14.5px;line-height:1.75;color:#9C968D;margin:0 0 46px}
.th-note b{color:#E8DEC4;font-weight:600}
"""

GROUPS = [
 ("Work out a number",
  "Four calculators. Change a figure and the answer moves. Nothing is saved and nothing is sent.",
  [("startup-cost-calculator.html","What will it cost to start?","One-off costs to open plus the months of running costs you need behind you.","Calculator"),
   ("breakeven-calculator.html","When do you break even?","Fixed costs divided by what each sale contributes, in units and in revenue.","Calculator"),
   ("hourly-rate-calculator.html","What should you charge an hour?","Worked back from the income you want and the hours you can actually bill.","Calculator"),
   ("product-pricing-calculator.html","What should you price a product at?","From the margin you want, with materials, labour, overhead and payment fees taken out.","Calculator")]),
 ("Find out what applies to you",
  "Reference built from primary sources, with a link back to every one of them.",
  [("state-filing.html","What do you file in your state?","All fifty states: the office, the document, the fee, the name search, the registered agent rule and the annual report.","Lookup"),
   ("business-structures.html","Sole proprietor, LLC or S corp","Seven rows on what actually differs. No recommendation, because that turns on facts a web page does not have.","Comparison"),
   ("domain-search.html","Is the name actually free?","A dozen domain endings checked at once, against the registries themselves.","Lookup")]),
 ("Work something out about yourself",
  "Answer a few questions, get something back you can use.",
  [("founder-diagnostic.html","Where are you, actually?","Five questions and a straight read on the stage you are at, plus what fits it.","Diagnostic"),
   ("positioning-statement.html","Say what you do in one sentence","Five questions, three drafts: the full statement, a bio line, and the party version.","Generator"),
   ("outreach-email.html","Reach out without the cringe","Six questions and a draft that could only have been sent to one person.","Generator")]),
 ("Fill it in and keep it",
  "The paper worksheets, made fillable. Everything stays in your own browser, so you can close the tab and come back to it.",
  [("weekly-check-in.html","Weekly check-in","Wins, key numbers, what got in the way, next week's top three. Fifteen minutes.","Worksheet"),
   ("90-day-goals.html","90-day goals","Reflect, set the vision, pick three priorities, build the weekly rhythm.","Worksheet"),
   ("startup-checklist.html","Startup checklist","Five phases ordered by risk, not by paperwork. Progress is remembered.","Checklist"),
   ("support-system-checklist.html","Support system checklist","Five kinds of support, fifteen honest questions, and a plan for the gaps.","Checklist")]),
]

body = ['<div class="th">']
body.append('<p class="th-note"><b>All of it is free and none of it asks for an email.</b> '
            'The calculators and generators keep nothing at all. The worksheets and checklists save '
            'what you type in your own browser so you can come back to them, which also means they '
            'stay on the device you filled them in on and nobody else can see them.</p>')
for name, blurb, cards in GROUPS:
    body.append('<section class="th-g"><h2>%s</h2><p>%s</p><div class="th-cards">' % (e(name), e(blurb)))
    for href, title, desc, kind in cards:
        body.append('<a class="th-c" href="%s"><b>%s</b><span>%s</span><i>%s</i></a>'
                    % (e(href), e(title), e(desc), e(kind)))
    body.append("</div></section>")
body.append("</div>")

count = sum(len(g[2]) for g in GROUPS)
DESC = ("Fourteen free tools for people starting something: calculators, a fifty state filing "
        "lookup, a domain checker, fillable worksheets and checklists that remember your progress. "
        "No account and no email.")
items = [{"@type":"ListItem","position":i+1,"url":f"{SITE}/{h}","name":t}
         for i,(h,t,_,_) in enumerate([c for g in GROUPS for c in g[2]])]
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

n = page("tools.html", "Free Business Tools: Calculators, Worksheets, Lookups | SideKix",
         DESC, "Tools", "Fourteen things that <em>do the work</em>.",
         "Calculators that give you a number, lookups that tell you what applies where you are, "
         "and worksheets that remember what you wrote. No account, no email, nothing sent anywhere.",
         "".join(body), css=CSS, schema=sch, back=BACK)
print("tools.html %.0f KB, %d tools in %d groups" % (n/1024, count, len(GROUPS)))
