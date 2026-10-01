# -*- coding: utf-8 -*-
"""17쪽(유지보수 관리 체계 1/5) 2차: 원본 구조로 재구성. 인자: <src> <dst>
- 방법론 3종을 카드 위 한 줄 머리띠로(+ 이음), 카드 머리 두 줄 제목 13.5pt
- 3D 일러스트·하단 인물 삭제, 원본 문장 10.5pt(위·아래 두 칸)
- 하단: 남색 '방법론' 칸 + 원문 막대 13.5pt 가로 전체"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from pptx import Presentation
from lib_g import *

sys.stdout.reconfigure(encoding="utf-8")
src, dst = sys.argv[1:3]
p = Presentation(src); s = p.slides[16]
icons = [pic_blob(s, i) for i in (72, 88, 103)]
purge(s)

COLS = [BLUE, MID, NAVY]
GAP = 0.14
cw = (W - GAP * 4) / 3
cx = [L + GAP + k * (cw + GAP) for k in range(3)]

# 1) 방법론 머리띠(카드 열과 같은 폭) + 이음 기호
BY, BH = 1.62, 0.50
labels = ["운영 및 유지보수 방법론(S-ISM)", "사업관리방법론(S-PMM)", "기능 개발방법론(S-SEM)"]
seg = W / 3
for k in range(3):
    tb(s, L + k * seg, BY, seg, BH, [labels[k]], 13.5, fill=COLS[k], line=None, color=WHITE, font=F4,
       align=PP_ALIGN.CENTER, wrap=False, margins=(0.0, 0.0))
for k in (1, 2):
    jx = L + k * seg
    box(s, jx - 0.19, BY + BH / 2 - 0.19, 0.38, 0.38, fill=WHITE, line=COLS[k - 1], lw=1.5, shape=MSO_SHAPE.OVAL)
    pl = box(s, jx - 0.11, BY + BH / 2 - 0.11, 0.22, 0.22, fill=COLS[k - 1], line=None, shape=MSO_SHAPE.MATH_PLUS)
    pl.adjustments[0] = 0.18

# 2) 세 카드를 감싸는 판
PY0, PY1 = BY + BH, 5.60
box(s, L, PY0, W, PY1 - PY0, fill=WHITE, line=LIGHT, lw=1, shape=MSO_SHAPE.RECTANGLE)

heads = ["유지관리\v기존 기능 안정적 운영", "시스템·법제도\v환경변화 신속 지원", "신규 요구사항\v기능 개발 지원"]
k3 = lambda t: (t, F3, INK)
k2 = lambda t: (t, F2, TXT)
bodies = [
    ([[k2("기존 서비스 안정성, 지속성, 사용 용이성 등\v"), k3("사용자 중심 고려")],
      [k3("비상시 업무 연속성 확보"), k2(" 운영")]],
     [[k2("백업 및 복구, 보안 관련 등 꼼꼼한\v"), k3("백-오피스 지원")],
      [k3("변경사항 즉시 현행화"), k2(" 관리")]]),
    ([[k2("시스템 특성상, 시스템적·법제도적\v행정환경 변화에 대한 "), k3("신속한 반응과\v반영 필요")],
      [k2("변화에 따른 "), k3("관리 차원 현행화")]],
     [[k2("전사차원에서 행정환경변화 감지 및\v"), k3("대응 전략 및 방안 지원")],
      [k3("중/장기적 변화 대비")]]),
    ([[k3("사용자와 밀착 면담"), k2("을 통해\v기존 서비스의 개선 사항이나\v"), k3("새로운 서비스 발굴")]],
     [[k3("정기적·비정기적 요구사항 파악"), k2("\v절차 수행")],
      [k3("서비스 만족도 점검")]]),
]
HY, HH = PY0 + 0.16, 0.72
UY = HY + HH
UH = 1.24
LY = UY + UH
LH = PY1 - 0.14 - LY
for k in range(3):
    x = cx[k]
    tb(s, x, HY, cw, HH, [heads[k]], 13.5, fill=COLS[k], line=None, color=WHITE, font=F4,
       align=PP_ALIGN.CENTER, margins=(0.45, 0.02), line_spacing=1.0)
    add_pic(s, icons[k], x + 0.30, HY + HH / 2, 0.36)
    up, lo = bodies[k]
    tb(s, x, UY, cw, UH, up, 10.5, fill=WHITE, line=LIGHT, lw=1, bullet="•", margins=(0.14, 0.04),
       space_after=4)
    tb(s, x, LY, cw, LH, lo, 10.5, fill=PALE, line=LIGHT, lw=1, bullet="•", margins=(0.14, 0.04),
       space_after=4)

# 3) 아래로 모이는 납작한 삼각형
tri = box(s, L + W * 0.30, 5.68, W * 0.40, 0.26, fill=LIGHT, line=None, shape=MSO_SHAPE.ISOSCELES_TRIANGLE)
tri.rotation = 180

# 4) 하단 '방법론' + 원문 막대
FY, FH = 6.08, 0.88
LW = 1.85
tb(s, L, FY, LW, FH, ["방법론"], 20, fill=NAVY, line=None, color=WHITE, font=F4, align=PP_ALIGN.CENTER,
   margins=(0.0, 0.0))
tb(s, L + LW, FY, W - LW, FH,
   [[("과업유형(운영·유지/기능개발/사업관리) 및 특성에 맞는 방법론 선택 ", F4, NAVY), ("커스터마이징", F4, BLUE)]],
   13.5, fill=PALE, line=None, align=PP_ALIGN.CENTER, wrap=False, margins=(0.0, 0.0))

p.save(dst)
print("saved", dst)
