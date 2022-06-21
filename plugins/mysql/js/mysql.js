function str2Obj(str){
    var data = {};
    kv = str.split('&');
    for(i in kv){
        v = kv[i].split('=');
        data[v[0]] = v[1];
    }
    return data;
}

function myPost(method,args,callback, title){

    var _args = null; 
    if (typeof(args) == 'string'){
        _args = JSON.stringify(str2Obj(args));
    } else {
        _args = JSON.stringify(args);
    }

    var _title = '正在获取...';
    if (typeof(title) != 'undefined'){
        _title = title;
    }

    var loadT = layer.msg(_title, { icon: 16, time: 0, shade: 0.3 });
    $.post('/plugins/run', {name:'mysql', func:method, args:_args}, function(data) {
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

function myPostN(method,args,callback, title){

    var _args = null; 
    if (typeof(args) == 'string'){
        _args = JSON.stringify(str2Obj(args));
    } else {
        _args = JSON.stringify(args);
    }

    var _title = '正在获取...';
    if (typeof(title) != 'undefined'){
        _title = title;
    }
    $.post('/plugins/run', {name:'mysql', func:method, args:_args}, function(data) {
        if(typeof(callback) == 'function'){
            callback(data);
        }
    },'json'); 
}

function myAsyncPost(method,args){
    var _args = null; 
    if (typeof(args) == 'string'){
        _args = JSON.stringify(str2Obj(args));
    } else {
        _args = JSON.stringify(args);
    }

    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });
    return syncPost('/plugins/run', {name:'mysql', func:method, args:_args}); 
}

function runInfo(){
    myPost('run_info','',function(data){

        var rdata = $.parseJSON(data.data);
        if (typeof(rdata['status']) != 'undefined'){
            layer.msg(rdata['msg'],{icon:0,time:2000,shade: [0.3, '#000']});
            return;
        }

        var cache_size = ((parseInt(rdata.Qcache_hits) / (parseInt(rdata.Qcache_hits) + parseInt(rdata.Qcache_inserts))) * 100).toFixed(2) + '%';
        if (cache_size == 'NaN%') cache_size = 'OFF';
        var Con = '<div class="divtable"><table class="table table-hover table-bordered" style="margin-bottom:10px;background-color:#fafafa">\
                    <tbody>\
                        <tr><th>启动时间</th><td>' + getLocalTime(rdata.Run) + '</td><th>每秒查询</th><td>' + parseInt(rdata.Questions / rdata.Uptime) + '</td></tr>\
                        <tr><th>总连接次数</th><td>' + rdata.Connections + '</td><th>每秒事务</th><td>' + parseInt((parseInt(rdata.Com_commit) + parseInt(rdata.Com_rollback)) / rdata.Uptime) + '</td></tr>\
                        <tr><th>发送</th><td>' + toSize(rdata.Bytes_sent) + '</td><th>File</th><td>' + rdata.File + '</td></tr>\
                        <tr><th>接收</th><td>' + toSize(rdata.Bytes_received) + '</td><th>Position</th><td>' + rdata.Position + '</td></tr>\
                    </tbody>\
                    </table>\
                    <table class="table table-hover table-bordered">\
                    <thead style="display:none;"><th></th><th></th><th></th><th></th></thead>\
                    <tbody>\
                        <tr><th>活动/峰值连接数</th><td>' + rdata.Threads_running + '/' + rdata.Max_used_connections + '</td><td colspan="2">若值过大,增加max_connections</td></tr>\
                        <tr><th>线程缓存命中率</th><td>' + ((1 - rdata.Threads_created / rdata.Connections) * 100).toFixed(2) + '%</td><td colspan="2">若过低,增加thread_cache_size</td></tr>\
                        <tr><th>索引命中率</th><td>' + ((1 - rdata.Key_reads / rdata.Key_read_requests) * 100).toFixed(2) + '%</td><td colspan="2">若过低,增加key_buffer_size</td></tr>\
                        <tr><th>Innodb索引命中率</th><td>' + ((1 - rdata.Innodb_buffer_pool_reads / rdata.Innodb_buffer_pool_read_requests) * 100).toFixed(2) + '%</td><td colspan="2">若过低,增加innodb_buffer_pool_size</td></tr>\
                        <tr><th>查询缓存命中率</th><td>' + cache_size + '</td><td colspan="2">' + lan.soft.mysql_status_ps5 + '</td></tr>\
                        <tr><th>创建临时表到磁盘</th><td>' + ((rdata.Created_tmp_disk_tables / rdata.Created_tmp_tables) * 100).toFixed(2) + '%</td><td colspan="2">若过大,尝试增加tmp_table_size</td></tr>\
                        <tr><th>已打开的表</th><td>' + rdata.Open_tables + '</td><td colspan="2">若过大,增加table_cache_size</td></tr>\
                        <tr><th>没有使用索引的量</th><td>' + rdata.Select_full_join + '</td><td colspan="2">若不为0,请检查数据表的索引是否合理</td></tr>\
                        <tr><th>没有索引的JOIN量</th><td>' + rdata.Select_range_check + '</td><td colspan="2">若不为0,请检查数据表的索引是否合理</td></tr>\
                        <tr><th>排序后的合并次数</th><td>' + rdata.Sort_merge_passes + '</td><td colspan="2">若值过大,增加sort_buffer_size</td></tr>\
                        <tr><th>锁表次数</th><td>' + rdata.Table_locks_waited + '</td><td colspan="2">若值过大,请考虑增加您的数据库性能</td></tr>\
                    <tbody>\
            </table></div>';
        $(".soft-man-con").html(Con);
    });
}


function myDbPos(){
    myPost('my_db_pos','',function(data){
        var con = '<div class="line ">\
            <div class="info-r  ml0">\
            <input id="datadir" name="datadir" class="bt-input-text mr5 port" type="text" style="width:330px" value="'+data.data+'">\
            <span class="glyphicon cursor mr5 glyphicon-folder-open icon_datadir" onclick="changePath(\'datadir\')"></span>\
            <button id="btn_change_path" name="btn_change_path" class="btn btn-success btn-sm mr5 ml5 btn_change_port">迁移</button>\
            </div></div>';
        $(".soft-man-con").html(con);

        $('#btn_change_path').click(function(){
            var datadir = $("input[name='datadir']").val();
            myPost('set_db_pos','datadir='+datadir,function(data){
                var rdata = $.parseJSON(data.data);
                layer.msg(rdata.msg,{icon:rdata.status ? 1 : 5,time:2000,shade: [0.3, '#000']});
            });
        });
    });
}

function myPort(){
    myPost('my_port','',function(data){
        var con = '<div class="line ">\
            <div class="info-r  ml0">\
            <input name="port" class="bt-input-text mr5 port" type="text" style="width:100px" value="'+data.data+'">\
            <button id="btn_change_port" name="btn_change_port" class="btn btn-success btn-sm mr5 ml5 btn_change_port">修改</button>\
            </div></div>';
        $(".soft-man-con").html(con);

        $('#btn_change_port').click(function(){
            var port = $("input[name='port']").val();
            myPost('set_my_port','port='+port,function(data){
                var rdata = $.parseJSON(data.data);
                if (rdata.status){
                    layer.msg('修改成功!',{icon:1,time:2000,shade: [0.3, '#000']});
                } else {
                    layer.msg(rdata.msg,{icon:1,time:2000,shade: [0.3, '#000']});
                }
            });
        });
    });
}


//数据库存储信置
function changeMySQLDataPath(act) {
    if (act != undefined) {
        layer.confirm(lan.soft.mysql_to_msg, { closeBtn: 2, icon: 3 }, function() {
            var datadir = $("#datadir").val();
            var data = 'datadir=' + datadir;
            var loadT = layer.msg(lan.soft.mysql_to_msg1, { icon: 16, time: 0, shade: [0.3, '#000'] });
            $.post('/database?action=SetDataDir', data, function(rdata) {
                layer.close(loadT)
                layer.msg(rdata.msg, { icon: rdata.status ? 1 : 5 });
            });
        });
        return;
    }

    $.post('/database?action=GetMySQLInfo', '', function(rdata) {
        var LimitCon = '<p class="conf_p">\
                            <input id="datadir" class="phpUploadLimit bt-input-text mr5" style="width:350px;" type="text" value="' + rdata.datadir + '" name="datadir">\
                            <span onclick="ChangePath(\'datadir\')" class="glyphicon glyphicon-folder-open cursor mr20" style="width:auto"></span><button class="btn btn-success btn-sm" onclick="changeMySQLDataPath(1)">' + lan.soft.mysql_to + '</button>\
                        </p>';
        $(".soft-man-con").html(LimitCon);
    });
}




//数据库配置状态
function myPerfOpt() {
    //获取MySQL配置
    myPost('db_status','',function(data){
        var rdata = $.parseJSON(data.data);
        // console.log(rdata);
        var key_buffer_size = toSizeM(rdata.mem.key_buffer_size);
        var query_cache_size = toSizeM(rdata.mem.query_cache_size);
        var tmp_table_size = toSizeM(rdata.mem.tmp_table_size);
        var innodb_buffer_pool_size = toSizeM(rdata.mem.innodb_buffer_pool_size);
        var innodb_additional_mem_pool_size = toSizeM(rdata.mem.innodb_additional_mem_pool_size);
        var innodb_log_buffer_size = toSizeM(rdata.mem.innodb_log_buffer_size);

        var sort_buffer_size = toSizeM(rdata.mem.sort_buffer_size);
        var read_buffer_size = toSizeM(rdata.mem.read_buffer_size);
        var read_rnd_buffer_size = toSizeM(rdata.mem.read_rnd_buffer_size);
        var join_buffer_size = toSizeM(rdata.mem.join_buffer_size);
        var thread_stack = toSizeM(rdata.mem.thread_stack);
        var binlog_cache_size = toSizeM(rdata.mem.binlog_cache_size);

        var a = key_buffer_size + query_cache_size + tmp_table_size + innodb_buffer_pool_size + innodb_additional_mem_pool_size + innodb_log_buffer_size;
        var b = sort_buffer_size + read_buffer_size + read_rnd_buffer_size + join_buffer_size + thread_stack + binlog_cache_size;
        var memSize = a + rdata.mem.max_connections * b;


        var memCon = '<div class="conf_p" style="margin-bottom:0">\
                        <div style="border-bottom:#ccc 1px solid;padding-bottom:10px;margin-bottom:10px"><span><b>最大使用内存: </b></span>\
                        <select class="bt-input-text" name="mysql_set" style="margin-left:-4px">\
                            <option value="0">请选择</option>\
                            <option value="1">1-2GB</option>\
                            <option value="2">2-4GB</option>\
                            <option value="3">4-8GB</option>\
                            <option value="4">8-16GB</option>\
                            <option value="5">16-32GB</option>\
                        </select>\
                        <span>' + lan.soft.mysql_set_maxmem + ': </span><input style="width:70px;background-color:#eee;" class="bt-input-text mr5" name="memSize" type="text" value="' + memSize.toFixed(2) + '" readonly>MB\
                        </div>\
                        <p><span>key_buffer_size</span><input style="width: 70px;" class="bt-input-text mr5" name="key_buffer_size" value="' + key_buffer_size + '" type="number" >MB, <font>' + lan.soft.mysql_set_key_buffer_size + '</font></p>\
                        <p><span>query_cache_size</span><input style="width: 70px;" class="bt-input-text mr5" name="query_cache_size" value="' + query_cache_size + '" type="number" >MB, <font>' + lan.soft.mysql_set_query_cache_size + '</font></p>\
                        <p><span>tmp_table_size</span><input style="width: 70px;" class="bt-input-text mr5" name="tmp_table_size" value="' + tmp_table_size + '" type="number" >MB, <font>' + lan.soft.mysql_set_tmp_table_size + '</font></p>\
                        <p><span>innodb_buffer_pool_size</span><input style="width: 70px;" class="bt-input-text mr5" name="innodb_buffer_pool_size" value="' + innodb_buffer_pool_size + '" type="number" >MB, <font>' + lan.soft.mysql_set_innodb_buffer_pool_size + '</font></p>\
                        <p><span>innodb_log_buffer_size</span><input style="width: 70px;" class="bt-input-text mr5" name="innodb_log_buffer_size" value="' + innodb_log_buffer_size + '" type="number">MB, <font>' + lan.soft.mysql_set_innodb_log_buffer_size + '</font></p>\
                        <p style="display:none;"><span>innodb_additional_mem_pool_size</span><input style="width: 70px;" class="bt-input-text mr5" name="innodb_additional_mem_pool_size" value="' + innodb_additional_mem_pool_size + '" type="number" >MB</p>\
                        <p><span>sort_buffer_size</span><input style="width: 70px;" class="bt-input-text mr5" name="sort_buffer_size" value="' + (sort_buffer_size * 1024) + '" type="number" >KB * ' + lan.soft.mysql_set_conn + ', <font>' + lan.soft.mysql_set_sort_buffer_size + '</font></p>\
                        <p><span>read_buffer_size</span><input style="width: 70px;" class="bt-input-text mr5" name="read_buffer_size" value="' + (read_buffer_size * 1024) + '" type="number" >KB * ' + lan.soft.mysql_set_conn + ', <font>' + lan.soft.mysql_set_read_buffer_size + ' </font></p>\
                        <p><span>read_rnd_buffer_size</span><input style="width: 70px;" class="bt-input-text mr5" name="read_rnd_buffer_size" value="' + (read_rnd_buffer_size * 1024) + '" type="number" >KB * ' + lan.soft.mysql_set_conn + ', <font>' + lan.soft.mysql_set_read_rnd_buffer_size + ' </font></p>\
                        <p><span>join_buffer_size</span><input style="width: 70px;" class="bt-input-text mr5" name="join_buffer_size" value="' + (join_buffer_size * 1024) + '" type="number" >KB * ' + lan.soft.mysql_set_conn + ', <font>' + lan.soft.mysql_set_join_buffer_size + '</font></p>\
                        <p><span>thread_stack</span><input style="width: 70px;" class="bt-input-text mr5" name="thread_stack" value="' + (thread_stack * 1024) + '" type="number" >KB * ' + lan.soft.mysql_set_conn + ', <font>' + lan.soft.mysql_set_thread_stack + '</font></p>\
                        <p><span>binlog_cache_size</span><input style="width: 70px;" class="bt-input-text mr5" name="binlog_cache_size" value="' + (binlog_cache_size * 1024) + '" type="number" >KB * ' + lan.soft.mysql_set_conn + ', <font>' + lan.soft.mysql_set_binlog_cache_size + '</font></p>\
                        <p><span>thread_cache_size</span><input style="width: 70px;" class="bt-input-text mr5" name="thread_cache_size" value="' + rdata.mem.thread_cache_size + '" type="number" ><font> ' + lan.soft.mysql_set_thread_cache_size + '</font></p>\
                        <p><span>table_open_cache</span><input style="width: 70px;" class="bt-input-text mr5" name="table_open_cache" value="' + rdata.mem.table_open_cache + '" type="number" > <font>' + lan.soft.mysql_set_table_open_cache + '</font></p>\
                        <p><span>max_connections</span><input style="width: 70px;" class="bt-input-text mr5" name="max_connections" value="' + rdata.mem.max_connections + '" type="number" ><font> ' + lan.soft.mysql_set_max_connections + '</font></p>\
                        <div style="margin-top:10px; padding-right:15px" class="text-right"><button class="btn btn-success btn-sm mr5" onclick="reBootMySqld()">重启数据库</button><button class="btn btn-success btn-sm" onclick="setMySQLConf()">保存</button></div>\
                    </div>'

        $(".soft-man-con").html(memCon);

        $(".conf_p input[name*='size'],.conf_p input[name='max_connections'],.conf_p input[name='thread_stack']").change(function() {
            comMySqlMem();
        });

        $(".conf_p select[name='mysql_set']").change(function() {
            mySQLMemOpt($(this).val());
            comMySqlMem();
        });
    });
}

function reBootMySqld(){
    pluginOpService('mysql','restart','');
}


//设置MySQL配置参数
function setMySQLConf() {
    $.post('/system/system_total', '', function(memInfo) {
        var memSize = memInfo['memTotal'];
        var setSize = parseInt($("input[name='memSize']").val());
        
        if(memSize < setSize){
            var errMsg = "错误,内存分配过高!<p style='color:red;'>物理内存: {1}MB<br>最大使用内存: {2}MB<br>可能造成的后果: 导致数据库不稳定,甚至无法启动MySQLd服务!";
            var msg = errMsg.replace('{1}',memSize).replace('{2}',setSize);
            layer.msg(msg,{icon:2,time:5000});
            return;
        }

        var query_cache_size = parseInt($("input[name='query_cache_size']").val());
        var query_cache_type = 0;
        if (query_cache_size > 0) {
            query_cache_type = 1;
        }
        var data = {
            key_buffer_size: parseInt($("input[name='key_buffer_size']").val()),
            query_cache_size: query_cache_size,
            query_cache_type: query_cache_type,
            tmp_table_size: parseInt($("input[name='tmp_table_size']").val()),
            max_heap_table_size: parseInt($("input[name='tmp_table_size']").val()),
            innodb_buffer_pool_size: parseInt($("input[name='innodb_buffer_pool_size']").val()),
            innodb_log_buffer_size: parseInt($("input[name='innodb_log_buffer_size']").val()),
            sort_buffer_size: parseInt($("input[name='sort_buffer_size']").val()),
            read_buffer_size: parseInt($("input[name='read_buffer_size']").val()),
            read_rnd_buffer_size: parseInt($("input[name='read_rnd_buffer_size']").val()),
            join_buffer_size: parseInt($("input[name='join_buffer_size']").val()),
            thread_stack: parseInt($("input[name='thread_stack']").val()),
            binlog_cache_size: parseInt($("input[name='binlog_cache_size']").val()),
            thread_cache_size: parseInt($("input[name='thread_cache_size']").val()),
            table_open_cache: parseInt($("input[name='table_open_cache']").val()),
            max_connections: parseInt($("input[name='max_connections']").val())
        };

        myPost('set_db_status', data, function(data){
            var rdata = $.parseJSON(data.data);
            showMsg(rdata.msg,function(){
                reBootMySqld();
            },{ icon: rdata.status ? 1 : 2 });
        });
    },'json');
}


//MySQL内存优化方案
function mySQLMemOpt(opt) {
    var query_size = parseInt($("input[name='query_cache_size']").val());
    switch (opt) {
        case '0':
            $("input[name='key_buffer_size']").val(8);
            if (query_size) $("input[name='query_cache_size']").val(4);
            $("input[name='tmp_table_size']").val(8);
            $("input[name='innodb_buffer_pool_size']").val(16);
            $("input[name='sort_buffer_size']").val(256);
            $("input[name='read_buffer_size']").val(256);
            $("input[name='read_rnd_buffer_size']").val(128);
            $("input[name='join_buffer_size']").val(128);
            $("input[name='thread_stack']").val(256);
            $("input[name='binlog_cache_size']").val(32);
            $("input[name='thread_cache_size']").val(4);
            $("input[name='table_open_cache']").val(32);
            $("input[name='max_connections']").val(500);
            break;
        case '1':
            $("input[name='key_buffer_size']").val(128);
            if (query_size) $("input[name='query_cache_size']").val(64);
            $("input[name='tmp_table_size']").val(64);
            $("input[name='innodb_buffer_pool_size']").val(256);
            $("input[name='sort_buffer_size']").val(768);
            $("input[name='read_buffer_size']").val(768);
            $("input[name='read_rnd_buffer_size']").val(512);
            $("input[name='join_buffer_size']").val(1024);
            $("input[name='thread_stack']").val(256);
            $("input[name='binlog_cache_size']").val(64);
            $("input[name='thread_cache_size']").val(64);
            $("input[name='table_open_cache']").val(128);
            $("input[name='max_connections']").val(100);
            break;
        case '2':
            $("input[name='key_buffer_size']").val(256);
            if (query_size) $("input[name='query_cache_size']").val(128);
            $("input[name='tmp_table_size']").val(384);
            $("input[name='innodb_buffer_pool_size']").val(384);
            $("input[name='sort_buffer_size']").val(768);
            $("input[name='read_buffer_size']").val(768);
            $("input[name='read_rnd_buffer_size']").val(512);
            $("input[name='join_buffer_size']").val(2048);
            $("input[name='thread_stack']").val(256);
            $("input[name='binlog_cache_size']").val(64);
            $("input[name='thread_cache_size']").val(96);
            $("input[name='table_open_cache']").val(192);
            $("input[name='max_connections']").val(200);
            break;
        case '3':
            $("input[name='key_buffer_size']").val(384);
            if (query_size) $("input[name='query_cache_size']").val(192);
            $("input[name='tmp_table_size']").val(512);
            $("input[name='innodb_buffer_pool_size']").val(512);
            $("input[name='sort_buffer_size']").val(1024);
            $("input[name='read_buffer_size']").val(1024);
            $("input[name='read_rnd_buffer_size']").val(768);
            $("input[name='join_buffer_size']").val(2048);
            $("input[name='thread_stack']").val(256);
            $("input[name='binlog_cache_size']").val(128);
            $("input[name='thread_cache_size']").val(128);
            $("input[name='table_open_cache']").val(384);
            $("input[name='max_connections']").val(300);
            break;
        case '4':
            $("input[name='key_buffer_size']").val(512);
            if (query_size) $("input[name='query_cache_size']").val(256);
            $("input[name='tmp_table_size']").val(1024);
            $("input[name='innodb_buffer_pool_size']").val(1024);
            $("input[name='sort_buffer_size']").val(2048);
            $("input[name='read_buffer_size']").val(2048);
            $("input[name='read_rnd_buffer_size']").val(1024);
            $("input[name='join_buffer_size']").val(4096);
            $("input[name='thread_stack']").val(384);
            $("input[name='binlog_cache_size']").val(192);
            $("input[name='thread_cache_size']").val(192);
            $("input[name='table_open_cache']").val(1024);
            $("input[name='max_connections']").val(400);
            break;
        case '5':
            $("input[name='key_buffer_size']").val(1024);
            if (query_size) $("input[name='query_cache_size']").val(384);
            $("input[name='tmp_table_size']").val(2048);
            $("input[name='innodb_buffer_pool_size']").val(4096);
            $("input[name='sort_buffer_size']").val(4096);
            $("input[name='read_buffer_size']").val(4096);
            $("input[name='read_rnd_buffer_size']").val(2048);
            $("input[name='join_buffer_size']").val(8192);
            $("input[name='thread_stack']").val(512);
            $("input[name='binlog_cache_size']").val(256);
            $("input[name='thread_cache_size']").val(256);
            $("input[name='table_open_cache']").val(2048);
            $("input[name='max_connections']").val(500);
            break;
    }
}

//计算MySQL内存开销
function comMySqlMem() {
    var key_buffer_size = parseInt($("input[name='key_buffer_size']").val());
    var query_cache_size = parseInt($("input[name='query_cache_size']").val());
    var tmp_table_size = parseInt($("input[name='tmp_table_size']").val());
    var innodb_buffer_pool_size = parseInt($("input[name='innodb_buffer_pool_size']").val());
    var innodb_additional_mem_pool_size = parseInt($("input[name='innodb_additional_mem_pool_size']").val());
    var innodb_log_buffer_size = parseInt($("input[name='innodb_log_buffer_size']").val());

    var sort_buffer_size = $("input[name='sort_buffer_size']").val() / 1024;
    var read_buffer_size = $("input[name='read_buffer_size']").val() / 1024;
    var read_rnd_buffer_size = $("input[name='read_rnd_buffer_size']").val() / 1024;
    var join_buffer_size = $("input[name='join_buffer_size']").val() / 1024;
    var thread_stack = $("input[name='thread_stack']").val() / 1024;
    var binlog_cache_size = $("input[name='binlog_cache_size']").val() / 1024;
    var max_connections = $("input[name='max_connections']").val();

    var a = key_buffer_size + query_cache_size + tmp_table_size + innodb_buffer_pool_size + innodb_additional_mem_pool_size + innodb_log_buffer_size
    var b = sort_buffer_size + read_buffer_size + read_rnd_buffer_size + join_buffer_size + thread_stack + binlog_cache_size
    var memSize = a + max_connections * b
    $("input[name='memSize']").val(memSize.toFixed(2));
}

function syncGetDatabase(){
    myPost('sync_get_databases', null, function(data){
        var rdata = $.parseJSON(data.data);
        showMsg(rdata.msg,function(){
            dbList();
        },{ icon: rdata.status ? 1 : 2 });
    });
}

function syncToDatabase(type){
    var data = [];
    $('input[type="checkbox"].check:checked').each(function () {
        if (!isNaN($(this).val())) data.push($(this).val());
    });
    var postData = 'type='+type+'&ids='+JSON.stringify(data); 
    myPost('sync_to_databases', postData, function(data){
        var rdata = $.parseJSON(data.data);
        // console.log(rdata);
        showMsg(rdata.msg,function(){
            dbList();
        },{ icon: rdata.status ? 1 : 2 });
    });
}

function setRootPwd(type, pwd){
    if (type==1){
        var data = $("#mod_pwd").serialize();
        myPost('set_root_pwd', data, function(data){
            var rdata = $.parseJSON(data.data);
            // console.log(rdata);
            showMsg(rdata.msg,function(){
                dbList();
                $('.layui-layer-close1').click();
            },{icon: rdata.status ? 1 : 2});   
        });
        return;
    }

    var index = layer.open({
        type: 1,
        skin: 'demo-class',
        area: '500px',
        title: '修改数据库密码',
        closeBtn: 1,
        shift: 5,
        shadeClose: true,
        content: "<form class='bt-form pd20 pb70' id='mod_pwd'>\
                    <div class='line'>\
                    <span class='tname'>root密码</span>\
                    <div class='info-r'><input class='bt-input-text mr5' type='text' name='password' id='MyPassword' style='width:330px' value='"+pwd+"' /><span title='随机密码' class='glyphicon glyphicon-repeat cursor' onclick='repeatPwd(16)'></span></div>\
                    </div>\
                    <div class='bt-form-submit-btn'>\
                        <button id='my_mod_close' type='button' class='btn btn-danger btn-sm btn-title'>关闭</button>\
                        <button type='button' class='btn btn-success btn-sm btn-title' onclick=\"setRootPwd(1)\" >提交</button>\
                    </div>\
                  </form>",
    });

    $('#my_mod_close').click(function(){
        $('.layui-layer-close1').click();
    });
}

function showHidePass(obj){
    var a = "glyphicon-eye-open";
    var b = "glyphicon-eye-close";
    
    if($(obj).hasClass(a)){
        $(obj).removeClass(a).addClass(b);
        $(obj).prev().text($(obj).prev().attr('data-pw'))
    }
    else{
        $(obj).removeClass(b).addClass(a);
        $(obj).prev().text('***');
    }
}

function copyPass(password){
    var clipboard = new ClipboardJS('#bt_copys');
    clipboard.on('success', function (e) {
        layer.msg('复制成功',{icon:1,time:2000});
    });

    clipboard.on('error', function (e) {
        layer.msg('复制失败，浏览器不兼容!',{icon:2,time:2000});
    });
    $("#bt_copys").attr('data-clipboard-text',password);
    $("#bt_copys").click();
}

function checkSelect(){
    setTimeout(function () {
        var num = $('input[type="checkbox"].check:checked').length;
        // console.log(num);
        if (num == 1) {
            $('button[batch="true"]').hide();
            $('button[batch="false"]').show();
        }else if (num>1){
            $('button[batch="true"]').show();
            $('button[batch="false"]').show();
        }else{
            $('button[batch="true"]').hide();
            $('button[batch="false"]').hide();
        }
    },5)
}

function setDbAccess(username){
    myPost('get_db_access','username='+username, function(data){
        var rdata = $.parseJSON(data.data);
        if (!rdata.status){
            layer.msg(rdata.msg,{icon:2,shade: [0.3, '#000']});
            return;
        }
        
        var index = layer.open({
            type: 1,
            area: '500px',
            title: '设置数据库权限',
            closeBtn: 1,
            shift: 5,
            shadeClose: true,
            content: "<form class='bt-form pd20 pb70' id='set_db_access'>\
                        <div class='line'>\
                            <span class='tname'>访问权限</span>\
                            <div class='info-r '>\
                                <select class='bt-input-text mr5' name='dataAccess' style='width:100px'>\
                                <option value='127.0.0.1'>本地服务器</option>\
                                <option value=\"%\">所有人</option>\
                                <option value='ip'>指定IP</option>\
                                </select>\
                            </div>\
                        </div>\
                        <div class='bt-form-submit-btn'>\
                            <button id='my_mod_close' type='button' class='btn btn-danger btn-sm btn-title'>关闭</button>\
                            <button id='my_mod_save' type='button' class='btn btn-success btn-sm btn-title'>提交</button>\
                        </div>\
                      </form>",
        });

        layer.ready(function(){
            if (rdata.msg == '127.0.0.1'){
                $('select[name="dataAccess"]').find("option[value='127.0.0.1']").attr("selected",true);
            } else if (rdata.msg == '%'){
                $('select[name="dataAccess"]').find('option[value="%"]').attr("selected",true);
            } else if ( rdata.msg == 'ip' ){
                $('select[name="dataAccess"]').find('option[value="ip"]').attr("selected",true);
                $('select[name="dataAccess"]').after("<input id='dataAccess_subid' class='bt-input-text mr5' type='text' name='address' placeholder='多个IP使用逗号(,)分隔' style='width: 230px; display: inline-block;'>");
            } else {
                $('select[name="dataAccess"]').find('option[value="ip"]').attr("selected",true);
                $('select[name="dataAccess"]').after("<input value='"+rdata.msg+"' id='dataAccess_subid' class='bt-input-text mr5' type='text' name='address' placeholder='多个IP使用逗号(,)分隔' style='width: 230px; display: inline-block;'>");
            }
        });

        $('#my_mod_close').click(function(){
            $('.layui-layer-close1').click();
        });


        $('select[name="dataAccess"]').change(function(){
            var v = $(this).val();
            if (v == 'ip'){
                $(this).after("<input id='dataAccess_subid' class='bt-input-text mr5' type='text' name='address' placeholder='多个IP使用逗号(,)分隔' style='width: 230px; display: inline-block;'>");
            } else {
                $('#dataAccess_subid').remove();
            }
        });

        $('#my_mod_save').click(function(){
            var data = $("#set_db_access").serialize();
            data = decodeURIComponent(data);
            var dataObj = str2Obj(data);
            if(!dataObj['access']){
                dataObj['access'] = dataObj['dataAccess'];
                if ( dataObj['dataAccess'] == 'ip'){
                    if (dataObj['address']==''){
                        layer.msg('IP地址不能空!',{icon:2,shade: [0.3, '#000']});
                        return;
                    }
                    dataObj['access'] = dataObj['address'];
                }
            }
            dataObj['username'] = username;
            // console.log(data,dataObj);
            myPost('set_db_access', dataObj, function(data){
                var rdata = $.parseJSON(data.data);
                showMsg(rdata.msg,function(){
                    dbList();
                    $('.layui-layer-close1').click();
                },{icon: rdata.status ? 1 : 2});   
            });
        });
    });
}

function setDbPass(id, username, password){

    var index = layer.open({
        type: 1,
        skin: 'demo-class',
        area: '500px',
        title: '修改数据库密码',
        closeBtn: 1,
        shift: 5,
        shadeClose: true,
        content: "<form class='bt-form pd20 pb70' id='mod_pwd'>\
                    <div class='line'>\
                        <span class='tname'>用户名</span>\
                        <div class='info-r'><input readonly='readonly' name=\"name\" class='bt-input-text mr5' type='text' style='width:330px;outline:none;' value='"+username+"' /></div>\
                    </div>\
                    <div class='line'>\
                    <span class='tname'>密码</span>\
                    <div class='info-r'><input class='bt-input-text mr5' type='text' name='password' id='MyPassword' style='width:330px' value='"+password+"' /><span title='随机密码' class='glyphicon glyphicon-repeat cursor' onclick='repeatPwd(16)'></span></div>\
                    </div>\
                    <input type='hidden' name='id' value='"+id+"'>\
                    <div class='bt-form-submit-btn'>\
                        <button id='my_mod_close' type='button' class='btn btn-danger btn-sm btn-title'>关闭</button>\
                        <button id='my_mod_save' type='button' class='btn btn-success btn-sm btn-title'>提交</button>\
                    </div>\
                  </form>",
    });

    $('#my_mod_close').click(function(){
        $('.layui-layer-close1').click();
    });

    $('#my_mod_save').click(function(){
        var data = $("#mod_pwd").serialize();
        myPost('set_user_pwd', data, function(data){
            var rdata = $.parseJSON(data.data);
            showMsg(rdata.msg,function(){
                dbList();
                $('.layui-layer-close1').click();
            },{icon: rdata.status ? 1 : 2});   
        });
    });
}

function addDatabase(type){
    if (type==1){
        var data = $("#add_db").serialize();
        data = decodeURIComponent(data);
        var dataObj = str2Obj(data);
        if(!dataObj['address']){
            dataObj['address'] = dataObj['dataAccess'];
        }
        myPost('add_db', dataObj, function(data){
            var rdata = $.parseJSON(data.data);
            showMsg(rdata.msg,function(){
                if (rdata.status){
                    dbList();
                }
                $('.layui-layer-close1').click();
            },{icon: rdata.status ? 1 : 2},600);
        });
        return;
    }
    var index = layer.open({
        type: 1,
        skin: 'demo-class',
        area: '500px',
        title: '添加数据库',
        closeBtn: 1,
        shift: 5,
        shadeClose: true,
        content: "<form class='bt-form pd20 pb70' id='add_db'>\
                    <div class='line'>\
                        <span class='tname'>数据库名</span>\
                        <div class='info-r'><input name='name' class='bt-input-text mr5' placeholder='新的数据库名称' type='text' style='width:65%' value=''>\
                        <select class='bt-input-text mr5 codeing_a5nGsm' name='codeing' style='width:27%'>\
                            <option value='utf8'>utf-8</option>\
                            <option value='utf8mb4'>utf8mb4</option>\
                            <option value='gbk'>gbk</option>\
                            <option value='big5'>big5</option>\
                        </select>\
                        </div>\
                    </div>\
                    <div class='line'><span class='tname'>用户名</span><div class='info-r'><input name='db_user' class='bt-input-text mr5' placeholder='数据库用户' type='text' style='width:65%' value=''></div></div>\
                    <div class='line'>\
                    <span class='tname'>密码</span>\
                    <div class='info-r'><input class='bt-input-text mr5' type='text' name='password' id='MyPassword' style='width:330px' value='"+(randomStrPwd(16))+"' /><span title='随机密码' class='glyphicon glyphicon-repeat cursor' onclick='repeatPwd(16)'></span></div>\
                    </div>\
                    <div class='line'>\
                        <span class='tname'>访问权限</span>\
                        <div class='info-r '>\
                            <select class='bt-input-text mr5' name='dataAccess' style='width:100px'>\
                            <option value='127.0.0.1'>本地服务器</option>\
                            <option value=\"%\">所有人</option>\
                            <option value='ip'>指定IP</option>\
                            </select>\
                        </div>\
                    </div>\
                    <input type='hidden' name='ps' value='' />\
                    <div class='bt-form-submit-btn'>\
                        <button id='my_mod_close' type='button' class='btn btn-danger btn-sm btn-title'>关闭</button>\
                        <button type='button' class='btn btn-success btn-sm btn-title' onclick=\"addDatabase(1)\" >提交</button>\
                    </div>\
                  </form>",
    });

    $("input[name='name']").keyup(function(){
        var v = $(this).val();
        $("input[name='db_user']").val(v);
        $("input[name='ps']").val(v);
    });

    $('#my_mod_close').click(function(){
        $('.layui-layer-close1').click();
    });
    $('select[name="dataAccess"]').change(function(){
        var v = $(this).val();
        if (v == 'ip'){
            $(this).after("<input id='dataAccess_subid' class='bt-input-text mr5' type='text' name='address' placeholder='多个IP使用逗号(,)分隔' style='width: 230px; display: inline-block;'>");
        } else {
            $('#dataAccess_subid').remove();
        }
    });
}

function delDb(id, name){
    safeMessage('删除['+name+']','您真的要删除['+name+']吗？',function(){
        var data='id='+id+'&name='+name
        myPost('del_db', data, function(data){
            var rdata = $.parseJSON(data.data);
            showMsg(rdata.msg,function(){
                dbList();
                $('.layui-layer-close1').click();
            },{icon: rdata.status ? 1 : 2}, 600);
        });
    });
}

function delDbBatch(){
    var arr = [];
    $('input[type="checkbox"].check:checked').each(function () {
        var _val = $(this).val();
        var _name = $(this).parent().next().text();
        if (!isNaN(_val)) {
            arr.push({'id':_val,'name':_name});
        }
    });

    safeMessage('批量删除数据库','<a style="color:red;">您共选择了[2]个数据库,删除后将无法恢复,真的要删除吗?</a>',function(){
        var i = 0;
        $(arr).each(function(){
            var data  = myAsyncPost('del_db', this);
            var rdata = $.parseJSON(data.data);
            if (!rdata.status){
                layer.msg(rdata.msg,{icon:2,time:2000,shade: [0.3, '#000']});
            }
            i++;
        });
        
        var msg = '成功删除['+i+']个数据库!';
        showMsg(msg,function(){
            dbList();
        },{icon: 1}, 600);
    });
}


function setDbPs(id, name, obj) {
    var _span = $(obj);
    var _input = $("<input class='baktext' value=\""+_span.text()+"\" type='text' placeholder='备注信息' />");
    _span.hide().after(_input);
    _input.focus();
    _input.blur(function(){
        $(this).remove();
        var ps = _input.val();
        _span.text(ps).show();
        var data = {name:name,id:id,ps:ps};
        myPost('set_db_ps', data, function(data){
            var rdata = $.parseJSON(data.data);
            layer.msg(rdata.msg, { icon: rdata.status ? 1 : 2 });
        });
    });
    _input.keyup(function(){
        if(event.keyCode == 13){
            _input.trigger('blur');
        }
    });
}

function openPhpmyadmin(name,username,password){

    data = syncPost('/plugins/check',{'name':'phpmyadmin'});
    if (!data.status){
        layer.msg(data.msg,{icon:2,shade: [0.3, '#000']});
        return;
    }

    data = syncPost('/plugins/run',{'name':'phpmyadmin','func':'status'});
    if (data.data != 'start'){
        layer.msg('phpMyAdmin未启动',{icon:2,shade: [0.3, '#000']});
        return;
    }

    data = syncPost('/plugins/run',{'name':'phpmyadmin','func':'get_home_page'});
    var rdata = $.parseJSON(data.data);
    if (!rdata.status){
        layer.msg(rdata.msg,{icon:2,shade: [0.3, '#000']});
        return;
    }
    $("#toPHPMyAdmin").attr('action',rdata.data);

    if($("#toPHPMyAdmin").attr('action').indexOf('phpmyadmin') == -1){
        layer.msg('请先安装phpMyAdmin',{icon:2,shade: [0.3, '#000']});
        setTimeout(function(){ window.location.href = '/soft'; },3000);
        return;
    }

    var murl = $("#toPHPMyAdmin").attr('action');
    $("#pma_username").val(username);
    $("#pma_password").val(password);
    $("#db").val(name);

    layer.msg('正在打开phpMyAdmin',{icon:16,shade: [0.3, '#000'],time:1000});

    setTimeout(function(){
        $("#toPHPMyAdmin").submit();
    },2000);
}

function delBackup(filename,name){
    myPost('delete_db_backup',{filename:filename},function(){
        layer.msg('执行成功!');
        setTimeout(function(){
            $('.layui-layer-close2').click();
            setBackup(name);
        },2000);
    });
}

function downloadBackup(file){
    window.open('/files/download?filename='+encodeURIComponent(file));
}

function importBackup(file,name){
    myPost('import_db_backup',{file:file,name:name}, function(data){
        // console.log(data);
        layer.msg('执行成功!');
    });
}

function setBackup(db_name,obj){
     myPost('get_db_backup_list', {name:db_name}, function(data){

        var rdata = $.parseJSON(data.data);
        var tbody = '';
        for (var i = 0; i < rdata.data.length; i++) {
            tbody += '<tr>\
                    <td><span> ' + rdata.data[i]['name'] + '</span></td>\
                    <td><span> ' + rdata.data[i]['size'] + '</span></td>\
                    <td><span> ' + rdata.data[i]['time'] + '</span></td>\
                    <td style="text-align: right;">\
                        <a class="btlink" onclick="importBackup(\'' + rdata.data[i]['name'] + '\',\'' +db_name+ '\')">导入</a> | \
                        <a class="btlink" onclick="downloadBackup(\'' + rdata.data[i]['file'] + '\')">下载</a> | \
                        <a class="btlink" onclick="delBackup(\'' + rdata.data[i]['name'] + '\',\'' +db_name+ '\')">删除</a>\
                    </td>\
                </tr> ';
        }

        var s = layer.open({
            type: 1,
            title: "数据库备份详情",
            area: ['600px', '280px'],
            closeBtn: 2,
            shadeClose: false,
            content: '<div class="pd15">\
                        <div class="db_list">\
                            <button id="btn_backup" class="btn btn-success btn-sm" type="button">备份</button>\
                        </div >\
                        <div class="divtable">\
                        <div  id="database_fix"  style="height:150px;overflow:auto;border:#ddd 1px solid">\
                        <table class="table table-hover "style="border:none">\
                            <thead>\
                                <tr>\
                                    <th>文件名称</th>\
                                    <th>文件大小</th>\
                                    <th>备份时间</th>\
                                    <th style="text-align: right;">操作</th>\
                                </tr>\
                            </thead>\
                            <tbody class="gztr">' + tbody + '</tbody>\
                        </table>\
                        </div>\
                    </div>\
            </div>'
        });

        $('#btn_backup').click(function(){
            myPost('set_db_backup',{name:db_name}, function(data){
                layer.msg('执行成功!');

                setTimeout(function(){
                    layer.close(s);
                    setBackup(db_name,obj);
                },2000);
            });
        });
    });
}


function dbList(page, search){
    var _data = {};
    if (typeof(page) =='undefined'){
        var page = 1;
    }
    
    _data['page'] = page;
    _data['page_size'] = 10;
    if(typeof(search) != 'undefined'){
        _data['search'] = search;
    }
    myPost('get_db_list', _data, function(data){
        var rdata = $.parseJSON(data.data);
        var list = '';
        for(i in rdata.data){
            list += '<tr>';
            list +='<td><input value="'+rdata.data[i]['id']+'" class="check" onclick="checkSelect();" type="checkbox"></td>';
            list += '<td>' + rdata.data[i]['name'] +'</td>';
            list += '<td>' + rdata.data[i]['username'] +'</td>';
            list += '<td>' + 
                        '<span class="password" data-pw="'+rdata.data[i]['password']+'">***</span>' +
                        '<span onclick="showHidePass(this)" class="glyphicon glyphicon-eye-open cursor pw-ico" style="margin-left:10px"></span>'+
                        '<span class="ico-copy cursor btcopy" style="margin-left:10px" title="复制密码" onclick="copyPass(\''+rdata.data[i]['password']+'\')"></span>'+
                    '</td>';
        

            list += '<td><span class="c9 input-edit" onclick="setDbPs(\''+rdata.data[i]['id']+'\',\''+rdata.data[i]['name']+'\',this)" style="display: inline-block;">'+rdata.data[i]['ps']+'</span></td>';
            list += '<td style="text-align:right">';

            list += '<a href="javascript:;" class="btlink" class="btlink" onclick="setBackup(\''+rdata.data[i]['name']+'\',this)" title="数据库备份">'+(rdata.data[i]['is_backup']?'备份':'未备份') +'</a> | ';

            list += '<a href="javascript:;" class="btlink" onclick="openPhpmyadmin(\''+rdata.data[i]['name']+'\',\''+rdata.data[i]['username']+'\',\''+rdata.data[i]['password']+'\')" title="数据库管理">管理</a> | ' +
                        '<a href="javascript:;" class="btlink" onclick="repTools(\''+rdata.data[i]['name']+'\')" title="MySQL优化修复工具">工具</a> | ' +
                        '<a href="javascript:;" class="btlink" onclick="setDbAccess(\''+rdata.data[i]['username']+'\')" title="设置数据库权限">权限</a> | ' +
                        '<a href="javascript:;" class="btlink" onclick="setDbPass('+rdata.data[i]['id']+',\''+ rdata.data[i]['username'] +'\',\'' + rdata.data[i]['password'] + '\')">改密</a> | ' +
                        '<a href="javascript:;" class="btlink" onclick="delDb(\''+rdata.data[i]['id']+'\',\''+rdata.data[i]['name']+'\')" title="删除数据库">删除</a>' +
                    '</td>';
            list += '</tr>';
        }

        //<button onclick="" id="dataRecycle" title="删除选中项" class="btn btn-default btn-sm" style="margin-left: 5px;"><span class="glyphicon glyphicon-trash" style="margin-right: 5px;"></span>回收站</button>
        var con = '<div class="safe bgw">\
            <button onclick="addDatabase()" title="添加数据库" class="btn btn-success btn-sm" type="button" style="margin-right: 5px;">添加数据库</button>\
            <button onclick="setRootPwd(0,\''+rdata.info['root_pwd']+'\')" title="设置MySQL管理员密码" class="btn btn-default btn-sm" type="button" style="margin-right: 5px;">root密码</button>\
            <button onclick="openPhpmyadmin(\'\',\'root\',\''+rdata.info['root_pwd']+'\')" title="打开phpMyadmin" class="btn btn-default btn-sm" type="button" style="margin-right: 5px;">phpMyAdmin</button>\
            <button onclick="setDbAccess(\'root\')" title="ROOT权限" class="btn btn-default btn-sm" type="button" style="margin-right: 5px;">ROOT权限</button>\
            <span style="float:right">              \
                <button batch="true" style="float: right;display: none;margin-left:10px;" onclick="delDbBatch();" title="删除选中项" class="btn btn-default btn-sm">删除选中</button>\
            </span>\
            <div class="divtable mtb10">\
                <div class="tablescroll">\
                    <table id="DataBody" class="table table-hover" width="100%" cellspacing="0" cellpadding="0" border="0" style="border: 0 none;">\
                    <thead><tr><th width="30"><input class="check" onclick="checkSelect();" type="checkbox"></th>\
                    <th>数据库名</th>\
                    <th>用户名</th>\
                    <th>密码</th>\
                    '+
                    // '<th>备份</th>'+
                    '<th>备注</th>\
                    <th style="text-align:right;">操作</th></tr></thead>\
                    <tbody>\
                    '+ list +'\
                    </tbody></table>\
                </div>\
                 <div id="databasePage" class="dataTables_paginate paging_bootstrap page"></div>\
                <div class="table_toolbar">\
                    <span class="sync btn btn-default btn-sm" style="margin-right:5px" onclick="syncToDatabase(1)" title="将选中数据库信息同步到服务器">同步选中</span>\
                    <span class="sync btn btn-default btn-sm" style="margin-right:5px" onclick="syncToDatabase(0)" title="将所有数据库信息同步到服务器">同步所有</span>\
                    <span class="sync btn btn-default btn-sm" onclick="syncGetDatabase()" title="从服务器获取数据库列表">从服务器获取</span>\
                </div>\
            </div>\
        </div>';

        con += '<form id="toPHPMyAdmin" action="" method="post" style="display: none;" target="_blank">\
            <input type="text" name="pma_username" id="pma_username" value="">\
            <input type="password" name="pma_password" id="pma_password" value="">\
            <input type="text" name="server" value="1">\
            <input type="text" name="target" value="index.php">\
            <input type="text" name="db" id="db" value="">\
        </form>';

        $(".soft-man-con").html(con);
        $('#databasePage').html(rdata.page);

        readerTableChecked();
    });
}


function myLogs(){
    
    myPost('bin_log', {status:1}, function(data){
        var rdata = $.parseJSON(data.data);

        var limitCon = '<p class="conf_p">\
                        <span class="f14 c6 mr20">二进制日志 </span><span class="f14 c6 mr20">' + toSize(rdata.msg) + '</span>\
                        <button class="btn btn-success btn-xs btn-bin va0">'+ (rdata.status ? lan.soft.off : lan.soft.on) + '</button>\
                        <p class="f14 c6 mtb10" style="border-top:#ddd 1px solid; padding:10px 0">错误日志<button class="btn btn-default btn-clear btn-xs" style="float:right;" >清空</button></p>\
                        <textarea readonly style="margin: 0px;width: 100%;height: 440px;background-color: #333;color:#fff; padding:0 5px" id="error_log"></textarea>\
                    </p>'
        $(".soft-man-con").html(limitCon);

        //设置二进制日志
        $(".btn-bin").click(function () {
            myPost('bin_log', 'close=change', function(data){
                var rdata = $.parseJSON(data.data);
                layer.msg(rdata.msg, { icon: rdata.status ? 1 : 5 });
            
                setTimeout(function(){
                    myLogs();
                }, 2000);
            });
        });

         //清空日志
        $(".btn-clear").click(function () {
            myPost('error_log', 'close=1', function(data){
                var rdata = $.parseJSON(data.data);
                layer.msg(rdata.msg, { icon: rdata.status ? 1 : 5 });
            
                setTimeout(function(){
                    myLogs();
                }, 2000);
            });
        })

        myPost('error_log', 'p=1', function(data){
            var rdata = $.parseJSON(data.data);
            var error_body = '';
            if (rdata.status){
                error_body = rdata.data;
            } else {
                error_body = rdata.msg;
            }
            $("#error_log").text(error_body);
            var ob = document.getElementById('error_log');
            ob.scrollTop = ob.scrollHeight;
        });
    });
}


function repCheckeds(tables) {
    var dbs = []
    if (tables) {
        dbs.push(tables)
    } else {
        var db_tools = $("input[value^='dbtools_']");
        for (var i = 0; i < db_tools.length; i++) {
            if (db_tools[i].checked) dbs.push(db_tools[i].value.replace('dbtools_', ''));
        }
    }

    if (dbs.length < 1) {
        layer.msg('请至少选择一张表!', { icon: 2 });
        return false;
    }
    return dbs;
}

function repDatabase(db_name, tables) {
    dbs = repCheckeds(tables);
    
    myPost('repair_table', { db_name: db_name, tables: JSON.stringify(dbs) }, function(data){
        var rdata = $.parseJSON(data.data);
        layer.msg(rdata.msg, { icon: rdata.status ? 1 : 2 });
        repTools(db_name, true);
    },'已送修复指令,请稍候...');
}


function optDatabase(db_name, tables) {
    dbs = repCheckeds(tables);
    
    myPost('opt_table', { db_name: db_name, tables: JSON.stringify(dbs) }, function(data){
        var rdata = $.parseJSON(data.data);
        layer.msg(rdata.msg, { icon: rdata.status ? 1 : 2 });
        repTools(db_name, true);
    },'已送优化指令,请稍候...');
}

function toDatabaseType(db_name, tables, type){
    dbs = repCheckeds(tables);
    myPost('alter_table', { db_name: db_name, tables: JSON.stringify(dbs),table_type: type }, function(data){
        var rdata = $.parseJSON(data.data);
        layer.msg(rdata.msg, { icon: rdata.status ? 1 : 2 });
        repTools(db_name, true);
    }, '已送引擎转换指令,请稍候...');
}


function selectedTools(my_obj, db_name) {
    var is_checked = false

    if (my_obj) is_checked = my_obj.checked;
    var db_tools = $("input[value^='dbtools_']");
    var n = 0;
    for (var i = 0; i < db_tools.length; i++) {
        if (my_obj) db_tools[i].checked = is_checked;
        if (db_tools[i].checked) n++;
    }
    if (n > 0) {
        var my_btns = '<button class="btn btn-default btn-sm" onclick="repDatabase(\'' + db_name + '\',null)">修复</button>\
            <button class="btn btn-default btn-sm" onclick="optDatabase(\'' + db_name + '\',null)">优化</button>\
            <button class="btn btn-default btn-sm" onclick="toDatabaseType(\'' + db_name + '\',null,\'InnoDB\')">转为InnoDB</button></button>\
            <button class="btn btn-default btn-sm" onclick="toDatabaseType(\'' + db_name + '\',null,\'MyISAM\')">转为MyISAM</button>'
        $("#db_tools").html(my_btns);
    } else {
        $("#db_tools").html('');
    }
}

function repTools(db_name, res){
    myPost('get_db_info', {name:db_name}, function(data){
        var rdata = $.parseJSON(data.data);
        var types = { InnoDB: "MyISAM", MyISAM: "InnoDB" };
        var tbody = '';
        for (var i = 0; i < rdata.tables.length; i++) {
            if (!types[rdata.tables[i].type]) continue;
            tbody += '<tr>\
                    <td><input value="dbtools_' + rdata.tables[i].table_name + '" class="check" onclick="selectedTools(null,\'' + db_name + '\');" type="checkbox"></td>\
                    <td><span style="width:220px;"> ' + rdata.tables[i].table_name + '</span></td>\
                    <td>' + rdata.tables[i].type + '</td>\
                    <td><span style="width:90px;"> ' + rdata.tables[i].collation + '</span></td>\
                    <td>' + rdata.tables[i].rows_count + '</td>\
                    <td>' + rdata.tables[i].data_size + '</td>\
                    <td style="text-align: right;">\
                        <a class="btlink" onclick="repDatabase(\''+ db_name + '\',\'' + rdata.tables[i].table_name + '\')">修复</a> |\
                        <a class="btlink" onclick="optDatabase(\''+ db_name + '\',\'' + rdata.tables[i].table_name + '\')">优化</a> |\
                        <a class="btlink" onclick="toDatabaseType(\''+ db_name + '\',\'' + rdata.tables[i].table_name + '\',\'' + types[rdata.tables[i].type] + '\')">转为' + types[rdata.tables[i].type] + '</a>\
                    </td>\
                </tr> '
        }

        if (res) {
            $(".gztr").html(tbody);
            $("#db_tools").html('');
            $("input[type='checkbox']").attr("checked", false);
            $(".tools_size").html('大小：' + rdata.data_size);
            return;
        }

        layer.open({
            type: 1,
            title: "MySQL工具箱【" + db_name + "】",
            area: ['780px', '580px'],
            closeBtn: 2,
            shadeClose: false,
            content: '<div class="pd15">\
                            <div class="db_list">\
                                <span><a>数据库名称：'+ db_name + '</a>\
                                <a class="tools_size">大小：'+ rdata.data_size + '</a></span>\
                                <span id="db_tools" style="float: right;"></span>\
                            </div >\
                            <div class="divtable">\
                            <div  id="database_fix"  style="height:360px;overflow:auto;border:#ddd 1px solid">\
                            <table class="table table-hover "style="border:none">\
                                <thead>\
                                    <tr>\
                                        <th><input class="check" onclick="selectedTools(this,\''+ db_name + '\');" type="checkbox"></th>\
                                        <th>表名</th>\
                                        <th>引擎</th>\
                                        <th>字符集</th>\
                                        <th>行数</th>\
                                        <th>大小</th>\
                                        <th style="text-align: right;">操作</th>\
                                    </tr>\
                                </thead>\
                                <tbody class="gztr">' + tbody + '</tbody>\
                            </table>\
                            </div>\
                        </div>\
                        <ul class="help-info-text c7">\
                            <li>【修复】尝试使用REPAIR命令修复损坏的表，仅能做简单修复，若修复不成功请考虑使用myisamchk工具</li>\
                            <li>【优化】执行OPTIMIZE命令，可回收未释放的磁盘空间，建议每月执行一次</li>\
                            <li>【转为InnoDB/MyISAM】转换数据表引擎，建议将所有表转为InnoDB</li>\
                        </ul></div>'
        });
        tableFixed('database_fix');
    });
}


function setDbMaster(name){
    myPost('set_db_master', {name:name}, function(data){
        var rdata = $.parseJSON(data.data);
        layer.msg(rdata.msg, { icon: rdata.status ? 1 : 5 });
        setTimeout(function(){
            masterOrSlaveConf();
        }, 2000);
    });
}


function setDbSlave(name){
    myPost('set_db_slave', {name:name}, function(data){
        var rdata = $.parseJSON(data.data);
        layer.msg(rdata.msg, { icon: rdata.status ? 1 : 5 });
        setTimeout(function(){
            masterOrSlaveConf();
        }, 2000);
    });
}


function addMasterRepSlaveUser(){

        
    var index = layer.open({
        type: 1,
        skin: 'demo-class',
        area: '500px',
        title: '添加同步账户',
        closeBtn: 1,
        shift: 5,
        shadeClose: true,
        content: "<form class='bt-form pd20 pb70' id='add_master'>\
            <div class='line'><span class='tname'>用户名</span><div class='info-r'><input name='username' class='bt-input-text mr5' placeholder='用户名' type='text' style='width:330px;' value='"+(randomStrPwd(6))+"'></div></div>\
            <div class='line'>\
            <span class='tname'>密码</span>\
            <div class='info-r'><input class='bt-input-text mr5' type='text' name='password' id='MyPassword' style='width:330px' value='"+(randomStrPwd(16))+"' /><span title='随机密码' class='glyphicon glyphicon-repeat cursor' onclick='repeatPwd(16)'></span></div>\
            </div>\
            <input type='hidden' name='ps' value='' />\
            <div class='bt-form-submit-btn'>\
                <button id='my_mod_close' type='button' class='btn btn-danger btn-sm btn-title'>关闭</button>\
                <button type='button' class='btn btn-success btn-sm btn-title' id='submit_add_master' >提交</button>\
            </div>\
          </form>",
    });

    // <div class='line'>\
    //             <span class='tname'>访问权限</span>\
    //             <div class='info-r '>\
    //                 <select class='bt-input-text mr5' name='dataAccess' style='width:100px'>\
    //                 <option value='127.0.0.1'>本地服务器</option>\
    //                 <option value=\"%\">所有人</option>\
    //                 <option value='ip'>指定IP</option>\
    //                 </select>\
    //             </div>\
    //         </div>\

    $("input[name='name']").keyup(function(){
        var v = $(this).val();
        $("input[name='db_user']").val(v);
        $("input[name='ps']").val(v);
    });

    $('#my_mod_close').click(function(){
        $('.layui-layer-close1').click();
    });
    $('select[name="dataAccess"]').change(function(){
        var v = $(this).val();
        if (v == 'ip'){
            $(this).after("<input id='dataAccess_subid' class='bt-input-text mr5' type='text' name='address' placeholder='多个IP使用逗号(,)分隔' style='width: 230px; display: inline-block;'>");
        } else {
            $('#dataAccess_subid').remove();
        }
    });

    $('#submit_add_master').click(function(){

        var data = $("#add_master").serialize();
        data = decodeURIComponent(data);
        var dataObj = str2Obj(data);
        if(!dataObj['address']){
            dataObj['address'] = dataObj['dataAccess'];
        }
        // console.log(dataObj);
        myPost('add_master_rep_slave_user', dataObj, function(data){
            var rdata = $.parseJSON(data.data);
            showMsg(rdata.msg,function(){
                if (rdata.status){
                    getMasterRepSlaveList();
                }
                $('.layui-layer-close1').click();
            },{icon: rdata.status ? 1 : 2},600);
        });
    });
}



function updateMasterRepSlaveUser(username){

        
    var index = layer.open({
        type: 1,
        skin: 'demo-class',
        area: '500px',
        title: '更新账户',
        closeBtn: 1,
        shift: 5,
        shadeClose: true,
        content: "<form class='bt-form pd20 pb70' id='update_master'>\
            <div class='line'><span class='tname'>用户名</span><div class='info-r'><input name='username' readonly='readonly' class='bt-input-text mr5' placeholder='用户名' type='text' style='width:330px;' value='"+username+"'></div></div>\
            <div class='line'>\
            <span class='tname'>密码</span>\
            <div class='info-r'><input class='bt-input-text mr5' type='text' name='password' id='MyPassword' style='width:330px' value='"+(randomStrPwd(16))+"' /><span title='随机密码' class='glyphicon glyphicon-repeat cursor' onclick='repeatPwd(16)'></span></div>\
            </div>\
            <input type='hidden' name='ps' value='' />\
            <div class='bt-form-submit-btn'>\
                <button type='button' class='btn btn-success btn-sm btn-title' id='submit_update_master' >提交</button>\
            </div>\
          </form>",
    });

    $('#submit_update_master').click(function(){
        var data = $("#update_master").serialize();
        data = decodeURIComponent(data);
        var dataObj = str2Obj(data);
        // console.log(dataObj);
        myPost('update_master_rep_slave_user', data, function(data){
            var rdata = $.parseJSON(data.data);
            showMsg(rdata.msg,function(){
                if (rdata.status){
                    getMasterRepSlaveList();
                }
                $('.layui-layer-close1').click();
            },{icon: rdata.status ? 1 : 2},600);
        });
    });
}

function getMasterRepSlaveUserCmd(username, db=''){
    myPost('get_master_rep_slave_user_cmd', {username:username,db:db}, function(data){
        var rdata = $.parseJSON(data.data);

        if (!rdata['status']){
            layer.msg(rdata['msg']);
            return;
        }


        var loadOpen = layer.open({
            type: 1,
            title: '同步命令',
            area: '500px',
            content:"<form class='bt-form pd20 pb70' id='add_master'>\
            <div class='line'>"+rdata.data+"</div>\
            <div class='bt-form-submit-btn'>\
                <button type='button' class='btn btn-success btn-sm btn-title class-copy-cmd'>复制</button>\
            </div>\
          </form>",
        });

        copyPass(rdata.data);
        $('.class-copy-cmd').click(function(){
            copyPass(rdata.data);
        });
    });
}

function delMasterRepSlaveUser(username){
    myPost('del_master_rep_slave_user', {username:username}, function(data){
        var rdata = $.parseJSON(data.data);
        layer.msg(rdata.msg);

        $('.layui-layer-close1').click();

        setTimeout(function(){
            getMasterRepSlaveList();
        },1000);
    });
}

function getMasterRepSlaveList(){
    var _data = {};
    if (typeof(page) =='undefined'){
        var page = 1;
    }
    
    _data['page'] = page;
    _data['page_size'] = 10;
    myPost('get_master_rep_slave_list', _data, function(data){
        // console.log(data);
        var rdata = [];
        try {
            rdata = $.parseJSON(data.data);
        } catch(e){
            console.log(e);
        }
        var list = '';
        // console.log(rdata['data']);
        var user_list = rdata['data'];
        for (i in user_list) {
            // console.log(i);
            var name = user_list[i]['username'];
            list += '<tr><td>'+name+'</td>\
                <td>'+user_list[i]['password']+'</td>\
                <td>\
                    <a class="btlink" onclick="updateMasterRepSlaveUser(\''+name+'\');">修改</a> | \
                    <a class="btlink" onclick="delMasterRepSlaveUser(\''+name+'\');">删除</a> | \
                    <a class="btlink" onclick="getMasterRepSlaveUserCmd(\''+name+'\');">从库同步命令</a>\
                </td>\
            </tr>';
        }

        var page = '<div class="dataTables_paginate_4 dataTables_paginate paging_bootstrap page" style="margin-top:0px;"></div>';
        page += '<div class="table_toolbar"><span class="sync btn btn-default btn-sm" onclick="addMasterRepSlaveUser()" title="">添加同步账户</span></div>';

        var loadOpen = layer.open({
            type: 1,
            title: '同步账户列表',
            area: '500px',
            content:"<div class='bt-form pd20 c6'>\
                     <div class='divtable mtb10'>\
                        <div><table class='table table-hover'>\
                            <thead><tr><th>用户民</th><th>密码</th><th>操作</th></tr></thead>\
                            <tbody>" + list + "</tbody>\
                        </table></div>\
                        "+page +"\
                    </div>\
                </div>"
        });

        $('.dataTables_paginate_4').html(rdata['page']);
    });
}


function deleteSlave(){
    myPost('delete_slave', {}, function(data){
        var rdata = $.parseJSON(data.data);
        layer.msg(rdata['msg']);
        setTimeout(function(){
            masterOrSlaveConf();
        }, 3000);

    });
}


function getFullSyncStatus(db){

    var btn = '<div class="table_toolbar"><span class="sync btn btn-default btn-sm" id="begin_full_sync" title="">开始</span></div>';
    var loadOpen = layer.open({
        type: 1,
        title: '全量同步['+db+']',
        area: '500px',
        content:"<div class='bt-form pd20 c6'>\
                 <div class='divtable mtb10'>\
                    <span id='full_msg'></span>\
                    <div class='progress'>\
                        <div class='progress-bar' role='progressbar' aria-valuenow='0' aria-valuemin='0' aria-valuemax='100' style='min-width: 2em;'>0%</div>\
                    </div>\
                </div>\
                "+btn+"\
            </div>"
    });

    var timeId = setInterval(function(){
        fullSync(db,0);
    }, 1000);

    function fullSync(db,begin){
       
        myPostN('full_sync', {db:db,begin:begin}, function(data){
            var rdata = $.parseJSON(data.data);
            $('#full_msg').text(rdata['msg']);
            $('.progress-bar').css('width',rdata['progress']+'%');
            $('.progress-bar').text(rdata['progress']+'%');

            if (rdata['code']==6 ||rdata['code']<0){
                layer.msg(rdata['msg']);
                clearInterval(timeId);
            }
        });
    }

    fullSync(db,0);
    $('#begin_full_sync').click(function(){
        fullSync(db,1);

        timeId= setTimeout(function(){
            fullSync(db,0);
        }, 1000);
    });

    $('.layui-layer-close1').click(function(){
        clearInterval(timeId);
    });
}

function handlerRun(){
    cmd = 'cd /www/server/mdserver-web && python /www/server/mdserver-web/plugins/mysql/index.py do_full_sync {"db":"all"}';
    var loadOpen = layer.open({
        type: 1,
        title: '手动执行',
        area: '500px',
        content:"<form class='bt-form pd20 pb70' id='add_master'>\
        <div class='line'>"+cmd+"</div>\
        <div class='bt-form-submit-btn'>\
            <button type='button' class='btn btn-success btn-sm btn-title class-copy-cmd'>复制</button>\
        </div>\
      </form>",
    });
    copyPass(cmd);
    $('.class-copy-cmd').click(function(){
        copyPass(cmd);
    });
}

function masterOrSlaveConf(version=''){

    function getMasterDbList(){
        var _data = {};
        if (typeof(page) =='undefined'){
            var page = 1;
        }
        
        _data['page'] = page;
        _data['page_size'] = 10;

        myPost('get_masterdb_list', _data, function(data){
            var rdata = $.parseJSON(data.data);
            var list = '';
            for(i in rdata.data){
                list += '<tr>';
                list += '<td>' + rdata.data[i]['name'] +'</td>';
                list += '<td>' + (rdata.data[i]['master']?'是':'否') +'</td>';
                list += '<td style="text-align:right">' + 
                    '<a href="javascript:;" class="btlink" onclick="setDbMaster(\''+rdata.data[i]['name']+'\')" title="加入或退出">'+(rdata.data[i]['master']?'退出':'加入')+'</a> | ' +
                    '<a href="javascript:;" class="btlink" onclick="getMasterRepSlaveUserCmd(\'\',\''+rdata.data[i]['name']+'\')" title="同步命令">同步命令</a>' +
                '</td>';
                list += '</tr>';
            }

            var con = '<div class="divtable mtb10">\
                    <div class="tablescroll">\
                        <table id="DataBody" class="table table-hover" width="100%" cellspacing="0" cellpadding="0" border="0" style="border: 0 none;">\
                        <thead><tr>\
                        <th>数据库名</th>\
                        <th>同步</th>\
                        <th style="text-align:right;">操作</th></tr></thead>\
                        <tbody>\
                        '+ list +'\
                        </tbody></table>\
                    </div>\
                    <div id="databasePage" class="dataTables_paginate paging_bootstrap page"></div>\
                    <div class="table_toolbar">\
                        <span class="sync btn btn-default btn-sm" onclick="getMasterRepSlaveList()" title="">同步账户列表</span>\
                    </div>\
                </div>';

            $(".table_master_list").html(con);
            $('#databasePage').html(rdata.page);
        });
    }

    function getAsyncMasterDbList(){
        var _data = {};
        if (typeof(page) =='undefined'){
            var page = 1;
        }
        
        _data['page'] = page;
        _data['page_size'] = 10;

        myPost('get_slave_list', _data, function(data){
            var rdata = $.parseJSON(data.data);
            var list = '';
            for(i in rdata.data){
                list += '<tr>';
                list += '<td>' + rdata.data[i]['Master_Host'] +'</td>';
                list += '<td>' + rdata.data[i]['Master_Port'] +'</td>';
                list += '<td>' + rdata.data[i]['Master_User'] +'</td>';
                list += '<td>' + rdata.data[i]['Master_Log_File'] +'</td>';
                list += '<td>' + rdata.data[i]['Slave_IO_Running'] +'</td>';
                list += '<td>' + rdata.data[i]['Slave_SQL_Running'] +'</td>';
                list += '<td style="text-align:right">' + 
                    '<a href="javascript:;" class="btlink" onclick="deleteSlave()" title="删除">删除</a>' +
                '</td>';
                list += '</tr>';
            }

            var con = '<div class="divtable mtb10">\
                    <div class="tablescroll">\
                        <table id="DataBody" class="table table-hover" width="100%" cellspacing="0" cellpadding="0" border="0" style="border: 0 none;">\
                        <thead><tr>\
                        <th>主[服务]</th>\
                        <th>端口</th>\
                        <th>用户</th>\
                        <th>日志</th>\
                        <th>IO</th>\
                        <th>SQL</th>\
                        <th style="text-align:right;">操作</th></tr></thead>\
                        <tbody>\
                        '+ list +'\
                        </tbody></table>\
                    </div>\
                </div>';

            // <div id="databasePage_slave" class="dataTables_paginate paging_bootstrap page"></div>\
            // <div class="table_toolbar">\
            //     <span class="sync btn btn-default btn-sm" onclick="getMasterRepSlaveList()" title="">添加</span>\
            // </div>
            $(".table_slave_status_list").html(con);
        });
    }

    function getAsyncDataList(){
        var _data = {};
        if (typeof(page) =='undefined'){
            var page = 1;
        }
        
        _data['page'] = page;
        _data['page_size'] = 10;
        myPost('get_masterdb_list', _data, function(data){
            var rdata = $.parseJSON(data.data);
            var list = '';
            for(i in rdata.data){
                list += '<tr>';
                list += '<td>' + rdata.data[i]['name'] +'</td>';
                list += '<td style="text-align:right">' + 
                    '<a href="javascript:;" class="btlink" onclick="setDbSlave(\''+rdata.data[i]['name']+'\')"  title="加入|退出">'+(rdata.data[i]['slave']?'退出':'加入')+'</a> | ' +
                    '<a href="javascript:;" class="btlink" onclick="getFullSyncStatus(\''+rdata.data[i]['name']+'\')" title="修复">修复</a>' +
                '</td>';
                list += '</tr>';
            }

            var con = '<div class="divtable mtb10">\
                    <div class="tablescroll">\
                        <table id="DataBody" class="table table-hover" width="100%" cellspacing="0" cellpadding="0" border="0" style="border: 0 none;">\
                        <thead><tr>\
                        <th>本地库名</th>\
                        <th style="text-align:right;">操作</th></tr></thead>\
                        <tbody>\
                        '+ list +'\
                        </tbody></table>\
                    </div>\
                    <div id="databasePage" class="dataTables_paginate paging_bootstrap page"></div>\
                    <div class="table_toolbar">\
                        <span class="sync btn btn-default btn-sm" onclick="handlerRun()" title="免登录设置后,需要手动执行一下!">手动命令</span>\
                        <span class="sync btn btn-default btn-sm" onclick="getFullSyncStatus(\'ALL\')" title="全量同步">全量同步</span>\
                    </div>\
                </div>';

            $(".table_slave_list").html(con);
            $('#databasePage').html(rdata.page);
        });
    }

    function getMasterStatus(){
        myPost('get_master_status', '', function(data){
            var rdata = $.parseJSON(data.data);
            var limitCon = '<p class="conf_p">\
                    <span class="f14 c6 mr20">Master[主]配置</span><span class="f14 c6 mr20"></span>\
                    <button class="btn '+(!rdata.status ? 'btn-danger' : 'btn-success')+' btn-xs btn-master va0">'+(!rdata.status ? '未开启' : '已开启') +'</button><hr/>\
                </p>\
                <!-- master list -->\
                <div class="safe bgw table_master_list"></div>\
                <hr/>\
                <p class="conf_p">\
                    <span class="f14 c6 mr20">Slave[从]配置</span><span class="f14 c6 mr20"></span>\
                    <button class="btn '+(!rdata.data.slave_status ? 'btn-danger' : 'btn-success')+' btn-xs btn-slave va0">'+(!rdata.data.slave_status ? '未启动' : '已启动') +'</button><hr/>\
                </p>\
                <!-- slave status list -->\
                <div class="safe bgw table_slave_status_list"></div>\
                <!-- slave list -->\
                <div class="safe bgw table_slave_list"></div>\
                ';
            $(".soft-man-con").html(limitCon);

            //设置主服务器配置
            $(".btn-master").click(function () {
                myPost('set_master_status', 'close=change', function(data){
                    var rdata = $.parseJSON(data.data);
                    layer.msg(rdata.msg, { icon: rdata.status ? 1 : 5 });
                    setTimeout(function(){
                        getMasterStatus();
                    }, 3000);
                });
            });

            $(".btn-slave").click(function () {
                myPost('set_slave_status', 'close=change', function(data){
                    var rdata = $.parseJSON(data.data);
                    layer.msg(rdata.msg, { icon: rdata.status ? 1 : 5 });
                    setTimeout(function(){
                        getMasterStatus();
                    }, 3000);
                });
            });

            if (rdata.status){
                getMasterDbList();
            }
            
            if (rdata.data.slave_status){
                getAsyncMasterDbList();
                getAsyncDataList()
            }
        });
    }
    getMasterStatus();
}
