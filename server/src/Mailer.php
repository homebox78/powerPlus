<?php
declare(strict_types=1);

require_once __DIR__ . '/Config.php';

/** 단순 메일 발송 (PHP mail()). 공유호스팅용 MVP — 필요 시 SMTP로 교체. */
final class Mailer
{
    public static function send(string $to, string $subject, string $body): bool
    {
        $from = (string) Config::get('mail_from', 'noreply@localhost');
        $name = (string) Config::get('mail_from_name', 'powerPlus');

        $headers = implode("\r\n", [
            'MIME-Version: 1.0',
            'Content-Type: text/plain; charset=UTF-8',
            'From: ' . self::encodeWord($name) . ' <' . $from . '>',
            'Reply-To: ' . $from,
        ]);

        return @mail($to, self::encodeWord($subject), $body, $headers);
    }

    /** 한글 제목/이름을 위한 MIME 인코딩 (RFC 2047). */
    private static function encodeWord(string $text): string
    {
        return '=?UTF-8?B?' . base64_encode($text) . '?=';
    }
}
