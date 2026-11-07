"""Load the site's fonts on every page that uses them.

170 pages ask for Cormorant Garamond, Poppins and Space Grotesk in their CSS
but never load assets/fonts.css, so they rendered in the browser's fallback
fonts (Times, Arial, a typewriter face). This adds the same stylesheet link
the homepage uses, before the page's first stylesheet, on any page that
names a site font but loads none. The path is root-relative so pages in
folders (q/..., business-events/...) find it too.

Safe to run again, and worth running after any build: pages that already
load fonts.css (or Google Fonts, or declare the site fonts with their own @font-face) are left alone.
"""
import glob, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP = ('node_modules', 'build', 'audit', 'host-configs', 'sidekix-events-handoff', 'assets', 'patches')
LINK = '<link href="/assets/fonts.css" rel="stylesheet"/>'


def main():
    done = []
    for path in glob.glob(os.path.join(ROOT, '**', '*.html'), recursive=True):
        rel = os.path.relpath(path, ROOT)
        if rel.split(os.sep)[0] in SKIP:
            continue
        s = open(path, encoding='utf-8').read()
        # skip only pages that already load the site fonts; a page can declare
        # other faces of its own (declaration.html has handwriting fonts) and still need these
        if 'fonts.css' in s or 'fonts.googleapis' in s or re.search(r"@font-face\s*\{[^}]*font-family:\s*['\"]?(Cormorant|Poppins|Space Grotesk)", s):
            continue
        if not re.search(r'Cormorant|Poppins|Space Grotesk', s):
            continue
        head_end = s.find('</head>')
        if head_end < 0:
            continue
        m = re.search(r'<link[^>]+rel="stylesheet"[^>]*>|<link[^>]+stylesheet[^>]*>|<style', s[:head_end])
        at = m.start() if m else head_end
        s = s[:at] + LINK + '\n' + s[at:]
        open(path, 'w', encoding='utf-8').write(s)
        done.append(rel)
    print('fonts.css linked on %d pages' % len(done))
    return done


if __name__ == '__main__':
    main()
