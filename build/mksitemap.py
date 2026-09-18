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

# Glossary term pages are ~90 words each and the definition repeats three times
# on the page, so Google reads the set as doorway content: 59 pages, 0
# impressions in the first quarter. They stay live and linked for readers, and
# vercel.json serves them X-Robots-Tag: noindex, follow. Listing them in the
# sitemap while asking Google not to index them is a contradiction, so they are
# dropped here too. Delete this pattern if the pages are ever written out
# properly.
SKIP_PATTERNS = (re.compile(r"^what-is-[a-z0-9-]+\.html$"),)

# Two pages that are live but deliberately unlinked and unfinished: the
# Homegrown offering has not settled on a name, and the jobs map goes with it.
# A page that nothing links to but the sitemap advertises is exactly what
# produces "Discovered, currently not indexed", so they stay out until they
# ship under their real name.
SKIP_UNSHIPPED = {"homegrown.html", "where-the-jobs-are.html"}

PRIORITY = {
 "": "1.0", "index.html": "1.0",
 "how-it-works.html": "0.9", "membership.html": "0.9", "join.html": "0.9",
 "tools.html": "0.9", "library.html": "0.9", "assessment.html": "0.9",
 "market-data.html": "0.9", "state-filing.html": "0.9",
 "business-idea-where-to-start.html": "0.9",
 "what-business-should-i-start.html": "0.9",
 "discoveries.html": "0.9",
 "homegrown.html": "0.9",
 "start-a-business-in-north-carolina.html": "0.9",
 "terms.html": "0.3", "privacy.html": "0.3", "cookies.html": "0.3",
}
FREQ = {"index.html": "weekly", "events.html": "weekly", "press.html": "weekly",
        "library.html": "weekly", "market-data.html": "monthly"}

# The twenty industry guides rank on their own and are not leaf content, so
# they sit above the 0.7 default rather than in it.
GUIDE_PRIORITY = "0.8"


def main():
    path = os.path.join(ROOT, "sitemap.xml")
    sm = io.open(path, encoding="utf-8").read()
    have = dict(re.findall(r"<url>\s*<loc>([^<]+)</loc>(.*?)</url>", sm, re.S))

    on_disk = []
    for p in sorted(glob.glob(os.path.join(ROOT, "*.html"))):
        f = os.path.basename(p)
        if f in SKIP or f in SKIP_UNSHIPPED or any(rx.match(f) for rx in SKIP_PATTERNS):
            continue
        # Read the whole file, not the first 8KB: the shell inlines about 110KB
        # of CSS before the meta tags, so the robots tag sits near byte 72,000
        # and an 8KB probe never reached it.
        if re.search(r'<meta content="noindex', io.open(p, encoding="utf-8").read()):
            continue
        on_disk.append(("" if f == "index.html" else f, p))
    for p in sorted(glob.glob(os.path.join(ROOT, "blog", "*", "index.html"))):
        on_disk.append(("blog/%s/" % os.path.basename(os.path.dirname(p)), p))
    # the quizzes live one folder deep so the URL is short enough to type off a
    # screenshot, which means the flat *.html glob above never sees them
    for p in sorted(glob.glob(os.path.join(ROOT, "q", "*", "index.html"))):
        on_disk.append(("q/%s/" % os.path.basename(os.path.dirname(p)), p))

    urls = []
    for slug, p in on_disk:
        url = SITE + "/" + slug
        mod = datetime.date.fromtimestamp(os.path.getmtime(p)).isoformat()
        key = os.path.basename(slug) or "index.html"
        urls.append((url, mod, FREQ.get(key, "monthly"),
                     PRIORITY.get(key,
                         "0.8" if slug.startswith("q/")
                         else GUIDE_PRIORITY if key.startswith("how-to-start-")
                         else "0.6" if slug.startswith("blog/") else "0.7")))

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
