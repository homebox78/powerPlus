# -*- coding: utf-8 -*-
"""s24 연계 현황 관리 절차 — 원본 1013x890px"""
from pptx.enum.shapes import MSO_SHAPE
from diag import Diagram, find_pic

B, E = "a시월구일2", "a시월구일3"
DOC = "assets/icon_398.png"


def build(prs):
    s = prs.slides[23]
    d = Diagram(s, find_pic(s, 276), 1013, 890)

    # 레인
    d.box(0, 50, 268, 840, fill="near")
    d.box(557, 50, 456, 840, fill="near")
    d.rbox(0, 0, 1013, 50, "", fill="navy", radius=0.2)
    d.label(0, 0, 268, 50, "연계대상기관", size=8, color="white", face=E)
    d.label(268, 0, 289, 50, "청주시", size=8, color="white", face=E)
    d.label(557, 0, 456, 50, "유지관리 담당자", size=8, color="white", face=E)
    d.vline(268, 10, 40, color="steel")
    d.vline(557, 10, 40, color="steel")

    W = dict(fill="white", color="ink", face=B, size=7)          # 흰 상자
    K = dict(fill="white", line="steel", color="navy", face=E, size=7, lw=1.0)  # 테두리 상자
    d.box(28, 57, 972, 48, "사전 연계 협의", **K)
    d.box(25, 148, 218, 37, "연계 요청 공문 접수", **W)
    d.box(303, 140, 212, 58, "연계 요청\n(공문)", align="l", **K)
    d.box(610, 140, 355, 38, "연계정보 및 기술검토", **W)
    d.label(288, 205, 150, 95, "• 연계신청서\n• 연계정의서\n• 변경신청서", align="l", color="ink2")
    d.image(440, 205, 75, 85, DOC)
    d.box(25, 291, 218, 37, "연계 검토 의견", **W)
    d.label(45, 352, 210, 70, "• 연계 방식 결정\n• 연계 일정 등 제시", align="l", color="ink2")
    d.box(300, 328, 212, 80, "연계 검토의견\n공문 수신 및\n의사결정사항 전달", align="l", **K)
    d.box(282, 430, 248, 80, "", fill="tint", line="steel", shape=MSO_SHAPE.DIAMOND, lw=1.0)
    d.label(322, 430, 168, 80, "연계 여부 확정?", color="navy", face=E)
    d.box(345, 533, 121, 34, "종 료", fill="teal", color="white", size=7)
    d.box(610, 452, 355, 35, "서비스요청관리", **W)
    d.box(607, 508, 356, 37, "연계현황정보 등록/수정", **W)

    # 모듈 구현 / 변경요청관리 묶음
    for gx0, gx1, title, items, ix0, ix1 in [
        (23, 260, "연계모듈 구현", ["연계 모듈 개발", "연계 테스트", "연계모듈 적용"], 45, 230),
        (573, 1000, "변경요청관리", ["연계 모듈 개발", "연계 테스트", "배포"], 601, 970)]:
        d.box(gx0, 560, gx1 - gx0, 182, fill="near", line="steel", lw=1.0)
        d.box(gx0 + 2, 560, gx1 - gx0 - 4, 37, title, fill="white", line="steel", color="navy", face=E, size=7)
        cx = (ix0 + ix1) / 2
        for k, t in enumerate(items):
            y0 = 606 + k * 46
            d.box(ix0, y0, ix1 - ix0, 35, t, **W)
            if k:
                d.line([(cx, y0 - 11), (cx, y0)], color="silver")
    d.line([(260, 668), (573, 668)], color="silver", dash=True, head=True)
    d.box(360, 655, 100, 26, "상호확인", fill="near", color="ink2", face=B, size=7)

    d.image(100, 752, 70, 75, "assets/icon_1386.png")
    d.label(45, 830, 200, 30, "연계확인서 공문 발송", color="ink2")
    d.box(300, 770, 226, 28, "연계확인서 공문수신", **K)
    d.box(610, 765, 353, 40, "연계현황정보 내역 변경", **W)
    d.box(685, 830, 210, 40, "연계 완료", fill="teal", color="white", size=8)

    L = lambda pts, **k: d.line(pts, color="silver", **k)
    L([(422, 105), (422, 133)])
    L([(303, 170), (243, 170)])
    L([(610, 170), (515, 170)], dash=True)
    L([(133, 185), (133, 291)])
    L([(243, 310), (405, 310), (405, 328)])
    L([(405, 408), (405, 430)])
    L([(530, 470), (610, 470)])
    L([(405, 510), (405, 533)])
    L([(785, 487), (785, 508)])
    L([(785, 545), (785, 560)])
    L([(785, 742), (785, 765)])
    L([(785, 805), (785, 830)])
    L([(185, 785), (300, 785)])
    L([(526, 785), (610, 785)])
    L([(136, 742), (136, 752)])
    d.label(532, 440, 40, 26, "예", color="crimson", face=E)
    d.label(296, 506, 100, 26, "아니오", color="crimson", face=E, align="r")
    d.finish()
