# coding:utf-8

import sys
import io
import os
import time
import re

sys.path.append(os.getcwd() + "/class/core")
import mw

app_debug = False
if mw.isAppleSystem():
    app_debug = True


def getPluginName():
    return 'dynamic-tracking'


def getPluginDir():
    return mw.getPluginDir() + '/' + getPluginName()


def getServerDir():
    return mw.getServerDir() + '/' + getPluginName()


def getInitDFile():
    if app_debug:
        return '/tmp/' + getPluginName()
    return '/etc/init.d/' + getPluginName()


def getInitDTpl():
    path = getPluginDir() + "/init.d/" + getPluginName() + ".tpl"
    return path


def getArgs():
    args = sys.argv[3:]
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
    dir_path = getServerDir() + '/trace'
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)
    return 'start'


def dtOp(method):
    return 'ok'


def start():
    return dtOp('start')


def stop():
    return dtOp('stop')


def restart():
    status = dtOp('restart')
    return status


def reload():
    return dtOp('reload')


def initdStatus():
    return 'ok'


def initdInstall():
    return 'ok'


def initdUinstall():
    return 'ok'


def dtFileList():
    dir_path = getServerDir() + '/trace'
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)

    file_info = []
    for name in os.listdir(dir_path):
        if name == ".DS_Store":
            continue

        # print(name)
        info = {}
        try:
            info['name'] = name
        except Exception as e:
            return mw.returnJson(False, str(e))

        file_info.append(info)

    file_info = sorted(file_info, key=lambda x: x['name'], reverse=False)
    return mw.returnJson(True, 'ok!', file_info)


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
    elif func == 'initd_status':
        print(initdStatus())
    elif func == 'initd_install':
        print(initdInstall())
    elif func == 'initd_uninstall':
        print(initdUinstall())
    elif func == 'run_info':
        print(runInfo())
    elif func == 'conf':
        print(getConf())
    elif func == 'run_log':
        print(runLog())
    elif func == 'file_list':
        print(dtFileList())
    else:
        print('error')
