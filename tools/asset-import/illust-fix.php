<?php
declare(strict_types=1);
// 일회용: ① 중복 105장 덮어쓰기(id·태그 유지, 썸네일·지문 재계산) ② 새 묶음별 등록시각 나누기. 실행 후 삭제.
require __DIR__ . '/src/Config.php';
$K = (string) Config::get('import_key', '');
if ($K === '' || !hash_equals($K, (string) ($_GET['key'] ?? ''))) { http_response_code(404); exit; }
header('Content-Type: text/plain; charset=utf-8');
require __DIR__ . '/src/Database.php';
require __DIR__ . '/src/AssetService.php';
require __DIR__ . '/src/Thumb.php';
$root = __DIR__ . '/';
$pdo = Database::pdo();
$step = (string) ($_GET['step'] ?? '');
$apply = ($_GET['apply'] ?? '') === '1';
$num = fn($id) => (int) substr($id, 7);

if ($step === 'rep') {
    $n = 0; $err = [];
    foreach (glob($root . '_rep/illust_*.png') as $src) {
        $id = basename($src, '.png');
        $st = $pdo->prepare('SELECT * FROM assets WHERE id=:id'); $st->execute([':id' => $id]);
        $row = $st->fetch(PDO::FETCH_ASSOC);
        if (!$row) { $err[] = "없음 $id"; continue; }
        $img = (string) $row['image_path'];
        if (!$apply) { echo "$id → $img\n"; $n++; continue; }
        if (!@copy($src, $root . $img)) { $err[] = "복사 실패 $id"; continue; }
        clearstatcache();
        $thumb = Thumb::pathFor($img);
        Thumb::make($root . $img, $root . $thumb, 360);
        AssetService::refreshStyleSig($id, $row);
        $n++;
    }
    echo "덮어쓰기 " . ($apply ? '적용' : '예정') . " $n\n"; foreach ($err as $e) echo " - $e\n";
    exit;
}
if ($step === 'group') {
    $from = (int) ($_GET['from'] ?? 0);           // 이번에 새로 들어온 첫 번호
    $cnt = array_map('intval', explode(',', (string) ($_GET['counts'] ?? '')));
    $rep = array_map('intval', explode(',', (string) ($_GET['rep'] ?? '')));  // 덮어쓴 번호들 → g1 과 같은 시각
    $rows = $pdo->query("SELECT id FROM assets WHERE category='illust'")->fetchAll(PDO::FETCH_COLUMN);
    $ids = array_values(array_filter($rows, fn($i) => $num($i) >= $from));
    usort($ids, fn($a, $b) => $num($a) <=> $num($b));
    if (count($ids) !== array_sum($cnt)) { echo "개수 불일치 " . count($ids) . " vs " . array_sum($cnt) . "\n"; exit; }
    $base = time() - 6 * 3600; $p = 0;
    $up = $pdo->prepare('UPDATE assets SET created_at=:t WHERE id=:id');
    foreach ($cnt as $g => $c) {
        $t = date('Y-m-d H:i:s', $base + $g * 2700);   // 묶음 사이 45분
        $grp = array_slice($ids, $p, $c); $p += $c;
        if ($g === 0) foreach ($rep as $r) $grp[] = 'illust_' . $r;
        echo "묶음" . ($g + 1) . " $t · " . count($grp) . "개 (" . reset($grp) . "~" . end($grp) . ")\n";
        if ($apply) foreach ($grp as $id) $up->execute([':t' => $t, ':id' => $id]);
    }
    exit;
}
if ($step === 'set') {
    $svc = new AssetService();
    foreach (explode(',', (string) ($_GET['ids'] ?? '')) as $id) {
        $s = $svc->styleSet($id);
        $items = $s['data'] ?? $s['items'] ?? $s;
        echo "$id → " . (is_array($items) ? count($items) : '?') . "\n";
    }
    exit;
}
echo "step=rep|group|set\n";
