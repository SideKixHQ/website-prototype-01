#!/usr/bin/env python3
"""strip_donor_schema.py - take the blog post's structured data off the pages
that borrowed its shell.

Several pages are built by copying the head, nav and footer of an existing
page so they cannot drift out of step with the rest of the site. The page
chosen as the donor is a blog post, and a blog post keeps its structured data
after the article rather than in the head, so the copy brought three JSON-LD
blocks with it:

  BlogPosting      says the page is "How to Network When You're Just Starting
                   Out" and points mainEntityOfPage at the blog post's URL.
  BreadcrumbList   a trail ending Home > Blog > How to Network ...
  FAQPage          the networking questions from that post.

On 27 pages, including all 25 state event pages, that told Google each page
was an article it is not, gave it a breadcrumb trail to somewhere else, and
attached questions that have nothing to do with it. Each of those pages also
writes its own CollectionPage or WebPage graph with its own BreadcrumbList, so
the two disagreed.

The builders no longer copy these blocks. This removes the ones already on
disk. It matches on the donor's exact text, so a page's own structured data
cannot be caught by mistake, and it never touches the donor itself.

Idempotent.

    python build/strip_donor_schema.py [--dry-run]
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DONOR = ROOT / "blog" / "how-to-network-when-youre-just-starting-out" / "index.html"

GLOBS = ("*.html", "blog/*/index.html", "q/*/index.html", "business-events/*.html")
BLOCK = re.compile(r'\s*<script type="application/ld\+json">.*?</script>', re.S)


def donor_blocks() -> list[str]:
    """The blocks the donor keeps after its article, which is what got copied."""
    text = DONOR.read_text(encoding="utf-8")
    body = re.search(r"<body>(.*)</body>", text, re.S).group(1)
    tail = body[body.rfind("</main>") + len("</main>"):]
    return [m.group(0).strip() for m in BLOCK.finditer(tail)]


def main() -> int:
    dry = "--dry-run" in sys.argv
    if not DONOR.exists():
        print(f"  donor page missing: {DONOR.relative_to(ROOT)}")
        return 1
    blocks = donor_blocks()
    if not blocks:
        print("  the donor carries no structured data after its article, nothing to do")
        return 0
    print(f"  {len(blocks)} donor blocks to look for")

    changed, removed = [], 0
    for pattern in GLOBS:
        for path in sorted(ROOT.glob(pattern)):
            if path.resolve() == DONOR.resolve():
                continue
            text = path.read_text(encoding="utf-8")
            out, hits = text, 0
            for block in blocks:
                while block in out:
                    out = out.replace(block, "", 1)
                    hits += 1
            if hits:
                removed += hits
                changed.append((str(path.relative_to(ROOT)), hits))
                if not dry:
                    path.write_text(re.sub(r"\n{3,}", "\n\n", out), encoding="utf-8")

    print(f"  {len(changed)} pages {'would lose' if dry else 'lost'} "
          f"{removed} borrowed blocks")
    for name, hits in changed[:8]:
        print(f"    {name}: {hits}")
    if len(changed) > 8:
        print(f"    and {len(changed) - 8} more")
    if not changed:
        print("  nothing to do, no page is carrying the donor's structured data")
    return 0


if __name__ == "__main__":
    sys.exit(main())
