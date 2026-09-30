"""청주시 4쪽 — 시안(design_ppt 1번) 구성으로 재조립.

생성 그림(노트북·인물·건물 5·도시 풍경)을 원본 크기로 넣고, 글·도형은 PowerPoint 도형으로 그린다.
문구는 기존 장표 그대로.  사용: py design_s04.py <src.pptx> <dst.pptx> <그림 폴더>
"""
import sys, os
from PIL import Image, ImageDraw
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.dml import MSO_LINE

src, dst, art = sys.argv[1:4]
NAVY, BLUE, PINK = RGBColor(0x14, 0x3A, 0x69), RGBColor(0x2F, 0x78, 0xE0), RGBColor(0xEC, 0x1C, 0x68)
SOFT, PALE, WHITE = RGBColor(0xD0, 0xE6, 0xFA), RGBColor(0xE8, 0xF2, 0xFC), RGBColor(0xFF, 0xFF, 0xFF)
F2, F3 = "a시월구일2", "a시월구일3"


def cutout(name):
    """가장자리에서 이어진 흰 바탕만 투명하게 (그림 안쪽 흰색은 유지)."""
    p = os.path.join(art, name + ".png")
    o = os.path.join(art, name + "_t.png")
    im = Image.open(p).convert("RGB")
    w, h = im.size
    key = (255, 0, 255)
    for x in range(0, w, 8):
        for y in (0, h - 1):
            if min(im.getpixel((x, y))) > 236:
                ImageDraw.floodfill(im, (x, y), key, thresh=60)
    for y in range(0, h, 8):
        for x in (0, w - 1):
            if min(im.getpixel((x, y))) > 236:
                ImageDraw.floodfill(im, (x, y), key, thresh=60)
    rgba = im.convert("RGBA")
    px = rgba.load()
    for y in range(h):
        for x in range(w):
            if px[x, y][:3] == key:
                px[x, y] = (255, 255, 255, 0)
    rgba = rgba.crop(rgba.getbbox())
    rgba.save(o)
    return o, rgba.size


prs = Presentation(src)
s = prs.slides[3]
tree = s.shapes._spTree
for sh in list(s.shapes):
    if sh.name in ("그룹 90", "그림 89"):
        tree.remove(sh._element)


def box(shape, l, t, w, h, fill=None, line=None, text=None, size=10, color=NAVY, font=F3, adj=None, dash=False, lw=0.75):
    b = s.shapes.add_shape(shape, Inches(l), Inches(t), Inches(w), Inches(h))
    b.shadow.inherit = False
    if adj is not None:
        b.adjustments[0] = adj
    if fill is None:
        b.fill.background()
    else:
        b.fill.solid(); b.fill.fore_color.rgb = fill
    if line is None:
        b.line.fill.background()
    else:
        b.line.color.rgb = line; b.line.width = Pt(lw)
        if dash:
            b.line.dash_style = MSO_LINE.DASH
    tf = b.text_frame
    tf.margin_left = tf.margin_right = Inches(0.04); tf.margin_top = tf.margin_bottom = Inches(0.02)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE; tf.word_wrap = True
    if text:
        for i, ln in enumerate(text if isinstance(text, list) else [text]):
            pg = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            pg.alignment = PP_ALIGN.CENTER
            r = pg.add_run(); r.text = ln
            r.font.size = Pt(size); r.font.color.rgb = color; r.font.name = font
            rPr = r._r.get_or_add_rPr()
            for tag in ("a:ea",):
                from pptx.oxml.ns import qn
                ea = rPr.find(qn(tag))
                if ea is None:
                    from lxml import etree
                    ea = etree.SubElement(rPr, qn(tag))
                ea.set("typeface", font)
    return b


def pic(path, l, t, w):
    return s.shapes.add_picture(path, Inches(l), Inches(t), width=Inches(w))


# 하단 도시 풍경 (위쪽 흰 여백은 자르고, 맨 뒤로)
city = pic(os.path.join(art, "city.png"), 0, 0, 10.83)
full_h = city.height
city.crop_top = 0.45
city.crop_bottom = 0.18
city.height = int(full_h * (1 - 0.27 - 0.36))
city.top = Inches(7.5) - city.height
tree.remove(city._element); tree.insert(2, city._element)

# 왼쪽: 노트북 + 화면 안 구성
lp, (lw_, lh_) = cutout("laptop")
LW = 5.3; LL, LT = 0.35, 2.22
laptop = pic(lp, LL, LT, LW)
LH = LW * lh_ / lw_
im = Image.open(lp); W0, H0 = im.size
# 화면(흰 면) 범위를 픽셀에서 읽는다: 가운데 세로줄·가로줄에서 흰 구간
rgb = im.convert("RGB")
cx = W0 // 2
ys = [y for y in range(H0) if min(rgb.getpixel((cx, y))) > 245 and im.getpixel((cx, y))[3] > 0]
y0, y1 = ys[0], [y for i, y in enumerate(ys) if i == len(ys) - 1 or ys[i + 1] != y + 1][0]
cy = (y0 + y1) // 2
xs = [x for x in range(W0) if min(rgb.getpixel((x, cy))) > 245 and im.getpixel((x, cy))[3] > 0]
x0, x1 = xs[0], xs[-1]
SL, ST = LL + LW * x0 / W0, LT + LH * y0 / H0
SW, SH = LW * (x1 - x0) / W0, LH * (y1 - y0) / H0
print("screen", round(SL, 2), round(ST, 2), round(SW, 2), round(SH, 2))

box(MSO_SHAPE.ROUNDED_RECTANGLE, SL + SW / 2 - 0.75, ST + 0.1, 1.5, 0.3, fill=PINK, text="핵심 시스템", size=11, color=WHITE, adj=0.5)
box(MSO_SHAPE.RECTANGLE, SL, ST + 0.45, SW, 0.3, text="행정포털(굿모닝)", size=12)
wp, (ww, wh) = cutout("woman")
WWID = 1.25
pic(wp, SL + 0.12, ST + SH - WWID * wh / ww - 0.04, WWID)
CL, CT, CW = SL + SW - 1.62, ST + 0.85, 1.5
RH = (SH - 0.85 - 0.1) / 2
box(MSO_SHAPE.ROUNDED_RECTANGLE, CL, CT, CW, RH * 2, fill=PALE, line=SOFT, adj=0.1)
for i, (k, v) in enumerate((("분야", "5개 분야"), ("업무", "227종"))):
    box(MSO_SHAPE.RECTANGLE, CL, CT + RH * i, 0.5, RH, text=k, size=8, font=F2)
    box(MSO_SHAPE.RECTANGLE, CL + 0.45, CT + RH * i, CW - 0.45, RH, text=v, size=13, color=BLUE)

# 가운데 화살표
box(MSO_SHAPE.LEFT_RIGHT_ARROW, 5.78, 3.72, 0.9, 0.62, fill=BLUE)

# 오른쪽: 사용자 조직
RL, RT, RW, RHH = 6.8, 2.3, 3.75, 3.85
box(MSO_SHAPE.ROUNDED_RECTANGLE, RL, RT, RW, RHH, fill=WHITE, line=RGBColor(0x78, 0xA8, 0xF0), adj=0.05, dash=True)
box(MSO_SHAPE.ROUNDED_RECTANGLE, RL + 0.3, RT + 0.18, RW - 0.6, 0.42, fill=BLUE, text="청주시 공무원 (5,000명)", size=13, color=WHITE, adj=0.5)
rows = ["시 본청", "4개 구청 / 보건소(상당, 서원, 청원, 흥덕)", "43개 읍면동", "16개 도서관 / 평생학습관", "사업본부 / 사업소 / 박물관 / 미술관 등"]
pitch = 0.6; top0 = RT + 0.78
for i, tx in enumerate(rows):
    y = top0 + pitch * i
    bp, (bw, bh) = cutout("b%d" % (i + 1))
    k = min(0.6 / bw, 0.52 / bh); iw, ih = bw * k, bh * k
    p_ = s.shapes.add_picture(bp, Inches(RL + 0.2 + (0.6 - iw) / 2), Inches(y + (0.52 - ih) / 2), height=Inches(ih))
    box(MSO_SHAPE.ROUNDED_RECTANGLE, RL + 0.88, y + 0.08, RW - 1.06, 0.36, fill=PALE, text=tx, size=9, adj=0.5)

prs.save(dst)
print("saved", dst)
