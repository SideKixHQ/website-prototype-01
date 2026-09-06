# -*- coding: utf-8 -*-
"""Find the reading units inside a comic sheet.

Each sheet is one image holding a grid of cells separated by flat gutters. The
detector samples the outer frame for the gutter colour, masks every pixel close
to it, then looks for rows where almost the whole width is gutter, and inside
each row for columns where almost the whole height is gutter. What survives is
a list of [x, y, w, h] fractions the reader clips to.

Run it, then look at the contact sheet it writes. Filenames lie; crops do not.
"""
import json, os, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMICS = os.path.join(ROOT, "assets", "comics")


def bands(flags, min_run):
    """Turn a per-line boolean 'this line is content' into [start, end) runs."""
    out, start = [], None
    for i, on in enumerate(flags):
        if on and start is None:
            start = i
        elif not on and start is not None:
            if i - start >= min_run:
                out.append((start, i))
            start = None
    if start is not None and len(flags) - start >= min_run:
        out.append((start, len(flags)))
    return out


def detect(path, tol=42, gut=0.94, min_freq=0.02):
    im = Image.open(path).convert("RGB")
    W, H = im.size
    px = im.load()

    # the gutter colour, read from the outer frame rather than assumed
    edge = []
    for x in range(0, W, 7):
        edge.append(px[x, 2]); edge.append(px[x, H - 3])
    for y in range(0, H, 7):
        edge.append(px[2, y]); edge.append(px[W - 3, y])
    gr = sum(c[0] for c in edge) // len(edge)
    gg = sum(c[1] for c in edge) // len(edge)
    gb = sum(c[2] for c in edge) // len(edge)

    def is_gutter(c):
        return abs(c[0]-gr) <= tol and abs(c[1]-gg) <= tol and abs(c[2]-gb) <= tol

    step = 2
    xs = range(0, W, step)
    ys = range(0, H, step)

    rowfill = []
    for y in ys:
        n = sum(1 for x in xs if is_gutter(px[x, y]))
        rowfill.append(n / len(xs) < gut)          # True where the row has content

    rows = bands(rowfill, int(H * min_freq / step))
    boxes = []
    for r0, r1 in rows:
        y0, y1 = r0 * step, min(r1 * step, H)
        colfill = []
        for x in xs:
            n = sum(1 for y in range(y0, y1, step) if is_gutter(px[x, y]))
            colfill.append(n / max(1, len(range(y0, y1, step))) < gut)
        cols = bands(colfill, int(W * min_freq / step))
        for c0, c1 in cols:
            x0, x1 = c0 * step, min(c1 * step, W)
            if (x1 - x0) < W * 0.06 or (y1 - y0) < H * 0.04:
                continue
            boxes.append([round(x0 / W, 5), round(y0 / H, 5),
                          round((x1 - x0) / W, 5), round((y1 - y0) / H, 5)])
    return boxes


def contact(path, boxes, out):
    """Write every detected box as a strip, so they can be checked by eye."""
    im = Image.open(path).convert("RGB")
    W, H = im.size
    tw = 260
    crops = []
    for b in boxes:
        c = im.crop((int(b[0]*W), int(b[1]*H), int((b[0]+b[2])*W), int((b[1]+b[3])*H)))
        th = max(1, int(c.height * tw / c.width))
        crops.append(c.resize((tw, th)))
    cols = 4
    rows = (len(crops) + cols - 1) // cols
    rh = max(c.height for c in crops) + 8
    sheet = Image.new("RGB", (cols * (tw + 8), rows * rh), (20, 20, 20))
    for i, c in enumerate(crops):
        sheet.paste(c, ((i % cols) * (tw + 8), (i // cols) * rh))
    sheet.save(out)


def main(keys=None):
    pj = os.path.join(COMICS, "panels.json")
    data = json.load(open(pj)) if os.path.exists(pj) else {}
    todo = keys or sorted(
        os.path.basename(p)[:-5] for p in os.listdir(COMICS)
        if p.endswith(".webp") and not p.endswith("-sm.webp"))
    for k in todo:
        src = os.path.join(COMICS, k + ".webp")
        if not os.path.exists(src):
            print("  missing", k); continue
        b = detect(src)
        data[k] = b
        contact(src, b, "/tmp/claude-0/contact_%s.png" % k)
        print("%-28s %2d units" % (k, len(b)))
    json.dump(data, open(pj, "w"), separators=(",", ":"))
    print("panels.json written, %d comics" % len(data))


if __name__ == "__main__":
    main(sys.argv[1:] or None)
