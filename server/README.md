# powerPlus Server (Phase 2 — PHP + MySQL)

자산 라이브러리 REST API. 프레임워크 없이 순수 PHP + PDO(MySQL).
Apache 서브디렉터리 배포(예: `https://hom2box.com/powerPlus/`)와 PHP 내장 서버 모두 지원.

## 요구 사항
- PHP 8.1+ (pdo_mysql 확장)
- MySQL 5.7+ / MariaDB 10.4+
- Apache + mod_rewrite (공유 호스팅 배포 시)

## DB 준비 (phpMyAdmin)
1. `sql/seed.sql` 내용을 phpMyAdmin SQL 탭에 붙여넣어 실행
   → `assets` 테이블 생성 + 자산 18종 입력 (DB는 `powerplus` 선택 상태)

## DB 접속 설정
`config/config.php` 를 만들고 실제 값 입력 (git 제외):
```php
<?php
return [
    'host' => 'localhost',
    'port' => 3306,
    'db'   => 'powerplus',
    'user' => '본인_DB_계정',
    'pass' => '본인_DB_비밀번호',
];
```
> 환경변수 `DB_HOST/DB_PORT/DB_NAME/DB_USER/DB_PASS` 가 있으면 그쪽이 우선.

## 배포 (Apache, 예: /var/www/html/powerPlus/)
아래 파일을 업로드:
```
powerPlus/
├── index.php          # 프론트 컨트롤러
├── .htaccess          # 라우팅 + 민감 폴더 차단
├── src/               # Database / AssetService / AssetController
└── config/config.php  # DB 접속 정보 (서버에서 직접 생성)
```
접근 URL: `https://hom2box.com/powerPlus/api/assets`

## 실행 (로컬 개발, PHP 설치 시)
```bash
php -S localhost:8000 index.php
```

## API
| 메서드 | 경로 | 설명 |
|---|---|---|
| GET | `/health` | 헬스 체크 |
| GET | `/api/assets?category=&q=&page=&limit=` | 목록/검색 (페이지네이션) |
| GET | `/api/assets/{id}` | 단건 조회 |

### 응답 포맷
```json
{ "data": [], "total": 18, "page": 1, "limit": 50 }
```

## 참고
- `bin/seed.php` : PHP CLI로 시드하는 대안 (phpMyAdmin 대신 `php bin/seed.php`)
- 인증(Google OAuth vs Azure AD)은 Phase 2 결정 사항
