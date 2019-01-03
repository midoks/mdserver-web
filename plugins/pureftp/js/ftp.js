function str2Obj(str){
	var data = {};
	kv = str.split('&');
	for(i in kv){
		v = kv[i].split('=');
		data[v[0]] = v[1];
	}
	return data;
}

function ftpPost(method,args,callback){

	var _args = null; 
	if (typeof(args) == 'string'){
		_args = JSON.stringify(str2Obj(args));
	} else {
		_args = JSON.stringify(args);
	}

    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });
    $.post('/plugins/run', {name:'pureftp', func:method, args:_args}, function(data) {
        layer.close(loadT);
        if (!data.status){
            layer.msg(data.msg,{icon:0,time:2000,shade: [0.3, '#000']});
            return;
        }

        if(typeof(callback) == 'function'){
            callback(data);
        }
    },'json'); 
}


function ftpAsyncPost(method,args){
	return syncPost('/plugins/run',
		{name:'pureftp', func:method, args:JSON.stringify(args)}
	);
}

function ftpListFind(){
    var search = $('#ftp_find_user').val();
    if (search==''){
        layer.msg('搜索字符不能为空!',{icon:0,time:2000,shade: [0.3, '#000']});
        return;
    }
    ftpList(1, search);
}

function ftpList(page, search){
	var _data = {};
    if (typeof(page) =='undefined'){
        var page = 1;
    }
    
    _data['page'] = page;
    _data['page_size'] = 10;
    if(typeof(search) != 'undefined'){
        _data['search'] = search;
    }

    ftpPost('get_ftp_list', _data, function(data){

        var rdata = $.parseJSON(data.data);
        console.log(rdata);
        content = '<div class="info-title-tips"><p><span class="glyphicon glyphicon-alert" style="color: #f39c12; margin-right: 10px;"></span>当前FTP地址为：ftp://'+rdata['info']['ip']+':'+rdata['info']['port']+'</p></div>';
        content += '<div class="finduser"><input class="bt-input-text mr5 outline_no" type="text" placeholder="查找用户名" id="ftp_find_user" style="height: 28px; border-radius: 3px;width: 605px;">';
        content += '<button class="btn btn-success btn-sm" onclick="ftpListFind();">查找</button></div>';

        content += '<div class="divtable" style="margin-top:5px;"><table class="table table-hover" width="100%" cellspacing="0" cellpadding="0" border="0">';
        content += '<thead><tr>';
        content += '<th style="width:10%;overflow:hidden;">用户名</th>';
        content += '<th style="width:10%;overflow:hidden;">密码</th>';
        content += '<th style="width:10%;">状态</th>';
        content += '<th>根目录</th>';
        content += '<th>备注</th>';
        content += '<th>操作(<a class="btlink" onclick="addFtp(0);">添加</a>|<a class="btlink">端口</a>)</th>';
        content += '</tr></thead>';

        content += '<tbody>';

        ulist = rdata.data;
        for (i in ulist){
        	// console.log(ulist[i]);
        	status = '<a href="javascript:;" onclick="ftpStart(\''+ulist[i]['id']+'\',\''+ulist[i]['name']+'\')" <span="" style="color:red">已停用<span style="color:red" class="glyphicon glyphicon-pause"></span></a>';
        	if (ulist[i]['status'] == '1'){
        		status = '<a href="javascript:;" title="FTP帐户" onclick="ftpStop(\''+ulist[i]['id']+'\',\''+ulist[i]['name']+'\')"><span style="color:#5CB85C">已启用</span><span style="color:#5CB85C" class="glyphicon glyphicon-play"></span></a>';
        	}
            content += '<tr><td>'+ulist[i]['name']+'</td>'+
        		'<td>'+ulist[i]['password']+'</td>'+
        		'<td>'+status+'</td>' +
        		'<td>'+ulist[i]['path']+'</td>' +
        		'<td>'+ulist[i]['ps']+'</td>' +
            	'<td><a class="btlink" onclick="ftpMod(\''+ulist[i]['id']+'\',\''+ulist[i]['name']+'\',\''+ulist[i]['password']+'\')">改密</a> | ' +
            	'<a class="btlink" onclick="ftpDelete(\''+ulist[i]['id']+'\',\''+ulist[i]['name']+'\')">删除</a></td></tr>';
        }

        content += '</tbody>';
        content += '</table></div>';

        page = '<div class="dataTables_paginate paging_bootstrap pagination" style="margin-top:0px;"><ul id="softPage" class="page"><div>';
        page += rdata.page;
        page += '</div></ul></div>';

        content += page;

        $(".soft-man-con").html(content);
    });
}


/**
 * 取回FTP数据列表
 * @param {Number} page   当前页
 */
// function getFtp(page, search) {
// 	if(page == undefined) page = 1
// 	search = search == undefined ? '':search;
// 	search = $("#SearchValue").prop("value");
// 	order = getCookie('order');
// 	if(order){
// 		order = '&order=' + order;
// 	} else {
// 		order = '';
// 	}
// 	var sUrl = '/data?action=getData'
// 	var data = 'tojs=getFtp&table=ftps&limit=15&p='+page+'&search='+search + order;
// 	var loadT = layer.load();
// 	$.post(sUrl,data, function(data){
// 		layer.close(loadT);
// 		//构造数据列表
// 		var Body = '';
// 		if(data.data == ""){
// 			Body="<tr><td colspan='7'>"+lan.ftp.empty+"</td></tr>";
// 			$(".dataTables_paginate").hide()
// 		}
// 		for (var i = 0; i < data.data.length; i++) {
// 			if(data.data[i].status == '1'){
// 				var ftp_status = "<a href='javascript:;' title='"+lan.ftp.stop_title+"' onclick=\"ftpStop("+data.data[i].id+",'"+data.data[i].name+"')\"><span style='color:#5CB85C'>"+lan.ftp.start+" </span> <span style='color:#5CB85C' class='glyphicon glyphicon-play'></span></a>";
// 			} else {
// 				var ftp_status = "<a href='javascript:;' title='"+lan.ftp.start_title+"' onclick=\"ftpStart("+data.data[i].id+",'"+data.data[i].name+"')\"><span style='color:red'>"+lan.ftp.stop+" </span> <span style='color:red;' class='glyphicon glyphicon-pause'></span></a>";;
// 			}
// 			Body +="<tr><td><input type='checkbox' onclick='checkSelect();' title='"+data.data[i].name+"' name='id' value='"+data.data[i].id+"'></td>\
// 					<td>"+data.data[i].name+"</td>\
// 					<td class='relative'><span class='password' data-pw='"+data.data[i].password+"'>**********</span><span class='glyphicon glyphicon-eye-open cursor pw-ico' style='margin-left:10px'></span><span class='ico-copy cursor btcopy' style='margin-left:10px' title='"+lan.ftp.copy+"' data-pw='"+data.data[i].password+"' onclick=\"btcopy('"+data.data[i].password+"')\"></span></td>\
// 					<td>"+ftp_status+"</td>\
// 					<td><a class='btlink' title='"+lan.ftp.open_path+"' href=\"javascript:openPath('"+data.data[i].path+"');\">"+data.data[i].path+"</a></td>\
// 					<td><a class='btlinkbed' href='javascript:;' data-id='"+data.data[i].id+"'>" + data.data[i].ps + "</a></td>\
// 					<td style='text-align:right; color:#bbb'>\
//                        <a href='javascript:;' class='btlink' onClick=\"ftpEditSet("+data.data[i].id+",'"+data.data[i].name+"','"+data.data[i].password+"')\">"+lan.ftp.edit_pass+" </a>\
//                         | <a href='javascript:;' class='btlink' onclick=\"ftpDelete('"+data.data[i].id+"','"+data.data[i].name+"')\" >"+lan.public.del+"</a>\
//                     </td></tr>"                 			
// 		}
// 		//输出数据列表
// 		$("#ftpBody").html(Body);
// 		//输出分页
// 		$("#ftpPage").html(data.page);
// 		//备注
// 		$(".btlinkbed").click(function(){
// 			var dataid = $(this).attr("data-id");
// 			var databak = $(this).text();
// 			$(this).hide().after("<input class='baktext' type='text' data-id='"+dataid+"' name='bak' value='" + databak + "' placeholder='"+lan.ftp.ps+"' onblur='GetBakPost(\"ftps\")' />");
// 			$(".baktext").focus();
// 		});
// 		//复制密码
// 		showHidePwd();
// 	});
// }

/**
 *添加FTP帐户
 * @param {Number} type	添加类型
 */
function addFtp(type) {
	if (type == 1) {
		var loadT = layer.load({shade: true,shadeClose: false});
		var data = $("#ftpAdd").serialize();
		ftpPost('add_ftp', data, function(data){
			if (data.data == 'ok'){
				layer.msg('添加成功!', {icon: 1});
			} else {
				layer.msg(rdata.data, {icon: 5});
			}
			ftpList();
			layer.close(loadT);
		});
		return true;
	}

	var data = ftpAsyncPost('get_www_dir');
	var defaultPath = data.data;
	var index = layer.open({
		type: 1,
		skin: 'demo-class',
		area: '500px',
		title: '添加FTP帐户',
		closeBtn: 2,
		shift: 5,
		shadeClose: false,
		content: "<form class='bt-form pd20 pb70' id='ftpAdd'>\
					<div class='line'>\
					<span class='tname'>用户名</span>\
					<div class='info-r'><input class='bt-input-text' type='text' id='ftpUser' name='ftp_username' style='width:330px' /></div>\
					</div>\
					<div class='line'>\
					<span class='tname'>密码</span>\
					<div class='info-r'><input class='bt-input-text mr5' type='text' name='ftp_password' id='MyPassword' style='width:330px' value='"+(randomStrPwd(16))+"' /><span title='随机密码' class='glyphicon glyphicon-repeat cursor' onclick='repeatPwd(16)'></span></div>\
					</div>\
					<div class='line'>\
					<span class='tname'>根目录</span>\
					<div class='info-r'><input id='inputPath' class='bt-input-text mr5' type='text' name='path' value='"+defaultPath+"/' placeholder='"+lan.ftp.add_path_title+"'  style='width:330px' /><span class='glyphicon glyphicon-folder-open cursor' onclick='changePath(\"inputPath\")'></span><p class='c9 mt10'>"+lan.ftp.add_path_ps+"</p></div>\
					</div>\
                    <div class='line' style='display:none'>\
					<span class='tname'>备注</span>\
					<div class='info-r'>\
					<input id='ftp_ps' class='bt-input-text' type='text' name='ps' value='' placeholder='备注' />\
					</div></div>\
					<div class='bt-form-submit-btn'>\
						<button type='button' class='btn btn-danger btn-sm btn-title' onclick='layer.closeAll()'>关闭</button>\
				        <button type='button' class='btn btn-success btn-sm btn-title' onclick=\"addFtp(1)\" >提交</button>\
			        </div>\
			      </form>",
	});
	
	$("#ftpUser").keyup(function(){
		var ftpName = $(this).val();
		$("#inputPath").val(defaultPath+'/'+ftpName);
		$("#ftp_ps").val(ftpName);
	});
}


/**
 * 删除FTP帐户
 * @param {Number} id 
 * @param {String} ftp_username  欲被删除的用户名
 * @return {bool}
 */
function ftpDelete(id,ftp_username){
	safeMessage(lan.public.del+"["+ftp_username+"]",lan.get('confirm_del',[ftp_username]),function(){
		layer.msg(lan.public.the_del,{icon:16,time:0,shade: [0.3, '#000']});
		var data='&id='+id+'&username='+ftp_username;

		ftpPost('del_ftp', data, function(data){
			layer.msg('删除成功!', {icon: 1});
			ftpList();
		})
	});
}


function ftpMod(id,name,password){
	console.log(id,name,password);
}


//批量删除
// function allDeleteFtp(){
// 	var checkList = $("input[name=id]");
// 	var dataList = new Array();
// 	for(var i=0;i<checkList.length;i++){
// 		if(!checkList[i].checked) continue;
// 		var tmp = new Object();
// 		tmp.name = checkList[i].title;
// 		tmp.id = checkList[i].value;
// 		dataList.push(tmp);
// 	}
// 	safeMessage(lan.ftp.del_all,"<a style='color:red;'>"+lan.get('del_all_ftp',[dataList.length])+"</a>",function(){
// 		layer.closeAll();
// 		syncDeleteFtp(dataList,0,'');
// 	});
// }

//模拟同步开始批量删除
// function syncDeleteFtp(dataList,successCount,errorMsg){
// 	if(dataList.length < 1) {
// 		layer.msg(lan.get('del_all_ftp_ok',[successCount]),{icon:1});
// 		return;
// 	}
// 	var loadT = layer.msg(lan.get('del_all_task_del',[dataList[0].name]),{icon:16,time:0,shade: [0.3, '#000']});
// 	$.ajax({
// 		type:'POST',
// 		url:'/ftp?action=DeleteUser',
// 		data:'id='+dataList[0].id+'&username='+dataList[0].name,
// 		async: true,
// 		success:function(frdata){
// 			layer.close(loadT);
// 			if(frdata.status){
// 				successCount++;
// 				$("input[title='"+dataList[0].name+"']").parents("tr").remove();
// 			}else{
// 				if(!errorMsg){
// 					errorMsg = '<br><p>'+lan.ftp.del_all_err+'</p>';
// 				}
// 				errorMsg += '<li>'+dataList[0].name+' -> '+frdata.msg+'</li>'
// 			}
// 			dataList.splice(0,1);
// 			syncDeleteFtp(dataList,successCount,errorMsg);
// 		}
// 	});
// }


/**
 * 选中项操作
 */
// function goSet(num){
// 	//取选中对象
// 	var el = document.getElementsByTagName('input');
// 	var len = el.length;
// 	var data='';
// 	var a = '';
// 	var count = 0;
// 	//构造POST数据
// 	for(var i=0;i<len;i++){
// 		if(el[i].checked == true && el[i].value != 'on'){
// 			data += a+count+'='+el[i].value;
// 			a = '&';
// 			count++;
// 		}
// 	}
// 	//判断操作类别
// 	if(num==1){
// 		reAdd(data);
// 	}
// 	else if(num==2){
// 		shift(data);
// 	}
// }


/**
 * 停止FTP帐号
 * @param {Number} id	FTP的ID
 * @param {String} username	FTP用户名
 */
function ftpStop(id, username) {
	layer.confirm('您真的要停止{1}的FTP吗?'.replace('{1}',username), {
		title: 'FTP帐户',icon:3,
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
// function ftpStart(id, username) {
// 	var loadT = layer.load({shade: true,shadeClose: false});
// 	var data='id=' + id + '&username=' + username + '&status=1';
// 	$.post('/ftp?action=SetStatus',data, function(rdata) {
// 		layer.close(loadT);
// 		if (rdata.status == true) {
// 			layer.msg(rdata.msg, {icon: 1});
// 			getFtp(1);
// 		} else {
// 			layer.msg(rdata.msg, {icon: 5});
// 		}
// 	});
// }

/**
 * 修改FTP帐户信息
 * @param {Number} type 修改类型
 * @param {Number} id	FTP编号
 * @param {String} username	FTP用户名
 * @param {String} statu	FTP状态
 * @param {String} group	FTP权限
 * @param {String} passwd	FTP密码
 */
// function ftpEditSet(id, username, passwd) {
// 	if (id != undefined) {
// 		var index = layer.open({
// 			type: 1,
// 			skin: 'demo-class',
// 			area: '300px',
// 			title: lan.ftp.pass_title,
// 			closeBtn: 2,
// 			shift: 5,
// 			shadeClose: false,
// 			content: "<form class='bt-form pd20 pb70' id='ftpEditSet'>\
// 						<div class='line'>\
// 						<input type='hidden' name='id' value='" + id + "'/>\
// 						<input type='hidden' name='ftp_username' value='" + username + "'/>\
// 						<span class='tname'>"+lan.ftp.pass_user+":</span><div class='info-r'><input class='bt-input-text' type='text' name='myusername' value='" + username + "' disabled  style='width:100%'/></div></div>\
// 						<div class='line'>\
// 						<span class='tname'>"+lan.ftp.pass_new+":</span><div class='info-r'><input class='bt-input-text' type='text' name='new_password' value='" + passwd + "' style='width:100%' /></div>\
// 						</div>\
// 				        <div class='bt-form-submit-btn'>\
// 							<button type='button' class='btn btn-danger btn-sm btn-title' onclick='layer.closeAll()'>"+lan.public.close+"</button>\
// 					        <button type='button' class='btn btn-success btn-sm btn-title' onclick='ftpEditSet()' >"+lan.public.ok+"</button>\
// 				        </div>\
// 				      </form>"
// 		});
// 	} else {
// 		layer.confirm(lan.ftp.pass_confirm, {
// 			title: lan.ftp.stop_title,icon:3,
// 			closeBtn:2
// 		}, function(index) {
// 			if (index > 0) {
// 				var loadT = layer.load({
// 					shade: true,
// 					shadeClose: false
// 				});
// 				var data = $("#ftpEditSet").serialize();
// 				$.post('/ftp?action=SetUserPassword', data, function(rdata) {
// 					layer.closeAll();
// 					layer.msg(rdata.msg, { icon: rdata.status?1:5});
// 					getFtp(1);
// 				});
// 			}
// 		});
// 	}
// }

/**
 *修改FTP服务端口
 */
// function ftpPortEdit(port) {
// 	layer.open({
// 		type: 1,
// 		skin: 'demo-class',
// 		area: '300px',
// 		title: lan.ftp.port_title,
// 		closeBtn: 2,
// 		shift: 5,
// 		shadeClose: false,
// 		content: "<div class='bt-form pd20 pb70' id='ftpEditSet'>\
// 					<div class='line'><input id='ftp_port' class='bt-input-text' type='text' name='ftp_port' value='" + port + "' style='width:100%' /></div>\
// 			        <div class='bt-form-submit-btn'>\
// 						<button type='button' class='btn btn-danger btn-sm btn-title' onclick='layer.closeAll()'>"+lan.public.close+"</button>\
// 				        <button id='poseFtpPort' type='button' class='btn btn-success btn-sm btn-title'>"+lan.public.submit+"</button>\
// 			        </div>\
// 			      </div>"
// 	});
// 	 $("#poseFtpPort").click(function(){
// 	 	var NewPort = $("#ftp_port").val();
// 	 	ftpPortPost(NewPort);
// 	 })
// 	 $("#ftp_port").focus().keyup(function(e){
// 		if(e.keyCode == 13) $("#poseFtpPort").click();
// 	});
// }

//修改FTP服务端口
// function ftpPortPost(port){
// 	layer.closeAll();
// 	var loadT = layer.msg(lan.public.the,{icon:16,time:0,shade: [0.3, '#000']});
// 	var data='port=' + port;
// 	$.post('/ftp?action=setPort',data, function(rdata) {
// 		layer.close(loadT)
// 		layer.msg(rdata.msg,{icon:rdata.status?1:2})
// 		setTimeout(function(){
// 			window.location.reload()	
// 		},3000)
		
// 	});
// }