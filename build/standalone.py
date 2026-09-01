import re, base64, os
ASSETS="/home/claude/site/assets"
css=open(f"{ASSETS}/fonts.css",encoding="utf-8").read()

# inline only the font files that actually exist, latin subsets
out=[]
for b in re.findall(r'@font-face\s*\{.*?\}',css,re.S):
    m=re.search(r'url\("assets/([^"]+)"\)',b)
    ur=re.search(r'unicode-range:\s*([^;]+);',b)
    if not m: continue
    path=os.path.join(ASSETS,m.group(1))
    if not os.path.exists(path): continue          # Poppins and EA Majer files are absent
    if ur and not ur.group(1).strip().startswith("U+0000"): continue
    data=base64.b64encode(open(path,"rb").read()).decode()
    fmt="woff2" if path.endswith("woff2") else "truetype"
    out.append(re.sub(r'url\("assets/[^"]+"\)', f'url("data:font/{fmt};base64,{data}")', b))
FONTCSS="\n".join(out)
print("inlined font faces:",len(out),"| css bytes:",len(FONTCSS)//1024,"KB")

def standalone(src,dst,banner):
    h=open(src,encoding="utf-8").read()
    h=h.replace('<link rel="preload" href="assets/fonts.css" as="style">','')
    h=h.replace('<link rel="stylesheet" href="assets/fonts.css">',f"<style>{FONTCSS}</style>")
    h=h.replace('<link rel="icon" href="favicon.ico">','')
    # the wordmark in the top bar is already base64 in the theme; the PDF link cannot work offline
    h=h.replace('href="assets/worksheets/sidekix-business-glossary.pdf" download','href="#" data-offline="1"')
    note=(f'<div style="position:fixed;left:0;right:0;bottom:0;z-index:400;'
          f'background:rgba(10,9,7,.94);border-top:1px solid rgba(212,168,86,.4);'
          f'color:#C9A761;font:500 12px/1.5 system-ui,sans-serif;letter-spacing:.04em;'
          f'padding:9px 16px;text-align:center;">{banner}</div>')
    h=h.replace("</body>",note+"</body>")
    open(dst,"w",encoding="utf-8").write(h)
    print(f"  {os.path.getsize(dst)//1024:4d} KB  {dst}")

standalone("/home/claude/site/glossary.html","/mnt/user-data/outputs/glossary.html",
  "Standalone preview. Search, filters, copy buttons and all effects work. "
  "Links to other pages and the PDF only work in the full site.")
standalone("/home/claude/site/tools.html","/mnt/user-data/outputs/tools.html",
  "Standalone preview. All four calculators and copy buttons work. "
  "Links to other pages only work in the full site.")
