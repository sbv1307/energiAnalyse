<?php

require('vendor/autoload.php');

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

if ($redis->get("debug")) {
    echo "\nDebug enabled!\n";
}

$mqtt = new \PhpMqtt\Client\MqttClient($server, $port, $clientId);

$mqtt->connect();

$sTopic = 'channel/+/timestamp';
$mqtt->subscribe($sTopic, function ($topic, $message, $retained, $matchedWildcards) {
    setKeyValue( $topic, $message);
}, 0);

$mqtt->loop(true);
$mqtt->disconnect();
?>