function str2Obj(str){
    var data = {};
    kv = str.split('&');
    for(i in kv){
        v = kv[i].split('=');
        data[v[0]] = v[1];
    }
    return data;
}

function wsPost(method, version, args,callback){
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });

    var req_data = {};
    req_data['name'] = 'webstats';
    req_data['func'] = method;
    req_data['version'] = version;
 
    if (typeof(args) == 'string'){
        req_data['args'] = JSON.stringify(str2Obj(args));
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

function wsPostCallbak(method, version, args,callback){
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });

    var req_data = {};
    req_data['name'] = 'webstats';
    req_data['func'] = method;
    args['version'] = version;
 
    if (typeof(args) == 'string'){
        req_data['args'] = JSON.stringify(str2Obj(args));
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


function wsOverview(){
    var args = {};   
    args['page'] = 1;
    args['page_size'] = 10;
    args['site'] = 'unset';
    args['tojs'] = 'wsOverview';
    wsPost('get_logs_list', '' ,args, function(rdata){
        var rdata = $.parseJSON(rdata.data);
        console.log(rdata);
        var list = '';
        var data = rdata.data.data;
        for(i in data){
            list += '<tr>';
            list += '<td>' + data[i]['time']+'</td>';
            list += '<td>' + data[i]['domain'] +'</td>';
            list += '<td>' + data[i]['ip'] +'</td>';
            list += '<td>' + data[i]['body_length'] +'</td>';
            list += '<td>' + data[i]['request_time'] +'ms</td>';
            list += '<td>' + data[i]['uri'] +'</td>';
            list += '<td>' + data[i]['status_code']+'/' + data[i]['method'] +'</td>';
            list += '<td><a href="javascript:;" class="btlink" onclick="openPhpmyadmin()" title="详情">详情</a></td>';
            list += '</tr>';
        }
        var table = '<div class="divtable mtb10">\
                        <div class="tablescroll">\
                            <table id="DataBody" class="table table-hover" width="100%" cellspacing="0" cellpadding="0" border="0" style="border: 0 none;">\
                            <thead><tr>\
                            <th>时间</th>\
                            <th>域名</th>\
                            <th>IP</th>\
                            <th>响应</th>\
                            <th>耗时</th>\
                            <th>URL</th>\
                            <th>状态/类型</th>\
                            <th style="text-align:right;">操作</th></tr></thead>\
                            <tbody>\
                            '+ list +'\
                            </tbody></table>\
                        </div>\
                        <div id="wsPage" class="dataTables_paginate paging_bootstrap page"></div>\
                    </div>';

        var html = '<div>\
                        <div style="padding-bottom:10px;">\
                            <span>网站: </span>\
                            <select class="bt-input-text" name="" style="margin-left:4px">\
                                <option value="0">请选择</option>\
                                <option value="1">1-2GB</option>\
                            </select>\
                            <span style="margin-left:10px">时间: </span>\
                            <div class="input-group" style="width:510px;float:right;">\
                                <div class="input-group-btn btn-group-sm">\
                                    <button type="button" class="btn btn-default gt">今日</button>\
                                    <button type="button" class="btn btn-default gt">昨日</button>\
                                    <button type="button" class="btn btn-default gt">近7天</button>\
                                    <button type="button" class="btn btn-default gt">近30天</button>\
                                </div>\
                                <input type="text" class="form-control btn-group-sm" autocomplete="off" placeholder="自定义时间" style="font-size: 12px;padding: 0 10px;height:30px;width: 150px; background-position: 10px center;">\
                            </div>\
                        </div>\
                        <div style="padding-bottom:10px;">\
                            <span>请求类型: </span>\
                            <select class="bt-input-text" name="req_type" style="margin-left:4px">\
                                <option value="0">所有</option>\
                                <option value="GET">GET</option>\
                                <option value="POST">POST</option>\
                                <option value="HEAD">HEAD</option>\
                                <option value="PUT">PUT</option>\
                                <option value="DELETE">DELETE</option>\
                            </select>\
                            <span style="margin-left:10px;">状态码: </span>\
                            <select class="bt-input-text" name="code_type" style="margin-left:4px">\
                                <option value="0">所有</option>\
                                <option value="500">500</option>\
                                <option value="502">502</option>\
                                <option value="503">503</option>\
                                <option value="404">404</option>\
                                <option value="200">200</option>\
                            </select>\
                            <span style="margin-left:10px;">蜘蛛过滤: </span>\
                            <select class="bt-input-text" name="spider_type" style="margin-left:4px">\
                                <option value="0">不过滤</option>\
                                <option value="baidu">百度</option>\
                            </select>\
                            <span style="margin-left:10px;">URL过滤: </span>\
                            <div class="input-group" style="width:210px;float:right;">\
                                <input type="text" class="form-control btn-group-sm" autocomplete="off" placeholder="URI搜索" style="font-size: 12px;padding: 0 10px;height:30px;">\
                                <div class="input-group-btn btn-group-sm">\
                                    <button type="button" class="btn btn-default">搜索</button>\
                                </div>\
                            </div>\
                        </div>\
                        '+table+'\
                    </div>';
        $(".soft-man-con").html(html);
        $('#wsPage').html(rdata.data.page);
    });
}



function wsSitesErrorLog(){
    var args = {};   
    args['page'] = 1;
    args['page_size'] = 10;
    args['site'] = 'unset';
    args['tojs'] = 'wsSitesErrorLog';
    wsPost('get_logs_list', '' ,args, function(rdata){
        var rdata = $.parseJSON(rdata.data);
        console.log(rdata);
        var list = '';
        var data = rdata.data.data;
        for(i in data){
            list += '<tr>';
            list += '<td>' + data[i]['time']+'</td>';
            list += '<td>' + data[i]['domain'] +'</td>';
            list += '<td>' + data[i]['ip'] +'</td>';
            list += '<td>' + data[i]['body_length'] +'</td>';
            list += '<td>' + data[i]['request_time'] +'ms</td>';
            list += '<td>' + data[i]['uri'] +'</td>';
            list += '<td>' + data[i]['status_code']+'/' + data[i]['method'] +'</td>';
            list += '<td><a href="javascript:;" class="btlink" onclick="openPhpmyadmin()" title="详情">详情</a></td>';
            list += '</tr>';
        }
        var table = '<div class="divtable mtb10">\
                        <div class="tablescroll">\
                            <table id="DataBody" class="table table-hover" width="100%" cellspacing="0" cellpadding="0" border="0" style="border: 0 none;">\
                            <thead><tr>\
                            <th>时间</th>\
                            <th>域名</th>\
                            <th>IP</th>\
                            <th>响应</th>\
                            <th>耗时</th>\
                            <th>URL</th>\
                            <th>状态/类型</th>\
                            <th style="text-align:right;">操作</th></tr></thead>\
                            <tbody>\
                            '+ list +'\
                            </tbody></table>\
                        </div>\
                        <div id="wsPage" class="dataTables_paginate paging_bootstrap page"></div>\
                    </div>';

        var html = '<div>\
                        <div style="padding-bottom:10px;">\
                            <span>网站: </span>\
                            <select class="bt-input-text" name="" style="margin-left:4px">\
                                <option value="0">请选择</option>\
                                <option value="1">1-2GB</option>\
                            </select>\
                            <span style="margin-left:10px">时间: </span>\
                            <div class="input-group" style="width:510px;float:right;">\
                                <div class="input-group-btn btn-group-sm">\
                                    <button type="button" class="btn btn-default gt">今日</button>\
                                    <button type="button" class="btn btn-default gt">昨日</button>\
                                    <button type="button" class="btn btn-default gt">近7天</button>\
                                    <button type="button" class="btn btn-default gt">近30天</button>\
                                </div>\
                                <input id="time_choose" type="text" class="form-control btn-group-sm" autocomplete="off" placeholder="自定义时间" style="font-size: 12px;padding: 0 10px;height:30px;width: 150px; background-position: 10px center;">\
                            </div>\
                        </div>\
                        <div style="padding-bottom:10px;">\
                            <span>请求类型: </span>\
                            <select class="bt-input-text" name="req_type" style="margin-left:4px">\
                                <option value="0">所有</option>\
                                <option value="GET">GET</option>\
                                <option value="POST">POST</option>\
                                <option value="HEAD">HEAD</option>\
                                <option value="PUT">PUT</option>\
                                <option value="DELETE">DELETE</option>\
                            </select>\
                            <span style="margin-left:10px;">状态码: </span>\
                            <select class="bt-input-text" name="code_type" style="margin-left:4px">\
                                <option value="0">所有</option>\
                                <option value="500">500</option>\
                                <option value="502">502</option>\
                                <option value="503">503</option>\
                                <option value="404">404</option>\
                                <option value="200">200</option>\
                            </select>\
                            <span style="margin-left:10px;">蜘蛛过滤: </span>\
                            <select class="bt-input-text" name="spider_type" style="margin-left:4px">\
                                <option value="0">不过滤</option>\
                                <option value="baidu">百度</option>\
                            </select>\
                            <span style="margin-left:10px;">URL过滤: </span>\
                            <div class="input-group" style="width:210px;float:right;">\
                                <input type="text" class="form-control btn-group-sm" autocomplete="off" placeholder="URI搜索" style="font-size: 12px;padding: 0 10px;height:30px;">\
                                <div class="input-group-btn btn-group-sm">\
                                    <button type="button" class="btn btn-default">搜索</button>\
                                </div>\
                            </div>\
                        </div>\
                        '+table+'\
                    </div>';
        $(".soft-man-con").html(html);
        $('#wsPage').html(rdata.data.page);
    });
}


function wsTableLogRequest(page){

    // console.log("wsTableRequest:",$('select[name="site"]').val());
    var args = {};   
    args['page'] = page;
    args['page_size'] = 10;

    args['site'] = $('select[name="site"]').val();
    args['method'] = $('select[name="method"]').val();
    args['status_code'] = $('select[name="status_code"]').val();
    args['spider_type'] = $('select[name="spider_type"]').val();
    args['tojs'] = 'wsTableLogRequest';
    wsPost('get_logs_list', '' ,args, function(rdata){
        var rdata = $.parseJSON(rdata.data);
        var list = '';
        var data = rdata.data.data;
        for(i in data){
            list += '<tr>';
            list += '<td>' + getLocalTime(data[i]['time'])+'</td>';
            list += '<td>' + data[i]['domain'] +'</td>';
            list += '<td>' + data[i]['ip'] +'</td>';
            list += '<td>' + toSize(data[i]['body_length']) +'</td>';
            list += '<td>' + data[i]['request_time'] +'ms</td>';
            list += '<td><span class="overflow_hide" style="width:180px;">' + data[i]['uri'] +'</span></td>';
            list += '<td>' + data[i]['status_code']+'/' + data[i]['method'] +'</td>';
            list += '<td><a href="javascript:;" class="btlink" onclick="openPhpmyadmin()" title="详情">详情</a></td>';
            list += '</tr>';
        }
        var table = '<div class="tablescroll">\
                            <table id="DataBody" class="table table-hover" width="100%" cellspacing="0" cellpadding="0" border="0" style="border: 0 none;">\
                            <thead><tr>\
                            <th>时间</th>\
                            <th>域名</th>\
                            <th>IP</th>\
                            <th>响应</th>\
                            <th>耗时</th>\
                            <th >URL</th>\
                            <th>状态/类型</th>\
                            <th style="text-align:right;">操作</th></tr></thead>\
                            <tbody>\
                            '+ list +'\
                            </tbody></table>\
                        </div>\
                        <div id="wsPage" class="dataTables_paginate paging_bootstrap page"></div>';
        $('#ws_table').html(table);
        $('#wsPage').html(rdata.data.page);
    });
}

function wsSitesLog(){
////////////////////////////////////////////////////////////////////////////////////////////////////////
var randstr = getRandomString(10);

var html = '<div>\
                <div style="padding-bottom:10px;">\
                    <span>网站: </span>\
                    <select class="bt-input-text" name="site" style="margin-left:4px;width:100px;">\
                        <option value="unset">未设置</option>\
                    </select>\
                    <span style="margin-left:10px">时间: </span>\
                    <div class="input-group" style="margin-left:10px;width:550px;display: inline-table;vertical-align: top;">\
                        <div class="input-group-btn btn-group-sm">\
                            <button type="button" class="btn btn-default">今日</button>\
                            <button type="button" class="btn btn-default">昨日</button>\
                            <button type="button" class="btn btn-default">近7天</button>\
                            <button type="button" class="btn btn-default">近30天</button>\
                        </div>\
                        <span class="last-span"><input type="text" id="time_choose" lay-key="1000001_'+randstr+'" class="form-control btn-group-sm" autocomplete="off" placeholder="自定义时间" style="display: inline-block;font-size: 12px;padding: 0 10px;height:30px;width: 300px;"></span>\
                    </div>\
                </div>\
                <div style="padding-bottom:10px;">\
                    <span>请求类型: </span>\
                    <select class="bt-input-text" name="method" style="margin-left:4px">\
                        <option value="all">所有</option>\
                        <option value="GET">GET</option>\
                        <option value="POST">POST</option>\
                        <option value="HEAD">HEAD</option>\
                        <option value="PUT">PUT</option>\
                        <option value="DELETE">DELETE</option>\
                    </select>\
                    <span style="margin-left:10px;">状态码: </span>\
                    <select class="bt-input-text" name="status_code" style="margin-left:4px">\
                        <option value="all">所有</option>\
                        <option value="500">500</option>\
                        <option value="502">502</option>\
                        <option value="503">503</option>\
                        <option value="404">404</option>\
                        <option value="200">200</option>\
                    </select>\
                    <span style="margin-left:10px;">蜘蛛过滤: </span>\
                    <select class="bt-input-text" name="spider_type" style="margin-left:4px">\
                        <option value="normal">不过滤</option>\
                        <option value="only_spider">仅显示蜘蛛</option>\
                        <option value="no_spider">不显示蜘蛛</option>\
                        <option value="1">百度</option>\
                        <option value="2">必应</option>\
                        <option value="3">奇虎360</option>\
                        <option value="4">Google</option>\
                        <option value="5">头条</option>\
                        <option value="6">搜狗</option>\
                        <option value="7">有道</option>\
                        <option value="8">搜搜</option>\
                        <option value="9">Dnspod</option>\
                        <option value="10">Yandex</option>\
                        <option value="12">神马</option>\
                        <option value="12">其他</option>\
                    </select>\
                    <span style="margin-left:10px;">URL过滤: </span>\
                    <div class="input-group" style="width:210px;display:inline-flex;">\
                        <input type="text" class="form-control btn-group-sm" autocomplete="off" placeholder="URI搜索" style="font-size: 12px;padding: 0 10px;height:30px;">\
                        <div class="input-group-btn btn-group-sm">\
                            <button type="button" class="btn btn-default">搜索</button>\
                        </div>\
                    </div>\
                </div>\
                <div class="divtable mtb10" id="ws_table"></div>\
            </div>';
$(".soft-man-con").html(html);

//日期范围
laydate.render({
    elem: '#time_choose',
    value:'',
    range:true,
    done:function(value, startDate, endDate){
        if(!value){
            $('#time_choose').remove("cur");
            return false;
        }

        var timeA  = value.split('-')
        var start = $.trim(timeA[0]+'-'+timeA[1]+'-'+timeA[2])
        var end = $.trim(timeA[3]+'-'+timeA[4]+'-'+timeA[5])
        query_txt = toUnixTime(start + " 00:00:00") + "-"+ toUnixTime(end + " 00:00:00")
        console.log(query_txt)
        $('#time_choose').addClass("cur");
    },
});

$('select[name="method"]').change(function(){
    wsTableLogRequest(1);
});

$('select[name="status_code"]').change(function(){
    wsTableLogRequest(1);
});

$('select[name="spider_type"]').change(function(){
    wsTableLogRequest(1);
});

wsPost('get_default_site','',{},function(rdata){
    $('select[name="site"]').html('');

    var rdata = $.parseJSON(rdata.data);
    var rdata = rdata.data;
    var default_site = rdata["default"];
    var select = '';
    for (var i = 0; i < rdata["list"].length; i++) {
        if (default_site ==  rdata["list"][i]){
            select += '<option value="'+rdata["list"][i]+'" selected>'+rdata["list"][i]+'</option>';
        } else{
            select += '<option value="'+rdata["list"][i]+'">'+rdata["list"][i]+'</option>';
        }
    }
    $('select[name="site"]').html(select);
    wsTableLogRequest(1);

    $('select[name="site"]').change(function(){
        wsTableLogRequest(1);
    });
});




////////////////////////////////////////////////////////////////////////////////////////////////////////
}










