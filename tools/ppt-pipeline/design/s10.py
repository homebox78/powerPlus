"""10쪽 — 수행 전략 개요 (시안 5번)."""
from lib import *
from PIL import Image as _Im, ImageDraw as _Dr


def _clear(path, box):
    """오린 그림에서 box(px, 그림 좌표 2000 기준 비율 아님: 실제 픽셀) 를 투명하게."""
    im = _Im.open(path).convert("RGBA")
    im.paste((255, 255, 255, 0), box)
    im.save(path)


def build(c):
    title_font = F3
    for sh in c.s.shapes:
        if sh.name == "직사각형 117":
            for r in sh.text_frame.paragraphs[0].runs:
                ea = r._r.find(".//" + qn("a:ea"))
                title_font = (ea.get("typeface") if ea is not None else None) or r.font.name or F3
    c.keep_only("TextBox 76")
    c.background(1000, 240)
    c.vmap(250, 1.6, 1030, 7.1)
    Z = c.Z
    INK = c.rgb(880, 405)          # 본문 짙은 글
    GREY = hexrgb("5B6B86")
    LN = c.rgb(40, 600)            # 패널 테두리
    LN2 = hexrgb("B9D3F5")

    # ── 제목 ──
    ty = 1.22
    c.text(0, ty - 0.3, SLIDE_W, 0.6, [[("최적의 전략으로 사업의 ", 23, NAVY, title_font),
                                        ("성공적 수행 및 목표 달성", 23, c.rgb(1010, 190), title_font)]])
    c.line(70 * K, ty, 330 * K, ty, c.rgb(250, 181), 1.0)
    c.line(1668 * K, ty, 1935 * K, ty, c.rgb(1750, 182), 1.0)

    T0, B0 = c.cy(262), c.cy(1028)     # 패널 위·아래
    HH = 86 * K                         # 머리 높이

    # ══ 왼쪽: 고객의 고민 ══
    c.rrect(40 * K, T0 + HH + 0.04, 517 * K, B0 - T0 - HH - 0.04, adj=0.03, fill=c.rgb(200, 380), line=LN2, lw=0.75)
    c.rrect(40 * K, T0, 517 * K, HH, adj=0.18, fill=c.rgb(300, 275))
    c.pic(c.crop("person", 74, 270, 142, 344, cut=(150, 300)), 74 * K, T0 + HH / 2 - 37 * K, 68 * K)
    c.text(165 * K, T0, 380 * K, HH, [[("고객의 고민, 걱정...", 15, NAVY, F3)]], LEFT)

    hexes = [(255, 380, 378, 520, 317, 450, 395, "안정성 확보", 481),
             (292, 508, 415, 648, 354, 578, 430, "불편 해소", 608),
             (294, 652, 418, 792, 356, 722, 430, "변화 대응", 755),
             (264, 800, 392, 946, 328, 872, 412, "신뢰 확보", 904)]
    polys = []
    for i, (x0, y0, x1, y1, cx, cyy, tx, lab, ly) in enumerate(hexes):
        g = c.grp(cyy, cyy)
        R = (y1 - y0) / 2.0 - 3; hw = (x1 - x0) / 2.0 - 3
        poly = [(cx, cyy - R), (cx + hw, cyy - R / 2), (cx + hw, cyy + R / 2), (cx, cyy + R), (cx - hw, cyy + R / 2), (cx - hw, cyy - R / 2)]
        polys.append([(cx + (px - cx) * 1.12, cyy + (py - cyy) * 1.12) for px, py in poly])
        hp = c.crop("hex%d" % i, x0, y0, x1, y1)
        im = _Im.open(hp).convert("RGBA"); mk = _Im.new("L", im.size, 0)
        _Dr.Draw(mk).polygon([((px - x0) * Z, (py - y0) * Z) for px, py in poly], fill=255)
        im.putalpha(mk); im.save(hp)
        c.pic(hp, g.X(x0), g.Y(y0), (x1 - x0) * K)
        c.text(g.X(tx), g.Y(cyy - 28), 140 * K, 46 * K, [[(lab, 10, INK, F3)]], LEFT)
        c.line(g.X(tx), g.Y(ly), g.X(540), g.Y(ly), LN2, 0.75)
        c.oval(g.X(tx) - 0.025, g.Y(ly) - 0.025, 0.05, 0.05, fill=c.rgb(398, 481))
    p = c.crop("man", 10, 425, 292, 1012, cut=(240, 600), cut_thresh=42)
    im = _Im.open(p).convert("RGBA"); d = _Dr.Draw(im)
    for poly in polys:
        d.polygon([((px - 10) * Z, (py - 425) * Z) for px, py in poly], fill=(255, 255, 255, 0))
    d.rectangle((int(200 * Z), 0, im.size[0], int(95 * Z)), fill=(255, 255, 255, 0))
    im.save(p)
    man = c.pic(p, 10 * K, 0, 282 * K)
    man.top = Inches(B0 - 0.01) - man.height

    # ══ 화살표 ══
    AR = c.rgb(600, 600)
    am = (T0 + B0) / 2 + 0.1
    for x in (566, 1245):
        c.shape(MSO_SHAPE.RIGHT_ARROW, x * K, am - 0.45, 66 * K, 0.9, fill=AR, adj=[0.5, 0.6])

    # ══ 가운데: 핵심 성공 요소 ══
    pod = c.pic(c.crop("podium", 590, 948, 1280, 1046, cut=(585, 1000), cut_thresh=30), 590 * K, 0, 690 * K)
    pod.top = Inches(B0 + 0.12) - pod.height
    c.rrect(640 * K, T0 + HH / 2, 592 * K, B0 - 0.42 - T0 - HH / 2, adj=0.05, fill=c.rgb(650, 600), line=c.rgb(664, 600), lw=1.0)
    c.pill(630 * K, T0, 610 * K, HH, fill=c.rgb(900, 330))
    c.pic(c.crop("target", 672, 272, 734, 332, cut=(640, 300), cut_thresh=70), 672 * K, T0 + HH / 2 - 30 * K, 62 * K)
    c.text(745 * K, T0, 480 * K, HH, [[("핵심 성공 요소 - 5대 CSF", 14.5, WHITE, F3)]], LEFT)

    rows = [(417, "1", "시스템 목적 사상", "완벽 이해", 378, 458),
            (529, "2", "구축/운영 수행 경험", "업무지식 기술역량", 490, 570),
            (648, "3", "정확한 문제진단", "최적 해결방안", 608, 688),
            (768, "4", "선제적 대응", "능동적 변화관리", 728, 808),
            (888, "5", "원활한 의사소통", "신뢰관계", 848, 928)]
    r0, r1 = c.cy(417) + 0.02, B0 - 1.0
    for i, (y, n, a, b, iy0, iy1) in enumerate(rows):
        m = r0 + (r1 - r0) * i / 4.0
        Y = lambda v, m=m, y=y: m + (v - y) * K
        c.pill(668 * K, Y(y - 46), 534 * K, 92 * K, fill=WHITE, line=LN2, lw=0.75)
        nc = c.rgb(700, y) if i < 4 else c.rgb(700, 888)
        c.write(c.oval(680 * K, Y(y - 39), 78 * K, 78 * K, fill=nc), [[(n, 17, WHITE, F3)]])
        c.pic(c.crop("ric%d" % i, 776, iy0, 852, iy1, cut=(860, y), cut_thresh=18), 776 * K, Y(iy0), 76 * K)
        c.text(873 * K, Y(y - 34), 320 * K, 36 * K, [[(a, 10, INK, F3)]], LEFT)
        c.text(873 * K, Y(y + 4), 320 * K, 32 * K, [[(b, 8.5, GREY, F2)]], LEFT)

    # ══ 오른쪽: 3대 추진 전략 ══
    c.rrect(1310 * K, T0 + HH / 2, 657 * K, B0 - T0 - HH / 2, adj=0.03, fill=c.rgb(1316, 700), line=LN2, lw=0.75)
    c.rrect(1310 * K, T0, 650 * K, HH, adj=0.3, fill=c.rgb(1500, 330))
    c.pic(c.crop("tree", 1340, 270, 1408, 336, cut=(1320, 300), cut_thresh=70), 1340 * K, T0 + HH / 2 - 33 * K, 68 * K)
    c.text(1435 * K, T0, 500 * K, HH, [[("3대 추진 전략 및 5개 ACT", 13.5, WHITE, F3)]], LEFT)

    cards = [(372, 580, (1338, 385, 1525, 562), "전략 1", "안정성 확보", [("ACT.1", "핵심인력 투입"), ("ACT.2", "장애 Zero 유지")]),
             (598, 815, (1338, 612, 1525, 802), "전략 2", "관리체계 확립", [("ACT.3", "기능개선"), ("ACT.4", "법제도 모니터링")]),
             (835, 1010, (1345, 845, 1515, 1006), "전략 3", "변화 실천", [("ACT.5", "환경변화 대응")])]
    CARD = hexrgb("DCEEFE")
    TAG = c.rgb(1550, 390)
    ACT = c.rgb(1650, 468)
    # 카드 세 장을 패널 안에 고르게(세로로 늘려) 배치
    top, bot, gap = T0 + HH + 0.12, B0 - 0.12, 0.12
    hs = [208.0, 217.0, 175.0]; unit = (bot - top - 2 * gap) / sum(hs)
    t = top
    for i, (y0, y1, pb, tag, ttl, acts) in enumerate(cards):
        h = hs[i] * unit
        c.rrect(1327 * K, t, 628 * K, h, adj=0.08, fill=CARD)
        mid = t + h / 2; ym = (y0 + y1) / 2.0
        Y = lambda v: mid + (v - ym) * K
        c.pic(c.crop("cpic%d" % i, *pb, cut=(1345, 400), cut_thresh=45), pb[0] * K, Y(pb[1]), (pb[2] - pb[0]) * K)
        hy = y0 + 31
        b = c.shape(MSO_SHAPE.ROUND_2_DIAG_RECTANGLE, 1537 * K, Y(hy - 22), 108 * K, 44 * K, fill=TAG, adj=[0.3, 0.0])
        c.write(b, [[(tag, 8.5, WHITE, F3)]])
        c.text(1670 * K, Y(hy - 24), 280 * K, 48 * K, [[(ttl, 11, NAVY, F3)]], LEFT)
        for j, (an, at) in enumerate(acts):
            ay = y0 + 95 + j * 68 if i < 2 else y0 + 114
            c.pill(1540 * K, Y(ay - 30), 402 * K, 60 * K, fill=WHITE)
            c.write(c.pill(1557 * K, Y(ay - 21), 106 * K, 42 * K, fill=ACT), [[(an, 8, WHITE, F3)]])
            c.text(1686 * K, Y(ay - 24), 250 * K, 48 * K, [[(at, 8.5, INK, F2)]], LEFT)
        t += h + gap
