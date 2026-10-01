# -*- coding: utf-8 -*-
"""글이 상자에 비해 너무 적어 아래가 휑한 경우: 줄간격(최대 1.5)과 글자(최대 +2pt)를 늘려 상자의 약 88%를 채운다.
상자 = 글 도형 자신(채움/테두리)이 아니면 글 중심을 품는 가장 작은 채운 도형.
인자: <src> <dst> --slide N --match "글 일부" [--match ...]
"""
import os, sys, time
import win32com.client as win32
sys.stdout.reconfigure(encoding="utf-8")
args = [a for a in sys.argv[1:] if not a.startswith("--")]
src, dst = os.path.abspath(args[0]), os.path.abspath(args[1])
SL = int(sys.argv[sys.argv.index("--slide") + 1])
MATCH = [sys.argv[i + 1] for i, a in enumerate(sys.argv) if a == "--match"]
TARGET = 0.88

app = win32.Dispatch("PowerPoint.Application")
pres = app.Presentations.Open(src, WithWindow=False)


def flat(c):
    o = []
    for i in range(1, c.Count + 1):
        s = c.Item(i)
        o += flat(s.GroupItems) if s.Type == 6 else [s]
    return o


try:
    shs = flat(pres.Slides(SL).Shapes)
    for m in MATCH:
        t = next(s for s in shs if s.HasTextFrame and s.TextFrame.HasText and m in s.TextFrame.TextRange.Text)
        tr = t.TextFrame.TextRange
        cx, cy = tr.BoundLeft + tr.BoundWidth / 2, tr.BoundTop + tr.BoundHeight / 2
        box = None
        for f in shs:
            try:
                ok = f.Fill.Visible or f.Line.Visible
            except Exception:
                ok = False
            if ok and f.Left <= cx <= f.Left + f.Width and f.Top <= cy <= f.Top + f.Height and f.Height >= tr.BoundHeight:
                if box is None or f.Width * f.Height < box.Width * box.Height:
                    box = f
        room = (box.Height if box else t.Height) * TARGET
        t.TextFrame.AutoSize = 0
        if t.Height < room / TARGET:
            pass
        sizes = [tr.Runs(k).Font.Size for k in range(1, tr.Runs().Count + 1)]
        tr.ParagraphFormat.LineRuleWithin = True
        sp = tr.ParagraphFormat.SpaceWithin or 1.0
        best = None
        for add in [0, 0.5, 1.0, 1.5, 2.0]:
            for k, s0 in enumerate(sizes, 1):
                tr.Runs(k).Font.Size = s0 + add
            for spw in [x / 100 for x in range(int(sp * 100), 151, 5)]:
                tr.ParagraphFormat.SpaceWithin = spw
                if tr.BoundHeight <= room:
                    best = (add, spw, tr.BoundHeight)
                else:
                    break
        if best:
            for k, s0 in enumerate(sizes, 1):
                tr.Runs(k).Font.Size = s0 + best[0]
            tr.ParagraphFormat.SpaceWithin = best[1]
            # 글 상자가 상자보다 작으면 넓혀서 세로 가운데
            if box is not None and box is not t:
                t.Top = box.Top + (box.Height - t.Height) / 2
            print(m, "글자 +%.1f 줄간격 %.2f 높이 %.0f/%.0f" % (best[0], best[1], best[2], room / TARGET))
    pres.SaveAs(dst)
finally:
    pres.Close()
    time.sleep(0.3)
