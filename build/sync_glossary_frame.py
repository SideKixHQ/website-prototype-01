"""Bring glossary.html onto the site's current frame.

glossary.html was built before the main navigation changed and never picked
the changes up: its top bar had no menu links and no phone Menu button, the
logo was an inline base64 image, the orb menu was pinned to the top right by
four old style blocks, and it did not load assets/site-wide.css.

This copies the shared frame from library.html (the Resources page the
glossary sits under), leaving the glossary's own content and styles alone:
  - the <nav id="kx-nav"> bar and the <div id="kx-orbnav"> orb menu
  - the navigation style blocks, by id
  - the menu scripts (orb tray, pill label, phone menu toggle)
  - the site-wide stylesheet link
and removes the old orb-at-the-top styles.

Safe to run again. Run from the repo root:  python3 build/sync_glossary_frame.py
"""
import os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'library.html')
DST = os.path.join(ROOT, 'glossary.html')

NAV_STYLES = ['kx-fixed-fix', 'kx-mainnav', 'kx-mainnav-hover', 'kx-mainnav-current',
              'kx-mainnav-states', 'kx-mainnav-final', 'kx-bar-clean', 'kx-nav-stack', 'kx-perf-mobile',
              'kx-nav-active', 'kx-cursor-size']
# The orb-at-the-top styles, and kx-navclear, which pads the first section for a
# taller bar than this page has (its own padding already clears the bar).
OLD_STYLES = ['kx-orb-topright', 'kx-orb-label', 'kx-orbcue-fix', 'kx-orb-bar', 'kx-navclear']
SCRIPT_KEYS = {
    'orb': "var orbnav=document.getElementById('kx-orbnav')",
    'pill': 'the pill reads CLOSE while the tray is open',
    'toggle': 'window.__kxNavToggle',
}


def element(s, start_pat):
    """Return (start, end) of the element whose opening tag matches start_pat, by tag depth."""
    m = re.search(start_pat, s)
    assert m, start_pat
    tag = re.match(r'<(\w+)', s[m.start():]).group(1)
    depth, i = 0, m.start()
    pat = re.compile(r'<(/?)%s\b[^>]*>' % tag)
    for t in pat.finditer(s, m.start()):
        depth += -1 if t.group(1) else 1
        if depth == 0:
            return m.start(), t.end()
    raise AssertionError('unclosed ' + tag)


def style_block(s, sid):
    m = re.search(r'<style[^>]*\bid="%s"[^>]*>.*?</style>\n?' % re.escape(sid), s, re.S)
    return m


def script_block(s, key):
    for m in re.finditer(r'<script(?:\s[^>]*)?>.*?</script>\n?', s, re.S):
        if key in m.group(0):
            return m
    return None


def main():
    src = open(SRC, encoding='utf-8').read()
    s = open(DST, encoding='utf-8').read()

    for name in ('kx-nav', 'kx-orbnav'):
        a, b = element(src, r'<(?:nav|div)\b[^>]*\bid="%s"' % name)
        c, d = element(s, r'<(?:nav|div)\b[^>]*\bid="%s"' % name)
        s = s[:c] + src[a:b] + s[d:]

    for sid in OLD_STYLES:
        m = style_block(s, sid)
        if m:
            s = s[:m.start()] + s[m.end():]

    add = ''
    for sid in NAV_STYLES:
        m = style_block(src, sid)
        assert m, sid
        old = style_block(s, sid)
        if old:
            s = s[:old.start()] + m.group(0) + s[old.end():]
        else:
            add += m.group(0)
    if 'assets/site-wide.css' not in s:
        link = re.search(r'<link[^>]*href="assets/site-wide\.css[^"]*"[^>]*>\n?', src).group(0)
        add = link + add
    if add:
        s = s.replace('</head>', add + '</head>', 1)

    for name, key in SCRIPT_KEYS.items():
        m = script_block(src, key)
        assert m, name
        old = script_block(s, key)
        if old:
            s = s[:old.start()] + m.group(0) + s[old.end():]
        else:
            s = s.replace('</body>', m.group(0) + '</body>', 1)

    open(DST, 'w', encoding='utf-8').write(s)
    print('glossary.html: frame synced from library.html')


if __name__ == '__main__':
    main()
