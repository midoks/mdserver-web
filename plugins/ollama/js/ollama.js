var ollama  = {
    plugin_name: 'ollama',
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
        data['name'] = 'ollama';
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
        data['name'] = 'ollama';
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

    readme:function (){
        var readme = '<ul class="help-info-text c7">';
        readme += '<li>能查看。</li>';
        readme += '</ul>';
        $('.soft-man-con').html(readme);
    }
}
