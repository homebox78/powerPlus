"""31쪽 — 사업관리 방법 (2차 시안 design_ppt2/s31.png).

글이 아주 촘촘한 쪽이라(BRIEF2 5) 원래 도형을 살리고 면·색·모양·글자 크기만 시안에 맞춘다.
- 판(패널): 흰 면 + 옅은 파란 테두리, 둥근 모서리
- 판 머리: 프로세스 관리·프로젝트 지원 = 파란 알약 / S-PMM = 파란 띠 / S-ISM·SEM·CEM = 옅은 파란 띠
- 칸 제목은 굵은 글, 7pt 미만 글은 7pt 로 올리고 넘치는 칸은 넓힌다
- Repository·SVN 아이콘은 시안의 3D 아이콘을 오려 원래 원 안에 넣는다
- 실물(CMMI 인증서·배지 그림)은 원래 것을 그대로 둔다
"""
from lib import *

A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
KM_FONT = "G마켓 산스 TTF Bold"
KM_NAVY, KM_BLUE = hexrgb("0B2E6B"), hexrgb("2070E8")


def all_shapes(c):
    out = []

    def walk(sh):
        out.append(sh)
        if sh.shape_type == 6:
            for ch in sh.shapes: walk(ch)
    for sh in c.s.shapes: walk(sh)
    return out


def by(c, name):
    for sh in c.s.shapes:
        if sh.name == name: return sh
    raise KeyError(name)


def geom(sh, prst, adj=None):
    g = sh._element.find(".//" + A + "prstGeom")
    g.set("prst", prst)
    av = g.find(A + "avLst")
    if av is None: av = etree.SubElement(g, A + "avLst")
    for ch in list(av): av.remove(ch)
    if adj is not None:
        gd = etree.SubElement(av, A + "gd"); gd.set("name", "adj1" if prst == "round2SameRect" else "adj"); gd.set("fmla", "val %d" % int(adj * 100000))


def solid(sh, rgb, line=None, lw=0.75):
    sh.fill.solid(); sh.fill.fore_color.rgb = rgb
    if line is None: sh.line.fill.background()
    else:
        sh.line.color.rgb = line; sh.line.width = Pt(lw)


def setfont(r, font):
    """런 서체(latin·ea). ea 는 스키마 순서대로 latin 바로 뒤에."""
    r.font.name = font
    rPr = r._r.get_or_add_rPr()
    ea = rPr.find(qn("a:ea"))
    if ea is None:
        ea = etree.Element(qn("a:ea"))
        lat = rPr.find(qn("a:latin"))
        lat.addnext(ea)
    ea.set("typeface", font)


def restyle(sh, size=None, color=None, font=None):
    for p in sh.text_frame.paragraphs:
        for r in p.runs:
            if size: r.font.size = Pt(size)
            if color is not None: r.font.color.rgb = color
            if font:
                setfont(r, font)


def box(sh, l=None, t=None, w=None, h=None):
    if l is not None: sh.left = Inches(l)
    if t is not None: sh.top = Inches(t)
    if w is not None: sh.width = Inches(w)
    if h is not None: sh.height = Inches(h)


def build(c):
    PANEL_LN = c.rgb(380, 700)           # 판 테두리(옅은 파랑)
    CARD = hexrgb("E2F0FD")               # 판 안 칸
    PILL = hexrgb("D3EAFD")               # 칸 안 알약
    BLUE_HDR = c.rgb(330, 270)            # 알약 머리
    PMM = c.rgb(440, 262)                 # S-PMM 띠
    SUB_HDR = c.rgb(450, 598)             # S-ISM 등 옅은 띠
    CHEV = hexrgb("2F78E0")
    ORB = c.rgb(160, 545)                 # Repository 원

    # ── 바탕 ──
    c.background(20, 700)

    # ── 키메시지 (BRIEF2 2) ──
    c.remove("직사각형 306")
    km = c.text(0.20, 1.03, 10.43, 0.40, [[("청주시 업무지원포털시스템 유지관리에 최적화된 ", 23, KM_NAVY, KM_FONT),
                                            ("관리방법론 적용", 23, KM_BLUE, KM_FONT)]])
    km.name = "키메시지"

    # ── 판(패널): 흰 면 + 옅은 테두리 ──
    for n in ("직사각형 25", "직사각형 67", "직사각형 71", "직사각형 133", "직사각형 177", "직사각형 207", "모서리가 둥근 직사각형 18"):
        sh = by(c, n); geom(sh, "roundRect", 0.035 if sh.height > Inches(2) else 0.08)
        solid(sh, WHITE, PANEL_LN, 0.75)

    # 알약 머리: 프로세스 관리 / 프로젝트 지원
    for hn, tn in (("한쪽 모서리가 잘린 사각형 26", "직사각형 27"), ("한쪽 모서리가 잘린 사각형 68", "직사각형 69")):
        hd, tx = by(c, hn), by(c, tn)
        l, w = hd.left / 914400.0 + 0.12, hd.width / 914400.0 - 0.24
        geom(hd, "roundRect", 0.5); solid(hd, BLUE_HDR)
        box(hd, l, 1.63, w, 0.26)
        box(tx, l, 1.63, w, 0.26); tx.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
        restyle(tx, 11, WHITE, F3)
    # S-PMM 띠
    hd = by(c, "한쪽 모서리가 잘린 사각형 72"); geom(hd, "roundRect", 0.3); solid(hd, PMM)
    box(hd, h=0.26)
    tx = by(c, "직사각형 73"); box(tx, hd.left / 914400.0, hd.top / 914400.0, hd.width / 914400.0, 0.26)
    tx.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
    for i, r in enumerate(tx.text_frame.paragraphs[0].runs):
        r.font.color.rgb = WHITE
    first = tx.text_frame.paragraphs[0].runs[0]
    restyle(tx, color=WHITE)
    # 첫 구절(프로젝트 관리 (S-PMM))만 굵게 크게
    for r in tx.text_frame.paragraphs[0].runs:
        if "S-PMM" in r.text or "프로젝트" in r.text:
            r.font.size = Pt(11); setfont(r, F3)
    # S-ISM / S-SEM / S-CEM 옅은 띠
    for hn, tn in (("한쪽 모서리가 잘린 사각형 134", "직사각형 135"), ("한쪽 모서리가 잘린 사각형 178", "직사각형 179"),
                   ("한쪽 모서리가 잘린 사각형 208", "직사각형 209")):
        hd, tx = by(c, hn), by(c, tn)
        geom(hd, "roundRect", 0.3); solid(hd, SUB_HDR)
        box(tx, hd.left / 914400.0, hd.top / 914400.0, hd.width / 914400.0, hd.height / 914400.0)
        tx.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
        restyle(tx, color=KM_NAVY)
        for r in tx.text_frame.paragraphs[0].runs:
            if "S-" in r.text or "유지보수" in r.text or "개발" in r.text or "연계" in r.text:
                if "Solideos" not in r.text and "Mate" not in r.text:
                    r.font.size = Pt(10.5); setfont(r, F3)
    # 연계확대 머리의 오타 ") )" → ")"
    for r in by(c, "직사각형 209").text_frame.paragraphs[0].runs:
        if r.text.strip() == ")": r.text = " "

    # ── 칸: 옅은 파랑 둥근 칸 ──
    cards = ("직사각형 28", "직사각형 44", "직사각형 58", "직사각형 74", "직사각형 89", "직사각형 98", "직사각형 104",
             "직사각형 114", "직사각형 136", "직사각형 150", "직사각형 157", "직사각형 164", "직사각형 171", "직사각형 180",
             "직사각형 201", "직사각형 210", "직사각형 225", "직사각형 237", "직사각형 244", "직사각형 246", "직사각형 290")
    for n in cards:
        sh = by(c, n); geom(sh, "roundRect", 0.07); solid(sh, CARD)
    for n in ("모서리가 둥근 직사각형 52", "모서리가 둥근 직사각형 54"):
        solid(by(c, n), CARD)

    # 칸 제목 = 굵은 남색
    titles = ("직사각형 29", "직사각형 45", "직사각형 59", "직사각형 75", "직사각형 90", "직사각형 99", "직사각형 105",
              "직사각형 115", "직사각형 137", "직사각형 151", "직사각형 158", "직사각형 165", "직사각형 172", "직사각형 181",
              "직사각형 226", "직사각형 238", "직사각형 245", "직사각형 247", "직사각형 291", "직사각형 55", "직사각형 53")
    for n in titles:
        sh = by(c, n); restyle(sh, color=KM_NAVY, font=F3)
        # 제목 글상자는 칸 폭 전체로
    # 짙은 남색 갈매기(품질보증)도 같은 파랑
    solid(by(c, "갈매기형 수장 229"), CHEV)

    # ── 7pt 미만 글 → 7pt ──
    for sh in all_shapes(c):
        if sh.has_text_frame:
            for p in sh.text_frame.paragraphs:
                for r in p.runs:
                    if r.font.size is not None and r.font.size.pt < 7: r.font.size = Pt(7)

    # 알약 위 좁은 글상자는 알약 폭으로 (가운데 정렬 유지)
    def fit_to(txt, base):
        txt.left, txt.width = base.left, base.width
        txt.top, txt.height = base.top, base.height
        txt.text_frame.word_wrap = False
        txt.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
        for m in ("margin_left", "margin_right", "margin_top", "margin_bottom"): setattr(txt.text_frame, m, 0)
        for p in txt.text_frame.paragraphs: p.alignment = CENTER
    # 최상위: 알약 바로 다음에 놓인 TextBox 19 / 직사각형 짝
    top = list(c.s.shapes)
    for i, sh in enumerate(top):
        if sh.shape_type == 6:           # 그룹: 안쪽 두 도형 짝
            ch = list(sh.shapes)
            if len(ch) == 2 and ch[1].has_text_frame and ch[1].text_frame.text.strip(): fit_to(ch[1], ch[0])
            continue
        if not (sh.has_text_frame and sh.text_frame.text.strip()): continue
        if i == 0: continue
        prev = top[i - 1]
        pg = prev._element.find(".//" + A + "prstGeom")
        if pg is None or pg.get("prst") not in ("roundRect", "round2SameRect"): continue
        if prev.height > Inches(0.3) or prev.has_text_frame and prev.text_frame.text.strip(): continue
        cx = sh.left + sh.width / 2; cy = sh.top + sh.height / 2
        if prev.left <= cx <= prev.left + prev.width and prev.top <= cy <= prev.top + prev.height:
            fit_to(sh, prev)

    # 재해복구 관리 알약 3개: 두 줄 글이 들어가게 높이 조금 키움
    for pn, tn in (("모서리가 둥근 직사각형 106", "직사각형 107"), ("모서리가 둥근 직사각형 109", "직사각형 110"),
                   ("모서리가 둥근 직사각형 111", "직사각형 112")):
        p, t = by(c, pn), by(c, tn)
        box(p, t=2.79, h=0.25); fit_to(t, p)
        for pp in t.text_frame.paragraphs: pp.line_spacing = 0.9

    # 재해복구 알약: 글이 7pt 로 커져 알약을 조금 넓히고 자간을 줄인다
    for k, (pn, tn) in enumerate((("모서리가 둥근 직사각형 106", "직사각형 107"), ("모서리가 둥근 직사각형 109", "직사각형 110"),
                                  ("모서리가 둥근 직사각형 111", "직사각형 112"))):
        p, t = by(c, pn), by(c, tn)
        box(p, l=3.99 + k * 0.665, w=0.64); fit_to(t, p)
        for pp in t.text_frame.paragraphs:
            for r in pp.runs: r._r.get_or_add_rPr().set("spc", "-60")

    # 품질관리 갈매기 네 칸 글: 갈매기 폭에 맞춰 두 줄
    for n, cx in (("직사각형 233", 6.54), ("직사각형 234", 6.92), ("직사각형 235", 7.27), ("직사각형 236", 7.60)):
        t = by(c, n); box(t, l=cx - 0.19, w=0.38, t=2.155, h=0.24)
        t.text_frame.word_wrap = False
        for m in ("margin_left", "margin_right", "margin_top", "margin_bottom"): setattr(t.text_frame, m, 0)
        for pp in t.text_frame.paragraphs:
            pp.alignment = CENTER; pp.line_spacing = 0.85
            for r in pp.runs: r._r.get_or_add_rPr().set("spc", "-40")

    # 연계확대: 왼쪽 설명이 7pt 로 커져 넓힘 → 오른쪽 알약 두 줄을 오른쪽으로 좁혀 민다
    for rowp in (("모서리가 둥근 직사각형 212", "모서리가 둥근 직사각형 214", "모서리가 둥근 직사각형 216"),
                 ("모서리가 둥근 직사각형 219", "모서리가 둥근 직사각형 221", "모서리가 둥근 직사각형 223")):
        for k, n in enumerate(rowp):
            sh = by(c, n); box(sh, l=3.10 + k * 0.955, w=0.915)
    top = list(c.s.shapes)
    for i, sh in enumerate(top):
        if sh.name in ("모서리가 둥근 직사각형 212", "모서리가 둥근 직사각형 214", "모서리가 둥근 직사각형 216",
                       "모서리가 둥근 직사각형 219", "모서리가 둥근 직사각형 221", "모서리가 둥근 직사각형 223"):
            fit_to(top[i + 1], sh)
    for n in ("직사각형 211", "직사각형 218"):
        t = by(c, n); box(t, l=2.24, w=0.84); t.text_frame.word_wrap = False
        for p in t.text_frame.paragraphs: p.alignment = CENTER
    box(by(c, "직사각형 211"), t=6.38, h=0.12)
    box(by(c, "직사각형 218"), t=6.50, h=0.24)
    # 검증 및 확인(S-SEM) 왼쪽 글 7pt
    t = by(c, "직사각형 202"); box(t, l=2.22, w=0.62)

    # ── Repository·SVN: 원은 시안 파랑, 속 아이콘은 시안 3D 그림 ──
    for n in ("모서리가 둥근 직사각형 37", "모서리가 둥근 직사각형 281", "모서리가 둥근 직사각형 286"):
        solid(by(c, n), ORB)
    c.remove("Freeform 13")
    for nm, (x0, y0, x1, y1), cx in (("db1", (184, 508, 246, 564), (185, 509)),):
        pass
    icons = [("db1", (184, 508, 246, 565), "모서리가 둥근 직사각형 37"),
             ("db2", (1217, 794, 1275, 848), "모서리가 둥근 직사각형 281"),
             ("svn", (1370, 792, 1431, 846), "모서리가 둥근 직사각형 286")]
    for nm, (x0, y0, x1, y1), on in icons:
        o = by(c, on)
        p = c.pic(c.crop(nm, x0, y0, x1, y1, cut=(x0 + 1, y0 + 1), cut_thresh=70), 0, 0, None, 0.27)
        p.left = int(o.left + o.width / 2 - p.width / 2); p.top = int(o.top + Inches(0.07))
    for n in ("직사각형 40", "직사각형 284", "직사각형 289"):
        restyle(by(c, n), 7, WHITE, F3)
        t = by(c, n); o = None
    for tn, on in (("직사각형 40", "모서리가 둥근 직사각형 37"), ("직사각형 284", "모서리가 둥근 직사각형 281"),
                   ("직사각형 289", "모서리가 둥근 직사각형 286")):
        t, o = by(c, tn), by(c, on)
        t.left, t.width = o.left, o.width; t.top = o.top + Inches(0.38); t.height = Inches(0.14)
        t.text_frame.word_wrap = False
        for p in t.text_frame.paragraphs: p.alignment = CENTER

    # 화살표 선 = 파랑
    for n in ("직선 연결선 41", "직선 연결선 42", "직선 연결선 56", "직선 연결선 57"):
        ln = by(c, n); ln.line.color.rgb = BLUE_HDR; ln.line.width = Pt(1.25)

    # 각주는 안내선(7.02in) 안으로
    fn = by(c, "직사각형 305"); box(fn, t=6.84, h=0.18)
    restyle(fn, 7.5, hexrgb("4A5A78"))
