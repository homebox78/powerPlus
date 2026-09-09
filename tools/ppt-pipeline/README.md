# 장표(PPT) 등록 파이프라인 — 전체본 + 낱장 분기

완성된 발표 장표 하나를 **전체 패키지 1건 + 슬라이드별 낱장 N건**으로 등록한다.
낱장이 따로 등록돼야 "표지만", "로드맵만", "조직도만" 같은 검색이 걸린다.

## 흐름

```
data/_incoming/ppt/<파일>.pptx
  ① optimize.py   이미지 다운스케일 + 불투명 PNG→JPEG + 알파 PNG 조건부 양자화
  ② split.py      슬라이드 1장짜리 낱장으로 분할(zip 수술, 마스터 가지치기)
  ③ render.py     PowerPoint COM 으로 슬라이드 PNG 렌더(썸네일 겸 검수용)
  ④ dump.py       슬라이드별 텍스트 추출 → 키워드 작성 근거
  ⑤ sheet.py      번호 컨택트시트 → 눈으로 분류·키워드 확정
  ⑥ meta.py       이름 · slide_page · 키워드 정의(meta.sample.py 복사해 작성)
  ⑦ stage.py      _stage/ppt/{files,thumbs,manifest.json} 구성
  ⑧ tar → scp → server/bin/import-ppt.php (웹루트 임시 사본 + curl ?key=)
```

## 실행 예

```bash
PY="C:/Users/hbox7/AppData/Local/Python/pythoncore-3.14-64/python.exe"
cd <작업폴더>

# ① 최적화 (마지막 인자 = 이미지 최대 변, 1200 이면 대개 40MB 아래로 떨어진다)
"$PY" optimize.py "d:/powerPlus/data/_incoming/ppt/원본.pptx" full.pptx 1200

# ② 낱장 분할
"$PY" split.py full.pptx parts

# ③ 썸네일 렌더(전체) / 특정 장만 하려면 뒤에 번호 나열
"$PY" render.py full.pptx thumbs

# ④⑤ 텍스트·시트로 내용 파악
"$PY" dump.py && "$PY" sheet.py 1 16

# ⑥ meta.py 작성 후 ⑦ 스테이징
"$PY" stage.py
```

이후 `_stage/ppt` 를 tar 로 묶어 서버 `<webroot>/_stage/` 에 풀고,
`bin/import-ppt.php` 를 웹루트로 복사해 `curl 'localhost/powerPlus/<임시>.php?key=<import_key>'`.

## 규칙 · 함정

- **용량**: 서버 장표 상한 40MB. 이미지 최대 변 1200px 이면 233MB → 25MB 수준으로 떨어지고
  원본과 렌더 색차 0.1 미만(육안 구분 불가)이다. 값을 바꾸면 반드시 렌더를 대조할 것.
- ⚠️ **낱장이 전부 원본 크기로 나오면 마스터 가지치기가 안 된 것**이다. slideMaster 가
  전체 layout 을 참조하므로, 그 슬라이드가 쓰는 layout 만 남기지 않으면 미디어가 통째로 딸려온다.
  `split.py` 는 master 의 `sldLayoutIdLst` 와 master.rels 를 함께 잘라낸다.
- ⚠️ 낱장에는 notesMaster·handoutMaster·섹션 목록(`p14:sectionLst`)을 남기지 않는다.
  남기면 다른 제안서의 빈 섹션이 탐색창에 보인다.
- **분류**(`slide_page`): cover / toc / divider / content / qa / etc. 전체본은 `slide_kind: package`.
- **키워드**: 장표 안에 실제로 쓰인 말을 우선 넣는다(폭염·영향체인·G-클라우드처럼).
  거기에 ①용도(로드맵·조직도·구성도·간지) ②도메인(기후위기적응·웹지아이에스) ③표기 변형
  (Web-GIS → 웹지아이에스)을 더한다. 사업 공통 키워드는 `COMMON_KO/EN` 으로 전 낱장에 얹는다.
- 등록이 끝나면 **로컬 원본은 삭제**한다(서버가 라이브 라이브러리).
