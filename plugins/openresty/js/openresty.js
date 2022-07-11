function orPost(method, args, callback){
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });
    $.post('/plugins/run', {name:'openresty', func:method, args:JSON.stringify(args)}, function(data) {
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

function orPluginService(_name, version){
    var data = {name:_name, func:'status'}
    if ( typeof(version) != 'undefined' ){
        data['version'] = version;
    } else {
        version = '';
    }

    orPost('status', data, function(data){
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
            <button class="btn btn-default btn-sm" onclick="orPluginOpService(\''+_name+'\',\'restart\',\''+version+'\')">重启</button>\
            <button class="btn btn-default btn-sm" onclick="orPluginOpService(\''+_name+'\',\'reload\',\''+version+'\')">重载配置</button>\
        </div>'; 
    $(".soft-man-con").html(serviceCon);
}


function orPluginOpService(a, b, v) {

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
        orPost('get_os',{},function(data){
            var rdata = $.parseJSON(data.data);
            if (!rdata['auth']){
                layer.prompt({title: '检查到权限不足,需要输入密码!', formType: 1},function(pwd, index){
                
                    layer.close(index);
                    var data = {'pwd':pwd};
                    c += '&args='+JSON.stringify(data);
                    orPluginOpServiceOp(a,b,c,d,a,v);
                });
            } else {
                orPluginOpServiceOp(a,b,c,d,a,v);

            }
        });
    })
}

function orPluginOpServiceOp(a,b,c,d,a,v){
    var e = layer.msg(msgTpl('正在{1}{2}{3}服务,请稍候...',[d,a,v]), {icon: 16,time: 0});
    $.post("/plugins/run", c, function(g) {
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

        // setTimeout(function(){
        //     location.reload();
        // },2000);
    },'json').error(function() {
        layer.close(e);
        layer.msg('操作异常!', {icon: 2});
    });
}


//查看Nginx负载状态
function getOpenrestyStatus() {
    $.post('/plugins/run', {name:'openresty', func:'run_info'}, function(data) {
        if (!data.status){
            showMsg(data.msg, function(){}, null,3000);
            return;
        }
        try {
            var rdata = $.parseJSON(data.data);
            var con = "<div><table class='table table-hover table-bordered'>\
                            <tr><th>活动连接(Active connections)</th><td>" + rdata.active + "</td></tr>\
                            <tr><th>总连接次数(accepts)</th><td>" + rdata.accepts + "</td></tr>\
                            <tr><th>总握手次数(handled)</th><td>" + rdata.handled + "</td></tr>\
                            <tr><th>总请求数(requests)</th><td>" + rdata.requests + "</td></tr>\
                            <tr><th>请求数(Reading)</th><td>" + rdata.Reading + "</td></tr>\
                            <tr><th>响应数(Writing)</th><td>" + rdata.Writing + "</td></tr>\
                            <tr><th>驻留进程(Waiting)</th><td>" + rdata.Waiting + "</td></tr>\
                         </table></div>";
            $(".soft-man-con").html(con);
        }catch(err){
             showMsg(data.data, function(){}, null,3000);
        }
    },'json');
}

//nginx
function nginxSoftMain(name, version) {
    var loadT = layer.msg(lan.public.the, { icon: 16, time: 0, shade: [0.3, '#000'] });
    $.get('/system?action=GetConcifInfo', function(rdata) {
        layer.close(loadT);
        nameA = rdata['web'];
        var status = name == 'nginx' ? '<p onclick="GetNginxStatus()">' + lan.soft.nginx_status + '</p>' : '';
        var menu = '';
        if (version != undefined || version != '') {
            var menu = '<p onclick="softChangeVer(\'' + name + '\',\'' + version + '\')">' + lan.soft.nginx_version + '</p>';
        }

        var waf = ''
        if (name == 'nginx') {
            waf = '<p onclick="waf()">' + lan.soft.waf_title + '</p>'
        }

        var logsPath = (name == 'nginx') ? '/www/wwwlogs/nginx_error.log' : '/www/wwwlogs/error_log';
        layer.open({
            type: 1,
            area: '640px',
            title: name + '管理',
            closeBtn: 2,
            shift: 0,
            content: '<div class="bt-w-main" style="width:640px;">\
                <div class="bt-w-menu">\
                    <p class="bgw" onclick="service(\'' + name + '\',' + nameA.status + ')">' + lan.soft.web_service + '</p>\
                    <p onclick="configChange(\'' + name + '\')">' + lan.soft.config_edit + '</p>\
                    ' + waf + '\
                    ' + menu + '\
                    ' + status + '\
                    <p onclick="showLogs(\'' + logsPath + '\')">错误日志</p>\
                </div>\
                <div id="webEdit-con" class="bt-w-con pd15" style="height:555px;overflow:auto">\
                    <div class="soft-man-con"></div>\
                </div>\
            </div>'
        });
        service(name, nameA.status);
        $(".bt-w-menu p").click(function() {
            //var i = $(this).index();
            $(this).addClass("bgw").siblings().removeClass("bgw");
        });
    });
}

//显示指定日志
function showLogs(logPath) {
    var loadT = layer.msg(lan.public.the_get, { icon: 16, time: 0, shade: [0.3, '#000'] });
    $.post('/ajax?action=GetOpeLogs', { path: logPath }, function(rdata) {
        layer.close(loadT);
        if (rdata.msg == '') rdata.msg = '当前没有日志!';
        var ebody = '<div class="soft-man-con"><textarea readonly="" style="margin: 0px;width: 500px;height: 520px;background-color: #333;color:#fff; padding:0 5px" id="error_log">' + rdata.msg + '</textarea></div>';
        $(".soft-man-con").html(ebody);
        var ob = document.getElementById('error_log');
        ob.scrollTop = ob.scrollHeight;
    });
}

//WAF防火墙
function waf() {
    var loadT = layer.msg(lan.public.the_get, { icon: 16, time: 0, shade: [0.3, '#000'] });
    $.get("/waf?action=GetConfig", function(rdata) {
        layer.close(loadT);
        if (rdata.status == -1) {
            layer.msg(lan.soft.waf_not, { icon: 5, time: 5000 });
            return;
        }

        var whiteList = ""
        for (var i = 0; i < rdata.ipWhitelist.length; i++) {
            if (rdata.ipWhitelist[i] == "") continue;
            whiteList += "<tr><td>" + rdata.ipWhitelist[i] + "</td><td><a href=\"javascript:deleteWafKey('ipWhitelist','" + rdata.ipWhitelist[i] + "');\">" + lan.public.del + "</a></td></tr>";
        }

        var blackList = ""
        for (var i = 0; i < rdata.ipBlocklist.length; i++) {
            if (rdata.ipBlocklist[i] == "") continue;
            blackList += "<tr><td>" + rdata.ipBlocklist[i] + "</td><td><a href=\"javascript:deleteWafKey('ipBlocklist','" + rdata.ipBlocklist[i] + "');\">" + lan.public.del + "</a></td></tr>";
        }

        var cc = rdata.CCrate.split('/')

        var con = "<div class='wafConf'>\
                    <div class='wafConf-btn'>\
                        <span>" + lan.soft.waf_title + "</span><div class='ssh-item'>\
                            <input class='btswitch btswitch-ios' id='closeWaf' type='checkbox' " + (rdata.status == 1 ? 'checked' : '') + ">\
                            <label class='btswitch-btn' for='closeWaf' onclick='CloseWaf()'></label>\
                        </div>\
                        <div class='pull-right'>\
                        <button class='btn btn-default btn-sm' onclick='gzEdit()'>" + lan.soft.waf_edit + "</button>\
                        <button class='btn btn-default btn-sm' onclick='upLimit()'>" + lan.soft.waf_up_title + "</button>\
                        </div>\
                    </div>\
                    <div class='wafConf_checkbox label-input-group ptb10 relative'>\
                    <input type='checkbox' id='waf_UrlDeny' " + (rdata['UrlDeny'] == 'on' ? 'checked' : '') + " onclick=\"SetWafConfig('UrlDeny','" + (rdata['UrlDeny'] == 'on' ? 'off' : 'on') + "')\" /><label for='waf_UrlDeny'>" + lan.soft.waf_input1 + "</label>\
                    <input type='checkbox' id='waf_CookieMatch' " + (rdata['CookieMatch'] == 'on' ? 'checked' : '') + " onclick=\"SetWafConfig('CookieMatch','" + (rdata['CookieMatch'] == 'on' ? 'off' : 'on') + "')\" /><label for='waf_CookieMatch'>" + lan.soft.waf_input2 + "</label>\
                    <input type='checkbox' id='waf_postMatch' " + (rdata['postMatch'] == 'on' ? 'checked' : '') + " onclick=\"SetWafConfig('postMatch','" + (rdata['postMatch'] == 'on' ? 'off' : 'on') + "')\" /><label for='waf_postMatch'>" + lan.soft.waf_input3 + "</label>\
                    <input type='checkbox' id='waf_CCDeny' " + (rdata['CCDeny'] == 'on' ? 'checked' : '') + " onclick=\"SetWafConfig('CCDeny','" + (rdata['CCDeny'] == 'on' ? 'off' : 'on') + "')\" /><label for='waf_CCDeny'>" + lan.soft.waf_input4 + "</label>\
                    <input type='checkbox' id='waf_attacklog' " + (rdata['attacklog'] == 'on' ? 'checked' : '') + " onclick=\"SetWafConfig('attacklog','" + (rdata['attacklog'] == 'on' ? 'off' : 'on') + "')\" /><label for='waf_attacklog'>" + lan.soft.waf_input5 + "</label>\
                    <span class='glyphicon glyphicon-folder-open' style='position: absolute; right: 10px; top: 12px; color: orange;cursor: pointer' onclick='openPath(\"/www/wwwlogs/waf\")'></span>\
                    </div>\
                    <div class='wafConf_cc'>\
                    <span>" + lan.soft.waf_input6 + "</span><input id='CCrate_1' class='bt-input-text' type='number' value='" + cc[0] + "' style='width:80px;margin-right:30px'/>\
                    <span>" + lan.soft.waf_input7 + "(" + lan.bt.s + ")</span><input id='CCrate_2' class='bt-input-text' type='number' value='" + cc[1] + "' style='width:80px;'/>\
                    <button onclick=\"SetWafConfig('CCrate','')\" class='btn btn-default btn-sm'>" + lan.public.ok + "</button>\
                    </div>\
                    <div class='wafConf_ip'>\
                        <fieldset>\
                        <legend>" + lan.soft.waf_input8 + "</legend>\
                        <input type='text' id='ipWhitelist_val' class='bt-input-text mr5' placeholder='" + lan.soft.waf_ip + "' style='width:175px;' /><button onclick=\"addWafKey('ipWhitelist')\" class='btn btn-default btn-sm'>" + lan.public.add + "</button>\
                        <div class='table-overflow'><table class='table table-hover'>" + whiteList + "</table></div>\
                        </fieldset>\
                        <fieldset>\
                        <legend>" + lan.soft.waf_input9 + "</legend>\
                        <input type='text' id='ipBlocklist_val' class='bt-input-text mr5' placeholder='" + lan.soft.waf_ip + "' style='width:175px;' /><button onclick=\"addWafKey('ipBlocklist')\" class='btn btn-default btn-sm'>" + lan.public.add + "</button>\
                        <div class='table-overflow'><table class='table table-hover'>" + blackList + "</table></div>\
                        </fieldset>\
                    </div>\
                </div>"
        $(".soft-man-con").html(con);
    });
}

//上传限制
function upLimit() {
    var loadT = layer.msg(lan.public.the_get, { icon: 16, time: 0, shade: [0.3, '#000'] });
    $.get("/waf?action=GetConfig", function(rdata) {
        layer.close(loadT);
        var black_fileExt = ''
        for (var i = 0; i < rdata.black_fileExt.length; i++) {
            black_fileExt += "<tr><td>" + rdata.black_fileExt[i] + "</td><td><a style='float:right;' href=\"javascript:deleteWafKey('black_fileExt','" + rdata.black_fileExt[i] + "');\">" + lan.public.del + "</a></td></tr>";
        }

        if ($("#blacktable").html() != undefined) {
            $("#blacktable").html(black_fileExt);
            $("#black_fileExt_val").val('');
            return;
        }

        layer.open({
            type: 1,
            area: '300px',
            title: lan.soft.waf_up_title,
            closeBtn: 2,
            shift: 0,
            content: "<div class='dirBinding mlr15'>" +
                "<input class='bt-input-text mr5' type='text' placeholder='" + lan.soft.waf_up_from1 + "' id='black_fileExt_val' style='height: 28px; border-radius: 3px;width: 219px;margin-top:15px' />" +
                "<button class='btn btn-success btn-sm' onclick=\"addWafKey('black_fileExt')\">" + lan.public.add + "</button>" +
                "</div>" +
                "<div class='divtable' style='margin:15px'><table class='table table-hover' width='100%' style='margin-bottom:0'>" +
                "<thead><tr><th>" + lan.soft.waf_up_from2 + "</th><th width='100' class='text-right'>" + lan.public.action + "</th></tr></thead>" +
                "<tbody id='blacktable'>" + black_fileExt + "</tbody>" +
                "</table></div>"
        });
    });
}

//设置waf状态
function closeWaf() {
    var loadT = layer.msg(lan.public.the, { icon: 16, time: 0, shade: [0.3, '#000'] });
    $.post('/waf?action=SetStatus', '', function(rdata) {
        layer.close(loadT)
        layer.msg(rdata.msg, { icon: rdata.status ? 1 : 5 });
        if (rdata.status) waf();
    });
}

//取规则文件 
function getWafFile(name) {
    onlineEditFile(0, '/www/server/panel/vhost/wafconf/' + name);
}
//规则编辑
function gzEdit() {
    layer.open({
        type: 1,
        area: '360px',
        title: lan.soft.waf_edit,
        closeBtn: 2,
        shift: 0,
        content: "<div class='gzEdit'><button class='btn btn-default btn-sm' onclick=\"GetWafFile('cookie')\">Cookie</button>\
                <button class='btn btn-default btn-sm' onclick=\"GetWafFile('post')\">POST</button>\
                <button class='btn btn-default btn-sm' onclick=\"GetWafFile('url')\">URL</button>\
                <button class='btn btn-default btn-sm' onclick=\"GetWafFile('user-agent')\">User-Agent</button>\
                <button class='btn btn-default btn-sm' onclick=\"GetWafFile('args')\">Args</button>\
                <button class='btn btn-default btn-sm' onclick=\"GetWafFile('whiteurl')\">" + lan.soft.waf_url_white + "</button>\
                <button class='btn btn-default btn-sm' onclick=\"GetWafFile('returnhtml')\">" + lan.soft.waf_index + "</button>\
                <button class='btn btn-default btn-sm' onclick=\"updateWaf('returnhtml')\">" + lan.soft.waf_cloud + "</button></div>"
    });
}

//更新WAF规则
function updateWaf() {
    var loadT = layer.msg(lan.soft.waf_update, { icon: 16, time: 0, shade: [0.3, '#000'] });
    $.post('/waf?action=updateWaf', '', function(rdata) {
        layer.close(loadT)
        layer.msg(rdata.msg, { icon: rdata.status ? 1 : 5 });
    });
}

//设置WAF配置值
function setWafConfig(name, value) {
    if (name == 'CCrate') {
        var CCrate_1 = $("#CCrate_1").val();
        var CCrate_2 = $("#CCrate_2").val();
        if (CCrate_1 < 1 || CCrate_1 > 3000 || CCrate_2 < 1 || CCrate_2 > 1800) {
            layer.msg(lan.soft.waf_cc_err, { icon: 5 });
            return;
        }
        value = CCrate_1 + '/' + CCrate_2;
    }
    var loadT = layer.msg(lan.public.the, { icon: 16, time: 0, shade: [0.3, '#000'] });
    $.post('/waf?action=SetConfigString', 'name=' + name + '&value=' + value, function(rdata) {
        layer.close(loadT)
        layer.msg(rdata.msg, { icon: rdata.status ? 1 : 5 });
        if (rdata.status) waf();

    });
}


//删除WAF指定值
function deleteWafKey(name, value) {
    var loadT = layer.msg(lan.public.the, { icon: 16, time: 0, shade: [0.3, '#000'] });
    $.post('/waf?action=SetConfigList&act=del', 'name=' + name + '&value=' + value, function(rdata) {
        layer.close(loadT)
        layer.msg(rdata.msg, { icon: rdata.status ? 1 : 5 });
        if (rdata.status) waf();
        if (name == 'black_fileExt') upLimit();
    });
}

//删除WAF指定值
function addWafKey(name) {
    var value = $('#' + name + '_val').val();
    var loadT = layer.msg(lan.public.the, { icon: 16, time: 0, shade: [0.3, '#000'] });
    $.post('/waf?action=SetConfigList&act=add', 'name=' + name + '&value=' + value, function(rdata) {
        layer.close(loadT)
        layer.msg(rdata.msg, { icon: rdata.status ? 1 : 5 });
        if (rdata.status) waf();
        if (name == 'black_fileExt') upLimit();
    });
}
