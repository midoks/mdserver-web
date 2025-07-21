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

        var tbody = '';
        for (var i in idata) {
            tbody += '<tr><th>'+i+'</th><td>' + idata[i] + '</td><td colspan="2">'+i+'</td></tr>';
        }

        var con = '<div class="divtable"><table class="table table-hover table-bordered" style="margin-bottom:10px;background-color:#fafafa">\
                    <tbody>\
                        <tr><th>运行时间</th><td>' + secToTime(idata.uptime) + '</td><th>每秒查询</th><td>' + parseInt(parseInt(idata.queries) / parseInt(idata.uptime)) + '</td></tr>\
                        <tr><th>总连接次数</th><td>' + idata.connections + '</td><th>work_queue_length</th><td>' +idata.work_queue_length + '</td></tr>\
                        <tr><th>agent_connect</th><td>' + idata.agent_connect+ '</td><th>workers_active</th><td>' + idata.workers_active + '</td></tr>\
                        <tr><th>agent_retry</th><td>' + idata.agent_retry + '</td><th>workers_total</th><td>' + idata.workers_total + '</td></tr>\
                    </tbody>\
                    </table>\
                    <table class="table table-hover table-bordered">\
                        <thead style="display:none;"><th></th><th></th><th></th><th></th></thead>\
                        <tbody>\
                            '+tbody+'\
                        <tbody>\
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

