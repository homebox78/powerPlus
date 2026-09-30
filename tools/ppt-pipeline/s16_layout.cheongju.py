import win32com.client as win32, sys, os
sys.stdout.reconfigure(encoding="utf-8")
SRC=os.path.abspath("l17.pptx"); DST=r"D:\powerPlus\제안서\청주시_발표자료(제안요약서)_v0.18_s16정리.pptx"
app=win32.Dispatch("PowerPoint.Application"); pr=app.Presentations.Open(SRC,ReadOnly=False,WithWindow=False)
sl=pr.Slides(16); S=sl.Shapes
def rgb(h): return int(h[4:6],16)<<16|int(h[2:4],16)<<8|int(h[0:2],16)
W=1.19*72; G=0.06*72; X0=0.33*72; GAP=0.30*72; HY=4.58*72; HH=0.90*72; BY=5.18*72
# 왼쪽 그룹 3장 폭·머리 높이를 오른쪽과 동일하게
g2=S("Group 2"); heads=[]; bodies=[]
for i in range(1,g2.GroupItems.Count+1):
    s=g2.GroupItems.Item(i); (heads if s.AutoShapeType==152 else bodies).append(s)
heads.sort(key=lambda s:s.Left); bodies.sort(key=lambda s:s.Left)
for k,(h,b) in enumerate(zip(heads,bodies)):
    x=X0+k*(W+G); h.Left=x;h.Width=W;h.Top=HY;h.Height=HH; b.Left=x;b.Width=W;b.Top=BY
g3=S("Group 3"); heads=[]; bodies=[]
for i in range(1,g3.GroupItems.Count+1):
    s=g3.GroupItems.Item(i); (heads if s.AutoShapeType==152 else bodies).append(s)
heads.sort(key=lambda s:s.Left); bodies.sort(key=lambda s:s.Left)
X1=X0+3*(W+G)-G+GAP
for k,(h,b) in enumerate(zip(heads,bodies)):
    x=X1+k*(W+G); h.Left=x;h.Width=W;h.Top=HY;h.Height=HH; b.Left=x;b.Width=W;b.Top=BY
# 부채꼴 화살표 삭제 → 라벨 필 + 가로선(브래킷)
for i in range(S.Count,0,-1):
    s=S.Item(i)
    if s.Name.startswith("Straight Arrow Connector"): s.Delete()
def label(old, x0, x1, txt, col):
    S(old).Delete() if False else None
    L=x1-x0; y=4.02*72
    ln=S.AddLine(x0,y+0.30*72+0.14*72,x1,y+0.30*72+0.14*72); ln.Line.ForeColor.RGB=rgb(col); ln.Line.Weight=1.0; ln.Name="BRK_"+txt
    for xx in (x0,x1):
        t=S.AddLine(xx,y+0.44*72,xx,y+0.44*72+0.10*72); t.Line.ForeColor.RGB=rgb(col); t.Line.Weight=1.0; t.Name="BRKT_"+txt
    pw=1.45*72; p=S.AddShape(5,(x0+x1)/2-pw/2,y,pw,0.30*72); p.Name="LBL_"+txt
    p.Fill.ForeColor.RGB=rgb(col); p.Line.Visible=0;
    tr=p.TextFrame.TextRange; tr.Text=txt; tr.Font.Name="a시월구일4"; tr.Font.NameFarEast="a시월구일4"; tr.Font.Size=12; tr.Font.Color.RGB=rgb("FFFFFF"); tr.ParagraphFormat.Alignment=2
    p.TextFrame.MarginTop=p.TextFrame.MarginBottom=0; p.TextFrame.VerticalAnchor=3
    p.TextFrame.WordWrap=0
label(None, X0, X0+3*W+2*G, "사업수행방안", "0456B6")
label(None, X1, X1+5*W+4*G, "사업지원방안", "3A46A0")
for nm in ("Rectangle 145",):
    S(nm).Delete()
for i in range(S.Count,0,-1):
    s=S.Item(i)
    if s.Type==17 and s.HasTextFrame and s.TextFrame.TextRange.Text.strip()=="사업수행방안": s.Delete()
# 일러스트 키워서 오른쪽 위 자리 채움
sw=S("SW13"); r=sw.Width/sw.Height; sw.Height=1.85*72; sw.Width=sw.Height*r; sw.Left=10.53*72-sw.Width; sw.Top=1.05*72
# 키메시지·설명 텍스트를 일러스트 왼쪽 영역 가운데로
for nm,w in (("Text Box 38",None),):
    pass
km=[s for s in S if s.Type==17 and s.HasTextFrame and s.TextFrame.TextRange.Text.startswith("안정적 유지관리")][0]
sub=[s for s in S if s.Type==17 and s.HasTextFrame and s.TextFrame.TextRange.Text.startswith("환경변화와")][0]
cx=(0.33*72+sw.Left)/2
km.Left=cx-km.Width/2; sub.Left=cx-sub.Width/2
pr.SaveCopyAs(DST); pr.Close(); print("ok")
