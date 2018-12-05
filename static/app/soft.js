//转换单们到MB
function toSizeM(byteLen) {
    var a = parseInt(byteLen) / 1024 / 1024;
    return a || 0;
}

//重置插件弹出框宽度
function resetPluginWinWidth(width){
    $("div[id^='layui-layer'][class*='layui-layer-page']").width(width);
}

//软件管理窗口
function softMain(name, version) {
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

//取软件列表
function getSList(isdisplay) {
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
    $.get('/plugins/list?' + condition, '', function(rdata) {
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


            var handle = '<a class="btlink" onclick="addVersion(\'' + plugin.name + '\',\'' + version_info + '\',\'' + plugin.tip + '\',this,\'' + plugin.title + '\')">安装</a>';

            
            if (plugin.setup == true) {

                var mupdate = '';//(plugin.versions[n] == plugin.updates[n]) '' : '<a class="btlink" onclick="SoftUpdate(\'' + plugin.name + '\',\'' + plugin.versions[n].version + '\',\'' + plugin.updates[n] + '\')">更新</a> | ';
                // if (plugin.versions[n] == '') mupdate = '';
                handle = mupdate + '<a class="btlink" onclick="softMain(\'' + plugin.name + '\',\'' + version_info + '\')">设置</a> | <a class="btlink" onclick="uninstallVersion(\'' + plugin.name + '\',\'' + plugin.setup_version + '\',\'' + plugin.title + '\')">卸载</a>';
                titleClick = 'onclick="softMain(\'' + plugin.name + '\',\'' + version_info + '\')" style="cursor:pointer"';
             
                softPath = '<span class="glyphicon glyphicon-folder-open" title="' + plugin.path + '" onclick="openPath(\'' + plugin.path + '\')"></span>';
                if (plugin.coexist){
                    indexshow = '<div class="index-item"><input class="btswitch btswitch-ios" id="index_' + plugin.name  + plugin.versions + '" type="checkbox" ' + checked + '><label class="btswitch-btn" for="index_' + plugin.name + plugin.versions + '" onclick="toIndexDisplay(\'' + plugin.name + '\',\'' + plugin.versions + '\',\'' + plugin.coexist +'\')"></label></div>';
                } else {
                    indexshow = '<div class="index-item"><input class="btswitch btswitch-ios" id="index_' + plugin.name + '" type="checkbox" ' + checked + '><label class="btswitch-btn" for="index_' + plugin.name + '" onclick="toIndexDisplay(\'' + plugin.name + '\',\'' + plugin.setup_version + '\')"></label></div>';
                }
                
                if (plugin.status == true) {
                    state = '<span style="color:#20a53a" class="glyphicon glyphicon-play"></span>'
                } else {
                    state = '<span style="color:red" class="glyphicon glyphicon-pause"></span>'
                }
            }

            var isTask = plugin.task;
            if (plugin.task == '-2') {
                handle = '<a style="color:green;" href="javascript:task();">正在卸载...</a>';
            } else if (plugin.task == '-1') {
                handle = '<a style="color:green;" href="javascript:task();">正在安装...</a>';
            } else if (isTask == '0') {
                handle = '<a style="color:#C0C0C0;" href="javascript:task();">等待中...</a>';
            }

            var plugin_title = plugin.title;
            if (plugin.setup && !plugin.coexist){
                plugin_title = plugin.title + ' ' + plugin.setup_version;
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
            getSList();
        })
    },'json');
}

function addVersion(name, ver, type, obj, title) {
    var option = '';
    var titlename = name;
    if (ver.indexOf('|') >= 0){
        var veropt = ver.split("|");
        var SelectVersion = '';
        for (var i = 0; i < veropt.length; i++) {
            SelectVersion += '<option>' + name + ' ' + veropt[i] + '</option>';
        }
        option = "<select id='SelectVersion' class='bt-input-text' style='margin-left:30px'>" + SelectVersion + "</select>";
    } else {
        option = '<span id="SelectVersion">' + name + ' ' + ver + '</span>';
    }

    layer.open({
        type: 1,
        title: titlename + "软件安装",
        area: '350px',
        closeBtn: 2,
        shadeClose: true,
        content: "<div class='bt-form pd20 pb70 c6'>\
			<div class='version line'>安装版本：" + option + "</div>\
	    	<div class='bt-form-submit-btn'>\
				<button type='button' class='btn btn-danger btn-sm btn-title' onclick='layer.closeAll()'>关闭</button>\
		        <button type='button' id='bi-btn' class='btn btn-success btn-sm btn-title bi-btn'>提交</button>\
	        </div>\
	    </div>"
    });

    $('.fangshi input').click(function() {
        $(this).attr('checked', 'checked').parent().siblings().find("input").removeAttr('checked');
    });
    $("#bi-btn").click(function() {

        var info = $("#SelectVersion").val().toLowerCase();
        if (info == ''){
            info = $("#SelectVersion").text().toLowerCase();
        }
        var name = info.split(" ")[0];
        var version = info.split(" ")[1];
        var type = $('.fangshi input').prop("checked") ? '1' : '0';
        var data = "name=" + name + "&version=" + version + "&type=" + type;

        var loadT = layer.msg(lan.soft.add_install, { icon: 16, time: 0, shade: [0.3, '#000'] });
        $.post("/plugins/install", data, function(rdata) {
            layer.closeAll();
            layer.msg(rdata.msg, { icon: rdata.status ? 1 : 2 });
            getSList();
        });
    });
    InstallTips();
    fly("bi-btn");
}

//卸载软件
function uninstallVersion(name, version, title) {
    layer.confirm(msgTpl('您真的要卸载[{1}-{2}]吗?', [title, version]), { icon: 3, closeBtn: 2 }, function() {
        var data = 'name=' + name + '&version=' + version;
        var loadT = layer.msg(lan.public.the, { icon: 16, time: 0, shade: [0.3, '#000'] });
        $.post('/plugins/uninstall', data, function(rdata) {
            layer.close(loadT)
            getSList();
            layer.msg(rdata.msg, { icon: rdata.status ? 1 : 2 });
        },'json');
    });
}


//首页显示
function toIndexDisplay(name, version, coexist) {

    var status = $("#index_" + name).prop("checked") ? "0" : "1";
    if (coexist == "true") {
        var verinfo = version.replace(/\./, "");
        status = $("#index_" + name + verinfo).prop("checked") ? "0" : "1";
    }

    var data = "name=" + name + "&status=" + status + "&version=" + version;
    $.post("/plugins/set_index", data, function(rdata) {
        if (rdata.status) {
            layer.msg(rdata.msg, { icon: 1 })
        }
    },'json');
}

function indexListHtml(callback){
    var loadT = layer.msg('正在获取列表...', { icon: 16, time: 0, shade: [0.3, '#000'] });
    $.get('/plugins/index_list', function(rdata) {
        layer.close(loadT);
        $("#indexsoft").html('');
        var con = '';
        for (var i = 0; i < rdata.length; i++) {
            var plugin = rdata[i];
            var len = plugin.versions.length;
            var version_info = '';

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

            if (plugin.status == true) {
                    state = '<span style="color:#20a53a" class="glyphicon glyphicon-play"></span>'
                } else {
                    state = '<span style="color:red" class="glyphicon glyphicon-pause"></span>'
            }

            var name = plugin.title + ' ' + plugin.setup_version + '  ';
            var data_id = plugin.name + '-' + plugin.setup_version;
            if (plugin.coexist){
                name = plugin.title + '  ';
                data_id = plugin.name + '-' + plugin.versions;
            }
            

            con += '<div class="col-sm-3 col-md-3 col-lg-3" data-id="' + data_id + '">\
                <span class="spanmove"></span>\
                <div onclick="softMain(\'' + plugin.name + '\',\'' + version_info + '\')">\
                <div class="image"><img src="plugins/file?name=' + plugin.name + '&f=ico.png"></div>\
                <div class="sname">' +  name + state + '</div>\
                </div>\
            </div>';
        
        }

        $("#indexsoft").html(con);
        //软件位置移动
        var softboxlen = $("#indexsoft > div").length;
        var softboxsum = 12;
        var softboxcon = '';
        var softboxn = softboxlen;
        if (softboxlen <= softboxsum) {
            for (var i = 0; i < softboxsum - softboxlen; i++) {
                // softboxn += 1000;
                softboxcon += '<div class="col-sm-3 col-md-3 col-lg-3 no-bg" data-id="'  + '"></div>'
            }
            $("#indexsoft").append(softboxcon);
        }

        if (typeof callback=='function'){
            callback();
        }
    },'json');
}


//首页软件列表
function indexSoft() {
    indexListHtml(function(){
        $("#indexsoft").dragsort({ dragSelector: ".spanmove", dragBetween: true, dragEnd: saveOrder, placeHolderTemplate: "<div class='col-sm-3 col-md-3 col-lg-3 dashed-border'></div>" });
    });
    
    function saveOrder() {
        var data = $("#indexsoft > div").map(function() { return $(this).attr("data-id"); }).get();
        tmp = [];
        for(i in data){
            console.log(data[i]);
            if (data[i] != ''){
                tmp.push($.trim(data[i]));
            }
        }
        var ssort = tmp.join("|");
        $("input[name=list1SortOrder]").val(ssort);
        $.post("/plugins/index_sort", 'ssort=' + ssort, function(rdata) {
            if (!rdata.status){
                showMsg('设置失败:'+ rdata.msg, function(){
                    indexListHtml();
                }, { icon: 16, time: 0, shade: [0.3, '#000'] });
            }
        },'json');
    };
}

$(function() {
    if (window.document.location.pathname == '/soft/') {
        setInterval(function() { getSList(); }, 8000);
    }
});