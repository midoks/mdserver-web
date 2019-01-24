function qbPostMin(method, args, callback){

    var req_data = {};
    req_data['name'] = 'qbittorrent';
    req_data['func'] = method;
 
    if (typeof(args) != 'undefined' && args!=''){
        req_data['args'] = JSON.stringify(args);
    }

    $.post('/plugins/run', req_data, function(data) {
        if (!data.status){
            layer.msg(data.msg,{icon:0,time:2000,shade: [0.3, '#000']});
            return;
        }

        if(typeof(callback) == 'function'){
            callback(data);
        }
    },'json'); 
}

function qbPost(method, args, callback){
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });
    qbPostMin(method,args,function(data){
        layer.close(loadT);
        if(typeof(callback) == 'function'){
            callback(data);
        } 
    });
}

function qbList(page,search){
    var _data = {};
    if (typeof(page) =='undefined'){
        var page = 1;
    }
    
    _data['page'] = page;
    _data['page_size'] = 10;
    if(typeof(search) != 'undefined'){
        _data['search'] = search;
    }

    qbPost('qb_list', _data, function(data){


        var rdata = $.parseJSON(data.data);
        if (!rdata['status']){
            layer.msg(rdata.msg,{icon:0,time:2000,shade: [0.3, '#000']});
            return;
        }
        console.log(rdata);
        content = '';
        // content += '<button class="btn btn-success btn-sm" onclick="csvnUserFind();">查找</button></div>';

        content += '<div class="divtable" style="margin-top:5px;"><table class="table table-hover" width="100%" cellspacing="0" cellpadding="0" border="0">';
        content += '<thead><tr>';
        content += '<th>种子(hash)</th>';
        content += '<th>状态</th>';
        content += '<th>操作(<a class="btlink" onclick="csvnAddUser();">添加</a> | <a class="btlink" onclick="">管理</a>)</th>';
        content += '</tr></thead>';

        content += '<tbody>';

        ulist = rdata.data;
        for (i in ulist){
            content += '<tr><td>'+ulist[i]['hash']+'</td>'+
                '<td>'+'下载中'+'</td>'+
                '<td><a class="btlink" onclick="csvnDelUser(\''+ulist[i]+'\')">删除</a></td></tr>';
        }

        content += '</tbody>';
        content += '</table></div>';

        // page = '<div class="dataTables_paginate paging_bootstrap pagination" style="margin-top:0px;"><ul id="softPage" class="page"><div>';
        // page += rdata.list;
        // page += '</div></ul></div>';

        // content += page;

        $(".soft-man-con").html(content);
    });
}
