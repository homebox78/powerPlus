"""콘텐츠 요소(TH·TD·작은 머리) 톤: 짙은 채움 + 흰 글자 → 옅은 면 + 남색 글자. 인자: 원본 결과
   머리(TH) CCE3FD + 남색 굵은 글자 / 칸(TD) F1F7FE / 묶는 면 E1EEFD. 구역 제목 띠(1·2단계)는 그대로."""
import sys, collections
from pptx import Presentation
from lxml import etree
sys.stdout.reconfigure(encoding="utf-8")
A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"; P = "{http://schemas.openxmlformats.org/presentationml/2006/main}"; E = 914400
TH, TD, FACE, NAVY = "CCE3FD", "F1F7FE", "E1EEFD", "0B2E6B"
p = Presentation(sys.argv[1]); cnt = collections.Counter()
def spPr(s): return s._element.find(P + "spPr")
def fc(sp):
    sf = sp.find(A + "solidFill") if sp is not None else None
    c = sf.find(A + "srgbClr") if sf is not None else None
    return c
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
def navy_runs(el, force):
    """흰 글자(명시·테마 bg1·상속)를 남색으로. 색 있는 글자는 그대로."""
    n = 0
    for r in el.iter(A + "r"):
        rp = r.find(A + "rPr")
        if rp is None:
            if not force: continue
            rp = etree.Element(A + "rPr"); r.insert(0, rp)
        if any(rp.find(A + t) is not None for t in ("noFill", "pattFill", "blipFill")): continue
        gf = rp.find(A + "gradFill")
        if gf is not None:                      # 흰색만으로 된 그라데이션 글자 = 흰 글자
            stops = list(gf.iter(A + "gs"))
            def w(g):
                c, sc = g.find(A + "srgbClr"), g.find(A + "schemeClr")
                return (c is not None and c.get("val").upper() == "FFFFFF") or (sc is not None and sc.get("val") in ("bg1", "lt1") and len(sc) == 0)
            if not stops or not all(w(g) for g in stops): continue
            i = list(rp).index(gf); rp.remove(gf)
            sf = etree.Element(A + "solidFill"); etree.SubElement(sf, A + "srgbClr", val=NAVY); rp.insert(i, sf); n += 1
            continue
        sf = rp.find(A + "solidFill")
        if sf is not None:
            c, sc, pc = sf.find(A + "srgbClr"), sf.find(A + "schemeClr"), sf.find(A + "prstClr")
            white = (c is not None and c.get("val").upper() == "FFFFFF") or (sc is not None and sc.get("val") in ("bg1", "lt1")) or (pc is not None and pc.get("val") == "white")
            if not white: continue
            rp.remove(sf)
        elif not force: continue
        sf = etree.Element(A + "solidFill"); etree.SubElement(sf, A + "srgbClr", val=NAVY)
        pos = 1 if rp.find(A + "ln") is not None else 0
        rp.insert(pos, sf); n += 1
    return n
for n, sl in enumerate(p.slides, 1):
    fs = list(flat(sl.shapes)); conv = []
    for s, x, y, w, h in fs:
        c = fc(spPr(s))
        if c is None: continue
        v = c.get("val").upper()
        if v == "78A8F0":                       # 3단계 = 콘텐츠 안 머리(TH)
            c.set("val", TH); cnt["th"] += 1; conv.append((x, y, w, h))
            tb = s._element.find(P + "txBody")
            if tb is not None: cnt["txt"] += navy_runs(tb, True)
        elif v == "D0E6FA" and w > 1.0 * E and h > 0.7 * E: c.set("val", FACE); cnt["face"] += 1
        elif v == "E8F2FC": c.set("val", TD); cnt["td"] += 1
    # 머리 위에 따로 얹힌 흰 글상자
    filled = [(x, y, w, h, fc(spPr(s)).get("val").upper()) for s, x, y, w, h in fs if fc(spPr(s)) is not None]
    for s, x, y, w, h in fs:
        tb = s._element.find(P + "txBody")
        if tb is None or fc(spPr(s)) is not None: continue
        cx, cy = x + w / 2, y + h / 2
        under = [f for f in filled if f[0] <= cx <= f[0] + f[2] and f[1] <= cy <= f[1] + f[3]]
        if under and min(under, key=lambda f: f[2] * f[3])[4] == TH: cnt["over"] += navy_runs(tb, True)
    # 표
    for tc in sl._element.iter(A + "tc"):
        pr = tc.find(A + "tcPr"); sf = pr.find(A + "solidFill") if pr is not None else None
        c = sf.find(A + "srgbClr") if sf is not None else None
        if c is not None and c.get("val").upper() in ("0B2E6B", "2F78E0", "78A8F0", TH):
            c.set("val", TH); cnt["tc"] += 1; navy_runs(tc, True)
print(dict(cnt)); p.save(sys.argv[2])
