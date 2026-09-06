# -*- coding: utf-8 -*-
"""One page per glossary term.

Fifty nine definitions behind a single page is fifty nine "what is X" searches
with nowhere to land. Each term gets an address, its definition as the first
thing on the page, why it matters, a worked example where the term is
quantitative, the tool on this site that uses it, and the other terms in its
family.

DefinedTerm markup ties each page back to the glossary as its parent set,
which is what tells an answer engine these are entries in one reference rather
than fifty nine unrelated pages.
"""
import html as H, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from toolgen import page, SITE
from terms import TERMS, CATS
from termdepth import DEPTH

def e(s): return H.escape(str(s), quote=True)
def slug(t): return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")
def fn(t): return "what-is-%s.html" % slug(t)

TOOLNAME = {
 "breakeven-calculator.html": "the breakeven calculator",
 "product-pricing-calculator.html": "the product pricing calculator",
 "hourly-rate-calculator.html": "the hourly rate calculator",
 "startup-cost-calculator.html": "the startup cost calculator",
 "business-structures.html": "the structure comparison",
 "state-filing.html": "the state filing lookup",
 "domain-search.html": "the name availability check",
 "positioning-statement.html": "the positioning statement builder",
 "outreach-email.html": "the outreach email builder",
 "market-data.html": "the market data page",
 "90-day-goals.html": "the 90 day goals worksheet",
}

CSS = """
.tm{max-width:42rem;margin:0 auto}
.tm .def{margin:0 0 30px;padding:24px 26px;border-left:3px solid #D4A856;
  background:rgba(212,168,86,.06);border-radius:0 12px 12px 0}
.tm .def p{margin:0;font-size:18.5px;line-height:1.65;color:#F0E6CE}
.tm .cat{display:inline-flex;align-items:center;min-height:34px;padding:0 14px;
  border-radius:999px;border:1px solid rgba(212,168,86,.4);color:#F3E4A8;
  font-family:var(--util,inherit);font-size:10.5px;letter-spacing:.2em;
  text-transform:uppercase;text-decoration:none;margin:0 0 26px}
.tm .cat:hover{background:rgba(212,168,86,.12)}
.tm h2{font-size:12px;letter-spacing:.18em;text-transform:uppercase;color:#BDB4A4;
  font-weight:700;margin:34px 0 12px;padding:0 0 9px;
  border-bottom:1px solid rgba(212,168,86,.18)}
.tm p{font-size:16.5px;line-height:1.78;color:#CFC7B4;margin:0 0 16px}
.tm .eg{padding:18px 20px;border-radius:12px;background:rgba(255,255,255,.03);
  border:1px solid rgba(212,168,86,.16)}
.tm .eg p{margin:0;font-size:16px;color:#E4DAC4}
.tm a{color:#F3E4A8}
.tm .rel{display:flex;flex-wrap:wrap;gap:8px}
.tm .rel a{font-size:14px;padding:8px 13px;border-radius:999px;
  border:1px solid rgba(212,168,86,.24);color:#D9D0BC;text-decoration:none;
  min-height:40px;display:inline-flex;align-items:center}
.tm .rel a:hover{border-color:#D4A856;color:#F3E4A8;background:rgba(212,168,86,.08)}
"""


def build_one(name, cat, definition, by_cat):
    why, example, tool = DEPTH[name]
    url = "%s/%s" % (SITE, fn(name))

    b = ['<div class="tm">']
    b.append('<a class="cat" href="glossary.html">%s</a>' % e(cat))
    b.append('<h2>The definition</h2><div class="def"><p>%s</p></div>' % e(definition))

    if example:
        b.append('<h2>An example</h2><div class="eg"><p>%s</p></div>' % e(example))
    if tool:
        b.append('<h2>Where it comes up</h2><p>This shows up in '
                 '<a href="%s">%s</a> on this site.</p>' % (e(tool), e(TOOLNAME.get(tool, tool))))

    siblings = [t for t in by_cat[cat] if t != name]
    if siblings:
        b.append('<h2>Related</h2><nav class="rel" aria-label="Related terms">%s</nav>'
                 % "".join('<a href="%s">%s</a>' % (fn(s), e(s)) for s in siblings))
    b.append('<p style="margin:32px 0 0"><a href="glossary.html">All %d terms &rarr;</a></p>'
             % len(TERMS))
    b.append("</div>")

    schema = [
        {"@context": "https://schema.org", "@type": "DefinedTerm",
         "name": name, "description": definition, "url": url,
         "inDefinedTermSet": {"@type": "DefinedTermSet",
                              "name": "The SideKix business glossary",
                              "url": "%s/glossary.html" % SITE}},
        {"@context": "https://schema.org", "@type": "FAQPage", "url": url,
         "mainEntity": [{"@type": "Question", "name": "What is %s?" % name,
                         "acceptedAnswer": {"@type": "Answer",
                                            "text": definition + " " + why}}]},
        {"@context": "https://schema.org", "@type": "BreadcrumbList",
         "itemListElement": [
             {"@type": "ListItem", "position": 1, "name": "SideKix", "item": SITE},
             {"@type": "ListItem", "position": 2, "name": "Glossary",
              "item": "%s/glossary.html" % SITE},
             {"@type": "ListItem", "position": 3, "name": name, "item": url}]},
    ]

    back = ('<p class="kx-backrow"><a class="kx-bk" href="glossary.html">'
            '<svg aria-hidden="true" focusable="false" viewbox="0 0 24 24">'
            '<path d="M15 5l-7 7 7 7"></path></svg> Back to the glossary</a></p>')

    desc = (definition + " " + why)[:180]
    # "What Is LLC?" and "What Is Breakeven point?" both read wrong, and getting
    # the article right per term is more trouble than avoiding it.
    title = "%s: What It Means and Why It Matters | SideKix" % name
    return page(fn(name), title, desc,
                cat, "What is <em>%s</em>?" % e(name), e(why),
                "".join(b), css=CSS, schema=schema, wrapcls="wrap res", back=back)


def main():
    by_cat = {c: [] for c in CATS}
    for n, c, d in TERMS:
        by_cat[c].append(n)
    for c in by_cat:
        by_cat[c].sort()
    total = 0
    for n, c, d in TERMS:
        total += build_one(n, c, d, by_cat)
    print("%d term pages, %d KB total" % (len(TERMS), total // 1024))


if __name__ == "__main__":
    main()
