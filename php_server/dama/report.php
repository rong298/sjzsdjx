<?php
ini_set("error_reprorting", "E_ALL");
ini_set("display_errors", "Off");
ini_set("log_errors", "On");
ini_set("error_log", "/tmp/error_log.log"); 

$suffix = date("Y-m-d");
$log_file = "/var/log/php-fpm/php_dama_report_".$suffix.".log";

$finger = $_POST['id'];
error_log(date("[Y-m-d H:i:s]")." -[".$_SERVER['REQUEST_URI']."] : GET PARAMS: ".json_encode($_POST)."\n", 3, $log_file);

require 'dama2Lib/Dama2CurlApi.php';
$dama_api = new Dama2Api('yunhu001', 'yur140608');

$result = $dama_api->report_error($finger);
error_log(date("[Y-m-d H:i:s]")." -[".$_SERVER['REQUEST_URI']."] : REPORT PARAMS: ".json_encode($result)."\n", 3, $log_file);
echo json_encode($result);
?>
