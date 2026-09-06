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
])


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
