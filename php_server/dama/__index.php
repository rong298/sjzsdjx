<?php
header('Content-Type: text/html; charset=utf-8');
// require('dama2Lib/Dama2Api.php');
require 'dama2Lib/Dama2CurlApi.php';

//构造函数传递用户名和密码
$testApi = new Dama2Api('xxxxxxxx', 'test');
?>
<!DOCTYPE html>

<html>
    <head>
        <title>打码兔 Web Api</title>
        <meta charset='utf-8'>
    </head>
    <style type="text/css">
    .content{
        border:1px solid #aeaeae; 
        /*position: absolute;*/
        margin: 10px auto;
        padding: 10px;
        border-radius: 5px 5px 5px 5px;
        width: 750px;
        background-color: #f8f8f8;
        background-image: -webkit-gradient(linear, left 0%, left 100%, from(#fefefe), to(#f1f1f1));
        background-image: -webkit-linear-gradient(top, #fefefe, 0%, #f1f1f1, 100%);
        background-image: -moz-linear-gradient(top, #fefefe 0%, #f1f1f1 100%);
        background-image: linear-gradient(to bottom, #fefefe 0%, #f1f1f1 100%);
        background-repeat: repeat-x;
        filter: progid:DXImageTransform.Microsoft.gradient(startColorstr='#fefefe', endColorstr='#f1f1f1', GradientType=0);
    }
    </style>
    <body>
        <div class='content'>

            <h3>读取用户信息 (方法: read_info)</h3>
            <p>参数: 无</p>
            <p>调用方式:<br>
                $testApi = new Dama2Api('用户名', '密码');<br>
                $info = $testApi->read_info();
            </p>
            <em>返回结果</em>
            <p>
                <?php 
                $read_info = $testApi->read_info();
                if(isset($read_info['ret']) && $read_info['ret'] === '0'){
                    echo 'qq: ' . $read_info['qq'] . '<br>';
                    echo 'email: ' . $read_info['email'] . '<br>';
                    echo 'tel: ' . $read_info['tel'] . '<br>';
                }
                echo '<br>';
                echo '<pre>';
                var_dump($read_info);
                echo '</pre>';
                ?>
            </p>



            <h3>获取用户余额 (方法: get_balance)</h3>
            <p>参数: 无</p>
            <p>调用方式:<br>
                $testApi = new Dama2Api('用户名', '密码');<br>
                $balance = $testApi->get_balance();
            </p>
            <em>返回结果</em>
            <p>
                <?php 
                $balance = $testApi->get_balance();
                if(isset($balance['ret']) && $balance['ret'] === '0'){
                    echo '余额: ' . $balance['balance'];
                }
                echo '<br>';
                echo '<pre>';
                var_dump($balance);
                echo '</pre>';
                ?>
            </p>


            <h3>注册用户 (方法: register)</h3>
            <p>参数: (username, password, email, qq[可选], tel[可选])</p>
            <p>调用方式:<br>
                $register = Dama2Api::register('用户名', '密码', '邮箱', 'qq', '电话');
            </p>
            <em>返回结果</em>
            <p>
                <?php
                $register = Dama2Api::register('xxxxxxxx', 'test', '5823@111.com', '1234456', '1233111313');

                echo '<pre>';
                var_dump($register);
                echo '</pre>';
                ?>
            </p>

            <h3>POST文件打码</h3>
            <p>参数: (file, type, len[可选], timeout[超时])</p>
            <p>调用方式:<br>
                $testApi = new Dama2Api('用户名', '密码');<br>
                $decode = $testApi->decode('文件路径', '验证码类型', '验证码长度', '超时时间');
            </p>
            <em>返回结果</em>
            <p>
                <?php
                $decode = $testApi->decode('zw.JPG', '71');
                echo '<pre>';
                var_dump($decode);
                echo '</pre>';
                if(isset($decode['ret']) && $decode['ret'] === '0'){
                    $id = $decode['id'];
                }else{  
                    $id = '13414896541';
                }


                ?>
            </p>


            <h3>URL 打码</h3>
            <p>参数: (url, type, cookie[可选], $referer[可选],  len[可选], timeout[超时])</p>
            <p>调用方式:<br>
                $testApi = new Dama2Api('用户名', '密码');<br>
                $decode_url = $testApi->decode_url('验证码url', '验证码类型', 'cookie', 'referer', '验证码长度', '超时时间');
            </p>
            <em>返回结果</em>
            <p>
                <?php
                // $decode_url = $testApi->decode_url('http://www.dama2.com/Index/imgVerify?', '42');

                // echo '<pre>';
                // var_dump($decode_url);
                // echo '</pre>';
                
                ?>
            </p>

            <h3>获取打码结果</h3>
            <p>参数: (id)</p>
            <p>调用方式:<br>
                $testApi = new Dama2Api('用户名', '密码');<br>
                $get_result = $testApi->get_result('验证码ID');<br>
                (验证码ID 由 decode 或 decode_url 打码函数成功后返回的 id 字段值)
            </p>
            <em>返回结果</em>
            <p>
                <?php
                $get_result = array('ret' => '-303');//$testApi->get_result($id);
                // 打码记录结果需要时间返回, 返回码为-303时表示验证码还在处理中, 需要轮询获取验证结果, 具体处理方式
                // 还需要依据自身情况处理, sleep 为比较不好的方式
                var_dump($id);
                while (true) {
                   if(isset($get_result['ret']) && $get_result['ret'] === '-303'){
                    sleep(9);
                    $get_result = $testApi->get_result($id);
                   }else{
                    break;
                   }
                }
                echo '<pre>';
                var_dump($get_result) ;
                echo '</pre>';
                ?>
            </p>

            <h3>报告错误</h3>
            <p>参数: (id)</p>
            <p>调用方式:<br>
                $testApi = new Dama2Api('用户名', '密码');<br>
                $report_error = $testApi->report_error('验证码ID');<br>
                (验证码ID 由 decode 或 decode_url 打码函数成功后返回的 id 字段值)<br><br>
                <span style='color:#f00'>只有在判断结果是错误的情况下才报告错误, 如果不能判断结果是否正确, 不调用此接口</span>
            </p>
            <em>返回结果</em>
            <p>
                <?php
                //如果结果错误, 结果由 get_result 函数成功后返回的 result 字段值
                //如果不能判断结果是否正确, 不调用此接口
                if('结果不正确'){//根据自己软件实现判断

                    // $report_error = $testApi->report_error($id);
                }
               
                // echo '<pre>';
                // var_dump($report_error);
                // echo '</pre>';
                ?>
            </p>

        </div>
    </body>
</html>


<?php
// $ch = curl_init();

// $path = realpath('./1.JPG');
// var_dump($path);
// $data = array(
//     'auth' => $_SESSION['_dama2_api_auth'] ,
//     'type' => 42,
//     'file' => '@' . $path
//     );
// curl_setopt($ch, CURLOPT_URL, 'http://api.dama2.com:7788'. '/app/decode');

// curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
// curl_setopt($ch, CURLOPT_POST, 1);
// curl_setopt($ch, CURLOPT_TIMEOUT, 30);    
// curl_setopt($ch, CURLOPT_BINARYTRANSFER, 1);
// curl_setopt($ch, CURLOPT_POSTFIELDS, $data);

// $data = curl_exec($ch);
// var_dump($data);




