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
        apaPost('email_del', data, function(data){
            var rdata = $.parseJSON(data.data);
            showMsg(rdata.msg,function(){
                emailList();
            },{icon: rdata.status ? 1 : 2}, 600);
        });
    });
}

function dnsapiAdd(type){
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
                        <div class='info-r'><input name='name' class='bt-input-text mr5' style='width:100%;' placeholder='名称' type='text'></div>\
                    </div>\
                    <div class='line'>\
                        <span class='tname'>备注</span>\
                        <div class='info-r'><input name='remark' class='bt-input-text mr5' style='width:100%;' placeholder='备注' type='text'></div>\
                    </div>\
                  </form>",
        success:function(){
            $("input[name='name']").keyup(function(){
                var v = $(this).val();
                $("input[name='remark']").val(v);
            });
        },
        yes:function(index) {
            var data = $("#dnsapi_add").serialize();
            data = decodeURIComponent(data);
            // data = toArrayObject(data);
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
            list += '<td>' + rdata.data[i]['remark'] +'</td>';
            list += '<td style="text-align:right">';
            list += '<a href="javascript:;" class="btlink" onclick="dnsapiDel(\''+rdata.data[i]['id']+'\',\''+rdata.data[i]['name']+'\')" title="删除">删除</a>' +
                    '</td>';
            list += '</tr>';
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

function domainAdd(type){
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
                        <div class='info-r'><input name='domain' class='bt-input-text mr5' style='width:100%;' placeholder='域名' type='text'></div>\
                    </div>\
                    <div class='line'>\
                        <span class='tname'>备注</span>\
                        <div class='info-r'><input name='remark' class='bt-input-text mr5' style='width:100%;' placeholder='备注' type='text'></div>\
                    </div>\
                  </form>",
        success:function(){
            $("input[name='domain']").keyup(function(){
                var v = $(this).val();
                $("input[name='remark']").val(v);
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
            list += '<td>' + rdata.data[i]['remark'] +'</td>';
            list += '<td style="text-align:right">';
            list += '<a href="javascript:;" class="btlink" onclick="domainDel(\''+rdata.data[i]['id']+'\',\''+rdata.data[i]['domain']+'\')" title="删除">删除</a>' +
                    '</td>';
            list += '</tr>';
        }

        var con = '<div class="safe bgw">\
            <button onclick="domainAdd()" title="添加顶级域名" class="btn btn-success btn-sm" type="button" style="margin-right: 5px;">添加域名</button>\
            <span style="float:right"> \
                <button batch="true" style="float: right;display: none;margin-left:10px;" onclick="delDbBatch();" title="删除选中项" class="btn btn-default btn-sm">删除选中</button>\
            </span>\
            <div class="divtable mtb10">\
                <div class="tablescroll">\
                    <table id="DataBody" class="table table-hover" width="100%" cellspacing="0" cellpadding="0" border="0" style="border: 0 none;">\
                    <thead><tr><th width="30"><input class="check" onclick="checkSelect();" type="checkbox"></th>\
                    <th>域名</th>\
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
