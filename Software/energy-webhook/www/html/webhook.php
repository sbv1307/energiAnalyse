<?php
$debug = FALSE;
$getPostKey_UNKNOWN = TRUE;

function setKeyValue($fRedis, $fKey, $fValue) {
        if ($GLOBALS['debug']) {
                echo "<br>Nøgle: ", $fKey , "<br>";
                echo "<br>Værdi: ", $fValue, "<br>";
        }
        if ($fRedis->exists($fKey)) {
                echo "\nWEBHOOK 102 Processing\n";
        } elseif ($fRedis->set($fKey, $fValue)) {
                echo "\nWEBHOOK 200 OK\n";
        } else {
                echo "\nWEBHOOK 100 error\n";
        }
}



//Connecting to Redis
$redis = new Redis(['host' => 'redis-db']);

if (isset( $_GET["debug"] ) ) {
        $getPostKey_UNKNOWN = FALSE;
        switch ($_GET["debug"]) {
                case "true":
                        $redis->set("debug", "true");
                        echo "Enable debugging.<br>";
                        break;
                case "false":
                        $redis->set("debug", "false");
                        $redis->del("foo");
                        echo "Disable debugging.<br><br><br>";
                        break;
                default:
        }
}

if (isset( $_POST["debug"] )) {
        $getPostKey_UNKNOWN = FALSE;
        switch ($_POST["debug"]) {
                case "true":
                        $redis->set("debug", "true");
                        echo "Enable debugging.<br>";
                        break;
                case "false":
                        $redis->set("debug", "false");
                        $redis->del("foo");
                        echo "Disable debugging.<br><br><br>";
                        break;
                default:
        }
}

if ($redis->get("debug") == "true") {
        echo "Debugging Enabled!<br><br><br>";
        $debug = TRUE;
} else {
        $debug = FALSE;
}

if ($debug) {
        $key = "foo";
        $redis->set($key, "bar");
        echo "<br>Dumping var: redis->get for key: ", $key, ". Expect \"bar\"<br>";
        var_dump($redis->get($key));
        echo "<br>";
}

if ($debug) {
        echo "<br>Hello there, this is the energimaaling project <br>The follwing is data from GET request:<br>";
        var_dump($_GET);
        echo "<br><br>";
}

if (isset($_GET["channel"]) and isset($_GET["millis"] )) {
        $key = $_GET["channel"];
        $value = $_GET["millis"];
        if (strlen($key) == 1 and
        1 <= strpos(" 12345678",$key) and 
        strpos(" 12345678",$key) <= 8 and
        ctype_digit($value)) {
                $getPostKey_UNKNOWN = FALSE;
                $l_key = "channel:".$key.":timestamp";
                setKeyValue($redis, $l_key, $value);
        }
}

if (isset($_GET["channel"]) and isset($_GET["metercount"] )) {
        $key = $_GET["channel"];
        $value = $_GET["metercount"];
        if (strlen($key) == 1 and
        1 <= strpos(" 12345678",$key) and 
        strpos(" 12345678",$key) <= 8 and
        ctype_digit($value)) {
                $getPostKey_UNKNOWN = FALSE;
                $l_key = "channel:".$key.":metercount";
                setKeyValue($redis, $l_key, $value);
        }
}

if (isset($_GET["pushtogoogle"] )) {
        $value = $_GET["pushtogoogle"];
        if ($value == "true" ) {
                $getPostKey_UNKNOWN = FALSE;
                $l_key = "pushtogoogle";
                setKeyValue($redis, $l_key, $value);
        }
}

if (isset($_GET["powerup"] )) {
        $value = $_GET["powerup"];
        if ($value == "true" ) {
                $getPostKey_UNKNOWN = FALSE;
                $l_key = "powerup";
                setKeyValue($redis, $l_key, $value);
        }
}

if (isset($_GET["stop"]) ) {
        $value = $_GET["stop"];
        if ($value == "true" ) {
                $getPostKey_UNKNOWN = FALSE;
                $l_key = "stop";
                setKeyValue($redis, $l_key, $value);
        }
}
        

if ($debug) {
        echo "<br> The following is from POST request:<br>";
        var_dump($_POST);
        echo "<br><br>";
}


if (isset($_POST["channel"]) and isset($_POST["millis"] )) {
        $key = $_POST["channel"];
        $value = $_POST["millis"];
        if (strlen($key) == 1 and
        1 <= strpos(" 12345678",$key) and 
        strpos(" 12345678",$key) <= 8 and
        ctype_digit($value)) {
                $getPostKey_UNKNOWN = FALSE;
                $l_key = "channel:".$key.":timestamp";
                setKeyValue($redis, $l_key, $value);
        }
}

if (isset($_POST["channel"]) and isset($_POST["metercount"] )) {
        $key = $_POST["channel"];
        $value = $_POST["metercount"];
        if (strlen($key) == 1 and
        1 <= strpos(" 12345678",$key) and 
        strpos(" 12345678",$key) <= 8 and
        ctype_digit($value)) {
                $getPostKey_UNKNOWN = FALSE;
                $l_key = "channel:".$key.":metercount";
                setKeyValue($redis, $l_key, $value);
        }
}

if (isset($_POST["pushtogoogle"] )) {
        $value = $_POST["pushtogoogle"];
        if ($value == "true" ) {
                $getPostKey_UNKNOWN = FALSE;
                $l_key = "pushtogoogle";
                setKeyValue($redis, $l_key, $value);
        }
}
        
if (isset($_POST["powerup"] )) {
        $value = $_POST["powerup"];
        if ($value == "true" ) {
                $getPostKey_UNKNOWN = FALSE;
                $l_key = "powerup";
                setKeyValue($redis, $l_key, $value);
        }
}
        
if (isset($_POST["stop"]) ) {
        $value = $_POST["stop"];
        if ($value == "true" ) {
                $getPostKey_UNKNOWN = FALSE;
                $l_key = "stop";
                setKeyValue($redis, $l_key, $value);
        }
}
        
                

if ($getPostKey_UNKNOWN) {
        echo "\nWEBHOOK 400 Bad Request\n>";
        echo "\nCheck POST og GET keys!\n>";
}

if ($debug) {
        echo "<br>Dumping var; redis->get for key: ", $l_key, "<br>";
        var_dump($redis->get($l_key));
        echo "<br>";

}
?>