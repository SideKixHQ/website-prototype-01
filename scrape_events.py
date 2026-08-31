#!/usr/bin/env python3
"""
scrape_events.py — rebuild events.json from the curated source list.

Run locally:   python scrape_events.py
Dry run:       python scrape_events.py --dry-run
Add a source:  edit SOURCES below

Safety rules baked in:
  * Never overwrites a healthy events.json with an empty or near-empty result.
  * Anything in pinned.json is always merged in, scraper or no scraper.
  * A source that returns nothing logs a warning and is skipped, not fatal.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from dateutil import parser as dateparse

HERE = Path(__file__).parent
OUT = HERE / "events.json"
PINNED = HERE / "pinned.json"

UA = {"User-Agent": "Mozilla/5.0 (compatible; SideKixEvents/1.0; +https://sidekixhq.com)"}
TIMEOUT = 25

# Set to False to publish titles, hosts and dates only, with no host-authored
# description text on the cards.
INCLUDE_SUMMARIES = True
SUMMARY_CHARS = 165

# How far ahead to keep events.
# Chapter networks like 1 Million Cups meet in person in most of their 160+
# communities. The page promises online events, so in-person is filtered out by
# default. Flip this to True to include them, and the card will need to show a
# location or the promise on the page has to change.
ALLOW_INPERSON = False

# What never belongs on this page, whatever ALLOW_INPERSON is set to.
# The old single pattern only caught a dollar sign, so "a small fee applies",
# "tickets required" and "costs 25 dollars" all passed as no-cost events.
PAID = re.compile(
    r"\$\s*[1-9]"
    r"|\b\d+\s*dollars?\b"
    r"|\bfees?\b|\bpaid\b|\bpricing\b|\bcost[s]?\s+\$?\d"
    r"|\bticket(s|ed)?\b|\bregistration fee\b|\bmembers only\b",
    re.I)
REPLAY = re.compile(r"on[- ]demand|\brecorded\b|\breplay\b|\bwatch anytime\b", re.I)
INPERSON = re.compile(r"in[- ]person|\bonsite\b|\bon-site\b", re.I)
BIGEVENT = re.compile(r"\bconference\b|\bexpo\b|\bsummit\b|\bgala\b", re.I)

# A meeting held in a room but streamed out is attendable from anywhere, which
# is the whole point of this page. 1 Million Cups Wilmington meets in person
# and streams live on Facebook; the in-person filter would have dropped it.
LIVESTREAM = re.compile(
    r"live ?stream|livestreamed|streams? live|streaming live"
    r"|facebook live|youtube live|linkedin live|twitch"
    r"|\bwebcast\b|watch live|join (?:us )?online|virtual option"
    r"|\bzoom\b|google meet|microsoft teams|\bhybrid\b",
    re.I)
REJECT = re.compile("|".join(p.pattern for p in (PAID, REPLAY, INPERSON, BIGEVENT)), re.I)

HORIZON_DAYS = 120

SOURCES = [
    # ============================================================
    # NATIONAL AGGREGATORS. highest yield per parser. sba.gov alone
    # carries SBDC, SCORE, WBC, VBOC and APEX events from every state.
    # ============================================================
    {"name": "SBA", "url": "https://www.sba.gov/events", "parser": "sba"},
    {"name": "America's SBDC", "url": "https://americassbdc.org/training-events/"},
    {"name": "SCORE", "url": "https://www.score.org/business-education/"},

    # ============================================================
    # FEDERAL. slow-moving markup, evergreen subject matter.
    # ============================================================
    {"name": "IRS", "url": "https://www.irs.gov/businesses/small-businesses-self-employed/webinars-for-small-businesses"},
    {"name": "USPTO", "url": "https://www.uspto.gov/learning-and-resources/events"},
    {"name": "MBDA", "url": "https://www.mbda.gov/events"},
    {"name": "USDA Rural Development", "url": "https://www.rd.usda.gov/newsroom/events"},

    # ============================================================
    # STATE SBDC NETWORKS. 63 members, ~1,000 centers, nearly all
    # hosted by universities and colleges. every domain below came
    # from the America's SBDC state directory.
    #
    # many run Neoserra / eCenterDirect, which the "neoserra" parser
    # handles. the rest fall through to JSON-LD then headings.
    # run with --probe to see which respond and which return events,
    # then delete the ones that come back empty.
    # ============================================================
    {"name": "Alabama SBDC", "url": "https://www.asbdc.org/events/"},
    {"name": "Alaska SBDC", "url": "https://aksbdc.org/events/"},
    {"name": "Arizona SBDC", "url": "https://azsbdc.net/events"},
    {"name": "Florida SBDC", "url": "https://floridasbdc.org/training/"},
    {"name": "Georgia SBDC", "url": "https://georgiasbdc.org/training-program/"},
    {"name": "Hawaii SBDC", "url": "https://www.hisbdc.org/events/"},
    {"name": "Idaho SBDC", "url": "https://idahosbdc.org/events/"},
    {"name": "Illinois SBDC", "url": "https://www.illinoissbdc.biz/events/"},
    {"name": "Indiana SBDC", "url": "https://isbdc.org/events/"},
    {"name": "New York SBDC", "url": "https://nysbdc.ecenterdirect.com/events", "parser": "neoserra"},
    {"name": "Pace University SBDC", "url": "https://www.pacesbdc.org/events"},
    {"name": "Virginia SBDC", "url": "https://clients.virginiasbdc.org/events.aspx", "parser": "neoserra"},

    # ============================================================
    # UNIVERSITY AND COLLEGE CENTERS
    # ============================================================
    {"name": "SBDC at University at Albany", "url": "https://www.sbdcalbany.org/course/ai-exchange"},

    # ============================================================
    # RECURRING NATIONAL NETWORKS. chapter-based programmes that run
    # the same format in many cities, week in week out. these are the
    # ones that turn a listings page into a way in, because someone in
    # a small town can join the same room as someone in Kansas City.
    #
    # NOTE ON 1 MILLION CUPS: 160+ communities, every Wednesday 9am,
    # always free. but most chapters meet IN PERSON, and REJECT drops
    # anything in-person. only the virtual and hybrid chapters will
    # survive the filter as things stand. see ALLOW_INPERSON below.
    # ============================================================
    {"name": "1 Million Cups", "url": "https://www.1millioncups.com/communities"},
    {"name": "Startup Grind", "url": "https://www.startupgrind.com/events/"},
    {"name": "Founder Institute", "url": "https://fi.co/events"},
    {"name": "CO by US Chamber", "url": "https://www.uschamber.com/co/events"},
    {"name": "Techstars", "url": "https://www.techstars.com/communities/startup-weekend"},
    {"name": "Hello Alice", "url": "https://helloalice.com/events/"},
    {"name": "NAWBO", "url": "https://www.nawbo.org/events"},

    # ============================================================
    # NONPROFIT AND CDFI
    # ============================================================
    {"name": "Small Business Majority", "url": "https://smallbusinessmajority.org/events"},
    {"name": "Accion Opportunity Fund", "url": "https://aofund.org/events/"},

    # ============================================================
    # POLICY AND ADVOCACY NONPROFITS
    # ============================================================
    {"name": "Right to Start", "url": "https://www.righttostart.org/events"},
    {"name": "America the Entrepreneurial", "url": "https://www.americatheentrepreneurial.org/events"},

    # ============================================================
    # MISSION LENDERS. CDFIs, nonprofit loan funds and community
    # development banks. they run capital-readiness sessions that
    # commercial banks charge for, and they are in every state.
    # ============================================================
    {"name": "Opportunity Finance Network", "url": "https://www.ofn.org/events/"},
    {"name": "CDFI Fund", "url": "https://www.cdfifund.gov/news/events"},
    {"name": "LISC", "url": "https://www.lisc.org/our-resources/events/"},
    {"name": "Kiva", "url": "https://www.kiva.org/borrow/events"},
    {"name": "Grameen America", "url": "https://www.grameenamerica.org/events"},
    {"name": "Native CDFI Network", "url": "https://nativecdfi.net/events/"},
    {"name": "Community Development Bankers Association", "url": "https://www.cdbanks.org/events"},

    # ============================================================
    # LIBRARIES. well-structured calendars, different flavour of event.
    # ============================================================
    # {"name": "New York Public Library", "url": "https://www.nypl.org/events/calendar"},
    # {"name": "Brooklyn Public Library", "url": "https://www.bklynlibrary.org/calendar"},

    # ============================================================
    # CORPORATE PROGRAMMES. all verified as running free live sessions.
    # they are lead generation for the sponsor, which sits against the
    # page's "no sales pitch" line, so weigh each one. the ones below
    # teach rather than demo, which is the test worth applying.
    #
    # coverage against the four stages:
    #   STARTING  Amazon ASBA (Start track), Grow with Google, SCORE
    #   GROWING   Verizon Digital Ready, Salesforce, HubSpot, Meta
    #   SCALING   Amazon ASBA (Launch), Intuit, Square, Shopify
    #   LEADING   CO by US Chamber, Goldman 10KSB, LinkedIn
    # ============================================================
    {"name": "Amazon Small Business Academy", "url": "https://www.amazon.com/smallbusinessacademy"},
    {"name": "Verizon Small Business Digital Ready", "url": "https://digitalready.verizonwireless.com/events"},
    {"name": "Grow with Google", "url": "https://grow.google/events/"},
    {"name": "Salesforce Small Business", "url": "https://www.salesforce.com/small-business/events/"},
    {"name": "Intuit QuickBooks", "url": "https://quickbooks.intuit.com/r/webinars/"},
    {"name": "HubSpot Academy", "url": "https://academy.hubspot.com/events"},
    {"name": "Meta Boost", "url": "https://www.facebook.com/business/boost/events"},
    {"name": "Goldman Sachs 10,000 Small Businesses", "url": "https://www.goldmansachs.com/citizenship/10000-small-businesses/US/events/"},
    {"name": "LinkedIn for Small Business", "url": "https://www.linkedin.com/smallbusiness/events"},

    # not yet confirmed as running a public events calendar. probe first.
    # {"name": "US Bank", "url": "https://www.usbank.com/business-banking/business-resources.html"},
    # {"name": "PayPal", "url": "https://www.paypal.com/us/brc/events"},
    # {"name": "Square", "url": "https://squareup.com/us/en/townsquare/events"},
    # {"name": "Wells Fargo", "url": "https://www.wellsfargo.com/biz/business-resources/"},
]

# topic keyword -> label, first match wins, checked in order
TOPIC_RULES = [
    (r"\b(hire|hiring|employee|contractor|payroll|staff|worker|\bhr\b)", "Hiring"),
    (r"\b(grant|crowdfund|financing|funding|capital|loan|lend|invest)", "Funding"),
    (r"\b(tax|bookkeep|cash flow|financial|profit|accounting|budget)", "Finance"),
    (r"\b(trademark|copyright|patent|contract|legal|llc|s-corp|entity|incorporat|lease)", "Legal"),
    (r"\b(market|brand|content|social|seo|advertis|holiday|customer|sales)", "Marketing"),
    (r"\b(\bai\b|artificial intelligence|automation|software|technolog|digital|website|gemini|workspace)", "Technology"),
    (r"\b(inventory|supply chain|operations|barcode|logistic|process|scal)", "Operations"),
    (r"\b(policy|congress|legislat|ballot|regulat|compliance|midterm)", "Policy"),
]

# The filters are declared once, near the top with ALLOW_INPERSON. A second
# copy used to live here and silently overrode the first, dropping the
# "costs $30" pattern and losing LIVESTREAM entirely.


def log(msg: str) -> None:
    print(msg, file=sys.stderr)


def classify(text: str) -> str:
    low = text.lower()
    for pattern, label in TOPIC_RULES:
        if re.search(pattern, low):
            return label
    return "Business"


def clean(raw: str) -> str:
    txt = BeautifulSoup(raw or "", "html.parser").get_text(" ", strip=True)
    txt = re.sub(r"\s+", " ", txt)
    # brand rule: no dashes as punctuation
    txt = re.sub(r"\s+[\u2013\u2014]\s+", ", ", txt)
    txt = txt.replace("\u2013", " ").replace("\u2014", " ")
    txt = re.sub(r"\s{2,}", " ", txt).strip()
    if len(txt) > SUMMARY_CHARS:
        cut = txt[:SUMMARY_CHARS].rsplit(" ", 1)[0]
        txt = cut.rstrip(",.;:") + "."
    return txt


def walk(node):
    if isinstance(node, dict):
        yield node
        for v in node.values():
            yield from walk(v)
    elif isinstance(node, list):
        for item in node:
            yield from walk(item)


def is_event(block: dict) -> bool:
    kind = block.get("@type", "")
    if isinstance(kind, list):
        return any("Event" in str(k) for k in kind)
    return "Event" in str(kind)


def name_of(value) -> str:
    if isinstance(value, dict):
        return value.get("name") or ""
    if isinstance(value, list):
        return name_of(value[0]) if value else ""
    return str(value or "")


def from_jsonld(soup: BeautifulSoup, source: dict) -> list[dict]:
    found = []
    for tag in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(tag.string or "")
        except (json.JSONDecodeError, TypeError):
            continue
        for block in walk(data):
            if not is_event(block) or not block.get("startDate"):
                continue
            found.append(
                {
                    "title": clean(block.get("name", "")),
                    "host": name_of(block.get("organizer")) or source["name"],
                    "start": block["startDate"],
                    "duration": "",
                    "topic": "",
                    "url": block.get("url") or source["url"],
                    "summary": clean(block.get("description", "")),
                }
            )
    return found


DATE_NEAR_LINK = re.compile(
    r"((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2}"
    r"(?:,\s*|\s+)(?:20\d\d)?(?:\s+(?:from\s+)?\d{1,2}(?::\d{2})?\s*(?:am|pm))?)",
    re.I,
)


def from_headings(soup: BeautifulSoup, source: dict) -> list[dict]:
    """Fallback for pages with no JSON-LD: a heading link followed by a date."""
    found = []
    for tag in soup.find_all(["h2", "h3", "h4", "h5"]):
        link = tag.find("a", href=True)
        if not link:
            continue
        title = clean(link.get_text(" ", strip=True))
        if len(title) < 12:
            continue

        window = " ".join(
            sib.get_text(" ", strip=True)
            for sib in list(tag.next_siblings)[:6]
            if getattr(sib, "get_text", None)
        )
        window = f"{tag.get_text(' ', strip=True)} {window}"

        match = DATE_NEAR_LINK.search(window)
        if not match:
            continue
        try:
            when = dateparse.parse(match.group(1), fuzzy=True)
        except (ValueError, OverflowError):
            continue
        if when.tzinfo is None:
            when = when.replace(tzinfo=timezone(timedelta(hours=-4)))

        found.append(
            {
                "title": title,
                "host": source["name"],
                "start": when.isoformat(),
                "duration": "",
                "topic": "",
                "url": requests.compat.urljoin(source["url"], link["href"]),
                "summary": clean(window[:400]),
            }
        )
    return found


def scrape(source: dict) -> list[dict]:
    try:
        resp = requests.get(source["url"], headers=UA, timeout=TIMEOUT)
        resp.raise_for_status()
    except requests.RequestException as err:
        log(f"  ! {source['name']}: fetch failed ({err})")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")

    # a source may name a dedicated parser. json-ld is still tried first,
    # because when a site publishes it, it is always the better data.
    events = from_jsonld(soup, source)
    how = "json-ld"
    if not events:
        which = source.get("parser")
        if which == "sba":
            events, how = from_sba(soup, source), "sba"
        elif which == "neoserra":
            events, how = from_neoserra(soup, source), "neoserra"
        else:
            events, how = from_headings(soup, source), "headings"

    log(f"  {source['name']}: {len(events)} raw via {how}")
    return events


def from_sba(soup: BeautifulSoup, source: dict) -> list[dict]:
    """sba.gov/events is the national aggregator for every SBA resource partner.

    Each row carries the host organisation separately from the title, which is
    the useful part: a SCORE webinar listed here says SCORE, not SBA, so the
    card credits whoever is actually running it.
    """
    out = []
    for row in soup.select("article, .usa-card, .views-row, li.event"):
        link = row.find("a", href=True)
        if not link:
            continue
        href = link["href"]
        if "/event/" not in href:
            continue
        title = " ".join(link.get_text(" ", strip=True).split())
        if not title:
            continue

        when = ""
        t = row.find("time")
        if t and t.get("datetime"):
            when = t["datetime"]
        else:
            m = re.search(r"[A-Z][a-z]{2,8}\s+\d{1,2},\s+\d{4}[^|]*", row.get_text(" ", strip=True))
            if m:
                when = m.group(0).strip()
        if not when:
            continue

        blob = row.get_text(" ", strip=True)
        # the aggregator lists in-person events too, so drop anything not online
        if not re.search(r"\bonline\b|\bvirtual\b|\bwebinar\b", blob, re.I):
            continue

        host = source["name"]
        h = row.find(attrs={"class": re.compile(r"host|organiz", re.I)})
        if h:
            got = " ".join(h.get_text(" ", strip=True).split())
            if got:
                host = got

        out.append({
            "title": title,
            "host": host,
            "start": when,
            "duration": "",
            "topic": "",
            "url": href if href.startswith("http") else "https://www.sba.gov" + href,
            "summary": blob[:400],
        })
    return out


def from_neoserra(soup: BeautifulSoup, source: dict) -> list[dict]:
    """Neoserra / eCenterDirect, the booking platform most state SBDCs run on.

    Written once, it works for any of them. New York and Virginia are wired up;
    adding another state is one line in SOURCES, no new code.
    """
    out = []
    for row in soup.select("tr, .event, .eventItem, li"):
        link = row.find("a", href=True)
        if not link:
            continue
        href = link["href"]
        if not re.search(r"/events?/\d+|eventId=|confId=", href, re.I):
            continue
        title = " ".join(link.get_text(" ", strip=True).split())
        if len(title) < 8:
            continue

        text = row.get_text(" ", strip=True)
        m = re.search(r"\d{1,2}/\d{1,2}/\d{2,4}(?:\s+\d{1,2}:\d{2}\s*[APap][Mm])?", text)
        if not m:
            m = re.search(r"[A-Z][a-z]{2,8}\s+\d{1,2},\s+\d{4}", text)
        if not m:
            continue

        base = re.match(r"https?://[^/]+", source["url"])
        url = href if href.startswith("http") else (base.group(0) + "/" + href.lstrip("/") if base else href)

        out.append({
            "title": title,
            "host": source["name"],
            "start": m.group(0),
            "duration": "",
            "topic": "",
            "url": url,
            "summary": text[:400],
        })
    return out


def keep(event: dict, now: datetime, horizon: datetime) -> bool:
    blob = f"{event['title']} {event['summary']}"
    # paid, recorded and big-ticket events are never allowed
    if PAID.search(blob) or REPLAY.search(blob) or BIGEVENT.search(blob):
        return False

    if INPERSON.search(blob):
        # a room with a camera in it is still reachable from anywhere
        if not (ALLOW_INPERSON or LIVESTREAM.search(blob)):
            return False
    try:
        when = dateparse.parse(event["start"])
    except (ValueError, OverflowError, TypeError):
        return False
    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)
    return now < when < horizon


def normalize(event: dict) -> dict:
    when = dateparse.parse(event["start"])
    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone(timedelta(hours=-4)))
    event["start"] = when.isoformat()
    event["topic"] = event["topic"] or classify(f"{event['title']} {event['summary']}")
    if not INCLUDE_SUMMARIES:
        event["summary"] = ""
    return event


def dedupe(events: list[dict]) -> list[dict]:
    seen, out = set(), []
    for event in events:
        key = re.sub(r"[^a-z0-9]", "", event["title"].lower())[:45]
        if key in seen:
            continue
        seen.add(key)
        out.append(event)
    return out



def probe() -> int:
    """Check every source and report what it returns.

    With a couple of dozen sources, most of the work is finding out which URLs
    are real and which return usable markup. This does that in one pass so the
    dead ones can be deleted rather than silently failing every Monday.
    """
    log(f"probing {len(SOURCES)} sources\n")
    log(f"  {'source':34s} {'http':>5}  {'via':>9}  {'events':>6}  note")
    log("  " + "-" * 74)
    dead, thin, good = [], [], []
    for src in SOURCES:
        name = src["name"]
        try:
            r = requests.get(src["url"], headers=UA, timeout=TIMEOUT)
            code = r.status_code
        except requests.RequestException as err:
            log(f"  {name:34s} {'---':>5}  {'':>9}  {'':>6}  {type(err).__name__}")
            dead.append(name)
            continue

        if code != 200:
            log(f"  {name:34s} {code:>5}  {'':>9}  {'':>6}  not reachable")
            dead.append(name)
            continue

        soup = BeautifulSoup(r.text, "html.parser")
        got = from_jsonld(soup, src)
        how = "json-ld"
        if not got:
            which = src.get("parser")
            if which == "sba":
                got, how = from_sba(soup, src), "sba"
            elif which == "neoserra":
                got, how = from_neoserra(soup, src), "neoserra"
            else:
                got, how = from_headings(soup, src), "headings"

        now = datetime.now(timezone.utc)
        horizon = now + timedelta(days=HORIZON_DAYS)
        kept = [e for e in got if keep(e, now, horizon)]
        note = ""
        if not got:
            note = "nothing parsed, needs a look"
            thin.append(name)
        elif not kept:
            note = "parsed, but all filtered out"
            thin.append(name)
        else:
            good.append(name)
        log(f"  {name:34s} {code:>5}  {how:>9}  {len(kept):>6}  {note}")

    log(f"\n  {len(good)} returning events, {len(thin)} reachable but empty, {len(dead)} unreachable")
    if dead:
        log(f"  unreachable: {', '.join(dead)}")
    if thin:
        log(f"  empty:       {', '.join(thin)}")
    log("\n  delete the unreachable ones. the empty ones either have no events")
    log("  right now or need their own parser.")
    return 0

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="print, do not write")
    ap.add_argument("--probe", action="store_true",
                    help="check every source and report what it returns, then stop")
    ap.add_argument("--min-events", type=int, default=5,
                    help="absolute floor, refuse to write fewer than this (default 5)")
    ap.add_argument("--allow-shrink", action="store_true",
                    help="write even when the result is smaller than the existing file")
    args = ap.parse_args()

    now = datetime.now(timezone.utc)
    horizon = now + timedelta(days=HORIZON_DAYS)

    if args.probe:
        return probe()

    log(f"scraping {len(SOURCES)} sources...")
    raw = []
    for source in SOURCES:
        raw.extend(scrape(source))

    events = [normalize(e) for e in raw if keep(e, now, horizon)]

    if PINNED.exists():
        pinned = json.loads(PINNED.read_text()).get("events", [])
        pinned = [normalize(e) for e in pinned if keep(e, now, horizon)]
        log(f"  pinned: {len(pinned)} kept")
        events = pinned + events

    events = dedupe(events)
    events.sort(key=lambda e: e["start"])

    log(f"\n{len(events)} events after filtering")
    for e in events:
        log(f"  {e['start'][:10]}  {e['topic']:<11} {e['host'][:28]:<28} {e['title'][:44]}")

    if args.dry_run:
        return 0

    # Never replace a healthy file with a thinner one. A site redesign that
    # breaks a parser should leave last week's page standing, not shrink it.
    #
    # This used to run only when the scrape returned fewer than --min-events,
    # so a run that came back with 6 against an existing 17 wrote silently and
    # the page lost eleven events. The comparison against the existing file now
    # happens on every run, whatever the count.
    previous = 0
    if OUT.exists():
        try:
            previous = len(json.loads(OUT.read_text()).get("events", []))
        except (json.JSONDecodeError, OSError):
            previous = 0

    if previous and len(events) < previous:
        log(f"\nREFUSING to write: got {len(events)}, existing file has {previous}.")
        log("A source likely changed its markup. Leaving events.json alone.")
        log("Re-run with --allow-shrink once you have confirmed events really did drop off.")
        if not args.allow_shrink:
            return 1
        log("--allow-shrink set, writing anyway.")

    if len(events) < args.min_events:
        log(f"\nREFUSING to write: only {len(events)} events, floor is {args.min_events}.")
        return 1

    OUT.write_text(
        json.dumps(
            {
                "updated": now.date().isoformat(),
                "note": "Generated by scrape_events.py. Hand additions go in pinned.json.",
                "events": events,
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    log(f"\nwrote {OUT} with {len(events)} events")
    return 0


if __name__ == "__main__":
    sys.exit(main())
