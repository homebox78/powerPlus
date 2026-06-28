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
   - `server/bin/import-assets.php` 를 **웹루트로 임시 업로드** → `curl ".../import-assets.php?key=pp_import_7Yq2"` → 삭제.
     (import-assets.php: nextId 부여 → uploads 복사 → 썸네일(GD) → assets 생성(tags_ko/en) → _import 파일을 _imported 로 이동)
   - 서버 `_import` 잔여 정리.
5. **로컬 정리**: `data/_incoming/<cat>/*` → `data/_imported/<cat>/` 이동(다음 회차 중복 방지).
6. **보고**: 등록 수 / 카테고리별 총계 / 건너뜀(태그 누락 등).

## 태그 규칙
- 국문 25 · 영문 25, **단어형 키워드**(검색 매칭용). 문장/조사 금지.
- 동의어·상위어·용도·형태·색/스타일·관련 상황까지 포함해 검색 적중률↑ (예 아이콘 "협업": 협업/팀/팀워크/협동/그룹/사람/동료/회의/소통/조직/…).
- 통합 tags 는 서버가 ko+en 합쳐 자동 생성(검색용). 부분일치 LIKE.

## 키 / 경로
- import key: `pp_import_7Yq2` (운영 전 교체 권장)
- 서버 배포·접속: `server/bin/deploy.sh`, `config/deploy.env`(gitignore)
