"""디자인 시스템 7.5 — 채움·테두리 도형 안 글의 좌우 여백.
   좌측 정렬 0.08in, 그 외 0.04in. 줄 수가 늘거나 글이 넘치면 되돌린다. (COM)"""
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
ok = back = 0
per = {}
for sl in pr.Slides:
    for s in walk(sl.Shapes):
        try:
            if not s.HasTextFrame or not s.TextFrame.HasText: continue
            if not (s.Fill.Visible or s.Line.Visible): continue
            tf = s.TextFrame
            if s.Fill.Visible and (s.Fill.ForeColor.RGB & 0xFFFFFF) in (0x00FFFF, 0xCCFFFF): continue  # 노랑 메모
            if tf.AutoSize != 0: continue
            tr = tf.TextRange
            want = 5.76 if tr.ParagraphFormat.Alignment == 1 else 2.88
            l0, r0 = tf.MarginLeft, tf.MarginRight
            if l0 >= want - 0.3 and r0 >= want - 0.3: continue
            n0 = tr.Lines().Count; h0 = tr.BoundHeight
            tf.MarginLeft = max(l0, want); tf.MarginRight = max(r0, want)
            if tr.Lines().Count > n0 or tr.BoundHeight > h0 + 0.5:
                tf.MarginLeft, tf.MarginRight = l0, r0; back += 1
            else:
                ok += 1; per[sl.SlideIndex] = per.get(sl.SlideIndex, 0) + 1
        except Exception:
            pass
print("적용", ok, "되돌림", back, per)
pr.SaveAs(DST); pr.Close()
