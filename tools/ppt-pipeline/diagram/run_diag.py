# -*- coding: utf-8 -*-
"""지정한 도식 빌더들을 차례로 적용. 인자: <src> <dst> 모듈명...  (예: d_s20 d_s21)"""
import sys, importlib
sys.path.insert(0,".")
from pptx import Presentation
src,dst=sys.argv[1],sys.argv[2]
p=Presentation(src)
for m in sys.argv[3:]:
    importlib.import_module(m).build(p); print("built", m)
p.save(dst)
