"""v0.52 - every content slide carries one deep-navy highlight face (tone 143A69). args: src dst
   1) existing navy faces 0B2E6B -> 143A69 (shape/table fills only, text untouched)
   2) slides without a navy face: slide 6 left section labels, slide 37 band -> navy + white text."""
import sys, collections
from lxml import etree
from pptx import Presentation
sys.stdout.reconfigure(encoding="utf-8")
A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
P = "{http://schemas.openxmlformats.org/presentationml/2006/main}"
E = 914400; HL = "143A69"
p = Presentation(sys.argv[1]); cnt = collections.Counter()
def flat(shapes, tf=(0, 0, 1, 1)):
    ox, oy, sx, sy = tf
    for s in shapes:
        if s.width is None: continue
        if s.shape_type == 6:
            x = s._element.find(P + "grpSpPr").find(A + "xfrm"); co, ce = x.find(A + "chOff"), x.find(A + "chExt")
            kx = s.width / int(ce.get("cx")) if int(ce.get("cx")) else 1; ky = s.height / int(ce.get("cy")) if int(ce.get("cy")) else 1
            yield from flat(s.shapes, (ox + s.left * sx - int(co.get("x")) * kx * sx, oy + s.top * sy - int(co.get("y")) * ky * sy, sx * kx, sy * ky))
        else: yield s, ox + s.left * sx, oy + s.top * sy, s.width * sx, s.height * sy
def white(el):
    for r in el.iter(A + "r"):
        rp = r.find(A + "rPr")
        if rp is None:
            rp = etree.Element(A + "rPr"); r.insert(0, rp)
        for t in ("solidFill", "gradFill", "noFill", "pattFill"):
            for e in rp.findall(A + t): rp.remove(e)
        sf = etree.Element(A + "solidFill"); etree.SubElement(sf, A + "srgbClr", val="FFFFFF")
        ln = rp.find(A + "ln"); rp.insert((list(rp).index(ln) + 1) if ln is not None else 0, sf)
def fillc(s):
    sp = s._element.find(P + "spPr"); sf = sp.find(A + "solidFill") if sp is not None else None
    return sf.find(A + "srgbClr") if sf is not None else None
for n, sl in enumerate(p.slides, 1):
    for c in sl._element.iter(A + "srgbClr"):
        par = c.getparent().getparent()
        if c.get("val").upper() == "0B2E6B" and par.tag in (P + "spPr", A + "tcPr", A + "ln"):
            c.set("val", HL); cnt["navy"] += 1
    if n not in (6, 37): continue
    fs = list(flat(sl.shapes)); done = []
    for s, x, y, w, h in fs:
        c = fillc(s)
        if c is None: continue
        v = c.get("val").upper()
        if (n == 6 and v == "CCE3FD" and x < 1.2 * E and w < 1.6 * E and h > 0.4 * E) or (n == 37 and v == "2F78E0" and w > 4 * E):
            for a in list(c): c.remove(a)
            c.set("val", HL); white(s._element); done.append((x, y, w, h)); cnt["add"] += 1
    for s, x, y, w, h in fs:
        if not getattr(s, "has_text_frame", False) or not s.text_frame.text.strip() or fillc(s) is not None: continue
        cx, cy = x + w / 2, y + h / 2
        if any(a <= cx <= a + c_ and b <= cy <= b + d for a, b, c_, d in done): white(s._element); cnt["txt"] += 1
print(dict(cnt)); p.save(sys.argv[2])
