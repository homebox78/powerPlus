"""14쪽 — 변화 실천 (시안 9번). 왼쪽 환경 분석 3카드 + 오른쪽 변경 관리 6단계."""
from lib import *


def _title_font(shapes):
    for sh in shapes:
        if sh.shape_type == 6:
            f = _title_font(sh.shapes)
            if f: return f
        elif sh.name == "직사각형 151":
            for r in sh.text_frame.paragraphs[0].runs:
                ea = r._r.find(".//" + qn("a:ea"))
                return (ea.get("typeface") if ea is not None else None) or r.font.name
    return None


def build(c):
    tfont = _title_font(c.s.shapes) or F3
    c.keep_only("TextBox 105")          # 머리 띠 글만 남긴다
    c.vmap(258, 1.66, 1060, 7.05)       # 두 패널이 본문 아래까지 차도록

    INK = c.rgb(560, 183)               # 짙은 남색 글
    TXT = hexrgb("22356B")

    def label(x, yc, w, runs, g, align=LEFT, h=0.3):
        return c.text(g.X(x), g.Y(yc) - h / 2, w * K, h, [runs], align)

    # ── 전략 띠 / ACT 띠 ──
    g = c.grp(152, 228)
    c.pill(g.X(32), g.Y(152), 980 * K, 76 * K, fill=c.rgb(900, 165))
    c.rect(g.X(32), g.Y(152), 60 * K, 76 * K, fill=c.rgb(60, 190))
    b = c.shape(MSO_SHAPE.PENTAGON, g.X(32), g.Y(152), 238 * K, 76 * K, fill=c.rgb(60, 190), adj=0.42)
    c.write(b, [[("전략 3", 16, WHITE, F3)]], margin=0)
    label(302, 190, 690, [("환경과 수요에 대응한 변화를 실천합니다.", 14.4, INK, tfont)], g)
    c.pill(g.X(1030), g.Y(152), 945 * K, 76 * K, fill=c.rgb(1900, 165))
    c.write(c.pill(g.X(1030), g.Y(152), 192 * K, 76 * K, fill=c.rgb(1060, 190)), [[("ACT.5", 14.5, WHITE, F3)]])
    label(1256, 190, 700, [("사용자 환경 변화 대응 체계 구축을 통한 능동적 대응", 11.6, INK, F3)], g)

    # ── 패널 틀 ──
    T, B = c.cy(258), c.cy(1060)
    HH = 77 * K
    LN = c.rgb(33, 700)
    for x0, x1, hx, title, ico in ((32, 947, 300, "사용자 업무 환경 분석 체계", (62, 270, 126, 325)),
                                   (970, 1968, 1500, "변경 관리 체계", (1003, 268, 1060, 328))):
        c.rrect(x0 * K, T + 0.1, (x1 - x0) * K, B - T - 0.1, adj=0.02, fill=c.rgb(x0 + 12, 700), line=LN, lw=0.75)
        hc = c.rgb(hx, 320)
        c.shape(MSO_SHAPE.ROUND_2_SAME_RECTANGLE, x0 * K, T, (x1 - x0) * K, HH, fill=hc, adj=[0.25, 0])
        ix0, iy0, ix1, iy1 = ico
        c.pic(c.crop("hico%d" % x0, ix0, iy0, ix1, iy1, cut=(ix0 - 6, (iy0 + iy1) // 2)),
              ix0 * K, T + (iy0 - 258) * K, (ix1 - ix0) * K)
        c.text((ix1 + 20) * K, T, 600 * K, HH, [[(title, 12.2, WHITE, F3)]], LEFT)

    # ── 왼쪽 카드 3개 ──
    BLUE1 = c.rgb(70, 406)
    BOXF, BOXL = c.rgb(745, 540), c.rgb(736, 470)
    cards = [
        (357, 578, 406, "사용자 PC 및 업무 환경 분석", [(463, "청주시청, 구청, 읍면동 등"), (502, "PC 사양 및 OS 버전")],
         (492, 382, 728, 572), (375, 555),
         [(404, (752, 390, 782, 420), 793, ["PC 사양"]), (458, (752, 443, 782, 473), 793, ["OS 버전"])], [432], (752, 487, 900, 533)),
        (597, 805, 642, "업무지원포털 시스템 환경 분석", [(699, "개발/실행 환경"), (737, "UI 플랫폼 이해")],
         (492, 615, 730, 782), (614, 782),
         [(643, (755, 630, 792, 657), 810, ["개발 환경"]), (696, (755, 681, 792, 711), 810, ["실행 환경"]),
          (749, (755, 733, 792, 765), 810, ["UI 플랫폼"])], [669, 722], None),
        (822, 1040, 870, "업무시스템 및 연계 환경 모니터링", [(930, "청주시 업무 시스템"), (968, "자치단체 표준 시스템")],
         (482, 838, 728, 1022), (847, 1015),
         [(893, (752, 874, 790, 910), 801, ["청주시", "업무 시스템"]), (967, (752, 945, 790, 985), 801, ["자치단체", "표준 시스템"])],
         [932], None),
    ]
    for n, (y0, y1, ty, title, bullets, pic, (by0, by1), rows, divs, extra) in enumerate(cards, 1):
        ct, cb = c.cy(y0), c.cy(y1)
        c.rrect(50 * K, ct, 878 * K, cb - ct, adj=0.08, fill=WHITE, line=c.rgb(40, 590), lw=0.5)
        g = c.grp(y0, y1)
        c.write(c.oval(g.X(61), g.Y(ty - 31), 62 * K, 62 * K, fill=BLUE1), [[(str(n), 17, WHITE, F3)]])
        label(145, ty, 360, [(title, 9.8, INK, F3)], g)
        for yy, tx in bullets:
            label(148, yy, 340, [("• " + tx, 8.7, TXT, F2)], g, h=0.25)
        px0, py0, px1, py1 = pic
        if n == 3:      # 제목 글자 끝이 그림 왼쪽 위에 걸려 있어 구름 부분만 따로 오린다
            c.pic(c.crop("pic3a", 540, py0, px1, 892, cut=(px1 - 2, py0 + 2), cut_thresh=18), g.X(540), g.Y(py0), (px1 - 540) * K)
            py0 = 892
        c.pic(c.crop("pic%d" % n, px0, py0, px1, py1, cut=(px0 + 2, py1 - 2), cut_thresh=18), g.X(px0), g.Y(py0), (px1 - px0) * K)
        c.rrect(g.X(735), g.Y(by0), 180 * K, (by1 - by0) * K, adj=0.1, fill=BOXF, line=BOXL, lw=0.5)
        for yy in divs:
            c.line(g.X(753), g.Y(yy), g.X(898), g.Y(yy), BOXL, 0.5)
        for ry, (ix0, iy0, ix1, iy1), tx, lines in rows:
            c.pic(c.crop("bi%d_%d" % (n, ry), ix0, iy0, ix1, iy1, cut=(ix0 + 1, iy0 + 1), cut_thresh=30), g.X(ix0), g.Y(iy0), (ix1 - ix0) * K)
            c.text(g.X(tx), g.Y(ry) - 0.2, 110 * K, 0.4, [[(t, 7, TXT, F2)] for t in lines], LEFT, spacing=1.0)
        if extra:
            ex0, ey0, ex1, ey1 = extra
            c.pic(c.crop("os%d" % n, ex0, ey0, ex1, ey1, cut=(ex0 + 1, ey0 + 1), cut_thresh=30), g.X(ex0), g.Y(ey0), (ex1 - ex0) * K)

    # ── 오른쪽: 3단계 화살 ──
    g = c.grp(360, 487)
    chev = [(990, 340, MSO_SHAPE.PENTAGON, "기능개선 사전검토", 1148, (1113, 372, 1188, 436)),
            (1312, 334, MSO_SHAPE.CHEVRON, "담당자 검토협의", 1480, (1428, 372, 1510, 434)),
            (1625, 330, MSO_SHAPE.CHEVRON, "기능개선 수행", 1793, (1763, 372, 1824, 434))]
    for x, w, kind, lab, cx, (ix0, iy0, ix1, iy1) in chev:
        fc = c.rgb(ix0 - 5, (iy0 + iy1) // 2)
        c.shape(kind, g.X(x), g.Y(360), w * K, 127 * K, fill=fc, adj=0.28)
        c.pic(c.crop("chv%d" % x, ix0, iy0, ix1, iy1, cut=(ix0 - 5, (iy0 + iy1) // 2), cut_thresh=60), g.X(ix0), g.Y(iy0), (ix1 - ix0) * K)
        label(cx - 150, 456, 300, [(lab, 8.5, WHITE, F3)], g, CENTER)

    # ── 오른쪽: STEP 카드 6개 ──
    PILL = c.rgb(1010, 540)
    CF, CL = c.rgb(1150, 600), c.rgb(990, 640)
    cols = [990, 1312, 1638]
    steps = [
        (516, 765, 0, ["기능개선사항 발생 및", "형상관리 등록"], (1045, 632, 1262, 762)),
        (516, 765, 1, ["세부사전검토"], (1340, 615, 1604, 762)),
        (516, 765, 2, ["관련 업무담당자 협의체 소집"], (1652, 615, 1940, 762)),
        (783, 1040, 0, ["전체의견수렴 및", "적용범위 설정"], (1020, 893, 1285, 1032)),
        (783, 1040, 1, ["기능개선작업", "소스코드 내역관리", "통합테스트"], (1335, 897, 1604, 1036)),
        (783, 1040, 2, ["운영시스템 적용 배포관리", "서비스 개시 안정화"], (1662, 897, 1942, 1032)),
    ]
    for i, (y0, y1, col, lines, (px0, py0, px1, py1)) in enumerate(steps, 1):
        x = cols[col]; ct, cb = c.cy(y0), c.cy(y1)
        c.rrect(x * K, ct, 308 * K, cb - ct, adj=0.06, fill=CF, line=CL, lw=0.5)
        c.pic(c.crop("step%d" % i, px0, py0, px1, py1, cut=(px0 + 1, py0 + 1), cut_thresh=22),
              px0 * K, cb - (y1 - py0) * K, (px1 - px0) * K)
        c.write(c.pill((x + 15) * K, ct + 7 * K, 108 * K, 35 * K, fill=PILL), [[("STEP %d" % i, 8.5, WHITE, F3)]])
        c.text((x + 22) * K, ct + 52 * K, 285 * K, 62 * K, [[(t, 8, INK, F3)] for t in lines], LEFT,
               anchor="top", spacing=1.05)
