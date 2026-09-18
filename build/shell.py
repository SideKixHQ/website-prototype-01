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


def _mainnav(current=""):
    """The real site nav, lifted out of resources.html at build time.

    The shell's own header only ever had the logo and the Build the Future
    pill, so every page built through here was missing Home, How it works,
    Membership, Advisors, Partners, Events and Resources. Copying the markup
    into the template is what caused that drift in the first place, so the bar
    is read from a real page instead and cannot fall behind again.

    Returns (markup, head) where head is the style and script the bar needs.
    """
    root = os.path.dirname(_HERE)
    try:
        src = open(os.path.join(root, "resources.html"), encoding="utf-8").read()
    except FileNotFoundError:
        return "", ""

    m = re.search(r'(<button[^>]*class="kx-burger".*?</button>\s*<div class="kx-links">.*?</div>)',
                  src, re.S)
    if not m:
        return "", ""
    markup = m.group(1)

    # mark the page you are on, and leave it unmarked when the page is not in the bar
    if current:
        markup = re.sub(r'<a href="%s"' % re.escape(current),
                        '<a aria-current="page" href="%s"' % current, markup, count=1)

    blocks = re.findall(r'<style[^>]*>(?:(?!</style>).)*?\.kx-(?:links|burger)(?:(?!</style>).)*?</style>',
                        src, re.S)
    blocks += re.findall(r'<script[^>]*>(?:(?!</script>).)*?kx-burger(?:(?!</script>).)*?</script>',
                         src, re.S)
    return markup, "\n".join(blocks)


def page(filename, title, desc, main_html, extra_css="", extra_js="", schema=(), og_title=None, nav_current=""):
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
    # the main nav bar, and the style and script it needs
    nav_markup, nav_head = _mainnav(nav_current)
    if nav_markup:
        top = top.replace("</head>", nav_head + "</head>", 1)
        top = re.sub(r'(<nav[^>]*id="kx-nav".*?)</nav>',
                     lambda mm: mm.group(1) + nav_markup + "</nav>", top, count=1, flags=re.S)

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
