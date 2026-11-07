"""Fallbacks for older browsers, so newer CSS degrades instead of breaking.

Current Chrome, Safari, Firefox, Edge and Samsung Internet use the modern
declaration in every case below; only browsers that do not understand it fall
back. Each fallback goes right before the declaration it backs up, inside the
same rule, so the modern one still wins where it is supported.

1. @property variables (--ang, --kxa, --b): browsers without @property treat
   an unset variable as invalid, which drops the whole gradient, so the gold
   trace borders vanished instead of standing still. A plain :root default
   equal to the registered initial-value keeps them visible.
2. color-mix(): without it the declaration is dropped and the colour is lost.
   A plain declaration goes first, using whichever of the two mixed colours
   carries more weight (so a faint glow mixed with transparent falls back to
   none, not to a solid colour).
3. overflow: clip: Safari before 16 ignores it, which removes the guard
   against sideways scrolling. overflow: hidden goes first.
4. svh / dvh / lvh units: older browsers drop the declaration (How it works'
   pinned story would collapse). The same value in vh goes first.

Safe to run again: a declaration that already has its fallback in front of it
is left alone. Run it after any build.
"""
import glob, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP = ('node_modules', 'audit', 'host-configs', 'sidekix-events-handoff', 'patches', '.git')
MARK = '/* kx-compat: plain defaults for browsers without @property */'


def split_args(s):
    """Split a function's argument string on top-level commas."""
    out, depth, cur = [], 0, ''
    for ch in s:
        if ch == '(':
            depth += 1
        elif ch == ')':
            depth -= 1
        if ch == ',' and depth == 0:
            out.append(cur.strip()); cur = ''
        else:
            cur += ch
    out.append(cur.strip())
    return out


def find_call(s, start):
    """Return the end index (exclusive) of the call whose '(' is at s[start]."""
    depth = 0
    for i in range(start, len(s)):
        if s[i] == '(':
            depth += 1
        elif s[i] == ')':
            depth -= 1
            if depth == 0:
                return i + 1
    return -1


def plain_colour(call):
    """color-mix(in srgb, A p%, B q%) -> the heavier of A and B."""
    inner = call[call.index('(') + 1:-1]
    args = split_args(inner)
    if len(args) != 3:
        return None
    def part(a):
        m = re.match(r'^(.*?)(?:\s+(\d+(?:\.\d+)?)%)?$', a.strip(), re.S)
        return m.group(1).strip(), (float(m.group(2)) if m.group(2) else None)
    (c1, p1), (c2, p2) = part(args[1]), part(args[2])
    if p1 is None and p2 is None:
        p1 = p2 = 50
    elif p1 is None:
        p1 = 100 - p2
    elif p2 is None:
        p2 = 100 - p1
    pick = c1 if p1 >= p2 else c2
    return None if 'color-mix' in pick else pick


def replace_mix(value):
    """Replace every color-mix(...) in a declaration value by its plain colour."""
    out, i = '', 0
    while True:
        j = value.find('color-mix(', i)
        if j < 0:
            return out + value[i:]
        k = find_call(value, j + len('color-mix'))
        if k < 0:
            return None
        col = plain_colour(value[j:k])
        if col is None:
            return None
        out += value[i:j] + col
        i = k


DECL = re.compile(r'(?P<pre>[{;]\s*)(?P<prop>-?[a-z][a-z-]*)\s*:\s*(?P<val>[^;{}]*)(?=[;}])')


def fix_css(css):
    n = 0
    def one(m):
        nonlocal n
        pre, prop, val = m.group('pre'), m.group('prop'), m.group('val')
        fb = None
        if 'color-mix(' in val:
            fb = replace_mix(val)
        elif prop.startswith('overflow') and re.match(r'^\s*clip\b', val):
            fb = re.sub(r'\bclip\b', 'hidden', val, count=1)
        elif re.search(r'\d(?:svh|dvh|lvh)\b', val):
            fb = re.sub(r'(\d)(?:svh|dvh|lvh)\b', r'\1vh', val)
        if not fb or fb == val:
            return m.group(0)
        # already backed up by the declaration just before it
        before = css[max(0, m.start() - 400):m.start() + len(pre)]
        last = re.split(r'[{;]', before.rstrip().rstrip(';'))[-1] if before.strip() else ''
        if re.match(r'\s*' + re.escape(prop) + r'\s*:', last):
            return m.group(0)
        n += 1
        return '%s%s:%s;%s:%s' % (pre, prop, fb.strip(), prop, val)
    css = DECL.sub(one, css)
    # @property defaults
    if MARK not in css:
        defaults = []
        for name, body in re.findall(r'@property\s+(--[\w-]+)\s*\{([^}]*)\}', css):
            iv = re.search(r'initial-value\s*:\s*([^;}]+)', body)
            if iv and (name, iv.group(1).strip()) not in defaults:
                defaults.append((name, iv.group(1).strip()))
        if defaults:
            css = css + '\n' + MARK + '\n:root{' + ';'.join('%s:%s' % d for d in defaults) + '}\n'
            n += len(defaults)
    return css, n


def process(path):
    s = open(path, encoding='utf-8').read()
    total = 0
    if path.endswith('.css'):
        s2, total = fix_css(s)
    else:
        def style(m):
            nonlocal total
            body, k = fix_css(m.group(2))
            total += k
            return m.group(1) + body + m.group(3)
        s2 = re.sub(r'(<style[^>]*>)(.*?)(</style>)', style, s, flags=re.S)
    if s2 != s:
        open(path, 'w', encoding='utf-8').write(s2)
    return total


def main():
    files = [f for f in glob.glob(os.path.join(ROOT, '**', '*'), recursive=True)
             if os.path.isfile(f) and f.endswith(('.html', '.css'))
             and os.path.relpath(f, ROOT).split(os.sep)[0] not in SKIP]
    files = [f for f in files if not os.path.relpath(f, ROOT).startswith('build' + os.sep) or f.endswith('kix-src.html')]
    changed = {}
    for f in files:
        k = process(f)
        if k:
            changed[os.path.relpath(f, ROOT)] = k
    print('fallbacks added: %d in %d files' % (sum(changed.values()), len(changed)))
    return changed


if __name__ == '__main__':
    main()
