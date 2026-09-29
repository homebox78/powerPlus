# -*- coding: utf-8 -*-
"""8-2 여백 — 채움·테두리가 있는 도형 안의 '좌측 정렬' 글이 가장자리에 붙어 있으면
   좌우 여백을 기준값(0.08in)으로 맞춘다. 줄 수가 늘거나 넘치면 되돌린다(그 도형은 보고).
   가운데 정렬 글·글상자·표·기획 메모·'디자인' 말풍선은 건드리지 않는다.
   인자: <src> <dst> [기준in=0.08]"""
import os, sys
import win32com.client as win32
sys.stdout.reconfigure(encoding="utf-8")
src, dst = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
M = (float(sys.argv[3]) if len(sys.argv) > 3 else 0.08) * 72
MEMO_BGR = {0x00FFFF, 0xCCFFFF, 0x99FFFF, 0x87FFFF}
app = win32.Dispatch("PowerPoint.Application")
pres = app.Presentations.Open(src, WithWindow=False)

def shapes(c):
    o = []
    for i in range(1, c.Count + 1):
        s = c.Item(i)
        try:
            o += shapes(s.GroupItems) if s.Type == 6 else [s]
        except Exception:
            o.append(s)
    return o

def boxed(s):
    try:
        f = s.Fill.Visible and s.Fill.Transparency < 0.9
    except Exception:
        f = False
    try:
        l = s.Line.Visible
    except Exception:
        l = False
    return f or l

def memo(s):
    try:
        if s.Fill.Visible and s.Fill.Type == 1 and s.Fill.ForeColor.RGB in MEMO_BGR:
            return True
        return "말풍선" in s.Name and "디자인" in s.TextFrame.TextRange.Text
    except Exception:
        return False

def state(tf):
    tr = tf.TextRange
    lines = [tr.Paragraphs(i).Lines().Count for i in range(1, tr.Paragraphs().Count + 1)]
    return lines, tr.BoundHeight + tf.MarginTop + tf.MarginBottom

done, kept = [], []
for sno in range(1, pres.Slides.Count + 1):
    for s in shapes(pres.Slides(sno).Shapes):
        try:
            if s.Type != 1 or not s.HasTextFrame or not s.TextFrame.HasText or memo(s) or not boxed(s):
                continue
            tf = s.TextFrame
            if tf.MarginLeft >= M * 0.6 or tf.WordWrap == 0:
                continue
            tr = tf.TextRange
            n = tr.Paragraphs().Count
            left = sum(1 for i in range(1, n + 1) if tr.Paragraphs(i).ParagraphFormat.Alignment == 1
                       and tr.Paragraphs(i).Text.strip())
            if left == 0 or left < n / 2:
                continue
            if s.Width < M * 6:
                continue
            ml, mr = tf.MarginLeft, tf.MarginRight
            l0, h0 = state(tf)
            tf.MarginLeft = tf.MarginRight = M
            l1, h1 = state(tf)
            if l1 != l0 or (h1 > s.Height + 0.5 and h1 > h0 + 0.5):
                tf.MarginLeft, tf.MarginRight = ml, mr
                kept.append((sno, s.Name, tr.Text.strip()[:24]))
            else:
                done.append((sno, s.Name))
        except Exception:
            continue
pres.SaveAs(dst); pres.Close()
print("여백 맞춤", len(done), "· 줄 수가 늘어 보류", len(kept))
for x in kept:
    print("  보류", x)
