def hx(c):
    c=c.lstrip('#')
    if len(c)==3: c="".join(ch*2 for ch in c)
    return tuple(int(c[i:i+2],16) for i in (0,2,4))
def lin(v):
    v/=255.0
    return v/12.92 if v<=0.04045 else ((v+0.055)/1.055)**2.4
def lum(rgb):
    r,g,b=[lin(x) for x in rgb]
    return 0.2126*r+0.7152*g+0.0722*b
def ratio(a,b):
    la,lb=lum(hx(a)),lum(hx(b))
    hi,lo=max(la,lb),min(la,lb)
    return (hi+0.05)/(lo+0.05)
def over(fg,bg,alpha):
    """flatten a translucent colour onto a background"""
    f,b=hx(fg),hx(bg)
    return '#%02x%02x%02x'%tuple(round(f[i]*alpha+b[i]*(1-alpha)) for i in range(3))
def mix(a,b,pct):
    """css color-mix(in srgb, a pct%, b)"""
    ra,rb=hx(a),hx(b)
    p=pct/100
    return '#%02x%02x%02x'%tuple(round(ra[i]*p+rb[i]*(1-p)) for i in range(3))

def check(label,fg,bg,size_px,bold=False,ui=False):
    r=ratio(fg,bg)
    large = size_px>=24 or (bold and size_px>=18.66)
    need = 3.0 if (ui or large) else 4.5
    tag="PASS" if r>=need else ("FAIL" if r<need else "")
    kind="UI/large" if (ui or large) else "text"
    return (tag,round(r,2),need,kind,label,fg,bg,size_px)
