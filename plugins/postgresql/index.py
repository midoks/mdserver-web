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
    return 'postgresql'


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
    path = getServerDir() + '/data/postgresql.conf'
    return path


def configTpl():

    clist = []

    app_dir = getServerDir()
    clist.append(app_dir + "/data/postgresql.conf")
    clist.append(app_dir + "/data/pg_hba.conf")

    return mw.getJson(clist)


def readConfigTpl():
    args = getArgs()
    data = checkArgs(args, ['file'])
    if not data[0]:
        return data[1]

    content = mw.readFile(args['file'])
    return mw.returnJson(True, 'ok', content)


def getDbPort():
    file = getConf()
    content = mw.readFile(file)
    rep = 'port\s*=\s*(\d*)?'
    tmp = re.search(rep, content)
    return tmp.groups()[0].strip()


def getSocketFile():
    file = getConf()
    content = mw.readFile(file)
    rep = 'socket\s*=\s*(.*)'
    tmp = re.search(rep, content)
    return tmp.groups()[0].strip()


def getInitdTpl(version=''):
    path = getPluginDir() + '/init.d/postgresql.tpl'
    if not os.path.exists(path):
        path = getPluginDir() + '/init.d/postgresql.tpl'
    return path


def contentReplace(content):
    service_path = mw.getServerDir()
    content = content.replace('{$ROOT_PATH}', mw.getRootDir())
    content = content.replace('{$SERVER_PATH}', service_path)
    content = content.replace('{$APP_PATH}', service_path + '/postgresql')
    return content


def pSqliteDb(dbname='databases'):
    file = getServerDir() + '/pgsql.db'
    name = 'pgsql'
    if not os.path.exists(file):
        conn = mw.M(dbname).dbPos(getServerDir(), name)
        csql = mw.readFile(getPluginDir() + '/conf/pgsql.sql')
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


def pgDb():

    sys.path.append(getPluginDir() + "/class")
    import pg

    db = pg.ORM()

    db.setPort(getDbPort())
    # db.setSocket(getSocketFile())
    db.setPwd(pSqliteDb('config').where('id=?', (1,)).getField('pg_root'))
    return db


def initDreplace(version=''):

    conf_dir = getServerDir()
    conf_list = [
        conf_dir + "/logs",
        conf_dir + "/tmp",
    ]
    for c in conf_list:
        if not os.path.exists(c):
            os.mkdir(c)

    init_pl = conf_dir + "/init.pl"
    if not os.path.exists(init_pl):
        # mw.writeFile(init_pl, 'ok')
        pg_conf = conf_dir + '/data/postgresql.conf'
        tpl = getPluginDir() + '/conf/postgresql.conf'
        content = mw.readFile(tpl)
        content = contentReplace(content)
        mw.writeFile(pg_conf, content)

        logfile = runLog()
        if not os.path.exists(logfile):
            mw.writeFile(logfile, '')

    # systemd
    system_dir = mw.systemdCfgDir()
    service = system_dir + '/postgresql.service'
    if os.path.exists(system_dir) and not os.path.exists(service):
        tpl = getPluginDir() + '/init.d/postgresql.service.tpl'
        service_path = mw.getServerDir()
        content = mw.readFile(tpl)
        content = contentReplace(content)
        mw.writeFile(service, content)
        mw.execShell('systemctl daemon-reload')

    if not mw.isAppleSystem():
        mw.execShell('chown -R postgresql:postgresql ' + getServerDir())

    initd_path = getServerDir() + '/init.d'
    if not os.path.exists(initd_path):
        os.mkdir(initd_path)

    file_bin = initd_path + '/' + getPluginName()
    if not os.path.exists(file_bin):
        tpl = getInitdTpl(version)
        content = mw.readFile(tpl)
        content = contentReplace(content)
        mw.writeFile(file_bin, content)
        mw.execShell('chmod +x ' + file_bin)
    return file_bin


def status(version=''):
    data = mw.execShell(
        "ps -ef|grep postgres |grep -v grep | grep -v python | grep -v mdserver-web | awk '{print $2}'")
    if data[0] == '':
        return 'stop'
    return 'start'


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
    info = mw.getNumLines(filename, 18)
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
    return 'postgresql'


def initPgData():
    serverdir = getServerDir()
    if not os.path.exists(serverdir + '/data'):
        cmd = serverdir + '/bin/initdb -D ' + serverdir + "/data"
        if not mw.isAppleSystem():
            cmd = "echo \"" + serverdir + "/bin/initdb -D " + \
                serverdir + "/data\" | su - postgresql"
        # print(cmd)
        mw.execShell(cmd)
        return False
    return True


def initPgPwd():

    serverdir = getServerDir()
    pwd = mw.getRandomString(16)

    cmd_pass = "echo \"create user root with superuser password '" + pwd + "'\" | "
    cmd_pass = cmd_pass + serverdir + '/bin/psql -d postgres'
    data = mw.execShell(cmd_pass)
    # print(cmd_pass)
    # print(data)

    pSqliteDb('config').where('id=?', (1,)).save('pg_root', (pwd,))
    return True


def pgOp(version, method):
    # import commands
    init_file = initDreplace()
    cmd = init_file + ' ' + method
    # print(cmd)
    try:
        isInited = initPgData()
        if not isInited:
            if mw.isAppleSystem():
                cmd_init_start = init_file + ' start'
                subprocess.Popen(cmd_init_start, stdout=subprocess.PIPE, shell=True,
                                 bufsize=4096, stderr=subprocess.PIPE)

                time.sleep(6)
            else:
                mw.execShell('systemctl start postgresql')

            initPgPwd()

            if mw.isAppleSystem():
                cmd_init_stop = init_file + ' stop'
                subprocess.Popen(cmd_init_stop, stdout=subprocess.PIPE, shell=True,
                                 bufsize=4096, stderr=subprocess.PIPE)
                time.sleep(3)
            else:
                mw.execShell('systemctl stop postgresql')

        if mw.isAppleSystem():
            sub = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True,
                                   bufsize=4096, stderr=subprocess.PIPE)
            sub.wait(5)
        else:
            mw.execShell('systemctl ' + method + ' postgresql')
        return 'ok'
    except Exception as e:
        # raise
        return method + ":" + str(e)


def appCMD(version, action):
    return pgOp(version, action)


def start(version=''):
    return appCMD(version, 'start')


def stop(version=''):
    return appCMD(version, 'stop')


def restart(version=''):
    return appCMD(version, 'restart')


def reload(version=''):
    logfile = runLog()
    if os.path.exists(logfile):
        mw.writeFile(logfile, '')
    return appCMD(version, 'reload')


def initdStatus():
    if mw.isAppleSystem():
        return "Apple Computer does not support"

    shell_cmd = 'systemctl status postgresql | grep loaded | grep "enabled;"'
    data = mw.execShell(shell_cmd)
    if data[0] == '':
        return 'fail'
    return 'ok'


def initdInstall():
    if mw.isAppleSystem():
        return "Apple Computer does not support"

    mw.execShell('systemctl enable postgresql')
    return 'ok'


def initdUinstall():
    if mw.isAppleSystem():
        return "Apple Computer does not support"

    mw.execShell('systemctl disable postgresql')
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

    # mw.execShell('/etc/init.d/mysqld stop')
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


def getPgPort():
    file = getConf()
    content = mw.readFile(file)
    rep = 'port\s*=\s*(.*)'
    tmp = re.search(rep, content)
    return tmp.groups()[0].strip()


def setPgPort():
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
        return mw.returnJson(False, 'PG未启动', [])

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


def runLog():
    return getServerDir() + "/logs/server.log"


def myDbStatus():
    result = {}
    db = pMysqlDb()
    data = db.query('show variables')
    # isError = isSqlError(data)
    # if isError != None:
    #     return isError

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


def __createUser(dbname, username, password, address):
    pdb = pMysqlDb()

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

    mysql_cmd = mw.getRootDir() + '/server/mysql/bin/mysql -uroot -p' + pwd + \
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
    pdb = pgDb()
    psdb = pSqliteDb('databases')
    data = pdb.query('SELECT * FROM pg_database WHERE datistemplate = false')
    print(data)
    return
    # isError = isSqlError(data)
    # if isError != None:
    #     return isError
    users = pdb.query(
        "select User,Host from mysql.user where User!='root' AND Host!='localhost' AND Host!=''")
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


def installPreInspection(version):
    return 'ok'


def uninstallPreInspection(version):
    # return "请手动删除MySQL[{}]".format(version)
    return 'ok'

if __name__ == "__main__":
    func = sys.argv[1]

    version = "14.4"
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
    elif func == 'conf':
        print(getConf())
    elif func == 'config_tpl':
        print(configTpl())
    elif func == 'read_config_tpl':
        print(readConfigTpl())
    elif func == 'run_info':
        print(runInfo())
    elif func == 'run_log':
        print(runLog())
    elif func == 'pg_port':
        print(getPgPort())
    elif func == 'set_pg_port':
        print(setPgPort())
    elif func == 'get_db_list':
        print(getDbList())
    elif func == 'sync_get_databases':
        print(syncGetDatabases())
    else:
        print('error')
