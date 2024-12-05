# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------

import json

import core.mw as mw
import thisdb

def init_option():
    thisdb.setOption('title', '夸父面板')
    thisdb.setOption('recycle_bin', 'open')
    thisdb.setOption('template', 'default')

    # SSL邮件地址
    thisdb.setOption('ssl_email', '')

    # 后台面板是否关闭
    thisdb.setOption('admin_close', 'no')

    # 未认证状态码
    thisdb.setOption('unauthorized_status', '0')

    # 调式模式,默认关闭
    thisdb.setOption('debug', 'close')

    # basic auth 配置
    thisdb.setOption('basic_auth', json.dumps({'open':False}))

    # 二步验证|默认关闭
    thisdb.setOption('two_step_verification', json.dumps({'open':False}))

    # 开启后台任务
    # thisdb.setOption('run_bg_task', 'close')

    # 首页展示初始化
    thisdb.setOption('display_index', '[]')

    # 监控默认配置
    thisdb.setOption('monitor_status', 'open', type='monitor')
    thisdb.setOption('monitor_day', '30', type='monitor')
    thisdb.setOption('monitor_only_netio', 'open', type='monitor')

    # 初始化安全路径
    thisdb.setOption('admin_path', mw.getRandomString(8))

    # API是否开启|默认关闭
    thisdb.setOption('panel_api', json.dumps({'open':False}))

    # 获取服务器IP
    ip = mw.getLocalIp()
    thisdb.setOption('server_ip', ip)

    # 默认备份目录
    thisdb.setOption('backup_path', mw.getFatherDir()+'/backup')
    # 默认站点目录
    thisdb.setOption('site_path', mw.getFatherDir()+'/wwwroot')


    # 异步邮件通知
    thisdb.setOption('notify_email', json.dumps({'open':False}), type='notify')
    # 异步Telegram Bot 通知
    thisdb.setOption('notify_tgbot', json.dumps({'open':False}), type='notify')
    
    return True