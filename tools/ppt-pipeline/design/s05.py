"""5쪽 — 업무지원포털시스템의 발전과정 (2차 시안 design_ppt2/s05.png).

본문은 시안 y235~1065 를 1.62~7.02in 로 늘려 놓는다(상자는 늘린 좌표, 글·그림은 크기 그대로 중심만 옮김).
글은 원래 장표 문구를 쓴다(시안의 대봉자문·효과 홍보·통새업무·대민/개편·관련 등은 GPT 오기).
"""
from lib import *

KEYFONT = "G마켓 산스 TTF Bold"


def build(c):
    # 머리말 글(TextBox 85)과 슬라이드 밖 메모만 남긴다
    c.keep_only("TextBox 85", "웃는 얼굴 74")
    c.vmap(235, 1.62, 1065, 7.02)
    V = c.cy

    def box(fn, x0, y0, x1, y1, **kw):
        return fn(x0 * K, V(y0), (x1 - x0) * K, V(y1) - V(y0), **kw)

    def pic(name, x0, y0, x1, y1, cut=None, thresh=45):
        p = c.crop(name, x0, y0, x1, y1, cut=cut, cut_thresh=thresh)
        return c.pic(p, x0 * K, V((y0 + y1) / 2.0) - (y1 - y0) * K / 2.0, (x1 - x0) * K)

    def txt(x0, x1, yc, lines, align=CENTER, h=0.4, **kw):
        return c.text(x0 * K, V(yc) - h / 2.0, (x1 - x0) * K, h, lines, align, **kw)

    def dark(x0, y0, x1, y1):
        im = c.D.crop((int(x0 * c.Z), int(y0 * c.Z), int(x1 * c.Z), int(y1 * c.Z)))
        return RGBColor(*min(im.getdata(), key=sum))

    def bullets(xb, xt, rows, size, color, font=F2, xe=None):
        """rows = [(y, 글, 첫줄여부)] — 줄마다 글상자. 첫 줄에만 • ."""
        for y, s, first in rows:
            if first:
                txt(xb - 6, xb + 14, y, [[("•", size, color, font)]], h=0.3)
            txt(xt, xe or (xt + 600), y, [[(s, size, color, font)]], LEFT, h=0.3)

    c.background(1000, 210)

    NAVY_T = dark(410, 385, 600, 430)        # 큰 제목 남색
    SUBC = dark(415, 440, 580, 478)          # (2004 ~ ) 옅은 남색
    BODY = dark(230, 585, 590, 612)          # 본문 글
    LBL = dark(85, 590, 165, 620)            # 서비스 등 라벨
    BLUE_T = dark(1380, 510, 1840, 548)      # 통합 파랑

    # ── 키메시지 ──
    km = c.text(0.20, 1.03, 10.43, 0.5, [[("업무지원포털시스템", 23, hexrgb("2070E8"), KEYFONT),
                                         ("의 발전과정", 23, hexrgb("0B2E6B"), KEYFONT)]])
    km.name = "키메시지"

    # ── 왼쪽 큰 판 (행정정보공유 · 행정포털) ──
    box(c.rrect, 50, 237, 1228, 967, adj=0.03, fill=c.rgb(100, 400), line=c.rgb(49, 600), lw=0.75)
    ch1 = box(lambda l, t, w, h, **kw: c.shape(MSO_SHAPE.CHEVRON, l, t, w, h, **kw),
              182, 262, 705, 338, fill=c.rgb(250, 285), adj=0.35)
    ch2 = box(lambda l, t, w, h, **kw: c.shape(MSO_SHAPE.CHEVRON, l, t, w, h, **kw),
              710, 262, 1192, 338, fill=c.rgb(1100, 285), adj=0.35)
    txt(182, 705, 300, [[("행정정보공유", 16, NAVY_T, F3)]])
    txt(710, 1192, 300, [[("행정포털", 16, NAVY_T, F3)]])
    c.line(680 * K, V(380), 680 * K, V(935), c.rgb(680, 600), 0.75)

    # 인물 + 제목
    pic("p1", 178, 365, 392, 501, cut=(185, 372), thresh=24)
    txt(415, 670, 408, [[("이력 중심", 17.5, NAVY_T, F3)]], LEFT, h=0.45)
    txt(415, 670, 458, [[("(2004  ~ )", 13.5, SUBC, F3)]], LEFT, h=0.4)
    pic("p2", 704, 360, 922, 501, cut=(712, 368), thresh=24)
    txt(940, 1215, 408, [[("틈새업무 포털", 17.5, NAVY_T, F3)]], LEFT, h=0.45)
    txt(940, 1215, 458, [[("(2006 - 2013)", 13.5, SUBC, F3)]], LEFT, h=0.4)

    # 띠 + 흰 상자
    BAND = c.rgb(640, 535)
    for x0, x1, t in ((146, 664, "청주시 내부 공유기반 마련"), (697, 1203, "행정효율성 제공")):
        box(lambda l, t_, w, h, **kw: c.shape(MSO_SHAPE.ROUND_2_SAME_RECTANGLE, l, t_, w, h, **kw),
            x0, 506, x1, 566, fill=BAND, adj=[0.25, 0])
        txt(x0, x1, 534, [[(t, 12, NAVY_T, F3)]])
    WH = c.rgb(400, 700)
    box(c.rrect, 184, 563, 664, 933, adj=0.03, fill=WH, line=c.rgb(400, 653), lw=0.5)
    box(c.rrect, 697, 563, 1203, 933, adj=0.03, fill=WH, line=c.rgb(400, 653), lw=0.5)
    DIV = c.rgb(400, 653)
    for y in (654, 746, 839):
        c.line(208 * K, V(y), 634 * K, V(y), DIV, 0.75)
    for y in (663, 733, 835):
        c.line(730 * K, V(y), 1172 * K, V(y), DIV, 0.75)

    # 왼쪽 라벨
    TILE = c.rgb(80, 625)
    for y0, y1, lab in ((570, 646, ["서비스"]), (654, 738, ["대상", "정보"]),
                        (747, 831, ["기술", "관리"]), (840, 926, ["문화"])):
        box(c.rrect, 71, y0, 183, y1, adj=0.15, fill=TILE)
        txt(71, 183, (y0 + y1) / 2.0, [[(s, 10, LBL, F3)] for s in lab], h=0.5, spacing=1.05)

    S = 9
    bullets(219, 236, [(599, "행정정보이용, 행정관제, 대량자료,", True), (628, "결과 통보 서비스", False),
                       (684, "제증명, 건축, 위생, 토지, 세무,", True), (716, "자동차 등 7개분야", False),
                       (776, "행정정보 공유 기반", True), (808, "정보 공유 이력 관리", True),
                       (868, "정보 공유 기반 마련", True), (900, "감사 및 증적 자료 생성", True)],
            S, BODY, xe=660)
    bullets(746, 763, [(596, "청주시 인트라넷", True), (629, "맞춤형 및 업무지원 포털", True),
                       (693, "행정 및 공공정보", True),
                       (766, "SSO (Single sign On) 단일 ID", True), (798, "로그인 체계 마련", False),
                       (866, "행정 업무 효율화", True), (899, "아침을 여는 시스템", True)],
            S, BODY, xe=1195)

    # ── 오른쪽 판 (업무지원포털) ──
    box(c.rrect, 1247, 237, 1953, 967, adj=0.03, fill=c.rgb(1950, 400), line=c.rgb(1230, 400), lw=0.75)
    box(lambda l, t, w, h, **kw: c.shape(MSO_SHAPE.ROUND_2_SAME_RECTANGLE, l, t, w, h, **kw),
        1247, 237, 1953, 320, fill=c.rgb(1250, 245), adj=[0.2, 0])
    txt(1247, 1953, 278, [[("업무지원포털", 18.5, WHITE, F3)]], h=0.45)
    pic("p3", 1280, 350, 1480, 492, cut=(1286, 356), thresh=24)
    txt(1500, 1950, 385, [[("단일 플랫폼", 17.5, NAVY_T, F3)]], LEFT, h=0.45)
    txt(1500, 1950, 442, [[("및 기능개편 (2014 ~)", 17.5, NAVY_T, F3)]], LEFT, h=0.45)
    box(c.rrect, 1276, 500, 1927, 559, adj=0.3, fill=c.rgb(1300, 560))
    txt(1276, 1927, 529, [[("행정정보공유 및 행정포털 통합", 13, BLUE_T, F3)]])
    box(c.rrect, 1276, 569, 1927, 945, adj=0.05, fill=c.rgb(1600, 700))
    bullets(1341, 1360, [(607, "행정정보 공유 및 행정포털 서비스", True), (641, "고도화 (메인 개편)", False),
                         (686, "제증명, 건축, 위생, 토지 등 7개 분야", True),
                         (726, "전자정부 표준 플랫폼으로 표준화", True),
                         (765, "청주시 업무지원 대표 관문 시스템으로", True), (799, "고도화", False)],
            10.5, WHITE, F3, xe=1920)
    box(c.rrect, 1300, 836, 1905, 927, adj=0.15, fill=c.rgb(1900, 880))
    pic("mega", 1326, 846, 1400, 918, cut=(1310, 882), thresh=20)
    txt(1418, 1900, 864, [[("(2024~2025, 클라우드 전환) 프라이빗", 10, BODY, F2)]], LEFT, h=0.3)
    txt(1418, 1900, 897, [[("클라우드 기반으로 전면 전환 구축", 10, BODY, F2)]], LEFT, h=0.3)

    # ── 아래 강조 띠 ──
    PK = dark(470, 1015, 1530, 1055)
    box(c.rrect, 400, 1003, 1600, 1063, adj=0.12, fill=c.rgb(402, 1030), line=PK, lw=1.0)
    txt(400, 1600, 1033, [[("2004년부터 구축 및 유지관리사업 주관사로 빠짐없이 참여", 16, PK, F3)]], h=0.4)
