function str2Obj(str){
    var data = {};
    kv = str.split('&');
    for(i in kv){
        v = kv[i].split('=');
        data[v[0]] = v[1];
    }
    return data;
}

function pPost(method,args,callback, title){

    var _args = null; 
    if (typeof(args) == 'string'){
        _args = JSON.stringify(str2Obj(args));
    } else {
        _args = JSON.stringify(args);
    }

    var _title = '正在获取...';
    if (typeof(title) != 'undefined'){
        _title = title;
    }

    var loadT = layer.msg(_title, { icon: 16, time: 0, shade: 0.3 });
    $.post('/plugins/run', {name:'go-fastdfs', func:method, args:_args}, function(data) {
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


function pRead(){
	var readme = '<ul class="help-info-text c7">';
    readme += '<li>使用默认solr端口,如有需要自行修改</li>';
    readme += '<li>如果开启防火墙,需要放行solr设置的端口,例如(8983)</li>';
    readme += '<li>数据源设置好后,需要在managed-schema中同时设置</li>';
    readme += '<li><a target="_blank" href="https://github.com/midoks/mdserver-web/wiki/插件管理%5Bsolr使用说明%5D">wiki说明</a></li>';
    readme += '</ul>';

    $('.soft-man-con').html(readme);   
}