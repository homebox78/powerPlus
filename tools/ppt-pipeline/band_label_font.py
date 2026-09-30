import win32com.client as win32, sys, os
sys.stdout.reconfigure(encoding="utf-8")
APPLY=len(sys.argv)>1
SRC=os.path.abspath("l19.pptx")
app=win32.GetActiveObject("PowerPoint.Application")
for p in app.Presentations:
    if "v0.19" in p.FullName: p.SaveCopyAs(SRC)
pr=app.Presentations.Open(SRC,ReadOnly=False,WithWindow=False)
def walk(c):
    for i in range(1,c.Count+1):
        s=c.Item(i)
        if s.Type==6: yield from walk(s.GroupItems)
        else: yield s
n=0
for sl in pr.Slides:
    shs=list(walk(sl.Shapes))
    bands=[s for s in shs if s.Type==1 and s.AutoShapeType==152 and 0.35*72<=s.Height<=0.7*72 and s.Width>=1.8*72 and s.Top<5*72]
    for b in bands:
        cx,cy=b.Left+b.Width/2,b.Top+b.Height/2
        texts=[t for t in shs if t.HasTextFrame and t.TextFrame.HasText and t.Left<=cx<=t.Left+t.Width and t.Top<=cy<=t.Top+t.Height and t.Height<=1.2*72]
        for t in texts:
            tr=t.TextFrame.TextRange
            print(sl.SlideIndex, b.Name,'|',t.Name, tr.Font.Name, tr.Font.Size, tr.Text[:25].replace('\r','/'))
            if APPLY and tr.Font.Size>=16 and sl.SlideIndex not in (18,38):
                tr.Font.Name="a시월구일3"; tr.Font.NameFarEast="a시월구일3"; tr.Font.Size=16; n+=1
if APPLY:
    pr.SaveCopyAs(r"D:\powerPlus\제안서\청주시_발표자료(제안요약서)_v0.20_섹션라벨16.pptx")
pr.Close(); print("적용",n)
