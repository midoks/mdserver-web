function redisPost(method, version, args,callback){
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });

    var req_data = {};
    req_data['name'] = 'redis';
    req_data['func'] = method;
    req_data['version'] = version;
 
    if (typeof(args) == 'string'){
        req_data['args'] = JSON.stringify(toArrayObject(args));
    } else {
        req_data['args'] = JSON.stringify(args);
    }

    $.post('/plugins/run', req_data, function(data) {
        layer.close(loadT);
        if (!data.status){
            //错误展示10S
            layer.msg(data.msg,{icon:0,time:2000,shade: [10, '#000']});
            return;
        }

        if(typeof(callback) == 'function'){
            callback(data);
        }
    },'json'); 
}

function redisPostCallbak(method, version, args,callback){
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });

    var req_data = {};
    req_data['name'] = 'redis';
    req_data['func'] = method;
    args['version'] = version;
 
    if (typeof(args) == 'string'){
        req_data['args'] = JSON.stringify(toArrayObject(args));
    } else {
        req_data['args'] = JSON.stringify(args);
    }

    $.post('/plugins/callback', req_data, function(data) {
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

//redis状态  start
function redisStatus(version) {

    redisPost('run_info',version, {},function(data){
        var rdata = $.parseJSON(data.data);

        if ('status' in rdata && !rdata.status){
            layer.msg(rdata.msg,{icon:0,time:2000,shade: [0.3, '#000']});
            return;
        }

        hit = (parseInt(rdata.keyspace_hits) / (parseInt(rdata.keyspace_hits) + parseInt(rdata.keyspace_misses)) * 100).toFixed(2);
        var con = '<div class="divtable">\
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
                </table></div>';
        $(".soft-man-con").html(con);
    });
}

function replStatus(version){
    redisPost('info_replication', version, {},function(data){
        var rdata = $.parseJSON(data.data);

        if ('status' in rdata && !rdata.status){
            layer.msg(rdata.msg,{icon:0,time:2000,shade: [0.3, '#000']});
            return;
        }

        var kv = {
            'role':'角色',
            'master_host':'连接主库HOST',
            'master_port':'连接主库PORT',
            'master_link_status':'连接主库状态',
            'master_last_io_seconds_ago':'上次同步时间',
            'master_sync_in_progress':'正在同步中',
            'slave_read_repl_offset':'从库读取复制位置',
            'slave_repl_offset':'从库复制位置',
            'slave_read_only':'从库是否仅读',
            'replica_announced':'已复制副本',
            'connected_slaves':'连接数量',
            'master_failover_state':'主库故障状态',
            'master_replid':'主库复制ID',
            'master_repl_offset':'主库复制位置',
            'repl_backlog_size':'backlog复制大小',
            'second_repl_offset':'复制位置时间',
            'repl_backlog_first_byte_offset':'第一个字节偏移量',
            'repl_backlog_histlen':'backlog中数据的长度',
            'repl_backlog_active':'开启复制缓冲区',
            'slave_priority':'同步优先级',
        }

        var tbody_text = '';
        for (k in rdata){
            if (k == 'master_replid'){
                tbody_text += '<tr><th>'+k+'</th><td class="overflow_hide" style="width:155px;display: inline-block;border: none;">' + rdata[k] + '</td><td>'+kv[k]+'</td></tr>';
            } else{

                if (k.substring(0,5) == 'slave' && !isNaN(k.substring(5))){
                    tbody_text += '<tr><th>'+k+'</th><td class="overflow_hide" style="width:155px;display: inline-block;border: none;" title="'+rdata[k]+'">' + rdata[k] + '</td><td>从库配置信息</td></tr>';
                } else{
                    tbody_text += '<tr><th>'+k+'</th><td>' + rdata[k] + '</td><td>'+kv[k]+'</td></tr>';
                }

                
            }   
        }

        var con = '<div class="divtable">\
                        <table class="table table-hover table-bordered" style="width: 490px;">\
                        <thead><th style="width:80px;">字段</th><th style="width:90px;">当前值</th><th>说明</th></thead>\
                        <tbody>'+tbody_text+'<tbody>\
                </table></div>';
        $(".soft-man-con").html(con);
    });
}

function clusterStatus(version){
    redisPost('cluster_info', version, {},function(data){
        var rdata = $.parseJSON(data.data);

        if ('status' in rdata && !rdata.status){
            layer.msg(rdata.msg,{icon:0,time:2000,shade: [0.3, '#000']});
            return;
        }

        var kv = {
            'cluster_state':'集群状态',
            'cluster_slots_assigned':'被分配的槽',
            'cluster_slots_ok':'被分配的槽状态',
            'cluster_known_nodes':'知道的节点',
            'cluster_size':'大小',
            'cluster_stats_messages_sent':'发送',
            'cluster_stats_messages_received':'接收',
            'cluster_current_epoch':'集群当前epoch',
            'cluster_my_epoch':'当前我的epoch',
            'cluster_slots_pfail':'处于PFAIL状态的槽数',
            'cluster_slots_fail':'处于FAIL状态的槽数',
            'total_cluster_links_buffer_limit_exceeded':'超出缓冲区总数',
        }

        var tbody_text = '';
        for (k in rdata){
            var desc = k;
            if (k in kv){
                desc = kv[k];
            }

            if (k == 'master_replid'){
                tbody_text += '<tr><th>'+k+'</th><td class="overflow_hide" style="width:155px;display: inline-block;border: none;">' + rdata[k] + '</td><td>'+desc+'</td></tr>';
            } else{
                tbody_text += '<tr><th>'+k+'</th><td>' + rdata[k] + '</td><td>'+desc+'</td></tr>';
            }   
        }

        if (tbody_text == ''){
            tbody_text += '<tr><td colspan="3" style="text-align:center;">无数据/未设置集群</td></tr>';
        }

        var con = '<div class="divtable">\
                        <table class="table table-hover table-bordered" style="width: 490px;">\
                        <thead><th style="width:80px;">字段</th><th style="width:90px;">当前值</th><th>说明</th></thead>\
                        <tbody>'+tbody_text+'<tbody>\
                </table></div>';
        $(".soft-man-con").html(con);
    });
}

function clusterNodes(version){
    redisPost('cluster_nodes', version, {},function(data){
        var rdata = $.parseJSON(data.data);

        if ('status' in rdata && !rdata.status){
            layer.msg(rdata.msg,{icon:0,time:2000,shade: [0.3, '#000']});
            return;
        }

        // console.log(rdata);
        var tbody_text = '';
        for (k in rdata){
            tbody_text += '<tr><td>'+ rdata[k] +'</td></tr>';
        }

        if (tbody_text == ''){
            tbody_text += '<tr><td style="text-align:center;">无数据/未设置集群</td></tr>';
        }

        var con = '<div class="divtable">\
                        <table class="table table-hover table-bordered" style="width: 490px;">\
                        <thead><th style="width:80px;text-align:center;">节点信息</th></thead>\
                        <tbody>'+tbody_text+'<tbody>\
                </table></div>';
        $(".soft-man-con").html(con);
    });
}

//redis状态 end

//配置修改
function getRedisConfig(version) {
    redisPost('get_redis_conf', version,'',function(data){
        // console.log(data);
        var rdata = $.parseJSON(data.data);
        // console.log(rdata);
        var mlist = '';
        for (var i = 0; i < rdata.length; i++) {
            var w = '70'
            if (rdata[i].name == 'error_reporting') w = '250';
            var ibody = '<input style="width: ' + w + 'px;" class="bt-input-text mr5" name="' + rdata[i].name + '" value="' + rdata[i].value + '" type="text" >';
            switch (rdata[i].type) {
                case 0:
                    var selected_1 = (rdata[i].value == 1) ? 'selected' : '';
                    var selected_0 = (rdata[i].value == 0) ? 'selected' : '';
                    ibody = '<select class="bt-input-text mr5" name="' + rdata[i].name + '" style="width: ' + w + 'px;"><option value="1" ' + selected_1 + '>开启</option><option value="0" ' + selected_0 + '>关闭</option></select>'
                    break;
                case 1:
                    var selected_1 = (rdata[i].value == 'On') ? 'selected' : '';
                    var selected_0 = (rdata[i].value == 'Off') ? 'selected' : '';
                    ibody = '<select class="bt-input-text mr5" name="' + rdata[i].name + '" style="width: ' + w + 'px;"><option value="On" ' + selected_1 + '>开启</option><option value="Off" ' + selected_0 + '>关闭</option></select>'
                    break;
            }
            mlist += '<p><span>' + rdata[i].name + '</span>' + ibody + ', <font>' + rdata[i].ps + '</font></p>'
        }
        var con = '<style>.conf_p p{margin-bottom: 2px}</style><div class="conf_p" style="margin-bottom:0">' + mlist + '\
                        <div style="margin-top:10px; padding-right:15px" class="text-right"><button class="btn btn-success btn-sm mr5" onclick="getRedisConfig(\'' + version + '\')">刷新</button>\
                        <button class="btn btn-success btn-sm" onclick="submitConf(\'' + version + '\')">保存</button></div>\
                    </div>'
        $(".soft-man-con").html(con);
    });
}

//提交配置
function submitConf(version) {
    var data = {
        version: version,
        bind: $("input[name='bind']").val(),
        'port': $("input[name='port']").val(),
        'timeout': $("input[name='timeout']").val(),
        maxclients: $("input[name='maxclients']").val(),
        databases: $("input[name='databases']").val(),
        requirepass: $("input[name='requirepass']").val(),
        maxmemory: $("input[name='maxmemory']").val(),
    };

    redisPost('submit_redis_conf', version, data, function(ret_data){
        var rdata = $.parseJSON(ret_data.data);
        layer.msg(rdata.msg, { icon: rdata.status ? 1 : 2 });
    });
}


function redisReadme(){
    var cmd_01 = '/www/server/redis/bin/redis-cli --cluster create 127.0.0.1:6379 127.0.0.1:6380 127.0.0.1:6381 --cluster-replicas 0';
    var cmd_02 = '/www/server/redis/bin/redis-cli --cluster create 127.0.0.1:6379 127.0.0.1:6380 127.0.0.1:6381 127.0.0.1:6382 127.0.0.1:6383 127.0.0.1:6384 --cluster-replicas 1';


    var readme = '<ul class="help-info-text c7">';
    readme += '<li>集群创建1</li>';
    readme += '<li>'+cmd_01+'</li>';
    readme += '<li>集群创建2</li>';
    readme += '<li>'+cmd_02+'</li>';
    readme += '</ul>';

    $('.soft-man-con').html(readme);   
}

