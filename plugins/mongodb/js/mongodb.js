function mgPost(method, version, args,callback){
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });

    var req_data = {};
    req_data['name'] = 'mongodb';
    req_data['func'] = method;
    req_data['version'] = version;
 
    if (typeof(args) == 'string'){
        req_data['args'] = JSON.stringify(toArrayObject(args));
    } else {
        req_data['args'] = JSON.stringify(args);
    }

    $.post('/plugins/run', req_data, function(data) {
        layer.close(loadT);
        if (!data.status){
            //错误展示10S
            layer.msg(data.msg,{icon:0,time:2000,shade: [10, '#000']});
            return;
        }

        if(typeof(callback) == 'function'){
            callback(data);
        }
    },'json'); 
}

function mgAsyncPost(method,args){
    var _args = null; 
    if (typeof(args) == 'string'){
        _args = JSON.stringify(toArrayObject(args));
    } else {
        _args = JSON.stringify(args);
    }

    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });
    return syncPost('/plugins/run', {name:'mongodb', func:method, args:_args}); 
}


function mongoStatus() {
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });
    $.post('/plugins/run', {name:'mongodb', func:'run_info'}, function(data) {
    	layer.close(loadT);
    	if (!data.status){
    		layer.msg(data.msg,{icon:0,time:2000,shade: [0.3, '#000']});
    		return;
    	}

    	var rdata = $.parseJSON(data.data);
        var con = '<div class="divtable">\
						<table class="table table-hover table-bordered" style="width: 660px;">\
						<thead><th>字段</th><th>当前值</th><th>说明</th></thead>\
						<tbody>\
							<tr><th>host</th><td>' + rdata.host + '</td><td>服务器</td></tr>\
							<tr><th>version</th><td>' + rdata.version + '</td><td>版本</td></tr>\
							<tr><th>db_path</th><td>' + rdata.db_path + '</td><td>数据路径</td></tr>\
							<tr><th>uptime</th><td>' + rdata.uptime + '</td><td>已运行秒</td></tr>\
							<tr><th>connections</th><td>' + rdata.connections + '</td><td>当前链接数</td></tr>\
							<tr><th>collections</th><td>' + rdata.collections + '</td><td>文档数</td></tr>\
							<tr><th>insert</th><td>' + rdata.pf['insert'] + '</td><td>插入命令数</td></tr>\
							<tr><th>query</th><td>' + rdata.pf['query'] + '</td><td>查询命令数</td></tr>\
							<tr><th>update</th><td>' + rdata.pf['update'] + '</td><td>更新命令数</td></tr>\
							<tr><th>delete</th><td>' + rdata.pf['delete'] + '</td><td>删除命令数</td></tr>\
							<tr><th>getmore</th><td>' + rdata.pf['getmore'] + '</td><td>getmore命令数</td></tr>\
							<tr><th>command</th><td>' + rdata.pf['command'] + '</td><td>执行命令数</td></tr>\
						<tbody>\
				</table></div>';

        $(".soft-man-con").html(con);
    },'json');
}


function mongoDocStatus() {
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });
    $.post('/plugins/run', {name:'mongodb', func:'run_doc_info'}, function(data) {
    	layer.close(loadT);
    	if (!data.status){
    		layer.msg(data.msg,{icon:0,time:2000,shade: [0.3, '#000']});
    		return;
    	}

    	var rdata = $.parseJSON(data.data);

		var t = '';
		for(var i=0; i<rdata.dbs.length;i++){
			t += '<tr>';
			t += '<th>'+rdata.dbs[i]["db"]+'</th>';
			t += '<th>'+toSize(rdata.dbs[i]["totalSize"])+'</th>';
			t += '<th>'+toSize(rdata.dbs[i]["storageSize"])+'</th>';
			t += '<th>'+toSize(rdata.dbs[i]["dataSize"])+'</th>';
			t += '<th>'+toSize(rdata.dbs[i]["indexSize"])+'</th>';
			t += '<th>'+rdata.dbs[i]["indexes"]+'</th>';
			t += '<th>'+rdata.dbs[i]["objects"]+'</th>';
			t += '</tr>';
		}
		// console.log(t);

		var con = '<div class="divtable">\
						<table class="table table-hover table-bordered" style="width: 660px;">\
						<thead><th>库名</th><th>大小</th><th>存储大小</th><th>数据</th><th>索引</th><th>文档数据</th><th>对象</th></thead>\
						<tbody>'+t+'<tbody>\
				</table></div>';
		// console.log(rdata.dbs);

        $(".soft-man-con").html(con);
    },'json');
}

function mongoReplStatus() {
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });
    $.post('/plugins/run', {name:'mongodb', func:'run_repl_info'}, function(data) {
    	layer.close(loadT);
    	if (!data.status){
    		layer.msg(data.msg,{icon:0,time:2000,shade: [0.3, '#000']});
    		return;
    	}

		var rdata = $.parseJSON(data.data);
		var rdata = rdata.data;

		var tbody = '';
		if (rdata.status == '无'){
			tbody += '<tr><td colspan="3" style="text-align:center;">无数据</td></tr>';
		} else{
			tbody += '<tr><th>状态</th><td>' + rdata.status + '</td><td>主/从</td></tr>\
					<tr><th>同步文档</th><td>' + rdata.setName + '</td><td>文档名</td></tr>\
					<tr><th>hosts</th><td><span class="overflow_hide" style="width:260px;" title="'+rdata.hosts+'">' + rdata.hosts + '</span></td><td>服务器所有节点</td></tr>\
					<tr><th>primary</th><td>' + rdata.primary + '</td><td>primary</td></tr>\
					<tr><th>me</th><td>' + rdata.me + '</td><td>me</td></tr>';
		}

        var con = '<div class="divtable">\
				<table class="table table-hover table-bordered" style="width: 660px;">\
					<thead><th>字段</th><th>当前值</th><th>说明</th></thead>\
					<tbody>\
						'+tbody+'\
					<tbody>\
				</table>\
			</div>';

        $(".soft-man-con").html(con);
    },'json');
}

//配置修改
function mongoSetConfig() {
    mgPost('get_config', '','',function(data){
        var rdata = $.parseJSON(data.data);
        if (!rdata['status']){
        	layer.msg(rdata['msg']);
        	return;
        }
        rdata = rdata.data;
        if (rdata['security']['authorization'] == 'enabled'){
        	var body_auth = '<input class="btswitch btswitch-ios" id="auth" type="checkbox" checked><label  style="float: left;top: -3px;" class="btswitch-btn" for="auth" onclick="mongoConfigAuth();"></label>';
        } else {
        	var body_auth = '<input class="btswitch btswitch-ios" id="auth" type="checkbox"><label  style="float: left;top: -3px;" class="btswitch-btn" for="auth" onclick="mongoConfigAuth();"></label>';
        }

        var body = "<div class='bingfa'>" +
            "<p class='line'><span class='span_tit'>IP：</span><input class='bt-input-text' type='text' name='bind_ip' value='" + rdata['net']['bindIp'] + "' />，<font>监听IP请勿随意修改</font></p>" +
            "<p class='line'><span class='span_tit'>port： </span><input class='bt-input-text' type='number' name='port' value='" + rdata['net']['port'] + "' />，<font>监听端口,一般无需修改</font></p>" +
            "<p class='line'><span class='span_tit'>dbPath：</span><input class='bt-input-text' type='text' name='data_path' value='" + rdata['storage']['dbPath'] + "' />，<font>数据存储位置</font></p>" +
            "<p class='line'><span class='span_tit'>path：</span><input class='bt-input-text' type='text' name='log' value='" + rdata['systemLog']['path'] + "' />，<font>日志文件位置</font></p>" +
            "<p class='line'><span class='span_tit'>pidFilePath：</span><input class='bt-input-text' type='text' name='pid_file_path' value='" + rdata['processManagement']['pidFilePath'] + "' />，<font>PID保存路径</font></p>" +
            "<p class='line'><span class='span_tit' style='float:left;'>安全认证：</span>"+body_auth+"</p>" +
            "<div class='mtb15' style='padding-top: 10px;text-align: center;'>\
            	<button class='btn btn-success btn-sm mr5' onclick='mongoSetConfig();'>刷新</button>\
            	<button class='btn btn-success btn-sm' onclick='mongoConfigSave();'>保存</button>" +
            "</div></div>";

        // console.log(body);
        $(".soft-man-con").html(body);
    });
}

function mongoConfigAuth(){
	mgPost('set_config_auth', '','',function(rdata){
		var rdata = $.parseJSON(rdata.data);
		layer.msg(rdata.msg, { icon: rdata.status ? 1 : 2 });
    });
}

function mongoConfigSave(){
	var data = {};
	data['bind_ip'] = $('input[name="bind_ip"]').val();
	data['port'] = $('input[name="port"]').val();
	data['data_path'] = $('input[name="data_path"]').val();
	data['log'] = $('input[name="log"]').val();
	data['pid_file_path'] = $('input[name="pid_file_path"]').val();

	mgPost('set_config', '',data,function(rdata){
		// console.log(rdata);
		var rdata = $.parseJSON(rdata.data);
		layer.msg(rdata.msg, { icon: rdata.status ? 1 : 2 });
    });
}

function dbList(page, search){
    var _data = {};
    if (typeof(page) =='undefined'){
        var page = 1;
    }

    if(typeof(search) != 'undefined'){
        _data['search'] = search;
    }
    
    _data['page'] = page;
    _data['page_size'] = 10;
   	console.log(_data);
    mgPost('get_db_list', '',_data, function(data){
    	console.log(data);
        var rdata = $.parseJSON(data.data);
        console.log(rdata);
        var list = '';
        for(i in rdata.data){
            list += '<tr>';
            list +='<td><input value="'+rdata.data[i]['id']+'" class="check" onclick="checkSelect();" type="checkbox"></td>';
            list += '<td>' + rdata.data[i]['name'] +'</td>';
            list += '<td>' + rdata.data[i]['username'] +'</td>';
            list += '<td>' + 
                        '<span class="password" data-pw="'+rdata.data[i]['password']+'">***</span>' +
                        '<span onclick="showHidePass(this)" class="glyphicon glyphicon-eye-open cursor pw-ico" style="margin-left:10px"></span>'+
                        '<span class="ico-copy cursor btcopy" style="margin-left:10px" title="复制密码" onclick="copyPass(\''+rdata.data[i]['password']+'\')"></span>'+
                    '</td>';
        

            list += '<td><span class="c9 input-edit" onclick="setDbPs(\''+rdata.data[i]['id']+'\',\''+rdata.data[i]['name']+'\',this)" style="display: inline-block;">'+rdata.data[i]['ps']+'</span></td>';
            list += '<td style="text-align:right">';

            list += '<a href="javascript:;" class="btlink" class="btlink" onclick="setBackup(\''+rdata.data[i]['name']+'\',this)" title="数据库备份">'+(rdata.data[i]['is_backup']?'备份':'未备份') +'</a> | ';

            list += '<a href="javascript:;" class="btlink" onclick="repTools(\''+rdata.data[i]['name']+'\')" title="MySQL优化修复工具">工具</a> | ' +
                        '<a href="javascript:;" class="btlink" onclick="setDbAccess(\''+rdata.data[i]['username']+'\')" title="设置数据库权限">权限</a> | ' +
                        '<a href="javascript:;" class="btlink" onclick="setDbPass('+rdata.data[i]['id']+',\''+ rdata.data[i]['username'] +'\',\'' + rdata.data[i]['password'] + '\')">改密</a> | ' +
                        '<a href="javascript:;" class="btlink" onclick="delDb(\''+rdata.data[i]['id']+'\',\''+rdata.data[i]['name']+'\')" title="删除数据库">删除</a>' +
                    '</td>';
            list += '</tr>';
        }

        //<button onclick="" id="dataRecycle" title="删除选中项" class="btn btn-default btn-sm" style="margin-left: 5px;"><span class="glyphicon glyphicon-trash" style="margin-right: 5px;"></span>回收站</button>
        // <button onclick="setDbAccess(\'root\')" title="ROOT权限" class="btn btn-default btn-sm" type="button" style="margin-right: 5px;">ROOT权限</button>\
        var con = '<div class="safe bgw">\
            <button onclick="addDatabase()" title="添加数据库" class="btn btn-success btn-sm" type="button" style="margin-right: 5px;">添加数据库</button>\
            <button onclick="setRootPwd(0,\''+rdata.info['root_pwd']+'\')" title="设置Mongodb管理员密码" class="btn btn-default btn-sm" type="button" style="margin-right: 5px;">root密码</button>\
            <span style="float:right">              \
                <button batch="true" style="float: right;display: none;margin-left:10px;" onclick="delDbBatch();" title="删除选中项" class="btn btn-default btn-sm">删除选中</button>\
            </span>\
            <div class="divtable mtb10">\
                <div class="tablescroll">\
                    <table id="DataBody" class="table table-hover" width="100%" cellspacing="0" cellpadding="0" border="0" style="border: 0 none;">\
                    <thead><tr><th width="30"><input class="check" onclick="checkSelect();" type="checkbox"></th>\
                    <th>数据库名</th>\
                    <th>用户名</th>\
                    <th>密码</th>\
                    '+
                    // '<th>备份</th>'+
                    '<th>备注</th>\
                    <th style="text-align:right;">操作</th></tr></thead>\
                    <tbody>\
                    '+ list +'\
                    </tbody></table>\
                </div>\
                <div id="databasePage" class="dataTables_paginate paging_bootstrap page"></div>\
                <div class="table_toolbar" style="left:0px;">\
                    <span class="sync btn btn-default btn-sm" style="margin-right:5px" onclick="syncToDatabase(1)" title="将选中数据库信息同步到服务器">同步选中</span>\
                    <span class="sync btn btn-default btn-sm" style="margin-right:5px" onclick="syncToDatabase(0)" title="将所有数据库信息同步到服务器">同步所有</span>\
                    <span class="sync btn btn-default btn-sm" onclick="syncGetDatabase()" title="从服务器获取数据库列表">从服务器获取</span>\
                </div>\
            </div>\
        </div>';

        $(".soft-man-con").html(con);
        $('#databasePage').html(rdata.page);

        readerTableChecked();
    });
}

function addDatabase(type){
    layer.open({
        type: 1,
        area: '500px',
        title: '添加数据库',
        closeBtn: 1,
        shift: 5,
        shadeClose: true,
        btn:["提交","关闭"],
        content: "<form class='bt-form pd20' id='add_db'>\
                    <div class='line'>\
                        <span class='tname'>数据库名</span>\
                        <div class='info-r'><input name='name' class='bt-input-text mr5' placeholder='新的数据库名称' type='text' style='width:65%' value=''>\
                        </div>\
                    </div>\
                    <div class='line'><span class='tname'>用户名</span><div class='info-r'><input name='db_user' class='bt-input-text mr5' placeholder='数据库用户' type='text' style='width:65%' value=''></div></div>\
                    <div class='line'>\
                    <span class='tname'>密码</span>\
                    <div class='info-r'><input class='bt-input-text mr5' type='text' name='password' id='MyPassword' style='width:330px' value='"+(randomStrPwd(16))+"' /><span title='随机密码' class='glyphicon glyphicon-repeat cursor' onclick='repeatPwd(16)'></span></div>\
                    </div>\
                    <div class='line'>\
                        <span class='tname'>访问权限</span>\
                        <div class='info-r '>\
                            <select class='bt-input-text mr5' name='dataAccess' style='width:100px'>\
                            <option value='127.0.0.1'>本地服务器</option>\
                            <option value=\"%\">所有人</option>\
                            <option value='ip'>指定IP</option>\
                            </select>\
                        </div>\
                    </div>\
                    <input type='hidden' name='ps' value='' />\
                  </form>",
        success:function(){
            $("input[name='name']").keyup(function(){
                var v = $(this).val();
                $("input[name='db_user']").val(v);
                $("input[name='ps']").val(v);
            });

            $('select[name="dataAccess"]').change(function(){
                var v = $(this).val();
                if (v == 'ip'){
                    $(this).after("<input id='dataAccess_subid' class='bt-input-text mr5' type='text' name='address' placeholder='多个IP使用逗号(,)分隔' style='width: 230px; display: inline-block;'>");
                } else {
                    $('#dataAccess_subid').remove();
                }
            });
        },
        yes:function(index) {
            var data = $("#add_db").serialize();
            data = decodeURIComponent(data);
            var dataObj = toArrayObject(data);
            if(!dataObj['address']){
                dataObj['address'] = dataObj['dataAccess'];
            }
            mgPost('add_db', '',dataObj, function(data){
                var rdata = $.parseJSON(data.data);
                showMsg(rdata.msg,function(){
                    if (rdata.status){
                        layer.close(index);
                        dbList();
                    }
                },{icon: rdata.status ? 1 : 2}, 2000);
            });
        }
    });
}

function setRootPwd(type, pwd){
    if (type==1){
        var password = $("#MyPassword").val();
        mgPost('set_root_pwd', '',{password:password}, function(data){
            var rdata = $.parseJSON(data.data);
            showMsg(rdata.msg,function(){
                dbList();
            },{icon: rdata.status ? 1 : 2});   
        });
        return;
    }

    var index = layer.open({
        type: 1,
        area: '500px',
        title: '修改数据库密码',
        closeBtn: 1,
        shift: 5,
        btn:["提交", "关闭", "复制ROOT密码", "强制修改"],
        shadeClose: true,
        content: "<form class='bt-form pd20' id='mod_pwd'>\
                    <div class='line'>\
                        <span class='tname'>root密码</span>\
                        <div class='info-r'><input class='bt-input-text mr5' type='text' name='password' id='MyPassword' style='width:330px' value='"+pwd+"' />\
                            <span title='随机密码' class='glyphicon glyphicon-repeat cursor' onclick='repeatPwd(16)'></span>\
                        </div>\
                    </div>\
                  </form>",
        yes:function(layerIndex){
            var password = $("#MyPassword").val();
            mgPost('set_root_pwd', '',{password:password}, function(data){
                var rdata = $.parseJSON(data.data);
                showMsg(rdata.msg,function(){
                    layer.close(layerIndex);
                    dbList();
                },{icon: rdata.status ? 1 : 2});   
            });
        },
        btn3:function(){
            var password = $("#MyPassword").val();
            copyText(password);
            return false;
        },
        btn4:function(layerIndex){
            layer.confirm('强制修改,是为了在重建时使用,确定强制?', {
                btn: ['确定', '取消']
            }, function(index, layero){
                layer.close(index);
                var password = $("#MyPassword").val();
                mgPost('set_root_pwd', '',{password:password,force:'1'}, function(data){
                    var rdata = $.parseJSON(data.data);
                    showMsg(rdata.msg,function(){
                        layer.close(layerIndex);
                        dbList();
                    },{icon: rdata.status ? 1 : 2});   
                });
            });
            return false;
        }
    });
}

function syncGetDatabase(){
    mgPost('sync_get_databases', '', '', function(data){
        var rdata = $.parseJSON(data.data);
        showMsg(rdata.msg,function(){
            dbList();
        },{ icon: rdata.status ? 1 : 2 });
    });
}

function showHidePass(obj){
    var a = "glyphicon-eye-open";
    var b = "glyphicon-eye-close";
    
    if($(obj).hasClass(a)){
        $(obj).removeClass(a).addClass(b);
        $(obj).prev().text($(obj).prev().attr('data-pw'))
    }
    else{
        $(obj).removeClass(b).addClass(a);
        $(obj).prev().text('***');
    }
}

function setDbPs(id, name, obj) {
    var _span = $(obj);
    var _input = $("<input class='baktext' value=\""+_span.text()+"\" type='text' placeholder='备注信息' />");
    _span.hide().after(_input);
    _input.focus();
    _input.blur(function(){
        $(this).remove();
        var ps = _input.val();
        _span.text(ps).show();
        var data = {name:name,id:id,ps:ps};
        mgPost('set_db_ps', '',data, function(data){
            var rdata = $.parseJSON(data.data);
            layer.msg(rdata.msg, { icon: rdata.status ? 1 : 2 });
        });
    });
    _input.keyup(function(){
        if(event.keyCode == 13){
            _input.trigger('blur');
        }
    });
}

function delDb(id, name){
    safeMessage('删除['+name+']','您真的要删除['+name+']吗？',function(){
        var data='id='+id+'&name='+name;
        mgPost('del_db', '', data, function(data){
            var rdata = $.parseJSON(data.data);
            showMsg(rdata.msg,function(){
                dbList();
            },{icon: rdata.status ? 1 : 2}, 600);
        });
    });
}

function delDbBatch(){
    var arr = [];
    $('input[type="checkbox"].check:checked').each(function () {
        var _val = $(this).val();
        var _name = $(this).parent().next().text();
        if (!isNaN(_val)) {
            arr.push({'id':_val,'name':_name});
        }
    });

    safeMessage('批量删除数据库','<a style="color:red;">您共选择了[2]个数据库,删除后将无法恢复,真的要删除吗?</a>',function(){
        var i = 0;
        $(arr).each(function(){
            var data  = mgAsyncPost('del_db', this);
            var rdata = $.parseJSON(data.data);
            if (!rdata.status){
                layer.msg(rdata.msg,{icon:2,time:2000,shade: [0.3, '#000']});
            }
            i++;
        });
        
        var msg = '成功删除['+i+']个数据库!';
        showMsg(msg,function(){
            dbList();
        },{icon: 1}, 600);
    });
}

function setDbPass(id, username, password){
    layer.open({
        type: 1,
        area: '500px',
        title: '修改数据库密码',
        closeBtn: 1,
        shift: 5,
        shadeClose: true,
        btn:["提交","关闭"],
        content: "<form class='bt-form pd20' id='mod_pwd'>\
                    <div class='line'>\
                        <span class='tname'>用户名</span>\
                        <div class='info-r'><input readonly='readonly' name=\"name\" class='bt-input-text mr5' type='text' style='width:330px;outline:none;' value='"+username+"' /></div>\
                    </div>\
                    <div class='line'>\
                    <span class='tname'>密码</span>\
                    <div class='info-r'>\
                        <input class='bt-input-text mr5' type='text' name='password' id='MyPassword' style='width:330px' value='"+password+"' />\
                        <span title='随机密码' class='glyphicon glyphicon-repeat cursor' onclick='repeatPwd(16)'></span></div>\
                    </div>\
                    <input type='hidden' name='id' value='"+id+"'>\
                </form>",
        yes:function(index){
            // var data = $("#mod_pwd").serialize();
            var data = {};
            data['name'] = $('input[name=name]').val();
            data['password'] = $('#MyPassword').val();
            data['id'] = $('input[name=id]').val();
            mgPost('set_user_pwd', '',data, function(data){
                var rdata = $.parseJSON(data.data);
                showMsg(rdata.msg,function(){
                    layer.close(index);
                    dbList();
                },{icon: rdata.status ? 1 : 2});   
            });
        }
    });
}

function repTools(db_name, res){
    mgPost('get_db_info', '', {name:db_name}, function(data){
        var rdata = $.parseJSON(data.data);
        var rdata = rdata.data;

        console.log(rdata.collection_list);
        var tbody = '';
        for (var i = 0; i < rdata.collection_list.length; i++) {
            tbody += '<tr>\
                    <td><span style="width:220px;"> ' + rdata.collection_list[i].collection_name + '</span></td>\
                    <td><span style="width:220px;"> ' + rdata.collection_list[i].count + '</span></td>\
                    <td>' + toSize(rdata.collection_list[i].size) + '</td>\
                    <td><span style="width:90px;"> ' + toSize(rdata.collection_list[i].avg_obj_size) + '</span></td>\
                    <td>' + toSize(rdata.collection_list[i].storage_size) + '</td>\
                    <td>' + rdata.collection_list[i].nindexes + '</td>\
                    <td>' + toSize(rdata.collection_list[i].total_index_size) + '</td>\
                </tr> '
        }

        if (res) {
            $(".gztr").html(tbody);
            $("#db_tools").html('');
            $("input[type='checkbox']").attr("checked", false);
            $(".tools_size").html('大小：' + rdata.data_size);
            return;
        }

        layer.open({
            type: 1,
            title: "MongoDB工具箱【" + db_name + "】",
            area: ['780px', '480px'],
            closeBtn: 1,
            shadeClose: false,
            content: '<div class="pd15">\
                            <div class="db_list">\
                                <span><a>数据库名称：'+ db_name + '</a>\
                                <a>集合：'+ rdata.collections + '</a>\
                                <a class="tools_size">存储大小：'+ toSize(rdata.storageSize) + '</a>\
                                <a class="tools_size">索引大小：'+ toSize(rdata.indexSize) + '</a>\
                                </span>\
                                <span id="db_tools" style="float: right;"></span>\
                            </div >\
                            <div class="divtable">\
                            <div  id="database_fix"  style="height:360px;overflow:auto;border:#ddd 1px solid">\
                            <table class="table table-hover "style="border:none">\
                                <thead>\
                                    <tr>\
                                        <th>集合名称</th>\
                                        <th>文档数量</th>\
                                        <th>内存中的大小</th>\
                                        <th>对象平均大小</th>\
                                        <th>存储大小</th>\
                                        <th>索引数量</th>\
                                        <th>索引大小</th>\
                                    </tr>\
                                </thead>\
                                <tbody class="gztr">' + tbody + '</tbody>\
                            </table>\
                            </div>\
                        </div>\
                    </div>'
        });
        tableFixed('database_fix');
    });
}
