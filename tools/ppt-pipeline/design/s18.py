"""18쪽 — 유지보수 관리 체계 (2/5) (시안 12번)."""
from lib import *


def build(c):
    title_font = F3
    for sh in c.s.shapes:
        if sh.name == "직사각형 2":
            for r in sh.text_frame.paragraphs[0].runs:
                ea = r._r.find(".//" + qn("a:ea"))
                title_font = (ea.get("typeface") if ea is not None else None) or r.font.name or F3
    c.keep_only("TextBox 74")
    c.background(1000, 235)
    INK = hexrgb("0A3470")         # 카드 제목 남색
    BODY = hexrgb("26324A")
    LN = c.rgb(700, 252)           # 카드 테두리

    # 제목
    g = c.grp(140, 215)
    c.text(g.X(48), g.Y(140), 1800 * K, 75 * K,
           [[("행정 및 공공기관 통합유지보수 경험으로 검증된 ", 24, NAVY, title_font), ("서비스 지원 체계", 24, BLUE, title_font)]], LEFT)

    # 인물 + 특성 카드 3
    g = c.grp(220, 600)
    c.pic(c.crop("woman", 0, 222, 488, 600, cut=(3, 224), cut_thresh=30), g.X(0), g.Y(222), 488 * K)
    cards = [
        (512, 990, (540, 262, 685, 438), 705, "안정성",
         [(705, "착수부터 종료 안정적 관리활동,"), (705, "시스템 변화에 사용자 그룹이"), (620, "반응할 필요 없도록 안정적 서비스 보장.")]),
        (1018, 1494, (1045, 265, 1205, 435), 1225, "지속성",
         [(1225, "무중단 지속적 서비스,"), (1225, "강력한 보안 점검과 철저한"), (1225, "백업·복구 활동으로 지속성 확보.")]),
        (1515, 1968, (1525, 260, 1703, 430), 1715, "신속성",
         [(1715, "환경변화에 신속 반응,"), (1715, "사용자 요구 능동적 파악"), (1715, "신속 응대.")]),
    ]
    for i, (x0, x1, ic, tx, ttl, lines) in enumerate(cards):
        c.rrect(g.X(x0), g.Y(252), (x1 - x0) * K, 255 * K, adj=0.05, fill=c.rgb(x0 + 30, 480), line=LN, lw=0.75)
        c.pic(c.crop("top%d" % i, *ic, cut=(x0 + 12, 262), cut_thresh=40), g.X(ic[0]), g.Y(ic[1]), (ic[2] - ic[0]) * K)
        c.text(g.X(tx), g.Y(298), 250 * K, 62 * K, [[(ttl, 17, INK, F3)]], LEFT)
        for (lx, s), ly in zip(lines, (395, 430, 465)):
            c.text(g.X(lx), g.Y(ly - 15), (x1 - lx - 8) * K, 30 * K, [[(s, 7, BODY, F2)]], LEFT)

    # 주요활동 커스터마이징
    g = c.grp(530, 760)
    c.rrect(g.X(483), g.Y(595), 1485 * K, 168 * K, adj=0.08, fill=c.rgb(1060, 600))
    tab = c.shape(MSO_SHAPE.TRAPEZOID, g.X(493), g.Y(533), 425 * K, 59 * K, fill=c.rgb(700, 545), adj=0.55)
    c.pic(c.crop("gear", 534, 543, 574, 581), g.X(534), g.Y(543), 40 * K)
    c.text(g.X(588), g.Y(533), 300 * K, 59 * K, [[("주요활동 커스터마이징", 10.5, WHITE, F3)]], LEFT)
    c.line(g.X(916), g.Y(558), g.X(1962), g.Y(558), c.rgb(1400, 558), 1.0)
    acts = [(496, 775, (513, 628, 607, 724), 623, "SR 처리", 751),
            (795, 1053, (820, 626, 912, 722), 924, "RFC 처리", 1033),
            (1073, 1328, (1093, 630, 1192, 724), 1202, "배포 관리", 1309),
            (1347, 1655, (1376, 623, 1467, 724), 1479, "요구사항 관리", 1636),
            (1673, 1962, (1690, 628, 1784, 716), 1806, "장애 관리", 1937)]
    for i, (x0, x1, ic, tx, lab, cx) in enumerate(acts):
        c.rrect(g.X(x0), g.Y(612), (x1 - x0) * K, 133 * K, adj=0.08, fill=c.rgb(x1 - 40, 640), line=LN, lw=0.75)
        c.pic(c.crop("act%d" % i, *ic, cut=(x1 - 40, 640), cut_thresh=40), g.X(ic[0]), g.Y(ic[1]), (ic[2] - ic[0]) * K)
        c.text(g.X(tx), g.Y(660), (cx - tx - 12) * K, 44 * K, [[(lab, 8.5, INK, F3)]], LEFT)
        ch = c.shape(MSO_SHAPE.CHEVRON, g.X(cx - 6), g.Y(673), 11 * K, 19 * K, fill=INK, adj=0.85)

    # 운영/유지보수 방법론
    g = c.grp(767, 1072)
    PN = c.rgb(300, 830)
    c.rrect(g.X(35), g.Y(767), 1932 * K, 305 * K, adj=0.04, fill=PN)
    c.pic(c.crop("target", 68, 774, 122, 826), g.X(68), g.Y(774), 54 * K)
    c.text(g.X(135), g.Y(778), 380 * K, 45 * K, [[("운영/유지보수 방법론(S-ISM)", 10.5, WHITE, F3)]], LEFT)
    c.line(g.X(510), g.Y(800), g.X(1940), g.Y(800), WHITE, 0.75)
    blocks = [
        (50, 536, 98, (283, 522), 290, "01", "프로세스 관리", ["표준화된 프로세스 기반의", "체계적 운영 관리"]),
        (537, 1002, 580, (773, 988), 781, "02", "서비스 수행", ["안정적이고 연속적인", "서비스 운영"]),
        (1003, 1480, 1046, (1240, 1470), 1246, "03", "서비스 개발 및 전달", ["변화에 유연한 개발과", "신속한 전달 체계"]),
        (1482, 1952, 1526, (1722, 1933), 1730, "04", "지원", ["고객 중심의 기술지원 및", "전문가 지원 체계"]),
    ]
    for i, (x0, x1, nx, (cx0, cx1), tx, no, ttl, desc) in enumerate(blocks):
        c.pic(c.crop("blk%d" % i, x0, 835, x1, 1064), g.X(x0), g.Y(835), (x1 - x0) * K)
        c.rect(g.X(nx - 4), g.Y(897), 46 * K, 34 * K, fill=c.rgb(nx + 19, 894))
        c.text(g.X(nx - 12), g.Y(892), 62 * K, 44 * K, [[(no, 11, WHITE, F3)]])
        c.rect(g.X(cx0), g.Y(872), (cx1 - cx0) * K, 60 * K, fill=hexrgb("F6F9FE"))
        c.rect(g.X(cx0), g.Y(931), (cx1 - cx0) * K, 65 * K, fill=hexrgb("F1F6FE"))
        c.text(g.X(tx), g.Y(878), (cx1 - tx) * K, 44 * K, [[(ttl, 9.5, INK, F3)]], LEFT)
        for s, ly in zip(desc, (951, 982)):
            c.text(g.X(tx), g.Y(ly - 14), (cx1 - tx) * K, 28 * K, [[(s, 7, BODY, F2)]], LEFT)
