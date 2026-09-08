# -*- coding: utf-8 -*-
"""The launch press release, as a page on the site.

A release that exists only as a PDF is a release search engines barely read and
answer engines cannot quote. This builds the same words as an indexable page
with NewsArticle markup, and the PDF becomes the thing a journalist downloads
rather than the only copy that exists.

The figure is 174 million, matching market-data.html and the Census source
behind it. The earlier draft said 177 million and described the platform as
already available, both of which contradicted the rest of the site.
"""
import os, sys, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from toolgen import page, SITE

def e(s): return html.escape(str(s), quote=True)

FILENAME = "press-release-launch.html"
HEADLINE = ("174 million Americans have a business idea. "
            "Most never take the first step.")
SUB      = ("SideKix HQ opens prepay access to a business operating system built to move "
            "people from idea to action through personalized guidance, practical tools and "
            "structured support.")
DATELINE = "WILMINGTON, N.C., 5 September 2026"

BODY = [
 ("p", "174 million people in the United States carry business ideas they never act on, "
       "representing a large reservoir of untapped economic potential."),
 ("p", "They see problems worth solving. They imagine better ways of doing things. They "
       "think about building something of their own. But most never move beyond the idea stage."),
 ("p", "The barrier is rarely ambition. It is clarity, access and support."),
 ("p", "What do I do first? Am I making the right decision? How do I turn this idea into "
       "something real without getting overwhelmed or lost in conflicting advice? What if I fail?"),
 ("p", "SideKix HQ today opened prepay access to its AI-assisted, human-powered business "
       "operating system, designed to help people move from idea to action with clarity, "
       "structure and ongoing support. It is built for potential and existing entrepreneurs "
       "ready to move from idea to action, without needing the right connections, the right "
       "school, or a co-founder to show them the way."),
 ("p", "The platform addresses one of entrepreneurship's most persistent and under-discussed "
       "barriers: the gap between intention and action. According to research, 74% of Americans "
       "have had a business idea, yet 92% never pursue it (Zippia). Meanwhile, 90% of Americans "
       "say they want to own their own business (Forbes/Incfile, 2023), and by 2026 the number "
       "of solo entrepreneurs is projected to grow by 40% (Zippia). Companies will get smaller "
       "and there will be more of them."),
 ("p", "SideKix combines AI-driven support with a step-by-step action framework, community "
       "support, behavioral training and variable gamification, designed for potential and "
       "existing entrepreneurs, from first-time builders with early ideas to established "
       "business owners looking to grow or pivot."),
 ("p", "SideKix provides personalized guidance, practical tools and step-by-step structure "
       "tailored to each user's goals and business context."),
 ("q", "Most people don't struggle because they lack ideas or drive. They get stuck in "
       "uncertainty. Starting and growing a business is full of decisions that feel "
       "high-stakes and confusing. SideKix is designed to help people take the next clear "
       "step, and then the next one after that, until momentum replaces uncertainty."),
 ("p", "The company addresses what it calls the gap between intention and execution, the point "
       "where many business ideas stall for lack of structure, direction or support. Unlike "
       "traditional business planning tools or general-purpose AI assistants, SideKix delivers "
       "a guided experience built specifically for entrepreneurship. It combines AI-driven "
       "support with structured action paths, community connection, and practical learning "
       "tools that adapt as a business evolves."),
 ("q", "At the core, we believe potential is everywhere, but support is not. Sometimes people "
       "need help. We believe if a friend needs help, help them. There are people in every "
       "community with ideas that could create jobs, solve problems and improve lives. Most "
       "never get a fair shot at turning those ideas into reality, and most cannot get out of "
       "their own heads. Those are the things we want to change."),
 ("q", "We built SideKix to walk alongside you, to help you navigate every one of those "
       "action-stopping decisions. Not with generic advice, but with guidance specific to your "
       "idea, your situation, and where you are right now. You are no longer doing this alone."),
 ("p", "Memberships and Kix Credits can be prepaid now at SideKixHQ.com, ahead of the platform "
       "opening. More information is available at SideKixHQ.com."),
]

ATTRIB = "said James Martucci, Founder and Chief Executive Officer of SideKix HQ"

ABOUT = ("SideKix HQ is a human-powered, AI-assisted business operating system headquartered in "
         "Wilmington, North Carolina. The company helps entrepreneurs at every stage move from "
         "idea to action through personalized guidance, practical tools, community support and "
         "structured business-building experiences. Its mission is to make starting and growing "
         "a business clearer, more accessible and more achievable for people building something "
         "of their own. SideKix is a product of Character Limit LLC, doing business as SideKix.")

CSS = """
.rel{max-width:44rem;margin:0 auto}
.rel .rel-meta{display:flex;flex-wrap:wrap;gap:10px 26px;align-items:center;
  margin:0 0 30px;padding:0 0 22px;border-bottom:1px solid rgba(212,168,86,.2)}
.rel .rel-meta span{font-family:var(--util,inherit);font-size:11px;letter-spacing:.16em;
  text-transform:uppercase;color:#BDB4A4}
.rel .rel-dl{display:inline-flex;align-items:center;gap:8px;min-height:44px;padding:0 18px;
  border-radius:999px;border:1px solid rgba(212,168,86,.5);background:rgba(212,168,86,.07);
  color:#F3E4A8;font-weight:600;font-size:13.5px;text-decoration:none}
.rel .rel-dl:hover{background:rgba(212,168,86,.16);border-color:#D4A856}
.rel .rel-sub{font-size:19px;line-height:1.6;color:#E4DAC4;font-weight:600;margin:0 0 30px}
.rel p{font-size:17px;line-height:1.78;color:#CFC7B4;margin:0 0 20px}
.rel .dl{font-family:var(--util,inherit);font-size:12px;letter-spacing:.14em;
  text-transform:uppercase;color:#D4A856;font-weight:700}
.rel blockquote{margin:28px 0;padding:4px 0 4px 22px;border-left:3px solid #A1853E}
.rel blockquote p{font-family:Georgia,serif;font-style:italic;font-size:18.5px;
  line-height:1.66;color:#E8DEC4;margin:0 0 10px}
.rel blockquote cite{font-style:normal;font-size:14px;color:#BDB4A4}
.rel h2{font-size:12px;letter-spacing:.18em;text-transform:uppercase;color:#BDB4A4;
  margin:44px 0 14px;padding:0 0 10px;border-bottom:1px solid rgba(212,168,86,.2)}
.rel .ends{text-align:center;letter-spacing:.3em;color:#877F6F;font-size:12px;margin:40px 0}
.rel a{color:#F3E4A8}
.rel .contact a{color:#F3E4A8}
@media(max-width:560px){.rel p,.rel .rel-sub{font-size:16px}}
"""

def build():
    out = ['<div class="rel">']
    out.append('<div class="rel-meta"><span>Press release</span><span>5 September 2026</span>'
               '<a class="rel-dl" href="assets/press/sidekix-launch-release.pdf" download>'
               '<svg aria-hidden="true" focusable="false" viewbox="0 0 24 24" width="15" height="15" '
               'fill="none" stroke="currentColor" stroke-width="2"><path d="M12 3v12m0 0l-4-4m4 4l4-4"/>'
               '<path d="M4 19h16"/></svg> Download the PDF</a></div>')
    out.append('<p class="rel-sub">%s</p>' % e(SUB))
    first = True
    for kind, text in BODY:
        if kind == "p":
            if first:
                out.append('<p><span class="dl">%s</span> &nbsp;%s</p>' % (e(DATELINE), e(text)))
                first = False
            else:
                out.append("<p>%s</p>" % e(text))
        else:
            out.append('<blockquote><p>%s</p><cite>%s</cite></blockquote>' % (e(text), e(ATTRIB)))
    out.append('<p class="ends">###</p>')
    out.append('<h2>About SideKix HQ</h2><p>%s</p>' % e(ABOUT))
    out.append('<h2>Media contact</h2><p class="contact">SideKix HQ press office<br/>'
               '<a href="mailto:support@sidekixhq.com?subject=Press%20enquiry">'
               'support@sidekixhq.com</a></p>')
    out.append('<h2>Notes to editors</h2><p>The 174 million figure is drawn from US Census '
               'Bureau data on Americans aged 15 and over who have had an idea for a business. '
               'The derivation, and every other figure quoted here, is shown with its source on '
               '<a href="market-data.html">the SideKix market data page</a>.</p>')
    out.append("</div>")

    schema = [{
        "@context": "https://schema.org",
        "@type": "NewsArticle",
        "headline": HEADLINE,
        "description": SUB,
        "datePublished": "2026-09-05",
        "dateModified": "2026-09-06",
        "inLanguage": "en-US",
        "url": "%s/%s" % (SITE, FILENAME),
        "mainEntityOfPage": {"@type": "WebPage", "@id": "%s/%s" % (SITE, FILENAME)},
        "author":    {"@type": "Organization", "name": "SideKix HQ", "url": SITE},
        "publisher": {"@type": "Organization", "name": "SideKix HQ", "url": SITE},
        "about": {"@type": "Thing", "name": "Entrepreneurship in the United States"},
    }]

    back = ('<p class="kx-backrow"><a class="kx-bk" href="press.html">'
            '<svg aria-hidden="true" focusable="false" viewbox="0 0 24 24">'
            '<path d="M15 5l-7 7 7 7"></path></svg> Back to press</a></p>')

    h = page(FILENAME,
             "Press Release: 174 Million Americans Have a Business Idea | SideKix",
             "SideKix HQ opens prepay access to its AI-assisted business operating system. "
             "The full launch press release, with sources for every figure quoted.",
             "Press release", HEADLINE, SUB, "".join(out),
             css=CSS, schema=schema, wrapcls="wrap res", back=back)
    print("%s  %d KB" % (FILENAME, h // 1024))

if __name__ == "__main__":
    build()
