import sys, copy
from pptx import Presentation
from pptx.util import Pt
sys.stdout.reconfigure(encoding="utf-8")
A="{http://schemas.openxmlformats.org/drawingml/2006/main}"
P="{http://schemas.openxmlformats.org/presentationml/2006/main}"
E=914400
SRC=r"D:\powerPlus\제안서\청주시_발표자료(제안요약서)_v0.23_s25장애목록·백업표.pptx"
DST=r"D:\powerPlus\제안서\청주시_발표자료(제안요약서)_v0.24_목차색·인물방향·s16연결·s17·s19아이콘·지도.pptx"
p=Presentation(SRC)
def walk(sh):
    for s in sh:
        if s.shape_type==6: yield from walk(s.shapes)
        else: yield s
def setcol(r,hexv):
    rp=r._r.get_or_add_rPr()
    for f in rp.findall(A+"solidFill"): rp.remove(f)
    sf=rp.makeelement(A+"solidFill",{}); c=sf.makeelement(A+"srgbClr",{"val":hexv}); sf.append(c)
    # solidFill 은 ln 뒤·effectLst 앞 — 기존 순서 단순화: 맨 앞 삽입 후 ln 이 있으면 그 뒤로
    ln=rp.find(A+"ln")
    if ln is not None: ln.addnext(sf)
    else: rp.insert(0,sf)
# 1) 목차 색 통일 — 3·9·30 '직사각형 6': '전략N' 런(3A46A0)만 예외, 나머지 1F4E79
n1=0
for n in (3,9,30):
    for s in p.slides[n-1].shapes:
        if s.name!="직사각형 6": continue
        for pg in s.text_frame.paragraphs:
            for k,r in enumerate(pg.runs):
                t=r.text
                if t.strip().startswith("전략") or (t.strip().isdigit() and k>1): continue
                setcol(r,"1F4E79"); n1+=1
print("목차 런",n1)
# 2) s17 상단 박스 10pt
n2=0
for s in p.slides[16].shapes:
    if s.has_text_frame and abs(s.top/E-3.3)<0.15:
        for pg in s.text_frame.paragraphs:
            for r in pg.runs:
                if r.font.size and r.font.size.pt==11: r.font.size=Pt(10); n2+=1
print("s17 10pt 런",n2)
# 3) s19 아이콘 15%
n3=0
for s in walk(p.slides[18].shapes):
    if s.shape_type==13:
        w,h=s.width,s.height; s.width=int(w*1.15); s.height=int(h*1.15); s.left-= (s.width-w)//2; s.top-=(s.height-h)//2; n3+=1
print("s19 아이콘",n3)
# 4) 인물 방향 — 8 SW08, 18 SW15 반전
for n,name in ((8,"SW08"),(18,"SW15")):
    for s in walk(p.slides[n-1].shapes):
        if s.name==name:
            xf=s._element.find(P+"spPr").find(A+"xfrm")
            if xf.get("flipH")=="1": del xf.attrib["flipH"]
            else: xf.set("flipH","1")
            print("flip",n,name,xf.get("flipH"))
# 5) s22 지도 투명도 40%
for s in walk(p.slides[21].shapes):
    if s.name=="MAP_cheongju":
        blip=s._element.find(".//"+A+"blip")
        for c in list(blip):
            if c.tag==A+"alphaModFix": blip.remove(c)
        am=blip.makeelement(A+"alphaModFix",{"amt":"40000"}); blip.insert(0,am); print("map alpha 40%")
# 6) s16 카드 본체: 위 모서리 둥근 → 아래 모서리 둥근(180° 회전 + 글 반대 회전)
n6=0
for g in [x for x in p.slides[15].shapes if x.shape_type==6 and x.top<5.2*E and x.top+x.height>6.5*E]:
    for s in g.shapes:
        pg=s._element.find(P+"spPr").find(A+"prstGeom")
        pr=pg.get("prst") if pg is not None else None
        if pr in ("round2SameRect","roundRect") and s.top>=5.0*E:
            pg.set("prst","round2SameRect")   # 본체(머리는 top<5in)
            xf=s._element.find(P+"spPr").find(A+"xfrm"); xf.set("rot","10800000")
            bp=s._element.find(P+"txBody").find(A+"bodyPr"); bp.set("rot","-10800000")
            t,b=bp.get("tIns"),bp.get("bIns")
            if t is not None or b is not None:
                bp.set("tIns",b or "45720"); bp.set("bIns",t or "45720")
            n6+=1
        elif s.top>=5.0*E: print("본체 prst",pr,s.name)
print("s16 본체",n6)
p.save(DST); print("saved")
