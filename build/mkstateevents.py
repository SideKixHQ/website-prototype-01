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


def pretty_date(dt: datetime) -> str:
    if dt.hour or dt.minute:
        return dt.strftime("%A, %B %-d, %Y at %-I:%M %p")
    return dt.strftime("%A, %B %-d, %Y")


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


def event_rows(events: list[dict]) -> tuple[str, list[dict]]:
    """The visible list, and the structured data that matches it."""
    items, graph = [], []
    for e in events:
        dt = parse(e.get("start", ""))
        if dt is None:
            continue
        facts = [bes.mode_label(e), bes.cost_label(e)]
        where = (e.get("location") or "").strip()
        if where and not re.search(r"online", where, re.I):
            facts.append(where)
        items.append(
            '<li class="kx-ev">'
            f'<a href="{html.escape(e.get("url", HUB), quote=True)}"'
            ' rel="noopener nofollow" target="_blank">'
            f'{html.escape(e.get("title", ""))}</a>'
            f'<span>{html.escape(e.get("host", ""))}. {html.escape(pretty_date(dt))}. '
            f'{html.escape(". ".join(f for f in facts if f))}.</span>'
            "</li>")

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
              updated: str, head: str, nav: str, foot: str) -> str:
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
.kx-evlist{{list-style:none;margin:0;padding:0}}
.kx-ev{{padding:14px 0;border-bottom:1px solid rgba(255,255,255,.12)}}
.kx-ev a{{display:block;font-weight:600}}
.kx-ev span{{display:block;margin-top:4px;font-size:.92rem;opacity:.78}}
.kx-states{{display:flex;flex-wrap:wrap;gap:10px;margin:18px 0 0}}
.kx-states a{{padding:6px 12px;border:1px solid rgba(255,255,255,.22);border-radius:999px;font-size:.9rem}}
@media (prefers-color-scheme: light){{
  .kx-ev{{border-bottom-color:rgba(0,0,0,.12)}}
  .kx-states a{{border-color:rgba(0,0,0,.22)}}
}}
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
<ul class="kx-evlist">
{rows}
</ul>
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
        '.kx-statelist span{opacity:.62;font-size:.85rem}</style>\n'
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

    written = []
    for state in order:
        sibs = [x for x in order if x != state][:12]
        (OUTDIR / f"{slug(state)}.html").write_text(
            page_html(state, keep[state], sibs, updated, head, nav, foot),
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

    link_hub(order, {s: len(keep[s]) for s in order})

    skipped = sorted(set(by_state) - set(keep))
    print(f"\n  {len(written)} state pages written, {len(removed)} removed",
          file=sys.stderr)
    if skipped:
        print("  below the %d event threshold, hub only: %s"
              % (MIN_EVENTS, ", ".join(skipped)), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
