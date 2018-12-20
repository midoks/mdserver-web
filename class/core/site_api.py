# coding: utf-8

import psutil
import time
import os
import sys
import public
import re
import json
import pwd


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
        return public.returnJson(True, public.getNumLines(logPath, 1000))

    def getSitePhpVersion(self, siteName):
        conf = public.readFile(self.getHostConf(siteName))
        rep = "enable-php-([0-9]{2,3})\.conf"
        tmp = re.search(rep, conf).groups()
        data = {}
        data['phpversion'] = tmp[0]
        return public.getJson(data)

    def getIndex(self, sid):
        print sid
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

    def addDomain(self, domain, webname, pid):
        pass

    def getPhpVersion(self):
        phpVersions = ('00', '52', '53', '54', '55',
                       '56', '70', '71', '72', '73', '74')
        data = []
        for val in phpVersions:
            tmp = {}
            if val == '00':
                tmp['name'] = '纯静态'
                data.append(tmp)

            checkPath = public.getServerDir() + '/php/' + val + '/bin/php'
            if os.path.exists(checkPath):
                tmp['version'] = val
                tmp['name'] = 'PHP-' + val
                data.append(tmp)

        return public.getJson(data)

    def createRootDir(self, path):
        if not os.path.exists(path):
            os.makedirs(path)
            if not public.isAppleSystem():
                public.execShell('chown -R www:www ' + path)
            public.execShell('chmod -R 755 ' + path)

    def nginxAddConf(self):
        source_tpl = public.getRunDir() + '/data/tpl/nginx.conf'
        desc_file = self.setupPath + '/openresty/nginx/conf/vhost/' + self.siteName + '.conf'
        content = public.readFile(source_tpl)

        content = content.replace('{$PORT}', self.sitePort)
        content = content.replace('{$SERVER_NAME}', self.siteName)
        content = content.replace('{$ROOT_DIR}', self.sitePath)
        content = content.replace('{$PHPVER}', self.phpVersion)

        or_rewrite = self.setupPath + '/openresty/nginx/conf/rewrite'
        content = content.replace('{$OR_REWRITE}', or_rewrite)

        logsPath = public.getLogsDir()
        content = content.replace('{$LOGPATH}', logsPath)
        public.writeFile(desc_file, content)

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
        return public.getJson(data)

    def delete(self, sid, webname):

        confPath = self.setupPath + '/openresty/nginx/conf/vhost/' + webname + '.conf'
        if os.path.exists(confPath):
            os.remove(confPath)
        public.M('sites').where("id=?", (sid,)).delete()
        return public.returnJson(True, '站点删除成功!')

    def setEndDate(self, sid, edate):
        result = public.M('sites').where(
            'id=?', (sid,)).setField('edate', edate)
        siteName = public.M('sites').where('id=?', (sid,)).getField('name')
        public.writeLog('TYPE_SITE', '设置成功,站点到期后将自动停止!', (siteName, edate))
        return public.returnJson(True, '设置成功,站点到期后将自动停止!')
