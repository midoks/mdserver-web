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
    return 'mysql'


def getPluginDir():
    return mw.getPluginDir() + '/' + getPluginName()


def getSPluginDir():
    return '/www/server/mdserver-web/plugins/' + getPluginName()


def getServerDir():
    return mw.getServerDir() + '/' + getPluginName()


def getInitDFile():
    current_os = mw.getOs()
    if current_os == 'darwin':
        return '/tmp/' + getPluginName()

    if current_os.startswith('freebsd'):
        return '/etc/rc.d/' + getPluginName()
    return '/etc/init.d/' + getPluginName()


def getArgs():
    args = sys.argv[2:]
    tmp = {}
    args_len = len(args)
    if args_len == 1:
        t = args[0].strip('{').strip('}')
        if t.strip() == '':
            tmp = []
        else:
            t = t.split(':',1)
            tmp[t[0]] = t[1]
        tmp[t[0]] = t[1]
    elif args_len > 1:
        for i in range(len(args)):
            t = args[i].split(':',1)
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


def getDbPort():
    file = getConf()
    content = mw.readFile(file)
    rep = 'port\s*=\s*(.*)'
    tmp = re.search(rep, content)
    return tmp.groups()[0].strip()


def getDbServerId():
    file = getConf()
    content = mw.readFile(file)
    rep = 'server-id\s*=\s*(.*)'
    tmp = re.search(rep, content)
    return tmp.groups()[0].strip()


def getSocketFile():
    file = getConf()
    content = mw.readFile(file)
    rep = 'socket\s*=\s*(.*)'
    tmp = re.search(rep, content)
    return tmp.groups()[0].strip()


def getErrorLogsFile():
    file = getConf()
    content = mw.readFile(file)
    rep = 'log-error\s*=\s*(.*)'
    tmp = re.search(rep, content)
    return tmp.groups()[0].strip()

def getAuthPolicy():
    file = getConf()
    content = mw.readFile(file)
    rep = 'authentication_policy\s*=\s*(.*)'
    tmp = re.search(rep, content)
    if tmp:
        return tmp.groups()[0].strip()
    # caching_sha2_password
    return 'mysql_native_password'


def getInitdTpl(version=''):
    path = getPluginDir() + '/init.d/mysql' + version + '.tpl'
    if not os.path.exists(path):
        path = getPluginDir() + '/init.d/mysql.tpl'
    return path


def contentReplace(content):

    service_path = mw.getServerDir()
    content = content.replace('{$ROOT_PATH}', mw.getRootDir())
    content = content.replace('{$SERVER_PATH}', service_path)
    content = content.replace('{$SERVER_APP_PATH}', service_path + '/mysql')

    server_id = int(time.time())
    content = content.replace('{$SERVER_ID}', str(server_id))

    if mw.isAppleSystem():
        content = content.replace(
            'lower_case_table_names=0', 'lower_case_table_names=2')

    return content


def pSqliteDb(dbname='databases'):
    file = getServerDir() + '/mysql.db'
    name = 'mysql'

    import_sql = mw.readFile(getPluginDir() + '/conf/mysql.sql')
    md5_sql = mw.md5(import_sql)

    import_sign = False
    save_md5_file = getServerDir() + '/import_sql.md5'
    if os.path.exists(save_md5_file):
        save_md5_sql = mw.readFile(save_md5_file)
        if save_md5_sql != md5_sql:
            import_sign = True
            mw.writeFile(save_md5_file, md5_sql)
    else:
        mw.writeFile(save_md5_file, md5_sql)

    if not os.path.exists(file) or import_sql:
        conn = mw.M(dbname).dbPos(getServerDir(), name)
        csql_list = import_sql.split(';')
        for index in range(len(csql_list)):
            conn.execute(csql_list[index], ())

    conn = mw.M(dbname).dbPos(getServerDir(), name)
    return conn


def pMysqlDb():
    # pymysql
    db = mw.getMyORM()
    # MySQLdb |
    # db = mw.getMyORMDb()
    # print(getDbPort())
    db.setPort(getDbPort())
    db.setSocket(getSocketFile())
    # db.setCharset("utf8")
    db.setPwd(pSqliteDb('config').where('id=?', (1,)).getField('mysql_root'))
    return db


def makeInitRsaKey(version=''):
    try:
        datadir = getDataDir()
    except Exception as e:
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
    conf_dir = getServerDir() + '/etc'
    mode_dir = conf_dir + '/mode'

    conf_list = [
        conf_dir,
        mode_dir,
    ]
    for conf in conf_list:
        if not os.path.exists(conf):
            os.mkdir(conf)

    tmp_dir = getServerDir() + '/tmp'
    if not os.path.exists(tmp_dir):
        os.mkdir(tmp_dir)
        mw.execShell("chown -R mysql:mysql " + tmp_dir)
        mw.execShell("chmod 750 " + tmp_dir)

    my_conf = conf_dir + '/my.cnf'
    if not os.path.exists(my_conf):
        tpl = getPluginDir() + '/conf/my' + version + '.cnf'
        content = mw.readFile(tpl)
        content = contentReplace(content)
        mw.writeFile(my_conf, content)

    classic_conf = mode_dir + '/classic.cnf'
    if not os.path.exists(classic_conf):
        tpl = getPluginDir() + '/conf/classic.cnf'
        content = mw.readFile(tpl)
        content = contentReplace(content)
        mw.writeFile(classic_conf, content)

    gtid_conf = mode_dir + '/gtid.cnf'
    if not os.path.exists(gtid_conf):
        tpl = getPluginDir() + '/conf/gtid.cnf'
        content = mw.readFile(tpl)
        content = contentReplace(content)
        mw.writeFile(gtid_conf, content)

    # systemd
    system_dir = mw.systemdCfgDir()
    service = system_dir + '/mysql.service'
    if os.path.exists(system_dir) and not os.path.exists(service):
        tpl = getPluginDir() + '/init.d/mysql.service.tpl'
        service_path = mw.getServerDir()
        content = mw.readFile(tpl)
        content = content.replace('{$SERVER_PATH}', service_path)
        mw.writeFile(service, content)
        mw.execShell('systemctl daemon-reload')

    if not mw.isAppleSystem():
        mw.execShell('chown -R mysql mysql ' + getServerDir())

    initd_path = getServerDir() + '/init.d'
    if not os.path.exists(initd_path):
        os.mkdir(initd_path)

    file_bin = initd_path + '/' + getPluginName()
    if not os.path.exists(file_bin):
        initd_tpl = getInitdTpl(version)
        content = mw.readFile(initd_tpl)
        content = contentReplace(content)
        mw.writeFile(file_bin, content)
        mw.execShell('chmod +x ' + file_bin)
    return file_bin


def process_status():
    cmd = "ps -ef|grep mysql |grep -v grep | grep -v python | awk '{print $2}'"
    data = mw.execShell(cmd)
    if data[0] == '':
        return 'stop'
    return 'start'


def status(version=''):
    path = getConf()
    if not os.path.exists(path):
        return 'stop'

    pid = getPidFile()
    if not os.path.exists(pid):
        return 'stop'

    return 'start'


def getDataDir():
    file = getConf()
    content = mw.readFile(file)
    rep = 'datadir\s*=\s*(.*)'
    tmp = re.search(rep, content)
    return tmp.groups()[0].strip()


def getLogBinName():
    file = getConf()
    content = mw.readFile(file)
    rep = 'log-bin\s*=\s*(.*)'
    tmp = re.search(rep, content)
    return tmp.groups()[0].strip()


def getPidFile():
    file = getConf()
    content = mw.readFile(file)
    rep = 'pid-file\s*=\s*(.*)'
    tmp = re.search(rep, content)
    return tmp.groups()[0].strip()


def binLog(version = ''):
    args = getArgs()
    conf = getConf()
    con = mw.readFile(conf)

    if con.find('#log-bin=mysql-bin') != -1:
        if 'status' in args:
            return mw.returnJson(False, '0')
        con = con.replace('#log-bin=mysql-bin', 'log-bin=mysql-bin')
        con = con.replace('#binlog_format=mixed', 'binlog_format=mixed')
        mw.execShell('sync')
        restart(version)
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
        restart(version)
        mw.execShell('rm -f ' + path + '/mysql-bin.*')

    mw.writeFile(conf, con)
    return mw.returnJson(True, '设置成功!')


def binLogList():
    args = getArgs()
    data = checkArgs(args, ['page', 'page_size', 'tojs'])
    if not data[0]:
        return data[1]

    page = int(args['page'])
    page_size = int(args['page_size'])

    data_dir = getDataDir()
    log_bin_name = getLogBinName()

    alist = os.listdir(data_dir)
    log_bin_l = []
    for x in range(len(alist)):
        f = alist[x]
        t = {}
        if f.startswith(log_bin_name) and not f.endswith('.index'):
            abspath = data_dir + '/' + f
            t['name'] = f
            t['size'] = os.path.getsize(abspath)
            t['time'] = mw.getDataFromInt(os.path.getctime(abspath))
            log_bin_l.append(t)

    log_bin_l = sorted(log_bin_l, key=lambda x: x['time'], reverse=True)

    # print(log_bin_l)
    # print(data_dir, log_bin_name)

    count = len(log_bin_l)

    page_start = (page - 1) * page_size
    page_end = page_start + page_size
    if page_end > count:
        page_end = count

    data = {}
    page_args = {}
    page_args['count'] = count
    page_args['p'] = page
    page_args['row'] = page_size
    page_args['tojs'] = args['tojs']
    data['page'] = mw.getPage(page_args)
    data['data'] = log_bin_l[page_start:page_end]

    return mw.getJson(data)


def cleanBinLog():
    db = pMysqlDb()
    cleanTime = time.strftime('%Y-%m-%d %H:%i:%s', time.localtime())
    db.execute("PURGE MASTER LOGS BEFORE '" + cleanTime + "';")
    return mw.returnJson(True, '清理BINLOG成功!')

def getErrorLog():
    args = getArgs()
    filename = getErrorLogsFile()
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


def getMdb8Ver():
    return ['8.0','8.1','8.2','8.3','8.4']

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
        cmd = 'cd ' + serverdir + ' && ./scripts/mysql_install_db --defaults-file=' + myconf
        mw.execShell(cmd)
        return False
    return True


def initMysql57Data():
    '''
    cd /www/server/mysql && /www/server/mysql/bin/mysqld --defaults-file=/www/server/mysql/etc/my.cnf  --initialize-insecure --explicit_defaults_for_timestamp
    '''
    datadir = getDataDir()
    if not os.path.exists(datadir + '/mysql'):
        serverdir = getServerDir()
        myconf = serverdir + "/etc/my.cnf"
        user = pGetDbUser()
        cmd = 'cd ' + serverdir + ' && ./bin/mysqld --defaults-file=' + myconf + \
            ' --initialize-insecure --explicit_defaults_for_timestamp --user=mysql'
        data = mw.execShell(cmd)
        # print(data)
        return False
    return True


def initMysql8Data():
    datadir = getDataDir()
    if not os.path.exists(datadir + '/mysql'):
        serverdir = getServerDir()
        user = pGetDbUser()
        # cmd = 'cd ' + serverdir + ' && ./bin/mysqld --basedir=' + serverdir + ' --datadir=' + \
        #     datadir + ' --initialize'

        cmd = 'cd ' + serverdir + ' && ./bin/mysqld --basedir=' + serverdir + ' --datadir=' + \
            datadir + ' --initialize-insecure'

        # print(cmd)
        data = mw.execShell(cmd)
        # print(data)
        return False
    return True


def initMysqlPwd():
    time.sleep(5)

    serverdir = getServerDir()
    myconf = serverdir + "/etc/my.cnf"
    pwd = mw.getRandomString(16)

    cmd_pass = serverdir + '/bin/mysql --defaults-file=' + myconf + ' -uroot -e'
    cmd_pass = cmd_pass + \
        '"UPDATE mysql.user SET password=PASSWORD(\'' + \
        pwd + "') WHERE user='root';"
    cmd_pass = cmd_pass + 'flush privileges;"'
    data = mw.execShell(cmd_pass)
    # print(cmd_pass)
    # print(data)

    # 删除空账户
    drop_empty_user = serverdir + '/bin/mysql -uroot -p' + \
        pwd + ' -e "use mysql;delete from user where USER=\'\'"'
    mw.execShell(drop_empty_user)

    # 删除测试数据库
    drop_test_db = serverdir + '/bin/mysql -uroot -p' + \
        pwd + ' -e "drop database test";'
    mw.execShell(drop_test_db)

    # 删除冗余账户
    hostname = mw.execShell('hostname')[0].strip()
    if hostname != 'localhost':
        drop_hostname =  serverdir + '/bin/mysql  --defaults-file=' + \
            myconf + ' -uroot -p"' + pwd + '" -e "drop user \'\'@\'' + hostname + '\'";'
        mw.execShell(drop_hostname)

        drop_root_hostname =  serverdir + '/bin/mysql  --defaults-file=' + \
            myconf + ' -uroot -p"' + pwd + '" -e "drop user \'root\'@\'' + hostname + '\'";'
        mw.execShell(drop_root_hostname)

    pSqliteDb('config').where('id=?', (1,)).save('mysql_root', (pwd,))
    return True

def initMysql8Pwd():
    time.sleep(8)


    auth_policy = getAuthPolicy()

    serverdir = getServerDir()
    myconf = serverdir + "/etc/my.cnf"

    pwd = mw.getRandomString(16)

    alter_root_pwd = 'flush privileges;'

    alter_root_pwd = alter_root_pwd + \
        "UPDATE mysql.user SET authentication_string='' WHERE user='root';"
    alter_root_pwd = alter_root_pwd + "flush privileges;"
    alter_root_pwd = alter_root_pwd + \
        "alter user 'root'@'localhost' IDENTIFIED by '" + pwd + "';"
    alter_root_pwd = alter_root_pwd + \
        "alter user 'root'@'localhost' IDENTIFIED WITH "+auth_policy+" by '" + pwd + "';"
    alter_root_pwd = alter_root_pwd + "flush privileges;"

    cmd_pass = serverdir + '/bin/mysqladmin --defaults-file=' + \
        myconf + ' -uroot password root'
    data = mw.execShell(cmd_pass)
    # print(cmd_pass)
    # print(data)

    tmp_file = "/tmp/mysql_init_tmp.log"
    mw.writeFile(tmp_file, alter_root_pwd)
    cmd_pass = serverdir + '/bin/mysql --defaults-file=' + \
        myconf + ' -uroot -proot < ' + tmp_file

    data = mw.execShell(cmd_pass)
    os.remove(tmp_file)

    # 删除测试数据库
    drop_test_db = serverdir + '/bin/mysql  --defaults-file=' + \
        myconf + ' -uroot -p"' + pwd + '" -e "drop database test";'
    mw.execShell(drop_test_db)

    pSqliteDb('config').where('id=?', (1,)).save('mysql_root', (pwd,))

    # 删除冗余账户
    hostname = mw.execShell('hostname')[0].strip()
    if hostname != 'localhost':
        drop_hostname =  serverdir + '/bin/mysql  --defaults-file=' + \
            myconf + ' -uroot -p"' + pwd + '" -e "drop user \'\'@\'' + hostname + '\'";'
        mw.execShell(drop_hostname)

        drop_root_hostname =  serverdir + '/bin/mysql  --defaults-file=' + \
            myconf + ' -uroot -p"' + pwd + '" -e "drop user \'root\'@\'' + hostname + '\'";'
        mw.execShell(drop_root_hostname)

    return True


def myOp(version, method):
    # import commands
    init_file = initDreplace(version)
    current_os = mw.getOs()
    try:
        isInited = initMysqlData()
        if not isInited:

            if not mw.isSupportSystemctl():
                mw.execShell('service ' + getPluginName() + ' start')
            else:
                mw.execShell('systemctl start mysql')

            initMysqlPwd()

            if not mw.isSupportSystemctl():
                mw.execShell('service ' + getPluginName() + ' stop')
            else:
                mw.execShell('systemctl stop mysql')

        if not mw.isSupportSystemctl():
            mw.execShell('service ' + getPluginName() + ' ' + method)
        else:
            mw.execShell('systemctl ' + method + ' mysql')
        return 'ok'
    except Exception as e:
        return str(e)


def my8cmd(version, method):
    # mysql 8.0  and 5.7
    init_file = initDreplace(version)
    cmd = init_file + ' ' + method
    mdb8 = getMdb8Ver()
    try:
        isInited = True
        if mw.inArray(mdb8, version):
            isInited = initMysql8Data()
        else:
            isInited = initMysql57Data()

        if not isInited:

            if not mw.isSupportSystemctl():
                cmd_init_start = init_file + ' start'
                subprocess.Popen(cmd_init_start, stdout=subprocess.PIPE, shell=True,
                                 bufsize=4096, stderr=subprocess.PIPE)

                time.sleep(6)
            else:
                mw.execShell('systemctl start mysql')

            for x in range(10):
                mydb_status = process_status()
                if mydb_status == 'start':
                    initMysql8Pwd()
                    break
                time.sleep(1)

            if not mw.isSupportSystemctl():
                cmd_init_stop = init_file + ' stop'
                subprocess.Popen(cmd_init_stop, stdout=subprocess.PIPE, shell=True,
                                 bufsize=4096, stderr=subprocess.PIPE)
                time.sleep(3)
            else:
                mw.execShell('systemctl stop mysql')

        if not mw.isSupportSystemctl():
            sub = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True,
                                   bufsize=4096, stderr=subprocess.PIPE)
            sub.wait(5)
        else:
            mw.execShell('systemctl ' + method + ' mysql')
        return 'ok'
    except Exception as e:
        return str(e)


def appCMD(version, action):
    makeInitRsaKey(version)
    mdb8 = getMdb8Ver()
    mdb8.append('5.7')
    # print(mdb8)
    if mw.inArray(mdb8, version):
        status = my8cmd(version, action)
    else:
        status = myOp(version, action)
    return status


def start(version=''):
    return appCMD(version, 'start')


def stop(version=''):
    return appCMD(version, 'stop')


def restart(version=''):
    return appCMD(version, 'restart')


def reload(version=''):
    return appCMD(version, 'reload')


def initdStatus():
    current_os = mw.getOs()
    if current_os == 'darwin':
        return "Apple Computer does not support"

    if current_os.startswith('freebsd'):
        initd_bin = getInitDFile()
        if os.path.exists(initd_bin):
            return 'ok'

    shell_cmd = 'systemctl status mysql | grep loaded | grep "enabled;"'
    data = mw.execShell(shell_cmd)
    if data[0] == '':
        return 'fail'
    return 'ok'


def initdInstall():
    current_os = mw.getOs()
    if current_os == 'darwin':
        return "Apple Computer does not support"

    if current_os.startswith('freebsd'):
        import shutil
        source_bin = initDreplace()
        initd_bin = getInitDFile()
        shutil.copyfile(source_bin, initd_bin)
        mw.execShell('chmod +x ' + initd_bin)
        mw.execShell('sysrc ' + getPluginName() + '_enable="YES"')
        return 'ok'

    mw.execShell('systemctl enable mysql')
    return 'ok'


def initdUinstall():
    current_os = mw.getOs()
    if current_os == 'darwin':
        return "Apple Computer does not support"

    if current_os.startswith('freebsd'):
        initd_bin = getInitDFile()
        os.remove(initd_bin)
        mw.execShell('sysrc ' + getPluginName() + '_enable="NO"')
        return 'ok'

    mw.execShell('systemctl disable mysql')
    return 'ok'


def getMyDbPos():
    file = getConf()
    content = mw.readFile(file)
    rep = 'datadir\s*=\s*(.*)'
    tmp = re.search(rep, content)
    return tmp.groups()[0].strip()


def setMyDbPos(version):
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
    stop(version)
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
    start(version)

    result = mw.execShell('ps aux|grep mysqld| grep -v grep|grep -v python')
    if len(result[0]) > 10:
        mw.writeFile('data/datadir.pl', t_datadir)
        return mw.returnJson(True, '存储目录迁移成功!')
    else:
        mw.execShell('pkill -9 mysqld')
        mw.writeFile(myfile, mw.readFile(path + '/etc/my_backup.cnf'))
        start(version)
        return mw.returnJson(False, '文件迁移失败!')


def getMyPort():
    file = getConf()
    content = mw.readFile(file)
    rep = 'port\s*=\s*(.*)'
    tmp = re.search(rep, content)
    return tmp.groups()[0].strip()


def setMyPort(version):
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
    restart(version)
    return mw.returnJson(True, '编辑成功!')


def runInfo(version):

    if status(version) == 'stop':
        return mw.returnJson(False, 'MySQL未启动', [])

    db = pMysqlDb()
    data = db.query('show global status')
    isError = isSqlError(data)
    if isError != None:
        return isError

    gets = ['Max_used_connections', 'Com_commit', 'Com_select', 'Com_rollback', 'Questions', 'Innodb_buffer_pool_reads', 'Innodb_buffer_pool_read_requests', 'Key_reads', 'Key_read_requests', 'Key_writes',
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


def myDbStatus(version):
    if status(version) == 'stop':
        return mw.returnJson(False, 'MySQL未启动', [])

    result = {}
    db = pMysqlDb()
    data = db.query('show variables')
    isError = isSqlError(data)
    if isError != None:
        return isError

    gets = ['table_open_cache', 'thread_cache_size', 'key_buffer_size', 'tmp_table_size', 'max_heap_table_size', 'innodb_buffer_pool_size',
            'innodb_additional_mem_pool_size', 'innodb_log_buffer_size', 'max_connections', 'sort_buffer_size', 'read_buffer_size', 'read_rnd_buffer_size', 'join_buffer_size', 'thread_stack', 'binlog_cache_size']

    if version != "8.0":
        gets.append('query_cache_size')

    result['mem'] = {}
    for d in data:
        vname = d['Variable_name']
        for g in gets:
            # print(g)
            if vname == g:
                result['mem'][g] = d["Value"]
    return mw.getJson(result)


def setDbStatus(version):
    gets = ['key_buffer_size', 'tmp_table_size', 'max_heap_table_size', 'innodb_buffer_pool_size', 'innodb_log_buffer_size', 'max_connections',
            'table_open_cache', 'thread_cache_size', 'sort_buffer_size', 'read_buffer_size', 'read_rnd_buffer_size', 'join_buffer_size', 'thread_stack', 'binlog_cache_size']

    if version != "8.0":
        # gets.append('query_cache_size')
        gets = ['key_buffer_size', 'query_cache_size', 'tmp_table_size', 'max_heap_table_size', 'innodb_buffer_pool_size', 'innodb_log_buffer_size', 'max_connections',
                'table_open_cache', 'thread_cache_size', 'sort_buffer_size', 'read_buffer_size', 'read_rnd_buffer_size', 'join_buffer_size', 'thread_stack', 'binlog_cache_size']

    # print(gets)
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
        return mw.returnJson(False, '数据库密码错误,在管理列表-点击【修复】!')
    if "1045," in mysqlMsg:
        return mw.returnJson(False, '连接错误!')
    if "SQL syntax" in mysqlMsg:
        return mw.returnJson(False, 'SQL语法错误!')
    if "Connection refused" in mysqlMsg:
        return mw.returnJson(False, '数据库连接失败,请检查数据库服务是否启动!')
    if "1133," in mysqlMsg:
        return mw.returnJson(False, '数据库用户不存在!')
    if "1007," in mysqlMsg:
        return mw.returnJson(False, '数据库已经存在!')
    return None


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

    scDir = mw.getRunDir() + '/scripts/backup.py'
    cmd = 'python3 ' + scDir + ' database ' + args['name'] + ' 3'
    os.system(cmd)
    return mw.returnJson(True, 'ok')


# 数据库密码处理
def myPass(act, root):
    conf_file = getConf()
    mw.execShell("sed -i '/user=root/d' {}".format(conf_file))
    mw.execShell("sed -i '/password=/d' {}".format(conf_file))
    if act:
        mycnf = mw.readFile(conf_file)
        src_dump = "[mysqldump]\n"
        sub_dump = src_dump + "user=root\npassword=\"{}\"\n".format(root)
        if not mycnf:
            return False
        mycnf = mycnf.replace(src_dump, sub_dump)
        if len(mycnf) > 100:
            mw.writeFile(conf_file, mycnf)
        return True
    return True


def rootPwd():
    return pSqliteDb('config').where(
        'id=?', (1,)).getField('mysql_root')


def importDbExternal():
    args = getArgs()
    data = checkArgs(args, ['file', 'name'])
    if not data[0]:
        return data[1]

    file = args['file']
    name = args['name']

    import_dir = mw.getRootDir() + '/backup/import/'

    file_path = import_dir + file
    if not os.path.exists(file_path):
        return mw.returnJson(False, '文件突然消失?')

    exts = ['sql', 'gz', 'zip']
    ext = mw.getFileSuffix(file)
    if ext not in exts:
        return mw.returnJson(False, '导入数据库格式不对!')

    tmp = file.split('/')
    tmpFile = tmp[len(tmp) - 1]
    tmpFile = tmpFile.replace('.sql.' + ext, '.sql')
    tmpFile = tmpFile.replace('.' + ext, '.sql')
    tmpFile = tmpFile.replace('tar.', '')

    # print(tmpFile)
    import_sql = ""
    if file.find("sql.gz") > -1:
        cmd = 'cd ' + import_dir + ' && gzip -dc ' + \
            file + " > " + import_dir + tmpFile
        info = mw.execShell(cmd)
        if info[1] == "":
            import_sql = import_dir + tmpFile

    if file.find(".zip") > -1:
        cmd = 'cd ' + import_dir + ' && unzip -o ' + file
        mw.execShell(cmd)
        import_sql = import_dir + tmpFile

    if file.find("tar.gz") > -1:
        cmd = 'cd ' + import_dir + ' && tar -zxvf ' + file
        mw.execShell(cmd)
        import_sql = import_dir + tmpFile

    if file.find(".sql") > -1 and file.find(".sql.gz") == -1:
        import_sql = import_dir + file

    if import_sql == "":
        return mw.returnJson(False, '未找SQL文件')

    pwd = pSqliteDb('config').where('id=?', (1,)).getField('mysql_root')
    sock = getSocketFile()

    my_cnf = getConf()

    myPass(True, pwd)
    mysql_cmd = getServerDir() + '/bin/mysql --defaults-file=' + my_cnf + \
        ' -uroot -p"' + pwd + '" -f ' + name + ' < ' + import_sql

    # print(mysql_cmd)
    rdata = mw.execShell(mysql_cmd)
    myPass(False, pwd)
    # print(rdata)
    if ext != 'sql':
        os.remove(import_sql)

    if rdata[1].lower().find('error') > -1:
        return mw.returnJson(False, rdata[1])

    return mw.returnJson(True, 'ok')

def importDbExternalProgress():
    args = getArgs()
    data = checkArgs(args, ['file', 'name'])
    if not data[0]:
        return data[1]

    file = args['file']
    name = args['name']

    cmd = 'cd '+mw.getServerDir()+'/mdserver-web && source bin/activate && '
    cmd += 'python3 '+mw.getServerDir()+'/mdserver-web/plugins/mysql/index.py import_db_external_progress_bar  {"file":"'+file+'","name":"'+name+'"}'
    return mw.returnJson(True, 'ok',cmd)

def importDbExternalProgressBar():
    args = getArgs()
    data = checkArgs(args, ['file', 'name'])
    if not data[0]:
        return data[1]

    file = args['file']
    name = args['name']

    import_dir = mw.getRootDir() + '/backup/import/'

    file_path = import_dir + file
    if not os.path.exists(file_path):
        return mw.returnJson(False, '文件突然消失?')

    exts = ['sql', 'gz', 'zip']
    ext = mw.getFileSuffix(file)
    if ext not in exts:
        return mw.returnJson(False, '导入数据库格式不对!')

    tmp = file.split('/')
    tmpFile = tmp[len(tmp) - 1]
    tmpFile = tmpFile.replace('.sql.' + ext, '.sql')
    tmpFile = tmpFile.replace('.' + ext, '.sql')
    tmpFile = tmpFile.replace('tar.', '')

    # print(tmpFile)
    import_sql = ""
    if file.find("sql.gz") > -1:
        cmd = 'cd ' + import_dir + ' && gzip -dc ' + \
            file + " > " + import_dir + tmpFile
        info = mw.execShell(cmd)
        if info[1] == "":
            import_sql = import_dir + tmpFile

    if file.find(".zip") > -1:
        cmd = 'cd ' + import_dir + ' && unzip -o ' + file
        mw.execShell(cmd)
        import_sql = import_dir + tmpFile

    if file.find("tar.gz") > -1:
        cmd = 'cd ' + import_dir + ' && tar -zxvf ' + file
        mw.execShell(cmd)
        import_sql = import_dir + tmpFile

    if file.find(".sql") > -1 and file.find(".sql.gz") == -1:
        import_sql = import_dir + file

    if import_sql == "":
        return mw.returnJson(False, '未找SQL文件')

    pwd = pSqliteDb('config').where('id=?', (1,)).getField('mysql_root')
    sock = getSocketFile()

    my_cnf = getConf()
    mysql_cmd = getServerDir() + '/bin/mysql --defaults-file=' + my_cnf + \
        ' -uroot -p"' + pwd + '" -f ' + name
    mysql_cmd_progress_bar = "pv -t -p " + import_sql + '|'+ mysql_cmd
    print(mysql_cmd_progress_bar)
    rdata = os.system(mysql_cmd_progress_bar)
    return ""


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

    local_mode = recognizeDbMode()
    if local_mode == 'gtid':
        pdb = pMysqlDb()
        pdb.execute('reset master')

    pwd = pSqliteDb('config').where('id=?', (1,)).getField('mysql_root')
    sock = getSocketFile()
    mysql_cmd = getServerDir() + '/bin/mysql -S ' + sock + ' -uroot -p"' + pwd + \
        '" ' + name + ' < ' + file_path_sql

    # print(mysql_cmd)
    # os.system(mysql_cmd)

    rdata = mw.execShell(mysql_cmd)
    if rdata[1].lower().find('error') > -1:
        return mw.returnJson(False, rdata[1])

    return mw.returnJson(True, 'ok')


def importDbBackupProgress():
    args = getArgs()
    data = checkArgs(args, ['file', 'name'])
    if not data[0]:
        return data[1]

    file = args['file']
    name = args['name']

    cmd = 'cd '+mw.getServerDir()+'/mdserver-web && source bin/activate && '
    cmd += 'python3 '+mw.getServerDir()+'/mdserver-web/plugins/mysql/index.py import_db_backup_progress_bar  {"file":"'+file+'","name":"'+name+'"}'
    return mw.returnJson(True, 'ok',cmd)

    return mw.returnJson(True, 'ok')

def importDbBackupProgressBar():
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

    local_mode = recognizeDbMode()
    if local_mode == 'gtid':
        pdb = pMysqlDb()
        pdb.execute('reset master')

    pwd = pSqliteDb('config').where('id=?', (1,)).getField('mysql_root')
    sock = getSocketFile()

    mysql_cmd = getServerDir() + '/bin/mysql -S ' + sock + ' -uroot -p"' + pwd + \
        '" ' + name
    mysql_cmd_progress_bar = "pv -t -p " + file_path_sql + '|'+ mysql_cmd
    print(mysql_cmd_progress_bar)
    rdata = os.system(mysql_cmd_progress_bar)
    return ''


def deleteDbBackup():
    args = getArgs()
    data = checkArgs(args, ['filename', 'path'])
    if not data[0]:
        return data[1]

    path = args['path']
    full_file = ""
    bkDir = mw.getRootDir() + '/backup/database'
    full_file = bkDir + '/' + args['filename']
    if path != "":
        full_file = path + "/" + args['filename']
    os.remove(full_file)
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


def getDbBackupImportList():

    bkImportDir = mw.getRootDir() + '/backup/import'
    if not os.path.exists(bkImportDir):
        os.mkdir(bkImportDir)

    blist = os.listdir(bkImportDir)

    rr = []
    for x in range(0, len(blist)):
        name = blist[x]
        p = bkImportDir + '/' + name
        data = {}
        data['name'] = name

        rsize = os.path.getsize(p)
        data['size'] = mw.toSize(rsize)

        t = os.path.getctime(p)
        t = time.localtime(t)

        data['time'] = time.strftime('%Y-%m-%d %H:%M:%S', t)
        rr.append(data)

        data['file'] = p

    rdata = {
        "list": rr,
        "upload_dir": bkImportDir,
    }
    return mw.returnJson(True, 'ok', rdata)


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

        ps = vdb_name
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

    #强制修改
    force = 0
    if 'force' in args and args['force'] == '1':
        force = 1

    password = args['password']
    try:
        pdb = pMysqlDb()
        result = pdb.query("show databases")
        isError = isSqlError(result)
        if isError != None:
            if force == 1:
                pSqliteDb('config').where('id=?', (1,)).save('mysql_root', (password,))
                return mw.returnJson(True, '【强制修改】数据库root密码修改成功(不意为成功连接数据)!')
            return isError

        if version.find('5.7') > -1 or version.find('8.0') > -1:
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

        msg = ''
        if force == 1:
            msg = ',无须强制!'

        return mw.returnJson(True, '数据库root密码修改成功!'+msg)
    except Exception as ex:
        return mw.returnJson(False, '修改错误:' + str(ex))


def setUserPwd(version=''):
    args = getArgs()
    data = checkArgs(args, ['password', 'name'])
    if not data[0]:
        return data[1]

    newpassword = args['password']
    username = args['name']
    uid = args['id']
    try:
        pdb = pMysqlDb()
        psdb = pSqliteDb('databases')
        name = psdb.where('id=?', (uid,)).getField('name')

        if version.find('5.7') > -1 or version.find('8.0') > -1:
            accept = pdb.query(
                "select Host from mysql.user where User='" + name + "' AND Host!='localhost'")
            t1 = pdb.execute(
                "update mysql.user set authentication_string='' where User='" + username + "'")
            # print(t1)
            result = pdb.execute(
                "ALTER USER `%s`@`localhost` IDENTIFIED BY '%s'" % (username, newpassword))
            # print(result)
            for my_host in accept:
                t2 = pdb.execute("ALTER USER `%s`@`%s` IDENTIFIED BY '%s'" % (
                    username, my_host["Host"], newpassword))
                # print(t2)
        else:
            result = pdb.execute("update mysql.user set Password=password('" +
                                 newpassword + "') where User='" + username + "'")

        pdb.execute("flush privileges")
        psdb.where("id=?", (uid,)).setField('password', newpassword)
        return mw.returnJson(True, mw.getInfo('修改数据库[{1}]密码成功!', (name,)))
    except Exception as ex:
        return mw.returnJson(False, mw.getInfo('修改数据库[{1}]密码失败[{2}]!', (name, str(ex),)))


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

    reg = "^[\w-]+$"
    if not re.match(reg, args['name']):
        return mw.returnJson(False, '数据库名称不能带有特殊符号!')
    checks = ['root', 'mysql', 'test', 'sys', 'performance_schema','information_schema']
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
        sid = args['id']
        name = args['name']
        psdb = pSqliteDb('databases')
        pdb = pMysqlDb()
        find = psdb.where("id=?", (sid,)).field(
            'id,pid,name,username,password,accept,ps,addtime').find()
        accept = find['accept']
        username = find['username']

        # 删除MYSQL
        result = pdb.execute("drop database `" + name + "`")

        users = pdb.query("select Host from mysql.user where User='" +
                          username + "' AND Host!='localhost'")
        pdb.execute("drop user '" + username + "'@'localhost'")
        for us in users:
            pdb.execute("drop user '" + username + "'@'" + us["Host"] + "'")
        pdb.execute("flush privileges")

        # 删除SQLITE
        psdb.where("id=?", (sid,)).delete()
        return mw.returnJson(True, '删除成功!')
    except Exception as ex:
        return mw.returnJson(False, '删除失败!' + str(ex))


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
    pdb = pMysqlDb()
    psdb = pSqliteDb('databases')

    dbname = psdb.where('username=?', (name,)).getField('name')

    if name == 'root':
        password = pSqliteDb('config').where(
            'id=?', (1,)).getField('mysql_root')
    else:
        password = psdb.where("username=?", (name,)).getField('password')

    users = pdb.query("select Host from mysql.user where User='" +
                      name + "' AND Host!='localhost'")

    for us in users:
        pdb.execute("drop user '" + name + "'@'" + us["Host"] + "'")

    __createUser(dbname, name, password, access)

    psdb.where('username=?', (name,)).save('accept,rw', (access, 'rw',))
    return mw.returnJson(True, '设置成功!')


def openSkipGrantTables():
    mycnf = getConf()
    content = mw.readFile(mycnf)
    content = content.replace('#skip-grant-tables','skip-grant-tables')
    mw.writeFile(mycnf, content)
    return True

def closeSkipGrantTables():
    mycnf = getConf()
    content = mw.readFile(mycnf)
    content = content.replace('skip-grant-tables','#skip-grant-tables')
    mw.writeFile(mycnf, content)
    return True


def resetDbRootPwd(version):
    serverdir = getServerDir()
    myconf = serverdir + "/etc/my.cnf"
    pwd = mw.getRandomString(16)

    pSqliteDb('config').where('id=?', (1,)).save('mysql_root', (pwd,))

    mdb8 = getMdb8Ver()
    if not mw.inArray(mdb8, version):
        cmd_pass = serverdir + '/bin/mysql --defaults-file=' + myconf + ' -uroot -e'
        cmd_pass = cmd_pass + '"UPDATE mysql.user SET password=PASSWORD(\'' + pwd + "') WHERE user='root';"
        cmd_pass = cmd_pass + 'flush privileges;"'
        data = mw.execShell(cmd_pass)
        # print(data)
    else:
        auth_policy = getAuthPolicy()

        reset_pwd = 'flush privileges;'
        reset_pwd = reset_pwd + \
            "UPDATE mysql.user SET authentication_string='' WHERE user='root';"
        reset_pwd = reset_pwd + "flush privileges;"
        reset_pwd = reset_pwd + \
            "alter user 'root'@'localhost' IDENTIFIED by '" + pwd + "';"
        reset_pwd = reset_pwd + \
            "alter user 'root'@'localhost' IDENTIFIED WITH "+auth_policy+" by '" + pwd + "';"
        reset_pwd = reset_pwd + "flush privileges;"

        tmp_file = "/tmp/mysql_init_tmp.log"
        mw.writeFile(tmp_file, reset_pwd)
        cmd_pass = serverdir + '/bin/mysql --defaults-file=' + myconf + ' -uroot -proot < ' + tmp_file

        data = mw.execShell(cmd_pass)
        # print(data)
        os.remove(tmp_file)
    return True

def fixDbAccess(version):

    pdb = pMysqlDb()
    mdb_ddir = getDataDir()
    if not os.path.exists(mdb_ddir):
        return mw.returnJson(False, '数据目录不存在,尝试重启重建!')

    try:
        data = pdb.query('show databases')
        isError = isSqlError(data)
        if isError != None:
       
            # 重置密码
            appCMD(version, 'stop')
            openSkipGrantTables()
            appCMD(version, 'start')
            time.sleep(3)
            resetDbRootPwd(version)

            appCMD(version, 'stop')
            closeSkipGrantTables()
            appCMD(version, 'start')

            return mw.returnJson(True, '修复成功!')
        return mw.returnJson(True, '正常无需修复!')
    except Exception as e:
        return mw.returnJson(False, '修复失败请重试!')


def setDbRw(version=''):
    args = getArgs()
    data = checkArgs(args, ['username', 'id', 'rw'])
    if not data[0]:
        return data[1]

    username = args['username']
    uid = args['id']
    rw = args['rw']

    pdb = pMysqlDb()
    psdb = pSqliteDb('databases')
    dbname = psdb.where("id=?", (uid,)).getField('name')
    users = pdb.query(
        "select Host from mysql.user where User='" + username + "'")

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
    users = pdb.query("select Host from mysql.user where User='" +
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


def resetMaster(version=''):
    pdb = pMysqlDb()
    r = pdb.execute('reset master')
    isError = isSqlError(r)
    if isError != None:
        return isError
    return mw.returnJson(True, '重置成功!')


def getMasterDbList(version=''):
    try:
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
    except Exception as e:
        return mw.returnJson(False, "数据库密码错误,在管理列表-点击【修复】!")


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

    query_status_cmd = 'show slave status'
    is_mdb8 = False
    mdb8 = getMdb8Ver()
    if mw.inArray(mdb8, version):
        is_mdb8 = True
        query_status_cmd = 'show replica status'

    try:
        
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
        data['slave_status'] = False

        db = pMysqlDb()
        dlist = db.query(query_status_cmd)

        for v in dlist:

            if is_mdb8:
                if (v["Replica_IO_Running"] == 'Yes' or v["Replica_SQL_Running"] == 'Yes'):
                    data['slave_status'] = True
            else:
                if (v["Slave_IO_Running"] == 'Yes' or v["Slave_SQL_Running"] == 'Yes'):
                    data['slave_status'] = True

        return mw.returnJson(master_status, '设置成功', data)
    except Exception as e:
        return mw.returnJson(False, "数据库密码错误,在管理列表-点击【修复】,"+str(e), 'pwd')


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

    reg = "^[\w-]+$"
    if not re.match(reg, username):
        return mw.returnJson(False, '用户名不能带有特殊符号!')
    checks = ['root', 'mysql', 'test', 'sys', 'performance_schema','information_schema']
    if username in checks or len(username) < 1:
        return mw.returnJson(False, '用户名不合法!')
    if password in checks or len(password) < 1:
        return mw.returnJson(False, '密码不合法!')

    if len(password) < 1:
        password = mw.md5(time.time())[0:8]

    pdb = pMysqlDb()
    psdb = pSqliteDb('master_replication_user')

    auth_policy = getAuthPolicy()

    if psdb.where("username=?", (username)).count() > 0:
        return mw.returnJson(False, '用户已存在!')

    mdb8 = getMdb8Ver()
    if mw.inArray(mdb8,version):
        sql = "CREATE USER '" + username + \
            "'  IDENTIFIED WITH "+auth_policy+" BY '" + password + "';"
        pdb.execute(sql)
        sql = "grant replication slave on *.* to '" + username + "'@'%';"
        result = pdb.execute(sql)
        isError = isSqlError(result)
        if isError != None:
            return isError
    else:
        sql = "grant replication SLAVE ON *.* TO  '" + username + \
            "'@'%' identified by '" + password + "';"
        result = pdb.execute(sql)
        isError = isSqlError(result)
        if isError != None:
            return isError

    sql_select = "grant select,reload,REPLICATION CLIENT,PROCESS on *.* to " + username + "@'%';"
    pdb.execute(sql_select)
    pdb.execute('FLUSH PRIVILEGES;')

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

    sid = getDbServerId()
    channel_name = ""
    if sid != '':
        channel_name = " for channel 'r{}'".format(sid)

    mdb8 = getMdb8Ver()
    sql = ''
    if not mw.inArray(mdb8,version):
        base_sql = "CHANGE MASTER TO MASTER_HOST='" + ip + "', MASTER_PORT=" + port + ", MASTER_USER='" + \
                clist[0]['username'] + "', MASTER_PASSWORD='" + clist[0]['password'] + "'"

        sql += base_sql;
        sql += "<br/><hr/>";
        # sql += base_sql + ", MASTER_AUTO_POSITION=1" + channel_name
        sql += base_sql + channel_name
        sql += "<br/><hr/>";

        sql += base_sql + ", MASTER_LOG_FILE='" + mstatus[0]["File"] + "',MASTER_LOG_POS=" + str(mstatus[0]["Position"]) + channel_name
    else:
        base_sql = "CHANGE REPLICATION SOURCE TO SOURCE_HOST='" + ip + "', SOURCE_PORT=" + port + ", SOURCE_USER='" + \
                clist[0]['username']  + "', SOURCE_PASSWORD='" + clist[0]['password']+"'"
        sql += base_sql;
        sql += "<br/><hr/>";
        # sql += base_sql + ", MASTER_AUTO_POSITION=1" + channel_name
        sql += base_sql + channel_name
        sql += "<br/><hr/>";
        sql += base_sql + ", SOURCE_LOG_FILE='" + mstatus[0]["File"] + "',SOURCE_LOG_POS=" + str(mstatus[0]["Position"]) + channel_name


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

    users = pdb.query("select Host from mysql.user where User='" +
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


def getSlaveSyncUserByIp(version=''):
    args = getArgs()
    data = checkArgs(args, ['ip'])
    if not data[0]:
        return data[1]

    ip = args['ip']

    conn = pSqliteDb('slave_sync_user')
    data = conn.field('ip,port,user,pass,mode,cmd').where(
        "ip=?", (ip,)).select()
    return mw.returnJson(True, 'ok', data)


def addSlaveSyncUser(version=''):
    import base64

    args = getArgs()
    data = checkArgs(args, ['ip'])
    if not data[0]:
        return data[1]

    ip = args['ip']
    if ip == "":
        return mw.returnJson(True, 'ok')

    data = checkArgs(args, ['port', 'user', 'pass', 'mode'])
    if not data[0]:
        return data[1]

    cmd = args['cmd']
    port = args['port']
    user = args['user']
    apass = args['pass']
    mode = args['mode']
    addTime = time.strftime('%Y-%m-%d %X', time.localtime())

    conn = pSqliteDb('slave_sync_user')
    data = conn.field('ip').where("ip=?", (ip,)).select()
    if len(data) > 0:
        res = conn.where("ip=?", (ip,)).save(
            'port,user,pass,mode,cmd', (port, user, apass, mode, cmd))
    else:
        conn.add('ip,port,user,cmd,user,pass,mode,addtime',
                 (ip, port, user, cmd, user, apass, mode, addTime))

    return mw.returnJson(True, '设置成功!')


def delSlaveSyncUser(version=''):
    args = getArgs()
    data = checkArgs(args, ['ip'])
    if not data[0]:
        return data[1]

    ip = args['ip']

    conn = pSqliteDb('slave_sync_user')
    conn.where("ip=?", (ip,)).delete()
    return mw.returnJson(True, '删除成功!')


def getSlaveSyncUserList(version=''):
    args = getArgs()
    data = checkArgs(args, ['page', 'page_size'])
    if not data[0]:
        return data[1]

    page = int(args['page'])
    page_size = int(args['page_size'])

    conn = pSqliteDb('slave_sync_user')
    limit = str((page - 1) * page_size) + ',' + str(page_size)

    field = 'id,ip,port,user,pass,cmd,addtime'
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


def getSyncModeFile():
    return getServerDir() + "/sync.mode"


def getSlaveSyncMode(version):
    sync_mode = getSyncModeFile()
    if os.path.exists(sync_mode):
        mode = mw.readFile(sync_mode).strip()
        return mw.returnJson(True, 'ok', mode)
    return mw.returnJson(False, 'fail')


def setSlaveSyncMode(version):
    args = getArgs()
    data = checkArgs(args, ['mode'])
    if not data[0]:
        return data[1]
    mode = args['mode']
    sync_mode = getSyncModeFile()

    if mode == 'none':
        os.remove(sync_mode)
    else:
        mw.writeFile(sync_mode, mode)
    return mw.returnJson(True, '设置成功', mode)


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
    return mw.returnJson(True, '删除SSH成功!')


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

    query_status_cmd = 'show slave status'
    mdb8 = getMdb8Ver()
    if mw.inArray(mdb8, version):
        query_status_cmd = 'show replica status'

    if status(version) == 'stop':
        return mw.returnJson(False, 'MySQL未启动', [])

    db = pMysqlDb()
    dlist = db.query(query_status_cmd)

    # print(dlist)
    data = {}
    data['data'] = dlist
    return mw.getJson(data)


def trySlaveSyncBugfix(version=''):
    if status(version) == 'stop':
        return mw.returnJson(False, 'MySQL未启动', [])

    mode_file = getSyncModeFile()
    if not os.path.exists(mode_file):
        return mw.returnJson(False, '需要先设置同步配置')

    mode = mw.readFile(mode_file)
    if mode != 'sync-user':
        return mw.returnJson(False, '仅支持【同步账户】模式')

    conn = pSqliteDb('slave_sync_user')
    slave_sync_data = conn.field('ip,port,user,pass,mode,cmd').select()
    if len(slave_sync_data) < 1:
        return mw.returnJson(False, '需要先添加【同步用户】配置!')

    # print(slave_sync_data)
    # 本地从库
    sdb = pMysqlDb()

    gtid_purged = ''

    var_slave_gtid = sdb.query('show VARIABLES like "%gtid_purged%"')
    if len(var_slave_gtid) > 0:
            gtid_purged += var_slave_gtid[0]['Value'] + ','

    for i in range(len(slave_sync_data)):
        port = slave_sync_data[i]['port']
        password = slave_sync_data[i]['pass']
        host = slave_sync_data[i]['ip']
        user = slave_sync_data[i]['user']

        # print(port, password, host)

        mdb = mw.getMyORM()
        mdb.setHost(host)
        mdb.setPort(port)
        mdb.setUser(user)
        mdb.setPwd(password)
        mdb.setSocket('')

        var_gtid = mdb.query('show VARIABLES like "%gtid_purged%"')
        if len(var_gtid) > 0:
            gtid_purged += var_gtid[0]['Value'] + ','



    gtid_purged = gtid_purged.strip(',')
    sql = "set @@global.gtid_purged='" + gtid_purged + "'"

    sdb.query('stop slave')
    # print(sql)
    sdb.query(sql)
    sdb.query('start slave')
    return mw.returnJson(True, '修复成功!')


def getSlaveSyncCmd(version=''):
    root = mw.getRunDir()
    cmd = 'cd ' + root + ' && python3 ' + root + \
        '/plugins/mysql/index.py do_full_sync {"db":"all","sign",""}'
    return mw.returnJson(True, 'ok', cmd)


def initSlaveStatus(version=''):
    if status(version) == 'stop':
        return mw.returnJson(False, 'MySQL未启动', [])

    mode_file = getSyncModeFile()
    # print(mode_file)
    if not os.path.exists(mode_file):
        return mw.returnJson(False, '需要先设置同步配置')

    mode = mw.readFile(mode_file)
    if mode == 'ssh':
        return initSlaveStatusSSH(version)
    if mode == 'sync-user':
        return initSlaveStatusSyncUser(version)


def makeSyncUsercmd(u, version=''):
    mode = recognizeDbMode()
    sql = ''

    ip = u['ip']
    port = u['port']
    username = u['user']
    password = u['pass']
    if mode == "gtid":
        sql = "CHANGE MASTER TO MASTER_HOST='" + ip + "', MASTER_PORT=" + port + ", MASTER_USER='" + \
            username + "', MASTER_PASSWORD='" + \
            password + "', MASTER_AUTO_POSITION=1"
        if version == '8.0':
            sql = "CHANGE REPLICATION SOURCE TO SOURCE_HOST='" + ip  + "', SOURCE_PORT=" + port + ", SOURCE_USER='" + \
                username  + "', SOURCE_PASSWORD='" + \
                password + "', MASTER_AUTO_POSITION=1"
    return sql


def parseSlaveSyncCmd(cmd):
    a = {}
    if cmd.lower().find('for') > 0:
        cmd_tmp = cmd.split('for')
        cmd = cmd_tmp[0].strip()

        pattern_c = r"channel \'(.*)\';"
        match_val = re.match(pattern_c, cmd_tmp[1].strip(), re.I)
        if match_val:
            m_groups = match_val.groups()
            a['channel'] = m_groups[0]
    vlist = cmd.split(',')
    for i in vlist:
        tmp = i.strip()
        tmp_a = tmp.split(" ")
        real_tmp = tmp_a[len(tmp_a) - 1]
        kv = real_tmp.split("=")
        a[kv[0]] = kv[1].replace("'", '').replace("'", '').replace(";", '')
    return a


def initSlaveStatusSyncUser(version=''):
    conn = pSqliteDb('slave_sync_user')
    slave_data = conn.field('ip,port,user,pass,mode,cmd').select()
    if len(slave_data) < 1:
        return mw.returnJson(False, '需要先添加同步用户配置!')

    # print(data)
    pdb = pMysqlDb()
    if len(slave_data) == 1:
        dlist = pdb.query('show slave status')
        if len(dlist) > 0:
            return mw.returnJson(False, '已经初始化好了zz...')

    msg = ''
    local_mode = recognizeDbMode()
    for x in range(len(slave_data)):
        slave_t = slave_data[x]
        mode_name = 'classic'
        base_t = 'IP:' + slave_t['ip'] + ",PORT:" + \
            slave_t['port'] + ",USER:" + slave_t['user']

        if slave_t['mode'] == '1':
            mode_name = 'gtid'
        # print(local_mode, mode_name)
        if local_mode != mode_name:
            msg += base_t + '->同步模式不一致'
            continue

        cmd_sql = slave_t['cmd']
        if cmd_sql == '':
            msg += base_t + '->同步命令不能为空'
            continue

        try:
            pinfo = parseSlaveSyncCmd(cmd_sql)
        except Exception as e:
            return mw.returnJson(False, base_t + '->CMD同步命令不合规范!')
        # print(cmd_sql)
        t = pdb.query(cmd_sql)
        # print(t)
        isError = isSqlError(t)
        if isError:
            return isError

        # pdb.query("start slave user='{}' password='{}';".format(
        #     u['user'], u['pass']))

    pdb.query("start slave")
    pdb.query("start all slaves")

    if msg == '':
        msg = '初始化成功!'
    return mw.returnJson(True, msg)


def initSlaveStatusSSH(version=''):
    db = pMysqlDb()
    dlist = db.query('show slave status')

    conn = pSqliteDb('slave_id_rsa')
    ssh_list = conn.field('ip,port,id_rsa,db_user').select()

    if len(ssh_list) < 1:
        return mw.returnJson(False, '需要先配置【[主]SSH配置】!')

    local_mode = recognizeDbMode()

    import paramiko
    paramiko.util.log_to_file('paramiko.log')
    ssh = paramiko.SSHClient()

    db.query('stop slave')
    db.query('reset slave all')
    for data in ssh_list:
        ip = data['ip']
        SSH_PRIVATE_KEY = "/tmp/t_ssh_" + ip + ".txt"
        master_port = data['port']
        mw.writeFile(SSH_PRIVATE_KEY, data['id_rsa'].replace('\\n', '\n'))
        mw.execShell("chmod 600 " + SSH_PRIVATE_KEY)
        try:
            key = paramiko.RSAKey.from_private_key_file(SSH_PRIVATE_KEY)
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=ip, port=int(master_port),
                        username='root', pkey=key)

            db_user = data['db_user']
            cmd = 'cd /www/server/mdserver-web && source bin/activate && python3 ' + \
                getSPluginDir() + \
                '/index.py get_master_rep_slave_user_cmd {"username":"' + \
                db_user + '","db":""}'
            stdin, stdout, stderr = ssh.exec_command(cmd)
            result = stdout.read()
            result = result.decode('utf-8')
            if result.strip() == "":
                return mw.returnJson(False, '[主][' + ip + ']:获取同步命令失败!')

            cmd_data = json.loads(result)
            if not cmd_data['status']:
                return mw.returnJson(False, '[主][' + ip + ']:' + cmd_data['msg'])

            if local_mode != cmd_data['data']['mode']:
                return mw.returnJson(False, '[主][' + ip + ']:【{}】从【{}】,运行模式不一致!'.format(cmd_data['data']['mode'], local_mode))

            u = cmd_data['data']['info']

            ps = u['username'] + "|" + u['password']
            print(ps)
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
            db.query(cmd)
            ssh.close()
            if os.path.exists(SSH_PRIVATE_KEY):
                os.system("rm -rf " + SSH_PRIVATE_KEY)
        except Exception as e:
            return mw.returnJson(False, '[主][' + ip + ']:SSH认证配置连接失败!' + str(e))
    db.query('start slave')
    return mw.returnJson(True, '初始化成功!')


def setSlaveStatus(version=''):
    mode_file = getSyncModeFile()
    if not os.path.exists(mode_file):
        return mw.returnJson(False, '需要先设置同步配置')

    mode = mw.readFile(mode_file)
    pdb = pMysqlDb()
    dlist = pdb.query('show slave status')
    if len(dlist) == 0:
        return mw.returnJson(False, '需要手动添加同步账户或者执行初始化!')

    for v in dlist:
        connection_name = ''
        cmd = "slave"
        if 'Channel_Name' in v:
            ch_name = v['Channel_Name']
            cmd = "slave for channel '{}'".format(ch_name)

        if (v["Slave_IO_Running"] == 'Yes' or v["Slave_SQL_Running"] == 'Yes'):
            pdb.query("stop {}".format(cmd))
        else:
            pdb.query("start {}".format(cmd))

    return mw.returnJson(True, '设置成功!')

def deleteSlaveFunc(sign = ''):
    db = pMysqlDb()
    if sign !=  '':
        db.query("stop slave for channel '{}'".format(sign))
        db.query("reset slave all for channel '{}'".format(sign))
    else:
        db.query('stop slave')
        db.query('reset slave all')

def deleteSlave(version=''):
    args = getArgs()
    sign = ''
    if 'sign' in args:
        sign = args['sign']
    deleteSlaveFunc(sign)
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
            pwd + " --force --databases " + \
            ' '.join(dlist) + " | gzip > /tmp/dump.sql.gz"
    else:
        cmd = mysql_dir + "/bin/mysqldump --defaults-file=" + myconf + " " + option + " -uroot -p" + \
            pwd + " --force --databases " + \
            args['db'] + " | gzip > /tmp/dump.sql.gz"

    ret = mw.execShell(cmd)
    if ret[0] == '':
        return 'ok'
    return 'fail'


############### --- 重要 数据补足同步 ---- ###########

def getSyncMysqlDB(dbname,sign = ''):
    conn = pSqliteDb('slave_sync_user')
    if sign != '':
        data = conn.field('ip,port,user,pass,mode,cmd').where('ip=?', (sign,)).find()
    else:
        data = conn.field('ip,port,user,pass,mode,cmd').find()
    user = data['user']
    apass = data['pass']
    port = data['port']
    ip = data['ip']
    # 远程数据
    sync_db = mw.getMyORM()
    # MySQLdb |
    sync_db.setPort(port)
    sync_db.setHost(ip)
    sync_db.setUser(user)
    sync_db.setPwd(apass)
    sync_db.setDbName(dbname)
    sync_db.setTimeout(60)
    return sync_db

def syncDatabaseRepairTempFile():
    tmp_log = mw.getMWLogs()+ '/mysql-check.log'
    return tmp_log

def syncDatabaseRepairLog(version=''):
    import subprocess
    args = getArgs()
    data = checkArgs(args, ['db','sign','op'])
    if not data[0]:
        return data[1]

    sync_args_db = args['db']
    sync_args_sign = args['sign']
    op = args['op']
    tmp_log = syncDatabaseRepairTempFile()
    cmd = 'cd '+mw.getServerDir()+'/mdserver-web && source bin/activate && python3 plugins/mysql/index.py sync_database_repair  {"db":"'+sync_args_db+'","sign":"'+sync_args_sign+'"}'
    # print(cmd)

    if op == 'get':
        log = mw.getLastLine(tmp_log, 15)
        return mw.returnJson(True, log)

    if op == 'cmd':
        return mw.returnJson(True, 'ok', cmd)

    if op == 'do':
        os.system(' echo "开始执行" > '+ tmp_log)
        os.system(cmd +' >> '+ tmp_log +' &')
        return mw.returnJson(True, 'ok')

    return mw.returnJson(False, '无效请求!')


def syncDatabaseRepair(version=''):
    time_stats_s = time.time()
    tmp_log = syncDatabaseRepairTempFile()

    from pymysql.converters import escape_string
    args = getArgs()
    data = checkArgs(args, ['db','sign'])
    if not data[0]:
        return data[1]

    sync_args_db = args['db']
    sync_args_sign = args['sign']
    
    # 本地数据
    local_db = pMysqlDb()
    # 远程数据
    sync_db = getSyncMysqlDB(sync_args_db,sync_args_sign)

    tables = local_db.query('show tables from `%s`' % sync_args_db)
    table_key = "Tables_in_" + sync_args_db
    inconsistent_table = []

    tmp_dir = '/tmp/sync_db_repair'
    mw.execShell('mkdir -p '+tmp_dir)

    for tb in tables:

        table_name = sync_args_db+'.'+tb[table_key]
        table_check_file = tmp_dir+'/'+table_name+'.txt'

        if os.path.exists(table_check_file):
            # print(table_name+', 已检查OK')
            continue

        primary_key_sql = "SHOW INDEX FROM "+table_name+" WHERE Key_name = 'PRIMARY';";
        primary_key_data = local_db.query(primary_key_sql)
        # print(primary_key_sql,primary_key_data)
        pkey_name = '*'
        if len(primary_key_data) == 1:
            pkey_name = primary_key_data[0]['Column_name']
        # print(pkey_name)
        if pkey_name != '*' :
            # 智能校验(由于服务器同步可能会慢,比较总数总是对不上)
            cmd_local_newpk_sql = 'select ' + pkey_name + ' from ' + table_name + " order by " + pkey_name + " desc limit 1"
            cmd_local_newpk_data = local_db.query(cmd_local_newpk_sql)
            # print(cmd_local_newpk_data)
            if len(cmd_local_newpk_data) == 1:
                # 比较总数
                cmd_count_sql = 'select count('+pkey_name+') as num from '+table_name + ' where '+pkey_name + ' <= '+ str(cmd_local_newpk_data[0][pkey_name])
                local_count_data = local_db.query(cmd_count_sql)
                sync_count_data = sync_db.query(cmd_count_sql)

                if local_count_data != sync_count_data:
                    print(cmd_count_sql)
                    print("all data compare: ",local_count_data, sync_count_data)
                else:
                    print(table_name+' smart compare check ok.')
                    mw.writeFile(tmp_log, table_name+' smart compare check ok.\n','a+')
                    mw.execShell("echo 'ok' > "+table_check_file)
                    continue



        # 比较总数
        cmd_count_sql = 'select count('+pkey_name+') as num from '+table_name
        local_count_data = local_db.query(cmd_count_sql)
        sync_count_data = sync_db.query(cmd_count_sql)

        if local_count_data != sync_count_data:
            print("all data compare: ",local_count_data, sync_count_data)
            inconsistent_table.append(table_name)
            diff = sync_count_data[0]['num'] - local_count_data[0]['num']
            print(table_name+', need sync. diff,'+str(diff))
            mw.writeFile(tmp_log, table_name+', need sync. diff,'+str(diff)+'\n','a+')
        else:
            print(table_name+' check ok.')
            mw.writeFile(tmp_log, table_name+' check ok.\n','a+')
            mw.execShell("echo 'ok' > "+table_check_file)


    # inconsistent_table = ['xx.xx']
    # 数据对齐
    for table_name in inconsistent_table:
        is_break = False
        while not is_break:
            local_db.ping()
            # 远程数据
            sync_db.ping()

            print("check table:"+table_name)
            mw.writeFile(tmp_log, "check table:"+table_name+'\n','a+')
            table_name_pos = 0
            table_name_pos_file = tmp_dir+'/'+table_name+'.pos.txt'
            primary_key_sql = "SHOW INDEX FROM "+table_name+" WHERE Key_name = 'PRIMARY';";
            primary_key_data = local_db.query(primary_key_sql)
            pkey_name = primary_key_data[0]['Column_name']

            if os.path.exists(table_name_pos_file):
                table_name_pos = mw.readFile(table_name_pos_file)
            

            data_select_sql = 'select * from '+table_name + ' where '+pkey_name+' > '+str(table_name_pos)+' limit 10000'
            print(data_select_sql)
            local_select_data = local_db.query(data_select_sql)

            time_s = time.time()
            sync_select_data = sync_db.query(data_select_sql)
            print(f'sync query cos:{time.time() - time_s:.4f}s')
            mw.writeFile(tmp_log, f'sync query cos:{time.time() - time_s:.4f}s\n','a+')

            # print(local_select_data)
            # print(sync_select_data)
            
            # print(len(local_select_data))
            # print(len(sync_select_data))
            print('pos:',str(table_name_pos),'local compare sync,',local_select_data == sync_select_data)
                

            cmd_count_sql = 'select count('+pkey_name+') as num from '+table_name
            local_count_data = local_db.query(cmd_count_sql)
            time_s = time.time()
            sync_count_data = sync_db.query(cmd_count_sql)
            print(f'sync count data cos:{time.time() - time_s:.4f}s')
            print(local_count_data,sync_count_data)
            # 数据同步有延迟，相等即任务数据补足完成
            if local_count_data[0]['num'] == sync_count_data[0]['num']:
                is_break = True
                break

            diff = sync_count_data[0]['num'] - local_count_data[0]['num']
            print("diff," + str(diff)+' line data!')

            if local_select_data == sync_select_data:
                data_count = len(local_select_data)
                if data_count == 0:
                    # mw.writeFile(table_name_pos_file, '0')
                    print(table_name+",data is equal ok..")
                    is_break = True
                    break

                # print(table_name,data_count)
                pos = local_select_data[data_count-1][pkey_name]
                print('pos',pos)
                progress = pos/sync_count_data[0]['num']
                print('progress,%.2f' % progress+'%')
                mw.writeFile(table_name_pos_file, str(pos))
            else:
                sync_select_data_len = len(sync_select_data)
                skip_idx = 0
                # 主库PK -> 查询本地 | 保证一致
                if sync_select_data_len > 0:
                    for idx in range(sync_select_data_len):
                        sync_idx_data = sync_select_data[idx]
                        local_idx_data = None
                        if idx in local_select_data:
                            local_idx_data = local_select_data[idx]
                        if sync_select_data[idx] == local_idx_data:
                            skip_idx = idx
                            pos = local_select_data[idx][pkey_name]
                            mw.writeFile(table_name_pos_file, str(pos))

                        # print(insert_data)
                        local_inquery_sql = 'select * from ' + table_name+ ' where ' +pkey_name+' = '+ str(sync_idx_data[pkey_name])
                        # print(local_inquery_sql)
                        ldata = local_db.query(local_inquery_sql)
                        # print('ldata:',ldata)
                        if len(ldata) == 0:
                            print("id:"+ str(sync_idx_data[pkey_name])+ " no exists, insert")
                            insert_sql = 'insert into ' + table_name
                            field_str = ''
                            value_str = ''
                            for field in sync_idx_data:
                                field_str += '`'+field+'`,'
                                value_str += '\''+escape_string(str(sync_idx_data[field]))+'\','
                            field_str = '(' +field_str.strip(',')+')'
                            value_str = '(' +value_str.strip(',')+')'
                            insert_sql = insert_sql+' '+field_str+' values'+value_str+';'
                            print(insert_sql)
                            r = local_db.execute(insert_sql)
                            print(r)
                        else:
                            # print('compare sync->local:',sync_idx_data ==  ldata[0] )
                            if ldata[0] == sync_idx_data:
                                continue

                            print("id:"+ str(sync_idx_data[pkey_name])+ " data is not equal, update")
                            update_sql = 'update ' + table_name
                            field_str = ''
                            value_str = ''
                            for field in sync_idx_data:
                                if field == pkey_name:
                                    continue
                                field_str += '`'+field+'`=\''+escape_string(str(sync_idx_data[field]))+'\','
                            field_str = field_str.strip(',')
                            update_sql = update_sql+' set '+field_str+' where '+pkey_name+'=\''+str(sync_idx_data[pkey_name])+'\';'
                            print(update_sql)
                            r = local_db.execute(update_sql)
                            print(r)

                # 本地PK -> 查询主库 | 保证一致
                # local_select_data_len = len(local_select_data)
                # if local_select_data_len > 0:
                #     for idx in range(local_select_data_len):
                #         if idx < skip_idx:
                #             continue
                #         local_idx_data = local_select_data[idx]
                #         print('local idx check', idx, skip_idx)
                #         local_inquery_sql = 'select * from ' + table_name+ ' where ' +pkey_name+' = '+ str(local_idx_data[pkey_name])
                #         print(local_inquery_sql)
                #         sdata = sync_db.query(local_inquery_sql)
                #         sdata_len = len(sdata)
                #         print('sdata:',sdata,sdata_len)
                #         if sdata_len == 0:
                #             delete_sql = 'delete from ' + table_name + ' where ' +pkey_name+' = '+ str(local_idx_data[pkey_name])
                #             print(delete_sql)
                #             r = local_db.execute(delete_sql)
                #             print(r)
                #             break
                    

            if is_break:
                print("break all")
                break
            time.sleep(3)
    print(f'data check cos:{time.time() - time_stats_s:.4f}s')
    print("data supplementation completed")
    mw.execShell('rm -rf  '+tmp_dir)
    return 'ok'

############### --- 重要 同步---- ###########

def asyncTmpfile():
    path = '/tmp/mysql_async_status.txt'
    return path


def writeDbSyncStatus(data):
    path = asyncTmpfile()
    mw.writeFile(path, json.dumps(data))
    return True

def fullSyncCmd():
    time_all_s = time.time()
    args = getArgs()
    data = checkArgs(args, ['db', 'sign'])
    if not data[0]:
        return data[1]

    db = args['db']
    sign = args['sign']

    cmd = 'cd '+mw.getServerDir()+'/mdserver-web && source bin/activate && python3 plugins/mysql/index.py do_full_sync  {"db":"'+db+'","sign":"'+sign+'"}'
    return mw.returnJson(True,'ok',cmd)

def doFullSync(version=''):
    mode_file = getSyncModeFile()
    if not os.path.exists(mode_file):
        return mw.returnJson(False, '需要先设置同步配置')

    mode = mw.readFile(mode_file)
    if mode == 'ssh':
        return doFullSyncSSH(version)
    if mode == 'sync-user':
        return doFullSyncUser(version)


def isSimpleSyncCmd(sql):
    new_sql = sql.lower()
    if new_sql.find('master_auto_position') > 0:
        return False
    return True

def getChannelNameForCmd(cmd):
    cmd = cmd.lower()
    cmd_arr = cmd.split('channel')
    if len(cmd_arr) == 2:
        cmd_channel_info = cmd_arr[1]
        channel_name = cmd_channel_info.strip()
        channel_name = channel_name.strip(';')
        channel_name = channel_name.strip("'")
        return channel_name
    return ''



def doFullSyncUserImportContentForChannel(file, channel_name):
    # print(file, channel_name)
    content = mw.readFile(file)

    content = content.replace('STOP SLAVE;', "STOP SLAVE for channel '{}';".format(channel_name))
    content = content.replace('START SLAVE;', "START SLAVE for channel '{}';".format(channel_name))

    find_head = "CHANGE MASTER TO "
    find_re = find_head+"(.*?);"
    find_r = re.search(find_re, content, re.I|re.M)
    if find_r:
        find_rg = find_r.groups()
        if len(find_rg)>0:
            find_str = find_head+find_rg[0]
            if find_str.lower().find('channel')==-1:
                content = content.replace(find_str+';', find_str+" for channel '{}';".format(channel_name))

    mw.writeFile(file,content)
    return True


def doFullSyncUser(version=''):
    which_pv = mw.execShell('which pv')
    is_exist_pv = False
    if os.path.exists(which_pv[0]):
        is_exist_pv = True

    time_all_s = time.time()
    args = getArgs()
    data = checkArgs(args, ['db', 'sign'])
    if not data[0]:
        return data[1]

    sync_db = args['db']
    sync_db_import = args['db']

    if sync_db.lower() == 'all':
        sync_db_import = ''
        dbs = findBinlogSlaveDoDb()
        dbs_str = ''
        for x in dbs:
            dbs_str += ' ' + x
        sync_db = "--databases " + dbs_str.strip()

    sync_sign = args['sign']

    db = pMysqlDb()

    # 重置
    # deleteSlaveFunc(sync_sign)

    conn = pSqliteDb('slave_sync_user')
    if sync_sign != '':
        data = conn.field('ip,port,user,pass,mode,cmd').where(
            'ip=?', (sync_sign,)).find()
    else:
        data = conn.field('ip,port,user,pass,mode,cmd').find()

    # print(data)
    user = data['user']
    apass = data['pass']
    port = data['port']
    ip = data['ip']
    cmd = data['cmd']
    channel_name = getChannelNameForCmd(cmd)

    sync_mdb = getSyncMysqlDB(sync_db,sync_sign)

    bak_file = '/tmp/tmp.sql'
    if os.path.exists(bak_file):
        os.system("rm -rf " + bak_file)

    writeDbSyncStatus({'code': 0, 'msg': '开始同步...', 'progress': 0})
    dmp_option = ''
    mode = recognizeDbMode()
    if mode == 'gtid':
        dmp_option = ' --set-gtid-purged=off '

    time.sleep(1)
    writeDbSyncStatus({'code': 1, 'msg': '正在停止从库...', 'progress': 15})

    mdb8 = getMdb8Ver()
    if mw.inArray(mdb8,version):
        db.query("stop slave user='{}' password='{}';".format(user, apass))
    else:
        db.query("stop slave")
        
    time.sleep(1)

    writeDbSyncStatus({'code': 2, 'msg': '远程导出数据...', 'progress': 20})

    # --master-data=2表示在dump过程中记录主库的binlog和pos点，并在dump文件中注释掉这一行
    # --master-data=1表示在dump过程中记录主库的binlog和pos点，并在dump文件中不注释掉这一行，即恢复时会执行

    # --dump-slave=2表示在dump过程中，在从库dump，mysqldump进程也要在从库执行，记录当时主库的binlog和pos点，并在dump文件中注释掉这一行
    # --dump-slave=1表示在dump过程中，在从库dump，mysqldump进程也要在从库执行，记录当时主库的binlog和pos点，并在dump文件中不注释掉这一行

    # --force --opt --single-transaction
    # --skip-opt --create-options
    # --master-data=1

    find_run_dump = mw.execShell('ps -ef | grep mysqldump | grep -v grep')
    if find_run_dump[0] != "":
        print("正在远程导出数据中,别着急...")
        writeDbSyncStatus({'code': 3.1, 'msg': '正在远程导出数据中,别着急...', 'progress': 19})
        return False

    time_s = time.time()
    if not os.path.exists(bak_file):
        dmp_option += ' '
        if mw.inArray(mdb8,version):
            # --compression-algorithms
            dmp_option += " --source-data=1 --apply-replica-statements --include-source-host-port "
        else:
            dmp_option += " --master-data=1 --apply-slave-statements --include-master-host-port --compress "

        dump_sql_data = getServerDir() + "/bin/mysqldump --single-transaction --default-character-set=utf8mb4 -q " + dmp_option + " -h" + ip + " -P" + \
            port + " -u" + user + " -p'" + apass + "' --ssl-mode=DISABLED " + sync_db + " > " + bak_file
        print(dump_sql_data)
        time_s = time.time()
        r = mw.execShell(dump_sql_data)
        print(r)
    time_e = time.time()
    export_cos = time_e - time_s
    print("export cos:", export_cos)
    
    writeDbSyncStatus({'code': 3, 'msg': '导出耗时:'+str(int(export_cos))+'秒,正在到本地导入数据中...', 'progress': 40})

    find_run_import = mw.execShell('ps -ef | grep mysql| grep '+ bak_file +' | grep -v grep')
    if find_run_import[0] != "":
        print("正在导入数据中,别着急...")
        writeDbSyncStatus({'code': 4.1, 'msg': '正在导入数据中,别着急...', 'progress': 39})
        return False

    time_s = time.time()
    if os.path.exists(bak_file):
        # 重置 
        db.execute('reset master')

        # 加快导入 - 开始
        # db.execute('set global innodb_flush_log_at_trx_commit = 2')
        # db.execute('set global sync_binlog = 2000')

        if channel_name != '':
            doFullSyncUserImportContentForChannel(bak_file, channel_name)

        pwd = pSqliteDb('config').where('id=?', (1,)).getField('mysql_root')
        sock = getSocketFile()

        if is_exist_pv:
            my_import_cmd = getServerDir() + '/bin/mysql -S ' + sock + " -uroot -p'" + pwd + "' " + sync_db_import
            my_import_cmd = "pv -t -p " + bak_file + '|' + my_import_cmd
            print(my_import_cmd)
            os.system(my_import_cmd)
        else:
            my_import_cmd = getServerDir() + '/bin/mysql -S ' + sock + " -uroot -p'" + pwd + "' " + sync_db_import + ' < ' + bak_file
            print(my_import_cmd)
            mw.execShell(my_import_cmd)

        # 加快导入 - 结束
        # db.execute('set global innodb_flush_log_at_trx_commit = 1')
        # db.execute('set global sync_binlog = 1')

    time_e = time.time()
    import_cos = time_e - time_s
    print("import cos:", import_cos)
    writeDbSyncStatus({'code': 4, 'msg': '导入耗时:'+str(int(import_cos))+'秒', 'progress': 60})

    time.sleep(3)
    # print(cmd)
    # r = db.query(cmd)
    # print(r)

    if mw.inArray(mdb8,version):
        db.query("start replica user='{}' password='{}';".format(user, apass))
    else:
        db.query("start slave")

    db.query("start all slaves")
    time_all_e = time.time()
    cos = time_all_e - time_all_s
    writeDbSyncStatus({'code': 6, 'msg': '总耗时:'+str(int(cos))+'秒,从库重启完成...', 'progress': 100})

    if os.path.exists(bak_file):
        os.system("rm -rf " + bak_file)

    return True


def doFullSyncSSH(version=''):

    args = getArgs()
    data = checkArgs(args, ['db', 'sign'])
    if not data[0]:
        return data[1]

    sync_db = args['db']
    sync_sign = args['sign']

    db = pMysqlDb()

    id_rsa_conn = pSqliteDb('slave_id_rsa')
    if sync_sign != '':
        data = id_rsa_conn.field('ip,port,db_user,id_rsa').where(
            'ip=?', (sync_sign,)).find()
    else:
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
    cmd = "cd /www/server/mdserver-web && source bin/activate && python3 " + \
        getSPluginDir() + "/index.py dump_mysql_data {\"db\":'" + dbname + "'}"
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

    cmd = 'cd /www/server/mdserver-web && source bin/activate && python3 ' + \
        getSPluginDir() + \
        '/index.py get_master_rep_slave_user_cmd {"username":"' + \
        db_user + '","db":""}'
    stdin, stdout, stderr = ssh.exec_command(cmd)
    result = stdout.read()
    result = result.decode('utf-8')
    cmd_data = json.loads(result)

    db.query('stop slave')
    writeDbSyncStatus({'code': 3, 'msg': '停止从库完成...', 'progress': 45})

    cmd = cmd_data['data']['cmd']
    # 保证同步IP一致
    if cmd.find('SOURCE_HOST') > -1:
        cmd = re.sub(r"SOURCE_HOST='(.*?)'",
                     "SOURCE_HOST='" + ip + "'", cmd, 1)

    if cmd.find('MASTER_HOST') > -1:
        cmd = re.sub(r"MASTER_HOST='(.*?)'",
                     "MASTER_HOST='" + ip + "'", cmd, 1)

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

    print(cmd)
    import_data = mw.execShell(cmd)
    if import_data[0] == '':
        print(import_data[1])
        writeDbSyncStatus({'code': 5, 'msg': '导入数据完成...', 'progress': 90})
    else:
        print(import_data[0])
        writeDbSyncStatus({'code': 5, 'msg': '导入数据失败...', 'progress': 100})
        return 'fail'
    
    mdb8 = getMdb8Ver()
    if mw.inArray(mdb8,version):
        db.query("start slave user='{}' password='{}';".format(uinfo['username'], uinfo['password']))
    else:
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

    sign = ''
    if 'sign' in args:
        sign = args['sign']

    status_file = asyncTmpfile()
    if args['begin'] == '1':
        cmd = 'cd ' + mw.getRunDir() + ' && python3 ' + getPluginDir() + \
            '/index.py do_full_sync {"db":"' + \
            args['db'] + '","sign":"' + sign + '"} &'
        # print(cmd)
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
    import psutil
    mem = psutil.virtual_memory()
    memTotal = mem.total
    memG = memTotal/1024/1024/1024
    if memG > 2:
        return 'ok'

    swap_path = mw.getServerDir() + "/swap"
    if not os.path.exists(swap_path):
        return "内存小,为了稳定安装MySQL,先安装swap插件!"
    return 'ok'


def uninstallPreInspection(version):
    data_dir = getDataDir()
    if os.path.exists(data_dir):
        stop(version)

    if mw.isDebugMode():
        return 'ok'

    import plugins_api
    plugins_api.plugins_api().removeIndex(getPluginName(), version)

    return "请手动删除MySQL[{}]<br/> rm -rf {}".format(version, getServerDir())

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
        print(runInfo(version))
    elif func == 'db_status':
        print(myDbStatus(version))
    elif func == 'set_db_status':
        print(setDbStatus(version))
    elif func == 'conf':
        print(getConf())
    elif func == 'bin_log':
        print(binLog(version))
    elif func == 'binlog_list':
        print(binLogList())
    elif func == 'clean_bin_log':
        print(cleanBinLog())
    elif func == 'error_log':
        print(getErrorLog())
    elif func == 'show_log':
        print(getShowLogFile())
    elif func == 'my_db_pos':
        print(getMyDbPos())
    elif func == 'set_db_pos':
        print(setMyDbPos(version))
    elif func == 'my_port':
        print(getMyPort())
    elif func == 'set_my_port':
        print(setMyPort(version))
    elif func == 'init_pwd':
        print(initMysqlPwd())
    elif func == 'root_pwd':
        print(rootPwd())
    elif func == 'get_db_list':
        print(getDbList())
    elif func == 'set_db_backup':
        print(setDbBackup())
    elif func == 'import_db_backup':
        print(importDbBackup())
    elif func == 'import_db_backup_progress':
        print(importDbBackupProgress())
    elif func == 'import_db_backup_progress_bar':
        print(importDbBackupProgressBar())
    elif func == 'import_db_external':
        print(importDbExternal())
    elif func == 'import_db_external_progress':
        print(importDbExternalProgress())
    elif func == 'import_db_external_progress_bar':
        print(importDbExternalProgressBar())
    elif func == 'delete_db_backup':
        print(deleteDbBackup())
    elif func == 'get_db_backup_list':
        print(getDbBackupList())
    elif func == 'get_db_backup_import_list':
        print(getDbBackupImportList())
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
    elif func == 'fix_db_access':
        print(fixDbAccess(version))
    elif func == 'set_db_rw':
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
    elif func == 'reset_master':
        print(resetMaster(version))
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
    elif func == 'try_slave_sync_bugfix':
        print(trySlaveSyncBugfix(version))
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
    elif func == 'get_slave_sync_user_list':
        print(getSlaveSyncUserList(version))
    elif func == 'get_slave_sync_user_by_ip':
        print(getSlaveSyncUserByIp(version))
    elif func == 'add_slave_sync_user':
        print(addSlaveSyncUser(version))
    elif func == 'del_slave_sync_user':
        print(delSlaveSyncUser(version))
    elif func == 'get_slave_sync_mode':
        print(getSlaveSyncMode(version))
    elif func == 'set_slave_sync_mode':
        print(setSlaveSyncMode(version))
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
    elif func == 'full_sync_cmd':
        print(fullSyncCmd())
    elif func == 'dump_mysql_data':
        print(dumpMysqlData(version))
    elif func == 'sync_database_repair':
        print(syncDatabaseRepair())
    elif func == 'sync_database_repair_log':
        print(syncDatabaseRepairLog())
    else:
        print('error')
