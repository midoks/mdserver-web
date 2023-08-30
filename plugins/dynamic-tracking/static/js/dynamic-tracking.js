function changeDivH(){
    var l = $(window).height();
    var w = $(window).width();
    
    $('#ff_box').css('height',l-80-60);

    $('#file_list').css('height',l-80-60);
    $('#file_list .tab-con .list').css('height', l-80-60-70);


    $('#flame_graph').css('height',l-80-60).css('width',w-300-200-40);
    $('#flame_graph iframe').css('height',l-80-60-70);  
}


$(document).ready(function(){
   var tag = $.getUrlParam('tag');
    if(tag == 'dynamic-tracking'){
        dynamicTrackingLoad();
    }
});

function dynamicTrackingLoad(){
    changeDivH();
    $(window).resize(function(){
        changeDivH();
    });

    //加载采样数据列表
    dtFileList();
}


$('.data-collect').click(function(){
    layer.msg('开始采样',{icon:0,time:2000});
    var pid = $('#searchValue').val();

    dtPost('simple_trace', '', {pid:pid}, function(rdata){
        // console.log(rdata);
        var rdata = $.parseJSON(rdata.data);
        layer.msg(rdata['msg'],{icon:rdata['status']?1:2,time:2000,shade: [0.3, '#000']});
    });
});


function dtPost(method, version, args,callback){

    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });
    var req_data = {};
    req_data['name'] = 'dynamic-tracking';
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

function dtPostCb(method, version, args,callback){
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });

    var pdata = {};
    pdata['name'] = 'dynamic-tracking';
    pdata['func'] = method;
    args['version'] = version;
 
    if (typeof(args) == 'string'){
        pdata['args'] = JSON.stringify(toArrayObject(args));
    } else {
        pdata['args'] = JSON.stringify(args);
    }

    $.post('/plugins/callback', pdata, function(data) {
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


function dtFileList(){
    dtPost('file_list', '', {}, function(data){
        var rdata = $.parseJSON(data.data);
        var alist = rdata.data;

        if (alist.length == 0){
            var em ='<li class="data-file-list" style="text-align: center;">无数据</li>';
            $('#file_list .list').html(em);
            return;
        }

        var tli = '';
        for (var i = 0; i < alist.length; i++) {
            if (i==0){
                tli +='<li title="双击打开浏览"  class="data-file-list active" data-index="'+i+'" data-file="'+alist[i]['name']+'">\
                    <span class="file">'+alist[i]['name']+'</span>\
                    <span class="tootls">\
                        <span class="glyphicon glyphicon-link" aria-hidden="true" title="外部连接"></span>\
                        <span class="glyphicon glyphicon-trash" aria-hidden="true" title="删除"></span>\
                    </span>\
                </li>';
            } else{
                tli +='<li class="data-file-list" data-index="'+i+'" data-file="'+alist[i]['name']+'">\
                    <span class="file">'+alist[i]['name']+'</span>\
                    <span class="tootls">\
                        <span class="glyphicon glyphicon-link" aria-hidden="true" title="外部连接"></span>\
                        <span class="glyphicon glyphicon-trash" aria-hidden="true" title="删除"></span>\
                    </span>\
                </li>';
            }
        }

        $('#file_list .list').html(tli);

        dtGetFile(alist[0]['name']);
        $('#file_list li .file').click(function(){
            $('#file_list li').removeClass('active');
            $(this).parent().addClass('active');
            var i = $(this).parent().data('index');
            dtGetFile(alist[i]['name']);
        });


        $('#file_list li .glyphicon-link').click(function(){
           var i = $(this).parent().parent().data('index');
           var abs_p = alist[i]['abs_path'];

           var durl = '/files/download?filename='+abs_p;
           window.open(durl);
        });

        $('#file_list li .glyphicon-trash').click(function(){
            var i = $(this).parent().parent().data('index');
            var f = alist[i]['name'];
            dtPost('remove_file_path', '',{file:f}, function(rdata){
                var rdata = $.parseJSON(rdata.data);
                layer.msg(rdata['msg'],{icon:rdata['status']?1:2,time:2000});
                if (rdata.status){
                    dtFileList();
                }
            });
        });
    });
}

function dtGetFile(file){
    dtPost('get_file_path', '', {file:file}, function(data){
        var rdata = $.parseJSON(data.data);
        // console.log(rdata);
        if (!rdata.status){
            layer.msg(rdata.msg,{icon:0,time:2000,shade: [2, '#000']});
            return;
        }
        var durl = '/files/download?filename='+rdata.data;
        $('#flame_graph .tab-con .tab-block').attr('src',durl);
    });
}