"""33쪽 — 3. 품질관리 및 보증 (2차 시안 design_ppt2/s33.png).

원래 장표의 표(표 150)는 값·행·열 그대로 남기고 자리·색만 시안에 맞춘다.
인물 일러스트·순환 그림은 시안에서 오린다. 글은 원래 장표 문구.
"""
from lib import *

KFONT = "G마켓 산스 TTF Bold"
KNAVY, KBLUE = hexrgb("0B2E6B"), hexrgb("2070E8")
TXT = hexrgb("14326E")        # 본문 남색
HDR = hexrgb("1B4E90")        # 카드 머리 남색
OUT = hexrgb("4191FA")        # 알약 테두리 파랑
LN = hexrgb("8DB8F2")         # 연결선
EDGE = hexrgb("D6E6F7")       # 옅은 테두리


def _border(cell, color, w=0.75):
    tcPr = cell._tc.get_or_add_tcPr()
    for tag in ("a:lnL", "a:lnR", "a:lnT", "a:lnB"):
        old = tcPr.find(qn(tag))
        if old is not None: tcPr.remove(old)
    # 스키마 순서: lnL, lnR, lnT, lnB 가 맨 앞(lnTlToBr·채우기보다 앞)
    for i, tag in enumerate(("a:lnL", "a:lnR", "a:lnT", "a:lnB")):
        ln = etree.Element(qn(tag), w=str(int(w * 12700)), cap="flat", cmpd="sng", algn="ctr")
        sf = etree.SubElement(ln, qn("a:solidFill"))
        etree.SubElement(sf, qn("a:srgbClr"), val=str(color))
        etree.SubElement(ln, qn("a:prstDash"), val="solid")
        tcPr.insert(i, ln)


def build(c):
    s = c.s
    c.vmap(262, 1.62, 1092, 7.02)
    Y = c.cy
    X = lambda x: x * K

    table = None
    for sh in list(s.shapes):
        if sh.shape_type == 19:
            table = sh
        elif sh.name != "TextBox 79":
            c.tree.remove(sh._element)

    c.background(1000, 300)

    # ── 키메시지 ──
    km = c.text(0.20, 1.03, 10.43, 0.40, [[("전사적 품질관리 조직", 23, KBLUE, KFONT),
                                           ("에 의한 품질관리 및 품질보증", 23, KNAVY, KFONT)]])
    km.name = "키메시지"

    # ── 품질보증 대상 + 연결선 ──
    yl = Y(293)
    c.line(X(341), yl, X(815), yl, LN, 1.0)
    c.line(X(1185), yl, X(1659), yl, LN, 1.0)
    c.line(X(341), yl, X(341), Y(380), LN, 1.0)
    c.line(X(1659), yl, X(1659), Y(380), LN, 1.0)
    c.pill(X(840), Y(266), X(320), Y(322) - Y(266), fill=WHITE, line=EDGE, lw=0.75)
    for dx in (822, 1177):
        c.oval(X(dx - 13), yl - X(13), X(26), X(26), fill=hexrgb("D5ECFD"))
        c.oval(X(dx - 7), yl - X(7), X(14), X(14), fill=hexrgb("3180F2"))
    c.text(X(840), Y(266), X(320), Y(322) - Y(266), [[("품질보증 대상", 17, TXT, F3)]])
    c.text(X(700), Y(328), X(600), Y(370) - Y(328), [[("절차 / 산출물 / 성과", 13.5, hexrgb("0C50C2"), F3)]])

    # ── 세 목표 알약 ──
    pills = [(45, 680, "사업 연속성을 고려한 유지관리방법론 적용"),
             (697, 1305, "품질보증팀 구성을 통한 종합적/객관적 품질 점검 수행"),
             (1325, 1958, "분석/설계 도구 활용 및 점검도구를 활용한 생산성 확보")]
    for x0, x1 in ((680, 697), (1305, 1325)):
        c.line(X(x0), Y(417), X(x1), Y(417), OUT, 1.0)
    for x0, x1, t in pills:
        b = c.pill(X(x0), Y(380), X(x1 - x0), Y(455) - Y(380), fill=WHITE, line=OUT, lw=2.0)
        c.write(b, [[(t, 9, TXT, F2)]])

    # ── 세 활동 카드 ──
    cards = [(45, 678, "품질활동계획 수립", 117, 150,
              [(573, "품질관리 역할 정의"), (607, "품질활동 주기 및 시정/예방 조치 절차 정의"),
               (641, "표준 및 절차 정의"), (675, "품질특성 및 목표 정의")]),
             (698, 1303, "품질활동/품질평가", 750, 782,
              [(584, "진행 내역에 대한 위험/이슈 사항 점검"), (618, "프로젝트 관리 단계별 체크리스트 기반의 품질 평가"),
               (652, "품질요구사항 기반의 품질특성 및 목표의 측정")]),
             (1325, 1957, "품질활동 보고", 1378, 1410,
              [(571, "주간단위의 품질보증 활동 수행 결과"), (605, "품질평가 결과: 단계 평가 점수, 단계이슈 사항"),
               (639, "품질목표 측정결과 : 품질목표 달성여부,"), (673, None, "미 달성 시 조치 계획 수립")])]
    for x0, x1, head, cx, tx, items in cards:
        c.rrect(X(x0), Y(475), X(x1 - x0), Y(710) - Y(475), adj=0.05, fill=WHITE, line=EDGE, lw=0.75)
        c.shape(MSO_SHAPE.ROUND_2_SAME_RECTANGLE, X(x0), Y(475), X(x1 - x0), Y(541) - Y(475), fill=HDR, adj=[0.18, 0])
        c.text(X(x0), Y(475), X(x1 - x0), Y(541) - Y(475), [[(head, 15, WHITE, F3)]])
        lh = Y(24) - Y(0)
        for it in items:
            y, t = it[0], it[1]
            if t is None:
                t = it[2]
            else:
                c.text(X(cx - 6), Y(y) - lh / 2, X(30), lh, [[("✓", 10, hexrgb("2F62B6"), "Segoe UI Symbol")]])
            c.text(X(tx), Y(y) - lh / 2, X(x1 - tx - 20), lh, [[(t, 8.5, TXT, F2)]], LEFT)
    for px in (687, 1313):
        c.oval(X(px - 30), Y(510) - X(30), X(60), X(60), fill=WHITE, line=EDGE, lw=0.75)
        c.shape(MSO_SHAPE.MATH_PLUS, X(px - 20), Y(510) - X(20), X(40), X(40), fill=hexrgb("2D81F4"), adj=[0.2])

    # ── 아래 판 ──
    c.rrect(X(45), Y(733), X(1910), Y(1090) - Y(733), adj=0.04, fill=hexrgb("EEF7FD"), line=hexrgb("DCEBF8"), lw=0.75)

    # 인물·순환 그림(시안에서 오림) + 이름 띠
    g = c.grp(750, 1080)
    c.pic(c.crop("people", 85, 750, 742, 1080, cut=(87, 752), cut_thresh=18), g.X(85), g.Y(750), 657 * K)
    BAR = hexrgb("14437F")
    for x0, x1, a, b in ((88, 279, "품질통제", "(사업수행팀)"), (469, 739, "품질보증", "(전사품질팀)")):
        c.rect(g.X(x0 + 5), g.Y(952), (x1 - x0 - 10) * K, 68 * K, fill=BAR)
        c.text(g.X(x0 + 5), g.Y(952), (x1 - x0 - 10) * K, 68 * K,
               [[(a, 11.5, WHITE, F3)], [(b, 9, WHITE, F2)]], spacing=0.95)

    # ── 표: 원래 값 그대로, 자리·색만 ──
    if table is not None:
        c.tree.remove(table._element); c.tree.append(table._element)   # 아래 판 위로
        t = table.table
        cols = [198, 265, 459, 208]
        rows = [(755, 798), (798, 927), (927, 992), (992, 1068)]
        table.left = Inches(X(795)); table.top = Inches(Y(755))
        for col, w in zip(t.columns, cols):
            col.width = Inches(X(w))
        for row, (a, b) in zip(t.rows, rows):
            row.height = Inches(Y(b) - Y(a))
        for ri, row in enumerate(t.rows):
            for cell in row.cells:
                cell.fill.solid()
                cell.fill.fore_color.rgb = hexrgb("CDE7FE") if ri == 0 else hexrgb("E9F5FE")
                _border(cell, "B8CEEA", 0.75)
                for pg in cell.text_frame.paragraphs:
                    for r in pg.runs:
                        r.font.color.rgb = hexrgb("1251AE") if ri == 0 else TXT
