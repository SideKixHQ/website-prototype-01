# SideKix

Static site. No build step, no dependencies. Open `index.html` and it runs.

## Structure

```
index.html              home (React app, see note below)
how-it-works.html       membership.html      become-an-advisor.html
join.html               resources.html       market-data.html
glossary.html           tools.html           faq.html
terms.html              privacy.html         404.html

blog/<slug>/index.html  62 articles, folder name = URL slug
assets/                 css, js, fonts, images, worksheet PDFs
sitemap.xml  robots.txt  favicon.ico  .nojekyll
```

## Deploying to GitHub Pages

Push the **contents** of this folder to the repo root, so `index.html` sits at
the top level. `.nojekyll` is already here, which stops GitHub running Jekyll
over the files. Every path is relative, so it works from a user page or a
project subpath.

## Editing

Most pages are hand-written HTML with their CSS in a `<style>` block in the
head. Blog articles share `assets/article.css` and `assets/article.js`.

Two things to know before you change styling:

**Class names collide with the theme.** `.view`, `.hero`, `.rail`, `.dots`,
`.eyebrow` and others already mean something. Before adding a class, search the
file for it. A collision here is invisible until something disappears.

**Later rules win.** Several pages carry many `<style>` blocks added over time,
so the same selector can be set more than once. If a change appears to do
nothing, check whether a later rule overrides it rather than adding `!important`.

## Accessibility

The site passes WCAG 2.1 AA on the checks that can be automated: labels,
landmarks, headings, contrast, focus order, keyboard operation, reduced motion.
If you add UI, the things most easily broken are:

- text on a coloured button needs its colour set explicitly, or it inherits
- decorative SVGs need `aria-hidden="true"`
- a symbol inside a labelled button needs `aria-hidden` so it is not read out
- every `<nav>` needs its own `aria-label` when there is more than one

## Known items

- `index.html` is a React app. Editing its static markup has no effect; the
  bundle replaces the DOM on load.
- Two images still point at `sidekixhq.com/wp-content/` and will break when
  WordPress goes away: the coin on `make-money-online-without-feeling-lost` and
  a panel on `90-percent-of-americans-want-to-be-their-own-boss`.
- 31 blog titles run over 62 characters and will truncate in search results.
- The App Store link and the form endpoint are placeholders.
