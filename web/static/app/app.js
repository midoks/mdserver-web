function deleteApp(id) {
    layer.confirm('您确定要删除吗？', { title: '删除应用', closeBtn: 2, icon: 13, cancel: function () {} }, function () {
        $.post('/setting/delete_app', { 'id': id }, function (rdata) {
            layer.msg(rdata.msg, { icon: rdata.status ? 1 : 2 });
            if (rdata.status) {
                getAppList();
            }
        }, 'json');
    });
}

function toggleAppstatus(id) {
    $.post('/setting/toggle_app_status', { id: id }, function (rdata) {
        showMsg(rdata.msg, function () {
            if (rdata.status) {
                getAppList();
            }
        }, { icon: rdata.status ? 1 : 2 }, 2000);
    }, 'json');
}

function getAppList(page) {
    if (typeof (page) == 'undefined') {
        page = 1;
    }

    $.post('/setting/get_app_list', { page: page }, function (rdata) {
        var tbody = '';
        for (var i = 0; i < rdata.data.length; i++) {
            var row = rdata.data[i];

            tbody += '<tr>';
            tbody += '<td>' + row['app_id'] + '</td>';
            tbody += '<td>' + row['app_secret'] + '</td>';
            tbody += '<td>' + row['white_list'] + '</td>';

            if (row['status'] == 1) {
                tbody += '<td><a class="btlink" onclick="toggleAppstatus(' + row['id'] + ');">已开启</a></td>';
            } else {
                tbody += '<td><a style="color:red;" onclick="toggleAppstatus(' + row['id'] + ');">已关闭</a></td>';
            }

            tbody += '<td>' + row['add_time'] + '</td>';
            tbody += '<td>';
            tbody += '<a class="btlink" onclick="deleteApp(\'' + row['id'] + '\')" style="float:right;">删除</a>';
            tbody += '</td>';
            tbody += '</tr>';
        }

        $('#app_list_body tbody').html(tbody);
        $('#app_list_body .page').html(rdata.page);
    }, 'json');
}

function addApp() {
    layer.open({
        area: '570px',
        title: '添加应用',
        shift: 0,
        type: 1,
        content: '<div class="bt-form pd20">\
	<div class="line">\
		<span class="tname">应用ID</span>\
		<div class="info-r">\
			<input class="bt-input-text mr5" name="app_id" type="text" style="width: 310px;" disabled>\
			<button class="btn btn-success btn-xs app_id" style="margin-left: -50px;">重置</button>\
		</div>\
	</div>\
	<div class="line">\
		<span class="tname">应用密钥</span>\
		<div class="info-r">\
			<input class="bt-input-text mr5" name="app_secret" type="text" style="width: 310px;" disabled>\
			<button class="btn btn-success btn-xs app_secret" style="margin-left: -50px;">重置</button>\
		</div>\
	</div>\
	<div class="line">\
		<span class="tname" style="width: 90px; overflow: initial; height: 20px; line-height: 20px;">IP白名单<br/>(每行1个)</span>\
		<div class="info-r"><textarea class="bt-input-text" name="api_limit_addr" style="width: 310px; height: 80px; line-height: 20px; padding: 5px 8px;"></textarea></div>\
	</div>\
	<div class="line">\
		<span class="tname"></span>\
		<div class="info-r"><button class="btn btn-success btn-sm save_app_data">保存配置</button></div>\
	</div>\
	<ul class="help-info-text c7">\
		<li>开启API后，必需在IP白名单列表中的IP才能访问面板API接口</li>\
		<li style="color: red;">请谨慎在生产环境开启，这可能增加服务器安全风险；</li>\
	</ul>\
</div>',
        success: function (obj, cur_layer) {
            $('input[name="app_id"]').val(getRandomString(10));
            $('input[name="app_secret"]').val(getRandomString(20));

            $('.app_id').click(function () {
                $('input[name="app_id"]').val(getRandomString(10));
            });

            $('.app_secret').click(function () {
                $('input[name="app_secret"]').val(getRandomString(20));
            });

            $('.save_app_data').click(function () {
                var app_id = $('input[name="app_id"]').val();
                var app_secret = $('input[name="app_secret"]').val();
                var limit_addr = $('textarea[name="api_limit_addr"]').val();
                $.post('/setting/add_app', { 'app_id': app_id, 'app_secret': app_secret, 'limit_addr': limit_addr }, function (rdata) {
                    showMsg(rdata.msg, function () {
                        if (rdata.status) {
                            getAppList();
                            layer.close(cur_layer);
                        }
                    }, { icon: rdata.status ? 1 : 2 }, 2000);
                }, 'json');
            });
        }
    });
}

function appPage() {
    layer.open({
        area: ['900px', '380px'],
        title: 'APP应用管理',
        closeBtn: 1,
        shift: 0,
        type: 1,
        content: "<div class='login_view_table pd20'>\
			<button class='btn btn-success btn-sm app_add'>添加</button>\
			<div class='divtable mt10' id='app_list_body'>\
				<table class='table table-hover'>\
					<thead>\
					<tr>\
						<th>应用ID</th>\
						<th>应用密钥</th>\
						<th>白名单</th>\
						<th>状态</th>\
						<th>添加时间</th>\
						<th style='text-align:right;'>操作</th>\
					</tr>\
					</thead>\
					<tbody></tbody>\
				</table>\
				<div class='page'></div>\
			</div>\
		</div>",
        success: function () {
            getAppList();
            $('.app_add').click(function () {
                addApp();
            });
        }
    });
}
