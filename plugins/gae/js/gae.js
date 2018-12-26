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
            setName =  ulist[i]['isset'] ? '已设置' : '设置';
            content += '<tr><td>'+ulist[i]['name']+'</td>'+
                '<td>'+ulist[i]['dir']+'</td><td>'+
                '<a class="btlink" onclick="gaeSetProject(\''+ulist[i]['name']+'\','+ulist[i]['isset']+')">'+setName+'</a> | ' +
                '<a class="btlink" onclick="gaeAsyncProject(\''+ulist[i]['name']+'\')">同步</a> | ' +
                '<a class="btlink" target="_blank" onclick="gaeProjectCmd(\''+ulist[i]['name']+'\')">命令</a> | ' +
                '<a class="btlink" target="_blank" onclick="gaeProjectUrl(\''+ulist[i]['name']+'\')">访问</a>' +
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

function gaeSetProject(pname,isset){
    var html = '';
    if (isset){
        html += '<button onclick="gaeProjectDel(\''+pname+'\')" class="btn btn-default btn-sm">删除</button>';
    }
    html += '<button onclick="gaeProjectEdit(\''+pname+'\')" class="btn btn-default btn-sm">编辑</button>';

    var loadOpen = layer.open({
        type: 1,
        title: '['+ pname +']密钥设置',
        area: '240px',
        content:'<div class="change-default pd20">'+html+'</div>'
    });
}

function gaeProjectEdit(pname){
    gaePost('project_list_edit', {'name':pname}, function(data){
        onlineEditFile(0,data.data);
    });
}


function gaeProjectDel(pname){
    gaePost('project_list_del', {'name':pname}, function(data){
        layer.msg('删除成功!',{icon:0,time:2000,shade: [0.3, '#000']});
        projectList();
    });
}

function gaeAsyncProject(pname){
    gaePost('project_list_async', {'name':pname}, function(data){
        console.log(data);
        if (data.data !='ok'){
            layer.msg(data.data,{icon:0,time:2000,shade: [0.3, '#000']});
        } else {
            layer.msg('同步成功!',{icon:0,time:2000,shade: [0.3, '#000']});
        } 
    });
}


function gaeProjectCmd(pname){
    gaePost('project_list_cmd', {'name':pname}, function(data){
        var data_str = data.data;
        if (data_str.indexOf('gcloud') !== -1){
            layer.msg(data.data,{icon:1,time:5000,shade: [0.3, '#000']});
        } else {
            layer.msg(data.data,{icon:0,time:5000,shade: [0.3, '#000']});
        }
    });
}


function gaeProjectUrl(pname){
    gaePost('project_list_url', {'name':pname}, function(data){
        var data_str = data.data;
        if (data_str.indexOf('appspot.com') !== -1){
            window.open(data.data);
        } else {
            layer.msg(data.data,{icon:0,time:5000,shade: [0.3, '#000']});
        }
    });
}




