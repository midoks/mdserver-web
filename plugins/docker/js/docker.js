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

function dockerConListRender(){
    dPost('con_list', '', {}, function(rdata){
        // console.log(rdata);
        var rdata = $.parseJSON(rdata.data);
        console.log(rdata);
        if (!rdata.status){
            layer.msg(rdata.msg,{icon:2,time:2000});
            return; 
        }
        

        var list = '';
        var rlist = rdata.data;

        for (var i = 0; i < rlist.length; i++) {
            var status = '<span class="glyphicon glyphicon-pause" style="color:red;font-size:12px"></span>';
            if (rlist[i]['State']['Status'] == 'running'){
                status = '<span class="glyphicon glyphicon-play" style="color:#20a53a;font-size:12px"></span>';
            }

            var op = '';
            op += '<a href="javascript:;" onclick="pullImages(\''+rlist[i]['RepoTags']+'\',\''+rlist[i]['Id']+'\')" class="btlink">终端</a> | ';
            op += '<a href="javascript:;" onclick="logsCon(\''+rlist[i]['Id']+'\')" class="btlink">日志</a> | ';
            op += '<a href="javascript:;" onclick="deleteCon(\''+rlist[i]['Config']['Hostname']+'\')" class="btlink">删除</a>';


            list += '<tr>';
            list += '<td>'+rlist[i]['Name'].substring(1)+'</td>';
            list += '<td>'+rlist[i]['Config']['Image']+'</td>';
            list += '<td>'+getFormatTime(rlist[i]['Created'])+'</td>';
            list += '<td>'+status+'</td>';
            list += '<td class="text-right">'+op+'</td>';
            list += '</tr>';
        }

        $('#con_list tbody').html(list);
    });
}
function dockerConList(){

    var con = '<div class="safe bgw">\
            <button onclick="" title="" class="btn btn-success btn-sm" type="button" style="margin-right: 5px;">创建容器</button>\
            <span style="float:right">              \
                <button batch="true" style="float: right;display: none;margin-left:10px;" onclick="delDbBatch();" title="删除选中项" class="btn btn-default btn-sm">删除选中</button>\
            </span>\
            <div class="divtable mtb10">\
                <div class="tablescroll">\
                    <table id="con_list" class="table table-hover" width="100%" cellspacing="0" cellpadding="0" border="0" style="border: 0 none;">\
                    <thead><tr>\
                    <th>名称</th>\
                    <th>镜像</th>\
                    <th>创建时间</th>\
                    <th>状态</th>\
                    <th style="text-align:right;">操作</th></tr></thead>\
                    <tbody>\
                    ' + '</tbody></table>\
                </div>\
                <div id="databasePage" class="dataTables_paginate paging_bootstrap page"></div>\
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

function dockerImageList(){

    var con = '<div class="safe bgw">\
            <button onclick="" title="" class="btn btn-success btn-sm" type="button" style="margin-right: 5px;">获取镜像</button>\
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


