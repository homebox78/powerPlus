"""22쪽 — 수행 조직의 구성 및 운영 (시안 16번).

지도는 시안 것을 쓰지 않는다(구 이름·모양이 실제와 다름). 원래 장표의 지도 그림·구 이름·
인력 표시(아이콘 묶음)를 남겨 시안의 가운데 칸 자리로 줄여 옮긴다.
"""
from lib import *

# 원래 지도 묶음(지도+구 이름+인력 표시)의 범위(inch)와 옮길 자리
MAP_SRC = (3.06, 3.10)        # 원래 묶음의 왼쪽 위
MAP_S = 0.76                  # 배율
MAP_DST = (3.30, 2.62)        # 옮긴 뒤 왼쪽 위


def build(c):
    s = c.s
    c.vmap(128, 1.0, 1075, 7.1)

    # ── 시안에서 색 읽기 ──
    def ink(x0, y0, x1, y1):
        """영역에서 가장 짙고 선명한 점(글자색)."""
        best, bv = None, -1
        for y in range(int(y0), int(y1), 1):
            for x in range(int(x0), int(x1), 1):
                p = c.D.getpixel((int(x * c.Z), int(y * c.Z)))
                v = (max(p) - min(p)) + (255 - sum(p) / 3.0) * 0.6
                if v > bv: best, bv = p, v
        return RGBColor(*best)

    # ── 상자 좌표: G=덩어리(배율 유지), P=칸(세로로 늘림) ──
    def G(g, x0, y0, x1, y1): return (g.X(x0), g.Y(y0), (x1 - x0) * K, (y1 - y0) * K)
    def P(x0, y0, x1, y1): return (x0 * K, c.cy(y0), (x1 - x0) * K, c.cy(y1) - c.cy(y0))

    # ── 남길 것 고르기 ──
    title_font = F3
    keep = []
    for sh in list(s.shapes):
        n = sh.name
        if n == "직사각형 196":
            for r in sh.text_frame.paragraphs[0].runs:
                ea = r._r.find(".//" + qn("a:ea"))
                title_font = (ea.get("typeface") if ea is not None else None) or r.font.name or F3
        is_map = (n == "MAP_cheongju" or n.startswith("GU_") or n in ("그룹 2", "그룹 5", "그룹 159")
                  or (sh.has_text_frame and sh.text_frame.text.strip() == "세종시"))
        if is_map: keep.append(sh)
        elif n != "TextBox 113":
            c.tree.remove(sh._element)
    # PM 글자(묶음 안)는 말풍선 알약이 대신한다
    for sh in keep:
        if sh.name == "그룹 2":
            for ch in list(sh.shapes):
                if ch.has_text_frame and ch.text_frame.text.strip() == "PM":
                    ch._element.getparent().remove(ch._element)

    NV = ink(1225, 360, 1500, 390)          # 남색 글
    BL = c.rgb(1200, 300)                   # 알약 파랑
    PK = c.rgb(1600, 310)                   # 분홍
    LN = hexrgb("CFE0F7")
    card = c.rgb(1500, 440)                 # 줄 카드 바탕
    panel = c.rgb(300, 600)

    # ── 바탕·칸(지도보다 뒤) ──
    bgc = c.rgb(1000, 236)   # 쪽 번호(오른쪽 아래)는 가리지 않게 구석을 비운다
    for b in (c.rect(0, 0.87, SLIDE_W, 7.12 - 0.87, fill=bgc, name="시안 바탕"), c.rect(0, 7.12, 9.3, 0.38, fill=bgc, name="시안 바탕2")):
        c.to_back(b)
    c.rrect(*P(602, 245, 1100, 888), adj=0.04, fill=c.rgb(1080, 800))
    # 남긴 지도 묶음을 방금 그린 칸 위로 올리고 줄여 옮긴다
    for sh in keep:
        c.tree.remove(sh._element); c.tree.append(sh._element)
        l, t, w, h = sh.left / 914400.0, sh.top / 914400.0, sh.width / 914400.0, sh.height / 914400.0
        cx = MAP_DST[0] + (l + w / 2 - MAP_SRC[0]) * MAP_S
        cyy = MAP_DST[1] + (t + h / 2 - MAP_SRC[1]) * MAP_S
        if sh.shape_type in (6, 13):        # 묶음·그림은 줄인다
            w, h = w * MAP_S, h * MAP_S
            sh.width, sh.height = Inches(w), Inches(h)
        if sh.has_text_frame and sh.text_frame.text.strip() == "세종시":   # 글자는 안 줄어 아이콘과 겹친다 → 아이콘 위로
            cx, cyy = MAP_DST[0] + (3.84 - MAP_SRC[0]) * MAP_S, MAP_DST[1] + (5.32 - MAP_SRC[1]) * MAP_S - 0.11
        sh.left, sh.top = Inches(cx - w / 2), Inches(cyy - h / 2)

    # ── 제목 띠 ──
    g = c.grp(128, 225)
    c.rrect(*G(g, 28, 128, 1972, 225), adj=0.3, fill=c.rgb(1800, 176))
    c.pic(c.crop("target", 62, 130, 168, 224, cut=(1800, 176)), g.X(62), g.Y(130), 106 * K)
    c.text(g.X(200), g.Y(128), 1500 * K, 97 * K,
           [[("기존 인력 및 분야별 전문가 투입으로 업무 연속성 및 문제 해결력 보장", 18, ink(205, 150, 700, 200), title_font)]], LEFT)

    # ── 왼쪽 위: 두 줄 요약 ──
    c.rrect(*P(32, 248, 592, 440), adj=0.06, fill=panel, line=LN, lw=0.75)
    g = c.grp(248, 440)
    for i, y in enumerate((270, 372)):
        c.pic(c.crop("chk%d" % i, 50, y, 95, y + 45, cut=(300, 420)), g.X(50), g.Y(y), 45 * K)
    c.text(g.X(108), g.Y(262), 470 * K, 96 * K,
           [[("청주시 굿모닝시스템 특성을 반영한", 10.5, NV, F3)], [("조직 구성", 10.5, NV, F3)]], LEFT, spacing=1.15)
    c.text(g.X(108), g.Y(368), 480 * K, 52 * K, [[("지역/전문가 중심의 즉각 대응체계 구축", 10.5, NV, F3)]], LEFT)

    # ── 왼쪽 아래: 본사 지원 ──
    c.rrect(*P(32, 470, 585, 882), adj=0.04, fill=panel, line=LN, lw=0.75)
    g = c.grp(453, 517)
    c.pill(*G(g, 32, 453, 292, 517), fill=BL)
    c.pic(c.crop("hq", 58, 462, 108, 508, cut=(200, 462)), g.X(58), g.Y(462), 50 * K)
    c.text(g.X(120), g.Y(453), 160 * K, 64 * K, [[("본사 지원", 12, WHITE, F3)]], LEFT)

    g = c.grp(540, 692)
    tiles = [(57, 177, ["지역 지원"]), (185, 305, ["지원 관리"]), (313, 433, ["품질 보증"]), (441, 565, ["디자인 등", "분야별 전문가"])]
    tf = c.rgb(70, 680)
    for i, (x0, x1, lab) in enumerate(tiles):
        c.rrect(*G(g, x0, 540, x1, 692), adj=0.12, fill=tf)
        m = (x0 + x1) / 2.0
        c.pic(c.crop("hq%d" % i, m - 48, 543, m + 48, 620, cut=(70, 680)), g.X(m - 48), g.Y(543), 96 * K)
        c.text(g.X(x0), g.Y(625 if len(lab) > 1 else 622), (x1 - x0) * K, (60 if len(lab) > 1 else 36) * K,
               [[(t, 7, NV, F3)] for t in lab], spacing=1.1)

    g = c.grp(718, 858)
    c.rrect(*G(g, 57, 718, 565, 858), adj=0.15, fill=tf)
    c.pic(c.crop("badge", 60, 698, 268, 862, cut=(300, 845)), g.X(60), g.Y(698), 208 * K)
    c.write(c.oval(*G(g, 108, 720, 224, 836), fill=c.rgb(130, 800)), [[("100%", 14, WHITE, F3)]])
    c.text(g.X(280), g.Y(738), 270 * K, 44 * K, [[("행정정보화 경험", 10.5, NV, F3)]])
    c.text(g.X(280), g.Y(782), 270 * K, 58 * K, [[("100%", 21, ink(335, 790, 460, 830), F3)]])

    # ── 가운데: 인력 말풍선(그림은 시안, 지도·표시는 원래 것) ──
    def T(x, y):  # 원래 장표 좌표 → 옮긴 자리
        return (MAP_DST[0] + (x - MAP_SRC[0]) * MAP_S, MAP_DST[1] + (y - MAP_SRC[1]) * MAP_S)
    mapbg = (1080, 800)
    g = c.grp(250, 362)
    c.pic(c.crop("pm", 610, 250, 712, 362, cut=mapbg), g.X(610), g.Y(250), 102 * K)
    c.write(c.pill(*G(g, 698, 268, 850, 305), fill=BL), [[("PM", 10.5, WHITE, F3)]])
    c.text(g.X(698), g.Y(308), 152 * K, 32 * K, [[("(전담 관리)", 7, NV, F2)]])
    a = T(3.78, 4.20); c.line(g.X(705), g.Y(362), a[0], a[1], BL, 0.75, dash=True)

    g = c.grp(265, 415)
    c.pic(c.crop("lead", 998, 262, 1092, 350, cut=mapbg), g.X(998), g.Y(262), 94 * K)
    c.write(c.pill(*G(g, 960, 346, 1100, 384), fill=BL), [[("수행 책임", 8.5, WHITE, F3)]])
    c.text(g.X(960), g.Y(386), 140 * K, 30 * K, [[("(사업 총괄)", 7, NV, F2)]])
    a = T(5.44, 3.92); c.line(g.X(1005), g.Y(416), a[0], a[1], BL, 0.75, dash=True)

    g = c.grp(720, 860); g.t += 0.17; _X = g.X; g.X = lambda x: _X(x + 60)
    c.pic(c.crop("tech", 645, 720, 760, 858, cut=mapbg), g.X(645), g.Y(720), 115 * K)
    c.write(c.pill(*G(g, 757, 788, 945, 826), fill=BL), [[("기술지원 인력", 8, WHITE, F3)]])
    c.text(g.X(757), g.Y(828), 188 * K, 30 * K, [[("(기술·운영 지원)", 7, NV, F2)]])
    a = T(5.08, 4.84); c.line(g.X(700), g.Y(724), a[0], a[1], BL, 0.75, dash=True)

    # ── 오른쪽: 운영 ──
    g = c.grp(245, 323)
    c.pill(*G(g, 1125, 245, 1360, 323), fill=BL)
    c.pic(c.crop("gear", 1146, 256, 1202, 312, cut=(1300, 300)), g.X(1146), g.Y(256), 56 * K)
    c.text(g.X(1222), g.Y(245), 120 * K, 78 * K, [[("운영", 13.5, WHITE, F3)]], LEFT)
    c.pill(*G(g, 1537, 262, 1950, 320), fill=PK)
    c.pic(c.crop("goal", 1546, 268, 1592, 314, cut=(1600, 310)), g.X(1546), g.Y(268), 46 * K)
    c.text(g.X(1596), g.Y(262), 70 * K, 58 * K, [[("목표", 8.5, WHITE, F3)]])
    c.write(c.pill(*G(g, 1667, 266, 1946, 316), fill=WHITE), [[("업무공백 최소화", 11.5, PK, F3)]])

    c.rrect(*P(1125, 333, 1972, 908), adj=0.03, fill=panel, line=LN, lw=0.75)

    def head(y0, y1, name, box, label):
        g = c.grp(y0, y1)
        c.rrect(*G(g, 1143, y0, 1950, y1), adj=0.2, fill=card)
        c.pic(c.crop(name, *box, cut=(1700, (y0 + y1) / 2)), g.X(box[0]), g.Y(box[1]), (box[2] - box[0]) * K)
        c.text(g.X(1220), g.Y(y0), 600 * K, (y1 - y0) * K, [[(label, 11.5, NV, F3)]], LEFT)

    head(348, 397, "h1", (1148, 350, 1206, 396), "인력 변동 시 대처 방안")
    rows = ["주관기관 요구 기준 부합 인력 선정·투입", "상시 투입 가능한 전문 인력 Pool 구축",
            "결원·공백 발생 시 신속한 투입·철저한 인수인계", "주관기관 승인 후 15일 이상 인수인계·공동운영"]
    for i, (y0, tx) in enumerate(zip((411, 478, 545, 613), rows)):
        g = c.grp(y0, y0 + 56)
        c.rrect(*G(g, 1150, y0, 1947, y0 + 56), adj=0.3, fill=card)
        c.write(c.oval(*G(g, 1164, y0 + 7, 1206, y0 + 49), fill=BL), [[(str(i + 1), 9, WHITE, F3)]])
        c.text(g.X(1230), g.Y(y0), 700 * K, 56 * K, [[(tx, 9, NV, F2)]], LEFT)
    head(688, 738, "h2", (1150, 690, 1202, 738), "인력 변동 시 절차")

    g = c.grp(755, 892)
    steps = [(1153, 1270, ["변경사유", "발생"]), (1287, 1403, ["주관기관", "승인"]), (1420, 1537, ["인계인수"]),
             (1553, 1670, ["결과보고"]), (1687, 1805, ["승인 및 교체"]), (1822, 1943, ["기존 인력 철수"])]
    for i, (x0, x1, lab) in enumerate(steps):
        m = (x0 + x1) / 2.0
        c.rrect(*G(g, x0, 768, x1, 892), adj=0.12, fill=card)
        c.write(c.oval(*G(g, m - 16, 754, m + 16, 786), fill=BL, line=WHITE, lw=1.0), [[("%02d" % (i + 1), 7, WHITE, F3)]])
        c.pic(c.crop("st%d" % i, m - 34, 792, m + 34, 846, cut=(x0 + 8, 880)), g.X(m - 34), g.Y(792), 68 * K)
        two = len(lab) > 1
        c.text(g.X(x0), g.Y(845 if two else 850), (x1 - x0) * K, (46 if two else 36) * K,
               [[(t, 7, NV, F3)] for t in lab], spacing=1.0)
        if i < 5:
            tr = c.shape(MSO_SHAPE.ISOSCELES_TRIANGLE, g.X(x1 + 2), g.Y(813), 13 * K, 13 * K, fill=c.rgb(1277, 820))
            tr.rotation = 90

    # ── 아래 띠 ──
    g = c.grp(908, 1075)
    c.rrect(*G(g, 28, 922, 1972, 1075), adj=0.15, fill=c.rgb(600, 1060))
    c.pic(c.crop("land", 1272, 925, 1935, 1073, cut=(1290, 935)), g.X(1272), g.Y(925), 663 * K)
    c.write(c.rrect(*G(g, 1608, 940, 1698, 1012), adj=0.3, fill=BL),
            [[("청주", 8, WHITE, F3)], [("& 세종", 8, WHITE, F3)]], spacing=1.0)
    c.pic(c.crop("laptop", 435, 926, 762, 1066, cut=(600, 1060)), g.X(435), g.Y(926), 327 * K)
    for nm, x in (("b1", 42), ("b2", 848)):
        c.pic(c.crop(nm, x, 933, x + 102, 1035, cut=(600, 1060)), g.X(x), g.Y(933), 102 * K)
    c.text(g.X(158), g.Y(940), 290 * K, 50 * K, [[("업무지원포털", 11, NV, F3)]], LEFT)
    c.text(g.X(158), g.Y(988), 290 * K, 38 * K, [[("업무 / 컨텐츠 / 요소기술 경험", 8, NV, F2)]], LEFT)
    c.line(g.X(805), g.Y(938), g.X(805), g.Y(1045), NV, 0.75)
    c.text(g.X(965), g.Y(940), 310 * K, 50 * K, [[("유지관리 및 지원 인력", 11, NV, F3)]], LEFT)
    c.text(g.X(965), g.Y(988), 310 * K, 38 * K, [[("청주 및 세종 지역 거주", 8, NV, F2)]], LEFT)
