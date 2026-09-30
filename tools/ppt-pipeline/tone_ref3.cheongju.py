"""시안 캡처(2026-09-30, 11장)에서 읽은 팔레트로 값만 교체. 배치·그라데이션·초록 키메시지는 그대로.
   인자: 원본 결과"""
import sys, collections
from pptx import Presentation
sys.stdout.reconfigure(encoding="utf-8")
A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
MAP = {"0456B6": "2F78E0",   # 2단계: 선명한 파랑
       "658EBB": "78A8F0",   # 3단계: 밝은 파랑 알약
       "DEEBF7": "D0E6FA",   # 4단계: 카드 면
       "F2F7FC": "E8F2FC",   # 바탕 면
       "C0D2E6": "C2DCF5",   # 선
       "E84078": "EC1C68"}   # 포인트 핑크
BADGE = range(10, 15)        # 전략 번호 배지: 빨강 → 핑크
p = Presentation(sys.argv[1]); cnt = collections.Counter()
for n, sl in enumerate(p.slides, 1):
    for c in sl._element.iter(A + "srgbClr"):
        if A + "gradFill" in [a.tag for a in c.iterancestors()]: continue
        v = c.get("val").upper()
        if v in MAP: c.set("val", MAP[v]); cnt[v] += 1
        elif v == "D23737" and n in BADGE: c.set("val", "EC1C68"); cnt["badge"] += 1
print(dict(cnt)); p.save(sys.argv[2])
