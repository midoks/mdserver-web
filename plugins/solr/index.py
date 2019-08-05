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
    return 'solr'


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
    return getServerDir() + "/server/logs/solr.log"


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

    user = 'solr'
    if public.getOs() == 'darwin':
        user = public.execShell(
            "who | sed -n '2, 1p' |awk '{print $1}'")[0].strip()

    file_bin = initD_path + '/' + getPluginName()
    if not os.path.exists(file_bin):
        content = public.readFile(file_tpl)
        content = content.replace('{$SERVER_PATH}', service_path)
        content = content.replace('{$RUN_USER}', user)
        public.writeFile(file_bin, content)
        public.execShell('chmod +x ' + file_bin)

    return file_bin


def runShell(shell):
    if public.isAppleSystem():
        data = public.execShell(shell)
    else:
        data = public.execShell('su - solr -c "/bin/sh ' + shell + '"')
    return data


def start():
    file = initDreplace()
    data = runShell(file + ' start')
    if data[1] == '':
        return 'ok'
    return 'fail'


def stop():
    file = initDreplace()
    data = runShell(file + ' stop')
    if data[1] == '':
        return 'ok'
    return 'fail'


def restart():
    file = initDreplace()
    data = runShell(file + ' restart')
    if data[1] == '':
        return 'ok'
    return 'fail'


def reload():
    file = initDreplace()
    data = runShell(file + ' reload')
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


def collectionList():
    path = getServerDir() + '/server/solr'
    listDir = os.listdir(path)
    data = {}
    dlist = []
    for dirname in listDir:
        dirpath = path + '/' + dirname
        if not os.path.isdir(dirpath):
            continue
        if dirname == 'configsets':
            continue

        tmp = {}
        tmp['name'] = dirname
        dlist.append(tmp)
    data['list'] = dlist
    data['ip'] = public.getLocalIp()
    data['port'] = '8983'

    content = public.readFile(path + '/solr.xml')

    rep = "jetty.port:(.*)\}</int>"
    tmp = re.search(rep, content)
    port = tmp.groups()[0]
    data['port'] = port

    return public.returnJson(True, 'OK', data)


def addCollection():
    args = getArgs()
    data = checkArgs(args, ['name'])
    if not data[0]:
        return data[1]

    name = args['name']
    solr_bin = getServerDir() + "/bin/solr"

    retdata = runShell(solr_bin + ' create -c ' + name)
    if retdata[1] != "":
        return public.returnJson(False, '添加失败!:' + retdata[1])
    return public.returnJson(True, '添加成功!:' + retdata[0])


def removeCollection():
    args = getArgs()
    data = checkArgs(args, ['name'])
    if not data[0]:
        return data[1]

    name = args['name']
    solr_bin = getServerDir() + "/bin/solr"

    retdata = runShell(solr_bin + ' delete -c ' + name)
    if retdata[1] != "":
        return public.returnJson(False, '删除失败!:' + retdata[1])
    return public.returnJson(True, '删除成功!:' + retdata[0])


def confFileCollection():
    args = getArgs()
    data = checkArgs(args, ['name'])
    if not data[0]:
        return data[1]

    conf_file = getServerDir() + "/server/solr/" + \
        args['name'] + "/conf/" + args['conf_file']
    # print conf_file
    return public.returnJson(True, 'OK', {'path': conf_file})


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
    elif func == 'collection_list':
        print collectionList()
    elif func == 'add_collection':
        print addCollection()
    elif func == 'remove_collection':
        print removeCollection()
    elif func == 'conf_file_collection':
        print confFileCollection()
    else:
        print 'error'
