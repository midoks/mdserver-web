function rsPost(method,args,callback, title){

    var _args = null; 
    if (typeof(args) == 'string'){
        _args = JSON.stringify(toArrayObject(args));
    } else {
        _args = JSON.stringify(args);
    }

    var _title = '正在获取...';
    if (typeof(title) != 'undefined'){
        _title = title;
    }

    var loadT = layer.msg(_title, { icon: 16, time: 0, shade: 0.3 });
    $.post('/plugins/run', {name:'rsyncd', func:method, args:_args}, function(data) {
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

///////////////// ----------------- 发送配置 ---------------- //////////////

function createSendTask(name = ''){
    var args = {};
    args["name"] = name;
    rsPost('lsyncd_get', args, function(rdata){
        var rdata = $.parseJSON(rdata.data);
        var data = rdata.data;
        console.log(data);

        var layerName = '创建';
        if (name!=''){
            layerName = '编辑';
        }

        var compress_true = "";
        var compress_false = "";
        if (data['rsync']['compress'] == 'true'){
            compress_true = "selected";
            compress_false = "";
        } else {
            compress_true = "";
            compress_false = "selected";
        }


        var delete_true = "";
        var delete_false = "";
        if (data['delete'] == 'false'){
            delete_true = "selected";
            delete_false = "";
        } else {
            delete_true = "";
            delete_false = "selected";
        }


        var realtime_true = "";
        var realtime_false = "";
        if (data['realtime'] == 'true'){
            realtime_true = "selected";
            realtime_false = "";
        } else {
            realtime_true = "";
            realtime_false = "selected";
        }


        var period_day = "";
        var period_minute_n = "";
        if (data['period'] == 'day'){
            period_day = "selected";
            period_minute_n = "";
        } else {
            period_day = "";
            period_minute_n = "selected";
        }


        var layerID = layer.open({
            type: 1,
            area: ['600px','500px'],
            title: layerName+"发送任务",
            closeBtn: 1,
            shift: 0,
            shadeClose: false,
            btn: ['提交','取消'], 
            content:"<form class='bt-form pd20' id='fromServerPath' accept-charset='utf-8'>\
                <div class='line'>\
                    <span class='tname'>服务器IP</span>\
                    <div class='info-r c4'>\
                        <input class='bt-input-text' type='text' name='ip' placeholder='请输入接收服务器IP' value='"+data["ip"]+"' style='width:310px' />\
                    </div>\
                </div>\
                <div class='line'>\
                    <span class='tname'>同步目录</span>\
                    <div class='info-r c4'>\
                        <input id='inputPath' class='bt-input-text mr5' type='text' name='path' value='"+data["path"]+"' placeholder='请选择同步目录' style='width:310px' /><span class='glyphicon glyphicon-folder-open cursor' onclick='changePath(\"inputPath\")'></span>\
                        <span data-toggle='tooltip' data-placement='top' title='【同步目录】若不以/结尾，则表示将数据同步到二级目录，一般情况下目录路径请以/结尾' class='bt-ico-ask' style='cursor: pointer;'>?</span>\
                    </div>\
                </div>\
                <div class='line'>\
                    <span class='tname'>同步方式</span>\
                    <div class='info-r c4'>\
                        <select class='bt-input-text' name='delete' style='width:100px'>\
                            <option value='false' "+delete_true+">增量</option>\
                            <option value='true' "+delete_false+">完全</option>\
                        </select>\
                        <span data-toggle='tooltip' data-placement='top' title='【同步方式】增量： 数据更改/增加时同步，且只追加和替换文件\n【同步方式】完全： 保持两端的数据与目录结构的一致性，会同步删除、追加和替换文件和目录' class='bt-ico-ask' style='cursor: pointer;'>?</span>\
                        <span style='margin-left: 20px;margin-right: 10px;'>同步周期</span>\
                        <select class='bt-input-text synchronization' name='realtime' style='width:100px'>\
                            <option value='true' "+realtime_true+">实时同步</option>\
                            <option value='false' "+realtime_false+">定时同步</option>\
                        </select>\
                    </div>\
                </div>\
                <div class='line' id='period' style='height:45px;display:none;'>\
                    <span class='tname'>定时周期</span>\
                    <div class='info-r c4'>\
                        <select class='bt-input-text pull-left mr20' name='period' style='width:100px;'>\
                            <option value='day' "+period_day+">每天</option>\
                            <option value='minute-n' "+period_minute_n+">N分钟</option>\
                        </select>\
                        <div class='plan_hms pull-left mr20 bt-input-text hour'>\
                            <span><input class='bt-input-text' type='number' name='hour' value='"+data["hour"]+"' maxlength='2' max='23' min='0'></span>\
                            <span class='name'>小时</span>\
                        </div>\
                        <div class='plan_hms pull-left mr20 bt-input-text minute'>\
                            <span><input class='bt-input-text' type='number' name='minute' value='"+data["minute"]+"' maxlength='2' max='59' min='0'></span>\
                            <span class='name'>分钟</span>\
                        </div>\
                        <div class='plan_hms pull-left mr20 bt-input-text minute-n' style='display:none;'>\
                            <span><input class='bt-input-text' type='number' name='minute-n' value='"+data["minute-n"]+"' maxlength='2' max='59' min='0'></span>\
                            <span class='name'>分钟</span>\
                        </div>\
                    </div>\
                </div>\
                <div class='line'>\
                    <span class='tname'>限速</span>\
                    <div class='info-r c4'>\
                        <input class='bt-input-text' type='number' name='bwlimit' min='0'  value='1024' style='width:100px' /> KB\
                        <span data-toggle='tooltip' data-placement='top' title='【限速】限制数据同步任务的速度，防止因同步数据导致带宽跑高' class='bt-ico-ask' style='cursor: pointer;'>?</span>\
                        <span style='margin-left: 29px;margin-right: 10px;'>延迟</span><input class='bt-input-text' min='0' type='number' name='delay'  value='3' style='width:100px' /> 秒\
                        <span data-toggle='tooltip' data-placement='top' title='【延迟】在延迟时间周期内仅记录不同步，到达周期后一次性同步数据，以节省开销' class='bt-ico-ask' style='cursor: pointer;'>?</span>\
                    </div>\
                </div>\
                <div class='line'>\
                    <span class='tname'>连接方式</span>\
                    <div class='info-r c4'>\
                        <select class='bt-input-text' name='conn_type' style='width:100px'>\
                            <option value='key'>密钥</option>\
                            <option value='user'>帐号</option>\
                        </select>\
                        <span style='margin-left: 45px;margin-right: 10px;'>压缩传输</span>\
                        <select class='bt-input-text' name='compress' style='width:100px'>\
                            <option value='true' "+compress_true+">开启</option>\
                            <option value='false' "+compress_false+">关闭</option>\
                        </select>\
                        <span data-toggle='tooltip' data-placement='top' title='【压缩传输】开启后可减少带宽开销，但会增加CPU开销，如带宽充足，建议关闭此选项' class='bt-ico-ask' style='cursor: pointer;'>?</span>\
                    </div>\
                </div>\
                <div class='line conn-key'>\
                    <span class='tname'>接收密钥</span>\
                    <div class='info-r c4'>\
                        <textarea id='mainDomain' class='bt-input-text' name='secret_key' style='width:310px;height:75px;line-height:22px' placeholder='此密钥为 接收配置[接收账号] 的密钥'>"+data['secret_key']+"</textarea>\
                    </div>\
                </div>\
                <div class='line conn-user'>\
                    <span class='tname'>用户名</span>\
                    <div class='info-r c4'>\
                        <input class='bt-input-text' type='text' name='u_user' min='0'  value='"+data["name"]+"' style='width:310px' />\
                    </div>\
                </div>\
                <div class='line conn-user'>\
                    <span class='tname'>密码</span>\
                    <div class='info-r c4'>\
                        <input class='bt-input-text' type='text' name='u_pass' min='0'  value='"+data["password"]+"' style='width:310px' />\
                    </div>\
                </div>\
                <div class='line conn-user'>\
                    <span class='tname'>端口</span>\
                    <div class='info-r c4'>\
                        <input class='bt-input-text' type='number' name='u_port' min='0'  value='"+data["rsync"]["port"]+"' style='width:310px' />\
                    </div>\
                </div>\
                <ul class=\"help-info-text c7\">\
                </ul>\
              </form>",
            success:function(){
                $('[data-toggle="tooltip"]').tooltip();

                $(".conn-user").hide();
                $("select[name='conn_type']").change(function(){
                    if($(this).val() == 'key'){
                        $(".conn-user").hide();
                        $(".conn-key").show();
                    }else{
                        $(".conn-user").show();
                        $(".conn-key").hide();
                    }
                });


                var selVal = $('.synchronization option:selected').val();
                if (selVal == "false"){
                    $('#period').show();
                }else{
                    $('#period').hide();
                    $('.hour input,.minute input').val('0');
                    $('.minute-n input').val('1');
                }   
                $('.synchronization').change(function(event) {
                    var selVal = $('.synchronization option:selected').val();
                    if (selVal == "false"){
                        $('#period').show();
                    }else{
                        $('#period').hide();
                        $('.hour input,.minute input').val('0');
                        $('.minute-n input').val('1');
                    }
                });

                $("select[name='delete']").change(function(){
                    if($(this).val() == 'true'){
                        var mpath = $('input[name="path"]').val();
                        var msg = '<div><span style="color:orangered;">警告：您选择了完全同步，将会使本机同步与目标机器指定目录的文件保持一致，'
                            +'<br />请确认目录设置是否有误，一但设置错误，可能导致目标机器的目录文件被删除!</span>'
                            +'<br /><br /> <span style="color:red;">注意： 同步程序将本机目录：'
                            +mpath+'的所有数据同步到目标服务器，若目标服务器的同步目录存在其它文件将被删除!</span> <br /><br /> 已了解风险，请按确定继续</div>';

                        layer.confirm(msg,{title:'数据安全风险警告',icon:2,closeBtn: 1,shift: 5,
                        btn2:function(){
                            setTimeout(function(){$($("select[name='delete']").children("option")[0]).prop('selected',true);},100);
                        }
                        });
                    }
                });


                var selVal = $('#period select option:selected').val();
                if (selVal == 'day'){
                    $('.hour,.minute').show();
                    if ($('.hour input').val() == ''){
                        $('.hour input,.minute input').val('0');
                    }
                    $('.minute-n').hide();
                }else{
                    $('.hour,.minute').hide();
                    $('.minute-n').show();
                    if ($('.minute-n input').val() == ''){
                        $('.minute-n input').val('1');
                    }
                }
                $('#period').change(function(event) {
                    var selVal = $('#period select option:selected').val();
                    if (selVal == 'day'){
                        $('.hour,.minute').show();
                        if ($('.hour input').val() == ''){
                            $('.hour input,.minute input').val('0');
                        }
                        $('.minute-n').hide();
                    }else{
                        $('.hour,.minute').hide();
                        $('.minute-n').show();
                        if ($('.minute-n input').val() == ''){
                            $('.minute-n input').val('1');
                        }
                    }
                });
            },
            yes:function(index){
                var args = {};
                var conn_type = $("select[name='conn_type']").val();
        
                if(conn_type == 'key'){
                    if ( $('textarea[name="secret_key"]').val() != ''){
                        args['secret_key'] = $('textarea[name="secret_key"]').val();
                    } else {
                        layer.msg('请输入接收密钥！');
                        return false;
                    }
                } else {
                    args['sname'] = $("input[name='u_user']").val();
                    args['password'] = $("input[name='u_pass']").val();
                    var port = Number($("input[name='u_port']").val());
                    args['port'] = port;
                    if (!args['sname'] || !args['password'] || !args['port']){
                        layer.msg('请输入帐号、密码、端口信息');
                        return false;
                    }
                }

                if ($('input[name="ip"]').val() == ''){
                    layer.msg('请输入服务器IP地址！');
                    return false;
                }

                args['sname'] = $("input[name='u_user']").val();
                args['password'] = $("input[name='u_pass']").val();
                var port = Number($("input[name='u_port']").val());
                args['port'] = port;

                
                args['ip'] = $('input[name="ip"]').val();
                args['path'] = $('input[name="path"]').val();
                args['delete'] = $('select[name="delete"]').val();
                args['realtime'] = $('select[name="realtime"]').val();
                args['delay'] = $('input[name="delay"]').val();

                args['bwlimit'] = $('input[name="bwlimit"]').val();
                args['conn_type'] = $('select[name="conn_type"]').val();
                args['compress'] = $('select[name="compress"]').val();

                args['period'] = $('select[name="period"]').val(); 
                args['hour'] = $('input[name="hour"]').val();
                args['minute'] = $('input[name="minute"]').val();
                args['minute-n'] = $('input[name="minute-n"]').val();

                rsPost('lsyncd_add', args, function(rdata){
                    var rdata = $.parseJSON(rdata.data);
                    layer.msg(rdata.msg,{icon:rdata.status?1:2,time:2000,shade: [0.3, '#000']});

                    if (rdata.status){
                         setTimeout(function(){
                            layer.close(index);
                            lsyncdSend();
                         },2000);
                        return;
                    }
                });
                return true;
            }
        });
    });
}

function lsyncdDelete(name){
    safeMessage('删除['+name+']', '您真的要删除['+name+']吗？', function(){
        var args = {};
        args['name'] = name;
        rsPost('lsyncd_delete', args, function(rdata){
            var rdata = $.parseJSON(rdata.data);
            layer.msg(rdata.msg,{icon:rdata.status?1:2,time:2000,shade: [0.3, '#000']});
            setTimeout(function(){lsyncdSend();},2000);
        });
    });
}


function lsyncdRun(name){
    var args = {};
    args["name"] = name;
    rsPost('lsyncd_run', args, function(rdata){
        var rdata = $.parseJSON(rdata.data);
        layer.msg(rdata.msg,{icon:rdata.status?1:2,time:2000,shade: [0.3, '#000']});
    });
}

function lsyncdLog(name){
    var args = {};
    args["name"] = name;
    pluginStandAloneLogs("rsyncd", '', "lsyncd_log", JSON.stringify(args));
}


function lsyncdExclude(name){
    layer.open({
        type:1,
        title:'过滤器',
        area: '400px', 
        shadeClose:false,
        closeBtn:2,
        content:'<div class="lsyncd_exclude">\
                <div style="overflow:hidden;">\
                    <fieldset>\
                        <legend>排除的文件和目录</legend>\
                        <input type="text" class="bt-input-text mr5" data-type="exclude" title="例如：/home/www/" placeholder="例如：*.log" style="width:305px;">\
                        <button data-type="exclude" class=" addList btn btn-default btn-sm">添加</button>\
                        <div class="table-overflow">\
                            <table class="table table-hover BlockList"><tbody></tbody></table>\
                        </div>\
                    </fieldset>\
                </div>\
                <div>\
                    <ul class="help-info-text c7" style="list-style-type:decimal;">\
                        <li>排除的文件和目录是指当前目录下不需要同步的目录或者文件</li>\
                        <li>如果规则以斜线 <code>/</code>开头，则从头开始要匹配全部</li>\
                        <li>如果规则以 <code>/</code>结尾，则要匹配监控路径的末尾</li>\
                        <li><code>?</code> 匹配任何字符，但不包括<code>/</code></li>\
                        <li><code>*</code> 匹配0或多个字符，但不包括<code>/</code></li>\
                        <li><code>**</code> 匹配0或多个字符，可以是<code>/</code></li>\
                    </ul>\
                </div>\
            </div>'
    });

    function getIncludeExclude(mName){
        loadT = layer.msg('正在获取数据...',{icon:16,time:0,shade: [0.3, '#000']});
        rsPost('lsyncd_get_exclude',{"name":mName}, function(rdata) {
            layer.close(loadT);

            var rdata = $.parseJSON(rdata.data);
            var res = rdata.data;

            var list=''
            for (var i = 0; i < res.length; i++) {
                list += '<tr><td>'+ res[i] +'</td><td><a href="javascript:;" data-type='+ mName +' class="delList">删除</a></td></tr>';
            }
            $('.lsyncd_exclude .BlockList tbody').empty().append(list);
        });
    }
    getIncludeExclude(name);


    function addArgs(name,exclude){
        loadT = layer.msg('正在添加...',{icon:16,time:0,shade: [0.3, '#000']});
        rsPost('lsyncd_add_exclude', {name:name,exclude:exclude}, function(res){
            layer.close(loadT);

            console.log('addArgs:',res);

            if (res.status){
                getIncludeExclude(name);
                $('.lsyncd_exclude input').val('');
                layer.msg(res.msg);
            }else{
                layer.msg(res.msg);
            }
        });
    }
    $('.addList').click(function(event) {
        var val = $(this).prev().val();
        if(val == ''){
            layer.msg('当前输入内容为空,请输入');
            return false;
        }
        addArgs(name,val);
    });
    $('.lsyncd_exclude input').keyup(function(event){
        if (event.which == 13){
            var val = $(this).val();
            if(val == ''){
                layer.msg('当前输入内容为空,请输入');
                return false;
            }
            addArgs(name,val);
        }
    });


    $('.lsyncd_exclude').on('click', '.delList', function(event) {
        loadT = layer.msg('正在删除...',{icon:16,time:0,shade: [0.3, '#000']});
        var val = $(this).parent().prev().text();
        rsPost('lsyncd_remove_exclude',{"name":name,exclude:val}, function(rdata) {
            layer.close(loadT);

            console.log(rdata)
            var rdata = $.parseJSON(rdata.data);
            var res = rdata.data;

            var list=''
            for (var i = 0; i < res.length; i++) {
                list += '<tr><td>'+ res[i] +'</td><td><a href="javascript:;" data-type='+ name +' class="delList">删除</a></td></tr>';
            }
            $('.lsyncd_exclude .BlockList tbody').empty().append(list);
        });
    });
}

function lsyncdConfLog(){
    pluginRollingLogs("rsyncd","","lsyncd_conf_log");;
}

function lsyncdSend(){
    rsPost('lsyncd_list', '', function(data){
        var rdata = $.parseJSON(data.data);
        console.log(rdata);
        if (!rdata.status){
            layer.msg(rdata.msg,{icon:rdata.status?1:2,time:2000,shade: [0.3, '#000']});
            return;
        }
        var list = rdata.data.list;
        var con = '';

        con += '<div style="padding-top:1px;">\
                <button class="btn btn-success btn-sm" onclick="createSendTask();">创建发送任务</button>\
                <button class="btn btn-success btn-sm" onclick="lsyncdConfLog();">自动同步日志</button>\
            </div>';

        con += '<div class="divtable" style="margin-top:5px;"><table class="table table-hover" width="100%" cellspacing="0" cellpadding="0" border="0">';
        con += '<thead><tr>';
        con += '<th>名称(标识)</th>';
        con += '<th>源目录</th>';
        con += '<th>同步到</th>';
        con += '<th>模式</th>';
        con += '<th>周期</th>';
        con += '<th>操作</th>';
        con += '</tr></thead>';

        con += '<tbody>';

        

        for (var i = 0; i < list.length; i++) {
            var mode = '增量';
            if (list[i]['delete'] == 'true'){
                mode = '完全';
            } else {
                mode = '增量';
            }

            var period = "实时";
            if (list[i]['realtime'] == 'true'){
                period = '实时';
            } else {
                period = '定时';
            }

            con += '<tr>'+
                '<td>' + list[i]['name']+'</td>' +
                '<td><a class="btlink overflow_hide" style="width:40px;" onclick="openPath(\''+list[i]['path']+'\')">' + list[i]['path']+'</a></td>' +
                '<td>' + list[i]['ip']+":"+list[i]['name']+'</td>' +
                '<td>' + mode+'</td>' +
                '<td>' + period +'</td>' +
                '<td>\
                    <a class="btlink" onclick="lsyncdRun(\''+list[i]['name']+'\')">同步</a>\
                    | <a class="btlink" onclick="lsyncdLog(\''+list[i]['name']+'\')">手动日志</a>\
                    | <a class="btlink" onclick="lsyncdExclude(\''+list[i]['name']+'\')">过滤器</a>\
                    | <a class="btlink" onclick="createSendTask(\''+list[i]['name']+'\')">编辑</a>\
                    | <a class="btlink" onclick="lsyncdDelete(\''+list[i]['name']+'\')">删除</a>\
                </td>\
                </tr>';
        }

        con += '</tbody>';
        con += '</table></div>';

        $(".soft-man-con").html(con);
    });
}



///////////////// ----------------- 接收配置 ---------------- //////////////
function rsyncdConf(){
    rsPost('conf', {}, function(rdata){
        rpath = rdata['data'];
        if (rdata['status']){
            onlineEditFile(0, rpath);
        } else {
            layer.msg(rdata.msg,{icon:1,time:2000,shade: [0.3, '#000']});
        }        
    });
}

function rsyncdLog(){
    pluginRollingLogs("rsyncd","","run_log");
}


function rsyncdReceive(){
	rsPost('rec_list', '', function(data){
		var rdata = $.parseJSON(data.data);
		if (!rdata.status){
			layer.msg(rdata.msg,{icon:rdata.status?1:2,time:2000,shade: [0.3, '#000']});
			return;
		}
		// console.log(rdata);
		var list = rdata.data;
		var con = '';

        con += '<div style="padding-top:1px;">\
                <button class="btn btn-success btn-sm" onclick="rsyncdConf();">配置</button>\
                <button class="btn btn-success btn-sm" onclick="rsyncdLog();">日志</button>\
            </div>';

        con += '<div class="divtable" style="margin-top:5px;"><table class="table table-hover" width="100%" cellspacing="0" cellpadding="0" border="0">';
        con += '<thead><tr>';
        con += '<th>服务名</th>';
        con += '<th>路径</th>';
        con += '<th>备注</th>';
        con += '<th>操作(<a class="btlink" onclick="addReceive()">添加</a>)</th>';
        con += '</tr></thead>';

        con += '<tbody>';

        //<a class="btlink" onclick="modReceive(\''+list[i]['name']+'\')">编辑</a>
        for (var i = 0; i < list.length; i++) {
            con += '<tr>'+
                '<td>' + list[i]['name']+'</td>' +
                '<td><a class="btlink overflow_hide" onclick="openPath(\''+list[i]['path']+'\')">' + list[i]['path']+'</a></td>' +
                '<td>' + list[i]['comment']+'</td>' +
                '<td>\
                    <a class="btlink" onclick="cmdRecCmd(\''+list[i]['name']+'\')">命令</a>\
                	| <a class="btlink" onclick="cmdRecSecretKey(\''+list[i]['name']+'\')">密钥</a>\
                    | <a class="btlink" onclick="addReceive(\''+list[i]['name']+'\')">编辑</a>\
                	| <a class="btlink" onclick="delReceive(\''+list[i]['name']+'\')">删除</a></td>\
                </tr>';
        }

        con += '</tbody>';
        con += '</table></div>';

        $(".soft-man-con").html(con);
	});
}


function addReceive(name = ""){
    rsPost('get_rec',{"name":name},function(rdata) {
        var rdata = $.parseJSON(rdata.data);
        var data = rdata.data;

        var readonly = "";
        if (name !=""){
            readonly = 'readonly="readonly"'
        }

        var loadOpen = layer.open({
            type: 1,
            title: '创建接收',
            area: '400px',
            btn:['确认','取消'],
            content:"<div class='bt-form pd20 c6'>\
                <div class='line'>\
                    <span class='tname'>项目名</span>\
                    <div class='info-r c4'>\
                        <input id='name' value='"+data["name"]+"' class='bt-input-text' type='text' name='name' placeholder='项目名' style='width:200px' "+readonly+"/>\
                    </div>\
                </div>\
                <div class='line'>\
                    <span class='tname'>密钥</span>\
                    <div class='info-r c4'>\
                        <input id='MyPassword' value='"+data["pwd"]+"' class='bt-input-text' type='text' name='pwd' placeholder='密钥' style='width:200px'/>\
                        <span title='随机密码' class='glyphicon glyphicon-repeat cursor' onclick='repeatPwd(16)'></span>\
                    </div>\
                </div>\
                <div class='line'>\
                    <span class='tname'>同步到</span>\
                    <div class='info-r c4'>\
                        <input id='inputPath' value='"+data["path"]+"' class='bt-input-text' type='text' name='path' placeholder='/' style='width:200px'/>\
                        <span class='glyphicon glyphicon-folder-open cursor' onclick=\"changePath('inputPath')\"></span>\
                    </div>\
                </div>\
                <div class='line'>\
                    <span class='tname'>备注</span>\
                    <div class='info-r c4'>\
                        <input id='ps' class='bt-input-text' type='text' name='ps' value='"+data["comment"]+"' placeholder='备注' style='width:200px'/>\
                    </div>\
                </div>\
            </div>",
            success:function(layero, index){},
            yes:function(){
                var args = {};
                args['name'] = $('#name').val();
                args['pwd'] = $('#MyPassword').val();
                args['path'] = $('#inputPath').val();
                args['ps'] = $('#ps').val();
                var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });
                rsPost('add_rec', args, function(data){
                    var rdata = $.parseJSON(data.data);
                    layer.close(loadOpen);
                    layer.msg(rdata.msg,{icon:rdata.status?1:2,time:2000,shade: [0.3, '#000']});
                    setTimeout(function(){rsyncdReceive();},2000);
                });
            }
        });
    })
}


function delReceive(name){
	safeMessage('删除['+name+']', '您真的要删除['+name+']吗？', function(){
		var _data = {};
		_data['name'] = name;
		rsPost('del_rec', _data, function(data){
            var rdata = $.parseJSON(data.data);
            layer.msg(rdata.msg,{icon:rdata.status?1:2,time:2000,shade: [0.3, '#000']});
            setTimeout(function(){rsyncdReceive();},2000);
        });
	});
}

function cmdRecSecretKey(name){
	var _data = {};
	_data['name'] = name;
	rsPost('cmd_rec_secret_key', _data, function(data){
        var rdata = $.parseJSON(data.data);
	    layer.open({
	        type: 1,
	        title: '接收密钥',
	        area: '400px',
	        content:"<div class='bt-form pd20 pb70 c6'><textarea class='form-control' rows='6' readonly='readonly'>"+rdata.data+"</textarea></div>"
    	});
    });
}

function cmdRecCmd(name){
    var _data = {};
    _data['name'] = name;
    rsPost('cmd_rec_cmd', _data, function(data){
        var rdata = $.parseJSON(data.data);
        layer.open({
            type: 1,
            title: '接收命令例子',
            area: '400px',
            content:"<div class='bt-form pd20 pb70 c6'>"+rdata.data+"</div>"
        });
    });
}


function rsRead(){
	var readme = '<ul class="help-info-text c7">';
    readme += '<li>如需将其他服务器数据同步到本地服务器，请在接受配置中 "创建接收任务" </li>';
    readme += '<li>如果开启防火墙,需要放行873端口</li>';
    readme += '</ul>';

    $('.soft-man-con').html(readme);   
}