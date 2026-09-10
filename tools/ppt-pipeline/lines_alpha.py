# -*- coding: utf-8 -*-
import os, sys, time
import win32com.client as win32
sys.stdout.reconfigure(encoding="utf-8")
src, dst = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
app = win32.Dispatch("PowerPoint.Application"); pres = app.Presentations.Open(src, WithWindow=False)
def sh_of(c):
    o = []
    for i in range(1, c.Count + 1):
        s = c.Item(i); o += sh_of(s.GroupItems) if s.Type == 6 else [s]
    return o
n13 = na = 0
try:
    for sno in range(1, pres.Slides.Count + 1):
        for s in sh_of(pres.Slides(sno).Shapes):
            if s.Type == 19: continue
            try:
                ln = s.Line
                if ln.Visible != -1 or ln.DashStyle != 1: continue
                if abs(ln.Weight - 1.3) < 0.1 or abs(ln.Weight - 1.25) < 0.06: ln.Weight = 1.0; n13 += 1
                ln.Transparency = 0.3; na += 1
            except Exception: pass
    print(f"1.3→1pt {n13}개, 실선 투명도 30% {na}개")
    pres.SaveAs(dst); print("→", os.path.basename(dst))
finally:
    pres.Close(); time.sleep(0.4)
