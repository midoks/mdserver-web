
function msodPost(method,args,callback){
    var _args = null; 
    if (typeof(args) == 'string'){
        _args = JSON.stringify(toArrayObject(args));
    } else {
        _args = JSON.stringify(args);
    }

    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });
    $.post('/plugins/run', {name:'msonedrive', func:method, args:_args}, function(data) {
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


function createDir(){
    layer.open({
        type: 1,
        area: "400px",
        title: "创建目录",
        closeBtn: 1,
        shift: 5,
        shadeClose: false,
        btn: ['确定','取消'],
        content:'<div class="bingfa bt-form c6" style="padding-bottom: 10px;">\
                    <p>\
                        <span class="span_tit">目录名称：</span>\
                        <input style="width: 200px;" type="text" name="newPath" value="">\
                    </p>\
                </div>',
        success:function(){
            $("input[name='newPath']").focus().keyup(function(e){
                if(e.keyCode == 13) $(".layui-layer-btn0").click();
            });
        },
        yes:function(index,layero){
            var name = $("input[name='newPath']").val();
            if(name == ''){
                layer.msg('目录名称不能为空!',{icon:2});
                return;
            }
            var path = $("#myPath").val();
            var dirname = name;
            var loadT = layer.msg('正在创建目录['+dirname+']...',{icon:16,time:0,shade: [0.3, '#000']});
            msodPost('create_dir', {path:path,name:dirname}, function(data){
            	layer.close(loadT);
                var rdata = $.parseJSON(data.data);
                if(rdata.status) {
                    showMsg(rdata.msg, function(){
                        layer.close(index);
                        odList(path);
                    } ,{icon:1}, 2000);
                } else{
                    layer.msg(rdata.msg,{icon:2});
                }
            });
        }
    });
}


//设置API
function authApi(){

    msodPost('conf', {}, function(rdata){
        var rdata = $.parseJSON(rdata.data);

        // console.log(rdata);
        // console.log(rdata.data.auth_url);
        var apicon = '';
        if (rdata.status){

		    var html = '';
		    html += '<button id="clear_auth" onclick="clearAuth();" class="btn btn-default btn-sm">清空配置</button>';
		
		    var loadOpen = layer.open({
		        type: 1,
		        title: '已授权',
		        area: '240px',
		        content:'<div class="change-default pd20">'+html+'</div>',
		        success: function(){
		        	$('#clear_auth').click(function(){
		        		msodPost('clear_auth', {}, function(rdata){
							var rdata = $.parseJSON(rdata.data);
							showMsg(rdata.msg,function(){
								layer.close(loadOpen);
					            odList('/');
					        },{icon:rdata.status?1:2},2000);
						});  
		        	});	
		        }
		    });
		    return true;

        } else{
	        apicon = '<div class="new_form">'+$("#check_api").html()+'</div>';
        }
        
        var layer_auth = layer.open({
            type: 1,
            area: "620px",
            title: "OneDrive授权",
            closeBtn: 1,
            shift: 5,
            shadeClose: false,
            content:apicon,
            success:function(layero,index){
            	// console.log(layero,index);
            	if (!rdata.status){
            		$('.check_api .step_two_url').val(rdata.data['auth_url']);
            		$('.check_api .open_btlink').attr('href',rdata.data['auth_url']);

            		$('.check_api .ico-copy').click(function(){
            			copyPass(rdata.data['auth_url']);
            		});

            		$('.check_api .set_auth_btn').click(function(){

            			var url = $('.check_api .OneDrive').val();
						if ( url == ''){
							layer.msg("验证URL不能为空",{icon:2});
							return;
						}
						// console.log(url);
						msodPost('set_auth_url', {url:url}, function(rdata){
							var rdata = $.parseJSON(rdata.data);
							var show_time = 2000;
							if (!rdata.status){
								show_time = 10000;
							}

							showMsg(rdata.msg,function(){
								if (rdata.status){
									layer.close(layer_auth);
									odList('/');
								}
					        },{icon:rdata.status?1:2},show_time);
						});
            		});


            	}
            	
            }
        });
    });
}

//计算当前目录偏移
function upPathLeft(){
    var UlWidth = $(".place-input ul").width();
    var SpanPathWidth = $(".place-input").width() - 20;
    var Ml = UlWidth - SpanPathWidth;
    if(UlWidth > SpanPathWidth ){
        $(".place-input ul").css("left",-Ml)
    }
    else{
        $(".place-input ul").css("left",0)
    }
}

function odList(path){
    msodPost('get_list', {path:path}, function(rdata){
        var rdata = $.parseJSON(rdata.data);
        if(rdata.status === false){
            showMsg(rdata.msg,function(){
                authApi();
            },{icon:2},2000);
            return;
        }

        var mlist = rdata.data;
        var listBody = ''
        var listFiles = ''
        for(var i=0;i<mlist.list.length;i++){
            if(mlist.list[i].type == null){
                listBody += '<tr><td class="cursor" onclick="odList(\''+(path+'/'+mlist.list[i].name).replace('//','/')+'\')"><span class="ico ico-folder"></span>\<span>'+mlist.list[i].name+'</span></td>\
                <td>-</td>\
                <td>-</td>\
                <td class="text-right"><a class="btlink" onclick="deleteFile(\''+mlist.list[i].name+'\', true)">删除</a></td></tr>'
            }else{
                listFiles += '<tr><td class="cursor"><span class="ico ico-file"></span>\<span>'+mlist.list[i].name+'</span></td>\
                <td>'+toSize(mlist.list[i].size)+'</td>\
                <td>'+getLocalTime(mlist.list[i].time)+'</td>\
                <td class="text-right"><a target="_blank" href="'+mlist.list[i].download+'" class="btlink">下载</a> | <a class="btlink" onclick="deleteFile(\''+mlist.list[i].name+'\', false)">删除</a></td></tr>'
            }
        }
        listBody += listFiles;

        var pathLi='';
        var tmp = path.split('/')
        var pathname = '';
        var n = 0;
        for(var i=0;i<tmp.length;i++){
            if(n > 0 && tmp[i] == '') continue;
            var dirname = tmp[i];
            if(dirname == '') {
                dirname = '根目录';
                n++;
            }
            pathname += '/' + tmp[i];
            pathname = pathname.replace('//','/');
            pathLi += '<li><a title="'+pathname+'" onclick="odList(\''+pathname+'\')">'+dirname+'</a></li>';
        }
        var um = 1;
        if(tmp[tmp.length-1] == '') um = 2;
        var backPath = tmp.slice(0,tmp.length-um).join('/') || '/';
        $('#myPath').val(path);
        $(".upyunCon .place-input ul").html(pathLi);
        $(".upyunlist .list-list").html(listBody);

        upPathLeft();

        $('#backBtn').unbind().click(function() {
            odList(backPath);
        });

        $('.upyunCon .refreshBtn').unbind().click(function(){
            odList(path);
        });
    });
}


//删除文件
function deleteFile(name, is_dir){
    if (is_dir === false){
        safeMessage('删除文件','删除后将无法恢复，真的要删除['+name+']吗?',function(){
            var path = $("#myPath").val();
            var filename = name;
            msodPost('delete_file', {filename:filename,path:path}, function(rdata){
                var rdata = $.parseJSON(rdata.data);
                showMsg(rdata.msg,function(){
                    odList(path);
                },{icon:rdata.status?1:2},2000);
            });
        });
    } else {
        safeMessage('删除文件夹','删除后将无法恢复，真的要删除['+name+']吗?',function(){
            var path = $("#myPath").val();
            msodPost('delete_dir', {dir_name:name,path:path}, function(rdata){
                var rdata = $.parseJSON(rdata.data);
                showMsg(rdata.msg,function(){
                    odList(path);
                },{icon:rdata.status?1:2},2000);
            });
        });
    }
}