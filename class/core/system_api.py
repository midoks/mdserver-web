# coding: utf-8

import psutil
import time
import os
import re
import math
import sys
import json

from flask import Flask, session
from flask import request

import db
import mw

import config_api
import requests

from threading import Thread
from time import sleep


def mw_async(f):
    def wrapper(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        thr.start()
    return wrapper


class system_api:
    setupPath = None
    pids = None

    def __init__(self):
        self.setupPath = mw.getServerDir()

    ##### ----- start ----- ###
    def networkApi(self):
        data = self.getNetWork()
        return mw.getJson(data)

    def updateServerApi(self):
        stype = request.args.get('type', 'check')
        version = request.args.get('version', '')
        return self.updateServer(stype, version)

    def systemTotalApi(self):
        data = self.getSystemTotal()
        return mw.getJson(data)

    def diskInfoApi(self):
        diskInfo = self.getDiskInfo()
        return mw.getJson(diskInfo)

    def setControlApi(self):
        stype = request.form.get('type', '')
        day = request.form.get('day', '')
        data = self.setControl(stype, day)
        return data

    def getLoadAverageApi(self):
        start = request.args.get('start', '')
        end = request.args.get('end', '')
        data = self.getLoadAverageData(start, end)
        return mw.getJson(data)

    def getCpuIoApi(self):
        start = request.args.get('start', '')
        end = request.args.get('end', '')
        data = self.getCpuIoData(start, end)
        return mw.getJson(data)

    def getDiskIoApi(self):
        start = request.args.get('start', '')
        end = request.args.get('end', '')
        data = self.getDiskIoData(start, end)
        return mw.getJson(data)

    def getNetworkIoApi(self):
        start = request.args.get('start', '')
        end = request.args.get('end', '')
        data = self.getNetWorkIoData(start, end)
        return mw.getJson(data)

    def rememoryApi(self):
        os.system('sync')
        scriptFile = mw.getRunDir() + '/script/rememory.sh'
        mw.execShell("/bin/bash " + scriptFile)
        data = self.getMemInfo()
        return mw.getJson(data)

    # 重启面板
    def restartApi(self):
        self.restartMw()
        return mw.returnJson(True, '面板已重启!')

    def restartServerApi(self):
        if mw.isAppleSystem():
            return mw.returnJson(False, "开发环境不可重起")
        self.restartServer()
        return mw.returnJson(True, '正在重启服务器!')
    ##### ----- end ----- ###

    def restartTask(self):
        initd = mw.getRunDir() + '/scripts/init.d/mw'
        if os.path.exists(initd):
            os.system(initd + ' ' + 'restart_task')
        return True

    def restartMw(self):
        mw.writeFile('data/restart.pl', 'True')
        return True

    @mw_async
    def restartServer(self):
        if not mw.isRestart():
            return mw.returnJson(False, '请等待所有安装任务完成再执行!')
        mw.execShell("sync && init 6 &")
        return mw.returnJson(True, '命令发送成功!')

        # 名取PID
    def getPid(self, pname):
        try:
            if not self.pids:
                self.pids = psutil.pids()
            for pid in self.pids:
                if psutil.Process(pid).name() == pname:
                    return True
            return False
        except:
            return False

    # 检查端口是否占用
    def isOpen(self, port):
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect(('127.0.0.1', int(port)))
            s.shutdown(2)
            return True
        except:
            return False

    # 检测指定进程是否存活
    def checkProcess(self, pid):
        try:
            if not self.pids:
                self.pids = psutil.pids()
            if int(pid) in self.pids:
                return True
            return False
        except:
            return False

    def getPanelInfo(self, get=None):
        # 取面板配置
        address = mw.GetLocalIp()
        try:
            try:
                port = web.ctx.host.split(':')[1]
            except:
                port = mw.readFile('data/port.pl')
        except:
            port = '7200'
        domain = ''
        if os.path.exists('data/domain.conf'):
            domain = mw.readFile('data/domain.conf')

        autoUpdate = ''
        if os.path.exists('data/autoUpdate.pl'):
            autoUpdate = 'checked'
        limitip = ''
        if os.path.exists('data/limitip.conf'):
            limitip = mw.readFile('data/limitip.conf')

        templates = []
        for template in os.listdir('templates/'):
            if os.path.isdir('templates/' + template):
                templates.append(template)
        template = mw.readFile('data/templates.pl')

        check502 = ''
        if os.path.exists('data/502Task.pl'):
            check502 = 'checked'
        return {'port': port, 'address': address, 'domain': domain, 'auto': autoUpdate, '502': check502, 'limitip': limitip, 'templates': templates, 'template': template}

    def getSystemTotal(self, interval=1):
        # 取系统统计信息
        data = self.getMemInfo()
        cpu = self.getCpuInfo(interval)
        data['cpuNum'] = cpu[1]
        data['cpuRealUsed'] = cpu[0]
        data['time'] = self.getBootTime()
        data['system'] = self.getSystemVersion()
        data['isuser'] = mw.M('users').where(
            'username=?', ('admin',)).count()
        data['version'] = '0.0.1'
        return data

    def getLoadAverage(self):
        c = os.getloadavg()
        data = {}
        data['one'] = round(float(c[0]), 2)
        data['five'] = round(float(c[1]), 2)
        data['fifteen'] = round(float(c[2]), 2)
        data['max'] = psutil.cpu_count() * 2
        data['limit'] = data['max']
        data['safe'] = data['max'] * 0.75
        return data

    def getAllInfo(self, get):
        data = {}
        data['load_average'] = self.GetLoadAverage(get)
        data['title'] = self.GetTitle()
        data['network'] = self.GetNetWorkApi(get)
        data['panel_status'] = not os.path.exists(
            '/www/server/mdserver-web/data/close.pl')
        import firewalls
        ssh_info = firewalls.firewalls().GetSshInfo(None)
        data['enable_ssh_status'] = ssh_info['status']
        data['disable_ping_status'] = not ssh_info['ping']
        data['time'] = self.GetBootTime()
        # data['system'] = self.GetSystemVersion();
        # data['mem'] = self.GetMemInfo();
        data['version'] = web.ctx.session.version
        return data

    def getTitle(self):
        titlePl = 'data/title.pl'
        title = 'Linux面板'
        if os.path.exists(titlePl):
            title = mw.readFile(titlePl).strip()
        return title

    def getSystemVersion(self):
        # 取操作系统版本
        if mw.getOs() == 'darwin':
            data = mw.execShell('sw_vers')[0]
            data_list = data.strip().split("\n")
            mac_version = ''
            for x in data_list:
                mac_version += x.split("\t")[1] + ' '
            return mac_version

        redhat_series = '/etc/redhat-release'
        if os.path.exists(redhat_series):
            version = mw.readFile('/etc/redhat-release')
            version = version.replace('release ', '').strip()
            return version

        os_series = '/etc/os-release'
        if os.path.exists(os_series):
            version = mw.execShell(
                "cat /etc/*-release | grep PRETTY_NAME | awk -F = '{print $2}' | awk -F '\"' '{print $2}'")
            return version[0].strip()

        return '未识别系统信息'

    def getBootTime(self):
        # 取系统启动时间
        uptime = mw.readFile('/proc/uptime')
        if uptime == False:
            start_time = psutil.boot_time()
            run_time = time.time() - start_time
        else:
            run_time = uptime.split()[0]
        tStr = float(run_time)
        min = tStr / 60
        hours = min / 60
        days = math.floor(hours / 24)
        hours = math.floor(hours - (days * 24))
        min = math.floor(min - (days * 60 * 24) - (hours * 60))
        return mw.getInfo('已不间断运行: {1}天{2}小时{3}分钟', (str(int(days)), str(int(hours)), str(int(min))))

    def getCpuInfo(self, interval=1):
        # 取CPU信息
        cpuCount = psutil.cpu_count()
        cpuLogicalNum = psutil.cpu_count(logical=False)
        used = psutil.cpu_percent(interval=interval)

        if os.path.exists('/proc/cpuinfo'):
            c_tmp = mw.readFile('/proc/cpuinfo')
            d_tmp = re.findall("physical id.+", c_tmp)
            cpuLogicalNum = len(set(d_tmp))

        used_all = psutil.cpu_percent(percpu=True)
        cpu_name = mw.getCpuType() + " * {}".format(cpuLogicalNum)
        return used, cpuCount, used_all, cpu_name, cpuCount, cpuLogicalNum

    def getMemInfo(self):
        # 取内存信息
        mem = psutil.virtual_memory()
        if mw.getOs() == 'darwin':
            memInfo = {
                'memTotal': mem.total / 1024 / 1024
            }
            memInfo['memRealUsed'] = memInfo['memTotal'] * (mem.percent / 100)
        else:
            memInfo = {
                'memTotal': mem.total / 1024 / 1024,
                'memFree': mem.free / 1024 / 1024,
                'memBuffers': mem.buffers / 1024 / 1024,
                'memCached': mem.cached / 1024 / 1024
            }

            memInfo['memRealUsed'] = memInfo['memTotal'] - \
                memInfo['memFree'] - memInfo['memBuffers'] - \
                memInfo['memCached']
        return memInfo

    def getMemUsed(self):
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

    def getDiskInfo(self):
        info = self.getDiskInfo2()
        if len(info) != 0:
            return info

        # 取磁盘分区信息
        diskIo = psutil.disk_partitions()
        diskInfo = []

        for disk in diskIo:
            if disk[1] == '/mnt/cdrom':
                continue
            if disk[1] == '/boot':
                continue
            tmp = {}
            tmp['path'] = disk[1]
            size_tmp = psutil.disk_usage(disk[1])
            tmp['size'] = [mw.toSize(size_tmp[0]), mw.toSize(
                size_tmp[1]), mw.toSize(size_tmp[2]), str(size_tmp[3]) + '%']
            diskInfo.append(tmp)
        return diskInfo

    def getDiskInfo2(self):
        # 取磁盘分区信息
        temp = mw.execShell(
            "df -h -P|grep '/'|grep -v tmpfs | grep -v devfs")[0]
        tempInodes = mw.execShell(
            "df -i -P|grep '/'|grep -v tmpfs | grep -v devfs")[0]
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

    # 清理系统垃圾
    def clearSystem(self, get):
        count = total = 0
        tmp_total, tmp_count = self.ClearMail()
        count += tmp_count
        total += tmp_total
        tmp_total, tmp_count = self.ClearOther()
        count += tmp_count
        total += tmp_total
        return count, total

    # 清理邮件日志
    def clearMail(self):
        rpath = '/var/spool'
        total = count = 0
        import shutil
        con = ['cron', 'anacron', 'mail']
        for d in os.listdir(rpath):
            if d in con:
                continue
            dpath = rpath + '/' + d
            time.sleep(0.2)
            num = size = 0
            for n in os.listdir(dpath):
                filename = dpath + '/' + n
                fsize = os.path.getsize(filename)
                size += fsize
                if os.path.isdir(filename):
                    shutil.rmtree(filename)
                else:
                    os.remove(filename)
                print('mail clear ok')
                num += 1
            total += size
            count += num
        return total, count

    # 清理其它
    def clearOther(self):
        clearPath = [
            {'path': '/www/server/mdserver-web', 'find': 'testDisk_'},
            {'path': '/www/wwwlogs', 'find': 'log'},
            {'path': '/tmp', 'find': 'panelBoot.pl'},
            {'path': '/www/server/mdserver-web/install', 'find': '.rpm'}
        ]

        total = count = 0
        for c in clearPath:
            for d in os.listdir(c['path']):
                if d.find(c['find']) == -1:
                    continue
                filename = c['path'] + '/' + d
                fsize = os.path.getsize(filename)
                total += fsize
                if os.path.isdir(filename):
                    shutil.rmtree(filename)
                else:
                    os.remove(filename)
                count += 1
        mw.serviceReload()
        os.system('echo > /tmp/panelBoot.pl')
        return total, count

    def psutilNetIoCounters(self):
        '''
        统计网卡流量
        '''
        stat_pl = 'data/only_netio_counters.pl'
        if os.path.exists(stat_pl):
            local_lo = (0, 0, 0, 0)
            ioName = psutil.net_io_counters(pernic=True).keys()
            for x in ioName:

                if x.find("lo") > -1:
                    local_lo = psutil.net_io_counters(
                        pernic=True).get(x)[:4]

            all_io = psutil.net_io_counters()[:4]
            result_io = tuple([all_io[i] - local_lo[i]
                               for i in range(0, len(all_io))])

            # print(local_lo)
            # print(all_io)
            # print(result_io)
            return result_io
        return psutil.net_io_counters()[:4]

    def getNetWork(self):
        # 取网络流量信息
        try:
            # 取网络流量信息
            networkIo = self.psutilNetIoCounters()
            if not "otime" in session:
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

            # print networkIo[1], session['down'], ntime, session['otime']
            session['up'] = networkIo[0]
            session['down'] = networkIo[1]
            session['otime'] = time.time()

            networkInfo['cpu'] = self.getCpuInfo()
            networkInfo['load'] = self.getLoadAverage()
            networkInfo['mem'] = self.getMemInfo()

            return networkInfo
        except Exception as e:
            print("getNetWork error:", e)
            return None

    def getNetWorkIoData(self, start, end):
        # 取指定时间段的网络Io
        data = mw.M('network').dbfile('system').where("addtime>=? AND addtime<=?", (start, end)).field(
            'id,up,down,total_up,total_down,down_packets,up_packets,addtime').order('id asc').select()
        return self.toAddtime(data)

    def getDiskIoData(self, start, end):
        # 取指定时间段的磁盘Io
        data = mw.M('diskio').dbfile('system').where("addtime>=? AND addtime<=?", (start, end)).field(
            'id,read_count,write_count,read_bytes,write_bytes,read_time,write_time,addtime').order('id asc').select()
        return self.toAddtime(data)

    def getCpuIoData(self, start, end):
        # 取指定时间段的CpuIo
        data = mw.M('cpuio').dbfile('system').where("addtime>=? AND addtime<=?",
                                                    (start, end)).field('id,pro,mem,addtime').order('id asc').select()
        return self.toAddtime(data, True)

    def getLoadAverageData(self, start, end):
        data = mw.M('load_average').dbfile('system').where("addtime>=? AND addtime<=?", (
            start, end)).field('id,pro,one,five,fifteen,addtime').order('id asc').select()
        return self.toAddtime(data)

    # 格式化addtime列
    def toAddtime(self, data, tomem=False):
        import time
        if tomem:
            import psutil
            mPre = (psutil.virtual_memory().total / 1024 / 1024) / 100
        length = len(data)
        he = 1
        if length > 100:
            he = 1
        if length > 1000:
            he = 3
        if length > 10000:
            he = 15
        if he == 1:
            for i in range(length):
                data[i]['addtime'] = time.strftime(
                    '%m/%d %H:%M', time.localtime(float(data[i]['addtime'])))
                if tomem and data[i]['mem'] > 100:
                    data[i]['mem'] = data[i]['mem'] / mPre

            return data
        else:
            count = 0
            tmp = []
            for value in data:
                if count < he:
                    count += 1
                    continue
                value['addtime'] = time.strftime(
                    '%m/%d %H:%M', time.localtime(float(value['addtime'])))
                if tomem and value['mem'] > 100:
                    value['mem'] = value['mem'] / mPre
                tmp.append(value)
                count = 0
            return tmp

    def setControl(self, stype, day):

        filename = 'data/control.conf'
        stat_pl = 'data/only_netio_counters.pl'

        if stype == '0':
            mw.execShell("rm -rf " + filename)
        elif stype == '1':
            _day = int(day)
            if _day < 1:
                return mw.returnJson(False, "设置失败!")
            mw.writeFile(filename, day)
        elif stype == '2':
            mw.execShell("rm -rf " + stat_pl)
        elif stype == '3':
            mw.execShell("echo 'True' > " + stat_pl)
        elif stype == 'del':
            if not mw.isRestart():
                return mw.returnJson(False, '请等待所有安装任务完成再执行')
            os.remove("data/system.db")

            sql = db.Sql().dbfile('system')
            csql = mw.readFile('data/sql/system.sql')
            csql_list = csql.split(';')
            for index in range(len(csql_list)):
                sql.execute(csql_list[index], ())
            return mw.returnJson(True, "监控服务已关闭")
        else:
            data = {}
            if os.path.exists(filename):
                try:
                    data['day'] = int(mw.readFile(filename))
                except:
                    data['day'] = 30
                data['status'] = True
            else:
                data['day'] = 30
                data['status'] = False

            if os.path.exists(stat_pl):
                data['stat_all_status'] = True
            else:
                data['stat_all_status'] = False

            return mw.getJson(data)

        return mw.returnJson(True, "设置成功!")

    def versionDiff(self, old, new):
        '''
            test 测试
            new 有新版本
            none 没有新版本
        '''
        new_list = new.split('.')
        if len(new_list) > 3:
            return 'test'

        old_list = old.split('.')
        ret = 'none'

        isHasNew = True
        if int(new_list[0]) == int(old_list[0]) and int(new_list[1]) == int(old_list[1]) and int(new_list[2]) == int(old_list[2]):
            isHasNew = False

        if isHasNew:
            return 'new'
        return ret

    def getServerInfo(self):
        import urllib.request
        import ssl
        upAddr = 'https://api.github.com/repos/midoks/mdserver-web/releases/latest'
        try:
            context = ssl._create_unverified_context()
            req = urllib.request.urlopen(upAddr, context=context, timeout=3)
            result = req.read().decode('utf-8')
            version = json.loads(result)
            return version
        except Exception as e:
            print('getServerInfo', e)
        return {}

    def updateServer(self, stype, version=''):
        # 更新服务
        try:
            if not mw.isRestart():
                return mw.returnJson(False, '请等待所有安装任务完成再执行!')

            version_new_info = self.getServerInfo()
            version_now = config_api.config_api().getVersion()

            new_ver = version_new_info['name']

            if stype == 'check':
                if not 'name' in version_new_info:
                    return mw.returnJson(False, '服务器数据或网络有问题!')

                diff = self.versionDiff(version_now, new_ver)
                if diff == 'new':
                    return mw.returnJson(True, '有新版本!', new_ver)
                elif diff == 'test':
                    return mw.returnJson(True, '有测试版本!', new_ver)
                else:
                    return mw.returnJson(False, '已经是最新,无需更新!')

            if stype == 'info':
                if not 'name' in version_new_info:
                    return mw.returnJson(False, '服务器数据有问题!')
                diff = self.versionDiff(version_now, new_ver)
                data = {}
                data['version'] = new_ver
                data['content'] = version_new_info[
                    'body'].replace("\n", "<br/>")
                return mw.returnJson(True, '更新信息!', data)

            if stype == 'update':
                if version == '':
                    return mw.returnJson(False, '缺少版本信息!')

                if new_ver != version:
                    return mw.returnJson(False, '更新失败,请重试!')

                toPath = mw.getRootDir() + '/temp'
                if not os.path.exists(toPath):
                    mw.execShell('mkdir -p ' + toPath)

                newUrl = "https://github.com/midoks/mdserver-web/archive/refs/tags/" + version + ".zip"

                dist_mw = toPath + '/mw.zip'
                if not os.path.exists(dist_mw):
                    mw.execShell(
                        'wget --no-check-certificate -O ' + dist_mw + ' ' + newUrl)

                dist_to = toPath + "/mdserver-web-" + version
                if not os.path.exists(dist_to):
                    os.system('unzip -o ' + toPath +
                              '/mw.zip' + ' -d ' + toPath)

                cmd_cp = 'cp -rf ' + toPath + '/mdserver-web-' + \
                    version + '/* ' + mw.getServerDir() + '/mdserver-web'
                mw.execShell(cmd_cp)

                mw.execShell('rm -rf ' + toPath + '/mdserver-web-' + version)
                mw.execShell('rm -rf ' + toPath + '/mw.zip')

                self.restartMw()
                return mw.returnJson(True, '安装更新成功!')

            return mw.returnJson(False, '已经是最新,无需更新!')
        except Exception as ex:
            # print('updateServer', ex)
            return mw.returnJson(False, "连接服务器失败!" + str(ex))

    # 修复面板
    def repPanel(self, get):
        vp = ''
        if mw.readFile('/www/server/mdserver-web/class/common.py').find('checkSafe') != -1:
            vp = '_pro'
        mw.ExecShell("wget -O update.sh " + mw.get_url() +
                     "/install/update" + vp + ".sh && bash update.sh")
        if hasattr(web.ctx.session, 'getCloudPlugin'):
            del(web.ctx.session['getCloudPlugin'])
        return True
