"""32쪽 — 관리 및 지원조직 (2차 시안 design_ppt2/s32.png).
증명사진(그림 62)과 표(표 53)는 원래 장표 것을 남겨 자리·색만 시안에 맞춘다.
월계관·아이콘 3개는 시안에서 오리고, 글·상자·선은 도형으로 다시 그린다. 글은 원래 장표 문구."""
from lib import *

KEY_FONT = "G마켓 산스 TTF Bold"
NAVY_T = hexrgb("0B2E6B")
BLUE_T = hexrgb("2070E8")
TXT = hexrgb("0A2A6B")
SUB = hexrgb("2F7FE8")
DARK = hexrgb("1D569F")
LIGHT = hexrgb("C9E5FD")
LIGHT_LN = hexrgb("A9D2FA")
CONN = hexrgb("8EC2F4")
SUMC = hexrgb("EC1C68")

# 세로: 시안 y290(카드 위) → 1.62in, y1078(아래 상자 끝) → 7.02in
Y0, IN0, V = 290.0, 1.62, (7.02 - 1.62) / (1078 - 290)


def Y(y): return IN0 + (y - Y0) * V
def H(h): return h * V
def X(x): return x * K


def picc(c, name, x0, y0, x1, y1, light_key=None, **kw):
    """오린 그림을 가로 배율 K 로, 세로는 중심만 맞춰 놓는다.
    light_key=R: 빨강 값이 R 이상인 옅은 바탕 픽셀을 투명하게(바탕 두 가지 색에 걸친 아이콘용)."""
    p = c.crop(name, x0, y0, x1, y1, **kw)
    if light_key is not None:
        from PIL import Image as _I
        im = _I.open(p).convert("RGBA"); px = im.load()
        for yy in range(im.size[1]):
            for xx in range(im.size[0]):
                r, g, b, a = px[xx, yy]
                if r >= light_key:
                    px[xx, yy] = (r, g, b, 0)
                elif r >= light_key - 40:
                    px[xx, yy] = (r, g, b, int(a * (light_key - r) / 40.0))
        im.save(p)
    w = (x1 - x0) * K; h = (y1 - y0) * K
    return c.pic(p, X(x0), Y((y0 + y1) / 2.0) - h / 2, w)


def _borders(cell, color, w_pt):
    tcPr = cell._tc.get_or_add_tcPr()
    for tag in ("a:lnL", "a:lnR", "a:lnT", "a:lnB"):
        old = tcPr.find(qn(tag))
        if old is not None: tcPr.remove(old)
    for i, tag in enumerate(("a:lnL", "a:lnR", "a:lnT", "a:lnB")):
        ln = etree.Element(qn(tag)); ln.set("w", str(int(w_pt * 12700)))
        sf = etree.SubElement(ln, qn("a:solidFill")); cc = etree.SubElement(sf, qn("a:srgbClr")); cc.set("val", color)
        tcPr.insert(i, ln)


def _cell(cell, fill, size, color, font):
    cell.fill.solid(); cell.fill.fore_color.rgb = fill
    cell.margin_left = cell.margin_right = Inches(0.03)
    cell.margin_top = cell.margin_bottom = 0
    cell.vertical_anchor = MSO_ANCHOR.MIDDLE
    for pg in cell.text_frame.paragraphs:
        pg.alignment = CENTER
        for r in pg.runs:
            r.font.size = Pt(size); r.font.color.rgb = color; r.font.name = font; r.font.bold = False
            rPr = r._r.get_or_add_rPr(); ea = rPr.find(qn("a:ea"))
            if ea is None: ea = etree.SubElement(rPr, qn("a:ea"))
            ea.set("typeface", font)
    _borders(cell, "C9DFF5", 0.75)


def build(c):
    table = photo = None
    for sh in c.s.shapes:
        if sh.name == "표 53": table = sh
        if sh.name == "그림 62": photo = sh
    c.keep_only("TextBox 60", "표 53", "그림 62")
    c.background(1000, 1110)

    # 키메시지
    km = c.rect(0.20, 1.03, 10.43, 0.46, name="키메시지")
    c.write(km, [[("전문 지식 및 경험에 기반한", 23, BLUE_T, KEY_FONT), (" 조직 구성 및 인력 투입", 23, NAVY_T, KEY_FONT)]])

    # ── PM 카드 ──
    c.rrect(X(418), Y(290), 612 * K, H(342), adj=0.06, fill=hexrgb("F4F9FE"), line=hexrgb("C8E2FB"), lw=0.75)
    top = c.shape(MSO_SHAPE.ROUND_2_SAME_RECTANGLE, X(418), Y(290), 612 * K, H(70), fill=hexrgb("3182EA"), adj=[0.35, 0])
    c.write(top, [[("공공사업 21회", 12, WHITE, F3)]])
    ar = photo.width / float(photo.height)
    ph = H(146); photo.height = Inches(ph); photo.width = Inches(ph * ar)
    photo.left = Inches(X(513) - ph * ar / 2); photo.top = Inches(Y(376))
    c.tree.remove(photo._element); c.tree.append(photo._element)
    c.text(X(638), Y(380), 340 * K, H(46), [[("김영민 책임", 15, TXT, F3)]], LEFT)
    c.text(X(638), Y(433), 360 * K, H(70), [[("PM, 사업관리 등", 11.5, SUB, F3)], [("프로젝트 관리전문", 11.5, SUB, F3)]], LEFT, spacing=0.95)
    b = c.rrect(X(433), Y(533), 582 * K, H(88), adj=0.12, fill=hexrgb("E4F3FD"))
    c.write(b, [[("• 청주시 업무지원포털 시스템 유지관리(2023 ~ 현재)", 8.2, TXT, F2)],
                [("• 굿모닝 행정포털시스템 클라우드 전환 1, 2차(2024,2025)", 8.2, TXT, F2)]],
            LEFT, margin=0.1, spacing=1.15)

    # ── 연결선 ──
    c.line(X(690), Y(632), X(690), Y(665), CONN, 1.0)
    c.line(X(246), Y(665), X(1062), Y(665), CONN, 1.0)
    c.line(X(246), Y(665), X(246), Y(700), CONN, 1.0)
    c.line(X(1062), Y(665), X(1062), Y(690), CONN, 1.0)
    c.line(X(1062), Y(737), X(1062), Y(748), CONN, 1.0)
    c.line(X(1005), Y(866), X(645), Y(918), CONN, 1.0)
    c.line(X(1073), Y(866), X(992), Y(923), CONN, 1.0)
    c.line(X(1073), Y(866), X(1160), Y(923), CONN, 1.0)

    # ── 왼쪽: 유지관리 담당 ──
    picc(c, "server", 203, 693, 283, 745, cut=(205, 695))
    c.write(c.rrect(X(150), Y(753), 200 * K, H(130), adj=0.12, fill=DARK),
            [[("유지관리", 12.5, WHITE, F3)], [("담당", 12.5, WHITE, F3)]], spacing=0.95)
    c.text(X(386), Y(772), 300 * K, H(46), [[("이도훈 차장", 13.5, TXT, F3)]], LEFT)
    c.text(X(386), Y(817), 300 * K, H(40), [[("유지관리사업 12회", 11.5, SUB, F3)]], LEFT)
    c.write(c.rrect(X(50), Y(920), 407 * K, H(142), adj=0.1, fill=DARK),
            [[("PM 및 유지관리인력", 13, WHITE, F3)], [("전원 청주/세종 거주", 13, WHITE, F3)]], spacing=1.0)

    # ── 가운데: 분야별 전문인력 ──
    c.text(X(800), Y(760), 175 * K, H(90), [[("분야별", 13, TXT, F3)], [("전문인력", 13, TXT, F3)]], spacing=0.95)
    picc(c, "meet", 1030, 682, 1100, 742, cut=(1032, 684))
    c.write(c.rrect(X(989), Y(748), 172 * K, H(118), adj=0.14, fill=LIGHT, line=LIGHT_LN, lw=0.75),
            [[("전사적", 11, TXT, F3)], [("지원", 11, TXT, F3)]], spacing=0.95)
    for x0, w, lines in ((570, 145, ["지원", "관리"]), (919, 144, ["품질", "보증"]), (1088, 150, ["디자인"])):
        c.write(c.rrect(X(x0), Y(924), w * K, H(130), adj=0.14, fill=LIGHT, line=LIGHT_LN, lw=0.75),
                [[(t, 11, TXT, F3)] for t in lines], spacing=0.95)
    for i, t in enumerate(("관리 및 업무", "기술 및 연계", "조정 및 결정")):
        yy = 950 + i * 39
        c.text(X(733), Y(yy) - 0.12, 25 * K, 0.24, [[("✓", 9, SUB, F3)]])
        c.text(X(762), Y(yy) - 0.12, 150 * K, 0.24, [[(t, 9, TXT, F2)]], LEFT)

    # ── 오른쪽: 월계관 + 투입 표 ──
    picc(c, "laurel", 1373, 272, 1830, 604, cut=(1375, 275))
    cy = Y(432); r = 108 * K
    circ = c.oval(X(1602) - r, cy - r, 2 * r, 2 * r, fill=hexrgb("1F56AF"))
    c.write(circ, [[("공공사업경험", 10, WHITE, F3)], [("100%", 19, WHITE, F3)]], spacing=0.95)

    c.pill(X(1276), Y(612), 678 * K, H(76), fill=hexrgb("CFE8FD"), line=hexrgb("A9D2FA"), lw=0.75)
    c.text(X(1468), Y(612), 320 * K, H(76), [[("총 108MM 투입", 16.5, TXT, F3)]], LEFT)
    picc(c, "person", 1365, 606, 1458, 692, light_key=175)

    t = table.table
    table.left = Inches(X(1278)); table.top = Inches(Y(706))
    cw = 676 * K / 5
    for col in t.columns: col.width = Inches(cw)
    rh = H(372) / 7
    for row in t.rows: row.height = Inches(rh)
    table.width = Inches(cw * 5)
    HDR = hexrgb("E3F3FE"); BODY = hexrgb("FBFDFF"); SUMF = hexrgb("E3F3FE")
    for ri, row in enumerate(t.rows):
        for ci, cell in enumerate(row.cells):
            if ri == 0:
                _cell(cell, HDR, 10.5, TXT, F3)
            elif ri == 6:
                _cell(cell, SUMF, 10.5, TXT if ci == 0 else SUMC, F3)
            elif ci == 0:
                _cell(cell, HDR, 11, TXT, F2)
            else:
                _cell(cell, BODY, 11, TXT, F2)
