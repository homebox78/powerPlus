# -*- coding: utf-8 -*-
"""카드 안 콘텐츠 세로 중심(2판): 텍스트 실측 블록을 카드 중심에, 아이콘도 그 블록 중심에. 번호 뱃지(≤0.35in 원)는 제외."""
import os, sys, time
import win32com.client as win32
sys.stdout.reconfigure(encoding="utf-8")
src, dst = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2]); IN = 72.0
only = [int(x) for x in sys.argv[3:]]
app = win32.Dispatch("PowerPoint.Application"); pres = app.Presentations.Open(src, WithWindow=False)
def sh_of(c):
    o = []
    for i in range(1, c.Count + 1):
        s = c.Item(i); o += sh_of(s.GroupItems) if s.Type == 6 else [s]
    return o
def inside(s, card):
    cx, cy = s.Left + s.Width / 2, s.Top + s.Height / 2
    return card.Left + 2 <= cx <= card.Left + card.Width - 2 and card.Top <= cy <= card.Top + card.Height
hit = {}
try:
    for sno in (only or range(1, pres.Slides.Count + 1)):
        shapes = sh_of(pres.Slides(sno).Shapes)
        cards = [s for s in shapes if s.Type in (1, 5) and 0.6 * IN <= s.Height <= 2.0 * IN and s.Width >= 1.5 * IN
                 and not (s.HasTextFrame and s.TextFrame.HasText)]
        for card in cards:
            mem = [s for s in shapes if s is not card and inside(s, card) and s.Width < card.Width * 0.98
                   and not (s.Type in (1, 5) and s.Width > 0.35 * IN and s.Height > 0.35 * IN and not (s.HasTextFrame and s.TextFrame.HasText))]
            badge = [s for s in mem if s.Width <= 0.35 * IN and s.Height <= 0.35 * IN and s.Name != "PPICON"]
            icons = [s for s in mem if s.Name == "PPICON"]
            texts = [s for s in mem if s.HasTextFrame and s.TextFrame.HasText and s not in badge and s.Width > 0.6 * IN]
            if not icons or not texts: continue
            tops, bots = [], []
            for s in texts:
                tr = s.TextFrame.TextRange; tops.append(tr.BoundTop); bots.append(tr.BoundTop + tr.BoundHeight)
            ic_bot = max(i.Top + i.Height for i in icons); ic_top = min(i.Top for i in icons)
            stacked = ic_bot <= min(tops) + 4          # 아이콘이 글자 위에 있는 세로 스택 셀
            if stacked:
                top, bot = min(ic_top, min(tops)), max(bots)
                d = (card.Top + card.Height / 2) - (top + bot) / 2
                if abs(d) > 0.35 * IN: continue
                for s in texts + icons: s.Top += d
            else:
                bc = (min(tops) + max(bots)) / 2; d = (card.Top + card.Height / 2) - bc
                if abs(d) > 0.35 * IN: continue
                for s in texts: s.Top += d
                for ic in icons: ic.Top = (bc + d) - ic.Height / 2
            if abs(d) > 0.5: hit[sno] = hit.get(sno, 0) + 1
    print("카드 중심(2판):", sum(hit.values()), hit); pres.SaveAs(dst); print("→", os.path.basename(dst))
finally:
    pres.Close(); time.sleep(0.4)
