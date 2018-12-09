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
    initd_file = getInitDFile()

    if not os.path.exists(initd_file):
        return getServerDir()

    return initd_file


def status():
    data = public.execShell(
        "ps -ef|grep " + getPluginName() + " |grep -v grep | grep -v python | awk '{print $2}'")
    if data[0] == '':
        return 'stop'
    return 'start'


def csvnOp(method):

    if not app_debug:
        os_name = public.getOs()
        if os_name == 'darwin':
            return "Apple Computer does not support"

    _initd_csvn = '/etc/init.d/csvn'
    _initd_csvn_httpd = '/etc/init.d/csvn-httpd'

    ret_csvn = public.execShell(_initd_csvn + ' ' + method)
    ret_csvn_httpd = public.execShell(_initd_csvn + ' ' + method)
    if ret_csvn[1] == '' and ret_csvn_httpd[1] == '':
        return 'ok'
    return 'fail'


def start():
    return csvnOp('start')


def stop():
    return csvnOp('stop')


def restart():
    return csvnOp('restart')


def reload():
    return csvnOp('reload')


def initdStatus():
    if not app_debug:
        os_name = public.getOs()
        if os_name == 'darwin':
            return "Apple Computer does not support"

    _initd_csvn = '/etc/init.d/csvn'
    _initd_csvn_httpd = '/etc/init.d/csvn-httpd'

    if os.path.exists(_initd_csvn) and os.path.exists(_initd_csvn_httpd):
        return 'ok'
    return 'fail'


def initdInstall():
    import shutil
    if not app_debug:
        os_name = public.getOs()
        if os_name == 'darwin':
            return "Apple Computer does not support"

    _csvn = getServerDir() + '/bin/csvn'
    _csvn_httpd = getServerDir() + '/bin/csvn-httpd'

    ret_csvn = public.execShell(_csvn + ' install')
    ret_csvn_httpd = public.execShell(_csvn_httpd + ' install')
    if ret_csvn[1] == '' and ret_csvn_httpd[1] == '':
        return 'ok'
    return 'fail'


def initdUinstall():
    if not app_debug:
        os_name = public.getOs()
        if os_name == 'darwin':
            return "Apple Computer does not support"

    _csvn = getServerDir() + '/bin/csvn'
    _csvn_httpd = getServerDir() + '/bin/csvn-httpd'

    ret_csvn = public.execShell(_csvn + ' remove')
    ret_csvn_httpd = public.execShell(_csvn_httpd + ' remove')

    print ret_csvn, ret_csvn_httpd
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
