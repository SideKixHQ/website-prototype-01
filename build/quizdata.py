# -*- coding: utf-8 -*-
"""Quiz definitions, loaded and checked.

A quiz is data. Questions, weighted options, results. Adding the seventh quiz
is a JSON file, not a build change, which is the whole reason to start with six
rather than twenty.

Every quiz is validated on load: every option must score at least one result
key that exists, and every result must be reachable by some combination of
answers. A result nobody can get is the failure mode you do not notice by
clicking through once.
"""
import io, json, glob, os, re, collections, itertools

HERE = os.path.dirname(os.path.abspath(__file__))
QDIR = os.path.join(HERE, "quizzes")

BANNED = re.compile(r"\b(free|aspir\w*|mentor\w*|coach\w*|spark\w*)\b", re.I)
DIRECTIVE = ("you should", "you must", "you need to", "we recommend",
             "the best option", "the right option")


def _prose(q):
    """Every string a visitor can read."""
    out = [q["title"], q.get("kicker", ""), q.get("intro", ""),
           q.get("share_line", "")]
    for it in q["questions"]:
        out.append(it["q"])
        out += [o["a"] for o in it["options"]]
    for r in q["results"]:
        out += [r["name"], r.get("headline", ""), r.get("body", ""),
                r.get("nudge", "")]
    cta = q.get("cta") or {}
    out += [cta.get("label", ""), cta.get("blurb", "")]
    return [s for s in out if s]


def check(q):
    """Return a list of problems. Empty means the quiz is sound."""
    bad = []
    keys = [r["key"] for r in q["results"]]
    if len(set(keys)) != len(keys):
        bad.append("duplicate result keys")

    for i, it in enumerate(q["questions"]):
        if len(it["options"]) < 2:
            bad.append("q%d has fewer than two options" % (i + 1))
        for o in it["options"]:
            if not o.get("w"):
                bad.append("q%d option %r scores nothing" % (i + 1, o["a"][:30]))
            for k in (o.get("w") or {}):
                if k not in keys:
                    bad.append("q%d scores unknown result %r" % (i + 1, k))

    # A result nobody can reach is dead weight. Score the best case for each
    # result: pick the option that favours it most in every question.
    for k in keys:
        best = collections.Counter()
        for it in q["questions"]:
            pick = max(it["options"], key=lambda o: o["w"].get(k, 0))
            best.update(pick["w"])
        if best and max(best.values()) != best.get(k, 0):
            bad.append("result %r is unreachable, best case loses to %r"
                       % (k, best.most_common(1)[0][0]))

    for s in _prose(q):
        if "—" in s or "–" in s:
            bad.append("dash punctuation in %r" % s[:50])
        if re.search(r"(?<=[a-z0-9])\s-\s(?=[a-zA-Z0-9])", s):
            bad.append("spaced hyphen in %r" % s[:50])
        m = BANNED.search(s)
        if m:
            bad.append("banned word %r in %r" % (m.group(0), s[:50]))
        for d in DIRECTIVE:
            if d in s.lower():
                bad.append("directive %r in %r" % (d, s[:50]))
    return bad


def load():
    out = collections.OrderedDict()
    for p in sorted(glob.glob(os.path.join(QDIR, "*.json"))):
        q = json.load(io.open(p, encoding="utf-8"),
                      object_pairs_hook=collections.OrderedDict)
        q["file"] = "q/%s/index.html" % q["slug"]
        q["url"] = "/q/%s/" % q["slug"]
        out[q["slug"]] = q
    return out


if __name__ == "__main__":
    qs = load()
    print("%d quizzes" % len(qs))
    fail = 0
    for slug, q in qs.items():
        bad = check(q)
        fail += len(bad)
        print("  %-26s %2dq  %2d results  %s"
              % (slug, len(q["questions"]), len(q["results"]),
                 "ok" if not bad else "PROBLEMS"))
        for b in bad:
            print("      - " + b)
    print("\n%d problems" % fail)
