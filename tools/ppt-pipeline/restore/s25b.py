# -*- coding: utf-8 -*-
"""25쪽(6. 비상대책) 다듬기. 인자: <src> <dst>
 1) 장애 처리 목록(Rectangle 114): 글자·줄간격 키워 상자 높이 약 90% 채움, 세로 가운데
 2) 백업 방법 상자(Rectangle 603): 문단을 내어쓰기로 다시 쓰고 줄간격 늘려 꽉 차게
 3) 절차도 '장애 발생' 폭발 도형 → 분홍 알약 + 흰 글자(a시월구일3), 연결선 위치 유지
 4) '장애대응3단계 & 절차' 제목이 번호 원과 겹치지 않게(제목 위로·단계 줄 살짝 아래로)
 5) 작은 글자(6.5~7pt) 키움: 단계 카드 8pt, 절차도 7.5~8pt
머리 띠 두 개(장애관리 방안·백업/복구 방안)는 bar_center.py 몫이라 건드리지 않는다."""
import sys, copy
from pptx import Presentation
from pptx.util import Pt, Emu
from pptx.oxml.ns import qn
from pptx.dml.color import RGBColor
sys.stdout.reconfigure(encoding="utf-8")
src, dst = sys.argv[1:3]
IN = 914400
prs = Presentation(src)
sl = prs.slides[24]


def walk(shs):
    for x in shs:
        yield x
        if x.shape_type == 6:
            yield from walk(x.shapes)


ALL = list(walk(sl.shapes))
def one(name):
    hit = [x for x in ALL if x.name == name]
    assert len(hit) == 1, (name, len(hit))
    return hit[0]
def many(name):
    return [x for x in ALL if x.name == name]


def set_font(rPr, face):
    for tg in ("a:latin", "a:ea"):
        e = rPr.find(qn(tg))
        if e is None:
            e = rPr.makeelement(qn(tg), {})
            # latin·ea 는 solidFill/gradFill 뒤, cs 앞
            cs = rPr.find(qn("a:cs"))
            if cs is not None:
                cs.addprevious(e)
            else:
                rPr.append(e)
        e.attrib.clear()
        e.set("typeface", face)


def size_all(shape, pt):
    for p in shape.text_frame.paragraphs:
        for r in p.runs:
            r.font.size = Pt(pt)
        epr = p._p.find(qn("a:endParaRPr"))
        if epr is not None:
            epr.set("sz", str(int(pt * 100)))
        for br in p._p.findall(qn("a:br")):
            rp = br.find(qn("a:rPr"))
            if rp is not None:
                rp.set("sz", str(int(pt * 100)))


def set_lnspc(pPr, pct=None, pts=None):
    for t in ("a:lnSpc",):
        e = pPr.find(qn(t))
        if e is not None:
            pPr.remove(e)
    ln = pPr.makeelement(qn("a:lnSpc"), {})
    if pct is not None:
        c = ln.makeelement(qn("a:spcPct"), {"val": str(int(pct * 1000))})
    else:
        c = ln.makeelement(qn("a:spcPts"), {"val": str(int(pts * 100))})
    ln.append(c)
    pPr.insert(0, ln)


def set_spc(pPr, tag, pts):
    e = pPr.find(qn(tag))
    if e is not None:
        pPr.remove(e)
    e = pPr.makeelement(qn(tag), {})
    e.append(e.makeelement(qn("a:spcPts"), {"val": str(int(pts * 100))}))
    # 순서: lnSpc, spcBef, spcAft, bu*
    ln = pPr.find(qn("a:lnSpc"))
    if tag == "a:spcBef":
        (ln.addnext(e) if ln is not None else pPr.insert(0, e))
    else:
        bef = pPr.find(qn("a:spcBef"))
        anchor = bef if bef is not None else ln
        (anchor.addnext(e) if anchor is not None else pPr.insert(0, e))


# ── 1) 장애 처리 목록 ─────────────────────────────────────────
HEAD_PT, SUB_PT, GAP_PT = 8.5, 8.0, 2.0
LN_PCT, HEAD_BEF, SUB_BEF = 100, 1.0, 0.0
r114 = one("Rectangle 114")
tf = r114.text_frame
bp = tf._txBody.find(qn("a:bodyPr"))
bp.set("anchor", "ctr")
bp.set("wrap", "square")
for k in ("lIns", "rIns"):
    bp.set(k, str(int(0.03 * IN)))
for k in ("tIns", "bIns"):
    bp.set(k, "0")
for p in tf.paragraphs:
    pPr = p._p.get_or_add_pPr()
    lvl = int(pPr.get("lvl", "0"))
    empty = not p.text.strip()
    if empty:
        set_lnspc(pPr, pts=GAP_PT)
        e = pPr.find(qn("a:spcBef"))
        if e is not None:
            pPr.remove(e)
        epr = p._p.find(qn("a:endParaRPr"))
        if epr is not None:
            epr.set("sz", "400")
        continue
    set_lnspc(pPr, pct=LN_PCT)
    set_spc(pPr, "a:spcBef", HEAD_BEF if lvl == 0 else SUB_BEF)
    if lvl:
        pPr.set("marL", str(int(0.20 * IN)))
        pPr.set("indent", str(int(-0.10 * IN)))
    else:
        pPr.set("marL", str(int(0.13 * IN)))
        pPr.set("indent", str(int(-0.13 * IN)))
    for r in p.runs:
        rPr = r._r.get_or_add_rPr()
        r.font.size = Pt(HEAD_PT if lvl == 0 else SUB_PT)
        set_font(rPr, "a시월구일3" if lvl == 0 else "a시월구일2")
# 낱말 중간 줄바꿈 방지: 긴 문장은 어절 앞에서 줄바꿈(문구 그대로)
BREAK = {"자체적으로 해결이 어려운 부분은 기술 전문가, 시스템 관련 팀 통보":
         "자체적으로 해결이 어려운 부분은"}
for p in tf.paragraphs:
    t = p.text.strip()
    if t in BREAK:
        head = BREAK[t]
        rs = p.runs
        full = "".join(r.text for r in rs)
        i = full.index(head) + len(head)
        a, b = full[:i], full[i:].lstrip()
        for r in rs[1:]:
            p._p.remove(r._r)
        rs[0].text = a
        br = rs[0]._r.makeelement(qn("a:br"), {})
        br.append(copy.deepcopy(rs[0]._r.find(qn("a:rPr"))))
        rs[0]._r.addnext(br)
        r2 = copy.deepcopy(rs[0]._r)
        r2.find(qn("a:t")).text = b
        br.addnext(r2)

# ── 2) 백업 방법 상자 ─────────────────────────────────────────
BK_PT, BK_LN, BK_GAP = 7.5, 105, 4
r603 = one("Rectangle 603")
tx = r603.text_frame._txBody
bp = tx.find(qn("a:bodyPr"))
bp.set("anchor", "ctr")
bp.set("lIns", str(int(0.07 * IN))); bp.set("rIns", str(int(0.05 * IN)))
bp.set("tIns", "0"); bp.set("bIns", "0")
ps = tx.findall(qn("a:p"))
proto = copy.deepcopy(ps[0])
for p0 in ps:
    tx.remove(p0)
ROWS = [  # (단계, 글, 강조)
    (0, "• 백업 방법", True),
    (1, "- DB Full 백업 수행", False),
    (1, "- DBMS는 아카이브|모드로 운영", False),
    (0, "• 복구 방법", True),
    (1, "- DB 장애", False),
    (2, ": DB Data와 Log정보|(Redo/Archive Log)를|적용하여 복구", False),
]   # '|' = 어절 앞 줄바꿈(낱말 중간 끊김 방지, 문구 그대로)
for i, (lvl, text, strong) in enumerate(ROWS):
    p = copy.deepcopy(proto)
    for e in p.findall(qn("a:r")) + p.findall(qn("a:br")):
        p.remove(e)
    epr = p.find(qn("a:endParaRPr"))
    if epr is not None:
        p.remove(epr)
    r = copy.deepcopy(proto.find(qn("a:r")))
    rPr = r.find(qn("a:rPr"))
    rPr.set("sz", str(int(BK_PT * 100)))
    rPr.set("spc", "-20")
    rPr.set("b", "0")
    sf = rPr.find(qn("a:solidFill"))
    sf.find(qn("a:srgbClr")).set("val", "1F4E79" if strong else "333333")
    set_font(rPr, "a시월구일3" if strong else "a시월구일2")
    for k, piece in enumerate(text.split("|")):
        if k:
            br = p.makeelement(qn("a:br"), {})
            br.append(copy.deepcopy(rPr))
            p.append(br)
        rk = copy.deepcopy(r)
        rk.find(qn("a:t")).text = piece
        p.append(rk)
    pPr = p.find(qn("a:pPr"))
    mar = {0: (0.09, -0.09), 1: (0.17, -0.08), 2: (0.20, -0.06)}[lvl]
    pPr.set("marL", str(int(mar[0] * IN))); pPr.set("indent", str(int(mar[1] * IN)))
    set_lnspc(pPr, pct=BK_LN)
    if lvl == 0 and i:
        set_spc(pPr, "a:spcBef", BK_GAP)
    tx.append(p)

# 상자 폭을 왼쪽으로 조금 넓힘(표와 0.1in 간격 유지) — 낱말이 줄 끝에서 안 쪼개지게
WIDEN = int(0.11 * IN)
g18 = one("Group 18")
gx = g18._element.grpSpPr.find(qn("a:xfrm"))
for tag, attr in (("a:off", "x"), ("a:chOff", "x")):
    e = gx.find(qn(tag)); e.set(attr, str(int(e.get(attr)) - WIDEN))
for tag, attr in (("a:ext", "cx"), ("a:chExt", "cx")):
    e = gx.find(qn(tag)); e.set(attr, str(int(e.get(attr)) + WIDEN))
r603.left -= WIDEN
r603.width += WIDEN

# ── 3) 장애 발생: 폭발 → 분홍 알약 ─────────────────────────────
ex = one("Explosion 546")
arrow = one("Freeform 28")
ay = arrow.top + arrow.height // 2
H = int(0.25 * IN)
W = int(0.72 * IN)
ex.left, ex.top, ex.width, ex.height = arrow.left - W, ay - H // 2, W, H
geom = ex._element.spPr.find(qn("a:prstGeom"))
geom.set("prst", "roundRect")
av = geom.find(qn("a:avLst"))
for c in list(av):
    av.remove(c)
av.append(av.makeelement(qn("a:gd"), {"name": "adj", "fmla": "val 50000"}))
st = ex._element.find(qn("p:style"))
if st is not None:
    st.find(qn("a:effectRef")).set("idx", "0")
ex.fill.solid(); ex.fill.fore_color.rgb = RGBColor(0xEC, 0x1C, 0x68)
ex.line.fill.background()
etf = ex.text_frame
etf.text = "장애 발생"
ebp = etf._txBody.find(qn("a:bodyPr"))
for k in ("lIns", "tIns", "rIns", "bIns"):
    ebp.set(k, "0")
ebp.set("wrap", "none"); ebp.set("anchor", "ctr")
ep = etf.paragraphs[0]
ep.alignment = 2
er = ep.runs[0]
er.font.size = Pt(9)
er.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
erp = er._r.get_or_add_rPr(); erp.set("b", "0")
set_font(erp, "a시월구일3")
tb = one("TextBox 547")
tb._element.getparent().remove(tb._element)

# ── 4) 제목과 번호 원 겹침 ─────────────────────────────────────
DOWN = int(0.03 * IN)  # 단계 줄(카드·번호·알약)을 살짝 내림 — 아래 큰 상자와는 여전히 떨어짐
for nm in ("시안 2", "시안 5", "시안 8", "시안 3", "시안 4", "시안 6", "시안 7", "시안 9", "시안 10"):
    one(nm).top += DOWN
for x in many("AutoShape 103") + many("Rectangle 104") + many("Rectangle 111"):
    x.top += DOWN
band = one("양쪽 모서리가 둥근 사각형 8")
circ = one("시안 4")
title = one("Text Box 453")
tbp = title.text_frame._txBody.find(qn("a:bodyPr"))
for c in list(tbp):
    tbp.remove(c)  # spAutoFit 제거
tbp.set("tIns", "0"); tbp.set("bIns", "0"); tbp.set("anchor", "ctr"); tbp.set("wrap", "square")
top = band.top + band.height + int(0.02 * IN)
title.top = top
title.height = circ.top - int(0.03 * IN) - top
grp_l = band.left
title.left = grp_l + (band.width - title.width) // 2
for p in title.text_frame.paragraphs:
    p.alignment = 2
    set_lnspc(p._p.get_or_add_pPr(), pct=100)
    for r in p.runs:
        if r.text.strip() == "3":
            r.font.size = Pt(16)
        else:
            r.font.size = Pt(14)  # 원본 14pt

# ── 5) 작은 글자 키우기 ───────────────────────────────────────
for x in many("Rectangle 104") + many("Rectangle 111"):
    size_all(x, 8)  # 원본 8pt
FLOW = {  # 이름: 크기(칸 높이에 맞춤)
    "Rectangle 548": 7.5, "Rectangle 550": 7.5,
    "Rectangle 549": 7, "Rectangle 551": 7,
    "TextBox 553": 7, "TextBox 555": 8, "TextBox 557": 7,
    "TextBox 560": 8, "Rectangle 561": 8, "Rectangle 562": 8,
    "TextBox 563": 8, "TextBox 564": 8, "TextBox 565": 8,
    "TextBox 566": 7.5, "TextBox 567": 8, "TextBox 568": 7.5, "TextBox 569": 7,
}
for nm, pt in FLOW.items():
    size_all(one(nm), pt)
# 통보 글은 오른쪽 '장애 처리 결과 보고' 상자에 닿지 않게 자간만 좁힘
for p in one("TextBox 569").text_frame.paragraphs:
    for r in p.runs:
        r._r.get_or_add_rPr().set("spc", "-60")

prs.save(dst)
print("25쪽 다듬기 저장:", dst)
