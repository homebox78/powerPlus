"""21쪽 — 유지보수 관리 체계 (5/5): 테스트 방안·배포 절차 흐름도 (시안 15번).

흐름도의 상자·마름모·화살표는 전부 PowerPoint 도형. 그림(인물·아이콘)만 시안에서 오린다.
세로: 상자(패널·행·카드)는 c.cy 로 늘려 그리고, 안쪽 내용은 덩어리(grp) 중심에 원래 배율로 둔다.
"""
from lib import *

PK = hexrgb("E9326F")      # NO·피드백 선
PKT = hexrgb("D92F7E")     # 분홍 글
GR = hexrgb("17A17F")      # YES·정상
ARW = hexrgb("137FFA")     # 파란 화살표
LNB = hexrgb("8DBEF8")     # 단계 상자 선
HB = hexrgb("2478E8")      # 머리 파랑


def build(c):
    title_font = F3
    for sh in c.s.shapes:
        if sh.name == "직사각형 23":
            for r in sh.text_frame.paragraphs[0].runs:
                ea = r._r.find(".//" + qn("a:ea"))
                title_font = (ea.get("typeface") if ea is not None else None) or r.font.name or F3
    c.keep_only("TextBox 19")
    c.vmap(105, 0.93, 1075, 7.12)
    V = c.cy

    def box(fn, x0, y0, x1, y1, **kw):          # 세로를 늘려 그리는 상자
        return fn(x0 * K, V(y0), (x1 - x0) * K, V(y1) - V(y0), **kw)

    def txt(g, x0, x1, yc, lines, align=CENTER, h=30, **kw):
        n = len(lines)
        return c.text(g.X(x0), g.Y(yc - h * n / 2.0), (x1 - x0) * K, h * n * K, lines, align, **kw)

    def pic(g, name, x0, y0, x1, y1, dx=0, dy=0, **kw):
        return c.pic(c.crop(name, x0, y0, x1, y1, **kw), g.X(x0 + dx), g.Y(y0 + dy), (x1 - x0) * K)

    def chev(g, x, y, col=ARW):
        c.shape(MSO_SHAPE.CHEVRON, g.X(x - 5), g.Y(y - 8), 11 * K, 16 * K, fill=col, adj=0.5)

    # ── 제목 ──
    g = c.grp(118, 195)
    pic(g, "shield", 44, 116, 114, 197)
    txt(g, 148, 1600, 156, [[("체계적 테스트 및 배포 절차의 수행으로 ", 19, NAVY, title_font),
                             ("안정적이고 완전한 반영", 19, hexrgb("1769E0"), title_font)]], LEFT, h=60)

    # ── 왼쪽 패널: 테스트 방안 및 절차 ──
    box(c.rrect, 35, 215, 1420, 1070, adj=0.012, fill=WHITE, line=hexrgb("C0E3FC"), lw=1.0)
    box(c.rrect, 36, 216, 1419, 268, adj=0.2, fill=hexrgb("F2F8FD"))
    box(c.rrect, 35, 215, 420, 268, adj=0.22, fill=HB)
    c.shape(MSO_SHAPE.PARALLELOGRAM, 380 * K, V(215), 84 * K, V(268) - V(215), fill=HB, adj=0.35)
    g = c.grp(215, 268)
    pic(g, "gear", 54, 221, 96, 262, cut=(45, 240))
    txt(g, 115, 420, 241, [[("테스트 방안 및 절차", 11.5, WHITE, F3)]], LEFT, h=40)

    rows = [
        (297, 410, "1", "단위시험", "(개발환경)", (298, 302, 444, 407),
         [["단위시험계획", "수립"], ["시험데이터", "준비"], ["단위시험", "실시"]]),
        (431, 545, "2", "통합시험", "(개발환경)", (298, 437, 444, 543),
         [["통합시험계획", "수립"], ["시험데이터", "준비"], ["통합시험", "실시"]]),
        (565, 682, "3", "통합시험", "(운영환경)", (298, 572, 444, 681),
         [["운영 시험계획·", "시스템 환경준비"], ["시험 데이터", "준비"], ["운영 시험", "실시"]]),
        (702, 822, "4", "연계시스템 통합시험", "(선택적)", (314, 712, 452, 819),
         [["연계시험계획", "수립"], ["연계시험 협의", "(선택적)"], ["연계 데이터", "준비"], ["연계 시험", "실시"]]),
    ]
    for y0, y1, num, name, sub, ill, steps in rows:
        box(c.rrect, 50, y0, 1405, y1, adj=0.12, fill=hexrgb("F2F8FD"), line=hexrgb("C7E9FD"), lw=0.75)
        g = c.grp(y0, y1); m = (y0 + y1) / 2.0
        c.write(c.oval(g.X(62), g.Y(m - 29), 58 * K, 58 * K, fill=hexrgb("2478EA")), [[(num, 14, WHITE, F3)]])
        pic(g, "ill" + num, *ill, cut=(460, y0 + 12), dx=20 if num == "4" else 0)
        txt(g, 138, 330, m - 17, [[(name, 8.5 if num == "4" else 10.5, NAVY, F3)]], LEFT, h=36)
        txt(g, 138, 330, m + 18, [[(sub, 9, NAVY, F2)]], LEFT, h=32)
        fy = m + 7                                   # 흐름 중심선
        if len(steps) == 3:
            xs = [(483, 632), (664, 834), (867, 1028)]; dcx, dw = 1146, 66; back = 947
            chs = [648, 851]; dbl = 1050; nox, fbx = 1025, 1109
        else:
            xs = [(483, 610), (637, 766), (793, 927), (955, 1086)]; dcx, dw = 1171, 61; back = 1020
            chs = [624, 780, 941]; dbl = None; nox, fbx = 1086, 1149
        for (a, b), lines in zip(xs, steps):
            r = c.rrect(g.X(a), g.Y(fy - 32), (b - a) * K, 64 * K, adj=0.22, fill=hexrgb("F8FBFE"), line=LNB, lw=1.0)
            c.write(r, [[(t, 7, NAVY, F3)] for t in lines])
        for x in chs: chev(g, x, fy)
        if dbl:
            chev(g, dbl - 6, fy); chev(g, dbl + 6, fy)
        else:
            chev(g, 1100, fy)
        # 마름모(판단)
        d = c.shape(MSO_SHAPE.DIAMOND, g.X(dcx - dw), g.Y(fy - 43), 2 * dw * K, 86 * K, fill=hexrgb("FED3E8"), line=hexrgb("FA83B7"), lw=0.75)
        c.write(d, [[("요건 충족", 7, PKT, F3)]])
        # NO → 되돌림
        ty = fy - 55
        c.line(g.X(dcx), g.Y(fy - 43), g.X(dcx), g.Y(ty), PK, 1.0)
        c.line(g.X(dcx), g.Y(ty), g.X(back), g.Y(ty), PK, 1.0)
        c.line(g.X(back), g.Y(ty), g.X(back), g.Y(fy - 33), PK, 1.0, arrow=True)
        txt(g, nox - 30, nox + 30, ty - 15, [[("NO", 7, PK, F3)]], h=22)
        txt(g, fbx - 40, fbx + 40, ty - 15, [[("피드백", 7, PK, F3)]], h=22)
        # YES → 결과보고
        ex = dcx + dw
        c.line(g.X(ex + 2), g.Y(fy), g.X(ex + 74), g.Y(fy), GR, 1.25, arrow=True)
        txt(g, ex, ex + 70, fy - 17, [[("YES", 7, GR, F3)]], h=22)
        dx0 = 1318 if len(steps) == 3 else 1320
        c.pic(c.crop("doc" + num, dx0, y0 + 20, dx0 + 48, y0 + 72 + (4 if num == "4" else 0)), g.X(dx0), g.Y(fy - 48), 48 * K)
        txt(g, 1282, 1403, fy + 27, [[("결과보고", 7, NAVY, F3)], [("및 검토", 7, NAVY, F3)]], h=19)

    # ── 아래 두 상자 ──
    def under(x0, x1, title, icon):
        box(c.rrect, x0, 838, x1, 1053, adj=0.05, fill=WHITE, line=hexrgb("6FAEF5"), lw=1.0)
        b = c.shape(MSO_SHAPE.ROUND_2_SAME_RECTANGLE, x0 * K, V(838), (x1 - x0) * K, V(888) - V(838), fill=hexrgb("2782F2"), adj=[0.25, 0])
        g = c.grp(838, 888)
        pic(g, *icon, cut=(icon[1] + 40, 862))
        txt(g, x0 + 71, x1, 863, [[(title, 9, WHITE, F3)]], LEFT, h=36)

    under(51, 702, "테스트 대상 유지보수 활동", ("clip", 66, 842, 106, 886))
    under(720, 1403, "유지보수 표준절차 준수", ("shd", 736, 842, 780, 886))

    g = c.grp(902, 1037)
    L = [(66, 180, (96, 912, 152, 966), ["비정상 종료", "보완"]),
         (196, 311, (226, 912, 282, 966), ["효율 사용", "위한 변경"]),
         (327, 434, (352, 912, 408, 966), ["이용자 요구", "분석 개선"]),
         (447, 574, (482, 910, 544, 966), ["법·제도·업무", "환경변화", "기능개선"]),
         (588, 690, (608, 912, 670, 966), ["새로운 OS", "변경 반영"])]
    for i, (a, b, ic, lines) in enumerate(L):
        box(c.rrect, a, 902, b, 1037, adj=0.08, fill=hexrgb("EEF6FE"), line=hexrgb("D6E9FC"), lw=0.75)
        pic(g, "a%d" % i, *ic, dy=-6)
        sz = 7
        txt(g, a - 6, b + 6, 1002, [[(t, sz, NAVY, F3)] for t in lines], h=24)
    R = [(738, 860, ["변경영향평가", "테스트 수준", "정의"]),
         (874, 992, ["변경계획", "통합테스트", "시나리오"]),
         (1008, 1127, ["체크리스트", "단위테스트"]),
         (1141, 1259, ["시나리오", "통합테스트", "개발·운영 환경"]),
         (1274, 1390, ["연계 시스템", "통합테스트", "(선택적)"])]
    for i, (a, b, lines) in enumerate(R):
        box(c.rrect, a, 908, b, 1037, adj=0.08, fill=hexrgb("EEF6FE"), line=hexrgb("D6E9FC"), lw=0.75)
        m = (a + b) / 2.0
        c.write(c.oval(g.X(m - 12), g.Y(905), 24 * K, 24 * K, fill=hexrgb("1F66D8")), [[(str(i + 1), 7, WHITE, F3)]])
        txt(g, a, b, 984, [[(t, 7, NAVY, F3)] for t in lines], h=24)

    # ── 오른쪽 패널: 배포 절차 ──
    box(c.rrect, 1441, 212, 1968, 1070, adj=0.03, fill=WHITE, line=hexrgb("C2E0FB"), lw=1.0)
    c.shape(MSO_SHAPE.ROUND_2_SAME_RECTANGLE, 1441 * K, V(210), 527 * K, V(265) - V(210), fill=hexrgb("2171E0"), adj=[0.3, 0])
    g = c.grp(210, 265)
    pic(g, "plane", 1460, 218, 1508, 260, cut=(1800, 238))
    txt(g, 1522, 1900, 238, [[("배포 절차", 11.5, WHITE, F3)]], LEFT, h=40)

    CX = 1706
    RB = dict(fill=hexrgb("EAF3FE"), line=hexrgb("ABD1FC"), lw=0.75)

    def down(ya, yb):
        c.line(CX * K, V(ya) + 0.01, CX * K, V(yb) - 0.01, ARW, 1.25, arrow=True)

    def bullets(g, x, yc, items):
        txt(g, x, 1925, yc, [[("•  " + t, 7, NAVY, F2)] for t in items], LEFT, h=23)

    # 1
    box(c.rrect, 1484, 285, 1927, 342, adj=0.4, **RB); g = c.grp(285, 342)
    pic(g, "code", 1570, 288, 1638, 337, cut=(1500, 330))
    txt(g, 1640, 1840, 312, [[("프로그램/DB 변경", 8, NAVY, F3)]], h=34)
    down(342, 367)
    # 2
    box(c.rrect, 1484, 367, 1927, 465, adj=0.25, **RB); g = c.grp(367, 465)
    pic(g, "gear2", 1518, 376, 1580, 434, cut=(1500, 400), dy=10)
    txt(g, 1620, 1925, 395, [[("자체 테스트 배포 실시", 8, NAVY, F3)]], LEFT, h=32)
    bullets(g, 1620, 435, ["DB 검증 (DB배포)", "실패일 경우 배포 연기"])
    down(465, 490)
    # 3
    box(c.rrect, 1484, 490, 1927, 617, adj=0.2, **RB); g = c.grp(490, 617)
    pic(g, "person", 1518, 500, 1580, 558, cut=(1500, 600), dy=24)
    txt(g, 1620, 1925, 520, [[("운영서버 배포 승인", 8, NAVY, F3)]], LEFT, h=32)
    txt(g, 1620, 1925, 574, [[("•  배포·적용시간은", 7, NAVY, F2)], [("    업무 마감 후에 실시", 7, NAVY, F2)], [("•  고객의 승인단계 포함", 7, NAVY, F2)]], LEFT, h=23)
    down(617, 641)
    # 4
    box(c.rrect, 1484, 641, 1927, 698, adj=0.4, **RB); g = c.grp(641, 698)
    pic(g, "server", 1524, 648, 1576, 694, cut=(1500, 690))
    txt(g, 1606, 1806, 669, [[("운영서버 배포 수행", 8, NAVY, F3)]], h=34)
    down(698, 722)
    # 5
    box(c.rrect, 1484, 722, 1927, 797, adj=0.3, **RB); g = c.grp(722, 797)
    pic(g, "find", 1518, 731, 1576, 787, cut=(1500, 760))
    txt(g, 1620, 1925, 746, [[("운영서버 배포 확인", 8, NAVY, F3)]], LEFT, h=32)
    bullets(g, 1620, 776, ["통합테스트 수행"])
    down(797, 822)
    # 판단
    d = c.shape(MSO_SHAPE.DIAMOND, 1568 * K, V(822), 276 * K, V(920) - V(822), fill=hexrgb("FED8EA"), line=hexrgb("FA9BC6"), lw=0.75)
    g = c.grp(822, 920)
    pic(g, "warn", 1629, 851, 1666, 886, cut=(1600, 868), dx=4)
    txt(g, 1678, 1800, 869, [[("운영서버 배포", 7, PKT, F3)], [("장애여부", 7, PKT, F3)]], LEFT, h=24)
    # 분기
    gb = c.grp(953, 1038)
    c.line(1626 * K, V(902), 1590 * K, V(953) - 0.02, PK, 1.25, arrow=True)
    c.line(1786 * K, V(902), 1822 * K, V(953) - 0.02, GR, 1.25, arrow=True)
    c.text(1490 * K, V(917) - 0.1, 110 * K, 0.2, [[("장애 시", 7.5, PK, F3)]])
    c.text(1815 * K, V(917) - 0.1, 110 * K, 0.2, [[("정상 시", 7.5, GR, F3)]])
    box(c.rrect, 1472, 953, 1694, 1038, adj=0.18, fill=hexrgb("FEE9F3"), line=hexrgb("FD9DC7"), lw=1.0)
    pic(gb, "undo", 1500, 966, 1556, 1024, cut=(1490, 1000))
    txt(gb, 1572, 1690, 996, [[("원상복구", 8, hexrgb("C0095D"), F3)], [("피드백", 8, hexrgb("C0095D"), F3)]], LEFT, h=27)
    box(c.rrect, 1717, 953, 1939, 1038, adj=0.18, fill=hexrgb("E1F6EE"), line=hexrgb("80D4C0"), lw=1.0)
    pic(gb, "okc", 1748, 968, 1800, 1022, cut=(1740, 1000))
    txt(gb, 1810, 1937, 996, [[("결과확인 →", 8, hexrgb("0B7D60"), F3)], [("결과보고", 8, hexrgb("0B7D60"), F3)]], LEFT, h=27)
