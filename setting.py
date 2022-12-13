# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------
# 配置文件
# ---------------------------------------------------------------------------------


import time
import sys
import random
import os

pwd = os.getcwd()
sys.path.append(pwd + '/class/core')

import mw

# cmd = 'ls /usr/local/lib/ | grep python  | cut -d \\  -f 1 | awk \'END {print}\''
# info = mw.execShell(cmd)
# p = "/usr/local/lib/" + info[0].strip() + "/site-packages"
# p_debain = "/usr/local/lib/" + info[0].strip() + "/dist-packages"

# sys.path.append(p)
# sys.path.append(p_debain)

import system_api
cpu_info = system_api.system_api().getCpuInfo()
workers = cpu_info[1]


log_dir = os.getcwd() + '/logs'
if not os.path.exists(log_dir):
    os.mkdir(log_dir)

# default port
mw_port = "7200"
if os.path.exists("data/port.pl"):
    mw_port = mw.readFile('data/port.pl')
    mw_port.strip()
else:
    import firewall_api
    import common
    common.initDB()
    mw_port = str(random.randint(10000, 65530))
    firewall_api.firewall_api().addAcceptPortArgs(mw_port, 'WEB面板', 'port')
    mw.writeFile('data/port.pl', mw_port)

bind = []
if os.path.exists('data/ipv6.pl'):
    bind.append('[0:0:0:0:0:0:0:0]:%s' % mw_port)
else:
    bind.append('0.0.0.0:%s' % mw_port)


# 初始安装时,自动生成安全路径
if not os.path.exists('data/admin_path.pl'):
    admin_path = mw.getRandomString(8)
    mw.writeFile('data/admin_path.pl', '/' + admin_path.lower())

if workers > 2:
    workers = 1

threads = workers * 1
backlog = 512
reload = False
daemon = True
worker_class = 'geventwebsocket.gunicorn.workers.GeventWebSocketWorker'
timeout = 7200
keepalive = 60
preload_app = True
capture_output = True
access_log_format = '%(t)s %(p)s %(h)s "%(r)s" %(s)s %(L)s %(b)s %(f)s" "%(a)s"'
loglevel = 'info'
errorlog = log_dir + '/error.log'
accesslog = log_dir + '/access.log'
pidfile = log_dir + '/mw.pid'
