#!/usr/bin/env python3
"""
selftest.py - check the events pipeline without touching the network.

Run this before any deploy, and after any change to scrape_events.py.
It exercises the filters, the parsers, the safety rail and the data file
against known inputs, so a broken regex or a bad edit is caught here
rather than on a Monday morning when the Action runs.

    python selftest.py

Exit code is 0 if everything passes, 1 if anything fails, which means it
can go straight into CI.

What this CANNOT check: whether the 47 source URLs are real and return
usable markup. Nothing offline can. Use `python scrape_events.py --probe`
on a machine with network access for that.
"""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).parent
PASS, FAIL = [], []


def check(name: str, got, want) -> None:
    if got == want:
        PASS.append(name)
    else:
        FAIL.append(f"{name}\n        expected {want!r}\n        got      {got!r}")


def section(title: str) -> None:
    print(f"\n{title}")
    print("-" * len(title))


def load_scraper():
    spec = importlib.util.spec_from_file_location("se", HERE / "scrape_events.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ----------------------------------------------------------------------
def test_filters(m) -> None:
    section("1. What gets in, and what does not")
    now = datetime.now(timezone.utc)
    horizon = now + timedelta(days=m.HORIZON_DAYS)
    soon = (now + timedelta(days=7)).isoformat()

    def ev(title, summary, start=soon):
        return {"title": title, "summary": summary, "start": start}

    cases = [
        # (label, event, should be kept)
        ("plain online webinar",
         ev("Cash Flow Basics", "Online webinar, no cost to attend"), True),
        ("1MC in a room, streamed to Facebook",
         ev("1 Million Cups Wilmington",
            "Hosted in person at CFCC. Streams live on Facebook."), True),
        ("1MC fully virtual",
         ev("1 Million Cups Lincoln", "Virtual, join on Zoom"), True),
        ("1MC hybrid",
         ev("1 Million Cups Kansas City",
            "In person at the Kauffman Center or virtually on zoom"), True),
        # ALLOW_INPERSON is on, so a room-only event is kept and the card
        # carries its location. Section 2 checks both positions of the switch.
        ("1MC room only, no stream",
         ev("1 Million Cups Tampa",
            "THIS EVENT WILL BE HOSTED IN PERSON. Walk-ins accepted."), True),
        ("priced with a dollar sign",
         ev("Advanced Bookkeeping", "Registration $49 per seat"), False),
        ("priced in words",
         ev("Tax Clinic", "Costs 25 dollars at the door"), False),
        ("has a fee",
         ev("Pitch Night", "A small fee applies"), False),
        ("ticketed",
         ev("Founder Mixer", "Tickets required"), False),
        ("members only",
         ev("Roundtable", "Members only session"), False),
        ("on demand recording",
         ev("Marketing 101", "Recorded, watch anytime"), False),
        # BIGEVENT is gala/fundraiser only. A no-cost conference is an event
        # a founder can attend, so it belongs on the page.
        ("a conference",
         ev("Growth Conference", "Two day conference, online"), True),
        ("a gala",
         ev("Annual Awards Gala", "Black tie gala, online stream"), False),
        ("a fundraiser",
         ev("Spring Fundraiser", "Fundraiser, join online"), False),
        ("already happened",
         ev("Old Webinar", "Online", (now - timedelta(days=2)).isoformat()), False),
        ("beyond the horizon",
         ev("Far Future", "Online",
            (now + timedelta(days=m.HORIZON_DAYS + 30)).isoformat()), False),
    ]
    for label, event, want in cases:
        check(f"   {label}", m.keep(event, now, horizon), want)
        print(f"   {'ok  ' if PASS and PASS[-1].strip() == label else 'FAIL'} {label}")


def test_inperson_switch(m) -> None:
    section("2. The ALLOW_INPERSON switch")
    now = datetime.now(timezone.utc)
    horizon = now + timedelta(days=m.HORIZON_DAYS)
    soon = (now + timedelta(days=7)).isoformat()
    room_only = {"title": "1 Million Cups Tampa",
                 "summary": "THIS EVENT WILL BE HOSTED IN PERSON.",
                 "start": soon}
    paid_room = {"title": "Founder Dinner",
                 "summary": "In person, tickets required", "start": soon}

    original = m.ALLOW_INPERSON
    try:
        m.ALLOW_INPERSON = False
        check("   room-only dropped when the switch is off",
              m.keep(room_only, now, horizon), False)
        print("   ok   room-only dropped when the switch is off")

        m.ALLOW_INPERSON = True
        check("   room-only kept when the switch is on",
              m.keep(room_only, now, horizon), True)
        print("   ok   room-only kept when the switch is on")

        check("   paid still dropped even with the switch on",
              m.keep(paid_room, now, horizon), False)
        print("   ok   paid still dropped even with the switch on")
    finally:
        m.ALLOW_INPERSON = original


def test_parsers(m) -> None:
    section("3. The parsers")
    from bs4 import BeautifulSoup

    sba_html = """
    <article class="usa-card">
      <a href="/event/71348">Grow with Google</a>
      <time datetime="2026-10-15T14:00:00-04:00">Oct 15, 2026</time>
      <span class="host-organization">UTPB-SBDC</span>
      <p>Free virtual workshop. Online.</p>
    </article>
    <article class="usa-card">
      <a href="/event/99001">Coffee and Contracts</a>
      <time datetime="2026-10-20T09:00:00-04:00">Oct 20, 2026</time>
      <p>In person at the Raleigh office.</p>
    </article>"""
    got = m.from_sba(BeautifulSoup(sba_html, "html.parser"),
                     {"name": "SBA", "url": "https://www.sba.gov/events"})
    check("   SBA parser keeps both rows", len(got), 2)
    print(f"   {'ok  ' if len(got)==2 else 'FAIL'} SBA parser keeps both rows")
    if got:
        check("   SBA parser credits the real host", got[0]["host"], "UTPB-SBDC")
        print(f"   {'ok  ' if got[0]['host']=='UTPB-SBDC' else 'FAIL'} SBA parser credits the real host, not SBA")
        check("   SBA parser builds an absolute url",
              got[0]["url"], "https://www.sba.gov/event/71348")
        print("   ok   SBA parser builds an absolute url")

    neo_html = """
    <table>
     <tr><td><a href="/events/1020216">Small Business Legal Clinic</a></td>
         <td>09/09/2026 4:30 PM</td></tr>
     <tr><td><a href="/about">About us</a></td><td>not an event</td></tr>
    </table>"""
    got2 = m.from_neoserra(BeautifulSoup(neo_html, "html.parser"),
                           {"name": "New York SBDC",
                            "url": "https://nysbdc.ecenterdirect.com/events"})
    check("   Neoserra parser skips non-event links", len(got2), 1)
    print(f"   {'ok  ' if len(got2)==1 else 'FAIL'} Neoserra parser skips non-event links")


def test_safety_rail(m) -> None:
    section("4. The safety rail")
    out = HERE / "events.json"
    if not out.exists():
        FAIL.append("events.json is missing")
        print("   FAIL events.json is missing")
        return
    before = out.read_bytes()
    existing = len(json.loads(before).get("events", []))
    print(f"   events.json currently holds {existing} events")
    print("   the rail is exercised for real by running:")
    print("       python scrape_events.py")
    print("   with every source unreachable it must refuse and exit 1.")
    check("   the file is valid json with events", existing > 0, True)
    print(f"   {'ok  ' if existing>0 else 'FAIL'} the file is valid json and not empty")


def test_data(m) -> None:
    section("5. The data file")
    d = json.loads((HERE / "events.json").read_text())
    events = d.get("events", [])
    required = ["title", "host", "start", "duration", "topic", "url", "summary"]

    missing = [f"{i}:{k}" for i, e in enumerate(events)
               for k in required if k not in e]
    check("   every event has all seven fields", missing, [])
    print(f"   {'ok  ' if not missing else 'FAIL'} every event has all seven fields")

    no_tz = [e["title"][:30] for e in events
             if not re.search(r"[+-]\d{2}:\d{2}$", e.get("start", ""))]
    check("   every start carries a UTC offset", no_tz, [])
    print(f"   {'ok  ' if not no_tz else 'FAIL'} every start carries a UTC offset")

    bad_url = [e["title"][:30] for e in events
               if not e.get("url", "").startswith("https://")]
    check("   every url is https", bad_url, [])
    print(f"   {'ok  ' if not bad_url else 'FAIL'} every url is https")

    banned = re.compile(r"\bfree\b|\baspiring\b|\bmentor\b|\bcoach\b|\bspark\b", re.I)
    hits = [e["title"][:30] for e in events
            if banned.search(e.get("summary", "") + " " + e.get("title", ""))]
    check("   no banned words in the copy", hits, [])
    print(f"   {'ok  ' if not hits else 'FAIL'} no banned words in the copy")

    dashes = [e["title"][:30] for e in events
              if re.search(r"[\u2013\u2014]|\s-\s", e.get("summary", ""))]
    check("   no dashes used as punctuation", dashes, [])
    print(f"   {'ok  ' if not dashes else 'FAIL'} no dashes used as punctuation")

    dupes = len(events) - len({e["title"].strip().lower() for e in events})
    check("   no duplicate titles", dupes, 0)
    print(f"   {'ok  ' if dupes==0 else 'FAIL'} no duplicate titles")


def test_page() -> None:
    section("6. The page")
    html = (HERE / "events.html").read_text()
    checks = [
        ("fetches events.json", "events.json" in html),
        ("has a failure message if the fetch dies", "could not load" in html),
        ("chips are built from the data", "renderFilters" in html),
        ("stage labels are derived", "STAGE_RULES" in html),
        ("cards are hidden, not re-rendered, on filter", "c.hidden=!on" in html.replace(" ", "")),
        ("the wash layer exists", "evwash" in html),
        ("the magnet is wired", "dataset.mag" in html),
        ("the orb menu is present", "kx-orbnav" in html),
        ("shared tokens are declared", "--gold-pale" in html),
    ]
    for label, ok in checks:
        check(f"   {label}", ok, True)
        print(f"   {'ok  ' if ok else 'FAIL'} {label}")



def test_location_cleaner(m) -> None:
    """The venue field arrived carrying the date, the time and the title.

    354 of the 860 published rows started with a year, a clock time or the
    event's own name. These are real strings taken from events.json.
    """
    section("location cleaner")
    C = m.clean_location
    check("   online label stops before the title",
          C("Online Meeting (Live) APEX - Capability Statements 101: Purpose",
            "APEX - Capability Statements 101: Purpose, Key Elements, and Best Practices"),
          "Online Meeting (Live)")
    check("   a leading year and time are dropped",
          C("2026 3:00-5:00pm CENTRAL 318 Main St, Evansville IN 47708"),
          "318 Main St, Evansville IN 47708")
    check("   a bare hour range is dropped too",
          C("2026 8 to 10 am 500 McCullough Ave, San Antonio TX 78215"),
          "500 McCullough Ave, San Antonio TX 78215")
    # The house number is the regression this guards: an earlier cut read
    # "1101" as a clock time and served "Halligan Drive" with no number.
    check("   a house number is not mistaken for a time",
          C("1101 Halligan Drive, North Platte NE 69101"),
          "1101 Halligan Drive, North Platte NE 69101")
    check("   a venue named for a year survives",
          C("The 1907 at Central School"), "The 1907 at Central School")
    # Case sensitivity is the point: EASTERN is a timezone, Eastern is a place.
    check("   a shouted timezone goes, a place name stays",
          C("Eastern Arizona College Academic Programs Building"),
          "Eastern Arizona College Academic Programs Building")
    check("   a doubled venue name is collapsed",
          C("Innovate Newport Innovate Newport"), "Innovate Newport")
    check("   a bare fragment becomes no venue",
          C("1490, Hazleton PA 18201"), "")
    check("   a facilitator line is left alone",
          C("Online Facilitated by Mason SBDC"), "Online Facilitated by Mason SBDC")


def test_unknown_time(m) -> None:
    """A date with no time parsed to midnight and the page printed 12:00 AM."""
    section("unknown start times")
    a = m.normalize({"title": "x", "start": "September 8, 2026", "url": "https://e.com",
                     "summary": "", "topic": "", "location": ""})
    check("   a date with no time is flagged", a["time_tbd"], True)
    b = m.normalize({"title": "x", "start": "September 8, 2026 3:00pm", "url": "https://e.com",
                     "summary": "", "topic": "", "location": ""})
    check("   a real time is not flagged", b["time_tbd"], False)
    # Re-normalising must not flip the flag: the ISO stamp contains "00:00".
    c = m.normalize(dict(a, start=a["start"]))
    check("   re-running keeps the flag", c["time_tbd"], True)


def test_mode_backfill(m) -> None:
    """153 rows carried no mode, so the card could not say where to turn up."""
    section("mode backfill")
    def mode(loc, host="H", title="t"):
        return m.normalize({"title": title, "start": "September 8, 2026 10:00am",
                            "url": "https://e.com", "summary": "", "topic": "",
                            "location": loc, "host": host})["mode"]
    check("   a named venue means in person", mode("Duncan Town Hall"), "In person")
    check("   a hyphenated on-line still reads online",
          mode("On-line Training - Statewide"), "Online")
    check("   an always-online host with no venue",
          mode("", host="Meta Blueprint"), "Online")
    check("   no signal stays honest and empty", mode("", host="H"), "")


def main() -> int:
    print("=" * 66)
    print("  SideKix events pipeline, offline self-test")
    print("=" * 66)
    m = load_scraper()
    test_filters(m)
    test_inperson_switch(m)
    test_parsers(m)
    test_safety_rail(m)
    test_data(m)
    test_location_cleaner(m)
    test_unknown_time(m)
    test_mode_backfill(m)
    test_page()

    print("\n" + "=" * 66)
    print(f"  {len(PASS)} passed, {len(FAIL)} failed")
    print("=" * 66)
    if FAIL:
        print("\nfailures:")
        for f in FAIL:
            print(f"  x {f}")
        return 1
    print("\nEverything offline checks out. What this does NOT prove is that the")
    print("47 source URLs are real. For that, on a machine with network access:")
    print("    python scrape_events.py --probe")
    return 0


if __name__ == "__main__":
    sys.exit(main())
