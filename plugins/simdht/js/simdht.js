function dhtPostMin(method, args, callback){

    var req_data = {};
    req_data['name'] = 'simdht';
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

function dhtPost(method, args, callback){
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });
    dhtPostMin(method,args,function(data){
        layer.close(loadT);
        if(typeof(callback) == 'function'){
            callback(data);
        } 
    });
}


function dhtTrend(){
    var trend = '<div id="dht_trend" style="width:100%;height:330px;"></div>';
    $('.soft-man-con').html(trend);
    dhtTrendRender();
}

function dhtTrendData(callback){
    dhtPostMin('get_trend_data',{interval:5},function(data){
        if(typeof(callback) == 'function'){
            callback(data);
        }
    });
}


function dhtTrendRender() {
    var myChartNetwork = echarts.init(document.getElementById('dht_trend'));
    var xData = [];
    var yData = [];
    var zData = [];

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

    function ts(m) { return m < 10 ? '0' + m : m }

    function format(sjc) {
        var time = new Date(sjc);
        var h = time.getHours();
        var mm = time.getMinutes();
        var s = time.getSeconds();
        return ts(h) + ':' + ts(mm) + ':' + ts(s);
    }

    function addData(data) {
        console.log(data);
        xData.push(getTime());
        yData.push(data[0]);
        zData.push(data[1]);
        // if (shift) {
        //     xData.shift();
        //     yData.shift();
        //     zData.shift();
        // }
    }
    for (var i = 8; i >= 0; i--) {
        var time = (new Date()).getTime();
        xData.push(format(time - (i * 3 * 1000)));
        yData.push(0);
        zData.push(0);
    }
    // 指定图表的配置项和数据
    var option = {
        title: {
            text: lan.index.interface_net,
            left: 'center',
            textStyle: {
                color: '#888888',
                fontStyle: 'normal',
                fontFamily: lan.index.net_font,
                fontSize: 16,
            }
        },
        tooltip: {
            trigger: 'axis'
        },
        legend: {
            data: [lan.index.net_up, lan.index.net_down],
            bottom: '2%'
        },
        xAxis: {
            type: 'category',
            boundaryGap: false,
            data: xData,
            axisLine: {
                lineStyle: {
                    color: "#666"
                }
            }
        },
        yAxis: {
            name: lan.index.unit + 'KB/s',
            splitLine: {
                lineStyle: {
                    color: "#eee"
                }
            },
            axisLine: {
                lineStyle: {
                    color: "#666"
                }
            }
        },
        series: [{
            name: lan.index.net_up,
            type: 'line',
            data: yData,
            smooth: true,
            showSymbol: false,
            symbol: 'circle',
            symbolSize: 6,
            areaStyle: {
                normal: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{
                        offset: 0,
                        color: 'rgba(255, 140, 0,0.5)'
                    }, {
                        offset: 1,
                        color: 'rgba(255, 140, 0,0.8)'
                    }], false)
                }
            },
            itemStyle: {
                normal: {
                    color: '#f7b851'
                }
            },
            lineStyle: {
                normal: {
                    width: 1
                }
            }
        }, {
            name: lan.index.net_down,
            type: 'line',
            data: zData,
            smooth: true,
            showSymbol: false,
            symbol: 'circle',
            symbolSize: 6,
            areaStyle: {
                normal: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{
                        offset: 0,
                        color: 'rgba(30, 144, 255,0.5)'
                    }, {
                        offset: 1,
                        color: 'rgba(30, 144, 255,0.8)'
                    }], false)
                }
            },
            itemStyle: {
                normal: {
                    color: '#52a9ff'
                }
            },
            lineStyle: {
                normal: {
                    width: 1
                }
            }
        }]
    };
    setInterval(function() {
        dhtTrendData(function(data){
            addData(data);
        });
        myChartNetwork.setOption({
            xAxis: {data: xData},
            series: [
                {name: '5s',data: yData}, 
                {name: '10s',data: zData}
            ]
        });
    }, 5000);
    // 使用刚指定的配置项和数据显示图表。
    myChartNetwork.setOption(option);
    window.addEventListener("resize", function() {
        myChartNetwork.resize();
    });
}


