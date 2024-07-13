
function pingPost(method, args, callback){
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });

    var req_data = {};
    req_data['name'] = 'simpleping';
    req_data['func'] = method;
 
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

function pingPostCallbak(method, args, callback){
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });

    var req_data = {};
    req_data['name'] = 'simpleping';
    req_data['script'] = 'simpleping_index';
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

function pingPostCallbakN(method, args, callback){
    var req_data = {};
    req_data['name'] = 'simpleping';
    req_data['script'] = 'simpleping_index';
    req_data['func'] = method;
 
    if (typeof(args) == 'string'){
        req_data['args'] = JSON.stringify(toArrayObject(args));
    } else {
        req_data['args'] = JSON.stringify(args);
    }

    $.post('/plugins/callback', req_data, function(data) {
        if(typeof(callback) == 'function'){
            callback(data);
        }
    },'json'); 
}


function appReadme(){

    var readme = '<ul class="help-info-text c7">';
    readme += '<li>简单说明</li>';
    readme += '<li>主要是检查内网连通性</li>';
    readme += '</ul>';
    $('.soft-man-con').html(readme);
}

var chartPing;
var chartPingData = [];
var posTimer;

// 把Unix时间戳转化成普通日期
function toCommonTime(unix_time){
    var unixTimestamp = new Date(unix_time*1000);
    var commonTime = unixTimestamp.toLocaleString();
    return commonTime;
}

function getToday(){
   var mydate = new Date();
   var str = "" + mydate.getFullYear() + "/";
   str += (mydate.getMonth()+1) + "/";
   str += mydate.getDate();
   return str;
}

//定义周期时间
function getBeforeDate(n){
    var n = n;
    var d = new Date();
    var year = d.getFullYear();
    var mon=d.getMonth()+1;
    var day=d.getDate();
    if(day <= n){
        if(mon>1) {
            mon = mon-1;
        } else {
            year = year-1;
            mon = 12;
        }
    }
    d.setDate(d.getDate()-n);
    year = d.getFullYear();
    mon=d.getMonth()+1;
    day=d.getDate();
    s = year+"/"+(mon<10?('0'+mon):mon)+"/"+(day<10?('0'+day):day);
    return s;
}


function pingDataGraphPosData(){

    var isOk = document.getElementById('pingview');
    if (!isOk){
        clearInterval(posTimer);
    }

    if (chartPingData.length>0){
        var dlen = chartPingData.length;
        last_pos = chartPingData[dlen-1];
        // console.log(start,end);
        var cur_ip = $('select[name="ip_list"]').val();
        pingPostCallbakN('pingData', {'type':'pos', 'pos':last_pos['created_unix'],"ip":cur_ip}, function(data){
            var tmp_data = data.data;
            for (x in tmp_data){
                chartPingData.push(tmp_data[x]);
            }
            pingDataGraphRender();
        });

    }
}


function pingDataGraphData(day){
    
    var now = (new Date().getTime())/1000;
    if(day==0){
        var start = (new Date(getToday() + " 00:00:01").getTime())/1000;
        start = Math.round(start);
        var end = Math.round(now);
    }
    if(day==1){
        var start = (new Date(getBeforeDate(day) + " 00:00:01").getTime())/1000;
        var end = (new Date(getBeforeDate(day) + " 23:59:59").getTime())/1000;
        start = Math.round(start);
        end = Math.round(end);
    } else {
        var start = (new Date(getBeforeDate(day) + " 00:00:01").getTime())/1000;
            start = Math.round(start);
        var end = Math.round(now);
    }

    var cur_ip = $('select[name="ip_list"]').val();
    // console.log(start,end);
    pingPostCallbak('pingData', {'type':'range', 'start':start, 'end':end, 'ip':cur_ip}, function(data){
        chartPingData = data.data;
        pingDataGraphRender();

        if (day!=1){
            clearInterval(posTimer);
            posTimer = setInterval(function() {
                pingDataGraphPosData();
            }, 3000);
        }
    });
}

function pingDataGraphRender(){
    var xData = [];
    var yData = [];
    var rdata = chartPingData;
    for(var i = 0; i < rdata.length; i++){
        xData.push(toCommonTime(rdata[i].created_unix));
        yData.push(rdata[i].speed/1000000);
    }
    var option = {
        tooltip: {
            trigger: 'axis',
            axisPointer: { type: 'cross' },
            formatter: '{b}<br />{a}: {c}'
        },
        xAxis: {
            type: 'category',
            boundaryGap: false,
            data: xData,
            axisLine:{ lineStyle:{ color:"#666"} } 
        },
        yAxis: {
            type: 'value',
            name: "PING延迟(ms)",
            // boundaryGap: [0, '100%'],
            // min:0,
            // max: 100,
            splitLine:{ lineStyle:{ color:"#ddd" } },
            axisLine:{ lineStyle:{ color:"#666" } }
        },
        series: [
            {
                name:'PING',
                type:'line',
                smooth:true,
                symbol: 'none',
                sampling: 'average',
                itemStyle: { normal: { color: 'rgb(0, 153, 238)' } },
                data: yData
            }
        ]
    };
    chartPing.setOption(option);
}

function pingIpList(){
    pingPost('ip_list', {}, function(data){
        var rdata = $.parseJSON(data.data);
        var ips = rdata.data;

        var option = '';
        option += '<option value="all">所有</option>';

        for (var i = 0; i < ips.length; i++) {
            option += '<option value="'+ips[i]+'">'+ips[i]+'</option>';
        }
        $('select[name="ip_list"]').html(option);


        $('select[name="ip_list"]').change(function(){
            chartPingData = [];
            pingDataGraphData(0);
        });

        pingDataGraphData(0);
    });

}

// console.log('pingDataGraph');
function pingDataGraph(){
    var tpl = '\
    <div class="col-xs-12 col-sm-12 col-md-12 pull-left pd0 view1">\
        <div class="pr8">\
            <div class="bgw pb15">\
                <div class="title c6 plr15">\
                    <h3 class="c-tit f16">连通性</h3>\
                    <div class="searcTime pull-right">\
                        <select class="bt-input-text gt" name="ip_list" style="height:28px;margin-left:0px;">\
                            <option value="all">所有</option>\
                        </select>\
                        <span class="gt" onclick="pingDataGraphData(1)">昨天</span>\
                        <span class="gt on" onclick="pingDataGraphData(0)">今天</span>\
                        <span class="gt" onclick="pingDataGraphData(7)">最近7天</span>\
                    </div>\
                </div>\
                <div id="pingview" style="width:100%; height:330px"></div>\
            </div>\
        </div>\
    </div>';
    $('.soft-man-con').html(tpl);

    $('.searcTime span').click(function(e){
        $('.searcTime span').removeClass('on');
        $(this).addClass('on');
    });

    chartPing = echarts.init(document.getElementById('pingview'));

    var option = {
        tooltip: {
            trigger: 'axis',
            axisPointer: { type: 'cross' },
            formatter: '{b}<br />{a}: {c}'
        },
        xAxis: {
            type: 'category',
            boundaryGap: false,
            data: [],
            axisLine:{ lineStyle:{ color:"#666"} } 
        },
        yAxis: {
            type: 'value',
            name: "PING延迟(ms)",
            splitLine:{ lineStyle:{ color:"#ddd" } },
            axisLine:{ lineStyle:{ color:"#666" } }
        },
        dataZoom: [{
            type: 'inside',
            start: 0,
            end: 100,
            zoomLock:true
        }, {
            start: 0,
            end: 100,
            handleIcon: 'M10.7,11.9v-1.3H9.3v1.3c-4.9,0.3-8.8,4.4-8.8,9.4c0,5,3.9,9.1,8.8,9.4v1.3h1.3v-1.3c4.9-0.3,8.8-4.4,8.8-9.4C19.5,16.3,15.6,12.2,10.7,11.9z M13.3,24.4H6.7V23h6.6V24.4z M13.3,19.6H6.7v-1.4h6.6V19.6z',
            handleSize: '80%',
            handleStyle: {
                color: '#fff',
                shadowBlur: 3,
                shadowColor: 'rgba(0, 0, 0, 0.6)',
                shadowOffsetX: 2,
                shadowOffsetY: 2
            }
        }],
        series: [
            {
                name:'PING',
                type:'line',
                smooth:true,
                symbol: 'none',
                sampling: 'average',
                itemStyle: { normal: { color: 'rgb(0, 153, 238)' } },
                data: []
            }
        ]
    };
    chartPing.setOption(option);
    window.addEventListener("resize",function(){
        chartPing.resize();
    });

    pingIpList();
}





// --------------------------------------------------------------------------------------------------------------
//                        MYSQL PING
// --------------------------------------------------------------------------------------------------------------

var chartMySQLPingData = [];
var chartMySQLPing;
var posMySQLTimer;

function pingMySQLDataGraphPosData(){

    var isOk = document.getElementById('mysqlview');
    if (!isOk){
        clearInterval(posMySQLTimer);
    }

    if (chartMySQLPingData.length>0){
        var dlen = chartMySQLPingData.length;
        last_pos = chartMySQLPingData[dlen-1];
        // console.log(start,end);
        pingPostCallbakN('pingMySQLData', {'type':'pos', 'pos':last_pos['created_unix']}, function(data){
            var tmp_data = data.data;
            for (x in tmp_data){
                chartMySQLPingData.push(tmp_data[x]);
            }
            pingDataMySQLGraphRender();
        });

    }
}

function pingDataMySQLGraphRender(){
    var xData = [];
    var yData = [];
    var rdata = chartMySQLPingData;
    for(var i = 0; i < rdata.length; i++){
        xData.push(toCommonTime(rdata[i].created_unix));
        yData.push(rdata[i].value);
    }
    var option = {
        tooltip: {
            trigger: 'axis',
            axisPointer: { type: 'cross' },
            formatter: '{b}<br />{a}: {c}'
        },
        xAxis: {
            type: 'category',
            boundaryGap: false,
            data: xData,
            axisLine:{ lineStyle:{ color:"#666"} } 
        },
        yAxis: {
            type: 'value',
            name: "MySQL同步延迟",
            splitLine:{ lineStyle:{ color:"#ddd" } },
            axisLine:{ lineStyle:{ color:"#666" } }
        },
        series: [
            {
                name:'同步延迟',
                type:'line',
                smooth:true,
                symbol: 'none',
                sampling: 'average',
                itemStyle: { normal: { color: 'rgb(0, 153, 238)' } },
                data: yData
            }
        ]
    };
    chartMySQLPing.setOption(option);
}

function pingMySQLDataGraphData(day){
    
    var now = (new Date().getTime())/1000;
    if(day==0){
        var start = (new Date(getToday() + " 00:00:01").getTime())/1000;
        start = Math.round(start);
        var end = Math.round(now);
    }
    if(day==1){
        var start = (new Date(getBeforeDate(day) + " 00:00:01").getTime())/1000;
        var end = (new Date(getBeforeDate(day) + " 23:59:59").getTime())/1000;
        start = Math.round(start);
        end = Math.round(end);
    } else {
        var start = (new Date(getBeforeDate(day) + " 00:00:01").getTime())/1000;
            start = Math.round(start);
        var end = Math.round(now);
    }

    var cur_ip = $('select[name="ip_list"]').val();
    // console.log(start,end);
    pingPostCallbak('pingMySQLData', {'type':'range', 'start':start, 'end':end, 'ip':cur_ip}, function(data){
        chartMySQLPingData = data.data;
        pingDataMySQLGraphRender();
        if (day!=1){
            clearInterval(posMySQLTimer);
            posMySQLTimer = setInterval(function() {
                pingMySQLDataGraphPosData();
            }, 3000);
        }
    });
}


function pingMySQLDataGraph(){
    var tpl = '\
    <div class="col-xs-12 col-sm-12 col-md-12 pull-left pd0 view1">\
        <div class="pr8">\
            <div class="bgw pb15">\
                <div class="title c6 plr15">\
                    <h3 class="c-tit f16">MySQL检查</h3>\
                    <div class="searcTime pull-right">\
                        <span class="gt" onclick="pingMySQLDataGraphData(1)">昨天</span>\
                        <span class="gt on" onclick="pingMySQLDataGraphData(0)">今天</span>\
                        <span class="gt" onclick="pingMySQLDataGraphData(7)">最近7天</span>\
                    </div>\
                </div>\
                <div id="mysqlview" style="width:100%; height:330px"></div>\
            </div>\
        </div>\
    </div>';
    $('.soft-man-con').html(tpl);

    $('.searcTime span').click(function(e){
        $('.searcTime span').removeClass('on');
        $(this).addClass('on');
    });

    chartMySQLPing = echarts.init(document.getElementById('mysqlview'));

    var option = {
        tooltip: {
            trigger: 'axis',
            axisPointer: { type: 'cross' },
            formatter: '{b}<br />{a}: {c}'
        },
        xAxis: {
            type: 'category',
            boundaryGap: false,
            data: [],
            axisLine:{ lineStyle:{ color:"#666"} } 
        },
        yAxis: {
            type: 'value',
            name: "MySQL延迟",
            splitLine:{ lineStyle:{ color:"#ddd" } },
            axisLine:{ lineStyle:{ color:"#666" } }
        },
        dataZoom: [{
            type: 'inside',
            start: 0,
            end: 100,
            zoomLock:true
        }, {
            start: 0,
            end: 100,
            handleIcon: 'M10.7,11.9v-1.3H9.3v1.3c-4.9,0.3-8.8,4.4-8.8,9.4c0,5,3.9,9.1,8.8,9.4v1.3h1.3v-1.3c4.9-0.3,8.8-4.4,8.8-9.4C19.5,16.3,15.6,12.2,10.7,11.9z M13.3,24.4H6.7V23h6.6V24.4z M13.3,19.6H6.7v-1.4h6.6V19.6z',
            handleSize: '80%',
            handleStyle: {
                color: '#fff',
                shadowBlur: 3,
                shadowColor: 'rgba(0, 0, 0, 0.6)',
                shadowOffsetX: 2,
                shadowOffsetY: 2
            }
        }],
        series: [
            {
                name:'延迟',
                type:'line',
                smooth:true,
                symbol: 'none',
                sampling: 'average',
                itemStyle: { normal: { color: 'rgb(0, 153, 238)' } },
                data: []
            }
        ]
    };
    chartMySQLPing.setOption(option);
    window.addEventListener("resize",function(){
        chartMySQLPing.resize();
    });

    pingMySQLDataGraphData(0);
}


