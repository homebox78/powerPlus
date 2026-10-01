# -*- coding: utf-8 -*-
"""17쪽(유지보수 관리 체계 1/5) 원본 문구 복원. 인자: <src> <dst>
- 세 카드 일러스트 축소, 설명 칸 확대 → 원본 문장 전부(9pt, 핵심 구절 강조 서체)
- 방법론 막대: '운영 및 유지보수 방법론(S-ISM)' 원문, 글자 10pt
- 하단: 원문 '과업유형(운영·유지/기능개발/사업관리) 및 특성에 맞는 방법론 선택 커스터마이징', 인물 20% 축소"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from pptx import Presentation
from pptx.util import Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from lib_e import *

sys.stdout.reconfigure(encoding="utf-8")
src, dst = sys.argv[1:3]
p = Presentation(src); s = p.slides[16]
by = by_id(s)

# 1) 방법론 막대
for icon, txt, ix, tx, tw, label in ((60, 61, 0.66, 1.04, 2.58, "운영 및 유지보수 방법론(S-ISM)"),
                                     (63, 64, 4.36, 4.74, 1.98, "사업관리방법론(S-PMM)"),
                                     (66, 67, 7.52, 7.90, 2.38, "기능 개발방법론(S-SEM)")):
    by[icon].left = I(ix)
    t = by[txt]; place(t, x=tx, w=tw, y=1.71, h=0.32)
    color = t.text_frame.paragraphs[0].runs[0].font.color.rgb
    fill_tf(t, [label], 10.5, color=color, font=F4, anchor=MSO_ANCHOR.MIDDLE, wrap=False, margins=(0.0, 0.0))

# 2) 카드 머리
for i, sz in ((73, 13), (104, 13)):
    for r in by[i].text_frame.paragraphs[0].runs:
        r.font.size = Pt(sz)
for i in (75, 106):
    for r in by[i].text_frame.paragraphs[0].runs:
        r.font.size = Pt(9.5)
for r in by[89].text_frame.paragraphs[0].runs:
    r.font.size = Pt(11)
by[89].top = I(2.57)
for r in by[90].text_frame.paragraphs[0].runs:
    r.font.size = Pt(9.5)
by[90].top = I(2.83); by[90].height = I(0.21)

# 3) 일러스트 축소, 설명 칸 확대
cards = [(70, 76), (86, 91), (101, 107)]
for card, pic in cards:
    c = by[card]
    fit_pic(by[pic], (c.left + c.width / 2) / 914400, 3.50, h=0.70)
for b in (77, 92, 108):
    place(by[b], y=3.92, h=1.48)

cols = {
    0: (77, [78, 80, 82, 84], [
        [("기존 서비스 안정성, 지속성, 사용 용이성 등", F2, TXT), ("사용자 중심 고려", F3, INK)],
        [("비상시 업무 연속성 확보", F3, INK), (" 운영", F2, TXT)],
        [("백업 및 복구, 보안 관련 등 꼼꼼한", F2, TXT), ("백-오피스 지원", F3, INK)],
        [("변경사항 즉시 현행화", F3, INK), (" 관리", F2, TXT)]]),
    1: (92, [93, 95, 97, 99], [
        [("시스템 특성상, 시스템적·법제도적 행정환경변화에 대한 ", F2, TXT), ("신속한 반응과 반영 필요", F3, INK)],
        [("변화에 따른 ", F2, TXT), ("관리 차원 현행화", F3, INK)],
        [("전사차원에서 행정환경변화 감지 및", F2, TXT), ("대응 전략 및 방안 지원", F3, INK)],
        [("중/장기적 변화 대비", F3, INK)]]),
    2: (108, [109, 112, 114], [
        [("사용자와 밀착 면담", F3, INK), ("을 통해 기존 서비스의개선 사항이나 ", F2, TXT), ("새로운 서비스 발굴", F3, INK)],
        [("정기적·비정기적 요구사항 파악", F3, INK), (" 절차 수행", F2, TXT)],
        [("서비스 만족도 점검", F3, INK)]]),
}
kill(s, [79, 81, 83, 85, 94, 96, 98, 100, 110, 111, 113, 115])
SZ, LH = 9.5, 0.168
for k, (panel, pics, items) in cols.items():
    pb = by[panel]
    px = pb.left / 914400; tw = pb.width / 914400 - 0.42
    lines = [1 + "".join(t for t, _, _ in it).count("") for it in items]
    gap = 0.07
    total = sum(lines) * LH + gap * (len(items) - 1)
    y = 4.06
    for it, n, pic in zip(items, lines, pics):
        ip = by[pic]
        ip.left = I(px + 0.11); ip.top = I(y + (LH - 0.15) / 2 + 0.005)
        textbox(s, px + 0.33, y - 0.01, tw, n * LH + 0.02, [it], SZ, line_spacing=1.0)
        y += n * LH + gap

# 4) 하단 방법론 막대
w = by[120]; bottom = (w.top + w.height) / 914400
fit_pic(w, 0.45 + 1.88 * 0.8 / 2, bottom - 1.59 * 0.8 / 2, h=1.59 * 0.8)
place(by[116], x=2.12, w=8.41)
by[117].left = I(2.36)
by[118].left = I(3.00)
t = by[119]; place(t, x=3.16, w=7.30, y=6.02, h=0.42)
fill_tf(t, [[("과업유형(운영·유지/기능개발/사업관리) 및 특성에 맞는 방법론 선택 ", F4, NAVY), ("커스터마이징", F4, BLUE)]],
        12.5, anchor=MSO_ANCHOR.MIDDLE, wrap=False, margins=(0.0, 0.0))

p.save(dst)
print("saved", dst)
