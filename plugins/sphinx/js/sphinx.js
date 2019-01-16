function spPostMin(method, args, callback){

    var req_data = {};
    req_data['name'] = 'sphinx';
    req_data['func'] = method;
 
    if (typeof(args) != 'undefined' && args!=''){
        req_data['args'] = JSON.stringify(args);
    }

    $.post('/plugins/run', req_data, function(data) {
        if (!data.status){
            layer.msg(data.msg,{icon:0,time:2000,shade: [0.3, '#000']});
            return;
        }

        if(typeof(callback) == 'function'){
            callback(data);
        }
    },'json'); 
}

function spPost(method, args, callback){
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });
    spPostMin(method,args,function(data){
        layer.close(loadT);
        if(typeof(callback) == 'function'){
            callback(data);
        } 
    });
}

function rebuild(){
    var con = '<button class="btn btn-default btn-sm" onclick="rebuildIndex();">重建索引</button>';
    $(".soft-man-con").html(con);
}

function rebuildIndex(){
    spPost('rebuild', '', function(data){
        if (data.data == 'ok'){
            layer.msg('在重建中..',{icon:1,time:2000,shade: [0.3, '#000']});
        } else {
            layer.msg(data.data,{icon:1,time:2000,shade: [0.3, '#000']});
        }
    });
}

