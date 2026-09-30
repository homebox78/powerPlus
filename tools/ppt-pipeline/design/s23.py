"""23쪽 — 인수인계 (2차 시안 design_ppt2/s23.png). 글은 원래 장표(v0.65) 문구."""
from lib import *

KM_FONT = "G마켓 산스 TTF Bold"
KM_NAVY, KM_BLUE = hexrgb("0B2E6B"), hexrgb("2070E8")
HDR = hexrgb("3A86EA")        # 머리 띠 파랑
DEEP = hexrgb("2B74DF")       # 진한 화살표·배지
TXT = hexrgb("17407A")        # 본문 남색
LIGHT = hexrgb("D5EBFE")
CELL = hexrgb("DCEEFD")
LINE = hexrgb("A9CDF3")
PILL = hexrgb("3E81D3")
ACC = hexrgb("0B53BC")


def _find(shapes, name):
    for sh in shapes:
        if sh.name == name:
            return sh
        if sh.shape_type == 6:
            r = _find(sh.shapes, name)
            if r is not None:
                return r
    return None


def _lines(c, name, group=None):
    """원래 도형의 글을 줄 단위로(문단·줄바꿈 기준)."""
    root = c.s.shapes if group is None else _find(c.s.shapes, group).shapes
    sh = _find(root, name)
    out = []
    for pg in sh.text_frame.paragraphs:
        t = "".join(r.text for r in pg.runs)
        out.extend(t.replace("\x0b", "\n").split("\n"))
    return out


def build(c):
    # 원래 문구 읽기
    acts = [_lines(c, "TextBox %d" % n) for n in range(420, 427)]
    jg = [l for l in _lines(c, "Rectangle 61", "그룹 24") if l.strip()]
    ig = _lines(c, "Rectangle 61", "그룹 19") + ["|"] + _lines(c, "Rectangle 24", "그룹 19")
    sg = _lines(c, "Rectangle 61", "그룹 17") + ["|"] + _lines(c, "Rectangle 24", "그룹 17")
    c.keep_only("TextBox 49")
    c.background(1000, 250)

    # 좌표: 가로는 안내선(0.24~10.59in), 세로는 본문(1.62~7.02in)에 맞춘다
    kx = 10.35 / 1922.0
    ky = 5.40 / 818.0
    X = lambda x: 0.24 + (x - 40) * kx
    Y = lambda y: 1.62 + (y - 272) * ky
    def box(fn, x0, y0, x1, y1, **kw):
        return fn(X(x0), Y(y0), (x1 - x0) * kx, (y1 - y0) * ky, **kw)
    def txt(x0, y0, x1, y1, lines, align=CENTER, **kw):
        return c.text(X(x0), Y(y0), (x1 - x0) * kx, (y1 - y0) * ky, lines, align, **kw)

    # ── 키메시지 ──
    km = c.text(0.20, 1.03, 10.43, 0.52, [[("현 사업자로 ", 23, KM_NAVY, KM_FONT), ("즉시", 23, KM_BLUE, KM_FONT),
                                         (" 업무 수행 가능, 사업자 변경 시 마무리 지원 보장", 23, KM_NAVY, KM_FONT)]])
    km.name = "키메시지"

    # ── 두 패널 ──
    for x0, x1, title, icon in ((40, 1005, "업무연속성 보장을 위한 인수인계 방안", (80, 283, 168, 352)),
                                (1035, 1962, "인수인계 조직과 역할", (1080, 283, 1142, 352))):
        box(c.rrect, x0, 330, x1, 1090, adj=0.03, fill=hexrgb("F7FBFE"), line=hexrgb("CFE3F8"), lw=0.75)
        box(lambda l, t, w, h, **kw: c.shape(MSO_SHAPE.ROUND_2_SAME_RECTANGLE, l, t, w, h, **kw),
            x0, 272, x1, 360, adj=[0.3, 0], fill=HDR)
        ip = c.crop("hico%d" % x0, *icon, cut=(icon[0] + 2, icon[1] + 3), cut_thresh=60)
        ih = (icon[3] - icon[1]) * kx
        c.pic(ip, X(icon[0]), Y(316) - ih / 2, (icon[2] - icon[0]) * kx)
        txt(icon[2] + 22, 272, x1 - 10, 360, [[(title, 15, WHITE, F3)]], LEFT)

    # ── 왼쪽: 단계 흐름 화살표 ──
    b = box(lambda l, t, w, h, **kw: c.shape(MSO_SHAPE.PENTAGON, l, t, w, h, **kw), 102, 388, 418, 498,
            fill=LIGHT, adj=0.35)
    c.write(b, [[("인수인계 착수", 11, TXT, F3)]])
    box(lambda l, t, w, h, **kw: c.shape(MSO_SHAPE.CHEVRON, l, t, w, h, **kw), 395, 388, 802, 498,
        fill=hexrgb("BEE1FE"), adj=0.35)
    box(lambda l, t, w, h, **kw: c.shape(MSO_SHAPE.CHEVRON, l, t, w, h, **kw), 432, 444, 778, 498,
        fill=hexrgb("E3F2FE"), adj=0.45)
    txt(470, 390, 730, 442, [[("인수현황 통제", 11, TXT, F3)]])
    txt(470, 446, 730, 496, [[("인수현황 수행", 11, TXT, F3)]])
    b = box(lambda l, t, w, h, **kw: c.shape(MSO_SHAPE.CHEVRON, l, t, w, h, **kw), 765, 388, 977, 498,
            fill=DEEP, adj=0.35)
    txt(800, 390, 935, 496, [[("인수", 10, WHITE, F3)], [("인계", 10, WHITE, F3)], [("종료", 10, WHITE, F3)]])

    # 왼쪽 세로 이름표
    for y0, y1, lab in ((518, 616, ["단계"]), (632, 888, ["수행", "활동"]), (908, 1072, ["사업자", "변경시", "인계"])):
        b = box(c.rrect, 66, y0, 152, y1, adj=0.12, fill=hexrgb("3B8BEF"))
        c.write(b, [[(t, 9.5, WHITE, F3)] for t in lab])

    # 단계 카드 3묶음
    for x0, x1, y1 in ((160, 387, 888), (395, 762, 812), (770, 978, 888)):
        box(c.rrect, x0, 518, x1, y1, adj=0.05, fill=WHITE, line=hexrgb("CFE3F8"), lw=0.75)
    cols = [(163, 272), (278, 384), (398, 514), (520, 645), (651, 759), (773, 871), (877, 975)]
    heads = ["착수준비", "계획수립", "인수인계\n실시", "공동운영", "단독운영", "인수확인", "완료보고"]
    for i, ((x0, x1), hd, act) in enumerate(zip(cols, heads, acts)):
        b = box(c.rrect, x0 + 3, 522, x1 - 3, 612, adj=0.1, fill=CELL)
        c.write(b, [[(t, 8, TXT, F3)] for t in hd.split("\n")])
        while act and not act[-1].strip():
            act.pop()
        c.text(X(x0) + 0.03, Y(630), (x1 - x0) * kx - 0.03, 0.9,
               [[(t, 7, TXT, F2)] for t in act], LEFT, anchor="top", spacing=1.2)
    for x, yb in ((275, 880), (516, 804), (648, 804), (874, 880)):
        c.line(X(x), Y(622), X(x), Y(yb), LINE, 0.75, dash=True)
    b = box(c.rrect, 397, 822, 760, 888, adj=0.15, fill=CELL)
    c.write(b, [[("위험/이슈 정의 및 관리", 8.5, TXT, F2)], [("중요사항 협의/요청", 8.5, TXT, F2)]])

    # 사업자 변경 시 인계 4단계
    box(c.rrect, 160, 908, 978, 1072, adj=0.08, fill=WHITE, line=hexrgb("CFE3F8"), lw=0.75)
    steps = [(270, ["인수인계", "사전준비"]), (472, ["인수인계", "실시"]), (672, ["공동", "운영"]), (872, ["비상주", "운영지원"])]
    D = 150 * kx
    for i, (cx, lab) in enumerate(steps):
        cy = Y(993)
        c.oval(X(cx) - D / 2, cy - D / 2, D, D, fill=hexrgb("F7FAFE"), line=hexrgb("C7E1FA"), lw=3)
        col = ACC if i == 3 else TXT
        c.text(X(cx) - D / 2, cy - D / 2 + 0.05, D, D - 0.05, [[(t, 10, col, F3)] for t in lab])
        bd = 34 * kx
        b = c.oval(X(cx - 49) - bd / 2, Y(945) - bd / 2, bd, bd, fill=DEEP)
        c.write(b, [[(str(i + 1), 9, WHITE, F3)]])
        if i < 3:
            ax = cx + 100
            c.line(X(ax - 12), Y(983), X(ax + 3), Y(993), hexrgb("8FC2F3"), 1.5)
            c.line(X(ax - 12), Y(1003), X(ax + 3), Y(993), hexrgb("8FC2F3"), 1.5)

    # ── 오른쪽: 주관기관 ──
    c.pic(c.crop("man", 1060, 388, 1272, 646, cut=(1064, 392), cut_thresh=40), X(1060), Y(645) - 258 * kx, 212 * kx)
    box(c.rrect, 1276, 430, 1938, 634, adj=0.08, fill=WHITE, line=hexrgb("E1EEFB"), lw=0.75)
    box(c.rrect, 1276, 432, 1690, 634, adj=0.08, fill=WHITE, line=hexrgb("CFE3F8"), lw=0.75)
    b = box(lambda l, t, w, h, **kw: c.shape(MSO_SHAPE.ROUND_2_SAME_RECTANGLE, l, t, w, h, **kw),
            1276, 387, 1690, 437, adj=[0.3, 0], fill=HDR)
    c.write(b, [[("주관기관", 11, WHITE, F3)]])
    c.text(X(1305), Y(448), 380 * kx, Y(628) - Y(448), [[("• " + " ".join(t.split()), 9, TXT, F2)] for t in jg],
           LEFT, anchor="middle", spacing=1.05)

    # 인계·인수 사업자
    def party(x0, x1, title, lines):
        box(c.rrect, x0, 690, x1, 938, adj=0.05, fill=WHITE, line=hexrgb("CFE3F8"), lw=0.75)
        b = box(lambda l, t, w, h, **kw: c.shape(MSO_SHAPE.ROUND_2_SAME_RECTANGLE, l, t, w, h, **kw),
                x0, 652, x1, 697, adj=[0.3, 0], fill=HDR)
        c.write(b, [[(title, 11, WHITE, F3)]])
        top = [l for l in lines[:lines.index("|")]]
        bot = [l for l in lines[lines.index("|") + 1:] if l.strip()]
        rows, cont = [], {"현상 파악·문제 도출"}
        exp = []
        for l in top:
            s = " ".join(l.split())
            if "검토·현상" in s:
                i = s.index("검토·") + 3
                exp += [s[:i], s[i:].strip()]
            else:
                exp.append(s)
        for s in exp:
            if not s:
                rows.append(None); continue
            rows.append((22, s) if s in cont else (0, "• " + s))
        yy = 706
        for r in rows:
            if r is None:
                yy += 8; continue
            c.text(X(x0 + 22 + r[0]), Y(yy), (x1 - x0 - 30 - r[0]) * kx, 24 * ky, [[(r[1], 9, TXT, F2)]], LEFT)
            yy += 24
        c.line(X(x0 + 20), Y(855), X(x1 - 20), Y(855), LINE, 0.75, dash=True)
        yy = 866
        for s in bot:
            c.text(X(x0 + 22), Y(yy), (x1 - x0 - 30) * kx, 24 * ky, [[("• " + " ".join(s.split()), 9, TXT, F2)]], LEFT)
            yy += 26
    party(1055, 1402, "인계사업자", ig)
    party(1565, 1925, "인수사업자", sg)

    # 가운데 공동운영
    c.pic(c.crop("hand", 1418, 655, 1548, 718, cut=(1420, 658), cut_thresh=50), X(1418), Y(686) - 63 * kx / 2, 130 * kx)
    b = box(c.rrect, 1417, 722, 1550, 790, adj=0.15, fill=hexrgb("CEE9FC"))
    c.write(b, [[("S/W", 8.5, ACC, F3)], [("유지보수", 8.5, ACC, F3)], [("부문", 8.5, ACC, F3)]])
    b = box(c.pill, 1378, 798, 1590, 864, fill=WHITE, line=hexrgb("2B6DD8"), lw=2.25)
    c.write(b, [[("시스템 공동운영", 10, TXT, F3)], [("(인수인계기간)", 8, TXT, F3)]])
    b = box(c.rrect, 1417, 872, 1550, 938, adj=0.15, fill=hexrgb("CEE9FC"))
    c.write(b, [[("운영지원", 8.5, ACC, F3)], [("부문", 8.5, ACC, F3)]])

    # 필요 범위 + 점검 알약 3
    txt(1055, 950, 1925, 994, [[("인수인계 필요 범위 파악 및 대응방안 마련", 12, ACC, F3)]])
    for x0, x1, t in ((1057, 1340, "기존 사업 미진 사항 점검"), (1362, 1646, "과업 미 종료 사항 점검"),
                      (1670, 1938, "협의예정사항 점검")):
        b = box(c.pill, x0, 1006, x1, 1066, fill=PILL)
        c.write(b, [[(t, 9, WHITE, F3)]])
