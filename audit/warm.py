"""Warm the palette without moving contrast.

The trick is to hold relative luminance constant. Warming a colour normally
brightens it, because red and green carry most of the perceived luminance, and
that would shift every contrast ratio on the site. Here the shift is applied,
then the result is scaled back until its luminance matches the original.
"""
import re

def lum(rgb):
    s=[]
    for v in rgb:
        v/=255
        s.append(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4)
    return .2126*s[0]+.7152*s[1]+.0722*s[2]

def to_rgb(h):
    h=h.lstrip("#")
    return [int(h[i:i+2],16) for i in (0,2,4)]

def to_hex(rgb):
    return "#%02X%02X%02X" % tuple(max(0,min(255,round(v))) for v in rgb)

def warm(hexcol, amount=0.055):
    """Nudge a colour toward amber, then restore its original luminance."""
    rgb = to_rgb(hexcol)
    target = lum(rgb)
    r,g,b = rgb
    mx = max(rgb)
    # skip colours that are already strongly warm, and pure white/black
    if r - b > 60: return hexcol
    if mx == 0: 
        # near-black still takes a warm tint, just a small absolute one
        out = [r+3, g+2, b+0]
        return to_hex(out)
    # push red up, blue down, green slightly up. the span is capped so a light
    # colour does not turn yellow: "a little warmer" not "amber".
    span = min(14.0, max(4.0, mx*amount))
    out = [r + span, g + span*0.55, b - span*0.65]
    # restore luminance so no contrast ratio moves
    if target > 0:
        for _ in range(24):
            cur = lum(out)
            if cur <= 0: break
            k = (target/cur) ** 0.5
            if abs(k-1) < 0.0015: break
            out = [v*k for v in out]
    return to_hex(out)

if __name__ == "__main__":
    print(f"{'before':9s} {'after':9s} {'lum before':>11} {'lum after':>10}  drift")
    for c in ["#050505","#0B0B0C","#161512","#C9C9C9","#E6E6E6","#2A2A2A",
              "#1C1C1C","#3D3D3D","#DCD7CC","#9C968D","#B9B4AB","#FFFFFF"]:
        w=warm(c)
        a,b=lum(to_rgb(c)), lum(to_rgb(w))
        drift = abs(a-b)/max(a,1e-6)*100
        print(f"  {c}  {w}  {a:>10.5f} {b:>10.5f}  {drift:>5.2f}%")
