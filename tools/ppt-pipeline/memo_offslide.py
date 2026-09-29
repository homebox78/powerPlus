"""노랑 기획 메모(스마일·노랑 채움 말풍선)를 슬라이드 오른쪽 밖으로 옮긴다 — 슬라이드쇼에서 안 보이게.
   메모는 지우지 않는다(편집 화면 오른쪽 여백에서 그대로 보인다). 세로 위치는 유지.
   같은 그룹에 묶인 메모는 그룹째 옮긴다. 슬라이드 밖에 이미 있는 것은 건너뛴다.
   **열린 문서(COM)** 에 적용 후 SaveCopyAs.  인자: <열린 문서 이름 일부> [apply <저장경로>]"""
import sys
import win32com.client as win32
sys.stdout.reconfigure(encoding="utf-8")
SRC = sys.argv[1]
APPLY = "apply" in sys.argv
OUT = sys.argv[sys.argv.index("apply") + 1] if APPLY else None
YELLOW = {0x00FFFF, 0xCCFFFF, 0x99FFFF, 0x87FFFF, 0x66FFFF, 0x00FFFF}  # BGR
GAP = 0.3 * 72  # 슬라이드 오른쪽 가장자리에서 띄울 거리(pt)
app = win32.GetObject(Class="PowerPoint.Application")
pr = [app.Presentations(i) for i in range(1, app.Presentations.Count + 1) if SRC in app.Presentations(i).Name][0]
W = pr.PageSetup.SlideWidth


def is_memo(s):
    try:
        if s.Type == 1 and s.AutoShapeType == 17:  # 스마일
            return True
        if s.Fill.Visible and s.Fill.Type == 1 and (s.Fill.ForeColor.RGB in YELLOW):
            return True
    except Exception:
        pass
    return False


def memo_in_group(g):
    return any(is_memo(g.GroupItems(i)) for i in range(1, g.GroupItems.Count + 1))


tot = 0
for sn in range(1, pr.Slides.Count + 1):
    sl = pr.Slides(sn)
    targets = []
    for s in sl.Shapes:
        if s.Type == 6:
            items = [s.GroupItems(i) for i in range(1, s.GroupItems.Count + 1)]
            if all(is_memo(x) or not x.HasTextFrame or True for x in items) and memo_in_group(s):
                # 그룹 안에 메모 말고 본문이 섞였으면 그룹째 옮기지 않는다
                others = [x for x in items if not is_memo(x) and x.HasTextFrame and x.TextFrame.HasText
                          and not (x.Fill.Visible and x.Fill.ForeColor.RGB in YELLOW)]
                big = s.Width > W * 0.5
                if not big:
                    targets.append(s)
                else:
                    print(f"  s{sn} 그룹 {s.Name} 은 너무 커서 건너뜀(본문과 묶임?)")
        elif is_memo(s):
            targets.append(s)
    # 스마일 옆에 붙은 노랑 글상자(메모 문구)도 같이
    for s in targets:
        if s.Left >= W:
            continue
        txt = s.TextFrame.TextRange.Text.strip()[:20] if s.HasTextFrame and s.TextFrame.HasText else ""
        print(f"s{sn:02d} {s.Name} L{s.Left/72:.2f} T{s.Top/72:.2f} W{s.Width/72:.2f} '{txt}'")
        tot += 1
    if APPLY:
        # 한 장의 메모들을 서로 겹치지 않게 오른쪽 밖에 위에서부터 쌓는다(세로 순서 유지)
        live = sorted([s for s in targets if s.Left < W], key=lambda s: s.Top)
        y = None
        for s in live:
            top = s.Top if y is None else max(s.Top, y)
            s.Left = W + GAP
            s.Top = top
            y = top + s.Height + 4
print("대상", tot)
if APPLY:
    pr.SaveCopyAs(OUT)
    print("저장:", OUT)
