"""13쪽 — 관리체계 확립 (2/2) (시안 8번). AS-IS / TO-BE."""
from lib import *


def _title_font(shapes, name):
    for sh in shapes:
        if sh.shape_type == 6:
            f = _title_font(sh.shapes, name)
            if f: return f
        elif sh.name == name and sh.has_text_frame:
            for r in sh.text_frame.paragraphs[0].runs:
                ea = r._r.find(".//" + qn("a:ea"))
                return (ea.get("typeface") if ea is not None else None) or r.font.name
    return None


def build(c):
    KF = _title_font(c.s.shapes, "직사각형 151") or F3      # 키메시지 서체
    c.keep_only("TextBox 79")                               # 머리말 글만 남긴다
    c.vmap(132, 1.0, 1053, 7.12)
    c.background(1000, 270)

    def dark(x0, y0, x1, y1):
        """영역에서 가장 짙은 점의 색(글자색 읽기)."""
        best = None
        for y in range(int(y0 * c.Z), int(y1 * c.Z)):
            for x in range(int(x0 * c.Z), int(x1 * c.Z)):
                p = c.D.getpixel((x, y))
                if best is None or sum(p) < sum(best): best = p
        return RGBColor(*best)

    def box(x0, y0, x1, y1, **kw):
        """세로를 vmap 으로 늘린 둥근 상자."""
        return c.rrect(x0 * K, c.cy(y0), (x1 - x0) * K, c.cy(y1) - c.cy(y0), **kw)

    NV = dark(240, 235, 900, 270)
    SL = c.rgb(70, 345)          # AS-IS 회청
    BL = c.rgb(1040, 347)        # TO-BE 파랑

    # ── 전략 띠 ──
    g = c.grp(132, 196)
    c.shape(MSO_SHAPE.PENTAGON, g.X(60), g.Y(132), 1902 * K, 64 * K, fill=c.rgb(1700, 150), adj=0.4)
    PK = c.rgb(60, 165)
    c.shape(MSO_SHAPE.PENTAGON, g.X(110), g.Y(132), 110 * K, 64 * K, fill=PK, adj=0.4)
    c.pill(g.X(40), g.Y(132), 150 * K, 64 * K, fill=PK)
    c.text(g.X(40), g.Y(132), 170 * K, 64 * K, [[("전략 2", 13.5, WHITE, F3)]])
    c.text(g.X(250), g.Y(132), 900 * K, 64 * K, [[("서비스 지속성을 위한 관리체계를 확립합니다.", 13.5, dark(250, 145, 900, 185), KF)]], LEFT)

    # ── ACT.4 ──
    g = c.grp(223, 281)
    c.write(c.pill(g.X(40), g.Y(223), 166 * K, 58 * K, fill=c.rgb(52, 252)), [[("ACT.4", 13, WHITE, F3)]])
    c.text(g.X(235), g.Y(223), 900 * K, 58 * K, [[("법제도 및 업무 변경 모니터링 체계 마련", 15, NV, F3)]], LEFT)

    # ── AS-IS 판 ──
    PF = c.rgb(110, 560)
    box(42, 295, 840, 1053, adj=0.03, fill=PF, line=c.rgb(42, 600), lw=1.0)
    g = c.grp(313, 377)
    c.write(c.pill(g.X(58), g.Y(313), 189 * K, 64 * K, fill=SL), [[("AS-IS", 14, WHITE, F3)]])
    c.text(g.X(272), g.Y(313), 300 * K, 64 * K, [[("수동적 대응", 13.5, dark(272, 325, 450, 365), F3)]], LEFT)

    g = c.grp(378, 705)
    DL = c.rgb(345, 470)
    for x0, y0, x1, y1 in ((333, 467, 368, 482), (543, 480, 578, 466), (330, 592, 365, 578), (545, 578, 578, 592)):
        c.line(g.X(x0), g.Y(y0), g.X(x1), g.Y(y1), DL, 1.5, dash=True)
    CF = c.rgb(200, 430); CT = dark(228, 478, 290, 500)
    for cx, cy_, r, ico, lab, ly in (
            (258, 450, 75, (222, 396, 296, 470), "법제도", 489),
            (649, 447, 72, (612, 394, 684, 466), "업무규정", 485),
            (257, 628, 77, (214, 572, 300, 646), "조례", 667),
            (650, 628, 76, (610, 572, 692, 644), "업무시스템", 663)):
        c.oval(g.X(cx - r), g.Y(cy_ - r), 2 * r * K, 2 * r * K, fill=CF)
        x0, y0, x1, y1 = ico
        c.pic(c.crop("ico%d_%d" % (cx, cy_), x0, y0, x1, y1, cut=(x0 + 2, y0 + 2)), g.X(x0), g.Y(y0), (x1 - x0) * K)
        c.text(g.X(cx - r), g.Y(ly - 16), 2 * r * K, 32 * K, [[(lab, 8.5, CT, F3)]])
    c.pic(c.crop("mgr", 368, 445, 545, 610, cut=(370, 447)), g.X(368), g.Y(445), 177 * K)
    c.write(c.pill(g.X(361), g.Y(608), 194 * K, 43 * K, fill=c.rgb(372, 630)), [[("유지관리 담당자", 8.5, WHITE, F3)]])

    g = c.grp(712, 900)
    c.pic(c.crop("p_it", 165, 712, 320, 857, cut=(167, 714)), g.X(165), g.Y(712), 155 * K)
    c.pic(c.crop("p_biz", 562, 715, 710, 857, cut=(564, 717)), g.X(562), g.Y(715), 148 * K)
    ar = c.line(g.X(327), g.Y(802), g.X(549), g.Y(802), c.rgb(440, 802), 2.5, arrow=True)
    ln = ar.line._get_or_add_ln(); he = etree.Element(qn("a:headEnd")); he.set("type", "triangle")
    ln.insert(list(ln).index(ln.find(qn("a:tailEnd"))), he)
    PP = c.rgb(160, 878)
    c.write(c.pill(g.X(151), g.Y(856), 220 * K, 43 * K, fill=PP), [[("정보통신담당자", 8.5, WHITE, F3)]])
    c.write(c.pill(g.X(521), g.Y(856), 216 * K, 43 * K, fill=PP), [[("업무담당자", 8.5, WHITE, F3)]])

    g = c.grp(917, 1030)
    b = c.rrect(g.X(63), g.Y(917), 756 * K, 113 * K, adj=0.15, fill=c.rgb(80, 975))
    c.write(b, [[("업무처리 담당자 법제도 및 업무변경 요청", 9.3, dark(232, 938, 661, 962), F2)],
                [("'공문/서면으로 변경요청'", 10.4, dark(420, 980, 594, 1004), F3)]], spacing=1.25)

    # ── 가운데 화살표 ──
    g = c.grp(515, 712)
    c.pic(c.crop("arrow", 858, 515, 992, 712, cut=(860, 517)), g.X(858), g.Y(515), 134 * K)

    # ── TO-BE 판 ──
    box(1001, 293, 1961, 1053, adj=0.03, fill=c.rgb(1015, 700), line=c.rgb(1001, 700), lw=1.0)
    g = c.grp(313, 392)
    c.write(c.pill(g.X(1028), g.Y(313), 210 * K, 68 * K, fill=BL), [[("TO-BE", 15, WHITE, F3)]])
    TB = dark(1268, 315, 1755, 345)
    c.text(g.X(1268), g.Y(308), 640 * K, 88 * K, [[("법제도 및 업무 변경 모니터링을 통한", 12.2, TB, F3)],
                                                 [("체계적이고 능동적인 관리", 12.2, TB, F3)]], LEFT, spacing=1.1)

    CD = c.rgb(1045, 560); CL = c.rgb(1031, 520); NB = c.rgb(1060, 465)
    GY = dark(1251, 555, 1523, 580)

    def card(n, y0, y1, title, ty):
        box(1031, y0, 1931, y1, adj=0.1, fill=CD, line=CL, lw=0.75)
        g = c.grp(y0, y1)
        c.write(c.oval(g.X(1046), g.Y(ty - 37), 74 * K, 74 * K, fill=NB), [[(str(n), 17, WHITE, F3)]])
        c.text(g.X(1144), g.Y(ty - 25), 470 * K, 50 * K, [[(title, 11.2, NV, F3)]], LEFT)
        return g

    # 1
    g = card(1, 413, 620, "입법예고 및 요청사항 모니터링", 462)
    CH = c.rgb(1150, 519); CHT = dark(1163, 508, 1207, 530)
    for y, k, v in ((499, "주기", "일일"), (548, "대상", "법제처, 자치법규관리시스템")):
        c.write(c.pill(g.X(1144), g.Y(y), 82 * K, 40 * K, fill=CH), [[(k, 9, CHT, F3)]])
        c.text(g.X(1251), g.Y(y), 340 * K, 40 * K, [[(v, 9, GY, F2)]], LEFT)
    c.pic(c.crop("c1", 1600, 434, 1912, 602, cut=(1602, 436), cut_thresh=18), g.X(1600), g.Y(434), 312 * K)

    # 2
    g = card(2, 641, 815, "사용자 및 정보통신담당자 밀착 지원", 697)
    c.text(g.X(1144), g.Y(728), 440 * K, 70 * K,
           [[("사용자와의 유선, 대면 서비스 요청 접수 및", 8, GY, F2)], [("처리 결과 통보 시 법규정 변경 사항 식별", 8, GY, F2)]],
           LEFT, anchor="top", spacing=1.15)
    p = c.pic(c.crop("c2", 1612, 648, 1912, 812, cut=(1614, 650), cut_thresh=30), g.X(1612), g.Y(648), 300 * K)
    p.top = Inches(c.cy(815) - 0.025) - p.height          # 시안처럼 카드 바닥에 붙인다

    # 3
    g = card(3, 838, 1030, "전사 공유체계 활용", 897)
    c.text(g.X(1144), g.Y(930), 340 * K, 70 * K,
           [[("제안사의 업무시스템 유지관리", 7.5, GY, F2)], [("담당자들간의 법개정 관련 사항", 7.5, GY, F2)], [("공유체계 활용", 7.5, GY, F2)]],
           LEFT, anchor="top", spacing=1.15)
    c.pic(c.crop("c3", 1492, 845, 1890, 1024, cut=(1494, 847)), g.X(1492), g.Y(845), 398 * K)
