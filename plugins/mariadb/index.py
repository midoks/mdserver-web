# coding:utf-8

import sys
import io
import os
import time
import subprocess
import re
import json


# reload(sys)
# sys.setdefaultencoding('utf-8')

sys.path.append(os.getcwd() + "/class/core")
import mw


if mw.isAppleSystem():
    cmd = 'ls /usr/local/lib/ | grep python  | cut -d \\  -f 1 | awk \'END {print}\''
    info = mw.execShell(cmd)
    p = "/usr/local/lib/" + info[0].strip() + "/site-packages"
    sys.path.append(p)


app_debug = False
if mw.isAppleSystem():
    app_debug = True


def getPluginName():
    return 'mariadb'


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


def getConf():
    path = getServerDir() + '/etc/my.cnf'
    return path


def getDataDir():
    file = getConf()
    content = mw.readFile(file)
    rep = 'datadir\s*=\s*(.*)'
    tmp = re.search(rep, content)
    return tmp.groups()[0].strip()


def getPidFile():
    file = getConf()
    content = mw.readFile(file)
    rep = 'pid-file\s*=\s*(.*)'
    tmp = re.search(rep, content)
    return tmp.groups()[0].strip()


def getDbPort():
    file = getConf()
    content = mw.readFile(file)
    rep = 'port\s*=\s*(.*)'
    tmp = re.search(rep, content)
    return tmp.groups()[0].strip()


def getSocketFile():
    file = getConf()
    content = mw.readFile(file)
    rep = 'socket\s*=\s*(.*)'
    tmp = re.search(rep, content)
    return tmp.groups()[0].strip()


def getInitdTpl(version=''):
    path = getPluginDir() + '/init.d/mariadb' + version + '.tpl'
    if not os.path.exists(path):
        path = getPluginDir() + '/init.d/mariadb.tpl'
    return path


def contentReplace(content):
    service_path = mw.getServerDir()
    content = content.replace('{$ROOT_PATH}', mw.getRootDir())
    content = content.replace('{$SERVER_PATH}', service_path)
    content = content.replace('{$SERVER_APP_PATH}', service_path + '/mariadb')
    server_id = int(time.time())
    content = content.replace('{$SERVER_ID}', str(server_id))

    if mw.isAppleSystem():
        user = mw.execShell(
            "who | sed -n '2, 1p' |awk '{print $1}'")[0].strip()
        content = content.replace('user = mysql', 'user = ' + user)
    return content


def pSqliteDb(dbname='databases'):
    file = getServerDir() + '/mariadb.db'
    name = 'mysql'
    if not os.path.exists(file):
        conn = mw.M(dbname).dbPos(getServerDir(), name)
        csql = mw.readFile(getPluginDir() + '/conf/mariadb.sql')
        csql_list = csql.split(';')
        for index in range(len(csql_list)):
            conn.execute(csql_list[index], ())
    else:
        # 现有run
        # conn = mw.M(dbname).dbPos(getServerDir(), name)
        # csql = mw.readFile(getPluginDir() + '/conf/mysql.sql')
        # csql_list = csql.split(';')
        # for index in range(len(csql_list)):
        #     conn.execute(csql_list[index], ())
        conn = mw.M(dbname).dbPos(getServerDir(), name)
    return conn


def pMysqlDb(name=''):
    # pymysql
    db = mw.getMyORM()
    # MySQLdb |
    # db = mw.getMyORMDb()

    db.setDbConf(getConf())
    db.setPort(getDbPort())
    db.setSocket(getSocketFile())
    db.setDbName(name)

    pwd = pSqliteDb('config').where('id=?', (1,)).getField('mysql_root')
    db.setPwd(pwd)
    return db


def makeInitRsaKey(version=''):
    datadir = getServerDir() + "/data"

    mysql_pem = datadir + "/mysql.pem"
    if not os.path.exists(mysql_pem):
        rdata = mw.execShell(
            'cd ' + datadir + ' && openssl genrsa -out mysql.pem 1024')
        # print(data)
        rdata = mw.execShell(
            'cd ' + datadir + ' && openssl rsa -in mysql.pem -pubout -out mysql.pub')
        # print(rdata)

        if not mw.isAppleSystem():
            mw.execShell('cd ' + datadir + ' && chmod 400 mysql.pem')
            mw.execShell('cd ' + datadir + ' && chmod 444 mysql.pub')
            mw.execShell('cd ' + datadir + ' && chown mysql:mysql mysql.pem')
            mw.execShell('cd ' + datadir + ' && chown mysql:mysql mysql.pub')


def initDreplace(version=''):
    initd_tpl = getInitdTpl(version)

    mysql_conf_dir = getServerDir() + '/etc'
    if not os.path.exists(mysql_conf_dir):
        os.mkdir(mysql_conf_dir)

    mysql_conf = mysql_conf_dir + '/my.cnf'
    if not os.path.exists(mysql_conf):
        mysql_conf_tpl = getPluginDir() + '/conf/my.cnf'
        content = mw.readFile(mysql_conf_tpl)
        content = contentReplace(content)
        mw.writeFile(mysql_conf, content)

    initD_path = getServerDir() + '/init.d'
    if not os.path.exists(initD_path):
        os.mkdir(initD_path)

    file_bin = initD_path + '/' + getPluginName()
    if not os.path.exists(file_bin):
        content = mw.readFile(initd_tpl)
        content = contentReplace(content)
        mw.writeFile(file_bin, content)
        mw.execShell('chmod +x ' + file_bin)

    mysql_tmp = getServerDir() + '/tmp'
    if not os.path.exists(mysql_tmp):
        os.mkdir(mysql_tmp)
        mw.execShell("chown -R mysql:mysql " + mysql_tmp)

    # systemd
    systemDir = mw.systemdCfgDir()
    systemService = systemDir + '/mariadb.service'
    systemServiceTpl = getPluginDir() + '/init.d/mariadb.service.tpl'
    if os.path.exists(systemDir) and not os.path.exists(systemService):
        service_path = mw.getServerDir()
        se_content = mw.readFile(systemServiceTpl)
        se_content = se_content.replace('{$SERVER_PATH}', service_path)
        mw.writeFile(systemService, se_content)
        mw.execShell('systemctl daemon-reload')

    if mw.getOs() != 'darwin':
        mw.execShell('chown -R mysql mysql ' + getServerDir())
    return file_bin


def status(version=''):
    try:
        pid = getPidFile()
        if os.path.exists(pid):
            return 'start'
    except Exception as e:
        return 'stop'
    return 'stop'


def binLog():
    args = getArgs()
    conf = getConf()
    con = mw.readFile(conf)

    if con.find('#log-bin=mysql-bin') != -1:
        if 'status' in args:
            return mw.returnJson(False, '0')
        con = con.replace('#log-bin=mysql-bin', 'log-bin=mysql-bin')
        con = con.replace('#binlog_format=mixed', 'binlog_format=mixed')
        mw.execShell('sync')
        restart()
    else:
        path = getDataDir()
        if 'status' in args:
            dsize = 0
            for n in os.listdir(path):
                if len(n) < 9:
                    continue
                if n[0:9] == 'mysql-bin':
                    dsize += os.path.getsize(path + '/' + n)
            return mw.returnJson(True, dsize)
        con = con.replace('log-bin=mysql-bin', '#log-bin=mysql-bin')
        con = con.replace('binlog_format=mixed', '#binlog_format=mixed')
        mw.execShell('sync')
        restart()
        mw.execShell('rm -f ' + path + '/mysql-bin.*')

    mw.writeFile(conf, con)
    return mw.returnJson(True, '设置成功!')


def setSkipGrantTables(v):
    '''
    设置是否密码验证
    '''
    conf = getConf()
    con = mw.readFile(conf)
    if v:
        if con.find('#skip-grant-tables') != -1:
            con = con.replace('#skip-grant-tables', 'skip-grant-tables')
    else:
        con = con.replace('skip-grant-tables', '#skip-grant-tables')
    mw.writeFile(conf, con)
    return True


def getErrorLog():
    args = getArgs()
    path = getDataDir()
    filename = ''
    for n in os.listdir(path):
        if len(n) < 5:
            continue
        if n == 'error.log':
            filename = path + '/' + n
            break
    # print filename
    if not os.path.exists(filename):
        return mw.returnJson(False, '指定文件不存在!')
    if 'close' in args:
        mw.writeFile(filename, '')
        return mw.returnJson(False, '日志已清空')
    info = mw.getLastLine(filename, 18)
    return mw.returnJson(True, 'OK', info)


def getShowLogFile():
    file = getConf()
    content = mw.readFile(file)
    rep = 'slow-query-log-file\s*=\s*(.*)'
    tmp = re.search(rep, content)
    return tmp.groups()[0].strip()


def pGetDbUser():
    if mw.isAppleSystem():
        user = mw.execShell(
            "who | sed -n '2, 1p' |awk '{print $1}'")[0].strip()
        return user
    return 'mysql'


def initMysqlData():
    datadir = getDataDir()
    if not os.path.exists(datadir + '/mysql'):
        serverdir = getServerDir()
        myconf = serverdir + "/etc/my.cnf"
        user = pGetDbUser()
        cmd = 'cd ' + serverdir + ' && ./scripts/mariadb-install-db ' + \
            ' --defaults-file=' + myconf
        data = mw.execShell(cmd)
        # print(data[0])
        # print(data[1])
        return False
    return True


def initMariaDbPwd():
    time.sleep(5)

    serverdir = getServerDir()
    myconf = serverdir + "/etc/my.cnf"
    pwd = mw.getRandomString(16)

    db_option = "-S " + serverdir + "/mysql.sock"
    cmd_pass = serverdir + '/bin/mysql ' + db_option + ' -uroot -e'
    cmd_pass = cmd_pass + \
        "\"flush privileges;use mysql;grant all privileges on *.* to 'root'@'localhost' identified by '" + pwd + "';"
    cmd_pass = cmd_pass + "flush privileges;\""

    # print(cmd_pass)
    data = mw.execShell(cmd_pass)
    # print(data)
    if data[1].find("ERROR") != -1:
        print("init mariadb password fail:" + data[1])
        exit(1)

    # 删除测试数据库
    drop_test_db = serverdir + '/bin/mysql ' + db_option + ' -uroot -p' + \
        pwd + ' -e "drop database test";'
    mw.execShell(drop_test_db)

    # 删除冗余账户
    hostname = mw.execShell('hostname')[0].strip()
    drop_hostname =  serverdir + '/bin/mysql  --defaults-file=' + \
        myconf + ' -uroot -p' + pwd + ' -e "drop user \'\'@\'' + hostname + '\'";'
    mw.execShell(drop_hostname)

    drop_root_hostname =  serverdir + '/bin/mysql  --defaults-file=' + \
        myconf + ' -uroot -p' + pwd + ' -e "drop user \'root\'@\'' + hostname + '\'";'
    mw.execShell(drop_root_hostname)

    pSqliteDb('config').where('id=?', (1,)).save('mysql_root', (pwd,))
    return True


def myOp(version, method):
    # import commands
    init_file = initDreplace()
    cmd = init_file + ' ' + method
    try:
        isInited = initMysqlData()
        if not isInited:
            if mw.isAppleSystem():
                setSkipGrantTables(True)
                cmd_init_start = init_file + ' start'
                subprocess.Popen(cmd_init_start, stdout=subprocess.PIPE, shell=True,
                                 bufsize=4096, stderr=subprocess.PIPE)

                time.sleep(6)
            else:
                mw.execShell('systemctl start mariadb')

            initMariaDbPwd()

            if mw.isAppleSystem():
                setSkipGrantTables(False)
                cmd_init_stop = init_file + ' stop'
                subprocess.Popen(cmd_init_stop, stdout=subprocess.PIPE, shell=True,
                                 bufsize=4096, stderr=subprocess.PIPE)
                time.sleep(3)
            else:
                mw.execShell('systemctl stop mariadb')

        if mw.isAppleSystem():
            print
            sub = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True,
                                   bufsize=4096, stderr=subprocess.PIPE)
            sub.wait(5)
        else:
            mw.execShell('systemctl ' + method + ' mariadb')

        return 'ok'
    except Exception as e:
        return str(e)


def appCMD(version, action):
    makeInitRsaKey(version)
    return myOp(version, action)


def start(version=''):
    return appCMD(version, 'start')


def stop(version=''):
    return appCMD(version, 'stop')


def restart(version=''):
    return appCMD(version, 'restart')


def reload(version=''):
    return appCMD(version, 'reload')


def initdStatus():
    if mw.isAppleSystem():
        return "Apple Computer does not support"

    shell_cmd = 'systemctl status mariadb | grep loaded | grep "enabled;"'
    data = mw.execShell(shell_cmd)
    if data[0] == '':
        return 'fail'
    return 'ok'


def initdInstall():
    if mw.isAppleSystem():
        return "Apple Computer does not support"

    mw.execShell('systemctl enable mariadb')
    return 'ok'


def initdUinstall():
    if mw.isAppleSystem():
        return "Apple Computer does not support"

    mw.execShell('systemctl disable mariadb')
    return 'ok'


def getMyDbPos():
    file = getConf()
    content = mw.readFile(file)
    rep = 'datadir\s*=\s*(.*)'
    tmp = re.search(rep, content)
    return tmp.groups()[0].strip()


def setMyDbPos():
    args = getArgs()
    data = checkArgs(args, ['datadir'])
    if not data[0]:
        return data[1]

    s_datadir = getMyDbPos()
    t_datadir = args['datadir']
    if t_datadir == s_datadir:
        return mw.returnJson(False, '与当前存储目录相同，无法迁移文件!')

    if not os.path.exists(t_datadir):
        mw.execShell('mkdir -p ' + t_datadir)

    stop()
    mw.execShell('cp -rf ' + s_datadir + '/* ' + t_datadir + '/')
    mw.execShell('chown -R mysql mysql ' + t_datadir)
    mw.execShell('chmod -R 755 ' + t_datadir)
    mw.execShell('rm -f ' + t_datadir + '/*.pid')
    mw.execShell('rm -f ' + t_datadir + '/*.err')

    path = getServerDir()
    myfile = path + '/etc/my.cnf'
    mycnf = mw.readFile(myfile)
    mw.writeFile(path + '/etc/my_backup.cnf', mycnf)

    mycnf = mycnf.replace(s_datadir, t_datadir)
    mw.writeFile(myfile, mycnf)
    start()

    result = mw.execShell(
        'ps aux|grep mysqld| grep -v grep|grep -v python')
    if len(result[0]) > 10:
        mw.writeFile('data/datadir.pl', t_datadir)
        return mw.returnJson(True, '存储目录迁移成功!')
    else:
        mw.execShell('pkill -9 mysqld')
        mw.writeFile(myfile, mw.readFile(path + '/etc/my_backup.cnf'))
        start()
        return mw.returnJson(False, '文件迁移失败!')


def getMyPort():
    file = getConf()
    content = mw.readFile(file)
    rep = 'port\s*=\s*(.*)'
    tmp = re.search(rep, content)
    return tmp.groups()[0].strip()


def setMyPort():
    args = getArgs()
    data = checkArgs(args, ['port'])
    if not data[0]:
        return data[1]

    port = args['port']
    file = getConf()
    content = mw.readFile(file)
    rep = "port\s*=\s*([0-9]+)\s*\n"
    content = re.sub(rep, 'port = ' + port + '\n', content)
    mw.writeFile(file, content)
    restart()
    return mw.returnJson(True, '编辑成功!')


def runInfo():

    if status(version) == 'stop':
        return mw.returnJson(False, 'MySQL未启动', [])

    db = pMysqlDb()
    data = db.query('show global status')
    gets = ['Max_used_connections', 'Com_commit', 'Com_rollback', 'Questions', 'Innodb_buffer_pool_reads', 'Innodb_buffer_pool_read_requests', 'Key_reads', 'Key_read_requests', 'Key_writes',
            'Key_write_requests', 'Qcache_hits', 'Qcache_inserts', 'Bytes_received', 'Bytes_sent', 'Aborted_clients', 'Aborted_connects',
            'Created_tmp_disk_tables', 'Created_tmp_tables', 'Innodb_buffer_pool_pages_dirty', 'Opened_files', 'Open_tables', 'Opened_tables', 'Select_full_join',
            'Select_range_check', 'Sort_merge_passes', 'Table_locks_waited', 'Threads_cached', 'Threads_connected', 'Threads_created', 'Threads_running', 'Connections', 'Uptime']

    result = {}
    # print(data)
    for d in data:
        vname = d["Variable_name"]
        for g in gets:
            if vname == g:
                result[g] = d["Value"]

    # print(result, int(result['Uptime']))
    result['Run'] = int(time.time()) - int(result['Uptime'])
    tmp = db.query('show master status')
    try:
        result['File'] = tmp[0]["File"]
        result['Position'] = tmp[0]["Position"]
    except:
        result['File'] = 'OFF'
        result['Position'] = 'OFF'
    return mw.getJson(result)


def myDbStatus():
    result = {}
    db = pMysqlDb()
    data = db.query('show variables')
    isError = isSqlError(data)
    if isError != None:
        return isError

    gets = ['table_open_cache', 'thread_cache_size', 'key_buffer_size', 'tmp_table_size', 'max_heap_table_size', 'innodb_buffer_pool_size',
            'innodb_additional_mem_pool_size', 'innodb_log_buffer_size', 'max_connections', 'sort_buffer_size', 'read_buffer_size', 'read_rnd_buffer_size', 'join_buffer_size', 'thread_stack', 'binlog_cache_size']
    result['mem'] = {}
    for d in data:
        vname = d['Variable_name']
        for g in gets:
            # print(g)
            if vname == g:
                result['mem'][g] = d["Value"]
    return mw.getJson(result)


def setDbStatus():
    gets = ['key_buffer_size', 'tmp_table_size', 'max_heap_table_size', 'innodb_buffer_pool_size', 'innodb_log_buffer_size', 'max_connections',
            'table_open_cache', 'thread_cache_size', 'sort_buffer_size', 'read_buffer_size', 'read_rnd_buffer_size', 'join_buffer_size', 'thread_stack', 'binlog_cache_size']
    emptys = ['max_connections', 'thread_cache_size', 'table_open_cache']
    args = getArgs()
    conFile = getConf()
    content = mw.readFile(conFile)
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
    mw.writeFile(conFile, content)
    return mw.returnJson(True, '设置成功!')


def isSqlError(mysqlMsg):
    # 检测数据库执行错误
    mysqlMsg = str(mysqlMsg)
    if "MySQLdb" in mysqlMsg:
        return mw.returnJson(False, 'MySQLdb组件缺失! <br>进入SSH命令行输入: pip install mysql-python | pip install mysqlclient==2.0.3')
    if "2002," in mysqlMsg:
        return mw.returnJson(False, '数据库连接失败,请检查数据库服务是否启动!')
    if "2003," in mysqlMsg:
        return mw.returnJson(False, "Can't connect to MySQL server on '127.0.0.1' (61)")
    if "using password:" in mysqlMsg:
        return mw.returnJson(False, '数据库管理密码错误!')
    if "1045" in mysqlMsg:
        return mw.returnJson(False, '连接错误!')
    if "SQL syntax" in mysqlMsg:
        return mw.returnJson(False, 'SQL语法错误!')
    if "Connection refused" in mysqlMsg:
        return mw.returnJson(False, '数据库连接失败,请检查数据库服务是否启动!')
    if "1133" in mysqlMsg:
        return mw.returnJson(False, '数据库用户不存在!')
    if "1007" in mysqlMsg:
        return mw.returnJson(False, '数据库已经存在!')
    return None


def __createUser(dbname, username, password, address):
    pdb = pMysqlDb('mysql')

    if username == 'root':
        dbname = '*'

    pdb.execute(
        "CREATE USER `%s`@`localhost` IDENTIFIED BY '%s'" % (username, password))
    pdb.execute(
        "grant all privileges on %s.* to `%s`@`localhost`" % (dbname, username))
    for a in address.split(','):
        pdb.execute(
            "CREATE USER `%s`@`%s` IDENTIFIED BY '%s'" % (username, a, password))
        pdb.execute(
            "grant all privileges on %s.* to `%s`@`%s`" % (dbname, username, a))
    pdb.execute("flush privileges")


def getDbBackupListFunc(dbname=''):
    bkDir = mw.getRootDir() + '/backup/database'
    blist = os.listdir(bkDir)
    r = []

    bname = 'db_' + dbname
    blen = len(bname)
    for x in blist:
        fbstr = x[0:blen]
        if fbstr == bname:
            r.append(x)
    return r


def setDbBackup():
    args = getArgs()
    data = checkArgs(args, ['name'])
    if not data[0]:
        return data[1]

    scDir = getPluginDir() + '/scripts/backup.py'
    cmd = 'python3 ' + scDir + ' database ' + args['name'] + ' 3'
    os.system(cmd)
    return mw.returnJson(True, 'ok')


def importDbBackup():
    args = getArgs()
    data = checkArgs(args, ['file', 'name'])
    if not data[0]:
        return data[1]

    file = args['file']
    name = args['name']

    file_path = mw.getRootDir() + '/backup/database/' + file
    file_path_sql = mw.getRootDir() + '/backup/database/' + file.replace('.gz', '')

    if not os.path.exists(file_path_sql):
        cmd = 'cd ' + mw.getRootDir() + '/backup/database && gzip -d ' + file
        mw.execShell(cmd)

    pwd = pSqliteDb('config').where('id=?', (1,)).getField('mysql_root')
    sock = getSocketFile()
    mysql_cmd = getServerDir() + '/bin/mysql -S ' + sock + ' -uroot -p' + pwd + \
        ' ' + name + ' < ' + file_path_sql

    # print(mysql_cmd)
    os.system(mysql_cmd)
    return mw.returnJson(True, 'ok')


def deleteDbBackup():
    args = getArgs()
    data = checkArgs(args, ['filename'])
    if not data[0]:
        return data[1]

    bkDir = mw.getRootDir() + '/backup/database'

    os.remove(bkDir + '/' + args['filename'])
    return mw.returnJson(True, 'ok')


def getDbBackupList():
    args = getArgs()
    data = checkArgs(args, ['name'])
    if not data[0]:
        return data[1]

    r = getDbBackupListFunc(args['name'])
    bkDir = mw.getRootDir() + '/backup/database'
    rr = []
    for x in range(0, len(r)):
        p = bkDir + '/' + r[x]
        data = {}
        data['name'] = r[x]

        rsize = os.path.getsize(p)
        data['size'] = mw.toSize(rsize)

        t = os.path.getctime(p)
        t = time.localtime(t)

        data['time'] = time.strftime('%Y-%m-%d %H:%M:%S', t)
        rr.append(data)

        data['file'] = p

    return mw.returnJson(True, 'ok', rr)


def getDbList():
    args = getArgs()
    page = 1
    page_size = 10
    search = ''
    data = {}
    if 'page' in args:
        page = int(args['page'])

    if 'page_size' in args:
        page_size = int(args['page_size'])

    if 'search' in args:
        search = args['search']

    conn = pSqliteDb('databases')
    limit = str((page - 1) * page_size) + ',' + str(page_size)
    condition = ''
    if not search == '':
        condition = "name like '%" + search + "%'"
    field = 'id,pid,name,username,password,accept,rw,ps,addtime'
    clist = conn.where(condition, ()).field(
        field).limit(limit).order('id desc').select()

    for x in range(0, len(clist)):
        dbname = clist[x]['name']
        blist = getDbBackupListFunc(dbname)
        # print(blist)
        clist[x]['is_backup'] = False
        if len(blist) > 0:
            clist[x]['is_backup'] = True

    count = conn.where(condition, ()).count()
    _page = {}
    _page['count'] = count
    _page['p'] = page
    _page['row'] = page_size
    _page['tojs'] = 'dbList'
    data['page'] = mw.getPage(_page)
    data['data'] = clist

    info = {}
    info['root_pwd'] = pSqliteDb('config').where(
        'id=?', (1,)).getField('mysql_root')
    data['info'] = info

    return mw.getJson(data)


def syncGetDatabases():
    pdb = pMysqlDb()
    psdb = pSqliteDb('databases')
    data = pdb.query('show databases')
    isError = isSqlError(data)
    if isError != None:
        return isError
    users = pdb.query(
        "select User,Host from user where User!='root' AND Host!='localhost' AND Host!=''")
    nameArr = ['information_schema', 'performance_schema', 'mysql', 'sys']
    n = 0

    # print(users)
    for value in data:
        vdb_name = value["Database"]
        b = False
        for key in nameArr:
            if vdb_name == key:
                b = True
                break
        if b:
            continue
        if psdb.where("name=?", (vdb_name,)).count() > 0:
            continue
        host = '127.0.0.1'
        for user in users:
            if vdb_name == user["User"]:
                host = user["Host"]
                break

        ps = mw.getMsg('INPUT_PS')
        if vdb_name == 'test':
            ps = mw.getMsg('DATABASE_TEST')
        addTime = time.strftime('%Y-%m-%d %X', time.localtime())
        if psdb.add('name,username,password,accept,ps,addtime', (vdb_name, vdb_name, '', host, ps, addTime)):
            n += 1

    msg = mw.getInfo('本次共从服务器获取了{1}个数据库!', (str(n),))
    return mw.returnJson(True, msg)


def toDbBase(find):
    pdb = pMysqlDb()
    psdb = pSqliteDb('databases')
    if len(find['password']) < 3:
        find['username'] = find['name']
        find['password'] = mw.md5(str(time.time()) + find['name'])[0:10]
        psdb.where("id=?", (find['id'],)).save(
            'password,username', (find['password'], find['username']))

    result = pdb.execute("create database `" + find['name'] + "`")
    if "using password:" in str(result):
        return -1
    if "Connection refused" in str(result):
        return -1

    password = find['password']
    __createUser(find['name'], find['username'], password, find['accept'])
    return 1


def syncToDatabases():
    args = getArgs()
    data = checkArgs(args, ['type', 'ids'])
    if not data[0]:
        return data[1]

    pdb = pMysqlDb()
    result = pdb.execute("show databases")
    isError = isSqlError(result)
    if isError:
        return isError

    stype = int(args['type'])
    psdb = pSqliteDb('databases')
    n = 0

    if stype == 0:
        data = psdb.field('id,name,username,password,accept').select()
        for value in data:
            result = toDbBase(value)
            if result == 1:
                n += 1
    else:
        data = json.loads(args['ids'])
        for value in data:
            find = psdb.where("id=?", (value,)).field(
                'id,name,username,password,accept').find()
            # print find
            result = toDbBase(find)
            if result == 1:
                n += 1
    msg = mw.getInfo('本次共同步了{1}个数据库!', (str(n),))
    return mw.returnJson(True, msg)


def setRootPwd(version=''):
    args = getArgs()
    data = checkArgs(args, ['password'])
    if not data[0]:
        return data[1]

    password = args['password']
    try:
        pdb = pMysqlDb('mysql')
        result = pdb.query("show databases")
        isError = isSqlError(result)
        if isError != None:
            return isError

        cmd = "ALTER USER 'root'@'localhost' IDENTIFIED BY '" + password + "';"
        r = pdb.execute(cmd)
        # print(r)

        pSqliteDb('config').where('id=?', (1,)).save('mysql_root', (password,))
        orm = pMysqlDb()
        orm.execute("flush privileges")
        return mw.returnJson(True, '数据库root密码修改成功!')
    except Exception as ex:
        return mw.returnJson(False, '修改错误:' + str(ex))


def setUserPwd(version=''):
    args = getArgs()
    data = checkArgs(args, ['password', 'name', 'id'])
    if not data[0]:
        return data[1]

    newpassword = args['password']
    username = args['name']
    uid = args['id']
    try:
        pdb = pMysqlDb()
        psdb = pSqliteDb('databases')
        data = psdb.field('id,name,accept').where('id=?', (uid,)).find()

        cmd = "SET PASSWORD FOR '" + username + \
            "'@'localhost' = PASSWORD('" + newpassword + "')"
        r = pdb.execute(cmd)
        # print(cmd, r)

        accept = data['accept']
        alist = accept.split(',')
        for x in alist:
            cmd = "SET PASSWORD FOR '" + username + \
                "'@'" + x + "' = PASSWORD('" + newpassword + "')"
            r = pdb.execute(cmd)
            # print(cmd, r)

        psdb.where("id=?", (uid,)).setField('password', newpassword)

        orm = pMysqlDb()
        orm.execute("flush privileges")
        return mw.returnJson(True, mw.getInfo('修改数据库[{1}]密码成功!', (data['name'],)))
    except Exception as ex:
        return mw.returnJson(False, mw.getInfo('修改数据库[{1}]密码失败[{2}]!', (data['name'], str(ex),)))


def setDbPs():
    args = getArgs()
    data = checkArgs(args, ['id', 'name', 'ps'])
    if not data[0]:
        return data[1]

    ps = args['ps']
    sid = args['id']
    name = args['name']
    try:
        psdb = pSqliteDb('databases')
        psdb.where("id=?", (sid,)).setField('ps', ps)
        return mw.returnJson(True, mw.getInfo('修改数据库[{1}]备注成功!', (name,)))
    except Exception as e:
        return mw.returnJson(True, mw.getInfo('修改数据库[{1}]备注失败!', (name,)))


def addDb():
    args = getArgs()
    data = checkArgs(args,
                     ['password', 'name', 'codeing', 'db_user', 'dataAccess', 'ps'])
    if not data[0]:
        return data[1]

    if not 'address' in args:
        address = ''
    else:
        address = args['address'].strip()

    dbname = args['name'].strip()
    dbuser = args['db_user'].strip()
    codeing = args['codeing'].strip()
    password = args['password'].strip()
    dataAccess = args['dataAccess'].strip()
    ps = args['ps'].strip()

    reg = "^[\w\.-]+$"
    if not re.match(reg, args['name']):
        return mw.returnJson(False, '数据库名称不能带有特殊符号!')
    checks = ['root', 'mysql', 'test', 'sys', 'panel_logs']
    if dbuser in checks or len(dbuser) < 1:
        return mw.returnJson(False, '数据库用户名不合法!')
    if dbname in checks or len(dbname) < 1:
        return mw.returnJson(False, '数据库名称不合法!')

    if len(password) < 1:
        password = mw.md5(time.time())[0:8]

    wheres = {
        'utf8':   'utf8_general_ci',
        'utf8mb4': 'utf8mb4_general_ci',
        'gbk':    'gbk_chinese_ci',
        'big5':   'big5_chinese_ci'
    }
    codeStr = wheres[codeing]

    pdb = pMysqlDb()
    psdb = pSqliteDb('databases')

    if psdb.where("name=? or username=?", (dbname, dbuser)).count():
        return mw.returnJson(False, '数据库已存在!')

    result = pdb.execute("create database `" + dbname +
                         "` DEFAULT CHARACTER SET " + codeing + " COLLATE " + codeStr)
    # print result
    isError = isSqlError(result)
    if isError != None:
        return isError

    pdb.execute("drop user '" + dbuser + "'@'localhost'")
    for a in address.split(','):
        pdb.execute("drop user '" + dbuser + "'@'" + a + "'")

    __createUser(dbname, dbuser, password, address)

    addTime = time.strftime('%Y-%m-%d %X', time.localtime())
    psdb.add('pid,name,username,password,accept,ps,addtime',
             (0, dbname, dbuser, password, address, ps, addTime))
    return mw.returnJson(True, '添加成功!')


def delDb():
    args = getArgs()
    data = checkArgs(args, ['id', 'name'])
    if not data[0]:
        return data[1]
    try:
        id = args['id']
        name = args['name']
        psdb = pSqliteDb('databases')
        pdb = pMysqlDb('mysql')
        find = psdb.where("id=?", (id,)).field(
            'id,pid,name,username,password,accept,ps,addtime').find()
        accept = find['accept']
        username = find['username']

        # 删除MYSQL
        result = pdb.execute("drop database `" + name + "`")

        users = pdb.query("select Host from user where User='" +
                          username + "' AND Host!='localhost'")
        pdb.execute("drop user '" + username + "'@'localhost'")
        for us in users:
            pdb.execute("drop user '" + username + "'@'" + us["Host"] + "'")
        pdb.execute("flush privileges")

        # 删除SQLITE
        psdb.where("id=?", (id,)).delete()
        return mw.returnJson(True, '删除成功!')
    except Exception as ex:
        return mw.returnJson(False, '删除失败!' + str(ex))


def getDbAccess():
    args = getArgs()
    data = checkArgs(args, ['username'])
    if not data[0]:
        return data[1]
    username = args['username']
    pdb = pMysqlDb('mysql')

    users = pdb.query("select Host from user where User='" +
                      username + "' AND Host!='localhost'")

    if len(users) < 1:
        return mw.returnJson(True, "127.0.0.1")
    accs = []
    for c in users:
        accs.append(c["Host"])
    userStr = ','.join(accs)
    return mw.returnJson(True, userStr)


def setDbAccess():
    args = getArgs()
    data = checkArgs(args, ['username', 'access'])
    if not data[0]:
        return data[1]
    name = args['username']
    access = args['access']
    pdb = pMysqlDb('mysql')
    psdb = pSqliteDb('databases')

    dbname = psdb.where('username=?', (name,)).getField('name')

    if name == 'root':
        password = pSqliteDb('config').where(
            'id=?', (1,)).getField('mysql_root')
    else:
        password = psdb.where("username=?", (name,)).getField('password')

    users = pdb.query("select Host from user where User='" +
                      name + "' AND Host!='localhost'")

    for us in users:
        pdb.execute("drop user '" + name + "'@'" + us["Host"] + "'")

    __createUser(dbname, name, password, access)

    psdb.where('username=?', (name,)).save('accept,rw', (access, 'rw',))
    return mw.returnJson(True, '设置成功!')


def setDbRw(version=''):
    args = getArgs()
    data = checkArgs(args, ['username', 'id', 'rw'])
    if not data[0]:
        return data[1]

    username = args['username']
    uid = args['id']
    rw = args['rw']

    pdb = pMysqlDb('mysql')
    psdb = pSqliteDb('databases')
    dbname = psdb.where("id=?", (uid,)).getField('name')
    users = pdb.query(
        "select Host from user where User='" + username + "'")

    # show grants for demo@"127.0.0.1";
    for x in users:
        # REVOKE ALL PRIVILEGES ON `imail`.* FROM 'imail'@'127.0.0.1';

        sql = "REVOKE ALL PRIVILEGES ON `" + dbname + \
            "`.* FROM '" + username + "'@'" + x["Host"] + "';"
        r = pdb.query(sql)
        # print(sql, r)

        if rw == 'rw':
            sql = "GRANT SELECT, INSERT, UPDATE, DELETE ON " + dbname + ".* TO " + \
                username + "@'" + x["Host"] + "'"
        elif rw == 'r':
            sql = "GRANT SELECT ON " + dbname + ".* TO " + \
                username + "@'" + x["Host"] + "'"
        else:
            sql = "GRANT all privileges ON " + dbname + ".* TO " + \
                username + "@'" + x["Host"] + "'"
        pdb.execute(sql)
    pdb.execute("flush privileges")
    r = psdb.where("id=?", (uid,)).setField('rw', rw)
    # print(r)
    return mw.returnJson(True, '切换成功!')


def getDbInfo():
    args = getArgs()
    data = checkArgs(args, ['name'])
    if not data[0]:
        return data[1]

    db_name = args['name']
    pdb = pMysqlDb()
    # print 'show tables from `%s`' % db_name
    tables = pdb.query('show tables from `%s`' % db_name)

    ret = {}
    sql = "select sum(DATA_LENGTH)+sum(INDEX_LENGTH) as sum_size from information_schema.tables  where table_schema='%s'" % db_name
    data_sum = pdb.query(sql)

    data = 0
    if data_sum[0]['sum_size'] != None:
        data = data_sum[0]['sum_size']

    ret['data_size'] = mw.toSize(data)
    ret['database'] = db_name

    ret3 = []
    table_key = "Tables_in_" + db_name
    for i in tables:
        tb_sql = "show table status from `%s` where name = '%s'" % (db_name, i[
                                                                    table_key])
        table = pdb.query(tb_sql)

        tmp = {}
        tmp['type'] = table[0]["Engine"]
        tmp['rows_count'] = table[0]["Rows"]
        tmp['collation'] = table[0]["Collation"]

        data_size = 0
        if table[0]['Avg_row_length'] != None:
            data_size = table[0]['Avg_row_length']

        if table[0]['Data_length'] != None:
            data_size = table[0]['Data_length']

        tmp['data_byte'] = data_size
        tmp['data_size'] = mw.toSize(data_size)
        tmp['table_name'] = table[0]["Name"]
        ret3.append(tmp)

    ret['tables'] = (ret3)

    return mw.getJson(ret)


def repairTable():
    args = getArgs()
    data = checkArgs(args, ['db_name', 'tables'])
    if not data[0]:
        return data[1]

    db_name = args['db_name']
    tables = json.loads(args['tables'])
    pdb = pMysqlDb()
    mtable = pdb.query('show tables from `%s`' % db_name)

    ret = []
    key = "Tables_in_" + db_name
    for i in mtable:
        for tn in tables:
            if tn == i[key]:
                ret.append(tn)

    if len(ret) > 0:
        for i in ret:
            pdb.execute('REPAIR TABLE `%s`.`%s`' % (db_name, i))
        return mw.returnJson(True, "修复完成!")
    return mw.returnJson(False, "修复失败!")


def optTable():
    args = getArgs()
    data = checkArgs(args, ['db_name', 'tables'])
    if not data[0]:
        return data[1]

    db_name = args['db_name']
    tables = json.loads(args['tables'])
    pdb = pMysqlDb()
    mtable = pdb.query('show tables from `%s`' % db_name)
    ret = []
    key = "Tables_in_" + db_name
    for i in mtable:
        for tn in tables:
            if tn == i[key]:
                ret.append(tn)

    if len(ret) > 0:
        for i in ret:
            pdb.execute('OPTIMIZE TABLE `%s`.`%s`' % (db_name, i))
        return mw.returnJson(True, "优化成功!")
    return mw.returnJson(False, "优化失败或者已经优化过了!")


def alterTable():
    args = getArgs()
    data = checkArgs(args, ['db_name', 'tables'])
    if not data[0]:
        return data[1]

    db_name = args['db_name']
    tables = json.loads(args['tables'])
    table_type = args['table_type']
    pdb = pMysqlDb()
    mtable = pdb.query('show tables from `%s`' % db_name)

    ret = []
    key = "Tables_in_" + db_name
    for i in mtable:
        for tn in tables:
            if tn == i[key]:
                ret.append(tn)

    if len(ret) > 0:
        for i in ret:
            pdb.execute('alter table `%s`.`%s` ENGINE=`%s`' %
                        (db_name, i, table_type))
        return mw.returnJson(True, "更改成功!")
    return mw.returnJson(False, "更改失败!")


def getTotalStatistics():
    st = status()
    data = {}

    isInstall = os.path.exists(getServerDir() + '/version.pl')

    if st == 'start' and isInstall:
        data['status'] = True
        data['count'] = pSqliteDb('databases').count()
        data['ver'] = mw.readFile(getServerDir() + '/version.pl').strip()
        return mw.returnJson(True, 'ok', data)
    else:
        data['status'] = False
        data['count'] = 0
        return mw.returnJson(False, 'fail', data)


def recognizeDbMode():
    conf = getConf()
    con = mw.readFile(conf)
    rep = r"!include %s/(.*)?\.cnf" % (getServerDir() + "/etc/mode",)
    mode = 'none'
    try:
        data = re.findall(rep, con, re.M)
        mode = data[0]
    except Exception as e:
        pass
    return mode


def getDbrunMode(version=''):
    mode = recognizeDbMode()
    return mw.returnJson(True, "ok", {'mode': mode})


def setDbrunMode(version=''):
    if version == '5.5':
        return mw.returnJson(False, "不支持切换")

    args = getArgs()
    data = checkArgs(args, ['mode', 'reload'])
    if not data[0]:
        return data[1]

    mode = args['mode']
    dbreload = args['reload']

    if not mode in ['classic', 'gtid']:
        return mw.returnJson(False, "mode的值无效:" + mode)

    origin_mode = recognizeDbMode()
    path = getConf()
    con = mw.readFile(path)
    rep = r"!include %s/%s\.cnf" % (getServerDir() + "/etc/mode", origin_mode)
    rep_after = "!include %s/%s.cnf" % (getServerDir() + "/etc/mode", mode)
    con = re.sub(rep, rep_after, con)
    mw.writeFile(path, con)

    if version == '5.6':
        dbreload = 'yes'
    else:
        db = pMysqlDb()
        # The value of @@GLOBAL.GTID_MODE can only be changed one step at a
        # time: OFF <-> OFF_PERMISSIVE <-> ON_PERMISSIVE <-> ON. Also note that
        # this value must be stepped up or down simultaneously on all servers.
        # See the Manual for instructions.
        if mode == 'classic':
            db.query('set global enforce_gtid_consistency=off')
            db.query('set global gtid_mode=on')
            db.query('set global gtid_mode=on_permissive')
            db.query('set global gtid_mode=off_permissive')
            db.query('set global gtid_mode=off')
        elif mode == 'gtid':
            db.query('set global enforce_gtid_consistency=on')
            db.query('set global gtid_mode=off')
            db.query('set global gtid_mode=off_permissive')
            db.query('set global gtid_mode=on_permissive')
            db.query('set global gtid_mode=on')

    if dbreload == "yes":
        restart(version)

    return mw.returnJson(True, "切换成功!")


def findBinlogDoDb():
    conf = getConf()
    con = mw.readFile(conf)
    rep = r"binlog-do-db\s*?=\s*?(.*)"
    dodb = re.findall(rep, con, re.M)
    return dodb


def findBinlogSlaveDoDb():
    conf = getConf()
    con = mw.readFile(conf)
    rep = r"replicate-do-db\s*?=\s*?(.*)"
    dodb = re.findall(rep, con, re.M)
    return dodb


def setDbMasterAccess():
    args = getArgs()
    data = checkArgs(args, ['username', 'access'])
    if not data[0]:
        return data[1]
    username = args['username']
    access = args['access']
    pdb = pMysqlDb()
    psdb = pSqliteDb('master_replication_user')
    password = psdb.where("username=?", (username,)).getField('password')
    users = pdb.query("select Host from user where User='" +
                      username + "' AND Host!='localhost'")
    for us in users:
        pdb.execute("drop user '" + username + "'@'" + us["Host"] + "'")

    dbname = '*'
    for a in access.split(','):
        pdb.execute(
            "CREATE USER `%s`@`%s` IDENTIFIED BY '%s'" % (username, a, password))
        pdb.execute(
            "grant all privileges on %s.* to `%s`@`%s`" % (dbname, username, a))

    pdb.execute("flush privileges")
    psdb.where('username=?', (username,)).save('accept', (access,))
    return mw.returnJson(True, '设置成功!')


def getMasterDbList(version=''):
    args = getArgs()
    page = 1
    page_size = 10
    search = ''
    data = {}
    if 'page' in args:
        page = int(args['page'])

    if 'page_size' in args:
        page_size = int(args['page_size'])

    if 'search' in args:
        search = args['search']

    conn = pSqliteDb('databases')
    limit = str((page - 1) * page_size) + ',' + str(page_size)
    condition = ''
    dodb = findBinlogDoDb()
    data['dodb'] = dodb

    slave_dodb = findBinlogSlaveDoDb()

    if not search == '':
        condition = "name like '%" + search + "%'"
    field = 'id,pid,name,username,password,accept,ps,addtime'
    clist = conn.where(condition, ()).field(
        field).limit(limit).order('id desc').select()
    count = conn.where(condition, ()).count()

    for x in range(0, len(clist)):
        if clist[x]['name'] in dodb:
            clist[x]['master'] = 1
        else:
            clist[x]['master'] = 0

        if clist[x]['name'] in slave_dodb:
            clist[x]['slave'] = 1
        else:
            clist[x]['slave'] = 0

    _page = {}
    _page['count'] = count
    _page['p'] = page
    _page['row'] = page_size
    _page['tojs'] = 'dbList'
    data['page'] = mw.getPage(_page)
    data['data'] = clist

    return mw.getJson(data)


def setDbMaster(version):
    args = getArgs()
    data = checkArgs(args, ['name'])
    if not data[0]:
        return data[1]

    conf = getConf()
    con = mw.readFile(conf)
    rep = r"(binlog-do-db\s*?=\s*?(.*))"
    dodb = re.findall(rep, con, re.M)

    isHas = False
    for x in range(0, len(dodb)):

        if dodb[x][1] == args['name']:
            isHas = True

            con = con.replace(dodb[x][0] + "\n", '')
            mw.writeFile(conf, con)

    if not isHas:
        prefix = '#binlog-do-db'
        con = con.replace(
            prefix, prefix + "\nbinlog-do-db=" + args['name'])
        mw.writeFile(conf, con)

    restart(version)
    time.sleep(4)
    return mw.returnJson(True, '设置成功', [args, dodb])


def setDbSlave(version):
    args = getArgs()
    data = checkArgs(args, ['name'])
    if not data[0]:
        return data[1]

    conf = getConf()
    con = mw.readFile(conf)
    rep = r"(replicate-do-db\s*?=\s*?(.*))"
    dodb = re.findall(rep, con, re.M)

    isHas = False
    for x in range(0, len(dodb)):
        if dodb[x][1] == args['name']:
            isHas = True

            con = con.replace(dodb[x][0] + "\n", '')
            mw.writeFile(conf, con)

    if not isHas:
        prefix = '#replicate-do-db'
        con = con.replace(
            prefix, prefix + "\nreplicate-do-db=" + args['name'])
        mw.writeFile(conf, con)

    restart(version)
    time.sleep(4)
    return mw.returnJson(True, '设置成功', [args, dodb])


def getMasterStatus(version=''):

    if status(version) == 'stop':
        return mw.returnJson(False, 'MySQL未启动,或正在启动中...!', [])

    conf = getConf()
    content = mw.readFile(conf)
    master_status = False
    if content.find('#log-bin') == -1 and content.find('log-bin') > 1:
        dodb = findBinlogDoDb()
        if len(dodb) > 0:
            master_status = True

    data = {}
    data['mode'] = recognizeDbMode()
    data['status'] = master_status

    db = pMysqlDb()
    dlist = db.query('show slave status')

    # print(dlist[0])
    if len(dlist) > 0 and (dlist[0]["Slave_IO_Running"] == 'Yes' or dlist[0]["Slave_SQL_Running"] == 'Yes'):
        data['slave_status'] = True

    return mw.returnJson(master_status, '设置成功', data)


def setMasterStatus(version=''):

    conf = getConf()
    con = mw.readFile(conf)

    if con.find('#log-bin') != -1:
        return mw.returnJson(False, '必须开启二进制日志')

    sign = 'mdserver_ms_open'

    dodb = findBinlogDoDb()
    if not sign in dodb:
        prefix = '#binlog-do-db'
        con = con.replace(prefix, prefix + "\nbinlog-do-db=" + sign)
        mw.writeFile(conf, con)
    else:
        con = con.replace("binlog-do-db=" + sign + "\n", '')
        rep = r"(binlog-do-db\s*?=\s*?(.*))"
        dodb = re.findall(rep, con, re.M)
        for x in range(0, len(dodb)):
            con = con.replace(dodb[x][0] + "\n", '')
        mw.writeFile(conf, con)

    restart(version)
    return mw.returnJson(True, '设置成功')


def getMasterRepSlaveList(version=''):
    args = getArgs()
    page = 1
    page_size = 10
    search = ''
    data = {}
    if 'page' in args:
        page = int(args['page'])

    if 'page_size' in args:
        page_size = int(args['page_size'])

    if 'search' in args:
        search = args['search']

    conn = pSqliteDb('master_replication_user')
    limit = str((page - 1) * page_size) + ',' + str(page_size)
    condition = ''

    if not search == '':
        condition = "name like '%" + search + "%'"
    field = 'id,username,password,accept,ps,addtime'
    clist = conn.where(condition, ()).field(
        field).limit(limit).order('id desc').select()
    count = conn.where(condition, ()).count()

    _page = {}
    _page['count'] = count
    _page['p'] = page
    _page['row'] = page_size
    _page['tojs'] = 'getMasterRepSlaveList'
    data['page'] = mw.getPage(_page)
    data['data'] = clist

    return mw.getJson(data)


def addMasterRepSlaveUser(version=''):
    args = getArgs()
    data = checkArgs(args, ['username', 'password'])
    if not data[0]:
        return data[1]

    if not 'address' in args:
        address = ''
    else:
        address = args['address'].strip()

    username = args['username'].strip()
    password = args['password'].strip()
    # ps = args['ps'].strip()
    # address = args['address'].strip()
    # dataAccess = args['dataAccess'].strip()

    reg = "^[\w\.-]+$"
    if not re.match(reg, username):
        return mw.returnJson(False, '用户名不能带有特殊符号!')
    checks = ['root', 'mysql', 'test', 'sys', 'panel_logs']
    if username in checks or len(username) < 1:
        return mw.returnJson(False, '用户名不合法!')
    if password in checks or len(password) < 1:
        return mw.returnJson(False, '密码不合法!')

    if len(password) < 1:
        password = mw.md5(time.time())[0:8]

    pdb = pMysqlDb()
    psdb = pSqliteDb('master_replication_user')

    if psdb.where("username=?", (username)).count() > 0:
        return mw.returnJson(False, '用户已存在!')

    sql = "GRANT REPLICATION SLAVE ON *.* TO  '" + username + \
        "'@'%' identified by '" + password + "';"
    result = pdb.execute(sql)
    result = pdb.execute('FLUSH PRIVILEGES;')
    isError = isSqlError(result)
    if isError != None:
        return isError

    addTime = time.strftime('%Y-%m-%d %X', time.localtime())
    psdb.add('username,password,accept,ps,addtime',
             (username, password, '%', '', addTime))
    return mw.returnJson(True, '添加成功!')


def getMasterRepSlaveUserCmd(version):

    args = getArgs()
    data = checkArgs(args, ['username', 'db'])
    if not data[0]:
        return data[1]

    psdb = pSqliteDb('master_replication_user')
    f = 'username,password'
    username = args['username']
    if username == '':
        count = psdb.count()
        if count == 0:
            return mw.returnJson(False, '请添加同步账户!')

        clist = psdb.field(f).limit('1').order('id desc').select()
    else:
        clist = psdb.field(f).where("username=?", (username,)).limit(
            '1').order('id desc').select()

    ip = mw.getLocalIp()
    port = getMyPort()
    db = pMysqlDb()

    mstatus = db.query('show master status')
    if len(mstatus) == 0:
        return mw.returnJson(False, '未开启!')

    mode = recognizeDbMode()

    if mode == "gtid":
        sql = "CHANGE MASTER TO MASTER_HOST='" + ip + "', MASTER_PORT=" + port + ", MASTER_USER='" + \
            clist[0]['username'] + "', MASTER_PASSWORD='" + \
            clist[0]['password'] + "', MASTER_AUTO_POSITION=1"
    else:
        sql = "CHANGE MASTER TO MASTER_HOST='" + ip + "', MASTER_PORT=" + port + ", MASTER_USER='" + \
            clist[0]['username']  + "', MASTER_PASSWORD='" + \
            clist[0]['password'] + \
            "', MASTER_LOG_FILE='" + mstatus[0]["File"] + \
            "',MASTER_LOG_POS=" + str(mstatus[0]["Position"])

    data = {}
    data['cmd'] = sql
    data["info"] = clist[0]
    data['mode'] = mode

    return mw.returnJson(True, 'ok!', data)


def delMasterRepSlaveUser(version=''):
    args = getArgs()
    data = checkArgs(args, ['username'])
    if not data[0]:
        return data[1]

    name = args['username']

    pdb = pMysqlDb()
    psdb = pSqliteDb('master_replication_user')
    pdb.execute("drop user '" + name + "'@'%'")
    pdb.execute("drop user '" + name + "'@'localhost'")

    users = pdb.query("select Host from user where User='" +
                      name + "' AND Host!='localhost'")
    for us in users:
        pdb.execute("drop user '" + name + "'@'" + us["Host"] + "'")

    psdb.where("username=?", (args['username'],)).delete()

    return mw.returnJson(True, '删除成功!')


def updateMasterRepSlaveUser(version=''):
    args = getArgs()
    data = checkArgs(args, ['username', 'password'])
    if not data[0]:
        return data[1]

    pdb = pMysqlDb()
    psdb = pSqliteDb('master_replication_user')
    pdb.execute("drop user '" + args['username'] + "'@'%'")

    pdb.execute("GRANT REPLICATION SLAVE ON *.* TO  '" +
                args['username'] + "'@'%' identified by '" + args['password'] + "'")

    psdb.where("username=?", (args['username'],)).save(
        'password', args['password'])

    return mw.returnJson(True, '更新成功!')


def getSlaveSSHList(version=''):
    args = getArgs()
    data = checkArgs(args, ['page', 'page_size'])
    if not data[0]:
        return data[1]

    page = int(args['page'])
    page_size = int(args['page_size'])

    conn = pSqliteDb('slave_id_rsa')
    limit = str((page - 1) * page_size) + ',' + str(page_size)

    field = 'id,ip,port,db_user,id_rsa,ps,addtime'
    clist = conn.field(field).limit(limit).order('id desc').select()
    count = conn.count()

    data = {}
    _page = {}
    _page['count'] = count
    _page['p'] = page
    _page['row'] = page_size
    _page['tojs'] = args['tojs']
    data['page'] = mw.getPage(_page)
    data['data'] = clist

    return mw.getJson(data)


def getSlaveSSHByIp(version=''):
    args = getArgs()
    data = checkArgs(args, ['ip'])
    if not data[0]:
        return data[1]

    ip = args['ip']

    conn = pSqliteDb('slave_id_rsa')
    data = conn.field('ip,port,db_user,id_rsa').where("ip=?", (ip,)).select()
    return mw.returnJson(True, 'ok', data)


def addSlaveSSH(version=''):
    import base64

    args = getArgs()
    data = checkArgs(args, ['ip'])
    if not data[0]:
        return data[1]

    ip = args['ip']
    if ip == "":
        return mw.returnJson(True, 'ok')

    data = checkArgs(args, ['port', 'id_rsa', 'db_user'])
    if not data[0]:
        return data[1]

    id_rsa = args['id_rsa']
    port = args['port']
    db_user = args['db_user']
    user = 'root'
    addTime = time.strftime('%Y-%m-%d %X', time.localtime())

    conn = pSqliteDb('slave_id_rsa')
    data = conn.field('ip,id_rsa').where("ip=?", (ip,)).select()
    if len(data) > 0:
        res = conn.where("ip=?", (ip,)).save(
            'port,id_rsa,db_user', (port, id_rsa, db_user))
    else:
        conn.add('ip,port,user,id_rsa,db_user,ps,addtime',
                 (ip, port, user, id_rsa, db_user, '', addTime))

    return mw.returnJson(True, '设置成功!')


def delSlaveSSH(version=''):
    args = getArgs()
    data = checkArgs(args, ['ip'])
    if not data[0]:
        return data[1]

    ip = args['ip']

    conn = pSqliteDb('slave_id_rsa')
    conn.where("ip=?", (ip,)).delete()
    return mw.returnJson(True, 'ok')


def updateSlaveSSH(version=''):
    args = getArgs()
    data = checkArgs(args, ['ip', 'id_rsa'])
    if not data[0]:
        return data[1]

    ip = args['ip']
    id_rsa = args['id_rsa']
    conn = pSqliteDb('slave_id_rsa')
    conn.where("ip=?", (ip,)).save('id_rsa', (id_rsa,))
    return mw.returnJson(True, 'ok')


def getSlaveList(version=''):

    db = pMysqlDb()
    dlist = db.query('show slave status')

    # print(dlist)
    ret = []
    for x in range(0, len(dlist)):
        tmp = {}
        tmp['Master_User'] = dlist[x]["Master_User"]
        tmp['Master_Host'] = dlist[x]["Master_Host"]
        tmp['Master_Port'] = dlist[x]["Master_Port"]
        tmp['Master_Log_File'] = dlist[x]["Master_Log_File"]
        tmp['Slave_IO_Running'] = dlist[x]["Slave_IO_Running"]
        tmp['Slave_SQL_Running'] = dlist[x]["Slave_SQL_Running"]
        ret.append(tmp)
    data = {}
    data['data'] = ret

    return mw.getJson(data)


def getSlaveSyncCmd(version=''):

    root = mw.getRunDir()
    cmd = 'cd ' + root + ' && python3 ' + root + \
        '/plugins/mysql/index.py do_full_sync {"db":"all"}'
    return mw.returnJson(True, 'ok', cmd)


def initSlaveStatus(version=''):
    db = pMysqlDb()
    dlist = db.query('show slave status')
    if len(dlist) > 0:
        return mw.returnJson(False, '已经初始化好了zz...')

    conn = pSqliteDb('slave_id_rsa')
    data = conn.field('ip,port,id_rsa,db_user').find()

    if len(data) < 1:
        return mw.returnJson(False, '需要先配置【[主]SSH配置】!')

    SSH_PRIVATE_KEY = "/tmp/t_ssh.txt"
    ip = data['ip']
    master_port = data['port']
    mw.writeFile(SSH_PRIVATE_KEY, data['id_rsa'].replace('\\n', '\n'))

    import paramiko
    paramiko.util.log_to_file('paramiko.log')
    ssh = paramiko.SSHClient()

    try:

        mw.execShell("chmod 600 " + SSH_PRIVATE_KEY)
        key = paramiko.RSAKey.from_private_key_file(SSH_PRIVATE_KEY)
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=ip, port=int(master_port),
                    username='root', pkey=key)

        db_user = data['db_user']
        cmd = 'cd /www/server/mdserver-web && python3 plugins/mariadb/index.py get_master_rep_slave_user_cmd {"username":"' + db_user + '","db":""}'
        stdin, stdout, stderr = ssh.exec_command(cmd)
        result = stdout.read()
        result = result.decode('utf-8')
        cmd_data = json.loads(result)
        time.sleep(1)
        ssh.close()
        if not cmd_data['status']:
            return mw.returnJson(False, '[主]:' + cmd_data['msg'])

        local_mode = recognizeDbMode()
        if local_mode != cmd_data['data']['mode']:
            return mw.returnJson(False, '主【{}】从【{}】,运行模式不一致!'.format(cmd_data['data']['mode'], local_mode))

        u = cmd_data['data']['info']
        ps = u['username'] + "|" + u['password']
        conn.where('ip=?', (ip,)).setField('ps', ps)
        db.query('stop slave')

        # 保证同步IP一致
        cmd = cmd_data['data']['cmd']
        if cmd.find('SOURCE_HOST') > -1:
            cmd = re.sub(r"SOURCE_HOST='(.*?)'",
                         "SOURCE_HOST='" + ip + "'", cmd, 1)

        if cmd.find('MASTER_HOST') > -1:
            cmd = re.sub(r"MASTER_HOST='(.*?)'",
                         "MASTER_HOST='" + ip + "'", cmd, 1)

        # print(cmd)
        db.query(cmd)
        db.query("start slave")

    except Exception as e:
        return mw.returnJson(False, 'SSH认证配置连接失败!' + str(e))

    os.system("rm -rf " + SSH_PRIVATE_KEY)
    return mw.returnJson(True, '初始化成功!')


def setSlaveStatus(version=''):

    db = pMysqlDb()
    dlist = db.query('show slave status')
    if len(dlist) == 0:
        return mw.returnJson(False, '需要手动添加主服务命令或者执行[初始化]!')

    # print(dlist)
    if len(dlist) > 0 and (dlist[0]["Slave_IO_Running"] == 'Yes' or dlist[0]["Slave_SQL_Running"] == 'Yes'):
        db.query('stop slave')
    else:
        ip = dlist[0]['Master_Host']
        conn = pSqliteDb('slave_id_rsa')
        data = conn.field('ip,ps').where("ip=?", (ip,)).find()
        if len(data) == 0:
            return mw.returnJson(False, '没有数据无法重启!')
        db.query("start slave")

    return mw.returnJson(True, '设置成功!')


def deleteSlave(version=''):
    db = pMysqlDb()
    dlist = db.query('stop slave')
    dlist = db.query('reset slave all')
    return mw.returnJson(True, '删除成功!')


def dumpMysqlData(version=''):
    args = getArgs()
    data = checkArgs(args, ['db'])
    if not data[0]:
        return data[1]

    pwd = pSqliteDb('config').where('id=?', (1,)).getField('mysql_root')
    mysql_dir = getServerDir()
    myconf = mysql_dir + "/etc/my.cnf"

    option = ''
    mode = recognizeDbMode()
    if mode == 'gtid':
        option = ' --set-gtid-purged=off '

    if args['db'].lower() == 'all':
        dlist = findBinlogDoDb()
        cmd = mysql_dir + "/bin/mysqldump --defaults-file=" + myconf + " " + option + " -uroot -p" + \
            pwd + " --databases " + \
            ' '.join(dlist) + " | gzip > /tmp/dump.sql.gz"
    else:
        cmd = mysql_dir + "/bin/mysqldump --defaults-file=" + myconf + " " + option + " -uroot -p" + \
            pwd + " --databases " + args['db'] + " | gzip > /tmp/dump.sql.gz"

    ret = mw.execShell(cmd)
    if ret[0] == '':
        return 'ok'
    return 'fail'


############### --- 重要 同步---- ###########

def writeDbSyncStatus(data):
    path = '/tmp/db_async_status.txt'
    # status_data['code'] = 1
    # status_data['msg'] = '主服务器备份完成...'
    # status_data['progress'] = 30
    mw.writeFile(path, json.dumps(data))


def doFullSync(version=''):

    args = getArgs()
    data = checkArgs(args, ['db'])
    if not data[0]:
        return data[1]

    db = pMysqlDb()

    id_rsa_conn = pSqliteDb('slave_id_rsa')
    data = id_rsa_conn.field('ip,port,db_user,id_rsa').find()

    SSH_PRIVATE_KEY = "/tmp/mysql_sync_id_rsa.txt"
    id_rsa = data['id_rsa'].replace('\\n', '\n')
    mw.writeFile(SSH_PRIVATE_KEY, id_rsa)

    ip = data["ip"]
    master_port = data['port']
    db_user = data['db_user']
    print("master ip:", ip)

    writeDbSyncStatus({'code': 0, 'msg': '开始同步...', 'progress': 0})

    import paramiko
    paramiko.util.log_to_file('paramiko.log')
    ssh = paramiko.SSHClient()

    print(SSH_PRIVATE_KEY)
    if not os.path.exists(SSH_PRIVATE_KEY):
        writeDbSyncStatus({'code': 0, 'msg': '需要配置SSH......', 'progress': 0})
        return 'fail'

    try:
        # ssh.load_system_host_keys()
        mw.execShell("chmod 600 " + SSH_PRIVATE_KEY)
        key = paramiko.RSAKey.from_private_key_file(SSH_PRIVATE_KEY)
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print(ip, master_port)

        # pkey=key
        # key_filename=SSH_PRIVATE_KEY
        ssh.connect(hostname=ip, port=int(master_port),
                    username='root', pkey=key)
    except Exception as e:
        print(str(e))
        writeDbSyncStatus(
            {'code': 0, 'msg': 'SSH配置错误:' + str(e), 'progress': 0})
        return 'fail'

    writeDbSyncStatus({'code': 0, 'msg': '登录Master成功...', 'progress': 5})
    dbname = args['db']
    cmd = "cd /www/server/mdserver-web && python3 plugins/mariadb/index.py dump_mysql_data {\"db\":'" + dbname + "'}"
    print(cmd)
    stdin, stdout, stderr = ssh.exec_command(cmd)
    result = stdout.read()
    result = result.decode('utf-8')
    if result.strip() == 'ok':
        writeDbSyncStatus({'code': 1, 'msg': '主服务器备份完成...', 'progress': 30})
    else:
        writeDbSyncStatus(
            {'code': 1, 'msg': '主服务器备份失败...:' + str(result), 'progress': 100})
        return 'fail'

    print("同步文件", "start")
    # cmd = 'scp -P' + str(master_port) + ' -i ' + SSH_PRIVATE_KEY + \
    #     ' root@' + ip + ':/tmp/dump.sql.gz /tmp'
    t = ssh.get_transport()
    sftp = paramiko.SFTPClient.from_transport(t)
    copy_status = sftp.get("/tmp/dump.sql.gz", "/tmp/dump.sql.gz")
    print("同步信息:", copy_status)
    print("同步文件", "end")
    if copy_status == None:
        writeDbSyncStatus({'code': 2, 'msg': '数据同步本地完成...', 'progress': 40})

    cmd = 'cd /www/server/mdserver-web && python3 plugins/mariadb/index.py get_master_rep_slave_user_cmd {"username":"' + db_user + '","db":""}'
    stdin, stdout, stderr = ssh.exec_command(cmd)
    result = stdout.read()
    result = result.decode('utf-8')
    cmd_data = json.loads(result)

    db.query('stop slave')
    writeDbSyncStatus({'code': 3, 'msg': '停止从库完成...', 'progress': 45})

    cmd = cmd_data['data']['cmd']
    # 保证同步IP一致
    if cmd.find('SOURCE_HOST') > -1:
        cmd = re.sub(r"SOURCE_HOST='(.*)'", "SOURCE_HOST='" + ip + "'", cmd, 1)

    if cmd.find('MASTER_HOST') > -1:
        cmd = re.sub(r"MASTER_HOST='(.*)'", "SOURCE_HOST='" + ip + "'", cmd, 1)

    db.query(cmd)
    uinfo = cmd_data['data']['info']
    ps = uinfo['username'] + "|" + uinfo['password']
    id_rsa_conn.where('ip=?', (ip,)).setField('ps', ps)
    writeDbSyncStatus({'code': 4, 'msg': '刷新从库同步信息完成...', 'progress': 50})

    pwd = pSqliteDb('config').where('id=?', (1,)).getField('mysql_root')
    root_dir = getServerDir()
    msock = root_dir + "/mysql.sock"
    mw.execShell("cd /tmp && gzip -d dump.sql.gz")
    cmd = root_dir + "/bin/mysql -S " + msock + \
        " -uroot -p" + pwd + " < /tmp/dump.sql"
    import_data = mw.execShell(cmd)
    if import_data[0] == '':
        print(import_data[1])
        writeDbSyncStatus({'code': 5, 'msg': '导入数据完成...', 'progress': 90})
    else:
        print(import_data[0])
        writeDbSyncStatus({'code': 5, 'msg': '导入数据失败...', 'progress': 100})
        return 'fail'

    db.query("start slave")
    writeDbSyncStatus({'code': 6, 'msg': '从库重启完成...', 'progress': 100})

    os.system("rm -rf " + SSH_PRIVATE_KEY)
    os.system("rm -rf /tmp/dump.sql")
    return True


def fullSync(version=''):
    args = getArgs()
    data = checkArgs(args, ['db', 'begin'])
    if not data[0]:
        return data[1]

    status_file = '/tmp/db_async_status.txt'
    if args['begin'] == '1':
        cmd = 'cd ' + mw.getRunDir() + ' && python3 ' + \
            getPluginDir() + \
            '/index.py do_full_sync {"db":"' + args['db'] + '"} &'
        print(cmd)
        mw.execShell(cmd)
        return json.dumps({'code': 0, 'msg': '同步数据中!', 'progress': 0})

    if os.path.exists(status_file):
        c = mw.readFile(status_file)
        tmp = json.loads(c)
        if tmp['code'] == 1:
            sys_dump_sql = "/tmp/dump.sql"
            if os.path.exists(sys_dump_sql):
                dump_size = os.path.getsize(sys_dump_sql)
                tmp['msg'] = tmp['msg'] + ":" + "同步文件:" + mw.toSize(dump_size)
            c = json.dumps(tmp)

        # if tmp['code'] == 6:
        #     os.remove(status_file)
        return c

    return json.dumps({'code': 0, 'msg': '点击开始,开始同步!', 'progress': 0})


def installPreInspection(version):
    swap_path = mw.getServerDir() + "/swap"
    if not os.path.exists(swap_path):
        return "为了稳定安装MariaDB,先安装swap插件!"
    return 'ok'


def uninstallPreInspection(version):
    stop(version)
    if mw.isDebugMode():
        return 'ok'

    return "请手动删除MariaDB[{}]<br/> rm -rf {}".format(version, getServerDir())

if __name__ == "__main__":
    func = sys.argv[1]

    version = "5.6"
    version_pl = getServerDir() + "/version.pl"
    if os.path.exists(version_pl):
        version = mw.readFile(version_pl).strip()

    if func == 'status':
        print(status(version))
    elif func == 'start':
        print(start(version))
    elif func == 'stop':
        print(stop(version))
    elif func == 'restart':
        print(restart(version))
    elif func == 'reload':
        print(reload(version))
    elif func == 'initd_status':
        print(initdStatus())
    elif func == 'initd_install':
        print(initdInstall())
    elif func == 'initd_uninstall':
        print(initdUinstall())
    elif func == 'install_pre_inspection':
        print(installPreInspection(version))
    elif func == 'uninstall_pre_inspection':
        print(uninstallPreInspection(version))
    elif func == 'run_info':
        print(runInfo())
    elif func == 'db_status':
        print(myDbStatus())
    elif func == 'set_db_status':
        print(setDbStatus())
    elif func == 'conf':
        print(getConf())
    elif func == 'bin_log':
        print(binLog())
    elif func == 'clean_bin_log':
        print(cleanBinLog())
    elif func == 'error_log':
        print(getErrorLog())
    elif func == 'show_log':
        print(getShowLogFile())
    elif func == 'my_db_pos':
        print(getMyDbPos())
    elif func == 'set_db_pos':
        print(setMyDbPos())
    elif func == 'my_port':
        print(getMyPort())
    elif func == 'set_my_port':
        print(setMyPort())
    elif func == 'init_pwd':
        print(initMysqlPwd())
    elif func == 'get_db_list':
        print(getDbList())
    elif func == 'set_db_backup':
        print(setDbBackup())
    elif func == 'import_db_backup':
        print(importDbBackup())
    elif func == 'delete_db_backup':
        print(deleteDbBackup())
    elif func == 'get_db_backup_list':
        print(getDbBackupList())
    elif func == 'add_db':
        print(addDb())
    elif func == 'del_db':
        print(delDb())
    elif func == 'sync_get_databases':
        print(syncGetDatabases())
    elif func == 'sync_to_databases':
        print(syncToDatabases())
    elif func == 'set_root_pwd':
        print(setRootPwd(version))
    elif func == 'set_user_pwd':
        print(setUserPwd(version))
    elif func == 'get_db_access':
        print(getDbAccess())
    elif func == 'set_db_access':
        print(setDbAccess())
    elif func == 'get_db_rw':
        print(setDbRw(version))
    elif func == 'set_db_ps':
        print(setDbPs())
    elif func == 'get_db_info':
        print(getDbInfo())
    elif func == 'repair_table':
        print(repairTable())
    elif func == 'opt_table':
        print(optTable())
    elif func == 'alter_table':
        print(alterTable())
    elif func == 'get_total_statistics':
        print(getTotalStatistics())
    elif func == 'get_dbrun_mode':
        print(getDbrunMode(version))
    elif func == 'set_dbrun_mode':
        print(setDbrunMode(version))
    elif func == 'get_masterdb_list':
        print(getMasterDbList(version))
    elif func == 'get_master_status':
        print(getMasterStatus(version))
    elif func == 'set_master_status':
        print(setMasterStatus(version))
    elif func == 'set_db_master':
        print(setDbMaster(version))
    elif func == 'set_db_slave':
        print(setDbSlave(version))
    elif func == 'set_dbmaster_access':
        print(setDbMasterAccess())
    elif func == 'get_master_rep_slave_list':
        print(getMasterRepSlaveList(version))
    elif func == 'add_master_rep_slave_user':
        print(addMasterRepSlaveUser(version))
    elif func == 'del_master_rep_slave_user':
        print(delMasterRepSlaveUser(version))
    elif func == 'update_master_rep_slave_user':
        print(updateMasterRepSlaveUser(version))
    elif func == 'get_master_rep_slave_user_cmd':
        print(getMasterRepSlaveUserCmd(version))
    elif func == 'get_slave_list':
        print(getSlaveList(version))
    elif func == 'get_slave_sync_cmd':
        print(getSlaveSyncCmd(version))
    elif func == 'get_slave_ssh_list':
        print(getSlaveSSHList(version))
    elif func == 'get_slave_ssh_by_ip':
        print(getSlaveSSHByIp(version))
    elif func == 'add_slave_ssh':
        print(addSlaveSSH(version))
    elif func == 'del_slave_ssh':
        print(delSlaveSSH(version))
    elif func == 'update_slave_ssh':
        print(updateSlaveSSH(version))
    elif func == 'init_slave_status':
        print(initSlaveStatus(version))
    elif func == 'set_slave_status':
        print(setSlaveStatus(version))
    elif func == 'delete_slave':
        print(deleteSlave(version))
    elif func == 'full_sync':
        print(fullSync(version))
    elif func == 'do_full_sync':
        print(doFullSync(version))
    elif func == 'dump_mysql_data':
        print(dumpMysqlData(version))
    else:
        print('error')
