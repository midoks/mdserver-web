# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------

from admin import model

import core.mw as mw

def getUnauthStatus(
    code: str | None = '0'
):
    code = str(code)
    data = {}
    data['code'] = code
    if code == '0':
        data['text'] = "默认-安全入口错误提示"
    elif code == '400':
        data['text'] = "400-客户端请求错误"
    elif code == '401':
        data['text'] = "401-未授权访问"
    elif code == '403':
        data['text'] = "403-拒绝访问"
    elif code == '404':
        data['text'] = "404-页面不存在"
    elif code == '408':
        data['text'] = "408-客户端超时"
    elif code == '416':
        data['text'] = "416-无效的请求"
    else:
        data['code'] = '0'
        data['text'] = "默认-安全入口错误提示"
    return data

def getGlobalVar():
    '''
    获取全局变量
    '''
    data = {}
    data['title'] = model.getOption('title', default='后羿面板')
    data['ip'] = model.getOption('server_ip', default='127.0.0.1')

    data['site_path'] = model.getOption('site_path', default=mw.getFatherDir()+'/wwwroot')
    data['backup_path'] = model.getOption('backup_path', default=mw.getFatherDir()+'/backup')
    data['admin_path'] = '/'+model.getOption('admin_path', default='')
    data['debug'] = model.getOption('debug', default='close')
    data['admin_close'] = model.getOption('admin_close', default='no')
    data['site_count'] = model.getSitesCount()
    data['port'] = mw.getHostPort()

    # 获取未认证状态信息
    unauthorized_status = model.getOption('unauthorized_status', default='0')
    data['unauthorized_status'] = getUnauthStatus(code=unauthorized_status)
    data['basic_auth'] = model.getOptionByJson('basic_auth', default={'open':False})

    # 服务器时间
    sformat = 'date +"%Y-%m-%d %H:%M:%S %Z %z"'
    data['systemdate'] = mw.execShell(sformat)[0].strip()


    data['hook_menu'] = model.getOptionByJson('hook_menu',type='hook',default=[])
    data['hook_global_static'] = model.getOptionByJson('hook_global_static',type='hook',default=[])
    
    return data