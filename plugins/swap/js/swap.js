

function swapPost(method, version, args,callback){
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });

    var req_data = {};
    req_data['name'] = 'swap';
    req_data['func'] = method;
    req_data['version'] = version;
 
    if (typeof(args) == 'string'){
        req_data['args'] = JSON.stringify(toArrayObject(args));
    } else {
        req_data['args'] = JSON.stringify(args);
    }

    $.post('/plugins/run', req_data, function(data) {
        layer.close(loadT);
        if (!data.status){
            //错误展示10S
            layer.msg(data.msg,{icon:0,time:2000,shade: [10, '#000']});
            return;
        }

        if(typeof(callback) == 'function'){
            callback(data);
        }
    },'json'); 
}


function swapStatus() {
    swapPost('swap_status', '', {}, function(data){
        var rdata = $.parseJSON(data.data);
        var size = rdata.data['size'];

        var spCon = '<div class="conf_p" style="margin-top:30px;margin-bottom:0">\
                        <div style="border-bottom:#ccc 1px solid;padding-bottom:10px;margin-bottom:10px"><span><b>最大使用交换分区: </b></span>\
                        <select class="bt-input-text" name="swap_set" style="margin-left:-4px">\
                            <option value="218MB">218MB</option>\
                            <option value="512MB">512MB</option>\
                            <option value="1GB">1GB</option>\
                            <option value="2GB">2GB</option>\
                            <option value="4GB">4GB</option>\
                        </select>\
                        <span>当前: </span><input style="width:70px;background-color:#eee;" class="bt-input-text mr5" name="cur_size" type="text" value="' + size + '" readonly>MB\
                        </div>\
                        <p><span>修改</span><input style="width: 70px;" class="bt-input-text mr5" name="size" value="' + size + '" type="number" >MB</p>\
                        <div style="margin-top:10px; padding-right:15px" class="text-right"><button class="btn btn-success btn-sm" onclick="submitSwap()">提交</button></div>\
                    </div>';

        $(".soft-man-con").html(spCon);

        $(".conf_p select[name='swap_set']").change(function() {
            var swap_size = $(this).val();
            if (swap_size.indexOf('GB')>-1){
                swap_size = parseInt(swap_size)*1024;
            } else{
                swap_size = parseInt(swap_size);
            }
            $("input[name='cur_size']").val(swap_size);
            $("input[name='size']").val(swap_size);
        });
    });
}

function submitSwap(){
    var size = $("input[name='size']").val();
    swapPost('change_swap', '',{"size":size}, function(data){
        var rdata = $.parseJSON(data.data);
        layer.msg(rdata.msg, { icon: rdata.status ? 1 : 5 });
    });
}

function readme(){
    var readme = '<ul class="help-info-text c7">';
    readme += '<li>dd if=/dev/zero of=/www/server/swap/swapfile bs=1M count=2048</li>';
    readme += '<li>mkswap /www/server/swap/swapfile</li>';
    readme += '</ul>';
    $('.soft-man-con').html(readme);
}
