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
    return 'php'


def getPluginDir():
    return public.getPluginDir() + '/' + getPluginName()


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


def getConf(version):
    path = getPluginDir() + "/init.d/php" + version + '.tpl'
    return path


def status(version):
    cmd = "ps -ef|grep 'php/" + version + \
        "' |grep -v grep | grep -v python | awk '{print $2}'"
    data = public.execShell(cmd)
    if data[0] == '':
        return 'stop'
    return 'start'


def phpFpmReplace(version):
    service_path = public.getServerDir()

    tpl_php_fpm = getPluginDir() + '/conf/php-fpm.conf'
    service_php_fpm = getServerDir() + '/' + version + '/etc/php-fpm.conf'
    content = public.readFile(tpl_php_fpm)
    content = content.replace('{$SERVER_PATH}', service_path)
    content = content.replace('{$PHP_VERSION}', version)

    public.writeFile(service_php_fpm, content)


def phpFpmWwwReplace(version):
    service_path = public.getServerDir()

    tpl_php_fpmwww = getPluginDir() + '/conf/www.conf'
    service_php_fpm_dir = getServerDir() + '/' + version + '/etc/php-fpm.d/'
    service_php_fpmwww = service_php_fpm_dir + '/www.conf'
    if not os.path.exists(service_php_fpm_dir):
        os.mkdir(service_php_fpm_dir)

    content = public.readFile(tpl_php_fpmwww)
    content = content.replace('{$PHP_VERSION}', version)
    public.writeFile(service_php_fpmwww, content)


def initDreplace(version):

    file_tpl = getConf(version)
    service_path = public.getServerDir()

    initD_path = getServerDir() + '/init.d'
    if not os.path.exists(initD_path):
        os.mkdir(initD_path)
    file_bin = initD_path + '/php' + version

    content = public.readFile(file_tpl)
    content = content.replace('{$SERVER_PATH}', service_path)

    public.writeFile(file_bin, content)
    public.execShell('chmod +x ' + file_bin)

    phpFpmWwwReplace(version)
    phpFpmReplace(version)

    return file_bin


def phpOp(version, method):
    file = initDreplace(version)
    data = public.execShell(file + ' ' + method)
    if data[1] == '':
        return 'ok'
    return 'fail'


def start(version):
    return phpOp(version, 'start')


def stop(version):
    return phpOp(version, 'stop')


def restart(version):
    return phpOp(version, 'restart')


def reload(version):
    return phpOp(version, 'reload')


def runInfo(version):
    path = os.path.dirname(os.getcwd())
    cmd = path + "/redis/bin/redis-cli info"
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


if __name__ == "__main__":
    func = sys.argv[1]
    version = sys.argv[2]

    if func == 'status':
        print status(version)
    elif func == 'start':
        print start(version)
    elif func == 'stop':
        print stop(version)
    elif func == 'restart':
        print restart(version)
    elif func == 'reload':
        print reload(version)
    elif func == 'run_info':
        print runInfo(version)
    elif func == 'conf':
        print getConf(version)
    else:
        print "fail"
