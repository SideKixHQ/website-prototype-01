# -*- coding: utf-8 -*-
"""Build homegrown.html - the SideKix Homegrown offering for towns and counties.

Run:  python3 build/mkhomegrown.py
Writes: homegrown.html at the repo root, on the shared site theme.
"""
import os, sys, json, datetime

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
sys.path.insert(0, _HERE)
from shell import page

SITE = "https://sidekixhq.com"
OUT = os.path.join(_ROOT, "homegrown.html")

TITLE = "Homegrown: Local Talent for Economic Development | SideKix"
DESC = ("A workforce program for towns and counties. Homegrown builds a named, tracked bench of "
        "local residents moving toward the jobs your target industries hire for.")

# ---------------------------------------------------------------- schema
org = {"@id": f"{SITE}/#organization"}
svc = {
  "@context": "https://schema.org", "@type": "Service",
  "name": "SideKix Homegrown",
  "serviceType": "Workforce and economic development program",
  "provider": org,
  "areaServed": {"@type": "State", "name": "North Carolina"},
  "audience": {"@type": "Audience", "audienceType":
               "Municipal and county economic development organizations, workforce boards, chambers of commerce"},
  "description": DESC,
  "url": f"{SITE}/homegrown.html",
}
faqs = [
 ("Is Homegrown a training provider?",
  "No. Homegrown does not teach a trade. It is the layer in front of training: working out what a "
  "resident's next move actually is, building the behavior to make it, and holding them to it for "
  "ninety days. Where a resident needs a credential, Homegrown hands them to the community college "
  "or the NCWorks career center and tracks whether they enrolled."),
 ("How is this different from what the workforce board already does?",
  "The workforce board funds and measures placement. Homegrown produces something no one in a region "
  "can usually produce: a named, current list of residents in motion toward specific occupations, with "
  "a person accountable for each one. That list is what an economic developer needs in a recruitment "
  "conversation, and it is not the same as a list of programs."),
 ("What does a town actually receive?",
  "A cohort of residents run through the eight week program and ninety days of follow through, a "
  "quarterly bench report written to be handed to a site consultant or dropped into an RFI response, "
  "and a local fill rate figure for the target employers you name."),
 ("How long before there is anything to show?",
  "One cohort takes eight weeks, and the outcomes that matter are verified at a hundred and eighty "
  "days. A credible bench in the first six months is tens of residents, not hundreds. Anyone promising "
  "a pipeline of three hundred people in a quarter is selling a list, not a bench."),
 ("Has SideKix run this before?",
  "Not yet. Homegrown is open for design partners, which means the first towns shape the program, "
  "get founding terms, and are named on the results. That is a better deal than buying a finished "
  "product, and it is the truth."),
]
faqschema = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
  {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]}
crumbs = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
  {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
  {"@type": "ListItem", "position": 2, "name": "Homegrown", "item": f"{SITE}/homegrown.html"}]}

# ---------------------------------------------------------------- css
CSS = """
/* Homegrown - own namespace, nothing here matches a theme script selector */
.hg{padding:0 0 90px}
.hg [hidden]{display:none !important}

.hg .hgwrap{max-width:1120px;margin:0 auto;padding:0 24px}
.hg .narrow{max-width:760px}

/* hero */
.hg .hghero{padding:clamp(56px,9vw,104px) 0 clamp(34px,5vw,56px);text-align:center}
.hg .hghero h1{font-family:var(--display);font-weight:600;font-size:clamp(36px,6.4vw,68px);
  line-height:1.05;color:#FFF8E8;margin:14px auto 0;max-width:17ch;letter-spacing:-.01em}
.hg .hgdek{font-size:clamp(16px,1.9vw,18.5px);line-height:1.66;color:#B9B4AB;
  margin:24px auto 0;max-width:60ch}
.hg .hgstamp{font-family:var(--util);font-size:10.5px;letter-spacing:.2em;text-transform:uppercase;
  color:var(--gold-mid);margin-top:30px}

/* section furniture */
.hg section{margin:clamp(52px,7vw,86px) 0 0}
/* the shell already gives the first section 132px of top padding; adding the section
   rhythm on top of it double-spaces the page under the hero */
.hg section:first-of-type{margin-top:0}
.hg h2{font-family:var(--display);font-weight:600;font-size:clamp(27px,3.9vw,42px);
  line-height:1.14;color:#FFF8E8;margin:0 0 6px}
.hg h3{font-family:var(--display);font-weight:600;font-size:clamp(20px,2.4vw,25px);
  line-height:1.2;color:#FFF3DC;margin:0 0 8px}
.hg p{font-size:16px;line-height:1.72;color:#B9B4AB;margin:0 0 16px;max-width:68ch}
.hg p.lead{font-size:17.5px;color:#CFC9BE}
.hg strong{color:#EFE7D6;font-weight:600}
.hg .rule{height:1px;background:linear-gradient(90deg,transparent,rgba(212,168,86,.42),transparent);
  margin:0 0 34px}

/* stat row */
.hg .stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:14px;margin:32px 0 8px}
.hg .stat{border:1px solid rgba(212,168,86,.28);border-radius:14px;padding:22px 20px;
  background:linear-gradient(180deg,rgba(26,20,8,.5),rgba(8,8,9,.72))}
.hg .stat b{display:block;font-family:var(--display);font-size:clamp(30px,4.2vw,40px);
  line-height:1;color:var(--cream);margin-bottom:9px}
.hg .stat span{display:block;font-size:14px;line-height:1.55;color:#A8A296}

/* figure / diagram */
.hg figure{margin:34px 0 0}
.hg .dwrap{border:1px solid rgba(212,168,86,.3);border-radius:18px;padding:26px 20px 20px;
  background:linear-gradient(180deg,rgba(24,18,7,.55),rgba(7,7,8,.92));
  overflow-x:auto;-webkit-overflow-scrolling:touch}
.hg .dwrap svg{display:block;width:100%;min-width:660px;height:auto;margin:0 auto;max-width:980px}
.hg figcaption{font-size:14.5px;line-height:1.6;color:#918B80;margin:14px auto 0;
  max-width:74ch;text-align:center}
.hg .dbar{display:flex;justify-content:center;margin:14px 0 0}
.hg .dget{font-family:var(--util);font-size:10.5px;letter-spacing:.18em;text-transform:uppercase;
  cursor:pointer;background:none;border:1px solid rgba(212,168,86,.34);color:#B9B4AB;
  border-radius:999px;padding:0 20px;min-height:44px;transition:border-color .3s,color .3s}
.hg .dget:hover{border-color:var(--gold);color:var(--gold-pale)}
.hg .dget:focus-visible{outline:3px solid var(--gold-pale);outline-offset:3px}

/* svg type */
.hg .d-lab{font-family:var(--util);font-size:13px;font-weight:500;letter-spacing:.16em;
  text-transform:uppercase;fill:#FFF8E8}
.hg .d-sub{font-family:var(--body);font-size:12.5px;fill:#A8A296}
.hg .d-wk{font-family:var(--util);font-size:10.5px;letter-spacing:.18em;text-transform:uppercase}
.hg .d-mid{font-family:var(--display);font-size:23px;font-weight:600;fill:#FFF8E8}
.hg .d-mids{font-family:var(--body);font-size:12px;fill:#C6BE9E}
.hg .d-note{font-family:var(--util);font-size:10px;letter-spacing:.16em;text-transform:uppercase;
  fill:#CDAA63}

/* card grids */
.hg .cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:14px;margin:26px 0 0}
.hg .card{border:1px solid rgba(212,168,86,.26);border-radius:15px;padding:24px 22px;
  background:linear-gradient(180deg,rgba(22,17,7,.5),rgba(8,8,9,.7))}
.hg .card[data-c]{border-color:color-mix(in srgb,var(--c) 34%,transparent)}
/* the fallback has to clear 4.5:1 on the card fill in its own right: gold-mid does not */
.hg .card .tag{font-family:var(--util);font-size:10px;letter-spacing:.2em;text-transform:uppercase;
  color:var(--c,#CDAA63);display:block;margin-bottom:10px}
.hg .card h3{font-size:21px;margin-bottom:7px}
.hg .card p{font-size:14.8px;line-height:1.64;margin:0;color:#A8A296;max-width:none}

/* phase detail */
.hg .phase{display:grid;grid-template-columns:132px minmax(0,1fr);gap:22px;align-items:start;
  padding:22px 0;border-top:1px solid rgba(212,168,86,.16)}
.hg .phase:first-of-type{border-top:none}
.hg .phase .pk{font-family:var(--util);font-size:10.5px;letter-spacing:.18em;text-transform:uppercase;
  color:var(--c,var(--gold-mid));padding-top:5px;line-height:1.7}
.hg .phase p{margin:0;font-size:15.4px}
.hg .phase h3{font-size:22px}

/* plain list */
.hg ul.plain{list-style:none;margin:6px 0 18px;padding:0;max-width:68ch}
.hg ul.plain li{position:relative;padding:9px 0 9px 26px;font-size:15.6px;line-height:1.66;
  color:#B9B4AB;border-top:1px solid rgba(212,168,86,.13)}
.hg ul.plain li:first-child{border-top:none}
.hg ul.plain li::before{content:'';position:absolute;left:4px;top:19px;width:7px;height:7px;
  border-radius:50%;background:var(--gold-mid)}
.hg ul.plain li b{color:#EFE7D6;font-weight:600}

/* metric table */
.hg .mtab{width:100%;border-collapse:collapse;margin:22px 0 0;font-size:15.2px}
.hg .mtab th,.hg .mtab td{text-align:left;padding:14px 14px 14px 0;
  border-top:1px solid rgba(212,168,86,.16);vertical-align:top;line-height:1.6}
.hg .mtab thead th{border-top:none;font-family:var(--util);font-size:10.5px;letter-spacing:.18em;
  text-transform:uppercase;color:var(--gold-mid);padding-bottom:9px}
.hg .mtab td:first-child{color:#EFE7D6;font-weight:600;width:34%}
.hg .mtab td{color:#A8A296}
.hg .mtab tr.hero td:first-child{color:var(--cream)}

/* callout */
.hg .callout{border-left:2px solid var(--gold);padding:4px 0 4px 22px;margin:28px 0;
  max-width:70ch}
.hg .callout p{font-family:var(--display);font-size:clamp(19px,2.5vw,25px);line-height:1.38;
  color:#FFF3DC;margin:0}

/* cta */
.hg .cta{border:1px solid rgba(212,168,86,.36);border-radius:20px;padding:clamp(30px,5vw,52px);
  text-align:center;background:radial-gradient(120% 140% at 50% 0%,rgba(34,26,10,.7),rgba(7,7,8,.92));
  margin-top:clamp(52px,7vw,86px)}
.hg .cta h2{margin-bottom:12px}
.hg .cta p{margin-left:auto;margin-right:auto;text-align:center}
.hg .btnrow{display:flex;flex-wrap:wrap;gap:12px;justify-content:center;margin-top:26px}
.hg .btn{display:inline-flex;align-items:center;justify-content:center;min-height:48px;padding:0 28px;
  border-radius:999px;text-decoration:none;font-family:var(--body);font-size:14.5px;font-weight:600;
  transition:transform .25s,border-color .25s,color .25s}
.hg .btn.solid{background:linear-gradient(180deg,#D7C582,#A1853E);color:#1a1400;border:none}
.hg .btn.ghost{border:1px solid rgba(212,168,86,.44);color:#D8D2C6;background:none}
.hg .btn:hover{transform:translateY(-2px)}
.hg .btn.ghost:hover{border-color:var(--gold);color:var(--gold-pale)}
.hg .btn:focus-visible{outline:3px solid var(--gold-pale);outline-offset:3px}

/* sources */
.hg .src{margin-top:clamp(48px,6vw,72px)}
.hg .src ol{margin:18px 0 0;padding:0 0 0 20px;max-width:74ch}
.hg .src li{font-size:14px;line-height:1.7;color:#8E887D;padding:6px 0}
.hg .src a{color:#A8A296;text-decoration:underline;text-underline-offset:3px;
  text-decoration-color:rgba(212,168,86,.4)}
.hg .src a:hover{color:var(--gold-pale)}

@media (max-width:640px){
  .hg .phase{grid-template-columns:1fr;gap:8px}
  .hg .phase .pk{padding-top:0}
  .hg .mtab td:first-child{width:auto}
  .hg .mtab,.hg .mtab tbody,.hg .mtab tr,.hg .mtab td{display:block;width:100%}
  .hg .mtab thead{display:none}
  .hg .mtab td{border-top:none;padding:2px 0}
  .hg .mtab tr{border-top:1px solid rgba(212,168,86,.16);padding:14px 0}
}

@media print{
  .hg{padding-bottom:0}
  .hg .dwrap{overflow:visible;background:none;border-color:#999}
  .hg .dwrap svg{min-width:0}
  .hg .dbar,.hg .btnrow{display:none}
  .hg section{break-inside:avoid}
}
"""

# ---------------------------------------------------------------- diagrams
def _defs(sfx):
    """Each diagram carries its own ids so two inline SVGs never collide."""
    return f"""<defs>
<marker id="hgar{sfx}" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7"
        orient="auto-start-reverse">
  <path d="M0,1 L9,5 L0,9" fill="none" stroke="#A1853E" stroke-width="1.6"
        stroke-linecap="round" stroke-linejoin="round"/>
</marker>
<radialGradient id="hgcore{sfx}" cx="50%" cy="30%" r="72%">
  <stop offset="0%" stop-color="#2a2109"/><stop offset="100%" stop-color="#0b0a06"/>
</radialGradient>
<linearGradient id="hgcard{sfx}" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0%" stop-color="#170f04"/><stop offset="100%" stop-color="#08080a"/>
</linearGradient>
<radialGradient id="hgglow{sfx}" cx="50%" cy="50%" r="50%">
  <stop offset="0%" stop-color="#D4A856" stop-opacity=".13"/>
  <stop offset="62%" stop-color="#D4A856" stop-opacity=".05"/>
  <stop offset="100%" stop-color="#D4A856" stop-opacity="0"/>
</radialGradient>
</defs>"""

def _node(x, y, w, h, colour, label, sub):
    cx, cy = x + w / 2, y + h / 2
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="13" fill="url(#hgcardA)" '
            f'stroke="{colour}" stroke-opacity=".55" stroke-width="1.4"/>'
            f'<text class="d-lab" x="{cx}" y="{cy - 6}" text-anchor="middle" style="fill:{colour}">{label}</text>'
            f'<text class="d-sub" x="{cx}" y="{cy + 17}" text-anchor="middle">{sub}</text>')

LOOP_SVG = f"""<svg viewBox="0 0 900 520" role="img" aria-labelledby="hgd1t hgd1d"
     xmlns="http://www.w3.org/2000/svg">
<title id="hgd1t">The Homegrown loop</title>
<desc id="hgd1d">Four stages turning clockwise in a ring - attract, expand, hire local and prove -
around a centre marked The Bench: local residents assessed, matched and tracked. The bench feeds
all four stages, and hiring locally is what makes the next deal defensible.</desc>
{_defs('A')}
<circle cx="450" cy="260" r="205" fill="url(#hgglowA)"/>
<circle cx="450" cy="260" r="95" fill="url(#hgcoreA)" stroke="#D4A856" stroke-opacity=".62" stroke-width="1.6"/>
<text class="d-note" x="450" y="226" text-anchor="middle">The asset</text>
<text class="d-mid" x="450" y="256" text-anchor="middle">The Bench</text>
<text class="d-mids" x="450" y="282" text-anchor="middle">residents, assessed,</text>
<text class="d-mids" x="450" y="300" text-anchor="middle">matched and tracked</text>

<g stroke="#A1853E" stroke-opacity=".5" stroke-width="1.2" stroke-dasharray="3 5">
  <path d="M450,165 L450,112"/><path d="M545,260 L660,260"/>
  <path d="M450,355 L450,408"/><path d="M355,260 L240,260"/>
</g>

<g fill="none" stroke="#A1853E" stroke-opacity=".72" stroke-width="1.6" marker-end="url(#hgarA)">
  <path d="M556,86 Q690,110 752,210"/>
  <path d="M754,310 Q690,410 558,436"/>
  <path d="M344,436 Q210,410 148,310"/>
  <path d="M146,210 Q210,110 342,84"/>
</g>

{_node(350, 28, 200, 84, '#4FC3F7', 'Attract', 'a staffing answer')}
{_node(660, 218, 200, 84, '#5FB6A6', 'Expand', 'employers grow here')}
{_node(350, 408, 200, 84, '#F3E4A8', 'Hire local', 'fill rate, measured')}
{_node(40, 218, 200, 84, '#B18BE4', 'Prove', 'the next deal lands')}
</svg>"""

PH = [("Weeks 1&#8211;2", "Begin", "#F0855A", "Where you actually", "are. Assessed."),
      ("Weeks 3&#8211;5", "Build", "#FFE7A6", "Initiative, applied to", "your real situation."),
      ("Weeks 6&#8211;8", "Become", "#5FB6A6", "One move chosen.", "A ninety-day plan."),
      ("+ 90 days", "Follow through", "#B18BE4", "A weekly check-in.", "An advisor each month.")]
EX = [("Exit 01", "Advance", "up, where you work now"),
      ("Exit 02", "Switch", "into a higher-wage role"),
      ("Exit 03", "Credential", "enrolled at the college"),
      ("Exit 04", "Own it", "start the thing yourself")]
_XS = [36, 268, 500, 732]

def _phase(i):
    x = _XS[i]; wk, nm, c, s1, s2 = PH[i]; cx = x + 106
    return (f'<rect x="{x}" y="40" width="212" height="118" rx="14" fill="url(#hgcardB)" '
            f'stroke="{c}" stroke-opacity=".5" stroke-width="1.4"/>'
            f'<text class="d-wk" x="{cx}" y="70" text-anchor="middle" fill="{c}">{wk}</text>'
            f'<text class="d-lab" x="{cx}" y="99" text-anchor="middle">{nm}</text>'
            f'<text class="d-sub" x="{cx}" y="123" text-anchor="middle">{s1}</text>'
            f'<text class="d-sub" x="{cx}" y="141" text-anchor="middle">{s2}</text>')

def _exit(i):
    x = _XS[i]; tag, nm, sub = EX[i]; cx = x + 106
    return (f'<rect x="{x}" y="266" width="212" height="100" rx="14" fill="url(#hgcardB)" '
            f'stroke="#D4A856" stroke-opacity=".4" stroke-width="1.3"/>'
            f'<text class="d-note" x="{cx}" y="294" text-anchor="middle">{tag}</text>'
            f'<text class="d-lab" x="{cx}" y="321" text-anchor="middle">{nm}</text>'
            f'<text class="d-sub" x="{cx}" y="345" text-anchor="middle">{sub}</text>')

def _chev(x):
    return (f'<path d="M{x - 5},91 L{x + 5},99 L{x - 5},107" fill="none" stroke="#A1853E" '
            f'stroke-opacity=".8" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/>')

FLOW_SVG = f"""<svg viewBox="0 0 980 410" role="img" aria-labelledby="hgd2t hgd2d"
     xmlns="http://www.w3.org/2000/svg">
<title id="hgd2t">The Next Move program</title>
<desc id="hgd2d">Four stages left to right - Begin in weeks one and two, Build in weeks three to
five, Become in weeks six to eight, then ninety days of follow through - feeding down into four
exits: advance, switch, credential, or own it.</desc>
{_defs('B')}
{''.join(_phase(i) for i in range(4))}
{_chev(258)}{_chev(490)}{_chev(722)}
<path d="M490,163 V214" fill="none" stroke="#A1853E" stroke-opacity=".6" stroke-width="1.4"/>
<path d="M142,214 H838" fill="none" stroke="#A1853E" stroke-opacity=".6" stroke-width="1.4"/>
<circle cx="490" cy="214" r="3.4" fill="#A1853E"/>
<g fill="none" stroke="#A1853E" stroke-opacity=".6" stroke-width="1.4" marker-end="url(#hgarB)">
  <path d="M142,214 V260"/><path d="M374,214 V260"/>
  <path d="M606,214 V260"/><path d="M838,214 V260"/>
</g>
{''.join(_exit(i) for i in range(4))}
</svg>"""

# ---------------------------------------------------------------- content
CHECKED = "10 September 2026"

def _card(c, tag, h, p):
    return (f'<div class="card" data-c style="--c:{c}"><span class="tag">{tag}</span>'
            f'<h3>{h}</h3><p>{p}</p></div>')

def _phrow(c, k, h, p):
    return (f'<div class="phase" style="--c:{c}"><div class="pk">{k}</div>'
            f'<div><h3>{h}</h3><p>{p}</p></div></div>')

SOURCES = [
 ('Occupational Employment and Wage Statistics, Wilmington NC metropolitan area, May 2024 &#8212; '
  'mean hourly wage $26.94 against $32.66 nationally; food preparation and serving 13.5% of area '
  'employment at $14.99. U.S. Bureau of Labor Statistics.',
  'https://www.bls.gov/regions/southeast/news-release/occupationalemploymentandwages_wilmington.htm'),
 ('North Carolina employment projections 2024&#8211;2034 &#8212; the Wilmington area projected to add '
  'roughly 13,800 jobs, a 6.9% increase. NC Department of Commerce.',
  'https://www.commerce.nc.gov/data-tools-reports/labor-market-data-tools/employment-projections/north-carolina-employment-projections-2024-2034-regional-occupational-trends'),
 ('Brunswick County the fastest-growing county in North Carolina, up 24% between April 2020 and July '
  '2024 to 169,448; Leland at 30,264 in 2023, more than double its 2010 count. Business North Carolina, '
  'citing the Census Bureau and the NC Office of State Budget and Management.',
  'https://businessnc.com/community-close-up-brunswick-new-hanover-pender-counties/'),
 ('Workforce availability a leading site selection factor, and roughly 60% of manufacturers naming '
  'talent shortages a top concern. Business Facilities.',
  'https://businessfacilities.com/topics/site-selection-factors/education-and-workforce/'),
 ('Training transfer at roughly 10&#8211;15%, and forgetting of about 70% within a day. Summary of the '
  'transfer-of-training literature.',
  'https://www.aimforbehavior.com/library/only-10-to-15-percent-of-what-people/'),
 ('Campos et al., <em>Teaching personal initiative beats traditional training in boosting small business '
  'in West Africa</em>, Science, 2017 &#8212; 30% profit gain against a statistically insignificant 11% '
  'for conventional training.',
  'https://www.science.org/doi/10.1126/science.aan5329'),
 ('Seven-year follow-up to the same trial &#8212; a 52% profit gain, with effects concentrated among men. '
  'World Bank Development Impact.',
  'https://blogs.worldbank.org/en/impactevaluations/personal-initiative-training-continues-to-yield-positive-benefit'),
 ('Sector-focused training programs across four randomized trials &#8212; earnings gains of 14&#8211;38% '
  'in the year after training, persisting at 12&#8211;34%. WorkRise.',
  'https://workrisenetwork.org/working-knowledge/evidence-sector-focused-training-programs-shows-significant-and-persistent'),
 ('Entrepreneurial skills training and microenterprise services as allowable WIOA activities, and the '
  'direction to coordinate workforce with economic development. WorkforceGPS, U.S. Department of Labor.',
  'https://www.workforcegps.org/resources/2019/10/30/13/49/Resources-to-Support-Entrepreneurship'),
 ('Eligible Training Provider List requirements &#8212; programs must lead to a recognized postsecondary '
  'credential, certificate of apprenticeship or licence to draw voucher funding. WorkforceGPS.',
  'https://ion.workforcegps.org/resources/2016/03/10/17/06/Eligible_Training_Provider_Provisions_and_ETPLs_in_WOIA'),
 ('Sector partnership grants to North Carolina local workforce boards, the Cape Fear board among them. '
  'NC Department of Commerce.',
  'https://www.commerce.nc.gov/news/press-releases/2024/01/31/nc-commerce-awards-grants-local-workforce-boards-supporting-sector-partnerships-advanced'),
 ('A 70% completion standard applied to federally funded short-term workforce programs. NC Community '
  'College System, Workforce Pell resources.',
  'https://www.nccommunitycolleges.edu/workforce-pell/'),
]

MAIN = f"""<main id="maincontent" class="hg">

<header class="hghero">
  <div class="hgwrap">
    <p class="eyebrow">SideKix Homegrown</p>
    <h1>The jobs you attract should go to the people already here.</h1>
    <p class="hgdek">Homegrown is a workforce program for towns and counties. It builds a named,
      tracked bench of residents moving toward the work your target industries actually hire for,
      so recruitment has a staffing answer, expansion has somewhere to draw from, and the growth
      you win reaches the people who were already living there.</p>
    <p class="hgstamp">For economic developers, workforce boards and chambers</p>
  </div>
</header>

<section>
 <div class="hgwrap">
  <p class="eyebrow">The case</p>
  <h2>Three asks, one problem</h2>
  <div class="rule"></div>
  <p class="lead">Most economic development offices are carrying three jobs at once. Attract
    business. Grow the industries already here. Make sure residents can actually get the work.
    They get funded separately, measured separately and discussed separately.</p>
  <p>They are one problem, and the third one is where it breaks.</p>
  <p>Workforce availability has been a leading factor in site selection for years running. Close to
    six in ten manufacturers name talent shortages a top concern, and site consultants have stopped
    asking only who lives here now &#8212; they ask what the pipeline looks like. Meanwhile the
    growth that does land gets filled by people who move in. The residents who were already there
    stay roughly where they were. And the next incentive package becomes a harder vote.</p>
  <div class="callout"><p>You cannot sell a region you cannot staff, and you cannot defend a deal
    to a council whose residents did not get hired.</p></div>
  <p>Those are not two problems either. They are the same missing asset.</p>

  <div class="stats">
    <div class="stat"><b>$26.94</b><span>Mean hourly wage in the Wilmington metro. The national
      figure is $32.66.</span></div>
    <div class="stat"><b>13.5%</b><span>Of metro employment is food preparation and serving, at
      $14.99 an hour &#8212; the largest single occupational group.</span></div>
    <div class="stat"><b>24%</b><span>Population growth in Brunswick County between 2020 and 2024.
      The fastest in North Carolina.</span></div>
    <div class="stat"><b>13,800</b><span>Jobs the Wilmington metro is projected to add by 2034.
      Someone is going to fill them.</span></div>
  </div>
 </div>
</section>

<section>
 <div class="hgwrap">
  <figure>
    <div class="dwrap">{LOOP_SVG}</div>
    <div class="dbar"><button type="button" class="dget" data-svg="loop">Download this diagram</button></div>
    <figcaption>The loop only closes if residents get hired. Break that link and attraction stops
      compounding: the jobs arrive, the wages do not move, and the political case for the next deal
      gets thinner every cycle. The bench in the middle is what holds it together.</figcaption>
  </figure>
 </div>
</section>

<section>
 <div class="hgwrap">
  <p class="eyebrow">The asset</p>
  <h2>The thing nobody can hand a site consultant</h2>
  <div class="rule"></div>
  <p>Ask an economic development office for its workforce case and you get institutions. A community
    college. A university. A career center. Real assets, every one &#8212; but they describe
    <strong>capacity</strong>, not <strong>supply</strong>. A site consultant already assumes you have
    a college.</p>
  <p>What almost no region can produce is this:</p>
  <div class="callout"><p>Here are 240 residents, assessed, moving toward these occupations, with
    timelines, and a person accountable for each one.</p></div>
  <p>That is a bench. It is not a training program and it is not a list of graduates. It is a live
    roster you can put in front of a site consultant in March and again in June and have it mean
    something different each time. Homegrown exists to produce it.</p>
 </div>
</section>

<section>
 <div class="hgwrap">
  <p class="eyebrow">The program</p>
  <h2>Next Move</h2>
  <div class="rule"></div>
  <p>Homegrown is what the town buys. Next Move is what the resident does: eight weeks, then ninety
    days of follow through. It is facilitated, it runs in cohorts, and every exercise operates on the
    participant's real situation rather than a case study.</p>

  <figure>
    <div class="dwrap">{FLOW_SVG}</div>
    <div class="dbar"><button type="button" class="dget" data-svg="flow">Download this diagram</button></div>
    <figcaption>Eight weeks to a decision and a plan, then ninety days holding the person to it.
      Four exits, because a program with only one acceptable outcome pushes people toward it whether
      it fits them or not.</figcaption>
  </figure>

  <div style="margin-top:34px">
  {_phrow('#F0855A', 'Weeks 1&#8211;2', 'Begin &#8212; where you actually are',
    'A behavioral assessment, a career diagnostic and an honest read on the ground: current wage, '
    'real skills, real constraints, and what this person actually wants. It ends in a one-page '
    'profile they keep. Adults do not learn from a syllabus handed to them. They learn from their '
    'own situation, examined properly.')}
  {_phrow('#FFE7A6', 'Weeks 3&#8211;5', 'Build &#8212; initiative, not information',
    'The core of the program and the part most training skips entirely. Proactivity. Spotting an '
    'opening. Planning for the obstacle before it arrives. Starting without being told to. This is '
    'competency work, run by a facilitator, against each participant&#8217;s live circumstances.')}
  {_phrow('#5FB6A6', 'Weeks 6&#8211;8', 'Become &#8212; one move, chosen and planned',
    'The participant picks a single next move and builds the ninety-day plan that makes it happen: '
    'implementation intentions written down, an advisor session, and a commitment they sign. Vague '
    'intent does not survive a Monday.')}
  {_phrow('#B18BE4', '+ 90 days', 'Follow through &#8212; the part everyone skips',
    'A weekly check-in and a monthly advisor touch for ninety days after the room empties. This is '
    'where a program either produces a result or produces a certificate. People forget most of what '
    'they hear inside a week, and the environment someone returns to shapes whether a new behavior '
    'survives far more than the content ever did.')}
  </div>
 </div>
</section>

<section>
 <div class="hgwrap">
  <p class="eyebrow">The exits</p>
  <h2>Four ways out, and the college gets three of them</h2>
  <div class="rule"></div>
  <div class="cards">
    {_card('#4FC3F7', 'Exit 01', 'Advance',
     'A raise, a promotion or a step across, with the employer the person already has. The cheapest '
     'good outcome available to a region, and the one nobody runs a program for.')}
    {_card('#5FB6A6', 'Exit 02', 'Switch',
     'Into a higher-wage occupation, usually inside a target industry. This is where the wage gap '
     'actually closes.')}
    {_card('#FFE7A6', 'Exit 03', 'Credential',
     'Enrolled at the community college or through the career center, in the right program, for a '
     'reason the person can articulate. Tracked to enrollment, not just to referral.')}
    {_card('#B18BE4', 'Exit 04', 'Own it',
     'Self-employment, where that is the honest answer. Most American small businesses have no '
     'employees at all, so this is a normal destination and not a consolation prize.')}
  </div>
  <p style="margin-top:26px">Only one of those four is a new job with a new employer, and that is
    deliberate.</p>
  <p>It also settles the question every partner asks first. <strong>Homegrown does not teach a trade
    and does not want to.</strong> When a resident needs a credential they are handed to the community
    college or the career center, and Homegrown reports whether they enrolled &#8212; which is worth
    real money to a college funded on enrollment. This is a feeder, not a competitor. That distinction
    is the difference between a partner network and a turf fight.</p>
 </div>
</section>

<section>
 <div class="hgwrap">
  <p class="eyebrow">The method</p>
  <h2>Why it is built on behavior, not curriculum</h2>
  <div class="rule"></div>
  <p>Because the curriculum version does not work, and this is one of the few corners of workforce
    development where the evidence is unusually clean.</p>
  <p>Across the research, something like <strong>ten to fifteen per cent</strong> of training
    transfers to the job. People forget roughly seventy per cent of what they are told within a day.
    The environment someone returns to shapes whether a new behavior survives more than the content
    ever did.</p>
  <p>The cleanest comparison anyone has run: fifteen hundred business owners in Togo were randomized
    into three groups &#8212; a control, conventional business training, and psychology-based training
    in personal initiative. Same hours, same mentoring afterwards. Conventional training moved profits
    eleven per cent, which was not statistically significant. <strong>The initiative training moved
    them thirty per cent at two years and fifty-two per cent at seven</strong>, and paid for itself
    inside a year.</p>
  <p>Worth saying plainly, because someone will ask and they should: those results come from
    microenterprises in Lom&#233;, not a Carolina metro, and at seven years the gains were
    concentrated among the men in the study. It is the strongest evidence available for this method.
    It is not proof of what happens here. Measuring what happens here is what the first cohorts
    are for.</p>
  <p>The structure around the method has its own record. Sector-focused programs have four randomized
    trials behind them, producing earnings gains of fourteen to thirty-eight per cent in the year after
    training and still running at twelve to thirty-four per cent years later. What those programs share
    is not a curriculum. It is cohorts, a real employer connection and genuine support around the
    person. That is the shape of this.</p>
 </div>
</section>

<section>
 <div class="hgwrap">
  <p class="eyebrow">The deliverable</p>
  <h2>What a town gets</h2>
  <div class="rule"></div>
  <ul class="plain">
    <li><b>A cohort.</b> Residents you nominate or we recruit alongside you, run through the eight
      weeks and the ninety days that follow.</li>
    <li><b>The bench report, quarterly.</b> Who is in motion, toward what, and how far along. Written
      to be handed to a site consultant or dropped into an RFI response, not filed.</li>
    <li><b>A local fill rate.</b> For the target employers you name, the share of new hires who
      already lived in the county.</li>
    <li><b>The handoffs, tracked.</b> Who was referred to the college or the career center, and who
      actually enrolled.</li>
    <li><b>A facilitator.</b> The program is run by a person in a room, not a video library with a
      completion bar.</li>
  </ul>
 </div>
</section>

<section>
 <div class="hgwrap">
  <p class="eyebrow">The numbers</p>
  <h2>How it is measured</h2>
  <div class="rule"></div>
  <p>Seat hours and satisfaction scores are not outcomes. These are, and they are set before the
    first cohort starts rather than chosen afterwards to suit the result.</p>
  <table class="mtab">
    <thead><tr><th>Measure</th><th>What it is</th></tr></thead>
    <tbody>
      <tr class="hero"><td>Local fill rate</td><td>The share of new hires at the target employers you
        name who already lived in the county. The number that decides whether the next incentive
        package survives a vote, and the one almost nobody reports.</td></tr>
      <tr><td>Documented move</td><td>The share of participants who advance, switch, enroll or
        register a business within 180 days.</td></tr>
      <tr><td>Wage change</td><td>Taken at baseline in week one, verified at 180 days.</td></tr>
      <tr><td>Completion</td><td>Target 70 per cent &#8212; deliberately the standard federally funded
        short-term programs are now held to.</td></tr>
      <tr><td>Handoff conversion</td><td>Referred to a college or career center, and enrolled. Two
        different numbers, reported as two different numbers.</td></tr>
      <tr><td>Twelve-month retention</td><td>Still living and working in the county a year on. The
        economic development metric, as opposed to the placement metric.</td></tr>
    </tbody>
  </table>
 </div>
</section>

<section>
 <div class="hgwrap">
  <p class="eyebrow">The money</p>
  <h2>How it is paid for</h2>
  <div class="rule"></div>
  <p>The question after &#8220;does it work&#8221; is always &#8220;which line does it come out
    of&#8221;. Usually more than one:</p>
  <ul class="plain">
    <li><b>Economic development discretionary budget.</b> The fastest route and the one an ED office
      controls outright. Most first cohorts should start here.</li>
    <li><b>The workforce board.</b> Entrepreneurial skills training and microenterprise services are
      allowable activities under federal workforce law, and boards are specifically directed to
      coordinate workforce with economic development. Board procurement runs on its own annual cycle,
      so treat this as a plan-ahead route rather than a fast one.</li>
    <li><b>Sector partnership and employer engagement grants.</b> North Carolina has funded local
      boards for precisely this kind of work, the Cape Fear board included.</li>
    <li><b>Capital readiness funding</b>, where the self-employment exit is in scope.</li>
    <li><b>Chambers and employers</b>, for the advancement track &#8212; the employer keeps the
      person, so the employer can carry part of the cost.</li>
  </ul>
  <p>One thing worth settling early rather than late. Federal training vouchers require a program
    that leads to a recognized credential. <strong>Homegrown does not, by design</strong> &#8212; it is
    the layer in front of the credential, not the credential itself. That keeps it off the state
    eligible training provider list and outside voucher funding, and it keeps it fast to start and
    free to change. If a town needs the voucher route specifically, that is a different build, and it
    is better said before anyone budgets than after.</p>
 </div>
</section>

<section>
 <div class="hgwrap">
  <p class="eyebrow">The first cohorts</p>
  <h2>Where it starts</h2>
  <div class="rule"></div>
  <p>SideKix is in Wilmington, North Carolina, and the Cape Fear region is where the first cohorts
    run.</p>
  <p>The regional case is not abstract. The Wilmington metro&#8217;s mean wage runs about seventeen
    per cent under the national figure, and its largest single occupational group is food preparation
    and serving at just under fifteen dollars an hour. Next door, Brunswick County is the fastest
    growing county in the state, up twenty-four per cent in four years, with Leland more than doubling
    since 2010 &#8212; a town adding residents considerably faster than it adds places for them to
    work.</p>
  <p>Two genuinely different problems. Wilmington needs people who already have jobs to move up.
    Leland needs residents who can build a career without crossing the bridge every morning. Same
    program, weighted differently, measured the same way.</p>
  <p><strong>Homegrown has not run yet.</strong> The first towns are design partners: they shape it,
    they get founding terms, and their results are the evidence every town after them sees. That is a
    better position than buying something finished, and it has the advantage of being true.</p>
 </div>
</section>

<div class="hgwrap">
 <div class="cta">
  <h2>Make the growth reach the people already there</h2>
  <p>Homegrown is open for design partners for its first cohorts, in the Cape Fear region and
    beyond. A first conversation runs about thirty minutes and does not need a budget attached
    to it.</p>
  <div class="btnrow">
    <a class="btn solid" href="mailto:support@sidekixhq.com?subject=SideKix%20Homegrown%20-%20enquiry&amp;body=Which%20town%20or%20county%3A%0AYour%20role%3A%0AWhat%20you%20are%20trying%20to%20fix%3A%0A">Start a conversation</a>
    <a class="btn ghost" href="how-it-works.html">How SideKix works</a>
  </div>
 </div>
</div>

<section>
 <div class="hgwrap narrow">
  <h2>Questions</h2>
  <div class="rule"></div>
  {''.join(f'<details><summary>{q}</summary><p>{a}</p></details>' for q, a in faqs)}
 </div>
</section>

<section class="src">
 <div class="hgwrap">
  <h2>Where these numbers come from</h2>
  <div class="rule"></div>
  <p>Every figure on this page is from a public source. Each is listed below, checked on
    {CHECKED}. Where a claim is weaker than it looks, that is said on the page rather than here.</p>
  <ol>
    {''.join(f'<li>{t} <a href="{u}" target="_blank" rel="noopener noreferrer">Source</a></li>' for t, u in SOURCES)}
  </ol>
 </div>
</section>

</main>"""

# ---------------------------------------------------------------- js
# The diagrams are styled by the page stylesheet, which does not travel with a
# serialised SVG. Export therefore clones the node, injects the resolved rules,
# paints the dark ground and rasterises at 2x so the result is usable in a deck.
JS = """
var HGCSS = [
 '.d-lab{font-family:\\'Space Grotesk\\',ui-monospace,monospace;font-size:13px;font-weight:500;',
 'letter-spacing:.16em;text-transform:uppercase;fill:#FFF8E8}',
 '.d-sub{font-family:\\'Poppins\\',system-ui,sans-serif;font-size:12.5px;fill:#A8A296}',
 '.d-wk{font-family:\\'Space Grotesk\\',ui-monospace,monospace;font-size:10.5px;',
 'letter-spacing:.18em;text-transform:uppercase}',
 '.d-mid{font-family:\\'Cormorant Garamond\\',Georgia,serif;font-size:23px;font-weight:600;fill:#FFF8E8}',
 '.d-mids{font-family:\\'Poppins\\',system-ui,sans-serif;font-size:12px;fill:#C6BE9E}',
 '.d-note{font-family:\\'Space Grotesk\\',ui-monospace,monospace;font-size:10px;',
 'letter-spacing:.16em;text-transform:uppercase;fill:#CDAA63}'
].join('');

// A serialised SVG in a data: URI cannot reach assets/fonts.css, so an export
// would fall back to system fonts. Read the faces the page already loaded, and
// inline the basic-latin subsets as data URIs. Everything here is best effort:
// any failure returns '' and the export proceeds on the fallback stacks.
var HGFONTS = null;
var WANT = { 'Cormorant Garamond': [600], 'Poppins': [400], 'Space Grotesk': [400, 500] };

function hgFaceRules(){
  var out = [];
  for (var i = 0; i < document.styleSheets.length; i++){
    var rules;
    try { rules = document.styleSheets[i].cssRules; } catch (e) { continue; }
    if (!rules) continue;
    for (var j = 0; j < rules.length; j++){
      var r = rules[j];
      if (r.type !== 5) continue;                       // CSSFontFaceRule
      var fam = (r.style.getPropertyValue('font-family') || '').replace(/['\"]/g, '').trim();
      if (!WANT[fam]) continue;
      var wt = parseInt(r.style.getPropertyValue('font-weight'), 10) || 400;
      if (WANT[fam].indexOf(wt) === -1) continue;
      if ((r.style.getPropertyValue('font-style') || 'normal').trim() !== 'normal') continue;
      var range = r.style.getPropertyValue('unicode-range') || '';
      // basic latin only; the diagrams carry nothing outside it
      var flat = range.toUpperCase().replace(/\\s+/g, '');
      if (range && flat.indexOf('U+0-FF') === -1 && flat.indexOf('U+0000-00FF') === -1) continue;
      var src = r.style.getPropertyValue('src') || '';
      var m = src.match(/url\\(\\s*["']?([^"')]+)["']?\\s*\\)/);
      if (!m) continue;
      out.push({ fam: fam, wt: wt, url: new URL(m[1], document.styleSheets[i].href || location.href).href });
    }
  }
  return out;
}

function hgFontCSS(){
  if (HGFONTS !== null) { return Promise.resolve(HGFONTS); }
  var faces = hgFaceRules();
  if (!faces.length || !window.fetch || !window.Promise) { HGFONTS = ''; return Promise.resolve(''); }
  var jobs = faces.map(function(f){
    return fetch(f.url).then(function(res){
      if (!res.ok) { throw new Error('font ' + res.status); }
      return res.blob();
    }).then(function(blob){
      return new Promise(function(resolve, reject){
        var fr = new FileReader();
        fr.onload = function(){ resolve(fr.result); };
        fr.onerror = reject;
        fr.readAsDataURL(blob);
      });
    }).then(function(data){
      return "@font-face{font-family:'" + f.fam + "';font-style:normal;font-weight:" + f.wt +
             ";src:url(" + data + ") format('woff2');}";
    }).catch(function(){ return ''; });
  });
  var bail = new Promise(function(resolve){ setTimeout(function(){ resolve(null); }, 4000); });
  return Promise.race([Promise.all(jobs), bail]).then(function(parts){
    HGFONTS = parts ? parts.join('') : '';
    return HGFONTS;
  }).catch(function(){ HGFONTS = ''; return ''; });
}

function hgRaster(svg, name, fontCSS){
  var box = svg.viewBox.baseVal;
  var w = box && box.width ? box.width : svg.clientWidth;
  var h = box && box.height ? box.height : svg.clientHeight;
  var clone = svg.cloneNode(true);
  clone.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
  clone.setAttribute('width', w);
  clone.setAttribute('height', h);
  var st = document.createElementNS('http://www.w3.org/2000/svg', 'style');
  st.appendChild(document.createTextNode((fontCSS || '') + HGCSS));
  clone.insertBefore(st, clone.firstChild);

  var markup = new XMLSerializer().serializeToString(clone);
  var url = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(markup);
  var img = new Image();
  img.onload = function(){
    var scale = 2;
    var cv = document.createElement('canvas');
    cv.width = w * scale; cv.height = h * scale;
    var cx = cv.getContext('2d');
    cx.fillStyle = '#0b0a06';
    cx.fillRect(0, 0, cv.width, cv.height);
    cx.drawImage(img, 0, 0, cv.width, cv.height);
    cv.toBlob(function(blob){
      if (!blob) { return; }
      var a = document.createElement('a');
      var href = URL.createObjectURL(blob);
      a.href = href; a.download = 'sidekix-homegrown-' + name + '.png';
      document.body.appendChild(a); a.click(); a.remove();
      setTimeout(function(){ URL.revokeObjectURL(href); }, 4000);
    }, 'image/png');
  };
  img.onerror = function(){
    // Rasterising failed; hand over the vector rather than nothing at all.
    var a = document.createElement('a');
    a.href = url; a.download = 'sidekix-homegrown-' + name + '.svg';
    document.body.appendChild(a); a.click(); a.remove();
  };
  img.src = url;
}

Array.prototype.forEach.call(document.querySelectorAll('.hg .dget'), function(btn){
  btn.addEventListener('click', function(){
    var fig = btn.closest('figure');
    var svg = fig && fig.querySelector('svg');
    if (!svg) { return; }
    var label = btn.textContent;
    btn.textContent = 'Preparing\\u2026';
    btn.disabled = true;
    var done = function(){ btn.textContent = label; btn.disabled = false; };
    hgFontCSS().then(function(css){
      hgRaster(svg, btn.getAttribute('data-svg') || 'diagram', css);
    }).catch(function(){
      hgRaster(svg, btn.getAttribute('data-svg') || 'diagram', '');
    }).then(function(){ setTimeout(done, 1200); }, function(){ setTimeout(done, 1200); });
  });
});
"""

# ---------------------------------------------------------------- write
html = page("homegrown.html", TITLE, DESC, MAIN,
            extra_css=CSS, extra_js=JS,
            schema=(svc, faqschema, crumbs),
            og_title="SideKix Homegrown")

stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
html = html.replace("<!DOCTYPE html>\n",
                    f"<!DOCTYPE html>\n<!-- kx-build {stamp} homegrown -->\n", 1)

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write(html)
print("homegrown.html written:", len(html) // 1024, "KB ->", OUT)
