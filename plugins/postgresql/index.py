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

# python3 plugins/postgresql/index.py start 14.4
# python3 plugins/postgresql/index.py run_info 14.4
# ps -ef | grep -v grep| grep run_info | awk '{print $2}' | xargs kill -9
# vi /etc/sysconfig/network-scripts/ifcfg-eth0

web_dir = os.getcwd() + "/web"
if os.path.exists(web_dir):
    sys.path.append(web_dir)
    os.chdir(web_dir)

import core.mw as mw


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


def getBackupDir():
    bk_path = mw.getBackupDir() + "/database/postgresql"
    if not os.path.isdir(bk_path):
        mw.execShell("mkdir -p {}".format(bk_path))
    return bk_path


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


def pgHbaConf():
    return getServerDir() + "/data/pg_hba.conf"


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
    rep = r'port\s*=\s*(\d*)?'
    tmp = re.search(rep, content)
    return tmp.groups()[0].strip()


def getSocketFile():
    # sock_name = '.s.PGSQL.' + getDbPort()
    sock_name = ""
    sock_tmp = '/tmp/' + sock_name
    if os.path.exists(sock_tmp):
        return sock_tmp

    sock_app = getServerDir() + "/" + sock_name
    if os.path.exists(sock_app):
        return sock_app
    return sock_app


def getInitdTpl(version=''):
    path = getPluginDir() + '/init.d/postgresql.tpl'
    if not os.path.exists(path):
        path = getPluginDir() + '/init.d/postgresql.tpl'
    return path


def contentReplace(content):
    service_path = mw.getServerDir()
    content = content.replace('{$ROOT_PATH}', mw.getFatherDir())
    content = content.replace('{$SERVER_PATH}', service_path)
    content = content.replace('{$APP_PATH}', service_path + '/postgresql')
    return content


def pSqliteDb(dbname='databases', name='pgsql'):
    file = getServerDir() + '/' + name + '.db'
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
    db.setPwd(pSqliteDb('config').where('id=?', (1,)).getField('pg_root'))
    db.setSocket(getSocketFile())
    return db


def initConfig(version=''):
    conf_dir = getServerDir()
    init_pl = conf_dir + "/init.pl"
    if not os.path.exists(init_pl):
        mw.writeFile(init_pl, 'ok')

        # postgresql.conf
        pg_conf = conf_dir + '/data/postgresql.conf'
        tpl = getPluginDir() + '/conf/postgresql.conf'
        content = mw.readFile(tpl)
        content = contentReplace(content)
        mw.writeFile(pg_conf, content)

        # pg_hba.conf
        tpl = getPluginDir() + '/conf/pg_hba.conf'
        pg_hba_conf = conf_dir + '/data/pg_hba.conf'
        content = mw.readFile(tpl)
        mw.writeFile(pg_hba_conf, content)

        logfile = runLog()
        if not os.path.exists(logfile):
            mw.writeFile(logfile, '')


def initDreplace(version=''):

    conf_dir = getServerDir()
    conf_list = [
        conf_dir + "/logs",
        conf_dir + "/tmp",
        conf_dir + "/archivelog",
    ]
    for c in conf_list:
        if not os.path.exists(c):
            os.mkdir(c)

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
        mw.execShell('chown -R postgres:postgres ' + getServerDir())

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


def pgCmd(cmd):
    return "su - postgres -c \"" + cmd + "\""


def execShellPg(cmd):
    return mw.execShell(pgCmd(cmd))


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
            execShellPg(cmd)
            return False
        mw.execShell(cmd)
        return False
    return True


def initPgPwd():

    serverdir = getServerDir()
    pwd = mw.getRandomString(16)

    cmd_pass = serverdir + '/bin/createuser -s -r postgres'

    if not mw.isAppleSystem():
        cmd_pass = 'su - postgres -c "' + cmd_pass + '"'
    data = mw.execShell(cmd_pass)

    cmd_pass = "echo \"alter user postgres with password '" + pwd + "'\" | "
    if not mw.isAppleSystem():
        cmd = serverdir + '/bin/psql -d postgres'
        cmd_pass = cmd_pass + ' ' + pgCmd(cmd)
    else:
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
        initConfig(version)
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
    rep = r'datadir\s*=\s*(.*)'
    tmp = re.search(rep, content)
    return tmp.groups()[0].strip()


def getPgPort():
    file = getConf()
    content = mw.readFile(file)
    rep = r'port\s*=\s*(.*)'
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
    rep = r"port\s*=\s*([0-9]+)\s*\n"
    content = re.sub(rep, 'port = ' + port + '\n', content)
    mw.writeFile(file, content)
    restart()
    return mw.returnJson(True, '编辑成功!')


def runInfo():

    if status(version) == 'stop':
        return mw.returnJson(False, 'PG未启动', [])

    db = pgDb()
    data_dir = getServerDir() + "/data"
    port = getPgPort()
    result = {}

    result['uptime'] = mw.execShell(
        '''cat {}/postmaster.pid |sed -n 3p '''.format(data_dir))[0]
    timestamp = result['uptime']
    time_local = time.localtime(int(timestamp))
    dt = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
    result['uptime'] = dt

    result['progress_num'] = mw.execShell(
        "ps -ef |grep postgres |wc -l")[0].strip()
    result['pid'] = mw.execShell(
        '''cat {}/postmaster.pid |sed -n 1p '''.format(data_dir))[0].strip()
    res = db.query(
        "select count(*) from pg_stat_activity where not pid=pg_backend_pid()")

    # print(res)
    result['connections'] = res[0][0]

    res = db.query("select pg_size_pretty(pg_database_size('postgres'))")
    result['pg_size'] = res[0][0]
    result['pg_mem'] = mw.execShell(
        '''cat /proc/%s/status|grep VmRSS|awk -F: '{print $2}' ''' % (result['pid']))[0]

    result['pg_vm_lock'] = mw.execShell(
        '''cat /proc/%s/status|grep VmLck|awk -F: '{print $2}'  ''' % (result['pid'].strip()))[0]
    result['pg_vm_high'] = mw.execShell(
        '''cat /proc/%s/status|grep VmHWM|awk -F: '{print $2}'  ''' % (result['pid'].strip()))[0]
    result['pg_vm_data_size'] = mw.execShell(
        '''cat /proc/%s/status|grep VmData|awk -F: '{print $2}'  ''' % (result['pid'].strip()))[0]
    result['pg_vm_sk_size'] = mw.execShell(
        '''cat /proc/%s/status|grep VmStk|awk -F: '{print $2}'  ''' % (result['pid'].strip()))[0]
    result['pg_vm_code_size'] = mw.execShell(
        '''cat /proc/%s/status|grep VmExe|awk -F: '{print $2}'  ''' % (result['pid'].strip()))[0]
    result['pg_vm_lib_size'] = mw.execShell(
        '''cat /proc/%s/status|grep VmLib|awk -F: '{print $2}'  ''' % (result['pid'].strip()))[0]
    result['pg_vm_swap_size'] = mw.execShell(
        '''cat /proc/%s/status|grep VmSwap|awk -F: '{print $2}'  ''' % (result['pid'].strip()))[0]
    result['pg_vm_page_size'] = mw.execShell(
        '''cat /proc/%s/status|grep VmPTE|awk -F: '{print $2}'  ''' % (result['pid'].strip()))[0]
    result['pg_sigq'] = mw.execShell(
        '''cat /proc/%s/status|grep SigQ|awk -F: '{print $2}'  ''' % (result['pid'].strip()))[0]

    return mw.getJson(result)


def runLog():
    return getServerDir() + "/logs/server.log"


def getSlowLog():
    # pgsql慢日志查询
    return getServerDir() + "/logs/" + time.strftime("postgresql-%Y-%m-%d.log")


def getUnit(args):
    unit = ''
    if "GB" in args:
        unit = "GB"
    elif "MB" in args:
        unit = "MB"
    elif "KB" in args:
        unit = "KB"
    elif "kB" in args:
        unit = "kB"
    return unit


def pgDbStatus():

    data_directory = getServerDir() + "/data"
    data = {}
    shared_buffers, work_mem, effective_cache_size, maintence_work_mem, max_connections, temp_buffers, max_prepared_transactions, max_stack_depth, bgwriter_lru_maxpages, max_worker_processes, listen_addresses = '', '', '', '', '', '', '', '', '', '', ''
    with open("{}/postgresql.conf".format(data_directory)) as f:
        for i in f:
            if i.strip().startswith("shared_buffers"):
                shared_buffers = i.split("=")[1]
            elif i.strip().startswith("#shared_buffers"):
                shared_buffers = i.split("=")[1]

            shared_buffers_num = re.match(
                r'\d+', shared_buffers.strip()).group() if re.match(r'\d+', shared_buffers.strip()) else ""
            data['shared_buffers'] = [shared_buffers_num, "MB",
                                      "PG通过shared_buffers和内核和磁盘打交道，通常设置为实际内存的10％."]

            if i.strip().startswith("work_mem"):
                work_mem = i.split("=")[1]
            elif i.strip().startswith("#work_mem"):
                work_mem = i.split("=")[1]

            work_mem_num = re.match(
                r'\d+', work_mem.strip()).group() if re.match(r'\d+', work_mem.strip()) else ""
            data['work_mem'] = [work_mem_num, "MB",
                                "增加work_mem有助于提高排序的速度。通常设置为实际RAM的2% -4%."]

            if i.strip().startswith("effective_cache_size"):
                effective_cache_size = i.split("=")[1]
            elif i.strip().startswith("#effective_cache_size"):
                effective_cache_size = i.split("=")[1]

            effective_cache_size_num = re.match(r'\d+', effective_cache_size.strip(
            )).group() if re.match(r'\d+', effective_cache_size.strip()) else ""
            data['effective_cache_size'] = [effective_cache_size_num,
                                            "GB", "PG能够使用的最大缓存,比如4G的内存，可以设置为3GB."]

            if i.strip().startswith("temp_buffers "):
                temp_buffers = i.split("=")[1]
            elif i.strip().startswith("#temp_buffers "):
                temp_buffers = i.split("=")[1]

            temp_buffers_num = re.match(
                r'\d+', temp_buffers.strip()).group() if re.match(r'\d+', temp_buffers.strip()) else ""
            data['temp_buffers'] = [temp_buffers_num, "MB",
                                    "设置每个数据库会话使用的临时缓冲区的最大数目，默认是8MB"]

            if i.strip().startswith("max_connections"):
                max_connections = i.split("=")[1]
            elif i.strip().startswith("#max_connections"):
                max_connections = i.split("=")[1]

            max_connections_num = re.match(
                r'\d+', max_connections.strip()).group() if re.match(r'\d+', max_connections.strip()) else ""
            data['max_connections'] = [max_connections_num,
                                       getUnit(max_connections), "最大连接数"]

            if i.strip().startswith("max_prepared_transactions"):
                max_prepared_transactions = i.split("=")[1]
            elif i.strip().startswith("#max_prepared_transactions"):
                max_prepared_transactions = i.split("=")[1]

            max_prepared_transactions_num = re.match(r'\d+', max_prepared_transactions.strip(
            )).group() if re.match(r'\d+', max_prepared_transactions.strip()) else ""
            data['max_prepared_transactions'] = [max_prepared_transactions_num, getUnit(
                max_prepared_transactions), "设置可以同时处于 prepared 状态的事务的最大数目"]

            if i.strip().startswith("max_stack_depth "):
                max_stack_depth = i.split("=")[1]
            elif i.strip().startswith("#max_stack_depth "):
                max_stack_depth = i.split("=")[1]

            max_stack_depth_num = re.match(
                r'\d+', max_stack_depth.strip()).group() if re.match(r'\d+', max_stack_depth.strip()) else ""
            data['max_stack_depth'] = [max_stack_depth_num,
                                       "MB", "指定服务器的执行堆栈的最大安全深度，默认是2MB"]

            if i.strip().startswith("bgwriter_lru_maxpages "):
                bgwriter_lru_maxpages = i.split("=")[1]
            elif i.strip().startswith("#bgwriter_lru_maxpages "):
                bgwriter_lru_maxpages = i.split("=")[1]

            bgwriter_lru_maxpages_num = re.match(r'\d+', bgwriter_lru_maxpages.strip(
            )).group() if re.match(r'\d+', bgwriter_lru_maxpages.strip()) else ""
            data['bgwriter_lru_maxpages'] = [
                bgwriter_lru_maxpages_num, "", "一个周期最多写多少脏页"]

            if i.strip().startswith("max_worker_processes "):
                max_worker_processes = i.split("=")[1]
            elif i.strip().startswith("#max_worker_processes "):
                max_worker_processes = i.split("=")[1]

            max_worker_processes_num = re.match(r'\d+', max_worker_processes.strip(
            )).group() if re.match(r'\d+', max_worker_processes.strip()) else ""
            data['max_worker_processes'] = [max_worker_processes_num,
                                            "", "如果要使用worker process, 最多可以允许fork 多少个worker进程."]

            # if i.strip().startswith("listen_addresses"):
            #     listen_addresses = i.split("=")[1]
            # elif i.strip().startswith("#listen_addresses"):
            #     listen_addresses = i.split("=")[1]

            # listen_addresses = re.match(r"\'.*?\'", listen_addresses.strip()).group(
            # ) if re.match(r"\'.*?\'", listen_addresses.strip()) else ""
            # data['listen_addresses'] = [listen_addresses.replace(
            #     "'", '').replace("127.0.0.1", 'localhost'), "", "pgsql监听地址"]

    # 返回数据到前端
    data['status'] = True
    return mw.getJson(data)


def sedConf(name, val):
    path = getServerDir() + "/data/postgresql.conf"
    content = ''
    with open(path) as f:
        for i in f:
            if i.strip().startswith(name):
                i = "{} = {} \n".format(name, val)
            content += i

    mw.writeFile(path, content)
    return True


def pgSetDbStatus():
    '''
    保存pgsql性能调整信息
    '''
    args = getArgs()
    data = checkArgs(args, ['shared_buffers', 'work_mem', 'effective_cache_size',
                            'temp_buffers', 'max_connections', 'max_prepared_transactions',
                            'max_stack_depth', 'bgwriter_lru_maxpages', 'max_worker_processes'])
    if not data[0]:
        return data[1]

    for k, v in args.items():
        sedConf(k, v)

    restart()
    return mw.returnJson(True, '设置成功!')


def setUserPwd(version=''):
    args = getArgs()
    data = checkArgs(args, ['password', 'name'])
    if not data[0]:
        return data[1]

    newpwd = args['password']
    username = args['name']
    uid = args['id']
    try:
        pdb = pgDb()
        psdb = pSqliteDb('databases')
        name = psdb.where('id=?', (uid,)).getField('name')

        r = pdb.execute(
            "alter user {} with password '{}'".format(username, newpwd))

        psdb.where("id=?", (uid,)).setField('password', newpwd)
        return mw.returnJson(True, mw.getInfo('修改数据库[{1}]密码成功!', (name,)))
    except Exception as ex:
        return mw.returnJson(False, mw.getInfo('修改数据库[{1}]密码失败[{2}]!', (name, str(ex),)))


def getDbBackupListFunc(dbname=''):
    bkDir = getBackupDir()
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

def rootPwd():
    return pSqliteDb('config').where('id=?', (1,)).getField('pg_root')

def importDbBackup():
    args = getArgs()
    data = checkArgs(args, ['file', 'name'])
    if not data[0]:
        return data[1]

    file = args['file']
    name = args['name']

    file_path = getBackupDir() + '/' + file
    file_path_sql = getBackupDir() + '/' + file.replace('.gz', '')

    if not os.path.exists(file_path_sql):
        cmd = 'cd ' + getBackupDir() + ' && gzip -d ' + file
        mw.execShell(cmd)

    pwd = pSqliteDb('config').where('id=?', (1,)).getField('pg_root')

    mysql_cmd = mw.getFatherDir() + '/server/mysql/bin/mysql -uroot -p' + pwd + ' ' + name + ' < ' + file_path_sql

    # print(mysql_cmd)
    os.system(mysql_cmd)
    return mw.returnJson(True, 'ok')


def deleteDbBackup():
    args = getArgs()
    data = checkArgs(args, ['filename'])
    if not data[0]:
        return data[1]

    bkDir = getBackupDir()
    os.remove(bkDir + '/' + args['filename'])
    return mw.returnJson(True, 'ok')


def getDbBackupList():
    args = getArgs()
    data = checkArgs(args, ['name'])
    if not data[0]:
        return data[1]

    r = getDbBackupListFunc(args['name'])
    bkDir = getBackupDir()
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
        'id=?', (1,)).getField('pg_root')
    data['info'] = info

    return mw.getJson(data)


def syncGetDatabases():
    pdb = pgDb()
    psdb = pSqliteDb('databases')
    data = pdb.table('pg_database').field(
        'datname').where("datistemplate=false").select()
    nameArr = ['postgres']
    n = 0

    for value in data:
        vdb_name = value["datname"]
        b = False
        for key in nameArr:
            if vdb_name == key:
                b = True
                break
        if b:
            continue
        if psdb.where("name=?", (vdb_name,)).count() > 0:
            continue
        host = '127.0.0.1/32'
        ps = vdb_name
        addTime = time.strftime('%Y-%m-%d %X', time.localtime())
        if psdb.add('name,username,password,accept,ps,addtime', (vdb_name, vdb_name, '', host, ps, addTime)):
            n += 1

    msg = mw.getInfo('本次共从服务器获取了{1}个数据库!', (str(n),))
    return mw.returnJson(True, msg)


def addDb():
    args = getArgs()
    data = checkArgs(args, ['password', 'name', 'db_user', 'dataAccess'])
    if not data[0]:
        return data[1]

    address = ''
    if 'address' in args:
        address = args['address'].strip()

    dbname = args['name'].strip()
    dbuser = args['db_user'].strip()
    password = args['password'].strip()
    dataAccess = args['dataAccess'].strip()

    listen_ip = "127.0.0.1/32"
    if 'listen_ip' in args:
        listen_ip = args['listen_ip'].strip()

    if not re.match(r"(?:[0-9]{1,3}\.){3}[0-9]{1,3}/\d+", listen_ip):
        return mw.returnJson(False, "你输入的权限不合法，添加失败！")

    # 修改监听所有地址
    if listen_ip not in ["127.0.0.1/32", "localhost", "127.0.0.1"]:
        sedConf("listen_addresses", "'*'")

    reg = r"^[\w\.-]+$"
    if not re.match(reg, dbname):
        return mw.returnJson(False, '数据库名称不能带有特殊符号!')

    checks = ['root', 'mysql', 'test', 'sys', 'postgres', 'postgresql']
    if dbuser in checks or len(dbuser) < 1:
        return mw.returnJson(False, '数据库用户名不合法!')
    if dbname in checks or len(dbname) < 1:
        return mw.returnJson(False, '数据库名称不合法!')

    if len(password) < 1:
        password = mw.md5(time.time())[0:8]

    pdb = pgDb()
    psdb = pSqliteDb('databases')

    if psdb.where("name=? or username=?", (dbname, dbuser)).count():
        return mw.returnJson(False, '数据库或用户已存在!')

    sql = "select pg_terminate_backend(pid) from pg_stat_activity where DATNAME = 'template1';"
    pdb.execute(sql)
    r = pdb.execute("create database " + dbname)
    # print(r)
    r = pdb.execute("create user " + dbuser)
    # print(r)
    pdb.execute("alter user {} with password '{}'".format(dbuser, password,))
    pdb.execute(
        "GRANT ALL PRIVILEGES ON DATABASE {} TO {}".format(dbname, dbuser,))

    pg_hba = getServerDir() + "/data/pg_hba.conf"

    content = mw.readFile(pg_hba)
    content += "\nhost    {}  {}    {}    md5".format(
        dbname, dbuser, listen_ip)
    mw.writeFile(pg_hba, content)

    addTime = time.strftime('%Y-%m-%d %X', time.localtime())
    psdb.add('pid,name,username,password,accept,ps,addtime',
             (0, dbname, dbuser, password, listen_ip, dbname, addTime))

    restart()
    return mw.returnJson(True, '添加成功!')


def delDb():
    args = getArgs()
    data = checkArgs(args, ['id', 'name'])
    if not data[0]:
        return data[1]

    did = args['id']
    name = args['name']

    pdb = pgDb()
    psdb = pSqliteDb('databases')

    username = psdb.where('id=?', (did,)).getField('username')
    # print(username, len(username))
    if len(username) > 0:
        r = pdb.execute("drop user " + str(username))
        # print(r)

    sql = "SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE datname='" + \
        name + "' AND pid<>pg_backend_pid();"

    r = pdb.execute(sql)
    # print(r)
    r = pdb.execute("drop database " + name)
    # print(r)

    pg_hba = pgHbaConf()
    old_config = mw.readFile(pg_hba)
    new_config = re.sub(r'host\s*{}.*'.format(name), '', old_config).strip()
    mw.writeFile(pg_hba, new_config)

    psdb.where("id=?", (did,)).delete()
    return mw.returnJson(True, '删除成功!')


def setDbRw(version=''):
    args = getArgs()
    data = checkArgs(args, ['username', 'id', 'rw'])
    if not data[0]:
        return data[1]

    username = args['username']
    uid = args['id']
    rw = args['rw']

    pdb = pgDb()
    psdb = pSqliteDb('databases')
    dbname = psdb.where("id=?", (uid,)).getField('name')

    sql = "REVOKE ALL ON database " + dbname + " FROM " + username
    pdb.query(sql)

    if rw == 'rw':
        sql = "GRANT SELECT, INSERT, UPDATE, DELETE ON database " + dbname + " TO " + username
    elif rw == 'r':
        sql = "GRANT SELECT ON database " + dbname + " TO " + username
    else:
        sql = "GRANT all ON database " + dbname + " TO " + username

    r = pdb.execute(sql)
    psdb.where("id=?", (uid,)).setField('rw', rw)
    return mw.returnJson(True, '切换成功!')


def getDbAccess():
    args = getArgs()
    data = checkArgs(args, ['name'])
    if not data[0]:
        return data[1]
    name = args['name']
    psdb = pSqliteDb('databases')
    accept = psdb.where("name=?", (name,)).getField('accept')
    return mw.returnJson(True, accept)


def setDbAccess():
    args = getArgs()
    data = checkArgs(args, ['name'])
    if not data[0]:
        return data[1]

    name = args['name']
    access = args['access']

    psdb = pSqliteDb('databases')

    conf = pgHbaConf()
    data = mw.readFile(conf)
    new_data = re.sub(r'host\s*{}.*'.format(name), '', data).strip()

    new_data += "\nhost    {}  {}    {}    md5".format(
        name, name, access)
    mw.writeFile(conf, new_data)

    psdb.where("name=?", (name,)).setField('accept', access)
    return mw.returnJson(True, "设置成功")


def pgBack():
    # 备份数据库

    args = getArgs()
    data = checkArgs(args, ['name'])
    if not data[0]:
        return data[1]

    bk_path_upload = getBackupDir()
    database = args['name']
    port = getPgPort()

    cmd = '''su - postgres -c "/www/server/pgsql/bin/pg_dump -c {} -p {} "| gzip > {}/{}_{}.gz '''.format(
        database, port, bk_path_upload, database, time.strftime("%Y%m%d_%H%M%S"))

    if mw.isAppleSystem():
        cmd = '''{}/bin/pg_dump -c {} -p {} | gzip > {}/{}_{}.gz '''.format(
            getServerDir(), database, port, bk_path_upload, database, time.strftime("%Y%m%d_%H%M%S"))
    mw.execShell(cmd)

    return mw.returnJson(True, '备份成功!')


def pgBackList():

    args = getArgs()
    data = checkArgs(args, ['name'])
    if not data[0]:
        return data[1]

    database = args['name']

    bk_path_upload = getBackupDir()
    file_list = os.listdir(bk_path_upload)
    data = []
    for i in file_list:
        if i.split("_")[0].startswith(database):
            file_path = os.path.join(bk_path_upload, i)
            file_info = os.stat(file_path)
            create_time = file_info.st_ctime
            time_local = time.localtime(int(create_time))
            create_time = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
            file_size = file_info.st_size
            file_size = mw.toSize(file_size)
            data.append({"name": i, "time": create_time,
                         "size": file_size, "file": file_path})

    return mw.returnJson(True, 'ok', data)


def importDbBackup():
    args = getArgs()
    data = checkArgs(args, ['file', 'name'])
    if not data[0]:
        return data[1]

    file = args['file']
    name = args['name']

    bk_path_upload = getBackupDir()

    file_path = os.path.join(bk_path_upload, name)
    if not os.path.exists(file_path):
        return mw.returnJson(False, '备份文件不存在')

    port = getPgPort()
    cmd = '''gunzip -c {}|su - postgres -c " /www/server/pgsql/bin/psql  -d {}  -p {} " '''.format(
        file, name, port)

    if mw.isAppleSystem():
        cmd = '''gunzip -c {} | {}/bin/psql  -d {}  -p {}'''.format(
            name, getServerDir(), port)

    # print(cmd)

    mw.execShell(cmd)
    return mw.returnJson(True, '恢复数据库成功')


def deleteDbBackup():
    args = getArgs()
    data = checkArgs(args, ['filename'])
    if not data[0]:
        return data[1]

    bk_path_upload = getBackupDir()
    os.remove(bk_path_upload + '/' + args['filename'])
    return mw.returnJson(True, 'ok')


############ 主从功能 ######################
def getMasterStatus(version=''):

    data = {}
    data['mode'] = 'classic'
    data['status'] = False
    data['slave_status'] = False
    pg_conf = getServerDir() + "/data/postgresql.conf"
    pg_content = mw.readFile(pg_conf)

    if pg_content.find('#archive_mode') > -1:
        data['status'] = False
    else:
        data['status'] = True

    if pg_content.find('#hot_standby') > -1:
        data['slave_status'] = False
    else:
        data['slave_status'] = True

    return mw.returnJson(True, '设置成功', data)


def setMasterStatus(version=''):
    pg_conf = getServerDir() + "/data/postgresql.conf"
    data = mw.readFile(pg_conf)

    if data.find('#archive_mode') > -1:
        data = data.replace('#archive_mode', 'archive_mode')
        data = data.replace('#archive_command', 'archive_command')
        data = data.replace('#wal_level', 'wal_level')
        data = data.replace('#max_wal_senders', 'max_wal_senders')
        data = data.replace('#wal_sender_timeout', 'wal_sender_timeout')
    else:
        data = data.replace('archive_mode', '#archive_mode')
        data = data.replace('archive_command', '#archive_command')
        data = data.replace('wal_level', '#wal_level')
        data = data.replace('max_wal_senders', '#max_wal_senders')
        data = data.replace('wal_sender_timeout', '#wal_sender_timeout')

    mw.writeFile(pg_conf, data)
    restart(version)
    return mw.returnJson(True, '设置成功')


def setSlaveStatus(version):
    pg_conf = getServerDir() + "/data/postgresql.conf"
    data = mw.readFile(pg_conf)
    if data.find('#hot_standby') > -1:
        data = data.replace('#hot_standby', 'hot_standby')
        data = data.replace('#primary_conninfo', 'primary_conninfo')
        data = data.replace('#max_standby_streaming_delay',
                            'max_standby_streaming_delay')
        data = data.replace('#wal_receiver_status_interval',
                            'wal_receiver_status_interval')
        data = data.replace('#hot_standby_feedback', 'hot_standby_feedback')
        data = data.replace('#recovery_target_timeline',
                            'recovery_target_timeline')
    else:
        data = data.replace('hot_standby', '#hot_standby')
        data = data.replace('primary_conninfo', '#primary_conninfo')
        data = data.replace('max_standby_streaming_delay',
                            '#max_standby_streaming_delay')
        data = data.replace('wal_receiver_status_interval',
                            '#wal_receiver_status_interval')
        data = data.replace('hot_standby_feedback', '#hot_standby_feedback')
        data = data.replace('#recovery_target_timeline',
                            'recovery_target_timeline')

    mw.writeFile(pg_conf, data)

    restart(version)
    return mw.returnJson(True, '设置成功')


def getSlaveList(version=''):

    db = pgDb()

    res = db.execute('select * from pg_stat_replication')
    print(res)
    # dlist = db.query('show slave status')
    # ret = []
    # for x in range(0, len(dlist)):
    #     tmp = {}
    #     tmp['Master_User'] = dlist[x]["Master_User"]
    #     tmp['Master_Host'] = dlist[x]["Master_Host"]
    #     tmp['Master_Port'] = dlist[x]["Master_Port"]
    #     tmp['Master_Log_File'] = dlist[x]["Master_Log_File"]
    #     tmp['Slave_IO_Running'] = dlist[x]["Slave_IO_Running"]
    #     tmp['Slave_SQL_Running'] = dlist[x]["Slave_SQL_Running"]
    #     ret.append(tmp)
    data = {}
    data['data'] = []

    return mw.getJson(data)


def getSlaveSSHByIp(version=''):
    args = getArgs()
    data = checkArgs(args, ['ip'])
    if not data[0]:
        return data[1]

    ip = args['ip']

    conn = pSqliteDb('slave_id_rsa', 'pgsql_slave')
    data = conn.field('ip,port,db_user,id_rsa').where("ip=?", (ip,)).select()
    return mw.returnJson(True, 'ok', data)


def getSlaveSSHList(version=''):
    args = getArgs()
    data = checkArgs(args, ['page', 'page_size'])
    if not data[0]:
        return data[1]

    page = int(args['page'])
    page_size = int(args['page_size'])

    conn = pSqliteDb('slave_id_rsa', 'pgsql_slave')
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


def addSlaveSSH(version=''):
    import base64

    args = getArgs()
    data = checkArgs(args, ['ip'])
    if not data[0]:
        return data[1]

    ip = args['ip']
    if ip == "":
        return mw.returnJson(True, 'ok')

    data = checkArgs(args, ['port', 'id_rsa'])
    if not data[0]:
        return data[1]

    id_rsa = args['id_rsa']
    port = args['port']
    user = 'root'
    addTime = time.strftime('%Y-%m-%d %X', time.localtime())

    conn = pSqliteDb('slave_id_rsa', 'pgsql_slave')
    data = conn.field('ip,id_rsa').where("ip=?", (ip,)).select()
    if len(data) > 0:
        res = conn.where("ip=?", (ip,)).save(
            'port,id_rsa', (port, id_rsa,))
    else:
        conn.add('ip,port,user,id_rsa,ps,addtime',
                 (ip, port, user, id_rsa, '', addTime))

    return mw.returnJson(True, '设置成功!')


def delSlaveSSH(version=''):
    args = getArgs()
    data = checkArgs(args, ['ip'])
    if not data[0]:
        return data[1]

    ip = args['ip']

    conn = pSqliteDb('slave_id_rsa', 'pgsql_slave')
    conn.where("ip=?", (ip,)).delete()
    return mw.returnJson(True, 'ok')


def updateSlaveSSH(version=''):
    args = getArgs()
    data = checkArgs(args, ['ip', 'id_rsa'])
    if not data[0]:
        return data[1]

    ip = args['ip']
    id_rsa = args['id_rsa']
    conn = pSqliteDb('slave_id_rsa', 'pgsql_slave')
    conn.where("ip=?", (ip,)).save('id_rsa', (id_rsa,))
    return mw.returnJson(True, 'ok')


def getMasterRepSlaveList(version=''):
    args = getArgs()
    data = checkArgs(args, ['page', 'page_size'])
    if not data[0]:
        return data[1]

    page = int(args['page'])
    page_size = int(args['page_size'])
    data = {}

    conn = pSqliteDb('master_replication_user')
    limit = str((page - 1) * page_size) + ',' + str(page_size)

    field = 'id,username,password,accept,ps,addtime'
    clist = conn.field(field).limit(limit).order('id desc').select()
    count = conn.count()

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
    data = checkArgs(args, ['username', 'password', 'address'])
    if not data[0]:
        return data[1]

    address = args['address'].strip()
    username = args['username'].strip()
    password = args['password'].strip()

    if len(password) < 1:
        password = mw.md5(time.time())[0:8]

    if not re.match(r"^[\w\.-]+$", username):
        return mw.returnJson(False, '用户名不能带有特殊符号!')
    checks = ['root', 'mysql', 'test', 'sys', 'panel_logs']
    if username in checks or len(username) < 1:
        return mw.returnJson(False, '用户名不合法!')
    if password in checks or len(password) < 1:
        return mw.returnJson(False, '密码不合法!')

    pdb = pgDb()
    psdb = pSqliteDb('master_replication_user')

    if psdb.where("username=?", (username)).count() > 0:
        return mw.returnJson(False, '用户已存在!')

    sql = "CREATE ROLE " + username + " login replication password '" + password + "'"
    pdb.execute(sql)

    pg_conf = pgHbaConf()
    data = mw.readFile(pg_conf)

    data = data + "\nhost   replication  " + \
        username + "   " + address + "     md5"

    mw.writeFile(pg_conf, data)

    addTime = time.strftime('%Y-%m-%d %X', time.localtime())
    psdb.add('username,password,accept,ps,addtime',
             (username, password, address, '', addTime))
    return mw.returnJson(True, '添加成功!')


def delMasterRepSlaveUser(version=''):
    args = getArgs()
    data = checkArgs(args, ['username'])
    if not data[0]:
        return data[1]

    name = args['username']

    pdb = pgDb()
    psdb = pSqliteDb('master_replication_user')

    pdb.execute("drop user " + name)

    pg_hba = pgHbaConf()
    old_config = mw.readFile(pg_hba)
    new_config = re.sub(
        r'host\s*replication\s*{}.*'.format(name), '', old_config).strip()
    mw.writeFile(pg_hba, new_config)

    psdb.where("username=?", (args['username'],)).delete()
    return mw.returnJson(True, '删除成功!')


def getMasterRepSlaveUserCmd(version=''):
    args = getArgs()
    data = checkArgs(args, ['username', 'db'])
    if not data[0]:
        return data[1]

    psdb = pSqliteDb('master_replication_user')
    mdir = getServerDir()
    port = getPgPort()
    localIp = mw.getLocalIp()
    f = 'username,password'
    username = args['username']
    if username == '':
        clist = psdb.field(f).limit('1').order('id desc').select()
    else:
        clist = psdb.field(f).where(
            "username=?", (username,)).order('id desc').select()

    if len(clist) == 0:
        return mw.returnJson(False, '请添加同步账户!')

    cmd = 'echo "' + clist[0]['password'] + '" | ' + mdir + '/bin/pg_basebackup -Fp --progress -D ' + mdir + \
        '/postgresql/data -h ' + localIp + ' -p ' + port + \
        ' -U ' + clist[0]['username'] + ' --password'

    data = {}
    data['cmd'] = cmd
    data['info'] = clist
    return mw.returnJson(True, 'ok!', data)


def slaveSyncCmd(version=''):
    data = {}
    data['cmd'] = 'cd /www/server/mdserver-web && python3 plugins/postgresql/index.py do_full_sync'
    return mw.returnJson(True, 'ok!', data)


def writeDbSyncStatus(data):
    path = '/tmp/db_async_status.txt'
    mw.writeFile(path, json.dumps(data))


def doFullSync(version=''):

    db = pgDb()

    id_rsa_conn = pSqliteDb('slave_id_rsa', 'pgsql_slave')
    data = id_rsa_conn.field('ip,port,db_user,id_rsa').find()

    SSH_PRIVATE_KEY = "/tmp/pg_sync_id_rsa.txt"
    id_rsa = data['id_rsa'].replace('\\n', '\n')
    mw.writeFile(SSH_PRIVATE_KEY, id_rsa)

    ip = data["ip"]
    master_port = data['port']
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

    print("同步文件", "start")
    t = ssh.get_transport()
    sftp = paramiko.SFTPClient.from_transport(t)
    copy_status = sftp.get(
        "/www/server/postgresql/pgsql.db", getServerDir() + "/pgsql.db")
    print("同步信息:", copy_status)
    print("同步文件", "end")
    if copy_status == None:
        writeDbSyncStatus({'code': 2, 'msg': '数据库信息同步本地完成...', 'progress': 40})

    cmd = 'cd /www/server/mdserver-web && python3 plugins/postgresql/index.py get_master_rep_slave_user_cmd {"username":"","db":""}'
    stdin, stdout, stderr = ssh.exec_command(cmd)
    result = stdout.read()
    result = result.decode('utf-8')
    cmd_data = json.loads(result)

    print(cmd_data)
    username = cmd_data['data']['info'][0]['username']
    password = cmd_data['data']['info'][0]['password']

    writeDbSyncStatus({'code': 3, 'msg': '数据库获取完成...', 'progress': 45})

    mdir = getServerDir()
    port = getPgPort()

    cmd = mdir + '/bin/pg_basebackup -Fp --progress -D ' + mdir + \
        '/postgresql/data -h ' + ip + ' -p ' + port + \
        ' -U ' + username + ' --password'
    print(cmd)

    cmd_tmp = "/tmp/cmd_run.sh"

    cmd_tmp_data = """#!/bin/expect
spawn %s
expect "Password:"
 
send "%s\r"

interact
""" % (cmd, password)

    mw.writeFile(cmd_tmp, cmd_tmp_data)

    os.system("expect " + cmd_tmp)

    writeDbSyncStatus({'code': 6, 'msg': '从库重启完成...', 'progress': 100})

    os.system("rm -rf " + SSH_PRIVATE_KEY)
    os.system("rm -rf " + cmd_tmp)
    return True


def installPreInspection(version):
    return 'ok'


def uninstallPreInspection(version):
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
    elif func == 'pg_hba_conf':
        print(pgHbaConf())
    elif func == 'config_tpl':
        print(configTpl())
    elif func == 'read_config_tpl':
        print(readConfigTpl())
    elif func == 'run_info':
        print(runInfo())
    elif func == 'run_log':
        print(runLog())
    elif func == 'slow_log':
        print(getSlowLog())
    elif func == 'db_status':
        print(pgDbStatus())
    elif func == 'set_db_status':
        print(pgSetDbStatus())
    elif func == 'set_user_pwd':
        print(setUserPwd())
    elif func == 'pg_port':
        print(getPgPort())
    elif func == 'set_pg_port':
        print(setPgPort())
    elif func == 'root_pwd':
        print(rootPwd())
    elif func == 'get_db_list':
        print(getDbList())
    elif func == 'add_db':
        print(addDb())
    elif func == 'del_db':
        print(delDb())
    elif func == 'set_db_rw':
        print(setDbRw(version))
    elif func == 'get_db_access':
        print(getDbAccess())
    elif func == 'set_db_access':
        print(setDbAccess())
    elif func == 'pg_back':
        print(pgBack())
    elif func == 'pg_back_list':
        print(pgBackList())
    elif func == 'import_db_backup':
        print(importDbBackup())
    elif func == 'delete_db_backup':
        print(deleteDbBackup())
    elif func == 'sync_get_databases':
        print(syncGetDatabases())
    elif func == 'add_slave_ssh':
        print(addSlaveSSH(version))
    elif func == 'get_slave_list':
        print(getSlaveList(version))
    elif func == 'del_slave_ssh':
        print(delSlaveSSH(version))
    elif func == 'update_slave_ssh':
        print(updateSlaveSSH(version))
    elif func == 'get_slave_ssh_list':
        print(getSlaveSSHList(version))
    elif func == 'get_slave_ssh_by_ip':
        print(getSlaveSSHByIp(version))
    elif func == 'get_master_status':
        print(getMasterStatus(version))
    elif func == 'set_master_status':
        print(setMasterStatus(version))
    elif func == 'set_slave_status':
        print(setSlaveStatus(version))
    elif func == 'get_master_rep_slave_list':
        print(getMasterRepSlaveList(version))
    elif func == 'add_master_rep_slave_user':
        print(addMasterRepSlaveUser(version))
    elif func == 'del_master_rep_slave_user':
        print(delMasterRepSlaveUser(version))
    elif func == 'get_master_rep_slave_user_cmd':
        print(getMasterRepSlaveUserCmd(version))
    elif func == 'slave_sync_cmd':
        print(slaveSyncCmd(version))
    elif func == 'do_full_sync':
        print(doFullSync(version))
    else:
        print('error')
