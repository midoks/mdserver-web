

function pRead(){
	var readme = '<ul class="help-info-text c7">';
    readme += '<li>修改后,点击重启按钮</li>';
    readme += '</ul>';

    $('.soft-man-con').html(readme);   
}


//redis负载状态  start
function varnishStatus() {
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });
    $.post('/plugins/run', {name:'varnish', func:'run_info'}, function(data) {
        layer.close(loadT);
        if (!data.status){
            layer.msg(data.msg,{icon:0,time:2000,shade: [0.3, '#000']});
            return;
        }

        var rdata = $.parseJSON(data.data);
        // console.log(rdata);

        var tmp = "";
        for (let i in rdata) {
            // console.log(i,rdata[i]);
            if (i == 'timestamp'){
                tmp += "<tr><th>"+i+"</th><td colspan='2'>"+rdata[i]+"</td></tr>"
            } else{
                tmp += "<tr><th>"+i+"</th><td>"+rdata[i]['value']+"</td><td>"+rdata[i]['description']+"</td></tr>"
            }
        }

        hit = (parseInt(rdata.keyspace_hits) / (parseInt(rdata.keyspace_hits) + parseInt(rdata.keyspace_misses)) * 100).toFixed(2);
        var Con = '<div class="divtable">\
                        <table class="table table-hover table-bordered" style="width: 490px;">\
                        <thead><th>字段</th><th>当前值</th><th>说明</th></thead>\
                        <tbody>'+tmp+'<tbody>\
                </table></div>'
        $(".soft-man-con").html(Con);
    },'json');
}
//redis负载状态 end