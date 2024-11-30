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

# 初始化db
from admin import setup
setup.init()

import core.mw as mw
import utils.system as system 
import thisdb

cpu_info = system.getCpuInfo()
workers = cpu_info[1]
# workers = 1

panel_dir = mw.getPanelDir()
log_dir = mw.getMWLogs()
if not os.path.exists(log_dir):
    os.mkdir(log_dir)

data_dir = panel_dir+'/data'
if not os.path.exists(data_dir):
    os.mkdir(data_dir)

# default port
panel_port = '7200'
from utils.firewall import Firewall as MwFirewall
default_port_file = panel_dir+'/data/port.pl'
if os.path.exists(default_port_file):
    panel_port = mw.readFile(default_port_file)
    panel_port.strip()
    MwFirewall.instance().addAcceptPort(panel_port,'PANEL端口', 'port')
else:
    panel_port = str(random.randint(10000, 65530))
    MwFirewall.instance().addPanelPort(panel_port)
    mw.writeFile(default_port_file, panel_port)

bind = []
default_ipv6_file = panel_dir+'/data/ipv6.pl'
if os.path.exists(default_ipv6_file):
    bind.append('[0:0:0:0:0:0:0:0]:%s' % panel_port)
else:
    bind.append('0.0.0.0:%s' % panel_port)

panel_ssl_data = thisdb.getOptionByJson('panel_ssl', default={'open':False})
if panel_ssl_data['open']:
    choose = panel_ssl_data['choose']
    if mw.inArray(['local','nginx'],choose):
        panel_cert = panel_dir+'/ssl/'+choose+'/cert.pem'
        panel_private = panel_dir+'/ssl/'+choose+'/private.pem'
        if os.path.exists(panel_cert) and os.path.exists(panel_private):
            certfile = panel_cert
            keyfile  = panel_private
            ciphers = 'TLSv1 TLSv1.1 TLSv1.2 TLSv1.3'
            ssl_version = 2

if workers > 2:
    workers = 2

threads = workers * 2
backlog = 512
reload = False
daemon = True
# # worker_class = 'geventwebsocket.gunicorn.workers.GeventWebSocketWorker'
worker_class = 'eventlet'
timeout = 600
keepalive = 60
preload_app = False
capture_output = True
access_log_format = '%(t)s %(p)s %(h)s "%(r)s" %(s)s %(L)s %(b)s %(f)s" "%(a)s"'
loglevel = 'info'
errorlog = log_dir + '/panel_error.log'
accesslog = log_dir + '/panel.log'
pidfile = log_dir + '/panel.pid'
