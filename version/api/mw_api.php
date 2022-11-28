<?php
/**
 * MW API接口示例Demo
 * 仅供参考，请根据实际项目需求开发，并做好安全处理
 * date 2022-11-28
 * author midoks
 */
class mwApi {
    private $MW_KEY   = "j7GQhzNcBV4KU9QKYPXvtjSzCcmfkc0e"; //接口密钥
    private $MW_PANEL = "http://127.0.0.1:7200"; //面板地址

    //如果希望多台面板，可以在实例化对象时，将面板地址与密钥传入
    public function __construct($mw_panel = null, $mw_key = null) {
        if ($mw_panel) {
            $this->MW_PANEL = $mw_panel;
        }

        if ($mw_key) {
            $this->MW_KEY = $mw_key;
        }
    }

    /**
     * 发起POST请求
     * @param String $url 目标网填，带http://
     * @param Array|String $data 欲提交的数据
     * @return string
     */
    private function httpPostCookie($url, $data, $timeout = 60) {
        //定义cookie保存位置
        $cookie_file = './' . md5($this->MW_PANEL) . '.cookie';
        if (!file_exists($cookie_file)) {
            $fp = fopen($cookie_file, 'w+');
            fclose($fp);
        }

        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_TIMEOUT, $timeout);
        curl_setopt($ch, CURLOPT_POST, 1);
        curl_setopt($ch, CURLOPT_POSTFIELDS, $data);
        curl_setopt($ch, CURLOPT_COOKIEJAR, $cookie_file);
        curl_setopt($ch, CURLOPT_COOKIEFILE, $cookie_file);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
        curl_setopt($ch, CURLOPT_HEADER, 0);
        curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, false);
        curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
        $output = curl_exec($ch);
        curl_close($ch);
        return $output;
    }

    /**
     * 构造带有签名的关联数组
     */
    private function getKeyData() {
        $now_time   = time();
        $ready_data = array(
            'request_token' => md5($now_time . '' . md5($this->MW_KEY)),
            'request_time'  => $now_time,
        );
        return $ready_data;
    }

    //示例取面板日志
    public function getLogsList() {
        //拼接URL地址
        $url = $this->MW_PANEL . '/api/firewall/get_log_list';

        //准备POST数据
        $post_data          = $this->getKeyData(); //取签名
        $post_data['p']     = '1';
        $post_data['limit'] = 10;

        //请求面板接口
        $result = $this->httpPostCookie($url, $post_data);

        //解析JSON数据
        $data = json_decode($result, true);
        return $data;
    }

}

//实例化对象
$api = new mwApi();
//获取面板日志
$rdata = $api->getLogsList();

// var_dump($rdata);
//输出JSON数据到浏览器
echo json_encode($rdata);

?>