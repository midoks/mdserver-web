function gorsePost(method, version, args,callback){
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });

    var req_data = {};
    req_data['name'] = 'gorse';
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

function gorsePostCallbak(method, version, args,callback){
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });

    var req_data = {};
    req_data['name'] = 'gorse';
    req_data['func'] = method;
    args['version'] = version;
 
    if (typeof(args) == 'string'){
        req_data['args'] = JSON.stringify(toArrayObject(args));
    } else {
        req_data['args'] = JSON.stringify(args);
    }

    $.post('/plugins/callback', req_data, function(data) {
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


function gorseCommonFunc(){
    gorsePost('info', '', {}, function(rdata){
        var rdata = $.parseJSON(rdata.data);
        var info = rdata['data'];
        var con = '<p class="conf_p">\
            <span>用户名</span>\
            <input class="bt-input-text mr5" type="text" value="' + info.dashboard_user_name + '">\
        </p>';

        con += '<p class="conf_p">\
            <span>密码</span>\
            <input class="bt-input-text mr5" type="text" value="' + info.dashboard_password  +'">\
        </p>';
        con += '<p class="conf_p">\
            <span>端口</span>\
            <input class="bt-input-text mr5" type="text" value="' + info.http_port  +'">\
        </p>';

        con += '<hr/><p class="conf_p" style="text-align:center;">\
            <button id="open_url" class="btn btn-default btn-sm">打开Gorse</button>\
        </p>';

        $(".soft-man-con").html(con);
        $('#open_url').click(function(){
            var url = 'http://' + info.ip + ':' + info.http_port;
            window.open(url);
            copyText(url);
        });
    });
}

function gorseReadme(){

    var readme = '<ul class="help-info-text c7">';
    readme += '<li>参考官方</li>';
    readme += '<li><a target="_blank" href="https://gorse.io">https://gorse.io</a></li>';
    readme += '<li>mongodb初始化,是无认证的</li>';
    readme += '</ul>';

    $('.soft-man-con').html(readme);   
}

