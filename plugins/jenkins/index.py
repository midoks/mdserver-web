# coding: utf-8

import time
import random
import os
import json
import re
import sys
import subprocess

sys.path.append(os.getcwd() + "/class/core")
import public

app_debug = False
if public.isAppleSystem():
    app_debug = True


def getPluginName():
    return 'jenkins'


def getPluginDir():
    return public.getPluginDir() + '/' + getPluginName()


def getServerDir():
    return public.getServerDir() + '/' + getPluginName()


def getInitDFile():
    if app_debug:
        return '/tmp/' + getPluginName()
    return '/etc/init.d/' + getPluginName()


def getInitDTpl():
    return getPluginDir() + "/init.d/" + getPluginName() + ".tpl"


def getLog():
    return "/var/log/jenkins/jenkins.log"


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
            return (False, public.returnJson(False, '参数:(' + ck[i] + ')没有!'))
    return (True, public.returnJson(True, 'ok'))


def status():
    pn = getPluginName()
    cmd = "ps -ef|grep 'jenkins.war' | grep -v grep | awk '{print $2}'"
    data = public.execShell(cmd)
    if data[0] == '':
        return 'stop'
    return 'start'


def start():
    if public.isAppleSystem():
        return "Apple Computer does not support"

    data = public.execShell('service jenkins start')
    if data[1] == '':
        return 'ok'
    return 'fail'


def stop():
    if public.isAppleSystem():
        return "Apple Computer does not support"

    data = public.execShell('service jenkins stop')
    if data[1] == '':
        return 'ok'
    return 'fail'


def restart():
    data = public.execShell('service jenkins restart')
    if data[1] == '':
        return 'ok'
    return 'fail'


def reload():
    data = public.execShell('service jenkins restart')
    if data[1] == '':
        return 'ok'
    return 'fail'


def initdStatus():
    initd_bin = getInitDFile()
    if os.path.exists(initd_bin):
        return 'ok'
    return 'fail'


def initdInstall():

    if not app_debug:
        public.execShell('chkconfig --add ' + getPluginName())
    return 'ok'


def initdUinstall():
    if not app_debug:
        public.execShell('chkconfig --del ' + getPluginName())
    return 'ok'


# rsyncdReceive
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
    elif func == 'run_log':
        print getLog()
    else:
        print 'error'
