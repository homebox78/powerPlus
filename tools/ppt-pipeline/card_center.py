# -*- coding: utf-8 -*-
"""카드(빈 도형) 안에 아이콘+텍스트만 있으면 그 블록을 카드 세로 중심으로."""
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
def inside(s, card):
    cx, cy = s.Left + s.Width / 2, s.Top + s.Height / 2
    return card.Left <= cx <= card.Left + card.Width and card.Top <= cy <= card.Top + card.Height
hit = {}
try:
    for sno in range(1, pres.Slides.Count + 1):
        shapes = sh_of(pres.Slides(sno).Shapes)
        cards = [s for s in shapes if s.Type in (1, 5) and 0.6 * IN <= s.Height <= 2.0 * IN and s.Width >= 1.5 * IN
                 and not (s.HasTextFrame and s.TextFrame.HasText)]
        for card in cards:
            members = [s for s in shapes if s is not card and inside(s, card) and s.Width < card.Width * 0.98
                       and not (s.Type in (1, 5) and s.Width > 0.3 * IN and s.Height > 0.3 * IN and not (s.HasTextFrame and s.TextFrame.HasText))]
            icons = [s for s in members if s.Name == "PPICON"]
            texts = [s for s in members if s.HasTextFrame and s.TextFrame.HasText]
            if not icons or not texts or len(members) > 5: continue
            tops, bots = [], []
            for s in texts:
                tr = s.TextFrame.TextRange; tops.append(tr.BoundTop); bots.append(tr.BoundTop + tr.BoundHeight)
            d = (card.Top + card.Height / 2) - (min(tops) + max(bots)) / 2
            if 0.5 < abs(d) <= 0.25 * IN:
                for s in members: s.Top += d
                hit[sno] = hit.get(sno, 0) + 1
    print("카드 중심 정렬:", sum(hit.values()), hit); pres.SaveAs(dst); print("→", os.path.basename(dst))
finally:
    pres.Close(); time.sleep(0.4)
