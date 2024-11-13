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


import core.mw as mw
import utils.system as system 

cpu_info = system.getCpuInfo()
workers = cpu_info[1]

panel_dir = mw.getPanelDir()


log_dir = mw.getMWLogs()
if not os.path.exists(log_dir):
    os.mkdir(log_dir)

# default port
panel_port = '7200'
default_port_file = panel_dir+'/data/port.pl'
if os.path.exists(default_port_file):
    panel_port = mw.readFile(default_port_file)
    panel_port.strip()
else:
    from utils.firewall import Firewall as MwFirewall
    mw_port = str(random.randint(10000, 65530))
    MwFirewall.instance().addAcceptPort(panel_port, 'Panel端口', 'port')
    mw.writeFile('data/port.pl', panel_port)

bind = []
default_ipv6_file = panel_dir+'/data/ipv6.pl'
if os.path.exists(default_ipv6_file):
    bind.append('[0:0:0:0:0:0:0:0]:%s' % panel_port)
else:
    bind.append('0.0.0.0:%s' % panel_port)

if workers > 2:
    workers = 1

threads = workers * 1
backlog = 512
reload = False
daemon = True
# worker_class = 'geventwebsocket.gunicorn.workers.GeventWebSocketWorker'
worker_class = 'eventlet'
timeout = 600
keepalive = 60
preload_app = True
capture_output = True
access_log_format = '%(t)s %(p)s %(h)s "%(r)s" %(s)s %(L)s %(b)s %(f)s" "%(a)s"'
loglevel = 'info'
errorlog = log_dir + '/panel_error.log'
accesslog = log_dir + '/panel.log'
pidfile = log_dir + '/panel.pid'
