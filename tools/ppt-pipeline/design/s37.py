"""37쪽 — 제안사 소개 (2차 시안 design_ppt2/s37.png).

실물은 원래 장표 것을 남긴다: 두 회사 로고(그림 36·그림 91), 회사명 글상자, 표창·인증 그림 묶음(그룹 5).
글은 원래 장표 문구. 표는 값을 그대로 두고 도형으로 다시 그린다.
"""
from lib import *

TOP, BOT = 1.62, 7.02            # 본문 안내선
Y0, Y1 = 260, 1063               # 시안 본문(카드 위·아래)
KV = (BOT - TOP) / (Y1 - Y0)


def Y(y): return TOP + (y - Y0) * KV
def H(h): return h * KV


def build(c):
    s = c.s
    # 원래 제목 서체
    title_font = "G마켓 산스 TTF Bold"
    for sh in s.shapes:
        if sh.name == "직사각형 60":
            for r in sh.text_frame.paragraphs[0].runs:
                ea = r._r.find(".//" + qn("a:ea"))
                title_font = (ea.get("typeface") if ea is not None else None) or r.font.name or title_font

    # 남길 실물을 이름·글로 찾는다
    logo_s = logo_v = name_s = name_v = certs = None
    for sh in s.shapes:
        if sh.name == "그림 36": logo_s = sh
        elif sh.name == "그림 91": logo_v = sh
        elif sh.name == "그룹 5": certs = sh
        elif sh.name == "TextBox 19":
            if "솔리데오" in sh.text_frame.text: name_s = sh
            else: name_v = sh
    keep = [x._element for x in (logo_s, logo_v, name_s, name_v, certs) if x is not None]
    for sh in list(s.shapes):
        if any(sh._element is e for e in keep) or sh.name == "TextBox 35":   # 머리말 글 유지
            continue
        c.tree.remove(sh._element)

    c.background(1000, 240)

    NAVY_T = hexrgb("0B2E6B"); EMPH = hexrgb("2070E8")
    TXT = hexrgb("2F3B6F"); BUL = c.rgb(89, 525)
    CARD = c.rgb(150, 290); CARD_LN = hexrgb("D6E6F7")
    LIST = c.rgb(500, 505)
    SEC = c.rgb(440, 832)

    # ── 키메시지 ──
    km = c.text(0.20, 1.03, 10.43, 0.40, [[("청주시 업무지원포털 유지관리 ", 23, NAVY_T, title_font),
                                            ("최상의 컨소시엄", 23, EMPH, title_font)]])
    km.name = "키메시지"

    def band(x0, x1, lines):
        b = c.shape(MSO_SHAPE.ROUND_2_SAME_RECTANGLE, x0 * K, Y(367), (x1 - x0) * K, H(123), adj=[0.28, 0])
        b.fill.gradient(); b.fill.gradient_angle = 90
        st = b.fill.gradient_stops
        st[0].color.rgb = c.rgb(500, 375); st[0].position = 0
        st[1].color.rgb = c.rgb(100, 470); st[1].position = 1.0
        c.write(b, [[(t, 18, WHITE, F3)] for t in lines], spacing=0.95)

    def bullets(x, y, w, h, items, spacing, wrap=False, gap=0.0):
        """진짜 글머리표(buChar)와 내어쓰기로 쓴 목록."""
        # 글이 "+" 로 시작하면 앞 항목의 이어지는 줄(글머리표 없이 내어쓰기 자리에서 시작)
        b = c.text(x, y, w, h, [[(tx.lstrip("+"), pt, TXT, F2)] for tx, pt in items], LEFT, anchor="middle",
                   spacing=spacing, wrap=wrap)
        for pg, (tx, pt) in zip(b.text_frame.paragraphs, items):
            pPr = pg._p.get_or_add_pPr()
            if tx.startswith("+"):
                pPr.set("marL", str(int(0.17 * 914400))); pPr.set("indent", "0")
                etree.SubElement(pPr, qn("a:buNone"))
                continue
            pPr.set("marL", str(int(0.17 * 914400))); pPr.set("indent", str(int(-0.17 * 914400)))
            if gap:
                sb = etree.SubElement(pPr, qn("a:spcBef")); etree.SubElement(sb, qn("a:spcPts")).set("val", str(int(gap * 100)))
            bc = etree.SubElement(pPr, qn("a:buClr")); etree.SubElement(bc, qn("a:srgbClr")).set("val", str(BUL))
            etree.SubElement(pPr, qn("a:buSzPct")).set("val", "100000")
            etree.SubElement(pPr, qn("a:buFont")).set("typeface", "Arial")
            etree.SubElement(pPr, qn("a:buChar")).set("char", "•")
        return b

    # ── 왼쪽 카드 (솔리데오) ──
    c.rrect(50 * K, Y(260), 957 * K, H(803), adj=0.025, fill=CARD, line=CARD_LN, lw=0.75)
    band(60, 1000, ["최고의 행정정보화", "전문기업"])
    c.rrect(65 * K, Y(497), 928 * K, H(306), adj=0.05, fill=LIST)
    bullets(85 * K, Y(505), 900 * K, H(290), [
        ("2019년 운영지원단 업무혁신 한마당 최우수상(2019년, 한국지역정보개발원)", 8.8),
        ("2018년 대한민국 ICT INNOVATION 대상 (단체부문)(2018년, 과학기술정보통신부)", 8.8),
        ("16회 대한민국 SW기업 경쟁력 최우수상 (시스템통합)(2017년, 한국소프트웨어산업협회)", 8.8),
        ("대표이사 산업 포장(2014년, 행정자치부)", 8.8),
        ("2012 공공정보화 대상 경진대회 대통령상 (2012년, 국가건물에너지통합관리시스템)", 8.8),
        ("신기술실용화 유공기업 장관상(2009, 지식경제부)", 8.8),
        ("대표이사 국가정보화 유공자 대통령 표창 (2008년, 행정안전부)", 8.8),
    ], 1.8)
    c.text(50 * K, Y(812), 957 * K, H(42), [[("표창 및 인증 내역", 13, SEC, F3)]])

    # 표창 그림 묶음(실물) — 자리·크기만
    if certs is not None:
        ratio = certs.height / float(certs.width)
        w = 3.90; h = w * ratio
        cx = (158 + 891) / 2.0 * K
        certs.left = Inches(cx - w / 2); certs.width = Inches(w)
        certs.top = Inches(Y(951) - h / 2); certs.height = Inches(h)
        for sub in certs.shapes:
            for g in (sub.shapes if sub.shape_type == 6 else [sub]):
                if g.shape_type == 1:
                    g.fill.solid(); g.fill.fore_color.rgb = c.rgb(180, 1030)
                    g.line.color.rgb = c.rgb(158, 950); g.line.width = Pt(0.75)
                    g.shadow.inherit = False
                if g.shape_type == 17:            # 좁은 자간 풀기(글자가 붙어 보임)
                    for rp in g._element.iter(qn("a:rPr")):
                        if rp.get("spc") is not None: rp.set("spc", "0")
                    g.text_frame.word_wrap = False

    # 로고·회사명(실물)
    def place(logo, name, lx, ly_mid, nx):
        if logo is not None:
            logo.left = Inches(lx); logo.top = Inches(ly_mid - logo.height / 914400.0 / 2)
        if name is not None:
            name.left = Inches(nx); name.width = Inches(2.2); name.height = Inches(0.36)
            name.top = Inches(ly_mid - 0.18)
            tf = name.text_frame; tf.word_wrap = False; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
            for pg in tf.paragraphs:
                pg.alignment = LEFT
                for r in pg.runs:
                    r.font.size = Pt(15); r.font.color.rgb = NAVY_T
                    rPr = r._r.get_or_add_rPr()
                    ea = rPr.find(qn("a:ea"))
                    if ea is None: ea = etree.SubElement(rPr, qn("a:ea"))
                    ea.set("typeface", F3); r.font.name = F3

    place(logo_s, name_s, 228 * K, Y(312), 466 * K)
    place(logo_v, name_v, 1262 * K, Y(318), 1492 * K)

    # ── 오른쪽 위 카드 (발로) ──
    c.rrect(1037 * K, Y(260), 915 * K, H(470), adj=0.04, fill=CARD, line=CARD_LN, lw=0.75)
    band(1045, 1943, ["정보화 요소기술 기반의", "지방 신생기업"])
    c.rrect(1050 * K, Y(497), 890 * K, H(221), adj=0.07, fill=LIST)
    bullets(1070 * K, Y(505), 860 * K, H(205), [
        ("청주시 다수 사업 수행 (발로 전신 현아온시스템즈)", 10),
        ("충북 지방자치단체 행정지원포털 구축 (진천/옥천/보은/영동)", 10),
        ("중앙부처 전자정부 시스템 구축 경험 (행정안전부/식품의약품안전처/소상공인시장진흥공단)", 8),
        ("솔리데오시스템즈 근속 이력 (입사 ~ 10년 이상) : 청주시 업무지원포털 구축사업 참여", 8.6),
    ], 1.75)

    # ── 오른쪽 아래 카드 (컨소시엄 표) ──
    c.rrect(1037 * K, Y(750), 915 * K, H(313), adj=0.05, fill=CARD, line=CARD_LN, lw=0.75)
    xs = [1048, 1272, 1723, 1942]
    ys = [760, 827, 951, 1050]
    HEAD = c.rgb(1100, 770); ROW = c.rgb(1500, 1040); TL = c.rgb(1272, 900)
    c.rect(xs[0] * K, Y(ys[0]), (xs[3] - xs[0]) * K, H(ys[1] - ys[0]), fill=HEAD)
    c.rect(xs[0] * K, Y(ys[1]), (xs[3] - xs[0]) * K, H(ys[3] - ys[1]), fill=ROW)
    for yy in ys[1:]:
        c.line(xs[0] * K, Y(yy), xs[3] * K, Y(yy), TL, 0.75)
    for xx in xs[1:3]:
        c.line(xx * K, Y(ys[0]), xx * K, Y(ys[3]), TL, 0.75)
    heads = ["업체명", "주요 역할", "컨소시엄 구성비율"]
    for i, t in enumerate(heads):
        lines = [[(t, 12, NAVY_T, F3)]] if i < 2 else [[("컨소시엄", 12, NAVY_T, F3)], [("구성비율", 12, NAVY_T, F3)]]
        c.text(xs[i] * K, Y(ys[0]), (xs[i + 1] - xs[i]) * K, H(ys[1] - ys[0]), lines, spacing=0.9)
    NMC = c.rgb(1140, 885); PCT = c.rgb(1830, 890)
    data = [("솔리데오", ["사업 총괄 관리/운영", "품질관리, 프로세스관리, 전사", "+기술지원", "디자인, 중앙부처 연계"], "60%"),
            ("발로", ["업무지원포털 중심 수행", "포털 요소기술, 솔루션 관련 응용 및", "+적용"], "40%")]
    for r, (nm, roles, pct) in enumerate(data):
        y0, y1 = ys[r + 1], ys[r + 2]
        c.text(xs[0] * K, Y(y0), (xs[1] - xs[0]) * K, H(y1 - y0), [[(nm, 13, NMC, F3)]])
        bullets(xs[1] * K + 0.12, Y(y0), (xs[2] - xs[1]) * K - 0.18, H(y1 - y0),
                [(t, 9.5, ) for t in roles], 1.0, wrap=True)
        c.text(xs[2] * K, Y(y0), (xs[3] - xs[2]) * K, H(y1 - y0), [[(pct, 20, PCT, F3)]])

    # 실물을 도형 위로
    for x in (logo_s, logo_v, name_s, name_v, certs):
        if x is not None:
            c.tree.remove(x._element)
            ext = c.tree.find(qn("p:extLst"))
            if ext is not None: ext.addprevious(x._element)
            else: c.tree.append(x._element)
