
//全局
var host_ssh_list = [];

//刷新页面
$(window).unload(function(){
    for (i in host_ssh_list) {
        host_ssh_list[i].close();
    }
    return false;
});

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
   var tag = $.getUrlParam('tag');
    if(tag == 'webssh'){
        webShell_Load();
    }
});

function webShell_Resize(){
    var cur_ssh = $('.term_item_tab .list .active');
    if (cur_ssh.length > 0){
        var data = $(cur_ssh).data();
        var item = host_ssh_list[data.id];
        item.term.fit();
        item.resize({ cols: item.term.cols, rows: item.term.rows});
        item.term.focus();
    }
}

function webShell_Load(){
    changeDivH();
    $(window).resize(function(){
        changeDivH();
        webShell_Resize();
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
        webShell_Resize();
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

    // 切换服务器终端视图
    $('.term_item_tab .list').on('click', 'span.item', function (ev) {
        var index = $(this).index();
        var data = $(this).data();
        if ($(this).hasClass('addServer')) {
        } else if ($(this).hasClass('tab_tootls')) {
        } else {
            $(this).addClass('active').siblings().removeClass('active');
            $('.term_content_tab .term_item:eq(' + index + ')').addClass('active').siblings().removeClass('active');
            webShell_Resize();
        }
    });

    $('.term_item_tab').on('click', '.icon-trem-close', function () {
        var id = $(this).parent().data('id');
        webShell_removeTermView(id);
    })

    //服务器列表和常用命令
    webShell_getHostList();

    //服务器列表和命令切换
    $('.term_tootls .tab-nav span').click(function(){
        var list_type = $(this).attr('data-type');
        if (!$(this).hasClass('on')){

            $('.term_tootls .tab-nav span').removeClass('on');
            $(this).addClass('on');

            $('.term_tootls .tab-con .tab-block').removeClass('on')
            if (list_type == 'host'){
                $('.term_tootls .tab-con .tab-block').eq(0).addClass('on');
                webShell_getHostList();
            }

            if (list_type == 'shell'){
                $('.term_tootls .tab-con .tab-block').eq(1).addClass('on');
                webShell_getCmdList();
            }
        }
    });

    webShell_Menu();
}


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
                    <span class="span_title">'+alist[i]['title']+'</span>\
                    <span class="tootls">\
                        <span class="glyphicon glyphicon-edit" aria-hidden="true" title="编辑常用命令信息"></span>\
                        <span class="glyphicon glyphicon-trash" aria-hidden="true" title="删除常用命令信息"></span>\
                    </span>\
                </li>';
        }
    
        $('.tootls_commonly_list').html(tli);

        $('.data-cmd-list .glyphicon-edit').click(function(){
            var index = $(this).parent().parent().attr('data-index');
            var t = alist[index];
            webShell_cmd(t['title'],t['cmd']);
        });

        $('.data-cmd-list .glyphicon-trash').click(function(){
            var index = $(this).parent().parent().attr('data-index');
            var t = alist[index];
            appPost('del_cmd', {title:t['title']}, function(rdata){
                var rdata = $.parseJSON(rdata.data);
                showMsg(rdata.msg, function(){
                    webShell_getCmdList();
                },{ icon: rdata.status ? 1 : 2 });
            });
        });

        $('.data-cmd-list .span_title').click(function(e){
            copyText($(this).parent().attr('data-clipboard-text'));
            e.preventDefault();
        });
    });
}

var n;
function Terms_WebSocketIO_Create(ip, random){
    n = new Terms_WebSocketIO('#'+random, { ssh_info: { host: ip, ps: "22", id: random } });
    n.registerCloseCallBack(function(){
        webShell_removeTermView(random);
        layer.msg('已经关闭【'+ip+'】', { icon: 1, time: 3000 });
    });

    n.registerConnectedCallBack(function(){
        var that = this;
        $('.term_item_tab .item').each(function(){
            var id = $(this).data('id');
            if (id == that.id){
                $(this).find('.icon').removeClass('icon-warning').addClass('icon-sucess');
            }
        });
        webShell_Resize();
    });

    n.registerExitCallBack(function(){
        var that = this;
        $('.term_item_tab .item').each(function(){
            var id = $(this).data('id');
            if (id == that.id){
                $(this).find('.icon').removeClass('icon-sucess').addClass('icon-warning');
            }
        });
    });
    return n;
}


function webShell_Menu(){
    var random = 'localhost';
    // host_ssh_list[random] = new Terms_WebSocketIO('#'+random, { ssh_info: { host: "38.6.224.67", ps: "22", id: random } });
    host_ssh_list[random] = Terms_WebSocketIO_Create('127.0.0.1',random);
}

function webShell_openTermView(info) {
    if (typeof info === "undefined") {
        info = { host: '127.0.0.1', ps: '本地服务器' }
    }
    var random = getRandomString(9);
    var tab_content = $('.term_content_tab');
    var item_list = $('.term_item_tab .list');
    tab_content.find('.term_item').removeClass('active').siblings().removeClass('active');
    tab_content.append('<div class="term_item active" id="' + random + '" data-host="' + info.host + '"></div>');
    item_list.find('.item').removeClass('active');
    if (info.ps == ''){
        info.ps = info.host;
    }
    item_list.append('<span class="active item ' + (info.host == '127.0.0.1' ? 'localhost_item' : '') + '" data-host="' + info.host + '" data-id="' + random + '"><i class="icon icon-sucess"></i><div class="content"><span>' + info.ps + '</span></div><span class="icon-trem-close"></span></span>');
    host_ssh_list[random] = Terms_WebSocketIO_Create(info.host, random);
}


function webShell_removeTermView(id){
    var item = $('[data-id="' + id + '"]');
    var next = item.next();
    var prev = item.prev();
    $('#' + id).remove();
    item.remove();
    try {
        host_ssh_list[id].close();
    } catch (error) {
        console.log(error);
    }

    delete host_ssh_list[id];
    if (item.hasClass('active')) {
        if (next.length > 0) {
            next.click();
        } else {
            prev.click();
        }
    }
}

function webShell_getHostList(info){
    appPost('get_server_list', {}, function(rdata){
        var rdata = $.parseJSON(rdata.data);
        var alist = rdata.data;

        var tli = '';
        for (var i = 0; i < alist.length; i++) {
            tli+='<li class="data-host-list" data-index="'+i+'" data-host="'+alist[i]['host']+'">\
                    <i></i>\
                    <span class="host">'+alist[i]['host']+'</span>\
                    <span class="tootls">\
                        <span class="glyphicon glyphicon-edit" aria-hidden="true" title="编辑常用命令信息"></span>\
                        <span class="glyphicon glyphicon-trash" aria-hidden="true" title="删除常用命令信息"></span>\
                    </span>\
                </li>';
        }
    
        $('.tootls_host_list').html(tli);

        $('.data-host-list .glyphicon-edit').click(function(e){
            var index = $(this).parent().parent().attr('data-index');
            var info = alist[index];
            webShell_addServer(info);
        });

        $('.data-host-list .glyphicon-trash').click(function(e){
            var index = $(this).parent().parent().attr('data-index');
            var t = alist[index];
            appPost('del_server', {host:t['host']}, function(rdata){
                var rdata = $.parseJSON(rdata.data);
                showMsg(rdata.msg, function(){
                    webShell_getHostList();
                },{ icon: rdata.status ? 1 : 2 });
            });
        });


        $('.tootls_host_list .host').on('click', function (e) {
            var _this = $(this).parent();
            var index = $(_this).index();
            var host = $(_this).data('host');
            $(_this).find('i').addClass('active');
            if ($('.item[data-host="' + host + '"]').length > 0) {
                layer.msg('已经打开!', { icon: 0, time: 3000 });
            } else {
                webShell_openTermView(alist[index]);
            }
            e.preventDefault();
        });
    });
}

function webShell_addServer(info=[]){
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
                        <div class="info-r">\
                            <div class="btn-group">\
                                <button type="button" tabindex="-1" class="btn btn-sm auth_type_checkbox btn-default btn-success" data-ctype="0">密码验证</button>\
                                <button type="button" tabindex="-1" class="btn btn-sm auth_type_checkbox btn-default" data-ctype="1">私钥验证\
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
                    <div class="line key_pwd_line hide" style="display:none;">\
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
            if (typeof(info['host'])!='undefined'){
                $('input[name="host"]').val(info['host']);
                appPost('get_server_by_host',{host:info['host']},function(rdata){
                    var rdata = $.parseJSON(rdata.data);
                    var jdata = rdata.data;
                    if (jdata['type'] == 0){
                        $('input[name="password"]').val(jdata['password']);
                    } else{
                        $('textarea[name="pkey"]').val(jdata['pkey']);
                        // $('input[name="pkey_passwd"]').val(jdata['pkey_passwd']);
                    }
                    $('input[name="ps"]').val(jdata['ps']);
                    $('input[name="port"]').val(jdata['port']);
                    $('.auth_type_checkbox').each(function(){
                        if ($(this).data('ctype') == jdata['type']){
                            $(this).addClass('btn-success');
                        } else {
                            $(this).removeClass('btn-success');
                        }
                    });
                    if (jdata['type'] == 0){
                        $('.c_password_view').removeClass('show').addClass('show');
                        $('.c_pkey_view').removeClass('show').addClass('hide');
                        // $('.key_pwd_line').removeClass('show').addClass('hide');

                    }else{
                        $('.c_password_view').removeClass('show').addClass('hide');
                        $('.c_pkey_view').removeClass('show').addClass('show');
                        // $('.key_pwd_line').removeClass('show').addClass('show');
                    }
                });
            }

            $('.auth_type_checkbox').click(function(){
                var ctype = $(this).attr('data-ctype');
                $('.auth_type_checkbox').removeClass('btn-success');
                $(this).addClass('btn-success');

                if (ctype == 0){
                    $('.c_password_view').removeClass('show').addClass('show');
                    $('.c_pkey_view').removeClass('show').addClass('hide');
                    // $('.key_pwd_line').removeClass('show').addClass('hide');

                }else{
                    $('.c_password_view').removeClass('show').addClass('hide');
                    $('.c_pkey_view').removeClass('show').addClass('show');
                    // $('.key_pwd_line').removeClass('show').addClass('show');
                }
            });
        },
        yes:function(l,layeror){
            var host = $('input[name="host"]').val();
            var port = $('input[name="port"]').val();
            var username = $('input[name="username"]').val();
            var password = '';
            var pkey = '';
            var pkey_passwd = '';
            var type = $('.btn-group .btn-success').attr('data-ctype');
            if (type == "0"){
                password = $('input[name="password"]').val();
            } else{
                pkey = $('textarea[name="pkey"]').val();
                pkey_passwd = $('input[name="pkey_passwd"]').val();
            }
            
            var ps = $('input[name="ps"]').val();

            var req_data = {
                type:type,
                host:host,
                port:port,
                username:username,
                password:password,
                pkey:pkey,
                pkey_passwd:pkey_passwd,
                ps:ps,
            };

            console.log(req_data);

            appPost('add_server',req_data,function(rdata){
                layer.close(l);
                var rdata = $.parseJSON(rdata.data);
                showMsg(rdata.msg, function(){
                    webShell_getHostList();
                },{ icon: rdata.status ? 1 : 2 });
            });
        },
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

