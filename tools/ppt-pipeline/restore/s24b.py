# -*- coding: utf-8 -*-
"""24쪽 왼쪽 관리 카드 3장: 아이콘 줄이고(0.75→0.5in) 설명글 7→9pt, 글 상자는 아이콘 옆 남는 폭 전부.
카드 = (본체 이름, 머리 이름, 그림 이름, 글 이름). 인자: <src> <dst>"""
import sys
from pptx import Presentation
from pptx.util import Pt, Emu
from pptx.enum.text import MSO_ANCHOR
sys.stdout.reconfigure(encoding="utf-8")
src, dst = sys.argv[1:3]
IN = 914400
CARDS = [("시안 9", "시안 10", "시안 그림 11", "시안 12"),
         ("시안 13", "시안 14", "시안 그림 15", "시안 16"),
         ("시안 17", "시안 18", "시안 그림 19", "시안 20")]
ICON = 0.42
prs = Presentation(src)
sl = prs.slides[23]
by = {s.name: s for s in sl.shapes}
for body, head, pic, txt in CARDS:
    b, hd, p, t = by[body], by[head], by[pic], by[txt]
    top = hd.top + hd.height
    bot = b.top + b.height
    k = ICON * IN / max(p.width, p.height)
    p.width, p.height = int(p.width * k), int(p.height * k)
    p.left = int(b.left + 0.08 * IN)
    p.top = int(top + (bot - top - p.height) / 2)
    t.left = int(p.left + p.width + 0.06 * IN)
    t.width = int(b.left + b.width - 0.06 * IN - t.left)
    t.top, t.height = int(top + 0.04 * IN), int(bot - top - 0.08 * IN)
    tf = t.text_frame
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Emu(int(0.03 * IN))
    for pg in tf.paragraphs:
        for r in pg.runs:
            r.font.size = Pt(9)
# 설명글: 문장 중간 강제 줄바꿈을 합쳐 다시 씀(문구 그대로)
import copy
from pptx.oxml.ns import qn
TEXTS = {
    "시안 12": [("", "연계여부 확정 이후 운영지원센터에서 개발한 연계모듈과 관련 산출물 관리"),
               ("• ", "형상관리시스템을 통해 관리"), ("- ", "연계모듈(프로그램 소스)"), ("- ", "인터페이스 규격서")],
    "시안 16": [("", "현재 31종의 정보연계 내역·이력 현행화 관리"),
               ("- ", "대상기관, 대상시스템, 연계근거"), ("- ", "적용기술, 연계항목, 연계주기, 연계코드"),
               ("- ", "관리항목 및 서비스 변경 시 청주시와 협의에 의해 연계모듈 변경사항 반영")],
    "시안 20": [("", "연계를 위한 각종 신청 문서 및 기술검토 문서 등 관리"),
               ("• ", "연계신청서, 검토의견서(수신), 연계정보정의서, 연계확인서 등")],
}
for name, rows in TEXTS.items():
    tf = by[name].text_frame
    tx = tf._txBody
    ps = tx.findall(qn("a:p"))
    proto = copy.deepcopy(ps[0])
    for p0 in ps:
        tx.remove(p0)
    for mark, body in rows:
        p = copy.deepcopy(proto)
        rs = p.findall(qn("a:r"))
        for r in rs[1:]:
            p.remove(r)
        rs[0].find(qn("a:t")).text = mark + body
        pPr = p.find(qn("a:pPr"))
        if pPr is None:
            pPr = p.makeelement(qn("a:pPr"), {}); p.insert(0, pPr)
        ind = {"": 0, "• ": 1, "- ": 2}[mark]
        pPr.set("marL", str(int((0.0 if ind == 0 else 0.09 + 0.08 * (ind - 1)) * IN)))
        pPr.set("indent", str(int(-0.09 * IN) if ind else 0))
        sp = pPr.find(qn("a:spcBef"))
        tx.append(p)
    for pg in tf.paragraphs:
        for r in pg.runs:
            r.font.size = Pt(8.5)

# 오른쪽 절차도: 흰 바탕에 흰 상자라 안 보임 → 원본처럼 구분
from pptx.dml.color import RGBColor
grp = [x for x in sl.shapes if x.shape_type == 6]
def walk(shs):
    for x in shs:
        if x.shape_type == 6:
            yield from walk(x.shapes)
        else:
            yield x
LANE = {"Rectangle 357", "Rectangle 358"}
BODY = {"Rectangle 377", "Rectangle 382"}
for g in grp:
    for x in walk(g.shapes):
        if x.name in LANE:
            x.fill.solid(); x.fill.fore_color.rgb = RGBColor(0xEE, 0xF1, 0xF5)
            x.line.fill.background()
        elif x.name in BODY:
            x.fill.solid(); x.fill.fore_color.rgb = RGBColor(0xE3, 0xEC, 0xF7)
            x.line.color.rgb = RGBColor(0x7F, 0x9C, 0xC4); x.line.width = Pt(0.75)
        elif x.shape_type == 1 and x.has_text_frame and x.text_frame.text.strip():
            try:
                ft = x.fill.type
                rgb = x.fill.fore_color.rgb if ft == 1 else None
            except Exception:
                ft, rgb = None, None
            light = ft in (None, 5) or (rgb is not None and min(rgb) >= 0xE8)
            if light and x.name != "Rectangle 387":   # 상호확인: 점선 위 글 받침이라 테두리 없음
                x.fill.solid(); x.fill.fore_color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
                x.line.color.rgb = RGBColor(0x7F, 0x9C, 0xC4); x.line.width = Pt(0.75)
        elif x.shape_type == 1 and x.name == "Diamond 372":
            x.line.color.rgb = RGBColor(0x2F, 0x78, 0xE0); x.line.width = Pt(1)
    # 머리 줄: 연계대상기관 | 청주시 | 유지관리 담당자 (세 칸에 각각)
    hd = {x.name: x for x in walk(g.shapes)}
    if "TextBox 360" in hd:
        lane_l, lane_r = hd["Rectangle 357"], hd["Rectangle 358"]
        cols = [("TextBox 360", lane_l.left, lane_l.width),
                ("TextBox 361", lane_l.left + lane_l.width, lane_r.left - lane_l.left - lane_l.width),
                ("TextBox 362", lane_r.left, lane_r.width)]
        bar = hd["Rounded Rectangle 359"]
        for nm, l0, w0 in cols:
            t = hd[nm]
            t.left, t.width, t.top, t.height = l0, w0, bar.top, bar.height
            tf = t.text_frame
            tf.vertical_anchor = MSO_ANCHOR.MIDDLE
            tf.margin_top = tf.margin_bottom = 0
            for pg in tf.paragraphs:
                pg.alignment = 2
                for r in pg.runs:
                    r.font.size = Pt(9)
                    r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
                    rPr = r._r.get_or_add_rPr(); rPr.set("b", "0")
                    for tg in ("a:latin", "a:ea"):
                        e = rPr.find(qn(tg))
                        if e is None:
                            e = rPr.makeelement(qn(tg), {}); rPr.append(e)
                        e.set("typeface", "a시월구일3")
        if "Freeform 35" in hd:   # 원본처럼 왼쪽 칸 경계에도 세로 구분선
            sep = hd["Freeform 35"]
            el = copy.deepcopy(sep._element)
            sep._element.addnext(el)
            x0 = int(sep.left - (lane_r.left - lane_l.left - lane_l.width))
            el.find(qn("p:spPr")).find(qn("a:xfrm")).find(qn("a:off")).set("x", str(x0))
print("24쪽 카드", len(CARDS))
prs.save(dst)
