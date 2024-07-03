
function myPost(method,args,callback, title){

    var _args = null; 
    if (typeof(args) == 'string'){
        _args = JSON.stringify(toArrayObject(args));
    } else {
        _args = JSON.stringify(args);
    }

    var _title = '正在获取...';
    if (typeof(title) != 'undefined'){
        _title = title;
    }

    var loadT = layer.msg(_title, { icon: 16, time: 0, shade: 0.3 });
    $.post('/plugins/run', {name:'mysql-yum', func:method, args:_args}, function(data) {
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
        _args = JSON.stringify(toArrayObject(args));
    } else {
        _args = JSON.stringify(args);
    }

    var _title = '正在获取...';
    if (typeof(title) != 'undefined'){
        _title = title;
    }
    $.post('/plugins/run', {name:'mysql-yum', func:method, args:_args}, function(data) {
        if(typeof(callback) == 'function'){
            callback(data);
        }
    },'json'); 
}

function myAsyncPost(method,args){
    var _args = null; 
    if (typeof(args) == 'string'){
        _args = JSON.stringify(toArrayObject(args));
    } else {
        _args = JSON.stringify(args);
    }

    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });
    return syncPost('/plugins/run', {name:'mysql', func:method, args:_args}); 
}


function myPostCallbak(method, version, args,callback){
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });

    var req_data = {};
    req_data['name'] = 'mysql-yum';
    req_data['func'] = method;
    req_data['script']='index_mysql_yum';
    args['version'] = version;

 
    if (typeof(args) == 'string' && args == ''){
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

function myPostCallbakN(method, version, args,callback){

    var req_data = {};
    req_data['name'] = 'mysql-yum';
    req_data['func'] = method;
    req_data['script']='index_mysql_yum';
    args['version'] = version;

 
    if (typeof(args) == 'string' && args == ''){
        req_data['args'] = JSON.stringify(toArrayObject(args));
    } else {
        req_data['args'] = JSON.stringify(args);
    }

    $.post('/plugins/callback', req_data, function(data) {
        if (!data.status){
            layer.msg(data.msg,{icon:0,time:2000,shade: [0.3, '#000']});
            return;
        }

        if(typeof(callback) == 'function'){
            callback(data);
        }
    },'json'); 
}

function vaildPhpmyadmin(url,username,password){
    // console.log("Authorization: Basic " + btoa(username + ":" + password));
    $.ajax({
        type: "GET",
        url: url,
        dataType: 'json',
        async: false,
        username:username,
        password:password,
        headers: {
            "Authorization": "Basic " + btoa(username + ":" + password)
        },
        data: 'vaild',
        success: function (){
            alert('Thanks for your comment!');
        }
    });
}

function runInfo(){
    myPost('run_info','',function(data){

        var rdata = $.parseJSON(data.data);
        if (typeof(rdata['status']) != 'undefined'){
            layer.msg(rdata['msg'],{icon:0,time:2000,shade: [0.3, '#000']});
            return;
        }

        // Com_select , Qcache_inserts
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
                        <tr><th>Innodb索引命中率</th><td>' + (rdata.Innodb_buffer_pool_read_requests / (rdata.Innodb_buffer_pool_read_requests+rdata.Innodb_buffer_pool_reads)).toFixed(2) + '%</td><td colspan="2">若过低,增加innodb_buffer_pool_size</td></tr>\
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
            <input name="port" class="bt-input-text mr5 port" type="number" style="width:100px" value="'+data.data+'">\
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

//数据库配置状态
function myPerfOpt() {
    //获取MySQL配置
    myPost('db_status','',function(data){
        var rdata = $.parseJSON(data.data);
        if ( typeof(rdata.status) != 'undefined' && !rdata.status){
            layer.msg(rdata.msg, {icon:2});
            return; 
        }


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
    pluginOpService('mysql-yum','restart','');
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
        var password = $("#MyPassword").val();
        myPost('set_root_pwd', {password:password}, function(data){
            var rdata = $.parseJSON(data.data);
            showMsg(rdata.msg,function(){
                dbList();
            },{icon: rdata.status ? 1 : 2});   
        });
        return;
    }

    var index = layer.open({
        type: 1,
        area: '500px',
        title: '修改数据库密码',
        closeBtn: 1,
        shift: 5,
        btn:["提交", "关闭", "复制ROOT密码", "强制修改"],
        shadeClose: true,
        content: "<form class='bt-form pd20' id='mod_pwd'>\
                    <div class='line'>\
                        <span class='tname'>root密码</span>\
                        <div class='info-r'><input class='bt-input-text mr5' type='text' name='password' id='MyPassword' style='width:330px' value='"+pwd+"' />\
                            <span title='随机密码' class='glyphicon glyphicon-repeat cursor' onclick='repeatPwd(16)'></span>\
                        </div>\
                    </div>\
                  </form>",
        yes:function(layerIndex){
            var password = $("#MyPassword").val();
            myPost('set_root_pwd', {password:password}, function(data){
                var rdata = $.parseJSON(data.data);
                showMsg(rdata.msg,function(){
                    layer.close(layerIndex);
                    dbList();
                },{icon: rdata.status ? 1 : 2});   
            });
        },
        btn3:function(){
            var password = $("#MyPassword").val();
            copyText(password);
            return false;
        },
        btn4:function(layerIndex){
            layer.confirm('强制修改,是为了在重建时使用,确定强制?', {
                btn: ['确定', '取消']
            }, function(index, layero){
                layer.close(index);
                var password = $("#MyPassword").val();
                myPost('set_root_pwd', {password:password,force:'1'}, function(data){
                    var rdata = $.parseJSON(data.data);
                    showMsg(rdata.msg,function(){
                        layer.close(layerIndex);
                        dbList();
                    },{icon: rdata.status ? 1 : 2});   
                });
            });
            return false;
        }
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

function setDbRw(id,username,val){
    myPost('set_db_rw',{id:id,username:username,rw:val}, function(data){
        var rdata = $.parseJSON(data.data);
        // layer.msg(rdata.msg,{icon:rdata.status ? 1 : 5,shade: [0.3, '#000']});
        showMsg(rdata.msg, function(){
            dbList();
        },{icon:rdata.status ? 1 : 5,shade: [0.3, '#000']}, 2000);

    });
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
            btn:["提交","取消"],
            shadeClose: true,
            content: "<form class='bt-form pd20' id='set_db_access'>\
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
                      </form>",
            success:function(){
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

                 $('select[name="dataAccess"]').change(function(){
                    var v = $(this).val();
                    if (v == 'ip'){
                        $(this).after("<input id='dataAccess_subid' class='bt-input-text mr5' type='text' name='address' placeholder='多个IP使用逗号(,)分隔' style='width: 230px; display: inline-block;'>");
                    } else {
                        $('#dataAccess_subid').remove();
                    }
                });
            },
            yes:function(index){
                var data = $("#set_db_access").serialize();
                data = decodeURIComponent(data);
                var dataObj = toArrayObject(data);
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
                myPost('set_db_access', dataObj, function(data){
                    var rdata = $.parseJSON(data.data);
                    showMsg(rdata.msg,function(){
                        layer.close(index);
                        dbList();
                    },{icon: rdata.status ? 1 : 2});   
                });
            }
        });

    });
}

function fixDbAccess(username){
    myPost('fix_db_access', '', function(rdata){
        var rdata = $.parseJSON(rdata.data);
        showMsg(rdata.msg,function(){
            dbList();
        },{icon: rdata.status ? 1 : 2}); 
    });
}

function setDbPass(id, username, password){
    layer.open({
        type: 1,
        area: '500px',
        title: '修改数据库密码',
        closeBtn: 1,
        shift: 5,
        shadeClose: true,
        btn:["提交","关闭"],
        content: "<form class='bt-form pd20' id='mod_pwd'>\
                    <div class='line'>\
                        <span class='tname'>用户名</span>\
                        <div class='info-r'><input readonly='readonly' name=\"name\" class='bt-input-text mr5' type='text' style='width:330px;outline:none;' value='"+username+"' /></div>\
                    </div>\
                    <div class='line'>\
                    <span class='tname'>密码</span>\
                    <div class='info-r'>\
                        <input class='bt-input-text mr5' type='text' name='password' id='MyPassword' style='width:330px' value='"+password+"' />\
                        <span title='随机密码' class='glyphicon glyphicon-repeat cursor' onclick='repeatPwd(16)'></span></div>\
                    </div>\
                    <input type='hidden' name='id' value='"+id+"'>\
                </form>",
        yes:function(index){
            // var data = $("#mod_pwd").serialize();
            var data = {};
            data['name'] = $('input[name=name]').val();
            data['password'] = $('#MyPassword').val();
            data['id'] = $('input[name=id]').val();
            myPost('set_user_pwd', data, function(data){
                var rdata = $.parseJSON(data.data);
                showMsg(rdata.msg,function(){
                    layer.close(index);
                    dbList();
                },{icon: rdata.status ? 1 : 2});   
            });
        }
    });
}

function addDatabase(type){
    layer.open({
        type: 1,
        area: '500px',
        title: '添加数据库',
        closeBtn: 1,
        shift: 5,
        shadeClose: true,
        btn:["提交","关闭"],
        content: "<form class='bt-form pd20' id='add_db'>\
                    <div class='line'>\
                        <span class='tname'>数据库名</span>\
                        <div class='info-r'><input name='name' class='bt-input-text mr5' placeholder='新的数据库名称' type='text' style='width:65%' value=''>\
                        <select class='bt-input-text mr5 codeing_a5nGsm' name='codeing' style='width:27%'>\
                            <option value='utf8mb4'>utf8mb4</option>\
                            <option value='utf8'>utf-8</option>\
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
                  </form>",
        success:function(){
            $("input[name='name']").keyup(function(){
                var v = $(this).val();
                $("input[name='db_user']").val(v);
                $("input[name='ps']").val(v);
            });

            $('select[name="dataAccess"]').change(function(){
                var v = $(this).val();
                if (v == 'ip'){
                    $(this).after("<input id='dataAccess_subid' class='bt-input-text mr5' type='text' name='address' placeholder='多个IP使用逗号(,)分隔' style='width: 230px; display: inline-block;'>");
                } else {
                    $('#dataAccess_subid').remove();
                }
            });
        },
        yes:function(index) {
            var data = $("#add_db").serialize();
            data = decodeURIComponent(data);
            var dataObj = toArrayObject(data);
            if(!dataObj['address']){
                dataObj['address'] = dataObj['dataAccess'];
            }
            myPost('add_db', dataObj, function(data){
                var rdata = $.parseJSON(data.data);
                showMsg(rdata.msg,function(){
                    if (rdata.status){
                        layer.close(index);
                        dbList();
                    }
                },{icon: rdata.status ? 1 : 2}, 2000);
            });
        }
    });
}

function delDb(id, name){
    safeMessage('删除['+name+']','您真的要删除['+name+']吗？',function(){
        var data='id='+id+'&name='+name;
        myPost('del_db', data, function(data){
            var rdata = $.parseJSON(data.data);
            showMsg(rdata.msg,function(){
                dbList();
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
    $.post('/plugins/run', {'name':'phpmyadmin','func':'plugins_db_support'}, function(data){
        var rdata = $.parseJSON(data.data);

        if (rdata.data['installed'] != 'ok'){
            layer.msg('phpMyAdmin未安装!',{icon:2,shade: [0.3, '#000']});
            return;
        }

        if (rdata.data['status'] != 'start'){
            layer.msg('phpMyAdmin未启动',{icon:2,shade: [0.3, '#000']});
            return;
        }

        if (rdata.data['cfg']['choose'] != 'mysql-yum'){
            layer.msg('当前为['+rdata.data['cfg']['choose'] + ']模式,若要使用请修改phpMyAdmin访问切换.',{icon:2,shade: [0.3, '#000']});
            return;
        }
        var home_page = rdata.data['home_page'];
        $("#toPHPMyAdmin").attr('action',home_page);
        if($("#toPHPMyAdmin").attr('action').indexOf('phpmyadmin') == -1){
            layer.msg('请先安装phpMyAdmin',{icon:2,shade: [0.3, '#000']});
            setTimeout(function(){ window.location.href = '/soft'; },3000);
            return;
        }
        //检查版本
        bigVer = rdata.data['version'];
        if (bigVer>=4.5){

            setTimeout(function(){
                $("#toPHPMyAdmin").submit();
            },2000);
            layer.msg('phpMyAdmin['+data.data+']需要手动登录😭',{icon:16,shade: [0.3, '#000'],time:4000});
            
        } else{
            var murl = $("#toPHPMyAdmin").attr('action');
            $("#pma_username").val(username);
            $("#pma_password").val(password);
            $("#db").val(name);

            layer.msg('正在打开phpMyAdmin',{icon:16,shade: [0.3, '#000'],time:2000});

            setTimeout(function(){
                $("#toPHPMyAdmin").submit();
            },2000);
        }

    },'json');
}

function delBackup(filename, name, path){
    if(typeof(path) == "undefined"){
        path = "";
    }
    myPost('delete_db_backup',{filename:filename,path:path},function(){
        layer.msg('执行成功!');
        setTimeout(function(){
            setBackupReq(name);
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

function importBackupProgress(file,name){
    myPost('import_db_backup_progress',{file:file,name:name}, function(data){
        var rdata = $.parseJSON(data.data);
        layer.open({
            title: "手动导入命令CMD【显示进度】",
            area: ['600px', '180px'],
            type:1,
            closeBtn: 1,
            shadeClose: false,
            btn:["复制","取消"],
            content: '<div class="pd15">\
                        <div class="divtable">\
                            <pre class="layui-code">'+rdata.data+'</pre>\
                        </div>\
                    </div>',
            success:function(){
                copyText(rdata.data);
            },
            yes:function(){
                copyText(rdata.data);
            }
        });
    });
}


function importDbExternal(file,name){
    myPost('import_db_external',{file:file,name:name}, function(data){
        layer.msg('执行成功!');
    });
}

function importDbExternalProgress(file,name){
    myPost('import_db_external_progress',{file:file,name:name}, function(data){
        var rdata = $.parseJSON(data.data);
        layer.open({
            title: "手动导入命令CMD【显示进度】",
            area: ['600px', '180px'],
            type:1,
            closeBtn: 1,
            shadeClose: false,
            btn:["复制","取消"],
            content: '<div class="pd15">\
                        <div class="divtable">\
                            <pre class="layui-code">'+rdata.data+'</pre>\
                        </div>\
                    </div>',
            success:function(){
                copyText(rdata.data);
            },
            yes:function(){
                copyText(rdata.data);
            }
        });
    });
}

function setLocalImport(db_name){

    //上传文件
    function uploadDbFiles(upload_dir){
        var up_db = layer.open({
            type:1,
            closeBtn: 1,
            title:"上传导入文件["+upload_dir+']',
            area: ['500px','300px'],
            shadeClose:false,
            content:'<div class="fileUploadDiv">\
                    <input type="hidden" id="input-val" value="'+upload_dir+'" />\
                    <input type="file" id="file_input"  multiple="true" autocomplete="off" />\
                    <button type="button"  id="opt" autocomplete="off">添加文件</button>\
                    <button type="button" id="up" autocomplete="off" >开始上传</button>\
                    <span id="totalProgress" style="position: absolute;top: 7px;right: 147px;"></span>\
                    <span style="float:right;margin-top: 9px;">\
                    <font>文件编码:</font>\
                    <select id="fileCodeing" >\
                        <option value="byte">二进制</option>\
                        <option value="utf-8">UTF-8</option>\
                        <option value="gb18030">GB2312</option>\
                    </select>\
                    </span>\
                    <button type="button" id="filesClose" autocomplete="off">关闭</button>\
                    <ul id="up_box"></ul>\
                </div>',
            success:function(){
                $('#filesClose').click(function(){
                    layer.close(up_db);
                });
            }

        });
        uploadStart(function(){
            getList();
            layer.close(up_db);
        });
    }

    function getList(){
        myPost('get_db_backup_import_list',{}, function(data){
            var rdata = $.parseJSON(data.data);

            var file_list = rdata.data.list;
            var upload_dir = rdata.data.upload_dir;

            var tbody = '';
            for (var i = 0; i < file_list.length; i++) {
                tbody += '<tr>\
                        <td><span> ' + file_list[i]['name'] + '</span></td>\
                        <td><span> ' + file_list[i]['size'] + '</span></td>\
                        <td><span> ' + file_list[i]['time'] + '</span></td>\
                        <td style="text-align: right;">\
                            <a class="btlink" onclick="importDbExternal(\'' + file_list[i]['name'] + '\',\'' +db_name+ '\')">导入</a> | \
                            <a class="btlink" onclick="importDbExternalProgress(\'' + file_list[i]['name'] + '\',\'' +db_name+ '\')">导入进度</a> | \
                            <a class="btlink del" index="'+i+'">删除</a>\
                        </td>\
                    </tr>';
            }

            $('#import_db_file_list').html(tbody);
            $('input[name="upload_dir"]').val(upload_dir);

            $("#import_db_file_list .del").on('click',function(){
                var index = $(this).attr('index');
                var filename = file_list[index]["name"];
                myPost('delete_db_backup',{filename:filename,path:upload_dir},function(){
                    showMsg('执行成功!', function(){
                        getList();
                    },{icon:1},2000);
                });
            });
        });
    }

    var layerIndex = layer.open({
        type: 1,
        title: "从文件导入数据",
        area: ['700px', '380px'],
        closeBtn: 1,
        shadeClose: false,
        content: '<div class="pd15">\
                    <div class="db_list">\
                        <button id="btn_file_upload" class="btn btn-success btn-sm" type="button">从本地上传</button>\
                    </div >\
                    <div class="divtable">\
                    <input type="hidden" name="upload_dir" value=""> \
                    <div id="database_fix"  style="height:150px;overflow:auto;border:#ddd 1px solid">\
                    <table class="table table-hover "style="border:none">\
                        <thead>\
                            <tr>\
                                <th>文件名称</th>\
                                <th>文件大小</th>\
                                <th>备份时间</th>\
                                <th style="text-align: right;">操作</th>\
                            </tr>\
                        </thead>\
                        <tbody  id="import_db_file_list" class="gztr"></tbody>\
                    </table>\
                    </div>\
                    <ul class="help-info-text c7">\
                        <li>仅支持sql、zip、sql.gz、(tar.gz|gz|tgz)</li>\
                        <li>zip、tar.gz压缩包结构：test.zip或test.tar.gz压缩包内，必需包含test.sql</li>\
                        <li>若文件过大，您还可以使用SFTP工具，将数据库文件上传到/www/backup/import</li>\
                    </ul>\
                </div>\
        </div>',
        success:function(index){
            $('#btn_file_upload').click(function(){
                var upload_dir = $('input[name="upload_dir"]').val();
                uploadDbFiles(upload_dir);
            });

            getList();
        },
    });

    
}

function setBackup(db_name){
    var layerIndex = layer.open({
        type: 1,
        title: "数据库备份详情",
        area: ['700px', '280px'],
        closeBtn: 1,
        shadeClose: false,
        content: '<div class="pd15">\
                    <div class="db_list">\
                        <button id="btn_backup" class="btn btn-success btn-sm" type="button">备份</button>\
                        <button id="btn_local_import" class="btn btn-success btn-sm" type="button">外部导入</button>\
                    </div >\
                    <div class="divtable">\
                    <div  id="database_fix"  style="height:150px;overflow:auto;border:#ddd 1px solid">\
                    <table id="database_table" class="table table-hover "style="border:none">\
                        <thead>\
                            <tr>\
                                <th>文件名称</th>\
                                <th>文件大小</th>\
                                <th>备份时间</th>\
                                <th style="text-align: right;">操作</th>\
                            </tr>\
                        </thead>\
                        <tbody class="list"></tbody>\
                    </table>\
                    </div>\
                </div>\
        </div>',
        success:function(index){
            $('#btn_backup').click(function(){
                myPost('set_db_backup',{name:db_name}, function(data){
                    showMsg('执行成功!', function(){
                        setBackupReq(db_name);
                    }, {icon:1}, 2000);
                });
            });

            $('#btn_local_import').click(function(){
                setLocalImport(db_name);
            });

            setBackupReq(db_name);
        },
    });
}


function setBackupReq(db_name, obj){
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
                        <a class="btlink" onclick="importBackupProgress(\'' + rdata.data[i]['name'] + '\',\'' +db_name+ '\')">导入进度</a> | \
                        <a class="btlink" onclick="downloadBackup(\'' + rdata.data[i]['file'] + '\')">下载</a> | \
                        <a class="btlink" onclick="delBackup(\'' + rdata.data[i]['name'] + '\',\'' +db_name+ '\')">删除</a>\
                    </td>\
                </tr> ';
        }
        $('#database_table tbody').html(tbody);
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

            list += '<a href="javascript:;" class="btlink" class="btlink" onclick="setBackup(\''+rdata.data[i]['name']+'\',this)" title="数据库备份">'+(rdata.data[i]['is_backup']?'已备份':'未备份') +'</a> | ';

            var rw = '';
            var rw_change = 'all';
            if (typeof(rdata.data[i]['rw'])!='undefined'){
                var rw_val = '读写';
                if (rdata.data[i]['rw'] == 'all'){
                    rw_val = "所有";
                    rw_change = 'rw';
                } else if (rdata.data[i]['rw'] == 'rw'){
                    rw_val = "读写";
                    rw_change = 'r';
                } else if (rdata.data[i]['rw'] == 'r'){
                    rw_val = "只读";
                    rw_change = 'all';
                }
                rw = '<a href="javascript:;" class="btlink" onclick="setDbRw(\''+rdata.data[i]['id']+'\',\''+rdata.data[i]['name']+'\',\''+rw_change+'\')" title="设置读写">'+rw_val+'</a> | ';
            }


            list += '<a href="javascript:;" class="btlink" onclick="openPhpmyadmin(\''+rdata.data[i]['name']+'\',\''+rdata.data[i]['username']+'\',\''+rdata.data[i]['password']+'\')" title="数据库管理">管理</a> | ' +
                        '<a href="javascript:;" class="btlink" onclick="repTools(\''+rdata.data[i]['name']+'\')" title="MySQL优化修复工具">工具</a> | ' +
                        '<a href="javascript:;" class="btlink" onclick="setDbAccess(\''+rdata.data[i]['username']+'\')" title="设置数据库权限">权限</a> | ' +
                        rw +
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
            <button onclick="fixDbAccess(\'root\')" title="修复" class="btn btn-default btn-sm" type="button" style="margin-right: 5px;">修复</button>\
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
                <div class="table_toolbar" style="left:0px;">\
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


function myBinRollingLogs(_name, func, _args, line){

    var file_line = 100;
    if ( typeof(line) != 'undefined' ){
        file_line = line;
    }

    var reqTimer = null;

    function requestLogs(func,file,line){
        myPostCallbakN(func,'',{'file':file,"line":line}, function(rdata){
            var data = rdata.data.data;
            var cmd = rdata.data.cmd;
            if(data == '') {
                data = '当前没有日志!';
            }

            $('#my_rolling_cmd').html(cmd);

            $('#my_rolling_copy').click(function(){
                copyText(cmd);
            });

            var ebody = '<textarea readonly="readonly" style="margin: 0px;width: 100%;height: 570px;background-color: #333;color:#fff; padding:0 5px" id="roll_info_log">'+data+'</textarea>';
            $("#my_rolling_logs").html(ebody);
            var ob = document.getElementById('roll_info_log');
            ob.scrollTop = ob.scrollHeight;
        });
    }


    layer.open({
        type: 1,
        title: _name + '日志',
        area: ['800px','700px'],
        end: function(){
            if (reqTimer){
                clearInterval(reqTimer);
            }
        },
        content:'<div class="change-default" style="padding:0px 20px 0px;">\
                    <div class="divtable mtb10">\
                    <table class="table table-hover"><tr>\
                    <td id="my_rolling_cmd">cmd</td>\
                    <td id="my_rolling_copy" style="width:35px;"><span class="ico-copy cursor btcopy" title="复制密码"></span></td>\
                    <tr>\
                    </table>\
                    </div>\
                </div>\
                <div class="change-default" style="padding:0px 20px 0px;" id="my_rolling_logs">\
                    <textarea readonly="readonly" style="margin: 0px;width: 100%;height: 570px;background-color: #333;color:#fff; padding:0 5px" id="roll_info_log"></textarea>\
                </div>',
        success:function(){
            var fileName = _args['file'];
            requestLogs(func,fileName,file_line);
            reqTimer = setInterval(function(){
                requestLogs(func,fileName,file_line);
            },1000);
        }
    });
}

function myBinLogsRender(page){
    var _data = {};
    if (typeof(page) =='undefined'){
        var page = 1;
    }
    
    _data['page'] = page;
    _data['page_size'] = 10;
    _data['tojs'] = 'myBinLogsRender';
    myPost('binlog_list', _data, function(data){
        var rdata = $.parseJSON(data.data);
        // console.log(rdata);
        var list = '';
        for(i in rdata.data){
            list += '<tr>';

            list += '<td>' + rdata.data[i]['name'] +'</td>';
            list += '<td>' + toSize(rdata.data[i]['size'])+'</td>';
            list += '<td>' + rdata.data[i]['time'] +'</td>';
            

            list += '<td style="text-align:right">';
            list += '<a href="javascript:;" data-index="'+i+'" class="btlink look" class="btlink">查看</a> | ';
            list += '<a href="javascript:;" data-index="'+i+'" class="btlink look_decode" class="btlink">解码查看</a>';
            list += '</td></tr>';
        }

        if (rdata.data.length ==0){
            list = '<tr><td colspan="4">无数据</td</tr>';
        }

        $("#binlog_list tbody").html(list);
        $('#binlog_page').html(rdata.page);


        $('#binlog_list .look').click(function(){
            var i = $(this).data('index');
            var file = rdata.data[i]['name'];
            myBinRollingLogs('查看BINLOG','binLogListLook',{'file':file },100);
        });

        $('#binlog_list .look_decode').click(function(){
            var i = $(this).data('index');
            var file = rdata.data[i]['name'];
            myBinRollingLogs('查看解码BINLOG','binLogListLookDecode',{'file':file },100);
        });
    });
}

function myBinLogs(){
    var con = '<div class="safe bgw">\
            <button class="btn btn-success btn-sm relay_trace" type="button" style="margin-right: 5px;">中继日志跟踪</button>\
            <button class="btn btn-default btn-sm binlog_trace" type="button" style="margin-right: 5px;">最新BINLOG日志跟踪</button>\
            <div id="binlog_list" class="divtable mtb10">\
                <div class="tablescroll">\
                    <table class="table table-hover" width="100%" cellspacing="0" cellpadding="0" border="0" style="border: 0 none;">\
                    <thead><tr>\
                    <th>文件名称</th>\
                    <th>大小</th>\
                    <th>时间</th>\
                    <th style="text-align:right;">操作</th>\
                    </tr></thead>\
                    <tbody></tbody></table>\
                </div>\
                <div id="binlog_page" class="dataTables_paginate paging_bootstrap page"></div>\
            </div>\
        </div>';
    $(".soft-man-con").html(con);
    myBinLogsRender(1);

    $('.soft-man-con .relay_trace').click(function(){
        myBinRollingLogs('中继日志跟踪','binLogListTraceRelay',{'file':''},100);
    });

    $('.soft-man-con .binlog_trace').click(function(){
        myBinRollingLogs('最新BINLOG日志跟踪','binLogListTraceBinLog',{'file':''},100);
    });
}

function myLogs(){
    
    myPost('bin_log', {status:1}, function(data){
        var rdata = $.parseJSON(data.data);

        var line_status = ""
        if (rdata.status){
            line_status = '<button class="btn btn-success btn-xs btn-bin va0">关闭</button>\
                        <button class="btn btn-success btn-xs clean-btn-bin va0">清理BINLOG日志</button>';
        } else {
            line_status = '<button class="btn btn-success btn-xs btn-bin va0">开启</button>';
        }

        var limitCon = '<p class="conf_p">\
                        <span class="f14 c6 mr20">二进制日志 </span><span class="f14 c6 mr20">' + toSize(rdata.msg) + '</span>\
                        '+line_status+'\
                        <p class="f14 c6 mtb10" style="border-top:#ddd 1px solid; padding:10px 0">错误日志<button class="btn btn-default btn-clear btn-xs" style="float:right;" >清理日志</button></p>\
                        <textarea readonly style="margin: 0px;width: 100%;height: 438px;background-color: #333;color:#fff; padding:0 5px" id="error_log"></textarea>\
                    </p>';
        $(".soft-man-con").html(limitCon);

        //设置二进制日志
        $(".btn-bin").click(function () {
            myPost('bin_log', 'close=change', function(data){
                var rdata = $.parseJSON(data.data);
                layer.msg(rdata.msg, { icon: rdata.status ? 1 : 5 });
                setTimeout(function(){myLogs();}, 2000);
            });
        });

        $(".clean-btn-bin").click(function () {
            myPost('clean_bin_log', '', function(data){
                var rdata = $.parseJSON(data.data);
                layer.msg(rdata.msg, { icon: rdata.status ? 1 : 5 });
                setTimeout(function(){myLogs();}, 2000);
            });
        });

         //清空日志
        $(".btn-clear").click(function () {
            myPost('error_log', 'close=1', function(data){
                var rdata = $.parseJSON(data.data);
                layer.msg(rdata.msg, { icon: rdata.status ? 1 : 5 });
                setTimeout(function(){myLogs();}, 2000);
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
            $("#error_log").html(error_body);
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
            closeBtn: 1,
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
    layer.open({
        type: 1,
        area: '500px',
        title: '添加同步账户',
        closeBtn: 1,
        shift: 5,
        shadeClose: true,
        btn:["提交","取消"],
        content: "<form class='bt-form pd20' id='add_master'>\
            <div class='line'><span class='tname'>用户名</span><div class='info-r'><input name='username' class='bt-input-text mr5' placeholder='用户名' type='text' style='width:330px;' value='"+(randomStrPwd(6))+"'></div></div>\
            <div class='line'>\
            <span class='tname'>密码</span>\
            <div class='info-r'><input class='bt-input-text mr5' type='text' name='password' id='MyPassword' style='width:330px' value='"+(randomStrPwd(16))+"' /><span title='随机密码' class='glyphicon glyphicon-repeat cursor' onclick='repeatPwd(16)'></span></div>\
            </div>\
            <input type='hidden' name='ps' value='' />\
          </form>",
        success:function(){
            $("input[name='name']").keyup(function(){
                var v = $(this).val();
                $("input[name='db_user']").val(v);
                $("input[name='ps']").val(v);
            });

            $('select[name="dataAccess"]').change(function(){
                var v = $(this).val();
                if (v == 'ip'){
                    $(this).after("<input id='dataAccess_subid' class='bt-input-text mr5' type='text' name='address' placeholder='多个IP使用逗号(,)分隔' style='width: 230px; display: inline-block;'>");
                } else {
                    $('#dataAccess_subid').remove();
                }
            });
        },
        yes:function(index){
            var data = $("#add_master").serialize();
            data = decodeURIComponent(data);
            var dataObj = toArrayObject(data);
            if(!dataObj['address']){
                dataObj['address'] = dataObj['dataAccess'];
            }

            myPost('add_master_rep_slave_user', dataObj, function(data){
                var rdata = $.parseJSON(data.data);
                showMsg(rdata.msg,function(){
                    layer.close(index);
                    if (rdata.status){
                        getMasterRepSlaveList();
                    }
                },{icon: rdata.status ? 1 : 2},600);
            });
        }
    });
}



function updateMasterRepSlaveUser(username, password){
  
    var index = layer.open({
        type: 1,
        area: '500px',
        title: '更新账户',
        closeBtn: 1,
        shift: 5,
        shadeClose: true,
        content: "<form class='bt-form pd20 pb70' id='update_master'>\
            <div class='line'><span class='tname'>用户名</span><div class='info-r'><input name='username' readonly='readonly' class='bt-input-text mr5' placeholder='用户名' type='text' style='width:330px;' value='"+username+"'></div></div>\
            <div class='line'>\
            <span class='tname'>密码</span>\
            <div class='info-r'><input class='bt-input-text mr5' type='text' name='password' id='MyPassword' style='width:330px' value='"+password+"' /><span title='随机密码' class='glyphicon glyphicon-repeat cursor' onclick='repeatPwd(16)'></span></div>\
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
        var dataObj = toArrayObject(data);
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

        var cmd = rdata.data['cmd'];
        
        var loadOpen = layer.open({
            type: 1,
            title: '同步命令',
            area: '500px',
            content:"<form class='bt-form pd20 pb70' id='add_master'>\
            <div class='line'>"+cmd+"</div>\
            <div class='bt-form-submit-btn' style='text-align:center;'>\
                <button type='button' class='btn btn-success btn-sm btn-title'>选择其中一个复制</button>\
            </div>\
          </form>",
        });
    });
}

function delMasterRepSlaveUser(username){
    myPost('del_master_rep_slave_user', {username:username}, function(data){
        var rdata = $.parseJSON(data.data);
        showMsg(rdata.msg, function(){
            getMasterRepSlaveList();
        },{icon: rdata.status ? 1 : 2},1000)
    });
}


function setDbMasterAccess(username){
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
            btn:["提交","取消"],
            shadeClose: true,
            content: "<form class='bt-form pd20' id='set_db_access'>\
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
                      </form>",
            success:function(){
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

                 $('select[name="dataAccess"]').change(function(){
                    var v = $(this).val();
                    if (v == 'ip'){
                        $(this).after("<input id='dataAccess_subid' class='bt-input-text mr5' type='text' name='address' placeholder='多个IP使用逗号(,)分隔' style='width: 230px; display: inline-block;'>");
                    } else {
                        $('#dataAccess_subid').remove();
                    }
                });
            },
            yes:function(index){
                var data = $("#set_db_access").serialize();
                data = decodeURIComponent(data);
                var dataObj = toArrayObject(data);
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
                myPost('set_dbmaster_access', dataObj, function(data){
                    var rdata = $.parseJSON(data.data);
                    showMsg(rdata.msg,function(){
                        layer.close(index);
                    },{icon: rdata.status ? 1 : 2});   
                });
            }
        });

    });
}


function resetMaster(){
    myPost('reset_master', '', function(data){
        var rdata = $.parseJSON(data.data);
        showMsg(rdata.msg,function(){
        },{icon: rdata.status ? 1 : 2});   
    },'正在执行重置master命令[reset master]');
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
            var password = user_list[i]['password'];
            list += '<tr><td>'+name+'</td>\
                <td>'+password+'</td>\
                <td>\
                    <a class="btlink" onclick="updateMasterRepSlaveUser(\''+name+'\',\''+password+'\');">修改</a> | \
                    <a class="btlink" onclick="delMasterRepSlaveUser(\''+name+'\');">删除</a> | \
                    <a class="btlink" onclick="setDbMasterAccess(\''+name+'\');">权限</a> | \
                    <a class="btlink" onclick="getMasterRepSlaveUserCmd(\''+name+'\');">从库同步命令</a>\
                </td>\
            </tr>';
        }

        $('#get_master_rep_slave_list_page tbody').html(list);
        $('.dataTables_paginate_4').html(rdata['page']);
    });
}

function getMasterRepSlaveListPage(){
    var page = '<div class="dataTables_paginate_4 dataTables_paginate paging_bootstrap page" style="margin-top:0px;"></div>';
        page += '<div class="table_toolbar" style="left:0px;"><span class="sync btn btn-default btn-sm" onclick="addMasterRepSlaveUser()" title="">添加同步账户</span></div>';

    var loadOpen = layer.open({
        type: 1,
        title: '同步账户列表',
        area: '500px',
        content:"<div class='bt-form pd20 c6'>\
                 <div class='divtable mtb10' id='get_master_rep_slave_list_page'>\
                    <div><table class='table table-hover'>\
                        <thead><tr><th>用户名</th><th>密码</th><th>操作</th></tr></thead>\
                        <tbody></tbody>\
                    </table></div>\
                    "+page +"\
                </div>\
            </div>",
        success:function(){
            getMasterRepSlaveList();
        }
    });
}


function deleteSlave(sign){
    myPost('delete_slave', {sign:sign}, function(data){
        var rdata = $.parseJSON(data.data);
        showMsg(rdata['msg'], function(){
            masterOrSlaveConf();
        },{icon:rdata.status?1:2,time:3000},3000);
    });
}


function getFullSyncStatus(db){
    var timeId = null;

    myPost('get_slave_list', {page:1,page_size:100}, function(data){
        var rdata = $.parseJSON(data.data);
        var rsource = rdata.data;

        if (db == 'ALL' && rsource.length>1){
            layer.msg("多主不支持该模式!",{icon:2});
            return;
        }

        var dataSource = '';
        if (rsource.length>1){
            var sourceList = '';
            for (var i = 0; i < rsource.length; i++) {
                if ('Channel_Name' in rsource[i]){
                    sourceList += '<option val="'+rsource[i]['Master_Host']+'">'+rsource[i]['Master_Host']+'</option>';
                }
            }

            dataSource = "<p class='line' style='text-align:center;'>\
                <span>同步数据源：</span>\
                <select class='bt-input-text' name='data_source' style='width:200px;'>" + sourceList + "</select>\
            </p>";
        }

        layer.open({
            type: 1,
            title: '全量同步['+db+']',
            area: '500px',
            content:"<div class='bt-form pd15'>\
                     <div class='divtable mtb10'>\
                        "+dataSource+"\
                        <span id='full_msg'></span>\
                        <div class='progress'>\
                            <div class='progress-bar' role='progressbar' aria-valuenow='0' aria-valuemin='0' aria-valuemax='100' style='min-width: 2em;'>0%</div>\
                        </div>\
                    </div>\
                    <div class='table_toolbar' style='left:0px;'>\
                        <span data-status='init' class='sync btn btn-default btn-sm' id='begin_full_sync'>开始</span>\
                        <span data-status='init' class='btn btn-default btn-sm' id='full_sync_cmd'>手动命令</span>\
                    </div>\
                </div>",
            cancel: function(){ 
                clearInterval(timeId);
            },
            success:function(){
                $('#begin_full_sync').click(function(){
                    var val = $(this).data('status');
                    var sign = '';
                    if (dataSource !=''){
                        sign = $('select[name="data_source"]').val();
                    }
                    if (val == 'init'){
                        fullSync(db, sign, 1);
                        timeId = setInterval(function(){
                            fullSync(db,sign,0);
                        }, 1000);
                        $(this).data('status','starting');
                        $('#begin_full_sync').text("同步中");
                    } else {
                        layer.msg("正在同步中..",{icon:0});
                    }
                });

                $('#full_sync_cmd').click(function(){
                    myPostN('full_sync_cmd', {'db':db,'sign':''}, function(rdata){
                        var rdata = $.parseJSON(rdata.data);
                        layer.open({
                        title: "手动执行命令CMD",
                            area: ['600px', '180px'],
                            type:1,
                            closeBtn: 1,
                            shadeClose: false,
                            btn:["复制","取消"],
                            content: '<div class="pd15">\
                                        <div class="divtable">\
                                            <pre class="layui-code">'+rdata.data+'</pre>\
                                        </div>\
                                    </div>',
                            success:function(){
                                copyText(rdata.data);
                            },
                            yes:function(){
                                copyText(rdata.data);
                            }
                        });
                    });
                });
            }
        });
    });

    function fullSync(db,sign,begin){
       
        myPostN('full_sync', {db:db,sign:sign,begin:begin}, function(data){
            var rdata = $.parseJSON(data.data);
            $('#full_msg').text(rdata['msg']);
            $('.progress-bar').css('width',rdata['progress']+'%');
            $('.progress-bar').text(rdata['progress']+'%');

            if (rdata['code']==6 ||rdata['code']<0){
                layer.msg(rdata['msg']);
                clearInterval(timeId);
                $('#begin_full_sync').text("同步结束,再次同步?");
                $("#begin_full_sync").attr('data-status','init');
            }
        });
    }
}

function dataSyncVerify(db){
    var reqTimer = null;

    function requestLogs(layerIndex){
        myPostN('sync_database_repair_log', {db:db, sign:'',op:'get'}, function(rdata){
            var rdata = $.parseJSON(rdata.data);

            if(!rdata.status) {
                layer.close(layerIndex);
                layer.msg(rdata.msg,{icon:2, time:2000});
                clearInterval(reqTimer);
                return;
            };

            if (rdata.msg == ''){
                rdata.msg = '暂无数据!';
            }

            $("#data_verify_log").html(rdata.msg);
            //滚动到最低
            var ob = document.getElementById('data_verify_log');
            ob.scrollTop = ob.scrollHeight; 
        });
    }

    layer.open({
        type: 1,
        title: '同步数据库['+db+']数据校验',
        area: '500px',
        btn:[ "开始","取消","手动"],
        content:"<div class='bt-form'>\
                "+'<pre id="data_verify_log" style="overflow: auto; border: 0px none; line-height:23px;padding: 5px; margin: 0px; white-space: pre-wrap; height: 395px; background-color: rgb(51,51,51);color:#f1f1f1;border-radius:0px;font-family:"></pre>'+"\
            </div>",
        cancel: function(){
            if (reqTimer){
                clearInterval(reqTimer);
            }
        },
        yes:function(index,layer_index){
            myPostN('sync_database_repair_log', {db:db, sign:'',op:'do'}, function(data){});
            layer.msg("执行成功");

            requestLogs(layer_index);
            reqTimer = setInterval(function(){
                requestLogs(layer_index);
            },3000);
        },
        success:function(){
        },
        btn3: function(){
            myPostN('sync_database_repair_log', {db:db, sign:'',op:'cmd'}, function(rdata){
                var rdata = $.parseJSON(rdata.data);
                layer.open({
                title: "手动执行命令CMD",
                    area: ['600px', '180px'],
                    type:1,
                    closeBtn: 1,
                    shadeClose: false,
                    btn:["复制","取消"],
                    content: '<div class="pd15">\
                                <div class="divtable">\
                                    <pre class="layui-code">'+rdata.data+'</pre>\
                                </div>\
                            </div>',
                    success:function(){
                        copyText(rdata.data);
                    },
                    yes:function(){
                        copyText(rdata.data);
                    }
                });
            });
            return false;
        }

    });
}

function addSlaveSSH(ip=''){

    myPost('get_slave_ssh_by_ip', {ip:ip}, function(rdata){
        
        var rdata = $.parseJSON(rdata.data);

        var ip = '127.0.0.1';
        var port = "22";
        var id_rsa = '';
        var db_user ='';

        if (rdata.data.length>0){
            ip = rdata.data[0]['ip'];
            port = rdata.data[0]['port'];
            id_rsa = rdata.data[0]['id_rsa'];
            db_user = rdata.data[0]['db_user'];
        }

        var index = layer.open({
            type: 1,
            area: ['500px','480px'],
            title: '添加SSH',
            closeBtn: 1,
            shift: 5,
            shadeClose: true,
            btn:["确认","取消"],
            content: "<form class='bt-form pd20'>\
                <div class='line'><span class='tname'>IP</span><div class='info-r'><input name='ip' class='bt-input-text mr5' type='text' style='width:330px;' value='"+ip+"'></div></div>\
                <div class='line'><span class='tname'>端口</span><div class='info-r'><input name='port' class='bt-input-text mr5' type='number' style='width:330px;' value='"+port+"'></div></div>\
                <div class='line'><span class='tname'>同步账户[DB]</span><div class='info-r'><input name='db_user'  placeholder='为空则取第一个!' class='bt-input-text mr5' type='text' style='width:330px;' value='"+db_user+"'></div></div>\
                <div class='line'>\
                <span class='tname'>ID_RSA</span>\
                <div class='info-r'><textarea class='bt-input-text mr5' row='20' cols='50' name='id_rsa' style='width:330px;height:200px;'></textarea></div>\
                </div>\
                <input type='hidden' name='ps' value='' />\
              </form>",
            success:function(){
                $('textarea[name="id_rsa"]').html(id_rsa);
            },
            yes:function(index){
                var ip = $('input[name="ip"]').val();
                var port = $('input[name="port"]').val();
                var db_user = $('input[name="db_user"]').val();
                var id_rsa = $('textarea[name="id_rsa"]').val();

                var data = {ip:ip,port:port,id_rsa:id_rsa,db_user:db_user};
                myPost('add_slave_ssh', data, function(data){
                    layer.close(index);
                    var rdata = $.parseJSON(data.data);
                    showMsg(rdata.msg,function(){
                        if (rdata.status){
                            getSlaveSSHPage();
                        }
                    },{icon: rdata.status ? 1 : 2},600);
                });
            }
        });
    });
}


function delSlaveSSH(ip){
    myPost('del_slave_ssh', {ip:ip}, function(rdata){
        var rdata = $.parseJSON(rdata.data);
        showMsg(rdata.msg,function(){
            if (rdata.status){
                getSlaveSSHPage();
            }
        },{icon: rdata.status ? 1 : 2}, 600);
    });
}


function delSlaveSyncUser(ip){
    myPost('del_slave_sync_user', {ip:ip}, function(rdata){
        var rdata = $.parseJSON(rdata.data);
        showMsg(rdata.msg,function(){
            if (rdata.status){
                getSlaveSyncUserPage();
            }
        },{icon: rdata.status ? 1 : 2}, 600);
    });
}

function getSlaveSSHPage(page=1){
    var _data = {};    
    _data['page'] = page;
    _data['page_size'] = 5;
    _data['tojs'] ='getSlaveSSHPage';
    myPost('get_slave_ssh_list', _data, function(data){
        var layerId = null;
        var rdata = [];
        try {
            rdata = $.parseJSON(data.data);
        } catch(e) {
            console.log(e);
        }
        var list = '';
        var ssh_list = rdata['data'];
        for (i in ssh_list) {
            var ip = ssh_list[i]['ip'];
            var port = ssh_list[i]['port'];

            var id_rsa = '未设置';
            if ( ssh_list[i]['port'] != ''){
                id_rsa = '已设置';
            }

            var db_user = '未设置';
            if ( ssh_list[i]['db_user'] != ''){
                db_user = ssh_list[i]['db_user'];
            }

            list += '<tr><td>'+ip+'</td>\
                <td>'+port+'</td>\
                <td>'+db_user+'</td>\
                <td>'+id_rsa+'</td>\
                <td>\
                    <a class="btlink" onclick="addSlaveSSH(\''+ip+'\');">修改</a> | \
                    <a class="btlink" onclick="delSlaveSSH(\''+ip+'\');">删除</a>\
                </td>\
            </tr>';
        }

        $('.get-slave-ssh-list tbody').html(list);
        $('.dataTables_paginate_4').html(rdata['page']);
    });
}



function addSlaveSyncUser(ip=''){

    myPost('get_slave_sync_user_by_ip', {ip:ip}, function(rdata){
        
        var rdata = $.parseJSON(rdata.data);

        var ip = '127.0.0.1';
        var port = "22";
        var cmd = '';
        var user = 'input_sync_user';
        var pass = 'input_sync_pwd';
        var mode = '0';

        if (rdata.data.length>0){
            ip = rdata.data[0]['ip'];
            port = rdata.data[0]['port'];
            cmd = rdata.data[0]['cmd'];
            user = rdata.data[0]['user'];
            pass = rdata.data[0]['pass'];
            mode = rdata.data[0]['mode'];
        }

        var index = layer.open({
            type: 1,
            area: ['500px','510px'],
            title: '同步账户',
            closeBtn: 1,
            shift: 5,
            shadeClose: true,
            btn:["确认","取消"],
            content: "<form class='bt-form pd20'>\
                <div class='line'><span class='tname'>IP</span><div class='info-r'><input name='ip' class='bt-input-text mr5' type='text' style='width:330px;' value='"+ip+"'></div></div>\
                <div class='line'><span class='tname'>端口</span><div class='info-r'><input name='port' class='bt-input-text mr5' type='number' style='width:330px;' value='"+port+"'></div></div>\
                <div class='line'><span class='tname'>同步账户</span><div class='info-r'><input name='user' class='bt-input-text mr5' type='text' style='width:330px;' value='"+user+"'></div></div>\
                <div class='line'><span class='tname'>同步密码</span><div class='info-r'><input name='pass' class='bt-input-text mr5' type='text' style='width:330px;' value='"+pass+"'></div></div>\
                <div class='line'>\
                    <span class='tname'>同步模式</span>\
                    <div class='info-r'>\
                        <select class='bt-input-text mr5' name='mode'>\
                            <option value='0' "+( mode == '0' ? 'selected="selected"' : '')+">经典</option>\
                            <option value='1' "+( mode == '1' ? 'selected="selected"' : '')+">GTID</option>\
                        </select>\
                    </div>\
                </div>\
                <div class='line'>\
                <span class='tname'>CMD[必填]</span>\
                <div class='info-r'><textarea class='bt-input-text mr5' row='20' cols='30' name='cmd' style='width:330px;height:150px;'></textarea></div>\
                </div>\
                <input type='hidden' name='mode' value='"+mode+"' />\
              </form>",
            success:function(){
                $('textarea[name="cmd"]').html(cmd);
                $('textarea[name="cmd"]').change(function(){
                    var val = $(this).val();
                    val = val.replace(';','');
                    var a = {};
                    if (val.toLowerCase().indexOf('for')>0){
                        cmd_tmp = val.split('for');
                        val = cmd_tmp[0].trim();

                        const channel_str = cmd_tmp[1].trim();
                        const ch_reg = /channel \'(.*)\';/;
                        var match_val = channel_str.match(ch_reg);
                        if (match_val.length>1){
                            a['channel'] = match_val[1];
                        }
                    }

                    var vlist = val.split(',');
                    for (var i in vlist) {
                        var tmp = toTrim(vlist[i]);
                        var tmp_a = tmp.split(" ");
                        var real_tmp = tmp_a[tmp_a.length-1];
                        var kv = real_tmp.split("=");
                        a[kv[0]] = kv[1].replace("'",'').replace("'",'');
                    }

                    if ('MASTER_HOST' in a){
                        $('input[name="ip"]').val(a['MASTER_HOST']);
                        $('input[name="port"]').val(a['MASTER_PORT']);
                        $('input[name="user"]').val(a['MASTER_USER']);
                        $('input[name="pass"]').val(a['MASTER_PASSWORD']);
                    } else {
                        $('input[name="ip"]').val(a['SOURCE_HOST']);
                        $('input[name="port"]').val(a['SOURCE_PORT']);
                        $('input[name="user"]').val(a['SOURCE_USER']);
                        $('input[name="pass"]').val(a['SOURCE_PASSWORD']);
                    }
                });
            },
            yes:function(index){
                var ip = $('input[name="ip"]').val();
                var port = $('input[name="port"]').val();
                var user = $('input[name="user"]').val();
                var pass = $('input[name="pass"]').val();
                var cmd = $('textarea[name="cmd"]').val();
                var mode = $('select[name="mode"]').val();

                var data = {ip:ip,port:port,cmd:cmd,user:user,pass:pass,mode:mode};
                myPost('add_slave_sync_user', data, function(ret_data){
                    layer.close(index);
                    var rdata = $.parseJSON(ret_data.data);
                    showMsg(rdata.msg,function(){
                        if (rdata.status){
                            getSlaveSyncUserPage();
                        }
                    },{icon: rdata.status ? 1 : 2},600);
                });
            }
        });
    });
}

function getSlaveSyncUserPage(page=1){
    var _data = {};    
    _data['page'] = page;
    _data['page_size'] = 5;
    _data['tojs'] ='getSlaveSyncUserPage';
    myPost('get_slave_sync_user_list', _data, function(data){
        var layerId = null;
        var rdata = [];
        try {
            rdata = $.parseJSON(data.data);
        } catch(e) {
            console.log(e);
        }

        var list = '';
        var user_list = rdata['data'];
        for (i in user_list) {
            var ip = user_list[i]['ip'];
            var port = user_list[i]['port'];
            var user = user_list[i]['user'];
            var apass = user_list[i]['pass'];
            
            var cmd = '未设置';
            if (user_list[i]['cmd']!=''){
                cmd = '已设置';
            }

            list += '<tr><td>'+ip+'</td>\
                <td>'+port+'</td>\
                <td>'+user+'</td>\
                <td>'+apass+'</td>\
                <td>'+cmd+'</td>\
                <td>\
                    <a class="btlink" onclick="addSlaveSyncUser(\''+ip+'\');">修改</a> | \
                    <a class="btlink" onclick="delSlaveSyncUser(\''+ip+'\');">删除</a>\
                </td>\
            </tr>';
        }

        $('.get-slave-ssh-list tbody').html(list);
        $('.dataTables_paginate_4').html(rdata['page']);
    });
}

function getSlaveCfg(){

    myPost('get_slave_sync_mode', '', function(data){
        var rdata = $.parseJSON(data.data);
        var mode_none = 'success';
        var mode_ssh = 'danger';
        var mode_sync_user = 'danger';
        if(rdata.status){
            var mode_none = 'danger';
            if (rdata.data == 'ssh'){
                var mode_ssh = 'success';
                var mode_sync_user = 'danger';
            } else {
                var mode_ssh = 'danger';
                var mode_sync_user = 'success';
            }
        }

        layerId = layer.open({
            type: 1,
            title: '同步配置',
            area: ['400px','180px'],
            content:"<div class='bt-form pd20 c6'>\
                    <p class='conf_p'>\
                        <span class='f14 c6 mr20'>当前从库同步模式</span>\
                        <b class='f14 c6 mr20'></b>\
                        <button class='btn btn-"+mode_none+" btn-xs slave-db-mode btn-none'>无</button>\
                        <button class='btn btn-"+mode_ssh+" btn-xs slave-db-mode btn-ssh'>SSH</button>\
                        <button class='btn btn-"+mode_sync_user+" btn-xs slave-db-mode btn-sync-user'>同步账户</button>\
                    </p>\
                    <hr />\
                    <p class='conf_p'>\
                        <span class='f14 c6 mr20'>配置设置</span>\
                        <b class='f14 c6 mr20'></b>\
                        <button class='btn btn-success btn-xs btn-slave-ssh'>SSH</button>\
                        <button class='btn btn-success btn-xs btn-slave-user'>同步账户</button>\
                    </p>\
                </div>",
            success:function(){
                $('.btn-slave-ssh').click(function(){
                    getSlaveSSHList();
                });

                $('.btn-slave-user').click(function(){
                    getSlaveUserList();
                });

                $('.slave-db-mode').click(function(){
                    var _this = this;
                    var mode = 'none';
                    if ($(this).hasClass('btn-ssh')){
                        mode = 'ssh';
                    }
                    if ($(this).hasClass('btn-sync-user')){
                        mode = 'sync-user';
                    }

                    myPost('set_slave_sync_mode', {mode:mode}, function(data){
                        var rdata = $.parseJSON(data.data);
                        showMsg(rdata.msg,function(){
                            $('.slave-db-mode').remove('btn-success').addClass('btn-danger');
                            $(_this).removeClass('btn-danger').addClass('btn-success');
                        },{icon:rdata.status?1:2},2000);
                    });

                });
            }
        });
    });
}


function getSlaveUserList(){

    var page = '<div class="dataTables_paginate_4 dataTables_paginate paging_bootstrap page" style="margin-top:0px;"></div>';
    page += '<div class="table_toolbar" style="left:0px;"><span class="sync btn btn-default btn-sm" onclick="addSlaveSyncUser()" title="">添加同步账户</span></div>';

    layerId = layer.open({
        type: 1,
        title: '同步账户列表',
        area: '600px',
        content:"<div class='bt-form pd20 c6'>\
                 <div class='divtable mtb10'>\
                    <div><table class='table table-hover get-slave-ssh-list'>\
                        <thead><tr><th>IP</th><th>PORT</th><th>同步账户</th><th>同步密码</th><th>CMD</th><th>操作</th></tr></thead>\
                        <tbody></tbody>\
                    </table></div>\
                    "+page +"\
                </div>\
            </div>",
        success:function(){
            getSlaveSyncUserPage(1);
        }
    });
}

function getSlaveSSHList(page=1){

    var page = '<div class="dataTables_paginate_4 dataTables_paginate paging_bootstrap page" style="margin-top:0px;"></div>';
    page += '<div class="table_toolbar" style="left:0px;"><span class="sync btn btn-default btn-sm" onclick="addSlaveSSH()" title="">添加SSH</span></div>';

    layerId = layer.open({
        type: 1,
        title: 'SSH列表',
        area: '600px',
        content:"<div class='bt-form pd20 c6'>\
                 <div class='divtable mtb10'>\
                    <div><table class='table table-hover get-slave-ssh-list'>\
                        <thead><tr><th>IP</th><th>PORT</th><th>同步账户</th><th>SSH</th><th>操作</th></tr></thead>\
                        <tbody></tbody>\
                    </table></div>\
                    "+page +"\
                </div>\
            </div>",
        success:function(){
            getSlaveSSHPage(1);
        }
    });
}

function handlerRun(){
    myPostN('get_slave_sync_cmd', {}, function(data){
        var rdata = $.parseJSON(data.data);
        var cmd = rdata['data'];
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
    });
}

function initSlaveStatus(){
    myPost('init_slave_status', '', function(data){
        var rdata = $.parseJSON(data.data);
        showMsg(rdata.msg,function(){
            if (rdata.status){
                masterOrSlaveConf();
            }
        },{icon:rdata.status?1:2},2000);
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
                    <div class="table_toolbar" style="left:0px;">\
                        <span class="sync btn btn-default btn-sm" onclick="getMasterRepSlaveListPage()" title="">同步账户列表</span>\
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

        var mdb_ver = $('.plugin_version').attr('version');

        myPost('get_slave_list', _data, function(data){
            var rdata = $.parseJSON(data.data);
            var list = '';

            var isHasSign = false;
            for(i in rdata.data){

                var v = rdata.data[i];
                if ('Channel_Name' in v && v['Channel_Name'] !=''){
                    isHasSign = true;
                }

                var status = "<a data-id="+i+"  class='btlink db_error'>异常</>";
                if (mdb_ver >= 8){                    
                    if (v['Replica_SQL_Running'] == 'Yes' && v['Replica_IO_Running'] == 'Yes'){
                        status = "正常";
                    }

                    list += '<tr>';
                    list += '<td>' + rdata.data[i]['Source_Host'] +'</td>';
                    list += '<td>' + rdata.data[i]['Source_Port'] +'</td>';
                    list += '<td>' + rdata.data[i]['Source_User'] +'</td>';
                    list += '<td>' + rdata.data[i]['Relay_Source_Log_File'] +'</td>';
                    list += '<td>' + rdata.data[i]['Replica_IO_Running'] +'</td>';
                    list += '<td>' + rdata.data[i]['Replica_SQL_Running'] +'</td>';

                } else {
                    if (v['Slave_SQL_Running'] == 'Yes' && v['Slave_IO_Running'] == 'Yes'){
                        status = "正常";
                    }

                    list += '<tr>';
                    list += '<td>' + rdata.data[i]['Master_Host'] +'</td>';
                    list += '<td>' + rdata.data[i]['Master_Port'] +'</td>';
                    list += '<td>' + rdata.data[i]['Master_User'] +'</td>';
                    list += '<td>' + rdata.data[i]['Master_Log_File'] +'</td>';
                    list += '<td>' + rdata.data[i]['Slave_IO_Running'] +'</td>';
                    list += '<td>' + rdata.data[i]['Slave_SQL_Running'] +'</td>';
                }
                

                if (isHasSign){
                    list += '<td>' + v['Channel_Name'] +'</td>';
                }

                list += '<td>' + status +'</td>';
                list += '<td style="text-align:right">' + 
                    '<a data-id="'+i+'" href="javascript:;" class="btlink btn_delete_slave" title="删除">删除</a>' +
                '</td>';
                list += '</tr>';
            }

            var signThead_th = '';
            if (isHasSign){
                var signThead_th = '<th>标识</th>';
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
                        '+signThead_th+'\
                        <th>状态</th>\
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

            $(".btn_delete_slave").click(function(){
                var id = $(this).data('id');
                var v = rdata.data[id];
                if ('Channel_Name' in v){
                    deleteSlave(v['Channel_Name']);
                } else{
                    deleteSlave();
                }
            });

             $('.db_error').click(function(){
                var id = $(this).data('id');
                var info = rdata.data[id];

                var err_line = "";
                err_line +="<tr>\
                    <td>IO错误</td>\
                    <td>"+ (info['Last_IO_Error'] == '' ? '无':info['Last_IO_Error'])+"</td>\
                </tr>";
                err_line +="<tr>\
                    <td>SQL错误</td>\
                    <td>"+(info['Last_SQL_Error'] == '' ? '无':info['Last_SQL_Error'])+"</td>\
                </tr>";

                err_line +="<tr>\
                    <td>状态</td>\
                    <td>"+(info['Slave_SQL_Running_State'] == '' ? '无':info['Slave_SQL_Running_State']) +"</td>\
                </tr>";


                var btn_list = ['复制错误',"取消"];
                if (info['Last_IO_Error'].search(/1236/i)>0){
                    btn_list = ['复制错误',"取消","尝试修复"];
                }
                layer.open({
                    type: 1,
                    title: '同步异常信息',
                    area: ['600px','300px'],
                    btn:btn_list,
                    content:"<form class='bt-form pd15'>\
                        <div class='divtable mtb10'>\
                        <div class='tablescroll'>\
                            <table class='table table-hover' width='100%' cellspacing='0' cellpadding='0' border='0' style='border: 0 none;'>\
                            <thead><tr>\
                                <th style='width:80px;'>类型</th>\
                                <th>内容</th>\
                            </tr></thead>\
                            <tbody>"+ err_line +"</tbody>\
                            </table>\
                        </div>\
                    </div>\
                    </form>",
                    success:function(){
                        if (info['Last_IO_Error'] != ''){
                            copyText(info['Last_IO_Error']);
                            return;
                        }

                        if (info['Last_SQL_Error'] != ''){
                            copyText(info['Last_SQL_Error']);
                            return;
                        }

                        if (info['Slave_SQL_Running_State'] != ''){
                            copyText(info['Slave_SQL_Running_State']);
                            return;
                        }
                    },
                    yes:function(){
                        if (info['Last_IO_Error'] != ''){
                            copyText(info['Last_IO_Error']);
                            return;
                        }

                        if (info['Last_SQL_Error'] != ''){
                            copyText(info['Last_SQL_Error']);
                            return;
                        }

                        if (info['Slave_SQL_Running_State'] != ''){
                            copyText(info['Slave_SQL_Running_State']);
                            return;
                        }
                    },
                    btn3:function(){
                        myPost('try_slave_sync_bugfix', {}, function(data){
                            var rdata = $.parseJSON(data.data);
                            showMsg(rdata.msg, function(){
                                masterOrSlaveConf();
                            },{ icon: rdata.status ? 1 : 5 },2000);
                        });
                    }
                });
            });
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
                    '<a href="javascript:;" class="btlink" onclick="getFullSyncStatus(\''+rdata.data[i]['name']+'\')" title="同步">同步</a> | ' +
                    '<a href="javascript:;" class="btlink" onclick="dataSyncVerify(\''+rdata.data[i]['name']+'\')" title="数据校验">数据校验</a>' +
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
                    <div class="table_toolbar" style="left:0px;">\
                        <span class="sync btn btn-default btn-sm" onclick="handlerRun()" title="免登录设置后,需要手动执行一下!">手动命令</span>\
                        <span class="sync btn btn-default btn-sm" onclick="getFullSyncStatus(\'ALL\')" title="全量同步">全量同步</span>\
                    </div>\
                </div>';

            $(".table_slave_list").html(con);
            $('#databasePage').html(rdata.page);
        });
    }


    function getMasterStatus(){
        myPost('get_master_status', '', function(rdata){
            var rdata = $.parseJSON(rdata.data);
            // console.log('mode:',rdata.data);
            if ( typeof(rdata.status) != 'undefined' && !rdata.status && rdata.data == 'pwd'){
                layer.msg(rdata.msg, {icon:2});
                return;
            }

            var rdata = rdata.data;
            var limitCon = '\
                <p class="conf_p">\
                    <span class="f14 c6 mr20">主从同步模式</span><span class="f14 c6 mr20"></span>\
                    <button class="btn '+(!(rdata.mode == "classic") ? 'btn-danger' : 'btn-success')+' btn-xs db-mode btn-classic">经典</button>\
                    <button class="btn '+(!(rdata.mode == "gtid") ? 'btn-danger' : 'btn-success')+' btn-xs db-mode btn-gtid">GTID</button>\
                </p>\
                <hr/>\
                <p class="conf_p">\
                    <span class="f14 c6 mr20">Master[主]配置</span><span class="f14 c6 mr20"></span>\
                    <button class="btn '+(!rdata.status ? 'btn-danger' : 'btn-success')+' btn-xs btn-master">'+(!rdata.status ? '未开启' : '已开启') +'</button>\
                    <button class="btn btn-success btn-xs" onclick="resetMaster()">重置</button>\
                </p>\
                <hr/>\
                <!-- master list -->\
                <div class="safe bgw table_master_list"></div>\
                <hr/>\
                <!-- class="conf_p" -->\
                <p class="conf_p">\
                    <span class="f14 c6 mr20">Slave[从]配置</span><span class="f14 c6 mr20"></span>\
                    <button class="btn '+(!rdata.slave_status ? 'btn-danger' : 'btn-success')+' btn-xs btn-slave">'+(!rdata.slave_status ? '未启动' : '已启动') +'</button>\
                    <button class="btn btn-success btn-xs" onclick="getSlaveCfg()" >同步配置</button>\
                    <button class="btn btn-success btn-xs" onclick="initSlaveStatus()" >初始化</button>\
                </p>\
                <hr/>\
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

            $('.db-mode').click(function(){
                if ($(this).hasClass('btn-success')){
                    //no action
                    return;
                }

                var mode = 'classic';
                if ($(this).hasClass('btn-gtid')){
                    mode = 'gtid';
                }

                layer.open({
                    type:1,
                    title:"MySQL主从模式切换",
                    shadeClose:false,
                    btnAlign: 'c',
                    btn: ['切换并重启', '切换不重启'],
                    yes: function(index, layero){
                        this.change(index,mode,"yes");

                    },
                    btn2: function(index, layero){
                        this.change(index,mode,"no");
                        return false;
                    },
                    change:function(index,mode,reload){
                        console.log(index,mode,reload);
                        myPost('set_dbrun_mode',{'mode':mode,'reload':reload},function(data){
                            layer.close(index);
                            var rdata = $.parseJSON(data.data);
                            showMsg(rdata.msg ,function(){
                                getMasterStatus();
                            },{ icon: rdata.status ? 1 : 5 });
                        });
                    }
                });
            });

            if (rdata.status){
                getMasterDbList();
            }
            
            // if (rdata.slave_status){
                getAsyncMasterDbList();
                getAsyncDataList()
            // }
        });
    }
    getMasterStatus();
}
