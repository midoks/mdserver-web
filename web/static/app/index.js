//获取负载
function getLoad(data) {
    $("#Load").text("获取中..");
    setCookie('one', data.one);
    setCookie('five', data.five);
    setCookie('fifteen', data.fifteen);
    var transformLeft, transformRight, LoadColor, Average, Occupy, AverageText, conterError = '';
    var index = $("#LoadList");
    if (Average == undefined) Average = data.one;
    setCookie('conterError', conterError);
    Occupy = Math.round((Average / data.max) * 100);
    if (Occupy > 100) Occupy = 100;
    if (Occupy <= 30) {
        LoadColor = '#20a53a';
        AverageText = '运行流畅';
    } else if (Occupy <= 70) {
        LoadColor = '#6ea520';
        AverageText = '运行正常';
    } else if (Occupy <= 90) {
        LoadColor = '#ff9900';
        AverageText = '运行缓慢';
    } else {
        LoadColor = '#dd2f00';
        AverageText = '运行堵塞';
    }
    index.find('.mask').css({ "color": LoadColor });
    updateLinearProgressValue(document.getElementById('LoadProgress'), Occupy, LoadColor);
    $('#Load').html(Occupy);
    $('#LoadState').html('<span>' + AverageText + '</span>');
}

$('#LoadList .mw-stat-progress').click(function() {
    // getNet();
});

$('#LoadList .mw-stat-value').hover(function() {
    var one, five, fifteen;
    var that = this;
    one = getCookie('one');
    five = getCookie('five');
    fifteen = getCookie('fifteen');
    var text = '最近1分钟平均负载：' + one + '</br>最近5分钟平均负载：' + five + '</br>最近15分钟平均负载：' + fifteen + '';
    layer.tips(text, that, { time: 0, tips: [1, '#999'] });
}, function() {
    layer.closeAll('tips');
});


function showCpuTips(rdata){
    $('#cpuChart .mask').unbind().hover(function() {
        var cpuText = '';
        if (rdata.cpu[2].length == 1){
            var cpuUse = parseFloat(rdata.cpu[2][0] == 0 ? 0 : rdata.cpu[2][0]).toFixed(1);
            cpuText += 'CPU-1：' + cpuUse + '%';
        } else {
            for (var i = 1; i < rdata.cpu[2].length + 1; i++) {
                var cpuUse = parseFloat(rdata.cpu[2][i - 1] == 0 ? 0 : rdata.cpu[2][i - 1]).toFixed(1);
                if (i % 2 != 0) {
                    cpuText += 'CPU-' + i + '：' + cpuUse + '%&nbsp;|&nbsp;';
                } else {
                    cpuText += 'CPU-' + i + '：' + cpuUse + '%';
                    cpuText += '\n';
                }
            } 
        }
        layer.tips(rdata.cpu[3] + "</br>" + rdata.cpu[5] + "个物理CPU，" + (rdata.cpu[4]) + "个物理核心，" + rdata.cpu[1] + "个逻辑核心</br>" + cpuText, this, { time: 0, tips: [1, '#999'] });
    }, function() {
        layer.closeAll('tips');
    });
}

function getChartTheme() {
    var styles = getComputedStyle(document.documentElement);
    function resolveCssVar(value) {
        if (!value) {
            return value;
        }
        var trimmed = value.trim();
        if (trimmed.indexOf('var(') !== 0) {
            return trimmed;
        }
        var match = trimmed.match(/var\((--[^,\s)]+)\s*(?:,\s*(.+))?\)/);
        if (!match) {
            return trimmed;
        }
        var resolved = styles.getPropertyValue(match[1]).trim();
        if (resolved) {
            return resolveCssVar(resolved);
        }
        if (match[2]) {
            return resolveCssVar(match[2].trim());
        }
        return trimmed;
    }
    return {
        primary: resolveCssVar(styles.getPropertyValue('--mw-primary')) || '#6750a4',
        secondary: resolveCssVar(styles.getPropertyValue('--mdui-color-secondary')) || '#4f8ef7',
        border: resolveCssVar(styles.getPropertyValue('--mw-border')) || '#e2e8f0',
        muted: resolveCssVar(styles.getPropertyValue('--mw-muted')) || '#64748b',
        surface: resolveCssVar(styles.getPropertyValue('--mw-surface')) || '#ffffff',
        text: resolveCssVar(styles.getPropertyValue('--mw-text')) || '#1f1f1f',
        surfaceContainer: resolveCssVar(styles.getPropertyValue('--mw-surface-container')) || '#f2f3f7'
    };
}

function updateLinearProgressValue(element, value, color) {
    if (!element) {
        return;
    }
    var safeValue = Math.max(0, Math.min(100, parseFloat(value) || 0));
    element.value = safeValue;
    element.setAttribute('value', safeValue);
    if (color) {
        element.style.setProperty('--mdui-color-primary', color);
    }
}

function escapeHtml(text) {
    return String(text || '')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

function renderNoteMarkdown(content) {
    var text = String(content || '').trim();
    if (!text) {
        return '';
    }
    if (window.marked && typeof window.marked.parse === 'function') {
        return window.marked.parse(text);
    }
    return escapeHtml(text).replace(/\n/g, '<br>');
}

function initNoteBoard() {
    var preview = $('#notePreview');
    if (!preview.length) {
        return;
    }
    var editor = $('#noteEditor');
    var input = $('#noteInput');
    var editButton = $('#noteEditBtn');
    var saveButton = $('#noteSaveBtn');
    var cancelButton = $('#noteCancelBtn');
    var storageKey = 'mw-note-board';
    var fallbackText = '## 欢迎使用便签\n\n- 支持 **Markdown** 语法\n- 记录维护事项、变更说明\n- 点击底部“编辑”开始编写';
    var storedText = '';
    try {
        storedText = localStorage.getItem(storageKey) || '';
    } catch (error) {
        storedText = '';
    }
    var currentText = storedText || fallbackText;

    function updatePreview(text) {
        var rendered = renderNoteMarkdown(text);
        if (!rendered) {
            preview.html('<p class="c9">暂无便签内容，点击“编辑”开始记录。</p>');
        } else {
            preview.html(rendered);
        }
    }

    function setEditMode(editing) {
        if (editing) {
            editor.removeClass('hide');
            preview.addClass('hide');
            editButton.addClass('hide');
        } else {
            editor.addClass('hide');
            preview.removeClass('hide');
            editButton.removeClass('hide');
        }
    }

    updatePreview(currentText);
    setEditMode(false);

    editButton.on('click', function () {
        input.val(currentText);
        setEditMode(true);
        input.trigger('focus');
    });

    saveButton.on('click', function () {
        var nextText = input.val();
        currentText = nextText;
        try {
            localStorage.setItem(storageKey, nextText);
        } catch (error) {
            console.warn('Failed to save note content', error);
        }
        updatePreview(currentText);
        setEditMode(false);
    });

    cancelButton.on('click', function () {
        setEditMode(false);
    });
}

function applyColorAlpha(color, alpha) {
    if (!color) {
        return 'rgba(0, 0, 0, ' + alpha + ')';
    }
    if (color.indexOf('rgb') === 0) {
        var numbers = color.replace(/[^\d,]/g, '').split(',');
        if (numbers.length >= 3) {
            return 'rgba(' + numbers[0] + ', ' + numbers[1] + ', ' + numbers[2] + ', ' + alpha + ')';
        }
    }
    if (color.indexOf('#') === 0) {
        var hex = color.replace('#', '');
        if (hex.length === 3) {
            hex = hex.split('').map(function (item) { return item + item; }).join('');
        }
        if (hex.length === 6) {
            var r = parseInt(hex.slice(0, 2), 16);
            var g = parseInt(hex.slice(2, 4), 16);
            var b = parseInt(hex.slice(4, 6), 16);
            return 'rgba(' + r + ', ' + g + ', ' + b + ', ' + alpha + ')';
        }
    }
    return color;
}

function initEchartWhenReady(elementId, option, onReady) {
    if (typeof echarts === 'undefined') {
        return null;
    }
    var element = document.getElementById(elementId);
    if (!element) {
        return null;
    }
    var attempt = 0;
    var maxAttempts = 30;
    var raf = window.requestAnimationFrame || function(callback) {
        return setTimeout(callback, 16);
    };
    function tryInit() {
        if (element.clientWidth === 0 || element.clientHeight === 0) {
            if (attempt++ < maxAttempts) {
                raf(tryInit);
            }
            return;
        }
        var chart = echarts.getInstanceByDom(element) || echarts.init(element);
        if (option) {
            chart.setOption(option);
        }
        if (onReady) {
            onReady(chart);
        }
    }
    tryInit();
    return null;
}


function rocket(sum, m) {
    var n = sum - m;
    $(".mem-release").find(".mask span").text(n);
}

//释放内存
function reMemory() {
    var memButton = $("#memReleaseBtn");
    memButton.prop("disabled", true);
    $("#memory").text(lan.index.memre_ok_0);
    $.post('/system/rememory', '', function(rdata) {
        var percent = getPercent(rdata.memRealUsed, rdata.memTotal);
        percent = Math.round(parseFloat(percent) || 0);
        var memText = Math.round(rdata.memRealUsed) + "/" + Math.round(rdata.memTotal) + " (MB)";
        var prevMemRealUsed = parseFloat(getCookie("memRealUsed")) || 0;
        setCookie("mem-before", memText);
        setCookie("memRealUsed", rdata.memRealUsed);
        $("#left").text(percent);
        var memColor = setcolor(percent, "#left", 75, 90, 95);
        updateLinearProgressValue(document.getElementById('MemProgress'), percent, memColor);
        var memNull = Math.round(prevMemRealUsed - rdata.memRealUsed);
        if (prevMemRealUsed > 0 && memNull > 0) {
            $("#memory").text(lan.index.memre_ok_1 + " " + memNull + "MB");
        } else {
            $("#memory").text(lan.index.memre_ok_2);
        }
        $(".mem-release").removeClass("mem-action");
        memButton.prop("disabled", false);
    },'json').fail(function() {
        $(".mem-release").removeClass("mem-action");
        $("#memory").text(lan.index.memre_ok_2);
        memButton.prop("disabled", false);
    });
}

function getPercent(num, total) {
    num = parseFloat(num);
    total = parseFloat(total);
    if (isNaN(num) || isNaN(total)) {
        return "-";
    }
    return total <= 0 ? "0%" : (Math.round(num / total * 10000) / 100.00);
}

function getDiskInfo() {
    $.get('/system/disk_info', function(rdata) {
        var rdata = rdata.data;
        var dBody;
        for (var i = 0; i < rdata.length; i++) {
            var usagePercent = parseInt(rdata[i].size[3].replace('%', ''));
            var LoadColor = setcolor(usagePercent, false, 75, 90, 95);

            //判断inode信息是否存在
            var inodes = '';
            if ( typeof(rdata[i]['inodes']) !=='undefined' ){
                inodes = ' data="Inode信息<br>总数：' + rdata[i].inodes[0] + '<br>已使用：' + rdata[i].inodes[1] + '<br>可用：' + rdata[i].inodes[2] + '<br>Inode使用率：' + rdata[i].inodes[3] + '"';

                var ipre = parseInt(rdata[i].inodes[3].replace('%', ''));
                if (ipre > 95) {
                    $("#messageError").show();
                    $("#messageError").append('<p><span class="glyphicon glyphicon-alert" style="color: #ff4040; margin-right: 10px;"></span>分区[' + rdata[i].path + ']当前Inode使用率超过' + ipre + '%，当使用率满100%时将无法在此分区创建文件，请及时清理!<a class="btlink" href="javascript:ClearSystem();">[清理垃圾]</a></p>');
                }
            }

            if (rdata[i].path == '/' || rdata[i].path == '/www') {
                if (rdata[i].size[2].indexOf('M') != -1) {
                    $("#messageError").show();
                    $("#messageError").append('<p><span class="glyphicon glyphicon-alert" style="color: #ff4040; margin-right: 10px;"></span> ' + lan.get('diskinfo_span_1', [rdata[i].path]) + '<a class="btlink" href="javascript:ClearSystem();">[清理垃圾]</a></p>');
                } 
            }
           
            dBody = '<li class="col-xs-6 col-sm-3 col-md-3 col-lg-2 mtb20 circle-box mw-stat-item diskbox">' +
                '<h3 class="c5 f15">' + rdata[i].path + '</h3>' +
                '<div class="mw-stat-progress mw-disk-progress">' +
                '<mdui-linear-progress max="100" value="' + usagePercent + '" style="--mdui-color-primary: ' + LoadColor + ';"></mdui-linear-progress>' +
                '</div>' +
                '<div class="mw-stat-value mask" style="color:' + LoadColor + '"' + inodes + '><span>' + usagePercent + '</span>%</div>' +
                '<h4 class="c5 f15">' + rdata[i].size[1] + '/' + rdata[i].size[0] + '</h4>' +
                '</li>'
            $("#systemInfoList").append(dBody);
        }
        setImg();
    },'json');
}

//清理垃圾
function clearSystem() {
    var loadT = layer.msg('正在清理系统垃圾 <img src="/static/img/ing.gif">', { icon: 16, time: 0, shade: [0.3, "#000"] });
    $.get('/system?action=ClearSystem', function(rdata) {
        layer.close(loadT);
        layer.msg('清理完成,共清理[' + rdata[0] + ']个文件,释放[' + toSize(rdata[1]) + ']磁盘空间!', { icon: 1 });
    });
}

function setMemImg(info){

    var memRealUsedBytes = parseFloat(info.memRealUsed) || 0;
    var memTotalBytes = parseFloat(info.memTotal) || 0;
    var gbBytes = 1024 * 1024 * 1024;
    var memRealUsedVal;
    var memTotalVal;
    var unit;
    if (memRealUsedBytes < gbBytes) {
        memRealUsedVal = (memRealUsedBytes / 1024 / 1024).toFixed(2);
        memTotalVal = (memTotalBytes / 1024 / 1024).toFixed(2);
        unit = 'MB';
    } else {
        memRealUsedVal = (memRealUsedBytes / gbBytes).toFixed(2);
        memTotalVal = (memTotalBytes / gbBytes).toFixed(2);
        unit = 'GB';
    }

    var mem_txt = memRealUsedVal + '/' + memTotalVal + ' ('+ unit +')';
    setCookie("mem-before", mem_txt);
    $("#memory").html(mem_txt);

    var memPre = Math.floor(info.memRealUsed / (info.memTotal / 100));
    $("#left").html(memPre);
    var memColor = setcolor(memPre, "#left", 75, 90, 95);
    updateLinearProgressValue(document.getElementById('MemProgress'), memPre, memColor);

    var memFree = info.memTotal - info.memRealUsed;
    if (memFree/(1024*1024) < 64) {
        $("#messageError").show();
        $("#messageError").append('<p><span class="glyphicon glyphicon-alert" style="color: #ff4040; margin-right: 10px;">当前可用物理内存小于64M，这可能导致MySQL自动停止，站点502等错误，请尝试释放内存！</span></p>')
    }
}

function getInfo() {
    $.get("/system/system_total", function(info) {

        setMemImg(info);

        $("#info").html(info.system);
        $("#running").html(info.time);
        var _system = info.system;
        if(_system.indexOf("Windows") != -1){
            $(".ico-system").addClass("ico-windows");
        } else if(_system.indexOf("CentOS") != -1) {
            $(".ico-system").addClass("ico-centos");
        } else if(_system.indexOf("Ubuntu") != -1) {
            $(".ico-system").addClass("ico-ubuntu");
        } else if(_system.indexOf("Debian") != -1) {
            $(".ico-system").addClass("ico-debian");
        } else if(_system.indexOf("Fedora") != -1) {
            $(".ico-system").addClass("ico-fedora");
        } else if(_system.indexOf("Mac") != -1){
            $(".ico-system").addClass("ico-mac");
        } else {
            $(".ico-system").addClass("ico-linux");
        }
        $("#core").html(info.cpuNum + ' 核心');
        $("#state").html(info.cpuRealUsed);
        var cpuColor = setcolor(info.cpuRealUsed, "#state", 30, 70, 90);
        updateLinearProgressValue(document.getElementById('CpuProgress'), info.cpuRealUsed, cpuColor);
       

        // if (info.isuser > 0) {
        //     $("#messageError").show();
        //     $("#messageError").append('<p><span class="glyphicon glyphicon-alert" style="color: #ff4040; margin-right: 10px;"></span>' + lan.index.user_warning + '<span class="c7 mr5" title="此安全问题不可忽略，请尽快处理" style="cursor:no-drop"> [不可忽略]</span><a class="btlink" href="javascript:setUserName();"> [立即修改]</a></p>')
        // }
        setImg();
    },'json');
}


function setcolor(pre, s, s1, s2, s3) {
    var value = parseFloat(pre);
    if (isNaN(value)) {
        value = 0;
    }
    var LoadColor;
    if (value <= s1) {
        LoadColor = '#20a53a';
    } else if (value <= s2) {
        LoadColor = '#6ea520';
    } else if (value <= s3) {
        LoadColor = '#ff9900';
    } else {
        LoadColor = '#dd2f00';
    }
    if (s == false) {
        return LoadColor;
    }
    var co = $(s).closest('.mask');
    co.css("color", LoadColor);
    var item = co.closest('.mw-stat-item');
    var progressElement = item.find('mdui-linear-progress').get(0);
    updateLinearProgressValue(progressElement, value, LoadColor);
    return LoadColor;
}


function getNet() {
    var up, down;
    $.get("/system/network", function(net) {

        console.log(net);

        $("#InterfaceSpeed").html(lan.index.interfacespeed + "： 1.0Gbps");
        $("#upSpeed").html(toSize(net.up));
        $("#downSpeed").html(toSize(net.down));
        $("#downAll").html(toSize(net.downTotal));
        $("#downAll").attr('title', lan.index.package + ':' + net.downPackets)
        $("#upAll").html(toSize(net.upTotal));
        $("#upAll").attr('title', lan.index.package + ':' + net.upPackets)
        $("#core").html(net.cpu[1] + " " + lan.index.cpu_core);
        $("#state").html(net.cpu[0]);
        var cpuColor = setcolor(net.cpu[0], "#state", 30, 70, 90);
        updateLinearProgressValue(document.getElementById('CpuProgress'), net.cpu[0], cpuColor);
        setCookie("upNet", net.up);
        setCookie("downNet", net.down);

        //负载
        getLoad(net.load);

        //内存
        setMemImg(net.mem);

        //绑定hover事件
        setImg();
        showCpuTips(net);

    },'json');
}

//网络IO
function netImg() {
    
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

    var default_unit = 'KB/s';
    function addData(shift) {
        xData.push(getTime());

        if (getCookie("upNet") > getCookie("downNet") ){
            tmp = getCookie("upNet");
        } else {
            tmp = getCookie("downNet");
        }
        var tmpSize = toSize(tmp);
        default_unit = tmpSize.split(' ')[1] + '/s';


        var upNetTmp = toSize(getCookie("upNet"));
        var downNetTmp = toSize(getCookie("downNet"));
        
        var upNetTmpSize = upNetTmp.split(' ')[0];
        var downNetTmp = downNetTmp.split(' ')[0];
        
        yData.push(upNetTmpSize);
        zData.push(downNetTmp);
        if (shift) {
            xData.shift();
            yData.shift();
            zData.shift();
        }
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
            text: "接口流量实时",
            left: 'center',
            textStyle: {
                color: '#888888',
                fontStyle: 'normal',
                fontFamily: "宋体",
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
            name:  '单位 '+ default_unit,
            splitLine: {
                lineStyle: { color: "#eee" }
            },
            axisLine: {
                lineStyle: { color: "#666" }
            }
        },
        series: [{
            name: '上行',
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
        },
        {
            name: '下行',
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
                        color: 'rgba(30, 144, 255,0.5)',
                    }, {
                        offset: 1,
                        color: 'rgba(30, 144, 255,0.8)',
                    }], false)
                }
            },
            itemStyle: {
                normal: {
                    color: '#52a9ff',
                }
            },
            lineStyle: {
                normal: {
                    width: 1,
                }
            }
        }]
    };

    var echartsNetImg = echarts.init(document.getElementById('netImg'));
    setInterval(function() {
        getNet();
        addData(true);
        echartsNetImg.setOption({
            yAxis: {
                name:  '单位 '+ default_unit,
                splitLine: { lineStyle: { color: "#eee" } },
                axisLine: { lineStyle: { color: "#666" } }
            },
            xAxis: {
                data: xData
            },
            series: [{
                name: lan.index.net_up,
                data: yData
            }, {
                name: lan.index.net_down,
                data: zData
            }]
        });
    }, 3000);

    // 使用刚指定的配置项和数据显示图表。
    echartsNetImg.setOption(option);
    window.addEventListener("resize", function() {
        echartsNetImg.resize();
    });
}


function setImg() {
    $('.circle').each(function(index, el) {
        var num = $(this).find('span').text() * 3.6;
        if (num <= 180) {
            $(this).find('.left').css('transform', "rotate(0deg)");
            $(this).find('.right').css('transform', "rotate(" + num + "deg)");
        } else {
            $(this).find('.right').css('transform', "rotate(180deg)");
            $(this).find('.left').css('transform', "rotate(" + (num - 180) + "deg)");
        };
    });

    $('.diskbox .mask').unbind().hover(function() {
        layer.closeAll('tips');
        var that = this;
        var conterError = $(this).attr("data");
        layer.tips(conterError, that, { time: 0, tips: [1, '#999'] });
    }, function() {
        layer.closeAll('tips');
    });
}

// 检查更新
setTimeout(function() {
    $.get('/system/update_server?type=check', function(rdata) {
        if (rdata.status == false) return;
        if (rdata.data != undefined) {
            $("#toUpdate").html('<a class="btlink" href="javascript:updateMsg();">更新</a>');
            $('#toUpdate a').html('更新<i style="display: inline-block; color: red; font-size: 40px;position: absolute;top: -35px; font-style: normal; right: -8px;">.</i>');
            $('#toUpdate a').css("position","relative");
            return;
        }
    },'json').error(function() {
    });
}, 3000);


//检查更新
function checkUpdate() {
    var loadT = layer.msg(lan.index.update_get, { icon: 16, time: 0, shade: [0.3, '#000'] });
    $.get('/system/update_server?type=check', function(rdata) {
        layer.close(loadT);

        if (rdata.data == 'download'){
            updateStatus();return;
        }

        if (rdata.status === false) {
            layer.confirm(rdata.msg, { title: lan.index.update_check, icon: 1, closeBtn: 1, btn: [lan.public.know, lan.public.close] });
            return;
        }
        layer.msg(rdata.msg, { icon: 1 });
        if (rdata.data != undefined) updateMsg();
    },'json');
}

function updateMsg(){
    $.get('/system/update_server?type=info',function(rdata){

        if (rdata.data == 'download'){
            updateStatus();return;
        }

        var v = rdata.data.version;
        var v_info = '';
        if (v.split('.').length>3){
            v_info = "<span class='label label-warning'>测试版本</span>";
        } else {
            v_info = "<span class='label label-success arrowed'>正式版本</span>";
        }

        layer.open({
            type:1,
            title:v_info + '<span class="badge badge-inverse">升级到['+rdata.data.version+']</span>',
            area: '400px', 
            shadeClose:false,
            closeBtn:2,
            content:'<div class="setchmod bt-form pd20 pb70">'
                    +'<p style="padding: 0 0 10px;line-height: 24px;">'+rdata.data.content+'</p>'
                    +'<div class="bt-form-submit-btn">'
                    +'<button type="button" class="btn btn-danger btn-sm btn-title" onclick="layer.closeAll()">取消</button>'
                    +'<button type="button" class="btn btn-success btn-sm btn-title" onclick="updateVersion(\''+rdata.data.version+'\')" >立即更新</button>'
                    +'</div>'
                    +'</div>'
        });
    },'json');
}


//开始升级
function updateVersion(version) {
    var loadT = layer.msg('正在升级面板..', { icon: 16, time: 0, shade: [0.3, '#000'] });
    $.get('/system/update_server?type=update&version='+version, function(rdata) {

        layer.closeAll();
        if (rdata.status === false) {
            layer.msg(rdata.msg, { icon: 5, time: 5000 });
            return;
        }
        layer.msg(rdata.msg, { icon: rdata.status ? 1 : 2 });
        if (rdata.status) {
            $("#btversion").html(version);
            $("#toUpdate").html('');
        }
    },'json').error(function() {
        layer.msg('更新失败,请重试!', { icon: 2 });
        setTimeout(function() {
            window.location.reload();
        }, 3000);
    });
}

function pluginIndexService(pname,pfunc, callback){
    $.post('/plugins/run', {name:'openresty', func:pfunc}, function(data) {
        if (!data.status){
            layer.msg(data.msg,{icon:0,time:2000,shade: [0.3, '#000']});
            return;
        }

        if(typeof(callback) == 'function'){
            callback(data);
        }
    },'json'); 
}

//重启服务器
function reBoot() {
    layer.open({
        type: 1,
        title: '重启服务器或者面板',
        area: '330px',
        closeBtn: 1,
        shadeClose: false,
        content: '<div class="rebt-con">\
                <div class="rebt-li"><a data-id="server" href="javascript:;">重启服务器</a></div>\
                <div class="rebt-li"><a data-id="panel" href="javascript:;">重启面板</a></div>\
            </div>'
    });

    $('.rebt-con a').click(function () {
        var type = $(this).attr('data-id');
        switch (type) {
            case 'panel':
                layer.confirm('即将重启面板服务，继续吗？', { title: '重启面板服务', closeBtn: 1, icon: 3 }, function () {
                    var loadT = layer.load();
                    $.post('/system/restart','',function (rdata) {
                        layer.close(loadT);
                        layer.msg(rdata.msg);
                        setTimeout(function () { window.location.reload(); }, 3000);
                    },'json');
                });
                break;
            case 'server':
                var rebootbox = layer.open({
                    type: 1,
                    title: '安全重启服务器',
                    area: ['500px', '280px'],
                    closeBtn: 1,
                    shadeClose: false,
                    content: "<div class='bt-form bt-window-restart'>\
                            <div class='pd15'>\
                            <p style='color:red; margin-bottom:10px; font-size:15px;'>注意，若您的服务器是一个容器，请取消。</p>\
                            <div class='SafeRestart' style='line-height:26px'>\
                                <p>安全重启有利于保障文件安全，将执行以下操作：</p>\
                                <p>1.停止Web服务</p>\
                                <p>2.停止MySQL服务</p>\
                                <p>3.开始重启服务器</p>\
                                <p>4.等待服务器启动</p>\
                            </div>\
                            </div>\
                            <div class='bt-form-submit-btn'>\
                                <button type='button' class='btn btn-danger btn-sm btn-reboot'>取消</button>\
                                <button type='button' class='btn btn-success btn-sm WSafeRestart' >确定</button>\
                            </div>\
                        </div>"
                });
                setTimeout(function () {
                    $(".btn-reboot").click(function () {
                        rebootbox.close();
                    })
                    $(".WSafeRestart").click(function () {
                        var body = '<div class="SafeRestartCode pd15" style="line-height:26px"></div>';
                        $(".bt-window-restart").html(body);
                        $(".SafeRestartCode").append("<p>正在停止Web服务</p>");
                        pluginIndexService('openresty', 'stop', function (r1) {
                            $(".SafeRestartCode p").addClass('c9');
                            $(".SafeRestartCode").append("<p>正在停止MySQL服务...</p>");
                            pluginIndexService('mysql','stop', function (r2) {
                                $(".SafeRestartCode p").addClass('c9');
                                $(".SafeRestartCode").append("<p>开始重启服务器...</p>");
                                $.post('/system/restart_server', '',function (rdata) {
                                    $(".SafeRestartCode p").addClass('c9');
                                    $(".SafeRestartCode").append("<p>等待服务器启动...</p>");
                                    var sEver = setInterval(function () {
                                       $.get("/system/system_total", function(info) {
                                            clearInterval(sEver);
                                            $(".SafeRestartCode p").addClass('c9');
                                            $(".SafeRestartCode").append("<p>服务器重启成功!...</p>");
                                            setTimeout(function () {
                                                layer.closeAll();
                                            }, 3000);
                                        })
                                    }, 3000);
                                })
                            })
                        })
                    })
                }, 100);
                break;
        }
    });
}

//关机服务器
function shutdownServer() {
    layer.confirm('确定要关闭服务器吗？此操作将会停止所有服务。', { title: '关机确认', closeBtn: 1, icon: 3 }, function () {
        var loadT = layer.load();
        $.post('/system/shutdown_server', '', function (rdata) {
            layer.close(loadT);
            layer.msg(rdata.msg, { icon: rdata.status ? 1 : 2 });
        }, 'json').error(function () {
            layer.close(loadT);
            layer.msg('关机请求失败，请重试。', { icon: 2 });
        });
    });
}

var __vipCountdownTimer = null;

function formatVipRemain(seconds) {
    if (seconds <= 0) {
        return '永久有效';
    }
    var day = Math.floor(seconds / 86400);
    var hour = Math.floor((seconds % 86400) / 3600);
    var minute = Math.floor((seconds % 3600) / 60);
    var second = Math.floor(seconds % 60);
    return day + '天 ' + hour + '小时 ' + minute + '分钟 ' + second + '秒';
}

function showVipInfo() {
    var expireAt = new Date('2038-01-19T03:14:07+08:00').getTime();
    var content = '<div class="pd20" style="line-height:1.9;">' +
        '<div style="font-size:18px;font-weight:600;color:#20a53a;">PowerLinux Pro Max · 永久尊享</div>' +
        '<div style="margin-top:8px;color:#666;">您已经是永久VIP，感谢长期支持。</div>' +
        '<hr style="margin:12px 0;">' +
        '<div><b>会员到期时间：</b>2038年1月19日03:14:07</div>' +
        '<div><b>剩余时长：</b><span id="vipRemainTime">计算中...</span></div>' +
        '<hr style="margin:12px 0;">' +
        '<div><b>会员权益</b></div>' +
        '<ul style="margin:8px 0 0 18px;padding:0;">' +
        '<li>无限期面板更新（优先体验新版能力）</li>' +
        '<li>高级监控与可视化页面持续增强</li>' +
        '<li>社区身份标识与优先反馈通道</li>' +
        '<li>长期稳定版本与性能优化补丁</li>' +
        '</ul>' +
        '<div style="margin-top:10px;color:#999;font-size:12px;">提示：剩余时长将实时刷新显示。</div>' +
        '</div>';

    layer.open({
        type: 1,
        title: 'Pro Max会员信息',
        area: ['520px', '430px'],
        closeBtn: 1,
        icon: 1,
        content: content,
        success: function () {
            if (__vipCountdownTimer) {
                clearInterval(__vipCountdownTimer);
                __vipCountdownTimer = null;
            }
            function tick() {
                var now = Date.now();
                var left = Math.max(0, Math.floor((expireAt - now) / 1000));
                var remain = formatVipRemain(left);
                $('#vipRemainTime').text(remain);
            }
            tick();
            __vipCountdownTimer = setInterval(tick, 1000);
        },
        end: function () {
            if (__vipCountdownTimer) {
                clearInterval(__vipCountdownTimer);
                __vipCountdownTimer = null;
            }
        }
    });
}

//修复面板
function repPanel() {
    layer.confirm(lan.index.rep_panel_msg, { title: lan.index.rep_panel_title, closeBtn: 1, icon: 3 }, function() {
        var loadT = layer.msg(lan.index.rep_panel_the, { icon: 16, time: 0, shade: [0.3, '#000'] });
        $.get('/system?action=RepPanel', function(rdata) {
            layer.close(loadT);
            layer.msg(lan.index.rep_panel_ok, { icon: 1 });
        }).error(function() {
            layer.close(loadT);
            layer.msg(lan.index.rep_panel_ok, { icon: 1 });
        });
    });
}

//获取警告信息
function getWarning() {
    $.get('/ajax?action=GetWarning', function(wlist) {
        var num = 0;
        for (var i = 0; i < wlist.data.length; i++) {
            if (wlist.data[i].ignore_count >= wlist.data[i].ignore_limit) continue;
            if (wlist.data[i].ignore_time != 0 && (wlist.time - wlist.data[i].ignore_time) < wlist.data[i].ignore_timeout) continue;
            var btns = '';
            for (var n = 0; n < wlist.data[i].btns.length; n++) {
                if (wlist.data[i].btns[n].type == 'javascript') {
                    btns += '<a href="javascript:WarningTo(\'' + wlist.data[i].btns[n].url + '\',' + wlist.data[i].btns[n].reload + ');" class="' + wlist.data[i].btns[n].class + '"> ' + wlist.data[i].btns[n].title + '</a>'
                } else {
                    btns += '<a href="' + wlist.data[i].btns[n].url + '" class="' + wlist.data[i].btns[n].class + '" target="' + wlist.data[i].btns[n].target + '"> ' + wlist.data[i].btns[n].title + '</a>'
                }
            }
            $("#messageError").append('<p><img src="' + wlist.icon[wlist.data[i].icon] + '" style="margin-right:14px;vertical-align:-3px">' + wlist.data[i].body + btns + '</p>');
            num++;
        }
        if (num > 0) $("#messageError").show();
    });
}

//按钮调用
function warningTo(to_url, def) {
    var loadT = layer.msg(lan.public.the_get, { icon: 16, time: 0, shade: [0.3, '#000'] });
    $.post(to_url, {}, function(rdata) {
        layer.close(loadT);
        layer.msg(rdata.msg, { icon: rdata.status ? 1 : 2 });
        if (rdata.status && def) setTimeout(function() { location.reload(); }, 1000);
    },'json');
}

function setSafeHide() {
    setCookie('safeMsg', '1');
    $("#safeMsg").remove();
}

//查看报告
function showDanger(num, port) {
    var atxt = "因未使用安全隔离登录，所有IP都可以尝试连接，存在较高风险，请立即处理。";
    if (port == "22") {
        atxt = "因未修改SSH默认22端口，且未使用安全隔离登录，所有IP都可以尝试连接，存在较高风险，请立即处理。";
    }
    layer.open({
        type: 1,
        area: ['720px', '410px'],
        title: '安全提醒(如你想放弃任何安全提醒通知，请删除宝塔安全登录插件)',
        closeBtn: 1,
        shift: 5,
        content: '<div class="pd20">\
                <table class="f14 showDanger">\
                    <tbody>\
                    <tr><td class="text-right" width="150">风险类型：</td><td class="f16" style="color:red">暴力破解 <a href="https://www.bt.cn/bbs/thread-9562-1-1.html" class="btlink f14" style="margin-left:10px" target="_blank">说明</a></td></tr>\
                    <tr><td class="text-right">累计遭遇攻击总数：</td><td class="f16" style="color:red">' + num + ' <a href="javascript:showDangerIP();" class="btlink f14" style="margin-left:10px">详细</a><span class="c9 f12" style="margin-left:10px">（数据直接来源本服务器日志）</span></td></tr>\
                    <tr><td class="text-right">风险等级：</td><td class="f16" style="color:red">较高风险</td></tr>\
                    <tr><td class="text-right" style="vertical-align:top">风险描述：</td><td style="line-height:20px">' + atxt + '</td></tr>\
                    <tr><td class="text-right" style="vertical-align:top">可参考解决方案：</td><td><p style="margin-bottom:8px">方案一：修改SSH默认端口，修改SSH验证方式为数字证书，清除近期登陆日志。</p><p>方案二：购买宝塔企业运维版，一键部署安全隔离服务，高效且方便。</p></td></tr>\
                    </tbody>\
                </table>\
            </div>'
    });
    $(".showDanger td").css("padding", "8px");
}

function pluginInit(){
    $.post('/plugins/init', function(data){
        if (!data.status){
            return false;
        }

        var rdata = data.data;
        var plugin_list = '';

        for (var i = 0; i < rdata.length; i++) {
            var ver = rdata[i]['versions'];
            var select_list = '';
            if (typeof(ver)=='string'){
                select_list = '<option value="' + ver +'">' + rdata[i]['title'] + ' - ' + ver + '</option>';
            } else {
                for (var vi = 0; vi < ver.length; vi++) {

                    if (ver[vi] == rdata[i]['default_ver']){
                        select_list += '<option value="'+ver[vi]+'" selected="selected">'+ rdata[i]['title'] + ' - '+ ver[vi] + '</option>';
                    } else {
                        select_list += '<option value="'+ver[vi]+'">'+ rdata[i]['title'] + ' - '+ ver[vi] + '</option>';
                    }
                }
            }

            var pn_checked = '<input id="data_'+rdata[i]['name']+'" type="checkbox" checked>';
            if (rdata[i]['name'] == 'swap'){
                var pn_checked = '<input id="data_'+rdata[i]['name']+'" type="checkbox" disabled="disabled" checked>';
            }
            
            plugin_list += '<li><span class="ico"><img src="/plugins/file?name='+rdata[i]['name']+'&f=ico.png"></span>\
            <span class="name">\
                <select id="select_'+rdata[i]['name']+'" class="sl-s-info">'+select_list+'</select>\
            </span>\
            <span class="pull-right">'+pn_checked+'</span></li>';
        }

        layer.open({
            type: 1,
            title: '推荐安装',
            area: ["320px", "400px"],
            closeBtn: 2,
            shadeClose: false,
            content:"\
        <div class='rec-install'>\
            <div class='important-title'>\
                <p><span class='glyphicon glyphicon-alert' style='color: #f39c12; margin-right: 10px;'></span>推荐以下一键套件，或在<a href='javascript:jump()' style='color:#20a53a'>软件管理</a>按需选择。</p>\
                <!-- <button style='margin-top: 8px;height: 30px;' type='button' class='btn btn-sm btn-default no-show-rec-btn'>不再显示推荐</button> -->\
            </div>\
            <div class='rec-box'>\
                <h3 style='text-align: center'>经典LNMP</h3>\
                <div class='rec-box-con'>\
                    <ul class='rec-list'>" + plugin_list + "</ul>\
                    <div class='onekey'>一键安装</div>\
                </div>\
            </div>\
        </div>",
            success:function(l,index){
                $('.rec-box-con .onekey').click(function(){
                    var post_data = [];
                    for (var i = 0; i < rdata.length; i++) {
                        var key_ver = '#select_'+rdata[i]['name'];
                        var key_checked = '#data_'+rdata[i]['name'];

                        var val_checked = $(key_checked).prop("checked");
                        if (val_checked){

                            var tmp = {};
                            var val_key = $(key_ver).val();

                            tmp['version'] = val_key;
                            tmp['name'] = rdata[i]['name'];
                            post_data.push(tmp);
                        }
                    }

                    $.post('/plugins/init_install', 'list='+JSON.stringify(post_data), function(data){
                        showMsg(data.msg, function(){
                            if (data.status){
                                layer.closeAll();
                                messageBox();
                            }
                        },{ icon: data.status ? 1 : 2 },2000);
                    },'json');
                });   
            },
            cancel:function(){
                layer.confirm('是否不再显示推荐安装套件?', {btn : ['确定', '取消'],title: "不再显示推荐?"}, function() {
                    $.post('/files/create_dir', 'path=/www/server/php', function(rdata) {
                        layer.closeAll();
                    },'json');
                });
            }
        });
    },'json');
}

function appendOverviewItem(name, value, href, onclick) {
    var linkStart = '<span>';
    var linkEnd = '</span>';
    if (onclick) {
        linkStart = '<a class="btlink" href="javascript:;" onclick="' + onclick.replace(/"/g, '&quot;') + '">';
        linkEnd = '</a>';
    } else if (href) {
        linkStart = '<a class="btlink" href="' + href + '">';
        linkEnd = '</a>';
    }

    var html = '<li class="sys-li-box mw-overview-item mw-overview-dynamic">' +
        '<p class="name f15 c9">' + name + '</p>' +
        '<div class="val">' + linkStart + value + linkEnd + '</div>' +
        '</li>';
    $('#index_overview').append(html);
}

function loadOverviewSystemStats() {
    $.get('/overview_stats', function(res) {
        if (!res || !res.status || !res.data) {
            return;
        }

        var data = res.data;
        if ($('#overview_site_count').length) {
            $('#overview_site_count').text(data.site_count);
        }

        appendOverviewItem('数据库', '<span id="overview_db_total">0</span>', null, null);
        appendOverviewItem('Docker容器', '<span id="overview_docker_total">0</span>', null, null);
        appendOverviewItem('待执行任务', data.pending_task_count, '/task/index');
        appendOverviewItem('计划任务', data.crontab_count, '/crontab/index');
        appendOverviewItem('防火墙规则', data.firewall_count, '/firewall/index');
        appendOverviewItem('应用', data.enabled_app_count, '/setting/index');
    }, 'json');
}

function loadOverviewDatabaseStats() {
    var dbPlugins = ['mysql', 'pgsql', 'mongodb'];
    var total = 0;
    var done = 0;

    function flushDbTotal() {
        if ($('#overview_db_total').length) {
            $('#overview_db_total').text(total);
        }
    }

    if (dbPlugins.length === 0) {
        flushDbTotal();
    }

    for (var i = 0; i < dbPlugins.length; i++) {
        (function(pname) {
            $.post('/plugins/run', {name: pname, func: 'get_total_statistics'}, function(data) {
                var rdata;
                try {
                    rdata = $.parseJSON(data['data']);
                } catch(e) {
                    done++;
                    if (done >= dbPlugins.length) flushDbTotal();
                    return;
                }

                if (rdata && rdata['status'] && rdata['data']) {
                    var count = Number(rdata['data']['count'] || 0);
                    if (!isNaN(count) && count > 0) {
                        total += count;
                    }
                }

                done++;
                if (done >= dbPlugins.length) {
                    flushDbTotal();
                }
            }, 'json').error(function() {
                done++;
                if (done >= dbPlugins.length) flushDbTotal();
            });
        })(dbPlugins[i]);
    }

    // Docker 容器数量（未安装插件或读取失败时保持 0）
    $.post('/plugins/run', {name: 'docker', func: 'get_total_statistics'}, function(data) {
        var dockerCount = 0;
        try {
            var rdata = $.parseJSON(data['data']);
            if (rdata && rdata['status'] && rdata['data']) {
                dockerCount = Number(rdata['data']['count'] || 0);
                if (isNaN(dockerCount) || dockerCount < 0) {
                    dockerCount = 0;
                }
            }
        } catch(e) {}

        if ($('#overview_docker_total').length) {
            $('#overview_docker_total').text(dockerCount);
        }
    }, 'json').error(function() {
        if ($('#overview_docker_total').length) {
            $('#overview_docker_total').text(0);
        }
    });
}

function loadKeyDataCount(){
    $('#index_overview .mw-overview-dynamic').remove();
    loadOverviewSystemStats();
    loadOverviewDatabaseStats();
}


$(function() {
    $("#memReleaseBtn").on("click", function() {
        if ($(".mem-release").hasClass("mem-action")) {
            return;
        }
        $(".mem-release").addClass("mem-action");
        reMemory();
    });

    $("select[name='network-io'],select[name='disk-io']").change(function () {
        var key = $(this).val(), type = $(this).attr('name');
        if (type == 'network-io') {
            if (key == 'ALL') {
                key = '';
            }
            setCookie('network_io_key', key);
        } else {
            if (key == 'ALL') {
                key = '';
            }
            setCookie('disk_io_key', key);
        }
    });

    $('.tabs-nav span').click(function () {
        var indexs = $(this).index();
        $(this).addClass('active').siblings().removeClass('active');
        $('.tabs-content .tabs-item:eq(' + indexs + ')').addClass('tabs-active').siblings().removeClass('tabs-active');
        $('.tabs-down select:eq(' + indexs + ')').removeClass('hide').siblings().addClass('hide');
        switch (indexs) {
        case 0:
          if (index.net.table) {
              index.net.table.resize();
          }
          break;
        case 1:
          if (index.iostat.table) {
              index.iostat.table.resize();
          }
          break;
        }
    })
});

var index = {
    common:{
        ts:function (m) { return m < 10 ? '0' + m : m },
        format:function (sjc) {
            var time = new Date(sjc);
            var h = time.getHours();
            var mm = time.getMinutes();
            var s = time.getSeconds();
            return h+ ':' + mm + ':' +s;
        },
        getTime:function () {
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
        },
    },
    net: {
        table: null,
        data: {
          xData: [],
          yData: [],
          zData: []
        },
        default_unit : 'KB/s',
        init_select : false,
        init: function(){
            for (var i = 8; i >= 0; i--) {
                var time = (new Date()).getTime();
                index.net.data.xData.push(index.common.format(time - (i * 3 * 1000)));
                index.net.data.yData.push(0);
                index.net.data.zData.push(0);
            }

            var option = index.net.defaultOption();
            initEchartWhenReady('netImg', option, function (chart) {
                index.net.table = chart;
                window.addEventListener("resize", function () {
                    if (index.net.table) {
                        index.net.table.resize();
                    }
                });
            });
        },
        render:function(){
            if (!index.net.table) {
                return;
            }
            var theme = getChartTheme();
            index.net.table.setOption({
                yAxis: {
                    name:  '单位 '+ index.net.default_unit,
                    splitLine: { lineStyle: { color: theme.border } },
                    axisLine: { lineStyle: { color: theme.border } },
                    axisLabel: { color: theme.muted }
                },
                xAxis: {
                    data: index.net.data.xData,
                    axisLine: { lineStyle: { color: theme.border } },
                    axisLabel: { color: theme.muted }
                },
                series: [{
                    name: lan.index.net_up,
                    data: index.net.data.yData
                }, {
                    name: lan.index.net_down,
                    data: index.net.data.zData
                }]
            });
        },
        defaultOption:function(){
            var theme = getChartTheme();
            var option = {
                backgroundColor: theme.surfaceContainer,
                color: [theme.primary, theme.secondary],
                title: {
                    text: "",
                    left: 'center',
                    textStyle: {
                        color: theme.muted,
                        fontStyle: 'normal',
                        fontFamily: "Inter, PingFang SC, Microsoft YaHei, sans-serif",
                        fontSize: 14
                    }
                },
                tooltip: {
                    trigger: 'axis',
                    backgroundColor: theme.surface,
                    borderColor: theme.border,
                    textStyle: { color: theme.text },
                    extraCssText: 'box-shadow: 0 12px 28px rgba(15, 23, 42, 0.12); border-radius: 12px; padding: 10px;',
                    axisPointer: {
                        type: 'line',
                        lineStyle: { color: theme.border }
                    },
                    formatter :function (config) {
                        var _config = config, _tips = "时间：" + _config[0].axisValue + "<br />";
                        for (var i = 0; i < config.length; i++) {
                            if (typeof config[i].data == "undefined") {
                                return false;
                            }
                            _tips += '<span style="display: inline-block;width: 10px;height: 10px;border-radius: 50%;background: ' + config[i].color + ';"></span>&nbsp;&nbsp;<span>' + config[i].seriesName + '：' + config[i].data + ' '+ index.net.default_unit + '</span><br />'
                        }
                        return _tips;
                    }

                },
                legend: {
                    data: [lan.index.net_up, lan.index.net_down],
                    bottom: '2%',
                    textStyle: { color: theme.muted }
                },
                grid: {
                    left: '2%',
                    right: '3%',
                    bottom: '15%',
                    containLabel: true
                },
                xAxis: {
                    type: 'category',
                    boundaryGap: false,
                    data: index.net.data.xData,
                    axisLine: {
                        lineStyle: {
                            color: theme.border
                        }
                    },
                    axisLabel: { color: theme.muted }
                },
                yAxis: {
                    name:  '单位 '+ index.net.default_unit,
                    splitLine: {
                        lineStyle: { color: theme.border }
                    },
                    axisLine: {
                        lineStyle: { color: theme.border }
                    },
                    axisLabel: { color: theme.muted }
                },
                series: [{
                    name: '上行',
                    type: 'line',
                    data: index.net.data.yData,
                    smooth: true,
                    showSymbol: false,
                    symbol: 'circle',
                    symbolSize: 6,
                    areaStyle: {
                        normal: {
                            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{
                                offset: 0,
                                color: applyColorAlpha(theme.primary, 0.35)
                            }, {
                                offset: 1,
                                color: applyColorAlpha(theme.primary, 0.08)
                            }], false)
                        }
                    },
                    itemStyle: {
                        normal: {
                            color: theme.primary
                        }
                    },
                    lineStyle: {
                        normal: {
                            width: 1
                        }
                    }
                },
                {
                    name: '下行',
                    type: 'line',
                    data: index.net.data.zData,
                    smooth: true,
                    showSymbol: false,
                    symbol: 'circle',
                    symbolSize: 6,
                    areaStyle: {
                        normal: {
                            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{
                                offset: 0,
                                color: applyColorAlpha(theme.secondary, 0.35)
                            }, {
                                offset: 1,
                                color: applyColorAlpha(theme.secondary, 0.08)
                            }], false)
                        }
                    },
                    itemStyle: {
                        normal: {
                            color: theme.secondary,
                        }
                    },
                    lineStyle: {
                        normal: {
                            width: 1,
                        }
                    }
                }]
            };
            return option;
        },

        
        add: function (up, down) {
            var _net = this;
            var limit = 8;
            var d = new Date()
            if (_net.data.xData.length >= limit) _net.data.xData.splice(0, 1);
            if (_net.data.yData.length >= limit) _net.data.yData.splice(0, 1);
            if (_net.data.zData.length >= limit) _net.data.zData.splice(0, 1);

            _net.data.xData.push(d.getHours() + ':' + d.getMinutes() + ':' + d.getSeconds());

            if (up>down){
                var upTmp = toSizePos(up);
                var upTmpSize = upTmp['name'].split(' ')[0];
                index.net.default_unit = upTmp['name'].split(' ')[1] + '/s';

                var downTmpSize = toSizePos(down,upTmp['pos'])['name'].split(' ')[0];
                // console.log('up',upTmp['pos'],toSizePos(down, upTmp['pos']),downTmpSize);

                _net.data.zData.push(downTmpSize);
                _net.data.yData.push(upTmpSize);
            } else {

                var downTmp = toSizePos(down);
                var downTmpSize = downTmp['name'].split(' ')[0];
                index.net.default_unit = downTmp['name'].split(' ')[1] + '/s';

                var upTmpSize = toSizePos(up, downTmp['pos'])['name'].split(' ')[0];
                // console.log('down',downTmp['pos'],toSizePos(up, downTmp['pos']),upTmpSize);

                _net.data.zData.push(downTmpSize);
                _net.data.yData.push(upTmpSize);
            }
            
        },
        renderSelect:function(net){
            // console.log(net);
            if (!index.net.init_select){
                var option = '';
                var network = net.network;
                var network_io_key = getCookie('network_io_key');

                for (var name in network) {
                    if (name == 'ALL'){
                        option += '<option value="'+name+'">全部</option>';
                    } else if (network_io_key == name){
                        option += '<option value="'+name+'" selected>'+name+'</option>';
                    } else {
                        option += '<option value="'+name+'">'+name+'</option>';
                    }
                }
                $('select[name="network-io"]').html(option);
                index.net.init_select = true;
            }
        }
    },

    iostat:{
        table: null,
        data: {
          xData: [],
          yData: [],
          zData: [],
          tipsData: []
        },
        init_select:false,
        default_unit : 'MB/s',
        init:function(){
            for (var i = 8; i >= 0; i--) {
                var time = (new Date()).getTime();
                index.iostat.data.xData.push(index.common.format(time - (i * 3 * 1000)));
                index.iostat.data.yData.push(0);
                index.iostat.data.zData.push(0);
                index.iostat.data.tipsData.push({});
            }

            var option = index.iostat.defaultOption();
            initEchartWhenReady('ioStat', option, function (chart) {
                index.iostat.table = chart;
                window.addEventListener("resize", function () {
                    if (index.iostat.table) {
                        index.iostat.table.resize();
                    }
                });
            });
        },

        render:function(){
            if (!index.iostat.table) {
                return;
            }
            var theme = getChartTheme();
            index.iostat.table.setOption({
                tooltip: {
                    trigger: 'axis',
                    backgroundColor: theme.surface,
                    borderColor: theme.border,
                    textStyle: { color: theme.text },
                    extraCssText: 'box-shadow: 0 12px 28px rgba(15, 23, 42, 0.12); border-radius: 12px; padding: 10px;',
                    axisPointer: {
                        type: 'line',
                        lineStyle: { color: theme.border }
                    },
                    formatter :function (config) {
                        var _config = config, _tips = "时间：" + _config[0].axisValue + "<br />", options = {
                            read_bytes: '读取字节数',
                            read_count: '读取次数 ',
                            read_merged_count: '合并读取次数',
                            read_time: '读取延迟',
                            write_bytes: '写入字节数',
                            write_count: '写入次数',
                            write_merged_count: '合并写入次数',
                            write_time: '写入延迟',
                        }, data = index.iostat.data.tipsData[config[0].dataIndex], list = ['read_count', 'write_count', 'read_merged_count', 'write_merged_count', 'read_time', 'write_time',];
                        for (var i = 0; i < config.length; i++) {
                            if (typeof config[i].data == "undefined") {
                                return false;
                            }
                            _tips += '<span style="display: inline-block;width: 10px;height: 10px;border-radius: 50%;background: ' + config[i].color + ';"></span>&nbsp;&nbsp;<span>' + config[i].seriesName + '：' + config[i].data + ' MB/s' + '</span><br />'
                        }
                        $.each(list, function (index, item) {

                            if (typeof data[item] != 'undefined'){
                                _tips += '<span style="display: inline-block;width: 10px;height: 10px;"></span>&nbsp;&nbsp;<span style="' + (item.indexOf('time') > -1 ? ('color:' + ((data[item] > 100 && data[item] < 1000) ? '#ff9900' : (data[item] >= 1000 ? 'red' : '#20a53a'))) : '') + '">' + options[item] + '：' + data[item] + (item.indexOf('time') > -1 ? ' ms' : ' 次/秒') + '</span><br />';
                            }
                        })
                        return _tips;
                    }
                },
                yAxis: {
                    name:  '单位 '+ index.iostat.default_unit,
                    splitLine: { lineStyle: { color: theme.border } },
                    axisLine: { lineStyle: { color: theme.border } },
                    axisLabel: { color: theme.muted }
                },
                xAxis: {
                    data: index.iostat.data.xData,
                    axisLine: { lineStyle: { color: theme.border } },
                    axisLabel: { color: theme.muted }
                },
                series: [{
                    name: "读取",
                    data: index.iostat.data.yData
                }, {
                    name: "写入",
                    data: index.iostat.data.zData
                }]
            });
        },
        defaultOption:function(){
            var theme = getChartTheme();
            var option = {
                backgroundColor: theme.surfaceContainer,
                color: [theme.primary, theme.secondary],
                title: {
                    text: "",
                    left: 'center',
                    textStyle: {
                        color: theme.muted,
                        fontStyle: 'normal',
                        fontFamily: "Inter, PingFang SC, Microsoft YaHei, sans-serif",
                        fontSize: 14
                    }
                },
                tooltip: {
                    trigger: 'axis',
                    backgroundColor: theme.surface,
                    borderColor: theme.border,
                    textStyle: { color: theme.text },
                    extraCssText: 'box-shadow: 0 12px 28px rgba(15, 23, 42, 0.12); border-radius: 12px; padding: 10px;',
                    axisPointer: {
                        type: 'line',
                        lineStyle: { color: theme.border }
                    }
                },
                legend: {
                    data: ["读取", "写入"],
                    bottom: '2%',
                    textStyle: { color: theme.muted }
                },
                grid: {
                    left: '2%',
                    right: '3%',
                    bottom: '15%',
                    containLabel: true
                },
                xAxis: {
                    type: 'category',
                    boundaryGap: false,
                    data: index.iostat.data.xData,
                    axisLine: {
                        lineStyle: {
                            color: theme.border
                        }
                    },
                    axisLabel: { color: theme.muted }
                },
                yAxis: {
                    name:  '单位 '+ index.iostat.default_unit,
                    splitLine: {
                        lineStyle: { color: theme.border }
                    },
                    axisLine: {
                        lineStyle: { color: theme.border }
                    },
                    axisLabel: { color: theme.muted }
                },
                series: [{
                    name: '读取',
                    type: 'line',
                    data: index.iostat.data.yData,
                    smooth: true,
                    showSymbol: false,
                    symbol: 'circle',
                    areaStyle: {
                        normal: {
                            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{
                                offset: 0,
                                color: applyColorAlpha(theme.primary, 0.3)
                            }, {
                                offset: 1,
                                color: applyColorAlpha(theme.primary, 0.06)
                            }], false)
                        }
                    },
                    itemStyle: {
                        normal: {
                            color: theme.primary
                        }
                    },
                    lineStyle: {
                        normal: {
                            width: 1,
                        }
                    }
                },
                {
                    name: '写入',
                    type: 'line',
                    data: index.iostat.data.zData,
                    smooth: true,
                    showSymbol: false,
                    symbol: 'circle',
                    symbolSize: 6,
                    areaStyle: {
                        normal: {
                            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{
                                offset: 0,
                                color: applyColorAlpha(theme.secondary, 0.3)
                            }, {
                                offset: 1,
                                color: applyColorAlpha(theme.secondary, 0.06)
                            }], false)
                        }
                    },
                    itemStyle: {
                        normal: {
                            color: theme.secondary
                        }
                    },
                    lineStyle: {
                        normal: {
                            width: 1,
                        }
                    }
                }]
            };
            return option;
        },

        renderSelect:function(data){
            if (!index.iostat.init_select){
                var option = '';
                var iostat = data.iostat;
                var disk_io_key = getCookie('disk_io_key');

                for (var name in iostat) {
                    if (name == 'ALL'){
                        option += '<option value="'+name+'">全部</option>';
                    } else if (disk_io_key == name){
                        option += '<option value="'+name+'" selected>'+name+'</option>';
                    } else {
                        option += '<option value="'+name+'">'+name+'</option>';
                    }
                }
                $('select[name="disk-io"]').html(option);
                index.iostat.init_select = true;
            }
        },
        add: function (read, write, data) {
            var _iostat = this;
            var limit = 8;
            var d = new Date()
            if (_iostat.data.xData.length >= limit) _iostat.data.xData.splice(0, 1);
            if (_iostat.data.yData.length >= limit) _iostat.data.yData.splice(0, 1);
            if (_iostat.data.zData.length >= limit) _iostat.data.zData.splice(0, 1);
            if (_iostat.data.tipsData.length >= limit) _iostat.data.tipsData.splice(0, 1);


            var readTmpSize = toSizeMB(read).split(' ')[0];
            var writeTmpSize = toSizeMB(write).split(' ')[0];

            _iostat.data.zData.push(writeTmpSize);
            _iostat.data.yData.push(readTmpSize);
            _iostat.data.tipsData.push(data);
            _iostat.data.xData.push(d.getHours() + ':' + d.getMinutes() + ':' + d.getSeconds());
        },

    },
    getData:function(){

        $.get("/system/network", function(net) {

            //网络IO
            var network_io_key = getCookie('network_io_key');
            var network_data = net.network;
            var network_select = network_data['ALL'];
            if (network_io_key && network_io_key != ''){
                network_select = network_data[network_io_key];
            }

            index.net.add(network_select.up,network_select.down);
            index.net.render();
            index.net.renderSelect(net);

            $("#upSpeed").html(toSize(network_select.up));
            $("#downSpeed").html(toSize(network_select.down));

            $("#downAll").html(toSize(network_select.downTotal));
            $("#downAll").attr('title','数据包:' + network_select.downPackets)
            $("#upAll").html(toSize(network_select.upTotal));
            $("#upAll").attr('title','数据包:' + network_select.upPackets)


            //磁盘IO
            var disk_io_key = getCookie('disk_io_key');
            var iostat_data = net.iostat;
            var iostat_select = iostat_data['ALL'];
            if (disk_io_key && disk_io_key != ''){
                iostat_select = iostat_data[disk_io_key];
            }

            index.iostat.add(iostat_select.read_bytes,iostat_select.write_bytes, iostat_select);
            index.iostat.render();
            index.iostat.renderSelect(net);

            $("#readBytes").html(toSize(iostat_select.read_bytes));
            $("#writeBytes").html(toSize(iostat_select.write_bytes));
            $("#diskIops").html(iostat_select.read_count+":"+iostat_select.write_count+ " 次");
            $("#diskTime").html(iostat_select.read_time+":"+iostat_select.write_time +" ms");


            $("#core").html(net.cpu[1] + " " + lan.index.cpu_core);
            $("#state").html(net.cpu[0]);
            
            setcolor(net.cpu[0], "#state", 30, 70, 90);
            //负载
            getLoad(net.load);
            //内存
            setMemImg(net.mem);
            //绑定hover事件
            setImg();
            showCpuTips(net);

        },'json');
    },
    task:function(){
        // index.getData();
        setInterval(function() {
            index.getData();
        }, 3000);
    },
    init: function(){
        index.net.init();
        index.iostat.init();
        index.task();
    }
}
