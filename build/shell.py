import os
"""Build a top-level SideKix page on the real site theme, cloned from resources.html."""
import re, json

BACKROW = ('<p class="kx-backrow"><a class="kx-bk" href="resources.html">'
           '<svg aria-hidden="true" focusable="false" viewBox="0 0 24 24">'
           '<path d="M15 5l-7 7 7 7"></path></svg> Back to resources</a></p>')



def _chrome():
    """The shared chrome: orb menu, MENU pill, back link, footer hover, image
    aspect rule. These used to be patched into the built pages by hand, so
    every rebuild silently dropped them and the orb reverted to the bottom
    right. Reading the file here means a rebuild keeps them."""
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_chrome.html")
    try:
        return open(p, encoding="utf-8").read()
    except FileNotFoundError:
        return ""



# Relative to this file rather than to one absolute location, so the repo can
# be checked out anywhere and still build.
_HERE = os.path.dirname(os.path.abspath(__file__))
TOP = open(os.path.join(_HERE, "_shell_top.html"), encoding="utf-8").read()
BOTTOM = open(os.path.join(_HERE, "_shell_bottom.html"), encoding="utf-8").read()
SITE = "https://sidekixhq.com"

def page(filename, title, desc, main_html, extra_css="", extra_js="", schema=(), og_title=None):
    top = TOP
    top = re.sub(r'<title>.*?</title>', f'<title>{title}</title>', top, count=1, flags=re.S)
    old = re.search(r'<meta name="description" content="(.*?)"', top, re.S).group(1)
    top = top.replace(old, desc)                     # meta, og and twitter descriptions together
    top = top.replace("__DESC__", desc)
    top = top.replace("__OGTITLE__", og_title or title.split(" | ")[0])
    top = top.replace(f'{SITE}/resources.html', f'{SITE}/{filename}')
    # the orb tray highlights the current page; these are not tray entries, so clear the marker
    top = top.replace("window.KXHERE='resources'", "window.KXHERE=''")
    if extra_css:
        top = top.replace("</head>", f"<style>\n{extra_css}\n</style>\n</head>", 1)
    # the shared chrome goes last so it wins the cascade, exactly as it did
    # when it was appended to the built file
    top = top.replace("</head>", _chrome() + "</head>", 1)

    for s in schema:
        top = top.replace("</head>",
            f'<script type="application/ld+json">{json.dumps(s, ensure_ascii=False)}</script>\n</head>', 1)
    bottom = BOTTOM
    if extra_js:
        bottom = bottom.replace("</body>", f"<script>\ntry{{\n{extra_js}\n}}catch(e){{console.error('SideKix [{filename}] failed:',e);}}\n</script>\n</body>", 1)
    return top + main_html + bottom
