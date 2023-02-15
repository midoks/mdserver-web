# coding:utf-8

import sys
import io
import os
import time
import re
import json

sys.path.append(os.getcwd() + "/class/core")
import mw

app_debug = False
if mw.isAppleSystem():
    app_debug = True


def getPluginName():
    return 'migration_api'


def getPluginDir():
    return mw.getPluginDir() + '/' + getPluginName()


def getServerDir():
    return mw.getServerDir() + '/' + getPluginName()


def getInitDFile():
    if app_debug:
        return '/tmp/' + getPluginName()
    return '/etc/init.d/' + getPluginName()


def getConf():
    path = getServerDir() + "/ma.cfg"
    return path


def getCfgData():
    path = getConf()
    if not os.path.exists(path):
        mw.writeFile(path, '{}')

    t = mw.readFile(path)
    return json.loads(t)


def getArgs():
    args = sys.argv[2:]
    tmp = {}
    args_len = len(args)

    if args_len == 1:
        t = args[0].strip('{').strip('}')
        if t.strip() == '':
            tmp = []
        else:
            t = t.split(':')
            tmp[t[0]] = t[1]
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


def status():
    return 'start'


def initDreplace():
    return 'ok'


def stepOne():
    args = getArgs()
    data = checkArgs(args, ['url', 'token'])
    if not data[0]:
        return data[1]

    data = getCfgData()
    print(data)

    return mw.returnJson(True, 'ok')


if __name__ == "__main__":
    func = sys.argv[1]
    if func == 'status':
        print(status())
    elif func == 'start':
        print(start())
    elif func == 'stop':
        print(stop())
    elif func == 'step_one':
        print(stepOne())
    else:
        print('error')
