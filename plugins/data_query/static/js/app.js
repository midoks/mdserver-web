$(document).ready(function(){
    var tag = $.getUrlParam('tag');
    if(tag == 'data_query'){
        initDataQuery();
    }
});

function redisPostCB(method, args, callback){
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });

    var req_data = {};
    req_data['name'] = 'data_query';
    req_data['func'] = method;
    req_data['script']='nosql_redis';
    args['version'] = '';
 
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

function mgdbPostCB(method, args, callback){
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });

    var req_data = {};
    req_data['name'] = 'data_query';
    req_data['func'] = method;
    req_data['script']='nosql_mongodb';
    args['version'] = '';
 
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

function memPostCB(method, args, callback){
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });

    var req_data = {};
    req_data['name'] = 'data_query';
    req_data['func'] = method;
    req_data['script']='nosql_memcached';
    args['version'] = '';
 
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

function myPostCB(method, args, callback){
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });

    var req_data = {};
    req_data['name'] = 'data_query';
    req_data['func'] = method;
    req_data['script']='sql_mysql';
    args['version'] = '';
 
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


function myPostCBN(method, args, callback){
    var req_data = {};
    req_data['name'] = 'data_query';
    req_data['func'] = method;
    req_data['script']='sql_mysql';
    args['version'] = '';
 
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

function pgPostCB(method, args, callback){
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });

    var req_data = {};
    req_data['name'] = 'data_query';
    req_data['func'] = method;
    req_data['script']='sql_postgresql';
    args['version'] = '';
 
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


function pgPostCBN(method, args, callback){
    var req_data = {};
    req_data['name'] = 'data_query';
    req_data['func'] = method;
    req_data['script']='sql_postgresql';
    args['version'] = '';
 
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


function selectTab(tab = 'redis'){
    $('.tab-view-box .tab-con').addClass('hide').removeClass('show').removeClass('w-full');
    $('#'+tab).removeClass('hide').addClass('w-full');
}

function showInstallLayer(){
    $('.mask_layer').css('display','block');
}

function closeInstallLayer(){
    $('.mask_layer').css('display','none');
}

function initTabFunc(tab){
    switch(tab){
        case 'redis':initTabRedis();break;
        case 'mongodb':initTabMongodb();break;
        case 'memcached':initTabMemcached();break;
        case 'mysql':initTabMySQL();break;
        case 'postgresql':initTabPostgresql();break;
        case 'default:':initTabRedis();break;
    }
}

function initDataQuery(){
    var tab = $('#cutTab .tabs-item.active').data('name');
    initTabFunc(tab);
    $('#cutTab .tabs-item').click(function(){
        var tab = $(this).data('name');
        $('#cutTab .tabs-item').removeClass('active');
        $(this).addClass('active');
        selectTab(tab);
        initTabFunc(tab);
    });    
}

function initTabRedis(){
    //渲染数据
    redisGetList();

    $('#redis_add_key').unbind('click').click(function(){
        redisAdd();
    });

    //搜索
    $('#redis_ksearch').unbind('click').keyup(function(e){
        if (e.keyCode == 13){
            var val = $(this).val();
            if (val == ''){
                layer.msg('搜索不能为空!',{icon:7});
                return;
            }
            redisGetKeyList(1, val);
        }
    });

    $('#redis_ksearch_span').unbind('click').click(function(){
        var val = $('#redis_ksearch').val();
        if (val == ''){
            layer.msg('搜索不能为空!',{icon:7});
            return;
        }
        redisGetKeyList(1, val);
    });

    //批量删除
    $('#redis_batch_del').unbind('click').click(function(){
        redisBatchDel();
    });

    //清空所有
    $('#redis_clear_all').unbind('click').click(function(){
        redisBatchClear();
    });

    readerTableChecked();
}

function initTabMongodb(){
    //渲染数据
    mongodbGetList();
}


function initTabMemcached(){
    memcachedGetList();

    $('#memcached_add_key').unbind('click').click(function(){
        memcachedAdd();
    });

    $('#memcached_clear_all').unbind('click').click(function(){
        var sid = memcachedGetSid();
        memPostCB('clear',{'sid':sid} ,function(rdata){
            console.log("xxx",rdata);
            showMsg(rdata.data.msg,function(){
                if (rdata.data.status){
                    memcachedGetList();
                }
            },{icon: rdata.data.status ? 1 : 2}, 2000);
        });
    });
}

var mysql_timer = null;
function initTabMySQL(){

    mysqlGetServerList(function(){
        mysqlGetDbList();
        mysqlProcessList();
    });

    clearInterval(mysql_timer);    
    mysql_timer = setInterval(function(){
        var name = $('#mysql_list_tab .tab-nav span.on').data('name');
        mysqlRunMysqlTab(name);

        var fname = $('#cutTab .tab-list .active').data('name');
        if (fname != 'mysql'){
            clearInterval(mysql_timer);
        }
    },2000);

    $('#mysql_list_tab .tab-nav span').unbind('click').click(function(){
        $('#mysql_list_tab .tab-nav span').removeClass('on');
        $(this).addClass('on');
        var name = $(this).data('name');
        mysqlRunMysqlTab(name);
    });

    mysqlCommonFunc();
}

function mysqlCommonFuncMysqlNSQL(){
    function renderSQL(){
        var sid = mysqlGetSid();
        var filter_db = $('#filter_db').is(':checked');
        myPostCBN('get_topn_list',{'sid':sid,'filter_db':filter_db ? 'yes':'no'} ,function(rdata){
            var data = rdata.data;
            if (data['status']){
                var items = data.data;
                var tbody = '';
                for (var i = 0; i < items.length; i++) {
                    var t = '<tr>';
                    t += '<td>'+items[i].query+'</td>';
                    t += '<td>'+items[i].db+'</td>';
                    t += '<td>'+items[i].last_seen+'</td>';
                    t += '<td>'+items[i].exec_count+'</td>';
                    t += '<td>'+items[i].max_latency+'</td>';
                    t += '<td>'+items[i].avg_latency+'</td>';
                    t += '</tr>';
                    tbody += t;
                }
                $('#topn_list tbody').html(tbody);
            } else {
                layer.msg(data.msg,{icon:2});
            }
        });
    }

    var sql_timer = null;
    layer.open({
        type: 1,
        title: "查询执行次数最频繁的前N条SQL语句",
        area: ['1200px', '500px'],
        closeBtn: 1,
        shadeClose: false,
        content: '<div class="bt-form pd20 divtable taskdivtable">\
            <div class="mr20 pull-left" style="border-right: 1px solid #ccc; padding-right: 20px;">\
                <div class="ss-text pull-left">\
                    <em>实时监控</em>\
                    <div class="ssh-item">\
                        <input class="btswitch btswitch-ios" id="real_time_monitoring" type="checkbox">\
                        <label id="real_time_label" class="btswitch-btn" for="real_time_monitoring"></label>\
                    </div>\
                </div>\
                <div class="ss-text pull-left" style="padding-left:10px;">\
                    <em>过滤数据库</em>\
                    <div class="ssh-item">\
                        <input class="btswitch btswitch-ios" id="filter_db" type="checkbox">\
                        <label class="btswitch-btn" for="filter_db"></label>\
                    </div>\
                </div>\
            </div>\
            <hr />\
            <table class="table table-hover" id="topn_list">\
                <thead>\
                    <th>SQL</th>\
                    <th style="width:100px;">数据名</th>\
                    <th>最近时间</th>\
                    <th style="width:100px;">总次数</th>\
                    <th style="width:100px;">最大时间</th>\
                    <th style="width:100px;">平均时间</th>\
                </thead>\
                <tbody></tbody>\
            </table>\
        </div>',
        success:function(i,l){
            renderSQL();

            $('#real_time_label').click(function(){
                sql_timer = setInterval(function(){
                    var t = $('#real_time_monitoring').is(':checked');
                    if (t){
                        renderSQL();
                    } else{
                        clearInterval(sql_timer);
                    }
                }, 3000);
            });
        }
    });
}

function mysqlCommonFuncMysqlNet(){
    function renderSQL(){
        var sid = mysqlGetSid();
        myPostCBN('get_net_list',{'sid':sid} ,function(rdata){
            var data = rdata.data;
            if (data['status']){
                var items = data.data;
                var tbody = '';
                for (var i = 0; i < items.length; i++) {
                    var t = '<tr>';
                    t += '<td>'+items[i]['current_time']+'</td>';
                    t += '<td>'+items[i]['select']+'</td>';
                    t += '<td>'+items[i]['insert']+'</td>';
                    t += '<td>'+items[i]['update']+'</td>';
                    t += '<td>'+items[i]['delete']+'</td>';
                    t += '<td>'+items[i]['conn']+'</td>';
                    t += '<td>'+items[i]['max_conn']+'</td>';
                    t += '<td>'+items[i]['recv_mbps']+'</td>';
                    t += '<td>'+items[i]['send_mbps']+'</td>';
                    t += '</tr>';
                    tbody += t;
                }
                $('#net_list tbody').html(tbody);
            } else {
                layer.msg(data.msg,{icon:2});
            }
        });
    }

    var sql_timer = null;
    layer.open({
        type: 1,
        title: "MySQL服务器的QPS/TPS/网络带宽指标",
        area: ['750px', '220px'],
        closeBtn: 1,
        shadeClose: false,
        content: '<div class="bt-form pd20 divtable taskdivtable">\
            <div class="mr20 pull-left" style="border-right: 1px solid #ccc; padding-right: 20px;">\
                <div class="ss-text pull-left">\
                    <em>实时监控</em>\
                    <div class="ssh-item">\
                        <input class="btswitch btswitch-ios" id="real_qps_monitoring" type="checkbox">\
                        <label id="real_qps_label" class="btswitch-btn" for="real_qps_monitoring"></label>\
                    </div>\
                </div>\
            </div>\
            <hr />\
            <table class="table table-hover" id="net_list">\
                <thead>\
                    <th style="width:160px;">时间</th>\
                    <th style="width:50px;">Select</th>\
                    <th style="width:50px;">Insert</th>\
                    <th style="width:50px;">Update</th>\
                    <th style="width:50px;">Delete</th>\
                    <th style="width:50px;">Conn</th>\
                    <th style="width:50px;">Max_conn</th>\
                    <th style="width:90px;">Recv</th>\
                    <th style="width:90px;">Send</th>\
                </thead>\
                <tbody></tbody>\
            </table>\
        </div>',
        success:function(i,l){
            renderSQL();

            $('#real_qps_label').click(function(){
                sql_timer = setInterval(function(){
                    var t = $('#real_qps_monitoring').is(':checked');
                    if (t){
                        renderSQL();
                    } else{
                        clearInterval(sql_timer);
                    }
                }, 3000);
            });
        }
    });
}

function mysqlCommonFuncRedundantIndexes(){
    function renderSQL(){
        var sid = mysqlGetSid();
        myPostCBN('get_redundant_indexes',{'sid':sid} ,function(rdata){
            var data = rdata.data;
            if (data['status']){
                var items = data.data;
                var tbody = '';
                for (var i = 0; i < items.length; i++) {
                    var t = '<tr>';
                    t += '<td>'+items[i]['table_schema']+'</td>';
                    t += '<td>'+items[i]['table_name']+'</td>';
                    t += '<td>'+items[i]['redundant_index_name']+'</td>';
                    t += '<td>'+items[i]['redundant_index_columns']+'</td>';
                    t += '<td>'+items[i]['sql_drop_index']+'</td>';
                    t += '<td><a class="exec btlink" index="'+i+'">执行</a></td>';
                    t += '</tr>';
                    tbody += t;
                }
                $('#redundant_indexes tbody').html(tbody);
                $('#redundant_indexes tbody .exec').click(function(){
                    var index = $(this).attr('index');
                    myPostCB('redundant_indexes_cmd', {'sid':sid, 'index':index}, function(rdata){
                        var data = rdata.data;
                        showMsg(data.msg,function(){
                            if (data.status){
                                renderSQL();
                            }
                        },{icon: data.status ? 1 : 2}, 2000);
                    });
                });
            } else {
                layer.msg(data.msg,{icon:2});
            }
        });
    }

    layer.open({
        type: 1,
        title: "查看重复或冗余的索引",
        area: ['1100px', '400px'],
        closeBtn: 1,
        shadeClose: false,
        content: '<div class="bt-form pd20 divtable taskdivtable">\
            <table class="table table-hover" id="redundant_indexes">\
                <thead>\
                    <th style="width:100px;">数据库名</th>\
                    <th style="width:50px;">表名</th>\
                    <th style="width:50px;">冗余索引名</th>\
                    <th style="width:50px;">冗余索引列名</th>\
                    <th style="width:300px;">删除冗余索引SQL</th>\
                    <th style="width:30px;">操作</th>\
                </thead>\
                <tbody></tbody>\
            </table>\
        </div>',
        success:function(i,l){
            renderSQL();
        }
    });
}

function mysqlCommonFuncTableInfo(){
    function renderSQL(){
        var sid = mysqlGetSid();
        myPostCBN('get_table_info',{'sid':sid} ,function(rdata){
            var data = rdata.data;
            if (data['status']){
                var items = data.data;
                var tbody = '';
                for (var i = 0; i < items.length; i++) {
                    var t = '<tr>';
                    t += '<td>'+items[i]['TABLE_SCHEMA']+'</td>';
                    t += '<td>'+items[i]['TABLE_NAME']+'</td>';
                    t += '<td>'+items[i]['ENGINE']+'</td>';
                    t += '<td>'+items[i]['DATA_LENGTH']+'</td>';
                    t += '<td>'+items[i]['INDEX_LENGTH']+'</td>';
                    t += '<td>'+items[i]['TOTAL_LENGTH']+'</td>';
                    t += '<td>'+items[i]['COLUMN_NAME']+'</td>';
                    t += '<td>'+items[i]['COLUMN_TYPE']+'</td>';
                    t += '<td>'+items[i]['AUTO_INCREMENT']+'</td>';
                    t += '<td>'+items[i]['RESIDUAL_AUTO_INCREMENT']+'</td>';
                    t += '</tr>';
                    tbody += t;
                }
                $('#mysql_data_id tbody').html(tbody);
            } else {
                layer.msg(data.msg,{icon:2});
            }
        });
    }

    layer.open({
        type: 1,
        title: "统计库里每个表的大小",
        area: ['1200px', '400px'],
        closeBtn: 1,
        shadeClose: false,
        content: '<div class="bt-form pd20 divtable taskdivtable">\
            <table class="table table-hover" id="mysql_data_id">\
                <thead>\
                    <th style="width:100px;">库名</th>\
                    <th style="width:50px;">表名</th>\
                    <th style="width:80px;">储存引擎</th>\
                    <th style="width:150px;">数据大小(GB)</th>\
                    <th style="width:130px;">索引大小(GB)</th>\
                    <th style="width:100px;">总计(GB)</th>\
                    <th style="width:150px;">主键自增字段</th>\
                    <th style="width:200px;">主键字段属性</th>\
                    <th style="width:150px;">主键自增当前</th>\
                    <th style="width:150px;">主键自增剩余</th>\
                </thead>\
                <tbody></tbody>\
            </table>\
        </div>',
        success:function(i,l){
            renderSQL();
        }
    });
}

function mysqlCommonFuncConnCount(){
    function renderSQL(){
        var sid = mysqlGetSid();
        myPostCBN('get_conn_count',{'sid':sid} ,function(rdata){
            var data = rdata.data;
            if (data['status']){
                var items = data.data;
                var tbody = '';
                for (var i = 0; i < items.length; i++) {
                    var t = '<tr>';
                    t += '<td>'+items[i]['user']+'</td>';
                    t += '<td>'+items[i]['db']+'</td>';
                    t += '<td>'+items[i]['Client_IP']+'</td>';
                    t += '<td>'+items[i]['count']+'</td>';
                    t += '</tr>';
                    tbody += t;
                }
                $('#app_ip_list tbody').html(tbody);
            } else {
                layer.msg(data.msg,{icon:2});
            }
        });
    }

    var sql_timer = null;
    layer.open({
        type: 1,
        title: "查看应用端IP连接数总和",
        area: ['700px', '420px'],
        closeBtn: 1,
        shadeClose: false,
        content: '<div class="bt-form pd20 divtable taskdivtable">\
            <div class="mr20 pull-left" style="border-right: 1px solid #ccc; padding-right: 20px;">\
                <div class="ss-text pull-left">\
                    <em>实时监控</em>\
                    <div class="ssh-item">\
                        <input class="btswitch btswitch-ios" id="app_ip_monitoring" type="checkbox">\
                        <label id="app_ip_label" class="btswitch-btn" for="app_ip_monitoring"></label>\
                    </div>\
                </div>\
            </div>\
            <hr />\
            <table class="table table-hover" id="app_ip_list">\
                <thead>\
                    <th style="width:160px;">连接用户</th>\
                    <th style="width:50px;">数据库名</th>\
                    <th style="width:50px;">应用端IP</th>\
                    <th style="width:50px;">数量</th>\
                </thead>\
                <tbody></tbody>\
            </table>\
        </div>',
        success:function(i,l){
            renderSQL();

            $('#app_ip_label').click(function(){
                sql_timer = setInterval(function(){
                    var t = $('#app_ip_monitoring').is(':checked');
                    if (t){
                        renderSQL();
                    } else{
                        clearInterval(sql_timer);
                    }
                }, 3000);
            });
        }
    });
}

function mysqlCommonFuncFpkInfo(){
    function renderSQL(){
        var sid = mysqlGetSid();
        myPostCBN('get_fpk_info',{'sid':sid} ,function(rdata){
            var data = rdata.data;
            if (data['status']){
                var items = data.data;
                var tbody = '';
                for (var i = 0; i < items.length; i++) {
                    var t = '<tr>';
                    t += '<td>'+items[i]['table_schema']+'</td>';
                    t += '<td>'+items[i]['table_name']+'</td>';
                    t += '</tr>';
                    tbody += t;
                }
                $('#mysql_data_id tbody').html(tbody);
            } else {
                layer.msg(data.msg,{icon:2});
            }
        });
    }

    layer.open({
        type: 1,
        title: "快速找出没有主键的表",
        area: ['800px', '400px'],
        closeBtn: 1,
        shadeClose: false,
        content: '<div class="bt-form pd20 divtable taskdivtable">\
            <table class="table table-hover" id="mysql_data_id">\
                <thead>\
                    <th style="width:100px;">库名</th>\
                    <th style="width:50px;">表名</th>\
                </thead>\
                <tbody></tbody>\
            </table>\
        </div>',
        success:function(i,l){
            renderSQL();
        }
    });
}

function mysqlCommonFuncLockSQL(){
    function renderSQL(){
        var sid = mysqlGetSid();
        myPostCBN('get_lock_sql',{'sid':sid} ,function(rdata){
            var data = rdata.data;
            if (data['status']){
                var items = data.data;
                var tbody = '';
                for (var i = 0; i < items.length; i++) {
                    var t = '<tr>';
                    t += '<td>'+items[i]['trx_id']+'</td>';
                    t += '<td>'+items[i]['trx_state']+'</td>';
                    t += '<td>'+items[i]['trx_started']+'</td>';
                    t += '<td>'+items[i]['processlist_id']+'</td>';
                    t += '<td>'+items[i]['info']+'</td>';
                    t += '<td>'+items[i]['user']+'</td>';
                    t += '<td>'+items[i]['host']+'</td>';
                    t += '<td>'+items[i]['db']+'</td>';
                    t += '<td>'+items[i]['command']+'</td>';
                    t += '<td>'+items[i]['state']+'</td>';
                    t += '<td>'+items[i]['sql_kill_blocking_query']+'</td>';
                    t += '<td><a class="exec btlink" index="'+i+'">执行</a></td>';
                    t += '</tr>';
                    tbody += t;
                }
                $('#mysql_data_id tbody').html(tbody);

                $('#mysql_data_id tbody .exec').click(function(){
                    var index = $(this).attr('index');
                    var pid = items[index]['processlist_id'];
                    myPostCB('kill_lock_pid', {'sid':sid, 'pid':pid}, function(rdata){
                        var data = rdata.data;
                        showMsg(data.msg,function(){
                            if (data.status){
                                renderSQL();
                            }
                        },{icon: data.status ? 1 : 2}, 2000);
                    });
                });
            } else {
                layer.msg(data.msg,{icon:2});
            }
        });
    }

    layer.open({
        type: 1,
        title: "查看当前锁阻塞的SQL",
        area: ['1000px', '400px'],
        closeBtn: 1,
        shadeClose: false,
        content: '<div class="bt-form pd20 divtable taskdivtable">\
            <div class="mr20 pull-left" style="border-right: 1px solid #ccc; padding-right: 20px;">\
                <button id="kill_all" type="button" class="btn btn-default btn-sm">关闭所有阻塞</button>\
            </div>\
            <hr />\
            <table class="table table-hover" id="mysql_data_id">\
                <thead>\
                    <th style="width:80px;">事务ID</th>\
                    <th style="width:80px;">事务状态</th>\
                    <th style="width:220px;">执行时间</th>\
                    <th style="width:100px;">线程ID</th>\
                    <th style="width:50px;">Info</th>\
                    <th style="width:50px;">user</th>\
                    <th style="width:50px;">host</th>\
                    <th style="width:50px;">db</th>\
                    <th style="width:50px;">command</th>\
                    <th style="width:50px;">state</th>\
                    <th style="width:140px;">kill</th>\
                    <th style="width:50px;">操作</th>\
                </thead>\
                <tbody></tbody>\
            </table>\
        </div>',
        success:function(i,l){
            renderSQL();

            $('#kill_all').unbind('click').click(function(){
                var sid = mysqlGetSid();
                myPostCB('kill_all_lock', {'sid':sid}, function(rdata){
                    var data = rdata.data;
                    showMsg(data.msg,function(){
                        if (data.status){
                            renderSQL();
                        }
                    },{icon: data.status ? 1 : 2}, 2000);
                });
            });
        }
    });
}

function mysqlCommonFuncDeadlockInfo(){

    function renderSQL(){
        var sid = mysqlGetSid();
        myPostCBN('get_deadlock_info',{'sid':sid} ,function(rdata){
            var data = rdata.data;
            $('#info_log').html(data.data);
            var ob = document.getElementById('info_log');
            ob.scrollTop = ob.scrollHeight; 
        });
    }

    layer.open({
        type: 1,
        title: "查看死锁信息",
        area: ['800px', '400px'],
        closeBtn: 1,
        shadeClose: false,
        content: '<div class="bt-form pd15">\
            <textarea readonly="" style="margin: 0px;height: 330px;width: 100%;background-color: #333;color:#fff; padding:0 5px" id="info_log"></textarea>\
        </div>',
        success:function(i,l){
            renderSQL();
        }
    });
}

function mysqlCommonFuncSlaveStatus(){

    function renderSQL(){
        var sid = mysqlGetSid();
        myPostCBN('get_slave_status',{'sid':sid} ,function(rdata){
            var data = rdata.data;
            $('#info_log').html(data.data);
            var ob = document.getElementById('info_log');
            ob.scrollTop = ob.scrollHeight; 
        });
    }

    layer.open({
        type: 1,
        title: "查看主从复制信息",
        area: ['800px', '400px'],
        closeBtn: 1,
        shadeClose: false,
        content: '<div class="bt-form pd15">\
            <textarea readonly="" style="margin: 0px;height: 330px;width: 100%;background-color: #333;color:#fff; padding:0 5px" id="info_log"></textarea>\
        </div>',
        success:function(i,l){
            renderSQL();
        }
    });
}

function mysqlSlaveSyncProgress(){
    var html = '<div>';
    html += '<div class="slave_sync_progress" id="slave_sync_progress" style="width:750px;height:350px;"></div>';
    html += '<hr/><div class="slave_sync_info"></div>';
    html += '</div>';
    var timer = null;
    var statEc = null;
    layer.open({
        type: 1,
        title: "查看从库延迟进度",
        area: ['800px', '500px'],
        closeBtn: 1,
        shadeClose: false,
        content:'<div class="bt-form pd20">' + html + '</div>',
        success:function(i,l){
            // console.log(i,l);
            statEc = echarts.init(document.getElementById('slave_sync_progress'));

            var chat = {};
            chat['tooltip'] = {
                show:true,
                trigger: 'axis',
                backgroundColor: 'rgba(255,255,255,0.8)',
                axisPointer: { 
                    type: 'line',
                    lineStyle: { color: 'rgba(150,150,150,0.2)'}
                },
                textStyle: {
                    color: '#666',
                    fontSize: '14px',
                },
            }

            legend_name = ["延迟进度", "回放延迟", '已拉取的GTID集合积压'];
            var option = {
                tooltip:chat['tooltip'],
                backgroundColor:'#fff',
                legend:{
                    data:legend_name,
                    left:'center',
                    top:'94%',
                },
                // grid: {left: 60, right: 60, top: 70, bottom: 50 },
                graphic:[{
                    type: 'group',
                    right: 750,
                    top: 0,
                    z: 100,
                    children: [{
                        type: 'text',
                        left: 'center',
                        top: 'center',
                        z: 100,
                        style: {
                            fill: '#ccc',
                            text: "延迟进度",
                            font: '16px Arial'
                        }
                    }]
                }],
                xAxis: { type: 'category', boundaryGap: false, data: [],},
                yAxis: [
                  { type: 'value', name: legend_name[0]},
                  { type: 'value', name: legend_name[1]},
                ],
                series: [
                    {
                        name:legend_name[0],
                        yAxisIndex: 0,
                        data: [],
                        type: 'line',
                        smooth: true,
                        showSymbol: false,
                        lineStyle: { color: '#ee6666' },
                        itemStyle: { color: '#ee6666' },
                    },
                    {
                        name:legend_name[1],
                        yAxisIndex: 1,
                        data: [],
                        type: 'line',
                        smooth: true,
                        showSymbol: false,
                        lineStyle: { color: '#3A84FF' },
                        itemStyle: { color: '#3A84FF' },
                    },
                ]
            };
            var xData = [''];
            var yData = ['0'];
            var pdData = ['0']
            statEc.setOption(option);
            statEc.setOption({
                xAxis: {
                    data: xData
                },
                series: [
                    { name: legend_name[0], data: yData},
                    { name: legend_name[1], data: pdData}
                ]
            });
            var timer = setInterval(function(){
                var sid = mysqlGetSid();
                myPostCBN('get_slave_runtime',{'sid':sid} ,function(rdata){
                    if (!rdata.status){
                        return;
                    }
                    var data = rdata.data;
                    if (!data.status){
                        return;
                    }

                    var real_data = data.data;
                    var my_status = real_data.data;
                    var pd_data = my_status['Read_Master_Log_Pos'] - my_status['Exec_Master_Log_Pos'];
                    var retrieved_gtid = 0;

                    var seconds_behind_master = 0;
                    if ('Seconds_Behind_Source' in my_status){
                        seconds_behind_master = real_data.data["Seconds_Behind_Source"];
                    } else {
                        seconds_behind_master = real_data.data["Seconds_Behind_Master"];
                    } 

                    if (my_status['Retrieved_Gtid_Set'] != ''){
                        // 639b3c89-1a74-11f0-8027-7cd30ab0ff74:7729919001-7735855943
                        var t = my_status['Retrieved_Gtid_Set'];
                        t = t.split(":");
                        t = t[1].split("-");
                        console.log(t);
                    }
                    
                    console.log('data:',data.data);

                    xData.push(real_data.time);
                    yData.push(seconds_behind_master);
                    pdData.push(pd_data);
                    

                    if (xData.length > 20){
                        xData.shift();
                        yData.shift();
                        pdData.shift();
                    }

                    statEc.setOption({
                        xAxis: {
                            data: xData
                        },
                        series: [
                            { name: legend_name[0], data: yData},
                            { name: legend_name[1], data: pdData}
                        ]
                    });
                });
            },3000);
        },
        // 弹窗关闭后清理定时器与图表实例,避免重复打开产生多个定时器并访问已销毁实例
        end:function(){
            if (timer){ clearInterval(timer); timer = null; }
            if (statEc){ statEc.dispose(); statEc = null; }
        }
    });

}

function mysqlCommonFunc(){
    $('#mysql_common').unbind('click').click(function(){
        layer.open({
            type: 1,
            title: "MySQL常用功能",
            area: ['600px', '230px'],
            closeBtn: 1,
            shadeClose: false,
            content: '<div class="bt-form pd20">\
                <button style="margin-bottom: 8px;" id="mysql_top_nsql" type="button" class="btn btn-default btn-sm">查询执行次数最频繁的前N条SQL语句</button>\
                <button style="margin-bottom: 8px;" id="mysql_net_stat" type="button" class="btn btn-default btn-sm">MySQL服务器的QPS/TPS/网络带宽指标</button>\
                <button style="margin-bottom: 8px;" id="mysql_redundant_indexes" type="button" class="btn btn-default btn-sm">查看重复或冗余的索引</button>\
                <button style="margin-bottom: 8px;" id="mysql_table_info" type="button" class="btn btn-default btn-sm">统计库里每个表的大小</button>\
                <button style="margin-bottom: 8px;" id="mysql_conn_count" type="button" class="btn btn-default btn-sm">查看应用端IP连接数总和</button>\
                <button style="margin-bottom: 8px;" id="mysql_fpk_info" type="button" class="btn btn-default btn-sm">快速找出没有主键的表</button>\
                <button style="margin-bottom: 8px;" id="mysql_lock_sql" type="button" class="btn btn-default btn-sm">查看当前锁阻塞的SQL</button>\
                <button style="margin-bottom: 8px;" id="mysql_deadlock_info" type="button" class="btn btn-default btn-sm">查看死锁信息</button>\
                <button style="margin-bottom: 8px;" id="mysql_slave_status" type="button" class="btn btn-default btn-sm">查看主从复制信息</button>\
                <button style="margin-bottom: 8px;" id="mysql_slave_sync_progress" type="button" class="btn btn-default btn-sm">查看从延迟进度</button>\
            </div>',
            success:function(i,l){
                $('#mysql_top_nsql').click(function(){
                    mysqlCommonFuncMysqlNSQL();
                });

                $('#mysql_net_stat').click(function(){
                    mysqlCommonFuncMysqlNet();
                });

                $('#mysql_redundant_indexes').click(function(){
                    mysqlCommonFuncRedundantIndexes();
                });

                $('#mysql_table_info').click(function(){
                    mysqlCommonFuncTableInfo();
                });

                $('#mysql_conn_count').click(function(){
                    mysqlCommonFuncConnCount();
                });

                $('#mysql_fpk_info').click(function(){
                    mysqlCommonFuncFpkInfo();
                });

                $('#mysql_lock_sql').click(function(){
                    mysqlCommonFuncLockSQL();
                });

                $('#mysql_deadlock_info').click(function(){
                    mysqlCommonFuncDeadlockInfo();
                });

                $('#mysql_slave_status').click(function(){
                    mysqlCommonFuncSlaveStatus();
                });

                $('#mysql_slave_sync_progress').click(function(){
                    mysqlSlaveSyncProgress();
                });
            }
        });
    });
}

function mysqlRunMysqlTab(name){
    switch(name){
        case 'proccess':mysqlProcessList();break;
        case 'status':mysqlStatusList();break;
        case 'stats':mysqlStatsList();break;
    }
}

// ------------------------- mysql start -------------------------------
function mysqlGetSid(){
    return $('#mysql select[name=sid]').val();
    // return 0;
}

function mysqlGetDbName(){
    return $('#mysql .mysql_db_list select[name=mysql_db]').val();
}

function mysqlGetTableName(){
    var table = $('#mysql .mysql_table_list select[name=mysql_table]').val();
    if (!table){
        return '';
    }
    return table;
}

function mysqlInitField(f, data){
    var option_html = '<option value="0">无字段</option>';
    for (var i = 0; i < f.length; i++) {
        if (data['soso_field'] == f[i]){
            option_html+= '<option value="'+f[i]+'" selected>'+f[i]+'</option>';
        } else {
            option_html+= '<option value="'+f[i]+'">'+f[i]+'</option>';
        }

        
    }

    $('select[name="mysql_field_key"]').html(option_html);

    $('#mysql_find').unbind('click').click(function(){
        var val = $('input[name="mysql_field_value"]').val();
        if (val == ''){
            layer.msg('搜索不能为空!',{icon:7});
            return;
        }
        mysqlGetDataList(1);
    });
}


function mysqlGetServerList(call_func){
    closeInstallLayer();
    myPostCBN('get_server_list', {}, function(rdata){
        var rdata = rdata.data;
        if (rdata.data.length != 0){
            var items = rdata.data;
            var content = '';
            for (var i = 0; i < items.length; i++) {
                var t = items[i];
                if (i == 0){
                    content += '<option value="'+t['val']+'" selected>'+t['name']+'</option>';
                } else {
                    content += '<option value="'+t['val']+'">'+t['name']+'</option>';
                }
            }


            $('#mysql select[name=sid]').html(content);
            $('#mysql select[name=sid]').change(function(){
                mysqlGetDbList();
            });
            if (typeof(call_func) == 'function'){
                call_func();
            }
            closeInstallLayer();
        } else {
            layer.msg(rdata.data.msg,{ icon: 7, time: 2000, shade: 0.3 });
            setTimeout(function(){
                showInstallLayer();
            },2050);
        }
    });
}

function mysqlGetDbList(){
    var sid = mysqlGetSid();
    myPostCBN('get_db_list',{'sid':sid} ,function(rdata){
        if (rdata.data.status){
            var items = rdata.data.data['list'];
            var content = '';
            for (var i = 0; i < items.length; i++) {
                var name = items[i];
                if (i == 0){
                    content += '<option value="'+name+'" selected>database['+name+']</option>';
                } else {
                    content += '<option value="'+name+'">database['+name+']</option>';
                }
            }
            // console.log(content);
            $('#mysql .mysql_db_list select[name=mysql_db]').html(content);
            $('#mysql .mysql_db_list select[name=mysql_db]').change(function(){
                mysqlGetTableList(1);
            });

            mysqlGetTableList(1);
        }
    });
}

function mysqlGetTableList(p){
    // console.log('mysqlGetTableList',p);
    var sid = mysqlGetSid();
    var db = mysqlGetDbName();

    if (!db){
        return;
    }

    myPostCBN('get_table_list',{'sid':sid,'db':db} ,function(rdata){
        if (rdata.data.status){

            var items = rdata.data.data['list'];
            var content = '';
            for (var i = 0; i < items.length; i++) {
                var name = items[i];
                if (i == 0){
                    content += '<option value="'+name+'" selected>table['+name+']</option>';
                } else {
                    content += '<option value="'+name+'">table['+name+']</option>';
                }
            }
            // console.log(content);
            $('#mysql .mysql_table_list select[name=mysql_table]').html(content);
            $('#mysql .mysql_table_list select[name=mysql_table]').change(function(){
                mysqlGetDataList(1);
            });

            mysqlGetDataList(1);
        }
    });
}

function mysqlGetDataList(p){
    var sid = mysqlGetSid();
    var db = mysqlGetDbName();
    var table = mysqlGetTableName();

    var mysql_field = $('select[name="mysql_field_key"]').val();
    var mysql_value = $('input[name="mysql_field_value"]').val();

    var request_data = {
        'sid':sid,
        'db':db,
        'table':table,
        'p':p
    };

    if (mysql_field != '0'){
        request_data['where'] = {
            field : mysql_field,
            value : mysql_value
        };
    } else {
        request_data['where'] = {};
    }

    myPostCB('get_data_list',request_data ,function(rdata){

        if (rdata.data.status){
            var data = rdata.data.data;
            var dlist = data['list'];

            var fields = mongodbGetDataFields(dlist);
            if (fields.length != 0 ){
                mysqlInitField(fields,data);
            }
        
            var header_field = '';
            for (var i =0 ; i<fields.length ; i++) {
                header_field += '<th>'+fields[i]+'</th>';
            }
            $('#mysql_table thead tr').html(header_field);

            var tbody = '';
            for (var i = 0; i < dlist.length; i++) {
                tbody += '<tr>';
                for (var j = 0; j < fields.length; j++) {
                    var f = fields[j];
                    if (f in dlist[i]) {
                        tbody += '<td title="'+dlist[i][f]+'">'+dlist[i][f]+'</td>';
                    } else {
                        tbody += '<td>undefined</td>';
                    }
                }
                tbody += '</tr>';
            }

            $('#mysql_table tbody').html(tbody);
            $('#mysql .mysql_list_page').html(data.page);
        }
        // 
    });
}


function mysqlProcessList(){
    var sid = mysqlGetSid();
    var request_data = {};
    request_data['sid'] = sid;
    myPostCBN('get_proccess_list',request_data ,function(rdata){
        if (rdata.data.status){
            var data = rdata.data.data;
            var dlist = data['list'];

            var fields = mongodbGetDataFields(dlist);
        
            var header_field = '';
            for (var i =0 ; i<fields.length ; i++) {
                header_field += '<th>'+fields[i]+'</th>';
            }
            $('#mysql_ot_table thead tr').html(header_field);

            var tbody = '';
            for (var i = 0; i < dlist.length; i++) {
                tbody += '<tr>';
                for (var j = 0; j < fields.length; j++) {
                    var f = fields[j];
                    if (f in dlist[i]) {
                        tbody += '<td title="'+dlist[i][f]+'">'+dlist[i][f]+'</td>';
                    } else {
                        tbody += '<td>undefined</td>';
                    }
                }
                tbody += '</tr>';
            }

            $('#mysql_ot_table tbody').html(tbody);
        }
    });
}

function mysqlStatusList(){
    var sid = mysqlGetSid();
    var request_data = {};
    request_data['sid'] = sid;
    myPostCBN('get_status_list',request_data ,function(rdata){
        // console.log(rdata);
        if (rdata.data.status){
            var data = rdata.data.data;
            var dlist = data['list'];

            var fields = mongodbGetDataFields(dlist);
        
            var header_field = '';
            for (var i =0 ; i<fields.length ; i++) {
                header_field += '<th>'+fields[i]+'</th>';
            }
            $('#mysql_ot_table thead tr').html(header_field);

            var tbody = '';
            for (var i = 0; i < dlist.length; i++) {
                tbody += '<tr>';
                for (var j = 0; j < fields.length; j++) {
                    var f = fields[j];
                    if (f in dlist[i]) {
                        tbody += '<td title="'+dlist[i][f]+'">'+dlist[i][f]+'</td>';
                    } else {
                        tbody += '<td>undefined</td>';
                    }
                }
                tbody += '</tr>';
            }

            $('#mysql_ot_table tbody').html(tbody);
        }
    });
}

function mysqlStatsList(){
    var sid = mysqlGetSid();
    var request_data = {};
    request_data['sid'] = sid;
    myPostCBN('get_stats_list',request_data ,function(rdata){
        // console.log(rdata);
        if (rdata.data.status){
            var data = rdata.data.data;
            var dlist = data['list'];

            var fields = mongodbGetDataFields(dlist);
        
            var header_field = '';
            for (var i =0 ; i<fields.length ; i++) {
                header_field += '<th>'+fields[i]+'</th>';
            }
            $('#mysql_ot_table thead tr').html(header_field);

            var tbody = '';
            for (var i = 0; i < dlist.length; i++) {
                tbody += '<tr>';
                for (var j = 0; j < fields.length; j++) {
                    var f = fields[j];
                    if (f in dlist[i]) {
                        tbody += '<td title="'+dlist[i][f]+'">'+dlist[i][f]+'</td>';
                    } else {
                        tbody += '<td>undefined</td>';
                    }
                }
                tbody += '</tr>';
            }

            $('#mysql_ot_table tbody').html(tbody);
        }
    });
}


// ------------------------- mysql start -------------------------------

// ------------------------- memcached start -------------------------------
function memcachedGetSid(){
    return 0;
}

function memcachedGetItem(){
    return $('#memcached .item_list select').val();
}

function memcachedGetList(){
    var sid = memcachedGetSid();
    closeInstallLayer();
    memPostCB('get_items',{'sid':sid} ,function(rdata){
        if (rdata.data.status){
            var items = rdata.data.data['items'];
            var content = '';
            for (var i = 0; i < items.length; i++) {
                var name = items[i];
                if (i == 0){
                    content += '<option value="'+name+'" selected>items['+name+']</option>';
                } else {
                    content += '<option value="'+name+'">items['+name+']</option>';
                }
            }
            $('#memcached .item_list select').html(content);
            $('#memcached .item_list select').change(function(){
                memcachedGetKeyList(1);
            });
            closeInstallLayer();
            memcachedGetKeyList(1);
        } else {
            layer.msg(rdata.data.msg,{ icon: 7, time: 2000, shade: 0.3 });
            setTimeout(function(){
                showInstallLayer();
            },2050);
        }
        
    });
}

function memcachedGetKeyList(p){
    var item_id = memcachedGetItem();
    var sid = memcachedGetSid();
    memPostCB('get_key_list',{'sid':sid,'item_id':item_id,'p':p} ,function(rdata){
        if (rdata.data.status){
            var data = rdata.data.data;
            var dlist = data['list'];

            var tbody = '';
            for (var i = 0; i < dlist.length; i++) {
                tbody += '<tr>';

                tbody += "<td><input type='checkbox' class='check' name='id' onclick='checkSelect();'></td>";

                tbody += '<td>'+ dlist[i]['k'] +'</td>';
                tbody += '<td><span style="width:100px;" class="size_ellipsis">'+dlist[i]['v']+'</span><span data-index="'+i+'" class="ico-copy cursor copy ml5" title="复制值"></span></td>';
                tbody += '<td>'+ dlist[i]['s'] +'</td>';

                if (dlist[i]['t'] == '0'){
                    tbody += '<td>永久</td>';
                } else {
                    tbody += '<td>'+ dlist[i]['t'] +'</td>';
                }

                tbody += '<td style="text-align:right;">\
                        <a href="javascript:;" data-index="'+i+'" class="btlink del" title="删除">删除</a>\
                        </td>';

                tbody += '</tr>';
            }

            $('.memcached_table_content tbody').html(tbody);
            $('.memcached_list_page').html(data.page);


            $('.del').click(function(){
                var i = $(this).data('index');
                memcachedDeleteKey(dlist[i]['k']);
            });

            $('.copy').click(function(){
                var i = $(this).data('index');
                copyText(dlist[i]['v']);
            });
        } else {
            $('.memcached_table_content tbody').html('');
        }
    });
}

function memcachedDeleteKey(key){
    layer.confirm('确定要删除?', {btn: ['确定', '取消']}, function(){
        var data = {};
        data['sid'] = memcachedGetSid();
        data['key'] = key;
        memPostCB('del_val', data, function(rdata){
            showMsg(rdata.data.msg,function(){
                if (rdata.data.status){
                    memcachedGetKeyList(1);
                }
            },{icon: rdata.data.status ? 1 : 2}, 2000);
        });
    });
}


function memcachedAdd(){
    layer.open({
        type: 1,
        area: '480px',
        title: '添加Key至服务器',
        closeBtn: 1,
        shift: 0,
        shadeClose: false,
        btn:['确定','取消'],
        content: "<form class='bt-form pd20'>\
            <div class='line'>\
                <span class='tname'>键</span>\
                <div class='info-r c4'>\
                    <input class='bt-input-text' type='text' name='key' placeholder='键' style='width:260px;'/>\
                </div>\
            </div>\
            <div class='line'>\
                <span class='tname'>值</span>\
                <div class='info-r c4'>\
                    <textarea class='bt-input-text' name='val' style='width:260px;height:100px;'/></textarea>\
                </div>\
            </div>\
            <div class='line'>\
                <span class='tname'>有效期</span>\
                <div class='info-r c4'>\
                    <input class='bt-input-text mr5' type='number' name='endtime' value='60' style='width:260px;'/>\
                </div>\
            </div>\
            <div class='line'>\
                <div>\
                    <ul class='help-info-text c7' style='margin-left:30px;'><li>有效期为0表示永久</li>\
                </div>\
            </div>\
        </form>",
        success:function(){
        },
        yes: function(index){
            var data = {};
            data['sid'] = memcachedGetSid();
            data['key'] = $('input[name="key"]').val();
            data['val'] = $('textarea[name="val"]').val();
            data['endtime'] = $('input[name="endtime"]').val();

            memPostCB('set_kv', data ,function(rdata){
                showMsg(rdata.data.msg,function(){
                    layer.close(index);
                    memcachedGetList();
                },{icon: rdata.data.status ? 1 : 2}, 1000); 
            });
        }
    });
}

// ------------------------- memcached end ---------------------------------

// ------------------------- mongodb start ---------------------------------
function mongodbGetSid(){
    return 0;
}

function mongodbGetDbName(){
    return $('.db_list select[name="db"]').val();
}

function mongodbInitField(f, data){
    var option_html = '<option value="0">无字段</option>';
    for (var i = 0; i < f.length; i++) {
        if (data['soso_field'] == f[i]){
            option_html+= '<option value="'+f[i]+'" selected>'+f[i]+'</option>';
        } else {
            option_html+= '<option value="'+f[i]+'">'+f[i]+'</option>';
        }

        
    }

    $('select[name="mongodb_field_key"]').html(option_html);

    $('#mongodb .mongodb_find').unbind('click').click(function(){
        var val = $('input[name="mongodb_field_value"]').val();
        if (val == ''){
            layer.msg('搜索不能为空!',{icon:7});
            return;
        }
        mongodbDataList(1);
    });

    $('#mongodb .mongodb_refresh').unbind('click').click(function(){
        mongodbDataList(1);
    });
}

var mogodb_db_list;
function mongodbCollectionName(){
    var v = mogodb_db_list.getValue('value');
    if (v.length == 0){
        // console.log($('#mongodb').data('collection'));
        return $('#mongodb').data('collection');
    }
    return v[0];
}

function mongodbGetList(){
    var sid = mongodbGetSid();
    closeInstallLayer();
    mgdbPostCB('get_db_list',{'sid':sid} ,function(rdata){
        // console.log(rdata);
        if (rdata.data.status){
            var list = rdata.data.data['list'];
            var content = '';
            for (var i = 0; i < list.length; i++) {
                var name = list[i];
                if (i == 0){
                    content += '<option value="'+name+'" selected>'+name+'</option>';
                } else {
                    content += '<option value="'+name+'">'+name+'</option>';
                }
            }
            $('.db_list select').html(content);

            if (list.length > 0) {
                mongodbGetCollections(list[0]);
            }

            $('#mongodb_select .db_list select[name="db"]').change(function(){
                var collection_name = $(this).val();
                mongodbGetCollections(collection_name);
            });

            closeInstallLayer();
        } else {
            layer.msg(rdata.data.msg,{ icon: 7, time: 2000, shade: 0.3 });
            setTimeout(function(){
                showInstallLayer();
            },2050);
            
        }
    });
}


function mongodbGetCollections(name){
    var sid = mongodbGetSid();
    
    mgdbPostCB('get_collections_list',{'sid':sid,'name':name} ,function(rdata){
        // console.log(rdata);
        if (rdata.data.status){
            var list = rdata.data.data['collections'];

            var select_list = [];
            for (var i = 0; i < list.length; i++) {
                var t = {};
                t['name'] = list[i];
                t['value'] = list[i];

                if (i == 0){
                    t['selected'] = true;
                }

                select_list.push(t);
            }

            mogodb_db_list = xmSelect.render({
                el: '#mongodb_search', 
                radio: true,
                toolbar: {show: true},
                data: select_list,
                on: function(data){
                    //arr:  当前多选已选中的数据
                    var arr = data.arr;
                    //change, 此次选择变化的数据,数组
                    var change = data.change;
                    //isAdd, 此次操作是新增还是删除
                    var isAdd = data.isAdd;
                    if (isAdd){
                        $('#mongodb').data('collection',change[0].value);

                        setTimeout(function(){
                            mongodbDataList(1);
                        },200);
                    }
                },
            });

            if (select_list.length > 0){

                setTimeout(function(){
                    mongodbDataList(1);
                },200);
            } 
        }
    });
}

function mongodbGetDataFields(data){
    var fields = [];
    for (var i = 0; i < data.length; i++) {    
        var d = data[i];
        for (var j in d) {
            if (fields.indexOf(j) == -1 ){
                fields.push(j);              
            }
        }
    }
    return fields;
}

function mongodbDataList(p){
    var sid = mongodbGetSid();
    var db = mongodbGetDbName();
    var collection = mongodbCollectionName();

    var mongodb_field = $('select[name="mongodb_field_key"]').val();
    var mongodb_value = $('input[name="mongodb_field_value"]').val();

    var request_data = {
        'sid':sid,
        'db':db,
        'collection':collection,
        "p":p,
    };

    if (mongodb_field != '0'){
        request_data['where'] = {
            field : mongodb_field,
            value : mongodb_value
        };
    } else {
        request_data['where'] = {};
    }

    // console.log({'sid':sid,'db':db,'collection':collection,"p":p});
    mgdbPostCB('get_data_list', request_data, function(rdata){
        if (rdata.data.status){
            var data = rdata.data.data;
            var dlist = data['list'];
            // console.log(dlist);

            var fields = mongodbGetDataFields(dlist);
            if (fields.length != 0 ){
                mongodbInitField(fields,data);
            }
            
            // console.log(fields);

            var header_field = '';
            for (var i =0 ; i<fields.length ; i++) {
                header_field += '<th>'+fields[i]+'</th>';
            }
            header_field += '<th class="text-right">操作</th>';

            $('#mongodb .mongodb_table thead tr').html(header_field);

            var tbody = '';
            for (var i = 0; i < dlist.length; i++) {
                tbody += '<tr>';
                for (var j = 0; j < fields.length; j++) {
                    var f = fields[j];

                    if (f in dlist[i]) {
                        if (f == '_id' ){
                            tbody += '<td>'+dlist[i]['_id']['$oid']+'</td>';
                        } else {
                            tbody += '<td>'+dlist[i][f]+'</td>';
                        }
                    } else {
                        tbody += '<td>undefined</td>';
                    }
                }

                tbody += '<td style="text-align:right;">\
                        <a href="javascript:;" data-index="'+i+'" class="btlink del" title="删除">删除</a>\
                        </td>';

                tbody += '</tr>';
            }

            // console.log($(window).width()-230);
            $('#mongodb_table').css('width', $(document).width()+240).parent().css('width', $(document).width()-240).css('overflow','scroll');
            $('#mongodb').css('width',$(document).width()-240).css('overflow','hidden');
            $('#mongodb .mongodb_table tbody').html(tbody);
            $('#mongodb .mongodb_list_page').html(data.page);

            $('#mongodb .del').click(function(){
                var i = $(this).data('index');
                mongodbDel(dlist[i]['_id']['$oid']);
            });
        }
    });
}

function mongodbDel(mgdb_id){
    // console.log(mgdb_id);
    var sid = mongodbGetSid();
    var db = mongodbGetDbName();
    var collection = mongodbCollectionName();
    mgdbPostCB('del_by_id',{'sid':sid,'db':db,'collection':collection,"_id":mgdb_id} ,function(rdata){
        showMsg(rdata.data.msg,function(){
            if (rdata.data.status){
                mongodbDataList(1);
            }
        },{icon: rdata.data.status ? 1 : 2}, 2000);
    });
}

// ------------------------- mongodb end ---------------------------------

// ------------------------- redis start ---------------------------------
function redisGetSid(){
    return 0;
}

function redisGetIdx(){
    return $('#redis_list_tab .tab-nav span.on').data('id');
}

function redisGetList(){
    var sid = redisGetSid();
    closeInstallLayer();
    redisPostCB('get_list',{'sid':sid} ,function(rdata){
        if (rdata.data.status){
            var list = rdata.data.data;
            var content = '';
            for (var i = 0; i < list.length; i++) {
                if (i == 0){
                    content += '<span data-id="'+i+'" class="on">'+list[i]['name'] + '('+ list[i]['keynum'] +')</span>'; 
                } else {
                    content += '<span data-id="'+i+'">'+list[i]['name'] + '('+ list[i]['keynum'] +')</span>'; 
                }
            }
            $('#redis_list_tab .tab-nav').html(content);

            $('#redis_list_tab .tab-nav span').click(function(){
                $('#redis_list_tab .tab-nav span').removeClass('on');
                $(this).addClass('on');
                redisGetKeyList(1);
            });
            redisGetKeyList(1);
            closeInstallLayer();
        } else {
            layer.msg(rdata.data.msg,{ icon: 7, time: 1000, shade: 0.3 });
            setTimeout(function(){
                showInstallLayer();
            },1050);
        }
    });
}

function redisGetKeyList(page,search = ''){

    var args = {};
    args['sid'] = redisGetSid();
    args['idx'] = redisGetIdx();
    args['p'] = page;
    args['search'] = search;

    var input_search_val = $('#redis_ksearch').val();
    if (input_search_val!=''){
        args['search'] = input_search_val;
    }

    redisPostCB('get_dbkey_list', args, function(rdata){
        if (rdata.data.status){
            var data = rdata.data.data.data;
            var tbody = '';
            for (var i = 0; i < data.length; i++) {


                tbody += '<tr>';
                tbody += "<td><input type='checkbox' class='check' name='id' title='"+data[i].name+"' onclick='checkSelect();' value='"+data[i].name+"'></td>";
                tbody += '<td style="width:100px;">'+data[i].name+'</td>';
                tbody += '<td><span style="width:100px;" class="size_ellipsis">'+data[i].val+'</span><span data-index="'+i+'" class="ico-copy cursor copy ml5" title="复制值"></span></td>';
                tbody += '<td>'+data[i].type+'</td>';
                tbody += '<td>'+data[i].len+'</td>';

                if (data[i].endtime == -1){
                    tbody += '<td>永久</td>';
                } else {
                    tbody += '<td>'+data[i].endtime+'</td>';
                }

                tbody += '<td style="width:200px;text-align:right; color:#bbb">\
                        <a href="javascript:;" data-index="'+i+'" class="btlink edit" title="编辑">编辑</a> | \
                        <a href="javascript:;" class="btlink" onclick="redisDeleteKey(\''+data[i].name+'\')">删除</a>\
                        </td>';

                tbody += '</tr>';
            }

            // console.log(tbody);
            $('.redis_table_content tbody').html(tbody);
            $('.redis_list_page').html(rdata.data.data.page);


            $('.edit').click(function(){
                var i = $(this).data('index');
                redisEditKv(data[i].name,data[i].val,data[i].endtime);
            });

            $('.copy').click(function(){
                var i = $(this).data('index');
                copyText(data[i].val);
            });

        }
    });
}

function redisDeleteKey(name){
    layer.confirm('确定要删除?', {btn: ['确定', '取消']}, function(){
        var data = {};
        data['idx'] = redisGetIdx();
        data['sid'] = redisGetSid();
        data['name'] = name;
        redisPostCB('del_val', data, function(rdata){
            showMsg(rdata.data.msg,function(){
                if (rdata.data.status){
                    redisGetList();
                }
            },{icon: rdata.data.status ? 1 : 2}, 2000);
        });
    });
}

function redisAdd(){
    layer.open({
        type: 1,
        area: '480px',
        title: '添加Key至服务器',
        closeBtn: 1,
        shift: 0,
        shadeClose: false,
        btn:['确定','取消'],
        content: "<form class='bt-form pd20'>\
            <div class='line'>\
                <span class='tname'>数据库</span>\
                <div class='info-r c4'>\
                    <select name='idx' class='bt-input-text' style='width:260px;'>\
                        <option value='0'>DB(0)</option>\
                    </select>\
                </div>\
            </div>\
            <div class='line'>\
                <span class='tname'>键</span>\
                <div class='info-r c4'>\
                    <input class='bt-input-text' type='text' name='key' placeholder='键' style='width:260px;'/>\
                </div>\
            </div>\
            <div class='line'>\
                <span class='tname'>值</span>\
                <div class='info-r c4'>\
                    <textarea class='bt-input-text' name='val' style='width:260px;height:100px;'/></textarea>\
                </div>\
            </div>\
            <div class='line'>\
                <span class='tname'>有效期</span>\
                <div class='info-r c4'>\
                    <input class='bt-input-text mr5' type='number' name='endtime' value='60' style='width:260px;'/>\
                </div>\
            </div>\
            <div class='line'>\
                <div>\
                    <ul class='help-info-text c7' style='margin-left:30px;'><li>有效期为0表示永久</li>\
                </div>\
            </div>\
        </form>",
        success:function(){
            var db_list = $('#redis_list_tab .tab-nav span');
            var db_list_count = db_list.length;

            var idx_html = '';
            for (var i = 0; i < db_list_count; i++) {
                idx_html += "<option value='"+i+"'>DB("+i+")</option>";
            }
            $('select[name=idx]').html(idx_html);
        },
        yes: function(index){
            var data = {};
            data['idx'] = $('select[name=idx]').val();
            data['sid'] = redisGetSid();
            data['name'] = $('input[name="key"]').val();
            data['val'] = $('textarea[name="val"]').val();
            data['endtime'] = $('input[name="endtime"]').val();

            redisPostCB('set_kv', data ,function(rdata){
                showMsg(rdata.data.msg,function(){
                    layer.close(index);
                    redisGetList();
                },{icon: rdata.data.status ? 1 : 2}, 1000); 
            });
        }
    });
}

function redisEditKv(name, val, endtime){
    layer.open({
        type: 1,
        area: '480px',
        title: '编辑['+name+']Key',
        closeBtn: 1,
        shift: 0,
        shadeClose: false,
        btn:['确定','取消'],
        content: "<form class='bt-form pd20'>\
            <div class='line'>\
                <span class='tname'>数据库</span>\
                <div class='info-r c4'>\
                    <select name='idx' class='bt-input-text' style='width:260px;'>\
                        <option value='0'>DB(0)</option>\
                    </select>\
                </div>\
            </div>\
            <div class='line'>\
                <span class='tname'>键</span>\
                <div class='info-r c4'>\
                    <input class='bt-input-text' type='text' name='key' placeholder='键' style='width:260px;'/>\
                </div>\
            </div>\
            <div class='line'>\
                <span class='tname'>值</span>\
                <div class='info-r c4'>\
                    <textarea class='bt-input-text' name='val' style='width:260px;height:100px;'/></textarea>\
                </div>\
            </div>\
            <div class='line'>\
                <span class='tname'>有效期</span>\
                <div class='info-r c4'>\
                    <input class='bt-input-text mr5' type='number' name='endtime' value='60' style='width:260px;'/>\
                </div>\
            </div>\
            <div class='line'>\
                <div>\
                    <ul class='help-info-text c7' style='margin-left:30px;'><li>有效期为0表示永久</li>\
                </div>\
            </div>\
        </form>",
        success:function(){
            var idx = redisGetIdx();
            var idx_html = "<option value='"+idx+"'>DB("+idx+")</option>";
            $('select[name=idx]').html(idx_html).attr('readonly','readonly');
            $('input[name="key"]').val(name).attr('readonly','readonly');
            $('textarea[name="val"]').val(val);

            if (endtime == -1){
                $('input[name="endtime"]').val(0);
            } else {
                $('input[name="endtime"]').val(endtime);
            }            
        },
        yes: function(index){
            var data = {};
            data['idx'] = $('select[name=idx]').val();
            data['sid'] = redisGetSid();
            data['name'] = $('input[name="key"]').val();
            data['val'] = $('textarea[name="val"]').val();
            data['endtime'] = $('input[name="endtime"]').val();
            redisPostCB('set_kv', data ,function(rdata){
                showMsg(rdata.data.msg,function(){
                    if (rdata.data.status){
                        layer.close(index);
                        redisGetList();
                    }
                },{icon: rdata.data.status ? 1 : 2}, 1000);
            });
        }
    });
}

function redisBatchDel(){
    var keys = [];
    $('input[type="checkbox"].check:checked').each(function () {
        keys.push($(this).val());
    });
    if (keys.length == 0){
        layer.msg('没有选中数据!',{icon:7});
        return;
    } 

    layer.confirm('确定要批量删除?', {btn: ['确定', '取消']}, function(){
        var data = {};
        data['idx'] = redisGetIdx();
        data['sid'] = redisGetSid();
        data['keys'] = keys;
        redisPostCB('batch_del_val', data, function(rdata){
            showMsg(rdata.data.msg,function(){
                if (rdata.data.status){
                   redisGetList(); 
                }
            },{icon: rdata.data.status ? 1 : 2}, 2000);
        });
    });
}

function redisBatchClear(){
    var xm_db_list;
    layer.open({
        type: 1,
        area: ['480px','180px'],
        title: '清空【本地服务器】数据库',
        closeBtn: 1,
        shift: 0,
        shadeClose: false,
        btn:['确定','取消'],
        content: "<form class='bt-form pd20'>\
            <div class='line'>\
                <span class='tname'>选择数据库</span>\
                <div class='info-r'>\
                    <div id='select_db'></div>\
                </div>\
            </div>\
        </form>",
        success:function(l,i){
            var db_list = $('#redis_list_tab .tab-nav span');
            var db_list_count = db_list.length;

            var idx_db = [];
            for (var i = 0; i < db_list_count; i++) {
                var t = {};
                t['name'] = "DB("+i+")";
                t['value'] = i;
                idx_db.push(t);
            }

            xm_db_list = xmSelect.render({
                el: '#select_db', 
                repeat: false,
                toolbar: {show: true},
                data: idx_db,
            });

            $(l).find('.layui-layer-content').css('overflow','visible');
        },
        yes: function(index){
            var xm_db_val = xm_db_list.getValue('value');
            layer.confirm('确定要批量清空?', {btn: ['确定', '取消']}, function(){
                var data = {};
                data['sid'] = redisGetSid();
                data['idxs'] = xm_db_val;
                redisPostCB('clear_flushdb', data, function(rdata){
                    showMsg(rdata.data.msg,function(){
                        if (rdata.data.status){
                           redisGetList();
                           layer.close(index);
                        }
                    },{icon: rdata.data.status ? 1 : 2}, 2000);
                });
            });
        }
    });
}
// ------------------------- redis end ---------------------------------

// ------------------------- postgresql start -------------------------------
var pg_timer = null;
var pg_last_error = '';

function pgToastError(msg){
    // 轮询失败时避免每 2 秒重复弹出相同的提示
    if (!msg || pg_last_error == msg){
        return;
    }
    pg_last_error = msg;
    layer.msg(msg,{icon:7,time:2500});
}

function pgHtml(v){
    if (v === null || v === undefined){
        return '';
    }
    return String(v).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function pgGetSid(){
    return $('#postgresql select[name=sid]').val();
}

function pgGetDbName(){
    return $('#postgresql .postgresql_db_list select[name=postgresql_db]').val();
}

function pgGetTableName(){
    var table = $('#postgresql .postgresql_table_list select[name=postgresql_table]').val();
    if (!table || table == '0'){
        return '';
    }
    return table;
}

function pgShowNotice(title, msg){
    layer.open({
        type: 1,
        title: title,
        area: ['560px', '260px'],
        closeBtn: 1,
        shadeClose: false,
        content: '<div class="bt-form pd20"><pre style="white-space:pre-wrap;word-break:break-all;margin:0;line-height:1.8;">'+pgHtml(msg)+'</pre></div>'
    });
}

function pgModalTable(title, list, width, height){
    if (!list || list.length == 0){
        layer.msg('暂无数据',{icon:7});
        return;
    }

    var fields = mongodbGetDataFields(list);
    var thead = '';
    for (var i = 0; i < fields.length; i++){
        thead += '<th>'+pgHtml(fields[i])+'</th>';
    }

    var tbody = '';
    for (var i = 0; i < list.length; i++){
        tbody += '<tr>';
        for (var j = 0; j < fields.length; j++){
            var f = fields[j];
            var val = (f in list[i]) ? list[i][f] : '';
            tbody += '<td title="'+pgHtml(val)+'">'+pgHtml(val)+'</td>';
        }
        tbody += '</tr>';
    }

    layer.open({
        type: 1,
        title: title,
        area: [width || '900px', height || '420px'],
        closeBtn: 1,
        shadeClose: false,
        content: '<div class="bt-form pd20 divtable taskdivtable" style="height:'+(parseInt(height || '420') - 80)+'px;overflow:auto;">\
            <table class="table table-hover">\
                <thead><tr>'+thead+'</tr></thead>\
                <tbody>'+tbody+'</tbody>\
            </table>\
        </div>'
    });
}

function pgInitField(f, data){
    var option_html = '<option value="0">无字段</option>';
    for (var i = 0; i < f.length; i++){
        if (data['soso_field'] == f[i]){
            option_html += '<option value="'+pgHtml(f[i])+'" selected>'+pgHtml(f[i])+'</option>';
        } else {
            option_html += '<option value="'+pgHtml(f[i])+'">'+pgHtml(f[i])+'</option>';
        }
    }
    $('#postgresql select[name="postgresql_field_key"]').html(option_html);
}

function initTabPostgresql(){
    clearInterval(pg_timer);
    pg_last_error = '';

    pgGetServerList(function(){
        pgGetDbList();
        pgProcessList();

        clearInterval(pg_timer);
        pg_timer = setInterval(function(){
            var name = $('#postgresql_list_tab .tab-nav span.on').data('name');
            pgRunPgTab(name);

            var fname = $('#cutTab .tabs-item.active').data('name');
            if (fname != 'postgresql'){
                clearInterval(pg_timer);
            }
        }, 2000);
    });

    $('#postgresql_list_tab .tab-nav span').unbind('click').click(function(){
        $('#postgresql_list_tab .tab-nav span').removeClass('on');
        $(this).addClass('on');
        var name = $(this).data('name');
        pgRunPgTab(name);
    });

    $('#postgresql_find').unbind('click').click(function(){
        var val = $('#postgresql input[name="postgresql_field_value"]').val();
        if (val == ''){
            layer.msg('搜索不能为空!',{icon:7});
            return;
        }
        pgGetDataList(1);
    });

    pgCommonFunc();
}

function pgRunPgTab(name){
    switch(name){
        case 'proccess':pgProcessList();break;
        case 'status':pgStatusList();break;
        case 'stats':pgStatsList();break;
    }
}

function pgGetServerList(call_func){
    closeInstallLayer();
    pgPostCBN('get_server_list', {}, function(rdata){
        var data = rdata.data;
        if (data.data && data.data.length != 0){
            var items = data.data;
            var content = '';
            for (var i = 0; i < items.length; i++){
                var t = items[i];
                if (i == 0){
                    content += '<option value="'+t['val']+'" selected>'+t['name']+'</option>';
                } else {
                    content += '<option value="'+t['val']+'">'+t['name']+'</option>';
                }
            }

            $('#postgresql select[name=sid]').html(content);
            $('#postgresql select[name=sid]').change(function(){
                pgGetDbList();
            });

            if (typeof(call_func) == 'function'){
                call_func();
            }
            closeInstallLayer();
        } else {
            layer.msg('当前未安装 PostgreSQL',{icon:7,time:2000,shade:0.3});
            setTimeout(function(){
                showInstallLayer();
            },2050);
        }
    });
}

function pgGetDbList(){
    var sid = pgGetSid();
    pgPostCBN('get_db_list',{'sid':sid}, function(rdata){
        var data = rdata.data;
        if (!data.status){
            layer.msg(data.msg,{icon:7,time:2500});
            return;
        }

        var items = data.data['list'];
        if (items.length == 0){
            $('#postgresql .postgresql_db_list select[name=postgresql_db]').html('<option value="0">数据库空</option>');
            $('#postgresql .postgresql_table_list select[name=postgresql_table]').html('<option value="0">数据表空</option>');
            $('#postgresql_table thead tr').html('');
            $('#postgresql_table tbody').html('');
            $('.postgresql_list_page').html('<div><span class="Pcurrent">0</span><span class="Pcount">共0条</span></div>');
            return;
        }

        var content = '';
        for (var i = 0; i < items.length; i++){
            var name = items[i];
            if (i == 0){
                content += '<option value="'+pgHtml(name)+'" selected>database['+pgHtml(name)+']</option>';
            } else {
                content += '<option value="'+pgHtml(name)+'">database['+pgHtml(name)+']</option>';
            }
        }

        $('#postgresql .postgresql_db_list select[name=postgresql_db]').html(content);
        $('#postgresql .postgresql_db_list select[name=postgresql_db]').change(function(){
            pgGetTableList(1);
        });

        pgGetTableList(1);
    });
}

function pgGetTableList(p){
    var sid = pgGetSid();
    var db = pgGetDbName();
    if (!db || db == '0'){
        return;
    }

    pgPostCBN('get_table_list',{'sid':sid,'db':db}, function(rdata){
        var data = rdata.data;
        if (!data.status){
            layer.msg(data.msg,{icon:7,time:2500});
            return;
        }

        var items = data.data['list'];
        if (items.length == 0){
            $('#postgresql .postgresql_table_list select[name=postgresql_table]').html('<option value="0">数据表空</option>');
            $('#postgresql_table thead tr').html('');
            $('#postgresql_table tbody').html('');
            $('.postgresql_list_page').html('<div><span class="Pcurrent">0</span><span class="Pcount">共0条</span></div>');
            return;
        }

        var content = '';
        for (var i = 0; i < items.length; i++){
            var name = items[i];
            if (i == 0){
                content += '<option value="'+pgHtml(name)+'" selected>table['+pgHtml(name)+']</option>';
            } else {
                content += '<option value="'+pgHtml(name)+'">table['+pgHtml(name)+']</option>';
            }
        }

        $('#postgresql .postgresql_table_list select[name=postgresql_table]').html(content);
        $('#postgresql .postgresql_table_list select[name=postgresql_table]').change(function(){
            pgGetDataList(1);
        });

        pgGetDataList(1);
    });
}

function pgGetDataList(p){
    var sid = pgGetSid();
    var db = pgGetDbName();
    var table = pgGetTableName();

    var pg_field = $('#postgresql select[name="postgresql_field_key"]').val();
    var pg_value = $('#postgresql input[name="postgresql_field_value"]').val();

    var request_data = {
        'sid': sid,
        'db': db,
        'table': table,
        'p': p,
        'size': 10
    };

    if (pg_field != '0' && pg_field){
        request_data['where'] = {field: pg_field, value: pg_value};
    } else {
        request_data['where'] = {};
    }

    pgPostCB('get_data_list', request_data, function(rdata){
        var data = rdata.data;
        if (!data.status){
            layer.msg(data.msg,{icon:7,time:2500});
            return;
        }

        var rdata2 = data.data;
        var dlist = rdata2['list'];
        var fields = mongodbGetDataFields(dlist);
        if (fields.length != 0){
            pgInitField(fields, rdata2);
        }

        var header_field = '';
        for (var i = 0; i < fields.length; i++){
            header_field += '<th>'+pgHtml(fields[i])+'</th>';
        }
        $('#postgresql_table thead tr').html(header_field);

        var tbody = '';
        for (var i = 0; i < dlist.length; i++){
            tbody += '<tr>';
            for (var j = 0; j < fields.length; j++){
                var f = fields[j];
                var val = (f in dlist[i]) ? dlist[i][f] : '';
                tbody += '<td title="'+pgHtml(val)+'">'+pgHtml(val)+'</td>';
            }
            tbody += '</tr>';
        }
        $('#postgresql_table tbody').html(tbody);
        $('#postgresql .postgresql_list_page').html(rdata2['page']);
    });
}

function pgRenderOtTable(dlist){
    var fields = mongodbGetDataFields(dlist);

    var header_field = '';
    for (var i = 0; i < fields.length; i++){
        header_field += '<th>'+pgHtml(fields[i])+'</th>';
    }
    $('#postgresql_ot_table thead tr').html(header_field);

    var tbody = '';
    for (var i = 0; i < dlist.length; i++){
        tbody += '<tr>';
        for (var j = 0; j < fields.length; j++){
            var f = fields[j];
            var val = (f in dlist[i]) ? dlist[i][f] : '';
            tbody += '<td title="'+pgHtml(val)+'">'+pgHtml(val)+'</td>';
        }
        tbody += '</tr>';
    }
    $('#postgresql_ot_table tbody').html(tbody);
}

function pgProcessList(){
    pgPostCBN('get_proccess_list',{'sid':pgGetSid()}, function(rdata){
        var data = rdata.data;
        if (!data.status){
            pgToastError(data.msg);
            return;
        }
        pg_last_error = '';
        pgRenderOtTable(data.data['list']);
    });
}

function pgStatusList(){
    pgPostCBN('get_status_list',{'sid':pgGetSid()}, function(rdata){
        var data = rdata.data;
        if (!data.status){
            pgToastError(data.msg);
            return;
        }
        pg_last_error = '';
        pgRenderOtTable(data.data['list']);
    });
}

function pgStatsList(){
    pgPostCBN('get_stats_list',{'sid':pgGetSid()}, function(rdata){
        var data = rdata.data;
        if (!data.status){
            pgToastError(data.msg);
            return;
        }
        pg_last_error = '';
        pgRenderOtTable(data.data['list']);
    });
}

function pgCommonFunc(){
    $('#postgresql_common').unbind('click').click(function(){
        layer.open({
            type: 1,
            title: "PostgreSQL常用功能",
            area: ['600px', '200px'],
            closeBtn: 1,
            shadeClose: false,
            content: '<div class="bt-form pd20">\
                <button style="margin-bottom: 8px;" id="pg_top_nsql" type="button" class="btn btn-default btn-sm">查询执行次数最频繁的前N条SQL语句</button>\
                <button style="margin-bottom: 8px;" id="pg_net_stat" type="button" class="btn btn-default btn-sm">PostgreSQL服务器的QPS/TPS指标</button>\
                <button style="margin-bottom: 8px;" id="pg_redundant_indexes" type="button" class="btn btn-default btn-sm">查看重复或冗余的索引</button>\
                <button style="margin-bottom: 8px;" id="pg_table_info" type="button" class="btn btn-default btn-sm">统计库里每个表的大小</button>\
                <button style="margin-bottom: 8px;" id="pg_conn_count" type="button" class="btn btn-default btn-sm">查看应用端IP连接数总和</button>\
                <button style="margin-bottom: 8px;" id="pg_fpk_info" type="button" class="btn btn-default btn-sm">快速找出没有主键的表</button>\
                <button style="margin-bottom: 8px;" id="pg_lock_sql" type="button" class="btn btn-default btn-sm">查看当前锁阻塞的SQL</button>\
                <button style="margin-bottom: 8px;" id="pg_deadlock_info" type="button" class="btn btn-default btn-sm">查看死锁信息</button>\
                <button style="margin-bottom: 8px;" id="pg_slave_status" type="button" class="btn btn-default btn-sm">查看主从复制信息</button>\
            </div>',
            success:function(i,l){
                $('#pg_top_nsql').click(function(){ pgCommonFuncTopN(); });
                $('#pg_net_stat').click(function(){ pgCommonFuncNet(); });
                $('#pg_redundant_indexes').click(function(){ pgCommonFuncRedundantIndexes(); });
                $('#pg_table_info').click(function(){ pgCommonFuncTableInfo(); });
                $('#pg_conn_count').click(function(){ pgCommonFuncConnCount(); });
                $('#pg_fpk_info').click(function(){ pgCommonFuncFpkInfo(); });
                $('#pg_lock_sql').click(function(){ pgCommonFuncLockSQL(); });
                $('#pg_deadlock_info').click(function(){ pgCommonFuncDeadlockInfo(); });
                $('#pg_slave_status').click(function(){ pgCommonFuncSlaveStatus(); });
            }
        });
    });
}

function pgCommonFuncTopN(){
    pgPostCBN('get_topn_list',{'sid':pgGetSid()}, function(rdata){
        var data = rdata.data;
        if (!data.status){
            pgShowNotice('查询执行次数最频繁的前N条SQL语句', data.msg);
            return;
        }
        pgModalTable('查询执行次数最频繁的前N条SQL语句', data.data, '1000px', '450px');
    });
}

function pgCommonFuncNet(){
    pgPostCBN('get_net_list',{'sid':pgGetSid()}, function(rdata){
        var data = rdata.data;
        if (!data.status){
            pgShowNotice('PostgreSQL服务器的QPS/TPS指标', data.msg);
            return;
        }
        pgModalTable('PostgreSQL服务器的QPS/TPS指标（网络带宽需在系统层监控）', data.data, '1000px', '360px');
    });
}

function pgCommonFuncRedundantIndexes(){
    function renderList(){
        pgPostCBN('get_redundant_indexes',{'sid':pgGetSid()}, function(rdata){
            var data = rdata.data;
            if (!data.status){
                layer.msg(data.msg,{icon:7,time:2500});
                return;
            }

            var items = data.data;
            if (items.length == 0){
                layer.msg('没有发现重复或冗余的索引',{icon:7});
                return;
            }

            var tbody = '';
            for (var i = 0; i < items.length; i++){
                tbody += '<tr>\
                    <td>'+pgHtml(items[i]['table_schema'])+'</td>\
                    <td>'+pgHtml(items[i]['table_name'])+'</td>\
                    <td>'+pgHtml(items[i]['redundant_index_name'])+'</td>\
                    <td>'+pgHtml(items[i]['redundant_index_columns'])+'</td>\
                    <td><a class="pg_drop_index btlink" index="'+i+'">删除</a></td>\
                </tr>';
            }

            layer.open({
                type: 1,
                title: "查看重复或冗余的索引",
                area: ['1000px', '420px'],
                closeBtn: 1,
                shadeClose: false,
                content: '<div class="bt-form pd20 divtable taskdivtable">\
                    <table class="table table-hover" id="pg_redundant_table">\
                        <thead><tr>\
                            <th>库名</th><th>表名</th><th>冗余索引</th><th>字段</th><th>操作</th>\
                        </tr></thead>\
                        <tbody>'+tbody+'</tbody>\
                    </table>\
                </div>',
                success: function(){
                    $('#pg_redundant_table .pg_drop_index').click(function(){
                        var index = $(this).attr('index');
                        layer.confirm('确定删除索引 '+pgHtml(items[index]['redundant_index_name'])+' ?', {btn:['确定','取消']}, function(li){
                            pgPostCB('redundant_indexes_cmd', {'sid':pgGetSid(),'index':index}, function(r2){
                                var d = r2.data;
                                showMsg(d.msg,function(){
                                    if (d.status){
                                        layer.close(li);
                                        renderList();
                                    }
                                },{icon: d.status ? 1 : 2}, 2000);
                            });
                        });
                    });
                }
            });
        });
    }
    renderList();
}

function pgCommonFuncTableInfo(){
    pgPostCBN('get_table_info',{'sid':pgGetSid()}, function(rdata){
        var data = rdata.data;
        if (!data.status){
            pgShowNotice('统计库里每个表的大小（单位 GB）', data.msg);
            return;
        }
        pgModalTable('统计库里每个表的大小（单位 GB）', data.data, '1200px', '460px');
    });
}

function pgCommonFuncConnCount(){
    pgPostCBN('get_conn_count',{'sid':pgGetSid()}, function(rdata){
        var data = rdata.data;
        if (!data.status){
            pgShowNotice('查看应用端IP连接数总和', data.msg);
            return;
        }
        pgModalTable('查看应用端IP连接数总和', data.data, '700px', '420px');
    });
}

function pgCommonFuncFpkInfo(){
    pgPostCBN('get_fpk_info',{'sid':pgGetSid()}, function(rdata){
        var data = rdata.data;
        if (!data.status){
            layer.msg(data.msg,{icon:7,time:2500});
            return;
        }
        pgModalTable('快速找出没有主键的表', data.data, '800px', '400px');
    });
}

function pgCommonFuncLockSQL(){
    function renderSQL(){
        pgPostCBN('get_lock_sql',{'sid':pgGetSid()}, function(rdata){
            var data = rdata.data;
            if (!data.status){
                layer.msg(data.msg,{icon:7,time:2500});
                return;
            }

            var items = data.data;
            var tbody = '';
            for (var i = 0; i < items.length; i++){
                var t = '<tr>';
                t += '<td>'+pgHtml(items[i]['trx_id'])+'</td>';
                t += '<td>'+pgHtml(items[i]['trx_state'])+'</td>';
                t += '<td>'+pgHtml(items[i]['trx_started'])+'</td>';
                t += '<td>'+pgHtml(items[i]['processlist_id'])+'</td>';
                t += '<td title="'+pgHtml(items[i]['info'])+'">'+pgHtml(items[i]['info'])+'</td>';
                t += '<td>'+pgHtml(items[i]['user'])+'</td>';
                t += '<td>'+pgHtml(items[i]['host'])+'</td>';
                t += '<td>'+pgHtml(items[i]['db'])+'</td>';
                t += '<td>'+pgHtml(items[i]['command'])+'</td>';
                t += '<td>'+pgHtml(items[i]['state'])+'</td>';
                t += '<td>'+pgHtml(items[i]['sql_kill_blocking_query'])+'</td>';
                t += '<td><a class="exec btlink" index="'+i+'">执行</a></td>';
                t += '</tr>';
                tbody += t;
            }
            $('#pg_lock_table tbody').html(tbody);

            $('#pg_lock_table tbody .exec').click(function(){
                var index = $(this).attr('index');
                var pid = items[index]['processlist_id'];
                pgPostCB('kill_lock_pid', {'sid':pgGetSid(),'pid':pid}, function(r2){
                    var d = r2.data;
                    showMsg(d.msg,function(){
                        if (d.status){
                            renderSQL();
                        }
                    },{icon: d.status ? 1 : 2}, 2000);
                });
            });
        });
    }

    layer.open({
        type: 1,
        title: "查看当前锁阻塞的SQL",
        area: ['1100px', '420px'],
        closeBtn: 1,
        shadeClose: false,
        content: '<div class="bt-form pd20 divtable taskdivtable">\
            <div class="mr20 pull-left" style="border-right: 1px solid #ccc; padding-right: 20px;">\
                <button id="pg_kill_all" type="button" class="btn btn-default btn-sm">关闭所有阻塞</button>\
            </div>\
            <hr />\
            <table class="table table-hover" id="pg_lock_table">\
                <thead><tr>\
                    <th>事务ID</th><th>事务状态</th><th>执行时间</th><th>线程ID</th>\
                    <th>Info</th><th>user</th><th>host</th><th>db</th>\
                    <th>command</th><th>state</th><th>kill</th><th>操作</th>\
                </tr></thead>\
                <tbody></tbody>\
            </table>\
        </div>',
        success:function(){
            renderSQL();
            $('#pg_kill_all').unbind('click').click(function(){
                pgPostCB('kill_all_lock', {'sid':pgGetSid()}, function(r2){
                    var d = r2.data;
                    showMsg(d.msg,function(){
                        if (d.status){
                            renderSQL();
                        }
                    },{icon: d.status ? 1 : 2}, 2000);
                });
            });
        }
    });
}

function pgCommonFuncDeadlockInfo(){
    function renderText(){
        pgPostCBN('get_deadlock_info',{'sid':pgGetSid()}, function(rdata){
            var data = rdata.data;
            if (!data.status){
                layer.msg(data.msg,{icon:7,time:2500});
                return;
            }
            $('#pg_info_log').val(data.data);
        });
    }

    layer.open({
        type: 1,
        title: "查看死锁信息",
        area: ['800px', '400px'],
        closeBtn: 1,
        shadeClose: false,
        content: '<div class="bt-form pd15">\
            <textarea readonly="" style="margin: 0px;height: 330px;width: 100%;background-color: #333;color:#fff; padding:0 5px" id="pg_info_log"></textarea>\
        </div>',
        success:function(){
            renderText();
        }
    });
}

function pgCommonFuncSlaveStatus(){
    function renderText(){
        pgPostCBN('get_slave_status',{'sid':pgGetSid()}, function(rdata){
            var data = rdata.data;
            if (!data.status){
                layer.msg(data.msg,{icon:7,time:2500});
                return;
            }
            $('#pg_info_log').val(data.data);
        });
    }

    layer.open({
        type: 1,
        title: "查看主从复制信息",
        area: ['800px', '400px'],
        closeBtn: 1,
        shadeClose: false,
        content: '<div class="bt-form pd15">\
            <textarea readonly="" style="margin: 0px;height: 330px;width: 100%;background-color: #333;color:#fff; padding:0 5px" id="pg_info_log"></textarea>\
        </div>',
        success:function(){
            renderText();
        }
    });
}
// ------------------------- postgresql end ---------------------------------

