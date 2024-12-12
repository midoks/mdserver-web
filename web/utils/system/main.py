# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------

import os
import sys
import re
import time
import math
import psutil

import core.mw as mw

from threading import Thread
from time import sleep

def mw_async(f):
    def wrapper(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        thr.start()
    return wrapper

@mw_async
def restartServer():
    if not mw.isRestart():
        return mw.returnData(False, '请等待所有安装任务完成再执行!')
    mw.execShell("sync && init 6 &")
    return mw.returnData(True, '命令发送成功!')

def getPid(self, pname):
    try:
        pids = psutil.pids()
        for pid in pids:
            if psutil.Process(pid).name() == pname:
                return True
        return False
    except:
        return False

def getEnvInfo():
    data = {}
    data['status'] = True
    sdir = mw.getServerDir()

    data['webserver'] = '未安装'
    if os.path.exists(sdir + '/openresty/nginx/sbin/nginx'):
        data['webserver'] = 'OpenResty'
    data['php'] = []
    phpversions = ['52', '53', '54', '55', '56', '70', '71', '72', '73', '74', '80', '81', '82', '83', '84']
    phpPath = sdir + '/php/'
    for pv in phpversions:
        if not os.path.exists(phpPath + pv + '/bin/php'):
            continue
        data['php'].append(pv)
    data['mysql'] = False
    if os.path.exists(sdir + '/mysql/bin/mysql'):
        data['mysql'] = True
    try:
        diskInfo = psutil.disk_usage('/www')
    except:
        diskInfo = psutil.disk_usage('/')
    data['disk'] = diskInfo[2]
    return mw.returnData(True, 'ok', data)

def getDiskInfo():
    # 取磁盘分区信息
    temp = mw.execShell("df -h -P|grep '/'|grep -v tmpfs | grep -v devfs")[0]
    tempInodes = mw.execShell("df -i -P|grep '/'|grep -v tmpfs | grep -v devfs")[0]
    temp1 = temp.split('\n')
    tempInodes1 = tempInodes.split('\n')
    diskInfo = []
    n = 0
    cuts = ['/mnt/cdrom', '/boot', '/boot/efi', '/dev',
            '/dev/shm', '/zroot', '/run/lock', '/run', '/run/shm', '/run/user']
    for tmp in temp1:
        n += 1
        inodes = tempInodes1[n - 1].split()
        disk = tmp.split()
        if len(disk) < 5:
            continue
        if disk[1].find('M') != -1:
            continue
        if disk[1].find('K') != -1:
            continue
        if len(disk[5].split('/')) > 4:
            continue
        if disk[5] in cuts:
            continue
        arr = {}
        arr['path'] = disk[5]
        tmp1 = [disk[1], disk[2], disk[3], disk[4]]
        arr['size'] = tmp1
        arr['inodes'] = [inodes[1], inodes[2], inodes[3], inodes[4]]
        diskInfo.append(arr)
    return diskInfo


def getLoadAverage():
    c = os.getloadavg()
    data = {}
    data['one'] = round(float(c[0]), 2)
    data['five'] = round(float(c[1]), 2)
    data['fifteen'] = round(float(c[2]), 2)
    data['max'] = psutil.cpu_count() * 2
    data['limit'] = data['max']
    data['safe'] = data['max'] * 0.75
    return data

def getSystemVersion():
    # 取操作系统版本
    current_os = mw.getOs()
    # sys_temper = self.getSystemDeviceTemperature()
    # print(sys_temper)
    # mac
    if current_os == 'darwin':
        data = mw.execShell('sw_vers')[0]
        data_list = data.strip().split("\n")
        mac_version = ''
        for x in data_list:
            xlist = x.split("\t")
            mac_version += xlist[len(xlist)-1] + ' '

        arch_ver = mw.execShell("arch")
        return mac_version + " (" + arch_ver[0].strip() + ")"

    # freebsd
    if current_os.startswith('freebsd'):
        version = mw.execShell(
            "cat /etc/*-release | grep PRETTY_NAME | awk -F = '{print $2}' | awk -F '\"' '{print $2}'")
        arch_ver = mw.execShell(
            "sysctl -a | egrep -i 'hw.machine_arch' | awk -F ':' '{print $2}'")
        return version[0].strip() + " (" + arch_ver[0].strip() + ")"

    redhat_series = '/etc/redhat-release'
    if os.path.exists(redhat_series):
        version = mw.readFile('/etc/redhat-release')
        version = version.replace('release ', '').strip()

        arch_ver = mw.execShell("arch")
        return version + " (" + arch_ver[0].strip() + ")"

    os_series = '/etc/os-release'
    if os.path.exists(os_series):
        version = mw.execShell(
            "cat /etc/*-release | grep PRETTY_NAME | awk -F = '{print $2}' | awk -F '\"' '{print $2}'")

        arch_ver = mw.execShell("arch")
        return version[0].strip() + " (" + arch_ver[0].strip() + ")"

def getBootTime():
    # 取系统启动时间
    if os.path.exists('/proc/uptime'):
        uptime = mw.readFile('/proc/uptime')
        run_time = uptime.split()[0]
    else:
        start_time = psutil.boot_time()
        run_time = time.time() - start_time
        
    tStr = float(run_time)
    min = tStr / 60
    hours = min / 60
    days = math.floor(hours / 24)
    hours = math.floor(hours - (days * 24))
    min = math.floor(min - (days * 60 * 24) - (hours * 60))
    return mw.getInfo('已不间断运行: {1}天{2}小时{3}分钟', (str(int(days)), str(int(hours)), str(int(min))))

def getCpuInfo(interval=1):
    # 取CPU信息
    cpuCount = psutil.cpu_count()
    cpuLogicalNum = psutil.cpu_count(logical=False)
    used = psutil.cpu_percent(interval=interval)
    cpuLogicalNum = 0
    if os.path.exists('/proc/cpuinfo'):
        c_tmp = mw.readFile('/proc/cpuinfo')
        d_tmp = re.findall("physical id.+", c_tmp)
        cpuLogicalNum = len(set(d_tmp))

    used_all = psutil.cpu_percent(percpu=True)
    cpu_name = mw.getCpuType() + " * {}".format(cpuLogicalNum)
    return used, cpuCount, used_all, cpu_name, cpuCount, cpuLogicalNum

def getMemInfo():
    # 取内存信息
    mem = psutil.virtual_memory()
    if sys.platform == 'darwin':
        memInfo = {'memTotal': mem.total}
        memInfo['memRealUsed'] = memInfo['memTotal'] * (mem.percent / 100)
    else:
        memInfo = {
            'memTotal': mem.total,
            'memFree': mem.free,
            'memBuffers': mem.buffers,
            'memCached': mem.cached
        }
        memInfo['memRealUsed'] = memInfo['memTotal'] - memInfo['memFree'] - memInfo['memBuffers'] - memInfo['memCached']
    return memInfo

def getMemUsed():
    # 取内存使用率
    try:
        import psutil
        mem = psutil.virtual_memory()

        if mw.getOs() == 'darwin':
            return mem.percent

        memInfo = {'memTotal': mem.total / 1024 / 1024, 'memFree': mem.free / 1024 / 1024,
                   'memBuffers': mem.buffers / 1024 / 1024, 'memCached': mem.cached / 1024 / 1024}
        tmp = memInfo['memTotal'] - memInfo['memFree'] - \
            memInfo['memBuffers'] - memInfo['memCached']
        tmp1 = memInfo['memTotal'] / 100
        return (tmp / tmp1)
    except Exception as ex:
        return 1

