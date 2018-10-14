# coding:utf-8

import time
import psutil
import os
import sys

from flask import Flask, session
from flask import Blueprint, render_template
from flask import jsonify

sys.path.append("class/")
import public


system = Blueprint('system', __name__, template_folder='templates')


def GetCpuInfo(interval=1):
    # 取CPU信息
    cpuCount = psutil.cpu_count()
    used = psutil.cpu_percent(interval=interval)
    return used, cpuCount


def GetLoadAverage():
    c = os.getloadavg()
    data = {}
    data['one'] = float(c[0])
    data['five'] = float(c[1])
    data['fifteen'] = float(c[2])
    data['max'] = psutil.cpu_count() * 2
    data['limit'] = data['max']
    data['safe'] = data['max'] * 0.75
    return data


def GetMemInfo():
    # 取内存信息
    mem = psutil.virtual_memory()
    memInfo = {'memTotal': mem.total / 1024 / 1024,
               'memFree': mem.free / 1024 / 1024,
               # 'memBuffers': mem.buffers / 1024 / 1024,
               # 'memCached': mem.cached / 1024 / 1024
               }

    memInfo['memRealUsed'] = memInfo['memTotal'] - \
        memInfo['memFree']
    #- memInfo['memBuffers'] - memInfo['memCached']
    return memInfo


def GetBootTime():
    conf = public.readFile('/proc/uptime').split()
    tStr = float(conf[0])
    min = tStr / 60
    hours = min / 60
    days = math.floor(hours / 24)
    hours = math.floor(hours - (days * 24))
    min = math.floor(min - (days * 60 * 24) - (hours * 60))
    return public.getMsg('SYS_BOOT_TIME', (str(int(days)), str(int(hours)), str(int(min))))


def GetSystemVersion():
    # 取操作系统版本
    version = public.readFile('/etc/redhat-release')
    if not version:
        version = public.readFile(
            '/etc/issue').strip().split("\n")[0].replace('\\n', '').replace('\l', '').strip()
    else:
        version = version.replace('release ', '').strip()
    return version


@system.route("/network")
def network():
    # 取网络流量信息
    networkIo = psutil.net_io_counters()[:4]
    if not hasattr(session, 'otime'):
        session['up'] = networkIo[0]
        session['down'] = networkIo[1]
        session['otime'] = time.time()

    ntime = time.time()
    networkInfo = {}
    networkInfo['upTotal'] = networkIo[0]
    networkInfo['downTotal'] = networkIo[1]
    networkInfo['up'] = round(float(
        networkIo[0] - session['up']) / 1024 / (ntime - session['otime']), 2)
    networkInfo['down'] = round(
        float(networkIo[1] - session['down']) / 1024 / (ntime - session['otime']), 2)
    networkInfo['downPackets'] = networkIo[3]
    networkInfo['upPackets'] = networkIo[2]

    session['up'] = networkIo[0]
    session['down'] = networkIo[1]
    session['otime'] = time.time()

    networkInfo['cpu'] = GetCpuInfo()
    networkInfo['load'] = GetLoadAverage()
    return jsonify(networkInfo)


@system.route("/diskinfo")
def diskinfo():
        # 取磁盘分区信息
    temp = public.ExecShell("df -h -P|grep '/'|grep -v tmpfs")[0]
    tempInodes = public.ExecShell("df -i -P|grep '/'|grep -v tmpfs")[0]
    temp1 = temp.split('\n')
    tempInodes1 = tempInodes.split('\n')
    diskInfo = []
    n = 0
    cuts = ['/mnt/cdrom', '/boot', '/boot/efi', '/dev',
            '/dev/shm', '/run/lock', '/run', '/run/shm', '/run/user']
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
        if disk[5] == '/':
            bootLog = '/tmp/panelBoot.pl'
            if disk[2].find('M') != -1:
                if os.path.exists(bootLog):
                    os.system('rm -f ' + bootLog)
            else:
                pass
                if not os.path.exists(bootLog):
                    os.system('sleep 1 &')
        # print arr
        diskInfo.append(arr)
    return jsonify(diskInfo)


@system.route("/systemtotal")
def systemtotal():
     # 取系统统计信息
    data = GetMemInfo()
    cpu = GetCpuInfo(1)
    data['cpuNum'] = cpu[1]
    data['cpuRealUsed'] = cpu[0]
    # data['time'] = GetBootTime()
    # data['system'] = GetSystemVersion()
    data['isuser'] = public.M('users').where('username=?', ('admin',)).count()
    data['version'] = '0.0.1'
    return jsonify(data)
