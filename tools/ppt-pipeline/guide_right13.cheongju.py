import zipfile,shutil,sys
sys.stdout.reconfigure(encoding="utf-8")
F=r"D:\powerPlus\제안서\청주시_발표자료(제안요약서)_v0.24_목차색·인물방향·s16연결·s17·s19아이콘·지도.pptx"
T=F+".tmp"
zi=zipfile.ZipFile(F); zo=zipfile.ZipFile(T,"w",zipfile.ZIP_DEFLATED)
for it in zi.infolist():
    d=zi.read(it.filename)
    if it.filename=="ppt/viewProps.xml":
        s=d.decode("utf-8"); n=s.count('<p:guide pos="6046"/>'); s=s.replace('<p:guide pos="6046"/>','<p:guide pos="6068"/>'); print("guide",n); d=s.encode("utf-8")
    zo.writestr(it,d)
zi.close(); zo.close(); shutil.move(T,F); print("ok")
