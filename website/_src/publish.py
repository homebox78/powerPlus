# -*- coding: utf-8 -*-
"""생성물을 사이트 폴더로 옮긴다 — 빌드의 마지막 단계.

build.py 는 페이지를 `_src/` 안에 만들고 페이지 사이 링크를 `{{HOME}}` 같은
토큰으로 남긴다. 이 스크립트가 그 토큰을 실제 파일명으로 바꿔 상위 폴더에 쓴다.
이 단계를 빼먹으면 build.py 가 "built index.html" 을 찍어도 사이트는 그대로다.

쓰는 법
    py build.py && py polish.py index.html features.html usecases.html pricing.html
    py publish.py
    py fonts.py
"""
import io
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)

PAGES = ['index.html', 'features.html', 'usecases.html', 'pricing.html']
TOKENS = {
    '{{HOME}}': 'index.html',
    '{{FEATURES}}': 'features.html',
    '{{USECASES}}': 'usecases.html',
    '{{PRICING}}': 'pricing.html',
    '{{DOCS}}': 'docs.html',
}

if __name__ == '__main__':
    for p in PAGES:
        src = os.path.join(HERE, p)
        if not os.path.exists(src):
            sys.exit('생성물이 없습니다: %s — build.py 를 먼저 돌리세요.' % p)
        s = open(src, encoding='utf-8').read()
        for tok, fn in TOKENS.items():
            s = s.replace(tok, fn)
        left = [t for t in TOKENS if t in s]
        if left:
            sys.exit('%s 에 바뀌지 않은 토큰이 남았습니다: %s' % (p, ', '.join(left)))
        io.open(os.path.join(SITE, p), 'w', encoding='utf-8', newline='').write(s)
        print('publish %s  %6.1f KB' % (p, len(s.encode('utf-8')) / 1024))
    print('\ndocs.html 은 손으로 쓴 문서라 이 단계를 거치지 않는다.')
