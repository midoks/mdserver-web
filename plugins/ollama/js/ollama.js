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

    ai_model_list:function(){
        this.send({
            "tips":"加载中...",
            "method": 'get_ai_model_list',
            "success": function(data){
                var html = '<div class="divtable mtb15">';
                html += '<table class="table table-hover">';
                html += '<thead><tr><th>NAME</th><th>ID</th><th>SIZE</th><th>MODIFIED</th></tr></thead>';
                html += '<tbody>';
                
                if (data && data.length > 0) {
                    for (var i = 0; i < data.length; i++) {
                        var item = data[i];
                        html += '<tr>';
                        html += '<td>' + (item.name || '') + '</td>';
                        html += '<td>' + (item.id || '') + '</td>';
                        html += '<td>' + (item.size || '') + '</td>';
                        html += '<td>' + (item.modified || '') + '</td>';
                        html += '</tr>';
                    }
                } else {
                    html += '<tr><td colspan="4" class="text-center c7">暂无模型</td></tr>';
                }
                
                html += '</tbody></table></div>';
                $('.soft-man-con').html(html);
            },
        })
    },

    readme:function (){
        var readme = '<ul class="help-info-text c7">';
        readme += '<li>常用命令说明：</li>';
        readme += '</ul>';
        readme += '<div class="divtable mtb15">';
        readme += '<table class="table table-hover">';
        readme += '<thead><tr><th>命令</th><th>说明</th><th>示例</th></tr></thead>';
        readme += '<tbody>';
        readme += '<tr><td><code>ollama pull &lt;模型名&gt;</code></td><td>仅下载指定的模型到本地，不立即运行</td><td><code>ollama pull deepseek-r1:7b</code></td></tr>';
        readme += '<tr><td><code>ollama run &lt;模型名&gt;</code></td><td>下载（若本地无）并运行模型，进入交互界面</td><td><code>ollama run llama3.2</code></td></tr>';
        readme += '<tr><td><code>ollama list</code></td><td>列出所有已下载到本地的模型</td><td><code>ollama list</code></td></tr>';
        readme += '<tr><td><code>ollama ps</code></td><td>查看当前正在运行的模型</td><td><code>ollama ps</code></td></tr>';
        readme += '<tr><td><code>ollama stop &lt;模型名&gt;</code></td><td>停止一个正在运行的模型</td><td><code>ollama stop llama3.2</code></td></tr>';
        readme += '<tr><td><code>ollama rm &lt;模型名&gt;</code></td><td>从本地删除指定模型，释放磁盘空间</td><td><code>ollama rm llama3.2</code></td></tr>';
        readme += '<tr><td><code>ollama serve</code></td><td>启动 Ollama 后台服务（首次运行模型时也会自动启动）</td><td><code>ollama serve</code></td></tr>';
        readme += '</tbody></table></div>';
        $('.soft-man-con').html(readme);
    }
}
