function maPost(method,args,callback){
    var _args = null; 
    if (typeof(args) == 'string'){
        _args = JSON.stringify(toArrayObject(args));
    } else {
        _args = JSON.stringify(args);
    }

    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });
    $.post('/plugins/run', {name:'migration_api', func:method, args:_args}, function(data) {
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

function maAsyncPost(method,args){
    var _args = null; 
    if (typeof(args) == 'string'){
        _args = JSON.stringify(toArrayObject(args));
    } else {
        _args = JSON.stringify(args);
    }
    return syncPost('/plugins/run', {name:'migration_api', func:method, args:_args}); 
}


function maPostCallbak(method, args, callback){
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });

    var req_data = {};
    req_data['name'] = 'migration_api';
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


function selectProgress(val){
    $('.step_head li').removeClass('active');
    $('.step_head li').each(function(){
        var v = $(this).find('span').text();
        if (val == v){
            $(this).addClass('active');
        }
    });
}

function initStep1(){
    var url = $('input[name="sync_url"]').val();
    var token = $('input[name="sync_token"]').val();
    maPost('step_one',{url:url,token:token}, function(rdata){
        var rdata = $.parseJSON(rdata.data);
        showMsg(rdata.msg,function(){
            if (rdata.status){
                selectProgress(2);
                initStep2();
            }
        },{ icon: rdata.status ? 1 : 2 });
    });
}

function initStep2(){
    maPost('step_two',{}, function(rdata){
        var rdata = $.parseJSON(rdata.data);
        console.log(rdata);
        showMsg(rdata.msg,function(){
            if (rdata.status){
                $('.psync_info').hide();

                var info = rdata.data;

                var body = '<div class="divtable">\
                    <table class="table table-hover">\
                    <thead>\
                        <tr><th style="border-right:1px solid #ddd">服务</th><th>当前服务器</th><th>远程服务器</th></tr>\
                    </thead>\
                    <tbody>\
                        <tr>\
                            <td style="border-right:1px solid #ddd">网站服务</td>\
                            <td>'+info['local']['webserver']+'</td>\
                            <td>'+info['remote']['webserver']+'</td>\
                        </tr>\
                        <tr>\
                            <td style="border-right:1px solid #ddd">安装MySQL</td>\
                            <td>'+(info['local']['mysql']?'是':'否')+'</td>\
                            <td>'+(info['remote']['mysql']?'是':'否')+'</td>\
                        </tr>\
                        <tr>\
                            <td style="border-right:1px solid #ddd">安装PHP</td>\
                            <td>'+(info['local']['php'].join('/'))+'</td>\
                            <td>'+(info['remote']['php'].join('/')) +'</td>\
                        </tr>\
                        <tr>\
                            <td style="border-right:1px solid #ddd">可用磁盘</td>\
                            <td>'+info['local']['disk']+'</td>\
                            <td>'+info['remote']['disk'][0]['size'][0]+'</td>\
                        </tr>\
                    </tbody>\
                    </table>\
                    </div>';
                body += '<div class="line mtb20" style="text-align: left;">\
                    <button class="btn btn-default btn-sm mr20 pathTestting">重新检测</button>\
                    <button class="btn btn-default btn-sm mr20 pathBcak">上一步</button>\
                    <button class="btn btn-success btn-sm psync-next pathNext">下一步</button>\
                </div>';

                $('.psync_path').html(body);
                $('.psync_path').show();

                $('.pathNext').click(function(){
                    selectProgress(3);
                    initStep3();
                });
            } 
        },{ icon: rdata.status ? 1 : 2 });
    });
}

function initStep3(){
    maPost('step_three',{}, function(rdata){
        var rdata = $.parseJSON(rdata.data);
        console.log(rdata);
        showMsg(rdata.msg,function(){
            if (rdata.status){
                var pdata = rdata.data;
                var site_li = '';
                for (var i = 0; i < pdata.sites.length; i++) {
                    site_li+='<li>\
                        <label>\
                        <input type="checkbox" data-id="'+i+'" id="sites_'+pdata.sites[i]['name']+'" value="'+pdata.sites[i]['name']+'" name="sites" checked="">\
                        <span title="'+pdata.sites[i]['name']+'">'+pdata.sites[i]['name']+'</span>\
                        </label>\
                    </li>';
                }

                $('#sites_li').html(site_li);


                var db_li = '';
                for (var i = 0; i < pdata.databases.length; i++) {
                    db_li+='<li>\
                        <label>\
                        <input type="checkbox" data-id="'+i+'" id="sites_'+pdata.databases[i]['name']+'" value="'+pdata.databases[i]['name']+'" name="databases" checked="">\
                        <span title="'+pdata.databases[i]['name']+'">'+pdata.databases[i]['name']+'</span>\
                        </label>\
                    </li>';
                }
                $('#db_li').html(db_li);


                $('.psync_path').hide();
                $('.psync_data').show();
                $('.dataMigrate').click(function(){
                    selectProgress(4);
                    initStep4();
                });

                $('.dataBack').click(function(){
                    selectProgress(3);
                    $('.psync_data').hide();
                    $('.psync_path').show();
                });
            } 
        },{ icon: rdata.status ? 1 : 2 });
    });
}

function initStep4(){

    var site_checked = '';
    $('input[name="sites"]:checked').each(function(){
        site_checked += $(this).val()+',';
    });

    var databases_checked = '';
    $('input[name="databases"]').each(function(){
        databases_checked+=$(this).val()+',';
    });

    maPost('step_four',{sites:site_checked,databases:databases_checked}, function(rdata){
        var rdata = $.parseJSON(rdata.data);

        var tby = '<div class="line">\
            <div class="success text-center" style="padding: 10px 0 15px;">\
            <p style="font-size: 14px;margin-top:2px;color: #939292;">传输大小: 4.92 KB,耗时: 0分6秒,平均速度: 840 B/s</p>\
            <p class="mtb15">\
                <button class="btn btn-success btn-sm mr5 okBtn">确定完成</button>\
                <button class="btn btn-default btn-sm lookInfo">查看记录</button>\
                <a class="btn btn-default btn-sm" style="margin-left: 10px;" href="/download?filename=/www/server/panel/logs/psync.log">迁移日志</a>\
            </p>\
            </div>\
            </div>';

        $('.psync_data').hide();
        
        $('.psync_migrate').html(tby);
        $('.psync_migrate').show();
    });
}


function initStep(){
     maPost('get_conf',{}, function(rdata){
        var rdata = $.parseJSON(rdata.data);
        $('input[name="sync_url"]').val(rdata.data['url']);
        $('input[name="sync_token"]').val(rdata.data['token']);
    });

    $('.infoNext').click(function(){
        var step = $('.step_head .active span').text();
        switch(step){
            case '1':initStep1();break;
            case '2':initStep2();break;
            case '3':initStep3();break;
            case '4':initStep4();break;
        }
    });
}










