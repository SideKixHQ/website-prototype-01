# -*- coding: utf-8 -*-
"""Open Graph cards, at the size Facebook and LinkedIn actually want.

Two problems this fixes. The site's og:image was a relative path, which the
Open Graph spec does not allow and LinkedIn's crawler commonly resolves to
nothing, so shared links showed no image at all. And the asset was 512x512,
which renders as a small square thumbnail beside the text rather than the large
landscape card that gets the engagement.

Rendered from HTML with the real page fonts rather than drawn by hand, so the
cards look like the site.
"""
import io, os, sys, json, asyncio
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from quizdata import load

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "og")

TPL = """<!doctype html><meta charset="utf-8">
<style>
  @font-face{font-family:CG;src:url('file://%(root)s/assets/Cormorant-Garamond-600-normal-1430ef1c.woff2') format('woff2');font-weight:600}
  *{margin:0;padding:0;box-sizing:border-box}
  html,body{width:1200px;height:630px}
  body{background:#0B0A08;color:#FFF8D8;font-family:system-ui,sans-serif;
       display:flex;align-items:center;justify-content:center;overflow:hidden}
  .glow{position:absolute;inset:0;
    background:radial-gradient(ellipse 620px 380px at 50%% 42%%, %(accent)s33, transparent 70%%)}
  .frame{position:absolute;inset:26px;border:3px solid %(accent)s55;border-radius:6px}
  .in{position:relative;text-align:center;padding:0 92px;width:100%%}
  .kick{font-size:21px;letter-spacing:.24em;text-transform:uppercase;
        color:%(accent)s;margin:0 0 26px;font-weight:700}
  h1{font-family:CG,Georgia,serif;font-weight:600;font-size:%(size)dpx;
     line-height:1.06;letter-spacing:-.01em;margin:0 0 26px}
  p{font-size:27px;line-height:1.5;color:#CFC7B4;margin:0 auto;max-width:900px}
  .foot{position:absolute;left:0;right:0;bottom:56px;text-align:center}
  .foot b{font-size:24px;letter-spacing:.2em;color:#BDB4A4;font-weight:700}
  .foot i{display:block;font-style:normal;font-size:22px;color:%(accent)s;
          letter-spacing:.06em;margin-top:8px;font-weight:600}
</style>
<div class="glow"></div><div class="frame"></div>
<div class="in"><p class="kick">%(kick)s</p><h1>%(title)s</h1><p>%(sub)s</p></div>
<div class="foot"><b>SIDEKIX</b><i>%(url)s</i></div>
"""


def html_for(title, kick, sub, url, accent="#D4A856"):
    size = 78 if len(title) < 34 else (64 if len(title) < 52 else 54)
    return TPL % {"root": ROOT, "accent": accent, "kick": kick, "title": title,
                  "sub": sub, "url": url, "size": size}


CARDS = [
    # the sitewide default, which is what every page without its own card uses
    ("default", "A complete business operating system",
     "SideKix", "Find a personalised path from where you are to where you want to be.",
     "sidekixhq.com", "#D4A856"),
]


async def render(pairs):
    from playwright.async_api import async_playwright
    async with async_playwright() as pw:
        b = await pw.chromium.launch()
        pg = await b.new_page(viewport={"width": 1200, "height": 630})
        for name, html in pairs:
            path = os.path.join(OUT, name + ".png")
            await pg.set_content(html)
            await pg.wait_for_timeout(320)
            await pg.screenshot(path=path)
            print("  %-28s %6d bytes" % (name + ".png", os.path.getsize(path)))
        await b.close()


def main():
    os.makedirs(OUT, exist_ok=True)
    pairs = []
    for name, kick, title, sub, url, accent in CARDS:
        pairs.append((name, html_for(title, kick, sub, url, accent)))
    for slug, q in load().items():
        pairs.append(("q-" + slug,
                      html_for(q["title"], "A discovery",
                               q.get("og_line") or q["kicker"],
                               "sidekixhq.com/q/" + slug,
                               q.get("accent", "#D4A856"))))
    asyncio.run(render(pairs))
    print("%d cards" % len(pairs))


if __name__ == "__main__":
    main()
