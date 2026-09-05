"""
Build the SideKix tool pages.

The shell is cloned from the live tools.html rather than from build/_shell_top.html,
because that older shell predates the nav reorder and the Library to Resources
rename: it has no site-wide.css link, no robots meta, and a tray that still points
Resources at resources.html. Cloning the live page means a generated tool inherits
whatever the site currently is, including anything fixed after this was written.

Only one block is dropped from the donor: the calculator script. Everything else in
that file is shared chrome and shared theme.
"""
import io, re, json, os, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://sidekixhq.com"
DONOR = os.path.join(ROOT, "tools.html")

def e(s): return html.escape(str(s), quote=True)

_src = io.open(DONOR, encoding="utf-8").read()

# ---- split the donor -------------------------------------------------------
_head_end = _src.index("</head>")
HEAD = _src[:_head_end]                       # doctype, meta, every style block
_main_i = _src.index('<main id="maincontent">')
CHROME = _src[_head_end + len("</head>"):_main_i]   # body open, nav, overlays
TAIL = _src[_src.index("</main>") + len("</main>"):]  # footer and scripts

# Nothing is stripped from the tail. The obvious move was to drop the
# calculator script, but that script shares one block with the nav toggle, the
# orb tray, the cursor and the desaturation layer, so removing it takes the
# chrome with it. It guards on the elements it needs and does nothing when they
# are absent, which is exactly how the membership code in the same block already
# behaves on tools.html. Inert code beats broken navigation.

BACK = ('<p class="kx-backrow"><a class="kx-bk" href="tools.html">'
        '<svg aria-hidden="true" focusable="false" viewbox="0 0 24 24">'
        '<path d="M15 5l-7 7 7 7"></path></svg> Back to Tools</a></p>')


FAQ_CSS = """
/* Google asks that FAQPage markup describe content a visitor can actually
   read on the page. These pages carried the schema and nothing visible, so
   the questions are rendered from the same list the schema is built from and
   the two cannot drift apart. */
.tfaq{max-width:1120px;margin:56px auto 0;padding-top:34px;
  border-top:1px solid rgba(212,168,86,.16)}
.tfaq > h2{font-family:var(--util);font-size:11px;letter-spacing:.2em;text-transform:uppercase;
  color:var(--gold);margin:0 0 14px;font-weight:400}
.tfaq details{border-top:1px solid rgba(212,168,86,.14)}
.tfaq details:last-of-type{border-bottom:1px solid rgba(212,168,86,.14)}
.tfaq summary{list-style:none;cursor:pointer;padding:19px 40px 19px 0;position:relative;
  font-size:16.5px;color:#EFE7D4}
.tfaq summary::-webkit-details-marker{display:none}
.tfaq summary::after{content:"";position:absolute;right:6px;top:50%;width:8px;height:8px;
  border-right:1.5px solid var(--gold);border-bottom:1.5px solid var(--gold);
  transform:translateY(-70%) rotate(45deg);transition:transform .25s}
.tfaq details[open] summary::after{transform:translateY(-30%) rotate(-135deg)}
.tfaq summary:focus-visible{outline:2px solid var(--gold);outline-offset:2px;border-radius:4px}
.tfaq details > div{padding:0 40px 22px 0}
.tfaq details p{margin:0;font-size:15.5px;line-height:1.75;color:#A8A296}
"""

def faqhtml(pairs):
    """Render the same question list the FAQPage schema is built from."""
    if not pairs: return ""
    rows = "".join('<details><summary>%s</summary><div><p>%s</p></div></details>'
                   % (e(q), e(a)) for q, a in pairs)
    return '<section class="tfaq"><h2>Questions people ask</h2>%s</section>' % rows

def page(filename, title, desc, eyebrow, h1, lede, body,
         css="", js="", schema=(), wrapcls="wrap res calcs", back=BACK):
    """Return one complete tool page."""
    head = HEAD
    head = re.sub(r"<title>.*?</title>", f"<title>{e(title)}</title>", head, count=1, flags=re.S)
    # every description-bearing meta on the donor carries the same string
    old = re.search(r'<meta content="([^"]*)" name="description"/?>', head).group(1)
    head = head.replace(old, e(desc))
    head = head.replace(f"{SITE}/tools.html", f"{SITE}/{filename}")
    head = re.sub(r'(<meta content=")[^"]*(" property="og:title"/?>)',
                  lambda m: m.group(1) + e(title.split(" | ")[0]) + m.group(2), head, count=1)
    head = re.sub(r'(<meta content=")[^"]*(" name="twitter:title"/?>)',
                  lambda m: m.group(1) + e(title.split(" | ")[0]) + m.group(2), head, count=1)
    # the donor's own structured data describes the calculators page
    head = re.sub(r'<script type="application/ld\+json">.*?</script>', "", head, flags=re.S)
    # the donor also carries whatever page CSS it was built with. tools.html is
    # its own donor, so without this every regeneration stacked another copy of
    # the hub styles on top of the last one and the oldest rules kept winning.
    head = re.sub(r'<style id="kx-(tool|faq)">.*?</style>\s*', "", head, flags=re.S)
    for s in schema:
        head += ('<script type="application/ld+json">'
                 + json.dumps(s, ensure_ascii=False) + "</script>\n")
    if css:
        head += f'<style id="kx-tool">\n{css}\n</style>\n'

    faq_pairs = []
    for sc in schema:
        nodes = sc.get("@graph", [sc]) if isinstance(sc, dict) else []
        for nd in (nodes if isinstance(nodes, list) else [nodes]):
            if isinstance(nd, dict) and nd.get("@type") == "FAQPage":
                for qa in nd.get("mainEntity", []):
                    faq_pairs.append((qa["name"], qa["acceptedAnswer"]["text"]))
    if faq_pairs:
        head += f'<style id="kx-faq">\n{FAQ_CSS}\n</style>\n'
    head += "</head>"

    main = (f'<main id="maincontent">\n<section class="{wrapcls}">\n{back}\n'
            f'<span class="eyebrow">{e(eyebrow)}</span>\n<h1>{h1}</h1>\n'
            f'<p class="lede">{lede}</p>\n{body}\n{faqhtml(faq_pairs)}\n</section>\n</main>')

    tail = TAIL
    if js:
        tail = tail.replace("</body>",
            f"<script>\ntry{{\n(function(){{\n{js}\n}})();\n}}catch(err){{console.error('SideKix [{filename}] failed:',err);}}\n</script>\n</body>", 1)
    out = head + CHROME + main + tail
    io.open(os.path.join(ROOT, filename), "w", encoding="utf-8").write(out)
    return len(out)

def crumbs(name, filename):
    return {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"Home","item":f"{SITE}/"},
        {"@type":"ListItem","position":2,"name":"Resources","item":f"{SITE}/library.html"},
        {"@type":"ListItem","position":3,"name":"Tools","item":f"{SITE}/tools.html"},
        {"@type":"ListItem","position":4,"name":name,"item":f"{SITE}/{filename}"}]}

def webapp(name, filename, desc, features):
    return {"@context":"https://schema.org","@type":"WebApplication","name":name,
        "url":f"{SITE}/{filename}","applicationCategory":"BusinessApplication",
        "operatingSystem":"Any","isAccessibleForFree":True,"description":desc,
        "offers":{"@type":"Offer","price":"0","priceCurrency":"USD"},
        "publisher":{"@id":f"{SITE}/#organization"},"featureList":features}

def faqpage(pairs):
    return {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
        {"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in pairs]}
