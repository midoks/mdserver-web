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
    $.post('/plugins/run', {name:'l2tp', func:method, args:_args}, function(data) {
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


function addUser(){
    var loadOpen = layer.open({
        type: 1,
        title: '添加用户',
        area: '240px',
        content:"<div class='bt-form pd20 pb70 c6'>\
            <div class='version line'>\
                <div><input class='bt-input-text mr5 outline_no' type='text' id='username' name='username' style='height: 28px; border-radius: 3px;width: 200px;' placeholder='输入用户名'></div>\
            </div>\
            <div class='bt-form-submit-btn'>\
                <button type='button' id='add_ok' class='btn btn-success btn-sm btn-title bi-btn'>确认</button>\
            </div>\
        </div>"
    });

    $('#add_ok').click(function(){
        _data = {};
        _data['username'] = $('#username').val();
        var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });
        lpPost('add_user', _data, function(data){
            var rdata = $.parseJSON(data.data);
            layer.close(loadOpen);
            layer.msg(rdata.msg,{icon:rdata.status?1:2,time:2000,shade: [0.3, '#000']});
            setTimeout(function(){userList();},2000);
        });
    });
}

function delUser(username){
    lpPost('del_user', {username:username}, function(data){
        var rdata = $.parseJSON(data.data);
        layer.msg(rdata.msg,{icon:rdata.status?1:2,time:2000,shade: [0.3, '#000']});
        setTimeout(function(){userList();},2000);
    });
}

function modUser(username){
    var loadOpen = layer.open({
        type: 1,
        title: '修改密码',
        area: '240px',
        content:"<div class='bt-form pd20 pb70 c6'>\
            <div class='version line'>\
                <div><input class='bt-input-text mr5 outline_no' type='text' id='password' name='password' style='height: 28px; border-radius: 3px;width: 200px;' placeholder='输入密码'></div>\
            </div>\
            <div class='bt-form-submit-btn'>\
                <button type='button' id='mod_ok' class='btn btn-success btn-sm btn-title bi-btn'>确认</button>\
            </div>\
        </div>"
    });

    $('#mod_ok').click(function(){
        _data = {};
        _data['username'] = username;
        _data['password'] = $('#password').val();
        var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });
        lpPost('mod_user', _data, function(data){
            var rdata = $.parseJSON(data.data);
            layer.close(loadOpen);
            layer.msg(rdata.msg,{icon:rdata.status?1:2,time:2000,shade: [0.3, '#000']});
            setTimeout(function(){userList();},2000);
        });
    });
}

