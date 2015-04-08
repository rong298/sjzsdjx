<?php
ini_set("error_reprorting", "E_ALL");
ini_set("display_errors", "Off");
ini_set("log_errors", "On");
ini_set("error_log", "/tmp/error_log.log");

$username = $_POST['username'];
$password = $_POST['password'];
$app_key = $_POST['app_key'];
$app_id = $_POST['app_id'];
$redis_ip = '121.42.139.97';
$redis_port = 6379;
$redis_auth = 'toptrain';

require 'dama2Lib/Dama2CurlApi.php';
$dama_api = new Dama2Api($username, $password, $app_key, $app_id, $redis_ip, $redis_port, $redis_auth);

$result = $dama_api->get_balance();
echo json_encode($result);
?>
