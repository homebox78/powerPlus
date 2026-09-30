"""26쪽 — 기능 및 성능 개선 (1/2) (2차 시안 design_ppt2/s26.png). 글은 원래 장표 문구."""
from lib import *
from PIL import Image

KF = "G마켓 산스 TTF Bold"
NV = hexrgb("0B2E6B")      # 본문 남색
KB = hexrgb("2070E8")      # 키메시지 강조
BL = hexrgb("2F78E0")      # 예시 파랑(원래 장표)
PK = hexrgb("EC1C68")      # 강조 분홍(원래 장표)
LN = hexrgb("C9E1F8")      # 옅은 선


def _clear_box(path, Z, x0, y0, x1, y1, crop_x0, crop_y0):
    """오린 그림 안의 (시안 좌표) 영역을 투명하게 — 딸려 온 글자 조각 지우기."""
    im = Image.open(path).convert("RGBA"); px = im.load(); w, h = im.size
    for y in range(max(0, int((y0 - crop_y0) * Z)), min(h, int((y1 - crop_y0) * Z))):
        for x in range(max(0, int((x0 - crop_x0) * Z)), min(w, int((x1 - crop_x0) * Z))):
            px[x, y] = (255, 255, 255, 0)
    im.save(path)


def build(c):
    c.keep_only("TextBox 75")          # 머리말 제목만 남김
    c.background(1000, 240)
    c.vmap(250, 1.62, 1095, 7.02)

    # ── 키메시지 ──
    b = c.rect(0.20, 1.03, 10.43, 0.50, name="키메시지")
    c.write(b, [[("미래 성장을 위한 ", 23, NV, KF), ("선제적이고 지속적인 기능 개선", 23, KB, KF)]])

    # ── 위 카드 2장 ──
    g = c.grp(258, 450)
    cards = [
        (47, 990, "업무 · 법제도적 환경변화에 따른 개선",
         "기존 서비스와 관련된 업무 및 법제도적 환경 변화에 따라 기능 개선 요구 발생",
         "필수 관리 항목 제거/추가/변경, 개인정보보호법 개정에 따른 비식별화 처리 ", "등"),
        (1012, 1955, "기술 환경변화에 따른 개선",
         "안정적이고 지속적 서비스 운영을 위한 기술 환경 변화에 따른 개선 요구 발생",
         "패치 적용과 신규 OS 및 브라우저 적용 지원", ""),
    ]
    for x0, x1, head, l1, l2, tail in cards:
        w = (x1 - x0) * K
        c.rrect(g.X(x0), g.Y(258), w, 192 * K, adj=0.08, fill=hexrgb("F9FCFF"), line=hexrgb("A9CFF7"), lw=1.0)
        hb = c.shape(MSO_SHAPE.ROUND_2_SAME_RECTANGLE, g.X(x0), g.Y(258), w, 89 * K,
                     fill=c.rgb(500, 265), adj=[0.17, 0])
        c.write(hb, [[(head, 16, WHITE, F3)]])
        c.text(g.X(x0), g.Y(357), w, 83 * K,
               [[(l1, 9.5, NV, F2)],
                [("(예) ", 9.5, NV, F2), (l2, 9.5, BL, F2)] + ([(tail, 9.5, NV, F2)] if tail else [])],
               spacing=1.05)

    # ── 차이 분석 줄 ──
    g = c.grp(455, 700)
    p = c.crop("left", 125, 458, 572, 692, cut=(30, 470), cut_thresh=24)
    c.pic(p, g.X(125), g.Y(458), 447 * K)
    p = c.crop("right", 1376, 452, 1832, 692, cut=(1850, 470), cut_thresh=24)
    _clear_box(p, c.Z, 1370, 648, 1424, 700, 1376, 452)
    c.pic(p, g.X(1376), g.Y(452), 456 * K)
    gb = c.rrect(g.X(765), g.Y(490), 472 * K, 102 * K, adj=0.22, fill=hexrgb("F6FBFF"),
                 line=hexrgb("0B4EB5"), lw=2.25)
    c.write(gb, [[("차이(gap) 분석", 20, NV, F3)]])
    c.line(g.X(590), g.Y(638), g.X(1470), g.Y(638), hexrgb("B6D9FE"), 0.75)
    c.shape(MSO_SHAPE.ISOSCELES_TRIANGLE, g.X(986), g.Y(626), 28 * K, 12 * K, fill=hexrgb("B6D9FE"))
    c.text(g.X(540), g.Y(652), 940 * K, 40 * K,
           [[("현재와 변화 내용 분석을 통하여 수행해야 할 ", 14, NV, F3), ("범위 규명", 14, PK, F3)]])

    # ── 차원 육각형 줄 + 세부 요건 도출 ──
    g = c.grp(705, 865)
    HX = hexrgb("CCE7FD")
    for x0, x1, lab in ((258, 730, [("정보시스템 기능(SW) 차원", 12, NV, F2)]),
                        (770, 1230, [("업무적 차원", 12, NV, F2)]),
                        (1272, 1742, [("시스템 장비(HW) 차원", 12, NV, F2)])):
        h = c.shape(MSO_SHAPE.HEXAGON, g.X(x0), g.Y(712), (x1 - x0) * K, 75 * K, fill=HX, adj=[0.45, 1.155])
        c.write(h, [lab])
    for a, b2 in ((730, 770), (1230, 1272)):
        c.line(g.X(a), g.Y(750), g.X(b2), g.Y(750), hexrgb("A9D3F7"), 1.0)
    c.text(g.X(560), g.Y(800), 880 * K, 42 * K,
           [[("기능개선방안 세부 요건", 14, PK, F3), (" 도출", 14, NV, F3)]])
    c.line(g.X(520), g.Y(849), g.X(1485), g.Y(849), LN, 1.0)
    c.shape(MSO_SHAPE.ISOSCELES_TRIANGLE, g.X(986), g.Y(849), 28 * K, 12 * K, fill=LN).rotation = 180

    # ── 단계 띠 + STEP 카드 ──
    g = c.grp(866, 1092)
    bars = [(MSO_SHAPE.PENTAGON, 47, 690, hexrgb("D5EAFD"), "기능개선 사전검토", hexrgb("4E678D")),
            (MSO_SHAPE.CHEVRON, 683, 1325, hexrgb("C1E2FD"), "담당자 검토협의", NV),
            (MSO_SHAPE.CHEVRON, 1320, 1955, hexrgb("3A8BEF"), "기능개선 수행", WHITE)]
    for kind, x0, x1, col, lab, tc in bars:
        s = c.shape(kind, g.X(x0), g.Y(866), (x1 - x0) * K, 47 * K, fill=col, adj=0.5)
        c.write(s, [[(lab, 14, tc, F3)]])

    steps = [
        (47, 345, ["기능개선사항 발생 및", "형상관리 등록"], None, "변경계획 수립"),
        (375, 658, ["세부사전검토"], "(범위/영향성/사유/기능 등)", "보고"),
        (690, 980, ["관련 업무담당자", "관리 협의체 소집"], None, "상세분석 및 타당성 검토"),
        (1008, 1300, ["전체의견수렴 및 적용", "범위 설정"], None, "적용계획 수립"),
        (1330, 1625, ["기능개선작업"], "(소스코드 상세 내역)", "통합테스트 및 검증 결과 반영"),
        (1657, 1955, ["운영시스템 적용 및", "배포 관리"], None, "서비스 개시 및 안정화"),
    ]
    for i, (x0, x1, b1, sub, b2) in enumerate(steps):
        dark = i >= 4
        w = (x1 - x0) * K
        c.rrect(g.X(x0), g.Y(930), w, 162 * K, adj=0.06,
                fill=hexrgb("2E81ED") if dark else hexrgb("C3E4FC"),
                line=hexrgb("2A74DD") if dark else hexrgb("A9D3F7"), lw=0.75)
        c.text(g.X(x0), g.Y(932), w, 36 * K, [[("STEP %d" % (i + 1), 11, WHITE if dark else NV, F3)]])
        c.rrect(g.X(x0 + 9), g.Y(970), w - 18 * K, 114 * K, adj=0.13, fill=WHITE)
        bx = x0 + 18
        lines = [[(b1[0], 8, NV, F2)]]
        if len(b1) > 1:
            lines.append([(b1[1], 8, NV, F2)])
        if sub:
            lines.append([(sub, 7.5, NV, F2)])
        c.text(g.X(bx), g.Y(985), 10 * K, 22 * K, [[("•", 8, NV, F2)]])
        c.text(g.X(bx + 12), g.Y(983), (x1 - bx - 12) * K, 50 * K, lines, LEFT, anchor="top")
        c.text(g.X(bx), g.Y(1042), 10 * K, 22 * K, [[("•", 8, NV, F2)]])
        c.text(g.X(bx + 12), g.Y(1040), (x1 - bx - 12) * K, 25 * K, [[(b2, 7.5 if len(b2) > 14 else 8, NV, F2)]], LEFT, anchor="top")
        if i < 5:
            nx = steps[i + 1][0]
            cx = (x1 + nx) / 2.0
            c.shape(MSO_SHAPE.CHEVRON, g.X(cx - 11), g.Y(990), 22 * K, 42 * K, fill=hexrgb("8FC0F5"), adj=0.55)
