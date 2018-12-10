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

        content = '<div class="finduser"><input class="bt-input-text mr5" type="text" placeholder="查找用户名" id="disable_function_val" style="height: 28px; border-radius: 3px;width: 410px;">';
        content += '<button class="btn btn-success btn-sm">查找</button></div>';

        content += '<div class="divtable" style="margin-top:0px;"><table class="table table-hover" width="100%" cellspacing="0" cellpadding="0" border="0">';
        content += '<thead><tr>';
        content += '<th>用户名</th>';
        content += '<th>操作</th>';
        content += '</tr></thead>';

        content += '<tbody>';

        ulist = rdata.data;
        for (i in ulist){
            content += '<tr><td>'+ulist[i]+'</td><td>'+
                '<a class="btlink" onclick="csvnDelUser(\''+ulist[i]+'\')">删除</a>|' +
                '<a class="btlink" onclick="csvnDelUser(\''+ulist[i]+'\')">改密</a></td></tr>';
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