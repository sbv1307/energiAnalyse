<?php

require('/var/mqtt/vendor/autoload.php');
require __DIR__ . '/sendMail.php';

use \PhpMqtt\Client\MqttClient;
use \PhpMqtt\Client\ConnectionSettings;

$server   = 'mosquitto-mqtt';
$port     = 1883;
$clientId = 'webhook-subscriber';

//Connecting to Redis
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
    if ($fRedis->get("debug")) 
        echo "arduino status modtaget: ", $message , ". Sender mail...\n";
    $to = "pist@eltt.dk";
    $subject = "Energianalyse MQTT status: " . $message;
    $mailMessage = "Energianalyse: MQTT modtaget fra: " . $topic . ". Message: " . $message . "<br>If Disconnected - Arduino might need a restart.";
    $success = sendMail($to, $subject, $mailMessage);
    if (!$success) {
        $errorMessage = error_get_last()['message'];
        echo $errorMessage , "\n";
    }
}

if ($redis->get("debug")) {
    echo "\nDebug enabled!\n";
}

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