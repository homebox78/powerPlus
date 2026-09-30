"""35쪽 — 서비스수준협약(SLA) (2차 시안 design_ppt2/s35.png).
왼쪽 표(원래 Table 84)는 값 그대로 두고 자리·색만 시안에 맞춘다. 오른쪽 성과 카드·절차 줄은 도형으로 다시 그리고
아이콘 4개만 시안에서 오린다. 글은 원래 장표 문구."""
from lib import *

KEY_FONT = "G마켓 산스 TTF Bold"
TXT = hexrgb("1B2B4B")
NAVY_T = hexrgb("0B2E6B")
BLUE_T = hexrgb("2070E8")
VAL = hexrgb("0A72FA")

# 세로: 시안 y272(본문 카드 위) → 1.62in, y1088(카드 아래) → 7.02in
Y0, IN0, V = 272.0, 1.62, (7.02 - 1.62) / (1088 - 272)


def Y(y): return IN0 + (y - Y0) * V
def H(h): return h * V
def X(x): return x * K


def _borders(cell, color, w_pt):
    tcPr = cell._tc.get_or_add_tcPr()
    for tag in ("a:lnL", "a:lnR", "a:lnT", "a:lnB"):
        old = tcPr.find(qn(tag))
        if old is not None: tcPr.remove(old)
    for i, tag in enumerate(("a:lnL", "a:lnR", "a:lnT", "a:lnB")):
        ln = etree.Element(qn(tag)); ln.set("w", str(int(w_pt * 12700)))
        sf = etree.SubElement(ln, qn("a:solidFill")); c = etree.SubElement(sf, qn("a:srgbClr")); c.set("val", color)
        tcPr.insert(i, ln)


def _cell_text(cell, size, color, font, align=CENTER):
    tf = cell.text_frame
    cell.margin_left = cell.margin_right = Inches(0.03)
    cell.margin_top = cell.margin_bottom = 0
    cell.vertical_anchor = MSO_ANCHOR.MIDDLE
    for pg in tf.paragraphs:
        pg.alignment = align
        for r in pg.runs:
            r.font.size = Pt(size); r.font.color.rgb = color; r.font.name = font; r.font.bold = False
            rPr = r._r.get_or_add_rPr(); ea = rPr.find(qn("a:ea"))
            if ea is None: ea = etree.SubElement(rPr, qn("a:ea"))
            ea.set("typeface", font)


def build(c):
    table = None
    for sh in c.s.shapes:
        if sh.shape_type == 19: table = sh
    c.remove("TextBox 80", "직사각형 461", "직사각형 462", "한쪽 모서리가 잘린 사각형 95", "한쪽 모서리가 잘린 사각형 92",
             "TextBox 19", "그룹 1", "TextBox 669")

    c.background(1000, 1110)

    # 키메시지
    km = c.rect(0.20, 1.03, 10.43, 0.46, name="키메시지")
    c.write(km, [[("다수 공공기관 ", 23, NAVY_T, KEY_FONT), ("SLA 운영 경험 보유", 23, BLUE_T, KEY_FONT),
                  (" · 목표 수준 달성으로 ", 23, NAVY_T, KEY_FONT), ("검증된 관리 역량", 23, BLUE_T, KEY_FONT)]])

    CARD = hexrgb("FBFDFF"); CARD_LN = hexrgb("DCEAF8")
    HDR = c.rgb(900, 330)
    # ── 왼쪽 카드 ──
    c.rrect(X(45), Y(270), 945 * K, H(818), adj=0.025, fill=CARD, line=CARD_LN, lw=0.75)
    c.write(c.rrect(X(62), Y(283), 913 * K, H(69), adj=0.35, fill=HDR),
            [[("SLA 지표 체계 및 운영 실적(2026. 8월)", 15, WHITE, F3)]], align=LEFT, margin=0.2)

    # 표 — 원래 값 그대로, 자리·색만
    t = table.table
    widths = [140, 262, 118, 127, 115, 138]
    for i, w in enumerate(widths): t.columns[i].width = Inches(w * K)
    table.left = Inches(X(68)); table.top = Inches(Y(375))
    hh = H(56); body = (H(1022 - 375) - hh) / 12.0
    t.rows[0].height = Inches(hh)
    for r in range(1, 13): t.rows[r].height = Inches(body)
    TH, CAT, CELL = hexrgb("D0E9FE"), hexrgb("D6EAFD"), hexrgb("F3F8FE")
    tbl = t._tbl; pr = tbl.tblPr
    for a in ("firstRow", "bandRow"): pr.set(a, "0")
    for r in range(13):
        for ci in range(6):
            cell = t.cell(r, ci)
            if r == 0:
                cell.fill.solid(); cell.fill.fore_color.rgb = TH
                _cell_text(cell, 9, TXT, F3)
            elif ci == 0:
                cell.fill.solid(); cell.fill.fore_color.rgb = CAT
                _cell_text(cell, 9, TXT, F3)
            else:
                cell.fill.solid(); cell.fill.fore_color.rgb = CELL
                if ci == 5: _cell_text(cell, 8.5, VAL, F3)
                elif ci == 1: _cell_text(cell, 8.5, TXT, F2, LEFT)
                else: _cell_text(cell, 8.5, TXT, F2)
            if ci == 1 and r > 0: cell.margin_left = Inches(0.08)
            _borders(cell, "FFFFFF", 1.5)
    # 표를 카드 앞으로
    c.tree.remove(table._element)
    ext = c.tree.find(qn("p:extLst"))
    if ext is not None: ext.addprevious(table._element)
    else: c.tree.append(table._element)
    c.text(X(72), Y(1036), 900 * K, H(28),
           [[("※ 공공기관 2등급 정보시스템 운영지원 사업 서비스수준협약서 기준 · 2026.8월 평가 결과", 7.5, TXT, F2)]], align=LEFT)

    # ── 오른쪽 카드 ──
    c.rrect(X(1008), Y(270), 952 * K, H(818), adj=0.025, fill=CARD, line=CARD_LN, lw=0.75)
    c.write(c.rrect(X(1025), Y(281), 917 * K, H(73), adj=0.35, fill=HDR),
            [[("SLA 운영 성과 및 협약 관리 경험", 15, WHITE, F3)]], align=LEFT, margin=0.2)

    KPI = hexrgb("DCEEFD")
    kx = [(1028, 1240), (1258, 1476), (1493, 1710), (1726, 1940)]
    kd = [("종합평가", "100점", "탁월 등급"), ("가용률", "100%", "무중단 운영"),
          ("장애 발생", "0건", "인적·반복장애 0"), ("요청 적기처리", "100%", "목표 100% 달성")]
    for (x0, x1), (a, b, d) in zip(kx, kd):
        w = (x1 - x0) * K
        c.rrect(X(x0), Y(372), w, H(153), adj=0.1, fill=KPI)
        c.text(X(x0), Y(384), w, H(30), [[(a, 9.5, TXT, F2)]])
        c.text(X(x0), Y(419), w, H(56), [[(b, 20, VAL, F3)]])
        c.text(X(x0), Y(480), w, H(30), [[(d, 8.5, TXT, F2)]])

    LAB, ROW, ROWLN = hexrgb("D4E9FD"), hexrgb("F7FBFF"), hexrgb("E1EEFB")
    LAB_T = hexrgb("3F7FD6")
    rows = [
        (548, 645, "협약 체결·개정", (1236, 543, 1338, 640),
         ["필수지표(가용률) + 선택지표 11개를 발주기관과 합의하여 협약 체결",
          "운영 중 지표·목표수준 조정은 협약 개정요청서로 처리"]),
        (665, 760, "월간 측정·보고", (1238, 660, 1336, 757),
         ["매월 지표별 측정값·근거자료 산출 → 월간 운영보고서", "제출·대면 보고",
          "ITSM 자동 집계와 근거자료 교차 확인으로 측정 신뢰성 확보"]),
        (778, 875, "평가·환류", (1240, 772, 1334, 870),
         ["평가점수 × 가중치 환산으로 종합점수 산출,", "평가등급(탁월~불량) 관리",
          "미달 지표는 원인 분석 후 개선계획 수립 → 익월 보고로 이행 확인"]),
        (893, 990, "위약·제재 관리", (1236, 895, 1338, 990),
         ["종합서비스 수준 미달 시 위약금,", "장시간·반복·인적장애 시 제재금 기준 숙지",
          "계약 기간 중 제재 부과 사례 없음"]),
    ]
    for i, (y0, y1, lab, ib, desc) in enumerate(rows):
        c.rrect(X(1028), Y(y0), 912 * K, H(y1 - y0), adj=0.08, fill=ROW, line=ROWLN, lw=0.75)
        c.write(c.rrect(X(1034), Y(y0 + 5), 188 * K, H(y1 - y0 - 10), adj=0.1, fill=LAB),
                [[(lab, 9.5, LAB_T, F3)]])
        x0, iy0, x1, iy1 = ib
        p = c.crop("ico%d" % i, x0, iy0, x1, iy1, cut=(x0 + 2, iy0 + 2), cut_thresh=40)
        iw = (x1 - x0) * K; ih = iw * (iy1 - iy0) / (x1 - x0)
        c.pic(p, X(x0), Y((y0 + y1) / 2.0) - ih / 2, iw)
        c.text(X(1352), Y(y0 + 6), 585 * K, H(y1 - y0 - 12),
               [[(d, 7.5, TXT, F2)] for d in desc], align=LEFT, wrap=True, spacing=1.1)

    c.write(c.pill(X(1027), Y(1012), 915 * K, H(54), fill=c.rgb(1100, 1025)),
            [[("상시 모니터링 · 월간 평가 · 즉시 개선으로 목표 수준 달성", 12, WHITE, F3)]])
