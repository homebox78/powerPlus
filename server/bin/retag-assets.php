<?php
// 키가드 임시 러너: _retag.json {id:{ko:[],en:[]}} 를 기존 태그에 병합(중복 제거·40개 상한) 후 UPDATE.
require 'src/Config.php'; require 'src/Database.php';
$IMPORT_KEY = (string) Config::get('import_key', '');
if ($IMPORT_KEY === '' || !hash_equals($IMPORT_KEY, (string) ($_GET['key'] ?? ''))) { http_response_code(404); exit; }
$db = Database::pdo();
$in = json_decode((string) file_get_contents(__DIR__ . '/_retag.json'), true) ?: [];
$dry = isset($_GET['dry']);
$sel = $db->prepare('SELECT tags_ko, tags_en FROM assets WHERE id=?');
$upd = $db->prepare('UPDATE assets SET tags=?, tags_ko=?, tags_en=? WHERE id=?');
$dedup = function (array $xs): array {
    $out = []; $seen = [];
    foreach ($xs as $x) {
        $x = trim((string) $x); if ($x === '') continue;
        if (class_exists('Normalizer')) $x = Normalizer::normalize($x, Normalizer::FORM_C);
        $k = mb_strtolower($x); if (isset($seen[$k])) continue;
        $seen[$k] = 1; $out[] = $x;
    }
    return $out;
};
$n = 0; $sumKo = 0; $sumEn = 0;
foreach ($in as $id => $t) {
    $sel->execute([$id]); $row = $sel->fetch(PDO::FETCH_ASSOC); if (!$row) continue;
    $ko = $dedup(array_merge(json_decode($row['tags_ko'] ?: '[]', true) ?: [], $t['ko'] ?? []));
    $en = $dedup(array_merge(json_decode($row['tags_en'] ?: '[]', true) ?: [], $t['en'] ?? []));
    $ko = array_slice($ko, 0, 40); $en = array_slice($en, 0, 40);
    $all = array_values(array_unique(array_merge($ko, $en)));
    if (!$dry) $upd->execute([json_encode($all, JSON_UNESCAPED_UNICODE), json_encode($ko, JSON_UNESCAPED_UNICODE), json_encode($en, JSON_UNESCAPED_UNICODE), $id]);
    $n++; $sumKo += count($ko); $sumEn += count($en);
}
echo json_encode(['updated' => $n, 'dry' => $dry, 'avg_ko' => $n ? round($sumKo / $n, 1) : 0, 'avg_en' => $n ? round($sumEn / $n, 1) : 0]);
