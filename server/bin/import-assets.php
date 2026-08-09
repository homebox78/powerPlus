<?php
declare(strict_types=1);
/**
 * 자산 일괄 임포터 (재사용). 보안: ?key= 필요. bin/ 은 .htaccess 차단이므로
 * 실행 시 웹루트로 임시 업로드 → curl 호출 → 삭제하는 패턴으로 쓴다.
 *
 * 입력(웹루트 기준):
 *   _import/<category>/<file>.(png|jpg|jpeg)      ← 리사이즈된 이미지
 *   _import/tags.json                              ← { "<category>/<file>": {"ko":[..25],"en":[..25]} }
 * 동작: 새 자산만(스테이징에 있는 파일 전부) → nextId 부여 → uploads/<cat>/ 복사 +
 *       썸네일 생성 + assets 생성(tags_ko/tags_en). 처리 후 _import/<cat> 파일은 _imported/<cat> 로 이동.
 */
if (($_GET['key'] ?? '') !== 'pp_import_2f71c98d0b5f') { http_response_code(404); exit; }
header('Content-Type: text/plain; charset=utf-8');
require __DIR__ . '/src/Database.php';
require __DIR__ . '/src/AssetService.php';
require __DIR__ . '/src/CategoryService.php';
require __DIR__ . '/src/Thumb.php';

$root = __DIR__ . '/';
$svc  = new AssetService();
$cats = new CategoryService();
$importDir = $root . '_import';
$tagsFile  = $importDir . '/tags.json';
$tagsMap   = is_file($tagsFile) ? (json_decode((string) file_get_contents($tagsFile), true) ?: []) : [];

$IMG_EXT = ['png' => 'png', 'jpg' => 'jpg', 'jpeg' => 'jpg'];
$done = 0; $skip = 0; $errs = [];

foreach (glob($importDir . '/*', GLOB_ONLYDIR) as $catDir) {
    $cat = basename($catDir);
    if (!$cats->exists($cat)) { $errs[] = "카테고리 없음: $cat"; continue; }
    foreach (glob($catDir . '/*') as $src) {
        if (!is_file($src)) continue;
        $ext = strtolower(pathinfo($src, PATHINFO_EXTENSION));
        if (!isset($IMG_EXT[$ext])) { continue; }
        $rel = $cat . '/' . basename($src);
        $tags = $tagsMap[$rel] ?? $tagsMap[basename($src)] ?? null;
        $ko = is_array($tags['ko'] ?? null) ? $tags['ko'] : [];
        $en = is_array($tags['en'] ?? null) ? $tags['en'] : [];
        if (!$ko && !$en) { $skip++; $errs[] = "태그 없음(건너뜀): $rel"; continue; }

        $id  = $svc->nextId($cat);
        $outExt = $IMG_EXT[$ext];
        $relImg = "uploads/$cat/$id.$outExt";
        @mkdir(dirname($root . $relImg), 0775, true);
        if (!@copy($src, $root . $relImg)) { $errs[] = "복사 실패: $rel"; continue; }
        $thumbRel = Thumb::pathFor($relImg);
        $thumb = Thumb::make($root . $relImg, $root . $thumbRel, 360) ? $thumbRel : null;

        $svc->create([
            'id' => $id, 'category' => $cat,
            'tags_ko' => array_values(array_slice($ko, 0, 40)),
            'tags_en' => array_values(array_slice($en, 0, 40)),
            'image_path' => $relImg, 'thumb_path' => $thumb,
        ]);
        // 처리 완료 → _imported 로 이동(중복 등록 방지)
        $movedDir = $root . '_imported/' . $cat;
        @mkdir($movedDir, 0775, true);
        @rename($src, $movedDir . '/' . basename($src));
        $done++;
    }
}

echo "등록(신규): $done · 건너뜀: $skip\n";
foreach ($errs as $e) echo "  - $e\n";
echo "카테고리별 총계:\n";
foreach (Database::pdo()->query("SELECT category, COUNT(*) c FROM assets GROUP BY category") as $r) {
    echo "  {$r['category']}: {$r['c']}\n";
}
