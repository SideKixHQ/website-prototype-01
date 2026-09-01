"""SideKix worksheet PDF builder. wkhtmltopdf + Poppins/Lora, gold on cream, wordmark on every page."""
import os, subprocess, base64, textwrap

LOGO = base64.b64encode(open("/home/claude/site/assets/sidekix-wordmark.png","rb").read()).decode()

CSS = """
@page { size: Letter; margin: 20mm 16mm 22mm 16mm; }
* { box-sizing: border-box; }
body { font-family:'Lora',Georgia,serif; font-size:10.5pt; line-height:1.62;
       color:#1a1712; margin:0; }
.mast { border-bottom:2px solid #D4A856; padding-bottom:9px; margin-bottom:20px;
        display:flex; align-items:flex-end; justify-content:space-between; }
.mast img { height:26px; }
.mast .kick { font-family:'Poppins',sans-serif; font-size:7.5pt; letter-spacing:.19em;
              text-transform:uppercase; color:#8a7231; padding-bottom:3px; }
h1 { font-family:'Poppins',sans-serif; font-size:20pt; line-height:1.16; font-weight:700;
     color:#0d0b08; margin:0 0 7px; letter-spacing:-.01em; }
.dek { font-size:10.5pt; color:#5b5346; margin:0 0 22px; font-style:italic; }
h2 { font-family:'Poppins',sans-serif; font-size:11.5pt; font-weight:700; color:#0d0b08;
     margin:22px 0 9px; padding-bottom:5px; border-bottom:1px solid #e6ddc7;
     page-break-after:avoid; }
h2 .n { color:#B8912F; font-size:9pt; margin-right:8px; }
p { margin:0 0 10px; }
.hint { font-family:'Poppins',sans-serif; font-size:8.5pt; color:#6f6656; margin:0 0 11px; }
.field { border:1px solid #d9cfb6; border-radius:4px; background:#fdfbf5;
         padding:9px 11px; margin:0 0 9px; page-break-inside:avoid; }
.field .lab { font-family:'Poppins',sans-serif; font-size:8pt; font-weight:600;
              letter-spacing:.05em; text-transform:uppercase; color:#8a7231; margin-bottom:4px; }
.rule { border-bottom:1px solid #cfc4a8; height:17px; margin-top:3px; }
.rows .rule { margin-top:9px; }
table { width:100%; border-collapse:collapse; margin:0 0 12px; page-break-inside:avoid; }
th { font-family:'Poppins',sans-serif; font-size:8pt; font-weight:600; text-transform:uppercase;
     letter-spacing:.06em; color:#8a7231; text-align:left; border-bottom:1.5px solid #D4A856;
     padding:0 8px 5px; }
td { border-bottom:1px solid #e6ddc7; padding:11px 8px; vertical-align:top; }
td.blank { height:26px; }
ul { margin:0 0 12px; padding-left:0; list-style:none; }
li { padding-left:20px; position:relative; margin-bottom:7px; }
li:before { content:'\\25A1'; position:absolute; left:0; color:#B8912F; font-size:11pt; }
.note { background:#faf4e6; border-left:3px solid #D4A856; padding:10px 13px;
        font-size:9.5pt; color:#4a4237; margin:0 0 14px; page-break-inside:avoid; }
.foot { position:fixed; bottom:-14mm; left:0; right:0; font-family:'Poppins',sans-serif;
        font-size:7.5pt; color:#9a9081; display:flex; justify-content:space-between;
        border-top:1px solid #e6ddc7; padding-top:5px; }
.foot b { color:#8a7231; font-weight:600; }
"""

def build(slug, kicker, title, dek, blocks, outdir="/home/claude/site/assets/worksheets"):
    os.makedirs(outdir, exist_ok=True)
    body = "".join(blocks)
    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>
<div class="mast"><img src="data:image/png;base64,{LOGO}" alt="SideKix"><div class="kick">{kicker}</div></div>
<h1>{title}</h1><p class="dek">{dek}</p>
{body}
<div class="foot"><span><b>SideKix</b> &nbsp;sidekixhq.com</span><span>Talent is everywhere. Opportunity is for all.</span></div>
</body></html>"""
    src = f"/home/claude/build/_{slug}.html"
    open(src,"w",encoding="utf-8").write(html)
    out = f"{outdir}/{slug}.pdf"
    r = subprocess.run(["wkhtmltopdf","--quiet","--enable-local-file-access",
        "--print-media-type","--dpi","150",src,out],capture_output=True,text=True)
    if r.returncode!=0: raise RuntimeError(r.stderr[:500])
    return out

# ---- block helpers ----
def h2(n,t):    return f'<h2><span class="n">{n}</span>{t}</h2>'
def p(t):       return f"<p>{t}</p>"
def hint(t):    return f'<p class="hint">{t}</p>'
def note(t):    return f'<div class="note">{t}</div>'
def field(lab,lines=2):
    return f'<div class="field"><div class="lab">{lab}</div>'+('<div class="rule"></div>'*lines)+'</div>'
def rows(lab,n=4):
    return f'<div class="field rows"><div class="lab">{lab}</div>'+('<div class="rule"></div>'*n)+'</div>'
def checks(items): return "<ul>"+"".join(f"<li>{i}</li>" for i in items)+"</ul>"
def table(heads,nrows=5):
    th="".join(f"<th>{h}</th>" for h in heads)
    tr=("<tr>"+"".join('<td class="blank"></td>' for _ in heads)+"</tr>")*nrows
    return f"<table><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table>"
