# -*- coding: utf-8 -*-
"""오른쪽 화살표 도형(AutoShapeType 33) 전부: 좌=현재 색 100% → 우=#6890CD 알파 15% 가로 그라데이션."""
import os, sys, time
import win32com.client as win32
sys.stdout.reconfigure(encoding="utf-8")
src, dst = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
RIGHT = 0xCD9068   # BGR of #6890CD
app = win32.Dispatch("PowerPoint.Application"); pres = app.Presentations.Open(src, WithWindow=False)
def sh_of(c):
    o = []
    for i in range(1, c.Count + 1):
        s = c.Item(i); o += sh_of(s.GroupItems) if s.Type == 6 else [s]
    return o
hit = {}
try:
    for sno in range(1, pres.Slides.Count + 1):
        for s in sh_of(pres.Slides(sno).Shapes):
            try: ast = s.AutoShapeType
            except Exception: continue
            if ast != 33: continue
            f = s.Fill
            try: base = f.ForeColor.RGB
            except Exception: base = 0xF08A3B
            f.TwoColorGradient(1, 1)                 # msoGradientHorizontal
            gs = f.GradientStops
            while gs.Count > 2: gs.Delete(gs.Count)
            gs(1).Color.RGB = base; gs(1).Position = 0; gs(1).Transparency = 0
            gs(2).Color.RGB = RIGHT; gs(2).Position = 1; gs(2).Transparency = 0.85
            s.Line.Visible = 0
            hit[sno] = hit.get(sno, 0) + 1
    print("화살표 그라데이션:", sum(hit.values()), hit); pres.SaveAs(dst); print("→", os.path.basename(dst))
finally:
    pres.Close(); time.sleep(0.4)
