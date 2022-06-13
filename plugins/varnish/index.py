# coding:utf-8

import sys
import io
import os
import time

sys.path.append(os.getcwd() + "/class/core")
import mw

app_debug = False
if mw.isAppleSystem():
    app_debug = True


def getPluginName():
    return 'varnish'


def getPluginDir():
    return mw.getPluginDir() + '/' + getPluginName()


def getServerDir():
    return mw.getServerDir() + '/' + getPluginName()


def getInitDFile():
    if app_debug:
        return '/tmp/' + getPluginName()
    return '/etc/init.d/' + getPluginName()


def getConf():
    path = "/etc/varnish/default.vcl"
    return path


def getConfTpl():
    path = getPluginDir() + "/config/redis.conf"
    return path


def getInitDTpl():
    path = getPluginDir() + "/init.d/" + getPluginName() + ".tpl"
    return path


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
    data = mw.execShell(
        "ps -ef|grep varnish |grep -v grep | grep -v python | grep -v mdserver-web | awk '{print $2}'")

    if data[0] == '':
        return 'stop'
    return 'start'


def start():
    data = mw.execShell('systemctl start ' + getPluginName())
    if data[1] == '':
        return 'ok'
    return 'fail'


def stop():
    data = mw.execShell('systemctl stop ' + getPluginName())
    if data[1] == '':
        return 'ok'
    return 'fail'


def restart():
    data = mw.execShell('systemctl restart ' + getPluginName())
    log_file = getServerDir() + "/data/redis.log"
    mw.execShell("echo '' > " + log_file)
    if data[1] == '':
        return 'ok'
    return 'fail'


def reload():
    # file = initDreplace()
    data = mw.execShell('systemctl restart ' + getPluginName())
    if data[1] == '':
        return 'ok'
    return 'fail'


def runInfo():
    cmd = getServerDir() + "/usr/bin/varnishstat -j"
    data = mw.execShell(cmd)[0].strip()
    return data
    # print(data)
    # result = {}
    # for d in data:
    #     if len(d) < 3:
    #         continue
    #     t = d.strip().split(':')
    #     if not t[0] in res:
    #         continue
    #     result[t[0]] = t[1]
    # return mw.getJson(result)


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


def initdStatus():
    if not app_debug:
        if mw.isAppleSystem():
            return "Apple Computer does not support"

    shell_cmd = 'systemctl status ' + \
        getPluginName() + ' | grep loaded | grep "enabled;"'
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


def runLog():
    return "/var/log/varnish/varnishncsa.log"

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
    elif func == 'config_tpl':
        print(configTpl())
    elif func == 'read_config_tpl':
        print(readConfigTpl())
    else:
        print('error')
