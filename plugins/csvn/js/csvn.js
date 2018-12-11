pluginService('csvn');


function csvnUserList(page) {
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });
    _data = {};
    _data['page'] = page;
    _data['page_size'] = 10;
    $.post('/plugins/run', {name:'csvn', func:'user_list', args:JSON.stringify(_data)}, function(data) {
    	layer.close(loadT);
    	
    	if (!data.status){
    		layer.msg(data.msg,{icon:0,time:2000,shade: [0.3, '#000']});
    		return;
    	}

        var rdata = $.parseJSON(data.data);
        // console.log(rdata);

        content = '<div class="finduser"><input class="bt-input-text mr5 outline_no" type="text" placeholder="查找用户名" id="find_user" style="height: 28px; border-radius: 3px;width: 505px;">';
        content += '<button class="btn btn-success btn-sm">查找</button></div>';

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
    },'json');
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

function csvnAddUser(){
    var loadOpen = layer.open({
        type: 1,
        title: '添加用户',
        area: '240px',
        content:"<div class='bt-form pd20 pb70 c6'>\
            <div class='version line'>\
            <div><input class='bt-input-text mr5 outline_no' type='text' id='csvn_username' name='username' style='height: 28px; border-radius: 3px;width: 200px;' placeholder='输入用户名'></div>\
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

            layer.close(loadOpen);
            layer.msg("删除成功!",{icon:1,time:3000,shade: [0.3, '#000']});
        },'json');
    });

}

function csvnModPwdUser(name){
    console.log(name);   
}


function csvnProjectList(page){
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });
    _data = {};
    _data['page'] = page;
    _data['page_size'] = 10;
    $.post('/plugins/run', {name:'csvn', func:'project_list', args:JSON.stringify(_data)}, function(data) {
        layer.close(loadT);
        
        if (!data.status){
            layer.msg(data.msg,{icon:0,time:2000,shade: [0.3, '#000']});
            return;
        }

        var rdata = $.parseJSON(data.data);
        // console.log(rdata);

        content = '<div class="finduser"><input class="bt-input-text mr5" type="text" placeholder="查找项目" id="disable_function_val" style="height: 28px; border-radius: 3px;width: 410px;">';
        content += '<button class="btn btn-success btn-sm">查找</button></div>';

        content += '<div class="divtable" style="margin-top:5px;"><table class="table table-hover" width="100%" cellspacing="0" cellpadding="0" border="0">';
        content += '<thead><tr>';
        content += '<th>项目名</th>';
        content += '<th>操作</th>';
        content += '</tr></thead>';

        content += '<tbody>';

        ulist = rdata.data;
        for (i in ulist){
            content += '<tr><td>'+ulist[i]+'</td><td>'+
                '<a class="btlink" onclick="csvnDelUser(\''+ulist[i]+'\')">删除</a>|' +
                '<a class="btlink" onclick="csvnModUser(\''+ulist[i]+'\')">改密</a></td></tr>';
        }

        content += '</tbody>';
        content += '</table></div>';

        page = '<div class="dataTables_paginate paging_bootstrap pagination" style="margin-top:0px;"><ul id="softPage" class="page"><div>';
        page += rdata.list;
        page += '</div></ul></div>';

        content += page;

        $(".soft-man-con").html(content);
    },'json');
}