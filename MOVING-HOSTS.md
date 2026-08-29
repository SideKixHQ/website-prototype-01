# Moving to another host

The files do not change. This is a static site: HTML, CSS, fonts, one JS file.
Any host that serves files will serve it. What changes is a small amount of
host configuration, and one thing inside the files if the domain changes.

## The three things a host must do

**1. Serve `index.html` for a directory request.**
All 61 blog links point at `/blog/some-slug/`, not `/blog/some-slug/index.html`.
If the host does not resolve a directory to its `index.html`, every article 404s.
Almost every host does this by default. Worth testing one article first.

**2. Send `.woff2` as `font/woff2`.**
34 font files. If the MIME type is wrong the browser silently refuses them and
the whole site falls back to a system font. This is the most common thing that
breaks on a move and the easiest to miss, because nothing errors.

**3. Serve `404.html` for missing pages.**
The file is there; most hosts need to be told to use it.

Nothing else. No server-side code, no database, no forms posting anywhere, no
build step.

## Config files

`host-configs/` has a ready file for each common host. Copy the one you need to
the site root and delete the rest.

| Host | File |
|---|---|
| Apache, cPanel, most shared hosting | `.htaccess` |
| Netlify | `netlify.toml` |
| Vercel | `vercel.json` |
| Cloudflare Pages | `_headers` |
| Your own nginx server | `nginx.conf` (a server block, not a drop-in) |
| S3 + CloudFront | set the index document to `index.html` and the error document to `404.html` |

Each sets the directory index, the 404, correct MIME types, gzip, and caching:
a year on assets, ten minutes on HTML.

## If the domain changes

`https://sidekixhq.com` is written into every page, in the canonical link and
the Open Graph tags, and into `sitemap.xml`. If the site will live somewhere
else, run a find and replace across all 75 HTML files and the sitemap.

```bash
cd site
grep -rl "https://sidekixhq.com" . | xargs sed -i '' 's|https://sidekixhq.com|https://newdomain.com|g'   # macOS
grep -rl "https://sidekixhq.com" . | xargs sed -i    's|https://sidekixhq.com|https://newdomain.com|g'   # Linux
```

If the domain is staying the same, change nothing.

## Files you can delete on a non-GitHub host

- `.nojekyll` is only meaningful to GitHub Pages. Harmless anywhere else.

Keep `robots.txt` and `sitemap.xml` wherever you go.

## After the move, check these five

1. An article loads: `/blog/how-to-price-your-product-or-service/`
2. Fonts render as the serif, not a system fallback (check the big headings)
3. A made-up URL shows your 404 page, not the host's
4. The PDFs download: `/assets/worksheets/sidekix-business-glossary.pdf`
5. `https://` is forced and `www` resolves to the same place
