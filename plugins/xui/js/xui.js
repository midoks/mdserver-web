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
        var con = '<p class="conf_p">\
            <span>用户名</span>\
            <input class="bt-input-text mr5" type="number" value="' + rdata['username'] + '">\
        </p>';

        con += '<p class="conf_p">\
            <span>密码</span>\
            <input class="bt-input-text mr5" type="number" value="' + rdata['password']  +'">\
        </p>';
        con += '<p class="conf_p">\
            <span>端口</span>\
            <input class="bt-input-text mr5" type="number" value="' + rdata['port']  +'">\
        </p>';

        var con += '<hr/><p class="conf_p" style="text-align:center;">\
            <button id="mtproxy_url" class="btn btn-default btn-sm">打开XUI</button>\
        </p>';

        $(".soft-man-con").html(con);
    });
    
    // $('#mtproxy_url').click(function(){
    // 	mtPost('url', '', {}, function(rdata){
    //         var data = $.parseJSON(rdata.data);

    //         layer.open({
    //             title: "mtproxy代理信息",
    //             area: ['600px', '180px'],
    //             type:1,
    //             closeBtn: 1,
    //             shadeClose: false,
    //             btn:["复制","取消"],
    //             content: '<div class="pd15">\
    //                         <div class="divtable">\
    //                             <pre class="layui-code">'+data.data+'</pre>\
    //                         </div>\
    //                     </div>',
    //             success:function(){
    //                 copyText(data.data);
    //             },
    //             yes:function(){
    //                 copyText(data.data);
    //             }
    //         });
    // 	});
    // });
}