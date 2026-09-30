"""v0.69 원본 대조 결과 중 객관적 표기 오류 수정. 인자: <src> <dst> [--dry]"""
import sys
from pptx import Presentation
sys.stdout.reconfigure(encoding="utf-8")
src, dst = sys.argv[1:3]
DRY = "--dry" in sys.argv
pr = Presentation(src)

R = {
    4: [("4개구청", "4개 구청"), ("43개읍면동", "43개 읍면동"), ("16개도서관", "16개 도서관"), ("시본청", "시 본청")],
    5: [("(2006 - 2013)", "(2006 ~ 2013)"), ("(2004  ~ )", "(2004 ~)"), ("7개분야", "7개 분야"), ("Single sign On", "Single Sign-On")],
    8: [("장기계속계약 사용자와", "장기계속계약사업으로 사용자와")],
    9: [("전략1  ", "전략1 "), ("전략2  ", "전략2 "), ("전략3  ", "전략3 ")],
    10: [("시스템 목적 사상", "시스템 목적·사상"), ("업무지식 기술역량", "업무지식 및 기술역량")],
    11: [("연계모니터링", "연계 모니터링"), ("최우선 입니다", "최우선입니다")],
    12: [("지속가능한", "지속 가능한"), ("변경요청을 검토하고 승인합니다", "변경 영향을 평가·처리하고 주관기관 승인을 받습니다")],
    13: [("담당자들간의", "담당자들 간의")],
    14: [("전체의견수렴", "전체 의견수렴")],
    16: [("서비스요청유형 특성 처리", "요청유형별 특성에 맞는 처리")],
    17: [("운영 및 유지보수(S-ISM)", "운영·유지보수 방법론(S-ISM)"),
         ("사용자와 밀착 면담 기존 개선 사항", "사용자 밀착 면담으로 기존 개선 사항"),
         ("정기적 비정기", "정기·비정기"), ("기존기능", "기존 기능")],
    18: [("착수부터 종료 안정적", "착수부터 종료까지 안정적")],
    19: [("신구 시스템", "신·구 시스템")],
    22: [("상시 투입 가능한 전문 인력 Pool 구축", "즉시 대체 가능한 전문 인력 Pool 구축")],
    23: [("업무 인계팀 업무 인수팀 지원", "업무 인계팀·인수팀 지원")],
    25: [("모드로운영", "모드로 운영"), ("적용하여복구", "적용하여 복구")],
    27: [("제거 ,", "제거,"), ("편의성  증진", "편의성 증진"), ("개선 안 도출", "개선안 도출")],
    29: [("따라구분", "따라 구분"), ("인계인수등", "인계인수 등"), ("작성참여", "작성 참여"), ("인계 인수", "인계인수")],
    31: [("메뉴얼", "매뉴얼"), ("테스크", "태스크")],
    32: [("(2024,2025)", "(2024, 2025)")],
    33: [("프러덕트", "프로덕트"), ("미 달성", "미달성")],
    34: [("1개월이내", "1개월 이내"), ("지표별측정결과", "지표별 측정결과"), ("년 SLA실적보고서", "연간 SLA실적보고서")],
    35: [("2026.8월", "2026. 8월")],
    37: [("(2009,", "(2009년,"), ("산업 포장", "산업포장")],
    38: [("20여년", "20여 년"), ("녹아있어", "녹아 있어"), ("제시 합니다", "제시합니다")],
}
PAGES = {  # 41쪽 세부평가항목 → 쪽
    "유지보수 관리체계 및 절차의 적정성": "17 ~ 21", "유지보수 인력투입 계획의 적정성": "22",
    "인수인계 방안의 적정성": "23", "시스템 연계 및 관리의 적정성": "24",
    "비상대책(백업/복구, 장애대응)": "25", "기능 및 성능 요구 충족도": "26 ~ 27",
    "보안진단 및 조치·관리방안": "28", "사용자 교육 계획": "29", "관리방법론의 적정성": "31",
    "사업수행조직의 적정성": "32", "품질보증 및 제조사 등 기술 지원 방안": "33",
}


def walk(shs):
    for sh in shs:
        if sh.shape_type == 6:
            yield from walk(sh.shapes)
        else:
            yield sh


def paras(sl):
    for sh in walk(sl.shapes):
        if sh.has_text_frame:
            yield from sh.text_frame.paragraphs
        elif getattr(sh, "has_table", False) and sh.has_table:
            for row in sh.table.rows:
                for c in row.cells:
                    yield from c.text_frame.paragraphs


def rep(pg, old, new):
    runs = list(pg.runs)
    n = 0
    for r in runs:
        if old in r.text:
            n += r.text.count(old)
            if not DRY:
                r.text = r.text.replace(old, new)
    if n:
        return n
    full = "".join(r.text for r in runs)
    if old not in full:
        return 0
    # 여러 런에 걸침: 걸친 첫 런에 합치고 나머지 런에서 해당 부분 제거
    start = full.index(old)
    end = start + len(old)
    pos = 0
    first = True
    for r in runs:
        a, b = pos, pos + len(r.text)
        pos = b
        if b <= start or a >= end:
            continue
        s, e = max(a, start) - a, min(b, end) - a
        if not DRY:
            r.text = r.text[:s] + (new if first else "") + r.text[e:]
        first = False
    return 1


tot = 0
for no, pairs in R.items():
    sl = pr.slides[no - 1]
    for old, new in pairs:
        n = sum(rep(pg, old, new) for pg in paras(sl))
        tot += n
        print("%02d %-28s → %-28s %s" % (no, old, new, n if n else "없음!"))

# 5쪽 숨은 메모 — 규칙상 지우지 않음(슬라이드 밖 유지)

# 4쪽 사용자 조직: 원본 내용 복원(설명 줄 추가, 테두리 상자 아래로 늘림)
from pptx.util import Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
IN = 914400
s4 = pr.slides[3]
SUB = {"시안 43": "평생학습관", "시안 37": "보건소 4곳\n(상당·서원·\n청원·흥덕)", "시안 46": "사업소·박물관·\n미술관 등"}
for sh in list(s4.shapes):
    if sh.name == "시안 46" and not DRY:
        sh.text_frame.paragraphs[0].runs[0].text = "사업본부"
    if sh.name == "시안 26" and not DRY:
        sh.height = Emu(sh.height + int(0.42 * IN))
    if sh.name in SUB and not DRY:
        tb = s4.shapes.add_textbox(sh.left - int(0.04 * IN), sh.top + sh.height + int(0.03 * IN), sh.width + int(0.08 * IN), int(0.46 * IN))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.TOP
        for m in ("margin_left", "margin_right", "margin_top", "margin_bottom"):
            setattr(tf, m, 0)
        for k, line in enumerate(SUB[sh.name].split("\n")):
            pg = tf.paragraphs[0] if k == 0 else tf.add_paragraph()
            pg.alignment = PP_ALIGN.CENTER
            r = pg.add_run()
            r.text = line
            r.font.size = Pt(7)
            r.font.name = "a시월구일2"
            r.font.color.rgb = RGBColor.from_string("5F7496")
            rpr = r._r.get_or_add_rPr()
            ea = rpr.makeelement("{http://schemas.openxmlformats.org/drawingml/2006/main}ea", {"typeface": "a시월구일2"})
            rpr.append(ea)
        tb.name = "원본복원 " + sh.name
        print("04 설명 추가", sh.text_frame.text, "/", SUB[sh.name].replace("\n", " "))

# 41쪽 쪽 번호
for sh in walk(pr.slides[40].shapes):
    if getattr(sh, "has_table", False) and sh.has_table:
        for row in sh.table.rows:
            cells = list(row.cells)
            texts = [c.text_frame.text.strip() for c in cells]
            for k, v in PAGES.items():
                if k in texts:
                    last = cells[-1]
                    old = last.text_frame.text.strip()
                    print("41 %s: %s → %s" % (k, old, v))
                    if not DRY and old != v:
                        pg = last.text_frame.paragraphs[0]
                        pg.runs[0].text = v
                        for r in pg.runs[1:]:
                            r.text = ""
if not DRY:
    pr.save(dst)
print("치환", tot)
