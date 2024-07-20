function zabbixPost(method, version, args,callback){
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });

    var req_data = {};
    req_data['name'] = 'zabbix';
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

function zabbixPostCallbak(method, version, args,callback){
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });

    var req_data = {};
    req_data['name'] = 'zabbix';
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


function zabbixReadme(){
    var readme = '<ul class="help-info-text c7">';
    readme += '<li>需要手动配置【默认配置】</li>';
    readme += '</ul>';

    $('.soft-man-con').html(readme);   
}

//配置修改模版 --- start
function zagentDConfigTpl(_name, version, func, config_tpl_func, read_config_tpl_func, save_callback_func){
    if ( typeof(version) == 'undefined' ){
        version = '';
    }

    var func_name = 'conf';
    if ( typeof(func) != 'undefined' ){
        func_name = func;
    }

    var _config_tpl_func = 'config_tpl';
    if ( typeof(config_tpl_func) != 'undefined' ){
        _config_tpl_func = config_tpl_func;
    }

    var _read_config_tpl_func = 'read_config_tpl';
    if ( typeof(read_config_tpl_func) != 'undefined' ){
        _read_config_tpl_func = read_config_tpl_func;
    }


    var con = '<p style="color: #666; margin-bottom: 7px">提示：Ctrl+F 搜索关键字，Ctrl+G 查找下一个，Ctrl+S 保存，Ctrl+Shift+R 查找替换!</p>\
                <select id="config_tpl" class="bt-input-text mr20" style="width:30%;margin-bottom: 3px;"><option value="0">请选择</option></select>\
                <textarea class="bt-input-text" style="height: 320px; line-height:18px;" id="textBody"></textarea>\
                <button id="onlineEditFileBtn" class="btn btn-success btn-sm" style="margin-top:10px;">保存</button>\
                <ul class="help-info-text c7 ptb15">\
                    <li>此处为【'+ _name + version +'】主配置文件,若您不了解配置规则,请勿随意修改。</li>\
                </ul>';
    $(".soft-man-con").html(con);

    function getFileName(file){
        var list = file.split('/');
        var f = list[list.length-1];
        return f 
    }

    var fileName = '';
    $.post('/plugins/run',{name:_name, func:_config_tpl_func,version:version}, function(data){
        var rdata = $.parseJSON(data.data);
        for (var i = 0; i < rdata.length; i++) {
            $('#config_tpl').append('<option value="'+rdata[i]+'"">'+getFileName(rdata[i])+'</option>');
        }

        $('#config_tpl').change(function(){
            var selected = $(this).val();
            if (selected != '0'){
                var loadT = layer.msg('配置模版获取中...',{icon:16,time:0,shade: [0.3, '#000']});
                fileName = selected;
                var _args = JSON.stringify({file:selected});
                $.post('/plugins/run', {name:_name, func:_read_config_tpl_func,version:version,args:_args}, function(data){
                    layer.close(loadT);
                    var rdata = $.parseJSON(data.data);
                    if (!rdata.status){
                        layer.msg(rdata.msg,{icon:0,time:2000,shade: [0.3, '#000']});
                        return;
                    }

                    $("#textBody").empty().text(rdata.data);
                    $(".CodeMirror").remove();
                    var editor = CodeMirror.fromTextArea(document.getElementById("textBody"), {
                        extraKeys: {
                            "Ctrl-Space": "autocomplete",
                            "Ctrl-F": "findPersistent",
                            "Ctrl-H": "replaceAll",
                            "Ctrl-S": function() {
                                $("#textBody").text(editor.getValue());
                                pluginConfigSave(fileName,save_callback_func);
                            }
                        },
                        lineNumbers: true,
                        matchBrackets:true,
                    });
                    editor.focus();
                    $(".CodeMirror-scroll").css({"height":"300px","margin":0,"padding":0});
                    $("#onlineEditFileBtn").unbind('click');
                    $("#onlineEditFileBtn").click(function(){
                        $("#textBody").text(editor.getValue());
                        pluginConfigSave(fileName, save_callback_func);
                    });
                },'json');
            }
        });

    },'json');

    var loadT = layer.msg('配置文件路径获取中...',{icon:16,time:0,shade: [0.3, '#000']});
    $.post('/plugins/run', {name:_name, func:func_name,version:version}, function (data) {
        layer.close(loadT);

        var loadT2 = layer.msg('文件内容获取中...',{icon:16,time:0,shade: [0.3, '#000']});
        fileName = data.data;
        $.post('/files/get_body', 'path=' + fileName, function(rdata) {
            layer.close(loadT2);
            if (!rdata.status){
                layer.msg(rdata.msg,{icon:0,time:2000,shade: [0.3, '#000']});
                return;
            }
            $("#textBody").empty().text(rdata.data.data);
            $(".CodeMirror").remove();
            var editor = CodeMirror.fromTextArea(document.getElementById("textBody"), {
                extraKeys: {
                    "Ctrl-Space": "autocomplete",
                    "Ctrl-F": "findPersistent",
                    "Ctrl-H": "replaceAll",
                    "Ctrl-S": function() {
                        $("#textBody").text(editor.getValue());
                        pluginConfigSave(fileName,save_callback_func);
                    }
                },
                lineNumbers: true,
                matchBrackets:true,
            });
            editor.focus();
            $(".CodeMirror-scroll").css({"height":"300px","margin":0,"padding":0});
            $("#onlineEditFileBtn").click(function(){
                $("#textBody").text(editor.getValue());
                pluginConfigSave(fileName,save_callback_func);
            });
        },'json');
    },'json');
}

