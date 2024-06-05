  
function tmPostCallback(method, args, callback, version='1.0'){
    var req_data = {};
    req_data['name'] = 'task_manager';
    req_data['func'] = method;
    req_data['script']='task_manager_index';
    args['version'] = version;

    if (typeof(args) == 'string' && args == ''){
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

var tab_name = 'p_list';
var search_val = '';
var select_pid = undefined; // 当前选中进程的id
var realProcess = []; // 进程数组
var originProcess = []; // 当前进程展示的列表
var wrapPid = {}; // 展开的父进程
var TaskProcessLayerIndex = '';  // 进程详情弹窗的index
var canScroll2TaskMangerPossess = true; // 是否可以定位到选中的进程

$('.t-mana .man-menu-sub span').click(function () {
    $(this).siblings().removeClass("on");
    tab_name = $(this).attr('class');
    $(this).addClass("on")
    // console.log(tab_name);
    if (tab_name == 'p_resource') {
      $('.resource-panel').addClass('resource-panel-show')
      $('.taskdivtable').addClass('divtable-hide')
      $('.ts-line').addClass('divtable-hide')
    } else if (tab_name !== 'p_resource on') {
      $('.resource-panel').removeClass('resource-panel-show')
      $('.taskdivtable').removeClass('divtable-hide')
      $('.ts-line').removeClass('divtable-hide')
    }
    search_val = $('.search-bar .search_input').val('')
    get_list_bytab(false);
});

$('.search-bar .search_input').on({
    'keyup': function (e) {
        if (e.keyCode == 13) {
            get_list_bytab();
        }
    },
    'blur': function () {
        get_list_bytab(true);
    },
});

$('.search-bar .glyphicon').click(function (e) {
    get_list_bytab();
});

var process_list_s = 0;
get_process_list();

function setTableHead(data) {
    $.each(Object.keys(data.meter_head), function (index, item) {
        if (!$('.' + item).hasClass('disabled')) {
            if (data.meter_head[item]) {
                $('.' + item).addClass('active');
            } else {
                $('.' + item).removeClass('active');
            }
        }
    });

    $('#change_thead').bind("contextmenu", function () {
      return false;
    })
    $(".plug_menu").bind("contextmenu", function () {
      return false;
    })
    $('#change_thead').mousedown(function (e) {
      e.preventDefault();
      if (e.which == 3) {  // 1 = 鼠标左键; 2 = 鼠标中键; 3 = 鼠标右键
        var menu = $('.setting_ul');
        var offset = $(this).offset();
        var x = e.pageX - offset.left;
        var y = e.pageY - offset.top;
        var width = menu.outerWidth();
        $(".plug_menu").removeAttr('style');
        $(".setting_ul").removeClass('undisplay');
        if ($('#change_thead').width() - x < width) {
          $(".plug_menu").css({
            position: 'absolute',
            left: x - width + 150 + "px",
            top: y + 50 + "px",
          }).show();
        } else {
          $(".plug_menu").css({
            position: 'absolute',
            left: x + width + "px",
            top: y + 50 + "px",
          }).show();
        }
      }
      $(".setting_ul").show();
    });
}


$('.layui-layer').not($('.setting_ul_li')).click(function () {
    $(".plug_menu").hide()
    $(".setting_ul").hide();
});
var isProcessing = false; // 设置标志

$('.setting_ul_li').off('click').click(function (e) {
    var that = $(this);
    e.stopPropagation();
    // 检查标志
    if (isProcessing) {
        return;
    }
    if (!$(this).hasClass('disabled')) {
        isProcessing = true; // 点击事件被触发，设置标志
        var name = $(this).attr("name");
        clearInterval(process_list_s);

        tmPostCallback('set_meter_head',{meter_head_name: name}, function(data){
            isProcessing = false; // 操作完成，清除标志
            if (!data) {
                layer.msg('设置失败');
            }
            that.toggleClass('active');
            get_process_list(null, null, false);
            clearInterval(process_list_s);
            process_list_s = setInterval(function () {
            if ($(".t-mana").length == 0) {
                    clearInterval(process_list_s);
                    process_list_s = 0;
                    console.log('进程列表轮询任务已停止');
                }
                get_process_list(null, null, true);
            }, 3000);
        });
    }
});

$('.setting_btn').on('click',function (e) {
    e.stopPropagation();
    var offset = $('.man-menu-sub').offset();
    var x = e.pageX - offset.left;
    var y = e.pageY - offset.top;
    var width = $('.man-menu-sub').outerWidth();
    if ($('.man-menu-sub').width() - x < width) {
        $(".plug_menu").css({
            position: 'absolute',
            right: "14.5px",
            top:"40px",
        }).toggle();
        $('.setting_ul').addClass('undisplay')
    }
    $(".setting_ul").toggle();
});

if (process_list_s === 0) {
    process_list_s = setInterval(function () {
        if ($(".t-mana").length == 0) {
            clearInterval(process_list_s);
            process_list_s = 0;
            console.log('进程列表轮询任务已停止');
        }
        get_process_list(null, null, true);
    }, 3000);
}

function get_list_bytab(isblur) {
    if (isblur && $('.search-bar .search_input').val() === search_val) {
        return;
    }
    search_val = $('.search-bar .search_input').val();
    get_process_list();

    switch (tab_name) {
        case 'p_list':
            $('.table_config').show();
            $('.search-bar span').addClass('r56');
            select_pid = '';
            wrapPid = {};
            canScroll2TaskMangerPossess = true;
            get_process_list();
            break;
        case 'p_resource':
            $('.table_config').hide();
            $('.search-bar span').removeClass('r56');
            get_resource_list();
            break;
        case 'p_run':
            $('.table_config').hide();
            $('.search-bar span').removeClass('r56');
            get_run_list();
            break;
        case 'p_service':
            $('.table_config').hide();
            $('.search-bar span').removeClass('r56');
            get_service_list();
            break;
        case 'p_network':
            $('.table_config').hide();
            $('.search-bar span').removeClass('r56');
            get_network_list();
            break;
        case 'p_user':
            $('.table_config').hide();
            $('.search-bar span').removeClass('r56');
            get_user_list();
            break;
        case 'p_cron':
            $('.table_config').hide();
            $('.search-bar span').removeClass('r56');
            get_cron_list();
            break;
        case 'p_session':
            $('.table_config').hide();
            $('.search-bar span').removeClass('r56');
            get_who_list();
            break;
    }
}

function get_process_list(sortx, reverse, rx) {
    if ($('.t-mana .man-menu-sub .on').attr('class') != 'p_list on') return;
    var cookie_key = 'task_process_sort';
    var s_tmp = getCookie(cookie_key);
    if (sortx == undefined || sortx == null) {
        if (s_tmp) {
            sortx_arr = s_tmp.split('|');
            sortx = sortx_arr[0];
            reverse = sortx_arr[1];
        } else {
            sortx = 'cpu_percent';
        }
    }

    res_list = {True: 'False',False: 'True'};
    setCookie(cookie_key, sortx + '|' + reverse);
    if (!rx) {
      var loadT = layer.msg('正在获取进程列表..', {icon: 16, time: 0, shade: [0.3, '#000']})
    }

    tmPostCallback('get_process_list', {sortx: sortx,reverse: reverse,search:search_val}, function(rdata){
        // console.log(rdata);
        if (!rx) layer.close(loadT);
        if ($('.t-mana .man-menu-sub .on').attr('class') != 'p_list on') return;
        if (rdata.status === false) {
            layer.closeAll();
            layer.msg(rdata.msg, {icon: 2});
            return;
        }
        var data = rdata.data;

        var year = new Date().getFullYear();
        realProcess = [];
        originProcess = [];
        var list = data.process_list;
        for (var i = 0; i < list.length; i++) {
            list[i].haschild = false;
            if (list[i].children && list[i].children.length > 0) {
                list[i].haschild = true;
            }
            originProcess.push(list[i]);
            realProcess.push(list[i]);
        }
        var selectline = buildRealProcess();
        var tbody_tr = createProcessTable(true, data);
        var tbody = '<thead title="右键可设置表头" id="change_thead">\
					<tr style="cursor: pointer;">\
						<th style="width:160px;' + (data.meter_head.ps ? '' : 'display:none;') + '" class="pro_name pro_ps"  onclick="get_process_list(\'ps\',\'' + res_list[reverse] + '\')">应用名称</th>\
						<th class="pro_pid" style="' + (data.meter_head.pid ? '' : 'display:none;') + '" onclick="get_process_list(\'pid\',\'' + res_list[reverse] + '\')">PID</th>\
						<th class="pro_threads" style="' + (data.meter_head.threads ? '' : 'display:none;') + '" onclick="get_process_list(\'threads\',\'True\')">线程</th>\
						<th style="width:80px;' + (data.meter_head.user ? '' : 'display:none;') + '" class="pro_user" onclick="get_process_list(\'user\',\'' + res_list[reverse] + '\')">用户</th>\
						<th style="' + (data.meter_head.cpu_percent ? '' : 'display:none;') + '" class="pro_cpu_percent" onclick="get_process_list(\'cpu_percent\',\'True\')">CPU</th>\
						<th class="pro_memory_used" style="' + (data.meter_head.memory_used ? '' : 'display:none;') + '" onclick="get_process_list(\'memory_used\',\'True\')">内存</th>\
						<th style="width:70px;' + (data.meter_head.io_read_bytes ? '' : 'display:none;') + '" class="pro_io_read_speed" onclick="get_process_list(\'io_read_speed\',\'True\')">io读</th>\
						<th style="width:70px;' + (data.meter_head.io_write_bytes ? '' : 'display:none;') + '" class="pro_io_write_speed" onclick="get_process_list(\'io_write_speed\',\'True\')">io写</th>\
						<th style="width:70px;' + (data.meter_head.up ? '' : 'display:none;') + '" class="pro_up" onclick="get_process_list(\'up\',\'True\')">上行</th>\
						<th style="width:70px;' + (data.meter_head.down ? '' : 'display:none;') + '" class="pro_down" onclick="get_process_list(\'down\',\'True\')">下行</th>\
						<th class="pro_connects" style="' + (data.meter_head.connects ? '' : 'display:none;') + '" onclick="get_process_list(\'connects\',\'True\')">连接</th>\
						<th class="pro_status" style="' + (data.meter_head.status ? '' : 'display:none;') + '" onclick="get_process_list(\'status\',\'' + res_list[reverse] + '\')">状态</th>\
						<th style="cursor:text;">操作</th>\
					</tr>\
				</thead>\
				<tbody>' + tbody_tr + '</tbody>';
        $("#TaskManagement").html(tbody);
        var topMsg = '<div class="mini-info-box">\
				<div class="mini-info-con"><p><span class="tname">CPU：</span>' + data.info.cpu + '%</p><p><span class="tname">内存：</span>' + toSize(data.info.mem) + '</p></div>\
				<div class="mini-info-con"><p style="text-align:center">负载(load average)</p><p style="text-align:center">' + data.info.load_average[1] + ', ' + data.info.load_average[5] + ', ' + data.info.load_average[15] + '</p></div>\
				<div class="mini-info-con"><p><span class="tname">进程数：</span>' + data.process_list.length + '</p><p><span class="tname">磁盘：</span>' + toSize(data.info.disk) + '</p></div>\
			</div>';
        $("#load_average").html(topMsg).show();
        $(".pro_" + sortx).append('<span class="glyphicon glyphicon-triangle-' + (reverse == 'True' ? 'bottom' : 'top') + '" style="margin-left:5px;color:#bbb"></span>');
        $(".table-cont").css("height", "500px");
        scropll2selectPossess(selectline);
        show_task();
        setTableHead(data);
        if(getCookie('table_config_tip')=='false'||!getCookie('table_config_tip')){
            layer.tips('点击可设置表头', '.setting_btn', {
                tips: [1, '#20a53a'],
                time: 3000
            });
            setCookie('table_config_tip',true);
        }
        // 清除掉之前绑定的滚动事件
        // $("#table-cont").unbind('scroll');
        // 重新绑定滚动事件
        // $('#table-cont').scroll(task_manager_possess_scroll());
    });
}

function task_manager_possess_scroll() {
    var timer = null;
    var set2selected = null;
    // 滚动节流
    return function () {
        if (timer !== null) return;
        timer = setTimeout(function () {
            timer = null;
            canScroll2TaskMangerPossess = false;
            if (set2selected !== null) clearTimeout(set2selected)
            // 最后一次滚动后2秒内不再滚动，才能滚动到选中的行
            set2selected = setTimeout(function () {
                canScroll2TaskMangerPossess = true;
            }, 2000);
        }, 500);
    }
}

function scropll2selectPossess(selectline) {
    if (canScroll2TaskMangerPossess && selectline !== -1) {
        var top = $('#table-cont')[0].scrollTop;
        // if(selectline > 2)
        if (selectline * 38 > top + 500 || selectline * 38 < top) {
            $('#table-cont')[0].scrollTo(0, (selectline - 2) * 38, 'smooth');
        }
    }
}

function show_process_child(pid) {
    wrapPid[pid + ''] = true;
    // buildRealProcess()
    // createProcessTable()
}

function colp_process_child(pid) {
    // select_pid = pid+'';
    wrapPid[pid + ''] = false;
    // buildRealProcess()
    // createProcessTable()
}

function click_process_tr(e, pid, fpid) {
    select_pid = pid + '';
    if (e.target.innerText === '结束' && fpid) {
      select_pid = fpid + '';
    }
    var selectline = buildRealProcess()
    createProcessTable()
    scropll2selectPossess(selectline)
}

// 构建真实进程列表
function buildRealProcess() {
    realProcess = [];
    var len = originProcess.length;
    for (var i = 0; i < len; i++) {
      realProcess.push(originProcess[i]);
      if (wrapPid[originProcess[i].pid + '']) {
        // console.log(originProcess[i]);
        if (!originProcess[i].children) {
          wrapPid[originProcess[i].pid + ''] = false;
          continue;
        }
        var childSelected = false;
        for (var j = 0; j < originProcess[i].children.length; j++) {
          originProcess[i].children[j].fpid = originProcess[i].pid + ''
          originProcess[i].children[j].ischild = true
          originProcess[i].children[j].isselect = false
          if (originProcess[i].pid + '' === select_pid) {
            originProcess[i].children[j].isselect = true
          }
          if (originProcess[i].children[j].pid + '' === select_pid) {
            var childSelected = true;
          }
          realProcess.push(originProcess[i].children[j]);
          // 显示选中的父子进程
        }
        if (childSelected) {
          for (var k = 0; k <= originProcess[i].children.length; k++) {
            realProcess.pop()
          }
          originProcess[i].isselect = true
          realProcess.push(originProcess[i])
          for (var l = 0; l < originProcess[i].children.length; l++) {
            originProcess[i].children[l].isselect = true
            realProcess.push(originProcess[i].children[l]);
          }
        }
      }
    }
    for (var i = 0; i < realProcess.length; i++) {
      if (realProcess[i].pid + '' === select_pid) {
        return i// 返回选中的下标
      }
    }
    return -1
}

// 生成进程表格内容
function createProcessTable(getboday, data) {
    var tbody_tr = '';
    for (var i = 0; i < realProcess.length; i++) {
        if (realProcess[i].status == '活动') realProcess[i].status = '<span style="color:green;">活动</span>';
        var colp = realProcess[i].haschild ? '<svg class="colp arrow" onclick="show_process_child(' + realProcess[i].pid + ')" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="18" height="18" style="border-color: rgba(0,0,0,0);border-width: bpx;border-style: undefined" filter="none">\
			<path d="M15.811 23.47c-0.252-0.060-0.47-0.185-0.641-0.356l-10.685-10.685c-0.521-0.521-0.521-1.365 0-1.886s1.365-0.521 1.886 0l9.746 9.746 9.745-9.745c0.521-0.521 1.365-0.521 1.886 0s0.521 1.365 0 1.886l-10.685 10.685c-0.339 0.339-0.816 0.458-1.251 0.355z" fill="#999999"></path>\
        </svg>' : '';
        if (wrapPid[realProcess[i].pid + '']) {
            colp = '<svg class="arrow" onclick="colp_process_child(' + realProcess[i].pid + ')" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="18" height="18" style="border-color: rgba(0,0,0,0);border-width: bpx;border-style: undefined" filter="none">\
					<path d="M15.811 23.47c-0.252-0.060-0.47-0.185-0.641-0.356l-10.685-10.685c-0.521-0.521-0.521-1.365 0-1.886s1.365-0.521 1.886 0l9.746 9.746 9.745-9.745c0.521-0.521 1.365-0.521 1.886 0s0.521 1.365 0 1.886l-10.685 10.685c-0.339 0.339-0.816 0.458-1.251 0.355z" fill="#999999"></path>\
				</svg>';
        }
        var childNums = realProcess[i].haschild ? '<span style="float:none;">(' + realProcess[i].children.length + ')</span>' : '';
        var namewidth = "max-width:120px;"
        if (realProcess[i].ischild) {
            namewidth = "max-width:80px;"
        }
        if (realProcess[i].haschild) {
            namewidth = "max-width:100px;"
        }
        var processName = '<span class="size_ellipsis" style="' + (namewidth) + 'float:none;vertical-align:middle;">' + realProcess[i].ps + '</span>';
        var isProcessChild = realProcess[i].ischild ? 'process-child' : '';
        var childStyle = realProcess[i].ischild ? 'width:100px' : '';
        var selected = realProcess[i].pid + '' === select_pid || realProcess[i].isselect ? 'class="process-select"' : '';
        var selected_one = realProcess[i].pid + '' === select_pid ? 'style="background-color:#F6F6F6;"' : '';
        var kill_process = realProcess[i].haschild ? 'kill_process_all' : 'kill_process';

        var tbody_td = '';
        if ('io_read_bytes' in realProcess[i]){
            tbody_td += '<td style="' + (data?(data.meter_head.io_read_bytes ? '' : 'display:none;'):'') + '">' + toSize(realProcess[i].io_read_speed).replace(' ', '') + '</td>';
            tbody_td += '<td style="' + (data?(data.meter_head.io_write_bytes ? '' : 'display:none;'):'') + '">' + toSize(realProcess[i].io_write_speed).replace(' ', '') + '</td>';

            tbody_td += '<td style="' + (data?(data.meter_head.up ? '' : 'display:none;'):'') + '" title="上行速度：' + toSize(realProcess[i].up) + '/秒\n发包速度：' + realProcess[i].up_package + '个/秒">' + toSize(realProcess[i].up).replace(' ', '') + '</td>';
            tbody_td += '<td style="' + (data?(data.meter_head.down ? '' : 'display:none;'):'') + '" title="下行速度：' + toSize(realProcess[i].down) + '/秒\n收包速度：' + realProcess[i].down_package + '个/秒">' + toSize(realProcess[i].down).replace(' ', '') + '</td>';
        }
        
        tbody_tr += '<tr ' + selected + selected_one + ' onclick="click_process_tr(event,' + realProcess[i].pid + ',' + realProcess[i].fpid + ')" >\
			<td class="td-pid" style="' + (data?(data.meter_head.ps ? '' : 'display:none;'):'') + '">\
				' + colp + '\
				<a style="display:block; position:relative; width:120px;' + childStyle + '" title="名称：' + realProcess[i].ps + '\nname: ' + realProcess[i].name + '\nexe: ' + realProcess[i].exe + '"\
				class="btlink ' + isProcessChild + '" onclick="get_process_info(' + realProcess[i].pid + ')">\
					' + processName + '\
					' + childNums + '\
			</td>\
			<td style="' + (data?(data.meter_head.pid ? '' : 'display:none;'):'') + '">' + realProcess[i].pid + '</td>\
			<td style="' + (data?(data.meter_head.threads ? '' : 'display:none;'):'') + '">' + realProcess[i].threads + '</td>\
			<td style="' + (data?(data.meter_head.user ? '' : 'display:none;'):'') + '" title="' + realProcess[i].user + '"><span style="width:80px;" class="size_ellipsis">' + realProcess[i].user + '</span></td>\
			<td style="' + (data?(data.meter_head.cpu_percent ? '' : 'display:none;'):'') + '">' + realProcess[i].cpu_percent + '%</td>\
            <td style="' + (data?(data.meter_head.memory_used ? '' : 'display:none;'):'') + '">' + toSize(realProcess[i].memory_used).replace(' ', '') + '</td>\
            '+tbody_td+'\
			<td style="' + (data?(data.meter_head.connects ? '' : 'display:none;'):'') + '">' + realProcess[i].connects + '</td>\
			<td style="' + (data?(data.meter_head.status ? '' : 'display:none;'):'') + '">' + realProcess[i].status + '</td>\
			<td><a class="btlink" onclick="' + kill_process + '(' + realProcess[i].pid + ',' + realProcess[i].fpid + ')">结束</a></td>\
		</tr>';
    }
    if (getboday) return tbody_tr;
    $("#TaskManagement tbody").html(tbody_tr);
}

// 获取资源列表
function get_resource_list() {
    // console.log('get_resource_list----------');
    var url = '/plugin?action=a&name=task_manager&s=cpu_status'
    // url = 'plugin?action=a&name=task_manager&s=get_disk_staus'

    var res_list = {
      True: 'False',
      False: 'True'
    }
    var reverse = 'True'
    $.post(url, function (data) {
      console.log(data);
      realProcess = []
      originProcess = []
      var list = data.process_list
      for (var i = 0; i < list.length; i++) {
        list[i].haschild = false
        if (list[i].children && list[i].children.length > 0) {
          list[i].haschild = true
        }
        originProcess.push(list[i])
        realProcess.push(list[i])
      }
      // console.log('realllll');

      buildRealProcess()
      var tbody_tr = createProcessTable(true);
      var tbody = '<thead>\
					<tr style="cursor: pointer;">\
						<th style="width:120px;" class="pro_name pro_ps" onclick="get_process_list(\'ps\',\'' + res_list[reverse] + '\')">应用名称</th>\
						<th class="pro_pid" onclick="get_process_list(\'pid\',\'' + res_list[reverse] + '\')">PID</th>\
						<th style="width:50px;"class="pro_threads" onclick="get_process_list(\'threads\',\'True\')">线程</th>\
						<th style="width:60px;" class="pro_user" onclick="get_process_list(\'user\',\'' + res_list[reverse] + '\')">用户</th>\
						<th style="width:70px;" class="pro_cpu_percent" onclick="get_process_list(\'cpu_percent\',\'True\')">CPU</th>\
						<th style="width:70px;" class="pro_memory_used" onclick="get_process_list(\'memory_used\',\'True\')">内存</th>\
						<th style="width:70px;" class="pro_io_read_speed" onclick="get_process_list(\'io_read_speed\',\'True\')">io读</th>\
						<th style="width:70px;" class="pro_io_write_speed" onclick="get_process_list(\'io_write_speed\',\'True\')">io写</th>\
						<th style="width:70px;" class="pro_up" onclick="get_process_list(\'up\',\'True\')">上行</th>\
						<th style="width:70px;" class="pro_down" onclick="get_process_list(\'down\',\'True\')">下行</th>\
						<th style="width:50px;" class="pro_connects" onclick="get_process_list(\'connects\',\'True\')">连接</th>\
						<th style="width:50px;" class="pro_status" onclick="get_process_list(\'status\',\'' + res_list[reverse] + '\')">状态</th>\
						<th style="width:50px;cursor:text">操作</th>\
					</tr>\
				</thead>\
				<tbody>' + tbody_tr + '</tbody>'
      $('#taskResourceTable').html(tbody);
      $(".table-cont").css("height", "220px");
    })

    $("#load_average").html('')
}

//查看计划任务列表
function get_cron_list() {
    var loadT = layer.msg('获取计划任务列表..', {icon: 16, time: 0, shade: [0.3, '#000']});
    tmPostCallback('get_cron_list', {search:search_val}, function(rdata){
        layer.close(loadT);

        var rdata = rdata.data;
        var tbody_tr = '';
        for (var i = 0; i < rdata.length; i++) {
            tbody_tr += '<tr title=\'' + rdata[i].command + '\'>\
						<td>' + rdata[i].cycle + '</td>\
						<td><a class="btlink" onclick="online_edit_file(\'' + rdata[i].exe + '\')">' + rdata[i].exe + '</a></td>\
						<td style="text-wrap:wrap;">' + rdata[i].ps + '</td>\
						<td><a class="btlink" onclick="remove_cron(' + i + ')">删除</a></td>\
					</tr>';
        }
        var tbody = '<thead>\
					<tr>\
						<th width="150">周期</th>\
						<th >执行</th>\
						<th overflow="hidden" width="40%">描述</th>\
						<th width="50">操作</th>\
					</tr>\
				</thead>\
				<tbody>' + tbody_tr + '</tbody>';
        $("#TaskManagement").html(tbody);
        var topMsg = '';
        $("#load_average").html(topMsg).hide();
        $(".table-cont").css("height", "597px");
        show_task();
    });
}


//查看网络状态
function get_network_list(rflush) {
    var loadT = layer.msg(lan.public.the_get, {icon: 16, time: 0, shade: [0.3, '#000']});
    tmPostCallback('get_network_list', {search:search_val}, function(rdata){
        layer.close(loadT);
        if (rdata.data['is_mac']){
            tbody_tr += "<tr><td colspan='6' style='text-align:center;'>mac无法使用</td></tr>";
            tbody = "<thead>\
                <tr>\
                    <th>" + lan.index.net_protocol + "</th>\
                    <th>" + lan.index.net_address_dst + "</th>\
                    <th>" + lan.index.net_address_src + "</th>\
                    <th>" + lan.index.net_address_status + "</th>\
                    <th>" + lan.index.net_process + "</th>\
                    <th>" + lan.index.net_process_pid + "</th>\
                </tr>\
            </thead>\
            <tbody>" + tbody_tr + "</tbody>";
            $("#TaskManagement").html(tbody);
            show_task();
            return;
        }

        var rdata = rdata.data;
        
        var tbody_tr = "";
        for (var i = 0; i < rdata.list.length; i++) {
            tbody_tr += "<tr>"
              + "<td>" + rdata.list[i].type + "</td>"
              + "<td>" + rdata.list[i].laddr[0] + ":" + rdata.list[i].laddr[1] + "</td>"
              + "<td>" + (rdata.list[i].raddr.length > 1 ? "<a style='color:blue;' title='" + lan.index.net_dorp_ip + "' href=\"javascript:dropAddress('" + rdata.list[i].raddr[0] + "');\">" + rdata.list[i].raddr[0] + "</a>:" + rdata.list[i].raddr[1] : 'NONE') + "</td>"
              + "<td>" + rdata.list[i].status + "</td>"
              + "<td>" + rdata.list[i].process + "</td>"
              + "<td>" + rdata.list[i].pid + "</td>"
              + "</tr>";
        }

        tbody = "<thead>\
                <tr>\
        			<th>" + lan.index.net_protocol + "</th>\
        			<th>" + lan.index.net_address_dst + "</th>\
        			<th>" + lan.index.net_address_src + "</th>\
        			<th>" + lan.index.net_address_status + "</th>\
        			<th>" + lan.index.net_process + "</th>\
        			<th>" + lan.index.net_process_pid + "</th>\
                </tr>\
    		</thead>\
    		<tbody>" + tbody_tr + "</tbody>";

        $("#TaskManagement").html(tbody);
        var topMsg = '<div class="mini-info-box" style="width:666px">\
				<div class="mini-info-con" style="width:25%">\
					<p><span class="tname">总发送：</span>' + toSize(rdata.state.upTotal) + '</p>\
					<p><span class="tname">总接收：</span>' + toSize(rdata.state.downTotal) + '</p>\
				</div>\
				<div class="mini-info-con" style="width:25%">\
					<p><span class="tname">上行：</span>' + toSize(rdata.state.up) + '</p>\
					<p><span class="tname">下行：</span>' + toSize(rdata.state.down) + '</p>\
				</div>\
				<div class="mini-info-con" style="width:25%;border-right:#DBDBEA 1px solid">\
					<p><span class="tname">总发包：</span>' + to_max(rdata.state.upPackets) + '</p>\
					<p><span class="tname">总收包：</span>' + to_max(rdata.state.downPackets) + '</p>\
				</div>\
				<div class="mini-info-con" style="width:25%;">\
					<p><span class="tname">包发送/秒：</span>' + to_max(rdata.state.upPackets_s) + '</p>\
					<p><span class="tname">包接收/秒：</span>' + to_max(rdata.state.downPackets_s) + '</p>\
				</div>\
			</div>';
        $("#load_average").html(topMsg).show();
        $(".table-cont").css("height", "500px");
        show_task();
    });
}

function to_max(num) {
    if (num > 10000) {
      num = num / 10000;
      if (num > 10000) {
        num = num / 10000;
        return num.toFixed(5) + ' 亿';
      }
      return num.toFixed(5) + ' 万';
    }
    return num;
}

//获取会话列表
function get_who_list() {
    var loadT = layer.msg('正在获取用户会话列表..', {icon: 16, time: 0, shade: [0.3, '#000']});
    tmPostCallback('get_who', {search:search_val}, function(data){
        layer.close(loadT);
        var rdata = data.data;
        var tbody_tr = '';
        for (var i = 0; i < rdata.length; i++) {
            tbody_tr += '<tr>\
				<td>' + rdata[i].user + '</td>\
				<td>' + rdata[i].pts + '</td>\
				<td>' + rdata[i].ip + '</td>\
				<td>' + rdata[i].date + '</td>\
				<td><a class="btlink" onclick="pkill_session(\'' + rdata[i].pts + '\')">强制断开</a></td>\
			</tr>';
        }
        var tbody = '<thead>\
					<tr>\
						<th width="130">用户</th>\
						<th width="130">PTS</th>\
						<th>登陆IP</th>\
						<th>登陆时间</th>\
						<th width="80">操作</th>\
					</tr>\
				</thead>\
				<tbody>' + tbody_tr + '</tbody>';
        $("#TaskManagement").html(tbody);
        var topMsg = '';
        $("#load_average").html(topMsg).hide();
        $(".table-cont").css("height", "597px");
        show_task();
    });
}

//获取启动列表
function get_run_list() {
    var loadT = layer.msg('正在获取启动项列表..', {icon: 16, time: 0, shade: [0.3, '#000']});
    tmPostCallback('get_run_list', {search:search_val}, function(rdata){
        layer.close(loadT);
        if (rdata.data['is_mac']){
            tbody_tr += "<tr><td colspan='6' style='text-align:center;'>mac无法使用</td></tr>";
            var tbody = '<thead>\
                    <tr>\
                        <th width="170">名称</th>\
                        <th width="200">启动路径</th>\
                        <th width="100">文件大小</th>\
                        <th width="100">文件权限</th>\
                        <th>描述</th>\
                        <th width="50">操作</th>\
                    </tr>\
                </thead>\
                <tbody>' + tbody_tr + '</tbody>';
            $("#TaskManagement").html(tbody);
            return;
        }

        var rdata = rdata.data;
        var tbody_tr = '';
        for (var i = 0; i < rdata.run_list.length; i++) {
            tbody_tr += '<tr>\
				<td>' + rdata.run_list[i].name + '</td>\
				<td>' + rdata.run_list[i].srcfile + '</td>\
				<td>' + toSize(rdata.run_list[i].size) + '</td>\
				<td>' + rdata.run_list[i].access + '</td>\
				<td style="text-wrap:wrap;">' + rdata.run_list[i].ps + '</td>\
				<td><a class="btlink" onclick="online_edit_file(\'' + rdata.run_list[i].srcfile + '\')">编辑</a></td>\
			</tr>';
        }
        var tbody = '<thead>\
					<tr>\
						<th width="170">名称</th>\
						<th width="200">启动路径</th>\
						<th width="100">文件大小</th>\
						<th width="100">文件权限</th>\
						<th>描述</th>\
						<th width="50">操作</th>\
					</tr>\
				</thead>\
				<tbody>' + tbody_tr + '</tbody>';
        $("#TaskManagement").html(tbody);
        var topMsg = '<div class="mini-level">当前运行级别： level-' + rdata.run_level + '</div>';
        $("#load_average").html(topMsg).show();
        $(".table-cont").css("height", "500px");
        show_task();
    });
}

//获取服务列表
function get_service_list() {
    var loadT = layer.msg('正在获取服务列表..', {icon: 16, time: 0, shade: [0.3, '#000']});
    tmPostCallback('get_service_list', {search:search_val}, function(rdata){
        layer.close(loadT);
        if (rdata.data['is_mac']){
            tbody_tr += "<tr><td colspan='10' style='text-align:center;'>mac无法使用</td></tr>";
            var tbody = '<thead>\
                    <tr>\
                        <th>名称</th>\
                        <th width="70">Level-0</th>\
                        <th width="70">Level-1</th>\
                        <th width="70">Level-2</th>\
                        <th width="70">Level-3</th>\
                        <th width="70">Level-4</th>\
                        <th width="70">Level-5</th>\
                        <th width="70">Level-6</th>\
                        <th style="overflow:hidden">描述</th>\
                        <th width="50">操作</th>\
                    </tr>\
                </thead>\
                <tbody>' + tbody_tr + '</tbody>';
            $("#TaskManagement").html(tbody);
            return;
        }

        var rdata = rdata.data;

        var tbody_tr = '';
        for (var i = 0; i < rdata.serviceList.length; i++) {
        tbody_tr += '<tr>\
				<td>' + rdata.serviceList[i].name + '</td>\
				<td><a style="cursor:pointer" onclick="set_runlevel_state(0,\'' + rdata.serviceList[i].name + '\')">' + rdata.serviceList[i].runlevel_0 + '</a></td>\
				<td><a style="cursor:pointer" onclick="set_runlevel_state(1,\'' + rdata.serviceList[i].name + '\')">' + rdata.serviceList[i].runlevel_1 + '</a></td>\
				<td><a style="cursor:pointer" onclick="set_runlevel_state(2,\'' + rdata.serviceList[i].name + '\')">' + rdata.serviceList[i].runlevel_2 + '</a></td>\
				<td><a style="cursor:pointer" onclick="set_runlevel_state(3,\'' + rdata.serviceList[i].name + '\')">' + rdata.serviceList[i].runlevel_3 + '</a></td>\
				<td><a style="cursor:pointer" onclick="set_runlevel_state(4,\'' + rdata.serviceList[i].name + '\')">' + rdata.serviceList[i].runlevel_4 + '</a></td>\
				<td><a style="cursor:pointer" onclick="set_runlevel_state(5,\'' + rdata.serviceList[i].name + '\')">' + rdata.serviceList[i].runlevel_5 + '</a></td>\
				<td><a style="cursor:pointer" onclick="set_runlevel_state(6,\'' + rdata.serviceList[i].name + '\')">' + rdata.serviceList[i].runlevel_6 + '</a></td>\
				<td style="text-wrap:wrap;">' + rdata.serviceList[i].ps + '</td>\
				<td><a class="btlink" onclick="remove_service(\'' + rdata.serviceList[i].name + '\')">删除</a></td>\
			</tr>';
        }
        var tbody = '<thead>\
					<tr>\
						<th>名称</th>\
						<th width="70">Level-0</th>\
						<th width="70">Level-1</th>\
						<th width="70">Level-2</th>\
						<th width="70">Level-3</th>\
						<th width="70">Level-4</th>\
						<th width="70">Level-5</th>\
						<th width="70">Level-6</th>\
						<th style="overflow:hidden">描述</th>\
						<th width="50">操作</th>\
					</tr>\
				</thead>\
				<tbody>' + tbody_tr + '</tbody>';
        $("#TaskManagement").html(tbody);
        var topMsg = '<div class="mini-level">当前运行级别： level-' + rdata.runlevel + '</div>';
        $("#load_average").html(topMsg).show();
        $(".table-cont").css("height", "500px");
        show_task();
    });
}

//取用户列表
function get_user_list() {
    var loadT = layer.msg('正在获取用户列表..', {icon: 16, time: 0, shade: [0.3, '#000']});
    tmPostCallback('get_user_list', {search:search_val}, function(data){
        layer.close(loadT);
        var rdata = data.data;        
        var tbody_tr = '';
        for (var i = 0; i < rdata.length; i++) {
            tbody_tr += '<tr>\
					<td>' + rdata[i].username + '</td>\
					<td>' + rdata[i].home + '</td>\
					<td>' + rdata[i].group + '</td>\
					<td>' + rdata[i].uid + '</td>\
					<td>' + rdata[i].gid + '</td>\
					<td>' + rdata[i].login_shell + '</td>\
					<td style="text-wrap:wrap;">' + rdata[i].ps + '</td>\
					<td><a class="btlink" onclick="userdel(\'' + rdata[i].username + '\')">删除</a></td>\
				</tr>';
        }
        var tbody = '<thead>\
			<tr>\
				<th width="140">用户名</th>\
				<th width="140">home</th>\
				<th width="140">用户组</th>\
				<th width="50">uid</th>\
				<th width="50">gid</th>\
				<th width="150">登陆脚本</th>\
				<th style="overflow:hidden">描述</th>\
				<th width="50">操作</th>\
			</tr>\
		</thead>\
		<tbody>' + tbody_tr + '</tbody>';
        $("#TaskManagement").html(tbody);
        var topMsg = '';
        $("#load_average").html(topMsg).hide();
        $(".table-cont").css("height", "597px");
        show_task();
    });
}

//删除用户
function userdel(user) {
    safeMessage('删除用户【' + user + '】', '删除后可能导致您的环境无法正常运行,继续吗？', function () {
        var loadT = layer.msg('正在删除用户[' + user + ']..', {icon: 16, time: 0, shade: [0.3, '#000']});
        tmPostCallback('remove_user', {user:user}, function(rdata){
            layer.close(loadT);
            var rdata = rdata.data;
            showMsg(rdata.msg, function(){
                if (rdata.status) {
                    get_user_list();
                }
            },{icon: rdata.status ? 1 : 2});
        });
    });
}

//结束进程
function kill_process(pid, fpid) {
    if (fpid) {
        select_pid = fpid;
    }
    var w = layer.confirm('您是否要结束 (' + pid + ') 进程？', {
        btn: ['结束', '取消'], //按钮
        title: '结束' + pid,
        closeBtn: 2
    }, function () {
        var loadT = layer.msg('正在结束进程[' + pid + ']..', {icon: 16, time: 0, shade: [0.3, '#000']});
        tmPostCallback('kill_process', {pid:pid}, function(data){
            layer.close(loadT);
            var rdata = data.data;
            layer.msg(rdata.msg, {icon: rdata.status ? 1 : 2});
            if (rdata.status) {
                get_process_list();
            }
        });
    }, function () {
        layer.close(w);
    })
}

//结束进程树
function kill_process_all(pid) {
    var w = layer.confirm('您是否要结束 (' + pid + ') 进程？', {
        btn: ['结束', '取消'], //按钮
        title: '结束' + pid,
        closeBtn: 2
    }, function () {
        var loadT = layer.msg('正在结束父进程[' + pid + ']..', {icon: 16, time: 0, shade: [0.3, '#000']});
        tmPostCallback('kill_process_all', {pid:pid}, function(data){
            layer.close(loadT);
            var rdata = data.data;
            showMsg(rdata.msg, function(){
                if (rdata.status) {
                    get_process_list();
                }
            },{icon: rdata.status ? 1 : 2});            
        });
    }, function () {
        layer.close(w);
    });
}

//打开文件所在位置
function open_path(path) {
    var tmp = path.split('/');
    tmp[tmp.length - 1] = '';
    var path = '/' + tmp.join('/');
    openPath(path);
}

//删除服务
function remove_service(serviceName) {
    safeMessage('删除服务【' + serviceName + '】', '删除后可能导致您的环境无法正常运行,继续吗？', function () {
        var loadT = layer.msg('正在删除服务[' + serviceName + ']..', {icon: 16, time: 0, shade: [0.3, '#000']});
        tmPostCallback('remove_service', {serviceName:serviceName}, function(data){
            var rdata = data.data;
            layer.close(loadT);
            showMsg(rdata.msg, function(){
                if (rdata.status){
                    get_service_list();
                }
            },{icon: rdata.status ? 1 : 2})
        });
    });
}

//在线编辑文件
function online_edit_file(fileName) {
    onlineEditFile(0, fileName);
}

//删除计划任务
function remove_cron(index) {
    safeMessage('删除计划任务[' + index + ']', '删除后将无法恢复,继续吗？', function () {
        var loadT = layer.msg('正在删除计划任务..', {icon: 16, time: 0, shade: [0.3, '#000']});
        tmPostCallback('remove_cron', {index:index}, function(rdata){
            layer.close(loadT);
            var rdata = rdata.data;
            showMsg(rdata.msg, function(){
                if (rdata.status) {
                    get_cron_list();
                }
            },{icon: rdata.status ? 1 : 2});
        });
    });
}

//强制断开会话
function pkill_session(pts) {
    safeMessage('强制断开会话[' + pts + ']', '强制断开此会话吗？', function () {
        var loadT = layer.msg('正在断开会话..', {icon: 16, time: 0, shade: [0.3, '#000']});
        tmPostCallback('pkill_session', {pts:pts}, function(data){
            layer.close(loadT);

            var rdata = data.data;
            layer.msg(rdata.msg, {icon: rdata.status ? 1 : 2});
            if (rdata.status){
                get_who_list();
            }
        });
    });
}

//设置服务启动级别状态
function set_runlevel_state(runlevel, serviceName) {
    var loadT = layer.msg('正在设置服务[' + serviceName + ']..', {icon: 16, time: 0, shade: [0.3, '#000']});
    tmPostCallback('set_runlevel_state', {runlevel: runlevel,serviceName: serviceName}, function(data){
        layer.close(loadT);
        var rdata = data.data;
        showMsg(rdata.msg, function(){
            if (rdata.status) {
                get_service_list();
            }
        },{icon: rdata.status ? 1 : 2});
    });
}

//查看进程详情
function get_process_info(pid) {
    var loadT = layer.msg('正在获取进程信息[' + pid + ']..', {icon: 16, time: 0, shade: [0.3, '#000']});
    tmPostCallback('get_process_info', {pid:pid}, function(data){
        layer.close(loadT);
        var rdata = data.data;
        fileBody = '';
        for (var i = 0; i < rdata.open_files.length; i++) {
            fileBody += '<tr><td>' + rdata.open_files[i].path + '</td>\
                <td>' + rdata.open_files[i].mode + '</td>\
                <td>' + rdata.open_files[i].position + '</td>\
                <td>' + rdata.open_files[i].flags + '</td>\
                <td>' + rdata.open_files[i].fd + '</td>\
            </tr>';
        }
        var cbody = '<div class="pd15 jc-detail">\
			<div class="divtable">\
				<table class="table">\
					<tbody>\
						<tr>\
							<th width="70">名称</th><td  width="180">' + rdata.name + '</td>\
							<th width="50">PID</th><td  width="180">' + rdata.pid + '</td>\
							<th width="50">状态</th><td  width="180">' + rdata.status + '</td>\
						</tr>\
						<tr>\
							<th>父进程</th><td>' + rdata.pname + '(' + rdata.ppid + ')</td>\
							<th>用户</th><td>' + rdata.user + '</td>\
							<th>线程</th><td>' + rdata.threads + '</td>\
						</tr>\
						<tr>\
							<th>Socket</th><td>' + rdata.connects + '</td>\
							<th>io读</th><td>' + toSize(rdata.io_read_bytes) + '</td>\
							<th>io写</th><td>' + toSize(rdata.io_write_bytes) + '</td>\
						</tr>\
						<tr>\
							<th>启动时间</th><td>' + getLocalTime(rdata.create_time) + '</td>\
							<th>描述</th><td colspan="3">' + rdata.ps + '</td>\
						</tr>\
						<tr>\
							<th>启动命令</th><td colspan="5">' + rdata.comline.join(" ") + '</td>\
						</tr>\
					</tbody>\
				</table>\
			</div>\
			<h3 class="tname">内存</h3>\
			<div class="divtable">\
				<table class="table">\
					<tbody>\
						<tr>\
							<th width="70">rss</th><td width="180">' + toSize(rdata.memory_full.rss) + '</td>\
							<th width="50">pss</th><td width="180">' + toSize(rdata.memory_full.pss) + '</td>\
							<th width="50">uss</th><td width="180">' + toSize(rdata.memory_full.uss) + '</td>\
						</tr>\
						<tr>\
							<th>vms</th><td>' + toSize(rdata.memory_full.vms) + '</td>\
							<th>swap</th><td>' + toSize(rdata.memory_full.swap) + '</td>\
							<th>shared</th><td>' + toSize(rdata.memory_full.shared) + '</td>\
						</tr>\
						<tr>\
							<th>data</th><td>' + toSize(rdata.memory_full.data) + '</td>\
							<th>text</th><td>' + toSize(rdata.memory_full.text) + '</td>\
							<th>dirty</th><td>' + toSize(rdata.memory_full.dirty) + '</td>\
						</tr>\
					</tbody>\
				</table>\
			</div>\
			<h3 class="tname">打开的文件列表</h3>\
			<div class="divtable">\
				<div id="jc-file-table" class="jc-file-table" style="height:206px;overflow:auto;border:#ddd 1px solid">\
					<table class="table table-hover" style="border:none">\
						<thead>\
							<tr>\
								<th>文件</th>\
								<th>mode</th>\
								<th>position</th>\
								<th>flags</th>\
								<th>fd</th>\
							</tr>\
						</thead>\
						<tbody>' + fileBody + '</tbody>\
					</table>\
				</div>\
			</div>\
		</div>\
		<div class="mini-info">\
			<button class="btn btn-sm btn-default mr5" onclick="open_path(\'' + rdata.exe + '\')">打开文件位置</button>\
			<button class="btn btn-sm btn-default" onclick="kill_process_all(' + rdata.pid + ')">结束进程树</button>\
		</div>';

        TaskProcessLayerIndex = layer.open({
            type: 1,
            title: '进程属性[' + rdata.name + '] -- ' + rdata.exe,
            area: '750px',
            closeBtn: 2,
            shadeClose: false,
            content: cbody
        });
        show_jc_flie();
    });
}

//屏蔽指定IP
function dropAddress(address) {
    layer.confirm(lan.index.net_doup_ip_msg, {icon: 3, closeBtn: 2}, function () {
        loadT = layer.msg(lan.index.net_doup_ip_to, {icon: 16, time: 0, shade: [0.3, '#000']});
        $.post('/firewall/add_drop_address', 'type=address&protocol=tcp&port=' + address + '&ps=手动屏蔽', function (rdata) {
            layer.close(loadT);
            layer.msg(rdata.msg, {icon: rdata.status ? 1 : 2});
        });
    });
}

function show_task() {
    $(".ts-line").width($("#TaskManagement").width());
    $("#TaskManagement tbody td").click(function () {
        // console.log('---');
        $(this).parents("tr").addClass("active").siblings().removeClass("active");
    });
    var tableCont = document.querySelector('#table-cont');
    //表格固定
    var sct = tableCont.scrollTop;
    tableCont.querySelector('thead').style.transform = 'translateY(' + sct + 'px)';
    tableCont.addEventListener('scroll', scrollHandle);
}

function show_jc_flie() {
    var tableJc = document.querySelector('#jc-file-table');
    //文件表格固定
    tableJc.addEventListener('scroll', scrollHandle);
}

function scrollHandle(e) {
    var scrollTop = this.scrollTop;
    this.querySelector('thead').style.transform = 'translateY(' + scrollTop + 'px)';
}