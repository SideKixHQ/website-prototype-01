#!/usr/bin/env python3
"""
build_events_seo.py - make events.html tell the truth, and make it readable
without JavaScript.

Run after scrape_events.py, from the same workflow.

Two problems this fixes.

1. The page promised online events. It now carries livestreamed and in-person
   ones too, so the copy, the title and the share cards all had to change, and
   every card had to start saying which kind it is and what the host says about
   the price.

2. Every event was drawn by JavaScript from events.json, so the HTML a crawler
   downloads contained no event text at all. Google renders JavaScript. Most
   answer engines do not. A page whose entire subject matter only exists after
   a script runs is, to them, a page about nothing. So the next few weeks of
   events are written into the HTML as a plain list, with Event structured
   data beside it, and the interactive grid hides that list once it has drawn
   its own. Same content either way, which is the only version of this that is
   honest.

Everything here is idempotent: it can run every Monday for a year without
stacking up duplicates, and it reports what it changed and what it could not
find rather than failing silently.
"""

from __future__ import annotations

import html
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).parent
PAGE = HERE / "events.html"
DATA = HERE / "events.json"
SITEMAP = HERE / "sitemap.xml"
LLMS = HERE / "llms.txt"

SITE = "https://sidekixhq.com"
PAGE_URL = f"{SITE}/events.html"

# How many events go into the static block and the structured data. The grid
# still shows everything; this is the slice worth handing a crawler, and it
# keeps the page from doubling in weight.
SEO_LIMIT = 200

START = "<!-- kx:seo:start -->"
END = "<!-- kx:seo:end -->"

TITLE = "Free Business Events Near You, Every State, Updated Weekly | SideKix"
DESCRIPTION = (
    "Business events for founders in every state, from SBDCs, colleges, "
    "nonprofits, banks and companies. Online, livestreamed and in person. "
    "Checked at the source every week."
)
OG_TITLE = "Business events in every state, checked every week"
HERO = (
    "Events run online, streamed live, and held in person, from colleges, "
    "nonprofits, banks and companies in every state. Anything with a published "
    "price is left out, and each card shows what the host says about cost."
)

OLD_HERO = re.compile(
    r"Every event is online, costs nothing to attend, and is checked at the "
    r"source each week\.\s*No filler,? or hidden sales pitches\.",
    re.I)

changes: list[str] = []


def note(ok: bool, label: str) -> None:
    changes.append(("changed  " if ok else "NOT FOUND ") + label)


def set_meta(page: str, attr: str, key: str, value: str) -> str:
    """Rewrite one meta tag's content, whatever order its attributes are in.

    A page carrying the same meta name twice has told search engines two
    different things and left them to pick. Every copy is removed and exactly
    one is put back.
    """
    pattern = re.compile(
        r"<meta\b(?=[^>]*\b" + attr + r'="' + re.escape(key) + r'")[^>]*>',
        re.I)
    found = pattern.findall(page)
    replacement = f'<meta content="{html.escape(value, quote=True)}" {attr}="{key}"/>'

    if not found:
        page = page.replace("</head>", replacement + "\n</head>", 1)
        note(True, f"meta {key} (added, was missing)")
        return page

    page = pattern.sub("", page)
    page = page.replace("</title>", "</title>\n" + replacement, 1)
    extra = f" (removed {len(found) - 1} duplicate)" if len(found) > 1 else ""
    note(True, f"meta {key}{extra}")
    return page


def mode_label(event: dict) -> str:
    return event.get("mode") or "Check with host"


def cost_label(event: dict) -> str:
    """What the card says about price.

    An empty cost means the host did not publish one, and that is what the card
    says. It never guesses, and it never rounds an unknown down to free.
    """
    cost = (event.get("cost") or "").strip()
    if not cost:
        return "Cost not listed"
    if re.search(r"no fee|no cost|free", cost, re.I):
        return "No cost"
    return cost


def is_free(event: dict) -> bool:
    return bool(re.search(r"no fee|no cost|free", event.get("cost", ""), re.I))


def attendance(event: dict) -> str:
    mode = (event.get("mode") or "").lower()
    if mode == "online":
        return "https://schema.org/OnlineEventAttendanceMode"
    if mode == "livestream":
        return "https://schema.org/MixedEventAttendanceMode"
    if mode == "in person":
        return "https://schema.org/OfflineEventAttendanceMode"
    return ""


def location_block(event: dict) -> dict:
    place = (event.get("location") or "").strip()
    mode = (event.get("mode") or "").lower()
    if mode == "online" or (place and re.search(r"online", place, re.I)):
        return {"@type": "VirtualLocation", "url": event.get("url") or PAGE_URL}
    if place:
        return {"@type": "Place", "name": place,
                "address": {"@type": "PostalAddress", "name": place}}
    return {"@type": "VirtualLocation", "url": event.get("url") or PAGE_URL}


def build_block(events: list[dict], updated: str) -> str:
    """The static list and the structured data that goes with it."""
    rows = []
    for e in events:
        try:
            when = datetime.fromisoformat(e["start"])
        except (ValueError, KeyError):
            continue
        pretty = when.strftime("%A, %B %-d, %Y at %-I:%M %p") if when.hour or when.minute \
            else when.strftime("%A, %B %-d, %Y")
        bits = [mode_label(e), cost_label(e)]
        where = (e.get("location") or "").strip()
        if where and not re.search(r"online", where, re.I):
            bits.append(where)
        rows.append(
            "<li>"
            f'<a href="{html.escape(e.get("url", PAGE_URL), quote=True)}"'
            ' rel="noopener nofollow" target="_blank">'
            f'{html.escape(e.get("title", ""))}</a>'
            f'<span> {html.escape(e.get("host", ""))}. {html.escape(pretty)}. '
            f'{html.escape(". ".join(bits))}.</span>'
            "</li>")

    graph = []
    for e in events:
        node = {
            "@type": "Event",
            "name": e.get("title", ""),
            "startDate": e.get("start", ""),
            "eventStatus": "https://schema.org/EventScheduled",
            "location": location_block(e),
            "organizer": {"@type": "Organization", "name": e.get("host", "")},
            "url": e.get("url", PAGE_URL),
        }
        mode = attendance(e)
        if mode:
            node["eventAttendanceMode"] = mode
        summary = (e.get("summary") or "").strip()
        if summary:
            node["description"] = summary[:300]
        # Only claim a price when the host stated one. A free Offer on an event
        # whose price nobody published is the kind of structured data that gets
        # a site's rich results pulled.
        if is_free(e):
            node["offers"] = {
                "@type": "Offer", "price": "0", "priceCurrency": "USD",
                "availability": "https://schema.org/InStock",
                "url": e.get("url", PAGE_URL),
                "validFrom": updated,
            }
        graph.append(node)

    itemlist = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": "Business events for founders across the United States",
        "description": DESCRIPTION,
        "url": PAGE_URL,
        "numberOfItems": len(graph),
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "item": node}
            for i, node in enumerate(graph)
        ],
    }

    return (
        f"{START}\n"
        '<section id="kx-seo" aria-label="Upcoming business events">\n'
        "  <h2>Upcoming events</h2>\n"
        f"  <p>{html.escape(DESCRIPTION)}</p>\n"
        f"  <p>Last checked {html.escape(updated)}.</p>\n"
        "  <ul>\n    " + "\n    ".join(rows) + "\n  </ul>\n"
        "</section>\n"
        '<script type="application/ld+json">'
        + json.dumps(itemlist, ensure_ascii=False, separators=(",", ":"))
        + "</script>\n"
        f"{END}"
    )


def patch_card_template(page: str) -> str:
    """Add the mode, place and cost line to each card in the grid."""
    anchor = "'<div class=\"kx-meta\">'+meta([e.host, time(d), e.duration])+'</div>'+"
    if "kx-badges" in page:
        note(True, "card template (already patched)")
        return page
    if anchor not in page:
        note(False, "card template")
        return page
    added = (
        anchor
        + "\n      '<div class=\"kx-badges\">'+"
        + "'<span class=\"kx-badge kx-mode-'+esc((e.mode||'other').toLowerCase().replace(/ /g,'-'))+'\">'+esc(e.mode||'Check with host')+'</span>'+"
        + "(e.location && !/online/i.test(e.location) ? '<span class=\"kx-badge kx-where\">'+esc(e.location)+'</span>' : '')+"
        + "'<span class=\"kx-badge kx-cost\">'+esc(costLabel(e))+'</span>'+"
        + "'</div>'+"
    )
    page = page.replace(anchor, added, 1)
    note(True, "card template")
    return page


HELPERS = """
function costLabel(e){
  /* An event whose host never published a price says so. Rounding an unknown
     down to "free" is the one mistake this page cannot afford to make. */
  var c=(e.cost||'').trim();
  if(!c) return 'Cost not listed';
  if(/no fee|no cost|free/i.test(c)) return 'No cost';
  return c;
}
function hideSeoList(){
  /* The plain list is the page without JavaScript. Once the grid has drawn
     the same events, the list is redundant, so it goes. */
  var s=document.getElementById('kx-seo');
  if(s) s.hidden=true;
}
"""

BADGE_CSS = """
#kx-seo{max-width:1100px;margin:0 auto;padding:0 56px 60px;color:#9B958B;font-size:14px;line-height:1.7}
#kx-seo h2{color:#EFE9DF;font-size:20px;margin:0 0 10px}
#kx-seo ul{list-style:none;padding:0;margin:0}
#kx-seo li{padding:10px 0;border-bottom:1px solid rgba(239,233,223,.08)}
#kx-seo li a{color:#EFE9DF;text-decoration:none;font-weight:600}
#kx-seo li a:hover{text-decoration:underline}
#kx-seo li span{display:block;color:#9B958B;font-size:13px;margin-top:3px}
.kx-badges{display:flex;flex-wrap:wrap;gap:6px;margin-top:10px}
.kx-badge{font-family:'Space Grotesk',system-ui,sans-serif;font-size:10.5px;letter-spacing:.08em;text-transform:uppercase;padding:4px 9px;border-radius:999px;border:1px solid rgba(239,233,223,.18);color:#C9C2B6;white-space:nowrap}
.kx-badge.kx-mode-online{border-color:rgba(122,196,168,.45);color:#8FD4B6}
.kx-badge.kx-mode-livestream{border-color:rgba(214,178,102,.5);color:#E2BE72}
.kx-badge.kx-mode-in-person{border-color:rgba(196,142,122,.45);color:#DDA98C}
.kx-badge.kx-cost{border-color:rgba(239,233,223,.28);color:#EFE9DF}
.kx-badge.kx-where{max-width:260px;overflow:hidden;text-overflow:ellipsis}
"""


def touch_sitemap(updated: str) -> None:
    """Move the events page's lastmod to the day the list was actually rebuilt.

    A lastmod that never moves, on a page that changes every week, is a signal
    pointing the wrong way. Crawlers use it to decide how often to come back.
    """
    if not SITEMAP.exists():
        note(False, "sitemap lastmod")
        return
    text = SITEMAP.read_text()
    block = re.search(r"<url>(?:(?!</url>)[\s\S])*?events\.html(?:(?!</url>)[\s\S])*?</url>",
                      text, re.I)
    if not block:
        note(False, "sitemap lastmod (no events entry)")
        return
    fixed, n = re.subn(r"(<lastmod>)[^<]*(</lastmod>)",
                       r"\g<1>" + updated + r"\g<2>", block.group(0), count=1)
    if not n:
        note(False, "sitemap lastmod (no lastmod tag)")
        return
    if fixed == block.group(0):
        note(True, "sitemap lastmod (already current)")
        return
    SITEMAP.write_text(text.replace(block.group(0), fixed, 1))
    note(True, f"sitemap lastmod set to {updated}")


LLMS_OLD = "a weekly listing of no-cost online business events"
LLMS_NEW = ("a weekly listing of business events in every state, online, "
            "livestreamed and in person, with the cost shown as the host states it")


def fix_llms() -> None:
    """llms.txt is what an answer engine reads to decide what this site is.

    It still described the events page as online-only and free, which stopped
    being true the moment in-person events were let in. A file whose whole job
    is telling machines the truth about the site is the last place to leave a
    stale claim standing.
    """
    if not LLMS.exists():
        note(False, "llms.txt")
        return
    text = LLMS.read_text()
    if LLMS_NEW in text:
        note(True, "llms.txt (already updated)")
        return
    if LLMS_OLD not in text:
        note(False, "llms.txt (line not found)")
        return
    LLMS.write_text(text.replace(LLMS_OLD, LLMS_NEW))
    note(True, "llms.txt")


def main() -> int:
    if not PAGE.exists() or not DATA.exists():
        print("events.html or events.json missing", file=sys.stderr)
        return 1

    page = PAGE.read_text()
    data = json.loads(DATA.read_text())
    events = data.get("events", [])
    updated = data.get("updated") or datetime.now(timezone.utc).date().isoformat()

    page = re.sub(r"<title>.*?</title>", f"<title>{html.escape(TITLE)}</title>",
                  page, count=1, flags=re.S)
    note("<title>" in page, "title")

    page = set_meta(page, "name", "description", DESCRIPTION)
    page = set_meta(page, "property", "og:title", OG_TITLE)
    page = set_meta(page, "property", "og:description", DESCRIPTION)

    # Twitter reads the og: tags when its own are missing, but the title and
    # description are the two it will not infer, so they are stated.
    if "twitter:title" not in page:
        cards = (f'<meta content="{html.escape(OG_TITLE, quote=True)}" name="twitter:title"/>\n'
                 f'<meta content="{html.escape(DESCRIPTION, quote=True)}" name="twitter:description"/>\n'
                 f'<meta content="{SITE}/assets/k-mark.png" name="twitter:image"/>')
        page = page.replace("</head>", cards + "\n</head>", 1)
        note(True, "twitter card tags")
    else:
        note(True, "twitter card tags (already present)")

    if HERO[:40] in page:
        note(True, "hero copy (already updated)")
    else:
        page, n = OLD_HERO.subn(html.escape(HERO), page)
        note(bool(n), "hero copy")

    page = patch_card_template(page)

    if "function costLabel" not in page:
        page = page.replace("function stageOf(e){", HELPERS + "\nfunction stageOf(e){", 1)
        note("function costLabel" in page, "card helpers")
    else:
        note(True, "card helpers (already present)")

    if "#kx-seo{" not in page:
        page = page.replace("</head>", f"<style>{BADGE_CSS}</style>\n</head>", 1)
        note("#kx-seo{" in page, "badge styles")
    else:
        note(True, "badge styles (already present)")

    if "hideSeoList();\n  renderGrid();" not in page:
        page = page.replace("  renderGrid();\n}", "  hideSeoList();\n  renderGrid();\n}", 1)
    note("hideSeoList();\n  renderGrid();" in page, "grid hides the plain list")

    block = build_block(events[:SEO_LIMIT], updated)
    if START in page and END in page:
        page = re.sub(re.escape(START) + r"[\s\S]*?" + re.escape(END), lambda _: block, page, count=1)
        note(True, f"structured data refreshed ({min(len(events), SEO_LIMIT)} events)")
    else:
        anchor = "</main>" if "</main>" in page else "</body>"
        page = page.replace(anchor, block + "\n" + anchor, 1)
        note(True, f"structured data inserted ({min(len(events), SEO_LIMIT)} events)")

    PAGE.write_text(page)
    touch_sitemap(updated)
    fix_llms()

    for line in changes:
        print("  " + line, file=sys.stderr)
    missing = [c for c in changes if c.startswith("NOT FOUND")]
    print(f"\n  {len(changes) - len(missing)} applied, {len(missing)} not found",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
