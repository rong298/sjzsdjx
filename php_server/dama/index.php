<?php
ini_set("error_reprorting", "E_ALL");
ini_set("display_errors", "Off");
ini_set("log_errors", "On");
ini_set("error_log", "/tmp/error_log.log"); 

$suffix = date("Y-m-d");
$log_file = "/var/log/php-fpm/php_dama_".$suffix.".log";

$content = $_POST['content'];
$file_type = $_POST['file_type'];
#error_log(date("[Y-m-d H:i:s]")." -[".$_SERVER['REQUEST_URI']."] : GET PARAMS: ".json_encode($_POST)."\n", 3, $log_file);

require 'dama2Lib/Dama2CurlApi.php';
$dama_api = new Dama2Api('yunhu001', 'yur140608');

$fn = "/tmp/".md5($content.date("[Y-m-d H:i:s]")).'.jpg';
file_put_contents($fn, @base64_decode($content), LOCK_EX);

$info = $dama_api->decode($fn, intval($file_type));
@unlink($fn);
error_log(date("[Y-m-d H:i:s]")." -[".$_SERVER['REQUEST_URI']."] : DECODE RESULT: ".json_encode($info)."\n", 3, $log_file);
if(intval($info['ret']) != 0){
   $info['id'] = null; 
   echo json_encode($info);
   exit;
} 

/*
$result = $dama_api->get_result($info['id']);
error_log(date("[Y-m-d H:i:s]")." -[".$_SERVER['REQUEST_URI']."] : GET RESULT: ".json_encode($result)."\n", 3, $log_file);
$result['id'] = $info['id'];
echo json_encode($result);     
*/
$cnt = 0
while(1){
   $result = $dama_api->get_result($info['id']);
   error_log(date("[Y-m-d H:i:s]")." -[".$_SERVER['REQUEST_URI']."] : GET RESULT: ".json_encode($result)."\n", 3, $log_file);

   if(intval($result['ret']) == 0 || $cnt > 15){
       $result['id'] = $info['id'];
       echo json_encode($result);     
       exit;
   }
   else{
      sleep(1);
   }
   $cnt += 1
}
?>
