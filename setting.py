# coding:utf-8


import time
import sys
import os
chdir = os.getcwd()
sys.path.append(chdir + '/class/core')

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


if not os.path.exists(os.getcwd() + '/logs'):
    os.mkdir(os.getcwd() + '/logs')

# default port
mw_port = "7200"
if os.path.exists("data/port.pl"):
    mw_port = mw.readFile('data/port.pl')
    mw_port.strip()
else:
    mw.writeFile('data/port.pl', mw_port)

bind = []
if os.path.exists('data/ipv6.pl'):
    bind.append('[0:0:0:0:0:0:0:0]:%s' % mw_port)
else:
    bind.append('0.0.0.0:%s' % mw_port)

if workers > 2:
    workers = 2

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
errorlog = chdir + '/logs/error.log'
accesslog = chdir + '/logs/access.log'
pidfile = chdir + '/logs/mw.pid'
if os.path.exists(os.getcwd() + '/data/ssl.pl'):
    certfile = 'ssl/certificate.pem'
    keyfile = 'ssl/privateKey.pem'
