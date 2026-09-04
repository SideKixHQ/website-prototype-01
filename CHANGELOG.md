# Changelog

A record of what changed on the SideKix site, why, and how each change was
checked. Written because the repository history is a run of "Add files via
upload" commits, which say nothing about intent.

All measurements below were taken with Playwright against a local copy of the
site, comparing the build before the change with the build after it.

---

## 2026-09-04, night

### Advisors, on a phone

**The hero artwork was there and could not be seen.** It sits behind the copy
as a backdrop at .26 opacity under a scrim running to .9, which works on a wide
screen where the art has its own column to the right of the words. A phone has
no such column: the art was directly underneath the text, so the scrim had to
be that heavy, and what was left was invisible. Below 760px it stops being a
backdrop and becomes a picture: out of absolute positioning, under the copy, in
full colour, scrim off.

The plate carries a baked alpha vignette so the artwork can rise out of the
dark on desktop. Standing alone that fade is empty space, so the box is sized
to what is actually drawn. Measured from the alpha channel: opaque from 6.6% to
87.8% down and 10.7% to 89.6% across, an aspect of 0.66. The box is set to that
and the plate scaled 1.26 to fill it.

**The clock was above the words.** In one column it came first in source, so a
phone opened on a red countdown with nothing to say what it was counting. Copy
first now, clock underneath, centred rather than pinned left. It still stops at
00:15.

**The responsibilities list had uneven spacing.** Rows were as tall as their
text, so one line and two lines produced different gaps and the rules beneath
them fell at uneven intervals. A 92px minimum row height puts every rule on the
same spacing, and the number is centred against the row rather than pinned to
its top, so it sits in the middle of a two line row instead of riding above it.
Measured: all six rows 92px, number centre 46px, row centre 46px.

**The support heading stretched.** "We do not just ask you to show up." broke
after "show" and left "up." alone. It is a block with `text-wrap: balance` and
a 15ch measure on a phone now, so it stacks evenly beside the sticker.

### The poster, on the partners page

Left of the hero. It rests gold: desaturated, sepia shifted toward the site
gold, dimmed to .6, so it belongs on the page rather than shouting off it.
Hover restores full colour and lifts brightness past 1, with a gold sheen that
sweeps across once and a gold rim that ignites. The filter is the same function
list in the same order in both states, so the browser interpolates rather than
snapping. Touch devices get no hover, so they rest in a brighter middle state.

`.wrap` on this page is full bleed, unlike the hub pages, because every section
below sets its own measure. The hero row had to do the same or the poster sat
flat against the left edge of the window.

---

## 2026-09-04, evening

### The Resources hub pages did not line up with each other

Going from one to the next, the whole hero moved. Measured across the six at
1440, 1200, 1024, 820, 640, 480, 390 and 360.

The largest cause was source order. Three pages opened with the eyebrow and
then the back link, three with the back link and then the eyebrow, which put
the heading 66px lower on half of them. `market-data.html` was further out
again: no eyebrow at all, an `h1` two pixels larger with a 40px bottom margin
instead of 14, and its disc row four thousand pixels down the page rather than
under the lede. On top of that the eyebrow carried 14px or 18px depending on
the page, the lede 30px or 34px and 52ch or 54ch, and the disc row 34px or
40px.

Order is now fixed in the markup, one sequence everywhere: back link, eyebrow,
heading, lede, discs. The rhythm is set once in `site-wide.css` rather than six
times, so the next page added to the hub inherits it. Every value chosen is the
one the majority of the six already used.

That left copy length. Two of the six headings run to two lines and two of the
ledes to three, so the disc row still landed anywhere in a 57px band, and that
row is exactly what the eye tracks between pages. Above 600px the taller case
is now reserved for both, 2.12em on the heading and 5.17em on the lede, being
two and three lines at their own line heights. Disc row spread from 1440 down
to 640: **0px at every width**, from 57, 56, 48, 38 and 32.

Phones are left alone deliberately. The ledes run to five and six lines at 390
and 360, so reserving the tallest would spend 175px of dead space to close a
32px gap. The residual spread there is 31 to 58px.

CLS after the change: 0.0000 to 0.0271 across the six, well inside the
threshold.

---

## 2026-09-04, later

### Core Web Vitals: two pages were failing CLS

Measured with Playwright, layout-shift observer, buffered, at 390x844 and
1440x900.

**events.html was at 0.2481 desktop and 0.2095 mobile.** Google's threshold is
0.1. `#kx-filters`, `#kx-next` and `#kx-grid` are all empty on first paint and
get filled once `events.json` parses, about 350ms in. The "every Monday" panel
below them was drawn inside the first viewport and then shoved out of it. That
one push was the whole score.

Fixed by reserving the space each block is about to occupy. Settled heights,
measured after render: filters 97px at 1024 and up, 256px on a phone; the
next-up panel 389 to 404 desktop, 574 mobile; the grid runs past nine thousand
pixels, so all that matters there is "taller than the fold". The reservations
are scoped to `html:not(.kx-ready)` and the class goes on in the same frame the
content does, so a week with no upcoming event does not leave a 404px hole.
`#kx-stamp`, empty until the JSON lands and then one 14px line, got a
`min-height` too.

Now 0.0000 desktop. Mobile alternates between 0.0000 and 0.0469 across runs;
the residue is the Google Fonts swap reflowing the hero, which is the same
root cause as the Poppins loading problem already on the known issues list.
Both numbers are inside the "good" band.

**library.html was at 0.0955 desktop**, a hair under the threshold. The
sixty-three article counts on the filter chips were computed in JavaScript from
cards that are already in the HTML, then appended, widening every chip and
reflowing the row. The counts are now baked into the markup at build time. The
script keeps its `if(!b.querySelector('.n'))` guard, so it is a no-op when they
are already there. Now 0.0000 at both widths.

Everything else measured clean: LCP between 92 and 552ms locally, total
blocking time 0 on every page.

### Metadata

An audit of all eighteen pages. Sitemap and robots.txt came back clean:
seventy-nine URLs, no duplicates, no orphans, every HTML file present, every
blog post present, all https, and the sitemap declared in robots.txt with
sixteen AI crawlers named and allowed. Canonicals are self-referential and
correct on every page. Every JSON-LD block parses. One `h1` per page.

Fixed:

- Three titles ran past the roughly sixty characters a result shows.
  `events.html` 68 to 53, `partners.html` 62 to 55, `advisors.html` 61 to 53.
- Four descriptions truncated, five were short enough that Google would write
  its own. All eighteen now sit between 130 and 156 characters. The homepage
  was the worst of them at 83.
- `max-image-preview:large` was on three pages. It is now on all seventeen
  indexable ones, which is what lets a result carry a large image and what
  several answer engines read. `404.html` keeps `noindex`.
- Four pages carried the same `og:description` twice.

### Known, not fixed

- `404.html` has no `og:url`. It is `noindex`, so nothing reads it.
- The homepage title uses an em dash, which the SideKix copy rules exclude.
  Left alone because it is the brand lockup rather than generated copy.
- `library.html` has a card categorised Legal but no Legal filter chip, so
  that piece is only reachable under Everything.
- `index.html` transfers 1.56 MB and `how-it-works.html` 1.12 MB, almost all
  images.

---

## 2026-09-04

### Library became Resources, and the hub discs say where you are

The top level nav item read **Library** and pointed at `library.html`, while the
floating orb tray built its own list in JavaScript and pointed **Resources** at
`resources.html`. Two names, two destinations, one idea. Both now read
**Resources** and both go to `library.html`, which is the hub: the blog index
with its topic filters, and the row of discs leading to everything else.

`resources.html`, the directory of twenty nine public agencies, lenders and
registries, is now the **Resource library** and sits under that hub.

The disc row itself worked backwards. Each page showed the *other* five
destinations and omitted its own, so landing anywhere in the hub gave no sense
of place: five discs, none of them you. Every hub page now carries the same six
discs in the same order, and lights its own:

    Blogs · Resource library · Calculators · Glossary · FAQs · Market data

The lit state is carried by three things rather than colour alone, so it still
reads in greyscale: a brighter rim, the smile that hover normally reveals, and a
halo ring offset from the disc. `aria-current="page"` carries it to a screen
reader.

**Mobile.** Six discs would not fit the single line the row used, so on a phone
it had become a sideways scroller with two discs past the edge and no
affordance saying so. On `market-data.html` the lit disc was the hidden sixth.
Below 600px the row is now a wrapping 3x2 grid: 92px discs, two 14px gaps,
304px inside a 320px viewport. Measured `scrollWidth - clientWidth` at 390px
across all six pages: was 274px, now 0.

The grid rules are written as `.hubdiscs.hubdiscs.hubdiscs` because the
per-page blocks declare `flex-wrap:nowrap` and their gaps with `!important` at
(0,2,0); among `!important` declarations specificity still decides the winner.

**Also fixed while in these files.**

- `library.html` declared `"@id"` and `"url"` of `resources.html` in its
  `CollectionPage` node, and both pages pointed breadcrumb position 2 at
  `resources.html`. The fourth instance of this inherited copy-and-paste in the
  original export. Both now describe themselves; `resources.html` gained a third
  breadcrumb level under Resources.
- Both pages carried two `og:description` tags with different text, the second
  being the other page's. The wrong one is gone from each.
- `library.html` was in neither `sitemap.xml` nor `llms.txt`, despite being the
  index for all sixty three blog posts. So was `partners.html`. Both added.
- `llms.txt` described `resources.html` as "Blog and resources" with the blog's
  own summary. Both entries now describe the page they point at.
- The orb tray had no Advisors entry, so `advisors.html` lit **Partners**
  instead. The tray list now mirrors the nav, and `KXHERE` is set correctly on
  `advisors.html`, `become-an-advisor.html`, `faq.html`, `glossary.html`,
  `tools.html` and `market-data.html`, which were empty or wrong.

### Advisors page

- The countdown stops at **00:15 MIN** rather than running to zero. The caption
  under it reads "Shortest session" instead of "Minimum required"; the body copy
  still says there is no minimum overall commitment, which is a different claim
  and still true.
- The hero's second sentence starts its own line. A `<br/>` would have done it
  at one width and left a two word orphan at every other, so the sentence is a
  block instead: it always begins on a new line and still wraps on its own
  terms. It sets no colour, so the hover gradient on the parent still clips
  through it.
- "Your role" is now "Your responsibilities". "Generate revenue" is now "Work
  from anywhere".

### Membership: the reserve note

The sentence under the tier cards was capped twice, at 60ch on the line and
62ch on the paragraph, which put it on four lines and made a footnote read as
a wall. Both caps lifted; the paragraph now runs to 960px and settles on two
lines at 1440. Phones are already narrower than the cap, so nothing changes
there.

The **Sign up for notifications** button warmed by one shade on hover, which
was easy to miss next to the three tier buttons above it. It now fills with the
gold gradient the site uses elsewhere, ink text on gold, with the same glow.
Contrast on hover is `#151000` on `#F3E4A8` to `#D4A856`. The rule covers
`:focus-visible` as well, so keyboard users get the same signal.

### Checked

Playwright, 14 pages, at 390x844 and 1440x900, scrolled to the bottom and back
so lazy sections had rendered.

- Six discs on every hub page, exactly one lit, `aria-current="page"` on it,
  computed rim `rgb(243, 228, 168)`, mouth opacity 1.
- Horizontal document overflow: 0 on every page at both widths.
- Text overlap, measured as intersecting rectangles of leaf text nodes covering
  more than 30% of the smaller box, ignoring fixed and sticky layers: 0 pairs on
  all six hub pages and on `advisors.html`, `events.html`, `how-it-works.html`
  and `partners.html`. What remains is the intentional crossfade on
  `index.html` and `membership.html`, plus wrapped inline links whose multi-line
  bounding boxes overlap by definition.
- Clock reads `00:15 MIN` at rest at both widths.

---

## 2026-09-03

### Repository cleaned out

Four files removed, about 11.3 MB. Each was checked for references across all
154 text files in the repository first; only the changelog mentioned any of
them.

- `server.js`, the backend source. It belongs in `sidekix-email-server`, which
  is what Render deploys, and the copy there was verified byte for byte
  identical before deleting this one. Vercel serves this repository statically,
  so it was publicly readable. No credentials in it, every key reads from
  `process.env`, but it did publish the honeypot field name, the rate limits and
  the CORS allowlist.
- `sidekix-site.zip`, 10.9 MB, the old WordPress export.
- `assets/img/3c4841d185f2.webp` and `assets/img/9640f533f3e5.webp`, the two
  superseded versions of the Advisors hero artwork.

The stray root-level `sitewide.css` was removed earlier the same day.

Left in place: the ten `assets/worksheets/*.txt` files. Nothing links to them,
but each one sits beside the PDF that is linked, so they read as the plain text
source rather than as cruft. All eleven linked worksheet PDFs are present and
accounted for.

### Wide-screen type scaling removed

An earlier version of `site-wide.css` raised the ceiling on 73 font-size,
padding and gap values by 1.45x above 1600px. Two problems.

It was too much: the membership hero went from 56px to 81.2px, which pushed it
from two lines to three.

Worse, it was a step rather than a scale-up. Each rule kept the vw growth rate
the page already used, and those rates had passed their old ceilings well
before 1600px — so crossing 1600px by a single pixel jumped that heading 31%
at once, 56px to 73.6px. All 73 rules shared the flaw.

The three `max-width` rules stay. Shells still widen from 1180px to 1560px and
stay centred, which is what actually fixed the site looking small on a wide
monitor. Type and spacing return to exactly what the pages define.

Verified at 2303px across 8 pages, 3,758 elements compared against the build
from before this stylesheet existed: zero differences in font-size,
line-height, padding or gap. `.wrap` still measures 1560px where the pages
alone give it 1180px.

`assets/site-wide.css`

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
