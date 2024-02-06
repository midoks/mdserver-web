
function wsGlobalSetting(){
////////////////////////////////////////////////
wsPost('get_global_conf', '' ,{}, function(rdata){
	var rdata = $.parseJSON(rdata.data);
	var rdata = rdata.data;
	var html = '<div id="webstats">\
		<div class="ws_setting">\
			<div class="ws_title">统计:</div>\
			<div class="ws_content">\
				<div class="item-line">\
					<div class="choose_title">IP统计</div>\
					<input type="number" class="bt-input-text" name="ip_top_num" value="'+rdata['global']['ip_top_num']+'" style="width:55px;">\
					<button type="button" id="ip_top_num" class="btn btn-default btn-sm" style="margin-left: 62px;"><span>保存</span></button>\
					<span class="tips" data-toggle="tooltip" data-placement="top" title="设置IP统计页面的TOP数量">?</span>\
				</div>\
				<div class="item-line">\
					<div class="choose_title">URI统计</div>\
					<input type="number" class="bt-input-text" name="uri_top_num" value="'+rdata['global']['uri_top_num']+'" style="width:55px;">\
					<button type="button" id="uri_top_num" class="btn btn-default btn-sm" style="margin-left: 62px;"><span>保存</span></button>\
					<span class="tips" data-toggle="tooltip" data-placement="top" title="设置URI统计页面的TOP数量">?</span>\
				</div>\
			</div>\
		</div>\
		<div class="dash_line"></div>\
		<div class="ws_setting">\
			<div class="ws_title">日志:</div>\
			<div class="ws_content">\
				<div class="item-line">\
					<div class="choose_title">日志保存天数</div>\
					<input type="number" class="bt-input-text" name="save_day" value="'+rdata['global']['save_day']+'" style="width:55px;">/天 \
					<button type="button" id="save_day" class="btn btn-default btn-sm" style="margin-left: 48px;"><span>保存</span></button>\
					<span class="tips" data-toggle="tooltip" data-placement="top" title="缩短日志保存天数原有记录的日志将被删除，请谨慎操作">?</span>\
				</div>\
			</div>\
		</div>\
		<div class="dash_line"></div>\
		<div class="ws_setting">\
			<div class="ws_title">监控配置:</div>\
			<div class="ws_content" style="width:570px;">\
				<div class="tab-nav">\
					<span data-type="cdn_headers" class="on">CDN headers</span>\
					<span data-type="exclude_extension">排除扩展</span>\
					<span data-type="exclude_status">排除响应状态</span>\
					<span data-type="exclude_url">排除路径</span>\
					<span data-type="exclude_ip">排除IP</span>\
					<span data-type="record_post_args">记录请求原文</span>\
				</div>\
				<div class="tab-con">\
					<span class="ws_tips">* 准确识别CDN网络IP地址，请注意大小写，如需多个请换行填写</span>\
					<textarea name="setting-cdn" cols="52" rows="8"></textarea>\
				</div>\
				<p style="margin-top:10px">\
					<button type="button" class="btn btn-success btn-sm" id="submitSetting">保存</button>\
					<button type="button" class="btn btn-default btn-sm" id="setAll" style="margin-left: 10px;">同步所有站点</button>\
					<span class="tips" style="margin-left:10px;" data-toggle="tooltip" data-placement="top" title="【保存】【同步所有站点】只会保存/同步当前所选中的监控配置内容">?</span>\
				</p>\
			</div>\
		</div>\
	</div>';
	$(".soft-man-con").html(html);
	$('[data-toggle="tooltip"]').tooltip();

	var common_tpl_tips = '<span class="ws_tips">* 准确识别CDN网络IP地址，请注意大小写，如需多个请换行填写</span>';
	var common_tpl_area = '<textarea name="setting-cdn" cols="52" rows="8"></textarea>';

	$('#webstats .tab-con textarea').text(rdata['global']['cdn_headers'].join('\n'));
	$('#webstats .tab-nav span').click(function(e){
		$('#webstats .tab-nav span').removeClass('on');
		$(this).addClass('on');
		$('#webstats .tab-con').html('');

		var typename = $(this).attr('data-type');
		if (typename == 'cdn_headers'){
			var content = $(common_tpl_tips).html('* 准确识别CDN网络IP地址，请注意大小写，如需多个请换行填写').prop('outerHTML');
			var area = $(common_tpl_area).html(rdata['global']['cdn_headers'].join('\n')).prop('outerHTML');

			content += area;
			$('#webstats .tab-con').html(content);
		} else if (typename == 'exclude_extension'){

			var content = $(common_tpl_tips).html('* 排除的请求不写入网站日志，不统计PV、UV、IP，只累计总请求、总流量数，如需多个请换行填写').prop('outerHTML');
			var area = $(common_tpl_area).html(rdata['global']['exclude_extension'].join('\n')).prop('outerHTML');
			content += area;
			$('#webstats .tab-con').html(content);
		} else if (typename == 'exclude_status'){
			var content = $(common_tpl_tips).html('* 排除的请求不写入网站日志，不统计PV、UV、IP，只累计总请求、总流量数，如需多个请换行填写').prop('outerHTML');
			var area = $(common_tpl_area).html(rdata['global']['exclude_status'].join('\n')).prop('outerHTML');
			content += area;
			$('#webstats .tab-con').html(content);
		} else if (typename == 'exclude_ip'){
			var txt = '<div>* 排除的IP不写入网站日志，不统计PV、UV、IP，只累计总请求、总流量数，如需多个请换行填写</div>\
					   <div style="margin-left: -10px">* 支持 192.168.1.1-192.168.1.10格式排除区间IP</div>'
			var content = $(common_tpl_tips).html(txt).prop('outerHTML');
			var area = $(common_tpl_area).html(rdata['global']['exclude_ip'].join('\n')).prop('outerHTML');
			content += area;
			$('#webstats .tab-con').html(content);
		} else if (typename == 'record_post_args'){
			var txt = '<div>记录请求原文说明：HTTP请求原文包括客户端请求详细参数，有助于分析或排查异常请求；</div>\
					   <div style="margin-left: -10px">考虑到HTTP请求原文会<span style="color:red;">占用额外存储空间</span>，默认仅记录500错误请求原文。</div>'
			var content = $(common_tpl_tips).html(txt).prop('outerHTML');

			var record_post_args = '';
			if (rdata['global']['record_post_args']){
				record_post_args = 'checked';
			}
			var record_get_403_args = '';
			if (rdata['global']['record_get_403_args']){
				record_get_403_args = 'checked';
			}


			var check = '<div class="checkbox" style="margin: 20px 0 0 -10px;">\
						<label style="cursor: pointer;margin-right:15px;">\
							<input type="checkbox" name="record_post_args" style="margin: 1px 10 0;" '+record_post_args+'>记录POST请求原文\
						</label>\
						<label style="cursor: pointer;">\
							<input type="checkbox" name="record_get_403_args" style="margin: 1px 10 0;" '+record_get_403_args+'><span>记录403错误请求原文</span>\
						</label>\
					</div>';
			content+=check;

			$('#webstats .tab-con').html(content);
		} else if ( typename == 'exclude_url'){
			var txt = '* 排除的请求不写入网站日志，不统计PV、UV、IP，只累计总请求、总流量数'
			var content = $(common_tpl_tips).html(txt).prop('outerHTML');

			var _text = '';
			var _tmp = rdata['global']['exclude_url'];
			for(var i = 0; i<10; i++){
	            if(typeof _tmp[i] == 'undefined'){
	                _tmp[i] = {mode:'regular',url:''}
	            }
	            
	            _text += '<tr>\
	                <td>\
	                    <select name="url_type_'+i+'">\
	                        <option value="normal" '+(_tmp[i].mode == 'normal'?'selected':'')+'>完整匹配</option>\
	                        <option value="regular" '+(_tmp[i].mode == 'regular'?'selected':'')+'>模糊匹配</option>\
	                    </select>\
	                </td>\
	                <td><input name="url_val_'+i+'" style="width:290px" placeholder="'+(_tmp[i].mode == 'normal'?'例：需排除a.com/test.html请求，请填写 test.html':'包含此内容的URL请求将不会被统计，请谨慎填写')+'" type="text" value="'+_tmp[i].url+'"></td>\
	            </tr>';
            }

			var list = '<div class="divtable mt10 setting-exclude-url" style="margin-left: -10px;height: 100px;width:100%;">\
						<table class="table table-hover">\
							<thead>\
								<tr><th width="96">排除方式</th><th>排除路径</th></tr>\
							</thead>\
							<tbody>'+_text+'</tbody>\
						</table>\
					</div>';
             
            content += list;
			$('#webstats .tab-con').html(content);
		}

	});

	$('#ip_top_num').click(function(){
		var num = $('input[name="ip_top_num"]').val();
		if(num == '' || num <= 0 || num > 2000) return layer.msg('请设置1-2000范围的统计数量',{icon:2});
		wsPost('set_global_conf','',{ip_top_num:num}, function(rdata){
			var rdata = $.parseJSON(rdata.data);
			layer.msg(rdata.msg,{icon:rdata.status?1:2});
		});
	});

	$('#uri_top_num').click(function(){
		var num = $('input[name="uri_top_num"]').val();
		if(num == '' || num <= 0 || num > 2000) return layer.msg('请设置1-2000范围的统计数量',{icon:2})
		wsPost('set_global_conf','',{uri_top_num:num}, function(rdata){
			var rdata = $.parseJSON(rdata.data);
			layer.msg(rdata.msg,{icon:rdata.status?1:2});
		});
	});

	$('#save_day').click(function(){
		var num = $('input[name="save_day"]').val();
		wsPost('set_global_conf','',{save_day:num}, function(rdata){
			var rdata = $.parseJSON(rdata.data);
			layer.msg(rdata.msg,{icon:rdata.status?1:2});
		});
	});

	$('#submitSetting').click(function(){
		var select = $('#webstats .tab-nav span');
		var select_pos = 0;
		$('#webstats .tab-nav span').each(function(i){
			if ($(this).hasClass('on')){select_pos = i;}
		});

		if ( [0,1,2,4].indexOf(select_pos)>-1 ){
			var setting_cdn = $('textarea[name="setting-cdn"]').val();

			// var list = setting_cdn.split('\n')
			var args = {}

			if ( select_pos == 0 ){
				args['cdn_headers'] = setting_cdn;
			} else if ( select_pos == 1 ){
				args['exclude_extension'] = setting_cdn;
			} else if ( select_pos == 2 ){
				args['exclude_status'] = setting_cdn;
			} else if ( select_pos == 4 ){
				args['exclude_ip'] = setting_cdn;
			}

			wsPost('set_global_conf','', args, function(rdata){
				var rdata = $.parseJSON(rdata.data);
				layer.msg(rdata.msg,{icon:rdata.status?1:2});
			});
		}

		if (select_pos == 3 ){

			var list = "";
			for (var i = 0; i<10; i++) {
				var tmp = "";
				var url_type = $('select[name="url_type_'+i+'"]').val();
				var url_val = $('input[name="url_val_'+i+'"]').val();

				if (url_val != ""){
					list += url_type +'|' + url_val +';';
				}
			}
			wsPost('set_global_conf','', {"exclude_url":list}, function(rdata){
				var rdata = $.parseJSON(rdata.data);
				layer.msg(rdata.msg,{icon:rdata.status?1:2});
			});
		}

		if (select_pos == 5){

			var record_post_args = $('input[name="record_post_args"]').prop('checked');
			var record_get_403_args = $('input[name="record_get_403_args"]').prop('checked');
			wsPost('set_global_conf','', {"record_post_args":record_post_args,'record_get_403_args':record_get_403_args}, function(rdata){
				var rdata = $.parseJSON(rdata.data);
				layer.msg(rdata.msg,{icon:rdata.status?1:2});
			});
		}

		wsGlobalSetting();
	});


	$('#setAll').click(function(){
		var args = "name=webstats&func=reload";
		layer.confirm('您真的要同步所有站点吗?', {icon:3,closeBtn: 1}, function() {
	        var e = layer.msg('正在同步,请稍候...', {icon: 16,time: 0});
	        $.post("/plugins/run", args, function(g) {
	            layer.close(e);
	            if( g.status && g.data != 'ok' ) {
	                layer.msg(g.data, {icon: 2,time: 3000,shade: 0.3,shadeClose: true});
	            } else {
	            	layer.msg('同步成功!', {icon: 1,time: 0});
	            }
	        },'json').error(function() {
	            layer.close(e);
	            layer.msg('操作异常!', {icon: 1});
	        });
	    })
	});

	
});
///////////////////////////////////////////////
}