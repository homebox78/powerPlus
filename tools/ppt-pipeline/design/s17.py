"""17쪽 — 유지보수 관리 체계 (1/5) (시안 11번)."""
from lib import *


def build(c):
    title_font = F3
    for sh in c.s.shapes:
        if sh.name == "직사각형 9":
            for r in sh.text_frame.paragraphs[0].runs:
                ea = r._r.find(".//" + qn("a:ea"))
                title_font = (ea.get("typeface") if ea is not None else None) or r.font.name or F3
    c.keep_only("TextBox 52")
    c.background(1000, 235)

    INK = hexrgb("1F2A44")
    LN = hexrgb("C9DCF7")

    def T(g, x, yc, runs, w=600, h=44, align=LEFT):
        return c.text(g.X(x), g.Y(yc - h / 2.0), w * K, h * K, [runs], align)

    # ── 제목 ──
    g = c.grp(135, 220)
    c.rrect(g.X(810), g.Y(198), 436 * K, 22 * K, adj=0.5, fill=c.rgb(1000, 212))
    T(g, 85, 175, [("과업의 유형 및 특성을 반영한 ", 22.5, c.rgb(108, 160), title_font),
                   ("실효성 있는 맞춤 관리 체계", 22.5, c.rgb(838, 160), title_font)], w=1800, h=80)

    # ── 방법론 띠 ──
    g = c.grp(245, 343)
    c.rrect(g.X(58), g.Y(245), 1885 * K, 98 * K, adj=0.3, fill=c.rgb(700, 252), line=LN, lw=0.75)
    bars = [(87, 675, (100, 292), "gear", (200, 262, 258, 322), 288, "운영 및 유지보수(S-ISM)", WHITE),
            (753, 1257, (770, 292), "org", (845, 266, 902, 318), 927, "사업관리방법론(S-PMM)", WHITE),
            (1335, 1913, (1350, 292), "code", (1438, 270, 1496, 314), 1520, "기능 개발방법론(S-SEM)", c.rgb(1560, 285))]
    for x0, x1, pt, nm, box, tx, lab, col in bars:
        c.pill(g.X(x0), g.Y(257), (x1 - x0) * K, 70 * K, fill=c.rgb(*pt))
        c.pic(c.crop(nm, *box, cut=pt), g.X(box[0]), g.Y(box[1]), (box[2] - box[0]) * K)
        T(g, tx, 292, [(lab, 10.5, col, F3)], w=340)
    for x in (714, 1297):
        T(g, x - 30, 291, [("+", 16, c.rgb(100, 292), F3)], w=60, align=CENTER)

    # ── 카드 3장 ──
    g = c.grp(362, 912)
    HB = c.rgb(300, 440)
    cards = [
        (58, 676, "shield", (92, 378, 164, 458), [(187, "유지관리", 357, 385, "기존기능 안정적 운영")],
         (120, 478, 640, 684), 75, 660, 688,
         [(725, "기존 서비스 안정성 · 지속성 · 사용 용이성"), (769, "비상시 업무연속성"),
          (815, "백업복구 · 보안 백오피스"), (858, "변경사항 즉시 현행화")]),
        (691, 1308, "bank", (728, 378, 802, 452), None,
         (790, 478, 1225, 686), 708, 1292, 688,
         [(725, "시스템적 · 법제도적 행정환경 변화 신속 반응"), (771, "변화 관리 차원 현행화"),
          (815, "전사 차원 행정환경변화 감지 및 대응"), (858, "중장기적 변화 대비")]),
        (1325, 1943, "bulb", (1362, 372, 1440, 458), [(1460, "신규 요구사항", 1697, 1723, "기능 개발 지원")],
         (1360, 488, 1910, 688), 1342, 1926, 690,
         [(728, "사용자와 밀착 면담 기존 개선 사항 · 새로운"), (768, None), (816, "정기적 비정기 요구사항 파악"),
          (861, "서비스 만족도 점검")]),
    ]
    chk = c.crop("chk", 94, 711, 123, 740, cut=(96, 713), cut_thresh=30)
    for x0, x1, ico, ibox, head, ill, bx0, bx1, by, items in cards:
        c.rrect(g.X(x0), g.Y(362), (x1 - x0) * K, 550 * K, adj=0.035, fill=c.rgb(x0 + 12, 600), line=LN, lw=0.75)
        c.shape(MSO_SHAPE.ROUND_2_SAME_RECTANGLE, g.X(x0), g.Y(362), (x1 - x0) * K, 106 * K, fill=HB, adj=[0.18, 0])
        c.pic(c.crop(ico, *ibox, cut=(x0 + 20, 440)), g.X(ibox[0]), g.Y(ibox[1]), (ibox[2] - ibox[0]) * K)
        if head:
            tx, big, dx, sx, small = head[0]
            T(g, tx, 416, [(big, 13.5 if x0 < 100 else 12.5, WHITE, F3)], w=260, h=60)
            c.line(g.X(dx), g.Y(397), g.X(dx), g.Y(437), WHITE, 0.75)
            T(g, sx, 417, [(small, 9.5, hexrgb("D6E6FF"), F2)], w=260)
        else:
            T(g, 825, 402, [("시스템 · 법제도 환경변화", 11.5, WHITE, F3)], w=440, h=50)
            T(g, 825, 441, [("신속 지원", 10, WHITE, F2)], w=300, h=36)
        c.pic(c.crop(ico + "_ill", *ill, cut=(ill[0] + 2, ill[1] + 2), cut_thresh=18), g.X(ill[0]), g.Y(ill[1]), (ill[2] - ill[0]) * K)
        c.rrect(g.X(bx0), g.Y(by), (bx1 - bx0) * K, (895 - by) * K, adj=0.1, fill=WHITE, line=hexrgb("E3EDFB"), lw=0.75)
        for y, tx in items:
            if tx is None:
                T(g, bx0 + 66, y, [("서비스 발굴", 8.5, INK, F2)])
                continue
            c.pic(chk, g.X(bx0 + 20), g.Y(y - 14), 28 * K)
            T(g, bx0 + 66, y, [(tx, 8.5, INK, F2)])

    # ── 아래: 안내 인물 + 결론 띠 ──
    g = c.grp(945, 1050)
    PB = c.rgb(1200, 960)
    c.pill(g.X(455), g.Y(945), 1230 * K, 105 * K, fill=PB)
    c.pic(c.crop("target", 552, 948, 648, 1044, cut=(1200, 960)), g.X(552), g.Y(948), 96 * K)
    c.line(g.X(673), g.Y(975), g.X(673), g.Y(1020), c.rgb(838, 160), 1.0)
    T(g, 713, 997, [("과업유형 및 특성에 맞는 방법론 선택 ", 15, c.rgb(108, 160), F3),
                    ("커스터마이징", 15, c.rgb(838, 160), F3)], w=940, h=70)
    wp = c.pic(c.crop("woman", 150, 872, 450, 1125, cut=(160, 935), cut_thresh=80), 95 * K, 0, 360 * K)
    wp.top = Inches(SLIDE_H) - wp.height
