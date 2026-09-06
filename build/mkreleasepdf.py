# -*- coding: utf-8 -*-
"""Print the corrected release to PDF.

The PDF a journalist downloads has to say the same thing as the page. The
original carried 177 million and described the platform as already available;
both are corrected here, and the layout follows the original: white paper,
the wordmark, one column.
"""
import os, sys, asyncio, base64
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mkrelease import HEADLINE, SUB, DATELINE, BODY, ATTRIB, ABOUT
import html as H
def e(s): return H.escape(str(s), quote=True)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def mark():
    p = os.path.join(ROOT, "assets", "sidekix-wordmark.png")
    return "data:image/png;base64," + base64.b64encode(open(p, "rb").read()).decode()

def doc():
    body = []
    first = True
    for kind, text in BODY:
        if kind == "p":
            if first:
                body.append('<p><b>%s</b> &nbsp;%s</p>' % (e(DATELINE), e(text)))
                first = False
            else:
                body.append("<p>%s</p>" % e(text))
        else:
            body.append('<blockquote><p>&ldquo;%s&rdquo;</p><cite>%s</cite></blockquote>'
                        % (e(text), e(ATTRIB)))
    return """<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"/>
<title>%(hl)s</title>
<style>
@page{size:letter;margin:0.9in 0.85in}
*{box-sizing:border-box}
body{margin:0;font-family:'Poppins','Helvetica Neue',Helvetica,Arial,sans-serif;
 color:#111;font-size:10.5pt;line-height:1.62}
.mk{text-align:center;margin:0 0 34px}
.mk img{height:34px;width:auto}
h1{font-size:19pt;line-height:1.22;margin:0 0 18px;font-weight:700;color:#000}
.sub{font-size:11.5pt;font-weight:700;line-height:1.5;margin:0 0 22px;color:#111}
p{margin:0 0 13px}
blockquote{margin:18px 0;padding:2px 0 2px 14px;border-left:2.5pt solid #C9A227}
blockquote p{font-style:italic;margin:0 0 6px}
cite{font-style:normal;font-size:9pt;color:#444}
h2{font-size:11pt;margin:26px 0 9px;font-weight:700}
.ends{text-align:center;letter-spacing:.3em;margin:26px 0;color:#666}
a{color:#111}
.small{font-size:9.5pt;color:#333}
</style></head><body>
<div class="mk"><img alt="SideKix" src="%(mk)s"/></div>
<h1>%(hl)s</h1>
<p class="sub">%(sub)s</p>
%(body)s
<p class="ends">###</p>
<h2>About SideKix HQ</h2><p class="small">%(about)s</p>
<h2>Media contact</h2><p class="small">SideKix HQ press office<br/>support@sidekixhq.com</p>
<h2>Notes to editors</h2><p class="small">The 174 million figure is drawn from US Census Bureau
data on Americans aged 15 and over who have had an idea for a business. The derivation, and
every other figure quoted here, is shown with its source at sidekixhq.com/market-data.html</p>
</body></html>""" % {"hl": e(HEADLINE), "sub": e(SUB), "body": "".join(body),
                     "about": e(ABOUT), "mk": mark()}

async def main():
    from playwright.async_api import async_playwright
    src = os.path.join(ROOT, "assets", "press", "_release.html")
    open(src, "w").write(doc())
    out = os.path.join(ROOT, "assets", "press", "sidekix-launch-release.pdf")
    async with async_playwright() as pw:
        b = await pw.chromium.launch()
        pg = await b.new_page()
        await pg.goto("file://" + src)
        await pg.pdf(path=out, format="Letter", print_background=True)
        await b.close()
    os.remove(src)
    print("PDF written: %d KB" % (os.path.getsize(out) // 1024))

if __name__ == "__main__":
    asyncio.run(main())
