# coding:utf-8

import sys
import io
import os
import time
import subprocess
import re
import json

reload(sys)
sys.setdefaultencoding('utf-8')

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


def checkArgs(data, ck=[]):
    for i in range(len(ck)):
        if not ck[i] in data:
            return (False, public.returnJson(False, '参数:(' + ck[i] + ')没有!'))
    return (True, public.returnJson(True, 'ok'))


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
    time.sleep(5)

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


def isSqlError(mysqlMsg):
    # 检测数据库执行错误
    mysqlMsg = str(mysqlMsg)
    if "MySQLdb" in mysqlMsg:
        return public.returnJson(False, 'MySQLdb组件缺失! <br>进入SSH命令行输入： pip install mysql-python')
    if "2002," in mysqlMsg:
        return public.returnJson(False, '数据库连接失败,请检查数据库服务是否启动!')
    if "using password:" in mysqlMsg:
        return public.returnJson(False, '数据库管理密码错误!')
    if "Connection refused" in mysqlMsg:
        return public.returnJson(False, '数据库连接失败,请检查数据库服务是否启动!')
    if "1133" in mysqlMsg:
        return public.returnJson(False, '数据库用户不存在!')
    if "1007" in mysqlMsg:
        return public.returnJson(False, '数据库已经存在!')
    return None


def mapToList(map_obj):
    # map to list
    try:
        if type(map_obj) != list and type(map_obj) != str:
            map_obj = list(map_obj)
        return map_obj
    except:
        return []


def __createUser(dbname, username, password, address):
    pdb = pMysqlDb()
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
    field = 'id,pid,name,username,password,accept,ps,addtime'
    clist = conn.where(condition, ()).field(
        field).limit(limit).order('id desc').select()
    count = conn.where(condition, ()).count()
    _page = {}
    _page['count'] = count
    _page['p'] = page
    _page['row'] = page_size
    _page['tojs'] = 'dbList'
    data['page'] = public.getPage(_page)
    data['data'] = clist

    info = {}
    info['root_pwd'] = pSqliteDb('config').where(
        'id=?', (1,)).getField('mysql_root')
    data['info'] = info

    return public.getJson(data)


def syncGetDatabases():
    pdb = pMysqlDb()
    psdb = pSqliteDb('databases')
    data = pdb.query('show databases')
    isError = isSqlError(data)
    if isError != None:
        return isError
    users = pdb.query(
        "select User,Host from mysql.user where User!='root' AND Host!='localhost' AND Host!=''")
    nameArr = ['information_schema', 'performance_schema', 'mysql', 'sys']
    n = 0
    for value in data:
        b = False
        for key in nameArr:
            if value[0] == key:
                b = True
                break
        if b:
            continue
        if psdb.where("name=?", (value[0],)).count():
            continue
        host = '127.0.0.1'
        for user in users:
            if value[0] == user[0]:
                host = user[1]
                break

        ps = public.getMsg('INPUT_PS')
        if value[0] == 'test':
            ps = public.getMsg('DATABASE_TEST')
        addTime = time.strftime('%Y-%m-%d %X', time.localtime())
        if psdb.add('name,username,password,accept,ps,addtime', (value[0], value[0], '', host, ps, addTime)):
            n += 1

    msg = public.getInfo('本次共从服务器获取了{1}个数据库!', (str(n),))
    return public.returnJson(True, msg)


def toDbBase(find):
    pdb = pMysqlDb()
    psdb = pSqliteDb('databases')
    if len(find['password']) < 3:
        find['username'] = find['name']
        find['password'] = public.md5(str(time.time()) + find['name'])[0:10]
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
    msg = public.getInfo('本次共同步了{1}个数据库!', (str(n),))
    return public.returnJson(True, msg)


def setRootPwd():
    args = getArgs()
    if not 'password' in args:
        return 'password missing'
    password = args['password']
    try:
        pdb = pMysqlDb()
        result = pdb.query("show databases")
        isError = isSqlError(result)
        if isError != None:
            return isError

        m_version = public.readFile(getServerDir() + '/version.pl')
        if m_version.find('5.7') == 0 or m_version.find('8.0') == 0:
            pdb.execute(
                "UPDATE mysql.user SET authentication_string='' WHERE user='root'")
            pdb.execute(
                "ALTER USER 'root'@'localhost' IDENTIFIED BY '%s'" % password)
            pdb.execute(
                "ALTER USER 'root'@'127.0.0.1' IDENTIFIED BY '%s'" % password)
        else:
            result = pdb.execute(
                "update mysql.user set Password=password('" + password + "') where User='root'")
        pdb.execute("flush privileges")
        pSqliteDb('config').where('id=?', (1,)).save('mysql_root', (password,))
        return public.returnJson(True, '数据库root密码修改成功!')
    except Exception as ex:
        return public.returnJson(False, '修改错误:' + str(ex))


def setUserPwd():
    args = getArgs()
    data = checkArgs(args, ['password', 'name'])
    if not data[0]:
        return data[1]

    newpassword = args['password']
    username = args['name']
    id = args['id']
    try:
        pdb = pMysqlDb()
        psdb = pSqliteDb('databases')
        name = psdb.where('id=?', (id,)).getField('name')

        m_version = public.readFile(getServerDir() + '/version.pl')
        if m_version.find('5.7') == 0 or m_version.find('8.0') == 0:
            tmp = pdb.query(
                "select Host from mysql.user where User='" + name + "' AND Host!='localhost'")
            accept = mapToList(tmp)
            pdb.execute(
                "update mysql.user set authentication_string='' where User='" + username + "'")
            result = pdb.execute(
                "ALTER USER `%s`@`localhost` IDENTIFIED BY '%s'" % (username, newpassword))
            for my_host in accept:
                pdb.execute("ALTER USER `%s`@`%s` IDENTIFIED BY '%s'" % (
                    username, my_host[0], newpassword))
        else:
            result = pdb.execute("update mysql.user set Password=password('" +
                                 newpassword + "') where User='" + username + "'")
        isError = isSqlError(result)
        if isError != None:
            return isError
        pdb.execute("flush privileges")
        psdb.where("id=?", (id,)).setField('password', newpassword)
        return public.returnJson(True, public.getInfo('修改数据库[{1}]密码成功!', (name)))
    except Exception as ex:
        print str(ex)
        return public.returnJson(False, public.getInfo('修改数据库[{1}]密码失败!', (name)))


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
        return public.returnJson(False, '数据库名称不能带有特殊符号!')
    checks = ['root', 'mysql', 'test', 'sys', 'panel_logs']
    if dbuser in checks or len(dbuser) < 1:
        return public.returnJson(False, '数据库用户名不合法!')
    if dbname in checks or len(dbname) < 1:
        return public.returnJson(False, '数据库名称不合法!')

    if len(password) < 1:
        password = public.md5(time.time())[0:8]

    wheres = {
        'utf8':   'utf8_general_ci',
        'utf8mb4':   'utf8mb4_general_ci',
        'gbk':   'gbk_chinese_ci',
        'big5':   'big5_chinese_ci'
    }
    codeStr = wheres[codeing]

    pdb = pMysqlDb()
    psdb = pSqliteDb('databases')

    if psdb.where("name=? or username=?", (dbname, dbuser)).count():
        return public.returnJson(False, '数据库已存在!')

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
    return public.returnJson(True, '添加成功!')


def delDb():
    args = getArgs()
    data = checkArgs(args, ['id', 'name'])
    if not data[0]:
        return data[1]
    try:
        id = args['id']
        name = args['name']
        psdb = pSqliteDb('databases')
        pdb = pMysqlDb()
        find = psdb.where("id=?", (id,)).field(
            'id,pid,name,username,password,accept,ps,addtime').find()
        accept = find['accept']
        username = find['username']

        # 删除MYSQL
        result = pdb.execute("drop database `" + name + "`")
        isError = isSqlError(result)
        if isError != None:
            return isError

        users = pdb.query(
            "select Host from mysql.user where User='" + username + "' AND Host!='localhost'")
        pdb.execute("drop user '" + username + "'@'localhost'")
        for us in users:
            pdb.execute("drop user '" + username + "'@'" + us[0] + "'")
        pdb.execute("flush privileges")

        # 删除SQLITE
        psdb.where("id=?", (id,)).delete()
        return public.returnJson(True, '删除成功!')
    except Exception as ex:
        return public.returnJson(False, '删除失败!' + str(ex))


def getDbAccess():
    args = getArgs()
    data = checkArgs(args, ['username'])
    if not data[0]:
        return data[1]
    username = args['username']
    pdb = pMysqlDb()

    users = pdb.query("select Host from mysql.user where User='" +
                      username + "' AND Host!='localhost'")
    isError = isSqlError(users)
    if isError != None:
        return isError

    users = mapToList(users)
    if len(users) < 1:
        return public.returnJson(True, "127.0.0.1")
    accs = []
    for c in users:
        accs.append(c[0])
    userStr = ','.join(accs)
    return public.returnJson(True, userStr)


def setDbAccess():
    args = getArgs()
    data = checkArgs(args, ['username', 'access'])
    if not data[0]:
        return data[1]
    name = args['username']
    access = args['access']
    pdb = pMysqlDb()
    psdb = pSqliteDb('databases')

    dbname = psdb.where('username=?', (name,)).getField('name')
    password = psdb.where("username=?", (name,)).getField('password')
    users = pdb.query("select Host from mysql.user where User='" +
                      name + "' AND Host!='localhost'")
    for us in users:
        pdb.execute("drop user '" + name + "'@'" + us[0] + "'")

    __createUser(dbname, name, password, access)

    psdb.where('username=?', (name,)).save('accept', (access,))
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
    elif func == 'init_pwd':
        print initMysqlPwd()
    elif func == 'get_db_list':
        print getDbList()
    elif func == 'add_db':
        print addDb()
    elif func == 'del_db':
        print delDb()
    elif func == 'sync_get_databases':
        print syncGetDatabases()
    elif func == 'sync_to_databases':
        print syncToDatabases()
    elif func == 'set_root_pwd':
        print setRootPwd()
    elif func == 'set_user_pwd':
        print setUserPwd()
    elif func == 'get_db_access':
        print getDbAccess()
    elif func == 'set_db_access':
        print setDbAccess()
    else:
        print 'error'
