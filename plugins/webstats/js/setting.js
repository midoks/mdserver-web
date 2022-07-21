
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
					<input type="number" class="bt-input-text" name="ip_total" value="'+rdata['global']['ip_top_num']+'" style="width:55px;">\
					<button type="button" class="btn btn-default btn-sm" bt-event-click="totalNumSubmit" style="margin-left: 62px;"><span>保存</span></button>\
					<span class="tips" data-toggle="tooltip" data-placement="top" title="设置IP统计页面的TOP数量">?</span>\
				</div>\
				<div class="item-line">\
					<div class="choose_title">URI统计</div>\
					<input type="number" class="bt-input-text" name="ip_total" value="'+rdata['global']['uri_top_num']+'" style="width:55px;">\
					<button type="button" class="btn btn-default btn-sm" bt-event-click="totalNumSubmit" style="margin-left: 62px;"><span>保存</span></button>\
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
					<input type="number" class="bt-input-text" name="ip_total" value="'+rdata['global']['save_day']+'" style="width:55px;">/天 \
					<button type="button" class="btn btn-default btn-sm" bt-event-click="totalNumSubmit" style="margin-left: 48px;"><span>保存</span></button>\
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
					<button type="button" class="btn btn-success btn-sm" bt-event-click="submitSetting" name="set">保存</button>\
					<button type="button" class="btn btn-default btn-sm" bt-event-click="submitSetting" name="setAll" style="margin-left: 10px;">同步所有站点</button>\
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

			var check = '<div class="checkbox" style="margin: 20px 0 0 -10px;">\
						<label style="cursor: pointer;margin-right:15px;">\
							<input type="checkbox" name="id" style="margin: 1px 10 0;">记录POST请求原文\
						</label>\
						<label style="cursor: pointer;">\
							<input type="checkbox" name="id" style="margin: 1px 10 0;"><span>记录403错误请求原文</span>\
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
	                    <select>\
	                        <option value="normal" '+(_tmp[i].mode == 'normal'?'selected':'')+'>完整匹配</option>\
	                        <option value="regular" '+(_tmp[i].mode == 'regular'?'selected':'')+'>模糊匹配</option>\
	                    </select>\
	                </td>\
	                <td><input style="width:290px" placeholder="'+(_tmp[i].mode == 'normal'?'例：需排除a.com/test.html请求，请填写 test.html':'包含此内容的URL请求将不会被统计，请谨慎填写')+'" type="text" value="'+_tmp[i].url+'"></td>\
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
});
///////////////////////////////////////////////
}