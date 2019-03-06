function str2Obj(str){
    var data = {};
    kv = str.split('&');
    for(i in kv){
        v = kv[i].split('=');
        data[v[0]] = v[1];
    }
    return data;
}

function rsPost(method,args,callback, title){

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
    $.post('/plugins/run', {name:'rsyncd', func:method, args:_args}, function(data) {
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


function rsyncdReceive(){
	rsPost('rec_list', '', function(data){
		var rdata = $.parseJSON(data.data);
		if (!rdata.status){
			layer.msg(rdata.msg,{icon:rdata.status?1:2,time:2000,shade: [0.3, '#000']});
			return;
		}
		console.log(rdata);
		var list = rdata.data;
		var con = '';
        con += '<div class="divtable" style="margin-top:5px;"><table class="table table-hover" width="100%" cellspacing="0" cellpadding="0" border="0">';
        con += '<thead><tr>';
        con += '<th>服务名</th>';
        con += '<th>路径</th>';
        con += '<th>备注</th>';
        con += '<th>操作(<a class="btlink" onclick="addReceive()">添加</a>)</th>';
        con += '</tr></thead>';

        con += '<tbody>';

        for (var i = 0; i < list.length; i++) {
            con += '<tr>'+
                '<td>' + list[i]['name']+'</td>' +
                '<td>' + list[i]['path']+'</td>' +
                '<td>' + list[i]['comment']+'</td>' +
                '<td><a class="btlink" onclick="modUser(\''+list[i]['name']+'\')">改密</a>|<a class="btlink" onclick="delReceive(\''+list[i]['name']+'\')">删除</a></td></tr>';
        }

        con += '</tbody>';
        con += '</table></div>';

        $(".soft-man-con").html(con);
	});
}

function addReceive(){
    var loadOpen = layer.open({
        type: 1,
        title: '创建接收',
        area: '400px',
        content:"<div class='bt-form pd20 pb70 c6'>\
            <div class='line'>\
                <span class='tname'>项目名</span>\
                <div class='info-r c4'>\
                	<input id='name' class='bt-input-text' type='text' name='name' placeholder='项目名' style='width:200px' />\
                </div>\
            </div>\
            <div class='line'>\
                <span class='tname'>同步到</span>\
                <div class='info-r c4'>\
                	<input id='inputPath' class='bt-input-text' type='text' name='path' placeholder='/' style='width:200px' />\
                	<span class='glyphicon glyphicon-folder-open cursor' onclick=\"changePath('inputPath')\"></span>\
                </div>\
            </div>\
            <div class='line'>\
                <span class='tname'>备注</span>\
                <div class='info-r c4'>\
                	<input id='ps' class='bt-input-text' type='text' name='ps' placeholder='备注' style='width:200px' />\
                </div>\
            </div>\
            <div class='bt-form-submit-btn'>\
                <button type='button' id='add_ok' class='btn btn-success btn-sm btn-title bi-btn'>确认</button>\
            </div>\
        </div>"
    });

    $('#add_ok').click(function(){
        _data = {};
        _data['name'] = $('#name').val();
        _data['path'] = $('#inputPath').val();
        _data['ps'] = $('#ps').val();
        var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });
        rsPost('add_rec', _data, function(data){
            var rdata = $.parseJSON(data.data);
            layer.close(loadOpen);
            layer.msg(rdata.msg,{icon:rdata.status?1:2,time:2000,shade: [0.3, '#000']});
            setTimeout(function(){rsyncdReceive();},2000);
        });
    });
}


function delReceive(name){
	safeMessage('删除['+name+']', '您真的要删除['+name+']吗？', function(){
		var _data = {};
		_data['name'] = name;
		rsPost('del_rec', _data, function(data){
            var rdata = $.parseJSON(data.data);
            layer.msg(rdata.msg,{icon:rdata.status?1:2,time:2000,shade: [0.3, '#000']});
            setTimeout(function(){rsyncdReceive();},2000);
        });
	});
}


function rsRead(){
	var readme = '<ul class="help-info-text c7">';
    readme += '<li>如需将其他服务器数据同步到本地服务器，请在接受配置中 "创建接受任务" </li>';
    readme += '</ul>';

    $('.soft-man-con').html(readme);   
}