"""25쪽 — 6. 비상대책 (2차 시안 design_ppt2/s25.png).

원래 장표가 이미 시안과 같은 배치라(글이 촘촘한 쪽) 원래 도형·표·문구는 그대로 두고,
시안과 다른 곳만 바꾼다: 키메시지 규칙, 3단계 카드(번호 원+단계 알약), 백업/복구 3D 아이콘(시안에서 오림),
사용자 아이콘(시안에서 오림), 가운데 + 원 장식 제거.
"""
from lib import *

KEY_FONT = "G마켓 산스 TTF Bold"
NAVY_T = hexrgb("0B2E6B")
BLUE_T = hexrgb("2070E8")
EMU = 914400.0


def find(shapes, name):
    for sh in shapes:
        if sh.name == name:
            return sh
    return None


def remove_in(grp, *names):
    for sh in list(grp.shapes):
        if sh.name in names:
            sh._element.getparent().remove(sh._element)


def into(grp, sh, after):
    """최상위에 만든 도형을 그룹 안(after 도형 바로 뒤)으로 옮기고 좌표를 그룹 자식 좌표로 바꾼다."""
    x = grp._element.grpSpPr.find(qn("a:xfrm"))
    off, ext = x.find(qn("a:off")), x.find(qn("a:ext"))
    cho, che = x.find(qn("a:chOff")), x.find(qn("a:chExt"))
    ox, oy, ex, ey = int(off.get("x")), int(off.get("y")), int(ext.get("cx")), int(ext.get("cy"))
    cx0, cy0, cex, cey = int(cho.get("x")), int(cho.get("y")), int(che.get("cx")), int(che.get("cy"))
    sx, sy = cex / float(ex), cey / float(ey)
    l, t, w, h = sh.left, sh.top, sh.width, sh.height
    el = sh._element
    el.getparent().remove(el)
    ref = find(grp.shapes, after)._element
    ref.addnext(el)
    sh.left = int(cx0 + (l - ox) * sx); sh.top = int(cy0 + (t - oy) * sy)
    sh.width = int(w * sx); sh.height = int(h * sy)
    return sh


def keymsg(c, parts):
    b = c.rect(0.20, 1.03, 10.43, 0.40, name="키메시지")
    c.write(b, [[(tx, 23, col, KEY_FONT) for tx, col in parts]], CENTER)
    for r in b.text_frame.paragraphs[0].runs:
        r._r.get_or_add_rPr().set("spc", "-150")
    return b


def build(c):
    c.remove("직사각형 36", "그룹 3")      # 원 키메시지, 가운데 + 원 장식
    keymsg(c, [("완벽한 지원체계 구성으로 ", NAVY_T), ("24시간 운영 안정성 및 업무 지속성 보장", BLUE_T)])

    # ── 장애대응 3단계 카드: 괄호 틀·"1단계" 글 → 둥근 카드 + 번호 원 + 단계 알약 ──
    g2 = find(c.s.shapes, "그룹 2")
    remove_in(g2, "Group 103", "Group 106", "Group 109", "Text Box 21", "Text Box 33", "Text Box 45")
    CARD_LN = hexrgb("C8DAF4")
    BADGE = hexrgb("2B6FE3")
    back, front = [], []
    for i, x in enumerate((0.43, 2.11, 3.78)):
        card = c.rrect(x, 2.76, 1.47, 0.92, adj=0.07, fill=hexrgb("F7FAFF"), line=CARD_LN, lw=0.75)
        tab = c.pill(x + 0.19, 2.62, 0.50, 0.23, fill=WHITE, line=CARD_LN, lw=0.75)
        c.write(tab, [[("단계", 9.5, NAVY_T, F3)]], RIGHT, margin=0.08)
        num = c.oval(x + 0.03, 2.59, 0.29, 0.29, fill=BADGE)
        c.write(num, [[(str(i + 1), 13, WHITE, F3)]])
        back.append(card); front += [tab, num]
    after = "양쪽 모서리가 둥근 사각형 8"      # 카드는 배경 바로 위(글·제목 띠 뒤)
    for sh in back:
        into(g2, sh, after); after = sh.name
    after = list(g2.shapes)[-1].name          # 번호 원·단계 알약은 맨 위
    for sh in front:
        into(g2, sh, after); after = sh.name

    # ── 백업/복구: 원래 아이콘 → 시안 3D 아이콘 ──
    g4 = find(c.s.shapes, "Group 4")
    remove_in(g4, "Picture 578", "Picture 583", "Picture 588", "Picture 593", "Picture 598",
              "TextBox 573", "Freeform 14")
    c.remove("백업대상 아이콘")
    icons = [  # 이름, 시안 오림(2000 기준), 카드 왼쪽(in), 카드 위(in)
        ("db", (1128, 392, 1258, 518), 5.88, 2.61),
        ("inbox", (1440, 400, 1564, 518), 7.50, 2.61),
        ("tape", (1745, 402, 1874, 515), 9.11, 2.61),
        ("mon", (1130, 640, 1274, 734), 5.88, 3.96),
        ("rest", (1436, 630, 1570, 746), 7.50, 3.96),
        ("bug", (1745, 628, 1880, 744), 9.11, 3.96),
    ]
    H = 0.66
    for nm, (x0, y0, x1, y1), cl, ct in icons:
        p = c.crop(nm, x0, y0, x1, y1, cut=(x0 + 2, y0 + 2), cut_thresh=30)
        w = H * (x1 - x0) / float(y1 - y0)
        if w > 0.80:
            w = 0.80
        pic = c.pic(p, 0, 0, w)
        pic.left = Inches(cl + 0.66 - w / 2.0)
        pic.top = Inches(ct + 0.08 + (0.74 - pic.height / EMU) / 2.0)

    # ── 사용자 아이콘 ──
    g17 = find(c.s.shapes, "Group 17")
    remove_in(g17, "Picture 559")
    p = c.crop("user", 116, 700, 184, 758, cut=(118, 702), cut_thresh=30)
    pic = c.pic(p, 0.735, 4.38, 0.36)
