function changeDivH(){
    var l = $(window).height();
    var w = $(window).width();
    $('#ff_box').css('height',l-80-60);
    $('#file_list').css('height',l-80-60);

    $('#file_list .tab-con .list').css('height', l-80-60-70);


    $('#flame_graph').css('height',l-80-60).css('width',w-300-200-40);

    // $('.tootls_host_list').css('display','block').css('height',l-192);
    // $('.tootls_commonly_list').css('display','block').css('height',l-192);    
}


$(document).ready(function(){
   var tag = $.getUrlParam('tag');
    if(tag == 'dynamic-tracking'){
        dynamicTrackingLoad();
    }
});

function dynamicTrackingLoad(){
    changeDivH();
    $(window).resize(function(){
        changeDivH();
    });
}






function redisPost(method, version, args,callback){
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });

    var req_data = {};
    req_data['name'] = 'dynamic-tracking';
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

function redisPostCallbak(method, version, args,callback){
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });

    var req_data = {};
    req_data['name'] = 'dynamic-tracking';
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