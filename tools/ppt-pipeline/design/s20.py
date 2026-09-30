"""20쪽 — 유지보수 관리 체계 (4/5) (시안 14번). 흐름도·표는 전부 도형, 문구는 원래 장표 기준."""
from lib import *


def build(c):
    title_font = F3
    for sh in c.s.shapes:
        if sh.name == "직사각형 358":
            for r in sh.text_frame.paragraphs[0].runs:
                ea = r._r.find(".//" + qn("a:ea"))
                title_font = (ea.get("typeface") if ea is not None else None) or r.font.name or F3
    c.keep_only("TextBox 13")
    c.vmap(95, 0.87, 1125, 7.65)
    KY = (7.65 - 0.87) / (1125 - 95.0)
    X = lambda x: x * K
    Y = c.cy
    c.background()

    NV = hexrgb("0C3B6D"); BL = hexrgb("2F74E0"); LN = hexrgb("2767C9")
    PK = hexrgb("D53389"); PKT = hexrgb("B0226F"); GR = hexrgb("3CB587")
    EDGE = hexrgb("D3E3F7")

    # ── 키메시지 + 그림 ──
    g = c.grp(100, 292)
    c.pic(c.crop("hero", 1040, 112, 1836, 292, cut=(1045, 114), cut_thresh=60), g.X(1040), g.Y(112), 796 * K)
    b = c.rrect(g.X(1838), g.Y(124), 116 * K, 78 * K, adj=0.18, fill=c.rgb(1890, 160))
    c.write(b, [[("빠른처리", 8, WHITE, F3)], [("정확한대응", 8, WHITE, F3)]])
    c.rect(g.X(45), g.Y(137), 13 * K, 118 * K, fill=c.rgb(50, 200))
    c.text(g.X(84), g.Y(130), 900 * K, 130 * K,
           [[("요청 유형에 적합한 처리절차의 진행으로", 18, NV, title_font)],
            [("신속하고 정확한 대응", 18, c.rgb(300, 225), title_font)]], LEFT, spacing=1.05)

    # ── 왼쪽 판: 서비스 요청 처리 절차 ──
    P0, P1 = Y(290), Y(1030)
    c.rrect(X(42), P0, X(1113), P1 - P0, adj=0.025, fill=WHITE, line=EDGE, lw=0.75)
    HB = c.rgb(700, 320); hh = Y(356) - P0
    c.rect(X(42), P0, X(850), hh, fill=HB)
    c.shape(MSO_SHAPE.RIGHT_TRIANGLE, X(892), P0, X(45), hh, fill=HB)
    c.pic(c.crop("tree", 60, 298, 110, 346, cut=(62, 300), cut_thresh=40), X(60), P0 + hh / 2 - 24 * K, 50 * K)
    c.text(X(130), P0, X(600), hh, [[("서비스 요청 처리 절차", 12.5, WHITE, F3)]], LEFT)

    lanes = [(57, 327), (335, 640), (648, 1142)]
    HBG = c.rgb(80, 400)
    for x0, x1 in lanes:
        c.rect(X(x0), Y(450), X(x1 - x0), Y(1015) - Y(450), fill=hexrgb("FAFCFF"), line=EDGE, lw=0.5)
        c.rrect(X(x0), Y(370), X(x1 - x0), Y(445) - Y(370), adj=0.08, fill=HBG)
    hc = (Y(370) + Y(445)) / 2
    c.pic(c.crop("user", 100, 376, 163, 445, cut=(98, 400), cut_thresh=30), X(100), hc - 34 * K, 63 * K)
    c.text(X(180), Y(370), X(140), Y(445) - Y(370), [[("사용자", 11.5, BL, F3)]], LEFT)
    c.pic(c.crop("mgr", 388, 376, 446, 445, cut=(384, 400), cut_thresh=30), X(388), hc - 34 * K, 58 * K)
    c.text(X(458), Y(370), X(180), Y(445) - Y(370), [[("청주시 담당자 및", 8.5, NV, F3)], [("IT 서비스 책임자", 8.5, NV, F3)]], LEFT)
    c.pic(c.crop("gear", 746, 376, 798, 428, cut=(744, 400), cut_thresh=30), X(746), hc - 26 * K, 52 * K)
    c.text(X(818), Y(370), X(320), Y(445) - Y(370), [[("상주 유지관리 담당자", 10, NV, F3)]], LEFT)

    # 흐름도 도형
    def box(xc, yc, w, txt, style="light", h=40, icon=None, size=8):
        l, t, ww, hgt = X(xc - w / 2.0), Y(yc - h / 2.0), X(w), h * KY
        if style == "fill":
            b = c.pill(l, t, ww, hgt, fill=hexrgb("2F78E6")); col = WHITE
        elif style == "line":
            b = c.rrect(l, t, ww, hgt, adj=0.3, fill=WHITE, line=hexrgb("4C8FE8"), lw=1.0); col = NV
        elif style == "green":
            b = c.rrect(l, t, ww, hgt, adj=0.25, fill=hexrgb("EAF7F1"), line=GR, lw=1.0); col = hexrgb("014D68")
        elif style == "pink":
            b = c.pill(l, t, ww, hgt, fill=hexrgb("FEF3F8"), line=PK, lw=1.0); col = PKT
        else:
            b = c.rrect(l, t, ww, hgt, adj=0.25, fill=hexrgb("DFEEFE"), line=hexrgb("7FB2EE"), lw=0.75); col = NV
        if icon:
            c.write(b, [[(txt, 7, col, F3)]], LEFT, margin=0.31)
            p = c.crop(*icon[0], cut=icon[1], cut_thresh=40)
            ih = 0.19
            pic = c.pic(p, l + 0.09, t + hgt / 2 - ih / 2, h=ih)
        else:
            c.write(b, [[(txt, size, col, F3)]])
        return b

    def dia(xc, yc, w, lines, pink=False, h=68):
        b = c.shape(MSO_SHAPE.DIAMOND, X(xc - w / 2.0), Y(yc - h / 2.0), X(w), h * KY,
                    fill=hexrgb("FEF3F8") if pink else hexrgb("ECF4FE"), line=PK if pink else hexrgb("5B9BEA"), lw=1.0)
        c.write(b, [[(t, 7.5, PKT if pink else NV, F3)] for t in lines], spacing=0.9)

    def path(pts, color=LN):
        for i in range(len(pts) - 1):
            (x0, y0), (x1, y1) = pts[i], pts[i + 1]
            c.line(X(x0), Y(y0), X(x1), Y(y1), color, 1.0, arrow=(i == len(pts) - 2))

    def lab(x, y, t, color=NV):
        c.text(X(x - 25), Y(y) - 0.07, X(50), 0.14, [[(t, 7, color, F3)]])

    L1, L2, A, B = 192, 487, 790, 1020
    I_DOC = (("i_doc", 104, 489, 134, 528), (102, 508))
    I_CHAT = (("i_chat", 91, 609, 131, 649), (88, 630))
    I_MAN = (("i_man", 99, 734, 135, 774), (96, 755))
    I_CHK = (("i_chk", 107, 856, 147, 896), (104, 875))
    def ic(i, n): return ((i[0][0] + n,) + i[0][1:], i[1])

    # 화살표 먼저(도형 아래로)
    path([(L1 + 114, 480), (A - 100, 480)])                       # 요청 → 접수
    path([(A, 500), (A, 516)])                                    # 접수 → 단순 해결
    path([(A, 580), (A, 598)]); lab(A + 16, 588, "Y")             # Y → 문제 해결
    path([(A - 100, 618), (L1 + 114, 618)])                       # 문제 해결 → 답변
    path([(L1, 638), (L1, 660)]); path([(L1, 700), (L1, 721)])    # 답변 → 확인 → 종료
    path([(A + 100, 548), (1005, 548), (1005, 586)]); lab(920, 536, "N")
    path([(1090, 618), (1120, 618), (1120, 685)]); lab(1108, 605, "N")   # → 변경 처리
    path([(1005, 650), (1005, 662), (L2, 662), (L2, 671)]); lab(1022, 657, "Y")
    path([(L2, 739), (L2, 759)], PK); lab(L2 + 36, 749, "기각", PKT)
    path([(L2 + 115, 705), (A - 100, 705)]); lab(L2 + 135, 693, "Y")
    path([(A + 100, 705), (950, 705), (950, 826)]); lab(966, 765, "Y")
    path([(B - 100, 846), (A + 100, 846)])                        # 작성 → 확인
    path([(A - 100, 846), (L2 + 115, 846)])                       # 확인 → 승인
    path([(L2, 880), (L2, 899), (A, 899), (A, 918)]); lab(L2 + 18, 890, "Y")
    path([(A - 100, 938), (L1 + 114, 938)])                       # 자료 처리 → 요청자 확인
    path([(L1, 958), (L1, 971)])

    box(L1, 480, 228, "유지관리요청", "fill", icon=ic(I_DOC, ""))
    box(L1, 618, 228, "유지관리 요청 답변", "line", icon=ic(I_CHAT, ""))
    box(L1, 680, 228, "요청자 확인", "line", icon=ic(I_MAN, "1"))
    box(L1, 740, 228, "종료", "fill", h=38, icon=ic(I_CHK, "1"))
    box(L1, 938, 228, "요청자 확인", "line", icon=ic(I_MAN, "2"))
    box(L1, 990, 228, "종료", "fill", h=38, icon=ic(I_CHK, "2"))

    dia(L2, 705, 230, ["IT서비스", "책임자 승인"], pink=True)
    box(L2, 778, 120, "종료", "pink", h=38)
    dia(L2, 846, 230, ["IT서비스", "책임자 승인"], pink=True)

    box(A, 480, 200, "요청 접수", "fill")
    dia(A, 548, 200, ["단순 해결"], h=64)
    box(A, 618, 200, "문제 해결", "green")
    dia(1005, 618, 170, ["자료처리", "지원"], h=64)
    box(1070, 705, 120, "변경 처리")
    dia(A, 705, 200, ["스크립트", "지원 여부"])
    box(B, 846, 200, "스크립트 작성")
    box(A, 846, 200, "스크립트 확인")
    box(A, 938, 200, "자료 처리")

    # ── 오른쪽 판: 서비스 요청 유형별 처리 내용 ──
    c.rrect(X(1180), P0, X(783), P1 - P0, adj=0.025, fill=WHITE, line=EDGE, lw=0.75)
    c.shape(MSO_SHAPE.ROUND_2_SAME_RECTANGLE, X(1180), P0, X(783), hh, fill=HB, adj=[0.3, 0])
    c.pic(c.crop("gear2", 1198, 302, 1248, 352, cut=(1196, 304), cut_thresh=40), X(1198), P0 + hh / 2 - 25 * K, 50 * K)
    c.text(X(1268), P0, X(600), hh, [[("서비스 요청 유형별 처리 내용", 12.5, WHITE, F3)]], LEFT)

    C0, C1, C2, C3 = 1194, 1388, 1617, 1947
    TH = c.rgb(1500, 403); TL = hexrgb("D9E6F0")
    for x0, x1, t in ((C0, C1, "조치유형"), (C1, C2, "세부유형"), (C2, C3, "내용")):
        b = c.rect(X(x0), Y(375), X(x1 - x0), Y(432) - Y(375), fill=TH, line=WHITE, lw=0.75)
        c.write(b, [[(t, 10, WHITE, F3)]])

    groups = [
        (435, [500, 565], ["단순 해결"], "w1", (1207, 467, 1273, 533), False,
         [("단순답변", ["단순 문의에 대한 답변 처리"]), ("기술지원", ["시스템 기술지원/운영상태 점검"])]),
        (575, [640, 704, 768], ["자료 처리", "지원"], "w2", (1207, 643, 1273, 709), False,
         [("자료처리", ["자료처리·보정 지원"]), ("자료전환", ["시스템 확산 등을 위한", "자료 전환 수행"]),
          ("자료요청", ["사용자로부터 요청되는", "일괄 다운로드 자료"])]),
        (778, [862, 912, 961, 1010], ["시스템", "변경 처리"], "w3", (1207, 852, 1273, 918), True,
         [("기능개선", ["제도 변경사항 반영,", "기술·업무환경 변경사항 반영,", "자체 기능개선"]), ("오류정정", ["하자사항 및 오류 보완"]),
          ("연계지원", ["정보연계 및 모니터링"]), ("장애복구", ["장애예방 및 복구"])]),
    ]
    for y0, ends, label, nm, ib, pink, rows in groups:
        y1 = ends[-1]
        lf = hexrgb("FAE9F3") if pink else hexrgb("E1EFFE")
        c.rrect(X(C0), Y(y0), X(C1 - C0), Y(y1) - Y(y0), adj=0.04, fill=lf)
        mid = (Y(y0) + Y(y1)) / 2
        c.pic(c.crop(nm, *ib, cut=(ib[0] - 2, ib[1] + 1), cut_thresh=40), X(ib[0]), mid - 33 * K, 66 * K)
        c.text(X(1285), Y(y0), X(100), Y(y1) - Y(y0), [[(t, 9, PKT if pink else BL, F3)] for t in label], LEFT)
        ya = y0
        for yb, (sub, cont) in zip(ends, rows):
            b = c.rect(X(C1), Y(ya), X(C2 - C1), Y(yb) - Y(ya), fill=hexrgb("FDF3F9") if pink else hexrgb("F3F9FD"), line=TL, lw=0.5)
            c.write(b, [[(sub, 9, hexrgb("8E1B5C") if pink else NV, F3)]], LEFT, margin=0.17)
            b = c.rect(X(C2), Y(ya), X(C3 - C2), Y(yb) - Y(ya), fill=WHITE, line=TL, lw=0.5)
            c.write(b, [[(t, 7.5, hexrgb("1F2D3D"), F2)] for t in cont], LEFT, margin=0.12, wrap=True)
            ya = yb

