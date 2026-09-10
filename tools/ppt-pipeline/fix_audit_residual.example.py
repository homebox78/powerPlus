# -*- coding: utf-8 -*-
"""audit 02/03 잔여 2건(s12 카드, s16 아이콘) — audit과 같은 실측식으로 보정."""
import os, sys, time, win32com.client as w
sys.stdout.reconfigure(encoding="utf-8")
IN = 72.0
src, dst = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
app = w.Dispatch("PowerPoint.Application"); pp = app.Presentations.Open(src, WithWindow=False)
def sh_of(shs):
    out = []
    for s in shs:
        if s.Type == 6: out += sh_of(s.GroupItems)
        else: out.append(s)
    return out
try:
    # s16: 아이콘 ↔ 우측 텍스트
    shapes = sh_of(pp.Slides(16).Shapes)
    for ic in [s for s in shapes if s.Name == "PPICON"]:
        L, T, W, H = ic.Left, ic.Top, ic.Width, ic.Height
        near = []
        for t in shapes:
            if not t.HasTextFrame or not t.TextFrame.HasText or t.Height > 2*IN or t.Width > 8*IN: continue
            gap = t.Left - (L+W)
            if not (-W*0.25 <= gap <= 0.8*IN): continue
            tr = t.TextFrame.TextRange; bt, bh = tr.BoundTop, tr.BoundHeight
            if bt+bh < T-0.3*IN or bt > T+H+0.3*IN: continue
            if t.Width < 0.5*IN and len(tr.Text.strip()) <= 3: continue
            near.append((bt, bt+bh, tr.Text.strip()[:20]))
        if near:
            d = (min(n[0] for n in near)+max(n[1] for n in near))/2 - (T+H/2)
            if 0.03*IN < abs(d) <= 0.35*IN:
                print(f"s16 icon @({L/IN:.2f},{T/IN:.2f}) d={d/IN:+.2f} near={[n[2] for n in near]}")
                ic.Top = T + d
    # s12: 카드 내 콘텐츠
    shapes = sh_of(pp.Slides(12).Shapes)
    cards = [s for s in shapes if s.Type in (1,5) and 0.6*IN <= s.Height <= 2.0*IN and s.Width >= 1.5*IN and not (s.HasTextFrame and s.TextFrame.HasText)]
    for card in cards:
        def inside(s): cx, cy = s.Left+s.Width/2, s.Top+s.Height/2; return card.Left+2 <= cx <= card.Left+card.Width-2 and card.Top <= cy <= card.Top+card.Height
        mem = [s for s in shapes if s is not card and inside(s) and s.Width < card.Width*0.98 and not (s.Type in (1,5) and s.Width > 0.35*IN and s.Height > 0.35*IN and not (s.HasTextFrame and s.TextFrame.HasText))]
        ics = [s for s in mem if s.Name == "PPICON"]; tts = [s for s in mem if s.HasTextFrame and s.TextFrame.HasText and s.Width > 0.6*IN]
        if not ics or not tts: continue
        tops = [s.TextFrame.TextRange.BoundTop for s in tts]; bots = [s.TextFrame.TextRange.BoundTop+s.TextFrame.TextRange.BoundHeight for s in tts]
        ic_top = min(i.Top for i in ics); ic_bot = max(i.Top+i.Height for i in ics)
        stacked = ic_bot <= min(tops)+4
        top, bot = (min(ic_top, min(tops)), max(bots)) if stacked else (min(tops), max(bots))
        d = (card.Top+card.Height/2) - (top+bot)/2
        if 0.04*IN < abs(d) <= 0.35*IN:
            print(f"s12 card @({card.Left/IN:.2f},{card.Top/IN:.2f}) d={d/IN:+.2f} stacked={stacked} mem={len(mem)}")
            for s in mem: s.Top = s.Top + d
    pp.SaveAs(dst)
finally:
    pp.Close(); time.sleep(0.4)
print("saved", dst)
