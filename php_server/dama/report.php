<?php
ini_set("error_reprorting", "E_ALL");
ini_set("display_errors", "Off");
ini_set("log_errors", "On");
ini_set("error_log", "/tmp/error_log.log"); 

$suffix = date("Y-m-d");
$log_file = "/var/log/php-fpm/php_dama_report_".$suffix.".log";

$finger = $_POST['id'];
$username = $_POST['username'];
$password = $_POST['password'];
$app_key = $_POST['app_key'];
$app_id = $_POST['app_id'];
$redis_ip = '121.42.139.97';
$redis_port = 6379;
$redis_auth = 'toptrain';

error_log(date("[Y-m-d H:i:s]")." -[".$_SERVER['REQUEST_URI']."] : GET PARAMS: ".json_encode($_POST)."\n", 3, $log_file);

require 'dama2Lib/Dama2CurlApi.php';
$dama_api = new Dama2Api($username, $password, $app_key, $app_id, $redis_ip, $redis_port, $redis_auth);

$result = $dama_api->report_error($finger);
error_log(date("[Y-m-d H:i:s]")." -[".$_SERVER['REQUEST_URI']."] : REPORT PARAMS: ".json_encode($result)."\n", 3, $log_file);
echo json_encode($result);
?>
