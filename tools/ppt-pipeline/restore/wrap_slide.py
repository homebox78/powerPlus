# -*- coding: utf-8 -*-
"""지정 쪽만 어절 중간 줄바꿈을 푼다(글자 크기는 그대로, 잘린 어절 앞 공백을 chr(11)로).
   PowerPoint 실제 렌더 줄(TextRange.Lines) 기준. 제자리 저장.  인자: <pptx> <쪽번호...>"""
import os, sys, re, time
import win32com.client as win32
sys.stdout.reconfigure(encoding="utf-8")
path = os.path.abspath(sys.argv[1]); nos = [int(x) for x in sys.argv[2:]]
SP = "  \t\r\n\v\u000b"
PUNCT = ",.)·%]’”"
WORD = re.compile(r"[0-9A-Za-z가-힣()]")


def shapes(c):
    o = []
    for i in range(1, c.Count + 1):
        s = c.Item(i)
        try:
            o += shapes(s.GroupItems) if s.Type == 6 else [s]
        except Exception:
            o.append(s)
    return o


def bad_lines(p):
    n = p.Lines().Count; bad = []
    for i in range(1, n):
        a, b = p.Lines(i, 1).Text, p.Lines(i + 1, 1).Text
        if a and b and a[-1] not in SP and b[0] not in SP and WORD.match(a[-1]) and (WORD.match(b[0]) or b[0] in PUNCT):
            bad.append(i)
    return bad


for attempt in range(6):
    try:
        app = win32.Dispatch("PowerPoint.Application")
        pres = app.Presentations.Open(path, WithWindow=False)
        break
    except Exception as e:
        print("재시도", e); time.sleep(5)
fixed, left = 0, []
for no in nos:
    for s in shapes(pres.Slides(no).Shapes):
        try:
            if s.HasTable or not s.HasTextFrame or not s.TextFrame.HasText or s.TextFrame.WordWrap == 0:
                continue
        except Exception:
            continue
        tr = s.TextFrame.TextRange
        for pi in range(1, tr.Paragraphs().Count + 1):
            for _ in range(6):
                p = tr.Paragraphs(pi)
                bad = bad_lines(p)
                if not bad:
                    break
                ln = p.Lines(bad[0], 1); t = ln.Text
                cut = max(t.rfind(" "), t.rfind(" "))
                if cut < 0:
                    left.append((no, s.Name, p.Text[:30])); break
                tr.Characters(ln.Start + cut, 1).Text = chr(11); fixed += 1
            # 고아 줄(마지막 줄 3글자 이하): 윗줄 마지막 어절을 함께 내린다
            p = tr.Paragraphs(pi); n = p.Lines().Count
            if n >= 2 and len(p.Lines(n, 1).Text.strip()) <= 3 and len(p.Text.strip()) > 8:
                ln = p.Lines(n - 1, 1); t = ln.Text.rstrip(SP)
                cut = max(t.rfind(" "), t.rfind(" "))
                if cut > 0:
                    tr.Characters(ln.Start + cut, 1).Text = chr(11); fixed += 1
pres.Save(); pres.Close()
print("어절 앞 줄바꿈", fixed, "· 남김", left)
