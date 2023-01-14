
function whPost(method, args,callback){
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });

    var req_data = {};
    req_data['name'] = 'webhook';
    req_data['func'] = method;
 
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


function whPostNoMessage(method, args,callback){

    var req_data = {};
    req_data['name'] = 'webhook';
    req_data['func'] = method;
 
    if (typeof(args) == 'string'){
        req_data['args'] = JSON.stringify(toArrayObject(args));
    } else {
        req_data['args'] = JSON.stringify(args);
    }

    $.post('/plugins/run', req_data, function(data) {;
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

function whPostCallbak(method, version, args,callback){
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });

    var req_data = {};
    req_data['name'] = 'webhook';
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

var whEditor = null;

//添加
function addHook(){
    layer.open({
        type: 1,
        area: '600px',
        title: '添加Hook',
        closeBtn: 1,
        shift: 5,
        shadeClose: false,
        btn:['提交','关闭'],
        content: "<div class='bt-form pd20'>\
                <div class='line'>\
                <span class='tname'>名称</span>\
                <div class='info-r'><input class='bt-input-text' placeholder='Hook名称' type='text' id='hook_title' name='title' style='width:380px' /></div>\
                </div>\
                <div class='line'>\
                <span class='tname'>执行脚本</span>\
                <div class='info-r'>\
                    <textarea id='hook_shell' style='width:380px; height:300px;border:1px solid #ccc;font-size:15px'></textarea>\
                </div>\
            </div>\
          </div>",
        success:function(){

            $("#hook_shell").empty().text('');
            $(".CodeMirror").remove();
            whEditor = CodeMirror.fromTextArea(document.getElementById("hook_shell"), {
                extraKeys: {
                    "Ctrl-Space": "autocomplete",
                    "Ctrl-F": "findPersistent",
                    "Ctrl-H": "replaceAll",
                    "Ctrl-S": function() {}
                },
                lineNumbers: true,
                matchBrackets:true,
                mode:"sh",
            });

            $(".CodeMirror-scroll").css({"height":"300px","margin":0,"padding":0});
            whEditor.focus();
        },
        yes:function(indexs){
            var loadT = layer.msg("提交中...",{icon:16,time:0});
            var data = {
              title: $("#hook_title").val(),
              shell: whEditor.getValue(),
            }
            whPost('add_hook', data, function(rdata){
                var rdata = $.parseJSON(rdata.data);
                if (!rdata.status){
                    layer.msg(rdata.msg,{icon:2});
                    return;
                }
                layer.close(indexs);
                showMsg(rdata.msg, function(){
                    getHookList();
                }, {icon:1}, 2000);
            });
        }
    });
}
//获取列表
function getHookList(){
    whPost('get_list', {}, function(rdata){
        var rdata = $.parseJSON(rdata.data);
        var zbody = '';
        var mlist = rdata.data.list;
        var script_dir = rdata.data.script_dir;
        for(var i=0;i<mlist.length;i++){
            zbody += '<tr>'
                +'<td>'+mlist[i].title+'</td>'
                +'<td>'+getLocalTime(mlist[i].addtime)+'</td>'
                +'<td>'+getLocalTime(mlist[i].uptime)+'</td>'
                +'<td>'+mlist[i].count+'</td>'
                +'<td><a href="javascript:showWebHookCode(\''+mlist[i].url+'\',\''+mlist[i].access_key+'\')" class="btlink">查看密钥</a></td>'
                +'<td><a href="javascript:runHook(\''+mlist[i].access_key+'\');" class="btlink">测试</a> | '
                +'<a href="javascript:onlineEditFile(0,\''+ script_dir + '/'+ mlist[i].access_key+'\',\'sh\');" class="btlink">编辑</a> | '
                +'<a href="javascript:getLogs(\''+ script_dir + '/' + mlist[i].access_key+'.log\');" class="btlink">日志</a> | '
                +'<a href="javascript:deleteHook(\''+mlist[i].access_key+'\',\''+ mlist[i].title +'\');" class="btlink">删除</a></td>'
            +'</tr>'
        }
        $("#zipBody").html(zbody);
    });
}

//查看密钥
function showWebHookCode(url,code){
    layer.open({
        type:1,
        title:'查看密钥',
        area: '600px', 
        shadeClose:false,
        closeBtn:2,
        content:'<div class="bt-form pd20">\
            <div class="line"><span class="tname" style="width:50px">密钥</span><input class="bt-input-text mr5" disabled="disabled" value="'+ code +'" style="width:420px" /><button class="btn btn-success btn-sm" onclick="bt.pub.copy_pass(\''+ code +'\')">复制密钥</button></div>\
            <div class="line help">\
                <b>WebHook使用方法:</b><br>\
                GET/POST:<br>\
                '+window.location.protocol + "//" + window.location.hostname + (window.location.port ? ':' + window.location.port: '')+'/hook?access_key='+code+'&amp;params=aaa<br>\
                @param access_key  string  HOOK密钥<br>\
                @param params string 自定义参数（在hook脚本中使用$1接收）| 多个参数 "1 2" -> $1为1, $2为2<br>\
            </div>\
        </div>' 
    })
}

function getLogsTimer(path,success,error){
     whPostNoMessage('get_log', {"path":path}, function(rdata){
        var rdata = $.parseJSON(rdata.data);
        if (!rdata.status){
            if (typeof(error) == 'function'){
                error();
            }
            return;   
        }

        $('[name="site_logs"]').text(rdata.data);
        if (typeof(success) == 'function'){
            success();
        }
    });
}

//查看日志
function getLogs(path){
    logs_web = layer.open({
        type:1,
        title:'任务执行日志',
        area: ['600px','400px'], 
        shadeClose:false,
        closeBtn:2,
        content:'<div class="bt-logs" style="font-size:0;">\
            <textarea class="bt-input-text mr20 site_logs pd10" name="site_logs" style="width:100%;line-height:22px;white-space: pre-line;font-size:12px;height:358px;border: none;" readonly="readonly">正在获取中...</textarea>\
        </div>',
        success:function(){
            $('[name="site_logs"]').scrollTop($('[name="site_logs"]')[0].scrollHeight);

            logs_timer = setInterval(function(){
                getLogsTimer(path,function(){
                
                },function(){
                    layer.msg(rdata.msg,{icon:2});
                    layer.close(logs_web);
                });
            },1000);
        },
        cancel:function(){
            clearInterval(logs_timer);
        }
    });    
}

//运行
function runHook(key){
    whPost('run_shell', {"access_key":key}, function(rdata){
        var rdata = $.parseJSON(rdata.data);
        if (!rdata.status){
            layer.msg(rdata.msg,{icon:2});
        }

        showMsg(rdata.msg,function(){
            getHookList();
        },{icon:1},2000);
    });
}
//删除
function deleteHook(key, title){
    layer.confirm('删除Hook-['+ title +']',{
        title:'是否删除Hook-['+ title +']任务，是否继续'
    },function(){
        whPost('del_hook', {"access_key":key}, function(rdata){
            var rdata = $.parseJSON(rdata.data);
            if (!rdata.status){
                layer.msg(rdata.msg,{icon:2});
            }

            showMsg(rdata.msg,function(){
                getHookList();
            },{icon:1},2000);
        });
    });
}

