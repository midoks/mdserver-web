//转换单们到MB
function ToSizeM(byteLen) {
    var a = parseInt(byteLen) / 1024 / 1024;
    return a || 0;
}

//重置插件弹出框宽度
function resetPluginWinWidth(width){
    $("div[id^='layui-layer'][class*='layui-layer-page']").width(width);
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


//插件设置菜单
function pluginMan(name, title) {
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
            var len = plugin.versions.length;
            var version_info = '';
            var version = '';
            var softPath = '';
            var titleClick = '';
            var state = '';
            var indexshow = '';
            var checked = '';

            checked = plugin.display ? 'checked' : '';

            console.log(plugin.versions);
    
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

            console.log(version_info);

            var handle = '<a class="btlink" onclick="addVersion(\'' + plugin.name + '\',\'' + version_info + '\',\'' + plugin.tip + '\',this,\'' + plugin.title + '\')">安装</a>';
            var isSetup = false;
            for (var n = 0; n < len; n++) {
                if (plugin.status == true) {
                    isSetup = true;
                    // if (plugin.tip == 'lib') {
                    //     var mupdate = (plugin.versions[n].no == plugin.versions[n].version) ? '' : '<a class="btlink" onclick="SoftUpdate(\'' + plugin.name + '\',\'' + plugin.versions + '\',\'' + plugin.versions[n].version + '\')">更新</a> | ';
                    //     handle = mupdate + '<a class="btlink" onclick="PluginMan(\'' + plugin.name + '\',\'' + plugin.title + '\')">' + lan.soft.setup + '</a> | <a class="btlink" onclick="UninstallVersion(\'' + plugin.name + '\',\'' + plugin.versions + '\',\'' + plugin.title + '\')">卸载</a>';
                    //     titleClick = 'onclick="PluginMan(\'' + plugin.name + '\',\'' + plugin.title + '\')" style="cursor:pointer"';
                    // } else {

                        var mupdate = '';//(plugin.versions[n] == plugin.updates[n]) '' : '<a class="btlink" onclick="SoftUpdate(\'' + plugin.name + '\',\'' + plugin.versions[n].version + '\',\'' + plugin.updates[n] + '\')">更新</a> | ';
                        if (plugin.versions[n] == '') mupdate = '';
                        handle = mupdate + '<a class="btlink" onclick="SoftMan(\'' + plugin.name + '\',\'' + version_info + '\')">' + lan.soft.setup + '</a> | <a class="btlink" onclick="UninstallVersion(\'' + plugin.name + '\',\'' + plugin.versions + '\',\'' + plugin.title + '\')">卸载</a>';
                        titleClick = 'onclick="SoftMan(\'' + plugin.name + '\',\'' + version_info + '\')" style="cursor:pointer"';
                    // }

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
                if (plugin.task == '-1') {
                    handle = '<a style="color:green;" href="javascript:task();">正在安装...</a>';
                } else if (isTask == '0') {
                    handle = '<a style="color:#C0C0C0;" href="javascript:task();">等待安装...</a>';
                }
            }

            var plugin_title = plugin.title
            if (isSetup){
                plugin_title = plugin.title + ' ' + version_info;
            }

            sBody += '<tr>' +
                '<td><span ' + titleClick + 
                '><img src="/plugins/file?name=' + plugin.name + 
                '&f=ico.png' + '">' + plugin_title + '</span></td>' +
                '<td>' + plugin.ps + '</td>' +
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
function softUpdate(name, version, update) {
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
			<div class='version line'>安装版本：<span style='margin-left:30px'>" + name + " " + version + "</span>" + optw + "</div>\
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

function addVersion(name, ver, type, obj, title) {
    // console.log(ver.indexOf('|'));
    var SelectVersion = '';
    // if (ver.indexOf('|') >= 0){
        var titlename = name;
        var veropt = ver.split("|");
       
        for (var i = 0; i < veropt.length; i++) {
            SelectVersion += '<option>' + name + ' ' + veropt[i] + '</option>';
        }
    //} else {
        // SelectVersion = ver;
    //}

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
			<div class='version line'>安装版本：<select id='SelectVersion' class='bt-input-text' style='margin-left:30px'>" + SelectVersion + "</select></div>\
	    	<div class='bt-form-submit-btn'>\
				<button type='button' class='btn btn-danger btn-sm btn-title' onclick='layer.closeAll()'>" + lan.public.close + "</button>\
		        <button type='button' id='bi-btn' class='btn btn-success btn-sm btn-title bi-btn'>" + lan.public.submit + "</button>\
	        </div>\
	    </div>"
    });

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
    layer.confirm(msgTpl('您真的要卸载[{1}-{2}]吗?', [title, version]), { icon: 3, closeBtn: 2 }, function() {
        var data = 'name=' + name + '&version=' + version;
        var loadT = layer.msg(lan.public.the, { icon: 16, time: 0, shade: [0.3, '#000'] });
        $.post('/plugins/uninstall', data, function(rdata) {
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