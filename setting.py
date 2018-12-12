import os
import time
import sys

sys.path.append(os.getcwd() + '/class/core')
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
reload = False
daemon = False
timeout = 7200
keepalive = 1
chdir = os.getcwd()
capture_output = True
access_log_format = '%(t)s %(p)s %(h)s "%(r)s" %(s)s %(L)s %(b)s %(f)s" "%(a)s"'
loglevel = 'info'
errorlog = os.getcwd() + '/logs/error.log'
accesslog = os.getcwd() + '/logs/access.log'
pidfile = os.getcwd() + '/logs/mw.pid'
# if os.path.exists(chdir + '/data/ssl.pl'):
#     certfile = 'ssl/certificate.pem'
#     keyfile = 'ssl/privateKey.pem'
