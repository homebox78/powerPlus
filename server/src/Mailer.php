<?php
declare(strict_types=1);

require_once __DIR__ . '/Config.php';
require_once __DIR__ . '/../lib/PHPMailer/Exception.php';
require_once __DIR__ . '/../lib/PHPMailer/PHPMailer.php';
require_once __DIR__ . '/../lib/PHPMailer/SMTP.php';

use PHPMailer\PHPMailer\PHPMailer;
use PHPMailer\PHPMailer\Exception as PHPMailerException;

/**
 * 메일 발송. smtp_host 설정이 있으면 SMTP(PHPMailer), 없으면 PHP mail() 폴백.
 * 공유호스팅은 mail()이 막힌 경우가 많아 SMTP 가 기본 경로.
 */
final class Mailer
{
    public static function send(string $to, string $subject, string $body): bool
    {
        $from = (string) Config::get('mail_from', 'noreply@localhost');
        $name = (string) Config::get('mail_from_name', 'powerPlus');

        if ((string) Config::get('smtp_host', '') !== '') {
            return self::sendSmtp($to, $subject, $body, $from, $name);
        }

        // 폴백: PHP mail()
        $headers = implode("\r\n", [
            'MIME-Version: 1.0',
            'Content-Type: text/plain; charset=UTF-8',
            'From: ' . self::encodeWord($name) . ' <' . $from . '>',
            'Reply-To: ' . $from,
        ]);
        return @mail($to, self::encodeWord($subject), $body, $headers, '-f' . $from);
    }

    private static function sendSmtp(string $to, string $subject, string $body, string $from, string $name): bool
    {
        $mail = new PHPMailer(true);
        try {
            $mail->isSMTP();
            $mail->Host       = (string) Config::get('smtp_host', '');
            $mail->Port       = (int) Config::get('smtp_port', 587);
            $mail->SMTPAuth   = true;
            $mail->Username   = (string) Config::get('smtp_user', '');
            $mail->Password   = (string) Config::get('smtp_pass', '');
            $mail->CharSet    = 'UTF-8';

            // 'ssl'(465) 또는 'tls'(587, STARTTLS)
            $secure = (string) Config::get('smtp_secure', 'tls');
            if ($secure === 'ssl') {
                $mail->SMTPSecure = PHPMailer::ENCRYPTION_SMTPS;
            } elseif ($secure === 'tls') {
                $mail->SMTPSecure = PHPMailer::ENCRYPTION_STARTTLS;
            }

            $mail->setFrom($from, $name);
            $mail->addAddress($to);
            $mail->Subject = $subject;
            $mail->Body    = $body;

            return $mail->send();
        } catch (PHPMailerException $e) {
            // 발송 실패 원인은 로그로 (운영에서 디버깅용)
            @file_put_contents(
                __DIR__ . '/../logs/mail-error.log',
                date('c') . ' ' . $mail->ErrorInfo . "\n",
                FILE_APPEND
            );
            return false;
        }
    }

    /** 한글 제목/이름을 위한 MIME 인코딩 (RFC 2047). mail() 폴백 경로에서만 사용. */
    private static function encodeWord(string $text): string
    {
        return '=?UTF-8?B?' . base64_encode($text) . '?=';
    }
}
