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
    return 'socket5'


def getPluginDir():
    return mw.getPluginDir() + '/' + getPluginName()


def getServerDir():
    return mw.getServerDir() + '/' + getPluginName()


def getInitDFile():
    if app_debug:
        return '/tmp/' + getPluginName()
    return '/etc/init.d/ss5'


def initDreplace():
    return getPluginDir() + '/init.d/ss5'


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
    cmd = "ps -ef|grep ss5 |grep -v grep | grep -v python | awk '{print $2}'"
    data = mw.execShell(cmd)
    if data[0] == '':
        return 'stop'
    return 'start'


def initConf():
    ss5_conf = getServerDir() + '/ss5.conf'
    if not os.path.exists(ss5_conf):
        tmp = getPluginDir() + '/tmp/ss5.conf'
        if not os.path.exists(tmp):
            mw.execShell('cp -rf ' + tmp + ' /etc/opt/ss5')
        mw.execShell('cp -rf ' + tmp + ' ' + getServerDir())

        init_file = '/etc/init.d/ss5'
        if os.path.exists(init_file):
            mw.execShell('chmod +x ' + init_file)

    ss5_pwd = getServerDir() + '/ss5.passwd'
    if not os.path.exists(ss5_pwd):
        tmp = getPluginDir() + '/tmp/ss5.passwd'

        if not os.path.exists(tmp):
            mw.execShell('cp -rf ' + tmp + ' /etc/opt/ss5')
        mw.execShell('cp -rf ' + tmp + ' ' + getServerDir())


def start():
    initConf()

    if mw.isAppleSystem():
        return "Apple Computer does not support"

    data = mw.execShell('service ss5 start')
    if data[1] == '':
        return 'ok'
    return data[1]


def stop():
    if mw.isAppleSystem():
        return "Apple Computer does not support"

    data = mw.execShell('service ss5 stop')
    if data[1] == '':
        return 'ok'
    return data[1]


def restart():
    if mw.isAppleSystem():
        return "Apple Computer does not support"

    data = mw.execShell('service ss5 restart')
    if data[1] == '':
        return 'ok'
    return data[1]


def reload():
    data = mw.execShell('service ss5 reload')
    if data[1] == '':
        return 'ok'
    return data[1]


def getPathFile():
    if mw.isAppleSystem():
        return getServerDir() + '/ss5.conf'
    return '/etc/opt/ss5/ss5.conf'


def getPathFilePwd():
    if mw.isAppleSystem():
        return getServerDir() + '/ss5.passwd'
    return '/etc/opt/ss5/ss5.passwd'


def getPathFilePort():
    return '/etc/sysconfig/ss5'


def initdStatus():
    if not app_debug:
        if mw.isAppleSystem():
            return "Apple Computer does not support"
    initd_bin = getInitDFile()
    if os.path.exists(initd_bin):
        return 'ok'
    return 'fail'


def initdInstall():
    import shutil
    if not app_debug:
        if mw.isAppleSystem():
            return "Apple Computer does not support"

    source_bin = initDreplace()
    initd_bin = getInitDFile()
    shutil.copyfile(source_bin, initd_bin)
    mw.execShell('chmod +x ' + initd_bin)
    mw.execShell('chkconfig --add ' + getPluginName())
    return 'ok'


def initdUinstall():
    if not app_debug:
        if mw.isAppleSystem():
            return "Apple Computer does not support"

    mw.execShell('chkconfig --del ' + getPluginName())
    initd_bin = getInitDFile()
    os.remove(initd_bin)
    return 'ok'


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
    elif func == 'conf_pwd':
        print(getPathFilePwd())
    elif func == 'conf_port':
        print(getPathFilePort())
    elif func == 'initd_status':
        print(initdStatus())
    elif func == 'initd_install':
        print(initdInstall())
    elif func == 'initd_uninstall':
        print(initdUinstall())
    else:
        print('error')
