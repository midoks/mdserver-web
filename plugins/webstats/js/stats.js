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





function wsClientStatLogRequest(page){

    var args = {};   
    args['page'] = page;
    args['page_size'] = 10;

    args['site'] = $('select[name="site"]').val();
    args['status_code'] = $('select[name="status_code"]').val();

    var query_date = 'today';
    if ($('#time_choose').attr("data-name") != ''){
        query_date = $('#time_choose').attr("data-name");
    } else {
        query_date = $('#search_time button.cur').attr("data-name");
    }
    args['query_date'] = query_date;

    args['tojs'] = 'wsClientStatLogRequest';
    wsPost('get_client_stat_list', '' ,args, function(rdata){
        var rdata = $.parseJSON(rdata.data);
        var list = '';
        var data = rdata.data.data;
        if (data.length > 0){
            for(i in data){
                list += '<tr>';
                list += '<td>' + data[i]['time']+'</td>';
                list += '<td>' + data[i]['android'] +'</td>';
                list += '<td>' + data[i]['iphone'] +'</td>';
                list += '<td>' + data[i]['windows'] +'</td>';
                list += '<td>' + data[i]['chrome'] +'</td>';
                list += '<td>' + data[i]['weixin'] +'</td>';
                list += '<td>' + data[i]['qh360'] +'</td>';
                list += '<td>' + data[i]['edeg'] +'</td>';
                list += '<td>' + data[i]['firefox'] +'</td>';
                list += '<td>' + data[i]['safari'] +'</td>';
                list += '<td>' + data[i]['mac'] +'</td>';
                list += '<td>' + data[i]['msie'] +'</td>';
                list += '<td>' + data[i]['machine'] +'</td>';
                list += '<td>' + data[i]['other'] +'</td>';
                list += '</tr>';
            }
        } else{
             list += '<tr><td colspan="14" style="text-align:center;">客服端列表为空</td></tr>';
        }
        
        var table = '<div class="tablescroll">\
                            <table id="DataBody" class="table table-hover" width="100%" cellspacing="0" cellpadding="0" border="0" style="border: 0 none;">\
                            <thead><tr>\
                            <th>日期</th>\
                            <th>安桌</th>\
                            <th>iOS</th>\
                            <th>Windows</th>\
                            <th>Chrome</th>\
                            <th>微信</th>\
                            <th>360</th>\
                            <th>Edge</th>\
                            <th>火狐</th>\
                            <th>Safari</th>\
                            <th>Mac</th>\
                            <th>IE</th>\
                            <th>机器 <span class="tips" data-toggle="tooltip" data-placement="bottom" title="机器或者脚本应用程序访问，包括：Curl、HeadlessChrome、Bot、Wget、Spider、Crawler、Scrapy、zgrab、Python、java, ab 此类关键词">?</span></th>\
                            <th>其他</th>\</tr></thead>\
                            <tbody>\
                            '+ list +'\
                            </tbody></table>\
                        </div>\
                        <div id="wsPage" class="dataTables_paginate paging_bootstrap page"></div>';
        $('#ws_table').html(table);
        $('#wsPage').html(rdata.data.page);
        $('[data-toggle="tooltip"]').tooltip();


        // 图形化
        var initData = rdata.data.stat_list;
        var sumData = rdata.data.sum_data;
        var colorList = ['#6ec71e','#4885FF'];
        var source_name = {android:'安卓',iphone:'iOS',windows:'Windows',chrome:'Chrome',weixin:'微信',qh360:'360',edeg:'Edge',firefox:'火狐',safari:'Safari',mac:'Mac',linux:'Linux',msie:'IE',metasr:'搜狗',theworld:'世界之窗',tt:'腾讯TT',maxthon:'遨游',opera:'Opera',qq:'QQ浏览器',uc:'UC',pc2345:'2345',other:'其他',machine:'Machine'};
        var lenend2_obj = {};

        var leftEc = echarts.init(document.getElementById('echart_left_total'));
        var rightEc = echarts.init(document.getElementById('echart_right_total'));


        var datas = [
            { value: sumData.pc, name: 'PC客服端' },
            { value: sumData.mobile, name: '移动客服端' },
        ];

        var leftOption = {
            backgroundColor:'#fff',
            title: {
                text: sumData.reqest_total,
                textStyle: {
                    color: '#484848',
                    fontSize: 17
                },
                subtext: '总请求数',
                subtextStyle: {
                    color: '#717171',
                    fontSize: 15
                },
                itemGap: 20,
                left: 'center',
                top: '42%'
            },
            tooltip: {
                trigger: 'item'
            },
            series: [{
                type: 'pie',
                radius: ['45%', '55%'],
                center: ["50%", "50%"],
                clockwise: true,
                avoidLabelOverlap: false,
                hoverOffset: 15,
                itemStyle: {
                    normal: {
                        label: {
                            show: true,
                            position: 'outside',
                            color: '#666',
                            formatter: function(params) {
                                var percent = 0;
                                var total = 0;
                                for (var i = 0; i < datas.length; i++) {
                                    total += datas[i].value;
                                }
                                if(params.name !== '') {
                                    return params.name + '\n' + '\n' +  params.value + '/次';
                                }else {
                                    return '';
                                }
                            },
                        },
                        labelLine: {
                            length: 20,
                            length2: 10
                        },
                        color: function(params) {
                            return colorList[params.dataIndex]
                        }
                    }
                },
                data: datas
            },{
                itemStyle: {
                    normal: {
                        color: '#F5F6FA',
                    }
                },
                type: 'pie',
                hoverAnimation: false,
                radius: ['42%', '58%'],
                center: ["50%", "50%"],
                label: {
                    normal: {
                        show:false,
                    }
                },
                data: [],
                z:-1
            }]
        }
        leftEc.setOption(leftOption);

        var xAxixName = $('#search_time button.cur').text();
        var is_compare  = false;

        var lenend = [];
        var serData = [];
        for(var i = 0;i<initData.length; i++){
            for(var j in initData[i]){
                source_name[j] = source_name[j]?source_name[j]:j
                lenend.push(source_name[j])
                serData.push({
                    name: source_name[j],
                    type: 'bar',
                    label:{
                        normal: { 
                            show: true, 
                            position: 'top', 
                            formatter:function(params){
                                return params.data;
                            }
                        }
                    },
                    barMaxWidth:60,
                    data: [initData[i][j]?initData[i][j]:0]
                })
            }
        }
        for (var i = 0; i < lenend.length; i++) {
            if (i > (is_compare?2:4)) {
                lenend2_obj[lenend[i]] = false;
            } else {
                lenend2_obj[lenend[i]] = true;
            }
        }

        var rightOption = {
            backgroundColor:'#fff',
            tooltip: {
                trigger: 'axis',
                axisPointer: { 
                    type: 'shadow' ,
                    textStyle: {
                        color: '#fff',
                        fontSize: '26'
                    },
                }
            },
            legend: {
                top:'0%',
                data: lenend,
                selected:lenend2_obj,
                textStyle:{
                    fontSize:12,
                    color:'#808080'
                },
                icon:'rect'
            },
            grid: {
                top:60,
                left:60,
                right:0,
                bottom:50
            },
            xAxis: [{
                type: 'category',
                axisLabel:{
                    color:'#4D4D4D',
                    fontSize:14,
                    fontWeight:'bold'
                },
                data: [xAxixName],
            }],
            color:['#4fa8f9', '#6ec71e', '#f56e6a', '#fc8b40', '#818af8', '#31c9d7', '#f35e7a', '#ab7aee',
            '#14d68b', '#cde5ff'],
            yAxis: [{
                type: 'value',
                axisLine: {
                    show: false,
                },
                axisTick: {
                    show: false
                },
                splitNumber:4,   //y轴分割线数量
                axisLabel:{
                    color:'#8C8C8C'
                },
                splitLine:{
                    lineStyle:{
                        type:'dashed'
                    }
                }
            }],
            series: serData
        }


        rightEc.setOption(rightOption);
        
        var oop = lenend.slice(0, (is_compare?3:5));
        rightEc.on('legendselectchanged', function (params) {
            var legend_option = this.getOption(),newAxisName = [];
            $.each(legend_option['xAxis'][0]['data'],function(index,item){
                newAxisName.push(item.replace(/\([^\)]*\)/g,""))
            })
            legend_option['xAxis'][0]['data'] = newAxisName;
            
            var num = 0;
            for(var e in  params.selected){
                if(params.selected.hasOwnProperty(e)){
                    params.selected[e]? num++ : '';
                }
            }
            if(num > (is_compare?3:5)){
                oop.push(params.name)
            }
            if (num > (is_compare?3:5)) {
                var hah = oop.slice(oop.length - (is_compare?4:6), oop.length - (is_compare?3:4))[0] + '';
                legend_option.legend[0].selected[hah] = false;
            }
            if (num < 1){
                legend_option.legend[0].selected[params.name] = true;
            }
            this.setOption(legend_option)
        });
    });
}


function wsClientStat(){
////////////////////////////////////////////////////////////////////////////////////////////////////////
var randstr = getRandomString(10);

var html = '<div>\
                <div style="padding-bottom:10px;">\
                    <span>网站: </span>\
                    <select class="bt-input-text" name="site" style="margin-left:4px;width:100px;">\
                        <option value="unset">未设置</option>\
                    </select>\
                    <span style="margin-left:10px">时间: </span>\
                    <div class="input-group" style="margin-left:10px;width:350px;display: inline-table;vertical-align: top;">\
                        <div id="search_time" class="input-group-btn btn-group-sm">\
                            <button data-name="today" type="button" class="btn btn-default">今日</button>\
                            <button data-name="yesterday" type="button" class="btn btn-default">昨日</button>\
                            <button data-name="l7" type="button" class="btn btn-default">近7天</button>\
                            <button data-name="l30" type="button" class="btn btn-default">近30天</button>\
                        </div>\
                        <span class="last-span"><input data-name="" type="text" id="time_choose" lay-key="1000001_'+randstr+'" class="form-control btn-group-sm" autocomplete="off" placeholder="自定义时间" style="display: inline-block;font-size: 12px;padding: 0 10px;height:30px;width: 200px;"></span>\
                    </div>\
                </div>\
                <div class="echart_container">\
                    <div id="echart_left_total" style="height: 280px; width: 300px;display: inline-block;position: relative;"></div>\
                    <div id="echart_right_total" style="height: 280px; width: 450px;display: inline-block;position: relative;"></div>\
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
            return false;
        }

        $('#search_time button').each(function(){
            $(this).removeClass('cur');
        });

        var timeA  = value.split('-')
        var start = $.trim(timeA[0]+'-'+timeA[1]+'-'+timeA[2])
        var end = $.trim(timeA[3]+'-'+timeA[4]+'-'+timeA[5])
        query_txt = toUnixTime(start + " 00:00:00") + "-"+ toUnixTime(end + " 00:00:00")

        $('#time_choose').attr("data-name",query_txt);
        $('#time_choose').addClass("cur");

        wsClientStatLogRequest(1);
    },
});

$('#search_time button:eq(0)').addClass('cur');
$('#search_time button').click(function(){
    $('#search_time button').each(function(){
        if ($(this).hasClass('cur')){
            $(this).removeClass('cur');
        }
    });
    $('#time_choose').attr("data-name",'');
    $('#time_choose').removeClass("cur");

    $(this).addClass('cur');

    wsClientStatLogRequest(1);
});


$('select[name="status_code"]').change(function(){
    wsClientStatLogRequest(1);
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
    wsClientStatLogRequest(1);

    $('select[name="site"]').change(function(){
        wsClientStatLogRequest(1);
    });
});

////////////////////////////////////////////////////////////////////////////////////////////////////////
}




function wsTableErrorLogRequest(page){

    var args = {};   
    args['page'] = page;
    args['page_size'] = 10;

    args['site'] = $('select[name="site"]').val();
    args['status_code'] = $('select[name="status_code"]').val();

    var query_date = 'today';
    if ($('#time_choose').attr("data-name") != ''){
        query_date = $('#time_choose').attr("data-name");
    } else {
        query_date = $('#search_time button.cur').attr("data-name");
    }
    args['query_date'] = query_date;

    args['tojs'] = 'wsTableErrorLogRequest';
    wsPost('get_logs_error_list', '' ,args, function(rdata){
        var rdata = $.parseJSON(rdata.data);
        var list = '';
        var data = rdata.data.data;
        if (data.length > 0){
            for(i in data){
                list += '<tr>';
                list += '<td>' + getLocalTime(data[i]['time'])+'</td>';
                list += '<td>' + data[i]['domain'] +'</td>';
                list += '<td>' + data[i]['ip'] +'</td>';
                list += '<td>' + toSize(data[i]['body_length']) +'</td>';
                list += '<td>' + data[i]['request_time'] +'ms</td>';
                list += '<td><span class="overflow_hide" style="width:180px;">' + data[i]['uri'] +'</span></td>';
                list += '<td>' + data[i]['status_code']+'/' + data[i]['method'] +'</td>';
                list += '<td><a data-id="'+i+'" href="javascript:;" class="btlink details" title="详情">详情</a></td>';
                list += '</tr>';
            }
        } else{
             list += '<tr><td colspan="8" style="text-align:center;">错误日志为空</td></tr>';
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


        $(".tablescroll .details").click(function(){
            var index = $(this).attr('data-id');
            var res = data[index];
            layer.open({
                type: 1,
                title: "【"+res.domain + "】详情信息",
                area: '600px',
                closeBtn: 2,
                shadeClose: false,
                content: '<div class="pd15 lib-box">\
                    <div style="height:80px;"><table class="table" style="border:#ddd 1px solid; margin-bottom:10px">\
                    <tbody class="site_details_tbody">\
                        <tr><th>时间</th><td>' + getLocalTime(res.time) + '</td><th>真实IP</th><td><span class="overflow_hide detail_ip">' + res.ip + '</span></td><th>客户端端口</th><td>'+(res.client_port>0 && res.client_port != ''?res.client_port:'')+'</td></tr>\
                        <tr><th>类型</th><td>' + res.method + '</td><th>状态</th><td>' + res.status_code + '</td><th>响应大小</th><td>' + toSize(res.body_length) + '</td>\</tr>\
                    </tbody></table></div>\
                    <div><b style="margin-left:10px">协议</b></div>\
                    <div class="lib-con mt10"><div class="divpre">' + res.protocol + '</div></div>\
                    <div><b style="margin-left:10px">URL</b></div>\
                    <div class="lib-con mt10"><div class="divpre">' + $('<div ></div>').text(res.uri).html() + '</div></div>\
                    <div><b style="margin-left:10px">完整IP列表</b></div>\
                    <div class="lib-con pull-left mt10"><div class="divpre" style="max-height: 66px;">' + $('<div ></div>').text(res.ip_list).html() + '</div></div>\
                    <div><b style="margin-left:10px">来路</b></div>\
                    <div class="lib-con mt10"><div class="divpre">' + $('<div ></div>').text(res.referer == null ?'None':res.referer).html() + '</div></div>\
                    <div><b style="margin-left:10px">User-Agent</b></div>\
                    <div class="lib-con mt10"><div class="divpre">' + $('<div ></div>').text(res.user_agent).html() + '</div></div>\
                    <div><b style="margin-left:10px">处理耗时</b></div>\
                    <div class="lib-con mt10"><div class="divpre">' +res.request_time + ' ms</div></div>\
                </div>',
            });
        });
    });
}


function wsSitesErrorLog(){
////////////////////////////////////////////////////////////////////////////////////////////////////////
var randstr = getRandomString(10);

var html = '<div>\
                <div style="padding-bottom:10px;">\
                    <span>网站: </span>\
                    <select class="bt-input-text" name="site" style="margin-left:4px;width:100px;">\
                        <option value="unset">未设置</option>\
                    </select>\
                    <span style="margin-left:10px;">状态码: </span>\
                    <select class="bt-input-text" name="status_code" style="margin-left:4px">\
                        <option value="all">所有</option>\
                        <option value="50x">50x</option>\
                        <option value="40x">40x</option>\
                        <option value="500">500</option>\
                        <option value="501">501</option>\
                        <option value="502">502</option>\
                        <option value="503">503</option>\
                        <option value="403">403</option>\
                        <option value="404">404</option>\
                    </select>\
                    <span style="margin-left:10px">时间: </span>\
                    <div class="input-group" style="margin-left:10px;width:350px;display: inline-table;vertical-align: top;">\
                        <div id="search_time" class="input-group-btn btn-group-sm">\
                            <button data-name="today" type="button" class="btn btn-default">今日</button>\
                            <button data-name="yesterday" type="button" class="btn btn-default">昨日</button>\
                            <button data-name="l7" type="button" class="btn btn-default">近7天</button>\
                            <button data-name="l30" type="button" class="btn btn-default">近30天</button>\
                        </div>\
                        <span class="last-span"><input data-name="" type="text" id="time_choose" lay-key="1000001_'+randstr+'" class="form-control btn-group-sm" autocomplete="off" placeholder="自定义时间" style="display: inline-block;font-size: 12px;padding: 0 10px;height:30px;width: 200px;"></span>\
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
            return false;
        }

        $('#search_time button').each(function(){
            $(this).removeClass('cur');
        });

        var timeA  = value.split('-')
        var start = $.trim(timeA[0]+'-'+timeA[1]+'-'+timeA[2])
        var end = $.trim(timeA[3]+'-'+timeA[4]+'-'+timeA[5])
        query_txt = toUnixTime(start + " 00:00:00") + "-"+ toUnixTime(end + " 00:00:00")

        $('#time_choose').attr("data-name",query_txt);
        $('#time_choose').addClass("cur");

        wsTableErrorLogRequest(1);
    },
});

$('#search_time button:eq(0)').addClass('cur');
$('#search_time button').click(function(){
    $('#search_time button').each(function(){
        if ($(this).hasClass('cur')){
            $(this).removeClass('cur');
        }
    });
    $('#time_choose').attr("data-name",'');
    $('#time_choose').removeClass("cur");

    $(this).addClass('cur');

    wsTableErrorLogRequest(1);
});


$('select[name="status_code"]').change(function(){
    wsTableErrorLogRequest(1);
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
    wsTableErrorLogRequest(1);

    $('select[name="site"]').change(function(){
        wsTableErrorLogRequest(1);
    });
});

////////////////////////////////////////////////////////////////////////////////////////////////////////
}


function wsTableLogRequest(page){

    var args = {};   
    args['page'] = page;
    args['page_size'] = 10;

    args['site'] = $('select[name="site"]').val();
    args['method'] = $('select[name="method"]').val();
    args['status_code'] = $('select[name="status_code"]').val();
    args['spider_type'] = $('select[name="spider_type"]').val();

    var query_date = 'today';
    if ($('#time_choose').attr("data-name") != ''){
        query_date = $('#time_choose').attr("data-name");
    } else {
        query_date = $('#search_time button.cur').attr("data-name");
    }
    args['query_date'] = query_date;
     // console.log("query_date:",query_date);


    var search_uri = $('input[name="search_uri"]').val();
    args['search_uri'] = search_uri;

    args['tojs'] = 'wsTableLogRequest';
    wsPost('get_logs_list', '' ,args, function(rdata){
        var rdata = $.parseJSON(rdata.data);
        var list = '';
        var data = rdata.data.data;
        if (data.length > 0){
            for(i in data){
                list += '<tr>';
                list += '<td>' + getLocalTime(data[i]['time'])+'</td>';
                list += '<td>' + data[i]['domain'] +'</td>';
                list += '<td>' + data[i]['ip'] +'</td>';
                list += '<td>' + toSize(data[i]['body_length']) +'</td>';
                list += '<td>' + data[i]['request_time'] +'ms</td>';
                list += '<td><span class="overflow_hide" style="width:180px;">' + data[i]['uri'] +'</span></td>';
                list += '<td>' + data[i]['status_code']+'/' + data[i]['method'] +'</td>';
                list += '<td><a data-id="'+i+'" href="javascript:;" class="btlink details" title="详情">详情</a></td>';
                list += '</tr>';
            }
        } else{
             list += '<tr><td colspan="8" style="text-align:center;">网站日志为空</td></tr>';
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


        $(".tablescroll .details").click(function(){
            var index = $(this).attr('data-id');
            var res = data[index];
            layer.open({
                type: 1,
                title: "【"+res.domain + "】详情信息",
                area: '600px',
                closeBtn: 2,
                shadeClose: false,
                content: '<div class="pd15 lib-box">\
                    <div style="height:80px;"><table class="table" style="border:#ddd 1px solid; margin-bottom:10px">\
                    <tbody class="site_details_tbody">\
                        <tr><th>时间</th><td>' + getLocalTime(res.time) + '</td><th>真实IP</th><td><span class="overflow_hide detail_ip">' + res.ip + '</span></td><th>客户端端口</th><td>'+(res.client_port>0 && res.client_port != ''?res.client_port:'')+'</td></tr>\
                        <tr><th>类型</th><td>' + res.method + '</td><th>状态</th><td>' + res.status_code + '</td><th>响应大小</th><td>' + toSize(res.body_length) + '</td>\</tr>\
                    </tbody></table></div>\
                    <div><b style="margin-left:10px">协议</b></div>\
                    <div class="lib-con mt10"><div class="divpre">' + res.protocol + '</div></div>\
                    <div><b style="margin-left:10px">URL</b></div>\
                    <div class="lib-con mt10"><div class="divpre">' + $('<div ></div>').text(res.uri).html() + '</div></div>\
                    <div><b style="margin-left:10px">完整IP列表</b></div>\
                    <div class="lib-con pull-left mt10"><div class="divpre" style="max-height: 66px;">' + $('<div ></div>').text(res.ip_list).html() + '</div></div>\
                    <div><b style="margin-left:10px">来路</b></div>\
                    <div class="lib-con mt10"><div class="divpre">' + $('<div ></div>').text(res.referer == null ?'None':res.referer).html() + '</div></div>\
                    <div><b style="margin-left:10px">User-Agent</b></div>\
                    <div class="lib-con mt10"><div class="divpre">' + $('<div ></div>').text(res.user_agent).html() + '</div></div>\
                    <div><b style="margin-left:10px">处理耗时</b></div>\
                    <div class="lib-con mt10"><div class="divpre">' +res.request_time + ' ms</div></div>\
                </div>',
            });
        });
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
                        <div id="search_time" class="input-group-btn btn-group-sm">\
                            <button data-name="today" type="button" class="btn btn-default">今日</button>\
                            <button data-name="yesterday" type="button" class="btn btn-default">昨日</button>\
                            <button data-name="l7" type="button" class="btn btn-default">近7天</button>\
                            <button data-name="l30" type="button" class="btn btn-default">近30天</button>\
                        </div>\
                        <span class="last-span"><input data-name="" type="text" id="time_choose" lay-key="1000001_'+randstr+'" class="form-control btn-group-sm" autocomplete="off" placeholder="自定义时间" style="display: inline-block;font-size: 12px;padding: 0 10px;height:30px;width: 300px;"></span>\
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
                        <input type="text" name="search_uri" class="form-control btn-group-sm" autocomplete="off" placeholder="URI搜索" style="font-size: 12px;padding: 0 10px;height:30px;">\
                        <div class="input-group-btn btn-group-sm">\
                            <button id="logs_search" type="button" class="btn btn-default">搜索</button>\
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
            return false;
        }

        $('#search_time button').each(function(){
            $(this).removeClass('cur');
        });

        var timeA  = value.split('-')
        var start = $.trim(timeA[0]+'-'+timeA[1]+'-'+timeA[2])
        var end = $.trim(timeA[3]+'-'+timeA[4]+'-'+timeA[5])
        query_txt = toUnixTime(start + " 00:00:00") + "-"+ toUnixTime(end + " 00:00:00")

        $('#time_choose').attr("data-name",query_txt);
        $('#time_choose').addClass("cur");

        wsTableLogRequest(1);
    },
});

$('#search_time button:eq(0)').addClass('cur');
$('#search_time button').click(function(){
    $('#search_time button').each(function(){
        if ($(this).hasClass('cur')){
            $(this).removeClass('cur');
        }
    });
    $('#time_choose').attr("data-name",'');
    $('#time_choose').removeClass("cur");

    $(this).addClass('cur');

    wsTableLogRequest(1);
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

$('#logs_search').click(function(){
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










