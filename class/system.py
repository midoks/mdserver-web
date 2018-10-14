#coding: utf-8
# +-------------------------------------------------------------------
# | 宝塔Linux面板 x3
# +-------------------------------------------------------------------
# | Copyright (c) 2015-2016 宝塔软件(http://bt.cn) All rights reserved.
# +-------------------------------------------------------------------
# | Author: 黄文良 <287962566@qq.com>
# +-------------------------------------------------------------------
import psutil,web,time,os,public,re
class system:
    setupPath = None;
    pids = None
    def __init__(self):
        self.setupPath = '/www/server';
    
    def GetConcifInfo(self,get=None):
        #取环境配置信息
        if not hasattr(web.ctx.session, 'config'):
            web.ctx.session.config = public.M('config').where("id=?",('1',)).field('webserver,sites_path,backup_path,status,mysql_root').find();
        if not hasattr(web.ctx.session.config,'email'):
            web.ctx.session.config['email'] = public.M('users').where("id=?",('1',)).getField('email');
        data = {}
        data = web.ctx.session.config
        data['webserver'] = web.ctx.session.config['webserver']
        #PHP版本
        phpVersions = ('52','53','54','55','56','70','71','72','73','74')
        
        data['php'] = []
        
        for version in phpVersions:
            tmp = {}
            tmp['setup'] = os.path.exists(self.setupPath + '/php/'+version+'/bin/php');
            if tmp['setup']:
                phpConfig = self.GetPHPConfig(version)
                tmp['version'] = version
                tmp['max'] = phpConfig['max']
                tmp['maxTime'] = phpConfig['maxTime']
                tmp['pathinfo'] = phpConfig['pathinfo']
                tmp['status'] = os.path.exists('/tmp/php-cgi-'+version+'.sock')
                data['php'].append(tmp)
            
        tmp = {}
        data['webserver'] = ''
        serviceName = 'nginx'
        tmp['setup'] = False
        phpversion = "54"
        phpport = '888';
        pstatus = False;
        pauth = False;
        if os.path.exists(self.setupPath+'/nginx'): 
            data['webserver'] = 'nginx'
            serviceName = 'nginx'
            tmp['setup'] = os.path.exists(self.setupPath +'/nginx/sbin/nginx');
            configFile = self.setupPath + '/nginx/conf/nginx.conf';
            try:
                if os.path.exists(configFile):
                    conf = public.readFile(configFile);
                    rep = "listen\s+([0-9]+)\s*;";
                    rtmp = re.search(rep,conf);
                    if rtmp:
                        phpport = rtmp.groups()[0];
                    
                    if conf.find('AUTH_START') != -1: pauth = True;
                    if conf.find(self.setupPath + '/stop') == -1: pstatus = True;
                    configFile = self.setupPath + '/nginx/conf/enable-php.conf';
                    conf = public.readFile(configFile);
                    rep = "php-cgi-([0-9]+)\.sock";
                    rtmp = re.search(rep,conf);
                    if rtmp:
                        phpversion = rtmp.groups()[0];
            except:
                pass;
            
        elif os.path.exists(self.setupPath+'/apache'):
            data['webserver'] = 'apache'
            serviceName = 'httpd'
            tmp['setup'] = os.path.exists(self.setupPath +'/apache/bin/httpd');
            configFile = self.setupPath + '/apache/conf/extra/httpd-vhosts.conf';
            try:
                if os.path.exists(configFile):
                    conf = public.readFile(configFile);
                    rep = "php-cgi-([0-9]+)\.sock";
                    rtmp = re.search(rep,conf);
                    if rtmp:
                        phpversion = rtmp.groups()[0];
                    rep = "Listen\s+([0-9]+)\s*\n";
                    rtmp = re.search(rep,conf);
                    if rtmp:
                        phpport = rtmp.groups()[0];
                    if conf.find('AUTH_START') != -1: pauth = True;
                    if conf.find(self.setupPath + '/stop') == -1: pstatus = True;
            except:
                pass
                
                
        tmp['type'] = data['webserver']
        tmp['version'] = public.readFile(self.setupPath + '/'+data['webserver']+'/version.pl');
        tmp['status'] = False
        result = public.ExecShell('/etc/init.d/' + serviceName + ' status')
        if result[0].find('running') != -1: tmp['status'] = True
        data['web'] = tmp
        
        tmp = {}
        vfile = self.setupPath + '/phpmyadmin/version.pl';
        tmp['version'] = public.readFile(vfile);
        tmp['setup'] = os.path.exists(vfile);
        tmp['status'] = pstatus;
        tmp['phpversion'] = phpversion;
        tmp['port'] = phpport;
        tmp['auth'] = pauth;
        data['phpmyadmin'] = tmp;
        
        tmp = {}
        tmp['setup'] = os.path.exists('/etc/init.d/tomcat');
        tmp['status'] = False
        if tmp['setup']:
            if os.path.exists('/www/server/tomcat/logs/catalina-daemon.pid'):
                tmp['status'] = self.getPid('jsvc')
            if not tmp['status']:
                tmp['status'] = self.getPid('java')
        tmp['version'] = public.readFile(self.setupPath + '/tomcat/version.pl');
        data['tomcat'] = tmp;
        
        tmp = {}
        tmp['setup'] = os.path.exists(self.setupPath +'/mysql/bin/mysql');
        tmp['version'] = public.readFile(self.setupPath + '/mysql/version.pl');
        tmp['status'] = os.path.exists('/tmp/mysql.sock')
        data['mysql'] = tmp
        
        tmp = {}
        tmp['setup'] = os.path.exists(self.setupPath +'/redis/runtest');
        tmp['status'] = os.path.exists('/var/run/redis_6379.pid');
        data['redis'] = tmp;
        
        tmp = {}
        tmp['setup'] = os.path.exists('/usr/local/memcached/bin/memcached');
        tmp['status'] = os.path.exists('/var/run/memcached.pid');
        data['memcached'] = tmp;
        
        tmp = {}
        tmp['setup'] = os.path.exists(self.setupPath +'/pure-ftpd/bin/pure-pw');
        tmp['version'] = public.readFile(self.setupPath + '/pure-ftpd/version.pl');
        tmp['status'] = os.path.exists('/var/run/pure-ftpd.pid')
        data['pure-ftpd'] = tmp
        data['panel'] = self.GetPanelInfo()
        data['systemdate'] = public.ExecShell('date +"%Y-%m-%d %H:%M:%S %Z %z"')[0].strip();
        
        return data
    
    
    #名取PID
    def getPid(self,pname):
        try:
            if not self.pids: self.pids = psutil.pids()
            for pid in self.pids:
                if psutil.Process(pid).name() == pname: return True;
            return False
        except: return False
    
    #检测指定进程是否存活
    def checkProcess(self,pid):
        try:
            if not self.pids: self.pids = psutil.pids()
            if int(pid) in self.pids: return True
            return False;
        except: return False
    
    
    def GetPanelInfo(self,get=None):
        #取面板配置
        address = public.GetLocalIp()
        try:
            try:
                port = web.ctx.host.split(':')[1]
            except:
                port = public.readFile('data/port.pl')
        except:
            port = '8888';
        domain = ''
        if os.path.exists('data/domain.conf'):
           domain = public.readFile('data/domain.conf');
        
        autoUpdate = ''
        if os.path.exists('data/autoUpdate.pl'): autoUpdate = 'checked';
        limitip = ''
        if os.path.exists('data/limitip.conf'): limitip = public.readFile('data/limitip.conf');
        
        templates = []
        for template in os.listdir('templates/'):
            if os.path.isdir('templates/' + template): templates.append(template);
        template = public.readFile('data/templates.pl');
        
        check502 = '';
        if os.path.exists('data/502Task.pl'): check502 = 'checked';
        return {'port':port,'address':address,'domain':domain,'auto':autoUpdate,'502':check502,'limitip':limitip,'templates':templates,'template':template}
    
    def GetPHPConfig(self,version):
        #取PHP配置
        file = self.setupPath + "/php/"+version+"/etc/php.ini"
        phpini = public.readFile(file)
        file = self.setupPath + "/php/"+version+"/etc/php-fpm.conf"
        phpfpm = public.readFile(file)
        data = {}
        try:
            rep = "upload_max_filesize\s*=\s*([0-9]+)M"
            tmp = re.search(rep,phpini).groups()
            data['max'] = tmp[0]
        except:
            data['max'] = '50'
        try:
            rep = "request_terminate_timeout\s*=\s*([0-9]+)\n"
            tmp = re.search(rep,phpfpm).groups()
            data['maxTime'] = tmp[0]
        except:
            data['maxTime'] = 0
        
        try:
            rep = ur"\n;*\s*cgi\.fix_pathinfo\s*=\s*([0-9]+)\s*\n"
            tmp = re.search(rep,phpini).groups()
            
            if tmp[0] == '1':
                data['pathinfo'] = True
            else:
                data['pathinfo'] = False
        except:
            data['pathinfo'] = False
        
        return data

    
    def GetSystemTotal(self,get,interval = 1):
        #取系统统计信息
        data = self.GetMemInfo();
        cpu = self.GetCpuInfo(interval);
        data['cpuNum'] = cpu[1];
        data['cpuRealUsed'] = cpu[0];
        data['time'] = self.GetBootTime();
        data['system'] = self.GetSystemVersion();
        data['isuser'] = public.M('users').where('username=?',('admin',)).count();
        data['version'] = web.ctx.session.version;
        return data
    
    def GetLoadAverage(self,get):
        c = os.getloadavg()
        data = {};
        data['one'] = float(c[0]);
        data['five'] = float(c[1]);
        data['fifteen'] = float(c[2]);
        data['max'] = psutil.cpu_count() * 2;
        data['limit'] = data['max'];
        data['safe'] = data['max'] * 0.75;
        return data;
    
    def GetAllInfo(self,get):
        data = {}
        data['load_average'] = self.GetLoadAverage(get);
        data['title'] = self.GetTitle();
        data['network'] = self.GetNetWorkApi(get);
        data['panel_status'] = not os.path.exists('/www/server/panel/data/close.pl');
        import firewalls
        ssh_info = firewalls.firewalls().GetSshInfo(None)
        data['enable_ssh_status'] = ssh_info['status']
        data['disable_ping_status'] = not ssh_info['ping']
        data['time'] = self.GetBootTime();
        #data['system'] = self.GetSystemVersion();
        #data['mem'] = self.GetMemInfo();
        data['version'] = web.ctx.session.version;
        return data;
    
    def GetTitle(self):
        titlePl = 'data/title.pl';
        title = '宝塔Linux面板';
        if os.path.exists(titlePl): title = public.readFile(titlePl).strip();
        return title;
    
    def GetSystemVersion(self):
        #取操作系统版本
        import public
        version = public.readFile('/etc/redhat-release')
        if not version:
            version = public.readFile('/etc/issue').strip().split("\n")[0].replace('\\n','').replace('\l','').strip();
        else:
            version = version.replace('release ','').strip();
        return version
    
    def GetBootTime(self):
        #取系统启动时间
        import public,math
        conf = public.readFile('/proc/uptime').split()
        tStr = float(conf[0])
        min = tStr / 60;
        hours = min / 60;
        days = math.floor(hours / 24);
        hours = math.floor(hours - (days * 24));
        min = math.floor(min - (days * 60 * 24) - (hours * 60));
        return public.getMsg('SYS_BOOT_TIME',(str(int(days)),str(int(hours)),str(int(min))))
    
    def GetCpuInfo(self,interval = 1):
        #取CPU信息
        cpuCount = psutil.cpu_count()
        used = psutil.cpu_percent(interval=interval)
        return used,cpuCount
    
    def GetMemInfo(self,get=None):
        #取内存信息
        mem = psutil.virtual_memory()
        memInfo = {'memTotal':mem.total/1024/1024,'memFree':mem.free/1024/1024,'memBuffers':mem.buffers/1024/1024,'memCached':mem.cached/1024/1024}
        memInfo['memRealUsed'] = memInfo['memTotal'] - memInfo['memFree'] - memInfo['memBuffers'] - memInfo['memCached']
        return memInfo
    
    def GetDiskInfo(self,get=None):
        return self.GetDiskInfo2();
        #取磁盘分区信息
        diskIo = psutil.disk_partitions();
        diskInfo = []
        
        for disk in diskIo:
            if disk[1] == '/mnt/cdrom':continue;
            if disk[1] == '/boot':continue;
            tmp = {}
            tmp['path'] = disk[1]
            tmp['size'] = psutil.disk_usage(disk[1])
            diskInfo.append(tmp)
        return diskInfo
    
    def GetDiskInfo2(self):
        #取磁盘分区信息
        temp = public.ExecShell("df -h -P|grep '/'|grep -v tmpfs")[0];
        tempInodes = public.ExecShell("df -i -P|grep '/'|grep -v tmpfs")[0];
        temp1 = temp.split('\n');
        tempInodes1 = tempInodes.split('\n');
        diskInfo = [];
        n = 0
        cuts = ['/mnt/cdrom','/boot','/boot/efi','/dev','/dev/shm','/run/lock','/run','/run/shm','/run/user'];
        for tmp in temp1:
            n += 1
            inodes = tempInodes1[n-1].split();
            disk = tmp.split();
            if len(disk) < 5: continue;
            if disk[1].find('M') != -1: continue;
            if disk[1].find('K') != -1: continue;
            if len(disk[5].split('/')) > 4: continue;
            if disk[5] in cuts: continue;
            arr = {}
            arr['path'] = disk[5];
            tmp1 = [disk[1],disk[2],disk[3],disk[4]];
            arr['size'] = tmp1;
            arr['inodes'] = [inodes[1],inodes[2],inodes[3],inodes[4]]
            if disk[5] == '/':
                bootLog = '/tmp/panelBoot.pl';
                if disk[2].find('M') != -1:
                    if os.path.exists(bootLog): os.system('rm -f ' + bootLog);
                else:
                    if not os.path.exists(bootLog): os.system('sleep 1 && /etc/init.d/bt reload &');
            diskInfo.append(arr);
        return diskInfo;

    #清理系统垃圾
    def ClearSystem(self,get):
        count = total = 0;
        tmp_total,tmp_count = self.ClearMail();
        count += tmp_count;
        total += tmp_total;
        tmp_total,tmp_count = self.ClearOther();
        count += tmp_count;
        total += tmp_total;
        return count,total
    
    #清理邮件日志
    def ClearMail(self):
        rpath = '/var/spool';
        total = count = 0;
        import shutil
        con = ['cron','anacron','mail'];
        for d in os.listdir(rpath):
            if d in con: continue;
            dpath = rpath + '/' + d
            time.sleep(0.2);
            num = size = 0;
            for n in os.listdir(dpath):
                filename = dpath + '/' + n
                fsize = os.path.getsize(filename);
                size += fsize
                if os.path.isdir(filename):
                    shutil.rmtree(filename)
                else:
                    os.remove(filename)
                print '\t\033[1;32m[OK]\033[0m'
                num += 1
            total += size;
            count += num;
        return total,count
    
    #清理其它
    def ClearOther(self):
        clearPath = [
                     {'path':'/www/server/panel','find':'testDisk_'},
                     {'path':'/www/wwwlogs','find':'log'},
                     {'path':'/tmp','find':'panelBoot.pl'},
                     {'path':'/www/server/panel/install','find':'.rpm'}
                     ]
        
        total = count = 0;
        for c in clearPath:
            for d in os.listdir(c['path']):
                if d.find(c['find']) == -1: continue;
                filename = c['path'] + '/' + d;
                fsize = os.path.getsize(filename);
                total += fsize
                if os.path.isdir(filename):
                    shutil.rmtree(filename)
                else:
                    os.remove(filename)
                count += 1;
        public.serviceReload();
        os.system('echo > /tmp/panelBoot.pl');
        return total,count
    
    def GetNetWork(self,get=None):
        #return self.GetNetWorkApi(get);
        #取网络流量信息
        try:
            networkIo = psutil.net_io_counters()[:4]
            if not hasattr(web.ctx.session,'otime'):
                web.ctx.session.up   =  networkIo[0]
                web.ctx.session.down =  networkIo[1]
                web.ctx.session.otime = time.time();
            
            ntime = time.time();
            networkInfo = {}
            networkInfo['upTotal']   = networkIo[0]
            networkInfo['downTotal'] = networkIo[1]
            networkInfo['up']        = round(float(networkIo[0] - web.ctx.session.up) / 1024 / (ntime - web.ctx.session.otime),2)
            networkInfo['down']      = round(float(networkIo[1] - web.ctx.session.down) / 1024 / (ntime - web.ctx.session.otime),2)
            networkInfo['downPackets'] =networkIo[3]
            networkInfo['upPackets']   =networkIo[2]
            
            web.ctx.session.up   =  networkIo[0]
            web.ctx.session.down =  networkIo[1]
            web.ctx.session.otime = ntime;
            
            networkInfo['cpu'] = self.GetCpuInfo()
            networkInfo['load'] = self.GetLoadAverage(get);
            return networkInfo
        except:
            return None
        
    
    def GetNetWorkApi(self,get=None):
        #取网络流量信息
        try:
            tmpfile = 'data/network.temp';
            networkIo = psutil.net_io_counters()[:4]
            
            if not os.path.exists(tmpfile): 
                public.writeFile(tmpfile,str(networkIo[0])+'|'+str(networkIo[1])+'|' + str(int(time.time())));
                
            lastValue = public.readFile(tmpfile).split('|');
            
            ntime = time.time();
            networkInfo = {}
            networkInfo['upTotal']   = networkIo[0]
            networkInfo['downTotal'] = networkIo[1]
            networkInfo['up']        = round(float(networkIo[0] - int(lastValue[0])) / 1024 / (ntime - int(lastValue[2])),2)
            networkInfo['down']      = round(float(networkIo[1] - int(lastValue[1])) / 1024 / (ntime - int(lastValue[2])),2)
            networkInfo['downPackets'] =networkIo[3]
            networkInfo['upPackets']   =networkIo[2]
            
            public.writeFile(tmpfile,str(networkIo[0])+'|'+str(networkIo[1])+'|' + str(int(time.time())));
            
            #networkInfo['cpu'] = self.GetCpuInfo(0.1)
            return networkInfo
        except:
            return None
    
    def GetNetWorkOld(self):
        #取网络流量信息
        import time;
        pnet = public.readFile('/proc/net/dev');
        rep = '([^\s]+):[\s]{0,}(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)';
        pnetall = re.findall(rep,pnet);
        networkInfo = {}
        networkInfo['upTotal'] = networkInfo['downTotal'] = networkInfo['up'] = networkInfo['down'] = networkInfo['downPackets'] = networkInfo['upPackets'] = 0;
        for pnetInfo in pnetall:
            if pnetInfo[0] == 'io': continue;
            networkInfo['downTotal'] += int(pnetInfo[1]);
            networkInfo['downPackets'] += int(pnetInfo[2]);
            networkInfo['upTotal'] += int(pnetInfo[9]);
            networkInfo['upPackets'] += int(pnetInfo[10]);
        
        if not hasattr(web.ctx.session,'otime'):
            web.ctx.session.up   =  networkInfo['upTotal']
            web.ctx.session.down =  networkInfo['downTotal']
            web.ctx.session.otime = time.time();
        ntime = time.time();
        tmpDown = networkInfo['downTotal'] - web.ctx.session.down;
        tmpUp = networkInfo['upTotal'] - web.ctx.session.up;
        networkInfo['down'] = str(round(float(tmpDown) / 1024 / (ntime - web.ctx.session.otime),2));
        networkInfo['up']   = str(round(float(tmpUp) / 1024 / (ntime - web.ctx.session.otime),2));
        if networkInfo['down'] < 0: networkInfo['down'] = 0;
        if networkInfo['up'] < 0: networkInfo['up'] = 0;
        
        web.ctx.session.up   =  networkInfo['upTotal'];
        web.ctx.session.down =  networkInfo['downTotal'];
        web.ctx.session.otime = ntime;
        networkInfo['cpu'] = self.GetCpuInfo()
        return networkInfo;
    
    def ServiceAdmin(self,get=None):
        #服务管理
        
        if get.name == 'mysqld': public.CheckMyCnf();
        
        if get.name == 'phpmyadmin':
            import ajax
            get.status = 'True';
            ajax.ajax().setPHPMyAdmin(get);
            return public.returnMsg(True,'SYS_EXEC_SUCCESS');
        
        #检查httpd配置文件
        if get.name == 'apache' or get.name == 'httpd':
            get.name = 'httpd';
            if not os.path.exists(self.setupPath+'/apache/bin/apachectl'): return public.returnMsg(True,'SYS_NOT_INSTALL_APACHE');
            vhostPath = self.setupPath + '/panel/vhost/apache'
            if not os.path.exists(vhostPath):
                public.ExecShell('mkdir ' + vhostPath);
                public.ExecShell('/etc/init.d/httpd start');
            
            if get.type == 'start': 
                public.ExecShell('/etc/init.d/httpd stop');
                public.ExecShell('pkill -9 httpd');
                
            result = public.ExecShell('ulimit -n 10240 && ' + self.setupPath+'/apache/bin/apachectl -t');
            if result[1].find('Syntax OK') == -1:
                public.WriteLog("TYPE_SOFT",'SYS_EXEC_ERR', (str(result),));
                return public.returnMsg(False,'SYS_CONF_APACHE_ERR',(result[1].replace("\n",'<br>'),));
            
            if get.type == 'restart':
                public.ExecShell('pkill -9 httpd');
                public.ExecShell('/etc/init.d/httpd start');
            
        #检查nginx配置文件
        elif get.name == 'nginx':
            vhostPath = self.setupPath + '/panel/vhost/rewrite'
            if not os.path.exists(vhostPath): public.ExecShell('mkdir ' + vhostPath);
            vhostPath = self.setupPath + '/panel/vhost/nginx'
            if not os.path.exists(vhostPath):
                public.ExecShell('mkdir ' + vhostPath);
                public.ExecShell('/etc/init.d/nginx start');
            
            result = public.ExecShell('ulimit -n 10240 && nginx -t -c '+self.setupPath+'/nginx/conf/nginx.conf');
            if result[1].find('perserver') != -1:
                limit = self.setupPath + '/nginx/conf/nginx.conf';
                nginxConf = public.readFile(limit);
                limitConf = "limit_conn_zone $binary_remote_addr zone=perip:10m;\n\t\tlimit_conn_zone $server_name zone=perserver:10m;";
                nginxConf = nginxConf.replace("#limit_conn_zone $binary_remote_addr zone=perip:10m;",limitConf);
                public.writeFile(limit,nginxConf)
                public.ExecShell('/etc/init.d/nginx start');
                return public.returnMsg(True,'SYS_CONF_NGINX_REP');
            
            if result[1].find('proxy') != -1:
                import panelSite
                panelSite.panelSite().CheckProxy(get);
                public.ExecShell('/etc/init.d/nginx start');
                return public.returnMsg(True,'SYS_CONF_NGINX_REP');
            
            #return result
            if result[1].find('successful') == -1:
                public.WriteLog("TYPE_SOFT",'SYS_EXEC_ERR', (str(result),));
                return public.returnMsg(False,'SYS_CONF_NGINX_ERR',(result[1].replace("\n",'<br>'),));
        
        #执行
        execStr = "/etc/init.d/"+get.name+" "+get.type
        if execStr == '/etc/init.d/pure-ftpd reload': execStr = self.setupPath+'/pure-ftpd/bin/pure-pw mkdb '+self.setupPath+'/pure-ftpd/etc/pureftpd.pdb'
        if execStr == '/etc/init.d/pure-ftpd start': os.system('pkill -9 pure-ftpd');
        if execStr == '/etc/init.d/tomcat reload': execStr = '/etc/init.d/tomcat stop && /etc/init.d/tomcat start';
        if execStr == '/etc/init.d/tomcat restart': execStr = '/etc/init.d/tomcat stop && /etc/init.d/tomcat start';
        
        if get.name != 'mysqld':
            result = public.ExecShell(execStr);
        else:
            os.system(execStr);
            result = [];
            result.append('');
            result.append('');
        
        if result[1].find('nginx.pid') != -1:
            public.ExecShell('pkill -9 nginx && sleep 1');
            public.ExecShell('/etc/init.d/nginx start');
        if get.type != 'test':
            public.WriteLog("TYPE_SOFT", 'SYS_EXEC_SUCCESS',(execStr,));
        
        if len(result[1]) > 1 and get.name != 'pure-ftpd': return public.returnMsg(False, '<p>警告消息： <p>' + result[1].replace('\n','<br>'));
        return public.returnMsg(True,'SYS_EXEC_SUCCESS');
    
    def RestartServer(self,get):
        if not public.IsRestart(): return public.returnMsg(False,'EXEC_ERR_TASK');
        public.ExecShell("sync && /etc/init.d/bt stop && init 6 &");
        return public.returnMsg(True,'SYS_REBOOT');
    
    #释放内存
    def ReMemory(self,get):
        os.system('sync');
        scriptFile = 'script/rememory.sh'
        if not os.path.exists(scriptFile):
            public.downloadFile(web.ctx.session.home + '/script/rememory.sh',scriptFile);
        public.ExecShell("/bin/bash " + self.setupPath + '/panel/' + scriptFile);
        return self.GetMemInfo();
    
    #重启面板     
    def ReWeb(self,get):
        #if not public.IsRestart(): return public.returnMsg(False,'EXEC_ERR_TASK');
        public.ExecShell('/etc/init.d/bt restart &');
        return True
    
    #修复面板
    def RepPanel(self,get):
        vp = '';
        if public.readFile('/www/server/panel/class/common.py').find('checkSafe') != -1: vp = '_pro';
        public.ExecShell("wget -O update.sh " + public.get_url() + "/install/update"+vp+".sh && bash update.sh");
        if hasattr(web.ctx.session,'getCloudPlugin'): del(web.ctx.session['getCloudPlugin']);
        return True;
    
    #升级到专业版
    def UpdatePro(self,get):
        public.ExecShell("wget -O update.sh " + public.get_url() + "/install/update_pro.sh && bash update.sh pro");
        if hasattr(web.ctx.session,'getCloudPlugin'): del(web.ctx.session['getCloudPlugin']);
        return True;
        
        
        
        
        
        