
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



function wafScreen(){

    var con = '<div class="wavbox alert alert-success" style="margin-right:16px">总拦截<span>0</span>次</div>';
    con += '<div class="wavbox alert alert-info" style="margin-right:16px">安全防护<span>0</span>天</div>';

    con += '<div class="gjcs">\
        <div class="line"><span class="name">POST渗透</span><span class="val">0</span></div>\
        <div class="line"><span class="name">GET渗透</span><span class="val">0</span></div>\
        <div class="line"><span class="name">CC攻击</span><span class="val">0</span></div>\
        <div class="line"><span class="name">恶意User-Agent</span><span class="val">0</span></div>\
        <div class="line"><span class="name">Cookie渗透</span><span class="val">0</span></div>\
        <div class="line"><span class="name">恶意扫描</span><span class="val">0</span></div>\
        <div class="line"><span class="name">恶意HEAD请求</span><span class="val">0</span></div>\
        <div class="line"><span class="name">URI自定义拦截</span><span class="val">0</span></div>\
        <div class="line"><span class="name">URI保护</span><span class="val">0</span></div>\
        <div class="line"><span class="name">恶意文件上传</span><span class="val">0</span></div>\
        <div class="line"><span class="name">禁止的扩展名</span><span class="val">0</span></div>\
        <div class="line"><span class="name">禁止PHP脚本</span><span class="val">0</span></div>\
        </div>';

    con += '<div style="width:480px;"><ul class="help-info-text c7">\
        <li>在此处关闭防火墙后,所有站点将失去保护</li>\
        <li>网站防火墙会使nginx有一定的性能损失(&lt;5% 10C静态并发测试结果)</li>\
        <li>网站防火墙仅主要针对网站渗透攻击,暂时不具备系统加固功能</li>\
        </ul></div>';

    $(".soft-man-con").html(con);
}


function wafGloabl(){
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

    con += '<div style="width:480px;"><ul class="help-info-text c7">\
        <li>继承: 全局设置将在站点配置中自动继承为默认值</li>\
        <li>优先级: IP白名单 > IP黑名单 > URL白名单 > URL黑名单 > CC防御 > 禁止国外IP访问 > User-Agent > URI过滤 > URL参数 > Cookie > POST</li>\
        </ul></div>';
    $(".soft-man-con").html(con);
}


function wafSite(){
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
