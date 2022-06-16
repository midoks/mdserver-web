
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
			list += '<td>' + rdata.data[i]['runStatus'] +'</td>';
			list += '<td>' + rdata.data[i]['runStatus'] +'</td>';

            list += '<td style="text-align:right">\
            			<a href="javascript:;" class="btlink" onclick="startOrStop(\''+rdata.data[i]['name']+'\',\''+rdata.data[i]['username']+'\',\''+rdata.data[i]['password']+'\')" title="启动|停止">启动</a> | ' +
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


function updateJob(name){

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
		for (var i=rdata.length-1;i>=0;i--) {
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
