# -*- coding: utf-8 -*-
"""One page per business somebody is thinking of starting.

"How to start a cleaning business" is twenty separate searches with real
commercial intent, and a single page about starting a business ranks for none
of them. This gives each one an address, on the same flat pattern the fifty
state pages and fifty-nine term pages already use.

Every figure is assembled from build/industry/*.json, which carries its own
source URL per claim. Where no primary source publishes a number the page says
that in as many words rather than quoting a figure from a vendor blog, which is
the whole reason the corpus has nulls in it.
"""
import os, sys, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from toolgen import page, SITE
from guidedata import (load, cost_text, filename, article,
                       DEMAND_LABEL, GROUP_ORDER)
import html as H

def e(s):
    return H.escape(str(s), quote=True)

def sentence(t):
    """First sentence, for the answer box."""
    m = re.match(r"(.+?[.!?])(\s|$)", t.strip())
    return (m.group(1) if m else t.strip())

def titlecase(name):
    small = {"a", "an", "and", "for", "in", "of", "or", "the", "to"}
    out = []
    for i, w in enumerate(name.split()):
        if w in ("AI", "EV"):
            out.append(w)
        elif i and w.lower() in small:
            out.append(w.lower())
        else:
            out.append(w[:1].upper() + w[1:])
    return " ".join(out)

def srclist(urls, label="Source"):
    if not urls:
        return ""
    bits = []
    for i, u in enumerate(urls[:4]):
        bits.append('<a href="%s" rel="noopener nofollow" target="_blank">%s</a>'
                    % (e(u), "source" if i == 0 and len(urls) == 1 else str(i + 1)))
    return '<p class="src">%s: %s</p>' % (e(label), ", ".join(bits))

CSS = """
.gd{max-width:46rem;margin:0 auto}
.gd .answer{margin:0 0 30px;padding:22px 24px;border-left:3px solid #D4A856;
  background:rgba(212,168,86,.06);border-radius:0 12px 12px 0}
.gd .answer p{margin:0;font-size:17.5px;line-height:1.7;color:#E8DEC4}
.gd h2{font-size:clamp(20px,3vw,25px);color:#FFF8D8;margin:44px 0 12px;
  font-family:Georgia,serif;font-weight:600;line-height:1.25}
.gd p{font-size:16.5px;line-height:1.78;color:#CFC7B4;margin:0 0 16px}
.gd a{color:#F3E4A8}
.gd ul{margin:0 0 18px;padding:0 0 0 1.1em;color:#CFC7B4}
.gd li{font-size:16.5px;line-height:1.72;margin:0 0 9px}
.gd .big{font-family:Georgia,serif;font-size:clamp(28px,6vw,38px);color:#FFF8D8;
  line-height:1.05;margin:0 0 6px;display:block}
.gd .nofig{font-family:Georgia,serif;font-size:clamp(19px,3.6vw,23px);
  color:#E8DEC4;line-height:1.25;margin:0 0 6px;display:block}
.gd .figrow{display:flex;flex-wrap:wrap;gap:14px;margin:0 0 20px}
.gd .fig{flex:1 1 13rem;padding:18px 20px;border:1px solid rgba(212,168,86,.24);
  border-radius:12px;background:rgba(212,168,86,.04)}
.gd .fig b{display:block;font-family:var(--util,inherit);font-size:10.5px;
  letter-spacing:.2em;text-transform:uppercase;color:#BDB4A4;margin:0 0 10px}
.gd .fig span.v{font-family:Georgia,serif;font-size:22px;color:#FFF8D8;
  line-height:1.2;display:block}
.gd .src{font-size:13.5px;color:#9C9484;line-height:1.65;margin:-6px 0 24px}
.gd .src a{color:#B9AF98}
.gd .cite{margin:36px 0 0;padding:18px 20px;border:1px solid rgba(212,168,86,.28);
  border-radius:12px;background:rgba(212,168,86,.04)}
.gd .cite b{display:block;font-family:var(--util,inherit);font-size:10.5px;
  letter-spacing:.2em;text-transform:uppercase;color:#BDB4A4;margin:0 0 8px}
.gd .cite p{font-size:14.5px;margin:0;color:#CFC7B4}
.gd .caveat{font-size:14.5px;color:#B9AF98;line-height:1.7;margin:0 0 18px;
  padding:14px 16px;border:1px dashed rgba(212,168,86,.3);border-radius:10px}
.gd .nav20{display:flex;flex-wrap:wrap;gap:7px;margin:12px 0 0}
.gd .nav20 a{font-size:13.5px;padding:7px 12px;border-radius:999px;
  border:1px solid rgba(212,168,86,.24);color:#D9D0BC;text-decoration:none;
  min-height:38px;display:inline-flex;align-items:center}
.gd .nav20 a:hover{border-color:#D4A856;color:#F3E4A8}
.gd .dem{display:inline-flex;align-items:center;gap:7px}
.gd .dot{width:9px;height:9px;border-radius:50%;flex:none}
.gd .d-up{background:#7FBF7F}.gd .d-flat{background:#D4A856}
.gd .d-down{background:#D08A6A}.gd .d-unclear{background:#8A8272}
"""


def build_one(rec, others):
    slug, name = rec["slug"], rec["name"]
    Name = titlecase(name)
    url = "%s/%s" % (SITE, rec["file"])
    costed = rec["startup_cost_low_usd"] is not None
    art = article(name)
    cost = cost_text(rec)
    dirn = rec["demand_direction"]
    demand = DEMAND_LABEL[dirn]

    b = ['<div class="gd">']

    # ---- the answer, first thing on the page and first thing quoted
    if costed:
        lead = ("Starting %s %s costs %s, on figures published by a primary "
                "source. " % (art, e(name), e(cost)))
    else:
        lead = ("No government or peer-reviewed source publishes a startup cost "
                "range for %s %s, so no figure is quoted here. "
                % (art, e(name)))
    lead += "The hardest part is %s%s" % (
        sentence(rec["hardest_part"])[0].lower(),
        sentence(rec["hardest_part"])[1:])
    b.append('<div class="answer"><p>%s</p></div>' % lead)

    # ---- the three numbers, side by side
    b.append('<div class="figrow">')
    b.append('<div class="fig"><b>Startup cost</b><span class="v">%s</span></div>'
             % (e(cost) if costed else "Not published"))
    b.append('<div class="fig"><b>Demand</b><span class="v">'
             '<span class="dem"><span class="dot d-%s"></span>%s</span>'
             '</span></div>' % (e(dirn), e(demand)))
    b.append('<div class="fig"><b>Licences to expect</b><span class="v">%d</span></div>'
             % len(rec["licences"]))
    b.append("</div>")

    # ---- cost
    b.append("<h2>What it costs to start</h2>")
    if costed:
        b.append('<span class="big">%s</span>' % e(cost))
    else:
        b.append('<span class="nofig">No primary source publishes this</span>')
    b.append("<p>%s</p>" % e(rec["startup_cost_note"]))
    b.append(srclist(rec["startup_cost_sources"]))

    # ---- licences
    b.append("<h2>What you have to file</h2>")
    b.append('<p class="caveat">Licensing is set by state, county and city, so this '
             'is what the category tends to require rather than a list for where you '
             'live. The state pages below carry the filing detail for each of the 50.</p>')
    b.append("<ul>%s</ul>" % "".join("<li>%s</li>" % e(l) for l in rec["licences"]))
    b.append(srclist(rec["licences_sources"]))

    # ---- margin
    b.append("<h2>What the margins look like</h2>")
    b.append("<p>%s</p>" % e(rec["margin_note"]))
    if rec["margin_note_known"]:
        b.append(srclist(rec["margin_sources"]))

    # ---- demand
    b.append("<h2>Whether demand is growing</h2>")
    b.append('<p><span class="dem"><span class="dot d-%s"></span><b>%s</b></span></p>'
             % (e(dirn), e(demand)))
    b.append("<p>%s</p>" % e(rec["demand_note"]))
    b.append(srclist(rec["demand_sources"]))

    # ---- size of the thing
    b.append("<h2>How big the market is</h2>")
    b.append("<p>%s</p>" % e(rec["key_stat"]))
    b.append(srclist(rec["key_stat_sources"]))

    # ---- the hard part
    b.append("<h2>The part that ends most of them</h2>")
    b.append("<p>%s</p>" % e(rec["hardest_part"]))
    b.append(srclist(rec["hardest_part_sources"]))

    # ---- next steps, options rather than instructions
    b.append("<h2>Before you start</h2><ul>"
             '<li><a href="startup-cost-calculator.html">What it will cost you</a>, '
             'since the numbers above are the category and not your version of it</li>'
             '<li><a href="business-structures.html">Sole proprietor, LLC or S corp</a>, '
             'what actually differs, with no recommendation</li>'
             '<li><a href="state-filing.html">What your state wants filed</a>, '
             'read from the state\'s own pages</li>'
             '<li><a href="breakeven-calculator.html">What you have to sell to break '
             'even</a>, which decides whether the margin above matters</li>'
             '<li><a href="assessment.html">Which way you actually work</a>, '
             'if the choice between these is really a choice about you</li></ul>')

    # ---- the other nineteen
    b.append('<h2>A different business</h2>'
             '<nav class="nav20" aria-label="Other business guides">')
    for o in others:
        if o["slug"] == slug:
            continue
        b.append('<a href="%s">%s</a>' % (o["file"], e(titlecase(o["name"]))))
    b.append("</nav>")
    b.append('<p style="margin-top:14px"><a href="what-business-should-i-start.html">'
             'Compare all twenty side by side</a></p>')

    b.append('<div class="cite"><b>Cite this page</b><p>SideKix, &ldquo;How to start '
             '%s %s&rdquo;. %s</p></div>' % (art, e(name), e(url)))
    b.append("</div>")
    return b, url, costed, cost, demand, Name, art


def render(rec, others):
    b, url, costed, cost, demand, Name, art = build_one(rec, others)
    name = rec["name"]

    # ---- schema. FAQPage and BreadcrumbList only: Google retired HowTo rich
    # results in 2023, so a HowTo block would be weight with nothing behind it.
    faq = [
        ("How much does it cost to start %s %s?" % (art, name),
         ("%s. %s" % (cost, rec["startup_cost_note"])) if costed
         else rec["startup_cost_note"]),
        ("What licences do you need for %s %s?" % (art, name),
         "Typically: %s. Licensing is set by state, county and city, so the exact "
         "list depends on where you operate."
         % "; ".join(l.split(".")[0] for l in rec["licences"][:5])),
        ("What profit margin does %s %s make?" % (art, name), rec["margin_note"]),
        ("Is demand for %s %s growing?" % (art, name), rec["demand_note"]),
        ("What is the hardest part of running %s %s?" % (art, name), rec["hardest_part"]),
    ]
    schema = [
        {"@context": "https://schema.org", "@type": "FAQPage", "url": url,
         "mainEntity": [{"@type": "Question", "name": q,
                         "acceptedAnswer": {"@type": "Answer", "text": a}}
                        for q, a in faq]},
        {"@context": "https://schema.org", "@type": "BreadcrumbList",
         "itemListElement": [
             {"@type": "ListItem", "position": 1, "name": "SideKix", "item": SITE},
             {"@type": "ListItem", "position": 2, "name": "What business should I start",
              "item": "%s/what-business-should-i-start.html" % SITE},
             {"@type": "ListItem", "position": 3, "name": "How to start %s %s" % (art, name),
              "item": url}]},
    ]

    # longest form that still fits, so the title carries what the page answers
    stem = "How to Start %s %s" % (art, Name)
    for tail in (": Costs, Licences and Margins | SideKix",
                 ": Costs and Licences | SideKix",
                 " | SideKix"):
        title = stem + tail
        if len(title) <= 118:
            break

    if costed:
        desc = ("It costs %s to start %s %s. %s demand, %d licences to expect, "
                "and the margin, hardest part and market size, every figure cited "
                "to a primary source."
                % (cost, art, name, demand, len(rec["licences"])))
    else:
        desc = ("What it takes to start %s %s: %s demand, %d licences to expect, the "
                "margin and the hardest part. No startup cost is quoted because no "
                "primary source publishes one."
                % (art, name, demand.lower(), len(rec["licences"])))

    back = ('<p class="kx-backrow"><a class="kx-bk" '
            'href="what-business-should-i-start.html">'
            '<svg aria-hidden="true" focusable="false" viewbox="0 0 24 24">'
            '<path d="M15 5l-7 7 7 7"></path></svg> All twenty businesses</a></p>')

    return page(rec["file"], title[:120], desc[:300], "Starting a business",
                "How to start %s <em>%s</em>" % (art, e(name)),
                "What it costs, what you file, what it earns and what ends most of "
                "them. Every number below is cited to where it came from.",
                "".join(b), css=CSS, schema=schema, wrapcls="wrap res", back=back)


def main():
    ind, _meta = load()
    recs = list(ind.values())
    order = []
    for g in GROUP_ORDER:
        order += [r for r in recs if r["group"] == g]
    total = 0
    for r in order:
        total += render(r, order)
    print("%d guide pages, %d KB total" % (len(order), total // 1024))


if __name__ == "__main__":
    main()
