# Changelog

A record of what changed on the SideKix site, why, and how each change was
checked. Written because the repository history is a run of "Add files via
upload" commits, which say nothing about intent.

All measurements below were taken with Playwright against a local copy of the
site, comparing the build before the change with the build after it.

---

## 2026-09-03

### Events listings printed raw markup and drifted a day outside Eastern time

Audited all 761 cards the events page renders. Four defects:

**Markup shown as text.** Some hosts publish their blurb as HTML, so the weekly
feed arrives carrying paragraph tags, entities and literal escapes. The page
escapes incoming text for safety, which is correct, but that meant the tag was
*printed* rather than executed. 21 cards opened with a visible `<p>`. A
`clean()` pass now decodes entities first, then strips tags, so an
already-escaped tag cannot survive as text.

**One card overrunning its neighbour.** A description that was nothing but a
47-character URL had no break opportunity, so 160px of text painted across the
card beside it — measured at 1100px, 1600px and 2000px. A grid track declared
`1fr` keeps an automatic minimum equal to its widest unbreakable content;
`min-width: 0` on the items removes it and `overflow-wrap` lets the word break.
The narrow breakpoints already did this, so it now applies at every width. A
description that is only the event's own link is dropped — the button below it
says the same thing.

**Blurbs cut mid-sentence.** Nine listings arrived already truncated by the
host, ending on a dangling function word plus a full stop ("…retaining
workers. At."). Those fragments are trimmed, and the page's own 200-character
cut now lands on a word boundary with an ellipsis.

**Date-only rows drifting a day.** 170 listings carry no real start time, and
the feed pads them to midnight in the host's timezone. Converting midnight to
the reader's clock moves the date: an event whose own title reads "September 8"
showed as "September 7 · 9pm" in California. Verified across five timezones.
Date-only rows are now read as plain calendar numbers, so the day is the host's
day everywhere. Listings with a real start time still convert, which is
correct — a 3pm Eastern webinar should read 12pm in California.

Counts across 761 cards, before → after: visible markup 21 → 0, stray escapes
1 → 0, text outside its box 1 → 0, mid-sentence cuts 9 → 0.

517 cards still carry no description at all. That is a gap in the source data,
not a rendering fault.

`events.html`, `assets/site-wide.css`

### The trace-a-path counter sat below the diagram's centre

`.loop-centre` was absolutely positioned at `top: 50%` of `.loop-stage`, but
the stage is the square diagram *plus* the path readout and the "Trace a path"
button beneath it. Half of that column falls about 60px below the diamond's
real centre, so "PATHS TRACED" landed on the horizontal Community–Discovery
edge and the numeral ran 12px into the Advisors node.

Percentage margins resolve against the containing block's *width*, and the
diagram is square and fills the stage, so `margin-top: 50%` is exactly half the
diagram's height. This correction already existed at the mobile breakpoint; it
now applies everywhere. Block centre against the edge it should sit on:

| Width  | Should be | Was | Now |
|--------|-----------|-----|-----|
| 390px  | 363 | 363 | 363 |
| 768px  | 452 | 524 | 452 |
| 1440px | 461 | 521 | 461 |
| 2303px | 604 | 664 | 604 |

Also hides the blue "Entered at …" line, which repeated the first step of the
path readout directly below it while sitting on top of the Advisors node. This
is a different element from the blue "Every path is different" sentence removed
earlier that day. A soft radial disc behind the numeral lets the two edges that
cross at the centre pass behind it rather than striking through.

`assets/site-wide.css`

### The three doors clipped their own labels

`#kx-doors` set a fixed height — 300px on desktop, 210px on phones — and each
card's text was absolutely positioned against the bottom edge. Absolute content
contributes nothing to its parent's height, so any card whose text ran past
that fixed height pushed its top line out through the roof of the box, where
`overflow: hidden` cut it away.

"Share what you know" is one line longer than its neighbours, so its FOR
ADVISORS label was clipped at every width — 30px on desktop, where the label
vanished entirely. On phones all three cards clipped: 19px, 42px, 19px.
Measured across 16 widths from 375px to 2303px; now 0 everywhere.

The text is a normal flow child, so the card grows to fit it, and
`justify-content` moved up to the card so the text stays bottom-anchored as
before. Cards gain 31px on desktop and 20–43px on mobile.

`assets/site-wide.css`

### The cursor spotlight cost the site three quarters of its frame rate

`#kx-desat` covered the whole viewport with `backdrop-filter` plus an animated
mask, so every pointer movement forced the browser to re-snapshot and re-filter
the entire screen. Measured at 1440×900 while moving the pointer and scrolling:
how-it-works 66.7ms per frame (~15fps), terms 50.0ms, partners 66.7ms, faq
66.6ms, with 57–60 of every 60 frames stuttering.

Worse than the frame rate, the promoted full-viewport layer left stale tiles on
screen during the pinned how-it-works sequence: the phone and the beat panels
were painted at the wrong offset or not at all, which read as images being cut
off mid-scroll. DOM geometry was correct throughout — the phone measured
165–985 in a 1150px viewport — so only the paint was wrong.

Painting a radial gradient gives the same spotlight without re-reading the
backdrop. Every affected page now holds 16.7ms (60fps). One consequence: a
painted overlay cannot desaturate, so the page keeps its colour outside the
cursor instead of greying out. Contrast improves as a side effect.

The override lives in `site-wide.css` at `#kx-desat#kx-desat` so it outranks
every per-page variant regardless of load order.

`assets/site-wide.css`

### Cache headers, corrected twice

`vercel.json` applied `max-age=31536000, immutable` to everything under
`/assets/`. That is right for extracted images, scripts and fonts, whose
filenames are content hashes — a change always produces a new URL. It is wrong
for `site-wide.css`, which has a stable name: updating it produced a file
browsers would not re-fetch for a year.

The first correction scoped the rules by path but got their order backwards.
Vercel applies every matching rule and lets later ones win for the same header
key, so the general `/assets/(.*)` catch-all sat last and overrode the specific
rules above it. Measured live: hashed images were getting `max-age=86400`
instead of `immutable`, and `site-wide.css` was getting 86400 instead of 600.
Neither rule was doing what it said.

Final order, general first and specific last:

| Path | Cache |
|------|-------|
| `/assets/img\|js\|fonts/*` | one year, immutable — content-hashed names |
| `/assets/*.woff2` | one year, immutable — stable content |
| `/assets/*.css\|js` | 10 minutes — stable names, mutable content |
| `/assets/*` | one day |
| `*.html` | 10 minutes |

The stylesheet link is also versioned by content hash, because correcting a
header does not help a browser already holding the file under the old one —
only a different URL does.

`vercel.json`, 17 HTML pages

### The mobile nav left a stray band under the header

At 760px and below the nav collapses `.kx-links` with `max-height: 0` and
`overflow: hidden`. `max-height` clips the content box only — not padding, not
borders. The panel kept 6px top and 10px bottom padding, so 17px of background
stayed on screen as a band beneath the header, with the gold rule stranded at
the bottom of it.

Only the padding is zeroed; the 1px bottom border *is* that gold rule and is
deliberately kept. `.kx-links` goes from 17px to 1px — the line and nothing
else. Scoped to the closed state, so the open menu is untouched: verified it
still opens to 329px with its padding restored.

### Wide screens pushed content left instead of centring it

`site-wide.css` capped `.wrap`, `.next` and `.mem .phasechips` but never gave
them automatic side margins, so constraining the width moved content left
rather than centring it — 372px off on partners.html at 2303px. Added
`margin-inline: auto`. Verified at 1440/1800/2000/2303px: offset now 0 on every
page, shells still capped, no overflow. index.html's hero stays left-aligned by
design, identical with and without the stylesheet.

### Every form on the site discarded what people typed

The waitlist form on `join.html` validated input, hid itself and showed the
thank-you panel **without sending anything anywhere**. Signups made through it
were silently thrown away. The 65-field advisor application on
`become-an-advisor.html` had the same defect: it validated, rendered a summary,
showed the confirmation and sent nothing. The support modal appears on 14 pages
but only one had been pointed at the API; the other 13 fell back to opening a
mail client. `partners.html` was mailto-only and collected no email address at
all, so applications arrived with no way to reply.

All of them now post to the backend. Each carries a hidden honeypot field the
server checks. On failure the visitor gets a real error and a working address
to write to, rather than a false confirmation.

Verified end-to-end against a live backend: waitlist and support confirmed on
the production site, the advisor application confirmed at the API level with
the CV and photo attached to the notification email.

`join.html`, `partners.html`, `become-an-advisor.html`, 14 pages for the modal

### Brand fonts had never loaded

Pre-existing, from the original export. The `@font-face` rules used
`url("assets/…woff2")`, but the stylesheet itself lives at
`/assets/fonts.css`, so those resolved to `/assets/assets/…` and 404'd.
Confirmed against production: 34 faces, zero loaded, both Space Grotesk and
Cormorant Garamond failing `document.fonts.check`. The site had been rendering
in Georgia and system fallbacks throughout. Rewrote 40 paths.

**Still outstanding:** Poppins, the body face, is declared as
`url("assets/"Poppins"-<hash>.ttf")` — the quotes are nested wrong and the
files it names are not in the repository. Body copy still falls back to
whatever sans the visitor's device supplies. Also from the original export.

`assets/fonts.css`

### Event cards overflowed on phones

`#kx-grid` had five competing rules, every one marked `!important`, layered up
from earlier patches. The last in source order won with a plain `1fr` column,
whose automatic minimum is the item's content width — 544px. On a 390px phone
that put 174px of every card past the right edge, and because `main` uses
`overflow-x: clip` the page did not scroll, it simply cut the cards off.

Changed the governing rule to `minmax(0,1fr)` plus `min-width: 0` on the
children. Verified at 320/360/390/430/768/1024/1440/2303px: one column on
phones, two on tablets, three on desktop, zero overflow at every width. Desktop
rendering unchanged.

### A year of cached 404s from the asset extraction

`vercel.json` applied `max-age=31536000, immutable` to everything under
`/assets/`, and Vercel sends that header on 404 responses too. Any browser that
loaded the site while the extracted images were missing had those failures
cached for a year — and a phone cannot hard-refresh. Appended `?v=2` to all 176
asset references: same files, new URLs, cached failures bypassed automatically.

### The FAQ cursor was inert

The markup and base styles were present but the driver script was not, so the
elements sat at `opacity: 0` and never moved. Three layering rules were missing
too, including the z-index that puts the cursor above the page. Added both,
matching `glossary.html`.

**Still outstanding:** `privacy.html` and `terms.html` have the same gap.

`faq.html`

---

## Known issues

- **Poppins does not load.** Malformed `@font-face` URLs and missing files, in
  `assets/fonts.css`. Body copy renders in a system fallback everywhere.
- **The homepage is slow.** ~50ms per frame on desktop and ~67ms on mobile even
  after the spotlight fix, from the hero artwork's drop-shadows and blend
  modes. Not yet addressed.
- **`server.js` is in this repository.** It belongs in `sidekix-email-server`,
  which is what Render deploys, and an identical copy is already there. Vercel
  serves this repository statically, so it is publicly readable. It contains no
  credentials — every key reads from `process.env` — but it does publish the
  honeypot field name, the rate limits and the CORS allowlist.
- **`sidekix-site.zip` is in this repository** — 11.1 MB, the old export.
- **`sitewide.css` at the repository root** is a stray duplicate of
  `assets/site-wide.css`. Nothing links to it.
- **517 event cards have no description**, because the host published none.
- **`partners.html` is missing from `sitemap.xml`.**
- **Backend contacts are stored in `/tmp`** on Render, which is wiped on
  restart.
- **The shared secret is published** in the portal repository's source and in
  the backend README. Rotating it requires changing Render and the portal at
  the same moment.
- **Test records to delete:** `james+wl-test@`, `james+sup-test@` and
  `james+adv-test@sidekixhq.com`. The waitlist one is in the 3/7/14-day
  follow-up sequence.
