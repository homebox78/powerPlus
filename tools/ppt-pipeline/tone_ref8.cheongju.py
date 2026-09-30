"""v0.51 - args: src dst
   A) slide 16: both pills navy + white, cards one light face (no line), navy titles, pink bullets + pink rule, 3D icons on top.
   B) whole deck: neutral gray text -> blue-toned gray.
   C) slide 5: the (2024~2025 ...) line keeps its emphasis inside the navy box (light face + navy text)."""
import sys, io, json, colorsys, collections, copy, urllib.request
from lxml import etree
from pptx import Presentation
from pptx.util import Emu
sys.stdout.reconfigure(encoding="utf-8")
A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
P = "{http://schemas.openxmlformats.org/presentationml/2006/main}"
E = 914400
NAVY, WHITE, PINK, FACE, BGRAY = "0B2E6B", "FFFFFF", "EC1C68", "E1EEFD", "5F7496"
ICONS = ["icon_1446", "icon_1326", "icon_1279", "icon_1264", "icon_1666", "icon_1642", "icon_1691", "icon_1416"]
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
        else: yield s, ox + s.left * sx, oy + s.top * sy, s.width * sx, s.height * sy, sy
def set_fill(s, hexv):
    sp = spPr(s)
    for t in ("solidFill", "gradFill", "noFill", "pattFill"):
        for e in sp.findall(A + t): sp.remove(e)
    sf = etree.Element(A + "solidFill"); etree.SubElement(sf, A + "srgbClr", val=hexv)
    g = sp.find(A + "prstGeom"); g = g if g is not None else sp.find(A + "custGeom")
    sp.insert(list(sp).index(g) + 1, sf)
def no_line(s):
    sp = spPr(s); ln = sp.find(A + "ln")
    if ln is None:
        ln = etree.Element(A + "ln"); sf = sp.find(A + "solidFill"); sp.insert(list(sp).index(sf) + 1, ln)
    for c in list(ln): ln.remove(c)
    etree.SubElement(ln, A + "noFill")
def set_line(s, hexv):
    sp = spPr(s); ln = sp.find(A + "ln")
    if ln is None: return
    for c in list(ln):
        if c.tag in (A + "solidFill", A + "noFill", A + "gradFill"): ln.remove(c)
    sf = etree.Element(A + "solidFill"); etree.SubElement(sf, A + "srgbClr", val=hexv); ln.insert(0, sf)
def set_runs(el, hexv, bold=None):
    for r in el.iter(A + "r"):
        rp = r.find(A + "rPr")
        if rp is None:
            rp = etree.Element(A + "rPr"); r.insert(0, rp)
        for t in ("solidFill", "gradFill", "noFill", "pattFill"):
            for e in rp.findall(A + t): rp.remove(e)
        sf = etree.Element(A + "solidFill"); etree.SubElement(sf, A + "srgbClr", val=hexv)
        ln = rp.find(A + "ln"); rp.insert((list(rp).index(ln) + 1) if ln is not None else 0, sf)
def icon_urls():
    out = {}
    for q in ("유지관리", "조직", "서버", "비상", "보안", "성장", "교육"):
        u = "https://hom2box.com/powerPlus/api/public/assets?category=icon&limit=60&q=" + urllib.request.quote(q)
        for a in json.load(urllib.request.urlopen(u))["data"]: out[a["id"]] = a["image_url"]
    return out
# ---- A) slide 16
sl = p.slides[15]; fs = list(flat(sl.shapes))
heads, bodies = [], []
for s, x, y, w, h, k in fs:
    nm = s.name
    if nm.startswith("LBL_"):
        set_fill(s, NAVY); set_line(s, NAVY); set_runs(s._element, WHITE)
        for r in s.text_frame.paragraphs[0].runs: r.font.size = Emu(14 * 12700)
    elif nm.startswith("FAN_LBL_"): set_line(s, NAVY)
    elif nm.startswith("DOT_LBL_"): set_fill(s, NAVY)
    elif s.has_text_frame and s.text_frame.text.strip() and y > 4 * E and w < 1.4 * E:
        (heads if h < 1.2 * E else bodies).append((s, x, y, w, h, k))
urls = icon_urls()
heads.sort(key=lambda t: t[1]); bodies.sort(key=lambda t: t[1])
GROW = 0.32 * E
for i, (s, x, y, w, h, k) in enumerate(heads):
    set_fill(s, FACE); no_line(s); set_runs(s._element, NAVY)
    s.height = int(s.height + GROW / k)
    bp = s._element.find(P + "txBody").find(A + "bodyPr"); bp.set("anchor", "b"); bp.set("bIns", "36000")
    data = urllib.request.urlopen(urls[ICONS[i]]).read()
    sz = int(0.52 * E)
    sl.shapes.add_picture(io.BytesIO(data), int(x + (w - sz) / 2), int(y + 0.1 * E), sz, sz)
    bar = sl.shapes.add_shape(1, int(x + w / 2 - 0.15 * E), int(y + h + GROW + 0.04 * E), int(0.3 * E), int(0.02 * E))
    set_fill(bar, PINK); no_line(bar); cnt["icon"] += 1
for s, x, y, w, h, k in bodies:
    set_fill(s, FACE); no_line(s)
    s.top = int(s.top + GROW / k); s.height = int(s.height - GROW / k)
    bp = s._element.find(P + "txBody").find(A + "bodyPr"); bp.set("tIns", "108000")
    for pg in s._element.iter(A + "p"):
        pp = pg.find(A + "pPr")
        if pp is None: continue
        for e in pp.findall(A + "buClr") + pp.findall(A + "buClrTx"): pp.remove(e)
        bc = etree.Element(A + "buClr"); etree.SubElement(bc, A + "srgbClr", val=PINK)
        pos = [i for i, c in enumerate(pp) if c.tag in (A + "lnSpc", A + "spcBef", A + "spcAft")]
        pp.insert((pos[-1] + 1) if pos else 0, bc)
# ---- C) slide 5
for s, x, y, w, h, k in flat(p.slides[4].shapes):
    if s.has_text_frame and s.text_frame.text.strip().startswith("(2024"):
        set_fill(s, "CCE3FD"); set_runs(s._element, NAVY); cnt["s5"] += 1
# ---- D) slide 6: label faces visible, center pill pink, side pills light face
for s, x, y, w, h, k in flat(p.slides[5].shapes):
    sp = spPr(s)
    if sp is None: continue
    sf = sp.find(A + "solidFill"); c = sf.find(A + "srgbClr") if sf is not None else None
    if x < 1.2 * E and w < 1.6 * E and h > 0.4 * E and c is not None and c.find(A + "alpha") is not None:
        set_fill(s, "CCE3FD"); cnt["s6lbl"] += 1
    elif 1.3 * E < y < 2.4 * E and 0.45 * E < h < 1.0 * E and w > 1.0 * E:
        if c is not None and c.get("val").upper() == "2F78E0":
            set_fill(s, PINK); set_line(s, PINK); set_runs(s._element, WHITE); cnt["s6pink"] += 1
        elif sp.find(A + "ln") is not None and sp.find(A + "ln").find(A + "prstDash") is not None:
            set_fill(s, "CCE3FD"); no_line(s); cnt["s6side"] += 1
# ---- B) gray text -> blue-toned gray
TXT = {A + "rPr", A + "defRPr", A + "endParaRPr"}
for sl in p.slides:
    for sf in sl._element.iter(A + "solidFill"):
        if sf.getparent().tag not in TXT or not len(sf): continue
        c = sf[0]; gray = False
        if c.tag == A + "srgbClr":
            v = c.get("val")
            r, g, b = [int(v[i:i + 2], 16) / 255 for i in (0, 2, 4)]
            hh, ss, vv = colorsys.rgb_to_hsv(r, g, b)
            gray = ss < 0.12 and 0.3 <= vv <= 0.8
        elif c.tag == A + "prstClr":
            lo = c.find(A + "lumOff")
            gray = c.get("val") == "black" and lo is not None and int(lo.get("val")) >= 25000
        elif c.tag == A + "schemeClr":
            lm = c.find(A + "lumMod"); lo = c.find(A + "lumOff")
            if c.get("val") in ("bg1", "lt1") and lm is not None and 30000 <= int(lm.get("val")) <= 75000: gray = True
            if c.get("val") in ("tx1", "dk1") and lo is not None and int(lo.get("val")) >= 25000: gray = True
        if gray:
            sf.remove(c); etree.SubElement(sf, A + "srgbClr", val=BGRAY); cnt["gray"] += 1
print(dict(cnt))
p.save(sys.argv[2])
