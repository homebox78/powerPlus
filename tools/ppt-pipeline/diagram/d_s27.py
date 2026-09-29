# -*- coding: utf-8 -*-
"""s27 주요 성능개선 대상 — CPU/Mem/I-O 순환 도식 (원본 346x232px)"""
from pptx.enum.shapes import MSO_SHAPE
from diag import Diagram, find_pic

E = "a시월구일3"


def build(prs):
    s = prs.slides[26]
    d = Diagram(s, find_pic(s, 127), 346, 232)
    d.box(83, 30, 180, 180, "", fill=None, line="mist", shape=MSO_SHAPE.OVAL, lw=3)
    d.box(128, 80, 88, 88, "", fill="azure", shape=MSO_SHAPE.OVAL)
    d.label(118, 80, 108, 88, "성능", size=10, color="white", face=E)
    for cx, cy, t, f in [(173, 32, "CPU", "indigo"), (251, 170, "Mem", "blue"), (95, 170, "I/O", "teal")]:
        d.box(cx - 30, cy - 30, 60, 60, "", fill=f, shape=MSO_SHAPE.OVAL, line="white", lw=1.5)
        d.label(cx - 40, cy - 30, 80, 60, t, size=7, color="white", face=E)
    d.finish()
