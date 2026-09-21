#!/usr/bin/env python3
"""add_affiliate_link.py - put the Affiliate Policy in the footer of every page.

The site has no template layer. Every page carries its own inlined footer, so
a new legal link has to be written into all of them. Doing that by hand across
279 files is how a footer ends up different on the twelve pages someone
missed, which is exactly the inconsistency an FTC disclosure cannot afford:
the disclosure has to be reachable from wherever a reader lands.

Three different footers are in use. Most pages list Terms, Privacy, Cookie and
Purchase Policy; the quizzes stop at Cookie Policy; the glossary stops at
Privacy. All three end the Company column with the same Support line, so that
is the anchor, and the new link goes immediately before it. The relative
prefix is read off the Terms link on the same page, so a blog post two folders
deep gets ../../ and a root page gets none without this script knowing
anything about the folder layout.

Idempotent: a page that already has the link is left alone.

    python build/add_affiliate_link.py [--dry-run]
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SUPPORT = '<li><a href="mailto:support@sidekixhq.com">Support</a></li>'
# Whichever legal link a given footer happens to carry, all of them point at a
# root level page, so any one of them gives the right number of ../ steps.
PREFIX = re.compile(r'href="((?:\.\./)*)(?:terms|privacy|cookies)\.html"')

# The generators build new pages by copying the head, nav and footer of a
# donor page, so the donors have to carry the link too or the next page built
# drops it again.
GLOBS = ("*.html", "blog/*/index.html", "q/*/index.html", "business-events/*.html")


def main() -> int:
    dry = "--dry-run" in sys.argv
    paths: list[Path] = []
    for pattern in GLOBS:
        paths.extend(sorted(ROOT.glob(pattern)))

    changed, already, skipped = [], 0, []
    for path in paths:
        text = path.read_text(encoding="utf-8")
        if text.count(SUPPORT) != 1:
            skipped.append(str(path.relative_to(ROOT)))
            continue
        found = PREFIX.search(text)
        if not found:
            skipped.append(str(path.relative_to(ROOT)))
            continue
        prefix = found.group(1)
        link = (f'<li><a href="{prefix}affiliate-policy.html">'
                "Affiliate Policy</a></li>")
        if link in text:
            already += 1
            continue
        if not dry:
            path.write_text(text.replace(SUPPORT, link + SUPPORT, 1),
                            encoding="utf-8")
        changed.append(str(path.relative_to(ROOT)))

    print(f"  {len(paths)} pages checked")
    print(f"  {len(changed)} {'would change' if dry else 'changed'}, "
          f"{already} already had it")
    if skipped:
        print(f"  {len(skipped)} have no footer to add it to: "
              f"{', '.join(skipped)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
