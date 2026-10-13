# -*- coding: utf-8 -*-
"""Build feed.xml (RSS 2.0) from the blog posts on disk.

Every blog/<slug>/index.html already carries og:title, a meta description and
article:published_time, so the feed is read straight off those tags. Nothing to
maintain by hand: publish a post, run this, commit feed.xml.

Also makes sure library.html advertises the feed with a <link rel="alternate">
tag, so browsers, readers and tools like Zapier can find it. Set POST_LINKS to
True to add the same tag to every post. Safe to run repeatedly.

    python3 build/mkfeed.py
"""
import glob, html, os, re, datetime
from email.utils import format_datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://sidekixhq.com"
FEED_URL = SITE + "/feed.xml"
POST_LINKS = False
LINK_TAG = ('<link rel="alternate" type="application/rss+xml" '
            'title="SideKix Blog" href="/feed.xml"/>')


def meta(doc, attr, name):
    for pat in (r'<meta[^>]*content="([^"]*)"[^>]*%s="%s"' % (attr, re.escape(name)),
                r'<meta[^>]*%s="%s"[^>]*content="([^"]*)"' % (attr, re.escape(name))):
        m = re.search(pat, doc)
        if m:
            return html.unescape(m.group(1)).strip()
    return ""


def esc(s):
    return html.escape(s, quote=False)


def ensure_link(path):
    with open(path, encoding="utf-8") as f:
        doc = f.read()
    if 'type="application/rss+xml"' in doc or "</head>" not in doc:
        return False
    doc = doc.replace("</head>", LINK_TAG + "\n</head>", 1)
    with open(path, "w", encoding="utf-8") as f:
        f.write(doc)
    return True


posts = []
for path in glob.glob(os.path.join(ROOT, "blog", "*", "index.html")):
    slug = os.path.basename(os.path.dirname(path))
    with open(path, encoding="utf-8") as f:
        doc = f.read()
    title = meta(doc, "property", "og:title")
    if not title:
        m = re.search(r"<title>([^<]*)</title>", doc)
        title = html.unescape(m.group(1)).split(" | ")[0].strip() if m else slug
    date = meta(doc, "property", "article:published_time")
    if not date:
        print("skipped, no article:published_time:", slug)
        continue
    when = datetime.datetime.fromisoformat(date[:10]).replace(
        hour=12, tzinfo=datetime.timezone.utc)
    posts.append({
        "title": title,
        "desc": meta(doc, "name", "description"),
        "image": meta(doc, "property", "og:image"),
        "url": "%s/blog/%s/" % (SITE, slug),
        "when": when,
    })
    if POST_LINKS:
        ensure_link(path)

posts.sort(key=lambda p: (p["when"], p["title"]), reverse=True)
ensure_link(os.path.join(ROOT, "library.html"))

items = []
for p in posts:
    enclosure = ""
    if p["image"]:
        enclosure = '\n      <media:content url="%s" medium="image"/>' % esc(p["image"])
    items.append("""    <item>
      <title>%s</title>
      <link>%s</link>
      <guid isPermaLink="true">%s</guid>
      <pubDate>%s</pubDate>
      <description>%s</description>%s
    </item>""" % (esc(p["title"]), p["url"], p["url"],
                  format_datetime(p["when"]), esc(p["desc"]), enclosure))

latest = posts[0]["when"] if posts else datetime.datetime.now(datetime.timezone.utc)
xml = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:media="http://search.yahoo.com/mrss/">
  <channel>
    <title>SideKix Blog</title>
    <link>%s/library.html</link>
    <atom:link href="%s" rel="self" type="application/rss+xml"/>
    <description>Guides, answers and essays for people starting and building a business, from SideKix.</description>
    <language>en-us</language>
    <lastBuildDate>%s</lastBuildDate>
    <image>
      <url>%s/assets/k-mark.png</url>
      <title>SideKix Blog</title>
      <link>%s/library.html</link>
    </image>
%s
  </channel>
</rss>
""" % (SITE, FEED_URL, format_datetime(latest), SITE, SITE, "\n".join(items))

with open(os.path.join(ROOT, "feed.xml"), "w", encoding="utf-8") as f:
    f.write(xml)
print("feed.xml: %d posts, newest %s" % (len(posts), posts[0]["url"] if posts else "none"))
