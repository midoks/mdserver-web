//软件管理
function phpSoftMain(name, key) {
    if (!isNaN(name)) {
        var nametext = "php" + name;
        name = name.replace(".", "");
    }

    var loadT = layer.msg(lan.public.the, { icon: 16, time: 0, shade: [0.3, '#000'] });
    $.get('/plugins?action=getPluginInfo&name=php', function(rdata) {
        layer.close(loadT);
        nameA = rdata.versions[key];
        bodys = [
            '<p class="bgw pstate" data-id="0"><a href="javascript:service(\'' + name + '\',' + nameA.run + ')">' + lan.soft.php_main1 + '</a><span class="spanmove"></span></p>',
            '<p data-id="1"><a id="phpext" href="javascript:SetPHPConfig(\'' + name + '\',' + nameA.pathinfo + ')">' + lan.soft.php_main5 + '</a><span class="spanmove"></span></p>',
            '<p data-id="2"><a href="javascript:SetPHPConf(\'' + name + '\')">' + lan.soft.config_edit + '</a><span class="spanmove"></span></p>',
            '<p data-id="3"><a href="javascript:phpUploadLimit(\'' + name + '\',' + nameA.max + ')">' + lan.soft.php_main2 + '</a><span class="spanmove"></span></p>',
            '<p class="phphide" data-id="4"><a href="javascript:phpTimeLimit(\'' + name + '\',' + nameA.maxTime + ')">' + lan.soft.php_main3 + '</a><span class="spanmove"></span></p>',
            '<p data-id="5"><a href="javascript:configChange(\'' + name + '\')">' + lan.soft.php_main4 + '</a><span class="spanmove"></span></p>',
            '<p data-id="6"><a href="javascript:disFun(\'' + name + '\')">' + lan.soft.php_main6 + '</a><span class="spanmove"></span></p>',
            '<p class="phphide" data-id="7"><a href="javascript:SetFpmConfig(\'' + name + '\')">' + lan.soft.php_main7 + '</a><span class="spanmove"></span></p>',
            '<p class="phphide" data-id="8"><a href="javascript:GetPHPStatus(\'' + name + '\')">' + lan.soft.php_main8 + '</a><span class="spanmove"></span></p>',
            '<p class="phphide" data-id="9"><a href="javascript:GetFpmLogs(\'' + name + '\')">FPM日志</a><span class="spanmove"></span></p>',
            '<p class="phphide" data-id="10"><a href="javascript:GetFpmSlowLogs(\'' + name + '\')">慢日志</a><span class="spanmove"></span></p>',
            '<p data-id="11"><a href="javascript:BtPhpinfo(\'' + name + '\')">phpinfo</a><span class="spanmove"></span></p>'
        ]

        var sdata = '';
        if (rdata.phpSort == false) {
            rdata.phpSort = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11];
        } else {
            rdata.phpSort = rdata.phpSort.split('|');
        }
        for (var i = 0; i < rdata.phpSort.length; i++) {
            sdata += bodys[rdata.phpSort[i]];
        }

        layer.open({
            type: 1,
            area: '640px',
            title: nametext + lan.soft.admin,
            closeBtn: 2,
            shift: 0,
            content: '<div class="bt-w-main" style="width:640px;">\
				<input name="softMenuSortOrder" type="hidden" />\
				<div class="bt-w-menu soft-man-menu">\
					' + sdata + '\
				</div>\
				<div id="webEdit-con" class="bt-w-con pd15" style="height:555px;overflow:auto">\
					<div class="soft-man-con"></div>\
				</div>\
			</div>'
        });
        if (name == "52") {
            $(".phphide").hide();
        }

        if (rdata.versions.length < 5) {
            $(".phphide").hide();
            $(".pstate").hide();
            SetPHPConfig(name, nameA.pathinfo);
            $("p[data-id='4']").addClass('bgw');
        } else {
            service(name, nameA.run);
        }

        $(".bt-w-menu p a").click(function() {
            var txt = $(this).text();
            $(this).parent().addClass("bgw").siblings().removeClass("bgw");
            if (txt != lan.soft.php_menu_ext) $(".soft-man-con").removeAttr("style");
        });
        $(".soft-man-menu").dragsort({ dragSelector: ".spanmove", dragEnd: MenusaveOrder });
    });
}

//FPM日志
function GetFpmLogs(phpversion) {
    var loadT = layer.msg(lan.public.the, { icon: 16, time: 0, shade: [0.3, '#000'] });
    $.get('/ajax?action=GetFpmLogs&version=' + phpversion, function(logs) {
        layer.close(loadT);
        if (logs.status !== true) {
            logs.msg = '';
        }
        if (logs.msg == '') logs.msg = '当前没有fpm日志.';
        var phpCon = '<textarea readonly="" style="margin: 0px;width: 500px;height: 520px;background-color: #333;color:#fff; padding:0 5px" id="error_log">' + logs.msg + '</textarea>';
        $(".soft-man-con").html(phpCon);
        var ob = document.getElementById('error_log');
        ob.scrollTop = ob.scrollHeight;
    });
}

//FPM-Slow日志
function GetFpmSlowLogs(phpversion) {
    var loadT = layer.msg(lan.public.the, { icon: 16, time: 0, shade: [0.3, '#000'] });
    $.get('/ajax?action=GetFpmSlowLogs&version=' + phpversion, function(logs) {
        layer.close(loadT);
        if (logs.status !== true) {
            logs.msg = '';
        }
        if (logs.msg == '') logs.msg = '当前没有慢日志.';
        var phpCon = '<textarea readonly="" style="margin: 0px;width: 500px;height: 520px;background-color: #333;color:#fff; padding:0 5px" id="error_log">' + logs.msg + '</textarea>';
        $(".soft-man-con").html(phpCon);
        var ob = document.getElementById('error_log');
        ob.scrollTop = ob.scrollHeight;
    });
}


//配置修改
function SetPHPConf(version) {
    var loadT = layer.msg(lan.public.the, { icon: 16, time: 0, shade: [0.3, '#000'] });
    $.post('/config?action=GetPHPConf', 'version=' + version, function(rdata) {
        layer.close(loadT);
        var mlist = '';
        for (var i = 0; i < rdata.length; i++) {
            var w = '70'
            if (rdata[i].name == 'error_reporting') w = '250';
            var ibody = '<input style="width: ' + w + 'px;" class="bt-input-text mr5" name="' + rdata[i].name + '" value="' + rdata[i].value + '" type="text" >';
            switch (rdata[i].type) {
                case 0:
                    var selected_1 = (rdata[i].value == 1) ? 'selected' : '';
                    var selected_0 = (rdata[i].value == 0) ? 'selected' : '';
                    ibody = '<select class="bt-input-text mr5" name="' + rdata[i].name + '" style="width: ' + w + 'px;"><option value="1" ' + selected_1 + '>开启</option><option value="0" ' + selected_0 + '>关闭</option></select>'
                    break;
                case 1:
                    var selected_1 = (rdata[i].value == 'On') ? 'selected' : '';
                    var selected_0 = (rdata[i].value == 'Off') ? 'selected' : '';
                    ibody = '<select class="bt-input-text mr5" name="' + rdata[i].name + '" style="width: ' + w + 'px;"><option value="On" ' + selected_1 + '>开启</option><option value="Off" ' + selected_0 + '>关闭</option></select>'
                    break;
            }
            mlist += '<p><span>' + rdata[i].name + '</span>' + ibody + ', <font>' + rdata[i].ps + '</font></p>'
        }
        var phpCon = '<style>.conf_p p{margin-bottom: 2px}</style><div class="conf_p" style="margin-bottom:0">\
						' + mlist + '\
						<div style="margin-top:10px; padding-right:15px" class="text-right"><button class="btn btn-success btn-sm mr5" onclick="SetPHPConf(' + version + ')">' + lan.public.fresh + '</button><button class="btn btn-success btn-sm" onclick="SubmitPHPConf(' + version + ')">' + lan.public.save + '</button></div>\
					</div>'
        $(".soft-man-con").html(phpCon);
    });
}


//提交PHP配置
function SubmitPHPConf(version) {
    var data = {
        version: version,
        display_errors: $("select[name='display_errors']").val(),
        'cgi.fix_pathinfo': $("select[name='cgi.fix_pathinfo']").val(),
        'date.timezone': $("input[name='date.timezone']").val(),
        short_open_tag: $("select[name='short_open_tag']").val(),
        asp_tags: $("select[name='asp_tags']").val() || 'On',
        safe_mode: $("select[name='safe_mode']").val(),
        max_execution_time: $("input[name='max_execution_time']").val(),
        max_input_time: $("input[name='max_input_time']").val(),
        memory_limit: $("input[name='memory_limit']").val(),
        post_max_size: $("input[name='post_max_size']").val(),
        file_uploads: $("select[name='file_uploads']").val(),
        upload_max_filesize: $("input[name='upload_max_filesize']").val(),
        max_file_uploads: $("input[name='max_file_uploads']").val(),
        default_socket_timeout: $("input[name='default_socket_timeout']").val(),
        error_reporting: $("input[name='error_reporting']").val() || 'On'
    }

    var loadT = layer.msg(lan.public.the, { icon: 16, time: 0, shade: [0.3, '#000'] });
    $.post('/config?action=SetPHPConf', data, function(rdata) {
        layer.close(loadT);
        layer.msg(rdata.msg, { icon: rdata.status ? 1 : 2 });
    });

}


//php超时限制
function phpTimeLimit(version, max) {
    var LimitCon = '<p class="conf_p"><input class="phpTimeLimit bt-input-text mr5" type="number" value="' + max + '">' + lan.bt.s + '<button class="btn btn-success btn-sm" onclick="SetPHPMaxTime(\'' + version + '\')" style="margin-left:20px">' + lan.public.save + '</button></p>';
    $(".soft-man-con").html(LimitCon);
}
//设置超时限制
function SetPHPMaxTime(version) {
    var max = $(".phpTimeLimit").val();
    var loadT = layer.msg(lan.soft.the_save, { icon: 16, time: 0, shade: [0.3, '#000'] });
    $.post('/config?action=setPHPMaxTime', 'version=' + version + '&time=' + max, function(rdata) {
        $(".bt-w-menu .active").attr('onclick', "phpTimeLimit('" + version + "'," + max + ")");
        $(".bt-w-menu .active a").attr('href', "javascript:phpTimeLimit('" + version + "'," + max + ");");
        layer.close(loadT);
        layer.msg(rdata.msg, { icon: rdata.status ? 1 : 2 });
    });
}
//设置PHP上传限制
function SetPHPMaxSize(version) {
    max = $(".phpUploadLimit").val();
    if (max < 2) {
        alert(max);
        layer.msg(lan.soft.php_upload_size, { icon: 2 });
        return;
    }
    var loadT = layer.msg(lan.soft.the_save, { icon: 16, time: 0, shade: [0.3, '#000'] });
    $.post('/config?action=setPHPMaxSize', '&version=' + version + '&max=' + max, function(rdata) {
        $(".bt-w-menu .active").attr('onclick', "phpUploadLimit('" + version + "'," + max + ")");
        $(".bt-w-menu .active a").attr('href', "javascript:phpUploadLimit('" + version + "'," + max + ");");
        layer.close(loadT);
        layer.msg(rdata.msg, { icon: rdata.status ? 1 : 2 });
    })
}
//配置修改
function configChange(type) {
    var con = '<p style="color: #666; margin-bottom: 7px">' + lan.bt.edit_ps + '</p><textarea class="bt-input-text" style="height: 320px; line-height:18px;" id="textBody"></textarea>\
					<button id="OnlineEditFileBtn" class="btn btn-success btn-sm" style="margin-top:10px;">' + lan.public.save + '</button>\
					<ul class="help-info-text c7 ptb15">\
						<li>' + lan.get('config_edit_ps', [type]) + '</li>\
					</ul>';
    $(".soft-man-con").html(con);
    var fileName = '';
    switch (type) {
        case 'mysqld':
            fileName = '/etc/my.cnf';
            break;
        case 'nginx':
            fileName = '/www/server/nginx/conf/nginx.conf';
            break;
        case 'pure-ftpd':
            fileName = '/www/server/pure-ftpd/etc/pure-ftpd.conf';
            break;
        case 'apache':
            fileName = '/www/server/apache/conf/httpd.conf';
            break;
        case 'tomcat':
            fileName = '/www/server/tomcat/conf/server.xml';
            break;
        case 'memcached':
            fileName = '/etc/init.d/memcached';
            break;
        case 'redis':
            fileName = '/www/server/redis/redis.conf';
            break;
        default:
            fileName = '/www/server/php/' + type + '/etc/php.ini';
            break;
    }
    var loadT = layer.msg(lan.soft.get, { icon: 16, time: 0, shade: [0.3, '#000'] });
    $.post('/files?action=GetFileBody', 'path=' + fileName, function(rdata) {
        layer.close(loadT);
        $("#textBody").empty().text(rdata.data);
        $(".CodeMirror").remove();
        var editor = CodeMirror.fromTextArea(document.getElementById("textBody"), {
            extraKeys: { "Ctrl-Space": "autocomplete" },
            lineNumbers: true,
            matchBrackets: true,
        });
        editor.focus();
        $(".CodeMirror-scroll").css({ "height": "300px", "margin": 0, "padding": 0 });
        $("#OnlineEditFileBtn").click(function() {
            $("#textBody").text(editor.getValue());
            confSafe(fileName);
        });
    });
}


//设置PATHINFO
function SetPathInfo(version, type) {
    var loadT = layer.msg(lan.public.the, { icon: 16, time: 0, shade: [0.3, '#000'] });
    $.post('/config?action=setPathInfo', 'version=' + version + '&type=' + type, function(rdata) {
        var pathinfo = (type == 'on') ? true : false;
        var pathinfoOpt = '<a style="color:red;" href="javascript:SetPathInfo(\'' + version + '\',\'off\');">' + lan.public.off + '</a>'
        if (!pathinfo) {
            pathinfoOpt = '<a class="link" href="javascript:SetPathInfo(\'' + version + '\',\'on\');">' + lan.public.on + '</a>'
        }
        var pathinfo1 = '<td>PATH_INFO</td><td>' + lan.soft.php_menu_ext + '</td><td>' + lan.soft.mvc_ps + '</td><td><span class="ico-' + (pathinfo ? 'start' : 'stop') + ' glyphicon glyphicon-' + (pathinfo ? 'ok' : 'remove') + '"></span></td><td style="text-align: right;" width="50">' + pathinfoOpt + '</td>';
        $("#pathInfo").html(pathinfo1);
        $(".bt-w-menu .bgw").attr('onclick', "SetPHPConfig('" + version + "'," + pathinfo + ",1)");
        $(".bt-w-menu .bgw a").attr('href', "javascript:SetPHPConfig('" + version + "'," + pathinfo + ",1);");
        layer.msg(rdata.msg, { icon: 1 });
    });
}


//PHP扩展配置
function SetPHPConfig(version, pathinfo, go) {
    $.get('/ajax?action=GetPHPConfig&version=' + version, function(rdata) {
        var body = ""
        var opt = ""
        for (var i = 0; i < rdata.libs.length; i++) {
            if (rdata.libs[i].versions.indexOf(version) == -1) continue;
            if (rdata.libs[i]['task'] == '-1' && rdata.libs[i].phpversions.indexOf(version) != -1) {
                opt = '<a style="color:green;" href="javascript:messagebox();">' + lan.soft.the_install + '</a>'
            } else if (rdata.libs[i]['task'] == '0' && rdata.libs[i].phpversions.indexOf(version) != -1) {
                opt = '<a style="color:#C0C0C0;" href="javascript:messagebox();">' + lan.soft.sleep_install + '</a>'
            } else if (rdata.libs[i].status) {
                opt = '<a style="color:red;" href="javascript:UninstallPHPLib(\'' + version + '\',\'' + rdata.libs[i].name + '\',\'' + rdata.libs[i].title + '\',' + pathinfo + ');">' + lan.soft.uninstall + '</a>'
            } else {
                opt = '<a class="btlink" href="javascript:InstallPHPLib(\'' + version + '\',\'' + rdata.libs[i].name + '\',\'' + rdata.libs[i].title + '\',' + pathinfo + ');">' + lan.soft.install + '</a>'
            }

            body += '<tr>' +
                '<td>' + rdata.libs[i].name + '</td>' +
                '<td>' + rdata.libs[i].type + '</td>' +
                '<td>' + rdata.libs[i].msg + '</td>' +
                '<td><span class="ico-' + (rdata.libs[i].status ? 'start' : 'stop') + ' glyphicon glyphicon-' + (rdata.libs[i].status ? 'ok' : 'remove') + '"></span></td>' +
                '<td style="text-align: right;">' + opt + '</td>' +
                '</tr>'
        }

        var pathinfoOpt = '<a style="color:red;" href="javascript:SetPathInfo(\'' + version + '\',\'off\');">' + lan.soft.off + '</a>'
        if (!rdata.pathinfo) {
            pathinfoOpt = '<a class="btlink" href="javascript:SetPathInfo(\'' + version + '\',\'on\');">' + lan.soft.on + '</a>'
        }
        var pathinfo1 = '<tr id="pathInfo"><td>PATH_INFO</td><td>' + lan.soft.php_menu_ext + '</td><td>' + lan.soft.mvc_ps + '</td><td><span class="ico-' + (rdata.pathinfo ? 'start' : 'stop') + ' glyphicon glyphicon-' + (rdata.pathinfo ? 'ok' : 'remove') + '"></span></td><td style="text-align: right;" width="50">' + pathinfoOpt + '</td></tr>';
        var con = '<div class="divtable" id="phpextdiv" style="margin-right:10px;height: 420px; overflow: auto; margin-right: 0px;">' +
            '<table class="table table-hover" width="100%" cellspacing="0" cellpadding="0" border="0">' +
            '<thead>' +
            '<tr>' +
            '<th>' + lan.soft.php_ext_name + '</th>' +
            '<th width="64">' + lan.soft.php_ext_type + '</th>' +
            '<th>' + lan.soft.php_ext_ps + '</th>' +
            '<th width="40">' + lan.soft.php_ext_status + '</th>' +
            '<th style="text-align: right;" width="50">' + lan.public.action + '</th>' +
            '</tr>' +
            '</thead>' +
            '<tbody>' + pathinfo1 + body + '</tbody>' +
            '</table>' +
            '</div>' +
            '<ul class="help-info-text c7 pull-left"><li>请按实际需求安装扩展,不要安装不必要的PHP扩展,这会影响PHP执行效率,甚至出现异常</li><li>Redis扩展只允许在1个PHP版本中使用,安装到其它PHP版本请在[软件管理]重装Redis</li><li>opcache/xcache/apc等脚本缓存扩展,请只安装其中1个,否则可能导致您的站点程序异常</li></ul>';
        var divObj = document.getElementById('phpextdiv');
        var scrollTopNum = 0;
        if (divObj) scrollTopNum = divObj.scrollTop;
        $(".soft-man-con").html(con);
        document.getElementById('phpextdiv').scrollTop = scrollTopNum;
    });

    if (go == undefined) {
        setTimeout(function() {
            if ($(".bgw #phpext").html() != '安装扩展') {
                return;
            }
            SetPHPConfig(version, pathinfo);
        }, 3000);
    }
}

//安装扩展
function InstallPHPLib(version, name, title, pathinfo) {
    layer.confirm(lan.soft.php_ext_install_confirm.replace('{1}', name), { icon: 3, closeBtn: 2 }, function() {
        name = name.toLowerCase();
        var data = "name=" + name + "&version=" + version + "&type=1";
        var loadT = layer.msg(lan.soft.add_install, { icon: 16, time: 0, shade: [0.3, '#000'] });
        $.post('/files?action=InstallSoft', data, function(rdata) {
            setTimeout(function() {
                layer.close(loadT);
                SetPHPConfig(version, pathinfo, true);
                setTimeout(function() {
                    layer.msg(rdata.msg, { icon: rdata.status ? 1 : 2 });
                }, 1000);
            }, 1000);
        });

        fly("bi-btn");
        InstallTips();
        GetTaskCount();
    });
}

//卸载扩展
function UninstallPHPLib(version, name, title, pathinfo) {
    layer.confirm(lan.soft.php_ext_uninstall_confirm.replace('{1}', name), { icon: 3, closeBtn: 2 }, function() {
        name = name.toLowerCase();
        var data = 'name=' + name + '&version=' + version;
        var loadT = layer.msg(lan.public.the, { icon: 16, time: 0, shade: [0.3, '#000'] });
        $.post('/files?action=UninstallSoft', data, function(rdata) {
            layer.close(loadT);
            layer.msg(rdata.msg, { icon: rdata.status ? 1 : 2 });
            SetPHPConfig(version, pathinfo, true);
        });
    });
}
//禁用函数
function disFun(version) {
    $.get('/ajax?action=GetPHPConfig&version=' + version, function(rdata) {
        var disable_functions = rdata.disable_functions.split(',');
        var dbody = ''
        for (var i = 0; i < disable_functions.length; i++) {
            if (disable_functions[i] == '') continue;
            dbody += "<tr><td>" + disable_functions[i] + "</td><td><a style='float:right;' href=\"javascript:disable_functions('" + version + "','" + disable_functions[i] + "','" + rdata.disable_functions + "');\">" + lan.public.del + "</a></td></tr>";
        }

        var con = "<div class='dirBinding'>" +
            "<input class='bt-input-text mr5' type='text' placeholder='" + lan.soft.fun_ps1 + "' id='disable_function_val' style='height: 28px; border-radius: 3px;width: 410px;' />" +
            "<button class='btn btn-success btn-sm' onclick=\"disable_functions('" + version + "',1,'" + rdata.disable_functions + "')\">" + lan.public.add + "</button>" +
            "</div>" +
            "<div class='divtable mtb15' style='height:350px;overflow:auto'><table class='table table-hover' width='100%' style='margin-bottom:0'>" +
            "<thead><tr><th>" + lan.soft.php_ext_name + "</th><th width='100' class='text-right'>" + lan.public.action + "</th></tr></thead>" +
            "<tbody id='blacktable'>" + dbody + "</tbody>" +
            "</table></div>";

        con += '\
		<ul class="help-info-text">\
			<li>' + lan.soft.fun_ps2 + '</li>\
			<li>' + lan.soft.fun_ps3 + '</li>\
		</ul>';

        $(".soft-man-con").html(con);
    });
}
//设置禁用函数
function disable_functions(version, act, fs) {
    var fsArr = fs.split(',');
    if (act == 1) {
        var functions = $("#disable_function_val").val();
        for (var i = 0; i < fsArr.length; i++) {
            if (functions == fsArr[i]) {
                layer.msg(lan.soft.fun_msg, { icon: 5 });
                return;
            }
        }
        fs += ',' + functions;
        msg = lan.public.add_success;
    } else {

        fs = '';
        for (var i = 0; i < fsArr.length; i++) {
            if (act == fsArr[i]) continue;
            fs += fsArr[i] + ','
        }
        msg = lan.public.del_success;
        fs = fs.substr(0, fs.length - 1);
    }

    var data = 'version=' + version + '&disable_functions=' + fs;
    var loadT = layer.msg(lan.public.the, { icon: 16, time: 0, shade: [0.3, '#000'] });
    $.post('/config?action=setPHPDisable', data, function(rdata) {
        layer.close(loadT);
        layer.msg(rdata.status ? msg : rdata.msg, { icon: rdata.status ? 1 : 2 });
        disFun(version);
    });
}
//性能调整
function SetFpmConfig(version, action) {
    if (action == 1) {
        $.post('/system?action=GetMemInfo', '', function(memInfo) {
            var limit_children = parseInt(memInfo['memTotal'] / 8);
            var max_children = Number($("input[name='max_children']").val());
            var start_servers = Number($("input[name='start_servers']").val());
            var min_spare_servers = Number($("input[name='min_spare_servers']").val());
            var max_spare_servers = Number($("input[name='max_spare_servers']").val());
            var pm = $("select[name='pm']").val();

            if (limit_children < max_children) {
                layer.msg('当前服务器内存不足，最大允许[' + limit_children + ']个子进程!', { icon: 2 });
                $("input[name='max_children']").focus();
                return;
            }

            if (max_children < max_spare_servers) {
                layer.msg(lan.soft.php_fpm_err1, { icon: 2 });
                return;
            }

            if (min_spare_servers > start_servers) {
                layer.msg(lan.soft.php_fpm_err2, { icon: 2 });
                return;
            }

            if (max_spare_servers < min_spare_servers) {
                layer.msg(lan.soft.php_fpm_err3, { icon: 2 });
                return;
            }

            if (max_children < start_servers) {
                layer.msg(lan.soft.php_fpm_err4, { icon: 2 });
                return;
            }

            if (max_children < 1 || start_servers < 1 || min_spare_servers < 1 || max_spare_servers < 1) {
                layer.msg(lan.soft.php_fpm_err5, { icon: 2 });
                return;
            }
            var data = 'version=' + version + '&max_children=' + max_children + '&start_servers=' + start_servers + '&min_spare_servers=' + min_spare_servers + '&max_spare_servers=' + max_spare_servers + '&pm=' + pm;
            var loadT = layer.msg(lan.public.the, { icon: 16, time: 0, shade: [0.3, '#000'] });
            $.post('/config?action=setFpmConfig', data, function(rdata) {
                layer.close(loadT);
                var loadT = layer.msg(rdata.msg, { icon: rdata.status ? 1 : 2 });
            }).error(function() {
                layer.close(loadT);
                layer.msg(lan.public.config_ok, { icon: 1 });
            });
        });
        return;
    }

    $.post('/config?action=getFpmConfig', 'version=' + version, function(rdata) {

        var limitList = "<option value='0'>" + lan.soft.concurrency_m + "</option>" +
            "<option value='1' " + (rdata.max_children == 30 ? 'selected' : '') + ">30" + lan.soft.concurrency + "</option>" +
            "<option value='2' " + (rdata.max_children == 50 ? 'selected' : '') + ">50" + lan.soft.concurrency + "</option>" +
            "<option value='3' " + (rdata.max_children == 100 ? 'selected' : '') + ">100" + lan.soft.concurrency + "</option>" +
            "<option value='4' " + (rdata.max_children == 200 ? 'selected' : '') + ">200" + lan.soft.concurrency + "</option>" +
            "<option value='5' " + (rdata.max_children == 300 ? 'selected' : '') + ">300" + lan.soft.concurrency + "</option>" +
            "<option value='6' " + (rdata.max_children == 500 ? 'selected' : '') + ">500" + lan.soft.concurrency + "</option>"
        var pms = [{ 'name': 'static', 'title': lan.bt.static }, { 'name': 'dynamic', 'title': lan.bt.dynamic }];
        var pmList = '';
        for (var i = 0; i < pms.length; i++) {
            pmList += '<option value="' + pms[i].name + '" ' + ((pms[i].name == rdata.pm) ? 'selected' : '') + '>' + pms[i].title + '</option>';
        }
        var body = "<div class='bingfa'>" +
            "<p class='line'><span class='span_tit'>" + lan.soft.concurrency_type + "：</span><select class='bt-input-text' name='limit' style='width:100px;'>" + limitList + "</select></p>" +
            "<p class='line'><span class='span_tit'>" + lan.soft.php_fpm_model + "：</span><select class='bt-input-text' name='pm' style='width:100px;'>" + pmList + "</select><span class='c9'>*" + lan.soft.php_fpm_ps1 + "</span></p>" +
            "<p class='line'><span class='span_tit'>max_children：</span><input class='bt-input-text' type='number' name='max_children' value='" + rdata.max_children + "' /><span class='c9'>*" + lan.soft.php_fpm_ps2 + "</span></p>" +
            "<p class='line'><span class='span_tit'>start_servers：</span><input class='bt-input-text' type='number' name='start_servers' value='" + rdata.start_servers + "' />  <span class='c9'>*" + lan.soft.php_fpm_ps3 + "</span></p>" +
            "<p class='line'><span class='span_tit'>min_spare_servers：</span><input class='bt-input-text' type='number' name='min_spare_servers' value='" + rdata.min_spare_servers + "' />   <span class='c9'>*" + lan.soft.php_fpm_ps4 + "</span></p>" +
            "<p class='line'><span class='span_tit'>max_spare_servers：</span><input class='bt-input-text' type='number' name='max_spare_servers' value='" + rdata.max_spare_servers + "' />   <span class='c9'>*" + lan.soft.php_fpm_ps5 + "</span></p>" +
            "<div class='mtb15'><button class='btn btn-success btn-sm' onclick='SetFpmConfig(\"" + version + "\",1)'>" + lan.public.save + "</button></div>" +
            "</div>"

        $(".soft-man-con").html(body);
        $("select[name='limit']").change(function() {
            var type = $(this).val();
            var max_children = rdata.max_children;
            var start_servers = rdata.start_servers;
            var min_spare_servers = rdata.min_spare_servers;
            var max_spare_servers = rdata.max_spare_servers;
            switch (type) {
                case '1':
                    max_children = 30;
                    start_servers = 5;
                    min_spare_servers = 5;
                    max_spare_servers = 20;
                    break;
                case '2':
                    max_children = 50;
                    start_servers = 15;
                    min_spare_servers = 15;
                    max_spare_servers = 35;
                    break;
                case '3':
                    max_children = 100;
                    start_servers = 20;
                    min_spare_servers = 20;
                    max_spare_servers = 70;
                    break;
                case '4':
                    max_children = 200;
                    start_servers = 25;
                    min_spare_servers = 25;
                    max_spare_servers = 150;
                    break;
                case '5':
                    max_children = 300;
                    start_servers = 30;
                    min_spare_servers = 30;
                    max_spare_servers = 180;
                    break;
                case '6':
                    max_children = 500;
                    start_servers = 35;
                    min_spare_servers = 35;
                    max_spare_servers = 250;
                    break;
            }

            $("input[name='max_children']").val(max_children);
            $("input[name='start_servers']").val(start_servers);
            $("input[name='min_spare_servers']").val(min_spare_servers);
            $("input[name='max_spare_servers']").val(max_spare_servers);
        });
    });
}

//phpinfo
function BtPhpinfo(version) {
    var con = '<button class="btn btn-default btn-sm" onclick="GetPHPInfo(\'' + version + '\')">' + lan.soft.phpinfo + '</button>';
    $(".soft-man-con").html(con);
}
//获取PHPInfo
function GetPHPInfo(version) {
    var loadT = layer.msg(lan.soft.get, { icon: 16, time: 0, shade: [0.3, '#000'] });
    $.get('/ajax?action=GetPHPInfo&version=' + version, function(rdata) {
        layer.close(loadT);
        layer.open({
            type: 1,
            title: "PHP-" + version + "-PHPINFO",
            area: ['70%', '90%'],
            closeBtn: 2,
            shadeClose: true,
            content: rdata.replace('a:link {color: #009; text-decoration: none; background-color: #fff;}', '').replace('a:link {color: #000099; text-decoration: none; background-color: #ffffff;}', '')
        });
    });
}


//查看PHP负载状态
function GetPHPStatus(version) {
    $.post('/ajax?action=GetPHPStatus', 'version=' + version, function(rdata) {
        var con = "<div style='height:420px;overflow:hidden;'><table class='table table-hover table-bordered GetPHPStatus' style='margin:0;padding:0'>\
						<tr><th>" + lan.bt.php_pool + "</th><td>" + rdata.pool + "</td></tr>\
						<tr><th>" + lan.bt.php_manager + "</th><td>" + ((rdata['process manager'] == 'dynamic') ? lan.bt.dynamic : lan.bt.static) + "</td></tr>\
						<tr><th>" + lan.bt.php_start + "</th><td>" + rdata['start time'] + "</td></tr>\
						<tr><th>" + lan.bt.php_accepted + "</th><td>" + rdata['accepted conn'] + "</td></tr>\
						<tr><th>" + lan.bt.php_queue + "</th><td>" + rdata['listen queue'] + "</td></tr>\
						<tr><th>" + lan.bt.php_max_queue + "</th><td>" + rdata['max listen queue'] + "</td></tr>\
						<tr><th>" + lan.bt.php_len_queue + "</th><td>" + rdata['listen queue len'] + "</td></tr>\
						<tr><th>" + lan.bt.php_idle + "</th><td>" + rdata['idle processes'] + "</td></tr>\
						<tr><th>" + lan.bt.php_active + "</th><td>" + rdata['active processes'] + "</td></tr>\
						<tr><th>" + lan.bt.php_total + "</th><td>" + rdata['total processes'] + "</td></tr>\
						<tr><th>" + lan.bt.php_max_active + "</th><td>" + rdata['max active processes'] + "</td></tr>\
						<tr><th>" + lan.bt.php_max_children + "</th><td>" + rdata['max children reached'] + "</td></tr>\
						<tr><th>" + lan.bt.php_slow + "</th><td>" + rdata['slow requests'] + "</td></tr>\
					 </table></div>";
        $(".soft-man-con").html(con);
        $(".GetPHPStatus td,.GetPHPStatus th").css("padding", "7px");
    })
}


//php上传限制
function phpUploadLimit(version, max) {
    var LimitCon = '<p class="conf_p"><input class="phpUploadLimit bt-input-text mr5" type="number" value="' + max + '" name="max">MB<button class="btn btn-success btn-sm" onclick="SetPHPMaxSize(\'' + version + '\')" style="margin-left:20px">' + lan.public.save + '</button></p>';
    $(".soft-man-con").html(LimitCon);
}

function GetPHPStatus(a) {
    if(a == "52") {
        layer.msg(lan.bt.php_status_err, {
            icon: 2
        });
        return
    }
    $.post("/ajax?action=GetPHPStatus", "version=" + a, function(b) {
        layer.open({
            type: 1,
            area: "400",
            title: lan.bt.php_status_title,
            closeBtn: 2,
            shift: 5,
            shadeClose: true,
            content: "<div style='margin:15px;'><table class='table table-hover table-bordered'>                        <tr><th>"+lan.bt.php_pool+"</th><td>" + b.pool + "</td></tr>                        <tr><th>"+lan.bt.php_manager+"</th><td>" + ((b["process manager"] == "dynamic") ? lan.bt.dynamic : lan.bt.static) + "</td></tr>                     <tr><th>"+lan.bt.php_start+"</th><td>" + b["start time"] + "</td></tr>                      <tr><th>"+lan.bt.php_accepted+"</th><td>" + b["accepted conn"] + "</td></tr>                        <tr><th>"+lan.bt.php_queue+"</th><td>" + b["listen queue"] + "</td></tr>                        <tr><th>"+lan.bt.php_max_queue+"</th><td>" + b["max listen queue"] + "</td></tr>                        <tr><th>"+lan.bt.php_len_queue+"</th><td>" + b["listen queue len"] + "</td></tr>                        <tr><th>"+lan.bt.php_idle+"</th><td>" + b["idle processes"] + "</td></tr>                       <tr><th>"+lan.bt.php_active+"</th><td>" + b["active processes"] + "</td></tr>                       <tr><th>"+lan.bt.php_total+"</th><td>" + b["total processes"] + "</td></tr>                     <tr><th>"+lan.bt.php_max_active+"</th><td>" + b["max active processes"] + "</td></tr>                       <tr><th>"+lan.bt.php_max_children+"</th><td>" + b["max children reached"] + "</td></tr>                     <tr><th>"+lan.bt.php_slow+"</th><td>" + b["slow requests"] + "</td></tr>                     </table></div>"
        })
    })
}

pluginService('php', $('.bt-form .plugin_version').attr('version'));
