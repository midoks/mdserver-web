# coding:utf-8

import sys
import io
import os
import time
import subprocess
import re

sys.path.append(os.getcwd() + "/class/core")
import public


app_debug = False
if public.isAppleSystem():
    app_debug = True


def getPluginName():
    return 'mysql'


def getPluginDir():
    return public.getPluginDir() + '/' + getPluginName()

sys.path.append(getPluginDir() + "/class")
import mysql


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
    path = getServerDir() + '/etc/my.cnf'
    return path


def getInitdTpl():
    path = getPluginDir() + '/init.d/mysql.tpl'
    return path


def contentReplace(content):
    service_path = public.getServerDir()
    content = content.replace('{$ROOT_PATH}', public.getRootDir())
    content = content.replace('{$SERVER_PATH}', service_path)
    content = content.replace('{$SERVER_APP_PATH}', service_path + '/mysql')
    return content


def pSqliteDb():
    file = getServerDir() + '/mysql.db'
    name = 'mysql'
    if not os.path.exists(file):
        conn = public.M(name).dbPos(getServerDir(), name)
        csql = public.readFile(getPluginDir() + '/conf/mysql.sql')
        csql_list = csql.split(';')
        for index in range(len(csql_list)):
            conn.execute(csql_list[index], ())
    else:
        conn = public.M(name).dbPos(getServerDir(), name)
    return conn


def pMysqlDb():
    return ''


def initDreplace():
    initd_tpl = getInitdTpl()

    initD_path = getServerDir() + '/init.d'
    if not os.path.exists(initD_path):
        os.mkdir(initD_path)

    file_bin = initD_path + '/' + getPluginName()
    if not os.path.exists(file_bin):
        content = public.readFile(initd_tpl)
        content = contentReplace(content)
        public.writeFile(file_bin, content)
        public.execShell('chmod +x ' + file_bin)

    mysql_conf_dir = getServerDir() + '/etc'
    if not os.path.exists(mysql_conf_dir):
        os.mkdir(mysql_conf_dir)

    mysql_conf = mysql_conf_dir + '/my.cnf'
    if not os.path.exists(mysql_conf):
        mysql_conf_tpl = getPluginDir() + '/conf/my.cnf'
        content = public.readFile(mysql_conf_tpl)
        content = contentReplace(content)
        public.writeFile(mysql_conf, content)

    return file_bin


def status():
    data = public.execShell(
        "ps -ef|grep mysqld |grep -v grep | grep -v python | awk '{print $2}'")
    if data[0] == '':
        return 'stop'
    return 'start'


def getDataDir():

    file = getConf()
    content = public.readFile(file)
    rep = 'datadir\s*=\s*(.*)'
    tmp = re.search(rep, content)
    return tmp.groups()[0].strip()


def initMysqlData():
    datadir = getDataDir()
    serverdir = getServerDir()
    if not os.path.exists(datadir + '/mysql'):
        cmd = 'cd ' + serverdir + ' && ./scripts/mysql_install_db --user=midoks --basedir=' + \
            serverdir + ' --ldata=' + datadir
        public.execShell(cmd)

        pwd = public.getRandomString(16)
        cmd_pass = serverdir + '/bin/mysqladmin -uroot -p12345'
        print cmd_pass
    return True


def myOp(method):
    init_file = initDreplace()
    cmd = init_file + ' ' + method
    if method == 'start':
        initMysqlData()
        subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True,
                         bufsize=4096, stderr=subprocess.PIPE)
        return 'ok'
    else:
        data = public.execShell(cmd)
        if data[1] == '':
            return 'ok'
        return data[1]


def start():
    return myOp('start')


def stop():
    return myOp('stop')


def restart():
    return myOp('restart')


def reload():
    return myOp('reload')


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


def runInfo():
    db = mysql.mysql()
    db.__DB_CNF = getConf()
    data = db.query('show global status')
    print data
    return 'ok'


def getShowLog():
    return 'ok'

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
    elif func == 'run_info':
        print runInfo()
    elif func == 'conf':
        print getConf()
    elif func == 'show_log':
        print getShowLog()
    else:
        print 'error'
