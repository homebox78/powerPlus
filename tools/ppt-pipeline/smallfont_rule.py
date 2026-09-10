# -*- coding: utf-8 -*-
"""작은 글(≤10pt) 서체 규칙: 본문=a시월구일2, 강조(볼드 계열 서체) 런=a시월구일3."""
import os, re, sys, time
import win32com.client as win32
sys.stdout.reconfigure(encoding="utf-8")
src, dst = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
REG, BLD, MAX = "a시월구일2", "a시월구일3", 10.0
app = win32.Dispatch("PowerPoint.Application"); pres = app.Presentations.Open(src, WithWindow=False)
def sh_of(c):
    o = []
    for i in range(1, c.Count + 1):
        s = c.Item(i); o += sh_of(s.GroupItems) if s.Type == 6 else [s]
    return o
cnt = {"reg": 0, "bld": 0}
def fix(tr):
    for i in range(1, tr.Runs().Count + 1):
        r = tr.Runs(i); f = r.Font
        if f.Size > MAX or not re.search(r"[가-힣A-Za-z0-9]", r.Text): continue
        name = (f.Name or "") + "|" + (f.NameFarEast or "")
        bold = f.Bold == -1 or "Bold" in name or BLD in name
        want = BLD if bold else REG
        if f.Name != want or f.NameFarEast != want:
            f.Name = want; f.NameFarEast = want; cnt["bld" if bold else "reg"] += 1
        if bold: f.Bold = 0
try:
    for sno in range(1, pres.Slides.Count + 1):
        for s in sh_of(pres.Slides(sno).Shapes):
            if s.HasTable == -1:
                t = s.Table
                for r in range(1, t.Rows.Count + 1):
                    for c in range(1, t.Columns.Count + 1): fix(t.Cell(r, c).Shape.TextFrame.TextRange)
            elif s.HasTextFrame and s.TextFrame.HasText: fix(s.TextFrame.TextRange)
    print(cnt); pres.SaveAs(dst); print("→", os.path.basename(dst))
finally:
    pres.Close(); time.sleep(0.4)
