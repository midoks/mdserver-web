function dPost(method, version, args,callback){
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });

    var req_data = {};
    req_data['name'] = 'docker';
    req_data['func'] = method;
    req_data['version'] = version;
 
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

function dPostCallbak(method, version, args,callback){
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });

    var req_data = {};
    req_data['name'] = 'docker';
    req_data['func'] = method;
    args['version'] = version;
 
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


function logsCon(id){
    dPost('docker_con_log','',{Hostname:id},function(rdata){
        var rdata = $.parseJSON(rdata.data);
        if(!rdata.status) {
            layer.msg(rdata.msg,{icon:2});
            return;
        };
        layer.open({
            type:1,
            title:'Docker日志',
            area: '600px',
            closeBtn: 2,
            content:'<div class="bt-form">'
                    +'<pre class="crontab-log" style="overflow: auto; \
                    border: 0px none; line-height:23px;padding: 15px; \
                    margin: 0px; white-space: pre-wrap; height: 405px; \
                    background-color: rgb(51,51,51);color:#f1f1f1;\
                    border-radius:0px;">'+ (rdata.msg == '' ? 'No logs':rdata.msg) +'</pre>'
                    +'</div>',
            success:function(index,layers){
                $(".crontab-log").scrollTop(1000000);
            }
        });
    });
}

function deleteCon(Hostname){
    // 删除容器
    safeMessage('删除容器 ', '删除容器 ['+Hostname+'], 确定?',function(){
        dPost('docker_remove_con','',{Hostname:Hostname},function(rdata){
            var rdata = $.parseJSON(rdata.data);
            showMsg(rdata.msg,function(){
                if(rdata.status) {
                    dockerConListRender();
                }
            },{icon:rdata.status?1:2});
        });
    });
}


function startCon(Hostname){
    dPost('docker_run_con','',{Hostname:Hostname},function(rdata){
        var rdata = $.parseJSON(rdata.data);
        showMsg(rdata.msg,function(){
            if(rdata.status) {
                dockerConListRender();
            }
        },{icon:rdata.status?1:2});
    });
}

function stopCon(Hostname){
    dPost('docker_stop_con','',{Hostname:Hostname},function(rdata){
        var rdata = $.parseJSON(rdata.data);
        showMsg(rdata.msg,function(){
            if(rdata.status) {
                dockerConListRender();
            }
        },{icon:rdata.status?1:2});
    });
}

function execCon(Hostname){
    webShell();
    var pdata_socket = {};
    var shell = setInterval(function(){
        if($('.term-box').length == 0){
            pdata_socket['data'] = 'exit\n';
            socket.emit('webssh',pdata_socket);
            setTimeout(function(){socket.emit('webssh',pdata_socket['data']);},1000);
            clearInterval(shell);
        }
    },500);
    setTimeout(function(){
        dPost('docker_exec','',{Hostname:Hostname},function(res){
            var res = $.parseJSON(res.data);
            if(!res.status){
                layer.msg(res.msg,{icon:res.status?1:2});
            }else{
                pdata_socket['data'] = 'clear && ' + res.msg +'\n'
                socket.emit('webssh',pdata_socket);
                setTimeout(function(){socket.emit('webssh',pdata_socket['data']);},1000);
            }
        });
    });
}

function dockerConListRender(){
    dPost('con_list', '', {}, function(rdata){
        var rdata = $.parseJSON(rdata.data);
        console.log(rdata);
        if (!rdata.status){
            layer.msg(rdata.msg,{icon:2,time:2000});
            return; 
        }
        

        var list = '';
        var rlist = rdata.data;

        for (var i = 0; i < rlist.length; i++) {
            var docker_status = 'stop';
            var status = '<span class="glyphicon glyphicon-pause" style="color:red;font-size:12px"></span>';
            if (rlist[i]['State']['Status'] == 'running'){
                docker_status = 'start';
                status = '<span class="glyphicon glyphicon-play" style="color:#20a53a;font-size:12px"></span>';
            }

            var op = '';
            op += '<a href="javascript:;" onclick="execCon(\''+rlist[i]['Config']['Hostname']+'\')" class="btlink">终端</a> | ';
            op += '<a href="javascript:;" onclick="logsCon(\''+rlist[i]['Id']+'\')" class="btlink">日志</a> | ';
            op += '<a href="javascript:;" onclick="deleteCon(\''+rlist[i]['Config']['Hostname']+'\')" class="btlink">删除</a>';

            list += '<tr>';
            list += '<td>'+rlist[i]['Name'].substring(1)+'</td>';
            list += '<td>'+rlist[i]['Config']['Image']+'</td>';
            list += '<td>'+getFormatTime(rlist[i]['Created'])+'</td>';


            if (docker_status == 'start'){
                list += '<td style="cursor:pointer;" align="center" onclick="stopCon(\''+rlist[i]['Config']['Hostname']+'\')">'+status+'</td>';  
            } else{
                list += '<td style="cursor:pointer;" align="center" onclick="startCon(\''+rlist[i]['Config']['Hostname']+'\')">'+status+'</td>';
            }
            list += '<td class="text-right">'+op+'</td>';
            list += '</tr>';
        }

        $('#con_list tbody').html(list);
    });
}

function createConTemplate(){

    dPost('get_docker_create_info','',{},function(rdata){
        var rdata = $.parseJSON(rdata.data);
        console.log(rdata);
        var rdata = rdata.data;
        var imageOpt = '';
        for(var i=0;i<rdata.images.length;i++){
            var imageName = rdata.images[i].RepoTags.indexOf('panel') == -1? rdata.images[i].RepoTags:'aaPanel:'+rdata.images[i].RepoTags.split(':')[1];
            imageOpt += '<option value="'+rdata.images[i].RepoTags+'">'+imageName+'</option>';
        }
        var iplistOpt = '';
        for(var i=0;i<rdata.iplist.length;i++){
            iplistOpt += '<option value="'+rdata.iplist[i].address+'">'+rdata.iplist[i].address+'</option>';
        }

        var layer_index = layer.open({
            type: 1,
            title: "创建容器",
            area: '556',
            closeBtn: 2,
            shadeClose: false,
            btn: ['确定', '取消'],
            content: '<div class="bt-form pd20 pb70 ceart-docker new_tname">\
                        <div class="line">\
                            <span class="tname">镜像</span>\
                            <div class="info-r c4"><select class="bt-input-text docker-image" style="width:330px">'+imageOpt+'</select></div>\
                        </div>\
                        <div class="line">\
                            <span class="tname">绑定IP</span>\
                            <div class="info-r c4"><select class="bt-input-text docker-address" style="width:330px"><option value="0.0.0.0">0.0.0.0</optin>'+iplistOpt+'</select></div>\
                        </div>\
                        <div class="line">\
                            <span class="tname">端口映射</span>\
                            <div class="info-r c4">\
                                <div class="type-port">\
                                    <input class="bt-input-text" name="name1" type="number" placeholder="容器端口" style="width:110px;margin-right:15px">\
                                    <select class="bt-input-text" style="width:90px;margin-right:15px"><option value="TCP">TCP</optin><option value="UDP">UDP</optin></select>\
                                    <input class="bt-input-text" name="name2" type="number" placeholder="服务器端口" style="width:90px">\
                                    <span class="plus glyphicon glyphicon-plus" style="color: #20a53a;font-size: 11px;"></span>\
                                </div>\
                                <div class="divtable" style="max-height:100px;overflow:auto; margin-top:15px;width:330px;padding-left: 0px;">\
                                    <table class="table table-hover">\
                                        <tbody id="portabletr"><tr class="more1"><td>当前未添加端口映射</td></tr></tbody>\
                                    </table>\
                                </div>\
                            </div>\
                        </div>\
                        <div class="line">\
                            <span class="tname">目录映射</span>\
                            <div class="info-r c4">\
                                <div class="type-volumes">\
                                    <input class="bt-input-text" name="path1" type="text" placeholder="容器目录" style="width:110px;margin-right:15px">\
                                    <select class="bt-input-text" style="width:90px;margin-right:15px"><option value="rw">read-write</optin><option value="ro">read only</optin></select>\
                                    <input class="bt-input-text" name="path2" type="text" placeholder="服务器目录" style="width:90px">\
                                    <span class="plus2 glyphicon glyphicon-plus" style="color: #20a53a;font-size: 11px;"></span>\
                                </div>\
                                <div class="divtable" style="max-height:100px;overflow:auto; margin-top:15px;width:330px;padding-left: 0px;">\
                                    <table class="table table-hover">\
                                        <tbody id="portabletr2"><tr class="more2"><td>当前未添加目录映射</td></tr></tbody>\
                                    </table>\
                                </div>\
                            </div>\
                        </div>\
                        <div class="line">\
                            <span class="tname" style="height: auto;line-height: 20px;">环境变量<br>(每行一个)</span>\
                            <div class="info-r c4" style="margin-bottom: 0;">\
                                <div class="type-volumes">\
                                    <textarea placeholder="Add variables format as following, one per line:\nJAVA_HOME=/usr/local/java8&#10;HOSTNAME=master" name="environments" class="docker-environments"></textarea>\
                                </div>\
                            </div>\
                        </div>\
                        <div class="line">\
                            <span class="tname">内存配额</span>\
                            <div class="info-r c4"><input class="bt-input-text mr5 docker-mem" type="number" style="width:100px" value="'+parseInt(rdata.memSize/2)+'">\
                            <span class="dc-un">MB</span><i class="help">不超过， '+ rdata.memSize +'MB</i></div>\
                        </div>\
                        <div class="line">\
                            <span class="tname">CPU配额</span>\
                            <div class="info-r c4">\
                            <input class="bt-input-text mr5 docker-cpu" type="number" max="100" min="1" style="width:100px" value="100">\
                            <span class="dc-un"></span><i class="help">越大，占用的CPU越多</i></div>\
                        </div>\
                        <div class="line">\
                            <span class="tname">执行命令</span>\
                            <div class="info-r c4"><input class="bt-input-text docker-command" type="text" style="width:330px" value="" placeholder="/bin/bash"></div>\
                        </div>\
                        <div class="line" style="display:none">\
                            <span class="tname">entrypoint</span>\
                            <div class="info-r c4"><input class="bt-input-text docker-entrypoint" type="text" style="width:300px" value=""></div>\
                        </div>\
                    </div>',
            success:function(){
                $(".bt-cancel").click(function(){
                    layer.close(layer_index);
                });


                $(".plus").click(function(){
                    var name1 = $(".type-port input[name='name1']").val();
                    var name2 = $(".type-port input[name='name2']").val();
                    if(name1 < 1 || name1 > 65535 || name2 < 1 || name2 > 65535 || isNaN(name1) || isNaN(name2)){
                        layer.msg('Port setting value range is invalid, range [1-65535]',{icon:2});
                        return;
                    }
                    
                    var portval = $('#portabletr')[0].childNodes;
                    for(var i=0;i<portval.length;i++){
                        if(portval[i].childNodes[0].innerText == '当前未添加目录映射') continue;
                        var sport = portval[i].childNodes[2].innerText;
                        if(name2 == sport){
                            layer.msg('The port ['+name2+'] is already in the mapping list!',{icon:2});
                            return;
                        }
                    }
                    var address = $('.docker-address').val();
                    if(address == '0.0.0.0'){
                        address = '*';
                    }
                    var port = address + ':' + name2;
                    var loadT = layer.msg('Testing <img src="/static/img/ing.gif">',{icon:16,time:0,shade: [0.3, "#000"]});
                    $.post('/plugin?action=a&name=docker&s=IsPortExists',{port:port},function(rdata){
                        layer.close(loadT);
                        if(rdata !== false){
                            layer.msg('Port ['+name2+'] is already in the mapping list!',{icon:2});
                            return;
                        }
                        var selecttype = $(".type-port select").val();
                        var portable= '<tr><td>'+name1+'</td><td>'+selecttype+'</td><td>'+name2+'</td><td class="text-right" width="60"><a href="javascript:;" class="btlink minus">Del</a></td></tr>';
                        $("#portabletr").append(portable);
                        $(".more1").remove();
                        $(".minus").click(function(){
                            $(this).parents("tr").remove();
                        });
                    });
                });
                
                $(".plus2").click(function(){
                    var path1 = $(".type-volumes input[name='path1']").val();
                    var path2 = $(".type-volumes input[name='path2']").val();
                    
                    var notPath = ['/boot','/bin','/sbin','/etc','/usr/bin','/usr/sbin','/dev']
                    if($.inArray(path2,notPath) != -1){
                        layer.msg('Cannot map' + path2,{icon:2});
                        return;
                    }           
                    var portval = $('#portabletr2')[0].childNodes;
                    for(var i=0;i<portval.length;i++){
                        if(portval[i].childNodes[0].innerText == '当前未添加目录映射') continue;
                        var sport = portval[i].childNodes[2].innerText;
                        if(path2 == sport){
                            layer.msg('Directory ['+path2+'] is already in the mapping list!',{icon:2});
                            return;
                        }
                    }
                    var selecttype = $(".type-volumes select").val();
                    var portable= '<tr>\
                        <td class="td_width_1" title="'+path1+'">'+path1+'</td>\
                        <td>'+selecttype+'</td><td title="'+path2+'" class="td_width_1" style="max-width: 138px;">'+path2+'</td>\
                        <td class="text-right" width="50"><a href="javascript:;" class="btlink minus2">Del</a></td>\
                    </tr>';
                    $("#portabletr2").append(portable);
                    $(".more2").remove();
                    $(".minus2").click(function(){
                        $(this).parents("tr").remove();
                    });
                });
            },
            yes:function(layero,layer_id){
                var ports = {};
                var volumes = {};
                var portval = $('#portabletr')[0].childNodes;
                var address = $('.docker-address').val();
                var portval2 = $('#portabletr2')[0].childNodes;
                var command = $('.docker-command').val()
                var entrypoint = $('.docker-entrypoint').val()
                var accept = [];

                //遍历端口映射
                for(var i=0;i<portval.length;i++){
                    // console.log(portval[i].childNodes[0].innerText);
                    if(portval[i].childNodes[0].innerText == '当前未添加端口映射') {
                        continue;
                    }
                    var port = portval[i].childNodes[0].innerText.replace(/\s/g,'');
                    var dport = port + '/' + portval[i].childNodes[1].innerText.toLowerCase().replace(/\s/g,'');
                    var sport = [address,parseInt(portval[i].childNodes[2].innerText.replace(/\s/g,''))];
                    ports[dport] = sport
                    accept.push(port);
                }
                
                //遍历目录映射
                volumes['/sys/fs/cgroup'] = {'bind':'/sys/fs/cgroup', 'mode': 'rw'};
                for(var i=0;i<portval2.length;i++){
                    if(portval2[i].childNodes[0].innerText.replace(/\s/g,' ') == '当前未添加目录映射') {
                        continue;
                    }
                    var dpath = portval2[i].childNodes[2].innerText.replace(/\s/g,'');
                    var spath = {'bind':portval2[i].childNodes[0].innerText.replace(/\s/g,''),'mode':portval2[i].childNodes[1].innerText.toLowerCase().replace(/\s/g,'')};
                    volumes[dpath] = spath
                }
                
                var data = {
                    image:$('.docker-image').val(),
                    ports:JSON.stringify(ports),
                    accept:JSON.stringify(accept),
                    volumes:JSON.stringify(volumes),
                    environments:$('.docker-environments').val(),
                    mem_limit:$('.docker-mem').val(),
                    cpu_shares:$('.docker-cpu').val(),
                    command:command,
                    entrypoint:entrypoint
                }
                
                if(data.mem_limit > rdata.memSize){
                    layer.msg('内存配额不能大于物理内存 ['+rdata.memSize+']!',{icon:2});
                    return;
                }
                
                if(data.cpu_shares > 100 || data.cpu_shares < 1){
                    layer.msg('CPU配额设置值范围应为 [1-100]!',{icon:2});
                    return;
                }
                dPost('docker_create_con','', data, function(rdata){
                    var rdata = $.parseJSON(rdata.data);
                    showMsg(rdata.msg,function(){
                        if(rdata.status) {
                            layer.close(layer_index);
                            dockerConListRender();
                        }
                    },{ icon: rdata.status ? 1 : 2 });
                });
            }
        });
    });

}

function dockerConList(){

    var con = '<div class="safe bgw">\
            <button onclick="createConTemplate();" class="btn btn-success btn-sm" type="button" style="margin-right: 5px;">创建容器</button>\
            <div class="divtable mtb10">\
                <div class="tablescroll">\
                    <table id="con_list" class="table table-hover" width="100%" cellspacing="0" cellpadding="0" border="0" style="border: 0 none;">\
                    <thead><tr>\
                    <th>名称</th>\
                    <th>镜像</th>\
                    <th>创建时间</th>\
                    <th>状态</th>\
                    <th style="text-align:right;">操作</th></tr></thead>\
                    <tbody></tbody></table>\
                </div>\
            </div>\
        </div>';

    $(".soft-man-con").html(con);
    dockerConListRender();
}

function deleteImages(tag, id){
    safeMessage('删除镜像','删除镜像['+tag+'],确定？',function(){
        dPost('docker_remove_image','', {imageId:id,repoTags:tag},function(rdata){
            var rdata = $.parseJSON(rdata.data);
            showMsg(rdata.msg,function(){
                if(rdata.status) {
                    dockerImageListRender();
                }
            },{ icon: rdata.status ? 1 : 2 });
        });
    });
}

function pullImages(tag, id){
    console.log(tag, id);
    layer.msg('开发中!',{ icon: 2 });
}

function dockerImageListRender(){
    dPost('image_list', '', {}, function(rdata){
        var rdata = $.parseJSON(rdata.data);
        console.log(rdata);
        if (!rdata.status){
            layer.msg(rdata.msg,{icon:2,time:2000});
            return; 
        }
        
        var list = '';
        var rlist = rdata.data;

        for (var i = 0; i < rlist.length; i++) {

            var tag = rlist[i]['RepoTags'].split(":")[1];

            var license = 'null';
            var desc = 'null';
            if (rlist[i]['Labels'] == null){
                license = 'free';
            }

            var op = '';
            op += '<a href="javascript:;" onclick="pullImages(\''+rlist[i]['RepoTags']+'\',\''+rlist[i]['Id']+'\')" class="btlink">拉取</a> | ';
            op += '<a href="javascript:;" onclick="deleteImages(\''+rlist[i]['RepoTags']+'\',\''+rlist[i]['Id']+'\')" class="btlink">删除</a>';

            list += '<tr>';
            list += '<td>'+rlist[i]['RepoTags']+'</td>';
            list += '<td>'+tag+'</td>';
            list += '<td>'+toSize(rlist[i]['Size'])+'</td>';
            list += '<td>'+license+'</td>';
            list += '<td>'+desc+'</td>';
            list += '<td class="text-right">'+op+'</td>';
            list += '</tr>';
        }

        $('#con_list tbody').html(list);
    });
}

function dockerPullImagesFileTemplate(){
    // 拉取镜像文件模板
    var layer_index = layer.open({
        type: 1,
        title: "获取镜像",
        area: '500px',
        closeBtn: 2,
        shadeClose: false,
        content: '<div class="bt-docker pd20">'+
                    '<div class="docker-sub">'+
                        '<span class="on">官方库</span>'+
                        '<span>公共库</span>'+
                        '<span>私有库</span>'+
                    '</div>'+
                    '<div class="bt-form bt-docker-con">'+
                        '<div class="conter official_pull pd15"><div class="line">'+
                            '<span class="tname">镜像名:</span>\
                            <div class="info-r c4">\
                                <input class="bt-input-text mr5" type="text" name="official_pull_name" style="width:218px" value="">\
                                <button type="button" class="btn btn-sm btn-success official_pull_btn">获取</button>\
                            </div>'+
                        '</div></div>'+
                        '<div class="conter public_pull pd15" style="display: none;"><div class="line">'+
                            '<span class="tname">镜像名:</span>\
                            <div class="info-r c4">\
                                <input class="bt-input-text mr5" type="text" name="public_pull_path" style="width:218px" value="">\
                                <button type="button" class="btn btn-sm btn-success public_pull_btn">获取</button>\
                            </div>'+
                        '</div></div>'+
                        '<div class="conter private_pull pd15" style="display: none;">'+
                            '<div class="line"><span class="tname">镜像地址:</span>\
                                <div class="info-r c4">\
                                    <input class="bt-input-text mr5" type="text" name="private_pull_path" style="width:218px" value="">\
                                    <button type="button" class="btn btn-sm btn-success private_pull_btn">获取</button>\
                                </div>\
                            </div>\
                        </div>\
                    </div>\
                </div>',
        success:function(layero,layer_id){

            $('.docker-sub span').click(function(){
                var index = $(this).index();
                $(this).addClass('on').siblings().removeClass('on');
                $(this).parent().next().find('.conter').eq(index).show().siblings().hide();
            });

            $('.official_pull_btn').click(function(){
                var name = $('[name="official_pull_name"]').val();
                if(name == ''){
                    layer.msg('镜像名不能为空!');
                    return;
                }
                dPost('docker_pull','',{images:name}, function(rdata){
                    var rdata = $.parseJSON(rdata.data);
                    showMsg(rdata.msg,function(){
                        if(rdata.status) {
                            layer.close(layer_index);
                            dockerImageListRender();
                            
                        }
                    },{ icon: rdata.status ? 1 : 2 });
                });
            });

            $('.public_pull_btn').click(function(){
                var path = $('[name="public_pull_path"]').val();
                if(path == ''){
                    layer.msg('公共网络镜像地址不能为空。');
                    return;
                }

                dPost('docker_pull_reg','',{path:path}, function(rdata){
                    var rdata = $.parseJSON(rdata.data);
                    showMsg(rdata.msg,function(){
                        if(rdata.status) {
                            layer.close(layer_index);
                            dockerImageListRender();
                        }
                    },{ icon: rdata.status ? 1 : 2 });
                });
            });
            $('.private_pull_btn').click(function(){
                var path = $('[name="private_pull_path"]').val();
                if(path == ''){
                    layer.msg('专用镜像地址不能为空!');
                    return
                }

                dPost('docker_pull_private_new','',{path:path}, function(rdata){
                    var rdata = $.parseJSON(rdata.data);
                    showMsg(rdata.msg,function(){
                        if(rdata.status) {
                            layer.close(layer_index);
                            dockerImageListRender();
                        }
                    },{ icon: rdata.status ? 1 : 2 });
                });
            });
        }

    });
}

function dockerImageList(){

    var con = '<div class="safe bgw">\
            <button onclick="dockerPullImagesFileTemplate()" class="btn btn-success btn-sm" type="button" style="margin-right: 5px;">获取镜像</button>\
            <div class="divtable mtb10">\
                <div class="tablescroll">\
                    <table id="con_list" class="table table-hover" width="100%" cellspacing="0" cellpadding="0" border="0" style="border: 0 none;">\
                    <thead><tr>\
                    <th>名称</th>\
                    <th>版本</th>\
                    <th>大小</th>\
                    <th>证书</th>\
                    <th>描述</th>\
                    <th style="text-align:right;">操作</th></tr></thead>\
                    <tbody></tbody></table>\
                </div>\
                <div id="databasePage" class="dataTables_paginate paging_bootstrap page"></div>\
            </div>\
        </div>';

    $(".soft-man-con").html(con);

    dockerImageListRender();
}

// login
function repoLogin(){
    var _option1= "";
    var obj = {hub_name: "", namespace: "",name: "", registry: "", user_pass: "", user_name: "",arry: ['Docker Repository','Other Repository']};
    for(var i = 0; i< obj.arry.length;i++){ 
        _option1 += '<option value="'+ obj.arry[i] +'">'+ obj.arry[i] +'</option>';
    }
    var layer_index = layer.open({
        type: 1,
        title: "登录到存储库",
        area: '450px',
        closeBtn: 2,
        shadeClose: false,
        content: '<div class="bt-docker-con docker_content">'+
                    '<style>.line .tname{width:120px;}</style>'+
                    '<div class="soft-man-con pd20 pb70 private_pull">'+
                        '<div class="line"><span class="tname">Repository Type</span><div class="info-r c4"><select class="bt-input-text mr5 project_version" name="dtype" style="width:250px">'+ _option1 +'</select></div></div>'+
                        '<div class="line"><span class="tname">Name:</span><div class="info-r"><input class="bt-input-text" type="text" name="ctm_name" style="width:250px" value="'+obj.name+'"></div></div>'+
                        '<div class="line"><span class="tname">Username:</span><div class="info-r"><input class="bt-input-text" type="text" name="user" style="width:250px" value="'+obj.user_name+'"></div></div>'+
                        '<div class="line"><span class="tname">Password:</span><div class="info-r"><input class="bt-input-text" type="password" name="passwd" style="width:250px" value="'+obj.user_pass+'"></div></div>'+
                        '<div class="line"><span class="tname">Repository Name:</span><div class="info-r"><input class="bt-input-text" type="text" name="hub_name" style="width:250px" value="'+obj.hub_name+'"></div></div>'+
                        '<div class="line"><span class="tname">Namespaces:</span><div class="info-r"><input class="bt-input-text" type="text" name="namespace" style="width:250px" value="'+obj.namespace+'"></div></div>'+
                        '<div class="line" style="display:none"><span class="tname">Registry:</span><div class="info-r"><input class="bt-input-text" type="text" name="registry" style="width:250px" value="'+obj.registry+'"></div></div>'+
                        '<div class="bt-form-submit-btn"><button type="button" class="btn btn-sm btn-success login_aliyun">登录</button></div>'+
                    '</div>'+
                '</div>',
        success:function(){
            $('[name="dtype"]').change(function(e){
                var docker_type = $(this).val();
                if(docker_type == 'Other Repository'){
                    $('.docker_content .line').show();
                }else{
                    $('.docker_content .line').filter(":lt(3)").show().end().filter(":gt(4)").hide();
                }
            }); 
            $('.login_aliyun').click(function(){
                var user = $('[name="user"]').val(),
                passwd = $('[name="passwd"]').val(),
                registry = $('[name="registry"]').val(),
                name = $('[name="ctm_name"]').val(),
                hub_name = $('[name="hub_name"]').val(),
                namespace = $('[name="namespace"]').val();

                var args = {
                    user:user,
                    passwd:passwd,
                    registry:'',
                    repository_name:name,
                    hub_name:hub_name,
                    namespace:namespace
                };
                if($('[name="dtype"]').val() == 'Docker Repository'){
                    args.registry = '';
                }else{
                    args.registry = registry;
                }

                console.log(obj);
                dPost('docker_login', '', args, function(rdata){
                    var rdata = $.parseJSON(rdata.data);
                    console.log(rdata);
                    layer.msg(rdata.msg,{icon:rdata.status?1:2});
                    if(res.status){
                        repoListRender();
                        layer.close(layer_index);
                    }
                });
            });
        }
    });

}


function delRepo(address){
    safeMessage('退出','你将退出 ['+address+'],确定?',function(){
        dPost('docker_logout', '',
            {registry:address},
            function(rdata){
                var rdata = $.parseJSON(rdata.data);
                layer.msg(rdata.msg,{icon:rdata.status?1:2});
                if(rdata.status) {
                    repoListRender();
                }
            }
        );
    });
}


function repoListRender(){
    dPost('repo_list', '', {}, function(rdata){
        var rdata = $.parseJSON(rdata.data);
        console.log(rdata);
        if (!rdata.status){
            layer.msg(rdata.msg,{icon:2,time:2000});
            return; 
        }
        
        var list = '';
        var rlist = rdata.data;

        for (var i = 0; i < rlist.length; i++) {

            list += '<tr>';
            list += '<td>'+rlist[i]['hub_name']+'</td>';
            list += '<td>'+rlist[i]['repository_name']+'</td>';
            list += '<td>'+rlist[i]['namespace']+'</td>';
            list += '<td>'+rlist[i]['registry']+'</td>';
            list += '<td class="text-right"><a href="javascript:;" onclick="delRepo(\''+rlist[i]['registry']+'\')" class="btlink">删除</a></td>';
            list += '</tr>';
        }

        $('#con_list tbody').html(list);
    });
}
function repoList(){

    var con = '<div class="safe bgw">\
            <button id="docker_login" title="" class="btn btn-success btn-sm" type="button" style="margin-right: 5px;">登录</button>\
            <div class="divtable mtb10">\
                <div class="tablescroll">\
                    <table id="con_list" class="table table-hover" width="100%" cellspacing="0" cellpadding="0" border="0" style="border: 0 none;">\
                    <thead><tr>\
                    <th>Name</th>\
                    <th>Repository Name</th>\
                    <th>NameSpace</th>\
                    <th>地址</th>\
                    <th style="text-align:right;">操作</th></tr></thead>\
                    <tbody>\
                    ' + '</tbody></table>\
                </div>\
                <div id="databasePage" class="dataTables_paginate paging_bootstrap page"></div>\
            </div>\
        </div>';

    $(".soft-man-con").html(con);

    //login
    $('#docker_login').click(function(){
        repoLogin();
    });

    repoListRender();
}


