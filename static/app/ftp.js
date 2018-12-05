/**
 * 取回FTP数据列表
 * @param {Number} page   当前页
 */
function getFtp(page,search) {
	if(page == undefined) page = 1
	search = search == undefined ? '':search;
	search = $("#SearchValue").prop("value");
	order = getCookie('order');
	if(order){
		order = '&order=' + order;
	}else{
		order = '';
	}
	var sUrl = '/data?action=getData'
	var data = 'tojs=getFtp&table=ftps&limit=15&p='+page+'&search='+search + order;
	var loadT = layer.load();
	$.post(sUrl,data, function(data){
		layer.close(loadT);
		//构造数据列表
		var Body = '';
		if(data.data == ""){
			Body="<tr><td colspan='7'>"+lan.ftp.empty+"</td></tr>";
			$(".dataTables_paginate").hide()
		}
		for (var i = 0; i < data.data.length; i++) {
			if(data.data[i].status == '1'){
				var ftp_status = "<a href='javascript:;' title='"+lan.ftp.stop_title+"' onclick=\"ftpStop("+data.data[i].id+",'"+data.data[i].name+"')\"><span style='color:#5CB85C'>"+lan.ftp.start+" </span> <span style='color:#5CB85C' class='glyphicon glyphicon-play'></span></a>";
			}else{
				var ftp_status = "<a href='javascript:;' title='"+lan.ftp.start_title+"' onclick=\"ftpStart("+data.data[i].id+",'"+data.data[i].name+"')\"><span style='color:red'>"+lan.ftp.stop+" </span> <span style='color:red;' class='glyphicon glyphicon-pause'></span></a>";;
			}
			Body +="<tr><td><input type='checkbox' onclick='checkSelect();' title='"+data.data[i].name+"' name='id' value='"+data.data[i].id+"'></td>\
					<td>"+data.data[i].name+"</td>\
					<td class='relative'><span class='password' data-pw='"+data.data[i].password+"'>**********</span><span class='glyphicon glyphicon-eye-open cursor pw-ico' style='margin-left:10px'></span><span class='ico-copy cursor btcopy' style='margin-left:10px' title='"+lan.ftp.copy+"' data-pw='"+data.data[i].password+"' onclick=\"btcopy('"+data.data[i].password+"')\"></span></td>\
					<td>"+ftp_status+"</td>\
					<td><a class='btlink' title='"+lan.ftp.open_path+"' href=\"javascript:openPath('"+data.data[i].path+"');\">"+data.data[i].path+"</a></td>\
					<td><a class='btlinkbed' href='javascript:;' data-id='"+data.data[i].id+"'>" + data.data[i].ps + "</a></td>\
					<td style='text-align:right; color:#bbb'>\
                       <a href='javascript:;' class='btlink' onClick=\"ftpEditSet("+data.data[i].id+",'"+data.data[i].name+"','"+data.data[i].password+"')\">"+lan.ftp.edit_pass+" </a>\
                        | <a href='javascript:;' class='btlink' onclick=\"ftpDelete('"+data.data[i].id+"','"+data.data[i].name+"')\" >"+lan.public.del+"</a>\
                    </td></tr>"                 			
		}
		//输出数据列表
		$("#ftpBody").html(Body);
		//输出分页
		$("#ftpPage").html(data.page);
		//备注
		$(".btlinkbed").click(function(){
			var dataid = $(this).attr("data-id");
			var databak = $(this).text();
			$(this).hide().after("<input class='baktext' type='text' data-id='"+dataid+"' name='bak' value='" + databak + "' placeholder='"+lan.ftp.ps+"' onblur='GetBakPost(\"ftps\")' />");
			$(".baktext").focus();
		});
		//复制密码
		showHidePwd();
	});
}

/**
 *添加FTP帐户
 * @param {Number} type	添加类型
 */
function ftpAdd(type) {
	if (type == 1) {
		var loadT = layer.load({
			shade: true,
			shadeClose: false
		});
		var data = $("#ftpAdd").serialize();
		$.post('/ftp?action=AddUser', data, function(rdata) {
			if (rdata.status) {
				getFtp(1);
				layer.closeAll();
				layer.msg(rdata.msg, {
					icon: 1
				});
			} else {
				getFtp(1);
				layer.closeAll();
				layer.msg(rdata.msg, {
					icon: 5
				});
			}
		});
		return true;
	}
	var defaultPath = $("#defaultPath").html();
	var index = layer.open({
		type: 1,
		skin: 'demo-class',
		area: '500px',
		title: lan.ftp.add_title,
		closeBtn: 2,
		shift: 5,
		shadeClose: false,
		content: "<form class='bt-form pd20 pb70' id='ftpAdd'>\
					<div class='line'>\
					<span class='tname'>"+lan.ftp.add_user+"</span>\
					<div class='info-r'><input class='bt-input-text' type='text' id='ftpUser' name='ftp_username' style='width:330px' /></div>\
					</div>\
					<div class='line'>\
					<span class='tname'>"+lan.ftp.add_pass+"</span>\
					<div class='info-r'><input class='bt-input-text mr5' type='text' name='ftp_password' id='MyPassword' style='width:330px' value='"+(RandomStrPwd(10))+"' /><span title='"+lan.ftp.add_pass_rep+"' class='glyphicon glyphicon-repeat cursor' onclick='repeatPwd(10)'></span></div>\
					</div>\
					<div class='line'>\
					<span class='tname'>"+lan.ftp.add_path+"</span>\
					<div class='info-r'><input id='inputPath' class='bt-input-text mr5' type='text' name='path' value='"+defaultPath+"/' placeholder='"+lan.ftp.add_path_title+"'  style='width:330px' /><span class='glyphicon glyphicon-folder-open cursor' onclick='ChangePath(\"inputPath\")'></span><p class='c9 mt10'>"+lan.ftp.add_path_ps+"</p></div>\
					</div>\
                    <div class='line' style='display:none'>\
					<span class='tname'>"+lan.ftp.add_ps+"</span>\
					<div class='info-r'>\
					<input class='bt-input-text' type='text' name='ps' value='' placeholder='"+lan.ftp.add_ps_title+"' />\
					</div></div>\
					<div class='bt-form-submit-btn'>\
						<button type='button' class='btn btn-danger btn-sm btn-title' onclick='layer.closeAll()'>"+lan.public.close+"</button>\
				        <button type='button' class='btn btn-success btn-sm btn-title' onclick=\"ftpAdd(1)\" >"+lan.public.submit+"</button>\
			        </div>\
			      </form>"
	});
	
	
	$("#ftpUser").keyup(function()
	{
		var ftpName = $(this).val();
		if($("#inputPath").val().substr(0,11) == '/www/wwwroo' )
		{
			$("#inputPath").val('/www/wwwroot/'+ftpName);
		}
	});
}


/**
 * 删除FTP帐户
 * @param {Number} id 
 * @param {String} ftp_username  欲被删除的用户名
 * @return {bool}
 */
function ftpDelete(id,ftp_username){
	SafeMessage(lan.public.del+"["+ftp_username+"]",lan.get('confirm_del',[ftp_username]),function(){
		layer.msg(lan.public.the_del,{icon:16,time:0,shade: [0.3, '#000']});
		var data='&id='+id+'&username='+ftp_username;
		$.post('/ftp?action=DeleteUser',data,function(rdata){
			layer.closeAll();
			if(rdata['status'] == true){
				getFtp(1);
				layer.msg(rdata.msg,{icon:1});
			}else{
				layer.msg(rdata.msg,{icon:2});
			}
		});
	});
}


//批量删除
function allDeleteFtp(){
	var checkList = $("input[name=id]");
	var dataList = new Array();
	for(var i=0;i<checkList.length;i++){
		if(!checkList[i].checked) continue;
		var tmp = new Object();
		tmp.name = checkList[i].title;
		tmp.id = checkList[i].value;
		dataList.push(tmp);
	}
	SafeMessage(lan.ftp.del_all,"<a style='color:red;'>"+lan.get('del_all_ftp',[dataList.length])+"</a>",function(){
		layer.closeAll();
		syncDeleteFtp(dataList,0,'');
	});
}

//模拟同步开始批量删除
function syncDeleteFtp(dataList,successCount,errorMsg){
	if(dataList.length < 1) {
		layer.msg(lan.get('del_all_ftp_ok',[successCount]),{icon:1});
		return;
	}
	var loadT = layer.msg(lan.get('del_all_task_del',[dataList[0].name]),{icon:16,time:0,shade: [0.3, '#000']});
	$.ajax({
		type:'POST',
		url:'/ftp?action=DeleteUser',
		data:'id='+dataList[0].id+'&username='+dataList[0].name,
		async: true,
		success:function(frdata){
			layer.close(loadT);
			if(frdata.status){
				successCount++;
				$("input[title='"+dataList[0].name+"']").parents("tr").remove();
			}else{
				if(!errorMsg){
					errorMsg = '<br><p>'+lan.ftp.del_all_err+'</p>';
				}
				errorMsg += '<li>'+dataList[0].name+' -> '+frdata.msg+'</li>'
			}
			dataList.splice(0,1);
			syncDeleteFtp(dataList,successCount,errorMsg);
		}
	});
}


/**
 * 选中项操作
 */
function goSet(num){
	//取选中对象
	var el = document.getElementsByTagName('input');
	var len = el.length;
	var data='';
	var a = '';
	var count = 0;
	//构造POST数据
	for(var i=0;i<len;i++){
		if(el[i].checked == true && el[i].value != 'on'){
			data += a+count+'='+el[i].value;
			a = '&';
			count++;
		}
	}
	//判断操作类别
	if(num==1){
		reAdd(data);
	}
	else if(num==2){
		shift(data);
	}
}


/**
 * 停止FTP帐号
 * @param {Number} id	FTP的ID
 * @param {String} username	FTP用户名
 */
function ftpStop(id, username) {
	layer.confirm(lan.ftp.stop_confirm.replace('{1}',username), {
		title: lan.ftp.stop_title,icon:3,
		closeBtn:2
	}, function(index) {
		if (index > 0) {
			var loadT = layer.load({shade: true,shadeClose: false});
			var data='id=' + id + '&username=' + username + '&status=0';
			$.post('/ftp?action=SetStatus',data, function(rdata) {
				layer.close(loadT);
				if (rdata.status == true) {
					layer.msg(rdata.msg, {icon: 1});
					getFtp(1);
				} else {
					layer.msg(rdata.msg, {icon: 5});
				}
			});
		} else {
			layer.closeAll();
		}
	});
}

/**
 * 启动FTP帐号
 * @param {Number} id	FTP的ID
 * @param {String} username	FTP用户名
 */
function ftpStart(id, username) {
	var loadT = layer.load({shade: true,shadeClose: false});
	var data='id=' + id + '&username=' + username + '&status=1';
	$.post('/ftp?action=SetStatus',data, function(rdata) {
		layer.close(loadT);
		if (rdata.status == true) {
			layer.msg(rdata.msg, {icon: 1});
			getFtp(1);
		} else {
			layer.msg(rdata.msg, {icon: 5});
		}
	});
}

/**
 * 修改FTP帐户信息
 * @param {Number} type 修改类型
 * @param {Number} id	FTP编号
 * @param {String} username	FTP用户名
 * @param {String} statu	FTP状态
 * @param {String} group	FTP权限
 * @param {String} passwd	FTP密码
 */
function ftpEditSet(id, username, passwd) {
	if (id != undefined) {
		var index = layer.open({
			type: 1,
			skin: 'demo-class',
			area: '300px',
			title: lan.ftp.pass_title,
			closeBtn: 2,
			shift: 5,
			shadeClose: false,
			content: "<form class='bt-form pd20 pb70' id='ftpEditSet'>\
						<div class='line'>\
						<input type='hidden' name='id' value='" + id + "'/>\
						<input type='hidden' name='ftp_username' value='" + username + "'/>\
						<span class='tname'>"+lan.ftp.pass_user+":</span><div class='info-r'><input class='bt-input-text' type='text' name='myusername' value='" + username + "' disabled  style='width:100%'/></div></div>\
						<div class='line'>\
						<span class='tname'>"+lan.ftp.pass_new+":</span><div class='info-r'><input class='bt-input-text' type='text' name='new_password' value='" + passwd + "' style='width:100%' /></div>\
						</div>\
				        <div class='bt-form-submit-btn'>\
							<button type='button' class='btn btn-danger btn-sm btn-title' onclick='layer.closeAll()'>"+lan.public.close+"</button>\
					        <button type='button' class='btn btn-success btn-sm btn-title' onclick='ftpEditSet()' >"+lan.public.ok+"</button>\
				        </div>\
				      </form>"
		});
	} else {
		layer.confirm(lan.ftp.pass_confirm, {
			title: lan.ftp.stop_title,icon:3,
			closeBtn:2
		}, function(index) {
			if (index > 0) {
				var loadT = layer.load({
					shade: true,
					shadeClose: false
				});
				var data = $("#ftpEditSet").serialize();
				$.post('/ftp?action=SetUserPassword', data, function(rdata) {
					layer.closeAll();
					layer.msg(rdata.msg, { icon: rdata.status?1:5});
					getFtp(1);
				});
			}
		});
	}
}

/**
 *修改FTP服务端口
 */
function ftpPortEdit(port) {
	layer.open({
		type: 1,
		skin: 'demo-class',
		area: '300px',
		title: lan.ftp.port_title,
		closeBtn: 2,
		shift: 5,
		shadeClose: false,
		content: "<div class='bt-form pd20 pb70' id='ftpEditSet'>\
					<div class='line'><input id='ftp_port' class='bt-input-text' type='text' name='ftp_port' value='" + port + "' style='width:100%' /></div>\
			        <div class='bt-form-submit-btn'>\
						<button type='button' class='btn btn-danger btn-sm btn-title' onclick='layer.closeAll()'>"+lan.public.close+"</button>\
				        <button id='poseFtpPort' type='button' class='btn btn-success btn-sm btn-title'>"+lan.public.submit+"</button>\
			        </div>\
			      </div>"
	});
	 $("#poseFtpPort").click(function(){
	 	var NewPort = $("#ftp_port").val();
	 	ftpPortPost(NewPort);
	 })
	 $("#ftp_port").focus().keyup(function(e){
		if(e.keyCode == 13) $("#poseFtpPort").click();
	});
}
//修改FTP服务端口
function ftpPortPost(port){
	layer.closeAll();
	var loadT = layer.msg(lan.public.the,{icon:16,time:0,shade: [0.3, '#000']});
	var data='port=' + port;
	$.post('/ftp?action=setPort',data, function(rdata) {
		layer.close(loadT)
		layer.msg(rdata.msg,{icon:rdata.status?1:2})
		setTimeout(function(){
			window.location.reload()	
		},3000)
		
	});
}