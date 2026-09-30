# -*- coding: utf-8 -*-
"""서체 바꾸기(키메시지 제외) — 적용 글꼴(COM Font.Name/NameFarEast) 기준이라 글상자 기본값에서 물려받은 글자도 잡힌다.
   키메시지 = 위 띠(Top 0.8~1.45in)·20pt 이상 글자가 있는 글상자(표 제외). 표 칸·그룹 안도 처리.
   인자: <src> <dst> <옛 글꼴> <새 글꼴>   예: "G마켓 산스 TTF Bold" a시월구일4"""
import os, sys
import win32com.client as win32
sys.stdout.reconfigure(encoding="utf-8")
src, dst, OLD, NEW = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2]), sys.argv[3], sys.argv[4]
app = win32.Dispatch("PowerPoint.Application")
pr = app.Presentations.Open(src, ReadOnly=False, WithWindow=False)


def flat(c):
    o = []
    for i in range(1, c.Count + 1):
        s = c.Item(i)
        o += flat(s.GroupItems) if s.Type == 6 else [s]
    return o


def frames(s):
    if s.HasTable:
        t = s.Table
        for r in range(1, t.Rows.Count + 1):
            for c in range(1, t.Columns.Count + 1):
                yield t.Cell(r, c).Shape.TextFrame
    elif s.HasTextFrame:
        yield s.TextFrame


n, kept = 0, 0
for sn in range(1, pr.Slides.Count + 1):
    for s in flat(pr.Slides(sn).Shapes):
        try:
            fl = list(frames(s))
        except Exception:
            continue
        for tf in fl:
            if not tf.HasText:
                continue
            runs = [tf.TextRange.Runs(i) for i in range(1, tf.TextRange.Runs().Count + 1)]
            key = (not s.HasTable) and 0.8 <= s.Top / 72 <= 1.45 and any(r.Font.Size >= 20 and r.Text.strip() for r in runs)
            for r in runs:
                if OLD in (r.Font.Name, r.Font.NameFarEast):
                    if key:
                        kept += 1; continue
                    r.Font.Name = NEW; r.Font.NameFarEast = NEW; n += 1
pr.SaveCopyAs(dst); pr.Close()
print("바꾼 런", n, "키메시지로 유지", kept)
