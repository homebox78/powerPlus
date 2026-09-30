"""38쪽 — 제안의 특징 및 장점 (2차 시안 design_ppt2/s38.png).

키메시지 두 줄 + '축적된 경험과 지식…' 부제, 왼쪽 원 안 회사 로고·화면(원래 장표 실물),
오른쪽 특징 카드 3장(아이콘은 시안에서 오림, 글은 원래 장표 문구).
"""
import io
from lib import *

KF = "G마켓 산스 TTF Bold"
KNAVY, KBLUE = hexrgb("0B2E6B"), hexrgb("2070E8")


def _find(shapes, name):
    for sh in shapes:
        if sh.name == name:
            return sh
        if sh.shape_type == 6:
            r = _find(sh.shapes, name)
            if r is not None:
                return r
    return None


def _lift(c, name):
    """그룹 안 그림을 최상위로 꺼낸다(원래 도형 그대로)."""
    sh = _find(c.s.shapes, name)
    el = sh._element
    el.getparent().remove(el)
    c.tree.append(el)
    for s2 in c.s.shapes:
        if s2._element is el:
            return s2


def build(c):
    # ── 원래 실물 확보 ──
    logo_blob = _find(c.s.shapes, "Picture 10").image.blob
    mon = _lift(c, "그림 51")          # 화면 캡처(모니터)
    cons = _lift(c, "그림 30")         # '솔리데오 컨소시엄' 글 그림
    c.keep_only("TextBox 57", mon.name, cons.name)
    c.background(1000, 450)

    # ── 키메시지 ──
    km = c.text(0.20, 1.03, 10.43, 0.92,
                [[("청주시 업무지원포털은 20여년 동안의 생각과 운영경험이 녹아있어", 23, KNAVY, KF)],
                 [("업무와 시스템에 대한 깊은 이해", 23, KBLUE, KF), ("를 필요로 합니다", 23, KNAVY, KF)]])
    km.name = "키메시지"

    # ── 부제(점 3개 + 한 줄) ──
    for x in (790, 847, 904):
        d = 13 * K
        c.oval(x * K - d / 2, 2.13 - d / 2, d, d, fill=KBLUE)
    c.text(0.24, 2.24, 10.35, 0.5,
           [[("축적된 경험과 지식에 기반한 ", 20, KNAVY, F4),
             ("차별화된 유지관리 방안을 제시 ", 26, KBLUE, F4),
             ("합니다", 20, KNAVY, F4)]])

    # ── 왼쪽 원 ──
    CY = 4.93

    def Y(y): return CY + (y - 744) * K
    DX = 6
    def X(x): return (x + DX) * K

    ring = c.rgb(60, 740)
    c.oval(X(22), Y(462), 560 * K, 560 * K, fill=c.rgb(300, 1080), alpha=0.9)
    c.oval(X(40), Y(478), 526 * K, 526 * K, fill=c.rgb(300, 520), line=ring, lw=7)
    # 로고(원래 로고 그림의 앞부분 'solideoS.')
    from PIL import Image
    im = Image.open(io.BytesIO(logo_blob)).convert("RGBA").crop((0, 0, 178, 59))
    lp = c.work + "/s38_logo.png"; im.save(lp)
    c.pic(lp, X(218), Y(556), 168 * K)
    cons.left, cons.top = Inches(X(100)), Inches(Y(622))
    cons.width = Inches(205 * K); cons.height = Inches(205 * K * 28 / 152)
    # 화면 캡처: 원래 그림의 모니터+겹친 화면(가로 200~755)이 시안 130~545 에 오도록
    sc = 415.0 / 555
    mon.width = Inches(829 * sc * K); mon.height = Inches(346 * sc * K)
    mon.left = Inches(X(130 - 200 * sc)); mon.top = Inches(Y(690 - 8 * sc))
    for p in (mon, cons):
        c.tree.remove(p._element); c.tree.append(p._element)

    # ── 화살표 ──
    c.shape(MSO_SHAPE.PENTAGON, 598 * K, Y(625), 92 * K, 215 * K, fill=c.rgb(640, 730), adj=0.46)

    # ── 오른쪽 카드 3장 ──
    SY = 1.197
    TOPS = [2.85, 4.284, 5.718]
    PILL = c.rgb(1750, 520)
    EDGE = hexrgb("CFE3F8")
    TXT = hexrgb("22406F")
    bul = c.crop("bul", 973, 572, 1001, 600, cut=(974, 573))
    cards = [
        (473, "사업의 목적과 사상에 대한 이해",
         ["사업의 본질에 대한 정확한 이해를 바탕으로", "구체화된 세부 실행방안을 제시"], (738, 484, 928, 652)),
        (685, "사업수행에 필요한 지식과 경험",
         ["핵심 역량 중심의 인력 투입계획과", "최적의 수행조직 운영 방안 제시"], (740, 698, 922, 866)),
        (895, "정확한 문제진단 및 해결방안 도출",
         ["구축 및 지속적 유지관리 참여로 사업의 연속성 확보 및", "특화 방법론에 기반한 최적의 사업 및 품질관리 방안 제시"],
         (745, 908, 910, 1076)),
    ]
    for (ty, title, lines, ic), T in zip(cards, TOPS):
        def cy(y): return T + (y - ty) * K * SY
        H = 195 * K * SY
        c.rrect(708 * K, T, 1250 * K, H, adj=0.09, fill=c.rgb(1850, ty + 140), line=EDGE, lw=1.0)
        c.rrect(722 * K, cy(ty + 12), 212 * K, H - 24 * K * SY, adj=0.12, fill=c.rgb(760, 700))
        x0, y0, x1, y1 = ic
        iw, ih = (x1 - x0) * K, (y1 - y0) * K
        c.pic(c.crop("ico%d" % ty, x0, y0, x1, y1, cut=(x0 + 2, y0 + 2), cut_thresh=30),
              x0 * K, cy((y0 + y1) / 2.0) - ih / 2, iw)
        c.write(c.pill(940 * K, cy(ty + 41) - 36 * K, 1008 * K, 72 * K, fill=PILL),
                [[(title, 14, WHITE, F3)]], LEFT, margin=58 * K)
        for i, t in enumerate(lines):
            yy = cy(ty + 112 + 45 * i)
            c.pic(bul, 973 * K, yy - 14 * K, 28 * K)
            c.text(1018 * K, yy - 0.15, 920 * K, 0.3, [[(t, 11.5, TXT, F2)]], LEFT)
