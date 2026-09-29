# -*- coding: utf-8 -*-
"""s28 보안관리 — 보안 3요소 · 보안점검 4단계 · 취약점 진단 절차와 점검항목 표"""
from pptx.enum.shapes import MSO_SHAPE
from diag import Diagram, find_pic

B, E = "a시월구일2", "a시월구일3"


def triad(s):
    d = Diagram(s, find_pic(s, 204), 822, 532)
    d.label(0, 0, 822, 30, "체계적이고 표준화된", size=9, color="ink", face=E)
    d.label(0, 30, 822, 50, "보안진단 활동 수행", size=14, color="black", face="G마켓 산스 TTF Bold")
    d.box(95, 88, 632, 108, "", fill="near", shape=MSO_SHAPE.ISOSCELES_TRIANGLE)
    for cx, k, en, col in [(140, "기밀성", "(Confidentiality)", "crimson"), (410, "무결성", "(Integrity)", "navy"),
                           (680, "가용성", "(Availability)", "green")]:
        d.label(cx - 130, 112, 260, 36, k, size=11, color=col, face=E)
        d.label(cx - 130, 146, 260, 36, en, size=9, color="ink", face=B)
    panels = [(3, 265, "산출물", "• 취약점진단 및 분석\n• 진단결과 조치 지원\n• 개선사항 도출 및 활동"),
              (273, 535, "보안진단도구", "• Tools\n  - 체크리스트\n  - ISO 27001(국제보안표준)\n  - 국정원 보안관리 수준평가 기준"),
              (543, 807, "프로세스", "• 진단 공정 절차(착수~종료)")]
    for x0, x1, head, body in panels:
        d.box(x0, 200, x1 - x0, 168, fill="near", line="gray")
        d.rbox(x0 + 12, 208, x1 - x0 - 24, 32, head, fill="blue", color="white", size=9, radius=0.5)
        d.label(x0 + 14, 248, x1 - x0 - 24, 116, body, size=8, color="ink", face=B, align="l", anchor="t")
    d.rbox(3, 400, 805, 128, fill=None, line="cyan", lw=2.25, radius=0.08)
    d.rbox(170, 377, 480, 44, "수행역량확보", fill="cyan", color="white", size=10, radius=0.5, spc=300)
    for x0, x1, t in [(15, 195, "운영 및 유지관리\n전문사업 수행능력"), (218, 398, "유지관리 프로젝트\nBP 사례보유"),
                      (420, 600, "보안진단 인프라\n및 노하우 보유"), (622, 795, "해당사업 정보보호\n경험 전문인력")]:
        d.rbox(x0, 437, x1 - x0, 62, t, fill="near", color="ink", face=B, size=8, radius=0.1)
    d.finish()


def steps(s):
    d = Diagram(s, find_pic(s, 265), 756, 204)
    heads = [(0, 200, "보안점검 계획수립", "tint", "navy", MSO_SHAPE.PENTAGON),
             (185, 385, "보안점검 실시", "mist", "navy", MSO_SHAPE.CHEVRON),
             (370, 572, "정기 보안점검\n결과분석 및 조치", "steel", "white", MSO_SHAPE.CHEVRON),
             (557, 756, "보안가이드 라인\n이력관리", "blue", "white", MSO_SHAPE.CHEVRON)]
    for x0, x1, t, f, c, shp in heads:
        d.box(x0, 0, x1 - x0, 64, "", fill=f, shape=shp)
        d.label(x0 + 24, 0, x1 - x0 - 46, 64, t, size=8, color=c, face=E)
    d.box(0, 70, 756, 134, fill="near")
    bodies = [(8, 190, "• 정기 보안 취약점\n  진단 계획 수립\n• 자체 점검 계획 수립"),
              (198, 376, "• 자체 모의 점검 수행\n• 점검결과 분석 후 적용"),
              (384, 563, "• 보안점검 결과 분석 및\n  취약항목별 대응\n• 조치항목에 대한 일괄\n  적용 및 기술지원"),
              (571, 750, "• 자체 점검 결과를\n  토대로 시스템 보안\n  가이드라인 작성\n• 보안가이드라인 제출")]
    for x0, x1, t in bodies:
        d.label(x0, 80, x1 - x0, 116, t, size=7, color="ink", face=B, align="l", anchor="t")
    for x in (192, 378, 565):
        d.vline(x, 76, 186, color="silver", dash=True)
        d.box(x - 4, 186, 8, 8, fill="silver", shape=MSO_SHAPE.OVAL)
    d.finish()


def vuln(s):
    d = Diagram(s, find_pic(s, 289), 1026, 925)
    d.box(0, 0, 390, 415, fill="tint")
    d.box(0, 0, 1026, 66, fill="near")
    d.hline(0, 0, 1026, color="steel", lw=1.0); d.hline(66, 0, 1026, color="gray")
    d.vline(390, 0, 415, color="gray"); d.vline(673, 0, 415, color="gray")
    d.label(0, 0, 390, 66, "상주 유지관리 담당자\n전사지원", size=8, color="navy", face=E)
    d.label(390, 0, 283, 66, "청주시", size=8, color="navy", face=E)
    d.label(673, 0, 353, 66, "업무지원포털", size=8, color="navy", face=E)
    d.image(60, 82, 90, 82, "assets/icon_1454.png")
    d.label(10, 178, 190, 80, "보안취약점\n점검계획수립\n(대상범위 및 일정)", color="ink")
    d.image(262, 82, 80, 80, "assets/icon_1340.png")
    d.label(215, 162, 175, 80, "보안취약점\n점검 및 이행\n여부 확인", color="ink")
    d.image(262, 300, 80, 80, "assets/icon_1397.png")
    d.label(240, 380, 125, 30, "담당자", color="ink")
    d.image(480, 78, 90, 90, "assets/icon_1256.png")
    d.label(430, 168, 190, 50, "청주시 IT서비스\n책임자", color="ink")
    d.box(700, 100, 297, 257, fill="white", line="steel")
    d.image(704, 104, 289, 249, "assets/portal_ace.png")
    L = lambda pts, **k: d.line(pts, color="silver", **k)
    L([(150, 128), (255, 128)])
    L([(345, 122), (478, 122)])
    L([(302, 240), (302, 298)])
    L([(345, 322), (518, 322), (518, 228), (697, 228)])
    d.label(352, 88, 160, 30, "점검결과 보고", color="ink2", align="l")
    d.label(410, 234, 108, 80, "취약점\n수정조치 후\n반영", color="ink2")
    rows = [["점검항목", "산출물명"],
            ["XSS\n(Cross-Site Script)", "• 입력 값에 악성 XSS코드를 포함하는 객체 및 비정상적인 Script가\n  입력 또는 수행되는지 여부 진단"],
            ["SQL Injection", "• Injection 문자열 필터 및 비정상 SQL 구문, 취약한 SQL 문자열 사용 가능여부 점검"],
            ["File\nUpload & Download", "• 정해진 파일 경로 외 접근가능 여부 및 비 정상적 경로 파일 내려 받기 기능 점검\n• Server Side Script, 실행파일 등의 업로드 가능여부 및 파일경로 실행권한 점검"],
            ["URL 강제접속", "• 인증이 필요한 모든 페이지의 강제접속 가능여부 및 서버스크립트 사용가능여부 점검"],
            ["Buffer Overflow", "• 서버와 어플리케이션에 존재하는 Buffer Overflow 취약점을 주기적으로 점검"],
            ["HTTP Method", "• 취약한 HTTP Method를 사용하는지 여부 진단"],
            ["Email Exploitation", "• 내·외부에 노출된 전자우편 계정에 대한 WORM, VIRUS 유입 여부 점검"],
            ["Common File\nExtension", "• 개발자가 평상시 습관적으로 사용하는 일반적인 이름의\n  Backup 및 Source File Directory 등이 존재하는지 여부 진단\n• 개발 및 테스트를 위해 개발자가 남겨 둔 Back Door 점검 및 차단"],
            ["DDos", "• ICMP 패킷을 이용한 공격 가능여부 진단(Smurf, Fraggle, Ping of Death 등)\n• IP 데이터 그램 및 IP주소 위조 공격 가능여부 진단(Teardrop, Land 등)"]]
    d.table(0, 420, 1026, 505, rows, colw=[215, 811], size=7, row_h=[1, 2, 1, 2, 1, 1, 1, 1, 3, 2])
    d.finish()


def build(prs):
    s = prs.slides[27]
    triad(s)
    steps(s)
    vuln(s)
