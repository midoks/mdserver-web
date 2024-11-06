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

    def getDirBindRewrite(self, siteName, dirname):
        return self.rewritePath + '/' + siteName + '_' + dirname + '.conf'

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


    def deleteWSLogs(self, webname):
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
        self.deleteWSLogs(webname)

        if path == '1':
            rootPath = mw.getWwwDir() + '/' + webname
            mw.execShell('rm -rf ' + rootPath)

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
            wlog = tag + ".log"
            wlog_error = tag + ".error.log"

            if os.path.exists(wlog):
                mw.execShell('rm -rf ' + wlog)
            if os.path.exists(wlog_error):
                mw.execShell('rm -rf ' + wlog_error)

        thisdb.deleteBindingBySiteId(site_id)
        mw.restartWeb()
        return mw.returnData(True, '站点【%s】删除成功!' % webname)

    def nginxAddConf(self):
        source_tpl = mw.getRunDir() + '/data/tpl/nginx.conf'
        vhost_file = self.vhostPath + '/' + self.siteName + '.conf'
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

    # 设置网站过期
    def setEndDate(self, site_id, end_date):
        info = thisdb.getSitesById(site_id)
        thisdb.setSitesData(site_id, edate=end_date)
        mw.writeLog('网站', '设置成功,站点【{1}】到期【{2}】后将自动停止!', (info['name'], end_date,))
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
        return mw.getJson(data)

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
        return mw.returnJson(True, '设置成功!')

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