# 자산 대량 등록 자동화 (runbook)

새 자산을 `data/_incoming/<category>/` 에 드롭한 뒤 "자산 등록"이라고 하면 아래를 실행한다.
대상 카테고리(이미지): icon · photo · illust · diagram. (장표 ppt 는 관리자 화면에서 분류 등록.)

## 단계
1. **신규 분리**: `data/_incoming/<cat>/` 에 있는 파일 = 미등록 신규(처리 후 `data/_imported/` 로 이동되므로 중복 없음).
2. **리사이즈**(원본 대용량 → 카테고리별): 아이콘 512 · 일러스트 700 · 다이어그램 900 · 사진 1600px. PowerShell System.Drawing, PNG는 투명 유지. 결과 → `data/_stage/<cat>/`.
3. **태깅(비전)**: 스테이지 이미지를 직접 보고 **국문 25 · 영문 25 키워드**(문장 X, 단어형 검색 키워드) 생성 → `data/_stage/tags.json` = `{ "<cat>/<file>": {"ko":[..25],"en":[..25]} }`.
   - 대량이면 멀티에이전트 워크플로(병렬 비전 태깅) 사용 — 사용자 옵트인/토큰 비용 안내.
4. **업로드+등록**:
   - tar 로 `data/_stage/*` → 서버 `<webroot>/_import/<cat>/`, `tags.json` → `<webroot>/_import/tags.json` 업로드.
   - `server/bin/import-assets.php` 를 **웹루트로 임시 업로드** → `curl ".../import-assets.php?key=<config.php의 import_key>"` → 삭제.
     (import-assets.php: nextId 부여 → uploads 복사 → 썸네일(GD) → assets 생성(tags_ko/en) → _import 파일을 _imported 로 이동)
   - 서버 `_import` 잔여 정리.
5. **로컬 정리**: `data/_incoming/<cat>/*` → `data/_imported/<cat>/` 이동(다음 회차 중복 방지).
6. **보고**: 등록 수 / 카테고리별 총계 / 건너뜀(태그 누락 등).

## 태그 규칙
- 국문 25 · 영문 25, **단어형 키워드**(검색 매칭용). 문장/조사 금지.
- 동의어·상위어·용도·형태·색/스타일·관련 상황까지 포함해 검색 적중률↑ (예 아이콘 "협업": 협업/팀/팀워크/협동/그룹/사람/동료/회의/소통/조직/…).
- 통합 tags 는 서버가 ko+en 합쳐 자동 생성(검색용). 부분일치 LIKE.

## 키 / 경로
- import key: 서버 `config/config.php`의 `import_key` 값(git 제외 — 소스에 키를 두지 않음)
- 서버 배포·접속: `server/bin/deploy.sh`, `config/deploy.env`(gitignore)

## 기존 자산 재태깅 (2026-09-11)
얇게 태깅된 자산(태그 15개 미만)에 비전 태그를 덧붙일 때.
1. 대상 id·썸네일 목록 → 번호 라벨 컨택트시트(6×5) + `idxmap.json`(idx→id) 생성
2. 시트 2장/에이전트로 병렬 태깅 → `res_NN.json` (`[{idx,ko[20],en[15]}]`)
3. `python bin/retag-merge.py` → `_retag.json` `{id:{ko,en}}` (커버리지·누락 idx 출력)
4. `_retag.json` + `bin/retag-assets.php` 를 웹루트에 scp → `curl localhost/powerPlus/retag-assets.php?key=<import_key>&dry=1` 로 평균 확인 → `dry` 빼고 실적용 → 임시 파일 삭제
   - 기존 tags_ko/tags_en 과 병합(NFC·소문자 dedup, 40개 상한), `tags` = ko∪en
5. 전후 비교는 `bin/search-audit.php`(같은 방식으로 웹루트 curl) — search_logs 무결과 (query,category) 쌍 재실행 해소율 + 아이콘 태그 밀도 + 샘플 검색
