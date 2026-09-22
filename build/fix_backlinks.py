# -*- coding: utf-8 -*-
"""
Back links that pointed at the wrong hub, and the pages that never got one.

Three problems, one pass, every step idempotent so this can sit in the
rebuild pipeline and cost nothing on a run where the markup is already right.

1. Every article under blog/ carries "Back to the blog" pointing at
   resources.html. resources.html is the Resource Library, the page of
   agencies, lenders and registries. The blog index is library.html, which is
   where all sixty three posts are listed, so the link was sending readers to
   a page that does not list a single one of them.

2. glossary.html carries "Back to resources" pointing at resources.html while
   faq.html, market-data.html, tools.html and resources.html all point at
   library.html. It was the odd one out inside its own hub.

3. business-events/*.html, hire-a-business-advisor.html and
   free-small-business-help-north-carolina.html have no back link at all.
   All of them use the article shell, so a .backlink anchor as the first
   child of .ahead picks up assets/article.css with no new styling.

Nothing here needs the network and nothing outside the standard library.
"""

import io
import os
import re
import glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read(path):
    with io.open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def write(path, text):
    with io.open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)


# ---- 1. the blog articles -------------------------------------------------
# The anchor is written by the article builder and is byte identical across
# all sixty three files, so an exact string swap is safer than a regex.

BLOG_OLD = '<a class="backlink" href="../../resources.html">'
BLOG_NEW = '<a class="backlink" href="../../library.html">'


def fix_blog():
    changed = 0
    for path in sorted(glob.glob(os.path.join(ROOT, "blog", "*", "index.html"))):
        text = read(path)
        if BLOG_OLD not in text:
            continue
        write(path, text.replace(BLOG_OLD, BLOG_NEW))
        changed += 1
    return changed


# ---- 2. the glossary ------------------------------------------------------
# Only the anchor inside the back row moves. Other references to
# resources.html on the page are real links to the Resource Library.

GLOSS = re.compile(
    r'(<p class="kx-backrow">\s*<a class="kx-bk" href=")resources\.html'
    r'("[\s\S]*?)Back to resources(\s*</a>)'
)


def fix_glossary():
    path = os.path.join(ROOT, "glossary.html")
    if not os.path.exists(path):
        return 0
    text = read(path)
    fixed = GLOSS.sub(r"\1library.html\2Back to Resources\3", text, count=1)
    if fixed == text:
        return 0
    write(path, fixed)
    return 1


# ---- 3. the pages with no back link at all --------------------------------

AHEAD = '<div class="ahead">\n'


def anchor(href, label):
    return (
        '<a class="backlink" href="%s">\n'
        '<svg aria-hidden="true" focusable="false" viewbox="0 0 24 24">'
        '<path d="M15 5l-7 7 7 7"></path></svg>\n'
        "        %s\n"
        "      </a>\n" % (href, label)
    )


def add_backlink(path, href, label):
    """Put a back link at the top of .ahead. Leaves a page that already has
    one of either kind exactly as it found it."""
    if not os.path.exists(path):
        return False
    text = read(path)
    if 'class="backlink"' in text or "kx-backrow" in text:
        return False
    head = text.find(AHEAD)
    if head == -1:
        return False
    cut = head + len(AHEAD)
    write(path, text[:cut] + anchor(href, label) + text[cut:])
    return True


def fix_orphans():
    changed = 0
    for path in sorted(glob.glob(os.path.join(ROOT, "business-events", "*.html"))):
        if add_backlink(path, "../events.html", "Back to Events"):
            changed += 1
    for name in ("hire-a-business-advisor.html",
                 "free-small-business-help-north-carolina.html"):
        if add_backlink(os.path.join(ROOT, name), "library.html", "Back to Resources"):
            changed += 1
    return changed


def main():
    blog = fix_blog()
    gloss = fix_glossary()
    orphans = fix_orphans()
    print("blog articles repointed at library.html: %d" % blog)
    print("glossary back row repointed:             %d" % gloss)
    print("pages given a back link:                 %d" % orphans)
    if not (blog or gloss or orphans):
        print("Nothing to do, every back link already points where it should.")


if __name__ == "__main__":
    main()
