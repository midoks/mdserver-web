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
import public

app_debug = False
if public.isAppleSystem():
    app_debug = True


def getPluginName():
    return 'go-fastdfs'


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
            return (False, public.returnJson(False, '参数:(' + ck[i] + ')没有!'))
    return (True, public.returnJson(True, 'ok'))


def status():
    pn = getPluginName()
    data = public.execShell(
        "ps -ef|grep " + pn + " |grep -v grep | grep -v python | awk '{print $2}'")
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
        content = public.readFile(file_tpl)
        content = content.replace('{$SERVER_PATH}', service_path)
        public.writeFile(file_bin, content)
        public.execShell('chmod +x ' + file_bin)

    return file_bin


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
    data = public.execShell(file + ' restart')
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
    initd_bin = getInitDFile()
    if os.path.exists(initd_bin):
        return 'ok'
    return 'fail'


def initdInstall():
    import shutil

    source_bin = initDreplace()
    initd_bin = getInitDFile()
    shutil.copyfile(source_bin, initd_bin)
    public.execShell('chmod +x ' + initd_bin)

    if not app_debug:
        public.execShell('chkconfig --add ' + getPluginName())
    return 'ok'


def initdUinstall():
    if not app_debug:
        public.execShell('chkconfig --del ' + getPluginName())

    initd_bin = getInitDFile()

    if os.path.exists(initd_bin):
        os.remove(initd_bin)
    return 'ok'


def gfConf():
    return getServerDir() + "/conf/cfg.json"


def gfConfSet():
    gets = [
        {'name': 'addr', 'type': -1, 'ps': '绑定端口'},
        {'name': 'peer_id', 'type': -1, 'ps': '集群内唯一,请使用0-9的单字符'},
        {'name': 'host', 'type': -1, 'ps': '本主机地址'},
        {'name': 'group', 'type': -1, 'ps': '组号'},
        {'name': 'support_group_manage', 'type': 0, 'ps': '是否支持按组（集群）管理'},
        {'name': 'enable_merge_small_file', 'type': 0, 'ps': '是否合并小文件'},
        {'name': 'refresh_interval', 'type': 1, 'ps': '重试同步失败文件的时间'},
        {'name': 'rename_file', 'type': 0, 'ps': '是否自动重命名'},
        {'name': 'enable_web_upload', 'type': 0, 'ps': '是否支持web上传,方便调试'},
        {'name': 'enable_custom_path', 'type': 0, 'ps': '是否支持非日期路径'},
        {'name': 'enable_migrate', 'type': 0, 'ps': '是否启用迁移'},
        {'name': 'enable_cross_origin', 'type': 0, 'ps': '是否开启跨站访问'},
        {'name': 'enable_tus', 'type': 0, 'ps': '是否开启断点续传'}
    ]
    data = public.readFile(gfConf())
    result = json.loads(data)

    ret = []
    for g in gets:
        if g['name'] in result:
            g['value'] = result[g['name']]
            ret.append(g)

    return public.getJson(ret)

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
    elif func == 'breakpoint_log':
        print gfBreakpointLog()
    elif func == 'conf':
        print gfConf()
    elif func == 'gf_conf_set':
        print gfConfSet()
    else:
        print 'error'
