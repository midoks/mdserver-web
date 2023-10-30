
function gogsPost(method,args,callback, title){

    var _args = null; 
    if (typeof(args) == 'string'){
        _args = JSON.stringify(toArrayObject(args));
    } else {
        _args = JSON.stringify(args);
    }

    var _title = '正在获取...';
    if (typeof(title) != 'undefined'){
        _title = title;
    }

    var loadT = layer.msg(_title, { icon: 16, time: 0, shade: 0.3 });
    $.post('/plugins/run', {name:'gitea', func:method, args:_args}, function(data) {
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

function gogsSetConfig(){
    gogsPost('get_gogs_conf', '', function(data){
        var rrdata = $.parseJSON(data.data);
        if (!rrdata.status){
            layer.msg(rrdata.msg,{icon:0,time:2000,shade: [0.3, '#000']});
            return;
        }
        var rdata = rrdata.data;
        var mlist = '';
        for (var i = 0; i < rdata.length; i++) {
            var w = '140';
            if (rdata[i].name == 'error_reporting') w = '250';
            var ibody = '<input style="width: ' + w + 'px;" class="bt-input-text mr5" name="' + rdata[i].name + '" value="' + rdata[i].value + '" type="text" >';
            switch (rdata[i].type) {
                case 0:
                    var selected_1 = (rdata[i].value == 1) ? 'selected' : '';
                    var selected_0 = (rdata[i].value == 0) ? 'selected' : '';
                    ibody = '<select class="bt-input-text mr5" name="' + rdata[i].name + '" style="width: ' + w + 'px;">\
                        <option value="1" ' + selected_1 + '>开启</option>\
                        <option value="0" ' + selected_0 + '>关闭</option>\
                        </select>';
                    break;
                case 1:
                    var selected_1 = (rdata[i].value == 'On') ? 'selected' : '';
                    var selected_0 = (rdata[i].value == 'Off') ? 'selected' : '';
                    ibody = '<select class="bt-input-text mr5" name="' + rdata[i].name + '" style="width: ' + w + 'px;">\
                        <option value="On" ' + selected_1 + '>开启</option>\
                        <option value="Off" ' + selected_0 + '>关闭</option></select>'
                    break;
                case 2:
                    var selected_1 = (rdata[i].value == 'true') ? 'selected' : '';
                    var selected_0 = (rdata[i].value == 'false') ? 'selected' : '';
                    ibody = '<select class="bt-input-text mr5" name="' + rdata[i].name + '" style="width: ' + w + 'px;">\
                        <option value="true" ' + selected_1 + '>开启</option>\
                        <option value="false" ' + selected_0 + '>关闭</option></select>'
                    break;
            }
            mlist += '<p><span>' + rdata[i].name + '</span>' + ibody + ', <font>' + rdata[i].ps + '</font></p>'
        }
        var html = '<style>.conf_p p{margin-bottom: 2px}</style><div class="conf_p" style="margin-bottom:0">\
                        ' + mlist + '\
                        <div style="margin-top:10px; padding-right:15px" class="text-right">\
                        <button class="btn btn-success btn-sm mr5" onclick="gogsSetConfig()">刷新</button>\
                        <button class="btn btn-success btn-sm" onclick="submitGogsConf()">保存</button></div>\
                    </div>';
        $(".soft-man-con").html(html);
    });
}


//提交PHP配置
function submitGogsConf() {
    var data = {
        DOMAIN: $("input[name='DOMAIN']").val(),
        ROOT_URL: $("input[name='ROOT_URL']").val(),
        HTTP_ADDR: $("select[name='HTTP_ADDR']").val(),
        HTTP_PORT: $("input[name='HTTP_PORT']").val(),
        START_SSH_SERVER: $("select[name='START_SSH_SERVER']").val() || 'false',
        SSH_PORT: $("input[name='SSH_PORT']").val(),
        REQUIRE_SIGNIN_VIEW: $("select[name='REQUIRE_SIGNIN_VIEW']").val() || 'false',
        ENABLE_CAPTCHA: $("select[name='ENABLE_CAPTCHA']").val() || 'true',
        DISABLE_REGISTRATION: $("select[name='DISABLE_REGISTRATION']").val() || 'false',
        ENABLE_NOTIFY_MAIL: $("select[name='ENABLE_NOTIFY_MAIL']").val() || 'false',
        FORCE_PRIVATE: $("select[name='FORCE_PRIVATE']").val() || 'false',
        SHOW_FOOTER_BRANDING: $("select[name='SHOW_FOOTER_BRANDING']").val() || 'false',
        SHOW_FOOTER_VERSION: $("select[name='SHOW_FOOTER_VERSION']").val() || 'false',
        SHOW_FOOTER_TEMPLATE_LOAD_TIME: $("select[name='SHOW_FOOTER_TEMPLATE_LOAD_TIME']").val() || 'false',
    };

    gogsPost('submit_gogs_conf', data, function(ret_data){
        var rdata = $.parseJSON(ret_data.data);
        layer.msg(rdata.msg, { icon: rdata.status ? 1 : 2 });
        gogsSetConfig();
    });
}

function gogsEdit(){

    gogsPost('gogs_edit',{} , function(data){
        // console.log(data);
        var rdata = $.parseJSON(data.data);
        var edit = '<p class="status">通用的手动编辑:</p>';
        edit +='<div class="sfm-opt">\
                <button class="btn btn-default btn-sm" onclick="onlineEditFile(0,\''+rdata['post_receive']+'\');">post-receive.tpl</button>\
                <button class="btn btn-default btn-sm" onclick="onlineEditFile(0,\''+rdata['commit']+'\');">commit.tpl</button>\
            </div>'; 
        $(".soft-man-con").html(edit);
    });
    
}


function giteaUserList(page, search) {

    var _data = {};
    if (typeof(page) =='undefined'){
        var page = 1;
    }
    
    _data['page'] = page;
    _data['page_size'] = 10;
    if(typeof(search) != 'undefined'){
        _data['search'] = search;
    }

    gogsPost('user_list', _data, function(data){

        var rdata = $.parseJSON(data.data);
        if (!rdata.status){
            layer.msg(rdata.msg,{icon:0,time:2000,shade: [0.3, '#000']});
            return;
        }
        content = '<div class="finduser"><input class="bt-input-text mr5 outline_no" type="text" placeholder="查找用户名" id="find_user" style="height: 28px; border-radius: 3px;width: 435px;">';
        content += '<button class="btn btn-success btn-sm find_user" >查找</button></div>';

        content += '<div class="divtable" style="margin-top:5px;"><table class="table table-hover" width="100%" cellspacing="0" cellpadding="0" border="0">';
        content += '<thead><tr>';
        content += '<th>序号</th>';
        content += '<th>用户或组织</th>';
        content += '<th>邮件地址</th>';
        content += '<th>操作(<a href="'+rdata['data']['root_url']+'" class="btlink" target="_blank">WEB管理</a>)</th>';
        content += '</tr></thead>';

        content += '<tbody>';

        ulist = rdata['data']['data'];
        for (i in ulist){

            var email = ulist[i]["email"] == '' ? '无' : ulist[i]["email"];
            var user_url = rdata['data']['root_url'] + ulist[i]["name"];
            content += '<tr><td>'+ulist[i]["id"]+'</td>'+
                '<td>'+ulist[i]["name"]+'</td>'+
                '<td>'+email+'</td>'+
                '<td><a class="btlink" target="_blank" href="'+user_url+'">项目管理</a></td>'+
                '</tr>';
        }

        content += '</tbody>';
        content += '</table></div>';

        var page_html = '<div class="dataTables_paginate paging_bootstrap pagination" style="margin-top:0px;"><ul id="softPage" class="page"><div>';
        page_html += rdata['data']['list'];
        page_html += '</div></ul></div>';

        content += page_html;

        $(".soft-man-con").html(content);

        $('.find_user').click(function(){
            var name = $('#find_user').val();
            giteaUserList(page, name);
        });
    });
}

function userProjectList(user, search){
    var loadOpen = layer.open({
        type: 1,
        title: '用户('+user+')项目列表',
        area: '500px',
        content:"<div class='bt-form pd20 c6'>\
                    <div>\
                        <div id='gitea_table' class='divtable' style='margin-top:5px;'>\
                            <table class='table table-hover'>\
                                <thead><tr><th>项目</th><th>操作</th></tr></thead>\
                                <tbody></tbody>\
                            </table>\
                            <div class='dataTables_paginate paging_bootstrap pagination' style='margin-top:0px;'><ul class='page'><div class='gitea_page'></div></ul></div>\
                        </div>\
                    </div>\
                </div>",
        success:function(){
            userProjectListPost(user,search);
        }
    });
}

function userProjectListPost(user, search){
    var req = {};
    if (!isNaN(user)){
        req['page'] = user;
        req['name'] = user = getCookie('gogsUserSelected');
    } else {
        req['page'] = 1;
        req['name'] = user;
        setCookie('gogsUserSelected', user);
    }
    
    req['page_size'] = 5;
    req['search'] = '';
    if(typeof(search) != 'undefined'){
        req['search'] = search;
    }
    
    gogsPost('user_project_list', req, function(data){
        var rdata = [];
        try {
            rdata = $.parseJSON(data.data);
        } catch(e){}

        if (!rdata['status']){
            layer.msg(rdata['msg'], { icon: 2 });
            return;
        }

        var list = '';
        // console.log(rdata);
        var project_list = rdata['data']['data'];
        for (i in project_list) {
            var name = project_list[i]['name'];
            list += '<tr>\
                    <td>'+name+'</td>\
                    <td>\
                        <a class="btlink" target="_blank" href="'+rdata['data']['root_url']+user+'/'+name+'">源码</a> | \
                        <a class="btlink" onclick="projectScript(\''+user+'\',\''+name+'\','+project_list[i]['has_hook']+');">脚本</a>\
                    </td>\
                </tr>';
        }

        $('#gitea_table tbody').html(list);

        var page = rdata['data']['list'];
        $('#gitea_table .gitea_page').html(page);
    });
}


function projectScript(user, name,has_hook){
    // console.log(user,name,has_hook);
    var html = '';
    if (has_hook){
        html += '<button class="btn btn-default btn-sm hook_edit">手动编辑</button>';
        html += '<button class="btn btn-default btn-sm hook_log">调试日志</button>';
        html += '<button class="btn btn-default btn-sm hook_load">重新加载</button>';
        html += '<button class="btn btn-default btn-sm hook_unload">卸载脚本</button>';
    } else {
        html += '<button class="btn btn-default btn-sm hook_load">加载脚本</button>';
    }

    var loadOpen = layer.open({
        type: 1,
        title: '['+user+']['+name+']脚本设置',
        area: '240px',
        content:'<div class="change-default pd20">'+html+'</div>',
        success:function(layero,index) {

            $('.hook_edit').click(function(){
                projectScriptEdit(user,name,index);
            });

            $('.hook_log').click(function(){
                projectScriptDebug(user,name,index);
            });

            $('.hook_load').click(function(){
                projectScriptLoad(user,name,index);
            });

            $('.hook_unload').click(function(){
                projectScriptUnload(user,name,index);
            });
        }
    });
}

function projectScriptEdit(user,name,index){
    gogsPost('project_script_edit', {'user':user,'name':name}, function(data){
        var rdata = $.parseJSON(data.data);
        if (rdata['status']){
            onlineEditFile(0, rdata['data']['path']);
        } else {
            layer.msg(rdata.msg,{icon:1,time:2000,shade: [0.3, '#000']});
        }        
    });
}

function projectScriptLoad(user,name,index){
    gogsPost('project_script_load', {'user':user,'name':name}, function(data){
        if (data.data != 'ok'){
            layer.msg(data.data,{icon:0,time:2000,shade: [0.3, '#000']});
            return;
        }

        showMsg('加载成功!',function(){
            layer.close(index);
            userProjectListPost(1);
        },{icon:1,time:2000,shade: [0.3, '#000']},2000);
    });
}

function projectScriptUnload(user,name,index){
    gogsPost('project_script_unload', {'user':user,'name':name}, function(data){
        if (data.data != 'ok'){
            layer.msg(data.data,{icon:0,time:2000,shade: [0.3, '#000']});
            return;
        }

        showMsg('卸载成功!',function(){
            layer.close(index);
            userProjectListPost(1);
        },{icon:1,time:2000,shade: [0.3, '#000']},2000);
    });
} 

function projectScriptDebug(user,name,index){
    gogsPost('project_script_debug', {'user':user,'name':name}, function(data){
        var rdata = $.parseJSON(data.data);
        if (rdata['status']){
            onlineEditFile(0, rdata['path']);
        } else {
            showMsg(rdata.msg,function(){
            },{icon:1,time:2000,shade: [0.3, '#000']},2000);
        }        
    });
}

function gogsRepoListPage(page, search){
    var _data = {};
    if (typeof(page) =='undefined'){
        var page = 1;
    }
    
    _data['page'] = page;
    _data['page_size'] = 10;
    if(typeof(search) != 'undefined'){
        _data['search'] = search;
    }

    gogsPost('repo_list', _data, function(data){

        var rdata = $.parseJSON(data.data);
        if (!rdata.status){
            layer.msg(rdata.msg,{icon:0,time:2000,shade: [0.3, '#000']});
            return;
        }
 
        var ulist = rdata['data']['data'];
        var body = ''
        for (i in ulist){
            // console.log(ulist[i]);

            var option = '';
            if(ulist[i]['has_hook']){
                option += '<a class="btlink unload" data-index="'+i+'">卸载脚本</a>' + ' | ';
                option += '<a class="btlink load" data-index="'+i+'">重载</a>' + ' | ';
                option += '<a class="btlink edit" data-index="'+i+'">编辑</a>' + ' | ';
                option += '<a class="btlink debug" data-index="'+i+'">日志</a>' + ' | ';
                option += '<a class="btlink run" data-index="'+i+'">手动</a>' + ' | ';
                option += '<a class="btlink scripts" data-index="'+i+'" onclick="projectScriptSelf(\''+ulist[i]["name"]+'\',\''+ulist[i]["repo"]+'\')" >自定义</a>';
            } else{
                option += '<a data-index="'+i+'" class="btlink load">加载脚本</a>';
            }


            body += '<tr><td>'+ulist[i]["id"]+'</td>'+
                '<td class="overflow_hide" style="width:70px;">' + ulist[i]["name"]+'</td>'+
                '<td class="overflow_hide" style="width:70px;display: inline-block;">' + ulist[i]["repo"]+'</td>'+
                '<td>' +
                    '<a class="btlink" target="_blank" href="'+rdata['data']['root_url']+ulist[i]["name"]+'/'+ulist[i]["repo"]+'">源码</a>' + ' | ' +
                    option + 
                '</td>' +
                '</tr>';
        }

        $('#repo_list tbody').html(body);
        $('#repo_list_page').html(rdata['data']['list']);

        $('.find_repo').click(function(){
            var find_repo = $('#find_repo').val();
            gogsRepoListPage(page, find_repo);
        });


        $('#repo_list .load').click(function(){
            var i = $(this).data('index');
            var user = ulist[i]["name"];
            var name = ulist[i]["repo"];

            gogsPost('project_script_load', {'user':user,'name':name}, function(data){
                if (data.data != 'ok'){
                    layer.msg(data.data,{icon:0,time:2000,shade: [0.3, '#000']});
                    return;
                }
                layer.msg('加载成功!',{icon:1,time:2000,shade: [0.3, '#000']});
                setTimeout(function(){
                    gogsRepoListPage(page, search);
                }, 2000);
            });
        });

        $('#repo_list .unload').click(function(){
            var i = $(this).data('index');
            var user = ulist[i]["name"];
            var name = ulist[i]["repo"];

            gogsPost('project_script_unload', {'user':user,'name':name}, function(data){
                if (data.data != 'ok'){
                    layer.msg(data.data,{icon:0,time:2000,shade: [0.3, '#000']});
                    return;
                }

                layer.msg('卸载成功!',{icon:1,time:2000,shade: [0.3, '#000']});
                setTimeout(function(){
                    gogsRepoListPage(page, search);
                }, 2000);
            });
        });

        $('#repo_list .edit').click(function(){
            var i = $(this).data('index');
            var user = ulist[i]["name"];
            var name = ulist[i]["repo"];

            gogsPost('project_script_edit', {'user':user,'name':name}, function(data){
                var rdata = $.parseJSON(data.data);
                if (rdata['status']){
                    onlineEditFile(0, rdata['data']['path']);
                } else {
                    layer.msg(rdata.msg,{icon:1,time:2000,shade: [0.3, '#000']});
                }        
            });
        });


        $('#repo_list .debug').click(function(){
            var i = $(this).data('index');
            var user = ulist[i]["name"];
            var name = ulist[i]["repo"];

            gogsPost('project_script_debug', {'user':user,'name':name}, function(data){
                var rdata = $.parseJSON(data.data);
                if (rdata['status']){
                    onlineEditFile(0, rdata['path']);
                } else {
                    layer.msg(rdata.msg,{icon:1,time:2000,shade: [0.3, '#000']});
                }        
            });
        });


        $('#repo_list .run').click(function(){
            var i = $(this).data('index');
            var user = ulist[i]["name"];
            var name = ulist[i]["repo"];

            gogsPost('project_script_run', {'user':user,'name':name}, function(data){
                var data = $.parseJSON(data.data);
                layer.msg(data.msg,{icon:data.status?1:2,time:2000,shade: [0.3, '#000']});
            });
        });
        
    //---------
    });
}


function giteaRepoList() {
    content = '<div class="finduser"><input class="bt-input-text mr5 outline_no" type="text" placeholder="查找项目" id="find_repo" style="height: 28px; border-radius: 3px;width: 435px;">';
    content += '<button class="btn btn-success btn-sm find_repo">查找</button></div>';

    content += '<div id="repo_list" class="divtable" style="margin-top:5px;"><table class="table table-hover" width="100%" cellspacing="0" cellpadding="0" border="0">';
    content += '<thead><tr>';
    content += '<th style="width:50px;">序号</th>';
    content += '<th style="width:80px;">用户/组织</th>';
    content += '<th style="width:80px;">项目名</th>';
    content += '<th>操作</th>';
    content += '</tr></thead>';

    content += '<tbody></tbody>';
    content += '</table></div>';

    var page = '<div class="dataTables_paginate paging_bootstrap pagination" style="margin-top:0px;"><ul id="repo_list_page" class="page"></ul></div>';

    content += page;

    $(".soft-man-con").html(content);

    gogsRepoListPage(1);
}

function projectScriptSelfRender(user, name){
    gogsPost('project_script_self', {'user':user,'name':name}, function(data){
        var rdata = $.parseJSON(data.data);

        var data = rdata['data']['data'];

        if (rdata['data']['self_hook']){
            $('#open_script').prop('checked',true);
        }

        var body = '';
        if(data.length == 0 ){
            body += '<tr><td colspan="3" style="text-align:center;">无脚本数据</td></tr>';
        } else{
            for (var i = 0; i < data.length; i++) {
                var b_status = '<a class="btlink status" data-index="'+i+'" target="_blank">已使用</a>';
                if (data[i]["is_hidden"]){
                    b_status = '<a class="btlink status" data-index="'+i+'" target="_blank">已隐藏</a>';
                }

                body += '<tr>'+
                '<td>' + data[i]["name"]+'</td>'+
                '<td>' + b_status + '</td>'+
                '<td>' +
                    '<a class="btlink del" data-index="'+i+'" target="_blank">删除</a>' + ' | ' +
                    '<a class="btlink edit" data-index="'+i+'" target="_blank">编辑</a>' + ' | ' +
                    '<a class="btlink logs" data-index="'+i+'" target="_blank">日志</a>' + ' | ' +
                    '<a class="btlink run" data-index="'+i+'" target="_blank">手动</a>' + ' | ' +
                    '<a class="btlink rename" data-index="'+i+'" target="_blank">重命名</a>' +
                '</td></tr>';
            }   
            
        }

        $('#gogs_self_table tbody').html(body);
        $('#gogs_self_table .page').html(rdata['data']['list']);

        $('#gogs_self_table .status').click(function(){
            var i = $(this).data('index');
            var file = data[i]["name"];
            var status = '1';
            if (data[i]["is_hidden"]){
                status = '0';
            }
            gogsPost('project_script_self_status', {'user':user,'name':name,'file':file, status:status}, function(data){
                var data = $.parseJSON(data.data);
                showMsg(data.msg ,function(){
                    projectScriptSelfRender(user, name);
                },{icon:data.code?2:1,time:2000,shade: [0.3, '#000']},2000);
            });
        });

        $('#gogs_self_table .del').click(function(){
            var i = $(this).data('index');
            var file = data[i]["name"];
            gogsPost('project_script_self_del', {'user':user,'name':name,'file':file}, function(data){
                var data = $.parseJSON(data.data);
                showMsg(data.msg ,function(){
                    projectScriptSelfRender(user, name);
                },{icon:data.code?2:1,time:2000,shade: [0.3, '#000']},2000);
            });
        });

        $('#gogs_self_table .edit').click(function(){
            var i = $(this).data('index');
            var path = data[i]["path"];
            onlineEditFile(0,path);
        });

        $('#gogs_self_table .logs').click(function(){
            var i = $(this).data('index');
            var file = data[i]["name"];
            gogsPost('project_script_self_logs', {'user':user,'name':name,'file':file}, function(data){
                var rdata = $.parseJSON(data.data);
                // console.log(rdata);
                if (rdata['status']){
                    onlineEditFile(0, rdata['data']['path']);
                } else {
                    layer.msg(rdata.msg,{icon:data.status?2:1,time:2000,shade: [0.3, '#000']});
                }        
            });
        });

        $('#gogs_self_table .run').click(function(){
            var i = $(this).data('index');
            var file = data[i]["name"];
            if (data[i]["is_hidden"]){
                layer.msg("已经禁用,不能执行!",{icon:2,time:2000,shade: [0.3, '#000']});
                return;
            }
            gogsPost('project_script_self_run', {'user':user,'name':name,'file':file}, function(data){
                var rdata = $.parseJSON(data.data);
                layer.msg(rdata.msg,{icon:data.status?1:2,time:2000,shade: [0.3, '#000']});      
            });
        });


        $('#gogs_self_table .rename').click(function(){
            var i = $(this).data('index');
            var file = data[i]["name"];

            if (data[i]["is_hidden"]){
                layer.msg("已经禁用,不能执行!",{icon:2,time:2000,shade: [0.3, '#000']});
                return;
            }

            file = file.split('.sh')[0];

            layer.open({
                type: 1,
                shift: 5,
                closeBtn: 1,
                area: '320px', 
                title: '重命名',
                btn:['设置','关闭'],
                content: '<div class="bt-form pd20">\
                            <div class="line">\
                                <input type="text" class="bt-input-text" name="Name" id="newFileName" value="'+file+'" placeholder="文件名" style="width:100%" />\
                            </div>\
                        </div>',
                success:function(){
                    $("#newFileName").focus().keyup(function(e){
                        if(e.keyCode == 13) $(".layui-layer-btn0").click();
                    });
                },
                yes:function(){
                    var n_file = $("#newFileName").val();
                    var o_file = file;

                    gogsPost('project_script_self_rename', {'user':user,'name':name,'o_file':o_file,'n_file':n_file}, function(data){
                        var data = $.parseJSON(data.data);
                        showMsg(data.msg ,function(){
                            $(".layui-layer-btn1").click();
                            projectScriptSelfRender(user, name);
                        },{icon:data.code?2:1,time:2000,shade: [0.3, '#000']},2000);     
                    });
                }
            });
        //-----
        });
    //------
    });
}

//新建文件
function createScriptFile(type, user, name, file) {
    if (type == 1) {
        gogsPost('project_script_self_create', {'user':user,'name':name,'file': file }, function(data){
            var rdata = $.parseJSON(data.data);
            if(!rdata['status']){
                layer.msg(rdata.msg,{icon:2,time:2000,shade: [0.3, '#000']});
                return;
            }

            showMsg(rdata.msg, function(){
                $(".layui-layer-btn1").click();
                onlineEditFile(0,rdata['data']['abs_file']);
                projectScriptSelfRender(user, name);
            }, {icon:1,shade: [0.3, '#000']},2000);
        });
        return;
    }
    layer.open({
        type: 1,
        shift: 5,
        closeBtn: 1,
        area: '320px', 
        title: '新建自定义脚本',
        btn:['新建','关闭'],
        content: '<div class="bt-form pd20">\
                    <div class="line">\
                        <input type="text" class="bt-input-text" name="Name" id="newFileName" value="" placeholder="文件名" style="width:100%" />\
                    </div>\
                </div>',
        success:function(){
            $("#newFileName").focus().keyup(function(e){
                if(e.keyCode == 13) $(".layui-layer-btn0").click();
            });
        },
        yes:function(){
            var file = $("#newFileName").val();;
            createScriptFile(1, user, name, file);
        }
    });
}

function projectScriptSelf(user, name){
    layer.open({
        type: 1,
        title: '项目('+user+'/'+name+')自定义脚本',
        area: '500px',
        content:"<div class='bt-form pd15'>\
                <button id='create_script' class='btn btn-success btn-sm' type='button' style='margin-right: 5px;''>添加脚本</button>\
                <div style='float:right;'>\
                    <span style='line-height: 23px;'>开启自定义脚本</span>\
                    <input class='btswitch btswitch-ios' id='open_script' type='checkbox'>\
                    <label id='script_hook_enable' class='btswitch-btn' for='open_script'  style='display: inline-flex;line-height:38px;margin-left: 4px;float: right;'></label>\
                </div>\
                <div id='gogs_self_table' class='divtable' style='margin-top:5px;'>\
                    <table class='table table-hover'>\
                        <thead><tr><th style='width:100px;'>脚本文件名</th><th>状态</th><th>操作</th></tr></thead>\
                        <tbody></tbody>\
                    </table>\
                    <div class='dataTables_paginate paging_bootstrap pagination' style='margin-top:0px;'>\
                        <ul class='page'><div class='gogs_page'></div></ul>\
                    </div>\
                </div>\
            </div>",
        success:function(){
            projectScriptSelfRender(user, name);

            $('#create_script').click(function(){
                createScriptFile(0, user, name);
            });

            $('#script_hook_enable').click(function(){
                var enable = $('#open_script').prop('checked');
                var enable_option = '0';
                if (!enable){
                    enable_option = '1';
                }
                gogsPost('project_script_self_enable', {'user':user,'name':name,'enable':enable_option}, function(data){
                    var data = $.parseJSON(data.data);
                    showMsg(data.msg ,function(){
                        projectScriptSelfRender(user, name);
                    },{icon:data.status?1:2,shade: [0.3, '#000']},2000);
                });

            });
        }
    });  
}

function getRsaPublic(){
    gogsPost('get_rsa_public', {}, function(data){
        var rdata = $.parseJSON(data.data);
        var con = '<div class="tab-con">\
            <div class="myKeyCon ptb15">\
                <textarea style="margin:0px;width:580px;height:110px;outline:none;" spellcheck="false">'+rdata.mw+'</textarea>\
            </div>\
            <ul class="help-info-text c7 pull-left"></ul>\
        </div>'
        layer.open({
            type: 1,
            area: "600px",
            title: '本机公钥',
            closeBtn: 2,
            shift: 5,
            shadeClose: false,
            content:con
        });   
    });
}

function giteaRead(){

    var readme = '<ul class="help-info-text c7">';
    readme += '<li>默认使用MySQL,第一个启动加载各种配置,并修改成正确的数据库配置</li>';
    readme += '<li>邮件端口使用456,gitea仅支持使用STARTTLS的SMTP协议</li>';
    readme += '<li>项目【加载脚本】后,会自动同步到wwwroot目录下</li>';
    readme += '<li><a href="#" onclick="getRsaPublic();">点击查看本机公钥</></li>';
    readme += '</ul>';

    $('.soft-man-con').html(readme);   
}