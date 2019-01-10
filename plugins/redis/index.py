# coding:utf-8

import sys
import io
import os
import time

sys.path.append(os.getcwd() + "/class/core")
import public

app_debug = False
if public.getOs() == 'darwin':
    app_debug = True


def getPluginName():
    return 'redis'


def getPluginDir():
    return public.getPluginDir() + '/' + getPluginName()


def getServerDir():
    return public.getServerDir() + '/' + getPluginName()


def getInitDFile():
    if app_debug:
        return '/tmp/' + getPluginName()
    return '/etc/init.d/' + getPluginName()


def getConf():
    path = getPluginDir() + "/config/redis.conf"
    return path


def getInitDTpl():
    path = getPluginDir() + "/init.d/" + getPluginName() + ".tpl"
    return path


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


def status():
    data = public.execShell(
        "ps -ef|grep redis |grep -v grep | grep -v python | awk '{print $2}'")
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
    content = public.readFile(file_tpl)
    content = content.replace('{$SERVER_PATH}', service_path)
    public.writeFile(file_bin, content)
    public.execShell('chmod +x ' + file_bin)

    # config replace
    conf_content = public.readFile(getConf())
    conf_content = conf_content.replace('{$SERVER_PATH}', service_path)
    public.writeFile(getServerDir() + '/redis.conf', conf_content)

    return file_bin


def start():
    file = initDreplace()
    data = public.execShell(file + ' start')
    if data[1] == '':
        return 'ok'
    return 'fail'


def stop():
    file = initDreplace()
    data = public.execShell(file + ' stop')
    if data[1] == '':
        return 'ok'
    return 'fail'


def restart():
    file = initDreplace()
    data = public.execShell(file + ' restart')
    if data[1] == '':
        return 'ok'
    return 'fail'


def reload():
    file = initDreplace()
    data = public.execShell(file + ' reload')
    if data[1] == '':
        return 'ok'
    return 'fail'


def runInfo():
    cmd = getServerDir() + "/bin/redis-cli info"
    data = public.execShell(cmd)[0]
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
    return public.getJson(result)


def initdStatus():
    if not app_debug:
        os_name = public.getOs()
        if os_name == 'darwin':
            return "Apple Computer does not support"
    initd_bin = getInitDFile()
    if os.path.exists(initd_bin):
        return 'ok'
    return 'fail'


def initdInstall():
    import shutil
    if not app_debug:
        os_name = public.getOs()
        if os_name == 'darwin':
            return "Apple Computer does not support"

    source_bin = initDreplace()
    initd_bin = getInitDFile()
    shutil.copyfile(source_bin, initd_bin)
    public.execShell('chmod +x ' + initd_bin)
    return 'ok'


def initdUinstall():
    if not app_debug:
        os_name = public.getOs()
        if os_name == 'darwin':
            return "Apple Computer does not support"
    initd_bin = getInitDFile()
    os.remove(initd_bin)
    return 'ok'


def runLog():
    return getServerDir() + '/data/redis.log'

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
    elif func == 'run_log':
        print runLog()
    else:
        print 'error'
