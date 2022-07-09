function mongoStatus() {
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });
    $.post('/plugins/run', {name:'mongodb', func:'run_info'}, function(data) {
    	layer.close(loadT);
    	if (!data.status){
    		layer.msg(data.msg,{icon:0,time:2000,shade: [0.3, '#000']});
    		return;
    	}

    	var rdata = $.parseJSON(data.data);
        hit = (parseInt(rdata.keyspace_hits) / (parseInt(rdata.keyspace_hits) + parseInt(rdata.keyspace_misses)) * 100).toFixed(2);
        var Con = '<div class="divtable">\
						<table class="table table-hover table-bordered" style="width: 490px;">\
						<thead><th>字段</th><th>当前值</th><th>说明</th></thead>\
						<tbody>\
							<tr><th>version</th><td>' + rdata.version + '</td><td>版本</td></tr>\
							<tr><th>db_path</th><td>' + rdata.db_path + '</td><td>数据路径</td></tr>\
							<tr><th>uptime</th><td>' + rdata.uptime + '</td><td>已运行秒</td></tr>\
							<tr><th>connections</th><td>' + rdata.connections + '</td><td>当前链接数</td></tr>\
							<tr><th>collections</th><td>' + rdata.collections + '</td><td>文档数</td></tr>\
						<tbody>\
				</table></div><hr/>';

		var t = '';
		for(var i=0; i<rdata.dbs.length;i++){
			t += '<tr>';
			t += '<th>'+rdata.dbs[i]["db"]+'</th>';
			t += '<th>'+toSize(rdata.dbs[i]["totalSize"])+'</th>';
			t += '<th>'+toSize(rdata.dbs[i]["storageSize"])+'</th>';
			t += '<th>'+toSize(rdata.dbs[i]["dataSize"])+'</th>';
			t += '<th>'+toSize(rdata.dbs[i]["indexSize"])+'</th>';
			t += '<th>'+rdata.dbs[i]["indexes"]+'</th>';
			t += '<th>'+rdata.dbs[i]["objects"]+'</th>';
			t += '</tr>';
		}
		// console.log(t);

		Con += '<div class="divtable">\
						<table class="table table-hover table-bordered" style="width: 490px;">\
						<thead><th>库名</th><th>大小</th><th>存储大小</th><th>数据</th><th>索引</th><th>文档数据</th><th>对象</th></thead>\
						<tbody>'+t+'<tbody>\
				</table></div>';
		// console.log(rdata.dbs);

        $(".soft-man-con").html(Con);
    },'json');
}