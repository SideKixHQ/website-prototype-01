# -*- coding: utf-8 -*-
"""Bring every blog article into line with the rest of the site.

Articles run on the light article template and had drifted from the main site
in three ways:

  1. The top bar was a stripped one of their own, a wordmark and a Build the
     Future button, which no longer exists. They now carry the same #kx-nav as
     every other page, which means they also load assets/site.css for it. The
     bar is position:fixed, and article.css holds the content clear of it.

  2. The footer was a reduced copy: it had lost Press, The Back Room, Cookie
     Policy and Purchase Policy, and pointed Resources at resources.html rather
     than library.html. It is now the homepage footer, with the links rewritten
     for a page two directories down.

  3. Nothing checked the breadcrumb data, so a post built by copying another
     could inherit that post's name and URL and hand search engines the wrong
     identity for the page. The last breadcrumb is now derived from the file's
     own canonical.

Safe to run repeatedly: anything already correct is left alone.
"""
import glob, io, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

NAV = """<nav aria-label="Main" id="kx-nav">
<a aria-label="SideKix home" href="../../index.html"><img alt="SideKix" decoding="async" fetchpriority="high" height="602" loading="eager" src="../../assets/img/2321feb76252.png?v=2" width="2164"/></a>
<button aria-expanded="false" aria-label="Menu" class="kx-burger" type="button"><i aria-hidden="true"></i><span>Menu</span></button>
<div class="kx-links"><a href="../../index.html">Home</a><a href="../../how-it-works.html">How it works</a><a href="../../membership.html">Membership</a><a href="../../advisors.html">Advisors</a><a href="../../partners.html">Partners</a><a href="../../events.html">Events</a><span aria-current="page">Resources</span></div>
</nav>"""

SITECSS = '<link href="../../assets/site.css" rel="stylesheet"/>'


def footer_for_articles():
    """The homepage footer, with its relative links pointed two levels up."""
    home = io.open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
    f = re.search(r"<footer[\s\S]*?</footer>", home).group(0)
    return re.sub(r'(href|src)="(?!https?:|mailto:|#|\.\./)([^"]+)"',
                  lambda m: '%s="../../%s"' % (m.group(1), m.group(2)), f)


def nav_script():
    """The bar's open/close behaviour, taken from a page that already has it."""
    src = io.open(os.path.join(ROOT, "library.html"), encoding="utf-8").read()
    m = re.search(r'<script id="kx-nav-toggle">[\s\S]*?</script>', src)
    return m.group(0) if m else ""


def fix_breadcrumb(s, url, title):
    """Point the last breadcrumb at this page rather than whatever it was copied from."""
    def one(m):
        try:
            o = json.loads(m.group(1))
        except ValueError:
            return m.group(0)
        for node in (o.get("@graph") or [o]):
            if node.get("@type") == "BreadcrumbList":
                last = node["itemListElement"][-1]
                if last.get("item") == url and last.get("name") == title:
                    return m.group(0)
                last["item"], last["name"] = url, title
                return '<script type="application/ld+json">%s</script>' % json.dumps(o, ensure_ascii=False)
        return m.group(0)
    return re.sub(r'<script type="application/ld\+json">([\s\S]*?)</script>', one, s)


def main():
    footer = footer_for_articles()
    toggle = nav_script()
    changed = clean = 0
    for p in sorted(glob.glob(os.path.join(ROOT, "blog", "*", "index.html"))):
        s = orig = io.open(p, encoding="utf-8").read()
        slug = os.path.basename(os.path.dirname(p))
        url = "https://sidekixhq.com/blog/%s/" % slug
        tm = re.search(r"<h1[^>]*>([\s\S]*?)</h1>", s)
        title = re.sub(r"<[^>]+>", "", tm.group(1)).strip() if tm else slug

        # the bar: replace the old one, or an earlier interim version of this fix
        s = re.sub(r"<header class=\"abar\">[\s\S]*?</header>", NAV, s, count=1)
        if 'id="kx-nav"' not in s:
            print("   ! no top bar found in %s" % slug)
            continue

        if SITECSS not in s:
            s = s.replace('<link href="../../assets/article.css" rel="stylesheet"/>',
                          SITECSS + '\n<link href="../../assets/article.css" rel="stylesheet"/>', 1)

        s = re.sub(r"<footer[\s\S]*?</footer>", lambda _m: footer, s, count=1)

        if toggle and 'id="kx-nav-toggle"' not in s:
            s = s.replace("</body>", toggle + "\n</body>", 1)

        s = fix_breadcrumb(s, url, title)

        if s != orig:
            io.open(p, "w", encoding="utf-8").write(s)
            changed += 1
        else:
            clean += 1
    print("articles: %d updated, %d already correct" % (changed, clean))


if __name__ == "__main__":
    main()
