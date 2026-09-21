#!/usr/bin/env python3
"""
fix_page_meta.py - give every indexed page a description, a canonical and
share tags.

The cause. build/toolgen.py builds a page by copying the head of a donor
page, tools.html, and swapping the description string inside it. At some
point tools.html was regenerated without a description, a canonical or any
og tags, so there was nothing left to swap and every page built from it
inherited a head with none of them. That is 111 of the 217 URLs in the
sitemap, including all fifty state LLC pages, the industry guides and the
quizzes. Google writes its own snippet when there is no description, which
is why those pages collect impressions and no clicks.

The fix has two halves. toolgen.py now writes the tags itself rather than
inheriting them, so new pages are correct. This script repairs the pages
already on disk, because regenerating them would mean re-running a dozen
builders and risking hand edits made since.

Where the text comes from. Every one of these pages already carries a
hand-written <p class="lede">, which is a summary of the page written by a
person. That is a better description than anything assembled from body copy,
so it is what gets used, trimmed to fit a search result at a sentence or
clause boundary rather than mid-word.

Idempotent: a page that already has a tag keeps the one it has.

    python build/fix_page_meta.py [--dry-run]
"""

from __future__ import annotations

import html as H
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://sidekixhq.com"
SITEMAP = os.path.join(ROOT, "sitemap.xml")

# Google renders roughly 155 to 160 characters. Going long is not an error,
# it just gets cut, so the target is a clean end rather than a hard limit.
TARGET = 158
FLOOR = 90

OG_IMAGE = f"{SITE}/assets/k-mark.png"


def text_of(fragment: str) -> str:
    txt = re.sub(r"<[^>]+>", " ", fragment)
    txt = H.unescape(txt)
    return re.sub(r"\s+", " ", txt).strip()


def trim(text: str) -> str:
    """Cut to length at a boundary a reader would not notice."""
    if len(text) <= TARGET:
        return text
    window = text[:TARGET + 1]
    # Prefer ending on a finished sentence.
    for stop in (". ", "? ", "! "):
        cut = window.rfind(stop)
        if cut >= FLOOR:
            return window[:cut + 1].strip()
    if window.rstrip().endswith((".", "?", "!")):
        return window.strip()
    # Then a clause break, then a word break.
    for stop in (", ", "; ", ": "):
        cut = window.rfind(stop)
        if cut >= FLOOR:
            return window[:cut].strip() + "."
    cut = window.rfind(" ")
    return (window[:cut] if cut >= FLOOR else window).strip().rstrip(",;:") + "."


def sitemap_paths() -> list[str]:
    sm = io.open(SITEMAP, encoding="utf-8").read()
    out = []
    for url in re.findall(r"<loc>([^<]+)</loc>", sm):
        rel = url.replace(SITE + "/", "")
        if rel == "":
            rel = "index.html"
        elif not rel.endswith(".html"):
            rel = rel.rstrip("/") + "/index.html"
        out.append(rel)
    return out


def canonical_for(rel: str) -> str:
    if rel == "index.html":
        return SITE + "/"
    if rel.endswith("/index.html"):
        return f"{SITE}/{rel[:-len('index.html')]}"
    return f"{SITE}/{rel}"


def repair(rel: str, dry: bool) -> tuple[bool, str]:
    path = os.path.join(ROOT, rel)
    if not os.path.exists(path):
        return False, "missing on disk"
    s = io.open(path, encoding="utf-8", errors="replace").read()

    title_m = re.search(r"<title>(.*?)</title>", s, re.S)
    if not title_m:
        return False, "no <title> to anchor to"
    title = text_of(title_m.group(1))
    short = title.split(" | ")[0].strip()

    # A page that already has a description keeps it, and the share tags are
    # built from it, so the two never disagree.
    have = (re.search(r'<meta[^>]*name="description"[^>]*content="([^"]*)"', s)
            or re.search(r'<meta[^>]*content="([^"]*)"[^>]*name="description"', s))
    if have:
        desc = H.unescape(have.group(1)).strip()
    else:
        desc = ""
        lede = re.search(r'<p class="lede"[^>]*>(.*?)</p>', s, re.S)
        if lede:
            desc = text_of(lede.group(1))
        # The quiz pages use the lede for a run time ("5 questions, about 30
        # seconds"), which describes nothing. When it is that short, the real
        # summary is the longest paragraph near the top of the page.
        if len(desc) < 60:
            paras = [text_of(m) for m in re.findall(r"<p[^>]*>(.*?)</p>", s, re.S)[:12]]
            paras = [x for x in paras if len(x) >= 60 and not x.lower().startswith("last updated")]
            if paras:
                desc = max(paras, key=len)
        desc = trim(desc) if desc else ""
    if len(desc) < 40:
        return False, "description would be too thin"

    add = []
    if not re.search(r'name="description"', s):
        add.append(f'<meta content="{H.escape(desc, quote=True)}" name="description"/>')
    if not re.search(r'rel="canonical"', s):
        add.append(f'<link href="{canonical_for(rel)}" rel="canonical"/>')
    if not re.search(r'name="robots"', s):
        add.append('<meta content="index, follow, max-image-preview:large" name="robots"/>')
    if not re.search(r'property="og:title"', s):
        add.append(f'<meta content="{H.escape(short, quote=True)}" property="og:title"/>')
    if not re.search(r'property="og:description"', s):
        add.append(f'<meta content="{H.escape(desc, quote=True)}" property="og:description"/>')
    if not re.search(r'property="og:url"', s):
        add.append(f'<meta content="{canonical_for(rel)}" property="og:url"/>')
    if not re.search(r'property="og:image"', s):
        add.append(f'<meta content="{OG_IMAGE}" property="og:image"/>')
    if not re.search(r'property="og:site_name"', s):
        add.append('<meta content="SideKix" property="og:site_name"/>')
    if not re.search(r'property="og:type"', s):
        add.append('<meta content="website" property="og:type"/>')
    if not re.search(r'name="twitter:card"', s):
        add.append('<meta content="summary_large_image" name="twitter:card"/>')
    if not re.search(r'name="twitter:title"', s):
        add.append(f'<meta content="{H.escape(short, quote=True)}" name="twitter:title"/>')
    if not re.search(r'name="twitter:description"', s):
        add.append(f'<meta content="{H.escape(desc, quote=True)}" name="twitter:description"/>')

    if not add:
        return False, "already complete"
    if dry:
        return True, f"would add {len(add)} tags | {desc[:70]}"

    block = "\n" + "\n".join(add)
    s = s.replace(title_m.group(0), title_m.group(0) + block, 1)
    io.open(path, "w", encoding="utf-8").write(s)
    return True, f"added {len(add)} tags"


def main() -> int:
    dry = "--dry-run" in sys.argv
    paths = sitemap_paths()
    changed, skipped, failed = [], 0, []
    for rel in paths:
        ok, why = repair(rel, dry)
        if ok:
            changed.append((rel, why))
        elif why == "already complete":
            skipped += 1
        else:
            failed.append((rel, why))

    print(f"  {len(paths)} sitemap pages checked")
    print(f"  {len(changed)} repaired, {skipped} already complete, {len(failed)} could not be done")
    for rel, why in changed[:6]:
        print(f"    {rel}: {why}")
    if len(changed) > 6:
        print(f"    and {len(changed) - 6} more")
    for rel, why in failed:
        print(f"    SKIP {rel}: {why}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
