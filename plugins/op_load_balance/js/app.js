function ooPost(method,args,callback){
    var _args = null; 
    if (typeof(args) == 'string'){
        _args = JSON.stringify(toArrayObject(args));
    } else {
        _args = JSON.stringify(args);
    }

    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });
    $.post('/plugins/run', {name:'op_load_balance', func:method, args:_args}, function(data) {
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

function ooAsyncPost(method,args){
    var _args = null; 
    if (typeof(args) == 'string'){
        _args = JSON.stringify(toArrayObject(args));
    } else {
        _args = JSON.stringify(args);
    }
    return syncPost('/plugins/run', {name:'op_load_balance', func:method, args:_args}); 
}

function ooPostCallbak(method, args, callback){
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });

    var req_data = {};
    req_data['name'] = 'op_load_balance';
    req_data['func'] = method;
    args['version'] = '1.0';
 
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

function addNode(){
    layer.open({
        type: 1,
        area: ['450px','580px'],
        title: '添加节点',
        closeBtn: 1,
        shift: 5,
        shadeClose: true,
        btn:['提交','关闭'],
        content: "<form class='bt-form pd20'>\
            <div class='line'>\
                <span class='tname'>IP地址</span>\
                <div class='info-r'>\
                    <input name='ip' class='bt-input-text mr5' placeholder='负载名称,可以是英文字母和下划线,不能使用中文' type='text' style='width:250px' value='127.0.0.1'>\
                </div>\
            </div>\
            <div class='line'>\
                <span class='tname'>端口</span>\
                <div class='info-r'>\
                    <input name='port' class='bt-input-text mr5' type='text' style='width:250px' value='80'>\
                </div>\
            </div>\
            <div class='line'>\
                <span class='tname'>验证文件路径</span>\
                <div class='info-r'>\
                    <input name='path' class='bt-input-text mr5' type='text' style='width:250px' value='/'>\
                </div>\
            </div>\
            <div class='line'>\
                <span class='tname'>节点状态</span>\
                <div class='info-r'>\
                    <select name='state'>\
                        <option value='1'>参与者</option>\
                        <option value='2'>备份</option>\
                        <option value='0'>停用</option>\
                    </select>\
                </div>\
            </div>\
            <div class='line'>\
                <span class='tname'>权重</span>\
                <div class='info-r'>\
                    <input name='weight' class='bt-input-text mr5' type='text' style='width:250px' value='1'>\
                </div>\
            </div>\
            <div class='line'>\
                <span class='tname'>阈值</span>\
                <div class='info-r'>\
                    <input name='max_fails' class='bt-input-text mr5' type='text' style='width:250px' value='2'>次\
                </div>\
            </div>\
            <div class='line'>\
                <span class='tname'>恢复时间</span>\
                <div class='info-r'>\
                    <input name='fail_timeout' class='bt-input-text mr5' type='text' style='width:250px' value='10'>秒\
                </div>\
            </div>\
            <ul style='margin-left:10px' class='help-info-text c7'>\
                <li>备份状态: 指当其它节点都无法使用时才会使用此节点</li>\
                <li>参与状态: 正常参与负载均衡,请至少添加1个普通节点</li>\
                <li>验证文件路径: 用于检查文件路径地址是否可用</li>\
                <li>IP地址: 仅支持IP地址,否则无法正常参与负载均衡</li>\
                <li>阈值: 在恢复时间的时间段内，如果OpenResty与节点通信尝试失败的次数达到此值，OpenResty就认为服务器不可用</li>\
            </ul>\
        </form>",
        success:function(){
        },
        yes:function(index) {

            var ip = $('input[name="ip"]').val();
            var port = $('input[name="port"]').val();
            var path = $('input[name="path"]').val();
            var state = $('select[name="state"]').val();
            var weight = $('input[name="weight"]').val();
            var max_fails = $('input[name="max_fails"]').val();
            var fail_timeout = $('input[name="fail_timeout"]').val();

            ooPost('check_url', {ip:ip,port:port,path:path},function(rdata){             
                var rdata = $.parseJSON(rdata.data);
                showMsg(rdata.msg, function(){
                    if (rdata.status){
                        layer.close(index);
                        $('#nodecon .nulltr').hide();

                        var tbody = '<tr>';
                        tbody +='<td>'+ip+'</td>';
                        tbody +='<td>'+port+'</td>';
                        tbody +='<td>'+path+'</td>';

                        tbody +="<td><select name='state'>";
                        var state_option_list = {
                            '1':'参与者',
                            '2':'备份',
                            '0':'停用',
                        }
                        for (i in state_option_list) {
                            if (i == state){
                                tbody +="<option value='"+i+"' selected>"+state_option_list[i]+"</option>";
                            } else{
                                tbody +="<option value='"+i+"'>"+state_option_list[i]+"</option>";
                            }
                        }
                        tbody +="</select></td>";

                        tbody +='<td><input type="number" name="weight" value="'+weight+'" style="width:50px"></td>';
                        tbody +='<td><input type="number" name="max_fails" value="'+max_fails+'" style="width:50px"></td>';
                        tbody +='<td><input type="number" name="fail_timeout" value="'+fail_timeout+'" style="width:50px"></td>';
                        tbody +='<td class="text-right" width="50"><a class="btlink minus delete">删除</a></td>';
                        tbody += '</tr>';
                        $('#nodecon').append(tbody);

                        $('#nodecon .delete').click(function(){
                            $(this).parent().parent().remove();
                            if ($('#nodecon tr').length == 1 ){
                                $('#nodecon .nulltr').show();
                            }
                        });
                    }
                },{ icon: rdata.status ? 1 : 2 }, 2000);
            });
        }
    });
}

function addBalance(){
    layer.open({
        type: 1,
        area: ['750px','460px'],
        title: '创建负载',
        closeBtn: 1,
        shift: 5,
        shadeClose: true,
        btn:['提交','关闭'],
        content: "<form class='bt-form pd20'>\
            <div class='line'>\
                <span class='tname'>域名</span>\
                <div class='info-r'><textarea name='load_domain' class='bt-input-text mr5' placeholder='' style='width:95%;resize: none;height:90px;line-height:20px;'></textarea></div>\
            </div>\
            <div class='line'>\
                <span class='tname'>负载名称</span>\
                <div class='info-r'>\
                    <input name='upstream_name' class='bt-input-text mr5' placeholder='负载名称,可以是英文字母和下划线,不能使用中文' type='text' style='width:95%' value=''>\
                </div>\
            </div>\
            <div class='line'>\
                <span class='tname'>节点调度</span>\
                <div class='info-r'>\
                    <select name='node_algo'>\
                        <option value='polling'>轮询[默认]</option>\
                        <option value='ip_hash'>ip_hash</option>\
                        <option value='fair'>fair</option>\
                        <option value='url_hash'>url_hash</option>\
                        <option value='least_conn'>least_conn</option>\
                    </select>\
                </div>\
            </div>\
            <div class='line'>\
                <span class='tname'>节点健康检查</span>\
                <div class='info-r'>\
                    <input type='checkbox' name='node_health_check' checked>\
                </div>\
            </div>\
            <div class='line'>\
                <span class='tname'>节点</span>\
                <div class='info-r'>\
                    <div class='table-con divtable' style='max-height:120px;overflow:auto; margin-bottom:8px;width:95%'>\
                    <table class='table table-hover' id='fixTable3'>\
                    <thead>\
                        <tr>\
                            <th width='120'>IP地址</th>\
                            <th width='60'>端口</th>\
                            <th width='120'>验证路径</th>\
                            <th width='60'>状态</th>\
                            <th width='60'>权重</th>\
                            <th width='60'>阀值</th>\
                            <th width='120'>恢复时间</th>\
                            <th width='80' class='text-right'>操作</th>\
                        </tr>\
                    </thead>\
                    <tbody id='nodecon'>\
                        <tr class='nulltr'>\
                            <td colspan='8' align='center'>当前节点为空，请至少添加一个普通节点</td>\
                        </tr>\
                    </tbody>\
                    </table>\
                    </div>\
                    <span class='btn btn-success btn-sm add_node' style='vertical-align:0'>添加节点</span>\
                </div>\
            </div>\
        </form>",
        success:function(){
            $('textarea[name="load_domain"]').attr('placeholder','每行填写一个域名，默认为80端口。\n泛解析添加方法 *.domain.com\n如另加端口格式为 www.domain.com:88');
            var rval = getRandomString(6);
            $('input[name="upstream_name"]').val('load_balance_'+rval);

            $('.add_node').click(function(){
                addNode();
            });
        },
        yes:function(index) {
            var data = {};

            var upstream_name = $('input[name="upstream_name"]').val();
            if (upstream_name == ''){
                layer.msg('负载名称不能为空!',{icon:0,time:2000,shade: [0.3, '#000']});
                return;
            }

            var domain = $('textarea[name="load_domain"]').val().replace('http://','').replace('https://','').split("\n");
            if (domain[0] == ''){
                layer.msg('域名不能为空!',{icon:0,time:2000,shade: [0.3, '#000']});
                return;
            }

            var domainlist = '';
            for(var i=1; i<domain.length; i++){
                domainlist += '"'+domain[i]+'",';
            }
            domain ='{"domain":"'+domain[0]+'","domainlist":['+domainlist+'],"count":'+domain.length+'}';//拼接json
            data['domain'] = domain;
            data['upstream_name'] = upstream_name;

            data['node_algo'] = $('select[name="node_algo"]').val();

            data['node_health_check'] = 'fail';
            if ($('input[name="node_health_check"]').prop('checked')){
                data['node_health_check'] = 'ok';
            }

            var node_list = [];
            $('#nodecon tr').each(function(){

                var ip = $(this).find('td').eq(0).text();
                var port = $(this).find('td').eq(1).text();

                if (port == ''){return;}

                var path = $(this).find('td').eq(2).text();
                var state = $(this).find('select[name="state"]').val();
                var weight = $(this).find('input[name="weight"]').val();
                var max_fails = $(this).find('input[name="max_fails"]').val();
                var fail_timeout = $(this).find('input[name="fail_timeout"]').val();

                var tmp = {
                    ip:ip,
                    port:port,
                    path:path,
                    state:state,
                    weight:weight,
                    max_fails:max_fails,
                    fail_timeout:fail_timeout,
                }
                node_list.push(tmp);
            });
            data['node_list'] = node_list;
            ooPostCallbak('add_load_balance', data, function(rdata){
                var rdata = $.parseJSON(rdata.data);
                showMsg(rdata.msg, function(){
                    layer.close(index);
                    loadBalanceListRender();
                },{ icon: rdata.status ? 1 : 2 }, 2000);
            });
        }
    });
}

function editBalance(data, row){
    layer.open({
        type: 1,
        area: ['750px','400px'],
        title: '编辑负载',
        closeBtn: 1,
        shift: 5,
        shadeClose: true,
        btn:['提交','关闭'],
        content: "<form class='bt-form pd20'>\
            <div class='line'>\
                <span class='tname'>负载名称</span>\
                <div class='info-r'><input name='upstream_name' class='bt-input-text mr5' type='text' style='width:95%;background: rgb(238, 238, 238);' value='' readonly></div>\
            </div>\
            <div class='line'>\
                <span class='tname'>节点调度</span>\
                <div class='info-r'>\
                    <select name='node_algo'>\
                        <option value='polling'>轮询[默认]</option>\
                        <option value='ip_hash'>ip_hash</option>\
                        <option value='fair'>fair</option>\
                        <option value='url_hash'>url_hash</option>\
                        <option value='least_conn'>least_conn</option>\
                    </select>\
                </div>\
            </div>\
            <div class='line'>\
                <span class='tname'>节点健康检查</span>\
                <div class='info-r'>\
                    <input type='checkbox' name='node_health_check'>\
                </div>\
            </div>\
            <div class='line'>\
                <span class='tname'>节点</span>\
                <div class='info-r'>\
                    <div class='table-con divtable' style='max-height:120px;overflow:auto; margin-bottom:8px;width:95%'>\
                    <table class='table table-hover' id='fixTable3'>\
                    <thead>\
                        <tr>\
                            <th width='120'>IP地址</th>\
                            <th width='60'>端口</th>\
                            <th width='120'>验证路径</th>\
                            <th width='60'>状态</th>\
                            <th width='60'>权重</th>\
                            <th width='60'>阀值</th>\
                            <th width='120'>恢复时间</th>\
                            <th width='80' class='text-right'>操作</th>\
                        </tr>\
                    </thead>\
                    <tbody id='nodecon'>\
                        <tr class='nulltr'>\
                            <td colspan='8' align='center'>当前节点为空，请至少添加一个普通节点</td>\
                        </tr>\
                    </tbody>\
                    </table>\
                    </div>\
                    <span class='btn btn-success btn-sm add_node' style='vertical-align:0'>添加节点</span>\
                </div>\
            </div>\
        </form>",
        success:function(){
            $('input[name="upstream_name"]').val(data['upstream_name']);
            $('select[name="node_algo"]').val(data['node_algo']);

            $('input[name="node_health_check"]').prop('checked',false);
            if (data['node_health_check'] == 'ok'){
                $('input[name="node_health_check"]').prop('checked',true);
            }

            var node_list = data['node_list'];
            if (node_list.length>0){
                $('#nodecon .nulltr').hide();
            }

            var state_option_list = {
                '1':'参与者',
                '2':'备份',
                '0':'停用',
            }

            for (var n in  node_list) {

                var tbody = '<tr>';
                tbody +='<td>'+node_list[n]['ip']+'</td>';
                tbody +='<td>'+node_list[n]['port']+'</td>';
                tbody +='<td>'+node_list[n]['path']+'</td>';

                tbody +="<td><select name='state'>";
                
                for (i in state_option_list) {
                    if (i == node_list[n]['state']){
                        tbody +="<option value='"+i+"' selected>"+state_option_list[i]+"</option>";
                    } else{
                        tbody +="<option value='"+i+"'>"+state_option_list[i]+"</option>";
                    }
                }
                tbody +="</select></td>";

                tbody +='<td><input type="number" name="weight" value="'+node_list[n]['weight']+'" style="width:50px"></td>';
                tbody +='<td><input type="number" name="max_fails" value="'+node_list[n]['max_fails']+'" style="width:50px"></td>';
                tbody +='<td><input type="number" name="fail_timeout" value="'+node_list[n]['fail_timeout']+'" style="width:50px"></td>';
                tbody +='<td class="text-right" width="50"><a class="btlink minus delete">删除</a></td>';
                tbody += '</tr>';
                $('#nodecon').append(tbody);
            }

            $('#nodecon .delete').click(function(){
                $(this).parent().parent().remove();
                if ($('#nodecon tr').length == 1 ){
                    $('#nodecon .nulltr').show();
                }
            });

            $('.add_node').click(function(){
                addNode();
            });
        },
        yes:function(index) {
            var data = {};

            data['node_algo'] = $('select[name="node_algo"]').val();
            data['node_health_check'] = 'fail';
            if ($('input[name="node_health_check"]').prop('checked')){
                data['node_health_check'] = 'ok';
            }

            var node_list = [];
            $('#nodecon tr').each(function(){

                var ip = $(this).find('td').eq(0).text();
                var port = $(this).find('td').eq(1).text();

                if (port == ''){return;}

                var path = $(this).find('td').eq(2).text();
                var state = $(this).find('select[name="state"]').val();
                var weight = $(this).find('input[name="weight"]').val();
                var max_fails = $(this).find('input[name="max_fails"]').val();
                var fail_timeout = $(this).find('input[name="fail_timeout"]').val();

                var tmp = {
                    ip:ip,
                    port:port,
                    path:path,
                    state:state,
                    weight:weight,
                    max_fails:max_fails,
                    fail_timeout:fail_timeout,
                }
                node_list.push(tmp);
            });
            data['node_list'] = node_list;
            data['row'] = row;
            ooPostCallbak('edit_load_balance', data, function(rdata){
                var rdata = $.parseJSON(rdata.data);
                showMsg(rdata.msg, function(){
                    layer.close(index);
                    loadBalanceListRender();
                },{ icon: rdata.status ? 1 : 2 }, 2000);
            });
        }
    });
}

function loadBalanceListRender(){
    ooPost('load_balance_list', {}, function(rdata){
        var rdata = $.parseJSON(rdata.data);
        var alist = rdata.data;

        var tbody = '';
        for (var i = 0; i < alist.length; i++) {
            tbody += '<tr>';
            tbody += '<td>'+alist[i]['domain']+'</td>';
            tbody += '<td>'+alist[i]['upstream_name']+'</td>';
            tbody += '<td>'+alist[i]['node_list'].length+'</td>';
            tbody += '<td><a class="btlink log_look" data-row="'+i+'">查看</a></td>';
            tbody += '<td><a class="btlink health_status" data-row="'+i+'">查看</a></td>';
            tbody += '<td style="text-align: right;"><a class="btlink edit" data-row="'+i+'">修改</a> | <a class="btlink delete" data-row="'+i+'">删除</a></td>';
            tbody += '</tr>';
        }

        $('#nodeTable').html(tbody);
        $('.nodeTablePage .Pcount').text('共'+alist.length+'条');
        $('#nodeTable .edit').click(function(){
            var row = $(this).data('row');
            editBalance(alist[row],row);
        });

        $('#nodeTable .log_look').click(function(){
            var row = $(this).data('row');
            var args = {'domain':alist[row]['domain']};
            pluginRollingLogs('op_load_balance','','get_logs',JSON.stringify(args),20);
        });

        $('#nodeTable .health_status').click(function(){
            var row = $(this).data('row');
            ooPost('get_health_status', {row:row}, function(rdata){
                var rdata = $.parseJSON(rdata.data);

                var tval = '';
                for (var i = 0; i < rdata.data.length; i++) {
                    tval += '<tr>';
                    tval += '<td>'+rdata.data[i]['name']+'</td>';

                    if (typeof(rdata.data[i]['down']) != 'undefined' && rdata.data[i]['down']){
                        tval += '<td><span style="color:red;">不正常</span></td>';
                    } else{
                        tval += '<td><span class="btlink">正常</span></td>';
                    }
                    tval += '</tr>';
                }

                var tbody = "<div class='bt-form pd20'>\
                    <div>\
                        <div id='gitea_table' class='divtable' style='margin-top:5px;'>\
                            <table class='table table-hover'>\
                                <thead>\
                                    <tr>\
                                        <th width='120'>地址</th>\
                                        <th width='60'>状态</th>\
                                    </tr>\
                                </thead>\
                                <tbody>"+tval+"</tbody>\
                            </table>\
                        </div>\
                    </div>\
                </div>";

                layer.open({
                    type: 1,
                    area: ['500px','300px'],
                    title: '节点状态',
                    closeBtn: 1,
                    shift: 5,
                    shadeClose: true,
                    btn:['提交','关闭'],
                    content:tbody,
                });
            });
        });

        $('#nodeTable .delete').click(function(){
            var row = $(this).data('row');
            ooPost('load_balance_delete', {row:row}, function(rdata){
                var rdata = $.parseJSON(rdata.data);
                showMsg(rdata.msg, function(){
                    loadBalanceListRender();
                },{ icon: rdata.status ? 1 : 2 }, 2000);
            });
        });

    });
}

function loadBalanceList() {
    var body = '<div class="bt-box active" style="display: block;">\
        <div class="mb10">\
          <button class="btn btn-success btn-sm" data-index="0" onclick="addBalance()">添加负载</button>\
          <div class="divtable mt10">\
            <table class="table table-hover">\
            <thead>\
                <tr>\
                    <th>网站</th>\
                    <th>负载名称</th>\
                    <th>节点</th>\
                    <th>日志</th>\
                    <th>状态</th>\
                    <th width="100" style="text-align: right;">操作</th>\
                </tr>\
            </thead>\
            <tbody id="nodeTable"></tbody>\
            </table>\
            <div class="nodeTablePage page" data-type="nodePage">\
                <div><span class="Pcount">共0条</span></div>\
            </div>\
          </div>\
        </div>\
      </div>\
      </div>';
    $(".soft-man-con").html(body);
    loadBalanceListRender();
}
