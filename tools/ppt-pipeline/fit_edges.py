# -*- coding: utf-8 -*-
"""도형 가장자리에 닿거나 넘친 글자를 줄여 안쪽 여유를 확보 (전 장, 실제 렌더 기준).

대상: 글 줄이 채운 도형(자기 자신 또는 바로 아래 바탕) 안에 있는데,
      글 묶음 왼쪽·오른쪽이 바탕 가장자리 여유(높이의 22%, 최소 4pt)보다 바깥에 있는 것.
처리: 0.5pt 씩 줄여 여유 안에 들어오면 멈춤. 원래 크기의 80% 밑으로는 안 줄이고 보고만.
     줄 수가 늘어나면(줄바꿈 생김) 그 단계는 버린다.
인자: <src> <dst> [--dry] [--slides 5,7]
"""
import os, sys, time
import win32com.client as win32
sys.stdout.reconfigure(encoding="utf-8")
args = [a for a in sys.argv[1:] if not a.startswith("--")]
src, dst = os.path.abspath(args[0]), os.path.abspath(args[1])
DRY = "--dry" in sys.argv
ONLY = [int(x) for x in sys.argv[sys.argv.index("--slides") + 1].split(",")] if "--slides" in sys.argv else None

app = win32.Dispatch("PowerPoint.Application")
pres = app.Presentations.Open(src, WithWindow=False)
SW, SH = pres.PageSetup.SlideWidth, pres.PageSetup.SlideHeight


def flat(c):
    o = []
    for i in range(1, c.Count + 1):
        s = c.Item(i)
        if s.Type == 6:
            try:
                o += flat(s.GroupItems)
            except Exception:
                pass
        else:
            o.append(s)
    return o


def filled(s):
    try:
        return s.Type in (1, 17) and ((s.Fill.Visible and s.Fill.Transparency < 0.5) or (s.Line.Visible and s.Line.Weight >= 0.5 and s.Line.Transparency < 0.5)) and s.Width > 8 and s.Height > 8 \
            and not (s.Width > SW * 0.6 and s.Height > SH * 0.3)
    except Exception:
        return False


def base_of(shs, i, t, tr):
    bl, bt, bw, bh = tr.BoundLeft, tr.BoundTop, tr.BoundWidth, tr.BoundHeight
    cx, cy = bl + bw / 2, bt + bh / 2
    best = None
    for j, f in enumerate(shs[: i + 1]):
        if not filled(f):
            continue
        if not (f.Left <= cx <= f.Left + f.Width and f.Top <= cy <= f.Top + f.Height):
            continue
        if f.Height > max(bh * 3.2, 60):
            continue
        if best is None or f.Width * f.Height < best.Width * best.Height:
            best = f
    return best


def sizes(tr):
    out = []
    for k in range(1, tr.Runs().Count + 1):
        out.append(tr.Runs(k).Font.Size)
    return out


fixed, warned = 0, []
try:
    for sno in range(1, pres.Slides.Count + 1):
        if ONLY and sno not in ONLY:
            continue
        shs = flat(pres.Slides(sno).Shapes)
        for i, t in enumerate(shs):
            try:
                if t.Type == 19 or not t.HasTextFrame or not t.TextFrame.HasText:
                    continue
                tr = t.TextFrame.TextRange
                if len(tr.Text.strip()) <= 3 or t.TextFrame.Orientation != 1 or abs(t.Rotation) > 1:
                    # 번호 원·짧은 표시(1·01·CPU)는 형제끼리 크기가 갈라지므로 손대지 않는다
                    continue
                if tr.BoundHeight <= 0 or tr.BoundHeight > 80:
                    continue
                f = base_of(shs, i, t, tr)
            except Exception:
                continue
            if f is None:
                continue
            pad = max(4.0, f.Height * 0.22)
            lo, hi = f.Left + pad, f.Left + f.Width - pad

            def over():
                return max(lo - tr.BoundLeft, tr.BoundLeft + tr.BoundWidth - hi, 0)
            ov = over()
            if ov < 0.5:
                continue
            orig = sizes(tr)
            lines0 = tr.Lines().Count
            name = t.Name
            txt = tr.Text[:20].replace("\r", "/")
            if DRY:
                print(sno, name, "넘침 %.1fpt" % ov, txt)
                fixed += 1
                continue
            step, ok = 0, False
            while True:
                step += 0.5
                new = [max(1, s - step) for s in orig]
                if min(n / o for n, o in zip(new, orig)) < 0.8:
                    break
                for k, n in enumerate(new, 1):
                    tr.Runs(k).Font.Size = n
                if tr.Lines().Count > lines0:
                    continue
                if over() < 0.5:
                    ok = True
                    break
            if ok:
                fixed += 1
                print(sno, name, "-%.1fpt" % step, txt)
            else:
                for k, o in enumerate(orig, 1):
                    tr.Runs(k).Font.Size = o
                warned.append((sno, name, round(ov, 1), txt))
    for w in warned:
        print("못 맞춤", *w)
    if not DRY:
        pres.SaveAs(dst)
    print("고침", fixed, "못 맞춤", len(warned))
finally:
    pres.Close()
    time.sleep(0.3)
