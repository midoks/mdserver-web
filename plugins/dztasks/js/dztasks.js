function zdPost(method, version, args,callback){
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });

    var req_data = {};
    req_data['name'] = 'dztasks';
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

function zdPostCallbak(method, version, args,callback){
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });

    var req_data = {};
    req_data['name'] = 'dztasks';
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

function commonHomePage(){
    zdPost('home_page', '', {}, function(data){
        var rdata = $.parseJSON(data.data);
        window.open(rdata.data);
    });
}

function postCrossPort(data, url) {
    var xhr = new XMLHttpRequest();
    xhr.open('POST', url, true);
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhr.onreadystatechange = function() {
        if(xhr.readyState == 4 && xhr.status == 200) {
            console.log(xhr.responseText);
        }
    };
    xhr.send(data);
}

function dzLogin(){

    zdPost('run_info', '', {}, function(data){
        var rdata = $.parseJSON(data.data);
        var info = rdata.data;
        var post_url = info['url']+'/do_login';

        $("#toSite").attr('action',post_url);
        $("#username").val(info['user']);
        $("#password").val(info['pass']);
        layer.msg('正在打开dztasks',{icon:16,shade: [0.3, '#000'],time:2000});

        setTimeout(function(){
            $("#toSite").submit();
        },2000);
    });
}

function dzCommonFunc(){
    var con = '';
    con += '<hr/><p class="conf_p" style="text-align:center;">\
        <button class="btn btn-default btn-sm" onclick="commonHomePage()">主页</button> \
        <button class="btn btn-default btn-sm" onclick="dzLogin()">直接登陆</button>\
    </p>';

    con += '<form id="toSite" action="" method="post" style="display: none;" target="_blank">\
            <input type="text" name="username" id="username" value="">\
            <input type="password" name="password" id="password" value="">\
        </form>';
    $(".soft-man-con").html(con);
}

function zdReadme(){
    var readme = '<ul class="help-info-text c7">';
    readme += '<li>自己修改配置</li>';
    readme += '</ul>';

    $('.soft-man-con').html(readme);   
}

