
function readme(){
	var con = '<ul class="help-info-text c7">';
	con += '<li>一旦安装无法退回!谨慎使用</li>';
    con += '<li>只有KVM架构的VPS才能使用</li>';
    con += '<li>安装 Google BBR 需升级系统内核，而安装锐速则需降级系统内核，<br/>故两者不能同时安装。</li>';
    con += '<li>安装 Google BBR 需升级系统内核，有可能造成系统不稳定，<br/>故不建议将其应用在重要的生产环境中</li>';
    con += '<hr/>';
    con += '<li>安装升级后,可删除无用的旧内核[谨慎操作]</li>';
    con += '<li>yum remove $(rpm -qa | grep kernel | grep -v $(uname -r))</li>';
    con += '</ul>';
    $(".soft-man-con").html(con);  
}