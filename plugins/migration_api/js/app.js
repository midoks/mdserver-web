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


function initStep1(){
    var url = $('input[name="sync_url"]').val();
    var token = $('input[name="sync_token"]').val();
    maPost('step_one',{url:url,token:token}, function(rdata){
        var rdata = $.parseJSON(rdata.data);
        showMsg(rdata.msg,function(){
            if (rdata.status){

            }
        },{ icon: rdata.status ? 1 : 2 });
    });
}

function initStep2(){
    maPost('step_one',{}, function(rdata){
        var rdata = $.parseJSON(rdata.data);
        console.log(rdata);
        if (rdata.status){

        } else {

        }
    });
}

function initStep3(){
    maPost('step_one',{}, function(rdata){
        console.log(rdata);
    });
}

function initStep4(){
    maPost('step_one',{}, function(rdata){
        console.log(rdata);
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










