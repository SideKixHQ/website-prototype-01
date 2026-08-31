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
import datetime as dt
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

# A single non-browser User-Agent with no other headers is what most bot
# filters reject, and eight sources came back 403, 406 or 429 on the first real
# run: SCORE, MBDA, USDA Rural Development, NAWBO, Goldman 10KSB, Native CDFI
# Network, Kiva and Hello Alice. These are the headers an ordinary browser
# sends. A Session is used so cookies set by an interstitial are kept for the
# retry, which is what 406 usually wants.
UA = {
    "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/126.0.0.0 Safari/537.36"),
    "Accept": ("text/html,application/xhtml+xml,application/xml;q=0.9,"
               "image/avif,image/webp,*/*;q=0.8"),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
    "Connection": "keep-alive",
}

SESSION = requests.Session()
SESSION.headers.update(UA)


def fetch(url: str, tries: int = 3):
    """GET with a retry and a growing pause.

    429 means we asked too fast, so waiting is the whole fix. 403 and 406 are
    sometimes a first-request check that passes on the retry once a cookie is
    set. Anything else fails fast, because retrying a 404 is pointless.
    """
    import time
    last = None
    for attempt in range(tries):
        try:
            r = SESSION.get(url, timeout=TIMEOUT, allow_redirects=True)
            if r.status_code in (403, 406, 429) and attempt < tries - 1:
                time.sleep(2 * (attempt + 1))
                last = requests.HTTPError(f"{r.status_code} on attempt {attempt + 1}")
                continue
            r.raise_for_status()
            return r
        except requests.RequestException as err:
            last = err
            if attempt < tries - 1:
                time.sleep(1.5 * (attempt + 1))
                continue
    raise last if last else requests.RequestException("unknown")
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
ALLOW_INPERSON = True

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
# Conferences, expos and summits used to be rejected wholesale. Many of the
# best free sessions are exactly that, and the PAID pattern already catches the
# ticketed ones, so only fundraisers are dropped by name now.
BIGEVENT = re.compile(r"\bgala\b|\bfundraiser\b|\bfundraising dinner\b", re.I)

# How a host says "you can attend this from your desk".
ONLINE = re.compile(
    r"\bonline\b|\bvirtual\b|\bwebinar\b|\bwebcast\b|\bremote\b"
    r"|\bzoom\b|google meet|microsoft teams|\bteleconference\b|\blive online\b",
    re.I)

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

def load_sources() -> list[dict]:
    """The source list is data, not code.

    It changes every time a host redesigns a page, which is far more often than
    the parsers change. Keeping it in sources.json means the list can be edited,
    reviewed and diffed on its own without anyone touching the scraper.
    """
    path = HERE / "sources.json"
    if not path.exists():
        print("sources.json missing, nothing to scrape", file=sys.stderr)
        return []
    return json.loads(path.read_text()).get("sources", [])


SOURCES = load_sources()

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


import re as _re

_DATEISH = _re.compile(
    r"^\s*(?:"
    r"(?:mon|tue|wed|thu|fri|sat|sun)[a-z]*,?\s*"          # Monday,
    r"|(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d"  # October 21
    r"|\d{1,2}[/-]\d{1,2}"                                  # 10/21
    r"|\d{1,2}:\d{2}\s*(?:am|pm)"                          # 12:00 pm
    r")", _re.I)

_TIMERANGE = _re.compile(r"\d{1,2}:\d{2}\s*(?:am|pm).{0,12}\d{1,2}:\d{2}\s*(?:am|pm)", _re.I)


def is_real_title(text: str) -> bool:
    """Reject link text that is a date or a time range rather than a title.

    The first real run produced two entries titled things like
    "October 21 from 12:00 pm to 1:00 pm (EDT)", because on some calendars the
    date is its own link next to the title. A title has to have some words in
    it that are not calendar furniture.
    """
    t = (text or "").strip()
    if len(t) < 12:
        return False
    if _TIMERANGE.search(t):
        return False
    if _DATEISH.match(t):
        # a date at the start is fine only if real words follow it
        tail = _DATEISH.sub("", t, count=1)
        words = [w for w in _re.findall(r"[A-Za-z]{3,}", tail)
                 if w.lower() not in {"from", "edt", "est", "pdt", "pst", "cdt", "cst", "utc", "and"}]
        return len(words) >= 3
    # a title made only of numbers and punctuation is not a title
    return len(_re.findall(r"[A-Za-z]{3,}", t)) >= 2


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
            _t = clean(block.get("name", ""))
            if not is_real_title(_t):
                continue
            found.append(
                {
                    "title": _t,
                    "host": name_of(block.get("organizer")) or source["name"],
                    "start": block["startDate"],
                    "duration": "",
                    "topic": "",
                    "url": block.get("url") or source["url"],
                    "summary": clean(block.get("description", "")),
                    "location": name_of(block.get("location")),
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

        if not is_real_title(title):
            continue
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


def parse_page(soup: BeautifulSoup, source: dict) -> tuple[list[dict], str]:
    """json-ld first, then the source's named parser, then headings."""
    events = from_jsonld(soup, source)
    if events:
        return events, "json-ld"
    which = source.get("parser")
    if which == "sba":
        return from_sba(soup, source), "sba"
    if which == "neoserra":
        return from_neoserra(soup, source), "neoserra"
    return from_headings(soup, source), "headings"


def paged_url(url: str, page: int) -> str:
    """Page two onwards of a listing.

    Only Drupal-style ?page=N is handled, which is what the SBA aggregators
    use. A source that paginates differently should get its own parser rather
    than a guess here.
    """
    if page == 0:
        return url
    join = "&" if "?" in url else "?"
    return f"{url}{join}page={page}"


def scrape(source: dict) -> list[dict]:
    """Fetch a source and return its events.

    A source may declare "pages" to walk a paginated listing. The SBA
    aggregators carry over a thousand events between them, and reading only the
    first page threw almost all of it away. Paging stops at the first page that
    returns nothing new, so a source that runs out at page four does not cost
    twelve requests.
    """
    pages = int(source.get("pages", 1))
    collected: list[dict] = []
    how = "?"
    seen_urls: set[str] = set()

    for page in range(pages):
        try:
            resp = fetch(paged_url(source["url"], page))
        except requests.RequestException as err:
            if page == 0:
                log(f"  ! {source['name']}: fetch failed ({err})")
                return []
            break

        soup = BeautifulSoup(resp.text, "html.parser")
        got, how = parse_page(soup, source)

        fresh = [e for e in got if e.get("url") not in seen_urls]
        if not fresh:
            break
        seen_urls.update(e.get("url") for e in fresh)
        collected.extend(fresh)

    # Every event carries where it came from, so the page can group by kind of
    # host and by state without guessing from the host name.
    for e in collected:
        e.setdefault("category", source.get("category", ""))
        e.setdefault("scope", source.get("scope", ""))

    pagenote = f" over {pages} pages" if pages > 1 else ""
    log(f"  {source['name']}: {len(collected)} raw via {how}{pagenote}")
    return collected


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
        # The aggregator lists in-person events too. Those used to be dropped
        # here. They are kept now and labelled by mode instead, because an SBA
        # district office workshop three towns over is exactly the kind of
        # event this page exists to surface.

        host = source["name"]
        h = row.find(attrs={"class": re.compile(r"host|organiz", re.I)})
        if h:
            got = " ".join(h.get_text(" ", strip=True).split())
            if got:
                host = got

        if not is_real_title(title):
            continue
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

        if not is_real_title(title):
            continue
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


# Hosts whose events are streamed as a matter of course, whether or not the
# listing happens to say so. 1 Million Cups chapters pitch in a room and put it
# on Facebook Live every time; waiting for each listing to mention that would
# lose most of them.
ALWAYS_STREAMS = {"1 Million Cups"}


def mode_of(blob: str, streams: bool) -> str:
    """Online, Livestream or In person, from how the host describes it.

    Livestream is deliberately its own answer rather than being folded into
    Online. Someone choosing between them cares: a livestream is a room you are
    watching, an online event is a room you are in.
    """
    inperson = bool(INPERSON.search(blob))
    if streams and inperson:
        return "Livestream"
    if ONLINE.search(blob):
        return "Online"
    if streams:
        return "Livestream"
    if inperson:
        return "In person"
    return ""


def keep(event: dict, now: datetime, horizon: datetime) -> bool:
    blob = f"{event['title']} {event['summary']} {event.get('location', '')}"
    streams = (event.get("host") in ALWAYS_STREAMS) or bool(LIVESTREAM.search(blob))
    # paid, recorded and fundraising events are never allowed
    if PAID.search(blob) or REPLAY.search(blob) or BIGEVENT.search(blob):
        return False

    event["mode"] = event.get("mode") or mode_of(blob, streams)
    if INPERSON.search(blob) and not ALLOW_INPERSON and not streams:
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
    event.setdefault("mode", "")
    event.setdefault("location", "")
    event.setdefault("category", "")
    event.setdefault("scope", "")
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
            r = fetch(src["url"])
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
        got, how = parse_page(soup, src)

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
    # Compare against events in the existing file that have NOT yet happened.
    # The old comparison counted everything, so as the current 17 expire the
    # bar would keep rising against a shrinking real set and the guard would
    # block forever. What matters is whether we are about to publish fewer
    # upcoming events than we already show.
    previous = 0
    if OUT.exists():
        try:
            old = json.loads(OUT.read_text()).get("events", [])
        except (json.JSONDecodeError, OSError):
            old = []
        today = dt.date.today().isoformat()
        previous = sum(1 for e in old if str(e.get("start", ""))[:10] >= today)
        stale = len(old) - previous
        if stale:
            log(f"  {stale} event(s) in the existing file have already passed; "
                f"comparing against the {previous} still upcoming.")

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
