pluginService('csvn');

function csvnPost(method,args,callback){
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });
    $.post('/plugins/run', {name:'csvn', func:method, args:JSON.stringify(args)}, function(data) {
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



function csvnEdit(){

    csvnPost('csvn_edit',{} , function(data){
        // console.log(data);
        var rdata = $.parseJSON(data.data);
        var edit = '<p class="status">通用的手动编辑:</p>';
        edit +='<div class="sfm-opt">\
                <button class="btn btn-default btn-sm" onclick="onlineEditFile(0,\''+rdata['svn_access_file']+'\');">权限编辑</button>\
                <button class="btn btn-default btn-sm" onclick="onlineEditFile(0,\''+rdata['post_commit_tpl']+'\');">post_commit_tpl</button>\
                <button class="btn btn-default btn-sm" onclick="onlineEditFile(0,\''+rdata['commit_tpl']+'\');">commit_tpl</button>\
            </div>'; 
        $(".soft-man-con").html(edit);
    });
    
}


function csvnUserFind(){
    var search = $('#csvn_find_user').val();
    if (search==''){
        layer.msg('搜索字符不能为空!',{icon:0,time:2000,shade: [0.3, '#000']});
        return;
    }
    csvnUserList(1, search);
}

function csvnUserList(page, search) {

    var _data = {};
    if (typeof(page) =='undefined'){
        var page = 1;
    }
    
    _data['page'] = page;
    _data['page_size'] = 10;
    if(typeof(search) != 'undefined'){
        _data['search'] = search;
    }

    csvnPost('user_list', _data, function(data){

        var rdata = $.parseJSON(data.data);
        // console.log(rdata);
        content = '<div class="finduser"><input class="bt-input-text mr5 outline_no" type="text" placeholder="查找用户名" id="csvn_find_user" style="height: 28px; border-radius: 3px;width: 505px;">';
        content += '<button class="btn btn-success btn-sm" onclick="csvnUserFind();">查找</button></div>';

        content += '<div class="divtable" style="margin-top:5px;"><table class="table table-hover" width="100%" cellspacing="0" cellpadding="0" border="0">';
        content += '<thead><tr>';
        content += '<th>用户名</th>';
        content += '<th>操作(<a class="btlink" onclick="csvnAddUser();">添加</a>)</th>';
        content += '</tr></thead>';

        content += '<tbody>';

        ulist = rdata.data;
        for (i in ulist){
            content += '<tr><td>'+ulist[i]+'</td><td>'+
                '<a class="btlink" onclick="csvnDelUser(\''+ulist[i]+'\')">删除</a> | ' +
                '<a class="btlink" onclick="csvnModPwdUser(\''+ulist[i]+'\')">改密</a></td></tr>';
        }

        content += '</tbody>';
        content += '</table></div>';

        page = '<div class="dataTables_paginate paging_bootstrap pagination" style="margin-top:0px;"><ul id="softPage" class="page"><div>';
        page += rdata.list;
        page += '</div></ul></div>';

        content += page;

        $(".soft-man-con").html(content);
    });
}

function csvnDelUser(name){
    var loadOpen = layer.open({
        type: 1,
        title: '删除用户',
        area: '350px',
        content:"<div class='bt-form pd20 pb70 c6'>\
            <div class='version line'>你要确认要删除"+ name + "账户?</div>\
            <div class='bt-form-submit-btn'>\
                <button type='button' id='csvn_del_close' class='btn btn-danger btn-sm btn-title'>关闭</button>\
                <button type='button' id='csvn_del_ok' class='btn btn-success btn-sm btn-title bi-btn'>确认</button>\
            </div>\
        </div>"
    });

    $('#csvn_del_close').click(function(){
        layer.close(loadOpen);
    });

    $('#csvn_del_ok').click(function(){
        _data = {};
        _data['username'] = name;
        var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });
        $.post('/plugins/run', {name:'csvn', func:'user_del', args:JSON.stringify(_data)}, function(data) {
            layer.close(loadT);
            if (!data.status){
                layer.msg(data.data,{icon:0,time:2000,shade: [0.3, '#000']});
                return;
            }

            if (data.data !='ok'){
                layer.msg(data.data,{icon:2,time:2000,shade: [0.3, '#000']});
            }

            layer.close(loadOpen);
            layer.msg("删除成功!",{icon:1,time:3000,shade: [0.3, '#000']});

        },'json');
    });
}

function csvnAddUser(username){

    user_input = ''
    if (typeof(username) == 'undefined'){
        user_input = "<div><input class='bt-input-text mr5 outline_no' type='text' id='csvn_username' name='username' style='height: 28px; border-radius: 3px;width: 200px;' placeholder='输入用户名'></div>";
    } else {
        user_input = "<div><input value='"+ username +"' class='bt-input-text mr5 outline_no' type='text' id='csvn_username' name='username' style='height: 28px; border-radius: 3px;width: 200px;' disabled='true'></div>";
    }

    var loadOpen = layer.open({
        type: 1,
        title: '添加用户',
        area: '240px',
        content:"<div class='bt-form pd20 pb70 c6'>\
            <div class='version line'>\
            "+user_input+"\
            <div style='padding-top:3px;'><input class='bt-input-text mr5 outline_no' type='text' id='csvn_password' name='password' style='height: 28px; border-radius: 3px;width: 200px;' placeholder='输入密码'></div>\
            </div>\
            <div class='bt-form-submit-btn'>\
                <button type='button' id='csvn_add_close' class='btn btn-danger btn-sm btn-title'>关闭</button>\
                <button type='button' id='csvn_add_ok' class='btn btn-success btn-sm btn-title bi-btn'>确认</button>\
            </div>\
        </div>"
    });

    $('#csvn_add_close').click(function(){
        layer.close(loadOpen);
    });

    $('#csvn_add_ok').click(function(){
        _data = {};

        _data['username'] = $('#csvn_username').val();
        _data['password'] = $('#csvn_password').val();

        var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });
        $.post('/plugins/run', {name:'csvn', func:'user_add', args:JSON.stringify(_data)}, function(data) {
            layer.close(loadT);
            if (!data.status){
                layer.msg(data.data,{icon:0,time:2000,shade: [0.3, '#000']});
                return;
            }

            if (data.data !='ok'){
                layer.msg(data.data,{icon:2,time:2000,shade: [0.3, '#000']});
            }

            csvnUserList();
            layer.close(loadOpen);
            layer.msg("操作成功!",{icon:1,time:3000,shade: [0.3, '#000']});
        },'json');
    });
}

function csvnModPwdUser(name){
    csvnAddUser(name);
}

function csvnProjectFind(){
    var search = $('#csvn_project_find').val();
    if (search == ''){
         layer.msg('查找字符不能为空!',{icon:0,time:2000,shade: [0.3, '#000']});
         return;
    }

    csvnProjectList(1, search);
}

function csvnProjectList(page, search){
    var _data = {};
    _data['page_size'] = 10;
    if (typeof(search) != 'undefined'){
         _data['search'] = search;
    }

    if (typeof(page) != 'undefined'){
         _data['page'] = page;
         setCookie('csvnProjectListPage',page);
    } else {
        _data['page'] = 1;
        cookie_page = getCookie('csvnProjectListPage')
        if (cookie_page >0){
            _data['page'] = cookie_page;
        }
    }

    csvnPost('project_list', _data, function(data){

        var rdata = $.parseJSON($.trim(data.data));
        var csvn_mg = project_url = 'http://' +rdata['ip'] +(rdata['csvn_port'] == '80' ? '': ':'+rdata['csvn_port']);

        content = '<div><input class="bt-input-text mr5" type="text" placeholder="查找项目" id="csvn_project_find" style="height: 28px; border-radius: 3px;width: 505px;">';
        content += '<button class="btn btn-success btn-sm" onclick="csvnProjectFind();">查找</button></div>';

        content += '<div class="divtable" style="margin-top:5px;"><table class="table table-hover" width="100%" cellspacing="0" cellpadding="0" border="0">';
        content += '<thead><tr>';
        content += '<th>项目名</th>';
        content += '<th>地址</th>';
        content += '<th>操作(<a class="btlink" onclick="csvnAddProject();">添加</a>) | <a class="btlink" target="_blank" href="'+csvn_mg+'">后台管理</a> </th>';
        content += '</tr></thead>';
        content += '<tbody>';

        // console.log(rdata);
        ulist = rdata.data;
        for (i in ulist){
            var project_url = 'http://' +rdata['ip'] +(rdata['port'] == '80' ? '': ':'+rdata['port'])+ '/svn/'+ulist[i]['name'];
            var code_url = 'http://' +rdata['ip'] +(rdata['port'] == '80' ? '': ':'+rdata['port'])+ '/viewvc/'+ulist[i]['name'];
            content += '<tr><td>'+ulist[i]['name']+'</td>'+
                '<td>'+project_url+'</td><td>'+
                '<a class="btlink" onclick="csvnDelProject(\''+ulist[i]['name']+'\')">删除</a> | ' +
                '<a class="btlink" onclick="csvnAclProject(\''+ulist[i]['name']+'\')">权限</a> | ' +
                '<a class="btlink" target="_blank" href="' + code_url +'">源码</a> | ' +
                '<a class="btlink" onclick="csvnProjectScript(\''+ulist[i]['name']+'\','+ ulist[i]['has_hook']+')">脚本</a>' +
                '</td></tr>';
        }

        content += '</tbody>';
        content += '</table></div>';

        page = '<div class="dataTables_paginate paging_bootstrap pagination" style="margin-top:0px;"><ul id="softPage" class="page"><div>';
        page += rdata.list;
        page += '</div></ul></div>';

        content += page;
        $(".soft-man-con").html(content);
    });
}

function csvnDelProject(name){
    var loadOpen = layer.open({
        type: 1,
        title: '删除用户',
        area: '350px',
        content:"<div class='bt-form pd20 pb70 c6'>\
            <div class='version line'>你要确认要删除"+ name + "账户?</div>\
            <div class='bt-form-submit-btn'>\
                <button type='button' id='csvn_del_close' class='btn btn-danger btn-sm btn-title'>关闭</button>\
                <button type='button' id='csvn_del_ok' class='btn btn-success btn-sm btn-title bi-btn'>确认</button>\
            </div>\
        </div>"
    });

    $('#csvn_del_close').click(function(){
        layer.close(loadOpen);
    });

    $('#csvn_del_ok').click(function(){
        var _data = {};
        _data['name'] = name;
        var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });
        $.post('/plugins/run', {name:'csvn', func:'project_del', args:JSON.stringify(_data)}, function(data) {
            layer.close(loadT);
            if (!data.status){
                layer.msg(data.data,{icon:0,time:2000,shade: [0.3, '#000']});
                return;
            }

            if (data.data !='ok'){
                layer.msg(data.data,{icon:2,time:2000,shade: [0.3, '#000']});
                return;
            }

            csvnProjectList();
            layer.close(loadOpen);
            layer.msg("删除成功!",{icon:1,time:3000,shade: [0.3, '#000']});
        },'json');
    });
}

function csvnAddProject(){

    var loadOpen = layer.open({
        type: 1,
        title: '添加项目',
        area: '240px',
        content:"<div class='bt-form pd20 pb70 c6'>\
            <div class='version line'>\
            <div><input class='bt-input-text mr5 outline_no' type='text' id='csvn_name' name='username' style='height: 28px; border-radius: 3px;width: 200px;' placeholder='输入项目名'></div>\
            </div>\
            <div class='bt-form-submit-btn'>\
                <button type='button' id='csvn_project_close' class='btn btn-danger btn-sm btn-title'>关闭</button>\
                <button type='button' id='csvn_project_ok' class='btn btn-success btn-sm btn-title bi-btn'>确认</button>\
            </div>\
        </div>"
    });

    $('#csvn_project_close').click(function(){
        layer.close(loadOpen);
    });

    $('#csvn_project_ok').click(function(){
        var _data = {};
        _data['name'] = $('#csvn_name').val();

        csvnPost('project_add', _data, function(data){

            if (data.data !='ok'){
                layer.msg(data.data,{icon:2,time:2000,shade: [0.3, '#000']});
                return;
            }

            csvnProjectList();
            layer.close(loadOpen);
            layer.msg("操作成功!",{icon:1,time:3000,shade: [0.3, '#000']});
        });
    });
}


function csvnProjectScript(pname, has_hook){

    var html = '';
    if (has_hook){
        html += '<button onclick="csvnProjectScriptEdit(\''+pname+'\')" class="btn btn-default btn-sm">手动编辑</button>';
        html += '<button onclick="csvnProjectScriptDebug(\''+pname+'\')" class="btn btn-default btn-sm">调试日志</button>';
        html += '<button onclick="csvnProjectScriptLoad(\''+pname+'\')" class="btn btn-default btn-sm">重新加载</button>';
        html += '<button onclick="csvnProjectScriptUnload(\''+pname+'\')" class="btn btn-default btn-sm">卸载脚本</button>';
    } else {
        html += '<button onclick="csvnProjectScriptLoad(\''+pname+'\')" class="btn btn-default btn-sm">加载脚本</button>';
    }

    var loadOpen = layer.open({
        type: 1,
        title: '脚本设置',
        area: '240px',
        content:'<div class="change-default pd20">'+html+'</div>'
    });
}

function csvnProjectScriptLoad(pname){
    csvnPost('project_script_load', {'pname':pname}, function(data){
        if (data.data != 'ok'){
            layer.msg(data.data,{icon:0,time:2000,shade: [0.3, '#000']});
            return;
        }

        layer.msg('加载成功!',{icon:1,time:2000,shade: [0.3, '#000']});
        setTimeout(function(){
            csvnProjectList();
        },2000);
    });
}

function csvnProjectScriptUnload(pname){
    csvnPost('project_script_unload', {'pname':pname}, function(data){
        if (data.data != 'ok'){
            layer.msg(data.data,{icon:0,time:2000,shade: [0.3, '#000']});
            return;
        }

        layer.msg('卸载成功!',{icon:1,time:2000,shade: [0.3, '#000']});
        setTimeout(function(){
            csvnProjectList();
        },2000);
    });
}

function csvnProjectScriptEdit(pname){
    csvnPost('project_script_edit', {'pname':pname}, function(data){
        var rdata = $.parseJSON(data.data);
        if (rdata['status']){
            onlineEditFile(0, rdata['path']);
            csvnProjectList();
        } else {
            layer.msg(rdata.msg,{icon:1,time:2000,shade: [0.3, '#000']});
        }        
    });
}

function csvnProjectScriptDebug(pname){
    csvnPost('project_script_debug', {'pname':pname}, function(data){
        var rdata = $.parseJSON(data.data);
        if (rdata['status']){
            onlineEditFile(0, rdata['path']);
            csvnProjectList();
        } else {
            layer.msg(rdata.msg,{icon:1,time:2000,shade: [0.3, '#000']});
        }        
    });
}


function csvnAclAdd(pname){
    var uname = $('#csvn_username').val();
    if (uname == ''){
        layer.msg('添加用户名不能为空!',{icon:0,time:2000,shade: [0.3, '#000']});
        return;
    }

    csvnPost('project_acl_add', {'pname':pname,'uname':uname}, function(data){
        if (data.data != 'ok'){
            layer.msg(data.data,{icon:0,time:2000,shade: [0.3, '#000']});
            return;
        }
        $('.layui-layer-close1').click();
        csvnAclProject(pname);
    });
}

function csvnAclDel(pname, uname){
    csvnPost('project_acl_del', {'pname':pname,'uname':uname}, function(data){
        if (data.data != 'ok'){
            layer.msg(data.data,{icon:0,time:2000,shade: [0.3, '#000']});
            return;
        }
        $('.layui-layer-close1').click();
        csvnAclProject(pname);
    });
}

function csvnAclSet(obj, pname, uname, acl, selected){

    if (selected){
        $(obj).prop('checked',true);
        layer.msg('权限没有变化!',{icon:0,time:2000,shade: [0.3, '#000']});
        return;
    }

    csvnPost('project_acl_set', {'pname':pname,'uname':uname, 'acl':acl}, function(data){
        if (data.data != 'ok'){
            layer.msg(data.data,{icon:0,time:2000,shade: [0.3, '#000']});
            return;
        }

        $('.layui-layer-close1').click();
        csvnAclProject(pname);
    });
}

function csvnAclProject(pname){
    csvnPost('project_acl_list', {'name':pname}, function(data){
    
        var rdata = [];
        try {
            rdata = $.parseJSON(data.data);
        } catch(e){}

        var list = '';
        for (i in rdata) {
            var user = rdata[i]['user'];
            var acl = '';
            if (rdata[i]['acl'] == 'r'){
                acl += '<input type="checkbox" onclick="csvnAclSet(this,\''+pname+'\',\''+user+'\',\'r\',true)" checked="true"> 只读  |  <input type="checkbox" onclick="csvnAclSet(this,\''+pname+'\',\''+user+'\',\'rw\', false)"> 读写';
            } else {
                acl += '<input type="checkbox" onclick="csvnAclSet(this,\''+pname+'\',\''+user+'\',\'r\',false)"> 只读  |  <input type="checkbox" onclick="csvnAclSet(this,\''+pname+'\',\''+user+'\',\'rw\',true)" checked="true"> 读写';
            }

            list += '<tr><td>'+user+'</td><td>' + acl +'</td>'+
                '<td><a class="btlink" onclick="csvnAclDel(\''+pname+'\',\''+user+'\')">删除</a></td>'+'</tr>';
        }

        var loadOpen = layer.open({
            type: 1,
            title: '项目('+pname+')权限设置',
            area: '300px',
            content:"<div class='bt-form pd20 c6'>\
                    <div>\
                        <div><input class='bt-input-text mr5 outline_no' type='text' id='csvn_username' name='username' style='height: 28px; border-radius: 3px;width: 205px;' placeholder='用户名'>\
                        <button class='btn btn-success btn-sm' onclick='csvnAclAdd(\""+pname+"\");'>添加</button></div>\
                        <div class='divtable' style='margin-top:5px;'><table class='table table-hover'><thead><tr><th>用户</th><th>权限</th><th>操作</th></tr></thead>\
                        <tbody>"+list+"</tbody>\
                        </table></div>\
                    </div>\
                </div>"
        });
    });
}