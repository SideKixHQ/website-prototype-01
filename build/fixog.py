# -*- coding: utf-8 -*-
"""Make og:image and twitter:image absolute, and point them at a real card.

The Open Graph spec requires an absolute URL. Every page on this site carried
a relative one, which LinkedIn commonly resolves to nothing, so shared links
showed no image. og:url on the same pages was already absolute, so this looks
like it was simply missed.

The quiz pages get their own card. Everything else gets the new 1200x630
default in place of the old 512x512 square, which rendered as a thumbnail.
"""
import io, os, re, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://sidekixhq.com"
OLD = "assets/img/6d3c8fff08a8.png?v=2"
DEFAULT = SITE + "/assets/og/default.png"

def card_for(path):
    rel = os.path.relpath(path, ROOT).replace(os.sep, "/")
    m = re.match(r"^q/([a-z0-9\-]+)/index\.html$", rel)
    if m and os.path.exists(os.path.join(ROOT, "assets", "og", "q-%s.png" % m.group(1))):
        return "%s/assets/og/q-%s.png" % (SITE, m.group(1))
    return DEFAULT

def main():
    files = sorted(glob.glob(os.path.join(ROOT, "*.html")) +
                   glob.glob(os.path.join(ROOT, "blog", "*", "index.html")) +
                   glob.glob(os.path.join(ROOT, "q", "*", "index.html")))
    changed = 0
    for p in files:
        s = io.open(p, encoding="utf-8").read()
        card = card_for(p)
        out = s
        # the exact relative value the whole site carries
        out = out.replace('content="%s" property="og:image"' % OLD,
                          'content="%s" property="og:image"' % card)
        out = out.replace('content="%s" name="twitter:image"' % OLD,
                          'content="%s" name="twitter:image"' % card)
        # anything else still relative on these two tags
        def abs_tag(m):
            attr, val, tail = m.group(1), m.group(2), m.group(3)
            if val.startswith("http") or val.startswith("data:"):
                return m.group(0)
            return '<meta content="%s" %s="%s"%s' % (card, attr[0], tail and tail or "", "")
        for prop in ('property="og:image"', 'name="twitter:image"'):
            out = re.sub(r'<meta content="(?!https?:|data:)([^"]*)" ' + re.escape(prop),
                         lambda m: '<meta content="%s" %s' % (card, prop), out)
        # a large card renders as a large card only if declared as one
        if "twitter:card" in out:
            out = re.sub(r'(<meta content=")summary("\s+name="twitter:card")',
                         r'\1summary_large_image\2', out)
        if out != s:
            io.open(p, "w", encoding="utf-8").write(out)
            changed += 1
    print("%d of %d files updated" % (changed, len(files)))

if __name__ == "__main__":
    main()
