
$(document).ready(function(){
   getLogs(1);
   logsLoad();
});

function changeLogsViewH(){
    var l = $(window).height();
    $('.container-fluid .tab-view-box').css('max-height',l-80-60);
}

function logsLoad(){
    changeLogsViewH();
    $(window).resize(function(){
        changeLogsViewH();
    });
}


$('#panelLogs .refresh').click(function(){
	getLogs(1);
});

$('#panelLogs .clear').click(function(){
	delLogs(1);
});




function getLogs(page,search) {
	search = search == undefined ? '':search;
	var loadT = layer.load();
	$.post('/firewall/get_log_list','limit=10&p=' + page+"&search="+search, function(data) {
		layer.close(loadT);
		var body = '';
		for (var i = 0; i < data.data.length; i++) {
			body += "<tr>\
						<td><em class='dlt-num'>" + data.data[i].id + "</em></td>\
						<td>" + data.data[i].type + "</td>\
						<td>" + data.data[i].log + "</td>\
						<td>" + data.data[i].addtime + "</td>\
					</tr>";
		}
		$("#operationLog tbody").html(body);
		$("#panelLogs .page").html(data.page);
	},'json');
}

function delLogs(){
	layer.confirm('即将清空面板日志，继续吗？',{title:'清空日志',closeBtn:2},function(){
		var loadT = layer.msg('正在清理,请稍候...',{icon:16});
		$.post('/firewall/del_panel_logs','',function(rdata){
			layer.close(loadT);
			layer.msg(rdata.msg,{icon:rdata.status?1:2});
			getLogs(1);
		},'json');
	});
}