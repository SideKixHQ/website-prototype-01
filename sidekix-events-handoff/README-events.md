# SideKix events page: engineer handoff

Everything the events page needs to run and to keep refreshing itself.
Repository of record: https://github.com/SideKixHQ/website-prototype-01

## What is in this bundle

| File | Role |
|---|---|
| `events.html` | The page. Plain HTML, all CSS and JS inline, no build step. |
| `events.json` | The event data the page renders. Generated, not hand edited. |
| `pinned.json` | Hand added events. Always merged in, never overwritten by the scraper. |
| `sources.json` | The 108 sources the scraper reads, with a parser name per source. |
| `scrape_events.py` | Reads `sources.json`, merges `pinned.json`, writes `events.json`. |
| `build_events_seo.py` | Rewrites parts of `events.html`, plus `sitemap.xml` and `llms.txt`. |
| `selftest.py` | Offline checks on the pipeline. Exit code 0 or 1, so it fits in CI. |
| `requirements.txt` | requests, beautifulsoup4, python-dateutil. |
| `refresh-events.yml` | The GitHub Action. Belongs at `.github/workflows/refresh-events.yml`. |
| `assets/` | The three images `events.html` references. |

## How the page gets its data

`events.html` fetches `events.json` at runtime and draws the cards in the
browser. There is no server and no framework.

Because a crawler that does not run scripts would see an empty page,
`build_events_seo.py` also writes the next 60 events into the HTML as a plain
list, between the markers `<!-- kx:seo:start -->` and `<!-- kx:seo:end -->`,
with Event structured data beside it. When the JSON loads, the grid replaces
that list. When it does not, the plain list stays up.

### Opening the file directly shows the plain list, not the cards

A `file://` page cannot fetch `events.json`, so the fallback list is what
renders. This is the page working as designed rather than a fault. Serving the
folder over HTTP shows the real page:

    python3 -m http.server 8000
    # then open http://127.0.0.1:8000/events.html

## The data contract

`events.json`:

```json
{ "updated": "2026-09-01", "note": "...", "events": [ ... ] }
```

Each event, with every field a string:

```json
{
  "title":    "Start Smart: Starting A Business in Kentucky",
  "host":     "Kentucky SBDC",
  "start":    "2026-09-01T23:00:00-04:00",
  "duration": "",
  "topic":    "Business",
  "url":      "https://...",
  "summary":  "...",
  "category": "Company",
  "scope":    "National",
  "mode":     "",
  "host_topic": "",
  "cost":     "",
  "location": ""
}
```

`start` is ISO 8601 with an offset. `topic` drives the colored chips.
`mode` is one of online, livestream, in person, or empty. `cost` and
`location` are shown verbatim on the card, so an empty value renders as
"Check with host" rather than an assumption.

`pinned.json` uses the same field names and is merged on every run.

## Running the pipeline

    pip install -r requirements.txt

    python scrape_events.py --probe        # what every source returns, writes nothing
    python scrape_events.py --dry-run      # what it would write
    python scrape_events.py                # write events.json
    python build_events_seo.py             # rewrite the page, sitemap and llms.txt
    python selftest.py                     # offline checks

Other flags on the scraper: `--min-events N` (default 5) and `--allow-shrink`,
which permits a write that produces fewer events than the published file.

`--probe` run from the Action rather than a laptop is what catches a source
that works locally and returns 403 from a CI runner, since the runner IP and
headers are what the weekly job actually uses.

## The weekly refresh

`.github/workflows/refresh-events.yml` runs `0 11 * * 1`, Mondays at 11:00 UTC,
and can be dispatched by hand with two inputs: `mode` (refresh or probe) and
`allow_shrink`. On a refresh it scrapes, rebuilds the page, then commits
`events.json`, `events.html`, `sitemap.xml`, `llms.txt` and `assets` under the
identity `events-bot`, rebasing before the push so a concurrent edit does not
lose the run.

Consequence for anyone editing `events.html` by hand: the file has an automated
writer. A local copy goes stale every Monday.

## Editing the page safely

`build_events_seo.py` patches specific regions rather than regenerating the
file, so hand edits outside those regions survive. Verified against the current
header and footer change: the builder reported 16 patches applied and left the
navigation, the link row and the footer untouched.

Regions the builder owns:

- the `<title>` and meta description
- the Open Graph and Twitter tags
- the block between `<!-- kx:seo:start -->` and `<!-- kx:seo:end -->`
- the block between `<!-- kx:browser:start -->` and `<!-- kx:browser:end -->`
- the card template and card helpers
- the JSON-LD structured data

Suggested action: run `python selftest.py`, then `python build_events_seo.py`
against a copy, and diff the result before any hand edit lands on `main`.

## Shared shell

The header, the navigation link row and the footer are shared with the other
site pages. They live inline in every page rather than in a partial, so a
change to the shell is a change to 15 files. The blocks that govern the bar
carry ids: `kx-mainnav`, `kx-mainnav-hover`, `kx-mainnav-current`,
`kx-mainnav-states`, `kx-mainnav-final`, `kx-bar-clean`, `kx-nav-stack`, and
the script `kx-mainnav-js`.
