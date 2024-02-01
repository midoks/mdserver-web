$(document).ready(function(){
    var tag = $.getUrlParam('tag');
    if(tag == 'data_query'){
        initDataQuery();
    }
});

function redisPostCB(method, args, callback){
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });

    var req_data = {};
    req_data['name'] = 'data_query';
    req_data['func'] = method;
    req_data['script']='nosql_redis';
    args['version'] = '';
 
    if (typeof(args) == 'string' && args == ''){
        req_data['args'] = JSON.stringify(toArrayObject(args));
    } else {
        req_data['args'] = JSON.stringify(args);
    }

    $.post('/plugins/callback', req_data, function(data) {
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

function mgdbPostCB(method, args, callback){
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });

    var req_data = {};
    req_data['name'] = 'data_query';
    req_data['func'] = method;
    req_data['script']='nosql_mongodb';
    args['version'] = '';
 
    if (typeof(args) == 'string' && args == ''){
        req_data['args'] = JSON.stringify(toArrayObject(args));
    } else {
        req_data['args'] = JSON.stringify(args);
    }

    $.post('/plugins/callback', req_data, function(data) {
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


function selectTab(tab = 'redis'){
    $('.tab-view-box .tab-con').addClass('hide').removeClass('show').removeClass('w-full');
    $('#'+tab).removeClass('hide').addClass('w-full');
}

function showInstallLayer(){
    $('.mask_layer').css('display','block');
}

function closeInstallLayer(){
    $('.mask_layer').css('display','none');
}

function initTabFunc(tab){
    switch(tab){
        case 'redis':initTabRedis();break;
        case 'mongodb':initTabMongodb();break;
    }
}

function initDataQuery(){
    var tab = $('#cutTab .tabs-item.active').data('name');
    initTabFunc(tab);
    $('#cutTab .tabs-item').click(function(){
        var tab = $(this).data('name');
        $('#cutTab .tabs-item').removeClass('active');
        $(this).addClass('active');
        selectTab(tab);
        initTabFunc(tab);
    });    
}

function initTabRedis(){
    //渲染数据
    redisGetList();

    $('#redis_add_key').unbind('click').click(function(){
        redisAdd();
    });

    //搜索
    $('#redis_ksearch').unbind('click').keyup(function(e){
        if (e.keyCode == 13){
            var val = $(this).val();
            if (val == ''){
                layer.msg('搜索不能为空!',{icon:7});
                return;
            }
            redisGetKeyList(1, val);
        }
    });

    $('#redis_ksearch_span').unbind('click').click(function(){
        var val = $('#redis_ksearch').val();
        if (val == ''){
            layer.msg('搜索不能为空!',{icon:7});
            return;
        }
        redisGetKeyList(1, val);
    });

    //批量删除
    $('#redis_batch_del').unbind('click').click(function(){
        redisBatchDel();
    });

    //清空所有
    $('#redis_clear_all').unbind('click').click(function(){
        redisBatchClear();
    });

    readerTableChecked();
}

function initTabMongodb(){
    //渲染数据
    mongodbGetList();
}

// ------------------------- mongodb start ---------------------------------
function mongodbGetSid(){
    return 0;
}


function mongodbGetList(){
    var sid = mongodbGetSid();
    mgdbPostCB('get_db_list',{'sid':sid} ,function(rdata){
        if (rdata.data.status){
            var list = rdata.data.data;
            var content = '';
            for (var i = 0; i < list.length; i++) {
                if (i == 0){
                    content += '<span data-id="'+i+'" class="on">'+list[i]['name'] + '('+ list[i]['keynum'] +')</span>'; 
                } else {
                    content += '<span data-id="'+i+'">'+list[i]['name'] + '('+ list[i]['keynum'] +')</span>'; 
                }
            }
            $('#redis_list_tab .tab-nav').html(content);

            $('#redis_list_tab .tab-nav span').click(function(){
                $('#redis_list_tab .tab-nav span').removeClass('on');
                $(this).addClass('on');
                redisGetKeyList(1);
            });
            // redisGetKeyList(1);
        } else {
            showInstallLayer();
        }
    });
}
// ------------------------- mongodb end ---------------------------------

// ------------------------- redis start ---------------------------------
function redisGetSid(){
    return 0;
}

function redisGetIdx(){
    return $('#redis_list_tab .tab-nav span.on').data('id');
}

function redisGetList(){
    var sid = redisGetSid();
    redisPostCB('get_list',{'sid':sid} ,function(rdata){
        if (rdata.data.status){
            var list = rdata.data.data;
            var content = '';
            for (var i = 0; i < list.length; i++) {
                if (i == 0){
                    content += '<span data-id="'+i+'" class="on">'+list[i]['name'] + '('+ list[i]['keynum'] +')</span>'; 
                } else {
                    content += '<span data-id="'+i+'">'+list[i]['name'] + '('+ list[i]['keynum'] +')</span>'; 
                }
            }
            $('#redis_list_tab .tab-nav').html(content);

            $('#redis_list_tab .tab-nav span').click(function(){
                $('#redis_list_tab .tab-nav span').removeClass('on');
                $(this).addClass('on');
                redisGetKeyList(1);
            });
            redisGetKeyList(1);
        } else {
            showInstallLayer();
        }
    });
}

function redisGetKeyList(page,search = ''){

    var args = {};
    args['sid'] = redisGetSid();
    args['idx'] = redisGetIdx();
    args['p'] = page;
    args['search'] = search;

    var input_search_val = $('#redis_ksearch').val();
    if (input_search_val!=''){
        args['search'] = input_search_val;
    }

    redisPostCB('get_dbkey_list', args, function(rdata){
        if (rdata.data.status){
            var data = rdata.data.data.data;
            var tbody = '';
            for (var i = 0; i < data.length; i++) {


                tbody += '<tr>';
                tbody += "<td><input type='checkbox' class='check' name='id' title='"+data[i].name+"' onclick='checkSelect();' value='"+data[i].name+"'></td>";
                tbody += '<td style="width:100px;">'+data[i].name+'</td>';
                tbody += '<td><span style="width:100px;" class="size_ellipsis">'+data[i].val+'</span><span data-index="'+i+'" class="ico-copy cursor copy ml5" title="复制值"></span></td>';
                tbody += '<td>'+data[i].type+'</td>';
                tbody += '<td>'+data[i].len+'</td>';


                if (data[i].endtime == -1){
                    tbody += '<td>永久</td>';
                } else {
                    tbody += '<td>'+data[i].endtime+'</td>';
                }
                

                tbody += '<td style="text-align:right; color:#bbb">\
                        <a href="javascript:;" data-index="'+i+'" class="btlink edit" title="编辑">编辑</a> | \
                        <a href="javascript:;" class="btlink" onclick="redisDeleteKey(\''+data[i].name+'\')">删除</a>\
                        </td>';

                tbody += '</tr>';
            }

            // console.log(tbody);
            $('.redis_table_content tbody').html(tbody);
            $('.redis_list_page').html(rdata.data.data.page);


            $('.edit').click(function(){
                var i = $(this).data('index');
                redisEditKv(data[i].name,data[i].val,data[i].endtime);
            });

            $('.copy').click(function(){
                var i = $(this).data('index');
                copyText(data[i].val);
            });

        }
    });
}

function redisDeleteKey(name){
    layer.confirm('确定要删除?', {btn: ['确定', '取消']}, function(){
        var data = {};
        data['idx'] = redisGetIdx();
        data['sid'] = redisGetSid();
        data['name'] = name;
        redisPostCB('del_val', data, function(rdata){
            if (rdata.data.status){
            showMsg(rdata.data.msg,function(){
                redisGetList();
            },{icon: rdata.data.status ? 1 : 2}, 2000);
        }
        });
    });
}

function redisAdd(){
    layer.open({
        type: 1,
        area: '480px',
        title: '添加Key至服务器',
        closeBtn: 1,
        shift: 0,
        shadeClose: false,
        btn:['确定','取消'],
        content: "<form class='bt-form pd20'>\
            <div class='line'>\
                <span class='tname'>数据库</span>\
                <div class='info-r c4'>\
                    <select name='idx' class='bt-input-text' style='width:260px;'>\
                        <option value='0'>DB(0)</option>\
                    </select>\
                </div>\
            </div>\
            <div class='line'>\
                <span class='tname'>键</span>\
                <div class='info-r c4'>\
                    <input class='bt-input-text' type='text' name='key' placeholder='键' style='width:260px;'/>\
                </div>\
            </div>\
            <div class='line'>\
                <span class='tname'>值</span>\
                <div class='info-r c4'>\
                    <textarea class='bt-input-text' name='val' style='width:260px;height:100px;'/></textarea>\
                </div>\
            </div>\
            <div class='line'>\
                <span class='tname'>有效期</span>\
                <div class='info-r c4'>\
                    <input class='bt-input-text mr5' type='number' name='endtime' value='60' style='width:260px;'/>\
                </div>\
            </div>\
            <div class='line'>\
                <div>\
                    <ul class='help-info-text c7' style='margin-left:30px;'><li>有效期为0表示永久</li>\
                </div>\
            </div>\
        </form>",
        success:function(){
            var db_list = $('#redis_list_tab .tab-nav span');
            var db_list_count = db_list.length;

            var idx_html = '';
            for (var i = 0; i < db_list_count; i++) {
                idx_html += "<option value='"+i+"'>DB("+i+")</option>";
            }
            $('select[name=idx]').html(idx_html);
        },
        yes: function(index){
            var data = {};
            data['idx'] = $('select[name=idx]').val();
            data['sid'] = redisGetSid();
            data['name'] = $('input[name="key"]').val();
            data['val'] = $('textarea[name="val"]').val();
            data['endtime'] = $('input[name="endtime"]').val();

            redisPostCB('set_kv', data ,function(rdata){
                if (rdata.data.status){
                    showMsg(rdata.data.msg,function(){
                        layer.close(index);
                        redisGetList();
                    },{icon: rdata.data.status ? 1 : 2}, 1000);
                }
            });
        }
    });
}

function redisEditKv(name, val, endtime){
    layer.open({
        type: 1,
        area: '480px',
        title: '编辑['+name+']Key',
        closeBtn: 1,
        shift: 0,
        shadeClose: false,
        btn:['确定','取消'],
        content: "<form class='bt-form pd20'>\
            <div class='line'>\
                <span class='tname'>数据库</span>\
                <div class='info-r c4'>\
                    <select name='idx' class='bt-input-text' style='width:260px;'>\
                        <option value='0'>DB(0)</option>\
                    </select>\
                </div>\
            </div>\
            <div class='line'>\
                <span class='tname'>键</span>\
                <div class='info-r c4'>\
                    <input class='bt-input-text' type='text' name='key' placeholder='键' style='width:260px;'/>\
                </div>\
            </div>\
            <div class='line'>\
                <span class='tname'>值</span>\
                <div class='info-r c4'>\
                    <textarea class='bt-input-text' name='val' style='width:260px;height:100px;'/></textarea>\
                </div>\
            </div>\
            <div class='line'>\
                <span class='tname'>有效期</span>\
                <div class='info-r c4'>\
                    <input class='bt-input-text mr5' type='number' name='endtime' value='60' style='width:260px;'/>\
                </div>\
            </div>\
            <div class='line'>\
                <div>\
                    <ul class='help-info-text c7' style='margin-left:30px;'><li>有效期为0表示永久</li>\
                </div>\
            </div>\
        </form>",
        success:function(){
            var idx = redisGetIdx();
            var idx_html = "<option value='"+idx+"'>DB("+idx+")</option>";
            $('select[name=idx]').html(idx_html).attr('readonly','readonly');
            $('input[name="key"]').val(name).attr('readonly','readonly');
            $('textarea[name="val"]').val(val);

            if (endtime == -1){
                $('input[name="endtime"]').val(0);
            } else {
                $('input[name="endtime"]').val(endtime);
            }            
        },
        yes: function(index){
            var data = {};
            data['idx'] = $('select[name=idx]').val();
            data['sid'] = redisGetSid();
            data['name'] = $('input[name="key"]').val();
            data['val'] = $('textarea[name="val"]').val();
            data['endtime'] = $('input[name="endtime"]').val();

            redisPostCB('set_kv', data ,function(rdata){
                if (rdata.data.status){
                    showMsg(rdata.data.msg,function(){
                        layer.close(index);
                        redisGetList();
                    },{icon: rdata.data.status ? 1 : 2}, 1000);
                }
            });
        }
    });
}

function redisBatchDel(){
    var keys = [];
    $('input[type="checkbox"].check:checked').each(function () {
        keys.push($(this).val());
    });
    if (keys.length == 0){
        layer.msg('没有选中数据!',{icon:7});
        return;
    } 

    layer.confirm('确定要批量删除?', {btn: ['确定', '取消']}, function(){
        var data = {};
        data['idx'] = redisGetIdx();
        data['sid'] = redisGetSid();
        data['keys'] = keys;
        redisPostCB('batch_del_val', data, function(rdata){
            if (rdata.data.status){
            showMsg(rdata.data.msg,function(){
                if (rdata.data.status){
                   redisGetList(); 
                }
            },{icon: rdata.data.status ? 1 : 2}, 2000);
        }
        });
    });
}

function redisBatchClear(){
    var xm_db_list;
    layer.open({
        type: 1,
        area: ['480px','180px'],
        title: '清空【本地服务器】数据库',
        closeBtn: 1,
        shift: 0,
        shadeClose: false,
        btn:['确定','取消'],
        content: "<form class='bt-form pd20'>\
            <div class='line'>\
                <span class='tname'>选择数据库</span>\
                <div class='info-r'>\
                    <div id='select_db'></div>\
                </div>\
            </div>\
        </form>",
        success:function(l,i){
            var db_list = $('#redis_list_tab .tab-nav span');
            var db_list_count = db_list.length;

            var idx_db = [];
            for (var i = 0; i < db_list_count; i++) {
                var t = {};
                t['name'] = "DB("+i+")";
                t['value'] = i;
                idx_db.push(t);
            }

            xm_db_list = xmSelect.render({
                el: '#select_db', 
                repeat: true,
                toolbar: {show: true},
                data: idx_db,
            });

            $(l).find('.layui-layer-content').css('overflow','visible');
        },
        yes: function(index){
            var xm_db_val = xm_db_list.getValue('value');
            layer.confirm('确定要批量清空?', {btn: ['确定', '取消']}, function(){
                var data = {};
                data['sid'] = redisGetSid();
                data['idxs'] = xm_db_val;
                redisPostCB('clear_flushdb', data, function(rdata){
                    showMsg(rdata.data.msg,function(){
                        if (rdata.data.status){
                           redisGetList();
                           layer.close(index);
                        }
                    },{icon: rdata.data.status ? 1 : 2}, 2000);
                });
            });
        }
    });
}
// ------------------------- redis end ---------------------------------

