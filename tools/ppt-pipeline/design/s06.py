"""6쪽 — 사업의 배경 및 목적 (시안 2번).

세로는 시안 y140~1095 를 1.02~7.10in 로 늘려 놓는다. 상자는 늘린 좌표로 그리고,
그림·글은 크기는 그대로 두고 중심만 같은 대응으로 옮긴다.
"""
from lib import *


def build(c):
    title_font = F3
    for sh in c.s.shapes:
        if sh.name == "직사각형 99":
            for r in sh.text_frame.paragraphs[0].runs:
                ea = r._r.find(".//" + qn("a:ea"))
                title_font = (ea.get("typeface") if ea is not None else None) or r.font.name or F3
    c.keep_only("TextBox 73")
    c.vmap(140, 1.02, 1095, 7.15)
    V = c.cy

    def box(fn, x0, y0, x1, y1, **kw):
        return fn(x0 * K, V(y0), (x1 - x0) * K, V(y1) - V(y0), **kw)

    def pic(name, x0, y0, x1, y1, cut=None, thresh=45):
        p = c.crop(name, x0, y0, x1, y1, cut=cut, cut_thresh=thresh)
        return c.pic(p, x0 * K, V((y0 + y1) / 2.0) - (y1 - y0) * K / 2.0, (x1 - x0) * K)

    def txt(x0, x1, yc, lines, align=CENTER, h=0.5, **kw):
        return c.text(x0 * K, V(yc) - h / 2.0, (x1 - x0) * K, h, lines, align, **kw)

    def dark(x0, y0, x1, y1):
        im = c.D.crop((int(x0 * c.Z), int(y0 * c.Z), int(x1 * c.Z), int(y1 * c.Z)))
        return RGBColor(*min(im.getdata(), key=sum))

    c.background(15, 330)
    INK = dark(1130, 735, 1290, 760)
    GRAY = dark(910, 1020, 1130, 1062)
    LN = c.rgb(1000, 337)

    # ── 키메시지 띠 ──
    box(c.rrect, 37, 140, 1963, 313, adj=0.06, fill=c.rgb(1000, 300), line=c.rgb(1000, 140), lw=0.5)
    pic("ban_l", 70, 143, 415, 312, cut=(430, 250), thresh=30)
    pic("ban_r", 1625, 152, 1945, 312, cut=(1600, 250), thresh=18)
    txt(430, 1600, 193, [[("안정적 운영관리 및 환경 변화에 대한 신속 대처로", 16.5, dark(560, 170, 1440, 215), title_font)]])
    txt(430, 1600, 258, [[("내부 지원업무의 효율성 지속적 확보와 유지", 18, dark(570, 240, 1430, 280), title_font)]])

    # ── 왼쪽 남색 카드 3 ──
    NV = c.rgb(50, 500)
    SUB = c.rgb(200, 455)
    cards = [(335, 522, "사업목적", ["본 사업의 궁극적인 목적과", "지향점을 제시합니다."], (62, 368, 162, 466)),
             (540, 813, "사업목표", ["구체적인 목표와 달성하고자", "하는 가치를 제시합니다."], (68, 594, 158, 694)),
             (832, 1093, "추진배경", ["사업을 추진하게 된", "필요성과 근거를 제시합니다."], (66, 866, 162, 962))]
    for i, (y0, y1, ttl, sub, ic) in enumerate(cards):
        box(c.rrect, 37, y0, 414, y1, adj=0.06, fill=NV)
        pic("lc%d" % i, *ic, cut=(45, (y0 + y1) / 2), thresh=30)
        yc = (ic[1] + ic[3]) / 2.0
        txt(180, 410, yc - 15, [[(ttl, 12.5, WHITE, F3)]], LEFT, h=0.4)
        txt(180, 412, yc + 50, [[(s, 7, WHITE, F2)] for s in sub], LEFT, h=0.4, spacing=1.25)

    # ── 오른쪽 패널 ──
    PF = c.rgb(1200, 530)
    box(c.rrect, 433, 335, 1963, 820, adj=0.03, fill=PF, line=LN, lw=0.5)
    box(c.rrect, 433, 840, 1963, 1095, adj=0.05, fill=c.rgb(1200, 862), line=LN, lw=0.5)
    BAR = c.rgb(454, 361)
    for y, t in ((361, "사업목표"), (545, "5대 목표"), (860, "4대 추진배경")):
        c.rrect(450 * K, V(y) - 0.075, 0.04, 0.15, adj=0.5, fill=BAR)
        txt(472, 800, y, [[(t, 10, INK, F3)]], LEFT, h=0.3)

    # 사업목표 흐름
    PB = c.rgb(700, 480)
    box(c.pill, 466, 388, 896, 500, fill=PB)
    box(c.pill, 1532, 388, 1942, 500, fill=c.rgb(1750, 480))
    box(c.pill, 965, 385, 1460, 502, fill=c.rgb(1200, 480))
    pic("cloud", 515, 398, 622, 488, cut=(640, 480), thresh=30)
    pic("mon", 1028, 401, 1116, 489)
    pic("shd", 1592, 398, 1675, 490, cut=(1700, 480), thresh=30)
    txt(630, 890, 444, [[("무중단 서비스 제공", 9.2, INK, F3)]], LEFT, h=0.3)
    txt(1700, 1930, 444, [[("서비스 품질 보장", 9.2, INK, F3)]], LEFT, h=0.3)
    txt(1148, 1450, 444, [[("안정적이고 능동적인", 9.5, WHITE, F3)], [("업무지원포털 서비스 제공", 9.5, WHITE, F3)]], LEFT, h=0.5, spacing=1.15)
    AR = c.rgb(930, 442)
    for x in (913, 1480):
        c.line(x * K, V(442), (x + 34) * K, V(442), AR, 1.25, arrow=True)

    # 5대 목표
    PK = c.rgb(515, 585)
    kp = [(458, 750, (540, 614, 690, 722), ["시스템 안정성 확보"]),
          (766, 1050, (858, 608, 992, 722), ["업무 연속성 보장"]),
          (1067, 1349, (1158, 612, 1288, 722), ["보안을 강화하여", "철통보안 보장"]),
          (1365, 1646, (1452, 612, 1592, 722), ["체계적이고 지속적인", "지원"]),
          (1662, 1945, (1732, 612, 1902, 722), ["시스템 기능개선"])]
    for i, (x0, x1, ic, lab) in enumerate(kp):
        box(c.rrect, x0, 570, x1, 806, adj=0.06, fill=WHITE, line=LN, lw=0.75)
        pic("kpi%d" % i, *ic, cut=(x0 + 20, 780), thresh=24)
        b = c.pill((x0 + 20) * K, V(595) - 0.07, 80 * K, 0.14, fill=PK)
        c.write(b, [[("KPI %02d" % (i + 1), 7, WHITE, F2)]])
        txt(x0, x1, 761, [[(s, 9.5, INK, F3)] for s in lab], h=0.45, spacing=1.1)

    # 4대 추진배경
    NB = c.rgb(500, 912); NC = c.rgb(500, 933)
    bg = [(455, 811, (602, 898, 698, 968), "안정적인 유지관리", ["지속적인 시스템 운영과", "예방적 유지관리로 안정성 확보"]),
          (829, 1198, (975, 896, 1068, 972), "신속한 장애복구", ["장애 발생 시 신속한 대응으로", "서비스 중단 최소화"]),
          (1216, 1580, (1362, 898, 1440, 972), "무중단 서비스", ["언제 어디서나 끊김 없는", "서비스 제공"]),
          (1597, 1950, (1752, 898, 1836, 970), "업무추진 환경변화 대응", ["비즈니스 및 기술 환경 변화에", "유연하게 대응"])]
    for i, (x0, x1, ic, ttl, desc) in enumerate(bg):
        box(c.rrect, x0, 888, x1, 1082, adj=0.08, fill=WHITE, line=LN, lw=0.75)
        pic("bg%d" % i, *ic, cut=(x0 + 100, 1070), thresh=24)
        d = 58 * K
        o = c.oval((x0 + 17) * K, V(933) - d / 2, d, d, fill=NB)
        c.write(o, [[("%02d" % (i + 1), 8.5, NC, F3)]])
        txt(x0, x1, 991, [[(ttl, 9, INK, F3)]], h=0.3)
        txt(x0, x1, 1040, [[(s, 7, GRAY, F2)] for s in desc], h=0.4, spacing=1.2)
