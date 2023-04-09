<?php

require('/var/mqtt/vendor/autoload.php');
require __DIR__ . '/sendMail.php';

use \PhpMqtt\Client\MqttClient;
use \PhpMqtt\Client\ConnectionSettings;

$server = getenv('MQTT_SERVER', true) ?: getenv('MQTT_SERVER');
$port = getenv('MQTT_PORT', true) ?: getenv('MQTT_PORT');
$clientId = getenv('MQTT_CLIENT_ID', true) ?: getenv('MQTT_CLIENT_ID');
$notifyEmail = getenv('NOTIFICATION_E_MAIL', true) ?: getenv('NOTIFICATION_E_MAIL');

$powerUpNotifi = getenv('MQTT_POWERUP_NOTIFICATION', true) ?: getenv('MQTT_POWERUP_NOTIFICATION');
$disconnectNotifi = getenv('MQTT_DISCONNECT_NOTIFICATION', true) ?: getenv('MQTT_DISCONNECT_NOTIFICATION');
$reconnectNotifi = getenv('MQTT_RECONNECT_NOTIFICATION', true) ?: getenv('MQTT_RECONNECT_NOTIFICATION');
$aliveNotifi = getenv('MQTT_ALIVE_NOTIFICATION', true) ?: getenv('MQTT_ALIVE_NOTIFICATION');


//Connecting to Redis
echo "mqtt_subscribe connecting to r Redis...\n";
$redis = new Redis(['host' => 'redis-db']);

function setKeyValue( $fTopic, $fValue) {
    $fRedis = $GLOBALS['redis'];
    $fKey = str_replace("/",":", $fTopic);
    $fRedis->set($fKey, $fValue);
    if ($fRedis->get("debug")) {
        echo "\nMQTT Topic: ", $fTopic , ". ";
        echo "Redis key: ", $fKey, ". ";
        echo "Message / Value: ", $fValue, ". Redis var_dump: ";
        var_dump($fRedis->get($fKey));
    }
}

function mosquittoTest( $topic, $message) {
    $fRedis = $GLOBALS['redis'];
    $logFile = fopen("/var/log/mqttlog", "a");
    $logText = 'MQTT Topic: ' . $topic . ' - Message: ' . $message . "\n";
    fwrite( $logFile, $logText);
    fclose($logFile);
    if ($fRedis->get("debug")) {
        echo "MQTT Topic: ", $topic , " written to file /var/log/mqttlog. ";
        echo "Message: ", $message, "\n";
    }

}

function notifyStatus( $topic, $message) {
    $fRedis = $GLOBALS['redis'];
    
    $debug = $fRedis->get("debug");
    if ($debug) 
        echo "mqtt_sobscribe Arduino status modtaget: ", $message;
     
        if ($message == "powerup") {
        $fRedis->set($message, "true");
    }

    if (($GLOBALS['powerUpNotifi'] and strpos( $message, 'powerup') !== false) or 
        ($GLOBALS['disconnectNotifi'] and strpos( $message, 'disconnected') !== false) or
        ($GLOBALS['reconnectNotifi'] and strpos( $message, 're-connect') !== false) or
        ($GLOBALS['aliveNotifi'] and strpos( $message, 'alive') !== false) or
        strpos( $message, 'buffer_overrun') !== false) {
            $to =  $GLOBALS['notifyEmail'];
            if (strpos( $to, '@') !== false) {
                if ($debug) 
                    echo  ". Sender mail...\n";
                
                $subject = "Energianalyse MQTT status: " . $message;
                $mailMessage = "Energianalyse: MQTT modtaget fra: " . $topic . ". Message: " . $message . "<br>If Disconnected - Arduino might need a restart.";
                $success = sendMail($to, $subject, $mailMessage);
                if (!$success) {
                    $errorMessage = error_get_last()['message'];
                    echo $errorMessage , "\n";
                }
            } else {
                if ($debug) 
                    echo ". No in incorrect e-mail address provided: " . $to . ".\n";
            }
        
        } else {
            if ($debug) 
                echo ".\n";

        }
}

if ($redis->get("debug")) {
    echo "\nDebug enabled!\n";
}

echo "mqtt_subscribe connection to MQTT broker at: " . $server . ". Port: " . $port . ". As:" . $clientId . "\n";
echo "mqtt_subscribe ";
if ($powerUpNotifi) 
    echo "Power UP, ";
if ($disconnectNotifi)
    echo "Disconnect, ";
if ($reconnectNotifi )
    echo "Re-connect, ";
if ($aliveNotifi)
    echo "Alive, ";

echo "e-mail notifications will be send to: " . $notifyEmail . "\n";

$mqtt = new \PhpMqtt\Client\MqttClient($server, $port, $clientId);

$mqtt->connect();

$sTopic = 'arduino/status';
$mqtt->subscribe($sTopic, function ($topic, $message, $retained, $matchedWildcards) {
    notifyStatus( $topic, $message);
}, 0);

$sTopic = 'mosquitto/test';
$mqtt->subscribe($sTopic, function ($topic, $message, $retained, $matchedWildcards) {
    mosquittoTest( $topic, $message);
}, 0);

$sTopic = 'channel/+/timestamp';
$mqtt->subscribe($sTopic, function ($topic, $message, $retained, $matchedWildcards) {
    setKeyValue( $topic, $message);
}, 0);

$mqtt->loop(true);
$mqtt->disconnect();
?>