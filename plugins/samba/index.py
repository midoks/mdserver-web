# coding: utf-8

import time
import random
import os
import json
import re
import sys

sys.path.append(os.getcwd() + "/class/core")
import public

app_debug = False
if public.isAppleSystem():
    app_debug = True


def getPluginName():
    return 'samba'


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
    data = public.execShell(
        "ps -ef|grep smbd |grep -v grep | grep -v python | awk '{print $2}'")
    if data[0] == '':
        return 'stop'
    return 'start'


def start():
    if public.isAppleSystem():
        return "Apple Computer does not support"

    data = public.execShell('systemctl start smb')
    if data[1] == '':
        return 'ok'
    return 'fail'


def stop():
    if public.isAppleSystem():
        return "Apple Computer does not support"
    data = public.execShell('systemctl stop smb')
    if data[1] == '':
        return 'ok'
    return 'fail'


def restart():
    if public.isAppleSystem():
        return "Apple Computer does not support"
    data = public.execShell('systemctl restart smb')
    if data[1] == '':
        return 'ok'
    return 'fail'


def reload():
    if public.isAppleSystem():
        return "Apple Computer does not support"

    data = public.execShell('systemctl reload smb')
    if data[1] == '':
        return 'ok'
    return 'fail'


def initdStatus():
    if public.isAppleSystem():
        return "Apple Computer does not support"
    initd_bin = getInitDFile()
    if os.path.exists(initd_bin):
        return 'ok'
    return 'fail'


def initdInstall():
    if public.isAppleSystem():
        return "Apple Computer does not support"

    source_bin = initDreplace()
    initd_bin = getInitDFile()
    shutil.copyfile(source_bin, initd_bin)
    public.execShell('chmod +x ' + initd_bin)
    return 'ok'


def initdUinstall():
    if public.isAppleSystem():
        return "Apple Computer does not support"

    initd_bin = getInitDFile()
    os.remove(initd_bin)
    return 'ok'


def smbConf():
    return '/etc/samba/smb.conf'

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
    elif func == 'conf':
        print smbConf():
