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
            console.log("send:",ret_data);
            // if (!ret_data.status){
            //     layer.msg(ret_data.msg,{icon:2,time:2000});
            //     return;
            // }

            // console.log("send2:",ret_data);

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

    save_cfg:function(version){
        var username = $("input[name='username']").val();
        var password = $("input[name='password']").val();

        this.send({
            tips:'正在设置中...',
            data:{'username':username,'password':password},
            method:'nezha_save_cfg',
            success:function(rdata){
                layer.msg(rdata.msg, { icon: rdata.status ? 1 : 2 });
            }
        });
    },

    cfg:function(version){
        this.send({
            tips:'正在获取中...',
            method:'nezha_cfg',
            success:function(data){
                var d = data.data;
                var value = '<p>\
                    <span>用户名</span>\
                    <input id="nz_username" style="width: 160px;" class="bt-input-text mr5" name="username" value="'+d['username']+'" type="text">\
                    ,<span title="随机用户名" class="glyphicon glyphicon-repeat cursor" onclick="nezha.repeatPwd(8,\'nz_username\')"></span>\
                </p>';

                value += '<p>\
                    <span>密码</span>\
                    <input id="nz_password" style="width: 160px;" class="bt-input-text mr5" name="password" value="'+d['password']+'" type="text">\
                    ,<span title="随机密码" class="glyphicon glyphicon-repeat cursor" onclick="nezha.repeatPwd(16,\'nz_password\')"></span>\
                </p>';
                var conf = '<style>.conf_p p{margin-bottom: 2px;} .conf_p span {width: 50px;}</style><div class="conf_p" style="margin-bottom:0">\
                                ' + value + '\
                                <div style="margin-top:10px; padding-right:15px" class="text-right">\
                                    <button class="btn btn-success btn-sm mr5" onclick="nezha.cfg(\'' + version + '\')">刷新</button>\
                                    <button class="btn btn-success btn-sm" onclick="nezha.save_cfg(\'' + version + '\')">保存</button>\
                                </div>\
                            </div>'
                $(".soft-man-con").html(conf);
            }
        });
    },

    agent_save_cfg:function(version){
        var host = $("input[name='host']").val();
        var secret = $("input[name='secret']").val();

        this.send({
            tips:'正在设置中...',
            data:{'host':host,'secret':secret},
            method:'agent_save_cfg',
            success:function(rdata){
                layer.msg(rdata.msg, { icon: rdata.status ? 1 : 2 });
            }
        });
    },

    agent_cfg:function(version){
        this.send({
            tips:'正在获取中...',
            method:'agent_cfg',
            success:function(data){
                var d = data.data;
                var value = '<p>\
                    <span>地址</span>\
                    <input id="nz_username" style="width: 160px;" class="bt-input-text mr5" name="host" value="'+d['host']+'" type="text">\
                    ,<font>如1.1.1.1:5444</font>\
                </p>';

                value += '<p>\
                    <span>密钥</span>\
                    <input id="nz_password" style="width: 160px;" class="bt-input-text mr5" name="secret" value="'+d['secret']+'" type="text">\
                    ,<font>密钥</font>\
                </p>';
                var conf = '<style>.conf_p p{margin-bottom: 2px;} .conf_p span {width: 50px;}</style><div class="conf_p" style="margin-bottom:0">\
                                ' + value + '\
                                <div style="margin-top:10px; padding-right:15px" class="text-right">\
                                    <button class="btn btn-success btn-sm mr5" onclick="nezha.agent_cfg(\'' + version + '\')">刷新</button>\
                                    <button class="btn btn-success btn-sm" onclick="nezha.agent_save_cfg(\'' + version + '\')">保存</button>\
                                </div>\
                            </div>'
                $(".soft-man-con").html(conf);
            }
        });
    },

    readme:function (){
        var readme = '<ul class="help-info-text c7">';
        readme += '<li>安装时不会自动启动。</li>';
        readme += '<li>哪吒面板是改造版，用户名和密码登录【面板配置】，不依赖github/gitee/gitlab。</li>';
        readme += '<li>Agent需要先手动填写正确信息。</li>';
        readme += '</ul>';
        $('.soft-man-con').html(readme);
    }
}
