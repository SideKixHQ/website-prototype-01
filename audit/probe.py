import os
# the pages live at the repository root, and this script sits in audit/
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import re
p=ROOT+"/scrape_events.py"
s=open(p,encoding="utf-8").read()

# a probe mode: check every source and report what it actually returns
old = '''    ap.add_argument("--dry-run", action="store_true", help="print, do not write")'''
assert s.count(old)==1
new = '''    ap.add_argument("--dry-run", action="store_true", help="print, do not write")
    ap.add_argument("--probe", action="store_true",
                    help="check every source and report what it returns, then stop")'''
s=s.replace(old,new)

old2 = '''    log(f"scraping {len(SOURCES)} sources...")'''
assert s.count(old2)==1
new2 = '''    if args.probe:
        return probe()

    log(f"scraping {len(SOURCES)} sources...")'''
s=s.replace(old2,new2)

probe_fn = '''

def probe() -> int:
    """Check every source and report what it returns.

    With a couple of dozen sources, most of the work is finding out which URLs
    are real and which return usable markup. This does that in one pass so the
    dead ones can be deleted rather than silently failing every Monday.
    """
    log(f"probing {len(SOURCES)} sources\\n")
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

    log(f"\\n  {len(good)} returning events, {len(thin)} reachable but empty, {len(dead)} unreachable")
    if dead:
        log(f"  unreachable: {', '.join(dead)}")
    if thin:
        log(f"  empty:       {', '.join(thin)}")
    log("\\n  delete the unreachable ones. the empty ones either have no events")
    log("  right now or need their own parser.")
    return 0
'''
s = s.replace("\ndef main()", probe_fn + "\ndef main()", 1)
open(p,"w",encoding="utf-8").write(s)
print("probe mode added")
