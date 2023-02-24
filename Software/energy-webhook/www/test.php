<?php
// attempt a connection
$dbh = pg_connect("host=postgres-db dbname=energy user=energy password=energy");

if (!$dbh) {
    die("Error in connection: " . pg_last_error());
}

// execute query
$sql = "SELECT meter_no, meter_counts FROM meter_status ORDER BY meter_no";
$result = pg_query($dbh, $sql);

if (!$result) {
    die("Error in SQL query: " . pg_last_error());
} 
// else {
//    echo "Resultat af query: " . $result . "<br /";
//}

// iterate over result set
// print each row
?>
<html>
<head>
<title>Energi metre</title>
</head>
<body>

<iframe name="dummyframe" id="dummyframe" style="display: none;"></iframe>    

<h1>Tilret kWh for energimetre</h1>



<?php
$meter_metedata_sql = "SELECT meter_name FROM meter_metadata";
$meter_metedata = pg_query($dbh, $meter_metedata_sql);


while ($row = pg_fetch_array($result)) {
$meter_names = pg_fetch_array($meter_metedata);    

    
?>
<h3>  <?php echo $meter_names[0];?></h3>
<form method='post' action='./webhook.php' target="dummyframe">
    <label>Enter kWh for meter numer: </label>
    <input type='text' name='channel' value="<?php echo $row[0] ?>">
    <input type='text' name='metercount' value= "<?php echo $row[1] ?>">
    <input type='submit'>
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