# -*- coding: utf-8 -*-
"""22쪽(3. 수행 조직의 구성 및 운영)을 원본 구조로 되살린다. 인자: <src> <dst>

사용자 지적: "라인 연계가 보여야 하고 그룹핑된 것들 카드 내용 등이 원본과 너무 다름,
지도 거점에 시청 위치도 추가". 카드형으로 재해석한 현재 장을 지우고, 원본 백업 22쪽의
도형·연결선·지도·인물 아이콘을 그대로 옮겨 온 뒤 톤(색·서체)만 지금 장표 규칙으로 바꾼다.

- 옮기지 않는 것: 원본 제목·키메시지·따옴표(현재 장의 것을 유지), '시청 추가' 웃는 얼굴 메모,
  뒤에 가려져 있던 중복 글상자(유지관리 및 지원 인력 / 전원 청주지역 거주).
- 연결선: 지역 지원→PM 꺾인 선(원본은 흰색이라 안 보였다)·지역 지원→원 3개 = 파랑 실선,
  원 3개→업무지원포털 상자·지도 거점→유지관리 인력 상자 = 회색 점선.
- 원본 글 그대로(대처 방안 4줄 전문). 절차 마지막 번호 5 → 6(원본 오기).
- 지도에 청주시청(상당로 155, 네 구가 만나는 시내 중심의 상당구 쪽) 핀 + '청주시청' 라벨 추가.
- 색: 남색 143A69 / 파랑 2F78E0 / 옅은 면 E8F2FC / 테두리 C0D2E6 / 회색 5F7496 / 분홍 EC1C68.
- 서체: 머리 a시월구일4, 강조 a시월구일3, 본문 a시월구일2(latin·ea). 합성 굵게 해제, 최소 9pt.
"""
import copy
import io
import os
import sys

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches as I, Pt

sys.stdout.reconfigure(encoding="utf-8")
src, dst = sys.argv[1:3]
ORIG = os.environ.get("S22_ORIG", "제안서/청주시_발표자료.원본백업.pptx")

p = Presentation(src)
s = p.slides[21]
o = Presentation(ORIG).slides[21]

NS_R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
F2, F3, F4 = "a시월구일2", "a시월구일3", "a시월구일4"

# ── 1. 현재 22쪽 본문 지우기(바탕·머리말 제목·키메시지만 남김) ─────────────────────
KEEP = {"시안 바탕", "시안 바탕2", "TextBox 113", "키메시지"}
for sh in list(s.shapes):
    if sh.name not in KEEP:
        sh._element.getparent().remove(sh._element)

# ── 2. 원본 도형 복사 ───────────────────────────────────────────────────────────────
SKIP = {114, 197, 206, 207, 115, 83}
tree = s.shapes._spTree
ids = [int(e.get("id")) for e in tree.iter(qn("p:cNvPr"))]
next_id = max(ids + [0]) + 1000
idmap = {}
copied = []
for sh in o.shapes:
    if sh.shape_id in SKIP:
        continue
    el = copy.deepcopy(sh._element)
    for c in el.iter(qn("p:cNvPr")):
        old = int(c.get("id"))
        idmap[old] = next_id
        c.set("id", str(next_id))
        next_id += 1
    # 그림 관계 다시 걸기
    for node in el.iter():
        for att in list(node.attrib):
            if att.startswith("{%s}" % NS_R) and att.split("}")[1] in ("embed", "link"):
                rid = node.get(att)
                part = o.part.related_part(rid)
                _, new = s.part.get_or_add_image_part(io.BytesIO(part.blob))
                node.set(att, new)
    tree.append(el)
    copied.append((sh.shape_id, el))
# 연결선 끝점 id 다시 매기기
for _, el in copied:
    for tag in ("a:stCxn", "a:endCxn"):
        for c in el.iter(qn(tag)):
            if int(c.get("id")) in idmap:
                c.set("id", str(idmap[int(c.get("id"))]))
            else:
                c.getparent().remove(c)

EL = dict(copied)


def sub(old_id):
    """원본 id 로 새 슬라이드의 도형(중첩 포함) 찾기."""
    nid = idmap[old_id]
    for sh in s.shapes:
        if sh.shape_id == nid:
            return sh
    def walk(shs):
        for x in shs:
            if x.shape_id == nid:
                return x
            if x.shape_type == 6:
                r = walk(x.shapes)
                if r is not None:
                    return r
    return walk(s.shapes)


# ── 3. 색 바꾸기 ───────────────────────────────────────────────────────────────────
CMAP = {
    "3A46A0": "143A69", "002060": "143A69", "45488B": "143A69", "3974B5": "143A69",
    "0037A4": "143A69", "152E54": "143A69",
    "0456B6": "2F78E0", "4D66D7": "2F78E0", "378CA7": "2F78E0", "3C9DBD": "2F78E0",
    "2A80FE": "2F78E0", "2363CB": "2F78E0", "0070C0": "2F78E0",
    "DEEBF7": "E8F2FC", "A2AAC2": "C0D2E6", "6F75A2": "C0D2E6",
    "CA253E": "EC1C68", "EB696D": "EC1C68", "EE4444": "EC1C68",
    "000000": "333333", "808080": "5F7496",
}
for _, el in copied:
    for c in el.iter(qn("a:srgbClr")):
        v = c.get("val").upper()
        if v in CMAP:
            c.set("val", CMAP[v])

NAVY = RGBColor(0x14, 0x3A, 0x69)
BLUE = RGBColor(0x2F, 0x78, 0xE0)
PINK = RGBColor(0xEC, 0x1C, 0x68)
GRAY = RGBColor(0x5F, 0x74, 0x96)
TXT = RGBColor(0x33, 0x33, 0x33)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

# 큰 상자 테두리 = 파랑 1pt
for oid in (53, 51):
    sh = sub(oid)
    sh.line.color.rgb = RGBColor(0xC0, 0xD2, 0xE6)
    sh.line.width = Pt(1)

# 배지 바깥 꽃잎은 옅게
badge = EL[211]
for c in badge.iter(qn("a:srgbClr")):
    if c.get("val") == "EC1C68" and c.getparent().getparent().tag == qn("p:spPr"):
        pass
# 부제 그림자 제거
for e in list(EL[90].iter(qn("a:effectLst"))):
    for ch in list(e):
        e.remove(ch)

# ── 4. 서체 ───────────────────────────────────────────────────────────────────────
FONT = {55: F4, 56: F4, 90: F3, 93: F3, 147: F3, 178: F3, 182: F3, 126: F3, 150: F3,
        184: F3, 185: F3, 187: F3, 188: F3, 190: F3, 192: F3, 213: F3,
        102: F3, 117: F3, 144: F3, 163: F3, 110: F3, 173: F3}


def set_face(rpr, f):
    for tag in ("a:latin", "a:ea"):
        e = rpr.find(qn(tag))
        if e is None:
            e = rpr.makeelement(qn(tag), {})
            # 스키마 순서: ln, fill, effect, highlight, uLnTx.., latin, ea, cs, sym, hlink..
            after = [rpr.find(qn(t)) for t in ("a:cs", "a:sym", "a:hlinkClick", "a:hlinkMouseOver", "a:rtl", "a:extLst")]
            after = [a for a in after if a is not None]
            if tag == "a:latin" and rpr.find(qn("a:ea")) is not None:
                after = [rpr.find(qn("a:ea"))] + after
            if after:
                after[0].addprevious(e)
            else:
                rpr.append(e)
        e.set("typeface", f)
    if rpr.get("b") is not None:
        rpr.attrib.pop("b")


for oid, el in copied:
    for txb in el.iter(qn("p:txBody")):
        sp = txb.getparent()
        sid = int(sp.find(".//" + qn("p:cNvPr")).get("id"))
        old = next((k for k, v in idmap.items() if v == sid), None)
        f = FONT.get(old, F2)
        for tag in ("a:rPr", "a:endParaRPr", "a:defRPr"):
            for r in txb.iter(qn(tag)):
                set_face(r, f)
                sz = r.get("sz")
                if sz is not None and int(sz) < 900 and tag != "a:defRPr":
                    r.set("sz", "900")

# 2줄 상자 첫 줄은 강조체
for oid in (78, 210):
    tf = sub(oid).text_frame
    for r in tf.paragraphs[0].runs:
        set_face(r._r.get_or_add_rPr(), F3)
# 배지 100% 는 머리체
for r in sub(213).text_frame.paragraphs[-1].runs:
    set_face(r._r.get_or_add_rPr(), F4)

# 글자 색
def color_runs(oid, rgb):
    for pg in sub(oid).text_frame.paragraphs:
        for r in pg.runs:
            r.font.color.rgb = rgb

for oid in (90, 144, 163, 110, 173):
    color_runs(oid, NAVY)
color_runs(95, TXT)
color_runs(117, GRAY)
color_runs(93, PINK)
color_runs(102, WHITE)
color_runs(181, TXT)
# 세종시 글자 효과(흰 글자 그림자) 제거
for e in list(sub(117)._element.iter(qn("a:effectLst"))):
    for ch in list(e):
        e.remove(ch)

# 절차 마지막 번호 5 → 6
r = sub(192).text_frame.paragraphs[0].runs[0]
r.text = "6"

# ── 5. 연결선 ─────────────────────────────────────────────────────────────────────
def style_line(oid, rgb, w, dash=None, tail=None):
    sh = sub(oid)
    ln = sh.line
    ln.color.rgb = rgb
    ln.width = Pt(w)
    lnel = sh._element.spPr.find(qn("a:ln"))
    for t in ("a:prstDash", "a:tailEnd", "a:headEnd"):
        x = lnel.find(qn(t))
        if x is not None:
            lnel.remove(x)
    if dash:
        d = lnel.makeelement(qn("a:prstDash"), {"val": dash})
        lnel.append(d)
    if tail:
        # 원본 꺾인 연결선은 PM 쪽에서 시작(시작점=PM) → 지역 지원에서 PM 으로 향하게 머리 쪽 화살표
        lnel.append(lnel.makeelement(qn("a:headEnd"), {"type": tail, "w": "med", "len": "med"}))


style_line(96, BLUE, 1.25, tail="triangle")
# 지역 지원 → PM: 원본은 지도 앞(3.40in)에서 끊겨 있어 PM 아이콘(3.60in) 바로 앞까지 늘린다
_l = sub(96)
_l.width = I(3.56) - _l.left
for oid in (138, 139, 140):
    style_line(oid, BLUE, 1.25)
for oid in (193, 194, 195, 174, 175, 176, 177):
    style_line(oid, GRAY, 1.0, dash="dash")

# ── 6. 청주시청 핀 ────────────────────────────────────────────────────────────────
# 원본 지도 그림(L3.48 T3.06, 329×319px, 0.00909in/px)에서 네 구 경계가 만나는 점 ≈ (140,118)px,
# 시청(상당로 155)은 그 바로 동쪽 상당구 쪽 ≈ (150,124)px → (4.84, 4.19)in.
tipx, tipy = I(4.84), I(4.19)
d = I(0.20)
circ = s.shapes.add_shape(MSO_SHAPE.OVAL, tipx - d // 2, tipy - I(0.27), d, d)
tri = s.shapes.add_shape(MSO_SHAPE.ISOSCELES_TRIANGLE, tipx - I(0.06), tipy - I(0.105), I(0.12), I(0.105))
tri.rotation = 180
for x in (circ, tri):
    x.fill.solid(); x.fill.fore_color.rgb = PINK
    x.line.fill.background()
    x.shadow.inherit = False
star = s.shapes.add_shape(MSO_SHAPE.STAR_5_POINT, tipx - I(0.065), tipy - I(0.235), I(0.13), I(0.125))
star.fill.solid(); star.fill.fore_color.rgb = WHITE
star.line.fill.background(); star.shadow.inherit = False
circ.name, tri.name, star.name = "시청 핀", "시청 핀 꼬리", "시청 핀 별"

# 라벨은 핀 아래(위쪽엔 지도 속 '청원구', 왼쪽엔 '흥덕구' 글자가 있다)
lab = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, tipx - I(0.41), tipy + I(0.04), I(0.60), I(0.22))
lab.name = "시청 라벨"
lab.adjustments[0] = 0.5
lab.fill.solid(); lab.fill.fore_color.rgb = PINK
lab.line.fill.background(); lab.shadow.inherit = False
tf = lab.text_frame
tf.word_wrap = False
bp = tf._txBody.find(qn("a:bodyPr"))
bp.set("anchor", "ctr")
bp.set("lIns", "0"); bp.set("rIns", "0"); bp.set("tIns", "0"); bp.set("bIns", str(int(Pt(9 * 0.115))))
pg = tf.paragraphs[0]
pg.alignment = PP_ALIGN.CENTER
run = pg.add_run(); run.text = "청주시청"
run.font.size = Pt(9); run.font.color.rgb = WHITE
set_face(run._r.get_or_add_rPr(), F3)

# 키메시지·제목을 맨 위로
for name in ("TextBox 113", "키메시지"):
    for sh in s.shapes:
        if sh.name == name:
            tree.remove(sh._element); tree.append(sh._element)

p.save(dst)
print("saved", dst, "copied", len(copied))
