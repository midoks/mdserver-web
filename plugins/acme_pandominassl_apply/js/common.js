function apaPost(method, args,callback){
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });

    var req_data = {};
    req_data['name'] = 'acme_pandominassl_apply';
    req_data['func'] = method;
    req_data['version'] = $('.plugin_version').attr('version');
 
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


function apaPostN(method, args,callback){

    var req_data = {};
    req_data['name'] = 'acme_pandominassl_apply';
    req_data['func'] = method;
    req_data['version'] = $('.plugin_version').attr('version');
 
    if (typeof(args) == 'string'){
        req_data['args'] = JSON.stringify(toArrayObject(args));
    } else {
        req_data['args'] = JSON.stringify(args);
    }

    $.post('/plugins/run', req_data, function(data) {
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

function apaPostCallbak(method, version, args,callback){
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });

    var req_data = {};
    req_data['name'] = 'acme_pandominassl_apply';
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

function apaReadme(){
    var readme = '<ul class="help-info-text c7">';
    readme += '<li>ACME泛域名SSL申请/管理/HOOK</li>';
    readme += '<li>通过DNS验证获取SSL证书!</li>';
    readme += '<li>HOOK: ssl发生变动时调用!</li>';
    readme += '<li>暂时仅支持1000个域名管理!</li>';
    readme += '<li>DNSAPI文档: https://github.com/acmesh-official/acme.sh/wiki/dnsapi</li>';
    readme += '<li>默认7天强制更新!</li>';

    
    readme += '</ul>';
    $('.soft-man-con').html(readme);   
}


function emailDel(id, name){
    safeMessage('删除['+name+']','您真的要删除['+name+']吗？',function(){
        var data='id='+id+'&name='+name;
        apaPost('email_del', data, function(data){
            var rdata = $.parseJSON(data.data);
            showMsg(rdata.msg,function(){
                emailList();
            },{icon: rdata.status ? 1 : 2}, 600);
        });
    });
}

function emailAdd(type){
    layer.open({
        type: 1,
        area: '500px',
        title: '添加邮件地址',
        closeBtn: 1,
        shift: 5,
        shadeClose: true,
        btn:["提交","关闭"],
        content: "<form class='bt-form pd20' id='email_add'>\
                    <div class='line'>\
                        <span class='tname'>邮件地址</span>\
                        <div class='info-r'><input name='addr' class='bt-input-text mr5' style='width:100%;' placeholder='邮件地址' type='text'></div>\
                    </div>\
                    <div class='line'>\
                        <span class='tname'>备注</span>\
                        <div class='info-r'><input name='remark' class='bt-input-text mr5' style='width:100%;' placeholder='备注' type='text'></div>\
                    </div>\
                  </form>",
        success:function(){
            $("input[name='addr']").keyup(function(){
                var v = $(this).val();
                $("input[name='remark']").val(v);
            });
        },
        yes:function(index) {
            var data = $("#email_add").serialize();
            data = decodeURIComponent(data);
            // data = toArrayObject(data);
            apaPost('email_add', data, function(data){
                var rdata = $.parseJSON(data.data);
                showMsg(rdata.msg,function(){
                    if (rdata.status){
                        layer.close(index);
                        emailList();
                    }
                },{icon: rdata.status ? 1 : 2}, 2000);
            });
        }
    });
}


function emailList(page, search){
    var _data = {};
    if (typeof(page) =='undefined'){
        var page = 1;
    }
    
    _data['page'] = page;
    _data['page_size'] = 10;
    if(typeof(search) != 'undefined'){
        _data['search'] = search;
    }

    apaPost('email_list', _data, function(data){
        var rdata = $.parseJSON(data.data);
        var list = '';
        for(i in rdata.data){
            list += '<tr>';
            list +='<td><input value="'+rdata.data[i]['id']+'" class="check" onclick="checkSelect();" type="checkbox"></td>';
            list += '<td>' + rdata.data[i]['addr'] +'</td>';
            list += '<td>' + rdata.data[i]['remark'] +'</td>';
            list += '<td style="text-align:right">';
            list += '<a href="javascript:;" class="btlink" onclick="emailDel(\''+rdata.data[i]['id']+'\',\''+rdata.data[i]['addr']+'\')" title="删除">删除</a>' +
                    '</td>';
            list += '</tr>';
        }

        var con = '<div class="safe bgw">\
            <button onclick="emailAdd()" title="添加邮件地址" class="btn btn-success btn-sm" type="button" style="margin-right: 5px;">添加邮件地址</button>\
            <span style="float:right"> \
                <button batch="true" style="float: right;display: none;margin-left:10px;" onclick="delDbBatch();" title="删除选中项" class="btn btn-default btn-sm">删除选中</button>\
            </span>\
            <div class="divtable mtb10">\
                <div class="tablescroll">\
                    <table id="DataBody" class="table table-hover" width="100%" cellspacing="0" cellpadding="0" border="0" style="border: 0 none;">\
                    <thead><tr><th width="30"><input class="check" onclick="checkSelect();" type="checkbox"></th>\
                    <th>邮件地址</th>\
                    <th>备注</th>\
                    <th style="text-align:right;">操作</th></tr></thead>\
                    <tbody>'+ list +'</tbody>\
                    </table>\
                </div>\
                <div class="dataTables_paginate paging_bootstrap page"></div>\
            </div>\
        </div>';

        $(".soft-man-con").html(con);
        $('.dataTables_paginate').html(rdata.page);

        readerTableChecked();
    });
}


function dnsapiDel(id, name){
    safeMessage('删除['+name+']','您真的要删除['+name+']吗？',function(){
        var data='id='+id+'&name='+name;
        apaPost('dnsapi_del', data, function(data){
            var rdata = $.parseJSON(data.data);
            showMsg(rdata.msg,function(){
                dnsapiList();
            },{icon: rdata.status ? 1 : 2}, 600);
        });
    });
}

var dnsapi_option = [
    {"name":"dns_cf", "title":'cloudflare', 'key':'CF_Key:CF_Email'},
    {"name":"dns_dp", "title":'dnspod/国内', 'key':'DP_Id:DP_Key'},
    {"name":"dns_dpi", "title":'dnspod/国际', 'key':'DPI_Id:DPI_Key'},
    {"name":"dns_gd", "title":'GoDaddy', 'key':'GD_Key:GD_Secret'},
    {"name":"dns_pdns", "title":'PowerDNS', 'key':'PDNS_Url:PDNS_ServerId:PDNS_Token:PDNS_Ttl'},
    {"name":"dns_lua", "title":'LuaDNS', 'key':'LUA_Key:LUA_Email'},
    {"name":"dns_me", "title":'DNSMadeEasy', 'key':'ME_Key:ME_Secret'},
    {"name":"dns_aws", "title":'Amazon Route53', 'key':'AWS_ACCESS_KEY_ID:AWS_SECRET_ACCESS_KEY'},
    {"name":"dns_ali", "title":'Aliyun', 'key':'Ali_Key:Ali_Secret'},
    {"name":"dns_ispconfig", "title":'ISPConfig', 'key':'ISPC_User:ISPC_Password:ISPC_Api:ISPC_Api_Insecure'},
    {"name":"dns_ad", "title":'Alwaysdata', 'key':'AD_API_KEY'},
    {"name":"dns_linode_v4", "title":'Linode', 'key':'LINODE_V4_API_KEY'},
    {"name":"dns_freedns", "title":'FreeDNS', 'key':'FREEDNS_User:FREEDNS_Password'},
    {"name":"dns_cyon", "title":'cyon.ch', 'key':'CY_Username:CY_Password:CY_OTP_Secret'},
    {"name":"dns_gandi_livedns", "title":'LiveDNS', 'key':'GANDI_LIVEDNS_TOKEN'},
    {"name":"dns_knot", "title":'Knot', 'key':'KNOT_SERVER:KNOT_KEY'},
    {"name":"dns_dgon", "title":'DigitalOcean', 'key':'DO_API_KEY'},
    {"name":"dns_cloudns", "title":'ClouDNS.net', 'key':'CLOUDNS_SUB_AUTH_ID:CLOUDNS_AUTH_PASSWORD'},
    {"name":"dns_namesilo", "title":'Namesilo', 'key':'Namesilo_Key'},
    {"name":"dns_azure", "title":'Azure', 'key':'AZUREDNS_SUBSCRIPTIONID:AZUREDNS_TENANTID:AZUREDNS_APPID:AZUREDNS_CLIENTSECRET'},
    {"name":"dns_selectel", "title":'selectel.com', 'key':'SL_Key'},
    {"name":"dns_zonomi", "title":'zonomi.com', 'key':'ZM_Key'},
    {"name":"dns_kinghost", "title":'KingHost', 'key':'KINGHOST_Username:KINGHOST_Password'},
    {"name":"dns_zilore", "title":'Zilore', 'key':'Zilore_Key'},
    {"name":"dns_gcloud", "title":'Google Cloud DNS', 'key':'CLOUDSDK_ACTIVE_CONFIG_NAME'},
    {"name":"dns_mydnsjp", "title":'MyDNS.JP', 'key':'MYDNSJP_MasterID:MYDNSJP_Password'},
    {"name":"dns_doapi", "title":'do.de', 'key':'DO_LETOKEN'},
    {"name":"dns_online", "title":'Online', 'key':'ONLINE_API_KEY'},
    {"name":"dns_cn", "title":'Core-Networks', 'key':'CN_User:CN_Password'},
    {"name":"dns_ultra", "title":'UltraDNS', 'key':'ULTRA_USR:ULTRA_PWD'},
    {"name":"dns_hetzner", "title":'Hetzner', 'key':'HETZNER_Token'},
    {"name":"dns_ddnss", "title":'DDNSS.de', 'key':'DDNSS_Token'},
];

function getDnsapiKey(name){
    for (var i = 0; i < dnsapi_option.length; i++) {
        if (dnsapi_option[i]['name'] == name){
            return dnsapi_option[i]['key'];
        }
    }
    return '';
}

function getDnsapiTitle(name){
    for (var i = 0; i < dnsapi_option.length; i++) {
        if (dnsapi_option[i]['name'] == name){
            return dnsapi_option[i]['title'];
        }
    }
    return '其他';
}



function dnsapiAdd(row){
    // console.log(row);
    var option_name = '';
    var option_remark = '';
    var option_type = 'cf';
    var option_val = '';
    var option_id = 0;
    if (typeof(row) != 'undefined'){
        option_name = row['name'];
        option_remark = row['remark'];
        option_type = row['type'];
        option_val = row['val'];
        option_id = row['id'];
        
    }

    // console.log(option_name);
    function renderDnsapiOption(name, val){
        var vlist = {};
        if (val != ''){
            var t = val.split('~');
            for (var i = 0; i < t.length; i++) {
                var kv = t[i].split('|');
                if (kv.length == 2){
                    vlist[kv[0]] = kv[1];
                } else {
                    vlist[kv[0]] = '';
                }
            }
            // console.log(vlist);
        }


        var key = getDnsapiKey(name);
        var klist = key.split(':');
        // console.log(klist);
        var option_html = '';
        for (var i = 0; i < klist.length; i++) {
            var klist_val = '';
            if (klist[i] in vlist){
                klist_val = vlist[klist[i]];
            }

            option_html += "\
                <span class='tname'>"+klist[i]+"</span>\
                <div class='info-r'>\
                    <input name='"+klist[i]+"' class='bt-input-text mr5' style='width:100%;' value='"+klist_val+"' placeholder='请输入对应值' type='text'>\
                </div>";
        }
        $('#dnsapi_option').html(option_html);
    }

    layer.open({
        type: 1,
        area: '500px',
        title: '添加DNSAPI',
        closeBtn: 1,
        shift: 5,
        shadeClose: true,
        btn:["提交","关闭"],
        content: "<form class='bt-form pd20' id='dnsapi_add'>\
                    <div class='line'>\
                        <span class='tname'>名称</span>\
                        <div class='info-r'><input name='name' class='bt-input-text mr5' style='width:100%;' placeholder='名称' value='"+option_name+"' type='text'></div>\
                    </div>\
                    <div class='line'>\
                        <span class='tname'>DNSAPI类型</span>\
                        <div class='info-r'>\
                            <select class='bt-input-text mr5' name='type'>\
                                <option name='cf'>cloudflare</option>\
                            </select>\
                        </div>\
                    </div>\
                    <div class='line' id='dnsapi_option'>\
                        <span class='tname'>CF_Key</span>\
                        <div class='info-r'>\
                            <input name='v1' class='bt-input-text mr5' style='width:100%;' placeholder='请输入对应值' type='text'>\
                        </div>\
                        <span class='tname'>CF_Email</span>\
                        <div class='info-r'>\
                            <input name='v2' class='bt-input-text mr5' style='width:100%;' placeholder='请输入对应值' type='text'>\
                        </div>\
                    </div>\
                    <div class='line'>\
                        <span class='tname'>备注</span>\
                        <div class='info-r'><input name='remark' class='bt-input-text mr5' style='width:100%;' placeholder='备注' value='"+option_remark+"' type='text'></div>\
                    </div>\
                    <input name='id' value='"+option_id+"' type='hidden'>\
                  </form>",
        success:function(){
            $("input[name='name']").keyup(function(){
                var v = $(this).val();
                $("input[name='remark']").val(v);
            });

            var option = '';
            for (var i = 0; i<dnsapi_option.length; i++) {

                if (dnsapi_option[i]['name'] == option_type){
                    option += "<option value='"+dnsapi_option[i]['name']+"' key='"+dnsapi_option[i]['key']+"' selected>"+dnsapi_option[i]['title']+"</option>";
                } else {
                    option += "<option value='"+dnsapi_option[i]['name']+"' key='"+dnsapi_option[i]['key']+"'>"+dnsapi_option[i]['title']+"</option>";
                }
            }

            renderDnsapiOption(option_type, option_val);
            $('select[name="type"]').html(option);
            $('select[name="type"]').change(function(){
                var name = $(this).val();

                if (option_type == name){
                    renderDnsapiOption(name, option_val);
                } else {
                    renderDnsapiOption(name,'');
                }
                
            });
        },
        yes:function(index) {
            var data = $("#dnsapi_add").serialize();
            data = decodeURIComponent(data);
            data = toArrayObject(data);

            var key = getDnsapiKey(data['type']);
            var klist = key.split(':');
            var val = '';
            for (var i = 0; i < klist.length; i++) {
                var k = klist[i];
                if (k in data){
                    if (klist.length - 1 == i){
                        val += k + '|' + data[k];
                    } else {
                        val += k + '|' + data[k]+'~';
                    }
                }
            }
            data['val'] = val;
            apaPost('dnsapi_add', data, function(data){
                var rdata = $.parseJSON(data.data);
                showMsg(rdata.msg,function(){
                    if (rdata.status){
                        layer.close(index);
                        dnsapiList();
                    }
                },{icon: rdata.status ? 1 : 2}, 2000);
            });
        }
    });
}


function dnsapiList(page, search){
    var _data = {};
    if (typeof(page) =='undefined'){
        var page = 1;
    }
    
    _data['page'] = page;
    _data['page_size'] = 10;
    if(typeof(search) != 'undefined'){
        _data['search'] = search;
    }

    apaPost('dnsapi_list', _data, function(data){
        var rdata = $.parseJSON(data.data);
        var list = '';
        for(i in rdata.data){
            list += '<tr>';
            list +='<td><input value="'+rdata.data[i]['id']+'" class="check" onclick="checkSelect();" type="checkbox"></td>';
            list += '<td>' + rdata.data[i]['name'] +'</td>';
            list += '<td>' + getDnsapiTitle(rdata.data[i]['type']) +'</td>';
            list += '<td>' + rdata.data[i]['val'].split('~').join("<br/>") +'</td>';
            list += '<td>' + rdata.data[i]['remark'] +'</td>';

            list += '<td style="text-align:right">';
            list += '<a href="javascript:;" index="'+i+'" class="btlink edit" title="编辑">编辑</a> | ';
            list += '<a href="javascript:;" class="btlink" onclick="dnsapiDel(\''+rdata.data[i]['id']+'\',\''+rdata.data[i]['name']+'\')" title="删除">删除</a>';
            list += '</td></tr>';
        }

        var con = '<div class="safe bgw">\
            <button onclick="dnsapiAdd()" title="DNSAPI" class="btn btn-success btn-sm" type="button" style="margin-right: 5px;">添加DNSAPI</button>\
            <span style="float:right"> \
                <button batch="true" style="float: right;display: none;margin-left:10px;" onclick="delDbBatch();" title="删除选中项" class="btn btn-default btn-sm">删除选中</button>\
            </span>\
            <div class="divtable mtb10">\
                <div class="tablescroll">\
                    <table id="DataBody" class="table table-hover" width="100%" cellspacing="0" cellpadding="0" border="0" style="border: 0 none;">\
                    <thead><tr><th width="30"><input class="check" onclick="checkSelect();" type="checkbox"></th>\
                    <th>名称</th>\
                    <th>类型</th>\
                    <th>值</th>\
                    <th>备注</th>\
                    <th style="text-align:right;">操作</th></tr></thead>\
                    <tbody>'+ list +'</tbody>\
                    </table>\
                </div>\
                <div class="dataTables_paginate paging_bootstrap page"></div>\
            </div>\
        </div>';

        $(".soft-man-con").html(con);
        $('.dataTables_paginate').html(rdata.page);

        $('.edit').click(function(){
            var idx = $(this).attr('index');
            var row = rdata.data[idx];
            // console.log(row);
            dnsapiAdd(row);
        })

        readerTableChecked();
    });
}


function domainDel(id, name){
    safeMessage('删除['+name+']','您真的要删除['+name+']吗？',function(){
        var data='id='+id+'&name='+name;
        apaPost('domain_del', data, function(data){
            var rdata = $.parseJSON(data.data);
            showMsg(rdata.msg,function(){
                domainList();
            },{icon: rdata.status ? 1 : 2}, 600);
        });
    });
}

function domainStatusToggle(id){
    var data='id='+id;
    apaPost('domain_status_toggle', data, function(data){
        var rdata = $.parseJSON(data.data);
        showMsg(rdata.msg,function(){
            domainList();
        },{icon: rdata.status ? 1 : 2}, 600);
    });
}

function domainIdCmd(id){
    var data='id='+id;
    apaPost('get_run_hook_id_cmd', data, function(data){
        var rdata = $.parseJSON(data.data);
        // console.log(rdata);
        layer.open({
            title: "手动同步命令",
            area: ['600px', '180px'],
            type:1,
            closeBtn: 1,
            shadeClose: false,
            btn:["复制","取消"],
            content: '<div class="pd15">\
                        <div class="divtable">\
                            <pre class="layui-code">'+rdata.data+'</pre>\
                        </div>\
                    </div>',
            success:function(){
                copyText(rdata.data);
            },
            yes:function(){
                copyText(rdata.data);
            }
        });
    });
}

function domainHookCmd(){
    apaPost('run_hook_cmd', {}, function(data){
        var rdata = $.parseJSON(data.data);
        layer.open({
            title: "手动同步全部命令",
            area: ['600px', '180px'],
            type:1,
            closeBtn: 1,
            shadeClose: false,
            btn:["复制","取消"],
            content: '<div class="pd15">\
                        <div class="divtable">\
                            <pre class="layui-code">'+rdata.data+'</pre>\
                        </div>\
                    </div>',
            success:function(){
                copyText(rdata.data);
            },
            yes:function(){
                copyText(rdata.data);
            }
        });
    });
}

function syncCfCmd(){
    apaPost('run_sync_cf_cmd', {}, function(data){
        var rdata = $.parseJSON(data.data);
        layer.open({
            title: "手动同步CloudFlare全部域名命令",
            area: ['600px', '180px'],
            type:1,
            closeBtn: 1,
            shadeClose: false,
            btn:["复制","取消"],
            content: '<div class="pd15">\
                        <div class="divtable">\
                            <pre class="layui-code">'+rdata.data+'</pre>\
                        </div>\
                    </div>',
            success:function(){
                copyText(rdata.data);
            },
            yes:function(){
                copyText(rdata.data);
            }
        });
    });
}

function syncDnsPodCmd(){
    apaPost('run_sync_dnspod_cmd', {}, function(data){
        var rdata = $.parseJSON(data.data);
        layer.open({
            title: "手动同步DnsPod全部域名命令",
            area: ['600px', '180px'],
            type:1,
            closeBtn: 1,
            shadeClose: false,
            btn:["复制","取消"],
            content: '<div class="pd15">\
                        <div class="divtable">\
                            <pre class="layui-code">'+rdata.data+'</pre>\
                        </div>\
                    </div>',
            success:function(){
                copyText(rdata.data);
            },
            yes:function(){
                copyText(rdata.data);
            }
        });
    });
}

function domainAdd(row){

    var option_domian = '';
    var option_remark = '备注';
    var option_email = '';
    var option_id = 0;
    var option_dnsapi_id = 0;
    if (typeof(row) != 'undefined'){
        option_domian = row['domain'];
        option_remark = row['remark'];
        option_email = row['email'];
        option_id = row['id'];
        option_dnsapi_id = row['dnsapi_id'];
    }

    layer.open({
        type: 1,
        area: '500px',
        title: '添加顶级域名',
        closeBtn: 1,
        shift: 5,
        shadeClose: true,
        btn:["提交","关闭"],
        content: "<form class='bt-form pd20' id='domain_add'>\
                    <div class='line'>\
                        <span class='tname'>域名</span>\
                        <div class='info-r'><input name='domain' class='bt-input-text mr5' style='width:100%;' value='"+option_domian+"' placeholder='域名' type='text'></div>\
                    </div>\
                    <div class='line'>\
                        <span class='tname'>DNSAPI</span>\
                        <div class='info-r'>\
                            <select class='bt-input-text mr5' name='dnsapi_id'>\
                                <option name='0'>无设置</option>\
                            </select>\
                        </div>\
                    </div>\
                    <div class='line'>\
                        <span class='tname'>邮件</span>\
                        <div class='info-r'><input name='email' class='bt-input-text mr5' style='width:100%;' value='"+option_email+"' placeholder='邮件' type='text'></div>\
                    </div>\
                    <div class='line'>\
                        <span class='tname'>备注</span>\
                        <div class='info-r'><input name='remark' class='bt-input-text mr5' style='width:100%;' value='"+option_remark+"' placeholder='备注' type='text'></div>\
                    </div>\
                    <input name='id' value='"+option_id+"' type='hidden'>\
                  </form>",
        success:function(){
            // $("input[name='domain']").keyup(function(){
            //     var v = $(this).val();
            //     $("input[name='remark']").val(v);
            // });

            var dnsapi_id_html = "<option value='0'>无设置</option>";
            apaPostN('dnsapi_list_all', {}, function(data){
                var rdata = $.parseJSON(data.data);
                for (var i = 0; i < rdata.length; i++) {
                    if (option_dnsapi_id == rdata[i]['id']){
                        dnsapi_id_html += "<option value='"+rdata[i]['id']+"' selected>"+rdata[i]['name']+"</option>";
                    } else {
                        dnsapi_id_html += "<option value='"+rdata[i]['id']+"'>"+rdata[i]['name']+"</option>";
                    }
                }
                $('select[name="dnsapi_id"]').html(dnsapi_id_html);
            });
        },
        yes:function(index) {
            var data = $("#domain_add").serialize();
            data = decodeURIComponent(data);
            apaPost('domain_add', data, function(data){
                var rdata = $.parseJSON(data.data);
                showMsg(rdata.msg,function(){
                    if (rdata.status){
                        layer.close(index);
                        domainList();
                    }
                },{icon: rdata.status ? 1 : 2}, 2000);
            });
        }
    });
}

function domainList(page, search){
    var _data = {};
    if (typeof(page) =='undefined'){
        var page = 1;
    }
    
    _data['page'] = page;
    _data['page_size'] = 10;
    if(typeof(search) != 'undefined'){
        _data['search'] = search;
    }

    apaPost('domain_list', _data, function(data){
        var rdata = $.parseJSON(data.data);
        // console.log(rdata);
        var list = '';
        for(i in rdata.data){
            list += '<tr>';
            list +='<td><input value="'+rdata.data[i]['id']+'" class="check" onclick="checkSelect();" type="checkbox"></td>';
            list += '<td>' + rdata.data[i]['domain'] +'</td>';
            list += '<td>' + rdata.data[i]['dnsapi_id_alias'] +'</td>';
            list += '<td>' + rdata.data[i]['email'] +'</td>';
            list += '<td>' + rdata.data[i]['remark'] +'</td>';

            

            if (rdata.data[i]['effective_date'] == ''){
                list += '<td>空/未申请</td>';
            } else {
                list += '<td>'+getFormatTime(rdata.data[i]['effective_date'],'yyyy/MM/dd')+'</td>';
            }

            if (rdata.data[i]['expiration_date'] == ''){
                list += '<td>空/未申请</td>';
            } else {
                list += '<td>'+getFormatTime(rdata.data[i]['expiration_date'],'yyyy/MM/dd')+'</td>';
            }

            if (rdata.data[i]['status'] == '0'){
                list += '<td><a href="javascript:;" index="'+i+'" class="btlink status">否</a></td>';
            } else {
                list += '<td><a href="javascript:;" index="'+i+'" class="btlink status">是</a></td>';
            }

            list += '<td style="text-align:right">';
            list += '<a href="javascript:;" index="'+i+'" class="btlink cmd" title="命令">命令</a> | ';
            list += '<a href="javascript:;" index="'+i+'" class="btlink edit" title="编辑">编辑</a> | ';
            list += '<a href="javascript:;" class="btlink" onclick="domainDel(\''+rdata.data[i]['id']+'\',\''+rdata.data[i]['domain']+'\')" title="删除">删除</a>';
            list += '</td></tr>';
        }

        var con = '<div class="safe bgw">\
            <button onclick="domainAdd()" title="添加顶级域名" class="btn btn-success btn-sm" type="button" style="margin-right: 5px;">添加域名</button>\
            <button onclick="domainHookCmd()" title="全部同步命令" class="btn btn-success btn-sm" type="button" style="margin-right: 5px;">全部同步命令</button>\
            <button onclick="syncCfCmd()" title="cloudflare同步命令" class="btn btn-success btn-sm" type="button" style="margin-right: 5px;">cloudflare同步命令</button>\
            <button onclick="syncDnsPodCmd()" title="DnsPod国际同步命令" class="btn btn-success btn-sm" type="button" style="margin-right: 5px;">DnsPod国际同步命令</button>\
            <div class="divtable mtb10">\
                <div class="tablescroll">\
                    <table id="DataBody" class="table table-hover" width="100%" cellspacing="0" cellpadding="0" border="0" style="border: 0 none;">\
                    <thead><tr><th width="30"><input class="check" onclick="checkSelect();" type="checkbox"></th>\
                    <th>域名</th>\
                    <th>DNSAPI</th>\
                    <th>邮件</th>\
                    <th>备注</th>\
                    <th>开始</th>\
                    <th>结束</th>\
                    <th>同步</th>\
                    <th style="text-align:right;">操作</th></tr></thead>\
                    <tbody>'+ list +'</tbody>\
                    </table>\
                </div>\
                <div class="dataTables_paginate paging_bootstrap page"></div>\
            </div>\
        </div>';

        $(".soft-man-con").html(con);
        $('.dataTables_paginate').html(rdata.page);

        $('.edit').click(function(){
            var idx = $(this).attr('index');
            var row = rdata.data[idx];
            domainAdd(row);
        });

        $('.status').click(function(){
            var idx = $(this).attr('index');
            var row = rdata.data[idx];
            domainStatusToggle(row['id']);
        });

        $('.cmd').click(function(){
            var idx = $(this).attr('index');
            var row = rdata.data[idx];
            domainIdCmd(row['id']);
        });

        readerTableChecked();
    });
}
