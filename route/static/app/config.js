
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
		closeBtn: 2,
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
		closeBtn: 2,
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
		setTimeout(function(){
			window.location.reload();
		},1500);
	},'json');
}