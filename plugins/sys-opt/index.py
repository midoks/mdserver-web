# coding: utf-8

import time
import random
import os
import json
import re
import sys

web_dir = os.getcwd() + "/web"
if os.path.exists(web_dir):
    sys.path.append(web_dir)
    os.chdir(web_dir)

import core.mw as mw


def getPluginName():
    return 'sys-opt'


def getPluginDir():
    return mw.getPluginDir() + '/' + getPluginName()


def getServerDir():
    return mw.getServerDir() + '/' + getPluginName()


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


def checkArgs(data, ck=[]):
    for i in range(len(ck)):
        if not ck[i] in data:
            return (False, mw.returnJson(False, '参数:(' + ck[i] + ')没有!'))
    return (True, mw.returnJson(True, 'ok'))


def contentReplace(content):
    service_path = mw.getServerDir()
    content = content.replace('{$ROOT_PATH}', mw.getFatherDir())
    content = content.replace('{$SERVER_PATH}', service_path)
    content = content.replace('{$SERVER_APP}', service_path + '/sys-opt')
    return content


def status():
    return 'start'


def start():
    mw.execShell('sysctl -p')
    return "ok"


def stop():
    mw.execShell('sysctl -p')
    return 'ok'


def restart():
    mw.execShell('sysctl -p')
    return 'ok'


def reload():
    mw.execShell('sysctl -p')
    return 'ok'


def configTpl():
    path = getPluginDir() + '/tpl'
    pathFile = os.listdir(path)
    tmp = []
    for one in pathFile:
        file = path + '/' + one
        tmp.append(file)
    return mw.getJson(tmp)


def readConfigTpl():
    args = getArgs()
    data = checkArgs(args, ['file'])
    if not data[0]:
        return data[1]

    content = mw.readFile(args['file'])
    content = contentReplace(content)
    return mw.returnJson(True, 'ok', content)


def sysConf():
    return '/etc/sysctl.conf'


def secRunLog():
    if os.path.exists('/var/log/auth.log'):
        return '/var/log/auth.log'
    return '/var/log/secure'


def msgRunLog():
    if os.path.exists('/var/log/kern.log'):
        return '/var/log/kern.log'
    return '/var/log/messages'


def cronRunLog():
    if os.path.exists('/var/log/syslog.log'):
        return '/var/log/syslog.log'
    return '/var/log/cron'


def systemRunLog():
    return '/var/log/syslog'

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
        print(sysConf())
    elif func == 'config_tpl':
        print(configTpl())
    elif func == 'read_config_tpl':
        print(readConfigTpl())
    elif func == 'sec_run_log':
        print(secRunLog())
    elif func == 'msg_run_log':
        print(msgRunLog())
    elif func == 'cron_run_log':
        print(cronRunLog())
    elif func == 'sys_run_log':
        print(systemRunLog())
    else:
        print('err')
