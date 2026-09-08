"""Turn a SideKix worksheet .txt into a structure the page generator can render.

The ten files in assets/worksheets share one layout, so this reads the layout
rather than hard-coding each sheet:

    TITLE                     first line
    subtitle                  second line
    -- SECTION --------       a section
    (hint)                    a parenthetical under a section heading
    [ ] item                  a checkbox
    Label:                    a label for the blanks that follow
    ______                    one blank line of writing space
    A | B | C                 a table header, followed by a rule and blank rows
"""
import re, io

def parse(path):
    raw = io.open(path, encoding="utf-8").read().replace("\r\n", "\n")
    lines = raw.split("\n")
    title = lines[0].strip()
    subtitle = lines[1].strip() if len(lines) > 1 else ""
    body = lines[2:]
    sections, cur = [], None
    i = 0
    while i < len(body):
        ln = body[i].rstrip()
        s = ln.strip()
        i += 1
        if not s or set(s) <= set("=") or s.startswith("SideKix") or s == "sidekixhq.com":
            continue
        m = re.match(r"^--\s+(.+?)\s+-+$", s)
        if m:
            cur = {"name": m.group(1).strip(), "items": []}
            sections.append(cur)
            continue
        if cur is None:
            cur = {"name": "", "items": []}
            sections.append(cur)
        if s.startswith("*"):
            cur["items"].append({"t": "note", "text": s.lstrip("* ").strip()}); continue
        if re.match(r"^\(.*\)$", s):
            cur["items"].append({"t": "hint", "text": s[1:-1].strip()}); continue
        if s.startswith("[ ]"):
            cur["items"].append({"t": "check", "text": s[3:].strip()}); continue
        if "|" in s and "_" not in s:
            cols = [c.strip() for c in s.split("|")]
            rows = 0
            while i < len(body):
                nxt = body[i].strip()
                if set(nxt) <= set("-") and nxt:
                    i += 1; continue
                if "|" in nxt and "_" in nxt:
                    rows += 1; i += 1; continue
                break
            cur["items"].append({"t": "table", "cols": cols, "rows": max(rows, 3)}); continue
        if set(s) <= set("_") and s:
            n = 1
            while i < len(body) and set(body[i].strip()) <= set("_") and body[i].strip():
                n += 1; i += 1
            if cur["items"] and cur["items"][-1]["t"] == "label":
                lab = cur["items"].pop()["text"]
            else:
                lab = ""
            cur["items"].append({"t": "write", "label": lab, "lines": n}); continue
        if set(s) <= set("-") and s:
            continue
        cur["items"].append({"t": "label", "text": s})
    # a trailing label with nothing under it is a stray
    for sec in sections:
        while sec["items"] and sec["items"][-1]["t"] == "label":
            sec["items"].pop()
    sections = [s for s in sections if s["items"]]
    return {"title": title, "subtitle": subtitle, "sections": sections}
