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
import json
import time
import threading
import multiprocessing

import core.mw as mw
import thisdb


class sites(object):
    # lock
    _instance_lock = threading.Lock()

    @classmethod
    def instance(cls, *args, **kwargs):
        if not hasattr(sites, "_instance"):
            with sites._instance_lock:
                if not hasattr(sites, "_instance"):
                    sites._instance = sites(*args, **kwargs)
        return sites._instance

    def __init__(self):
        # nginx conf
        self.setupPath = mw.getServerDir() + '/web_conf'
        self.logsPath = mw.getLogsDir()

        self.vhostPath = vhost = self.setupPath + '/nginx/vhost'
        if not os.path.exists(vhost):
            mw.execShell("mkdir -p " + vhost + " && chmod -R 755 " + vhost)
        self.rewritePath = rewrite = self.setupPath + '/nginx/rewrite'
        if not os.path.exists(rewrite):
            mw.execShell("mkdir -p " + rewrite + " && chmod -R 755 " + rewrite)

        self.passPath = passwd = self.setupPath + '/nginx/pass'
        if not os.path.exists(passwd):
            mw.execShell("mkdir -p " + passwd + " && chmod -R 755 " + passwd)

        self.redirectPath = redirect = self.setupPath + '/nginx/redirect'
        if not os.path.exists(redirect):
            mw.execShell("mkdir -p " + redirect +" && chmod -R 755 " + redirect)

        self.proxyPath = proxy = self.setupPath + '/nginx/proxy'
        if not os.path.exists(proxy):
            mw.execShell("mkdir -p " + proxy + " && chmod -R 755 " + proxy)

        # ssl conf
        self.sslDir = self.setupPath + '/ssl'
        self.sslLetsDir = self.setupPath + '/letsencrypt'
        if not os.path.exists(self.sslLetsDir):
            mw.execShell("mkdir -p " + self.sslLetsDir +" && chmod -R 755 " + self.sslLetsDir)

    # 域名编码转换
    def toPunycode(self, domain):
        if sys.version_info[0] == 2:
            domain = domain.encode('utf8')
        tmp = domain.split('.')
        newdomain = ''
        for dkey in tmp:
            # 匹配非ascii字符
            match = re.search(u"[\x80-\xff]+", dkey)
            if not match:
                newdomain += dkey + '.'
            else:
                newdomain += 'xn--' + dkey.decode('utf-8').encode('punycode') + '.'
        return newdomain[0:-1]

    # 中文路径处理
    def toPunycodePath(self, path):
        if sys.version_info[0] == 2:
            path = path.encode('utf-8')
        if os.path.exists(path):
            return path
        match = re.search(u"[\x80-\xff]+", path)
        if not match:
            return path
        npath = ''
        for ph in path.split('/'):
            npath += '/' + self.toPunycode(ph)
        return npath.replace('//', '/')

    def getHostConf(self, siteName):
        return self.vhostPath + '/' + siteName + '.conf'

    def saveHostConf(self, path, data, encoding):
        import utils.file as file
        mw.backFile(path)
        rdata = file.saveBody(path, data, encoding)

        if rdata['status']:
            isError = mw.checkWebConfig()
            if isError != True:
                mw.restoreFile(path)
                msg = 'ERROR: 检测到配置文件有错误,请先排除后再操作<br><br><a style="color:red;">' + isError.replace("\n", '<br>') + '</a>'
                return mw.returnData(False, msg)
            mw.restartWeb()
            mw.removeBackFile(path)
        return rdata

    def getRewriteConf(self, siteName):
        return self.rewritePath + '/' + siteName + '.conf'

    def getRedirectDataPath(self, siteName):
        return "{}/{}/data.json".format(self.redirectPath, siteName)

    def getRedirectPath(self, siteName):
        return "{}/{}".format(self.redirectPath, siteName)

    def getProxyDataPath(self, siteName):
        return "{}/{}/data.json".format(self.proxyPath, siteName)

    def getProxyPath(self, siteName):
        return "{}/{}".format(self.proxyPath, siteName)

    def getDirBindRewrite(self, site_name, dir_name):
        return self.rewritePath + '/' + site_name + '_' + dir_name + '.conf'

    def getIndexConf(self):
        return mw.getServerDir() + '/openresty/nginx/conf/nginx.conf'


    # 路径处理
    def getPath(self, path):
        if path[-1] == '/':
            return path[0:-1]
        return path

    def createRootDir(self, path):
        autoInit = False
        if not os.path.exists(path):
            autoInit = True
            os.makedirs(path)
        if not mw.isAppleSystem():
            mw.execShell('chown -R www:www ' + path)

        if autoInit:
            mw.writeFile(path + '/index.html', 'Work has started!!!')
            mw.execShell('chmod -R 755 ' + path)

    def add(self, webname, port, ps, path, version):
        site_root_dir = mw.getWwwDir()
        if site_root_dir == path.rstrip('/'):
            return mw.returnData(False, '不要以网站根目录创建站点!')

        print(webname, port, ps, path, version)
        siteMenu = json.loads(webname)

        self.siteName = self.toPunycode(siteMenu['domain'].strip().split(':')[0]).strip()
        self.sitePath = self.toPunycodePath(self.getPath(path.replace(' ', '')))
        self.sitePort = port.strip().replace(' ', '')
        self.phpVersion = version

        if thisdb.isSitesExist(self.siteName):
            return mw.returnData(False, '您添加的站点[%s]已存在!' % self.siteName)

        pid = thisdb.addSites(self.siteName, self.sitePath)
        if pid < 1:
            return mw.returnData(False, '添加失败!') 


        self.createRootDir(self.sitePath)
        self.nginxAddConf()

        # 主域名配置
        thisdb.addDomain(pid, self.siteName, self.sitePort)

        # 绑定域名配置

        # 添加更多域名
        # for domain in siteMenu['domainlist']:
        #     thisdb.addDomain(pid, self.siteName, self.sitePort)

        mw.restartWeb()
        # return mw.returnData(False, '开发中!')
        return mw.returnData(True, '添加成功')


    def deleteALlLogs(self, webname):
        assLogPath = mw.getLogsDir() + '/' + webname + '.log'
        errLogPath = mw.getLogsDir() + '/' + webname + '.error.log'
        confFile = self.setupPath + '/nginx/vhost/' + webname + '.conf'
        rewriteFile = self.setupPath + '/nginx/rewrite/' + webname + '.conf'
        passFile = self.setupPath + '/nginx/pass/' + webname + '.conf'
        keyPath = self.sslDir + webname + '/privkey.pem'
        certPath = self.sslDir + webname + '/fullchain.pem'
        logs = [assLogPath,
                errLogPath,
                confFile,
                rewriteFile,
                passFile,
                keyPath,
                certPath]
        for i in logs:
            mw.deleteFile(i)

        # 重定向目录
        redirectDir = self.setupPath + '/nginx/redirect/' + webname
        if os.path.exists(redirectDir):
            mw.execShell('rm -rf ' + redirectDir)
        # 代理目录
        proxyDir = self.setupPath + '/nginx/proxy/' + webname
        if os.path.exists(proxyDir):
            mw.execShell('rm -rf ' + proxyDir)

    def delete(self, site_id, path):
        info = thisdb.getSitesById(site_id)
        webname = info['name']
        self.deleteALlLogs(webname)

        if path == '1':
            web_root_path = mw.getWwwDir() + '/' + webname
            mw.execShell('rm -rf ' + web_root_path)

        # ssl
        ssl_dir = self.sslDir + '/' + webname
        if os.path.exists(ssl_dir):
            mw.execShell('rm -rf ' + ssl_dir)

        ssl_lets_dir = self.sslLetsDir + '/' + webname
        if os.path.exists(ssl_lets_dir):
            mw.execShell('rm -rf ' + ssl_lets_dir)

        ssl_acme_dir = mw.getAcmeDir() + '/' + webname
        if os.path.exists(ssl_acme_dir):
            mw.execShell('rm -rf ' + ssl_acme_dir)

        thisdb.deleteSitesById(site_id)
        thisdb.deleteDomainBySiteId(site_id)

        binding_list = thisdb.getBindingListBySiteId(site_id)
        for x in binding_list:
            tag = mw.getLogsDir() + "/" + webname + "_" + x['domain']
            site_log = tag + ".log"
            site_error = tag + ".error.log"

            if os.path.exists(site_log):
                mw.execShell('rm -rf ' + site_log)
            if os.path.exists(site_error):
                mw.execShell('rm -rf ' + site_error)

        thisdb.deleteBindingBySiteId(site_id)
        mw.restartWeb()
        return mw.returnData(True, '站点【%s】删除成功!' % webname)

    def nginxAddConf(self):
        source_tpl = mw.getPanelDir() + '/data/tpl/nginx.conf'
        vhost_file = self.getHostConf(self.siteName)
        content = mw.readFile(source_tpl)

        content = content.replace('{$PORT}', self.sitePort)
        content = content.replace('{$SERVER_NAME}', self.siteName)
        content = content.replace('{$ROOT_DIR}', self.sitePath)
        content = content.replace('{$PHP_DIR}', self.setupPath + '/php')
        content = content.replace('{$PHPVER}', self.phpVersion)
        content = content.replace('{$OR_REWRITE}', self.rewritePath)
        # content = content.replace('{$OR_REDIRECT}', self.redirectPath)
        # content = content.replace('{$OR_PROXY}', self.proxyPath)

        logsPath = mw.getLogsDir()
        content = content.replace('{$LOGPATH}', logsPath)
        mw.writeFile(vhost_file, content)

        # 和反代配置冲突 && 默认伪静态为空
#         rewrite_content = '''
# location /{
#     if ($PHP_ENV != "1"){
#         break;
#     }

#     if (!-e $request_filename) {
#        rewrite  ^(.*)$  /index.php/$1  last;
#        break;
#     }
# }
# '''
        rewrite_file = self.getRewriteConf(self.siteName)
        mw.writeFile(rewrite_file, '')

    # 设置网站过期
    def setEndDate(self, site_id, end_date):
        info = thisdb.getSitesById(site_id)
        thisdb.setSitesData(site_id, edate=end_date)
        mw.writeLog('网站管理', '设置成功,站点【{1}】到期【{2}】后将自动停止!', (info['name'], end_date,))
        return mw.returnData(True, '设置成功,站点到期后将自动停止!')

    # 设置网站备注
    def setPs(self, site_id, ps):
        if thisdb.setSitesData(site_id, ps=ps):
            return mw.returnData(True, '修改成功!')
        return mw.returnData(False, '修改失败!')

    # 获取默认站点
    def getDefaultSite(self):
        data = {}
        data['sites'] = mw.M('sites').field('name').order('id desc').select()
        data['default_site'] = thisdb.getOption('default_site', default='')
        return data

    # 获取域名列表
    def getDomain(self, pid):
        data =  thisdb.getDomainByPid(pid)
        return data

    # 获取日志内容
    def getLogs(self, siteName):
        logPath = mw.getLogsDir() + '/' + siteName + '.log'
        if not os.path.exists(logPath):
            return mw.returnData(False, '日志为空')
        return mw.returnData(True, mw.getLastLine(logPath, 100))

    # 获取错误日志内容
    def getErrorLogs(self, siteName):
        logPath = mw.getLogsDir() + '/' + siteName + '.error.log'
        if not os.path.exists(logPath):
            return mw.returnData(False, '日志为空')
        return mw.returnData(True, mw.getLastLine(logPath, 100))

    # 获取模版名内容
    def getRewriteTpl(self, tplname):
        file = mw.getPanelDir() + '/rewrite/nginx/' + tplname + '.conf'
        if not os.path.exists(file):
            return mw.returnData(False, '模版不存在!')
        return mw.returnData(True, 'OK', file)

    def getRewriteList(self):
        rewriteList = {}
        rewriteList['rewrite'] = []
        rewriteList['rewrite'].append('0.当前')
        rewrite_nginx_dir = mw.getPanelDir() + '/rewrite/nginx'
        for ds in os.listdir(rewrite_nginx_dir):
            rewriteList['rewrite'].append(ds[0:len(ds) - 5])
        rewriteList['rewrite'] = sorted(rewriteList['rewrite'])
        return rewriteList

    # 取日志状态
    def getLogsStatus(self, siteName):
        filename = self.getHostConf(siteName)
        conf = mw.readFile(filename)
        if conf.find('#ErrorLog') != -1:
            return False
        if conf.find("access_log  off") != -1:
            return False
        return True

    # 取目录加密状态
    def getHasPwd(self, siteName):
        filename = self.getHostConf(siteName)
        conf = mw.readFile(filename)
        if conf.find('#AUTH_START') != -1:
            return True
        return False

    # 取当站点前运行目录
    def getSiteRunPath(self, site_name, site_path):
        filename = self.getHostConf(site_name)
        if os.path.exists(filename):
            conf = mw.readFile(filename)
            rep = r'\s*root\s*(.+);'
            path = re.search(rep, conf).groups()[0]

        data = {}
        if site_path == path:
            data['path'] = '/'
        else:
            data['path'] = path.replace(site_path, '')

        dirnames = []
        dirnames.append('/')
        for filename in os.listdir(site_path):
            try:
                file_path = site_path + '/' + filename
                if os.path.islink(file_path):
                    continue
                if os.path.isdir(file_path):
                    dirnames.append('/' + filename)
            except:
                pass

        data['dirs'] = dirnames
        return data

    def getDirUserIni(self, site_id):

        info = thisdb.getSitesById(site_id)

        path = info['path']
        name = info['name']
        data = {}
        data['logs'] = self.getLogsStatus(name)
        data['run_path'] = self.getSiteRunPath(name, path)

        data['user_ini'] = False
        if os.path.exists(path + '/.user.ini'):
            data['user_ini'] = True

        if data['run_path']['path'] != '/':
            user_ini = path + data['run_path']['path'] + '/.user.ini'
            if os.path.exists(user_ini):
                data['userini'] = True

        data['pass'] = self.getHasPwd(name)
        data['path'] = path
        data['name'] = name
        return mw.returnData(True, 'OK', data)

    # 清除多余user.ini
    def delUserInI(self, path, up=0):
        filename = path + '/.user.ini'
        if os.path.exists(filename):
            mw.execShell("which chattr && chattr -i " + filename)
            os.remove(filename)
        
        for f in os.listdir(path):
            try:
                npath = path + '/' + f
                if os.path.isdir(npath):
                    if up < 100:
                        self.delUserInI(npath, up + 1)

                user_ini = npath + '/.user.ini'
                print('ff:',user_ini)
                if not os.path.exists(user_ini):
                    continue
                mw.execShell('which chattr && chattr -i ' + user_ini)
                os.remove(user_ini)
            except:
                continue
        return True


    # 设置目录防御
    def addDirUserIni(self, site_path, run_path):
        new_path = site_path + run_path
        filename = new_path + '/.user.ini'
        if os.path.exists(filename):
            return mw.returnData(True, '已打开防跨站设置!')

        open_path = 'open_basedir={}/:{}/'.format(new_path, site_path)
        if run_path == '/' or run_path == '':
            open_path = 'open_basedir={}/'.format(site_path)

        mw.writeFile(filename, open_path + ':/www/server/php:/tmp/:/proc/')
        mw.execShell("which chattr && chattr +i " + filename)

    def setDirUserIni(self, site_path, run_path):
        filename = site_path + '/.user.ini'
        if os.path.exists(filename):
            self.delUserInI(site_path)
            return mw.returnData(True, '已清除防跨站设置!')
        self.addDirUserIni(site_path, run_path)
        return mw.returnData(True, '已打开防跨站设置!')


    def getDirBinding(self, site_id):
        info = thisdb.getSitesById(site_id)
        path = info['path']
        if not os.path.exists(path):
            checks = ['/', '/usr', '/etc']
            if path in checks:
                data = {}
                data['dirs'] = []
                data['binding'] = []
                return mw.returnData(True, 'OK', data)
            os.system('mkdir -p ' + path)
            os.system('chmod 755 ' + path)
            os.system('chown www:www ' + path)
            siteName = info['name']
            mw.writeLog('网站管理', '站点[' + siteName + '],根目录[' + path + ']不存在,已重新创建!')

        dirnames = []
        for filename in os.listdir(path):
            try:
                filePath = path + '/' + filename
                if os.path.islink(filePath):
                    continue
                if os.path.isdir(filePath):
                    dirnames.append(filename)
            except:
                pass

        data = {}
        data['dirs'] = dirnames
        data['binding'] = thisdb.getBindingListBySiteId(site_id)
        return mw.returnJson(True, 'OK', data)

    def addDirBind(self, site_id, domain, dir_name):
        domain_split = domain.split(':')
        domain = domain_split[0]
        port = '80'
        if len(domain_split) > 1:
            port = domain_split[1]
        if dir_name == '':
            mw.returnData(False, '目录不能为空!')

        reg = r"^([\w\-\*]{1,100}\.){1,4}(\w{1,10}|\w{1,10}\.\w{1,10})$"
        if not re.match(reg, domain):
            return mw.returnData(False, '主域名格式不正确!')

        info = thisdb.getSitesById(site_id)
        webdir = info['path'] + '/' + dir_name

        if thisdb.getBindingCountByDomain(domain):
            return mw.returnData(False, '您添加的域名在子目录已存在!')

        if thisdb.getDomainCountByName(domain) > 0:
            return mw.returnData(False, '您添加的域名已存在!')

        filename = self.getHostConf(info['name'])
        conf = mw.readFile(filename)
        if conf:
            rep = r"enable-php-([0-9]{2,3})\.conf"
            domain_split = re.search(rep, conf).groups()
            version = domain_split[0]

            source_dirbind_tpl = mw.getPanelDir() + '/data/tpl/nginx_dirbind.conf'
            content = mw.readFile(source_dirbind_tpl)
            content = content.replace('{$PORT}', port)
            content = content.replace('{$PHPVER}', version)
            content = content.replace('{$DIRBIND}', domain)
            content = content.replace('{$ROOT_DIR}', webdir)
            content = content.replace('{$SERVER_MAIN}', info['name'])
            content = content.replace('{$OR_REWRITE}', self.rewritePath)
            content = content.replace('{$PHP_DIR}', self.setupPath + '/php')
            content = content.replace('{$LOGPATH}', mw.getLogsDir())

            conf += "\r\n" + content
            mw.backFile(filename)
            mw.writeFile(filename, conf)
        conf = mw.readFile(filename)

        # 检查配置是否有误
        isError = mw.checkWebConfig()
        if isError != True:
            mw.restoreFile(filename)
            msg = 'ERROR: <br><a style="color:red;">' + isError.replace("\n", '<br>') + '</a>'
            return mw.returnData(False, msg)

        thisdb.addBinding(site_id,domain,port,dir_name)
        msg = mw.getInfo('网站[{1}]子目录[{2}]绑定到[{3}]',(info['name'], dir_name, domain))
        mw.writeLog('网站管理', msg)
        mw.restartWeb()
        mw.removeBackFile(filename)
        return mw.returnData(True, '添加成功!')

    # 取子目录Rewrite
    def getDirBindingRewrite(self, binding_id, add):
        binding_info = thisdb.getBindingById(binding_id)
        info = thisdb.getSitesById(binding_info['pid'])

        filename = self.getDirBindRewrite(info['name'], binding_info['path'])
        if add == '1':
            mw.writeFile(filename, '')
            file = self.getHostConf(info['name'])
            conf = mw.readFile(file)
            domain = binding_info['domain']
            rep = "\n#BINDING-" + domain + "-START(.|\n)+BINDING-" + domain + "-END"
            tmp = re.search(rep, conf).group()
            dirConf = tmp.replace('rewrite/' + info['name'] + '.conf;', 'rewrite/' + info['name'] + '_' + binding_info['path'] + '.conf;')
            conf = conf.replace(tmp, dirConf)
            mw.writeFile(file, conf)
        data = {}
        data['rewrite_dir'] = self.rewritePath
        data['status'] = False
        if os.path.exists(filename):
            data['status'] = True
            data['data'] = mw.readFile(filename)
            data['rlist'] = []
            for ds in os.listdir(self.rewritePath):
                if ds[0:1] == '.':
                    continue
                if ds == 'list.txt':
                    continue
                data['rlist'].append(ds[0:len(ds) - 5])
            data['filename'] = filename
        return data

    def delDirBinding(self, binding_id):

        binding_info = thisdb.getBindingById(binding_id)
        info = thisdb.getSitesById(binding_info['pid'])

        filename = self.getHostConf(info['name'])
        conf = mw.readFile(filename)
        if conf:
            rep = r"\s*.+BINDING-" + binding_info['domain'] + "-START(.|\n)+BINDING-" + binding_info['domain'] + "-END"
            conf = re.sub(rep, '', conf)
            mw.writeFile(filename, conf)

        filename = self.getDirBindRewrite(info['name'],  binding_info['path'])
        if os.path.exists(filename):
            os.remove(filename)
        
        msg = mw.getInfo('删除网站[{1}]子目录[{2}]绑定',(info['name'], binding_info['path']))
        mw.writeLog('网站管理', msg)
        mw.restartWeb()

        thisdb.deleteBindingById(binding_id)
        return mw.returnJson(True, '删除成功!')


    def logsOpen(self, site_id):
        info = thisdb.getSitesById(site_id)
        name = info['name']

        filename = self.getHostConf(name)
        if os.path.exists(filename):
            conf = mw.readFile(filename)
            rep = self.logsPath + '/' + name + '.log'
            if conf.find(rep) != -1:
                conf = conf.replace(rep + ' main', 'off')
            else:
                conf = conf.replace('access_log  off', 'access_log  ' + rep + ' main')
            mw.writeFile(filename, conf)

        mw.restartWeb()
        return mw.returnData(True, '操作成功!')

    def setSitePath(self, site_id, path):
        path = self.getPath(path)
        if path == "" or site_id == '0':
            return mw.returnData(False,  "目录不能为空!")

        import utils.file as file
        if not file.checkDir(path):
            return mw.returnData(False,  "不能以系统关键目录作为站点目录")

        info = thisdb.getSitesById(site_id)
        if info['path'] == path:
            return mw.returnData(False,  "与原路径一致，无需修改!")
        conf_file = self.getHostConf(info['name'])
        content = mw.readFile(conf_file)
        if content:
            content = content.replace(info['path'], path)
            mw.writeFile(file, content)

        thisdb.setSitesData(site_id, path=path)
        msg = mw.getInfo('修改网站[{1}]物理路径成功!', (info['name'],))
        mw.writeLog('网站管理', msg)
        mw.restartWeb()
        return mw.returnData(True,  "设置成功!")

    # 设置当前站点运行目录
    def setSiteRunPath(self, site_id, run_path):
        info = thisdb.getSitesById(site_id)
        site_name = info['name']
        site_path = info['path']

        new_path = site_path + run_path

        # 处理Nginx
        filename = self.getHostConf(site_name)
        if os.path.exists(filename):
            conf = mw.readFile(filename)
            rep = r'\s*root\s*(.+);'
            path = re.search(rep, conf).groups()[0]
            conf = conf.replace(path, new_path)
            mw.writeFile(filename, conf)

        self.setSitePath(site_path, run_path)
        mw.restartWeb()
        return mw.returnData(True, '设置成功!')

    # 设置目录加密
    def setHasPwd(self, site_id, username, password):
        if len(username.strip()) == 0 or len(password.strip()) == 0:
            return mw.returnData(False, '用户名或密码不能为空!')

        info = thisdb.getSitesById(site_id)
        siteName = info['name']
        filename = self.passPath + '/' + siteName + '.pass'
        passconf = username + ':' + mw.hasPwd(password)

        configFile = self.getHostConf(siteName)
        # 处理Nginx配置
        conf = mw.readFile(configFile)
        if conf:
            rep = '#error_page   404   /404.html;'
            if conf.find(rep) == -1:
                rep = '#error_page 404/404.html;'
            data = '''
    #AUTH_START
    auth_basic "Authorization";
    auth_basic_user_file %s;
    #AUTH_END''' % (filename,)
            conf = conf.replace(rep, rep + data)
            mw.writeFile(configFile, conf)
        # 写密码配置
        passDir = self.passPath
        if not os.path.exists(passDir):
            mw.execShell('mkdir -p ' + passDir)
        mw.writeFile(filename, passconf)

        msg = mw.getInfo('设置网站[{1}]为需要密码认证!', (siteName,))
        mw.writeLog("网站管理", msg)
        mw.restartWeb()
        return mw.returnData(True, '设置成功!')

    # 取消目录加密
    def closeHasPwd(self, site_id):
        info = thisdb.getSitesById(site_id)
        siteName = info['name']
        configFile = self.getHostConf(siteName)
        if os.path.exists(configFile):
            conf = mw.readFile(configFile)
            rep = r"\n\s*#AUTH_START(.|\n){1,200}#AUTH_END"
            conf = re.sub(rep, '', conf)
            mw.writeFile(configFile, conf)

        msg = mw.getInfo('清除网站[{1}]的密码认证!', (siteName,))
        mw.writeLog("网站管理", msg)
        mw.restartWeb()
        return mw.returnData(True, '设置成功!')

    def getSecurity(self, site_id):
        info = thisdb.getSitesById(site_id)
        name = info['name']
        filename = self.getHostConf(name)
        conf = mw.readFile(filename)
        data = {}
        if conf.find('SECURITY-START') != -1:
            rep = "#SECURITY-START(\n|.){1,500}#SECURITY-END"
            tmp = re.search(rep, conf).group()
            data['fix'] = re.search(r"\(.+\)\$", tmp).group().replace('(', '').replace(')$', '').replace('|', ',')

            data['status'] = False
            data['none'] = False

            valid_referers = re.search(r"valid_referers\s+(.+);\n", tmp)
            valid_referers_none = re.search(r"valid_referers\s+none\s+blocked\s+(.+);\n", tmp)

            if valid_referers or valid_referers_none:
                data['status'] = True

            if valid_referers_none:
                domain_t = valid_referers_none.groups()[0].split()
                data['domains'] = ','.join(domain_t)
                data['none'] = True
            elif valid_referers:
                domain_t = valid_referers.groups()[0].split()
                data['domains'] = ','.join(domain_t)
                data['none'] = False
        else:
            data['fix'] = 'gif|jpg|jpeg|png|bmp|swf|js|css|ttf|woff2'
            domains = thisdb.getDomainByPid(site_id)
            tmp = []
            for domain in domains:
                tmp.append(domain['name'])
            data['domains'] = ','.join(tmp)
            data['status'] = False
            data['none'] = False
        return data

    def setSecurity(self, site_id, fix, domains, status, none=''):
        info = thisdb.getSitesById(site_id)
        name = info['name']

        if len(fix) < 2:
            return mw.returnData(False, 'URL后缀不能为空!')

        file = self.getHostConf(name)
        if os.path.exists(file):
            conf = mw.readFile(file)
            if status == 'false':
                rep = r"\s{0,4}#SECURITY-START(\n|.){1,500}#SECURITY-END\n?"
                conf = re.sub(rep, '', conf)
                mw.writeLog('网站管理', '站点[' + name + ']已关闭防盗链设置!')
            else:
                rep = r"\s{0,4}#SECURITY-START(\n|.){1,500}#SECURITY-END\n?"
                conf = re.sub(rep, '', conf)

                valid_referers = domains.strip().replace(',', ' ')
                if none == 'true':
                    valid_referers = 'none blocked ' + valid_referers

                pre_path = self.setupPath + "/php/conf"
                re_path = r"include\s+" + pre_path + "/enable-php-"
                rconf = r'''#SECURITY-START 防盗链配置
    location ~ .*\.(%s)$
    {
        expires      30d;
        access_log /dev/null;
        valid_referers %s;
        if ($invalid_referer){
           return 404;
        }
    }
    #SECURITY-END
    include %s/enable-php-''' % (fix.strip().replace(',', '|'), valid_referers, pre_path)
                conf = re.sub(re_path, rconf, conf)
                mw.writeLog('网站管理', '站点[' + name + ']已开启防盗链!')
            mw.writeFile(file, conf)
        mw.restartWeb()
        return mw.returnData(True, '设置成功!')

    def getSitePhpVersion(self, siteName):
        conf = mw.readFile(self.getHostConf(siteName))
        rep = r"enable-php-(.*)\.conf"
        find_php_cnf = re.search(rep, conf)

        def_pver = '00'
        if find_php_cnf:
            tmp = find_php_cnf.groups()
            def_pver = tmp[0]
            
        data = {}
        data['phpversion'] = def_pver
        return data

    def getIndex(self, site_id):
        info = thisdb.getSitesById(site_id)
        file = self.getHostConf(info['name'])
        conf = mw.readFile(file)
        rep = r"\s+index\s+(.+);"
        tmp = re.search(rep, conf).groups()
        return tmp[0].replace(' ', ',')

    def setIndex(self, site_id, index):
        if index.find('.') == -1:
            return mw.returnData(False,  '默认文档格式不正确，例：index.html')

        index = index.replace(' ', '')
        index = index.replace(',,', ',')

        if len(index) < 3:
            return mw.returnData(False,  '默认文档不能为空!')

        info = thisdb.getSitesById(site_id)
        siteName = info['name']
        index_l = index.replace(",", " ")
        file = self.getHostConf(siteName)
        conf = mw.readFile(file)
        if conf:
            rep = r"\s+index\s+.+;"
            conf = re.sub(rep, "\n\tindex " + index_l + ";", conf)
            mw.writeFile(file, conf)

        mw.writeLog('网站管理', '站点[{1}]设置{2}成功', (siteName, index_l))
        return mw.returnJson(True,  '设置成功!')

    def getLimitNet(self, site_id):
        info = thisdb.getSitesById(site_id)
        siteName = info['name']
        filename = self.getHostConf(siteName)
        # 站点总并发
        data = {}
        conf = mw.readFile(filename)
        try:
            rep = r"\s+limit_conn\s+perserver\s+([0-9]+);"
            tmp = re.search(rep, conf).groups()
            data['perserver'] = int(tmp[0])

            # IP并发限制
            rep = r"\s+limit_conn\s+perip\s+([0-9]+);"
            tmp = re.search(rep, conf).groups()
            data['perip'] = int(tmp[0])

            # 请求并发限制
            rep = r"\s+limit_rate\s+([0-9]+)\w+;"
            tmp = re.search(rep, conf).groups()
            data['limit_rate'] = int(tmp[0])
        except:
            data['perserver'] = 0
            data['perip'] = 0
            data['limit_rate'] = 0
        return data

    def setLimitNet(self, site_id, perserver, perip, limit_rate):
        str_perserver = 'limit_conn perserver ' + perserver + ';'
        str_perip = 'limit_conn perip ' + perip + ';'
        str_limit_rate = 'limit_rate ' + limit_rate + 'k;'

        info = thisdb.getSitesById(site_id)
        siteName = info['name']

        filename = self.getHostConf(siteName)
        conf = mw.readFile(filename)
        if(conf.find('limit_conn perserver') != -1):
            # 替换总并发
            rep = r"limit_conn\s+perserver\s+([0-9]+);"
            conf = re.sub(rep, str_perserver, conf)

            # 替换IP并发限制
            rep = r"limit_conn\s+perip\s+([0-9]+);"
            conf = re.sub(rep, str_perip, conf)

            # 替换请求流量限制
            rep = r"limit_rate\s+([0-9]+)\w+;"
            conf = re.sub(rep, str_limit_rate, conf)
        else:
            conf = conf.replace('#error_page 404/404.html;', "#error_page 404/404.html;\n    " +
                                str_perserver + "\n    " + str_perip + "\n    " + str_limit_rate)

        mw.writeFile(filename, conf)
        mw.restartWeb()
        mw.writeLog('网站管理', '网站[{1}]流量限制已开启!', (siteName,))
        return mw.returnData(True, '设置成功!')
        
    def closeLimitNet(self, site_id):
        info = thisdb.getSitesById(site_id)
        siteName = info['name']

        filename = self.getHostConf(siteName)
        conf = mw.readFile(filename)
        # 清理总并发
        rep = r"\s+limit_conn\s+perserver\s+([0-9]+);"
        conf = re.sub(rep, '', conf)

        # 清理IP并发限制
        rep = r"\s+limit_conn\s+perip\s+([0-9]+);"
        conf = re.sub(rep, '', conf)

        # 清理请求流量限制
        rep = r"\s+limit_rate\s+([0-9]+)\w+;"
        conf = re.sub(rep, '', conf)
        mw.writeFile(filename, conf)
        mw.restartWeb()
        mw.writeLog('网站管理', '网站[{1}]流量限制已关闭!', (siteName,))
        return mw.returnData(True, '已关闭流量限制!')


    # 获取重定向配置
    def getRedirect(self, siteName):
        redirect_file = self.getRedirectDataPath(siteName)
        if not os.path.exists(redirect_file):
            mw.execShell("mkdir {}/{}".format(self.redirectPath, siteName))
            return mw.returnData(True, "no exists!", {"result": [], "count": 0})

        content = mw.readFile(redirect_file)
        data = json.loads(content)
        # 处理301信息
        return mw.returnData(True, "ok", {"result": data, "count": len(data)})

    # 操作 重定向配置
    def operateRedirectConf(self, siteName, method='start'):
        vhost_file = self.getHostConf(siteName)
        content = mw.readFile(vhost_file)

        cnf_301 = '''#301-START
    include %s/*.conf;
    #301-END''' % (self.getRedirectPath( siteName))

        cnf_301_source = '#301-START'
        # print('operateRedirectConf', content.find('#301-END'))
        if content.find('#301-END') != -1:
            if method == 'stop':
                rep = '#301-START(\n|.){1,500}#301-END'
                content = re.sub(rep, '#301-START', content)
        else:
            if method == 'start':
                content = re.sub(cnf_301_source, cnf_301, content)

        mw.writeFile(vhost_file, content)

    # get redirect status
    def setRedirect(self, siteName, site_from, to, type, r_type, keep_path):
        if siteName == '' or site_from == '' or to == '' or type == '' or r_type == '':
            return mw.returnData(False, "必填项不能为空!")

        redirect_file = self.getRedirectDataPath(siteName)
        content = mw.readFile(redirect_file) if os.path.exists(redirect_file) else ""
        data = json.loads(content) if content != "" else []

        _r_type = 0 if r_type == "301" else 1
        _type_code = 0 if type == "path" else 1
        _keep_path = 1 if keep_path == "1" else 0

        # check if domain exists in site
        if _type_code == 1:
            pid = mw.M('domain').where("name=?", (_siteName,)).field('id,pid,name,port,addtime').select()
            site_domain_lists = mw.M('domain').where("pid=?", (pid[0]['pid'],)).field('name').select()
            found = False
            for item in site_domain_lists:
                if item['name'] == _from:
                    found = True
                    break
            if found == False:
                return mw.returnData(False, "域名不存在!")

        file_content = ""
        # path
        if _type_code == 0:
            redirect_type = "permanent" if _r_type == 0 else "redirect"
            if not site_from.startswith("/"):
                site_from = "/{}".format(site_from)
            if _keep_path == 1:
                to = "{}$1".format(to)
                site_from = "{}(.*)".format(site_from)
            file_content = "rewrite ^{} {} {};".format(site_from, to, redirect_type)
        # domain
        else:
            if _keep_path == 1:
                _to = "{}$request_uri".format(_to)

            redirect_type = "301" if _type_code == 0 else "302"
            _if = "if ($host ~ '^{}')".format(site_from)
            _return = "return {} {}; ".format(redirect_type, to)
            file_content = _if + "{\r\n    " + _return + "\r\n}"

        _id = mw.md5("{}+{}".format(file_content, siteName))

        # 防止规则重复
        for item in data:
            if item["r_from"] == site_from:
                return mw.returnData(False, "重复的规则!")

        rep = r"http(s)?\:\/\/([a-zA-Z0-9][-a-zA-Z0-9]{0,62}\.)+([a-zA-Z0-9][a-zA-Z0-9]{0,62})+.?"
        if not re.match(rep, to):
            return mw.returnData(False, "错误的目标地址")

        # write data json file
        data.append({"r_from": site_from, "type": _type_code, "r_type": _type_code,"r_to": to, 'keep_path': _keep_path, 'id': _id})
        mw.writeFile(redirect_file, json.dumps(data))
        mw.writeFile("{}/{}.conf".format(self.getRedirectPath(siteName), _id), file_content)

        self.operateRedirectConf(siteName, 'start')
        mw.restartWeb()
        return mw.returnData(True, "设置成功")

    def getRedirectConf(self, siteName, rid):
        if rid == '' or siteName == '':
            return mw.returnData(False, "必填项不能为空!")

        path = self.getRedirectPath(siteName)
        conf = "{}/{}.conf".format(path, rid)
        data = mw.readFile(conf)
        if data == False:
            return mw.returnData(False, "获取失败!")
        return mw.returnData(True, "ok", {"result": data})

        # 删除指定重定向
    def delRedirect(self,siteName, rid):
        if rid == '' or siteName == '':
            return mw.returnData(False, "必填项不能为空!")

        try:
            data_path = self.getRedirectDataPath(siteName)
            data_content = mw.readFile(data_path) if os.path.exists(data_path) else ""
            data = json.loads(data_content) if data_content != "" else []
            for item in data:
                if item["id"] == rid:
                    data.remove(item)
                    break
            # write database
            mw.writeFile(data_path, json.dumps(data))
            # data is empty ,should stop
            if len(data) == 0:
                self.operateRedirectConf(siteName, 'stop')
            # remove conf file
            mw.execShell("rm -rf {}/{}.conf".format(self.getRedirectPath(siteName), rid))
        except Exception as e:
            return mw.returnData(False, "删除失败:"+str(e))
        return mw.returnData(True, "删除成功!")

    # 读取 网站 反向代理列表
    def getProxyList(self, site_name):
        data_path = self.getProxyDataPath(site_name)

        if not os.path.exists(data_path):
            mw.execShell("mkdir {}/{}".format(self.proxyPath, site_name))
            return mw.returnData(True, "", {"result": [], "count": 0})

        content = mw.readFile(data_path)
        data = json.loads(content)
        tmp = []
        for proxy in data:
            proxy_dir = "{}/{}".format(self.proxyPath, site_name)
            proxy_dir_file = proxy_dir + '/' + proxy['id'] + '.conf'
            if os.path.exists(proxy_dir_file):
                proxy['status'] = True
            else:
                proxy['status'] = False
            tmp.append(proxy)
        return mw.returnData(True, "ok", {"result": data, "count": len(data)})

    # 操作 反向代理配置
    def operateProxyConf(self, site_name, method='start'):
        vhost_file = self.getHostConf(site_name)
        content = mw.readFile(vhost_file)

        proxy_cnf = '''#PROXY-START
    include %s/*.conf;
    #PROXY-END''' % (self.getProxyPath(site_name))

        proxy_cnf_source = '#PROXY-START'

        if content.find('#PROXY-END') != -1:
            if method == 'stop':
                rep = '#PROXY-START(\n|.){1,500}#PROXY-END'
                content = re.sub(rep, '#PROXY-START', content)
        else:
            if method == 'start':
                content = re.sub(proxy_cnf_source, proxy_cnf, content)

        mw.writeFile(vhost_file, content)

    # 设置 网站 反向代理列表
    def setProxy(self, site_name, site_from, to, host, name, open_proxy, open_cache, cache_time, pid):
        from urllib.parse import urlparse
        if  site_name == "" or site_from == "" or to == "" or host == "" or name == "":
            return mw.returnData(False, "必填项不能为空")

        rep = r"http(s)?\:\/\/([a-zA-Z0-9][-a-zA-Z0-9]{0,62}\.)+([a-zA-Z0-9][a-zA-Z0-9]{0,62})+.?"
        if not re.match(rep, to):
            return mw.returnData(False, "错误的目标地址!")

        # get host from url
        try:
            if host == "$host":
                host_tmp = urlparse(_to)
                host = host_tmp.netloc
        except:
            return mw.returnData(False, "错误的目标地址")

        proxy_site_path = self.getProxyDataPath(site_name)
        data_content = mw.readFile(proxy_site_path) if os.path.exists(proxy_site_path) else ""
        data = json.loads(data_content) if data_content != "" else []

        proxy_action = 'add'
        if pid == "":
            pid = mw.md5("{}".format(name))
        else:
            proxy_action = 'edit'

        if proxy_action == "add":
            for item in data:
                if item["name"] == name:
                    return mw.returnData(False, "名称重复!!")
                if item["from"] == site_from:
                    return mw.returnData(False, "代理目录已存在!!")

        tpl = "#PROXY-START\n\
location ^~ {from} {\n\
    proxy_pass {to};\n\
    proxy_set_header Host {host};\n\
    proxy_ssl_server_name on;\n\
    proxy_set_header X-Real-IP $remote_addr;\n\
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n\
    proxy_set_header REMOTE-HOST $remote_addr;\n\
    proxy_set_header Upgrade $http_upgrade;\n\
    proxy_set_header Connection $connection_upgrade;\n\
    proxy_http_version 1.1;\n\
    \n\
    add_header X-Cache $upstream_cache_status;\n\
    \n\
     {proxy_cache}\n\
}\n\
# PROXY-END"

        tpl_proxy_cache = "\n\
    if ( $uri ~* \\.(gif|png|jpg|css|js|woff|woff2)$\" )\n\
    {\n\
        expires {cache_time}m;\n\
    }\n\
    proxy_ignore_headers Set-Cookie Cache-Control expires;\n\
    proxy_cache mw_cache;\n\
    proxy_cache_key \"$host$uri$is_args$args\";\n\
    proxy_cache_valid 200 304 301 302 {cache_time}m;\n\
"

        tpl_proxy_nocache = "\n\
    set $static_files_app 0; \n\
    if ( $uri ~* \\.(gif|png|jpg|css|js|woff|woff2)$\" )\n\
    {\n\
        set $static_files_app 1;\n\
        expires 12h;\n\
    }\n\
    if ( $static_files_app = 0 )\n\
    {\n\
        add_header Cache-Control no-cache;\n\
    }\n\
"

        # replace
        if site_from[0] != '/':
            site_from = '/' + site_from
        tpl = tpl.replace("{from}", site_from, 999)
        tpl = tpl.replace("{to}", to)
        tpl = tpl.replace("{host}", host, 999)
        tpl = tpl.replace("{cache_time}", cache_time, 999)

        if open_cache == 'on':
            tpl_proxy_cache = tpl_proxy_cache.replace("{cache_time}", cache_time, 999)
            tpl = tpl.replace("{proxy_cache}", tpl_proxy_cache, 999)
        else:
            tpl = tpl.replace("{proxy_cache}", tpl_proxy_nocache, 999)


        conf_proxy = "{}/{}.conf".format(self.getProxyPath(site_name), pid)
        conf_bk = "{}/{}.conf.txt".format(self.getProxyPath(site_name), pid)
        mw.writeFile(conf_proxy, tpl)

        rule_test = mw.checkWebConfig()
        if rule_test != True:
            os.remove(conf_proxy)
            return mw.returnData(False, "OpenResty配置测试不通过, 请重试: {}".format(rule_test))

        if proxy_action == "add":
            # 添加代理
            pid = mw.md5("{}".format(name))
            for item in data:
                if item["name"] == name:
                    return mw.returnData(False, "名称重复!")
                if item["from"] == site_from:
                    return mw.returnData(False, "代理目录已存在!")
            data.append({
                "name": name,
                "from": site_from,
                "to": to,
                "host": host,
                "open_cache": open_cache,
                "open_proxy": open_proxy,
                "cache_time": cache_time,
                "id": pid,
            })
        else:
            # 修改代理
            dindex = -1
            for x in range(len(data)):
                if data[x]["id"] == pid:
                    dindex = x
                    break
            if dindex < 0:
                return mw.returnData(False, "异常请求")
            data[dindex]['from'] = site_from
            data[dindex]['to'] = to
            data[dindex]['host'] = host
            data[dindex]['open_cache'] = open_cache
            data[dindex]['open_proxy'] = open_proxy
            data[dindex]['cache_time'] = cache_time

        if open_proxy != 'on':
            os.rename(conf_proxy, conf_bk)

        mw.writeFile(proxy_site_path, json.dumps(data))
        self.operateProxyConf(site_name, 'start')
        mw.restartWeb()
        return mw.returnData(True, "ok", {"hash": pid})

    def getProxyConf(self, site_name, pid):
        if pid == '' or site_name == '':
            return mw.returnData(False, "必填项不能为空!")

        conf_file = "{}/{}/{}.conf".format(self.proxyPath, site_name, pid)
        if not os.path.exists(conf_file):
            conf_file = "{}/{}/{}.conf.txt".format(self.proxyPath, site_name, pid)

        if not os.path.exists(conf_file):
            return mw.returnData(False, "获取失败!")

        data = mw.readFile(conf_file)
        return mw.returnData(True, "ok", {"result": data})

    def delProxy(self, site_name, pid):
        if pid == '' or site_name == '':
            return mw.returnData(False, "必填项不能为空!")

        try:
            data_path = self.getProxyDataPath(site_name)
            data_content = mw.readFile(data_path) if os.path.exists(data_path) else ""
            data = json.loads(data_content) if data_content != "" else []
            for item in data:
                if item["id"] == pid:
                    data.remove(item)
                    break
            # write database
            mw.writeFile(data_path, json.dumps(data))

            # data is empty,should stop
            if len(data) == 0:
                self.operateProxyConf(site_name, 'stop')
            # remove conf file
            cmd = "rm -rf {}/{}.conf*".format(self.getProxyPath(site_name), pid)
            mw.execShell(cmd)
        except:
            return mw.returnData(False, "删除反代失败!")

        mw.restartWeb()
        return mw.returnData(True, "删除反代成功!")


    def setPhpVersion(self, siteName, version):
        # nginx
        file = self.getHostConf(siteName)
        conf = mw.readFile(file)
        if conf:
            rep = r"enable-php-(.*)\.conf"
            tmp = re.search(rep, conf).group()
            conf = conf.replace(tmp, 'enable-php-' + version + '.conf')
            mw.writeFile(file, conf)

        msg = mw.getInfo('成功切换网站[{1}]的PHP版本为PHP-{2}', (siteName, version))
        mw.writeLog("网站管理", msg)
        mw.restartWeb()
        return mw.returnData(True, msg)


    def setDefaultSite(self, name):
        # 清理旧的
        default_site = thisdb.getOption('default_site', default='')
        if default_site:
            path = self.getHostConf(default_site)
            if os.path.exists(path):
                conf = mw.readFile(path)
                rep = r"listen\s+80.+;"
                conf = re.sub(rep, 'listen 80;', conf, 1)
                rep = r"listen\s+443.+;"
                conf = re.sub(rep, 'listen 443 ssl;', conf, 1)
                mw.writeFile(path, conf)

        path = self.getHostConf(name)
        if os.path.exists(path):
            conf = mw.readFile(path)
            rep = r"listen\s+80\s*;"
            conf = re.sub(rep, 'listen 80 default_server;', conf, 1)
            rep = r"listen\s+443\s*ssl\s*\w*\s*;"
            conf = re.sub(rep, 'listen 443 ssl default_server;', conf, 1)
            mw.writeFile(path, conf)

        thisdb.setOption('default_site', name)
        mw.restartWeb()
        return mw.returnData(True, '设置成功!')

    def setCliPhpVersion(self, version):
        php_bin = '/usr/bin/php'
        php_bin_src = "/www/server/php/%s/bin/php" % version
        php_ize = '/usr/bin/phpize'
        php_ize_src = "/www/server/php/%s/bin/phpize" % version
        php_fpm = '/usr/bin/php-fpm'
        php_fpm_src = "/www/server/php/%s/sbin/php-fpm" % version
        php_pecl = '/usr/bin/pecl'
        php_pecl_src = "/www/server/php/%s/bin/pecl" % version
        php_pear = '/usr/bin/pear'
        php_pear_src = "/www/server/php/%s/bin/pear" % version
        if not os.path.exists(php_bin_src):
            return mw.returnData(False, '指定PHP版本未安装!')

        is_chattr = mw.execShell('lsattr /usr|grep /usr/bin')[0].find('-i-')
        if is_chattr != -1:
            mw.execShell('chattr -i /usr/bin')
        mw.execShell("rm -f " + php_bin + ' ' + php_ize + ' ' + php_fpm + ' ' + php_pecl + ' ' + php_pear)
        mw.execShell("ln -sf %s %s" % (php_bin_src, php_bin))
        mw.execShell("ln -sf %s %s" % (php_ize_src, php_ize))
        mw.execShell("ln -sf %s %s" % (php_fpm_src, php_fpm))
        mw.execShell("ln -sf %s %s" % (php_pecl_src, php_pecl))
        mw.execShell("ln -sf %s %s" % (php_pear_src, php_pear))
        if is_chattr != -1:
            mw.execShell('chattr +i /usr/bin')
        mw.writeLog('面板设置', '设置PHP-CLI版本为: %s' % version)
        return mw.returnData(True, '设置成功!')

    def addSiteTypes(name):
        if not name:
            return mw.returnData(False, "分类名称不能为空")
        if len(name) > 18:
            return mw.returnData(False, "分类名称长度不能超过6个汉字或18位字母")

        all_count = thisdb.getSiteTypesCount()
        if all_count >= 10:
            return mw.returnData(False, '最多添加10个分类!')

        name_count = thisdb.getSiteTypesCountByName(name)
        if name_count > 0:
            return mw.returnData(False, "指定分类名称已存在!")

        thisdb.addSiteTypes(name)
        return mw.returnData(True, '添加成功!')


    def getPhpVersion(self):
        phpVersions = ('00', '52', '53', '54', '55',
                       '56', '70', '71', '72', '73',
                       '74', '80', '81', '82', '83',
                       '84')
        data = []
        for val in phpVersions:
            tmp = {}
            if val == '00':
                tmp['version'] = '00'
                tmp['name'] = '纯静态'
                data.append(tmp)

            # 标准判断
            checkPath = mw.getServerDir() + '/php/' + val + '/bin/php'
            if os.path.exists(checkPath):
                tmp['version'] = val
                tmp['name'] = 'PHP-' + val
                data.append(tmp)

        # 其他PHP安装类型
        conf_dir = mw.getServerDir() + "/web_conf/php/conf"
        conf_list = os.listdir(conf_dir)
        l = len(conf_list)
        rep = r"enable-php-(.*?)\.conf"
        for name in conf_list:
            tmp = {}
            try:
                matchVer = re.search(rep, name).groups()[0]
            except Exception as e:
                continue

            if matchVer in phpVersions:
                continue

            tmp['version'] = matchVer
            tmp['name'] = 'PHP-' + matchVer
            data.append(tmp)
        return data