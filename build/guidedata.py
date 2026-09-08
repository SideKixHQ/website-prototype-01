# -*- coding: utf-8 -*-
"""The industry corpus, loaded once and presented in one shape.

Four research batches were compiled at different times and did not agree on
field names, so build/industry/*.json is normalised on the way in rather than
in twenty places downstream. Nothing here invents a value: a business with no
published startup cost arrives with None and the page says so.
"""
import io, json, glob, os, re, collections

HERE = os.path.dirname(os.path.abspath(__file__))

# Slug to display name. Everything else title-cases from the slug, but an
# acronym does not survive that, and "Ai consulting" would be the tell.
DISPLAY = {
    "ai-consulting-business": "AI consulting business",
    "ev-charging-business": "EV charging business",
    "social-media-marketing-agency": "social media marketing agency",
    "online-store-business": "online store",
    "med-spa-business": "med spa",
    "food-truck-business": "food truck business",
    "coffee-shop-business": "coffee shop",
    "bakery-business": "bakery",
    "pet-daycare-business": "pet daycare business",
    "home-care-business": "home care business",
    "mobile-car-detailing-business": "mobile car detailing business",
}

# What a reader is really choosing between, used to group the hub table.
GROUP = {
    "cleaning-business": "Services you can start from a van",
    "lawn-care-business": "Services you can start from a van",
    "mobile-car-detailing-business": "Services you can start from a van",
    "handyman-business": "Services you can start from a van",
    "pressure-washing-business": "Services you can start from a van",
    "food-truck-business": "Food",
    "bakery-business": "Food",
    "coffee-shop-business": "Food",
    "catering-business": "Food",
    "meal-prep-business": "Food",
    "bookkeeping-business": "Work you can do from a desk",
    "consulting-business": "Work you can do from a desk",
    "ai-consulting-business": "Work you can do from a desk",
    "online-store-business": "Work you can do from a desk",
    "photography-business": "Work you can do from a desk",
    "social-media-marketing-agency": "Work you can do from a desk",
    "home-care-business": "Licensed and regulated",
    "med-spa-business": "Licensed and regulated",
    "pet-daycare-business": "Licensed and regulated",
    "ev-charging-business": "Licensed and regulated",
}

GROUP_ORDER = ["Services you can start from a van", "Food",
               "Work you can do from a desk", "Licensed and regulated"]

DEMAND_LABEL = {
    "up": "Growing",
    "flat": "Flat",
    "down": "Shrinking",
    "unclear": "Not established",
}


def display(slug):
    return DISPLAY.get(slug, slug.replace("-", " "))


# "a AI consulting business" is the kind of thing that makes a page look
# generated, and it would have been baked into the URL too.
VOWEL_SOUND = re.compile(r"^(a|e|i|o|u|AI|EV|hour|honest)", re.I)


def article(name):
    return "an" if VOWEL_SOUND.match(name.strip()) else "a"


def filename(slug):
    """Built from the display name, not the slug, so the URL reads the way
    somebody would actually type the search."""
    name = display(slug)
    return "how-to-start-%s-%s.html" % (
        article(name), re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-"))


# Four records came back with no margin figure at all, which is a finding
# rather than a gap: IRS SOI does not publish a line that specific and the
# percentages in circulation come from vendor surveys with undisclosed samples.
# Rendering that as the string "None" is how a null reaches a live page, so it
# is filled here once instead of in each generator.
UNKNOWN = {
    "margin_note": (
        "No primary source publishes a profit margin for this business. IRS "
        "Statistics of Income does not break out a line this specific, and the "
        "percentages in wide circulation come from vendor surveys and market "
        "research whose samples and methods are not published, so none is "
        "quoted here."),
    "key_stat": (
        "No primary source publishes a market size figure at this level of "
        "detail."),
    "demand_note": (
        "No primary source establishes a demand direction for this business."),
    "hardest_part": (
        "No single failure mode is established by a primary source for this "
        "business."),
    "startup_cost_note": (
        "No primary source publishes a startup cost range for this business."),
}


def load():
    """Every industry, in the order the batches were compiled."""
    out = collections.OrderedDict()
    meta = []
    for f in sorted(glob.glob(os.path.join(HERE, "industry", "batch*.json"))):
        d = json.load(io.open(f, encoding="utf-8"),
                      object_pairs_hook=collections.OrderedDict)
        for k, v in d.items():
            if k.startswith("_"):
                meta.append(v)
                continue
            for fld, fallback in UNKNOWN.items():
                v[fld + "_known"] = bool(v.get(fld))
                if not v.get(fld):
                    v[fld] = fallback
            v["slug"] = k
            v["name"] = display(k)
            v["file"] = filename(k)
            v["group"] = GROUP[k]
            out[k] = v
    return out, meta


def cost_text(rec, dash="not published"):
    lo, hi = rec["startup_cost_low_usd"], rec["startup_cost_high_usd"]
    if lo is None:
        return dash
    fmt = lambda n: "$%s" % "{:,}".format(n)
    return "%s to %s" % (fmt(lo), fmt(hi))


if __name__ == "__main__":
    ind, meta = load()
    print("%d industries, %d meta blocks" % (len(ind), len(meta)))
    for g in GROUP_ORDER:
        ks = [k for k in ind if ind[k]["group"] == g]
        print("  %-32s %d" % (g, len(ks)))
        for k in ks:
            print("      %-34s %-19s %s"
                  % (ind[k]["name"], cost_text(ind[k]),
                     DEMAND_LABEL[ind[k]["demand_direction"]]))
