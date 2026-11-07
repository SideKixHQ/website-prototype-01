"""Keep the last word of a text block off a line by itself.

Joins the last two words of each text element with a no-break space (&nbsp;),
so a line can never end up holding a single word. Works in every browser,
unlike CSS text-wrap, which older Safari and Firefox ignore.

Only text that sits directly before an element's closing tag is touched, and
only when the two words are short enough to share a line on a narrow phone.
Scripts, styles and structured data are left alone.

Safe to run again: a block that already ends in &nbsp; is skipped.

Usage, from the repo root:
  python3 build/no_orphans.py               every page
  python3 build/no_orphans.py kix-src.html  one or more files
"""
import glob, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP = ('node_modules', 'audit', 'host-configs', 'sidekix-events-handoff', 'patches', '.git', 'build')
TAGS = 'div|i|cite|caption|legend|p|dd|dt|li|figcaption|blockquote|h1|h2|h3|h4|h5|h6|summary|button|a|span|label|td|th|small|em|b|strong'
# text right before a closing tag: "... word word</tag>"
END = re.compile(r'(?<=>)([^<>]*?[^<>\s])[ \t]+([^<>\s&]+)(\s*)</(%s)>' % TAGS)
RAW = re.compile(r'(<script\b.*?</script>|<style\b.*?</style>|<!--.*?-->|<textarea\b.*?</textarea>|<pre\b.*?</pre>)', re.S | re.I)
MAXPAIR = 24   # the two joined words must fit on a 320px line comfortably


def fix_text(html):
    n = 0
    def one(m):
        nonlocal n
        before, last, ws, tag = m.group(1), m.group(2), m.group(3), m.group(4)
        prev = re.split(r'\s', before)[-1]
        words = len(before.split()) + 1
        if words < 3 or len(prev) + 1 + len(last) > MAXPAIR:
            return m.group(0)
        n += 1
        return before + '&nbsp;' + last + ws + '</' + tag + '>'
    return END.sub(one, html), n


def process(path):
    s = open(path, encoding='utf-8').read()
    parts = RAW.split(s)
    total = 0
    for i in range(0, len(parts), 2):          # even parts are ordinary markup
        parts[i], k = fix_text(parts[i])
        total += k
    s2 = ''.join(parts)
    if s2 != s:
        open(path, 'w', encoding='utf-8').write(s2)
    return total


def main(args):
    if args:
        files = [a if os.path.isabs(a) else os.path.join(ROOT, a if os.path.exists(os.path.join(ROOT, a)) else os.path.join('build', a)) for a in args]
    else:
        files = [f for f in glob.glob(os.path.join(ROOT, '**', '*.html'), recursive=True)
                 if os.path.relpath(f, ROOT).split(os.sep)[0] not in SKIP]
    changed = {}
    for f in files:
        k = process(f)
        if k:
            changed[os.path.relpath(f, ROOT)] = k
    print('joined last words: %d in %d files' % (sum(changed.values()), len(changed)))
    return changed


if __name__ == '__main__':
    main(sys.argv[1:])
