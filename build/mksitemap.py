# -*- coding: utf-8 -*-
"""Keep sitemap.xml in step with what is actually on disk.

Adds any page that exists but is missing from the sitemap, drops any entry
pointing at a file that no longer exists, and refreshes lastmod from the file's
own modification time. Pages that should never be listed are named below.
"""
import io, os, re, glob, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://sidekixhq.com"

# noindex or not a destination
SKIP = {"404.html"}

PRIORITY = {
 "": "1.0", "index.html": "1.0",
 "how-it-works.html": "0.9", "membership.html": "0.9", "join.html": "0.9",
 "tools.html": "0.9", "library.html": "0.9", "assessment.html": "0.9",
 "market-data.html": "0.9", "state-filing.html": "0.9",
 "business-idea-where-to-start.html": "0.9",
 "start-a-business-in-north-carolina.html": "0.9",
 "terms.html": "0.3", "privacy.html": "0.3", "cookies.html": "0.3",
}
FREQ = {"index.html": "weekly", "events.html": "weekly", "press.html": "weekly",
        "library.html": "weekly", "market-data.html": "monthly"}


def main():
    path = os.path.join(ROOT, "sitemap.xml")
    sm = io.open(path, encoding="utf-8").read()
    have = dict(re.findall(r"<url>\s*<loc>([^<]+)</loc>(.*?)</url>", sm, re.S))

    on_disk = []
    for p in sorted(glob.glob(os.path.join(ROOT, "*.html"))):
        f = os.path.basename(p)
        if f in SKIP:
            continue
        if re.search(r'<meta content="noindex"', io.open(p, encoding="utf-8").read(8000)):
            continue
        on_disk.append(("" if f == "index.html" else f, p))
    for p in sorted(glob.glob(os.path.join(ROOT, "blog", "*", "index.html"))):
        on_disk.append(("blog/%s/" % os.path.basename(os.path.dirname(p)), p))

    urls = []
    for slug, p in on_disk:
        url = SITE + "/" + slug
        mod = datetime.date.fromtimestamp(os.path.getmtime(p)).isoformat()
        key = os.path.basename(slug) or "index.html"
        urls.append((url, mod, FREQ.get(key, "monthly"),
                     PRIORITY.get(key, "0.6" if slug.startswith("blog/") else "0.7")))

    live = {u for u, _, _, _ in urls}
    dropped = [u for u in have if u not in live]
    added = [u for u, _, _, _ in urls if u not in have]

    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for url, mod, freq, pri in urls:
        out.append("  <url>\n    <loc>%s</loc>\n    <lastmod>%s</lastmod>\n"
                   "    <changefreq>%s</changefreq>\n    <priority>%s</priority>\n  </url>"
                   % (url, mod, freq, pri))
    out.append("</urlset>\n")
    io.open(path, "w", encoding="utf-8").write("\n".join(out))

    print("sitemap: %d urls (%d added, %d dropped)" % (len(urls), len(added), len(dropped)))
    for u in added:
        print("   + " + u)
    for u in dropped:
        print("   - " + u)


if __name__ == "__main__":
    main()
