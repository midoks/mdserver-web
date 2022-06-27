

function pRead(){
	var readme = '<ul class="help-info-text c7">';
    readme += '<li>修改后,点击重启按钮</li>';
    readme += '</ul>';

    $('.soft-man-con').html(readme);   
}


//varnish负载状态  start
function varnishStatus() {
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });
    $.post('/plugins/run', {name:'varnish', func:'run_info'}, function(data) {
        layer.close(loadT);
        if (!data.status){
            layer.msg(data.msg,{icon:0,time:2000,shade: [0.3, '#000']});
            return;
        }

        var rdata = $.parseJSON(data.data);
        console.log(rdata);

        var tmp = "";
        for (let i in rdata) {
            // console.log(i,rdata[i]);
            if (i == 'timestamp'){
                tmp += "<tr><th>"+i+"</th><td colspan='2'>"+rdata[i]+"</td></tr>"
            } else{
                tmp += "<tr><th>"+i+"</th><td>"+rdata[i]['value']+"</td><td>"+rdata[i]['description']+"</td></tr>"
            }
        }

        hit = (parseInt(rdata.keyspace_hits) / (parseInt(rdata.keyspace_hits) + parseInt(rdata.keyspace_misses)) * 100).toFixed(2);
        var Con = '<div class="divtable">\
                        <table class="table table-hover table-bordered" style="width: 490px;">\
                        <thead><th>字段</th><th>当前值</th><th>说明</th></thead>\
                        <tbody>'+tmp+'<tbody>\
                </table></div>'
        $(".soft-man-con").html(Con);
    },'json');
}
//varnish负载状态 end


//varnish service --- 
function varnishPluginConfig(_name, version, func){
    if ( typeof(version) == 'undefined' ){
        version = '';
    }

    var func_name = 'conf';
    if ( typeof(func) != 'undefined' ){
        func_name = func;
    }

    var con = '<p style="color: #666; margin-bottom: 7px">提示：Ctrl+F 搜索关键字，Ctrl+G 查找下一个，Ctrl+S 保存，Ctrl+Shift+R 查找替换!</p>\
                <textarea class="bt-input-text" style="height: 320px; line-height:18px;" id="textBody"></textarea>\
                <button id="onlineEditFileBtn" class="btn btn-success btn-sm" style="margin-top:10px;">保存</button>\
                <ul class="help-info-text c7 ptb15">\
                    <li>此处为'+ _name + version +'主配置文件,若您不了解配置规则,请勿随意修改。</li>\
                </ul>';
    $(".soft-man-con").html(con);

    var loadT = layer.msg('配置文件路径获取中...',{icon:16,time:0,shade: [0.3, '#000']});
    $.post('/plugins/run', {name:_name, func:func_name,version:version},function (data) {
        layer.close(loadT);

        var loadT2 = layer.msg('文件内容获取中...',{icon:16,time:0,shade: [0.3, '#000']});
        var fileName = data.data;
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
                        pluginConfigSave(fileName);
                    }
                },
                lineNumbers: true,
                matchBrackets:true,
            });
            editor.focus();
            $(".CodeMirror-scroll").css({"height":"300px","margin":0,"padding":0});
            $("#onlineEditFileBtn").click(function(){
                $("#textBody").text(editor.getValue());
                pluginConfigSave(fileName);
            });
        },'json');
    },'json');
}
