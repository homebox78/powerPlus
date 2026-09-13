# -*- coding: utf-8 -*-
"""빌드 후처리 — 문장이 끝나는 마침표 뒤에서 줄을 바꾼다.

한 문단에 두 문장이 이어 붙으면 한글에서는 어디서 끊어 읽어야 할지 잘 안 보인다.
'…습니다. 다음 문장' 처럼 종결어미 + 마침표 뒤에 <br> 를 넣어 문장마다 줄을 준다.

태그 밖 텍스트에만 적용한다(속성값·style·script 는 건드리지 않는다).
"""
import io, re, sys

TAG = re.compile(r'(<[^>]*>)')
# 한국어 종결어미(다/요/죠) + 마침표 + 공백 → 다음 문장 시작
SENT = re.compile(r'(?<=[다요죠])\.[ \t]+(?=[^\s<])')
# 의문문 종결
QSENT = re.compile(r'(?<=[까요나])\?[ \t]+(?=[^\s<])')
# 굵은 글씨가 문장을 끝내고 닫힌 뒤 다음 문장이 이어지는 경우
AFTER_TAG = re.compile(r'(?<=다\.)(</b>|</strong>|</span>)[ \t]+(?=[^\s<])')

SKIP_OPEN = ('<style', '<script', '<title', '<code')
SKIP_CLOSE = ('</style', '</script', '</title', '</code')


def add_breaks(html: str) -> str:
    parts = TAG.split(html)
    depth = 0
    out = []
    for part in parts:
        if part.startswith('<'):
            low = part.lower()
            if low.startswith(SKIP_OPEN):
                depth += 1
            elif low.startswith(SKIP_CLOSE):
                depth = max(0, depth - 1)
            out.append(part)
        else:
            out.append(part if depth else QSENT.sub('?<br>', SENT.sub('.<br>', part)))
    html = ''.join(out)
    return AFTER_TAG.sub(lambda m: m.group(1) + '<br>', html)


if __name__ == '__main__':
    for f in sys.argv[1:]:
        s = io.open(f, encoding='utf-8').read()
        before = s.count('<br>')
        s = add_breaks(s)
        io.open(f, 'w', encoding='utf-8', newline='').write(s)
        print('%-14s +%d 문장 줄바꿈' % (f, s.count('<br>') - before))
