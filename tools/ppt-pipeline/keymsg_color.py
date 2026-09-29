"""전 장 키메시지 색 통일 — 기준 장(청주: 34p)의 색으로. 강조 F71148, 나머지 테마 글자색2(ObjectThemeColor 15 = 222A35).
   대상: 상단 띠(Top 0.8~1.45in) 글상자 중 20pt 이상 글자에 빨간 계열 강조가 있는 것.
   **열린 문서(COM)** 에 적용 후 SaveCopyAs — 사용자의 저장 안 된 수정을 살린다.
   인자: <열린 문서 이름 일부> [apply <저장경로>]  (apply 없으면 대상 목록만)"""
import sys
import win32com.client as win32
sys.stdout.reconfigure(encoding="utf-8")
SRC = sys.argv[1]
APPLY = "apply" in sys.argv
OUT = sys.argv[sys.argv.index("apply") + 1] if APPLY else None
RED = 0x4811F7  # BGR of F71148
app = win32.GetObject(Class="PowerPoint.Application")
pr = [app.Presentations(i) for i in range(1, app.Presentations.Count + 1) if SRC in app.Presentations(i).Name][0]


def rgb(c):
    v = c.RGB
    return v & 255, (v >> 8) & 255, (v >> 16) & 255


def is_red(ru):
    r, g, b = rgb(ru.Font.Color)
    return r > 200 and g < 140 and b < 150


tot = 0
for sn in range(1, pr.Slides.Count + 1):
    for s in pr.Slides(sn).Shapes:
        if not s.HasTextFrame or not (0.8 <= s.Top / 72 <= 1.45):
            continue
        tr = s.TextFrame.TextRange
        runs = [tr.Runs(i) for i in range(1, tr.Runs().Count + 1)]
        big = [ru for ru in runs if ru.Font.Size >= 20 and ru.Text.strip()]
        if not big or not any(is_red(ru) for ru in big):
            continue
        red = [ru.Text for ru in runs if is_red(ru)]
        print(f"s{sn:02d} {s.Name}: {tr.Text.strip()[:50]}  | 강조={''.join(red).strip()}")
        tot += 1
        if APPLY:
            for ru in runs:
                if is_red(ru):
                    ru.Font.Color.RGB = RED
                else:
                    ru.Font.Color.ObjectThemeColor = 15  # 테마 글자색2
print("대상", tot)
if APPLY:
    pr.SaveCopyAs(OUT)
    print("저장:", OUT)
