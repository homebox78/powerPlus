"""v0.49 - reference tone for content shapes (whole deck). args: src dst
   1) repeated same-size blue shapes (3+ in a slide) = column heads/cells: mid blue -> light head + navy text,
      the navy one stays as the single emphasis.
   2) big mid-blue panel -> light face + navy text.
   3) slide 5: body boxes white + line, body text color; stage 3 head stays navy.
   Pictures untouched."""
import sys, collections
from lxml import etree
sys.argv_keep = sys.argv[:]
SRC, DST = sys.argv[1], sys.argv[2]
src = open(__file__.replace("tone_ref6", "tone_ref5"), encoding="utf-8").read().split("for n, sl in enumerate")[0]
exec(src)
BODY, MID, DARK, LINE, WHITE = "2F3B6F", "2F78E0", "0B2E6B", "C2DCF5", "FFFFFF"
def recolor(el, hexv):
    global NAVY
    keep = NAVY; NAVY = hexv
    try: return navy_runs(el, True)
    finally: NAVY = keep
def set_line(s, hexv, w=9525):
    sp = spPr(s); ln = sp.find(A + "ln")
    if ln is None:
        ln = etree.Element(A + "ln")
        idx = [i for i, c in enumerate(sp) if c.tag in (A + "solidFill", A + "gradFill", A + "noFill")]
        sp.insert((idx[-1] + 1) if idx else len(sp), ln)
    for c in list(ln):
        if c.tag in (A + "solidFill", A + "gradFill", A + "noFill", A + "pattFill"): ln.remove(c)
    sf = etree.Element(A + "solidFill"); etree.SubElement(sf, A + "srgbClr", val=hexv); ln.insert(0, sf)
    ln.set("w", str(w))
for n, sl in enumerate(p.slides, 1):
    fs = list(flat(sl.shapes)); conv = {}
    blue = [(s, x, y, w, h, fc(spPr(s)).get("val").upper()) for s, x, y, w, h in fs if fc(spPr(s)) is not None and fc(spPr(s)).get("val").upper() in (MID, DARK)]
    for s, x, y, w, h, v in blue:
        if v != MID: continue
        to = None
        if n == 5:
            to = WHITE if h > E else TH
        elif w > 2 * E and h > 1.5 * E:
            to = FACE
        elif w > 0.7 * E:
            sib = [b for b in blue if abs(b[3] - w) < 0.04 * w and abs(b[4] - h) < 0.04 * h]
            if len(sib) >= 3: to = TH
        if to:
            fc(spPr(s)).set("val", to); conv[id(s)] = (x, y, w, h, to); cnt[to] += 1
            if to == WHITE: set_line(s, LINE)
            tb = s._element.find(P + "txBody")
            if tb is not None: cnt["txt"] += recolor(tb, BODY if to == WHITE else NAVY)
    if n == 5:
        for s, x, y, w, h in fs:
            c5 = fc(spPr(s))
            if c5 is not None and c5.get("val").upper() == TH and h > E and w > 2 * E:
                c5.set("val", WHITE); set_line(s, LINE); conv[id(s)] = (x, y, w, h, WHITE)
        for s, x, y, w, h, v in blue:
            if v == DARK and h > E and w > 2 * E:
                fc(spPr(s)).set("val", WHITE); set_line(s, LINE); conv[id(s)] = (x, y, w, h, WHITE)
        for s, x, y, w, h in fs:
            ln = spPr(s).find(A + "ln") if spPr(s) is not None else None
            if ln is not None and s.shape_type == 9:
                for sc in ln.iter(A + "schemeClr"):
                    if sc.get("val") == "bg1":
                        par = sc.getparent(); par.remove(sc); etree.SubElement(par, A + "srgbClr", val=LINE)
            if s.has_text_frame and s.text_frame.text.startswith("2004"): set_line(s, "EC1C68", 12700)
    if not conv: continue
    filled = [(x, y, w, h, id(s)) for s, x, y, w, h in fs if spPr(s) is not None and (spPr(s).find(A + "solidFill") is not None or spPr(s).find(A + "gradFill") is not None)]
    for s, x, y, w, h in fs:
        tb = s._element.find(P + "txBody")
        if tb is None or id(s) in conv or not s.text_frame.text.strip(): continue
        sp = spPr(s)
        if sp.find(A + "solidFill") is not None or sp.find(A + "gradFill") is not None: continue
        cx, cy = x + w / 2, y + h / 2
        under = [f for f in filled if f[0] <= cx <= f[0] + f[2] and f[1] <= cy <= f[1] + f[3]]
        if not under: continue
        top = min(under, key=lambda f: f[2] * f[3])
        if top[4] in conv:
            cnt["over"] += recolor(tb, BODY if conv[top[4]][4] == WHITE else NAVY)
print(dict(cnt))
p.save(DST)
