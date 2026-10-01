set -e
cd /d/powerPlus
S=C:/Users/hbox7/AppData/Local/Temp/claude/d--powerPlus/4e9aa913-8dbd-4e57-9712-83f0924f0b04/scratchpad/merge2
T=tools/ppt-pipeline; R=$T/restore
python $R/s22c.py $S/b6.pptx $S/f1.pptx
python $R/s05b.py $S/f1.pptx $S/f2.pptx
python $R/s24b.py $S/f2.pptx $S/f3.pptx
python $T/bar_center.py $S/f3.pptx $S/f4.pptx
python $T/small_font3.py $S/f4.pptx $S/f5.pptx
python $R/s25b.py $S/f5.pptx $S/f6.pptx
python $R/s26b.py $S/f6.pptx $S/f7.pptx
python $R/s27b.py $S/f7.pptx $S/f8.pptx
python $R/s28b.py $S/f8.pptx $S/f9.pptx
python $R/s29b.py $S/f9.pptx $S/f10.pptx
python $R/s31b.py $S/f10.pptx $S/f11.pptx
python $T/small_bar.py $S/f11.pptx $S/f12.pptx

python $T/vcenter_text.py $S/f12.pptx $S/f13.pptx
python $T/fit_edges.py $S/f13.pptx $S/f14.pptx
python $T/fit_breaks.py $S/f14.pptx $S/f15.pptx
python $R/s34b.py $S/f15.pptx $S/f16.pptx
python $R/s34c.py $S/f16.pptx $S/f17.pptx
