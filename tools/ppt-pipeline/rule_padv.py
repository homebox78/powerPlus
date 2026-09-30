"""디자인 시스템 7.5 — 채움·테두리 도형 안 글의 상하 여백 0.04in.
   글 높이 + 여백이 도형 높이를 넘거나 줄 수가 바뀌면 되돌린다. (COM)"""
import sys, os
import win32com.client as win32
sys.stdout.reconfigure(encoding="utf-8")
SRC, DST = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
app = win32.Dispatch("PowerPoint.Application")
pr = app.Presentations.Open(SRC, ReadOnly=False, WithWindow=False)
def walk(shs):
    for i in range(1, shs.Count + 1):
        s = shs.Item(i)
        if s.Type == 6:
            for j in range(1, s.GroupItems.Count + 1):
                yield s.GroupItems.Item(j)
        else:
            yield s
W = 2.88
ok = back = 0
for sl in pr.Slides:
    for s in walk(sl.Shapes):
        try:
            if not s.HasTextFrame or not s.TextFrame.HasText: continue
            if not (s.Fill.Visible or s.Line.Visible): continue
            if s.Fill.Visible and (s.Fill.ForeColor.RGB & 0xFFFFFF) in (0x00FFFF, 0xCCFFFF): continue
            tf = s.TextFrame
            if tf.AutoSize != 0: continue
            t0, b0 = tf.MarginTop, tf.MarginBottom
            if t0 >= W - 0.3 and b0 >= W - 0.3: continue
            tr = tf.TextRange
            n0 = tr.Lines().Count
            if tr.BoundHeight + 2 * W > s.Height: back += 1; continue
            tf.MarginTop = max(t0, W); tf.MarginBottom = max(b0, W)
            if tr.Lines().Count != n0:
                tf.MarginTop, tf.MarginBottom = t0, b0; back += 1
            else: ok += 1
        except Exception:
            pass
print("적용", ok, "건너뜀", back)
pr.SaveAs(DST); pr.Close()
