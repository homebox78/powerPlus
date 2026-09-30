import win32com.client as win32,sys
sys.stdout.reconfigure(encoding="utf-8")
F=r"D:\powerPlus\제안서\청주시_발표자료(제안요약서)_v0.22_s16강조.pptx"
D=r"D:\powerPlus\제안서\청주시_발표자료(제안요약서)_v0.23_s25장애목록·백업표.pptx"
app=win32.Dispatch("PowerPoint.Application");pr=app.Presentations.Open(F,ReadOnly=False,WithWindow=False)
def walk(c):
    for i in range(1,c.Count+1):
        s=c.Item(i)
        if s.Type==6: yield from walk(s.GroupItems)
        else: yield s
n=m=0
for s in walk(pr.Slides(25).Shapes):
    if s.Name=="Rectangle 114":
        tr=s.TextFrame.TextRange
        for k in range(1,tr.Paragraphs().Count+1):
            pg=tr.Paragraphs(k)
            if pg.IndentLevel==1 and pg.Text.strip():
                pg.Font.Name="a시월구일3";pg.Font.NameFarEast="a시월구일3";pg.Font.Size=8.5;n+=1
    if s.HasTable and s.Name=="Table 602":
        tb=s.Table
        for r in range(1,tb.Rows.Count+1):
            for c in range(1,tb.Columns.Count+1):
                t=tb.Cell(r,c).Shape.TextFrame.TextRange; t.Font.Size=6.5;m+=1
print("1차",n,"표셀",m)
pr.SaveCopyAs(D);pr.Close()
