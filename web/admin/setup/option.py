# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------

import json

from flask import request

from admin import model
from admin.model import db, Users

import core.mw as mw

def init_option():
    model.setOption('title', '后羿面板')
    model.setOption('recycle_bin', 'open')
    model.setOption('template', 'default')

    # 后台面板是否关闭
    model.setOption('admin_close', 'no')

    # 未认证状态码
    model.setOption('unauthorized_status', '0')

    # 调式模式,默认关闭
    model.setOption('debug', 'close')

    # basic auth 配置
    model.setOption('basic_auth', json.dumps({'open':False}))




    # 开启后台任务
    # model.setOption('run_bg_task', 'close')

    # 首页展示初始化
    model.setOption('display_index', '[]')

    # 监控默认配置
    model.setOption('monitor_status', 'open', type='monitor')
    model.setOption('monitor_day', '30', type='monitor')
    model.setOption('monitor_only_netio', 'open', type='monitor')

    # 初始化安全路径
    model.setOption('admin_path', mw.getRandomString(8))
    model.setOption('server_ip', '127.0.0.1')

    # 默认备份目录
    model.setOption('backup_path', mw.getFatherDir()+'/backup')
    # 默认站点目录
    model.setOption('site_path', mw.getFatherDir()+'/wwwroot')
    

    return True