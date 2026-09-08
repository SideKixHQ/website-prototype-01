# -*- coding: utf-8 -*-
import io, os, re, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
SITE = "https://sidekixhq.com"

TOOLS = [
 ("tools.html","Business Tools: Calculators, Worksheets and Lookups | SideKix",
  "Fourteen free tools for people starting something: calculators, a fifty state filing lookup, a domain checker, fillable worksheets and checklists that remember your progress. No account and no email.","weekly"),
 ("startup-cost-calculator.html","Startup Cost Calculator: What It Costs to Start | SideKix",
  "Add your one-off costs and monthly running costs and see what you need before you open. Nothing saved, nothing sent, no account.","monthly"),
 ("breakeven-calculator.html","Breakeven Calculator: Units and Revenue | SideKix",
  "Enter fixed costs, price and variable cost per sale to see the units and the revenue you need to cover them.","monthly"),
 ("hourly-rate-calculator.html","Hourly Rate Calculator for Freelancers | SideKix",
  "Works back from the income you want and the hours you can actually bill, not the hours you work.","monthly"),
 ("product-pricing-calculator.html","Product Pricing Calculator: Margin and Fees | SideKix",
  "Works back from the margin you want, with materials, labour, overhead and payment fees included.","monthly"),
 ("state-filing.html","What Do I File in My State? LLC Lookup for All 50 | SideKix",
  "What you file to start an LLC in any US state: the office, the form, the fee, the name search and the annual report. Every figure linked to its source.","monthly"),
 ("business-structures.html","Sole Proprietor vs LLC vs S Corp: Side by Side | SideKix",
  "Sole proprietor, LLC and S corporation compared on what differs: liability, taxes, ownership limits, cost and ongoing work. Reference, not advice.","monthly"),
 ("domain-search.html","Business Name Domain Checker: 12 Endings at Once | SideKix",
  "Check a business name across a dozen domain endings at once, against the registries themselves. No account and nothing stored.","monthly"),
 ("founder-diagnostic.html","Founder Diagnostic: Where Are You Actually? | SideKix",
  "Five questions and a straight read on where your business actually is, plus the things on this site that fit that stage.","monthly"),
 ("positioning-statement.html","Positioning Statement Generator | SideKix",
  "Answer five questions and get a positioning statement you can edit, plus a bio line and a one-sentence answer for when somebody asks what you do.","monthly"),
 ("outreach-email.html","Outreach Email Generator: Reach Out Without the Cringe | SideKix",
  "Six questions and a short outreach email that sounds like a person: how you found them, the specific thing you noticed, who you are and one clear ask.","monthly"),
 ("weekly-check-in.html","Weekly Business Check-In: Fillable Worksheet | SideKix",
  "A fillable weekly business check-in. Wins, key numbers, progress, what got in the way and next week's top three. Saves in your browser, prints, downloads.","monthly"),
 ("90-day-goals.html","90-Day Goals: Fillable Worksheet | SideKix",
  "A fillable 90-day goal-setting worksheet. Reflect, set a vision, pick three priorities and build the weekly rhythm.","monthly"),
 ("startup-checklist.html","Business Startup Checklist: Tick and Track | SideKix",
  "An interactive business startup checklist in five phases ordered by risk: decide, validate, set up, build, sell. Remembers your progress.","monthly"),
 ("support-system-checklist.html","Support System Checklist for Founders | SideKix",
  "An interactive support system checklist for founders: personal, peer, expertise, resource and community support, with a gap plan.","monthly"),
]

# ---------------- sitemap ----------------
sm = io.open("sitemap.xml", encoding="utf-8").read()
have = set(re.findall(r"<loc>([^<]+)</loc>", sm))
anchor = re.search(r"  <url>\s*<loc>https://sidekixhq\.com/tools\.html</loc>.*?</url>\n", sm, re.S)
add = []
for f, _t, _d, freq in TOOLS:
    url = f"{SITE}/{f}"
    if url in have:
        continue
    add.append("  <url>\n    <loc>%s</loc>\n    <lastmod>2026-09-05</lastmod>\n"
               "    <changefreq>%s</changefreq>\n    <priority>0.9</priority>\n  </url>\n" % (url, freq))
if add:
    sm = sm[:anchor.end()] + "".join(add) + sm[anchor.end():]
    io.open("sitemap.xml", "w", encoding="utf-8").write(sm)
print("sitemap: %d added, %d urls total" % (len(add), sm.count("<loc>")))

# ---------------- llms.txt ----------------
lm = io.open("llms.txt", encoding="utf-8").read()
old = re.search(r"- \[Free Business Calculators[^\n]*\n", lm)
lines = []
for f, t, d, _ in TOOLS:
    lines.append("- [%s](%s/%s): %s\n" % (t, SITE, f, d))
if old:
    lm = lm[:old.start()] + "".join(lines) + lm[old.end():]
    io.open("llms.txt", "w", encoding="utf-8").write(lm)
print("llms.txt: %d tool entries" % len(lines))

# ---------------- the Resources hub points at Tools ----------------
lib = io.open("library.html", encoding="utf-8").read()
print("library.html links tools.html:", "tools.html" in lib)
