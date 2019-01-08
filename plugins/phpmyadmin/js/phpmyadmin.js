function str2Obj(str){
    var data = {};
    kv = str.split('&');
    for(i in kv){
        v = kv[i].split('=');
        data[v[0]] = v[1];
    }
    return data;
}

function pmaPost(method,args,callback){

    var _args = null; 
    if (typeof(args) == 'string'){
        _args = JSON.stringify(str2Obj(args));
    } else {
        _args = JSON.stringify(args);
    }

    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });
    $.post('/plugins/run', {name:'phpmyadmin', func:method, args:_args}, function(data) {
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

function homePage(){
    pmaPost('get_home_page', '', function(data){
        console.log(data);
        var rdata = $.parseJSON(data.data);
        console.log(rdata);
        if (!rdata.status){
            layer.msg(rdata.msg,{icon:0,time:2000,shade: [0.3, '#000']});
            return;
        }
        var con = '<button class="btn btn-default btn-sm" onclick="window.open(\'' + rdata.data + '\')">主页</button>';
        $(".soft-man-con").html(con);
    });
}

//phpmyadmin安全设置
function safeConf(name, port, auth) {
    var con = '<div class="ver line">\
                        <span style="margin-right:10px">' + lan.soft.pma_port + '</span>\
                        <input class="bt-input-text phpmyadmindk mr20" name="Name" id="pmport" value="' + port + '" placeholder="' + lan.soft.pma_port_title + '" maxlength="5" type="number">\
                        <button class="btn btn-success btn-sm" onclick="phpmyadminport()">' + lan.public.save + '</button>\
                    </div>\
                    <div class="user_pw_tit">\
                        <span class="tit">' + lan.soft.pma_pass + '</span>\
                        <span class="btswitch-p"><input class="btswitch btswitch-ios" id="phpmyadminsafe" type="checkbox" ' + (auth ? 'checked' : '') + '>\
                        <label class="btswitch-btn phpmyadmin-btn" for="phpmyadminsafe" onclick="phpmyadminSafe()"></label>\
                        </span>\
                    </div>\
                    <div class="user_pw">\
                        <p><span>' + lan.soft.pma_user + '</span><input id="username_get" class="bt-input-text" name="username_get" value="" type="text" placeholder="' + lan.soft.edit_empty + '"></p>\
                        <p><span>' + lan.soft.pma_pass1 + '</span><input id="password_get_1" class="bt-input-text" name="password_get_1" value="" type="password" placeholder="' + lan.soft.edit_empty + '"></p>\
                        <p><span>' + lan.soft.pma_pass2 + '</span><input id="password_get_2" class="bt-input-text" name="password_get_1" value="" type="password" placeholder="' + lan.soft.edit_empty + '"></p>\
                        <p><button class="btn btn-success btn-sm" onclick="phpmyadmin(\'get\')">' + lan.public.save + '</button></p>\
                    </div>\
                    <ul class="help-info-text c7"><li>' + lan.soft.pma_ps + '</li></ul>';
    $(".soft-man-con").html(con);
    if (auth) {
        $(".user_pw").show();
    }
}


function phpVerChange(type, msg) {
    var data = type + '=' + $("#" + msg).val();
    var loadT = layer.msg(lan.public.the, { icon: 16, time: 0, shade: [0.3, '#000'] });
    $.post('/ajax?action=setPHPMyAdmin', data, function(rdata) {
        layer.closeAll();
        layer.msg(rdata.msg, { icon: rdata.status ? 1 : 2 });
        if (rdata.status) {
            setTimeout(function() {
                window.location.reload();
            }, 3000);
        }
    })
}


//phpmyadmin切换php版本
function phpVer(name, version) {
    $.post('/site?action=GetPHPVersion', function(rdata) {
        var body = "<div class='ver line'><span class='tname'>" + lan.soft.php_version + "</span><select id='get' class='bt-input-text mr20' name='phpVersion' style='width:110px'>";
        var optionSelect = '';
        for (var i = 0; i < rdata.length; i++) {
            optionSelect = rdata[i].version == version ? 'selected' : '';
            body += "<option value='" + rdata[i].version + "' " + optionSelect + ">" + rdata[i].name + "</option>"
        }
        body += '</select><button class="btn btn-success btn-sm" onclick="phpVerChange(\'phpversion\',\'get\')">' + lan.public.save + '</button></div>';
        $(".soft-man-con").html(body);
    })
}
//修改phpmyadmin端口
function phpmyadminport() {
    var pmport = $("#pmport").val();
    if (pmport < 80 || pmport > 65535) {
        layer.msg(lan.firewall.port_err, { icon: 2 });
        return;
    }
    var data = 'port=' + pmport;
    var loadT = layer.msg(lan.public.the, { icon: 16, time: 0, shade: [0.3, '#000'] });
    $.post('/ajax?action=setPHPMyAdmin', data, function(rdata) {
        layer.close(loadT);
        layer.msg(rdata.msg, { icon: rdata.status ? 1 : 2 });
    });
}

//phpmyadmin二级密码
function phpmyadminSafe() {
    var stat = $("#phpmyadminsafe").prop("checked");
    if (stat) {
        $(".user_pw").hide();
        phpmyadmin('close');
    } else {
        $(".user_pw").show();
    }

}

//设置phpmyadmin二级密码
function phpmyadmin(msg) {
    type = 'password';
    if (msg == 'close') {
        password_1 = msg;
        username = msg;
        layer.confirm(lan.soft.pma_pass_close, { closeBtn: 2, icon: 3 }, function() {
            var data = type + '=' + msg + '&siteName=phpmyadmin';
            var loadT = layer.msg(lan.public.the, { icon: 16, time: 0, shade: [0.3, '#000'] });
            $.post('/ajax?action=setPHPMyAdmin', data, function(rdata) {
                layer.close(loadT);
                layer.msg(rdata.msg, { icon: rdata.status ? 1 : 2 });
            });
        });
        return;
    } else {
        username = $("#username_get").val()
        password_1 = $("#password_get_1").val()
        password_2 = $("#password_get_2").val()
        if (username.length < 1 || password_1.length < 1) {
            layer.msg(lan.soft.pma_pass_empty, { icon: 2 });
            return;
        }
        if (password_1 != password_2) {
            layer.msg(lan.bt.pass_err_re, { icon: 2 });
            return;
        }
    }
    msg = password_1 + '&username=' + username + '&siteName=phpmyadmin';
    var data = type + '=' + msg;
    var loadT = layer.msg(lan.public.the, { icon: 16, time: 0, shade: [0.3, '#000'] });
    $.post('/ajax?action=setPHPMyAdmin', data, function(rdata) {
        layer.close(loadT);
        layer.msg(rdata.msg, { icon: rdata.status ? 1 : 2 });
    });
}