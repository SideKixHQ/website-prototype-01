"""Add Kix to the site navigation, right after Home, everywhere the nav appears.

Three places on a page carry the nav:
  - the top bar            <div class="kx-links"> ... </div>
  - the MENU orb's tray    <a class="kx-tray-item" ...>How it works</a>
  - the footer's Explore   <li><a href="...how-it-works.html">How it works</a></li>

Each Kix link copies the How it works link next to it, so it keeps that link's
relative path (index.html, ../../index.html, /...) and styling. Safe to run
again: a block that already links kix.html is left alone. Runs over the built
pages and over the templates in build/, so a rebuild keeps the link.
"""
import glob, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_DIRS = ('node_modules/', 'host-configs/', 'sidekix-events-handoff/')

HIW = r'href="([^"]*?)how-it-works\.html"'


def _kix_href(prefix):
    return 'href="%skix.html"' % prefix


def top_bar(s):
    def fix(m):
        block = m.group(0)
        if 'kix.html' in block:
            return block
        return re.sub(r'(<a\b[^>]*?)' + HIW + r'([^>]*>)',
                      lambda a: '<a %s>Kix</a>' % _kix_href(a.group(2)) + a.group(0), block, count=1)
    return re.subn(r'<div class="kx-links">.*?</div>', fix, s, flags=re.S)


def tray(s):
    n = 0
    def fix(m):
        nonlocal n
        item = m.group(0)
        # the tray is one run of items; skip if Kix is already just before this one
        if re.search(r'class="kx-tray-item"[^>]*?kix\.html"[^>]*>(?:(?!</a>).)*?Kix</a>\s*$', s[max(0, m.start() - 3000):m.start()], re.S):
            return item
        kix = re.sub(HIW, lambda a: _kix_href(a.group(1)), item, count=1)
        kix = kix.replace(' aria-current="page"', '')
        kix = re.sub(r'How it works</a>$', 'Kix</a>', kix)
        n += 1
        return kix + item
    s = re.sub(r'<a class="kx-tray-item"[^>]*?' + HIW + r'[^>]*>(?:(?!</a>).)*?How it works</a>', fix, s, flags=re.S)
    return s, n


def footer(s):
    def fix(m):
        block = m.group(0)
        if 'kix.html' in block:
            return block
        return re.sub(r'(\s*)(<li>\s*<a\b[^>]*?' + HIW + r'[^>]*>How it works</a>\s*</li>)',
                      lambda a: '%s<li><a %s>Kix</a></li>%s%s' % (a.group(1), _kix_href(a.group(3)), a.group(1), a.group(2)),
                      block, count=1)
    return re.subn(r'Explore</h2>\s*<ul>.*?</ul>', fix, s, flags=re.S)


def tray_script(s):
    """The shared orb script rebuilds the tray from its own list at runtime."""
    if "['kix','Kix','kix.html']" in s:
        return s, 0
    return re.subn(r"(\[\['home','Home','index\.html'\],)(\s*)(\['how-it-works',)",
                   r"\1\2['kix','Kix','kix.html'],\2\3", s)


def run(path):
    s0 = open(path, encoding='utf-8').read()
    s, _ = tray_script(s0)
    s, a = top_bar(s)
    s, b = tray(s)
    s, c = footer(s)
    if s != s0:
        open(path, 'w', encoding='utf-8').write(s)
    return s != s0


def main():
    files = [f for f in glob.glob(os.path.join(ROOT, '**/*.html'), recursive=True)
             if not any(d in os.path.relpath(f, ROOT) + '/' for d in SKIP_DIRS)]
    files += [os.path.join(ROOT, 'build', x) for x in ('artgen.py', 'patcharticles.py', 'parts/calc.js')]
    changed = [os.path.relpath(f, ROOT) for f in files if os.path.exists(f) and run(f)]
    print('nav: Kix added on %d files' % len(changed))
    return changed


if __name__ == '__main__':
    main()
