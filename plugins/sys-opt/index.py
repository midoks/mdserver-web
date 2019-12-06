# coding: utf-8

import time
import random
import os
import json
import re
import sys

sys.path.append(os.getcwd() + "/class/core")
import public


def status():
    return 'start'


def start():
    public.execShell('sysctl -p')
    return "ok"


def stop():
    public.execShell('sysctl -p')
    return 'ok'


def restart():
    public.execShell('sysctl -p')
    return 'ok'


def reload():
    public.execShell('sysctl -p')
    return 'ok'


def sysConf():
    return '/etc/sysctl.conf'


def secRunLog():
    return '/var/log/secure'


def msgRunLog():
    return '/var/log/message'


def cronRunLog():
    return '/var/log/cron'

if __name__ == "__main__":
    func = sys.argv[1]
    if func == 'status':
        print status()
    elif func == 'start':
        print start()
    elif func == 'stop':
        print stop()
    elif func == 'restart':
        print restart()
    elif func == 'reload':
        print reload()
    elif func == 'conf':
        print sysConf()
    elif func == 'sec_run_log':
        print secRunLog()
    elif func == 'msg_run_log':
        print msgRunLog()
    elif func == 'cron_run_log':
        print cronRunLog()
    else:
        print 'err'
