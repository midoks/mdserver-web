function pgPost(method,args,callback){

    var _args = null; 
    if (typeof(args) == 'string'){
        _args = JSON.stringify(toArrayObject(args));
    } else {
        _args = JSON.stringify(args);
    }

    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });
    $.post('/plugins/run', {name:'pgadmin', func:method, args:_args}, function(data) {
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


function pgAsyncPost(method,args){

    var _args = null; 
    if (typeof(args) == 'string'){
        _args = JSON.stringify(toArrayObject(args));
    } else {
        _args = JSON.stringify(args);
    }
    return syncPost('/plugins/run', {name:'pgadmin', func:method, args:_args}); 
}

function homePage(){
    pgPost('get_home_page', '', function(data){
        var rdata = $.parseJSON(data.data);
        if (!rdata.status){
            layer.msg(rdata.msg,{icon:0,time:2000,shade: [0.3, '#000']});
            return;
        }
        var con = '<button class="btn btn-default btn-sm" onclick="window.open(\'' + rdata.data + '\')">主页</button>';
        $(".soft-man-con").html(con);
    });
}


//phpmyadmin安全设置
function safeConf() {
    pgPost('get_pg_option', {}, function(rdata){
        var rdata = $.parseJSON(rdata.data);
        if (!rdata.status){
            layer.msg(rdata.msg,{icon:2,time:2000,shade: [0.3, '#000']});
            return;
        }

        var cfg = rdata.data;
        var con = '<div class="ver line">\
                    <span class="tname">访问端口</span>\
                    <input style="width:110px" class="bt-input-text phpmyadmindk mr20" name="Name" id="pmport" value="' + cfg['port'] + '" placeholder="pgadmin访问端口" maxlength="5" type="number">\
                    <button class="btn btn-success btn-sm" onclick="setPgPort()">保存</button>\
                </div>\
                <div class="ver line">\
                    <span class="tname">用户名</span>\
                    <input style="width:110px" class="bt-input-text mr20" name="username" id="pmport" value="' + cfg['username'] + '" placeholder="认证用户名" type="text">\
                    <button class="btn btn-success btn-sm" onclick="setPgUsername()">保存</button>\
                </div>\
                <div class="ver line">\
                    <span class="tname">密码</span>\
                    <input style="width:110px" class="bt-input-text mr20" name="password" id="pmport" value="' + cfg['password'] + '" placeholder="密码" type="text">\
                    <button class="btn btn-success btn-sm" onclick="setPgPassword()">保存</button>\
                </div>\
                <hr/>\
                <div class="ver line">pgadmin登录信息</div>\
                <div class="ver line">\
                    <span class="tname">PG登录用户名</span>\
                    <input style="width:110px" class="bt-input-text mr20" name="username" id="pmport" value="' + cfg['web_pg_username'] + '" placeholder="PG登录用户名" type="text">\
                    <button class="btn btn-success btn-sm" onclick="setPgUsername()">保存</button>\
                </div>\
                <div class="ver line">\
                    <span class="tname">PG登录密码</span>\
                    <input style="width:110px" class="bt-input-text mr20" name="password" id="pmport" value="' + cfg['web_pg_password'] + '" placeholder="PG登录密码" type="text">\
                    <button class="btn btn-success btn-sm" onclick="setPgPassword()">保存</button>\
                </div>';
        $(".soft-man-con").html(con);
    });
}

function setPgUsername(){
    var username = $("input[name=username]").val();
    pgPost('set_pg_username',{'username':username}, function(data){
        var rdata = $.parseJSON(data.data);
        layer.msg(rdata.msg, { icon: rdata.status ? 1 : 2 });
    });
}

function setPgPassword(){
    var password = $("input[name=password]").val();
    pgPost('set_pg_password',{'password':password}, function(data){
        var rdata = $.parseJSON(data.data);
        layer.msg(rdata.msg, { icon: rdata.status ? 1 : 2 });
    });
}

//修改phpmyadmin端口
function setPgPort() {
    var pmport = $("#pmport").val();
    if (pmport < 80 || pmport > 65535) {
        layer.msg('端口范围不合法!', { icon: 2 });
        return;
    }
    var data = 'port=' + pmport;
    
    pgPost('set_pg_port',data, function(data){
        var rdata = $.parseJSON(data.data);
        layer.msg(rdata.msg, { icon: rdata.status ? 1 : 2 });
    });
}