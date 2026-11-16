function spPostMin(method, args, callback){

    var req_data = {};
    req_data['name'] = 'sphinx';
    req_data['func'] = method;
 
    if (typeof(args) != 'undefined' && args!=''){
        req_data['args'] = JSON.stringify(args);
    }

    $.post('/plugins/run', req_data, function(data) {
        if (!data.status){
            layer.msg(data.msg,{icon:0,time:2000,shade: [0.3, '#000']});
            return;
        }

        if(typeof(callback) == 'function'){
            callback(data);
        }
    },'json'); 
}

function myPost(method, args, callback, title){
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

    $.post('/plugins/run', {name:'mysql', func:method, args:_args}, function(data) {
        if (!data.status){
            layer.msg(data.msg,{icon:0,time:2000,shade: [0.3, '#000']});
            return;
        }

        if(typeof(callback) == 'function'){
            callback(data);
        }
    },'json'); 
}


function spPost(method, args, callback){
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });
    spPostMin(method,args,function(data){
        layer.close(loadT);
        if(typeof(callback) == 'function'){
            callback(data);
        } 
    });
}

function commonFunc(){
    var con = '<button class="btn btn-default btn-sm" onclick="confirmRebuildIndex();">重建索引</button>';
    con += '&nbsp;&nbsp; <button class="btn btn-default btn-sm" onclick="autoMakeConf();">自动创建配置</button>';
    $(".soft-man-con").html(con);
}

function autoMakeConf(){
    var xm_db_list;

    var con = '<ul class="help-info-text c7">';
    con += '<li style="color:red;">如果数据量比较大,第一次启动会失败!(可通过手动建立索引)</li>';
    con += '<li style="color:red;">以下内容,需手动加入计划任务。</li>';
    layer.open({
        type: 1,
        area: ['380px','350px'],
        title: '自动创建配置',
        closeBtn: 1,
        shift: 5,
        shadeClose: true,
        btn:["提交","关闭"],
        content: "<form class='bt-form pd20'>\
                    <div class='line'>\
                        <span class='tname'>选择数据库</span>\
                        <div class='info-r'>\
                            <select class='bt-input-text mr5' name='dbname' style='width:100%'>\
                                <option value=''>无</option>\
                            </select>\
                        </div>\
                    </div>\
                    <div class='line'>\
                        <span class='tname'>选择表</span>\
                        <div class='info-r'>\
                            <div id='table'></div>\
                        </div>\
                    </div>\
                    <div class='line'>\
                        <span class='tname'>是否增量</span>\
                        <div class='info-r'>\
                            <select class='bt-input-text mr5' name='is_delta' style='width:100px'>\
                                <option value='no'>否</option>\
                                <option value='yes'>是</option>\
                            </select>\
                        </div>\
                    </div>\
                    <div class='line'>\
                        <span class='tname'>是否覆盖配置</span>\
                        <div class='info-r'>\
                            <select class='bt-input-text mr5' name='is_cover' style='width:100px'>\
                                <option value='yes'>是</option>\
                                <option value='no'>否</option>\
                            </select>\
                        </div>\
                    </div>\
                    <ul class='help-info-text c7'>\
                        <li style='color:red;'>具体配置，仍须手动修改!!!</li>\
                        <li style='color:red;'>增量索引,需要有更新权限,主从分离时,需要主库配置</li>\
                    </ul>\
                </form>\
            ",

        success:function(l,i){
            $(l).find('.layui-layer-content').css('overflow','visible');

            xm_db_list = xmSelect.render({
                el: '#table', 
                repeat: false,
                toolbar: {show: true},
                data: [],
            });

            myPost('get_db_list', {"page":1,"page_size":20}, function(data){
                var rdata = $.parseJSON(data.data);
                var dblist = rdata.data;

                var db_html = '';
                for (var i = 0; i < dblist.length; i++) {
                    db_html += "<option value='"+dblist[i]['name']+"'>"+dblist[i]['name']+"</option>";
                }

                if (dblist.length > 0){
                    initDbSelect(dblist[0]['name']);
                }
                $('select[name="dbname"]').html(db_html);
            });

            $('select[name="dbname"]').change(function(){
                var db = $('select[name="dbname"]').val();
                initDbSelect(db);
            });

        },
        yes:function(index){
            var args = {}
            args['db'] = $('select[name="dbname"]').val();
            args['is_delta'] = $('select[name="is_delta"]').val();
            args['is_cover'] = $('select[name="is_cover"]').val();
            args['tables'] = xm_db_list.getValue('value').join(',');
            // console.log(args);
            spPost('db_to_sphinx', args, function(rdata){
                var rdata = $.parseJSON(rdata.data);
                // console.log(rdata);
                showMsg(rdata.msg,function(){
                    if (rdata.status){
                       layer.close(index);
                       confirmRebuildIndex();
                    }
                },{icon: rdata.status ? 1 : 2}, 2000);
            });
        }

    });

    function initDbSelect(db){
        if (db == ''){
            return;
        }
        getDbInfo(db, function(rdata){
            var rdata = $.parseJSON(rdata.data);
            var tables = rdata.tables;

            var idx_db = [];
            for (var i = 0; i < tables.length; i++) {
                var t = {};
                t['name'] = tables[i]['table_name'];
                t['value'] = tables[i]['table_name'];
                idx_db.push(t);
            }
            xm_db_list = xmSelect.render({el: '#table', filterable: true,repeat: false,toolbar: {show: true},data: idx_db,});
        });
    }

    function getDbInfo(db_name, callback){
        myPost('get_db_info', {name:db_name}, function(data){
            callback(data);
        });
    }
}

function rebuildIndex(){
    spPost('rebuild', '', function(data){
        if (data.data == 'ok'){
            layer.msg('重建成功!',{icon:1,time:2000,shade: [0.3, '#000']});
        } else {
            layer.msg(data.data,{icon:2,time:10000,shade: [0.3, '#000']});
        }
    });
}

function confirmRebuildIndex(){
    layer.confirm("是否重建索引?", {icon:3,closeBtn: 1} , function(){
        rebuildIndex();
    });
}


function tryRebuildIndex(){
    layer.confirm("修改配置后，是否尝试重建索引!", {icon:3,closeBtn: 1} , function(){
        rebuildIndex();
    });
}


function secToTime(s) {
    var t;
    if(s > -1){
        var hour = Math.floor(s/3600);
        var min = Math.floor(s/60) % 60;
        var sec = s % 60;
        if(hour < 10) {
            t = '0'+ hour + ":";
        } else {
            t = hour + ":";
        }

        if(min < 10){t += "0";}
        t += min + ":";
        if(sec < 10){t += "0";}
        t += sec.toFixed(2);
    }
    return t;
}


function runStatus(){
    spPost('run_status', '', function(data){
        var rdata = $.parseJSON(data.data);
        if (!rdata['status']){
            layer.msg(rdata['msg'],{icon:2,time:2000,shade: [0.3, '#000']});
            return;
        }
        var idata = rdata.data;

        var sv = function(k){
            if (typeof(idata[k]) == 'undefined' || idata[k] === ''){
                return '-';
            }
            return idata[k];
        };

        var uptime = parseFloat(idata.uptime);
        var queries = parseFloat(idata.queries);
        var qps = (uptime > 0 && !isNaN(queries)) ? (queries / uptime).toFixed(2) : '-';

        // searchd 状态字段的中文名称与说明, 便于直接观察
        var statusInfo = {
            uptime: ['运行时间', '服务启动至今的运行秒数'],
            connections: ['总连接次数', '自启动以来建立的客户端连接总数'],
            maxed_out: ['超出连接上限次数', '并发达到上限后被拒绝的请求次数'],
            work_queue_length: ['等待队列长度', '当前排队等待处理的请求数, 长期大于 0 表示搜索压力偏大'],
            work_queue_max: ['队列峰值', '等待队列出现过的最大长度'],
            workers_active: ['活跃线程数', '正在处理请求的工作线程数'],
            workers_total: ['线程总数', 'searchd 启动的工作线程总数'],
            workers_avail: ['空闲线程数', '当前空闲可用的工作线程数'],
            queries: ['查询总次数', '累计执行的搜索查询次数'],
            dist_queries: ['分布式查询次数', '转发到远端 agent 的查询次数'],
            command_search: ['搜索请求数', '客户端发起的搜索请求总数'],
            command_excerpt: ['摘要请求数', '生成摘要(excerpt)的请求数'],
            command_update: ['更新请求数', '文档全量更新请求数'],
            command_delete: ['删除请求数', '文档删除请求数'],
            command_keywords: ['关键词提取请求数', '关键词(keywords)提取请求数'],
            command_persist: ['持久化请求数', '索引落盘持久化请求数'],
            command_status: ['状态查询次数', '状态信息查询请求数'],
            command_flushattrs: ['刷新属性请求数', '强制刷新属性的请求数'],
            command_setfilter: ['设置过滤器请求数', '设置过滤条件的请求数'],
            command_rtmerge: ['实时索引合并次数', '实时(RT)索引合并请求数'],
            command_attr_update: ['属性更新请求数', '按文档批量更新属性的请求数'],
            agent_connect: ['agent 连接次数', '与远端 agent 建立连接的次数'],
            agent_retry: ['agent 重试次数', '连接远端 agent 失败后的重试次数']
        };

        var tbody = '';
        var used = {};
        for (var key in statusInfo) {
            used[key] = true;
            var name = statusInfo[key][0];
            tbody += '<tr><th>' + name + '<br><span class="c8" style="font-weight:normal;">' + key + '</span></th>\
                <td>' + sv(key) + '</td><td class="c6">' + statusInfo[key][1] + '</td></tr>';
        }
        for (var i in idata) {
            if (used[i]) {
                continue;
            }
            tbody += '<tr><th>' + i + '</th><td>' + idata[i] + '</td><td class="c6">searchd 原始指标</td></tr>';
        }

        var con = '<div class="divtable"><table class="table table-hover table-bordered" style="margin-bottom:10px;background-color:#fafafa">\
                    <tbody>\
                        <tr><th>运行时间</th><td>' + secToTime(idata.uptime) + '</td><th>每秒查询(平均)</th><td>' + qps + '</td></tr>\
                        <tr><th>总连接次数</th><td>' + sv('connections') + '</td><th>等待队列长度</th><td>' + sv('work_queue_length') + '</td></tr>\
                        <tr><th>工作线程(活跃/总数)</th><td>' + sv('workers_active') + ' / ' + sv('workers_total') + '</td><th>超出连接上限次数</th><td>' + sv('maxed_out') + '</td></tr>\
                        <tr><th>agent 连接次数</th><td>' + sv('agent_connect') + '</td><th>agent 重试次数</th><td>' + sv('agent_retry') + '</td></tr>\
                    </tbody>\
                    </table>\
                    <table class="table table-hover table-bordered">\
                        <thead><tr><th style="width:32%;">指标</th><th style="width:20%;">数值</th><th>中文说明</th></tr></thead>\
                        <tbody>\
                            '+tbody+'\
                        </tbody>\
                    </table>\
                </div>';

        $(".soft-man-con").html(con);
    });
}

function readme(){
    spPost('sphinx_cmd', '', function(data){

        var rdata = $.parseJSON(data.data);
        if (!rdata['status']){
            layer.msg(rdata['msg'],{icon:2,time:2000,shade: [0.3, '#000']});
            return;
        }

        // console.log(rdata['data']);
        var con = '<ul class="help-info-text c7">';

        con += '<li style="color:red;">如果数据量比较大,第一次启动会失败!(可通过手动建立索引)</li>';
        con += '<li style="color:red;">以下内容,需手动加入计划任务。</li>';

        con += '<li>全量:' + rdata['data']['cmd'] + ' --all --rotate</li>';

        //主索引
        for (var i = 0; i < rdata['data']['index'].length; i++) {
            var index_kv = rdata['data']['index'][i];
            var index = index_kv['index'];
            // console.log(index);
            con += '<li>主索引 :' + rdata['data']['cmd'] + ' '+ index +' --rotate</li>';
            if (typeof(index_kv['delta']) != 'undefined'){
                var delta = index_kv['delta'];
                con += '<li>增量索引 :' + rdata['data']['cmd'] + ' '+ delta +' --rotate</li>';
                con += '<li>合并索引 :' + rdata['data']['cmd'] + ' --merge '+ index  + ' ' + delta +' --rotate</li>';
            }
        }
        con += '</ul>';

        $(".soft-man-con").html(con);
    });
    
}

