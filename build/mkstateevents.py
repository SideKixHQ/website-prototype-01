#!/usr/bin/env python3
"""
mkstateevents.py - one page per state, built from the same events.json the
hub page uses.

Why this exists. events.html carries every state at once. A single page cannot
rank for "small business events in ohio" and "small business events in texas"
at the same time, because it is not about either of them in particular. The
event data is already collected, already verified weekly and already unique to
each state, so the only thing missing was a URL per state for Google to point
at.

The doorway-page trap is real and the glossary pages already fell into it: 59
near-identical pages, zero impressions in a quarter. The guard here is
MIN_EVENTS. A state page is written only when that state has enough genuinely
different upcoming events to be worth a visit on its own. Everything below the
line stays on the hub, where it belongs. The set of pages therefore changes as
coverage changes, which is the honest behaviour: pages appear when there is
something on them and are removed when there is not.

Run after scrape_events.py and build_events_seo.py, from the same workflow.
Idempotent: rerunning replaces each page in place and deletes any state page
that no longer clears the threshold.
"""

from __future__ import annotations

import html
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import build_events_seo as bes  # noqa: E402  (path has to be set first)

DATA = ROOT / "events.json"
OUTDIR = ROOT / "business-events"
REFERENCE = ROOT / "blog" / "how-to-network-when-youre-just-starting-out" / "index.html"

# The reference page sits two levels deep and these sit one, so every
# relative path lifted from it loses a level.
UP = ("../../", "../")

SITE = "https://sidekixhq.com"
HUB = f"{SITE}/events.html"

# A state needs this many upcoming events before it earns its own page. Below
# it the page would be thin, near-duplicate and indistinguishable from the
# other thin ones, which is how a set of pages gets read as doorway content
# rather than as a resource.
MIN_EVENTS = 8

# Nothing beyond this horizon goes on a page. Listings that far out move or
# vanish before anyone can attend them, and stale Event data is worse than no
# Event data.
HORIZON_DAYS = 120

# "National" is not a place, so it gets no state page; those events already sit
# on the hub and on every state page they are relevant to.
NOT_A_STATE = {"National", "", None}

# Matching the hub card exactly: the same three stroke colours cycling and
# the same month abbreviations.
STROKE = ("#38D2FF", "#D670FF", "#F3E4A8")
MONTHS = ("JAN", "FEB", "MAR", "APR", "MAY", "JUN",
          "JUL", "AUG", "SEP", "OCT", "NOV", "DEC")
FULL = ("January", "February", "March", "April", "May", "June", "July",
        "August", "September", "October", "November", "December")


def slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def parse(when: str):
    try:
        dt = datetime.fromisoformat(when)
    except (ValueError, TypeError):
        return None
    return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt


def upcoming(events: list[dict]) -> list[dict]:
    """Future events only, nearest first, inside the horizon."""
    now = datetime.now(timezone.utc)
    out = []
    for e in events:
        dt = parse(e.get("start", ""))
        if dt is None or dt < now:
            continue
        if (dt - now).days > HORIZON_DAYS:
            continue
        out.append((dt, e))
    out.sort(key=lambda p: p[0])
    return [e for _, e in out]


def chrome() -> tuple[str, str, str]:
    """Head chrome, nav and footer, lifted from a page already in the site.

    Taking them from a real page rather than a copy kept here means these
    pages cannot drift out of step with the rest of the site when the nav or
    the footer changes.
    """
    src = REFERENCE.read_text(encoding="utf-8")
    head = re.search(r"<head>(.*?)</head>", src, re.S).group(1)

    # Strip everything page-specific. What is left is fonts, stylesheets, the
    # icon and the shared inline styles.
    head = re.sub(r'<script type="application/ld\+json">.*?</script>', "", head, flags=re.S)
    head = re.sub(r"<title>.*?</title>", "", head, flags=re.S)
    head = re.sub(r'<meta[^>]*(name|property)="'
                  r'(description|robots|og:[a-z:_]+|twitter:[a-z]+|article:[a-z_]+)"[^>]*/?>',
                  "", head)
    head = re.sub(r'<link[^>]*rel="canonical"[^>]*/?>', "", head)
    head = re.sub(r'<meta charset[^>]*/?>|<meta[^>]*name="viewport"[^>]*/?>', "", head)
    head = head.replace(*UP)
    head = re.sub(r"\n{3,}", "\n\n", head).strip()

    body = re.search(r"<body>(.*)</body>", src, re.S).group(1)
    nav = body[: body.find("<main")].replace(*UP)
    # These pages live under Events, not Resources.
    nav = nav.replace('<span aria-current="page">Resources</span>',
                      '<a href="../library.html">Resources</a>')
    nav = nav.replace('<a href="../events.html">Events</a>',
                      '<span aria-current="page">Events</span>')
    foot = body[body.rfind("</main>") + len("</main>"):].replace(*UP)
    return head, nav, foot


CARD_SELECTORS = ("#kx-grid", ".kx-ev", ".kx-num", ".kx-mon", ".rough",
                  ".kx-meta", ".kx-badge", ".kx-badges", ".kx-go")


def card_styles() -> tuple[str, str]:
    """The card CSS and the rough-edge filter, taken from events.html.

    These pages used a plain text list while the hub drew cards, so the two
    looked like different sites. Copying the rules here rather than rewriting
    them means a change to the hub's card design reaches the state pages on
    the next build instead of drifting apart again.
    """
    src = (ROOT / "events.html").read_text(encoding="utf-8")
    css = "".join(re.findall(r"<style[^>]*>(.*?)</style>", src, re.S))
    keep = []
    for sel, body in re.findall(r"([^{}]+)\{([^{}]*)\}", css):
        sel = sel.strip()
        if sel.startswith("@") or not sel:
            continue
        # The hub carries several #kx-grid overrides marked !important, for
        # the width its own filter controls need. Copied here they beat the
        # rule below and collapsed the grid to a single column, so the card
        # styling comes across and the layout does not.
        if "#kx-grid" in sel:
            continue
        if any(w in sel for w in CARD_SELECTORS):
            keep.append(f"{sel}{{{body.strip()}}}")
    # The base grid is set inline on the hub's container, so it is not in the
    # stylesheet to copy. State pages have no filter controls, so they lay out
    # the same way at every width without the hub's overrides.
    grid = ("#kx-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));"
            "gap:24px;max-width:1180px;margin:0 auto}"
            "@media (max-width:900px){#kx-grid{grid-template-columns:1fr}}")
    filt = re.search(r"<svg[^>]*>\s*<defs>\s*<filter id=\"kx-rough\".*?</svg>", src, re.S)
    return grid + "\n" + "\n".join(keep), (filt.group(0) if filt else "")


def event_rows(events: list[dict]) -> tuple[str, list[dict]]:
    """The visible cards, and the structured data that matches them."""
    items, graph = [], []
    for e in events:
        dt = parse(e.get("start", ""))
        if dt is None:
            continue
        where = (e.get("location") or "").strip()
        mode = bes.mode_label(e)
        badges = [f'<span class="kx-badge kx-mode-'
                  f'{html.escape((mode or "other").lower().replace(" ", "-"))}">'
                  f'{html.escape(mode or "Check with host")}</span>']
        if where and not re.search(r"online", where, re.I):
            badges.append(f'<span class="kx-badge kx-where">{html.escape(where)}</span>')
        badges.append(f'<span class="kx-badge kx-cost">{html.escape(bes.cost_label(e))}</span>')

        bits = [e.get("host", ""), f"{FULL[dt.month - 1]} {dt.day}"]
        if not e.get("time_tbd") and (dt.hour or dt.minute):
            bits.append(dt.strftime("%-I:%M %p"))
        meta = " &middot; ".join(html.escape(x) for x in bits if x)
        stroke = STROKE[len(items) % len(STROKE)]
        items.append(
            f'<article class="kx-ev" data-topic="{html.escape(e.get("topic") or "")}">'
            '<div class="rough" aria-hidden="true"></div>'
            f'<div class="kx-num" style="-webkit-text-stroke:1.5px {stroke};">{dt.day}</div>'
            f'<div class="kx-mon">{MONTHS[dt.month - 1]}</div>'
            f'<h3><a href="{html.escape(e.get("url", HUB), quote=True)}"'
            ' rel="noopener nofollow" target="_blank">'
            f'{html.escape(e.get("title", ""))}</a></h3>'
            f'<div class="kx-meta">{meta}</div>'
            f'<div class="kx-badges">{"".join(badges)}</div>'
            f'<a class="kx-go" href="{html.escape(e.get("url", HUB), quote=True)}"'
            ' rel="noopener nofollow" target="_blank">Open event page &rarr;</a>'
            "</article>")

        place = bes.location_block(e)
        if place is None:
            # No address Google will accept. It stays visible to readers and
            # out of the structured data, which is the same rule the hub uses.
            continue
        node = {
            "@type": "Event",
            "name": e.get("title", ""),
            "startDate": e.get("start", ""),
            "eventStatus": "https://schema.org/EventScheduled",
            "eventAttendanceMode": bes.attendance(e),
            "location": place,
            "url": e.get("url", HUB),
        }
        ends = bes.end_date(e)
        if ends:
            node["endDate"] = ends
        if e.get("summary"):
            node["description"] = e["summary"]
        host = (e.get("host") or "").strip()
        if host:
            node["organizer"] = bes.organizer_block(host, e.get("url", ""))
        if bes.is_free(e):
            node["offers"] = {
                "@type": "Offer", "price": "0", "priceCurrency": "USD",
                "availability": "https://schema.org/InStock",
                "url": e.get("url", HUB),
            }
        graph.append(node)
    return "\n".join(items), graph


def page_html(state: str, events: list[dict], siblings: list[str],
              updated: str, head: str, nav: str, foot: str,
              cardcss: str, roughsvg: str) -> str:
    s = slug(state)
    url = f"{SITE}/business-events/{s}.html"
    title = f"Small Business Events in {state}, Updated Weekly | SideKix"
    desc = (f"Business events for {state} founders, from SBDCs, colleges, nonprofits, "
            f"banks and companies. Online, livestreamed and in person, with the cost "
            f"shown as the host states it. Checked at the source every week.")
    rows, graph = event_rows(events)

    ld = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "CollectionPage",
                "@id": url + "#page",
                "url": url,
                "name": f"Small Business Events in {state}",
                "description": desc,
                "isPartOf": {"@id": f"{SITE}/#website"},
                "dateModified": updated,
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "SideKix", "item": SITE + "/"},
                    {"@type": "ListItem", "position": 2, "name": "Events", "item": HUB},
                    {"@type": "ListItem", "position": 3, "name": state, "item": url},
                ],
            },
            {
                "@type": "ItemList",
                "name": f"Upcoming business events in {state}",
                "numberOfItems": len(graph),
                "itemListElement": [
                    {"@type": "ListItem", "position": i + 1, "item": node}
                    for i, node in enumerate(graph)
                ],
            },
        ],
    }

    sib = "".join(
        f'<a href="{slug(x)}.html">{html.escape(x)}</a>' for x in siblings)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta content="width=device-width,initial-scale=1" name="viewport"/>
<title>{html.escape(title)}</title>
<meta content="{html.escape(desc, quote=True)}" name="description"/>
<link href="{url}" rel="canonical"/>
<meta content="index, follow, max-image-preview:large" name="robots"/>
<meta content="website" property="og:type"/>
<meta content="SideKix" property="og:site_name"/>
<meta content="{html.escape(f'Small Business Events in {state}', quote=True)}" property="og:title"/>
<meta content="{html.escape(desc, quote=True)}" property="og:description"/>
<meta content="{url}" property="og:url"/>
<meta content="{SITE}/assets/k-mark.png" property="og:image"/>
<meta content="summary_large_image" name="twitter:card"/>
<meta content="#060502" name="theme-color"/>
{head}
<style id="kx-ev">
{cardcss}
.kx-states{{display:flex;flex-wrap:wrap;gap:10px;margin:18px 0 0}}
.kx-states a{{padding:6px 12px;border:1px solid rgba(212,168,86,.35);border-radius:999px;font-size:.9rem}}
.kx-states a:hover{{border-color:rgba(212,168,86,.8)}}
/* The article shell holds body copy to a reading column, which squeezed the
   card grid into a single lane. Centring against the viewport instead lets
   the cards use the page the way they do on the hub, without touching the
   shell's own width for the prose above and below. */
/* The grid sits outside the article column rather than inside it. A CSS
   breakout would have to know how far the column is offset from the centre
   of the page, and it is not centred, so the cards kept running off the
   left edge. Taking it out of that container in the markup needs no
   arithmetic and cannot drift when the shell changes. */
.kx-evsection{{padding:8px 28px 12px}}
.kx-evhead{{max-width:1180px;margin:0 auto 6px;font-size:clamp(20px,3vw,26px)}}
/* article.css underlines links in body copy. On a card the whole heading is
   the link, so the underline reads as a mistake. */
.kx-ev h3 a{{text-decoration:none;border-bottom:none;background:none}}
.kx-ev h3 a:hover{{text-decoration:underline}}
</style>
<script type="application/ld+json">{json.dumps(ld, separators=(",", ":"))}</script>
</head>
<body>
{nav}
<main id="maincontent">
<div class="artgrid">
<article>
<div class="ahead">
<h1>Small Business Events in {html.escape(state)}</h1>
<p class="lede">{len(events)} upcoming events for people starting, growing or
leading a business in {html.escape(state)}. Hosted by SBDCs, colleges,
nonprofits, banks and companies. Online, livestreamed and in person, with the
cost shown as the host states it.</p>
<div class="meta"><span>Checked at the source. Updated {html.escape(updated)}.</span></div>
</div>
<div class="body">
<p>Most of these are not advertised anywhere a founder would think to look.
They sit on the calendars of organizations that do not compete for attention,
so the events run half empty while the people who would benefit never hear
about them. This page gathers what is scheduled in {html.escape(state)} over
the next few months, in one place, refreshed weekly.</p>
</div>
</article>
</div>
{roughsvg}
<section aria-labelledby="kx-ev-h" class="kx-evsection">
<h2 class="kx-evhead" id="kx-ev-h">What is coming up in {html.escape(state)}</h2>
<div id="kx-grid">
{rows}
</div>
</section>
<div class="artgrid">
<article>
<div class="body">
<h2>What is on this list</h2>
<p>Every listing links to the host, not to SideKix. The cost line repeats what
the host states, so an event marked at no cost is one the host describes that
way. Nothing here is sponsored and nothing is placed in exchange for anything.</p>
<h2>Events in other states</h2>
<div class="kx-states">{sib}</div>
<p style="margin-top:14px"><a href="../events.html">See every state on the
events hub</a>.</p>
</div>
<section aria-labelledby="cta-h" class="cta">
<h2 id="cta-h">Building something in {html.escape(state)}?</h2>
<p>SideKix is a business operating system that pairs guided planning with real
Advisors and a community of people building alongside you. It opens soon.</p>
<div class="row"><a class="btn" href="../join.html">Join the waitlist</a></div>
</section>
</article>
</div>
</main>{foot}
</body>
</html>
"""


HUB_START = "<!-- kx:states:start -->"
HUB_END = "<!-- kx:states:end -->"


def link_hub(order: list[str], counts: dict[str, int]) -> None:
    """Put the state pages on the hub, between markers of their own.

    They sit before the SEO block rather than inside it, because that block is
    rewritten wholesale every week by build_events_seo.py and anything placed
    in it would be thrown away. A page nothing links to is a page Google files
    under "discovered, currently not indexed", so this link is the difference
    between the state pages existing and the state pages counting.
    """
    page_path = ROOT / "events.html"
    if not page_path.exists():
        print("  events.html missing, state pages left unlinked", file=sys.stderr)
        return
    page = page_path.read_text(encoding="utf-8")

    links = "".join(
        f'<li><a href="business-events/{slug(s)}.html">{html.escape(s)}'
        f'<span> {counts[s]} upcoming</span></a></li>' for s in sorted(order))
    block = (
        f'{HUB_START}\n'
        '<section id="kx-states" aria-labelledby="kx-states-h">\n'
        '  <h2 id="kx-states-h">Browse by state</h2>\n'
        '  <p>States with enough scheduled events to be worth their own page. '
        'Everything else is in the list above.</p>\n'
        f'  <ul class="kx-statelist">{links}</ul>\n'
        '</section>\n'
        '<style>#kx-states{max-width:1180px;margin:0 auto;padding:8px 28px 34px}'
        '.kx-statelist{list-style:none;display:flex;flex-wrap:wrap;gap:10px;'
        'margin:16px 0 0;padding:0}'
        '.kx-statelist a{display:inline-block;padding:8px 14px;border:1px solid '
        'rgba(255,255,255,.22);border-radius:999px;font-size:.95rem}'
        '.kx-statelist span{opacity:.80;font-size:.85rem}</style>\n'
        f'{HUB_END}')

    if HUB_START in page and HUB_END in page:
        page = re.sub(re.escape(HUB_START) + r"[\s\S]*?" + re.escape(HUB_END),
                      lambda _: block, page, count=1)
        print("  hub state links refreshed", file=sys.stderr)
    elif bes.START in page:
        page = page.replace(bes.START, block + "\n" + bes.START, 1)
        print("  hub state links inserted", file=sys.stderr)
    else:
        anchor = "</main>" if "</main>" in page else "</body>"
        page = page.replace(anchor, block + "\n" + anchor, 1)
        print("  hub state links appended", file=sys.stderr)
    page_path.write_text(page, encoding="utf-8")


LLMS_START = "<!-- kx:states:llms:start -->"
LLMS_END = "<!-- kx:states:llms:end -->"


def update_llms(order: list[str], counts: dict[str, int], updated: str) -> None:
    """Put the state pages in llms.txt.

    llms.txt is the file an answer engine reads to work out what this site
    covers. A weekly verified events listing per state is the most citable
    thing here and the least likely to be duplicated anywhere else, so it
    belongs in that file rather than only in the sitemap. Written between
    markers and regenerated each run, because the set of states changes.
    """
    path = ROOT / "llms.txt"
    if not path.exists():
        print("  llms.txt missing, state pages left out of it", file=sys.stderr)
        return
    text = path.read_text(encoding="utf-8")

    lines = [f"{LLMS_START}", "## Business events by state", "",
             f"Checked at the source and refreshed weekly. Last run {updated}. "
             "Each page lists what is scheduled in that state over the next few "
             "months, with the host, the date and the cost as the host states it.",
             ""]
    for state in sorted(order):
        lines.append(
            f"- [Business events in {state}]"
            f"({SITE}/business-events/{slug(state)}.html): "
            f"{counts[state]} upcoming events for people starting, growing or "
            f"leading a business in {state}.")
    lines += ["", LLMS_END]
    block = "\n".join(lines)

    if LLMS_START in text and LLMS_END in text:
        text = re.sub(re.escape(LLMS_START) + r"[\s\S]*?" + re.escape(LLMS_END),
                      lambda _: block, text, count=1)
        print("  llms.txt state section refreshed", file=sys.stderr)
    else:
        marker = "## Facts worth citing accurately"
        if marker in text:
            text = text.replace(marker, block + "\n\n" + marker, 1)
        else:
            text = text.rstrip() + "\n\n" + block + "\n"
        print("  llms.txt state section added", file=sys.stderr)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    if not DATA.exists():
        print("events.json missing", file=sys.stderr)
        return 1
    data = json.loads(DATA.read_text(encoding="utf-8"))
    updated = data.get("updated") or datetime.now(timezone.utc).date().isoformat()

    by_state: dict[str, list[dict]] = {}
    for e in upcoming(data.get("events", [])):
        scope = e.get("scope")
        if scope in NOT_A_STATE:
            continue
        by_state.setdefault(scope, []).append(e)

    keep = {s: evs for s, evs in by_state.items() if len(evs) >= MIN_EVENTS}
    order = sorted(keep, key=lambda s: (-len(keep[s]), s))

    OUTDIR.mkdir(exist_ok=True)
    head, nav, foot = chrome()
    cardcss, roughsvg = card_styles()

    written = []
    for state in order:
        sibs = [x for x in order if x != state][:12]
        (OUTDIR / f"{slug(state)}.html").write_text(
            page_html(state, keep[state], sibs, updated, head, nav, foot,
                      cardcss, roughsvg),
            encoding="utf-8")
        written.append(slug(state))
        print(f"  {state}: {len(keep[state])} events", file=sys.stderr)

    # A state that dropped below the threshold should not leave a stale page
    # behind advertising events that are over.
    removed = []
    for f in OUTDIR.iterdir():
        if f.suffix == ".html" and f.stem not in written:
            f.unlink()
            removed.append(f.stem)
        elif f.is_dir():
            # left over from the directory-per-state layout
            shutil.rmtree(f)
            removed.append(f.name + "/")

    counts = {s: len(keep[s]) for s in order}
    link_hub(order, counts)
    update_llms(order, counts, updated)

    skipped = sorted(set(by_state) - set(keep))
    print(f"\n  {len(written)} state pages written, {len(removed)} removed",
          file=sys.stderr)
    if skipped:
        print("  below the %d event threshold, hub only: %s"
              % (MIN_EVENTS, ", ".join(skipped)), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
