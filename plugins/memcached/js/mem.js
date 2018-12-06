


//memcached负载状态
function memcachedStatus() {
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });
    $.post('/plugins/run', {name:'memcached', func:'run_info'}, function(data) {
    	layer.close(loadT);

        if (!data.status){
    		showMsg(data.msg, function(){}, null,13000);
    		return;
    	}
        
        var rdata = $.parseJSON(data.data);
        if ($.isEmptyObject(rdata)){
            showMsg('memcached服务没有启动!', function(){}, undefined, 3000);
            return;
        }
        var Con = '<div class="divtable">\
						<table class="table table-hover table-bordered" style="width: 490px;">\
						<thead><th>字段</th><th>当前值</th><th>说明</th></thead>\
						<tbody>\
							<tr><th>BindIP</th><td>' + rdata.bind + '</td><td>监听IP</td></tr>\
							<tr><th>PORT</th><td>' + rdata.port + '</td><td>监听端口</td></tr>\
							<tr><th>CACHESIZE</th><td>' + rdata.cachesize + ' MB</td><td>最大缓存容量</td></tr>\
							<tr><th>MAXCONN</th><td>' + rdata.maxconn + '</td><td>最大连接数限制</td></tr>\
							<tr><th>curr_connections</th><td>' + rdata.curr_connections + '</td><td>当前打开的连接数</td></tr>\
							<tr><th>cmd_get</th><td>' + rdata.cmd_get + '</td><td>GET请求数</td></tr>\
							<tr><th>get_hits</th><td>' + rdata.get_hits + '</td><td>GET命中次数</td></tr>\
							<tr><th>get_misses</th><td>' + rdata.get_misses + '</td><td>GET失败次数</td></tr>\
							<tr><th>hit</th><td>' + rdata.hit.toFixed(2) + '%</td><td>GET命中率</td></tr>\
							<tr><th>curr_items</th><td>' + rdata.curr_items + '</td><td>当前被缓存的数据行数</td></tr>\
							<tr><th>evictions</th><td>' + rdata.evictions + '</td><td>因内存不足而被清理的缓存行数</td></tr>\
							<tr><th>bytes</th><td>' + toSize(rdata.bytes) + '</td><td>当前已使用内存</td></tr>\
							<tr><th>bytes_read</th><td>' + toSize(rdata.bytes_read) + '</td><td>请求总大小</td></tr>\
							<tr><th>bytes_written</th><td>' + toSize(rdata.bytes_written) + '</td><td>发送总大小</td></tr>\
						<tbody>\
				</table></div>'
        $(".soft-man-con").html(Con);
    },'json');
}

//memcached性能调整
function memcachedCache() {
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });
    $.post('/plugins/run', {name:'memcached', func:'run_info'}, function(data) {
        layer.close(loadT);

        if (!data.status){
            showMsg(data.msg, function(){}, null,13000);
            return;
        }
        
        var rdata = $.parseJSON(data.data);
        if ($.isEmptyObject(rdata)){
            showMsg('memcached服务没有启动!', function(){}, undefined, 3000);
            return;
        }

        var memCon = '<div class="conf_p" style="margin-bottom:0">\
						<p><span>BindIP</span><input style="width: 120px;" class="bt-input-text mr5" name="membind" value="' + rdata.bind + '" type="text" ><font>监听IP,请勿随意修改</font></p>\
						<p><span>PORT</span><input style="width: 120px;" class="bt-input-text mr5" max="65535" name="memport" value="' + rdata.port + '" type="number" ><font>监听端口,一般无需修改</font></p>\
						<p><span>CACHESIZE</span><input style="width: 120px;" class="bt-input-text mr5" name="memcachesize" value="' + rdata.cachesize + '" type="number" >MB,<font>缓存大小,建议不要大于512M</font></p>\
						<p><span>MAXCONN</span><input style="width: 120px;" class="bt-input-text mr5" name="memmaxconn" value="' + rdata.maxconn + '" type="number" ><font>最大连接数,建议不要大于40960</font></p>\
						<div style="margin-top:10px; padding-right:230px" class="text-right"><button class="btn btn-success btn-sm" onclick="setMemcachedConf()">保存</button></div>\
					</div>'
        $(".soft-man-con").html(memCon);
    },'json');
}

//memcached提交配置
function setMemcachedConf() {
    var data = {
        ip: $("input[name='membind']").val(),
        port: $("input[name='memport']").val(),
        cachesize: $("input[name='memcachesize']").val(),
        maxconn: $("input[name='memmaxconn']").val()
    }

    if (data.ip.split('.').length < 4) {
        layer.msg('IP地址格式不正确!', { icon: 2 });
        return;
    }

    if (data.port < 1 || data.port > 65535) {
        layer.msg('端口范围不正确!', { icon: 2 });
        return;
    }

    if (data.cachesize < 8) {
        layer.msg('缓存值过小', { icon: 2 });
        return;
    }

    if (data.maxconn < 4) {
        layer.msg('最大连接数过小', { icon: 2 });
        return;
    }

    var loadT = layer.msg('正在保存...', { icon: 16, time: 0, shade: 0.3 });
    $.post('/plugins/run', {name:'memcached', func:'save_conf',args:JSON.stringify(data) }, function(rdata) {
        layer.close(loadT);
        layer.msg(rdata.msg, { icon: rdata.status ? 1 : 2 });
    },'json');
}