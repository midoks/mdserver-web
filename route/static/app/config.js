
// $.post('/config/get','',function(rdata){
// 	console.log(rdata);
// },'json');


$(".set-submit").click(function(){
	var data = $("#set_config").serialize();
	layer.msg('正在保存配置...',{icon:16,time:0,shade: [0.3, '#000']});
	$.post('/config/set',data,function(rdata){
		layer.closeAll();
		layer.msg(rdata.msg,{icon:rdata.status?1:2});
		if(rdata.status){
			setTimeout(function(){
				window.location.href = ((window.location.protocol.indexOf('https') != -1)?'https://':'http://') + rdata.data.host + window.location.pathname;
			},2500);
		}
	},'json');
});


//关闭面板
function closePanel(){
	layer.confirm('关闭面板会导致您无法访问面板 ,您真的要关闭Linux面板吗？',{title:'关闭面板',closeBtn:2,icon:13,cancel:function(){
		$("#closePl").prop("checked",false);
	}}, function() {
		$.post('/config/close_panel','',function(rdata){
			layer.msg(rdata.msg,{icon:rdata.status?1:2});
			setTimeout(function(){
				window.location.reload();
			},1000);
		},'json');
	},function(){
		$("#closePl").prop("checked",false);
	});
}

//开发模式
function debugMode(){
	var loadT = layer.msg('正在发送请求,请稍候...', { icon: 16, time: 0, shade: [0.3, '#000'] });
    $.post('/config/open_debug', {}, function (rdata) {
        layer.close(loadT);
        showMsg(rdata.msg, function(){
			window.location.reload();
		} ,{icon:rdata.status?1:2}, 1000);
    },'json');
}


function modifyAuthPath() {
    var auth_path = $("#admin_path").val();
    btn = "<button type='button' class='btn btn-success btn-sm' onclick=\"bindBTName(1,'b')\">确定</button>";
    layer.open({
        type: 1,
        area: "500px",
        title: "修改安全入口",
        closeBtn: 1,
        shift: 5,
        shadeClose: false,
        content: '<div class="bt-form bt-form pd20 pb70">\
                    <div class="line ">\
                        <span class="tname">入口地址</span>\
                        <div class="info-r">\
                            <input name="auth_path_set" class="bt-input-text mr5" type="text" style="width: 311px" value="'+ auth_path+'">\
                        </div></div>\
                        <div class="bt-form-submit-btn">\
                            <button type="button" class= "btn btn-sm btn-danger" onclick="layer.closeAll()"> 关闭</button>\
                            <button type="button" class="btn btn-sm btn-success" onclick="setAuthPath();">提交</button>\
                    </div></div>'
    });
}

function setAuthPath() {
    var auth_path = $("input[name='auth_path_set']").val();
    var loadT = layer.msg(lan.config.config_save, { icon: 16, time: 0, shade: [0.3, '#000'] });
    $.post('/config/set_admin_path', { admin_path: auth_path }, function (rdata) {
        layer.close(loadT);
        if (rdata.status) {
            layer.closeAll();
            $("#admin_path").val(auth_path);
        }
        setTimeout(function () { layer.msg(rdata.msg, { icon: rdata.status ? 1 : 2 }); }, 200);
    },'json');
}

function setPassword(a) {
	if(a == 1) {
		p1 = $("#p1").val();
		p2 = $("#p2").val();
		if(p1 == "" || p1.length < 8) {
			layer.msg('面板密码不能少于8位!', {icon: 2});
			return
		}
		
		//准备弱口令匹配元素
		var checks = ['admin888','123123123','12345678','45678910','87654321','asdfghjkl','password','qwerqwer'];
		pchecks = 'abcdefghijklmnopqrstuvwxyz1234567890';
		for(var i=0;i<pchecks.length;i++){
			checks.push(pchecks[i]+pchecks[i]+pchecks[i]+pchecks[i]+pchecks[i]+pchecks[i]+pchecks[i]+pchecks[i]);
		}
		
		//检查弱口令
		cps = p1.toLowerCase();
		var isError = "";
		for(var i=0;i<checks.length;i++){
			if(cps == checks[i]){
				isError += '['+checks[i]+'] ';
			}
		}
		
		if(isError != ""){
			layer.msg('面板密码不能为弱口令'+isError,{icon:5});
			return;
		}
			
		if(p1 != p2) {
			layer.msg('两次输入的密码不一致', {icon: 2});
			return;
		}
		$.post("/config/set_password", "password1=" + encodeURIComponent(p1) + "&password2=" + encodeURIComponent(p2), function(b) {
			if(b.status) {
				layer.closeAll();
				layer.msg(b.msg, {icon: 1});
			} else {
				layer.msg(b.msg, {icon: 2});
			}
		},'json');
		return;
	}
	layer.open({
		type: 1,
		area: "290px",
		title: '修改密码',
		closeBtn: 1,
		shift: 5,
		shadeClose: false,
		content: "<div class='bt-form pd20 pb70'>\
				<div class='line'>\
					<span class='tname'>密码</span>\
					<div class='info-r'><input class='bt-input-text' type='text' name='password1' id='p1' value='' placeholder='新的密码' style='width:100%'/></div>\
				</div>\
				<div class='line'>\
					<span class='tname'>重复</span>\
					<div class='info-r'><input class='bt-input-text' type='text' name='password2' id='p2' value='' placeholder='再输一次' style='width:100%' /></div>\
				</div>\
				<div class='bt-form-submit-btn'>\
					<span style='float: left;' title='随机密码' class='btn btn-default btn-sm' onclick='randPwd(10)'>随机</span>\
					<button type='button' class='btn btn-danger btn-sm' onclick=\"layer.closeAll()\">关闭</button>\
					<button type='button' class='btn btn-success btn-sm' onclick=\"setPassword(1)\">修改</button>\
				</div>\
			</div>"
	});
}


function randPwd(){
	var pwd = randomStrPwd(12);
	$("#p1").val(pwd);
	$("#p2").val(pwd);
	layer.msg(lan.bt.pass_rep_ps,{time:2000})
}

function setUserName(a) {
	if(a == 1) {
		p1 = $("#p1").val();
		p2 = $("#p2").val();
		if(p1 == "" || p1.length < 3) {
			layer.msg('用户名长度不能少于3位', {icon: 2});
			return;
		}
		if(p1 != p2) {
			layer.msg('两次输入的用户名不一致', {icon: 2});
			return;
		}
		$.post("/config/set_name", "name1=" + encodeURIComponent(p1) + "&name2=" + encodeURIComponent(p2), function(b) {
			if(b.status) {
				layer.closeAll();
				layer.msg(b.msg, {icon: 1});
				$("input[name='username_']").val(p1)
			} else {
				layer.msg(b.msg, {icon: 2});
			}
		},'json');
		return
	}
	layer.open({
		type: 1,
		area: "290px",
		title: '修改面板用户名',
		closeBtn: 1,
		shift: 5,
		shadeClose: false,
		content: "<div class='bt-form pd20 pb70'>\
			<div class='line'><span class='tname'>用户名</span>\
				<div class='info-r'><input class='bt-input-text' type='text' name='password1' id='p1' value='' placeholder='新的用户名' style='width:100%'/></div>\
			</div>\
			<div class='line'>\
				<span class='tname'>重复</span>\
				<div class='info-r'><input class='bt-input-text' type='text' name='password2' id='p2' value='' placeholder='再输一次' style='width:100%'/></div>\
			</div>\
			<div class='bt-form-submit-btn'>\
				<button type='button' class='btn btn-danger btn-sm' onclick=\"layer.closeAll()\">关闭</button>\
				<button type='button' class='btn btn-success btn-sm' onclick=\"setUserName(1)\">修改</button>\
			</div>\
		</div>"
	})
}


function syncDate(){
	var loadT = layer.msg('正在同步时间...',{icon:16,time:0,shade: [0.3, '#000']});
	$.post('/config/sync_date','',function(rdata){
		layer.close(loadT);
		layer.msg(rdata.msg,{icon:rdata.status?1:2});
		setTimeout(function(){window.location.reload();},1500);
	},'json');
}


function setIPv6() {
    var loadT = layer.msg('正在配置,请稍候...', { icon: 16, time: 0, shade: [0.3, '#000'] });
    $.post('/config/set_ipv6_status', {}, function (rdata) {
        layer.close(loadT);
        layer.msg(rdata.msg, {icon:rdata.status?1:2});
        setTimeout(function(){window.location.reload();},5000);
    },'json');
}


//设置面板SSL
function setPanelSSL(){
	var status = $("#sshswitch").prop("checked")==true?1:0;
	var msg = $("#panelSSL").attr('checked')?'关闭SSL后,必需使用http协议访问面板,继续吗?':'<a style="font-weight: bolder;font-size: 16px;">危险！此功能不懂别开启!</a>\
	<li style="margin-top: 12px;color:red;">必须要用到且了解此功能才决定自己是否要开启!</li>\
	<li>面板SSL是自签证书，不被浏览器信任，显示不安全是正常现象</li>\
	<li>开启后导致面板不能访问，可以点击下面链接了解解决方法</li>\
	<p style="margin-top: 10px;">\
		<input type="checkbox" id="checkSSL" /><label style="font-weight: 400;margin: 3px 5px 0px;" for="checkSSL">我已了经解详情,并愿意承担风险</label>\
		<a target="_blank" class="btlink" href="https://www.bt.cn/bbs/thread-4689-1-1.html" style="float: right;">了解详情</a>\
	</p>';
	layer.confirm(msg,{title:'设置面板SSL',closeBtn:1,icon:3,area:'550px',cancel:function(){
		if(status == 0){
			$("#panelSSL").prop("checked",false);
		}
		else{
			$("#panelSSL").prop("checked",true);
		}
	}},function(){
		if(window.location.protocol.indexOf('https') == -1){
			if(!$("#checkSSL").prop('checked')){
				layer.msg(lan.config.ssl_ps,{icon:2});
				return false;
			}
		}
		var loadT = layer.msg('正在安装并设置SSL组件,这需要几分钟时间...',{icon:16,time:0,shade: [0.3, '#000']});
		$.post('/config/set_panel_ssl','',function(rdata){
			layer.close(loadT);
			layer.msg(rdata.msg,{icon:rdata.status?1:5});
			if(rdata.status === true){
				$.post('/system/restart','',function (rdata) {
                    layer.close(loadT);
                    layer.msg(rdata.msg);
                    setTimeout(function(){
						window.location.href = ((window.location.protocol.indexOf('https') != -1)?'http://':'https://') + window.location.host + window.location.pathname;
					},3000);
                },'json');
			}
		},'json');
	},function(){
		if(status == 0){
			$("#panelSSL").prop("checked",false);
		}
		else{
			$("#panelSSL").prop("checked",true);
		}
	});
}


function getPanelSSL(){
	var loadT = layer.msg('正在获取证书信息...',{icon:16,time:0,shade: [0.3, '#000']});
	$.post('/config/get_panel_ssl',{},function(cert){
		layer.close(loadT);
		var certBody = '<div class="tab-con">\
			<div class="myKeyCon ptb15">\
				<div class="ssl-con-key pull-left mr20">密钥(KEY)<br>\
					<textarea id="key" class="bt-input-text">'+cert.privateKey+'</textarea>\
				</div>\
				<div class="ssl-con-key pull-left">证书(PEM格式)<br>\
					<textarea id="csr" class="bt-input-text">'+cert.certPem+'</textarea>\
				</div>\
				<div class="ssl-btn pull-left mtb15" style="width:100%">\
					<button class="btn btn-success btn-sm" onclick="savePanelSSL()">保存</button>\
				</div>\
			</div>\
			<ul class="help-info-text c7 pull-left">\
				<li>粘贴您的*.key以及*.pem内容，然后保存即可。</li>\
				<li>如果浏览器提示证书链不完整,请检查是否正确拼接PEM证书</li><li>PEM格式证书 = 域名证书.crt + 根证书(root_bundle).crt</li>\
			</ul>\
		</div>'
		layer.open({
			type: 1,
			area: "600px",
			title: '自定义面板证书',
			closeBtn: 1,
			shift: 5,
			shadeClose: false,
			content:certBody
		});
	},'json');
}


function savePanelSSL(){
	var data = {
		privateKey:$("#key").val(),
		certPem:$("#csr").val()
	}
	var loadT = layer.msg('正在安装并设置SSL组件,这需要几分钟时间...',{icon:16,time:0,shade: [0.3, '#000']});
	$.post('/config/save_panel_ssl',data,function(rdata){
		layer.close(loadT);
		if(rdata.status){
			layer.closeAll();
		}
		layer.msg(rdata.msg,{icon:rdata.status?1:2});
	},'json');
}

