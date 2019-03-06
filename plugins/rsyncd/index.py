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
    return 'rsyncd'


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
        "ps -ef|grep rsync |grep -v grep | grep -v python | awk '{print $2}'")
    if data[0] == '':
        return 'stop'
    return 'start'


def appConf():
    if public.isAppleSystem():
        return getServerDir() + '/rsyncd.conf'
    return '/etc/rsyncd.conf'


def getLog():
    conf_path = appConf()
    conf = public.readFile(conf_path)
    rep = 'log file\s*=\s*(.*)'
    tmp = re.search(rep, conf)
    if not tmp:
        return ''
    return tmp.groups()[0]


def initConf():
    import re
    conf_path = appConf()
    conf = public.readFile(conf_path)
    conf = re.sub('#*(.*)', '', conf)
    conf_tpl_path = getPluginDir() + '/conf/rsyncd.conf'
    if conf.strip() == '':
        content = public.readFile(conf_tpl_path)
        public.writeFile(conf_path, content)


def start():
    initConf()

    if public.isAppleSystem():
        return "Apple Computer does not support"

    data = public.execShell('systemctl start rsyncd.service')
    if data[1] == '':
        return 'ok'
    return 'fail'


def stop():
    if public.isAppleSystem():
        return "Apple Computer does not support"
    data = public.execShell('systemctl stop rsyncd.service')
    if data[1] == '':
        return 'ok'
    return 'fail'


def restart():
    if public.isAppleSystem():
        return "Apple Computer does not support"
    data = public.execShell('systemctl restart rsyncd.service')
    if data[1] == '':
        return 'ok'
    return 'fail'


def reload():
    if public.isAppleSystem():
        return "Apple Computer does not support"

    data = public.execShell('systemctl reload rsyncd.service')
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
    elif func == 'conf':
        print appConf()
    elif func == 'run_log':
        print getLog()
    else:
        print 'error'
