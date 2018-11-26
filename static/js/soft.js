

function MenusaveOrder() {
    var data = $(".soft-man-menu > p").map(function() { return $(this).attr("data-id"); }).get();
    var ssort = data.join("|");
    $("input[name=softMenuSortOrder]").val(ssort);
    $.post('/ajax?action=phpSort', 'ssort=' + ssort, function() {});
};

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
function GetNginxStatus() {
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
    })
}

//软件管理窗口
function SoftMan(name, version) {
    var loadT = layer.msg("正在处理,请稍后...", { icon: 16, time: 0, shade: [0.3, '#000'] });
    $.get('/plugins/setting?name='+name, function(rdata) {
        layer.close(loadT);
        layer.open({
            type: 1,
            area: '640px',
            title: name + "管理",
            closeBtn: 2,
            shift: 0,
            content: rdata
        });
        $(".bt-w-menu p").click(function() {
            $(this).addClass("bgw").siblings().removeClass("bgw");
        });
    });
}

//转换单们到MB
function ToSizeM(byteLen) {
    var a = parseInt(byteLen) / 1024 / 1024;
    return a || 0;
}


//首页软件列表
function indexsoft() {
    return;
    var loadT = layer.msg('正在获取列表...', { icon: 16, time: 0, shade: [0.3, '#000'] });
    $.post('/plugins/get_plugin_list', 'display=1', function(rdata) {
        layer.close(loadT);
        var con = '';
        for (var i = 0; i < rdata['data'].length - 1; i++) {
            var len = rdata.data[i].versions.length;
            var version_info = '';
            for (var j = 0; j < len; j++) {
                if (rdata.data[i].versions[j].status) continue;
                version_info += rdata.data[i].versions[j].version + '|';
            }
            if (version_info != '') {
                version_info = version_info.substring(0, version_info.length - 1);
            }
            if (rdata.data[i].display) {
                var isDisplay = false;
                if (rdata.data[i].name != 'php') {
                    for (var n = 0; n < len; n++) {
                        if (rdata.data[i].versions[n].status == true) {
                            isDisplay = true;
                            var version = rdata.data[i].versions[n].version;
                            if (rdata.data[i].versions[n].run == true) {
                                state = '<span style="color:#20a53a" class="glyphicon glyphicon-play"></span>'
                            } else {
                                state = '<span style="color:red" class="glyphicon glyphicon-pause"></span>'
                            }
                        }
                    }
                    if (isDisplay) {
                        var clickName = 'SoftMan';
                        if (rdata.data[i].tip == 'lib') {
                            clickName = 'PluginMan';
                            version_info = rdata.data[i].title;
                        }

                        con += '<div class="col-sm-3 col-md-3 col-lg-3" data-id="' + rdata.data[i].pid + '">\
									<span class="spanmove"></span>\
									<div onclick="' + clickName + '(\'' + rdata.data[i].name + '\',\'' + version_info + '\')">\
									<div class="image"><img src="/static/img/soft_ico/ico-' + rdata.data[i].name + '.png"></div>\
									<div class="sname">' + rdata.data[i].title + ' ' + version + state + '</div>\
									</div>\
								</div>'
                    }
                } else {
                    for (var n = 0; n < len; n++) {
                        if (rdata.data[i].versions[n].status == true) {
                            var version = rdata.data[i].versions[n].version;
                            if (rdata.data[i].versions[n].run == true) {
                                state = '<span style="color:#20a53a" class="glyphicon glyphicon-play"></span>'
                            } else {
                                state = '<span style="color:red" class="glyphicon glyphicon-pause"></span>'
                            }
                        }
                        if (rdata.data[i].versions[n].display == true) {
                            con += '<div class="col-sm-3 col-md-3 col-lg-3" data-id="' + rdata.data[i].pid + '">\
								<span class="spanmove"></span>\
								<div onclick="phpSoftMain(\'' + rdata.data[i].versions[n].version + '\',' + n + ')">\
								<div class="image"><img src="/static/img/soft_ico/ico-' + rdata.data[i].name + '.png"></div>\
								<div class="sname">' + rdata.data[i].title + ' ' + rdata.data[i].versions[n].version + state + '</div>\
								</div>\
							</div>'
                        }
                    }
                }
            }
        }
        $("#indexsoft").html(con);
        //软件位置移动
        var softboxlen = $("#indexsoft > div").length;
        var softboxsum = 12;
        var softboxcon = '';
        var softboxn = softboxlen;
        if (softboxlen <= softboxsum) {
            for (var i = 0; i < softboxsum - softboxlen; i++) {
                softboxn += 1000;
                softboxcon += '<div class="col-sm-3 col-md-3 col-lg-3 no-bg" data-id="' + softboxn + '"></div>'
            }
            $("#indexsoft").append(softboxcon);
        }
        $("#indexsoft").dragsort({ dragSelector: ".spanmove", dragBetween: true, dragEnd: saveOrder, placeHolderTemplate: "<div class='col-sm-3 col-md-3 col-lg-3 dashed-border'></div>" });

        function saveOrder() {
            var data = $("#indexsoft > div").map(function() { return $(this).attr("data-id"); }).get();
            var ssort = data.join("|");
            $("input[name=list1SortOrder]").val(ssort);
            $.post("/plugin?action=savePluginSort", 'ssort=' + ssort, function(rdata) {});
        };
    });
}

//插件设置菜单
function PluginMan(name, title) {
    loadT = layer.msg(lan.soft.menu_temp, { icon: 16, time: 0, shade: [0.3, '#000'] });
    $.get('/plugins/setting?name=' + name, function(rhtml) {
        layer.close(loadT);
        if (rhtml.status === false) {
            if (name == "phpguard") {
                layer.msg(lan.soft.menu_phpsafe, { icon: 1 })
            } else {
                layer.msg(rhtml.msg, { icon: 2 });
            }
            return;
        }
        layer.open({
            type: 1,
            shift: 5,
            offset: '20%',
            closeBtn: 2,
            area: '700px',
            title: '' + title,
            content: rhtml
        });
        rcode = rhtml.split('<script type="javascript/text">')[1]
        if (!rcode) rcode = rhtml.split('<script type="text/javascript">')[1]
        rcode = rcode.replace('</script>', '');
        setTimeout(function() {
            if (!!(window.attachEvent && !window.opera)) {
                execScript(rcode);
            } else {
                window.eval(rcode);
            }
        }, 200)

    });
}


//设置插件
function SetPluginConfig(name, param, def) {
    if (def == undefined) def = 'SetConfig';
    loadT = layer.msg(lan.config.config_save, { icon: 16, time: 0, shade: [0.3, '#000'] });
    $.post('/plugin?action=a&name=' + name + '&s=' + def, param, function(rdata) {
        layer.close(loadT);
        layer.msg(rdata.msg, { icon: rdata.status ? 1 : 2 });
    });
}



//取软件列表
function GetSList(isdisplay) {
    if (isdisplay !== true) {
        var loadT = layer.msg(lan.soft.get_list, { icon: 16, time: 0, shade: [0.3, '#000'] })
    }
    if (!isdisplay || isdisplay === true)
        isdisplay = getCookie('p' + getCookie('softType'));
    if (isdisplay == true || isdisplay == 'true') isdisplay = 1;

    var search = $("#SearchValue").val();
    if (search != '') {
        search = '&search=' + search;
    }
    var type = '';
    var istype = getCookie('softType');
    if (istype == 'undefined' || istype == 'null' || !istype) {
        istype = '0';
    }

    type = '&type=' + istype;
    var page = '';
    if (isdisplay) {
        page = '&p=' + isdisplay;
        setCookie('p' + getCookie('softType'), isdisplay);
    }

    var condition = (search + type + page).slice(1);
    $.post('/plugins/list?' + condition, '', function(rdata) {
        layer.close(loadT);
        var tBody = '';
        var sBody = '';
        var pBody = '';

        for (var i = 0; i < rdata.type.length; i++) {
            var c = '';
            if (istype == rdata.type[i].type) {
                c = 'class="on"';
            }
            tBody += '<span typeid="' + rdata.type[i].type + '" ' + c + '>' + rdata.type[i].title + '</span>';
        }

        $(".softtype").html(tBody);
        $("#softPage").html(rdata.list);
        $("#softPage .Pcount").css({ "position": "absolute", "left": "0" })

        $(".task").text(rdata.data[rdata.length - 1]);
        for (var i = 0; i < rdata.data.length; i++) {
            var plugin = rdata.data[i];
            var len = rdata.data[i].versions.length;
            var version_info = '';
            var version = '';
            var softPath = '';
            var titleClick = '';
            var state = '';
            var indexshow = '';
            var checked = '';

            checked = plugin.display ? 'checked' : '';
    
            if (typeof plugin.versions == "string"){
                version_info += plugin.versions + '|';
            } else {
                for (var j = 0; j < len; j++) {
                    version_info += plugin.versions[j] + '|';
                }
            }
            if (version_info != '') {
                version_info = version_info.substring(0, version_info.length - 1);
            }

            var handle = '<a class="btlink" onclick="AddVersion(\'' + plugin.name + '\',\'' + version_info + '\',\'' + plugin.tip + '\',this,\'' + plugin.title + '\')">安装</a>';
            var isSetup = false;
                for (var n = 0; n < len; n++) {
                    if (plugin.status == true) {
                        isSetup = true;
                        if (plugin.tip == 'lib') {
                            var mupdate = (plugin.versions[n].no == plugin.versions[n].version) ? '' : '<a class="btlink" onclick="SoftUpdate(\'' + plugin.name + '\',\'' + plugin.versions[n].version + '\',\'' + plugin.versions[n].version + '\')">更新</a> | ';
                            handle = mupdate + '<a class="btlink" onclick="PluginMan(\'' + plugin.name + '\',\'' + plugin.title + '\')">' + lan.soft.setup + '</a> | <a class="btlink" onclick="UninstallVersion(\'' + plugin.name + '\',\'' + plugin.versions[n].version + '\',\'' + plugin.title + '\')">卸载</a>';
                            titleClick = 'onclick="PluginMan(\'' + plugin.name + '\',\'' + plugin.title + '\')" style="cursor:pointer"';
                        } else {
                            console.log(plugin, n);


                            var mupdate = '';//(plugin.versions[n] == plugin.updates[n]) '' : '<a class="btlink" onclick="SoftUpdate(\'' + plugin.name + '\',\'' + plugin.versions[n].version + '\',\'' + plugin.updates[n] + '\')">更新</a> | ';
                            if (plugin.versions[n] == '') mupdate = '';
                            handle = mupdate + '<a class="btlink" onclick="SoftMan(\'' + plugin.name + '\',\'' + version_info + '\')">' + lan.soft.setup + '</a> | <a class="btlink" onclick="UninstallVersion(\'' + plugin.name + '\',\'' + plugin.versions[n].version + '\',\'' + plugin.title + '\')">卸载</a>';
                            titleClick = 'onclick="SoftMan(\'' + plugin.name + '\',\'' + version_info + '\')" style="cursor:pointer"';
                        }

                        version = plugin.version;
                        softPath = '<span class="glyphicon glyphicon-folder-open" title="' + rdata.data[i].path + '" onclick="openPath(\'' + rdata.data[i].path + '\')"></span>';
                        indexshow = '<div class="index-item"><input class="btswitch btswitch-ios" id="index_' + rdata.data[i].name + '" type="checkbox" ' + checked + '><label class="btswitch-btn" for="index_' + plugin.name + '" onclick="toIndexDisplay(\'' + plugin.name + '\',\'' + version + '\')"></label></div>';
                        if (rdata.data[i].versions[n].run == true) {
                            state = '<span style="color:#20a53a" class="glyphicon glyphicon-play"></span>'
                        } else {
                            state = '<span style="color:red" class="glyphicon glyphicon-pause"></span>'
                        }
                    }
                    var isTask = plugin.task;
                    if (isTask == '-1') {
                        handle = '<a style="color:green;" href="javascript:task();">正在安装...</a>';
                    } else if (isTask == '0') {
                        handle = '<a style="color:#C0C0C0;" href="javascript:task();">等待安装...</a>';
                    }
                }

                // console.log(plugin);

                sBody += '<tr>' +
                    '<td><span ' + titleClick + 
                    '><img src="/plugins/file?name=' + rdata.data[i].name + 
                    '&f=ico.png' + '">' + rdata.data[i].title + ' ' + version_info + '</span></td>' +
                    '<td>' + rdata.data[i].ps + '</td>' +
                    '<td>' + softPath + '</td>' +
                    '<td>' + state + '</td>' +
                    '<td>' + indexshow + '</td>' +
                    '<td style="text-align: right;">' + handle + '</td>' +
                    '</tr>';
        }
            

        sBody += pBody;
        $("#softList").html(sBody);
        $(".menu-sub span").click(function() {
            setCookie('softType', $(this).attr('typeid'));
            $(this).addClass("on").siblings().removeClass("on");
            GetSList();
        })
    },'json');
}

//刷新状态
function FPStatus() {
    $.get("/auth?action=flush_pay_status", function(res) {
        layer.msg(res.msg, { icon: res.status ? "1" : "2" })
    })
}
//更新
function SoftUpdate(name, version, update) {
    var msg = "<li>建议您在服务器负载闲时进行软件更新.</li>";
    if (name == 'mysql') msg = "<ul style='color:red;'><li>更新数据库有风险,建议在更新前,先备份您的数据库.</li><li>如果您的是云服务器,强烈建议您在更新前做一个快照.</li><li>建议您在服务器负载闲时进行软件更新.</li></ul>";
    SafeMessage('更新[' + name + ']', '更新过程可能会导致服务中断,您真的现在就将[' + name + ']更新到[' + update + ']吗?', function() {
        var data = "name=" + name + "&version=" + version + "&type=0&upgrade=" + update;
        var loadT = layer.msg('正在更新[' + name + '-' + version + '],请稍候...', { icon: 16, time: 0, shade: [0.3, '#000'] });
        $.post('/plugins/install', data, function(rdata) {
            if (rdata.status) {
                GetTaskCount();
                layer.msg('已添加到任务列表,请稍候...', { icon: 1 });
            } else {
                layer.msg('更新失败!', { icon: 2 });
            }

            layer.close(loadT);
        });
    }, msg);
}

//独立安装
function oneInstall(name, version) {
    var isError = false


    var optw = '';
    if (name == 'mysql') {
        optw = "<br><br><li style='color:red;'>" + lan.soft.mysql_f + "</li>"
        var sUrl = '/data?action=getData&table=databases';
        $.ajax({
            url: sUrl,
            type: "GET",
            async: false,
            success: function(dataD) {
                if (dataD.data.length > 0) {
                    layer.msg(lan.soft.mysql_d, { icon: 5, time: 5000 })
                    isError = true;;
                }
            }
        });
    }

    if (isError) return;
    var one = layer.open({
        type: 1,
        title: '选择安装方式',
        area: '350px',
        closeBtn: 2,
        shadeClose: true,
        content: "<div class='bt-form pd20 pb70 c6'>\
			<div class='version line'>" + lan.soft.install_version + "：<span style='margin-left:30px'>" + name + " " + version + "</span>" + optw + "</div>\
	    	<div class='fangshi line'>" + lan.bt.install_type + "：<label data-title='" + lan.bt.install_rpm_title + "'>极速安装<input type='checkbox' checked></label><label data-title='" + lan.bt.install_src_title + "'>源码安装<input type='checkbox'></label></div>\
	    	<div class='bt-form-submit-btn'>\
				<button type='button' class='btn btn-danger btn-sm btn-title one-close'>关闭</button>\
		        <button type='button' id='bi-btn' class='btn btn-success btn-sm btn-title bi-btn'>提交</button>\
	        </div>\
	    </div>"
    })
    $('.fangshi input').click(function() {
        $(this).attr('checked', 'checked').parent().siblings().find("input").removeAttr('checked');
    });
    $("#bi-btn").click(function() {
        var type = $('.fangshi input').prop("checked") ? '1' : '0';
        var data = "name=" + name + "&version=" + version + "&type=" + type;
        var loadT = layer.msg(lan.soft.add_install, { icon: 16, time: 0, shade: [0.3, '#000'] });
        $.post('/files?action=InstallSoft', data, function(rdata) {
            layer.closeAll();
            layer.msg(rdata.msg, { icon: rdata.status ? 1 : 2 });
            GetSList();
        })

    });
    $(".one-close").click(function() {
        layer.close(one);
    })
    InstallTips();
    fly("bi-btn");
}

function AddVersion(name, ver, type, obj, title) {
    if (type == "lib") {
        layer.confirm(lan.get('install_confirm', [title, ver]), { icon: 3, closeBtn: 2 }, function() {
            $(obj).text(lan.soft.install_the);
            var data = "name=" + name+"&version="+ver;
            var loadT = layer.msg(lan.soft.the_install, { icon: 16, time: 0, shade: [0.3, '#000'] });
            $.post("/plugins/install", data, function(rdata) {
                layer.close(loadT);
                layer.msg(rdata.msg, { icon: rdata.status ? 1 : 2 });
                setTimeout(function() { GetSList() }, 2000)
            });
        });
        return;
    }


    var titlename = name;
    var veropt = ver.split("|");
    var SelectVersion = '';
    for (var i = 0; i < veropt.length; i++) {
        SelectVersion += '<option>' + name + ' ' + veropt[i] + '</option>';
    }
    if (name == 'phpmyadmin' || name == 'nginx' || name == 'apache') {
        var isError = false
        $.ajax({
            url: '/ajax?action=GetInstalled',
            type: 'get',
            async: false,
            success: function(rdata) {
                if (name == 'nginx') {
                    if (rdata.webserver != name.toLowerCase() && rdata.webserver != false) {
                        layer.msg(lan.soft.err_install1, { icon: 2 })
                        isError = true;
                        return;
                    }
                }
                if (name == 'apache') {
                    if (rdata.webserver != name.toLowerCase() && rdata.webserver != false) {
                        layer.msg(lan.soft.err_install2, { icon: 2 })
                        isError = true;
                        return;
                    }
                }
                if (name == 'phpmyadmin') {
                    if (rdata.php.length < 1) {
                        layer.msg(lan.soft.err_install3, { icon: 2 })
                        isError = true;
                        return;
                    }
                    if (!rdata.mysql.setup) {
                        layer.msg(lan.soft.err_install4, { icon: 2 })
                        isError = true;
                        return;
                    }

                }
            }
        });
        if (isError) return;
    }

    layer.open({
        type: 1,
        title: titlename + lan.soft.install_title,
        area: '350px',
        closeBtn: 2,
        shadeClose: true,
        content: "<div class='bt-form pd20 pb70 c6'>\
			<div class='version line'>" + lan.soft.install_version + "：<select id='SelectVersion' class='bt-input-text' style='margin-left:30px'>" + SelectVersion + "</select></div>\
	    	<div class='fangshi line'>" + lan.bt.install_type + "：<label data-title='" + lan.bt.install_rpm_title + "'>" + lan.bt.install_rpm + "<input type='checkbox' checked></label><label data-title='" + lan.bt.install_src_title + "'>" + lan.bt.install_src + "<input type='checkbox'></label></div>\
	    	<div class='bt-form-submit-btn'>\
				<button type='button' class='btn btn-danger btn-sm btn-title' onclick='layer.closeAll()'>" + lan.public.close + "</button>\
		        <button type='button' id='bi-btn' class='btn btn-success btn-sm btn-title bi-btn'>" + lan.public.submit + "</button>\
	        </div>\
	    </div>"
    })
    selectChange();
    $('.fangshi input').click(function() {
        $(this).attr('checked', 'checked').parent().siblings().find("input").removeAttr('checked');
    });
    $("#bi-btn").click(function() {
        var info = $("#SelectVersion").val().toLowerCase();
        var name = info.split(" ")[0];
        var version = info.split(" ")[1];
        var type = $('.fangshi input').prop("checked") ? '1' : '0';
        var data = "name=" + name + "&version=" + version + "&type=" + type;

        var loadT = layer.msg(lan.soft.add_install, { icon: 16, time: 0, shade: [0.3, '#000'] });
        $.post("/plugins/install", data, function(rdata) {
            layer.closeAll();
            layer.msg(rdata.msg, { icon: rdata.status ? 1 : 2 });
            GetSList();
        });
    });
    InstallTips();
    fly("bi-btn");
}



//卸载软件
function UninstallVersion(name, version, title) {
    var isError = false
    if (name == 'mysql') {
        var sUrl = '/data?action=getData&table=databases';
        $.ajax({
            url: sUrl,
            type: "GET",
            async: false,
            success: function(dataD) {
                if (dataD.data.length > 0) {
                    layer.msg(lan.soft.mysql_del_err + '<p style="color:red">强行卸载: curl http://h.bt.cn/mu.sh|bash</p>', { icon: 5, time: 8000 });
                    isError = true;;
                }
            }
        });
    }
    if (isError) return;
    layer.confirm(lan.soft.uninstall_confirm.replace('{1}', title).replace('{2}', version), { icon: 3, closeBtn: 2 }, function() {
        var data = 'name=' + name + '&version=' + version;
        var loadT = layer.msg(lan.public.the, { icon: 16, time: 0, shade: [0.3, '#000'] });
        $.post('/plugins?action=unInstall', data, function(rdata) {
            layer.close(loadT)
            GetSList();
            layer.msg(rdata.msg, { icon: rdata.status ? 1 : 2 });
        })
    });
}


//首页显示
function toIndexDisplay(name, version) {
    var status = $("#index_" + name).prop("checked") ? "0" : "1";
    if (name == "php") {
        var verinfo = version.replace(/\./, "");
        status = $("#index_" + name + verinfo).prop("checked") ? "0" : "1";
    }
    var data = "name=" + name + "&status=" + status + "&version=" + version;
    $.post("/plugins/set_plugin_status", data, function(rdata) {
        if (rdata.status) {
            layer.msg(rdata.msg, { icon: 1 })
        }
    })
}

//刷新缓存
function flush_cache() {
    var loadT = layer.msg(lan.soft.get_list, { icon: 16, time: 0, shade: [0.3, '#000'] })
    $.post('/plugins?action=flush_cache', {}, function(rdata) {
        layer.close(loadT)
        layer.msg(rdata.msg, { icon: rdata.status ? 1 : 2 });
    });
}


// $(function() {
//     if (window.document.location.pathname == '/soft/') {
//         setInterval(function() { GetSList(true); }, 5000);
//     }
// });