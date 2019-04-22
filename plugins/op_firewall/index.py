# coding:utf-8

import sys
import io
import os
import time
import subprocess

sys.path.append(os.getcwd() + "/class/core")
import public


app_debug = False
if public.isAppleSystem():
    app_debug = True


def getPluginName():
    return 'op_firewall'


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


def getConf():
    path = public.getServerDir() + "/openresty/nginx/conf/nginx.conf"
    return path


def status():
    path = getConf()
    if not os.path.exists(path):
        return 'stop'

    conf = public.readFile(path)
    if conf.find("#include luawaf.conf;") != -1:
        return 'stop'
    if conf.find("luawaf.conf;") == -1:
        return 'stop'
    return 'start'


def initDreplace():
    path = public.getServerDir() + "/openresty/nginx/conf"
    if not os.path.exists(path + '/waf'):
        sdir = getPluginDir() + '/waf'
        cmd = 'cp -rf ' + sdir + ' ' + path
        public.execShell(cmd)


def start():
    initDreplace()
    # data = public.execShell(file + ' start')
    # if data[1] == '':
    #     return 'ok'
    # return data[1]
    return 'ok'


def stop():
    file = initDreplace()
    data = public.execShell(file + ' stop')
    clearTemp()
    if data[1] == '':
        return 'ok'
    return data[1]


def restart():
    file = initDreplace()
    data = public.execShell(file + ' restart')
    if data[1] == '':
        return 'ok'
    return data[1]


def reload():
    file = initDreplace()
    data = public.execShell(file + ' reload')
    if data[1] == '':
        return 'ok'
    return data[1]


def initdStatus():
    if not app_debug:
        if public.isAppleSystem():
            return "Apple Computer does not support"
    initd_bin = getInitDFile()
    if os.path.exists(initd_bin):
        return 'ok'
    return 'fail'


def initdInstall():
    import shutil
    if not app_debug:
        if public.isAppleSystem():
            return "Apple Computer does not support"

    source_bin = initDreplace()
    initd_bin = getInitDFile()
    shutil.copyfile(source_bin, initd_bin)
    public.execShell('chmod +x ' + initd_bin)
    public.execShell('chkconfig --add ' + getPluginName())
    return 'ok'


def initdUinstall():
    if not app_debug:
        if public.isAppleSystem():
            return "Apple Computer does not support"

    public.execShell('chkconfig --del ' + getPluginName())
    initd_bin = getInitDFile()
    os.remove(initd_bin)
    return 'ok'


def runInfo():
    # 取Openresty负载状态
    try:
        result = public.httpGet('http://127.0.0.1/nginx_status')
        tmp = result.split()
        data = {}
        data['active'] = tmp[2]
        data['accepts'] = tmp[9]
        data['handled'] = tmp[7]
        data['requests'] = tmp[8]
        data['Reading'] = tmp[11]
        data['Writing'] = tmp[13]
        data['Waiting'] = tmp[15]
        return public.getJson(data)
    except Exception as e:
        return 'oprenresty not started'


def errorLogPath():
    return getServerDir() + '/nginx/logs/error.log'


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
        print getConf()
    elif func == 'get_os':
        print getOs()
    elif func == 'run_info':
        print runInfo()
    elif func == 'error_log':
        print errorLogPath()
    else:
        print 'error'
