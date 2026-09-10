# -*- coding: utf-8 -*-
"""Build jobs-map.json: where people work against where they live.

Everything here is free federal data.

  LODES  https://lehd.ces.census.gov/data/lodes/  block level, 2002 to 2023
         WAC = jobs located in a block. RAC = employed residents living in one.
         OD  = origin and destination pairs, which gives commute flows.
  TIGER  https://tigerweb.geo.census.gov/  tract geometry, public domain.

The point of the map is the imbalance. A tract with far more jobs than resident
workers is an employment centre. A tract with far more resident workers than
jobs is a bedroom community, and its residents are commuting out of it every
morning. That gap is the whole Homegrown argument, drawn from public data.

Run:  python3 build/mkjobsmap.py
      python3 build/mkjobsmap.py --region 37129,37019     (any county FIPS)
      python3 build/mkjobsmap.py --year 2021

Needs outbound network to census.gov. Writes jobs-map.json at the repo root.
"""
import os, sys, json, gzip, csv, io, argparse, urllib.request, urllib.error, collections, datetime

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
OUT = os.path.join(_ROOT, "jobs-map.json")

LODES = "https://lehd.ces.census.gov/data/lodes/LODES8"
TIGER = ("https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb"
         "/Tracts_Blocks/MapServer/0/query")

# The Cape Fear workforce area by default: New Hanover, Brunswick, Pender, Columbus.
DEFAULT_REGION = {
    "37129": "New Hanover",
    "37019": "Brunswick",
    "37141": "Pender",
    "37047": "Columbus",
}
STATE_OF = {"37": "nc"}


def _get(url, label, tries=3):
    """Fetch with a real user agent. census.gov rejects the python default."""
    req = urllib.request.Request(url, headers={
        "User-Agent": "SideKix-Homegrown/1.0 (+https://sidekixhq.com) python-urllib",
        "Accept": "*/*",
    })
    last = None
    for attempt in range(1, tries + 1):
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                return r.read()
        except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
            last = e
            sys.stderr.write(f"  {label}: attempt {attempt} failed ({e})\n")
    raise SystemExit(
        f"\nCould not fetch {label}.\n  {url}\n  last error: {last}\n\n"
        "If this is a sandbox with restricted egress, run it somewhere with\n"
        "outbound access to census.gov. Nothing else in the build needs network.\n")


def _rows(blob):
    """LODES ships gzipped CSV with a header row."""
    with gzip.GzipFile(fileobj=io.BytesIO(blob)) as gz:
        yield from csv.DictReader(io.TextIOWrapper(gz, encoding="utf-8"))


def lodes(state, kind, year, part="S000_JT00"):
    if kind == "od":
        name = f"{state}_od_main_JT00_{year}.csv.gz"
        url = f"{LODES}/{state}/od/{name}"
    else:
        name = f"{state}_{kind}_{part}_{year}.csv.gz"
        url = f"{LODES}/{state}/{kind}/{name}"
    print(f"  fetching {name}")
    return _get(url, name)


def tract_of(block_geoid):
    """A 15 digit block GEOID starts with its 11 digit tract."""
    return block_geoid[:11]


def county_of(geoid):
    return geoid[:5]


def collect(region, year):
    counties = set(region)
    states = sorted({STATE_OF[c[:2]] for c in counties})

    jobs = collections.Counter()      # tract -> jobs located there
    workers = collections.Counter()   # tract -> employed residents living there
    flows = collections.Counter()     # (home county, work county) -> jobs

    for st in states:
        for row in _rows(lodes(st, "wac", year)):
            g = row["w_geocode"]
            if county_of(g) in counties:
                jobs[tract_of(g)] += int(row["C000"])
        for row in _rows(lodes(st, "rac", year)):
            g = row["h_geocode"]
            if county_of(g) in counties:
                workers[tract_of(g)] += int(row["C000"])
        for row in _rows(lodes(st, "od", year)):
            h, w = county_of(row["h_geocode"]), county_of(row["w_geocode"])
            if h in counties or w in counties:
                flows[(h, w)] += int(row["S000"])

    return jobs, workers, flows


def geometry(region):
    """Tract polygons from TIGERweb, as GeoJSON, paged."""
    by_state = collections.defaultdict(list)
    for fips in region:
        by_state[fips[:2]].append(fips[2:])

    feats = []
    for state, counties in by_state.items():
        clause = ",".join(f"'{c}'" for c in counties)
        offset = 0
        while True:
            q = (f"{TIGER}?where=STATE%3D%27{state}%27+AND+COUNTY+IN+({clause})"
                 f"&outFields=GEOID,NAME,BASENAME&returnGeometry=true&outSR=4326"
                 f"&f=geojson&resultOffset={offset}&resultRecordCount=1000")
            print(f"  fetching tract geometry, offset {offset}")
            data = json.loads(_get(q.replace(" ", "+"), "tract geometry"))
            got = data.get("features", [])
            feats.extend(got)
            if len(got) < 1000:
                break
            offset += 1000
    return feats


def thin(coords, places=4):
    """Round coordinates. Tract outlines do not need seven decimal places, and
    the file has to ship inside a static site."""
    if isinstance(coords[0], (int, float)):
        return [round(coords[0], places), round(coords[1], places)]
    return [thin(c, places) for c in coords]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--region", help="comma separated county FIPS, e.g. 37129,37019")
    ap.add_argument("--year", type=int, default=2022)
    ap.add_argument("--out", default=OUT)
    a = ap.parse_args()

    if a.region:
        region = {f.strip(): f.strip() for f in a.region.split(",") if f.strip()}
    else:
        region = dict(DEFAULT_REGION)
    for fips in region:
        if fips[:2] not in STATE_OF:
            raise SystemExit(f"No LODES state slug for FIPS {fips}. Add it to STATE_OF.")

    print(f"Region: {', '.join(region.values())}   Year: {a.year}")
    jobs, workers, flows = collect(region, a.year)
    feats = geometry(region)
    print(f"  {len(feats)} tracts, {sum(jobs.values()):,} jobs, "
          f"{sum(workers.values()):,} resident workers")

    tracts = []
    for f in feats:
        props, geom = f.get("properties") or {}, f.get("geometry")
        gid = props.get("GEOID")
        if not gid or not geom:
            continue
        j, w = jobs.get(gid, 0), workers.get(gid, 0)
        tracts.append({
            "id": gid,
            "county": region.get(county_of(gid), county_of(gid)),
            "name": props.get("BASENAME") or props.get("NAME") or gid,
            "jobs": j,
            "workers": w,
            "net": j - w,                                  # the number the map draws
            "type": geom["type"],
            "coords": thin(geom["coordinates"]),
        })
    tracts.sort(key=lambda t: t["id"])

    named = {c: n for c, n in region.items()}
    flow_rows = [
        {"home": h, "homeName": named.get(h, h), "work": w, "workName": named.get(w, w),
         "jobs": n}
        for (h, w), n in flows.most_common() if n >= 25
    ][:400]

    out = {
        "meta": {
            "built": datetime.date.today().isoformat(),
            "year": a.year,
            "region": named,
            "source": "US Census LEHD LODES 8 (WAC, RAC, OD) and TIGERweb tract geometry",
            "note": ("net is jobs located in the tract minus employed residents living "
                     "in it. Positive means an employment centre, negative means people "
                     "live there and work elsewhere."),
        },
        "tracts": tracts,
        "flows": flow_rows,
    }
    with open(a.out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, separators=(",", ":"))
    kb = os.path.getsize(a.out) // 1024
    print(f"wrote {a.out}  ({kb} KB, {len(tracts)} tracts, {len(flow_rows)} flows)")
    print("now run: python3 build/mkjobspage.py")


if __name__ == "__main__":
    main()
