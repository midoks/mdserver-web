# coding:utf-8

import sys
import io
import os
import time

sys.path.append(os.getcwd() + "/class/core")
import public


def status():
    data = public.execShell(
        "ps -ef|grep memcached |grep -v grep | grep -v python | awk '{print $2}'")
    if data[0] == '':
        return 'stop'
    return 'start'


def start():
    path = os.path.dirname(os.getcwd())
    cmd = path + "/memcached/bin/memcached"
    cmd = cmd + " " + path + "/memcached/memcached.conf"
    data = public.execShell(cmd)
    if data[0] == '':
        return 'ok'
    return 'fail'


def stop():
    data = public.execShell(
        "ps -ef|grep memcached |grep -v grep |grep -v python |awk '{print $2}' | xargs kill -9")
    if data[0] == '':
        return 'ok'
    return 'fail'


def restart():
    return 'ok'


def reload():
    return 'ok'


def runInfo():
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


def getConf():
    path = os.getcwd() + "/plugins/memcached/init.d/memcached.tpl"
    return path

if __name__ == "__main__":
    func = sys.argv[1]
    if func == 'run_info':
        print runInfo()
    elif func == 'conf':
        print getConf()
    elif func == 'status':
        print status()
    elif func == 'start':
        print start()
    elif func == 'stop':
        print stop()
    elif func == 'restart':
        print restart()
    elif func == 'reload':
        print reload()
