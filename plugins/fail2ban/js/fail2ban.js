function getVersion(){
    return $('.plugin_version').attr('version');
}

function f2bPost(method, version, args,callback){
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });

    var req_data = {};
    req_data['name'] = 'fail2ban';
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

function f2bPostCallbak(method, version, args, callback){
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });

    var req_data = {};
    req_data['name'] = 'fail2ban';
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

function f2bBanIpSave(black_ip){
    var ver = getVersion();
    f2bPost('set_black_ip', ver, {'black_ip':black_ip}, function(data){
        var rdata = $.parseJSON(data.data);
        layer.msg(rdata.msg, { icon: rdata.status ? 1 : 2 });
    });
}

function f2bBanIp(){
    var con = '<p style="color: #666; margin-bottom: 7px">提示：Ctrl+F 搜索关键字，Ctrl+G 查找下一个，Ctrl+S 保存，Ctrl+Shift+R 查找替换!</p>\
                <textarea class="bt-input-text" style="height: 320px; line-height:18px;" id="textBody"></textarea>\
                <button id="onlineEditFileBtn" class="btn btn-success btn-sm" style="margin-top:10px;">保存</button>\
                <ul class="help-info-text c7 ptb15">\
                    <li>如有多个请以换行隔开例：<br/>\
                    192.168.1.1<br/>\
                    192.168.1.0/24\
                    </li>\
                </ul>';

    $(".soft-man-con").html(con);
    $("#textBody").empty();
    var editor = CodeMirror.fromTextArea(document.getElementById("textBody"), {
        extraKeys: {
            "Ctrl-Space": "autocomplete",
            "Ctrl-F": "findPersistent",
            "Ctrl-H": "replaceAll",
            "Ctrl-S": function() {
                $("#textBody").text(editor.getValue());
                f2bPost('set_black_list', '', {'black_ip':editor.getValue()}, function(data){
                    var rdata = $.parseJSON(data.data);
                    layer.msg(rdata.msg, { icon: rdata.status ? 1 : 2 });
                });

                f2bBanIpSave(editor.getValue());
            }
        },
        lineNumbers: true,
        matchBrackets:true,
    });
    editor.focus();

    f2bPost('get_black_list', '', {}, function(data){
        var rdata = $.parseJSON(data.data);
        $("#textBody").text(rdata.data);
    });

    $("#onlineEditFileBtn").click(function(){
        f2bBanIpSave(editor.getValue());
    });
}

