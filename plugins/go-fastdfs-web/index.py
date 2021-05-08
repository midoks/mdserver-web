# coding: utf-8

import time
import random
import os
import json
import re
import sys
import subprocess
import threading

sys.path.append(os.getcwd() + "/class/core")
import mw

app_debug = False
if mw.isAppleSystem():
    app_debug = True


def getPluginName():
    return 'go-fastdfs-web'


def getPluginDir():
    return mw.getPluginDir() + '/' + getPluginName()


def getServerDir():
    return mw.getServerDir() + '/' + getPluginName()


def getInitDFile():
    if app_debug:
        return '/tmp/' + getPluginName()
    return '/etc/init.d/' + getPluginName()


def getInitDTpl():
    return getPluginDir() + "/init.d/" + getPluginName() + ".tpl"


def getLog():
    return getServerDir() + "/log/fileserver.log"


def gfBreakpointLog():
    return getServerDir() + "/log/tusd.log"


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


def status():
    pn = getPluginName()
    data = mw.execShell(
        "ps -ef|grep " + pn + " | grep -v grep | grep -v python | awk '{print $2}'")
    if data[0] == '':
        return 'stop'
    return 'start'


def initDreplace():

    file_tpl = getInitDTpl()
    service_path = os.path.dirname(os.getcwd())

    initD_path = getServerDir() + '/init.d'
    if not os.path.exists(initD_path):
        os.mkdir(initD_path)

    file_bin = initD_path + '/' + getPluginName()
    if not os.path.exists(file_bin):
        content = mw.readFile(file_tpl)
        content = content.replace('{$SERVER_PATH}', service_path)
        mw.writeFile(file_bin, content)
        mw.execShell('chmod +x ' + file_bin)

    return file_bin


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


def restart():
    file = initDreplace()
    data = mw.execShell(file + ' restart')
    if data[1] == '':
        return 'ok'
    return 'fail'


def reload():
    file = initDreplace()
    data = mw.execShell(file + ' reload')
    if data[1] == '':
        return 'ok'
    return 'fail'


def initdStatus():
    initd_bin = getInitDFile()
    if os.path.exists(initd_bin):
        return 'ok'
    return 'fail'


def initdInstall():
    import shutil

    source_bin = initDreplace()
    initd_bin = getInitDFile()
    shutil.copyfile(source_bin, initd_bin)
    mw.execShell('chmod +x ' + initd_bin)

    if not app_debug:
        mw.execShell('chkconfig --add ' + getPluginName())
    return 'ok'


def initdUinstall():
    if not app_debug:
        mw.execShell('chkconfig --del ' + getPluginName())

    initd_bin = getInitDFile()

    if os.path.exists(initd_bin):
        os.remove(initd_bin)
    return 'ok'


def gfConf():
    return getServerDir() + "/config/application-prod.properties"


def getLog():
    return getServerDir() + "/logs/go-fastdfs-web.log"


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
    elif func == 'run_log':
        print(getLog())
    elif func == 'conf':
        print(gfConf())
    else:
        print('error')
