function readme(){
    var readme = '<ul class="help-info-text c7">';
    readme += '<li>在填写好配置信息好后,还要执行下面命令。进行手机号和短信码验证。再重启，即可正常使用</li>';
    readme += '<li>cd /www/server/mdserver-web && source bin/activate && python3 /www/server/tgclient/tgclient.py</li>';
    readme += '<li>https://my.telegram.org/auth</li>';
    readme += '</ul>';
    $('.soft-man-con').html(readme);
}

function appPost(method, args,callback){
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });

    var req_data = {};
    req_data['name'] = 'tgclient';
    req_data['func'] = method;
 
    if (typeof(args) == 'string'){
        req_data['args'] = JSON.stringify(toArrayObject(args));
    } else {
        req_data['args'] = JSON.stringify(args);
    }

    $.post('/plugins/run', req_data, function(data) {
        layer.close(loadT);
        if(typeof(callback) == 'function'){
            callback(data);
        }
    },'json'); 
}

function appPostCallbak(method, args,callback){
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });

    var req_data = {};
    req_data['name'] = 'tgclient';
    req_data['func'] = method;
 
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

function clientConf(){
    appPost('get_client_conf','',function(data){
        var rdata = $.parseJSON(data.data);
        var api_id = 'api_id';
        var api_hash = 'api_hash';
        if(rdata['status']){
            db_data = rdata['data'];

            // api_id, api_hash
            api_id = db_data['api_id'];
            api_hash = db_data['api_hash'];

        }

        var mlist = '';
        mlist += '<p><span>api_id</span><input style="width: 250px;" class="bt-input-text mr5" name="api_id" value="'+api_id+'" type="text"><font>必填写</font></p>';
        mlist += '<p><span>api_hash</span><input style="width: 250px;" class="bt-input-text mr5" name="api_hash" value="'+api_hash+'" type="text"><font>必填写</font></p>';
        var option = '<style>.conf_p p{margin-bottom: 2px}</style>\
            <div class="conf_p" style="margin-bottom:0">\
                ' + mlist + '\
                <div style="margin-top:10px; padding-right:15px" class="text-right">\
                    <button class="btn btn-success btn-sm" onclick="submitBotConf()">保存</button>\
                </div>\
            </div>';
        $(".soft-man-con").html(option);
    });
}

function submitBotConf(){
    var pull_data = {};
    pull_data['api_id'] = base64_encode($('input[name="api_id"]').val());
    pull_data['api_hash'] = base64_encode($('input[name="api_hash"]').val());
    appPost('set_client_conf',pull_data,function(data){
        var rdata = $.parseJSON(data.data);
        layer.msg(rdata['msg'],{icon:rdata['status']?1:2,time:2000,shade: [0.3, '#000']});
    });
}


function botExtList(){
    var body = '<div class="divtable mtb10">\
            <table class="table table-hover" width="100%" cellspacing="0" cellpadding="0" border="0">\
                <thead>\
                    <tr>\
                        <th width="20">脚本</th>\
                        <th width="120">类型</th>\
                        <th width="10">状态</th>\
                    </tr>\
                </thead>\
                <tbody id="ext_list"></tbody>\
            </table>\
            <div class="dataTables_paginate paging_bootstrap pagination">\
                <ul id="ext_list_page" class="page"></ul>\
            </div>\
        </div>';
    $('.soft-man-con').html(body);
    botExtListP(1);
}

function setBotExtStatus(name,status){
    appPost('set_ext_status',{'name':name,'status':status}, function(rdata){
        var rdata = $.parseJSON(rdata.data);
        layer.msg(rdata['msg'],);
        showMsg(rdata['msg'], function(){
            botExtListP(1);
        },{icon:rdata['status']?1:2,shade: [0.3, '#000']},2000);
    });
}

function botExtListP(p=1){
    appPost('client_ext_list',{'p':p}, function(rdata){
        // console.log(rdata);
        var rdata = $.parseJSON(rdata.data);
        // console.log(rdata);
        var tBody = '';

        if (!rdata.status && rdata.data.length == 0 ){
            var tBody = '<tr><td colspan="4"><div style="text-align:center;">无数据</div></td></tr>';
        } else{
            var ldata = rdata.data.data;
            for (var i = 0; i < ldata.length; i++) {
                tBody += '<tr data-name="'+ldata[i]['name']+'">'
                tBody += '<td>'+ldata[i]['name']+'</td>';
                tBody += '<td>'+ldata[i]['tag']+'</td>';

                if (ldata[i]['status'] == 'start'){
                    tBody += '<td><span style="color:#20a53a;cursor: pointer;"  class="ext_status glyphicon glyphicon-play"></span></td>';
                } else{
                    tBody += '<td><span style="color:red;cursor: pointer;" class="ext_status glyphicon glyphicon-pause"></span></td>';
                }
                tBody +='<tr>';
            }
        }
        
        $('#ext_list').html(tBody);
        $('#ext_list_page').html(rdata.data.list);

        $('#ext_list .ext_status').click(function(){
            var name = $(this).parent().parent().data('name');
            var status = 'stop';
            if ($(this).hasClass('glyphicon-pause')){
                status = 'start';
            }
            setBotExtStatus(name,status);
        });
    });
}
