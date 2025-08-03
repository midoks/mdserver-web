function gPost(method, version, args,callback){
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });

    var req_data = {};
    req_data['name'] = 'prometheus';
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

function gPostCallbak(method, version, args,callback){
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });

    var req_data = {};
    req_data['name'] = 'prometheus';
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

function gCommonFunc(){
    var con = '<hr/><p class="conf_p" style="text-align:center;">\
        <button id="prometheus_url" class="btn btn-default btn-sm">获取连接地址</button>\
    </p>';

    $(".soft-man-con").html(con);

    $('#prometheus_url').click(function(){
        gPost('prometheus_url', '', {}, function(rdata){
            layer.open({
                title: "prometheus连接",
                area: ['600px', '180px'],
                type:1,
                closeBtn: 1,
                shadeClose: false,
                btn:["复制","取消"],
                content: '<div class="pd15">\
                            <div class="divtable">\
                                <pre class="layui-code">'+rdata.data+'</pre>\
                            </div>\
                        </div>',
                success:function(){
                    copyText(rdata.data);
                },
                yes:function(){
                    copyText(rdata.data);
                }
            });
        });
    });
}


function gReadme(){
    var readme = '<ul class="help-info-text c7">';
    readme += '<li>https://prometheus.io/download</li>';
    readme += '</ul>';

    $('.soft-man-con').html(readme);   
}

