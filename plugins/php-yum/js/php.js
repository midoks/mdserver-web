function phpPost(method, version, args,callback){
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });

    var req_data = {};
    req_data['name'] = 'php-yum';
    req_data['func'] = method;
    req_data['version'] = version;
 
    if (typeof(args) == 'string'){
        req_data['args'] = JSON.stringify(toArrayObject(args));
    } else {
        req_data['args'] = JSON.stringify(args);
    }

    $.post('/plugins/run', req_data, function(data) {
        layer.close(loadT);
        if (!data.status){
            //错误展示10S
            layer.msg(data.msg,{icon:0,time:2000,shade: [10, '#000']});
            return;
        }

        if(typeof(callback) == 'function'){
            callback(data);
        }
    },'json'); 
}

function phpPostCallbak(method, version, args,callback){
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });

    var req_data = {};
    req_data['name'] = 'php-yum';
    req_data['func'] = method;
    args['version'] = version;
 
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


//配置修改
function phpSetConfig(version) {
    phpPost('get_php_conf', version,'',function(data){
        // console.log(data);
        var rdata = $.parseJSON(data.data);
        // console.log(rdata);
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
                        <div style="margin-top:10px; padding-right:15px" class="text-right"><button class="btn btn-success btn-sm mr5" onclick="phpSetConfig(' + version + ')">刷新</button><button class="btn btn-success btn-sm" onclick="submitConf(' + version + ')">保存</button></div>\
                    </div>'
        $(".soft-man-con").html(phpCon);
    });
}


//提交PHP配置
function submitConf(version) {
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
        max_input_vars: $("input[name='max_input_vars']").val(),
        memory_limit: $("input[name='memory_limit']").val(),
        post_max_size: $("input[name='post_max_size']").val(),
        file_uploads: $("select[name='file_uploads']").val(),
        upload_max_filesize: $("input[name='upload_max_filesize']").val(),
        max_file_uploads: $("input[name='max_file_uploads']").val(),
        default_socket_timeout: $("input[name='default_socket_timeout']").val(),
        error_reporting: $("input[name='error_reporting']").val() || 'On'
    };

    phpPost('submit_php_conf', version, data, function(ret_data){
        var rdata = $.parseJSON(ret_data.data);
        // console.log(rdata);
        layer.msg(rdata.msg, { icon: rdata.status ? 1 : 2 });
    });
}



//php超时限制
function phpCommonFunc(version){
    phpPost('get_limit_conf', version, '', function(ret_data){
        var rdata = $.parseJSON(ret_data.data);
        var con = '<p class="conf_p">\
            <span>超时限制</span>\
            <input class="phpTimeLimit bt-input-text mr5" type="number" value="' + rdata['maxTime'] + '">, 秒\
            <button class="btn btn-success btn-sm" onclick="setPHPMaxTime(\'' + version + '\')" style="margin-left:20px">保存</button>\
            </p>';

        con += '<p class="conf_p">\
            <span>上传限制</span>\
            <input class="phpUploadLimit bt-input-text mr5" type="number" value="' + rdata['max']+'" name="max">,MB\
            <button class="btn btn-success btn-sm" onclick="setPHPMaxSize(\''+ version+'\')" style="margin-left:20px">保存</button>\
        </p>';

        con += '<hr/><p class="conf_p" style="text-align:center;">\
            <button class="btn btn-default btn-sm" onclick="getPHPInfo(\'' + version + '\')">查看phpinfo()</button>\
            <button class="btn btn-default btn-sm" onclick="phpPreload(\'' + version + '\')">预加载脚本</button>\
            <button class="btn btn-default btn-sm" onclick="phpOpcacheBlacklist(\'' + version + '\')">OPCACHE黑名单</button>\
            <button class="btn btn-default btn-sm" onclick="phpFpmRoot(\'' + version + '\')">PHP-FPM(global)</button>\
        </p>';

        $(".soft-man-con").html(con);
    });
}

//设置超时限制
function setPHPMaxTime(version) {
    var max = $(".phpTimeLimit").val();
    phpPost('set_max_time',version,{'time':max},function(data){
        var rdata = $.parseJSON(data.data);
        showMsg(rdata.msg,function(){
            phpCommonFunc(version);
        },{ icon: rdata.status ? 1 : 2 });

    });
}
//设置PHP上传限制
function setPHPMaxSize(version) {
    max = $(".phpUploadLimit").val();
    if (max < 2) {
        alert(max);
        layer.msg('上传大小限制不能小于2M', { icon: 2 });
        return;
    }

    phpPost('set_max_size',version,{'max':max},function(data){
        var rdata = $.parseJSON(data.data);
        layer.msg(rdata.msg, { icon: rdata.status ? 1 : 2 });
    });
}

function phpPreload(version){
    phpPost('app_start',version,{},function(data){
        onlineEditFile(0, data['data']);
    });
}

function phpOpcacheBlacklist(version){
    phpPost('opcache_blacklist_file',version,{},function(data){
        onlineEditFile(0, data['data']);
    });
}

function phpFpmRoot(version){
    phpPost('get_fpm_file',version,{},function(data){
        onlineEditFile(0, data['data']);
    });
}


function getFpmConfig(version){
    phpPost('get_fpm_conf', version, {}, function(data){
        // console.log(data);
        var rdata = $.parseJSON(data.data);
        // console.log(rdata);
        var limitList = "<option value='0'>自定义</option>" +
            "<option value='1' " + (rdata.max_children == 30 ? 'selected' : '') + ">30并发</option>" +
            "<option value='2' " + (rdata.max_children == 50 ? 'selected' : '') + ">50并发</option>" +
            "<option value='3' " + (rdata.max_children == 100 ? 'selected' : '') + ">100并发</option>" +
            "<option value='4' " + (rdata.max_children == 200 ? 'selected' : '') + ">200并发</option>" +
            "<option value='5' " + (rdata.max_children == 300 ? 'selected' : '') + ">300并发</option>" +
            "<option value='6' " + (rdata.max_children == 500 ? 'selected' : '') + ">500并发</option>" +
            "<option value='6' " + (rdata.max_children == 2000 ? 'selected' : '') + ">2000并发</option>";
        var pms = [{ 'name': 'static', 'title': '静态' }, { 'name': 'dynamic', 'title': '动态' },{ 'name': 'ondemand', 'title': '按需' }];
        var pmList = '';
        for (var i = 0; i < pms.length; i++) {
            pmList += '<option value="' + pms[i].name + '" ' + ((pms[i].name == rdata.pm) ? 'selected' : '') + '>' + pms[i].title + '</option>';
        }
        var body = "<div class='bingfa'>" +
            "<p class='line'><span class='span_tit'>并发方案：</span><select class='bt-input-text' name='limit' style='width:100px;'>" + limitList + "</select></p>" +
            "<p class='line'><span class='span_tit'>运行模式：</span><select class='bt-input-text' name='pm' style='width:100px;'>" + pmList + "</select><span class='c9'>*PHP-FPM运行模式</span></p>" +
            "<p class='line'><span class='span_tit'>max_children：</span><input class='bt-input-text' type='number' name='max_children' value='" + rdata.max_children + "' /><span class='c9'>*允许创建的最大子进程数</span></p>" +
            "<p class='line'><span class='span_tit'>start_servers：</span><input class='bt-input-text' type='number' name='start_servers' value='" + rdata.start_servers + "' />  <span class='c9'>*起始进程数（服务启动后初始进程数量）</span></p>" +
            "<p class='line'><span class='span_tit'>min_spare_servers：</span><input class='bt-input-text' type='number' name='min_spare_servers' value='" + rdata.min_spare_servers + "' />   <span class='c9'>*最小空闲进程数（清理空闲进程后的保留数量）</span></p>" +
            "<p class='line'><span class='span_tit'>max_spare_servers：</span><input class='bt-input-text' type='number' name='max_spare_servers' value='" + rdata.max_spare_servers + "' />   <span class='c9'>*最大空闲进程数（当空闲进程达到此值时清理）</span></p>" +
            "<div class='mtb15'><button class='btn btn-success btn-sm' onclick='setFpmConfig(\"" + version + "\",1)'>保存</button></div>" +
            "</div>";

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
                case '7':
                    max_children = 2000;
                    start_servers = 40;
                    min_spare_servers = 40;
                    max_spare_servers = 255;
                    break;
            }

            $("input[name='max_children']").val(max_children);
            $("input[name='start_servers']").val(start_servers);
            $("input[name='min_spare_servers']").val(min_spare_servers);
            $("input[name='max_spare_servers']").val(max_spare_servers);
        });
    });
}

function setFpmConfig(version){
    var max_children = Number($("input[name='max_children']").val());
    var start_servers = Number($("input[name='start_servers']").val());
    var min_spare_servers = Number($("input[name='min_spare_servers']").val());
    var max_spare_servers = Number($("input[name='max_spare_servers']").val());
    var pm = $("select[name='pm']").val();

    if (max_children < max_spare_servers) {
        layer.msg('max_spare_servers 不能大于 max_children', { icon: 2 });
        return;
    }

    if (min_spare_servers > start_servers) {
        layer.msg('min_spare_servers 不能大于 start_servers', { icon: 2 });
        return;
    }

    if (max_spare_servers < min_spare_servers) {
        layer.msg('min_spare_servers 不能大于 max_spare_servers', { icon: 2 });
        return;
    }

    if (max_children < start_servers) {
        layer.msg('start_servers 不能大于 max_children', { icon: 2 });
        return;
    }

    if (max_children < 1 || start_servers < 1 || min_spare_servers < 1 || max_spare_servers < 1) {
        layer.msg('配置值不能小于1', { icon: 2 });
        return;
    }

    var data = {
        version:version,
        max_children:max_children,
        start_servers:start_servers,
        min_spare_servers:min_spare_servers,
        max_spare_servers:max_spare_servers,
        pm:pm,
    };
    phpPost('set_fpm_conf', version, data, function(ret_data){
        var rdata = $.parseJSON(ret_data.data);
        layer.msg(rdata.msg, { icon: rdata.status ? 1 : 2 });
    });
}


function getFpmStatus(version){
    phpPost('get_fpm_status', version, '', function(ret_data){
        var tmp_data = $.parseJSON(ret_data.data);
        if(!tmp_data.status){
            layer.msg(tmp_data.msg, { icon: tmp_data.status ? 1 : 2 });
            return;
        }

        var rdata = tmp_data.data;
        var php_fpm_status = '动态';
        if (rdata['process manager'] == 'dynamic'){
            php_fpm_status = '动态';
        } else if(rdata['process manager'] == 'static'){
            php_fpm_status = '静态';
        } else if(rdata['process manager'] == 'ondemand'){
            php_fpm_status = '按需';
        }
        
        var con = "<div style='height:420px;overflow:hidden;'><table class='table table-hover table-bordered GetPHPStatus' style='margin:0;padding:0'>\
                        <tr><th>应用池(pool)</th><td>" + rdata.pool + "</td></tr>\
                        <tr><th>进程管理方式(process manager)</th><td>" + php_fpm_status + "</td></tr>\
                        <tr><th>启动日期(start time)</th><td>" + rdata['start time'] + "</td></tr>\
                        <tr><th>请求数(accepted conn)</th><td>" + rdata['accepted conn'] + "</td></tr>\
                        <tr><th>请求队列(listen queue)</th><td>" + rdata['listen queue'] + "</td></tr>\
                        <tr><th>最大等待队列(max listen queue)</th><td>" + rdata['max listen queue'] + "</td></tr>\
                        <tr><th>socket队列长度(listen queue len)</th><td>" + rdata['listen queue len'] + "</td></tr>\
                        <tr><th>空闲进程数量(idle processes)</th><td>" + rdata['idle processes'] + "</td></tr>\
                        <tr><th>活跃进程数量(active processes)</th><td>" + rdata['active processes'] + "</td></tr>\
                        <tr><th>总进程数量(total processes)</th><td>" + rdata['total processes'] + "</td></tr>\
                        <tr><th>最大活跃进程数量(max active processes)</th><td>" + rdata['max active processes'] + "</td></tr>\
                        <tr><th>到达进程上限次数(max children reached)</th><td>" + rdata['max children reached'] + "</td></tr>\
                        <tr><th>慢请求数量(slow requests)</th><td>" + rdata['slow requests'] + "</td></tr>\
                     </table></div>";
        $(".soft-man-con").html(con);
        $(".GetPHPStatus td,.GetPHPStatus th").css("padding", "7px");
    });
}

function getSessionConfig(version){
    phpPost('get_session_conf', version, '', function(ret_data){
        var rdata = $.parseJSON(ret_data.data);
        if(!rdata.status){
            layer.msg(rdata.msg, { icon: rdata.status ? 1 : 2 });
            return;
        }
        var rdata = rdata.data;

         var cacheList = "<option value='files' " + (rdata.save_handler == "files" ? 'selected' : '') + ">files</option>" +
            "<option value='redis' " + (rdata.save_handler == "redis" ? 'selected' : '') + ">redis</option>" +
            "<option value='memcache' " + (rdata.save_handler == "memcache" ? 'selected' : '') + ">memcache</option>" +
            "<option value='memcached' " + (rdata.save_handler == "memcached" ? 'selected' : '') + ">memcached</option>";


        var info = rdata.save_path.split(":");
        var con = "<div class='conf_p'>" +
            "<p class='line'><span class='span_tit'>存储模式：</span><select class='bt-input-text' name='save_handler' style='width:200px;'>" + cacheList + "</select></p>" +
            "<p class='line'><span class='span_tit'>IP地址：</span><input class='bt-input-text' type='text' name='ip' style='width:200px;' value='"+ info[0] +"' /></p>" +
            "<p class='line'><span class='span_tit'>端口：</span><input class='bt-input-text' type='text' name='port' style='width:200px;' value='"+rdata.port+"' /></p>" +
            "<p class='line'><span class='span_tit'>密码：</span><input class='bt-input-text' type='text' name='passwd' style='width:200px;' value='"+rdata.passwd+"' /></p>" +
            "<p class='line'><div class='mtb15' style='margin-left:100px;'><button class='btn btn-success btn-sm' onclick='setSessionConfig(\"" + version + "\",1)'>保存</button></div></p>" +
            "</div>\
            <ul class='help-info-text c7'>\
                <li>若你的站点并发比较高，使用Redis，Memcache能有效提升PHP并发能力</li>\
                <li>若调整Session模式后，网站访问异常，请切换回原来的模式</li>\
                <li>切换Session模式会使在线的用户会话丢失，请在流量小的时候切换</li>\
            </ul>\
            <div id='session_clear' class='session_clear' style='border-top: #ccc 1px dashed;padding-top: 15px;margin-top: 15px;'>\
            </div>\
            </div>";

        $(".soft-man-con").html(con);

        if (rdata.save_handler == 'files'){
            $('input[name="ip"]').attr('disabled','disabled');
            $('input[name="port"]').attr('disabled','disabled');
            $('input[name="passwd"]').attr('placeholder','如果没有密码留空');
            $('input[name="passwd"]').attr('disabled','disabled');
        }

        // change event
        $("select[name='save_handler']").change(function() {
            var type = $(this).val();

            var passwd = $('input[name="passwd"]').val();
            if (passwd == ""){
                $('input[name="passwd"]').attr('placeholder','如果没有密码留空');
            }

            var ip = $('input[name="ip"]').val();
            if (ip == ""){
                $('input[name="ip"]').val('127.0.0.1');
            }

            switch (type) {
                case 'redis':
                    var port = $('input[name="port"]').val();
                    if (port == ""){
                        $('input[name="port"]').val('6379');
                    }
                    $('input[name="ip"]').removeAttr('disabled');
                    $('input[name="port"]').removeAttr('disabled');
                    $('input[name="passwd"]').removeAttr('disabled');
                    break;
                case 'files':
                    $('input[name="ip"]').val("").attr('disabled','disabled');
                    $('input[name="port"]').val("").attr('disabled','disabled');
                    $('input[name="passwd"]').val("").attr('disabled','disabled');
                    break;
                case 'memcache':
                    var port = $('input[name="port"]').val();
                    if (port == ""){
                        $('input[name="port"]').val('11211');
                    }
                    $('input[name="ip"]').removeAttr('disabled');
                    $('input[name="port"]').removeAttr('disabled');
                    $('input[name="passwd"]').removeAttr('disabled');
                    break;
                case 'memcached':
                    var port = $('input[name="port"]').val();
                    if (port == ""){
                        $('input[name="port"]').val('11211');
                    }
                    $('input[name="ip"]').removeAttr('disabled');
                    $('input[name="port"]').removeAttr('disabled');
                    $('input[name="passwd"]').removeAttr('disabled');
                    break;
            }
        });

        //load session stats
        phpPost('get_session_count', version, '', function(ret_data){
            var rdata = $.parseJSON(ret_data.data);
            if(!rdata.status){
                layer.msg(rdata.msg, { icon: rdata.status ? 1 : 2 });
                return;
            }
            var rdata = rdata.data;

            var html_var = "<div class='clear_title' style='padding-bottom:15px;'>清理Session文件</div>\
                <div class='clear_conter'>\
                    <div class='session_clear_list'>\
                        <div class='line'><span>总Session文件数量</span><span>"+rdata.total+"</span></div>\
                        <div class='line'><span>可清理的Session文件数量</span><span>"+rdata.oldfile+"</span></div>\
                    </div>\
                <button id='clean_func' class='btn btn-success btn-sm clear_session_file'>清理session文件</button>";

            $("#session_clear").html(html_var);


            $('#clean_func').click(function(){
                phpPost('clean_session_old', version, '', function(ret_data){
                    var rdata = $.parseJSON(ret_data.data);
                    showMsg(rdata.msg,function(){
                        getSessionConfig(version);
                    },{ icon: rdata.status ? 1 : 2 });
                });
            });
        });
    });

}

function setSessionConfig(version){
    var ip = $('input[name="ip"]').val();
    var port = $('input[name="port"]').val();
    var passwd = $('input[name="passwd"]').val();
    var save_handler = $("select[name='save_handler']").val();
    var data = {
        ip:ip,
        port:port,
        passwd:passwd,
        save_handler:save_handler,
    };
    phpPost('set_session_conf', version, data, function(ret_data){
        var rdata = $.parseJSON(ret_data.data);
        layer.msg(rdata.msg, { icon: rdata.status ? 1 : 2 });
    });
}

//禁用函数
function disableFunc(version) {
    phpPost('get_disable_func', version,'',function(data){
        var rdata = $.parseJSON(data.data);
        var disable_functions = rdata.disable_functions.split(',');
        var dbody = ''
        for (var i = 0; i < disable_functions.length; i++) {
            if (disable_functions[i] == '') continue;
            dbody += "<tr><td>" + disable_functions[i] + "</td><td><a style='float:right;' href=\"javascript:setDisableFunc('" + version + "','" + disable_functions[i] + "','" + rdata.disable_functions + "');\">删除</a></td></tr>";
        }

        var con = "<div class='dirBinding'>" +
            "<input class='bt-input-text mr5' type='text' placeholder='添加要被禁止的函数名,如: exec' id='disable_function_val' style='height: 28px; border-radius: 3px;width: 410px;' />" +
            "<button class='btn btn-success btn-sm' onclick=\"setDisableFunc('" + version + "',1,'" + rdata.disable_functions + "')\">添加</button>" +
            "</div>" +
            "<div class='divtable mtb15' style='height:350px;overflow:auto'><table class='table table-hover' width='100%' style='margin-bottom:0'>" +
            "<thead><tr><th>名称</th><th width='100' class='text-right'>操作</th></tr></thead>" +
            "<tbody id='blacktable'>" + dbody + "</tbody>" +
            "</table></div>";

        con += '<ul class="help-info-text">\
                    <li>在此处可以禁用指定函数的调用,以增强环境安全性!</li>\
                    <li>强烈建议禁用如exec,system等危险函数!</li>\
                </ul>';

        $(".soft-man-con").html(con);
    });
}
//设置禁用函数
function setDisableFunc(version, act, fs) {
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
        msg = '添加成功';
    } else {

        fs = '';
        for (var i = 0; i < fsArr.length; i++) {
            if (act == fsArr[i]) continue;
            fs += fsArr[i] + ','
        }
        msg = '删除成功';
        fs = fs.substr(0, fs.length - 1);
    }

    var data = {
        'version':version,
        'disable_functions':fs,
    };

    phpPost('set_disable_func', version,data,function(data){
        var rdata = $.parseJSON(data.data);
        showMsg(rdata.status ? msg : rdata.msg, function(){
            disableFunc(version);
        } ,{ icon: rdata.status ? 1 : 2 });        
    });
}


//phpinfo
// function getPhpinfo(version) {
//     var con = '<button class="btn btn-default btn-sm" onclick="getPHPInfo(\'' + version + '\')">查看phpinfo()</button>';
//     $(".soft-man-con").html(con);
// }

//获取PHPInfo
function getPHPInfo_old(version) {
    phpPost('get_phpinfo', version, '', function(data){
        var rdata = data.data;
        layer.open({
            type: 1,
            title: "PHP-" + version + "-PHPINFO",
            area: ['90%', '90%'],
            closeBtn: 2,
            shadeClose: true,
            content: rdata
        });
    });
}

function getPHPInfo(version) {
    phpPostCallbak('get_php_info', version, {}, function(data){
        if (!data.status){
            layer.msg(rdata.msg, { icon: 2 });
            return;
        }

        layer.open({
            type: 1,
            title: "PHP-" + version + "-PHPINFO",
            area: ['70%', '90%'],
            closeBtn: 2,
            shadeClose: true,
            content: data.data.replace('a:link {color: #009; text-decoration: none; background-color: #fff;}', '').replace('a:link {color: #000099; text-decoration: none; background-color: #ffffff;}', '')
        });
    })
}



function phpLibConfig(version){
    
    phpPost('get_lib_conf', version, '', function(data){
        var rdata = $.parseJSON(data.data);

        if (!rdata.status){
            layer.msg(rdata.msg, { icon: rdata.status ? 1 : 2 });
            return;
        }

        var libs = rdata.data;
        var body = '';
        var opt = '';

        for (var i = 0; i < libs.length; i++) {
            if (libs[i].versions.indexOf(version) == -1){
                continue;
            }

            if (libs[i]['task'] == '-1' && libs[i].phpversions.indexOf(version) != -1) {
                opt = '<a style="color:green;" href="javascript:messageBox();">安装</a>'
            } else if (libs[i]['task'] == '0' && libs[i].phpversions.indexOf(version) != -1) {
                opt = '<a style="color:#C0C0C0;" href="javascript:messageBox();">等待安装...</a>'
            } else if (libs[i].status) {
                opt = '<a style="color:red;" href="javascript:uninstallPHPLib(\'' + version + '\',\'' + libs[i].name + '\',\'' + libs[i].title + '\',' + '' + ');">卸载</a>'
            } else {
                opt = '<a class="btlink" href="javascript:installPHPLib(\'' + version + '\',\'' + libs[i].name + '\',\'' + libs[i].title + '\',' + '' + ');">安装</a>'
            }

            body += '<tr>' +
                '<td>' + libs[i].name + '</td>' +
                '<td>' + libs[i].type + '</td>' +
                '<td>' + libs[i].msg + '</td>' +
                '<td><span class="ico-' + (libs[i].status ? 'start' : 'stop') + ' glyphicon glyphicon-' + (libs[i].status ? 'ok' : 'remove') + '"></span></td>' +
                '<td style="text-align: right;">' + opt + '</td>' +
                '</tr>';
        }


        var con = '<div class="divtable" id="phpextdiv" style="margin-right:10px;height: 420px; overflow: auto; margin-right: 0px;">' +
            '<table class="table table-hover" width="100%" cellspacing="0" cellpadding="0" border="0">' +
            '<thead>' +
            '<tr>' +
            '<th>名称</th>' +
            '<th width="64">类型</th>' +
            '<th>说明</th>' +
            '<th width="40">状态</th>' +
            '<th style="text-align: right;" width="50">操作</th>' +
            '</tr>' +
            '</thead>' +
            '<tbody>'  + body + '</tbody>' +
            '</table>' +
            '</div>' +
            '<ul class="help-info-text c7 pull-left">\
                <li>请按实际需求安装扩展,不要安装不必要的PHP扩展,这会影响PHP执行效率,甚至出现异常</li>\
                <li>Redis扩展只允许在1个PHP版本中使用,安装到其它PHP版本请在[软件管理]重装Redis</li>\
                <li>opcache/xcache/apc等脚本缓存扩展,请只安装其中1个,否则可能导致您的站点程序异常</li>\
                <li>ioncube要在ZendGuardLoader/opcache前安装,否则可能导致您的站点程序异常</li>\
            </ul>';
        $('.soft-man-con').html(con);
    });

}

//安装扩展
function installPHPLib(version, name, title, pathinfo) {
    layer.confirm('您真的要安装{1}吗?'.replace('{1}', name), { icon: 3, closeBtn: 2 }, function() {
        name = name.toLowerCase();
        var data = "name=" + name + "&version=" + version + "&type=1";

        phpPost('install_lib', version, data, function(data){
            var rdata = $.parseJSON(data.data);
            // layer.msg(rdata.msg, { icon: rdata.status ? 1 : 2 });
            showMsg(rdata.msg, function(){
                getTaskCount();
                phpLibConfig(version);
            },{ icon: rdata.status ? 1 : 2 });
            
        });
    });
}

//卸载扩展
function uninstallPHPLib(version, name, title, pathinfo) {
    layer.confirm('您真的要卸载{1}吗?'.replace('{1}', name), { icon: 3, closeBtn: 2 }, function() {
        name = name.toLowerCase();
        var data = 'name=' + name + '&version=' + version;
        phpPost('uninstall_lib', version, data, function(data){
            var rdata = $.parseJSON(data.data);
            // layer.msg(rdata.msg, { icon: rdata.status ? 1 : 2 });
            showMsg(rdata.msg, function(){
                getTaskCount();
                phpLibConfig(version);
            },{ icon: rdata.status ? 1 : 2 },5000);
            
        });
    });
}