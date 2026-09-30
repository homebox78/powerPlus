"""29쪽 — 사용자 교육 (2차 시안 design_ppt2/s29.png).

글은 원래 장표(v0.65) 문구 그대로, 배치·색·그림은 시안.
본문이 두 큰 카드(좌 사용자 교육 방안 / 우 기술이전교육)라 세로는 한 배율(KV)로 늘려 1.62~7.02in 를 채운다.
"""
from PIL import Image, ImageDraw
from lib import *

TOP, BOT = 1.62, 7.02          # 본문 안내선
Y0, Y1 = 238, 1080             # 시안 본문(카드 위·아래)
KV = (BOT - TOP) / (Y1 - Y0)


def Y(y): return TOP + (y - Y0) * KV
def H(h): return h * KV
def X(x): return x * K


NAVYT = hexrgb("0B2E6B")
TXT = hexrgb("1C3561")
LBLUE = hexrgb("B3DEFD")
LINE2 = hexrgb("D6E8FA")


def blank(path, rects, col):
    """오린 그림 안의 글 조각을 바탕색으로 지운다(rects 는 시안 좌표, 그림 원점 기준 상대값 아님)."""
    im = Image.open(path).convert("RGB")
    return im


def patch(c, path, x0, y0, rects, col):
    im = Image.open(path).convert("RGB"); d = ImageDraw.Draw(im)
    for rx0, ry0, rx1, ry1 in rects:
        d.rectangle([(rx0 - x0) * c.Z, (ry0 - y0) * c.Z, (rx1 - x0) * c.Z, (ry1 - y0) * c.Z], fill=col)
    im.save(path)
    return path


def img(c, name, x0, y0, x1, y1, cut=None, rects=None, fillcol=None):
    p = c.crop(name, x0, y0, x1, y1, cut=cut)
    if rects:
        patch(c, p, x0, y0, rects, fillcol)
    w = (x1 - x0) * K; h = (y1 - y0) * K
    cy = Y((y0 + y1) / 2.0)
    return c.pic(p, X(x0), cy - h / 2, w)


def bullets(c, l, t, w, h, items, size=8, color=None, line_gap=None, anchor="top", font=F2):
    color = color or TXT
    lines = []
    for it in items:
        if isinstance(it, tuple):       # (첫 줄, 이어지는 줄)
            lines.append([("• " + it[0], size, color, font)])
            lines.append([("   " + it[1], size, color, font)])
        else:
            lines.append([("• " + it, size, color, font)])
    return c.text(l, t, w, h, lines, LEFT, anchor=anchor, wrap=True, spacing=line_gap)


def build(c):
    # 키메시지 서체
    kfont = "G마켓 산스 TTF Bold"
    for sh in c.s.shapes:
        if sh.name == "직사각형 11":
            r = sh.text_frame.paragraphs[0].runs[0]
            kfont = r.font.name or kfont
    c.keep_only("TextBox 92")
    c.background(1000, 1110)

    # ── 키메시지 ──
    km = c.text(0.20, 1.03, 10.43, 0.46, [[("현장 밀착형 ", 23, NAVYT, kfont),
                                          ("사용자 및 운영자 맞춤 교육", 23, hexrgb("2070E8"), kfont),
                                          (" 실시", 23, NAVYT, kfont)]])
    km.name = "키메시지"

    # ════ 왼쪽: 사용자 교육 방안 ════
    c.rrect(X(38), Y(238), 972 * K, H(842), adj=0.025, fill=hexrgb("F9FCFE"), line=LBLUE, lw=1.0)
    hd = c.shape(MSO_SHAPE.ROUND_2_SAME_RECTANGLE, X(38), Y(238), 972 * K, H(77), fill=hexrgb("3887F0"), adj=[0.25, 0])
    c.write(hd, [[("사용자 교육 방안", 16, WHITE, F3)]])

    # 청주시 카드
    c.rrect(X(58), Y(335), 437 * K, H(473), adj=0.04, fill=c.rgb(76, 409), line=hexrgb("DCEBF8"), lw=0.75)
    b = c.shape(MSO_SHAPE.PENTAGON, X(68), Y(345), 407 * K, H(53), fill=hexrgb("D0E8FD"), adj=0.35)
    c.write(b, [[("청주시", 14, hexrgb("163A73"), F3)]])
    img(c, "cj_teach", 72, 405, 318, 553, rects=[(300, 420, 318, 505)], fillcol=tuple(c.rgb(76, 409)))
    c.text(X(302), Y(430), 188 * K, H(75), [[("역할별 차별화된", 9.5, TXT, F2)], [("교육실시", 9.5, TXT, F2)]], LEFT)
    # 교육요구사항
    c.pill(X(75), Y(563), 395 * K, H(40), fill=hexrgb("E4F3FE"))
    c.oval(X(80), Y(571), 22 * K, 22 * K, fill=WHITE, line=hexrgb("1E5BB5"), lw=3)
    c.text(X(112), Y(563), 300 * K, H(40), [[("교육요구사항", 11, hexrgb("163A73"), F3)]], LEFT)
    c.rrect(X(75), Y(612), 395 * K, H(181), adj=0.08, fill=hexrgb("E9F4FD"))
    reqs = ["제도변경에 따른 업무프로세스 교육", "교육교재 지원", "사용자 및 운영자별 사용법 교육",
            ("전산시스템의 업무환경변화에 따른", "기술교육")]
    rows = [(612, 650), (650, 686), (686, 723), (723, 793)]
    for i, (it, (ra, rb)) in enumerate(zip(reqs, rows)):
        if i:
            c.line(X(90), Y(ra), X(455), Y(ra), WHITE, 1.0)
        if isinstance(it, tuple):
            ln = [[("• " + it[0], 8, TXT, F2)], [("   " + it[1], 8, TXT, F2)]]
        else:
            ln = [[("• " + it, 8, TXT, F2)]]
        c.text(X(92), Y(ra), 370 * K, H(rb - ra), ln, LEFT)

    # 제안사 카드
    c.rrect(X(497), Y(342), 493 * K, H(476), adj=0.04, fill=hexrgb("F7FCFF"), line=hexrgb("DCEBF8"), lw=0.75)
    hd = c.shape(MSO_SHAPE.ROUND_2_SAME_RECTANGLE, X(500), Y(345), 488 * K, H(58), fill=hexrgb("2F6AAE"), adj=[0.2, 0])
    c.write(hd, [[("제안사", 14, WHITE, F3)]])
    img(c, "jn_teach", 512, 418, 722, 565, rects=[(645, 540, 722, 565)], fillcol=(247, 252, 255))
    c.text(X(722), Y(430), 262 * K, H(75), [[("교육대상별 차별화된", 10, hexrgb("2174EF"), F3)],
                                             [("현장 밀착형 교육 실시", 10, hexrgb("2174EF"), F3)]], LEFT)
    c.text(X(640), Y(538), 300 * K, H(32), [[("사용자 교육 수용 방안", 10.5, hexrgb("163A73"), F3)]], LEFT)
    c.rrect(X(512), Y(585), 460 * K, H(218), adj=0.05, fill=hexrgb("3B75B4"))
    grp = [("운영자 그룹", "시스템 환경 및 제반 사항", "설정 등 관리자 기능 사용법"),
           ("사용자 그룹", "업무별 교육 지원", None),
           ("상담원 그룹", "상담 수행 시 필요사항 교육", None),
           ("전체", "신규개발부문에 대한 현행화 교육", None)]
    rows = [(588, 657), (657, 705), (705, 753), (753, 801)]
    for i, (g, a, b2) in enumerate(grp):
        ra, rb = rows[i]
        if i:
            c.line(X(530), Y(ra), X(955), Y(ra), hexrgb("6C9DCF"), 0.75)
        ln = [[("• " + g + " : ", 8.5, WHITE, F3), (a, 8.5, WHITE, F2)]]
        if b2:
            ln.append([("                       " + b2, 8.5, WHITE, F2)])
        c.text(X(528), Y(ra), 440 * K, H(rb - ra), ln, LEFT)

    # 교육대상 및 조직, 교육 형태
    c.oval(X(72), Y(828), 24 * K, 24 * K, fill=WHITE, line=hexrgb("1E5BB5"), lw=3)
    c.text(X(108), Y(820), 400 * K, H(40), [[("교육대상 및 조직, 교육 형태", 11, hexrgb("163A73"), F3)]], LEFT)
    cols = [(65, "교육 대상", ["주관기관 시스템 관리자", "업무부서 사용자", "상담요원"]),
            (377, "교육 조직", ["교육수행 조직 구성", "업무별 핵심사용자 지정", "본사 기술지원그룹 활용"]),
            (688, "교육 형태", [("정기교육 / 수시교육", "– 기능 추가 및 변경 시"), ("집합교육 / 방문교육", "– 사용대상 규모에 따라구분")])]
    for x0, head, items in cols:
        c.rrect(X(x0), Y(868), 295 * K, H(187), adj=0.05, fill=hexrgb("CCE8FC"))
        c.text(X(x0), Y(868), 295 * K, H(40), [[(head, 11, hexrgb("163A73"), F3)]])
        c.rrect(X(x0 + 3), Y(910), 289 * K, H(142), adj=0.05, fill=WHITE)
        bullets(c, X(x0 + 14), Y(916), 272 * K, H(132), items, size=8, anchor="middle", line_gap=1.3)

    # ════ 오른쪽: 기술이전교육 ════
    c.rrect(X(1030), Y(238), 937 * K, H(842), adj=0.025, fill=hexrgb("F7FBFE"), line=LBLUE, lw=1.0)
    hd = c.shape(MSO_SHAPE.ROUND_2_SAME_RECTANGLE, X(1030), Y(238), 937 * K, H(77), fill=hexrgb("235999"), adj=[0.25, 0])
    c.write(hd, [[("기술이전교육", 16, WHITE, F3)]])
    c.rrect(X(1048), Y(335), 900 * K, H(357), adj=0.04, fill=hexrgb("EFF7FD"))
    c.text(X(1048), Y(342), 900 * K, H(92), [[("업무지원포털시스템 운영에 필요한", 13.5, hexrgb("163A73"), F3)],
                                              [("기술이전교육으로 독자적인 운영능력 함양", 13.5, hexrgb("163A73"), F3)]])
    c.text(X(1048), Y(438), 900 * K, H(36), [[("유지보수 공동참여, 실무위주의 대면 전수, 지속적인 이전, 산출물 인계인수등", 9, hexrgb("2E4468"), F2)]])
    img(c, "tr_left", 1058, 492, 1336, 692)
    img(c, "tr_right", 1705, 492, 1948, 692)
    bx = c.rrect(X(1360), Y(538), 282 * K, H(136), adj=0.12, fill=WHITE, line=hexrgb("187CF3"), lw=2.25)
    c.write(bx, [[("효과적인", 14, hexrgb("0F2A55"), F3)], [("기술이전 추진", 14, hexrgb("0F2A55"), F3)]])
    img(c, "cap", 1583, 505, 1690, 585, cut=(1590, 510))

    cols = [(1050, "이전 대상 범위", ["하드웨어", "사용 소프트웨어", "네트워크 및 보안관련 장비", "시스템 운영지원 노하우", "장비 유지보수 운영 노하우"]),
            (1357, "기술이전 필수요소", [("개발자 및 운영자의", "기술습득 의지"), "체계적인 기술이전 방안", ("기술이전 대상자의", "적극적 참여")]),
            (1667, "기술이전 방법", ["유지보수 공동참여 유도", "실무위주의 교육훈련 실시", "지속적인 기술이전 수행", ("산출물 작성참여 및", "인계 인수")])]
    for x0, head, items in cols:
        c.rrect(X(x0), Y(712), 277 * K, H(258), adj=0.05, fill=WHITE, line=hexrgb("E1EDF8"), lw=0.75)
        hd = c.shape(MSO_SHAPE.ROUND_2_SAME_RECTANGLE, X(x0), Y(712), 277 * K, H(52), fill=hexrgb("2C5A99"), adj=[0.25, 0])
        c.write(hd, [[(head, 12, WHITE, F3)]])
        bullets(c, X(x0 + 10), Y(778), 265 * K, H(180), items, size=7.5, anchor="top", line_gap=1.45)

    c.text(X(1050), Y(990), 900 * K, H(50), [[("※ 기술지원 및 이전은 제안사 프로젝트 전사 지원조직인 기술지원그룹과 합동으로 수행함", 8, hexrgb("5F7496"), F2)]])
