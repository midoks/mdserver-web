function ldapPost(method, version, args,callback){
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });

    var req_data = {};
    req_data['name'] = 'ldap';
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

function ldapPostCallbak(method, version, args,callback){
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });

    var req_data = {};
    req_data['name'] = 'ldap';
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

//配置修改
function getLadpConfig(version) {
    ladpPost('get_redis_conf', version,'',function(data){
        // console.log(data);
        var rdata = $.parseJSON(data.data);
        // console.log(rdata);
        var mlist = '';
        for (var i = 0; i < rdata.length; i++) {
            var w = '70'
            if (rdata[i].name == 'error_reporting') w = '250';
            var ibody = '<input style="width: ' + w + 'px;" class="bt-input-text mr5" name="' + rdata[i].name + '" value="' + rdata[i].value + '" type="text" >';
            switch (rdata[i].type) {
                case 0:
                    var selected_1 = (rdata[i].value == 1) ? 'selected' : '';
                    var selected_0 = (rdata[i].value == 0) ? 'selected' : '';
                    ibody = '<select class="bt-input-text mr5" name="' + rdata[i].name + '" style="width: ' + w + 'px;"><option value="1" ' + selected_1 + '>开启</option><option value="0" ' + selected_0 + '>关闭</option></select>'
                    break;
                case 1:
                    var selected_1 = (rdata[i].value == 'On') ? 'selected' : '';
                    var selected_0 = (rdata[i].value == 'Off') ? 'selected' : '';
                    ibody = '<select class="bt-input-text mr5" name="' + rdata[i].name + '" style="width: ' + w + 'px;"><option value="On" ' + selected_1 + '>开启</option><option value="Off" ' + selected_0 + '>关闭</option></select>'
                    break;
            }
            mlist += '<p><span>' + rdata[i].name + '</span>' + ibody + ', <font>' + rdata[i].ps + '</font></p>'
        }
        var con = '<style>.conf_p p{margin-bottom: 2px}</style><div class="conf_p" style="margin-bottom:0">' + mlist + '\
                        <div style="margin-top:10px; padding-right:15px" class="text-right"><button class="btn btn-success btn-sm mr5" onclick="getRedisConfig(\'' + version + '\')">刷新</button>\
                        <button class="btn btn-success btn-sm" onclick="submitConf(\'' + version + '\')">保存</button></div>\
                    </div>'
        $(".soft-man-con").html(con);
    });
}

//提交配置
function submitConf(version) {
    var data = {
        version: version,
        bind: $("input[name='bind']").val(),
        'port': $("input[name='port']").val(),
        'timeout': $("input[name='timeout']").val(),
        maxclients: $("input[name='maxclients']").val(),
        databases: $("input[name='databases']").val(),
        requirepass: $("input[name='requirepass']").val(),
        maxmemory: $("input[name='maxmemory']").val(),
    };

    redisPost('submit_ladp_conf', version, data, function(ret_data){
        var rdata = $.parseJSON(ret_data.data);
        layer.msg(rdata.msg, { icon: rdata.status ? 1 : 2 });
    });
}


function ladpReadme(){
    var readme = '<ul class="help-info-text c7">';
    readme += '<li>集群创建1</li>';
    readme += '</ul>';

    $('.soft-man-con').html(readme);   
}

