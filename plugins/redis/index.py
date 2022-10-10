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
    if app_debug:
        return '/tmp/' + getPluginName()
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
        t = t.split(':')
        tmp[t[0]] = t[1]
    elif args_len > 1:
        for i in range(len(args)):
            t = args[i].split(':')
            tmp[t[0]] = t[1]

    return tmp


def status():
    data = mw.execShell(
        "ps -ef|grep redis |grep -v grep | grep -v python | grep -v mdserver-web | awk '{print $2}'")

    if data[0] == '':
        return 'stop'
    return 'start'


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
        mw.writeFile(dst_conf, conf_content)
        mw.writeFile(dst_conf_init, 'ok')

    # systemd
    systemDir = mw.systemdCfgDir()
    systemService = systemDir + '/redis.service'
    systemServiceTpl = getPluginDir() + '/init.d/redis.service.tpl'
    if os.path.exists(systemDir) and not os.path.exists(systemService):
        service_path = mw.getServerDir()
        se_content = mw.readFile(systemServiceTpl)
        se_content = se_content.replace('{$SERVER_PATH}', service_path)
        mw.writeFile(systemService, se_content)
        mw.execShell('systemctl daemon-reload')

    return file_bin


def redisOp(method):
    file = initDreplace()

    if not mw.isAppleSystem():
        data = mw.execShell('systemctl ' + method + ' redis')
        if data[1] == '':
            return 'ok'
        return data[1]

    data = mw.execShell(file + ' start')
    if data[1] == '':
        return 'ok'
    return 'fail'


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


def runInfo():
    s = status()
    if s == 'stop':
        return mw.returnJson(False, '未启动')

    requirepass = ""

    conf = getServerDir() + '/redis.conf'
    content = mw.readFile(conf)
    rep = "^(requirepass" + ')\s*([.0-9A-Za-z_& ~]+)'
    tmp = re.search(rep, content, re.M)
    if tmp:
        requirepass = tmp.groups()[1]

    default_ip = '0.0.0.0'
    findDebian = mw.execShell('cat /etc/issue |grep Debian')
    if findDebian[0] != '':
        default_ip = mw.getLocalIp()

    cmd = getServerDir() + "/bin/redis-cli -h " + default_ip + " info"
    if requirepass != "":
        cmd = getServerDir() + '/bin/redis-cli -h ' + default_ip + \
            ' -a "' + requirepass + '" info'

    data = mw.execShell(cmd)[0]
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


def initdStatus():
    if mw.isAppleSystem():
        return "Apple Computer does not support"

    shell_cmd = 'systemctl status redis | grep loaded | grep "enabled;"'
    data = mw.execShell(shell_cmd)
    if data[0] == '':
        return 'fail'
    return 'ok'


def initdInstall():
    if mw.isAppleSystem():
        return "Apple Computer does not support"

    mw.execShell('systemctl enable redis')
    return 'ok'


def initdUinstall():
    if mw.isAppleSystem():
        return "Apple Computer does not support"

    mw.execShell('systemctl disable redis')
    return 'ok'


def runLog():
    return getServerDir() + '/data/redis.log'


def getRedisConfInfo():
    conf = getServerDir() + '/redis.conf'
    content = mw.readFile(conf)

    gets = [
        {'name': 'bind', 'type': 2, 'ps': '绑定IP(修改绑定IP可能会存在安全隐患)'},
        {'name': 'port', 'type': 2, 'ps': '绑定端口'},
        {'name': 'timeout', 'type': 2, 'ps': '空闲链接超时时间,0表示不断开'},
        {'name': 'maxclients', 'type': 2, 'ps': '最大输入时间'},
        {'name': 'databases', 'type': 2, 'ps': '数据库数量'},
        {'name': 'requirepass', 'type': 2, 'ps': 'redis密码,留空代表没有设置密码'},
        {'name': 'maxmemory', 'type': 2, 'ps': 'MB,最大使用内存,0表示不限制'}
    ]
    content = mw.readFile(conf)

    result = []
    for g in gets:
        rep = "^(" + g['name'] + ')\s*([.0-9A-Za-z_& ~]+)'
        tmp = re.search(rep, content, re.M)
        if not tmp:
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
            'databases', 'requirepass', 'maxmemory']
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
    elif func == 'conf':
        print(getConf())
    elif func == 'run_log':
        print(runLog())
    elif func == 'get_redis_conf':
        print(getRedisConf())
    elif func == 'submit_redis_conf':
        print(submitRedisConf())
    else:
        print('error')
