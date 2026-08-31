# SideKix static site

77 pages. No build step: every page is plain HTML with its CSS and JavaScript
inline, so the repository is the deployable artifact.

## Deploying

### GitHub Pages
1. Push this repository to GitHub.
2. Settings, then Pages.
3. Source: Deploy from a branch. Branch: `main`, folder: `/ (root)`.
4. Add your domain under Custom domain, and create the DNS records GitHub
   shows you.

`.nojekyll` is included so Pages serves the files as they are rather than
running them through Jekyll.

### Netlify, Vercel, Cloudflare Pages
Point the project at this repository. There is no build command and no output
directory; publish the root.

Host-specific header and redirect files are in `host-configs/` if you want
caching and security headers set up. Copy the one for your host into the root.

## The events page

`events.html` reads `events.json`. That file is refreshed by
`scrape_events.py`, which checks 47 public sources for online business events
that cost nothing to attend.

### Running it

    pip install -r requirements.txt
    python scrape_events.py --probe      # which sources respond, and with what
    python scrape_events.py --dry-run    # what it would write, without writing
    python scrape_events.py              # write events.json

`--probe` is worth running first. Several of the 47 sources have never been
reached from the environment this was built in, so some URLs will need
correcting. The probe tells you which.

### On a schedule
`.github/workflows/refresh-events.yml` runs the scraper every Monday at 11:00
UTC and commits `events.json` only if it changed. You can also run it by hand
from the Actions tab with Run workflow.

The scraper refuses to write a file with fewer events than the current one,
which stops a bad run from emptying the page. Override with `--allow-shrink`.

### Pinning an event
`pinned.json` is for events you want on the page regardless of what the
scrapers return. It is currently empty.

## Tests

    python selftest.py

37 checks covering the scraper's filters, both parsers, the safety rail, the
data schema and the page's own elements. Exits non-zero on failure, so it can
gate a deploy.

## Layout

    *.html                  the 14 main pages
    blog/                   62 articles, one folder each
    assets/                 fonts and images
    host-configs/           headers and redirects per host
    .github/workflows/      the weekly events refresh
    scrape_events.py        the events scraper
    selftest.py             the test suite
    events.json             the current events, written by the scraper
    pinned.json             events pinned by hand
    robots.txt              15 AI crawlers named, nothing disallowed
    llms.txt                a plain-text summary for language models
    sitemap.xml             75 URLs

## Things left open

- The 47 scraper sources have not been reached from a real network yet. Run
  `--probe` and expect to correct some URLs.
- `events.json` holds 17 events from five sources. The rest arrive on the
  first successful run.
- The partnership form and the waitlist form both open a prefilled email,
  because there is no backend. Point them at an endpoint when you have one.
- The falling-star promo on the homepage generates a code that nothing
  downstream can receive. `join.html` has no referral field.
- Every page carries a build stamp on line 2, which is useful when checking
  whether a browser is showing a cached copy.
