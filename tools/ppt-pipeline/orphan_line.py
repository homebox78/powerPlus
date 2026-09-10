# -*- coding: utf-8 -*-
"""마지막 줄에 1~2글자만 남는 문단 → 폰트 0.25pt 씩(최대 1.5pt) 줄여 고아 줄 제거."""
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
def orphan(p):
    n = p.Lines().Count
    if n < 2: return False
    return len(p.Lines(n, 1).Text.strip()) <= 2
hits = []
def fix(tr, sno):
    for i in range(1, tr.Paragraphs().Count + 1):
        p = tr.Paragraphs(i)
        if not orphan(p): continue
        size0 = p.Font.Size; size = size0; ok = False
        while size > size0 - 1.5:
            size = round(size - 0.25, 2); p.Font.Size = size
            if not orphan(p): ok = True; break
        if not ok: p.Font.Size = size0
        hits.append((sno, p.Text.replace("\r", " ")[:24], size0, size if ok else None))
try:
    for sno in range(1, pres.Slides.Count + 1):
        for s in sh_of(pres.Slides(sno).Shapes):
            if s.HasTable == -1:
                t = s.Table
                for r in range(1, t.Rows.Count + 1):
                    for c in range(1, t.Columns.Count + 1): fix(t.Cell(r, c).Shape.TextFrame.TextRange, sno)
            elif s.HasTextFrame and s.TextFrame.HasText: fix(s.TextFrame.TextRange, sno)
    done = [h for h in hits if h[3]]
    print(f"고아 줄 {len(hits)}곳 중 {len(done)}곳 해결")
    for h in hits: print("  ", h)
    pres.SaveAs(dst); print("→", os.path.basename(dst))
finally:
    pres.Close(); time.sleep(0.4)
