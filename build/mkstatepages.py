# -*- coding: utf-8 -*-
"""One page per state.

Fifty states of filing data behind a single <select> is fifty rankable pages
Google cannot rank, because there is nothing to rank. "How much does an LLC
cost in Ohio" is a real search with commercial intent, and there are fifty of
them. This gives each one an address.

Every figure comes from build/state-filings.json, which was read from official
state sources and carries the date it was checked. Nothing here is generated
prose about a state; the sentences are assembled from fields that exist.
"""
import io, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from toolgen import page, SITE
import html as H

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = json.load(io.open(os.path.join(ROOT, "build", "state-filings.json"),
                         encoding="utf-8"))
STATES = DATA["states"]

def e(s): return H.escape(str(s), quote=True)
def slug(name): return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
def fn(name): return "start-an-llc-in-%s.html" % slug(name)

def money(n):
    if n is None: return None
    return "$%s" % ("{:,}".format(n) if n >= 1000 else n)

CSS = """
.st{max-width:46rem;margin:0 auto}
.st .answer{margin:0 0 30px;padding:22px 24px;border-left:3px solid #D4A856;
  background:rgba(212,168,86,.06);border-radius:0 12px 12px 0}
.st .answer p{margin:0;font-size:17.5px;line-height:1.7;color:#E8DEC4}
.st h2{font-size:clamp(20px,3vw,25px);color:#FFF8D8;margin:44px 0 12px;
  font-family:Georgia,serif;font-weight:600;line-height:1.25}
.st p{font-size:16.5px;line-height:1.78;color:#CFC7B4;margin:0 0 16px}
.st a{color:#F3E4A8}
.st ul{margin:0 0 18px;padding:0 0 0 1.1em;color:#CFC7B4}
.st li{font-size:16.5px;line-height:1.72;margin:0 0 9px}
.st .tblwrap{overflow-x:auto;-webkit-overflow-scrolling:touch;margin:0 0 12px}
.st .tblwrap:focus-visible{outline:3px solid #F3E4A8;outline-offset:3px;border-radius:8px}
.st table{width:100%;border-collapse:collapse;font-size:15.5px;min-width:26rem}
.st th,.st td{text-align:left;padding:12px 14px;
  border-bottom:1px solid rgba(212,168,86,.18);color:#CFC7B4;vertical-align:top}
.st th{color:#BDB4A4;font-family:var(--util,inherit);font-size:11px;
  letter-spacing:.14em;text-transform:uppercase;font-weight:700}
.st td b{color:#F3E4A8}
.st .big{font-family:Georgia,serif;font-size:30px;color:#FFF8D8;line-height:1}
.st .src{font-size:13.5px;color:#9C9484;line-height:1.65;margin:0 0 24px}
.st .cite{margin:36px 0 0;padding:18px 20px;border:1px solid rgba(212,168,86,.28);
  border-radius:12px;background:rgba(212,168,86,.04)}
.st .cite b{display:block;font-family:var(--util,inherit);font-size:10.5px;
  letter-spacing:.2em;text-transform:uppercase;color:#BDB4A4;margin:0 0 8px}
.st .cite p{font-size:14.5px;margin:0;color:#CFC7B4}
.st .nav50{display:flex;flex-wrap:wrap;gap:7px;margin:12px 0 0}
.st .nav50 a{font-size:13.5px;padding:7px 12px;border-radius:999px;
  border:1px solid rgba(212,168,86,.24);color:#D9D0BC;text-decoration:none;
  min-height:38px;display:inline-flex;align-items:center}
.st .nav50 a:hover{border-color:#D4A856;color:#F3E4A8}
"""


def build_one(name, rec, others):
    ar = rec["annual_report"]
    fee = rec["llc_fee_usd"]
    feetxt = money(fee)
    url = "%s/%s" % (SITE, fn(name))

    # ---- the answer, first thing on the page and first thing quoted
    if fee is not None:
        lead = ("Forming an LLC in %s costs %s to file the %s with the %s."
                % (e(name), feetxt, e(rec["llc_filing_name"]), e(rec["agency"])))
    else:
        lead = ("To form an LLC in %s you file the %s with the %s. The current fee "
                "could not be confirmed from an official source, so it is not "
                "quoted here." % (e(name), e(rec["llc_filing_name"]), e(rec["agency"])))
    if ar["required"]:
        lead += " After that, %s is due %s" % (
            e(ar["name"] or "a periodic report"),
            e(ar["due"][0].lower() + ar["due"][1:] if ar["due"] else "periodically"))
    else:
        lead += " %s does not require an annual report from an LLC." % e(name)

    b = ['<div class="st">']
    b.append('<div class="answer"><p>%s</p></div>' % lead)

    # ---- the numbers
    b.append("<h2>What it costs</h2>")
    rows = []
    if fee is not None:
        rows.append(("<b>%s</b>" % e(rec["llc_filing_name"]), feetxt,
                     "Once, when the LLC is formed"))
    else:
        rows.append(("<b>%s</b>" % e(rec["llc_filing_name"]), "Not confirmed",
                     "Check the state page before filing"))
    if ar["required"]:
        rows.append(("<b>%s</b>" % e(ar["name"] or "Periodic report"),
                     money(ar["fee_usd"]) or "See the state page", e(ar["due"] or "")))
    else:
        rows.append(("<b>Annual report</b>", "None", "%s does not require one" % e(name)))
    b.append('<div class="tblwrap" tabindex="0" role="region" aria-label="Costs"><table><thead><tr><th>What</th><th>Amount</th>'
             '<th>When</th></tr></thead><tbody>%s</tbody></table></div>'
             % "".join("<tr><td>%s</td><td>%s</td><td>%s</td></tr>" % r for r in rows))

    # ---- registered agent
    b.append("<h2>Registered agent</h2>")
    if rec["registered_agent_required"]:
        b.append("<p>%s requires one. %s</p>" % (e(name), e(rec["registered_agent_note"])))
    else:
        b.append("<p>%s</p>" % e(rec["registered_agent_note"]))

    # ---- annual obligation
    b.append("<h2>What you owe after year one</h2>")
    if ar["required"]:
        b.append("<p>%s</p>" % e(ar["due"]))
        b.append("<p>Missing it is the most common way a good standing lapses, and "
                 "restoring one costs more than filing on time.</p>")
    else:
        b.append("<p>%s</p>" % e(ar["due"]))

    if rec.get("notes"):
        b.append("<h2>Worth knowing</h2><p>%s</p>" % e(rec["notes"]))

    # ---- official links
    b.append("<h2>The official pages</h2><ul>")
    links = [("%s" % rec["agency"], rec["agency_url"]),
             ("Search the register for your name", rec["name_search_url"]),
             ("File the %s" % rec["llc_filing_name"], rec["llc_filing_url"])]
    if ar.get("url"):
        links.append(("Report filing and due dates", ar["url"]))
    for label, href in links:
        if href:
            b.append('<li><a href="%s" rel="noopener" target="_blank">%s</a></li>'
                     % (e(href), e(label)))
    b.append("</ul>")
    b.append('<p class="src">Read from %s on %s. Fees change, so check the state '
             'page before filing. SideKix has no relationship with any state agency '
             'and takes nothing for sending you there.</p>'
             % (", ".join('<a href="%s" rel="noopener" target="_blank">the source</a>'
                          % e(s) if i == 0 else
                          '<a href="%s" rel="noopener" target="_blank">%d</a>' % (e(s), i + 1)
                          for i, s in enumerate(rec["sources"][:4])),
                e(rec.get("checked", DATA["_meta"].get("checked", "")))))

    # ---- next steps into the tools
    b.append("<h2>Before you file</h2><ul>"
             '<li><a href="business-structures.html">Sole proprietor, LLC or S corp</a>, '
             'what actually differs, with no recommendation</li>'
             '<li><a href="startup-cost-calculator.html">What it will cost to start</a>, '
             'because the filing fee is the small part</li>'
             '<li><a href="domain-search.html">Whether the name is still free</a>, '
             'checked against the registries themselves</li>'
             '<li><a href="business-idea-where-to-start.html">What to do first</a> '
             'if the idea is still an idea</li></ul>')

    # ---- the other 49
    b.append('<h2>Another state</h2><nav class="nav50" aria-label="Other states">')
    for other in others:
        if other == name:
            continue
        b.append('<a href="%s">%s</a>' % (fn(other), e(other)))
    b.append("</nav>")

    b.append('<div class="cite"><b>Cite this page</b><p>SideKix, &ldquo;How much does '
             'an LLC cost in %s?&rdquo;, checked %s. %s</p></div>'
             % (e(name), e(rec.get("checked", "")), e(url)))
    b.append("</div>")

    # ---- schema
    faq = [("How much does it cost to start an LLC in %s?" % name,
            ("The state filing fee for the %s is %s." % (rec["llc_filing_name"], feetxt))
            if fee is not None else
            ("The fee for the %s could not be confirmed from an official state "
             "source." % rec["llc_filing_name"])),
           ("What form do I file to start an LLC in %s?" % name,
            "The %s, filed with the %s." % (rec["llc_filing_name"], rec["agency"])),
           ("Does %s require an annual report for an LLC?" % name,
            ar["due"] if ar["due"] else
            ("Yes." if ar["required"] else "No.")),
           ("Do I need a registered agent in %s?" % name,
            ("Yes. " + rec["registered_agent_note"]) if rec["registered_agent_required"]
            else rec["registered_agent_note"])]

    schema = [
        {"@context": "https://schema.org", "@type": "FAQPage", "url": url,
         "mainEntity": [{"@type": "Question", "name": q,
                         "acceptedAnswer": {"@type": "Answer", "text": a}}
                        for q, a in faq]},
        {"@context": "https://schema.org", "@type": "BreadcrumbList",
         "itemListElement": [
             {"@type": "ListItem", "position": 1, "name": "SideKix", "item": SITE},
             {"@type": "ListItem", "position": 2, "name": "State filing",
              "item": "%s/state-filing.html" % SITE},
             {"@type": "ListItem", "position": 3, "name": name, "item": url}]},
    ]

    title = ("How Much Does an LLC Cost in %s? %s to File | SideKix" % (name, feetxt)
             if fee is not None else
             "How to Start an LLC in %s: Forms, Fees and Steps | SideKix" % name)
    desc = ("It costs %s to file the %s with the %s. %s Every figure read from the "
            "state's own pages on %s."
            % (feetxt, rec["llc_filing_name"], rec["agency"],
               ("An annual report is required." if ar["required"]
                else "No annual report is required."),
               rec.get("checked", ""))) if fee is not None else (
           "Forms, fees and the order to do things in for an LLC in %s, read from "
           "the state's own pages." % name)

    back = ('<p class="kx-backrow"><a class="kx-bk" href="state-filing.html">'
            '<svg aria-hidden="true" focusable="false" viewbox="0 0 24 24">'
            '<path d="M15 5l-7 7 7 7"></path></svg> Back to state filing</a></p>')

    return page(fn(name), title[:120], desc[:300], name,
                "Starting an LLC in <em>%s</em>" % e(name),
                "What it costs, what you file and what you owe afterwards. "
                "Every figure below came from the state's own pages.",
                "".join(b), css=CSS, schema=schema, wrapcls="wrap res", back=back)


def main():
    names = sorted(STATES)
    total = 0
    for n in names:
        total += build_one(n, STATES[n], names)
    print("%d state pages, %d KB total" % (len(names), total // 1024))


if __name__ == "__main__":
    main()
