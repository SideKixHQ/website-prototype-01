# -*- coding: utf-8 -*-
"""Rewrite the 48 Energy Discovery items.

The scoring, the twelve energies and the results were right. The items were
not. They were written in a clipped, idiomatic register that reads as odd on
first pass and, in a few places, parses wrong: "I go back over something that
failed to find what actually caused it" sends the reader down the garden path
at "failed to find". Several others leaned on figures of speech ("stay level",
"takes a beat", "lands hard") or were too abstract to answer honestly.

Every item below is one observable behaviour, in ordinary English, short enough
to hold in your head, and anchored to something a person actually does. Four
per energy, which is what the scoring expects.
"""
import json, io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ITEMS = {
 "possum": [
  "When a situation feels unsettled, I wait before I act.",
  "I look at what could go wrong before I commit money or time.",
  "I save my energy for the things that will matter most.",
  "When I am not sure what is going on, I slow down instead of pushing ahead.",
 ],
 "highland": [
  "When the people around me get worked up, I stay calm.",
  "I think for a moment before I respond to bad news.",
  "I keep working at my normal pace through a stressful stretch.",
  "People come to me when they want someone steady.",
 ],
 "goat": [
  "I keep working on something after it stops being exciting.",
  "I break a big job into small steps and work through them.",
  "I go back to a problem that has already beaten me once.",
  "I keep making progress even when the work is hard going.",
 ],
 "panda": [
  "I work at a pace I could keep up for months, not days.",
  "I stop for the day at a set point instead of working until I am empty.",
  "I take breaks even when there is still work left to do.",
  "I do a little every day rather than everything at once.",
 ],
 "cat": [
  "I start things without waiting to be asked.",
  "I teach myself what I need to know instead of waiting to be shown.",
  "I decide my own order of work when nobody sets one.",
  "I would rather work something out on my own than be handed the answer.",
 ],
 "lion": [
  "I make the decision when everyone else is waiting.",
  "I say the difficult thing out loud when it needs saying.",
  "I pick a direction even when I do not have all the facts.",
  "I take responsibility in front of others when a decision of mine goes wrong.",
 ],
 "phoenix": [
  "After something fails, I go back and work out why.",
  "I try again in the same area after a setback.",
  "I change how I do things based on what went wrong last time.",
  "I talk openly about my own failures.",
 ],
 "octopus": [
  "I handle several different problems at the same time.",
  "I learn a new subject fast enough to start using it.",
  "I change my plan partway through when the situation changes.",
  "When the usual route is blocked, I look for another way in.",
 ],
 "dolphin": [
  "I can tell how someone is feeling before they say it.",
  "I change how I explain something depending on who I am talking to.",
  "People tell me things they do not tell other people.",
  "I go back and repair a relationship after a difficult conversation.",
 ],
 "gorilla": [
  "I help a group reach a decision it can actually act on.",
  "I would rather the group got it right than be right myself.",
  "I notice when someone has not spoken and make room for them.",
  "I pick up the work that nobody else has taken.",
 ],
 "dragon": [
  "I work towards goals that are years away.",
  "I can describe where we are heading so other people can picture it.",
  "I explain how today's work connects to the bigger goal.",
  "I take the slower path when it leads somewhere more important.",
 ],
 "unicorn": [
  "I come up with answers other people have not thought of.",
  "I put together two ideas that do not usually go together.",
  "I ask whether the normal way is the right way here.",
  "I stay with an idea after other people have written it off.",
 ],
}


def check(items):
    """Cheap guards against the failures that produced the last set."""
    bad = []
    BANNED = ["stay level", "takes a beat", "take a beat", "lands hard",
              "moving parts", "in play", "setup", "sitting unmade", "scramble"]
    for key, group in items.items():
        if len(group) != 4:
            bad.append("%s has %d items" % (key, len(group)))
        for t in group:
            # a leading "When ..." clause anchors the behaviour to a
            # situation, which is what makes the item answerable, so it is
            # allowed. What is not allowed is an item with no actor in it.
            if " I " not in (" " + t) and not t.startswith("People "):
                bad.append("%s: no first person subject: %s" % (key, t))
            if not t.endswith("."):
                bad.append("%s: no full stop: %s" % (key, t))
            if len(t.split()) > 17:
                bad.append("%s: %d words, too long: %s" % (key, len(t.split()), t))
            if "—" in t or "–" in t or " - " in t:
                bad.append("%s: dash used as punctuation: %s" % (key, t))
            for b in BANNED:
                if b in t.lower():
                    bad.append("%s: idiom '%s': %s" % (key, b, t))
    seen = {}
    for key, group in items.items():
        for t in group:
            if t in seen:
                bad.append("duplicate item in %s and %s" % (seen[t], key))
            seen[t] = key
    return bad


def main():
    path = os.path.join(ROOT, "energies.json")
    d = json.load(io.open(path, encoding="utf-8"))
    problems = check(ITEMS)
    if problems:
        for p in problems:
            print("  !", p)
        sys.exit(1)
    missing = {e["key"] for e in d["energies"]} - set(ITEMS)
    if missing:
        print("  ! no items for:", missing); sys.exit(1)
    n = 0
    for e in d["energies"]:
        e["items"] = ITEMS[e["key"]]
        n += len(e["items"])
    json.dump(d, io.open(path, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    words = [w for g in ITEMS.values() for t in g for w in t.split()]
    print("%d items across %d energies, %.1f words each on average"
          % (n, len(ITEMS), len(words) / n))


if __name__ == "__main__":
    main()
