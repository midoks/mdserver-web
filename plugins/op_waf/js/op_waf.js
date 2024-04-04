
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

function owPostN(method, args, callback){
    $.post('/plugins/run', {name:'op_waf', func:method, args:JSON.stringify(args)}, function(data) {
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
    });
}


function setRequestCode(ruleName, statusCode){
    layer.open({
        type: 1,
        title: "设置响应代码【" + ruleName + "】",
        area: '300px',
        shift: 5,
        closeBtn: 1,
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

            showMsg(rdata.msg, function(){
                wafGloabl();
            },{icon:1,time:2000,shade: [0.3, '#000']},2000);
        } else {
            layer.msg('设置失败!',{icon:0,time:2000,shade: [0.3, '#000']});
        }
    });
}


//保存CC规则
function saveCcRule(siteName,is_open_global, type) {
    var increase = "0";
    if(type == 2){
        // set_aicc_open('start');
        increase = "0";
    } else {
        // set_aicc_open('stop');
        increase = type;
    }
    increase = "0";
    var pdata = {
        siteName:siteName,
        cycle: $("input[name='cc_cycle']").val(),
        limit: $("input[name='cc_limit']").val(),
        endtime: $("input[name='cc_endtime']").val(),
        is_open_global:is_open_global,
        increase:increase
    }
    console.log(pdata);
    var act = 'set_cc_conf';
    if (siteName != 'undefined') act = 'set_site_cc_conf';

    owPost(act, pdata, function(data){
        var rdata = $.parseJSON(data.data);
        layer.msg(rdata.msg, { icon: rdata.status ? 1 : 2 });
        setTimeout(function(){
            if (siteName != 'undefined') {
                siteWafConfig(siteName, 1);
            } else {
                wafGloabl();
            }
        },1000);
    });
}


function setCcRule(cycle, limit, endtime, siteName, increase){
    var incstr = '<li style="color:red;">此处设置仅对当前站点有效。</li>';
    if (siteName == 'undefined') {
        incstr = '<li style="color:red;">此处设置的是初始值，新添加站点时将继承，对现有站点无效。</li>';
    }
    // <div class="line">\
    //     <span class="tname">增强模式</span>\
    //     <div class="info-r">\
    //         <select class="bt-input-text mr5" style="width:80px" name="enhance_mode">\
    //             <option value="0" '+ (enhance_mode == 0?'selected':'') +'>关闭</option>\
    //             <option value="1" '+ (enhance_mode == 1?'selected':'') +'>开启</option>\
    //         </select>\
    //     </div>\
    // </div>\
    // <div class="line" style="display:'+ (siteName == 'undefined'?'block':'none') +'">\
    //     <span class="tname">四层防御</span>\
    //     <div class="info-r">\
    //         <select class="bt-input-text mr5" style="width:80px" name="cc_four_defense">\
    //             <option value="0">关闭</option>\
    //             <option value="1">开启</option>\
    //         </select>\
    //     </div>\
    // </div>\
    //<li><font style="color:red;">增强模式:CC防御加强版，开启后可能会影响用户体验，建议在用户受到CC攻击时开启。</font></li>\

    create_l = layer.open({
        type: 1,
        title: "设置CC规则",
        area: '540px',
        closeBtn: 1,
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
                <ul class="help-info-text c7 ptb10">'+ incstr + '\
                    <li><font style="color:red;">'+ cycle + '</font> 秒内累计请求同一URL超过  <font style="color:red;">' + limit + '</font> 次,触发CC防御,封锁此IP <font style="color:red;">' + endtime + '</font> 秒</li>\
                    <li>请不要设置过于严格的CC规则,以免影响正常用户体验</li>\
                    <li><font style="color:red;display:'+ (siteName == 'undefined'?'display: inline-block;':'none') +';">全局应用:全局设置当前CC规则，且覆盖当前全部站点的CC规则</font></li>\
                </ul>\
                <div class="bt-form-submit-btn">\
                    <button type="button" class="btn btn-danger btn-sm btn_cc_all" style="margin-right:10px;display:'+ (siteName == 'undefined'?'display: inline-block;':'none') +';">全局应用</button>\
                    <button type="button" class="btn btn-success btn-sm btn_cc_present">应用</button>\
                </div>\
            </form>',
            success:function(layero,index){
                $('.btn_cc_all').click(function(){
                    saveCcRule(siteName,1,$('[name="enhance_mode"]').val());
                });
                $('.btn_cc_present').click(function(){
                    saveCcRule(siteName,0,$('[name="enhance_mode"]').val());
                });
            }
    });
}


//设置retry规则
function setRetry(retry_cycle, retry, retry_time, siteName) {
    create_layer = layer.open({
        type: 1,
        title: "设置恶意容忍规则",
        area: '500px',
        closeBtn: 1,
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
                    <li><font style="color:red;">全局应用:全局设置当前恶意容忍规则，且覆盖当前全部站点的恶意容忍规则</font></li>\
                </ul>\
                <div class="bt-form-submit-btn">\
                    <button type="button" class="btn btn-danger btn-sm btn_retry_all" style="margin-right:10px;display:'+ (siteName == undefined?'inline-block;':'none') +';">全局应用</button>\
                    <button type="button" class="btn btn-success btn-sm btn_retry_present">应用</button>\
                </div>\
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



//设置safe_verify规则
function setSafeVerify(auto, cpu, time, mode,siteName) {
    var svlayer = layer.open({
        type: 1,
        title: "设置强制安全验证",
        area: '500px',
        closeBtn: 1,
        shadeClose: false,
        content: '<form class="bt-form pd20 pb70">\
                <div class="line">\
                    <span class="tname">CPU</span>\
                    <div class="info-r"><input class="bt-input-text" name="cpu" type="number" max-number="100" value="'+ cpu + '" /> %</div>\
                </div>\
                <div class="line">\
                    <span class="tname">通行时间</span>\
                    <div class="info-r">\
                        <input class="bt-input-text" name="time" type="number" value="'+ time + '" /> 秒\
                    </div>\
                </div>\
                <div class="line">\
                    <span class="tname">验证模式</span>\
                    <div class="info-r">\
                        <select class="bt-input-text mr5" style="width:200px" name="mode">\
                        <option value="url" '+(mode=='url'?"selected=selected":"")+'>URL跳转验证</option>\
                        <option value="local" '+(mode=='local'?"selected=selected":"")+'>本地验证</option>\
                        </select>\
                    </div>\
                </div>\
                <div class="line">\
                    <span class="tname">开启自动</span>\
                    <div class="info-r">\
                        <select class="bt-input-text mr5" style="width:80px" name="auto">\
                        <option value="0" '+(auto==false?"selected=selected":"")+'>关闭</option>\
                        <option value="1" '+(auto==true?"selected=selected":"")+'>开启</option>\
                        </select>\
                    </div>\
                </div>\
                <ul class="help-info-text c7 ptb10">\
                    <li><font style="color:red;">全局设置强制安全验证</font></li>\
                    <li>开启自动后:cpu超过['+cpu+'%]后，强制验证。</li>\
                </ul>\
                <div class="bt-form-submit-btn">\
                    <button type="button" class="btn btn-success btn-sm btn_sv_present">应用</button>\
                </div>\
            </form>',
        success:function(index){
            $('.btn_sv_present').click(function(){
                var pdata = {
                    siteName: siteName,
                    cpu: $("input[name='cpu']").val(),
                    auto: $("select[name='auto']").val(),
                    mode: $("select[name='mode']").val(),
                    time: $("input[name='time']").val(),
                }
                var act = 'set_safe_verify';
                owPost(act, pdata, function(data){
                    var rdata = $.parseJSON(data.data);
                    showMsg(rdata.msg, function() {
                       layer.close(svlayer);
                       wafGloabl();
                    },{ icon: rdata.status ? 1 : 2 },1000);
                });
            });   

            
        },
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
    owPost(act, pdata, function(data){
        var rdata = $.parseJSON(data.data);
        layer.msg(rdata.msg, { icon: rdata.status ? 1 : 2 });
        layer.close(create_layer);
        wafGloablRefresh(1000);
    });
}

function addRule(ruleName) {
    var pdata = {
        'ruleValue': $("input[name='ruleValue']").val(),
        'ps': $("input[name='rulePs']").val(),
        'ruleName': ruleName
    }

    owPost('add_rule', pdata, function(data){
        var rdata = $.parseJSON(data.data);
        layer.msg(rdata.msg, { icon: rdata.status ? 1 : 2 });
        if (rdata.status) {
            setTimeout(function(){
                setObjConf(ruleName, 1);
            },1000);
        }
    });
}

function modifyRule(index, ruleName) {
    var ruleValue = $('.rule_body_' + index).text();
    $('.rule_body_' + index).html('<textarea class="bt-input-text" name="rule_body_' + index + '" style="margin: 0px; height: 70px; width: 99%;line-height:20px">' + ruleValue + '</textarea>');
    var rulePs = $('.rule_ps_' + index).text();
    $('.rule_ps_' + index).html('<input class="bt-input-text" type="text" name="rule_ps_' + index + '" value="' + rulePs + '" />');
    $('.rule_modify_' + index).html('<a class="btlink" onclick="modifyRuleSave(' + index + ',\'' + ruleName + '\')">保存</a> | <a class="btlink modr_cancel_' + index + '">取消</a>');
    $(".modr_cancel_" + index).click(function () {
        $('.rule_body_' + index).html(ruleValue);
        $('.rule_ps_' + index).html(rulePs);
        $('.rule_modify_' + index).html('<a class="btlink" onclick="modifyRule(' + index + ',\'' + ruleName + '\')">编辑</a>');
    })
}

function modifyRuleSave(index, ruleName) {
    var pdata = {
        index: index,
        ruleName: ruleName,
        ruleBody: $("textarea[name='rule_body_" + index + "']").val(),
        rulePs: $("input[name='rule_ps_" + index + "']").val()
    }

    owPost('modify_rule', pdata, function(data){
        var rdata = $.parseJSON(data.data);

        layer.msg(rdata.msg, { icon: rdata.status ? 1 : 2 });
        if (rdata.status) {
            setTimeout(function(){
                setObjConf(ruleName, 1);
            },1000);
        }
    });
}

function removeRule(ruleName, index) {
    var pdata = {
        'index': index,
        'ruleName': ruleName
    }
    safeMessage('删除规则', '您真的要删除这条过滤规则吗？', function () {
        owPost('remove_rule', pdata, function(data){
            var rdata = $.parseJSON(data.data);
            layer.msg(rdata.msg, { icon: rdata.status ? 1 : 2 });
            if (rdata.status) {
                setTimeout(function(){
                    setObjConf(ruleName, 1);
                },1000);
            }
        });
    });
}

function setRuleState(ruleName, index) {
    var pdata = {
        'index': index,
        'ruleName': ruleName
    }
    
    owPost('set_rule_state', pdata, function(data){
        var rdata = $.parseJSON(data.data);
        layer.msg(rdata.msg, { icon: rdata.status ? 1 : 2 });
        if (rdata.status) {
            setTimeout(function(){
                setObjConf(ruleName, 1);
            },1000);
        }
    });
}

//设置规则
function setObjConf(ruleName, type) {
    if (type == undefined) {
        create_l = layer.open({
            type: 1,
            title: "编辑规则【" + ruleName + "】",
            area: ['700px', '530px'],
            closeBtn: 1,
            shadeClose: false,
            content: '<div class="pd15">\
                <div style="border-bottom:#ccc 1px solid;margin-bottom:10px;padding-bottom:10px">\
                <input class="bt-input-text" name="ruleValue" type="text" value="" style="width:470px;margin-right:12px;" placeholder="规则内容,请使用正则表达式">\
                <input class="bt-input-text mr5" name="rulePs" type="text" style="width:120px;" placeholder="描述">\
                <button class="btn btn-success btn-sm va0 pull-right" onclick="addRule(\''+ ruleName + '\');">添加</button>\</div>\
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
        tableFixed("jc-file-table");
    }

    getRuleByName(ruleName, function(data){
        var tmp = $.parseJSON(data.data);
        var rdata = $.parseJSON(tmp.data);
        var tbody = ''
        for (var i = 0; i < rdata.length; i++) {
            var removeRule = ''
            if (rdata[i][3] != 0) removeRule = ' | <a class="btlink" onclick="removeRule(\'' + ruleName + '\',' + i + ')">删除</a>';
            tbody += '<tr>\
                    <td class="rule_body_'+ i + '">' + rdata[i][1] + '</td>\
                    <td class="rule_ps_'+ i + '">' + rdata[i][2] + '</td>\
                    <td class="rule_modify_'+ i + '"><a class="btlink" onclick="modifyRule(' + i + ',\'' + ruleName + '\')">编辑</a>' + removeRule + '</td>\
                    <td class="text-right">\
                        <div class="pull-right">\
                        <input class="btswitch btswitch-ios" id="closeua_'+ i + '" type="checkbox" ' + (rdata[i][0] ? 'checked' : '') + '>\
                        <label class="btswitch-btn" style="width:2.0em;height:1.2em;margin-bottom: 0" for="closeua_'+ i + '" onclick="setRuleState(\'' + ruleName + '\',' + i + ')"></label>\
                        </div>\
                    </td>\
                </tr>'
        }
        $("#set_obj_conf_con").html(tbody);
    });
}


//常用扫描器
function scanRule() {

    getRuleByName('scan_black', function(data){
        var tmp = $.parseJSON(data.data);
        var rdata = $.parseJSON(tmp.data);

        create_l = layer.open({
            type: 1,
            title: "常用扫描器过滤规则",
            area: '650px',
            closeBtn: 1,
            shadeClose: false,
            content: '<form class="bt-form pd20 pb70">\
                    <div class="line">\
                        <span class="tname">Header</span>\
                        <div class="info-r"><textarea style="margin: 0px;width:475px;height: 75px;line-height:20px" class="bt-input-text" name="scan_header" >'+ rdata.header + '</textarea></div>\
                    </div>\
                    <div class="line">\
                        <span class="tname">Cookie</span>\
                        <div class="info-r"><textarea style="margin: 0px;width:475px;height: 75px;line-height:20px" class="bt-input-text" name="scan_cookie" >'+ rdata.cookie + '</textarea></div>\
                    </div>\
                    <div class="line">\
                        <span class="tname">Args</span>\
                        <div class="info-r"><textarea style="margin: 0px;width:475px;height: 75px;line-height:20px" class="bt-input-text" name="scan_args" >'+ rdata.args + '</textarea></div>\
                    </div>\
                    <ul class="help-info-text c7 ptb10">\
                        <li>会同时过滤key和value,请谨慎设置</li>\
                        <li>请使用正则表达式,提交前应先备份原有表达式</li>\
                    </ul>\
                    <div class="bt-form-submit-btn">\
                        <button type="button" class="btn btn-success btn-sm btn-title" onclick="saveScanRule()">确定</button>\
                    </div>\
                </form>'
        });
    });
}

//保存扫描器规则
function saveScanRule() {
    pdata = {
        header: $("textarea[name='scan_header']").val(),
        cookie: $("textarea[name='scan_cookie']").val(),
        args: $("textarea[name='scan_args']").val()
    }
    owPost('save_scan_rule', pdata,function(data){
        var rdata = $.parseJSON(data.data);
        layer.msg(rdata.msg, { icon: rdata.status ? 1 : 2 });
        layer.close(create_l);
        wafGloablRefresh(1000);
    });
}

//添加IP段到IP白名单
function addIpWhite() {
    var pdata = {
        start_ip: $("input[name='start_ip']").val(),
        end_ip: $("input[name='end_ip']").val()
    }

    if (pdata['start_ip'].split('.').length < 4 || pdata['end_ip'].split('.').length < 4) {
        layer.msg('起始IP或结束IP格式不正确!');
        return;
    }

    owPost('add_ip_white', pdata, function(data){
        var rdata = $.parseJSON(data.data);
        layer.msg(rdata.msg, { icon: rdata.status ? 1 : 2 });
        if (rdata.status) {
            setTimeout(function(){
               ipWhite(1); 
            },1000);
        }
    });
}

//从IP白名单删除IP段
function removeIpWhite(index) {
    owPost('remove_ip_white', { index: index }, function(data){
        var rdata = $.parseJSON(data.data);
        if (rdata.status) {
            setTimeout(function(){
                ipWhite(1);
            },1000);   
        }
        layer.msg(rdata.msg, { icon: rdata.status ? 1 : 2 });
    });
}


function funDownload(content, filename) {
    // 创建隐藏的可下载链接
    var eleLink = document.createElement('a');
    eleLink.download = filename;
    eleLink.style.display = 'none';
    // 字符内容转变成blob地址
    var blob = new Blob([content]);
    eleLink.href = URL.createObjectURL(blob);
    // 触发点击
    document.body.appendChild(eleLink);
    eleLink.click();
    // 然后移除
    document.body.removeChild(eleLink);
}

function outputLayer(rdata, name, type) {
    window.Load_layer = layer.open({
        type: 1,
        title: type ? "导出数据" : "导入数据",
        area: ['400px', '370px'],
        shadeClose: false,
        content: '<div class="soft-man-con" style="padding:10px;">' +
            '<div class="line">' +
            '<div class="ml0" style="position:relative;" id="focus_tips">' +
            '<textarea class="bt-input-text mr20 config" name="config" style="width: 300px; height: 250px; line-height: 22px; display: none;" id="lead_data">' + (rdata != '' ? JSON.stringify(rdata) : '') + '</textarea>' +
            '<div class="placeholder c9" style="top: 15px; left: 15px; display:' + (rdata == "" ? "block;" : "none;") + '">导入格式如下：' +
            (name == 'ip_white' || name == 'ip_black' ? "[[[127, 0, 0, 1],[127, 0, 0, 255]],[[192, 0, 0, 1],[192, 0, 0, 255]]]" : "[\"^/test\",\"^/web\"]") +
            '</div>' +
            '</div>' +
            '</div>' +
            '<div class="line "><div class="ml0">' +
            (type ? '<button name="btn_save_to" class="btn btn-success btn-sm mr5 btn_save_to" >导出配置</button>' : '<button name="btn_save" class="btn btn-success btn-sm mr5 btn_save">保存</button>') +
            '</div></div>' +
            '</div>',
    });
    var lead_error = CodeMirror.fromTextArea(document.getElementById("lead_data"), {
        mode: 'html',
        matchBrackets: true,
        matchtags: true,
        autoMatchParens: true
    });
    setTimeout(function () {
        $('.btn_save').on('click', function () {
            importData(name, lead_error.getValue(), function(){
                layer.close(window.Load_layer);
                ipWhiteLoadList();
            });
        })
        $('.btn_save_to').on('click', function () {
            funDownload(lead_error.getValue(), name + '.json');
        });
        $('#focus_tips').on('click', function () {
            $('.placeholder').hide();
        });
    }, 100);
}


//导出数据
function outputData(name, callback) {
    var loadT = layer.msg('正在导出数据..', { icon: 16, time: 0 });

    owPost('output_data', { sname: name } , function(data){
        var tmp = $.parseJSON(data.data);
        var rdata = $.parseJSON(tmp.data);
        if (callback) callback(rdata,res);
        outputLayer(rdata, name, true);
    });
}

//导入数据
function importData(name, pdata, callback) {
    owPost('import_data', { sname: name, pdata: pdata } , function(data){
        var rdata = $.parseJSON(data.data);   
        if (callback) callback();
        layer.msg(rdata.msg, { icon: rdata.status ? 1 : 2 });
    });
}

function fileInput(name) {
    outputLayer('', name, false);
}


function ipWhiteLoadList(){
    getRuleByName('ip_white', function(data){
        var tmp = $.parseJSON(data.data);
        var rdata = $.parseJSON(tmp.data);
        var tbody = ''
        for (var i = 0; i < rdata.length; i++) {
            tbody += '<tr>\
                    <td>'+ rdata[i][0].join('.') + '</td>\
                    <td>'+ rdata[i][1].join('.') + '</td>\
                    <td class="text-right"><a class="btlink" onclick="removeIpWhite('+ i + ')">删除</a></td>\
                </tr>'
        }
        $("#ip_white_con").html(tbody);
    });
}
//IP白名单
function ipWhite(type) {
    if (type == undefined) {
        create_l = layer.open({
            type: 1,
            title: "管理IP白名单",
            area: ['500px', '500px'],
            closeBtn: 1,
            shadeClose: false,
            content: '<div class="pd15 ipv4_list">\
                        <div style="border-bottom:#ccc 1px solid;margin-bottom:10px;padding-bottom:10px">\
                            <input class="bt-input-text" name="start_ip" type="text" value="" style="width:180px;margin-right:15px;margin-left:5px" placeholder="起始IP地址">\
                            <input class="bt-input-text mr5" name="end_ip" type="text" style="width:180px;margin-left:5px;margin-right:20px" placeholder="结束IP地址">\
                            <button class="btn btn-success btn-sm va0 pull-right" onclick="addIpWhite();">添加</button>\</div>\
                        <div class="divtable">\
                        <div id="ipWhite" style="max-height:300px;overflow:auto;border:#ddd 1px solid">\
                            <table class="table table-hover" style="border:none">\
                                <thead>\
                                    <tr>\
                                        <th>超始IP</th>\
                                        <th>结束IP</th>\
                                        <th style="text-align: right;">操作</th>\
                                    </tr>\
                                </thead>\
                                <tbody id="ip_white_con" class="gztr"></tbody>\
                            </table>\
                        </div>\
                    </div>\
                    <div style="width:100%" class="mt5">\
                        <button class="btn btn-success btn-sm va0 mr5 mt10" onclick="fileInput(\'ip_white\')" >导入</button>\
                        <button class="btn btn-success btn-sm va0 mt10" onclick="outputData(\'ip_white\')">导出</button>\
                    </div>\
                    <ul class="help-info-text c7 ptb10">\
                        <li>所有规则对白名单中的IP段无效,包括IP黑名单和URL黑名单,IP白名单具备最高优先权</li>\
                    </ul>\
                </div>\
                <div class="pd15 ipv6_list">\
                </div>',
            success:function(index,layero){
                // $('.tab_list .tab_block').click(function(){
                //     $(this).addClass('active').siblings().removeClass('active');
                //     console.log($(this).index());
                //     if($(this).index() === 0){
                //         $('.ipv4_list').show().next().hide();
                //     }else{
                //         $('.ipv4_list').hide().next().show();
                //     }
                // });
                // <div class="tab_list"><div class="tab_block active">IPv4白名单</div><div class="tab_block">IPv6白名单</div></div>\
            }
        });
        tableFixed("ipWhite");
    }
    ipWhiteLoadList();
}

//IP白名单
function urlWhite(type) {

    var ruleName = "url_white";

    if (type == undefined) {
        create_l = layer.open({
            type: 1,
            title: "管理URL白名单",
            area: ['700px', '530px'],
            closeBtn: 1,
            shadeClose: false,
            content: '<div class="pd15">\
                <div style="border-bottom:#ccc 1px solid;margin-bottom:10px;padding-bottom:10px">\
                <input class="bt-input-text" name="ruleValue" type="text" value="" style="width:470px;margin-right:12px;" placeholder="规则内容,请使用正则表达式">\
                <input class="bt-input-text mr5" name="rulePs" type="text" style="width:120px;" placeholder="描述">\
                <button class="btn btn-success btn-sm va0 pull-right" onclick="addRule(\''+ ruleName + '\');">添加</button>\</div>\
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
        tableFixed("jc-file-table");
    }

    getRuleByName(ruleName, function(data){
        var tmp = $.parseJSON(data.data);
        var rdata = $.parseJSON(tmp.data);
        console.log(rdata);
        var tbody = ''
        for (var i = 0; i < rdata.length; i++) {
            var removeRule = ''
            if (rdata[i][3] != 0) removeRule = ' | <a class="btlink" onclick="removeRule(\'' + ruleName + '\',' + i + ')">删除</a>';
            tbody += '<tr>\
                    <td class="rule_body_'+ i + '">' + rdata[i][1] + '</td>\
                    <td class="rule_ps_'+ i + '">' + rdata[i][2] + '</td>\
                    <td class="rule_modify_'+ i + '"><a class="btlink" onclick="modifyRule(' + i + ',\'' + ruleName + '\')">编辑</a>' + removeRule + '</td>\
                    <td class="text-right">\
                        <div class="pull-right">\
                        <input class="btswitch btswitch-ios" id="closeua_'+ i + '" type="checkbox" ' + (rdata[i][0] ? 'checked' : '') + '>\
                        <label class="btswitch-btn" style="width:2.0em;height:1.2em;margin-bottom: 0" for="closeua_'+ i + '" onclick="setRuleState(\'' + ruleName + '\',' + i + ')"></label>\
                        </div>\
                    </td>\
                </tr>'
        }
        $("#set_obj_conf_con").html(tbody);
    });
}


// 获取IPV4黑名单
function getIpv4Address(callback){
    getRuleByName('ip_black', function(data){
        var tmp = $.parseJSON(data.data);
        var rdata = $.parseJSON(tmp.data);
        callback(rdata);
    });
}

// 获取IPV6黑名单
function getIpv6Address(callback){
    getRuleByName('ipv6_black', function(data){
        var tmp = $.parseJSON(data.data);
        var rdata = $.parseJSON(tmp.data);
        callback(rdata);
    });
}


// 添加ipv6请求
function addIpv6Req(ip,callback){
    var ip = ip.replace(/:/g, '_');
    owPost('set_ipv6_black', {addr:ip}, function(data){
        var rdata = $.parseJSON(data.data);
        if(callback) callback(rdata);
    });
}

// 添加ipv6请求
function removeIpv6Black(ip,callback){
    var ip = ip.replace(/:/g, '_');
    owPost('del_ipv6_black', {addr:ip}, function(data){
        var rdata = $.parseJSON(data.data);
        layer.msg(rdata.msg,{icon:rdata.status?1:2});
        $('.tab_list .tab_block:eq(1)').click();

        if(callback) callback(rdata);
    });
}

//添加IP段到IP黑名单
function addIpBlack() {
    var pdata = {
        start_ip: $("input[name='start_ip']").val(),
        end_ip: $("input[name='end_ip']").val()
    }

    if (pdata['start_ip'].split('.').length < 4 || pdata['end_ip'].split('.').length < 4) {
        layer.msg('起始IP或结束IP格式不正确!');
        return;
    }

    owPost('add_ip_black', pdata, function(data){
        var rdata = $.parseJSON(data.data);
        if (rdata.status) {
            ipBlack(1);
        }
        layer.msg(rdata.msg, { icon: rdata.status ? 1 : 2 });
    });
}

function addIpBlackArgs(ip) {
    var pdata = {
        start_ip: ip,
        end_ip: ip,
    }

    if (pdata['start_ip'].split('.').length < 4 || pdata['end_ip'].split('.').length < 4) {
        layer.msg('起始IP或结束IP格式不正确!');
        return;
    }

    owPost('add_ip_black', pdata, function(data){
        var rdata = $.parseJSON(data.data);
        layer.msg(rdata.msg, { icon: rdata.status ? 1 : 2 });
    });
}


//从IP黑名单删除IP段
function removeIpBlack(index) {
    owPost('remove_ip_black', { index: index }, function (data) {
        var rdata = $.parseJSON(data.data);
        if (rdata.status) {
            ipBlack(1);
        }
        layer.msg(rdata.msg, { icon: rdata.status ? 1 : 2 });
    });
}

//IP黑名单
function ipBlack(type) {
    if (type == undefined) {
        create_l = layer.open({
            type: 1,
            title: "管理IP黑名单",
            area: ['500px', '500px'],
            closeBtn: 1,
            shadeClose: false,
            content: '<div class="tab_list"><div class="tab_block active">IPv4黑名单</div><div class="tab_block">IPv6黑名单</div></div>\
                <div class="pd15 ipv4_block">\
                    <div style="border-bottom:#ccc 1px solid;margin-bottom:10px;padding-bottom:10px">\
                        <input class="bt-input-text" name="start_ip" type="text" value="" style="width:150px;margin-right:15px;margin-left:5px" placeholder="起始IP地址">\
                        <input class="bt-input-text mr5" name="end_ip" type="text" style="width:150px;margin-left:5px;margin-right:20px" placeholder="结束IP地址">\
                        <button class="btn btn-success btn-sm va0 pull-right" onclick="addIpBlack();">添加</button>\</div>\
                    <div class="divtable">\
                    <div id="ipBlack" style="max-height:300px;overflow:auto;border:#ddd 1px solid">\
                    <table class="table table-hover" style="border:none">\
                        <thead>\
                            <tr>\
                                <th>超始IP</th>\
                                <th>结束IP</th>\
                                <th style="text-align: right;">操作</th>\
                            </tr>\
                        </thead>\
                        <tbody id="ip_black_con" class="gztr"></tbody>\
                    </table>\
                    </div>\
                    <div style="width:100%" class="mt10">\
                        <button class="btn btn-success btn-sm va0 mr5 mt10" onclick="fileInput(\'ip_black\')" >导入</button>\
                        <button class="btn btn-success btn-sm va0 mt10" onclick="outputData(\'ip_black\')">导出</button>\
                    </div>\
                </div>\
                <ul class="help-info-text c7 ptb10">\
                    <li>黑名单中的IP段将被禁止访问,IP白名单中已存在的除外</li>\
                </ul>\
            </div>\
            <div class="pd15 ipv6_block">\
                <div style="border-bottom:#ccc 1px solid;margin-bottom:10px;padding-bottom:10px">\
                    <input class="bt-input-text" name="ipv6_address" type="text" style="width:380px;margin-right:15px;margin-left:5px" placeholder="ipv6地址">\
                    <button class="btn btn-success btn-sm va0 btn_add_ipv6" style="margin-left:15px;">添加</button>\
                </div>\
                <div class="divtable">\
                    <div id="ipv6_black" style="max-height:300px;overflow:auto;border:#ddd 1px solid">\
                        <table class="table table-hover" style="border:none">\
                            <thead><tr><th>IPv6地址</th><th style="text-align: right;">操作</th></tr></thead>\
                            <tbody id="ipv6_black_con" class="gztr"></tbody>\
                        </table>\
                    </div>\
                </div>\
                <ul class="help-info-text c7 ptb10">\
                    <li>黑名单中的IP段将被禁止访问,IP白名单中已存在的除外</li>\
                </ul>\
            </div>',
            success:function(index,layero){
                $('.tab_list .tab_block').click(function(){
                    $(this).addClass('active').siblings().removeClass('active');
                    if($(this).index() === 0){
                        $('.ipv4_block').show().next().hide();
                        getIpv4Address(function(rdata){
                            var tbody = ''
                            for (var i = 0; i < rdata.length; i++) {
                                tbody += '<tr>\
                                        <td>'+ rdata[i][0].join('.') + '</td>\
                                        <td>'+ rdata[i][1].join('.') + '</td>\
                                        <td class="text-right"><a class="btlink" onclick="removeIpBlack('+ i + ')">删除</a></td>\
                                    </tr>'
                            }
                            $("#ip_black_con").html(tbody);
                        });
                    }else{
                        $('.ipv4_block').hide().next().show();
                        getIpv6Address(function(res){
                            var tbody = '',rdata = res;
                            for (var i = 0; i < rdata.length; i++) {
                                tbody += '<tr>\
                                    <td>'+ rdata[i] + '</td>\
                                    <td class="text-right"><a class="btlink" onclick="removeIpv6Black(\''+ rdata[i] + '\')">删除</a></td>\
                                </tr>'
                            }
                            $("#ipv6_black_con").html(tbody);
                        });
                    }
                });
                $('.btn_add_ipv6').click(function(){
                    var ipv6 = $('[name="ipv6_address"]').val();
                    addIpv6Req(ipv6, function(res){
                        layer.msg(res.msg,{icon:res.status?1:2});
                        if(res.status){
                            $('[name="ipv6_address"]').val('');
                            $('.tab_list .tab_block:eq(1)').click();
                        }
                    });
                });
                $('.tab_list .tab_block:eq(0)').click();
            }
        });
        tableFixed("ipBlack");
    } else {
        $('.tab_list .tab_block:eq(0)').click();
    }
}

function wafScreen(){

    owPost('waf_srceen', {}, function(data){
        var rdata = $.parseJSON(data.data);

        var end_time = Date.now();
        var cos_time = (end_time/1000) - parseInt(rdata['start_time']);
        var cos_day = parseInt(parseInt(cos_time)/86400);

        var con = '<div class="wavbox alert alert-success" style="margin-right:16px">总拦截<span>'+rdata.total+'</span>次</div>';
        con += '<div class="wavbox alert alert-info" style="margin-right:16px">安全防护<span>'+cos_day+'</span>天</div>';

        con += '<div class="screen">\
            <div class="line"><span class="name">POST渗透</span><span class="val">'+rdata.rules.post+'</span></div>\
            <div class="line"><span class="name">GET渗透</span><span class="val">'+rdata.rules.args+'</span></div>\
            <div class="line"><span class="name">CC攻击</span><span class="val">'+rdata.rules.cc+'</span></div>\
            <div class="line"><span class="name">恶意User-Agent</span><span class="val">'+rdata.rules.user_agent+'</span></div>\
            <div class="line"><span class="name">Cookie渗透</span><span class="val">'+rdata.rules.cookie+'</span></div>\
            <div class="line"><span class="name">恶意扫描</span><span class="val">'+rdata.rules.scan+'</span></div>\
            <div class="line"><span class="name">恶意HEAD请求</span><span class="val">0</span></div>\
            <div class="line"><span class="name">URI自定义拦截</span><span class="val">'+rdata.rules.url+'</span></div>\
            <div class="line"><span class="name">URI保护</span><span class="val">'+rdata.rules.args+'</span></div>\
            <div class="line"><span class="name">恶意文件上传</span><span class="val">'+rdata.rules.upload_ext+'</span></div>\
            <div class="line"><span class="name">禁止的扩展名</span><span class="val">'+rdata.rules.path+'</span></div>\
            <div class="line"><span class="name">禁止PHP脚本</span><span class="val">'+rdata.rules.php_path+'</span></div>\
            </div>';

        con += '<div style="width:660px;"><ul class="help-info-text c7">\
            <li>在此处关闭防火墙后,所有站点将失去保护</li>\
            <li>网站防火墙会使nginx有一定的性能损失(&lt;5% 10C静态并发测试结果)</li>\
            <li>网站防火墙仅主要针对网站渗透攻击,暂时不具备系统加固功能</li>\
            </ul></div>';

        $(".soft-man-con").html(con);
    });
}

function wafGloablRefresh(time){
    setTimeout(function(){
        wafGloabl();
    }, time);
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
                        <td class="text-right"><a class="btlink" onclick="setRetry('+ rdata.retry.retry_cycle + ',' + rdata.retry.retry + ',' + rdata.retry.retry_time + ')">初始规则</a></td>\
                    </tr>\
                    <tr>\
                        <td>强制安全验证</td>\
                        <td>'+rdata.safe_verify.ps+'</td>\
                        <td>--</td>\
                        <td style="text-align: center;"><div class="ssh-item">\
                            <input class="btswitch btswitch-ios" id="close_safe_verify" type="checkbox" '+(rdata.safe_verify.open ? 'checked' : '')+'>\
                            <label class="btswitch-btn" for="close_safe_verify" onclick="setObjOpen(\'safe_verify\')"></label></div>\
                        </td>\
                        <td class="text-right"><a class="btlink" onclick="setSafeVerify('+ rdata.safe_verify.auto + ',' + rdata.safe_verify.cpu + ',' + rdata.safe_verify.time + ',\'' + rdata.safe_verify.mode + '\')">设置</a> | <a class="btlink" href="javascript:;" onclick="onlineEditFile(0,\''+rdata['reqfile_path']+'/safe_js.html\')">响应内容</a></td>\
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
                        </div></td><td class="text-right"><a class="btlink" onclick="setObjConf(\'args\')">规则</a> | <a class="btlink" href="javascript:;" onclick="onlineEditFile(0,\''+rdata['reqfile_path']+'/get.html\')">响应内容</a></td>\
                    </tr>\
                    <tr>\
                        <td>POST过滤</td><td>'+ rdata.post.ps + '</td><td><a class="btlink" onclick="setRequestCode(\'post\',' + rdata.post.status + ')">' + rdata.post.status + '</a></td><td><div class="ssh-item">\
                            <input class="btswitch btswitch-ios" id="closepost" type="checkbox" '+ (rdata.post.open ? 'checked' : '') + '>\
                            <label class="btswitch-btn" for="closepost" onclick="setObjOpen(\'post\')"></label>\
                        </div></td><td class="text-right"><a class="btlink" onclick="setObjConf(\'post\')">规则</a> | <a class="btlink" href="javascript:;" onclick="onlineEditFile(0,\''+rdata['reqfile_path']+'/post.html\')">响应内容</a></td>\
                    </tr>\
                    <tr>\
                        <td>User-Agent过滤</td><td>'+ rdata['user-agent'].ps + '</td><td><a class="btlink" onclick="setRequestCode(\'user-agent\',' + rdata['user-agent'].status + ')">' + rdata['user-agent'].status + '</a></td><td><div class="ssh-item">\
                            <input class="btswitch btswitch-ios" id="closeua" type="checkbox" '+ (rdata['user-agent'].open ? 'checked' : '') + '>\
                            <label class="btswitch-btn" for="closeua" onclick="setObjOpen(\'user-agent\')"></label>\
                        </div></td><td class="text-right"><a class="btlink" onclick="setObjConf(\'user_agent\')">规则</a> | <a class="btlink" href="javascript:;" onclick="onlineEditFile(0,\''+rdata['reqfile_path']+'/user_agent.html\')">响应内容</a></td>\
                    </tr>\
                    <tr>\
                        <td>Cookie过滤</td><td>'+ rdata.cookie.ps + '</td><td><a class="btlink" onclick="setRequestCode(\'cookie\',' + rdata.cookie.status + ')">' + rdata.cookie.status + '</a></td><td><div class="ssh-item">\
                            <input class="btswitch btswitch-ios" id="closecookie" type="checkbox" '+ (rdata.cookie.open ? 'checked' : '') + '>\
                            <label class="btswitch-btn" for="closecookie" onclick="setObjOpen(\'cookie\')"></label>\
                        </div></td><td class="text-right"><a class="btlink" onclick="setObjConf(\'cookie\')">规则</a> | <a class="btlink" href="javascript:;" onclick="onlineEditFile(0,\''+rdata['reqfile_path']+'/cookie.html\')">响应内容</a></td>\
                    </tr>\
                    <tr>\
                        <td>常见扫描器</td><td>'+ rdata.scan.ps + '</td><td><a class="btlink" onclick="setRequestCode(\'scan\',' + rdata.scan.status + ')">' + rdata.scan.status + '</a></td><td><div class="ssh-item">\
                            <input class="btswitch btswitch-ios" id="closescan" type="checkbox" '+ (rdata.scan.open ? 'checked' : '') + '>\
                            <label class="btswitch-btn" for="closescan" onclick="setObjOpen(\'scan\')"></label>\
                        </div></td><td class="text-right"><a class="btlink" onclick="scanRule()">设置</a></td>\
                    </tr>\
                    <tr>\
                        <td>URL白名单</td><td>所有规则对URL白名单无效</td><td style="text-align: center;">--</td>\
                        <td style="text-align: center;">--</td>\
                        <td class="text-right"><a class="btlink" onclick="urlWhite()">设置</a></td>\
                    </tr>\
                    <tr>\
                        <td>IP白名单</td><td>所有规则对IP白名单无效</td><td style="text-align: center;">--</td>\
                        <td style="text-align: center;">--</td>\
                        <td class="text-right"><a class="btlink" onclick="ipWhite()">设置</a></td>\
                    </tr>\
                    <tr>\
                        <td>IP黑名单</td><td>禁止访问的IP</td><td><a class="btlink" onclick="setRequestCode(\'cc\','+ rdata.cc.status + ')">' + rdata.cc.status + '</a></td>\
                        <td style="text-align: center;">--</td>\
                        <td class="text-right"><a class="btlink" onclick="ipBlack()">设置</a></td>\
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
            <li>优先级: IP白名单>IP黑名单>URL白名单>URL黑名单>CC防御>User-Agent>URI过滤>URL参数>Cookie>POST</li>\
            </ul></div>';
        $(".soft-man-con").html(con);
    });
}

//返回css
function back_css(v) {
    if (v > 0) {
        return 'tipsval'
    }
    else {
        return 'tipsval tipsvalnull'
    }
}

function html_encode(value) {
    return $('<div></div>').html(value).text();
}

function html_decode(value) {
    return $('<div></div>').text(value).html();
}

//添加站点过滤规则
function addSiteRule(siteName, ruleName) {
    var pdata = {
        ruleValue: $("input[name='site_rule_value']").val(),
        siteName: siteName,
        ruleName: ruleName
    }

    if (pdata['ruleValue'] == '') {
        layer.msg('过滤规则不能为空');
        $("input[name='site_rule_value']").focus();
        return;
    }

    owPost('add_site_rule', pdata, function(data){
        var rdata = $.parseJSON(data.data);
        layer.msg(rdata.msg, { icon: rdata.status ? 1 : 2 });
        if (rdata.status) {
            setTimeout(function(){
                siteRuleAdmin(siteName, ruleName, 1);
            },1000);
        }
    });
}

//删除站点过滤规则
function removeSiteRule(siteName, ruleName, index) {
    var pdata = {
        index: index,
        siteName: siteName,
        ruleName: ruleName
    }

    owPost('remove_site_rule', pdata, function(data){
        var rdata = $.parseJSON(data.data);
        layer.msg(rdata.msg, { icon: rdata.status ? 1 : 2 });
        if (rdata.status) {
            if (ruleName == 'url_tell') {
                site_url_tell(siteName, 1);
                return;
            }

            if (ruleName == 'url_rule') {
                site_url_rule(siteName, 1);
                return;
            }

            setTimeout(function(){
                siteRuleAdmin(siteName, ruleName, 1);
            },1000);
        }
    });
}

//网站规则管理
function siteRuleAdmin(siteName, ruleName, type) {
    var placeho = '';
    var ps = '';
    var title = '';
    switch (ruleName) {
        case 'disable_php_path':
            placeho = 'URI地址,支持正则表达式';
            ps = '<li>此处请不要包含URI参数,一般针对目录URL,示例：/admin</li>'
            title = '禁止运行PHP的URL地址'
            break;
        case 'disable_path':
            placeho = 'URI地址,支持正则表达式';
            ps = '<li>此处请不要包含URI参数,一般针对目录URL,示例：/admin</li>'
            title = '禁止访问的URL地址'
            break;
        case 'disable_ext':
            placeho = '扩展名，不包含点(.)，示例：sql';
            ps = '<li>直接填要被禁止访问的扩展名，如我希望禁止访问*.sql文件：sql</li>'
            title = '禁止访问的扩展名'
            break;
        case 'disable_upload_ext':
            placeho = '扩展名，不包含点(.)，示例：sql';
            ps = '<li>直接填要被禁止访问的扩展名，如我希望禁止上传*.php文件：php</li>'
            title = '禁止上传的文件类型'
            break;
    }
    if (type == undefined) {
        create_l = layer.open({
            type: 1,
            title: "管理网站过滤规则【" + title + "】",
            area: ['500px', '500px'],
            closeBtn: 1,
            shadeClose: false,
            content: '<div class="pd15">\
                <div style="border-bottom:#ccc 1px solid;margin-bottom:10px;padding-bottom:10px">\
                    <input class="bt-input-text" name="site_rule_value" type="text" value="" style="width:400px;margin-right:15px;margin-left:5px" placeholder="'+ placeho + '">\
                    <button class="btn btn-success btn-sm va0 pull-right" onclick="addSiteRule(\''+ siteName + '\',\'' + ruleName + '\');">添加</button>\</div>\
                <div class="divtable">\
                <div id="siteRuleAdmin" class="siteRuleAdmin" style="max-height:273px;overflow:auto;border:#ddd 1px solid">\
                <table class="table table-hover" style="border:none">\
                    <thead>\
                        <tr>\
                            <th>规则</th>\
                            <th style="text-align: right;">操作</th>\
                        </tr>\
                    </thead>\
                    <tbody id="site_rule_admin_con" class="gztr"></tbody>\
                </table>\
                </div>\
            </div>\
            <ul class="help-info-text c7 ptb10">\
                <li>除正则表达式语句外规则值对大小写不敏感,建议统一使用小写</li>'+ ps + '\
            </ul></div>'
        });
        tableFixed("siteRuleAdmin");
    }

    owPost('get_site_rule', { siteName: siteName, ruleName: ruleName }, function(data){
        var tmp = $.parseJSON(data.data);
        var rdata = $.parseJSON(tmp.data);
        var tbody = ''
        for (var i = 0; i < rdata.length; i++) {
            tbody += '<tr>\
                    <td>'+ rdata[i] + '</td>\
                    <td class="text-right"><a class="btlink" onclick="removeSiteRule(\''+ siteName + '\',\'' + ruleName + '\',' + i + ')">删除</a></td>\
                </tr>'
        }
        $("#site_rule_admin_con").html(tbody);
    });
}

//CDN-Header配置
function cdnHeader(siteName, type) {
    if (type == undefined) {
        create_l = layer.open({
            type: 1,
            title: "管理网站【" + siteName + "】CDN-Headers",
            area: ['500px', '500px'],
            closeBtn: 1,
            shadeClose: false,
            content: '<div class="pd15">\
                <div style="border-bottom:#ccc 1px solid;margin-bottom:10px;padding-bottom:10px">\
                    <input class="bt-input-text" name="cdn_header_key" type="text" value="" style="width:400px;margin-right:15px;margin-left:5px" placeholder="header名称">\
                    <button class="btn btn-success btn-sm va0 pull-right" onclick="addCdnHeader(\''+ siteName + '\');">添加</button>\</div>\
                <div class="divtable">\
                <div id="cdnHeader" style="max-height:300px;overflow:auto;border:#ddd 1px solid">\
                <table class="table table-hover" style="border:none">\
                    <thead>\
                        <tr>\
                            <th>header</th>\
                            <th style="text-align: right;">操作</th>\
                        </tr>\
                    </thead>\
                    <tbody id="cdn_header_con" class="gztr"></tbody>\
                </table>\
            </div>\
            </div>\
            <ul class="help-info-text c7 ptb10">\
                <li>防火墙将尝试在以上header中获取客户IP</li>\
            </ul></div>'
        });
        tableFixed("cdnHeader");
    }

    owPost('get_site_config_byname', { siteName: siteName }, function(data){
        var tmp = $.parseJSON(data.data);
        var t1 = tmp.data;
        var rdata = t1['cdn_header'];
        var tbody = ''
        for (var i = 0; i < rdata.length; i++) {
            tbody += '<tr>\
                    <td>'+ rdata[i] + '</td>\
                    <td class="text-right"><a class="btlink" onclick="removeCdnHeader(\''+ siteName + '\',\'' + rdata[i] + '\')">删除</a></td>\
                </tr>'
        }
        $("#cdn_header_con").html(tbody);
    });
}

//添加CDN-Header
function addCdnHeader(siteName) {
    var pdata = {
        cdn_header: $("input[name='cdn_header_key']").val(),
        siteName: siteName
    }

    if (pdata['cdn_header'] == '') {
        layer.msg('header不能为空');
        $("input[name='cdn_header_key']").focus();
        return;
    }

    owPost('add_site_cdn_header', pdata, function(data){
        var rdata = $.parseJSON(data);
        layer.msg(rdata.msg, { icon: rdata.status ? 1 : 2 });
        if (rdata.status) {
            setTimeout(function(){
                cdnHeader(siteName, 1);
            },1000);
        }
    });
}

 //删除CDN-Header
function removeCdnHeader(siteName, cdn_header_key) {
    owPost('remove_site_cdn_header', { siteName: siteName, cdn_header: cdn_header_key }, function(data){
        var rdata = $.parseJSON(data.data);
        layer.msg(rdata.msg, { icon: rdata.status ? 1 : 2 });
        if (rdata.status) {
            setTimeout(function(){
                cdnHeader(siteName, 1);
            },1000);
        }
    });
}

//设置网站防御功能
function setSiteObjState(siteName, obj) {
    // var loadT = layer.msg('正在处理，请稍候..', { icon: 16, time: 0 });
    owPost('set_site_obj_open', { siteName: siteName, obj: obj } , function(data){
        var rdata = $.parseJSON(data.data);
        layer.msg(rdata.msg, { icon: rdata.status ? 1 : 2 });
        setTimeout(function(){
            siteWafConfig(siteName, 1);
            // siteConfig();
        },1000);
    });
    // $.post('/plugin?action=a&name=btwaf&s=set_site_obj_open', { siteName: siteName, obj: obj }, function (rdata) {
    //     layer.close(loadT);
    //     site_waf_config(siteName, 1);
    //     siteconfig();
    //     layer.msg(rdata.msg, { icon: rdata.status ? 1 : 2 });
    // });
}


//网站规则设置
function setSiteObjConf(siteName, ruleName, type) {
    if (type == undefined) {
        create_l = layer.open({ 
            type: 1,
            title: "编辑网站【" + siteName + "】规则【" + ruleName + "】",
            area: ['700px', '530px'],
            closeBtn: 1,
            shadeClose: false,
            content: '<div class="pd15">\
                <div class="divtable">\
                <div id="SetSiteObjConf" class="table_head_fix" style="max-height:375px;overflow:auto;border:#ddd 1px solid">\
                <table class="table table-hover" style="border:none">\
                    <thead>\
                        <tr>\
                            <th width="450">规则</th>\
                            <th>说明</th>\
                            <th style="text-align: right;">状态</th>\
                        </tr>\
                    </thead>\
                    <tbody id="set_site_obj_conf_con" class="gztr"></tbody>\
                </table>\
                </div>\
            </div>\
            <ul class="help-info-text c7 ptb10">\
                <li>此处继承全局设置中已启用的规则</li>\
                <li>此处的设置仅对当前站点有效</li>\
            </ul></div>'
        });
        tableFixed("SetSiteObjConf");
    }

    getRuleByName(ruleName, function(data){
        var tmp = $.parseJSON(data.data);
        var rdata = $.parseJSON(tmp.data);
        var tbody = '';
        var tbody = '';
        for (var i = 0; i < rdata.length; i++) {
            if (rdata[i][0] == -1) continue;
            tbody += '<tr>\
                    <td>'+ rdata[i][1] + '</td>\
                    <td>'+ rdata[i][2] + '</td>\
                    <td style="text-align: right;">\
                        <div class="pull-right"><input class="btswitch btswitch-ios" id="close_'+ i + '" type="checkbox" ' + (rdata[i][0] ? 'checked' : '') + '>\
                        <label class="btswitch-btn" for="close_'+ i + '" style="width:2em;height:1.2em;margin-bottom: 0" for="closeua_' + i + '" onclick="set_site_rule_state(\'' + siteName + '\',\'' + ruleName + '\',' + i + ')"></label></div>\
                    </td>\
                </tr>'
        }
        $("#set_site_obj_conf_con").html(tbody)
    });
}

//网站设置
function siteWafConfig(siteName, type) {
    if (type == undefined) {
        create_2 = layer.open({
            type: 1,
            title: "网站配置【" + siteName + "】",
            area: ['700px', '500px'],
            closeBtn: 1,
            shadeClose: false,
            content: '<div id="s_w_c"></div>'
        });
    }

    owPost('get_site_config_byname', { siteName: siteName }, function(data){
        var tmp = $.parseJSON(data.data);
        var rdata = tmp.data;
        nginx_config = rdata;
        var con = '<div class="pd15">\
                <div class="lib-con-title">\
                    <span>网站防火墙开关</span>\
                    <div class="ssh-item" style="margin-right:20px;">\
                        <input class="btswitch btswitch-ios" id="closewaf_open" type="checkbox" '+ (rdata.open ? 'checked' : '') + '>\
                        <label class="btswitch-btn" for="closewaf_open" onclick="setSiteObjState(\''+ siteName + '\',\'open\')" style="width:2.4em;height:1.4em;margin-bottom: 0"></label>\
                    </div>\
                </div>\
                <div class="lib-con">\
                    <div class="divtable">\
                        <table class="table table-hover waftable">\
                            <thead>\
                                <tr>\
                                    <th>名称</th>\
                                    <th>描述</th>\
                                    <th width="80">状态</th>\
                                    <th style="text-align: right;">操作</th>\
                                </tr>\
                            </thead>\
                            <tbody>\
                                <tr>\
                                    <td>CC防御</td>\
                                    <td><font style="color:red;">'+ rdata.cc.cycle + '</font> 秒内,请求同一URI累计超过 <font style="color:red;">' + rdata.cc.limit + '</font> 次,封锁IP <font style="color:red;">' + rdata.cc.endtime + '</font> 秒</td>\
                                    <td>\
                                        <div class="ssh-item" style="margin-left:0">\
                                            <input class="btswitch btswitch-ios" id="closecc" type="checkbox" '+ (rdata.cc.open ? 'checked' : '') + '>\
                                            <label class="btswitch-btn" for="closecc" onclick="setSiteObjState(\''+ siteName + '\',\'cc\')"></label>\
                                        </div>\
                                    </td>\
                                    <td class="text-right"><a class="btlink" onclick="setCcRule('+ rdata.cc.cycle + ',' + rdata.cc.limit + ',' + rdata.cc.endtime + ',\'' + siteName + '\',' + rdata.cc.increase + ')">设置</a></td>\
                                </tr>\
                                <tr>\
                                    <td>恶意容忍设置</td>\
                                    <td><font style="color:red;">'+ rdata.retry.retry_cycle + '</font> 秒内,累计超过 <font style="color:red;">' + rdata.retry.retry + '</font> 次恶意请求,封锁IP <font style="color:red;">' + rdata.retry.retry_time + '</font> 秒</td>\
                                    <td style="text-align: left;">&nbsp;&nbsp;--</td>\
                                    <td class="text-right"><a class="btlink" onclick="setRetry('+ rdata.retry.retry_cycle + ',' + rdata.retry.retry + ',' + rdata.retry.retry_time + ',\'' + siteName + '\')">设置</a></td>\
                                </tr>\
                                <tr>\
                                    <td>GET-URI过滤</td>\
                                    <td>'+ rdata.get.ps + '</td>\
                                    <td>\
                                        <div class="ssh-item" style="margin-left:0">\
                                            <input class="btswitch btswitch-ios" id="closeget" type="checkbox" '+ (rdata.get ? 'checked' : '') + '>\
                                            <label class="btswitch-btn" for="closeget" onclick="setSiteObjState(\''+ siteName + '\',\'get\')"></label>\
                                        </div>\
                                    </td>\
                                    <td class="text-right"><a class="btlink" onclick="setSiteObjConf(\''+ siteName + '\',\'url\')">规则</a></td>\
                                </tr>\
                                <td>GET-参数过滤</td>\
                                    <td>'+ rdata.get.ps + '</td>\
                                    <td>\
                                        <div class="ssh-item" style="margin-left:0">\
                                            <input class="btswitch btswitch-ios" id="closeargs" type="checkbox" '+ (rdata.get ? 'checked' : '') + '>\
                                            <label class="btswitch-btn" for="closeargs" onclick="setSiteObjState(\''+ siteName + '\',\'get\')"></label>\
                                        </div>\
                                    </td>\
                                    <td class="text-right"><a class="btlink" onclick="setSiteObjConf(\''+ siteName + '\',\'args\')">规则</a></td>\
                                </tr>\
                                <tr>\
                                    <td>POST过滤</td>\
                                    <td>'+ rdata.post.ps + '</td>\
                                    <td>\
                                        <div class="ssh-item" style="margin-left:0">\
                                            <input class="btswitch btswitch-ios" id="closepost" type="checkbox" '+ (rdata.post ? 'checked' : '') + '>\
                                            <label class="btswitch-btn" for="closepost" onclick="setSiteObjState(\''+ siteName + '\',\'post\')"></label>\
                                        </div>\
                                    </td>\
                                    <td class="text-right"><a class="btlink" onclick="setSiteObjConf(\''+ siteName + '\',\'post\')">规则</a></td>\
                                </tr>\
                                <tr>\
                                    <td>User-Agent过滤</td>\
                                    <td>'+ rdata['user-agent'].ps + '</td>\
                                    <td>\
                                        <div class="ssh-item" style="margin-left:0">\
                                            <input class="btswitch btswitch-ios" id="closeua" type="checkbox" '+ (rdata['user-agent'] ? 'checked' : '') + '>\
                                            <label class="btswitch-btn" for="closeua" onclick="setSiteObjState(\''+ siteName + '\',\'user-agent\')"></label>\
                                        </div>\
                                    </td>\
                                    <td class="text-right"><a class="btlink" onclick="setSiteObjConf(\''+ siteName + '\',\'user_agent\')">规则</a></td>\
                                </tr>\
                                 <tr>\
                                    <td>Cookie过滤</td>\
                                    <td>'+ rdata.cookie.ps + '</td>\
                                    <td>\
                                    <div class="ssh-item" style="margin-left:0">\
                                        <input class="btswitch btswitch-ios" id="closecookie" type="checkbox" '+ (rdata.cookie ? 'checked' : '') + '>\
                                        <label class="btswitch-btn" for="closecookie" onclick="setSiteObjState(\''+ siteName + '\',\'cookie\')"></label>\
                                    </div>\
                                    </td>\
                                    <td class="text-right"><a class="btlink" onclick="setSiteObjConf(\''+ siteName + '\',\'cookie\')">规则</a></td>\
                                </tr>\
                                <tr>\
                                    <td>常见扫描器</td><td>'+ rdata.scan.ps + '</td>\
                                    <td>\
                                        <div class="ssh-item" style="margin-left:0">\
                                            <input class="btswitch btswitch-ios" id="closescan" type="checkbox" '+ (rdata.scan ? 'checked' : '') + '>\
                                            <label class="btswitch-btn" for="closescan" onclick="setSiteObjState(\''+ siteName + '\',\'scan\')"></label>\
                                        </div>\
                                    </td>\
                                    <td class="text-right"><a class="btlink" onclick="scanRule()">设置</a></td>\
                                </tr>\
                                <tr>\
                                    <td>使用CDN</td>\
                                    <td>该站点使用了CDN,启用后方可正确获取客户IP</td>\
                                    <td>\
                                        <div class="ssh-item" style="margin-left:0">\
                                            <input class="btswitch btswitch-ios" id="closecdn" type="checkbox" '+ (rdata.cdn ? 'checked' : '') + '>\
                                            <label class="btswitch-btn" for="closecdn" onclick="setSiteObjState(\''+ siteName + '\',\'cdn\')"></label>\
                                        </div>\
                                    </td>\
                                    <td class="text-right"><a class="btlink" onclick="cdnHeader(\''+ siteName + '\')">设置</a></td>\
                                </tr>\
                                <tr>\
                                    <td>禁止扩展名</td>\
                                    <td>禁止访问指定扩展名</td>\
                                    <td style="text-align: left;">&nbsp;&nbsp;--</td>\
                                    <td class="text-right"><a class="btlink" onclick="siteRuleAdmin(\''+ siteName + '\',\'disable_ext\')">设置</a></td>\
                                </tr>\
                                <tr>\
                                    <td>禁止上传的文件类型</td>\
                                    <td>禁止上传指定的文件类型</td>\
                                    <td style="text-align: left;">&nbsp;&nbsp;--</td>\
                                    <td class="text-right"><a class="btlink" onclick="siteRuleAdmin(\''+ siteName + '\',\'disable_upload_ext\')">设置</a></td>\
                                </tr>\
                            </tbody>\
                        </table>\
                    </div>\
                </div>\
                <ul class="help-info-text c7">\
                    <li>注意: 此处大部分配置,仅对当前站点有效!</li>\
                </ul>\
            </div>';
        $("#s_w_c").html(con);
    });
}



function wafSite(){
    owPost('get_site_config', {}, function(data){
        var tmp = $.parseJSON(data.data);
        var rdata = $.parseJSON(tmp.data);
        var tbody = '';
        var i = 0;
        $.each(rdata, function (k, v) {
            i += 1;
            tbody += '<tr>\
                    <td><a onclick="siteWafConfig(\''+ k + '\')" class="sitename btlink" title="' + k + '">' + k + '</a></td>\
                    <td><input onclick="setSiteObjState(\''+ k + '\',\'get\')" type="checkbox" ' + (v.get ? 'checked' : '') + '><span class="' + back_css(v.total[1].value) + '" title="拦截GET渗透次数:' + v.total[1].value + '">' + v.total[1].value + '</span></td>\
                    <td><input onclick="setSiteObjState(\''+ k + '\',\'post\')"  type="checkbox" ' + (v.post ? 'checked' : '') + '><span class="' + back_css(v.total[0].value) + '"  title="拦截POST渗透次数:' + v.total[0].value + '">' + v.total[0].value + '</span></td>\
                    <td><input onclick="setSiteObjState(\''+ k + '\',\'user-agent\')"  type="checkbox" ' + (v['user-agent'] ? 'checked' : '') + '><span class="' + back_css(v.total[3].value) + '" title="拦截恶意User-Agent次数:' + v.total[3].value + '">' + v.total[3].value + '</span></td>\
                    <td><input onclick="setSiteObjState(\''+ k + '\',\'cookie\')"  type="checkbox" ' + (v.cookie ? 'checked' : '') + '><span class="' + back_css(v.total[4].value) + '" title="拦截Cookie渗透次数:' + v.total[4].value + '">' + v.total[4].value + '</span></td>\
                    <td><input onclick="setSiteObjState(\''+ k + '\',\'cdn\')"  type="checkbox" ' + (v.cdn ? 'checked' : '') + '></td>\
                    <td><input onclick="setSiteObjState(\''+ k + '\',\'cc\')"  type="checkbox" ' + (v.cc.open ? 'checked' : '') + '><span class="' + back_css(v.total[2].value) + '" title="拦截CC攻击次数:' + v.total[2].value + '">' + v.total[2].value + '</span></td>\
                    <td>\
                        <div class="ssh-item" style="margin-left:0">\
                            <input class="btswitch btswitch-ios" id="closeget_'+ i + '" type="checkbox" ' + (v.open ? 'checked' : '') + '>\
                            <label class="btswitch-btn" for="closeget_'+ i + '" onclick="setSiteObjState(\'' + k + '\',\'open\')"></label>\
                        </div>\
                    </td>\
                    <td class="text-right"><a onclick="wafLogs(\''+ k + '\')" class="btlink ' + (v.log_size > 0 ? 'dot' : '') + '">日志</a> </td>\
                </tr>';
            //| <a onclick="siteWafConfig(\'' + k + '\')" class="btlink">设置</a>
        });

        var con = '<div class="lib-box">\
                    <div class="lib-con">\
                        <div class="divtable">\
                        <div id="siteCon_fix" style="max-height:580px; overflow:auto;border:#ddd 1px solid">\
                        <table class="table table-hover waftable" style="border:none">\
                            <thead>\
                                <tr>\
                                    <th>站点</th>\
                                    <th>GET</th>\
                                    <th>POST</th>\
                                    <th>UA</th>\
                                    <th>Cookie</th>\
                                    <th title="这个网站使用了CDN或其它代理时请勾选">CDN</th>\
                                    <th>CC防御</th>\
                                    <th>状态</th>\
                                    <th style="text-align: right;">操作</th>\
                                </tr>\
                            </thead>\
                            <tbody>'+ tbody + '</tbody>\
                        </table>\
                        </div>\
                        </div>\
                    </div>\
            </div>';
        $(".soft-man-con").html(con);
        tableFixed("siteCon_fix");
    });
}


function wafAreaLimitRender(){
    function keyVal(obj){
        var str = [];
        $.each(obj, function (index, item) {
            if (item == 1) {
                if (index == 'allsite') index = '所有站点';
                if (index == '海外') index = '中国大陆以外的地区(包括[港,澳,台])';
                if (index == '中国') index = '中国大陆(不包括[港,澳,台])';
                str.push(index);
            }
        });
        return str.toString();
    }
    owPost('get_area_limit', {}, function(rdata) {
        var rdata = $.parseJSON(rdata.data);
        if (!rdata.status) {
            layer.msg(rdata.msg, { icon: 2, time: 2000 });
            return;
        }

        var list = '';
        var rlist = rdata.data;

        for (var i = 0; i < rlist.length; i++) {
            var op = '';
            var type = rlist[i]['types'] === 'refuse' ? '拦截' : '只放行';
            var region_str = keyVal(rlist[i]['region']);
            var site_str = keyVal(rlist[i]['site']);

            op += '<a  data-id="'+i+'" href="javascript:;" class="area_limit_del btlink">删除</a>';

            list += '<tr>';
            list += '<td><span class="overflow_hide" style="width: 303px;" title="'+region_str+'"">' + region_str + '</span></td>';
            list += '<td>' + site_str + '</td>';
            list += '<td>' + type + '</td>';
        
            list += '<td class="text-right">' + op + '</td>';
            list += '</tr>';
        }

        $('#con_list tbody').html(list);
        $('.area_limit_del').click(function(){
            var data_id = $(this).data('id');

            var site = [],region = [];
            $.each(rlist[data_id]['site'], function (index, item) {
                site.push(index);
            });
            $.each(rlist[data_id]['region'], function (index, item) {
                region.push(index);
            });

            var type = rlist[data_id]['types'];

            owPost('del_area_limit', {
                site:site.toString(),
                region:region.toString(),
                types:type,
            }, function(rdata) {
                var rdata = $.parseJSON(rdata.data);
                showMsg(rdata.msg, function(){
                    if (rdata.status){
                        wafAreaLimit();
                    }
                },{ icon: rdata.status ? 1 : 2 });
            });
        });
    });
}

function wafAreaLimitSwitch(){
    owPostN('waf_conf', {}, function(data){
        var rdata = $.parseJSON(data.data);
        if (rdata['area_limit']){
            $('#area_limit_switch').prop('checked', true);
        } else{
            $('#area_limit_switch').prop('checked',false);
        }
    });
}

function setWafAreaLimitSwitch(){
    var area_limit_switch = $('#area_limit_switch').prop('checked');
    // console.log(area_limit_switch);
    var area_limit = 'off';
    if (!area_limit_switch){
        area_limit = 'on';
    }
    owPostN('area_limit_switch', {'area_limit': area_limit}, function(data){
        var rdata = $.parseJSON(data.data);
        layer.msg(rdata.msg, { icon: rdata.status ? 1 : 2 });
    });
}

// 地区限制
function wafAreaLimit(){
    var con = '<div class="safe bgw">\
            <button id="create_area_limit" class="btn btn-success btn-sm" type="button" style="margin-right: 5px;">添加地区限制</button>\
            <input class="btswitch btswitch-ios" id="area_limit_switch" type="checkbox">\
            <label class="btswitch-btn" for="area_limit_switch" onclick="setWafAreaLimitSwitch();" style="display: inline-flex;line-height:38px;margin-left: 4px;float: right;"></label>\
            <div class="divtable mtb10">\
                <div class="tablescroll">\
                    <table id="con_list" class="table table-hover" width="100%" cellspacing="0" cellpadding="0" border="0" style="border: 0 none;">\
                    <thead><tr>\
                    <th>地区</th>\
                    <th>站点</th>\
                    <th>类型</th>\
                    <th style="text-align:right;">操作</th></tr></thead>\
                    <tbody></tbody></table>\
                </div>\
            </div>\
        </div>';
    $(".soft-man-con").html(con);
    wafAreaLimitRender();
    wafAreaLimitSwitch();

    $('#create_area_limit').click(function(){
        var site_list;
        var area_list;
        var site_length = 0;
        layer.open({
            type: 1,
            title: '添加地区限制',
            area: ['450px','280px'],
            closeBtn: 1,
            btn: ['添加', '取消'],
            content: '<div class="waf-form pd20">\
                <div class="line">\
                    <span class="tname">类型</span>\
                    <div class="info-r c4">\
                        <select name="type" class="bt-input-text" style="width:230px">\
                            <option value="refuse" selected="">拦截</option>\
                            <option value="accept">只放行</option>\
                        </select>\
                    </div>\
                </div>\
                <div class="line">\
                    <span class="tname">站点</span>\
                    <div class="info-r">\
                        <div id="site_list"></div>\
                    </div>\
                </div>\
                <div class="line">\
                    <span class="tname">地区</span>\
                    <div class="info-r" id="area_list"></div>\
                </div>\
            </div>',
            success: function (layers, index) {
                document.getElementById('layui-layer' + index).getElementsByClassName('layui-layer-content')[0].style.overflow = 'unset';

                site_list = xmSelect.render({
                    el: '#site_list',
                    language: 'zn',
                    toolbar: {show: true,},
                    paging: true,
                    pageSize: 10,
                    data: [],
                });

                owPostN('get_default_site','', function(rdata){
                    var rdata = $.parseJSON(rdata.data);
                    var rlist = rdata.data.list;


                    var pdata = [];
                    for (var i = 0; i < rlist.length; i++) {
                        var tval = rlist[i];
                        if (tval != 'unset'){
                            var t = {name:rlist[i],value:rlist[i]};
                            pdata.push(t);
                        }
                    }
                    site_length = pdata.length;
                    site_list.update({data:pdata});
                });

                area_list = xmSelect.render({
                    el: '#area_list',
                    language: 'zn',
                    toolbar: {show: true,},
                    filterable: true,
                    data: [],
                });
                owPostN('get_country','', function(rdata){
                    var rdata = $.parseJSON(rdata.data);
                    var rlist = rdata.data;

                    var pdata = [];
                    for (var i = 0; i < rlist.length; i++) {
                        var tval = rlist[i];
                        if (tval != 'unset'){
                            var t = {name:tval,value:tval};
                            pdata.push(t);
                        }
                    }

                    area_list.update({data:pdata});
                });
            },
            yes: function (indexs) {

                var reg_type = $('select[name="type"]').val();
                var site_val = site_list.getValue('value');
                var area_val = area_list.getValue('value');

                if (area_val.length <1) return layer.msg('地区最少选一个!', { icon: 2 });
                if (site_val.length <1) return layer.msg('站点最少选一个!', { icon: 2 });

                var site = '';
                if (site_length === site_val.length) {
                    site = 'allsite';
                } else {
                    site = site_val.join();
                }

                var area = area_val.join();
                var region = area.replace('中国大陆以外的地区(包括[中国特别行政区:港,澳,台])', '海外')
                    .replace('中国大陆(不包括[中国特别行政区:港,澳,台])', '中国')
                    .replace('中国香港', '香港')
                    .replace('中国澳门', '澳门')
                    .replace('中国台湾', '台湾');

                owPost('add_area_limit',{
                    site:site,
                    types:reg_type,
                    region:region,
                }, function(rdata){
                    var rdata = $.parseJSON(rdata.data);
                    showMsg(rdata.msg, function(){
                        if (rdata.status){
                            layer.close(indexs);
                            wafAreaLimit();
                        }
                    },{ icon: rdata.status ? 1 : 2 });
                });

            },
        });
    });
}

function wafLogRequest(page){
    var args = {};   
    args['page'] = page;
    args['page_size'] = 10;
    args['site'] = $('select[name="site"]').val();

    var query_date = 'today';
    if ($('#time_choose').attr("data-name") != ''){
        query_date = $('#time_choose').attr("data-name");
    } else {
        query_date = $('#search_time button.cur').attr("data-name");
    }

    args['query_date'] = query_date;
    args['tojs'] = 'wafLogRequest';

    owPost('get_logs_list', args, function(rdata){
        var rdata = $.parseJSON(rdata.data);
        var list = '';
        var data = rdata.data.data;
        if (data.length > 0){
            for(i in data){
                list += '<tr>';
                list += '<td><span class="overflow_hide" style="width:112px;">' + getLocalTime(data[i]['time'])+'</span></td>';
                list += '<td><span class="overflow_hide" style="width:50px;">' + data[i]['domain'] +'</span></td>';
                list += '<td><span class="overflow_hide" style="width:60px;">' + data[i]['ip'] +'</span></td>';
                list += '<td><span class="overflow_hide" style="width:50px;">' + data[i]['uri'] +'</span></td>';// data[i]['uri']
                list += '<td><span class="overflow_hide" style="width:50px;">' + data[i]['rule_name'] +'</span></td>';
                list += '<td><span class="overflow_hide" style="width:200px;">' + entitiesEncode(data[i]['reason']) +'</span></td>';//data[i]['reason']
                list += '<td><a data-id="'+i+'" href="javascript:;" class="btlink details" title="详情">详情</a></td>';
                list += '</tr>';
            }
        } else{
             list += '<tr><td colspan="8" style="text-align:center;">封锁日志为空</td></tr>';
        }
        
        var table = '<div class="tablescroll">\
                            <table id="DataBody" class="table table-hover" width="100%" cellspacing="0" cellpadding="0" border="0" style="border: 0 none;">\
                            <thead><tr>\
                            <th>时间</th>\
                            <th>域名</th>\
                            <th>IP</th>\
                            <th>URI</th>\
                            <th>规则名</th>\
                            <th>原因</th>\
                            <th style="text-align:right;">操作</th></tr></thead>\
                            <tbody>\
                            '+ list +'\
                            </tbody></table>\
                        </div>\
                        <div id="wsPage" class="dataTables_paginate paging_bootstrap page"></div>';
        $('#ws_table').html(table);
        $('#wsPage').html(rdata.data.page);

        $(".tablescroll .details").click(function(){
            var index = $(this).attr('data-id');
            var res = data[index];
            var ip = res.ip;
            var time = getLocalTime(res.time);
            layer.open({
                type: 1,
                title: "【"+res.domain + "】详情",
                area: '600px',
                closeBtn: 1,
                shadeClose: false,
                content: '<div class="pd15 lib-box">\
                        <table class="table" style="border:#ddd 1px solid; margin-bottom:10px">\
                        <tbody><tr><th>时间</th><td>'+ time + '</td><th>用户IP</th><td><a class="btlink" href="javascript:addIpBlackArgs(\'' + escapeHTML(ip) + '\')" title="加入黑名单">' + escapeHTML(ip) + '</a></td></tr><tr><th>类型</th><td>' + escapeHTML(res.method) + '</td><th>过滤器</th><td>' + escapeHTML(res.rule_name) + '</td></tr></tbody></table>\
                        <div><b style="margin-left:10px">URI地址</b></div>\
                        <div class="lib-con pull-left mt10"><div class="divpre">'+ escapeHTML(res.uri) + '</div></div>\
                        <div><b style="margin-left:10px">User-Agent</b></div>\
                        <div class="lib-con pull-left mt10"><div class="divpre">'+ escapeHTML(res.user_agent) + '</div></div>\
                        <div><b style="margin-left:10px">过滤规则</b></div>\
                        <div class="lib-con pull-left mt10"><div class="divpre">'+ escapeHTML(res.rule_name) + '</div></div>\
                         <div><b style="margin-left:10px">Reason</b></div>\
                        <div class="lib-con pull-left mt10"><div class="divpre">'+ escapeHTML(res.reason) + '</div></div>\
                    </div>'
            })
        });
    });
}

function wafLogs(){
    var randstr = getRandomString(10);


    var html = '<div>\
                <div style="padding-bottom:10px;">\
                    <span>网站: </span>\
                    <select class="bt-input-text" name="site" style="margin-left:4px;width:100px;">\
                        <option value="unset">未设置</option>\
                    </select>\
                    <span style="margin-left:10px">时间: </span>\
                    <div class="input-group" style="margin-left:10px;width:350px;display: inline-table;vertical-align: top;">\
                        <div id="search_time" class="input-group-btn btn-group-sm">\
                            <button data-name="today" type="button" class="btn btn-default">今日</button>\
                            <button data-name="yesterday" type="button" class="btn btn-default">昨日</button>\
                            <button data-name="l7" type="button" class="btn btn-default">近7天</button>\
                            <button data-name="l30" type="button" class="btn btn-default">近30天</button>\
                        </div>\
                        <span class="last-span"><input data-name="" type="text" id="time_choose" lay-key="1000001_'+randstr+'" class="form-control btn-group-sm" autocomplete="off" placeholder="自定义时间" style="display: inline-block;font-size: 12px;padding: 0 10px;height:30px;width: 155px;"></span>\
                    </div>\
                    <div style="float:right;">\
                        <button id="UncoverAll" class="btn btn-success btn-sm" style="padding-left: 5px;padding-right: 5px;">解封所有</button>\
                        <button id="testRun" class="btn btn-default btn-sm" style="padding-left: 5px;padding-right: 5px;">测试</button>\
                    </div>\
                </div>\
                <div class="divtable mtb10" id="ws_table"></div>\
            </div>';
    $(".soft-man-con").html(html);
    // wafLogRequest(1);

    $("#UncoverAll").click(function(){
        owPost('clean_drop_ip',{},function(data){
            var rdata = $.parseJSON(data.data);
            var ndata = $.parseJSON(rdata.data);
            if (ndata.status == 0){
                layer.msg("解封所有成功",{icon:1,time:2000,shade: [0.3, '#000']});
            } else{
                layer.msg("解封所有异常:"+ndata.msg,{icon:5,time:2000,shade: [0.3, '#000']});
            }
        });
    });

    //测试demo
    $("#testRun").click(function(){
        owPost('test_run',{},function(data){
            var rdata = $.parseJSON(data.data);
            showMsg(rdata.msg, function(){
                wafLogRequest(1);
            },{icon:1,shade: [0.3, '#000']},2000);
        });
    });

    //日期范围
    laydate.render({
        elem: '#time_choose',
        value:'',
        range:true,
        done:function(value, startDate, endDate){
            if(!value){
                return false;
            }

            $('#search_time button').each(function(){
                $(this).removeClass('cur');
            });

            var timeA  = value.split('-');
            var start = $.trim(timeA[0]+'-'+timeA[1]+'-'+timeA[2])
            var end = $.trim(timeA[3]+'-'+timeA[4]+'-'+timeA[5])
            query_txt = toUnixTime(start + " 00:00:00") + "-"+ toUnixTime(end + " 00:00:00")

            $('#time_choose').attr("data-name",query_txt);
            $('#time_choose').addClass("cur");

            wafLogRequest(1);
        },
    });

    $('#search_time button:eq(0)').addClass('cur');
    $('#search_time button').click(function(){
        $('#search_time button').each(function(){
            if ($(this).hasClass('cur')){
                $(this).removeClass('cur');
            }
        });
        $('#time_choose').attr("data-name",'');
        $('#time_choose').removeClass("cur");

        $(this).addClass('cur');

        wafLogRequest(1);
    });

    owPostN('get_default_site',{},function(rdata){
        $('select[name="site"]').html('');

        var rdata = $.parseJSON(rdata.data);
        var rdata = rdata.data;
        var default_site = rdata["default"];
        var select = '';
        for (var i = 0; i < rdata["list"].length; i++) {
            if (default_site ==  rdata["list"][i]){
                select += '<option value="'+rdata["list"][i]+'" selected>'+rdata["list"][i]+'</option>';
            } else{
                select += '<option value="'+rdata["list"][i]+'">'+rdata["list"][i]+'</option>';
            }
        }
        $('select[name="site"]').html(select);
        wafLogRequest(1);

        $('select[name="site"]').change(function(){
            wafLogRequest(1);
        });
    });

}


function wafOpLogs(){
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
