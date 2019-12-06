function str2Obj(str){
    var data = {};
    kv = str.split('&');
    for(i in kv){
        v = kv[i].split('=');
        data[v[0]] = v[1];
    }
    return data;
}

function pPost(method,args,callback, title){
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
    $.post('/plugins/run', {name:'walle', func:method, args:_args}, function(data) {
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

function pPostCallbak(method, version, args,callback){
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });

    var req_data = {};
    req_data['name'] = 'walle';
    req_data['func'] = method;
    args['version'] = version;
 
    if (typeof(args) == 'string'){
        req_data['args'] = JSON.stringify(str2Obj(args));
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

function initEnv(){
    pPost('init_env', {}, function(data){
        layer.msg(data.data,{icon:1,time:6000,shade: [0.3, '#000']});
    },'初始化环境');
}

function initData(){
    pPost('init_data', {}, function(data){
        layer.msg(data.data,{icon:1,time:6000,shade: [0.3, '#000']});
    },'初始化数据');
}


function pluginCmd(){
    var serviceCon ='<p class="status">当前可以运行的命令：<span></span><span style="color: #20a53a;margin-left: 3px;" class="glyphicon"></span></p>\
        <div class="sfm-opt">\
            <button class="btn btn-default btn-sm" onclick="initEnv()">初始化环境</button>\
            <button class="btn btn-default btn-sm" onclick="initData()">初始化数据</button>\
        </div>'; 
    $(".soft-man-con").html(serviceCon);
}




function pRead(){
	var readme = '<ul class="help-info-text c7">';
    readme += '<li>使用默认walle端口5000,如有需要自行修改</li>';
    readme += '<li>修改配置正确后:</li>';
    readme += '<li>手动[初始化环境]:sh admin.sh init</li>';
    readme += '<li>手动[初始化数据]:sh admin.sh migration</li>';
    readme += '<li><a target="_blank" href="https://walle-web.io/docs/installation_docker.html">官方文档</a></li>';
    readme += '</ul>';

    $('.soft-man-con').html(readme);   
}