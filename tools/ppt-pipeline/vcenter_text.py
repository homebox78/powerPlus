# -*- coding: utf-8 -*-
"""도형 안 글자 세로 가운데 맞춤 (전 장, 화면 실측).

1) COM 으로 글자가 든 도형마다 '보이는 바탕 띠'를 찾는다.
   바탕 = 글 줄 가운데를 품는 채운 도형(자기 자신 포함). 그 위(z 위)에 겹친 채운 도형이
   띠를 가리면(카드 머리 아래 흰 판 등) 가려진 곳까지만 띠로 본다. 띠 높이는 한두 줄 글 크기여야 한다.
2) 장을 PNG 로 내보내 띠 안 글자 잉크의 위·아래 끝을 잰다(띠 바탕색과 다른 화소).
3) 잉크 가운데를 띠 가운데로: 글 상자가 따로면 상자를 옮기고, 자기 자신이 바탕이면 위·아래 안쪽 여백을 조정.
인자: <src> <dst> [--dry] [--slides 4,7] [--work 폴더]
"""
import os, sys, time
from collections import Counter
from PIL import Image
import win32com.client as win32
sys.stdout.reconfigure(encoding="utf-8")
args = [a for a in sys.argv[1:] if not a.startswith("--")]
src, dst = os.path.abspath(args[0]), os.path.abspath(args[1])
opt = lambda k, d=None: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d
DRY = "--dry" in sys.argv
ONLY = [int(x) for x in opt("--slides").split(",")] if opt("--slides") else None
WORK = os.path.abspath(opt("--work", os.path.join(os.environ.get("TEMP", "."), "vcenter")))
os.makedirs(WORK, exist_ok=True)
IN = 72.0
PXW = 3200

app = win32.Dispatch("PowerPoint.Application")
pres = app.Presentations.Open(src, WithWindow=False)
SW, SH = pres.PageSetup.SlideWidth, pres.PageSetup.SlideHeight
K = PXW / SW


def flat(c):
    o = []
    for i in range(1, c.Count + 1):
        s = c.Item(i)
        o += flat(s.GroupItems) if s.Type == 6 else [s]
    return o


def filled(s):
    try:
        return s.Type in (1, 17) and ((s.Fill.Visible and s.Fill.Transparency < 0.5) or (s.Line.Visible and s.Line.Weight >= 0.5 and s.Line.Transparency < 0.5)) and s.Width > 4 and s.Height > 4 \
            and not (s.Width > SW * 0.9 and s.Height > SH * 0.4)
    except Exception:
        return False


def band_of(shs, idx, t, bl, bw, bt, bh):
    tc = bt + bh / 2
    best = None
    for j, f in enumerate(shs):
        if not filled(f) or j > idx:
            continue
        if not (f.Left - 1 <= bl + 1 and bl + bw - 1 <= f.Left + f.Width + 1 and f.Top <= tc <= f.Top + f.Height):
            continue
        top, bot = f.Top, f.Top + f.Height
        for g in shs[j + 1:]:
            if g is t or not filled(g):
                continue
            if g.Left > bl + bw or g.Left + g.Width < bl:
                continue
            if g.Left > bl + 2 or g.Left + g.Width < bl + bw - 2:   # 글 폭을 다 덮는 판만
                continue
            if tc < g.Top < bot:
                bot = g.Top
            if top < g.Top + g.Height < tc:
                top = g.Top + g.Height
        h = bot - top
        if h < bh - 2 or h > max(bh * 2.4, 0.5 * IN):
            continue
        if best is None or h < best[1] - best[0]:
            best = (top, bot, f)
    return best


cands = []
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
                if not tr.Text.strip() or abs(t.Rotation) > 1 and abs(t.Rotation - 360) > 1 or t.TextFrame.Orientation != 1:
                    continue
                bt, bh, bl, bw = tr.BoundTop, tr.BoundHeight, tr.BoundLeft, tr.BoundWidth
            except Exception:
                continue
            if bh <= 0 or bh > 0.9 * IN:
                continue
            b = band_of(shs, i, t, bl, bw, bt, bh)
            if b:
                cands.append(dict(sno=sno, name=t.Name, idx=i, top=b[0], bot=b[1], bl=bl, bw=bw,
                                  self=b[2] is t, text=tr.Text[:18].replace("\r", "/")))
    slides = sorted(set(c["sno"] for c in cands))
    for sno in slides:
        pres.Slides(sno).Export(os.path.join(WORK, "v%02d.png" % sno), "PNG", PXW, int(PXW * SH / SW))
    # 잉크 실측
    fixes = []
    for c in cands:
        im = Image.open(os.path.join(WORK, "v%02d.png" % c["sno"])).convert("RGB")
        y0, y1 = int(c["top"] * K) + 2, int(c["bot"] * K) - 2
        x0, x1 = int(c["bl"] * K), int((c["bl"] + c["bw"]) * K)
        if y1 - y0 < 6 or x1 - x0 < 4:
            continue
        reg = im.crop((x0, y0, x1, y1))
        bgc = Counter(reg.getdata()).most_common(1)[0][0]
        px = reg.load(); W, H = reg.size
        far = lambda p: sum(abs(a - b) for a, b in zip(p, bgc)) > 120
        rows = [y for y in range(H) if sum(1 for x in range(W) if far(px[x, y])) >= 2]
        if not rows:
            continue
        ink = ((rows[0] + rows[-1]) / 2 + y0) / K
        d = (c["top"] + c["bot"]) / 2 - ink
        c["d"] = round(d, 2)
        if abs(d) >= 0.6 and abs(d) <= 0.2 * IN:
            fixes.append(c)
    for c in cands:
        if "d" in c and abs(c["d"]) >= 0.6:
            print(c["sno"], c["name"], c["d"], "자기" if c["self"] else "상자", c["text"], "" if c in fixes else "(건너뜀)")
    if not DRY:
        for c in fixes:
            shs = flat(pres.Slides(c["sno"]).Shapes)
            t = shs[c["idx"]]
            d = c["d"]
            if not c["self"]:
                t.Top = t.Top + d
                continue
            tf = t.TextFrame
            tf.AutoSize = 0
            a = tf.VerticalAnchor
            if a == 1:          # 위
                tf.MarginTop = max(0, tf.MarginTop + d)
            elif a == 4:        # 아래
                tf.MarginBottom = max(0, tf.MarginBottom - d)
            else:               # 가운데: 위 여백 +d, 아래 -d
                mt, mb = tf.MarginTop + d, tf.MarginBottom - d
                if mt < 0: mb -= mt; mt = 0
                if mb < 0: mt -= mb; mb = 0
                tf.MarginTop, tf.MarginBottom = mt, mb
        pres.SaveAs(dst)
    print("후보", len(cands), "고침" if not DRY else "고칠 것", len(fixes))
finally:
    pres.Close()
    time.sleep(0.3)
