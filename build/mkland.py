# -*- coding: utf-8 -*-
"""Two landing pages aimed at searches the head term cannot reach.

"How to start a business" is held by usa.gov, the IRS, the SBA, JPMorgan and
Salesforce. That page is not winnable and chasing it wastes the content.

These two are winnable. The first answers the question people actually type
when they are stuck, where the current results are Quora threads and a UK
borough council. The second is local, where the competition is a chamber of
commerce and a regional bank, and where SideKix has real state data to stand on.

Both answer the question in the first paragraph, because that is what an answer
engine quotes and what a reader came for.
"""
import os, sys, io, json, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from toolgen import page, SITE

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def e(s): return html.escape(str(s), quote=True)

NC = json.load(io.open(os.path.join(ROOT, "build", "state-filings.json"),
                       encoding="utf-8"))["states"]["North Carolina"]

CSS = """
.ld{max-width:46rem;margin:0 auto}
.ld .answer{margin:0 0 34px;padding:22px 24px;border-left:3px solid #D4A856;
  background:rgba(212,168,86,.06);border-radius:0 12px 12px 0}
.ld .answer p{margin:0;font-size:17.5px;line-height:1.7;color:#E8DEC4}
.ld h2{font-size:clamp(21px,3vw,26px);color:#FFF8D8;margin:46px 0 12px;
  font-family:Georgia,serif;font-weight:600;line-height:1.25}
.ld h3{font-size:17px;color:#F3E4A8;margin:28px 0 8px;font-weight:700}
.ld p{font-size:16.5px;line-height:1.78;color:#CFC7B4;margin:0 0 16px}
.ld ul,.ld ol{margin:0 0 18px;padding:0 0 0 1.1em;color:#CFC7B4}
.ld li{font-size:16.5px;line-height:1.72;margin:0 0 9px}
.ld a{color:#F3E4A8}
.ld .steps{list-style:none;counter-reset:s;padding:0;margin:0 0 12px}
.ld .steps>li{counter-increment:s;position:relative;padding:0 0 0 52px;margin:0 0 26px}
.ld .steps>li::before{content:counter(s);position:absolute;left:0;top:-2px;
  width:34px;height:34px;border-radius:50%;display:flex;align-items:center;
  justify-content:center;font-family:var(--util,inherit);font-size:14px;
  font-weight:700;color:#1B1400;background:linear-gradient(180deg,#D7C582,#A1853E)}
.ld .steps b{display:block;color:#FFF8D8;font-size:17.5px;margin:0 0 5px}
.ld table{width:100%;border-collapse:collapse;margin:0 0 20px;font-size:15.5px}
.ld th,.ld td{text-align:left;padding:12px 14px;border-bottom:1px solid rgba(212,168,86,.18);
  color:#CFC7B4;vertical-align:top}
.ld th{color:#BDB4A4;font-family:var(--util,inherit);font-size:11px;
  letter-spacing:.14em;text-transform:uppercase;font-weight:700}
.ld td b{color:#F3E4A8}
.ld .tblwrap{overflow-x:auto;-webkit-overflow-scrolling:touch}
.ld .src{font-size:13.5px;color:#9C9484;line-height:1.6;margin:0 0 26px}
.ld .cards{display:grid;grid-template-columns:repeat(2,1fr);gap:14px;margin:0 0 26px}
.ld .cards a{display:block;padding:18px 20px;border-radius:14px;text-decoration:none;
  border:1px solid rgba(212,168,86,.28);background:rgba(212,168,86,.05)}
.ld .cards a:hover{border-color:#D4A856;background:rgba(212,168,86,.12)}
.ld .cards b{display:block;color:#FFF8D8;font-size:16px;margin:0 0 4px}
.ld .cards span{color:#BDB4A4;font-size:14px;line-height:1.55}
@media(max-width:620px){.ld .cards{grid-template-columns:1fr}}
"""


def faq_schema(pairs, url):
    return {"@context": "https://schema.org", "@type": "FAQPage",
            "url": url,
            "mainEntity": [{"@type": "Question", "name": q,
                            "acceptedAnswer": {"@type": "Answer", "text": a}}
                           for q, a in pairs]}


def howto(name, desc, steps, url):
    return {"@context": "https://schema.org", "@type": "HowTo",
            "name": name, "description": desc, "url": url,
            "step": [{"@type": "HowToStep", "position": i + 1,
                      "name": s[0], "text": s[1]} for i, s in enumerate(steps)]}


def cards(items):
    return '<div class="cards">%s</div>' % "".join(
        '<a href="%s"><b>%s</b><span>%s</span></a>' % (h, e(t), e(d)) for h, t, d in items)


# ---------------------------------------------------------------- page one
def build_idea():
    fn = "business-idea-where-to-start.html"
    url = "%s/%s" % (SITE, fn)

    STEPS = [
     ("Write the idea down in one sentence",
      "Name who it is for and what changes for them. If the sentence needs a paragraph "
      "to make sense, the idea is still two or three ideas wearing a coat. Most people "
      "skip this because it feels too small to count as progress. It is the step that "
      "makes every later step answerable."),
     ("Say it out loud to five people who are not your friends",
      "Friends protect your feelings, which is the wrong input here. Look for the "
      "question you cannot answer. That question is the next piece of work, and it "
      "arrives faster from a stranger."),
     ("Find out what it costs before you find out what it earns",
      "Costs are knowable this week. Revenue is a guess for months. Knowing the number "
      "you need to survive turns a vague fear into a figure you can plan against."),
     ("Sell one before you build ten",
      "One person paying is worth more information than a hundred saying it sounds "
      "great. It also tells you the price, which no amount of thinking will."),
     ("Register only once money is moving",
      "The paperwork is real but it is rarely the first step. Filing early creates "
      "annual obligations for a business that may not exist yet."),
    ]

    FAQ = [
     ("I have a business idea but I do not know where to start. What do I do first?",
      "Write the idea in one sentence naming who it is for and what changes for them, "
      "then say it to five people who are not friends and listen for the question you "
      "cannot answer. That question is the next piece of work. Registering the business "
      "and building the product both come later, once someone has agreed to pay."),
     ("How do I know if my business idea is any good?",
      "The test is whether a stranger will pay before the thing is finished. Interest is "
      "cheap and encouragement is free. A deposit, a pre-order or a signed agreement is "
      "the first real evidence, and it usually arrives long before the product does."),
     ("Do I need a business plan to start?",
      "Not to start. A plan is needed when someone else needs to evaluate you, which "
      "usually means a lender or an investor. Before that, a page naming the customer, "
      "the price and the cost does the same work."),
     ("How much money do I need to start a business?",
      "It varies by what you are building, and the number that matters is not the "
      "startup cost but the point at which sales cover fixed costs. That figure is "
      "calculable in a few minutes once you know your fixed costs and what each sale "
      "contributes."),
     ("Should I register an LLC before I have customers?",
      "An LLC creates filing duties and annual fees from the moment it exists. Most "
      "states charge an annual report whether or not the business traded. Many people "
      "register once money is actually moving, though the answer turns on liability "
      "and tax facts a web page does not have."),
     ("What if my idea already exists?",
      "Almost every idea already exists. Competition is evidence that people pay for "
      "the thing. What matters is whether you can reach a group of them better, cheaper "
      "or more specifically than whoever is serving them now."),
    ]

    b = ['<div class="ld">']
    b.append('<div class="answer"><p>Write the idea down in one sentence naming who it is '
             'for and what changes for them. Then say it out loud to five people who are '
             'not your friends, and listen for the question you cannot answer. That '
             'question is your next piece of work. Everything else, the name, the logo, '
             'the website, the registration, comes after somebody has agreed to pay.</p></div>')
    b.append('<p>The gap between having an idea and starting is not usually a knowledge gap. '
             'The steps are published in a hundred places. It is that the first move is '
             'unclear, so every move looks equally urgent, and doing nothing feels safer '
             'than doing the wrong thing first.</p>')
    b.append('<p>What follows is an order. It is ordered by risk, which means the cheapest '
             'ways to be wrong come first.</p>')

    b.append('<h2>Five steps, in the order that costs least</h2><ol class="steps">')
    for t, d in STEPS:
        b.append('<li><b>%s</b>%s</li>' % (e(t), e(d)))
    b.append('</ol>')

    b.append('<h2>Where people actually get stuck</h2>')
    b.append('<h3>Waiting to feel ready</h3>'
             '<p>Readiness is not a feeling that arrives before the work. It is produced by '
             'the work. The people who look ready started before they felt it and got used '
             'to the discomfort on the way.</p>')
    b.append('<h3>Researching instead of asking</h3>'
             '<p>Reading has no failure state, which is what makes it comfortable. A week of '
             'research and one honest conversation with a potential customer are not '
             'equivalent, and only one of them can tell you the price.</p>')
    b.append('<h3>Building the whole thing first</h3>'
             '<p>A finished product built on a guess is an expensive way to test the guess. '
             'The order that costs less is to sell it, then build it.</p>')
    b.append('<h3>Doing it alone</h3>'
             '<p>Most of the difficulty is not technical. It is that no one is checking in, '
             'nobody notices when a week goes missing, and there is no one to ask whether '
             'a decision is reasonable.</p>')

    b.append('<h2>Things on this site that answer the next question</h2>')
    b.append(cards([
      ("founder-diagnostic.html", "Where are you, actually?",
       "Five questions and a straight read on the stage you are at."),
      ("startup-cost-calculator.html", "What will it cost to start?",
       "The real number, before revenue is a guess."),
      ("breakeven-calculator.html", "When do you break even?",
       "The point where sales cover the fixed costs."),
      ("business-structures.html", "Sole proprietor, LLC or S corp",
       "What actually differs, side by side."),
      ("state-filing.html", "What your state requires",
       "All fifty, each read from the state's own page."),
      ("assessment.html", "The Energy Discovery",
       "Forty eight questions on how you work when it is hard."),
    ]))

    schema = [faq_schema(FAQ, url),
              howto("What to do when you have a business idea and do not know where to start",
                    "Five steps ordered by risk, from writing the idea in one sentence to "
                    "registering once money is moving.",
                    STEPS, url)]

    b.append("</div>")
    n = page(fn,
             "I Have a Business Idea but Do Not Know Where to Start | SideKix",
             "The first move when you have a business idea and no idea what to do with it. "
             "Five steps ordered by risk, and the four places people get stuck.",
             "Where to start",
             "I have an idea.<br/>Now what?",
             "The steps are not the hard part. Knowing which one is first is the hard part. "
             "Here is an order, arranged so the cheapest ways to be wrong happen first.",
             "".join(b), css=CSS, schema=schema, wrapcls="wrap res",
             back=('<p class="kx-backrow"><a class="kx-bk" href="index.html">'
                   '<svg aria-hidden="true" focusable="false" viewbox="0 0 24 24">'
                   '<path d="M15 5l-7 7 7 7"></path></svg> Back to SideKix</a></p>'))
    print("%s  %d KB" % (fn, n // 1024))


# ---------------------------------------------------------------- page two
def build_nc():
    fn = "start-a-business-in-north-carolina.html"
    url = "%s/%s" % (SITE, fn)
    ar = NC["annual_report"]

    STEPS = [
     ("Check the name is free",
      "Search the Secretary of State register before anything else. A name that is already "
      "taken invalidates the filing and the fee is not returned."),
     ("Decide on the structure",
      "Sole proprietor, LLC or corporation. The choice changes what you file, what you pay "
      "and what you are personally liable for. It is worth understanding before filing, "
      "because changing it later means filing again."),
     ("Name a registered agent",
      "North Carolina requires one. " + NC["registered_agent_note"]),
     ("File the Articles of Organization",
      "Form L-01, filed with the Business Registration Division. The state fee is "
      "$%d." % NC["llc_fee_usd"]),
     ("Register for state taxes",
      "The Department of Revenue handles sales and use tax and withholding. Which of them "
      "apply turns on what you sell and whether you employ anyone."),
     ("Diarise the annual report",
      "Due %s" % ar["due"]),
    ]

    FAQ = [
     ("How much does it cost to start an LLC in North Carolina?",
      "The state filing fee for Articles of Organization is $%d. After that, an annual "
      "report is due every year: $%d on paper, or $%d online because of a $3 electronic "
      "transaction fee." % (NC["llc_fee_usd"], 200, ar["fee_usd"])),
     ("What form do I file to start an LLC in North Carolina?",
      "Articles of Organization, Form L-01, filed with the North Carolina Department of "
      "the Secretary of State, Business Registration Division."),
     ("When is the North Carolina annual report due?",
      ar["due"]),
     ("Do I need a registered agent in North Carolina?",
      "Yes. " + NC["registered_agent_note"]),
     ("How many small businesses are in North Carolina?",
      "About 1.1 million, which is 99.6% of all businesses in the state. They employ 1.8 "
      "million people, or 44.2% of the state's workforce, according to the SBA Office of "
      "Advocacy 2025 Small Business Profiles."),
     ("Can I start a business in North Carolina without an LLC?",
      "Yes. A sole proprietorship needs no formation filing with the Secretary of State, "
      "though local privilege licences, an assumed name certificate at the county register "
      "of deeds, and state tax registration may still apply. The trade off is that there "
      "is no liability separation between you and the business."),
    ]

    b = ['<div class="ld">']
    b.append('<div class="answer"><p>To form an LLC in North Carolina you file Articles of '
             'Organization, Form L-01, with the Secretary of State for $%d, having first '
             'checked the name is free and named a registered agent with a staffed physical '
             'address in the state. After that an annual report is due %s</p></div>'
             % (NC["llc_fee_usd"], ar["due"][0].lower() + ar["due"][1:]))

    b.append('<p>North Carolina has about 1.1 million small businesses, which is 99.6% of '
             'every business in the state. They employ 1.8 million people, or 44.2% of the '
             'workforce. Whatever you are starting, you are not doing anything unusual '
             'here.</p>')

    b.append('<h2>What it costs</h2><div class="tblwrap"><table>'
             '<thead><tr><th>What</th><th>Amount</th><th>When</th></tr></thead><tbody>'
             '<tr><td><b>Articles of Organization</b><br/>Form L-01</td><td>$%d</td>'
             '<td>Once, at formation</td></tr>'
             '<tr><td><b>Annual report</b><br/>Paper filing</td><td>$200</td>'
             '<td>%s</td></tr>'
             '<tr><td><b>Annual report</b><br/>Online filing</td><td>$%d</td>'
             '<td>The same date, with a $3 electronic transaction fee</td></tr>'
             '</tbody></table></div>'
             % (NC["llc_fee_usd"], e(ar["due"]), ar["fee_usd"]))
    b.append('<p class="src">Every figure on this page was read from the North Carolina '
             'Secretary of State and Department of Revenue between 4 and 5 September 2026. '
             'Fees change, so check the state page before you file.</p>')

    b.append('<h2>The order to do it in</h2><ol class="steps">')
    for t, d in STEPS:
        b.append('<li><b>%s</b>%s</li>' % (e(t), e(d)))
    b.append('</ol>')

    b.append('<h2>The official pages</h2><ul>')
    for label, href in [
        ("Business Registration Division, Secretary of State", NC["agency_url"]),
        ("Search the register for your name", NC["name_search_url"]),
        ("File Articles of Organization online", NC["llc_filing_url"]),
        ("Annual report filing and due dates", ar["url"]),
        ("Register a business with the Department of Revenue",
         "https://www.ncdor.gov/taxes-forms/register-business"),
    ]:
        b.append('<li><a href="%s" rel="noopener" target="_blank">%s</a></li>' % (e(href), e(label)))
    b.append('</ul>')
    b.append('<p class="src">These are state and federal pages. SideKix has no relationship '
             'with any of them and takes nothing for sending you there.</p>')

    b.append('<h2>Before you file</h2>')
    b.append(cards([
      ("business-structures.html", "Sole proprietor, LLC or S corp",
       "What actually differs, side by side, with no recommendation."),
      ("startup-cost-calculator.html", "What will it cost to start?",
       "Filing fees are the small part. This is the rest."),
      ("domain-search.html", "Is the name still available?",
       "Checked against the registries themselves."),
      ("state-filing.html", "The other forty nine states",
       "Same detail, each read from that state's own page."),
    ]))

    b.append("</div>")
    schema = [faq_schema(FAQ, url),
              howto("How to start a business in North Carolina",
                    "Name search, structure, registered agent, Articles of Organization, "
                    "state tax registration and the annual report.", STEPS, url)]

    n = page(fn,
             "How to Start a Business in North Carolina: Cost, Forms and Steps | SideKix",
             "Form L-01 costs $125 and the annual report is due April 15. Every fee and "
             "form read from the North Carolina Secretary of State, with the dates checked.",
             "North Carolina",
             "Starting a business in <em>North Carolina</em>",
             "What it costs, what you file and in what order. Every figure below came from "
             "the state's own pages, with the date it was checked.",
             "".join(b), css=CSS, schema=schema, wrapcls="wrap res",
             back=('<p class="kx-backrow"><a class="kx-bk" href="state-filing.html">'
                   '<svg aria-hidden="true" focusable="false" viewbox="0 0 24 24">'
                   '<path d="M15 5l-7 7 7 7"></path></svg> Back to state filing</a></p>'))
    print("%s  %d KB" % (fn, n // 1024))


if __name__ == "__main__":
    build_idea()
    build_nc()
