import os
# the pages live at the repository root, and this script sits in audit/
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import os, re, subprocess

PAGES = ["index","how-it-works","membership","resources","events","market-data",
         "glossary","tools","become-an-advisor","join","faq","privacy","terms"]

# this renderer supports neither position:fixed nor clamp(), so the bar and the
# orb land in the wrong place unless they are pinned explicitly. these
# substitutions only affect the screenshot, never the shipped file.
FIX = """<style>
#kx-nav{position:absolute !important;top:0 !important;left:0 !important;right:0 !important;
  background:linear-gradient(180deg,rgba(5,5,5,.92),rgba(5,5,5,0)) !important;
  border-bottom:1px solid rgba(212,168,86,.18) !important}
#kx-orbnav{position:absolute !important;top:0 !important;bottom:auto !important;
  right:24px !important;left:auto !important}
#kx-orbmaster > span img{height:25px !important;width:auto !important}
#kx-desat{display:none !important}
body{position:relative}
</style>
</head>"""

os.makedirs("/tmp/shots", exist_ok=True)
for p in PAGES:
    src=fROOT+"/{p}.html"
    if not os.path.exists(src): continue
    raw=open(src,encoding="utf-8").read()
    open(f"/tmp/shots/{p}.html","w",encoding="utf-8").write(raw.replace("</head>", FIX, 1))
print("prepared", len(PAGES), "pages")
