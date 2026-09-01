"""Render each worksheet's HTML blocks as plain text for copy and paste."""
import sys, re, os; sys.path.insert(0,'/home/claude/build')
from bs4 import BeautifulSoup
import gen  # populates gen.W

RULE = "_"*58

def to_text(cfg):
    L = [cfg["title"].upper(), cfg["dek"], "", "SideKix  |  sidekixhq.com", "="*58, ""]
    for blk in cfg["blocks"]:
        s = BeautifulSoup(blk, "lxml")
        el = s.body.find(recursive=False) if s.body else None
        if el is None: continue
        cls = el.get("class") or []
        if el.name == "h2":
            num = el.select_one(".n")
            t = el.get_text(" ", strip=True)
            if num: t = t.replace(num.get_text(strip=True), "", 1).strip()
            L += ["", f"-- {t.upper()} " + "-"*max(0, 54-len(t)), ""]
        elif el.name == "p" and "hint" in cls:
            L += [f"({el.get_text(' ', strip=True)})", ""]
        elif el.name == "p":
            L += [el.get_text(" ", strip=True), ""]
        elif "note" in cls:
            L += ["* " + el.get_text(" ", strip=True), ""]
        elif "field" in cls:
            lab = el.select_one(".lab").get_text(" ", strip=True)
            n = len(el.select(".rule"))
            L += ([lab + ":"] if lab else []) + [RULE]*n + [""]
        elif el.name == "ul":
            L += ["[ ] " + li.get_text(" ", strip=True) for li in el.select("li")] + [""]
        elif el.name == "table":
            heads = [th.get_text(" ", strip=True) for th in el.select("th")]
            nrows = len(el.select("tbody tr"))
            L += [" | ".join(heads), "-"*58] + [" | ".join([RULE[:max(6,54//len(heads))]]*len(heads))
                                                for _ in range(nrows)] + [""]
    L += ["", "="*58, "SideKix  |  Talent is everywhere. Opportunity is for all.",
          "sidekixhq.com"]
    out = "\n".join(L)
    return re.sub(r"\n{3,}", "\n\n", out).strip() + "\n"

os.makedirs("/home/claude/site/assets/worksheets", exist_ok=True)
made = {}
for slug, cfg in gen.W.items():
    t = to_text(cfg)
    p = f"/home/claude/site/assets/worksheets/{slug}.txt"
    open(p, "w", encoding="utf-8").write(t)
    made[slug] = t
    print(f"  {len(t):5d} chars  {slug}.txt")

print("\n----- sample: weekly check-in -----")
print(made["weekly-business-check-in-template"][:900])
