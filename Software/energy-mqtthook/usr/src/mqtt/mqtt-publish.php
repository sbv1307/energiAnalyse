<?php

require('/var/mqtt/vendor/autoload.php');

use \PhpMqtt\Client\MqttClient;
use \PhpMqtt\Client\ConnectionSettings;


$server   = 'mosquitto-mqtt';
$port     = 1883;
$clientId = 'test-publisher';

$mqtt = new \PhpMqtt\Client\MqttClient($server, $port, $clientId);
$mqtt->connect();
$mqtt->publish('mosquittotest', 'Hello World!', 0);
$mqtt->disconnect();
?>
