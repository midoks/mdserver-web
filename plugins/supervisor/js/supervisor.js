
function myPost(method,args,callback, title){

    var _args = null; 
    if (typeof(args) == 'string'){
        _args = JSON.stringify(str2Obj(args));
    } else {
        _args = JSON.stringify(args);
    }

    var _title = '正在获取...';
    if (typeof(title) != 'undefined'){
        _title = title;
    }

    var loadT = layer.msg(_title, { icon: 16, time: 0, shade: 0.3 });
    $.post('/plugins/run', {name:'supervisor', func:method, args:_args}, function(data) {
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



function supList(page, search){
    var _data = {};
    if (typeof(page) =='undefined'){
        var page = 1;
    }
    
    _data['page'] = page;
    _data['page_size'] = 10;
    if(typeof(search) != 'undefined'){
        _data['search'] = search;
    }

    myPost('get_sup_list', _data, function(data){
        var rdata = $.parseJSON(data.data);
        // console.log(rdata.data);
        var list = '';
        for(i in rdata.data){
            list += '<tr>';
            list += '<td>' + rdata.data[i]['program'] +'</td>';
            list += '<td>' + rdata.data[i]['command'] +'</td>';
            list += '<td>' + rdata.data[i]['user'] +'</td>';
            list += '<td>' + rdata.data[i]['pid'] +'</td>';
            list += '<td>' + rdata.data[i]['numprocs'] +'</td>';
            list += '<td>' + rdata.data[i]['priority'] +'</td>';
			
			sup_status = 'start'
			sup_status_desc = 'start'
            if (rdata.data[i]['runStatus'] == 'RUNNING' ){
            	sup_status = 'start'
            	sup_status_desc = '已启动'
            } else{
            	sup_status = 'stop'
            	sup_status_desc = '已停止'
            }

            list += '<td>'+sup_status_desc+'</td>';

			list += '<td>' + rdata.data[i]['runStatus'] +'</td>';

            list += '<td style="text-align:right">\
            			<a href="javascript:;" class="btlink" onclick="startOrStop(\''+rdata.data[i]['program']+'\',\''+sup_status+'\')" title="启动|停止">'+sup_status_desc+'</a> | ' +
            			'<a href="javascript:;" class="btlink" onclick="restartJob(\''+rdata.data[i]['program']+'\',\''+sup_status+'\')" title="重启">重启</a> | ' +
                        '<a href="javascript:;" class="btlink" onclick="updateJob(\''+rdata.data[i]['program']+'\')">修改</a> | ' +
                        '<a href="javascript:;" class="btlink" onclick="delJob(\''+rdata.data[i]['program']+'\')" title="删除">删除</a>' +
                    '</td>';

            list += '</tr>';
        }

        if(rdata.data.length==0){
        	list = "<tr><td colspan='9'>当前没有数据</td></tr>";
        }

        var con = '<div class="safe bgw">\
            <button onclick="supAdd()" title="添加守护进程" class="btn btn-success btn-sm" type="button" style="margin-right: 5px;">添加守护进程</button>\
            <div class="divtable mtb10">\
                <div class="tablescroll">\
                    <table id="DataBody" class="table table-hover" width="100%" cellspacing="0" cellpadding="0" border="0" style="border: 0 none;">\
                    <thead>\
                    <th>名称</th>\
                    <th>启动命令</th>\
                    <th>启动用户</th>\
                    <th>进程ID</th>\
                    <th>进程数量</th>\
                    <th>优先级</th>\
                    <th>进程管理</th>\
                    <th>状态</th>\
                    <th style="text-align:right;">操作</th></tr></thead>\
                    <tbody>\
                    '+ list +'\
                    </tbody></table>\
                </div>\
                <div id="databasePage" class="dataTables_paginate paging_bootstrap page"></div>\
            </div>\
        </div>';
        
        con += '<div class="code">\
            <span>supervisord 常见进程状态详细如下：</span>\
            <span>1：STOPPED：该进程已停止。 2：STOPPING：由于停止请求，该进程正在停止。</span>\
            <span>3：RUNNING：该进程正在运行。 4：STARTING：该进程由于启动请求而开始。</span>\
            <span>5：FATAL：该进程无法成功启动。</span>\
            <span>6：BACKOFF：该进程进入“ 启动”状态，但随后退出的速度太快而无法移至“ 运行”状态。</span>\
        </div>'

        $(".soft-man-con").html(con);
        $('#databasePage').html(rdata.page);
    });
}


function startOrStop(name,status){
	myPost('start_job',{'name':name,'status':status}, function(data){
		var rdata = $.parseJSON(data.data);
		showMsg(rdata.msg, function(){
			supList(1,10);
		},{icon:rdata.status?1:2}, rdata.status ? 2000 : 10000);
	});
}

function restartJob(name,status){
	myPost('restart_job',{'name':name,'status':status}, function(data){
		var rdata = $.parseJSON(data.data);
		layer.msg(rdata.msg,{icon:rdata.status?1:2});
		setTimeout(function(){
			supList(1,10);
		},2000);
	});
}

function updateJob(name){
	myPost('get_job_info',{'name':name},function(data){
		var rdata = $.parseJSON(data.data);
		// console.log(rdata);
		var defaultPath = $("#defaultPath").html();
		var ulist = "<div class='line'><span class='tname'>启动用户</span><select class='bt-input-text' name='user' id='c_k3' style='width:270px'>";
		for (var i=0;i<rdata['userlist'].length;i++) {
			if (rdata['userlist'][i] == rdata['daemoninfo']['user']){
				ulist += "<option value='"+rdata['userlist'][i]+"' selected>"+rdata['userlist'][i]+"</option>";
			} else {
				ulist += "<option value='"+rdata['userlist'][i]+"'>"+rdata['userlist'][i]+"</option>";
			}
        }

		ulist += "</select><span style='color:red;margin-left: 10px;width:270px;'></span></div>";
		layer.open({
			type: 1,
			area: '500px',
			title: '修改守护进程',
			closeBtn: 2,
			shift: 0,
			shadeClose: false,
			btn: ['确定', '取消'],
			content: "<div class='bt_conter bt-form pd15' style='height:auto;width:100%;'>\
						<div class='line'>\
		                    <span class='tname'>名称</span>\
		                    <div class='info-r c4'>\
		                    	<input id='name' class='bt-input-text' type='text' name='name' value='"+name+"' placeholder='请输入名称' style='width:270px' readonly/>\
		                    </div>\
	                    </div>\
	                    "+ulist+"\
	                    <div class='line'>\
		                    <span class='tname'>进程数量</span>\
		                    <div class='info-r c4'>\
		                    	<input id='numprocs' class='bt-input-text' type='text' name='numprocs' value='"+rdata['daemoninfo']['numprocs']+"' style='width:270px' />\
		                    </div>\
	                    </div>\
	                    <div class='line'>\
		                    <span class='tname'>启动优先级</span>\
		                    <div class='info-r c4'>\
		                    	<input id='priority' class='bt-input-text' type='text' name='priority' value='"+rdata['daemoninfo']['priority']+"' style='width:270px' />\
		                    </div>\
	                    </div>\
	                   </div>",
	        yes: function(index, layero){
	        	// console.log(index,layero);

	        	var options =  ['name','user','numprocs','priority'];
				var opval = {};
				for(var i in options){
		            opval[options[i]] = $('[name="'+ options[i] +'"]').val();
		            if(opval[options[i]] == ''){
		                if(options[i] == 'user'){
		                    layer.msg('启动用户不能为空');
		                    return false;
		                }else if(options[i] == 'priority'){
		                    layer.msg('启动优先级不能为空');
		                    return false;
		                }else if(options[i] == 'numprocs'){
		                    layer.msg('进程数量不能为空！');
		                    return false;
		                }
		            }
		        }

		        var numprocs = $('[name=numprocs]').val();
			    if (!(/(^[1-9]\d*$)/.test(numprocs))) {
		            layer.msg('进程数量请输入正整数')
		            return false;
			　　}

				myPost("update_job", opval, function(data){
					rdata = $.parseJSON(data.data);
					layer.msg(rdata.msg,{icon:rdata.status?1:2});
					rdata.status ? layer.close(index):'';
					supList(1,10);
				})
				return;
	        }
		});
	});
}


//卸载软件
function delJob(name) {
    layer.confirm(msgTpl('是否删除守护进程[{1}]?', [name]), { icon: 3, closeBtn: 2 }, function() {
    	///////////////////////////////////////
        var data = {'name':  name};
        var loadT = layer.msg('正在处理,请稍候...', { icon: 16, time: 0, shade: [0.3, '#000'] });
        myPost('del_job', data, function(rdata){
        	layer.close(loadT)

        	rdata = $.parseJSON(rdata.data);
         	supList(1,10);
         	layer.msg(rdata.msg, { icon: rdata.status ? 1 : 2 });
        });
        ///////////////////////////////////////
    });
}

//添加站点
function supAdd() {
	myPost('get_user_list',{},function(data){
		var rdata = $.parseJSON(data.data);
		// console.log(rdata);

		var defaultPath = $("#defaultPath").html();
		var ulist = "<div class='line'><span class='tname'>启动用户</span><select class='bt-input-text' name='user' id='c_k3' style='width:270px'>";
		for (var i=0;i<rdata.length;i++) {
            ulist += "<option value='"+rdata[i]+"'>"+rdata[i]+"</option>";
        }

        var www = syncPost('/site/get_root_dir');
		ulist += "</select><span id='php_w' style='color:red;margin-left: 10px;width:270px;'></span></div>";
		layer.open({
			type: 1,
			area: '500px',
			title: '添加守护进程',
			closeBtn: 2,
			shift: 0,
			shadeClose: false,
			btn: ['确定', '取消'],
			content: "<div class='bt_conter bt-form pd15' style='height:auto;width:100%;'>\
						<div class='line'>\
		                    <span class='tname'>名称</span>\
		                    <div class='info-r c4'>\
		                    	<input id='name' class='bt-input-text' type='text' name='name' placeholder='请输入名称' style='width:270px' />\
		                    </div>\
	                    </div>\
	                    "+ulist+"\
	                    <div class='line'>\
		                    <span class='tname'>运行目录</span>\
		                    <div class='info-r c4'>\
		                    	<input id='inputPath' class='bt-input-text mr5' type='text' name='path' placeholder='请选择运行目录' value='"+www['dir']+"/' placeholder='"+www['dir']+"' style='width:270px' />\
		                    	<span class='glyphicon glyphicon-folder-open cursor' onclick='changePath(\"inputPath\")'></span>\
		                    </div>\
	                    </div>\
	                    <div class='line'>\
		                    <span class='tname'>启动命令</span>\
		                    <div class='info-r c4'>\
		                    	<input id='command' class='bt-input-text' type='text' name='command' placeholder='请输入启动命令' style='width:270px' />\
		                    </div>\
	                    </div>\
	                    <div class='line'>\
		                    <span class='tname'>进程数量</span>\
		                    <div class='info-r c4'>\
		                    	<input id='numprocs' class='bt-input-text' type='text' name='numprocs' value='1' style='width:270px' />\
		                    </div>\
	                    </div>\
	                    <ul class='help-info-text c7' style='padding-left: 29px;margin-top:5px;'>\
	                    	<li style='color:#F00'>注意：填写进程名称请使用英文，暂不支持中文！</li>\
	                        <li>如果启动命令里面有文件，请填写文件的绝对路径！</li>\
	                        <li>进程数量默认值为1，如果值为大于1的整数，则相当于多进程！</li>\
	                    </ul>\
	                   </div>",
	        yes: function(index, layero){
	        	// console.log(index,layero);

	        	var options =  ['name','user','path','command','numprocs'];
				var opval = {};
				for(var i in options){
		            opval[options[i]] = $('[name="'+ options[i] +'"]').val();
		            if(opval[options[i]] == ''){
		                if(options[i] == 'name'){
		                    layer.msg('进程名称不能为空');
		                    return false;
		                }else if(options[i] == 'user'){
		                    layer.msg('启动用户不能为空');
		                    return false;
		                }else if(options[i] == 'path'){
		                    layer.msg('运行目录不能为空');
		                    return false;
		                }else if(options[i] == 'command'){
		                    layer.msg('启动命令不能为空');
		                    return false;
		                }else if(options[i] == 'numprocs'){
		                    layer.msg('进程数量不能为空！');
		                    return false;
		                }
		            }
		        }

		        var numprocs = $('[name=numprocs]').val();
			    if (!(/(^[1-9]\d*$)/.test(numprocs))) {
		            layer.msg('进程数量请输入正整数')
		            return false;
			　　}

				myPost("add_job", opval, function(data){
					rdata = $.parseJSON(data.data);
					layer.msg(rdata.msg,{icon:rdata.status?1:2});
					rdata.status ? layer.close(index):'';
					supList(1,10);
				})
				return;
	        }
		});
	});

}


//supervisor
function supConfigTpl(_name, version, func, config_tpl_func, read_config_tpl_func){
	if ( typeof(version) == 'undefined' ){
		version = '';
	}

	var func_name = 'conf';
    if ( typeof(func) != 'undefined' ){
        func_name = func;
    }

    var _config_tpl_func = 'config_tpl';
    if ( typeof(config_tpl_func) != 'undefined' ){
        _config_tpl_func = config_tpl_func;
    }

    var _read_config_tpl_func = 'read_config_tpl';
    if ( typeof(read_config_tpl_func) != 'undefined' ){
        _read_config_tpl_func = read_config_tpl_func;
    }


    var con = '<p style="color: #666; margin-bottom: 7px">提示：Ctrl+F 搜索关键字，Ctrl+G 查找下一个，Ctrl+S 保存，Ctrl+Shift+R 查找替换!</p>\
    			<select id="config_tpl" class="bt-input-text mr20" style="width:30%;margin-bottom: 3px;"><option value="0">请选择</option></select>\
    			<textarea class="bt-input-text" style="height: 320px; line-height:18px;" id="textBody"></textarea>\
                <button id="onlineEditFileBtn" class="btn btn-success btn-sm" style="margin-top:10px;">保存</button>\
                <ul class="help-info-text c7 ptb15">\
                    <li>此处为'+ _name + version +'配置文件,若您不了解配置规则,请勿随意修改。</li>\
                </ul>';
    $(".soft-man-con").html(con);

    function getFileName(file){
    	var list = file.split('/');
    	var f = list[list.length-1];
    	return f 
    }

    var fileName = '';
    $.post('/plugins/run',{name:_name, func:_config_tpl_func,version:version}, function(data){
    	var rdata = $.parseJSON(data.data);
    	for (var i = 0; i < rdata.length; i++) {
    		$('#config_tpl').append('<option value="'+rdata[i]+'"">'+getFileName(rdata[i])+'</option>');
    	}


    	$("#textBody").empty().text('');
		$(".CodeMirror").remove();
        var editor = CodeMirror.fromTextArea(document.getElementById("textBody"), {
            extraKeys: {
                "Ctrl-Space": "autocomplete",
                "Ctrl-F": "findPersistent",
                "Ctrl-H": "replaceAll",
                "Ctrl-S": function() {}
            },
            lineNumbers: true,
            matchBrackets:true,
        });
        editor.focus();

    	$('#config_tpl').change(function(){
    		var selected = $(this).val();
    		if (selected != '0'){
    			fileName = selected;
    			var loadT = layer.msg('配置获取中...',{icon:16,time:0,shade: [0.3, '#000']});

    			var _args = JSON.stringify({file:selected});
    			$.post('/plugins/run', {name:_name, func:_read_config_tpl_func,version:version,args:_args}, function(data){
    				layer.close(loadT);
    				var rdata = $.parseJSON(data.data);
    				if (!rdata.status){
		                layer.msg(rdata.msg,{icon:0,time:2000,shade: [0.3, '#000']});
		                return;
		            }

    				$("#textBody").empty().html(rdata.data);
    				$(".CodeMirror").remove();
		            var editor = CodeMirror.fromTextArea(document.getElementById("textBody"), {
		                extraKeys: {
		                    "Ctrl-Space": "autocomplete",
		                    "Ctrl-F": "findPersistent",
		                    "Ctrl-H": "replaceAll",
		                    "Ctrl-S": function() {
		                    	$("#textBody").text(editor.getValue());
		                        pluginConfigSave(fileName);
		                    }
		                },
		                lineNumbers: true,
		                matchBrackets:true,
		            });
		            editor.focus();
		            $(".CodeMirror-scroll").css({"height":"300px","margin":0,"padding":0});
		            $("#onlineEditFileBtn").unbind('click');
		            $("#onlineEditFileBtn").click(function(){
		                $("#textBody").html(editor.getValue());
		                pluginConfigSave(fileName);
		            });
    			},'json');
    		}
    	});

    },'json');

}


//保存
function supConfigSave(fileName) {
    var data = encodeURIComponent($("#textBody").val());
    var encoding = 'utf-8';
    var loadT = layer.msg('保存中...', {icon: 16,time: 0});
    $.post('/files/save_body', 'data=' + data + '&path=' + fileName + '&encoding=' + encoding, function(rdata) {
        layer.close(loadT);
        layer.msg(rdata.msg, {icon: rdata.status ? 1 : 2});
    },'json');
}



function supLogs(_name, config_tpl_func, read_config_tpl_func,line){

    var file_line = 100;
    if ( typeof(line) != 'undefined' ){
        file_line = line;
    }

    var _config_tpl_func = 'config_tpl';
    if ( typeof(config_tpl_func) != 'undefined' ){
        _config_tpl_func = config_tpl_func;
    }

    var _read_config_tpl_func = 'read_config_tpl';
    if ( typeof(read_config_tpl_func) != 'undefined' ){
        _read_config_tpl_func = read_config_tpl_func;
    }

    function getFileName(file){
    	var list = file.split('/');
    	var f = list[list.length-1];
    	return f 
    }

    var con = '<div><select id="config_tpl" class="bt-input-text mr20" style="width:30%;margin-bottom: 3px;"><option value="0">请选择</option></select>\
    			<button id="sup_clear_log" class="btn btn-success btn-sm clear_logs mr5">清理日志</button>\
    			<button id="sup_error_log" class="btn btn-success btn-sm clear_logs mr5">查看错误日志</button>\
    		</div>';
    con += '<textarea readonly="" style="margin: 0px;width: 100%;height: 520px;background-color: #333;color:#fff; padding:0 5px" id="info_log"></textarea>';
    $(".soft-man-con").html(con);
    var ob = document.getElementById('info_log');
    ob.scrollTop = ob.scrollHeight;

    function clearLog(file){
    	$('#sup_clear_log').click(function(){
    		myPost('sup_clear_log', {'file':file}, function (data) {
    			var rdata = $.parseJSON(data.data);
    			layer.msg(rdata.msg,{icon:rdata.status?1:2,time:2000,shade: [0.3, '#000']});
    		});
    	});
    }

    function errorLog(file,file_line){
    	$('#sup_error_log').click(function(){
    		var _args = JSON.stringify({file:file,line:file_line});
			$.post('/plugins/run', {name:_name, func:'read_config_log_error_tpl',args:_args}, function(data){
				var rdata = $.parseJSON(data.data);
				if (!rdata.status){
	                layer.msg(rdata.msg,{icon:0,time:2000,shade: [0.3, '#000']});
	                return;
	            }

				$("#info_log").empty().html(rdata.data);
			},'json');
    	});
    }

    var loadT = layer.msg('日志路径获取中...',{icon:16,time:0,shade: [0.3, '#000']});
    $.post('/plugins/run', {name:_name, func:_config_tpl_func},function (data) {
        layer.close(loadT);

        var rdata = $.parseJSON(data.data);
    	for (var i = 0; i < rdata.length; i++) {
    		$('#config_tpl').append('<option value="'+rdata[i]+'"">'+getFileName(rdata[i])+'</option>');
    	}

    	$('#config_tpl').change(function(){
    	///
    		var selected = $(this).val();
    		if (selected == '0'){
    			return;
    		}
    	
			fileName = selected;
			var loadT = layer.msg('日志获取中...',{icon:16,time:0,shade: [0.3, '#000']});

			var _args = JSON.stringify({file:selected,line:file_line});
			$.post('/plugins/run', {name:_name, func:_read_config_tpl_func,args:_args}, function(data){
				layer.close(loadT);
				var rdata = $.parseJSON(data.data);
				if (!rdata.status){
	                layer.msg(rdata.msg,{icon:0,time:2000,shade: [0.3, '#000']});
	                return;
	            }

				$("#info_log").empty().html(rdata.data);
			},'json');

			clearLog(selected);
			errorLog(selected,file_line);
    	///
    	});

    },'json');
}


function confdListTraceLog(name){
	var args = {};
    args["name"] = name;
    pluginRollingLogs("supervisor", '', "confd_list_trace_log", JSON.stringify(args), 21);
}

function confdListErrLog(name){
	var args = {};
    args["name"] = name;
    pluginRollingLogs("supervisor", '', "confd_list_error_log", JSON.stringify(args), 21);
}

function confdList(page, search){
    var _data = {};
    if (typeof(page) =='undefined'){
        var page = 1;
    }
    
    _data['page'] = page;
    _data['page_size'] = 10;
    if(typeof(search) != 'undefined'){
        _data['search'] = search;
    }

    myPost('confd_list', _data, function(data){
        var rdata = $.parseJSON(data.data);
        // console.log(rdata.data);
        var list = '';
        for(i in rdata.data){
            list += '<tr>';
            list += '<td>' + rdata.data[i]['name'] +'</td>';

            list += '<td style="text-align:right">\
                        <a class="btlink" onclick="confdListTraceLog(\''+rdata.data[i]['name']+'\')">日志跟踪</a> | ' +
                        '<a class="btlink" onclick="confdListErrLog(\''+rdata.data[i]['name']+'\')">查看错误日志</a>' +
                    '</td>';

            list += '</tr>';
        }

        if( rdata.data.length == 0 ){
        	list = "<tr><td colspan='9'>当前没有数据</td></tr>";
        }

        var con = '<div class="safe bgw">\
            <button onclick="confdList()" title="刷新" class="btn btn-success btn-sm" type="button" style="margin-right: 5px;">刷新</button>\
            <div class="divtable mtb10">\
                <div class="tablescroll">\
                    <table id="DataBody" class="table table-hover" width="100%" cellspacing="0" cellpadding="0" border="0" style="border: 0 none;">\
                    <thead>\
                    <th>名称</th>\
                    <th style="text-align:right;">操作</th></tr></thead>\
                    <tbody>'+ list +'</tbody></table>\
                </div>\
                <div id="databasePage" class="dataTables_paginate paging_bootstrap page"></div>\
            </div>\
        </div>';
        
        con += '<div class="code">\
            <span>方便查看日志</span>\
        </div>'

        $(".soft-man-con").html(con);
        $('#databasePage').html(rdata.page);
    });
}

