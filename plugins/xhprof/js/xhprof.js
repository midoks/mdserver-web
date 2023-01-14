function xhPost(method,args,callback){

    var _args = null; 
    if (typeof(args) == 'string'){
        _args = JSON.stringify(toArrayObject(args));
    } else {
        _args = JSON.stringify(args);
    }

    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });
    $.post('/plugins/run', {name:'xhprof', func:method, args:_args}, function(data) {
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

function xhAsyncPost(method,args){
    var _args = null; 
    if (typeof(args) == 'string'){
        _args = JSON.stringify(toArrayObject(args));
    } else {
        _args = JSON.stringify(args);
    }
    return syncPost('/plugins/run', {name:'xhprof', func:method, args:_args}); 
}

function homePage(){
    xhPost('get_home_page', '', function(data){
        var rdata = $.parseJSON(data.data);
        if (!rdata.status){
            layer.msg(rdata.msg,{icon:0,time:2000,shade: [0.3, '#000']});
            return;
        }
        var con = '<button class="btn btn-default btn-sm" onclick="window.open(\'' + rdata.data + '\')">主页</button>';
        $(".soft-man-con").html(con);
    });
}

//phpmyadmin切换php版本
function phpVer(version) {

    var _version = xhAsyncPost('get_set_php_ver','')
    if (_version['data'] != ''){
        version = _version['data'];
    }

    $.post('/site/get_php_version', function(rdata) {
        // console.log(rdata);
        var body = "<div class='ver line'><span class='tname'>PHP版本</span><select id='phpver' class='bt-input-text mr20' name='phpVersion' style='width:110px'>";
        var optionSelect = '';
        for (var i = 0; i < rdata.length; i++) {
            optionSelect = rdata[i].version == version ? 'selected' : '';
            body += "<option value='" + rdata[i].version + "' " + optionSelect + ">" + rdata[i].name + "</option>"
        }
        body += '</select><button class="btn btn-success btn-sm" onclick="phpVerChange(\'phpversion\',\'get\')">保存</button></div>';
        $(".soft-man-con").html(body);
    },'json');
}

function phpVerChange(type, msg) {
    var phpver = $("#phpver").val();
    xhPost('set_php_ver', 'phpver='+phpver, function(data){
        if ( data.data == 'ok' ){
            layer.msg('设置成功!',{icon:1,time:2000,shade: [0.3, '#000']});
        } else {
            layer.msg('设置失败!',{icon:2,time:2000,shade: [0.3, '#000']});
        }
    });
}


//xhprf 安全设置
function safeConf() {
    var data = xhAsyncPost('get_xhprof_port');
    var rdata = $.parseJSON(data.data);
    if (!rdata.status){
        layer.msg(rdata.msg,{icon:2,time:2000,shade: [0.3, '#000']});
        return;
    }
    var con = '<div class="ver line">\
                    <span style="margin-right:10px">访问端口</span>\
                    <input class="bt-input-text mr20" name="Name" id="pmport" value="' + rdata['data'] + '" placeholder="phpmyadmin访问端口" maxlength="5" type="number">\
                    <button class="btn btn-success btn-sm" onclick="xhprofPort()">保存</button>\
                </div>';
    $(".soft-man-con").html(con);
}

//修改 xhprf 端口
function xhprofPort() {
    var pmport = $("#pmport").val();
    if (pmport < 80 || pmport > 65535) {
        layer.msg('端口范围不合法!', { icon: 2 });
        return;
    }
    var data = 'port=' + pmport;
    
    xhPost('set_xhprof_port',data, function(data){
        var rdata = $.parseJSON(data.data);
        layer.msg(rdata.msg, { icon: rdata.status ? 1 : 2 });
    });
}