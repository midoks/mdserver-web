
function str2Obj(str){
    var data = {};
    kv = str.split('&');
    for(i in kv){
        v = kv[i].split('=');
        data[v[0]] = v[1];
    }
    return data;
}

function gogsPost(method,args,callback, title){

    var _args = null; 
    if (typeof(args) == 'string'){
        _args = JSON.stringify(str2Obj(args));
    } else {
        _args = JSON.stringify(args);
    }

    var _title = '正在获取...';
    if (typeof(title) != 'undefined'){
        _title = title;
    }

    var loadT = layer.msg(_title, { icon: 16, time: 0, shade: 0.3 });
    $.post('/plugins/run', {name:'gogs', func:method, args:_args}, function(data) {
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

function gogsSetConfig(){
    gogsPost('get_gogs_conf', '', function(data){
        console.log(data);
        var rdata = $.parseJSON(data.data);
        console.log(rdata);
        var mlist = '';
        for (var i = 0; i < rdata.length; i++) {
            var w = '140';
            if (rdata[i].name == 'error_reporting') w = '250';
            var ibody = '<input style="width: ' + w + 'px;" class="bt-input-text mr5" name="' + rdata[i].name + '" value="' + rdata[i].value + '" type="text" >';
            switch (rdata[i].type) {
                case 0:
                    var selected_1 = (rdata[i].value == 1) ? 'selected' : '';
                    var selected_0 = (rdata[i].value == 0) ? 'selected' : '';
                    ibody = '<select class="bt-input-text mr5" name="' + rdata[i].name + '" style="width: ' + w + 'px;">\
                        <option value="1" ' + selected_1 + '>开启</option>\
                        <option value="0" ' + selected_0 + '>关闭</option>\
                        </select>';
                    break;
                case 1:
                    var selected_1 = (rdata[i].value == 'On') ? 'selected' : '';
                    var selected_0 = (rdata[i].value == 'Off') ? 'selected' : '';
                    ibody = '<select class="bt-input-text mr5" name="' + rdata[i].name + '" style="width: ' + w + 'px;">\
                        <option value="On" ' + selected_1 + '>开启</option>\
                        <option value="Off" ' + selected_0 + '>关闭</option></select>'
                    break;
                case 2:
                    var selected_1 = (rdata[i].value == 'true') ? 'selected' : '';
                    var selected_0 = (rdata[i].value == 'false') ? 'selected' : '';
                    ibody = '<select class="bt-input-text mr5" name="' + rdata[i].name + '" style="width: ' + w + 'px;">\
                        <option value="true" ' + selected_1 + '>开启</option>\
                        <option value="false" ' + selected_0 + '>关闭</option></select>'
                    break;
            }
            mlist += '<p><span>' + rdata[i].name + '</span>' + ibody + ', <font>' + rdata[i].ps + '</font></p>'
        }
        var html = '<style>.conf_p p{margin-bottom: 2px}</style><div class="conf_p" style="margin-bottom:0">\
                        ' + mlist + '\
                        <div style="margin-top:10px; padding-right:15px" class="text-right">\
                        <button class="btn btn-success btn-sm mr5" onclick="gogsSetConfig()">刷新</button>\
                        <button class="btn btn-success btn-sm" onclick="submitGogsConf()">保存</button></div>\
                    </div>';
        $(".soft-man-con").html(html);
    });
}


//提交PHP配置
function submitGogsConf() {
    var data = {
        REQUIRE_SIGNIN_VIEW: $("select[name='REQUIRE_SIGNIN_VIEW']").val() || 'false',
    };

    gogsPost('submit_gogs_conf', data, function(ret_data){
        var rdata = $.parseJSON(ret_data.data);
        console.log(rdata);
        layer.msg(rdata.msg, { icon: rdata.status ? 1 : 2 });
    });
}