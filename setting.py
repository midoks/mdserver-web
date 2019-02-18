# coding:utf-8


import time
import sys
import os
chdir = os.getcwd()
sys.path.append(chdir + '/class/core')
sys.path.append("/usr/local/lib/python2.7/site-packages")
import public
import system_api

cpu_info = system_api.system_api().getCpuInfo()

if not os.path.exists(os.getcwd() + '/logs'):
    os.mkdir(os.getcwd() + '/logs')

bt_port = public.readFile('data/port.pl')
bind = ['0.0.0.0:%s' % bt_port]
workers = cpu_info[1] + 1
threads = 1
backlog = 512
reload = True
daemon = True
# worker_class = 'geventwebsocket.gunicorn.workers.GeventWebSocketWorker'
timeout = 7200
keepalive = 1
capture_output = True
access_log_format = '%(t)s %(p)s %(h)s "%(r)s" %(s)s %(L)s %(b)s %(f)s" "%(a)s"'
loglevel = 'info'
errorlog = chdir + '/logs/error.log'
accesslog = chdir + '/logs/access.log'
pidfile = chdir + '/logs/mw.pid'
if os.path.exists(os.getcwd() + '/data/ssl.pl'):
    certfile = 'ssl/certificate.pem'
    keyfile = 'ssl/privateKey.pem'
