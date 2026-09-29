# -*- coding: utf-8 -*-
"""고아 줄(마지막 줄 1~2글자) → 윗줄 마지막 어절 앞에 줄바꿈(chr 11)을 넣어 함께 내린다.
   글자 크기·여백을 건드리지 않아 형제 도형과 톤이 갈리지 않는다.
   윗줄이 한 어절뿐이면(의도된 2줄 라벨) 두고, 넣은 뒤 줄 수가 늘거나 새 고아가 생기면 되돌린다.
   기획 메모(노랑)는 제외. 인자: <src> <dst>"""
import os, sys
import win32com.client as win32
sys.stdout.reconfigure(encoding="utf-8")
src, dst = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
MEMO_BGR = {0x00FFFF, 0xCCFFFF, 0x99FFFF, 0x87FFFF}
VT = chr(11)
app = win32.Dispatch("PowerPoint.Application")
pres = app.Presentations.Open(src, WithWindow=False)


def shapes(c):
    o = []
    for i in range(1, c.Count + 1):
        s = c.Item(i)
        o += shapes(s.GroupItems) if s.Type == 6 else [s]
    return o


def L(p):
    return [p.Lines(k, 1).Text for k in range(1, p.Lines().Count + 1)]


def orphan(lines):
    return len(lines) >= 2 and 0 < len(lines[-1].strip(" \r\x0b")) <= 2


done, kept = [], []
for sno in range(1, pres.Slides.Count + 1):
    for s in shapes(pres.Slides(sno).Shapes):
        try:
            if not s.HasTextFrame or not s.TextFrame.HasText or not s.TextFrame.WordWrap:
                continue
            if s.Fill.Visible and s.Fill.Type == 1 and s.Fill.ForeColor.RGB in MEMO_BGR:
                continue
        except Exception:
            continue
        tr = s.TextFrame.TextRange
        for i in range(1, tr.Paragraphs().Count + 1):
            p = tr.Paragraphs(i)
            lines = L(p)
            if not orphan(lines):
                continue
            prev = lines[-2].rstrip(" \x0b")
            if " " not in prev.strip():
                kept.append((sno, s.Name, " / ".join(x.strip() for x in lines), "윗줄 한 어절")); continue
            # 윗줄의 마지막 공백 위치(문단 기준)
            start = sum(len(x) for x in lines[:-2])
            cut = start + prev.rfind(" ")          # 0-base, 공백 자리
            ch = p.Characters(cut + 1, 1)
            before = lines
            ch.Text = VT
            after = L(tr.Paragraphs(i))
            if len(after) > len(before) or orphan(after):
                tr.Paragraphs(i).Characters(cut + 1, 1).Text = " "
                kept.append((sno, s.Name, " / ".join(x.strip() for x in before), "균형 실패"))
            else:
                done.append((sno, s.Name, " / ".join(x.strip(" \r\x0b") for x in after)))
pres.SaveAs(dst)
try:
    pres.Close()
except Exception:
    pass
print("고아 줄 균형", len(done), "· 남김", len(kept))
for x in done:
    print("  ", x)
for x in kept:
    print("  남김", x)
