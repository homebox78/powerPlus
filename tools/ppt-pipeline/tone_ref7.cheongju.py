"""v0.50 - step chains get graded faces, arrow tails go transparent. args: src dst
   1) step chain = chevron/homePlate of same height in one row (2+): faces light -> strong by x order,
      text navy on light, white on strong. An existing navy step stays navy.
   2) gradient block arrows (custom pentagon / rightArrow): tail stop alpha 0, head stop solid blue."""
import sys, collections
from lxml import etree
from pptx import Presentation
sys.stdout.reconfigure(encoding="utf-8")
A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
P = "{http://schemas.openxmlformats.org/presentationml/2006/main}"
E = 914400
NAVY, WHITE, MID = "0B2E6B", "FFFFFF", "2F78E0"
RAMP = {1: [MID], 2: ["D0E6FA", "A9CBF5"], 3: ["D0E6FA", "A9CBF5", MID], 4: ["D0E6FA", "A9CBF5", "78A8F0", MID]}
p = Presentation(sys.argv[1]); cnt = collections.Counter()
def spPr(s): return s._element.find(P + "spPr")
def flat(shapes, tf=(0, 0, 1, 1)):
    ox, oy, sx, sy = tf
    for s in shapes:
        if s.width is None: continue
        if s.shape_type == 6:
            x = s._element.find(P + "grpSpPr").find(A + "xfrm"); co, ce = x.find(A + "chOff"), x.find(A + "chExt")
            kx = s.width / int(ce.get("cx")) if int(ce.get("cx")) else 1; ky = s.height / int(ce.get("cy")) if int(ce.get("cy")) else 1
            gx, gy = ox + s.left * sx, oy + s.top * sy
            yield from flat(s.shapes, (gx - int(co.get("x")) * kx * sx, gy - int(co.get("y")) * ky * sy, sx * kx, sy * ky))
        else: yield s, ox + s.left * sx, oy + s.top * sy, s.width * sx, s.height * sy
def set_runs(el, hexv):
    for r in el.iter(A + "r"):
        rp = r.find(A + "rPr")
        if rp is None:
            rp = etree.Element(A + "rPr"); r.insert(0, rp)
        for t in ("solidFill", "gradFill", "noFill", "pattFill"):
            for e in rp.findall(A + t): rp.remove(e)
        sf = etree.Element(A + "solidFill"); etree.SubElement(sf, A + "srgbClr", val=hexv)
        ln = rp.find(A + "ln"); rp.insert((list(rp).index(ln) + 1) if ln is not None else 0, sf)
def prst(s):
    sp = spPr(s); g = sp.find(A + "prstGeom") if sp is not None else None
    return g.get("prst") if g is not None else None
for n, sl in enumerate(p.slides, 1):
    fs = list(flat(sl.shapes))
    steps = []
    for s, x, y, w, h in fs:
        sp = spPr(s)
        if prst(s) in ("chevron", "homePlate") and sp.find(A + "solidFill") is not None and sp.find(A + "solidFill").find(A + "srgbClr") is not None:
            xf = sp.find(A + "xfrm")
            if xf is not None and xf.get("rot", "0") != "0": continue
            if 0.3 * E <= h <= 0.7 * E and 0.9 * E <= w <= 3 * E: steps.append((s, x, y, w, h))
    rows = []
    for it in sorted(steps, key=lambda t: t[2]):
        for r in rows:
            if abs(r[0][2] - it[2]) < 0.08 * E and abs(r[0][4] - it[4]) < 0.05 * E: r.append(it); break
        else: rows.append([it])
    for r in rows:
        r.sort(key=lambda t: t[1])
        if len(r) < 2 or len(r) > 5: continue
        cols = [spPr(t[0]).find(A + "solidFill").find(A + "srgbClr") for t in r]
        tail_navy = cols[-1].get("val").upper() == NAVY
        m = len(r) - (1 if tail_navy else 0)
        # slide 5: the two steps lead into a navy stage -> stay light
        ramp = RAMP[2] if (n == 5) else RAMP.get(m, RAMP[4])
        for i, t in enumerate(r):
            if tail_navy and i == len(r) - 1: hexv = NAVY
            else: hexv = ramp[min(i, len(ramp) - 1)]
            c = cols[i]
            for a in list(c): c.remove(a)
            c.set("val", hexv); cnt["step"] += 1
            tc = WHITE if hexv in (MID, NAVY) else NAVY
            s, x, y, w, h = t
            if s.has_text_frame and s.text_frame.text.strip(): set_runs(s._element, tc)
            for o, ox, oy, ow, oh in fs:
                if o is s or not getattr(o, "has_text_frame", False) or not o.text_frame.text.strip(): continue
                osp = spPr(o)
                if osp is not None and (osp.find(A + "solidFill") is not None or osp.find(A + "gradFill") is not None): continue
                cx, cy = ox + ow / 2, oy + oh / 2
                if x <= cx <= x + w and y <= cy <= y + h and oh < h * 1.6:
                    set_runs(o._element, tc); cnt["step_txt"] += 1
    for s, x, y, w, h in fs:
        sp = spPr(s)
        if sp is None: continue
        g = sp.find(A + "gradFill")
        if g is None: continue
        k = prst(s)
        if not (k == "rightArrow" or (k is None and s.name.startswith("오각형"))): continue
        stops = sorted(g.iter(A + "gs"), key=lambda e: int(e.get("pos")))
        if len(stops) != 2: continue
        small = h < 0.6 * E
        head = MID if small else "78A8F0"
        for e, alpha in ((stops[0], "0"), (stops[1], None if small else "70000")):
            for c in list(e): e.remove(c)
            c = etree.SubElement(e, A + "srgbClr", val=head)
            if alpha is not None: etree.SubElement(c, A + "alpha", val=alpha)
        cnt["arrow"] += 1
print(dict(cnt))
p.save(sys.argv[2])
