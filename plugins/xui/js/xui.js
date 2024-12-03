function mtPost(method, version, args,callback){
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });

    var req_data = {};
    req_data['name'] = 'mtproxy';
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

function mtCommonFunc(){
	var con = '<hr/><p class="conf_p" style="text-align:center;">\
        <button id="mtproxy_url" class="btn btn-default btn-sm">获取连接地址</button>\
    </p>';

    $(".soft-man-con").html(con);

    $('#mtproxy_url').click(function(){
    	mtPost('url', '', {}, function(rdata){
            var data = $.parseJSON(rdata.data);

            layer.open({
                title: "mtproxy代理信息",
                area: ['600px', '180px'],
                type:1,
                closeBtn: 1,
                shadeClose: false,
                btn:["复制","取消"],
                content: '<div class="pd15">\
                            <div class="divtable">\
                                <pre class="layui-code">'+data.data+'</pre>\
                            </div>\
                        </div>',
                success:function(){
                    copyText(data.data);
                },
                yes:function(){
                    copyText(data.data);
                }
            });
    	});
    });
}