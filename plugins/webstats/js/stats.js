function str2Obj(str){
    var data = {};
    kv = str.split('&');
    for(i in kv){
        v = kv[i].split('=');
        data[v[0]] = v[1];
    }
    return data;
}

function wsOriginPost(method, version, args, callback){

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



function wsPost(method, version, args,callback){
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });
    wsOriginPost(method, version, args,function(data){
        layer.close(loadT);
        callback(data);
    });
}



function wsPostCallbak(method, version, args,callback){
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });

    var req_data = {};
    req_data['name'] = 'webstats';
    req_data['script']='webstats_index';
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


function toSecond(val){
    if (val>=1000){
        val = (val / 1000).toFixed()+"s";
        return val;
    } 
    return val + "ms";
}


function makeHoursData(data, type="ip"){
    var list = [];
    var rlist = [];
    for (var i = 0; i < 24; i++) {
        if (i<10){
            list.push("0"+i)
        } else {
            list.push(i+"")
        }
        rlist.push(i+"")
    }

    var rdata = {};
    rdata['key'] = rlist;

    var tmpdata = {};
    for (var i = 0; i < data.length; i++) {
        var tk = data[i]['time'];

        var v =  data[i];
        if (type=='length'){
            v['length'] = (v['length']/1024).toFixed();
        }
        tmpdata[tk] = v;
    }

    var val = [];
    for (var i = 0; i < list.length; i++) {
        var tk = list[i];

        if (tmpdata[tk]){
            val.push(tmpdata[tk][type]);
        }else{
            val.push(0);
        }
    }

    rdata['value'] = val;
    // console.log(rdata);
    return rdata
}

function makeDayData(data, type="ip") {
    var rdata = {};

    var rdata_key = [];
    var rdata_val = [];

    for (var i = 0; i < data.length; i++) {
        var tk = data[i]['time'];

        rdata_key.push(tk);

        var v = data[i][type];
        if (type=='length'){
            v = (v/1024).toFixed();
        }
        rdata_val.push(v)
    }

    rdata['key'] = rdata_key;
    rdata['value'] = rdata_val;

    return rdata
}

function getTime() {
    var now = new Date();
    var hour = now.getHours();
    var minute = now.getMinutes();
    var second = now.getSeconds();
    if (minute < 10) {
        minute = "0" + minute;
    }
    if (second < 10) {
        second = "0" + second;
    }
    var nowdate = hour + ":" + minute + ":" + second;
    return nowdate;
}

var ovTimer = null;
function wsOverviewRequest(page){
    clearInterval(ovTimer);

    var args = {};

    args['site'] = $('select[name="site"]').val();

    var query_date = 'today';
    if ($('#time_choose').attr("data-name") != ''){
        query_date = $('#time_choose').attr("data-name");
    } else {
        query_date = $('#search_time button.cur').attr("data-name");
    }
    args['query_date'] = query_date;
    args['order'] = $('#time_order button.cur').attr('data-name');

    var select_option = $('.indicators-container input:checked').parent().attr('data-name');

    // console.log($('.indicators-container input:checked').parent().find('span').text());
    // console.log(select_option);

    wsPost('get_overview_list', '' ,args, function(rdata){
        var rdata = $.parseJSON(rdata.data);
        var list = '';
        var data = rdata.data.data;
        var statData = rdata.data.stat_list;

        // console.log(statData, data);

        var stat_pv = statData['pv'] == null?0:statData['pv'];
        var stat_uv = statData['uv'] == null?0:statData['uv'];
        var stat_ip = statData['ip'] == null?0:statData['ip'];
        var stat_length = statData['length'] == null?0:statData['length'];
        var stat_req = statData['req'] == null?0:statData['req'];

        $('.overview_list .overview_box:eq(0) .ov_num').text(stat_pv);
        $('.overview_list .overview_box:eq(1) .ov_num').text(stat_uv);
        $('.overview_list .overview_box:eq(2) .ov_num').text(stat_ip);
        $('.overview_list .overview_box:eq(3) .ov_num').text(toSize(stat_length));
        $('.overview_list .overview_box:eq(4) .ov_num').text(stat_req);

        var list = [];
        for (var i = 0; i < data.length; i++) {
            list.push(data[i][select_option]);
        }

        // console.log("list",list);
        var chat = {};
        var is_compare = false;

        var tmpChatData = {
            "key":[],
            "value":[]
        }

        if (select_option == 'realtime_traffic' || select_option == 'realtime_request'){
        } else {
            if (args['order'] == 'hour'){
                tmpChatData = makeHoursData(data, select_option);
            } else {
                tmpChatData = makeDayData(data, select_option);
            }
        }


        chat['yAxis'] = [{
            type: 'value',
            splitNumber: 5,
            axisLabel: {
                textStyle: {
                    color: '#a8aab0',
                    fontStyle: 'normal',
                    fontFamily: '微软雅黑',
                    fontSize: 12,
                },
            },
            axisLine:{
                show: false
            },
            axisTick:{
                show: false
            },
            splitLine: {
                show: true,
                lineStyle: {
                    color: '#E5E9ED'
                }
            }
        }];

        chat['tooltip'] = {
            show:true,
            trigger: 'axis',
            backgroundColor: 'rgba(255,255,255,0.8)',
            axisPointer: { // 坐标轴指示器，坐标轴触发有效
                type: 'line', // 默认为直线，可选为：'line' | 'shadow'
                lineStyle: {
                    color: 'rgba(150,150,150,0.2)'
                }
            },
            textStyle: {
                color: '#666',
                fontSize: '14px',
            },
            extraCssText: 'width:220px;height:'+(is_compare?'30%':'22%')+';padding:0;box-shadow: 0 0 3px rgba(0, 0, 0, 0.3);"',
            formatter: function (params) {
                var htmlStr = "";
                for (var i = 0; i < params.length; i++) {
                    var tem = params[i].name;
                    var val = params[i].value;
                    if(args['order'] == 'hour'){
                        if (tem.indexOf('/') < 0) {
                            tem > 9 ? tem = tem + ":00 - " + tem + ":59" : tem = "0" + tem + ":00 - " +
                                "0" + tem + ":59";
                        }
                        val > 0 ? val = val : val = '--'
                    }
                    
                    htmlStr +=
                        '<div style="height:26px;line-height:26px;overflow:hidden;padding:6px 8px;">' +
                        '<span style="float:left;max-width:160px;overflow:hidden;text-overflow: ellipsis;white-space: nowrap;">' +
                        '<span style="margin-right:5px;display:inline-block;width:10px;height:10px;border-radius:5px;background-color:' +
                        params[i].color + ';"></span>' + params[i].seriesName + '</span>' +
                        '<span style="float:right">' + val + '</span>' + '</div>'
                }
                var res ='<div><div style="height:40px;line-height:40px;padding:0 8px;background:rgba(237,233,233,0.4)">' +
                    tem + '<span style="float:right;">' + (is_compare?trend_name:'') +
                    '</span>' + htmlStr + '</div></div>'
                return res;
            }
        }

        var legendName = $('.indicators-container input:checked').parent().find('span').text()
        chat['legendData'] = [legendName];

        var statEc = echarts.init(document.getElementById('total_num_echart'));
        var option = {
            tooltip:chat['tooltip'],
            backgroundColor:'#fff',
            legend:{
                data:chat['legendData'],
                left:'center',
                top:'94%',
            },
            grid: {
                bottom: '9%',
                containLabel: true,
                x: 20,
                y: 20,
                x2: 20,
                y2: 20
            },
            xAxis: {
                type: 'category',
                boundaryGap: false,
                boundaryGap: false,
                axisTick: {
                    alignWithLabel: true
                },
                data: tmpChatData["key"],
            },
            yAxis: chat['yAxis'],
            graphic:[{
                type: 'group',
                right: 330,
                top: 0,
                z: 100,
                children: [{
                    type: 'text',
                    left: 'center',
                    top: 'center',
                    z: 100,
                    style: {
                        fill: '#ccc',
                        text: args['site'],
                        font: '16px Arial'
                    }
                }]
            }],
            series: [
            {
                name:legendName,
                data: tmpChatData["value"],
                type: 'line',
                smooth: true, 
                itemStyle: {
                    normal: {
                        color:'#3A84FF',
                        lineStyle: {
                            color: "#3A84FF",
                            width:1,
                        },
                        areaStyle: { 
                            color: new echarts.graphic.LinearGradient(0, 1, 0, 0, [{
                                offset: 0,
                                color: 'rgba(58,132,255,0)'
                            }, {
                                offset: 1,
                                color: 'rgba(58,132,255,0.35)'
                            }]),
                        }
                    }
                },
                areaStyle: {}
            }
          ]
        };

        statEc.setOption(option);

        if (select_option == 'realtime_traffic' || select_option == 'realtime_request'){
            
            var xData = [];
            var yData = [];
            ovTimer = setInterval(function(){
                var select_option = $('.indicators-container input:checked').parent().attr('data-name');
                if (select_option != "realtime_traffic" && select_option != 'realtime_request' ){
                    clearInterval(ovTimer);
                    // console.log("get_logs_realtime_info over:"+select_option);
                    return;
                }

                var second = $('#check_realtime_second').val();

                wsOriginPost("get_logs_realtime_info",'',{"site":args["site"], "type":select_option,'second':second} , function(rdata){    
                    
                    var rdata = $.parseJSON(rdata.data);

                    var realtime_traffic = rdata.data['realtime_traffic'];
                    var realtime_request = rdata.data['realtime_request'];

                    realtime_traffic_calc = toSize(realtime_traffic);


                    $('.overview_list .overview_box:eq(5) .ov_num').text(realtime_traffic_calc);
                    $('.overview_list .overview_box:eq(6) .ov_num').text(realtime_request);

                    
                    var realtime_name = select_option == 'realtime_traffic' ? '实时流量':'每秒请求';
                    var val = realtime_request;
                    if (select_option == 'realtime_traffic'){
                        val = realtime_traffic_calc.split(' ')[0];
                        realtime_name = realtime_traffic_calc;
                    }

                    xData.push(getTime());
                    yData.push(val);

                    if (xData.length > 20){
                        xData.shift();
                        yData.shift();
                    }

                    statEc.setOption({
                        xAxis: {
                            data: xData
                        },
                        series: [{
                            name: realtime_name,
                            data: yData
                        }]
                    });
                });
            },2000);
        }
    });
}


function wsOverview(){
////////////////////////////////////////////////////////////////////////////////////////////////////////
var randstr = getRandomString(10);

var html = '<div>\
                <div style="padding-bottom:10px;">\
                    <span>网站: </span>\
                    <select class="bt-input-text" name="site" style="margin-left:4px;width:100px;">\
                        <option value="unset">未设置</option>\
                    </select>\
                    <span style="margin-left:10px">时间: </span>\
                    <div class="input-group" style="margin-left:10px;width:300px;display: inline-table;vertical-align: top;">\
                        <div id="search_time" class="input-group-btn btn-group-sm">\
                            <button data-name="today" type="button" class="btn btn-default">今日</button>\
                            <button data-name="yesterday" type="button" class="btn btn-default">昨日</button>\
                            <button data-name="l7" type="button" class="btn btn-default">近7天</button>\
                            <button data-name="l30" type="button" class="btn btn-default">近30天</button>\
                        </div>\
                        <span class="last-span"><input data-name="" type="text" id="time_choose" lay-key="1000001_'+randstr+'" class="form-control btn-group-sm" autocomplete="off" placeholder="自定义时间" style="display: inline-block;font-size: 12px;padding: 0 10px;height:30px;width: 155px;"></span>\
                    </div>\
                    <span style="margin-left:10px">时段: </span>\
                    <div class="input-group" style="width:100px;margin-left:10px;display: inline-table;vertical-align: top;">\
                        <div id="time_order" class="input-group-btn btn-group-sm">\
                            <button data-name="hour" type="button" class="btn btn-default">按时</button>\
                            <button data-name="day" type="button" class="btn btn-default">按天</button>\
                        </div>\
                    </div>\
                    <div class="input-group" style="width:30px;margin-left:10px;display: inline-table;vertical-align: top;">\
                        <div class="input-group-btn btn-group-sm">\
                            <button id="ov_refresh" data-name="refresh" type="button" class="btn btn-default">刷新</button>\
                        </div>\
                    </div>\
                </div>\
                <!-- stat --->\
                <div class="overview_list" style="padding-top:10px;">\
                    <div class="overview_box">\
                        <p class="ov_title">浏览量(PV)<i class="tips" data-toggle="tooltip" data-placement="top" title="用户每次打开网站页面被记录1次。用户多次打开同一页面，访问量值累计多次。此指标衡量网站访问量情况。">?</i></p>\
                        <p class="ov_num">0</p>\
                    </div>\
                    <div class="overview_box">\
                        <p class="ov_title">访客量(UV)<i class="tips" data-toggle="tooltip" data-placement="top" title="访问您网站的上网电脑数量（以cookie为依据），此指标衡量独立访客数量情况。">?</i></p>\
                        <p class="ov_num">0</p>\
                    </div>\
                    <div class="overview_box">\
                        <p class="ov_title">IP数<i class="tips" data-toggle="tooltip" data-placement="top" title="当前时间段内您网站的独立访问ip数。">?</i></p>\
                        <p class="ov_num">0</p>\
                    </div>\
                    <div class="overview_box">\
                        <p class="ov_title">流量<i class="tips" data-toggle="tooltip" data-placement="top" title="当前时间段内您网站的总响应流量大小。包括已排除的请求。">?</i></p>\
                        <p class="ov_num">0</p>\
                    </div>\
                    <div class="overview_box">\
                        <p class="ov_title">请求<i class="tips" data-toggle="tooltip" data-placement="top" title="当前时间段内您网站的总请求数量。包括已排除的请求。">?</i></p>\
                        <p class="ov_num">0</p>\
                    </div>\
                    <div class="overview_box">\
                        <p class="ov_title">实时流量<i class="tips" data-toggle="tooltip" data-placement="top" title="当前X秒内您网站的实时流量大小。包括已排除的请求。">?</i></p>\
                        <p class="ov_num">0</p>\
                    </div>\
                    <div class="overview_box">\
                        <p class="ov_title"><span id="ov_title_req_second">每秒请求<span><i class="tips" data-toggle="tooltip" data-placement="top" title="当前1-10秒内您网站的实时请求数量。包括已排除的请求。">?</i></p>\
                        <p class="ov_num">0</p>\
                    </div>\
                </div>\
                <div class="indicators">\
                    <div class="indicators-container">\
                        <span>趋势指标: </span>\
                        <div class="indicators-label" bt-event-click="indicatorsType" data-name="pv">\
                            <input type="radio" id="check_pv" name="check_pv" checked="">\
                            <span class="check_pv" style="font-weight:normal">浏览量(PV)</span>\
                        </div>\
                        <div class="indicators-label" bt-event-click="indicatorsType" data-name="uv">\
                            <input type="radio" id="check_uv" name="check_uv">\
                            <span class="check_uv" style="font-weight:normal">访客量(UV)</span>\
                        </div>\
                        <div class="indicators-label" bt-event-click="indicatorsType" data-name="ip">\
                            <input type="radio" id="check_ip" name="check_ip">\
                            <span class="check_ip" style="font-weight:normal">IP数</span>\
                        </div>\
                        <div class="indicators-label" bt-event-click="indicatorsType" data-name="length">\
                            <input type="radio" id="check_length" name="check_length">\
                            <span class="check_length" style="font-weight:normal">流量(KB)</span>\
                        </div>\
                        <div class="indicators-label" bt-event-click="indicatorsType" data-name="req">\
                            <input type="radio" id="check_req" name="check_req">\
                            <span class="check_req" style="font-weight:normal">请求</span>\
                        </div>\
                        <div class="indicators-label" bt-event-click="indicatorsType" data-name="realtime_traffic">\
                            <input type="radio" id="check_realtime_traffic" name="check_realtime_traffic"> \
                            <span class="check_realtime_traffic" style="font-weight:normal">实时流量</span>\
                        </div>\
                        <div class="indicators-label" bt-event-click="indicatorsType" data-name="realtime_request">\
                            <input type="radio" id="check_realtime_request" name="check_realtime_request">\
                            <span class="check_realtime_request" style="font-weight:normal">每X秒请求</span>\
                        </div>\
                        <div class="indicators-label" bt-event-click="indicatorsType">\
                            <input class="bt-input-text mr5" type="number" id="check_realtime_second" name="check_realtime_second" value="1" style="width:40px;outline:none;height:23px;border-radius:3px;">\
                            <span style="font-weight:normal">秒</span>\
                        </div>\
                    </div>\
                </div>\
                <div class="total_num_echart" id="total_num_echart" style="height:330px;"></div>\
            </div>';
$(".soft-man-con").html(html);
$('[data-toggle="tooltip"]').tooltip();
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

        wsOverviewRequest(1);
    },
});

$('#ov_refresh').click(function(){
    wsOverviewRequest(1);
});

$('#time_order button:eq(0)').addClass('cur');
$('#time_order button').click(function(){
    $('#time_order button').each(function(){
        if ($(this).hasClass('cur')){
            $(this).removeClass('cur');
        }
    });
    $(this).addClass('cur');
    wsOverviewRequest(1);
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

    wsOverviewRequest(1);
});


function initRealtimeTraffic(){
    var check_realtime_second = $('#check_realtime_second').val();
    if (check_realtime_second<1){
        check_realtime_second = 1;
        $('#check_realtime_second').val(check_realtime_second);
    }

    if (check_realtime_second>10){
        check_realtime_second = 10;
        $('#check_realtime_second').val(check_realtime_second);
    }
    var title = "每秒请求";
    if (check_realtime_second > 1){
        title = '每'+check_realtime_second+'秒请求'
    }

    $('#ov_title_req_second').text(title)
    $('.check_realtime_request').text(title);
}


initRealtimeTraffic();
$('#check_realtime_second').change(function(){
    initRealtimeTraffic();
});

$('.indicators-container input[type=radio]').click(function(){
    $('.indicators-container input[type=radio]').each(function(){
        $(this).removeAttr('checked');
    });
    $(this).prop({'checked':true});

    wsOverviewRequest(1);
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
    wsOverviewRequest(1);

    $('select[name="site"]').change(function(){
        wsOverviewRequest(1);
    });
});

////////////////////////////////////////////////////////////////////////////////////////////////////////
}


function wsSitesListRequest(page){

    var args = {};
    var query_date = 'today';
    if ($('#time_choose').attr("data-name") != ''){
        query_date = $('#time_choose').attr("data-name");
    } else {
        query_date = $('#search_time button.cur').attr("data-name");
    }
    args['query_date'] = query_date;
   

    wsPost('get_site_list', '' ,args, function(rdata){

        var rdata = $.parseJSON(rdata.data);
        var data = rdata.data;


        var stat_pv = 0;
        var stat_uv = 0;
        var stat_ip = 0;
        var stat_length = 0;
        var stat_req = 0;

        // console.log(rdata, data);
         var list = '';
        if (data.length > 0){
            for(i in data){

                var tmp_pv = 0;
                var tmp_uv = 0;
                var tmp_ip = 0;
                var tmp_length = 0;
                var tmp_req = 0;

                if (data[i]['pv'] != null){
                    tmp_pv = data[i]['pv'];
                    stat_pv += data[i]['pv'];
                }

                if (data[i]['uv'] != null){
                    tmp_uv = data[i]['uv'];
                    stat_uv += data[i]['uv'];
                }

                if (data[i]['ip'] != null){
                    tmp_ip = data[i]['ip'];
                    stat_ip += data[i]['ip'];
                }

                if (data[i]['length'] != null){
                    tmp_length = data[i]['length'];
                    stat_length += data[i]['length'];
                }

                if (data[i]['req'] != null){
                    tmp_req = data[i]['req'];
                    stat_req += data[i]['req'];
                }

                list += '<tr>';
                list += '<td>' + data[i]['site']+'</td>';
                list += '<td>' + tmp_pv +'</td>';
                list += '<td>' + tmp_uv +'</td>';
                list += '<td>' + tmp_ip +'</td>';
                list += '<td>' + tmp_req +'</td>';
                list += '<td>' + toSize(tmp_length) +'</td>';
                list += '<td><a data-id="'+i+'" href="javascript:;" class="btlink web_set" title="设置">设置</a></td>';
                list += '</tr>';
            }
        } else{
             list += '<tr><td colspan="14" style="text-align:center;">网站列表为空</td></tr>';
        }

        $('.overview_list .overview_box:eq(0) .ov_num').text(stat_pv);
        $('.overview_list .overview_box:eq(1) .ov_num').text(stat_uv);
        $('.overview_list .overview_box:eq(2) .ov_num').text(stat_ip);
        $('.overview_list .overview_box:eq(3) .ov_num').text(toSize(stat_length));
        $('.overview_list .overview_box:eq(4) .ov_num').text(stat_req);
        
        var table = '<div class="tablescroll">\
                            <table id="DataBody" class="table table-hover" width="100%" cellspacing="0" cellpadding="0" border="0" style="border: 0 none;">\
                            <thead><tr>\
                            <th>网站</th>\
                            <th>流览量</th>\
                            <th>访客数</th>\
                            <th>IP数</th>\
                            <th>请求数</th>\
                            <th>总流量</th>\
                            <th>操作</th>\</tr></thead>\
                            <tbody>\
                            '+ list +'\
                            </tbody></table>\
                        </div>\
                        <div id="wsPage" class="dataTables_paginate paging_bootstrap page"></div>';
        $('#ws_table').html(table);


        $(".tablescroll .web_set").click(function(){
            var index = $(this).attr('data-id');

            var domain = data[index]["site"];
            wsPost('get_site_conf', '' ,{"site":domain}, function(rdata){
                var rdata = $.parseJSON(rdata.data);
                var rdata = rdata.data;
                console.log(rdata);
                layer.open({
                    type: 1,
                    title: "【"+domain + "】监控配置",
                    btn: ['保存','取消'], 
                    area: ['600px',"380px"],
                    closeBtn: 1,
                    shadeClose: false,
                    content: '<div id="site_conf" class="pd15 lib-box ws_setting">\
                       <div class="ws_content" style="width:570px;">\
                            <div class="tab-nav">\
                                <span data-type="cdn_headers" class="on">CDN headers</span>\
                                <span data-type="exclude_extension">排除扩展</span>\
                                <span data-type="exclude_status">排除响应状态</span>\
                                <span data-type="exclude_url">排除路径</span>\
                                <span data-type="exclude_ip">排除IP</span>\
                                <span data-type="record_post_args">记录请求原文</span>\
                            </div>\
                            <div class="tab-con">\
                                <span class="ws_tips">* 准确识别CDN网络IP地址，请注意大小写，如需多个请换行填写</span>\
                                <textarea name="setting-cdn" cols="52" rows="8"></textarea>\
                            </div>\
                        </div>\
                    </div>',
                    success:function(){
                        var common_tpl_tips = '<span class="ws_tips">* 准确识别CDN网络IP地址，请注意大小写，如需多个请换行填写</span>';
                        var common_tpl_area = '<textarea name="setting-cdn" cols="52" rows="8"></textarea>';

 
                        $('#site_conf .tab-con textarea').text(rdata['cdn_headers'].join('\n'));
                        $('#site_conf .tab-nav span').click(function(e){
                            $('#site_conf .tab-nav span').removeClass('on');
                            $(this).addClass('on');
                            $('#site_conf .tab-con').html('');

                            var typename = $(this).attr('data-type');
                            if (typename == 'cdn_headers'){
                                var content = $(common_tpl_tips).html('* 准确识别CDN网络IP地址，请注意大小写，如需多个请换行填写').prop('outerHTML');
                                var area = $(common_tpl_area).html(rdata['cdn_headers'].join('\n')).prop('outerHTML');

                                content += area;
                                $('#site_conf .tab-con').html(content);
                            } else if (typename == 'exclude_extension'){

                                var content = $(common_tpl_tips).html('* 排除的请求不写入网站日志，不统计PV、UV、IP，只累计总请求、总流量数，如需多个请换行填写').prop('outerHTML');
                                var area = $(common_tpl_area).html(rdata['exclude_extension'].join('\n')).prop('outerHTML');
                                content += area;
                                $('#site_conf .tab-con').html(content);
                            } else if (typename == 'exclude_status'){
                                var content = $(common_tpl_tips).html('* 排除的请求不写入网站日志，不统计PV、UV、IP，只累计总请求、总流量数，如需多个请换行填写').prop('outerHTML');
                                var area = $(common_tpl_area).html(rdata['exclude_status'].join('\n')).prop('outerHTML');
                                content += area;
                                $('#site_conf .tab-con').html(content);
                            } else if (typename == 'exclude_ip'){
                                var txt = '<div>* 排除的IP不写入网站日志，不统计PV、UV、IP，只累计总请求、总流量数，如需多个请换行填写</div>\
                                           <div style="margin-left: -10px">* 支持 192.168.1.1-192.168.1.10格式排除区间IP</div>'
                                var content = $(common_tpl_tips).html(txt).prop('outerHTML');
                                var area = $(common_tpl_area).html(rdata['exclude_ip'].join('\n')).prop('outerHTML');
                                content += area;
                                $('#site_conf .tab-con').html(content);
                            } else if (typename == 'record_post_args'){
                                var txt = '<div>记录请求原文说明：HTTP请求原文包括客户端请求详细参数，有助于分析或排查异常请求；</div>\
                                           <div style="margin-left: -10px">考虑到HTTP请求原文会<span style="color:red;">占用额外存储空间</span>，默认仅记录500错误请求原文。</div>'
                                var content = $(common_tpl_tips).html(txt).prop('outerHTML');

                                var record_post_args = '';
                                if (rdata['record_post_args']){
                                    record_post_args = 'checked';
                                }
                                var record_get_403_args = '';
                                if (rdata['record_get_403_args']){
                                    record_get_403_args = 'checked';
                                }


                                var check = '<div class="checkbox" style="margin: 20px 0 0 -10px;">\
                                            <label style="cursor: pointer;margin-right:15px;">\
                                                <input type="checkbox" name="record_post_args" style="margin: 1px 10 0;" '+record_post_args+'>记录POST请求原文\
                                            </label>\
                                            <label style="cursor: pointer;">\
                                                <input type="checkbox" name="record_get_403_args" style="margin: 1px 10 0;" '+record_get_403_args+'><span>记录403错误请求原文</span>\
                                            </label>\
                                        </div>';
                                content+=check;

                                $('#site_conf .tab-con').html(content);
                            } else if ( typename == 'exclude_url'){
                                var txt = '* 排除的请求不写入网站日志，不统计PV、UV、IP，只累计总请求、总流量数'
                                var content = $(common_tpl_tips).html(txt).prop('outerHTML');

                                var _text = '';
                                var _tmp = rdata['exclude_url'];
                                for(var i = 0; i<10; i++){
                                    if(typeof _tmp[i] == 'undefined'){
                                        _tmp[i] = {mode:'regular',url:''}
                                    }
                                    
                                    _text += '<tr>\
                                        <td>\
                                            <select name="url_type_'+i+'">\
                                                <option  value="normal" '+(_tmp[i].mode == 'normal'?'selected':'')+'>完整匹配</option>\
                                                <option value="regular" '+(_tmp[i].mode == 'regular'?'selected':'')+'>模糊匹配</option>\
                                            </select>\
                                        </td>\
                                        <td><input name="url_val_'+i+'" style="width:290px" placeholder="'+(_tmp[i].mode == 'normal'?'例：需排除a.com/test.html请求，请填写 test.html':'包含此内容的URL请求将不会被统计，请谨慎填写')+'" type="text" value="'+_tmp[i].url+'"></td>\
                                    </tr>';
                                }

                                var list = '<div class="divtable mt10 setting-exclude-url" style="margin-left: -10px;height: 100px;width:100%;">\
                                            <table class="table table-hover">\
                                                <thead>\
                                                    <tr><th width="96">排除方式</th><th>排除路径</th></tr>\
                                                </thead>\
                                                <tbody>'+_text+'</tbody>\
                                            </table>\
                                        </div>';
                                 
                                content += list;
                                $('#site_conf .tab-con').html(content);
                            }
                        });
                    },
                    yes:function(){
                        var select_pos = 0;
                        $('#site_conf .tab-nav span').each(function(i){
                            if ($(this).hasClass('on')){select_pos = i;}
                        });
                        var args = {"site":domain};
                        if ( [0,1,2,4].indexOf(select_pos)>-1 ){
                            var setting_cdn = $('textarea[name="setting-cdn"]').val();
                            // var list = setting_cdn.split('\n')
                            if ( select_pos == 0 ){
                                args['cdn_headers'] = setting_cdn;
                            } else if ( select_pos == 1 ){
                                args['exclude_extension'] = setting_cdn;
                            } else if ( select_pos == 2 ){
                                args['exclude_status'] = setting_cdn;
                            } else if ( select_pos == 4 ){
                                args['exclude_ip'] = setting_cdn;
                            }

                            wsPost('set_site_conf','', args, function(rdata){
                                var rdata = $.parseJSON(rdata.data);
                                layer.msg(rdata.msg,{icon:rdata.status?1:2});
                            });
                        }

                        if (select_pos == 3 ){

                            var list = "";
                            for (var i = 0; i<10; i++) {
                                var tmp = "";
                                var url_type = $('select[name="url_type_'+i+'"]').val();
                                var url_val = $('input[name="url_val_'+i+'"]').val();

                                if (url_val != ""){
                                    list += url_type +'|' + url_val +';';
                                }
                            }
                            args['exclude_url'] = list;
                            wsPost('set_site_conf','', args, function(rdata){
                                var rdata = $.parseJSON(rdata.data);
                                layer.msg(rdata.msg,{icon:rdata.status?1:2});
                            });
                        }

                        if (select_pos == 5){
                            var record_post_args = $('input[name="record_post_args"]').prop('checked');
                            var record_get_403_args = $('input[name="record_get_403_args"]').prop('checked');
                            args["record_post_args"] = record_post_args;
                            args['record_get_403_args'] = record_get_403_args;
                            wsPost('set_site_conf','', args, function(rdata){
                                var rdata = $.parseJSON(rdata.data);
                                layer.msg(rdata.msg,{icon:rdata.status?1:2});
                            });
                        }
                    },
                });
            });
        });
    });
}


function wsSitesList(){
////////////////////////////////////////////////////////////////////////////////////////////////////////
var randstr = getRandomString(10);

var html = '<div>\
                <div style="padding-bottom:10px;">\
                    <div class="input-group" style="width:300px;display: inline-table;vertical-align: top;">\
                        <div id="search_time" class="input-group-btn btn-group-sm">\
                            <button data-name="today" type="button" class="btn btn-default">今日</button>\
                            <button data-name="yesterday" type="button" class="btn btn-default">昨日</button>\
                            <button data-name="l7" type="button" class="btn btn-default">近7天</button>\
                            <button data-name="l30" type="button" class="btn btn-default">近30天</button>\
                        </div>\
                        <span class="last-span"><input data-name="" type="text" id="time_choose" lay-key="1000001_'+randstr+'" class="form-control btn-group-sm" autocomplete="off" placeholder="自定义时间" style="display: inline-block;font-size: 12px;padding: 0 10px;height:30px;width: 155px;"></span>\
                    </div>\
                </div>\
                <!-- stat --->\
                <div class="overview_list" style="padding-top:10px;">\
                    <div class="overview_box w_p20">\
                        <p class="ov_title">总浏览量(PV)</p>\
                        <p class="ov_num">0</p>\
                    </div>\
                    <div class="overview_box w_p20">\
                        <p class="ov_title">总访客量(UV)</p>\
                        <p class="ov_num">0</p>\
                    </div>\
                    <div class="overview_box w_p20">\
                        <p class="ov_title">总IP数</p>\
                        <p class="ov_num">0</p>\
                    </div>\
                    <div class="overview_box w_p20">\
                        <p class="ov_title">总流量</p>\
                        <p class="ov_num">0</p>\
                    </div>\
                    <div class="overview_box w_p20">\
                        <p class="ov_title">总请求</p>\
                        <p class="ov_num">0</p>\
                    </div>\
                </div>\
                <div class="divtable mtb10" id="ws_table"></div>\
            </div>';
$(".soft-man-con").html(html);
$('[data-toggle="tooltip"]').tooltip();
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

        wsSitesListRequest(1);
    },
});


$('#time_order button:eq(0)').addClass('cur');
$('#time_order button').click(function(){
    $('#time_order button').each(function(){
        if ($(this).hasClass('cur')){
            $(this).removeClass('cur');
        }
    });
    $(this).addClass('cur');
    wsSitesListRequest(1);
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

    wsSitesListRequest(1);
});

wsSitesListRequest(1);
////////////////////////////////////////////////////////////////////////////////////////////////////////
}


function wsSpiderStatLogRequest(page){

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

    args['tojs'] = 'wsSpiderStatLogRequest';
    wsPost('get_spider_stat_list', '' ,args, function(rdata){
        var rdata = $.parseJSON(rdata.data);
        var list = '';
        var data = rdata.data.data;
        if (data.length > 0){
            for(i in data){
                list += '<tr>';
                list += '<td>' + data[i]['time']+'</td>';
                list += '<td>' + data[i]['baidu'] +'</td>';
                list += '<td>' + data[i]['bing'] +'</td>';
                list += '<td>' + data[i]['qh360'] +'</td>';
                list += '<td>' + data[i]['google'] +'</td>';
                list += '<td>' + data[i]['bytes'] +'</td>';
                list += '<td>' + data[i]['sogou'] +'</td>';
                list += '<td>' + data[i]['soso'] +'</td>';
                list += '<td>' + data[i]['youdao'] +'</td>';
                list += '<td>' + data[i]['youdao'] +'</td>';
                list += '<td>' + data[i]['dnspod'] +'</td>';
                list += '<td>' + data[i]['yandex'] +'</td>';
                list += '<td>' + data[i]['other'] +'</td>';
                list += '<td>' + data[i]['other'] +'</td>';
                list += '</tr>';
            }
        } else{
             list += '<tr><td colspan="14" style="text-align:center;">蜘蛛列表为空</td></tr>';
        }
        
        var table = '<div class="tablescroll">\
                            <table id="DataBody" class="table table-hover" width="100%" cellspacing="0" cellpadding="0" border="0" style="border: 0 none;">\
                            <thead><tr>\
                            <th>日期</th>\
                            <th>百度</th>\
                            <th>必应</th>\
                            <th>奇虎360</th>\
                            <th>Google</th>\
                            <th>头条</th>\
                            <th>搜狗</th>\
                            <th>搜搜</th>\
                            <th>神马</th>\
                            <th>有道</th>\
                            <th>DNSPOD</th>\
                            <th>Yandex</th>\
                            <th>其他 <span class="tips" data-toggle="tooltip" data-placement="bottom" title="包括Yahoo,DuckDuckGo">?</span></th>\
                            <th>操作</th>\</tr></thead>\
                            <tbody>\
                            '+ list +'\
                            </tbody></table>\
                        </div>\
                        <div id="wsPage" class="dataTables_paginate paging_bootstrap page"></div>';
        $('#ws_table').html(table);
        $('#wsPage').html(rdata.data.page);
        $('[data-toggle="tooltip"]').tooltip();

        var sumData = rdata.data.sum_data;

        var percent = ((sumData.spider/sumData.reqest_total)*100).toFixed();
        
        $('#spider_left_total .request_spider').text(sumData.spider+"("+percent+"%)");
        $('#spider_left_total .request_total').text(sumData.reqest_total);

        // 图形化
        var initData = rdata.data.stat_list;
        
        var colorList = ['#6ec71e','#4885FF'];
        var source_name = {baidu:'百度',google:'Google',bytes:'头条',soso:'搜搜',bing:'必应',qh360:'奇虎360',youdao:'有道',yandex:'Yandex',dnspod:'DNSPOD',mpcrawler:'mpcrawler',other:'其他',};
        var lenend2_obj = {};

        var rightEc = echarts.init(document.getElementById('echart_right_total'));

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
            this.setOption(legend_option);
        });
    });
}


function wsSpiderStat(){
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
                    <div id="spider_left_total" style="height: 280px; width: 100px;display: inline-block;position: relative;">\
                        <div class="total_num_box"><p class="tn_title">总蜘蛛</p><p class="tn_num request_spider">0</p></div>\
                        <div class="total_num_box"><p class="tn_title">总请求</p><p class="tn_num request_total">0</p></div>\
                    </div>\
                    <div id="echart_right_total" style="height: 280px; width: 650px;display: inline-block;position: relative;"></div>\
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

        wsSpiderStatLogRequest(1);
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

    wsSpiderStatLogRequest(1);
});


$('select[name="status_code"]').change(function(){
    wsSpiderStatLogRequest(1);
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
    wsSpiderStatLogRequest(1);

    $('select[name="site"]').change(function(){
        wsSpiderStatLogRequest(1);
    });
});

////////////////////////////////////////////////////////////////////////////////////////////////////////
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



function wsIpStatLogRequest(page){

    var args = {}
    args['site'] = $('select[name="site"]').val();
    var query_date = 'today';
    query_date = $('#search_time button.cur').attr("data-name");
    args['query_date'] = query_date;

    args['tojs'] = 'wsIpStatLogRequest';
    wsPost('get_ip_stat_list', '' ,args, function(rdata){
        var rdata = $.parseJSON(rdata.data);
        var list = '';
        var data = rdata.data;
        // console.log(rdata,data);
        if (data.length > 0){
            for(i in data){
                list += '<tr>';
                list += '<td>' + (parseInt(i)+1)+'</td>';
                list += '<td><span class="overflow_hide" style="width:100px;">' + data[i]['ip']+'</span></td>';
                list += '<td>' + data[i]['area'] +'</td>';
                list += '<td>' + data[i]['day'] +'('+data[i]['day_rate']+'%)</td>';
                list += '<td>' + toSize(data[i]['flow']) +'('+data[i]['flow_rate']+'%)</td>';
                list += '<td><span><div class="share_num" style="width:'+data[i]['flow_rate']+'%"></div></span>' +'</td>';
                list += '</tr>';
            }


        } else{
             list += '<tr><td colspan="6" style="text-align:center;">IP列表为空</td></tr>';
        }
        
        var table = '<div class="tablescroll">\
                            <table id="DataBody" class="table table-hover" width="100%" cellspacing="0" cellpadding="0" border="0" style="border: 0 none;">\
                            <thead><tr>\
                            <th>序号</th>\
                            <th>IP</th>\
                            <th>归属地(仅供参考)</th>\
                            <th>请求数</th>\
                            <th>流量</th>\
                            <th>流量占比图</th>\
                            </tr></thead>\
                            <tbody>\
                            '+ list +'\
                            </tbody></table>\
                        </div>\
                        <div id="wsPage" class="dataTables_paginate paging_bootstrap page"></div>';
        $('#ws_table').html(table);
    });
}


function wsIpStat(){
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
                    </div>\
                </div>\
                <div class="divtable mtb10" id="ws_table"></div>\
            </div>';
$(".soft-man-con").html(html);


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

    wsIpStatLogRequest(1);
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
    wsIpStatLogRequest(1);

    $('select[name="site"]').change(function(){
        wsIpStatLogRequest(1);
    });
});

////////////////////////////////////////////////////////////////////////////////////////////////////////
}


function wsUriStatLogRequest(page){

    var args = {}
    args['site'] = $('select[name="site"]').val();
    var query_date = 'today';
    query_date = $('#search_time button.cur').attr("data-name");
    args['query_date'] = query_date;

    args['tojs'] = 'wsUriStatLogRequest';
    wsPost('get_uri_stat_list', '' ,args, function(rdata){
        var rdata = $.parseJSON(rdata.data);
        var list = '';
        var data = rdata.data;
        // console.log(rdata,data);
        if (data.length > 0){
            for(i in data){
                list += '<tr>';
                list += '<td>' + (parseInt(i)+1)+'</td>';
                list += '<td><span class="overflow_hide" style="width:100px;">' + data[i]['uri']+'</span></td>';
                list += '<td>' + data[i]['day'] +'('+data[i]['day_rate']+'%)</td>';
                list += '<td>' + toSize(data[i]['flow']) +'('+data[i]['flow_rate']+'%)</td>';
                list += '<td><span><div class="share_num" style="width:'+data[i]['flow_rate']+'%"></div></span>' +'</td>';
                list += '</tr>';
            }


        } else{
             list += '<tr><td colspan="6" style="text-align:center;">URI列表为空</td></tr>';
        }
        
        var table = '<div class="tablescroll">\
                            <table id="DataBody" class="table table-hover" width="100%" cellspacing="0" cellpadding="0" border="0" style="border: 0 none;">\
                            <thead><tr>\
                            <th>序号</th>\
                            <th>URI</th>\
                            <th>请求数</th>\
                            <th>流量</th>\
                            <th>流量占比图</th>\
                            </tr></thead>\
                            <tbody>\
                            '+ list +'\
                            </tbody></table>\
                        </div>\
                        <div id="wsPage" class="dataTables_paginate paging_bootstrap page"></div>';
        $('#ws_table').html(table);
    });
}


function wsUriStat(){
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
                    </div>\
                </div>\
                <div class="divtable mtb10" id="ws_table"></div>\
            </div>';
$(".soft-man-con").html(html);


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

    wsUriStatLogRequest(1);
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
    wsUriStatLogRequest(1);

    $('select[name="site"]').change(function(){
        wsUriStatLogRequest(1);
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
                list += '<td><span class="overflow_hide" style="width:100px;">' + data[i]['domain'] +'</span></td>';
                list += '<td><span class="overflow_hide" style="width:100px;">' + data[i]['ip'] +'</span></td>';
                list += '<td>' + toSize(data[i]['body_length']) +'</td>';
                list += '<td>' + toSecond(data[i]['request_time']) +'</td>';
                list += '<td><span class="overflow_hide" style="width:130px;">' + data[i]['uri'] +'</span></td>';
                list += '<td><span class="overflow_hide" style="width:60px;">' + data[i]['status_code']+'/' + data[i]['method'] +'</span></td>';
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
                closeBtn: 1,
                shadeClose: false,
                content: '<div class="pd15 lib-box">\
                    <div style="height:80px;"><table class="table" style="border:#ddd 1px solid; margin-bottom:10px">\
                    <tbody class="site_details_tbody">\
                        <tr><th>时间</th><td>' + getLocalTime(res.time) + '</td><th>真实IP</th><td><span class="overflow_hide detail_ip" style="width:100px;">' + res.ip + '</span></td><th>客户端端口</th><td>'+(res.client_port>0 && res.client_port != ''?res.client_port:'')+'</td></tr>\
                        <tr><th>类型</th><td>' + res.method + '</td><th>状态</th><td>' + res.status_code + '</td><th>响应大小</th><td>' + toSize(res.body_length) + '</td>\</tr>\
                    </tbody></table></div>\
                    <div><b style="margin-left:10px">协议</b></div>\
                    <div class="lib-con mt10"><div class="divpre">' + res.protocol + '</div></div>\
                    <div><b style="margin-left:10px">URL</b></div>\
                    <div class="lib-con mt10"><div class="divpre">' + $('<div ></div>').text(res.uri).html() + '</div></div>\
                    <div><b style="margin-left:10px">完整IP列表</b></div>\
                    <div class="lib-con mt10"><div class="divpre" style="max-height: 66px;">' + $('<div ></div>').text(res.ip_list).html() + '</div></div>\
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
                        <option value="499">499</option>\
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

        var timeA  = value.split('-');
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
    args['page_size'] = 9;

    args['site'] = $('select[name="site"]').val();
    args['method'] = $('select[name="method"]').val();
    args['status_code'] = $('select[name="status_code"]').val();
    args['request_time'] = $('select[name="request_time"]').val();
    args['request_size'] = $('select[name="request_size"]').val();
    args['spider_type'] = $('select[name="spider_type"]').val();
    args['referer'] = $('select[name="referer"]').val();
    args['ip'] = $('input[name="ip"]').val();

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

    var spider_table = {
        "1":"百度",
        "2":"必应",
        "3":"奇虎360",
        "4":"Google",
        "5":"头条",
        "6":"搜狗",
        "7":"有道",
        "8":"搜搜",
        "9":"Dnspod",
        "10":"Yandex",
        "11":"一搜",
        "12":"其他",
    }

    var req_status = $('#logs_search').attr('req');
    // console.log(req_status);
    if (typeof(req_status) != 'undefined'){
        if (req_status == 'start'){
            layer.msg("正在请求中,请稍候!");
            return;
        }
    }

    $('#logs_search').attr('req','start');
    // wsPost('get_logs_list', '' ,args, function(rdata){
    wsPostCallbak('get_logs_list', '' ,args, function(rdata){
        $('#logs_search').attr('req','end');
        var rdata = $.parseJSON(rdata.data);
        var list = '';
        var data = rdata.data.data;
        // console.log(data);

        if (data.length > 0){
            for(i in data){
                
                var spider_tip = '';
                if (data[i]['is_spider']>0){
                    spider_tip_name = spider_table[data[i]['is_spider']]
                    spider_tip = '<div data-toggle="tooltip" title="'+spider_tip_name+'爬虫" style="cursor:pointer;margin:3px;float:left;width:8px;height:8px;line-height:40px;border-radius:50%;background-color:#ccc;"></div>';
                }

                list += '<tr>';
                list += '<td>' + getLocalTime(data[i]['time'])+'</td>';
                list += '<td><span class="overflow_hide" style="width:100px;">' + data[i]['domain'] +'</span></td>';
                list += '<td><span class="overflow_hide" style="width:100px;">' + data[i]['ip'] +'</span></td>';
                list += '<td>' + toSize(data[i]['body_length']) +'</td>';
                list += '<td>' + toSecond(data[i]['request_time']) +'</td>';
                list += '<td><span class="overflow_hide" style="width:130px;">' + data[i]['uri'] +'</span></td>';
                list += '<td>'+spider_tip+'<span class="overflow_hide" style="width:60px;">' + data[i]['status_code']+'/' + data[i]['method'] +'</span></td>';

                var http_data = '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;';
                if (data[i]['request_headers']!=''){
                    http_data = '<a data-id="'+i+'" href="javascript:;" class="btlink http_data" title="HTTP">HTTP</a>&nbsp;|&nbsp;';
                }
                list += '<td><span>'+http_data+'<a data-id="'+i+'" href="javascript:;" class="btlink details" title="详情">详情</a></span></td>';
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
                            <th>URL</th>\
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
                closeBtn: 1,
                shadeClose: false,
                content: '<div class="pd15 lib-box">\
                    <div style="height:80px;"><table class="table" style="border:#ddd 1px solid; margin-bottom:10px">\
                    <tbody class="site_details_tbody">\
                        <tr><th>时间</th><td>' + getLocalTime(res.time) + '</td><th>真实IP</th><td><span class="overflow_hide detail_ip" style="width:100px;">' + res.ip + '</span></td><th>客户端端口</th><td>'+(res.client_port>0 && res.client_port != ''?res.client_port:'')+'</td></tr>\
                        <tr><th>类型</th><td>' + res.method + '</td><th>状态</th><td>' + res.status_code + '</td><th>响应大小</th><td>' + toSize(res.body_length) + '</td>\</tr>\
                    </tbody></table></div>\
                    <div><b style="margin-left:10px">协议</b></div>\
                    <div class="lib-con mt10"><div class="divpre">' + res.protocol + '</div></div>\
                    <div><b style="margin-left:10px">URL</b></div>\
                    <div class="lib-con mt10"><div class="divpre">' + $('<div></div>').text(res.uri).html() + '</div></div>\
                    <div><b style="margin-left:10px">完整IP列表</b></div>\
                    <div class="lib-con mt10"><div class="divpre" style="max-height: 66px;">' + $('<div ></div>').text(res.ip_list).html() + '</div></div>\
                    <div><b style="margin-left:10px">来路</b></div>\
                    <div class="lib-con mt10"><div class="divpre">' + $('<div></div>').text(res.referer == null ?'None':res.referer).html() + '</div></div>\
                    <div><b style="margin-left:10px">User-Agent</b></div>\
                    <div class="lib-con mt10"><div class="divpre">' + $('<div></div>').text(res.user_agent).html() + '</div></div>\
                    <div><b style="margin-left:10px">处理耗时</b></div>\
                    <div class="lib-con mt10"><div class="divpre">' +res.request_time + ' ms</div></div>\
                </div>',
            });
        });

        $(".tablescroll .http_data").click(function(){
            var index = $(this).attr('data-id');
            var res = data[index];
            var request_headers = res.request_headers;

            var req_data_html = res.method +' ' + res.uri + '<br/>';

            try {
                var req_data = $.parseJSON(request_headers);
                for (var d in req_data) {
                    if (d == 'payload'){
                        req_data_html += '<b style="color:red;">'+d +"</b>:"+req_data[d]+"<br/>";
                    } else{
                        req_data_html += d+":"+req_data[d]+"<br/>";
                    }
                }
            } catch (error) {
                req_data_html += request_headers;
            }


            layer.open({
                type: 1,
                title: "【"+res.domain + "】HTTP详情",
                area: ['600px','375px'],
                closeBtn: 1,
                shadeClose: false,
                content: '<div class="pd15 lib-box">\
                    <div class="lib-con mt10"><div class="divpre" style="max-height:250px;white-space: break-spaces;">' + req_data_html + '</div></div>\
                    <ul class="help-info-text c7 mtb15">\
                        <li style="list-style: none;">payload: POST请求中客户端提交的参数。</li>\
                    </ul>\
                </div>',
            });
        });

        $('[data-toggle="tooltip"]').tooltip();
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
                        <option value="400">400</option>\
                        <option value="404">404</option>\
                        <option value="499">499</option>\
                        <option value="301">301</option>\
                        <option value="302">302</option>\
                        <option value="200">200</option>\
                    </select>\
                    <span style="margin-left:10px;">来源: </span>\
                    <select class="bt-input-text" name="referer" style="margin-left:4px">\
                        <option value="all">所有</option>\
                        <option value="-1">无</option>\
                        <option value="1">有</option>\
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
                        <option value="11">一搜</option>\
                        <option value="12">其他</option>\
                    </select>\
                    <span>IP: </span>\
                    <div class="input-group" style="width:163px;display:inline-flex;">\
                        <input type="text" name="ip" class="form-control btn-group-sm" autocomplete="off" placeholder="IP地址" style="font-size: 12px;padding: 0 10px;height:30px;">\
                    </div>\
                </div>\
                <div style="padding-bottom:10px;">\
                    <span>耗时: </span>\
                    <select class="bt-input-text" name="request_time" style="margin-left:5px;">\
                        <option value="all">所有</option>\
                        <option value="0-50">0-50(ms)</option>\
                        <option value="50-200">50-200(ms)</option>\
                        <option value="200-500">200-500(ms)</option>\
                        <option value="500-1000">500ms-1s</option>\
                        <option value="1000">大于1s</option>\
                    </select>\
                    <span style="margin-left:10px;">大小: </span>\
                    <select class="bt-input-text" name="request_size" style="margin-left:5px;">\
                        <option value="all">所有</option>\
                        <option value="0-1">0-1(kb)</option>\
                        <option value="1-20">1-20(kb)</option>\
                        <option value="20-50">20-50(kb)</option>\
                        <option value="50-100">50-100(kb)</option>\
                        <option value="100">大于100kb</option>\
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

$('input[name="ip"]').bind('focus', function(e){
    $(this).keyup(function(e){
        if(e.keyCode == 13) {
            wsTableLogRequest(1);
        }
    });
});

$('input[name="search_uri"]').bind('focus', function(e){
    $(this).keyup(function(e){
        if(e.keyCode == 13) {
            wsTableLogRequest(1);
        }
    });
});

//日期范围
laydate.render({
    elem: '#time_choose',
    value:'',
    range:'~',
    type:'datetime',
    done:function(value, startDate, endDate){
        console.log(value, startDate, endDate);
        if(!value){
            return false;
        }

        $('#search_time button').each(function(){
            $(this).removeClass('cur');
        });

        var timeArr  = value.split('~');
        var start = $.trim(timeArr[0]);
        var end = $.trim(timeArr[1]);
        query_txt = toUnixTime(start) + "-"+ toUnixTime(end);

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

$('select[name="referer"]').change(function(){
    wsTableLogRequest(1);
});

$('select[name="request_time"]').change(function(){
    wsTableLogRequest(1);
});

$('select[name="request_size"]').change(function(){
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


