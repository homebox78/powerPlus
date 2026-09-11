<?php
// 키가드 임시 러너: search_logs 의 무결과 (query,category) 쌍을 지금 검색으로 재실행해 해소율을 잰다 + 아이콘 태그 밀도.
require 'src/Config.php'; require 'src/Database.php';
foreach (glob(__DIR__ . '/src/*.php') as $f) require_once $f;
$IMPORT_KEY = (string) Config::get('import_key', '');
if ($IMPORT_KEY === '' || !hash_equals($IMPORT_KEY, (string) ($_GET['key'] ?? ''))) { http_response_code(404); exit; }
$db = Database::pdo();
$rows = $db->query("SELECT DISTINCT query, category FROM search_logs WHERE results = 0 AND query <> ''")->fetchAll(PDO::FETCH_ASSOC);
$svc = new AssetService();
$ok = 0; $still = [];
foreach ($rows as $r) {
    $cat = (string) ($r['category'] ?? '') ?: 'all';
    try { $res = $svc->list($cat, (string) $r['query'], 1, 1); $tot = (int) ($res['total'] ?? 0); }
    catch (Throwable $e) { $tot = -1; }
    if ($tot > 0) $ok++; else $still[] = $r['query'] . '/' . $cat;
}
$dens = $db->query("SELECT AVG(JSON_LENGTH(tags_ko)) ko, AVG(JSON_LENGTH(tags_en)) en, SUM(JSON_LENGTH(tags_ko) < 15) thin FROM assets WHERE category='icon'")->fetch(PDO::FETCH_ASSOC);
$samples = [];
foreach (['표준','전문가','기관','달력','DNA','보안','클라우드','계약'] as $q) { $r = $svc->list('icon', $q, 1, 3); $samples[$q] = ['total' => (int) ($r['total'] ?? 0), 'top' => array_map(fn($a) => $a['id'], $r['data'] ?? [])]; }
echo json_encode(['pairs' => count($rows), 'resolved' => $ok, 'icon_density' => $dens, 'samples' => $samples, 'still_sample' => array_slice($still, 0, 40)], JSON_UNESCAPED_UNICODE);
