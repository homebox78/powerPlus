<?php
declare(strict_types=1);
/**
 * 장표(ppt) 일괄 임포터. 이미지 전용인 import-assets.php 와 짝을 이루는 ppt 전용 버전.
 * 보안: ?key= 필요. bin/ 은 .htaccess 차단이므로 실행 시 웹루트로 임시 업로드 →
 *       curl 호출 → 삭제하는 패턴으로 쓴다(import-assets.php 와 동일).
 *
 * 입력(웹루트 기준):
 *   _stage/ppt/files/<slug>.pptx        ← 미디어 정리된 장표 파일(<=40MB)
 *   _stage/ppt/thumbs/<slug>.png        ← 썸네일(선택)
 *   _stage/ppt/manifest.json            ← 자산 메타(아래 형식)
 *
 * manifest.json:
 *   { "category":"ppt", "items":[
 *       { "slide":"files/a01.pptx", "thumb":"thumbs/a01.png",
 *         "slide_kind":"package|single", "slide_page":"cover|toc|divider|greeting|content|qa|etc|null",
 *         "name":"표시명", "tags_ko":[...], "tags_en":[...] }, ... ] }
 *
 * 동작: 각 item → nextId('ppt') 부여 → uploads/ppt/{id}.pptx 복사 + (썸네일이 있으면)
 *       uploads/ppt/{id}.png 저장 후 900px 리사이즈 + 360px 썸네일 생성 → assets 행 생성.
 *       처리한 파일은 _imported/ppt/ 로 이동(중복 등록 방지).
 */
if (($_GET['key'] ?? '') !== 'pp_import_ppt_124e662a2d19') { http_response_code(404); exit; }
@set_time_limit(0);          // 618개 처리 — 실행시간 제한 해제
@ignore_user_abort(true);    // curl 끊겨도 끝까지 진행
header('Content-Type: text/plain; charset=utf-8');
require __DIR__ . '/src/Database.php';
require __DIR__ . '/src/AssetService.php';
require __DIR__ . '/src/CategoryService.php';
require __DIR__ . '/src/Thumb.php';

$root  = __DIR__ . '/';
$svc   = new AssetService();
$cats  = new CategoryService();
$stage = $root . '_stage/ppt';
$manFile = $stage . '/manifest.json';

if (!$cats->exists('ppt')) { echo "카테고리 없음: ppt\n"; exit; }
if (!is_file($manFile)) { echo "manifest.json 없음: $manFile\n"; exit; }
$man = json_decode((string) file_get_contents($manFile), true);
$items = is_array($man['items'] ?? null) ? $man['items'] : [];

$PAGES = ['cover','toc','divider','greeting','content','qa','etc'];
$done = 0; $skip = 0; $errs = [];

foreach ($items as $it) {
    $slideRel = (string) ($it['slide'] ?? '');
    $src = $stage . '/' . $slideRel;
    if ($slideRel === '' || !is_file($src)) { $skip++; continue; } // 이미 처리(이동)됐거나 누락
    $ext = strtolower(pathinfo($src, PATHINFO_EXTENSION));
    if (!in_array($ext, ['ppt','pptx'], true)) { $errs[] = "장표 아님: $slideRel"; continue; }

    $ko = is_array($it['tags_ko'] ?? null) ? $it['tags_ko'] : [];
    $en = is_array($it['tags_en'] ?? null) ? $it['tags_en'] : [];
    if (!$ko && !$en) { $skip++; $errs[] = "태그 없음(건너뜀): $slideRel"; continue; }

    $kind = ($it['slide_kind'] ?? '') === 'single' ? 'single' : 'package';
    $page = null;
    if ($kind === 'single') {
        $p = (string) ($it['slide_page'] ?? '');
        $page = in_array($p, $PAGES, true) ? $p : 'etc';
    }

    $id = $svc->nextId('ppt');
    $relSlide = "uploads/ppt/$id.$ext";
    @mkdir(dirname($root . $relSlide), 0775, true);
    if (!@copy($src, $root . $relSlide)) { $errs[] = "장표 복사 실패: $slideRel"; continue; }

    // 썸네일(선택): uploads/ppt/{id}.png 저장 → 900px 리사이즈 → 360px 썸네일
    $relImg = null; $thumbRel = null;
    $thumbSrc = isset($it['thumb']) ? $stage . '/' . $it['thumb'] : null;
    if ($thumbSrc && is_file($thumbSrc)) {
        $relImg = "uploads/ppt/$id.png";
        if (@copy($thumbSrc, $root . $relImg)) {
            $tmp = $root . $relImg . '.tmp';
            if (Thumb::make($root . $relImg, $tmp, 900)) { @rename($tmp, $root . $relImg); }
            else { @unlink($tmp); }
            $tp = Thumb::pathFor($relImg);
            $thumbRel = Thumb::make($root . $relImg, $root . $tp, 360) ? $tp : null;
        } else { $relImg = null; }
    }

    $svc->create([
        'id' => $id, 'category' => 'ppt',
        'name' => ($it['name'] ?? '') !== '' ? (string) $it['name'] : null,
        'tags_ko' => array_values(array_slice($ko, 0, 40)),
        'tags_en' => array_values(array_slice($en, 0, 40)),
        'slide_path' => $relSlide, 'slide_kind' => $kind, 'slide_page' => $page,
        'image_path' => $relImg, 'thumb_path' => $thumbRel,
    ]);

    // 처리 완료 → _imported/ppt 로 이동(중복 등록 방지)
    foreach ([$src, $thumbSrc] as $mv) {
        if ($mv && is_file($mv)) {
            $dst = $root . '_imported/ppt/' . ltrim(str_replace($stage, '', $mv), '/\\');
            @mkdir(dirname($dst), 0775, true);
            @rename($mv, $dst);
        }
    }
    $done++;
    echo "  + $id  [$kind" . ($page ? "/$page" : "") . "]  {$it['name']}\n";
}

echo "\n등록(신규): $done · 건너뜀: $skip\n";
foreach ($errs as $e) echo "  - $e\n";
echo "ppt 총계: ";
foreach (Database::pdo()->query("SELECT COUNT(*) c FROM assets WHERE category='ppt'") as $r) echo $r['c'] . "\n";
