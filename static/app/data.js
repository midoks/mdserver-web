/**
 * 取回数据库列表
 * @param {Number} page	页码
 */
function getData(page,search) {
	search = $("#SearchValue").prop("value");
	order = getCookie('order');
	if(order){
		order = '&order=' + order;
	}else{
		order = '';
	}
	var sUrl = '/data?action=getData';
	var sUrlData='tojs=getData&table=databases&limit=15&p='+page+'&search='+search + order;
	var loadT = layer.load();
	$.post(sUrl, sUrlData,function(data) {
		layer.close(loadT);
		//构造数据列表
		var Body = '';
		if(data.data == ""){
			Body="<tr><td colspan='7'>"+lan.database.empty+"</td></tr>";
			$("#DataPage").hide()
		}
		else{
			$("#DataPage").show();
			for (var i = 0; i < data.data.length; i++) {
				if(data.data[i].backup_count==0){
					var isback = "<a href='javascript:;' class='btlink' onclick=\"DataDetails('"+data.data[i].id+"','"+data.data[i].name+"')\">"+lan.database.backup_empty+"</a>"
				}else{
					var isback = "<a href='javascript:;' class='btlink' onclick=\"DataDetails('"+data.data[i].id+"','"+data.data[i].name+"')\">"+lan.database.backup_ok+"</a>"
				}
				Body += "<tr><td><input type='checkbox' title='"+data.data[i].name+"' onclick='checkSelect();' name='id' value='"+data.data[i].id+"'>\
						<td>" + data.data[i].name + "</td>\
						<td>" + data.data[i].username + "</td>\
						<td class='relative'><span class='password' data-pw='"+data.data[i].password+"'>**********</span><span class='glyphicon glyphicon-eye-open cursor pw-ico' style='margin-left:10px'></span><span class='ico-copy cursor btcopy' style='margin-left:10px' title='"+lan.database.copy_pass+"' data-pw='"+data.data[i].password+"' onclick=\"btcopy('"+data.data[i].password+"')\"></span></td>\
						<td>"+isback+" | <a class='btlink' href=\"javascript:InputDatabase('"+data.data[i].name+"');\" title='"+lan.database.input_title+"'>"+lan.database.input+"</a></td>\
						<td><a class='btlinkbed' href='javascript:;' data-id='"+data.data[i].id+"'>" + data.data[i].ps + "</a></td>\
						<td style='text-align:right;'>\
						<a href='javascript:;' class='btlink' onclick=\"AdminDatabase('"+data.data[i].name+"','"+data.data[i].username+"','"+data.data[i].password+"')\" title='"+lan.database.admin_title+"'>"+lan.database.admin+"</a> | \
						<a href='javascript:;' class='btlink' onclick=\"SetDatabaseAccess('"+data.data[i].username+"')\" title='"+lan.database.auth_title+"'>"+lan.database.auth+"</a> | \
						<a href='javascript:;' class='btlink' onclick=\"DataRespwd(0,'"+data.data[i].id+"','"+data.data[i].username+"')\" title='"+lan.database.edit_pass_title+"'>"+lan.database.edit_pass+"</a> | \
						<a href='javascript:;' class='btlink' onclick=\"DataDelete("+data.data[i].id+",'"+data.data[i].name+"')\" title='"+lan.database.del_title+"'>"+lan.public.del+"</a>\
						</td></tr>"
			}
		}
		//输出数据列表
		$("#DataBody").html(Body);
		//输出分页
		$("#DataPage").html(data.page);
		$("#DataPage .Pcount").css("position","static");
		//备注
		$(".btlinkbed").click(function(){
			var dataid = $(this).attr("data-id");
			var databak = $(this).text();
			$(this).hide().after("<input class='baktext' type='text' data-id='"+dataid+"' name='bak' value='" + databak + "' placeholder='"+lan.database.ps+"' onblur='GetBakPost(\"databases\")' />");
			$(".baktext").focus();
		});
		
		showHidePwd();
	});
}

/**
 *添加数据库 
 * @param {Number} sign	操作标识
 * @param {String} name	数据库名
 * @param {String} type	数据库类型
 * @param {Boolean} adduser	是否添加新用户
 * @param {String} bak	备注
 */
function DataAdd(sign){
	if(sign==0){
		var index = layer.open({
		type: 1,
		skin: 'demo-class',
		area: '480px',
		title: lan.database.add_title,
		closeBtn: 2,
		shift: 5,
		shadeClose: false,
		content: "<form class='bt-form pd20 pb70' id='DataAdd'>\
						<div class='line'>\
							<span class='tname'>"+lan.database.add_name+"</span><div class='info-r'>\
							<input class='bt-input-text mr5' id='db_name' type='text' name='name' placeholder='"+lan.database.add_name_title+"' style='width:70%' />\
							<select class='bt-input-text' name='codeing' style='width:22%'>\
								<option value='utf8'>utf-8</option>\
								<option value='utf8mb4'>utf8mb4</option>\
								<option value='gbk'>gbk</option>\
								<option value='big5'>big5</option>\
							</select>\
							</div>\
						</div>\
						<div class='line'>\
						<span class='tname'>用户名</span><div class='info-r'><input class='bt-input-text mr5' type='text' name='db_user' placeholder='数据库用户' style='width:70%;margin-bottom: 10px;' /></div>\
						<span class='tname'>"+lan.database.add_pass+"</span><div class='info-r'><input class='bt-input-text mr5' type='text' name='password' id='MyPassword' style='width:311px' placeholder='"+lan.database.add_pass_title+"' value='"+(RandomStrPwd(16))+"' /><span title='"+lan.database.add_pass_rep+"' class='glyphicon glyphicon-repeat cursor' onclick='repeatPwd(16)'></span></div>\
						</div>\
                        <div class='line'>\
						<span class='tname'>"+lan.database.add_auth+"</span>\
						<div class='info-r'>\
						<select id='dataAccess' class='bt-input-text mr5' style='width:100px;'>\
							<option value='127.0.0.1'>"+lan.database.add_auth_local+"</option>\
							<option value='%'>"+lan.database.add_auth_all+"</option>\
							<option value='ip'>"+lan.database.add_auth_ip+"</option>\
						</select>\
						<input class='bt-input-text' type='text' name='address' placeholder='"+lan.database.add_auth_ip_title+"' style='width:203px;display:none;' />\
						</div>\
						</div>\
						<div class='line' style='display:none'>\
						<span class='tname'>"+lan.database.add_ps+"</span><div class='info-r'><input class='bt-input-text' type='text' name='ps' placeholder='"+lan.database.ps+"' /></div>\
						</div>\
                        <div class='bt-form-submit-btn'>\
							<button type='button' class='btn btn-danger btn-sm btn-title' onclick='layer.closeAll()'>"+lan.public.close+"</button>\
					        <button type='button' class='btn btn-success btn-sm btn-title' onclick=\"DataAdd(1)\" >"+lan.public.submit+"</button>\
				        </div>\
				      </form>"
		});
		
		$("#dataAccess").change(function(){
			var access = $(this).val();
			if(access == 'ip'){
				$("input[name=address]").show().val('');
			}else{
				$("input[name=address]").hide();
			}
		});
		
		$("#db_name").change(function(){
			$("input[name='db_user']").val($(this).val());
		});
	}else{
		var loadT=layer.load({shade:true,shadeClose:false});
		var access = $("#dataAccess").val();
		if(access != 'ip') $("input[name=address]").val(access);
		var data = $("#DataAdd").serialize();
		$.post('/database?action=AddDatabase',data,function(rdata){
			if(rdata.status){
				getData(1);
				layer.closeAll();
				layer.msg(rdata.msg,{icon:1});
			}else{
				layer.closeAll();
				layer.msg(rdata.msg,{icon:2});
			}
		});
	}
}
/**
 *设置数据库密码 
 * @param {Number} sign	操作标识
 * @param {String} passwd	数据库新密码
 */
function DataSetuppwd(sign, passwd) {
	if (sign == 0) {
		$.post('/data?action=getKey','table=config&key=mysql_root&id=1',function(rdata){
			var mypasswd=rdata;
			var index = layer.open({
			type: 1,
			skin: 'demo-class',
			area: '500px',
			title: lan.database.edit_pass_title,
			closeBtn: 2,
			shift: 5,
			shadeClose: false,
			content: "<div class='bt-form pd20 pb70' id='DataSetuppwd'>\
					<div class='line'>\
					<span class='tname'>"+lan.database.edit_root+":</span><div class='info-r'><input id='MyPassword' class='bt-input-text mr5' type='text' name='password' value='"+mypasswd+"' style='width:320px' /><span title='"+lan.database.add_pass_rep+"' class='glyphicon glyphicon-repeat cursor' onclick='repeatPwd(16)'></span>\
					</div></div>\
			        <div class='bt-form-submit-btn'>\
						<button type='button' class='btn btn-danger btn-sm btn-title' onclick='layer.closeAll()'>"+lan.public.close+"</button>\
				        <button type='button' id='PostPwBtn' class='btn btn-success btn-sm btn-title' onclick='DataSetuppwd(1)' >"+lan.public.submit+"</button>\
			        </div>\
			      </div>"
		});
		RandomStrPwd(16);
		$("#MyPassword").focus().keyup(function(e){
			if(e.keyCode == 13) $("#PostPwBtn").click();
		});
	});			
	} else {
		var loadT=layer.msg(lan.public.the,{icon:16,time:0});
		var newPassword = $("#MyPassword").val();
		var data = 'password='+encodeURIComponent(newPassword);
		$.post('/database?action=SetupPassword',data,function(rdata){
			if(rdata.status){
				getData(1);
				layer.closeAll();
				layer.msg(rdata.msg,{icon:1});
				setTimeout(function(){window.location.reload();},3000);
			}else{
				layer.close(loadT);
				layer.msg(rdata.msg,{icon:2});
			}
		});
	}
}
/**
 * 重置数据库密码
 * @param {Number} sign	操作标识
 * @param {String} passwd	数据库密码
 */
function DataRespwd(sign,id,username){
	if(sign==0){
		layer.open({
			type:1,
			skin:'demo-class',
			area:'450px',
			title:lan.database.edit_pass_title,
			closeBtn:2,
			shift:5,
			shadeClose:false,
			content:"<form class='bt-form pd20 pb70' id='DataRespwd'>\
						<div class='line'>\
						<input type='text' name='id' value='"+id+"' hidden />\
						<span class='tname'>"+lan.database.user+":</span><div class='info-r'><input class='bt-input-text' type='text' name='username' value='"+username+"' readonly='readonly' style='width:100%' />\
						</div></div>\
						<div class='line'>\
						<span class='tname'>"+lan.database.edit_pass_new+":</span><div class='info-r'><input class='bt-input-text' type='text' name='password' placeholder='"+lan.database.edit_pass_new_title+"' style='width:100%' />\
						</div></div>\
				        <div class='bt-form-submit-btn'>\
							<button type='button' class='btn btn-danger btn-sm btn-title' onclick='layer.closeAll()'>"+lan.public.close+"</button>\
					        <button type='button' class='btn btn-success btn-sm btn-title' onclick='DataRespwd(1)' >"+lan.public.submit+"</button>\
				        </div>\
				      </form>"
		});
		return;
	}
	layer.confirm(lan.database.edit_pass_confirm,{title:lan.database.edit_pass_title,icon:3,closeBtn:2},function(index){
		if(index>0){
			var loadT=layer.load({shade:true,shadeClose:false});
			var data = 'username='+encodeURIComponent($("#DataRespwd input[name='username']").val()) + '&password=' + encodeURIComponent($("#DataRespwd input[name='password']").val()) + '&id=' + $("#DataRespwd input[name='id']").val();
			$.post('/database?action=ResDatabasePassword',data,function(rdata){
				getData(1);
				layer.closeAll();
				layer.msg(rdata.msg,{icon:rdata.status?1:2});
			});
		}
	});
	
}
/**
 *数据库管理详细信息 
 * @param {Number} id	数据库编号
 * @param {String} dataname	数据库名称
 */
function DataDetails(id,dataname,page){
	if(page == undefined){
		page = '1';
	}
	var loadT = layer.msg(lan.public.the_get,{icon:16,time:0});
	$.post('/data?action=getFind','table=databases&id='+id,function(rdata){
		$.post('/data?action=getData','table=backup&search='+id+'&limit=5&p=1&type=1&tojs=DataDetails&p='+page,function(frdata){
			layer.close(loadT);
			var ftpdown = '';
			var body='';
			var port;
			
			frdata.page = frdata.page.replace(/'/g,'"').replace(/DataDetails\(/g,"DataDetails(" + id + ",0,");
			for(var i=0;i<frdata.data.length;i++){
				if(frdata.data[i].type == '0') continue;
				if(frdata.data[i].filename.length < 12){
					var ftpdown = "<a class='btlink' href='/cloud?filename="+frdata.data[i].filename+"&name="+ frdata.data[i].name+"' target='_blank'>"+lan.public.download+"</a>";
				}else{
					var ftpdown = "<a class='btlink' herf='javascrpit:;' onclick=\"RecoveryData('"+frdata.data[i].filename+"','"+dataname+"')\">"+lan.database.backup_re+"</a> | <a class='btlink' href='/download?filename="+frdata.data[i].filename+"&name="+ frdata.data[i].name+"' target='_blank'>"+lan.public.download+"</a>";
				}
				
				 body += "<tr><td><span class='glyphicon glyphicon-file'></span>"+frdata.data[i].name+"</td>\
								<td>"+(ToSize(frdata.data[i].size))+"</td>\
								<td>"+frdata.data[i].addtime+"</td>\
								<td style='color:#bbb;text-align:right'>\
								"+ftpdown+" | <a class='btlink' herf='javascrpit:;' onclick=\"DataBackupDelete('"+id+"','"+frdata.data[i].id+"')\">"+lan.public.del+"</a>\
								</td>\
							</tr>"
			}
			
			
			if(dataname == 0){
				var sBody = "<table width='100%' id='DataBackupList' class='table table-hover'>\
							<thead><tr><th>"+lan.database.backup_name+"</th><th>"+lan.database.backup_size+"</th><th>"+lan.database.backup_time+"</th><th width='140px' class='text-right'>"+lan.public.action+"</th></tr></thead>\
							<tbody id='DataBackupBody' class='list-list'>"+body+"</tbody>\
							</table>"
				$("#DataBackupList").html(sBody);
				$(".page").html(frdata.page);
				return;
			}
			layer.closeAll();
			layer.open({
					type: 1,
					skin: 'demo-class',
					area: '700px',
					title: lan.database.backup_title,
					closeBtn: 2,
					shift: 5,
					shadeClose: false,
					content:"<form class='bt-form pd15' id='DataBackup' style='padding-bottom: 0'>\
							<button class='btn btn-success btn-sm' style='margin-right:10px' type='button' onclick=\"DataBackup(" + rdata.id + ",'" + dataname + "')\">"+lan.database.backup+"</button>\
							</form>\
							<div class='divtable pd15'><table width='100%' id='DataBackupList' class='table table-hover' style='margin-bottom:0'>\
							<thead><tr><th>"+lan.database.backup_name+"</th><th>"+lan.database.backup_size+"</th><th>"+lan.database.backup_time+"</th><th class='text-right'>"+lan.public.action+"</th></tr></thead>\
							<tbody id='DataBackupBody' class='list-list'>"+body+"</tbody>\
							</table><div class='page'>"+frdata.page+"</div></div>"
			});
		});
	});
}
//恢复数据库备份
function RecoveryData(fileName,dataName){
	layer.confirm(lan.database.input_confirm,{title:lan.database.input_title,icon:3,closeBtn:2},function(index){
		var loadT =layer.msg(lan.database.input_the, {icon:16,time:0,shade: [0.3, '#000']});
		$.post('/database?action=InputSql','file='+fileName+'&name='+dataName,function(rdata){
			layer.close(loadT);
			layer.msg(rdata.msg,{icon:rdata.status?1:2});
		});
	});
}
/**
 *设置数据库备份 
 * @param {Number} id	数据库编号
 * @param {String} dataname	数据库名称
 */
function DataBackup(id,dataname){
	var loadT =layer.msg(lan.database.backup_the, {icon:16,time:0,shade: [0.3, '#000']});
	$.post('/database?action=ToBackup', "id="+id, function(rdata) {
		layer.closeAll();
		layer.msg(rdata.msg,{icon:rdata.status?1:2});
		DataDetails(id,dataname);
	});
}

/**
 *删除数据库备份 
 * @param {Number} id	数据库编号
 * @param {String} dataname	数据库名称
 */
function DataBackupDelete(typeid,id,dataname){
	layer.confirm(lan.database.backup_del_confirm,{title:lan.database.backup_del_title,icon:3,closeBtn:2},function(index){
		var loadT=layer.load({shade:true,shadeClose:false});
		$.post('/database?action=DelBackup','id='+id,function(frdata){
			layer.closeAll();
			layer.msg(frdata.msg,{icon:frdata.status?1:2});
			DataDetails(typeid,dataname);
		});
	});
}

/**
 *删除数据库 
 * @param {Number} id	数据编号
 */

function DataDelete(id,name){
	SafeMessage(lan.get('del',[name]),lan.get('confirm_del',[name]),function(){
		deleteDatabase(id,name);
	});

}

//删除操作
function deleteDatabase(id,name){
	var loadT = layer.msg(lan.get('del_all_task_the',[name]),{icon:16,time:0,shade: [0.3, '#000']});
	$.post('/database?action=DeleteDatabase','id='+id+'&name='+name,function(frdata){
		getData(1);
		layer.close(loadT);
		layer.msg(frdata.msg,{icon:frdata.status?1:2});
	});
}


//批量删除
function allDeleteDatabase(){
	var checkList = $("input[name=id]");
	var dataList = new Array();
	for(var i=0;i<checkList.length;i++){
		if(!checkList[i].checked) continue;
		var tmp = new Object();
		tmp.name = checkList[i].title;
		tmp.id = checkList[i].value;
		dataList.push(tmp);
	}
	SafeMessage(lan.database.del_all_title,"<a style='color:red;'>"+lan.get('del_all_database',[dataList.length])+"</a>",function(){
		layer.closeAll();
		syncDelete(dataList,0,'');
	});
}

//模拟同步开始批量删除数据库
function syncDelete(dataList,successCount,errorMsg){
	if(dataList.length < 1) {
		layer.msg(lan.get('del_all_database_ok',[successCount]),{icon:1});
		return;
	}
	var loadT = layer.msg(lan.get('del_all_task_the',[dataList[0].name]),{icon:16,time:0,shade: [0.3, '#000']});
	$.ajax({
			type:'POST',
			url:'/database?action=DeleteDatabase',
			data:'id='+dataList[0].id+'&name='+dataList[0].name,
			async: true,
			success:function(frdata){
				layer.close(loadT);
				if(frdata.status){
					successCount++;
					$("input[title='"+dataList[0].name+"']").parents("tr").remove();
				}else{
					if(!errorMsg){
						errorMsg = '<br><p>'+lan.database.del_all_err+'</p>';
					}
					errorMsg += '<li>'+dataList[0].name+' -> '+frdata.msg+'</li>'
				}
				
				dataList.splice(0,1);
				syncDelete(dataList,successCount,errorMsg);
			}
	});
}



/**
 * 选中项操作
 */
function goSet(num){
	//取选中对象
	var el = document.getElementsByTagName('input');
	var len = el.length;
	var data='';
	var a = '';
	var count = 0;
	//构造POST数据
	for(var i=0;i<len;i++){
		if(el[i].checked == true && el[i].value != 'on'){
			data += a+count+'='+el[i].value;
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


Date.prototype.format = function(format)
{
	 var o = {
	 "M+" : this.getMonth()+1, //month
	 "d+" : this.getDate(),    //day
	 "h+" : this.getHours(),   //hour
	 "m+" : this.getMinutes(), //minute
	 "s+" : this.getSeconds(), //second
	 "q+" : Math.floor((this.getMonth()+3)/3),  //quarter
	 "S" : this.getMilliseconds() //millisecond
	 }
	 if(/(y+)/.test(format)) format=format.replace(RegExp.$1,
	 (this.getFullYear()+"").substr(4 - RegExp.$1.length));
	 for(var k in o)if(new RegExp("("+ k +")").test(format))
	 format = format.replace(RegExp.$1,
	 RegExp.$1.length==1 ? o[k] :
	 ("00"+ o[k]).substr((""+ o[k]).length));
	 return format;
}
//时间戳到格式日期
function getLocalTime(tm) {
	return new Date(parseInt(tm) * 1000).format("yyyy/MM/dd hh:mm:ss");
}


//取扩展名
function GetExtName(fileName,oext){
	var extArr = fileName.split(".");
	var exts = ['conf','sh','cnf','pl','so','passwd','cshrc','deny','cache','init','po','ext2','ext3','ext4','i686','img','gz','efi','old','pid','lock','frm','opt','err','MYI','MYD','CSM'];
	var extLastName = extArr[extArr.length - 1];
	if(oext) return extLastName;
	if(extArr.length<2 || extLastName.length>5 || extLastName.length < 2){
		return "file";
	}
	for(var i=0; i<exts.length; i++){
		if(exts[i]==extLastName){
			return "file";
		}
	}
	return extLastName;
}

//导入数据库
function InputDatabase(name){
	var path = getCookie('backup_path') + "/database";
	$.post('/files?action=GetDir','path='+path,function(rdata){
		var Body = '';
		for (var i = 0; i < rdata.FILES.length; i++) {
			if(rdata.FILES[i] == null) continue;
			var fmp = rdata.FILES[i].split(";");
			var ext = GetExtName(fmp[0],true);
			
			if(ext != 'sql' && ext != 'zip' && ext != 'gz' && ext != 'tgz') continue;
			Body += "<tr>\
						<td class='column-name'><span class='ico ico-"+ext+"'></span><a class='text'>" + fmp[0] + "</a></td>\
						<td>" + ((fmp[2].length > 11)?fmp[2]:getLocalTime(fmp[2])) + "</td>\
						<td>" + (ToSize(fmp[1])) + "</td>\
						<td class='editmenu'>\
							<a class='btlink' href='javascript:;' onclick=\"RecoveryData('" + rdata.PATH +"/"+ fmp[0] + "','"+name+"')\">"+lan.database.input+"</a>\
						</span></td>\
					</tr>";
		}
		layer.open({
				type: 1,
				skin: 'demo-class',
				area: '600px',
				title: lan.database.input_title_file,
				closeBtn: 2,
				shift: 5,
				shadeClose: false,
				content: '<div class="pd15">'
							+'<button class="btn btn-default btn-sm" onclick="UploadFiles1(\''+name+'\')">'+lan.database.input_local_up+'</button>'
							+'<div class="divtable mtb15" style="max-height:300px; overflow:auto">'
								+'<table class="table table-hover">'
									+'<thead>'
										+'<tr>'
											+'<th>'+lan.files.file_name+'</th>'
											+'<th>'+lan.files.file_etime+'</th>'
											+'<th>'+lan.files.file_size+'</th>'
											+'<th>'+lan.public.action+'</th>'
										+'</tr>'
									+'</thead>'
									+'<tbody>'+Body+'</tbody>'
								+'</table>'
							+'</div>'
							+'<ul class="help-info-text c7">'
							   +'<li>'+lan.database.input_ps1+'</li>'
							   +'<li>'+lan.database.input_ps2+'</li>'
							   +'<li>'+lan.database.input_ps3+'</li>'
							+'</ul>'
						+'</div>'
		});
	});
}


//上传文件
function UploadFiles1(name){
	var path = getCookie('backup_path') + "/database/";
	var index = layer.open({
		type:1,
		closeBtn: 2,
		title:lan.files.up_title+' --- <span style="color:red;">'+lan.database.input_up_type+'</span>',
		area: ['500px','500px'], 
		shadeClose:false,
		content:'<div class="fileUploadDiv"><input type="hidden" id="input-val" value="'+path+'" />\
				<input type="file" id="file_input"  multiple="true" autocomplete="off" />\
				<button type="button"  id="opt" autocomplete="off">'+lan.files.up_add+'</button>\
				<button type="button" id="up" autocomplete="off" >'+lan.files.up_start+'</button>\
				<span id="totalProgress" style="position: absolute;top: 7px;right: 147px;"></span>\
				<span style="float:right;margin-top: 9px;">\
				<font>'+lan.files.up_coding+':</font>\
				<select id="fileCodeing" >\
					<option value="byte">'+lan.files.up_bin+'</option>\
					<option value="utf-8">UTF-8</option>\
					<option value="gb18030">GB2312</option>\
				</select>\
				</span>\
				<button type="button" id="filesClose" autocomplete="off">'+lan.public.close+'</button>\
				<ul id="up_box"></ul></div>'
	});
	$("#filesClose").click(function(){
		layer.close(index);
		InputDatabase(name);
	});
	UploadStart(true);
}


//设置访问权限
function SetDatabaseAccess(dataName,action){
	if(action == 1){
		var access = $("#dataAccess").val();
		if(access == 'ip') access = $("input[name=address]").val();
		layer.msg(lan.public.the,{icon:16,time:0,shade: [0.3, '#000']});
		$.post('/database?action=SetDatabaseAccess','name='+dataName+'&access='+access,function(rdata){
			layer.closeAll();
			layer.msg(rdata.msg,{icon:rdata.status?1:2});
		});
		return;
	}
	
	
	$.post('/database?action=GetDatabaseAccess','name='+dataName,function(rdata){
		if(rdata == null){
			layer.msg(lan.database.auth_err,{icon:2});
			return;
		}
		layer.open({
			type: 1,
			skin: 'demo-class',
			area: '480px',
			title: lan.database.auth_title+'['+dataName+']',
			closeBtn: 2,
			shift: 5,
			shadeClose: false,
			content: "<form class='bt-form pd20 pb70' id='DatabaseAccess'>\
	                        <div class='line'>\
							<span class='tname'>"+lan.database.auth_name+"</span>\
							<div class='info-r'>\
							<select id='dataAccess' class='bt-input-text mr5' style='width:88px;'>\
								<option value='127.0.0.1' "+(rdata.msg == '127.0.0.1'?'selected':'')+">"+lan.database.add_auth_local+"</option>\
								<option value='%' "+(rdata.msg == '%'?'selected':'')+">"+lan.database.add_auth_all+"</option>\
								<option value='ip' "+((rdata.msg != '127.0.0.1' && rdata.msg != '%')?'selected':'')+">"+lan.database.add_auth_ip+"</option>\
							</select>\
							<input class='bt-input-text' type='text' name='address' placeholder='允可IP,多个请用逗号隔开' value='"+rdata.msg+"' style='width:218px;"+((rdata.msg != '127.0.0.1' && rdata.msg != '%')?'':'display:none;')+"' />\
							</div>\
							</div>\
	                        <div class='bt-form-submit-btn'>\
								<button type='button' class='btn btn-danger btn-sm btn-title' onclick='layer.closeAll()'>"+lan.public.close+"</button>\
						        <button type='button' class='btn btn-success btn-sm btn-title' onclick=\"SetDatabaseAccess('"+dataName+"',1)\" >"+lan.public.ok+"</button>\
					        </div>\
					      </form>"
		});
		
		$("#dataAccess").change(function(){
			var access = $(this).val();
			if(access == 'ip'){
				$("input[name=address]").show().val('');
			}else{
				$("input[name=address]").hide();
			}
		});
	});
}

//同步到数据库
function SyncToDatabases(type){
	//取选中对象
	var el = document.getElementsByTagName('input');
	var len = el.length;
	var data=[];
	//构造POST数据
	for(var i=0;i<len;i++){
		if(el[i].checked == true && el[i].value != 'on'){
			data.push(el[i].value)
		}
	}
	
	var loadT = layer.msg(lan.database.sync_the,{icon:16,time:0,shade: [0.3, '#000']});
	$.post('/database?action=SyncToDatabases&type='+type,{ids:JSON.stringify(data)},function(rdata){
		layer.close(loadT);
		layer.msg(rdata.msg,{icon:rdata.status?1:2});
	});
}

//从数据库中获取
function SyncGetDatabases(){
	var loadT = layer.msg(lan.database.sync_the,{icon:16,time:0,shade: [0.3, '#000']});
	$.post('/database?action=SyncGetDatabases',function(rdata){
		layer.close(loadT);
		getData(1);
		layer.msg(rdata.msg,{icon:rdata.status?1:2});
	});
}


//管理数据库
function AdminDatabase(name,username,password){
	if($("#toPHPMyAdmin").attr('action').indexOf('phpmyadmin') == -1){
		layer.msg(lan.database.phpmyadmin_err,{icon:2,shade: [0.3, '#000']})
		setTimeout(function(){ window.location.href = '/soft'; },3000);
		return;
	}
	var murl = $("#toPHPMyAdmin").attr('action');
	$("#pma_username").val(username);
	$("#pma_password").val(password);
	$("#db").val(name);
	layer.msg(lan.database.phpmyadmin,{icon:16,shade: [0.3, '#000'],time:1000});
	setTimeout(function(){
		$("#toPHPMyAdmin").submit();
	},200);
}

$(".safe .tipstitle").mouseover(function(){
var title = $(this).attr("data-title");
layer.tips(title, this, {
    tips: [1, '#3c8dbc'],
    time:0
})
}).mouseout(function(){
	$(".layui-layer-tips").remove();
})
$(".btn-more").hover(function(){
	$(this).addClass("open");
},function(){
	$(this).removeClass("open");
});
