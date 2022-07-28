function str2Obj(str){
    var data = {};
    kv = str.split('&');
    for(i in kv){
        v = kv[i].split('=');
        data[v[0]] = v[1];
    }
    return data;
}

function rsPost(method,args,callback, title){

    var _args = null; 
    if (typeof(args) == 'string'){
        _args = JSON.stringify(str2Obj(args));
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

function createSendTask(){

    layer.open({
        type: 1,
        area: ['600px','500px'],
        title: "创建发送任务",
        closeBtn: 1,
        shift: 0,
        shadeClose: false,
        btn: ['提交','取消'], 
        content:"<form class='bt-form pd20' id='fromServerPath' accept-charset='utf-8'>\
            <div class='line'>\
                <span class='tname'>服务器IP</span>\
                <div class='info-r c4'>\
                    <input class='bt-input-text' type='text' name='ip' placeholder='请输入接收服务器IP' value='' style='width:310px' />\
                </div>\
            </div>\
            <div class='line'>\
                <span class='tname'>同步目录</span>\
                <div class='info-r c4'>\
                    <input id='inputPath' class='bt-input-text mr5' type='text' name='path' value='/www/wwwroot' placeholder='请选择同步目录' style='width:310px' /><span class='glyphicon glyphicon-folder-open cursor' onclick='changePath(\"inputPath\")'></span>\
                    <span data-toggle='tooltip' data-placement='top' title='【同步目录】若不以/结尾，则表示将数据同步到二级目录，一般情况下目录路径请以/结尾' class='bt-ico-ask' style='cursor: pointer;'>?</span>\
                </div>\
            </div>\
            <div class='line'>\
                <span class='tname'>同步方式</span>\
                <div class='info-r c4'>\
                    <select class='bt-input-text' name='delete' style='width:100px'>\
                        <option value='false'>增量</option>\
                        <option value='true'>完全</option>\
                    </select>\
                    <span data-toggle='tooltip' data-placement='top' title='【同步方式】增量： 数据更改/增加时同步，且只追加和替换文件\n【同步方式】完全： 保持两端的数据与目录结构的一致性，会同步删除、追加和替换文件和目录' class='bt-ico-ask' style='cursor: pointer;'>?</span>\
                    <span style='margin-left: 20px;margin-right: 10px;'>同步周期</span>\
                    <select class='bt-input-text synchronization' name='realtime' style='width:100px'>\
                        <option value='true'>实时同步</option>\
                        <option value='false'>定时同步</option>\
                    </select>\
                </div>\
            </div>\
            <!--<div class='line'>\
                <span class='tname'>同步周期</span>\
                <div class='info-r c4'>\
                    <select class='bt-input-text synchronization' name='realtime' style='width:100px'>\
                        <option value='true'>实时同步</option>\
                        <option value='false'>定时同步</option>\
                    </select>\
                </div>\
            </div>-->\
            <div class='line' id='period' style='height:45px;display:none;'>\
                <span class='tname'>定时周期</span>\
                <div class='info-r c4'>\
                    <select class='bt-input-text pull-left mr20' name='period' style='width:100px;display:none;'>\
                        <option value='day' >每天</option>\
                        <option value='minute-n' >N分钟</option>\
                    </select>\
                    <div class='plan_hms pull-left mr20 bt-input-text hour' style='display:none;'>\
                        <span><input type='number' name='hour' value='0' maxlength='2' max='23' min='0'></span>\
                        <span class='name'>小时</span>\
                    </div>\
                    <div class='plan_hms pull-left mr20 bt-input-text minute' style='display:none;'>\
                        <span><input type='number' name='minute' value='0' maxlength='2' max='59' min='0'></span>\
                        <span class='name'>分钟</span>\
                    </div>\
                    <div class='plan_hms pull-left mr20 bt-input-text minute-n' style='display:none;'>\
                        <span><input type='number' name='minute-n' value='0' maxlength='2' max='59' min='0'></span>\
                        <span class='name'>分钟</span>\
                    </div>\
                </div>\
            </div>\
            <div class='line'>\
                <span class='tname'>限速</span>\
                <div class='info-r c4'>\
                    <input class='bt-input-text' type='number' name='bwlimit' min='0'  value='1000' style='width:100px' /> KB\
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
                        <option value='true'>开启</option>\
                        <option value='false'>关闭</option>\
                    </select>\
                    <span data-toggle='tooltip' data-placement='top' title='【压缩传输】开启后可减少带宽开销，但会增加CPU开销，如带宽充足，建议关闭此选项' class='bt-ico-ask' style='cursor: pointer;'>?</span>\
                </div>\
            </div>\
            <div class='line conn-key'>\
                <span class='tname'>接收密钥</span>\
                <div class='info-r c4'>\
                    <textarea id='mainDomain' class='bt-input-text' name='secret_key' style='width:310px;height:75px;line-height:22px' placeholder='此密钥为 接收配置[接收账号] 的密钥'></textarea>\
                </div>\
            </div>\
            <div class='line conn-user'>\
                <span class='tname'>用户名</span>\
                <div class='info-r c4'>\
                    <input class='bt-input-text' type='text' name='u_user' min='0'  value='' style='width:310px' />\
                </div>\
            </div>\
            <div class='line conn-user'>\
                <span class='tname'>密码</span>\
                <div class='info-r c4'>\
                    <input class='bt-input-text' type='text' name='u_pass' min='0'  value='' style='width:310px' />\
                </div>\
            </div>\
            <div class='line conn-user'>\
                <span class='tname'>端口</span>\
                <div class='info-r c4'>\
                    <input class='bt-input-text' type='number' name='u_port' min='0'  value='' style='width:310px' />\
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
        },
        yes:function(){
            var args = {};
            args['ip'] = $('input[name="ip"]').val();
            args['path'] = $('input[name="path"]').val();
            args['delete'] = $('input[name="delete"]').val();
            args['realtime'] = $('input[name="realtime"]').val();

            args['bwlimit'] = $('input[name="bwlimit"]').val();
            args['conn_type'] = $('input[name="conn_type"]').val();
            args['compress'] = $('input[name="compress"]').val();
            

            console.log(args);
            rsPost('lsyncd_add', args, function(rdata){
                console.log(rdata);
            });
            return false;
        }
    });
}

function rsyncdSend(){
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
                <button class="btn btn-success btn-sm" onclick="rsyncdLog();">创建本地同步</button>\
                <button class="btn btn-success btn-sm" onclick="rsyncdLog();">日志</button>\
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
            con += '<tr>'+
                '<td>' + "dd"+'</td>' +
                '<td><a class="btlink" onclick="openPath(\''+list[i]['path']+'\')">' + list[i]['path']+'</a></td>' +
                '<td>' + list[i]['ip']+":"+"cc"+'</td>' +
                '<td>' + "增量"+'</td>' +
                '<td>' + "实时" +'</td>' +
                '<td>\
                    <a class="btlink" onclick="cmdReceive(\''+list[i]['name']+'\')">同步</a>\
                    | <a class="btlink" onclick="delReceive(\''+list[i]['name']+'\')">日志</a>\
                    | <a class="btlink" onclick="delReceive(\''+list[i]['name']+'\')">过滤器</a>\
                    | <a class="btlink" onclick="delReceive(\''+list[i]['name']+'\')">编辑</a>\
                    | <a class="btlink" onclick="delReceive(\''+list[i]['name']+'\')">删除</a>\
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
    pluginStandAloneLogs("rsyncd","","run_log");
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
                '<td>' + list[i]['path']+'</td>' +
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
                        <input id='ps' class='bt-input-text' type='text' name='ps' placeholder='备注' style='width:200px'/>\
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