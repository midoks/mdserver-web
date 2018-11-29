function redisOp(a, b) {

	var c = "name=" + a + "&func=" + b;
	var d = "";

	switch(b) {
		case "stop":d = '停止';break;
		case "start":d = '启动';break;
		case "restart":d = '重启';break;
		case "reload":d = '重载';break;
	}
	layer.confirm( '您真的要{1}{2}服务吗？'.replace('{1}', d).replace('{2}', a), {icon:3,closeBtn: 2}, function() {
		var e = layer.msg('正在{1}{2}服务,请稍候...'.replace('{1}', d).replace('{2}', a), {icon: 16,time: 0});
		$.post("/plugins/run", c, function(g) {
			layer.close(e);
			
			var f = g.data == 'ok' ? '{1}服务已{2}'.replace('{1}', a).replace('{2}', d):'{1}服务{2}失败!'.replace('{1}', a).replace('{2}', d);
			layer.msg(f, {icon: g.data == 'ok' ? 1 : 2});
			
			if(b != "reload" && g.data == 'ok') {
				if (b == 'start') {
					setRedisService('redis', true);
				} else if (b=='stop'){
					setRedisService('redis', false);
				} else {
				}
			}
			if(g.data != 'ok') {
				layer.msg(g.data, {icon: 2,time: 0,shade: 0.3,shadeClose: true});
			}
		},'json').error(function() {
			layer.close(e);
			layer.msg('操作成功!', {icon: 1});
		});
	})
}

//服务
function setRedisService(name, status){
	var serviceCon ='<p class="status">当前状态：<span>'+(status ? '开启' : '关闭' )+
		'</span><span style="color: '+
		(status?'#20a53a;':'red;')+
		' margin-left: 3px;" class="glyphicon ' + (status?'glyphicon glyphicon-play':'glyphicon-pause')+'"></span></p><div class="sfm-opt">\
			<button class="btn btn-default btn-sm" onclick="redisOp(\''+name+'\',\''+(status?'stop':'start')+'\')">'+(status?'停止':'启动')+'</button>\
			<button class="btn btn-default btn-sm" onclick="redisOp(\''+name+'\',\'restart\')">重启</button>\
			<button class="btn btn-default btn-sm" onclick="redisOp(\''+name+'\',\'reload\')">重载配置</button>\
		</div>'; 
	$(".soft-man-con").html(serviceCon);
}


//服务
function redisService(){

	$.post('/plugins/run', {name:'redis', func:'status'}, function(data) {
    	console.log(data);
    	if(!data.status){
    		layer.msg(data.msg,{icon:0,time:3000,shade: [0.3, '#000']});
			return;
    	}
    	if (data.data == 'start'){
    		setRedisService('redis', true);
    	} else {
    		setRedisService('redis', false);
    	}
    },'json');
}

redisService();


//配置修改 --- start
function redisConfig(type){

	var con = '<p style="color: #666; margin-bottom: 7px">提示：Ctrl+F 搜索关键字，Ctrl+G 查找下一个，Ctrl+S 保存，Ctrl+Shift+R 查找替换!</p><textarea class="bt-input-text" style="height: 320px; line-height:18px;" id="textBody"></textarea>\
					<button id="OnlineEditFileBtn" class="btn btn-success btn-sm" style="margin-top:10px;">保存</button>\
					<ul class="help-info-text c7 ptb15">\
						<li>此处为redis主配置文件,若您不了解配置规则,请勿随意修改。</li>\
					</ul>';
	$(".soft-man-con").html(con);

	var loadT = layer.msg('配置文件路径获取中...',{icon:16,time:0,shade: [0.3, '#000']});
	$.post('/plugins/run', {name:'redis', func:'conf'},function (data) {
		layer.close(loadT);

		var loadT2 = layer.msg('文件内容获取中...',{icon:16,time:0,shade: [0.3, '#000']});
		var fileName = data.data;
		$.post('/files/get_body', 'path=' + fileName, function(rdata) {
			layer.close(loadT2);
			if (!rdata.status){
				layer.msg(rdata.msg,{icon:0,time:2000,shade: [0.3, '#000']});
				return;
			}
			$("#textBody").empty().text(rdata.data.data);
			$(".CodeMirror").remove();
			var editor = CodeMirror.fromTextArea(document.getElementById("textBody"), {
				extraKeys: {
					"Ctrl-Space": "autocomplete",
					"Ctrl-F": "findPersistent",
					"Ctrl-H": "replaceAll",
					"Ctrl-S": function() {
						redisConfSafe(fileName);
					}
				},
				lineNumbers: true,
				matchBrackets:true,
			});
			editor.focus();
			$(".CodeMirror-scroll").css({"height":"300px","margin":0,"padding":0});
			$("#OnlineEditFileBtn").click(function(){
				$("#textBody").text(editor.getValue());
				redisConfSafe(fileName);
			});
		},'json');
	},'json');
}

//配置保存
function redisConfSafe(fileName) {
    var data = encodeURIComponent($("#textBody").val());
    var encoding = 'utf-8';
    var loadT = layer.msg('保存中...', {
        icon: 16,
        time: 0
    });
    $.post('/files/save_body', 'data=' + data + '&path=' + fileName + '&encoding=' + encoding, function(rdata) {
        layer.close(loadT);
        layer.msg(rdata.msg, {
            icon: rdata.status ? 1 : 2
        });
    },'json');
}
//配置修改 --- end

//redis负载状态  start
function redisStatus() {
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });
    $.post('/plugins/run', {name:'redis', func:'run_info'}, function(data) {
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
							<tr><th>uptime_in_days</th><td>' + rdata.uptime_in_days + '</td><td>已运行天数</td></tr>\
							<tr><th>tcp_port</th><td>' + rdata.tcp_port + '</td><td>当前监听端口</td></tr>\
							<tr><th>connected_clients</th><td>' + rdata.connected_clients + '</td><td>连接的客户端数量</td></tr>\
							<tr><th>used_memory_rss</th><td>' + toSize(rdata.used_memory_rss) + '</td><td>Redis当前占用的系统内存总量</td></tr>\
							<tr><th>used_memory</th><td>' + toSize(rdata.used_memory) + '</td><td>Redis当前已分配的内存总量</td></tr>\
							<tr><th>used_memory_peak</th><td>' + toSize(rdata.used_memory_peak) + '</td><td>Redis历史分配内存的峰值</td></tr>\
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
//redis负载状态 end