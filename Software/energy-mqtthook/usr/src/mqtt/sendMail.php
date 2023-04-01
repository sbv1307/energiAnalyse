<?php
//Import PHPMailer classes into the global namespace
//These must be at the top of your script, not inside a function
use PHPMailer\PHPMailer\PHPMailer;
use PHPMailer\PHPMailer\SMTP;
use PHPMailer\PHPMailer\Exception;

//Load Composer's autoloader
require '/var/PHPMailer/vendor/autoload.php';

function sendMail($to, $subject, $message) {
    $returnValue = false;
    if ( $to == "" )  {
        $to = 'pist@eltt.dk';
    }
    if ( $subject == "") {
        $subject = 'No subject provided.';
    }
    if ( $message == "") {
        $message = "No message provided";
    }
    $mail_SMTP_host = getenv('MAIL_SMTP_HOST', true) ?: getenv('MAIL_SMTP_HOST');
    $mail_SMTP_username = getenv('MAIL_SMTP_USERNAME', true) ?: getenv('MAIL_SMTP_USERNAME');
    $mail_SMTP_password = getenv('MAIL_SMTP_PASSWORD', true) ?: getenv('MAIL_SMTP_PASSWORD');

        //Create an instance; passing `true` enables exceptions
    $mail = new PHPMailer(true);

    try {
        //Server settings
        $fRedis = $GLOBALS['redis'];
        if ($fRedis->get("debug")) {
            $mail->SMTPDebug = SMTP::DEBUG_SERVER;                  //Enable verbose debug output
            $debug = true;
        } else {
            $mail->SMTPDebug = SMTP::DEBUG_OFF;                      //No  debug output
            $debug = false;
        }
        $mail->isSMTP();                                            //Send using SMTP
        $mail->Host       = $mail_SMTP_host;                        //Set the SMTP server to send through
        $mail->SMTPAuth   = true;                                   //Enable SMTP authentication
        $mail->Username   = $mail_SMTP_username;                    //SMTP username
        $mail->Password   = $mail_SMTP_password;                    //SMTP password
        $mail->SMTPSecure = PHPMailer::ENCRYPTION_SMTPS;            //Enable implicit TLS encryption
        $mail->Port       = 465;                                    //TCP port to connect to; use 587 if you have set `SMTPSecure = PHPMailer::ENCRYPTION_STARTTLS`

        //Recipients
        $mail->setFrom('pist82774@gmail.com', 'Mailer');
        $mail->addAddress($to);                      //Name is optional
        $mail->addReplyTo('no-reply@example.com', 'No-reply');

        //Content
        $mail->isHTML(true);                                  //Set email format to HTML
        $mail->Subject = $subject;
        $mail->Body    = $message;
        
        $mail->send();
        $returnValue = true;
        if ($debug)
            echo "Message has been sent \n";
    } catch (Exception $e) {
        echo "Message could not be sent. Mailer Error: {$mail->ErrorInfo} \n";
    }
    return $returnValue;   
}


