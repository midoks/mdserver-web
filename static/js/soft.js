//软件管理
function phpSoftMain(name,key){
	if(!isNaN(name)){
		var nametext = "php"+name;
		name = name.replace(".","");
	}
	
	var loadT = layer.msg(lan.public.the,{icon:16,time:0,shade: [0.3, '#000']});
	$.get('/plugin?action=getPluginInfo&name=php',function(rdata){
		layer.close(loadT);
		nameA = rdata.versions[key];
		bodys = [
				'<p class="bgw pstate" data-id="0"><a href="javascript:service(\''+name+'\','+nameA.run+')">'+lan.soft.php_main1+'</a><span class="spanmove"></span></p>',
				'<p data-id="1"><a id="phpext" href="javascript:SetPHPConfig(\''+name+'\','+nameA.pathinfo+')">'+lan.soft.php_main5+'</a><span class="spanmove"></span></p>',
				'<p data-id="2"><a href="javascript:SetPHPConf(\''+name+'\')">'+lan.soft.config_edit+'</a><span class="spanmove"></span></p>',
				'<p data-id="3"><a href="javascript:phpUploadLimit(\''+name+'\','+nameA.max+')">'+lan.soft.php_main2+'</a><span class="spanmove"></span></p>',
				'<p class="phphide" data-id="4"><a href="javascript:phpTimeLimit(\''+name+'\','+nameA.maxTime+')">'+lan.soft.php_main3+'</a><span class="spanmove"></span></p>',
				'<p data-id="5"><a href="javascript:configChange(\''+name+'\')">'+lan.soft.php_main4+'</a><span class="spanmove"></span></p>',
				'<p data-id="6"><a href="javascript:disFun(\''+name+'\')">'+lan.soft.php_main6+'</a><span class="spanmove"></span></p>',
				'<p class="phphide" data-id="7"><a href="javascript:SetFpmConfig(\''+name+'\')">'+lan.soft.php_main7+'</a><span class="spanmove"></span></p>',
				'<p class="phphide" data-id="8"><a href="javascript:GetPHPStatus(\''+name+'\')">'+lan.soft.php_main8+'</a><span class="spanmove"></span></p>',
				'<p class="phphide" data-id="9"><a href="javascript:GetFpmLogs(\''+name+'\')">FPM日志</a><span class="spanmove"></span></p>',
				'<p class="phphide" data-id="10"><a href="javascript:GetFpmSlowLogs(\''+name+'\')">慢日志</a><span class="spanmove"></span></p>',
				'<p data-id="11"><a href="javascript:BtPhpinfo(\''+name+'\')">phpinfo</a><span class="spanmove"></span></p>'
		]
		
		var sdata = '';
		if(rdata.phpSort == false){
			rdata.phpSort = [0,1,2,3,4,5,6,7,8,9,10,11];
		}else{
			rdata.phpSort = rdata.phpSort.split('|');
		}
		for(var i=0;i<rdata.phpSort.length;i++){
			sdata += bodys[rdata.phpSort[i]];
		}
		
		layer.open({
			type: 1,
			area: '640px',
			title: nametext+lan.soft.admin,
			closeBtn: 2,
			shift: 0,
			content: '<div class="bt-w-main" style="width:640px;">\
				<input name="softMenuSortOrder" type="hidden" />\
				<div class="bt-w-menu soft-man-menu">\
					'+sdata+'\
				</div>\
				<div id="webEdit-con" class="bt-w-con pd15" style="height:555px;overflow:auto">\
					<div class="soft-man-con"></div>\
				</div>\
			</div>'
		});
		if(name== "52"){
			$(".phphide").hide();
		}
		
		if(rdata.versions.length < 5){
			$(".phphide").hide();
			$(".pstate").hide();
			SetPHPConfig(name,nameA.pathinfo);
			$("p[data-id='4']").addClass('bgw');
		}else{
			service(name,nameA.run);
		}
		
		$(".bt-w-menu p a").click(function(){
			var txt = $(this).text();
			$(this).parent().addClass("bgw").siblings().removeClass("bgw");
			if(txt != lan.soft.php_menu_ext) $(".soft-man-con").removeAttr("style");
		});
		$(".soft-man-menu").dragsort({dragSelector: ".spanmove", dragEnd: MenusaveOrder});
	});
}

//FPM日志
function GetFpmLogs(phpversion){
	var loadT = layer.msg(lan.public.the,{icon:16,time:0,shade: [0.3, '#000']});
	$.get('/ajax?action=GetFpmLogs&version='+phpversion,function(logs){
		layer.close(loadT);
		if(logs.status !== true){
			logs.msg = '';
		}
		if (logs.msg == '') logs.msg = '当前没有fpm日志.';
		var phpCon = '<textarea readonly="" style="margin: 0px;width: 500px;height: 520px;background-color: #333;color:#fff; padding:0 5px" id="error_log">'+logs.msg+'</textarea>';
		$(".soft-man-con").html(phpCon);
		var ob = document.getElementById('error_log');
		ob.scrollTop = ob.scrollHeight;		
	});
}

//FPM-Slow日志
function GetFpmSlowLogs(phpversion){
	var loadT = layer.msg(lan.public.the,{icon:16,time:0,shade: [0.3, '#000']});
	$.get('/ajax?action=GetFpmSlowLogs&version='+phpversion,function(logs){
		layer.close(loadT);
		if(logs.status !== true){
			logs.msg = '';
		}
		if (logs.msg == '') logs.msg = '当前没有慢日志.';
		var phpCon = '<textarea readonly="" style="margin: 0px;width: 500px;height: 520px;background-color: #333;color:#fff; padding:0 5px" id="error_log">'+logs.msg+'</textarea>';
		$(".soft-man-con").html(phpCon);
		var ob = document.getElementById('error_log');
		ob.scrollTop = ob.scrollHeight;		
	});
}


//配置修改
function SetPHPConf(version){
	var loadT = layer.msg(lan.public.the,{icon:16,time:0,shade: [0.3, '#000']});
	$.post('/config?action=GetPHPConf','version='+version,function(rdata){
		layer.close(loadT);
		var mlist = '';
		for(var i=0;i<rdata.length;i++){
			var w = '70'
			if(rdata[i].name == 'error_reporting') w = '250';
			var ibody = '<input style="width: '+w+'px;" class="bt-input-text mr5" name="'+rdata[i].name+'" value="'+rdata[i].value+'" type="text" >';
			switch(rdata[i].type){
				case 0:
					var selected_1 = (rdata[i].value == 1)?'selected':'';
					var selected_0 = (rdata[i].value == 0)?'selected':'';
					ibody = '<select class="bt-input-text mr5" name="'+rdata[i].name+'" style="width: '+w+'px;"><option value="1" '+selected_1+'>开启</option><option value="0" '+selected_0+'>关闭</option></select>'
					break;
				case 1:
					var selected_1 = (rdata[i].value == 'On')?'selected':'';
					var selected_0 = (rdata[i].value == 'Off')?'selected':'';
					ibody = '<select class="bt-input-text mr5" name="'+rdata[i].name+'" style="width: '+w+'px;"><option value="On" '+selected_1+'>开启</option><option value="Off" '+selected_0+'>关闭</option></select>'
					break;
			}
			mlist += '<p><span>'+rdata[i].name+'</span>'+ibody+', <font>'+rdata[i].ps+'</font></p>'
		}
		var phpCon = '<style>.conf_p p{margin-bottom: 2px}</style><div class="conf_p" style="margin-bottom:0">\
						'+mlist+'\
						<div style="margin-top:10px; padding-right:15px" class="text-right"><button class="btn btn-success btn-sm mr5" onclick="SetPHPConf('+version+')">'+lan.public.fresh+'</button><button class="btn btn-success btn-sm" onclick="SubmitPHPConf('+version+')">'+lan.public.save+'</button></div>\
					</div>'
		$(".soft-man-con").html(phpCon);
	});
}


//提交PHP配置
function SubmitPHPConf(version){
	var data = {
		version:version,
		display_errors:$("select[name='display_errors']").val(),
		'cgi.fix_pathinfo':$("select[name='cgi.fix_pathinfo']").val(),
		'date.timezone':$("input[name='date.timezone']").val(),
		short_open_tag:$("select[name='short_open_tag']").val(),
		asp_tags:$("select[name='asp_tags']").val()||'On',
		safe_mode:$("select[name='safe_mode']").val(),
		max_execution_time:$("input[name='max_execution_time']").val(),
		max_input_time:$("input[name='max_input_time']").val(),
		memory_limit:$("input[name='memory_limit']").val(),
		post_max_size:$("input[name='post_max_size']").val(),
		file_uploads:$("select[name='file_uploads']").val(),
		upload_max_filesize:$("input[name='upload_max_filesize']").val(),
		max_file_uploads:$("input[name='max_file_uploads']").val(),
		default_socket_timeout:$("input[name='default_socket_timeout']").val(),
		error_reporting:$("input[name='error_reporting']").val()||'On'
	}

	var loadT = layer.msg(lan.public.the,{icon:16,time:0,shade: [0.3, '#000']});
	$.post('/config?action=SetPHPConf',data,function(rdata){
		layer.close(loadT);
		layer.msg(rdata.msg,{icon:rdata.status?1:2});
	});
	
}

function MenusaveOrder() {
	var data = $(".soft-man-menu > p").map(function() { return $(this).attr("data-id"); }).get();
	var ssort = data.join("|");
	$("input[name=softMenuSortOrder]").val(ssort);
	$.post('/ajax?action=phpSort','ssort='+ssort,function(){});
};
//服务
function service(name,status){
	if(status == 'false') status = false;
	if(status == 'true') status = true;
	
	var serviceCon ='<p class="status">'+lan.soft.status+'：<span>'+(status?lan.soft.on:lan.soft.off)+'</span><span style="color: '+(status?'#20a53a;':'red;')+' margin-left: 3px;" class="glyphicon '+(status?'glyphicon glyphicon-play':'glyphicon-pause')+'"></span></p>\
					<div class="sfm-opt">\
						<button class="btn btn-default btn-sm" onclick="ServiceAdmin(\''+name+'\',\''+(status?'stop':'start')+'\')">'+(status?lan.soft.stop:lan.soft.start)+'</button>\
						<button class="btn btn-default btn-sm" onclick="ServiceAdmin(\''+name+'\',\'restart\')">'+lan.soft.restart+'</button>\
						<button class="btn btn-default btn-sm" onclick="ServiceAdmin(\''+name+'\',\'reload\')">'+lan.soft.reload+'</button>\
					</div>'; 
	$(".soft-man-con").html(serviceCon);
	var help = '<ul class="help-info-text c7 mtb15" style="padding-top:30px"><li>'+lan.soft.mysql_mem_err+'</li></ul>';
	if(name == 'mysqld'){
		$(".soft-man-con").append(help);
	}
}


//更新软件列表
function updateSoftList(){
	$.get('/plugin?action=getCloudPlugin',function(rdata){ });
}

//php上传限制
function phpUploadLimit(version,max){
	var LimitCon = '<p class="conf_p"><input class="phpUploadLimit bt-input-text mr5" type="number" value="'+max+'" name="max">MB<button class="btn btn-success btn-sm" onclick="SetPHPMaxSize(\''+version+'\')" style="margin-left:20px">'+lan.public.save+'</button></p>';
	$(".soft-man-con").html(LimitCon);
}
//php超时限制
function phpTimeLimit(version,max){
	var LimitCon = '<p class="conf_p"><input class="phpTimeLimit bt-input-text mr5" type="number" value="'+max+'">'+lan.bt.s+'<button class="btn btn-success btn-sm" onclick="SetPHPMaxTime(\''+version+'\')" style="margin-left:20px">'+lan.public.save+'</button></p>';
	$(".soft-man-con").html(LimitCon);
}
//设置超时限制
function SetPHPMaxTime(version){
	var max = $(".phpTimeLimit").val();
	var loadT = layer.msg(lan.soft.the_save,{icon:16,time:0,shade: [0.3, '#000']});
	$.post('/config?action=setPHPMaxTime','version='+version+'&time='+max,function(rdata){
		$(".bt-w-menu .active").attr('onclick',"phpTimeLimit('"+version+"',"+max+")");
		$(".bt-w-menu .active a").attr('href',"javascript:phpTimeLimit('"+version+"',"+max+");");
		layer.close(loadT);
		layer.msg(rdata.msg,{icon:rdata.status?1:2});
	});
}
//设置PHP上传限制
function SetPHPMaxSize(version){
	max = $(".phpUploadLimit").val();
	if(max < 2){
		alert(max);
		layer.msg(lan.soft.php_upload_size,{icon:2});
		return;
	}
	var loadT = layer.msg(lan.soft.the_save,{icon:16,time:0,shade: [0.3, '#000']});
	$.post('/config?action=setPHPMaxSize','&version='+version+'&max='+max,function(rdata){
		$(".bt-w-menu .active").attr('onclick',"phpUploadLimit('"+version+"',"+max+")");
		$(".bt-w-menu .active a").attr('href',"javascript:phpUploadLimit('"+version+"',"+max+");");
		layer.close(loadT);
		layer.msg(rdata.msg,{icon:rdata.status?1:2});
	})
}
//配置修改
function configChange(type){
	var con = '<p style="color: #666; margin-bottom: 7px">'+lan.bt.edit_ps+'</p><textarea class="bt-input-text" style="height: 320px; line-height:18px;" id="textBody"></textarea>\
					<button id="OnlineEditFileBtn" class="btn btn-success btn-sm" style="margin-top:10px;">'+lan.public.save+'</button>\
					<ul class="help-info-text c7 ptb15">\
						<li>'+lan.get('config_edit_ps',[type])+'</li>\
					</ul>';
	$(".soft-man-con").html(con);
	var fileName = '';
	switch(type){
		case 'mysqld':
			fileName = '/etc/my.cnf';
			break;
		case 'nginx':
			fileName = '/www/server/nginx/conf/nginx.conf';
			break;
		case 'pure-ftpd':
			fileName = '/www/server/pure-ftpd/etc/pure-ftpd.conf';
			break;
		case 'apache':
			fileName = '/www/server/apache/conf/httpd.conf';
			break;
		case 'tomcat':
			fileName = '/www/server/tomcat/conf/server.xml';
			break;
		case 'memcached':
			fileName = '/etc/init.d/memcached';
			break;
		case 'redis':
			fileName = '/www/server/redis/redis.conf';
			break;
		default:
			fileName = '/www/server/php/'+type+'/etc/php.ini';
			break;
	}
	var loadT = layer.msg(lan.soft.get,{icon:16,time:0,shade: [0.3, '#000']});
	$.post('/files?action=GetFileBody', 'path=' + fileName, function(rdata) {
		layer.close(loadT);
		$("#textBody").empty().text(rdata.data);
		$(".CodeMirror").remove();
		var editor = CodeMirror.fromTextArea(document.getElementById("textBody"), {
			extraKeys: {"Ctrl-Space": "autocomplete"},
			lineNumbers: true,
			matchBrackets:true,
		});
		editor.focus();
		$(".CodeMirror-scroll").css({"height":"300px","margin":0,"padding":0});
		$("#OnlineEditFileBtn").click(function(){
			$("#textBody").text(editor.getValue());
			confSafe(fileName);
		});
	});
}
//配置保存
function confSafe(fileName){
	var data = encodeURIComponent($("#textBody").val());
	var encoding = 'utf-8';
	var loadT = layer.msg(lan.soft.the_save, {
		icon: 16,
		time: 0
	});
	$.post('/files?action=SaveFileBody', 'data=' + data + '&path=' + fileName+'&encoding='+encoding, function(rdata) {
		layer.close(loadT);
		layer.msg(rdata.msg, {
			icon: rdata.status ? 1 : 2
		});
	});
}


//设置PATHINFO
function SetPathInfo(version,type){
	var loadT = layer.msg(lan.public.the,{icon:16,time:0,shade: [0.3, '#000']});
	$.post('/config?action=setPathInfo','version='+version+'&type='+type,function(rdata){
		var pathinfo = (type == 'on')?true:false;
		var pathinfoOpt = '<a style="color:red;" href="javascript:SetPathInfo(\''+version+'\',\'off\');">'+lan.public.off+'</a>'
		if(!pathinfo){
			pathinfoOpt = '<a class="link" href="javascript:SetPathInfo(\''+version+'\',\'on\');">'+lan.public.on+'</a>'
		}
		var pathinfo1 = '<td>PATH_INFO</td><td>'+lan.soft.php_menu_ext+'</td><td>'+lan.soft.mvc_ps+'</td><td><span class="ico-'+(pathinfo?'start':'stop')+' glyphicon glyphicon-'+(pathinfo?'ok':'remove')+'"></span></td><td style="text-align: right;" width="50">'+pathinfoOpt+'</td>';
		$("#pathInfo").html(pathinfo1);
		$(".bt-w-menu .bgw").attr('onclick',"SetPHPConfig('"+version+"',"+pathinfo+",1)");
		$(".bt-w-menu .bgw a").attr('href',"javascript:SetPHPConfig('"+version+"',"+pathinfo+",1);");
		layer.msg(rdata.msg,{icon:1});
	});
}


//PHP扩展配置
function SetPHPConfig(version,pathinfo,go){
	$.get('/ajax?action=GetPHPConfig&version='+version,function(rdata){
		var body  = ""
		var opt = ""
		for(var i=0;i<rdata.libs.length;i++){
			if(rdata.libs[i].versions.indexOf(version) == -1) continue;
			if(rdata.libs[i]['task'] == '-1' && rdata.libs[i].phpversions.indexOf(version) != -1){
				opt = '<a style="color:green;" href="javascript:messagebox();">'+lan.soft.the_install+'</a>'
			}else if(rdata.libs[i]['task'] == '0' && rdata.libs[i].phpversions.indexOf(version) != -1){
				opt = '<a style="color:#C0C0C0;" href="javascript:messagebox();">'+lan.soft.sleep_install+'</a>'
			}else if(rdata.libs[i].status){
				opt = '<a style="color:red;" href="javascript:UninstallPHPLib(\''+version+'\',\''+rdata.libs[i].name+'\',\''+rdata.libs[i].title+'\','+pathinfo+');">'+lan.soft.uninstall+'</a>'
			}else{
				opt = '<a class="btlink" href="javascript:InstallPHPLib(\''+version+'\',\''+rdata.libs[i].name+'\',\''+rdata.libs[i].title+'\','+pathinfo+');">'+lan.soft.install+'</a>'
			}
			
			body += '<tr>'
						+'<td>'+rdata.libs[i].name+'</td>'
						+'<td>'+rdata.libs[i].type+'</td>'
						+'<td>'+rdata.libs[i].msg+'</td>'
						+'<td><span class="ico-'+(rdata.libs[i].status?'start':'stop')+' glyphicon glyphicon-'+(rdata.libs[i].status?'ok':'remove')+'"></span></td>'
						+'<td style="text-align: right;">'+opt+'</td>'
				   +'</tr>'
		}
		
		var pathinfoOpt = '<a style="color:red;" href="javascript:SetPathInfo(\''+version+'\',\'off\');">'+lan.soft.off+'</a>'
		if(!rdata.pathinfo){
			pathinfoOpt = '<a class="btlink" href="javascript:SetPathInfo(\''+version+'\',\'on\');">'+lan.soft.on+'</a>'
		}
		var pathinfo1 = '<tr id="pathInfo"><td>PATH_INFO</td><td>'+lan.soft.php_menu_ext+'</td><td>'+lan.soft.mvc_ps+'</td><td><span class="ico-'+(rdata.pathinfo?'start':'stop')+' glyphicon glyphicon-'+(rdata.pathinfo?'ok':'remove')+'"></span></td><td style="text-align: right;" width="50">'+pathinfoOpt+'</td></tr>';
		var con='<div class="divtable" id="phpextdiv" style="margin-right:10px;height: 420px; overflow: auto; margin-right: 0px;">'
					+'<table class="table table-hover" width="100%" cellspacing="0" cellpadding="0" border="0">'
						+'<thead>'
							+'<tr>'
								+'<th>'+lan.soft.php_ext_name+'</th>'
								+'<th width="64">'+lan.soft.php_ext_type+'</th>'
								+'<th>'+lan.soft.php_ext_ps+'</th>'
								+'<th width="40">'+lan.soft.php_ext_status+'</th>'
								+'<th style="text-align: right;" width="50">'+lan.public.action+'</th>'
							+'</tr>'
						+'</thead>'
						+'<tbody>'+pathinfo1+body+'</tbody>'
					+'</table>'
				+'</div>'
				+'<ul class="help-info-text c7 pull-left"><li>请按实际需求安装扩展,不要安装不必要的PHP扩展,这会影响PHP执行效率,甚至出现异常</li><li>Redis扩展只允许在1个PHP版本中使用,安装到其它PHP版本请在[软件管理]重装Redis</li><li>opcache/xcache/apc等脚本缓存扩展,请只安装其中1个,否则可能导致您的站点程序异常</li></ul>';
		var divObj = document.getElementById('phpextdiv');
		var scrollTopNum = 0;
		if(divObj) scrollTopNum = divObj.scrollTop;
		$(".soft-man-con").html(con);
		document.getElementById('phpextdiv').scrollTop = scrollTopNum;
	});
	
	if(go == undefined){
		setTimeout(function(){
			if($(".bgw #phpext").html() != '安装扩展'){
				return;
			}
			SetPHPConfig(version,pathinfo);
		},3000);
	}
}

//安装扩展
function InstallPHPLib(version,name,title,pathinfo){
	layer.confirm(lan.soft.php_ext_install_confirm.replace('{1}',name),{icon:3,closeBtn:2},function(){
		name = name.toLowerCase();
		var data = "name="+name+"&version="+version+"&type=1";
		var loadT = layer.msg(lan.soft.add_install,{icon:16,time:0,shade: [0.3, '#000']});
		$.post('/files?action=InstallSoft', data, function(rdata)
		{
			setTimeout(function(){
				layer.close(loadT);
				SetPHPConfig(version,pathinfo,true);
				setTimeout(function(){
					layer.msg(rdata.msg,{icon:rdata.status?1:2});
				},1000);
			},1000);
		});
		
		fly("bi-btn");
		InstallTips();
		GetTaskCount();
	});
}

//卸载扩展
function UninstallPHPLib(version,name,title,pathinfo){
	layer.confirm(lan.soft.php_ext_uninstall_confirm.replace('{1}',name),{icon:3,closeBtn:2},function(){
		name = name.toLowerCase();
		var data = 'name='+name+'&version='+version;
		var loadT = layer.msg(lan.public.the,{icon:16,time:0,shade: [0.3, '#000']});
		$.post('/files?action=UninstallSoft',data,function(rdata){
			layer.close(loadT);
			layer.msg(rdata.msg,{icon:rdata.status?1:2});
			SetPHPConfig(version,pathinfo,true);
		});
	});
}
//禁用函数
function disFun(version){
	$.get('/ajax?action=GetPHPConfig&version='+version,function(rdata){
		var disable_functions = rdata.disable_functions.split(',');
		var dbody = ''
		for(var i=0;i<disable_functions.length;i++){
			if(disable_functions[i] == '') continue;
			dbody += "<tr><td>"+disable_functions[i]+"</td><td><a style='float:right;' href=\"javascript:disable_functions('"+version+"','"+disable_functions[i]+"','"+rdata.disable_functions+"');\">"+lan.public.del+"</a></td></tr>";
		}
		
		var con = "<div class='dirBinding'>"
				   +"<input class='bt-input-text mr5' type='text' placeholder='"+lan.soft.fun_ps1+"' id='disable_function_val' style='height: 28px; border-radius: 3px;width: 410px;' />"
				   +"<button class='btn btn-success btn-sm' onclick=\"disable_functions('"+version+"',1,'"+rdata.disable_functions+"')\">"+lan.public.add+"</button>"
				   +"</div>"
				   +"<div class='divtable mtb15' style='height:350px;overflow:auto'><table class='table table-hover' width='100%' style='margin-bottom:0'>"
				   +"<thead><tr><th>"+lan.soft.php_ext_name+"</th><th width='100' class='text-right'>"+lan.public.action+"</th></tr></thead>"
				   +"<tbody id='blacktable'>" + dbody + "</tbody>"
				   +"</table></div>";
		
		con +='\
		<ul class="help-info-text">\
			<li>'+lan.soft.fun_ps2+'</li>\
			<li>'+lan.soft.fun_ps3+'</li>\
		</ul>';
		
		$(".soft-man-con").html(con);
	});
}
//设置禁用函数
function disable_functions(version,act,fs){
	var fsArr = fs.split(',');
	if(act == 1){
		var functions = $("#disable_function_val").val();
		for(var i=0;i<fsArr.length;i++){
			if(functions == fsArr[i]){
				layer.msg(lan.soft.fun_msg,{icon:5});
				return;
			}
		}
		fs += ',' + functions;	
		msg = lan.public.add_success;
	}else{
		
		fs = '';
		for(var i=0;i<fsArr.length;i++){
			if(act == fsArr[i]) continue;
			fs += fsArr[i] + ','
		}
		msg = lan.public.del_success;
		fs = fs.substr(0,fs.length -1);
	}

	var data = 'version='+version+'&disable_functions='+fs;
	var loadT = layer.msg(lan.public.the,{icon:16,time:0,shade: [0.3, '#000']});
	$.post('/config?action=setPHPDisable',data,function(rdata){
		layer.close(loadT);
		layer.msg(rdata.status?msg:rdata.msg,{icon:rdata.status?1:2});
		disFun(version);
	});
}
//性能调整
function SetFpmConfig(version,action){
	if(action == 1){
		$.post('/system?action=GetMemInfo','',function(memInfo){
			var limit_children = parseInt(memInfo['memTotal'] / 8);
			var max_children = Number($("input[name='max_children']").val());
			var start_servers = Number($("input[name='start_servers']").val());
			var min_spare_servers = Number($("input[name='min_spare_servers']").val());
			var max_spare_servers = Number($("input[name='max_spare_servers']").val());
			var pm = $("select[name='pm']").val();
			
			if(limit_children < max_children){
				layer.msg('当前服务器内存不足，最大允许['+limit_children+']个子进程!',{icon:2});
				$("input[name='max_children']").focus();
				return;
			}
			
			if(max_children < max_spare_servers){
				layer.msg(lan.soft.php_fpm_err1,{icon:2});
				return;
			}
			
			if(min_spare_servers > start_servers) {
				layer.msg(lan.soft.php_fpm_err2,{icon:2});
				return;
			}
			
			if(max_spare_servers < min_spare_servers){
				layer.msg(lan.soft.php_fpm_err3,{icon:2});
				return;
			}
			
			if(max_children < start_servers){
				layer.msg(lan.soft.php_fpm_err4,{icon:2});
				return;
			}
			
			if(max_children < 1 || start_servers < 1 || min_spare_servers < 1 || max_spare_servers < 1){
				layer.msg(lan.soft.php_fpm_err5,{icon:2});
				return;
			}
			var data = 'version='+version+'&max_children='+max_children+'&start_servers='+start_servers+'&min_spare_servers='+min_spare_servers+'&max_spare_servers='+max_spare_servers + '&pm='+pm;
			var loadT = layer.msg(lan.public.the,{icon:16,time:0,shade: [0.3, '#000']});
			$.post('/config?action=setFpmConfig',data,function(rdata){
				layer.close(loadT);
				var loadT = layer.msg(rdata.msg,{icon:rdata.status?1:2});				
			}).error(function(){
				layer.close(loadT);
				layer.msg(lan.public.config_ok,{icon:1});
			});
		});
		return;
	}
	
	$.post('/config?action=getFpmConfig','version='+version,function(rdata){
		
		var limitList = "<option value='0'>"+lan.soft.concurrency_m+"</option>"
						+"<option value='1' "+(rdata.max_children==30?'selected':'')+">30"+lan.soft.concurrency+"</option>"
						+"<option value='2' "+(rdata.max_children==50?'selected':'')+">50"+lan.soft.concurrency+"</option>"
						+"<option value='3' "+(rdata.max_children==100?'selected':'')+">100"+lan.soft.concurrency+"</option>"
						+"<option value='4' "+(rdata.max_children==200?'selected':'')+">200"+lan.soft.concurrency+"</option>"
						+"<option value='5' "+(rdata.max_children==300?'selected':'')+">300"+lan.soft.concurrency+"</option>"
						+"<option value='6' "+(rdata.max_children==500?'selected':'')+">500"+lan.soft.concurrency+"</option>"
		var pms = [{'name':'static','title':lan.bt.static},{'name':'dynamic','title':lan.bt.dynamic}];
		var pmList = '';
		for(var i=0;i<pms.length;i++){
			pmList += '<option value="'+pms[i].name+'" '+((pms[i].name == rdata.pm)?'selected':'')+'>'+pms[i].title+'</option>';
		}
		var body="<div class='bingfa'>"
						+"<p class='line'><span class='span_tit'>"+lan.soft.concurrency_type+"：</span><select class='bt-input-text' name='limit' style='width:100px;'>"+limitList+"</select></p>"
						+"<p class='line'><span class='span_tit'>"+lan.soft.php_fpm_model+"：</span><select class='bt-input-text' name='pm' style='width:100px;'>"+pmList+"</select><span class='c9'>*"+lan.soft.php_fpm_ps1+"</span></p>"
						+"<p class='line'><span class='span_tit'>max_children：</span><input class='bt-input-text' type='number' name='max_children' value='"+rdata.max_children+"' /><span class='c9'>*"+lan.soft.php_fpm_ps2+"</span></p>"
						+"<p class='line'><span class='span_tit'>start_servers：</span><input class='bt-input-text' type='number' name='start_servers' value='"+rdata.start_servers+"' />  <span class='c9'>*"+lan.soft.php_fpm_ps3+"</span></p>"
						+"<p class='line'><span class='span_tit'>min_spare_servers：</span><input class='bt-input-text' type='number' name='min_spare_servers' value='"+rdata.min_spare_servers+"' />   <span class='c9'>*"+lan.soft.php_fpm_ps4+"</span></p>"
						+"<p class='line'><span class='span_tit'>max_spare_servers：</span><input class='bt-input-text' type='number' name='max_spare_servers' value='"+rdata.max_spare_servers+"' />   <span class='c9'>*"+lan.soft.php_fpm_ps5+"</span></p>"
						+"<div class='mtb15'><button class='btn btn-success btn-sm' onclick='SetFpmConfig(\""+version+"\",1)'>"+lan.public.save+"</button></div>"
				+"</div>"
		
		$(".soft-man-con").html(body);
		$("select[name='limit']").change(function(){
					var type = $(this).val();
					var max_children = rdata.max_children;
					var start_servers = rdata.start_servers;
					var min_spare_servers = rdata.min_spare_servers;
					var max_spare_servers = rdata.max_spare_servers;
					switch(type){
						case '1':
							max_children = 30;
							start_servers = 5;
							min_spare_servers = 5;
							max_spare_servers = 20;
							break;
						case '2':
							max_children = 50;
							start_servers = 15;
							min_spare_servers = 15;
							max_spare_servers = 35;
							break;
						case '3':
							max_children = 100;
							start_servers = 20;
							min_spare_servers = 20;
							max_spare_servers = 70;
							break;
						case '4':
							max_children = 200;
							start_servers = 25;
							min_spare_servers = 25;
							max_spare_servers = 150;
							break;
						case '5':
							max_children = 300;
							start_servers = 30;
							min_spare_servers = 30;
							max_spare_servers = 180;
							break;
						case '6':
							max_children = 500;
							start_servers = 35;
							min_spare_servers = 35;
							max_spare_servers = 250;
							break;
					}
					
					$("input[name='max_children']").val(max_children);
					$("input[name='start_servers']").val(start_servers);
					$("input[name='min_spare_servers']").val(min_spare_servers);
					$("input[name='max_spare_servers']").val(max_spare_servers);
				});
	});
}

//phpinfo
function BtPhpinfo(version){
	var con = '<button class="btn btn-default btn-sm" onclick="GetPHPInfo(\''+version+'\')">'+lan.soft.phpinfo+'</button>';
	$(".soft-man-con").html(con);
}
//获取PHPInfo
function GetPHPInfo(version){
	var loadT = layer.msg(lan.soft.get,{icon:16,time:0,shade: [0.3, '#000']});
	$.get('/ajax?action=GetPHPInfo&version='+version,function(rdata){
		layer.close(loadT);
		layer.open({
			type: 1,
		    title: "PHP-"+version+"-PHPINFO",
		    area: ['70%','90%'],
		    closeBtn: 2,
		    shadeClose: true,
		    content:rdata.replace('a:link {color: #009; text-decoration: none; background-color: #fff;}','').replace('a:link {color: #000099; text-decoration: none; background-color: #ffffff;}','')
		});
	});
}
//nginx
function nginxSoftMain(name,version){
	var loadT = layer.msg(lan.public.the,{icon:16,time:0,shade: [0.3, '#000']});
	$.get('/system?action=GetConcifInfo',function(rdata){
		layer.close(loadT);
		nameA = rdata['web'];
		var status = name=='nginx'?'<p onclick="GetNginxStatus()">'+lan.soft.nginx_status+'</p>':'';
		var menu = '';
		if(version != undefined || version !=''){
			var menu = '<p onclick="softChangeVer(\''+name+'\',\''+version+'\')">'+lan.soft.nginx_version+'</p>';
		}
		
		var waf = ''
		if(name == 'nginx'){
			waf = '<p onclick="waf()">'+lan.soft.waf_title+'</p>' 
		}
		
		var logsPath = (name == 'nginx')?'/www/wwwlogs/nginx_error.log':'/www/wwwlogs/error_log';
		layer.open({
			type: 1,
			area: '640px',
			title: name+lan.soft.admin,
			closeBtn: 2,
			shift: 0,
			content: '<div class="bt-w-main" style="width:640px;">\
				<div class="bt-w-menu">\
					<p class="bgw" onclick="service(\''+name+'\','+nameA.status+')">'+lan.soft.web_service+'</p>\
					<p onclick="configChange(\''+name+'\')">'+lan.soft.config_edit+'</p>\
					'+waf+'\
					'+menu+'\
					'+status+'\
					<p onclick="showLogs(\''+logsPath+'\')">错误日志</p>\
				</div>\
				<div id="webEdit-con" class="bt-w-con pd15" style="height:555px;overflow:auto">\
					<div class="soft-man-con"></div>\
				</div>\
			</div>'
		});
		service(name,nameA.status);
		$(".bt-w-menu p").click(function(){
			//var i = $(this).index();
			$(this).addClass("bgw").siblings().removeClass("bgw");
		});
	});
}

//显示指定日志
function showLogs(logPath){
	var loadT = layer.msg(lan.public.the_get,{icon:16,time:0,shade: [0.3, '#000']});
	$.post('/ajax?action=GetOpeLogs',{path:logPath},function(rdata){
		layer.close(loadT);
		if(rdata.msg == '') rdata.msg = '当前没有日志!';
		var ebody = '<div class="soft-man-con"><textarea readonly="" style="margin: 0px;width: 500px;height: 520px;background-color: #333;color:#fff; padding:0 5px" id="error_log">'+rdata.msg+'</textarea></div>';
		$(".soft-man-con").html(ebody);
		var ob = document.getElementById('error_log');
		ob.scrollTop = ob.scrollHeight;	
	});
}

//WAF防火墙
function waf(){
	var loadT = layer.msg(lan.public.the_get,{icon:16,time:0,shade: [0.3, '#000']});
	$.get("/waf?action=GetConfig",function(rdata){
		layer.close(loadT);
		if(rdata.status == -1){
			layer.msg(lan.soft.waf_not,{icon:5,time:5000});
			return;
		}
		
		var whiteList = ""
		for(var i=0;i<rdata.ipWhitelist.length;i++){
			if(rdata.ipWhitelist[i] == "") continue;
			whiteList += "<tr><td>"+rdata.ipWhitelist[i]+"</td><td><a href=\"javascript:deleteWafKey('ipWhitelist','"+rdata.ipWhitelist[i]+"');\">"+lan.public.del+"</a></td></tr>";
		}
		
		var blackList = ""
		for(var i=0;i<rdata.ipBlocklist.length;i++){
			if(rdata.ipBlocklist[i] == "") continue;
			blackList += "<tr><td>"+rdata.ipBlocklist[i]+"</td><td><a href=\"javascript:deleteWafKey('ipBlocklist','"+rdata.ipBlocklist[i]+"');\">"+lan.public.del+"</a></td></tr>";
		}
				
		var cc = rdata.CCrate.split('/')
		
		var con = "<div class='wafConf'>\
					<div class='wafConf-btn'>\
						<span>"+lan.soft.waf_title+"</span><div class='ssh-item'>\
                            <input class='btswitch btswitch-ios' id='closeWaf' type='checkbox' "+(rdata.status == 1?'checked':'')+">\
                            <label class='btswitch-btn' for='closeWaf' onclick='CloseWaf()'></label>\
                    	</div>\
						<div class='pull-right'>\
                    	<button class='btn btn-default btn-sm' onclick='gzEdit()'>"+lan.soft.waf_edit+"</button>\
                    	<button class='btn btn-default btn-sm' onclick='upLimit()'>"+lan.soft.waf_up_title+"</button>\
						</div>\
					</div>\
					<div class='wafConf_checkbox label-input-group ptb10 relative'>\
					<input type='checkbox' id='waf_UrlDeny' "+(rdata['UrlDeny'] == 'on'?'checked':'')+" onclick=\"SetWafConfig('UrlDeny','"+(rdata['UrlDeny'] == 'on'?'off':'on')+"')\" /><label for='waf_UrlDeny'>"+lan.soft.waf_input1+"</label>\
					<input type='checkbox' id='waf_CookieMatch' "+(rdata['CookieMatch'] == 'on'?'checked':'')+" onclick=\"SetWafConfig('CookieMatch','"+(rdata['CookieMatch'] == 'on'?'off':'on')+"')\" /><label for='waf_CookieMatch'>"+lan.soft.waf_input2+"</label>\
					<input type='checkbox' id='waf_postMatch' "+(rdata['postMatch'] == 'on'?'checked':'')+" onclick=\"SetWafConfig('postMatch','"+(rdata['postMatch'] == 'on'?'off':'on')+"')\" /><label for='waf_postMatch'>"+lan.soft.waf_input3+"</label>\
					<input type='checkbox' id='waf_CCDeny' "+(rdata['CCDeny'] == 'on'?'checked':'')+" onclick=\"SetWafConfig('CCDeny','"+(rdata['CCDeny'] == 'on'?'off':'on')+"')\" /><label for='waf_CCDeny'>"+lan.soft.waf_input4+"</label>\
					<input type='checkbox' id='waf_attacklog' "+(rdata['attacklog'] == 'on'?'checked':'')+" onclick=\"SetWafConfig('attacklog','"+(rdata['attacklog'] == 'on'?'off':'on')+"')\" /><label for='waf_attacklog'>"+lan.soft.waf_input5+"</label>\
					<span class='glyphicon glyphicon-folder-open' style='position: absolute; right: 10px; top: 12px; color: orange;cursor: pointer' onclick='openPath(\"/www/wwwlogs/waf\")'></span>\
					</div>\
					<div class='wafConf_cc'>\
					<span>"+lan.soft.waf_input6+"</span><input id='CCrate_1' class='bt-input-text' type='number' value='" + cc[0] + "' style='width:80px;margin-right:30px'/>\
					<span>"+lan.soft.waf_input7+"("+lan.bt.s+")</span><input id='CCrate_2' class='bt-input-text' type='number' value='" + cc[1] + "' style='width:80px;'/>\
					<button onclick=\"SetWafConfig('CCrate','')\" class='btn btn-default btn-sm'>"+lan.public.ok+"</button>\
					</div>\
					<div class='wafConf_ip'>\
						<fieldset>\
						<legend>"+lan.soft.waf_input8+"</legend>\
						<input type='text' id='ipWhitelist_val' class='bt-input-text mr5' placeholder='"+lan.soft.waf_ip+"' style='width:175px;' /><button onclick=\"addWafKey('ipWhitelist')\" class='btn btn-default btn-sm'>"+lan.public.add+"</button>\
						<div class='table-overflow'><table class='table table-hover'>"+whiteList+"</table></div>\
						</fieldset>\
						<fieldset>\
						<legend>"+lan.soft.waf_input9+"</legend>\
						<input type='text' id='ipBlocklist_val' class='bt-input-text mr5' placeholder='"+lan.soft.waf_ip+"' style='width:175px;' /><button onclick=\"addWafKey('ipBlocklist')\" class='btn btn-default btn-sm'>"+lan.public.add+"</button>\
						<div class='table-overflow'><table class='table table-hover'>"+blackList+"</table></div>\
						</fieldset>\
					</div>\
				</div>"
		$(".soft-man-con").html(con);
	});
}

//上传限制
function upLimit(){
	var loadT = layer.msg(lan.public.the_get,{icon:16,time:0,shade: [0.3, '#000']});
	$.get("/waf?action=GetConfig",function(rdata){
		layer.close(loadT);
		var black_fileExt = ''
		for(var i=0;i<rdata.black_fileExt.length;i++){
			black_fileExt += "<tr><td>"+rdata.black_fileExt[i]+"</td><td><a style='float:right;' href=\"javascript:deleteWafKey('black_fileExt','"+rdata.black_fileExt[i]+"');\">"+lan.public.del+"</a></td></tr>";
		}
		
		if($("#blacktable").html() != undefined){
			$("#blacktable").html(black_fileExt);
			$("#black_fileExt_val").val('');
			return;
		}
		
		layer.open({
			type: 1,
			area: '300px',
			title: lan.soft.waf_up_title,
			closeBtn: 2,
			shift: 0,
			content:"<div class='dirBinding mlr15'>"
				   +"<input class='bt-input-text mr5' type='text' placeholder='"+lan.soft.waf_up_from1+"' id='black_fileExt_val' style='height: 28px; border-radius: 3px;width: 219px;margin-top:15px' />"
				   +"<button class='btn btn-success btn-sm' onclick=\"addWafKey('black_fileExt')\">"+lan.public.add+"</button>"
				   +"</div>"
				   +"<div class='divtable' style='margin:15px'><table class='table table-hover' width='100%' style='margin-bottom:0'>"
				   +"<thead><tr><th>"+lan.soft.waf_up_from2+"</th><th width='100' class='text-right'>"+lan.public.action+"</th></tr></thead>"
				   +"<tbody id='blacktable'>" + black_fileExt + "</tbody>"
				   +"</table></div>"
		});
	});
}

//设置waf状态
function CloseWaf(){
	var loadT = layer.msg(lan.public.the,{icon:16,time:0,shade: [0.3, '#000']});
	$.post('/waf?action=SetStatus','',function(rdata){
		layer.close(loadT)
		layer.msg(rdata.msg,{icon:rdata.status?1:5});
		if(rdata.status) waf();
	});
}

//取规则文件 
function GetWafFile(name){
	OnlineEditFile(0,'/www/server/panel/vhost/wafconf/' + name);
}
//规则编辑
function gzEdit(){
	layer.open({
		type: 1,
		area: '360px',
		title: lan.soft.waf_edit,
		closeBtn: 2,
		shift: 0,
		content:"<div class='gzEdit'><button class='btn btn-default btn-sm' onclick=\"GetWafFile('cookie')\">Cookie</button>\
				<button class='btn btn-default btn-sm' onclick=\"GetWafFile('post')\">POST</button>\
				<button class='btn btn-default btn-sm' onclick=\"GetWafFile('url')\">URL</button>\
				<button class='btn btn-default btn-sm' onclick=\"GetWafFile('user-agent')\">User-Agent</button>\
				<button class='btn btn-default btn-sm' onclick=\"GetWafFile('args')\">Args</button>\
				<button class='btn btn-default btn-sm' onclick=\"GetWafFile('whiteurl')\">"+lan.soft.waf_url_white+"</button>\
				<button class='btn btn-default btn-sm' onclick=\"GetWafFile('returnhtml')\">"+lan.soft.waf_index+"</button>\
				<button class='btn btn-default btn-sm' onclick=\"updateWaf('returnhtml')\">"+lan.soft.waf_cloud+"</button></div>"
	});
}

//更新WAF规则
function updateWaf(){
	var loadT = layer.msg(lan.soft.waf_update,{icon:16,time:0,shade: [0.3, '#000']});
	$.post('/waf?action=updateWaf','',function(rdata){
		layer.close(loadT)
		layer.msg(rdata.msg,{icon:rdata.status?1:5});
	});
}

//设置WAF配置值
function SetWafConfig(name,value){
	if(name == 'CCrate'){
		var CCrate_1 = $("#CCrate_1").val();
		var CCrate_2 = $("#CCrate_2").val();
		if (CCrate_1 < 1 || CCrate_1 > 3000 || CCrate_2 < 1 || CCrate_2 > 1800){
			layer.msg(lan.soft.waf_cc_err,{icon:5});
			return;
		}
		value = CCrate_1 + '/' + CCrate_2;
	}
	var loadT = layer.msg(lan.public.the,{icon:16,time:0,shade: [0.3, '#000']});
	$.post('/waf?action=SetConfigString','name='+name+'&value='+value,function(rdata){
		layer.close(loadT)
		layer.msg(rdata.msg,{icon:rdata.status?1:5});
		if(rdata.status) waf();
		
	});
}


//删除WAF指定值
function deleteWafKey(name,value){
	var loadT = layer.msg(lan.public.the,{icon:16,time:0,shade: [0.3, '#000']});
	$.post('/waf?action=SetConfigList&act=del','name='+name+'&value='+value,function(rdata){
		layer.close(loadT)
		layer.msg(rdata.msg,{icon:rdata.status?1:5});
		if(rdata.status) waf();
		if(name == 'black_fileExt') upLimit();
	});
}

//删除WAF指定值
function addWafKey(name){
	var value = $('#'+name+'_val').val();
	var loadT = layer.msg(lan.public.the,{icon:16,time:0,shade: [0.3, '#000']});
	$.post('/waf?action=SetConfigList&act=add','name='+name+'&value='+value,function(rdata){
		layer.close(loadT)
		layer.msg(rdata.msg,{icon:rdata.status?1:5});
		if(rdata.status) waf();
		if(name == 'black_fileExt') upLimit();
	});
}



//查看Nginx负载状态
function GetNginxStatus(){
	$.post('/ajax?action=GetNginxStatus','',function(rdata){
		var con = "<div><table class='table table-hover table-bordered'>\
						<tr><th>"+lan.bt.nginx_active+"</th><td>"+rdata.active+"</td></tr>\
						<tr><th>"+lan.bt.nginx_accepts+"</th><td>"+rdata.accepts+"</td></tr>\
						<tr><th>"+lan.bt.nginx_handled+"</th><td>"+rdata.handled+"</td></tr>\
						<tr><th>"+lan.bt.nginx_requests+"</th><td>"+rdata.requests+"</td></tr>\
						<tr><th>"+lan.bt.nginx_reading+"</th><td>"+rdata.Reading+"</td></tr>\
						<tr><th>"+lan.bt.nginx_writing+"</th><td>"+rdata.Writing+"</td></tr>\
						<tr><th>"+lan.bt.nginx_waiting+"</th><td>"+rdata.Waiting+"</td></tr>\
					 </table></div>";
		$(".soft-man-con").html(con);
	})
}
//查看PHP负载状态
function GetPHPStatus(version){
	$.post('/ajax?action=GetPHPStatus','version='+version,function(rdata){
		var con = "<div style='height:420px;overflow:hidden;'><table class='table table-hover table-bordered GetPHPStatus' style='margin:0;padding:0'>\
						<tr><th>"+lan.bt.php_pool+"</th><td>"+rdata.pool+"</td></tr>\
						<tr><th>"+lan.bt.php_manager+"</th><td>"+((rdata['process manager'] == 'dynamic')?lan.bt.dynamic:lan.bt.static)+"</td></tr>\
						<tr><th>"+lan.bt.php_start+"</th><td>"+rdata['start time']+"</td></tr>\
						<tr><th>"+lan.bt.php_accepted+"</th><td>"+rdata['accepted conn']+"</td></tr>\
						<tr><th>"+lan.bt.php_queue+"</th><td>"+rdata['listen queue']+"</td></tr>\
						<tr><th>"+lan.bt.php_max_queue+"</th><td>"+rdata['max listen queue']+"</td></tr>\
						<tr><th>"+lan.bt.php_len_queue+"</th><td>"+rdata['listen queue len']+"</td></tr>\
						<tr><th>"+lan.bt.php_idle+"</th><td>"+rdata['idle processes']+"</td></tr>\
						<tr><th>"+lan.bt.php_active+"</th><td>"+rdata['active processes']+"</td></tr>\
						<tr><th>"+lan.bt.php_total+"</th><td>"+rdata['total processes']+"</td></tr>\
						<tr><th>"+lan.bt.php_max_active+"</th><td>"+rdata['max active processes']+"</td></tr>\
						<tr><th>"+lan.bt.php_max_children+"</th><td>"+rdata['max children reached']+"</td></tr>\
						<tr><th>"+lan.bt.php_slow+"</th><td>"+rdata['slow requests']+"</td></tr>\
					 </table></div>";
		$(".soft-man-con").html(con);
		$(".GetPHPStatus td,.GetPHPStatus th").css("padding","7px");
	})
}

//软件管理窗口
function SoftMan(name,version){
	switch(name){
		case 'nginx':
			nginxSoftMain(name,version);
			return;
			break;
		case 'apache':
			nginxSoftMain(name,version);
			return;
			break;
		case 'mysql':
			name='mysqld';
			break;
	}
	var loadT = layer.msg(lan.public.the,{icon:16,time:0,shade: [0.3, '#000']});
	$.get('/system?action=GetConcifInfo',function(rdata){
		layer.close(loadT);
		var nameA = rdata[name.replace('mysqld','mysql')];
		var menu = '<p onclick="configChange(\''+name+'\')">'+lan.soft.config_edit+'</p><p onclick="softChangeVer(\''+name+'\',\''+version+'\')">'+lan.soft.nginx_version+'</p>';
		if(name == "phpmyadmin"){
			menu = '<p onclick="phpVer(\''+name+'\',\''+nameA.phpversion+'\')">'+lan.soft.php_version+'</p><p onclick="safeConf(\''+name+'\','+nameA.port+','+nameA.auth+')">'+lan.soft.safe+'</p>';
		}
		if(version == undefined || version == ''){
			var menu = '<p onclick="configChange(\''+name+'\')">'+lan.soft.config_edit+'</p>';
		}
		
		if(name == 'mysqld'){
			menu += '<p onclick="changeMySQLDataPath()">'+lan.soft.save_path+'</p><p onclick="changeMySQLPort()">'+lan.site.port+'</p><p onclick="mysqlRunStatus()">'+lan.soft.status+'</p><p onclick="mysqlStatus()">'+lan.soft.php_main7+'</p><p onclick="mysqlLog()">'+lan.soft.log+'</p><p onclick="mysqlSlowLog()">慢日志</p>';
		}
		
		else if(name == 'memcached'){
			menu += '<p onclick="MemcachedStatus()">负载状态</p><p onclick="MemcachedCache()">性能调整</p>';
		}
		
		else if(name == 'redis'){
			menu += '<p onclick="RedisStatus()">负载状态</p>';
		}
		
		else if(name == 'tomcat'){
			menu += '<p onclick="showLogs(\'/www/server/tomcat/logs/catalina.out\')">运行日志</p>';
		}
		
		layer.open({
			type: 1,
			area: '640px',
			title: name+lan.soft.admin,
			closeBtn: 2,
			shift: 0,
			content: '<div class="bt-w-main" style="width:640px;">\
				<div class="bt-w-menu">\
					<p class="bgw" onclick="service(\''+name+'\',\''+nameA.status+'\')">'+lan.soft.service+'</p>'
					+menu+
				'</div>\
				<div id="webEdit-con" class="bt-w-con pd15" style="height:555px;overflow:auto">\
					<div class="soft-man-con"></div>\
				</div>\
			</div>'
		});
		service(name,nameA.status);
		$(".bt-w-menu p").click(function(){
			//var i = $(this).index();
			$(this).addClass("bgw").siblings().removeClass("bgw");
		});
	});
}

//redis负载状态
function RedisStatus(){
	var loadT = layer.msg('正在获取...',{icon:16,time:0,shade:0.3});
	$.get('/ajax?action=GetRedisStatus',function(rdata){
		layer.close(loadT);
		hit = (parseInt(rdata.keyspace_hits) / (parseInt(rdata.keyspace_hits) + parseInt(rdata.keyspace_misses)) * 100).toFixed(2);
		var Con = '<div class="divtable">\
						<table class="table table-hover table-bordered" style="width: 490px;">\
						<thead><th>字段</th><th>当前值</th><th>说明</th></thead>\
						<tbody>\
							<tr><th>uptime_in_days</th><td>'+rdata.uptime_in_days+'</td><td>已运行天数</td></tr>\
							<tr><th>tcp_port</th><td>'+rdata.tcp_port+'</td><td>当前监听端口</td></tr>\
							<tr><th>connected_clients</th><td>'+rdata.connected_clients+'</td><td>连接的客户端数量</td></tr>\
							<tr><th>used_memory_rss</th><td>'+ToSize(rdata.used_memory_rss)+'</td><td>Redis当前占用的系统内存总量</td></tr>\
							<tr><th>used_memory</th><td>'+ToSize(rdata.used_memory)+'</td><td>Redis当前已分配的内存总量</td></tr>\
							<tr><th>used_memory_peak</th><td>'+ToSize(rdata.used_memory_peak)+'</td><td>Redis历史分配内存的峰值</td></tr>\
							<tr><th>mem_fragmentation_ratio</th><td>'+rdata.mem_fragmentation_ratio+'%</td><td>内存碎片比率</td></tr>\
							<tr><th>total_connections_received</th><td>'+rdata.total_connections_received+'</td><td>运行以来连接过的客户端的总数量</td></tr>\
							<tr><th>total_commands_processed</th><td>'+rdata.total_commands_processed+'</td><td>运行以来执行过的命令的总数量</td></tr>\
							<tr><th>instantaneous_ops_per_sec</th><td>'+rdata.instantaneous_ops_per_sec+'</td><td>服务器每秒钟执行的命令数量</td></tr>\
							<tr><th>keyspace_hits</th><td>'+rdata.keyspace_hits+'</td><td>查找数据库键成功的次数</td></tr>\
							<tr><th>keyspace_misses</th><td>'+rdata.keyspace_misses+'</td><td>查找数据库键失败的次数</td></tr>\
							<tr><th>hit</th><td>'+hit+'%</td><td>查找数据库键命中率</td></tr>\
							<tr><th>latest_fork_usec</th><td>'+rdata.latest_fork_usec+'</td><td>最近一次 fork() 操作耗费的微秒数</td></tr>\
						<tbody>\
				</table></div>'
			$(".soft-man-con").html(Con);
	});
}

//memcached负载状态
function MemcachedStatus(){
	var loadT = layer.msg('正在获取...',{icon:16,time:0,shade:0.3});
	$.get('/ajax?action=GetMemcachedStatus',function(rdata){
		layer.close(loadT);
		var Con = '<div class="divtable">\
						<table class="table table-hover table-bordered" style="width: 490px;">\
						<thead><th>字段</th><th>当前值</th><th>说明</th></thead>\
						<tbody>\
							<tr><th>BindIP</th><td>'+rdata.bind+'</td><td>监听IP</td></tr>\
							<tr><th>PORT</th><td>'+rdata.port+'</td><td>监听端口</td></tr>\
							<tr><th>CACHESIZE</th><td>'+rdata.cachesize+' MB</td><td>最大缓存容量</td></tr>\
							<tr><th>MAXCONN</th><td>'+rdata.maxconn+'</td><td>最大连接数限制</td></tr>\
							<tr><th>curr_connections</th><td>'+rdata.curr_connections+'</td><td>当前打开的连接数</td></tr>\
							<tr><th>cmd_get</th><td>'+rdata.cmd_get+'</td><td>GET请求数</td></tr>\
							<tr><th>get_hits</th><td>'+rdata.get_hits+'</td><td>GET命中次数</td></tr>\
							<tr><th>get_misses</th><td>'+rdata.get_misses+'</td><td>GET失败次数</td></tr>\
							<tr><th>hit</th><td>'+rdata.hit.toFixed(2)+'%</td><td>GET命中率</td></tr>\
							<tr><th>curr_items</th><td>'+rdata.curr_items+'</td><td>当前被缓存的数据行数</td></tr>\
							<tr><th>evictions</th><td>'+rdata.evictions+'</td><td>因内存不足而被清理的缓存行数</td></tr>\
							<tr><th>bytes</th><td>'+ToSize(rdata.bytes)+'</td><td>当前已使用内存</td></tr>\
							<tr><th>bytes_read</th><td>'+ToSize(rdata.bytes_read)+'</td><td>请求总大小</td></tr>\
							<tr><th>bytes_written</th><td>'+ToSize(rdata.bytes_written)+'</td><td>发送总大小</td></tr>\
						<tbody>\
				</table></div>'
			$(".soft-man-con").html(Con);
	});
}

//memcached性能调整
function MemcachedCache(){
	var loadT = layer.msg('正在获取...',{icon:16,time:0,shade:0.3});
	$.get('/ajax?action=GetMemcachedStatus',function(rdata){
		layer.close(loadT);
		var memCon = '<div class="conf_p" style="margin-bottom:0">\
						<p><span>BindIP</span><input style="width: 120px;" class="bt-input-text mr5" name="membind" value="'+rdata.bind+'" type="text" ><font>监听IP,请勿随意修改</font></p>\
						<p><span>PORT</span><input style="width: 120px;" class="bt-input-text mr5" max="65535" name="memport" value="'+rdata.port+'" type="number" ><font>监听端口,一般无需修改</font></p>\
						<p><span>CACHESIZE</span><input style="width: 120px;" class="bt-input-text mr5" name="memcachesize" value="'+rdata.cachesize+'" type="number" >MB,<font>缓存大小,建议不要大于512M</font></p>\
						<p><span>MAXCONN</span><input style="width: 120px;" class="bt-input-text mr5" name="memmaxconn" value="'+rdata.maxconn+'" type="number" ><font>最大连接数,建议不要大于40960</font></p>\
						<div style="margin-top:10px; padding-right:230px" class="text-right"><button class="btn btn-success btn-sm" onclick="SetMemcachedConf()">'+lan.public.save+'</button></div>\
					</div>'
		$(".soft-man-con").html(memCon);
	});
}

//memcached提交配置
function SetMemcachedConf(){
	var data = {
			ip:$("input[name='membind']").val(),
			port:$("input[name='memport']").val(),
			cachesize:$("input[name='memcachesize']").val(),
			maxconn:$("input[name='memmaxconn']").val()
		}
	
	if(data.ip.split('.').length < 4){
		layer.msg('IP地址格式不正确!',{icon:2});
		return;
	}
	
	if(data.port < 1 || data.port > 65535){
		layer.msg('端口范围不正确!',{icon:2});
		return;
	}
	
	if(data.cachesize < 8){
		layer.msg('缓存值过小',{icon:2});
		return;
	}
	
	if(data.maxconn < 4){
		layer.msg('最大连接数过小',{icon:2});
		return;
	}
	var loadT = layer.msg('正在保存...',{icon:16,time:0,shade:0.3});
	$.post('/ajax?action=SetMemcachedCache',data,function(rdata){
		layer.close(loadT);
		layer.msg(rdata.msg,{icon:rdata.status?1:2});
	});
}

//数据库存储信置
function changeMySQLDataPath(act){
	if(act != undefined){
		layer.confirm(lan.soft.mysql_to_msg,{closeBtn:2,icon:3},function(){
			var datadir = $("#datadir").val();
			var data = 'datadir='+datadir;
			var loadT = layer.msg(lan.soft.mysql_to_msg1,{icon:16,time:0,shade: [0.3, '#000']});
			$.post('/database?action=SetDataDir',data,function(rdata){
				layer.close(loadT)
				layer.msg(rdata.msg,{icon:rdata.status?1:5});
			});
		});
		return;
	}
	
	$.post('/database?action=GetMySQLInfo','',function(rdata){
		var LimitCon = '<p class="conf_p">\
							<input id="datadir" class="phpUploadLimit bt-input-text mr5" style="width:350px;" type="text" value="'+rdata.datadir+'" name="datadir">\
							<span onclick="ChangePath(\'datadir\')" class="glyphicon glyphicon-folder-open cursor mr20" style="width:auto"></span><button class="btn btn-success btn-sm" onclick="changeMySQLDataPath(1)">'+lan.soft.mysql_to+'</button>\
						</p>';
		$(".soft-man-con").html(LimitCon);
	});
}

//MySQL-Slow日志
function mysqlSlowLog(){
	var loadT = layer.msg(lan.public.the,{icon:16,time:0,shade: [0.3, '#000']});
	$.post('/database?action=GetSlowLogs',{},function(logs){
		layer.close(loadT);
		if(logs.status !== true){
			logs.msg = '';
		}
		if (logs.msg == '') logs.msg = '当前没有慢日志.';
		var phpCon = '<textarea readonly="" style="margin: 0px;width: 500px;height: 520px;background-color: #333;color:#fff; padding:0 5px" id="error_log">'+logs.msg+'</textarea>';
		$(".soft-man-con").html(phpCon);
		var ob = document.getElementById('error_log');
		ob.scrollTop = ob.scrollHeight;		
	});
}

//数据库日志
function mysqlLog(act){
	//获取二进制日志相关信息
	$.post('/database?action=BinLog',"status=1",function(rdata){
		var limitCon = '<p class="conf_p">\
							<span class="f14 c6 mr20">'+lan.soft.mysql_log_bin+' </span><span class="f14 c6 mr20">'+ToSize(rdata.msg)+'</span>\
							<button class="btn btn-success btn-xs va0" onclick="SetBinLog();">'+(rdata.status?lan.soft.off:lan.soft.on)+'</button>\
							<p class="f14 c6 mtb10" style="border-top:#ddd 1px solid; padding:10px 0">'+lan.soft.mysql_log_err+'<button class="btn btn-default btn-xs" style="float:right;" onclick="closeMySqlLog();">'+lan.soft.mysql_log_close+'</button></p>\
							<textarea readonly style="margin: 0px;width: 515px;height: 440px;background-color: #333;color:#fff; padding:0 5px" id="error_log"></textarea>\
						</p>'
		
		$(".soft-man-con").html(limitCon);
		
		//获取错误日志
		$.post('/database?action=GetErrorLog',"",function(error_body){
			if(error_body.status === false){
				layer.msg(error_body.msg,{icon:5});
				error_body = lan.soft.mysql_log_ps1;
			}
			if(error_body == "") error_body = lan.soft.mysql_log_ps1;
			$("#error_log").text(error_body);
			var ob = document.getElementById('error_log');
			ob.scrollTop = ob.scrollHeight;
		});
	});
}

//取数据库运行状态
function mysqlRunStatus(){
	$.post('/database?action=GetRunStatus',"",function(rdata){
		var cache_size = ((parseInt(rdata.Qcache_hits)/(parseInt(rdata.Qcache_hits)+parseInt(rdata.Qcache_inserts)))* 100).toFixed(2) + '%';
		if(cache_size == 'NaN%') cache_size = 'OFF';
		var Con = '<div class="divtable"><table class="table table-hover table-bordered" style="width: 490px;margin-bottom:10px;background-color:#fafafa">\
						<tbody>\
							<tr><th>'+lan.soft.mysql_status_title1+'</th><td>'+getLocalTime(rdata.Run)+'</td><th>'+lan.soft.mysql_status_title5+'</th><td>'+parseInt(rdata.Questions/rdata.Uptime)+'</td></tr>\
							<tr><th>'+lan.soft.mysql_status_title2+'</th><td>'+rdata.Connections+'</td><th>'+lan.soft.mysql_status_title6+'</th><td>'+parseInt((parseInt(rdata.Com_commit) + parseInt(rdata.Com_rollback)) / rdata.Uptime) +'</td></tr>\
							<tr><th>'+lan.soft.mysql_status_title3+'</th><td>'+ToSize(rdata.Bytes_sent)+'</td><th>'+lan.soft.mysql_status_title7+'</th><td>'+rdata.File+'</td></tr>\
							<tr><th>'+lan.soft.mysql_status_title4+'</th><td>'+ToSize(rdata.Bytes_received)+'</td><th>'+lan.soft.mysql_status_title8+'</th><td>'+rdata.Position+'</td></tr>\
						</tbody>\
						</table>\
						<table class="table table-hover table-bordered" style="width: 490px;">\
						<thead style="display:none;"><th></th><th></th><th></th><th></th></thead>\
						<tbody>\
							<tr><th>'+lan.soft.mysql_status_title9+'</th><td>'+rdata.Threads_running+'/'+rdata.Max_used_connections+'</td><td colspan="2">'+lan.soft.mysql_status_ps1+'</td></tr>\
							<tr><th>'+lan.soft.mysql_status_title10+'</th><td>'+((1-rdata.Threads_created/rdata.Connections)* 100).toFixed(2)+'%</td><td colspan="2">'+lan.soft.mysql_status_ps2+'</td></tr>\
							<tr><th>'+lan.soft.mysql_status_title11+'</th><td>'+((1-rdata.Key_reads / rdata.Key_read_requests) * 100).toFixed(2)+'%</td><td colspan="2">'+lan.soft.mysql_status_ps3+'</td></tr>\
							<tr><th>'+lan.soft.mysql_status_title12+'</th><td>'+((1-rdata.Innodb_buffer_pool_reads/rdata.Innodb_buffer_pool_read_requests) * 100).toFixed(2)+'%</td><td colspan="2">'+lan.soft.mysql_status_ps4+'</td></tr>\
							<tr><th>'+lan.soft.mysql_status_title13+'</th><td>'+cache_size+'</td><td colspan="2">'+lan.soft.mysql_status_ps5+'</td></tr>\
							<tr><th>'+lan.soft.mysql_status_title14+'</th><td>'+((rdata.Created_tmp_disk_tables/rdata.Created_tmp_tables) * 100).toFixed(2)+'%</td><td colspan="2">'+lan.soft.mysql_status_ps6+'</td></tr>\
							<tr><th>'+lan.soft.mysql_status_title15+'</th><td>'+rdata.Open_tables+'</td><td colspan="2">'+lan.soft.mysql_status_ps7+'</td></tr>\
							<tr><th>'+lan.soft.mysql_status_title16+'</th><td>'+rdata.Select_full_join+'</td><td colspan="2">'+lan.soft.mysql_status_ps8+'</td></tr>\
							<tr><th>'+lan.soft.mysql_status_title17+'</th><td>'+rdata.Select_range_check+'</td><td colspan="2">'+lan.soft.mysql_status_ps9+'</td></tr>\
							<tr><th>'+lan.soft.mysql_status_title18+'</th><td>'+rdata.Sort_merge_passes+'</td><td colspan="2">'+lan.soft.mysql_status_ps10+'</td></tr>\
							<tr><th>'+lan.soft.mysql_status_title19+'</th><td>'+rdata.Table_locks_waited+'</td><td colspan="2">'+lan.soft.mysql_status_ps11+'</td></tr>\
						<tbody>\
				</table></div>'
			$(".soft-man-con").html(Con);
	});
}

//数据库配置状态
function mysqlStatus(){
	//获取MySQL配置
	$.post('/database?action=GetDbStatus',"",function(rdata){
		var key_buffer_size = ToSizeM(rdata.mem.key_buffer_size)
		var query_cache_size = ToSizeM(rdata.mem.query_cache_size)
		var tmp_table_size = ToSizeM(rdata.mem.tmp_table_size)
		var innodb_buffer_pool_size = ToSizeM(rdata.mem.innodb_buffer_pool_size)
		var innodb_additional_mem_pool_size = ToSizeM(rdata.mem.innodb_additional_mem_pool_size)
		var innodb_log_buffer_size = ToSizeM(rdata.mem.innodb_log_buffer_size)
		
		var sort_buffer_size = ToSizeM(rdata.mem.sort_buffer_size)
		var read_buffer_size = ToSizeM(rdata.mem.read_buffer_size) 
		var read_rnd_buffer_size = ToSizeM(rdata.mem.read_rnd_buffer_size)
		var join_buffer_size = ToSizeM(rdata.mem.join_buffer_size)
		var thread_stack = ToSizeM(rdata.mem.thread_stack)
		var binlog_cache_size = ToSizeM(rdata.mem.binlog_cache_size)
		
		var a = key_buffer_size + query_cache_size + tmp_table_size + innodb_buffer_pool_size + innodb_additional_mem_pool_size + innodb_log_buffer_size
		var b = sort_buffer_size + read_buffer_size + read_rnd_buffer_size + join_buffer_size + thread_stack + binlog_cache_size
		var memSize = a  + rdata.mem.max_connections * b
		
		
		var memCon = '<div class="conf_p" style="margin-bottom:0">\
						<div style="border-bottom:#ccc 1px solid;padding-bottom:10px;margin-bottom:10px"><span><b>'+lan.soft.mysql_set_msg+'</b></span>\
						<select class="bt-input-text" name="mysql_set" style="margin-left:-4px">\
							<option value="0">'+lan.soft.mysql_set_select+'</option>\
							<option value="1">1-2GB</option>\
							<option value="2">2-4GB</option>\
							<option value="3">4-8GB</option>\
							<option value="4">8-16GB</option>\
							<option value="5">16-32GB</option>\
						</select>\
						<span>'+lan.soft.mysql_set_maxmem+': </span><input style="width:70px;background-color:#eee;" class="bt-input-text mr5" name="memSize" type="text" value="'+memSize.toFixed(2)+'" readonly>MB\
						</div>\
						<p><span>key_buffer_size</span><input style="width: 70px;" class="bt-input-text mr5" name="key_buffer_size" value="'+key_buffer_size+'" type="number" >MB, <font>'+lan.soft.mysql_set_key_buffer_size+'</font></p>\
						<p><span>query_cache_size</span><input style="width: 70px;" class="bt-input-text mr5" name="query_cache_size" value="'+query_cache_size+'" type="number" >MB, <font>'+lan.soft.mysql_set_query_cache_size+'</font></p>\
						<p><span>tmp_table_size</span><input style="width: 70px;" class="bt-input-text mr5" name="tmp_table_size" value="'+tmp_table_size+'" type="number" >MB, <font>'+lan.soft.mysql_set_tmp_table_size+'</font></p>\
						<p><span>innodb_buffer_pool_size</span><input style="width: 70px;" class="bt-input-text mr5" name="innodb_buffer_pool_size" value="'+innodb_buffer_pool_size+'" type="number" >MB, <font>'+lan.soft.mysql_set_innodb_buffer_pool_size+'</font></p>\
						<p><span>innodb_log_buffer_size</span><input style="width: 70px;" class="bt-input-text mr5" name="innodb_log_buffer_size" value="'+innodb_log_buffer_size+'" type="number">MB, <font>'+lan.soft.mysql_set_innodb_log_buffer_size+'</font></p>\
						<p style="display:none;"><span>innodb_additional_mem_pool_size</span><input style="width: 70px;" class="bt-input-text mr5" name="innodb_additional_mem_pool_size" value="'+innodb_additional_mem_pool_size+'" type="number" >MB</p>\
						<p><span>sort_buffer_size</span><input style="width: 70px;" class="bt-input-text mr5" name="sort_buffer_size" value="'+(sort_buffer_size * 1024)+'" type="number" >KB * '+lan.soft.mysql_set_conn+', <font>'+lan.soft.mysql_set_sort_buffer_size+'</font></p>\
						<p><span>read_buffer_size</span><input style="width: 70px;" class="bt-input-text mr5" name="read_buffer_size" value="'+(read_buffer_size * 1024)+'" type="number" >KB * '+lan.soft.mysql_set_conn+', <font>'+lan.soft.mysql_set_read_buffer_size+' </font></p>\
						<p><span>read_rnd_buffer_size</span><input style="width: 70px;" class="bt-input-text mr5" name="read_rnd_buffer_size" value="'+(read_rnd_buffer_size * 1024)+'" type="number" >KB * '+lan.soft.mysql_set_conn+', <font>'+lan.soft.mysql_set_read_rnd_buffer_size+' </font></p>\
						<p><span>join_buffer_size</span><input style="width: 70px;" class="bt-input-text mr5" name="join_buffer_size" value="'+(join_buffer_size * 1024)+'" type="number" >KB * '+lan.soft.mysql_set_conn+', <font>'+lan.soft.mysql_set_join_buffer_size+'</font></p>\
						<p><span>thread_stack</span><input style="width: 70px;" class="bt-input-text mr5" name="thread_stack" value="'+(thread_stack * 1024)+'" type="number" >KB * '+lan.soft.mysql_set_conn+', <font>'+lan.soft.mysql_set_thread_stack+'</font></p>\
						<p><span>binlog_cache_size</span><input style="width: 70px;" class="bt-input-text mr5" name="binlog_cache_size" value="'+(binlog_cache_size * 1024)+'" type="number" >KB * '+lan.soft.mysql_set_conn+', <font>'+lan.soft.mysql_set_binlog_cache_size+'</font></p>\
						<p><span>thread_cache_size</span><input style="width: 70px;" class="bt-input-text mr5" name="thread_cache_size" value="'+rdata.mem.thread_cache_size+'" type="number" ><font> '+lan.soft.mysql_set_thread_cache_size+'</font></p>\
						<p><span>table_open_cache</span><input style="width: 70px;" class="bt-input-text mr5" name="table_open_cache" value="'+rdata.mem.table_open_cache+'" type="number" > <font>'+lan.soft.mysql_set_table_open_cache+'</font></p>\
						<p><span>max_connections</span><input style="width: 70px;" class="bt-input-text mr5" name="max_connections" value="'+rdata.mem.max_connections+'" type="number" ><font> '+lan.soft.mysql_set_max_connections+'</font></p>\
						<div style="margin-top:10px; padding-right:15px" class="text-right"><button class="btn btn-success btn-sm mr5" onclick="ReBootMySqld()">'+lan.soft.mysql_set_restart+'</button><button class="btn btn-success btn-sm" onclick="SetMySQLConf()">'+lan.public.save+'</button></div>\
					</div>'
		
		$(".soft-man-con").html(memCon);
		
		$(".conf_p input[name*='size'],.conf_p input[name='max_connections'],.conf_p input[name='thread_stack']").change(function(){
			ComMySqlMem();
		});
		
		$(".conf_p select[name='mysql_set']").change(function(){
			MySQLMemOpt($(this).val());
			ComMySqlMem();
		});
		
	});
}

//重启MySQL
function ReBootMySqld(){
	var loadT = layer.msg(lan.get('service_the',[lan.bt.restart,'MySQLd']),{icon:16,time:0,shade:0.3});
	$.post('/system?action=ServiceAdmin','name=mysqld&type=restart',function(rdata){
		layer.close(loadT);
		layer.msg(rdata.msg,{icon:rdata.status?1:2});
	});
}

//计算MySQL内存开销
function ComMySqlMem(){
	var key_buffer_size = parseInt($("input[name='key_buffer_size']").val());
	var query_cache_size = parseInt($("input[name='query_cache_size']").val());
	var tmp_table_size = parseInt($("input[name='tmp_table_size']").val());
	var innodb_buffer_pool_size = parseInt($("input[name='innodb_buffer_pool_size']").val());
	var innodb_additional_mem_pool_size = parseInt($("input[name='innodb_additional_mem_pool_size']").val());
	var innodb_log_buffer_size = parseInt($("input[name='innodb_log_buffer_size']").val());
	
	var sort_buffer_size = $("input[name='sort_buffer_size']").val() / 1024;
	var read_buffer_size = $("input[name='read_buffer_size']").val() / 1024;
	var read_rnd_buffer_size = $("input[name='read_rnd_buffer_size']").val() / 1024;
	var join_buffer_size = $("input[name='join_buffer_size']").val() / 1024;
	var thread_stack = $("input[name='thread_stack']").val() / 1024;
	var binlog_cache_size = $("input[name='binlog_cache_size']").val() / 1024;
	var max_connections = $("input[name='max_connections']").val();
	
	var a = key_buffer_size + query_cache_size + tmp_table_size + innodb_buffer_pool_size + innodb_additional_mem_pool_size + innodb_log_buffer_size
	var b = sort_buffer_size + read_buffer_size + read_rnd_buffer_size + join_buffer_size + thread_stack + binlog_cache_size
	var memSize = a  + max_connections * b
	$("input[name='memSize']").val(memSize.toFixed(2));
}

//MySQL内存优化方案
function MySQLMemOpt(opt){
	var query_size = parseInt($("input[name='query_cache_size']").val());
	switch(opt){
		case '1':
			$("input[name='key_buffer_size']").val(128);
			if(query_size) $("input[name='query_cache_size']").val(64);
			$("input[name='tmp_table_size']").val(64);
			$("input[name='innodb_buffer_pool_size']").val(256);
			$("input[name='sort_buffer_size']").val(768);
			$("input[name='read_buffer_size']").val(768);
			$("input[name='read_rnd_buffer_size']").val(512);
			$("input[name='join_buffer_size']").val(1024);
			$("input[name='thread_stack']").val(256);
			$("input[name='binlog_cache_size']").val(64);
			$("input[name='thread_cache_size']").val(64);
			$("input[name='table_open_cache']").val(128);
			$("input[name='max_connections']").val(100);
			break;
		case '2':
			$("input[name='key_buffer_size']").val(256);
			if(query_size) $("input[name='query_cache_size']").val(128);
			$("input[name='tmp_table_size']").val(384);
			$("input[name='innodb_buffer_pool_size']").val(384);
			$("input[name='sort_buffer_size']").val(768);
			$("input[name='read_buffer_size']").val(768);
			$("input[name='read_rnd_buffer_size']").val(512);
			$("input[name='join_buffer_size']").val(2048);
			$("input[name='thread_stack']").val(256);
			$("input[name='binlog_cache_size']").val(64);
			$("input[name='thread_cache_size']").val(96);
			$("input[name='table_open_cache']").val(192);
			$("input[name='max_connections']").val(200);
			break;
		case '3':
			$("input[name='key_buffer_size']").val(384);
			if(query_size) $("input[name='query_cache_size']").val(192);
			$("input[name='tmp_table_size']").val(512);
			$("input[name='innodb_buffer_pool_size']").val(512);
			$("input[name='sort_buffer_size']").val(1024);
			$("input[name='read_buffer_size']").val(1024);
			$("input[name='read_rnd_buffer_size']").val(768);
			$("input[name='join_buffer_size']").val(2048);
			$("input[name='thread_stack']").val(256);
			$("input[name='binlog_cache_size']").val(128);
			$("input[name='thread_cache_size']").val(128);
			$("input[name='table_open_cache']").val(384);
			$("input[name='max_connections']").val(300);
			break;
		case '4':
			$("input[name='key_buffer_size']").val(512);
			if(query_size) $("input[name='query_cache_size']").val(256);
			$("input[name='tmp_table_size']").val(1024);
			$("input[name='innodb_buffer_pool_size']").val(1024);
			$("input[name='sort_buffer_size']").val(2048);
			$("input[name='read_buffer_size']").val(2048);
			$("input[name='read_rnd_buffer_size']").val(1024);
			$("input[name='join_buffer_size']").val(4096);
			$("input[name='thread_stack']").val(384);
			$("input[name='binlog_cache_size']").val(192);
			$("input[name='thread_cache_size']").val(192);
			$("input[name='table_open_cache']").val(1024);
			$("input[name='max_connections']").val(400);
			break;
		case '5':
			$("input[name='key_buffer_size']").val(1024);
			if(query_size) $("input[name='query_cache_size']").val(384);
			$("input[name='tmp_table_size']").val(2048);
			$("input[name='innodb_buffer_pool_size']").val(4096);
			$("input[name='sort_buffer_size']").val(4096);
			$("input[name='read_buffer_size']").val(4096);
			$("input[name='read_rnd_buffer_size']").val(2048);
			$("input[name='join_buffer_size']").val(8192);
			$("input[name='thread_stack']").val(512);
			$("input[name='binlog_cache_size']").val(256);
			$("input[name='thread_cache_size']").val(256);
			$("input[name='table_open_cache']").val(2048);
			$("input[name='max_connections']").val(500);
			break;
	}
}

//设置MySQL配置参数
function SetMySQLConf(){
	$.post('/system?action=GetMemInfo','',function(memInfo){
		//var memSize = memInfo['memTotal'];
		//var setSize = parseInt($("input[name='memSize']").val());
		//if(memSize < setSize){
		//	var msg = lan.soft.mysql_set_err.replace('{1}',memSize).replace('{2}',setSize);
		//	layer.msg(msg,{icon:2,time:5000});
		//	return;
		//}
		var query_cache_size = parseInt($("input[name='query_cache_size']").val());
		var query_cache_type = 0;
		if(query_cache_size > 0){
			query_cache_type = 1;
		}
		var data = {
			key_buffer_size:parseInt($("input[name='key_buffer_size']").val()),
			query_cache_size:query_cache_size,
			query_cache_type:query_cache_type,
			tmp_table_size:parseInt($("input[name='tmp_table_size']").val()),
			max_heap_table_size:parseInt($("input[name='tmp_table_size']").val()),
			innodb_buffer_pool_size:parseInt($("input[name='innodb_buffer_pool_size']").val()),
			innodb_log_buffer_size:parseInt($("input[name='innodb_log_buffer_size']").val()),
			sort_buffer_size:parseInt($("input[name='sort_buffer_size']").val()),
			read_buffer_size:parseInt($("input[name='read_buffer_size']").val()),
			read_rnd_buffer_size:parseInt($("input[name='read_rnd_buffer_size']").val()),
			join_buffer_size:parseInt($("input[name='join_buffer_size']").val()),
			thread_stack:parseInt($("input[name='thread_stack']").val()),
			binlog_cache_size:parseInt($("input[name='binlog_cache_size']").val()),
			thread_cache_size:parseInt($("input[name='thread_cache_size']").val()),
			table_open_cache:parseInt($("input[name='table_open_cache']").val()),
			max_connections:parseInt($("input[name='max_connections']").val())
		};
		
		$.post('/database?action=SetDbConf',data,function(rdata){
			layer.msg(rdata.msg,{icon:rdata.status?1:2});	
		});
	})
}

//转换单们到MB
function ToSizeM(byteLen){
	var a = parseInt(byteLen) / 1024 /1024;
	return a || 0;
}

//设置二进制日志
function SetBinLog(){
	var loadT = layer.msg(lan.public.the,{icon:16,time:0,shade:0.3});
	$.post('/database?action=BinLog',"",function(rdata){
		layer.close(loadT);
		layer.msg(rdata.msg,{icon:rdata.status?1:5});
		mysqlLog();
	});
}

//清空日志
function closeMySqlLog(){
	var loadT = layer.msg(lan.public.the,{icon:16,time:0,shade:0.3});
	$.post('/database?action=GetErrorLog',"close=1",function(rdata){
		layer.close(loadT);
		layer.msg(rdata.msg,{icon:rdata.status?1:5});
		mysqlLog();
	});
}

//数据库端口
function changeMySQLPort(act){
	if(act != undefined){
		layer.confirm(lan.soft.mysql_port_title,{closeBtn:2,icon:3},function(){
			var port = $("#dataport").val();
			var data = 'port='+port;
			var loadT = layer.msg(lan.public.the,{icon:16,time:0,shade: [0.3, '#000']});
			$.post('/database?action=SetMySQLPort',data,function(rdata){
				layer.close(loadT)
				layer.msg(rdata.msg,{icon:rdata.status?1:5});
			});
		});
		return;
	}
	
	$.post('/database?action=GetMySQLInfo','',function(rdata){
		var LimitCon = '<p class="conf_p">\
							<input id="dataport" class="phpUploadLimit bt-input-text mr20" type="number" value="'+rdata.port+'" name="dataport">\
							<button style="margin-top: -1px;" class="btn btn-success btn-sm" onclick="changeMySQLPort(1)">'+lan.public.edit+'</button>\
						</p>';
						
		$(".soft-man-con").html(LimitCon);
	});
}


//软件切换版本
function softChangeVer(name,version){
	if(name == "mysqld") name = "mysql";
	var veropt = version.split("|");
	var SelectVersion = '';
	for(var i=0; i<veropt.length; i++){
		SelectVersion += '<option>'+name+' '+veropt[i]+'</option>';
	}
	
	var body = "<div class='ver line'><span class='tname'>"+lan.soft.select_version+"</span><select id='selectVer' class='bt-input-text mr20' name='phpVersion' style='width:160px'>";
	body += SelectVersion+'</select><button class="btn btn-success btn-sm">'+lan.soft.version_to+'</button></div>';
	
	if(name == 'mysql'){
		body += "<ul class='help-info-text c7 ptb15'><li style='color:red;'>"+lan.soft.mysql_f+"</li></ul>"
	}
	
	$(".soft-man-con").html(body);
	$(".btn-success").click(function(){
		var ver = $("#selectVer").val();
		oneInstall(name,ver.split(" ")[1]);
	});
	selectChange();
}

//phpmyadmin切换php版本
function phpVer(name,version){
	$.post('/site?action=GetPHPVersion',function(rdata){
		var body = "<div class='ver line'><span class='tname'>"+lan.soft.php_version+"</span><select id='get' class='bt-input-text mr20' name='phpVersion' style='width:110px'>";
		var optionSelect = '';
		for(var i=0;i<rdata.length;i++){
			optionSelect = rdata[i].version == version?'selected':'';
			body += "<option value='"+ rdata[i].version +"' "+ optionSelect +">"+ rdata[i].name +"</option>"
		}
		body += '</select><button class="btn btn-success btn-sm" onclick="phpVerChange(\'phpversion\',\'get\')">'+lan.public.save+'</button></div>';
		$(".soft-man-con").html(body);
	})
}
function phpVerChange(type,msg){
	var data = type + '=' + $("#" + msg).val();
	var loadT = layer.msg(lan.public.the,{icon:16,time:0,shade: [0.3, '#000']});
	$.post('/ajax?action=setPHPMyAdmin',data,function(rdata){
		layer.closeAll();
		layer.msg(rdata.msg,{icon:rdata.status?1:2});
		if(rdata.status){
			setTimeout(function(){
				window.location.reload();
			},3000);
		}
	})
}
//phpmyadmin安全设置
function safeConf(name,port,auth){
	var con = '<div class="ver line">\
						<span style="margin-right:10px">'+lan.soft.pma_port+'</span>\
						<input class="bt-input-text phpmyadmindk mr20" name="Name" id="pmport" value="'+port+'" placeholder="'+lan.soft.pma_port_title+'" maxlength="5" type="number">\
						<button class="btn btn-success btn-sm" onclick="phpmyadminport()">'+lan.public.save+'</button>\
					</div>\
					<div class="user_pw_tit">\
						<span class="tit">'+lan.soft.pma_pass+'</span>\
						<span class="btswitch-p"><input class="btswitch btswitch-ios" id="phpmyadminsafe" type="checkbox" '+(auth?'checked':'')+'>\
						<label class="btswitch-btn phpmyadmin-btn" for="phpmyadminsafe" onclick="phpmyadminSafe()"></label>\
						</span>\
					</div>\
					<div class="user_pw">\
						<p><span>'+lan.soft.pma_user+'</span><input id="username_get" class="bt-input-text" name="username_get" value="" type="text" placeholder="'+lan.soft.edit_empty+'"></p>\
						<p><span>'+lan.soft.pma_pass1+'</span><input id="password_get_1" class="bt-input-text" name="password_get_1" value="" type="password" placeholder="'+lan.soft.edit_empty+'"></p>\
						<p><span>'+lan.soft.pma_pass2+'</span><input id="password_get_2" class="bt-input-text" name="password_get_1" value="" type="password" placeholder="'+lan.soft.edit_empty+'"></p>\
						<p><button class="btn btn-success btn-sm" onclick="phpmyadmin(\'get\')">'+lan.public.save+'</button></p>\
					</div>\
					<ul class="help-info-text c7"><li>'+lan.soft.pma_ps+'</li></ul>';
	$(".soft-man-con").html(con);
	if(auth){
		$(".user_pw").show();
	}
}


//修改phpmyadmin端口
function phpmyadminport(){
	var pmport = $("#pmport").val();
	if(pmport < 80 || pmport > 65535){
		layer.msg(lan.firewall.port_err,{icon:2});
		return;
	}
	var data = 'port=' + pmport;
	var loadT = layer.msg(lan.public.the,{icon:16,time:0,shade: [0.3, '#000']});
	$.post('/ajax?action=setPHPMyAdmin',data,function(rdata){
		layer.close(loadT);
		layer.msg(rdata.msg,{icon:rdata.status?1:2});
	});
}
//phpmyadmin二级密码
function phpmyadminSafe(){
	var stat = $("#phpmyadminsafe").prop("checked");
	if(stat) {
		$(".user_pw").hide();
		phpmyadmin('close');
	}else{
		 $(".user_pw").show();
	}
	
}


//设置phpmyadmin二级密码
function phpmyadmin(msg){
	type = 'password';
	if(msg == 'close'){
		password_1 = msg;
		username = msg;
		layer.confirm(lan.soft.pma_pass_close,{closeBtn:2,icon:3},function(){
			var data = type + '=' + msg + '&siteName=phpmyadmin';
			var loadT = layer.msg(lan.public.the,{icon:16,time:0,shade: [0.3, '#000']});
			$.post('/ajax?action=setPHPMyAdmin',data,function(rdata){
				layer.close(loadT);
				layer.msg(rdata.msg,{icon:rdata.status?1:2});
			});
		});
		return;
	}else{
		username = $("#username_get").val()
		password_1 = $("#password_get_1").val()
		password_2 = $("#password_get_2").val()
		if(username.length < 1 || password_1.length < 1){
			layer.msg(lan.soft.pma_pass_empty,{icon:2});
			return;
		}
		if(password_1 != password_2){
			layer.msg(lan.bt.pass_err_re,{icon:2});
			return;
		}
	}
	msg = password_1 + '&username='+username + '&siteName=phpmyadmin';
	var data = type + '=' + msg;
	var loadT = layer.msg(lan.public.the,{icon:16,time:0,shade: [0.3, '#000']});
	$.post('/ajax?action=setPHPMyAdmin',data,function(rdata){
		layer.close(loadT);
		layer.msg(rdata.msg,{icon:rdata.status?1:2});
	});
}
//首页软件列表
function indexsoft(){
	var loadT = layer.msg(lan.soft.get_list,{icon:16,time:0,shade: [0.3, '#000']});
	$.post('/plugin?action=getPluginList','display=1',function(rdata){
		layer.close(loadT);
		var con = '';
		for(var i=0;i<rdata['data'].length - 1;i++){
			var len = rdata.data[i].versions.length;
			var version_info = '';
			for(var j=0;j<len;j++){
              	if(rdata.data[i].versions[j].status) continue;
             	version_info += rdata.data[i].versions[j].version + '|';
            }
          	if(version_info != ''){
             	 version_info = version_info.substring(0,version_info.length-1);
            }
			if(rdata.data[i].display){
				var isDisplay = false;
				if(rdata.data[i].name != 'php'){
					for(var n=0; n<len; n++){
						if(rdata.data[i].versions[n].status == true){
							isDisplay = true;
							var version = rdata.data[i].versions[n].version;
							if(rdata.data[i].versions[n].run == true){
								state='<span style="color:#20a53a" class="glyphicon glyphicon-play"></span>'
							}
							else{
								state='<span style="color:red" class="glyphicon glyphicon-pause"></span>'
							}
						}
					}
					if(isDisplay){
						var clickName = 'SoftMan';
						if(rdata.data[i].tip == 'lib'){
							clickName = 'PluginMan';
							version_info = rdata.data[i].title;
						} 
						
						con += '<div class="col-sm-3 col-md-3 col-lg-3" data-id="'+rdata.data[i].pid+'">\
									<span class="spanmove"></span>\
									<div onclick="' + clickName + '(\''+rdata.data[i].name+'\',\''+version_info+'\')">\
									<div class="image"><img src="/static/img/soft_ico/ico-'+rdata.data[i].name+'.png"></div>\
									<div class="sname">'+rdata.data[i].title+' '+version+state+'</div>\
									</div>\
								</div>'
					}
				}
				else{
					for(var n=0; n<len; n++){
						if(rdata.data[i].versions[n].status == true){
							var version = rdata.data[i].versions[n].version;
							if(rdata.data[i].versions[n].run == true){
								state='<span style="color:#20a53a" class="glyphicon glyphicon-play"></span>'
							}
							else{
								state='<span style="color:red" class="glyphicon glyphicon-pause"></span>'
							}
						}
						if(rdata.data[i].versions[n].display == true ){
							con += '<div class="col-sm-3 col-md-3 col-lg-3" data-id="'+rdata.data[i].pid+'">\
								<span class="spanmove"></span>\
								<div onclick="phpSoftMain(\''+rdata.data[i].versions[n].version+'\','+n+')">\
								<div class="image"><img src="/static/img/soft_ico/ico-'+rdata.data[i].name+'.png"></div>\
								<div class="sname">'+rdata.data[i].title+' '+rdata.data[i].versions[n].version+state+'</div>\
								</div>\
							</div>'
						}
					}
				}
			}
		}
		$("#indexsoft").html(con);
		//软件位置移动
		var softboxlen = $("#indexsoft > div").length;
		var softboxsum = 12;
		var softboxcon = '';
		var softboxn =softboxlen;
		if(softboxlen <= softboxsum){
			for(var i=0;i<softboxsum-softboxlen;i++){
				softboxn +=1000;
				softboxcon +='<div class="col-sm-3 col-md-3 col-lg-3 no-bg" data-id="'+softboxn+'"></div>'
			}
			$("#indexsoft").append(softboxcon);
		}
		$("#indexsoft").dragsort({ dragSelector: ".spanmove", dragBetween: true, dragEnd: saveOrder, placeHolderTemplate: "<div class='col-sm-3 col-md-3 col-lg-3 dashed-border'></div>" });

		function saveOrder() {
			var data = $("#indexsoft > div").map(function() { return $(this).attr("data-id"); }).get();
			var ssort = data.join("|");
			$("input[name=list1SortOrder]").val(ssort);
			$.post("/plugin?action=savePluginSort",'ssort=' + ssort,function(rdata){});
		};
	});
}

//插件设置菜单
function PluginMan(name,title){
	loadT = layer.msg(lan.soft.menu_temp,{icon:16,time:0,shade: [0.3, '#000']});
	$.get('/plugin?action=getConfigHtml&name=' + name,function(rhtml){
		layer.close(loadT);
		if(rhtml.status === false){
			if(name == "phpguard"){
				layer.msg(lan.soft.menu_phpsafe,{icon:1})
			}
			else{
				layer.msg(rhtml.msg,{icon:2});
			}
			return;
		}
		layer.open({
			type: 1,
			shift: 5,
			offset: '20%',
			closeBtn: 2,
			area: '700px', 
			title: ''+ title,
			content: rhtml
		});
		rcode = rhtml.split('<script type="javascript/text">')[1]
		if(!rcode) rcode = rhtml.split('<script type="text/javascript">')[1]
		rcode = rcode.replace('</script>','');
		setTimeout(function(){
			if(!!(window.attachEvent && !window.opera)){ 
				execScript(rcode); 
			}else{
				window.eval(rcode);
			}
		},200)
		
	});
}


//设置插件
function SetPluginConfig(name,param,def){
	if(def == undefined) def = 'SetConfig';
	loadT = layer.msg(lan.config.config_save,{icon:16,time:0,shade: [0.3, '#000']});
	$.post('/plugin?action=a&name='+name+'&s=' + def,param,function(rdata){
		layer.close(loadT);
		layer.msg(rdata.msg,{icon:rdata.status?1:2});
	});
}


//取七牛文件列表
function GetFileList(name){
	var loadT = layer.msg(lan.soft.qiniu_lise,{icon:16,time:0,shade: [0.3, '#000']});
	$.get('/ajax?action=GetQiniuFileList&name='+name,function(rdata){
		layer.close(loadT);
		if(rdata.status === false){
			layer.msg(rdata.msg,{icon:2});
			return;
		}
		
		var tBody = ''
		for(var i=0;i<rdata.length;i++){
			tBody += "<tr>\
						<td>"+rdata[i].key+"</td>\
						<td>"+rdata[i].mimeType+"</td>\
						<td>"+ToSize(rdata[i].fsize)+"</td>\
						<td>"+getLocalTime(rdata[i].putTime)+"</td>\
					</tr>"
		}
		
		layer.open({
			type: 1,
			skin: 'demo-class',
			area: '700px',
			title: lan.soft.qiniu_file_title,
			closeBtn: 2,
			shift: 0,
			content: "<div class='divtable' style='margin:17px'>\
						<table width='100%' class='table table-hover'>\
							<thead>\
								<tr>\
									<th>"+lan.soft.qiniu_th1+"</th>\
									<th>"+lan.soft.qiniu_th2+"</th>\
									<th>"+lan.soft.qiniu_th3+"</th>\
									<th>"+lan.soft.qiniu_th4+"</th>\
								</tr>\
							</thead>\
							<tbody class='list-list'>"+tBody+"</tbody>\
						</table>\
					</div>"
		});
	});
}

//取软件列表
function GetSList(isdisplay){
	if(isdisplay !== true){
		var loadT = layer.msg(lan.soft.get_list,{icon:16,time:0,shade: [0.3, '#000']})
	}
	if(!isdisplay || isdisplay === true)
		isdisplay = getCookie('p'+getCookie('softType'));
		if(isdisplay == true || isdisplay == 'true') isdisplay = 1;
	
	var search = $("#SearchValue").val();
	if(search != ''){
		search = '&search=' + search;
	}
	var type = '';
	var istype = getCookie('softType');
	if(istype == 'undefined' || istype == 'null' || !istype) {
		istype = '0';
	}
	type = '&type='+istype;
	var page = '';
	if(isdisplay){
		page = '&p='+isdisplay;
		setCookie('p'+getCookie('softType'),isdisplay);
	}
	
	$.post('/plugin?action=getPluginList&tojs=GetSList'+search+type+page,'',function(rdata){
		layer.close(loadT);
		var tBody = '';
		var sBody = '';
		var pBody = '';
		
		for(var i=0;i<rdata.type.length;i++){
			var c = '';
			if(istype == rdata.type[i].type){
				c = 'class="on"';
			}
			tBody += '<span typeid="'+rdata.type[i].type+'" '+c+'>'+rdata.type[i].title+'</span>';
		}
		
		$(".softtype").html(tBody);
		$("#softPage").html(rdata.page);
		$("#softPage .Pcount").css({"position":"absolute","left":"0"})
		
		$(".task").text(rdata.data[rdata.length - 1]);
		for(var i=0;i<rdata.data.length - 1;i++){
			var len = rdata.data[i].versions.length;
          	var version_info = '';
			var version = '';
			var softPath ='';
			var titleClick = '';
			var state = '';
			var indexshow = '';
			var checked = '';
			checked = rdata.data[i].display? 'checked':'';
          	for(var j=0;j<len;j++){
              	if(rdata.data[i].versions[j].status) continue;
             	version_info += rdata.data[i].versions[j].version + '|';
            }
          	if(version_info != ''){
             	 version_info = version_info.substring(0,version_info.length-1);
            }
			
			var handle = '<a class="btlink" onclick="AddVersion(\''+rdata.data[i].name+'\',\''+version_info+'\',\''+rdata.data[i].tip+'\',this,\''+rdata.data[i].title+'\')">'+lan.soft.install+'</a>';
			var isSetup = false;
			if(rdata.data[i].name != 'php'){
				for(var n=0; n<len; n++){
					if(rdata.data[i].versions[n].status == true){
						isSetup = true;
						if(rdata.data[i].tip == 'lib'){
							var mupdate = (rdata.data[i].versions[n].no == rdata.data[i].versions[n].version)? '': '<a class="btlink" onclick="SoftUpdate(\''+rdata.data[i].name+'\',\''+rdata.data[i].versions[n].version+'\',\''+rdata.data[i].versions[n].version+'\')">更新</a> | ';
							handle = mupdate + '<a class="btlink" onclick="PluginMan(\''+rdata.data[i].name+'\',\''+rdata.data[i].title+'\')">'+lan.soft.setup+'</a> | <a class="btlink" onclick="UninstallVersion(\''+rdata.data[i].name+'\',\''+rdata.data[i].versions[n].version+'\',\''+rdata.data[i].title+'\')">'+lan.soft.uninstall+'</a>';
							titleClick = 'onclick="PluginMan(\''+rdata.data[i].name+'\',\''+rdata.data[i].title+'\')" style="cursor:pointer"';
						}else{
							var mupdate = (rdata.data[i].versions[n].no == rdata.data[i].update[n])? '': '<a class="btlink" onclick="SoftUpdate(\''+rdata.data[i].name+'\',\''+rdata.data[i].versions[n].version+'\',\''+rdata.data[i].update[n]+'\')">更新</a> | ';
							if(rdata.data[i].versions[n].no == '') mupdate = '';
							handle = mupdate + '<a class="btlink" onclick="SoftMan(\''+rdata.data[i].name+'\',\''+version_info+'\')">'+lan.soft.setup+'</a> | <a class="btlink" onclick="UninstallVersion(\''+rdata.data[i].name+'\',\''+rdata.data[i].versions[n].version+'\',\''+rdata.data[i].title+'\')">'+lan.soft.uninstall+'</a>';
							titleClick = 'onclick="SoftMan(\''+rdata.data[i].name+'\',\''+version_info+'\')" style="cursor:pointer"';
						}
						
						version = rdata.data[i].versions[n].version;
						softPath = '<span class="glyphicon glyphicon-folder-open" title="'+rdata.data[i].path+'" onclick="openPath(\''+rdata.data[i].path+'\')"></span>';
						indexshow = '<div class="index-item"><input class="btswitch btswitch-ios" id="index_'+rdata.data[i].name+'" type="checkbox" '+checked+'><label class="btswitch-btn" for="index_'+rdata.data[i].name+'" onclick="toIndexDisplay(\''+rdata.data[i].name+'\',\''+version+'\')"></label></div>';
						if(rdata.data[i].versions[n].run == true){
							state='<span style="color:#20a53a" class="glyphicon glyphicon-play"></span>'
						}
						else{
							state='<span style="color:red" class="glyphicon glyphicon-pause"></span>'
						}
					}
					var isTask = rdata.data[i].versions[n].task;
					if(isTask == '-1'){
						handle = '<a style="color:green;" href="javascript:task();">'+lan.soft.the_install+'</a>'
					}else if(isTask == '0'){
						handle = '<a style="color:#C0C0C0;" href="javascript:task();">'+lan.soft.sleep_install+'</a>'
					}
				}
				var enddate = '<td class="c9 text-center">'+rdata.data[i].end+'</td>';
				if(rdata.data[i].price > 0){
					var price = '<td class="text-center" style="color:#fc6d26">￥'+rdata.data[i].price+'</td>';
					var uninstall = ''
					if(isSetup){
						uninstall = ' | <a class="btlink" onclick="UninstallVersion(\''+rdata.data[i].name+'\',\'1.0\',\''+rdata.data[i].title+'\')">'+lan.soft.uninstall+'</a>'
					}
					if(rdata.data[i].end == '未开通' || rdata.data[i].end == '已到期' || rdata.data[i].end == '待支付'){
						handle = '<a class="btlink" onclick="Renewinstall(\''+rdata.data[i].title+'\',\''+rdata.data[i].product_id+'\')">立即购买</a>' + uninstall
						titleClick = 'onclick="Renewinstall(\''+rdata.data[i].title+'\',\''+rdata.data[i].product_id+'\')" style="cursor:pointer"';
						if(rdata.data[i].end == '已到期') {
							
							handle = '<a class="btlink" onclick="Renewinstall(\''+rdata.data[i].title+'\',\''+rdata.data[i].product_id+'\',1)">立即续费</a>' + uninstall
						}
						enddate = '<td class="c9 text-center">'+rdata.data[i].end+'&nbsp;&nbsp;<span class="glyphicon glyphicon-repeat cursor" onclick="FPStatus()" title="刷新状态"></span></td>';
					}
					if(rdata.data[i].end.indexOf('20') != -1 || rdata.data[i].end == '已到期') enddate = '<td class="c9 text-center">'+rdata.data[i].end+'<a class="btlink" onclick="Renewinstall(\''+rdata.data[i].title+'\',\''+rdata.data[i].product_id+'\',1)"> (续费)</a></td>';
					
				}else{
					var price = '<td class="c9 text-center">免费</td>';
				}
				
				
				sBody += '<tr>'
						+'<td><span '+titleClick+'><img src="/static/img/soft_ico/ico-'+rdata.data[i].name+'.png">'+rdata.data[i].title+' '+version+'</span></td>'
						//+'<td>'+rdata.data[i].versions[0].no+'</td>'
						//+'<td>'+rdata.data[i].type+'</td>'
						+'<td>'+rdata.data[i].ps+'</td>'
						+price
						+enddate
						+'<td>'+softPath+'</td>'
						+'<td>'+state+'</td>'
						+'<td>'+indexshow+'</td>'
						+'<td style="text-align: right;">'+handle+'</td>'
					+'</tr>'
			}
			else{
				var pnum = 0;
				for(var n=0; n<len; n++){
					if(rdata.data[i].versions[n].status == true){
						checked = rdata.data[i].versions[n]['display'] ? "checked":"";
						var mupdate = (rdata.data[i].versions[n].no == rdata.data[i].update[n])? '': '<a class="btlink" onclick="SoftUpdate(\''+rdata.data[i].name+'\',\''+rdata.data[i].versions[n].version+'\',\''+rdata.data[i].update[n]+'\')">更新</a> | ';
						handle = mupdate + '<a class="btlink" onclick="phpSoftMain(\''+rdata.data[i].versions[n].version+'\','+n+')">'+lan.soft.setup+'</a> | <a class="btlink" onclick="UninstallVersion(\''+rdata.data[i].name+'\',\''+rdata.data[i].versions[n].version+'\',\''+rdata.data[i].title+'\')">'+lan.soft.uninstall+'</a>';
						softPath = '<span class="glyphicon glyphicon-folder-open" title="'+rdata.data[i].path+'" onclick="openPath(\''+rdata.data[i].path+"/"+rdata.data[i].versions[n].version.replace(/\./,"")+'\')"></span>';
						titleClick = 'onclick="phpSoftMain(\''+rdata.data[i].versions[n].version+'\','+n+')" style="cursor:pointer"';
						indexshow = '<div class="index-item"><input class="btswitch btswitch-ios" id="index_'+rdata.data[i].name+rdata.data[i].versions[n].version.replace(/\./,"")+'" type="checkbox" '+checked+'><label class="btswitch-btn" for="index_'+rdata.data[i].name+rdata.data[i].versions[n].version.replace(/\./,"")+'" onclick="toIndexDisplay(\''+rdata.data[i].name+'\',\''+rdata.data[i].versions[n].version+'\')"></label></div>';
						if(rdata.data[i].versions[n].run == true){
							state='<span style="color:#20a53a" class="glyphicon glyphicon-play"></span>'
						}
						else{
							state='<span style="color:red" class="glyphicon glyphicon-pause"></span>'
						}
					}
					else{
						handle = '<a class="btlink" onclick="oneInstall(\''+rdata.data[i].name+'\',\''+rdata.data[i].versions[n].version+'\')">'+lan.soft.install+'</a>';
						softPath ='';
						checked = '';
						indexshow = '';
						titleClick ='';
						state = '';
					}
					var pps = rdata.data[i].ps;
					if(rdata.data[i].apache == '2.2' && rdata.data[i].versions[n].fpm == true){
						pps += "<a style='color:red;'>, "+lan.soft.apache22+"</a>";
					}
					
					if(rdata.data[i].apache == '2.2' && rdata.data[i].versions[n].fpm == false) pnum++;
					
					if(rdata.data[i].apache != '2.2' && rdata.data[i].versions[n].fpm == false){
						pps += "<a style='color:red;'>, "+lan.soft.apache24+"</a>";
					}
					
					var isTask = rdata.data[i].versions[n].task;
					if(isTask == '-1'){
						if(rdata.data[i].apache == '2.2') pnum++;

						handle = '<a style="color:green;" href="javascript:task();">'+lan.soft.the_install+'</a>'
					}else if(isTask == '0'){
						if(rdata.data[i].apache == '2.2') pnum++;
						handle = '<a style="color:#C0C0C0;" href="javascript:task();">'+lan.soft.sleep_install+'</a>'
					}
					pBody += '<tr>'
							+'<td><span '+titleClick+'><img src="/static/img/soft_ico/ico-'+rdata.data[i].name+'.png">'+rdata.data[i].title+'-'+rdata.data[i].versions[n].version+'</span></td>'
							//+'<td>'+rdata.data[i].versions[n].no+'</td>'
							//+'<td>'+rdata.data[i].type+'</td>'
							+'<td>'+pps+'</td>'
							+'<td class="c9 text-center">免费</td>'
							+'<td class="c9 text-center">--</td>'
							+'<td>'+softPath+'</td>'
							+'<td>'+state+'</td>'
							+'<td>'+indexshow+'</td>'
							+'<td style="text-align: right;">'+handle+'</td>'
						+'</tr>'
				}
				
				if(pnum > 0){
					setCookie('apacheVersion','2.2');
					setCookie('phpVersion',1);
				}else{
					setCookie('apacheVersion','');
					setCookie('phpVersion',0);
				}
			}
		}
		sBody += pBody;
		$("#softList").html(sBody);
		$(".menu-sub span").click(function(){
			setCookie('softType',$(this).attr('typeid'));
			$(this).addClass("on").siblings().removeClass("on");
			GetSList();
		})
	})
}
//刷新状态
function FPStatus(){
	$.get("/auth?action=flush_pay_status",function(res){
		layer.msg(res.msg,{icon:res.status?"1":"2"})
	})
}
//更新
function SoftUpdate(name,version,update){
	var msg = "<li>建议您在服务器负载闲时进行软件更新.</li>";
	if(name == 'mysql') msg = "<ul style='color:red;'><li>更新数据库有风险,建议在更新前,先备份您的数据库.</li><li>如果您的是云服务器,强烈建议您在更新前做一个快照.</li><li>建议您在服务器负载闲时进行软件更新.</li></ul>";
	SafeMessage('更新['+name+']','更新过程可能会导致服务中断,您真的现在就将['+name+']更新到['+update+']吗?',function(){
		var data = "name="+name+"&version="+version+"&type=0&upgrade=" + update;
		var loadT = layer.msg('正在更新['+name+'-'+version+'],请稍候...',{icon:16,time:0,shade: [0.3, '#000']});
		$.post('/plugin?action=install', data, function(rdata) {
			if(rdata.status){
				GetTaskCount();
				layer.msg('已添加到任务列表,请稍候...',{icon:1});
			}else{
				layer.msg('更新失败!',{icon:2});
			}
			
			layer.close(loadT);
		});
	},msg);
}
//续费
function Renewinstall(pluginName,pid,an){
	if(an === undefined){
		var txt = "开通";
	}
	else{
		var txt = "续费";
	}
	var payhtml = '<div class="libPay" style="padding:15px 30px 30px 30px">\
				<div class="libPay-item f14 plr15 libPay-select">\
					<div class="li-tit c3">类型</div>\
					<div class="li-con c6">\
						<ul class="li-c-item">\
							<li class="active"><span class="item-name pull-left">'+pluginName+'</span><span class="item-info f12 pull-right c7">1款插件</span></li>\
							<li><span class="item-name">升级为专业版</span><span class="item-info f12 pull-right c7">所有插件免费使用</span></li>\
						</ul>\
						<p class="pro-info" style="position:absolute;top:151px;left:42px;color: #FF7301;font-size: 12px;display:none">（专业版过期了需要续费后才能登陆使用或者进SSH执行免费版升级命令来切换成免费版）</p>\
					</div>\
				</div>\
				<div class="libpay-con">\
				</div>\
			</div>';
	layer.open({
			type: 1,
			title: txt + pluginName,
			area: ['616px','680px'],
			closeBtn: 2,
			shadeClose: false,
			content:payhtml
		});
	get_plugin_price(pluginName,pid,1);
	$(".li-c-item li").click(function(){
		var i = $(this).index();
		$(this).addClass("active").siblings().removeClass("active");
		if(i==0){
			get_plugin_price(pluginName,pid,1);
			$(".pro-info").hide();
		}
		else{
			get_product_discount();
			$(".pro-info").show();
		}
	});
	$(".pay-btn-group > li").click(function(){
		$(this).addClass("active").siblings().removeClass("active");
	});
}
//升级为专业版
function updatapro(){
	var payhtml = '<div class="libPay" style="padding:15px 30px 30px 30px">\
				<div class="libpay-con">\
				</div>\
				<p style="position:absolute;bottom:17px;left:0;width:100%;text-align:center;color:red">注：如需购买多台永久授权，请登录宝塔官网购买。<a class="btlink" href="https://www.bt.cn/download/linuxpro.html#price" target="_blank">去宝塔官网</a></p>\
			</div>';
	layer.open({
			type: 1,
			title: '升级专业版，所有插件，免费使用',
			area: ['616px','540px'],
			closeBtn: 2,
			shadeClose: false,
			content:payhtml
		});
	get_product_discount();
	$(".pay-btn-group > li").click(function(){
		$(this).addClass("active").siblings().removeClass("active");
	});
}

//取插件折扣信息
function get_plugin_price(pluginName,pid,an){
	var con = '<div class="libPay-item f14 plr15">\
						<div class="li-tit c4">付款方式</div>\
						<div class="li-con c6" id="Payment"><ul class="pay-btn-group pay-cycle"><li class="pay-cycle-btn active"><span>微信支付</span></li><li class="pay-cycle-btn" onclick="get_plugin_coupon('+pid+')"><span>代金券</span></li></ul></div>\
					</div>\
					<div class="payment-con">\
						<div class="pay-weixin">\
							<div class="libPay-item f14 plr15">\
								<div class="li-tit c4">开通时长</div>\
								<div class="li-con c6" id="PayCycle"><div class="btn-group"></div></div>\
							</div>\
							<div class="lib-price-box text-center"><span class="lib-price-name f14"><b>总计</b></span><span class="price-txt"><b class="sale-price"></b>元</span><s class="cost-price"></s></div>\
							<div class="paymethod">\
								<div class="pay-wx"></div>\
								<div class="pay-wx-info f16 text-center"><span class="wx-pay-ico mr5"></span>微信扫码支付</div>\
							</div>\
						</div>\
						<div class="pay-coupon" style="display:none">\
							<div class="libPay-item f14 plr15" style="height:200px;overflow:auto">\
								<div class="li-tit c4 ">代金券列表</div>\
								<div class="li-con c6" id="couponlist"><div class="btn-group"></div></div>\
							</div>\
							<div class="paymethod-submit text-center">\
								<button class="btn btn-success btn-sm f16" style="width:200px;height:40px;background-color:#999;border-color:#888">提交</button>\
							</div>\
						</div>\
					</div>'
	$(".libpay-con").html("<div class='cloading'>加载中，请稍后</div>");
	$.post('/auth?action=get_plugin_price',{pluginName:pluginName},function(rdata){
		
		if(rdata.status === false){
			//未绑定
			var payhtml = '<div class="libLogin pd20" style="padding-top:100px"><div class="bt-form text-center"><div class="line mb15"><h3 class="c2 f16 text-center mtb20">绑定宝塔官网账号</h3></div><div class="line"><input class="bt-input-text" name="username2" type="text" placeholder="手机" id="p1" aautocomplete="new-password"></div><div class="line"><input autocomplete="new-password" class="bt-input-text" type="password" name="password2"  placeholder="密码" id="p2"></div><div class="line"><input class="login-button" value="登录" type="button" onclick="loginBT(\''+pluginName+'\',\''+pid+'\')"></div><p class="text-right"><a class="btlink" href="https://www.bt.cn/register.html" target="_blank">未有账号，去注册</a></p></div></div>';
			$(".libPay-select").hide();
			$(".libpay-con").html(payhtml);
		}
		else if(an === undefined){
			//同意协议
			var payhtml = '<div class="shuoming pd20"><div class="alert alert-danger f16" style="line-height:30px">注意：您购买的插件只在当前服务器有效。<br>本插件为特价期间，可能存在一定的稳定性问题。<br>有任何问题，欢迎咨询QQ394030111反馈。</div><div class="line text-center"><input id="apply-ps" class="login-button" value="同意" type="button" disabled style="background:#999;border-color:#999;box-shadow:inset 0 1px 2px #999"></div></div>';
			$(".libPay-select").hide();
			$(".libpay-con").html(payhtml);
			var imin=6;
			var timehwnd = setInterval(function countdown(){
				imin--;
				var applyObj = $("#apply-ps");
				if(imin == 0){
					applyObj.prop("value","同意");
					applyObj.removeAttr("disabled");
					applyObj.attr("onclick","anTo('"+pluginName+"','"+pid+"')");
					applyObj.removeAttr("style");
					clearInterval(timehwnd);
				}else{
					applyObj.prop("value","同意("+imin+")");
				}
			},1000);
		}
		else{
			$(".libPay-select").show();
			$(".libpay-con").html(con);
			$("#PayCycle .btn-group").html(rdata);
			$(".pay-cycle li").click(function(){
				var i = $(this).index();
				$(this).addClass("active").siblings().removeClass("active");
				$(".payment-con > div").eq(i).show().siblings().hide();
			});
			$(".btn-group .btn-success").click();
			$(".btn-group .btn").click(function(){
				$(this).addClass("btn-success").siblings().removeClass("btn-success");
			});
		}
	})
}

//取插件优惠券
function get_plugin_coupon(pid){
	var con = '';
	$("#couponlist").html("<div class='cloading'>加载中，请稍后</div>");
	$.post('/auth?action=get_voucher_plugin',{pid:pid},function(rdata){
		if(rdata !=''){
			for(var i=0,l=rdata.length;i<l;i++){
				con += '<li class="pay-cycle-btn" data-code="'+rdata[i].code+'"><span>'+rdata[i].cycle+conver_unit(rdata[i].unit)+'</span></li>';
			}
			$("#couponlist").html('<ul class="pay-btn-group">'+con+'</ul>');
			$(".pay-btn-group > li").click(function(){
				$(this).addClass("active").siblings().removeClass("active");
				$(".paymethod-submit button").css({"background-color":"#20a53a","border-color":"#20a53a"});
			});
			$(".paymethod-submit button").click(function(){
				var code = $("#couponlist .pay-btn-group .active").attr("data-code");
				if(code == undefined){
					layer.msg("请选择代金券");
				}
				else{
					useCoupon_plugin(code,pid);
				}
			})
		}
		else{
			$("#couponlist").html("<p class='text-center' style='margin-top:70px'>暂无代金券</p>");
		}
	})
}
//取专业版代金券
function get_pro_coupon(){
	$("#couponlist").html("<div class='cloading'>加载中，请稍后</div>");
	$.get("/auth?action=get_voucher",function(rdata){
		if(rdata !=null){
			var con = '';
			var len = rdata.length;
			for(var i=0; i<len; i++){
				if(rdata[i].status !=1){
					var cyc = rdata[i].cycle+conver_unit(rdata[i].unit);
					if(rdata[i].cycle == 999){
						cyc = "永久"
					}
					con += '<li class="pay-cycle-btn" data-code="'+rdata[i].code+'"><span>'+cyc+'</span></li>';
				}
			}
			$("#couponlist").html('<ul class="pay-btn-group">'+con+'</ul>');
			$(".pay-btn-group > li").click(function(){
				$(this).addClass("active").siblings().removeClass("active");
				$(".paymethod-submit button").css({"background-color":"#20a53a","border-color":"#20a53a"});
			});
			$(".paymethod-submit button").click(function(){
				var code = $("#couponlist .pay-btn-group .active").attr("data-code");
				if(code == undefined){
					layer.msg("请选择代金券");
				}
				else{
					useCoupon(code);
				}
			})
		}
		else{
			$("#couponlist").html("<p class='text-center' style='margin-top:70px'>暂无代金券</p>");
		}
	})
}
//插件代金券续费
function useCoupon_plugin(code,pid){
	var loadT = layer.msg("提交中，请稍后。",{ icon: 16, time: 0, shade: [0.3, "#000"]});
	$.post("/auth?action=create_order_voucher_plugin",{pid:pid,code:code},function(rdata){
		layer.closeAll();
		layer.msg(rdata.msg);
	})
}
//专业版代金券续费
function useCoupon(code){
	var loadT = layer.msg("提交中，请稍后。",{ icon: 16, time: 0, shade: [0.3, "#000"]});
	$.post("/auth?action=create_order_voucher",{code:code},function(rdata){
		layer.closeAll();
		layer.msg(rdata.msg);
		if(rdata.status === true){
			layer.msg("支付成功！专业版升级中，请勿操作！",{icon: 16, time: 0, shade: [0.3, "#000"]});
			$.get("/system?action=UpdatePro",function(rr){
				show_upVip();
			}).error(function(){
				show_upVip();
			});
		}
	})
}

function show_upVip(){
	layer.closeAll();
	layer.msg("恭喜您，升级完成！",{icon:1});
	setTimeout(function(){window.location.href = '/';},3000);
}

//取专业版产品折扣信息
function get_product_discount(){
	var con = '<div class="libPay-item f14 plr15">\
						<div class="li-tit c4">付款方式</div>\
						<div class="li-con c6" id="Payment"><ul class="pay-btn-group pay-cycle"><li class="pay-cycle-btn active"><span>微信支付</span></li><li class="pay-cycle-btn" onclick="get_pro_coupon()"><span>代金券</span></li></ul></div>\
					</div>\
					<div class="payment-con">\
						<div class="pay-weixin">\
							<div class="libPay-item f14 plr15">\
								<div class="li-tit c4">开通时长</div>\
								<div class="li-con c6" id="PayCycle"></div>\
							</div>\
							<div class="lib-price-box text-center"><span class="lib-price-name f14"><b>总计</b></span><span class="price-txt"><b class="sale-price"></b>元</span><s class="cost-price"></s></div>\
							<div class="paymethod">\
								<div class="pay-wx"></div>\
								<div class="pay-wx-info f16 text-center"><span class="wx-pay-ico mr5"></span>微信扫码支付</div>\
							</div>\
						</div>\
						<div class="pay-coupon" style="display:none">\
							<div class="libPay-item f14 plr15" style="height:200px;overflow:auto">\
								<div class="li-tit c4 ">代金券列表</div>\
								<div class="li-con c6" id="couponlist"><div class="btn-group"></div></div>\
							</div>\
							<div class="paymethod-submit text-center">\
								<button class="btn btn-success btn-sm f16" style="width:200px;height:40px;background-color:#999;border-color:#888">提交</button>\
							</div>\
						</div>\
					</div>'
	$(".libpay-con").html("<div class='cloading'>加载中，请稍后</div>");
	$.get("/auth?action=get_product_discount_by",function(rdata){
		if(rdata !=null){
			var coucon = '';
			var qarr = Object.keys(rdata);
			var qlen = qarr.length;
			//折扣列表
			for(var i=0;i<qlen;i++){
				var j = qarr[i];
				var a = rdata[j].price;
				var b = rdata[j].sprice;
				var c = rdata[j].discount;
				coucon +='<li class="pay-cycle-btn" onclick="getRsCodePro('+a+','+b+','+j+')"><span>'+conver_unit(j)+'</span>'+(c==1?"":'<em>'+c*10+'折</em>')+'</li>';
			}
			$(".libpay-con").html(con);
			$("#PayCycle").html('<ul class="pay-btn-group">'+coucon+'</ul>');
			$(".pay-btn-group li").click(function(){
				$(this).addClass("active").siblings().removeClass("active");
			});
			$(".pay-cycle li").click(function(){
				var i = $(this).index();
				$(this).addClass("active").siblings().removeClass("active");
				$(".payment-con > div").eq(i).show().siblings().hide();
			});
			$("#PayCycle .pay-btn-group li").eq(0).click();
		}
	})
}
//单位转换
function conver_unit(name){
	var unit= '';
	switch (name){
		case "year":
			unit = "年";
			break;
		case "month":
			unit = "个月";
			break;
		case "day":
			unit = "天";
			break;
		case "1":
			unit = "1个月";
			break;
		case "3":
			unit = "3个月";
			break;
		case "6":
			unit = "6个月";
			break;
		case "12":
			unit = "1年";
			break;
		case "24":
			unit = "2年";
			break;
		case "36":
			unit = "3年";
			break;
		case "999":
			unit = "永久";
			break;
	}
	return unit;
}
var wxpayTimeId = 0;

function getRsCode(pid,price,sprice,cycle){
	$(".sale-price").text(price);
	if(price == sprice){
		$(".cost-price").text(sprice+'元').hide();
	}
	else{
		$(".cost-price").text(sprice+'元').show();
	}
	$(".pay-wx").html('<span class="loading">加载中，请稍后</span>');
	$(".libPay").append('<div class="payloadingmask" style="height:100%;width:100%;position:absolute;top:0;left:0;z-index:9;background:#fff;opacity:0"></div>');
	$.post('/auth?action=get_buy_code',{pid:pid,cycle:cycle},function(rdata){
		$(".payloadingmask").remove();
		if(rdata.status === false){
			layer.msg(rdata.msg,{icon:2});
			return;
		}
		$(".pay-wx").html('');
		$(".pay-wx").qrcode(rdata.msg);
		clearInterval(wxpayTimeId);
		wxpayTimeId = setInterval(function(){
			$.post('/auth?action=check_pay_status',{id:pid},function(rdata){
				if(rdata.status) {
					layer.closeAll();
					layer.msg('支付成功!',{icon:1});
					clearInterval(wxpayTimeId);
					return;
				}
			})
		},3000);
		
	});
}
function getRsCodePro(price,sprice,cycle){
	$(".sale-price").text(price);
	if(price == sprice){
		$(".cost-price").text(sprice+'元').hide();
	}
	else{
		$(".cost-price").text(sprice+'元').show();
	}
	$(".pay-wx").html('<span class="loading">加载中，请稍后</span>');
	$(".libPay").append('<div class="payloadingmask" style="height:100%;width:100%;position:absolute;top:0;left:0;z-index:1"></div>');
	$.post('/auth?action=create_order',{cycle:cycle},function(rdata){
		$(".payloadingmask").remove();
		if(rdata.status === false){
			layer.msg(rdata.msg,{icon:2});
			return;
		}
		$(".pay-wx").html('');
		$(".pay-wx").qrcode(rdata.msg);
		clearInterval(wxpayTimeId);
		wxpayTimeId = setInterval(function(){
			$.post('/auth?action=get_re_order_status',function(rdata){
				if(rdata.status) {
					layer.closeAll();
					layer.msg("支付成功！专业版升级中，请勿操作！",{icon: 16, time: 0, shade: [0.3, "#000"]});
					clearInterval(wxpayTimeId);
					$.get("/system?action=UpdatePro",function(rr){
						show_upVip();
					}).error(function(){
						show_upVip();
					});
					return;
				}
			})
		},3000);
		
	});
}

function anTo(pluginName,pid){
	layer.closeAll();
	Renewinstall(pluginName,pid,1);
}

//登陆宝塔官网帐户
function loginBT(pluginName,pid){
	p1 = $("#p1").val();
	p2 = $("#p2").val();
	var loadT = layer.msg(lan.config.token_get,{icon:16,time:0,shade: [0.3, '#000']});
	$.post("/ssl?action=GetToken", "username=" + p1 + "&password=" + p2, function(b){
		layer.close(loadT);
		layer.msg(b.msg, {icon: b.status?1:2});
		if(b.status) {
			layer.closeAll();
			Renewinstall(pluginName,pid);
		}
	});
}

//独立安装
function oneInstall(name,version){
	var isError = false
	if (name == 'pure') name += '-'+version.toLowerCase();
	
	if (name == 'apache' || name == 'nginx'){
		
		$.ajax({
			url:'/ajax?action=GetInstalled',
			type:'get',
			async:false,
			success:function(rdata){
				if(rdata.webserver != name && rdata.webserver != false){
					layer.msg(lan.soft.err_install2,{icon:2})
					isError = true;
					return;
				}
			}
		});
	}
	
	if(name == 'php'){
		if(getCookie('apacheVersion') == '2.2' && getCookie('phpVersion') == 1){
			layer.msg(lan.soft.apache22_err,{icon:5});
			return;
		}
	}
	
	
	var optw = '';
	if(name == 'mysql'){
		optw = "<br><br><li style='color:red;'>"+lan.soft.mysql_f+"</li>"
		var sUrl = '/data?action=getData&table=databases';
		$.ajax({
			url:sUrl,
			type:"GET",
			async:false,
			success:function(dataD){
				if(dataD.data.length > 0) {
					layer.msg(lan.soft.mysql_d,{icon:5,time:5000})
					isError = true;;
				}
			}
		});
	}
	
	if (isError) return;
	var one = layer.open({
		type: 1,
	    title: lan.soft.type_title,
	    area: '350px',
	    closeBtn: 2,
	    shadeClose: true,
	    content:"<div class='bt-form pd20 pb70 c6'>\
			<div class='version line'>"+lan.soft.install_version+"：<span style='margin-left:30px'>"+name+" "+version+"</span>"+optw+"</div>\
	    	<div class='fangshi line'>"+lan.bt.install_type+"：<label data-title='"+lan.bt.install_rpm_title+"'>"+lan.bt.install_rpm+"<input type='checkbox' checked></label><label data-title='"+lan.bt.install_src_title+"'>"+lan.bt.install_src+"<input type='checkbox'></label></div>\
	    	<div class='bt-form-submit-btn'>\
				<button type='button' class='btn btn-danger btn-sm btn-title one-close'>"+lan.public.close+"</button>\
		        <button type='button' id='bi-btn' class='btn btn-success btn-sm btn-title bi-btn'>"+lan.public.submit+"</button>\
	        </div>\
	    </div>"
	})
	$('.fangshi input').click(function(){
		$(this).attr('checked','checked').parent().siblings().find("input").removeAttr('checked');
	});
	$("#bi-btn").click(function(){
		var type = $('.fangshi input').prop("checked") ? '1':'0';
		var data = "name="+name+"&version="+version+"&type="+type;
		var loadT = layer.msg(lan.soft.add_install,{icon:16,time:0,shade: [0.3, '#000']});
		$.post('/files?action=InstallSoft', data, function(rdata) {
			layer.closeAll();
			layer.msg(rdata.msg,{icon:rdata.status?1:2});
			GetSList();
		})
		
	});
	$(".one-close").click(function(){
		layer.close(one);
	})
	InstallTips();
	fly("bi-btn");
}

function AddVersion(name,ver,type,obj,title){
	if(type == "lib"){
		layer.confirm(lan.get('install_confirm',[title,ver]),{icon:3,closeBtn:2},function(){
			$(obj).text(lan.soft.install_the);
			var data = "name="+name;
			var loadT = layer.msg(lan.soft.the_install,{icon:16,time:0,shade: [0.3, '#000']});
			$.post("/plugin?action=install",data,function(rdata){
				layer.close(loadT);
				layer.msg(rdata.msg,{icon:rdata.status?1:2});
				setTimeout(function(){GetSList()},2000)
			});
		});
		return;
	}
	
	
	var titlename = name;
	var veropt = ver.split("|");
	var SelectVersion = '';
	for(var i=0; i<veropt.length; i++){
		SelectVersion += '<option>'+name+' '+veropt[i]+'</option>';
	}
	if(name == 'phpmyadmin' || name == 'nginx' || name == 'apache'){
		var isError = false
		$.ajax({
			url:'/ajax?action=GetInstalled',
			type:'get',
			async:false,
			success:function(rdata){
				if(name == 'nginx'){
					if(rdata.webserver != name.toLowerCase() && rdata.webserver != false){
						layer.msg(lan.soft.err_install1,{icon:2})
						isError = true;
						return;
					}
				}
				if(name == 'apache'){
					if(rdata.webserver != name.toLowerCase() && rdata.webserver != false){
						layer.msg(lan.soft.err_install2,{icon:2})
						isError = true;
						return;
					}
				}
				if(name == 'phpmyadmin'){
					if (rdata.php.length < 1){
						layer.msg(lan.soft.err_install3,{icon:2})
						isError = true;
						return;
					}
					if (!rdata.mysql.setup){
						layer.msg(lan.soft.err_install4,{icon:2})
						isError = true;
						return;
					}
					
				}
			}
		});
		if(isError) return;
	}
	
	layer.open({
		type: 1,
	    title: titlename+lan.soft.install_title,
	    area: '350px',
	    closeBtn: 2,
	    shadeClose: true,
	    content:"<div class='bt-form pd20 pb70 c6'>\
			<div class='version line'>"+lan.soft.install_version+"：<select id='SelectVersion' class='bt-input-text' style='margin-left:30px'>"+SelectVersion+"</select></div>\
	    	<div class='fangshi line'>"+lan.bt.install_type+"：<label data-title='"+lan.bt.install_rpm_title+"'>"+lan.bt.install_rpm+"<input type='checkbox' checked></label><label data-title='"+lan.bt.install_src_title+"'>"+lan.bt.install_src+"<input type='checkbox'></label></div>\
	    	<div class='bt-form-submit-btn'>\
				<button type='button' class='btn btn-danger btn-sm btn-title' onclick='layer.closeAll()'>"+lan.public.close+"</button>\
		        <button type='button' id='bi-btn' class='btn btn-success btn-sm btn-title bi-btn'>"+lan.public.submit+"</button>\
	        </div>\
	    </div>"
	})
	selectChange();
	$('.fangshi input').click(function(){
		$(this).attr('checked','checked').parent().siblings().find("input").removeAttr('checked');
	});
	$("#bi-btn").click(function(){
		var info = $("#SelectVersion").val().toLowerCase();
		var name = info.split(" ")[0];
		var version = info.split(" ")[1];
		var type = $('.fangshi input').prop("checked") ? '1':'0';
		var data = "name="+name+"&version="+version+"&type="+type;

		var loadT = layer.msg(lan.soft.add_install,{icon:16,time:0,shade: [0.3, '#000']});
		$.post("/plugin?action=install",data,function(rdata){
			layer.closeAll();
			layer.msg(rdata.msg,{icon:rdata.status?1:2});
			GetSList();
		});
	});
	InstallTips();
	fly("bi-btn");
}

function selectChange(){
	$("#SelectVersion,#selectVer").change(function(){
		var info = $(this).val();
		var name = info.split(" ")[0];
		var version = info.split(" ")[1];
		max=64
		msg="64M"
		if(name == 'mysql'){
			memSize = getCookie('memSize');
			switch(version){
				case '5.1':
					max = 256;
					msg = '256M';
					break;
				case '8.0':
					max = 5200;
					msg = '6GB';
					break;
				case '5.7':
					max = 1500;
					msg = '2GB';
					break;
				case '5.6':
					max = 800;
					msg = '1GB';
					break;
				case 'AliSQL':
					max = 800;
					msg = '1GB';
					break;
				case 'mariadb_10.0':
					max = 800;
					msg = '1GB';
					break;
				case 'mariadb_10.1':
					max = 1500;
					msg = '2GB';
					break;
			}
			if(memSize < max){
				layer.msg(lan.bt.insatll_mem.replace('{1}',msg).replace('{2}',version),{icon:5});
			}
		}
	});
}


//卸载软件
function UninstallVersion(name,version,title){
	var isError = false
	if(name == 'mysql'){
		var sUrl = '/data?action=getData&table=databases';
		$.ajax({
			url:sUrl,
			type:"GET",
			async:false,
			success:function(dataD){
				if(dataD.data.length > 0) {
					layer.msg(lan.soft.mysql_del_err + '<p style="color:red">强行卸载: curl http://h.bt.cn/mu.sh|bash</p>',{icon:5,time:8000});
					isError = true;;
				}
			}
		});
	}
	if(isError) return;
	layer.confirm(lan.soft.uninstall_confirm.replace('{1}',title).replace('{2}',version),{icon:3,closeBtn:2},function(){
		var data = 'name='+name+'&version='+version;
		var loadT = layer.msg(lan.public.the,{icon:16,time:0,shade: [0.3, '#000']});
		$.post('/plugin?action=unInstall',data,function(rdata){
			layer.close(loadT)
			GetSList();
			layer.msg(rdata.msg,{icon:rdata.status?1:2});
		})
	});
}


//获取插件列表
function GetLibList(){
	var loadT = layer.msg(lan.soft.get_list,{icon:16,time:0,shade: [0.3, '#000']})
	$.post('/ajax?action=GetLibList','',function(rdata){
		layer.close(loadT)
		var tBody = ''
		for(var i=0;i<rdata.length;i++){
			tBody += "<tr>\
						<td>"+rdata[i].name+"</td>\
						<td>"+rdata[i].type+"</td>\
						<td>"+rdata[i].ps+"</td>\
						<td>--</td>\
						<td>"+rdata[i].status+"</td>\
						<td style='text-align: right;'>"+rdata[i].optstr+"</td>\
					</tr>"
		}
		$("#softList").append(tBody);
	});
}


//设置插件
function SetLibConfig(name,action){
	if(action == 1){
		var access_key = $("input[name='access_key']").val();
		var secret_key = $("input[name='secret_key']").val();
		var bucket_name = $("input[name='bucket_name']").val();
		if(access_key.length < 1 || secret_key.length < 1 || bucket_name.length < 1){
			layer.msg(lan.soft.from_err,{icon:2});
			return;
		}
		
		var bucket_domain = $("input[name='bucket_domain']").val();
		var data = 'name='+name+'&access_key='+access_key+'&secret_key='+secret_key+'&bucket_name='+bucket_name+'&bucket_domain='+bucket_domain;
		
		var loadT = layer.msg(lan.soft.lib_the,{icon:16,time:0,shade:[0.3,'#000']});
		$.post('/ajax?action=SetQiniuAS',data,function(rdata){
			layer.close(loadT);
			if(rdata.status) layer.closeAll();
			layer.msg(rdata.msg,{icon:rdata.status?1:2});
		}).error(function(){
			layer.close(loadT);
			layer.msg(lan.public.error,{icon:2});
		});
		return;
	}
	
	if(name == 'beta'){
		neice();
		return;
	}
	
	$.post('/ajax?action=GetQiniuAS','name='+name,function(rdata){
		var keyMsg = rdata.info.key.split('|');
		var secretMsg = rdata.info.secret.split('|');
		var bucketMsg = rdata.info.bucket.split('|');
		var domainMsg = rdata.info.domain.split('|');
		
		var body="<div class='bt-form bingfa pd20 pb70'>"
				+"<p><span class='span_tit'>"+keyMsg[0]+"：</span><input placeholder='"+keyMsg[1]+"' style='width: 300px;' type='text' name='access_key' value='"+rdata.AS[0]+"' />  *"+keyMsg[2]+" "+'<a href="'+rdata.info.help+'" style="color:green" target="_blank"> ['+lan.public.help+']</a>'+"</p>"
				+"<p><span class='span_tit'>"+secretMsg[0]+"：</span><input placeholder='"+secretMsg[1]+"' style='width: 300px;' type='text' name='secret_key' value='"+rdata.AS[1]+"' />  *"+secretMsg[2]+"</p>"
				+"<p><span class='span_tit'>"+bucketMsg[0]+"：</span><input placeholder='"+bucketMsg[1]+"' style='width: 300px;' type='text' name='bucket_name' value='"+rdata.AS[2]+"' />   *"+bucketMsg[2]+"</p>"
				+"<p><span class='span_tit'>"+domainMsg[0]+"：</span><input placeholder='"+domainMsg[1]+"' style='width: 300px;' type='text' name='bucket_domain' value='"+rdata.AS[3]+"' />   *"+domainMsg[2]+"</p>"
			+'<div class="bt-form-submit-btn">'
				+'<button type="button" class="btn btn-danger btn-sm btn-title" onclick="layer.closeAll()">'+lan.public.close+'</button>'
				+'<button type="button" class="btn btn-success btn-sm btn-title" onclick="GetQiniuFileList(\''+name+'\')" style="margin-right: 4px;">'+lan.public.list+'</button>'
				+"<button class='btn btn-success btn-sm btn-title' onclick=\"SetLibConfig('"+name+"',1)\">"+lan.public.save+"</button>"
			+'</div>'
		+"</div>"
		
		layer.open({
			type: 1,
			shift: 5,
			closeBtn: 2,
			area: '700px', 
			title: lan.soft.lib_config+rdata.info.name,
			content: body
			});
	});
}


//安装插件
function InstallLib(name){
	layer.confirm(lan.soft.lib_insatll_confirm.replace('{1}',name),{title:lan.soft.lib_install,icon:3,closeBtn:2}, function() {
		var loadT = layer.msg(lan.soft.lib_install_the,{icon:16,time:0,shade:[0.3,'#000']});
		$.post('/ajax?action=InstallLib','name='+name,function(rdata){
			layer.close(loadT);
			layer.msg(rdata.msg,{icon:rdata.status?1:2});
			if(rdata.status){
				GetSList();
				SetLibConfig(name);
			}
		});
	});
}

//卸载插件
function UninstallLib(name){
	layer.confirm(lan.soft.lib_uninsatll_confirm.replace('{1}',name),{title:lan.soft.lib_uninstall,icon:3,closeBtn:2}, function() {
		var loadT = layer.msg(lan.soft.lib_uninstall_the,{icon:16,time:0,shade:[0.3,'#000']});
		$.post('/ajax?action=UninstallLib','name='+name,function(rdata){
			layer.close(loadT);
			layer.msg(rdata.msg,{icon:rdata.status?1:2});
			if(rdata.status){
				GetSList();
			}
		});
	});
}

//首页显示
function toIndexDisplay(name,version){
	var status = $("#index_"+name).prop("checked")?"0":"1";
	if(name == "php"){
		var verinfo = version.replace(/\./,"");
		status = $("#index_"+name+verinfo).prop("checked")?"0":"1";
	}
	var data= "name="+name+"&status="+status+"&version="+version;
	$.post("plugin?action=setPluginStatus",data,function(rdata){
		if(rdata.status){
			layer.msg(rdata.msg,{icon:1})
		}
	})
}

//刷新缓存
function flush_cache(){
	var loadT = layer.msg(lan.soft.get_list,{icon:16,time:0,shade: [0.3, '#000']})
	$.post('/plugin?action=flush_cache',{},function(rdata){
		layer.close(loadT)
		layer.msg(rdata.msg,{icon:rdata.status?1:2});
	});
}


$(function(){
	if(window.document.location.pathname == '/soft'){
		setInterval(function(){GetSList(true);},5000);
	}
});

updateSoftList();