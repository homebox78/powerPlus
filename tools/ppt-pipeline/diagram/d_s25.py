# -*- coding: utf-8 -*-
"""s25 장애관리 3단계 절차 · 백업/복구 6단계 · 백업 주기 표 · 백업·복구 방법 상자"""
from pptx.enum.shapes import MSO_SHAPE
from diag import Diagram, find_pic

B, E = "a시월구일2", "a시월구일3"


def incident(s):
    d = Diagram(s, find_pic(s, 13), 442, 628)
    d.box(18, 8, 110, 70, "", fill="crimson", shape=MSO_SHAPE.EXPLOSION1)
    d.label(30, 8, 86, 70, "장애발생", color="white", face=E)
    d.line([(132, 42), (190, 42)], color="silver", lw=3)

    def card(y0, y1, head, body):
        d.box(195, y0, 237, 24, head, fill="steel", color="white", size=7)
        d.box(195, y0 + 24, 237, y1 - y0 - 24, body, fill="white", line="steel",
              color="ink", face=B, size=7, align="l", anchor="t", spc=-50)
    card(5, 102, "장애 접수 및 내용 분석", "• 장애 유형 구분\n   - H/W, 어플리케이션,\n     상용 S/W")
    card(228, 325, "장애 유형 세부 분석", "• 유형별 장애 분석\n• 자체 해결 또는 공급업체를\n   통한 신속한 조치")

    def dia(y0, y1, t):
        d.box(205, y0, 225, y1 - y0, "", fill="tint", line="steel", shape=MSO_SHAPE.DIAMOND)
        d.label(240, y0, 155, y1 - y0, t, color="navy", face=E)
    dia(135, 200, "1차 처리\n(단순 조치)")
    dia(358, 418, "2차 처리")
    dia(448, 512, "3차 처리\n(전문가 파견)")

    # 사용자
    d.box(22, 118, 106, 106, "", fill="white", line="steel", shape=MSO_SHAPE.OVAL, lw=2.5)
    d.image(48, 128, 54, 58, "assets/icon_1397.png")
    d.label(22, 188, 106, 28, "사용자", color="navy", face=E)

    d.box(195, 545, 237, 33, "장애 처리 결과 보고", fill="tint", color="navy", size=7)
    d.box(195, 588, 237, 33, "장애 처리 이력 관리", fill="tint", color="navy", size=7)

    L = lambda pts, **k: d.line(pts, color="silver", **k)
    L([(313, 102), (313, 135)]); L([(313, 200), (313, 228)]); L([(313, 325), (313, 358)])
    L([(313, 418), (313, 448)]); L([(313, 512), (313, 545)])
    L([(205, 167), (130, 167)])
    L([(205, 388), (75, 388)], arrow=False); L([(205, 480), (75, 480)], arrow=False)
    L([(313, 520), (75, 520), (75, 224)])
    for x, y, t in [(165, 132, "예"), (150, 180, "장애 해결"), (330, 200, "아니오"),
                    (90, 360, "장애 해결  예"), (330, 420, "아니오"), (90, 452, "장애 해결  예")]:
        d.label(x, y, 120, 26, t, color="ink2", align="l")
    d.label(0, 522, 195, 44, "장애 조치내역 통보\n(전화, E-mail, FAX 등)", color="ink2")
    d.finish()


def backup(s):
    d = Diagram(s, find_pic(s, 464), 1018, 595)
    d.rbox(4, 4, 1010, 587, fill="white", line="navy", radius=0.03, lw=1.0)
    cards = [  # 카드x, 카드y, 배지, 아이콘, 하단 띠, 부가 설명
        (68, 58, "백업대상", "assets/icon_1194.png", "백업 대상 자료 선정", "시스템 및\n사용자 DATA"),
        (405, 58, "백업진행", "assets/icon_572.png", "주기별 백업 진행", None),
        (740, 58, "백업관리", "assets/icon_1263.png", "백업 미디어 관리", None),
        (740, 338, "장애발생", "assets/icon_534.png", "장애 원인 분석", None),
        (405, 338, "백업복구", "assets/icon_1280.png", "백업 복구 진행", None),
        (68, 338, "정상운영", "assets/icon_1447.png", "시스템 정상 운영", None),
    ]
    for x, y, badge, ico, band, sub in cards:
        d.box(x, y, 252, 214, fill="white", line="gray")
        if sub:
            d.image(x + 110, y + 20, 110, 90, ico)
            d.label(x + 60, y + 108, 190, 60, sub, color="ink")
        else:
            d.image(x + 80, y + 30, 110, 130, ico)
        d.box(x, y + 174, 252, 40, band, fill="blue", color="white", size=8)
        d.box(x - 42, y - 34, 112, 112, "", fill="near", line="mist", shape=MSO_SHAPE.OVAL, lw=2)
        d.label(x - 42, y - 34, 112, 112, badge, color="navy", face=E)
    A = lambda pts: d.line(pts, color="steel", lw=2.5)
    A([(343, 165), (390, 165)])
    A([(680, 160), (725, 160)])
    A([(878, 285), (878, 322)])
    A([(715, 455), (670, 455)])
    A([(380, 455), (335, 455)])
    d.finish()


def cycle_table(s):
    d = Diagram(s, find_pic(s, 465), 1018, 323)
    rows = [["구분", "월단위", "주단위", "일단위"],
            ["대상\n자료", "OS 커널,\n시스템 관련 파일,\n응용프로그램", "전체 데이터베이스", "긴급한\n복구대상 정보"],
            ["백업\n방안", "Full 백업 진행", "DBMS 전체의\nCOLD 백업 진행", "중요파일\nIncremental 백업"],
            ["장애\n유형", "디스크 손상,\n사용자 실수로\n인한 정보 삭제", "데이터베이스\n시스템 테이블에\n장애 발생",
             "디스크 손상,\n사용자 실수로\n인한 정보 삭제"],
            ["복구\n방안", "해당 백업자료를\n재저장", "데이터베이스 복구\n오퍼레이션 수행", "주요 정보 재저장"]]
    d.table(0, 0, 1018, 345, rows, colw=[112, 302, 302, 302], size=7, row_h=[0.7, 1, 1, 1, 1])
    d.finish()


def method_box(s):
    d = Diagram(s, find_pic(s, 18), 240, 234)
    d.box(0, 0, 240, 234,
          "• 백업 방법\n  - DB Full 백업 수행\n  - DBMS는 아카이브 모드로 운영\n"
          "• 복구 방법\n  - DB 장애\n    : DB Data와 Log정보(Redo/\n      Archive Log)를 적용하여 복구",
          fill="near", line="gray", color="ink", face=B, size=7, align="l", anchor="m", spc=-50, margin=8)
    d.finish()


def build(prs):
    s = prs.slides[24]
    incident(s)
    backup(s)
    cycle_table(s)
    method_box(s)
