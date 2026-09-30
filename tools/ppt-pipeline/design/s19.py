"""19쪽 — 유지보수 관리 체계 (3/5) 클라우드 전환 (시안 13번)."""
from lib import *


def build(c):
    title_font = F3
    for sh in c.s.shapes:
        if sh.name == "TextBox 80":
            for r in sh.text_frame.paragraphs[0].runs:
                ea = r._r.find(".//" + qn("a:ea"))
                title_font = (ea.get("typeface") if ea is not None else None) or r.font.name or F3
    c.keep_only("TextBox 79")

    c.vmap(168, 1.30, 1083, 7.00)
    Z = c.Z

    def cyan():
        best, bv = (90, 225, 245), -999
        for x in range(640, 1050, 2):
            for y in range(995, 1030, 3):
                r, g, b = c.D.getpixel((int(x * Z), int(y * Z)))
                v = g + b - 2 * r - abs(g - b)
                if v > bv: best, bv = (r, g, b), v
        return RGBColor(*best)

    TXT = NAVY
    BODY = hexrgb("1F2F55")
    DOT = c.rgb(1334, 338) if sum(c.D.getpixel((int(1334 * Z), int(338 * Z)))) < 600 else hexrgb("2B6DE8")
    LN = c.rgb(1600, 207)
    LN = hexrgb("BBD3F5")

    def box(x0, y0, x1, y1, adj, **kw):
        """위아래를 세로 대응으로 늘린 상자."""
        t = c.cy(y0); h = c.cy(y1) - t
        return c.rrect(x0 * K, t, (x1 - x0) * K, h, adj=adj, **kw), t, t + h

    def dot(g, x, y, r=4):
        c.oval(g.X(x - r), g.Y(y - r), 2 * r * K, 2 * r * K, fill=DOT)

    # 제목
    c.text(48 * K, c.cy(168) - 0.3, 8.0, 0.6,
           [[("클라우드 전환 경험과 높은 이해도를 기반으로 한 ", 17.5, TXT, title_font), ("안정적 관리", 17.5, BLUE, title_font)]], LEFT)

    # ── 왼쪽 큰 상자 ──
    box(38, 243, 1223, 1075, 0.03, fill=WHITE, line=LN, lw=1.0)
    g = c.grp(220, 282)
    HB = c.rgb(400, 270)
    tab = c.shape(MSO_SHAPE.PENTAGON, g.X(38), g.Y(220), 619 * K, 62 * K, fill=HB, adj=0.35)
    c.pic(c.crop("hcloud", 60, 228, 124, 276, cut=(130, 250)), g.X(60), g.Y(228), 64 * K)
    c.text(g.X(138), g.Y(220), 480 * K, 62 * K, [[("클라우드 전환 수행 이력 및 이해도", 11.5, WHITE, F3)]], LEFT)

    g = c.grp(300, 340)
    c.text(g.X(63), g.Y(300), 600 * K, 40 * K, [[("전환 사업을 직접 수행한 유지관리 사업자", 11, TXT, F3)]], LEFT)

    # 전환 사업 이력 상자
    BG1 = c.rgb(300, 620)
    _, t1, b1 = box(62, 353, 1200, 692, 0.06, fill=BG1)
    g = c.grp(353, 692)
    ill = c.pic(c.crop("team", 790, 262, 1200, 692, cut=(800, 640)), 790 * K, 0, 410 * K)
    ill.top = Inches(b1) - ill.height
    c.write(c.pill(g.X(82), g.Y(367), 538 * K, 43 * K, fill=c.rgb(95, 388)),
            [[("클라우드 전환 사업 1·2차 직접 수행 (2024 ~ 2025)", 8, WHITE, F3)]])
    c.line(g.X(97), g.Y(428), g.X(97), g.Y(567), LN, 1.0)
    CB = c.rgb(140, 464)
    for cyy, a, b_, rows in ((464, "1차", "(2024)", ["기반 전환 클라우드 아키텍처 구성", "공통서비스 전환(인증·파일·연계·결재·기안문)"]),
                             (567, "2차", "(2025)", ["단위업무 91종 일괄 전환 (공통 54 · 개별 37)", "신구 시스템 병행운영 완료"])):
        c.oval(g.X(88), g.Y(cyy - 9), 18 * K, 18 * K, fill=WHITE, line=CB, lw=2.0)
        c.write(c.oval(g.X(126), g.Y(cyy - 40), 80 * K, 80 * K, fill=CB),
                [[(a, 9, WHITE, F3)], [(b_, 7, WHITE, F2)]], spacing=0.9)
        for k, tx in enumerate(rows):
            yy = cyy - 18 + k * 38
            dot(g, 228, yy, 3.5)
            c.text(g.X(248), g.Y(yy - 17), 520 * K, 34 * K, [[(tx, 7.5, BODY, F2)]], LEFT)
    c.line(g.X(225), g.Y(521), g.X(752), g.Y(521), LN, 0.75)
    c.line(g.X(100), g.Y(627), g.X(752), g.Y(627), LN, 0.75)
    c.pic(c.crop("mcloud", 86, 635, 146, 683, cut=(150, 660)), g.X(86), g.Y(635), 60 * K)
    c.text(g.X(157), g.Y(640), 640 * K, 36 * K,
           [[("청주시 전산실 ", 7.5, BODY, F2), ("온프레미스 프라이빗 클라우드", 7.5, TXT, F3), (" MSA 구조로 재설계·구축", 7.5, BODY, F2)]], LEFT)

    # 두 카드
    chk = c.crop("chk", 84, 798, 106, 821, cut=(110, 800))
    HB2 = c.rgb(300, 760)
    g = c.grp(775, 945)
    for x0, x1 in ((62, 612), (632, 1199)):
        box(x0, 715, x1, 953, 0.05, fill=WHITE, line=LN, lw=1.0)
    MS = 1.0
    c.pic(c.crop("man", 415, 775, 610, 946, cut=(425, 785)), g.X(610 - 195 * MS), g.Y(946 - 171 * MS), 195 * MS * K)
    c.pic(c.crop("docs", 963, 768, 1194, 947, cut=(955, 790)), g.X(963), g.Y(768), 231 * K)
    # 오린 그림에 딸려 온 시안 글자 조각을 바탕색으로 덮는다
    c.rect(g.X(412), g.Y(795), 40 * K, 75 * K, fill=WHITE)
    c.rect(g.X(958), g.Y(905), 48 * K, 32 * K, fill=WHITE)
    for (x0, x1, hx0, hx1, ico, tx, title, cx, tx0, rows) in (
            (62, 612, 71, 610, (85, 726, 136, 762), 160, "전환인력 = 유지관리인력", 85, 113,
             [(808, "전환 사업 참여 인력을 본 유지관리에 투입"), (853, "서비스 경계·API·연계 구조 설계 단계부터 보유"), (898, "별도 인수인계 없이 즉시 안정운영")]),
            (632, 1199, 639, 1197, (658, 724, 692, 762), 720, "설계 산출물 · 소스 보유", 655, 684,
             [(801, "MSA 서비스 분해도"), (840, "API 게이트웨이 라우팅 정보"), (880, "컨테이너 구성 정보 · 배포 스크립트"), (920, "30여 종 연계 인터페이스 규격서·모듈 소스")])):
        hy = c.cy(715) + 1 * K
        c.rrect(hx0 * K, hy, (hx1 - hx0) * K, 52 * K, adj=0.2, fill=HB2)
        nm = "hi%d" % x0
        c.pic(c.crop(nm, ico[0], ico[1], ico[2], ico[3], cut=(ico[2] + 8, 743)), ico[0] * K, hy + (ico[1] - 716) * K, (ico[2] - ico[0]) * K)
        c.text(tx * K, hy, 400 * K, 52 * K, [[(title, 8.5, WHITE, F3)]], LEFT)
        for yy, s in rows:
            c.pic(chk, g.X(cx), g.Y(yy - 11), 22 * K)
            c.text(g.X(tx0), g.Y(yy - 16), 360 * K, 32 * K, [[(s, 7, BODY, F2)]], LEFT)

    # 결론 띠
    BN = c.rgb(700, 1040)
    _, t, b = box(62, 972, 1200, 1051, 0.2, fill=BN)
    g = c.grp(972, 1051)
    c.pic(c.crop("target", 225, 980, 292, 1044, cut=(215, 1010)), g.X(225), g.Y(980), 67 * K)
    tb = c.text(g.X(337), g.Y(975), 760 * K, 72 * K,
                [[("직접 전환 경험 기반, ", 12, WHITE, F3), ("가장 빠르고 정확한 시스템 관리", 12, cyan(), F3)]], LEFT)
    for r in tb.text_frame.paragraphs[0].runs:
        r.font.italic = True

    # ── 오른쪽 네 카드 ──
    BGR = c.rgb(1500, 395)
    NB = c.rgb(1285, 270)
    cards = (
        (207, 409, "01", 252, "컨테이너·오케스트레이션 관리", 1347, [(302, "자원 기준값·최대치 관리"), (338, "오토스케일링 · 헬스체크"), (373, "이미지 버전 관리")], (1700, 222, 1956, 403)),
        (427, 636, "02", 471, "CI/CD 기반 무중단 배포", 1347, [(522, "변경된 컨테이너만 빌드 · 배포"), (559, "영향범위 최소화"), (596, "독립배포 · 롤백")], (1700, 445, 1956, 631)),
        (652, 851, "03", 698, "통합 모니터링·장애 대응", 1347, [(751, "API 게이트웨이 측정치"), (784, "로그 분석"), (816, "Circuit Breaker")], (1690, 665, 1956, 846)),
        (869, 1055, "04", 913, "부하·자원 관리", 1352, [(961, "WEB/WAS VM Scale-out"), (992, "DB Scale-up"), (1022, "성능 기준선(Baseline)·자원 사용률 정기 점검")], (1712, 876, 1956, 1046)),
    )
    for y0, y1, no, ty, title, tx, rows, il in cards:
        box(1246, y0, 1966, y1, 0.1, fill=BGR, line=LN, lw=1.0)
        g = c.grp(y0, y1)
        c.pic(c.crop("r" + no, il[0], il[1], il[2], il[3], cut=(1680, (y0 + y1) // 2)), g.X(il[0]), g.Y(il[1]), (il[2] - il[0]) * K)
        if no == "01":
            c.rect(g.X(1697), g.Y(228), 26 * K, 48 * K, fill=BGR)
        c.write(c.oval(g.X(1272), g.Y(ty - 30), 60 * K, 60 * K, fill=NB), [[(no, 10, WHITE, F3)]])
        c.text(g.X(tx), g.Y(ty - 24), 420 * K, 48 * K, [[(title, 10, TXT, F3)]], LEFT)
        for yy, s in rows:
            dot(g, 1334, yy, 3.5)
            c.text(g.X(1353), g.Y(yy - 16), 370 * K, 32 * K, [[(s, 7 if len(s) > 25 else 7.5, BODY, F2)]], LEFT)

    # 주석
    g = c.grp(1068, 1098)
    c.pic(c.crop("info", 1244, 1067, 1276, 1099, cut=(1282, 1083)), g.X(1244), g.Y(1067), 32 * K)
    c.text(g.X(1290), g.Y(1068), 640 * K, 30 * K,
           [[("전환 사업 1·2차 설계 기준 유지, 청주시 클라우드 인프라 운영 기준과 연계 관리", 7, BODY, F2)]], LEFT)
