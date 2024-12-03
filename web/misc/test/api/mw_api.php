<?php
/**
 * MW API接口示例Demo
 * 仅供参考，请根据实际项目需求开发，并做好安全处理
 * date 2022-11-28
 * author midoks
 */
class mwApi {
	private $MW_PANEL      = "http://127.0.0.1:64307"; //面板地址
	private $MW_APP_ID     = 'hC6XArWzRY';
	private $MW_APP_SERECT = 'NSGaFhMWyaN5Yi3ftTkZ';

	//如果希望多台面板，可以在实例化对象时，将面板地址与密钥传入
	public function __construct($mw_panel = null, $app_id = null, $app_secret = null) {
		if ($mw_panel) {
			$this->MW_PANEL = $mw_panel;
		}

		if ($app_id) {
			$this->MW_APP_ID = $app_id;
		}

		if ($app_secret) {
			$this->MW_APP_SERECT = $app_secret;
		}
	}

	/**
	 * 发起POST请求
	 * @param String $url 目标网填，带http://
	 * @param Array|String $data 欲提交的数据
	 * @return string
	 */
	private function httpPost($url, $data, $timeout = 60) {

		$ch = curl_init();
		// 设置头部信息
		$headers = [
			'app-id: ' . $this->MW_APP_ID,
			'app-secret: ' . $this->MW_APP_SERECT,
		];
		curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
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

	public function panel($endpoint, $data) {
		$url = $this->MW_PANEL . $endpoint;
		return $this->httpPost($url, $data);
	}

	//示例取面板日志
	public function getLogsList() {
		$post_data['p']     = '1';
		$post_data['limit'] = 10;

		//请求面板接口
		$data = $this->panel('/logs/get_log_list', $post_data);

		//解析JSON数据
		// $data = json_decode($result, true);
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