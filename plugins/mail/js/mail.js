var mail  = {
    plugin_name: 'mail',
    post_env_list:['HostName','Postfix-Version','Postfix-install','Sqlite-support','Dovecot-install','Redis-install','Redis-Passwd','Rspamd-install','SElinux'],
    post_env_text:['主机名','Postfix版本','Postfix安装','Sqlite支持','Dovecot安装','Redis安装','Redis密码','Rspamd','SElinux'],
    init: function () {
        var _this = this;

        this.event();

        $('.layui-layer-page').hide();

        setTimeout(function () {
            var win = $(window),
                layer = $('.layui-layer-page');
            layer.show();
            layer.css({
                    'width':'1080px',
                    'top':((win.height()-layer.height())/2)+'px',
                    'left':((win.width()-1000)/2)+'px',
                    'zIndex':'999'
            });
            $('.layui-layer-shade').css('zIndex', '998');
        }, 200);


        _this.check_mail_sys({
            tips: '正在检查邮局服务是否正常,请稍后....',
            hostname: ''
        }, function (res) {
            console.log("aaaa",res);
            if (res.status == false && res.msg == '之前没有安装过邮局系统，请放心安装!') {
                layer.confirm('当前未设置邮局服务，是否现在设置?', {
                    icon: 0,
                    title: '邮局初始化',
                    btn: ['设置', '取消'], //按钮
                    cancel: function () {
                        layer.closeAll();
                    }
                }, function (index) {
                    _this.check_post_env('setup_mail_sys');
                }, function () {
                    layer.closeAll();
                });
            } else {
                // _this.create_domain_list();
                $('.tasklist .tab-nav span:first').click(); // 初始化
                _this.loadScript('/static/ckeditor/ckeditor.js', function () {
                    CKEDITOR.replace('editor1', {
                        customConfig: '/static/ckeditor/config.js?v1.0'
                    })
                });
            }
        });

        // _this.create_domain_list();
    },
    event: function () {
        var _this = this;

        $('.bt-w-main .bt-w-menu p').click(function () {
            var index = $(this).index();
            $(this).addClass('on').siblings().removeClass('on');
            $('.soft-man-con .task_block').eq(index).show().siblings().hide();
            console.log(index);


            switch (index) {
                case 0:
                    _this.create_domain_list();
                    // _this.get_mailSSL_status(function (res) {
                    //     $('#certificateSSL').prop("checked", res);
                    // });
                    break;
            }
        });


        

        console.log(_this);
    },

    // 编辑添加邮箱用户视图-方法
    edit_domain_view: function (type, obj) {
        var _this = this;
        if (obj == undefined) {
            obj = {
                domain: '',
                company_name: '',
                admin_name: '',
                admin_phone: ''
            }
        }
    
        layer.open({
            type: 1,
            title: type ? '添加邮箱域名' : '编辑邮箱域名',
            area: '500px',
            closeBtn: 1,
            btn: [type ? '提交' : '保存', '取消'],
            content: "<div class='bt-form pd20'>\
                <div class='line'>\
                    <span class='tname'>邮箱域名</span>\
                    <div class='info-r c4'>\
                        <input class='bt-input-text mr5' type='text' name='domain'  " + (!type ? "readonly='readonly'" : "") +
                "    value='" + obj.domain + "' placeholder='请输入域名，例如btmail.cn' style='width:320px;' />\
                    </div>\
                </div>\
                <div class='line'>\
                    <span class='tname'>A记录</span>\
                    <div class='info-r c4'>\
                        <input class='bt-input-text mr5' type='text' name='a_record'  " + (!type ? "readonly='readonly'" : "") +
                "    value='" + obj.domain + "' placeholder='请输入A记录,例如:btmail.btmail.cn' style='width:320px;' />\
                    </div>\
                </div>\
                <div class='line'>\
                    <ul class='help-info-text c7 mlr20' style='margin-top: 0px'>\
                        <li style='color: red;'>当前邮箱域名仅支持一级域名</li>\
                        <li>A记录解析参数[主机记录：mail或其他字符]、[记录值：当前服务器IP]</li>\
                        <li>A记录需要解析当前域名A记录，A记录=主机记录值+当前域名</li>\
                    </ul>\
                </div>\
            </div>",
            yes: function (index, layers) {
                var array = [
                        ['domain', '邮箱域名不能为空！', 'a_record', 'A记录值不能为空!']
                    ],
                    _form = {},
                    tel_reg = /^[1][3,4,5,6,7,8,9][0-9]{9}$/;
                for (var i = 0; i < array.length; i++) {
                    if ($('[name="' + array[i][0] + '"]').val() == '') {
                        layer.msg(array[i][1], {
                            icon: 2
                        });
                        return false;
                    } else if (array[i][0] == 'admin_phone' && !tel_reg.test($('[name="' + array[i]
                            [0] + '"]').val())) {
                        layer.msg('管理手机号码格式错误，请重试！', {
                            icon: 2
                        });
                        return false;
                    }
                    _form[array[i][0]] = $('[name="' + array[i][0] + '"]').val();
                    _form[array[i][2]] = $('[name="' + array[i][2] + '"]').val();
                }
                if (type) {
                    _this.add_domain(_form, function (res) {
                        console.log(res);
                        _this.create_domain_list({
                            page: 1,
                            size: 10
                        }, function (res) {
                            var rdata = res.msg.data,
                                hostname = rdata;
                            for (var i = 0; i < rdata.length; i++) {
                                if (rdata[i].domain == _form['domain']) hostname =
                                    rdata[i]['domain']
                            }
                            layer.close(index);
                        });
                    });
                } else {
                    _form['active'] = obj.active;
                    _this.update_domain(_form, function (res) {
                        _this.create_domain_list({
                            page: 1,
                            size: 10
                        }, function (res) {
                            layer.msg(res.msg, {
                                icon: 1
                            });
                            layer.close(index);
                        });
                    });
                }
            }
        })
    },

    // 添加域名_请求
    add_domain: function (obj, callback) {
        this.send({
            tips: '正在添加域名，请稍候...',
            method: 'add_domain',
            data: {
                domain: obj.domain,
                a_record: obj.a_record,
                company_name: obj.company_name,
                admin_name: obj.admin_name,
                admin_phone: obj.admin_phone
            },
            success: function (res) {
                if (callback) callback(res);
            }
        });
    },
    // 获取域名列表_请求
    get_domain_list: function (obj, callback) {
        this.send({
            tips: '正在获取域名列表,请稍候....',
            method: 'get_domains',
            data: {
                p: obj.page,
                size: obj.size
            },
            success: function (res) {
                if (callback) callback(res);
            }
        })
    },

    flush_domain_record: function(obj,callback){
        var _this = this;
        this.send({
            tips: obj == 'all'?'正在刷新所有域名记录，刷新时间视域名数量而定，请稍后...':'Refresh domain record, please wait...',
            method: 'flush_domain_record',
            data: {
                domain: obj
            },
            success: function (res) {
                console.log(res);
                if(res.status) _this.create_domain_list();
                if (callback) callback(res);
            }
        });
    },

    // 创建域名列表-方法
    create_domain_list: function (obj, callback) {
        if (obj == undefined) obj = {
            page: 1,
            size: 10
        }
        var _this = this;
        this.get_domain_list(obj, function (res) {
            console.log(res);
            var _tbody = '',
            rdata = res.data.data;
            _this.domain_list = rdata
            if (rdata.length > 0) {
                for (var i = 0; i < rdata.length; i++) {
                    _tbody += '<tr>\
                      <td>' + rdata[i].domain + '</td>\
                      <td>' + (rdata[i].mx_status ?
                        '<div style="color:#20a53a;"><span class="glyphicon glyphicon-ok" style="margin-right: 7px;"></span>已设置</div>' :
                        '<div style="color:red;display: inline-block;"><span class="glyphicon glyphicon-remove" style="margin-right: 7px;"></span><a href="javascript:;" style="color:red" onclick="mail.set_analysis_mail(\'' +
                        rdata[i].dkim_value + '\',\'' + rdata[i].dmarc_value + '\',\'' + rdata[i]
                        .domain + '\',\'' + rdata[i].mx_record + '\')">未设置记录值</a></div>') + '</td>\
                      <td>' + (rdata[i].a_status ?
                        '<div style="color:#20a53a;"><span class="glyphicon glyphicon-ok" style="margin-right: 7px;"></span>已设置</div>' :
                        '<div style="color:red;display: inline-block;"><span class="glyphicon glyphicon-remove" style="margin-right: 7px;"></span><a href="javascript:;" style="color:red" onclick="mail.set_analysis_mail(\'' +
                        rdata[i].dkim_value + '\',\'' + rdata[i].dmarc_value + '\',\'' + rdata[i]
                        .domain + '\',\'' + rdata[i].mx_record + '\')">未设置记录值</a></div>') + '</td>\
                      <td>' + (rdata[i].spf_status ?
                        '<div style="color:#20a53a;"><span class="glyphicon glyphicon-ok" style="margin-right: 7px;"></span>已设置</span></div>' :
                        '<div style="color:red;display: inline-block;"><span class="glyphicon glyphicon-remove" style="margin-right: 7px;"></span><a href="javascript:;" style="color:red" onclick="mail.set_analysis_mail(\'' +
                        rdata[i].dkim_value + '\',\'' + rdata[i].dmarc_value + '\',\'' + rdata[i]
                        .domain + '\',\'' + rdata[i].mx_record + '\')">未设置记录值</a></div>') + '</td>\
                      <td>' + (rdata[i].dkim_status ?
                        '<div style="color:#20a53a;"><span class="glyphicon glyphicon-ok" style="margin-right: 7px;"></span>已设置</span></div>' :
                        '<div style="color:red;display: inline-block;"><span class="glyphicon glyphicon-remove" style="margin-right: 7px;"></span><a href="javascript:;" style="color:red" onclick="mail.set_analysis_mail(\'' +
                        rdata[i].dkim_value + '\',\'' + rdata[i].dmarc_value + '\',\'' + rdata[i]
                        .domain + '\',\'' + rdata[i].mx_record + '\')">未设置记录值</a></div>') + '</td>\
                      <td>' + (rdata[i].dmarc_status ?
                        '<div style="color:#20a53a;"><span class="glyphicon glyphicon-ok" style="margin-right: 7px;"></span>已设置</span></div>' :
                        '<div style="color:red;display: inline-block;"><span class="glyphicon glyphicon-remove" style="margin-right: 7px;"></span><a href="javascript:;" style="color:red" onclick="mail.set_analysis_mail(\'' +
                        rdata[i].dkim_value + '\',\'' + rdata[i].dmarc_value + '\',\'' + rdata[i]
                        .domain + '\',\'' + rdata[i].mx_record + '\')">未设置记录值</a></div>') + '</td>\
                      <td><div><input type="checkbox" id="'+ rdata[i].domain +'" '+(rdata[i].catch_all ? 'checked':'')+' class="btswitch btswitch-ios catch_all"><label for="'+ rdata[i].domain +'" class="btswitch-btn"></label></div></td>\
                         <td><a href="javascript:;" class="btlink add_certificate" data-index='+i+'>'+(rdata[i].ssl_status?('到期时间: '+rdata[i].ssl_info.notAfter):'添加证书')+'</a></td>\
                      <td style="text-align: right;">' + (rdata[i].mx_status ? (
                        '<a href="javascript:;" class="btlink edit_ground_domain" data-hostname="' +
                        rdata[i].mx_record + '" data-domain="' + rdata[i].domain +
                        '" data-index="' + i + '">用户管理</a>') : (
                        '<a href="javascript:;" class="btlink" onclick="mail.set_analysis_mail(\'' +
                        rdata[i].dkim_value + '\',\'' + rdata[i].dmarc_value + '\',\'' + rdata[
                            i].domain + '\',\'' + rdata[i].mx_record + '\')">添加记录值</a>')) + '&nbsp;|&nbsp;\
                          <a href="javascript:;" class="btlink red del_domain" data-domain="' + rdata[i].domain + '">删除</a>\
                      </td>\
                      </tr>';
                };
            }
            $('#domain_list').html(_tbody);
            $('#domain_page').html(res.page);
            $('#domain_page a').click(function (e) {
                _this.create_domain_list({
                    page: $(this).attr('href').split('p=')[1],
                    size: 10
                })
                e.stopPropagation();
                e.preventDefault();
            })
            $('#flush_domain_record').unbind().on('click',function(e){
                _this.flush_domain_record('all',function(res){
                    layer.msg(res.msg, { icon: res.status ? 1 : 2 });
                });
            })
            $('.add_certificate').unbind().on('click',function(){
                var index = $(this).attr('data-index')
                _this.open_certificate_view(rdata[index].ssl_status, rdata[index].domain, rdata[index].ssl_info.dns, index)
            })
            $('.catch_all').click(function (e) {
                e.preventDefault();
                var _catch = $(this),
                _status = $(this).prop('checked'),
                _html = _status ? '<div style="font-size: 12px;"><span>邮件转寄</span><input class="bt-input-text mr5 catchall" type="text" name="catchall" placeholder="捕获不存在的邮箱，转发到此邮箱" style="width:275px;margin-left: 10px;"></div>' : '确认关闭此功能?',
                loadT = layer.confirm(_html, {title:'CatchAll设置', closeBtn: 2, area: '500'},function(){
                    var _email = _status ? $(".catchall").val() : '',
                    loadS = bt.load();
                    _this.enable_catchall({domain:_catch.attr('id'), email: _email},function(res){
                        loadS.close();
                        if(res.status) _catch.prop('checked', _status);
                        layer.msg(res.msg, { icon: res.status ? 1 : 2 });
                        loadT.close();
                    })
                });
            });
            if (callback) callback(res);
        });
    },

    // 获取邮箱服务是否正常_请求
    check_mail_sys: function (obj, callback) {
        this.send({
            tips: obj.tips,
            method: 'check_mail_sys',
            data: {
                hostname: obj.hostname
            },
            check: true,
            success: function (res) {
                if (callback) callback(res);
            }
        })
    },

    // 检查邮箱环境
    check_mail_env:function(callback){
        this.send({
            tips: '正在检查邮局环境，请稍候...',
            method: 'check_mail_env',
            success: function (res) {
                if (callback) callback(res);
            }
        })
    },

    //检查邮局环境
    check_post_env:function (name) {
        var _this = this;
        var layerE =  layer.open({
            skin:"",
            type: 1,
            closeBtn:1,
            title:'检查邮局环境',
            area: ['600px','520px'], //宽高
            btn: ['提交','取消','刷新列表'],
            content:'\
            <div class="pd20 mlr20 bt-mail-index" accept-charset="utf-8">\
                <div id="checkPostEnv">\
                    <div class="divtable" style="max-height:auto;">\
                        <table class="table table-hover">\
                            <thead style="position:relative;z-index:1;">\
                                <tr>\
                                    <th><span>环境</span></th>\
                                    <th><span>详情</span></th>\
                                    <th><span>操作</span></th>\
                                </tr>\
                            </thead>\
                            <tbody>\
                            </tbody>\
                        </table>\
                    </div>\
                </div>\
                <ul class="help-info-text c7 mlr20">\
                    <li>如果邮局环境异常，请先排除故障。 请在所有异常修复完成后执行下一步操作</li>\
                </ul>\
            </div>',
            success:function(index){
                _this.create_post_env_table();
            },
            cancel:function(){
                layer.closeAll();
            },
            yes:function(){
                if($('#checkPostEnv').find('.set_mail_key').length > 0){
                    layer.msg('请修复好所有的异常再提交');
                }else{
                    switch (name){
                        case 'setup_mail_sys':
                            _this.setup_mail_sys({tips:'正在初始化邮局...'},function(res){
                                layer.close(layerE)
                                layer.msg(res.msg,{icon:res.status?1:2});
                                _this.create_domain_list();
                            });
                            break;
                        case 'change_to_rspamd':
                            _this.change_to_rspamd(function(res){
                                layer.close(layerE)
                                layer.msg(res.msg,{icon:res.status?1:2});
                                _this.create_server_status_table()
                            })
                            break;
                    }
                }
            },
            btn3: function(index, layero){
                _this.create_post_env_table();
                return false;
            },
            btn2: function(index, layero){
                name == 'change_to_rspamd'?layer.close(layerE):layer.closeAll();
            },
           
        })
    },

    //创建邮局环境列表
    create_post_env_table:function (callback){
        var _this = this;
        _this.check_mail_env(function(rdata){
            var res = rdata.data;
            $('#checkPostEnv tbody').empty();
            $.each(_this.post_env_list,function(index,item){
                var list = [];
                var noOperList = ['Redis-install', 'Redis-Passwd', 'SElinux'];
                if(res[item].msg && noOperList.includes(item)){
                    $('#checkPostEnv tbody').append($('<tr><td>'+_this.post_env_text[index] +'</td><td title="'+res[item].msg.toString()+'" class="'+(res[item].status?'green':'set_mail_key red')+'">'+(res[item].status?"就绪":(res[item].msg.toString().length>30?res[item].msg.toString().substring(0,30)+'...':res[item].msg.toString()))+'</td><td>无操作</td></tr>'))
                }else{
                    $('#checkPostEnv tbody').append($(`<tr><td>`+_this.post_env_text[index] +`</td><td title="`+res[item].msg+`" class="${(res[item].status?"green":"red")}">${(res[item].status?"就绪":(res[item].msg !=''?(res[item].msg.toString().length>30?res[item].msg.toString().substring(0,30)+'...':res[item].msg.toString()):"异常"))}</td><td>${(res[item].status?"无操作":"<a href='javascript:;' class='btlink set_mail_key' data-keys= "+ item+" >修复</a>")}</td></tr>`))
                }
                $('#checkPostEnv .divtable').removeClass('mtb10');
            });
        });

        $('#checkPostEnv').unbind().on('click','a',function(){
           var key = $(this).attr('data-keys');
           var confirmA = layer.confirm('是否修复邮局环境?', {
               title: '修复邮局环境',
               icon: 3,
               closeBtn:2,
               btn: ['确定', '取消'],
           },function(index, layero){
                _this.repair_mail_env(key);
            });
       })
       if(callback) callback()
    },

    //修复邮局环境
    repair_mail_env: function (key) {
        var _this = this,_key;
        switch(key) {
            case 'Postfix-Version':
            case 'Postfix-install':
            case 'Sqlite-support':
                _key = 'repair_postfix';
                break;
            case 'Rspamd-install':
                _key = 'install_rspamd';
                break;
            case 'Dovecot-install':
                _key = 'repair_dovecot';
                break;
        }

        console.log(key,_key);
        
        this.send({
            tips: '正在修复' + key + ',请稍候...',
            method: _key,
            success: function (res) {
                layer.msg(res.msg, { icon: res.status?1:2 });
                _this.create_post_env_table();
            }
        })
    },
    
       
    str2Obj:function(str){
        var data = {};
        kv = str.split('&');
        for(i in kv){
            v = kv[i].split('=');
            data[v[0]] = v[1];
        }
        return data;
    },

    send:function(info){
        var tips = info['tips'];
        var method = info['method'];
        var args = info['data'];
        var callback = info['success'];

        var loadT = layer.msg(tips, { icon: 16, time: 0, shade: 0.3 });

        var data = {};
        data['name'] = 'mail';
        data['func'] = method;
        data['version'] = $('.plugin_version').attr('version');
     
        if (typeof(args) == 'string'){
            data['args'] = JSON.stringify(this.str2Obj(args));
        } else {
            data['args'] = JSON.stringify(args);
        }

        $.post('/plugins/run', data, function(res) {
            layer.close(loadT);
            if (!res.status){
                layer.msg(res.msg,{icon:2,time:10000});
                return;
            }

            var ret_data = $.parseJSON(res.data);
            console.log("send:",ret_data);
            // if (!ret_data.status){
            //     layer.msg(ret_data.msg,{icon:2,time:2000});
            //     return;
            // }

            // console.log("send2:",ret_data);

            if(typeof(callback) == 'function'){
                callback(ret_data);
            }
        },'json'); 
    },
    postCallback:function(info){
        var tips = info['tips'];
        var method = info['method'];
        var args = info['data'];
        var callback = info['success'];
        
        var loadT = layer.msg(tips, { icon: 16, time: 0, shade: 0.3 });

        var data = {};
        data['name'] = 'mail';
        data['func'] = method;
        data['version'] = $('.plugin_version').attr('version');
     
        if (typeof(args) == 'string'){
            data['args'] = JSON.stringify(this.str2Obj(args));
        } else {
            data['args'] = JSON.stringify(args);
        }

        $.post('/plugins/callback', data, function(res) {

            layer.close(loadT);
            if (!res.status){
                layer.msg(res.msg,{icon:2,time:10000});
                return;
            }

            var ret_data = $.parseJSON(res.data);
              if (!ret_data.status){
                layer.msg(ret_data.msg,{icon:2,time:2000});
                return;
            }

            if(typeof(callback) == 'function'){
                callback(res);
            }
        },'json');
    }
}
