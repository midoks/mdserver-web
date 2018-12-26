function gaePost(method,args,callback){
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });
    $.post('/plugins/run', {name:'gae', func:method, args:JSON.stringify(args)}, function(data) {
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

function projectList(page, search){
    var _data = {};
    _data['page_size'] = 10;
    if (typeof(search) != 'undefined'){
         _data['search'] = search;
    }

    if (typeof(page) != 'undefined'){
         _data['page'] = page;
         setCookie('gaeProjectListPage',page);
    } else {
        _data['page'] = 1;
        cookie_page = getCookie('gaeProjectListPage')
        if (cookie_page >0){
            _data['page'] = cookie_page;
        }
    }

    gaePost('project_list', _data, function(data){

        var rdata = $.parseJSON($.trim(data.data));
        // console.log(rdata);

        content = '<div><input class="bt-input-text mr5" type="text" placeholder="查找项目" id="project_find" style="height: 28px; border-radius: 3px;width: 435px;">';
        content += '<button class="btn btn-success btn-sm" onclick="projectListFind();">查找</button></div>';

        content += '<div class="divtable" style="margin-top:5px;"><table class="table table-hover" width="100%" cellspacing="0" cellpadding="0" border="0">';
        content += '<thead><tr>';
        content += '<th>项目名</th>';
        content += '<th>地址</th>';
        content += '<th>操作</th>';
        content += '</tr></thead>';
        content += '<tbody>';


        ulist = rdata.data;
        for (i in ulist){
            content += '<tr><td>'+ulist[i]['name']+'</td>'+
                '<td>'+ulist[i]['dir']+'</td><td>'+
                '<a class="btlink" onclick="gaeSetProject(\''+ulist[i]['name']+'\')">设置</a> | ' +
                '<a class="btlink" onclick="gaeAsyncProject(\''+ulist[i]['name']+'\')">同步</a> | ' +
                '<a class="btlink" target="_blank" href="' + '' +'">查看命令</a>' +
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

function projectListFind(){
    var search = $('#project_find').val();
    if (search == ''){
         layer.msg('查找字符不能为空!',{icon:0,time:2000,shade: [0.3, '#000']});
         return;
    }
    projectList(1, search);
}

function gaeSetProject(pname){

    var loadOpen = layer.open({
        type: 1,
        title: '项目('+pname+')同步密钥设置',
        area: '600px',
        content:"<div class='bt-form pd20 c6'>\
                <div>\
                    <div class='divtable'>\
                    <table class='table table-hover'>\
                    <thead><tr><th>用户</th><th>权限</th><th>操作</th></tr></thead>\
                    <tbody></tbody>\
                    </table>\
                    </div>\
                    <div class='bt-form-submit-btn'><button type='button' class='btn btn-danger btn-sm btn-title' onclick='layer.closeAll()'>关闭</button>\
                    <button type='button' class='btn btn-success btn-sm btn-title' onclick=';'>确定</button></div>\
                </div>\
            </div>"
    });

    // gaePost('project_list_set', '', function(data){
    //     console.log(data);
    // });
}




