"""24쪽 — 시스템의 연계 및 관리 (2차 시안 design_ppt2/s24.png).

왼쪽 판(연계 현황 관리 방안)은 시안대로 다시 그리고, 오른쪽 절차도는 원래 장표 그룹(Group 32)을
그대로 살려 시안 자리·색만 맞춘다(글이 촘촘해 다시 그리면 7pt 아래로 내려가므로).
글은 원래 장표 문구.
"""
from lib import *

# 세로: 판 윗변 y272 → 1.70in, 판 아랫변 y1088 → 7.00in (판 안쪽은 같은 비율)
Y0, IN0, KV = 272, 1.70, (7.00 - 1.70) / (1088 - 272)


def Y(y): return IN0 + (y - Y0) * KV
def H(h): return h * KV
def X(x): return x * K


NV = hexrgb("0B2E6B"); EM = hexrgb("2070E8"); TX = hexrgb("2F3B6F")
KFONT = "G마켓 산스 TTF Bold"


def build(c):
    c.keep_only("TextBox 34", "Group 32", "직사각형 278")
    c.background(1000, 245)

    # ── 키메시지 ──
    b = c.rect(0.20, 1.03, 10.43, 0.45, name="키메시지")
    parts = [("정확한", EM), (" 현황 관리 · ", NV), ("최적의", EM), (" 기술 구현 · ", NV), ("안정적", EM), (" 연계 운영", NV)]
    c.write(b, [[(t, 23, col, KFONT) for t, col in parts]])

    LINE = hexrgb("D3E3F6"); PANEL = hexrgb("F7FBFE")

    # ── 판 두 개 ──
    for x0, x1, head, col in ((45, 1010, "연계 현황 관리 방안", c.rgb(300, 300)),
                              (1033, 1958, "연계 및 기술지원 표준 절차", c.rgb(1100, 300))):
        c.rrect(X(x0), Y(272), X(x1 - x0), H(816), adj=0.025, fill=PANEL, line=LINE, lw=1.0)
        hd = c.shape(MSO_SHAPE.ROUND_2_SAME_RECTANGLE, X(x0), Y(272), X(x1 - x0), H(88), fill=col, adj=[0.3, 0])
        c.write(hd, [[(head, 18, WHITE, F3)]])

    # ── 왼쪽 판 ──
    c.text(X(60), Y(385), X(935), H(50), [[("행정정보공유 효율성 제고", 17, NV, F3)]])

    CARD = WHITE; CB = hexrgb("D6E5F7"); CH = c.rgb(90, 480)

    def card(x0, y0, x1, y1, title, hy=55):
        c.rrect(X(x0), Y(y0), X(x1 - x0), H(y1 - y0), adj=0.06, fill=CARD, line=CB, lw=0.75)
        h = c.shape(MSO_SHAPE.ROUND_2_SAME_RECTANGLE, X(x0), Y(y0), X(x1 - x0), H(hy), fill=CH, adj=[0.3, 0])
        c.write(h, [title], LEFT, margin=0.2)

    def body(x0, y0, x1, y1, lines, pt=8):
        """줄은 시안처럼 손으로 나눈다(어절 중간에서 끊기지 않게). 들여쓴 줄은 앞에 공백."""
        paras = [[(t, pt, TX, F2)] for t in lines]
        return c.text(X(x0), Y(y0), X(x1 - x0), H(y1 - y0), paras, LEFT, spacing=1.12)

    def run(t, pt=8.5, col=TX, f=F2): return (t, pt, col, f)

    def icon(name, box, cy, w):
        x0, y0, x1, y1 = box
        p = c.crop(name, x0, y0, x1, y1, cut=(x0 + 2, y0 + 2), cut_thresh=40)
        h = (y1 - y0) * K * w / float(x1 - x0)
        c.pic(p, X(x0), Y(cy) - h / 2, w * K)

    # 형상관리시스템(Git)
    card(75, 452, 513, 735, [run("형상관리시스템", 13, WHITE, F3), run("(Git)", 13, WHITE, F3)])
    icon("db", (88, 530, 250, 705), 617, 145)
    body(240, 520, 510, 725, [
        "연계여부 확정 이후",
        "운영지원센터에서 개발한 연계",
        "모듈과 관련 산출물 관리",
        "• 형상관리시스템을 통해 관리",
        "   - 연계모듈(프로그램 소스)",
        "   - 인터페이스 규격서"], pt=7.5)

    # 업무지원포털(31종)관리
    card(546, 452, 983, 735, [run("업무지원포털(31종)관리", 13, WHITE, F3)])
    icon("laptop", (550, 538, 715, 698), 618, 140)
    body(695, 520, 982, 725, [
        "현재 31종의 정보연계 내역·이력",
        "현행화 관리",
        " - 대상기관, 대상시스템, 연계근거",
        " - 적용기술, 연계항목, 연계주기,",
        "    연계코드",
        " - 관리항목 및 서비스 변경 시",
        "    청주시와 협의에 의해",
        "    연계모듈 변경사항 반영"], pt=7.5)

    # 문서관리
    card(75, 761, 513, 975, [run("문서관리", 13, WHITE, F3)], hy=51)
    icon("folder", (86, 822, 240, 962), 892, 140)
    body(238, 822, 510, 965, [
        "연계를 위한 각종 신청 문서 및",
        "기술검토 문서 등 관리",
        "• 연계신청서, 검토의견서(수신),",
        "   연계정보정의서, 연계확인서 등"], pt=7.5)

    # 신규 확대 대상기관 수요조사
    c.rrect(X(546), Y(760), X(437), H(215), adj=0.07, fill=hexrgb("E9F3FD"))
    c.text(X(575), Y(772), X(400), H(45), [[run("신규 확대 대상기관 수요조사", 12, NV, F3)]], LEFT)
    for yy, lab in ((830, "내부 수요 조사"), (897, "외부 성공 사례 분석")):
        c.write(c.rrect(X(577), Y(yy), X(218), H(52), adj=0.25, fill=WHITE, line=hexrgb("DDE9F8"), lw=0.5),
                [[run(lab, 9, NV, F3)]])
    CK = hexrgb("2070E8")
    for yy, lab in ((845, "공식적 설문"), (876, "밀착 면담"), (923, "본사 지원")):
        c.text(X(815), Y(yy) - 0.1, X(160), 0.2, [[("✓ ", 10, CK, "Segoe UI Symbol"), run(lab, 9.5, NV, F2)]], LEFT)

    # 아래 띠
    c.rrect(X(70), Y(988), X(918), H(80), adj=0.2, fill=hexrgb("EAF4FD"))
    c.text(X(70), Y(988), X(918), H(80), [[run("체계적 모니터링으로 안정적 서비스 제고", 17, NV, F3)]])

    # ── 오른쪽 판: 원래 절차도 그룹을 자리·색만 맞춘다 ──
    grp = [sh for sh in c.s.shapes if sh.name == "Group 32"][0]
    grp.left = Inches(X(1057)); grp.top = Inches(Y(378))
    for sh in grp.shapes:
        if sh.name == "Rounded Rectangle 359":
            sh.fill.solid(); sh.fill.fore_color.rgb = c.rgb(1070, 400)
        if sh.name == "Rectangle 363":
            sh.fill.solid(); sh.fill.fore_color.rgb = c.rgb(1100, 452)
    note = [sh for sh in c.s.shapes if sh.name == "직사각형 278"][0]
    for sh in (grp, note):        # 새로 그린 판 위로
        c.tree.remove(sh._element); c.tree.append(sh._element)
    note.left = Inches(X(1050)); note.top = Inches(Y(1045)); note.width = Inches(X(900)); note.height = Inches(H(34))
