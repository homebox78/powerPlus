<?php
declare(strict_types=1);

/** MySQL(PDO) 연결 싱글톤. 설정은 환경변수 우선, 없으면 config/config.php. */
final class Database
{
    private static ?PDO $pdo = null;

    public static function pdo(): PDO
    {
        if (self::$pdo === null) {
            $cfg = self::config();
            $dsn = sprintf(
                'mysql:host=%s;port=%d;dbname=%s;charset=utf8mb4',
                $cfg['host'],
                $cfg['port'],
                $cfg['db']
            );
            self::$pdo = new PDO($dsn, $cfg['user'], $cfg['pass'], [
                PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
                PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
                PDO::ATTR_EMULATE_PREPARES   => false,
            ]);
        }
        return self::$pdo;
    }

    /** @return array{host:string,port:int,db:string,user:string,pass:string} */
    private static function config(): array
    {
        $file = __DIR__ . '/../config/config.php';
        $cfg = is_file($file) ? require $file : [];
        return [
            'host' => getenv('DB_HOST') ?: ($cfg['host'] ?? '127.0.0.1'),
            'port' => (int) (getenv('DB_PORT') ?: ($cfg['port'] ?? 3306)),
            'db'   => getenv('DB_NAME') ?: ($cfg['db'] ?? 'powerplus'),
            'user' => getenv('DB_USER') ?: ($cfg['user'] ?? 'root'),
            'pass' => getenv('DB_PASS') ?: ($cfg['pass'] ?? ''),
        ];
    }
}
