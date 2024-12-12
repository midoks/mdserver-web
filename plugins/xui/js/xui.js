function xuiPost(method, version, args,callback){
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });

    var req_data = {};
    req_data['name'] = 'xui';
    req_data['func'] = method;
    req_data['version'] = version;
 
    if (typeof(args) == 'string'){
        req_data['args'] = JSON.stringify(toArrayObject(args));
    } else {
        req_data['args'] = JSON.stringify(args);
    }

    $.post('/plugins/run', req_data, function(data) {
        layer.close(loadT);
        if (!data.status){
            //错误展示10S
            layer.msg(data.msg,{icon:0,time:2000,shade: [10, '#000']});
            return;
        }

        if(typeof(callback) == 'function'){
            callback(data);
        }
    },'json'); 
}

function xuiCommonFunc(){

    xuiPost('info', '', {}, function(rdata){
        var rdata = $.parseJSON(rdata.data);
        var info = rdata['data'];
        var con = '<p class="conf_p">\
            <span>用户名</span>\
            <input class="bt-input-text mr5" type="text" value="' + info.username + '">\
        </p>';

        con += '<p class="conf_p">\
            <span>密码</span>\
            <input class="bt-input-text mr5" type="text" value="' + info.password  +'">\
        </p>';
        con += '<p class="conf_p">\
            <span>端口</span>\
            <input class="bt-input-text mr5" type="text" value="' + info.port  +'">\
        </p>';

        con += '<p class="conf_p">\
            <span>路径</span>\
            <input class="bt-input-text mr5" type="text" value="' + info.path  +'">\
        </p>';

        con += '<hr/><p class="conf_p" style="text-align:center;">\
            <button id="open_url" class="btn btn-default btn-sm">打开XUI</button>\
        </p>';

        $(".soft-man-con").html(con);
        $('#open_url').click(function(){
            var url = 'http://' + info.ip + ':' + info.port + info.path;
            window.open(url);
            copyText(url);
        });
    });
}