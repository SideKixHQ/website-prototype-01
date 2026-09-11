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
/* .hg p caps every paragraph at 68ch; without auto margins this one sits left of
   centre inside the centred hero instead of under it */
.hg .hgstamp{font-family:var(--util);font-size:10.5px;letter-spacing:.2em;text-transform:uppercase;
  color:var(--gold-mid);margin:30px auto 0;max-width:60ch}

/* One reading column, centred on the same axis as the hero and the diagrams.
   Before this, prose sat left in a 68ch box whose centre landed 160px left of
   everything else, which is what made the page look out of true. Diagrams,
   stat rows, card grids and the table still run the full width. */
/* One vertical scale for the whole page. Before this the gaps between blocks
   ran 6, 16, 18, 22, 26, 28, 30, 32 and 34px, four of them set inline on single
   paragraphs, and a figure could be followed 6px later by a list. Three steps:
   tight inside a unit, mid between blocks, wide around a full-width object. */
.hg{--hgcol:48rem;--sp-tight:16px;--sp-mid:26px;--sp-wide:34px}
.hg .hgwrap > .eyebrow,
.hg .hgwrap > h2,
.hg .hgwrap > h3,
.hg .hgwrap > .rule,
.hg .hgwrap > p,
.hg .hgwrap > ul.plain,
.hg .hgwrap > .callout{max-width:var(--hgcol);margin-left:auto;margin-right:auto}

/* section furniture */
.hg section{margin:clamp(52px,7vw,86px) 0 0}
/* the shell already gives the first section 132px of top padding; adding the section
   rhythm on top of it double-spaces the page under the hero. On this page the first
   section is the opening diagram rather than text, so it also sits closer than the
   shell default, which would strand it behind a screen of black. */
.hg section:first-of-type{margin-top:0;padding-top:clamp(30px,4vw,48px) !important}
/* and the opening diagram closes with a full section break, not a hairline */
.hg .hgfig{padding-bottom:clamp(64px,8vw,104px)}
.hg .hgfig figure{margin:0}
.hg h2{font-family:var(--display);font-weight:600;font-size:clamp(27px,3.9vw,42px);
  line-height:1.14;color:#FFF8E8;margin:0 0 6px}
.hg h3{font-family:var(--display);font-weight:600;font-size:clamp(20px,2.4vw,25px);
  line-height:1.2;color:#FFF3DC;margin:0 0 8px}
.hg p{font-size:16px;line-height:1.72;color:#B9B4AB;margin:0 0 var(--sp-tight);max-width:68ch}
.hg p.lead{font-size:17.5px;color:#CFC9BE}
.hg strong{color:#EFE7D6;font-weight:600}
.hg .rule{height:1px;background:linear-gradient(90deg,transparent,rgba(212,168,86,.42),transparent);
  margin:0 0 var(--sp-wide)}

/* The line the page turns on. A gold marker sits under it at rest so it still
   reads as emphasis in a screenshot or on a phone, and sweeps up into a full
   highlight on hover. Touch devices, which never hover, get the full state. */
.hg .punch{display:inline;background-image:linear-gradient(90deg,rgba(212,168,86,.34),rgba(212,168,86,.34));
  background-repeat:no-repeat;background-size:100% 10%;background-position:0 93%;
  transition:background-size .55s cubic-bezier(.22,.61,.36,1)}
.hg h2:hover .punch,.hg .punch:hover,.hg h2:focus-within .punch{background-size:100% 46%}
@media (hover:none){.hg .punch{background-size:100% 46%}}
@media (prefers-reduced-motion:reduce){.hg .punch{transition:none}}
/* The turn of the sentence, in red. Bright rather than deep: this heading also
   carries the gold marker, and the site's own --app-red measures 1.71:1 against
   that strip, well under the 3:1 large text needs. #FF6B5B clears both grounds
   and still reads brighter than the near-white heading around it. */
.hg .punch .no{color:#FF6B5B}

/* A sticky rail beside the content, which is the documented pattern for a long
   page: the sections stay visible and scrollable, and the rail says where you
   are and lets you jump. Nothing is hidden behind a click. */
.hg .hglayout{display:grid;grid-template-columns:200px minmax(0,1fr);gap:clamp(28px,4vw,64px);
  align-items:start}
.hg .hgrail{position:sticky;top:34px}
.hg .hgrail ol{list-style:none;margin:0;padding:0}
.hg .hgrail a{display:flex;gap:11px;align-items:baseline;padding:9px 0;text-decoration:none;
  color:#7E786F;font-size:14.5px;line-height:1.4;transition:color .22s}
.hg .hgrail a span{font-family:var(--util);font-size:10px;letter-spacing:.14em;color:#85806F;
  flex:none;transition:color .22s}
.hg .hgrail a:hover{color:#D8D2C6}
.hg .hgrail a[aria-current="true"]{color:#FFF8E8}
.hg .hgrail a[aria-current="true"] span{color:var(--gold)}
.hg .hgrail a:focus-visible{outline:3px solid var(--gold-pale);outline-offset:3px;border-radius:4px}
.hg .hgsec{scroll-margin-top:28px}
.hg .hgsec + .hgsec{margin-top:clamp(64px,8vw,104px)}
/* below the rail's width the page is one column and the rail rides along the top */
@media (max-width:900px){
  .hg .hglayout{grid-template-columns:minmax(0,1fr)}
  .hg .hgrail{position:static;border-bottom:1px solid rgba(212,168,86,.18);
    margin-bottom:34px;padding-bottom:6px}
  .hg .hgrail ol{display:flex;gap:20px;overflow-x:auto;-webkit-overflow-scrolling:touch;
    scrollbar-width:none}
  .hg .hgrail ol::-webkit-scrollbar{display:none}
  .hg .hgrail a{white-space:nowrap;padding:4px 0 12px;border-bottom:2px solid transparent;
    margin-bottom:-8px}
  .hg .hgrail a[aria-current="true"]{border-bottom-color:var(--gold)}
}

/* Movement. Every rule here describes the finished state as the default, and the
   .hgmo class that JS adds is what opts an element into starting from somewhere
   else. No JS, or reduced motion, and the page is simply already arrived. */
.hg .hgmo .rise{opacity:0;transform:translateY(18px)}
.hg .rise{transition:opacity .7s cubic-bezier(.22,.61,.36,1),
  transform .7s cubic-bezier(.22,.61,.36,1)}
.hg .rise.seen{opacity:1;transform:none}
.hg .hgmo .dwrap svg .pop{opacity:0}
.hg .dwrap svg .pop{transition:opacity .5s ease}
.hg .hgmo .dwrap svg .grow{transform:scaleX(0);transform-origin:left center}
.hg .dwrap svg .grow{transition:transform .9s cubic-bezier(.22,.61,.36,1)}
@media (prefers-reduced-motion:reduce){
  .hg .rise,.hg .dwrap svg .pop,.hg .dwrap svg .grow{transition:none !important;
    opacity:1 !important;transform:none !important}
}

/* the exits were four cards for four short labels, which is a lot of frame for
   very little content on a page already full of frames */
.hg .exits{list-style:none;margin:var(--sp-mid) 0;padding:0;display:grid;gap:2px;
  grid-template-columns:repeat(auto-fit,minmax(240px,1fr))}
.hg .exits li{padding:16px 20px 18px 0}
.hg .exits b{display:block;font-family:var(--util);font-size:10px;letter-spacing:.2em;
  text-transform:uppercase;color:var(--c,#CDAA63);margin-bottom:9px}
.hg .exits strong{display:block;font-family:var(--display);font-size:22px;font-weight:600;
  color:#FFF3DC;margin-bottom:6px}
.hg .exits span{display:block;font-size:14.8px;line-height:1.6;color:#A8A296}

/* stat row */
.hg .stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:14px;margin:var(--sp-wide) 0 var(--sp-mid)}
.hg .stat{border:1px solid rgba(212,168,86,.28);border-radius:14px;padding:22px 20px;
  background:linear-gradient(180deg,rgba(26,20,8,.5),rgba(8,8,9,.72))}
.hg .stat b{display:block;font-family:var(--display);font-size:clamp(30px,4.2vw,40px);
  line-height:1;color:var(--cream);margin-bottom:9px}
.hg .stat span{display:block;font-size:14px;line-height:1.55;color:#A8A296}

/* figure / diagram */
.hg figure{margin:var(--sp-wide) 0}
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
.hg .d-row{font-family:var(--util);font-size:12px;letter-spacing:.1em;text-transform:uppercase;
  fill:#E3DED2}

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
.hg ul.plain{list-style:none;margin:var(--sp-tight) 0;padding:0;max-width:68ch}
.hg ul.plain li{position:relative;padding:9px 0 9px 26px;font-size:15.6px;line-height:1.66;
  color:#B9B4AB;border-top:1px solid rgba(212,168,86,.13)}
.hg ul.plain li:first-child{border-top:none}
.hg ul.plain li::before{content:'';position:absolute;left:4px;top:19px;width:7px;height:7px;
  border-radius:50%;background:var(--gold-mid)}
.hg ul.plain li b{color:#EFE7D6;font-weight:600}

/* metric table */
.hg .mtab{width:100%;border-collapse:collapse;margin:var(--sp-mid) 0;font-size:15.2px}
.hg .mtab th,.hg .mtab td{text-align:left;padding:14px 14px 14px 0;
  border-top:1px solid rgba(212,168,86,.16);vertical-align:top;line-height:1.6}
.hg .mtab thead th{border-top:none;font-family:var(--util);font-size:10.5px;letter-spacing:.18em;
  text-transform:uppercase;color:var(--gold-mid);padding-bottom:9px}
.hg .mtab td:first-child{color:#EFE7D6;font-weight:600;width:34%}
.hg .mtab td{color:#A8A296}
.hg .mtab tr.hero td:first-child{color:var(--cream)}

/* callout */
.hg .callout{border-left:2px solid var(--gold);padding:4px 0 4px 22px;margin:var(--sp-mid) 0;
  max-width:70ch}
.hg .callout p{font-family:var(--display);font-size:clamp(19px,2.5vw,25px);line-height:1.38;
  color:#FFF3DC;margin:0}

/* cta */
.hg .hgcta{border:1px solid rgba(212,168,86,.36);border-radius:20px;padding:clamp(30px,5vw,52px);
  text-align:center;background:radial-gradient(120% 140% at 50% 0%,rgba(34,26,10,.7),rgba(7,7,8,.92));
  margin-top:clamp(52px,7vw,86px)}
/* the deck used to orphan its last two words onto a line of their own, which is
   what made this block read as crooked under a one line heading */
.hg .hgcta h2{margin-bottom:12px;max-width:22ch;margin-left:auto;margin-right:auto;
  text-wrap:balance}
.hg .hgcta p{margin-left:auto;margin-right:auto;text-align:center;max-width:48ch;
  text-wrap:balance}
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
<desc id="hgd1d">Four stages turning clockwise in a ring: attract, expand, hire local and prove,
set around a centre marked The Bench: local residents assessed, matched and tracked. The bench feeds
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

PH = [("Weeks 1 to 2", "Begin", "#F0855A", "Where you actually", "are. Assessed."),
      ("Weeks 3 to 5", "Build", "#FFE7A6", "Initiative, applied to", "your real situation."),
      ("Weeks 6 to 8", "Become", "#5FB6A6", "One move chosen.", "A ninety-day plan."),
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
<desc id="hgd2d">Four stages left to right. Begin in weeks one and two, Build in weeks three to
five, Become in weeks six to eight, then ninety days of follow through, feeding down into four
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

# The third diagram: what the eight weeks are supposed to move, and how far.
# Five named behaviors down the side, the same four stages across the top, and
# a bar that grows as the behavior goes from named to habitual. It is the
# design of the program, not a plot of results, and the caption says so.
# Two levels, kept separate, because collapsing them is the easy mistake.
# The NAME is the behavior: a trainable disposition that experience builds and
# practice keeps, and the thing a course can actually be designed around. The
# text beside it is a behavioral indicator: one witnessable act that evidences
# the behavior moved. You train information seeking; "asks the person who knows"
# is only proof it happened, so it cannot be the name.
# Names that are states of mind fail the other way. "Knows", "has a picture of"
# and "explores" cannot be scored by a manager or an advisor, however true.
#
# The five map onto the individual-contributor end of the Leadership Architect
# set, in order: plans and aligns, resourcefulness, decision quality, courage,
# action orientation. That end is the half that can be scored on one person; the
# rest measures somebody running other people, which is the wrong instrument for
# a town upskilling its residents. None of Korn Ferry's competency names are used
# here, because the library is licensed and this page is not.
# Initiative is the one with a randomised trial behind it, and Frese and Fay's
# construct is self-starting plus proactive plus persistent, which is why its
# indicator carries both starting and still being at it in month three.
#
# All five are written to read twice: as a growth plan for the resident, and as a
# hiring profile for the employer, who is the one the report goes to.
COMP = [
 ("Goal setting",        "#F0855A", "names a role and a date, and what comes first"),
 ("Information seeking", "#FFE7A6", "asks somebody doing the job, instead of guessing"),
 ("Decisiveness",        "#5FB6A6", "commits with what they have, rather than waiting"),
 ("Self-advocacy",       "#4FC3F7", "puts in for it, and asks again after a no"),
 ("Initiative",          "#B18BE4", "starts it unasked, and is still at it in month three"),
]
STAGE = [("Weeks 1 to 2", "named"), ("Weeks 3 to 5", "practiced"),
         ("Weeks 6 to 8", "applied"), ("+ 90 days", "habitual")]
_CX = [330, 500, 670, 840]          # column left edges, 140 wide
_CH = [13, 18, 24, 30]              # bar height grows with the behavior
_CO = [".17", ".38", ".64", ".96"]  # and so does its weight
_RY = [130, 195, 260, 325, 390]

def _grow_rows():
    out = []
    for i, (name, colour, _) in enumerate(COMP):
        cy = _RY[i]
        out.append(f'<text class="d-row" x="305" y="{cy + 4}" text-anchor="end">{name}</text>')
        for j in range(4):
            h = _CH[j]
            out.append(f'<rect x="{_CX[j]}" y="{cy - h / 2}" width="140" height="{h}" '
                       f'rx="{h / 2}" class="grow" fill="{colour}" fill-opacity="{_CO[j]}"/>')
        if i < len(COMP) - 1:
            out.append(f'<path d="M0,{cy + 32} H980" stroke="#A1853E" stroke-opacity=".13" '
                       f'stroke-width="1"/>')
    return "".join(out)

def _grow_cols():
    out = []
    for j, (stage, level) in enumerate(STAGE):
        cx = _CX[j] + 70
        out.append(f'<rect x="{_CX[j]}" y="88" width="140" height="330" rx="16" '
                   f'fill="#FFFFFF" fill-opacity=".017"/>')
        out.append(f'<text class="d-wk" x="{cx}" y="46" text-anchor="middle" fill="#CDAA63">{stage}</text>')
        out.append(f'<text class="d-sub" x="{cx}" y="68" text-anchor="middle">{level}</text>')
    return "".join(out)

GROWTH_SVG = f"""<svg viewBox="0 0 1000 470" role="img" aria-labelledby="hgd3t hgd3d"
     xmlns="http://www.w3.org/2000/svg">
<title id="hgd3t">What the program is built to move</title>
<desc id="hgd3d">Five competencies down the side: names the target, makes the call, finds out,
bets on themselves, and takes initiative. The same four stages across the top: weeks one to two
where each behavior is named, weeks three to five where it is practiced, weeks six to eight where
it is applied, and the ninety days after, where it becomes habitual. Each bar grows across the row.
This is the design of the program rather than a plot of measured results.</desc>
{_grow_cols()}
<text class="d-note" x="305" y="46" text-anchor="end">The competency</text>
{_grow_rows()}
<text class="d-sub" x="500" y="446" text-anchor="middle">Every one of them scored as observable behavior, at baseline in week one and again at day 180.</text>
</svg>"""


CULTURE_SVG = """<svg viewBox="0 0 900 578" role="img" aria-labelledby="hgd4t hgd4d"
     xmlns="http://www.w3.org/2000/svg">
<title id="hgd4t">The parts a culture is made of</title>
<desc id="hgd4d">Five parts set in a ring around a centre: mission, values, process, incentives and
environment. People sit in the middle, because every one of the five lands on them. A faint circle
joins the five to show they also act on each other.</desc>
{_defs('D')}
<circle cx="450" cy="312" r="214" fill="none" stroke="#A1853E" stroke-opacity=".22"
        stroke-width="1" stroke-dasharray="2 7"/>
<g stroke="#A1853E" stroke-opacity=".5" stroke-width="1.2" stroke-dasharray="3 5">
  <path d="M450,220 L450,142"/><path d="M537,284 L612,259"/><path d="M504,386 L550,450"/><path d="M396,386 L350,450"/><path d="M363,284 L288,259"/>
</g>
<circle cx="450" cy="312" r="196" fill="url(#hgglowD)"/>
<circle cx="450" cy="312" r="92" fill="url(#hgcoreD)" stroke="#D4A856" stroke-opacity=".62"
        stroke-width="1.6"/>
<text class="d-note" x="450" y="286" text-anchor="middle">The center</text>
<text class="d-mid" x="450" y="316" text-anchor="middle">People</text>
<text class="d-mids" x="450" y="340" text-anchor="middle">all five land here</text>
<rect x="352" y="60" width="196" height="76" rx="13" fill="url(#hgcardD)" stroke="#4FC3F7" stroke-opacity=".55" stroke-width="1.4"/><text class="d-lab" x="450" y="93" text-anchor="middle" style="fill:#4FC3F7">Mission</text><text class="d-sub" x="450" y="115" text-anchor="middle">what this is for</text><rect x="556" y="208" width="196" height="76" rx="13" fill="url(#hgcardD)" stroke="#FFE7A6" stroke-opacity=".55" stroke-width="1.4"/><text class="d-lab" x="654" y="241" text-anchor="middle" style="fill:#FFE7A6">Values</text><text class="d-sub" x="654" y="263" text-anchor="middle">what we say matters</text><rect x="478" y="447" width="196" height="76" rx="13" fill="url(#hgcardD)" stroke="#5FB6A6" stroke-opacity=".55" stroke-width="1.4"/><text class="d-lab" x="576" y="480" text-anchor="middle" style="fill:#5FB6A6">Process</text><text class="d-sub" x="576" y="502" text-anchor="middle">how the work moves</text><rect x="226" y="447" width="196" height="76" rx="13" fill="url(#hgcardD)" stroke="#B18BE4" stroke-opacity=".55" stroke-width="1.4"/><text class="d-lab" x="324" y="480" text-anchor="middle" style="fill:#B18BE4">Incentives</text><text class="d-sub" x="324" y="502" text-anchor="middle">what gets rewarded</text><rect x="148" y="208" width="196" height="76" rx="13" fill="url(#hgcardD)" stroke="#F0855A" stroke-opacity=".55" stroke-width="1.4"/><text class="d-lab" x="246" y="241" text-anchor="middle" style="fill:#F0855A">Environment</text><text class="d-sub" x="246" y="263" text-anchor="middle">where the work happens</text>
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
 ('Occupational Employment and Wage Statistics, Wilmington NC metropolitan area, May 2024. '
  'mean hourly wage $26.94 against $32.66 nationally; food preparation and serving 13.5% of area '
  'employment at $14.99. U.S. Bureau of Labor Statistics.',
  'https://www.bls.gov/regions/southeast/news-release/occupationalemploymentandwages_wilmington.htm'),
 ('North Carolina employment projections 2024 to 2034. The Wilmington area projected to add '
  'roughly 13,800 jobs, a 6.9% increase. NC Department of Commerce.',
  'https://www.commerce.nc.gov/data-tools-reports/labor-market-data-tools/employment-projections/north-carolina-employment-projections-2024-2034-regional-occupational-trends'),
 ('Brunswick County the fastest-growing county in North Carolina, up 24% between April 2020 and July '
  '2024 to 169,448; Leland at 30,264 in 2023, more than double its 2010 count. Business North Carolina, '
  'citing the Census Bureau and the NC Office of State Budget and Management.',
  'https://businessnc.com/community-close-up-brunswick-new-hanover-pender-counties/'),
 ('Workforce availability a leading site selection factor, and roughly 60% of manufacturers naming '
  'talent shortages a top concern. Business Facilities.',
  'https://businessfacilities.com/topics/site-selection-factors/education-and-workforce/'),
 ('Training transfer at roughly 10 to 15%, and forgetting of about 70% within a day. Summary of the '
  'transfer-of-training literature.',
  'https://www.aimforbehavior.com/library/only-10-to-15-percent-of-what-people/'),
 ('Campos et al., <em>Teaching personal initiative beats traditional training in boosting small business '
  'in West Africa</em>, Science, 2017. A 30% profit gain against a statistically insignificant 11% '
  'for conventional training.',
  'https://www.science.org/doi/10.1126/science.aan5329'),
 ('Seven-year follow-up to the same trial. A 52% profit gain, with effects concentrated among men. '
  'World Bank Development Impact.',
  'https://blogs.worldbank.org/en/impactevaluations/personal-initiative-training-continues-to-yield-positive-benefit'),
 ('Career adaptability and its four dimensions, concern, control, curiosity and confidence, as '
  'measured by the Career Adapt-Abilities Scale, validated across 13 countries. Savickas and '
  'Porfeli, and the CAAS chapter.',
  'https://www.marksavickas.com/files/1_Savickas_bio/Career%20Construction%20Theory/Publications/Book%20Chapters/CAAS_Chapter.pdf'),
 ('Confidence in one&#8217;s own skills predicting career progress, and the finding that most '
  'workers on a career path can name and communicate the skills employers value. Harvard Project '
  'on Workforce.',
  'https://pw.hks.harvard.edu/post/navigating-opportunity-career-information-and-mobility-in-low-wage-employment'),
 ('The odds of leaving low wage work roughly halving every four years, reaching about one per '
  'cent by year ten. Harvard Project on Workforce, reported via the Harvard Gazette.',
  'https://news.harvard.edu/gazette/story/2022/01/helping-trapped-low-wage-workers-employers-struggling-to-fill-spots/'),
 ('Sector-focused training programs across four randomized trials. Earnings gains of 14 to 38% '
  'in the year after training, persisting at 12 to 34%. WorkRise.',
  'https://workrisenetwork.org/working-knowledge/evidence-sector-focused-training-programs-shows-significant-and-persistent'),
 ('Entrepreneurial skills training and microenterprise services as allowable WIOA activities, and the '
  'direction to coordinate workforce with economic development. WorkforceGPS, U.S. Department of Labor.',
  'https://www.workforcegps.org/resources/2019/10/30/13/49/Resources-to-Support-Entrepreneurship'),
 ('Eligible Training Provider List requirements. Programs must lead to a recognized postsecondary '
  'credential, certificate of apprenticeship or licence to draw voucher funding. WorkforceGPS.',
  'https://ion.workforcegps.org/resources/2016/03/10/17/06/Eligible_Training_Provider_Provisions_and_ETPLs_in_WOIA'),
 ('Sector partnership grants to North Carolina local workforce boards, the Cape Fear board among them. '
  'NC Department of Commerce.',
  'https://www.commerce.nc.gov/news/press-releases/2024/01/31/nc-commerce-awards-grants-local-workforce-boards-supporting-sector-partnerships-advanced'),
 ('A 70% completion standard applied to federally funded short-term workforce programs. NC Community '
  'College System, Workforce Pell resources.',
  'https://www.nccommunitycolleges.edu/workforce-pell/'),
]

SECTIONS = [
    ("what",    "What we do"),
    ("skills",  "The skills"),
    ("program", "The program"),
    ("culture", "Culture"),
    ("gets",    "What you get"),
    ("case",    "Why it pays"),
]
RAIL = "".join(
    f'<li><a href="#{sid}" data-rail="{sid}"><span>{i:02d}</span>{label}</a></li>'
    for i, (sid, label) in enumerate(SECTIONS, 1))

MAIN = f"""<main id="maincontent" class="hg">

<header class="hghero">
  <div class="hgwrap">
    <p class="eyebrow">SideKix Homegrown</p>
    <h1>The jobs you bring in should go to the people already here.</h1>
    <p class="hgdek">Homegrown runs eight weeks in your town, with the people already there.
      Behavior, skills, career development, personal development, leadership. Ninety days making it
      stick. Then a list of names: who is ready, for what, and by when.</p>
    <p class="hgstamp">For economic developers, workforce boards and chambers</p>
  </div>
</header>

<section class="hgfig">
 <div class="hgwrap">
  <figure>
    <div class="dwrap">{LOOP_SVG}</div>
    <div class="dbar"><button type="button" class="dget" data-svg="loop">Download this diagram</button></div>
    <figcaption>Attracting business, growing the employers you have and getting residents hired are
      usually run as three programs. They are one loop, and it only closes on the third.</figcaption>
  </figure>
 </div>
</figure>
</section>

<div class="hgwrap">
 <div class="hglayout">

  <nav class="hgrail" aria-label="Sections of this page">
    <ol>{RAIL}</ol>
  </nav>

  <div class="hgbody">

   <section id="what" class="hgsec">
    <p class="eyebrow">What we do</p>
    <h2>Find people, and make them ready</h2>
    <div class="rule"></div>
    <p class="lead">Find people. Build a bench on deliberate skills and behaviors. Help them grow.
      Help the businesses grow.</p>
    <p>A resident spends eight weeks on five things, and every exercise runs on their own
      situation rather than a case study.</p>
    <ul class="plain">
      <li><b>Behavior.</b> How somebody acts when nobody is telling them what to do.</li>
      <li><b>Skills.</b> The specific thing an employer here is hiring for.</li>
      <li><b>Career development.</b> What the next rung is, what it pays, and how people get
        onto it.</li>
      <li><b>Personal development.</b> Money, confidence, transport, childcare. The things that
        decide whether any of the rest holds.</li>
      <li><b>Leadership.</b> Running a shift, running a team, or running your own thing.</li>
    </ul>
    <p>Those five are the curriculum. They are not the report. You cannot measure whether somebody
      was taught leadership, only whether they have started acting like one, so the report scores
      five behaviors instead. Each is a habit that experience builds and practice keeps, and each
      is listed with the act that proves it moved.</p>

    <figure>
      <div class="dwrap">{GROWTH_SVG}</div>
      <div class="dbar"><button type="button" class="dget" data-svg="growth">Download this diagram</button></div>
      <figcaption>The design of the program, not a plot of results.</figcaption>
    </figure>

    <ul class="plain">
      <li><b>Goal setting.</b> Names a role and a date, and says out loud what comes first.</li>
      <li><b>Information seeking.</b> Goes to somebody already doing the job and asks what it pays
        and what it takes, instead of guessing.</li>
      <li><b>Decisiveness.</b> Commits to a next move with what they have, rather than waiting to
        be handed the options.</li>
      <li><b>Self-advocacy.</b> Puts in for it before feeling ready, and asks again after a no.</li>
      <li><b>Initiative.</b> Starts the thing nobody asked for, and is still at it in month
        three.</li>
    </ul>
    <p>That list is a hiring profile as much as a growth plan. An employer reading it sees somebody
      who can say where they are going, will find the answer instead of guessing, decide instead of
      escalating, ask for the harder job, and still be there in month three. Which is the point,
      because the employer is who the report goes to.</p>
   </section>

   <section id="skills" class="hgsec">
    <p class="eyebrow">The skills</p>
    <h2>The syllabus is built per town</h2>
    <div class="rule"></div>
    <p class="lead">Behavior is the constant. Skills are not, and no town should accept a syllabus
      that turns up already written. Three inputs decide what gets taught.</p>
    <ul class="plain">
      <li><b>What is here now.</b> The employers in your county and the work they are actually
        hiring for, from your own labor market data.</li>
      <li><b>What you are chasing.</b> The target industries already in your strategy. Leland has
        published its own: life sciences, information technology, medical technology, aerospace,
        marine biology and wind energy.</li>
      <li><b>The gap between the two.</b> Where the work you want and the people you have do not
        line up is exactly where the skills teaching goes.</li>
    </ul>
    <p>Behavior transfers between towns. The skills half does not, and a program that pretends
      otherwise is selling you somebody else&#8217;s curriculum.</p>
   </section>

   <section id="program" class="hgsec">
    <p class="eyebrow">The program</p>
    <h2>Eight weeks, then ninety days</h2>
    <div class="rule"></div>
    <figure>
      <div class="dwrap">{FLOW_SVG}</div>
      <div class="dbar"><button type="button" class="dget" data-svg="flow">Download this diagram</button></div>
      <figcaption>Four exits, because a program with one acceptable outcome pushes people toward it
        whether it fits or not.</figcaption>
    </figure>
    <ul class="exits">
      <li style="--c:#4FC3F7"><b>Exit 01</b><strong>Advance</strong><span>A raise or a step across,
        with the employer they already have.</span></li>
      <li style="--c:#5FB6A6"><b>Exit 02</b><strong>Switch</strong><span>Into a higher wage
        occupation. Where the wage gap actually closes.</span></li>
      <li style="--c:#FFE7A6"><b>Exit 03</b><strong>Credential</strong><span>Enrolled at the
        college, for a reason they can say out loud.</span></li>
      <li style="--c:#B18BE4"><b>Exit 04</b><strong>Own it</strong><span>Self employment, where that
        is the honest answer.</span></li>
    </ul>
    <p><strong>Homegrown does not teach a trade and does not want to.</strong>
      When somebody needs a credential they go to the college, and we report whether they enrolled.
      This is a feeder, not a competitor.</p>
   </section>

   <section id="culture" class="hgsec">
    <p class="eyebrow">Cultural architecture</p>
    <h2>Culture is the other side of the desk</h2>
    <div class="rule"></div>
    <p>Somebody who moves up into a badly run workplace comes back down. Turnover is not a resident
      problem and retention is not a resident achievement. Both are built into how an employer runs,
      day to day.</p>
    <p><strong>Culture is alive.</strong> Everything you do, and everything you do not do, lands on
      it. It is built out of six things, and five of them meet in the same place.</p>
    <figure>
      <div class="dwrap">{CULTURE_SVG}</div>
      <div class="dbar"><button type="button" class="dget" data-svg="culture">Download this diagram</button></div>
      <figcaption>Move any one of the five and you have moved the culture, whether you meant to
        or not.</figcaption>
    </figure>
    <p>Identify the culture you actually have, map the one you want, then
      train your leaders to manage and measure it every day. That last step makes it stick, and it
      is the one most places skip.</p>
   </section>

   <section id="gets" class="hgsec">
    <p class="eyebrow">The deliverable</p>
    <h2>What a town gets</h2>
    <div class="rule"></div>
    <ul class="plain">
      <li><b>A cohort.</b> The residents you nominate, or that we recruit alongside you.</li>
      <li><b>The bench report, quarterly.</b> Who is in motion, toward what, how far along. Written
        to hand to a site consultant, not to file.</li>
      <li><b>A local fill rate.</b> For the employers you name, the share of new hires who already
        lived in the county.</li>
      <li><b>The handoffs, tracked.</b> Referred to the college, and separately, enrolled.</li>
      <li><b>A facilitator.</b> A person in a room, not a video library with a progress bar.</li>
      <li><b>The SideKix platform, for everybody in the cohort.</b> Community, resource library,
        self discoveries, events, training and AI guidance from Kix.</li>
    </ul>
    <details>
      <summary>How it is measured</summary>
      <table class="mtab">
        <thead><tr><th>Measure</th><th>What it is</th></tr></thead>
        <tbody>
          <tr class="hero"><td>Local fill rate</td><td>Share of new hires at the employers you name
            who already lived in the county.</td></tr>
          <tr><td>Documented move</td><td>Advanced, switched, enrolled or registered a business
            within 180 days.</td></tr>
          <tr><td>Wage change</td><td>Baseline in week one, verified at day 180.</td></tr>
          <tr><td>Completion</td><td>Target 70 per cent, the standard federally funded short
            programs are held to.</td></tr>
          <tr><td>Twelve month retention</td><td>Still living and working in the county a year
            on.</td></tr>
        </tbody>
      </table>
    </details>
   </section>

   <section id="case" class="hgsec">
    <p class="eyebrow">The case</p>
    <h2>Why a town pays for this</h2>
    <div class="rule"></div>
    <p class="lead">Most American metros have the same shape of problem. Employment is fine. Wages
      are not. And the growth that does land fills up with people who moved in for it.</p>
    <div class="stats">
      <div class="stat"><b data-to="26.94" data-dec="2" data-pre="$">$26.94</b><span>Mean hourly
        wage in the Wilmington metro. The national figure is $32.66.</span></div>
      <div class="stat"><b data-to="13.5" data-dec="1" data-suf="%">13.5%</b><span>Of metro jobs are
        food preparation and serving, at $14.99 an hour.</span></div>
      <div class="stat"><b data-to="24" data-dec="0" data-suf="%">24%</b><span>Population growth in
        Brunswick County, 2020 to 2024. The fastest in North Carolina.</span></div>
      <div class="stat"><b data-to="13800" data-dec="0" data-sep="1">13,800</b><span>Jobs the metro
        is projected to add by 2034. Somebody is going to fill them.</span></div>
    </div>
    <p>There is a clock on it: every four years somebody stays in low wage
      work, the odds of getting out roughly halve. By year ten they are down to about one in a
      hundred. Those four figures are Wilmington&#8217;s, because that is where the first cohorts
      run. Every town gets the same four from its own county.</p>
    <div class="callout"><p>You cannot sell a region you cannot staff, and you cannot defend a deal
      to a council whose residents did not get hired.</p></div>
   </section>

  </div>
 </div>
</div>

<div class="hgwrap">
 <div class="hgcta">
  <h2>Make the growth reach the people already there</h2>
  <p>A first conversation takes thirty minutes and needs no budget attached.</p>
  <div class="btnrow">
    <a class="btn solid" href="mailto:support@sidekixhq.com?subject=SideKix%20Homegrown%20-%20enquiry&amp;body=Which%20town%20or%20county%3A%0AYour%20role%3A%0AWhat%20you%20are%20trying%20to%20fix%3A%0A">Ask about your town</a>
  </div>
 </div>
</div>

<section class="src">
 <div class="hgwrap">
  <details>
    <summary>Why behavior and not curriculum</summary>
    <div class="stats">
      <div class="stat"><b>10 to 15%</b><span>Of ordinary training that ever shows up in
        somebody&#8217;s work.</span></div>
      <div class="stat"><b data-to="11" data-dec="0" data-suf="%">11%</b><span>Profit change from
        conventional business training, in a controlled trial of 1,500 owners in West Africa. Not
        statistically significant.</span></div>
      <div class="stat"><b data-to="30" data-dec="0" data-suf="%">30%</b><span>Same hours, same
        mentoring, behavior based instead. Fifty two per cent by year seven.</span></div>
    </div>
    <p>One caveat, up front rather than buried. That trial ran with small
      business owners in West Africa, not a Carolina metro, and by year seven the gains were much
      stronger for the men in it. It is the best evidence this method has, and it is not proof of
      what happens here.</p>
    <p>Four of the five scored competencies come from career adaptability, built for people changing
      jobs rather than managers running teams. The fifth is initiative, the construct with the trial
      behind it. None needs a supervisor&#8217;s title.</p>
  </details>
  <details>
    <summary>How it is paid for</summary>
    <ul class="plain">
      <li><b>Economic development budget.</b> Fastest, and the one an ED office controls
        outright.</li>
      <li><b>The workforce board.</b> Entrepreneurial skills training and microenterprise services
        are allowable under federal workforce law, on its own annual procurement cycle.</li>
      <li><b>Sector partnership and employer engagement grants.</b> North Carolina funds local
        boards for exactly this, the Cape Fear board included.</li>
      <li><b>Chambers and employers</b>, for the advancement track, where the employer keeps the
        person.</li>
    </ul>
    <p>Federal training vouchers require a program that leads to a credential. Homegrown does not,
      by design: it is the layer in front of the credential, which keeps it fast to start.</p>
  </details>
  <details>
    <summary>Where it starts, and whether it travels</summary>
    <p>The program runs anywhere with a county, an employer base and residents who are stuck. What
      changes between towns is the target industries, the local numbers and the weighting of the
      four exits. The eight weeks, the five competencies and the reporting do not change.</p>
    <p>SideKix is in Wilmington, so the Cape Fear region is where the first cohorts run. Wilmington
      needs people who already have jobs to move up. Leland, which has more than doubled since 2010,
      needs residents who can build a career without crossing the bridge every morning.</p>
    <p><strong>Homegrown has not run yet.</strong> The first towns are design partners: they shape
      it, they get founding terms, and their results are the evidence every town after them
      sees.</p>
  </details>
  {''.join(f'<details><summary>{q}</summary><p>{a}</p></details>' for q, a in faqs)}
  <details>
    <summary>Where these numbers come from</summary>
    <p>Every figure on this page is public, listed here, and checked on {CHECKED}.</p>
    <ol>
      {''.join(f'<li>{t} <a href="{u}" target="_blank" rel="noopener noreferrer">Source</a></li>' for t, u in SOURCES)}
    </ol>
  </details>
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
 'letter-spacing:.16em;text-transform:uppercase;fill:#CDAA63}',
 '.d-row{font-family:\\'Space Grotesk\\',ui-monospace,monospace;font-size:12px;',
 'letter-spacing:.1em;text-transform:uppercase;fill:#E3DED2}'
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


// Everything below is enhancement. The stylesheet already describes the arrived
// state, so this adds .hgmo first to opt the page into starting from somewhere
// else, and only when motion is actually wanted.
var HG = document.querySelector('.hg');
var HGREDUCED = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
var HGOBS = 'IntersectionObserver' in window;
if (HG && HGOBS && !HGREDUCED) { HG.classList.add('hgmo'); }

// --- the rail follows the section you are actually reading -------------------
(function(){
  var links = [].slice.call(document.querySelectorAll('.hgrail a[data-rail]'));
  var secs = links.map(function(a){ return document.getElementById(a.getAttribute('data-rail')); })
                  .filter(Boolean);
  if (!links.length || !secs.length) { return; }
  var current = null;
  function mark(id){
    if (id === current) { return; }
    current = id;
    links.forEach(function(a){
      if (a.getAttribute('data-rail') === id) { a.setAttribute('aria-current', 'true'); }
      else { a.removeAttribute('aria-current'); }
    });
  }
  // The last section whose top has crossed the reading line. Deterministic, where
  // an intersection band gets ambiguous when a tall section and a short one both
  // sit inside it.
  function pick(){
    var line = window.innerHeight * 0.34, best = secs[0];
    for (var i = 0; i < secs.length; i++) {
      if (secs[i].getBoundingClientRect().top <= line) { best = secs[i]; }
    }
    mark(best.id);
  }
  var queued = false;
  function onScroll(){
    if (queued) { return; }
    queued = true;
    requestAnimationFrame(function(){ queued = false; pick(); });
  }
  pick();
  window.addEventListener('scroll', onScroll, { passive: true });
  window.addEventListener('resize', onScroll, { passive: true });
})();

// --- sections arrive, rather than being already there ------------------------
(function(){
  if (!HGOBS) { return; }
  var bits = [].slice.call(document.querySelectorAll(
    '.hg .hgsec > *, .hg .hgcta, .hg .hghero > .hgwrap > *'));
  bits.forEach(function(el){ el.classList.add('rise'); });
  if (HGREDUCED) { bits.forEach(function(el){ el.classList.add('seen'); }); return; }
  var io = new IntersectionObserver(function(entries, obs){
    entries.forEach(function(e){
      if (!e.isIntersecting) { return; }
      var el = e.target;
      var sibs = [].slice.call(el.parentNode.children).filter(function(n){
        return n.classList && n.classList.contains('rise');
      });
      el.style.transitionDelay = Math.min(sibs.indexOf(el), 5) * 55 + 'ms';
      el.classList.add('seen');
      obs.unobserve(el);
    });
  }, { rootMargin: '0px 0px -12% 0px', threshold: 0.05 });
  bits.forEach(function(el){ io.observe(el); });
})();

// --- numbers count up --------------------------------------------------------
(function(){
  var nums = [].slice.call(document.querySelectorAll('.hg [data-to]'));
  if (!nums.length) { return; }
  function render(el, v){
    var dec = +(el.getAttribute('data-dec') || 0);
    var t = v.toFixed(dec);
    if (el.getAttribute('data-sep')) { t = (+t).toLocaleString('en-US'); }
    el.textContent = (el.getAttribute('data-pre') || '') + t + (el.getAttribute('data-suf') || '');
  }
  if (!HGOBS || HGREDUCED) { return; }               // the markup already reads correctly
  nums.forEach(function(el){ el.setAttribute('aria-label', el.textContent.trim()); });
  var io = new IntersectionObserver(function(entries, obs){
    entries.forEach(function(e){
      if (!e.isIntersecting) { return; }
      var el = e.target, to = parseFloat(el.getAttribute('data-to')), t0 = null;
      obs.unobserve(el);
      function step(ts){
        if (t0 === null) { t0 = ts; }
        var k = Math.min((ts - t0) / 1100, 1);
        render(el, to * (1 - Math.pow(1 - k, 3)));    // ease out, lands exactly on the value
        if (k < 1) { requestAnimationFrame(step); }
      }
      render(el, 0);
      requestAnimationFrame(step);
    });
  }, { threshold: 0.6 });
  nums.forEach(function(el){ io.observe(el); });
})();

// --- the diagrams draw themselves -------------------------------------------
(function(){
  if (!HGOBS || HGREDUCED) { return; }
  [].slice.call(document.querySelectorAll('.hg .dwrap svg')).forEach(function(svg){
    var marks = [].slice.call(svg.querySelectorAll('rect,circle,text,path'));
    var strokes = marks.filter(function(n){
      var f = n.getAttribute('fill');
      return n.tagName === 'path' && (f === 'none' || (!f && n.parentNode.getAttribute('fill') === 'none'));
    });
    marks.forEach(function(n){ if (!n.classList.contains('grow')) { n.classList.add('pop'); } });
    strokes.forEach(function(n){
      var len = 0;
      try { len = n.getTotalLength(); } catch (err) { return; }
      if (!len) { return; }
      n.style.strokeDasharray = len;
      n.style.strokeDashoffset = len;
      n.style.transition = 'stroke-dashoffset 1.1s cubic-bezier(.22,.61,.36,1)';
    });
    var io = new IntersectionObserver(function(entries, obs){
      entries.forEach(function(e){
        if (!e.isIntersecting) { return; }
        obs.unobserve(e.target);
        marks.forEach(function(n, i){
          var d = Math.min(i * 26, 900);
          n.style.transitionDelay = d + 'ms';
          n.classList.remove('pop');
          if (n.classList.contains('grow')) { n.style.transform = 'none'; }
        });
        strokes.forEach(function(n){ n.style.strokeDashoffset = '0'; });
      });
    }, { threshold: 0.25 });
    io.observe(svg);
  });
})();

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
