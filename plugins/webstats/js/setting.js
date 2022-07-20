
function wsGlobalSetting(){
	var html = '<div>\
		<div class="ws_setting">\
			<div class="ws_title">监控统计:</div>\
			<div class="ws_content">\
				<div class="item-line">\
					<div class="choose_title">监控开关</div>\
					<input type="number" class="bt-input-text" name="ip_total" value="50" style="width:55px;">\
					<button type="button" class="btn btn-default btn-sm" bt-event-click="totalNumSubmit" style="margin-left: 62px;"><span>保存</span></button>\
					<span class="tips" data-toggle="tooltip" data-placement="bottom" title="缩短日志保存天数原有记录的日志将被删除，请谨慎操作">?</span>\
				</div>\
				<div class="item-line">\
					<div class="choose_title">URI统计</div>\
					<input type="number" class="bt-input-text" name="ip_total" value="50" style="width:55px;">\
					<button type="button" class="btn btn-default btn-sm" bt-event-click="totalNumSubmit" style="margin-left: 62px;"><span>保存</span></button>\
					<span class="tips" data-toggle="tooltip" data-placement="top" title="缩短日志保存天数原有记录的日志将被删除，请谨慎操作">?</span>\
				</div>\
			</div>\
		</div>\
		<div class="dash_line"></div>\
		<div class="ws_setting">\
			<div class="ws_title">统计:</div>\
			<div class="ws_content">\
				<div class="item-line">\
					<div class="choose_title">IP统计</div>\
					<input type="number" class="bt-input-text" name="ip_total" value="50" style="width:55px;">\
					<button type="button" class="btn btn-default btn-sm" bt-event-click="totalNumSubmit" style="margin-left: 62px;"><span>保存</span></button>\
					<span class="tips" data-toggle="tooltip" data-placement="top" title="设置IP统计页面的TOP数量">?</span>\
				</div>\
				<div class="item-line">\
					<div class="choose_title">URI统计</div>\
					<input type="number" class="bt-input-text" name="ip_total" value="50" style="width:55px;">\
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
					<input type="number" class="bt-input-text" name="ip_total" value="50" style="width:55px;">/天 \
					<button type="button" class="btn btn-default btn-sm" bt-event-click="totalNumSubmit" style="margin-left: 43px;"><span>保存</span></button>\
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
					<span class="ws_tips">* 排除的请求不写入网站日志，不统计PV、UV、IP，只累计总请求、总流量数，如需多个请换行填写</span>\
					<textarea name="setting-cdn" cols="52" rows="8"></textarea>\
				</div>\
				<p style="margin-top:10px">\
					<button type="button" class="btn btn-success btn-sm" bt-event-click="submitSetting" name="set">保存</button>\
					<button type="button" class="btn btn-default btn-sm" bt-event-click="submitSetting" name="setAll" style="margin-left: 10px;">同步所有站点</button>\
					<span class="ws_tips">*【保存】【同步所有站点】只会保存/同步当前所选中的监控配置内容</span>\
				</p>\
			</div>\
		</div>\
		<div class="dash_line"></div>\
	</div>';
	$(".soft-man-con").html(html);
	$('[data-toggle="tooltip"]').tooltip();
}