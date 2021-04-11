function str2Obj(str){
    var data = {};
    kv = str.split('&');
    for(i in kv){
        v = kv[i].split('=');
        data[v[0]] = v[1];
    }
    return data;
}

function lpPost(method,args,callback, title){

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
    $.post('/plugins/run', {name:'aria2', func:method, args:_args}, function(data) {
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

function lpAsyncPost(method,args){
    var _args = null; 
    if (typeof(args) == 'string'){
        _args = JSON.stringify(str2Obj(args));
    } else {
        _args = JSON.stringify(args);
    }

    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });
    return syncPost('/plugins/run', {name:'l2tp', func:method, args:_args});
}

function userList(){
    lpPost('user_list', '' ,function(data){
        var rdata = $.parseJSON(data['data']);
        
        if (!rdata['status']){
            layer.msg(rdata.msg,{icon:0,time:2000,shade: [0.3, '#000']});
            return;
        }
        var list = rdata['data'];

        var con = '';
        con += '<div class="divtable" style="margin-top:5px;"><table class="table table-hover" width="100%" cellspacing="0" cellpadding="0" border="0">';
        con += '<thead><tr>';
        con += '<th>用户</th>';
        con += '<th>密码</th>';
        con += '<th>操作(<a class="btlink" onclick="addUser()">添加</a>)</th>';
        con += '</tr></thead>';

        con += '<tbody>';

        for (var i = 0; i < list.length; i++) {
            con += '<tr>'+
                '<td>' + list[i]['user']+'</td>' +
                '<td>' + list[i]['pwd']+'</td>' +
                '<td><a class="btlink" onclick="modUser(\''+list[i]['user']+'\')">改密</a>|<a class="btlink" onclick="delUser(\''+list[i]['user']+'\')">删除</a></td></tr>';
        }

        con += '</tbody>';
        con += '</table></div>';

        $(".soft-man-con").html(con);
    });
}



function readme(){
    var readme = '<ul class="help-info-text c7">';
    readme += '<li>使用时，查看对应的端口</li>';
    readme += '</ul>';
    $('.soft-man-con').html(readme);
}
