<?php
declare(strict_types=1);

/** 이미지 썸네일 생성 (GD). 원본 비율 유지, 최대 변(max) 기준 축소. PNG는 투명 유지. */
final class Thumb
{
    /** $src 절대경로 → $dst 절대경로로 썸네일 저장. 성공 시 true. */
    public static function make(string $src, string $dst, int $max = 360): bool
    {
        if (!function_exists('imagecreatetruecolor')) {
            return false; // GD 없음
        }
        $info = @getimagesize($src);
        if ($info === false) {
            return false;
        }
        [$w, $h] = $info;
        $type = $info[2];
        if ($w <= 0 || $h <= 0) {
            return false;
        }

        $dir = dirname($dst);
        if (!is_dir($dir) && !@mkdir($dir, 0775, true) && !is_dir($dir)) {
            return false;
        }

        // 원본이 이미 충분히 작으면 그대로 복사
        if (max($w, $h) <= $max) {
            return @copy($src, $dst);
        }

        $scale = $max / max($w, $h);
        $nw = max(1, (int) round($w * $scale));
        $nh = max(1, (int) round($h * $scale));

        switch ($type) {
            case IMAGETYPE_JPEG: $img = @imagecreatefromjpeg($src); break;
            case IMAGETYPE_PNG:  $img = @imagecreatefrompng($src);  break;
            case IMAGETYPE_GIF:  $img = @imagecreatefromgif($src);  break;
            default: return false;
        }
        if (!$img) {
            return false;
        }

        $out = imagecreatetruecolor($nw, $nh);
        if ($type === IMAGETYPE_PNG || $type === IMAGETYPE_GIF) {
            imagealphablending($out, false);
            imagesavealpha($out, true);
            $transparent = imagecolorallocatealpha($out, 0, 0, 0, 127);
            imagefilledrectangle($out, 0, 0, $nw, $nh, $transparent);
        }
        imagecopyresampled($out, $img, 0, 0, 0, 0, $nw, $nh, $w, $h);

        if ($type === IMAGETYPE_PNG) {
            $ok = imagepng($out, $dst, 6);
        } elseif ($type === IMAGETYPE_GIF) {
            $ok = imagegif($out, $dst);
        } else {
            $ok = imagejpeg($out, $dst, 82);
        }
        imagedestroy($img);
        imagedestroy($out);
        return (bool) $ok;
    }

    /** image_path(uploads/cat/id.ext) → thumb 상대경로(uploads/cat/thumbs/id.ext) */
    public static function pathFor(string $imagePath): string
    {
        $dir = dirname($imagePath);
        $file = basename($imagePath);
        return $dir . '/thumbs/' . $file;
    }
}
