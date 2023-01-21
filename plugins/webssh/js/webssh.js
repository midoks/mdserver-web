
function appPost(method,args,callback){
    var _args = null; 
    if (typeof(args) == 'string'){
        _args = JSON.stringify(toArrayObject(args));
    } else {
        _args = JSON.stringify(args);
    }

    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });
    $.post('/plugins/run', {name:'webssh', func:method, args:_args}, function(data) {
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

function appAsyncPost(method,args){
    var _args = null; 
    if (typeof(args) == 'string'){
        _args = JSON.stringify(toArrayObject(args));
    } else {
        _args = JSON.stringify(args);
    }
    return syncPost('/plugins/run', {name:'webssh', func:method, args:_args}); 
}

function appPostCallbak(method, args, callback){
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });

    var req_data = {};
    req_data['name'] = 'webssh';
    req_data['func'] = method;
    args['version'] = '1.0';
 
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

$(document).ready(function(){
    changeDivH();
    $(window).resize(function(){
        changeDivH();
    });

    $('.term_content_tab .term-tool-button').click(function(){
        if ($(this).hasClass('tool-show')){
            $('#term_box_view').css('margin-right',300);
            $('.term_tootls').css('display',"block");
            $(this).removeClass('tool-show').addClass('tool-hide');
            $(this).find('span').removeClass('glyphicon-menu-left').addClass('glyphicon-menu-right');
        } else {
            $('#term_box_view').css('margin-right',0);
            $('.term_tootls').css('display',"none");
            $(this).removeClass('tool-hide').addClass('tool-show');
            $(this).find('span').removeClass('glyphicon-menu-right').addClass('glyphicon-menu-left');
        }
    });

    $('.full_exit_screen').click(function(ele){
        if($(this).hasClass('glyphicon-resize-full')){
            requestFullScreen($('#term_box_view')[0]);
            $(this).removeClass('glyphicon-resize-full').addClass('glyphicon-resize-small');
        } else{
            exitFull();
            $(this).removeClass('glyphicon-resize-small').addClass('glyphicon-resize-full');
        }
    });

    $('.addServer').click(function(){
        webShell_addServer();
    });

    $('.tootls_host_btn').click(function(){
        webShell_addServer();
    });

    $('.tootls_commonly_btn').click(function(){
        webShell_cmd();
    });

    //服务器列表和常用命令
    $('.term_tootls .tab-nav span').click(function(){
        var list_type = $(this).attr('data-type');
        if (!$(this).hasClass('on')){

            $('.term_tootls .tab-nav span').removeClass('on');
            $(this).addClass('on');

            $('.term_tootls .tab-con .tab-block').removeClass('on')
            if (list_type == 'host'){
                $('.term_tootls .tab-con .tab-block').eq(0).addClass('on');
            }

            if (list_type == 'shell'){
                $('.term_tootls .tab-con .tab-block').eq(1).addClass('on');
                webShell_getCmdList();
            }
        }
    });

    webShell_Menu();
});


function changeDivH(){
    var l = $(window).height();
    $('#term_box_view').parent().css('height',l-80);

    $('#xterm-viewport').css('height',l-80);


    $('.tootls_host_list').css('display','block').css('height',l-192);
    $('.tootls_commonly_list').css('display','block').css('height',l-192);
    
}


// 窗口状态改变
function fullScreenChange(el, callback) {
    el.addEventListener("fullscreenchange", function () { 
        callback && callback(document.fullscreen);
    }); 

    el.addEventListener("webkitfullscreenchange", function () { 
        callback && callback(document.webkitIsFullScreen);
    }); 

    el.addEventListener("mozfullscreenchange", function () { 
        callback && callback(document.mozFullScreen);
    });

    el.addEventListener("msfullscreenchange", function () { 
        callback && callback(document.msFullscreenElement);
    });
}

// 全屏
function requestFullScreen(element) {
    var requestMethod = element.requestFullScreen || //W3C
    element.webkitRequestFullScreen ||    //Chrome等
    element.mozRequestFullScreen || //FireFox
    element.msRequestFullScreen; //IE11
    if (requestMethod) {
        requestMethod.call(element);
    }else if (typeof window.ActiveXObject !== "undefined") {//for Internet Explorer
        var wscript = new ActiveXObject("WScript.Shell");
        if (wscript !== null) {
            wscript.SendKeys("{F11}");
        }
    }
}

//退出全屏
function exitFull() {
    var exitMethod = document.exitFullscreen || //W3C
    document.mozCancelFullScreen ||    //Chrome等
    document.webkitExitFullscreen || //FireFox
    document.webkitExitFullscreen; //IE11
    if (exitMethod) {
        exitMethod.call(document);
    }else if (typeof window.ActiveXObject !== "undefined") {//for Internet Explorer
        var wscript = new ActiveXObject("WScript.Shell");
        if (wscript !== null) {
            wscript.SendKeys("{F11}");
        }
    }
}


function webShell_getCmdList(){
    appPost('get_cmd_list', {}, function(rdata){
        var rdata = $.parseJSON(rdata.data);
        var alist = rdata.data;

        var tli = '';
        for (var i = 0; i < alist.length; i++) {
            tli+='<li class="data-cmd-list" data-index="'+i+'" data-clipboard-text="'+alist[i]['cmd']+'">\
                    <i></i>\
                    <span>'+alist[i]['title']+'</span>\
                    <span class="tootls">\
                        <span class="glyphicon glyphicon-edit" aria-hidden="true" title="编辑常用命令信息"></span>\
                        <span class="glyphicon glyphicon-trash" aria-hidden="true" title="删除常用命令信息"></span>\
                    </span>\
                </li>';
        }
    
        $('.tootls_commonly_list').html(tli);

        $('.glyphicon-edit').click(function(){
            var index = $(this).parent().parent().attr('data-index');
            var t = alist[index];
            webShell_cmd(t['title'],t['cmd']);
        });

        $('.glyphicon-trash').click(function(){
            var index = $(this).parent().parent().attr('data-index');
            var t = alist[index];
            appPost('del_cmd', {title:t['title']}, function(rdata){
                var rdata = $.parseJSON(rdata.data);
                showMsg(rdata.msg, function(){
                    webShell_getCmdList();
                },{ icon: rdata.status ? 1 : 2 });
            });
        });

        $('.data-cmd-list').click(function(){
            copyText($(this).attr('data-clipboard-text'));
        });
    });
}


function webShell_Menu() {
    var termCols = 83;
    var termRows = 20;
    var sendTotal = 0;
    if(!socket)socket = io.connect();
    var term = new Terminal({ cols: termCols, rows: termRows, screenKeys: true, useStyle: true});

    term.open();
    term.setOption('cursorBlink', true);
    term.setOption('fontSize', 14);
    gterm = term

    socket.on('server_response', function (data) {
        term.write(data.data);
        if (data.data == '\r\n登出\r\n' || 
            data.data == '登出\r\n' || 
            data.data == '\r\nlogout\r\n' || 
            data.data == 'logout\r\n') {
            setTimeout(function () {
                layer.closeAll();
                term.destroy();
                clearInterval(interval);
            }, 500);
        }
    });

    $(window).unload(function(){
  　     term.destroy();
        clearInterval(interval);
    });

    if (socket) {
        socket.emit('connect_event', '');
        interval = setInterval(function () {
            socket.emit('connect_event', '');
        }, 1000);
    }
    
    term.on('data', function (data) {
        socket.emit('webssh', data);
    });

	$(".shell_btn_close").click(function(){
		layer.close(term_box);
		term.destroy();
        clearInterval(interval);
	})
	
    setTimeout(function () {
        $('.terminal').detach().appendTo('#ECFEfRWM8');
        $("#ECFEfRWM8").show();
        socket.emit('webssh', "\n");
        term.focus();

        // 鼠标右键事件
        var can = $("#term");
        can.contextmenu(function (e) {
            var winWidth = can.width();
            var winHeight = can.height();
            var mouseX = e.pageX;
            var mouseY = e.pageY;
            var menuWidth = $(".contextmenu").width();
            var menuHeight = $(".contextmenu").height();
            var minEdgeMargin = 10;
            if (mouseX + menuWidth + minEdgeMargin >= winWidth &&
                mouseY + menuHeight + minEdgeMargin >= winHeight) {
                menuLeft = mouseX - menuWidth - minEdgeMargin + "px";
                menuTop = mouseY - menuHeight - minEdgeMargin + "px";
            }
            else if (mouseX + menuWidth + minEdgeMargin >= winWidth) {
                menuLeft = mouseX - menuWidth - minEdgeMargin + "px";
                menuTop = mouseY + minEdgeMargin + "px";
            }
            else if (mouseY + menuHeight + minEdgeMargin >= winHeight) {
                menuLeft = mouseX + minEdgeMargin + "px";
                menuTop = mouseY - menuHeight - minEdgeMargin + "px";
            }
            else {
                menuLeft = mouseX + minEdgeMargin + "px";
                menuTop = mouseY + minEdgeMargin + "px";
            };

            var selectText = term.getSelection()
            var style_str = '';
            var paste_str = '';
            if (!selectText) {
                if (!getCookie('shell_copy_body')) {
                    paste_str = 'style="color: #bbb;" disable';
                }
                style_str = 'style="color: #bbb;" disable';
            } else {
                setCookie('ssh_selection', selectText);
            }


            var menudiv = '<ul class="contextmenu">\
                        <li><a class="shell_copy_btn menu_ssh" data-clipboard-text="'+ selectText + '" ' + style_str + '>复制到剪切板</a></li>\
                        <li><a  onclick="shell_paste_text()" '+ paste_str+'>粘贴选中项</a></li>\
                        <li><a onclick="shell_to_baidu()" ' + style_str + '>百度搜索</a></li>\
                    </ul>';
            $("body").append(menudiv);
            $(".contextmenu").css({
                "left": menuLeft,
                "top": menuTop
            });
            return false;
        });
        can.click(function () {
            remove_ssh_menu();
        });

        clipboard = new ClipboardJS('.shell_copy_btn');
        clipboard.on('success', function (e) {
            layer.msg('复制成功!');
            setCookie('shell_copy_body', e.text)
            remove_ssh_menu();
            term.focus();
        });

        clipboard.on('error', function (e) {
            layer.msg('复制失败，浏览器不兼容!');
            setCookie('shell_copy_body', e.text)
            remove_ssh_menu();
            term.focus();
        });

        $(".shellbutton").click(function () {
            var tobj = $("textarea[name='ssh_copy']");
            var ptext = tobj.val();
            tobj.val('');
            if ($(this).text().indexOf('Alt') != -1) {
                ptext +="\n";
            }
            socket.emit('webssh', ptext);
            term.focus();
        })
        $("textarea[name='ssh_copy']").keydown(function (e) {

            if (e.ctrlKey && e.keyCode == 13) {
                $(".shell_btn_1").click();
            } else if (e.altKey && e.keyCode == 13) {
                $(".shell_btn_1").click();
            }
        });

    }, 100);
}

function webShell_addServer(){
    layer.open({
        type: 1,
        title: '添加主机信息',
        area: '500px',
        btn:["确定","取消"],
        content:'<div class="bt-form pd20 c6">\
                    <div class="line input_group">\
                        <span class="tname">服务器IP</span>\
                        <div class="info-r">\
                            <input type="text" name="host" class="bt-input-text mr5" style="width:240px" value="127.0.0.1" placeholder="输入服务器IP" val="" autocomplete="off" />\
                            <input type="text" name="port" class="bt-input-text mr5" style="width:60px" placeholder="端口" value="22" autocomplete="off"/>\
                        </div>\
                    </div>\
                    <div class="line">\
                        <span class="tname">SSH账号</span>\
                        <div class="info-r">\
                            <input type="text" name="username" class="bt-input-text mr5" style="width:305px" placeholder="输入SSH账号" value="root" autocomplete="off"/>\
                        </div>\
                    </div>\
                    <div class="line">\
                        <span class="tname">验证方式</span>\
                        <div class="info-r ">\
                            <div class="btn-group">\
                                <button type="button" tabindex="-1" class="btn btn-sm auth_type_checkbox  btn-success" data-ctype="0">密码验证</button>\
                                <button type="button" tabindex="-1" class="btn btn-sm auth_type_checkbox  btn-default" data-ctype="1">私钥验证\
                                </button>\
                            </div>\
                        </div>\
                    </div>\
                    <div class="line c_password_view show">\
                        <span class="tname">密码</span>\
                        <div class="info-r">\
                            <input type="text" name="password" class="bt-input-text mr5" placeholder="请输入SSH密码" style="width:305px;" value="" autocomplete="off"/>\
                        </div>\
                    </div>\
                    <div class="line c_pkey_view hide">\
                        <span class="tname">私钥</span>\
                        <div class="info-r">\
                            <textarea rows="4" name="pkey" class="bt-input-text mr5" placeholder="请输入SSH私钥" style="width:305px;height: 80px;line-height: 18px;padding-top:10px;"></textarea>\
                        </div>\
                    </div>\
                    <div class="line key_pwd_line hide">\
                        <span class="tname">私钥密码</span>\
                        <div class="info-r">\
                            <input type="text" name="pkey_passwd" class="bt-input-text mr5" placeholder="请输入私钥密码" style="width:305px;" value="" autocomplete="off"/>\
                        </div>\
                    </div>\
                    <div class="line ssh_ps_tips">\
                        <span class="tname">备注</span>\
                        <div class="info-r">\
                            <input type="text" name="ps" class="bt-input-text mr5" placeholder="请输入备注,可为空" style="width:305px;" value="" autocomplete="off"/>\
                        </div>\
                    </div>\
                </div>',
        success:function(){
        }
    });
}

function webShell_cmd(title='', cmd=''){
    layer.open({
        type: 1,
        title: '添加常用命令信息',
        area: '500px',
        btn:["确定","取消"],
        content:'<div class="bt-form pd20 c6">\
                    <div class="line">\
                        <span class="tname">命令名称</span>\
                        <div class="info-r">\
                            <input type="text" name="title" class="bt-input-text mr5" style="width:305px" placeholder="请输入常用命令描述，必填项" value="'+title+'" autocomplete="off"/>\
                        </div>\
                    </div>\
                    <div class="line">\
                        <span class="tname">命令内容</span>\
                        <div class="info-r">\
                            <textarea rows="4" name="cmd" class="bt-input-text mr5" placeholder="请输入常用命令信息，必填项" style="width:305px;height: 150px;line-height: 18px;padding-top:10px;">'+cmd+'</textarea>\
                        </div>\
                    </div>\
                </div>',
        success:function(){
        },
        yes:function(l,layer_id){
            var title = $('input[name="title"]').val();
            var cmd = $('textarea[name="cmd"]').val();

            appPost('add_cmd', {title:title,cmd:cmd}, function(rdata){
                layer.close(l);
                var rdata = $.parseJSON(rdata.data);
                showMsg(rdata.msg, function(){
                    webShell_getCmdList();
                },{ icon: rdata.status ? 1 : 2 });
            });
            return false;
        }
    });   
}

