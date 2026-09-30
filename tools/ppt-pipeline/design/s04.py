"""4쪽 — 업무지원포털시스템의 구성 (시안 1번). 다른 쪽 작업의 본보기."""
from lib import *


def build(c):
    # 기존 본문(그룹·하단 선화 띠·제목)을 지우고 머리말 글만 남긴다
    title_font = F3
    for sh in c.s.shapes:
        if sh.name == "직사각형 18":
            for r in sh.text_frame.paragraphs[0].runs:
                ea = r._r.find(".//" + qn("a:ea"))
                title_font = (ea.get("typeface") if ea is not None else None) or r.font.name or F3
    c.remove("그룹 90", "그림 89", "직사각형 18")

    # 바탕 + 하단 도시 풍경(맨 뒤)
    city = c.pic(c.crop("city", 0, 884, 2000, 1125, fade_top=70), 0, 0, SLIDE_W)
    city.top = Inches(SLIDE_H) - city.height
    c.to_back(city)
    c.background()

    # 제목
    c.text(0, c.cy(215) - 0.3, SLIDE_W, 0.6, [[("청주시 ", 27, NAVY, title_font), ("업무지원포털시스템", 27, BLUE, title_font)]])

    # 노트북 덩어리
    g = c.grp(280, 870)
    c.pic(c.crop("laptop", 40, 280, 925, 872), g.X(40), g.Y(280), 885 * K)
    c.rect(g.X(143), g.Y(312), 687 * K, 443 * K, fill=c.rgb(700, 440))
    c.rrect(g.X(165), g.Y(405), 645 * K, 340 * K, adj=0.08, fill=c.rgb(500, 470))
    c.write(c.pill(g.X(343), g.Y(328), 310 * K, 67 * K, fill=c.rgb(360, 362)), [[("핵심 시스템", 16, WHITE, F3)]])
    for sx, dx in ((300, 1), (697, -1)):
        for dy in (-14, 0, 14):
            c.line(g.X(sx), g.Y(362 + dy * 1.4), g.X(sx + 30 * dx), g.Y(362 + dy * 0.6), PINK, 1.5)
    c.text(g.X(165), g.Y(415), 645 * K, 56 * K, [[("행정포털", 16.5, NAVY, F3), ("(굿모닝)", 16.5, NAVY, F2)]])
    c.pic(c.crop("woman", 165, 488, 562, 747), g.X(165), g.Y(488), 397 * K)
    c.rrect(g.X(580), g.Y(493), 220 * K, 247 * K, adj=0.1, fill=c.rgb(590, 600), line=c.rgb(580, 600))
    c.line(g.X(600), g.Y(620), g.X(782), g.Y(620), c.rgb(580, 600), 0.75)
    for iy, lab, big, small in ((527, "분야", "5", "개 분야"), (645, "업무", "227", "종")):
        c.pic(c.crop("ico%d" % iy, 601, iy - 4, 650, iy + 50), g.X(601), g.Y(iy - 4), 49 * K)
        c.text(g.X(668), g.Y(iy - 6), 120 * K, 28 * K, [[(lab, 8, NAVY, F2)]], LEFT)
        c.text(g.X(668), g.Y(iy + 24), 125 * K, 60 * K, [[(big, 18, BLUE, F3), (small, 10, BLUE, F3)]], LEFT)

    # 가운데 화살표
    g = c.grp(462, 612)
    b = c.shape(MSO_SHAPE.LEFT_RIGHT_ARROW, g.X(857), g.Y(462), 251 * K, 150 * K, fill=c.rgb(980, 500), adj=[0.62, 0.38])
    c.write(b, [[("시스템 연계", 10, WHITE, F3)], [("공동 이용", 9.5, WHITE, F2)]])

    # 사용자 조직
    g = c.grp(305, 820)
    LN = hexrgb("8DB8F2")
    c.rrect(g.X(1120), g.Y(305), 835 * K, 515 * K, adj=0.04, line=LN, lw=1.0, dash=True)
    c.pill(g.X(1210), g.Y(347), 660 * K, 86 * K, fill=c.rgb(1240, 390))
    c.text(g.X(1358), g.Y(347), 500 * K, 86 * K, [[("청주시 공무원 ", 13, WHITE, F3), ("5,000명", 18, WHITE, F3), (" 대상", 13, WHITE, F3)]], LEFT)
    c.pic(c.crop("people", 1262, 356, 1345, 420), g.X(1262), g.Y(356), 83 * K)
    c.text(g.X(1120), g.Y(452), 835 * K, 56 * K, [[("사용자 조직 구성", 15, NAVY, F3)]])
    xs = [1146, 1308, 1470, 1632, 1794]; TW = 146
    c.line(g.X(xs[0] + TW / 2), g.Y(533), g.X(xs[-1] + TW / 2), g.Y(533), LN, 0.75)
    for x, lab in zip(xs, ["시본청", "4개구청", "43개읍면동", "16개도서관", "사업소"]):
        c.line(g.X(x + TW / 2), g.Y(533), g.X(x + TW / 2), g.Y(567), LN, 0.75)
        c.pic(c.crop("tile%d" % x, x, 566, x + TW, 712), g.X(x), g.Y(566), TW * K)
        c.write(c.pill(g.X(x + 5), g.Y(716), (TW - 10) * K, 46 * K, fill=c.rgb(1160, 738)), [[(lab, 8, NAVY, F3)]])
