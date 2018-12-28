# coding: utf-8

import psutil
import time
import os
import re
import math
import json

from flask import Flask, session
from flask import request

import db
import public
import config


class system_api:
    setupPath = None
    pids = None

    def __init__(self):
        self.setupPath = public.getServerDir()

    ##### ----- start ----- ###
    def networkApi(self):
        data = self.getNetWork()
        return public.getJson(data)

    def updateServerApi(self):
        stype = request.args.get('type', 'check')
        version = request.args.get('version', '')
        return self.updateServer(stype, version)

    def systemTotalApi(self):
        data = self.getSystemTotal()
        return public.getJson(data)

    def diskInfoApi(self):
        diskInfo = self.getDiskInfo()
        return public.getJson(diskInfo)

    def setControlApi(self):
        stype = request.form.get('type', '')
        day = request.form.get('day', '')
        data = self.setControl(stype, day)
        return data

    def getLoadAverageApi(self):
        start = request.args.get('start', '')
        end = request.args.get('end', '')
        data = self.getLoadAverageData(start, end)
        return public.getJson(data)

    def getCpuIoApi(self):
        start = request.args.get('start', '')
        end = request.args.get('end', '')
        data = self.getCpuIoData(start, end)
        return public.getJson(data)

    def getDiskIoApi(self):
        start = request.args.get('start', '')
        end = request.args.get('end', '')
        data = self.getDiskIoData(start, end)
        return public.getJson(data)

    def getNetworkIoApi(self):
        start = request.args.get('start', '')
        end = request.args.get('end', '')
        data = self.getNetWorkIoData(start, end)
        return public.getJson(data)

    # 重启面板
    def restartApi(self):
        cmd = public.getRunDir() + '/scripts/init.d/mw start'
        public.execShell(cmd)
        return public.returnJson(True, '面板已重启!')
    ##### ----- end ----- ###

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
        address = public.GetLocalIp()
        try:
            try:
                port = web.ctx.host.split(':')[1]
            except:
                port = public.readFile('data/port.pl')
        except:
            port = '8888'
        domain = ''
        if os.path.exists('data/domain.conf'):
            domain = public.readFile('data/domain.conf')

        autoUpdate = ''
        if os.path.exists('data/autoUpdate.pl'):
            autoUpdate = 'checked'
        limitip = ''
        if os.path.exists('data/limitip.conf'):
            limitip = public.readFile('data/limitip.conf')

        templates = []
        for template in os.listdir('templates/'):
            if os.path.isdir('templates/' + template):
                templates.append(template)
        template = public.readFile('data/templates.pl')

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
        data['isuser'] = public.M('users').where(
            'username=?', ('admin',)).count()
        data['version'] = '0.0.1'
        return data

    def getLoadAverage(self, get=None):
        c = os.getloadavg()
        data = {}
        data['one'] = float(c[0])
        data['five'] = float(c[1])
        data['fifteen'] = float(c[2])
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
            '/www/server/panel/data/close.pl')
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
        title = '宝塔Linux面板'
        if os.path.exists(titlePl):
            title = public.readFile(titlePl).strip()
        return title

    def getSystemVersion(self):
        # 取操作系统版本
        os = public.getOs()
        if os == 'darwin':
            data = public.execShell('sw_vers')[0]
            data_list = data.strip().split("\n")
            mac_version = ''
            for x in data_list:
                mac_version += x.split("\t")[1] + ' '
            return mac_version

        version = public.readFile('/etc/redhat-release')
        if not version:
            version = public.readFile(
                '/etc/issue').strip().split("\n")[0].replace('\\n', '').replace('\l', '').strip()
        else:
            version = version.replace('release ', '').strip()
        return version

    def getBootTime(self):
        # 取系统启动时间
        start_time = psutil.boot_time()
        run_time = time.time() - start_time
        # conf = public.readFile('/proc/uptime').split()
        tStr = float(run_time)
        min = tStr / 60
        hours = min / 60
        days = math.floor(hours / 24)
        hours = math.floor(hours - (days * 24))
        min = math.floor(min - (days * 60 * 24) - (hours * 60))
        return public.getInfo('已不间断运行: {1}天{2}小时{3}分钟', (str(int(days)), str(int(hours)), str(int(min))))

    def getCpuInfo(self, interval=1):
        # 取CPU信息
        cpuCount = psutil.cpu_count()
        used = psutil.cpu_percent(interval=interval)
        return used, cpuCount

    def getMemInfo(self, get=None):
        # 取内存信息
        mem = psutil.virtual_memory()
        if public.getOs() == 'darwin':
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

            if public.getOs() == 'darwin':
                return mem.percent

            memInfo = {'memTotal': mem.total / 1024 / 1024, 'memFree': mem.free / 1024 / 1024,
                       'memBuffers': mem.buffers / 1024 / 1024, 'memCached': mem.cached / 1024 / 1024}
            tmp = memInfo['memTotal'] - memInfo['memFree'] - \
                memInfo['memBuffers'] - memInfo['memCached']
            tmp1 = memInfo['memTotal'] / 100
            return (tmp / tmp1)
        except Exception, ex:
            return 1

    def getDiskInfo(self, get=None):
        return self.getDiskInfo2()
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
            tmp['size'] = psutil.disk_usage(disk[1])
            diskInfo.append(tmp)
        return diskInfo

    def getDiskInfo2(self):
        # 取磁盘分区信息
        temp = public.execShell(
            "df -h -P|grep '/'|grep -v tmpfs | grep -v devfs")[0]
        tempInodes = public.execShell(
            "df -i -P|grep '/'|grep -v tmpfs | grep -v devfs")[0]
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
                bootLog = os.getcwd() + '/tmp/panelBoot.pl'
                if disk[2].find('M') != -1:
                    if os.path.exists(bootLog):
                        os.system('rm -f ' + bootLog)
                else:
                    if not os.path.exists(bootLog):
                        pass
            if inodes[2] != '0':
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
                print '\t\033[1;32m[OK]\033[0m'
                num += 1
            total += size
            count += num
        return total, count

    # 清理其它
    def clearOther(self):
        clearPath = [
            {'path': '/www/server/panel', 'find': 'testDisk_'},
            {'path': '/www/wwwlogs', 'find': 'log'},
            {'path': '/tmp', 'find': 'panelBoot.pl'},
            {'path': '/www/server/panel/install', 'find': '.rpm'}
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
        public.serviceReload()
        os.system('echo > /tmp/panelBoot.pl')
        return total, count

    def getNetWork(self, get=None):
        # return self.GetNetWorkApi(get);
        # 取网络流量信息
        try:
            # 取网络流量信息
            networkIo = psutil.net_io_counters()[:4]
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
            networkInfo['load'] = self.getLoadAverage(get)
            networkInfo['mem'] = self.getMemInfo(get)

            return networkInfo
        except Exception, e:
            print e
            return None

    def getNetWorkApi(self, get=None):
        # 取网络流量信息
        try:
            tmpfile = 'data/network.temp'
            networkIo = psutil.net_io_counters()[:4]

            if not os.path.exists(tmpfile):
                public.writeFile(tmpfile, str(
                    networkIo[0]) + '|' + str(networkIo[1]) + '|' + str(int(time.time())))

            lastValue = public.readFile(tmpfile).split('|')

            ntime = time.time()
            networkInfo = {}
            networkInfo['upTotal'] = networkIo[0]
            networkInfo['downTotal'] = networkIo[1]
            networkInfo['up'] = round(
                float(networkIo[0] - int(lastValue[0])) / 1024 / (ntime - int(lastValue[2])), 2)
            networkInfo['down'] = round(
                float(networkIo[1] - int(lastValue[1])) / 1024 / (ntime - int(lastValue[2])), 2)
            networkInfo['downPackets'] = networkIo[3]
            networkInfo['upPackets'] = networkIo[2]

            public.writeFile(tmpfile, str(
                networkIo[0]) + '|' + str(networkIo[1]) + '|' + str(int(time.time())))

            # networkInfo['cpu'] = self.GetCpuInfo(0.1)
            return networkInfo
        except:
            return None

    def restartServer(self, get):
        if not public.isRestart():
            return public.returnMsg(False, 'EXEC_ERR_TASK')
        public.ExecShell("sync && /etc/init.d/bt stop && init 6 &")
        return public.returnMsg(True, 'SYS_REBOOT')

    # 释放内存
    def reMemory(self, get):
        os.system('sync')
        scriptFile = 'script/rememory.sh'
        if not os.path.exists(scriptFile):
            public.downloadFile(web.ctx.session.home +
                                '/script/rememory.sh', scriptFile)
        public.ExecShell("/bin/bash " + self.setupPath +
                         '/panel/' + scriptFile)
        return self.GetMemInfo()

    def getNetWorkIoData(self, start, end):
        # 取指定时间段的网络Io
        data = public.M('network').dbfile('system').where("addtime>=? AND addtime<=?", (start, end)).field(
            'id,up,down,total_up,total_down,down_packets,up_packets,addtime').order('id asc').select()
        return self.toAddtime(data)

    def getDiskIoData(self, start, end):
        # 取指定时间段的磁盘Io
        data = public.M('diskio').dbfile('system').where("addtime>=? AND addtime<=?", (start, end)).field(
            'id,read_count,write_count,read_bytes,write_bytes,read_time,write_time,addtime').order('id asc').select()
        return self.toAddtime(data)

    def getCpuIoData(self, start, end):
        # 取指定时间段的CpuIo
        data = public.M('cpuio').dbfile('system').where("addtime>=? AND addtime<=?",
                                                        (start, end)).field('id,pro,mem,addtime').order('id asc').select()
        return self.toAddtime(data, True)

    def getLoadAverageData(self, start, end):
        data = public.M('load_average').dbfile('system').where("addtime>=? AND addtime<=?", (
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

        if stype == '0':
            public.execShell("rm -f " + filename)
        elif stype == '1':
            _day = int(day)
            if _day < 1:
                return public.returnJson(False, "设置失败!")
            public.writeFile(filename, day)
        elif stype == 'del':
            if not public.isRestart():
                return public.returnJson(False, '请等待所有安装任务完成再执行')
            os.remove("data/system.db")

            sql = db.Sql().dbfile('system')
            csql = public.readFile('data/sql/system.sql')
            csql_list = csql.split(';')
            for index in range(len(csql_list)):
                sql.execute(csql_list[index], ())
            return public.returnJson(True, "监控服务已关闭")
        else:
            data = {}
            if os.path.exists(filename):
                try:
                    data['day'] = int(public.readFile(filename))
                except:
                    data['day'] = 30
                data['status'] = True
            else:
                data['day'] = 30
                data['status'] = False
            return public.getJson(data)

        return public.returnJson(True, "设置成功!")

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
        for i in range(len(old_list)):
            tm_new = int(new_list[i])
            tm_old = int(new_list[i])
            if tm_new > tm_old:
                return 'new'
        return ret

    def getServerInfo(self):

        upAddr = 'https://raw.githubusercontent.com/midoks/mdserver-web/master/version'
        try:
            version = public.httpGet(
                upAddr + '/info.json')
            version = json.loads(version)
            return version[0]
        except Exception as e:
            print e
        return {}

    def updateServer(self, stype, version=''):
        # 更新服务
        try:

            if public.isUpdateLocalSoft():
                if stype == 'check' or stype == 'info' or stype == 'update':
                    return public.returnJson(True, '正在安装中...', 'download')
                if stype == 'update_status':

                    data = public.readFile('tmp/panelExec.log')
                    if data == 'done':
                        return public.returnJson(True, '进度!', 100)
                    else:
                        _data = json.loads(data)
                        return public.returnJson(True, '进度!', _data['pre'])

                    if os.path.exists('mdserver-web.zip'):
                        return public.returnJson(True, '进度!', 100)

            if not public.isRestart():
                return public.returnJson(False, '请等待所有安装任务完成再执行!')
            if stype == 'check':
                version_now = config.config().getVersion()
                version_new_info = self.getServerInfo()
                if not 'version' in version_new_info:
                    return public.returnJson(False, '服务器数据有问题!')

                diff = self.versionDiff(
                    version_now, version_new_info['version'])
                if diff == 'new':
                    return public.returnJson(True, '有新版本!', version_new_info['version'])
                elif diff == 'test':
                    return public.returnJson(True, '有测试版本!', version_new_info['version'])
                else:
                    return public.returnJson(False, '已经是最新,无需更新!')

            if stype == 'info':
                version_new_info = self.getServerInfo()
                version_now = config.config().getVersion()

                if not 'version' in version_new_info:
                    return public.returnJson(False, '服务器数据有问题!')
                diff = self.versionDiff(
                    version_now, version_new_info['version'])
                return public.returnJson(True, '更新信息!', version_new_info)

            if stype == 'update':
                if version == '':
                    return public.returnJson(False, '缺少版本信息!')

                v_new_info = self.getServerInfo()
                if v_new_info['version'] != version:
                    return public.returnJson(False, '更新失败,请重试!')

                if not 'path' in v_new_info or v_new_info['path'] == '':
                    return public.returnJson(False, '下载地址不存在!')

                execstr = v_new_info['path'] + '|dl|mdserver-web.zip'
                taskAdd = (None,  '下载[mdserver-web-' + v_new_info['version'] + ']',
                           'download', '0', time.strftime('%Y-%m-%d %H:%M:%S'), execstr)

                public.M('tasks').add(
                    'id,name,type,status,addtime, execstr', taskAdd)
                return public.returnJson(True, '下载中...')

            if stype == 'update_install':
                public.execShell('unzip -o mdserver-web.zip -d ./')
                public.execShell('rm -f mdserver-web.zip')
                return public.returnJson(True, '安装更新成功!')

            return public.returnJson(False, '已经是最新,无需更新!')
        except Exception as ex:
            print ex
            return public.returnJson(False, "连接服务器失败!")

    # 重启面板
    def reWeb(self, get):
        if not public.isRestart():
            public.returnMsg(False, '请等待所有安装任务完成再执行!')

        # public.ExecShell('/etc/init.d/bt restart &')
        public.returnMsg(True, '执行成功!')

    # 修复面板
    def repPanel(self, get):
        vp = ''
        if public.readFile('/www/server/panel/class/common.py').find('checkSafe') != -1:
            vp = '_pro'
        public.ExecShell("wget -O update.sh " + public.get_url() +
                         "/install/update" + vp + ".sh && bash update.sh")
        if hasattr(web.ctx.session, 'getCloudPlugin'):
            del(web.ctx.session['getCloudPlugin'])
        return True
