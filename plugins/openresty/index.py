# coding:utf-8

import sys
import io
import os
import time

sys.path.append(os.getcwd() + "/class/core")
import public


def status():
    data = public.execShell(
        "ps -ef|grep openresty |grep -v grep | grep -v python | awk '{print $2}'")
    if data[0] == '':
        return 'stop'
    return 'start'


def start():
    path = os.path.dirname(os.getcwd())
    cmd = path + "/openresty/bin/openresty -c "
    cmd = cmd + path + "/openresty/nginx/conf/nginx.conf"
    data = public.execShell(cmd)
    if data[0] == '':
        return 'ok'
    return 'fail'


def stop():
    path = os.path.dirname(os.getcwd())
    cmd = path + "/openresty/bin/openresty -s stop"
    data = public.execShell(cmd)
    if data[0] == '':
        return 'ok'
    return 'fail'


def reload():
    path = os.path.dirname(os.getcwd())
    cmd = path + "/openresty/bin/openresty -s reload"
    data = public.execShell(cmd)
    if data[0] == '':
        return 'ok'
    return 'fail'


def openrestyConf():
    path = os.path.dirname(os.getcwd())
    return path + "/openresty/nginx/conf/nginx.conf"


if __name__ == "__main__":
    func = sys.argv[1]
    if func == 'status':
        print status()
    elif func == 'start':
        print start()
    elif func == 'stop':
        print stop()
    elif func == 'reload':
        print reload()
    elif func == 'conf':
        print openrestyConf()
    else:
        print 'error'
