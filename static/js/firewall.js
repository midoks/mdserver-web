setTimeout(function(){
		GetSshInfo();
	},500);
	
	setTimeout(function(){
		ShowAccept(1);
	},1000);
	
	setTimeout(function(){
		getLogs(1);
	},1500);
	
	function CloseLogs(){
		$.post('/files?action=CloseLogs','',function(rdata){
		$("#logSize").html(rdata);
		layer.msg(lan.firewall.empty,{icon:1});
	});
}
	
$(function(){
	$.post('/files?action=GetDirSize','path=/www/wwwlogs',function(rdata){
		$("#logSize").html(rdata);
	});
})

$("#firewalldType").change(function(){
	var type = $(this).val();
	var w = '120px';
	var p = lan.firewall.port;
	var t = lan.firewall.accept;
	var m = lan.firewall.port_ps;
	if(type == 'address'){
		w = '150px';
		p = lan.firewall.ip;
		t = lan.firewall.drop;
		m = lan.firewall.ip_ps;
	}
	$("#AcceptPort").css("width",w);
	$("#AcceptPort").attr('placeholder',p);
	$("#toAccept").html(t);
	$("#f-ps").html(m);
	 
});


function GetSshInfo(){
	$.post('/firewall?action=GetSshInfo','',function(rdata){
		var SSHchecked = ''
		if(rdata.status){
			SSHchecked = "<input class='btswitch btswitch-ios' id='sshswitch' type='checkbox' checked><label class='btswitch-btn' for='sshswitch' onclick='SetMstscStatus()'></label>"
		}else{
			SSHchecked = "<input class='btswitch btswitch-ios' id='sshswitch' type='checkbox'><label class='btswitch-btn' for='sshswitch' onclick='SetMstscStatus()'></label>"
			$("#mstscSubmit").attr('disabled','disabled')
			$("#mstscPort").attr('disabled','disabled')
		}
		
		$("#in_safe").html(SSHchecked)
		$("#mstscPort").val(rdata.port)
		var isPint = ""
		if(rdata.ping){
			isPing = "<input class='btswitch btswitch-ios' id='noping' type='checkbox'><label class='btswitch-btn' for='noping' onclick='ping(0)'></label>"
		}else{
			isPing = "<input class='btswitch btswitch-ios' id='noping' type='checkbox' checked><label class='btswitch-btn' for='noping' onclick='ping(1)'></label>"
		}
		
		$("#isPing").html(isPing)
		
	});
}


/**
 * 修改远程端口
 */

function mstsc(port) {
	layer.confirm(lan.firewall.ssh_port_msg, {title: lan.firewall.ssh_port_title}, function(index) {
		var data = "port=" + port;
		var loadT = layer.load({
			shade: true,
			shadeClose: false
		});
		$.post('/firewall?action=SetSshPort', data, function(ret) {
			layer.msg(ret.msg,{icon:ret.status?1:2})
			layer.close(loadT)
			GetSshInfo()
		});
	});
}
/**
 * 更改禁ping状态
 * @param {Int} state 0.禁ping 1.可ping
 */
function ping(status){
	var msg = status==0?lan.firewall.ping_msg:lan.firewall.ping_un_msg;
	layer.confirm(msg,{title:lan.firewall.ping_title,closeBtn:2,cancel:function(){
		if(status == 1){
			$("#noping").prop("checked",true);
		}
		else{
			$("#noping").prop("checked",false);
			}
		}},function(){
		layer.msg(lan.public.the,{icon:16,time:20000});
		$.post('/firewall?action=SetPing','status='+status, function(ret) {
			layer.closeAll();
			if (ret.status == true) {
				if(status == 0){
					layer.msg(lan.firewall.ping, {icon: 1});
				}
				else{
					layer.msg(lan.firewall.ping_un, {icon: 1});
				}
				setTimeout(function(){window.location.reload();},3000);
				
				
			} else {
				layer.msg(lan.firewall.ping_err, {icon: 2});
			}
		})
	},function(){
		if(status == 1){
			$("#noping").prop("checked",true);
		}
		else{
			$("#noping").prop("checked",false);
			}
		}
	)
}

	
	
/**
 * 设置远程服务状态
 * @param {Int} state 0.启用 1.关闭
 */
function SetMstscStatus(){
	status = $("#sshswitch").prop("checked")==true?1:0;
	var msg = status==1?lan.firewall.ssh_off_msg:lan.firewall.ssh_on_msg;
	layer.confirm(msg,{title:lan.public.warning,closeBtn:2,cancel:function(){
		if(status == 0){
			$("#sshswitch").prop("checked",false);
		}
		else{
			$("#sshswitch").prop("checked",true);
		}
	}},function(index){
		if(index > 0){
			layer.msg(lan.public.the,{icon:16,time:20000});
			$.post('/firewall?action=SetSshStatus','status='+status,function(rdata){
				layer.closeAll();
				layer.msg(rdata.msg,{icon:rdata.status?1:2});
				refresh();
			})
		}
	},function(){
		if(status == 0){
			$("#sshswitch").prop("checked",false);
		}
		else{
			$("#sshswitch").prop("checked",true);
		}
	})
}

/**
 * 取回数据
 * @param {Int} page  分页号
 */
function ShowAccept(page,search) {
	search = search == undefined ? '':search;
	var loadT = layer.load();
	$.post('/data?action=getData','table=firewall&tojs=ShowAccept&limit=10&p=' + page+"&search="+search, function(data) {
		layer.close(loadT);
		var Body = '';
		for (var i = 0; i < data.data.length; i++) {
			var status = '';
			switch(data.data[i].status){
				case 0:
					status = lan.firewall.status_not;
					break;
				case 1:
					status = lan.firewall.status_net;
					break;
				default:
					status = lan.firewall.status_ok;
					break;
			}
			Body += "<tr>\
						<td><em class='dlt-num'>" + data.data[i].id + "</em></td>\
						<td>" + (data.data[i].port.indexOf('.') == -1?lan.firewall.accept_port+':['+data.data[i].port+']':lan.firewall.drop_ip+':['+data.data[i].port+']') + "</td>\
						<td>" + status + "</td>\
						<td>" + data.data[i].addtime + "</td>\
						<td>" + data.data[i].ps + "</td>\
						<td class='text-right'><a href='javascript:;' class='btlink' onclick=\"DelAcceptPort(" + data.data[i].id + ",'" + data.data[i].port + "')\">"+lan.public.del+"</a></td>\
					</tr>";
		}
		$("#firewallBody").html(Body);
		$("#firewallPage").html(data.page);
	})
}

//添加放行
function AddAcceptPort(){
	var type = $("#firewalldType").val();
	var port = $("#AcceptPort").val();
	var ps = $("#Ps").val();
	var action = "AddDropAddress";
	if(type == 'port'){
		ports = port.split(':');
		for(var i=0;i<ports.length;i++){
			if(isNaN(ports[i]) || ports[i] < 1 || ports[i] > 65535 ){
				layer.msg(lan.firewall.port_err,{icon:5});
				return;
			}
		}
		action = "AddAcceptPort";
	}
	
	
	if(ps.length < 1){
		layer.msg(lan.firewall.ps_err,{icon:2});
		$("#Ps").focus();
		return;
	}
	var loadT = layer.msg(lan.public.the_add,{icon:16,time:0,shade: [0.3, '#000']})
	$.post('/firewall?action='+action,'port='+port+"&ps="+ps+'&type='+type,function(rdata){
		layer.close(loadT);
		if(rdata.status == true || rdata.status == 'true'){
			layer.msg(rdata.msg,{icon:1});
			ShowAccept(1);
			$("#AcceptPort").val('');
			$("#Ps").val('');
		}else{
			layer.msg(rdata.msg,{icon:2});
		}
		
		$("#AcceptPort").attr('value',"");
		$("#Ps").attr('value',"");
	})
	
}

//删除放行
function DelAcceptPort(id, port) {
	var action = "DelDropAddress";
	if(port.indexOf('.') == -1){
		action = "DelAcceptPort";
	}
	
	layer.confirm(lan.get('confirm_del',[port]), {title: lan.firewall.del_title,closeBtn:2}, function(index) {
		var loadT = layer.msg(lan.public.the_del,{icon:16,time:0,shade: [0.3, '#000']})
		$.post("/firewall?action="+action,"id=" + id + "&port=" + port, function(ret) {
			layer.close(loadT);
			layer.msg(ret.msg,{icon:ret.status?1:2})
			ShowAccept(1);
		});
	});
}


/**
 * 取回数据
 * @param {Int} page  分页号
 */
function getLogs(page,search) {
	search = search == undefined ? '':search;
	var loadT = layer.load();
	$.post('/data?action=getData','table=logs&tojs=getLogs&limit=10&p=' + page+"&search="+search, function(data) {
		layer.close(loadT);
		var Body = '';
		for (var i = 0; i < data.data.length; i++) {
			Body += "<tr>\
							<td><em class='dlt-num'>" + data.data[i].id + "</em></td>\
							<td>" + data.data[i].type + "</td>\
							<td>" + data.data[i].log + "</td>\
							<td>" + data.data[i].addtime + "</td>\
						</tr>";
		}
		$("#logsBody").html(Body);
		$("#logsPage").html(data.page);
	})
}

//清理面板日志
function delLogs(){
	layer.confirm(lan.firewall.close_log_msg,{title:lan.firewall.close_log,closeBtn:2},function(){
		var loadT = layer.msg(lan.firewall.close_the,{icon:16});
		$.post('/ajax?action=delClose','',function(rdata){
			layer.close(loadT);
			layer.msg(rdata.msg,{icon:rdata.status?1:2});
			getLogs(1);
		});
	});
}