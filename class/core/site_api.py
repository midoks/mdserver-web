# coding: utf-8

import time
import os
import sys
import public
import re
import json
import pwd

sys.path.append("/usr/local/lib/python2.7/site-packages")
import psutil

from flask import request


class site_api:
    siteName = None  # 网站名称
    sitePath = None  # 根目录
    sitePort = None  # 端口
    phpVersion = None  # PHP版本
    setupPath = None  # 安装路径
    isWriteLogs = None  # 是否写日志

    def __init__(self):
        self.setupPath = public.getServerDir()
        path = self.setupPath + '/openresty/nginx/conf/vhost'
        if not os.path.exists(path):
            public.execShell("mkdir -p " + path + " && chmod -R 755 " + path)
        path = self.setupPath + '/openresty/nginx/conf/rewrite'
        if not os.path.exists(path):
            public.execShell("mkdir -p " + path + " && chmod -R 755 " + path)

    ##### ----- start ----- ###
    def listApi(self):
        return self.list()

    def getPhpVersionApi(self):
        return self.getPhpVersion()

    def setPhpVersionApi(self):
        siteName = request.form.get('siteName', '').encode('utf-8')
        version = request.form.get('version', '').encode('utf-8')

        # nginx
        file = self.setupPath + '/openresty/nginx/conf/vhost/' + siteName + '.conf'
        conf = public.readFile(file)
        if conf:
            rep = "enable-php-([0-9]{2,3})\.conf"
            tmp = re.search(rep, conf).group()
            conf = conf.replace(tmp, 'enable-php-' + version + '.conf')
            public.writeFile(file, conf)

        public.restartWeb()
        msg = public.getInfo('成功切换网站[{1}]的PHP版本为PHP-{2}', (siteName, version))
        public.writeLog("TYPE_SITE", msg)
        return public.returnJson(True, msg)

    def getDomainApi(self):
        pid = request.form.get('pid', '').encode('utf-8')
        return self.getDomain(pid)

    # 获取站点所有域名
    def getSiteDomainsApi(self):
        pid = request.form.get('id', '').encode('utf-8')

        data = {}
        domains = public.M('domain').where(
            'pid=?', (pid,)).field('name,id').select()
        binding = public.M('binding').where(
            'pid=?', (pid,)).field('domain,id').select()
        if type(binding) == str:
            return binding
        for b in binding:
            tmp = {}
            tmp['name'] = b['domain']
            tmp['id'] = b['id']
            domains.append(tmp)
        data['domains'] = domains
        data['email'] = public.M('users').getField('email')
        if data['email'] == '287962566@qq.com':
            data['email'] = ''
        return public.returnJson(True, 'OK', data)

    def getIndexApi(self):
        sid = request.form.get('id', '').encode('utf-8')
        data = {}
        index = self.getIndex(sid)
        data['index'] = index
        return public.getJson(data)

    def setIndexApi(self):
        sid = request.form.get('id', '').encode('utf-8')
        index = request.form.get('index', '').encode('utf-8')
        return self.setIndex(sid, index)

    def getLimitNetApi(self):
        sid = request.form.get('id', '').encode('utf-8')
        return self.getLimitNet(sid)

    def saveLimitNetApi(self):
        sid = request.form.get('id', '').encode('utf-8')
        perserver = request.form.get('perserver', '').encode('utf-8')
        perip = request.form.get('perip', '').encode('utf-8')
        limit_rate = request.form.get('limit_rate', '').encode('utf-8')
        return self.saveLimitNet(sid, perserver, perip, limit_rate)

    def closeLimitNetApi(self):
        sid = request.form.get('id', '').encode('utf-8')
        return self.closeLimitNet(sid)

    def getSecurityApi(self):
        sid = request.form.get('id', '').encode('utf-8')
        name = request.form.get('name', '').encode('utf-8')
        return self.getSecurity(sid, name)

    def setSecurityApi(self):
        fix = request.form.get('fix', '').encode('utf-8')
        domains = request.form.get('domains', '').encode('utf-8')
        status = request.form.get('status', '').encode('utf-8')
        name = request.form.get('name', '').encode('utf-8')
        sid = request.form.get('id', '').encode('utf-8')
        return self.setSecurity(sid, name, fix, domains, status)

    def getLogsApi(self):
        siteName = request.form.get('siteName', '').encode('utf-8')
        return self.getLogs(siteName)

    def getSitePhpVersionApi(self):
        siteName = request.form.get('siteName', '').encode('utf-8')
        return self.getSitePhpVersion(siteName)

    def getHostConfApi(self):
        siteName = request.form.get('siteName', '').encode('utf-8')
        host = self.getHostConf(siteName)
        return public.getJson({'host': host})

    def getRewriteConfApi(self):
        siteName = request.form.get('siteName', '').encode('utf-8')
        rewrite = self.getRewriteConf(siteName)
        return public.getJson({'rewrite': rewrite})

    def getRewriteTplApi(self):
        tplname = request.form.get('tplname', '').encode('utf-8')
        file = public.getRunDir() + '/rewrite/nginx/' + tplname + '.conf'
        if not os.path.exists(file):
            return public.returnJson(False, '模版不存在!')
        return public.returnJson(True, 'OK', file)

    def getRewriteListApi(self):
        rlist = self.getRewriteList()
        return public.getJson(rlist)

    def getRootDirApi(self):
        data = {}
        data['dir'] = public.getWwwDir()
        return public.getJson(data)

    def setEndDateApi(self):
        sid = request.form.get('id', '').encode('utf-8')
        edate = request.form.get('edate', '').encode('utf-8')
        return self.setEndDate(sid, edate)

    def addApi(self):
        webname = request.form.get('webinfo', '').encode('utf-8')
        ps = request.form.get('ps', '').encode('utf-8')
        path = request.form.get('path', '').encode('utf-8')
        version = request.form.get('version', '').encode('utf-8')
        port = request.form.get('port', '').encode('utf-8')
        return self.add(webname, port, ps, path, version)

    def addDomainApi(self):
        isError = public.checkWebConfig()
        if isError != True:
            return public.returnJson(False, 'ERROR: 检测到配置文件有错误,请先排除后再操作<br><br><a style="color:red;">' + isError.replace("\n", '<br>') + '</a>')

        domain = request.form.get('domain', '').encode('utf-8')
        webname = request.form.get('webname', '').encode('utf-8')
        pid = request.form.get('id', '').encode('utf-8')
        if len(domain) < 3:
            return public.returnJson(False, '域名不能为空!')
        domains = domain.split(',')
        for domain in domains:
            if domain == "":
                continue
            domain = domain.split(':')
            # print domain
            domain_name = self.toPunycode(domain[0])
            domain_port = '80'

            reg = "^([\w\-\*]{1,100}\.){1,4}([\w\-]{1,24}|[\w\-]{1,24}\.[\w\-]{1,24})$"
            if not re.match(reg, domain_name):
                return public.returnJson(False, '域名格式不正确!')

            if len(domain) == 2:
                domain_port = domain[1]
            if domain_port == "":
                domain_port = "80"

            if not public.checkPort(domain_port):
                return public.returnJson(False, '端口范围不合法!')

            opid = public.M('domain').where(
                "name=? AND (port=? OR pid=?)", (domain, domain_port, pid)).getField('pid')
            if opid:
                if public.M('sites').where('id=?', (opid,)).count():
                    return public.returnMsg(False, '指定域名已绑定过!')
                public.M('domain').where('pid=?', (opid,)).delete()

            if public.M('binding').where('domain=?', (domain,)).count():
                return public.returnMsg(False, '您添加的域名已存在!')

            self.nginxAddDomain(webname, domain_name, domain_port)

            # 添加放行端口
            # if port != '80':
            #     import firewalls
            #     get.ps = get.domain
            #     firewalls.firewalls().AddAcceptPort(get)

            public.restartWeb()
            msg = public.getInfo('网站[{1}]添加域名[{2}]成功!', (webname, domain_name))
            public.writeLog('TYPE_SITE', msg)
            public.M('domain').add('pid,name,port,addtime',
                                   (pid, domain_name, domain_port, public.getDate()))

        return public.returnJson(True, '域名添加成功!')

    def delDomainApi(self):
        domain = request.form.get('domain', '').encode('utf-8')
        webname = request.form.get('webname', '').encode('utf-8')
        port = request.form.get('port', '').encode('utf-8')
        pid = request.form.get('id', '')

        find = public.M('domain').where("pid=? AND name=?",
                                        (pid, domain)).field('id,name').find()

        domain_count = public.M('domain').where("pid=?", (pid,)).count()
        if domain_count == 1:
            return public.returnJson(False, '最后一个域名不能删除!')

        file = self.setupPath + '/openresty/nginx/conf/vhost/' + webname + '.conf'
        conf = public.readFile(file)
        if conf:
            # 删除域名
            rep = "server_name\s+(.+);"
            tmp = re.search(rep, conf).group()
            newServerName = tmp.replace(' ' + domain + ';', ';')
            newServerName = newServerName.replace(' ' + domain + ' ', ' ')
            conf = conf.replace(tmp, newServerName)

            # 删除端口
            rep = "listen\s+([0-9]+);"
            tmp = re.findall(rep, conf)
            port_count = public.M('domain').where(
                'pid=? AND port=?', (pid, port)).count()
            if public.inArray(tmp, port) == True and port_count < 2:
                rep = "\n*\s+listen\s+" + port + ";"
                conf = re.sub(rep, '', conf)
            # 保存配置
            public.writeFile(file, conf)

        public.M('domain').where("id=?", (find['id'],)).delete()
        msg = public.getInfo('网站[{1}]删除域名[{2}]成功!', (webname, domain))
        public.writeLog('TYPE_SITE', msg)
        public.restartWeb()
        return public.returnJson(True, '站点删除成功!')

    def deleteApi(self):
        sid = request.form.get('id', '').encode('utf-8')
        webname = request.form.get('webname', '').encode('utf-8')
        path = request.form.get('path', '0').encode('utf-8')
        return self.delete(sid, webname, path)
    ##### ----- end   ----- ###

    # 域名编码转换
    def toPunycode(self, domain):
        import re
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
                newdomain += 'xn--' + \
                    dkey.decode('utf-8').encode('punycode') + '.'
        return newdomain[0:-1]

    # 中文路径处理
    def toPunycodePath(self, path):
        if sys.version_info[0] == 2:
            path = path.encode('utf-8')
        if os.path.exists(path):
            return path
        import re
        match = re.search(u"[\x80-\xff]+", path)
        if not match:
            return path
        npath = ''
        for ph in path.split('/'):
            npath += '/' + self.toPunycode(ph)
        return npath.replace('//', '/')

    # 路径处理
    def getPath(self, path):
        if path[-1] == '/':
            return path[0:-1]
        return path

    def getHostConf(self, siteName):
        return public.getServerDir() + '/openresty/nginx/conf/vhost/' + siteName + '.conf'

    def getRewriteConf(self, siteName):
        return public.getServerDir() + '/openresty/nginx/conf/rewrite/' + siteName + '.conf'

    def getIndexConf(self):
        return public.getServerDir() + '/openresty/nginx/conf/nginx.conf'

    def list(self):
        _list = public.M('sites').where('', ()).field(
            'id,name,path,status,ps,addtime,edate').limit('0,5').order('id desc').select()
        _ret = {}
        _ret['data'] = _list

        count = public.M('sites').where('', ()).count()
        _page = {}
        _page['count'] = count
        _page['tojs'] = 'getWeb'

        _ret['page'] = public.getPage(_page)
        return public.getJson(_ret)

    def getDomain(self, pid):
        _list = public.M('domain').where("pid=?", (pid,)).field(
            'id,pid,name,port,addtime').select()
        return public.getJson(_list)

    def getLogs(self, siteName):
        logPath = public.getLogsDir() + '/' + siteName + '.log'
        if not os.path.exists(logPath):
            return public.returnJson(False, '日志为空')
        return public.returnJson(True, public.getNumLines(logPath, 100))

    def getSitePhpVersion(self, siteName):
        conf = public.readFile(self.getHostConf(siteName))
        rep = "enable-php-([0-9]{2,3})\.conf"
        tmp = re.search(rep, conf).groups()
        data = {}
        data['phpversion'] = tmp[0]
        return public.getJson(data)

    def getIndex(self, sid):
        siteName = public.M('sites').where("id=?", (sid,)).getField('name')
        file = self.getHostConf(siteName)
        conf = public.readFile(file)
        rep = "\s+index\s+(.+);"
        tmp = re.search(rep, conf).groups()
        return tmp[0].replace(' ', ',')

    def setIndex(self, sid, index):
        if index.find('.') == -1:
            return public.returnJson(False,  '默认文档格式不正确，例：index.html')

        index = index.replace(' ', '')
        index = index.replace(',,', ',')

        if len(index) < 3:
            return public.returnJson(False,  '默认文档不能为空!')

        siteName = public.M('sites').where("id=?", (sid,)).getField('name')
        index_l = index.replace(",", " ")
        file = self.getHostConf(siteName)
        conf = public.readFile(file)
        if conf:
            rep = "\s+index\s+.+;"
            conf = re.sub(rep, "\n\tindex " + index_l + ";", conf)
            public.writeFile(file, conf)

        public.writeLog('TYPE_SITE', 'SITE_INDEX_SUCCESS', (siteName, index_l))
        return public.returnJson(True,  '设置成功!')

    def getLimitNet(self, sid):
        siteName = public.M('sites').where("id=?", (sid,)).getField('name')
        filename = self.getHostConf(siteName)
        # 站点总并发
        data = {}
        conf = public.readFile(filename)
        try:
            rep = "\s+limit_conn\s+perserver\s+([0-9]+);"
            tmp = re.search(rep, conf).groups()
            data['perserver'] = int(tmp[0])

            # IP并发限制
            rep = "\s+limit_conn\s+perip\s+([0-9]+);"
            tmp = re.search(rep, conf).groups()
            data['perip'] = int(tmp[0])

            # 请求并发限制
            rep = "\s+limit_rate\s+([0-9]+)\w+;"
            tmp = re.search(rep, conf).groups()
            data['limit_rate'] = int(tmp[0])
        except:
            data['perserver'] = 0
            data['perip'] = 0
            data['limit_rate'] = 0

        return public.getJson(data)

    def checkIndexConf(self):
        limit = self.getIndexConf()
        nginxConf = public.readFile(limit)
        limitConf = "limit_conn_zone $binary_remote_addr zone=perip:10m;\n\t\tlimit_conn_zone $server_name zone=perserver:10m;"
        nginxConf = nginxConf.replace(
            "#limit_conn_zone $binary_remote_addr zone=perip:10m;", limitConf)
        public.writeFile(limit, nginxConf)

    def saveLimitNet(self, sid, perserver, perip, limit_rate):

        str_perserver = 'limit_conn perserver ' + perserver + ';'
        str_perip = 'limit_conn perip ' + perip + ';'
        str_limit_rate = 'limit_rate ' + limit_rate + 'k;'

        siteName = public.M('sites').where("id=?", (sid,)).getField('name')
        filename = self.getHostConf(siteName)

        conf = public.readFile(filename)
        if(conf.find('limit_conn perserver') != -1):
            # 替换总并发
            rep = "limit_conn\s+perserver\s+([0-9]+);"
            conf = re.sub(rep, str_perserver, conf)

            # 替换IP并发限制
            rep = "limit_conn\s+perip\s+([0-9]+);"
            conf = re.sub(rep, str_perip, conf)

            # 替换请求流量限制
            rep = "limit_rate\s+([0-9]+)\w+;"
            conf = re.sub(rep, str_limit_rate, conf)
        else:
            conf = conf.replace('#error_page 404/404.html;', "#error_page 404/404.html;\n    " +
                                str_perserver + "\n    " + str_perip + "\n    " + str_limit_rate)

        public.writeFile(filename, conf)
        public.restartWeb()
        public.writeLog('TYPE_SITE', 'SITE_NETLIMIT_OPEN_SUCCESS', (siteName,))
        return public.returnJson(True, '设置成功!')

    def closeLimitNet(self, sid):
        siteName = public.M('sites').where("id=?", (sid,)).getField('name')
        filename = self.getHostConf(siteName)
        conf = public.readFile(filename)
        # 清理总并发
        rep = "\s+limit_conn\s+perserver\s+([0-9]+);"
        conf = re.sub(rep, '', conf)

        # 清理IP并发限制
        rep = "\s+limit_conn\s+perip\s+([0-9]+);"
        conf = re.sub(rep, '', conf)

        # 清理请求流量限制
        rep = "\s+limit_rate\s+([0-9]+)\w+;"
        conf = re.sub(rep, '', conf)
        public.writeFile(filename, conf)
        public.restartWeb()
        public.writeLog(
            'TYPE_SITE', 'SITE_NETLIMIT_CLOSE_SUCCESS', (siteName,))
        return public.returnJson(True, '已关闭流量限制!')

    def getSecurity(self, sid, name):
        filename = self.getHostConf(name)
        conf = public.readFile(filename)
        data = {}
        if conf.find('SECURITY-START') != -1:
            rep = "#SECURITY-START(\n|.){1,500}#SECURITY-END"
            tmp = re.search(rep, conf).group()
            data['fix'] = re.search(
                "\(.+\)\$", tmp).group().replace('(', '').replace(')$', '').replace('|', ',')
            data['domains'] = ','.join(re.search(
                "valid_referers\s+none\s+blocked\s+(.+);\n", tmp).groups()[0].split())
            data['status'] = True
        else:
            data['fix'] = 'jpg,jpeg,gif,png,js,css'
            domains = public.M('domain').where(
                'pid=?', (sid,)).field('name').select()
            tmp = []
            for domain in domains:
                tmp.append(domain['name'])
            data['domains'] = ','.join(tmp)
            data['status'] = False
        return public.getJson(data)

    def setSecurity(self, sid, name, fix, domains, status):
        if len(fix) < 2:
            return public.returnJson(False, 'URL后缀不能为空!')
        file = self.getHostConf(name)
        if os.path.exists(file):
            conf = public.readFile(file)
            if conf.find('SECURITY-START') != -1:
                rep = "\s{0,4}#SECURITY-START(\n|.){1,500}#SECURITY-END\n?"
                conf = re.sub(rep, '', conf)
                public.writeLog('网站管理', '站点[' + name + ']已关闭防盗链设置!')
            else:
                rconf = '''#SECURITY-START 防盗链配置
    location ~ .*\.(%s)$
    {
        expires      30d;
        access_log /dev/null;
        valid_referers none blocked %s;
        if ($invalid_referer){
           return 404;
        }
    }
    #SECURITY-END
    include enable-php-''' % (fix.strip().replace(',', '|'), domains.strip().replace(',', ' '))
                conf = re.sub("include\s+enable-php-", rconf, conf)
                public.writeLog('网站管理', '站点[' + name + ']已开启防盗链!')
            public.writeFile(file, conf)
        public.restartWeb()
        return public.returnJson(True, '设置成功!')

    def getPhpVersion(self):
        phpVersions = ('00', '52', '53', '54', '55',
                       '56', '70', '71', '72', '73', '74')
        data = []
        for val in phpVersions:
            tmp = {}
            if val == '00':
                tmp['version'] = '00'
                tmp['name'] = '纯静态'
                data.append(tmp)

            checkPath = public.getServerDir() + '/php/' + val + '/bin/php'
            if os.path.exists(checkPath):
                tmp['version'] = val
                tmp['name'] = 'PHP-' + val
                data.append(tmp)

        return public.getJson(data)

    def getRewriteList(self):
        rewriteList = {}
        rewriteList['rewrite'] = []
        rewriteList['rewrite'].append('0.当前')
        for ds in os.listdir('rewrite/nginx'):
            rewriteList['rewrite'].append(ds[0:len(ds) - 5])
        rewriteList['rewrite'] = sorted(rewriteList['rewrite'])
        return rewriteList

    def createRootDir(self, path):
        if not os.path.exists(path):
            os.makedirs(path)
            if not public.isAppleSystem():
                public.execShell('chown -R www:www ' + path)
            public.execShell('chmod -R 755 ' + path)

    def nginxAddDomain(self, webname, domain, port):
        file = self.setupPath + '/openresty/nginx/conf/vhost/' + webname + '.conf'
        conf = public.readFile(file)
        if not conf:
            return

        # 添加域名
        rep = "server_name\s*(.*);"
        tmp = re.search(rep, conf).group()
        domains = tmp.split(' ')
        if not public.inArray(domains, domain):
            newServerName = tmp.replace(';', ' ' + domain + ';')
            conf = conf.replace(tmp, newServerName)

        # 添加端口
        rep = "listen\s+([0-9]+)\s*[default_server]*\s*;"
        tmp = re.findall(rep, conf)
        if not public.inArray(tmp, port):
            listen = re.search(rep, conf).group()
            conf = conf.replace(
                listen, listen + "\n\tlisten " + port + ';')
        # 保存配置文件
        public.writeFile(file, conf)
        return True

    def nginxAddConf(self):
        source_tpl = public.getRunDir() + '/data/tpl/nginx.conf'
        vhost_file = self.setupPath + '/openresty/nginx/conf/vhost/' + self.siteName + '.conf'
        content = public.readFile(source_tpl)

        content = content.replace('{$PORT}', self.sitePort)
        content = content.replace('{$SERVER_NAME}', self.siteName)
        content = content.replace('{$ROOT_DIR}', self.sitePath)
        content = content.replace('{$PHPVER}', self.phpVersion)

        or_rewrite = self.setupPath + '/openresty/nginx/conf/rewrite'
        content = content.replace('{$OR_REWRITE}', or_rewrite)

        logsPath = public.getLogsDir()
        content = content.replace('{$LOGPATH}', logsPath)
        public.writeFile(vhost_file, content)

        rewrite_content = '''
location /{
    if (!-e $request_filename) {
       rewrite  ^(.*)$  /index.php/$1  last;
       break;
    }
}
        '''
        rewrite_file = self.setupPath + \
            '/openresty/nginx/conf/rewrite/' + self.siteName + '.conf'
        public.writeFile(rewrite_file, rewrite_content)

    def add(self, webname, port, ps, path, version):

        siteMenu = json.loads(webname)
        self.siteName = self.toPunycode(
            siteMenu['domain'].strip().split(':')[0]).strip()
        self.sitePath = self.toPunycodePath(
            self.getPath(path.replace(' ', '')))
        self.sitePort = port.strip().replace(' ', '')
        self.phpVersion = version

        siteM = public.M('sites')
        if siteM.where("name=?", (self.siteName,)).count():
            return public.returnJson(False, '您添加的站点已存在!')

        # 写入数据库
        pid = siteM.add('name,path,status,ps,edate,addtime',
                        (self.siteName, self.sitePath, '1', ps, '0000-00-00', public.getDate()))
        opid = public.M('domain').where(
            "name=?", (self.siteName,)).getField('pid')
        if opid:
            if public.M('sites').where('id=?', (opid,)).count():
                return public.returnJson(False, '您添加的域名已存在!')
            public.M('domain').where('pid=?', (opid,)).delete()

        # 添加更多域名
        for domain in siteMenu['domainlist']:
            sdomain = domain
            swebname = self.siteName
            spid = str(get.pid)
            # self.addDomain(domain, webname, pid)

        public.M('domain').add('pid,name,port,addtime',
                               (pid, self.siteName, self.sitePort, public.getDate()))

        self.createRootDir(self.sitePath)

        self.nginxAddConf()

        data = {}
        data['siteStatus'] = False
        public.restartWeb()
        return public.returnJson(True, '添加成功')

    def deleteWSLogs(self, webname):
        assLogPath = public.getLogsDir() + '/' + webname + '.log'
        errLogPath = public.getLogsDir() + '/' + webname + '.error.log'
        confFile = self.setupPath + '/openresty/nginx/conf/vhost/' + webname + '.conf'
        rewriteFile = self.setupPath + '/openresty/nginx/conf/rewrite/' + webname + '.conf'
        logs = [assLogPath, errLogPath, confFile, rewriteFile]
        for i in logs:
            public.deleteFile(i)

    def delete(self, sid, webname, path):

        self.deleteWSLogs(webname)

        if path == '1':
            rootPath = public.getWwwDir() + '/' + webname
            public.execShell('rm -rf ' + rootPath)

        public.M('sites').where("id=?", (sid,)).delete()
        public.restartWeb()
        return public.returnJson(True, '站点删除成功!')

    def setEndDate(self, sid, edate):
        result = public.M('sites').where(
            'id=?', (sid,)).setField('edate', edate)
        siteName = public.M('sites').where('id=?', (sid,)).getField('name')
        public.writeLog('TYPE_SITE', '设置成功,站点到期后将自动停止!', (siteName, edate))
        return public.returnJson(True, '设置成功,站点到期后将自动停止!')
