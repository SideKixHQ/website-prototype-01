# -*- coding: utf-8 -*-
"""An emblem for every quiz result that has no animal.

Fourteen of the seventeen quizzes resolve to something with no picture, while
the page says "Post the image anywhere" and offers "Save the image". That
mismatch is the bug: the copy promised an image the visitor could not see.

These are faceted medallions in the same low-poly language as the twelve
animals, so they sit beside them rather than looking like a placeholder. The
geometry is seeded from the result key, so every result gets its own facet
pattern and keeps it forever, and the palette comes from the accent colour the
result already carries.
"""
import io, os, sys, json, glob, math, colorsys, hashlib, asyncio

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "assets", "emblems")
SIZE = 512


def rng(seed):
    """A small deterministic generator, so an emblem never changes."""
    h = int(hashlib.sha256(seed.encode("utf-8")).hexdigest(), 16)
    state = [h]
    def nxt():
        state[0] = (state[0] * 6364136223846793005 + 1442695040888963407) % (2 ** 64)
        return (state[0] >> 11) / float(1 << 53)
    return nxt


def hex_to_hls(hx):
    hx = hx.lstrip("#")
    r, g, b = (int(hx[i:i + 2], 16) / 255.0 for i in (0, 2, 4))
    return colorsys.rgb_to_hls(r, g, b)


def hls_to_hex(h, l, s):
    r, g, b = colorsys.hls_to_rgb(h % 1.0, max(0, min(1, l)), max(0, min(1, s)))
    return "#%02X%02X%02X" % (int(r * 255), int(g * 255), int(b * 255))


def facets(key, accent):
    """A faceted medallion, built on a shared vertex grid.

    The first pass jittered each facet's own corners, so neighbours did not
    meet and the background showed through as black cracks. The grid is now
    computed once and every facet reads its corners out of it, which means
    adjacent facets share vertices exactly and the surface is continuous.
    """
    r = rng(key)
    h, l, s = hex_to_hls(accent)
    cx = cy = SIZE / 2.0
    R = SIZE * 0.44
    n = 10 + int(r() * 4)                    # 10 to 13 wedges
    rings = [0.0, 0.30, 0.58, 0.82, 1.0]
    turn = r() * 2 * math.pi                 # a different orientation each time

    # one vertex per (ring, spoke), jittered once and then shared
    grid = []
    for j, rad in enumerate(rings):
        row = []
        for i in range(n):
            a = turn + (2 * math.pi * i) / n
            if j == 0:
                row.append((cx, cy))
                continue
            # the outermost ring only ever wobbles outward, so it always
            # reaches the stroked rim and leaves no dark crescent behind it
            wob = (1.0 + r() * 0.06) if j == len(rings) - 1 else 1.0 + (r() - 0.5) * 0.11
            aa = a + (r() - 0.5) * 0.07
            row.append((cx + math.cos(aa) * R * rad * wob,
                        cy + math.sin(aa) * R * rad * wob))
        grid.append(row)

    tris = []
    for j in range(len(rings) - 1):
        for i in range(n):
            i2 = (i + 1) % n
            if j == 0:
                poly = [grid[0][0], grid[1][i], grid[1][i2]]
            else:
                poly = [grid[j][i], grid[j][i2], grid[j + 1][i2], grid[j + 1][i]]
            depth = 1.0 - (rings[j] + rings[j + 1]) / 2.0
            ll = l * (0.5 + depth * 0.95) + (r() - 0.5) * 0.09
            ss = min(1.0, s * (0.7 + r() * 0.55))
            hh = h + (r() - 0.5) * 0.05
            tris.append((poly, hls_to_hex(hh, ll, ss)))
    return tris, R


def svg(key, accent):
    tris, R = facets(key, accent)
    h, l, s = hex_to_hls(accent)
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" '
             'viewBox="0 0 %d %d">' % (SIZE, SIZE, SIZE, SIZE)]
    parts.append('<defs><clipPath id="c"><circle cx="%g" cy="%g" r="%g"/></clipPath></defs>'
                 % (SIZE / 2, SIZE / 2, R))
    parts.append('<g clip-path="url(#c)">')
    for poly, col in tris:
        d = " ".join("%.1f,%.1f" % p for p in poly)
        # stroke in the fill colour so no sub pixel seam can show the page
        parts.append('<polygon points="%s" fill="%s" stroke="%s" '
                     'stroke-width="1.2" stroke-linejoin="round"/>' % (d, col, col))
    parts.append("</g>")
    parts.append('<circle cx="%g" cy="%g" r="%g" fill="none" stroke="%s" '
                 'stroke-width="7" opacity="0.9"/>'
                 % (SIZE / 2, SIZE / 2, R, hls_to_hex(h, min(0.72, l + 0.22), s)))
    parts.append("</svg>")
    return "".join(parts)


def needed():
    """Every result across every quiz that has no art of its own."""
    out = []
    for p in sorted(glob.glob(os.path.join(HERE, "quizzes", "*.json"))):
        q = json.load(io.open(p, encoding="utf-8"))
        for r in q["results"]:
            if r.get("art"):
                continue
            key = "%s-%s" % (q["slug"], r["key"])
            accent = r.get("accent") or q.get("accent") or "#D4A856"
            out.append((key, accent, q["slug"], r["key"]))
    return out


def main():
    """SVG rather than raster.

    Rasterising 69 medallions through a browser took minutes and bought
    nothing: these are flat polygons, so an SVG is a twentieth of the size,
    stays crisp at any density, and being same origin with no external
    references it draws onto the share canvas without tainting it.
    """
    os.makedirs(OUT, exist_ok=True)
    items = needed()
    tot = 0
    for key, accent, slug, rkey in items:
        path = os.path.join(OUT, key + ".svg")
        body = svg(key, accent)
        io.open(path, "w", encoding="utf-8").write(body)
        tot += len(body.encode("utf-8"))
    print("%d emblems, %d KB total, %d bytes average"
          % (len(items), tot // 1024, tot // max(1, len(items))))
    return items


if __name__ == "__main__":
    main()
