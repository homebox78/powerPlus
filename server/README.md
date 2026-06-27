# powerPlus Server (Phase 2 — PHP + MySQL)

자산 라이브러리 REST API. 프레임워크 없이 순수 PHP + PDO(MySQL)로 구성.

## 요구 사항
- PHP 8.1+ (pdo_mysql 확장)
- MySQL 5.7+ / MariaDB 10.4+

## 설정
```bash
# 1) DB 설정 복사 후 값 채우기 (config.php 는 git 제외)
cp config/config.example.php config/config.php

# 2) 스키마 생성
mysql -u root -p < sql/schema.sql

# 3) 시드 데이터 삽입 (addin mock 과 동일한 자산)
php bin/seed.php
```

## 실행 (개발)
```bash
php -S localhost:8000 public/index.php
```
> addin 의 webpack dev 서버가 `/api` 요청을 `http://localhost:8000` 으로 프록시합니다.

## API
| 메서드 | 경로 | 설명 |
|---|---|---|
| GET | `/health` | 헬스 체크 |
| GET | `/api/assets?category=&q=&page=&limit=` | 목록/검색 (페이지네이션) |
| GET | `/api/assets/{id}` | 단건 조회 |

### 응답 포맷
```json
// 목록
{ "data": [], "total": 18, "page": 1, "limit": 50 }
// 에러
{ "error": "메시지", "code": 404 }
```

## 구조
```
server/
├── public/index.php        프론트 컨트롤러 + 라우터 + CORS
├── src/
│   ├── Database.php         PDO 연결 (env 우선 → config/config.php)
│   ├── AssetService.php     조회/검색 (prepared statement)
│   └── AssetController.php  요청 파싱 → JSON 응답
├── config/config.example.php
├── sql/schema.sql
└── bin/seed.php            시드 스크립트
```

## 다음 단계
- 인증 (Google OAuth vs Azure AD — Phase 2 결정 사항)
- 자산 업로드/관리 API (관리자)
- 태그 정규화 테이블 (현재는 JSON 컬럼)
