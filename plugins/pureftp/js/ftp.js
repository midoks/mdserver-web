
function ftpPost(method,args,callback){
	var _args = null; 
	if (typeof(args) == 'string'){
		_args = JSON.stringify(toArrayObject(args));
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
        // console.log(rdata);
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
        content += '<th>操作(<a class="btlink" onclick="addFtp();">添加</a>|<a class="btlink" onclick="modFtpPort(0,\''+rdata['info']['port']+'\')">端口</a>)</th>';
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
            	'<td><a class="btlink" onclick="ftpModPwd(\''+ulist[i]['id']+'\',\''+ulist[i]['name']+'\',\''+ulist[i]['password']+'\')">改密</a> | ' +
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
 *添加FTP帐户
 */
function addFtp() {

	var data = ftpAsyncPost('get_www_dir');
	var defaultPath = data.data;
	var indexFtp = layer.open({
		type: 1,
		area: '500px',
		title: '添加FTP帐户',
		closeBtn: 2,
		shift: 5,
		shadeClose: false,
		btn: ['提交','关闭'],
		content: "<form class='form pd20' id='ftpAdd'>\
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
			      </form>",
		yes:function(index,layero){
			var loadT = layer.load({shade: true,shadeClose: false});
			var data = $("#ftpAdd").serialize();
			ftpPost('add_ftp', data, function(rdata){
				layer.close(loadT);
				layer.close(indexFtp);
				if (rdata.data == 'ok'){
					layer.msg('添加成功!', {icon: 1,time:3000});
				} else {
					layer.msg(rdata.data, {icon: 5,time:3000});
				}

				setTimeout(function(){ftpList();},2000);
			});
			return true;
        },
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

function modFtpPort(type, port){
	var index = layer.open({
		type: 1,
		skin: 'demo-class',
		area: '500px',
		title: '修改FTP帐户端口',
		content: "<form class='bt-form pd20 pb70'>\
					<div class='line'>\
					<span class='tname'>默认端口</span>\
					<div class='info-r'><input class='bt-input-text mr5' type='text' id='ftpPort' name='ftp_port' style='width:330px' value='"+port+"'/></div>\
					</div>\
					<div class='bt-form-submit-btn'>\
						<button id='ftp_port_close' type='button' class='btn btn-danger btn-sm btn-title'>关闭</button>\
				        <button id='ftp_port_submit' type='button' class='btn btn-success btn-sm btn-title'>提交</button>\
			        </div>\
			      </form>",
	});

	$('#ftp_port_close').click(function(){
		$('.layui-layer-close1').click();
	});

	$('#ftp_port_submit').click(function(){
		var port = $('#ftpPort').val();
		data = 'port='+port
		ftpPost('mod_ftp_port', data,function(data){
			ftpList();
			if (data.data == 'ok'){
				layer.msg('修改成功!', {icon: 1});
			} else {
				layer.msg(data.data, {icon: 2});
			}
			$('.layui-layer-close1').click();
		});
	});

}


function ftpModPwd(id,name,password){
	var index = layer.open({
		type: 1,
		skin: 'demo-class',
		area: '500px',
		title: '修改FTP帐户密码',
		content: "<form class='bt-form pd20 pb70'>\
					<div class='line'>\
					<span class='tname'>用户名</span>\
					<div class='info-r'><input disabled class='bt-input-text mr5' type='text' id='ftpUser' name='ftp_username' style='width:330px' value='"+name+"'/></div>\
					</div>\
					\
					<div class='line'>\
					<span class='tname'>密码</span>\
					<div class='info-r'><input class='bt-input-text mr5' type='text' name='ftp_password' id='MyPassword' style='width:330px' value='"+password+"' /><span title='随机密码' class='glyphicon glyphicon-repeat cursor' onclick='repeatPwd(16)'></span></div>\
					</div>\
					<div class='bt-form-submit-btn'>\
						<button id='ftp_mod_close' type='button' class='btn btn-danger btn-sm btn-title'>关闭</button>\
				        <button id='ftp_mod_submit' type='button' class='btn btn-success btn-sm btn-title'>提交</button>\
			        </div>\
			      </form>",
	});


	$('#ftp_mod_close').click(function(){
		$('.layui-layer-close1').click();
	});

	$('#ftp_mod_submit').click(function(){
		pwd = $('#MyPassword').val();
		data='id='+id+'&name='+name+'&password='+pwd
		ftpPost('mod_ftp', data,function(data){
			ftpList();
			if (data.data == 'ok'){
				layer.msg('修改成功!', {icon: 1});
			}
			$('.layui-layer-close1').click();
		});
	});
}


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
			ftpPost('stop_ftp', data, function(data){
				layer.close(loadT);
				if (data.data == 'ok'){
					showMsg('启动成功!', function(){
						ftpList();
					},{icon: 1});
				} else {
					layer.msg(data.data, {icon: 2});
				}
			});
		}
		$('.layui-layer-close1').click();
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
	ftpPost('start_ftp', data, function(data){
		layer.close(loadT);
		if (data.data == 'ok'){
			showMsg('启动成功!', function(){
				ftpList();
			},{icon: 1});
		} else {
			layer.msg(data.data, {icon: 2});
		}
		
	});
}

