var num = 0;
//查看任务日志
function GetLogs(id){
	layer.msg(lan.public.the_get,{icon:16,time:0,shade: [0.3, '#000']});
	var data='&id='+id
	$.post('/crontab?action=GetLogs',data,function(rdata){
		layer.closeAll();
		if(!rdata.status) {
			layer.msg(rdata.msg,{icon:2});
			return;
		};
		layer.open({
			type:1,
			title:lan.crontab.task_log_title,
			area: ['60%','500px'], 
			shadeClose:false,
			closeBtn:2,
			content:'<div class="setchmod bt-form pd20 pb70">'
					+'<pre id="crontab-log" style="overflow: auto; border: 0px none; padding: 15px; margin: 0px; height: 410px; background-color: rgb(255, 255, 255);"></pre>'
					+'<div class="bt-form-submit-btn" style="margin-top: 0px;">'
					+'<button type="button" class="btn btn-success btn-sm" onclick="CloseLogs('+id+')">'+lan.public.empty+'</button>'
					+'<button type="button" class="btn btn-danger btn-sm" onclick="layer.closeAll()">'+lan.public.close+'</button>'
				    +'</div>'
					+'</div>'
		});
		
		setTimeout(function(){
			$("#crontab-log").text(rdata.msg);
		},200)
	});
}

function getCronData(){
	var laid=layer.msg(lan.public.the,{icon:16,time:0,shade: [0.3, '#000']});
	$.post('/crontab?action=GetCrontab',"",function(rdata){
		layer.close(laid);
		var cbody="";
		if(rdata == ""){
			cbody="<tr><td colspan='6'>"+lan.crontab.task_empty+"</td></tr>"
		}
		else{
			for(var i=0;i<rdata.length;i++){
				cbody += "<tr>\
							<td><input type='checkbox' onclick='checkSelect();' title='"+rdata[i].name+"' name='id' value='"+rdata[i].id+"'></td>\
							<td>"+rdata[i].name+"</td>\
							<td>"+rdata[i].type+"</td>\
							<td>"+rdata[i].cycle+"</td>\
							<td>"+rdata[i].addtime+"</td>\
							<td>\
								<a href=\"javascript:StartTask("+rdata[i].id+");\" class='btlink'>"+lan.public.exec+"</a> | \
								<a href=\"javascript:OnlineEditFile(0,'/www/server/cron/"+rdata[i].echo+"');\" class='btlink'>"+lan.public.script+"</a> | \
								<a href=\"javascript:GetLogs("+rdata[i].id+");\" class='btlink'>"+lan.public.log+"</a> | \
								<a href=\"javascript:planDel("+rdata[i].id+" ,'"+rdata[i].name.replace('\\','\\\\').replace("'","\\'").replace('"','')+"');\" class='btlink'>"+lan.public.del+"</a>\
							</td>\
						</tr>"
			}
		}
		$('#cronbody').html(cbody);
	});
}

//执行任务脚本
function StartTask(id){
	layer.msg(lan.public.the,{icon:16,time:0,shade: [0.3, '#000']});
	var data='id='+id;
	$.post('/crontab?action=StartTask',data,function(rdata){
		layer.closeAll();
		layer.msg(rdata.msg,{icon:rdata.status?1:2});
	});
}


//清空日志
function CloseLogs(id){
	layer.msg(lan.public.the,{icon:16,time:0,shade: [0.3, '#000']});
	var data='id='+id;
	$.post('/crontab?action=DelLogs',data,function(rdata){
		layer.closeAll();
		layer.msg(rdata.msg,{icon:rdata.status?1:2});
	});
}


//删除
function planDel(id,name){
	SafeMessage(lan.get('del',[name]),lan.crontab.del_task,function(){
			layer.msg(lan.public.the,{icon:16,time:0,shade: [0.3, '#000']});
			var data='id='+id;
			$.post('/crontab?action=DelCrontab',data,function(rdata){
				layer.closeAll();
				layer.msg(rdata.msg,{icon:rdata.status?1:2});
				getCronData();
			});
	});
}


//批量删除
function allDeleteCron(){
	var checkList = $("input[name=id]");
	var dataList = new Array();
	for(var i=0;i<checkList.length;i++){
		if(!checkList[i].checked) continue;
		var tmp = new Object();
		tmp.name = checkList[i].title;
		tmp.id = checkList[i].value;
		dataList.push(tmp);
	}
	SafeMessage(lan.crontab.del_task_all_title,"<a style='color:red;'>"+lan.get('del_all_task',[dataList.length])+"</a>",function(){
		layer.closeAll();
		syncDeleteCron(dataList,0,'');
	});
}

//模拟同步开始批量删除数据库
function syncDeleteCron(dataList,successCount,errorMsg){
	if(dataList.length < 1) {
		layer.msg(lan.get('del_all_task_ok',[successCount]),{icon:1});
		return;
	}
	var loadT = layer.msg(lan.get('del_all_task_the',[dataList[0].name]),{icon:16,time:0,shade: [0.3, '#000']});
	$.ajax({
			type:'POST',
			url:'/crontab?action=DelCrontab',
			data:'id='+dataList[0].id+'&name='+dataList[0].name,
			async: true,
			success:function(frdata){
				layer.close(loadT);
				if(frdata.status){
					successCount++;
					$("input[title='"+dataList[0].name+"']").parents("tr").remove();
				}else{
					if(!errorMsg){
						errorMsg = '<br><p>'+lan.crontab.del_task_err+'</p>';
					}
					errorMsg += '<li>'+dataList[0].name+' -> '+frdata.msg+'</li>'
				}
				
				dataList.splice(0,1);
				syncDeleteCron(dataList,successCount,errorMsg);
			}
	});
}

	
function IsURL(str_url){
	var strRegex = '^(https|http|ftp|rtsp|mms)?://.+';
	var re=new RegExp(strRegex);
	if (re.test(str_url)){
		return (true);
	}else{
		return (false);
	}
}


//提交
function planAdd(){
	var name = $(".planname input[name='name']").val();
	if(name == ''){
		$(".planname input[name='name']").focus();
		layer.msg(lan.crontab.add_task_empty,{icon:2});
		return;
	}
	$("#set-Config input[name='name']").val(name);
	
	var type = $(".plancycle").find("b").attr("val");
	$("#set-Config input[name='type']").val(type);
	
	var where1 = $("#ptime input[name='where1']").val();
	var is1;
	var is2 = 1;
	switch(type){
		case 'day-n':
			is1=31;
			break;
		case 'hour-n':
			is1=23;
			break;
		case 'minute-n':
			is1=59;
			break;
		case 'month':
			is1=31;
			break;
		
	}
	
	if(where1 > is1 || where1 < is2){
		$("#ptime input[name='where1']").focus();
		layer.msg(lan.public.input_err,{icon:2});
		return;
	}
	
	$("#set-Config input[name='where1']").val(where1);
	
	var hour = $("#ptime input[name='hour']").val();
	if(hour > 23 || hour < 0){
		$("#ptime input[name='hour']").focus();
		layer.msg(lan.crontab.input_hour_err,{icon:2});
		return;
	}
	$("#set-Config input[name='hour']").val(hour);
	var minute = $("#ptime input[name='minute']").val();
	if(minute > 59 || minute < 0){
		$("#ptime input[name='minute']").focus();
		layer.msg(lan.crontab.input_minute_err,{icon:2});
		return;
	}
	$("#set-Config input[name='minute']").val(minute);
	
	var save = $("#save").val();
	
	if(save < 0){
		layer.msg(lan.crontab.input_number_err,{icon:2});
		return;
	}
	
	$("#set-Config input[name='save']").val(save);
	
	
	$("#set-Config input[name='week']").val($(".planweek").find("b").attr("val"));
	var sType = $(".planjs").find("b").attr("val");
	var sBody = encodeURIComponent($("#implement textarea[name='sBody']").val());
	
	if(sType == 'toFile'){
		if($("#viewfile").val() == ''){
			layer.msg(lan.crontab.input_file_err,{icon:2});
			return;
		}
	}else{
		if(sBody == ''){
			$("#implement textarea[name='sBody']").focus();
			layer.msg(lan.crontab.input_script_err,{icon:2});
			return;
		}
	}
	
	var urladdress = $("#urladdress").val();
	if(sType == 'toUrl'){
		if(!IsURL(urladdress)){
			layer.msg(lan.crontab.input_url_err,{icon:2});
			$("implement textarea[name='urladdress']").focus();
			return;
		}
	}
	urladdress = encodeURIComponent(urladdress);
	$("#set-Config input[name='urladdress']").val(urladdress);
	$("#set-Config input[name='sType']").val(sType);
	$("#set-Config textarea[name='sBody']").val(decodeURIComponent(sBody));
	
	if(sType == 'site' || sType == 'database'){
		var backupTo = $(".planBackupTo").find("b").attr("val");
		$("#backupTo").val(backupTo);
	}
	
	
	var sName = $("#sName").attr("val");
	
	if(sName == 'backupAll'){
		var alist = $("ul[aria-labelledby='backdata'] li a");
		var dataList = new Array();
		for(var i=1;i<alist.length;i++){
			var tmp = alist[i].getAttribute('value');
			dataList.push(tmp);
		}
		if(dataList.length < 1){
			layer.msg(lan.crontab.input_empty_err,{icon:5});
			return;
		}
		
		allAddCrontab(dataList,0,'');
		return;
	}
	
	$("#set-Config input[name='sName']").val(sName);
	layer.msg(lan.public.the_add,{icon:16,time:0,shade: [0.3, '#000']});
	var data= $("#set-Config").serialize() + '&sBody='+sBody + '&urladdress=' + urladdress;
	$.post('/crontab?action=AddCrontab',data,function(rdata){
		layer.closeAll();
		layer.msg(rdata.msg,{icon:rdata.status?1:2});
		getCronData();
	});
}

//批量添加任务
function allAddCrontab(dataList,successCount,errorMsg){
	if(dataList.length < 1) {
		layer.msg(lan.get('add_all_task_ok',[successCount]),{icon:1});
		return;
	}
	var loadT = layer.msg(lan.get('add',[dataList[0]]),{icon:16,time:0,shade: [0.3, '#000']});
	var sType = $(".planjs").find("b").attr("val");
	var minute = parseInt($("#set-Config input[name='minute']").val());
	var hour = parseInt($("#set-Config input[name='hour']").val());
	var sTitle = (sType == 'site')?lan.crontab.backup_site:lan.crontab.backup_database;
	if(sType == 'logs') sTitle = lan.crontab.backup_log;
	minute += 5;
	if(hour !== '' && minute > 59){
		if(hour >= 23) hour = 0;
		$("#set-Config input[name='hour']").val(hour+1);
		minute = 5;
	}
	$("#set-Config input[name='minute']").val(minute);
	$("#set-Config input[name='name']").val(sTitle + '['+dataList[0]+']');
	$("#set-Config input[name='sName']").val(dataList[0]);
	var pdata = $("#set-Config").serialize() + '&sBody=&urladdress=';
	$.ajax({
			type:'POST',
			url:'/crontab?action=AddCrontab',
			data:pdata,
			async: true,
			success:function(frdata){
				layer.close(loadT);
				if(frdata.status){
					successCount++;
					getCronData();
				}else{
					if(!errorMsg){
						errorMsg = '<br><p>'+lan.crontab.backup_all_err+'</p>';
					}
					errorMsg += '<li>'+dataList[0]+' -> '+frdata.msg+'</li>'
				}
				
				dataList.splice(0,1);
				allAddCrontab(dataList,successCount,errorMsg);
			}
	});
}

$(".dropdown ul li a").click(function(){
	var txt = $(this).text();
	var type = $(this).attr("value");
	$(this).parents(".dropdown").find("button b").text(txt).attr("val",type);
	switch(type){
		case 'day':
			closeOpt();
			toHour();
			toMinute();
			break;
		case 'day-n':
			closeOpt();
			toWhere1(lan.crontab.day);
			toHour();
			toMinute();
			break;
		case 'hour':
			closeOpt();
			toMinute();
			break;
		case 'hour-n':
			closeOpt();
			toWhere1(lan.crontab.hour);
			toMinute();
			break;
		case 'minute-n':
			closeOpt();
			toWhere1(lan.crontab.minute);
			break;
		case 'week':
			closeOpt();
			toWeek();
			toHour();
			toMinute();
			break;
		case 'month':
			closeOpt();
			toWhere1(lan.crontab.sun);
			toHour();
			toMinute();
			break;
		case 'toFile':
			toFile();
			break;
		case 'toShell':
			toShell();
			$(".controls").html(lan.crontab.sbody);
			break;
		case 'rememory':
			rememory();
			$(".controls").html(lan.public.msg);
			break;
		case 'site':
			toBackup('sites');
			$(".controls").html(lan.crontab.backup_site);
			break;
		case 'database':
			toBackup('databases');
			$(".controls").html(lan.crontab.backup_database);
			break;
		case 'logs':
			toBackup('logs');
			$(".controls").html(lan.crontab.log_site);
			break;
		case 'toUrl':
			toUrl();
			$(".controls").html(lan.crontab.url_address);
			break;
	}
})


//备份
function toBackup(type){
	var sMsg = "";
	switch(type){
		case 'sites':
			sMsg = lan.crontab.backup_site;
			sType = "sites";
			break;
		case 'databases':
			sMsg = lan.crontab.backup_database;
			sType = "databases";
			break;
		case 'logs':
			sMsg = lan.crontab.backup_log;
			sType = "sites";
			break;
	}
	var data='type='+sType
	$.post('/crontab?action=GetDataList',data,function(rdata){
		$(".planname input[name='name']").attr('readonly','true').css({"background-color":"#f6f6f6","color":"#666"});
		var sOpt = "";
		if(rdata.data.length == 0){
			layer.msg(lan.public.list_empty,{icon:2})
			return
		}
		for(var i=0;i<rdata.data.length;i++){
			if(i==0){
				$(".planname input[name='name']").val(sMsg+'['+rdata.data[i].name+']');
			}
			sOpt += '<li><a role="menuitem" tabindex="-1" href="javascript:;" value="'+rdata.data[i].name+'">'+rdata.data[i].name+'['+rdata.data[i].ps+']</a></li>';			
		}
		
		var orderOpt = ''
		for (var i=0;i<rdata.orderOpt.length;i++){
			orderOpt += '<li><a role="menuitem" tabindex="-1" href="javascript:;" value="'+rdata.orderOpt[i].value+'">'+rdata.orderOpt[i].name+'</a></li>'
		}
		
		

		var sBody = '<div class="dropdown pull-left mr20">\
					  <button class="btn btn-default dropdown-toggle" type="button" id="backdata" data-toggle="dropdown" style="width:auto">\
						<b id="sName" val="'+rdata.data[0].name+'">'+rdata.data[0].name+'['+rdata.data[0].ps+']</b> <span class="caret"></span>\
					  </button>\
					  <ul class="dropdown-menu" role="menu" aria-labelledby="backdata">\
					  	<li><a role="menuitem" tabindex="-1" href="javascript:;" value="backupAll">'+lan.public.all+'</a></li>\
					  	'+sOpt+'\
					  </ul>\
					</div>\
					<div class="textname pull-left mr20">'+lan.crontab.backup_to+'</div>\
					<div class="dropdown planBackupTo pull-left mr20">\
					  <button class="btn btn-default dropdown-toggle" type="button" id="excode" data-toggle="dropdown" style="width:auto;">\
						<b val="localhost">'+lan.crontab.disk+'</b> <span class="caret"></span>\
					  </button>\
					  <ul class="dropdown-menu" role="menu" aria-labelledby="excode">\
						<li><a role="menuitem" tabindex="-1" href="javascript:;" value="localhost">'+lan.crontab.disk+'</a></li>\
						'+ orderOpt +'\
					  </ul>\
					</div>\
					<div class="textname pull-left mr20">'+lan.crontab.save_new+'</div><div class="plan_hms pull-left mr20 bt-input-text">\
					<span><input type="number" name="save" id="save" value="3" maxlength="4" max="100" min="1"></span>\
					<span class="name">'+lan.crontab.save_num+'</span>\
					</div>';
		$("#implement").html(sBody);
		getselectname();
		$(".dropdown ul li a").click(function(){
			var sName = $("#sName").attr("val");
			if(!sName) return;
			$(".planname input[name='name']").val(sMsg+'['+sName+']');
		});
	});
}


//下拉菜单名称
function getselectname(){
	$(".dropdown ul li a").click(function(){
		var txt = $(this).text();
		var type = $(this).attr("value");
		$(this).parents(".dropdown").find("button b").text(txt).attr("val",type);
	});
}
//清理
function closeOpt(){
	$("#ptime").html('');
}
//星期
function toWeek(){
	var mBody = '<div class="dropdown planweek pull-left mr20">\
					  <button class="btn btn-default dropdown-toggle" type="button" id="excode" data-toggle="dropdown">\
						<b val="1">'+lan.crontab.TZZ1+'</b> <span class="caret"></span>\
					  </button>\
					  <ul class="dropdown-menu" role="menu" aria-labelledby="excode">\
						<li><a role="menuitem" tabindex="-1" href="javascript:;" value="1">'+lan.crontab.TZZ1+'</a></li>\
						<li><a role="menuitem" tabindex="-1" href="javascript:;" value="2">'+lan.crontab.TZZ2+'</a></li>\
						<li><a role="menuitem" tabindex="-1" href="javascript:;" value="3">'+lan.crontab.TZZ3+'</a></li>\
						<li><a role="menuitem" tabindex="-1" href="javascript:;" value="4">'+lan.crontab.TZZ4+'</a></li>\
						<li><a role="menuitem" tabindex="-1" href="javascript:;" value="5">'+lan.crontab.TZZ5+'</a></li>\
						<li><a role="menuitem" tabindex="-1" href="javascript:;" value="6">'+lan.crontab.TZZ6+'</a></li>\
						<li><a role="menuitem" tabindex="-1" href="javascript:;" value="0">'+lan.crontab.TZZ7+'</a></li>\
					  </ul>\
					</div>';
	$("#ptime").html(mBody);
	getselectname()
}
//指定1
function toWhere1(ix){
	var mBody ='<div class="plan_hms pull-left mr20 bt-input-text">\
					<span><input type="number" name="where1" value="3" maxlength="2" max="31" min="0"></span>\
					<span class="name">'+ix+'</span>\
					</div>';
	$("#ptime").append(mBody);
}
//小时
function toHour(){
	var mBody = '<div class="plan_hms pull-left mr20 bt-input-text">\
					<span><input type="number" name="hour" value="1" maxlength="2" max="23" min="0"></span>\
					<span class="name">'+lan.crontab.hour+'</span>\
					</div>';
	$("#ptime").append(mBody);
}

//分钟
function toMinute(){
	var mBody = '<div class="plan_hms pull-left mr20 bt-input-text">\
					<span><input type="number" name="minute" value="30" maxlength="2" max="59" min="0"></span>\
					<span class="name">'+lan.crontab.minute+'</span>\
					</div>';
	$("#ptime").append(mBody);
	
}

//从文件
function toFile(){
	var tBody = '<input type="text" value="" name="file" id="viewfile" onclick="fileupload()" readonly="true">\
				<button class="btn btn-default" onclick="fileupload()">'+lan.public.upload+'</button>';
	$("#implement").html(tBody);
	$(".planname input[name='name']").removeAttr('readonly style').val("");
}

//从脚本
function toShell(){
	var tBody = "<textarea class='txtsjs bt-input-text' name='sBody'></textarea>";
	$("#implement").html(tBody);
	$(".planname input[name='name']").removeAttr('readonly style').val("");
}

//从脚本
function toUrl(){
	var tBody = "<input type='text' style='width:400px; height:34px' class='bt-input-text' name='urladdress' id='urladdress' placeholder='"+lan.crontab.url_address+"' value='http://' />";
	$("#implement").html(tBody);
	$(".planname input[name='name']").removeAttr('readonly style').val("");
}

//释放内存
function rememory(){
	$(".planname input[name='name']").removeAttr('readonly style').val("");
	$(".planname input[name='name']").val(lan.crontab.mem);
	$("#implement").html(lan.crontab.mem_ps);
	return;
}
//上传
function fileupload(){
	$("#sFile").change(function(){
		$("#viewfile").val($("#sFile").val());
	});
	$("#sFile").click();
}