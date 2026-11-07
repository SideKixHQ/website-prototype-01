"""Build kix.html inside the real site frame.

The Kix content lives in build/kix-src.html (its own <main>, styles and scripts).
The frame comes from resources.html at build time: the head assets, the kx-nav
top bar, the MENU orb, the sk-footer and the shared scripts. Reading it from a
live page means /kix cannot drift from the rest of the site again.

The Kix styles are scoped to #kixpage, so they style the Kix content and
nothing in the site's header or footer.

Run from the repo root:  python3 build/mkkix.py
"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'build', 'kix-src.html')
FRAME = os.path.join(ROOT, 'resources.html')
OUT = os.path.join(ROOT, 'kix.html')
SITE = 'https://sidekixhq.com'

# the site's top bar is fixed, so the first section clears it like the other pages do
FRAME_FIT = ('#kixpage{background:#050403;color:#ECE5D3}'
             '#kixpage > section.kp-hero{padding-top:clamp(104px,12vw,140px)}')

TITLE = 'Kix: Your Entrepreneurial Support Guide | SideKix'
OG_TITLE = 'Kix, your entrepreneurial support guide | SideKix'


# ---------------------------------------------------------------- css scoping
DROP = re.compile(r'\.sitenav|\.menupanel|\.menubtn|\.links\b|(^|[\s,>+~])footer\b|\.skip\b|\.logo\b|body\.menu-open')


def _split_top(css):
    """Yield (prelude, body) for each top-level block, plus bare statements."""
    i, n, out = 0, len(css), []
    while i < n:
        j = css.find('{', i)
        semi = css.find(';', i)
        if j < 0:
            break
        if 0 <= semi < j and css[i:semi].strip().startswith('@'):   # @import / @charset
            out.append((css[i:semi + 1].strip(), None)); i = semi + 1; continue
        depth, k = 0, j
        while k < n:
            if css[k] == '{': depth += 1
            elif css[k] == '}':
                depth -= 1
                if depth == 0: break
            k += 1
        out.append((css[i:j].strip(), css[j + 1:k])); i = k + 1
    return out


def _scope_sel(sel):
    sel = sel.strip()
    if not sel:
        return None
    if DROP.search(sel):
        return None
    if sel in (':root', 'html', 'body', 'html,body'):
        return '#kixpage'
    m = re.match(r'^((?:html|body)(?:[.:#][\w-]+(?:\([^)]*\))?)+)\s*(.*)$', sel)
    if m:                                           # body.still x, html.rv-on x
        rest = m.group(2)
        return m.group(1) + ' #kixpage' + ((' ' + rest) if rest else '')
    if sel.startswith(('html ', 'body ')):
        return '#kixpage ' + sel.split(' ', 1)[1]
    return '#kixpage ' + sel


def scope(css):
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
    out = []
    for pre, body in _split_top(css):
        if body is None:
            continue
        if pre.startswith(('@media', '@supports')):
            inner = scope(body)
            if inner.strip():
                out.append(pre + '{' + inner + '}')
        elif pre.startswith(('@keyframes', '@property', '@font-face', '@-webkit-keyframes')):
            out.append(pre + '{' + body + '}')
        else:
            sels = [x for x in (_scope_sel(s) for s in pre.split(',')) if x]
            if sels:
                out.append(','.join(sels) + '{' + body.strip() + '}')
    return '\n'.join(out)


# ---------------------------------------------------------------- build
def main():
    src = open(SRC, encoding='utf-8').read()
    frame = open(FRAME, encoding='utf-8').read()

    # ---- the Kix parts
    css = '\n'.join(re.findall(r'<style>(.*?)</style>', src, re.S))
    ld = re.findall(r'<script type="application/ld\+json">.*?</script>', src, re.S)
    meta_desc = re.search(r'<meta name="description" content="([^"]*)"', src).group(1)
    og_desc = re.search(r'<meta property="og:description" content="([^"]*)"', src).group(1)
    main_inner = re.search(r'<main[^>]*>(.*)</main>', src, re.S).group(1)
    after_footer = src[src.index('</footer>') + len('</footer>'):]
    dock = re.search(r'<nav class="dock".*?</nav>', after_footer, re.S).group(0)
    audio = re.search(r'<audio id="kixAudio".*?</audio>', after_footer, re.S).group(0)
    scripts = [s for s in re.findall(r'<script>.*?</script>', after_footer, re.S)]
    assert len(scripts) == 2, len(scripts)

    # ---- the frame: everything up to <main>, and from </main> to the end
    head_end = frame.index('</head>')
    m_open = re.search(r'<main id="maincontent">', frame)
    m_close = frame.rindex('</main>')
    top, bottom = frame[:m_open.start()], frame[m_close + len('</main>'):]

    # head: this page's title, descriptions, address and structured data
    top = re.sub(r'<title>.*?</title>', '<title>%s</title>' % TITLE, top, count=1, flags=re.S)
    top = re.sub(r'(<meta content=")[^"]*(" name="description"/>)', lambda x: x.group(1) + meta_desc + x.group(2), top)
    top = re.sub(r'(<meta content=")[^"]*(" property="og:description"/>)', lambda x: x.group(1) + og_desc + x.group(2), top)
    top = re.sub(r'(<meta content=")[^"]*(" name="twitter:description"/>)', lambda x: x.group(1) + og_desc + x.group(2), top)
    top = re.sub(r'(<meta content=")[^"]*(" property="og:title"/>)', lambda x: x.group(1) + OG_TITLE + x.group(2), top)
    top = re.sub(r'(<meta content=")[^"]*(" name="twitter:title"/>)', lambda x: x.group(1) + OG_TITLE + x.group(2), top)
    top = top.replace(SITE + '/resources.html', SITE + '/kix.html')
    top = re.sub(r'<script type="application/ld\+json">.*?</script>\s*', '', top, flags=re.S)
    extra_head = ('<meta name="apple-itunes-app" content="app-id=6757533359"/>\n' + '\n'.join(ld) +
                  '\n<style id="kix-page">\n' + scope(css) + '\n' + FRAME_FIT + '\n</style>\n')
    top = top.replace('</head>', extra_head + '</head>', 1)

    # the bar and the orb mark Kix as the current page
    def mark(bar):
        bar = re.sub(r'<span aria-current="page">([^<]*)</span>',
                     lambda x: '<a href="%s">%s</a>' % ({'Resources': 'library.html'}.get(x.group(1), x.group(1).lower().replace(' ', '-') + '.html'), x.group(1)), bar)
        bar = bar.replace(' aria-current="page"', '')
        return re.sub(r'<a href="kix\.html">Kix</a>', '<span aria-current="page">Kix</span>', bar, count=1)
    top = re.sub(r'<div class="kx-links">.*?</div>', lambda x: mark(x.group(0)), top, count=1, flags=re.S)
    top = top.replace("window.KXHERE='resources'", "window.KXHERE='kix'")
    bottom = bottom.replace("window.KXHERE='resources'", "window.KXHERE='kix'")

    # ---- assemble
    page = (top + '<main id="maincontent">\n<div id="kixpage">\n' + main_inner.strip() + '\n' + dock + '\n' + audio +
            '\n</div>\n</main>' + bottom)
    page = page.replace('</body>', '\n'.join(scripts) + '\n</body>', 1)
    if 'kx-analytics.js' not in page:
        page = page.replace('</body>', '<script src="assets/kx-analytics.js" defer></script>\n</body>', 1)
    open(OUT, 'w', encoding='utf-8').write(page)
    print('kix.html: %d KB, Kix styles scoped to #kixpage' % (len(page) // 1024))


if __name__ == '__main__':
    main()
