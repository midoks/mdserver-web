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
    data['site_count'] = model.getSitesCount()
    data['port'] = mw.getHostPort()

    # 服务器时间
    sformat = 'date +"%Y-%m-%d %H:%M:%S %Z %z"'
    data['systemdate'] = mw.execShell(sformat)[0].strip()


    data['hook_menu'] = model.getOptionByJson('hook_menu',type='hook',default=[])
    data['hook_global_static'] = model.getOptionByJson('hook_global_static',type='hook',default=[])
    
    return data