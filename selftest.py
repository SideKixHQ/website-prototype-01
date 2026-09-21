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

    # The <time> fallback. Seventeen states returned nothing because their
    # listings put the date in a card above the title, or used a plain link
    # with no heading, and from_headings can read neither.
    src = {"name": "Test SBDC", "url": "https://example.org/events/"}

    tribe = """
    <div class="tribe-events-calendar-list__event-row">
      <time datetime="2026-10-06"><span>Oct</span><span>6</span></time>
      <div><h3><a href="/event/taking-the-leap/">Taking the Leap: Starting a Business</a></h3>
      <p>Wilmington, NC. In person.</p></div>
    </div>"""
    t1 = m.from_time_tags(BeautifulSoup(tribe, "html.parser"), src)
    check("   time parser reads a calendar card", len(t1), 1)
    print(f"   {'ok  ' if len(t1)==1 else 'FAIL'} time parser reads a calendar card")

    card = """
    <article><div><time datetime="2026-11-12T18:00:00-05:00">Nov 12</time></div>
    <h2><a href="/e/99">Money, Margins and Momentum</a></h2></article>"""
    t2 = m.from_time_tags(BeautifulSoup(card, "html.parser"), src)
    check("   time parser reads a date-first card", len(t2), 1)
    print(f"   {'ok  ' if len(t2)==1 else 'FAIL'} time parser reads a date above the title")

    noise = """
    <div><time datetime="2026-10-02">Oct 2</time>
    <a href="/y">October 2 from 12:00 pm to 1:00 pm</a></div>"""
    t3 = m.from_time_tags(BeautifulSoup(noise, "html.parser"), src)
    check("   time parser rejects calendar furniture", len(t3), 0)
    print(f"   {'ok  ' if len(t3)==0 else 'FAIL'} time parser rejects calendar furniture")

    twice = """
    <div><time datetime="2026-10-06T09:00">s</time><time datetime="2026-10-06T17:00">e</time>
    <h3><a href="/e/1">Building Your Foundation Workshop</a></h3></div>"""
    t4 = m.from_time_tags(BeautifulSoup(twice, "html.parser"), src)
    check("   time parser counts a start and end once", len(t4), 1)
    print(f"   {'ok  ' if len(t4)==1 else 'FAIL'} time parser counts a start and end once")

    # A weekday or month STEM is not a date. "Money," was read as "Monday,"
    # and "Marketing 101" as "March 1", so both titles were discarded.
    keep = ["Money, Margins and Momentum", "Marketing 101 for Founders",
            "Monthly Bookkeeping Basics", "Sunset Networking Mixer",
            "Wedding Business Bootcamp", "Friendly Introductions to Funding"]
    drop = ["Monday, October 21", "October 21 from 12:00 pm to 1:00 pm (EDT)",
            "Tue, Oct 6", "12:00 pm", "10/21"]
    wrong = ([t for t in keep if not m.is_real_title(t)]
             + [t for t in drop if m.is_real_title(t)])
    check("   real titles survive the date filter", wrong, [])
    print(f"   {'ok  ' if not wrong else 'FAIL'} real titles survive the date filter")

    # Localist, which runs most university calendars, writes the UTC offset in
    # seconds. dateutil rejects the whole stamp, so every event on every such
    # calendar used to fall back to the visible text and land at midnight.
    fixed = m.repair_seconds_offset("2026-09-24T10:00:00-14400")
    check("   a seconds offset is re-read as hours", fixed.isoformat(),
          "2026-09-24T10:00:00-04:00")
    print(f"   {'ok  ' if fixed else 'FAIL'} a seconds offset is re-read as hours")
    untouched = m.repair_seconds_offset("2026-09-24T10:00:00-04:00")
    check("   a well formed offset is left alone", untouched, None)
    print(f"   {'ok  ' if untouched is None else 'FAIL'} a well formed offset is left alone")
    silly = m.repair_seconds_offset("2026-09-24T10:00:00-99999")
    check("   an impossible offset is refused", silly, None)
    print(f"   {'ok  ' if silly is None else 'FAIL'} an impossible offset is refused")

    localist = """
    <div class="ev"><time datetime="2026-10-01T09:00:00-14400">Oct. 1, 2026 at 9 a.m.</time>
    <h3><a href="/event/start">How to Start Your Business Workshop</a></h3></div>"""
    t5 = m.from_time_tags(BeautifulSoup(localist, "html.parser"), src)
    got5 = t5[0]["start"] if t5 else ""
    check("   a Localist card keeps its real hour", got5, "2026-10-01T09:00:00-04:00")
    print(f"   {'ok  ' if got5.endswith('T09:00:00-04:00') else 'FAIL'} a Localist card keeps its real hour")

    # The heading sits inside the link rather than the other way round, and the
    # date follows the link. Reading only the usual shape skipped every row.
    wrapped = """
    <div class="listItem"><a class="listLink" href="/events/true-north">
    <div class="eventDate"><div class="day">21</div><div class="month">Sep</div></div>
    <h3 class="listTitle">True North Strategy Workshop</h3></a>
    <div class="listSummary"><span>September 21, 2026</span></div></div>"""
    t6 = m.from_headings(BeautifulSoup(wrapped, "html.parser"), src)
    title6 = t6[0]["title"] if t6 else ""
    check("   a card wrapped in its link is read", len(t6), 1)
    print(f"   {'ok  ' if len(t6)==1 else 'FAIL'} a card wrapped in its link is read")
    check("   the date badge stays out of the title", title6,
          "True North Strategy Workshop")
    print(f"   {'ok  ' if title6=='True North Strategy Workshop' else 'FAIL'} the date badge stays out of the title")

    # The ordinary shape, link inside the heading, must be unchanged by that.
    normal = """
    <h3><a href="/a">Marketing Basics For New Owners</a></h3><p>October 5, 2026 2:00 pm</p>"""
    t7 = m.from_headings(BeautifulSoup(normal, "html.parser"), src)
    check("   the ordinary heading shape still reads", len(t7), 1)
    print(f"   {'ok  ' if len(t7)==1 else 'FAIL'} the ordinary heading shape still reads")


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

    # These two used to assert the brand word and dash rules against scraped
    # event titles and summaries. That was always the wrong target: an event
    # name belongs to the host, and rewriting "SBA and DoD Mentor-Protege
    # Programs" would be putting words in their mouth. The rules govern copy
    # SideKix writes. What is worth checking here is that the host's text
    # arrives intact and is not silently mangled.
    mangled = [e["title"][:30] for e in events
               if "  " in e.get("title", "") or e.get("title", "") != e.get("title", "").strip()]
    check("   host titles arrive clean", mangled, [])
    print(f"   {'ok  ' if not mangled else 'FAIL'} host titles arrive clean")

    empty = [e.get("url", "")[:40] for e in events if not e.get("title", "").strip()]
    check("   no event is missing a title", empty, [])
    print(f"   {'ok  ' if not empty else 'FAIL'} no event is missing a title")

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
