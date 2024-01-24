

$("#site_search_input").keyup(function(event){
	if(event.keyCode == 13) {
		getWeb(1, -1, $(this).val());
	}
});

$('#site_search').click(function(){
	getWeb(1, -1, $('#site_search_input').val());
});

/**
 * 取回网站数据列表
 * @param {Number} page   当前页
 * @param {String} search 搜索条件
 */
 function getWeb(page, type_id, search) {
 	if ( typeof(search) == 'undefined' ){
		search = $('#site_search_input').val();
	}
	
	var page = page == undefined ? '1':page;
	var order = getCookie('order');
	if(order){
		order = '&order=' + order;
	} else {
		order = '';
	}

	var type = '';
	if ( typeof(type_id) == 'undefined' ){
		type = '&type_id=-1';
	} else {
		type = '&type_id='+type_id;
	}

	var sUrl = '/site/list';
	var pdata = 'limit=10&p=' + page + '&search=' + search + order + type;
	var loadT = layer.load();
	//取回数据
	$.post(sUrl, pdata, function(data) {
		layer.close(loadT);
		//构造数据列表
		var body = '';
		$("#webBody").html(body);
		for (var i = 0; i < data.data.length; i++) {
			//当前站点状态
			if (data.data[i].status == '正在运行' || data.data[i].status == '1') {
				var status = "<a href='javascript:;' title='停用这个站点' onclick=\"webStop(" + data.data[i].id + ",'" + data.data[i].name + "')\" class='btn-defsult'><span style='color:rgb(92, 184, 92)'>运行中</span><span style='color:rgb(92, 184, 92)' class='glyphicon glyphicon-play'></span></a>";
			} else {
				var status = "<a href='javascript:;' title='启用这个站点' onclick=\"webStart(" + data.data[i].id + ",'" + data.data[i].name + "')\" class='btn-defsult'><span style='color:red'>已停止</span><span style='color:rgb(255, 0, 0);' class='glyphicon glyphicon-pause'></span></a>";
			}

			//是否有备份
			if (data.data[i].backup_count > 0) {
				var backup = "<a href='javascript:;' class='btlink' onclick=\"getBackup(" + data.data[i].id + ")\">有备份</a>";
			} else {
				var backup = "<a href='javascript:;' class='btlink' onclick=\"getBackup(" + data.data[i].id + ")\">无备份</a>";
			}
			//是否设置有效期
			var web_end_time = (data.data[i].edate == "0000-00-00") ? '永久': data.data[i].edate;
			//表格主体
			var shortwebname = data.data[i].name;
			var shortpath = data.data[i].path;
			if(data.data[i].name.length > 30) {
				shortwebname = data.data[i].name.substring(0, 30) + "...";
			}
			if(data.data[i].path.length > 30){
				shortpath = data.data[i].path.substring(0, 30) + "...";
			}
			var idname = data.data[i].name.replace(/\./g,'_');
			
			body = "<tr><td><input type='checkbox' name='id' title='"+data.data[i].name+"' onclick='checkSelect();' value='" + data.data[i].id + "'></td>\
					<td><a class='btlink webtips' href='javascript:;' onclick=\"webEdit(" + data.data[i].id + ",'" + data.data[i].name + "','" + data.data[i].edate + "','" + data.data[i].addtime + "')\" title='"+data.data[i].name+"'>" + shortwebname + "</td>\
					<td>" + status + "</td>\
					<td>" + backup + "</td>\
					<td><a class='btlink' title='打开目录"+data.data[i].path+"' href=\"javascript:openPath('"+data.data[i].path+"');\">" + shortpath + "</a></td>\
					<td><a class='btlink setTimes' id='site_"+data.data[i].id+"' data-ids='"+data.data[i].id+"'>" + web_end_time + "</a></td>\
					<td><a class='btlinkbed' href='javascript:;' data-id='"+data.data[i].id+"'>" + data.data[i].ps + "</a></td>\
					<td style='text-align:right; color:#bbb'>\
					<a href='javascript:;' class='btlink' onclick=\"webEdit(" + data.data[i].id + ",'" + data.data[i].name + "','" + data.data[i].edate + "','" + data.data[i].addtime + "')\">设置</a>\
                        | <a href='javascript:;' class='btlink' onclick=\"webDelete('" + data.data[i].id + "','" + data.data[i].name + "')\" title='删除站点'>删除</a>\
					</td></tr>"
			
			$("#webBody").append(body);
			//setEdate(data.data[i].id,data.data[i].edate);
         	//设置到期日期
			function getDate(a) {
				var dd = new Date();
				dd.setTime(dd.getTime() + (a == undefined || isNaN(parseInt(a)) ? 0 : parseInt(a)) * 86400000);
				var y = dd.getFullYear();
				var m = dd.getMonth() + 1;
				var d = dd.getDate();
				return y + "-" + (m < 10 ? ('0' + m) : m) + "-" + (d < 10 ? ('0' + d) : d);
			}
            $('#webBody').on('click','#site_'+ data.data[i].id,function(){
				var _this = $(this);
				var id = $(this).attr('data-ids');
				laydate.render({
					elem: '#site_'+ id //指定元素
					,min:getDate(1)
					,max:'2099-12-31'
					,vlue:getDate(365)
					,type:'date'
					,format :'yyyy-MM-dd'
					,trigger:'click'
					,btns:['perpetual', 'confirm']
					,theme:'#20a53a'
					,done:function(dates){
						if(_this.html() == '永久'){
						 	dates = '0000-00-00';
						}
						var loadT = layer.msg(lan.site.saving_txt, { icon: 16, time: 0, shade: [0.3, "#000"]}); 
						$.post('/site/set_end_date','id='+id+'&edate='+dates,function(rdata){
							layer.close(loadT);
							layer.msg(rdata.msg,{icon:rdata.status?1:5});
						},'json');
					}
				});
            	this.click();
            });
		}
		if(body.length < 10){
			body = "<tr><td colspan='9'>当前没有站点数据</td></tr>";
			// $(".dataTables_paginate").hide();
			$("#webBody").html(body);
		}
		//输出数据列表
		$(".btn-more").hover(function(){
			$(this).addClass("open");
		},function(){
			$(this).removeClass("open");
		});
		
		//输出分页
		$("#webPage").html(data.page);
		// $("#webPage").html('<div class="site_type"><span>站点分类:</span><select class="bt-input-text mr5" style="width:100px"><option value="-1">全部分类</option><option value="0">默认分类</option></select></div>');
		
		$(".btlinkbed").click(function(){
			var dataid = $(this).attr("data-id");
			var databak = $(this).text();
			if(databak == null){
				databak = '';
			}
			$(this).hide().after("<input class='baktext' type='text' data-id='"+dataid+"' data-page='"+page+"' name='bak' value='" + databak + "' placeholder='备注信息' onblur='getBakPost(\"sites\")' />");
			$(".baktext").focus();
		});

		readerTableChecked();
	},'json');
}


function getBakPost(b) {
	$(".baktext").hide().prev().show();
	var id = $(".baktext").attr("data-id");
	var page = $(".baktext").attr("data-page");
	var a = $(".baktext").val();
	if(a == "") {
		a = '空';
	}
	setWebPs(b, id, a,page);
	$("a[data-id='" + id + "']").html(a);
	$(".baktext").remove();
}

function setWebPs(b, id, ps,page) {
	var d = layer.load({shade: true,shadeClose: false});
	var ps = 'ps=' + ps;
	$.post('/site/set_ps', 'id=' + id + "&" + ps, function(data) {
		if(data['status']) {
			getWeb(page);
			layer.closeAll();
			layer.msg('修改成功!', {icon: 1});
		} else {
			layer.closeAll();
			layer.msg('修改失败!', {icon: 2});
		}
	},'json');
}

//创建站点前,检查服务是否开启
function webAdd(type){
	loading = layer.msg('正在检查是否开启OpenResty服务!',{icon:16,time:0,shade: [0.3, "#000"]})
	$.post('/site/check_web_status', function(data){
		layer.close(loading);
		if (data.status){
			webAddPage(type)
		} else {
			layer.msg(data.msg,{icon:0,time:3000,shade: [0.3, "#000"]})
		}
	},'json');
}

//添加站点
function webAddPage(type) {

	if (type == 1) {
		var array;
		var str="";
		var domainlist='';
		var domain = array = $("#mainDomain").val().replace('http://','').replace('https://','').split("\n");
		var webport=[];
		var checkDomain = domain[0].split('.');
		if(checkDomain.length < 1){
			layer.msg(lan.site.domain_err_txt,{icon:2});
			return;
		}
		for(var i=1; i<domain.length; i++){
			domainlist += '"'+domain[i]+'",';
		}

		webport = domain[0].split(":")[1];//主域名端口
		if(webport == undefined){
			webport="80";
		}

		domainlist = domainlist.substring(0,domainlist.length-1);//子域名json
		domain ='{"domain":"'+domain[0]+'","domainlist":['+domainlist+'],"count":'+domain.length+'}';//拼接json
		var loadT = layer.msg(lan.public.the_get,{icon:16,time:0,shade: [0.3, "#000"]})
		var data = $("#addweb").serialize()+"&port="+webport+"&webinfo="+domain;

		$.post('/site/add', data, function(ret) {
			if (ret.status == true) {
				getWeb(1);
				layer.closeAll();
				layer.msg('成功创建站点',{icon:1})
			} else {
				layer.msg(ret.msg, {icon: 2});
			}
			layer.close(loadT);
		},'json');
		return;
	}
	
	$.post('/site/get_php_version',function(rdata){
	
		var defaultPath = $("#defaultPath").html();
		var php_version = "<div class='line'><span class='tname'>"+lan.site.php_ver+"</span><select class='bt-input-text' name='version' id='c_k3' style='width:100px'>";
		for (var i=rdata.length-1;i>=0;i--) {
            php_version += "<option value='"+rdata[i].version+"'>"+rdata[i].name+"</option>";
        }

        var www = syncPost('/site/get_root_dir');

		php_version += "</select><span id='php_w' style='color:red;margin-left: 10px;'></span></div>";
		layer.open({
			type: 1,
			skin: 'demo-class',
			area: '640px',
			title: '添加网站',
			closeBtn: 1,
			shift: 0,
			shadeClose: false,
			content: "<form class='bt-form pd20 pb70' id='addweb'>\
				<div class='line'>\
                    <span class='tname'>"+lan.site.domain+"</span>\
                    <div class='info-r c4'>\
						<textarea id='mainDomain' class='bt-input-text' name='webname' style='width:458px;height:100px;line-height:22px' /></textarea>\
					</div>\
				</div>\
                <div class='line'>\
                <span class='tname'>备注</span>\
                <div class='info-r c4'>\
                	<input id='Wbeizhu' class='bt-input-text' type='text' name='ps' placeholder='网站备注' style='width:458px' />\
                </div>\
                </div>\
                <div class='line'>\
                <span class='tname'>根目录</span>\
                <div class='info-r c4'>\
                	<input id='inputPath' class='bt-input-text mr5' type='text' name='path' value='"+www['dir']+"/' placeholder='"+www['dir']+"' style='width:458px' />\
                	<span class='glyphicon glyphicon-folder-open cursor' onclick='changePath(\"inputPath\")'></span>\
                </div>\
                </div>\
				"+php_version+"\
                <div class='bt-form-submit-btn'>\
					<button type='button' class='btn btn-danger btn-sm btn-title' onclick='layer.closeAll()'>取消</button>\
					<button type='button' class='btn btn-success btn-sm btn-title' onclick=\"webAdd(1)\">提交</button>\
				</div>\
            </form>",
		});

		$(function() {
			var placeholder = "<div class='placeholder c9' style='top:10px;left:10px'>"+lan.site.domain_help+"</div>";
			$('#mainDomain').after(placeholder);
			$(".placeholder").click(function(){
				$(this).hide();
				$('#mainDomain').focus();
			})
			$('#mainDomain').focus(function() {
			    $(".placeholder").hide();
			});
			
			$('#mainDomain').blur(function() {
				if($(this).val().length==0){
					$(".placeholder").show();
				}  
			});
			
			//验证PHP版本
			$("select[name='version']").change(function(){
				if($(this).val() == '52'){
					var msgerr = 'PHP5.2在您的站点有漏洞时有跨站风险，请尽量使用PHP5.3以上版本!';
					$('#php_w').text(msgerr);
				}else{
					$('#php_w').text('');
				}
			})

			$('#mainDomain').on('input', function() {
				var array;
				var res,ress;
				var str = $(this).val().replace('http://','').replace('https://','');
				var len = str.replace(/[^\x00-\xff]/g, "**").length;
				array = str.split("\n");
				ress =array[0].split(":")[0];
				res = ress.replace(new RegExp(/([-.])/g), '_');
				if(res.length > 15){ 
					res = res.substr(0,15);
				}

				var placeholder = $("#inputPath").attr('placeholder');
				$("#inputPath").val(placeholder+'/'+ress);
				
				if(res.length > 15){
					res = res.substr(0,15);
				}

				$("#Wbeizhu").val(ress);
			})

			//备注
			$('#Wbeizhu').on('input', function() {
				var str = $(this).val();
				var len = str.replace(/[^\x00-\xff]/g, "**").length;
				if (len > 20) {
					str = str.substring(0, 20);
					$(this).val(str);
					layer.msg('不能超出20个字符!', {
						icon: 0
					});
				}
			})
			//获取当前时间时间戳，截取后6位
			var timestamp = new Date().getTime().toString();
			var dtpw = timestamp.substring(7);
		});
	}, 'json');
}

//修改网站目录
function webPathEdit(id){
	$.post('/site/get_dir_user_ini','&id='+id, function(data){
		var userini = data['data'];
		var webpath = userini['path'];
		var siteName = userini['name'];
		var runPath = userini['runPath']['runPath'];
		var userinicheckeds = userini.userini?'checked':'';
		var logscheckeds = userini.logs?'checked':'';
		var opt = ''
		var selected = '';
		for(var i=0;i<userini.runPath.dirs.length;i++){
			selected = '';
			if(userini.runPath.dirs[i] == userini.runPath.runPath){ 
				selected = 'selected';
			}
			opt += '<option value="'+ userini.runPath.dirs[i] +'" '+selected+'>'+ userini.runPath.dirs[i] +'</option>'
		}
		var webPathHtml = "<div class='webedit-box soft-man-con'>\
					<div class='label-input-group ptb10'>\
						<input type='checkbox' name='userini' id='userini'"+userinicheckeds+" /><label class='mr20' for='userini' style='font-weight:normal'>防跨站攻击(open_basedir)</label>\
						<input type='checkbox' name='logs' id='logs'"+logscheckeds+" /><label for='logs' style='font-weight:normal'>写访问日志</label>\
					</div>\
					<div class='line mt10'>\
						<span class='mr5'>网站目录</span>\
						<input class='bt-input-text mr5' type='text' style='width:50%' placeholder='网站根目录' value='"+webpath+"' name='webdir' id='inputPath'>\
						<span onclick='changePath(&quot;inputPath&quot;)' class='glyphicon glyphicon-folder-open cursor mr20'></span>\
						<button class='btn btn-success btn-sm' onclick='setSitePath("+id+")'>保存</button>\
					</div>\
					<div class='line mtb15'>\
						<span class='mr5'>运行目录</span>\
						<select class='bt-input-text' type='text' style='width:50%; margin-right:41px' name='runPath' id='runPath'>"+opt+"</select>\
						<button class='btn btn-success btn-sm' onclick='setSiteRunPath("+id+")' style='margin-top: -1px;'>保存</button>\
					</div>\
					<ul class='help-info-text c7 ptb10'>\
						<li>部分程序需要指定二级目录作为运行目录，如ThinkPHP5，Laravel</li>\
						<li>选择您的运行目录，点保存即可</li>\
					</ul>"
					+'<div class="user_pw_tit" style="margin-top: -8px;padding-top: 11px;">'
						+'<span class="tit">密码访问</span>'
						+'<span class="btswitch-p"><input '+(userini.pass?'checked':'')+' class="btswitch btswitch-ios" id="pathSafe" type="checkbox">'
							+'<label class="btswitch-btn phpmyadmin-btn" for="pathSafe" onclick="pathSafe('+id+')"></label>'
						+'</span>'
					+'</div>'
					+'<div class="user_pw" style="margin-top: 10px;display:'+(userini.pass?'block;':'none;')+'">'
						+'<p><span>授权账号</span><input id="username_get" class="bt-input-text" name="username_get" value="" type="text" placeholder="不修改请留空"></p>'
						+'<p><span>访问密码</span><input id="password_get_1" class="bt-input-text" name="password_get_1" value="" type="password" placeholder="不修改请留空"></p>'
						+'<p><span>重复密码</span><input id="password_get_2" class="bt-input-text" name="password_get_1" value="" type="password" placeholder="不修改请留空"></p>'
						+'<p><button class="btn btn-success btn-sm" onclick="setPathSafe('+id+')">保存</button></p>'
					+'</div>'
				+'</div>';

		$("#webedit-con").html(webPathHtml);		
		$("#userini").change(function(){
			$.post('/site/set_dir_user_ini',{
				'path':webpath,
				'runPath':runPath,
			},function(userini){
				layer.msg(userini.msg+'<p style="color:red;">注意：设置防跨站需要重启PHP才能生效!</p>',{icon:userini.status?1:2});
				tryRestartPHP(siteName);
			},'json');
		});
		
		$("#logs").change(function(){
			var loadT = layer.msg("正在设置中...",{icon:16,time:10000,shade: [0.3, '#000']});
			$.post('/site/logs_open','id='+id, function(rdata){
				layer.close(loadT);
				layer.msg(rdata.msg,{icon:rdata.status?1:2});
			},'json');
		});
		
	},'json');
}

//是否设置访问密码
function pathSafe(id){
	var isPass = $('#pathSafe').prop('checked');
	if(!isPass){
		$(".user_pw").show();
	} else {
		var loadT = layer.msg(lan.public.the,{icon:16,time:10000,shade: [0.3, '#000']});
		$.post('/site/close_has_pwd',{id:id},function(rdata){
			layer.close(loadT);
			layer.msg(rdata.msg,{icon:rdata.status?1:2});
			$(".user_pw").hide();
		},'json');
	}
}

//设置访问密码
function setPathSafe(id){
	var username = $("#username_get").val();
	var pass1 = $("#password_get_1").val();
	var pass2 = $("#password_get_2").val();
	if(pass1 != pass2){
		layer.msg('两次输入的密码不一致!',{icon:2});
		return;
	}
	var loadT = layer.msg('正在处理,请稍候...',{icon:16,time:10000,shade: [0.3, '#000']});
	$.post('/site/set_has_pwd',{id:id,username:username,password:pass1},function(rdata){
		layer.close(loadT);
		layer.msg(rdata.msg,{icon:rdata.status?1:2});
	},'json');
}

//提交运行目录
function setSiteRunPath(id){
	var NewPath = $("#runPath").val();
	var loadT = layer.msg(lan.public.the,{icon:16,time:10000,shade: [0.3, '#000']});
	$.post('/site/set_site_run_path','id='+id+'&runPath='+NewPath,function(rdata){
		layer.close(loadT);
		var ico = rdata.status?1:2;
		layer.msg(rdata.msg,{icon:ico});
	},'json');
}

//提交网站目录
function setSitePath(id){
	var NewPath = $("#inputPath").val();
	var loadT = layer.msg('正在处理,请稍候...',{icon:16,time:10000,shade: [0.3, '#000']});
	$.post('/site/set_path','id='+id+'&path='+NewPath,function(rdata){
		layer.close(loadT);
		layer.msg(rdata.msg,{icon:rdata.status?1:2});
	},'json');
}

//修改网站备注
function webBakEdit(id){
	$.post("/data?action=getKey','table=sites&key=ps&id="+id,function(rdata){
		var webBakHtml = "<div class='webEdit-box padding-10'>\
					<div class='line'>\
					<label><span>"+lan.site.note_ph+"</span></label>\
					<div class='info-r'>\
					<textarea name='beizhu' id='webbeizhu' col='5' style='width:96%'>"+rdata+"</textarea>\
					<br><br><button class='btn btn-success btn-sm' onclick='SetSitePs("+id+")'>保存</button>\
					</div>\
					</div>";
		$("#webedit-con").html(webBakHtml);
	});
}


//设置默认文档
function setIndexEdit(id){
	$.post('/site/get_index','id='+id,function(data){
		var rdata = data['index'];
		rdata = rdata.replace(new RegExp(/(,)/g), "\n");
		var setIndexHtml = "<div id='SetIndex'><div class='SetIndex'>\
				<div class='line'>\
						<textarea class='bt-input-text' id='Dindex' name='files' style='height: 180px; width:50%; line-height:20px'>"+rdata+"</textarea>\
						<button type='button' class='btn btn-success btn-sm pull-right' onclick='setIndexList("+id+")' style='margin: 70px 130px 0px 0px;'>"+lan.public.save+"</button>\
				</div>\
				<ul class='help-info-text c7 ptb10'>\
					<li>默认文档，每行一个，优先级由上至下。</li>\
				</ul>\
				</div></div>";
		$("#webedit-con").html(setIndexHtml);
	},'json');
}

/**
 * 停止一个站点
 * @param {Int} wid  网站ID
 * @param {String} wname 网站名称
 */
function webStop(wid, wname) {
	layer.confirm('站点停用后将无法访问，您真的要停用这个站点吗？', {icon:3,closeBtn:2},function(index) {
		if (index > 0) {
			var loadT = layer.load();
			$.post("/site/stop","id=" + wid + "&name=" + wname, function(ret) {
				layer.msg(ret.msg,{icon:ret.status?1:2})
				layer.close(loadT);
				getWeb(1);
			},'json');
		}
	});
}

/**
 * 启动一个网站
 * @param {Number} wid 网站ID
 * @param {String} wname 网站名称
 */
function webStart(wid, wname) {
	layer.confirm('即将启动站点，您真的要启用这个站点吗？',{icon:3,closeBtn:2}, function(index) {
		if (index > 0) {
			var loadT = layer.load()
			$.post("/site/start","id=" + wid + "&name=" + wname, function(ret) {
				layer.msg(ret.msg,{icon:ret.status?1:2})
				layer.close(loadT);
				getWeb(1);
			},'json');
		}
	});
}

/**
 * 删除一个网站
 * @param {Number} wid 网站ID
 * @param {String} wname 网站名称
 */
function webDelete(wid, wname){
	var thtml = "<div class='options'>\
	    	<label><input type='checkbox' id='delpath' name='path'><span>根目录</span></label>\
	    	</div>";
	var info = '是否要删除同名根目录';
	safeMessage('删除站点'+"["+wname+"]",info, function(){
		var path='';
		if($("#delpath").is(":checked")){
			path='&path=1';
		}
		var loadT = layer.msg('正在处理,请稍候...',{icon:16,time:10000,shade: [0.3, '#000']});
		$.post("/site/delete","id=" + wid + "&webname=" + wname + path, function(ret){
			layer.closeAll();
			layer.msg(ret.msg,{icon:ret.status?1:2})
			getWeb(1);
		},'json');
	},thtml);
}


//批量删除
function allDeleteSite(){
	var checkList = $("input[name=id]");
	var dataList = new Array();
	for(var i=0;i<checkList.length;i++){
		if(!checkList[i].checked) continue;
		var tmp = new Object();
		tmp.name = checkList[i].title;
		tmp.id = checkList[i].value;
		dataList.push(tmp);
	}
	
	var thtml = "<div class='options'>\
	    	<label style=\"width:100%;\"><input type='checkbox' id='delpath' name='path'><span>"+lan.site.all_del_info+"</span></label>\
	    	</div>";
	safeMessage(lan.site.all_del_site,"<a style='color:red;'>"+lan.get('del_all_site',[dataList.length])+"</a>",function(){
		layer.closeAll();
		var path = '';
		if($("#delpath").is(":checked")){
			path='&path=1';
		}
		syncDeleteSite(dataList, 0,'',path);
	},thtml);
}

//模拟同步开始批量删除
function syncDeleteSite(dataList,successCount,errorMsg,path){
	if(dataList.length < 1) {
		showMsg(lan.get('del_all_site_ok',[successCount]), function(){
			// location.reload();
		},{icon:1});
		return;
	}
	var loadT = layer.msg(lan.get('del_all_task_the',[dataList[0].name]),{icon:16,time:0,shade: [0.3, '#000']});
	$.post('/site/delete', 'id='+dataList[0].id+'&webname='+dataList[0].name+path , function(rdata){
		layer.close(loadT);
		if(rdata.status){
			successCount++;
			$("input[title='"+dataList[0].name+"']").parents("tr").remove();
		} else {
			if(!errorMsg){
				errorMsg = '<br><p>'+lan.site.del_err+':</p>';
			}
			errorMsg += '<li>'+dataList[0].name+' -> '+rdata.msg+'</li>'
		}
		dataList.splice(0,1);
		syncDeleteSite(dataList,successCount,errorMsg,path);
	},'json');
}


/**
 * 域名管理
 * @param {Int} id 网站ID
 */
function domainEdit(id, name, msg, status) {
	$.post('/site/get_domain' ,{pid:id}, function(domain) {

		var echoHtml = "";
		for (var i = 0; i < domain.length; i++) {
			echoHtml += "<tr>\
				<td><a title='"+lan.site.click_access+"' target='_blank' href='http://" + domain[i].name + ":" + domain[i].port + "' class='btlinkbed'>" + domain[i].name + "</a></td>\
				<td><a class='btlinkbed'>" + domain[i].port + "</a></td>\
				<td class='text-center'><a class='table-btn-del' href='javascript:;' onclick=\"delDomain(" + id + ",'" + name + "','" + domain[i].name + "','" + domain[i].port + "',1)\"><span class='glyphicon glyphicon-trash'></span></a></td>\
				</tr>";
		}
		var bodyHtml = "<textarea id='newdomain' class='bt-input-text' style='height: 100px; width: 340px;padding:5px 10px;line-height:20px'></textarea>\
								<input type='hidden' id='newport' value='80' />\
								<button type='button' class='btn btn-success btn-sm pull-right' style='margin:30px 35px 0 0' onclick=\"domainAdd(" + id + ",'" + name + "',1)\">添加</button>\
							<div class='divtable mtb15' style='height:350px;overflow:auto'>\
								<table class='table table-hover' width='100%'>\
								<thead><tr><th>"+lan.site.domain+"</th><th width='70px'>端口</th><th width='50px' class='text-center'>操作</th></tr></thead>\
								<tbody id='checkDomain'>" + echoHtml + "</tbody>\
								</table>\
							</div>";
		$("#webedit-con").html(bodyHtml);
		if(msg != undefined){
			layer.msg(msg,{icon:status?1:5});
		}
		var placeholder = "<div class='placeholder c9' style='left:28px;width:330px;top:16px;'>每行填写一个域名，默认为80端口<br>泛解析添加方法 *.domain.com<br>如另加端口格式为 www.domain.com:88</div>";
		$('#newdomain').after(placeholder);
		$(".placeholder").click(function(){
			$(this).hide();
			$('#newdomain').focus();
		})
		$('#newdomain').focus(function() {
		    $(".placeholder").hide();
		});
		
		$('#newdomain').blur(function() {
			if($(this).val().length==0){
				$(".placeholder").show();
			}  
		});
		$("#newdomain").on("input",function(){
			var str = $(this).val();
			if(isChineseChar(str)) {
				$('.btn-zhm').show();
			} else{
				$('.btn-zhm').hide();
			}
		})
		//checkDomain();
	},'json');
}

//编辑域名/端口
function cancelSend(){
	$(".changeDomain,.changePort").hide().prev().show();
	$(".changeDomain,.changePort").remove();
}
//遍历域名
function checkDomain() {
	$("#checkDomain tr").each(function() {
		var $this = $(this);
		var domain = $(this).find("td:first-child").text();
		$(this).find("td:first-child").append("<i class='lading'></i>");
	});
}

/**
 * 添加域名
 * @param {Int} id  网站ID
 * @param {String} webname 主域名
 */
function domainAdd(id, webname,type) {
	var Domain = $("#newdomain").val().split("\n");

	var domainlist = '';
	for(var i=0; i<Domain.length; i++){
		domainlist += Domain[i]+ ',';
	}
	
	if(domainlist.length < 3){
		layer.msg(lan.site.domain_empty,{icon:5});
		return;
	}

	domainlist = domainlist.substring(0,domainlist.length-1);
	var loadT = layer.load();
	var data = "domain=" + domainlist + "&webname=" + webname + "&id=" + id;
	$.post('/site/add_domain', data, function(retuls) {
		layer.close(loadT);
		domainEdit(id, webname, retuls.msg, retuls.status);
	},'json');
}

/**
 * 删除域名
 * @param {Number} wid 网站ID
 * @param {String} wname 主域名
 * @param {String} domain 欲删除的域名
 * @param {Number} port 对应的端口
 */
function delDomain(wid, wname, domain, port,type) {
	var num = $("#checkDomain").find("tr").length;
	if(num==1){
		layer.msg(lan.site.domain_last_cannot);
	}
	layer.confirm(lan.site.domain_del_confirm,{icon:3,closeBtn:2}, function(index) {
		var url = "/site/del_domain"
		var data = "id=" + wid + "&webname=" + wname + "&domain=" + domain + "&port=" + port;
		var loadT = layer.msg(lan.public.the_del,{time:0,icon:16});
		$.post(url,data, function(ret) {
			layer.close(loadT);
			layer.msg(ret.msg,{icon:ret.status?1:2})
			if(type == 1){
				layer.close(loadT);
				domainEdit(wid,wname)
			}else{
				layer.closeAll();
				DomainRoot(wid, wname);
			}
		},'json');
	});
}

/**
 * 判断IP/域名格式
 * @param {String} domain  源文本
 * @return bool
 */
function isDomain(domain) {
	//domain = 'http://'+domain;
	var re = new RegExp();
	re.compile("^[A-Za-z0-9-_]+\\.[A-Za-z0-9-_%&\?\/.=]+$");
	if (re.test(domain)) {
		return (true);
	} else {
		return (false);
	}
}


/**
 *设置数据库备份
 * @param {Number} sign	操作标识
 * @param {Number} id	编号
 * @param {String} name	主域名
 */
function webBackup(id, name) {
	var loadT =layer.msg('正在备份,请稍候...', {icon:16,time:0,shade: [0.3, '#000']});
	$.post('/site/to_backup', "id="+id, function(rdata) {
		layer.closeAll();
		layer.msg(rdata.msg,{icon:rdata.status?1:2});

		getBackup(id);
	},'json');
}

/**
 *删除网站备份
 * @param {Number} webid	网站编号
 * @param {Number} id	文件编号
 * @param {String} name	主域名
 */
function webBackupDelete(id,pid){
	layer.confirm('真的要删除备份包吗?',{title:'删除备份文件!',icon:3,closeBtn:2},function(index){
		var loadT =layer.msg('正在删除,请稍候...', {icon:16,time:0,shade: [0.3, '#000']});
		$.post('/site/del_backup','id='+id, function(rdata){
			layer.closeAll();
			layer.msg(rdata.msg,{icon:rdata.status?1:2});
			getBackup(pid);
		},'json');
	})
}

function getBackup(id,name,page) {

	if(typeof(page) == 'undefined'){
		page = '1';
	}
	$.post('/site/get_backup','search=' + id + '&limit=5&p='+page, function(frdata){		
		var body = '';
		for (var i = 0; i < frdata.data.length; i++) {
			if(frdata.data[i].type == '1') {
				continue;
			}
			
			var ftpdown = "<a class='btlink' href='/files/download?filename="+frdata.data[i].filename+"&name="+frdata.data[i].name+"' target='_blank'>下载</a> | ";
			body += "<tr><td><span class='glyphicon glyphicon-file'></span>"+frdata.data[i].name+"</td>\
					<td>" + (toSize(frdata.data[i].size)) + "</td>\
					<td>" + frdata.data[i].addtime + "</td>\
					<td class='text-right' style='color:#ccc'>"+ ftpdown + "<a class='btlink' href='javascript:;' onclick=\"webBackupDelete('" + frdata.data[i].id + "',"+id+")\">删除</a></td>\
				</tr>"
		}

		var ftpdown = '';
		frdata.page = frdata.page.replace(/'/g,'"').replace(/getBackup\(/g,"getBackup(" + id + ",0,");

		if(name == 0){
			var sBody = "<table width='100%' id='webBackupList' class='table table-hover'>\
						<thead><tr><th>文件名称</th><th>文件大小</th><th>打包时间</th><th width='140px' class='text-right'>操作</th></tr></thead>\
						<tbody id='webBackupBody' class='list-list'>"+body+"</tbody>\
						</table>"
			$("#webBackupList").html(sBody);
			$(".page").html(frdata.page);
			return;
		}
		layer.closeAll();
		layer.open({
			type: 1,
			skin: 'demo-class',
			area: '700px',
			title: '打包备份',
			closeBtn: 1,
			shift: 0,
			shadeClose: false,
			content: "<div class='bt-form ptb15 mlr15' id='webBackup'>\
						<button class='btn btn-default btn-sm' style='margin-right:10px' type='button' onclick=\"webBackup('" + frdata['site']['id'] + "','" +  frdata['site']['name'] + "')\">打包备份</button>\
						<div class='divtable mtb15' style='margin-bottom:0'>\
							<table width='100%' id='webBackupList' class='table table-hover'>\
							<thead>\
								<tr><th>文件名称</th><th>文件大小</th><th>打包时间</th><th width='140px' class='text-right'>操作</th></tr>\
							</thead>\
							<tbody id='webBackupBody' class='list-list'>" + body + "</tbody>\
							</table>\
							<div class='page'>" + frdata.page + "</div>\
						</div>\
					</div>"
		});
	},'json');
}

function goSet(num) {
	//取选中对象
	var el = document.getElementsByTagName('input');
	var len = el.length;
	var data = '';
	var a = '';
	var count = 0;
	//构造POST数据
	for (var i = 0; i < len; i++) {
		if (el[i].checked == true && el[i].value != 'on') {
			data += a + count + '=' + el[i].value;
			a = '&';
			count++;
		}
	}
	//判断操作类别
	if(num==1){
		reAdd(data);
	}
	else if(num==2){
		shift(data);
	}
}


//设置默认文档
function setIndex(id){
	var quanju = (id==undefined)?lan.site.public_set:lan.site.local_site;
	var data=id==undefined?"":"id="+id;
	$.post('/site?action=GetIndex',data,function(rdata){
		rdata= rdata.replace(new RegExp(/(,)/g), "\n");
		layer.open({
				type: 1,
				area: '500px',
				title: lan.site.setindex,
				closeBtn: 1,
				shift: 5,
				shadeClose: true,
				content:"<form class='bt-form' id='SetIndex'><div class='SetIndex'>"
				+"<div class='line'>"
				+"	<span class='tname' style='padding-right:2px'>"+lan.site.default_doc+"</span>"
				+"	<div class='info-r'>"
				+"		<textarea id='Dindex' name='files' style='line-height:20px'>"+rdata+"</textarea>"
				+"		<p>"+quanju+lan.site.default_doc_help+"</p>"
				+"	</div>"
				+"</div>"
				+"<div class='bt-form-submit-btn'>"
				+"	<button type='button' id='web_end_time' class='btn btn-danger btn-sm btn-title' onclick='layer.closeAll()'>"+lan.public.cancel+"</button>"
			    +"    <button type='button' class='btn btn-success btn-sm btn-title' onclick='setIndexList("+id+")'>"+lan.public.ok+"</button>"
		        +"</div>"
				+"</div></form>"
		});
	});
}

//设置默认站点
function setDefaultSite(){
	var name = $("#default_site").val();
	var loadT = layer.msg('正在处理,请稍候...',{icon:16,time:0,shade: [0.3, '#000']});
	$.post('/site/set_default_site','name='+name,function(rdata){
		layer.closeAll();
		layer.msg(rdata.msg,{icon:rdata.status?1:5});
	},'json');
}


//默认站点
function getDefaultSite(){
	$.post('/site/get_default_site','',function(rdata){
		var opt = '<option value="off">未设置默认站点</option>';
		var selected = '';
		for(var i=0;i<rdata.sites.length;i++){
			selected = '';
			if(rdata.default_site == rdata.sites[i].name) selected = 'selected';
			opt += '<option value="' + rdata.sites[i].name + '" ' + selected + '>' + rdata.sites[i].name + '</option>';
		}
		
		layer.open({
			type: 1,
			area: '530px',
			title: '设置默认站点',
			closeBtn: 1,
			shift: 5,
			shadeClose: true,
			content:'<div class="bt-form ptb15 pb70">\
						<p class="line">\
							<span class="tname text-right">默认站点</span>\
							<select id="default_site" class="bt-input-text" style="width: 300px;">'+opt+'</select>\
						</p>\
						<ul class="help-info-text c6 plr20">\
						    <li>设置默认站点后,所有未绑定的域名和IP都被定向到默认站点</li>\
						    <li>可有效防止恶意解析</li>\
					    </ul>\
						<div class="bt-form-submit-btn">\
							<button type="button" class="btn btn-danger btn-sm btn-title" onclick="layer.closeAll()">取消</button>\
							<button class="btn btn-success btn-sm btn-title" onclick="setDefaultSite()">确定</button>\
						</div>\
					</div>'
		});
	},'json');
}

function setPHPVer(){
	$.post('/site/get_cli_php_version','',function(rdata){
		if(typeof(rdata['status'])!='undefined'){
			layer.msg(rdata.msg,{icon:rdata.status?1:2});
			return;
		}

		var opt = '';
		var selected = '';
		for(var i=0;i<rdata.versions.length;i++){
			selected = '';
			if(rdata.select.version == rdata.versions[i].version) selected = 'selected';

			if (rdata.versions[i].version.indexOf("yum")>-1){
				continue;
			}

			if (rdata.versions[i].version.indexOf("apt")>-1){
				continue;
			}

			opt += '<option value="' + rdata.versions[i].version + '" ' + selected + '>' + rdata.versions[i].name + '</option>';
		}
		
		var phpver_layer = layer.open({
			type: 1,
			area: '530px',
			title: '设置PHP-CLI(命令行)版本',
			closeBtn: 1,
			shift: 5,
			shadeClose: true,
			btn:["确定","取消"],
			content:'<div class="bt-form ptb15">\
						<p class="line">\
							<span class="tname text-right">PHP-CLI版本</span>\
							<select id="default_ver" class="bt-input-text" style="width: 300px;">'+opt+'</select>\
						</p>\
						<ul class="help-info-text c6 plr20">\
						    <li>此处可设置命令行运行php时使用的PHP版本</li>\
						    <li>安装新的PHP版本后此处需要重新设置</li>\
					    </ul>\
					</div>',
			yes:function(layero,index){
				var version = $("#default_ver").val();
				var loadT = layer.msg('正在处理,请稍候...',{icon:16,time:0,shade: [0.3, '#000']});
				$.post('/site/set_cli_php_version','version='+version,function(rdata){
					layer.close(loadT);
					showMsg(rdata.msg,function(){
						if (rdata.status){
							layer.close(phpver_layer);
						}
					},{icon:rdata.status?1:5},2000);
				},'json');
			},
		});
	},'json');
}

function setIndexList(id){
	var Dindex = $("#Dindex").val().replace(new RegExp(/(\n)/g), ",");
	if(id == undefined ){
		var data="id=&index="+Dindex;
	} else{
		var data="id="+id+"&index="+Dindex;
	}
	var loadT= layer.load(2);
	$.post('/site/set_index',data,function(rdata){
		layer.close(loadT);
		var ico = rdata.status? 1:5;
		layer.msg(rdata.msg,{icon:ico});
	},'json');
}


/*站点修改*/
function webEdit(id,website,endTime,addtime){
	layer.open({
		type: 1,
		area: '700px',
		title: '站点修改['+website+']  --  添加时间['+addtime+']',
		closeBtn: 1,
		shift: 0,
		content: "<div class='bt-form'>\
			<div class='bt-w-menu pull-left' style='height: 565px;'>\
				<p class='bgw'  onclick=\"domainEdit(" + id + ",'" + website + "')\">"+lan.site.domain_man+"</p>\
				<p onclick='dirBinding("+id+")' title='子目录绑定'>子目录绑定</p>\
				<p onclick='webPathEdit("+id+")' title='网站目录'>网站目录</p>\
				<p onclick='limitNet("+id+")' title='流量限制'>流量限制</p>\
				<p onclick=\"rewrite('"+website+"')\" title='伪静态'>伪静态</p>\
				<p onclick='setIndexEdit("+id+")' title='默认文档'>默认文档</p>\
				<p onclick=\"configFile('"+website+"')\" title='配置文件'>配置文件</p>\
				<p onclick=\"setSSL("+id+",'"+website+"')\" title='SSL'>SSL</p>\
				<p onclick=\"phpVersion('"+website+"')\" title='PHP版本'>PHP版本</p>\
				<p onclick=\"to301('"+website+"')\" title='重定向'>重定向</p>\
				<p onclick=\"toProxy('"+website+"')\" title='反向代理'>反向代理</p>\
				<p id='site_"+id+"' onclick=\"security('"+id+"','"+website+"')\" title='防盗链'>防盗链</p>\
				<p id='site_"+id+"' onclick=\"getSiteLogs('"+website+"')\" title='查看站点请求日志'>响应日志</p>\
				<p id='site_"+id+"' onclick=\"getSiteErrorLogs('"+website+"')\" title='查看站点错误日志'>错误日志</p>\
			</div>\
			<div id='webedit-con' class='bt-w-con webedit-con pd15' style='height: 565px;overflow: scroll;'></div>\
		</div>",
		success:function(){
			//域名输入提示
			var placeholder = "<div class='placeholder'>每行填写一个域名，默认为80端口<br>泛解析添加方法 *.domain.com<br>如另加端口格式为 www.domain.com:88</div>";
			$('#newdomain').after(placeholder);
			$(".placeholder").click(function(){
				$(this).hide();
				$('#newdomain').focus();
			});

			$('#newdomain').focus(function() {
			    $(".placeholder").hide();
			});
			
			$('#newdomain').blur(function() {
				if($(this).val().length == 0){
					$(".placeholder").show();
				}  
			});

			//切换
			$(".bt-w-menu p").click(function(){
				$(this).addClass("bgw").siblings().removeClass("bgw");
			});

			domainEdit(id,website);
		}
	});	
}

//取网站日志
function getSiteLogs(siteName){
	var loadT = layer.msg('正在处理,请稍候...',{icon:16,time:0,shade: [0.3, '#000']});
	$.post('/site/get_logs',{siteName:siteName},function(logs){
		layer.close(loadT);
		if(logs.status !== true){
			logs.msg = '';
		}
		if (logs.msg == '') logs.msg = '当前没有日志.';
		var phpCon = '<textarea wrap="off" readonly="" style="white-space: pre;margin: 0px;width: 560px;height: 530px;background-color: #333;color:#fff; padding:0 5px" id="error_log">'+logs.msg+'</textarea>';
		$("#webedit-con").html(phpCon);
		var ob = document.getElementById('error_log');
		ob.scrollTop = ob.scrollHeight;		
	},'json');
}

//取网站错误日志
function getSiteErrorLogs(siteName){
	var loadT = layer.msg('正在处理,请稍候...',{icon:16,time:0,shade: [0.3, '#000']});
	$.post('/site/get_error_logs',{siteName:siteName},function(logs){
		// console.log(logs);
		layer.close(loadT);
		if(logs.status !== true){
			logs.msg = '';
		}
		if (logs.msg == '') logs.msg = '当前没有日志.';
		var phpCon = '<textarea wrap="off" readonly="" style="white-space: pre;margin: 0px;width: 560px;height: 530px;background-color: #333;color:#fff; padding:0 5px" id="error_log">'+logs.msg+'</textarea>';
		$("#webedit-con").html(phpCon);
		var ob = document.getElementById('error_log');
		ob.scrollTop = ob.scrollHeight;		
	},'json');
}


//防盗链
function security(id,name){
	var loadT = layer.msg(lan.site.the_msg,{icon:16,time:0,shade: [0.3, '#000']});
	$.post('/site/get_security',{id:id,name:name},function(rdata){
		console.log(rdata);
		layer.close(loadT);
		var mbody = '<div>'
					+'<p style="margin-bottom:8px"><span style="display: inline-block; width: 60px;">URL后缀</span><input class="bt-input-text" type="text" name="sec_fix" value="'+rdata.fix+'" style="margin-left: 5px;width: 425px;height: 30px;margin-right:10px;'+(rdata.status?'background-color: #eee;':'')+'" placeholder="多个请用逗号隔开,例：png,jpeg,jpg,gif,zip" '+(rdata.status?'readonly':'')+'></p>'
					+'<p style="margin-bottom:8px"><span style="display: inline-block; width: 60px;">许可域名</span><input class="bt-input-text" type="text" name="sec_domains" value="'+rdata.domains+'" style="margin-left: 5px;width: 425px;height: 30px;margin-right:10px;'+(rdata.status?'background-color: #eee;':'')+'" placeholder="支持通配符,多个域名请用逗号隔开,例：*.test.com,test.com" '+(rdata.status?'readonly':'')+'></p>'
					+'<div class="label-input-group ptb10"><label style="font-weight:normal"><input type="checkbox" name="sec_status" onclick="setSecurity(\''+name+'\','+id+')" '+(rdata.status?'checked':'')+'>启用防盗链</label></div>'
					+'<div class="label-input-group ptb10"><label style="font-weight:normal"><input type="checkbox" name="sec_none_status" onclick="setSecurity(\''+name+'\','+id+')" '+(rdata.none?'checked':'')+'>允许空HTTP_REFERER请求</label></div>'
					+'<ul class="help-info-text c7 ptb10">'
						+'<li>默认允许资源被直接访问,即不限制HTTP_REFERER为空的请求</li>'
						+'<li>多个URL后缀与域名请使用逗号(,)隔开,如: png,jpeg,zip,js</li>'
						+'<li>当触发防盗链时,将直接返回404状态</li>'
					+'</ul>'
				+'</div>'
		$("#webedit-con").html(mbody);
	},'json');
}

//设置防盗链
function setSecurity(name,id, none){
	setTimeout(function(){
		var data = {
			fix:$("input[name='sec_fix']").val(),
			domains:$("input[name='sec_domains']").val(),
			status:$("input[name='sec_status']").prop("checked"),
			none:$("input[name='sec_none_status']").prop("checked"),
			name:name,
			id:id
		}
		var loadT = layer.msg(lan.site.the_msg,{icon:16,time:0,shade: [0.3, '#000']});
		$.post('/site/set_security',data,function(rdata){
			layer.close(loadT);
			layer.msg(rdata.msg,{icon:rdata.status?1:2});
			if(rdata.status) setTimeout(function(){security(id,name);},1000);
		},'json');
	},100);
}


//流量限制
function limitNet(id){
	$.post('/site/get_limit_net','id='+id, function(rdata){
		var status_selected = rdata.perserver != 0?'checked':'';
		if(rdata.perserver == 0){
			rdata.perserver = 300;
			rdata.perip = 25;
			rdata.limit_rate = 512;
		}
		var limitList = "<option value='1' "+((rdata.perserver == 0 || rdata.perserver == 300)?'selected':'')+">"+lan.site.limit_net_1+"</option>"
						+"<option value='2' "+((rdata.perserver == 200)?'selected':'')+">"+lan.site.limit_net_2+"</option>"
						+"<option value='3' "+((rdata.perserver == 50)?'selected':'')+">"+lan.site.limit_net_3+"</option>"
						+"<option value='4' "+((rdata.perserver == 500)?'selected':'')+">"+lan.site.limit_net_4+"</option>"
						+"<option value='5'  "+((rdata.perserver == 400)?'selected':'')+">"+lan.site.limit_net_5+"</option>"
						+"<option value='6' "+((rdata.perserver == 60)?'selected':'')+">"+lan.site.limit_net_6+"</option>"
						+"<option value='7' "+((rdata.perserver == 150)?'selected':'')+">"+lan.site.limit_net_7+"</option>"
		var body = "<div class='dirBinding flow c4'>"
				+'<p class="label-input-group ptb10"><label style="font-weight:normal"><input type="checkbox" name="status" '+status_selected+' onclick="saveLimitNet('+id+')" style="width:15px;height:15px;margin-right:5px" />'+lan.site.limit_net_8+'</label></p>'
				+"<p class='line' style='padding:10px 0'><span class='span_tit mr5'>"+lan.site.limit_net_9+"：</span><select class='bt-input-text mr20' name='limit' style='width:90px'>"+limitList+"</select></p>"
			    +"<p class='line' style='padding:10px 0'><span class='span_tit mr5'>"+lan.site.limit_net_10+"：</span><input class='bt-input-text mr20' style='width: 90px;' type='number' name='perserver' value='"+rdata.perserver+"' /></p>"
			    +"<p class='line' style='padding:10px 0'><span class='span_tit mr5'>"+lan.site.limit_net_12+"：</span><input class='bt-input-text mr20' style='width: 90px;' type='number' name='perip' value='"+rdata.perip+"' /></p>"
			    +"<p class='line' style='padding:10px 0'><span class='span_tit mr5'>"+lan.site.limit_net_14+"：</span><input class='bt-input-text mr20' style='width: 90px;' type='number' name='limit_rate' value='"+rdata.limit_rate+"' /></p>"
			    +"<button class='btn btn-success btn-sm mt10' onclick='saveLimitNet("+id+",1)'>"+lan.public.save+"</button>"
			    +"</div>"
				+"<ul class='help-info-text c7 mtb15'><li>"+lan.site.limit_net_11+"</li><li>"+lan.site.limit_net_13+"</li><li>"+lan.site.limit_net_15+"</li></ul>"
		$("#webedit-con").html(body);
			
		$("select[name='limit']").change(function(){
			var type = $(this).val();
			perserver = 300;
			perip = 25;
			limit_rate = 512;
			switch(type){
				case '1':
					perserver = 300;
					perip = 25;
					limit_rate = 512;
					break;
				case '2':
					perserver = 200;
					perip = 10;
					limit_rate = 1024;
					break;
				case '3':
					perserver = 50;
					perip = 3;
					limit_rate = 2048;
					break;
				case '4':
					perserver = 500;
					perip = 10;
					limit_rate = 2048;
					break;
				case '5':
					perserver = 400;
					perip = 15;
					limit_rate = 1024;
					break;
				case '6':
					perserver = 60;
					perip = 10;
					limit_rate = 512;
					break;
				case '7':
					perserver = 150;
					perip = 4;
					limit_rate = 1024;
					break;
			}
			
			$("input[name='perserver']").val(perserver);
			$("input[name='perip']").val(perip);
			$("input[name='limit_rate']").val(limit_rate);
		});
	},'json');
}


//保存流量限制配置
function saveLimitNet(id, type){
	var isChecked = $("input[name='status']").attr('checked');
	if(isChecked == undefined || type == 1 ){
		var data = 'id='+id+'&perserver='+$("input[name='perserver']").val()+'&perip='+$("input[name='perip']").val()+'&limit_rate='+$("input[name='limit_rate']").val();
		var loadT = layer.msg(lan.public.config,{icon:16,time:10000})
		$.post('/site/save_limit_net',data,function(rdata){
			layer.close(loadT);
			limitNet(id);
			layer.msg(rdata.msg,{icon:rdata.status?1:2});
		},'json');
	}else{
		var loadT = layer.msg(lan.public.config,{icon:16,time:10000})
		$.post('/site/close_limit_net',{id:id},function(rdata){
			layer.close(loadT);
			limitNet(id);
			layer.msg(rdata.msg,{icon:rdata.status?1:2});
		},'json');
	}
}


//子目录绑定
function dirBinding(id){
	$.post('/site/get_dir_binding',{'id':id},function(data){
		var rdata = data['data'];
		var echoHtml = '';
		for(var i=0;i<rdata.binding.length;i++){
			echoHtml += "<tr><td>"+rdata.binding[i].domain+"</td><td>"+rdata.binding[i].port+"</td><td>"+rdata.binding[i].path+"</td><td class='text-right'><a class='btlink' href='javascript:setDirRewrite("+rdata.binding[i].id+");'>伪静态</a> | <a class='btlink' href='javascript:delDirBind("+rdata.binding[i].id+","+id+");'>删除</a></td></tr>";
		}
		
		var dirList = '';
		for(var n=0;n<rdata.dirs.length;n++){
			dirList += "<option value='"+rdata.dirs[n]+"'>"+rdata.dirs[n]+"</option>";
		}
		
		var body = "<div class='dirBinding c5'>"
			   + "域名：<input class='bt-input-text mr20' type='text' name='domain' />"
			   + "子目录：<select class='bt-input-text mr20' name='dirName'>"+dirList+"</select>"
			   + "<button class='btn btn-success btn-sm' onclick='addDirBinding("+id+")'>添加</button>"
			   + "</div>"
			   + "<div class='divtable mtb15' style='height:470px;overflow:auto'><table class='table table-hover' width='100%' style='margin-bottom:0'>"
			   + "<thead><tr><th>域名</th><th width='70'>端口</th><th width='100'>子目录</th><th width='100' class='text-right'>操作</th></tr></thead>"
			   + "<tbody id='checkDomain'>" + echoHtml + "</tbody>"
			   + "</table></div>";
		
		$("#webedit-con").html(body);
	},'json');
}

//子目录伪静态
function setDirRewrite(id){
	$.post('/site/get_dir_bind_rewrite','id='+id,function(rdata){
		if(!rdata.status){
			var confirmObj = layer.confirm('你真的要为这个子目录创建独立的伪静态规则吗？',{icon:3,closeBtn:2},function(){
				$.post('/site/get_dir_bind_rewrite','id='+id+'&add=1',function(rdata){
					layer.close(confirmObj);
					showRewrite(rdata);
				},'json');
			});
			return;
		}
		showRewrite(rdata);
	},'json');
}

//显示伪静态
function showRewrite(rdata){
	var rList = ''; 
	for(var i=0;i<rdata.rlist.length;i++){
		rList += "<option value='"+rdata.rlist[i]+"'>"+rdata.rlist[i]+"</option>";
	}
	var webBakHtml = "<div class='c5 plr15'>\
				<div class='line'>\
					<select class='bt-input-text mr20' id='myRewrite' name='rewrite' style='width:30%;'>"+rList+"</select>\
					<textarea class='bt-input-text mtb15' style='height: 260px; width: 470px; line-height:18px;padding:5px;' id='rewriteBody'>"+rdata.data+"</textarea>\
				</div>\
				<button id='setRewriteBtn' class='btn btn-success btn-sm'>保存</button>\
				<ul class='help-info-text c7 ptb10'>\
					<li>请选择您的应用，若设置伪静态后，网站无法正常访问，请尝试设置回default</li>\
					<li>您可以对伪静态规则进行修改，修改完后保存即可。</li>\
				</ul>\
			</div>";
	layer.open({
		type: 1,
		area: '500px',
		title: '配置伪静态规则',
		closeBtn: 1,
		shift: 5,
		shadeClose: true,
		content:webBakHtml,
		success:function(){

			$("#myRewrite").change(function(){
				var rewriteName = $(this).val();
				$.post('/files/get_body','path='+rdata['rewrite_dir']+'/'+rewriteName+'.conf',function(fileBody){
					 $("#rewriteBody").val(fileBody.data.data);
				},'json');
			});

			$('#setRewriteBtn').click(function(){
				var data = $("#rewriteBody").val();
				setRewrite(rdata.filename, encodeURIComponent(data));
			});
		}
	});
}

//添加子目录绑定
function addDirBinding(id){
	var domain = $("input[name='domain']").val();
	var dirName = $("select[name='dirName']").val();
	if(domain == '' || dirName == '' || dirName == null){
		layer.msg(lan.site.d_s_empty,{icon:2});
		return;
	}
	
	var data = 'id='+id+'&domain='+domain+'&dirName='+dirName;
	$.post('/site/add_dir_bind',data,function(rdata){
		dirBinding(id);
		layer.msg(rdata.msg,{icon:rdata.status?1:2});
	},'json');
}

//删除子目录绑定
function delDirBind(id,siteId){
	layer.confirm(lan.site.s_bin_del,{icon:3,closeBtn:2},function(){
		$.post('/site/del_dir_bind','id='+id,function(rdata){
			dirBinding(siteId);
			layer.msg(rdata.msg,{icon:rdata.status?1:2});
		},'json');
	});
}
		
//301重定向
function to301(siteName, type, obj){
	
	// 设置 页面展示
	if(type == 1) {
		obj = {
			to: 'http://',
			from: '',
			r_type: '',
			type: 1,
			type: 'path',
			keep_path: 1
		}
		var redirect_form = layer.open({
			type: 1,
			skin: 'demo-class',
			area: '650px',
			title: type == 1 ? '创建重定向' : '修改重定向[' + obj.redirectname + ']',
			closeBtn: 1,
			shift: 5,
			shadeClose: false,
			content: "<form id='form_redirect' class='divtable pd20' style='padding-bottom: 60px'>" +
				"<div class='line' style='overflow:hidden;height: 40px;'>" +
				"<div style='display: inline-block;'>" +
				"<span class='tname' style='margin-left:10px;position: relative;top: -5px;'>保留URI参数</span>" +
				"<input class='btswitch btswitch-ios' id='keep_path' type='checkbox' name='keep_path' " + (obj.keep_path == 1 ? 'checked="checked"' : '') + " /><label class='btswitch-btn phpmyadmin-btn' for='keep_path' style='float:left'></label>" +
				"</div>" +
				"</div>" +
				"<div class='line' style='clear:both;'>" +
				"<span class='tname'>重定向类型</span>" +
				"<div class='info-r  ml0'>" +
				"<select class='bt-input-text mr5' name='type' style='width:100px'><option value='domain' " + (obj.type == 'domain' ? 'selected ="selected"' : "") + ">域名</option><option value='path'  " + (obj.type == 'path' ? 'selected ="selected"' : "") + ">路径</option></select>" +
				"<span class='mlr15'>重定向方式</span>" +
				"<select class='bt-input-text ml10' name='r_type' style='width:100px'><option value='301' " + (obj.r_type == '301' ? 'selected ="selected"' : "") + " >301</option><option value='302' " + (obj.r_type == '302' ? 'selected ="selected"' : "") + ">302</option></select></div>" +
				"</div>" +
				"<div class='line redirectdomain'>" +
				"<span class='tname'>重定向源</span>" +
				"<div class='info-r  ml0'>" +
				"<input  name='from' placeholder='域名或路径' class='bt-input-text mr5' type='text' style='width:200px;float: left;margin-right:0px' value='" + obj.from + "'>" +
				"<span class='tname' style='width:90px'>目标URL</span>" +
				"<input  name='to' class='bt-input-text mr5' type='text' style='width:200px' value='" + obj.to + "'>" +
				"</div>" +
				"</div>" +
				"</div>" +
				"<div class='bt-form-submit-btn'><button type='button' class='btn btn-sm btn-danger btn-colse-prosy'>关闭</button><button type='button' class='btn btn-sm btn-success btn-submit-redirect'>" + (type == 1 ? " 提交" : "保存") + "</button></div>" +
				"</form>"
		});
		setTimeout(function() {
			$('.btn-colse-prosy').click(function() {
				layer.close(redirect_form);
			});
			$('.btn-submit-redirect').click(function() {
				var keep_path = $('[name="keep_path"]').prop('checked') ? 1 : 0;
				var r_type = $('[name="r_type"]').val();
				var type = $('[name="type"]').val();
				var from = $('[name="from"]').val();
				var to = $('[name="to"]').val();
				
				$.post('/site/set_redirect', {
					siteName: siteName,
					type: type,
					r_type: r_type,
					from: from,
					to: to,
					keep_path: keep_path
				}, function(res) {
					res = JSON.parse(res);
					if (res.status) {
						layer.close(redirect_form);
						to301(siteName)
					} else {
						layer.msg(res.msg, {
							icon: 2
						});
					}
				});
			});
		}, 100);
	}

	if (type == 2) {
		$.post('/site/del_redirect', {
			siteName: siteName,
			id: obj,
		}, function(res) {
			res = JSON.parse(res);
			if (res.status == true) {
				layer.msg('删除成功', {time: 1000,icon: 1});
				to301(siteName);
			} else {
				layer.msg(res.msg, {time: 1000,icon: 2});
			}
		});
		return
	}

	if (type == 3) {
		var laoding = layer.load();
		var data = {siteName: siteName,id: obj};
		$.post('/site/get_redirect_conf', data, function(res) {
			layer.close(laoding);
			res = JSON.parse(res);
			if (res.status == true) {
				var mBody = "<div class='webEdit-box' style='padding: 20px'>\
				<textarea style='height: 320px; width: 445px; margin-left: 20px; line-height:18px' id='configRedirectBody'>"+res.data.result+"</textarea>\
					<div class='info-r'>\
						<ul class='help-info-text c7 ptb10'>\
							<li>此处为重定向配置文件,若您不了解配置规则,请勿随意修改.</li>\
						</ul>\
					</div>\
				</div>";
				var editor;
				var index = layer.open({
					type: 1,
					title: '编辑配置文件',
					closeBtn: 1,
					shadeClose: true,
					area: ['500px', '500px'],
					btn: ['提交','关闭'],
					content: mBody,
					success: function () {
						editor = CodeMirror.fromTextArea(document.getElementById("configRedirectBody"), {
							extraKeys: {"Ctrl-Space": "autocomplete"},
							lineNumbers: true,
							matchBrackets:true,
						});
						editor.focus();
						$(".CodeMirror-scroll").css({"height":"300px","margin":0,"padding":0});
						$("#onlineEditFileBtn").unbind('click');
					},
					yes:function(index,layero){
						$("#configRedirectBody").empty().text(editor.getValue());
						var load = layer.load();
						var data = {
							siteName: siteName,
							id: obj,
							config: editor.getValue(),
						};
						$.post('/site/save_redirect_conf', data, function(res) {
							layer.close(load)
							if (res.status == true) {
								layer.msg('保存成功', {icon: 1});
								layer.close(index);
							} else {
								layer.msg(res.msg, {time: 3000,icon: 2});
							}
						},'json');
						return true;
			        },
				});
				
			} else {
				layer.msg('请求错误!!', {time: 3000,icon: 2});
			}
		});
		return
	}

	var body = '<div id="redirect_list" class="bt_table">\
					<div style="padding-bottom: 10px">\
						<button type="button" title="添加重定向" class="btn btn-success btn-sm mr5" onclick="to301(\''+siteName+'\',1)" ><span>添加重定向</span></button>\
					</div>\
					<div class="divtable" style="max-height:200px;">\
						<table class="table table-hover" >\
							<thead style="position: relative;z-index: 1;">\
								<tr>\
									<th><span data-index="1"><span>重定向类型</span></span></th>\
									<th><span data-index="2"><span>重定向方式</span></span></th>\
									<th><span data-index="3"><span>保留URL参数</span></span></th>\
									<th><span data-index="4"><span>操作</span></span></th>\
								</tr>\
							</thead>\
							<tbody id="md-301-body">\
							</tbody>\
						</table>\
					</div>\
				</div>';
	$("#webedit-con").html(body);
	
	var loadT = layer.msg(lan.site.the_msg,{icon:16,time:0,shade: [0.3, '#000']});
	$.post('/site/get_redirect','siteName='+siteName, function(res) {
		layer.close(loadT);
		$("#md-301-loading").remove();
		if (res.status === true) {
			let data = res.data.result;
			data.forEach(function(item){
				lan_r_type = item.r_type == 0 ? "永久重定向" : "临时重定向"
				keep_path = item.keep_path == 0 ? "不保留" : "保留"
				let tmp = '<tr>\
					<td><span data-index="1"><span>'+item.r_from+'</span></span></td>\
					<td><span data-index="2"><span>'+lan_r_type+'</span></span></td>\
					<td><span data-index="2"><span>'+keep_path+'</span></span></td>\
					<td><span data-index="4"  onclick="to301(\''+siteName+'\', 3, \''+ item.id +'\')"  class="btlink">详细</span> | <span data-index="5" onclick="to301(\''+siteName+'\', 2, \''+ item.id +'\')" class="btlink">删除</span></td>\
				</tr>';
				$("#md-301-body").append(tmp);
			})
		} else {
			layer.msg(res.msg, {icon:2});
		}
	},'json');
}


//反向代理
function toProxy(siteName, type, obj) {
	// 设置 页面展示
	if(type == 1) {
		var proxy_title = "创建反向代理";
		if (typeof(obj) != 'undefined'){
			proxy_title = "编辑反向代理";
		}

		layer.open({
			type: 1,
			area: '650px',
			title: proxy_title,
			closeBtn: 1,
			shift: 5,
			shadeClose: false,
			btn: ['提交','关闭'],
			content: "<form id='form_proxy' class='divtable pd15' style='padding-bottom: 10px'>\
				<div class='line'>\
					<span class='tname'>开启代理</span>\
					<div class='info-r ml0 mt5'>\
						<input name='open_proxy' class='btswitch btswitch-ios' type='checkbox' checked>\
						<label id='open_proxy' class='btswitch-btn' for='openProxy' style='float:left'></label>\
						<div style='display: inline-block'>\
							<span class='tname' style='margin-left:15px;position: relative;top: -5px;'>是否缓存</span>\
							<input class='btswitch btswitch-ios' type='checkbox' name='open_cache'>\
							<label class='btswitch-btn' id='open_cache' for='openCache' style='float:left'></label>\
						</div>\
					</div>\
				</div>\
				<div class='line'>\
					<span class='tname'>名称</span>\
					<div class='info-r ml0'>\
					<input name='name' value='index' placeholder='请输入名称' class='bt-input-text mr5' type='text' style='width:200px''>\
					</div>\
				</div>\
				<div class='line' style='display:none' id='cache_time'>\
					<span class='tname'>缓存时间</span>\
					<div class='info-r ml0'>\
					<input name='cache_time' value='1' class='bt-input-text mr5' type='text' style='width:200px''>分钟\
					</div>\
				</div>\
				<div class='line'>\
					<span class='tname'>代理目录</span>\
					<div class='info-r ml0'>\
					<input name='from' value='/' placeholder='/' class='bt-input-text mr5' type='text' style='width:200px''>\
					</div>\
				</div>\
				<div class='line'>\
					<span class='tname'>目标URL</span>\
					<div class='info-r ml0'>\
					<input name='to' class='bt-input-text mr5' type='text' style='width:200px;float: left;margin-right:0px''>\
					<span class='tname' style='width:90px'>发送域名</span>\
					<input name='host' value='$host' class='bt-input-text mr5' type='text' style='width:200px'>\
					</div>\
				</div>\
				<input name='id' value='' type='hidden'>\
				<div class='help-info-text c7'>\
					<ul class='help-info-text c7'>\
					<li>代理目录：访问这个目录时将会把目标URL的内容返回并显示</li>\
					<li>目标URL：可以填写你需要代理的站点，目标URL必须为可正常访问的URL，否则将返回错误</li>\
					<li>发送域名：将域名添加到请求头传递到代理服务器，默认为目标URL域名，若设置不当可能导致代理无法正常运行</li>\
					</ul>\
				</div>\
				</form>",
			success:function(){

				if (typeof(obj) != 'undefined'){
					// console.log(obj);
					$('input[name="name"]').val(obj['name']).attr('readonly','readonly').addClass('disabled');
					if (obj['open_cache'] == 'on'){
						$("input[name='open_cache']").prop("checked",true);
						$('#cache_time').show();
					}

					$('input[name="from"]').val(obj['from']);
					$('input[name="to"]').val(obj['to']);

					var url = obj['to'];
					var ip_reg = /^(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])$/;
	                url = url.replace(/^http[s]?:\/\//, '');
	                url = url.replace(/(:|\?|\/|\\)(.*)$/, '');
	                if (ip_reg.test(url)) {
	                    $("[name='host']").val('$host');
	                } else {
	                    $("[name='host']").val(url);
	                }

	                $('input[name="id"]').val(obj['id']);
	                $('input[name="cache_time"]').val(obj['cache_time']);
				}


				$('input[name="to"]').on('keyup', function(){
					var url = $(this).val();
					var ip_reg = /^(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])$/;
	                url = url.replace(/^http[s]?:\/\//, '');
	                url = url.replace(/(:|\?|\/|\\)(.*)$/, '');
	                if (ip_reg.test(url)) {
	                    $("[name='host']").val('$host');
	                } else {
	                    $("[name='host']").val(url);
	                }
				});

				$("#open_proxy").click(function(){
					var status = $("input[name='open_proxy']").prop("checked")==true?1:0;
					if(status==1){
						$("input[name='open_proxy']").prop("checked",false);
					}else{
						$("input[name='open_proxy']").prop("checked",true);
					}
				});

				$('#open_cache').click(function(){
					var status = $("input[name='open_cache']").prop("checked")==true?1:0;
					if(status==1){
						$('#cache_time').hide();
						$("input[name='open_cache']").prop("checked",false);
					}else{
						$('#cache_time').show();
						$("input[name='open_cache']").prop("checked",true);
					}
				});
			},
			yes:function(index,layer_ro){
				var data = $('#form_proxy').serializeArray();
				var t = {};
				t['name'] = 'siteName';
				t['value'] = siteName;
				data.push(t);

				// console.log(data);
				var loading = layer.msg('正在'+proxy_title+'...',{icon:16,time:0,shade: [0.3, '#000']});
				$.post('/site/set_proxy',data, function(res) {
					layer.close(loading);
					if (!res.status){
						layer.msg(res.msg, {icon: 2,time:10000});
						return;
					}

					showMsg(proxy_title+"成功!",function(){
						layer.close(index);
						toProxy(siteName);
					},{icon: 1, time:2000});
				},'json');
			}
		});
	}

	if (type == 2) {
		var loading = layer.msg('正在删除中...',{icon:16,time:0,shade: [0.3, '#000']});
		$.post('/site/del_proxy', {siteName: siteName,id: obj,}, function(res) {
			layer.close(loading);
			if (res.status == true) {
				showMsg('删除成功', function(){
					toProxy(siteName);
				},{time: 1000,icon: 1});
			} else {
				layer.msg(res.msg, {time: 1000,icon: 2});
			}
		},'json');
		return
	}


	if (type == 3) {
		var laoding = layer.load();
		var data = {siteName: siteName,id: obj};
		$.post('/site/get_proxy_conf', data, function(res) {
			layer.close(laoding);
			if (!res.status){
				layer.msg('请求错误!!', {time: 3000,icon: 2});
				return;
			}

			var mBody = "<div class='webEdit-box' style='padding: 20px'>\
			<textarea style='height: 320px; width: 445px; margin-left: 20px; line-height:18px' id='configProxyBody'>"+res.data.result+"</textarea>\
				<div class='info-r'>\
					<ul class='help-info-text c7 ptb10'>\
						<li>此处为反向代理配置文件,若您不了解配置规则,请勿随意修改.</li>\
					</ul>\
				</div>\
			</div>";
			var editor;
			var index = layer.open({
				type: 1,
				title: '编辑配置文件',
				closeBtn: 1,
				shadeClose: true,
				area: ['500px', '500px'],
				btn: ['提交','关闭'],
				content: mBody,
				success: function () {
					editor = CodeMirror.fromTextArea(document.getElementById("configProxyBody"), {
						extraKeys: {"Ctrl-Space": "autocomplete"},
						lineNumbers: true,
						matchBrackets:true,
					});
					editor.focus();
					$(".CodeMirror-scroll").css({"height":"300px","margin":0,"padding":0});
					$("#onlineEditFileBtn").unbind('click');
				},
				yes:function(index,layero){
					$("#configProxyBody").empty().text(editor.getValue());
					var load = layer.load();
					var data = {
						siteName: siteName,
						id: obj,
						config: editor.getValue(),
					};

					$.post('/site/save_proxy_conf', data, function(res) {
						layer.close(load)
						if (res.status == true) {
							layer.msg('保存成功', {icon: 1});
							layer.close(index);
						} else {
							layer.msg(res.msg, {time: 3000,icon: 2});
						}
					},'json');
					return true;
		        },
			});
		},'json');
		return;
	}

	if (type == 10 || type == 11) {
		//[11]启动 或 停止[10]
		status = type==10 ? '0' : '1';
		var loading = layer.msg(lan.site.the_msg,{icon:16,time:0,shade: [0.3, '#000']});
		$.post('/site/set_proxy_status', {siteName: siteName,'status':status,'id':obj}, function(rdata) {
			layer.close(loading);
			if (!rdata.status){
				layer.msg(res.msg, {time: 3000,icon: 2});
				return;
			}

			showMsg("设置成功",function(){
				toProxy(siteName);
			},{icon: 1,time:2000});
		},'json');
		return;
	}

	if (type == 20 || type == 21) {
		//[20] 开始缓存 或 [21] 停止缓存
		var status = type == 20 ? 'on' : '';
		obj['open_cache'] = status;
		obj['siteName'] = siteName;

		var loading = layer.msg('正在提交请求...',{icon:16,time:0,shade: [0.3, '#000']});
		$.post('/site/set_proxy',obj, function(rdata) {
			layer.close(loading);
			if (!rdata.status){
				layer.msg(rdata.msg, {icon: 2,time:2000});
				return;
			}

			showMsg("设置成功!",function(){
				toProxy(siteName);
			},{icon: 1, time:2000});
		},'json');
		return;
	}

	var body = '<div id="proxy_list" class="bt_table">\
					<div style="padding-bottom: 10px">\
						<button type="button" title="添加反向代理" class="btn btn-success btn-sm mr5" onclick="toProxy(\''+siteName+'\',1)" >\
							<span>添加反向代理</span>\
						</button>\
					</div>\
					<div class="divtable" style="max-height:200px;">\
						<table class="table table-hover" >\
							<thead style="position: relative;z-index: 1;">\
								<tr>\
									<th>名称</th>\
									<th>代理目录</th>\
									<th>目标地址</th>\
									<th>缓存</th>\
									<th>状态</th>\
									<th>操作</th>\
								</tr>\
							</thead>\
							<tbody id="md-301-body"></tbody>\
						</table>\
					</div>\
				</div>';
	$("#webedit-con").html(body);
	
	var loading = layer.msg(lan.site.the_msg,{icon:16,time:0,shade: [0.3, '#000']});
	$.post("/site/get_proxy_list", {siteName: siteName},function (res) {
		layer.close(loading);
		if (!res.status){
			layer.msg(res.msg, {icon:2});
			return;
		}
	
		var data = res.data.result;
		for (var i = 0; i < data.length; i++) {
			var item = data[i];
		
			var switchProxy  = '<span onclick="toProxy(\''+siteName+'\', 10, \''+ item.id +'\')" style="color:rgb(92, 184, 92);" class="btlink glyphicon glyphicon-play"></span>';
			if (!item['status']){
				switchProxy = '<span onclick="toProxy(\''+siteName+'\', 11, \''+ item.id +'\')" style="color:rgb(255, 0, 0);" class="btlink glyphicon glyphicon-pause"></span>';
			}

			var openCache = '<span  data-index="'+i+'" class="btlink cache off">未开启</span>';
			if (item['open_cache'] == 'on'){
				openCache = '<span  data-index="'+i+'" class="btlink cache on">已开启</span>';
			}

			let tmp = '<tr>\
				<td>'+item.name+'</td>\
				<td>'+item.from+'</td>\
				<td>'+item.to+'</td>\
				<td>'+openCache+'</td>\
				<td>'+switchProxy+'</td>\
				<td>\
				   <span data-index="'+i+'" class="btlink detail">详细</span> |\
				   <span data-index="'+i+'" class="btlink edit">编辑</span> |\
				   <span data-index="'+i+'" class="btlink delete">删除</span>\
				</td>\
			</tr>';
			$("#md-301-body").append(tmp);
		}

		$('#md-301-body .detail').click(function(){
			var index = $(this).data('index');
			toProxy(siteName, 3 ,data[index]['id']);
		});

		$('#md-301-body .edit').click(function(){
			var index = $(this).data('index');
			toProxy(siteName, 1 ,data[index]);
		});

		$('#md-301-body .delete').click(function(){
			var index = $(this).data('index');
			toProxy(siteName, 2 ,data[index]['id']);
		});

		$('#md-301-body .cache').click(function(){
			var index = $(this).data('index');
			if ($(this).hasClass('on')){
				toProxy(siteName, 21 ,data[index]);
			} else{
				toProxy(siteName, 20 ,data[index]);
			}
		});
		
	},'json');
/////////
}

//证书夹
function sslAdmin(siteName){
	var loadT = layer.msg('正在提交任务...',{icon:16,time:0,shade: [0.3, '#000']});
	$.get('/site/get_cert_list',function(data){
		layer.close(loadT);
		var rdata = data['data'];
		var tbody = '';
		for(var i=0;i<rdata.length;i++){
			tbody += '<tr>\
				<td>'+rdata[i].subject+'</td>\
				<td>'+rdata[i].dns.join('<br>')+'</td>\
				<td>'+rdata[i].notAfter+'</td>\
				<td>'+rdata[i].issuer.split(' ')[0]+'</td>\
				<td style="text-align: right;"><a onclick="setCertSsl(\''+rdata[i].subject+'\',\''+siteName+'\')" class="btlink">部署</a> | <a onclick="removeSsl(\''+rdata[i].subject+'\')" class="btlink">删除</a></td>\
			</tr>'
		}
		var txt = '<div class="mtb15" style="line-height:30px">\
		<button style="margin-bottom: 7px;display:none;" class="btn btn-success btn-sm">添加</button>\
		<div class="divtable"><table class="table table-hover"><thead><tr><th>域名</th><th>信任名称</th><th>到期时间</th><th>品牌</th><th class="text-right" width="75">操作</th></tr></thead>\
		<tbody>'+tbody+'</tbody>\
		</table></div></div>';
		$(".tab-con").html(txt);
	},'json');
}

//删除证书
function removeSsl(certName){
	safeMessage('删除证书','您真的要从证书夹删除证书吗?',function(){
		var loadT = layer.msg(lan.site.the_msg,{icon:16,time:0,shade: [0.3, '#000']});
		$.post('/site/remove_cert',{certName:certName},function(rdata){
			layer.close(loadT);
			layer.msg(rdata.msg,{icon:rdata.status?1:2});
			$("#ssl_admin").click();
		},'json');
	});
}

//从证书夹部署
function setCertSsl(certName,siteName){
	var loadT = layer.msg('正在部署证书...',{icon:16,time:0,shade: [0.3, '#000']});
	$.post('/site/set_cert_to_site',{certName:certName,siteName:siteName},function(rdata){
		layer.close(loadT);
		showMsg(rdata.msg, function(){
			$(".tab-nav span:first-child").click();
		},{icon:rdata.status?1:2},2000);
	},'json');
}

//ssl
function setSSL(id,siteName){
	var sslHtml = '<div class="warning_info mb10" style="display:none;"><p class="">温馨提示：当前站点未开启SSL证书访问，站点访问可能存在风险。<button class="btn btn-success btn-xs ml10 cutTabView">申请证书</button></p></div>\
				<div class="tab-nav" style="margin-top: 10px;">\
					<span class="on" id="now_ssl" onclick="opSSL(\'now\','+id+',\''+siteName+'\')">当前证书 - <i class="error">[未部署SSL]</i></span>\
					<span onclick="opSSL(\'lets\','+id+',\''+siteName+'\')">Let\'s Encrypt</span>\
					<span onclick="opSSL(\'acme\','+id+',\''+siteName+'\')">ACME</span>\
					<span id="ssl_admin" onclick="sslAdmin(\''+siteName+'\')">证书夹</span>'
					+ '<div class="ss-text pull-right mr30" style="position: relative;top:-4px">\
	                </div></div>'
			  + '<div class="tab-con" style="padding: 0px;"></div>';
	$("#webedit-con").html(sslHtml);
	$(".tab-nav span").click(function(){
		$(this).addClass("on").siblings().removeClass("on");
	});
	opSSL('now',id,siteName);
}

//设置httpToHttps
function httpToHttps(siteName){
	var isHttps = $("#toHttps").prop('checked');
	if(isHttps){
		layer.confirm('关闭强制HTTPS后需要清空浏览器缓存才能看到效果,继续吗?',{icon:3,title:"关闭强制HTTPS"},function(){
			$.post('/site/close_to_https','siteName='+siteName,function(rdata){
				layer.msg(rdata.msg,{icon:rdata.status?1:2});
			},'json');
		});
	}else{
		$.post('/site/http_to_https','siteName='+siteName,function(rdata){
			layer.msg(rdata.msg,{icon:rdata.status?1:2});
		},'json');
	}
}


function deleteSSL(type,id,siteName){
	$.post('/site/delete_ssl','site_name='+siteName+'&ssl_type='+type,function(rdata){
		showMsg(rdata.msg, function(){
			opSSL(type,id,siteName);
		},{icon:rdata.status?1:2}, 2000);
	},'json');
}

function deploySSL(type,id,siteName){
	$.post('/site/deploy_ssl','site_name='+siteName+'&ssl_type='+type,function(rdata){
		showMsg(rdata.msg, function(){
			if (rdata.status){
				$('#now_ssl').click();
			} else{
				opSSL(type,id,siteName);
			}
		},{icon:rdata.status?1:2}, 2000);
	},'json');
}

function renewSSL(type,id,siteName){
	showSpeedWindow('正在续签...', 'site.get_let_logs', function(layers,index){
		$.post('/site/renew_ssl','site_name='+siteName+'&ssl_type='+type,function(rdata){
			showMsg(rdata.msg, function(){
				if (rdata.status){
					layer.close(index);
					opSSL(type,id,siteName);
				}
			},{icon:rdata.status?1:2}, 2000);
		},'json');
	});	
}

//SSL
function opSSL(type, id, siteName, callback){

	var now = '<div class="myKeyCon ptb15">\
	 				<div class="ssl_state_info" style="display:none;"></div>\
					<div class="custom_certificate_info">\
						<div class="ssl-con-key pull-left mr20">密钥(KEY)<br><textarea id="key" class="bt-input-text"></textarea></div>\
						<div class="ssl-con-key pull-left">证书(PEM格式)<br><textarea id="csr" class="bt-input-text"></textarea></div>\
					</div>\
					<div class="ssl-btn pull-left mtb15" style="width:100%">\
						<button class="btn btn-success btn-sm" onclick="saveSSL(\''+siteName+'\')">保存</button>\
					</div>\
				</div>\
				<ul class="help-info-text c7 pull-left">\
					<li>粘贴您的*.key以及*.pem内容，然后保存即可。</li>\
					<li>如果浏览器提示证书链不完整,请检查是否正确拼接PEM证书</li><li>PEM格式证书 = 域名证书.crt + 根证书(root_bundle).crt</li>\
					<li>在未指定SSL默认站点时,未开启SSL的站点使用HTTPS会直接访问到已开启SSL的站点</li>\
				</ul>';	

	var lets =  '<div class="apply_ssl">\
					<div class="label-input-group">\
						<div class="line mtb10">\
							<form>\
								<span class="tname text-center">验证方式</span>\
								<div style="margin-top:7px;display:inline-block">\
									<input type="radio" name="c_type" onclick="file_check()" id="check_file" checked="checked" />\
				  					<label class="mr20" for="check_file" style="font-weight:normal">文件验证</label></label>\
				  				</div>\
				  			</form>\
				  		</div>\
			  			<div class="check_message line">\
			  				<div style="margin-left:100px">\
			  					<input type="checkbox" name="checkDomain" id="checkDomain" checked="">\
			  					<label class="mr20" for="checkDomain" style="font-weight:normal">提前校验域名(提前发现问题,减少失败率)</label>\
			  				</div>\
			  			</div>\
			  		</div>\
			  		<div class="line mtb10">\
			  			<span class="tname text-center">管理员邮箱</span>\
			  			<input class="bt-input-text" style="width:240px;" type="text" name="admin_email" />\
			  		</div>\
			  		<div class="line mtb10">\
			  			<span class="tname text-center">域名</span>\
			  			<ul id="ymlist" style="padding: 5px 10px;max-height:180px;overflow:auto; width:240px;border:#ccc 1px solid;border-radius:3px"></ul>\
			  		</div>\
			  		<div class="line mtb10" style="margin-left:100px">\
			  			<button class="btn btn-success btn-sm letsApply">申请</button>\
			  		</div>\
				  	<ul class="help-info-text c7" id="lets_help">\
				  		<li>申请之前，请确保域名已解析，如未解析会导致审核失败</li>\
				  		<li>Let\'s Encrypt免费证书，有效期3个月，支持多域名。默认会自动续签</li>\
				  		<li>若您的站点使用了CDN或301重定向会导致续签失败</li>\
				  		<li>在未指定SSL默认站点时,未开启SSL的站点使用HTTPS会直接访问到已开启SSL的站点</li>\
				  	</ul>\
			  </div>';

	var acme =  '<div class="apply_ssl">\
					<div class="label-input-group">\
						<div class="line mtb10">\
							<form>\
								<span class="tname text-center">验证方式</span>\
								<div style="margin-top:7px;display:inline-block">\
									<input type="radio" name="c_type" onclick="file_check()" id="check_file" checked="checked" />\
				  					<label class="mr20" for="check_file" style="font-weight:normal">文件验证</label></label>\
				  				</div>\
				  			</form>\
				  		</div>\
			  			<div class="check_message line">\
			  				<div style="margin-left:100px">\
			  					<input type="checkbox" name="checkDomain" id="checkDomain" checked="">\
			  					<label class="mr20" for="checkDomain" style="font-weight:normal">提前校验域名(提前发现问题,减少失败率)</label>\
			  				</div>\
			  			</div>\
			  		</div>\
			  		<div class="line mtb10">\
			  			<span class="tname text-center">管理员邮箱</span>\
			  			<input class="bt-input-text" style="width:240px;" type="text" name="admin_email" />\
			  		</div>\
			  		<div class="line mtb10">\
			  			<span class="tname text-center">域名</span>\
			  			<ul id="ymlist" style="padding: 5px 10px;max-height:180px;overflow:auto; width:240px;border:#ccc 1px solid;border-radius:3px"></ul>\
			  		</div>\
			  		<div class="line mtb10" style="margin-left:100px">\
			  			<button class="btn btn-success btn-sm letsApply">申请</button>\
			  		</div>\
				  	<ul class="help-info-text c7" id="lets_help">\
				  		<li>申请之前，请确保域名已解析，如未解析会导致审核失败</li>\
			  			<li>由ACME免费申请证书，有效期3个月，支持多域名。默认会自动续签</li>\
			  			<li>若您的站点使用了CDN或301重定向会导致续签失败</li>\
			  			<li>在未指定SSL默认站点时,未开启SSL的站点使用HTTPS会直接访问到已开启SSL的站点</li></ul>\
				  	</ul>\
			  </div>';

			
	switch(type){
		case 'lets':
			$(".tab-con").html(lets);
			$.post('/site/get_ssl',  'site_name='+siteName+'&ssl_type=lets', function(data){
				var rdata = data['data'];
				if(rdata.csr == false){
					$.post('/site/get_site_domains','id='+id, function(rdata) {
						var data = rdata['data'];
						var opt='';
						for(var i=0;i<data.domains.length;i++){
							var isIP = isValidIP(data.domains[i].name);
							var x = isContains(data.domains[i].name, '*');
							if(!isIP && !x){
								opt+='<li style="line-height:26px"><input type="checkbox" style="margin-right:5px; vertical-align:-2px" value="'+data.domains[i].name+'">'+data.domains[i].name+'</li>'
							}
						}
						$("input[name='admin_email']").val(data.email);
						$("#ymlist").html(opt);
						$("#ymlist li input").click(function(e){
							e.stopPropagation();
						})
						$("#ymlist li").click(function(){
							var o = $(this).find("input");
							if(o.prop("checked")){
								o.prop("checked",false)
							}
							else{
								o.prop("checked",true);
							}
						})
						$(".letsApply").click(function(){
							var c = $("#ymlist input[type='checkbox']");
							var str = [];
							var domains = '';
							for(var i=0; i<c.length; i++){
								if(c[i].checked){
									str.push(c[i].value);
								}
							}
							domains = JSON.stringify(str);
							newSSL(siteName, id, domains);
						});

						if (typeof (callback) != 'undefined'){
							callback(rdata);
						}
					},'json');
					return;
				}
				var lets = '<div class="myKeyCon ptb15">\
						<div class="ssl_state_info" style="display:none;"></div>\
						<div class="custom_certificate_info">\
							<div class="ssl-con-key pull-left mr20" readonly>密钥(KEY)<br><textarea id="key" class="bt-input-text">'+rdata.key+'</textarea></div>\
							<div class="ssl-con-key pull-left" readonly>证书(PEM格式)<br><textarea id="csr" class="bt-input-text">'+rdata.csr+'</textarea></div>\
						</div>\
						<div class="ssl-btn pull-left mtb15" style="width:100%">\
							<button class="btn btn-success btn-sm" onclick="deploySSL(\'lets\','+id+',\''+siteName+'\')">部署</button>\
							<button class="btn btn-success btn-sm" onclick="renewSSL(\'lets\','+id+',\''+siteName+'\')">续期</button>\
							<button class="btn btn-success btn-sm" onclick="deleteSSL(\'lets\','+id+',\''+siteName+'\')">删除</button>\
						</div>\
					</div>\
					<ul class="help-info-text c7 pull-left">\
						<li>已为您自动生成Let\'s Encrypt免费证书</li>\
						<li>由Let\'s Encrypt免费申请证书，有效期3个月，支持多域名。默认会自动续签</li>\
						<li>如需使用其他SSL,请切换其他证书后粘贴您的KEY以及PEM内容，然后保存即可。</li>\
					</ul>';
				$(".tab-con").html(lets);

				if (rdata['cert_data']){
					var issuer = rdata['cert_data']['issuer'].split(" ");
					var domains = rdata['cert_data']['dns'].join("、");

					var cert_data = "<div class='state_info_flex'>\
						<div class='state_item'><span>证书品牌：</span><span class='ellipsis_text'>"+issuer[0]+"</span></div>\
						<div class='state_item'><span>到期时间：</span><span class='btlink'>剩余"+rdata['cert_data']['endtime']+"天到期</span></div>\
					</div>\
					<div class='state_info_flex'>\
						<div class='state_item'><span>认证域名：</span><span class='ellipsis_text'>"+domains+"</span></div>\
					</div>";
					$(".ssl_state_info").html(cert_data);
					$(".ssl_state_info").css('display','block');
				}
			},'json');			
			break;
		case 'acme':
			$(".tab-con").html(acme);
			$.post('/site/get_ssl',  'site_name='+siteName+'&ssl_type=acme', function(data){
				var rdata = data['data'];
				if(rdata.csr == false){
					$.post('/site/get_site_domains','id='+id, function(rdata) {
						var data = rdata['data'];
						var opt='';
						for(var i=0;i<data.domains.length;i++){
							var isIP = isValidIP(data.domains[i].name);
							var x = isContains(data.domains[i].name, '*');
							if(!isIP && !x){
								opt += '<li style="line-height:26px">\
									<input type="checkbox" style="margin-right:5px; vertical-align:-2px" value="'+data.domains[i].name+'">'+data.domains[i].name
								+'</li>';
							}
						}
						$("input[name='admin_email']").val(data.email);
						$("#ymlist").html(opt);
						$("#ymlist li input").click(function(e){
							e.stopPropagation();
						})
						$("#ymlist li").click(function(){
							var o = $(this).find("input");
							if(o.prop("checked")){
								o.prop("checked",false)
							}
							else{
								o.prop("checked",true);
							}
						})
						$(".letsApply").click(function(){
							var c = $("#ymlist input[type='checkbox']");
							var str = [];
							var domains = '';
							for(var i=0; i<c.length; i++){
								if(c[i].checked){
									str.push(c[i].value);
								}
							}
							domains = JSON.stringify(str);
							newAcmeSSL(siteName, id, domains);
						});

						if (typeof (callback) != 'undefined'){
							callback(rdata);
						}
					},'json');
					return;
				}
				var acme = '<div class="myKeyCon ptb15">\
						<div class="ssl_state_info" style="display:none;"></div>\
						<div class="custom_certificate_info">\
							<div class="ssl-con-key pull-left mr20" readonly>密钥(KEY)<br><textarea id="key" class="bt-input-text">'+rdata.key+'</textarea></div>\
							<div class="ssl-con-key pull-left" readonly>证书(PEM格式)<br><textarea id="csr" class="bt-input-text">'+rdata.csr+'</textarea></div>\
						</div>\
						<div class="ssl-btn pull-left mtb15" style="width:100%">\
							<button class="btn btn-success btn-sm" onclick="deploySSL(\'acme\','+id+',\''+siteName+'\')">部署</button>\
							<button class="btn btn-success btn-sm" onclick="deleteSSL(\'acme\','+id+',\''+siteName+'\')">删除</button>\
						</div>\
					</div>\
					<ul class="help-info-text c7 pull-left">\
						<li>已为您自动生成ACME免费证书</li>\
						<li>由ACME免费申请证书，有效期3个月，支持多域名。默认会自动续签</li>\
						<li>如需使用其他SSL,请切换其他证书后粘贴您的KEY以及PEM内容，然后保存即可。</li>\
					</ul>';
				$(".tab-con").html(acme);

				if (rdata['cert_data']){
					var issuer = rdata['cert_data']['issuer'].split(" ");
					var domains = rdata['cert_data']['dns'].join("、");

					var cert_data = "<div class='state_info_flex'>\
						<div class='state_item'><span>证书品牌：</span><span class='ellipsis_text'>"+issuer[0]+"</span></div>\
						<div class='state_item'><span>到期时间：</span><span class='btlink'>剩余"+rdata['cert_data']['endtime']+"天到期</span></div>\
					</div>\
					<div class='state_info_flex'>\
						<div class='state_item'><span>认证域名：</span><span class='ellipsis_text'>"+domains+"</span></div>\
					</div>";
					$(".ssl_state_info").html(cert_data);
					$(".ssl_state_info").css('display','block');
				}
			},'json');			
			break;
		case 'now':
			$(".tab-con").html(now);
			var key = '';
			var csr = '';
			var loadT = layer.msg('正在提交任务...',{icon:16,time:0,shade: [0.3, '#000']});
			$.post('site/get_ssl','site_name='+siteName,function(data){
				layer.close(loadT);
				var rdata = data['data'];

				if (rdata['cert_data']){
					var issuer = rdata['cert_data']['issuer'].split(" ");
					var domains = rdata['cert_data']['dns'].join("、");

					var cert_data = "<div class='state_info_flex'>\
						<div class='state_item'><span>证书品牌：</span><span class='ellipsis_text'>"+issuer[0]+"</span></div>\
						<div class='state_item'><span>到期时间：</span><span class='btlink'>剩余"+rdata['cert_data']['endtime']+"天到期</span></div>\
					</div>\
					<div class='state_info_flex'>\
						<div class='state_item'><span>认证域名：</span><span class='ellipsis_text'>"+domains+"</span></div>\
						<div class='state_item'><span>强制HTTPS：</span><span class='switch'>\
							<input class='btswitch btswitch-ios' id='toHttps' type='checkbox'>\
		                    <label class='btswitch-btn' for='toHttps' onclick=\"httpToHttps('" + siteName + "')\">\
						</span></div>\
					</div>";
					$(".ssl_state_info").html(cert_data);
					$(".ssl_state_info").css('display','block');
				}

				if(rdata.key == false){
					rdata.key = '';
				} else {
					$(".ssl-btn").append('<button style=\'margin-left:3px;\' class="btn btn-success btn-sm" onclick="deleteSSL(\'now\','+id+',\''+siteName+'\')">删除</button>');
				}

				if(rdata.csr == false){
					rdata.csr = '';
				}
				$("#key").val(rdata.key);
				$("#csr").val(rdata.csr);

				$("#toHttps").attr('checked',rdata.httpTohttps);
				if(rdata.status){
					$('.warning_info').css('display','none');
					
					$(".ssl-btn").append("<button class='btn btn-success btn-sm' onclick=\"ocSSL('close_ssl_conf','"+siteName+"')\" style='margin-left:3px;'>关闭SSL</button>");
					$('#now_ssl').html('当前证书 - <i style="color:#20a53a;">[已部署SSL]</i>');
				} else{
					$('.warning_info').css('display','block');
					$('#now_ssl').html('当前证书 - <i style="color:red;">[未部署SSL]</i>');
				}


				if (typeof (callback) != 'undefined'){
					callback(rdata);
				}
			},'json');
			break;
		default:
			layer.msg("错误类型", {icon:5});
			break;
	}
}


//开启与关闭SSL
function ocSSL(action,siteName){
	var loadT = layer.msg('正在获取证书列表，请稍后..',{icon:16,time:0,shade: [0.3, '#000']});
	$.post("/site/"+action,'siteName='+siteName+'&updateOf=1',function(rdata){
		layer.close(loadT)
		
		if(!rdata.status){
			if(!rdata.out){
				layer.msg(rdata.msg,{icon:rdata.status?1:2});
				setSSL(siteName);
				return;
			}
			data = "<p>证书获取失败：</p><hr />"
			for(var i=0;i<rdata.out.length;i++){
				data += "<p>域名: "+rdata.out[i].Domain+"</p>"
					  + "<p>错误类型: "+rdata.out[i].Type+"</p>"
					  + "<p>详情: "+rdata.out[i].Detail+"</p>"
					  + "<hr />";
			}
			layer.msg(data,{icon:2,time:0,shade:0.3,shadeClose:true});
			return;
		}
		layer.msg(rdata.msg,{icon:rdata.status?1:2});
		if(action == 'close_ssl_conf'){
			layer.msg('已关闭SSL,请务必清除浏览器缓存后再访问站点!',{icon:1,time:5000});
		}
		$(".tab-nav .on").click();
	},'json');
}

//生成SSL
function newSSL(siteName, id, domains){
	showSpeedWindow('正在申请...', 'site.get_let_logs', function(layers,index){
		var force = '';
		if ($("#checkDomain").prop("checked")){
			force = '&force=true';
		}
		var email = $("input[name='admin_email']").val();
		$.post('/site/create_let','siteName='+siteName+'&domains='+domains+'&email='+email + force,function(rdata){
			layer.close(index);
			if(rdata.status){
				showMsg(rdata.msg, function(){
					$(".tab-nav span:first-child").click();
				},{icon:1}, 2000);
				return;
			}
			layer.msg(rdata.msg,{icon:2,area:'500px',time:0,shade:0.3,shadeClose:true});
		},'json');
	});
}

function newAcmeSSL(siteName, id, domains){
	showSpeedWindow('正在由ACME申请...', 'site.get_acme_logs', function(layers,index){
		var force = '';
		if($("#checkDomain").prop("checked")){
			force = '&force=true';
		}
		var email = $("input[name='admin_email']").val();
		$.post('/site/create_acme','siteName='+siteName+'&domains='+domains+'&email='+email + force,function(rdata){
			layer.close(index);
			if(rdata.status){
				showMsg(rdata.msg, function(){
					$(".tab-nav span:first-child").click();
				},{icon:1}, 2000);
				return;
			}
			layer.msg(rdata.msg,{icon:2,area:'500px',time:0,shade:0.3,shadeClose:true});
		},'json');
	});
}

//保存SSL
function saveSSL(siteName){
	var data = 'type=1&siteName='+siteName+'&key='+encodeURIComponent($("#key").val())+'&csr='+encodeURIComponent($("#csr").val());
	var loadT = layer.msg(lan.site.saving_txt,{icon:16,time:20000,shade: [0.3, '#000']})
	$.post('/site/set_ssl',data,function(rdata){
		layer.close(loadT);
		if(rdata.status){
			layer.msg(rdata.msg,{icon:1});
			$(".ssl-btn").find(".btn-default").remove();
			$(".ssl-btn").append("<button class='btn btn-default btn-sm' onclick=\"ocSSL('close_ssl_conf','"+siteName+"')\" style='margin-left:10px'>"+lan.site.ssl_close+"</button>");
		} else {
			layer.msg(rdata.msg,{icon:2,time:0,shade:0.3,shadeClose:true});
		}
	},'json');
}

//PHP版本
function phpVersion(siteName){
	$.post('/site/get_site_php_version','siteName='+siteName,function(version){
		// console.log(version);
		if(version.status === false){
			layer.msg(version.msg,{icon:5});
			return;
		}
		$.post('/site/get_php_version',function(rdata){
			var versionSelect = "<div class='webEdit-box'>\
									<div class='line'>\
										<span class='tname' style='width:100px'>PHP版本</span>\
										<div class='info-r'>\
											<select id='phpVersion' class='bt-input-text mr5' name='phpVersion' style='width:110px'>";
			var optionSelect = '';
			for(var i=0;i<rdata.length;i++){
				optionSelect = version.phpversion == rdata[i].version?'selected':'';
				versionSelect += "<option value='"+ rdata[i].version +"' "+ optionSelect +">"+ rdata[i].name +"</option>"
			}
			versionSelect += "</select>\
							<button class='btn btn-success btn-sm' onclick=\"setPHPVersion('"+siteName+"')\">"+lan.site.switch+"</button>\
							</div>\
							<span id='php_w' style='color:red;margin-left: 32px;'></span>\
						</div>\
							<ul class='help-info-text c7 ptb10'>\
								<li>请根据您的程序需求选择版本</li>\
								<li>若非必要,请尽量不要使用PHP5.2,这会降低您的服务器安全性；</li>\
								<li>PHP7不支持mysql扩展，默认安装mysqli以及mysql-pdo。</li>\
							</ul>\
						</div>\
					</div>";
			$("#webedit-con").html(versionSelect);
			//验证PHP版本
			$("select[name='phpVersion']").change(function(){
				if($(this).val() == '52'){
					var msgerr = 'PHP5.2在您的站点有漏洞时有跨站风险，请尽量使用PHP5.3以上版本!';
					$('#php_w').text(msgerr);
				}else{
					$('#php_w').text('');
				}
			})
		},'json');
	},'json');
}


//设置PHP版本
function setPHPVersion(siteName){
	var data = 'version='+$("#phpVersion").val()+'&siteName='+siteName;
	var loadT = layer.msg('正在保存...',{icon:16,time:0,shade: [0.3, '#000']});
	$.post('/site/set_php_version',data,function(rdata){
		layer.close(loadT);
		layer.msg(rdata.msg,{icon:rdata.status?1:2});
	},'json');
}

//配置文件
function configFile(webSite){
	var info = syncPost('/site/get_host_conf', {siteName:webSite});
	$.post('/files/get_body','path='+info['host'],function(rdata){
		var mBody = "<div class='webEdit-box padding-10'>\
		<textarea style='height: 320px; width: 445px; margin-left: 20px;line-height:18px' id='configBody'>"+rdata.data.data+"</textarea>\
			<div class='info-r'>\
				<button id='SaveConfigFileBtn' class='btn btn-success btn-sm' style='margin-top:15px;'>保存</button>\
				<ul class='help-info-text c7 ptb10'>\
					<li>此处为站点主配置文件,若您不了解配置规则,请勿随意修改.</li>\
				</ul>\
			</div>\
		</div>";
		$("#webedit-con").html(mBody);
		var editor = CodeMirror.fromTextArea(document.getElementById("configBody"), {
			extraKeys: {"Ctrl-Space": "autocomplete"},
			lineNumbers: true,
			matchBrackets:true,
		});
		$(".CodeMirror-scroll").css({"height":"300px","margin":0,"padding":0});
		$("#SaveConfigFileBtn").click(function(){
			$("#configBody").empty();
			$("#configBody").text(editor.getValue());
			saveConfigFile(webSite,rdata.data.encoding, info['host']);
		})
	},'json');
}

//保存配置文件
function saveConfigFile(webSite,encoding,path){
	var data = 'encoding='+encoding+'&data='+encodeURIComponent($("#configBody").val())+'&path='+path;
	var loadT = layer.msg('保存中...',{icon:16,time:0,shade: [0.3, '#000']});
	$.post('/site/save_host_conf',data,function(rdata){
		layer.close(loadT);
		if(rdata.status){
			layer.msg(rdata.msg,{icon:1});
		}else{
			layer.msg(rdata.msg,{icon:2,time:0,shade:0.3,shadeClose:true});
		}
	},'json');
}

//伪静态
function rewrite(siteName){
	$.post("/site/get_rewrite_list", 'siteName='+siteName,function(rdata){
		var info = syncPost('/site/get_rewrite_conf', {siteName:siteName});
		var filename = info['rewrite'];
		$.post('/files/get_body','path='+filename,function(fileBody){
			var centent = fileBody['data']['data'];
			var rList = ''; 
			for(var i=0;i<rdata.rewrite.length;i++){
				if (i==0){
					rList += "<option value='0'>"+rdata.rewrite[i]+"</option>";	
				} else {
					rList += "<option value='"+rdata.rewrite[i]+"'>"+rdata.rewrite[i]+"</option>";		
				}
			}
			var webBakHtml = "<div class='bt-form'>\
						<div class='line'>\
						<select id='myRewrite' class='bt-input-text mr20' name='rewrite' style='width:30%;'>"+rList+"</select>\
						<textarea class='bt-input-text' style='height: 260px; width: 480px; line-height:18px;margin-top:10px;padding:5px;' id='rewriteBody'>"+centent+"</textarea></div>\
						<button id='SetRewriteBtn' class='btn btn-success btn-sm'>保存</button>\
						<button id='SetRewriteBtnTel' class='btn btn-success btn-sm'>另存为模板</button>\
						<ul class='help-info-text c7 ptb15'>\
							<li>请选择您的应用，若设置伪静态后，网站无法正常访问，请尝试设置回default</li>\
							<li>您可以对伪静态规则进行修改，修改完后保存即可。</li>\
						</ul>\
						</div>";
			$("#webedit-con").html(webBakHtml);
			
			var editor = CodeMirror.fromTextArea(document.getElementById("rewriteBody"), {
	            extraKeys: {"Ctrl-Space": "autocomplete"},
				lineNumbers: true,
				matchBrackets:true,
			});
			
			$(".CodeMirror-scroll").css({"height":"300px","margin":0,"padding":0});
			$("#SetRewriteBtn").click(function(){
				$("#rewriteBody").empty();
				$("#rewriteBody").text(editor.getValue());
				setRewrite(filename, encodeURIComponent(editor.getValue()));
			});
			$("#SetRewriteBtnTel").click(function(){
				$("#rewriteBody").empty();
				$("#rewriteBody").text(editor.getValue());
				setRewriteTel();
			});
			
			$("#myRewrite").change(function(){
				var rewriteName = $(this).val();
				if(rewriteName == '0'){
					rpath = filename;
				}else{
					var info = syncPost('/site/get_rewrite_tpl', {tplname:rewriteName});
					if (!info['status']){
						layer.msg(info['msg']);
						return;
					}
					rpath = info['data'];
				}
				
				$.post('/files/get_body','path='+rpath,function(fileBody){
					$("#rewriteBody").val(fileBody['data']['data']);
					editor.setValue(fileBody['data']['data']);
				},'json');
			});
		},'json');
	},'json');
}


//设置伪静态
function setRewrite(filename,data){
	var data = 'data='+data+'&path='+filename+'&encoding=utf-8';
	var loadT = layer.msg(lan.site.saving_txt,{icon:16,time:0,shade: [0.3, '#000']});
	$.post('/site/set_rewrite',data,function(rdata){
		layer.close(loadT);
		if(rdata.status){
			layer.msg(rdata.msg,{icon:1});
		}else{
			layer.msg(rdata.msg,{icon:2,time:0,shade:0.3,shadeClose:true});
		}
	},'json');
}
var aindex = null;

//保存为模板
function setRewriteTel(act){	
	aindex = layer.open({
		type: 1,
		shift: 5,
		closeBtn: 1,
		area: '320px', //宽高
		title: '保存为Rewrite模板',
		btn:[lan.public.ok,lan.public.cancel],
		content: '<div class="bt-form pd20">\
					<div class="line">\
						<input type="text" class="bt-input-text" name="rewriteName" id="rewriteName" value="" placeholder="'+lan.site.template_name+'" style="width:100%" />\
					</div>\
				</div>',
		success:function(index){
			$("#rewriteName").focus().keyup(function(e){
				if(e.keyCode == 13) $("#rewriteNameBtn").click();
			});
		},
		yes:function(index){
			name = $("#rewriteName").val();
			if(name == ''){
				layer.msg(lan.site.template_empty,{icon:5});
				return;
			}
			var data = 'data='+encodeURIComponent($("#rewriteBody").val())+'&name='+name;
			var loadT = layer.msg(lan.site.saving_txt,{icon:16,time:0,shade: [0.3, '#000']});
			$.post('/site/set_rewrite_tpl',data,function(rdata){
				layer.close(loadT);
				layer.close(index);
				layer.msg(rdata.msg, {icon:rdata.status?1:5});
			},'json');
			return;
		}
	});
}
//修改默认页
function siteDefaultPage(){
	stype = getCookie('serverType');
	layer.open({
		type: 1,
		area: '460px',
		title: '修改默认页',
		closeBtn: 1,
		shift: 0,
		content: '<div class="changeDefault pd20">\
						<button class="btn btn-default btn-sm mg10" style="width:188px" onclick="changeDefault(1)">默认文档</button>\
						<button class="btn btn-default btn-sm mg10" style="width:188px" onclick="changeDefault(2)">404错误页</button>\
						<button class="btn btn-default btn-sm mg10" style="width:188px" onclick="changeDefault(3)">空白页</button>\
						<button class="btn btn-default btn-sm mg10" style="width:188px" onclick="changeDefault(4)">默认站点停止页</button>\
				</div>'
	});
}

function changeDefault(type){
	$.post('/site/get_site_doc','type='+type, function(rdata){
		showMsg('操作成功!',function(){
			if (rdata.status){
				vhref = rdata.data.path;
				onlineEditFile(0,vhref);
			}
		},{icon:rdata.status?1:2});
	},'json');
}

function getClassType(){
	var select = $('.site_type > select');
	$.post('/site/get_site_types',function(rdata){
		$(select).html('');
		$(select).append('<option value="-1">全部分类</option>');
		for (var i = 0; i<rdata.length; i++) {
			$(select).append('<option value="'+rdata[i]['id']+'">'+rdata[i]['name']+'</option>');
		}

		$(select).bind('change',function(){
			var select_id = $(this).val();
			getWeb(1,select_id, '');
		})
	},'json');
}
getClassType();

function setClassType(){
	$.post('/site/get_site_types',function(rdata){
		var list = '';
		for (var i = 0; i<rdata.length; i++) {
			list +='<tr><td>' + rdata[i]['name'] + '</td>\
				<td><a class="btlink edit_type" onclick="editClassType(\''+rdata[i]['id']+'\',\''+rdata[i]['name']+'\')">编辑</a> | <a class="btlink del_type" onclick="removeClassType(\''+rdata[i]['id']+'\',\''+rdata[i]['name']+'\')">删除</a>\
				</td></tr>';
		}

		layer.open({
			type: 1,
			area: '350px',
			title: '网站分类管理',
			closeBtn: 1,
			shift: 0,
			content: '<div class="bt-form edit_site_type">\
					<div class="divtable mtb15" style="overflow:auto">\
						<div class="line "><div class="info-r  ml0">\
							<input name="type_name" class="bt-input-text mr5 type_name" placeholder="请填写分类名称" type="text" style="width:50%" value=""><button name="btn_submit" class="btn btn-success btn-sm mr5 ml5 btn_submit" onclick="addClassType();">添加</button></div>\
						</div>\
						<table id="type_table" class="table table-hover" width="100%">\
							<thead><tr><th>名称</th><th width="80px">操作</th></tr></thead>\
							<tbody>'+list+'</tbody>\
						</table>\
					</div>\
				</div>'
		});
	},'json');
}

function addClassType(){
	var name = $("input[name=type_name]").val();
	$.post('/site/add_site_type','name='+name, function(rdata){
		showMsg(rdata.msg,function(){
			if (rdata.status){
				layer.closeAll();
				setClassType();
				getClassType();
			}
		},{icon:rdata.status?1:2});
	},'json');
}

function removeClassType(id,name){
	if (id == 0){
		layer.msg('默认分类不可删除/不可编辑!',{icon:2});
		return;
	}
	layer.confirm('是否确定删除分类？',{title: '删除分类【'+ name +'】' }, function(){
		$.post('/site/remove_site_type','id='+id, function(rdata){
			showMsg(rdata.msg,function(){
				if (rdata.status){
					layer.closeAll();
					setClassType();
					getClassType();
				}
			},{icon:rdata.status?1:2});
		},'json');
	});
}

function editClassType(id,name){
	if (id == 0){
		layer.msg('默认分类不可删除/不可编辑!',{icon:2});
		return;
	}

	layer.open({
		type: 1,
		area: '350px',
		title: '修改分类管理【' + name + '】',
		closeBtn: 1,
		shift: 0,
		content: "<form class='bt-form bt-form pd20 pb70' id='mod_pwd'>\
                    <div class='line'>\
                        <span class='tname'>分类名称</span>\
                        <div class='info-r'><input name=\"site_type_mod\" class='bt-input-text mr5' type='text' value='"+name+"' /></div>\
                    </div>\
                    <div class='bt-form-submit-btn'>\
                        <button id='site_type_mod' type='button' class='btn btn-success btn-sm btn-title'>提交</button>\
                    </div>\
                  </form>"
	});

	$('#site_type_mod').unbind().click(function(){
		var _name = $('input[name=site_type_mod]').val();
		$.post('/site/modify_site_type_name','id='+id+'&name='+_name, function(rdata){
			showMsg(rdata.msg,function(){
				if (rdata.status){
					layer.closeAll();
					setClassType();
					getClassType();
				}
			},{icon:rdata.status?1:2});
		},'json');

	});
}


function moveClassTYpe(){
	$.post('/site/get_site_types',function(rdata){
		var option = '';
		for (var i = 0; i<rdata.length; i++) {
			option +='<option value="'+rdata[i]['id']+'">'+rdata[i]['name']+'</option>';
		}

		layer.open({
			type: 1,
			area: '350px',
			title: '设置站点分类',
			closeBtn: 1,
			shift: 0,
			content: '<div class="bt-form edit_site_type">\
					<div class="divtable mtb15" style="overflow:auto;height:80px;">\
						<div class="line"><span class="tname">默认站点</span>\
							<div class="info-r">\
							<select class="bt-input-text mr5" name="type_id" style="width:200px">'+option+'\
							</select>\
							</div>\
						</div>\
					</div>\
					<div class="bt-form-submit-btn"><button onclick="setSizeClassType();" type="button" class="btn btn-sm btn-success">提交</button></div>\
				</div>'
		});
	},'json');
}


function setSizeClassType(){
	var data = {};
	data['id'] = $('select[name=type_id]').val();
	var ids = [];
    $('table').find('td').find('input').each(function(i,obj){
        checked = $(this).prop('checked');
        if (checked) {
        	ids.push($(this).val());
        }
    });
	data['site_ids'] = JSON.stringify(ids);
	$.post('/site/set_site_type',data, function(rdata){
		showMsg(rdata.msg,function(){
			if (rdata.status){
				layer.closeAll();
			}
		},{icon:rdata.status?1:2});
	},'json');
}


// 尝试重启PHP
function tryRestartPHP(siteName){
	$.post('/site/get_site_php_version','siteName='+siteName,function(data){
		var phpversion = data.phpversion;

		if (phpversion == "00"){
			return
		}
		
		var php_sign = 'php';
		if (phpversion.indexOf('yum') > -1){
			php_sign = 'php-yum';
			phpversion = phpversion.replace('yum','');
		}

		if (phpversion.indexOf('apt') > -1){
			php_sign = 'php-apt';
			phpversion = phpversion.replace('apt','');
		}

		var reqData = {name: php_sign, func:'restart'}
		reqData['version'] = phpversion;

		// console.log(reqData);
		var loadT = layer.msg('尝试自动重启PHP['+phpversion+']...', { icon: 16, time: 0, shade: 0.3 });
		$.post('/plugins/run', reqData, function(data) {
			layer.close(loadT);
	        layer.msg(data.msg,{icon:data.status?1:2,time:3000,shade: [0.3, '#000']});
	    },'json');
	},'json');
}