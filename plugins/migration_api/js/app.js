
function maPostNoMsg(method,args,callback){
    var _args = null; 
    if (typeof(args) == 'string'){
        _args = JSON.stringify(toArrayObject(args));
    } else {
        _args = JSON.stringify(args);
    }
    $.post('/plugins/run', {name:'migration_api', func:method, args:_args}, function(data) {
        if (!data.status){
            layer.msg(data.msg,{icon:0,time:2000,shade: [0.3, '#000']});
            return;
        }

        if(typeof(callback) == 'function'){
            callback(data);
        }
    },'json'); 
}

function maPost(method,args,callback, msg = '正在获取...'){
    var _args = null; 
    if (typeof(args) == 'string'){
        _args = JSON.stringify(toArrayObject(args));
    } else {
        _args = JSON.stringify(args);
    }

    var loadT = layer.msg(msg, { icon: 16, time: 0, shade: 0.3 });
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
                initStep2();
            }
        },{ icon: rdata.status ? 1 : 2 });
    },'API校验中...');
}

function initStep2(){
    maPost('step_two',{}, function(rdata){
        var rdata = $.parseJSON(rdata.data);
        showMsg(rdata.msg,function(){
            if (rdata.status){
                selectProgress(2);
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
            } 
        },{ icon: rdata.status ? 1 : 2 });
    },'检测环境中...');
}

function initStep3(){
    maPost('step_three',{}, function(rdata){
        var rdata = $.parseJSON(rdata.data);
        showMsg(rdata.msg,function(){
            if (rdata.status){
                selectProgress(3);
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
            } 
        },{ icon: rdata.status ? 1 : 2 });
    });
}

function renderMigrationProgress(){
    maPostNoMsg('get_speed',{}, function(rdata){
        var rdata = $.parseJSON(rdata.data);
        // console.log('speed:',rdata.data);
        if (rdata.status){
            if (rdata['data']['action'] == 'True'){
                var end = '<div class="line">\
                        <div class="success text-center" style="padding: 10px 0 15px;">\
                        <p>数据迁移完成,请务必检查数据完整性!</p>\
                        <p style="font-size: 14px;margin-top:2px;color: #939292;">传输大小: '+toSize(rdata['data']['total_size'])+',耗时: '+rdata['data']['total_time']+',平均速度: '+toSize(rdata['data']['speed'])+'/s</p>\
                        <p class="mtb15">\
                            <button class="btn btn-success btn-sm mr5 okBtn">确定完成</button>\
                            <a class="btn btn-default btn-sm" style="margin-left: 10px;" target="_blank" href="/files/download?filename='+rdata['data']['log_file']+'">迁移日志</a>\
                        </p>\
                        </div>\
                    </div>';
                $('.psync_migrate').html(end);
            } else{
                $('.psync_migrate .action').text(rdata['data']['action']);
                $('.psync_migrate .done').text(rdata['data']['done']);
                $('.psync_migrate pre').text(rdata['data']['log']);

                var p = (rdata['data']['all_speed']/rdata['data']['all_total'])*100;
                if (p>100){
                    p = 100;
                }
                $('.psync_migrate .progress_info_bar').width(p+'%');
                $('.psync_migrate .progress_info').text(p+'%');

                renderMigrationProgress();
            }
        } else{
            layer.msg(rdata.msg,{icon:1});
        }
    });
}

function initStep4(){
    var site_checked = '';
    $('input[name="sites"]:checked').each(function(){
        site_checked += $(this).val()+',';
    });

    var databases_checked = '';
    $('input[name="databases"]:checked').each(function(){
        databases_checked+=$(this).val()+',';
    });

    maPost('step_four',{sites:site_checked,databases:databases_checked}, function(rdata){
        var rdata = $.parseJSON(rdata.data);
        selectProgress(4);

        var progress = '<div style="margin: 0 40px;">\
            <div class="line">\
                <div style="text-align:left"><span class="action">--</span>\
                <span style="margin-left: 20px;" class="done">当前: --</span><img src="/static/img/ing.gif"><a style="position: absolute;right: 40px;" class="btlink psync_close" onclick="migrate.close();">[取消]</a></div>\
                <div class="bt-progress" style="border-radius:0;height:20px;line-height:19px">\
                    <div class="bt-progress-bar progress_info_bar" style="border-radius: 0px; height: 20px; width: 0%;">\
                        <span class="bt-progress-text progress_info"></span></div>\
                    </div>\
                </div>\
            </div>\
            <pre style="height: 222px;text-align: left;margin:5px 38px 0;font-size: 12px;line-height: 20px;padding: 10px;background-color: #333;color: #fff;"></pre>\
        </div>';


        $('.psync_data').hide();
        $('.psync_migrate').html(progress);
        $('.psync_migrate').show();

        renderMigrationProgress();
    });
}


function initStep(){
    maPost('get_conf',{}, function(rdata){
        var rdata = $.parseJSON(rdata.data);
        $('input[name="sync_url"]').val(rdata.data['url']);
        $('input[name="sync_token"]').val(rdata.data['token']);
    });

    $('.infoNext').click(function(){
        initStep1();
    });

    // 重新检测按钮
    $('.psync_path').on('click', '.pathTestting', function () {
        initStep2();
    });

    $('.psync_path').on('click', '.pathBcak', function(){
        $('.psync_path').hide();
        $('.psync_info').show();
        selectProgress(1);
    });

    $('.psync_path').on('click', '.pathNext', function(){
        initStep3();
    });


    $('.psync_data').on('click', '.dataBack', function(){
        $('.psync_data').hide();
        $('.psync_path').show();
        selectProgress(2);
    });

    
    $('.psync_data').on('click', '.dataMigrate', function(){ 
        initStep4();
    });

    $('#sites_All').on('click',function(){ 
        var ch = $(this).prop('checked');
        $('#sites_li input').prop('checked',ch);
    });

    $('#db_All').on('click',function(){ 
        var ch = $(this).prop('checked');
        $('#db_li input').prop('checked',ch);
    });

    $('.psync_migrate').on('click', '.okBtn', function(){ 
        $('.psync_migrate').hide();
        $('.psync_info').show();
        selectProgress(1);
    });
}










