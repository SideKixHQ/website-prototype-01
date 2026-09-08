# -*- coding: utf-8 -*-
"""The page that answers "what business should I start".

Twenty links would be a list. This is a table, because the question is a
comparison and the answer is the shape of the trade: the cheap ones to start
are the ones with the least protection from competition, and the two with the
clearest published cost figures are the two hardest to run.

Sortable and filterable in the browser, and readable with JavaScript off,
because the table is in the HTML rather than built from a script.
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from toolgen import page, SITE
from guidedata import (load, cost_text, article, DEMAND_LABEL, GROUP_ORDER)
import html as H

def e(s):
    return H.escape(str(s), quote=True)

def titlecase(name):
    small = {"a", "an", "and", "for", "in", "of", "or", "the", "to"}
    out = []
    for i, w in enumerate(name.split()):
        if w in ("AI", "EV"):
            out.append(w)
        elif i and w.lower() in small:
            out.append(w.lower())
        else:
            out.append(w[:1].upper() + w[1:])
    return " ".join(out)

def short(t, n=118):
    t = " ".join(t.split())
    if len(t) <= n:
        return t
    cut = t[:n].rsplit(" ", 1)[0]
    return cut + "..."

CSS = """
.gh{max-width:64rem;margin:0 auto}
.gh .intro{margin:0 0 26px;padding:22px 24px;border-left:3px solid #D4A856;
  background:rgba(212,168,86,.06);border-radius:0 12px 12px 0}
.gh .intro p{margin:0 0 12px;font-size:17px;line-height:1.7;color:#E8DEC4}
.gh .intro p:last-child{margin:0}
.gh h2{font-size:clamp(19px,2.6vw,23px);color:#FFF8D8;margin:38px 0 12px;
  font-family:Georgia,serif;font-weight:600}
.gh p{font-size:16.5px;line-height:1.78;color:#CFC7B4;margin:0 0 16px}
.gh a{color:#F3E4A8}
.gh .ctrls{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin:0 0 16px}
.gh .ctrls label{font-family:var(--util,inherit);font-size:10.5px;
  letter-spacing:.18em;text-transform:uppercase;color:#BDB4A4}
.gh input[type=search],.gh select{background:rgba(255,255,255,.04);
  border:1px solid rgba(212,168,86,.3);border-radius:9px;color:#F0E8D4;
  padding:10px 13px;font:inherit;font-size:15px;min-height:44px}
.gh input[type=search]{flex:1 1 15rem;min-width:0}
.gh input[type=search]:focus-visible,.gh select:focus-visible,
.gh th button:focus-visible{outline:3px solid #F3E4A8;outline-offset:2px}
.gh .tblwrap{overflow-x:auto;-webkit-overflow-scrolling:touch;margin:0 0 10px}
.gh .tblwrap:focus-visible{outline:3px solid #F3E4A8;outline-offset:3px;border-radius:8px}
.gh table{width:100%;border-collapse:collapse;font-size:15px;min-width:44rem}
.gh th,.gh td{text-align:left;padding:13px 14px;vertical-align:top;
  border-bottom:1px solid rgba(212,168,86,.18);color:#CFC7B4}
/* No sticky header. The wrapper needs overflow-x for narrow screens, and an
   overflow container becomes the sticky positioning context, so the th sticks
   to a box that never scrolls vertically and simply scrolls away. Twenty rows
   of name, dollars, one word and a number do not need it. */
.gh thead th{color:#BDB4A4;font-family:var(--util,inherit);font-size:10.5px;
  letter-spacing:.14em;text-transform:uppercase;font-weight:700;
  background:#191713;padding:0;box-shadow:0 1px 0 rgba(212,168,86,.3)}
.gh #ghtable{scroll-margin-top:96px}
.gh th button{all:unset;display:block;width:100%;box-sizing:border-box;
  padding:13px 14px;cursor:pointer;color:inherit;font:inherit;
  letter-spacing:inherit;text-transform:inherit}
.gh th button:hover{color:#F3E4A8}
.gh th button::after{content:"";opacity:.5;margin-left:6px}
.gh th[aria-sort=ascending] button::after{content:"\\2191";opacity:1}
.gh th[aria-sort=descending] button::after{content:"\\2193";opacity:1}
.gh td.nm a{font-weight:600;text-decoration:none;color:#F3E4A8}
.gh td.nm a:hover{text-decoration:underline}
.gh td.nm small{display:block;color:#9C9484;font-size:13px;margin-top:3px;
  font-family:var(--util,inherit);letter-spacing:.06em;text-transform:uppercase}
.gh td.hp{color:#B9AF98;font-size:14.5px;line-height:1.6;max-width:24rem}
.gh .np{color:#8A8272;font-style:italic}
.gh .dem{display:inline-flex;align-items:center;gap:7px;white-space:nowrap}
.gh .dot{width:9px;height:9px;border-radius:50%;flex:none}
.gh .d-up{background:#7FBF7F}.gh .d-flat{background:#D4A856}
.gh .d-down{background:#D08A6A}.gh .d-unclear{background:#8A8272}
.gh tr[hidden]{display:none}
.gh .count{font-size:14px;color:#9C9484;margin:0 0 22px}
.gh .none{padding:26px;text-align:center;color:#B9AF98}
.gh .cite{margin:34px 0 0;padding:18px 20px;border:1px solid rgba(212,168,86,.28);
  border-radius:12px;background:rgba(212,168,86,.04)}
.gh .cite b{display:block;font-family:var(--util,inherit);font-size:10.5px;
  letter-spacing:.2em;text-transform:uppercase;color:#BDB4A4;margin:0 0 8px}
.gh .cite p{font-size:14.5px;margin:0;color:#CFC7B4}
@media(max-width:640px){.gh td.hp{display:none}.gh th.hp{display:none}}
"""

JS = """
(function(){
  var tb=document.getElementById('ghbody'); if(!tb) return;
  var rows=[].slice.call(tb.querySelectorAll('tr'));
  var q=document.getElementById('ghq'), g=document.getElementById('ghg');
  var cnt=document.getElementById('ghcount'), none=document.getElementById('ghnone');
  var heads=[].slice.call(document.querySelectorAll('#ghtable thead th[data-k]'));

  function apply(){
    var t=(q.value||'').toLowerCase().trim(), grp=g.value, n=0;
    rows.forEach(function(r){
      var okg = !grp || r.getAttribute('data-group')===grp;
      var okt = !t || (r.getAttribute('data-find')||'').indexOf(t)>-1;
      var show = okg && okt;
      r.hidden = !show; if(show) n++;
    });
    cnt.textContent = n===rows.length ? (n+' businesses')
      : (n+' of '+rows.length+' businesses');
    none.hidden = n>0;
  }
  q.addEventListener('input', apply);
  g.addEventListener('change', apply);

  /* Sorting on the numeric columns uses data-v, because "$2,000 to $10,000"
     and "Not published" do not sort as text in any useful order. */
  function sortBy(k, dir){
    var mult = dir==='descending' ? -1 : 1;
    rows.sort(function(a,b){
      var x=a.getAttribute('data-'+k), y=b.getAttribute('data-'+k);
      var nx=parseFloat(x), ny=parseFloat(y);
      /* A missing value sinks in BOTH directions. Sorting most-expensive-first
         and getting the twelve with no published figure at the top is not what
         anybody meant by that click. */
      if(!isNaN(nx) && !isNaN(ny)){
        if(nx!==ny) return (nx-ny)*mult;
      } else if(!isNaN(nx)) { return -1; }
      else if(!isNaN(ny)) { return 1; }
      else if(x!==y) { return (x<y?-1:1)*mult; }
      return a.getAttribute('data-name')<b.getAttribute('data-name')?-1:1;
    });
    rows.forEach(function(r){ tb.appendChild(r); });
  }
  heads.forEach(function(th){
    var btn=th.querySelector('button'); if(!btn) return;
    btn.addEventListener('click', function(){
      var cur=th.getAttribute('aria-sort');
      var dir = cur==='ascending' ? 'descending' : 'ascending';
      heads.forEach(function(o){ o.setAttribute('aria-sort','none'); });
      th.setAttribute('aria-sort', dir);
      sortBy(th.getAttribute('data-k'), dir);
    });
  });
  apply();
})();
"""


def build():
    ind, _meta = load()
    recs = []
    for grp in GROUP_ORDER:
        recs += [r for r in ind.values() if r["group"] == grp]

    # the resource tray, so the hub sits in the same cluster as the
    # other six rather than off on its own
    b = ['<div class="hubdiscs"><a class="hubdisc" href="library.html"><span aria-hidden="true" class="hd-disc"><i class="hd-mouth"></i></span><span class="hd-nm">Blogs</span></a><a class="hubdisc" href="resources.html"><span aria-hidden="true" class="hd-disc"><i class="hd-mouth"></i></span><span class="hd-nm">Resource library</span></a><a class="hubdisc" href="tools.html"><span aria-hidden="true" class="hd-disc"><i class="hd-mouth"></i></span><span class="hd-nm">Tools</span></a><a class="hubdisc" href="glossary.html"><span aria-hidden="true" class="hd-disc"><i class="hd-mouth"></i></span><span class="hd-nm">Glossary</span></a><a class="hubdisc" href="faq.html"><span aria-hidden="true" class="hd-disc"><i class="hd-mouth"></i></span><span class="hd-nm">FAQs</span></a><a class="hubdisc" href="market-data.html"><span aria-hidden="true" class="hd-disc"><i class="hd-mouth"></i></span><span class="hd-nm">Market data</span></a><a class="hubdisc on" aria-current="page" href="what-business-should-i-start.html"><span aria-hidden="true" class="hd-disc"><i class="hd-mouth"></i></span><span class="hd-nm">What to start</span></a></div>', '<div class="gh">']
    n_costed = sum(1 for r in recs if r["startup_cost_low_usd"] is not None)
    n_up = sum(1 for r in recs if r["demand_direction"] == "up")

    b.append('<div class="intro">'
             '<p>Twenty businesses people actually search for, with what it costs to '
             'start, what the margin looks like, whether demand is growing and the '
             'thing that ends most of them. Every figure is cited to where it came '
             'from.</p>'
             '<p>Two things worth knowing before you read the table. Only %d of the %d '
             'have a startup cost figure from a primary source, because no government '
             'or peer-reviewed body publishes startup costs by business type and the '
             'numbers that circulate come from vendor marketing. And %d of the %d have '
             'growing demand, which means the other %d do not, so a shrinking market '
             'is on this page next to a growing one rather than left off it.</p>'
             '</div>' % (n_costed, len(recs), n_up, len(recs), len(recs) - n_up))

    # ---- controls
    b.append('<div class="ctrls">'
             '<label for="ghq">Find</label>'
             '<input type="search" id="ghq" placeholder="cleaning, food, licence, '
             'margin" autocomplete="off">'
             '<label for="ghg">Kind</label><select id="ghg"><option value="">All</option>'
             + "".join('<option value="%s">%s</option>' % (e(g), e(g))
                       for g in GROUP_ORDER)
             + '</select></div>')
    b.append('<p class="count" id="ghcount" role="status">%d businesses</p>' % len(recs))

    # ---- the table
    cols = [("name", "Business", ""), ("cost", "Startup cost", ""),
            ("demand", "Demand", ""), ("lic", "Licences", ""),
            ("hp", "What ends most of them", "hp")]
    b.append('<div class="tblwrap" tabindex="0" role="region" '
             'aria-label="All twenty businesses compared">'
             '<table id="ghtable"><thead><tr>')
    for k, label, cls in cols:
        b.append('<th data-k="%s" aria-sort="none"%s>'
                 '<button type="button">%s</button></th>'
                 % (e(k), (' class="%s"' % cls) if cls else "", e(label)))
    b.append('</tr></thead><tbody id="ghbody">')

    for r in recs:
        lo = r["startup_cost_low_usd"]
        cost = cost_text(r)
        art = article(r["name"])
        find = " ".join([r["name"], r["group"], r["slug"].replace("-", " "),
                         DEMAND_LABEL[r["demand_direction"]],
                         r["hardest_part"][:200], r["margin_note"][:120]]).lower()
        b.append('<tr data-group="%s" data-name="%s" data-cost="%s" '
                 'data-demand="%s" data-lic="%d" data-hp="%s" data-find="%s">'
                 % (e(r["group"]), e(r["name"]),
                    (lo if lo is not None else ""),
                    {"up": 3, "flat": 2, "unclear": 1, "down": 0}[r["demand_direction"]],
                    len(r["licences"]), e(r["hardest_part"][:60]), e(find)))
        b.append('<td class="nm"><a href="%s">How to start %s %s</a>'
                 '<small>%s</small></td>'
                 % (e(r["file"]), art, e(r["name"]), e(r["group"])))
        b.append('<td>%s</td>' % (e(cost) if lo is not None
                                  else '<span class="np">Not published</span>'))
        b.append('<td><span class="dem"><span class="dot d-%s"></span>%s</span></td>'
                 % (e(r["demand_direction"]),
                    e(DEMAND_LABEL[r["demand_direction"]])))
        b.append('<td>%d</td>' % len(r["licences"]))
        b.append('<td class="hp">%s</td>' % e(short(r["hardest_part"], 110)))
        b.append("</tr>")
    b.append('</tbody></table></div>')
    b.append('<p class="none" id="ghnone" hidden>Nothing matches that. '
             'Clearing the search brings all twenty back.</p>')
    return b, recs, n_costed, n_up


def main():
    b, recs, n_costed, n_up = build()
    url = "%s/what-business-should-i-start.html" % SITE

    # ---- what the table is actually showing, said plainly
    b.append("<h2>What the table shows</h2>")
    cheap = sorted([r for r in recs if r["startup_cost_low_usd"] is not None],
                   key=lambda r: r["startup_cost_low_usd"])
    b.append("<p>The businesses with the lowest published startup costs are %s. "
             "They are cheap to start because the equipment is cheap, and the same "
             "fact means somebody else can start one next week, which is why the "
             "hardest part listed for each of them is competition or staffing "
             "rather than capital.</p>"
             % ", ".join("<a href=\"%s\">%s</a>" % (e(r["file"]), e(r["name"]))
                         for r in cheap[:3]))
    b.append("<p>Demand is not uniformly up. %d of the %d are growing on primary "
             "projections, and the rest are flat, shrinking, or have no established "
             "figure. A shrinking market is not the same as a bad business, since a "
             "smaller field has fewer people entering it, but it does change what the "
             "plan has to survive.</p>" % (n_up, len(recs)))
    b.append("<p>Only %d of the %d carry a startup cost figure at all. That is not an "
             "omission. No US government or peer-reviewed source publishes typical "
             "startup costs by business type, the SBA's own guide gives cost "
             "categories and no dollar figures, and the per-industry numbers in wide "
             "circulation trace to vendor marketing or paywalled market research. "
             "Where a primary figure exists it is quoted, and where one does not the "
             "cell says so.</p>" % (n_costed, len(recs)))

    b.append("<h2>Where the numbers came from</h2>")
    b.append('<ul>'
             '<li>Startup costs, where published: US Department of Energy for EV '
             'charging, SBDCNet and trade bodies for the service businesses</li>'
             '<li>Margins: IRS Statistics of Income, Nonfarm Sole Proprietorship '
             'Returns, Tax Year 2022, Table 1. These include the owner\'s own pay, '
             'because a sole proprietor deducts no salary, so they are not comparable '
             'to a corporate net margin</li>'
             '<li>Demand: Bureau of Labor Statistics employment projections, 2025 to '
             '2035, for the closest occupation, plus EIA for EV adoption</li>'
             '<li>Market size: Census Bureau Economic Census and Service Annual '
             'Survey, and BLS</li>'
             '<li>Licensing: state agencies, federal regulators and the SBA</li>'
             '</ul>')
    b.append('<p>Each page carries its own source links next to each claim, and flags '
             'the widely repeated statistics that have no primary study behind them, '
             'of which there are more in this subject than in most.</p>')

    b.append("<h2>If the question is still open</h2><ul>"
             '<li><a href="business-idea-where-to-start.html">You have an idea and do '
             'not know the first move</a></li>'
             '<li><a href="assessment.html">Which way you actually work</a>, since '
             'choosing between these is partly a question about you</li>'
             '<li><a href="startup-cost-calculator.html">What your version would '
             'cost</a>, rather than the category</li>'
             '<li><a href="state-filing.html">What your state wants filed</a>, '
             'whichever of the twenty it is</li>'
             '<li><a href="market-data.html">How many businesses start and last</a>, '
             'measured rather than asserted</li></ul>')

    b.append('<div class="cite"><b>Cite this page</b><p>SideKix, &ldquo;What business '
             'should I start? Twenty compared on cost, margin and demand&rdquo;. '
             '%s</p></div>' % e(url))
    b.append("</div>")

    schema = [
        {"@context": "https://schema.org", "@type": "ItemList",
         "name": "Twenty businesses compared on startup cost, margin and demand",
         "url": url, "numberOfItems": len(recs),
         "itemListElement": [
             {"@type": "ListItem", "position": i + 1,
              "name": "How to start %s %s" % (article(r["name"]), r["name"]),
              "url": "%s/%s" % (SITE, r["file"])}
             for i, r in enumerate(recs)]},
        {"@context": "https://schema.org", "@type": "FAQPage", "url": url,
         "mainEntity": [
             {"@type": "Question",
              "name": "What business should I start?",
              "acceptedAnswer": {"@type": "Answer", "text":
                  "It depends on what you can fund, how much regulation you are "
                  "willing to carry and whether you want a growing or a quiet market. "
                  "This page compares twenty on startup cost, profit margin, demand "
                  "direction and the number of licences to expect, so the trade is "
                  "visible rather than argued."}},
             {"@type": "Question",
              "name": "What is the cheapest business to start?",
              "acceptedAnswer": {"@type": "Answer", "text":
                  "Of the businesses here with a startup cost figure from a primary "
                  "source, %s has the lowest published range at %s. Low startup cost "
                  "and low barriers to entry are the same fact, so these compete on "
                  "price and on staffing rather than on capital."
                  % (cheap[0]["name"], cost_text(cheap[0]))}},
             {"@type": "Question",
              "name": "Which small businesses are growing?",
              "acceptedAnswer": {"@type": "Answer", "text":
                  "%d of the %d have growing demand on Bureau of Labor Statistics "
                  "projections for 2025 to 2035 or equivalent primary figures. The "
                  "remainder are flat, shrinking or have no established figure, and "
                  "are shown as such rather than left out."
                  % (n_up, len(recs))}},
         ]},
        {"@context": "https://schema.org", "@type": "BreadcrumbList",
         "itemListElement": [
             {"@type": "ListItem", "position": 1, "name": "SideKix", "item": SITE},
             {"@type": "ListItem", "position": 2,
              "name": "What business should I start", "item": url}]},
    ]

    back = ('<p class="kx-backrow"><a class="kx-bk" href="library.html">'
            '<svg aria-hidden="true" focusable="false" viewbox="0 0 24 24">'
            '<path d="M15 5l-7 7 7 7"></path></svg> Resources</a></p>')

    n = page("what-business-should-i-start.html",
             "What Business Should I Start? 20 Compared on Cost and Demand | SideKix",
             "Twenty businesses compared on startup cost, profit margin, demand "
             "direction and licences to expect. Every figure cited to a primary "
             "source, and the ones nobody publishes are marked as such.",
             "Starting a business",
             "What business <em>should I start?</em>",
             "Twenty of them, compared on what they cost, what they earn, whether "
             "demand is growing and what ends most of them.",
             "".join(b), css=CSS, js=JS, schema=schema, wrapcls="wrap res", back=back)
    print("hub: %d KB, %d rows, %d costed, %d growing"
          % (n // 1024, len(recs), n_costed, n_up))


if __name__ == "__main__":
    main()
