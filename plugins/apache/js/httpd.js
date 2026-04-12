function httpPost(method, args, callback){
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });
    $.post('/plugins/run', {name:'apache', func:method, args:JSON.stringify(args)}, function(data) {
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

function httpPluginService(_name, version){
    var data = {name:_name, func:'status'}
    if ( typeof(version) != 'undefined' ){
        data['version'] = version;
    } else {
        version = '';
    }

    httpPost('status', data, function(data){
        if (data.data == 'start'){
            orPluginSetService(_name, true, version);
        } else {
            orPluginSetService(_name, false, version);
        }
    });
}

function orPluginSetService(_name ,status, version){
    var serviceCon ='<p class="status">当前状态：<span>'+(status ? '开启' : '关闭' )+
        '</span><span style="color: '+
        (status?'#20a53a;':'red;')+
        ' margin-left: 3px;" class="glyphicon ' + (status?'glyphicon glyphicon-play':'glyphicon-pause')+'"></span></p><div class="sfm-opt">\
            <button class="btn btn-default btn-sm" onclick="orPluginOpService(\''+_name+'\',\''+(status?'stop':'start')+'\',\''+version+'\')">'+(status?'停止':'启动')+'</button>\
            <button class="btn btn-default btn-sm" onclick="orPluginOpService(\''+_name+'\',\'restart\',\''+version+'\',\'yes\')">重启</button>\
            <button class="btn btn-default btn-sm" onclick="orPluginOpService(\''+_name+'\',\'reload\',\''+version+'\')">重载配置</button>\
        </div>'; 
    $(".soft-man-con").html(serviceCon);
}


function orPluginOpService(a, b, v,request_callback) {

    var c = "name=" + a + "&func=" + b;
    if(v != ''){
        c = c + '&version='+v;
    }

    var d = "";

    switch(b) {
        case "stop":d = '停止';break;
        case "start":d = '启动';break;
        case "restart":d = '重启';break;
        case "reload":d = '重载';break;
    }
    layer.confirm( msgTpl('您真的要{1}{2}{3}服务吗？', [d,a,v]), {icon:3,closeBtn: 2}, function() {
        httpPost('get_os',{},function(data){
            var rdata = $.parseJSON(data.data);
            if (!rdata['auth']){
                layer.prompt({title: '检查到权限不足,需要输入密码!', formType: 1},function(pwd, index){
                
                    layer.close(index);
                    var data = {'pwd':pwd};
                    c += '&args='+JSON.stringify(data);
                    orPluginOpServiceOp(a,b,c,d,a,v,request_callback);
                });
            } else {
                orPluginOpServiceOp(a,b,c,d,a,v,request_callback);

            }
        });
    })
}

function orPluginOpServiceOp(a,b,c,d,a,v,request_callback){

    var request_path = "/plugins/run";
    if (request_callback == 'yes'){
        request_path = "/plugins/callback";
    }

    var e = layer.msg(msgTpl('正在{1}{2}{3}服务,请稍候...',[d,a,v]), {icon: 16,time: 0});
    $.post(request_path, c, function(g) {
        layer.close(e);
        
        var f = g.data == 'ok' ? msgTpl('{1}{2}服务已{3}',[a,v,d]) : msgTpl('{1}{2}服务{3}失败!',[a,v,d]);
        layer.msg(f, {icon: g.data == 'ok' ? 1 : 2});
        
        if( b != "reload" && g.data == 'ok' ) {
            if ( b == 'start' ) {
                orPluginSetService(a, true, v);
            } else if ( b == 'stop' ){
                orPluginSetService(a, false, v);
            }
        }

        if( g.status && g.data != 'ok' ) {
            layer.msg(g.data, {icon: 2,time: 10000,shade: 0.3});
        }

    },'json').error(function() {
        layer.close(e);
        layer.msg('操作异常!', {icon: 2});
    });
}


// 定时器变量
var httpdStatusTimer = null;

//查看Apache负载状态
function getHttpdStatus() {
    $.post('/plugins/run', {name:'apache', func:'run_info'}, function(data) {
        try {
            var rdata = $.parseJSON(data.data);

            console.log(rdata);
            if ('status' in rdata && !rdata.status){
                showMsg(rdata.msg, function(){}, null,3000);
                return;
            }

            var con = "<div><table class='table table-hover table-bordered'>\
                            <tr><th>服务器版本(ServerVersion)</th><td>" + (rdata.ServerVersion || '-') + "</td></tr>\
                            <tr><th>服务器MPM(ServerMPM)</th><td>" + (rdata.ServerMPM || '-') + "</td></tr>\
                            <tr><th>服务器构建时间(Server Built)</th><td>" + (rdata['Server Built'] || '-') + "</td></tr>\
                            <tr><th>当前时间(CurrentTime)</th><td>" + (rdata.CurrentTime || '-') + "</td></tr>\
                            <tr><th>重启时间(RestartTime)</th><td>" + (rdata.RestartTime || '-') + "</td></tr>\
                            <tr><th>服务器运行时间(ServerUptime)</th><td>" + (rdata.ServerUptime || '-') + "</td></tr>\
                            <tr><th>服务器运行秒数(ServerUptimeSeconds)</th><td>" + (rdata.ServerUptimeSeconds || '-') + "</td></tr>\
                            <tr><th>1分钟负载(Load1)</th><td>" + (rdata.Load1 || '-') + "</td></tr>\
                            <tr><th>5分钟负载(Load5)</th><td>" + (rdata.Load5 || '-') + "</td></tr>\
                            <tr><th>15分钟负载(Load15)</th><td>" + (rdata.Load15 || '-') + "</td></tr>\
                            <tr><th>总访问次数(Total Accesses)</th><td>" + (rdata['Total Accesses'] || '-') + "</td></tr>\
                            <tr><th>总流量(Total kBytes)</th><td>" + (rdata['Total kBytes'] || '-') + " KB</td></tr>\
                            <tr><th>总请求时间(Total Duration)</th><td>" + (rdata['Total Duration'] || '-') + "</td></tr>\
                            <tr><th>CPU用户时间(CPUUser)</th><td>" + (rdata.CPUUser || '-') + "</td></tr>\
                            <tr><th>CPU系统时间(CPUSystem)</th><td>" + (rdata.CPUSystem || '-') + "</td></tr>\
                            <tr><th>CPU负载(CPULoad)</th><td>" + (rdata.CPULoad || '-') + "</td></tr>\
                            <tr><th>每秒请求数(ReqPerSec)</th><td>" + (rdata.ReqPerSec || '-') + "</td></tr>\
                            <tr><th>每秒流量(BytesPerSec)</th><td>" + (rdata.BytesPerSec || '-') + "</td></tr>\
                            <tr><th>每请求流量(BytesPerReq)</th><td>" + (rdata.BytesPerReq || '-') + "</td></tr>\
                            <tr><th>每请求时间(DurationPerReq)</th><td>" + (rdata.DurationPerReq || '-') + "</td></tr>\
                            <tr><th>活动工作进程(BusyWorkers)</th><td>" + (rdata.BusyWorkers || '-') + "</td></tr>\
                            <tr><th>优雅关闭进程(GracefulWorkers)</th><td>" + (rdata.GracefulWorkers || '-') + "</td></tr>\
                            <tr><th>空闲工作进程(IdleWorkers)</th><td>" + (rdata.IdleWorkers || '-') + "</td></tr>\
                            <tr><th>进程数(Processes)</th><td>" + (rdata.Processes || '-') + "</td></tr>\
                            <tr><th>总连接数(ConnsTotal)</th><td>" + (rdata.ConnsTotal || '-') + "</td></tr>\
                         </table></div>";
            $(".soft-man-con").html(con);
        }catch(err){
             showMsg(data.data, function(){}, null,3000);
        }
    },'json');
}

// 启动自动刷新
function startHttpdStatusAutoRefresh() {
    // 先清除现有的定时器
    if (httpdStatusTimer) {
        clearInterval(httpdStatusTimer);
    }
    
    // 立即执行一次
    getHttpdStatus();
    
    // 设置定时器，每5秒刷新一次
    httpdStatusTimer = setInterval(getHttpdStatus, 5000);
}

// 停止自动刷新
function stopHttpdStatusAutoRefresh() {
    if (httpdStatusTimer) {
        clearInterval(httpdStatusTimer);
        httpdStatusTimer = null;
    }
}


function setOpCfg(){
    httpPost('get_cfg', {}, function(data){
        var rdata = $.parseJSON(data.data);
        var rdata = rdata.data;
        // console.log(rdata);

        var mlist = '';
        for (var i = 0; i < rdata.length; i++) {
            var w = '70'
            var ibody = '<input style="width: ' + w + 'px;" class="bt-input-text mr5" name="' + rdata[i].name + '" value="' + rdata[i].value + '" type="text" >';
            switch (rdata[i].type) {
                case 0:
                    var selected_1 = (rdata[i].value == 1) ? 'selected' : '';
                    var selected_0 = (rdata[i].value == 0) ? 'selected' : '';
                    ibody = '<select class="bt-input-text mr5" name="' + rdata[i].name + '" style="width: ' + w + 'px;">\
                        <option value="1" ' + selected_1 + '>开启</option>\
                        <option value="0" ' + selected_0 + '>关闭</option>\
                    </select>';
                    break;
                case 1:
                    var selected_1 = (rdata[i].value == 'on') ? 'selected' : '';
                    var selected_0 = (rdata[i].value == 'off') ? 'selected' : '';
                    ibody = '<select class="bt-input-text mr5" name="' + rdata[i].name + '" style="width: ' + w + 'px;">\
                        <option value="on" ' + selected_1 + '>开启</option>\
                        <option value="off" ' + selected_0 + '>关闭</option>\
                    </select>';
                    break;
            }
            mlist += '<p style="margin-top:15px;"><span>' + rdata[i].name + '</span>' + ibody + "<b class='unit c9'>"+rdata[i].unit+"</b>" +', <font class="c9">' + rdata[i].ps + '</font></p>';
        }
        var con = '<style>.conf_p p{margin-bottom: 2px}</style><div class="conf_p" style="margin-bottom:0">\
                        ' + mlist + '\
                        <div style="margin-top:10px; padding-right:15px" class="text-right">\
                            <button class="btn btn-success btn-sm mr5" onclick="setOpCfg()">刷新</button>\
                            <button class="btn btn-success btn-sm" onclick="submitConf()">保存</button>\
                        </div>\
                    </div>'
        $(".soft-man-con").html(con);
    });
}

function submitConf() {
    var data = {};
    
    // 收集所有配置参数
    $("input[name]").each(function() {
        data[$(this).attr('name')] = $(this).val();
    });
    
    $("select[name]").each(function() {
        data[$(this).attr('name')] = $(this).val() || 'on';
    });

    // console.log(data);
    httpPost('set_cfg', data, function(rdata){
        var rdata = $.parseJSON(rdata.data);
        // console.log(rdata);
        layer.msg(rdata.msg, { icon: rdata.status ? 1 : 2 });
    });
}

function otherFunc(){
    var con = '<p class="conf_p" style="text-align:center;">\
            <button class="btn btn-default btn-sm" onclick="cronAddCheck()">添加检查任务</button>  \
            <button class="btn btn-default btn-sm" onclick="cronDelCheck()">删除检查任务</button>\
        </p>';
    $(".soft-man-con").html(con);
}

function cronAddCheck(){
    httpPost('cron_add_check', {}, function(data){
        var rdata = $.parseJSON(data.data);
        layer.msg(rdata.msg, { icon: rdata.status ? 1 : 2 });
    });
}

function cronDelCheck(){
    httpPost('cron_del_check', {}, function(data){
        var rdata = $.parseJSON(data.data);
        layer.msg(rdata.msg, { icon: rdata.status ? 1 : 2 });
    });
}












