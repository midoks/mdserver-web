
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
        console.log(data);
        var rdata = $.parseJSON(data.data);
        console.log(rdata);
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
        DOMAIN: $("select[name='DOMAIN']").val(),
        ROOT_URL: $("select[name='ROOT_URL']").val(),
        HTTP_ADDR: $("select[name='HTTP_ADDR']").val(),
        HTTP_PORT: $("select[name='HTTP_PORT']").val(),
        START_SSH_SERVER: $("select[name='START_SSH_SERVER']").val() || 'false',
        SSH_PORT: $("select[name='SSH_PORT']").val(),
        ROOT_URL: $("select[name='ROOT_URL']").val(),
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
        // console.log(rdata);
        content = '<div class="finduser"><input class="bt-input-text mr5 outline_no" type="text" placeholder="查找用户名" id="find_user" style="height: 28px; border-radius: 3px;width: 435px;">';
        content += '<button class="btn btn-success btn-sm" onclick="userFind();">查找</button></div>';

        content += '<div class="divtable" style="margin-top:5px;"><table class="table table-hover" width="100%" cellspacing="0" cellpadding="0" border="0">';
        content += '<thead><tr>';
        content += '<th>用户名</th>';
        content += '<th>操作(<a class="btlink" onclick="csvnAddUser();">管理</a>)</th>';
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


function gogsRead(){
    var readme = '<p>* 默认使用MySQL,第一个启动加载各种配置,并修改成正确的数据库配置</p>';
    readme += '<p>* 邮件端口使用456,gogs仅支持使用STARTTLS的SMTP协议</p>';
    $('.soft-man-con').html(readme);   
}