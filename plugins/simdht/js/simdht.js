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
    var obj = $('#dht_trend');
    if (obj.length>0){
        console.log('已经加载图表...');
        return;
    }

    var trend = '<div id="dht_trend" style="width:100%;height:330px;"></div>';
    $('.soft-man-con').html(trend);
    dhtTrendRender();
}

function dhtTrendData(callback){
    dhtPostMin('get_trend_data',{interval:1},function(data){
        if(typeof(callback) == 'function'){
            callback(data);
        }
    });
}


function dhtTrendRender() {
    var myChartNetwork = echarts.init(document.getElementById('dht_trend'));
    var xData = [];
    var oneData = [];
    var twoData = [];
    var threeData = [];

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
        // console.log(data);
        var rdata = $.parseJSON(data.data);
        xData.push(getTime());
        oneData.push(rdata[0]);
        twoData.push(rdata[1]);
        threeData.push(rdata[2]);

        xData.shift();
        oneData.shift();
        twoData.shift();
        threeData.shift();
    }
    for (var i = 8; i >= 0; i--) {
        var time = (new Date()).getTime();
        xData.push(format(time - (i * 5 * 1000)));
        oneData.push(0);
        twoData.push(0);
        threeData.push(0);
    }
    // 指定图表的配置项和数据
    var option = {
        title: {
            text: '种子收录趋势',
            left: 'center',
            textStyle: {
                color: '#888888',fontStyle: 'normal',
                fontFamily: '宋体',fontSize: 16,
            }
        },
        tooltip: {
            trigger: 'axis'
        },
        legend: {
            data: ['1s', '5s', '10s'],
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
            name: '单位个数',
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
            name: '1s',
            type: 'line',
            data: oneData,
            smooth: true,
            showSymbol: false,
            symbol: 'circle',
            symbolSize: 6,
            areaStyle: {
                normal: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, 
                        [{offset: 0,color: 'rgba(205, 51, 51,0.5)'}, 
                        {offset: 1,color: 'rgba(205, 51, 51,0.8)'}], false)
                }
            },
            itemStyle: {
                normal: {color: '#cd3333'}
            },
            lineStyle: {
                normal: {width: 1}
            }
        }, {
            name: '5s',
            type: 'line',
            data: twoData,
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
                normal: {color: '#52a9ff'}
            },
            lineStyle: {
                normal: {
                    width: 1
                }
            }
        },{
            name: '10s',
            type: 'line',
            data: threeData,
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
                normal: {color: '#C6E2FF'}
            },
            lineStyle: {
                normal: {
                    width: 1
                }
            }
        }]
    };
    

    // 使用刚指定的配置项和数据显示图表。
    myChartNetwork.setOption(option);
    window.addEventListener("resize", function() {
        myChartNetwork.resize();
    });

    function render(){
        dhtTrendData(function(data){
            addData(data);
        });
        myChartNetwork.setOption({
            xAxis: {data: xData},
            series: [
                {name: '1s',data: oneData}, 
                {name: '5s',data: twoData},
                {name: '10s',data: threeData}
            ]
        });
    }
    render();

    renderTick = setInterval(function() {
        render();
    }, 3000);

    checkTick = setInterval(function() {
        var obj = $('#dht_trend');
        if (obj.length>0){
            return;
        } else {
            console.log('取消定时请求...');
            clearInterval(renderTick);
            clearInterval(checkTick);
        }
    }, 300);
}

function dhtRead(){
    dhtPost('dht_cmd','', function(data){
        // console.log(data);
        var readme = '<p>* 在手动导入SQL-先把数据表创建</p>';
        readme += '<p>* 修改成对应的配置文件</p>';
        readme += '<p>* 加入到计划[自行调节]:'+data.data+'</p>';
        $('.soft-man-con').html(readme);
    });
   
}
