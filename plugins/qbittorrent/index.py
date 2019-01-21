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
    return 'qbittorrent'


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


def getInitDTpl():
    path = getPluginDir() + "/init.d/" + getPluginName() + ".tpl"
    return path


def getSqlFile():
    file = getPluginDir() + "/conf/simdht.sql"
    return file


def getDbConf():
    file = getServerDir() + "/db.cfg"
    return file


def getRunLog():
    file = getServerDir() + "/logs.pl"
    return file


def initDreplace():

    ddir = getServerDir() + '/workers'
    if not os.path.exists(ddir):
        sdir = getPluginDir() + '/workers'
        public.execShell('cp -rf ' + sdir + ' ' + getServerDir())

    cfg = getServerDir() + '/db.cfg'
    if not os.path.exists(cfg):
        cfg_tpl = getPluginDir() + '/workers/db.cfg'
        content = public.readFile(cfg_tpl)
        public.writeFile(cfg, content)

    file_tpl = getInitDTpl()
    service_path = os.path.dirname(os.getcwd())

    initD_path = getServerDir() + '/init.d'
    if not os.path.exists(initD_path):
        os.mkdir(initD_path)
    file_bin = initD_path + '/' + getPluginName()

    # initd replace
    content = public.readFile(file_tpl)
    content = content.replace('{$SERVER_PATH}', service_path)
    public.writeFile(file_bin, content)
    public.execShell('chmod +x ' + file_bin)

    return file_bin


def status():
    data = public.execShell(
        "ps -ef|grep qbittorrent-nox-bin | grep -v grep | awk '{print $2}'")
    if data[0] == '':
        return 'stop'
    return 'start'


def start():
    file = initDreplace()

    data = public.execShell(file + ' start')
    if data[1] == '':
        return 'ok'
    return data[1]


def stop():
    file = initDreplace()
    data = public.execShell(file + ' stop')
    if data[1] == '':
        public.execShell('rm -rf /tmp/mysql.sock')
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

    mysql_bin = initDreplace()
    initd_bin = getInitDFile()
    shutil.copyfile(mysql_bin, initd_bin)
    public.execShell('chmod +x ' + initd_bin)
    return 'ok'


def initdUinstall():
    if not app_debug:
        if public.isAppleSystem():
            return "Apple Computer does not support"
    initd_bin = getInitDFile()
    os.remove(initd_bin)
    return 'ok'


def pMysqlDb():
    data = getDbConfInfo()
    conn = mysql.mysql()
    conn.setHost(data['DB_HOST'])
    conn.setUser(data['DB_USER'])
    conn.setPwd(data['DB_PASS'])
    conn.setPort(int(data['DB_PORT']))
    conn.setDb(data['DB_NAME'])
    return conn


def test():
    from qbittorrent import Client
    qb = Client('http://154.48.251.71:8080/')
    qb.login('admin', 'adminadmin')

    # magnet_link = "magnet:?xt=urn:btih:57a0ec92a61c60585f1b7a206a75798aa69285a5"
    # print qb.download_from_link(magnet_link)
    torrents = qb.torrents(filter='downloading')
    for torrent in torrents:
        print public.returnJson(False, torrent)

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
    elif func == 'get_sql':
        print getSqlFile()
    elif func == 'get_db_conf':
        print getDbConf()
    elif func == 'get_run_Log':
        print getRunLog()
    elif func == 'get_trend_data':
        print getTrendData()
    elif func == 'test':
        print test()
    else:
        print 'error'
