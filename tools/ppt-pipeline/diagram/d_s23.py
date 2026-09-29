# -*- coding: utf-8 -*-
"""s23 인수인계 절차 — 원본 1016x908px"""
from pptx.enum.shapes import MSO_SHAPE
from diag import Diagram, find_pic

B, E = "a시월구일2", "a시월구일3"


def build(prs):
    s = prs.slides[22]
    d = Diagram(s, find_pic(s, 355), 1016, 908)

    # 상단 단계 화살표
    d.box(100, 0, 293, 133, "", fill="mist", shape=MSO_SHAPE.PENTAGON)
    d.label(110, 0, 250, 133, "인수인계 착수", size=8, color="navy", face=E)
    d.box(360, 0, 445, 133, "", fill="mist", shape=MSO_SHAPE.CHEVRON)
    d.label(410, 0, 345, 68, "인수현황 통제", size=8, color="navy", face=E)
    d.box(400, 70, 365, 60, "인수현황 수행", fill="steel", color="white", size=8)
    d.box(762, 0, 253, 133, "", fill="mist", shape=MSO_SHAPE.CHEVRON)
    d.label(800, 0, 150, 133, "인수\n인계\n종료", size=8, color="navy", face=E)

    # 좌측 행 머리
    R = dict(fill="azure", color="white", size=8, radius=0.18)
    d.rbox(0, 155, 95, 117, "단계", **R)
    d.rbox(0, 310, 95, 332, "수행\n활동", **R)
    d.rbox(0, 683, 95, 225, "사업자\n변경시\n인계", **R)

    # 패널
    P = dict(fill="white", line="gray", radius=0.03)
    d.rbox(95, 133, 255, 522, **P)
    d.rbox(357, 133, 405, 415, **P)
    d.rbox(770, 133, 203, 522, **P)

    # 단계 상자
    S = dict(fill="tint", color="navy", size=7, radius=0.1, margin=0)
    for x0, x1, t in [(105, 219, "착수준비"), (227, 343, "계획수립"), (367, 490, "인수인계\n실시"),
                      (498, 620, "공동운영"), (628, 752, "단독운영"), (780, 866, "인수확인"),
                      (875, 965, "완료보고")]:
        d.rbox(x0, 148, x1 - x0, 129, t, **S)

    # 수행 활동
    acts = [(104, 222, "·조직구성\n·이관방안\n·교육 실시\n·업무범위\n  정의\n·교육\n·현황자료\n  요청"),
            (230, 352, "·일정계획\n  수립\n·의사소통\n  계획 수립\n·착수보고\n  실시\n·인수인계\n  안내"),
            (367, 490, "·산출물인수\n·현황 검토\n·업무상세\n  교육\n·업무별\n  인수인계"),
            (499, 622, "·운영방안\n  정의\n·공동운영\n·매뉴얼 정의"),
            (630, 755, "·단독운영\n  안내\n·시스템 백업\n·단독운영\n  실시"),
            (779, 870, "·최종인수\n  인계확인"),
            (878, 970, "·운영계획\n  수립\n·인수인계\n  완료보고")]
    for x0, x1, t in acts:
        d.label(x0 + 4, 298, x1 - x0 - 6, 240, t, size=7, color="ink", face=B, align="l", anchor="t", spc=-50)
    for x, y1 in [(226, 640), (493, 535), (625, 535), (873, 640)]:
        d.vline(x, 290, y1, color="silver", dash=True)
        d.box(x - 4, y1 - 4, 8, 8, fill="silver", shape=MSO_SHAPE.OVAL)

    d.box(357, 562, 405, 92, "위험/이슈 정의 및 관리\n중요사항 협의/요청",
          fill="tint", line="mist", color="navy", size=7, face=E)

    # 하단: 사업자 변경시 인계 4단계
    d.rbox(95, 675, 878, 231, fill="white", line="gray", radius=0.04)
    items = [(205, "인수인계\n사전준비", "ink"), (425, "인수인계\n실시", "ink"),
             (645, "공동\n운영", "ink"), (865, "비상주\n운영지원", "crimson")]
    for i, (cx, t, col) in enumerate(items, 1):
        d.box(cx - 86, 704, 172, 172, "", fill="white", line="gray", shape=MSO_SHAPE.OVAL, lw=4)
        d.label(cx - 80, 704, 160, 172, t, size=9, color=col, face=E)
        d.box(cx - 62, 712, 32, 32, str(i), fill="navy", color="white", size=7, shape=MSO_SHAPE.OVAL)
    for x0 in (297, 517, 737):
        d.line([(x0, 797), (x0 + 36, 797)], color="silver", lw=1.5)
    d.finish()
