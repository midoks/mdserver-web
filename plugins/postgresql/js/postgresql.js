function str2Obj(str){
    var data = {};
    kv = str.split('&');
    for(i in kv){
        v = kv[i].split('=');
        data[v[0]] = v[1];
    }
    return data;
}

function randomStr(b) {
    b = b || 32;
    var c = "AaBbCcDdEeFfGHhiJjKkLMmNnPpRSrTsWtXwYxZyz";
    var a = c.length;
    var d = "";
    for(i = 0; i < b; i++) {
        d += c.charAt(Math.floor(Math.random() * a))
    }
    return d
}

function randomLowerStr(b) {
    b = b || 32;
    var c = "abcdefhijkmnprstwxyz";
    var a = c.length;
    var d = "";
    for(i = 0; i < b; i++) {
        d += c.charAt(Math.floor(Math.random() * a))
    }
    return d
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
    $.post('/plugins/run', {name:'postgresql', func:method, args:_args}, function(data) {
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
    $.post('/plugins/run', {name:'postgresql', func:method, args:_args}, function(data) {
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

        function numberValue(value) {
            var number = Number(value);
            return isFinite(number) ? number : 0;
        }

        function displayValue(value) {
            return value === undefined || value === null || value === '' ? '-' : value;
        }

        function formatCount(value) {
            if (value === undefined || value === null || value === '') return '-';
            return numberValue(value).toLocaleString();
        }

        function formatDuration(value) {
            var seconds = Math.floor(numberValue(value));
            var days = Math.floor(seconds / 86400);
            var hours = Math.floor(seconds % 86400 / 3600);
            var minutes = Math.floor(seconds % 3600 / 60);
            var remainingSeconds = seconds % 60;
            if (days > 0) return days + '天 ' + hours + '小时';
            if (hours > 0) return hours + '小时 ' + minutes + '分钟';
            if (minutes > 0) return minutes + '分钟 ' + remainingSeconds + '秒';
            return remainingSeconds + '秒';
        }

        var uptime = numberValue(rdata.uptime);
        var commits = numberValue(rdata.com_commit);
        var rollbacks = numberValue(rdata.com_rollback);
        var tps = uptime > 0 ? ((commits + rollbacks) / uptime).toFixed(2) : '0.00';
        var blocksRead = numberValue(rdata.blks_read);
        var blocksHit = numberValue(rdata.blks_hit);
        var blocksTotal = blocksRead + blocksHit;
        var cacheHit = blocksTotal > 0 ? (blocksHit / blocksTotal * 100).toFixed(2) + '%' : '-';
        var tempBytes = numberValue(rdata.temp_bytes);

        function formatReplicationStatus(value) {
            var status = displayValue(value);
            var names = {
                'streaming': '流复制中',
                'catchup': '追赶中',
                'backup': '备份中',
                'stopping': '已停止',
                'startup': '启动中'
            };
            return names[status] || status;
        }

        function formatSyncState(value) {
            var names = {
                'sync': '同步',
                'async': '异步',
                'potential': '潜在同步',
                'quorum': '仲裁同步'
            };
            return names[value] || displayValue(value);
        }

        function formatDelay(value) {
            if (value === undefined || value === null || value === '') return '-';
            return formatDuration(value);
        }

        var replication = rdata.replication || {};
        var role = replication.role || 'unknown';
        var roleHtml = '<span class="label label-default">未知</span>';
        if (role === 'primary') roleHtml = '<span class="label label-success">主库</span>';
        if (role === 'standby') roleHtml = '<span class="label label-info">从库</span>';

        var replicationSummaryLabel = role === 'primary' ? '从库连接' : '复制状态';
        var replicationSummary = role === 'primary' ?
            formatCount(replication.replica_count || 0) + ' 个' :
            formatReplicationStatus(replication.status);
        var replicas = replication.replicas || [];
        var replicationCon = '';

        if (role === 'primary' && replicas.length > 0) {
            replicationCon = '<div style="font-weight:bold;margin:10px 0 6px">从库复制</div>\
                <table class="table table-hover table-bordered" style="margin-bottom:10px">\
                <thead><tr><th>从库</th><th>地址</th><th>状态</th><th>同步模式</th><th>发送/回放位置</th><th>延迟</th></tr></thead>\
                <tbody>';
            for (var i = 0; i < replicas.length; i++) {
                var replica = replicas[i];
                replicationCon += '<tr><td>' + displayValue(replica.name) + '</td><td>' + displayValue(replica.address) + '</td>\
                    <td>' + formatReplicationStatus(replica.state) + '</td><td>' + formatSyncState(replica.sync_state) + '</td>\
                    <td>' + displayValue(replica.sent_lsn) + '<br>' + displayValue(replica.replay_lsn) + '</td>\
                    <td>' + formatDelay(replica.replay_lag) + '</td></tr>';
            }
            replicationCon += '</tbody></table>';
        }

        if (role === 'standby') {
            var sender = displayValue(replication.sender_host);
            if (replication.sender_port && replication.sender_port !== '-') {
                sender += ':' + replication.sender_port;
            }
            replicationCon = '<div style="font-weight:bold;margin:10px 0 6px">主库复制</div>\
                <table class="table table-hover table-bordered" style="margin-bottom:10px"><tbody>\
                <tr><th>主库地址</th><td>' + sender + '</td><th>复制槽</th><td>' + displayValue(replication.slot_name) + '</td></tr>\
                <tr><th>接收状态</th><td>' + formatReplicationStatus(replication.status) + '</td><th>回放延迟</th><td>' + formatDelay(replication.replay_lag) + '</td></tr>\
                <tr><th>接收位置</th><td>' + displayValue(replication.receive_lsn) + '</td><th>回放位置</th><td>' + displayValue(replication.replay_lsn) + '</td></tr>\
                </tbody></table>';
        }

        var con = '<div class="divtable">\
                    <div style="font-weight:bold;margin-bottom:6px">运行概览</div>\
                    <table class="table table-hover table-bordered" style="margin-bottom:10px;background-color:#fafafa">\
                    <tbody>\
                        <tr><th>数据库角色</th><td>' + roleHtml + '</td><th>' + replicationSummaryLabel + '</th><td>' + replicationSummary + '</td></tr>\
                        <tr><th>启动时间</th><td>' + displayValue(rdata.run_time) + '</td><th>运行时长</th><td>' + formatDuration(uptime) + '</td></tr>\
                        <tr><th>当前/活动连接</th><td>' + formatCount(rdata.connections) + ' / ' + formatCount(rdata.threads_running) + '</td><th>最大连接数</th><td>' + formatCount(rdata.max_connections) + '</td></tr>\
                        <tr><th>数据库总大小</th><td>' + displayValue(rdata.pg_size) + '</td><th>主进程内存</th><td>' + displayValue(rdata.pg_mem) + '</td></tr>\
                        <tr><th>进程数</th><td>' + formatCount(rdata.progress_num) + '</td><th>PID</th><td>' + displayValue(rdata.pid) + '</td></tr>\
                        <tr><th>WAL文件</th><td>' + displayValue(rdata.file) + '</td><th>WAL位置</th><td>' + displayValue(rdata.position) + '</td></tr>\
                    </tbody>\
                    </table>' + replicationCon + '<div style="font-weight:bold;margin:10px 0 6px">累计统计</div>\
                    <table class="table table-hover table-bordered">\
                    <tbody>\
                        <tr><th>平均TPS</th><td>' + tps + '</td><th>缓存命中率</th><td>' + cacheHit + '</td></tr>\
                        <tr><th>提交/回滚事务</th><td>' + formatCount(commits) + ' / ' + formatCount(rollbacks) + '</td><th>死锁/恢复冲突</th><td>' + formatCount(rdata.deadlocks) + ' / ' + formatCount(rdata.conflicts) + '</td></tr>\
                        <tr><th>返回/提取行数</th><td>' + formatCount(rdata.tup_returned) + ' / ' + formatCount(rdata.tup_fetched) + '</td><th>插入/更新/删除行数</th><td>' + formatCount(rdata.tup_inserted) + ' / ' + formatCount(rdata.tup_updated) + ' / ' + formatCount(rdata.tup_deleted) + '</td></tr>\
                        <tr><th>临时文件数</th><td>' + formatCount(rdata.temp_files) + '</td><th>临时文件大小</th><td>' + toSize(tempBytes) + '</td></tr>\
                    </tbody>\
                    </table></div>';
        $(".soft-man-con").html(con);
    });
}


function pgPort(){
    myPost('pg_port','',function(data){
        var con = '<div class="line ">\
            <div class="info-r  ml0">\
            <input name="port" class="bt-input-text mr5 port" type="text" style="width:100px" value="'+data.data+'">\
            <button id="btn_change_port" name="btn_change_port" class="btn btn-success btn-sm mr5 ml5 btn_change_port">修改</button>\
            </div></div>';
        $(".soft-man-con").html(con);

        $('#btn_change_port').click(function(){
            var port = $("input[name='port']").val();
            myPost('set_pg_port','port='+port,function(data){
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
function pgPerfOpt() {
    myPost('db_status','',function(data){
        var rdata = $.parseJSON(data.data);
        if (!rdata.status){
            $(".soft-man-con").html('<div class="alert alert-warning" style="margin:15px 0">' + (rdata.msg || '获取配置失败') + '</div>');
            return;
        }

        var html_p = '';
        for (var i = 0; i < rdata.params.length; i++){
            var p = rdata.params[i];
            var unitCon = p.type == 'memory' ?
                '<span class="pg-unit" style="display:inline-block;width:20px;">' + p.unit + '</span>' :
                '<span style="display:inline-block;width:0px"></span>';
            html_p += '<div class="pg-param" style="display:flex;align-items:center;padding:6px 0;border-bottom:1px dashed #eee">\
                <span style="width:150px;text-align:right;margin-right:12px">' + p.label + '</span>\
                <input class="bt-input-text" data-type="' + p.type + '" name="' + p.name + '" value="' + p.value + '" type="number" step="any" min="0" style="width:90px;margin-right:8px">\
                ' + unitCon + '\
                <font class="text-muted" style="flex:1;font-size:10px;">' + p.desc + '</font>\
            </div>';
        }

        var options = '<option value="0">请选择</option>';
        for (var j = 0; j < rdata.profiles.length; j++){
            options += '<option value="' + rdata.profiles[j].memory + '">' + rdata.profiles[j].memory + 'GB</option>';
        }

        var memoryHint = '';
        if (rdata.total_memory > 0){
            memoryHint = '<span class="text-muted" style="margin-left:10px;width:260px;">检测到物理内存 ' + Math.round(rdata.total_memory / 1024) + 'GB，选择后自动填入推荐值</span>';
        }

        var memCon = '<div class="conf_p" style="margin-bottom:0">\
            <div style="border-bottom:#ccc 1px solid;padding-bottom:10px;margin-bottom:10px">\
                <span><b>内存推荐配置: </b></span>\
                <select class="bt-input-text" name="pg_set">' + options + '</select>' + memoryHint + '\
            </div>\
            <div id="pg_conf">' + html_p + '</div>\
            <div style="margin-top:10px;padding-right:15px" class="text-right">\
                <button class="btn btn-default btn-sm mr5" onclick="reBootPgSqld()">重启数据库</button>\
                <button class="btn btn-success btn-sm pg_conf">保存</button>\
            </div>\
        </div>';

        $(".soft-man-con").html(memCon);

        $(".conf_p select[name='pg_set']").change(function() {
            pgSQLMemOpt($(this).val(), rdata.profiles);
        });

        $(".pg_conf").unbind('click').click(function (e) {
            e.preventDefault();
            var data = {};
            $('#pg_conf .pg-param').each(function () {
                var input = $(this).find('input');
                var value = $.trim(input.val());
                if (value === '') return;
                if (input.attr('data-type') == 'memory'){
                    value += $(this).find('.pg-unit').text();
                }
                data[input.attr('name')] = value;
            });
            myPost('set_db_status', data, function(data){
                var rdata = $.parseJSON(data.data);
                showMsg(rdata.msg, function(){
                    if (rdata.status) pgPerfOpt();
                }, { icon: rdata.status ? 1 : 2 });
            });
            return false;
        });
    });
}

function pgSQLMemOpt(memory, profiles){
    if (!profiles) return;

    var profile = null;
    for (var i = 0; i < profiles.length; i++){
        if (String(profiles[i].memory) === String(memory)){
            profile = profiles[i];
            break;
        }
    }
    if (!profile) return;

    var names = ['shared_buffers', 'effective_cache_size', 'maintenance_work_mem', 'work_mem', 'temp_buffers'];
    for (var j = 0; j < names.length; j++){
        var matched = /^(\d+(?:\.\d+)?)\s*(kB|MB|GB|TB)$/i.exec(profile[names[j]] || '');
        if (!matched) continue;

        var unit = matched[2].toUpperCase();
        if (unit == 'KB') unit = 'kB';

        var row = $('#pg_conf input[name="' + names[j] + '"]').closest('.pg-param');
        row.find('input').val(matched[1]);
        row.find('.pg-unit').text(unit);
    }
}

function reBootPgSqld(){
    pluginOpService('postgresql','restart','');
}

//设置PG配置参数
function setPgConf() {
    return false;
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
            },{icon: rdata.status ? 1 : 2});
        });
        return;
    }

    layer.open({
        type: 1,
        area: '600px',
        title: '修改数据库密码',
        closeBtn: 1,
        shift: 5,
        shadeClose: true,
        btn:["提交", "关闭", "复制PG密码", "修改本地PG记录", "强改PG密码"],
        content: "<form class='bt-form pd20' id='mod_pwd'>\
                    <div class='line'>\
                        <span class='tname'>postgres密码</span>\
                        <div class='info-r'>\
                            <input class='bt-input-text mr5' type='text' name='password' id='MyPassword' style='width:330px' value='"+pwd+"' />\
                            <span title='随机密码' class='glyphicon glyphicon-repeat cursor' onclick='repeatPwd(16)'></span>\
                        </div>\
                    </div>\
                </form>",
        yes:function(layerIndex){
            var password = $("#MyPassword").val();
            myPost('set_postgres_pwd', {password:password}, function(data){
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
            layer.confirm('修改本地PG记录,确定修改?', {
                btn: ['确定', '取消']
            }, function(index, layero){
                layer.close(index);
                var password = $("#MyPassword").val();
                myPost('set_postgres_pwd', {password:password,force:'1'}, function(data){
                    var rdata = $.parseJSON(data.data);
                    showMsg(rdata.msg,function(){
                        layer.close(layerIndex);
                        dbList();
                    },{icon: rdata.status ? 1 : 2});   
                });
            });
            return false;
        },
        btn5:function(layerIndex){
            layer.confirm('强制修改PG密码,确定强制? (比较耗时)', {
                btn: ['确定', '取消']
            }, function(index, layero){
                layer.close(index);
                var password = $("#MyPassword").val();
                myPost('set_postgres_pwd', {password:password,force:'2'}, function(data){
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
        showMsg(rdata.msg, function(){
            dbList();
        },{icon:rdata.status ? 1 : 5,shade: [0.3, '#000']}, 2000);
    });
}

function repTools(db_name, res){
    myPost('get_db_info', {name:db_name}, function(data){
        var rdata = $.parseJSON(data.data);
        var tbody = '';
        for (var i = 0; i < rdata.tables.length; i++) {
            var t = rdata.tables[i];
            tbody += '<tr>\
                    <td><span style="width:220px;">' + t.schema + '.' + t.table_name + '</span></td>\
                    <td>' + t.type + '</td>\
                    <td>' + t.rows_count + '</td>\
                    <td>' + t.data_size + '</td>\
                    <td>' + t.index_size + '</td>\
                    <td>' + t.total_size + '</td>\
                </tr>';
        }
        if (tbody == ''){
            tbody = '<tr><td colspan="6" style="text-align:center;">暂无数据表</td></tr>';
        }

        if (res) {
            $(".gztr").html(tbody);
            $(".tools_size").html('大小：' + rdata.data_size);
            return;
        }

        layer.open({
            type: 1,
            title: "PostgreSQL数据表【" + db_name + "】",
            area: ['820px', '580px'],
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
                                        <th>表名(Schema.Table)</th>\
                                        <th>类型</th>\
                                        <th>行数</th>\
                                        <th>数据大小</th>\
                                        <th>索引大小</th>\
                                        <th>合计</th>\
                                    </tr>\
                                </thead>\
                                <tbody class="gztr">' + tbody + '</tbody>\
                            </table>\
                            </div>\
                        </div>\
                        <ul class="help-info-text c7">\
                            <li>【行数】count(*) 实时统计，大表打开时可能稍慢</li>\
                            <li>【数据/索引/合计】分别取自 pg_relation_size、pg_indexes_size、pg_total_relation_size，合计额外包含 TOAST/FSM</li>\
                        </ul></div>'
        });
        tableFixed('database_fix');
    });
}

function setDbAccess(name){
    myPost('get_db_access','name='+name, function(data){
        var rdata = $.parseJSON(data.data);
        if (!rdata.status){
            layer.msg(rdata.msg,{icon:2,shade: [0.3, '#000']});
            return;
        }
        
        layer.open({
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
                                <option value='127.0.0.1/32'>本地服务器</option>\
                                <option value='0.0.0.0/0'>所有人</option>\
                                <option value='ip'>指定网段</option>\
                                </select>\
                            </div>\
                        </div>\
                      </form>",
            success:function(){
                if (rdata.msg == '127.0.0.1/32'){
                    $('select[name="dataAccess"]').find("option[value='127.0.0.1/32']").attr("selected",true);
                } else if (rdata.msg == '0.0.0.0/0'){
                    $('select[name="dataAccess"]').find('option[value="0.0.0.0/0"]').attr("selected",true);
                } else {
                    $('select[name="dataAccess"]').find('option[value="ip"]').attr("selected",true);
                    $('select[name="dataAccess"]').after("<input value='"+rdata.msg+"' class='bt-input-text mr5' type='text' name='address' placeholder='如: 192.168.1.0/24' style='width: 230px; display: inline-block;'>");
                }

                $('select[name="dataAccess"]').change(function(){
                    var v = $(this).val();
                    if (v == 'ip'){
                        $(this).after("<input class='bt-input-text mr5' type='text' name='address' placeholder='如: 192.168.1.0/24' style='width: 230px; display: inline-block;'>");
                    } else {
                        $('input[name="address"]').remove()
                    }
                });
            },
            yes:function(index){
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
                dataObj['name'] = name;
                // console.log(dataObj);
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
    var index = layer.open({
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
                    <div class='info-r'><input class='bt-input-text mr5' type='text' name='password' id='MyPassword' style='width:330px' value='"+password+"' /><span title='随机密码' class='glyphicon glyphicon-repeat cursor' onclick='repeatPwd(16)'></span></div>\
                    </div>\
                    <input type='hidden' name='id' value='"+id+"'>\
                  </form>",
        yes:function(index){
            var data = $("#mod_pwd").serialize();
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

function addDatabase(type,layer_index){
    if (type == 1){
        var data = $("#add_db").serialize();
        data = decodeURIComponent(data);
        var dataObj = str2Obj(data);
        if(!dataObj['address']){
            dataObj['address'] = dataObj['dataAccess'];
        }
        
        var ip_segment = $('[name="dataAccess"]').val();
        if ($('[name="dataAccess"]').val() == 'ip'){
            dataObj['listen_ip'] = ip_segment;
        }
        myPost('add_db', dataObj, function(data){
            var rdata = $.parseJSON(data.data);
            showMsg(rdata.msg,function(){
                layer.close(layer_index);
                if (rdata.status){
                    dbList();
                }
            },{icon: rdata.status ? 1 : 2},2000);
        });
        return;
    }
    
    layer.open({
        type: 1,
        area: '450px',
        title: '添加数据库',
        closeBtn: 1,
        shift: 5,
        shadeClose: true,
        btn:["提交","取消"],
        content: "<form class='bt-form pd20' id='add_db'>\
                    <div class='line'>\
                        <span class='tname'>数据库名</span>\
                        <div class='info-r'>\
                            <input name='name' class='bt-input-text mr5' placeholder='新的数据库名称' type='text' style='width:270px' value=''>\
                        </div>\
                    </div>\
                    <div class='line'><span class='tname'>用户名</span><div class='info-r'><input name='db_user' class='bt-input-text mr5' placeholder='数据库用户' type='text' style='width:270px' value=''></div></div>\
                    <div class='line'>\
                    <span class='tname'>密码</span>\
                    <div class='info-r'><input class='bt-input-text mr5' type='text' name='password' id='MyPassword' style='width:270px' value='"+(randomStrPwd(16))+"' />\
                        <span title='随机密码' class='glyphicon glyphicon-repeat cursor' onclick='repeatPwd(16)'></span></div>\
                    </div>\
                    <div class='line'>\
                        <span class='tname'>访问权限</span>\
                        <div class='info-r'>\
                            <select class='bt-input-text mr5' name='dataAccess' style='width:100px'>\
                            <option value='127.0.0.1'>本地服务器</option>\
                            <option value=\"%\">所有人</option>\
                            <option value='ip'>指定网段</option>\
                            </select>\
                            <input class='bt-input-text' style='width: 162px;display:none;' placeholder='如: 192.168.1.0/24' name='ip_segment' value='' />\
                        </div>\
                    </div>\
                  </form>",
        success:function(){

            $("input[name='name']").keyup(function(){
                var v = $(this).val();
                $("input[name='db_user']").val(v);
            });

            $('select[name="dataAccess"]').change(function(){
                var v = $(this).val();
                if (v == 'ip'){
                    $('input[name="ip_segment"]').show();
                } else {
                    $('input[name="ip_segment"]').hide();
                    
                }
            });
        },
        yes:function(index){
            addDatabase(1,index);
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

function delBackup(filename,name){
    myPost('delete_db_backup',{filename:filename,path:""},function(rdata){
        layer.msg(rdata.msg, { icon: rdata.status ? 1 : 2 });
        setTimeout(function(){
            // $('.layui-layer-close2').click();
            setBackupReq(name);
        },2000);
    });
}

function downloadBackup(file){
    window.open('/files/download?filename='+encodeURIComponent(file));
}

function importBackup(file,name){
    myPost('import_db_backup',{file:file,name:name}, function(data){
        var rdata = $.parseJSON(data.data);
        layer.msg(rdata.msg, { icon: rdata.status ? 1 : 2 });
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

function setBackup(db_name,obj){
    layer.open({
        type: 1,
        title: "数据库备份详情",
        area: ['700px', '280px'],
        closeBtn: 2,
        shadeClose: false,
        content: '<div class="pd15">\
                    <div class="db_list">\
                        <button id="btn_backup" class="btn btn-success btn-sm" type="button">备份</button>\
                        <button id="btn_backup_reload" class="btn btn-success btn-sm" type="button">刷新</button>\
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
                        <tbody class="gztr"></tbody>\
                    </table>\
                    </div>\
                </div>\
        </div>',
        success:function(index){
            $('#btn_backup').click(function(){
                myPost('pg_back',{name:db_name}, function(data){
                    layer.msg('执行成功!');
                    setBackupReq(db_name);
                });
            });

            $('#btn_local_import').click(function(){
                setLocalImport(db_name);
            });

            $('#btn_backup_reload').click(function(){
                setBackupReq(db_name);
            });

            setBackupReq(db_name);
        },
    });
}

function setBackupReq(db_name, obj){
     myPost('pg_back_list', {name:db_name}, function(data){
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

            list += '<a href="javascript:;" class="btlink" class="btlink" onclick="setBackup(\''+rdata.data[i]['name']+'\',this)" title="数据库备份">'+(rdata.data[i]['is_backup']?'备份':'未备份') +'</a> | ';

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

            list +=  '<a href="javascript:;" class="btlink" onclick="repTools(\''+rdata.data[i]['name']+'\')" title="数据表信息">工具</a> | '
            list += '<a href="javascript:;" class="btlink" onclick="setDbAccess(\''+rdata.data[i]['name']+'\')" title="设置数据库权限">权限</a> | ' +
                        rw +
                        '<a href="javascript:;" class="btlink" onclick="setDbPass('+rdata.data[i]['id']+',\''+ rdata.data[i]['username'] +'\',\'' + rdata.data[i]['password'] + '\')">改密</a> | ' +
                        '<a href="javascript:;" class="btlink" onclick="delDb(\''+rdata.data[i]['id']+'\',\''+rdata.data[i]['name']+'\')" title="删除数据库">删除</a>' +
                    '</td>';
            list += '</tr>';
        }

        //<button onclick="" id="dataRecycle" title="删除选中项" class="btn btn-default btn-sm" style="margin-left: 5px;"><span class="glyphicon glyphicon-trash" style="margin-right: 5px;"></span>回收站</button>
        var con = '<div class="safe bgw">\
            <button onclick="addDatabase()" title="添加数据库" class="btn btn-success btn-sm" type="button" style="margin-right: 5px;">添加数据库</button>\
            <button onclick="setRootPwd(0,\''+rdata.info['root_pwd']+'\')" title="管理员密码" class="btn btn-default btn-sm" type="button" style="margin-right: 5px;">PG密码</button>\
            <button onclick="setDbAccess(\'postgres\')" title="ROOT权限" class="btn btn-default btn-sm" type="button" style="margin-right: 5px;">ROOT权限</button>\
            <button onclick="fixDbAccess(\'postgres\')" title="修复" class="btn btn-default btn-sm" type="button" style="margin-right: 5px;">修复</button>\
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
                    <th>备注</th>\
                    <th style="text-align:right;">操作</th></tr></thead>\
                    <tbody>\
                    '+ list +'\
                    </tbody></table>\
                </div>\
                <div id="databasePage" class="dataTables_paginate paging_bootstrap page"></div>\
                <div class="table_toolbar" style="left:0px;">\
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
///////////////////////////////// 主从 /////////////////////////


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


function repeatMSPwd(a) {
    $("#MyPassword").val(randomStr(a))
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
            <div class='line'><span class='tname'>用户名</span><div class='info-r'><input name='username' class='bt-input-text mr5' placeholder='用户名' type='text' style='width:330px;' value='"+(randomLowerStr(6))+"'></div></div>\
            <div class='line'>\
                <span class='tname'>密码</span>\
                <div class='info-r'>\
                    <input class='bt-input-text mr5' type='text' name='password' id='MyPassword' style='width:330px' value='"+(randomStr(16))+"' />\
                    <span title='随机密码' class='glyphicon glyphicon-repeat cursor' onclick='repeatMSPwd(16)'></span>\
                </div>\
            </div>\
            <div class='line'>\
                <span class='tname'>网段</span>\
                <div class='info-r'>\
                    <input class='bt-input-text mr5' type='text' name='address' style='width:330px' value='0.0.0.0/0' />\
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
        yes:function(index){
            var data = $("#add_master").serialize();
            data = decodeURIComponent(data);
            var dataObj = str2Obj(data);
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



function updateMasterRepSlaveUser(username){
  
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
        myPost('update_master_rep_slave_user', data, function(data){
            var rdata = $.parseJSON(data.data);
            showMsg(rdata.msg,function(){
                if (rdata.status){
                    getMasterRepSlaveList();
                }
            },{icon: rdata.status ? 1 : 2},600);
        });
    });
}


function setMasterRepSlaveAccess(name){
    myPost('get_master_rep_slave_access','name='+name, function(data){
        var rdata = $.parseJSON(data.data);
        if (!rdata.status){
            layer.msg(rdata.msg,{icon:2,shade: [0.3, '#000']});
            return;
        }
        
        layer.open({
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
                                <option value='127.0.0.1/32'>本地服务器</option>\
                                <option value='0.0.0.0/0'>所有人</option>\
                                <option value='ip'>指定网段</option>\
                                </select>\
                            </div>\
                        </div>\
                      </form>",
            success:function(){
                if (rdata.msg == '127.0.0.1/32'){
                    $('select[name="dataAccess"]').find("option[value='127.0.0.1/32']").attr("selected",true);
                } else if (rdata.msg == '0.0.0.0/0'){
                    $('select[name="dataAccess"]').find('option[value="0.0.0.0/0"]').attr("selected",true);
                } else {
                    $('select[name="dataAccess"]').find('option[value="ip"]').attr("selected",true);
                    $('select[name="dataAccess"]').after("<input value='"+rdata.msg+"' class='bt-input-text mr5' type='text' name='address' placeholder='如: 192.168.1.0/24' style='width: 230px; display: inline-block;'>");
                }

                $('select[name="dataAccess"]').change(function(){
                    var v = $(this).val();
                    if (v == 'ip'){
                        $(this).after("<input class='bt-input-text mr5' type='text' name='address' placeholder='如: 192.168.1.0/24' style='width: 230px; display: inline-block;'>");
                    } else {
                        $('input[name="address"]').remove()
                    }
                });
            },
            yes:function(index){
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
                dataObj['name'] = name;
                // console.log(dataObj);
                myPost('set_master_rep_slave_access', dataObj, function(data){
                    var rdata = $.parseJSON(data.data);
                    showMsg(rdata.msg,function(){
                        layer.close(index);
                        masterOrSlaveConf();
                    },{icon: rdata.status ? 1 : 2});   
                });
            }
        });

    });
}

function getMasterRepSlaveUserCmd(username, db=''){
    myPost('get_master_rep_slave_user_full_cmd', {username:username,db:db}, function(data){
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
        layer.msg(rdata.msg);

        showMsg(rdata.msg, function(){
            getMasterRepSlaveList();
        },{icon: rdata.status ? 1 : 2},1000);
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
            // console.log(i);/setDbMasterAccess
            var name = user_list[i]['username'];
            list += '<tr><td>'+name+'</td>\
                <td>'+user_list[i]['password']+'</td>\
                <td>\
                    <a class="btlink" onclick="delMasterRepSlaveUser(\''+name+'\');">删除</a> | \
                    <a class="btlink" onclick="setMasterRepSlaveAccess(\''+name+'\');">权限</a> | \
                    <a class="btlink" onclick="getMasterRepSlaveUserCmd(\''+name+'\');">从库同步命令</a> \
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


function deleteSlave(){
    myPost('delete_slave', {}, function(data){
        var rdata = $.parseJSON(data.data);
        showMsg(rdata['msg'], function(){
            masterOrSlaveConf();
        },{},3000);
    });
}


function getFullSyncStatus(db){
    var timeId = null;

    var btn = '<div class="table_toolbar" style="left:0px;"><span data-status="init" class="sync btn btn-default btn-sm" id="begin_full_sync" title="">开始</span></div>';
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
            </div>",
        cancel: function(){ 
            clearInterval(timeId);
        }
    });

    function fullSync(db,begin){
       
        myPostN('full_sync', {db:db,begin:begin}, function(data){
            var rdata = $.parseJSON(data.data);
            $('#full_msg').text(rdata['msg']);
            $('.progress-bar').css('width',rdata['progress']+'%');
            $('.progress-bar').text(rdata['progress']+'%');

            if (rdata['code']==6 ||rdata['code']<0){
                layer.msg(rdata['msg']);
                clearInterval(timeId);
                $("#begin_full_sync").attr('data-status','init');
            }
        });
    }

    $('#begin_full_sync').click(function(){
        var val = $(this).attr('data-status');
        if (val == 'init'){
            fullSync(db,1);
            timeId = setInterval(function(){
                fullSync(db,0);
            }, 1000);
            $(this).attr('data-status','starting');
        } else {
            layer.msg("正在同步中..");
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

        layer.open({
            type: 1,
            area: ['500px','450px'],
            title: '添加SSH',
            closeBtn: 1,
            shift: 5,
            shadeClose: true,
            btn:["确认","取消"],
            content: "<form class='bt-form pd20'>\
                <div class='line'><span class='tname'>IP</span><div class='info-r'><input name='ip' class='bt-input-text mr5' type='text' style='width:330px;' value='"+ip+"'></div></div>\
                <div class='line'><span class='tname'>端口</span><div class='info-r'><input name='port' class='bt-input-text mr5' type='number' style='width:330px;' value='"+port+"'></div></div>\
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
        layer.msg(rdata.msg, {icon: rdata.status ? 1 : 2});
        getSlaveSSHPage();
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
        var slot_name = '';

        if (rdata.data.length>0){
            ip = rdata.data[0]['ip'];
            port = rdata.data[0]['port'];
            cmd = rdata.data[0]['cmd'];
            user = rdata.data[0]['user'];
            pass = rdata.data[0]['pass'];
            mode = rdata.data[0]['mode'];
            slot_name = rdata.data[0]['slot_name'];
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
                <div class='line'><span class='tname'>槽名</span><div class='info-r'><input name='slot_name' class='bt-input-text mr5' type='text' style='width:330px;' value='"+slot_name+"'></div></div>\
                <div class='line'>\
                    <span class='tname'>同步模式</span>\
                    <div class='info-r'>\
                        <select class='bt-input-text mr5' name='mode'>\
                            <option value='0' "+( mode == '0' ? 'selected="selected"' : '')+">经典</option>\
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
                    if (val == '') {
                        return;
                    }
                    // PGPASSWORD='xxx' /www/server/postgresql/bin/pg_basebackup -D /www/server/postgresql/data -h 1.1.1.1 -p 5432 -U user --password -S slot
                    var pass = val.match(/PGPASSWORD=['"]?([^'"\s]+)['"]?/);
                    var ip = val.match(/-h\s+([^\s]+)/);
                    var port = val.match(/-p\s+(\d+)/);
                    var user = val.match(/-U\s+([^\s]+)/);
                    var slot = val.match(/-S\s+([^\s]+)/);
                    if (pass) {
                        $('input[name="pass"]').val(pass[1]);
                    }
                    if (ip) {
                        $('input[name="ip"]').val(ip[1]);
                    }
                    if (port) {
                        $('input[name="port"]').val(port[1]);
                    }
                    if (user) {
                        $('input[name="user"]').val(user[1]);
                    }
                    if (slot) {
                        $('input[name="slot_name"]').val(slot[1]);
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
                var slot_name = $('input[name="slot_name"]').val();

                var data = {ip:ip,port:port,cmd:cmd,user:user,pass:pass,mode:mode,slot_name:slot_name};
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
        area: '500px',
        content:"<div class='bt-form pd20 c6'>\
                 <div class='divtable mtb10'>\
                    <div><table class='table table-hover get-slave-ssh-list'>\
                        <thead><tr><th>IP</th><th>PORT</th><th>SSH</th><th>操作</th></tr></thead>\
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

function slaveSyncCmd(){
    myPost('slave_sync_cmd', {}, function(data){
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

function masterOrSlaveConf(version=''){

    function replicationValue(value) {
        return value === undefined || value === null || value === '' ? '-' : value;
    }

    function replicationDelay(value) {
        if (value === undefined || value === null || value === '') return '-';
        if (typeof value === 'string' && value.indexOf(':') > -1) {
            var parts = value.split(':');
            if (parts.length === 3) {
                value = parseInt(parts[0], 10) * 3600 + parseInt(parts[1], 10) * 60 + parseFloat(parts[2]);
            }
        }
        var seconds = Number(value);
        if (!isFinite(seconds)) return replicationValue(value);
        if (seconds < 0) return '-';
        if (seconds > 0 && seconds < 1) return Math.round(seconds * 1000) + '毫秒';
        seconds = Math.floor(seconds);
        var days = Math.floor(seconds / 86400);
        var hours = Math.floor(seconds % 86400 / 3600);
        var minutes = Math.floor(seconds % 3600 / 60);
        var remainingSeconds = seconds % 60;
        if (days > 0) return days + '天 ' + hours + '小时';
        if (hours > 0) return hours + '小时 ' + minutes + '分钟';
        if (minutes > 0) return minutes + '分钟 ' + remainingSeconds + '秒';
        return remainingSeconds + '秒';
    }

    function replicationStatus(value) {
        var status = replicationValue(value);
        var names = {
            'streaming': '流复制中',
            'catchup': '追赶中',
            'backup': '备份中',
            'stopping': '已停止',
            'startup': '启动中'
        };
        var labelClass = status === 'streaming' ? 'label-success' :
            (status === 'catchup' || status === 'backup' ? 'label-warning' : 'label-default');
        return '<span class="label ' + labelClass + '">' + (names[status] || status) + '</span>';
    }

    function replicationSync(value) {
        var names = {'sync': '同步', 'async': '异步', 'potential': '潜在同步', 'quorum': '仲裁同步'};
        return names[value] || replicationValue(value);
    }

    function replicationLsn(value) {
        return '<span style="font-family:monospace;word-break:break-all">' + replicationValue(value) + '</span>';
    }

    function getMasterDbList(){
        myPostN('get_master_link', {}, function(data){
            var rdata = $.parseJSON(data.data);
            if (rdata.status === false){
                $('.table_master_list').html('<div class="alert alert-danger" style="margin:10px 0">' + rdata.msg + '</div>');
                return;
            }

            var items = rdata.data || [];
            var list = '';
            for (var i = 0; i < items.length; i++){
                var item = items[i];
                var address = replicationValue(item.client_addr);
                if (item.client_port) address += ':' + item.client_port;
                list += '<div style="border:1px solid #ddd;border-radius:4px;margin-bottom:10px;overflow:hidden">\
                    <div class="clearfix" style="padding:8px 12px;background:#f5f5f5;">\
                        <strong>' + replicationValue(item.application_name) + '</strong><span class="pull-right">' + replicationStatus(item.state) + '</span>\
                    </div>\
                    <table class="table" style="margin:0;table-layout:fixed"><tbody>\
                        <tr><th style="width:15%">从库地址</th><td style="width:35%">' + address + '</td><th style="width:15%">复制账户</th><td style="width:35%">' + replicationValue(item.usename) + '</td></tr>\
                        <tr><th>同步模式</th><td>' + replicationSync(item.sync_state) + '</td><th>回放延迟</th><td>' + replicationDelay(item.replay_lag) + '</td></tr>\
                        <tr><th>发送位置</th><td>' + replicationLsn(item.sent_lsn) + '</td><th>写入位置</th><td>' + replicationLsn(item.write_lsn) + '</td></tr>\
                        <tr><th>刷盘位置</th><td>' + replicationLsn(item.flush_lsn) + '</td><th>回放位置</th><td>' + replicationLsn(item.replay_lsn) + '</td></tr>\
                    </tbody></table>\
                </div>';
            }

            if (items.length === 0){
                list = '<div class="text-center text-muted" style="padding:20px;border:1px dashed #ddd;margin-bottom:10px">暂无已连接的从库</div>';
            }
            var con = '<div class="mtb10">' + list + '<div class="clearfix">\
                <span class="sync btn btn-default btn-sm btn-master-refresh">刷新</span>\
                <span class="text-muted pull-right" style="line-height:30px">共 ' + items.length + ' 个从库连接</span>\
                </div></div>';
            $('.table_master_list').html(con);
            $('.table_master_list .btn-master-refresh').click(getMasterDbList);
        });
    }

    function getAsyncMasterDbList(){
        myPost('get_slave_link', {}, function(data){
            var rdata = $.parseJSON(data.data);
            if (rdata.status === false){
                $('.table_slave_status_list').html('<div class="alert alert-danger" style="margin:10px 0">' + rdata.msg + '</div>');
                return;
            }

            var items = rdata.data || [];
            var list = '';
            for (var i = 0; i < items.length; i++){
                var item = items[i];
                var address = replicationValue(item.sender_host);
                if (item.sender_port) address += ':' + item.sender_port;
                list += '<div style="border:1px solid #ddd;border-radius:4px;margin-bottom:10px;overflow:hidden">\
                    <div class="clearfix" style="padding:8px 12px;background:#f5f5f5;">\
                        <strong>主库 ' + address + '</strong><span class="pull-right">' + replicationStatus(item.status) + '</span>\
                    </div>\
                    <table class="table" style="margin:0;table-layout:fixed"><tbody>\
                        <tr><th style="width:15%">复制槽</th><td style="width:35%">' + replicationValue(item.slot_name) + '</td><th style="width:15%">回放延迟</th><td style="width:35%">' + replicationDelay(item.last_lsn_commit_time) + '</td></tr>\
                        <tr><th>接收位置</th><td>' + replicationLsn(item.receive_lsn) + '</td><th>回放位置</th><td>' + replicationLsn(item.replay_lsn) + '</td></tr>\
                        <tr><th>写入位置</th><td>' + replicationLsn(item.written_lsn) + '</td><th>刷盘位置</th><td>' + replicationLsn(item.flushed_lsn) + '</td></tr>\
                        <tr><th>接收起始</th><td>' + replicationLsn(item.receive_start_lsn) + '</td><th>最新结束</th><td>' + replicationLsn(item.latest_end_lsn) + '</td></tr>\
                    </tbody></table>\
                </div>';
            }

            if (items.length === 0){
                list = '<div class="text-center text-muted" style="padding:20px;border:1px dashed #ddd;margin-bottom:10px">暂无主库复制连接，请检查从库连接配置</div>';
            }
            var con = '<div class="mtb10">' + list + '<div>\
                <span class="sync btn btn-default btn-sm btn-slave-refresh">刷新</span>\
                </div></div>';
            $('.table_slave_status_list').html(con);
            $('.table_slave_status_list .btn-slave-refresh').click(getAsyncMasterDbList);
        });
    }

    function getMasterStatus(){
        myPost('get_master_status', '', function(data){
            var rdata = $.parseJSON(data.data);
            rdata = rdata.data;
            var limitCon = '\
                <p class="conf_p">\
                    <span class="f14 c6 mr20">复制模式</span><span class="f14 c6 mr20"></span>\
                    <button class="btn btn-default btn-xs">'+(rdata.mode == "classic" ? '经典流复制' : rdata.mode)+'</button>\
                </p>\
                <hr style="margin:12px 0"/>\
                <p class="conf_p">\
                    <span class="f14 c6 mr20">主库配置</span><span class="f14 c6 mr20"></span>\
                    <button title="'+(!rdata.status ? '开启主库复制' : '关闭主库复制')+'" class="btn '+(!rdata.status ? 'btn-danger' : 'btn-success')+' btn-xs btn-master">'+(!rdata.status ? '未开启' : '已开启') +'</button>\
                    <button class="btn btn-default btn-xs" onclick="getMasterRepSlaveListPage()">复制账户</button>\
                </p>\
                <hr style="margin:12px 0"/>\
                <!-- master list -->\
                <div class="safe bgw table_master_list"></div>\
                <hr style="margin:12px 0"/>\
                <!-- class="conf_p" -->\
                <p class="conf_p">\
                    <span class="f14 c6 mr20">从库配置</span><span class="f14 c6 mr20"></span>\
                    <button title="'+(!rdata.slave_status ? '开启从库复制' : '关闭从库复制')+'" class="btn '+(!rdata.slave_status ? 'btn-danger' : 'btn-success')+' btn-xs btn-slave">'+(!rdata.slave_status ? '未开启' : '已开启') +'</button>\
                    <button class="btn btn-default btn-xs" onclick="getSlaveCfg()">连接配置</button>\
                    <button class="btn btn-default btn-xs" onclick="slaveSyncCmd()">同步命令</button>\
                </p>\
                <hr style="margin:12px 0"/>\
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
            } else {
                $('.table_master_list').html('<div class="text-center text-muted" style="padding:20px;border:1px dashed #ddd;margin-bottom:10px">开启主库复制后，可在此查看从库连接状态</div>');
            }

            if (rdata.slave_status){
                getAsyncMasterDbList();
            } else {

                $('.table_slave_status_list').html('<div class="text-center text-muted" style="padding:20px;border:1px dashed #ddd;margin-bottom:10px">开启从库复制后，可在此查看主库连接状态</div>');
            }
        });
    }
    getMasterStatus();
}



function readme(){
    // console.log(rdata['data']);
    var con = '<ul class="help-info-text c7">';

    con += '<li style="color:red;">常规的维护任务</li>';
    con += '<li style="color:blue;">archivelog 外部维护</li>';
    con += '<li> - 按数量保留最近1000个</li>';
    con += '<li>ls -t /www/server/postgresql/archivelog/0000* 2>/dev/null | tail -n +1001 | xargs -r rm -f</li>';
    con += '<li> - 删除14天前的归档</li>';
    con += '<li>find /www/server/postgresql/archivelog -name "0000*" -type f -mtime +14 -delete</li>';
    con += '</ul>';

    $(".soft-man-con").html(con);
    
    
}

