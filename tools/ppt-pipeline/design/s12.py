"""12쪽 — 관리체계 확립 (1/2) (시안 7번)."""
from lib import *


def _find(shapes, name):
    for sh in shapes:
        if sh.name == name:
            return sh
        if sh.shape_type == 6:
            r = _find(sh.shapes, name)
            if r is not None:
                return r
    return None


def build(c):
    # 키메시지 서체를 읽어 두고, 머리말 글(TextBox 132)만 남긴다
    title_font = F3
    km = _find(c.s.shapes, "직사각형 126")
    if km is not None:
        for r in km.text_frame.paragraphs[0].runs:
            ea = r._r.find(".//" + qn("a:ea"))
            title_font = (ea.get("typeface") if ea is not None else None) or r.font.name or F3
    c.keep_only("TextBox 132")
    c.vmap(108, 0.87, 1125, 7.58)
    c.background(1000, 200)

    INK = hexrgb("16294F")
    TXT = hexrgb("2A3550")
    HEAD = c.rgb(300, 322)          # 패널 제목 파랑
    CB = c.rgb(84, 344)             # 원 파랑
    LN = hexrgb("BFD8F6")

    def T(g, x, yc, runs, w=600, h=40, align=LEFT):
        return c.text(g.X(x), g.Y(yc - h / 2.0), w * K, h * K, [runs], align)

    # ── 전략 알약 ──
    g = c.grp(127, 186)
    c.pill(g.X(38), g.Y(127), 1034 * K, 59 * K, fill=c.rgb(900, 150))
    c.write(c.pill(g.X(38), g.Y(127), 156 * K, 59 * K, fill=c.rgb(60, 156)), [[("전략 2", 13, WHITE, F3)]])
    T(g, 220, 156, [("서비스 지속성을 위한 관리체계를 확립합니다.", 11.3, INK, title_font)], w=840)

    # ── ACT.3 ──
    g = c.grp(211, 270)
    b = c.shape(MSO_SHAPE.PENTAGON, g.X(38), g.Y(211), 180 * K, 59 * K, fill=c.rgb(60, 240), adj=0.12)
    c.write(b, [[("ACT.3 ", 13.5, WHITE, F3)]])
    T(g, 238, 241, [("서비스 지속성을 위한 기능개선 체계 구축", 18.3, INK, F3)], w=1200, h=60)

    # ── 세 패널 ──
    g = c.grp(288, 702)
    panels = [(38, 672, "A", 118, 190, "풍부한 행정정보화 사업경험",
               ["다양한 공공기관 사업 수행 경험을 바탕으로", "검증된 역량과 노하우를 보유하고 있습니다."], (383, 416)),
              (702, 1288, "B", 773, 838, "공공행정 정보화 사업 특징",
               ["공공행정의 특수성을 이해하고,", "법·제도, 보안, 대국민 서비스 관점의", "요구사항을 반영합니다."], (375, 406, 437)),
              (1320, 1962, "C", 1394, 1458, "운영 및 유지관리 S-ISM 방법론",
               ["체계적인 운영·유지관리 프로세스와", "S-ISM 방법론을 통해 안정적이고", "지속가능한 서비스를 제공합니다."], (375, 406, 437))]
    for x0, x1, ch, cx, tx, title, desc, ys in panels:
        c.rrect(g.X(x0), g.Y(288), (x1 - x0) * K, 413 * K, adj=0.03, fill=c.rgb(x0 + 15, 310), line=LN, lw=1.0)
        c.write(c.oval(g.X(cx - 42), g.Y(302), 84 * K, 84 * K, fill=CB), [[(ch, 21, WHITE, F3)]])
        T(g, tx, 331, [(title, 11.1, HEAD, F3)], h=44)
        for d, y in zip(desc, ys):
            T(g, tx, y, [(d, 8, TXT, F2)], h=30)

    # A: 인물 + 타일 4
    c.pic(c.crop("manA", 55, 428, 280, 692, cut=(60, 440)), g.X(55), g.Y(428), 225 * K)
    for (tx0, ty0, th, lab) in ((283, 450, 107, "새올행정"), (445, 450, 107, "세움터"), (283, 570, 106, "행안부"), (445, 570, 106, "기타")):
        c.rrect(g.X(tx0), g.Y(ty0), 147 * K, th * K, adj=0.15, fill=WHITE, line=hexrgb("E3EEFB"), lw=0.5)
        c.pic(c.crop("tile%d_%d" % (tx0, ty0), tx0 + 36, ty0 + 8, tx0 + 112, ty0 + 68), g.X(tx0 + 36), g.Y(ty0 + 8), 76 * K)
        T(g, tx0, ty0 + 84, [(lab, 8, HEAD, F3)], w=147, h=30, align=CENTER)

    # 더하기 원
    for px in (688, 1305):
        c.oval(g.X(px - 46), g.Y(421), 92 * K, 92 * K, fill=CB, line=WHITE, lw=1.5)
        c.rrect(g.X(px - 21), g.Y(463), 42 * K, 8 * K, adj=0.5, fill=WHITE)
        c.rrect(g.X(px - 4), g.Y(446), 8 * K, 42 * K, adj=0.5, fill=WHITE)

    # B: 인물 + 목록 4
    c.pic(c.crop("womanB", 722, 447, 965, 690, cut=(730, 600), cut_thresh=60), g.X(722), g.Y(447), 243 * K)
    for i, lab in enumerate(["법·제도 준수", "보안 강화", "대국민 서비스", "변화 대응"]):
        y0 = 463 + i * 56
        c.rrect(g.X(972), g.Y(y0), 268 * K, 52 * K, adj=0.15, fill=c.rgb(1200, y0 + 12))
        c.pic(c.crop("li%d" % i, 998, y0 + 3, 1050, y0 + 49, cut=(1200, y0 + 12), cut_thresh=20), g.X(998), g.Y(y0 + 3), 52 * K)
        T(g, 1068, y0 + 27, [(lab, 8.5, INK, F2)], w=170, h=30)

    # C: 인물 + 순환 고리 + 확인 목록
    c.pic(c.crop("manC", 1335, 465, 1592, 690, cut=(1345, 600), cut_thresh=60), g.X(1335), g.Y(465), 257 * K)
    c.pic(c.crop("cycle", 1598, 470, 1794, 670, cut=(1600, 472)), g.X(1598), g.Y(470), 196 * K)
    b = c.oval(g.X(1638), g.Y(512), 116 * K, 116 * K, fill=c.rgb(1645, 570))
    c.write(b, [[("S-ISM", 10, INK, F3)], [("방법론", 10, INK, F3)]])
    c.rrect(g.X(1806), g.Y(496), 140 * K, 158 * K, adj=0.08, fill=c.rgb(1900, 550))
    for y, lab in ((524, "표준화"), (575, "체계화"), (626, "지속개선")):
        c.pic(c.crop("chk%d" % y, 1821, y - 14, 1849, y + 14), g.X(1821), g.Y(y - 14), 28 * K)
        T(g, 1858, y, [(lab, 8, INK, F2)], w=90, h=28)

    # ── 아래 화살표 ──
    ga = c.grp(705, 731)
    c.shape(MSO_SHAPE.FLOWCHART_MERGE, ga.X(900), ga.Y(705), 186 * K, 26 * K, fill=c.rgb(990, 712))

    # ── 5단계 상자 ──
    g = c.grp(735, 1092)
    c.rrect(g.X(38), g.Y(735), 1924 * K, 357 * K, adj=0.03, fill=WHITE, line=LN, lw=1.0)
    b = c.shape(MSO_SHAPE.ROUND_2_SAME_RECTANGLE, g.X(38), g.Y(735), 1924 * K, 55 * K, fill=c.rgb(300, 765), adj=[0.2, 0])
    c.write(b, [[("S-ISM 방법론 기반 5단계 청주시에 적합한 기능개선 체계", 11.5, WHITE, F3)]])
    cards = [(70, 423, "서비스요청(SR) 처리", (120, 395), ["사용자 및 현업의 서비스 요청을", "접수하고 신속하게 처리합니다."]),
             (471, 811, "변경요청(RFC) 처리", (500, 782), ["기능개선, 정책변경 등", "변경요청을 검토하고 승인합니다."]),
             (859, 1180, "배포 관리", (935, 1110), ["안정적인 배포를 위해", "절차에 따라 배포를 관리합니다."]),
             (1228, 1547, "요구사항 관리", (1312, 1495), ["요구사항을 수집·분석하고", "우선순위를 관리합니다."]),
             (1595, 1930, "장애관리", (1640, 1900), ["장애를 신속히 탐지·조치하고", "재발방지 대책을 수립합니다."])]
    for i, (x0, x1, title, (px0, px1), desc) in enumerate(cards):
        w = x1 - x0
        c.rrect(g.X(x0), g.Y(809), w * K, 262 * K, adj=0.04, fill=c.rgb(x0 + 12, 930), line=LN, lw=0.75)
        c.shape(MSO_SHAPE.ROUND_2_SAME_RECTANGLE, g.X(x0), g.Y(809), w * K, 48 * K, fill=c.rgb(x0 + w - 30, 835), adj=[0.2, 0])
        c.write(c.oval(g.X(x0 + 14), g.Y(810), 52 * K, 52 * K, fill=CB), [[(str(i + 1), 12, WHITE, F3)]])
        T(g, x0 + 66, 835, [(title, 9.5, INK, F3)], w=w - 80, h=40, align=CENTER)
        c.pic(c.crop("card%d" % i, px0, 862, px1, 988, cut=(px0 + 2, 864), cut_thresh=30), g.X(px0), g.Y(862), (px1 - px0) * K)
        c.rrect(g.X(x0 + 12), g.Y(992), (w - 24) * K, 72 * K, adj=0.1, fill=c.rgb(x0 + 30, 1060))
        T(g, x0, 1017, [(desc[0], 7, TXT, F2)], w=w, h=28, align=CENTER)
        T(g, x0, 1046, [(desc[1], 7, TXT, F2)], w=w, h=28, align=CENTER)
        if i < 4:
            nx = cards[i + 1][0]
            mx = (x1 + nx) / 2.0
            c.shape(MSO_SHAPE.CHEVRON, g.X(mx - 8), g.Y(896), 16 * K, 32 * K, fill=c.rgb(447, 912), adj=0.6)
