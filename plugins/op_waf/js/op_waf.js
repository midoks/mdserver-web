
function owPost(method, args, callback){
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });
    $.post('/plugins/run', {name:'op_waf', func:method, args:JSON.stringify(args)}, function(data) {
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


function getRuleByName(rule_name, callback){
    owPost('get_rule', {rule_name:rule_name}, function(data){
        callback(data);
    })
}


function setRequestCode(ruleName, statusCode){
    layer.open({
        type: 1,
        title: "设置响应代码【" + ruleName + "】",
        area: '300px',
        shift: 5,
        closeBtn: 2,
        shadeClose: true,
        content: '<div class="bt-form pd20 pb70">\
                    <div class="line">\
                        <span class="tname">响应代码</span>\
                        <div class="info-r">\
                            <select id="statusCode" class="bt-input-text mr5" style="width:150px;">\
                                <option value="200" '+ (statusCode == 200 ? 'selected' : '') + '>正常(200)</option>\
                                <option value="404" '+ (statusCode == 404 ? 'selected' : '') + '>文件不存在(404)</option>\
                                <option value="403" '+ (statusCode == 403 ? 'selected' : '') + '>拒绝访问(403)</option>\
                                <option value="444" '+ (statusCode == 444 ? 'selected' : '') + '>关闭连接(444)</option>\
                                <option value="500" '+ (statusCode == 500 ? 'selected' : '') + '>应用程序错误(500)</option>\
                                <option value="502" '+ (statusCode == 502 ? 'selected' : '') + '>连接超时(502)</option>\
                                <option value="503" '+ (statusCode == 503 ? 'selected' : '') + '>服务器不可用(503)</option>\
                            </select>\
                        </div>\
                    </div>\
                    <div class="bt-form-submit-btn">\
                        <button type="button" class="btn btn-success btn-sm btn-title" onclick="setState(\''+ ruleName + '\')">确定</button>\
                    </div>\
                </div>'
    });
}

function setState(ruleName){
    var statusCode = $('#statusCode').val();
    owPost('set_obj_status', {obj:ruleName,statusCode:statusCode},function(data){
        var rdata = $.parseJSON(data.data);
        if (rdata.status){
            layer.msg(rdata.msg,{icon:0,time:2000,shade: [0.3, '#000']});
            wafGloabl();
        } else {
            layer.msg('设置失败!',{icon:0,time:2000,shade: [0.3, '#000']});
        }
    });
}

function setObjOpen(ruleName){
    owPost('set_obj_open', {obj:ruleName},function(data){
        var rdata = $.parseJSON(data.data);
        if (rdata.status){
            layer.msg(rdata.msg,{icon:0,time:2000,shade: [0.3, '#000']});
            wafGloabl();
        } else {
            layer.msg('设置失败!',{icon:0,time:2000,shade: [0.3, '#000']});
        }
    });
}

function setCcRule(cycle, limit, endtime, siteName, increase){
    var incstr = '<li style="color:red;">此处设置仅对当前站点有效。</li>';
    if (siteName == 'undefined') {
        incstr = '<li style="color:red;">此处设置的是初始值，新添加站点时将继承，对现有站点无效。</li>';
    }

    // get_aicc_config(function(res){
        var enhance_mode = '';
        // if(res.status){
        //     enhance_mode = 2;
        // }else{
            if(increase){
                enhance_mode = 1;
            }else{
                enhance_mode = 0;
            }
        // }
        create_l = layer.open({
            type: 1,
            title: "设置CC规则",
            area: '540px',
            closeBtn: 2,
            shadeClose: false,
            content: '<form class="bt-form pd20 pb70">\
                    <div class="line">\
                        <span class="tname">周期</span>\
                        <div class="info-r"><input class="bt-input-text" name="cc_cycle" type="number" value="'+ cycle + '" /> 秒</div>\
                    </div>\
                    <div class="line">\
                        <span class="tname">频率</span>\
                        <div class="info-r"><input class="bt-input-text" name="cc_limit" type="number" value="'+ limit + '" /> 次</div>\
                    </div>\
                    <div class="line">\
                        <span class="tname">封锁时间</span>\
                        <div class="info-r"><input class="bt-input-text" name="cc_endtime" type="number" value="'+ endtime + '" /> 秒</div>\
                    </div>\
                    <div class="line">\
                        <span class="tname">增强模式</span>\
                        <div class="info-r">\
                            <select class="bt-input-text mr5" style="width:80px" name="enhance_mode">\
                                <option value="0" '+ (enhance_mode == 0?'selected':'') +'>关闭</option>\
                                <option value="1" '+ (enhance_mode == 1?'selected':'') +'>开启</option>\
                            </select>\
                        </div>\
                    </div>\
                    <div class="line" style="display:'+ (siteName == 'undefined'?'block':'none') +'">\
                        <span class="tname">四层防御</span>\
                        <div class="info-r">\
                            <select class="bt-input-text mr5" style="width:80px" name="cc_four_defense">\
                                <option value="0">关闭</option>\
                                <option value="1">开启</option>\
                            </select>\
                        </div>\
                    </div>\
                    <ul class="help-info-text c7 ptb10">'+ incstr + '\
                        <li><font style="color:red;">'+ cycle + '</font> 秒内累计请求同一URL超过  <font style="color:red;">' + limit + '</font> 次,触发CC防御,封锁此IP <font style="color:red;">' + endtime + '</font> 秒</li>\
                        <li>请不要设置过于严格的CC规则,以免影响正常用户体验</li>\
                        <li><font style="color:red;">增强模式:CC防御加强版，开启后可能会影响用户体验，建议在用户受到CC攻击时开启。</font></li>\
                        <li><font style="color:red;display:'+ (siteName == 'undefined'?'display: inline-block;':'none') +';">全局应用:全局设置当前CC规则，且覆盖当前全部站点的CC规则</font></li>\
                    </ul>\
                    <div class="bt-form-submit-btn"><button type="button" class="btn btn-danger btn-sm btn_cc_all" style="margin-right:10px;display:'+ (siteName == 'undefined'?'display: inline-block;':'none') +';">全局应用</button><button type="button" class="btn btn-success btn-sm btn_cc_present">应用</button></div>\
                </form>',
                success:function(layero,index){
                    // console.log(siteName == 'undefined');
                    // //<option value="2" '+ (enhance_mode == 2?'selected':'') +' style="'+ (siteName != 'undefined' && enhance_mode != 2?'display:none;':'') +'">自动</option>\
                    // if($('[name="enhance_mode"]').val() == 2 && siteName != 'undefined'){
                    //     $('[name="enhance_mode"]').attr('disabled','disabled');
                    // }
                    // get_stop_ip(function(rdata){
                    //     $('[name="cc_four_defense"]').val(rdata.status?'1':'0');
                    // });
                    // $('[name="cc_four_defense"]').change(function(){
                    //     var _val = $(this).val();
                    //     if(_val == '0'){
                    //         set_stop_ip_stop(function(res){
                    //             layer.msg(res.msg,{icon:res.status?1:2});
                    //         });
                    //     }else{
                    //         set_stop_ip(function(res){
                    //             layer.msg(res.msg,{icon:res.status?1:2});
                    //         });
                    //     }
                    // });
                    // $('.btn_cc_all').click(function(){
                    //     save_cc_rule(siteName,1,$('[name="enhance_mode"]').val());
                    //     layer.close(index);
                    // });
                    // $('.btn_cc_present').click(function(){
                    //     save_cc_rule(siteName,0,$('[name="enhance_mode"]').val());
                    //     layer.close(index);
                    // });
                }
        });
    // });

}


//设置retry规则
function setRetry(retry_cycle, retry, retry_time, siteName) {
    layer.open({
        type: 1,
        title: "设置恶意容忍规则",
        area: '500px',
        closeBtn: 2,
        shadeClose: false,
        content: '<form class="bt-form pd20 pb70">\
                <div class="line">\
                    <span class="tname">周期</span>\
                    <div class="info-r"><input class="bt-input-text" name="retry_cycle" type="number" value="'+ retry_cycle + '" /> 秒</div>\
                </div>\
                <div class="line">\
                    <span class="tname">频率</span>\
                    <div class="info-r"><input class="bt-input-text" name="retry" type="number" value="'+ retry + '" /> 次</div>\
                </div>\
                <div class="line">\
                    <span class="tname">封锁时间</span>\
                    <div class="info-r"><input class="bt-input-text" name="retry_time" type="number" value="'+ retry_time + '" /> 秒</div>\
                </div>\
                <ul class="help-info-text c7 ptb10">\
                    <li><font style="color:red;">'+ retry_cycle + '</font> 秒内累计恶意请求超过  <font style="color:red;">' + retry + '</font> 次,封锁 <font style="color:red;">' + retry_time + '</font> 秒</li>\
                    <li><font style="color:red;">全局应用:全局设置当前恶意容忍规则，且覆盖当前全部站点的恶意容忍规则</li>\
                </ul>\
                <div class="bt-form-submit-btn"><button type="button" class="btn btn-danger btn-sm btn_retry_all" style="margin-right:10px;display:'+ (siteName == undefined?'inline-block;':'none') +';">全局应用</button><button type="button" class="btn btn-success btn-sm btn_retry_present">应用</button></div>\
            </form>',
        success:function(){
            $('.btn_retry_all').click(function(){
                saveRetry(siteName,1);
            });
            $('.btn_retry_present').click(function(){
                saveRetry(siteName,0);
            });
        }
    });
}


//保存retry规则
function saveRetry(siteName,type) {
    var pdata = {
        siteName: siteName,
        retry: $("input[name='retry']").val(),
        retry_time: $("input[name='retry_time']").val(),
        retry_cycle: $("input[name='retry_cycle']").val(),
        is_open_global:type
    }

    var act = 'set_retry';
    if (siteName != undefined) act = 'set_site_retry';
    var loadT = layer.msg('正在保存，请稍候..', { icon: 16, time: 0 });
    $.post('/plugin?action=a&name=btwaf&s=' + act, pdata, function (rdata) {
        layer.close(loadT);
        if (rdata.status) {
            layer.close(create_l);
            if (siteName != 'undefined') {
                site_waf_config(siteName, 1);
            } else {
                wafconfig();
            }
        }
        layer.msg(rdata.msg, { icon: rdata.status ? 1 : 2 });
    });
}



//URL白名单
function urlWhite(type) {
    if (type == undefined) {
        layer.open({
            type: 1,
            title: "管理URL白名单",
            area: ['500px', '400px'],
            closeBtn: 2,
            shadeClose: false,
            content: '<div class="tab_list"><div class="tab_block active">标准模式-URL白名单</div><div class="tab_block">增强模式—URL白名单</div></div>\
                <div class="pd15">\
                    <div class="url_block">\
                        <div style="border-bottom:#ccc 1px solid;margin-bottom:10px;padding-bottom:10px">\
                            <input class="bt-input-text" name="url_white_address" type="text" value="" style="width:400px;margin-right:15px;margin-left:5px" placeholder="URL地址,支持正则表达式">\
                            <button class="btn btn-success btn-sm va0 pull-right" onclick="add_url_white();">添加</button>\
                        </div>\
                        <div class="divtable">\
                            <div id="urlWhite" style="max-height:300px;overflow:auto;border:#ddd 1px solid">\
                                <table class="table table-hover" style="border:none">\
                                    <thead>\
                                        <tr>\
                                            <th>URL</th>\
                                            <th style="text-align: right;">操作</th>\
                                        </tr>\
                                    </thead>\
                                    <tbody id="url_white_con" class="gztr"></tbody>\
                                </table>\
                            </div>\
                            <div class="btn-list">\
                                <button class="btn btn-success btn-sm va0 mr5 mt10" onclick="file_input(\'url_white\')" >导入</button>\
                                <button class="btn btn-success btn-sm va0 mt10" onclick="output_data(\'url_white\')">导出</button>\
                            </div>\
                        </div>\
                    </div>\
                    <div class="url_block" style="display:none">\
                        <div style="border-bottom:#ccc 1px solid;margin-bottom:10px;padding-bottom:10px">\
                            <input class="bt-input-text" name="url_increase_white_address" type="text" value="" style="width:400px;margin-right:15px;margin-left:5px" placeholder="URL地址,支持正则表达式">\
                            <button class="btn btn-success btn-sm va0 pull-right add_increase_white_event" >添加</button>\
                        </div>\
                        <div class="divtable">\
                            <div id="url_increase_white" style="max-height:300px;overflow:auto;border:#ddd 1px solid">\
                                <table class="table table-hover" style="border:none">\
                                    <thead>\
                                        <tr>\
                                            <th>URL</th>\
                                            <th style="text-align: right;">操作</th>\
                                        </tr>\
                                    </thead>\
                                    <tbody id="url_increase_white_con" class="gztr"></tbody>\
                                </table>\
                            </div>\
                        </div>\
                    </div>\
                    <ul class="help-info-text c7">\
                        <li>所有规则对白名单中的URL无效,包括IP黑名单和URL黑名单</li>\
                    </ul></div>',
            success:function(layero,index){
                $('.tab_list .tab_block').click(function(){
                    var index = $(this).index();
                    $(this).addClass('active').siblings().removeClass('active');
                    $('.url_block').eq(index).show().siblings().hide();
                    if(index == 1) {get_golbls_cc();}
                });
                $('.add_increase_white_event').click(function(){
                    var _val = $('[name="url_increase_white_address"]').val();
                    if(_val == ''){
                        layer.msg('URL规则不能为空!');
                        return false;
                    }
                    add_golbls_cc({text:_val},function(res){
                        if(res.status){
                            get_golbls_cc(function(){
                                if(res.status) get_golbls_cc(function(){
                                    layer.msg(res.msg,{icon:res.status?1:2});
                                });
                            });
                            $('[name="url_increase_white_address"]').val('');
                        }
                    });
                });
                $('#url_increase_white_con').on('click','.del_golbls_cc',function(){
                    var _val = $(this).attr('data-val');
                    del_golbls_cc({text:_val},function(res){
                        if(res.status) get_golbls_cc(function(){
                            layer.msg(res.msg,{icon:res.status?1:2});
                        });
                    });
                });
            }
        });
        tableFixed("urlWhite");
    }


    getRuleByName('url_white', function(data){
        var tmp = $.parseJSON(data.data);
        var rdata = $.parseJSON(tmp.data);
        console.log(rdata);
        var tbody = ''
        for (var i = 0; i < rdata.length; i++) {
            tbody += '<tr>\
                    <td>'+ rdata[i] + '</td>\
                    <td class="text-right"><a class="btlink" onclick="remove_url_white('+ i + ')">删除</a></td>\
                </tr>'
        }
        $("#url_white_con").html(tbody);
    });
}


//设置规则
function setObjConf(ruleName, type) {
    if (type == undefined) {
        create_l = layer.open({
            type: 1,
            title: "编辑规则【" + ruleName + "】",
            area: ['700px', '530px'],
            closeBtn: 2,
            shadeClose: false,
            content: '<div class="pd15">\
                <div style="border-bottom:#ccc 1px solid;margin-bottom:10px;padding-bottom:10px">\
                <input class="bt-input-text" name="ruleValue" type="text" value="" style="width:470px;margin-right:12px;" placeholder="规则内容,请使用正则表达式">\
                <input class="bt-input-text mr5" name="rulePs" type="text" style="width:120px;" placeholder="描述">\
                <button class="btn btn-success btn-sm va0 pull-right" onclick="add_rule(\''+ ruleName + '\');">添加</button>\</div>\
                <div class="divtable">\
                <div id="jc-file-table" class="table_head_fix" style="max-height:300px;overflow:auto;border:#ddd 1px solid">\
                <table class="table table-hover" style="border:none">\
                    <thead>\
                        <tr>\
                            <th width="360">规则</th>\
                            <th>说明</th>\
                            <th>操作</th>\
                            <th style="text-align: right;">状态</th>\
                        </tr>\
                    </thead>\
                    <tbody id="set_obj_conf_con" class="gztr"></tbody>\
                </table>\
                </div>\
            </div>\
            <ul class="help-info-text c7 ptb10">\
                <li style="color:red;">注意:如果您不了解正则表达式,请不要随意修改规则内容</li>\
                <li>您可以添加或修改规则内容,但请使用正则表达式</li>\
                <li>内置规则允许修改,但不可以直接删除,您可以设置规则状态来定义防火墙是否使用此规则</li>\
            </ul></div>'
        });
        tableFixed("jc-file-table")
    }
    var loadT = layer.msg('正在获取配置规则，请稍候..', { icon: 16, time: 0 });
    $.post('/plugin?action=a&name=btwaf&s=get_rule', { ruleName: ruleName }, function (rdata) {
        layer.close(loadT);
        var tbody = ''
        for (var i = 0; i < rdata.length; i++) {
            var removeRule = ''
            if (rdata[i][3] != 0) removeRule = ' | <a class="btlink" onclick="remove_rule(\'' + ruleName + '\',' + i + ')">删除</a>';
            tbody += '<tr>\
                    <td class="rule_body_'+ i + '">' + rdata[i][1] + '</td>\
                    <td class="rule_ps_'+ i + '">' + rdata[i][2] + '</td>\
                    <td class="rule_modify_'+ i + '"><a class="btlink" onclick="modify_rule(' + i + ',\'' + ruleName + '\')">编辑</a>' + removeRule + '</td>\
                    <td class="text-right">\
                        <div class="pull-right">\
                        <input class="btswitch btswitch-ios" id="closeua_'+ i + '" type="checkbox" ' + (rdata[i][0] ? 'checked' : '') + '>\
                        <label class="btswitch-btn" style="width:2.0em;height:1.2em;margin-bottom: 0" for="closeua_'+ i + '" onclick="set_rule_state(\'' + ruleName + '\',' + i + ')"></label>\
                        </div>\
                    </td>\
                </tr>'
        }
        $("#set_obj_conf_con").html(tbody)
    });
}

function wafScreen(){

    owPost('waf_srceen', {}, function(data){
        var rdata = $.parseJSON(data.data);
        console.log(rdata);

        var con = '<div class="wavbox alert alert-success" style="margin-right:16px">总拦截<span>'+rdata.total+'</span>次</div>';
        con += '<div class="wavbox alert alert-info" style="margin-right:16px">安全防护<span>0</span>天</div>';

        con += '<div class="screen">\
            <div class="line"><span class="name">POST渗透</span><span class="val">'+rdata.rules.post+'</span></div>\
            <div class="line"><span class="name">GET渗透</span><span class="val">0</span></div>\
            <div class="line"><span class="name">CC攻击</span><span class="val">'+rdata.rules.cc+'</span></div>\
            <div class="line"><span class="name">恶意User-Agent</span><span class="val">'+rdata.rules.user_agent+'</span></div>\
            <div class="line"><span class="name">Cookie渗透</span><span class="val">'+rdata.rules.cookie+'</span></div>\
            <div class="line"><span class="name">恶意扫描</span><span class="val">0</span></div>\
            <div class="line"><span class="name">恶意HEAD请求</span><span class="val">0</span></div>\
            <div class="line"><span class="name">URI自定义拦截</span><span class="val">0</span></div>\
            <div class="line"><span class="name">URI保护</span><span class="val">0</span></div>\
            <div class="line"><span class="name">恶意文件上传</span><span class="val">0</span></div>\
            <div class="line"><span class="name">禁止的扩展名</span><span class="val">0</span></div>\
            <div class="line"><span class="name">禁止PHP脚本</span><span class="val">0</span></div>\
            </div>';

        con += '<div style="width:660px;"><ul class="help-info-text c7">\
            <li>在此处关闭防火墙后,所有站点将失去保护</li>\
            <li>网站防火墙会使nginx有一定的性能损失(&lt;5% 10C静态并发测试结果)</li>\
            <li>网站防火墙仅主要针对网站渗透攻击,暂时不具备系统加固功能</li>\
            </ul></div>';

        $(".soft-man-con").html(con);
    });
}


function wafGloabl(){
    owPost('waf_conf', {}, function(data){
        var rdata = $.parseJSON(data.data);

        var con = '<div class="divtable">\
            <table class="table table-hover waftable">\
                <thead><tr><th width="18%">名称</th>\
                <th width="44%">描述</th>\
                <th width="10%">响应</th>\
                <th style="text-align: center;" width="10%">状态</th>\
                <th style="text-align: right;">操作</th></tr>\
                </thead>\
                <tbody>\
                    <tr><td>CC防御</td>\
                        <td>防御CC攻击，具体防御参数请到站点配置中调整</td>\
                        <td><a class="btlink" onclick="setRequestCode(\'cc\','+rdata.cc.status+')">'+rdata.cc.status+'</a></td>\
                        <td><div class="ssh-item">\
                            <input class="btswitch btswitch-ios" id="closecc" type="checkbox" '+(rdata.cc.open ? 'checked' : '')+'>\
                            <label class="btswitch-btn" for="closecc" onclick="setObjOpen(\'cc\')"></label></div>\
                        </td>\
                        <td class="text-right"><a class="btlink" onclick="setCcRule('+rdata.cc.cycle+','+rdata.cc.limit+','+rdata.cc.endtime+',\'undefined\','+rdata.cc.increase+')">初始规则</a></td>\
                    </tr>\
                    <tr>\
                        <td>恶意容忍度</td>\
                        <td>封锁连续恶意请求，请到站点配置中调整容忍阈值</td>\
                        <td><a class="btlink" onclick="setRequestCode(\'cc\','+ rdata.cc.status + ')">' + rdata.cc.status + '</a></td>\
                        <td style="text-align: center;">--</td>\
                        <td class="text-right"><a class="btlink" onclick="setRetry('+ rdata.retry_cycle + ',' + rdata.retry + ',' + rdata.retry_time + ')">初始规则</a></td>\
                    </tr>\
                    <tr>\
                        <td>GET-URI过滤</td>\
                        <td>'+ rdata.get.ps + '</td>\
                        <td><a class="btlink" onclick="setRequestCode(\'get\',' + rdata.get.status + ')">' + rdata.get.status + '</a></td>\
                        <td><div class="ssh-item">\
                            <input class="btswitch btswitch-ios" id="closeget" type="checkbox" '+ (rdata.get.open ? 'checked' : '') + '>\
                            <label class="btswitch-btn" for="closeget" onclick="setObjOpen(\'get\')"></label>\
                        </div></td>\
                        <td class="text-right"><a class="btlink" onclick="setObjConf(\'url\')">规则</a> | <a class="btlink" href="javascript:;" onclick="onlineEditFile(0,\''+rdata['reqfile_path']+'/get.html\')">响应内容</a></td>\
                    </tr>\
                    <tr>\
                        <td>GET-参数过滤</td><td>'+ rdata.get.ps + '</td><td><a class="btlink" onclick="setRequestCode(\'get\',' + rdata.get.status + ')">' + rdata.get.status + '</a></td><td><div class="ssh-item">\
                            <input class="btswitch btswitch-ios" id="closeget" type="checkbox" '+ (rdata.get.open ? 'checked' : '') + '>\
                            <label class="btswitch-btn" for="closeget" onclick="setObjOpen(\'get\')"></label>\
                        </div></td><td class="text-right"><a class="btlink" onclick="set_obj_conf(\'args\')">规则</a> | <a class="btlink" href="javascript:;" onclick="onlineEditFile(0,\''+rdata['reqfile_path']+'/get.html\')">响应内容</a></td>\
                    </tr>\
                    <tr>\
                        <td>POST过滤</td><td>'+ rdata.post.ps + '</td><td><a class="btlink" onclick="setRequestCode(\'post\',' + rdata.post.status + ')">' + rdata.post.status + '</a></td><td><div class="ssh-item">\
                            <input class="btswitch btswitch-ios" id="closepost" type="checkbox" '+ (rdata.post.open ? 'checked' : '') + '>\
                            <label class="btswitch-btn" for="closepost" onclick="setObjOpen(\'post\')"></label>\
                        </div></td><td class="text-right"><a class="btlink" onclick="set_obj_conf(\'post\')">规则</a> | <a class="btlink" href="javascript:;" onclick="onlineEditFile(0,\''+rdata['reqfile_path']+'/post.html\')">响应内容</a></td>\
                    </tr>\
                    <tr>\
                        <td>User-Agent过滤</td><td>'+ rdata['user-agent'].ps + '</td><td><a class="btlink" onclick="setRequestCode(\'user-agent\',' + rdata['user-agent'].status + ')">' + rdata['user-agent'].status + '</a></td><td><div class="ssh-item">\
                            <input class="btswitch btswitch-ios" id="closeua" type="checkbox" '+ (rdata['user-agent'].open ? 'checked' : '') + '>\
                            <label class="btswitch-btn" for="closeua" onclick="setObjOpen(\'user-agent\')"></label>\
                        </div></td><td class="text-right"><a class="btlink" onclick="set_obj_conf(\'user_agent\')">规则</a> | <a class="btlink" href="javascript:;" onclick="onlineEditFile(0,\''+rdata['reqfile_path']+'/user_agent.html\')">响应内容</a></td>\
                    </tr>\
                    <tr>\
                        <td>Cookie过滤</td><td>'+ rdata.cookie.ps + '</td><td><a class="btlink" onclick="setRequestCode(\'cookie\',' + rdata.cookie.status + ')">' + rdata.cookie.status + '</a></td><td><div class="ssh-item">\
                            <input class="btswitch btswitch-ios" id="closecookie" type="checkbox" '+ (rdata.cookie.open ? 'checked' : '') + '>\
                            <label class="btswitch-btn" for="closecookie" onclick="setObjOpen(\'cookie\')"></label>\
                        </div></td><td class="text-right"><a class="btlink" onclick="set_obj_conf(\'cookie\')">规则</a> | <a class="btlink" href="javascript:;" onclick="onlineEditFile(0,\''+rdata['reqfile_path']+'/cookie.html\')">响应内容</a></td>\
                    </tr>\
                    <tr>\
                        <td>常见扫描器</td><td>'+ rdata.scan.ps + '</td><td><a class="btlink" onclick="setRequestCode(\'scan\',' + rdata.scan.status + ')">' + rdata.scan.status + '</a></td><td><div class="ssh-item">\
                            <input class="btswitch btswitch-ios" id="closescan" type="checkbox" '+ (rdata.scan.open ? 'checked' : '') + '>\
                            <label class="btswitch-btn" for="closescan" onclick="setObjOpen(\'scan\')"></label>\
                        </div></td><td class="text-right"><a class="btlink" onclick="scan_rule()">设置</a></td>\
                    </tr>\
                    <tr>\
                        <td>IP白名单</td><td>所有规则对IP白名单无效</td><td style="text-align: center;">--</td>\
                        <td style="text-align: center;">--</td>\
                        <td class="text-right"><a class="btlink" onclick="ip_white()">设置</a></td>\
                    </tr>\
                    <tr>\
                        <td>IP黑名单</td><td>禁止访问的IP</td><td><a class="btlink" onclick="setRequestCode(\'cc\','+ rdata.cc.status + ')">' + rdata.cc.status + '</a></td>\
                        <td style="text-align: center;">--</td>\
                        <td class="text-right"><a class="btlink" onclick="ip_black()">设置</a></td>\
                    </tr>\
                    <tr>\
                        <td>URL白名单</td><td>大部分规则对URL白名单无效</td><td style="text-align: center;">--</td>\
                        <td style="text-align: center;">--</td>\
                        <td class="text-right"><a class="btlink" onclick="urlWhite()">设置</a></td>\
                    </tr>\
                    <tr>\
                        <td>URL黑名单</td><td>禁止访问的URL地址</td><td><a class="btlink" onclick="setRequestCode(\'get\','+ rdata.get.status + ')">' + rdata.get.status + '</a></td>\
                        <td style="text-align: center;">--</td>\
                        <td class="text-right"><a class="btlink" onclick="url_black()">设置</a></td>\
                    </tr>\
                    <tr>\
                        <td>其它</td><td>'+ rdata.other.ps + '</td><td>--</td>\
                        <td style="text-align: center;">--</td>\
                        <td class="text-right"><a class="btlink" href="javascript:;" onclick="onlineEditFile(0,\''+rdata['reqfile_path']+'/other.html\')">响应内容</a></td>\
                    </tr>\
                </tbody>\
            </table>\
            </div>';


        con += '<div style="width:645px;margin-top:10px;"><ul class="help-info-text c7">\
            <li>继承: 全局设置将在站点配置中自动继承为默认值</li>\
            <li>优先级: IP白名单>IP黑名单>URL白名单>URL黑名单>CC防御>禁止国外IP访问>User-Agent>URI过滤>URL参数>Cookie>POST</li>\
            </ul></div>';
        $(".soft-man-con").html(con);
    });
}


function wafSite(){
    var con = '<div class="divtable">\
        <table class="table table-hover waftable" style="color:#fff;">\
            <thead>\
                <tr><th width="18%">站点</th>\
                <th>GET</th>\
                <th>POST</th>\
                <th>UA</th>\
                <th>Cookie</th>\
                <th>CDN</th>\
                <th>CC</th>\
                <th>状态</th>\
                <th>操作</th></tr>\
            </thead>\
        </table>\
        </div>';
    $(".soft-man-con").html(con);
}



function wafHistory(){
    var con = '<button class="btn btn-success btn-sm" onclick="UncoverAll()">解封所有</button>';
    con += '<div class="divtable mt10">\
        <table class="table table-hover waftable" style="color:#fff;">\
            <thead><tr><th width="18%">开始时间</th>\
            <th width="44%">IP</th>\
            <th width="10%">站点</th>\
            <th width="10%">封锁原因</th>\
            <th width="10%">封锁时长</th>\
            <th style="text-align: center;" width="10%">状态</th>\
            </thead>\
        </table>\
        </div>';
    $(".soft-man-con").html(con);
}


function wafLogs(){
    var con = '<div class="divtable">\
        <table class="table table-hover waftable" style="color:#fff;">\
            <thead><tr><th width="18%">名称</th>\
            <th width="44%">描述</th>\
            <th width="10%">响应</th>\
            <th style="text-align: center;" width="10%">状态</th>\
            <th style="text-align: right;">操作</th></tr>\
            </thead>\
        </table>\
        </div>';    
    $(".soft-man-con").html(con);
}
