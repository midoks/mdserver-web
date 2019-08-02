function str2Obj(str){
    var data = {};
    kv = str.split('&');
    for(i in kv){
        v = kv[i].split('=');
        data[v[0]] = v[1];
    }
    return data;
}

function pPost(method,args,callback, title){

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
    $.post('/plugins/run', {name:'solr', func:method, args:_args}, function(data) {
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


function collectionManagement(){
	pPost('collection_list', '', function(data){
		var rdata = $.parseJSON(data.data);
		if (!rdata.status){
			layer.msg(rdata.msg,{icon:rdata.status?1:2,time:2000,shade: [0.3, '#000']});
			return;
		}

		var list = rdata.data.list;
		var con = '';
        con += '<div class="divtable" style="margin-top:5px;"><table class="table table-hover" width="100%" cellspacing="0" cellpadding="0" border="0">';
        con += '<thead><tr>';
        con += '<th>collection</th>';
        con += '<th>操作(<a class="btlink" onclick="addCollection()">添加</a>)'+ '|'+ '<a class="btlink" target="_blank" href="http://'+rdata.data.ip+':'+rdata.data.port+'">WEB管理</a></th>';
        con += '</tr></thead>';

        con += '<tbody>';

        for (var i = 0; i < list.length; i++) {
            con += '<tr>'+
                '<td>' + list[i]['name']+'</td>' +
                '<td>\
                    <a class="btlink" onclick="cmdCollection(\''+list[i]['name']+'\')">命令</a> \
                	| <a class="btlink" onclick="confCollection(\''+list[i]['name']+'\')">配置</a> \
                	| <a class="btlink" onclick="removeCollection(\''+list[i]['name']+'\')">删除</a></td> \
                </tr>';
        }

        con += '</tbody>';
        con += '</table></div>';

        $(".soft-man-con").html(con);
	});
}


function addCollection(){
    var loadOpen = layer.open({
        type: 1,
        title: '添加Collection',
        area: '400px',
        content:"<div class='bt-form pd20 pb70 c6'>\
            <div class='line'>\
                <span class='tname'>Collection</span>\
                <div class='info-r c4'>\
                    <input id='name' class='bt-input-text' type='text' name='name' placeholder='Collection' style='width:200px' />\
                </div>\
            </div>\
            <div class='bt-form-submit-btn'>\
                <button type='button' id='add_ok' class='btn btn-success btn-sm btn-title bi-btn'>确认</button>\
            </div>\
        </div>",
    });

    $('#add_ok').click(function(){
        _data = {};
        _data['name'] = $('#name').val();
        var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });
        pPost('add_collection', _data, function(data){
            var rdata = $.parseJSON(data.data);
            layer.close(loadOpen);
            layer.msg(rdata.msg,{icon:rdata.status?1:2,time:2000,shade: [0.3, '#000']});
            setTimeout(function(){collectionManagement();},2000);
        });
    });
}

function removeCollection(name){
    var loadOpen = layer.open({
        type: 1,
        title: '删除用户',
        area: '350px',
        content:"<div class='bt-form pd20 pb70 c6'>\
            <div class='version line'>你要确认要删除collection["+ name + "]</div>\
            <div class='bt-form-submit-btn'>\
                <button type='button' id='solr_del_close' class='btn btn-danger btn-sm btn-title'>关闭</button>\
                <button type='button' id='solr_del_ok' class='btn btn-success btn-sm btn-title bi-btn'>确认</button>\
            </div>\
        </div>"
    });

    $('#solr_del_close').click(function(){
        layer.close(loadOpen);
    });

    $('#solr_del_ok').click(function(){
        var _data = {};
        _data['name'] = name;
        var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });
        
        _data = {};
        _data['name'] = name;
        var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });
        pPost('remove_collection', _data, function(data){
            var rdata = $.parseJSON(data.data);
            layer.close(loadOpen);
            layer.msg(rdata.msg,{icon:rdata.status?1:2,time:2000,shade: [0.3, '#000']});
            setTimeout(function(){collectionManagement();},2000);
        });
    });
}


function confCollection(name){
    var html = '';
    html += '<button onclick="confFileCollection(\''+name+'\',\'solrconfig.xml\')" class="btn btn-default btn-sm">solrconfig.xml</button>';
    html += '<button onclick="confFileCollection(\''+name+'\',\'managed-schema\')" class="btn btn-default btn-sm">managed-schema</button>';

    var loadOpen = layer.open({
        type: 1,
        title: '['+name+']配置设置',
        area: '240px',
        content:'<div class="change-default pd20">'+html+'</div>'
    });
}

function confFileCollection(name, conf_file){
    pPost('conf_file_collection', {'name':name, 'conf_file':conf_file}, function(data){
        var rdata = $.parseJSON(data.data);
        if (rdata['status']){
            onlineEditFile(0, rdata['data']['path']);
        } else {
            layer.msg(rdata.msg,{icon:1,time:2000,shade: [0.3, '#000']});
        }        
    });
}


function cmdCollection(name){
    var cmd = '<div class="change-default pd20"><table class="table table-hover">';
    cmd += '<thead><tr><td>增量更新</td><td>curl "http://127.0.0.1:8983/solr/'+name+'/dataimport?command=delta-import&wt=json&clean=false&commit=true"</td></tr>';
    cmd += '<tr><td>权限更新</td><td>curl "http://127.0.0.1:8983/solr/'+name+'/dataimport?command=full-import&wt=json&clean=false&commit=true"<td></tr>';
    cmd += '<tr><td colspan="2">默认端口:8983(可修改),默认IP为本地,可修改。</td></tr></thead>';
    cmd += '</table></div>';

    layer.open({
        type: 1,
        title: '命令',
        area: '750px',
        content:cmd,
    });
}

function pRead(){
	var readme = '<ul class="help-info-text c7">';
    readme += '<li>使用默认solr端口,如有需要自行修改</li>';
    readme += '<li>如果开启防火墙,需要放行solr设置的端口,例如(8983)</li>';
    readme += '<li>数据源设置好后,需要在managed-schema中同时设置</li>';
    readme += '<li><a target="_blank" href="https://github.com/midoks/mdserver-web/wiki/插件管理%5Bsolr使用说明%5D">wiki说明</a></li>';
    readme += '</ul>';

    $('.soft-man-con').html(readme);   
}