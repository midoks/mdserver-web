# coding: utf-8

import time
import random
import os
import json
import re
import sys

sys.path.append(os.getcwd() + "/class/core")
import mw

app_debug = False
if mw.isAppleSystem():
    app_debug = True


def getPluginName():
    return 'solr'


def getPluginDir():
    return mw.getPluginDir() + '/' + getPluginName()


def getServerDir():
    return mw.getServerDir() + '/' + getPluginName()


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
            return (False, mw.returnJson(False, '参数:(' + ck[i] + ')没有!'))
    return (True, mw.returnJson(True, 'ok'))


def status():
    pn = getPluginName()
    data = mw.execShell(
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
    if mw.isAppleSystem():
        user = mw.execShell(
            "who | sed -n '2, 1p' |awk '{print $1}'")[0].strip()

    file_bin = initD_path + '/' + getPluginName()
    if not os.path.exists(file_bin):
        content = mw.readFile(file_tpl)
        content = content.replace('{$SERVER_PATH}', service_path)
        content = content.replace('{$RUN_USER}', user)
        mw.writeFile(file_bin, content)
        mw.execShell('chmod +x ' + file_bin)

    file_py = initD_path + '/' + getPluginName() + '.py'
    if not os.path.exists(file_py):
        content = mw.readFile(getPluginDir() + '/script/full.py')
        mw.writeFile(file_py, content)
        mw.execShell('chmod +x ' + file_py)

    file_incr_py = initD_path + '/' + getPluginName() + '_incr.py'
    if not os.path.exists(file_incr_py):
        content = mw.readFile(getPluginDir() + '/script/incr.py')
        mw.writeFile(file_incr_py, content)
        mw.execShell('chmod +x ' + file_incr_py)

        # realm.properties
        rp_path = getServerDir() + "/server/etc/realm.properties"
        rp_path_tpl = getPluginDir() + "/tpl/realm.properties"

        # if not os.path.exists(rp_path):
        content = mw.readFile(rp_path_tpl)
        mw.writeFile(rp_path, content)

        # web.xml
        web_xml = getServerDir() + "/server/solr-webapp/webapp/WEB-INF/web.xml"
        web_xml_tpl = getPluginDir() + "/tpl/web.xml"
        content = mw.readFile(web_xml_tpl)
        mw.writeFile(web_xml, content)

        # solr-jetty-context.xml
        solr_jetty_context_xml = getServerDir() + "/server/contexts/solr-jetty-context.xml"
        solr_jetty_context_xml_tpl = getPluginDir() + "/tpl/solr-jetty-context.xml"
        content = mw.readFile(solr_jetty_context_xml_tpl)
        mw.writeFile(solr_jetty_context_xml, content)

    log_file = getLog()
    if os.path.exists(log_file):
        mw.writeFile(log_file, '')

    if not mw.isAppleSystem():
        mw.execShell('chown -R solr:solr ' + getServerDir())

    return file_bin


def runShell(shell):
    if mw.isAppleSystem():
        data = mw.execShell(shell)
    else:
        data = mw.execShell('su - solr -c "/bin/bash ' + shell + '"')
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

    solr_log = getServerDir() + "/server/logs/solr.log"
    mw.writeFile(solr_log, "")

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
    mw.execShell('chmod +x ' + initd_bin)

    if not app_debug:
        mw.execShell('chkconfig --add ' + getPluginName())
    return 'ok'


def initdUinstall():
    if not app_debug:
        mw.execShell('chkconfig --del ' + getPluginName())

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
    data['ip'] = mw.getLocalIp()
    data['port'] = '8983'

    content = mw.readFile(path + '/solr.xml')

    rep = "jetty.port:(.*)\}</int>"
    tmp = re.search(rep, content)
    port = tmp.groups()[0]
    data['port'] = port

    return mw.returnJson(True, 'OK', data)


def addCollection():
    args = getArgs()
    data = checkArgs(args, ['name'])
    if not data[0]:
        return data[1]

    name = args['name']
    solr_bin = getServerDir() + "/bin/solr"

    retdata = runShell(solr_bin + ' create -c ' + name)
    if retdata[1] != "":
        return mw.returnJson(False, '添加失败!:' + retdata[1])

    sc_path = getServerDir() + "/server/solr/" + name + "/conf/solrconfig.xml"
    sc_path_tpl = getPluginDir() + "/tpl/solrconfig.xml"
    content = mw.readFile(sc_path_tpl)
    mw.writeFile(sc_path, content)

    sd_path = getServerDir() + "/server/solr/" + name + "/conf/db-data-config.xml"
    sd_path_tpl = getPluginDir() + "/tpl/db-data-config.xml"
    content = mw.readFile(sd_path_tpl)
    mw.writeFile(sd_path, content)

    sd_path = getServerDir() + "/server/solr/" + name + "/conf/managed-schema"
    sd_path_tpl = getPluginDir() + "/tpl/managed-schema"
    content = mw.readFile(sd_path_tpl)
    mw.writeFile(sd_path, content)

    return mw.returnJson(True, '添加成功!:' + retdata[0])


def removeCollection():
    args = getArgs()
    data = checkArgs(args, ['name'])
    if not data[0]:
        return data[1]

    name = args['name']
    solr_bin = getServerDir() + "/bin/solr"

    retdata = runShell(solr_bin + ' delete -c ' + name)
    if retdata[1] != "":
        return mw.returnJson(False, '删除失败!:' + retdata[1])
    return mw.returnJson(True, '删除成功!:' + retdata[0])


def confFileCollection():
    args = getArgs()
    data = checkArgs(args, ['name'])
    if not data[0]:
        return data[1]

    conf_file = getServerDir() + "/server/solr/" + \
        args['name'] + "/conf/" + args['conf_file']
    # print conf_file
    return mw.returnJson(True, 'OK', {'path': conf_file})


def scriptFull():
    return getServerDir() + "/init.d/solr.py"


def scriptIncr():
    return getServerDir() + "/init.d/solr_incr.py"

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
    elif func == 'script_full':
        print scriptFull()
    elif func == 'script_incr':
        print scriptIncr()
    else:
        print 'error'
