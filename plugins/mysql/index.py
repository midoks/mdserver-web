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


def pSqliteDb(dbname='databases'):
    file = getServerDir() + '/mysql.db'
    name = 'mysql'
    if not os.path.exists(file):
        conn = public.M(dbname).dbPos(getServerDir(), name)
        csql = public.readFile(getPluginDir() + '/conf/mysql.sql')
        csql_list = csql.split(';')
        for index in range(len(csql_list)):
            conn.execute(csql_list[index], ())
    else:
        conn = public.M(dbname).dbPos(getServerDir(), name)
    return conn


def pMysqlDb():
    db = mysql.mysql()
    db.__DB_CNF = getConf()
    db.setPwd(pSqliteDb('config').where(
        'id=?', (1,)).getField('mysql_root'))
    return db


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


def getShowLogFile():
    file = getConf()
    content = public.readFile(file)
    rep = 'slow-query-log-file\s*=\s*(.*)'
    tmp = re.search(rep, content)
    return tmp.groups()[0].strip()


def pGetDbUser():
    if public.isAppleSystem():
        user = public.execShell(
            "who | sed -n '2, 1p' |awk '{print $1}'")[0].strip()
        return user
    return 'mysql'


def initMysqlData():
    datadir = getDataDir()
    if not os.path.exists(datadir + '/mysql'):
        serverdir = getServerDir()
        user = pGetDbUser()
        cmd = 'cd ' + serverdir + ' && ./scripts/mysql_install_db --user=' + user + ' --basedir=' + \
            serverdir + ' --ldata=' + datadir
        public.execShell(cmd)
        return 0
    return 1


def initMysqlPwd():
    time.sleep(3)

    serverdir = getServerDir()

    pwd = public.getRandomString(16)
    cmd_pass = serverdir + '/bin/mysqladmin -uroot password ' + pwd
    pSqliteDb('config').where('id=?', (1,)).save('mysql_root', (pwd,))
    public.execShell(cmd_pass)
    return True


def myOp(method):
    import commands
    init_file = initDreplace()
    cmd = init_file + ' ' + method
    try:
        initData = initMysqlData()
        subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True,
                         bufsize=4096, stderr=subprocess.PIPE)
        if (initData == 0):
            initMysqlPwd()
        return 'ok'
    except Exception as e:
        return str(e)


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


def getMyPort():
    file = getConf()
    content = public.readFile(file)
    rep = 'port\s*=\s*(.*)'
    tmp = re.search(rep, content)
    return tmp.groups()[0].strip()


def setMyPort():
    args = getArgs()
    if not 'port' in args:
        return 'port missing'

    port = args['port']
    file = getConf()
    content = public.readFile(file)
    rep = "port\s*=\s*([0-9]+)\s*\n"
    content = re.sub(rep, 'port = ' + port + '\n', content)
    public.writeFile(file, content)
    restart()
    return public.returnJson(True, '编辑成功!')


def runInfo():
    db = pMysqlDb()
    data = db.query('show global status')
    gets = ['Max_used_connections', 'Com_commit', 'Com_rollback', 'Questions', 'Innodb_buffer_pool_reads', 'Innodb_buffer_pool_read_requests', 'Key_reads', 'Key_read_requests', 'Key_writes',
            'Key_write_requests', 'Qcache_hits', 'Qcache_inserts', 'Bytes_received', 'Bytes_sent', 'Aborted_clients', 'Aborted_connects',
            'Created_tmp_disk_tables', 'Created_tmp_tables', 'Innodb_buffer_pool_pages_dirty', 'Opened_files', 'Open_tables', 'Opened_tables', 'Select_full_join',
            'Select_range_check', 'Sort_merge_passes', 'Table_locks_waited', 'Threads_cached', 'Threads_connected', 'Threads_created', 'Threads_running', 'Connections', 'Uptime']

    try:
        # print data
        if data[0] == 1045 or data[0] == 2003:
            pwd = db.getPwd()
            return public.returnJson(False, 'mysql password error:' + pwd + '!')
    except Exception as e:
        pass

    result = {}
    for d in data:
        for g in gets:
            if d[0] == g:
                result[g] = d[1]
    result['Run'] = int(time.time()) - int(result['Uptime'])
    tmp = db.query('show master status')
    try:
        result['File'] = tmp[0][0]
        result['Position'] = tmp[0][1]
    except:
        result['File'] = 'OFF'
        result['Position'] = 'OFF'
    return public.getJson(result)


def myDbStatus():
    result = {}
    db = pMysqlDb()
    data = db.query('show variables')
    gets = ['table_open_cache', 'thread_cache_size', 'query_cache_type', 'key_buffer_size', 'query_cache_size', 'tmp_table_size', 'max_heap_table_size', 'innodb_buffer_pool_size',
            'innodb_additional_mem_pool_size', 'innodb_log_buffer_size', 'max_connections', 'sort_buffer_size', 'read_buffer_size', 'read_rnd_buffer_size', 'join_buffer_size', 'thread_stack', 'binlog_cache_size']
    result['mem'] = {}
    for d in data:
        for g in gets:
            if d[0] == g:
                result['mem'][g] = d[1]
    if result['mem']['query_cache_type'] != 'ON':
        result[
            'mem']['query_cache_size'] = '0'
    return public.getJson(result)


def setDbStatus():
    gets = ['key_buffer_size', 'query_cache_size', 'tmp_table_size', 'max_heap_table_size', 'innodb_buffer_pool_size', 'innodb_log_buffer_size', 'max_connections', 'query_cache_type',
            'table_open_cache', 'thread_cache_size', 'sort_buffer_size', 'read_buffer_size', 'read_rnd_buffer_size', 'join_buffer_size', 'thread_stack', 'binlog_cache_size']
    emptys = ['max_connections', 'query_cache_type',
              'thread_cache_size', 'table_open_cache']
    args = getArgs()
    conFile = getConf()
    content = public.readFile(conFile)
    n = 0
    for g in gets:
        s = 'M'
        if n > 5:
            s = 'K'
        if g in emptys:
            s = ''
        rep = '\s*' + g + '\s*=\s*\d+(M|K|k|m|G)?\n'
        c = g + ' = ' + args[g] + s + '\n'
        if content.find(g) != -1:
            content = re.sub(rep, '\n' + c, content, 1)
        else:
            content = content.replace('[mysqld]\n', '[mysqld]\n' + c)
        n += 1
    public.writeFile(conFile, content)
    return public.returnJson(True, '设置成功!')

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
    elif func == 'db_status':
        print myDbStatus()
    elif func == 'set_db_status':
        print setDbStatus()
    elif func == 'conf':
        print getConf()
    elif func == 'show_log':
        print getShowLogFile()
    elif func == 'my_port':
        print getMyPort()
    elif func == 'set_my_port':
        print setMyPort()
    else:
        print 'error'
