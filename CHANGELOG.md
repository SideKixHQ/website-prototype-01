# Changelog

A record of what changed on the SideKix site, why, and how each change was
checked. Written because the repository history is a run of "Add files via
upload" commits, which say nothing about intent.

All measurements below were taken with Playwright against a local copy of the
site, comparing the build before the change with the build after it.

---

## 2026-09-11

### Homegrown navigates by rail, and moves

The page had three tries at navigation before this one, and the last was wrong
on its own terms: four steps presented as tabs, under a heading that read "Four
steps. Pick one." Tabs are for alternatives. The four steps are a sequence, so
there was nothing to pick. The tab interface is gone; the four steps are now one
lead line in "What we do".

In its place the page runs on a sticky section rail. Six sections, numbered,
down the left at 1024px and wider, collapsing to a horizontal scroll strip above
the content below 900px. The rail marks the section you are in as you scroll,
so the page always answers "where am I" without being asked.

The rail's active section is picked deterministically rather than by observer
callback order: on each rAF-throttled scroll the code takes the last section
whose top has crossed a line 34% down the viewport. That gives one answer for
any scroll position, including the ones where two sections are on screen at
once. Checked at 390, 900 and 1280px: all six sections track.

Movement, because a page this long reads better when it responds to being read.
Sections rise in with a stagger. The four diagrams draw themselves, strokes
first by dashoffset, then labels fading in 26ms apart, then the growth bars
scaling out from their left edge. The stat numbers count up on a cubic ease-out
over 1100ms and land exactly on their value, not near it.

All of it is authored finished-state-first. The CSS default is the arrived
state; JavaScript adds a class that opts elements into starting somewhere else.
So the page with JavaScript off, and the page under prefers-reduced-motion,
both render complete and static. Verified all three ways: 0 elements left
stranded under 90% opacity in any of them, and the counters read their final
values in every case.

CSS scroll-driven animation would have been the lighter tool here, but it sits
around 84% support with Firefox still behind a flag, so this uses
IntersectionObserver.

Also raised the rail's section numbers from #5A554D to #85806F. At 10px they
need 4.5:1 and were sitting at 2.76:1 against the page ground; they now measure
5.1:1. Found by `audit/contrast3.js`, which was the only finding on the page
across the whole suite (wcag, wcag2, pour, seo, mobile, contrast3).

### Homegrown gets one spacing scale, and five behaviors an employer reads

Measured every vertical gap on the page. The section frame was disciplined,
16px eyebrow to heading and 34px below the rule in all six sections, but
everything under that rule was hand tuned: gaps ran 6, 16, 18, 22, 26, 28, 30,
32 and 34px, four of them set inline on single paragraphs. In "What we do" a
509px diagram was followed 6px later by a list, because `figure` carried no
bottom margin and `ul.plain` opened with 6px.

There are now three steps, as tokens on `.hg`: 16px inside a unit, 26px between
blocks, 34px around a full-width object. Every block margin reads from them and
the four inline margins are gone, carried instead by the block above each
paragraph. Gaps on the page now measure 16, 26 or 34, nothing else.

Two structural fixes came out of the same measurement. The shell sets
`main > section:first-of-type{padding-top:132px !important}`; the hero here is a
`<header>`, so that landed on the opening diagram instead. The diagram floated
188px below the hero and sat 34px above the first section, the reverse of what
it should be. It now opens at 48px and closes with a full section break, 102px
at 1280 and 64px at 390, matching the section rhythm exactly.

Separately, the five reported behaviors were all career self-management. They
served the resident navigating their own path and gave an employer nothing to
hire on, which matters because the employer is who the report goes to. The five
are now built on the individual-contributor end of the Leadership Architect
set: self-development, resourcefulness, decision quality, action orientation and
drives results. None of Korn Ferry's competency names are used, as the library
is licensed. Each still names an act somebody can be watched doing, and the list
now reads twice, as a growth plan and as a hiring profile. "Finds out" is gone;
it was a bare verb with no object.

Checked: all six rail sections track at 390, 900 and 1280px, counters land on
value, nothing stranded invisible with JavaScript on, off or under reduced
motion, no console errors, no horizontal page overflow, and the longest new
diagram label clears the viewBox edge by 100px. wcag, wcag2, pour, mobile and
contrast3 report nothing on this page.

One pre-existing finding left alone: the three chrome images the generator
injects carry inline CSS dimensions but no width/height attributes, which
`audit/seo.js` counts as layout shift. It predates this work and affects both
generated pages, so it belongs to `build/_chrome.html` and a pass of its own.

---

## 2026-09-10

### A jobs map, as a pipeline rather than a picture

`build/mkjobsmap.py` and `build/mkjobspage.py` build a map of where the jobs are
against where the workers live, for any set of US counties, from free federal
data: LEHD LODES for jobs, resident workers and commute flows, TIGERweb for
tract geometry. Blocks aggregate to tracts, flows aggregate to county pairs, and
the whole region comes out as one JSON file the page renders inline. No basemap
tiles, so no API key, no tile bill, no attribution constraint, and the thing
looks like the rest of the site instead of looking like Google.

The map draws one number per tract, jobs minus employed residents, which is a
polarity rather than a magnitude. So the scale is diverging: two hues either
side of a neutral grey midpoint, seven steps, no rainbow. The midpoint recedes
so tracts furthest out of balance carry the most weight, which is the point of
the map. Every step was checked rather than eyeballed: all seven clear 3:1 on
the panel ground, and lightness rises monotonically outward from the midpoint on
both sides. The categorical validator was run too and flagged the grey midpoint
and the pole lightness, which are the two things a diverging ramp is supposed to
do; its own scope note says it covers categorical palettes.

Tract hover and keyboard focus both raise a tooltip with jobs, resident workers
and the net, every tract is focusable, and the full table sits under a details
element so the map is not the only way to read it.

Neither the data file nor the page is committed. The sandbox this was written in
has no route to census.gov: the egress proxy denies it, over curl and over
fetch. So the pipeline was verified end to end against a synthetic fixture, 120
tracts through projection, colour assignment, hover and layout, and the fixture
and the page built from it were deleted rather than shipped. Running the two
commands anywhere with outbound access produces the real thing. Nothing invented
is in the repository.

### Homegrown scores named competencies, and the caveat says something

The five things the program scores were plain-language coinages, self starting,
opportunity spotting, obstacle anticipation, asking, follow through. They now
carry the competency names an L and D reader will recognise: action oriented,
resourcefulness, plans and aligns, courage, ensures accountability. Each still
sits beside a plain observable in the list underneath, so the label carries
weight with an evaluator and the sentence next to it carries meaning for
everyone else.

Worth recording, since it constrains what the page can say: the Leadership
Architect framework these names come from is Korn Ferry intellectual property,
descended from Lominger, licensed rather than public. The words themselves are
ordinary English and most predate the framework, so using them is fine. Naming
Lominger or Korn Ferry on the page, reproducing their definitions, or presenting
this as their instrument would not be, absent a licence. The page therefore uses
the terminology and defines it in SideKix's own words, and attributes nothing.

"Teaching people things does not work" is the line the argument turns on and was
set like any other heading. It now carries a gold marker that sits as a thin
underline at rest and sweeps up into a full highlight on hover. Rest state
matters more than the hover here: it is what a screenshot and a phone get, since
touch never hovers, so devices reporting `hover: none` are given the full
highlight outright and reduced-motion drops the transition.

The caveat about the trial was unreadable. It opened "Said plainly, because
someone should ask", named Lome, which means nothing to a reader who was never
told the trial was in Togo, and referred to "that trial" when the tile above had
not said where it ran. The tile now says West Africa and the caveat is four
plain sentences. It stays on the page: the thirty and fifty two per cent figures
are the strongest claim here, the audience includes people who will look the
study up, and quoting the gains while dropping the limits is the kind of thing
that ends a procurement conversation.

What a town gets now includes platform access for everybody in the cohort: the
community, the resource library, the self discoveries, events, training and AI
guidance. The eight weeks end and that does not, which is the answer to what
happens in month five.

Checked: `wcag`, `wcag2`, `pour`, `mobile` and `contrast3` clean, including the
cream heading over the new marker. No console errors. The longest competency
label, ensures accountability, measures 176px inside a 305px zone, so nothing
overflows the diagram.

### Homegrown rewritten: shorter, specific, and finally in alignment

The page said what it did in the abstract and buried the part that is actually
distinctive. It now leads with the method. After the opening diagram the second
section is "Five areas of work. Five behaviors we score.", which names the work
in plain words, behavior, skills, career development, personal development and
leadership, and then separates what gets taught from what gets reported. You
cannot audit a topic. You can watch a person do a thing.

The hero was rewritten. The old headline made a claim without saying what the
program is; the new deck says it in three sentences and ends on the deliverable,
a list of who is ready, for what, and by when.

Length came down from 3,181 words to 2,476, and from 3,181 to 1,836 for what a
reader actually faces, because the twelve sources and the five questions now sit
inside collapsed `details` rather than running down the page. The evidence
section lost four paragraphs of prose and became three figures, which is what
anyone was going to take from it anyway.

Two real alignment bugs, both mine.

The page had three horizontal axes. The hero and the figure captions centred on
620, the full width rows centred on 620, and the prose ran 84 to 831, centring
on 457, because `.hg p` capped at 68ch with no auto margins. Everything in the
reading column now shares one width, and the width is set in rem rather than ch:
`ch` resolves against each element's own font, so an `h2` at 70ch was far wider
than a `p` at 70ch and their left edges never lined up. Two bands now, 236 to
1004 for text and 84 to 1156 for diagrams, stat rows, cards and the table, both
centred on the same axis.

The call to action block was a class collision. The shell defines `.cta` as an
inline-block button; the section reused the name, inherited `display:inline-block`
and shrink-wrapped to 891px against the 1072px it should have filled, sitting
left of centre. Renamed to `.hgcta`. Namespacing by prefix rather than by
out-specifying a shell rule is the fix.

Checked: `wcag`, `wcag2`, `pour`, `mobile` and `contrast3` clean, no console
errors, no horizontal overflow at 390px, and the reading column and the full
width band both measured back to a common centre.

### Homegrown opens on the diagram, gains a growth model, and loses its dashes

Three changes, all from review.

The loop diagram now sits directly under the hero rather than after the opening
argument. It is the thesis of the page, and making a reader work through five
paragraphs of prose to reach it wasted it. Its caption was rewritten to stand on
its own, since it no longer has the argument above it to lean on. The first
section on this page also overrides the shell's 132px of top padding down to
about 58px: that default is right for a section that opens with a heading and
wrong for one that opens with a full width figure, which it stranded behind a
screen of black.

A third diagram was added, because neither of the first two showed what the
program actually changes in a person. One shows the system, the other shows the
mechanics. The new one names five behaviors, self starting, opportunity
spotting, obstacle anticipation, asking and follow through, and shows each of
them growing across the same four stages, from named to practiced to applied to
habitual. The caption says plainly that it is the design of the program and not
a plot of measured results, because a chart of bars will otherwise be read as
data. The five behaviors are also written out under it as observable
indicators, which is what makes the day 180 score mean anything.

Every em and en dash on the page is gone, per house style. They were reworded
rather than swapped for another mark: sentences split at full stops, lists took
colons, and the four phase headings read "Begin: where you actually are" and so
on. Week ranges are "Weeks 1 to 2". The two SVG descriptions used hyphens the
same way and were rewritten too. Worth noting for a later pass: `index.html`
carries 17 em dashes and `membership.html` 23, so the rule is not yet applied
site wide.

Checked: `wcag`, `wcag2`, `pour`, `mobile` and `contrast3` clean for the page,
no console errors, and all three download controls produce PNGs at 1800x1040,
2000x940 and 1960x820. Two spelling slips were caught before shipping, since the
new diagram had been written in British English against a site that uses
American.

### The body font was never loading on any page

`assets/fonts.css` declared Poppins five times and EA Majer once, and every one
of those rules had the family name interpolated into its own filename with the
quotes left in, so each `src` pointed at a file that does not exist and never
did. Nothing in `assets/` matched. `document.fonts` held no Poppins entry on any
page, and because `--body` is `'Poppins',system-ui,sans-serif`, every page on
the site has been rendering its body text in `system-ui`.

Poppins is now self-hosted the way Cormorant Garamond and Space Grotesk already
were: latin and latin-ext subsets at 400, 500, 600, 700 and 800, ten woff2 files
totalling about 120KB, with the unicode ranges Google publishes. Devanagari was
skipped, being roughly 60KB per weight and unused. The EA Majer rule was deleted
rather than repaired: no file, and no reference to it anywhere in the shell.

The weights were chosen from what the built pages actually ask for: 600 leads at
344 uses, then 700, 800, 500 and 400.

Checked: Poppins 400 through 800 report `loaded` on `index.html`,
`membership.html` and `homegrown.html`, `document.fonts.check` passes, and no
font request fails. Restoring a real font changes text metrics on every page, so
fifteen pages were measured for horizontal overflow at 390px and 1240px, and
none has any. A before and after of `membership.html` shows the layout holding
with the correct letterforms.

### SideKix Homegrown, an offering page for towns and counties

Two economic development directors, for Wilmington and for Leland, asked for
help with career development. `homegrown.html` is the offering that answers
that ask, and it is the first page on the site written to be sold rather than
read.

The argument it makes is that the three things an economic development office
is asked for, attracting business, growing the industries already here and
getting residents into the work, are one problem rather than three, and that
the missing asset is a named, tracked bench of local residents. The program
underneath it, Next Move, is eight weeks plus ninety days of follow through,
built on personal initiative rather than curriculum, with four exits so that a
credential handoff to the community college counts as a success rather than a
loss.

Two diagrams carry the argument, because the page also has to work projected in
a meeting. Both are inline SVG on the site palette, and both have a download
control that rasterises them at 2x onto the dark ground for use in a deck. The
export injects its own copy of the type rules, since a serialised SVG does not
carry the page stylesheet with it.

Every figure on the page is sourced, with the date checked, in the last section.
One claim about the share of US businesses with no employees was cut rather than
shipped, because the SBA Advocacy source could not be reached to verify the
exact figure and the page promises that every number is listed. The Togo trial
that the method leans on is quoted with its limits stated on the page, including
that the seven-year gains were concentrated among men, on the view that an
evaluator will find that out anyway and it is better to say it first.

Checked: `wcag`, `wcag2`, `pour`, `mobile`, `navclear` and `contrast3` all clean
for the page. No console or page errors. No horizontal overflow at 390px. Both
download controls produce PNGs, 1800x1040 and 1960x820. Three things were fixed
during the build rather than shipped: the title and meta description were over
the SEO audit's limits; the first section carried the section rhythm on top of
the 132px of top padding the shell already gives it, which double-spaced the
page under the hero, and every other page on the site sets that margin to zero;
and the colour fallback on the exit card tags was `--gold-mid`, which measures
3.55:1 on the card fill against the 4.5 needed. The rendered tags were never
affected, since they carry their own colour, but the fallback is now `#CDAA63`
at 5.69:1.

The diagram export embeds the fonts. A serialised SVG in a data URI cannot
reach `assets/fonts.css`, so the first version of the export rasterised on
system fallbacks. It now reads the faces the page already loaded out of the
CSSOM, fetches the basic-latin subsets and inlines them as data URIs, with any
failure falling back to the previous behaviour. Two things had to be corrected
to make it work: browsers serialise that subset's range as `U+0-FF` rather than
`U+0000-00FF`, and the weights asked for did not match the weights the diagrams
actually use.

Doing that surfaced a separate, pre-existing bug that is worth fixing on its
own. Every `@font-face` for Poppins and EA Majer in `assets/fonts.css` has a
malformed `src`, `url(""Poppins"-ec1e9eca.ttf")`, with the family name
interpolated into the filename and its quotes left in. No matching file exists
in `assets/` either. `document.fonts` holds no Poppins entry on `index.html`
any more than on this page, so the body font across the whole site is silently
falling back to `system-ui`. Not touched here, because it affects every page and
is not this change's to make.

`sitemap.xml` and `llms.txt` carry the page. The sitemap entry was added by
hand rather than by rerunning `build/mksitemap.py`, which wanted to add four
unrelated transactional pages and rewrite every `lastmod` from checkout
timestamps.

### The self test was failing on three assertions that the code had outgrown

`selftest.py` returned 48 passed, 5 failed. Three of the failures were the
suite disagreeing with changes made on purpose:

`ALLOW_INPERSON` is `True` and `events.html` carries an "In person" filter, but
section 1 still expected a room only 1 Million Cups to be dropped, and the SBA
parser test still expected one row out of two. Both now expect the event kept.
Section 2 already exercises the switch in both positions, so the coverage that
mattered was never lost.

`BIGEVENT` was narrowed to gala, fundraiser and fundraising dinner, so
conferences pass the filter. The "a conference" case expected a rejection.
It now expects the event kept, and two new cases hold the line that `BIGEVENT`
still guards: a gala and a fundraiser are both dropped.

53 passed, 2 failed after the change. The two that remain are the banned word
and dash rules running against scraped titles written by other organizations,
which is a rule the data cannot satisfy. Left red on purpose rather than
quietly weakened.

### Past events are no longer shipped to every visitor

`keep()` drops anything already past at scrape time, but the file is written
weekly and rows expire between runs. Three days after the 2026-09-07 refresh,
79 of 860 events had already happened. The page hid them, and every visitor
still downloaded them.

`scrape_events.py --prune` rewrites `events.json` with the past rows removed
and changes nothing else, so it can run on any cadence. Run once against the
current file: 860 events to 781, 519KB to 460KB. The shrink guard in `main()`
already compares against upcoming events in the existing file rather than the
total, so a pruned file does not make the next scrape refuse to write.

Checked: `--prune` a second time is a clean no op. The page renders 756
upcoming, filters by format, cost and state, and the "SHOW 60 MORE" control
pages through the set. No console errors, one h1, no horizontal overflow at
390px. All seven conference rows survived the prune.


## 2026-09-05

### Tools

**A section that was four calculators is now fifteen pages.** `tools.html` is
the hub, reached from the Tools orb on every Resources page, and it links four
calculators, a fifty state filing lookup, a structure comparison, a domain
checker, a founder diagnostic, two generators and four fillable worksheets.
One page per tool, each with its own title, description, breadcrumbs and
`WebApplication` schema, all wired into `sitemap.xml` and `llms.txt`.

The state data is `build/state-filings.json`: 50 states with the filing office,
the document name, the fee, the name search, the registered agent rule and the
report cadence, each with the government page it came from. Two states, New
Mexico and Tennessee, have no confirmed LLC fee and the page says so rather
than printing a number nobody checked.

**Nine of the pages had a JavaScript error that killed them.** The generator
wrapped page scripts in `try { ... } catch` but not in a function, so a
top-level `return` inside the page's own code was a syntax error and the whole
block never ran. On `founder-diagnostic.html` that meant the questions did not
advance; on the worksheets nothing saved. `build/toolgen.py` now emits an
IIFE inside the `try`, and the pages were regenerated rather than patched.

Checked: every calculator computes, `?state=Texas` deep-links and shows $300,
the worksheets survive a reload with their progress meters intact, and the
domain checker reports "no answer" rather than "available" when the registry
cannot be reached.

### Fonts

**Three pages were never loading the site's fonts.** `advisors.html`,
`partners.html` and `events.html` had the Google preconnect hints but no
`fonts.css` stylesheet, so they rendered in Georgia and system-ui while every
other page used Cormorant Garamond and Space Grotesk. On partners the hero
copy block sits outside `.wrap.res.prt`, so `.prt h1` never matched it either:
the heading was 32px of the body font where advisors is 66px of the display
serif. Both fixed, and the hero eyebrow and lede now take the same rules as
the rest of the page.

**The font swap was the largest source of layout shift on the site.** Every
face is `font-display: swap` and the files are only discovered once `fonts.css`
parses, so the fallback painted first and the page reflowed when the real font
arrived. Measured on a phone: state-filing 0.7063, startup-checklist 0.1186,
business-structures 0.1070, library 0.0915 on desktop. Blocking the woff2 files
dropped those to 0.0578, 0.0049, 0 and 0, which identified the cause.

Six `rel="preload"` hints for the Latin subsets now sit in every page head,
ahead of the stylesheet. Same bytes, earlier in the queue, and the request
chain is gone. Every page measured after the change: 0.0000 at 1440 and 390,
including all fifteen tool pages.

### Cleanup

Six image plates left over from earlier hero work, 2.5 MB, no longer referenced
by any page: removed. `__pycache__` added to `.gitignore`. Tap targets under
24px on a phone (worksheet checkboxes, the numbered source links on the state
page, the reference links on the structures page) brought up to size. Seven
meta descriptions were over 165 characters and were rewritten shorter.

Checked afterwards: 32 pages at 1440 and 390, no horizontal overflow, exactly
one `h1` each, no console errors and no failed requests.

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
