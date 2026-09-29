# -*- coding: utf-8 -*-
"""s21 ① 테스트 방안 및 절차(4열) · ② 배포 절차 플로우차트"""
from pptx.enum.shapes import MSO_SHAPE
from diag import Diagram, find_pic


def test_flow(s):
    d = Diagram(s, find_pic(s, 2), 1018, 537)
    d.box(0, 0, 1018, 537, fill="white", line="navy", lw=1.0)
    cols = [  # 패널x0,x1, 머리글, 머리색, 글자색, 단계들[(y0,y1,글)], 마름모y, 되돌아갈 단계 index, 우측 루프 x
        (25, 258, "단위시험\n(개발환경)", "mist", "navy",
         [(110, 148, "단위시험계획 수립"), (180, 226, "시험데이터 준비"), (263, 309, "단위시험 실시")],
         (343, 430), (458, 503), 1, 262),
        (275, 510, "통합시험\n(개발환경)", "steel", "white",
         [(105, 155, "통합시험계획 수립"), (183, 230, "시험데이터 준비"), (265, 311, "통합시험 실시")],
         (345, 432), (463, 510), 1, 502),
        (514, 750, "통합시험\n(운영환경)", "blue", "white",
         [(110, 142, "운영 시험계획 수립"), (158, 192, "시스템 및 환경준비"), (219, 253, "시험 데이터 준비"),
          (285, 319, "운영 시험 실시")],
         (348, 432), (462, 510), 1, 745),
        (758, 1006, "연계시스템 통합시험\n(선택적)", "navy", "white",
         [(110, 142, "연계시험계획 수립"), (160, 194, "연계시험 협의(선택적)"), (221, 254, "연계 데이터 준비"),
          (280, 313, "연계 시험 실시")],
         (345, 432), (462, 510), 1, 1000),
    ]
    hx = [(45, 285), (272, 510), (510, 752), (740, 1010)]
    for i, (px0, px1, head, hf, hc, steps, dia, res, back, lx) in enumerate(cols):
        d.box(px0, 95, px1 - px0, 428, fill="near")
        d.box(hx[i][0], 14, hx[i][1] - hx[i][0], 76, "", fill=hf,
              shape=MSO_SHAPE.CHEVRON if i else MSO_SHAPE.PENTAGON)
        # 셰브런 글상자는 기하상 좁아 접힌다 → 위에 글상자를 얹는다
        d.label(hx[i][0] + 22, 14, hx[i][1] - hx[i][0] - 44, 76, head, color=hc, face="a시월구일3")
        bx0, bx1 = px0 + 6, px1 - 28
        cx = (bx0 + bx1) / 2
        prev = None
        for (y0, y1, t) in steps:
            d.box(bx0, y0, bx1 - bx0, y1 - y0, t, fill="white", line="gray", color="ink", face="a시월구일2", size=7)
            if prev is not None:
                d.line([(cx, prev), (cx, y0)], color="silver")
            prev = y1
        dx0 = cx - 47
        d.box(dx0, dia[0], 94, dia[1] - dia[0], "", fill="blue", shape=MSO_SHAPE.DIAMOND)
        d.label(dx0 + 10, dia[0], 74, dia[1] - dia[0], "요건\n충족", color="white", face="a시월구일3")
        d.line([(cx, prev), (cx, dia[0])], color="silver")
        d.box(bx0, res[0], bx1 - bx0, res[1] - res[0], "결과보고 및 검토", fill="white", line="gray",
              color="ink", face="a시월구일2", size=7)
        d.line([(cx, dia[1]), (cx, res[0])], color="silver")
        my = (dia[0] + dia[1]) / 2
        by = (steps[back][0] + steps[back][1]) / 2
        lx = px1 - 5
        d.line([(dx0 + 94, my), (lx, my), (lx, by), (bx1, by)], color="silver")
        d.label(dx0 + 90, dia[0] - 6, 50, 26, "NO", color="ink2")
        d.label(dx0 + 80, dia[1] - 4, 50, 26, "YES", color="ink2")
    d.finish()


def deploy_flow(s):
    d = Diagram(s, find_pic(s, 3), 1017, 982)
    P = dict(fill="mist", color="navy", face="a시월구일2", size=7)
    G = dict(fill="near", line="gray", color="ink", face="a시월구일2", size=7)
    d.box(421, 8, 252, 70, "프로그램/DB 변경", **P)
    d.box(712, 105, 305, 72, "DB 검증 (DB배포)", **G)
    d.box(423, 210, 250, 110, "", fill="tint", line="steel", shape=MSO_SHAPE.DIAMOND, lw=1.0)
    d.label(460, 210, 176, 110, "자체 테스트\n배포 실시", color="navy", face="a시월구일3")
    d.label(716, 232, 290, 66, "자체 배포 테스트\n실패일 경우 배포 연기", align="l", color="ink")
    d.box(149, 391, 252, 71, "운영서버 배포 승인", **P)
    d.box(712, 371, 305, 177, "배포·적용시간은\n업무 마감 후에 실시\n고객의 승인단계 포함", **G)
    d.box(421, 498, 252, 70, "운영서버 배포 수행", **P)
    d.box(4, 607, 248, 111, "", fill="tint", line="steel", shape=MSO_SHAPE.DIAMOND, lw=1.0)
    d.label(34, 607, 188, 111, "운영서버 배포\n장애여부", color="navy", face="a시월구일3")
    d.box(421, 640, 252, 70, "운영서버 배포 확인", **P)
    d.box(706, 640, 306, 72, "통합테스트 수행", **G)
    d.box(149, 910, 252, 70, "운영서버 배포 결과확인", **P)
    d.box(421, 910, 252, 70, "운영서버 배포 결과보고", **P)

    L = lambda pts, **k: d.line(pts, color="silver", **k)
    L([(547, 78), (547, 210)])
    L([(712, 141), (547, 141)], arrow=False)
    L([(423, 265), (384, 265), (384, 44), (421, 44)])
    L([(128, 607), (128, 44), (384, 44)], arrow=False)
    L([(547, 320), (547, 428), (401, 428)])
    L([(276, 462), (276, 533), (421, 533)])
    L([(547, 568), (547, 640)])
    L([(706, 676), (673, 676)])
    L([(421, 672), (252, 672)])
    L([(128, 718), (128, 814), (547, 814)], arrow=False)
    L([(547, 710), (547, 910)])
    L([(421, 945), (401, 945)])
    for x, y, t in [(180, 4, "원상복구"), (386, 196, "실패"), (555, 332, "성공"), (218, 818, "정상")]:
        d.label(x, y, 110, 34, t, color="ink2", align="l")
    d.finish()


def build(prs):
    s = prs.slides[20]
    test_flow(s)
    deploy_flow(s)
