function dPost(method, version, args,callback){
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });

    var req_data = {};
    req_data['name'] = 'docker';
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

function dPostCallbak(method, version, args,callback){
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });

    var req_data = {};
    req_data['name'] = 'docker';
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

function dockerConList(){

    var con = '<div class="safe bgw">\
            <button onclick="" title="" class="btn btn-success btn-sm" type="button" style="margin-right: 5px;">创建容器</button>\
            <span style="float:right">              \
                <button batch="true" style="float: right;display: none;margin-left:10px;" onclick="delDbBatch();" title="删除选中项" class="btn btn-default btn-sm">删除选中</button>\
            </span>\
            <div class="divtable mtb10">\
                <div class="tablescroll">\
                    <table id="con_list" class="table table-hover" width="100%" cellspacing="0" cellpadding="0" border="0" style="border: 0 none;">\
                    <thead><tr>\
                    <th>名称</th>\
                    <th>镜像</th>\
                    <th>创建时间</th>\
                    <th>状态</th>\
                    <th style="text-align:right;">操作</th></tr></thead>\
                    <tbody>\
                    ' + '</tbody></table>\
                </div>\
                <div id="databasePage" class="dataTables_paginate paging_bootstrap page"></div>\
            </div>\
        </div>';

    $(".soft-man-con").html(con);

    dPost('con_list', '', {}, function(rdata){
        // console.log(rdata);
        var rdata = $.parseJSON(rdata.data);
        console.log(rdata);
        if (!rdata.status){
            layer.msg(rdata.msg,{icon:2,time:2000});
            return; 
        }
        

        var list = '';
        var rlist = rdata.data;

        for (var i = 0; i < rlist.length; i++) {

            var status = '<span class="glyphicon glyphicon-pause" style="color:red;font-size:12px"></span>';
            if (rlist[i]['State']['Status'] == 'running'){
                status = '<span class="glyphicon glyphicon-play" style="color:#20a53a;font-size:12px"></span>';
            }


            list += '<tr>';
            list += '<td>'+rlist[i]['Name'].substring(1)+'</td>';
            list += '<td>'+rlist[i]['Config']['Image']+'</td>';
            list += '<td>'+rlist[i]['Created']+'</td>';
            list += '<td>'+status+'</td>';
            list += '<td>'+'操作'+'</td>';
            list += '</tr>';
        }

        $('#con_list tbody').html(list);
    });
    
}

function dockerImageList(){

    var con = '<div class="safe bgw">\
            <button onclick="" title="" class="btn btn-success btn-sm" type="button" style="margin-right: 5px;">获取镜像</button>\
            <div class="divtable mtb10">\
                <div class="tablescroll">\
                    <table id="con_list" class="table table-hover" width="100%" cellspacing="0" cellpadding="0" border="0" style="border: 0 none;">\
                    <thead><tr>\
                    <th>名称</th>\
                    <th>版本</th>\
                    <th>大小</th>\
                    <th>证书</th>\
                    <th>描述</th>\
                    <th style="text-align:right;">操作</th></tr></thead>\
                    <tbody>\
                    ' + '</tbody></table>\
                </div>\
                <div id="databasePage" class="dataTables_paginate paging_bootstrap page"></div>\
            </div>\
        </div>';

    $(".soft-man-con").html(con);

    dPost('image_list', '', {}, function(rdata){
        var rdata = $.parseJSON(rdata.data);
        console.log(rdata);
        if (!rdata.status){
            layer.msg(rdata.msg,{icon:2,time:2000});
            return; 
        }
        
        var list = '';
        var rlist = rdata.data;

        for (var i = 0; i < rlist.length; i++) {

            var tag = rlist[i]['RepoTags'].split(":")[1];

            var license = 'null';
            var desc = 'null';

            if (typeof(rlist[i]['Labels']) == 'null'){
                license = 'free';
            }

            list += '<tr>';
            list += '<td>'+rlist[i]['RepoTags']+'</td>';
            list += '<td>'+tag+'</td>';
            list += '<td>'+rlist[i]['Size']+'</td>';
            list += '<td>'+license+'</td>';
            list += '<td>'+desc+'</td>';
            list += '<td>'+'操作'+'</td>';
            list += '</tr>';
        }

        $('#con_list tbody').html(list);
    });
    
}


function repoList(){

    var con = '<div class="safe bgw">\
            <button onclick="" title="" class="btn btn-success btn-sm" type="button" style="margin-right: 5px;">登录</button>\
            <div class="divtable mtb10">\
                <div class="tablescroll">\
                    <table id="con_list" class="table table-hover" width="100%" cellspacing="0" cellpadding="0" border="0" style="border: 0 none;">\
                    <thead><tr>\
                    <th>名称</th>\
                    <th>版本</th>\
                    <th>大小</th>\
                    <th>证书</th>\
                    <th>描述</th>\
                    <th style="text-align:right;">操作</th></tr></thead>\
                    <tbody>\
                    ' + '</tbody></table>\
                </div>\
                <div id="databasePage" class="dataTables_paginate paging_bootstrap page"></div>\
            </div>\
        </div>';

    $(".soft-man-con").html(con);

    dPost('image_list', '', {}, function(rdata){
        var rdata = $.parseJSON(rdata.data);
        console.log(rdata);
        if (!rdata.status){
            layer.msg(rdata.msg,{icon:2,time:2000});
            return; 
        }
        
        var list = '';
        var rlist = rdata.data;

        for (var i = 0; i < rlist.length; i++) {

            var tag = rlist[i]['RepoTags'].split(":")[1];

            var license = 'null';
            var desc = 'null';

            if (typeof(rlist[i]['Labels']) == 'null'){
                license = 'free';
            }

            list += '<tr>';
            list += '<td>'+rlist[i]['RepoTags']+'</td>';
            list += '<td>'+tag+'</td>';
            list += '<td>'+rlist[i]['Size']+'</td>';
            list += '<td>'+license+'</td>';
            list += '<td>'+desc+'</td>';
            list += '<td>'+'操作'+'</td>';
            list += '</tr>';
        }

        $('#con_list tbody').html(list);
    });
    
}


