# -*- coding: utf-8 -*-
import os, sys, time
import win32com.client as win32
sys.stdout.reconfigure(encoding="utf-8")
src, dst = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2]); FONT = "a시월구일3"
app = win32.Dispatch("PowerPoint.Application"); pres = app.Presentations.Open(src, WithWindow=False)
def sh_of(c):
    o = []
    for i in range(1, c.Count + 1):
        s = c.Item(i); o += sh_of(s.GroupItems) if s.Type == 6 else [s]
    return o
n = 0
def fix(tr):
    global n
    for i in range(1, tr.Runs().Count + 1):
        r = tr.Runs(i); f = r.Font
        if f.Bold == -1:
            f.Bold = 0; f.Name = FONT; f.NameFarEast = FONT; n += 1
try:
    for sno in range(1, pres.Slides.Count + 1):
        for s in sh_of(pres.Slides(sno).Shapes):
            if s.HasTable == -1:
                t = s.Table
                for r in range(1, t.Rows.Count + 1):
                    for c in range(1, t.Columns.Count + 1):
                        fix(t.Cell(r, c).Shape.TextFrame.TextRange)
            elif s.HasTextFrame and s.TextFrame.HasText:
                fix(s.TextFrame.TextRange)
    print("볼드 해제+서체 교체 런:", n)
    pres.SaveAs(dst); print("→", os.path.basename(dst))
finally:
    pres.Close(); time.sleep(0.4)
