
$(document).ready(function(){
   logsLoad();
});

function changeLogsViewH(){
	var winHeight = $(window).height();
	var pageHeader = $('.mw-log-page .mw-page-header').outerHeight(true) || 0;
	var tabHeader = $('#cutTab').outerHeight(true) || 0;
	var bodyHeight = Math.max(winHeight - pageHeader - tabHeader - 180, 420);
	var panelHeight = Math.max(bodyHeight - 40, 360);
	var contentHeight = Math.max(panelHeight - 12, 320);

	$('.mw-log-page .tab-view-box').css('height', bodyHeight + 'px');
	$('#panelLogs').css('height', panelHeight + 'px');

	$('#logAudit .logAuditTab').css('height', panelHeight + 'px');
	$('#logAudit .logAuditContent').css({
		'height': panelHeight + 'px',
		'display': 'flex',
		'flex-direction': 'column'
	});
	$('#logAuditTable').css({
		'height': contentHeight + 'px',
		'display': 'flex',
		'flex-direction': 'column'
	});

}

function logsLoad(){
    changeLogsViewH();
    $(window).resize(function(){
        changeLogsViewH();
    });

    getLogs(1);
}



$('#cutTab .tabs-item').click(function(){
	var type = $(this).data('name');

	$('#cutTab .tabs-item').removeClass('active');
	$(this).addClass('active');


	$('.tab-view-box .tab-con').addClass('hide').removeClass('show').removeClass('w-full');
	$('#'+type).addClass('show').addClass('w-full');

	switch(type){
	case 'panelLogs':
		getLogs(1);
		break;
	case 'logAudit':
		getAuditLogsFiles();
		break;
	}

});


$('#panelLogs .refresh').click(function(){
	getLogs(1);
});

$('#panelLogs .clear').click(function(){
	delLogs(1);
});


function getAuditLogsFiles(){
	var loadT = layer.msg('正在获取日志审计列表...', { icon: 16, time: 0, shade: 0.3 });
	$.post('/logs/get_audit_logs_files',{}, function(rdata) {
		var data = rdata.data;
		layer.close(loadT);
        if (!data || !data.length) {
            $("#logAudit .logAuditTab").html('<div class="logAuditItem active">暂无日志审计文件</div>');
            $("#logAudit .logAuditContent").html('<div class="mw-empty-state">当前没有可展示的日志审计数据。</div>');
            return;
        }
        var option = '';
        for (var i = 0; i < data.length; i++) {
        	var tip = data[i]['name'] +' - '+data[i]['title'] + '(' + toSize(data[i]['size']) + ')';
        	if (i==0){
        		option += '<div class="logAuditItem active" title="'+tip+'" data-file="'+data[i]['name']+'">'+tip+'</div>';
        	} else {
        		option += '<div class="logAuditItem" title="'+tip+'" data-file="'+data[i]['name']+'">'+tip+'</div>';
        	}
        }
        $("#logAudit .logAuditTab").html(option);

        getAuditFile(data[0]['name']);
        $('#logAudit .logAuditItem').click(function(){
        	$('#logAudit .logAuditItem').removeClass('active');
        	$(this).addClass('active');
        	getAuditFile($(this).data('file'));
        });

	},'json');
}


function getAuditFile(log_name){
	var loadT = layer.msg('正在获取日志审计内容...', { icon: 16, time: 0, shade: 0.3 });
	$.post('/logs/get_audit_file',{log_name:log_name}, function(data) {
		layer.close(loadT);
		// console.log(data);
		try{
            if (typeof(data) == 'object'){
            	var plist = data.data;
                if (!plist || !plist.length) {
                    $('#logAudit .logAuditContent').html('<div class="mw-empty-state">当前文件没有可解析的日志记录。</div>');
                    return;
                }

                var pre_html = '<div id="logAuditTable" class="mw-log-audit-table" style="position: relative;display: flex;">\
								<div class="tootls_group tootls_top">\
									<div class="pull-left">\
										<button type="button" title="刷新列表" class="refresh btn btn-success btn-sm mr5"><span>刷新列表</span></button>\
									</div>\
								<!-- <div class="pull-right">\
									<div class="logs_search" style="position: relative;">\
										<input type="text" class="search_input" style="" placeholder="请输入来源/端口/角色/事件">\
										<span class="glyphicon glyphicon-search" aria-hidden="true"></span>\
									</div>\
								</div> --> \
							</div>\
								<div class="divtable mtb10 mw-log-audit-table-scroll">\
									<table class="table table-hover">\
									<thead style="position: relative;z-index: 1;">\
										<tr>\
											<th><span data-index="0"><span>用户</span></span></th>\
											<th><span data-index="1"><span>来源</span></span></th>\
											<th><span data-index="2"><span>端口</span></span></th>\
											<th><span data-index="3"><span>时间</span></span></th>\
										</tr>\
									</thead>\
									<tbody>\
										<tr><td><span>root</span></td>\
											<td><span>117.139.193.29</span></td>\
											<td><span>pts/0</span></td>\
											<td><span>2023-08-25 13:27 still logged in</span></td>\
										</tr>\
									</tbody>\
								</table>\
							</div>\
							<div class="tootls_group tootls_bottom">\
								<div class="pull-left"></div>\
								<div class="pull-right">\
								</div>\
							</div>\
						</div>'

            	// var pre_html = '<table class="table table-hover" width="100%" cellspacing="0" cellpadding="0" border="0">\
			    //         <thead><tr><th>时间</th><th>角色</th><th>事件</th></tr></thead>\
			    //         <tbody></tbody>\
			    //     </table>';
				    $('#logAudit .logAuditContent').html(pre_html);
                    changeLogsViewH();

				    if (plist.length>0){
				        var tmp = plist[0];
				        var thead = '<tr>';
				        for (var i in tmp) {
				            thead += '<th>'+ i + '</th>';
				        }
				        thead += '</tr>';
				        $('#logAudit .logAuditContent thead').html(thead);
				    }


				    var tbody = '';
			    for (var i = 0; i < plist.length; i++) {
			        tbody += '<tr>';
			        for (var vv in plist[i]) {
			            tbody+= '<td>'+ plist[i][vv] + '</td>'
			        }
			        tbody += '</tr>';
			    }
			    $('#logAudit .logAuditContent tbody').html(tbody);

			    $('#logAudit .refresh').click(function(){
			    	getAuditFile(log_name);
			    });
            }

            if (typeof(data) == 'string'){
            	var cc = '<div id="logAuditPre">\
            		<pre style="height: 100%; background-color: rgb(51, 51, 51); color: rgb(255, 255, 255); overflow-x: hidden; overflow-wrap: break-word; white-space: pre-wrap;"><code>'+data+'</code></pre>\
            	</div>';
                $('#logAudit .logAuditContent').html(cc);
                changeLogsViewH();
            }
        } catch (e) {
            layer.msg(String(e),{icon:2,time:10000,shade: [0.3, '#000']});
        }
	});
}

function getLogs(page,search) {
	search = search == undefined ? '':search;
	var loadT = layer.load();
	$.post('/logs/get_log_list','limit=10&p=' + page+"&search="+search, function(data) {
		layer.close(loadT);
		var body = '';
		for (var i = 0; i < data.data.length; i++) {
			body += "<tr>\
						<td><em class='dlt-num'>" + data.data[i].id + "</em></td>\
						<td>" + data.data[i].type + "</td>\
						<td>" + data.data[i].log + "</td>\
						<td>" + data.data[i].add_time + "</td>\
					</tr>";
		}
		$("#operationLog tbody").html(body);
		$("#panelLogs .page").html(data.page);
	},'json');
}

function delLogs(){
	layer.confirm('即将清空面板日志，继续吗？',{title:'清空日志',closeBtn:2},function(){
		var loadT = layer.msg('正在清理,请稍候...',{icon:16});
		$.post('/logs/del_panel_logs','',function(rdata){
			layer.close(loadT);
			layer.msg(rdata.msg,{icon:rdata.status?1:2});
			getLogs(1);
		},'json');
	});
}
