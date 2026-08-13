<?php
declare(strict_types=1);

/**
 * 자산 이미지의 "스타일 지문".
 *
 * 세트를 등록 배치로만 묶었더니 **파란 단색 일러스트와 알록달록한 일러스트가 한 세트**로 나왔다.
 * 사용자가 말한 세트는 "같이 등록된 것"이 아니라 **색감·톤이 일관된 것**이다.
 * 그래서 썸네일 픽셀을 실제로 재서 주색상을 뽑는다.
 *
 * 실측 근거(2026-08-13, 같은 배치 175장을 눈으로 세 갈래로 나눠 놓고 지표를 대조):
 *   파랑 톤 플랫  최다색비중 0.72~0.92 · 평균채도 0.42~0.78
 *   사실적 인물   최다색비중 0.43~1.00 · 평균채도 0.32~0.47  ← 비중만 보면 파랑 톤과 겹친다
 *   컬러 장면     최다색비중 0.50~0.85 · 평균채도 0.27~0.59
 * 즉 **비중 하나로는 안 갈리고, "한 색이 지배 + 채도가 높다"는 조합**이 톤 스타일을 집어낸다.
 * (피부·머리색이 지배적인 사실적 인물은 채도가 낮아 자동으로 빠진다.)
 *
 * 지문 값: "t0".."t5"(밝은 그 색조) · "t0d".."t5d"(짙은 그 색조) · "c"(일반 컬러) · "n"(무채색)
 */
final class StyleSig
{
    /** 이미지 파일 → 지문. 못 읽으면 null(그 자산은 배치 기준만 쓴다). */
    public static function compute(string $file): ?string
    {
        if ($file === '' || !is_readable($file)) return null;
        $raw = @file_get_contents($file);
        if ($raw === false) return null;
        $im = @imagecreatefromstring($raw);
        if (!$im) return null;

        $w = imagesx($im);
        $h = imagesy($im);
        $stepX = max(1, intdiv($w, 40));
        $stepY = max(1, intdiv($h, 40));
        $hues = array_fill(0, 6, 0);   // 60° 단위 6칸 — 파랑(210°)과 시안(180°)은 한 계열로 본다
        $ink = 0;      // 배경 아닌 픽셀
        $chroma = 0;   // 그중 색을 가진 픽셀
        $satSum = 0;   // 평균 채도(톤 스타일 판정의 두 번째 축)
        $valSum = 0;   // 평균 밝기(세 번째 축 — 짙은 남색 양복 실사풍과 밝은 플랫을 가른다)

        for ($y = 0; $y < $h; $y += $stepY) {
            for ($x = 0; $x < $w; $x += $stepX) {
                $c = imagecolorat($im, $x, $y);
                if ((($c >> 24) & 0x7F) > 100) continue;                 // 투명 배경
                $R = (($c >> 16) & 0xFF) / 255;
                $G = (($c >> 8) & 0xFF) / 255;
                $B = ($c & 0xFF) / 255;
                $mx = max($R, $G, $B);
                $mn = min($R, $G, $B);
                $d  = $mx - $mn;
                if ($mx > 0.96 && $d < 0.06) continue;                    // 흰 배경
                $ink++;
                $valSum += $mx;
                $s = $mx > 0 ? $d / $mx : 0;
                $satSum += $s;
                if ($s < 0.18) continue;                                  // 무채색은 색상 집계 제외
                $chroma++;
                $deg = $mx === $R ? 60 * fmod(($G - $B) / $d, 6)
                     : ($mx === $G ? 60 * ((($B - $R) / $d) + 2)
                                   : 60 * ((($R - $G) / $d) + 4));
                if ($deg < 0) $deg += 360;
                $hues[(int) floor($deg / 60) % 6]++;
            }
        }
        imagedestroy($im);

        if ($ink < 30) return null;                                        // 표본이 너무 적다
        if ($chroma / $ink < 0.20) return 'n';                             // 거의 무채색(흑백 아이콘 등)

        $tot = array_sum($hues) ?: 1;
        $top = 0;
        foreach ($hues as $i => $n) if ($n > $hues[$top]) $top = $i;
        $dominance = $hues[$top] / $tot;    // 한 색조가 얼마나 지배하는가
        $avgSat = $satSum / $ink;           // 전체적으로 얼마나 쨍한가
        $avgVal = $valSum / $ink;           // 밝은 톤인가 짙은 톤인가

        // 한 색조가 지배하면서 채도까지 높아야 "그 색으로 통일된 스타일"이다.
        // 채도 기준이 없으면 피부·머리색이 지배적인 사실적 인물까지 톤 스타일로 잡힌다(실측).
        if ($dominance < 0.70 || $avgSat < 0.40) return 'c';

        // ⭐ 같은 파랑이어도 **짙은 남색 양복 실사풍**과 **밝은 플랫 일러스트**는 다른 스타일이다.
        //    (사용자 지적) 실측하니 양복 실사풍은 평균 밝기 0.33~0.50, 밝은 플랫은 0.56 이상으로 딱 갈렸다.
        return 't' . $top . ($avgVal < 0.55 ? 'd' : '');
    }

    /** 자산 행(image_path·thumb_path)에서 파일 경로를 골라 지문을 만든다. */
    public static function forRow(array $row, string $root): ?string
    {
        $rel = (string) ($row['thumb_path'] ?? '') ?: (string) ($row['image_path'] ?? '');
        if ($rel === '') return null;
        return self::compute(rtrim($root, '/\\') . '/' . ltrim($rel, '/'));
    }
}
