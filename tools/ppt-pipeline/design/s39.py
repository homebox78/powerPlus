"""39쪽 — 3. 제안사의 참여 당위성 (2차 시안 design_ppt2/s39.png).

키메시지 한 줄 가운데 원래 장표의 솔리데오 로고(그림 43)를 둔 상자, 아래로 전문성·준비성·책임감
세 줄(육각 배지 + 오각 화살 띠). 메달·악수 3D 그림은 시안에서 오린다. 글은 원래 장표 문구.
"""
from lib import *
from PIL import ImageFont

KFONT = "G마켓 산스 TTF Bold"
KNAVY = hexrgb("0B2E6B")


def _em_w(text, pt):
    """G마켓 산스 TTF Bold 로 잰 글 폭(inch)."""
    f = ImageFont.truetype("C:/Windows/Fonts/GmarketSansTTFBold.ttf", 400)
    return f.getlength(text) / 400.0 * pt / 72.0


def _hex(c, g, x0, y0, x1, y1, fill, line):
    """꼭짓점이 위아래인 육각형(90도 돌린 도형)."""
    cx, cy = g.X((x0 + x1) / 2.0), g.Y((y0 + y1) / 2.0)
    w, h = (y1 - y0) * K, (x1 - x0) * K          # 돌리기 전 상자
    b = c.shape(MSO_SHAPE.HEXAGON, cx - w / 2, cy - h / 2, w, h, fill=fill, line=line, lw=2.25, adj=[0.28])
    b.rotation = 90
    return b


def build(c):
    c.remove("그룹 1", "그룹 40", "IC_1434", "IC_1262")
    c.background(1000, 330)

    # ── 키메시지: 글 + 로고 상자 + 입니다 (가운데) ──
    left, right = "본 사업의 성공적 수행을 위한 최고의 선택은", "입니다"
    BOXW, BOXH, G1, G2 = 551 * K, 100 * K, 0.11, 0.20
    size = 23.0
    while True:
        wl, wr = _em_w(left, size) + 0.08, _em_w(right, size) + 0.08
        total = wl + G1 + BOXW + G2 + wr
        if total <= 10.2 or size <= 16:
            break
        size -= 0.5
    x = SLIDE_W / 2 - total / 2
    T, H = 1.03, 0.46
    k1 = c.text(x, T, wl, H, [[(left, size, KNAVY, KFONT)]], LEFT)
    k1.name = "키메시지"
    x += wl + G1
    c.rrect(x, T + H / 2 - BOXH / 2, BOXW, BOXH, adj=0.25, fill=c.rgb(1400, 215), line=c.rgb(1132, 250), lw=1.25, name="키메시지 로고 상자")
    for sh in c.s.shapes:
        if sh.name == "그림 43":                      # 원래 로고(실물) — 상자 가운데로
            sh.left = Inches(x + (BOXW - sh.width / 914400.0) / 2)
            sh.top = Inches(T + H / 2 - sh.height / 914400.0 / 2)
            c.tree.remove(sh._element); c.tree.append(sh._element)
    x += BOXW + G2
    k2 = c.text(x, T, wr, H, [[(right, size, KNAVY, KFONT)]], LEFT)
    k2.name = "키메시지 2"

    # ── 세 줄 ──
    c.vmap(470.5, 2.58, 935, 5.98)
    HEXF, HEXL = c.rgb(230, 530), hexrgb("CFE3FB")
    BARF, BARL = c.rgb(700, 395), hexrgb("B9D6F6")
    SMALL, BIG = hexrgb("0A3A8C"), hexrgb("1665D0")
    DARK = c.rgb(1800, 1000)
    rows = [
        # 배지(x0,y0,x1,y1), 띠(x0,y0,x1,y1), 끝 비율, 글 x, 작은 줄 y, 큰 줄 y, 라벨, 작은 글, 큰 글, 어두운 띠
        ((173, 353, 390, 588), (330, 367, 1605, 545), 0.40, 463, 415, 482, "전문성",
         "본 사업과 관련한 다수의 선행 및 유관사업 수행경험을 보유한", "최고의 행정/공공 정보화 전문기업", False, 23),
        ((287, 583, 507, 813), (445, 605, 1757, 790), 0.42, 585, 657, 722, "준비성",
         "본 사업 관련 법령, 업무, 시스템에 대한 정확한 이해를 바탕으로", "핵심전략과 실행방안이 구체화된 사업자", False, 22),
        ((405, 820, 628, 1050), (560, 843, 1915, 1015), 0.44, 702, 888, 952, "책임감",
         "최초 구축 및 지속적인 유지관리 참여로", "사업에 대한 애정과 사명감이 있는 사업자", True, 22),
    ]
    for hx, bar, tip, tx, ys, yb, lab, small, big, dark, bsz in rows:
        g = c.grp(min(hx[1], bar[1]), max(hx[3], bar[3]))
        bx0, by0, bx1, by1 = bar
        c.shape(MSO_SHAPE.PENTAGON, g.X(bx0), g.Y(by0), (bx1 - bx0) * K, (by1 - by0) * K,
                fill=DARK if dark else BARF, line=None if dark else BARL, lw=0.75, adj=[tip])
        cs, cb = (WHITE, WHITE) if dark else (SMALL, BIG)
        c.text(g.X(tx), g.Y(ys) - 0.14, 7.2, 0.28, [[(small, 13, cs, F3)]], LEFT)
        c.text(g.X(tx), g.Y(yb) - 0.24, 7.6, 0.48, [[(big, bsz, cb, F3)]], LEFT)
        _hex(c, g, *hx, fill=HEXF, line=HEXL)
        c.text(g.X(hx[0]), g.Y((hx[1] + hx[3]) / 2.0) - 0.2, (hx[2] - hx[0]) * K, 0.4, [[(lab, 19, WHITE, F3)]])

    # ── 3D 그림 ──
    g = c.grp(353, 588)
    c.pic(c.crop("medal", 1640, 345, 1895, 600, cut=(1645, 360)), g.X(1640), g.Y(345), 255 * K)
    g = c.grp(785, 1072)
    c.pic(c.crop("hand", 55, 791, 338, 1072, cut=(60, 795)), g.X(55), g.Y(791), 283 * K)
