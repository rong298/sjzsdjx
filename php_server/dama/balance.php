<?php
ini_set("error_reprorting", "E_ALL");
ini_set("display_errors", "Off");
ini_set("log_errors", "On");
ini_set("error_log", "/tmp/error_log.log");


require 'dama2Lib/Dama2CurlApi.php';
$dama_api = new Dama2Api('yunhu001', 'yur140608');



var_dump(11124);
$result = $dama_api->get_balance();
var_dump(11123);
echo json_encode($result);

?>
