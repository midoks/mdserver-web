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
    var con = '<button class="btn btn-default btn-sm" onclick="rebuildIndex();">重建索引</button>';
    $(".soft-man-con").html(con);
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


function tryRebuildIndex(){
    layer.confirm("修改配置后，是否尝试重建索引。", {icon:3,closeBtn: 1} , function(){
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

        var con = '<ul class="help-info-text c7">';

        con += '<li style="color:red;">如果数据量比较大,第一次启动会失败!(可通过手动建立索引)</li>';
        con += '<li style="color:red;">以下内容,需手动加入计划任务。</li>';
        //主索引
        for (var i = 0; i < rdata['data']['index'].length; i++) {
            var index_t = rdata['data']['index'][i];
            con += '<li>主索引:' + rdata['data']['cmd'] + ' '+ index_t +' --rotate</li>';
        }

        for (var i = 0; i < rdata['data']['delta'].length; i++) {
            var delta_t = rdata['data']['delta'][i];
            var list = delta_t.split(':');
            // console.log(list);
            con += '<li>增量索引:' + rdata['data']['cmd'] + ' '+ list[0] +' --rotate</li>';
            con += '<li>合并索引:' + rdata['data']['cmd'] + ' --merge '+ list[1] + ' ' + list[0] +' --rotate</li>';
        }
        con += '</ul>';

        $(".soft-man-con").html(con);
    });
    
}

