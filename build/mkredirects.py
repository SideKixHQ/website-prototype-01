# -*- coding: utf-8 -*-
"""Keep vercel.json redirects in step with what is on disk.

The site moved off WordPress and every top-level page gained a .html
extension, so every URL Google had indexed started returning 404, including
/advisors, which was ranking. These redirects hand the old shapes to the new
files so the ranking history and any inbound links survive.

Legacy slugs are listed by hand because only a person knows that /company and
/about-us both meant the how-it-works page. Everything else is derived.
"""
import collections, glob, json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LEGACY = collections.OrderedDict([
    ("about-us",             "/how-it-works.html"),
    ("about",                "/how-it-works.html"),
    ("company",              "/how-it-works.html"),
    ("our-story",            "/how-it-works.html"),
    ("contact",              "/faq.html"),
    ("contact-us",           "/faq.html"),
    ("support",              "/faq.html"),
    ("careers",              "/become-an-advisor.html"),
    ("jobs",                 "/become-an-advisor.html"),
    ("privacy-policy",       "/privacy.html"),
    ("app-terms-conditions", "/terms.html"),
    ("terms-conditions",     "/terms.html"),
    ("terms-and-conditions", "/terms.html"),
    ("terms-of-service",     "/terms.html"),
    ("cookie-policy",        "/cookies.html"),
    ("blog",                 "/library.html"),
    ("posts",                "/library.html"),
    ("articles",             "/library.html"),
    ("resources",            "/resources.html"),
    ("pricing",              "/membership.html"),
    ("plans",                "/membership.html"),
    ("get-started",          "/join.html"),
    ("signup",               "/join.html"),
    ("sign-up",              "/join.html"),
    ("home",                 "/"),
    ("sponsors",             "/partners.html"),
    ("opt-in-accept",        "/join.html"),
    # Still carrying internal links in Google's view of the old site, 69 each
    ("advisor-faqs",         "/faq.html"),
    ("general-faq",          "/faq.html"),
    ("members",              "/membership.html"),
    ("website-terms-conditions", "/terms.html"),
    ("ai-app-policy",        "/terms.html"),
])

# Wildcards, for URL shapes rather than single pages. Search Console's
# "Not found (404)" report named all of these as live 404s with crawl history.
#
# /wp-content is deliberately absent: those are deleted media files, and a
# 404 is the honest answer for a deleted image. Redirecting them to a page
# would turn 13 clean 404s into soft 404s, which is worse.
# ":slug*" does not match once trailingSlash has put a slash on the end, which
# is why the first attempt at these still 404ed. The explicit "(.*)" form
# matches the remainder of the path whatever it looks like.
#
# Order matters: Vercel takes the first source that matches, so the one exact
# post mapping has to sit above the catch all for its own directory.
PATTERNS = [
    # WordPress tag and category archives. The library is the list of posts
    # they used to be.
    ("/tag/:slug(.*)",      "/library.html"),
    ("/category/:slug(.*)", "/library.html"),
    # The Wix era put posts under /blog/f/. This one is a clear match for a
    # post that still exists; the rest go to the library rather than to a guess.
    ("/blog/f/great-you-have-an-idea-no-what",
     "/blog/what-to-do-after-having-your-business-idea/"),
    ("/blog/f/great-you-have-an-idea-no-what/",
     "/blog/what-to-do-after-having-your-business-idea/"),
    ("/blog/f/:slug(.*)",   "/library.html"),
    # Wix mobile routes
    ("/m/:path(.*)",        "/"),
]


def main():
    path = os.path.join(ROOT, "vercel.json")
    cfg = json.load(open(path))

    pages = sorted(os.path.basename(p)[:-5] for p in glob.glob(os.path.join(ROOT, "*.html")))
    pages = [p for p in pages if p not in ("404", "index")]

    red, seen = [], set()

    def add(src, dest):
        if src in seen:
            return
        seen.add(src)
        red.append({"source": src, "destination": dest, "permanent": True})

    for slug, dest in LEGACY.items():
        add("/" + slug, dest)
        add("/" + slug + "/", dest)

    # Patterns Search Console reported as 404 that a per page list cannot
    # cover. Tag archives and the old Wix blog shape both held many URLs.
    for src, dest in PATTERNS:
        add(src, dest)
    for p in pages:
        add("/" + p, "/%s.html" % p)
        add("/" + p + "/", "/%s.html" % p)
    add("/index", "/")
    add("/index.html", "/")

    missing = [r["destination"] for r in red
               if r["destination"] != "/"
               and not os.path.exists(os.path.join(ROOT, r["destination"].lstrip("/")))]
    if missing:
        raise SystemExit("redirect targets that do not exist: %s" % sorted(set(missing)))

    cfg["redirects"] = red
    with open(path, "w") as fh:
        json.dump(cfg, fh, indent=2)
        fh.write("\n")
    print("vercel.json: %d redirects covering %d pages and %d legacy slugs"
          % (len(red), len(pages), len(LEGACY)))


if __name__ == "__main__":
    main()
