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
    $.post('/plugins/run', {name:'solr', func:method, args:_args}, function(data) {
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


function collection_management(){
	pPost('collection_list', '', function(data){
		var rdata = $.parseJSON(data.data);
		if (!rdata.status){
			layer.msg(rdata.msg,{icon:rdata.status?1:2,time:2000,shade: [0.3, '#000']});
			return;
		}

		var list = rdata.data;
		var con = '';
        con += '<div class="divtable" style="margin-top:5px;"><table class="table table-hover" width="100%" cellspacing="0" cellpadding="0" border="0">';
        con += '<thead><tr>';
        con += '<th>collection</th>';
        con += '<th>操作(<a class="btlink" onclick="addCollection()">添加</a>)</th>';
        con += '</tr></thead>';

        con += '<tbody>';
        
        for (var i = 0; i < list.length; i++) {
            con += '<tr>'+
                '<td>' + list[i]['name']+'</td>' +
                '<td>\
                	<a class="btlink" onclick="cmdReceive(\''+list[i]['name']+'\')">命令</a>\
                	| <a class="btlink" onclick="delReceive(\''+list[i]['name']+'\')">删除</a></td>\
                </tr>';
        }

        con += '</tbody>';
        con += '</table></div>';

        $(".soft-man-con").html(con);
	});
}

function addCollection(){

}


function pRead(){
	var readme = '<ul class="help-info-text c7">';
    readme += '<li>使用默认solr端口,如有需要自行修改.</li>';
    readme += '<li>如果开启防火墙,需要放行solr设置的端口,例如(8983)。</li>';
    readme += '</ul>';

    $('.soft-man-con').html(readme);   
}