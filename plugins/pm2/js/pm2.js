
function str2Obj(str){
    var data = {};
    kv = str.split('&');
    for(i in kv){
        v = kv[i].split('=');
        data[v[0]] = v[1];
    }
    return data;
}


function pm2Post(method,args,callback){

    var _args = null; 
    if (typeof(args) == 'string'){
        _args = JSON.stringify(str2Obj(args));
    } else {
        _args = JSON.stringify(args);
    }

    var loadT = layer.msg('正在获取中...', { icon: 16, time: 0, shade: 0.3 });
    $.post('/plugins/run', {name:'pm2', func:method, args:_args}, function(data) {
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



function pm2List() {
	var con = '<div class="divtable" style="width:620px;">\
				<input class="bt-input-text mr5" id="mmpath" name="path" type="text" value="" style="width:260px" placeholder="项目所在根目录">\
				<span onclick="changePath(\'mmpath\')" class="glyphicon glyphicon-folder-open cursor mr20"></span>\
				<input class="bt-input-text mr5" name="run" type="text" value="" style="width:150px" placeholder="启动文件名称">\
				<input class="bt-input-text mr5" name="pname" type="text" value="" style="width:100px" placeholder="项目名称">\
				<button class="btn btn-default btn-sm va0" onclick="addNode();">添加</button>\
				<table class="table table-hover" style="margin-top: 10px; max-height: 380px; overflow: auto;">\
					<thead>\
						<tr><th>名称</th>\
						<th>模式</th>\
						<th>端口</th>\
						<th>状态</th>\
						<th>重启</th>\
						<th>时间</th>\
						<th>CPU</th>\
						<th>内存</th>\
						<th>目录</th>\
						<th style="text-align: right;" width="150">操作</th></tr>\
					</thead>\
					<tbody id="pmlist"></tbody>\
				</table>\
		</div>';

	$(".soft-man-con").html(con);


	pm2Post('list','', function(data){
		var rdata = $.parseJSON(data.data);
		// console.log(rdata);
		if (!rdata['status']){
            layer.msg(rdata['msg'],{icon:2,time:2000,shade: [0.3, '#000']});
            return;
        }

        var tbody = '';
        var tmp = rdata['data'];
        for(var i=0;i<tmp.length;i++){
            if(tmp[i].status != 'online'){
                var opt = '<a href="javascript:nodeStart(\''+tmp[i].name+'\')" class="btlink">启动</a> | ';
            }else{
                var opt = '<a href="javascript:nodeStop(\''+tmp[i].name+'\')" class="btlink">停止</a> | ';
            }
            tmp[i].path = tmp[i].path.replace('//','');
            
            var status = '<span style="color:rgb(92, 184, 92)" class="glyphicon glyphicon-play"></span>';
            if(tmp[i].status != 'online'){
                status = '<span style="color:rgb(255, 0, 0);" class="glyphicon glyphicon-pause"></span>';
            }
            
            tbody += '<tr>\
                        <td>'+tmp[i].name+'</td>\
                        <td>'+tmp[i].mode+'</td>\
                        <td>'+tmp[i].port+'</td>\
                        <td>'+status+'</td>\
                        <td>'+tmp[i].restart+'</td>\
                        <td>'+tmp[i].uptime+'</td>\
                        <td>'+tmp[i].cpu+'</td>\
                        <td>'+tmp[i].mem+'</td>\
                        <td><span onclick="openPath(\''+tmp[i].path+'\')" class="btlink cursor mr20" title="'+tmp[i].path+'">打开</span></td>\
                        <td style="text-align: right;">\
                            '+opt+'<a href="javascript:nodeLog(\''+tmp[i].name+'\')" class="btlink">日志</a> | <a href="javascript:delNode(\''+tmp[i].name+'\')" class="btlink">删除</a>\
                        </td>\
                    </tr>';
        }
        
        $("#pmlist").html(tbody);
	});
}



//取版本号列表
function getNodeVersions(){
    var loadT = layer.msg('正在获取版本列表...',{icon:16,time:0,shade: [0.3, '#000']});
    $.get('/plugin?action=a&s=Versions&name=pm2',function(versions){
        layer.close(loadT);
        
        
    });

    pm2Post('versions', '', function(data){
    	
    	var rdata = $.parseJSON(data.data);
        var versions = rdata.data;

    	var opt = '';
        for(var i=0;i<versions.list.length;i++){
            if(versions.list[i] == versions.version){
                opt += '<option value="'+versions.list[i]+'" selected="selected">'+versions.list[i]+'</option>';
            }else{
                opt += '<option value="'+versions.list[i]+'">'+versions.list[i]+'</option>';
            }
        }
        var con = '<div class="divtable" style="width: 620px;">\
		                <span>当前版本</span><select style="margin-left: 5px;width:100px;" class="bt-input-text" name="versions">'+opt+'</select>\
		                <button style="margin-bottom: 3px;margin-left: 5px;" class="btn btn-success btn-sm" onclick="setNodeVersion()">切换版本</button>\
		                <ul class="help-info-text c7 mtb15">\
		                    <li>当前版本为<font style="color:red;">['+versions.version+']</font></li>\
		                    <li>版本切换是全局的,切换版本后可能影响您正在运行的项目</li>\
		                </ul>\
                   </div>';
        $(".soft-man-con").html(con);
    });
}


//切换版本
function setNodeVersion(){
    var version = $("select[name='versions']").val();
    var data = "version="+version;
    pm2Post('set_node_version', data, function(data){
        var rdata = $.parseJSON(data.data);
        layer.msg(rdata.msg,{icon:rdata.status?1:2});
        if(rdata.status) {
            getNodeVersions();
        }
    });
}


//取模块列表
function getModList(){
    var con = '<div class="divtable" style="width: 620px;">\
                <input class="bt-input-text mr5" name="mname" type="text" value="" style="width:240px" placeholder="模块名称" />\
                <button class="btn btn-default btn-sm va0" onclick="installMod();">安装</button>\
                <table class="table table-hover" style="margin-top: 10px; max-height: 380px; overflow: auto;">\
                    <thead>\
                        <tr>\
                            <th>名称</th>\
                            <th>版本</th>\
                            <th style="text-align: right;">操作</th>\
                        </tr>\
                    </thead>\
                    <tbody id="modlist"></tbody>\
                </table>\
                <ul class="help-info-text c7 mtb15">\
                    <li>此处安装的模块均为安装到全局.</li>\
                    <li>仅安装到当前正在使用的nodejs版本.</li>\
                </ul>\
            </div>';

    $(".soft-man-con").html(con);

    pm2Post('mod_list', '', function(data){
        var rdata = $.parseJSON(data.data);
        var tbody = '';
        var tmp = rdata['data'];
        for(var i=0;i<tmp.length;i++){
            tbody += '<tr>\
                        <td>'+tmp[i].name+'</td>\
                        <td>'+tmp[i].version+'</td>\
                        <td style="text-align: right;">\
                            <a href="#" class="btlink" onclick="uninstallMod(\''+tmp[i].name+'\')">卸载</a>\
                        </td>\
                    </tr>';
        }
        $("#modlist").html(tbody);
    });
}


//安装模块
function installMod(){
    var mname = $("input[name='mname']").val();
    if(!mname){
        layer.msg('模块名称不能为空!',{icon:2});
        return;
    }
    
    // var loadT = layer.msg('正在安装模块['+mname+']...',{icon:16,time:0,shade: [0.3, '#000']});
    // $.post('/plugin?action=a&s=InstallMod&name=pm2',data,function(rdata){
    //     layer.close(loadT);
    //     layer.msg(rdata.msg,{icon:rdata.status?1:2});
    //     if(rdata.status) GetModList();
    // });
    
    var data = {mname:mname};
    pm2Post('install_mod', data, function(data){
        var rdata = $.parseJSON(data.data);
        layer.msg(rdata.msg,{icon:rdata.status?1:2});
        if(rdata.status) {
            getModList();
        }
    });
}


function uninstallMod(mname){
    safeMessage('卸载模块['+mname+']','卸载['+mname+']模块后,可能影响现有项目,继续吗?',function(){
        var data = "mname="+mname;
        pm2Post('uninstall_mod', data, function(data){
            var rdata = $.parseJSON(data.data);
            layer.msg(rdata.msg,{icon:rdata.status?1:2});
            if(rdata.status) {
                getModList();
            }
        });
    });
}

function addNode(){
	var data = {path:$("input[name='path']").val(),pname:$("input[name='pname']").val(),run:$("input[name='run']").val()}
	if(!data.path || !data.pname || !data.run){
        layer.msg('表单不完整，请检查!',{icon:2});
        return;
    }

    pm2Post('add', data, function(data){
    	var rdata = $.parseJSON(data.data);
        layer.msg(rdata.msg,{icon:rdata.status?1:2});
        pm2List();
    });
}

function delNode(pname){
    safeMessage('删除项目['+pname+']','删除['+pname+']项目后,该项目将无法被访问,继续吗?',function(){
        var data = "pname="+pname;
        pm2Post('delete', data, function(data){
        	var rdata = $.parseJSON(data.data);
	        layer.msg(rdata.msg,{icon:rdata.status?1:2});
	        pm2List();
        });
    });
}

function nodeStop(pname){
	var data = 'pname=' + pname;
	pm2Post('stop', data, function(data){
    	var rdata = $.parseJSON(data.data);
        layer.msg(rdata.msg,{icon:rdata.status?1:2});
        pm2List();
    });
}

function nodeStart(pname){
	var data = 'pname=' + pname;
	pm2Post('start', data, function(data){
    	var rdata = $.parseJSON(data.data);
        layer.msg(rdata.msg,{icon:rdata.status?1:2});
        pm2List();
    });
}

function pm2RollingLogs(func,pname){
    var args = {'pname':pname}
    _args = JSON.stringify(args);
    pluginRollingLogs('pm2','',func, _args);
}

function nodeLog(pname){
	var html = '';
    html += '<button onclick="pm2RollingLogs(\'node_log_run\',\''+pname+'\')" class="btn btn-default btn-sm">运行日志</button>';
    html += '<button onclick="nodeLogClearRun(\''+pname+'\')" class="btn btn-default btn-sm">清空运行日志</button>';
    html += '<button onclick="pm2RollingLogs(\'node_log_err\',\''+pname+'\')" class="btn btn-default btn-sm">错误日志</button>';
    html += '<button onclick="nodeLogClearError(\''+pname+'\')" class="btn btn-default btn-sm">清空错误日志</button>';

    var loadOpen = layer.open({
        type: 1,
        title: '日志',
        area: '240px',
        content:'<div class="change-default pd20">'+html+'</div>'
    });
}


function nodeLogClearRun(pname){
    var data = 'pname=' + pname;
    pm2Post('node_log_clear_run', data, function(data){
        var rdata = $.parseJSON(data.data);
        layer.msg(rdata.msg,{icon:rdata.status?1:2});
    });
}

function nodeLogClearError(pname){
    var data = 'pname=' + pname;
    pm2Post('node_log_clear_err', data, function(data){
        var rdata = $.parseJSON(data.data);
        layer.msg(rdata.msg,{icon:rdata.status?1:2});
    });
} 