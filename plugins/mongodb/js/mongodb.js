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


function mgPostN(method, version, args,callback){

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
					<tr><th>hosts</th><td><span class="overflow_hide" style="width:300px;word-wrap: break-word;white-space:pre-wrap;" title="'+rdata.hosts+'">' + rdata.hosts + '</span></td><td>服务器所有节点</td></tr>\
					<tr><th>primary</th><td>' + rdata.primary + '</td><td>主节点</td></tr>\
					<tr><th>me</th><td>' + rdata.me + '</td><td>本机</td></tr>';
		}

		var tbody_members = '';
		var member_list = rdata['members'];
		for (var i = 0; i < member_list.length; i++) {
			tbody_members += '<tr><th>'+member_list[i]['name']+'</th><td>' + member_list[i]['stateStr'] + '</td><td>'+member_list[i]['uptime']+'</td></tr>';
		}

		// console.log(rdata);
		var repl_on = 'btn-danger';
		var repl_on_title = '未开启';
		if ('repl_name' in rdata && rdata['repl_name'] != ''){
			repl_on = '';
			repl_on_title = '已开启';
		}

		var con = "<p class='conf_p'>\
                    <span class='f14 c6 mr20'>Mongodb副本配置</span><span class='f14 c6 mr20'></span>\
                    <button class='btn btn-success btn-xs "+repl_on+"'>"+repl_on_title+"</button>\
                    <button class='btn btn-success btn-xs' onclick='mongoReplCfg()'>配置</button>\
                </p><hr/>";

        con += '<div class="divtable">\
				<table class="table table-hover table-bordered" style="width: 660px;">\
					<thead><th>字段</th><th>当前值</th><th>说明</th></thead>\
					<tbody>'+tbody+'<tbody>\
				</table>\
			</div>';

		con += '<div class="divtable" style="margin-top:5px;">\
				<table class="table table-hover table-bordered" style="width: 660px;">\
					<thead><th>IP</th><th>状态</th><th>在线</th></thead>\
					<tbody>'+tbody_members+'<tbody>\
				</table>\
			</div>';

        $(".soft-man-con").html(con);
    },'json');
}

//设置副本名称
function mongoReplCfgReplSetName(){
	// <select class='bt-input-text mr5' name='replSetName' style='width:100px'><option value=''></option></select>
    layer.open({
        type: 1,
        area: '300px',
        title: '设置副本名称',
        closeBtn: 1,
        shift: 5,
        shadeClose: false,
        btn:["提交","关闭"],
        content: "<form class='bt-form pd20' id='mod_pwd'>\
                    <div class='line'>\
                    <span class='tname'>同步副本名称</span>\
                    <div class='info-r'>\
                        <input class='bt-input-text mr5' name='replSetName' style='width:100px' />\
                    </div>\
                    </div>\
                </form>",

        success: function(){
    		// // console.log(rdata);
    		// var rlist = rdata['dbs'];
    		// var dbs = [];
    		// var selectHtml = '';
    		// for (var i = 0; i < rlist.length; i++) {
    		// 	// console.log(rlist[i]['db']);
    		// 	var dbname = rlist[i]['db'];

    		// 	if (['admin','local','config'].includes(dbname)){
    		// 	} else {
    		// 		dbs.push(dbname);
    		// 	}
    		// }

    		// if (dbs.length == 0 ){
    		// 	selectHtml += "<option value=''>无</option>";
    		// }

    		// for (index in dbs) {
    		// 	selectHtml += "<option value='"+dbs[index]+"'>"+dbs[index]+"</option>";
    		// }

    		// $('select[name="replSetName"]').html(selectHtml);
        },
        yes:function(index){
        	var data = {};
            data['name'] = $('input[name=replSetName]').val();
            if (data['name'] == ''){
            	layer.msg("副本名称不能为空");
            	return;
            }
            mgPost('repl_set_name', '',data, function(data){
                var rdata = $.parseJSON(data.data);
                showMsg(rdata.msg,function(){
                    if (rdata['status']){
                		layer.close(index);
                		mongoReplCfgInit();
                	}
                },{icon: rdata.status ? 1 : 2});   
            });
        }
    });
}

function mongoReplCfgNodes(idx,host, priority, votes, arbiterOnly){

	if (typeof(host) == 'undefined'){
		host = '127.0.0.1:27017';
	}

	if (typeof(priority) == 'undefined'){
		priority = '1';
	}

	if (typeof(votes) == 'undefined'){
		votes = '1';
	}

	if (typeof(arbiterOnly) == 'undefined'){
		arbiterOnly = '1';
	}

	var title_name = '添加节点';
	if (idx>-1){
		title_name = '编辑节点';
	}

	layer.open({
        type: 1,
        area: '500px',
        title: '添加节点',
        closeBtn: 1,
        shift: 5,
        shadeClose: true,
        btn:["提交","关闭"],
        content: "<form class='bt-form pd20'>\
                    <div class='line'>\
	                    <span class='tname'>节点服务:</span>\
	                    <div class='info-r'>\
	                        <input class='bt-input-text mr5' type='text' name='node' style='width:330px' value='"+host+"'/>\
	                    </div>\
                    </div>\
                    <div class='line'>\
	                    <span class='tname'>priority:</span>\
	                    <div class='info-r'>\
	                        <input class='bt-input-text mr5' type='number' name='priority' style='width:220px' value='"+priority+"'/>\
	                        <span class='c9'>值越大，优先权越高</span>\
	                    </div>\
                    </div>\
                    <div class='line'>\
	                    <span class='tname'>votes:</span>\
	                    <div class='info-r'>\
	                        <input class='bt-input-text mr5' type='number' name='votes' style='width:220px' value='"+votes+"'/>\
	                        <span class='c9'>一般是0或者1</span>\
	                    </div>\
                    </div>\
                    <div class='line'>\
	                    <span class='tname'>仲裁员:</span>\
	                    <div class='info-r'>\
	                        <select class='bt-input-text mr5' name='arbiterOnly'>\
	                        	<option value='0' "+(arbiterOnly == "0" ? 'checked':'')+">否</option>\
	                        	<option value='1' "+(arbiterOnly == "1" ? 'checked':'')+">是</option>\
	                        </select>\
	                    </div>\
                    </div>\
                </form>",
        yes:function(index){
            // var data = $("#mod_pwd").serialize();
            var data = {};
            data['node'] = $('input[name=node]').val();
            data['priority'] = $('input[name=priority]').val();
            data['votes'] = $('input[name=votes]').val();
            data['arbiterOnly'] = $('select[name=arbiterOnly]').val();
            data['idx'] = idx;
            mgPost('repl_set_node', '',data, function(data){
                var rdata = $.parseJSON(data.data);
                showMsg(rdata.msg,function(){
                	if (rdata['status']){
                		layer.close(index);
                		mongoReplCfgInit();
                	}
                },{icon: rdata.status ? 1 : 2},rdata['status']?2000:10000);
            });
        }
    });
}

function mongoReplCfgDelNode(host){
	mgPost('del_repl_node', '', {"node":host}, function(data){
		var rdata = $.parseJSON(data.data);
		// console.log(rdata['status']);
        showMsg(rdata.msg,function(){
        	if (rdata['status']){
        		mongoReplCfgInit();
        	}
        },{icon: rdata.status ? 1 : 2});
	});
}

function mongoReplCfgInit(){
	mgPostN('get_repl_config', '', '', function(data){
		var rdata = $.parseJSON(data.data);
		$('#repl_name').html("同步副本："+rdata.data['name']);

		var node = '';
		for (var i = 0; i < rdata.data['nodes'].length; i++) {
			var t = rdata.data['nodes'][i];

			var arbiterOnly = '否';
			if(t['arbiterOnly']==1){
				arbiterOnly = '是';
			}

			var op = '<a href="javascript:;" class="btlink" onclick="mongoReplCfgDelNode(\''+t['host']+'\');" title="删除">删除</a>';
			op += ' | <a href="javascript:;" class="btlink" onclick="mongoReplCfgNodes(\''+i+'\',\''+t['host']+'\',\''+t['priority']+'\',\''+t['votes']+'\',\''+t['arbiterOnly']+'\');" title="编辑">编辑</a>';
			node += '<tr><td>'+t['host']+'</td><td>'+t['priority']+'</td><td>'+t['votes']+'</td><td>'+arbiterOnly+'</td><td>'+op+'</td></tr>';
		}
		$('#repl_node tbody').html(node);
	});
}

function mongoReplCfg(){
	layer.open({
        type: 1,
        title: "副本设置",
        area: ['580px', '380px'],
        closeBtn: 1,
        shadeClose: false,
        btn: ["初始化","取消","添加节点","设置同步副本","关闭副本同步"],
        content: '<div class="pd15">\
                <div class="db_list">\
                    <span>\
                    	<a id="repl_name">同步副本：</a>\
                    </span>\
                </div>\
                <div class="divtable" id="repl_node">\
	                <div id="database_fix"  style="height:210px;overflow:auto;border:#ddd 1px solid">\
	                <table class="table table-hover "style="border:none">\
	                    <thead>\
	                        <tr>\
	                            <th>节点</th>\
	                            <th>优先级</th>\
	                            <th>投票</th>\
	                            <th>仲裁者</th>\
	                            <th>操作</th>\
	                        </tr>\
	                    </thead>\
	                    <tbody class="gztr"></tbody>\
	                </table>\
                </div>\
            </div>\
        </div>',
        success:function(){
        	mongoReplCfgInit();
        },
        yes:function(){
        	mgPost('repl_init', '', '', function(data){
        		var rdata = $.parseJSON(data.data);
				showMsg(rdata.msg,function(){
					mongoReplStatus();
		        },{icon: rdata.status ? 1 : 2});
			});
        	return false;
        },
        btn3:function(){
        	mongoReplCfgNodes(-1);
            return false;
        },
        btn4:function(){
        	mongoReplCfgReplSetName();
            return false;
        },
        btn5:function(){
        	mgPost('repl_close', '', '', function(data){
        		var rdata = $.parseJSON(data.data);
				showMsg(rdata.msg,function(){
					if (rdata['status']){
						mongoReplStatus();
					}
		        },{icon: rdata.status ? 1 : 2});
			});
        	return false;
        }
    });
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
   	// console.log(_data);
    mgPost('get_db_list', '',_data, function(data){
    	// console.log(data);
        var rdata = $.parseJSON(data.data);
        // console.log(rdata);
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

            list += '<a href="javascript:;" class="btlink" class="btlink" onclick="setBackup(\''+rdata.data[i]['name']+'\',this)" title="数据库备份">'+(rdata.data[i]['is_backup']?'已备份':'未备份') +'</a> | ';

            list += '<a href="javascript:;" class="btlink" onclick="repTools(\''+rdata.data[i]['name']+'\')" title="MongoDB优化修复工具">工具</a> | ' +
                        '<a href="javascript:;" class="btlink" onclick="setDbAccess(\''+rdata.data[i]['username']+'\',\''+rdata.data[i]['name']+'\')" title="设置数据库权限">权限</a> | ' +
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
        // console.log(rdata.collection_list);
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

function syncToDatabase(type){
    var data = [];
    $('input[type="checkbox"].check:checked').each(function () {
        if (!isNaN($(this).val())) data.push($(this).val());
    });
    var postData = 'type='+type+'&ids='+JSON.stringify(data); 
    mgPost('sync_to_databases', '',postData, function(data){
        var rdata = $.parseJSON(data.data);
        // console.log(rdata);
        showMsg(rdata.msg,function(){
            dbList();
        },{ icon: rdata.status ? 1 : 2 });
    });
}

function setDbAccess(username,name){
    mgPost('get_db_access','','username='+username, function(data){
        var rdata = $.parseJSON(data.data);
        if (!rdata.status){
            layer.msg(rdata.msg,{icon:2,shade: [0.3, '#000']});
            return;
        }
        var db_roles = rdata.data.roles;
        var all_roles = rdata.data.all_roles;
        // console.log(all_roles);
        var role_list;
        var index = layer.open({
            type: 1,
            area: '500px',
            title: '设置数据库权限',
            closeBtn: 1,
            shift: 5,
            btn:["提交","取消"],
            shadeClose: true,
            content: "<form class='bt-form pd20' id='set_db_access'>\
                        <div class='line'>\
                            <span class='tname'>访问权限</span>\
                            <div class='info-r'>\
                                <div id='role_list'></div>\
                            </div>\
                        </div>\
                      </form>",
            success:function(layers, index){
            	document.getElementById('layui-layer' + index).getElementsByClassName('layui-layer-content')[0].style.overflow = 'unset';

            	var role_data = [];
            	for (var i = 0; i < db_roles.length; i++) {
            		var t = {};
            		t['name'] = db_roles[i]['role'];
            		t['value'] = db_roles[i]['role'];
            		role_data.push(t);	
            	}

                role_list = xmSelect.render({
                    el: '#role_list',
                    language: 'zn',
                    toolbar: {show: true,},
                    paging: false,
                    data: role_data,
                });

                var pdata = [];
                for (var i = 0; i < all_roles.length; i++) {
                    var tval = all_roles[i];
                    var isSelected = false;
                    for (var db_i = 0; db_i < db_roles.length; db_i++) {
	            		var db_name = db_roles[db_i]['role'];
	            		if (db_name == tval['role']){
	            			isSelected = true;
	            		}
	            	}

	            	var t = {name:tval['name'],value:tval['role']};
	            	if (isSelected){
	            		t = {name:tval['name'],value:tval['role'], selected: true};
	            	}  
                    pdata.push(t);
                }
                role_list.update({data:pdata});
            },
            yes:function(index){
                var data = $("#set_db_access").serialize();
                data = decodeURIComponent(data);
                var dataObj = toArrayObject(data);
                dataObj['username'] = username;
                dataObj['name'] = name;
                mgPost('set_db_access', '',dataObj, function(data){
                    var rdata = $.parseJSON(data.data);
                    showMsg(rdata.msg,function(){
                        layer.close(index);
                        dbList();
                    },{icon: rdata.status ? 1 : 2});   
                });
            }
        });

    });
}


function setBackup(db_name){
    var layerIndex = layer.open({
        type: 1,
        title: "数据库[MongoDB]备份详情",
        area: ['600px', '280px'],
        closeBtn: 1,
        shadeClose: false,
        content: '<div class="pd15">\
                    <div class="db_list">\
                        <button id="btn_backup" class="btn btn-success btn-sm" type="button">备份</button>\
                        <button id="btn_local_import" class="btn btn-success btn-sm" type="button">外部导入</button>\
                    </div >\
                    <div class="divtable">\
                    <div  id="database_fix"  style="height:150px;overflow:auto;border:#ddd 1px solid">\
                    <table id="database_table" class="table table-hover "style="border:none">\
                        <thead>\
                            <tr>\
                                <th>文件名称</th>\
                                <th>文件大小</th>\
                                <th>备份时间</th>\
                                <th style="text-align: right;">操作</th>\
                            </tr>\
                        </thead>\
                        <tbody class="list"></tbody>\
                    </table>\
                    </div>\
                </div>\
        </div>',
        success:function(index){
            $('#btn_backup').click(function(){
                mgPost('set_db_backup', '',{name:db_name}, function(data){
                    showMsg('执行成功!', function(){
                        setBackupReq(db_name);
                    }, {icon:1}, 2000);
                });
            });

            $('#btn_local_import').click(function(){
                setLocalImport(db_name);
            });

            setBackupReq(db_name);
        },
    });
}

function setBackupReq(db_name, obj){
     mgPost('get_db_backup_list', '', {name:db_name}, function(data){
        var rdata = $.parseJSON(data.data);
        var tbody = '';
        for (var i = 0; i < rdata.data.length; i++) {
            tbody += '<tr>\
                    <td><span> ' + rdata.data[i]['name'] + '</span></td>\
                    <td><span> ' + rdata.data[i]['size'] + '</span></td>\
                    <td><span> ' + rdata.data[i]['time'] + '</span></td>\
                    <td style="text-align: right;">\
                        <a class="btlink" onclick="importBackup(\'' + rdata.data[i]['name'] + '\',\'' +db_name+ '\')">导入</a> | \
                        <a class="btlink" onclick="downloadBackup(\'' + rdata.data[i]['file'] + '\')">下载</a> | \
                        <a class="btlink" onclick="delBackup(\'' + rdata.data[i]['name'] + '\',\'' +db_name+ '\')">删除</a>\
                    </td>\
                </tr> ';
        }
        $('#database_table tbody').html(tbody);
    });
}

function delBackup(filename, name, path){
    if(typeof(path) == "undefined"){
        path = "";
    }
    mgPost('delete_db_backup','',{filename:filename,path:path},function(){
        layer.msg('执行成功!');
        setTimeout(function(){
            setBackupReq(name);
        },2000);
    });
}

function downloadBackup(file){
    window.open('/files/download?filename='+encodeURIComponent(file));
}

function importBackup(file,name){
    mgPost('import_db_backup','',{file:file,name:name}, function(data){
        layer.msg('执行成功!');
    });
}

function setLocalImport(db_name){

    //上传文件
    function uploadDbFiles(upload_dir){
        var up_db = layer.open({
            type:1,
            closeBtn: 1,
            title:"上传导入文件["+upload_dir+']',
            area: ['500px','300px'],
            shadeClose:false,
            content:'<div class="fileUploadDiv">\
                    <input type="hidden" id="input-val" value="'+upload_dir+'" />\
                    <input type="file" id="file_input"  multiple="true" autocomplete="off" />\
                    <button type="button"  id="opt" autocomplete="off">添加文件</button>\
                    <button type="button" id="up" autocomplete="off" >开始上传</button>\
                    <span id="totalProgress" style="position: absolute;top: 7px;right: 147px;"></span>\
                    <span style="float:right;margin-top: 9px;">\
                    <font>文件编码:</font>\
                    <select id="fileCodeing" >\
                        <option value="byte">二进制</option>\
                        <option value="utf-8">UTF-8</option>\
                        <option value="gb18030">GB2312</option>\
                    </select>\
                    </span>\
                    <button type="button" id="filesClose" autocomplete="off">关闭</button>\
                    <ul id="up_box"></ul>\
                </div>',
            success:function(){
                $('#filesClose').click(function(){
                    layer.close(up_db);
                });
            }

        });
        uploadStart(function(){
            getList();
            layer.close(up_db);
        });
    }

    function getList(){
        mgPost('get_db_backup_import_list','',{}, function(data){
            var rdata = $.parseJSON(data.data);

            var file_list = rdata.data.list;
            var upload_dir = rdata.data.upload_dir;

            var tbody = '';
            for (var i = 0; i < file_list.length; i++) {
                tbody += '<tr>\
                        <td><span> ' + file_list[i]['name'] + '</span></td>\
                        <td><span> ' + file_list[i]['size'] + '</span></td>\
                        <td><span> ' + file_list[i]['time'] + '</span></td>\
                        <td style="text-align: right;">\
                            <a class="btlink" onclick="importDbExternal(\'' + file_list[i]['name'] + '\',\'' +db_name+ '\')">导入</a> | \
                            <a class="btlink del" index="'+i+'">删除</a>\
                        </td>\
                    </tr>';
            }

            $('#import_db_file_list').html(tbody);
            $('input[name="upload_dir"]').val(upload_dir);

            $("#import_db_file_list .del").on('click',function(){
                var index = $(this).attr('index');
                var filename = file_list[index]["name"];
                mgPost('delete_db_backup','',{filename:filename,path:upload_dir},function(){
                    showMsg('执行成功!', function(){
                        getList();
                    },{icon:1},2000);
                });
            });
        });
    }

    var layerIndex = layer.open({
        type: 1,
        title: "从文件导入数据",
        area: ['600px', '380px'],
        closeBtn: 1,
        shadeClose: false,
        content: '<div class="pd15">\
                    <div class="db_list">\
                        <button id="btn_file_upload" class="btn btn-success btn-sm" type="button">从本地上传</button>\
                    </div >\
                    <div class="divtable">\
                    <input type="hidden" name="upload_dir" value=""> \
                    <div id="database_fix"  style="height:150px;overflow:auto;border:#ddd 1px solid">\
                    <table class="table table-hover "style="border:none">\
                        <thead>\
                            <tr>\
                                <th>文件名称</th>\
                                <th>文件大小</th>\
                                <th>备份时间</th>\
                                <th style="text-align: right;">操作</th>\
                            </tr>\
                        </thead>\
                        <tbody  id="import_db_file_list" class="gztr"></tbody>\
                    </table>\
                    </div>\
                    <ul class="help-info-text c7">\
                        <li>仅支持sql、zip、sql.gz、(tar.gz|gz|tgz)</li>\
                        <li>zip、tar.gz压缩包结构：test.zip或test.tar.gz压缩包内，必需包含test.sql</li>\
                        <li>若文件过大，您还可以使用SFTP工具，将数据库文件上传到/www/backup/import</li>\
                    </ul>\
                </div>\
        </div>',
        success:function(index){
            $('#btn_file_upload').click(function(){
                var upload_dir = $('input[name="upload_dir"]').val();
                uploadDbFiles(upload_dir);
            });

            getList();
        },
    });  
}

function importDbExternal(file,name){
    mgPost('import_db_external','',{file:file,name:name}, function(data){
        layer.msg('执行成功!');
    });
}

function mgdbReadme(){
    var readme = '<ul class="help-info-text c7">';
    readme += '<li>认证同步说明</li>';
    readme += '<li>root/用户,配置Key完全一致才能同步。</li>';
    readme += '</ul>';

    $('.soft-man-con').html(readme);   
}

