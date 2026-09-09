# -*- coding: utf-8 -*-
"""PowerPoint COM 으로 슬라이드를 PNG 로 내보낸다. 인자: <pptx> <outdir> [슬라이드번호...]"""
import os, sys, time
import win32com.client as win32

src = os.path.abspath(sys.argv[1])
out = os.path.abspath(sys.argv[2])
picks = [int(x) for x in sys.argv[3:]] if len(sys.argv) > 3 else None
os.makedirs(out, exist_ok=True)

app = win32.Dispatch("PowerPoint.Application")
pres = app.Presentations.Open(src, WithWindow=False)
try:
    n = pres.Slides.Count
    todo = picks or range(1, n + 1)
    for i in todo:
        p = os.path.join(out, f"s{i:02d}.png")
        pres.Slides(i).Export(p, "PNG", 1600, 1108)
        print(f"  s{i:02d}.png")
    print(f"렌더 {len(list(todo))}/{n}")
finally:
    pres.Close()
    time.sleep(0.3)
