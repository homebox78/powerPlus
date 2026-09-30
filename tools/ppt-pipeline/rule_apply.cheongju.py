"""디자인 시스템 7절 적용 1단계 — 블루 4단계 흡수 + 본문 글자색 한 값.
   그라데이션 스톱은 건드리지 않는다."""
import sys, collections
from pptx import Presentation
sys.stdout.reconfigure(encoding="utf-8")
A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
SRC, DST = sys.argv[1], sys.argv[2]
BLUE = {"1973D1": "0456B6", "3A46A0": "0B2E6B"}
TEXT = {"333F50": "2F3B6F", "404040": "2F3B6F"}
TXT_TAGS = {A + "rPr", A + "defRPr", A + "endParaRPr"}
p = Presentation(SRC)
cnt = collections.Counter()
for n, sl in enumerate(p.slides, 1):
    for c in sl._element.iter(A + "srgbClr"):
        v = c.get("val").upper()
        anc = [a.tag for a in c.iterancestors()]
        if A + "gradFill" in anc:
            continue
        if v in BLUE:
            c.set("val", BLUE[v]); cnt[v] += 1
        elif v in TEXT and any(t in TXT_TAGS for t in anc) and A + "ln" not in anc:
            c.set("val", TEXT[v]); cnt[v] += 1
print(dict(cnt))
p.save(DST)
