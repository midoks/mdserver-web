# coding:utf-8

import sys
import io
import os
import time
import re

sys.path.append(os.getcwd() + "/class/core")
import mw

app_debug = False
if mw.isAppleSystem():
    app_debug = True


def getPluginName():
    return 'redis'


def getPluginDir():
    return mw.getPluginDir() + '/' + getPluginName()


def getServerDir():
    return mw.getServerDir() + '/' + getPluginName()


def getInitDFile():
    current_os = mw.getOs()
    if current_os == 'darwin':
        return '/tmp/' + getPluginName()

    if current_os.startswith('freebsd'):
        return '/etc/rc.d/' + getPluginName()

    return '/etc/init.d/' + getPluginName()


def getConf():
    path = getServerDir() + "/redis.conf"
    return path


def getConfTpl():
    path = getPluginDir() + "/config/redis.conf"
    return path


def getInitDTpl():
    path = getPluginDir() + "/init.d/" + getPluginName() + ".tpl"
    return path


def getArgs():
    args = sys.argv[3:]
    tmp = {}
    args_len = len(args)

    if args_len == 1:
        t = args[0].strip('{').strip('}')
        if t.strip() == '':
            tmp = []
        else:
            t = t.split(':')
            tmp[t[0]] = t[1]
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

def configTpl():
    path = getPluginDir() + '/tpl'
    pathFile = os.listdir(path)
    tmp = []
    for one in pathFile:
        file = path + '/' + one
        tmp.append(file)
    return mw.getJson(tmp)


def readConfigTpl():
    args = getArgs()
    data = checkArgs(args, ['file'])
    if not data[0]:
        return data[1]

    content = mw.readFile(args['file'])
    content = contentReplace(content)
    return mw.returnJson(True, 'ok', content)

def getPidFile():
    file = getConf()
    content = mw.readFile(file)
    rep = 'pidfile\s*(.*)'
    tmp = re.search(rep, content)
    return tmp.groups()[0].strip()

def status():
    pid_file = getPidFile()
    if not os.path.exists(pid_file):
        return 'stop'

    # data = mw.execShell(
    #     "ps aux|grep redis |grep -v grep | grep -v python | grep -v mdserver-web | awk '{print $2}'")

    # if data[0] == '':
    #     return 'stop'
    return 'start'

def contentReplace(content):
    service_path = mw.getServerDir()
    content = content.replace('{$ROOT_PATH}', mw.getRootDir())
    content = content.replace('{$SERVER_PATH}', service_path)
    content = content.replace('{$SERVER_APP}', service_path + '/redis')
    content = content.replace('{$REDIS_PASS}', mw.getRandomString(10))
    return content



def initDreplace():

    file_tpl = getInitDTpl()
    service_path = os.path.dirname(os.getcwd())

    initD_path = getServerDir() + '/init.d'
    if not os.path.exists(initD_path):
        os.mkdir(initD_path)
    file_bin = initD_path + '/' + getPluginName()

    # initd replace
    if not os.path.exists(file_bin):
        content = mw.readFile(file_tpl)
        content = content.replace('{$SERVER_PATH}', service_path)
        mw.writeFile(file_bin, content)
        mw.execShell('chmod +x ' + file_bin)

    # log
    dataLog = getServerDir() + '/data'
    if not os.path.exists(dataLog):
        mw.execShell('chmod +x ' + file_bin)

    # config replace
    dst_conf = getServerDir() + '/redis.conf'
    dst_conf_init = getServerDir() + '/init.pl'
    if not os.path.exists(dst_conf_init):
        conf_content = mw.readFile(getConfTpl())
        conf_content = conf_content.replace('{$SERVER_PATH}', service_path)
        conf_content = conf_content.replace(
            '{$REDIS_PASS}', mw.getRandomString(10))

        mw.writeFile(dst_conf, conf_content)
        mw.writeFile(dst_conf_init, 'ok')

    # systemd
    systemDir = mw.systemdCfgDir()
    systemService = systemDir + '/' + getPluginName() + '.service'
    if os.path.exists(systemDir) and not os.path.exists(systemService):
        systemServiceTpl = getPluginDir() + '/init.d/' + getPluginName() + '.service.tpl'
        service_path = mw.getServerDir()
        se_content = mw.readFile(systemServiceTpl)
        se_content = se_content.replace('{$SERVER_PATH}', service_path)
        mw.writeFile(systemService, se_content)
        mw.execShell('systemctl daemon-reload')

    return file_bin


def redisOp(method):
    file = initDreplace()

    current_os = mw.getOs()
    if current_os == "darwin":
        data = mw.execShell(file + ' ' + method)
        if data[1] == '':
            return 'ok'
        return data[1]

    if current_os.startswith("freebsd"):
        data = mw.execShell('service ' + getPluginName() + ' ' + method)
        if data[1] == '':
            return 'ok'
        return data[1]

    data = mw.execShell('systemctl ' + method + ' ' + getPluginName())
    if data[1] == '':
        return 'ok'
    return data[1]


def start():
    return redisOp('start')


def stop():
    return redisOp('stop')


def restart():
    status = redisOp('restart')

    log_file = runLog()
    mw.execShell("echo '' > " + log_file)
    return status


def reload():
    return redisOp('reload')


def getPort():
    conf = getServerDir() + '/redis.conf'
    content = mw.readFile(conf)

    rep = "^(" + 'port' + ')\s*([.0-9A-Za-z_& ~]+)'
    tmp = re.search(rep, content, re.M)
    if tmp:
        return tmp.groups()[1]

    return '6379'


def getRedisCmd():
    requirepass = ""
    conf = getServerDir() + '/redis.conf'
    content = mw.readFile(conf)
    rep = "^(requirepass" + ')\s*([.0-9A-Za-z_& ~]+)'
    tmp = re.search(rep, content, re.M)
    if tmp:
        requirepass = tmp.groups()[1]

    default_ip = '127.0.0.1'
    port = getPort()
    # findDebian = mw.execShell('cat /etc/issue |grep Debian')
    # if findDebian[0] != '':
    #     default_ip = mw.getLocalIp()
    cmd = getServerDir() + "/bin/redis-cli -h " + \
        default_ip + ' -p ' + port + " "

    if requirepass != "":
        cmd = getServerDir() + '/bin/redis-cli -h ' + default_ip + \
            ' -p ' + port + ' -a "' + requirepass + '" '

    return cmd

def runInfo():
    s = status()
    if s == 'stop':
        return mw.returnJson(False, '未启动')

    
    cmd = getRedisCmd()
    cmd = cmd + 'info'

    # print(cmd)
    data = mw.execShell(cmd)[0]
    # print(data)
    res = [
        'tcp_port',
        'uptime_in_days',  # 已运行天数
        'connected_clients',  # 连接的客户端数量
        'used_memory',  # Redis已分配的内存总量
        'used_memory_rss',  # Redis占用的系统内存总量
        'used_memory_peak',  # Redis所用内存的高峰值
        'mem_fragmentation_ratio',  # 内存碎片比率
        'total_connections_received',  # 运行以来连接过的客户端的总数量
        'total_commands_processed',  # 运行以来执行过的命令的总数量
        'instantaneous_ops_per_sec',  # 服务器每秒钟执行的命令数量
        'keyspace_hits',  # 查找数据库键成功的次数
        'keyspace_misses',  # 查找数据库键失败的次数
        'latest_fork_usec'  # 最近一次 fork() 操作耗费的毫秒数
    ]
    data = data.split("\n")
    result = {}
    for d in data:
        if len(d) < 3:
            continue
        t = d.strip().split(':')
        if not t[0] in res:
            continue
        result[t[0]] = t[1]
    return mw.getJson(result)

def infoReplication():
    # 复制信息
    s = status()
    if s == 'stop':
        return mw.returnJson(False, '未启动')

    cmd = getRedisCmd()
    cmd = cmd + 'info replication'

    # print(cmd)
    data = mw.execShell(cmd)[0]
    # print(data)
    res = [
        #slave
        'role',#角色
        'master_host',  # 连接主库HOST
        'master_port',  # 连接主库PORT
        'master_link_status',  # 连接主库状态
        'master_last_io_seconds_ago',  # 上次同步时间
        'master_sync_in_progress',  # 正在同步中
        'slave_read_repl_offset',  # 从库读取复制位置
        'slave_repl_offset',  # 从库复制位置
        'slave_priority',  # 从库同步优先级
        'slave_read_only',  # 从库是否仅读
        'replica_announced',  # 已复制副本
        'connected_slaves',  # 连接从库数量
        'master_failover_state',  # 主库故障状态
        'master_replid',  # 主库复制ID
        'master_repl_offset',  # 主库复制位置
        'second_repl_offset',  # 主库复制位置时间
        'repl_backlog_active',  # 复制状态
        'repl_backlog_size',  # 复制大小
        'repl_backlog_first_byte_offset',  # 第一个字节偏移量
        'repl_backlog_histlen',  # backlog中数据的长度
    ]

    data = data.split("\n")
    result = {}
    for d in data:
        if len(d) < 3:
            continue
        t = d.strip().split(':')
        if not t[0] in res:
            continue
        result[t[0]] = t[1]

    if 'role' in result and result['role'] == 'master':
        connected_slaves = int(result['connected_slaves'])
        slave_l = [] 
        for x in range(connected_slaves):
            slave_l.append('slave'+str(x))

        for d in data:
            if len(d) < 3:
                continue
            t = d.strip().split(':')
            if not t[0] in slave_l:
                continue
            result[t[0]] = t[1]

    return mw.getJson(result)


def clusterInfo():
    #集群信息
    # https://redis.io/commands/cluster-info/
    s = status()
    if s == 'stop':
        return mw.returnJson(False, '未启动')

    cmd = getRedisCmd()
    cmd = cmd + 'cluster info'

    # print(cmd)
    data = mw.execShell(cmd)[0]
    # print(data)

    res = [
        'cluster_state',#状态
        'cluster_slots_assigned',  # 被分配的槽
        'cluster_slots_ok',  # 被分配的槽状态
        'cluster_slots_pfail',  # 连接主库状态
        'cluster_slots_fail',  # 失败的槽
        'cluster_known_nodes',  # 知道的节点
        'cluster_size',  # 大小
        'cluster_current_epoch',  # 
        'cluster_my_epoch',  # 
        'cluster_stats_messages_sent',  # 发送
        'cluster_stats_messages_received',  # 接受
        'total_cluster_links_buffer_limit_exceeded',  #
    ]

    data = data.split("\n")
    result = {}
    for d in data:
        if len(d) < 3:
            continue
        t = d.strip().split(':')
        if not t[0] in res:
            continue
        result[t[0]] = t[1]

    return mw.getJson(result)

def clusterNodes():
    s = status()
    if s == 'stop':
        return mw.returnJson(False, '未启动')

    cmd = getRedisCmd()
    cmd = cmd + 'cluster nodes'

    # print(cmd)
    data = mw.execShell(cmd)[0]
    # print(data)

    data = data.strip().split("\n")
    return mw.getJson(data)

def initdStatus():
    current_os = mw.getOs()
    if current_os == 'darwin':
        return "Apple Computer does not support"

    if current_os.startswith('freebsd'):
        initd_bin = getInitDFile()
        if os.path.exists(initd_bin):
            return 'ok'

    shell_cmd = 'systemctl status ' + \
        getPluginName() + ' | grep loaded | grep "enabled;"'
    data = mw.execShell(shell_cmd)
    if data[0] == '':
        return 'fail'
    return 'ok'


def initdInstall():
    current_os = mw.getOs()
    if current_os == 'darwin':
        return "Apple Computer does not support"

    # freebsd initd install
    if current_os.startswith('freebsd'):
        import shutil
        source_bin = initDreplace()
        initd_bin = getInitDFile()
        shutil.copyfile(source_bin, initd_bin)
        mw.execShell('chmod +x ' + initd_bin)
        mw.execShell('sysrc ' + getPluginName() + '_enable="YES"')
        return 'ok'

    mw.execShell('systemctl enable ' + getPluginName())
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

    mw.execShell('systemctl disable ' + getPluginName())
    return 'ok'


def runLog():
    return getServerDir() + '/data/redis.log'


def getRedisConfInfo():
    conf = getServerDir() + '/redis.conf'

    gets = [
        {'name': 'bind', 'type': 2, 'ps': '绑定IP(修改绑定IP可能会存在安全隐患)','must_show':1},
        {'name': 'port', 'type': 2, 'ps': '绑定端口','must_show':1},
        {'name': 'timeout', 'type': 2, 'ps': '空闲链接超时时间,0表示不断开','must_show':1},
        {'name': 'maxclients', 'type': 2, 'ps': '最大连接数','must_show':1},
        {'name': 'databases', 'type': 2, 'ps': '数据库数量','must_show':1},
        {'name': 'requirepass', 'type': 2, 'ps': 'redis密码,留空代表没有设置密码','must_show':1},
        {'name': 'maxmemory', 'type': 2, 'ps': 'MB,最大使用内存,0表示不限制','must_show':1},
        {'name': 'slaveof', 'type': 2, 'ps': '同步主库地址','must_show':0},
        {'name': 'masterauth', 'type': 2, 'ps': '同步主库密码', 'must_show':0}
    ]
    content = mw.readFile(conf)

    result = []
    for g in gets:
        rep = "^(" + g['name'] + ')\s*([.0-9A-Za-z_& ~]+)'
        tmp = re.search(rep, content, re.M)
        if not tmp:
            if g['must_show'] == 0:
                continue

            g['value'] = ''
            result.append(g)
            continue
        g['value'] = tmp.groups()[1]
        if g['name'] == 'maxmemory':
            g['value'] = g['value'].strip("mb")
        result.append(g)

    return result


def getRedisConf():
    data = getRedisConfInfo()
    return mw.getJson(data)


def submitRedisConf():
    gets = ['bind', 'port', 'timeout', 'maxclients',
            'databases', 'requirepass', 'maxmemory','slaveof','masterauth']
    args = getArgs()
    conf = getServerDir() + '/redis.conf'
    content = mw.readFile(conf)
    for g in gets:
        if g in args:
            rep = g + '\s*([.0-9A-Za-z_& ~]+)'
            val = g + ' ' + args[g]

            if g == 'maxmemory':
                val = g + ' ' + args[g] + "mb"

            if g == 'requirepass' and args[g] == '':
                content = re.sub('requirepass', '#requirepass', content)
            if g == 'requirepass' and args[g] != '':
                content = re.sub('#requirepass', 'requirepass', content)
                content = re.sub(rep, val, content)

            if g != 'requirepass':
                content = re.sub(rep, val, content)
    mw.writeFile(conf, content)
    reload()
    return mw.returnJson(True, '设置成功')

if __name__ == "__main__":
    func = sys.argv[1]
    if func == 'status':
        print(status())
    elif func == 'start':
        print(start())
    elif func == 'stop':
        print(stop())
    elif func == 'restart':
        print(restart())
    elif func == 'reload':
        print(reload())
    elif func == 'initd_status':
        print(initdStatus())
    elif func == 'initd_install':
        print(initdInstall())
    elif func == 'initd_uninstall':
        print(initdUinstall())
    elif func == 'run_info':
        print(runInfo())
    elif func == 'info_replication':
        print(infoReplication())
    elif func == 'cluster_info':
        print(clusterInfo())
    elif func == 'cluster_nodes':
        print(clusterNodes())
    elif func == 'conf':
        print(getConf())
    elif func == 'run_log':
        print(runLog())
    elif func == 'get_redis_conf':
        print(getRedisConf())
    elif func == 'submit_redis_conf':
        print(submitRedisConf())
    elif func == 'config_tpl':
        print(configTpl())
    elif func == 'read_config_tpl':
        print(readConfigTpl())
    else:
        print('error')
