import win32com.client as win32, sys, os
sys.stdout.reconfigure(encoding="utf-8")
app=win32.Dispatch("PowerPoint.Application")
DST=r"D:\powerPlus\제안서\청주시_발표자료(제안요약서)_v0.23_s25장애목록·백업표.pptx"
pr=app.Presentations.Open(DST,ReadOnly=False,WithWindow=False)
sl=pr.Slides(16); S=sl.Shapes
def rgb(h): return int(h[4:6],16)<<16|int(h[2:4],16)<<8|int(h[0:2],16)
# 옛 라벨·브래킷 삭제
for i in range(S.Count,0,-1):
    n=S.Item(i).Name
    if n.startswith(("BRK_","BRKT_","LBL_","FAN_","DOT_")): S.Item(i).Delete()
# 규격: 수행(강조) 카드 폭·머리 10% 크게
W2=1.15*72; G=0.05*72; W1=W2*1.10; HH2=0.90*72; HH1=HH2*1.10; BY2=5.18*72; BH=1.82*72
X0=0.30*72; GAP=0.30*72
def parts(g):
    hs=[];bs=[]
    for i in range(1,g.GroupItems.Count+1):
        s=g.GroupItems.Item(i); (hs if s.AutoShapeType==152 else bs).append(s)
    return sorted(hs,key=lambda s:s.Left),sorted(bs,key=lambda s:s.Left)
BOT=BY2+BH
hs,bs=parts(S("Group 2"))
for k,(h,b) in enumerate(zip(hs,bs)):
    x=X0+k*(W1+G); h.Left=x;h.Width=W1;h.Height=HH1;h.Top=BY2-HH1; b.Left=x;b.Width=W1;b.Top=BY2;b.Height=BH
    h.Fill.ForeColor.RGB=rgb("0456B6"); h.Line.Visible=0
    b.Line.ForeColor.RGB=rgb("0456B6"); b.Line.Weight=1.25
X1=X0+3*W1+2*G+GAP
hs,bs=parts(S("Group 3"))
for k,(h,b) in enumerate(zip(hs,bs)):
    x=X1+k*(W2+G); h.Left=x;h.Width=W2;h.Height=HH2;h.Top=BY2-HH2; b.Left=x;b.Width=W2;b.Top=BY2;b.Height=BH
XR=X1+5*W2+4*G
# 라벨: 수행 = 짙은 파랑 채움 + 왼쪽 두꺼운 포인트, 지원 = 흰 바탕 남색 테두리
LY=3.42*72; LH=0.34*72
def lab(txt,x0,x1,fill,line,tc,w=1.55*72,bold=True):
    p=S.AddShape(5,(x0+x1)/2-w/2,LY,w,LH); p.Name="LBL_"+txt
    p.Fill.ForeColor.RGB=rgb(fill); p.Line.ForeColor.RGB=rgb(line); p.Line.Weight=1.25
    tr=p.TextFrame.TextRange; tr.Text=txt; tr.Font.Name="a시월구일4"; tr.Font.NameFarEast="a시월구일4"; tr.Font.Size=13; tr.Font.Color.RGB=rgb(tc); tr.ParagraphFormat.Alignment=2
    p.TextFrame.MarginTop=p.TextFrame.MarginBottom=0; p.TextFrame.VerticalAnchor=3; p.TextFrame.WordWrap=0
    return p
def fan(p,heads,col):
    cx=p.Left+p.Width/2; y0=p.Top+p.Height
    for h in heads:
        ln=S.AddLine(cx,y0,h.Left+h.Width/2,h.Top); ln.Line.ForeColor.RGB=rgb(col); ln.Line.Weight=1.0; ln.Name="FAN_"+p.Name
        d=S.AddShape(9,h.Left+h.Width/2-3,h.Top-3,6,6); d.Fill.ForeColor.RGB=rgb(col); d.Line.Visible=0; d.Name="DOT_"+p.Name
hs1,_=parts(S("Group 2")); hs2,_=parts(S("Group 3"))
p1=lab("사업수행방안",X0,X0+3*W1+2*G,"0456B6","0456B6","FFFFFF",w=1.75*72); p1.TextFrame.TextRange.Font.Size=14
p2=lab("사업지원방안",X1,XR,"FFFFFF","3A46A0","3A46A0")
fan(p1,hs1,"0456B6"); fan(p2,hs2,"3A46A0")
pr.Save(); pr.Close(); print("ok",XR/72)
