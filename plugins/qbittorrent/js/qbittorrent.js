function qbPostMin(method, args, callback){

    var req_data = {};
    req_data['name'] = 'qbittorrent';
    req_data['func'] = method;
 
    if (typeof(args) != 'undefined' && args!=''){
        req_data['args'] = JSON.stringify(args);
    }

    $.post('/plugins/run', req_data, function(data) {
        if (!data.status){
            layer.msg(data.msg,{icon:0,time:2000,shade: [0.3, '#000']});
            return;
        }

        if(typeof(callback) == 'function'){
            callback(data);
        }
    },'json'); 
}

function qbPost(method, args, callback){
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });
    qbPostMin(method,args,function(data){
        layer.close(loadT);
        if(typeof(callback) == 'function'){
            callback(data);
        } 
    });
}

function showHideHash(obj){
    var a = "glyphicon-eye-open";
    var b = "glyphicon-eye-close";
    
    if($(obj).hasClass(a)){
        $(obj).removeClass(a).addClass(b);
        $(obj).prev().text($(obj).prev().attr('data-pw'))
    } else{
        $(obj).removeClass(b).addClass(a);
        $(obj).prev().text($(obj).attr('data-pw'));
    }
}


function copyText(password){
    var clipboard = new ClipboardJS('#bt_copys');
    clipboard.on('success', function (e) {
        layer.msg('复制成功',{icon:1,time:2000});
    });

    clipboard.on('error', function (e) {
        layer.msg('复制失败，浏览器不兼容!',{icon:2,time:2000});
    });
    $("#bt_copys").attr('data-clipboard-text',password);
    $("#bt_copys").click();
}

function getLocalTime(nS) {     
   return new Date(parseInt(nS) * 1000).toLocaleString().replace(/:\d{1,2}$/,' ');     
}



function qbAdd(){

    var loadOpen = layer.open({
        type: 1,
        title: '添加资源',
        area: '400px',
        content:"<div class='bt-form pd20 pb70 c6'>\
            <div class='version line'>\
            <div><input class='bt-input-text mr5 outline_no' type='text' id='qb_hash' name='qb_hash' style='height: 28px; border-radius: 3px;width: 350px;' placeholder='hash'></div>\
            </div>\
            <div class='bt-form-submit-btn'>\
                <button type='button' id='qb_close' class='btn btn-danger btn-sm btn-title'>关闭</button>\
                <button type='button' id='qb_ok' class='btn btn-success btn-sm btn-title bi-btn'>确认</button>\
            </div>\
        </div>"
    });

    $('#qb_close').click(function(){
        layer.close(loadOpen);
    });

    $('#qb_ok').click(function(){
        var hash = $('#qb_hash').val();
        qbPost('qb_add', {hash:hash}, function(data){

            var rdata = $.parseJSON(data.data);
            if (rdata['status']){
                showMsg(rdata.msg, function(){
                    qbList();
                },{icon:1,time:2000,shade: [0.3, '#000']});
                layer.close(loadOpen);
            } else {
                layer.msg(rdata.msg,{icon:2,time:2000,shade: [0.3, '#000']});
            }
        });
    });
}


function qbDel(hash){
    qbPost('qb_del', {hash:hash}, function(data){
        var rdata = $.parseJSON(data.data);
        if (rdata['status']){
            layer.msg(rdata.msg,{icon:1,time:2000,shade: [0.3, '#000']});
        } else {
            layer.msg(rdata.msg,{icon:2,time:2000,shade: [0.3, '#000']});
        }
    });
}

function qbListFind(){
    var qbs = $('#qb_selected').val();
    if ( qbs == '0' ){
        qbList();
    } else {
        qbList(qbs);
    }
}

function openAdminUrl(){
    qbPost('qb_url', '', function(data){
        var rdata = $.parseJSON(data.data);
        window.open(rdata.data);
    });
}

function qbList(search){
    var _data = {};
    _data['test'] ='yes';
    if(typeof(search) != 'undefined'){
        _data['type'] = search;
    }

    qbPost('qb_list', _data, function(data){

        var rdata = $.parseJSON(data.data);
        if (!rdata['status']){
            layer.msg(rdata.msg,{icon:0,time:2000,shade: [0.3, '#000']});
            return;
        }

        content = '<select id="qb_selected" class="bt-input-text mr20" style="width:30%;margin-bottom: 3px;">'+
            '<option value="0">所有</option>' +
            '<option value="completed">已下载</option>' +
            '<option value="downloading">下载中</option>' +
            '</select>';
        content += '<button class="btn btn-success btn-sm" onclick="qbListFind();">查找</button></div>';

        content += '<div class="divtable" style="margin-top:5px;"><table class="table table-hover" width="100%" cellspacing="0" cellpadding="0" border="0">';
        content += '<thead><tr>';
        content += '<th>种子(hash)</th>';
        content += '<th>添加时间</th>';
        content += '<th>操作(<a class="btlink" onclick="qbAdd();">添加</a> | <a class="btlink" onclick="openAdminUrl();">管理</a>)</th>';
        content += '</tr></thead>';

        content += '<tbody>';

        ulist = rdata.data.torrents;
        for (i in ulist){
            content += '<tr><td>'+
                    '<span class="password" data-pw="'+ulist[i]['hash']+'">'+ulist[i]['hash'].substr(0,3)+'</span>' +
                    '<span onclick="showHideHash(this)" data-pw="'+ulist[i]['hash'].substr(0,3)+'" class="glyphicon glyphicon-eye-open cursor pw-ico" style="margin-left:10px"></span>'+
                    '<span class="ico-copy cursor btcopy" style="margin-left:10px" title="复制种子hash" onclick="copyText(\''+ulist[i]['hash']+'\')"></span>'+
                '</td>'+
                '<td>'+getLocalTime(ulist[i]['added_on'])+'</td>'+
                '<td><a class="btlink" onclick="qbDel(\''+ulist[i]['hash']+'\')">删除</a></td></tr>';
        }

        content += '</tbody>';
        content += '</table></div>';

        $(".soft-man-con").html(content);

        var type = rdata.data.type;
        if (type == ''){
            $("#qb_selected option[value='0']").attr("selected", true);
        } else {
            $("#qb_selected option[value='"+type+"']").attr("selected", true);
        }
    });
}
