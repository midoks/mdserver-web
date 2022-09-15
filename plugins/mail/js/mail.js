
function str2Obj(str){
    var data = {};
    kv = str.split('&');
    for(i in kv){
        v = kv[i].split('=');
        data[v[0]] = v[1];
    }
    return data;
}

function mailPost(method, version, args,callback){
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });

    var req_data = {};
    req_data['name'] = 'mail';
    req_data['func'] = method;
    req_data['version'] = version;
 
    if (typeof(args) == 'string'){
        req_data['args'] = JSON.stringify(str2Obj(args));
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

function mailPostCallbak(method, version, args,callback){
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });

    var req_data = {};
    req_data['name'] = 'mail';
    req_data['func'] = method;
    args['version'] = version;
 
    if (typeof(args) == 'string'){
        req_data['args'] = JSON.stringify(str2Obj(args));
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


function domainList(){
    var con = '<div class="task_block">\
            <button class="btn btn-sm btn-success mb15" style="margin-right:10px;" onclick="mail.edit_domain_view(true)">添加域名</button>\
            <!-- <div class="ssl-item" style="display: flex;width: 150px;float: right;">\
                <span style="display: inline-table;margin-top: 2px; margin-right: 5px;">添加证书</span>\
                <input type="checkbox" id="certificateSSL" class="btswitch btswitch-ios">\
                <label for="certificateSSL" class="btswitch-btn" onclick="mail.open_certificate_view()"></label>\
            </div> -->\
            <button class="btn btn-sm btn-default mb15" style="float:right" id="flush_domain_record">刷新域名记录</button>\
            <div class="domain_table divtable">\
                <table class="table table-hover">\
                    <thead>\
                        <tr>\
                            <th>邮箱域名</th>\
                            <th>MX记录</th>\
                            <th>A记录</th>\
                            <th>SPF记录</th>\
                            <th>DKIM记录</th>\
                            <th>DMARC记录</th>\
                            <th>CatchAll</th>\
                            <th width="160px">SSL</th>\
                            <th width="120px" style="text-align: right;">操作</th>\
                        </tr>\
                    </thead>\
                    <tbody id="domain_list"></tbody>\
                </table>\
            </div>\
            <div class="page" id="domain_page"></div>\
            <ul class="help-info-text c7 mlr20">\
                <li>\
                    <font style="color:red">添加域名后，需要添加MX记录（用于邮箱服务）和TXT记录（用于邮箱反垃圾服务）才能正常使用邮箱服务。</font>\
                </li>\
                <li>\
                    <font style="color:red">提示： 部分云厂商(如：阿里云，腾讯云)默认关闭25端口，需联系厂商开通25端口后才能正常使用邮局服务</font>\
                </li>\
                <li>该自建邮局版本为基础版本，仅提供基础功能，更多功能请耐心等候开发进度。</li>\
            </ul>\
        </div>';

    $(".soft-man-con").html(con);
}



function serviceStatus(){
    var con = '<div class="task_block divtable">\
            <table class="table table-hover">\
                <thead>\
                    <tr>\
                        <th>服务名称</th>\
                        <th>服务状态</th>\
                        <th width="190" style="text-align: center">操作</th>\
                    </tr>\
                </thead>\
                <tbody>\
                    <tr>\
                        <td>Dovecot</td>\
                        <td><span class="dovecot">获取中...</span></td>\
                        <td style="text-align: right">\
                            <a href="javascript:" class="btlink dovecot_start"\
                                onclick="">启动</a>\
                            <a href="javascript:" class="btlink dovecot_stop"\
                                onclick="">停止</a>&nbsp;|&nbsp;\
                            <a href="javascript:" class="btlink"\
                                onclick="">重启</a>&nbsp;|&nbsp;\
                            <a href="javascript:" class="btlink"\
                                onclick="">修复</a>&nbsp;|&nbsp;\
                            <a href="javascript:;" class="btlink"\
                                onclick=">配置文件</a>\
                        </td>\
                    </tr>\
                    <tr>\
                        <td>Opendkim</td>\
                        <td><span class="opendkim">获取中...</span></td>\
                        <td style="text-align: right">\
                            <a href="javascript:" class="btlink opendkim_start"\
                                onclick="">启动</a>\
                            <a href="javascript:" class="btlink opendkim_stop"\
                                onclick="">停止</a>&nbsp;|&nbsp;\
                            <a href="javascript:" class="btlink"\
                                onclick="">重启</a>&nbsp;|&nbsp;\
                            <a href="javascript:" class="btlink"\
                                onclick="">修复</a>&nbsp;|&nbsp;\
                            <a href="javascript:;" class="btlink"\
                                onclick="">配置文件</a>\
                        </td>\
                    </tr>\
                    <tr>\
                        <td>Rspamd</td>\
                        <td><span class="rspamd">获取中...</span></td>\
                        <td style="text-align: right">\
                            <a href="javascript:" class="btlink rspamd_start"\
                                onclick="">启动</a>\
                            <a href="javascript:" class="btlink rspamd_stop"\
                                onclick="">停止</a>&nbsp;|&nbsp;\
                            <a href="javascript:" class="btlink"\
                                onclick="">重启</a>&nbsp;|&nbsp;\
                            <a href="javascript:" class="btlink"\
                                onclick="">修复</a>&nbsp;|&nbsp;\
                            <a href="javascript:;" class="btlink"\
                                onclick="">配置文件</a>\
                        </td>\
                    </tr>\
                    <tr>\
                        <td>Postfix</td>\
                        <td><span class="postfix">获取中...</span></td>\
                        <td style="text-align: right">\
                            <a href="javascript:" class="btlink postfix_start"\
                                onclick="">启动</a>\
                            <a href="javascript:" class="btlink postfix_stop"\
                                onclick="">停止</a>&nbsp;|&nbsp;\
                            <a href="javascript:" class="btlink"\
                                onclick="">重启</a>&nbsp;|&nbsp;\
                            <a href="javascript:" class="btlink"\
                                onclick="">修复</a>&nbsp;|&nbsp;\
                            <a href="javascript:;" class="btlink"\
                                onclick="">配置文件</a>\
                        </td>\
                    </tr>\
                </tbody>\
            </table>\
        </div>';
    $(".soft-man-con").html(con);
}

