var nezha  = {
    plugin_name: 'nezha',
    init: function () {
        var _this = this;
    },

    send:function(info){
        var tips = info['tips'];
        var method = info['method'];
        var args = info['data'];
        var callback = info['success'];

        var loadT = layer.msg(tips, { icon: 16, time: 0, shade: 0.3 });

        var data = {};
        data['name'] = 'nezha';
        data['func'] = method;
        data['version'] = $('.plugin_version').attr('version');
     
        if (typeof(args) == 'string'){
            data['args'] = JSON.stringify(toArrayObject(args));
        } else {
            data['args'] = JSON.stringify(args);
        }

        $.post('/plugins/run', data, function(res) {
            layer.close(loadT);
            if (!res.status){
                layer.msg(res.msg,{icon:2,time:10000});
                return;
            }

            var ret_data = $.parseJSON(res.data);
            if(typeof(callback) == 'function'){
                callback(ret_data);
            }
        },'json'); 
    },

    postCallback:function(info){
        var tips = info['tips'];
        var method = info['method'];
        var args = info['data'];
        var callback = info['success'];
        
        var loadT = layer.msg(tips, { icon: 16, time: 0, shade: 0.3 });

        var data = {};
        data['name'] = 'nezha';
        data['func'] = method;
        data['version'] = $('.plugin_version').attr('version');
     
        if (typeof(args) == 'string'){
            data['args'] = JSON.stringify(toArrayObject(args));
        } else {
            data['args'] = JSON.stringify(args);
        }

        $.post('/plugins/callback', data, function(res) {
            layer.close(loadT);
            if (!res.status){
                layer.msg(res.msg,{icon:2,time:10000});
                return;
            }

            var ret_data = $.parseJSON(res.data);
              if (!ret_data.status){
                layer.msg(ret_data.msg,{icon:2,time:2000});
                return;
            }

            if(typeof(callback) == 'function'){
                callback(res);
            }
        },'json');
    },
    repeatPwd:function (a, id) {
        $("#"+id).val(randomStrPwd(a))
    },

    otherFunc:function(){
        var con = '<p class="conf_p" style="text-align:center;">\
                <button class="btn btn-default btn-sm" onclick="nezha.cronAddCheck()">添加更新任务</button>\
                <button class="btn btn-default btn-sm" onclick="nezha.cronDelCheck()">删除更新任务</button>\
            </p>';
        $(".soft-man-con").html(con);
    },
    cronAddCheck: function(){
        nezha.send({
            tips:"请求中...",
            method: "cron_add_check",
            success:function(rdata){
                layer.msg(rdata.msg, { icon: rdata.status ? 1 : 2 });
            }
        });
    },
    cronDelCheck:function(){
        nezha.send({
            tips:"请求中...",
            method: "cron_del_check",
            success:function(rdata){
                layer.msg(rdata.msg, { icon: rdata.status ? 1 : 2 });
            }
        });
    },
    readme:function (){
        var readme = '<ul class="help-info-text c7">';
        readme += '<li>默认用户和密码(admin:admin),务必在第一时间修改</li>';
        readme += '<li>经测试,修改(admin)密码后,需清空cookie,才能正常登录</li>';
        readme += '</ul>';
        $('.soft-man-con').html(readme);
    }
}
