# coding:utf-8

import sys
import io
import os
import time

sys.path.append(os.getcwd() + "/class/core")
import mw

app_debug = False
if mw.isAppleSystem():
    app_debug = True


def getPluginName():
    return 'clean'


def getPluginDir():
    return mw.getPluginDir() + '/' + getPluginName()


def getServerDir():
    return mw.getServerDir() + '/' + getPluginName()


def getInitDFile():
    if app_debug:
        return '/tmp/' + getPluginName()
    return '/etc/init.d/' + getPluginName()


def getConf():
    path = getServerDir() + "/clean.conf"
    return path


def getArgs():
    args = sys.argv[2:]
    tmp = {}
    args_len = len(args)

    if args_len == 1:
        t = args[0].strip('{').strip('}')
        t = t.split(':')
        tmp[t[0]] = t[1]
    elif args_len > 1:
        for i in range(len(args)):
            t = args[i].split(':')
            tmp[t[0]] = t[1]

    return tmp


def status():
    if os.path.exists(getConf()):
        return "start"
    return 'stop'


def start():
    file = initDreplace()
    data = mw.execShell(file + ' start')
    if data[1] == '':
        return 'ok'
    return 'fail'


def stop():
    file = initDreplace()
    data = mw.execShell(file + ' stop')
    if data[1] == '':
        return 'ok'
    return 'fail'


def reload():
    file = initDreplace()
    data = mw.execShell(file + ' reload')
    if data[1] == '':
        return 'ok'
    return 'fail'


def cleanLog():
    # 清理日志
    rootDir = "/var/log"
    print("clean start")

    clog = [
        "rm -rf /var/log/cron-*",
        "rm -rf /var/log/maillog-*",
        "rm -rf /var/log/secure-*",
        "rm -rf /var/log/spooler-*",
        "rm -rf /var/log/yum.log-*",
        "rm -rf /var/log/btmp-*",
    ]

    for i in clog:
        print(i)

    # mw.execShell("rm -rf /var/log/cron-*")
    # mw.execShell("rm -rf /var/log/maillog-*")
    # mw.execShell("rm -rf /var/log/secure-*")
    # mw.execShell("rm -rf /var/log/spooler-*")
    print("clean end")

if __name__ == "__main__":
    func = sys.argv[1]
    if func == 'status':
        print(status())
    elif func == 'start':
        print(start())
    elif func == 'stop':
        print(stop())
    elif func == 'restart':
        print(restart())
    elif func == 'reload':
        print(reload())
    elif func == 'conf':
        print(getConf())
    elif func == 'clean':
        cleanLog()
    else:
        print('error')
