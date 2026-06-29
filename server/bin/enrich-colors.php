<?php
declare(strict_types=1);
/**
 * 색상 자동 태깅 — 시각 자산(icon/photo/illust/diagram/logo)의 이미지에서
 * 주요 색을 추출해 색상 태그(파랑/blue 등)를 tags_ko/tags_en 에 병합한다.
 * "파란 톤 차트 아이콘" 같은 자연어 검색이 실제로 매칭되도록 데이터를 보강.
 * 보안: ?key= 필요. 멱등(다시 실행해도 중복 태그는 병합·제거됨).
 *
 * 사용: bin/ 은 .htaccess 차단 → 웹루트로 임시 업로드 후
 *       curl "https://.../enrich-colors.php?key=pp_enrich_7Yq2"
 */
if (($_GET['key'] ?? '') !== 'pp_enrich_7Yq2') { http_response_code(404); exit; }
header('Content-Type: text/plain; charset=utf-8');
require __DIR__ . '/src/Database.php';
require __DIR__ . '/src/AssetService.php';

$root = __DIR__ . '/';
$svc  = new AssetService();
$CATS = ['icon','photo','illust','diagram','logo'];
$BUCKET = [ // name => [ko, en]
 'red'=>['빨강','red'],'orange'=>['주황','orange'],'yellow'=>['노랑','yellow'],
 'green'=>['초록','green'],'teal'=>['청록','teal'],'blue'=>['파랑','blue'],
 'purple'=>['보라','purple'],'pink'=>['분홍','pink'],'brown'=>['갈색','brown'],
 'black'=>['검정','black'],'white'=>['흰색','white'],'gray'=>['회색','gray'],
];
$ALL_COLOR_KO = array_map(fn($v)=>$v[0], $BUCKET);
$ALL_COLOR_EN = array_map(fn($v)=>$v[1], $BUCKET);

function rgb2hsv(int $r,int $g,int $b): array {
    $r/=255; $g/=255; $b/=255; $mx=max($r,$g,$b); $mn=min($r,$g,$b); $d=$mx-$mn;
    $h=0.0;
    if ($d>0) {
        if ($mx==$r) $h=fmod((($g-$b)/$d),6);
        elseif ($mx==$g) $h=(($b-$r)/$d)+2;
        else $h=(($r-$g)/$d)+4;
        $h*=60; if ($h<0) $h+=360;
    }
    $s = $mx==0 ? 0 : $d/$mx;
    return [$h,$s,$mx];
}
function bucket(int $r,int $g,int $b): string {
    [$H,$S,$V]=rgb2hsv($r,$g,$b);
    if ($V<0.16) return 'black';
    if ($S<0.16) return $V>0.82 ? 'white':'gray';
    if ($S<0.28 && $V<0.55 && $H>=18 && $H<=45) return 'brown';
    if ($H<15 || $H>=345) return 'red';
    if ($H<45)  return $V<0.5 ? 'brown':'orange';
    if ($H<70)  return 'yellow';
    if ($H<160) return 'green';
    if ($H<200) return 'teal';
    if ($H<255) return 'blue';
    if ($H<295) return 'purple';
    return 'pink';
}
/** 이미지 경로 -> 상위 색 버킷명 배열(최대 2). */
function classify(string $path, array $BUCKET): array {
    $info=@getimagesize($path); if ($info===false) return [];
    $type=$info[2];
    $img = $type===IMAGETYPE_PNG ? @imagecreatefrompng($path)
         : ($type===IMAGETYPE_JPEG ? @imagecreatefromjpeg($path)
         : ($type===IMAGETYPE_GIF ? @imagecreatefromgif($path) : null));
    if (!$img) return [];
    $w=imagesx($img); $h=imagesy($img);
    $step=max(1,(int)floor(max($w,$h)/80));
    $counts=[]; $ink=0;
    for ($y=0;$y<$h;$y+=$step) for ($x=0;$x<$w;$x+=$step) {
        $c=imagecolorat($img,$x,$y);
        $a=($c>>24)&0x7F; if ($a>100) continue;            // 투명 배경
        $r=($c>>16)&0xFF; $g=($c>>8)&0xFF; $b=$c&0xFF;
        if ($r>242&&$g>242&&$b>242) continue;              // 흰 배경
        $bk=bucket($r,$g,$b); $counts[$bk]=($counts[$bk]??0)+1; $ink++;
    }
    imagedestroy($img);
    if ($ink===0) return ['white'];
    arsort($counts); $out=[];
    foreach ($counts as $name=>$c) {
        if ($c/$ink >= 0.16) $out[]=$name;
        if (count($out)>=2) break;
    }
    if (!$out) { $out=[array_key_first($counts)]; }
    return $out;
}

$done=0; $skip=0;
$rows = Database::pdo()->query(
    "SELECT id, category, image_path, thumb_path, tags_ko, tags_en
     FROM assets WHERE category IN ('".implode("','",$CATS)."')"
);
foreach ($rows as $r) {
    $rel = $r['image_path'] ?: $r['thumb_path'];
    if (!$rel) { $skip++; continue; }
    $path = $root . ltrim((string)$rel,'/');
    if (!is_file($path)) { $skip++; continue; }
    $names = classify($path, $BUCKET);
    if (!$names) { $skip++; continue; }
    $ko = json_decode((string)($r['tags_ko'] ?? '[]'), true) ?: [];
    $en = json_decode((string)($r['tags_en'] ?? '[]'), true) ?: [];
    // 기존 색상태그 제거 후 새로 병합(멱등)
    $ko = array_values(array_filter($ko, fn($t)=>!in_array($t,$GLOBALS['ALL_COLOR_KO'],true)));
    $en = array_values(array_filter($en, fn($t)=>!in_array($t,$GLOBALS['ALL_COLOR_EN'],true)));
    foreach ($names as $n) { $ko[]=$BUCKET[$n][0]; $en[]=$BUCKET[$n][1]; }
    $ko=array_values(array_unique($ko)); $en=array_values(array_unique($en));
    $svc->update($r['id'], ['tags_ko'=>$ko, 'tags_en'=>$en]);
    $done++;
    echo "  {$r['id']}: ".implode('/',array_map(fn($n)=>$BUCKET[$n][1],$names))."\n";
}
echo "\n색상 태깅 완료 — 갱신 $done · 건너뜀 $skip\n";
