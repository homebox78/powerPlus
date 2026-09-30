import win32com.client as win32, sys, os
sys.stdout.reconfigure(encoding="utf-8")
SRC=os.path.abspath("l18.pptx"); DST=r"D:\powerPlus\제안서\청주시_발표자료(제안요약서)_v0.19_s22지도.pptx"
IMG=r"C:\Users\hbox7\AppData\Local\Temp\claude\d--powerPlus\a457a841-ad4d-46e9-9ce1-62de9bb0eee4\scratchpad\map_thick.png"
def rgb(h): return int(h[4:6],16)<<16|int(h[2:4],16)<<8|int(h[0:2],16)
app=win32.Dispatch("PowerPoint.Application"); pr=app.Presentations.Open(SRC,ReadOnly=False,WithWindow=False)
sl=pr.Slides(22); S=sl.Shapes
old=S("Picture 73"); L,T,W,H=old.Left,old.Top,old.Width,old.Height; z=old.ZOrderPosition
h=H; w=h*5158/4836; l=L+(W-w)/2
new=S.AddPicture(IMG,0,-1,l,T,w,h); new.Name="MAP_cheongju"
while new.ZOrderPosition>z: new.ZOrder(3)   # msoSendBackward until at old position
old.Delete()
cx,cy=l+w/2,T+h/2
for txt,fx,fy in (("청원구",0.50,0.16),("흥덕구",0.18,0.60),("상당구",0.80,0.47),("서원구",0.47,0.79)):
    tb=S.AddTextbox(1,l+fx*w-0.4*72,T+fy*h-0.11*72,0.8*72,0.22*72); tb.Name="GU_"+txt
    tr=tb.TextFrame.TextRange; tr.Text=txt; tr.Font.Name="a시월구일4"; tr.Font.NameFarEast="a시월구일4"; tr.Font.Size=11; tr.Font.Color.RGB=rgb("0B2E6B"); tr.ParagraphFormat.Alignment=2
    tb.TextFrame.MarginLeft=tb.TextFrame.MarginRight=tb.TextFrame.MarginTop=tb.TextFrame.MarginBottom=0; tb.TextFrame.WordWrap=0
pr.SaveCopyAs(DST); pr.Close(); print("ok",w/72,h/72)
