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


    def runHook(self, hook_name, func_name):
        # 站点操作Hook
        hook_cfg = thisdb.getOptionByJson('hook_site_cb',type='hook',default=[])
        hook_num = len(hook_cfg)
        if hook_num == 0:
            return

        from utils.plugin import plugin as MwPlugin
        pa = MwPlugin.instance()

        for x in range(hook_num):
            hook_data = hook_cfg[x]
            if func_name in hook_data:
                app_name = hook_data["name"]
                run_func = hook_data[func_name]['func']
                pa.run(app_name, run_func)
        return True

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

    def getRewriteConf(self, site_name):
        return self.rewritePath + '/' + site_name + '.conf'

    def getRedirectDataPath(self, site_name):
        return "{}/{}/data.json".format(self.redirectPath, site_name)

    def getRedirectPath(self, site_name):
        return "{}/{}".format(self.redirectPath, site_name)

    def getProxyDataPath(self, site_name):
        return "{}/{}/data.json".format(self.proxyPath, site_name)

    def getProxyPath(self, site_name):
        return "{}/{}".format(self.proxyPath, site_name)

    def getDirBindRewrite(self, site_name, dir_name):
        return self.rewritePath + '/' + site_name + '_' + dir_name + '.conf'

    def getIndexConf(self):
        return mw.getServerDir() + '/openresty/nginx/conf/nginx.conf'


    # 路径处理
    def getPath(self, path):
        if path[-1] == '/':
            return path[0:-1]
        return path

    def getSitePath(self, site_name):
        file = self.getHostConf(site_name)
        if os.path.exists(file):
            conf = mw.readFile(file)
            rep = r'\s*root\s*(.+);'
            find_cnf = re.search(rep, conf)
            if not find_cnf:
                return ''
            path = find_cnf.groups()[0]
            return path
        return ''

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

    def add(self, site_info, port, ps, path, version):
        site_root_dir = mw.getWwwDir()
        if site_root_dir == path.rstrip('/'):
            return mw.returnData(False, '不要以网站根目录创建站点!')

        site_info = json.loads(site_info)

        self.siteName = self.toPunycode(site_info['domain'].strip().split(':')[0]).strip()
        self.sitePath = self.toPunycodePath(self.getPath(path.replace(' ', '')))
        self.sitePort = port.strip().replace(' ', '')
        self.phpVersion = version

        if thisdb.isSitesExist(self.siteName):
            return mw.returnData(False, '您添加的站点[%s]已存在!' % self.siteName)

        site_id = thisdb.addSites(self.siteName, self.sitePath)
        if site_id < 1:
            return mw.returnData(False, '添加失败!') 

        self.createRootDir(self.sitePath)
        self.nginxAddConf()

        # 主域名配置
        thisdb.addDomain(site_id, self.siteName, self.sitePort)
        # 添加更多域名
        for domain in site_info['domainlist']:
            self.addDomain(site_id, self.siteName, domain)

        mw.restartWeb()

        self.runHook('site_cb', 'add')
        return mw.returnData(True, '添加成功')

    def stop(self, site_id):
        site_info = thisdb.getSitesById(site_id)

        path = self.setupPath + '/stop'
        if not os.path.exists(path):
            os.makedirs(path)
            default_text = 'The website has been closed!!!'
            mw.writeFile(path + '/index.html', default_text)

        binding = thisdb.getBindingListBySiteId(site_id)
        for b in binding:
            bpath = path + '/' + b['path']
            if not os.path.exists(bpath):
                mw.execShell('mkdir -p ' + bpath)
                mw.execShell('ln -sf ' + path +'/index.html ' + bpath + '/index.html')


        # nginx
        file = self.getHostConf(site_info['name'])
        conf = mw.readFile(file)
        if conf:
            conf = conf.replace(site_info['path'], path)
            mw.writeFile(file, conf)

        thisdb.setSitesData(site_id, status='0')
        msg = mw.getInfo('网站[{1}]已被停用!', (site_info['name'],))
        mw.writeLog('网站管理', msg)
        mw.restartWeb()
        return mw.returnData(True, '站点已停用!')

    def start(self, site_id):
        site_info = thisdb.getSitesById(site_id)

        path = self.setupPath + '/stop'
        # nginx
        file = self.getHostConf(site_info['name'])
        conf = mw.readFile(file)
        if conf:
            conf = conf.replace(path, site_info['path'])
            mw.writeFile(file, conf)

        thisdb.setSitesData(site_id, status='1')
        
        msg = mw.getInfo('网站[{1}]已被启用!', (site_info['name'],))
        mw.writeLog('网站管理', msg)
        mw.restartWeb()
        return mw.returnData(True, '站点已启用!')

    def nginxAddDomain(self, site_name, domain, port):
        file = self.getHostConf(site_name)
        conf = mw.readFile(file)
        if not conf:
            return

        # 添加域名
        rep = r"server_name\s*(.*);"
        tmp = re.search(rep, conf).group()
        domains = tmp.split(' ')
        if not mw.inArray(domains, domain):
            newServerName = tmp.replace(';', ' ' + domain + ';')
            conf = conf.replace(tmp, newServerName)

        # 添加端口
        rep = r"listen\s+([0-9]+)\s*[default_server]*\s*;"
        tmp = re.findall(rep, conf)
        if not mw.inArray(tmp, port):
            listen = re.search(rep, conf).group()
            conf = conf.replace(
                listen, listen + "\n\tlisten " + port + ';')
        # 保存配置文件
        mw.writeFile(file, conf)
        return True

    def addDomain(self, site_id, site_name, domain):
        isError = mw.checkWebConfig()
        if isError != True:
            msg = 'ERROR: 检测到配置文件有错误,请先排除后再操作<br><br><a style="color:red;">' + isError.replace("\n", '<br>') + '</a>'
            return mw.returnData(False, msg)

        domains = domain.split(',')
        for d in domains:
            if d == '':
                continue
            d = d.split(':')
            name = self.toPunycode(d[0])
            port = '80'
            if len(d) == 2:
                port = d[1]

            if not mw.checkPort(port):
                return mw.returnData(False, '端口范围不合法!')

            reg = r"^([\w\-\*]{1,100}\.){1,4}([\w\-]{1,24}|[\w\-]{1,24}\.[\w\-]{1,24})$"
            if not re.match(reg, name):
                return mw.returnData(False, '域名格式不正确!')

            if thisdb.checkSitesDomainIsExist(name, port):
                return mw.returnData(False, '您添加的域名[{}:{}],已使用。请仔细检查!'.format(name, port))

            self.nginxAddDomain(site_name, name, port)

            msg = mw.getInfo('网站[{1}]添加域名[{2}]成功!', (site_name, name))
            mw.writeLog('网站管理', msg)
            thisdb.addDomain(site_id, name, port)

        mw.restartWeb()
        self.runHook('site_cb', 'add')
        return mw.returnData(True, '域名添加成功!')

    def delDomain(self, site_id, site_name, domain, port):
        domain_nums = thisdb.getDomainCountBySiteId(site_id)
        if domain_nums == 1:
            return mw.returnData(False, '最后一个域名不能删除!')

        info = mw.M('domain').field('id,name').where("pid=? AND name=? AND port=?",(site_id, domain, port)).find()

        file = self.getHostConf(site_name)
        conf = mw.readFile(file)
        if conf:
            # 删除域名
            rep = r"server_name\s+(.+);"
            tmp = re.search(rep, conf).group()
            newServerName = tmp.replace(' ' + domain + ';', ';')
            newServerName = newServerName.replace(' ' + domain + ' ', ' ')
            conf = conf.replace(tmp, newServerName)

            # 删除端口
            rep = r"listen\s+([0-9]+);"
            tmp = re.findall(rep, conf)
            port_nums = mw.M('domain').where('pid=? AND port=?', (site_id, port)).count()
            if mw.inArray(tmp, port) == True and port_nums < 2:
                rep = r"\n*\s+listen\s+" + port + ";"
                conf = re.sub(rep, '', conf)
            # 保存配置
            mw.writeFile(file, conf)

        thisdb.deleteDomainId(info['id'])
        msg = mw.getInfo('网站[{1}]删除域名[{2}:{3}]成功!', (site_name, domain, port))
        mw.writeLog('网站管理', msg)
        mw.restartWeb()
        return mw.returnData(True, '站点删除成功!')

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

        self.runHook('site_cb', 'delete')
        return mw.returnData(True, '站点【%s】删除成功!' % webname)

    def nginxAddConf(self):

        source_tpl = self.getNgxTplDir() + '/nginx.conf'
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

    def setSsl(self, site_name, key, csr):
        path = self.sslDir + '/' + site_name
        if not os.path.exists(path):
            mw.execShell('mkdir -p ' + path)

        csrpath = path + "/fullchain.pem"  # 生成证书路径
        keypath = path + "/privkey.pem"    # 密钥文件路径

        if(key.find('KEY') == -1):
            return mw.returnJson(False, '秘钥错误，请检查!')
        if(csr.find('CERTIFICATE') == -1):
            return mw.returnJson(False, '证书错误，请检查!')

        tmp_cert = '/tmp/cert.pl'
        mw.writeFile(tmp_cert, csr)
        if not mw.checkCert(tmp_cert):
            os.remove(tmp_cert)
            return mw.returnData(False, '证书错误,请粘贴正确的PEM格式证书!')
        os.remove(tmp_cert)
        
        mw.backFile(keypath)
        mw.backFile(csrpath)

        mw.writeFile(keypath, key)
        mw.writeFile(csrpath, csr)

        # 写入配置文件
        result = self.setSslConf(site_name)
        if not result['status']:
            return result

        isError = mw.checkWebConfig()
        if(type(isError) == str):
            mw.restoreFile(keypath)
            mw.restoreFile(csrpath)

            msg = 'ERROR: <br><a style="color:red;">' + isError.replace("\n", '<br>') + '</a>'
            return mw.returnData(False, msg)

        mw.writeLog('网站管理', '证书已保存!')
        mw.restartWeb()
        return mw.returnData(True, '证书已保存!')

    # ssl相关方法 start
    def setSslConf(self, site_name):
        file = self.getHostConf(site_name)
        conf = mw.readFile(file)
        if not conf:
            return mw.returnData(False, '站点[%s]配置异常!'.format(site_name))

        version = mw.getOpVer()
        keyPath = self.sslDir + '/' + site_name + '/privkey.pem'
        certPath = self.sslDir + '/' + site_name + '/fullchain.pem'

        if conf.find('ssl_certificate') == -1:
            # ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:HIGH:!aNULL:!MD5:!RC4:!DHE;
            # add_header Alt-Svc 'h3=":443";ma=86400,h3-29=":443";ma=86400';
            http3Header = """
    add_header Strict-Transport-Security "max-age=63072000";
    add_header Alt-Svc 'h3=":443";ma=86400';
"""
            if not version.startswith('1.25') or version.startswith('1.27'):
                http3Header = '';

            sslStr = """#error_page 404/404.html;
    ssl_certificate    %s;
    ssl_certificate_key  %s;
    ssl_protocols TLSv1 TLSv1.1 TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384:DHE-RSA-CHACHA20-POLY1305;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    %s
    error_page 497  https://$host$request_uri;""" % (certPath, keyPath, http3Header)
        if(conf.find('ssl_certificate') != -1):
            return mw.returnData(True, 'SSL开启成功!')

        conf = conf.replace('#error_page 404/404.html;', sslStr)

        rep = r"listen\s+([0-9]+)\s*[default_server|reuseport]*;"
        tmp = re.findall(rep, conf)
        if not mw.inArray(tmp, '443'):
            listen = re.search(rep, conf).group()
            
            if version.startswith('1.25') or version.startswith('1.27'):
                http_ssl = "\n\tlisten 443 ssl;"
                http_ssl = http_ssl + "\n\tlisten [::]:443 ssl;"
                http_ssl = http_ssl + "\n\thttp2 on;"
            else:
                http_ssl = "\n\tlisten 443 ssl;"
                http_ssl = http_ssl + "\n\tlisten [::]:443 ssl;"


            conf = conf.replace(listen, listen + http_ssl)

        mw.backFile(file)
        mw.writeFile(file, conf)
        isError = mw.checkWebConfig()
        if not isError:
            mw.restoreFile(file)
            return mw.returnData(False, '证书错误: <br><a style="color:red;">' + isError.replace("\n", '<br>') + '</a>')
    
        self.saveCert(site_name, keyPath, certPath)
        msg = mw.getInfo('网站[{1}]开启SSL成功!', (site_name,))
        mw.writeLog('网站管理', msg)

        mw.restartWeb()
        return mw.returnData(True, 'SSL开启成功!')

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
    def getDomain(self, site_id):
        data =  thisdb.getDomainBySiteId(site_id)
        return mw.returnData(True, 'ok', data)

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

    def getNgxRewriteDir(self):
        return mw.getPanelDir() + '/web/misc/nginx/rewrite'

    def getNgxTplDir(self):
        return mw.getPanelDir() + '/web/misc/nginx/tpl'

    # 获取模版名内容
    def getRewriteTpl(self, name):
        path = self.getNgxRewriteDir() +'/'+ name + ".conf"
        if not os.path.exists(path):
            return mw.returnData(False, '模版不存在!')
        return mw.returnData(True, 'OK', path)

    def setRewrite(self,path,data,encoding):
        if not os.path.exists(path):
            mw.writeFile(path, '')

        mw.backFile(path)
        mw.writeFile(path, data)
        isError = mw.checkWebConfig()
        if(type(isError) == str):
            mw.restoreFile(path)
            msg = 'ERROR: <br><a style="color:red;">' + isError.replace("\n", '<br>') + '</a>'
            return mw.returnJson(False, msg)
        mw.restartWeb()
        return mw.returnData(True, '设置成功!')

    def setRewriteTpl(self,name,data):
        path = self.getNgxRewriteDir() +'/'+ name + ".conf"
        if os.path.exists(path):
            return mw.returnData(False, '模版已经存在!')

        if data == "":
            return mw.returnData(False, '模版内容不能为空!')
        ok = mw.writeFile(path, data)
        if not ok:
            return mw.returnData(False, '模版保持失败!')

        return mw.returnData(True, '设置模板成功!')

    def getRewriteList(self):
        rewriteList = {}
        rewriteList['rewrite'] = []
        rewriteList['rewrite'].append('0.当前')
        rewrite_nginx_dir = self.getNgxRewriteDir()
        for ds in os.listdir(rewrite_nginx_dir):
            if ds.startswith('.'):
                continue
            if ds.endswith('conf'):
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

        if os.path.exists(site_path):
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

            source_dirbind_tpl = self.getNgxTplDir() + '/nginx_dirbind.conf'
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
        host_conf = self.getHostConf(info['name'])
        content = mw.readFile(host_conf)
        if content:
            content = content.replace(info['path'], path)
            mw.writeFile(host_conf, content)

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
        site_host = self.getHostConf(site_name)
        if os.path.exists(site_host):
            content = mw.readFile(site_host)
            rep = r'\s*root\s*(.+);'
            path = re.search(rep, content).groups()[0]
            content = content.replace(path, new_path)
            mw.writeFile(site_host, content)

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
            domains = thisdb.getDomainBySiteId(site_id)
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

    def httpToHttps(self, site_name):
        file = self.getHostConf(site_name)
        conf = mw.readFile(file)
        if not conf:
            return mw.returnData(False, '站点[{}]配置异常!'.format(site_name))

        if conf.find('ssl_certificate') == -1:
            return mw.returnData(False, '当前未开启SSL')
        to = "#error_page 404/404.html;\n\
    #HTTP_TO_HTTPS_START\n\
    if ($server_port !~ 443){\n\
        rewrite ^(/.*)$ https://$host$1 permanent;\n\
    }\n\
    #HTTP_TO_HTTPS_END"
        conf = conf.replace('#error_page 404/404.html;', to)
        mw.writeFile(file, conf)

        mw.restartWeb()
        return mw.returnData(True, '设置成功!')

    def closeToHttps(self, site_name):
        file = self.getHostConf(site_name)
        conf = mw.readFile(file)
        if not conf:
            return mw.returnData(False, '站点[{}]配置异常!'.format(site_name))
        rep = r"\n\s*#HTTP_TO_HTTPS_START(.|\n){1,300}#HTTP_TO_HTTPS_END"
        conf = re.sub(rep, '', conf)
        rep = r"\s+if.+server_port.+\n.+\n\s+\s*}"
        conf = re.sub(rep, '', conf)
        mw.writeFile(file, conf)

        mw.restartWeb()
        return mw.returnData(True, '关闭HTTPS跳转成功!')

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
        return mw.returnData(True,  '设置成功!')

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
            conf = conf.replace('#error_page 404/404.html;', "#error_page 404/404.html;\n    "+\
                                str_perserver+"\n    "+\
                                str_perip+"\n    "+\
                                str_limit_rate)

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
    def getRedirect(self, site_name):
        redirect_file = self.getRedirectDataPath(site_name)
        if not os.path.exists(redirect_file):
            mw.execShell("mkdir " + self.getRedirectPath(site_name))
            return mw.returnData(True, "no exists!", {"result": [], "count": 0})

        content = mw.readFile(redirect_file)
        data = json.loads(content)

        for i in range(len(data)):
            redirect_dir = self.getRedirectPath(site_name)
            redirect_file = redirect_dir + '/' + data[i]['id'] + '.conf'
            if os.path.exists(redirect_file):
                data[i]['status'] = True
            else:
                data[i]['status'] = False
        return mw.returnData(True, "ok", {"result": data, "count": len(data)})

    def setRedirectStatus(self, site_name, redirect_id, status):
        if status == '' or site_name == '' or redirect_id == '':
            return mw.returnData(False, "必填项不能为空!")

        conf_file = "{}/{}/{}.conf".format(self.redirectPath, site_name, redirect_id)
        conf_txt = "{}/{}/{}.conf.txt".format(self.redirectPath, site_name, redirect_id)

        if status == '1':
            mw.execShell('mv ' + conf_txt + ' ' + conf_file)
        else:
            mw.execShell('mv ' + conf_file + ' ' + conf_txt)

        mw.restartWeb()
        return mw.returnData(True, "OK")

    # 操作 重定向配置
    def operateRedirectConf(self, siteName, method='start'):
        vhost_file = self.getHostConf(siteName)
        content = mw.readFile(vhost_file)

        cnf_301 = '''#301-START
    include %s/*.conf;
    #301-END''' % (self.getRedirectPath(siteName,))

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
    def setRedirect(self, site_name, site_from, to, type, r_type, keep_path):
        if site_name == '' or site_from == '' or to == '' or type == '' or r_type == '':
            return mw.returnData(False, "必填项不能为空!")

        redirect_file = self.getRedirectDataPath(site_name)
        content = mw.readFile(redirect_file) if os.path.exists(redirect_file) else ""
        data = json.loads(content) if content != "" else []

        _r_type = 0 if r_type == "301" else 1
        _type_code = 0 if type == "path" else 1
        _keep_path = 1 if keep_path == "1" else 0

        # check if domain exists in site
        if _type_code == 1:
            domain_list = mw.M('domain').where("name=?", (site_name,)).field('id,pid,name,port,add_time').select()
            site_domain_lists = mw.M('domain').where("pid=?", (domain_list[0]['pid'],)).field('name').select()
            found = False
            for item in site_domain_lists:
                if item['name'] == site_from:
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
                _to = "{}$request_uri".format(to)

            redirect_type = "301" if _type_code == 0 else "302"
            _if = "if ($host ~ '^{}')".format(site_from)
            _return = "return {} {}; ".format(redirect_type, to)
            file_content = _if + "{\r\n    " + _return + "\r\n}"

        _id = mw.md5("{}+{}".format(file_content, site_name))

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
        mw.writeFile("{}/{}.conf".format(self.getRedirectPath(site_name), _id), file_content)

        self.operateRedirectConf(site_name, 'start')
        mw.restartWeb()
        return mw.returnData(True, "设置成功")

    def getRedirectConf(self, site_name, redirect_id):
        if redirect_id == '' or site_name == '':
            return mw.returnData(False, "必填项不能为空!")

        path = self.getRedirectPath(site_name)
        conf = "{}/{}.conf".format(path, redirect_id)
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
    def setProxy(self, site_name, site_from, to, host, name, open_proxy, open_cors, open_cache, cache_time, proxy_id):
        from urllib.parse import urlparse
        if  site_name == "" or site_from == "" or to == "" or host == "" or name == "":
            return mw.returnData(False, "必填项不能为空")

        rep = r"http(s)?\:\/\/([a-zA-Z0-9][-a-zA-Z0-9]{0,62}\.)+([a-zA-Z0-9][a-zA-Z0-9]{0,62})+.?"
        if not re.match(rep, to):
            return mw.returnData(False, "错误的目标地址!")

        # get host from url
        # try:
        #     if host == "$host":
        #         host_tmp = urlparse(to)
        #         host = host_tmp.netloc

        # except Exception as e:
        #     return mw.returnData(False, "错误的目标地址")
        # print(host)

        proxy_site_path = self.getProxyDataPath(site_name)
        data_content = mw.readFile(proxy_site_path) if os.path.exists(proxy_site_path) else ""
        data = json.loads(data_content) if data_content != "" else []

        proxy_action = 'add'
        if proxy_id == "":
            proxy_id = mw.md5("{}".format(name))
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
    add_header X-Cache $upstream_cache_status;\n\
    {cors}\n\
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
    {proxy_cache}\n\
}\n\
# PROXY-END"

        tpl_proxy_cache = "\n\
    if ( $uri ~* \\.(gif|png|jpg|jpeg|css|js|ttf|woff|woff2)$\" )\n\
    {\n\
        expires {cache_time}m;\n\
    }\n\
    proxy_ignore_headers Set-Cookie Cache-Control expires;\n\
    proxy_cache mw_cache;\n\
    proxy_cache_key \"$host$uri$is_args$args\";\n\
    proxy_cache_valid 200 304 301 302 {cache_time}m;\n\
"
        tpl_proxy_nocache_bak = "\n\
    set $static_files_app 0; \n\
    if ( $uri ~* \\.(gif|png|jpg|jpeg|css|js|ttf|woff|woff2)$\" )\n\
    {\n\
        set $static_files_app 1;\n\
        expires 12h;\n\
    }\n\
    if ( $static_files_app = 0 )\n\
    {\n\
        add_header Cache-Control no-cache;\n\
    }\n\
"

        tpl_proxy_nocache = "\n\
    add_header Cache-Control no-cache;\n\
"
        tpl_proxy_cors = "\n\
    add_header Access-Control-Allow-Origin *;\n\
    add_header Access-Control-Allow-Headers *;\n\
    add_header Access-Control-Allow-Methods 'GET, POST, OPTIONS';\n\
    if ($request_method = 'OPTIONS') {\n\
        return 204;\n\
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

        if open_cors == 'on':
            tpl = tpl.replace("{cors}", tpl_proxy_cors, 999)
        else:
            tpl = tpl.replace("{cors}", '', 999)


        conf_proxy = "{}/{}.conf".format(self.getProxyPath(site_name), proxy_id)
        conf_bk = "{}/{}.conf.txt".format(self.getProxyPath(site_name), proxy_id)
        mw.writeFile(conf_proxy, tpl)

        rule_test = mw.checkWebConfig()
        if rule_test != True:
            os.remove(conf_proxy)
            return mw.returnData(False, "OpenResty配置测试不通过, 请重试: {}".format(rule_test))

        if proxy_action == "add":
            # 添加代理
            proxy_id = mw.md5("{}".format(name))
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
                "cache_time": cache_time,
                "open_proxy": open_proxy,
                "open_cors": open_cors,
                "id": proxy_id,
            })
        else:
            # 修改代理
            dindex = -1
            for x in range(len(data)):
                if data[x]["id"] == proxy_id:
                    dindex = x
                    break
            if dindex < 0:
                return mw.returnData(False, "异常请求")
            data[dindex]['from'] = site_from
            data[dindex]['to'] = to
            data[dindex]['host'] = host
            data[dindex]['open_cache'] = open_cache
            data[dindex]['cache_time'] = cache_time
            data[dindex]['open_proxy'] = open_proxy
            data[dindex]['open_cors'] = open_cors

        if open_proxy != 'on':
            os.rename(conf_proxy, conf_bk)

        mw.writeFile(proxy_site_path, json.dumps(data))
        self.operateProxyConf(site_name, 'start')
        mw.restartWeb()
        return mw.returnData(True, "ok", {"hash": proxy_id})

    def setProxyStatus(self, site_name, proxy_id, status):
        if status == '' or site_name == '' or proxy_id == '':
            return mw.returnData(False, "必填项不能为空!")

        conf_file = "{}/{}/{}.conf".format(self.proxyPath, site_name, proxy_id)
        conf_txt = "{}/{}/{}.conf.txt".format(self.proxyPath, site_name, proxy_id)

        if status == '1':
            mw.execShell('mv ' + conf_txt + ' ' + conf_file)
        else:
            mw.execShell('mv ' + conf_file + ' ' + conf_txt)

        mw.restartWeb()
        return mw.returnData(True, "OK")


    def closeProxyAll(self, site_name):
        self.close_proxy = []
        proxy_path = self.getProxyDataPath(site_name)
        if os.path.exists(proxy_path):
            content = mw.readFile(proxy_path)
            data = json.loads(content)
            for proxy in data:
                proxy_dir = "{}/{}".format(self.proxyPath, site_name)
                proxy_conf = proxy_dir + '/' + proxy['id'] + '.conf'
                proxy_txt = "{}/{}/{}.conf.txt".format(self.proxyPath, site_name, proxy['id'])
                if os.path.exists(proxy_conf):
                    self.close_proxy.append(proxy['id'])
                    mw.execShell('mv ' + proxy_conf + ' ' + proxy_txt)
            mw.restartWeb()
        return True

    def openProxyByOpen(self, site_name):
        for proxy_id in self.close_proxy:
            proxy_dir = "{}/{}".format(self.proxyPath, site_name)
            proxy_conf = proxy_dir + '/' + proxy_id + '.conf'
            proxy_txt = "{}/{}/{}.conf.txt".format(self.proxyPath, site_name, proxy_id)
            if os.path.exists(proxy_txt):
                mw.execShell('mv ' + proxy_txt + ' ' + proxy_conf)

        if len(self.close_proxy) > 0:
            mw.restartWeb()
            self.close_proxy = []
        return True

    def closeRedirectAll(self, site_name):
        self.close_redirect = []
        redirect_path = self.getRedirectDataPath(site_name)
        if os.path.exists(redirect_path):
            content = mw.readFile(redirect_path)
            data = json.loads(content)
            for redirect_data in data:
                redirect_dir = "{}/{}".format(self.redirectPath, site_name)
                redirect_conf = redirect_dir + '/' + redirect_data['id'] + '.conf'
                redirect_txt = "{}/{}/{}.conf.txt".format(self.redirectPath, site_name, redirect_data['id'])
                if os.path.exists(redirect_conf):
                    self.close_redirect.append(redirect_data['id'])
                    mw.execShell('mv ' + redirect_conf + ' ' + redirect_txt)
            mw.restartWeb()

    def openRedirectByOpen(self, site_name):
        for redirect_id in self.close_redirect:
            redirect_dir = "{}/{}".format(self.redirectPath, site_name)
            redirect_conf = redirect_dir + '/' + redirect_id + '.conf'
            redirect_txt = "{}/{}/{}.conf.txt".format(self.redirectPath, site_name, redirect_id)
            if os.path.exists(redirect_txt):
                mw.execShell('mv ' + redirect_txt + ' ' + redirect_conf)

        if len(self.close_redirect) > 0:
            mw.restartWeb()
            self.close_redirect = []
        return True

    def saveRedirectConf(self, site_name, redirect_id, config):
        if redirect_id == '' or site_name == '':
            return mw.returnData(False, "必填项不能为空!")

        _old_config = mw.readFile("{}/{}/{}.conf".format(self.redirectPath, site_name, redirect_id))
        if _old_config == False:
            return mw.returnData(False, "非法操作")

        mw.writeFile("{}/{}/{}.conf".format(self.redirectPath, site_name, redirect_id), config)
        rule_test = mw.checkWebConfig()
        if rule_test != True:
            mw.writeFile("{}/{}/{}.conf".format(self.redirectPath,site_name, redirect_id), _old_config)
            return mw.returnData(False, "OpenResty 配置测试不通过, 请重试: {}".format(rule_test))

        self.operateRedirectConf(site_name, 'start')
        mw.restartWeb()
        return mw.returnData(True, "ok")


    def getProxyConf(self, site_name, proxy_id):
        if proxy_id == '' or site_name == '':
            return mw.returnData(False, "必填项不能为空!")

        conf_file = "{}/{}/{}.conf".format(self.proxyPath, site_name, proxy_id)
        if not os.path.exists(conf_file):
            conf_file = "{}/{}/{}.conf.txt".format(self.proxyPath, site_name, proxy_id)

        if not os.path.exists(conf_file):
            return mw.returnData(False, "获取失败!")

        data = mw.readFile(conf_file)
        return mw.returnData(True, "ok", {"result": data})

    def saveProxyConf(self, site_name, proxy_id, config):
        
        if proxy_id == '' or site_name == '':
            return mw.returnData(False, "必填项不能为空!")

        proxy_file = "{}/{}/{}.conf".format(self.proxyPath, site_name, proxy_id)
        mw.backFile(proxy_file)
        mw.writeFile(proxy_file, config)
        rule_test = mw.checkWebConfig()
        if rule_test != True:
            mw.restoreFile(proxy_file)
            mw.removeBackFile(proxy_file)
            return mw.returnData(False, "OpenResty 配置测试不通过, 请重试: {}".format(rule_test))

        mw.removeBackFile(proxy_file)
        self.operateRedirectConf(site_name, 'start')
        mw.restartWeb()
        return mw.returnData(True, "ok")

    def delProxy(self, site_name, proxy_id):
        if proxy_id == '' or site_name == '':
            return mw.returnData(False, "必填项不能为空!")

        try:
            data_path = self.getProxyDataPath(site_name)
            data_content = mw.readFile(data_path) if os.path.exists(data_path) else ""
            data = json.loads(data_content) if data_content != "" else []
            for item in data:
                if item["id"] == proxy_id:
                    data.remove(item)
                    break
            # write database
            mw.writeFile(data_path, json.dumps(data))

            # data is empty,should stop
            if len(data) == 0:
                self.operateProxyConf(site_name, 'stop')
            # remove conf file
            cmd = "rm -rf {}/{}.conf*".format(self.getProxyPath(site_name), proxy_id)
            mw.execShell(cmd)
        except:
            return mw.returnData(False, "删除反代失败!")

        mw.restartWeb()
        return mw.returnData(True, "删除反代成功!")

    # 是否跳转到https
    def isToHttps(self, site_name):
        file = self.getHostConf(site_name)
        conf = mw.readFile(file)
        if conf:
            if conf.find('$server_port !~ 443') != -1:
                return True
        return False

    def getSsl(self, site_name, ssl_type):
        file = self.getHostConf(site_name)
        content = mw.readFile(file)

        key_text = 'ssl_certificate'
        status = True
        stype = 0
        if content.find(key_text) == -1:
            status = False
            stype = -1

        to_https = self.isToHttps(site_name)

        site_info = thisdb.getSitesByName(site_name)
        domains = thisdb.getDomainBySiteId(site_info['id'])

        path = self.sslDir + '/' + site_name
        if ssl_type == 'lets':
            csr_path = self.sslLetsDir + '/' + site_name + '/fullchain.pem' # Let生成证书路径
            key_path = self.sslLetsDir + '/' + site_name + '/privkey.pem'   # Let密钥文件路径
        elif ssl_type == 'acme':
            csr_path = path + '/fullchain.pem' 
            key_path = path + '/privkey.pem'
            # acme_dir = mw.getAcmeDomainDir(site_name)
            # csr_path = acme_dir + '/fullchain.cer'            # ACME生成证书路径
            # key_path = acme_dir + '/' + site_name + '.key'    # ACME密钥文件路径
        else:
            csr_path = path + '/fullchain.pem'                              # 生成证书路径
            key_path = path + '/privkey.pem'                                # 密钥文件路径

        key = ''
        if os.path.exists(key_path):
            key = mw.readFile(key_path)

        csr = ''
        if os.path.exists(csr_path):
            csr = mw.readFile(csr_path)

        cert_data = mw.getCertName(csr_path)
        # print(csr_path,cert_data)
        data = {
            'status': status,
            'domain': domains,
            'key': key,
            'csr': csr,
            'type': stype,
            'httpTohttps': to_https,
            'cert_data': cert_data,
        }
        return mw.returnData(True, 'OK', data)

    def saveCert(self, site_name, keyPath, certPath):
        try:
            certInfo = mw.getCertName(certPath)
            if not certInfo:
                return mw.returnData(False, '证书解析失败!')
            vpath = self.sslDir + '/' + site_name
            if not os.path.exists(vpath):
                os.system('mkdir -p ' + vpath)
            mw.writeFile(vpath + '/privkey.pem', mw.readFile(keyPath))
            mw.writeFile(vpath + '/fullchain.pem', mw.readFile(certPath))
            mw.writeFile(vpath + '/info.json', json.dumps(certInfo))
            return mw.returnData(True, '证书保存成功!')
        except Exception as e:
            return mw.returnData(False, '证书保存失败!')

    def getCertList(self):
        try:
            vpath = self.sslDir
            if not os.path.exists(vpath):
                os.system('mkdir -p ' + vpath)
            data = []
            for d in os.listdir(vpath):

                # keyPath = self.sslDir + siteName + '/privkey.pem'
                # certPath = self.sslDir + siteName + '/fullchain.pem'

                keyPath = vpath + '/' + d + '/privkey.pem'
                certPath = vpath + '/' + d + '/fullchain.pem'
                if os.path.exists(keyPath) and os.path.exists(certPath):
                    self.saveCert(d, keyPath, certPath)

                mpath = vpath + '/' + d + '/info.json'
                if not os.path.exists(mpath):
                    continue

                tmp = mw.readFile(mpath)
                if not tmp:
                    continue
                tmp1 = json.loads(tmp)
                data.append(tmp1)
            return mw.returnData(True, 'OK', data)
        except:
            return mw.returnData(True, 'OK', [])


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

    def getDnsapi(self):
        dnsapi_data = thisdb.getOptionByJson('dnsapi', default={})
        dnsapi_option = [
            {"name":"none", "title":'手动解析', 'key':'', 'help':''},
            {"name":"dns_ali", "title":'Aliyun', 'key':'Ali_Key:Ali_Secret', 'help':'阿里云控制台》用户头像》accesskeys按指引获取AccessKey/SecretKey'},
            {"name":"dns_cf", "title":'cloudflare', 'key':'CF_Key:CF_Email', 'help':'CloudFlare后台获取Global API Key'},
            {"name":"dns_dp", "title":'dnspod/国内', 'key':'DP_Id:DP_Key','help':'DnsPod后台》用户中心》安全设置，开启API Token'},
            {"name":"dns_dpi", "title":'dnspod/国际', 'key':'DPI_Id:DPI_Key','help':'DnsPod后台》用户中心》安全设置，开启API Token'},
            {"name":"dns_tencent", "title":"腾讯云DNS", 'key':'Tencent_SecretId:Tencent_SecretKey', 'help':'腾讯云后台获取通行证'},
            {"name":"dns_gd", "title":'GoDaddy', 'key':'GD_Key:GD_Secret'},
            # {"name":"dns_pdns", "title":'PowerDNS', 'key':'PDNS_Url:PDNS_ServerId:PDNS_Token:PDNS_Ttl'},
            # {"name":"dns_lua", "title":'LuaDNS', 'key':'LUA_Key:LUA_Email'},
            # {"name":"dns_me", "title":'DNSMadeEasy', 'key':'ME_Key:ME_Secret'},
            {"name":"dns_aws", "title":'Amazon Route53', 'key':'AWS_ACCESS_KEY_ID:AWS_SECRET_ACCESS_KEY'},
            # {"name":"dns_ispconfig", "title":'ISPConfig', 'key':'ISPC_User:ISPC_Password:ISPC_Api:ISPC_Api_Insecure'},
            # {"name":"dns_ad", "title":'Alwaysdata', 'key':'AD_API_KEY'},
            {"name":"dns_linode_v4", "title":'Linode', 'key':'LINODE_V4_API_KEY'},
            # {"name":"dns_freedns", "title":'FreeDNS', 'key':'FREEDNS_User:FREEDNS_Password'},
            # {"name":"dns_cyon", "title":'cyon.ch', 'key':'CY_Username:CY_Password:CY_OTP_Secret'},
            # {"name":"dns_gandi_livedns", "title":'LiveDNS', 'key':'GANDI_LIVEDNS_TOKEN'},
            # {"name":"dns_knot", "title":'Knot', 'key':'KNOT_SERVER:KNOT_KEY'},
            {"name":"dns_dgon", "title":'DigitalOcean', 'key':'DO_API_KEY'},
            # {"name":"dns_cloudns", "title":'ClouDNS.net', 'key':'CLOUDNS_SUB_AUTH_ID:CLOUDNS_AUTH_PASSWORD'},
            {"name":"dns_namesilo", "title":'Namesilo', 'key':'Namesilo_Key'},
            {"name":"dns_azure", "title":'Azure', 'key':'AZUREDNS_SUBSCRIPTIONID:AZUREDNS_TENANTID:AZUREDNS_APPID:AZUREDNS_CLIENTSECRET'},
            # {"name":"dns_selectel", "title":'selectel.com', 'key':'SL_Key'},
            # {"name":"dns_zonomi", "title":'zonomi.com', 'key':'ZM_Key'},
            # {"name":"dns_kinghost", "title":'KingHost', 'key':'KINGHOST_Username:KINGHOST_Password'},
            # {"name":"dns_zilore", "title":'Zilore', 'key':'Zilore_Key'},
            {"name":"dns_gcloud", "title":'Google Cloud DNS', 'key':'CLOUDSDK_ACTIVE_CONFIG_NAME'},
            # {"name":"dns_mydnsjp", "title":'MyDNS.JP', 'key':'MYDNSJP_MasterID:MYDNSJP_Password'},
            # {"name":"dns_doapi", "title":'do.de', 'key':'DO_LETOKEN'},
            # {"name":"dns_online", "title":'Online', 'key':'ONLINE_API_KEY'},
            # {"name":"dns_cn", "title":'Core-Networks', 'key':'CN_User:CN_Password'},
            # {"name":"dns_ultra", "title":'UltraDNS', 'key':'ULTRA_USR:ULTRA_PWD'},
            # {"name":"dns_hetzner", "title":'Hetzner', 'key':'HETZNER_Token'},
            # {"name":"dns_ddnss", "title":'DDNSS.de', 'key':'DDNSS_Token'},
        ];

        for i in range(len(dnsapi_option)):
            dval = dnsapi_option[i]['key']
            dname = dnsapi_option[i]['name']
            if dname == 'none':
                continue

            keys = dval.split(':')
            data = {}
            if dname in dnsapi_data:
                dnsapi_option[i]['data'] = dnsapi_data[dname]
                dnsapi_option[i]['title'] = dnsapi_option[i]['title'] + ' - [已配置]'
            else:
                t = {}
                for field in keys:
                    t[field] = ''
                dnsapi_option[i]['data'] = t
        return dnsapi_option

    def setDnsapi(self, type, data):
        dnsapi_data = thisdb.getOptionByJson('dnsapi', default={})
        dnsapi_data[type] = json.loads(data)
        thisdb.setOption('dnsapi',json.dumps(dnsapi_data))
        return mw.returnData(True, '设置成功!')

    def acmeLogFile(self):
        return mw.getPanelDir() + '/logs/acme.log'

    def writeAcmeLog(self,msg):
        log_file = self.acmeLogFile()
        mw.writeFile(log_file, msg+"\n", 'w+')
        return True

    def letLogFile(self):
        return mw.getPanelDir() + '/logs/letsencrypt.log'

    def writeLetLog(self,msg):
        log_file = self.letLogFile()
        mw.writeFile(log_file, msg+"\n", "wb+")
        return True

    def closeSslConf(self, site_name):
        file = self.getHostConf(site_name)
        conf = mw.readFile(file)

        if conf:
            rep = "\n\\s*#HTTP_TO_HTTPS_START(.|\n){1,300}#HTTP_TO_HTTPS_END"
            conf = re.sub(rep, '', conf)
            rep = "\\s+ssl_certificate\\s+.+;\\s+ssl_certificate_key\\s+.+;"
            conf = re.sub(rep, '', conf)
            rep = "\\s+ssl_protocols\\s+.+;\n"
            conf = re.sub(rep, '', conf)
            rep = "\\s+ssl_ciphers\\s+.+;\n"
            conf = re.sub(rep, '', conf)
            rep = "\\s+ssl_prefer_server_ciphers\\s+.+;\n"
            conf = re.sub(rep, '', conf)
            rep = "\\s+ssl_session_cache\\s+.+;\n"
            conf = re.sub(rep, '', conf)
            rep = r"\s+ssl_session_timeout\s+.+;\n"
            conf = re.sub(rep, '', conf)
            rep = r"\s+ssl_ecdh_curve\s+.+;\n"
            conf = re.sub(rep, '', conf)
            rep = r"\s+ssl_session_tickets\s+.+;\n"
            conf = re.sub(rep, '', conf)
            rep = r"\s+ssl_stapling\s+.+;\n"
            conf = re.sub(rep, '', conf)
            rep = r"\s+ssl_stapling_verify\s+.+;\n"
            conf = re.sub(rep, '', conf)
            rep = r"\s+add_header\s+.+;\n"
            conf = re.sub(rep, '', conf)
            rep = r"\s+add_header\s+.+;\n"
            conf = re.sub(rep, '', conf)
            rep = r"\s+ssl\s+on;"
            conf = re.sub(rep, '', conf)
            rep = r"\s+error_page\s497.+;"
            conf = re.sub(rep, '', conf)
            rep = r"\s+if.+server_port.+\n.+\n\s+\s*}"
            conf = re.sub(rep, '', conf)
            rep = r"\s+listen\s+443.*;"
            conf = re.sub(rep, '', conf)
            rep = r"\s+listen\s+\[\:\:\]\:443.*;"
            conf = re.sub(rep, '', conf)
            rep = r"\s+http2\s+on;"
            conf = re.sub(rep, '', conf)
            mw.writeFile(file, conf)

        msg = mw.getInfo('网站[{1}]关闭SSL成功!', (site_name,))
        mw.writeLog('网站管理', msg)
        mw.restartWeb()
        return mw.returnData(True, 'SSL已关闭!')

    def deleteSsl(self,site_name,ssl_type):
        path = self.sslDir + '/' + site_name
        csr_path = path + '/fullchain.pem'

        file = self.getHostConf(site_name)
        content = mw.readFile(file)
        key_text = 'ssl_certificate'
        status = True
        if content.find(key_text) == -1:
            status = False

        if ssl_type == 'now':
            if status:
                return mw.returnData(False, '使用中,先关闭再删除')
            if os.path.exists(path):
                mw.execShell('rm -rf ' + path)
            else:
                return mw.returnData(False, '还未申请!')
        elif ssl_type == 'lets':
            ssl_lets_dir = self.sslLetsDir + '/' + site_name
            csr_lets_path = ssl_lets_dir + '/fullchain.pem'  # 生成证书路径
            if mw.md5(mw.readFile(csr_lets_path)) == mw.md5(mw.readFile(csr_path)):
                return mw.returnData(False, '使用中,先关闭再删除')
            mw.execShell('rm -rf ' + ssl_lets_dir)
        elif ssl_type == 'acme':
            ssl_acme_dir = mw.getAcmeDomainDir(site_name)
            csr_acme_path = ssl_acme_dir + '/fullchain.cer'  # 生成证书路径
            if mw.md5(mw.readFile(csr_acme_path)) == mw.md5(mw.readFile(csr_path)):
                return mw.returnData(False, '使用中,先关闭再删除')
            mw.execShell('rm -rf ' + ssl_acme_dir)

        mw.restartWeb()
        return mw.returnData(True, '删除成功')

    def createAcmeFile(self, site_name, domains, email, force, renew):
        site_conf = self.getHostConf(site_name)
        if not os.path.exists(site_conf):
            return mw.returnData(False, '配置异常!')

        # 关闭反向代理
        self.closeProxyAll(site_name)
        # 关闭重定向
        self.closeRedirectAll(site_name)

        site_info = thisdb.getSitesByName(site_name)
        path = self.getSitePath(site_name)
        if path == '':
            return mw.returnData(False, '【'+site_name+'】配置文件,异常!')

        src_path = site_info['path']
        acme_dir = mw.getAcmeDir()

        if force == 'true':
            force_bool = True

        if renew == 'true':
            cmd = acme_dir + "/acme.sh --renew --yes-I-know-dns-manual-mode-enough-go-ahead-please"
        else:
            cmd = acme_dir + "/acme.sh --issue --force"

        # 确定主域名顺序
        t = []
        if site_name in domains:
            t.append(site_name)
        for dd in domains:
            if dd == site_name:
                continue
            t.append(dd)
        domains = t

        domain_nums = 0
        for d in domains:
            if mw.checkIp(d):
                continue
            if d.find('*.') != -1:
                return mw.returnData(False, '泛域名不能使用【文件验证】的方式申请证书!')
            cmd += ' -w ' + path
            cmd += ' -d ' + d
            domain_nums += 1
        if domain_nums == 0:
            return mw.returnData(False, '请选择域名(不包括IP地址与泛域名)!')

        self.writeAcmeLog('开始ACME申请...')
        log_file = self.acmeLogFile()

        cmd = 'export ACCOUNT_EMAIL=' + email + ' && ' + cmd + ' >> ' + log_file
        result = mw.execShell(cmd)

        # 开启代理
        self.openProxyByOpen(site_name)
        # 开启重定向
        self.openRedirectByOpen(site_name)

        src_path = mw.getAcmeDomainDir(domains[0])
        src_cert = src_path + '/fullchain.cer'
        src_key = src_path + '/' + domains[0] + '.key'
        src_cert.replace("\\*", "*")

        msg = '签发失败,您尝试申请证书的失败次数已达上限!<p>1、检查域名是否绑定到对应站点</p>\
            <p>2、检查域名是否正确解析到本服务器,或解析还未完全生效</p>\
            <p>3、如果您的站点设置了反向代理,或使用了CDN,请先将其关闭</p>\
            <p>4、如果您的站点设置了301重定向,请先将其关闭</p>\
            <p>5、如果以上检查都确认没有问题，请尝试更换DNS服务商</p>'
        if not os.path.exists(src_cert):
            data = {}
            data['err'] = result
            data['out'] = result[0]
            data['msg'] = msg
            data['result'] = {}
            if result[1].find('new-authz error:') != -1:
                data['result'] = json.loads(re.search("{.+}", result[1]).group())
                if data['result']['status'] == 429:
                    data['msg'] = msg
            data['status'] = False
            return data

        dst_path = self.sslDir + '/' + site_name
        dst_cert = dst_path + "/fullchain.pem"  # 生成证书路径
        dst_key = dst_path + "/privkey.pem"  # 密钥文件路径

        if not os.path.exists(dst_path):
            mw.execShell("mkdir -p " + dst_path)

        mw.buildSoftLink(src_cert, dst_cert, True)
        mw.buildSoftLink(src_key, dst_key, True)
        mw.execShell('echo "acme" > "' + dst_path + '/README"')

        # 写入配置文件
        result = self.setSslConf(site_name)
        if not result['status']:
            return result
        result['csr'] = mw.readFile(src_cert)
        result['key'] = mw.readFile(src_key)

        mw.restartWeb()
        return mw.returnData(True, '证书已更新!', result)

    def getDnsapiExportVar(self, data):
        def_var = ''
        for k in data:
            def_var += 'export '+k+'="'+data[k]+'"\n'
        return def_var

    def getDomainRootName(self, domain):
        s = domain.split('.')
        count = len(s)
        last_index = count - 1
        top_domain =  s[last_index-1]+'.'+s[last_index]
        return top_domain

    # 查找手动验证,需要改动域名dns的配置
    # nslookup -q=txt _acme-challenge.xx.com
    def findAcmeHandDnsNotice(self, top_domain):
        log_file = self.acmeLogFile()
        info = mw.readFile(log_file)
        txt_rep = r"TXT value: \'(.*)\'"
        txt_value = re.finditer(txt_rep, info)

        rdata = []
        for text in txt_value:
            t = {}
            t['domain'] = '_acme-challenge.'+top_domain
            t['val'] = text.groups()[0]
            t['type'] = 'TXT'
            t['must'] = True
            rdata.append(t)
        return rdata

    # acme手动申请方式
    # https://github.com/acmesh-official/acme.sh/wiki/dns-manual-mode
    def createAcmeDnsTypeNone(self, site_name, domains, email, dnspai, wildcard_domain, force, renew, dns_alias):
        # print(site_name, domains, email, dnspai, wildcard_domain, force, renew)
        acme_dir = mw.getAcmeDir()
        log_file = self.acmeLogFile()

        for d in domains:
            top_domain = self.getDomainRootName(d)
            cmd = '''
#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin:%s
export PATH
''' % (acme_dir,)
            cmd += "acme.sh --register-account -m " + email + " \n"
            if wildcard_domain == 'true':
                cmd += 'acme.sh --issue -d '+top_domain+' -d "*.'+top_domain+'"'
                d = top_domain
            else:
                cmd += "acme.sh --issue -d " + d + " "
            cmd += " --dns --yes-I-know-dns-manual-mode-enough-go-ahead-please"

            if dns_alias != '':
                cmd += ' --domain-alias '+str(dns_alias)

            if renew == 'true':
                cmd += " --renew"
            cmd +=  ' > ' + log_file
            # print(cmd)
            result = mw.execShell(cmd)
            # print(result)

            # acme源的ssl证书
            src_path = mw.getAcmeDomainDir(d)
            src_cert = src_path + '/fullchain.cer'
            src_key = src_path + '/' + d + '.key'

            if not os.path.exists(src_cert):
                info = self.findAcmeHandDnsNotice(top_domain)
                if len(info) != 0:
                    return mw.returnData(True, '手动解析', info)

            # acme源建立软链接(目标)
            dst_path = self.sslDir + '/' + site_name
            dst_cert = dst_path + "/fullchain.pem"  # 生成证书路径
            dst_key = dst_path + "/privkey.pem"  # 密钥文件路径

            if not os.path.exists(dst_path):
                mw.execShell("mkdir -p " + dst_path)

            mw.buildSoftLink(src_cert, dst_cert, True)
            mw.buildSoftLink(src_key, dst_key, True)
            mw.execShell('echo "acme" > "' + dst_path + '/README"')

            # 写入配置文件
            result = self.setSslConf(site_name)
            if not result['status']:
                return result
            result['csr'] = mw.readFile(src_cert)
            result['key'] = mw.readFile(src_key)

        mw.restartWeb()
        return mw.returnData(True, '证书已更新!', result)

    def createAcmeDns(self, site_name, domains, email, dnspai, wildcard_domain, force, renew, dns_alias):
        dnsapi_option = thisdb.getOptionByJson('dnsapi', default={})
        log_file = self.acmeLogFile()
        cmd = 'echo "..." > '+ log_file
        mw.execShell(cmd)

        # 手动方式申请
        if dnspai == 'none':
            return self.createAcmeDnsTypeNone(site_name, domains, email, dnspai, wildcard_domain, force, renew, dns_alias)

        if not dnspai in dnsapi_option:
            return mw.returnData(False, '['+dnspai+']未设置!')

        dnsapi_data = dnsapi_option[dnspai]
        for k in dnsapi_data:
            if dnsapi_data[k] == '':
                return mw.returnData(False, k+'为空!')

        acme_dir = mw.getAcmeDir()
        
        for d in domains:
            cmd = '''
#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin:%s
export PATH
''' % (acme_dir,)
            cmd += "acme.sh --register-account -m "+email+" \n"
            cmd += self.getDnsapiExportVar(dnsapi_data)
            if wildcard_domain == 'true':
                top_domain = self.getDomainRootName(d)
                cmd += 'acme.sh --issue --dns '+str(dnspai)+' -d '+top_domain+' -d "*.'+top_domain+'"'
                d = top_domain
            else:
                cmd += 'acme.sh --issue --dns '+str(dnspai)+' -d '+d

            if dns_alias != '':
                cmd += ' --domain-alias '+str(dns_alias)
                
            cmd +=  ' > ' + log_file
            # print(cmd)
            result = mw.execShell(cmd)
            # print(result)

            # acme源的ssl证书
            src_path = mw.getAcmeDomainDir(d)
            src_cert = src_path + '/fullchain.cer'
            src_key = src_path + '/' + d + '.key'
            
            msg = '签发失败,您尝试申请证书的失败次数已达上限!\
                <p>1、检查域名是否正确解析到本服务器,或解析还未完全生效</p>\
                <p>2、如果以上检查都确认没有问题，请尝试更换DNS服务商</p>'
            if not os.path.exists(src_cert):
                data = {}
                data['err'] = result
                data['out'] = result[0]
                data['msg'] = msg
                data['result'] = {}
                if result[1].find('new-authz error:') != -1:
                    data['result'] = json.loads(re.search("{.+}", result[1]).group())
                    if data['result']['status'] == 429:
                        data['msg'] = msg
                data['status'] = False
                return data

            # acme源建立软链接(目标)
            dst_path = self.sslDir + '/' + site_name
            dst_cert = dst_path + "/fullchain.pem"  # 生成证书路径
            dst_key = dst_path + "/privkey.pem"  # 密钥文件路径

            if not os.path.exists(dst_path):
                mw.execShell("mkdir -p " + dst_path)

            mw.buildSoftLink(src_cert, dst_cert, True)
            mw.buildSoftLink(src_key, dst_key, True)
            mw.execShell('echo "acme" > "' + dst_path + '/README"')

            # 写入配置文件
            result = self.setSslConf(site_name)
            if not result['status']:
                return result
            result['csr'] = mw.readFile(src_cert)
            result['key'] = mw.readFile(src_key)

        mw.restartWeb()
        return mw.returnData(True, '证书已更新!', result)

    def createAcme(self, site_name, domains, force, renew, apply_type, dnspai, email, wildcard_domain, dns_alias):
        domains = json.loads(domains)
        if len(domains) < 1:
            return mw.returnData(False, '请选择域名')
        if email.strip() != '':
            thisdb.setOption('ssl_email', email)

        if email.strip() == '':
            email = mw.getRandomString(10)+"."+mw.getRandomString(3) + '@gmail.com'

        # 检测acme是否安装
        acme_dir = mw.getAcmeDir()
        if not os.path.exists(acme_dir):
            try:
                mw.execShell("curl -sS curl https://get.acme.sh | sh")
            except:
                pass
        if not os.path.exists(acme_dir):
            return mw.returnData(False, '尝试自动安装ACME失败,请通过以下命令尝试手动安装<p>安装命令: curl https://get.acme.sh | sh</p>')

        # 避免频繁执行
        checkAcmeRun = mw.execShell('ps -ef|grep acme.sh |grep -v grep')
        if checkAcmeRun[0] != '':
            return mw.returnData(False, '正在申请或更新SSL中...')

        if apply_type == 'file':
            return self.createAcmeFile(site_name, domains, email,force,renew)
        elif apply_type == 'dns':
            return self.createAcmeDns(site_name, domains, email, dnspai, wildcard_domain,force, renew, dns_alias)
        return mw.returnData(False, '异常请求')

    def createLet(self, site_name, domains, force, renew, apply_type, dnspai, email, wildcard_domain):
        domains = json.loads(domains)
        if len(domains) < 1:
            return mw.returnData(False, '请选择域名')
        if email.strip() != '':
            thisdb.setOption('ssl_email', email)


        host_conf_file = self.getHostConf(site_name)
        if os.path.exists(host_conf_file):
            siteConf = mw.readFile(host_conf_file)
            if siteConf.find('301-END') != -1:
                return mw.returnJson(False, '检测到您的站点做了301重定向设置，请先关闭重定向!')

            # 检测存在反向代理
            data_path = self.getProxyDataPath(site_name)
            data_content = mw.readFile(data_path)
            if data_content != False:
                try:
                    data = json.loads(data_content)
                except:
                    pass
                for proxy in data:
                    proxy_dir = "{}/{}".format(self.proxyPath, site_name)
                    proxy_dir_file = proxy_dir + '/' + proxy['id'] + '.conf'
                    if os.path.exists(proxy_dir_file):
                        return mw.returnJson(False, '检测到您的站点做了反向代理设置，请先关闭反向代理!')

            # fix binddir domain ssl apply question
            mw.backFile(host_conf_file)
            auth_to = self.getSitePath(site_name)
            rep = r"\s*root\s*(.+);"
            replace_root = "\n\troot " + auth_to + ";"
            siteConf = re.sub(rep, replace_root, siteConf)
            mw.writeFile(host_conf_file, siteConf)
            mw.restartWeb()

        to_args = {
            'domains': domains,
            'auth_type': 'http',
            'auth_to': auth_to,
        }

        src_letpath = mw.getServerDir() + '/web_conf/letsencrypt/' + site_name
        src_csrpath = src_letpath + "/fullchain.pem"  # 生成证书路径
        src_keypath = src_letpath + "/privkey.pem"  # 密钥文件路径

        dst_letpath = self.sslDir + '/' + site_name
        dst_csrpath = dst_letpath + '/fullchain.pem'
        dst_keypath = dst_letpath + '/privkey.pem'

        if not os.path.exists(src_letpath):
            import cert_api
            data = cert_api.cert_api().applyCertApi(to_args)
            mw.restoreFile(host_conf_file)
            if not data['status']:
                msg = data['msg']
                if type(data['msg']) != str:
                    msg = data['msg'][0]
                    emsg = data['msg'][1]['challenges'][0]['error']
                    msg = msg + '<p><span>响应状态:</span>' + str(emsg['status']) + '</p><p><span>错误类型:</span>' + emsg[
                        'type'] + '</p><p><span>错误代码:</span>' + emsg['detail'] + '</p>'
                return mw.returnData(data['status'], msg, data['msg'])

        mw.execShell('mkdir -p ' + dst_letpath)
        mw.buildSoftLink(src_csrpath, dst_csrpath, True)
        mw.buildSoftLink(src_keypath, dst_keypath, True)
        mw.execShell('echo "lets" > "' + dst_letpath + '/README"')

        # 写入配置文件
        result = self.setSslConf(site_name)
        if not result['status']:
            return result

        result['csr'] = mw.readFile(src_csrpath)
        result['key'] = mw.readFile(src_keypath)

        mw.restartWeb()
        return mw.returnData(data['status'], data['msg'], result)

    def setCertToSite(self, site_name, cert_name):
        try:
            path = self.sslDir + '/' + site_name.strip()
            if not os.path.exists(path):
                return mw.returnData(False, '证书不存在!')

            result = self.setSslConf(site_name)
            if not result['status']:
                return result

            mw.restartWeb()
            mw.writeLog('网站管理', '证书已部署!')
            return mw.returnData(True, '证书已部署!')
        except Exception as ex:
            return mw.returnData(False, '设置错误:' + str(ex))

    def removeCert(self, cert_name):
        try:
            path = self.sslDir + '/' + cert_name
            if not os.path.exists(path):
                return mw.returnData(False, '证书已不存在!')
            os.system("rm -rf " + path)
            return mw.returnData(True, '证书已删除!')
        except Exception as ex:
            return mw.returnData(False, '证书删除失败:'+str(ex))

    def getBackup(self,site_id,page=1,size=10):
        site_info = thisdb.getSitesById(site_id)
        info = thisdb.getBackupPage(site_id, page, size)
        
        data = {}
        data['data'] = info['list']
        data['site'] = site_info
        data['page'] = mw.getPage({'count':info['count'],'tojs':'getBackup','p':page, 'row':size})
        return data

    def toBackup(self, site_id):
        site_info = thisdb.getSitesById(site_id)

        filename = site_info['name'] + '_' + time.strftime('%Y%m%d_%H%M%S', time.localtime()) + '.zip'
        backup_path = mw.getBackupDir() + '/site'
        zip_name = backup_path + '/' + filename
        if not (os.path.exists(backup_path)):
            os.makedirs(backup_path)
        exec_log = mw.getPanelDir() + '/logs/panel_exec.log'
        cmd = "cd '" + site_info['path'] + "' && zip '" + zip_name + "' -r ./* > " + exec_log + " 2>&1"
        mw.execShell(cmd)

        fsize = 0
        if os.path.exists(zip_name):
            fsize = os.path.getsize(zip_name)

        thisdb.addBackup(site_id,filename,zip_name,fsize)

        msg = mw.getInfo('备份网站[{1}]成功!', (site_info['name'],))
        mw.writeLog('网站管理', msg)
        return mw.returnData(True, '备份成功!')

    def delBackup(self,backup_id):
        info = thisdb.getBackupById(backup_id)
        if os.path.exists(info['filename']):
            os.remove(info['filename'])
        msg = mw.getInfo('删除网站[{1}]的备份[{2}]成功!', (info['name'], info['filename']))
        mw.writeLog('网站管理', msg)

        thisdb.deleteBackupById(backup_id)
        return mw.returnData(True, '站点删除成功!')


    def getPhpVersion(self):
        phpVersions = ('00', '52', '53', '54', '55', '56',
                       '70', '71', '72', '73', '74', '80',
                       '81', '82', '83', '84', '85')
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
        if not os.path.exists(conf_dir):
            return data
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
        return mw.returnData(True, 'ok', data)
        # return data
