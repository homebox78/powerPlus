"""34쪽 — 서비스수준협약(SLA) 적용 계획 (2차 시안 design_ppt2/s34.png).

글은 원래 장표(v0.65) 문구 그대로. 남긴 실물: 운영성과 보고서 썸네일 묶음(그룹 290), 표(표 399 — 값 그대로, 색·자리만 시안).
세로는 시안 y270(패널 위)→1.62in, y1095(패널 아래)→7.02in 로 늘려 칸마다 옮긴다(글은 다시 쓰므로 늘려도 모양 유지).
"""
from PIL import Image, ImageDraw
from lib import *

S = 5.40 / 825.0
KEYFONT = "G마켓 산스 TTF Bold"
TX = hexrgb("173A73")          # 본문 남색 글
KNAVY, KBLUE = hexrgb("0B2E6B"), hexrgb("2070E8")


def V(y): return 1.62 + (y - 270) * S
def H(y0, y1): return (y1 - y0) * S


def _set_ea(r, font):
    rPr = r._r.get_or_add_rPr()
    ea = rPr.find(qn("a:ea"))
    if ea is None: ea = etree.SubElement(rPr, qn("a:ea"))
    ea.set("typeface", font)


def _cell(cell, fill, line, lw=1.5):
    tcPr = cell._tc.get_or_add_tcPr()
    for ch in list(tcPr):
        tcPr.remove(ch)
    for tag in ("a:lnL", "a:lnR", "a:lnT", "a:lnB"):
        ln = etree.SubElement(tcPr, qn(tag)); ln.set("w", str(int(lw * 12700)))
        sf = etree.SubElement(ln, qn("a:solidFill")); c = etree.SubElement(sf, qn("a:srgbClr")); c.set("val", line)
    sf = etree.SubElement(tcPr, qn("a:solidFill")); c = etree.SubElement(sf, qn("a:srgbClr")); c.set("val", fill)
    tcPr.set("anchor", "ctr")
    for a in ("marL", "marR"): tcPr.set(a, str(int(0.04 * 914400)))
    for a in ("marT", "marB"): tcPr.set(a, str(int(0.02 * 914400)))


def _cut2(path, refs, thresh=60):
    """오린 그림에서 가장자리와 이어진 바탕(refs 색)들을 투명하게."""
    im = Image.open(path).convert("RGB"); w, h = im.size; key = (255, 0, 255)
    edge = [(x, y) for x in range(0, w, 4) for y in (0, h - 1)] + [(x, y) for y in range(0, h, 4) for x in (0, w - 1)]
    for ref in refs:
        for pt in edge:
            p = im.getpixel(pt)
            if p != key and sum(abs(a - b) for a, b in zip(p, ref)) <= thresh:
                ImageDraw.floodfill(im, pt, key, thresh=thresh)
    im = im.convert("RGBA"); px = im.load()
    for y in range(h):
        for x in range(w):
            if px[x, y][:3] == key: px[x, y] = (255, 255, 255, 0)
    im.save(path); return path


def build(c):
    s = c.s
    keep = ("TextBox 79", "표 399", "그룹 290")
    for sh in list(s.shapes):
        if sh.name not in keep:
            c.tree.remove(sh._element)
    tbl_sh = [sh for sh in s.shapes if sh.name == "표 399"][0]
    thumbs = [sh for sh in s.shapes if sh.name == "그룹 290"][0]

    c.background(1000, 245)

    # ── 키메시지 ──
    kb = s.shapes.add_textbox(Inches(0.20), Inches(1.03), Inches(10.43), Inches(0.46)); kb.name = "키메시지"
    tf = kb.text_frame; tf.word_wrap = False; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    pg = tf.paragraphs[0]; pg.alignment = CENTER
    for t, col in (("공공 표준 SLA 지표 기반", KBLUE), (" 체계적 관리로 업무지원포털시스템의 안정적 운영", KNAVY)):
        r = pg.add_run(); r.text = t; r.font.size = Pt(23); r.font.bold = False
        r.font.name = KEYFONT; r.font.color.rgb = col; _set_ea(r, KEYFONT)

    BAND = hexrgb("2F7FEF"); PANEL = hexrgb("F7FBFF"); PLINE = hexrgb("D3E6FA")
    DARK = hexrgb("285FA6"); PINKT = hexrgb("E8356E")

    # ── 두 패널 + 머리 띠 ──
    for x0, x1, title in ((50, 982, "서비스 수준 협약(SLA) 추진 및 적용 계획"), (1018, 1953, "운영성과 보고 및 보고서")):
        c.rrect(x0 * K, V(270), (x1 - x0) * K, H(270, 1095), adj=0.03, fill=PANEL, line=PLINE, lw=1.0)
        c.shape(MSO_SHAPE.ROUND_2_SAME_RECTANGLE, x0 * K, V(270), (x1 - x0) * K, H(270, 350), adj=[0.35, 0], fill=BAND)
        c.text((x0 + 48) * K, V(270), 700 * K, H(270, 350), [[(title, 14.5, WHITE, F3)]], LEFT)

    # ── 왼쪽: 단계 표 ──
    LAB = hexrgb("D8EDFE"); CH = hexrgb("B8DDFD"); CL = hexrgb("7FB5F4"); AR = hexrgb("E2F0FD")
    labels = [((376, 630), ["관리대상", "서비스지표", "선정"]), ((634, 767), ["초기값 측정"]), ((773, 902), ["목표값 정의", "및 협약체결"])]
    for (y0, y1), ls in labels:
        b = c.rrect(70 * K, V(y0), 163 * K, H(y0, y1), adj=0.08, fill=LAB)
        c.write(b, [[(t, 11, TX, F3)] for t in ls], spacing=1.0)
    # SLA 적용 — 아래로 향한 오각형(90° 돌림, 글은 따로)
    cx, cyy, w, h = (70 + 233) / 2 * K, (V(909) + V(1042)) / 2, 163 * K, H(909, 1042)
    pent = c.shape(MSO_SHAPE.PENTAGON, cx - h / 2, cyy - w / 2, h, w, adj=0.28, fill=hexrgb("3A87F4"))
    pent.rotation = 90
    c.text(70 * K, V(909), 163 * K, H(909, 1010), [[("SLA 적용", 12, WHITE, F3)]])

    cards = [((377, 430, 483), "필수지표 : 정보시스템 가용률", None, ["업무영역 전체 가동률 관리"], False),
             ((496, 555, 625), "선택지표 : 장애·운영·보안·", "서비스 지원 등", ["청주시 업무 특성", "반영 지표"], False),
             ((636, 690, 760), "초기값 측정", None, ["현 서비스", "수준 분석"], False),
             ((773, 827, 885), "서비스 협약", None, ["목표값 정의"], True),
             ((897, 954, 1025), "평가 및 적용", None, ["서비스수준", "측정 및 보고"], True)]
    for (y0, ym, y1), head, head2, body, dash in cards:
        c.rrect(254 * K, V(y0), 284 * K, H(y0, y1), adj=0.12, fill=WHITE, line=CL, lw=1.0, dash=dash)
        hb = c.shape(MSO_SHAPE.ROUND_2_SAME_RECTANGLE, 254 * K, V(y0), 284 * K, H(y0, ym), adj=[0.3, 0], fill=CH, line=CL, lw=1.0)
        ln = [[(head, 8, TX, F3)]]
        if head2: ln.append([(head2, 7, TX, F3)])
        c.write(hb, ln, spacing=0.95)
        c.text(254 * K, V(ym), 284 * K, H(ym, y1), [[(t, 8.5, TX, F2)] for t in body], spacing=1.0)

    arrows = [((427, 484), ["굿모닝시스템 등급 : A4"], TX), ((555, 619), ["상호 합의", "평가 및 관리지표 선정"], PINKT),
              ((692, 757), ["서비스 지표값 분석", "신규지표 현수준 측정"], TX), ((827, 890), ["지표 및 목표수준 정의", "Penalty 산정 협의"], TX),
              ((955, 1017), ["서비스수준 결과분석", "서비스지표 조정"], PINKT)]
    for (y0, y1), ls, col in arrows:
        c.shape(MSO_SHAPE.PENTAGON, 545 * K, V(y0), 285 * K, H(y0, y1), adj=0.3, fill=AR)
        c.text(562 * K, V(y0), 240 * K, H(y0, y1), [[(t, 8, col, F2 if col == TX else F3)] for t in ls], LEFT, spacing=1.0)

    RING = hexrgb("4A93F3"); D = 116 * K
    for yc, ls in ((452, ["서비스", "조사"]), (587, ["서비스", "정의"]), (725, ["초기값", "측정"]), (860, ["SLA", "협약"]), (980, ["서비스", "관리"])):
        o = c.oval(903 * K - D / 2, V(yc) - D / 2, D, D, fill=WHITE, line=RING, lw=2.25)
        c.write(o, [[(t, 9, hexrgb("1E5FC9"), F3)] for t in ls], spacing=0.95)
    PILL = hexrgb("2F7FEF")
    c.write(c.pill(803 * K, V(811) - 0.14, 120 * K, 0.28, fill=PILL), [[("1개월이내", 8.5, WHITE, F3)]])
    c.write(c.pill(783 * K, V(1036) - 0.14, 154 * K, 0.28, fill=PILL), [[("개선점도출", 9, WHITE, F3)]])
    c.text(67 * K, V(1072) - 0.1, 700 * K, 0.2, [[("* SLA 관리지표 : 가용률 / 장애 / 운영 / 보안 / 성능 / 서비스지원", 8.5, TX, F2)]], LEFT)

    # ── 오른쪽: 배지 ──
    bw, bh = 107 * K, 121 * K; bx, byc = 1763.5 * K, 1.92
    hx = c.shape(MSO_SHAPE.HEXAGON, bx - bh / 2, byc - bw / 2, bh, bw, adj=[0.27, 1.15470], fill=hexrgb("EAF5FE"), line=hexrgb("5AA0F6"), lw=2.0)
    hx.rotation = 90
    c.text(bx - bw / 2, byc - bh / 2 + 0.06, bw, 0.2, [[("!", 16, KBLUE, F3)]])
    c.text(bx - bw / 2, byc - 0.01, bw, 0.28, [[("99.9점", 8.5, KBLUE, F3)], [("목표", 8.5, TX, F3)]], spacing=0.9)
    c.write(c.rrect(1833 * K, V(272), 103 * K, H(272, 340), adj=0.18, fill=hexrgb("E8356E")), [[("예시", 12, WHITE, F3)]])

    # ── 오른쪽: 단계 평행사변형 ──
    for x0, x1, ls, dark in ((1047, 1332, ["지표별측정결과", "산출"], False), (1338, 1620, ["측정 근거", "자료 작성"], False),
                             (1625, 1932, ["서비스수준평가", "결과 도출"], True)):
        p = c.shape(MSO_SHAPE.PARALLELOGRAM, x0 * K, V(375), (x1 - x0) * K, H(375, 455), adj=0.18,
                    fill=hexrgb("154E97") if dark else hexrgb("D3EBFE"))
        c.write(p, [[(t, 9.5, WHITE if dark else TX, F3)] for t in ls], spacing=0.95)

    # ── 오른쪽: 표(원래 값, 시안 색·자리) ──
    t = tbl_sh.table
    cw = [75, 190, 101, 99, 144, 280]
    for i, w in enumerate(cw): t.columns[i].width = Inches(w * K)
    rh = [(458, 500), (500, 627), (627, 752), (752, 840)]
    for i, (y0, y1) in enumerate(rh): t.rows[i].height = Inches(H(y0, y1))
    tbl_sh.left, tbl_sh.top = Inches(1043 * K), Inches(V(458))
    for ri, row in enumerate(t.rows):
        for ci, cell in enumerate(row.cells):
            head = ri == 0
            _cell(cell, "D2E6FB" if head else "E8F3FE", "FFFFFF", 1.5)
            for pgp in cell.text_frame.paragraphs:
                if not head and ci == 5: pgp.alignment = LEFT
                else: pgp.alignment = CENTER
                for r in pgp.runs:
                    bold = head or ci == 0
                    r.font.size = Pt(8 if head else (8 if ci == 0 else 7.5 if ci < 5 else 7))
                    r.font.bold = False
                    f = F3 if bold else F2
                    r.font.name = f; r.font.color.rgb = TX; _set_ea(r, f)

    # ── 성과결과 추출 방식 ──
    c.rrect(1040 * K, V(866), 457 * K, H(866, 1064), adj=0.08, fill=PANEL, line=PLINE, lw=1.0)
    c.shape(MSO_SHAPE.ROUND_2_SAME_RECTANGLE, 1040 * K, V(866), 457 * K, H(866, 937), adj=[0.3, 0], fill=DARK)
    c.text(1180 * K, V(866), 300 * K, H(866, 937), [[("성과결과 추출 방식", 11, WHITE, F3)]])
    c.text(1180 * K, V(937), 300 * K, H(937, 1064), [[("ITSM을 활용한", 10, TX, F2)], [("SLA 이행수준 평가", 10, TX, F2)]], spacing=1.2)
    ip = c.crop("clip", 1047, 880, 1172, 1025)
    _cut2(ip, [c.D.getpixel((int(1060 * c.Z), int(1045 * c.Z))), c.D.getpixel((int(1045 * c.Z), int(900 * c.Z))),
               c.D.getpixel((int(1170 * c.Z), int(885 * c.Z)))])
    iw = 125 * K
    c.pic(ip, 1047 * K, (V(866) + V(1064)) / 2 - iw * 145 / 125 / 2, iw)

    # ── 운영성과보고서(예시) ──
    c.rrect(1528 * K, V(853), 402 * K, H(853, 1066), adj=0.08, fill=PANEL, line=PLINE, lw=1.0)
    rb = c.shape(MSO_SHAPE.ROUND_2_SAME_RECTANGLE, 1528 * K, V(853), 402 * K, H(853, 900), adj=[0.35, 0], fill=DARK)
    c.write(rb, [[("운영성과 보고서(예시)", 11, WHITE, F3)]])
    top, bot = V(900) + 0.05, V(1066) - 0.06
    ar = thumbs.width / float(thumbs.height)
    hh = bot - top; ww = hh * ar
    thumbs.width, thumbs.height = Inches(ww), Inches(hh)
    thumbs.left, thumbs.top = Inches(1729 * K - ww / 2), Inches(top)
    # 남긴 실물(표·썸네일)을 새 도형 위로
    for sh in (tbl_sh, thumbs):
        c.tree.remove(sh._element); c.tree.append(sh._element)
