
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
            title: name + lan.soft.admin,
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
function CloseWaf() {
    var loadT = layer.msg(lan.public.the, { icon: 16, time: 0, shade: [0.3, '#000'] });
    $.post('/waf?action=SetStatus', '', function(rdata) {
        layer.close(loadT)
        layer.msg(rdata.msg, { icon: rdata.status ? 1 : 5 });
        if (rdata.status) waf();
    });
}

//取规则文件 
function GetWafFile(name) {
    OnlineEditFile(0, '/www/server/panel/vhost/wafconf/' + name);
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
function SetWafConfig(name, value) {
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



//查看Nginx负载状态
function getStatus() {

    $.post('/plugins/run', {name:'openresty', func:'run_status'}, function(data) {
        console.log(data);
    },'json');
    $.post('/ajax?action=GetNginxStatus', '', function(rdata) {
        var con = "<div><table class='table table-hover table-bordered'>\
						<tr><th>" + lan.bt.nginx_active + "</th><td>" + rdata.active + "</td></tr>\
						<tr><th>" + lan.bt.nginx_accepts + "</th><td>" + rdata.accepts + "</td></tr>\
						<tr><th>" + lan.bt.nginx_handled + "</th><td>" + rdata.handled + "</td></tr>\
						<tr><th>" + lan.bt.nginx_requests + "</th><td>" + rdata.requests + "</td></tr>\
						<tr><th>" + lan.bt.nginx_reading + "</th><td>" + rdata.Reading + "</td></tr>\
						<tr><th>" + lan.bt.nginx_writing + "</th><td>" + rdata.Writing + "</td></tr>\
						<tr><th>" + lan.bt.nginx_waiting + "</th><td>" + rdata.Waiting + "</td></tr>\
					 </table></div>";
        $(".soft-man-con").html(con);
    },'json');
}

function openrestyOp(a, b) {

    var c = "name=" + a + "&func=" + b;
    var d = "";

    switch(b) {
        case "stop":d = '停止';break;
        case "start":d = '启动';break;
        case "restart":d = '重启';break;
        case "reload":d = '重载';break;
    }
    layer.confirm( '您真的要{1}{2}服务吗？'.replace('{1}', d).replace('{2}', a), {icon:3,closeBtn: 2}, function() {
        var e = layer.msg('正在{1}{2}服务,请稍候...'.replace('{1}', d).replace('{2}', a), {icon: 16,time: 0});
        $.post("/plugins/run", c, function(g) {
            layer.close(e);
            
            var f = g.data == 'ok' ? '{1}服务已{2}'.replace('{1}', a).replace('{2}', d):'{1}服务{2}失败!'.replace('{1}', a).replace('{2}', d);
            layer.msg(f, {icon: g.data == 'ok' ? 1 : 2});
            
            if(b != "reload" && g.data == 'ok') {
                if (b == 'start') {
                    setRedisService('redis', true);
                } else if (b=='stop'){
                    setRedisService('redis', false);
                } else {
                }
            }
            if(g.data != 'ok') {
                layer.msg(g.data, {icon: 2,time: 0,shade: 0.3,shadeClose: true});
            }
        },'json').error(function() {
            layer.close(e);
            layer.msg('操作成功!', {icon: 1});
        });
    })
}

//服务
function setOpenrestyService(name, status){
    var serviceCon ='<p class="status">当前状态：<span>'+(status ? '开启' : '关闭' )+
        '</span><span style="color: '+
        (status?'#20a53a;':'red;')+
        ' margin-left: 3px;" class="glyphicon ' + (status?'glyphicon glyphicon-play':'glyphicon-pause')+'"></span></p><div class="sfm-opt">\
            <button class="btn btn-default btn-sm" onclick="openrestyOp(\''+name+'\',\''+(status?'stop':'start')+'\')">'+(status?'停止':'启动')+'</button>\
            <button class="btn btn-default btn-sm" onclick="openrestyOp(\''+name+'\',\'restart\')">重启</button>\
            <button class="btn btn-default btn-sm" onclick="openrestyOp(\''+name+'\',\'reload\')">重载配置</button>\
        </div>'; 
    $(".soft-man-con").html(serviceCon);
}

//服务
function openrestyService(){

    $.post('/plugins/run', {name:'openresty', func:'status'}, function(data) {
        console.log(data);
        if(!data.status){
            layer.msg(data.msg,{icon:0,time:3000,shade: [0.3, '#000']});
            return;
        }
        if (data.data == 'start'){
            setOpenrestyService('openresty', true);
        } else {
            setOpenrestyService('openresty', false);
        }
    },'json');
}
openrestyService();
