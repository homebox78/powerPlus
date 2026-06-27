<?php
declare(strict_types=1);

/** 앱 설정 로더. 환경변수(대문자 키) 우선, 없으면 config/config.php. */
final class Config
{
    private static ?array $cfg = null;

    public static function get(string $key, mixed $default = null): mixed
    {
        $env = getenv(strtoupper($key));
        if ($env !== false && $env !== '') {
            return $env;
        }
        return self::all()[$key] ?? $default;
    }

    public static function bool(string $key, bool $default = false): bool
    {
        $v = self::get($key, $default);
        return $v === true || $v === 1 || $v === '1' || $v === 'true';
    }

    /** @return array<string,mixed> */
    private static function all(): array
    {
        if (self::$cfg === null) {
            $file = __DIR__ . '/../config/config.php';
            self::$cfg = is_file($file) ? (array) require $file : [];
        }
        return self::$cfg;
    }
}
