# -*- coding: utf-8 -*-
import os, sys, time
import win32com.client as win32
sys.stdout.reconfigure(encoding="utf-8")
src, dst = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2]); IN = 72.0
app = win32.Dispatch("PowerPoint.Application"); pres = app.Presentations.Open(src, WithWindow=False)
def sh_of(c):
    o = []
    for i in range(1, c.Count + 1):
        s = c.Item(i); o += sh_of(s.GroupItems) if s.Type == 6 else [s]
    return o
def isbadge(s):
    if s.Type == 19 or not s.HasTextFrame or not s.TextFrame.HasText: return False   # 표 제외
    t = s.TextFrame.TextRange.Text.strip()
    return len(t) <= 6 and "\r" not in t and 0.35 * IN <= s.Width <= 1.1 * IN and s.Height <= 0.36 * IN
n = 0; hit = {}
try:
    for sno in range(1, pres.Slides.Count + 1):
        shapes = sh_of(pres.Slides(sno).Shapes)
        badges = [s for s in shapes if isbadge(s)]
        texts = [s for s in shapes if s.HasTextFrame and s.TextFrame.HasText and s not in badges and s.Height < 1.0 * IN and s.Width <= 4 * IN]
        for b in badges:
            bc = b.Top + b.Height / 2; R = b.Left + b.Width
            for t in texts:
                gap = t.Left - R
                if not (-0.05 * IN <= gap <= 0.4 * IN): continue
                if t.Top > b.Top + b.Height or t.Top + t.Height < b.Top: continue
                tr = t.TextFrame.TextRange; d = bc - (tr.BoundTop + tr.BoundHeight / 2)
                if 0.5 < abs(d) <= 0.2 * IN:
                    t.Top += d; n += 1; hit[sno] = hit.get(sno, 0) + 1
    print("뱃지 정렬:", n, hit); pres.SaveAs(dst); print("→", os.path.basename(dst))
finally:
    pres.Close(); time.sleep(0.4)
