# coding:utf-8

import sys
import io
import os
import time
import subprocess
import re
import json

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
        t = args[0].strip().strip('{}').strip()
        if t == '':
            return tmp
        arg_t = t.split(',')
        for i in range(len(arg_t)):
            kv = arg_t[i].split(':', 1)
            if len(kv) < 2:
                continue
            tmp[kv[0].strip().strip('"\'')] = kv[1].strip().strip('"\'')
    elif args_len > 1:
        for i in range(len(args)):
            kv = args[i].strip().strip('{}').split(':', 1)
            if len(kv) < 2:
                continue
            tmp[kv[0].strip().strip('"\'')] = kv[1].strip().strip('"\'')

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


def getImportDir():
    import_dir = mw.getBackupDir() + '/postgresql_import'
    if not os.path.exists(import_dir):
        os.makedirs(import_dir)
    return import_dir

def getDataDir():
    path = getServerDir() + '/data'
    return path

def getBakInitConf():
    path = getServerDir() + '/data.init/postgresql.conf'
    if os.path.exists(path):
        return path
    return path

def getConf():
    path = getServerDir() + '/data/postgresql.conf'
    if os.path.exists(path):
        return path
    return getBakInitConf()


def configTpl():
    clist = []
    app_dir = getServerDir()
    clist.append(app_dir + "/data/postgresql.conf")
    return mw.getJson(clist)


def pgHbaConf():
    return getServerDir() + "/data/pg_hba.conf"


def hbaRule(conn_type, database, user, address, method):
    '''
    按 conf/pg_hba.conf 的列宽(8/16/16/24)输出一条认证规则, 便于观察
    '''
    if address == '':
        return "{:<8}{:<16}{:<40}{}".format(conn_type, database, user, method)
    return "{:<8}{:<16}{:<16}{:<24}{}".format(
        conn_type, database, user, address, method)


def getHbaAccess(name):
    '''
    从 pg_hba.conf 读取数据库或用户为 name 的规则的 ADDRESS, 后写入的优先
    '''
    accept = ''
    content = mw.readFile(pgHbaConf()) or ''
    for line in content.splitlines():
        fields = line.split()
        # TYPE  DATABASE  USER  ADDRESS  METHOD
        if len(fields) < 5 or fields[0] != 'host':
            continue
        if name not in (fields[1], fields[2]):
            continue
        accept = fields[3]
    return accept


def setHbaAccess(name, access, user=''):
    '''
    删除数据库或用户为 name 的规则后写入新规则, 仅修改 pg_hba.conf
    '''
    lines = []
    for line in mw.readFile(pgHbaConf()).splitlines():
        fields = line.split()
        if len(fields) >= 5 and fields[0] == 'host' and name in (fields[1], fields[2]):
            continue
        lines.append(line)

    if user == '':
        user = name
    data = "\n".join(lines).strip()
    data += "\n" + hbaRule('host', name, user, access, 'scram-sha-256')
    mw.writeFile(pgHbaConf(), data)


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
    # libpq 中 host 以 / 开头时按 socket 目录处理，会自动查找 .s.PGSQL.<port>
    sock_name = '.s.PGSQL.' + getDbPort()
    for sock_dir in ['/tmp', getServerDir()]:
        if os.path.exists(sock_dir + '/' + sock_name):
            return sock_dir
    # 未找到 socket，返回空字符串让 ORM 走 TCP
    return ""


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


def readActiveConf(path):
    '''
    读取 postgresql.conf 中已生效(非注释)的配置项, 同名以最后一项为准
    '''
    conf = {}
    if not os.path.exists(path):
        return conf
    for line in mw.readFile(path).splitlines():
        line = line.strip()
        if line == '' or line.startswith('#') or '=' not in line:
            continue
        conf[line.split('=', 1)[0].strip()] = line
    return conf


def regenConfig():
    '''
    按模板重新生成配置, 已安装的实例在 restart 前同步一次:
    postgresql.conf 保留当前已生效的配置值
    pg_hba.conf 追加数据表中已有数据库、复制用户的访问规则
    '''
    # postgresql.conf
    path = getServerDir() + '/data/postgresql.conf'
    current = readActiveConf(path)
    tpl = contentReplace(mw.readFile(getPluginDir() + '/conf/postgresql.conf'))
    tpl_keys = set(re.findall(r'^\s*#?\s*([\w.]+)\s*=', tpl, re.M))

    lines = []
    used = set()
    for line in tpl.splitlines():
        match = re.match(r'^\s*#?\s*([\w.]+)\s*=', line)
        key = match.group(1) if match else ''
        if key == '' or key not in current or key in used:
            lines.append(line)
            continue
        # 用当前生效值覆盖模板中的默认值/注释项
        lines.append(current[key])
        used.add(key)

    for key in current:
        if key not in tpl_keys and key not in used:
            lines.append(current[key])
    mw.writeFile(path, "\n".join(lines) + "\n")

    # pg_hba.conf
    pg_accept = getHbaAccess('postgres')
    lines = []
    for line in mw.readFile(getPluginDir() + '/conf/pg_hba.conf').splitlines():
        fields = line.split()
        # 管理员规则单独处理, 从当前配置中取值后统一追加
        if len(fields) >= 5 and fields[0] == 'host' and 'postgres' in (fields[1], fields[2]):
            continue
        lines.append(line)

    rules = []
    rules.append(hbaRule('host', 'postgres', 'postgres', pg_accept, 'scram-sha-256'))
    for item in pSqliteDb('databases').field('name,username,accept').select():
        if item['accept']:
            rules.append(hbaRule('host', item['name'], item['username'],
                                 item['accept'], 'scram-sha-256'))

    for item in pSqliteDb('master_replication_user').field('username,accept').select():
        if item['accept']:
            rules.append(hbaRule('host', 'replication', item['username'],
                                 item['accept'], 'scram-sha-256'))

    if pg_accept == '':
        pg_accept = '127.0.0.1/32'

    lines.append('')
    lines.extend(rules)
    mw.writeFile(pgHbaConf(), "\n".join(lines) + "\n")
    return True


def isSlaveDb():
    standby = getDataDir()+"/standby.signal"
    if os.path.exists(standby):
        return True
    return False

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

def status_proccess(version=''):
    data = mw.execShell(
        "ps -ef|grep bin/postgres |grep -v grep | grep -v python | grep -v mdserver-web | awk '{print $2}'")
    if data[0] == '':
        return 'stop'
    return 'start'

def status(version=''):
    pid = getServerDir() + "/data/postmaster.pid"
    if os.path.exists(pid):
        return 'start'
    return 'stop'

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

            # 启用 pg_stat_statements 扩展
            try:
                db = pgDb()
                r = db.execute("CREATE EXTENSION IF NOT EXISTS pg_stat_statements")
                if isinstance(r, Exception):
                    print("CREATE EXTENSION pg_stat_statements: {}".format(r))
            except Exception as e:
                print("init pg_stat_statements failed: {}".format(e))

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
        # print(method + ":" + str(e))
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
    if not isSlaveDb():
        regenConfig()
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
    appCMD("", 'restart')
    return mw.returnJson(True, '编辑成功!')


def runInfo():
    if status(version) == 'stop':
        return mw.returnJson(False, 'PG未启动', [])

    db = pgDb()
    try:
        data = db.query("""
            SELECT
                extract(epoch FROM pg_postmaster_start_time())::bigint,
                extract(epoch FROM now() - pg_postmaster_start_time())::bigint,
                (SELECT count(*) FROM pg_stat_activity
                 WHERE backend_type = 'client backend' AND pid <> pg_backend_pid()),
                (SELECT count(*) FROM pg_stat_activity
                 WHERE backend_type = 'client backend' AND state = 'active'
                   AND pid <> pg_backend_pid()),
                (SELECT setting::int FROM pg_settings WHERE name = 'max_connections'),
                (SELECT count(*) FROM pg_stat_activity),
                coalesce(sum(xact_commit), 0)::bigint,
                coalesce(sum(xact_rollback), 0)::bigint,
                coalesce(sum(tup_returned), 0)::bigint,
                coalesce(sum(tup_fetched), 0)::bigint,
                coalesce(sum(tup_inserted), 0)::bigint,
                coalesce(sum(tup_updated), 0)::bigint,
                coalesce(sum(tup_deleted), 0)::bigint,
                coalesce(sum(blks_read), 0)::bigint,
                coalesce(sum(blks_hit), 0)::bigint,
                coalesce(sum(temp_files), 0)::bigint,
                coalesce(sum(temp_bytes), 0)::bigint,
                coalesce(sum(deadlocks), 0)::bigint,
                coalesce(sum(conflicts), 0)::bigint,
                (SELECT pg_size_pretty(sum(pg_database_size(datname))::bigint)
                 FROM pg_database WHERE datallowconn AND NOT datistemplate)
            FROM pg_stat_database
        """)
    except Exception as e:
        data = e
    if isinstance(data, Exception):
        return mw.returnJson(False, str(data), [])
    if not data:
        return mw.returnJson(False, '获取PG运行状态失败', [])

    row = data[0]
    result = {
        'run': row[0],
        'run_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(row[0])),
        'uptime': row[1],
        'connections': row[2],
        'threads_running': row[3],
        'max_connections': row[4],
        'progress_num': row[5],
        'com_commit': row[6],
        'com_rollback': row[7],
        'tup_returned': row[8],
        'tup_fetched': row[9],
        'tup_inserted': row[10],
        'tup_updated': row[11],
        'tup_deleted': row[12],
        'blks_read': row[13],
        'blks_hit': row[14],
        'temp_files': row[15],
        'temp_bytes': row[16],
        'deadlocks': row[17],
        'conflicts': row[18],
        'pg_size': row[19],
        'file': 'OFF',
        'position': 'OFF',
        'pid': '-',
        'pg_mem': '-',
        'replication': {
            'role': 'unknown',
            'status': '-',
            'replica_count': 0,
            'replicas': [],
        },
    }

    replication = result['replication']
    in_recovery = None
    try:
        recovery = db.query('SELECT pg_is_in_recovery()')
        if not isinstance(recovery, Exception) and recovery:
            in_recovery = recovery[0][0]
            replication['role'] = 'standby' if in_recovery else 'primary'
    except Exception:
        pass

    if in_recovery is not None:
        try:
            if in_recovery:
                wal = db.query("""
                    SELECT '-', coalesce(pg_last_wal_replay_lsn()::text, '-')
                """)
            else:
                wal = db.query("""
                    SELECT coalesce(pg_walfile_name(lsn), 'OFF'), coalesce(lsn::text, 'OFF')
                    FROM (SELECT pg_current_wal_lsn() AS lsn) AS wal
                """)
            if not isinstance(wal, Exception) and wal:
                result['file'] = wal[0][0]
                result['position'] = wal[0][1]
        except Exception:
            pass

    if in_recovery:
        try:
            standby = db.query("""
                SELECT
                    (SELECT status FROM pg_stat_wal_receiver LIMIT 1),
                    (SELECT sender_host::text FROM pg_stat_wal_receiver LIMIT 1),
                    (SELECT sender_port FROM pg_stat_wal_receiver LIMIT 1),
                    (SELECT slot_name FROM pg_stat_wal_receiver LIMIT 1),
                    coalesce(pg_last_wal_receive_lsn()::text, '-'),
                    coalesce(pg_last_wal_replay_lsn()::text, '-'),
                    extract(epoch FROM now() - pg_last_xact_replay_timestamp())::bigint
            """)
            if not isinstance(standby, Exception) and standby:
                info = standby[0]
                replication.update({
                    'status': info[0] or '-',
                    'sender_host': info[1] or '-',
                    'sender_port': info[2] or '-',
                    'slot_name': info[3] or '-',
                    'receive_lsn': info[4],
                    'replay_lsn': info[5],
                    'replay_lag': info[6],
                })
                result['position'] = info[5]
        except Exception:
            pass
    elif in_recovery is False:
        try:
            replicas = db.query("""
                SELECT coalesce(application_name, '-'),
                       coalesce(host(client_addr), '本地'),
                       coalesce(state, '-'), coalesce(sync_state, '-'),
                       coalesce(sent_lsn::text, '-'),
                       coalesce(replay_lsn::text, '-'),
                       extract(epoch FROM replay_lag)::bigint
                FROM pg_stat_replication
                ORDER BY application_name, client_addr
            """)
            if not isinstance(replicas, Exception):
                for replica in replicas:
                    replication['replicas'].append({
                        'name': replica[0],
                        'address': replica[1],
                        'state': replica[2],
                        'sync_state': replica[3],
                        'sent_lsn': replica[4],
                        'replay_lsn': replica[5],
                        'replay_lag': replica[6],
                    })
                replication['replica_count'] = len(replication['replicas'])
        except Exception:
            pass

    pid_content = mw.readFile(getDataDir() + '/postmaster.pid')
    pid_lines = pid_content.splitlines() if pid_content else []
    if pid_lines:
        pid = pid_lines[0].strip()
        result['pid'] = pid
        process_status = mw.readFile('/proc/{}/status'.format(pid))
        if process_status:
            vm_rss = re.search(r'^VmRSS:\s*(.+?)\s*$', process_status, re.M)
            if vm_rss:
                result['pg_mem'] = vm_rss.group(1)

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


# 物理内存(MB)与推荐配置对照
PG_MEMORY_PROFILES = [
    {'memory': 2, 'shared_buffers': '512MB', 'effective_cache_size': '1GB',
     'maintenance_work_mem': '64MB', 'work_mem': '2MB', 'temp_buffers': '4MB'},
    {'memory': 4, 'shared_buffers': '1GB', 'effective_cache_size': '3GB',
     'maintenance_work_mem': '128MB', 'work_mem': '4MB', 'temp_buffers': '8MB'},
    {'memory': 8, 'shared_buffers': '2GB', 'effective_cache_size': '6GB',
     'maintenance_work_mem': '256MB', 'work_mem': '8MB', 'temp_buffers': '8MB'},
    {'memory': 16, 'shared_buffers': '4GB', 'effective_cache_size': '12GB',
     'maintenance_work_mem': '512MB', 'work_mem': '16MB', 'temp_buffers': '16MB'},
    {'memory': 24, 'shared_buffers': '6GB', 'effective_cache_size': '18GB',
     'maintenance_work_mem': '768MB', 'work_mem': '16MB', 'temp_buffers': '16MB'},
    {'memory': 32, 'shared_buffers': '8GB', 'effective_cache_size': '24GB',
     'maintenance_work_mem': '1GB', 'work_mem': '24MB', 'temp_buffers': '32MB'},
    {'memory': 48, 'shared_buffers': '8GB', 'effective_cache_size': '36GB',
     'maintenance_work_mem': '1536MB', 'work_mem': '32MB', 'temp_buffers': '32MB'},
    {'memory': 64, 'shared_buffers': '8GB', 'effective_cache_size': '48GB',
     'maintenance_work_mem': '2GB', 'work_mem': '32MB', 'temp_buffers': '32MB'},
    {'memory': 96, 'shared_buffers': '8GB', 'effective_cache_size': '72GB',
     'maintenance_work_mem': '3GB', 'work_mem': '48MB', 'temp_buffers': '64MB'},
    {'memory': 128, 'shared_buffers': '8GB', 'effective_cache_size': '96GB',
     'maintenance_work_mem': '4GB', 'work_mem': '64MB', 'temp_buffers': '64MB'},
]

PG_PERF_PARAMS = [
    ('shared_buffers', '共享缓冲区', 'memory', 'MB',
     'PG通过shared_buffers和内核和磁盘打交道，通常设置为实际内存的25%.'),
    ('effective_cache_size', '系统缓存大小', 'memory', 'GB',
     'PG能够使用的最大缓存,比如4G的内存，可以设置为3GB.'),
    ('maintenance_work_mem', '维护工作内存', 'memory', 'MB',
     'VACUUM、CREATE INDEX 等维护操作可用的最大内存.'),
    ('work_mem', '工作内存', 'memory', 'MB',
     '增加work_mem有助于提高排序的速度。通常设置为实际RAM的2%-4%.'),
    ('temp_buffers', '临时缓冲区', 'memory', 'MB',
     '设置每个数据库会话使用的临时缓冲区的最大数目，默认是8MB'),
    ('max_connections', '最大连接数', 'number', '', '最大连接数'),
    ('max_prepared_transactions', '最大预备事务数', 'number', '',
     '设置可以同时处于 prepared 状态的事务的最大数目'),
    ('max_stack_depth', '最大堆栈深度', 'memory', 'MB',
     '指定服务器的执行堆栈的最大安全深度，默认是2MB'),
    ('bgwriter_lru_maxpages', '后台写脏页上限', 'number', '',
     '一个周期最多写多少脏页'),
    ('max_worker_processes', '最大工作进程数', 'number', '',
     '如果要使用worker process, 最多可以允许fork 多少个worker进程.'),
]

PG_MEMORY_UNITS = {
    'KB': 1024,
    'MB': 1024 * 1024,
    'GB': 1024 * 1024 * 1024,
    'TB': 1024 * 1024 * 1024 * 1024,
}


def getPgTotalMemory():
    try:
        if os.path.exists('/proc/meminfo'):
            with open('/proc/meminfo') as f:
                for line in f:
                    if line.startswith('MemTotal:'):
                        return int(line.split()[1]) // 1024
    except Exception:
        pass

    try:
        info = mw.execShell('sysctl -n hw.memsize')
        if info and info[0].strip().isdigit():
            return int(info[0].strip()) // (1024 * 1024)
    except Exception:
        pass
    return 0


def parsePgMemory(value):
    '''
    将 128MB、1GB、1.5GB 解析为 MB
    '''
    result = re.match(r'^(\d+(?:\.\d+)?)\s*([kKmMgGtT]?[bB])?$', str(value).strip())
    if not result:
        return None
    unit = (result.group(2) or 'MB').upper()
    byte_size = float(result.group(1)) * PG_MEMORY_UNITS[unit]
    return int(byte_size // PG_MEMORY_UNITS['MB'])


def formatPgMemory(mb):
    if mb >= 1024:
        gb = mb / 1024.0
        if gb == int(gb):
            gb = int(gb)
        return str(gb), 'GB'
    return str(int(mb)), 'MB'


def readPgConf():
    '''
    读取 postgresql.conf，活动配置优先，未开启时取注释中的默认值
    '''
    path = getServerDir() + "/data/postgresql.conf"
    if not os.path.exists(path):
        return {}

    active, commented = {}, {}
    with open(path) as f:
        for raw in f:
            line = raw.strip()
            if not line or '=' not in line:
                continue

            is_comment = line.startswith('#')
            if is_comment:
                line = line.lstrip('#').strip()

            name, value = line.split('=', 1)
            name = name.strip()
            value = value.split('#', 1)[0].strip()
            if not re.match(r'^[a-z_][a-z0-9_]*$', name) or not value:
                continue

            if is_comment:
                commented.setdefault(name, value)
            else:
                active[name] = value

    data = dict(commented)
    data.update(active)
    return data


def pgDbStatus():
    conf = readPgConf()
    if not conf:
        return mw.getJson({'status': False, 'msg': '未找到 postgresql.conf 配置文件'})

    params = []
    for name, label, ptype, default_unit, desc in PG_PERF_PARAMS:
        raw = conf.get(name, '')
        value, unit = '', ''
        if ptype == 'memory':
            mb = parsePgMemory(raw)
            if mb is None:
                unit = default_unit
            else:
                value, unit = formatPgMemory(mb)
        elif raw:
            value = raw

        params.append({
            'name': name,
            'label': label,
            'type': ptype,
            'value': value,
            'unit': unit,
            'desc': desc,
        })

    data = {
        'status': True,
        'total_memory': getPgTotalMemory(),
        'profiles': PG_MEMORY_PROFILES,
        'params': params,
    }
    return mw.getJson(data)


def sedConf(name, val):
    path = getServerDir() + "/data/postgresql.conf"
    active_pattern = re.compile(r'^\s*' + re.escape(name) + r'\s*=')
    item_pattern = re.compile(r'^\s*#?\s*' + re.escape(name) + r'\s*=')

    with open(path) as f:
        lines = f.readlines()

    active_indexes = [i for i, line in enumerate(lines) if active_pattern.match(line)]
    commented_indexes = [i for i, line in enumerate(lines) if item_pattern.match(line) and i not in active_indexes]

    # 优先替换已生效的配置，避免被后面的同名配置覆盖
    target = None
    if active_indexes:
        target = active_indexes[0]
    elif commented_indexes:
        target = commented_indexes[0]

    if target is not None:
        lines[target] = "{} = {}\n".format(name, val)
        # 去掉重复的生效配置，保证写入的值生效
        for index in reversed(active_indexes[1:]):
            del lines[index]
    else:
        if lines and not lines[-1].endswith('\n'):
            lines[-1] += '\n'
        lines.append("{} = {}\n".format(name, val))

    mw.writeFile(path, ''.join(lines))
    return True


def pgSetDbStatus():
    '''
    保存pgsql性能调整信息
    '''
    names = [p[0] for p in PG_PERF_PARAMS]
    args = getArgs()
    provided = [name for name in names if name in args]
    if not provided:
        return mw.returnJson(False, '没有需要保存的配置参数!')

    memory_names = set(p[0] for p in PG_PERF_PARAMS if p[2] == 'memory')
    for name in provided:
        value = args[name].strip()
        if name in memory_names:
            if not re.match(r'^\d+(?:\.\d+)?\s*(?:kB|MB|GB|TB)$', value, re.I):
                return mw.returnJson(False, '参数({})的值不合法: {}'.format(name, value))
        elif not re.match(r'^\d+$', value):
            return mw.returnJson(False, '参数({})必须是整数: {}'.format(name, value))

    for name in provided:
        sedConf(name, args[name].strip())

    if status() == 'start':
        restart()
        return mw.returnJson(True, '设置成功，数据库已重启!')
    return mw.returnJson(True, '设置成功，将在数据库下次启动时生效!')


def isPgError(msg):
    # 检测数据库执行错误
    msg = str(msg)
    if "failed" in msg:
        return mw.returnJson(False, '数据库连接失败,请检查数据库服务是否启动!')
    return None

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

    head = "cd "+mw.getPanelDir()
    cmd = head +' && . bin/activate &&  python3 plugins/postgresql/scripts/backup.py database ' + args['name'] + ' 3'
    os.system(cmd)
    return mw.returnJson(True, 'ok')

def rootPwd():
    return pSqliteDb('config').where('id=?', (1,)).getField('pg_root')

def openPgTrust():
    '''
    临时放开本地连接认证, 用于重置密码
    '''
    hba = pgHbaConf()
    content = mw.readFile(hba) or ''
    backup = hba + '.bak'
    # 保留首次备份, 避免中途失败时丢失原始认证配置
    if not os.path.exists(backup):
        mw.writeFile(backup, content)

    trust = hbaRule('local', 'all', 'all', '', 'trust') + "\n" \
            + hbaRule('host', 'all', 'all', '127.0.0.1/32', 'trust') + "\n" \
            + hbaRule('host', 'all', 'all', '::1/128', 'trust') + "\n"
    mw.writeFile(hba, trust + content)
    return True


def closePgTrust():
    '''
    恢复 pg_hba.conf 本地认证
    '''
    hba = pgHbaConf()
    backup = hba + '.bak'
    if os.path.exists(backup):
        mw.writeFile(hba, mw.readFile(backup))
        os.remove(backup)
    # pg_hba.conf 无需重启, 重新加载即可
    return True


def resetPgPwd(version, new_password=''):
    '''
    通过本地信任连接重置 postgres 用户密码
    '''
    pwd = new_password if new_password != '' else mw.getRandomString(16)

    tmp_dir = getServerDir() + '/tmp'
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)
    sql_file = tmp_dir + '/reset_pwd.sql'
    mw.writeFile(sql_file, "alter user postgres with password '{}';\n".format(
        pwd.replace("'", "''")))
    os.chmod(sql_file, 0o644)

    cmd = getServerDir() + '/bin/psql -d postgres -f ' + sql_file
    if not mw.isAppleSystem():
        cmd = pgCmd(cmd)
    data = mw.execShell(cmd)

    try:
        os.remove(sql_file)
    except Exception:
        pass

    output = (data[0] or '') + (data[1] or '')
    if 'ALTER ROLE' in output:
        pSqliteDb('config').where('id=?', (1,)).save('pg_root', (pwd,))
        return True
    return False


def setRootPwdForce(new_password, version=''):
    '''
    当前密码不可用(忘记密码/连接被拒)时, 通过临时放开本地认证的方式真正重置密码
    '''
    changed = False
    try:
        appCMD(version, 'stop')
        openPgTrust()
        appCMD(version, 'start')
        time.sleep(3)

        changed = resetPgPwd(version, new_password)
    except Exception:
        changed = False
    finally:
        # 无论成败都恢复本地认证, 避免数据库长期处于免密状态
        closePgTrust()
        appCMD(version, 'restart')

    if not changed:
        return False

    # 用新密码验证是否真的可以连接(启动可能较慢, 重试几次)
    for i in range(10):
        try:
            pdb = pgDb()
            result = pdb.query('select 1')
            if not isinstance(result, Exception) and not (isinstance(result, str) and result.startswith('error')):
                return True
        except Exception:
            pass
        time.sleep(2)

    return False

def setPostgresPwd(version=''):
    args = getArgs()
    data = checkArgs(args, ['password'])
    if not data[0]:
        return data[1]
    password = args['password']

    if 'force' in args and args['force'] == '1':
        pSqliteDb('config').where('id=?', (1,)).save('pg_root', (password,))
        return mw.returnJson(True, '【强制本地记录】PG密码修改成功!')

    # 忘记密码/连接被拒时, 临时放开本地认证重置
    if 'force' in args and args['force'] == '2':
        if not setRootPwdForce(password, version):
            return mw.returnJson(False, '【强制】修改失败,请检查PG运行状态!')
        return mw.returnJson(True, '【强制】postgres密码修改成功!')

    try:
        pdb = pgDb()
        result = pdb.execute("alter user postgres with password '{}'".format(password.replace("'", "''")))
        if isinstance(result, Exception):
            return mw.returnJson(False, '修改密码失败,请检查数据库连接状态!')
    except Exception as ex:
        return mw.returnJson(False, '修改密码失败[' + str(ex) + ']')

    pSqliteDb('config').where('id=?', (1,)).save('pg_root', (password,))
    return mw.returnJson(True, 'postgres密码修改成功!')

def importDbExternal():
    args = getArgs()
    data = checkArgs(args, ['file', 'name'])
    if not data[0]:
        return data[1]

    file = args['file']
    name = args['name']

    import_dir = getImportDir() + '/'

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

    psql = getServerDir() + '/bin/psql'
    if not os.path.exists(psql):
        psql = 'psql'
    port = getPgPort()

    psql_cmd = '{} -U postgres -d {} -p {}'.format(psql, name, port)
    if not mw.isAppleSystem():
        psql_cmd = 'su - postgres -c "{}"'.format(psql_cmd)

    cmd = '{} < "{}"'.format(psql_cmd, import_sql)
    rdata = mw.execShell(cmd)

    if ext != 'sql' and os.path.exists(import_sql):
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

    cmd = 'cd ' + mw.getPanelDir() + ' && . bin/activate && '
    cmd += 'python3 ' + mw.getPanelDir() + '/plugins/postgresql/index.py import_db_external_progress_bar {"file":"' + file + '","name":"' + name + '"}'
    return mw.returnJson(True, 'ok', cmd)

def importDbExternalProgressBar():
    args = getArgs()
    data = checkArgs(args, ['file', 'name'])
    if not data[0]:
        return data[1]

    file = args['file']
    name = args['name']

    import_dir = getImportDir() + '/'

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

    psql = getServerDir() + '/bin/psql'
    if not os.path.exists(psql):
        psql = 'psql'
    port = getPgPort()

    psql_cmd = '{} -U postgres -d {} -p {}'.format(psql, name, port)
    if not mw.isAppleSystem():
        psql_cmd = 'su - postgres -c "{}"'.format(psql_cmd)

    cmd = 'pv -t -p "{}" | {}'.format(import_sql, psql_cmd)
    print(cmd)
    os.system(cmd)

    if ext != 'sql' and os.path.exists(import_sql):
        os.remove(import_sql)
    return ""

def importDbBackupProgress():
    args = getArgs()
    data = checkArgs(args, ['file', 'name'])
    if not data[0]:
        return data[1]

    file = args['file']
    name = args['name']

    cmd = 'cd ' + mw.getPanelDir() + ' && . bin/activate && '
    cmd += 'python3 plugins/postgresql/index.py import_db_backup_progress_bar {"file":"' + file + '","name":"' + name + '"}'
    return mw.returnJson(True, 'ok', cmd)


def importDbBackupProgressBar():
    args = getArgs()
    data = checkArgs(args, ['file', 'name'])
    if not data[0]:
        return data[1]

    file = args['file']
    name = args['name']

    bk_path_upload = getBackupDir()
    file_path = os.path.join(bk_path_upload, file)
    if not os.path.exists(file_path):
        return '备份文件不存在'

    file_path_sql = file_path.replace('.gz', '')
    if not os.path.exists(file_path_sql):
        cmd = 'cd ' + bk_path_upload + ' && gzip -dk ' + file
        mw.execShell(cmd)

    port = getPgPort()
    psql = getServerDir() + '/bin/psql'
    if not os.path.exists(psql):
        psql = 'psql'

    cmd = 'pv -t -p {} | su - postgres -c "{} -d {} -p {}"'.format(file_path_sql, psql, name, port)
    if mw.isAppleSystem():
        cmd = 'pv -t -p {} | {} -d {} -p {}'.format(file_path_sql, psql, name, port)
       
    print(cmd)
    os.system(cmd)

    if os.path.exists(file_path_sql):
        os.unlink(file_path_sql)
    return ''

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


def getDbBackupImportList():

    bkImportDir = getImportDir()
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
        'id=?', (1,)).getField('pg_root')
    data['info'] = info

    return mw.getJson(data)

def getTableList():
    args = getArgs()
    db_name = ""
    if 'dbname' in args:
        db_name = args['dbname']
    elif 'name' in args:
        db_name = args['name']
    if db_name == "":
        return mw.returnJson(-1, "table表不能为空")

    pdb = pgDb()
    pdb.setDatabase(db_name)
    sql = "select tablename from pg_tables where schemaname not in ('pg_catalog','information_schema')"
    try:
        data = pdb.query(sql)
    except Exception as e:
        return mw.returnJson(-1, str(e))

    if isinstance(data, Exception):
        return mw.returnJson(-1, str(data))

    table_list = []
    for i in data:
        table_list.append(i[0])

    return mw.returnJson(0, "ok", table_list)

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
    # PostgreSQL 15+ 起 public schema 默认仅属主可写,需单独授权
    pdb.setDatabase(dbname)
    pdb.execute("GRANT ALL ON SCHEMA public TO {}".format(dbuser,))

    pg_hba = pgHbaConf()
    content = mw.readFile(pg_hba)
    content += "\n" + hbaRule('host', dbname, dbuser, listen_ip, 'scram-sha-256')
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

    # postgres 为内置库, 不在数据表记录, 直接读配置文件
    if name == 'postgres':
        return mw.returnJson(True, getHbaAccess(name))

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

    # postgres 为内置库, 不在数据表记录, 只改配置文件
    if name == 'postgres':
        setHbaAccess(name, access)
        restart()
        return mw.returnJson(True, "设置成功")

    psdb = pSqliteDb('databases')

    conf = pgHbaConf()
    data = mw.readFile(conf)
    new_data = re.sub(r'host\s*{}.*'.format(name), '', data).strip()

    new_data += "\n" + hbaRule('host', name, name, access, 'scram-sha-256')
    mw.writeFile(conf, new_data)

    psdb.where("name=?", (name,)).setField('accept', access)
    restart()
    return mw.returnJson(True, "设置成功")


def fixDbAccess(version):
    pdb = pgDb()
    data = pdb.query("select 1")
    isError = isPgError(data)
    if isError == None:
        return mw.returnJson(True, '正常无需修复!')

    if not setRootPwdForce(mw.getRandomString(16), version):
        return mw.returnJson(False, '密码重置失败,请检查数据库运行状态!!')
    return mw.returnJson(True, '修复成功,root密码已重置!')


def getDbInfo():
    args = getArgs()
    data = checkArgs(args, ['name'])
    if not data[0]:
        return data[1]

    db_name = args['name']
    pdb = pgDb()
    pdb.setDatabase(db_name)

    sql = """select n.nspname, c.relname, c.relkind,
                    greatest(c.reltuples, 0)::bigint,
                    pg_relation_size(c.oid),
                    pg_indexes_size(c.oid),
                    pg_total_relation_size(c.oid)
             from pg_class c
             join pg_namespace n on n.oid = c.relnamespace
             where c.relkind in ('r', 'p')
               and n.nspname not in ('pg_catalog', 'information_schema')
             order by n.nspname, c.relname"""
    try:
        tables = pdb.query(sql)
    except Exception as e:
        return mw.returnJson(-1, str(e))

    if isinstance(tables, Exception):
        return mw.returnJson(-1, str(tables))

    try:
        data_sum = pdb.query('select pg_database_size(current_database())')
    except Exception as e:
        return mw.returnJson(-1, str(e))

    if isinstance(data_sum, Exception):
        return mw.returnJson(-1, str(data_sum))

    data_size = 0
    if len(data_sum) > 0 and data_sum[0][0] is not None:
        data_size = data_sum[0][0]

    ret = {}
    ret['data_size'] = mw.toSize(data_size)
    ret['database'] = db_name

    kinds = {'r': 'table', 'p': 'partitioned table'}

    # 一次 union all 取所有表的真实行数，避免逐表新建连接
    count_map = {}
    count_sql_list = []
    for i in tables:
        count_sql_list.append(
            "select '{}' as schema_name, '{}' as table_name, count(*) from \"{}\".\"{}\"".format(
                i[0].replace("'", "''"), i[1].replace("'", "''"),
                i[0].replace('"', '""'), i[1].replace('"', '""')))
    if count_sql_list:
        count_data = pdb.query(' union all '.join(count_sql_list))
        if not isinstance(count_data, Exception):
            for row in count_data:
                count_map[(row[0], row[1])] = row[2]

    ret3 = []
    for i in tables:
        tmp = {}
        tmp['schema'] = i[0]
        tmp['table_name'] = i[1]
        tmp['type'] = kinds.get(i[2], i[2])
        tmp['rows_count'] = count_map.get((i[0], i[1]), i[3])
        tmp['data_byte'] = i[4]
        tmp['index_byte'] = i[5]
        tmp['total_byte'] = i[6]
        tmp['data_size'] = mw.toSize(i[4])
        tmp['index_size'] = mw.toSize(i[5])
        tmp['total_size'] = mw.toSize(i[6])
        ret3.append(tmp)

    ret['tables'] = ret3

    return mw.getJson(ret)

def pgBack():
    # 备份数据库 — 无锁 + 大库优化版本

    import subprocess
    import shutil

    args = getArgs()
    data = checkArgs(args, ['name'])
    if not data[0]:
        return data[1]

    bk_path_upload = getBackupDir()
    database = args['name']
    port = getPgPort()

    pg_dump = getServerDir() + '/bin/pg_dump'
    if not os.path.exists(pg_dump):
        pg_dump = 'pg_dump'

    # 检测 pg_dump 主版本, 14+ 加 --no-sync
    pg_major = 0
    try:
        out = subprocess.check_output([pg_dump, '--version'], stderr=subprocess.STDOUT)
        m = re.search(r'(\d+)', out.decode())
        if m:
            pg_major = int(m.group(1))
    except Exception:
        pass

    # 检测 pigz 并行压缩
    pigz = shutil.which('pigz')
    if pigz:
        # os.cpu_count() 跨平台, 兜底用 nproc (Linux) / sysctl (macOS)
        cpus = os.cpu_count() or 0
        if cpus <= 0:
            try:
                cpus = int(subprocess.check_output(['nproc']).strip())
            except Exception:
                try:
                    cpus = int(subprocess.check_output(['sysctl', '-n', 'hw.ncpu']).strip())
                except Exception:
                    cpus = 4
        compressor = pigz + ' -p ' + str(max(2, cpus - 1)) + ' -6'
    else:
        compressor = 'gzip -6'

    # 文件名按时间戳命名
    file_name = 'db_{}_{}.sql.gz'.format(
        database, time.strftime("%Y%m%d_%H%M%S"))
    file_path = os.path.join(bk_path_upload, file_name)

    # pg_dump 参数:
    #   -c --if-exists: DROP 语句便于覆盖恢复
    #   --serializable-deferrable: MVCC 快照一致性, 与 DDL 快照冲突时自动重试
    #   --lock-wait-timeout=30s: 等表锁最多 30 秒, 避免大 DDL 下一直阻塞
    #   --no-sync (PG 14+):    dump 完不等 fsync, 减少 I/O 等待
    dump_opts = '-c --if-exists --lock-wait-timeout=30s'
    if pg_major >= 14:
        dump_opts += ' --no-sync'

    #与从库冲突
    if not isSlaveDb():
        dump_opts += ' --serializable-deferrable'

    # set -o pipefail: 管道任一命令失败都能被检测到
    stderr_log = '/tmp/pg_dump_stderr.log'
    exit_code_file = '/tmp/pg_dump_exit_code'
    open(stderr_log, 'w').close()

    if mw.isAppleSystem():
        cmd = '''set -o pipefail && {} {} -U postgres -d {} -p {} 2>>{} | {} > "{}"; echo $? > {}'''.format(
            pg_dump, dump_opts, database, port, stderr_log, compressor, file_path, exit_code_file)
    else:
        cmd = '''set -o pipefail && su - postgres -c "{} {} -U postgres -d {} -p {}" 2>>{} | {} > "{}"; echo $? > {}'''.format(
            pg_dump, dump_opts, database, port, stderr_log, compressor, file_path, exit_code_file)

    rdata = mw.execShell(cmd)

    # 读取 stderr, pg_dump 自己的错误信息会写这里
    stderr_txt = ''
    try:
        with open(stderr_log) as f:
            stderr_txt = f.read().strip()
    except Exception:
        pass

    # 读取管道 exit code（通过 set -o pipefail, 管道任一命令失败即非零）
    exit_code = 0
    try:
        with open(exit_code_file) as f:
            exit_code = int(f.read().strip())
    except Exception:
        pass

    # 备份失败: pipefail 非零 / 文件不存在 / 文件太小
    err_hint = stderr_txt[-400:] if stderr_txt else ''
    if exit_code != 0 \
            or (not os.path.exists(file_path)) \
            or (os.path.exists(file_path) and os.path.getsize(file_path) < 200):
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass
        msg = err_hint or ('备份失败 (exit_code={})'.format(exit_code) if exit_code != 0 else '备份失败')
        return mw.returnJson(False, msg)

    return mw.returnJson(True, '备份成功!')


def pgBackList():

    args = getArgs()
    data = checkArgs(args, ['name'])
    if not data[0]:
        return data[1]

    database = "db_"+args['name']

    bk_path_upload = getBackupDir()
    file_list = os.listdir(bk_path_upload)
    data = []
    for i in file_list:

        if i.startswith(database):
            file_path = os.path.join(bk_path_upload, i)
            file_info = os.stat(file_path)
            create_time = file_info.st_ctime
            time_local = time.localtime(int(create_time))
            create_time = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
            file_size = file_info.st_size
            file_size = mw.toSize(file_size)
            data.append({"name": i, "time": create_time,
                         "size": file_size, "file": file_path})
    data.sort(key=lambda x: x['name'], reverse=True)
    return mw.returnJson(True, 'ok', data)


def importDbBackup():
    args = getArgs()
    data = checkArgs(args, ['file', 'name'])
    if not data[0]:
        return data[1]

    file = args['file']
    name = args['name']

    bk_path_upload = getBackupDir()

    file_path = os.path.join(bk_path_upload, file)
    if not os.path.exists(file_path):
        return mw.returnJson(False, '备份文件不存在')

    port = getPgPort()
    psql = getServerDir() + '/bin/psql'
    if not os.path.exists(psql):
        psql = 'psql'

    if mw.isAppleSystem():
        cmd = '''gunzip -c "{}" | {} -U postgres -d {} -p {}'''.format(
            file_path, psql, name, port)
    else:
        cmd = '''gunzip -c "{}" | su - postgres -c "{} -U postgres -d {} -p {}"'''.format(
            file_path, psql, name, port)

    # print(cmd)

    rdata = mw.execShell(cmd)
    if rdata[1].lower().find('error') > -1:
        return mw.returnJson(False, rdata[1])

    return mw.returnJson(True, '恢复数据库成功')


def deleteDbBackup():
    args = getArgs()
    data = checkArgs(args, ['filename', 'path'])
    if not data[0]:
        return data[1]

    path = args['path']

    bk_path_upload = getBackupDir()
    full_file = bk_path_upload + '/' + args['filename']
    if path != "":
        full_file = path + "/" + args['filename']
    if os.path.exists(full_file):
        os.remove(full_file)
    return mw.returnJson(True, '删除成功!')


############ 主从功能 ######################
def getMasterStatus(version=''):

    data = {}
    data['mode'] = 'classic'
    data['status'] = False
    data['slave_status'] = False
    pg_conf = getConf()
    pg_content = mw.readFile(pg_conf)

    if pg_content.find('#wal_level') > -1:
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

    field_list = ['max_replication_slots','wal_level','wal_sender_timeout','max_wal_senders']

    if data.find('#wal_level') > -1:
        # data = data.replace('#max_replication_slots', 'max_replication_slots')
        for field in field_list:
            data = data.replace('#'+field, field)
    else:
        for field in field_list:
            data = data.replace(field, '#'+field)

    mw.writeFile(pg_conf, data)
    restart(version)
    return mw.returnJson(True, '设置成功')

def openSlaveConf(version):
    pg_conf = getConf()
    data = mw.readFile(pg_conf)

    field_list = ['hot_standby','primary_conninfo','max_standby_streaming_delay',
        'wal_receiver_status_interval','hot_standby_feedback','primary_slot_name']

    for field in field_list:
        data = data.replace('#'+field, field)
    return True

def setSlaveStatus(version):
    pg_conf = getServerDir() + "/data/postgresql.conf"
    data = mw.readFile(pg_conf)

    field_list = ['hot_standby','primary_conninfo','max_standby_streaming_delay',
            'wal_receiver_status_interval','hot_standby_feedback','primary_slot_name']
    if data.find('#hot_standby') > -1:
        for field in field_list:
            data = data.replace('#'+field, field)
    else:
        for field in field_list:
            data = data.replace(field, '#'+field)
    mw.writeFile(pg_conf, data)

    restart(version)
    return mw.returnJson(True, '设置成功')

def getSlaveList(version=''):
    db = pgDb()
    res = db.execute('select * from pg_stat_replication')
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

def getSlaveSyncUserByIp(version=''):
    args = getArgs()
    data = checkArgs(args, ['ip'])
    if not data[0]:
        return data[1]

    ip = args['ip']

    conn = pSqliteDb('slave_sync_user')
    data = conn.field('ip,port,user,pass,mode,cmd,slot_name').where(
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
    slot_name = args['slot_name']
    addTime = time.strftime('%Y-%m-%d %X', time.localtime())

    conn = pSqliteDb('slave_sync_user')
    data = conn.field('ip').where("ip=?", (ip,)).select()
    if len(data) > 0:
        res = conn.where("ip=?", (ip,)).save(
            'port,user,pass,mode,cmd,slot_name', (port, user, apass, mode, cmd,slot_name))
    else:
        conn.add('ip,port,user,cmd,user,pass,mode,slot_name,addtime',
                 (ip, port, user, cmd, user, apass, mode, slot_name,addTime))

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

def getMasterLink(version):
    pdb = pgDb()
    fields = 'pid, usesysid,usename,application_name,client_addr,client_hostname,client_port,backend_xmin,state,sent_lsn,write_lsn,flush_lsn,replay_lsn,write_lag,flush_lag,replay_lag,sync_priority,sync_state'
    data = pdb.field(fields).table('pg_stat_replication').select()
    if isinstance(data, Exception):
        return mw.returnJson(False, '获取主库复制状态失败: ' + str(data), [])

    for item in data:
        for field in ['write_lag', 'flush_lag', 'replay_lag']:
            if item[field] is not None and hasattr(item[field], 'total_seconds'):
                item[field] = item[field].total_seconds()
    return mw.returnJson(True, 'ok', data)

def getSlaveLink(version):
    pdb = pgDb()
    fields = 'pid,status,receive_start_lsn,receive_start_tli,written_lsn,flushed_lsn,received_tli,latest_end_lsn,slot_name,sender_host,sender_port'
    data = pdb.field(fields).table('pg_stat_wal_receiver').select()
    if isinstance(data, Exception):
        return mw.returnJson(False, '获取从库复制状态失败: ' + str(data), [])

    if data:
        replay = pdb.query("""
            SELECT coalesce(pg_last_wal_receive_lsn()::text, '-'),
                   coalesce(pg_last_wal_replay_lsn()::text, '-'),
                   extract(epoch FROM now() - pg_last_xact_replay_timestamp())::bigint
        """)
        for item in data:
            item['receive_lsn'] = '-'
            item['replay_lsn'] = '-'
            item['last_lsn_commit_time'] = None
            if not isinstance(replay, Exception) and replay:
                item['receive_lsn'] = replay[0][0]
                item['replay_lsn'] = replay[0][1]
                item['last_lsn_commit_time'] = replay[0][2]
    return mw.returnJson(True, 'ok', data)

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

    # 创建同步用户+密码
    sql = "CREATE ROLE " + username + " login replication password '" + password + "'"
    pdb.execute(sql)

    # 创建slot,从库使用
    slot_sql = "SELECT pg_create_physical_replication_slot('"+username+"');"
    pdb.execute(slot_sql);

    pg_conf = pgHbaConf()
    data = mw.readFile(pg_conf)

    data = data + "\n" + hbaRule('host', 'replication', username, address, 'scram-sha-256')

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

    slot_sql = "SELECT pg_drop_replication_slot('"+name+"');";
    pdb.execute(slot_sql)

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
        clist = psdb.field(f).where("username=?", (username,)).order('id desc').select()

    if len(clist) == 0:
        return mw.returnJson(False, '请添加同步账户!')

    cmd = 'PGPASSWORD=\'' + clist[0]['password'] + '\' ' + mdir + '/bin/pg_basebackup -Fp --progress -D ' + mdir + \
        '/data -h ' + localIp + ' -p ' + port + \
        ' -U ' + clist[0]['username'] + ' --password'
    data = {}
    data['cmd'] = cmd
    data['info'] = clist
    return mw.returnJson(True, 'ok!', data)

def getMasterRepSlaveUserFullCmd(version=''):
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

    sql = '<span class="set-info c7 ta_center">手动测试</span><hr style="margin-top: 5px;margin-bottom: 10px;"/>'
    sql += 'PGPASSWORD=\'' + clist[0]['password'] + '\' ' + mdir + '/bin/pg_basebackup -Fp --progress -D ' + mdir + \
        '/data -h ' + localIp + ' -p ' + port + \
        ' -U ' + clist[0]['username'] + ' --password'
    sql += "<hr/>"
    sql += '<span class="set-info c7 ta_center">同步账户模式</span><hr style="margin-top: 5px;margin-bottom: 10px;"/>'
    sql +=  'PGPASSWORD=\'' + clist[0]['password'] + '\' ' + mdir + '/bin/pg_basebackup -D ' + mdir + '/data -h '\
            + localIp + ' -p ' + port + ' -U ' + clist[0]['username'] + ' --password '\
            + ' -S ' + clist[0]['username']

    data = {}
    data['cmd'] = sql
    data['info'] = clist
    data['mode'] = 0
    return mw.returnJson(True, 'ok!', data)


def slaveSyncCmd(version=''):
    data = {}
    data['cmd'] = 'cd /www/server/mdserver-web && . bin/activate && python3 plugins/postgresql/index.py do_full_sync'
    return mw.returnJson(True, 'ok!', data)


def writeDbSyncStatus(data):
    path = '/tmp/db_async_status.txt'
    mw.writeFile(path, json.dumps(data))


def doFullSync(version=''):
    mode_file = getSyncModeFile()
    if not os.path.exists(mode_file):
        return mw.returnJson(False, '需要先设置同步配置')

    mode = mw.readFile(mode_file)
    if mode == 'ssh':
        return doFullSyncSSH(version)
    if mode == 'sync-user':
        return doFullSyncUser(version)

def doFullSyncUser(version=''):
    db = pgDb()
    mdir = getServerDir()
    conn = pSqliteDb('slave_sync_user')
    data = conn.field('ip,port,user,pass,mode,cmd,slot_name').find()
    user = data['user']
    apass = data['pass']
    port = data['port']
    ip = data['ip']
    cmd = data['cmd']
    slot_name = data['slot_name']


    cmd_sync = mdir + '/bin/pg_basebackup --progress -D ' + mdir + \
        '/data -h ' + ip + ' -p ' + port \
        + ' -Fp -Xs -P -R ' \
        '-U ' + user + ' --password -S ' + slot_name

    cmd_sync_pwd = "PGPASSWORD='"+apass+"' " + cmd_sync
    print(cmd_sync_pwd)


    cmd_tmp = "/tmp/cmd_run.sh"
    cmd_tmp_data = """#!/bin/expect
spawn %s
expect "Password:"
send "%s\r"
interact
""" % (cmd_sync, apass)

    mw.writeFile(cmd_tmp, cmd_tmp_data)

    # 停用
    stop(version)

    # 备份
    data_dir = getDataDir()
    init_data_dir = getDataDir()+'.init'
    if not os.path.exists(init_data_dir):
        mw.execShell("mv " + data_dir +" " + init_data_dir)
    else:
        mw.execShell("rm -rf " + data_dir)
    mw.execShell("mkdir -p " + data_dir)
    mw.execShell("chown -R postgres:postgres " + data_dir)
    mw.execShell("chmod -R 700 " + data_dir)
    
    os.system('expect '+ cmd_tmp)


    primary_conninfo = "host=%s port=%s user=%s password=%s application_name=standby1" % (ip,port,user,apass)

    # 同步成功后,开启从库配置
    pg_conf = getConf()
    content = mw.readFile(pg_conf)
    field_list = ['hot_standby','primary_conninfo','max_standby_streaming_delay',
        'wal_receiver_status_interval','hot_standby_feedback','primary_slot_name']
    for field in field_list:
        content = content.replace('#'+field, field)

    content = re.sub(
        r"^(\s*primary_slot_name\s*=\s*)'standby_slot'",
        rf"\g<1>'{slot_name}'",
        content,
        flags=re.MULTILINE
    )

    content = re.sub(
        r"^(\s*primary_conninfo\s*=\s*)'.*'",
        rf"\g<1>'{primary_conninfo}'",
        content,
        flags=re.MULTILINE
    )
    # print(content)

    content = content.replace('wal_level', '#wal_level')
    mw.writeFile(pg_conf, content)
    start(version)

    if os.path.exists(cmd_tmp):
        mw.execShell("rm -rf " + cmd_tmp)
    return True

def doFullSyncSSH(version=''):
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
    copy_status = sftp.get("/www/server/postgresql/pgsql.db", getServerDir() + "/pgsql.db")
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

    cmd = mdir + '/bin/pg_basebackup --progress -D ' + mdir + \
        '/data -h ' + ip + ' -p ' + port\
        + ' -Fp -Xs -P -R ' \
        '-U ' + username + ' --password'
    print(cmd)

    cmd_tmp = "/tmp/cmd_run.sh"

    cmd_tmp_data = """#!/bin/expect
spawn %s
expect "Password:"
send "%s\r"
interact
""" % (cmd, password)

    mw.writeFile(cmd_tmp, cmd_tmp_data)
    # 停用
    stop(version)

    # 备份
    data_dir = getDataDir()
    init_data_dir = getDataDir()+'.init'
    if not os.path.exists(init_data_dir):
        mw.execShell("mv " + data_dir +" " + init_data_dir)
    else:
        mw.execShell("rm -rf " + data_dir)
    mw.execShell("mkdir -p " + data_dir)
    mw.execShell("chown -R postgres:postgres " + data_dir)
    mw.execShell("chmod -R 700 " + data_dir)
    os.system("expect " + cmd_tmp)

    slot_name = username
    primary_conninfo = "host=%s port=%s user=%s password=%s application_name=standby1" % (ip,port,username,password)

    # 同步成功后,开启从库配置
    pg_conf = getConf()
    content = mw.readFile(pg_conf)
    field_list = ['hot_standby','primary_conninfo','max_standby_streaming_delay',
        'wal_receiver_status_interval','hot_standby_feedback','primary_slot_name']
    for field in field_list:
        content = content.replace('#'+field, field)

    content = re.sub(
        r"^(\s*primary_slot_name\s*=\s*)'standby_slot'",
        rf"\g<1>'{slot_name}'",
        content,
        flags=re.MULTILINE
    )

    content = re.sub(
        r"^(\s*primary_conninfo\s*=\s*)'.*'",
        rf"\g<1>'{primary_conninfo}'",
        content,
        flags=re.MULTILINE
    )
    # print(content)
    content = content.replace('wal_level', '#wal_level')
    mw.writeFile(pg_conf, content)

    start(version)

    writeDbSyncStatus({'code': 6, 'msg': '从库重启完成...', 'progress': 100})
    if os.path.exists(SSH_PRIVATE_KEY):
        os.system("rm -rf " + SSH_PRIVATE_KEY)
    os.system("rm -rf " + cmd_tmp)
    return True


def installPreInspection(version):
    return 'ok'


def uninstallPreInspection(version):
    # if mw.isDebugMode():
    #     return 'ok'

    stop(version)
    from utils.plugin import plugin as MwPlugin
    MwPlugin.instance().removeIndex(getPluginName(), version)
    return "请手动删除PostgreSQL[{}]<br/> rm -rf {}".format(version, getServerDir())

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
    elif func == 'set_postgres_pwd':
        print(setPostgresPwd(version))
    elif func == 'get_db_list':
        print(getDbList())
    elif func == 'get_table_list':
        print(getTableList())
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
    elif func == 'fix_db_access':
        print(fixDbAccess(version))
    elif func == 'get_db_info':
        print(getDbInfo())
    elif func == 'pg_back':
        print(pgBack())
    elif func == 'pg_back_list':
        print(pgBackList())
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
    elif func == 'get_master_link':
        print(getMasterLink(version))
    elif func == 'get_slave_link':
        print(getSlaveLink(version))
    elif func == 'get_master_rep_slave_list':
        print(getMasterRepSlaveList(version))
    elif func == 'add_master_rep_slave_user':
        print(addMasterRepSlaveUser(version))
    elif func == 'del_master_rep_slave_user':
        print(delMasterRepSlaveUser(version))
    elif func == 'get_master_rep_slave_user_cmd':
        print(getMasterRepSlaveUserCmd(version))
    elif func == 'get_master_rep_slave_user_full_cmd':
        print(getMasterRepSlaveUserFullCmd(version))
    elif func == 'slave_sync_cmd':
        print(slaveSyncCmd(version))
    elif func == 'do_full_sync':
        print(doFullSync(version))
    else:
        print('error')
