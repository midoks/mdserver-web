
function str2Obj(str){
    var data = {};
    kv = str.split('&');
    for(i in kv){
        v = kv[i].split('=');
        data[v[0]] = v[1];
    }
    return data;
}

function gogsPost(method,args,callback, title){

    var _args = null; 
    if (typeof(args) == 'string'){
        _args = JSON.stringify(str2Obj(args));
    } else {
        _args = JSON.stringify(args);
    }

    var _title = '正在获取...';
    if (typeof(title) != 'undefined'){
        _title = title;
    }

    var loadT = layer.msg(_title, { icon: 16, time: 0, shade: 0.3 });
    $.post('/plugins/run', {name:'gogs', func:method, args:_args}, function(data) {
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

function gogsUserList(page, search) {

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
        content += '<button class="btn btn-success btn-sm" onclick="userFind();">查找</button></div>';

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
            email = ulist[i]["email"] == '' ? '无' : ulist[i]["email"];
            content += '<tr><td>'+ulist[i]["id"]+'</td>'+
                '<td>'+ulist[i]["name"]+'</td>'+
                '<td>'+email+'</td>'+
                '<td><a class="btlink" onclick="userProjectList(\''+ulist[i]["name"]+'\')">项目管理</a></td>'+
                '</tr>';
        }

        content += '</tbody>';
        content += '</table></div>';

        var page = '<div class="dataTables_paginate paging_bootstrap pagination" style="margin-top:0px;"><ul id="softPage" class="page"><div>';
        page += rdata['data']['list'];
        page += '</div></ul></div>';

        content += page;

        $(".soft-man-con").html(content);
    });
}

function userProjectList(user, search){
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

    $('.layui-layer-close1').click();
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
            list += '<tr><td>'+name+'</td>\
                    <td>\
                        <a class="btlink" target="_blank" href="'+rdata['data']['root_url']+user+'/'+name+'">源码</a> | \
                        <a class="btlink" onclick="projectScript(\''+user+'\',\''+name+'\','+project_list[i]['has_hook']+');">脚本</a>\
                    </td>\
                </tr>';
        }

        var page = '<div class="dataTables_paginate paging_bootstrap pagination" style="margin-top:0px;"><ul id="softPage" class="page"><div>';
        page += rdata['data']['list'];
        page += '</div></ul></div>';

        var loadOpen = layer.open({
            type: 1,
            title: '用户('+user+')项目列表',
            area: '500px',
            content:"<div class='bt-form pd20 c6'>\
                    <div>\
                            <div class='divtable' style='margin-top:5px;'>\
                                <table class='table table-hover'>\
                                    <thead><tr><th>项目</th><th>操作</th></tr></thead>\
                                    <tbody>" + list + "</tbody>\
                                </table>" + 
                                page +
                    "</div></div></div>"
        });
    });
}


function projectScript(user, name,has_hook){
    // console.log(user,name,has_hook);
    var html = '';
    if (has_hook){
        html += '<button onclick="projectScriptEdit(\''+user+'\',\''+name+'\')" class="btn btn-default btn-sm">手动编辑</button>';
        html += '<button onclick="projectScriptDebug(\''+user+'\',\''+name+'\')" class="btn btn-default btn-sm">调试日志</button>';
        html += '<button onclick="projectScriptLoad(\''+user+'\',\''+name+'\')" class="btn btn-default btn-sm">重新加载</button>';
        html += '<button onclick="projectScriptUnload(\''+user+'\',\''+name+'\')" class="btn btn-default btn-sm">卸载脚本</button>';
    } else {
        html += '<button onclick="projectScriptLoad(\''+user+'\',\''+name+'\')" class="btn btn-default btn-sm">加载脚本</button>';
    }

    var loadOpen = layer.open({
        type: 1,
        title: '['+user+']['+name+']脚本设置',
        area: '240px',
        content:'<div class="change-default pd20">'+html+'</div>'
    });
}

function projectScriptEdit(user,name){
    gogsPost('project_script_edit', {'user':user,'name':name}, function(data){
        var rdata = $.parseJSON(data.data);
        if (rdata['status']){
            onlineEditFile(0, rdata['data']['path']);
        } else {
            layer.msg(rdata.msg,{icon:1,time:2000,shade: [0.3, '#000']});
        }        
    });
}

function projectScriptLoad(user,name){
    gogsPost('project_script_load', {'user':user,'name':name}, function(data){
        if (data.data != 'ok'){
            layer.msg(data.data,{icon:0,time:2000,shade: [0.3, '#000']});
            return;
        }

        layer.msg('加载成功!',{icon:1,time:2000,shade: [0.3, '#000']});
        setTimeout(function(){
            userProjectList(1);
        }, 2000);
    });
}

function projectScriptUnload(user,name){
    gogsPost('project_script_unload', {'user':user,'name':name}, function(data){
        if (data.data != 'ok'){
            layer.msg(data.data,{icon:0,time:2000,shade: [0.3, '#000']});
            return;
        }

        layer.msg('卸载成功!',{icon:1,time:2000,shade: [0.3, '#000']});
        setTimeout(function(){
            userProjectList(1);
        }, 2000);
    });
} 

function projectScriptDebug(user,name){
    gogsPost('project_script_debug', {'user':user,'name':name}, function(data){
        var rdata = $.parseJSON(data.data);
        if (rdata['status']){
            onlineEditFile(0, rdata['path']);
        } else {
            layer.msg(rdata.msg,{icon:1,time:2000,shade: [0.3, '#000']});
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

function gogsRead(){

    var readme = '<ul class="help-info-text c7">';
    readme += '<li>默认使用MySQL,第一个启动加载各种配置,并修改成正确的数据库配置</li>';
    readme += '<li>邮件端口使用456,gogs仅支持使用STARTTLS的SMTP协议</li>';
    readme += '<li>如果使用项目中脚本本地同步,<a target="_blank" href="https://github.com/midoks/mdserver-web/wiki/%E6%8F%92%E4%BB%B6%E7%AE%A1%E7%90%86%5Bgogs%E4%BD%BF%E7%94%A8%E8%AF%B4%E6%98%8E%5D#%E5%90%AF%E5%8A%A8gogs%E5%90%8E%E5%A6%82%E6%9E%9C%E8%A6%81%E4%BD%BF%E7%94%A8hook%E8%84%9A%E6%9C%AC%E5%90%8C%E6%AD%A5%E4%BB%A3%E7%A0%81%E9%9C%80%E8%A6%81%E5%BC%80%E5%90%AFssh%E7%AB%AF%E5%8F%A3">点击查看</></li>';
    readme += '<li><a href="#" onclick="getRsaPublic();">点击查看本机公钥</></li>';
    readme += '</ul>';

    $('.soft-man-con').html(readme);   
}