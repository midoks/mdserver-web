

function bkfPost(method,args,callback){
    var _args = null; 
    if (typeof(args) == 'string'){
        _args = JSON.stringify(toArrayObject(args));
    } else {
        _args = JSON.stringify(args);
    }

    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });
    $.post('/plugins/run', {name:'backup_ftp', func:method, args:_args}, function(data) {
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

function getFtpLocalTime(data){
    var str = data.slice(0,4)+"/"+data.slice(4,6)+"/"+data.slice(6,8)
        + " " + data.slice(8,10)+":"+data.slice(10,12)+":"+data.slice(12,14);
    return str;
}

// 自定义部分
var i = null;
//设置API
function upyunApi(){

    bkfPost('conf', {}, function(rdata){
        var rdata = $.parseJSON(rdata.data);
        var token = rdata.data;
        var check_status = token.use_sftp;
        var sftp_checked = check_status === "true" ? " checked=\"checked\"" : "";

        if (typeof(token.ftp_host) == 'undefined'){
            token.ftp_host = '';
        }

        if (typeof(token.ftp_user) == 'undefined'){
            token.ftp_user = '';
        }

        if (typeof(token.ftp_pass) == 'undefined'){
            token.ftp_pass = '';
        }

        if (typeof(token.backup_path) == 'undefined'){
            token.backup_path = '';
        }

        var apicon = '<div class="bingfa mtb15" style="padding-bottom:0px;">\
            <p>\
                <span class="span_tit">使用SFTP：</span>\ <input style="width: 20px; vertical-align:middle;" type="checkbox" name="use_sftp"'+sftp_checked+'> 是否使用SFTP进行数据传输 \
            </p>\
            <p>\
                <span class="span_tit">Host：</span>\
                <input placeholder="请输入主机地址" style="width: 200px;" type="text" name="upyun_service" value="'+token.ftp_host+'">  *服务器地址,FTP默认端口21, SFTP默认端口22\
            </p>\
            <p>\
                <span class="span_tit">用户名：</span>\
                <input style="width: 200px;" type="text" name="ftp_username" value="'+token.ftp_user+'">  *指定用户名\
            </p>\
            <p>\
                <span class="span_tit">密码：</span>\
                <input style="width: 200px;" type="password" name="ftp_password" value="'+token.ftp_pass+'">  *登录密码\
            </p>\
            <p>\
                <span class="span_tit">存储位置：</span>\
                <input placeholder="请输入存储位置" style="width: 200px;" type="text" name="backup_path" value="'+token.backup_path+'"> *相对于根目录的路径，默认是/backup\
            </p>\
        </div>';
        layer.open({
            type: 1,
            area: "600px",
            title: "FTP/SFTP帐户设置",
            closeBtn: 1,
            shift: 5,
            shadeClose: false,
            btn: ['确定','取消'],
            content:apicon,
            yes:function(index,layero){
                var data = {
                    use_sftp:$("input[name='use_sftp']").prop('checked'),
                    ftp_user:$("input[name='ftp_username']").val(),
                    ftp_pass:$("input[name='ftp_password']").val(),
                    ftp_host:$("input[name='upyun_service']").val(),
                    backup_path:$("input[name='backup_path']").val()
                }
                bkfPost('set_config', data, function(rdata){
                    var rdata = $.parseJSON(rdata.data);
                    if (rdata.status){
                        showMsg(rdata.msg,function(){
                            layer.close(index);
                            osList("/");
                        },{icon:1},2000);
                    } else{
                       layer.msg(rdata.msg,{icon:2});
                    }
                })
            },
        });
    });
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
            // var loadT = layer.msg('正在创建目录['+dirname+']...',{icon:16,time:0,shade: [0.3, '#000']});
            bkfPost('create_dir', {path:path,name:dirname}, function(data){
                var rdata = $.parseJSON(data.data);
                if(rdata.status) {
                    showMsg(rdata.msg, function(){
                        layer.close(index);
                        osList(path);
                    } ,{icon:1}, 2000);
                } else{
                    layer.msg(rdata.msg,{icon:2});
                }
            });
        }
    });
}

//删除文件
function deleteFile(name, is_dir){
    if (is_dir === false){
        safeMessage('删除文件','删除后将无法恢复，真的要删除['+name+']吗?',function(){
            var path = $("#myPath").val();
            var filename = name;
            bkfPost('delete_file', {filename:filename,path:path}, function(rdata){
                var rdata = $.parseJSON(rdata.data);
                showMsg(rdata.msg,function(){
                    osList(path);
                },{icon:rdata.status?1:2},2000);
            });
        });
    } else {
        safeMessage('删除文件夹','删除后将无法恢复，真的要删除['+name+']吗?',function(){
            var path = $("#myPath").val();
            bkfPost('delete_dir', {dir_name:name,path:path}, function(rdata){
                var rdata = $.parseJSON(rdata.data);
                showMsg(rdata.msg,function(){
                    osList(path);
                },{icon:rdata.status?1:2},2000);
            });
        });
    }
}

function osList(path){
    bkfPost('get_list', {path:path}, function(rdata){
        
        var rdata = $.parseJSON(rdata.data);
        if(rdata.status === false){
            showMsg(rdata.msg,function(){
                upyunApi();
            },{icon:2},2000);
            return;
        }

        var mlist = rdata.data;
        // console.log(mlist);
        var listBody = ''
        var listFiles = ''
        for(var i=0;i<mlist.list.length;i++){
            if(mlist.list[i].type == null){
                listBody += '<tr><td class="cursor" onclick="osList(\''+(path+'/'+mlist.list[i].name).replace('//','/')+'\')"><span class="ico ico-folder"></span>\<span>'+mlist.list[i].name+'</span></td>\
                <td>-</td>\
                <td>-</td>\
                <td class="text-right"><a class="btlink" onclick="deleteFile(\''+mlist.list[i].name+'\', true)">删除</a></td></tr>'
            }else{
                listFiles += '<tr><td class="cursor"><span class="ico ico-file"></span>\<span>'+mlist.list[i].name+'</span></td>\
                <td>'+toSize(mlist.list[i].size)+'</td>\
                <td>'+getFtpLocalTime(mlist.list[i].time)+'</td>\
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
            pathLi += '<li><a title="'+pathname+'" onclick="osList(\''+pathname+'\')">'+dirname+'</a></li>';
        }
        var um = 1;
        if(tmp[tmp.length-1] == '') um = 2;
        var backPath = tmp.slice(0,tmp.length-um).join('/') || '/';
        $('#myPath').val(path);
        $(".upyunCon .place-input ul").html(pathLi);
        $(".upyunlist .list-list").html(listBody);

        upPathLeft();

        $('#backBtn').unbind().click(function() {
            osList(backPath);
        });

        $('.upyunCon .refreshBtn').unbind().click(function(){
            osList(path);
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
// $('.layui-layer-page').css('height','670px');