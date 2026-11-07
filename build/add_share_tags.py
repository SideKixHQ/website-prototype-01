"""Add description, canonical and share tags to pages built before the generators wrote them.

The glossary term pages (what-is-*.html) and get-app.html carry no meta
description, canonical, Open Graph or Twitter tags. build/toolgen.py writes
these for pages it builds now, but the term pages on disk predate that and
have been repaired by hand since, so rebuilding them is not safe. This adds
the same tags, in the same format, to the built files, and only where a tag
is missing, so it is safe to run again.

Robots are left alone: these pages are noindex on purpose (vercel.json and
get-app.html's own robots tag), and that is not this script's call.
"""
import glob, html, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://sidekixhq.com'
IMG = SITE + '/assets/og/default.png'


def e(s):
    return html.escape(s, quote=True)


def trim(text, limit=160):
    text = re.sub(r'\s+', ' ', text).strip()
    if len(text) <= limit:
        return text
    cut = text[:limit]
    end = max(cut.rfind('. '), cut.rfind('? '))           # a whole sentence if one fits
    if end >= 90:
        return cut[:end + 1]
    return cut[:cut.rfind(' ')].rstrip(',;:') + '…'


def add_tags(path, desc, short):
    s = open(path, encoding='utf-8').read()
    i = s.find('</head>')
    head = s[:i]
    url = '%s/%s' % (SITE, os.path.basename(path))
    added = 0
    for probe, tag in (
        ('name="twitter:description"', '<meta content="%s" name="twitter:description"/>' % e(desc)),
        ('name="twitter:image"', '<meta content="%s" name="twitter:image"/>' % IMG),
        ('name="twitter:title"', '<meta content="%s" name="twitter:title"/>' % e(short)),
        ('name="twitter:card"', '<meta content="summary_large_image" name="twitter:card"/>'),
        ('property="og:image:alt"', '<meta content="The SideKix K mark" property="og:image:alt"/>'),
        ('property="og:image"', '<meta content="%s" property="og:image"/>' % IMG),
        ('property="og:url"', '<meta content="%s" property="og:url"/>' % url),
        ('property="og:description"', '<meta content="%s" property="og:description"/>' % e(desc)),
        ('property="og:title"', '<meta content="%s" property="og:title"/>' % e(short)),
        ('property="og:site_name"', '<meta content="SideKix" property="og:site_name"/>'),
        ('property="og:type"', '<meta content="website" property="og:type"/>'),
        ('rel="canonical"', '<link href="%s" rel="canonical"/>' % url),
        ('name="description"', '<meta content="%s" name="description"/>' % e(desc)),
    ):
        if probe not in head:
            head = re.sub(r'(</title>)', lambda m: m.group(1) + '\n' + tag, head, count=1)
            added += 1
    if added:
        open(path, 'w', encoding='utf-8').write(head + s[i:])
    return added


def main():
    done = {}
    for path in sorted(glob.glob(os.path.join(ROOT, 'what-is-*.html'))):
        s = open(path, encoding='utf-8').read()
        title = re.search(r'<title>(.*?)</title>', s, re.S).group(1).strip()
        faq = None
        for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
            d = json.loads(block)
            if d.get('@type') == 'FAQPage':
                faq = d['mainEntity'][0]['acceptedAnswer']['text']
        done[os.path.basename(path)] = add_tags(path, trim(html.unescape(faq)), html.unescape(title.split(' | ')[0]))
    done['get-app.html'] = add_tags(os.path.join(ROOT, 'get-app.html'),
        'Download the SideKix app on iPhone from the App Store. Kix, your Entrepreneurial Support Guide, is inside the app.',
        'Get the SideKix app')
    print('pages updated: %d, tags added: %d' % (sum(1 for v in done.values() if v), sum(done.values())))


if __name__ == '__main__':
    main()
