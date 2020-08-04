# coding: utf-8

import time
import random
import os
import json
import re
import sys

sys.path.append(os.getcwd() + "/class/core")
import mw

reload(sys)
sys.setdefaultencoding('utf8')

sys.path.append('/usr/local/lib/python2.7/site-packages')


app_debug = False
if mw.isAppleSystem():
    app_debug = True


def getPluginName():
    return 'qbittorrent'


def getPluginDir():
    return mw.getPluginDir() + '/' + getPluginName()


def getServerDir():
    return mw.getServerDir() + '/' + getPluginName()


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
            return (False, mw.returnJson(False, '参数:(' + ck[i] + ')没有!'))
    return (True, mw.returnJson(True, 'ok'))


def getInitDTpl():
    path = getPluginDir() + "/init.d/" + getPluginName() + ".tpl"
    return path


def getSqlFile():
    file = getPluginDir() + "/conf/qb.sql"
    return file


def getRsyncShell():
    file = getServerDir() + "/workers/rsync.sh"
    return file


def getConf():
    file = getServerDir() + "/qb.conf"
    return file


def getRunLog():
    file = getServerDir() + "/logs.pl"
    return file


def contentReplace(content):
    service_path = mw.getServerDir()
    content = content.replace('{$SERVER_PATH}', service_path)
    content = content.replace('{$WWW_PATH}', mw.getRootDir() + "/wwwroot")
    return content


def initDreplace():

    ddir = getServerDir() + '/workers'
    if not os.path.exists(ddir):
        sdir = getPluginDir() + '/workers'
        mw.execShell('cp -rf ' + sdir + ' ' + getServerDir())

    cfg = getServerDir() + '/qb.conf'
    if not os.path.exists(cfg):
        cfg_tpl = getPluginDir() + '/conf/qb.conf'
        content = mw.readFile(cfg_tpl)
        content = contentReplace(content)
        mw.writeFile(cfg, content)

    file_tpl = getInitDTpl()
    service_path = os.path.dirname(os.getcwd())

    initD_path = getServerDir() + '/init.d'
    if not os.path.exists(initD_path):
        os.mkdir(initD_path)
    file_bin = initD_path + '/' + getPluginName()

    # initd replace
    content = mw.readFile(file_tpl)
    content = contentReplace(content)
    mw.writeFile(file_bin, content)
    mw.execShell('chmod +x ' + file_bin)

    return file_bin


def status():
    data = mw.execShell(
        "ps -ef|grep qbittorrent_worker | grep -v grep | awk '{print $2}'")
    if data[0] == '':
        return 'stop'
    return 'start'


def start():

    cmd = "ps -ef | grep qbittorrent-nox |grep -v grep |awk '{print $2}'"
    ret = mw.execShell(cmd)
    if ret[0] == '':
        mw.execShell('qbittorrent-nox -d')

    file = initDreplace()

    data = mw.execShell(file + ' start')
    if data[1] == '':
        return 'ok'
    return data[1]


def stop():
    file = initDreplace()
    data = mw.execShell(file + ' stop')
    # cmd = "ps -ef | grep qbittorrent-nox |grep -v grep |awk '{print $2}' | xargs kill"
    # mw.execShell(cmd)
    if data[1] == '':
        return 'ok'
    return data[1]


def restart():
    file = initDreplace()
    data = mw.execShell(file + ' restart')
    if data[1] == '':
        return 'ok'
    return data[1]


def reload():
    file = initDreplace()
    data = mw.execShell(file + ' reload')
    if data[1] == '':
        return 'ok'
    return data[1]


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

    mysql_bin = initDreplace()
    initd_bin = getInitDFile()
    shutil.copyfile(mysql_bin, initd_bin)
    mw.execShell('chmod +x ' + initd_bin)
    mw.execShell('chkconfig --add ' + getPluginName())
    return 'ok'


def initdUinstall():
    if not app_debug:
        if mw.isAppleSystem():
            return "Apple Computer does not support"
    initd_bin = getInitDFile()
    os.remove(initd_bin)
    mw.execShell('chkconfig --del ' + getPluginName())
    return 'ok'


def matchData(reg, content):
    tmp = re.search(reg, content).groups()
    return tmp[0]


def getDbConfInfo():
    cfg = getConf()
    content = mw.readFile(cfg)
    data = {}
    data['DB_HOST'] = matchData("DB_HOST\s*=\s(.*)", content)
    data['DB_USER'] = matchData("DB_USER\s*=\s(.*)", content)
    data['DB_PORT'] = matchData("DB_PORT\s*=\s(.*)", content)
    data['DB_PASS'] = matchData("DB_PASS\s*=\s(.*)", content)
    data['DB_NAME'] = matchData("DB_NAME\s*=\s(.*)", content)
    return data


def getQbConf():
    cfg = getConf()
    content = mw.readFile(cfg)
    data = {}
    data['QB_HOST'] = matchData("QB_HOST\s*=\s(.*)", content)
    data['QB_PORT'] = matchData("QB_PORT\s*=\s(.*)", content)
    data['QB_USER'] = matchData("QB_USER\s*=\s(.*)", content)
    data['QB_PWD'] = matchData("QB_PWD\s*=\s(.*)", content)
    return data


def pMysqlDb():
    data = getDbConfInfo()
    conn = mysql.mysql()
    conn.setHost(data['DB_HOST'])
    conn.setUser(data['DB_USER'])
    conn.setPwd(data['DB_PASS'])
    conn.setPort(int(data['DB_PORT']))
    conn.setDb(data['DB_NAME'])
    return conn


def pQbClient():
    from qbittorrent import Client
    info = getQbConf()
    url = 'http://' + info['QB_HOST'] + ':' + info['QB_PORT'] + '/'
    qb = Client(url)
    qb.login(info['QB_USER'], info['QB_PWD'])
    return qb


def getQbUrl():
    info = getQbConf()
    url = 'http://' + info['QB_HOST'] + ':' + info['QB_PORT'] + '/'
    return mw.returnJson(True, 'ok', url)


def qbList():
    args = getArgs()
    # data = checkArgs(args, ['type'])
    # if not data[0]:
    #     return data[1]
    args_type = ''
    if 'type' in args:
        args_type = args['type']

    f = ['downloading', 'completed']
    tfilter = ''
    if args_type in f:
        tfilter = args['type']
    try:
        qb = pQbClient()
        torrents = qb.torrents(filter=tfilter)
        data = {}
        data['type'] = tfilter
        data['torrents'] = torrents
        return mw.returnJson(True, 'ok', data)
    except Exception as e:
        return mw.returnJson(False, str(e))


def qbDel():
    args = getArgs()
    data = checkArgs(args, ['hash'])
    if not data[0]:
        return data[1]
    qb = pQbClient()
    data = qb.delete(args['hash'])
    return mw.returnJson(True, '操作成功!', data)


def qbAdd():
    args = getArgs()
    data = checkArgs(args, ['hash'])
    if not data[0]:
        return data[1]
    url = 'magnet:?xt=urn:btih:' + args['hash']
    qb = pQbClient()
    data = qb.download_from_link(url)
    return mw.returnJson(True, '操作成功!', data)


def test():
    qb = pQbClient()
    # magnet_link = "magnet:?xt=urn:btih:57a0ec92a61c60585f1b7a206a75798aa69285a5"
    # print qb.download_from_link(magnet_link)
    torrents = qb.torrents(filter='downloading')
    for torrent in torrents:
        print mw.returnJson(False, torrent)

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
    elif func == 'rsync_shell':
        print getRsyncShell()
    elif func == 'conf':
        print getConf()
    elif func == 'get_run_Log':
        print getRunLog()
    elif func == 'qb_list':
        print qbList()
    elif func == 'qb_del':
        print qbDel()
    elif func == 'qb_add':
        print qbAdd()
    elif func == 'qb_url':
        print getQbUrl()
    elif func == 'test':
        print test()
    else:
        print 'error'
