function alistPost(method, version, args,callback){
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });

    var req_data = {};
    req_data['name'] = 'alist';
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

function alistPostCallbak(method, version, args,callback){
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });

    var req_data = {};
    req_data['name'] = 'alist';
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

function clearTaskCopy(){
    layer.confirm('您真的要清空复制任务吗?', { icon: 3, closeBtn: 2 }, function() {
        alistPost('clear_copy_task', '', {}, function(data){
            var rdata = $.parseJSON(data.data);
            showMsg(rdata.msg, function(){},{ icon: rdata.status ? 1 : 2 });
        });
    });
}

function commonHomePage(){
    alistPost('home_page', '', {}, function(data){
        var rdata = $.parseJSON(data.data);
        window.open(rdata.data);
    });
}

function alistCommonFunc(){
    var con = '';
    con += '<hr/><p class="conf_p" style="text-align:center;">\
        <button class="btn btn-default btn-sm" onclick="commonHomePage()">主页</button>\
        <button class="btn btn-default btn-sm" onclick="clearTaskCopy()">清空复制任务</button>\
    </p>';

    $(".soft-man-con").html(con);
}

function alistReadme(){
 

    var readme = '<ul class="help-info-text c7">';
    readme += '<li>手动开启默认端口:5244</li>';
    readme += '<li>默认admin:admin</li>';
    readme += '<li>手动改密码: cd /www/server/alist && ./alist admin set NEW_PASSWORD</li>';
    readme += '</ul>';

    $('.soft-man-con').html(readme);   
}

