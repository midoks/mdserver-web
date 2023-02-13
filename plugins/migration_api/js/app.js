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
    maPost('step_one',{}, function(rdata){
        console.log(rdata);
    });
}

function initStep2(){
    maPost('step_one',{}, function(rdata){
        console.log(rdata);
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
    console.log($('.infoNext'));
    $('.infoNext').click(function(){
        var step = $('.step_head .active span').text();
        // console.log(step);
        // initStep1();
        switch(step){
            case '1':initStep1();break;
            case '2':initStep2();break;
            case '3':initStep3();break;
            case '4':initStep4();break;
        }
    });
}










