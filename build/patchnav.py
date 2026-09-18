# -*- coding: utf-8 -*-
"""Put the main nav into the top bar of every blog article.

Articles run on the light article template rather than the main site shell, so
until now the only way out of a post above the fold was the wordmark or the
Build the Future button. Someone arriving from a shared link could not reach
Membership, Advisors, Partners or Events without scrolling to the footer.

artgen.py emits the nav for anything written from here on. This brings the
articles that already exist into line. It is safe to run more than once: a post
that already has the nav is left alone.
"""
import glob, io, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

NAV = """<nav aria-label="Main" class="anav">
<a href="../../index.html">Home</a>
<a href="../../how-it-works.html">How it works</a>
<a href="../../membership.html">Membership</a>
<a href="../../advisors.html">Advisors</a>
<a href="../../partners.html">Partners</a>
<a href="../../events.html">Events</a>
<a aria-current="page" href="../../library.html">Resources</a>
</nav>
"""

# the anchor is the CTA that closes the bar, whatever whitespace surrounds it
CTA = re.compile(r'(\s*)(<a class="acta" href="\.\./\.\./membership\.html">Build the Future</a>)')


def main():
    posts = sorted(glob.glob(os.path.join(ROOT, "blog", "*", "index.html")))
    done = skipped = missed = 0
    for p in posts:
        s = io.open(p, encoding="utf-8").read()
        if 'class="anav"' in s:
            skipped += 1
            continue
        m = CTA.search(s)
        if not m:
            print("   ! no top bar CTA found in %s" % os.path.relpath(p, ROOT))
            missed += 1
            continue
        s = s[:m.start()] + "\n" + NAV + m.group(2) + s[m.end():]
        io.open(p, "w", encoding="utf-8").write(s)
        done += 1
    print("blog nav: %d updated, %d already had it, %d could not be matched"
          % (done, skipped, missed))


if __name__ == "__main__":
    main()
