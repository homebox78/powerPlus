# -*- coding: utf-8 -*-
"""16쪽(III-1. 수행 및 지원방안 개요) 2차 수정 — v0.77 기준.
- 번호 원 1~8 삭제
- 원본처럼 그룹 라벨 → 카드로 내려가는 묶음 선(가로선 + 카드별 짧은 내림선), 0.75pt
- 사업수행방안 강조: 라벨 16pt 남색 채움 / 사업지원방안 13pt 옅은 파랑 채움, 수행 카드 머리 남색·테두리 파랑
- 카드 = 머리(제목 12/11.5pt, 세로 가운데) + 본문(원본 설명 9pt) + 아래 작은 3D 아이콘(약 0.6in)
- 3D 만화 화살표가 든 일러스트(3·5·7)를 포함해 바닥 일러스트를 powerPlus 투명 3D 아이콘(원본 크기 파일)으로 교체
인자: <src> <dst>  (16쪽만 손댄다)
"""
import os, re, sys, tempfile, urllib.request
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.oxml.ns import qn
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")
src, dst = sys.argv[1:3]
SNO = 16
p = Presentation(src)
s = p.slides[SNO - 1]
by = {sh.shape_id: sh for sh in s.shapes}
I = Inches
HEX = lambda h: RGBColor.from_string(h)
NAVY, BLUE, LIGHT, PALE = HEX("143A69"), HEX("2F78E0"), HEX("D0E6FA"), HEX("E8F2FC")
TXT, INK, GRAY, PINK, WHITE = HEX("333333"), HEX("1F4E79"), HEX("5F7496"), HEX("EC1C68"), HEX("FFFFFF")
F2, F3, F4 = "a시월구일2", "a시월구일3", "a시월구일4"
DESC_PT = 9
VT = "\x0b"

# 아이콘: powerPlus 공개 자산(투명 PNG, 원본 크기 그대로 삽입)
ICON_URL = "https://hom2box.com/powerPlus/uploads/icon/{}.png"
CACHE = os.path.join(tempfile.gettempdir(), "pp_icons")


def icon_file(aid):
    os.makedirs(CACHE, exist_ok=True)
    fn = os.path.join(CACHE, aid + ".png")
    if not os.path.exists(fn):
        urllib.request.urlretrieve(ICON_URL.format(aid), fn)
    return fn


def face(r, f):
    rPr = r._r.get_or_add_rPr()
    for tag in ("a:latin", "a:ea"):
        e = rPr.find(qn(tag))
        if e is None:
            e = rPr.makeelement(qn(tag), {})
            rPr.append(e)
        e.set("typeface", f)


def clear(tf):
    for pg in list(tf.paragraphs)[1:]:
        pg._p.getparent().remove(pg._p)
    for r in list(tf.paragraphs[0].runs):
        r._r.getparent().remove(r._r)
    return tf.paragraphs[0]


def noshadow(sh):
    sp = sh._element.spPr
    if sp.find(qn("a:effectLst")) is None:
        sp.append(sp.makeelement(qn("a:effectLst"), {}))


def box(kind, x, y, w, h, fill=None, line=None, lw=0.75, name=None):
    sh = s.shapes.add_shape(kind, I(x), I(y), I(w), I(h))
    if fill is None:
        sh.fill.background()
    else:
        sh.fill.solid(); sh.fill.fore_color.rgb = fill
    if line is None:
        sh.line.fill.background()
    else:
        sh.line.color.rgb = line; sh.line.width = Pt(lw)
    noshadow(sh)
    if name:
        sh.name = name
    return sh


def label(sh, text, size, color, font=F4, align=PP_ALIGN.CENTER, inset=0.03):
    tf = sh.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_left = tf.margin_right = I(0.03)
    tf.margin_top = tf.margin_bottom = I(inset)
    pg = clear(tf)
    pg.alignment = align
    pg.line_spacing = 1.0
    for k, seg in enumerate(text.split("^")):
        if k:
            pg._p.append(pg._p.makeelement(qn("a:br"), {}))
        r = pg.add_run(); r.text = seg
        r.font.size = Pt(size); r.font.bold = False; r.font.color.rgb = color
        face(r, font)


def line(x1, y1, x2, y2, color):
    c = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, I(x1), I(y1), I(x2), I(y2))
    c.line.color.rgb = color
    c.line.width = Pt(0.75)
    c.name = "묶음선"
    return c


def add_run(pg, seg, emph):
    r = pg.add_run(); r.text = seg
    small = bool(re.fullmatch(r"\s*\([A-Za-z]+\)[,)]*\s*", seg))   # 영문 괄호 병기
    r.font.size = Pt(8 if small else DESC_PT); r.font.bold = False
    r.font.color.rgb = PINK if emph else TXT
    face(r, F3 if emph else F2)


def desc_box(x, y, w, h, items):
    """{…} = 원본에서 굵게 강조한 낱말 → 분홍·강조 서체. ^ = 어절 경계 줄바꿈."""
    tb = s.shapes.add_textbox(I(x), I(y), I(w), I(h))
    tb.name = "복원설명"
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.TOP
    tf.margin_left = tf.margin_right = I(0.01)
    tf.margin_top = tf.margin_bottom = 0
    p0 = clear(tf)
    ind = int(Pt(DESC_PT) * 0.7)
    for i, it in enumerate(items):
        pg = p0 if i == 0 else tf.add_paragraph()
        pg.alignment = PP_ALIGN.LEFT
        pg.line_spacing = 1.08
        pg.space_after = Pt(4)
        pPr = pg._p.get_or_add_pPr()
        pPr.set("marL", str(ind)); pPr.set("indent", str(-ind))
        bc = pPr.makeelement(qn("a:buClr"), {})
        bc.append(bc.makeelement(qn("a:srgbClr"), {"val": "5F7496"}))
        pPr.append(bc)
        pPr.append(pPr.makeelement(qn("a:buFont"), {"typeface": "Arial"}))
        pPr.append(pPr.makeelement(qn("a:buChar"), {"char": "•"}))
        for k, seg in enumerate(re.split(r"[{}]", it.replace("|", "{}"))):
            if not seg:
                continue
            emph = k % 2 == 1
            for q, part in enumerate(seg.split("^")):
                if q:
                    pg._p.append(pg._p.makeelement(qn("a:br"), {}))
                if part:
                    add_run(pg, part, emph)
    return tb


def picture(fn, cx, bottom, maxw, maxh):
    w, h = Image.open(fn).size
    k = min(maxw / w, maxh / h)
    W, H = w * k, h * k
    pic = s.shapes.add_picture(fn, I(cx - W / 2), I(bottom - H), I(W), I(H))
    pic.name = "카드 아이콘"
    return pic


# ── 0) 지울 것: 옛 라벨·묶음선·카드·번호·제목·바닥 일러스트·일러스트 위 글자·설명칸 ──
kill = list(range(48, 66)) + list(range(66, 105)) + list(range(106, 113)) + list(range(114, 122))
for i in kill:
    if i in by:
        by[i]._element.getparent().remove(by[i]._element)

# ── 1) 카드 배치 ──────────────────────────────────────────────
GAP, GGAP, X0 = 0.05, 0.16, 0.30
CW = (10.53 - X0 - 6 * GAP - GGAP) / 8
xs = [X0 + i * (CW + GAP) for i in range(3)]
x1 = xs[-1] + CW + GGAP
xs += [x1 + i * (CW + GAP) for i in range(5)]
CT, HEAD, CB = 3.52, 0.80, 6.98

cards = [  # (제목, 설명, 아이콘)
    ("꼼꼼한^유지관리^체계",
     ["제안사 검증된^방법론 기반",
      "{서비스요청유형}의^특성에 맞는^처리 절차 및^응대 관리 체계"], "icon_1359"),
    ("전문적^수행 조직^지원",
     ["대한민국 정부^행정정보시스템^집약 전문성 확보",
      "{청주시 유지보수^18년 경력}의^수행 책임자"], "icon_1363"),
    ("흔들림 없는^인수인계^유지",
     ["{현 사업자}",
      "안정된 인계를^위한 공동운영,^비상주^운영지원으로^{업무연속성^유지 보장}"], "icon_1262"),
    ("시스템 연계^(31개)^유지관리",
     ["청주시 시스템^연계 현황 현행화", "연계표준^가이드라인 관리", "전사차원의^기술적 지원"], "icon_1941"),
    ("안정적인^비상상황^대응관리",
     ["전사적^기술지원으로^확장된 {3단계^장애관리 체계}",
      "백업/복구 체계^및 절차,^수행 기준 관리"], "icon_1263"),
    ("철저한^보안관리",
     ["보안 원칙(기밀성^|(Confidentiality),^|무결성^|(Integrity),^|가용성^|(Availability))|에^충실한 관리"], "icon_1352"),
    ("신속한^환경변화^대응",
     ["기능개선 요구 및^법제도·시스템적^환경 변화에^신속한 대응이^가능토록 지원"], "icon_989"),
    ("실질적인^사용자^교육 관리",
     ["교육대상자^역할별 차별화된^교육 실시",
      "실질적 운영능력^배양을 위한^체계적 교육지원"], "icon_1684"),
]
R = 0.07  # 카드 모서리 반지름(in)
for i, (title, items, aid) in enumerate(cards):
    x = xs[i]
    lead = i < 3   # 사업수행방안
    bg = box(MSO_SHAPE.ROUNDED_RECTANGLE, x, CT, CW, CB - CT, fill=WHITE,
             line=BLUE if lead else HEX("C0D2E6"), lw=1.0 if lead else 0.75, name="카드")
    bg.adjustments[0] = R / CW
    hd = box(MSO_SHAPE.ROUND_2_SAME_RECTANGLE, x, CT, CW, HEAD, fill=NAVY if lead else BLUE, name="카드 머리")
    hd.adjustments[0] = R / HEAD
    hd.adjustments[1] = 0
    label(hd, title, 12 if lead else 11.5, WHITE)
    desc_box(x + 0.05, CT + HEAD + 0.13, CW - 0.08, 1.85, items)
    picture(icon_file(aid), x + CW / 2, CB - 0.10, 0.70, 0.62)

# ── 2) 그룹 라벨 + 묶음선 ───────────────────────────────────────
MIDY = 3.03
groups = [  # (첫 카드, 끝 카드, 라벨, 크기, 폭, 높이, 채움, 글자색, 선색)
    (0, 2, "사업수행방안", 16, 1.90, 0.48, NAVY, WHITE, BLUE),
    (3, 7, "사업지원방안", 13, 1.70, 0.38, LIGHT, NAVY, HEX("9FB3CC")),
]
HY = CT - 0.15   # 가로선 높이
for a, b, text, size, w, h, fill, fc, lc in groups:
    gx = (xs[a] + xs[b] + CW) / 2
    pill = box(MSO_SHAPE.ROUNDED_RECTANGLE, gx - w / 2, MIDY - h / 2, w, h, fill=fill, name="그룹 라벨")
    pill.adjustments[0] = 0.5
    label(pill, text, size, fc, inset=0.04)
    c1, c2 = xs[a] + CW / 2, xs[b] + CW / 2
    line(gx, MIDY + h / 2, gx, HY, lc)
    line(c1, HY, c2, HY, lc)
    for k in range(a, b + 1):
        cx = xs[k] + CW / 2
        line(cx, HY, cx, CT, lc)

p.save(dst)
print("저장", dst)
