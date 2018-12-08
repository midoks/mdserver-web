# coding: utf-8

import time
import random
import os
import urllib
import binascii
import json
import re
import sys

sys.path.append(os.getcwd() + "/class/core")
import public


app_debug = False
if public.getOs() == 'darwin':
    app_debug = True


def getPluginName():
    return 'csvn'


def getPluginDir():
    return public.getPluginDir() + '/' + getPluginName()


def getServerDir():
    return public.getServerDir() + '/' + getPluginName()


def getInitDFile():
    if app_debug:
        return '/tmp/' + getPluginName()
    return '/etc/init.d/' + getPluginName()


def getArgs():
    args = sys.argv[2:]
    tmp = {}
    for i in range(len(args)):
        t = args[i].split(':')
        tmp[t[0]] = t[1]
    return tmp


def initDreplace():

    file_tpl = getConf()
    service_path = os.path.dirname(os.getcwd())

    initD_path = getServerDir() + '/init.d'
    if not os.path.exists(initD_path):
        os.mkdir(initD_path)
    file_bin = initD_path + '/memcached'

    # if os.path.exists(file_bin):
    #     return file_bin

    content = public.readFile(file_tpl)
    content = content.replace('{$SERVER_PATH}', service_path)

    public.writeFile(file_bin, content)
    public.execShell('chmod +x ' + file_bin)
    return file_bin


def status():
    data = public.execShell(
        "ps -ef|grep " + getPluginName() + " |grep -v grep | grep -v python | awk '{print $2}'")
    if data[0] == '':
        return 'stop'
    return 'start'


def start():
    file = initDreplace()
    data = public.execShell(file + ' start')
    if data[1] == '':
        return 'ok'
    return 'fail'


def stop():
    file = initDreplace()
    data = public.execShell(file + ' stop')
    if data[1] == '':
        return 'ok'
    return 'fail'


def restart():
    file = initDreplace()
    data = public.execShell(file + ' reload')
    if data[1] == '':
        return 'ok'
    return 'fail'


def reload():
    file = initDreplace()
    data = public.execShell(file + ' reload')
    if data[1] == '':
        return 'ok'
    return 'fail'


def initdStatus():
    if not app_debug:
        os_name = public.getOs()
        if os_name == 'darwin':
            return "Apple Computer does not support"
    initd_bin = getInitDFile()
    if os.path.exists(initd_bin):
        return 'ok'
    return 'fail'


def initdInstall():
    import shutil
    if not app_debug:
        os_name = public.getOs()
        if os_name == 'darwin':
            return "Apple Computer does not support"

    mem_bin = initDreplace()
    initd_bin = getInitDFile()
    shutil.copyfile(mem_bin, initd_bin)
    public.execShell('chmod +x ' + initd_bin)
    return 'ok'

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
    elif func == 'initd_status':
        print initdStatus()
    elif func == 'initd_install':
        print initdInstall()
    elif func == 'initd_uninstall':
        print initdUinstall()
    elif func == 'run_info':
        print runInfo()
    elif func == 'conf':
        print getConf()
    elif func == 'save_conf':
        print saveConf()
    else:
        print 'fail'
