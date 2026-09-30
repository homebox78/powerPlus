"""8쪽 — 사업의 특징 및 고려사항 (시안 4번)."""
from lib import *
from PIL import Image as _Image


def _grad(b, stops, ang=0):
    """도형 채움을 그라데이션으로. stops = [(위치 0~100, RGBColor, 불투명도 0~1), …]"""
    spPr = b._element.spPr
    old = spPr.find(qn("a:solidFill"))
    g = etree.Element(qn("a:gradFill")); g.set("rotWithShape", "1")
    lst = etree.SubElement(g, qn("a:gsLst"))
    for pos, col, al in stops:
        gs = etree.SubElement(lst, qn("a:gs")); gs.set("pos", str(int(pos * 1000)))
        cl = etree.SubElement(gs, qn("a:srgbClr")); cl.set("val", str(col))
        if al < 1:
            a = etree.SubElement(cl, qn("a:alpha")); a.set("val", str(int(al * 100000)))
    lin = etree.SubElement(g, qn("a:lin")); lin.set("ang", str(int(ang * 60000))); lin.set("scaled", "0")
    spPr.replace(old, g)


def _erase_si(path, Z, ox, oy):
    """작업복 등판의 'SI' 흰 글자를 옷 색으로 덮는다(시안의 엉뚱한 표기)."""
    im = _Image.open(path).convert("RGB"); px = im.load()
    x0, y0, x1, y1 = [int(v * Z) for v in (140 - ox, 645 - oy, 212 - ox, 700 - oy)]
    hit = set()
    for y in range(y0, y1):
        for x in range(x0, x1):
            r, g, b = px[x, y]
            if r > 110 and g > 125:          # 흰 글자와 번진 가장자리
                hit.add((x, y))
    grow = set()
    for (x, y) in hit:
        for dx in range(-3, 4):
            for dy in range(-3, 4):
                grow.add((x + dx, y + dy))
    for (x, y) in sorted(grow):
        # 같은 줄에서 글자 밖 가장 가까운 옷 색
        for d in range(1, 120):
            for xx in (x - d, x + d):
                if (xx, y) not in grow and 0 <= xx < im.size[0]:
                    r, g, b = px[xx, y]
                    if r < 110:
                        px[x, y] = (r, g, b); break
            else:
                continue
            break
    im = im.convert("RGBA")
    im.save(path)


def _ink(c, x0, y0, x1, y1):
    """상자 안에서 가장 진한(글자) 색."""
    ps = []
    for y in range(int(y0 * c.Z), int(y1 * c.Z), 2):
        for x in range(int(x0 * c.Z), int(x1 * c.Z), 2):
            ps.append(c.D.getpixel((x, y)))
    ps.sort(key=sum); ps = ps[:max(1, len(ps) // 5)]
    best = tuple(sorted(p[i] for p in ps)[len(ps) // 2] for i in range(3))
    return RGBColor(*best)


def _clear(path, box, fill):
    im = _Image.open(path).convert("RGBA"); px = im.load()
    for y in range(box[1], min(box[3], im.size[1])):
        for x in range(box[0], min(box[2], im.size[0])):
            px[x, y] = fill
    im.save(path)


ROWS = [
    (288, ["안정성", "확보"], (858, 288, 930, 364),
     ["시스템 간 연계를 통한", "정보의 공동이용까지 포함"], "시스템 연계 아키텍처, 데이터 품질, 보안·안정성 강화"),
    (491, ["불편 해소"], (842, 494, 945, 566),
     ["특성이 다른 사용자 층의", "요구사항 해결"], "사용자 경험(UX), 맞춤형 기능, 접근성 향상"),
    (694, ["변화 대응"], (852, 698, 936, 782),
     ["법/제도/업무/기술 등", "주변 환경 변화"], "유연한 시스템 구조, 확장성, 선제적 대응 체계"),
    (897, ["신뢰 확보"], (838, 908, 950, 990),
     ["장기계속계약 사용자와", "유기적 관계 형성"], "지속적인 서비스 품질, 소통 강화, 파트너십 운영"),
]


def build(c):
    title_font = F3
    for sh in c.s.shapes:
        if sh.name == "직사각형 51":
            for r in sh.text_frame.paragraphs[0].runs:
                ea = r._r.find(".//" + qn("a:ea"))
                title_font = (ea.get("typeface") if ea is not None else None) or r.font.name or F3
    c.keep_only("TextBox 41")
    c.vmap(130, 0.95, 1125, 7.55)
    c.background(1000, 262)

    DK = _ink(c, 330, 170, 760, 240); BL = _ink(c, 1310, 165, 1680, 240); B2 = _ink(c, 795, 170, 990, 240)
    # 제목
    c.text(0, c.cy(205) - 0.35, SLIDE_W, 0.7, [[
        ("본 사업에 대한 ", 27, DK, title_font), ("고객의 ", 27, B2, title_font),
        ("한결같은 ", 27, DK, title_font), ("고민과 걱정", 31, BL, title_font)]])

    # 왼쪽 서버·기술자 그림
    g = c.grp(215, 1080)
    p = c.crop("server", 0, 215, 748, 1080)
    _erase_si(p, c.Z, 0, 215)
    _clear(p, (int(290 * c.Z), 0, int(748 * c.Z), int(65 * c.Z)), tuple(c.rgb(1000, 262)) + (255,))
    c.pic(p, g.X(0), g.Y(215) + 0.15, 748 * K)

    navy = c.rgb(800, 380); edge = c.rgb(894, 275)
    TXT = _ink(c, 1210, 312, 1430, 332)
    for i, (top, lab, ico, worry, consider) in enumerate(ROWS):
        g = c.grp(top - 16, top + 174)
        d = top - 288
        # 화살 띠
        band = c.shape(MSO_SHAPE.PENTAGON, g.X(940), g.Y(top), 1022 * K, 157 * K, fill=WHITE, adj=0.43)
        _grad(band, [(0, c.rgb(1015, top + 62), 1), (53, c.rgb(1480, top + 62), 1),
                     (80, c.rgb(1750, top + 62), 1), (100, c.rgb(1925, top + 78), 1)])
        low = c.rect(g.X(940), g.Y(top + 92), 953 * K, 58 * K, fill=WHITE)
        _grad(low, [(0, c.rgb(1015, top + 140), 1), (84, c.rgb(1745, top + 140), 1),
                    (93, c.rgb(1830, top + 140), 1), (100, c.rgb(1888, top + 125), 1)])
        # 육각형
        hx = c.shape(MSO_SHAPE.HEXAGON, g.X(770), g.Y(top - 14), 250 * K, 186 * K, fill=navy, line=edge, lw=2.25,
                     adj=[0.30, 1.1547])
        ip = c.crop("ico%d" % i, *ico, cut=(ico[0] + 1, ico[1] + 1), cut_thresh=40)
        c.pic(ip, g.X(ico[0]), g.Y(ico[1]), (ico[2] - ico[0]) * K)
        if len(lab) == 2:
            c.text(g.X(770), g.Y(top + 78), 250 * K, 88 * K, [[(t, 12.5, WHITE, F3)] for t in lab], spacing=0.95)
        else:
            c.text(g.X(770), g.Y(top + 93), 250 * K, 50 * K, [[(lab[0], 12.5, WHITE, F3)]])
        # 고민
        pk = c.rgb(1060, top + 36)
        c.write(c.pill(g.X(1046), g.Y(top + 17), 100 * K, 38 * K, fill=pk), [[("고민", 9, WHITE, F3)]])
        wc = _ink(c, 1210, 922, 1450, 945) if i == 3 else TXT
        cc = pk if i == 3 else navy
        for a, b_ in ((-10, 0), (10, 0)):
            c.line(g.X(1172), g.Y(top + 36 + a), g.X(1181), g.Y(top + 36), cc, 1.5)
        c.text(g.X(1209), g.Y(top + 12), 600 * K, 78 * K,
               [[(t, 9, wc, F3 if i == 3 else F2)] for t in worry], LEFT, spacing=1.3)
        # 고려사항
        bp = c.crop("bulb%d" % i, 1038, top + 100, 1080, top + 146, cut=(1084, top + 120), cut_thresh=30)
        c.pic(bp, g.X(1038), g.Y(top + 100), 42 * K)
        c.text(g.X(1088), g.Y(top + 104), 95 * K, 38 * K, [[("고려사항", 8.5, c.rgb(1098, 411), F3)]], LEFT)
        for a in (-8, 8):
            c.line(g.X(1201), g.Y(top + 122 + a), g.X(1208), g.Y(top + 122), c.rgb(1098, 411), 0.75)
        c.text(g.X(1232), g.Y(top + 104), 640 * K, 38 * K, [[(consider, 8.5, TXT, F2)]], LEFT)
