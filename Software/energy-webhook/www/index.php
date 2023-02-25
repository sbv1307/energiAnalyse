
<?php
// Safely get the value of an environment variable, ignoring whether 
// or not it was set by a SAPI or has been changed with putenv
$postgres_user = getenv('POSTGRES_USER', true) ?: getenv('POSTGRES_USER');
$postgres_password = getenv('POSTGRES_PASSWORD', true) ?: getenv('POSTGRES_PASSWORD');
$postgres_db = getenv('POSTGRES_DB', true) ?: getenv('POSTGRES_DB');
$postgres_host = getenv('POSTGRES_HOST', true) ?: getenv('POSTGRES_HOST');


// attempt a connection
$dbh = pg_connect("host=$postgres_host dbname=$postgres_db user=$postgres_user password=$postgres_password");

if (!$dbh) {
    die("Error in connection: " . pg_last_error());
}


$sql = "SELECT meter_no, meter_counts FROM meter_status ORDER BY meter_no";
$result = pg_query($dbh, $sql);

if (!$result) {
    die("Error in SQL query: " . pg_last_error());
} 

?>
<html>
<head>
<title>Update Energi meters</title>
</head>
<body>

<iframe name="dummyframe" id="dummyframe" style="display: none;"></iframe>    

<h1>Updater kWh for energimetre</h1>

<?php
$meter_metedata_sql = "SELECT meter_name FROM meter_metadata";
$meter_metedata = pg_query($dbh, $meter_metedata_sql);

while ($row = pg_fetch_array($result)) {
$meter_names = pg_fetch_array($meter_metedata);    

?>
<h3>  <?php echo $meter_names[0];?></h3>
<form method='post' action='./webhook.php' target="dummyframe">
    <label>Enter kWh for meter numer: </label>
    <input type='text' name='channel' value="<?php echo $row[0] ?>" size="1" readonly>
    <input type='number' name='metercount' value= "<?php echo $row[1] ?>" min="1" max="9999999" autofocus>
    <input type='submit' value="Opdater">
</form>

<?php

}

// free memory
pg_free_result($result);

// close connection
pg_close($dbh);

?>
<p></p>
</body>
</html>