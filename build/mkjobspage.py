# -*- coding: utf-8 -*-
"""Render where-the-jobs-are.html from jobs-map.json.

The map draws one number per tract: jobs located there minus employed residents
living there. Positive is an employment centre, negative is a place people leave
in the morning. That is a polarity, so the scale is diverging: two hues with a
neutral grey midpoint, never a rainbow, and the midpoint recedes so the tracts
that are furthest out of balance carry the most visual weight.

Run:  python3 build/mkjobsmap.py     (writes jobs-map.json, needs network)
      python3 build/mkjobspage.py    (writes where-the-jobs-are.html)
"""
import os, sys, json, math, html, datetime

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
sys.path.insert(0, _HERE)
from shell import page

DATA = os.path.join(_ROOT, "jobs-map.json")
OUT = os.path.join(_ROOT, "where-the-jobs-are.html")
SITE = "https://sidekixhq.com"

W, H, PAD = 980, 700, 24

# Diverging ramp, validated against the #0f0c06 panel: every step clears 3:1 on
# the surface and lightness rises monotonically outward from the midpoint.
MID = "#635E55"
COOL = ["#3E7893", "#42A3CE", "#6FCEFA"]   # more resident workers than jobs
WARM = ["#9A6A50", "#CD7E57", "#F5976B"]   # more jobs than resident workers


def ramp(net, scale):
    """Five thresholds either side of balance, on a shared scale."""
    if scale <= 0:
        return MID
    r = net / scale
    if r <= -0.45: return COOL[2]
    if r <= -0.18: return COOL[1]
    if r <= -0.05: return COOL[0]
    if r <   0.05: return MID
    if r <  0.18:  return WARM[0]
    if r <  0.45:  return WARM[1]
    return WARM[2]


def rings(t):
    """Normalise Polygon and MultiPolygon to a flat list of rings."""
    if t["type"] == "Polygon":
        return t["coords"]
    out = []
    for poly in t["coords"]:
        out.extend(poly)
    return out


def project(tracts):
    lons = [c[0] for t in tracts for r in rings(t) for c in r]
    lats = [c[1] for t in tracts for r in rings(t) for c in r]
    minlon, maxlon, minlat, maxlat = min(lons), max(lons), min(lats), max(lats)
    # equirectangular is fine at county scale; correct x for latitude
    k = math.cos(math.radians((minlat + maxlat) / 2))
    w, h = (maxlon - minlon) * k, (maxlat - minlat)
    s = min((W - 2 * PAD) / w, (H - 2 * PAD) / h)
    ox = (W - w * s) / 2
    oy = (H - h * s) / 2

    def pt(c):
        x = ox + (c[0] - minlon) * k * s
        y = oy + (maxlat - c[1]) * s        # north up
        return f"{x:.1f},{y:.1f}"
    return pt


def path_for(t, pt):
    parts = []
    for ring in rings(t):
        if len(ring) < 3:
            continue
        parts.append("M" + "L".join(pt(c) for c in ring) + "Z")
    return "".join(parts)


def build():
    if not os.path.exists(DATA):
        raise SystemExit(
            f"\n{DATA} is missing.\n"
            "Run  python3 build/mkjobsmap.py  first. It needs outbound network to\n"
            "census.gov and writes the file this page renders.\n")
    d = json.load(open(DATA, encoding="utf-8"))
    tracts = [t for t in d["tracts"] if t.get("coords")]
    if not tracts:
        raise SystemExit("jobs-map.json has no tract geometry.")
    meta = d["meta"]
    pt = project(tracts)

    scale = max(abs(t["net"]) for t in tracts) or 1
    paths = []
    for t in tracts:
        dd = path_for(t, pt)
        if not dd:
            continue
        net = t["net"]
        paths.append(
            f'<path d="{dd}" fill="{ramp(net, scale)}" fill-opacity=".92" '
            f'stroke="#0d0b07" stroke-width=".7" tabindex="0" role="listitem" '
            f'data-n="{html.escape(t["name"])}" data-c="{html.escape(t["county"])}" '
            f'data-j="{t["jobs"]}" data-w="{t["workers"]}" data-net="{net}" '
            f'aria-label="{html.escape(t["county"])} tract {html.escape(t["name"])}: '
            f'{t["jobs"]} jobs, {t["workers"]} resident workers"></path>')

    counties = meta.get("region", {})
    out_flows = [f for f in d.get("flows", []) if f["home"] != f["work"]]
    out_flows.sort(key=lambda f: -f["jobs"])
    stay = {c: 0 for c in counties}
    leave = {c: 0 for c in counties}
    for f in d.get("flows", []):
        if f["home"] in stay:
            if f["home"] == f["work"]:
                stay[f["home"]] += f["jobs"]
            else:
                leave[f["home"]] += f["jobs"]

    return d, tracts, paths, counties, out_flows, stay, leave, scale


def main():
    d, tracts, paths, counties, out_flows, stay, leave, scale = build()
    meta = d["meta"]
    year = meta["year"]
    total_jobs = sum(t["jobs"] for t in tracts)
    total_workers = sum(t["workers"] for t in tracts)

    cards = []
    for fips, name in sorted(counties.items(), key=lambda kv: -(stay.get(kv[0], 0) + leave.get(kv[0], 0))):
        s, l = stay.get(fips, 0), leave.get(fips, 0)
        tot = s + l
        if not tot:
            continue
        pct = round(100 * l / tot)
        cards.append(
            f'<div class="jm-card"><b>{pct}%</b>'
            f'<span>of employed {html.escape(name)} County residents leave the county for work. '
            f'{l:,} of {tot:,}.</span></div>')

    flow_rows = "".join(
        f"<tr><td>{html.escape(f['homeName'])}</td><td>{html.escape(f['workName'])}</td>"
        f"<td class=num>{f['jobs']:,}</td></tr>"
        for f in out_flows[:12])

    table_rows = "".join(
        f"<tr><td>{html.escape(t['county'])}</td><td>{html.escape(t['name'])}</td>"
        f"<td class=num>{t['jobs']:,}</td><td class=num>{t['workers']:,}</td>"
        f"<td class=num>{t['net']:+,}</td></tr>"
        for t in sorted(tracts, key=lambda t: t["net"]))

    legend = "".join(
        f'<span class="jm-sw" style="background:{c}"></span>'
        for c in [COOL[2], COOL[1], COOL[0], MID, WARM[0], WARM[1], WARM[2]])

    region_name = ", ".join(sorted(counties.values()))
    MAIN = f"""<main id="maincontent" class="jm">
<header class="jm-hero">
 <div class="jm-wrap">
  <p class="eyebrow">SideKix Homegrown</p>
  <h1>Where the jobs are, and where the workers sleep</h1>
  <p class="jm-dek">Every tract in {html.escape(region_name)}, coloured by one number: the jobs
    located in it minus the employed people living in it. Orange means more jobs than resident
    workers, an employment centre. Blue means more resident workers than jobs, a place people
    leave in the morning.</p>
 </div>
</header>

<section>
 <div class="jm-wrap">
  <div class="jm-panel">
   <svg viewBox="0 0 {W} {H}" role="list" aria-label="Census tracts coloured by jobs minus
        resident workers" class="jm-svg">{''.join(paths)}</svg>
   <div class="jm-tip" id="jmtip" hidden aria-live="polite"></div>
  </div>
  <div class="jm-legend">
   <span class="jm-lend">More workers than jobs</span>
   {legend}
   <span class="jm-lend">More jobs than workers</span>
  </div>
  <p class="jm-cap">{len(tracts)} tracts. {total_jobs:,} jobs and {total_workers:,} employed
    residents, {year}. Hover or focus a tract for its numbers.</p>
 </div>
</section>

<section>
 <div class="jm-wrap">
  <h2>Who leaves to work</h2>
  <div class="jm-cards">{''.join(cards)}</div>
 </div>
</section>

<section>
 <div class="jm-wrap">
  <h2>The biggest commutes</h2>
  <table class="jm-tab">
   <thead><tr><th>Live in</th><th>Work in</th><th class=num>Workers</th></tr></thead>
   <tbody>{flow_rows}</tbody>
  </table>
  <details class="jm-det">
   <summary>Every tract, as a table</summary>
   <table class="jm-tab">
    <thead><tr><th>County</th><th>Tract</th><th class=num>Jobs</th>
      <th class=num>Residents</th><th class=num>Net</th></tr></thead>
    <tbody>{table_rows}</tbody>
   </table>
  </details>
  <p class="jm-src">{html.escape(meta['source'])}. Data year {year}, built
    {meta['built']}. Net is jobs minus employed residents.
    <a href="homegrown.html">What SideKix does about it</a>.</p>
 </div>
</section>
</main>"""

    CSS = """
.jm{padding:0 0 90px}
.jm .jm-wrap{max-width:1120px;margin:0 auto;padding:0 24px}
.jm-hero{padding:clamp(40px,6vw,76px) 0 8px;text-align:center}
.jm h1{font-family:var(--display);font-weight:600;font-size:clamp(32px,5.4vw,56px);
  line-height:1.06;color:#FFF8E8;margin:12px auto 0;max-width:20ch}
.jm .jm-dek{font-size:17px;line-height:1.66;color:#B9B4AB;margin:22px auto 0;max-width:64ch}
.jm section{margin:clamp(40px,6vw,68px) 0 0}
.jm section:first-of-type{margin-top:26px;padding-top:0}
.jm h2{font-family:var(--display);font-weight:600;font-size:clamp(24px,3.4vw,34px);
  color:#FFF8E8;margin:0 0 18px;max-width:48rem;margin-left:auto;margin-right:auto}
.jm-panel{position:relative;border:1px solid rgba(212,168,86,.3);border-radius:18px;
  background:#0f0c06;padding:10px;overflow-x:auto}
.jm-svg{display:block;width:100%;min-width:620px;height:auto}
.jm-svg path{transition:fill-opacity .15s,stroke .15s;cursor:default}
.jm-svg path:hover,.jm-svg path:focus-visible{fill-opacity:1;stroke:#FFF8E8;stroke-width:1.4;
  outline:none}
.jm-tip{position:absolute;pointer-events:none;z-index:5;min-width:190px;
  background:rgba(10,9,7,.97);border:1px solid rgba(212,168,86,.5);border-radius:11px;
  padding:11px 13px;font-size:13px;line-height:1.55;color:#E3DED2;
  box-shadow:0 10px 30px rgba(0,0,0,.6)}
.jm-tip b{display:block;font-family:var(--util);font-size:10.5px;letter-spacing:.14em;
  text-transform:uppercase;color:#CDAA63;margin-bottom:6px}
.jm-tip .r{display:flex;justify-content:space-between;gap:18px}
.jm-tip .r span:last-child{font-variant-numeric:tabular-nums;color:#FFF8E8}
.jm-legend{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap;
  margin:16px auto 0}
.jm-sw{width:34px;height:11px;border-radius:2px;display:block}
.jm-lend{font-family:var(--util);font-size:10px;letter-spacing:.14em;text-transform:uppercase;
  color:#9C968D;padding:0 6px}
.jm-cap{text-align:center;font-size:14px;color:#918B80;margin:12px auto 0;max-width:70ch}
.jm-cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:14px}
.jm-card{border:1px solid rgba(212,168,86,.28);border-radius:14px;padding:22px 20px;
  background:linear-gradient(180deg,rgba(26,20,8,.5),rgba(8,8,9,.72))}
.jm-card b{display:block;font-family:var(--display);font-size:clamp(30px,4vw,40px);line-height:1;
  color:var(--cream);margin-bottom:9px;font-variant-numeric:tabular-nums}
.jm-card span{display:block;font-size:14px;line-height:1.55;color:#A8A296}
.jm-tab{width:100%;border-collapse:collapse;font-size:15px;max-width:48rem;margin:0 auto}
.jm-tab th,.jm-tab td{text-align:left;padding:11px 12px 11px 0;
  border-top:1px solid rgba(212,168,86,.16);color:#A8A296}
.jm-tab thead th{border-top:none;font-family:var(--util);font-size:10px;letter-spacing:.16em;
  text-transform:uppercase;color:#CDAA63}
.jm-tab .num{text-align:right;font-variant-numeric:tabular-nums;color:#E3DED2}
.jm-det{max-width:48rem;margin:26px auto 0;border-top:1px solid rgba(212,168,86,.16)}
.jm-det summary{cursor:pointer;padding:15px 0;color:#E3DED2;font-size:15.5px}
.jm-det[open] summary{color:#F3E4A8}
.jm-src{font-size:13.5px;color:#8E887D;margin:26px auto 0;max-width:48rem;line-height:1.7}
.jm-src a{color:#CDAA63}
@media (max-width:640px){
  .jm-tab,.jm-tab tbody,.jm-tab tr,.jm-tab td{display:block;width:100%}
  .jm-tab thead{display:none}
  .jm-tab td{border-top:none;padding:2px 0}
  .jm-tab tr{border-top:1px solid rgba(212,168,86,.16);padding:12px 0}
  .jm-tab .num{text-align:left}
}
@media (prefers-reduced-motion:reduce){.jm-svg path{transition:none}}
"""

    JS = """
var tip = document.getElementById('jmtip');
var panel = document.querySelector('.jm-panel');
function show(el){
  var n = el.getAttribute('data-n'), c = el.getAttribute('data-c');
  var j = +el.getAttribute('data-j'), w = +el.getAttribute('data-w');
  var net = +el.getAttribute('data-net');
  var verdict = net > 0 ? (net.toLocaleString() + ' more jobs than workers')
                        : (Math.abs(net).toLocaleString() + ' more workers than jobs');
  tip.innerHTML = '<b>' + c + ' \\u00b7 tract ' + n + '</b>'
    + '<span class=r><span>Jobs here</span><span>' + j.toLocaleString() + '</span></span>'
    + '<span class=r><span>Residents who work</span><span>' + w.toLocaleString() + '</span></span>'
    + '<span class=r><span>Net</span><span>' + verdict + '</span></span>';
  tip.hidden = false;
}
function place(ev){
  if (tip.hidden) { return; }
  var r = panel.getBoundingClientRect();
  var x = ev.clientX - r.left + 16, y = ev.clientY - r.top + 16;
  if (x + tip.offsetWidth > r.width) { x = ev.clientX - r.left - tip.offsetWidth - 16; }
  if (y + tip.offsetHeight > r.height) { y = r.height - tip.offsetHeight - 8; }
  tip.style.left = Math.max(4, x) + 'px';
  tip.style.top = Math.max(4, y) + 'px';
}
var svg = document.querySelector('.jm-svg');
if (svg) {
  svg.addEventListener('mouseover', function(e){ if (e.target.tagName === 'path') show(e.target); });
  svg.addEventListener('mousemove', place);
  svg.addEventListener('mouseleave', function(){ tip.hidden = true; });
  svg.addEventListener('focusin', function(e){
    if (e.target.tagName !== 'path') { return; }
    show(e.target);
    var b = e.target.getBoundingClientRect(), r = panel.getBoundingClientRect();
    tip.style.left = Math.max(4, Math.min(b.left - r.left, r.width - tip.offsetWidth - 8)) + 'px';
    tip.style.top = Math.max(4, b.top - r.top + b.height + 8) + 'px';
  });
  svg.addEventListener('focusout', function(){ tip.hidden = true; });
}
"""

    schema = {"@context": "https://schema.org", "@type": "Dataset",
              "name": f"Jobs and resident workers by census tract, {region_name}",
              "description": meta["note"], "creator": {"@id": f"{SITE}/#organization"},
              "isAccessibleForFree": True, "url": f"{SITE}/where-the-jobs-are.html",
              "temporalCoverage": str(year), "license": "https://www.usa.gov/government-works"}

    title = f"Where the Jobs Are: {region_name} | SideKix"
    desc = (f"Every census tract in {region_name} coloured by jobs minus employed residents, "
            f"from Census LODES {year}. Shows which places are employment centres and which "
            "export their workers every morning.")
    out = page("where-the-jobs-are.html", title[:62] if len(title) > 62 else title,
               desc[:158], MAIN, extra_css=CSS, extra_js=JS, schema=(schema,),
               og_title="Where the Jobs Are")
    stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    out = out.replace("<!DOCTYPE html>\n", f"<!DOCTYPE html>\n<!-- kx-build {stamp} jobsmap -->\n", 1)
    open(OUT, "w", encoding="utf-8").write(out)
    print(f"where-the-jobs-are.html written: {len(out)//1024} KB, {len(paths)} tracts")
    register(region_name)


def register(region_name):
    """Put the page in sitemap.xml and llms.txt if it is not already there.
    Idempotent, and surgical: rerunning build/mksitemap.py instead would rewrite
    every lastmod in the file from checkout timestamps."""
    sm = os.path.join(_ROOT, "sitemap.xml")
    if os.path.exists(sm):
        t = open(sm, encoding="utf-8").read()
        if "where-the-jobs-are.html" not in t:
            import re as _re
            entry = ("  <url>\n"
                     f"    <loc>{SITE}/where-the-jobs-are.html</loc>\n"
                     f"    <lastmod>{datetime.date.today().isoformat()}</lastmod>\n"
                     "    <changefreq>yearly</changefreq>\n"
                     "    <priority>0.8</priority>\n"
                     "  </url>\n")
            anchor = _re.search(r"  <url>\s*<loc>[^<]*homegrown\.html</loc>.*?</url>\n", t, _re.S)
            if anchor:
                t = t[:anchor.end()] + entry + t[anchor.end():]
            else:
                t = t.replace("</urlset>", entry + "</urlset>", 1)
            open(sm, "w", encoding="utf-8").write(t)
            print("  sitemap.xml updated")

    lt = os.path.join(_ROOT, "llms.txt")
    if os.path.exists(lt):
        t = open(lt, encoding="utf-8").read()
        if "where-the-jobs-are" not in t:
            line = (f"- [Where the Jobs Are]({SITE}/where-the-jobs-are.html): Every census tract in "
                    f"{region_name} coloured by the jobs located in it minus the employed people "
                    "living in it, from Census LODES. Shows which places are employment centres "
                    "and which export their workers every morning. Free federal data, no account.\n")
            key = "- [SideKix Homegrown]"
            if key in t:
                i = t.index(key)
                t = t[:i] + line + t[i:]
                open(lt, "w", encoding="utf-8").write(t)
                print("  llms.txt updated")


if __name__ == "__main__":
    main()
