"""11쪽 — 안정성 확보 (시안 6번).
담당자 사진(Picture 6)·solideos 로고(그림 116)는 원래 장표 도형을 남겨 시안 자리로 옮긴다."""
from lib import *

E = 914400
INK = hexrgb("1A2B4F")
GRAY = hexrgb("5F7496")


def _find(shapes, name):
    for sh in shapes:
        if sh.name == name:
            return sh
        if sh.shape_type == 6:
            r = _find(sh.shapes, name)
            if r is not None:
                return r
    return None


def build(c):
    # ── 원래 도형에서 읽어 둘 것 ──
    title_font = F3
    t = _find(c.s.shapes, "직사각형 76")
    if t is not None:
        for r in t.text_frame.paragraphs[0].runs:
            ea = r._r.find(".//" + qn("a:ea"))
            title_font = (ea.get("typeface") if ea is not None else None) or r.font.name or F3
    # 실물 사진·로고는 그룹 밖(최상위)으로 꺼내 남긴다
    keep = {}
    for nm in ("Picture 6", "그림 116"):
        sh = _find(c.s.shapes, nm)
        keep[nm] = (sh._element, sh.width / float(sh.height))
        sh._element.getparent().remove(sh._element)
    c.remove("그룹 22", "그룹 21", "그룹 20")
    c.background(1000, 225)

    BL = c.rgb(52, 245)            # ACT 파랑
    DEEP = c.rgb(1180, 590)        # 남색 알약
    LN = hexrgb("C5D8F3")
    PANEL = c.rgb(800, 345)        # 소제목 띠
    HEAD = c.rgb(1200, 262)        # ACT 머리 띠
    SOFT = c.rgb(1100, 1040)       # 속 카드
    X0, X1 = 40, 1960

    # ── 전략 띠 ──
    bt, bh = 0.98, 0.44
    c.rrect(X0 * K, bt, (X1 - X0) * K, bh, adj=0.3, fill=c.rgb(1500, 175))
    tag = c.shape(MSO_SHAPE.PENTAGON, X0 * K, bt, 293 * K, bh, fill=c.rgb(200, 150), adj=[0.25])
    c.pic(c.crop("target", 62, 140, 132, 210, cut=(140, 150), cut_thresh=60), 62 * K, bt + bh / 2 - 35 * K, 70 * K)
    c.text(150 * K, bt, 130 * K, bh, [[("전략 1", 15.5, WHITE, F3)]], LEFT)
    PK = c.rgb(60, 200)
    c.text(362 * K, bt, 900 * K, bh, [[("무엇보다도 ", 15.5, INK, title_font), ("안정성 확보", 15.5, PK, title_font),
                                       ("가 ", 15.5, INK, title_font), ("최우선", 15.5, PK, title_font), (" 입니다.", 15.5, INK, title_font)]], LEFT)

    def card(top, bot, act, title):
        c.rrect(X0 * K, top, (X1 - X0) * K, bot - top, adj=0.04, fill=WHITE, line=LN, lw=1.0)
        hh = 0.32
        c.shape(MSO_SHAPE.ROUND_2_SAME_RECTANGLE, X0 * K, top, (X1 - X0) * K, hh, fill=HEAD, adj=[0.3, 0])
        c.shape(MSO_SHAPE.ROUND_1_RECTANGLE, X0 * K, top, 120 * K, hh, fill=BL, adj=[0])
        tri = c.shape(MSO_SHAPE.RIGHT_TRIANGLE, 158 * K, top, 82 * K, hh, fill=BL)
        c.rect(X0 * K, top, 120 * K, hh, fill=BL)
        c.text(X0 * K, top, 165 * K, hh, [[(act, 14, WHITE, F3)]])
        c.text(255 * K, top, 700 * K, hh, [[(title, 12.5, INK, F3)]], LEFT)
        return top + hh

    def pic_c(name, x0, y0, x1, y1, yc, cut=None, thresh=45):
        """시안 조각을 가로는 제자리, 세로는 중심 yc(in) 에."""
        p = c.pic(c.crop(name, x0, y0, x1, y1, cut=cut, cut_thresh=thresh), x0 * K, 0, (x1 - x0) * K)
        p.top = int(yc * E - p.height / 2)
        return p

    def sub_head(x0, x1, top, icon, label):
        h = 0.27
        c.rrect(x0 * K, top, (x1 - x0) * K, h, adj=0.25, fill=PANEL)
        pic_c(icon[0], icon[1], icon[2], icon[3], icon[4], top + h / 2, cut=(icon[1] + 1, icon[2] + 1), thresh=30)
        c.text((x0 + 73) * K, top, 400 * K, h, [[(label, 10, INK, F3)]], LEFT)
        return top + h

    # ═══ ACT.1 ═══
    T1, B1 = 1.53, 4.18
    y = card(T1, B1, "ACT.1", "핵심인력 투입")
    bt1, bb1 = y + 0.08, B1 - 0.1                # 본문 범위
    H = bb1 - bt1

    # 인물: 실물 사진
    c.rrect(62 * K, bt1, 243 * K, H, adj=0.05, fill=c.rgb(280, 330))
    el, ar = keep["Picture 6"]
    c.tree.append(el)
    ph = _find(c.s.shapes, "Picture 6")
    pw = 1.2; phh = pw / ar
    ph.width, ph.height = int(pw * E), int(phh * E)
    ph.left = int((62 + 243 / 2.0) * K * E - ph.width / 2); ph.top = int((bt1 + H / 2) * E - ph.height / 2)

    ym = lambda f: bt1 + H * f
    c.text(340 * K, ym(0.19) - 0.17, 300 * K, 0.34, [[("이도훈 ", 16, INK, F3), ("차장", 11.5, INK, F3)]], LEFT)
    c.text(343 * K, ym(0.35) - 0.12, 300 * K, 0.24, [[("운영사업 18년", 10, INK, F2)]], LEFT)
    c.write(c.pill(331 * K, ym(0.52) - 0.15, 255 * K, 0.30, fill=c.rgb(345, 500)), [[("현재 유지관리 담당자", 9, BL, F3)]])
    el, ar = keep["그림 116"]
    c.tree.append(el)
    lg = _find(c.s.shapes, "그림 116")
    lw_ = 1.2
    lg.width, lg.height = int(lw_ * E), int(lw_ / ar * E)
    lg.left = int(343 * K * E); lg.top = int(ym(0.78) * E - lg.height / 2)

    c.line(611 * K, bt1, 611 * K, bb1, LN, 0.75)
    c.line(1037 * K, bt1, 1037 * K, bb1, LN, 0.75)

    # 주요 이력
    y = sub_head(625, 1022, bt1, ("ic_car", 645, 312, 682, 348), "주요 이력")
    items = [("행정포털 유지관리", "2006 ~ 2009"), ("행정정보공유 구축", "2010"), ("행정포털 유지관리", "2012 ~ 현재"), ("31개 연계시스템 채널 유지", None)]
    step = (bb1 - y - 0.06) / 3.55
    ys = [y + 0.16 + step * i for i in range(4)]
    c.line(657 * K, ys[0], 657 * K, ys[3], BL, 1.25)
    for i, (a, b) in enumerate(items):
        c.oval(657 * K - 0.04, ys[i] - 0.04, 0.08, 0.08, fill=BL)
        c.text(699 * K, ys[i] - 0.1, 320 * K, 0.2, [[(a, 8.5, INK, F3)]], LEFT)
        if b:
            c.text(699 * K, ys[i] + 0.1, 320 * K, 0.2, [[(b, 9, GRAY, F2)]], LEFT)
            c.line(692 * K, ys[i] + step * 0.72, 1015 * K, ys[i] + step * 0.72, LN, 0.5)

    # 핵심 프로세스
    y = sub_head(1050, 1944, bt1, ("ic_gear", 1065, 312, 1102, 348), "핵심 프로세스")
    c.rrect(1050 * K, y + 0.04, 894 * K, bb1 - y - 0.04, adj=0.04, fill=c.rgb(1300, 640))
    yi = y + 0.04 + (bb1 - y - 0.04) * 0.36
    yp = bb1 - 0.36
    for i, (x0, x1, px, lab) in enumerate(((1075, 1290, 1068, ("현 운영담당자", "업무 지속")), (1388, 1600, 1381, ("인수위험", "Zero")),
                                           (1703, 1917, 1696, ("안정적인", "유지보수")))):
        pic_c("proc%d" % i, x0, 365, x1, 537, yi, cut=(x0 + 2, 368), thresh=28)
        b = c.rrect(px * K, yp - 0.24, 229 * K, 0.48, adj=0.3, fill=DEEP)
        c.write(b, [[(lab[0], 9, WHITE, F3)], [(lab[1], 9, WHITE, F3)]])
    for ax in (1310, 1621):
        c.shape(MSO_SHAPE.RIGHT_ARROW, ax * K, yi - 0.12, 55 * K, 0.24, fill=c.rgb(1350, 458), adj=[0.45, 0.55])

    # ═══ ACT.2 ═══
    T2, B2 = 4.30, 7.10
    y = card(T2, B2, "ACT.2", "철저한 장애관리")
    bt2, bb2 = y + 0.08, B2 - 0.1
    c.line(957 * K, bt2, 957 * K, bb2, LN, 0.75)

    # 시스템 안정화 (그래프)
    y = sub_head(66, 940, bt2, ("ic_bar", 92, 755, 133, 792), "시스템 안정화")
    gx0, gx1 = 162 * K, 920 * K
    gt, gb = y + 0.35, bb2 - 0.22
    c.text(80 * K, y + 0.06, 70 * K, 0.18, [[("장애율", 7.5, INK, F2)]], LEFT)
    for i in range(5):
        yy = gt + (gb - gt) * i / 4.0
        c.line(gx0, yy, gx1, yy, hexrgb("E3ECF8") if i < 4 else hexrgb("9DB4D6"), 0.5 if i < 4 else 0.75)
    c.line(gx0, gt - 0.05, gx0, gb, hexrgb("9DB4D6"), 0.75)
    pts = [(198, 0.18), (348, 0.40), (500, 0.57), (655, 0.71), (806, 0.80), (891, 0.85)]   # 시안 곡선 모양
    P = [(x * K, gt + (gb - gt) * f) for x, f in pts]
    fb = c.s.shapes.build_freeform(int(P[0][0] * E), int(P[0][1] * E))
    fb.add_line_segments([(int(a * E), int(b * E)) for a, b in P[1:]] + [(int(P[-1][0] * E), int(gb * E)), (int(P[0][0] * E), int(gb * E))], close=True)
    ar_ = fb.convert_to_shape(); ar_.shadow.inherit = False; ar_.name = "시안 그래프 면"
    ar_.fill.solid(); ar_.fill.fore_color.rgb = hexrgb("D9E8FC"); ar_.line.fill.background()
    for a, b in zip(P, P[1:]):
        c.line(a[0], a[1], b[0], b[1], BL, 1.75)
    for a in P:
        c.oval(a[0] - 0.04, a[1] - 0.04, 0.08, 0.08, fill=WHITE, line=BL, lw=1.25)
    b = c.rrect(P[-1][0] - 0.2, P[-1][1] - 0.36, 0.4, 0.22, adj=0.3, fill=BL)
    c.write(b, [[("Zero", 9, WHITE, F3)]])
    b = c.rrect(560 * K, gt - 0.12, 330 * K, 0.4, adj=0.35, fill=c.rgb(640, 845))
    c.write(b, [[("지난 20여년간 운영을 통한", 8, BL, F3)], [("시스템 안정화", 8, BL, F3)]])

    # 4단계 장애율 관리 전략
    y = sub_head(980, 1932, bt2, ("ic_shd", 1003, 753, 1040, 793), "4단계 장애율 관리 전략")
    ct, cb = y + 0.1, bb2
    CH = cb - ct
    cards = [(1002, 1213, (1062, 1172), "예방점검 및 교육", ("정기 점검을 통한", "사전 장애 예방")),
             (1248, 1452, (1300, 1402), "변경관리 수행", ("변경에 따른", "리스크 최소화")),
             (1486, 1688, (1538, 1652), "연계모니터링 강화", ("실시간 연계 상태 점검", "및 이상 징후 대응")),
             (1723, 1928, (1782, 1882), "장애이력관리", ("이력 분석을 통한", "재발 방지"))]
    for i, (x0, x1, (ix0, ix1), tt, ds) in enumerate(cards):
        c.rrect(x0 * K, ct, (x1 - x0) * K, CH, adj=0.08, fill=SOFT)
        pic_c("step%d" % i, ix0, 832, ix1, 932, ct + CH * 0.30, cut=(ix0 + 1, 930), thresh=26)
        c.write(c.oval(x0 * K + 0.01, ct - 0.02, 0.26, 0.26, fill=BL), [[("%02d" % (i + 1), 8, WHITE, F3)]])
        c.text(x0 * K, ct + CH * 0.57 - 0.11, (x1 - x0) * K, 0.22, [[(tt, 8.5, BL, F3)]])
        c.text(x0 * K, ct + CH * 0.78 - 0.17, (x1 - x0) * K, 0.34, [[(ds[0], 7, GRAY, F2)], [(ds[1], 7, GRAY, F2)]])
        if i < 3:
            nx = cards[i + 1][0]
            c.shape(MSO_SHAPE.CHEVRON, (x1 + nx) / 2.0 * K - 0.035, ct + CH * 0.30 - 0.06, 0.07, 0.12, fill=BL, adj=[0.75])
