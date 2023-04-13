function ssPost(method,args,callback){
    var _args = null; 
    if (typeof(args) == 'string'){
        _args = JSON.stringify(toArrayObject(args));
    } else {
        _args = JSON.stringify(args);
    }

    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });



    var req_data = {};
    req_data['name'] = 'system_safe';
    req_data['script'] = 'system_safe';
    req_data['func'] = method;
    req_data['args'] = _args;
    $.post('/plugins/run', req_data, function(data) {
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

function ssAsyncPost(method,args){
    var _args = null; 
    if (typeof(args) == 'string'){
        _args = JSON.stringify(toArrayObject(args));
    } else {
        _args = JSON.stringify(args);
    }
    return syncPost('/plugins/run', {name:'system_safe', func:method, args:_args}); 
}

function ssPostCallbak(method, args, callback){
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });

    var req_data = {};
    req_data['name'] = 'system_safe';
    req_data['func'] = method;
    req_data['script'] = 'system_safe';
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

function getSafeConfigPathList(tag){
    ssPost('get_safe_data', {tag:tag}, function(rdata){
        var rdata = $.parseJSON(rdata.data);
        var slist = rdata.data.paths;

        var body = '';
        for (var i = 0; i < slist.length; i++) {
            body += "<tr>";
            body += "<td>"+slist[i]['path']+"</td>";

            if (slist[i]['chattr'] == 'i'){
                body += "<td>只读</td>";
            } else if (slist[i]['chattr'] == 'a'){
                body += "<td>追加</td>";
            } else{
                body += "<td>只读</td>";
            }

            if (rdata.msg['open']){
                body += "<td>"+slist[i]['d_mode']+"</td>";
                body += "<td><a class='btlink'>已保护</a></td>";
            } else {
                body += "<td>"+slist[i]['s_mode']+"</td>";
                body += "<td><a style='color:red;'>未保护</a></td>";
            }
            body += "<td style='text-align: right;'><a class='btlink safe_path_delete' row='"+i+"'>删除</a></td>";
            body += "</tr>";
        }

        $('#safe-file-table tbody').html(body);
        $('.safe_path_delete').click(function(){
            var id = $(this).attr('row');
            ssPost('del_safe_path',{tag:tag,index:id}, function(rdata){
                var rdata = $.parseJSON(rdata.data);
                showMsg(rdata.msg, function(){
                    getSafeConfigPathList(tag);
                },{icon:rdata.status?1:2,shade: [0.3, '#000']},2000);
            });
        });
    });
}

function setSafeConfigPath(tag, alist){

    layer.open({
        type: 1,
        area: ['700px','535px'],
        title: '配置【'+alist['name']+'】',
        content: "<form class='bt-form pd20'>\
                    <div style='border-bottom:#ccc 1px solid;margin-bottom:10px;padding-bottom:10px'>\
                        <input class='bt-input-text' name='s_path' id='s_path' type='text' value='' style='width:370px;margin-right:5px;' placeholder='被保护的文件或目录完整路径'>\
                        <a class='glyphicon cursor glyphicon-folder-open' onclick='changePath(\"s_path\")' style='color:#edca5c;margin-right:20px;font-size:16px'></a>\
                        <select class='bt-input-text' name='chattr'>\
                            <option value='i'>只读</option>\
                            <option value='a'>追加</option>\
                        </select>\
                        <input class='bt-input-text mr5' name='d_mode' type='text' style='width:120px;' placeholder='权限'>\
                        <button type='button' class='btn btn-success btn-sm va0 pull-right add_safe_config'>添加</button>\
                    </div>\
                    <div class='divtable'>\
                        <div id='safe-file-table' class='table_head_fix' style='max-height:300px;overflow:auto;border:#ddd 1px solid'>\
                        <table class='table table-hover' style='border:none'>\
                            <thead>\
                                <tr>\
                                    <th width='360'>路径</th>\
                                    <th>模式</th>\
                                    <th>权限</th>\
                                    <th>状态</th>\
                                    <th style='text-align: right;'>操作</th>\
                                </tr>\
                            </thead>\
                            <tbody></tbody>\
                            </table>\
                        </div>\
                    </div>\
                    <ul class='help-info-text c7 ptb10' style='margin-top: 5px;'>\
                        <li>【只读】无法修改、创建、删除文件和目录</li>\
                        <li>【追加】只能追加内容，不能删除或修改原有内容</li>\
                        <li>【权限】设置文件或目录在受保护状态下的权限(非继承),关闭保护后权限自动还原</li>\
                        <li>【如何填写权限】请填写Linux权限代号,如:644、755、600、555等,如果不填写,则使用文件原来的权限</li>\
                    </ul>\
                  </form>",
        success:function(){

            $('.add_safe_config').click(function(){
                var path = $('input[name="s_path"]').val();
                var chattr = $('select[name="chattr"]').val();
                var d_mode = $('input[name="d_mode"]').val();
                ssPost('add_safe_path',{tag:tag,path:path,chattr:chattr,d_mode:d_mode}, function(rdata){
                    var rdata = $.parseJSON(rdata.data);
                    showMsg(rdata.msg, function(){
                        getSafeConfigPathList(tag);
                    },{icon:rdata.status?1:2,shade: [0.3, '#000']},2000);
                });
            });
        }
    });
    getSafeConfigPathList(tag);

    
}

function setSafeConfigSsh(tag, alist){


    function setSafeConfigSshData(){
        ssPost('get_ssh_data', {}, function(rdata){
            var rdata = $.parseJSON(rdata.data);
            var info = rdata.data;

            $('input[name="s_cycle"]').val(info['cycle']);
            $('input[name="s_limit_count"]').val(info['limit_count']);
            $('input[name="s_limit"]').val(info['limit']);
        });
    }
    layer.open({
        type: 1,
        area: ['700px','210px'],
        title: '配置【'+alist['name']+'】',
        content: "<form class='bt-form pd20'>\
                    <div style='border-bottom:#ccc 1px solid;margin-bottom:10px;padding-bottom:10px'>\
                        在(检测周期)\
                        <input class='bt-input-text' min='30' max='1800' name='s_cycle' type='number' value='120' style='width:80px;margin-right:5px;'>\
                        秒内,登录错误(检测阈值)\
                        <input class='bt-input-text' min='30' max='1800' name='s_limit_count' type='number' value='120' style='width:80px;margin-right:5px;'>\
                        次,封锁(封锁时间)\
                        <input min='60' class='bt-input-text' name='s_limit' type='number' value='3600' style='width:80px;margin-right:12px;'>\
                        <button type='button' class='btn btn-success btn-sm va0 pull-right save_safe_ssh'>保存</button>\
                    </div>\
                    <ul class='help-info-text c7 ptb10' style='margin-top: 5px;'>\
                        <li>触发以上策略后，客户端IP将被封锁一段时间</li>\
                        <li>请在面板日志或操作日志中查看封锁记录</li>\
                        <li>请在面板日志或操作日志中查看SSH成功登录的记录</li>\
                    </ul>\
                  </form>",
        success:function(){
            setSafeConfigSshData();

            $('.save_safe_ssh').click(function(){
                var cycle = $('input[name="s_cycle"]').val();
                var limit_count = $('input[name="s_limit_count"]').val();
                var limit = $('input[name="s_limit"]').val();
                ssPost('save_safe_ssh',{cycle:cycle,limit_count:limit_count,limit:limit}, function(rdata){
                    var rdata = $.parseJSON(rdata.data);
                    showMsg(rdata.msg, function(){
                        setSafeConfigSshData();
                    },{icon:rdata.status?1:2,shade: [0.3, '#000']},2000);
                });
            });
        }
    });

}

function setSafeConfigProcessList(tag){
    ssPost('get_process_data', {}, function(rdata){
        var rdata = $.parseJSON(rdata.data);
        var slist = rdata.data.process_white;

        var body = '';
        for (var i = 0; i < slist.length; i++) {
            body += "<tr>\
                    <td>"+slist[i]+"</td>\
                    <td style='text-align: right;'><a class='btlink safe_path_delete' row='"+i+"'>删除</a></td>\
                </tr>";
        }

        $('#safe-file-table tbody').html(body);
        $('.safe_path_delete').click(function(){
            var id = $(this).attr('row');
            ssPost('del_safe_proccess_name',{tag:tag,index:id}, function(rdata){
                var rdata = $.parseJSON(rdata.data);
                showMsg(rdata.msg, function(){
                    setSafeConfigProcessList(tag);
                },{icon:rdata.status?1:2,shade: [0.3, '#000']},2000);
            });
        });
    });
}

function setSafeConfigProcess(tag, alist){
    layer.open({
        type: 1,
        area: ['700px','535px'],
        title: '配置【进程白名单】',
        content: "<form class='bt-form pd20'>\
                    <div style='border-bottom:#ccc 1px solid;margin-bottom:10px;padding-bottom:10px'>\
                        <input class='bt-input-text' name='s_name' id='s_name' type='text' value='' style='width:370px;margin-right:5px;' placeholder='完整的进程名'>\
                        <button type='button' class='btn btn-success btn-sm va0 pull-right add_process_white'>添加</button>\
                    </div>\
                    <div class='divtable'>\
                        <div id='safe-file-table' class='table_head_fix' style='max-height:300px;overflow:auto;border:#ddd 1px solid'>\
                        <table class='table table-hover' style='border:none'>\
                            <thead>\
                                <tr>\
                                    <th width='360'>进程名称</th>\
                                    <th style='text-align: right;'>操作</th>\
                                </tr>\
                            </thead>\
                            <tbody></tbody>\
                            </table>\
                        </div>\
                    </div>\
                    <ul class='help-info-text c7 ptb10' style='margin-top: 5px;'>\
                        <li>【进程名称】请填写完整的进程名称,如: mysqld</li>\
                        <li>【说明】在白名单列表中的进程将不再检测范围,建议将常用软件的进程添加进白名单</li>\
                    </ul>\
                  </form>",
        success:function(){
            $('.add_process_white').click(function(){
                var process_name = $('input[name="s_name"]').val();
                ssPost('add_process_white',{process_name:process_name}, function(rdata){
                    var rdata = $.parseJSON(rdata.data);
                    showMsg(rdata.msg, function(){
                        setSafeConfigProcessList(tag);
                    },{icon:rdata.status?1:2,shade: [0.3, '#000']},2000);
                });
            });
        }
    });

    setSafeConfigProcessList(tag);


}

function setSafeConfig(tag, alist){

    if ($.inArray(tag, ['bin', 'service', 'home', 'user', 'bin', 'cron'])>-1){
        setSafeConfigPath(tag,alist);
    }

    if ($.inArray(tag, ['ssh'])>-1){
        setSafeConfigSsh(tag,alist);
    }

    if ($.inArray(tag, ['process'])>-1){
        setSafeConfigProcess(tag,alist);
    }
}

//设置安全状态
function setSafeStatus(obj,tag){
    var o = $(obj).prev();
    var status = $(o).prop('checked');
    ssPost('set_safe_status', {tag:tag,status:!status}, function(rdata){
        var rdata = $.parseJSON(rdata.data);

        if (!rdata.status){
            layer.msg(rdata.msg,{icon:0,time:2000,shade: [0.3, '#000']});
            $(o).prop('checked',status);
            return;
        }
        layer.msg("配置成功!",{icon:1,time:2000,shade: [0.3, '#000']});
    });
}

function ssConfigList(){

    ssPost('conf',{},function(rdata){
        var rdata = $.parseJSON(rdata.data);
        var libs = rdata.data;
        // console.log(libs);
        var body = '';
        for (var i in libs) {
            
            if (i == 'open'){
                continue;
            }

            var checked = '';
            if (libs[i].open){
                checked = 'checked';
            }

            body += '<tr>' +
                '<td>' + libs[i].name + '</td>' +
                '<td>' + libs[i].ps + '</td>' +
                '<td>\
                    <div class="ssh-item">\
                        <input class="btswitch btswitch-ios" id="sys_service_'+i +'" type="checkbox" '+checked+'>\
                        <label class="btswitch-btn service_switch" for="sys_service_'+i+'" style="width: 2em; height: 1.1em;padding:1px;"></label>\
                    </div>\
                </td>'+
                '<td style="text-align: right;"><a id="conf_sys_service_'+i+'" class="btlink set_safe_config">配置</a></td>' +
                '</tr>';
        }

        var con = '<div class="divtable" id="system_safe_list" style="margin-right:10px;max-height: 320px; overflow: auto; margin-right: 0px;">' +
            '<table class="table table-hover" width="100%" cellspacing="0" cellpadding="0" border="0">' +
            '<thead>' +
            '<tr>' +
            '<th>名称</th>' +
            '<th>描述</th>' +
            '<th width="40">状态</th>' +
            '<th style="text-align: right;" width="50">操作</th>' +
            '</tr>' +
            '</thead>' +
            '<tbody>'  + body + '</tbody>' +
            '</table>' +
            '</div>' +
            '<ul class="help-info-text c7 pull-left">\
                <li>开启系统加固功能后，一些如软件安装等敏感操作将被禁止</li>\
                <li>开启【SSH服务加固】之后，用户登录SSH的行为将受到监控，若连续多次登录失败，将采取封IP措施</li>\
                <li>【异常进程监控】与【SSH服务加固】会占用一定服务器开销</li>\
                <li><span style="color:red;">【注意】如果您需要安装软件或插件，请先将系统加固关闭!</span></li>\
            </ul>';

        $('.soft-man-con').html(con);

        $('#system_safe_list .service_switch').click(function(){
            var val = $(this).prev().attr('id');
            val = val.replace('sys_service_','');
            setSafeStatus(this,val);
        });

        $('.set_safe_config').click(function(){
            var name = $(this).attr('id');
            // console.log(name);
            name = name.replace('conf_sys_service_','');
            setSafeConfig(name, libs[name]);
        });

    });

}

function ssOpLogList(p){
    ssPost('op_log',{p:p},function(rdata){
        var rdata = $.parseJSON(rdata.data);
        var plist = rdata.data.data;

        var body = '';
        for (var i = 0; i < plist.length; i++) {
            body += "<tr>\
                <td><em class='dlt-num'>" + plist[i].addtime + "</em></td>\
                <td>" + plist[i].log + "</td>\
            </tr>";
        }

        $("#system_safe_log_list tbody").html(body);
        $("#system_safe_log_page").html(rdata.data.page);
    });
}

function ssOpLog(){
    var con = '<div class="divtable" id="system_safe_log_list" style="margin-right:10px;max-height: 380px; overflow: auto; margin-right: 0px;">\
            <table class="table table-hover" width="100%" cellspacing="0" cellpadding="0" border="0">\
            <thead><tr><th style="width:135px;">时间</th><th>详情</th></tr></thead>\
            <tbody></tbody>\
            </table>\
        </div>\
        <div id="system_safe_log_page" class="dataTables_paginate paging_bootstrap page"></div>';
    $('.soft-man-con').html(con);
    ssOpLogList(1);
}


function ssLogAuditList(){
    ssPost('get_sys_logfiles',{},function(rdata){
        var rdata = $.parseJSON(rdata.data);
        var plist = rdata.data;
        var option = '';
        // console.log(plist);
        for (var i = 0; i < plist.length; i++) {
            option += '<option value="'+plist[i]['name']+'">'+plist[i]['name'] +' - '+plist[i]['title']+'</option>';
        }

        $("#system_safe_log_audit").html(option);
        var log_name = $('#system_safe_log_audit option:first').val();
        ssLogAuditFile(log_name);

        $('#system_safe_log_audit').change(function(){
             var log_name = $('#system_safe_log_audit option:selected').val();
            ssLogAuditFile(log_name);
        });
    });
}

function ssLogAuditFileRenderString(data){

    var tbody = '<textarea style="margin: 0px;width: 100%;height: 380px;background-color: #333;color:#fff; padding:0 5px" id="system_safe_log_audit_str"></textarea>';
    $("#system_safe_log_audit_list").html(tbody);
    var ob = document.getElementById('system_safe_log_audit_str');
    ob.scrollTop = ob.scrollHeight;

    $("#system_safe_log_audit_str").html(data);
}

function ssLogAuditFileRenderObject(plist){

    var pre_html = '<table class="table table-hover" width="100%" cellspacing="0" cellpadding="0" border="0">\
            <thead><tr><th>时间</th><th>角色</th><th>事件</th></tr></thead>\
            <tbody></tbody>\
        </table>';
    $("#system_safe_log_audit_list").html(pre_html);

    if (plist.length>0){
        var tmp = plist[0];
        // console.log(tmp);
        var thead = '';
        tbody += '<tr>'
        for (var i in tmp) {
            tbody+='<th>'+ i + '</th>';
        }
        tbody += '</tr>';
        $("#system_safe_log_audit_list thead").html(tbody);
    }
    

    var tbody = '';
    for (var i = 0; i < plist.length; i++) {
        tbody += '<tr>';
        for (var vv in plist[i]) {
            tbody+= '<td>'+ plist[i][vv] + '</td>'
        }
        tbody += '</tr>';
    }

    $("#system_safe_log_audit_list tbody").html(tbody);
}

function ssLogAuditFile(log_name){
    // ssPost('get_sys_log',{log_name:log_name},function(rdata){
    //     try{
    //         var rdata = $.parseJSON(rdata.data);
    //         if (typeof(rdata.data) == 'object'){
                
    //             if (!rdata.status){
    //                 layer.msg(rdata.msg,{icon:0,time:2000,shade: [0.3, '#000']});
    //                 return;
    //             }
    //             var plist = rdata.data;
    //             ssLogAuditFileRenderObject(plist);
    //         }
    //     }catch(e){
    //         if (typeof(rdata.data) == 'string'){
    //             ssLogAuditFileRenderString(rdata.data);
    //         }
    //     }
    // });

    ssPostCallbak('get_sys_log',{log_name:log_name},function(rdata){
        try{
            var rdata = $.parseJSON(rdata.data);
            if (typeof(rdata.data) == 'object'){
                if (!rdata.status){
                    layer.msg(rdata.msg,{icon:0,time:2000,shade: [0.3, '#000']});
                    return;
                }
                var plist = rdata.data;
                ssLogAuditFileRenderObject(plist);
            }
        }catch(e){
            if (typeof(rdata.data) == 'string'){
                ssLogAuditFileRenderString(rdata.data);
            }
        }
    });
}

function ssLogAudit(){
    var con = '<select id="system_safe_log_audit" class="bt-input-text mr20" style="width:50%;margin-bottom: 3px;">\
            <option value="0">请选择</option>\
        </select>\
        <div class="divtable" id="system_safe_log_audit_list" style="margin-right:10px;height: 380px; overflow: auto; margin-right: 0px;"></div>';
    $('.soft-man-con').html(con);
    ssLogAuditList();
}

function ssLockAddressList(){
    ssPost('get_ssh_limit_info',{},function(rdata){
        var rdata = $.parseJSON(rdata.data);
        var libs = rdata.data;
        var tbody = '';
        for (var i in libs) {
            var end_time = libs[i].end;
            var time_title = '手动解封';
            if (end_time != '0'){
                time_title = '自动解封时间:'+end_time;
            }
            tbody += '<tr>' +
                '<td style="width:100px;">' + libs[i].address + '</td>' +
                '<td style="width:100px;">'+time_title+'</td>' +
                '<td style="text-align: right;"><a ip="'+libs[i].address+'" class="btlink remove_ssh_limit">立即解封</a></td>' +
                '</tr>';
        }

        $('#system_lock_address tbody').html(tbody);
        $('#system_lock_address .remove_ssh_limit').click(function(){
            var address = $(this).attr('ip');
            ssPost('remove_ssh_limit', {ip:address}, function(rdata){
                var rdata = $.parseJSON(rdata.data);
                showMsg(rdata.msg, function(){
                    ssLockAddressList();
                },{icon:rdata.status?1:2,shade: [0.3, '#000']},2000);
            });
        });
    });
}

function ssLockAddress(){

    var con = '<div style="margin-bottom:10px;">\
                <input class="bt-input-text" name="s_address" type="text" value="" style="width:250px;margin-right:12px;" placeholder="IP地址">\
                <button class="btn btn-success btn-sm va0 add_lock_address">添加</button>\
            </div>\
            <div class="divtable" id="system_lock_address" style="margin-right:10px;max-height: 320px; overflow: auto; margin-right: 0px;">' +
            '<table class="table table-hover" width="100%" cellspacing="0" cellpadding="0" border="0">' +
            '<thead>' +
            '<tr>' +
            '<th>IP</th>' +
            '<th>解封时间</th>' +
            '<th style="text-align: right;" width="50">操作</th>' +
            '</tr>' +
            '</thead>' +
            '<tbody></tbody>' +
            '</table>' +
            '</div>' +
            '<ul class="help-info-text c7 pull-left">\
                <li>【封锁IP】此处封锁的IP仅针对SSH服务，即被封锁的IP将无法连接SSH</li>\
                <li>【添加】手动添加的IP封锁只能手动解封!</li>\
            </ul>';

    $('.soft-man-con').html(con);

    $('.add_lock_address').click(function(){
        var address = $('input[name="s_address"]').val();
        ssPost('add_ssh_limit', {ip:address}, function(rdata){
            var rdata = $.parseJSON(rdata.data);
            showMsg(rdata.msg, function(){
                ssLockAddressList();
            },{icon:rdata.status?1:2,shade: [0.3, '#000']},2000);
        });
    });
    ssLockAddressList();
}