# -*- coding: utf-8 -*-
import os, sys, time
import win32com.client as win32
sys.stdout.reconfigure(encoding="utf-8")
src, dst = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2]); IN = 72.0
VT = chr(11); SP = set(chr(32)+chr(9)+chr(13)+chr(10)+chr(11))
def nobreak(tr):
    for _ in range(6):
        txt = tr.Text; cnt = tr.Lines().Count; done = True
        for i in range(1, cnt):
            a = tr.Lines(i, 1); b = tr.Lines(i + 1, 1)
            e = a.Start + a.Length - 1; s = b.Start
            if e < 1 or s > len(txt): continue
            if txt[e - 1] in SP or txt[s - 1] in SP: continue
            p = e
            while p > 1 and txt[p - 2] not in SP: p -= 1
            if p <= a.Start: continue
            tr.Characters(p, 0).InsertBefore(VT); done = False; break
        if done: break
app = win32.Dispatch("PowerPoint.Application"); pres = app.Presentations.Open(src, WithWindow=False)
try:
    sl = pres.Slides(17); shapes = list(sl.Shapes)
    cards = [s for s in shapes if s.Type in (1, 5) and 1.2 * IN < s.Height < 1.5 * IN and s.Width > 3 * IN]
    n = 0
    for card in cards:
        inside = lambda s: card.Left <= s.Left + s.Width / 2 <= card.Left + card.Width and card.Top <= s.Top + s.Height / 2 <= card.Top + card.Height
        texts = [s for s in shapes if s is not card and s.HasTextFrame and s.TextFrame.HasText and inside(s)]
        icons = [s for s in shapes if s.Name == "PPICON" and inside(s)]
        if len(texts) != 2 or len(icons) != 1: continue
        title, desc = sorted(texts, key=lambda s: s.Top); ic = icons[0]
        desc.Left = title.Left; desc.Width = card.Left + card.Width - title.Left - 0.12 * IN
        tr1, tr2 = title.TextFrame.TextRange, desc.TextFrame.TextRange
        while VT in tr2.Text: tr2.Characters(tr2.Text.index(VT) + 1, 1).Delete()
        nobreak(tr2)
        D = chr(8212)
        if D in tr2.Text:
            # 대시 앞뒤의 VT 를 모두 지우고, 대시 바로 뒤에 넣은 뒤 실제 위치를 검증
            while True:
                t = tr2.Text; pos = t.find(D)
                if pos >= 1 and t[pos - 1] == VT: tr2.Characters(pos, 1).Delete(); continue
                if pos + 1 < len(t) and t[pos + 1] == VT: tr2.Characters(pos + 2, 1).Delete(); continue
                break
            for start in (pos + 2, pos + 1, pos + 3):
                tr2.Characters(start, 0).InsertBefore(VT)
                t = tr2.Text
                if t.find(D) + 1 < len(t) and t[t.find(D) + 1] == VT: break
                i = t.find(VT); tr2.Characters(i + 1, 1).Delete()
            nobreak(tr2)
        desc.Top += (tr1.BoundTop + tr1.BoundHeight + 1) - tr2.BoundTop        # 제목 아래 1pt
        top, bot = tr1.BoundTop, tr2.BoundTop + tr2.BoundHeight
        d = (card.Top + card.Height / 2) - (top + bot) / 2
        title.Top += d; desc.Top += d
        ic.Top = (top + bot) / 2 + d - ic.Height / 2; n += 1
    print("s17 카드", n); pres.SaveAs(dst); print("→", os.path.basename(dst))
finally:
    pres.Close(); time.sleep(0.4)
