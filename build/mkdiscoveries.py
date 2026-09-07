# -*- coding: utf-8 -*-
"""The Discoveries hub.

The product has a whole section of these. On the web they are the front door:
short, no account, no email, and the sort of thing somebody sends to a friend.
Cosmo quizzes, if Cosmo were about how you work.

The rule that keeps this from being a novelty shelf: every Discovery ends
somewhere real. A result that maps onto something SideKix actually does, and a
next step the person can take today. Traffic that ends at a shareable label
and nothing else is an audience, not a business.
"""
import os, sys, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from toolgen import page, crumbs, faqpage, SITE

def e(s): return html.escape(str(s), quote=True)

ZOO = ["lion", "dragon", "phoenix", "octopus", "dolphin", "unicorn",
       "gorilla", "panda", "cat", "goat", "highland", "possum"]

# (href, title, blurb, minutes, what you get, accent, art or None)
LIVE = [
 ("assessment.html", "The Energy Discovery",
  "Forty eight statements on how you actually behave under pressure, and a "
  "distribution across all twelve energies. Everyone runs on all of them. "
  "The question is the proportions.",
  "10", "your twelve, ranked", "#D4A856", "zoo"),
 ("founder-diagnostic.html", "Where are you, actually?",
  "Five questions and a straight read on the stage you are at, plus what "
  "tends to matter there and the handful of things on this site that fit.",
  "2", "your stage, named", "#6FB3A6", None),
]

# What is coming. Named because an empty shelf that says "more soon" tells a
# visitor nothing, and a named one tells them whether to come back.
QUICK = [
 ("q/founder-energy/", "Which energy do you run on?",
  "The short read on which of the twelve is loudest today. Six questions, and "
  "it ends by offering the full Discovery if you want the whole distribution.",
  "1", "one of the twelve", "#D4A856", "zoo"),
 ("q/what-business/", "What kind of business fits you?",
  "Not which idea, which shape. Eight questions, six kinds of business, and "
  "the real ones behind each of them with what they cost and what they earn.",
  "1", "a shape, and four guides", "#DE9E33", None),
 ("q/quit-your-job/", "Are you ready to quit your job?",
  "Not a verdict and not permission. A read on which of five places you are "
  "standing, based on what has happened rather than how it feels.",
  "1", "where you actually stand", "#4FA96B", None),
 ("q/when-it-goes-wrong/", "What do you do when it goes wrong?",
  "Everyone has a default. Knowing yours is the difference between using it "
  "and being used by it.",
  "1", "your default under pressure", "#E6323F", None),
 ("q/who-you-build-with/", "Who do you build with?",
  "What you bring to a room, and what you cost it. Most of what goes wrong in "
  "a business is about people rather than product.",
  "1", "your role in a room", "#3FAEBD", None),
 ("q/money-personality/", "How do you actually handle money?",
  "Not how you think you handle it. What you do when a number is in front of "
  "you, which is usually different.",
  "1", "your money default", "#8E6FBF", None),
]

# What is coming. Named because an empty shelf that says "more soon" tells a
# visitor nothing, and a named one tells them whether to come back.
SOON = [
 ("How do you decide?", "Whether you move on instinct, evidence or consensus, "
  "and what that costs you when the clock is running."),
 ("What are you actually good at?", "Not what you trained for. What people "
  "come to you for without being asked."),
]

CSS = """
.dsc{max-width:60rem;margin:0 auto}
.dsc-note{font-size:16.5px;line-height:1.75;color:#CFC7B4;margin:0 0 36px;
  max-width:44rem}
.dsc-note b{color:#F3E4A8;font-weight:600}
.dsc-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:20px;margin:0 0 56px}
.dsc-c{--a:#D4A856;position:relative;display:flex;flex-direction:column;
  padding:28px 28px 26px;border-radius:20px;text-decoration:none;
  border:1px solid rgba(212,168,86,.26);
  background:linear-gradient(180deg,rgba(255,255,255,.035),rgba(255,255,255,.012));
  transition:border-color .3s,transform .3s cubic-bezier(.16,1,.3,1),box-shadow .3s}
.dsc-c:hover,.dsc-c:focus-visible{border-color:var(--a);transform:translateY(-3px);
  box-shadow:0 18px 50px -22px rgba(0,0,0,.9)}
.dsc-c::before{content:"";position:absolute;left:28px;top:0;width:44px;height:2px;
  background:var(--a);border-radius:0 0 2px 2px}
.dsc-c b{display:block;font-family:var(--display);font-size:23px;line-height:1.15;
  color:#FFF8E8;margin:0 0 10px;font-weight:600}
.dsc-c span{color:#BDB4A4;font-size:15.5px;line-height:1.6}
.dsc-meta{display:flex;gap:14px;align-items:center;margin:18px 0 0;
  font-family:var(--util);font-size:10.5px;letter-spacing:.16em;
  text-transform:uppercase}
.dsc-meta em{font-style:normal;color:var(--a);font-weight:700}
.dsc-meta i{font-style:normal;color:#9C9484}
.dsc-zoo{display:flex;gap:4px;margin:16px 0 0;flex-wrap:wrap}
.dsc-zoo img{width:30px;height:30px;border-radius:50%;
  background:rgba(255,255,255,.04)}
.dsc-h3{font-family:var(--util);font-size:11px;letter-spacing:.22em;
  text-transform:uppercase;color:#BDB4A4;font-weight:600;margin:0 0 16px;
  padding:0 0 10px;border-bottom:1px solid rgba(212,168,86,.18)}
.dsc-soon{display:grid;grid-template-columns:repeat(2,1fr);gap:16px;margin:0 0 44px}
.dsc-s{padding:22px 24px;border-radius:16px;border:1px dashed rgba(212,168,86,.26)}
.dsc-s b{display:block;font-family:var(--display);font-size:19px;color:#E4DAC4;
  margin:0 0 7px;font-weight:600}
.dsc-s span{color:#9C9484;font-size:14.5px;line-height:1.6}
@media(max-width:760px){.dsc-grid,.dsc-soon{grid-template-columns:1fr}}
"""


def card(href, title, blurb, mins, gets, accent, art):
    zoo = ""
    if art == "zoo":
        zoo = ('<span aria-hidden="true" class="dsc-zoo">'
               + "".join('<img alt="" decoding="async" height="30" loading="lazy" '
                         'src="assets/energies/%s-sm.webp" width="30"/>' % a for a in ZOO)
               + '</span>')
    return ('<a class="dsc-c" href="%s" style="--a:%s">'
            '<b>%s</b><span>%s</span>%s'
            '<span class="dsc-meta"><em>%s min</em><i>%s</i></span></a>'
            % (e(href), e(accent), e(title), e(blurb), zoo, e(mins), e(gets)))


def build():
    b = ['<div class="dsc">']
    b.append('<p class="dsc-note">No account, no email, nothing kept. Every one '
             'of these runs in your own browser and forgets you the moment you '
             'close the tab. <b>They are for you, not for us.</b></p>')

    b.append('<h2 class="dsc-h3">The long ones</h2>')
    b.append('<div class="dsc-grid">%s</div>'
             % "".join(card(*c) for c in LIVE))

    # A separate tier on purpose. The Energy Discovery is 48 statements with a
    # method behind it, and putting a 40 second quiz beside it as an equal
    # would cost the longer one its credibility.
    b.append('<h2 class="dsc-h3">The quick ones</h2>')
    b.append('<p class="dsc-note">Under a minute each, and honest rather than '
             'flattering. Every one tells you what the result costs you as well '
             'as what it gives you, and you can post the card.</p>')
    b.append('<div class="dsc-grid">%s</div>'
             % "".join(card(*c) for c in QUICK))

    b.append('<h2 class="dsc-h3">Being written</h2>')
    b.append('<div class="dsc-soon">%s</div>'
             % "".join('<div class="dsc-s"><b>%s</b><span>%s</span></div>'
                       % (e(t), e(d)) for t, d in SOON))

    b.append('<h2 class="dsc-h3">Why these end somewhere</h2>')
    b.append('<p class="dsc-note">A result on its own changes nothing. The '
             'research on feedback is blunt about it: being told about yourself '
             'does not move behaviour, and self-focused feedback can do worse '
             'than none at all. What holds up is a plan tied to a situation you '
             'actually meet. So each of these ends with one, chosen by you '
             'rather than handed to you.</p>')
    b.append("</div>")

    faqs = [
     ("Do the Discoveries cost anything?",
      "No. There is no account, no email step and no payment. Everything runs "
      "in your browser and nothing is sent anywhere."),
     ("Are these scientifically validated?",
      "No, and the pages say so. They are self-report reflection tools built on "
      "established assessment practice, not psychometric instruments. They have "
      "not been through the reliability and validity testing that would let them "
      "be used for hiring, clinical or diagnostic purposes."),
     ("How long does the Energy Discovery take?",
      "About ten minutes for forty eight statements. The Founder Diagnostic is "
      "five questions and takes about two."),
     ("Is anything I answer saved?",
      "No. Nothing is stored and nothing is transmitted. Close the tab and the "
      "answers are gone, which also means you cannot come back to a part "
      "finished one."),
    ]

    n = page("discoveries.html",
             "Discoveries: Short Self-Assessments for People Building Something | SideKix",
             "Short discoveries about how you work, decide and recover. No "
             "account, no email, nothing kept. Each one ends with something you "
             "can act on.",
             "Discoveries",
             "Find out how you <em>actually</em> work.",
             "Short, honest and a little bit fun. Each one takes minutes, keeps "
             "nothing, and ends with something you can do rather than a label to "
             "carry around.",
             "".join(b), css=CSS,
             schema=(crumbs("Discoveries", "discoveries.html"),
                     faqpage(faqs),
                     {"@context": "https://schema.org", "@type": "CollectionPage",
                      "@id": "%s/discoveries.html#page" % SITE,
                      "url": "%s/discoveries.html" % SITE, "name": "Discoveries",
                      "mainEntity": {"@type": "ItemList",
                                     "numberOfItems": len(LIVE),
                                     "itemListElement": [
                                       {"@type": "ListItem", "position": i + 1,
                                        "url": "%s/%s" % (SITE, c[0]), "name": c[1]}
                                       for i, c in enumerate(LIVE)]}}),
             back=('<p class="kx-backrow"><a class="kx-bk" href="index.html">'
                   '<svg aria-hidden="true" focusable="false" viewbox="0 0 24 24">'
                   '<path d="M15 5l-7 7 7 7"></path></svg> Back to SideKix</a></p>'))
    print("discoveries.html %d KB, %d live, %d being written"
          % (n // 1024, len(LIVE), len(SOON)))


if __name__ == "__main__":
    build()
