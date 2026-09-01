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
SEO_LIMIT = 60

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
/* The plain list is the page for anyone whose browser is not running the
   script, which includes most answer engines. A browser that IS running it
   gets the interactive grid instead and never sees this, with no flash of it
   first, because the class lands before the body is parsed. */
.kx-js #kx-seo{display:none}
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


BROWSER_CSS = r"""
.kx-controls{display:flex;flex-wrap:wrap;gap:10px;align-items:center;justify-content:center;max-width:1100px;margin:0 auto 26px;padding:0 24px}
.kx-controls input[type=search],.kx-controls select{font-family:'Space Grotesk',system-ui,sans-serif;font-size:13px;color:#EFE9DF;background:rgba(239,233,223,.05);border:1px solid rgba(239,233,223,.18);border-radius:999px;padding:11px 16px;outline:none;transition:border-color .15s ease,background .15s ease}
.kx-controls input[type=search]{flex:1 1 320px;min-width:220px}
.kx-controls input[type=search]::placeholder{color:#8B857C}
.kx-controls input[type=search]:focus,.kx-controls select:focus{border-color:rgba(214,178,102,.7);background:rgba(239,233,223,.09)}
.kx-controls select{cursor:pointer;-webkit-appearance:none;appearance:none;padding-right:34px;background-image:linear-gradient(45deg,transparent 50%,#9B958B 50%),linear-gradient(135deg,#9B958B 50%,transparent 50%);background-position:calc(100% - 18px) 50%,calc(100% - 13px) 50%;background-size:5px 5px,5px 5px;background-repeat:no-repeat}
.kx-controls select option{background:#14120F;color:#EFE9DF}
.kx-clear{font-family:'Space Grotesk',system-ui,sans-serif;font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:#9B958B;background:none;border:none;cursor:pointer;padding:11px 6px}
.kx-clear:hover{color:#EFE9DF}
/* The selected pill used to change only its border, which on a dark page is
   almost invisible. Selection is a solid fill now: one glance tells you what
   you are looking at. */
#kx-filters .kx-store[aria-pressed="true"]{background:#D6B266;border-color:#D6B266;color:#14120F;font-weight:600}
#kx-filters .kx-store[aria-pressed="true"] .kx-n{color:#14120F;opacity:.65}
#kx-filters .kx-store{transition:background .15s ease,color .15s ease,border-color .15s ease}
.kx-go{display:inline-flex;align-items:center;gap:6px;margin-top:14px;font-family:'Space Grotesk',system-ui,sans-serif;font-size:12px;letter-spacing:.07em;text-transform:uppercase;color:#D6B266;text-decoration:none;border-bottom:1px solid rgba(214,178,102,.35);padding-bottom:2px}
.kx-go:hover{color:#EFE9DF;border-bottom-color:#EFE9DF}
.kx-hits{text-align:center;color:#9B958B;font-size:13px;margin:0 0 22px}
.kx-more{grid-column:1/-1;justify-self:center;margin-top:6px;font-family:'Space Grotesk',system-ui,sans-serif;font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:#EFE9DF;background:rgba(239,233,223,.05);border:1px solid rgba(239,233,223,.22);border-radius:999px;padding:14px 26px;cursor:pointer;min-height:44px}
.kx-more:hover{background:#D6B266;border-color:#D6B266;color:#14120F}

/* Phones.

   The grid already collapsed to one column below 640px, but a 1fr track keeps
   an automatic minimum sized to its content, so each card resolved to 515px
   inside a 348px column and 147px of every card sat off the right edge,
   clipped. minmax(0,1fr) lets the track shrink to the screen.

   The rest is thumbs: iOS zooms the whole page when a focused input is under
   16px and never zooms back, and the card's main action was a 19px-tall line
   of text where 44px is the floor. */
@media (max-width:640px){
  #kx-grid{grid-template-columns:minmax(0,1fr) !important}
  .kx-controls{padding:0 20px;gap:8px}
  .kx-controls input[type=search]{flex:1 1 100%;font-size:16px;padding:13px 16px}
  .kx-controls select{flex:1 1 calc(50% - 4px);min-width:0;font-size:16px;padding:13px 30px 13px 14px}
  .kx-clear{min-height:44px;padding:12px 10px;flex:0 0 auto}
  .kx-go{min-height:44px;align-items:flex-end;padding-bottom:12px;margin-top:8px}
  .kx-badge{font-size:11px;padding:6px 10px}
  .kx-badge.kx-where{max-width:100%}
  .kx-hits{margin-bottom:16px}
  #kx-seo{padding:0 20px 40px}
}
"""

BROWSER_JS = r"""
/* The events browser.

   This replaces the original topic-chip filter for one reason: the chips were
   the only way to narrow 842 events, they were rebuilt from whatever word each
   host happened to use for a topic, and there were 47 of them. Someone looking
   for a free online funding session in Ohio had no way to say so.

   It reads events.json itself rather than reaching into the page's variables,
   so it stands on its own and cannot be broken by a change elsewhere. */
(function(){
  var MONTHS=['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC'];
  var FULL=['January','February','March','April','May','June','July','August','September','October','November','December'];
  var STROKE=['#D6B266','#8FD4B6','#C48E7A'];
  var all=[],view=[],topic='All';
  var PAGE=60, shown=PAGE;

  /* The page's own script renders every one of the 842 cards and rebuilds the
     topic chips the moment events.json lands. This block replaces both. Doing
     that work first cost about half a second of blocked main thread and a
     second parse of a 500KB file to produce a result nobody ever saw, which is
     why the page felt slow arriving from anywhere else. These stubs are
     installed while that fetch is still in flight. */
  try{ window.renderGrid=function(){}; window.renderFilters=function(){}; }catch(e){}

  function esc(s){return String(s==null?'':s).replace(/[&<>"']/g,function(c){
    return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];});}

  function costOf(e){
    var c=(e.cost||'').trim();
    if(!c) return 'Cost not listed';
    if(/no fee|no cost|free/i.test(c)) return 'No cost';
    return c;
  }
  function isFree(e){return /no fee|no cost|free/i.test(e.cost||'');}
  function when(e){var d=new Date(e.start);return isNaN(d)?null:d;}

  function time(d){
    var h=d.getHours(),m=d.getMinutes();
    if(!h&&!m) return '';
    var ap=h>=12?'pm':'am',hh=h%12||12;
    return hh+(m?':'+String(m).padStart(2,'0'):'')+ap;
  }

  function blobOf(e){
    return ((e.title||'')+' '+(e.host||'')+' '+(e.summary||'')+' '+
            (e.location||'')+' '+(e.topic||'')+' '+(e.host_topic||'')+' '+
            (e.scope||'')).toLowerCase();
  }

  function card(e,i){
    var d=when(e),bits=[];
    bits.push('<span class="kx-badge kx-mode-'+esc((e.mode||'other').toLowerCase().replace(/ /g,'-'))+'">'+esc(e.mode||'Check with host')+'</span>');
    if(e.location&&!/online/i.test(e.location)){
      bits.push('<span class="kx-badge kx-where">'+esc(e.location)+'</span>');
    }
    bits.push('<span class="kx-badge kx-cost">'+esc(costOf(e))+'</span>');
    if(e.scope&&e.scope!=='National'){bits.push('<span class="kx-badge">'+esc(e.scope)+'</span>');}
    var t=time(d);
    return '<article class="kx-ev" data-i="'+i+'" data-topic="'+esc(e.topic||'')+'">'+
      '<div class="rough" aria-hidden="true"></div>'+
      '<div class="kx-num" style="-webkit-text-stroke:1.5px '+STROKE[i%3]+';">'+d.getDate()+'</div>'+
      '<div class="kx-mon">'+MONTHS[d.getMonth()]+'</div>'+
      '<h3><a href="'+esc(e.url)+'" target="_blank" rel="noopener">'+esc(e.title)+'</a></h3>'+
      /* Only show a description when there is one. Where the host publishes
         nothing, the listing row leaves behind a scrap like "Online Meeting
         (Live)", which the badges below already say. */
      ((e.summary||'').length>45 ? '<p>'+esc(e.summary.slice(0,200))+'</p>' : '')+
      '<div class="kx-meta">'+esc(e.host)+' &middot; '+esc(FULL[d.getMonth()]+' '+d.getDate())+(t?' &middot; '+esc(t):'')+'</div>'+
      '<div class="kx-badges">'+bits.join('')+'</div>'+
      '<a class="kx-go" href="'+esc(e.url)+'" target="_blank" rel="noopener">Open event page &rarr;</a>'+
      '</article>';
  }

  function apply(){
    var q=(document.getElementById('kx-q').value||'').trim().toLowerCase();
    var type=document.getElementById('kx-f-type').value;
    var cost=document.getElementById('kx-f-cost').value;
    var state=document.getElementById('kx-f-state').value;
    var terms=q.split(/\s+/).filter(Boolean);

    view=all.filter(function(e){
      if(topic!=='All'&&e.topic!==topic) return false;
      if(type&&(e.mode||'')!==type) return false;
      if(cost==='free'&&!isFree(e)) return false;
      if(cost==='unknown'&&(e.cost||'').trim()) return false;
      if(state&&e.scope!==state) return false;
      if(terms.length){
        var b=e._blob;
        for(var i=0;i<terms.length;i++){ if(b.indexOf(terms[i])<0) return false; }
      }
      return true;
    });

    shown=PAGE;
    draw();
  }

  function draw(){
    /* Only the first screenful is built. Writing 300 cards at once was 197ms
       of main-thread work before anyone had scrolled past the third one. */
    var grid=document.getElementById('kx-grid');
    var left=view.length-shown;
    grid.innerHTML=view.length
      ? view.slice(0,shown).map(card).join('') +
        (left>0 ? '<button type="button" id="kx-more" class="kx-more">Show '+
          Math.min(PAGE,left)+' more of '+view.length+'</button>' : '')
      : '<p style="grid-column:1/-1;text-align:center;color:#9B958B;font-size:15px;">Nothing matches those filters yet. Clearing one of them usually helps.</p>';

    var more=document.getElementById('kx-more');
    if(more) more.addEventListener('click',function(){ shown+=PAGE; draw(); });

    var hits=document.getElementById('kx-hits');
    if(hits){
      hits.textContent=view.length===0?'No events match'
        :(view.length===1?'1 event':view.length+' events')+
         (left>0?', showing '+shown:'');
    }
    var c=document.getElementById('kx-count');
    if(c) c.textContent=view.length;
    var none=document.getElementById('kx-none');
    if(none) none.hidden=true;
  }

  function pills(){
    var box=document.getElementById('kx-filters');
    if(!box) return;
    var counts={},order=[];
    all.forEach(function(e){
      var t=e.topic||'Business';
      if(counts[t]===undefined){counts[t]=0;order.push(t);}
      counts[t]++;
    });
    order.sort(function(a,b){return counts[b]-counts[a];});
    var list=['All'].concat(order);
    counts['All']=all.length;
    box.innerHTML=list.map(function(t){
      return '<button type="button" class="kx-store" aria-pressed="'+(t===topic)+
             '" data-topic="'+esc(t)+'">'+esc(t)+
             '<span class="kx-n" aria-hidden="true">'+counts[t]+'</span></button>';
    }).join('');
    box.querySelectorAll('button').forEach(function(b){
      b.addEventListener('click',function(){
        topic=b.getAttribute('data-topic');
        box.querySelectorAll('button').forEach(function(o){
          o.setAttribute('aria-pressed',String(o===b));
        });
        apply();
      });
    });
  }

  function controls(){
    var grid=document.getElementById('kx-grid');
    if(!grid||document.getElementById('kx-q')) return;
    var states=[],modes=[];
    all.forEach(function(e){
      if(e.scope&&states.indexOf(e.scope)<0) states.push(e.scope);
      if(e.mode&&modes.indexOf(e.mode)<0) modes.push(e.mode);
    });
    states.sort(); modes.sort();

    var bar=document.createElement('div');
    bar.className='kx-controls';
    bar.innerHTML=
      '<input type="search" id="kx-q" aria-label="Search events" placeholder="Search by title, host, topic or place">'+
      '<select id="kx-f-type" aria-label="Format"><option value="">Any format</option>'+
        modes.map(function(m){return '<option value="'+esc(m)+'">'+esc(m)+'</option>';}).join('')+'</select>'+
      '<select id="kx-f-cost" aria-label="Cost"><option value="">Any cost</option>'+
        '<option value="free">No cost</option><option value="unknown">Cost not listed</option></select>'+
      '<select id="kx-f-state" aria-label="Where"><option value="">Anywhere</option>'+
        states.map(function(s){return '<option value="'+esc(s)+'">'+esc(s)+'</option>';}).join('')+'</select>'+
      '<button type="button" class="kx-clear" id="kx-clear">Clear</button>';
    var hits=document.createElement('p');
    hits.className='kx-hits'; hits.id='kx-hits';
    grid.parentNode.insertBefore(bar,grid);
    grid.parentNode.insertBefore(hits,grid);

    document.getElementById('kx-q').addEventListener('input',apply);
    ['kx-f-type','kx-f-cost','kx-f-state'].forEach(function(id){
      document.getElementById(id).addEventListener('change',apply);
    });
    document.getElementById('kx-clear').addEventListener('click',function(){
      document.getElementById('kx-q').value='';
      ['kx-f-type','kx-f-cost','kx-f-state'].forEach(function(id){
        document.getElementById(id).value='';
      });
      topic='All';
      var box=document.getElementById('kx-filters');
      if(box) box.querySelectorAll('button').forEach(function(o){
        o.setAttribute('aria-pressed',String(o.getAttribute('data-topic')==='All'));
      });
      apply();
    });
  }

  function boot(events){
    var now=Date.now();
    all=events.filter(function(e){
      var d=new Date(e.start); return !isNaN(d)&&d.getTime()>now;
    }).sort(function(a,b){return new Date(a.start)-new Date(b.start);});
    all.forEach(function(e){ e._blob=blobOf(e); });
    var seo=document.getElementById('kx-seo');
    if(seo) seo.hidden=true;
    pills(); controls(); apply();
  }

  function start(){
    /* The page has already fetched events.json and put it in EVENTS. Fetching
       it again, with no-store on top, meant a second 500KB download and a
       second parse of the same file on every single visit. Wait for the one
       that is already coming, and only fetch if it never arrives. */
    var waited=0;
    (function poll(){
      if (window.EVENTS && window.EVENTS.length){ boot(window.EVENTS); return; }
      waited+=40;
      if (waited>9000){
        fetch('events.json').then(function(r){return r.json();})
          .then(function(j){ boot(j.events||[]); })
          .catch(function(){ /* the plain list stays up, which is the point of it */ });
        return;
      }
      setTimeout(poll,40);
    })();
  }

  if(document.readyState==='loading'){
    document.addEventListener('DOMContentLoaded',function(){setTimeout(start,80);});
  } else { setTimeout(start,80); }
})();
"""

BROWSER_START = "<!-- kx:browser:start -->"
BROWSER_END = "<!-- kx:browser:end -->"


def add_browser(page: str) -> str:
    """Install the search-and-filter browser in place of the topic-chip filter.

    Injected as one block between markers so it can be refreshed or removed
    whole, and so running this script twice does not leave two copies behind.
    """
    block = (BROWSER_START + "\n<style>" + BROWSER_CSS + "</style>\n<script>"
             + BROWSER_JS + "</script>\n" + BROWSER_END)
    if BROWSER_START in page and BROWSER_END in page:
        page = re.sub(re.escape(BROWSER_START) + r"[\s\S]*?" + re.escape(BROWSER_END),
                      lambda _: block, page, count=1)
        note(True, "events browser refreshed")
    else:
        page = page.replace("</body>", block + "\n</body>", 1)
        note(True, "events browser installed")
    return page


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
    page = add_browser(page)

    if "function costLabel" not in page:
        page = page.replace("function stageOf(e){", HELPERS + "\nfunction stageOf(e){", 1)
        note("function costLabel" in page, "card helpers")
    else:
        note(True, "card helpers (already present)")

    if "kx-js" not in page:
        page = page.replace(
            "</head>",
            "<script>document.documentElement.className+=' kx-js';</script>\n</head>", 1)
        note(True, "no-script fallback flag")
    else:
        note(True, "no-script fallback flag (already present)")

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
