
changeDivH();

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

    $('.glyphicon-resize-full').click(function(ele){
        const func = ele.requestFullscreen || ele.mozRequestFullScreen || ele.webkitRequestFullscreen || ele.msRequestFullscreen; 
        var e = $('#term_box_view').parent();
        func.call(e);
    });

    webShell_Menu();
});


function changeDivH(){
    var l = $(window).height();
    $('#term_box_view').parent().css('height',l-80);
}


function webShell_Menu() {
    var termCols = 83;
    var termRows = 21;
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

    // term.destroy();
    // clearInterval(interval);
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

function shell_to_baidu() {
    var selectText = getCookie('ssh_selection');
    remove_ssh_menu();
    window.open('https://www.baidu.com/s?wd=' + selectText)
    gterm.focus();
}

function shell_paste_text(){
    socket.emit('webssh', getCookie('ssh_selection'));
    remove_ssh_menu();
    gterm.focus();
}

function remove_ssh_menu() {
    $(".contextmenu").remove();
}