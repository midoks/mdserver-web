pluginService('csvn');


function csvnUserList(page) {
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });
    _data = {};
    _data['page'] = page;
    // _data['page_size'] = 10;
    $.post('/plugins/run', {name:'csvn', func:'user_list', args:JSON.stringify(_data)}, function(data) {
    	console.log(data);
    	layer.close(loadT);
    	if (!data.status){
    		layer.msg(data.msg,{icon:0,time:2000,shade: [0.3, '#000']});
    		return;
    	}

    	var rdata = $.parseJSON(data.data);
    },'json');
}