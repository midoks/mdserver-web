# coding:utf-8

import sys
import io
import os
import time
import shutil

sys.path.append(os.getcwd() + "/class/core")
import mw

app_debug = False
if mw.isAppleSystem():
    app_debug = True


def getPluginName():
    return 'v2ray'


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


def status():
    cmd = "ps -ef|grep v2ray |grep -v grep | grep -v 'mdserver-web'| awk '{print $2}'"
    data = mw.execShell(cmd)
    if data[0] == '':
        return 'stop'
    return 'start'


def start():

    shell_cmd = 'service  ' + getPluginName() + ' start'
    data = mw.execShell(shell_cmd)

    if data[0] == '':
        return 'ok'
    return data[1]


def stop():
    shell_cmd = 'service  ' + getPluginName() + ' stop'

    data = mw.execShell(shell_cmd)
    if data[0] == '':
        return 'ok'
    return data[1]


def restart():
    shell_cmd = 'service  ' + getPluginName() + ' restart'
    data = mw.execShell(shell_cmd)

    log_file = getLog()
    if os.path.exists(log_file):
        clear_log_cmd = "echo '' > " + log_file
        mw.execShell(clear_log_cmd)

    if data[0] == '':
        return 'ok'
    return data[1]


def reload():
    shell_cmd = 'service  ' + getPluginName() + ' reload'
    data = mw.execShell(shell_cmd)
    if data[0] == '':
        return 'ok'
    return data[1]


def getPathFile():
    if mw.isAppleSystem():
        return getServerDir() + '/config.json'
    return '/usr/local/etc/v2ray/config.json'


def getInitDFile():
    if app_debug:
        return '/tmp/' + getPluginName()
    return '/etc/init.d/' + getPluginName()


def initdStatus():
    shell_cmd = 'systemctl status v2ray.service | grep loaded | grep "enabled;"'
    data = mw.execShell(shell_cmd)
    if data[0] == '':
        return 'fail'
    return 'ok'


def initdInstall():
    import shutil
    if not app_debug:
        if mw.isAppleSystem():
            return "Apple Computer does not support"

    mw.execShell('systemctl enable ' + getPluginName())
    return 'ok'


def initdUinstall():
    if not app_debug:
        if mw.isAppleSystem():
            return "Apple Computer does not support"

    mw.execShell('systemctl disable ' + getPluginName())
    return 'ok'


def getLog():
    return '/var/log/v2ray/access.log'


def getErrLog():
    return '/var/log/v2ray/error.log'

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
        print(getPathFile())
    elif func == 'initd_status':
        print(initdStatus())
    elif func == 'initd_install':
        print(initdInstall())
    elif func == 'initd_uninstall':
        print(initdUinstall())
    elif func == 'run_log':
        print(getLog())
    elif func == 'error_log':
        print(getErrLog())
    else:
        print('error')
