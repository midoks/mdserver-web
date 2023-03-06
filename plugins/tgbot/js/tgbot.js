function appPost(method, args,callback){
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });

    var req_data = {};
    req_data['name'] = 'tgbot';
    req_data['func'] = method;
 
    if (typeof(args) == 'string'){
        req_data['args'] = JSON.stringify(toArrayObject(args));
    } else {
        req_data['args'] = JSON.stringify(args);
    }

    $.post('/plugins/run', req_data, function(data) {
        layer.close(loadT);
        if(typeof(callback) == 'function'){
            callback(data);
        }
    },'json'); 
}

function appPostCallbak(method, args,callback){
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });

    var req_data = {};
    req_data['name'] = 'tgbot';
    req_data['func'] = method;
 
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

function botConf(){
    appPost('get_bot_conf','',function(data){
        var rdata = $.parseJSON(data.data);
        var app_token = 'app_token';
        if(rdata['status']){
            db_data = rdata['data'];
            app_token = db_data['app_token'];

        }

        var mlist = '';
        mlist += '<p><span>app_token</span><input style="width: 250px;" class="bt-input-text mr5" name="app_token" value="'+app_token+'" type="text"><font>必填写</font></p>'
        var option = '<style>.conf_p p{margin-bottom: 2px}</style>\
            <div class="conf_p" style="margin-bottom:0">\
                ' + mlist + '\
                <div style="margin-top:10px; padding-right:15px" class="text-right">\
                    <button class="btn btn-success btn-sm" onclick="submitBotConf()">保存</button>\
                </div>\
            </div>';
        $(".soft-man-con").html(option);
    });
}

function submitBotConf(){
    var pull_data = {};
    pull_data['app_token'] = base64_encode($('input[name="app_token"]').val());
    appPost('set_bot_conf',pull_data,function(data){
        var rdata = $.parseJSON(data.data);
        layer.msg(rdata['msg'],{icon:rdata['status']?1:2,time:2000,shade: [0.3, '#000']});
    });
}
