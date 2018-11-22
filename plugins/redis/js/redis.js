

//服务
function redisService(name,status){
	if(status == 'false') status = false;
	if(status == 'true') status = true;
	
	var serviceCon ='<p class="status">当前状态：<span>'+(status?lan.soft.on:lan.soft.off)+'</span><span style="color: '+(status?'#20a53a;':'red;')+' margin-left: 3px;" class="glyphicon '+(status?'glyphicon glyphicon-play':'glyphicon-pause')+'"></span></p>\
					<div class="sfm-opt">\
						<button class="btn btn-default btn-sm" onclick="ServiceAdmin(\''+name+'\',\''+(status?'stop':'start')+'\')">'+(status?lan.soft.stop:lan.soft.start)+'</button>\
						<button class="btn btn-default btn-sm" onclick="ServiceAdmin(\''+name+'\',\'restart\')">'+lan.soft.restart+'</button>\
						<button class="btn btn-default btn-sm" onclick="ServiceAdmin(\''+name+'\',\'reload\')">'+lan.soft.reload+'</button>\
					</div>'; 
	$(".soft-man-con").html(serviceCon);
	var help = '<ul class="help-info-text c7 mtb15" style="padding-top:30px"><li>'+lan.soft.mysql_mem_err+'</li></ul>';
	if(name == 'mysqld'){
		$(".soft-man-con").append(help);
	}
}


function redisConfig(){
	console.log('redisConfig');
}


//redis负载状态
function redisStatus() {
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });
    $.post('/plugins/run', {name:'redis', func:'status'}, function(data) {
    	layer.close(loadT);
    	if (!data.status){
    		return;
    	}

    	var rdata = $.parseJSON(data.data);
        hit = (parseInt(rdata.keyspace_hits) / (parseInt(rdata.keyspace_hits) + parseInt(rdata.keyspace_misses)) * 100).toFixed(2);
        var Con = '<div class="divtable">\
						<table class="table table-hover table-bordered" style="width: 490px;">\
						<thead><th>字段</th><th>当前值</th><th>说明</th></thead>\
						<tbody>\
							<tr><th>uptime_in_days</th><td>' + rdata.uptime_in_days + '</td><td>已运行天数</td></tr>\
							<tr><th>tcp_port</th><td>' + rdata.tcp_port + '</td><td>当前监听端口</td></tr>\
							<tr><th>connected_clients</th><td>' + rdata.connected_clients + '</td><td>连接的客户端数量</td></tr>\
							<tr><th>used_memory_rss</th><td>' + ToSize(rdata.used_memory_rss) + '</td><td>Redis当前占用的系统内存总量</td></tr>\
							<tr><th>used_memory</th><td>' + ToSize(rdata.used_memory) + '</td><td>Redis当前已分配的内存总量</td></tr>\
							<tr><th>used_memory_peak</th><td>' + ToSize(rdata.used_memory_peak) + '</td><td>Redis历史分配内存的峰值</td></tr>\
							<tr><th>mem_fragmentation_ratio</th><td>' + rdata.mem_fragmentation_ratio + '%</td><td>内存碎片比率</td></tr>\
							<tr><th>total_connections_received</th><td>' + rdata.total_connections_received + '</td><td>运行以来连接过的客户端的总数量</td></tr>\
							<tr><th>total_commands_processed</th><td>' + rdata.total_commands_processed + '</td><td>运行以来执行过的命令的总数量</td></tr>\
							<tr><th>instantaneous_ops_per_sec</th><td>' + rdata.instantaneous_ops_per_sec + '</td><td>服务器每秒钟执行的命令数量</td></tr>\
							<tr><th>keyspace_hits</th><td>' + rdata.keyspace_hits + '</td><td>查找数据库键成功的次数</td></tr>\
							<tr><th>keyspace_misses</th><td>' + rdata.keyspace_misses + '</td><td>查找数据库键失败的次数</td></tr>\
							<tr><th>hit</th><td>' + hit + '%</td><td>查找数据库键命中率</td></tr>\
							<tr><th>latest_fork_usec</th><td>' + rdata.latest_fork_usec + '</td><td>最近一次 fork() 操作耗费的微秒数</td></tr>\
						<tbody>\
				</table></div>'
        $(".soft-man-con").html(Con);
    },'json');
}

redisService('redis', false);
