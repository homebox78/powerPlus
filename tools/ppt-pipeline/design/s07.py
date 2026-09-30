"""7쪽 — 사업의 대상 및 범위 (시안 3번). 수치·건수·부서 수는 원래 장표 값."""
from lib import *
from PIL import Image, ImageDraw

HEAD = MSO_SHAPE.ROUND_2_SAME_RECTANGLE


def build(c):
    c.keep_only("TextBox 221")
    c.background(1000, 626)
    c.vmap(381, 2.45, 848, 5.72)
    LN = hexrgb("C9DDF7")
    HB = c.rgb(700, 175)            # 머리 띠 파랑
    TINT = c.rgb(300, 243)          # 표 머리 옅은 파랑
    NUM = hexrgb("1F5FE0")

    def tx(g, x0, x1, yc, runs, align=CENTER, h=0.34):
        return c.text(g.X(x0), g.Y(yc) - h / 2, (x1 - x0) * K, h, [runs], align)

    def circ(name, cx, cy, r):
        p = c.crop(name, cx - r, cy - r, cx + r, cy + r)
        im = Image.open(p).convert("RGBA"); w, h = im.size
        m = Image.new("L", (w * 4, h * 4), 0); ImageDraw.Draw(m).ellipse((2, 2, w * 4 - 3, h * 4 - 3), fill=255)
        im.putalpha(m.resize((w, h), Image.LANCZOS)); im.save(p)
        return p

    # ───────── 위 왼쪽: 행정포털 유지보수 대상 ─────────
    g = c.grp(143, 620)
    c.rrect(g.X(40), g.Y(150), 1092 * K, 462 * K, adj=0.03, fill=WHITE, line=LN, lw=0.75)
    c.shape(HEAD, g.X(40), g.Y(143), 1092 * K, 63 * K, fill=HB, adj=[0.22, 0])
    c.pic(c.crop("h1", 66, 153, 124, 201, cut=(135, 175)), g.X(66), g.Y(153), 58 * K)
    tx(g, 142, 700, 175, [("행정포털(굿모닝) 유지보수 대상", 12.5, WHITE, F3)], LEFT)

    c.rrect(g.X(65), g.Y(221), 1045 * K, 276 * K, adj=0.03, fill=WHITE, line=LN, lw=0.75)
    c.shape(HEAD, g.X(65), g.Y(221), 1045 * K, 45 * K, fill=TINT, adj=[0.18, 0])
    for x0, x1, lab in ((65, 421, "구분"), (421, 770, "소스(본)"), (770, 1110, "DB 테이블")):
        tx(g, x0, x1, 244, [(lab, 8.5, NAVY, F3)])
    rows = [(295, "행정포털 메인", "184", "6"), (353, "공통 업무지원", "5,922", "282"),
            (410, "개별 업무지원", "4,303", "252"), (468, "정보광장", "161", "14")]
    for i, (yc, lab, a, b) in enumerate(rows):
        c.pic(c.crop("r%d" % i, 102, yc - 23, 150, yc + 23), g.X(102), g.Y(yc - 23), 48 * K)
        tx(g, 172, 420, yc, [(lab, 8.5, NAVY, F2)], LEFT)
        tx(g, 421, 770, yc, [(a, 10, NAVY, F3)])
        tx(g, 770, 1110, yc, [(b, 10, NAVY, F3)])
        if i:
            c.line(g.X(65), g.Y(yc - 29), g.X(1110), g.Y(yc - 29), LN, 0.5)
    for x in (421, 770):
        c.line(g.X(x), g.Y(221), g.X(x), g.Y(497), LN, 0.5)

    c.rrect(g.X(65), g.Y(513), 1045 * K, 75 * K, adj=0.18, fill=c.rgb(90, 550))
    c.pic(c.crop("src", 120, 530, 178, 571), g.X(120), g.Y(530), 58 * K)
    tx(g, 189, 350, 551, [("프로그램소스", 9, NAVY, F2)], LEFT)
    tx(g, 354, 560, 549, [("10,570", 15, NUM, F3), (" 본", 8, NUM, F3)], LEFT)
    c.line(g.X(576), g.Y(535), g.X(576), g.Y(566), hexrgb("9DBBEA"), 0.75)
    c.pic(c.crop("db", 646, 523, 696, 577), g.X(646), g.Y(523), 50 * K)
    tx(g, 710, 890, 551, [("DB 테이블", 9, NAVY, F2)], LEFT)
    tx(g, 898, 1090, 549, [("554", 15, NUM, F3), (" 개", 8, NUM, F3)], LEFT)

    # ───────── 위 오른쪽: 25개 요구사항 ─────────
    c.rrect(g.X(1159), g.Y(150), 804 * K, 470 * K, adj=0.03, fill=WHITE, line=LN, lw=0.75)
    c.shape(HEAD, g.X(1159), g.Y(143), 804 * K, 64 * K, fill=HB, adj=[0.22, 0])
    c.pic(c.crop("h2", 1185, 152, 1231, 202, cut=(1240, 175)), g.X(1185), g.Y(152), 46 * K)
    tx(g, 1250, 1900, 176, [("25개 요구사항 요약", 12.5, WHITE, F3)], LEFT)
    PB = c.rgb(1400, 250)
    req = [[("유지관리 수행", "6"), ("보안", "5"), ("제약사항", "3"), ("프로젝트지원", "2")],
           [("인력", "1"), ("인터페이스", "2"), ("프로젝트 관리", "5"), ("서비스수준협약", "1")]]
    for ci, (cx, x1) in enumerate(((1227, 1543), (1628, 1936))):
        for ri, yc in enumerate((267, 365, 464, 565)):
            lab, n = req[ci][ri]
            c.pill(g.X(cx), g.Y(yc - 33), (x1 - cx) * K, 66 * K, fill=PB)
            c.pic(circ("q%d%d" % (ci, ri), cx, yc, 41), g.X(cx - 41), g.Y(yc - 41), 82 * K)
            tx(g, cx + 60, x1 - 75, yc, [(lab, 8.5, NAVY, F3)], LEFT)
            tx(g, x1 - 80, x1 - 22, yc, [(n, 13.5, PINK, F3), (" 건", 8, PINK, F3)], RIGHT)

    # ───────── 아래: 시스템 구성도 ─────────
    g = c.grp(632, 1065)
    c.rrect(g.X(40), g.Y(634), 1923 * K, 431 * K, adj=0.03, fill=c.rgb(680, 900))
    fb = c.s.shapes.build_freeform(Inches(g.X(40)), Inches(g.Y(634)))
    fb.add_line_segments([(Inches(g.X(378)), Inches(g.Y(634))), (Inches(g.X(362)), Inches(g.Y(690))),
                          (Inches(g.X(40)), Inches(g.Y(690)))], close=True)
    tab = fb.convert_to_shape(); tab.fill.solid(); tab.fill.fore_color.rgb = HB
    tab.line.fill.background(); tab.shadow.inherit = False; tab.name = "시안 탭"
    c.pic(c.crop("h3", 68, 643, 117, 685, cut=(130, 662)), g.X(68), g.Y(643), 49 * K)
    tx(g, 147, 370, 662, [("시스템 구성도", 12, WHITE, F3)], LEFT)

    def card(x0, x1, y0, yh, y1, head):
        c.rrect(g.X(x0 + 2), g.Y(y1 - 10), (x1 - x0 - 4) * K, 26 * K, adj=0.5, fill=hexrgb("6FA8F7"))
        c.rrect(g.X(x0), g.Y(y0), (x1 - x0) * K, (y1 - y0) * K, adj=0.06, fill=head)
        c.rrect(g.X(x0 + 4), g.Y(yh), (x1 - x0 - 8) * K, (y1 - yh - 4) * K, adj=0.05, fill=WHITE)

    # 사용자 그룹
    card(65, 607, 712, 768, 1030, c.rgb(150, 725))
    c.pic(circ("ug", 260, 740, 27), g.X(233), g.Y(713), 54 * K)
    tx(g, 308, 560, 740, [("사용자 그룹", 11.5, hexrgb("2456B8"), F3)], LEFT)
    c.pic(c.crop("people", 100, 776, 565, 913, cut=(84, 800), cut_thresh=30), g.X(100), g.Y(776), 465 * K)
    for (x0, x1), lab in zip(((100, 217), (222, 335), (338, 452), (456, 574)), ("시청", "구청", "읍면동", "보건소")):
        c.write(c.rrect(g.X(x0), g.Y(922), (x1 - x0) * K, 45 * K, adj=0.3, fill=c.rgb(110, 960), line=LN, lw=0.5),
                [[(lab, 9, NAVY, F3)]])
    tx(g, 69, 603, 996, [("181", 13.5, NUM, F3), ("개 부서   ", 9.5, NUM, F3), ("5,100", 13.5, NUM, F3), ("명 이상", 9.5, NUM, F3)])

    AR = c.rgb(655, 862)
    for x in (617, 1328):
        c.shape(MSO_SHAPE.RIGHT_ARROW, g.X(x), g.Y(823), 56 * K, 80 * K, fill=AR, adj=[0.5, 0.6])

    # 행정포털서비스
    card(683, 1318, 708, 785, 1044, c.rgb(720, 760))
    c.pic(c.crop("bld", 775, 628, 1240, 708, cut=(765, 650)), g.X(775), g.Y(628), 465 * K)
    c.write(c.rect(g.X(917), g.Y(658), 143 * K, 50 * K, fill=WHITE), [[("굿모닝", 11, NUM, F3)]])
    tx(g, 683, 1318, 757, [("행정포털서비스 (굿모닝)", 12.5, WHITE, F3)])
    TB = c.rgb(900, 815)
    tiles = [(712, 803, "행정포털 메인", "6"), (1010, 803, "정보광장", "27"), (712, 917, "공통업무", "59"), (1010, 917, "개별업무", "38")]
    for i, (x, y, lab, n) in enumerate(tiles):
        c.rrect(g.X(x), g.Y(y), 281 * K, 98 * K, adj=0.14, fill=TB, line=hexrgb("B7D0F5"), lw=0.75)
        c.pic(c.crop("t%d" % i, x + 31, y + 14, x + 97, y + 80, cut=(x + 110, y + 50)), g.X(x + 31), g.Y(y + 14), 66 * K)
        tx(g, x + 118, x + 278, y + 30, [(lab, 9, NAVY, F3)], LEFT)
        tx(g, x + 118, x + 278, y + 66, [(n, 13, NUM, F3), ("종", 8.5, NUM, F3)], LEFT)

    # 시스템 연계
    card(1394, 1938, 711, 770, 1032, c.rgb(1430, 745))
    c.pic(circ("lk", 1559, 740, 26), g.X(1533), g.Y(714), 52 * K)
    tx(g, 1602, 1930, 740, [("시스템 연계", 11.5, WHITE, F3), ("(31개)", 9, WHITE, F3)], LEFT)
    SB = c.rgb(1420, 880)
    sysr = [(787, 903, 828, 880, [(1412, 1563, "새올행정"), (1576, 1750, "차세대지방재정"), (1764, 1920, "온나라")]),
            (917, 1026, 958, 1006, [(1412, 1546, "도시계획정보"), (1558, 1686, "기록관리"), (1698, 1826, "교통법규위반")])]
    for ri, (y0, y1, yi, yt, items) in enumerate(sysr):
        for ii, (x0, x1, lab) in enumerate(items):
            c.rrect(g.X(x0), g.Y(y0), (x1 - x0) * K, (y1 - y0) * K, adj=0.16, fill=SB, line=LN, lw=0.5)
            cx = (x0 + x1) / 2.0
            c.pic(circ("s%d%d" % (ri, ii), int(cx), yi, 35), g.X(int(cx) - 35), g.Y(yi - 35), 70 * K)
            tx(g, x0, x1, yt, [(lab, 7.5, NAVY, F3)], h=0.26)
    c.rrect(g.X(1839), g.Y(917), 81 * K, 109 * K, adj=0.2, fill=SB, line=LN, lw=0.5)
    for x in (1864, 1877, 1890):
        c.oval(g.X(x - 3.5), g.Y(953.5), 7 * K, 7 * K, fill=hexrgb("3B82F0"))
    tx(g, 1839, 1920, 992, [("등", 8, NAVY, F3)], h=0.26)
