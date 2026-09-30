import zipfile,re,sys
sys.stdout.reconfigure(encoding="utf-8")
D=r"D:\powerPlus\제안서\청주시_발표자료(제안요약서)_v0.26_원본해상도·압축안함·s7인물.pptx"
zi=zipfile.ZipFile("l26b.pptx"); zo=zipfile.ZipFile(D,"w",zipfile.ZIP_DEFLATED)
NS='xmlns:p14="http://schemas.microsoft.com/office/powerpoint/2010/main"'
for it in zi.infolist():
    d=zi.read(it.filename)
    if it.filename=="ppt/presentation.xml":
        s=d.decode("utf-8")
        s,n1=re.subn(r'<p15:guide id="2" pos="6046"[^>]*>.*?</p15:guide>','',s,count=1)
        s=re.sub(r'<p:ext uri="\{(E76CE94A-603C-4142-B9EB-6D1370010A27|D31A062A-798A-4329-ABDD-BBA856620510)\}">.*?</p:ext>','',s)
        add=f'<p:ext uri="{{E76CE94A-603C-4142-B9EB-6D1370010A27}}"><p14:discardImageEditData {NS} val="0"/></p:ext><p:ext uri="{{D31A062A-798A-4329-ABDD-BBA856620510}}"><p14:defaultImageDpi {NS} val="32767"/></p:ext>'
        assert s.count("<p:extLst>")==1
        s=s.replace("<p:extLst>","<p:extLst>"+add); print("guide removed",n1); d=s.encode("utf-8")
    zo.writestr(it,d)
zo.close(); print("ok")
