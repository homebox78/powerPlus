"""16쪽 — 수행 및 지원방안 개요 (시안 10번)."""
from lib import *

HS = 1.1            # 머리 그림(인물·풍경) 확대 비율
HTOP = 0.87         # 본문 시작
CARD_TOP, CARD_BOT = 3.66, 7.12
PIC_Y1 = 1058       # 카드 그림(일러스트+받침) 아래 끝


def HY(y):
    return HTOP + (y - 118) * K * HS


def grad(b, stops, ang=5400000):
    """도형 채우기를 선형 그라데이션으로. stops=[(0~100, RGBColor), …]"""
    spPr = b._element.spPr
    sf = spPr.find(qn("a:solidFill"))
    g = etree.Element(qn("a:gradFill")); g.set("rotWithShape", "1")
    lst = etree.SubElement(g, qn("a:gsLst"))
    for pos, col in stops:
        gs = etree.SubElement(lst, qn("a:gs")); gs.set("pos", str(int(pos * 1000)))
        etree.SubElement(gs, qn("a:srgbClr")).set("val", str(col))
    lin = etree.SubElement(g, qn("a:lin")); lin.set("ang", str(ang)); lin.set("scaled", "0")
    spPr.replace(sf, g)


def fade(path, left=0, right=0, bottom=0, hole=None, soft=1):
    """오린 그림의 가장자리를 투명하게 흐린다(px, 그림 픽셀 기준)."""
    im = Image.open(path).convert("RGBA"); px = im.load(); w, h = im.size
    for y in range(h):
        for x in range(w):
            a = 1.0
            if left and x < left: a = min(a, x / float(left))
            if right and x >= w - right: a = min(a, (w - 1 - x) / float(right))
            if bottom and y >= h - bottom: a = min(a, (h - 1 - y) / float(bottom))
            if hole and x < hole[0] + soft and y < hole[1] + soft:   # 왼쪽 위 모서리 구멍(시안 제목 글자 자리)
                a = min(a, max(0.0, (x - hole[0]) / float(soft), (y - hole[1]) / float(soft)))
            if a < 1.0:
                r, g, b, al = px[x, y]; px[x, y] = (r, g, b, int(al * a))
    im.save(path)
    return path


def build(c):
    title_font = F3
    for sh in c.s.shapes:
        if sh.name == "직사각형 56":
            for r in sh.text_frame.paragraphs[0].runs:
                ea = r._r.find(".//" + qn("a:ea"))
                title_font = (ea.get("typeface") if ea is not None else None) or r.font.name or F3
    c.keep_only("TextBox 36")
    c.background(1000, 470)

    # ── 머리: 인물(왼쪽) · 인물+풍경(오른쪽) ──
    z = c.Z
    p = fade(c.crop("man", 0, 118, 330, 468), right=int(50 * z), bottom=int(12 * z))
    c.pic(p, 0, HTOP, 330 * K * HS)
    p = fade(c.crop("city", 1585, 118, 2000, 468), left=int(14 * z), bottom=int(12 * z),
             hole=(int(115 * z), int(125 * z)), soft=int(30 * z))
    RX = lambda x: SLIDE_W - (2000 - x) * K * HS
    c.pic(p, RX(1585), HTOP, 415 * K * HS)
    # 그림 속 달력 머리의 뭉개진 글 → 다시 씀
    c.write(c.rect(RX(1603), HY(362), 66 * K * HS, 24 * K * HS, fill=c.rgb(1635, 420)),
            [[("KPI", 7, WHITE, F3)]])

    DK = c.rgb(420, 200)
    c.text(0, HY(200) - 0.3, SLIDE_W, 0.6,
           [[("신속하게 반응하여 ", 23.5, DK, title_font), ("청주의 일상을 끊김 없이 ", 23.5, BLUE, title_font),
             ("지킵니다", 23.5, DK, title_font)]])
    c.text(0, HY(285) - 0.2, SLIDE_W, 0.4,
           [[("안정적 유지관리 체계 & 신속한 반응으로 ", 14.5, c.rgb(600, 290), F2),
             ("최고 수준 서비스 지속 지원", 14.5, c.rgb(1300, 290), F3)]])

    # 파란 알약
    PX0, PX1 = 445, 1530
    b = c.pill(PX0 * K, HY(338), (PX1 - PX0) * K, HY(430) - HY(338), fill=c.rgb(700, 360))
    grad(b, [(0, c.rgb(450, 360)), (100, c.rgb(1540, 400))], ang=0)
    ih = 66 * K * HS
    c.pic(c.crop("pillico", 503, 351, 574, 417, cut=(490, 384)), 530 * K, (HY(338) + HY(430)) / 2 - ih / 2, h=ih)
    c.text(615 * K, HY(338), (PX1 - 40 - 615) * K, HY(430) - HY(338),
           [[("환경변화와 요구에 신속하게 반응하여 안정적이고 지속적인 운영 지원", 11.5, WHITE, F3)]], LEFT)

    # ── 구분 라벨 ──
    LY = 3.33
    for (x0, x1, lx0, lx1, rx0, rx1, fx, lab) in (
            (262, 580, 78, 245, 597, 760, (420, 480), "사업수행방안"),
            (1187, 1503, 888, 1175, 1518, 1925, (1345, 480), "사업지원방안")):
        col = c.rgb(*fx)
        c.write(c.pill(x0 * K, LY - 0.145, (x1 - x0) * K, 0.29, fill=col), [[(lab, 11.5, WHITE, F3)]])
        for a, e, dot in ((lx0, lx1, lx1), (rx1, rx0, rx0)):
            c.line(a * K, LY, e * K, LY, col, 1.0)
            c.line(a * K, LY, a * K, LY + 0.09, col, 1.0)
            c.oval(dot * K - 0.035, LY - 0.035, 0.07, 0.07, fill=col)
            c.oval(a * K - 0.02, LY + 0.07, 0.04, 0.04, fill=col)

    # ── 카드 8장 ──
    cards = [
        (34, 262, ["꼼꼼한", "유지관리 체계"], ["검증된 방법론 기반", "서비스요청유형 특성 처리"]),
        (283, 533, ["전문적 수행", "조직 지원"], ["공공 행정정보시스템", "전문성 + 18년 경력", "책임자"]),
        (553, 800, ["흔들림 없는", "인수인계 유지"], ["현 사업자 공동운영", "비상주 운영지원"]),
        (822, 1058, ["시스템 연계(31개)", "유지관리"], ["대외기관 및 내부시스템", "연계 안정적 운영"]),
        (1077, 1305, ["안정적인 비상상황", "대응관리"], ["3단계 장애관리", "백업·복구"]),
        (1322, 1526, ["철저한 보안관리"], ["기밀성 · 무결성 ·", "가용성"]),
        (1543, 1750, ["신속한 환경변화", "대응"], ["정책·제도·기술 변화에", "유연한 대응"]),
        (1767, 1972, ["실질적인 사용자", "교육 관리"], ["맞춤형 교육으로", "시스템 활용도 극대화"]),
    ]
    EDGE = hexrgb("A6C9F8")
    TCOL = c.rgb(420, 200); DCOL = hexrgb("4A5B78")
    tops = {}
    for i, (x0, x1, tl, dl) in enumerate(cards):
        y0 = 797 if i == 1 else 785
        w = (x1 - x0) * K; ph = (PIC_Y1 - y0) * K; pt = CARD_BOT - ph
        tops[i] = (pt, y0)
        body = c.rgb(x0 + 14, y0 + 2)
        b = c.shape(MSO_SHAPE.ROUND_2_SAME_RECTANGLE, x0 * K, CARD_TOP, w, pt - CARD_TOP + 0.04,
                    fill=body, line=EDGE, lw=0.75, adj=[0.09, 0])
        grad(b, [(0, c.rgb(x0 + 14, 548)), (30, c.rgb(x0 + 14, 625)), (100, body)])
        c.pic(c.crop("card%d" % i, x0, y0, x1, PIC_Y1), x0 * K, pt, w)
        cx = (x0 + x1) / 2.0 * K
        c.write(c.oval(cx - 0.17, CARD_TOP + 0.17, 0.34, 0.34, fill=c.rgb(147, 560) if i < 3 else c.rgb(943, 560)),
                [[(str(i + 1), 14, WHITE, F3)]])
        c.text(x0 * K, CARD_TOP + 0.62, w, 0.5, [[(t, 9.5, TCOL, F3)] for t in tl], spacing=1.1)
        c.text(x0 * K, CARD_TOP + 1.2, w, 0.62, [[(t, 7, DCOL, F2)] for t in dl], anchor="top", spacing=1.3)

    def CY(i, y):
        pt, y0 = tops[i]
        return pt + (y - y0) * K

    # 그림 속 글 → 바탕을 덮고 다시 씀
    c.write(c.rrect(378 * K, CY(1, 934), 70 * K, 34 * K, adj=0.2, fill=c.rgb(412, 926)), [[("18년", 9.5, WHITE, F3)]])
    c.write(c.pill(977 * K, CY(3, 803), 75 * K, 40 * K, fill=c.rgb(985, 822)), [[("31개", 9, WHITE, F3)]])
    c.write(c.pill(1203 * K, CY(4, 803), 77 * K, 40 * K, fill=c.rgb(1210, 822)), [[("3단계", 9, WHITE, F3)]])
    c.rect(1338 * K, CY(5, 973), 172 * K, 24 * K, fill=c.rgb(1345, 968))
    for x, t in ((1362, "기밀성"), (1424, "무결성"), (1486, "가용성")):
        c.text((x - 32) * K, CY(5, 972), 64 * K, 27 * K, [[(t, 7, TCOL, F2)]])
