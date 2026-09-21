#!/usr/bin/env python3
"""
fix_guides_cta.py - one string, 63 article pages.

Every article carries the same closing pair of buttons, and the second one
said "More free guides". The wording changes to "More guides". That is the
whole job, but it lives in 63 separate files, so it runs here rather than by
hand: a scripted replacement is reviewable, repeatable and cannot half apply
the way sixty three manual edits can.

Idempotent. Running it twice changes nothing the second time, so it is safe
to leave wired into a workflow.

    python build/fix_guides_cta.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Keyed on the closing tag so this only ever matches the button label and
# never prose that happens to contain the same words.
SWAPS = [(">More free guides</a>", ">More guides</a>")]

# The article generator writes the same markup into every new page, so it has
# to change too. Without this the next article built puts the old wording back.
ALSO = [ROOT / "build" / "artgen.py"]


def main() -> int:
    targets = sorted(ROOT.glob("blog/*/index.html"))
    targets += [p for p in ALSO if p.exists()]

    changed, hits = [], 0
    for path in targets:
        text = path.read_text(encoding="utf-8")
        before = text
        for old, new in SWAPS:
            hits += text.count(old)
            text = text.replace(old, new)
        if text != before:
            path.write_text(text, encoding="utf-8")
            changed.append(str(path.relative_to(ROOT)))

    print(f"  {len(changed)} files changed, {hits} replacements")
    for name in changed[:8]:
        print(f"    {name}")
    if len(changed) > 8:
        print(f"    and {len(changed) - 8} more")
    if not changed:
        print("  nothing to do, the wording is already current")
    return 0


if __name__ == "__main__":
    sys.exit(main())
