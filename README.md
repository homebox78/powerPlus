# powerPlus — PowerPoint 자산 라이브러리 Add-in

PowerPoint 작업창에서 회사 자산(아이콘·사진·일러스트·다이어그램·장표)을 **카테고리/태그로 검색 → 클릭 한 번에 슬라이드 삽입**하는 사내 도구.

- 사용자 규모: 사내 ~300명 (회사 도메인 `solideos.com`)
- 라이브 API: `https://hom2box.com/powerPlus/api`
- 관리자: `https://hom2box.com/powerPlus/admin/`

---

## 📁 폴더 구조

| 폴더 | 무엇 | 비고 |
|---|---|---|
| **`addin/`** | 애드인(작업창) 프론트엔드 — React 18 + TypeScript + Webpack 5, Office.js | 빌드 결과 `dist/`는 서버 `app/`으로 배포 |
| **`server/`** | 백엔드 API — PHP + MySQL(MariaDB), 프레임워크 없이 PDO | `index.php`(라우터)→Controller→Service→Database |
| **`server/admin/`** | 관리자 웹 대시보드(단일 HTML) — 자산/카테고리/공지/요청/통계 | 서버에서 호스팅 |
| **`server/bin/`** | 배포·마이그레이션·자산 임포트 스크립트 + 런북 | `deploy.sh`, `migrate.php`, `import-assets.php`, `ASSET-IMPORT.md` |
| **`installer/`** | **설치 마법사 소스** — WebView2(.NET8 WinForms) + 시안 HTML UI | 빌드하면 `powerPlus_Setup.exe` 생성 (개발용, 고객에 주지 않음) |
| **`design/`** | 디자인 시안(`*.dc.html`) — 디자인시스템/애드온/관리자/설치 | 구현의 1:1 기준(mock) |
| **`배포/`** | **전달용 완성품**(대상별 분리) | [배포/README.md](배포/README.md) 참고 |
| **`data/`** | 자산 원본/스테이징(대량 등록용) | git 제외(.gitignore), 서버 uploads에 보관 |
| **`.claude/`** | 개발 컨텍스트 라이브러리(myDev 서브모듈, 비공개) | 프로젝트 repo엔 포인터 커밋 안 함 |

### 배포물(대상별) — `배포/`
- `배포/사용자/` : **일반 사용자**에게 → 설치 파일 `powerPlus_Setup.exe` + [설치·사용 안내](배포/사용자/설치_및_사용안내.md)
- `배포/관리자/` : **관리자**에게 → [관리자 대시보드 안내](배포/관리자/관리자_안내.md)

---

## 🏗️ 기술 스택
- **애드인**: React 18 · TypeScript 5.6 · Webpack 5 · Office.js · plain CSS(디자인 토큰)
- **서버**: PHP · MariaDB(PDO, prepared statement) · REST/JSON
- **호스팅**: hom2box.com (GCP Compute Engine VM, Apache 서브디렉터리)
- **인증**: 이메일 OTP(6자리) + `solideos.com` 도메인 제한
- **폰트/디자인**: Pretendard + JetBrains Mono, 오렌지 팔레트(Primary `#E0701F`, 채움버튼=블랙)

## ▶️ 개발 / 빌드 / 배포

```bash
# 애드인 개발 서버 (작업창 https + /api 프록시)
cd addin && npm install && npm start

# 애드인 운영 빌드
cd addin && npm run build      # → addin/dist

# 서버+애드인 한 방 배포 (SSH/SCP, config.php는 서버 값 보존)
cd server && bash bin/deploy.sh

# 설치 exe 빌드 (수정 시: installer.html / manifest 바뀔 때)
cd installer && dotnet publish -c Release -r win-x64 --self-contained true \
  -p:PublishSingleFile=true -p:IncludeNativeLibrariesForSelfExtract=true \
  -p:EnableCompressionInSingleFile=true
# → installer/powerPlus_Setup.exe (배포/사용자/로 복사)
```

> 애드인/관리자 코드는 **서버 호스팅**이라, 코드 업데이트 시 사용자 재설치 불필요(배포만 하면 자동 반영). 설치 exe는 아이콘/매니페스트가 바뀔 때만 재빌드.

## 🔑 핵심 기술 포인트
- 이미지 삽입: `Office.context.document.setSelectedDataAsync(base64, {coercionType:Image, …})` — `slide.shapes.addImage`는 런타임에 없음
- 장표 삽입: `presentation.insertSlidesFromBase64(b64, {formatting, targetSlideId})` — 선택 슬라이드 뒤
- 크기 단위는 pt(px 아님), 삽입은 PowerPoint 런타임에서만
- 설치 위치: PowerPoint **[삽입 → 추가 기능 → 개발자 추가 기능 → powerPlus]**

## ⚙️ 설정 / 시크릿 (git 제외)
- `server/config/config.php` — DB·메일·인증 설정 (템플릿: `config.example.php`)
- `server/config/deploy.env`, SSH 키(`*.pem`) — 배포 접속 정보
- 전부 `.gitignore` + 서버 `.htaccess` deny

## 📌 남은 작업
- 실제 PowerPoint 삽입/리본 사용자 더블클릭 테스트
- 메일 발신 신뢰도(회사 SMTP 또는 SPF/DKIM)
- 인프라 보안(phpMyAdmin 공개 제한, 키/DB 비번 관리)
