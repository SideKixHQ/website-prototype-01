#!/usr/bin/env python3
"""Rebuild 404.html.

The old page linked relatively, so a 404 served at /advisors/ resolved every
link against /advisors/ and offered nothing but more dead ends. Every link
here is root-relative, and the page tries to work out what the visitor was
actually after before falling back to a directory.
"""
import json, os, re, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FONT = ("'Poppins',system-ui,-apple-system,sans-serif")

# What a lost visitor is most likely to want, in the order they'd want it.
DIRECTORY = [
    ("Start here", [
        ("/", "Home"),
        ("/how-it-works.html", "How it works"),
        ("/membership.html", "Membership"),
        ("/join.html", "Early access"),
    ]),
    ("Do something", [
        ("/tools.html", "Tools and calculators"),
        ("/assessment.html", "Energy Discovery"),
        ("/library.html", "Library"),
        ("/glossary.html", "Glossary"),
    ]),
    ("Look things up", [
        ("/market-data.html", "Market data"),
        ("/state-filing.html", "State filing guide"),
        ("/faq.html", "FAQ"),
        ("/resources.html", "Resources"),
    ]),
    ("The rest of it", [
        ("/advisors.html", "Advisors"),
        ("/partners.html", "Partners"),
        ("/events.html", "Events"),
        ("/press.html", "Press"),
        ("/back-room.html", "The Back Room"),
        ("/become-an-advisor.html", "Become an advisor"),
    ]),
]


def slugs():
    """Every real destination, for the did-you-mean matcher."""
    out = []
    for p in sorted(glob.glob(os.path.join(ROOT, "*.html"))):
        name = os.path.basename(p)[:-5]
        if name in ("404",):
            continue
        out.append(["/" if name == "index" else "/%s.html" % name,
                    "Home" if name == "index" else name.replace("-", " ")])
    for p in sorted(glob.glob(os.path.join(ROOT, "blog", "*", "index.html"))):
        slug = os.path.basename(os.path.dirname(p))
        out.append(["/blog/%s/" % slug, slug.replace("-", " ")])
    return out


CSS = """
 *{box-sizing:border-box}
 body{margin:0;min-height:100vh;display:flex;flex-direction:column;background:#060502;
  color:#F4EACF;font-family:%(font)s;text-align:center}
 main.w{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;
  padding:48px 22px 56px;max-width:820px;margin:0 auto;width:100%%}
 .nfbar{display:flex;align-items:center;justify-content:space-between;gap:18px;
  padding:16px clamp(18px,4vw,48px);border-bottom:1px solid rgba(212,168,86,.16);
  background:rgba(5,5,5,.82)}
 .nfbar img{height:26px;width:auto;display:block}
 .nfbar .nfcta{display:inline-flex;align-items:center;min-height:44px;padding:0 22px;border-radius:999px;
  text-decoration:none;border:1px solid rgba(212,168,86,.5);background:rgba(212,168,86,.06);
  color:#F3E4A8;font-weight:600;font-size:14px;white-space:nowrap}
 .nfbar .nfcta:hover{background:rgba(212,168,86,.14);border-color:#D4A856}
 .nffoot{border-top:1px solid rgba(212,168,86,.16);padding:26px clamp(18px,4vw,48px) 34px}
 .nffoot p{font-family:Georgia,serif;font-style:italic;color:#A1853E;font-size:14px;margin:0 0 14px}
 .nffoot nav{display:flex;flex-wrap:wrap;gap:6px 4px;justify-content:center}
 .nffoot nav a{color:#BDB49F;font-weight:500;font-size:13.5px;padding:0 11px;
  min-height:44px;text-decoration:none;display:inline-flex;align-items:center}
 .nffoot nav a:hover{color:#F3E4A8;text-decoration:underline;text-underline-offset:4px}
 h1{font-family:Georgia,serif;font-weight:600;font-size:clamp(30px,6vw,48px);color:#FFF8D8;
  margin:0 0 14px;line-height:1.1}
 h1 em{font-style:italic;color:#D4A856}
 .lede{color:#BDB49F;font-size:16px;line-height:1.7;margin:0 0 30px;max-width:30em}
 main a.go{display:inline-flex;align-items:center;min-height:48px;padding:0 28px;border-radius:999px;
  text-decoration:none;background:linear-gradient(180deg,#D7C582,#A1853E);color:#1B1400;font-weight:700}

 /* did-you-mean */
 #nf-guess{margin:0 0 34px;width:100%%;max-width:560px}
 #nf-guess[hidden]{display:none}
 .nf-gl{display:block;font-size:11.5px;letter-spacing:.16em;text-transform:uppercase;
  color:#BDB4A4;margin:0 0 12px}
 #nf-guess ul{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:8px}
 #nf-guess a{display:flex;align-items:center;justify-content:center;gap:10px;min-height:52px;
  padding:8px 20px;border-radius:12px;text-decoration:none;font-weight:600;font-size:15px;
  color:#F3E4A8;border:1px solid rgba(212,168,86,.34);background:rgba(212,168,86,.07)}
 #nf-guess a:hover{background:rgba(212,168,86,.15);border-color:#D4A856}

 /* directory */
 .nf-dir{width:100%%;margin:40px 0 0;text-align:left;
  display:grid;grid-template-columns:repeat(4,1fr);gap:26px 30px}
 .nf-dir h2{font-size:11.5px;letter-spacing:.16em;text-transform:uppercase;color:#BDB4A4;
  font-weight:600;margin:0 0 8px;padding:0 0 8px;border-bottom:1px solid rgba(212,168,86,.18)}
 .nf-dir ul{list-style:none;margin:0;padding:0}
 .nf-dir a{display:flex;align-items:center;min-height:40px;color:#D9D0BC;font-size:14.5px;
  text-decoration:none;line-height:1.35}
 .nf-dir a:hover{color:#F3E4A8;text-decoration:underline;text-underline-offset:4px}
 .tm{margin:40px 0 0;color:#877F6F;font-size:10px;letter-spacing:.08em;line-height:1.6}
 a:focus-visible{outline:3px solid #F3E4A8;outline-offset:3px}
 @media(max-width:860px){.nf-dir{grid-template-columns:repeat(2,1fr)}}
 @media(max-width:460px){.nf-dir{grid-template-columns:1fr;gap:22px}}
""" % {"font": FONT}

JS = """
(function(){
  var data = JSON.parse(document.getElementById('nf-slugs').textContent);
  var raw = decodeURIComponent(location.pathname || '')
              .toLowerCase()
              .replace(/\\.html?$/,'')
              .replace(/^\\/+|\\/+$/g,'');
  if(!raw) return;
  var asked = raw.split('/').pop();
  if(!asked) return;
  var words = asked.split(/[^a-z0-9]+/).filter(function(w){ return w.length > 2; });

  /* a few words people type that are not any page's slug */
  var HINT = {comic:'/back-room.html', comics:'/back-room.html', game:'/back-room.html',
              play:'/back-room.html', declaration:'/back-room.html',
              pricing:'/membership.html', price:'/membership.html', plans:'/membership.html',
              contact:'/faq.html', support:'/faq.html', help:'/faq.html',
              about:'/how-it-works.html', team:'/how-it-works.html',
              news:'/press.html', media:'/press.html', quiz:'/assessment.html',
              blog:'/library.html', articles:'/library.html', calculator:'/tools.html'};

  function flat(t){ return t.toLowerCase().replace(/[^a-z0-9]/g,''); }

  /* edit distance, capped: only worth computing for near misses */
  function near(a,b){
    if(Math.abs(a.length-b.length) > 3) return 99;
    var prev=[], cur=[], i, j;
    for(j=0;j<=b.length;j++) prev[j]=j;
    for(i=1;i<=a.length;i++){
      cur[0]=i;
      for(j=1;j<=b.length;j++){
        cur[j]=Math.min(prev[j]+1, cur[j-1]+1,
                        prev[j-1] + (a.charAt(i-1)===b.charAt(j-1)?0:1));
      }
      prev=cur.slice();
    }
    return prev[b.length];
  }

  var askedFlat = flat(asked);

  function score(entry){
    var path = entry[0], label = entry[1];
    var slug = path.toLowerCase().replace(/\\.html?$/,'').replace(/^\\/+|\\/+$/g,'').split('/').pop();
    if(!slug) return 0;
    if(slug === asked) return 1000;
    var s = 0, sf = flat(slug);
    if(sf === askedFlat) s += 200;                        /* marketdata = market-data */
    else if(sf.indexOf(askedFlat) > -1 || askedFlat.indexOf(sf) > -1) s += 40;
    if(s === 0 && askedFlat.length > 3){
      var d = near(askedFlat, sf);                        /* advisorz = advisors */
      if(d <= 2) s += 60 - d * 10;
    }
    if(HINT[asked] === path) s += 120;
    var hay = flat(slug + label);
    for(var i=0;i<words.length;i++){ if(hay.indexOf(flat(words[i])) > -1) s += 12; }
    return s;
  }

  var hits = data.map(function(e){ return {e:e, s:score(e)}; })
                 .filter(function(h){ return h.s >= 24; })
                 .sort(function(a,b){ return b.s - a.s; })
                 .slice(0,3);
  if(!hits.length) return;

  var box = document.getElementById('nf-guess');
  var ul  = box.querySelector('ul');
  hits.forEach(function(h){
    var li = document.createElement('li');
    var a  = document.createElement('a');
    a.href = h.e[0];
    a.textContent = h.e[1].replace(/\\b\\w/g, function(c){ return c.toUpperCase(); });
    li.appendChild(a); ul.appendChild(li);
  });
  box.hidden = false;
})();
"""


def build():
    dirhtml = []
    for heading, links in DIRECTORY:
        items = "".join('<li><a href="%s">%s</a></li>' % (h, t) for h, t in links)
        dirhtml.append("<section><h2>%s</h2><ul>%s</ul></section>" % (heading, items))

    foot = [("/", "Home"), ("/how-it-works.html", "How it works"),
            ("/membership.html", "Membership"), ("/library.html", "Library"),
            ("/glossary.html", "Glossary"), ("/tools.html", "Calculators"),
            ("/faq.html", "FAQ"), ("/press.html", "Press"),
            ("/join.html", "Early access")]

    html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta content="width=device-width,initial-scale=1" name="viewport"/>
<title>Page not found | SideKix</title>
<meta content="noindex" name="robots"/>
<link href="/favicon.ico" rel="icon"/>
<style>%(css)s</style>
</head>
<body>
<a class="skip-link" href="#main" style="position:absolute;left:-9999px;top:0;background:#D4A856;color:#1B1400;padding:12px 18px;border-radius:0 0 8px 0;font-weight:700;z-index:99">Skip to content</a>
<style>.skip-link:focus{left:0}</style>
<header class="nfbar">
<a aria-label="SideKix home" href="/"><img alt="SideKix" decoding="async" fetchpriority="high" height="602" loading="eager" src="/assets/sidekix-wordmark.png" width="2164"/></a>
<a class="nfcta" href="/membership.html">Build the Future</a>
</header>
<main class="w" id="main">
<h1>That page took a <em>different path</em>.</h1>
<p class="lede">The page you were looking for is not here. Everything else still is.</p>
<div hidden id="nf-guess"><span class="nf-gl">You may have been looking for</span><ul></ul></div>
<a class="go" href="/">Back to the start</a>
<nav aria-label="Site directory" class="nf-dir">%(dir)s</nav>
<p class="tm">SideKix&trade; is a trademark of Character Limit LLC. U.S. federal trademark application pending.</p>
</main>
<footer class="nffoot">
<p>Talent is everywhere. Opportunity is for all.</p>
<nav aria-label="Site">%(foot)s</nav>
</footer>
<script id="nf-slugs" type="application/json">%(slugs)s</script>
<script>
try{%(js)s}catch(err){console.error('SideKix [404] failed:',err);}
</script>
</body>
</html>
""" % {
        "css": CSS,
        "dir": "".join(dirhtml),
        "foot": "".join('<a href="%s">%s</a>' % (h, t) for h, t in foot),
        "slugs": json.dumps(slugs(), separators=(",", ":")),
        "js": JS,
    }
    open(os.path.join(ROOT, "404.html"), "w").write(html)
    print("404.html %d KB, %d destinations" % (len(html) // 1024, len(slugs())))


if __name__ == "__main__":
    build()
