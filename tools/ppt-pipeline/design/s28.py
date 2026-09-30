"""28쪽 — 8. 보안관리 (2차 시안 design_ppt2/s28.png).

글은 원래 장표 문구 그대로, 배치·색·아이콘은 시안. 실물: 굿모닝 화면 캡처(Picture 401)·점검항목 표(Table 404)는 원래 것을 옮겨 쓴다.
"""
import copy
from lib import *

EMU = 914400
BG = hexrgb("F0F8FE")
PANEL = hexrgb("F5FAFE")
PANEL_LN = hexrgb("CFE6FC")
NV = hexrgb("0B2E6B")      # 제목·강조 남색
TX = hexrgb("22386E")      # 본문 글
CARD_LN = hexrgb("D6E9FB")
BLUE1 = hexrgb("3589F2")   # 왼쪽 머리·카드 머리·단계
NAVYH = hexrgb("1D5EAA")   # 오른쪽 머리
ARR = hexrgb("7FB2EA")     # 흐름 화살표
DIV = hexrgb("CFE3F7")


def _lift_pic(c, grp_name, pic_name):
    """그룹 안 그림을 그룹 밖(슬라이드 좌표)으로 꺼낸다."""
    for sh in c.s.shapes:
        if sh.name != grp_name:
            continue
        x = sh._element.find(qn("p:grpSpPr")).find(qn("a:xfrm"))
        off, ext, cho, che = [x.find(qn(t)) for t in ("a:off", "a:ext", "a:chOff", "a:chExt")]
        sx = int(ext.get("cx")) / float(che.get("cx")); sy = int(ext.get("cy")) / float(che.get("cy"))
        for ch in sh.shapes:
            if ch.name == pic_name:
                el = copy.deepcopy(ch._element)
                cx = el.find(".//" + qn("a:xfrm"))
                o, e = cx.find(qn("a:off")), cx.find(qn("a:ext"))
                nx = int(off.get("x")) + (int(o.get("x")) - int(cho.get("x"))) * sx
                ny = int(off.get("y")) + (int(o.get("y")) - int(cho.get("y"))) * sy
                o.set("x", str(int(nx))); o.set("y", str(int(ny)))
                e.set("cx", str(int(int(e.get("cx")) * sx))); e.set("cy", str(int(int(e.get("cy")) * sy)))
                c.tree.append(el)
                return el
    return None


def _cell_style(cell, fill, color, border):
    cell.fill.solid(); cell.fill.fore_color.rgb = fill
    for pg in cell.text_frame.paragraphs:
        for r in pg.runs:
            r.font.color.rgb = color
    tcPr = cell._tc.get_or_add_tcPr()
    for t in ("a:lnL", "a:lnR", "a:lnT", "a:lnB"):
        for e in tcPr.findall(qn(t)):
            tcPr.remove(e)
    for i, t in enumerate(("a:lnL", "a:lnR", "a:lnT", "a:lnB")):
        ln = etree.Element(qn(t)); ln.set("w", "9525"); ln.set("cap", "flat"); ln.set("cmpd", "sng")
        sf = etree.SubElement(ln, qn("a:solidFill")); cl = etree.SubElement(sf, qn("a:srgbClr")); cl.set("val", border)
        etree.SubElement(ln, qn("a:prstDash")).set("val", "solid")
        tcPr.insert(i, ln)


def build(c):
    # ── 원래 도형 정리: 머리말 글·메모·표·화면 캡처만 남긴다 ──
    shot = _lift_pic(c, "Group 3", "Picture 401")
    shot_name = None
    for sh in c.s.shapes:
        if sh._element is shot:
            sh.name = "굿모닝 화면"; shot_name = sh.name
    c.keep_only("TextBox 33", "웃는 얼굴 40", "Table 404", "굿모닝 화면")
    table = shot_pic = None
    for sh in c.s.shapes:
        if sh.name == "Table 404": table = sh
        if sh.name == "굿모닝 화면": shot_pic = sh

    c.background(1000, 240)

    # ── 키메시지 ──
    km = c.text(0.20, 1.03, 10.43, 0.40, [[("보안관리 정책 및 지침 준수를 통해 ", 23, NV, "G마켓 산스 TTF Bold"),
                                           ("완벽한 기밀 보안 실현", 23, hexrgb("2070E8"), "G마켓 산스 TTF Bold")]])
    km.name = "키메시지"

    # 세로 대응(시안 y → inch)
    def L(y): return 1.67 + (y - 263) * 0.006369
    def R(y): return 1.67 + (y - 262) * 0.006115
    X = lambda x: x * K
    W = lambda a, b: (b - a) * K

    # ── 두 판 ──
    c.rrect(0.26, 1.62, 5.155, 5.40, adj=0.025, fill=PANEL, line=PANEL_LN, lw=1.0)
    c.rrect(5.51, 1.62, 5.08, 5.40, adj=0.025, fill=PANEL, line=PANEL_LN, lw=1.0)

    # ════════ 왼쪽: 보안취약점 진단 ════════
    c.write(c.pill(X(60), L(263), W(60, 995), L(330) - L(263), fill=BLUE1), [[("보안취약점 진단", 16, WHITE, F3)]])
    c.text(X(330), L(338), W(330, 726), L(368) - L(338), [[("체계적이고 표준화된", 9.5, TX, F2)]])
    c.text(X(300), L(368), W(300, 756), L(412) - L(368), [[("보안진단 활동 수행", 14, NV, F4)]])

    # 삼각 연결선
    ax, ay = X(528), L(414)
    for bx in (306, 752):
        c.line(ax, ay, X(bx), L(478), ARR, 1.0)
        c.oval(X(bx) - 0.025, L(478) - 0.025, 0.05, 0.05, fill=ARR)
    c.line(ax, ay, ax, L(426), ARR, 1.0)

    for cx_, y0, t1, col, t2 in ((226, 413, "기밀성", hexrgb("EC1C68"), "(Confidentiality)"),
                                 (528, 428, "무결성", hexrgb("1672F0"), "(Integrity)"),
                                 (825, 413, "가용성", hexrgb("138A2E"), "(Availability)")):
        c.text(X(cx_ - 130), L(y0), W(0, 260), L(y0 + 32) - L(y0), [[(t1, 12, col, F3)]])
        c.text(X(cx_ - 130), L(y0 + 32), W(0, 260), L(y0 + 62) - L(y0 + 32), [[(t2, 9.5, TX, F2)]])

    # 3D 아이콘(시안에서)
    for nm, x0, y0, x1 in (("shield", 148, 478, 300), ("lock", 440, 492, 616), ("bank", 742, 478, 918)):
        p = c.crop(nm, x0, y0, x1, 618, cut=(x0 + 2, y0 + 2), cut_thresh=24)
        pw = W(x0, x1); ph = pw * (618 - y0) / float(x1 - x0)
        c.pic(p, X(x0), L(618) - ph - (L(618) - L(478) - (618 - 478) * K) / 2, pw)

    # 산출물·보안진단도구·프로세스 카드
    cards = [
        (72, 362, 84, 356, "산출물", [["• 취약점진단 및 분석"], ["• 진단결과 조치 지원"], ["• 개선사항 도출 및 활동"]], "top"),
        (380, 682, 388, 673, "보안진단도구", [["• Tools"], ["  - 체크리스트"], ["  - ISO 27001", "(국제보안표준)"], ["  - 국정원 보안관리 수준평가 기준"]], "top"),
        (698, 982, 707, 961, "프로세스", [["• 진단 공정 절차(착수~종료)"]], "middle"),
    ]
    cy0, cy1 = 630, 782
    for x0, x1, h0, h1, head, lines, anc in cards:
        c.rrect(X(x0), L(cy0), W(x0, x1), L(cy1) - L(cy0), adj=0.07, fill=WHITE, line=CARD_LN, lw=0.75)
        hd = c.shape(MSO_SHAPE.ROUND_2_SAME_RECTANGLE, X(h0), L(cy0), W(h0, h1), L(668) - L(cy0), fill=BLUE1, adj=[0.35, 0])
        c.write(hd, [[(head, 9, WHITE, F3)]])
        rows = []
        for ln in lines:
            if len(ln) == 2:
                rows.append([(ln[0], 8, TX, F2), (ln[1], 7, TX, F2)])
            elif "국정원" in ln[0]:
                rows.append([(ln[0], 7, TX, F2)])
            else:
                rows.append([(ln[0], 8, TX, F2)])
        b = c.rect(X(x0 + 10), L(676), W(x0 + 10, x1 - 2), L(cy1 - 6) - L(676))
        c.write(b, rows, LEFT, anchor=anc, spacing=1.0)

    # 수행역량확보
    c.rrect(X(72), L(818), W(72, 975), L(926) - L(818), adj=0.12, fill=hexrgb("F7FBFF"), line=hexrgb("4BA4FD"), lw=2.0)
    c.write(c.pill(X(265), L(796), W(265, 778), L(836) - L(796), fill=hexrgb("3285F0")), [[("수 행 역 량 확 보", 11, WHITE, F3)]])
    caps = [(82, 294, "운영 및 유지관리", "전문사업 수행능력"), (306, 526, "유지관리 프로젝트", "BP 사례보유"),
            (540, 752, "보안진단 인프라", "및 노하우 보유"), (764, 966, "해당사업 정보보호", "경험 전문인력")]
    for x0, x1, a, b2 in caps:
        c.write(c.rrect(X(x0), L(846), W(x0, x1), L(910) - L(846), adj=0.18, fill=WHITE, line=CARD_LN, lw=0.75),
                [[(a, 8.5, TX, F3)], [(b2, 8.5, TX, F3)]], spacing=0.95)

    # 보안점검 단계
    steps = [(70, 312, ["보안점검 계획수립"]), (300, 534, ["보안점검 실시"]),
             (522, 758, ["정기 보안점검", "결과분석 및 조치"]), (746, 978, ["보안가이드 라인", "이력관리"])]
    for i, (x0, x1, t) in enumerate(steps):
        kind = MSO_SHAPE.PENTAGON if i == 0 else MSO_SHAPE.CHEVRON
        sh = c.shape(kind, X(x0), L(934), W(x0, x1), L(983) - L(934), fill=BLUE1, adj=[0.3])
        sh.text_frame.margin_left = Inches(0.12 if i else 0.02); sh.text_frame.margin_right = Inches(0.06)
        c.write(sh, [[(s, 8.5, WHITE, F3)] for s in t], spacing=0.9)
    descs = [(72, 292, ["• 정기 보안 취약점", "   진단 계획 수립", "• 자체 점검 계획 수립"]),
             (305, 525, ["• 자체 모의 점검 수행", "• 점검결과 분석 후 적용"]),
             (538, 752, ["• 보안점검 결과 분석 및", "   취약항목별 대응", "• 조치항목에 대한 일괄", "   적용 및 기술지원"]),
             (764, 976, ["• 자체 점검 결과를", "   토대로 시스템 보안", "   가이드라인 작성", "• 보안가이드라인 제출"])]
    for x0, x1, t in descs:
        c.rrect(X(x0), L(990), W(x0, x1), L(1092) - L(990), adj=0.07, fill=WHITE, line=CARD_LN, lw=0.75)
        b = c.rect(X(x0 + 8), L(998), W(x0 + 8, x1 - 2), L(1086) - L(998))
        c.write(b, [[(s, 7, TX, F2)] for s in t], LEFT, anchor="top", spacing=1.0)

    # ════════ 오른쪽: 보완 절차 및 주요 점검 항목 ════════
    c.write(c.pill(X(1030), R(264), W(1030, 1945), R(334) - R(264), fill=NAVYH), [[("보완 절차 및 주요 점검 항목", 16, WHITE, F3)]])

    # 머리 칸
    c.rrect(X(1037), R(347), W(1037, 1937), R(403) - R(347), adj=0.12, fill=WHITE, line=CARD_LN, lw=0.75)
    for xd in (1368, 1620):
        c.line(X(xd), R(351), X(xd), R(399), DIV, 0.75)
    c.text(X(1040), R(347), W(1040, 1365), R(403) - R(347), [[("상주 유지관리 담당자", 8.5, TX, F3)], [("전사지원", 8.5, TX, F3)]], spacing=0.95)
    c.text(X(1368), R(347), W(1368, 1620), R(403) - R(347), [[("청주시", 8.5, TX, F3)]])
    c.text(X(1620), R(347), W(1620, 1937), R(403) - R(347), [[("업무지원포털", 8.5, TX, F3)]])

    # 흐름 칸
    c.rrect(X(1037), R(408), W(1037, 1937), R(697) - R(408), adj=0.05, fill=hexrgb("EAF5FE"), line=CARD_LN, lw=0.75)
    for xd in (1378, 1620):
        c.line(X(xd), R(414), X(xd), R(692), DIV, 0.75)

    def icon(nm, x0, y0, x1, y1):
        p = c.crop(nm, x0, y0, x1, y1, cut=(x0 + 1, y0 + 1), cut_thresh=24)
        pw = W(x0, x1); ph = pw * (y1 - y0) / float(x1 - x0)
        c.pic(p, X(x0), (R(y0) + R(y1)) / 2 - ph / 2, pw)
    icon("clip", 1082, 412, 1164, 508)
    icon("lock2", 1252, 410, 1340, 508)
    icon("bank2", 1462, 412, 1554, 504)
    icon("person", 1262, 602, 1344, 674)

    c.text(X(1047), R(512), W(1047, 1197), R(590) - R(512),
           [[("보안취약점", 8, TX, F2)], [("점검계획수립", 8, TX, F2)], [("(대상범위 및 일정)", 8, TX, F2)]], spacing=0.95)
    c.text(X(1222), R(510), W(1222, 1372), R(583) - R(510),
           [[("보안취약점", 8, TX, F2)], [("점검 및 이행", 8, TX, F2)], [("여부 확인", 8, TX, F2)]], spacing=0.95)
    c.line(X(1297), R(585), X(1297), R(600), ARR, 1.0, arrow=True)
    c.text(X(1232), R(674), W(1232, 1362), R(697) - R(674), [[("담당자", 8.5, TX, F3)]])
    c.line(X(1180), R(466), X(1236), R(466), ARR, 1.25, arrow=True)
    c.line(X(1350), R(466), X(1456), R(466), ARR, 1.25, arrow=True)
    c.text(X(1340), R(420), W(1340, 1452), R(446) - R(420), [[("점검결과 보고", 8, TX, F2)]])
    c.text(X(1418), R(508), W(1418, 1588), R(556) - R(508), [[("청주시 IT서비스", 8, TX, F2)], [("책임자", 8, TX, F2)]], spacing=0.95)
    c.text(X(1392), R(568), W(1392, 1502), R(634) - R(568),
           [[("취약점", 8, TX, F2)], [("수정조치 후", 8, TX, F2)], [("반영", 8, TX, F2)]], spacing=0.95)
    # 되돌림 선: 담당자 → 위로 → 업무지원포털
    c.line(X(1352), R(640), X(1517), R(640), ARR, 1.0)
    c.line(X(1517), R(640), X(1517), R(555), ARR, 1.0)
    c.line(X(1517), R(555), X(1630), R(555), ARR, 1.25, arrow=True)

    # 굿모닝, ACE 틀 + 원래 화면 캡처
    if shot_pic is not None:
        ar = shot_pic.width / float(shot_pic.height)
        h = R(676) - R(428); w = h * ar
        maxw = W(1640, 1922)
        if w > maxw: w = maxw; h = w / ar
        cxm = X((1643 + 1918) / 2.0)
        shot_pic.left = Inches(cxm - w / 2); shot_pic.top = Inches((R(428) + R(676)) / 2 - h / 2); shot_pic.width = Inches(w); shot_pic.height = Inches(h)
        c.tree.remove(shot_pic._element); c.tree.append(shot_pic._element)

    # ── 점검항목 표(원래 값) ──
    if table is not None:
        table.left = Inches(X(1037)); table.top = Inches(4.41)
        tb = table.table
        for ri, row in enumerate(tb.rows):
            for ci, cell in enumerate(row.cells):
                if ri == 0:
                    _cell_style(cell, hexrgb("D2E8FD"), NV, "BDDCF9")
                elif ci == 0:
                    _cell_style(cell, hexrgb("E3F1FD"), hexrgb("12346F"), "BDDCF9")
                else:
                    _cell_style(cell, WHITE, TX, "BDDCF9")
        c.tree.remove(table._element); c.tree.append(table._element)
