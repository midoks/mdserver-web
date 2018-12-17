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
            public.execShell("mkdir -p " + path + " && chmod -R 644 " + path)
        path = self.setupPath + '/openresty/nginx/conf/rewrite'
        if not os.path.exists(path):
            public.execShell("mkdir -p " + path + " && chmod -R 644 " + path)
        path = self.setupPath + '/stop'
        if not os.path.exists(path):
            os.system('mkdir -p ' + path)
            # os.system('wget -O ' + path + '/index.html ' +
            #           public.get_url() + '/stop.html &')

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
            print public.execShell('chown -R www:www ' + path)
            public.execShell('chmod -R 755 ' + path)

    def nginxAddConf(self):
        pass

    def add(self, webname, port, ps, path, version):

        siteMenu = json.loads(webname)
        self.siteName = self.toPunycode(
            siteMenu['domain'].strip().split(':')[0]).strip()
        self.sitePath = self.toPunycodePath(
            self.getPath(path.replace(' ', '')))
        self.sitePort = port.strip().replace(' ', '')

        # 写入数据库
        pid = public.M('sites').add('name,path,status,ps,edate,addtime',
                                    (self.siteName, self.sitePath, '1', ps, '0000-00-00', public.getDate()))

        self.createRootDir(self.sitePath)
        # public.M('domain').add('pid,name,port,addtime',
        #                        (get.pid, self.siteName, self.sitePort, public.getDate()))

        self.nginxAddConf()

        data = {}
        data['siteStatus'] = False
        return public.getJson(data)

    def delete(self, sid):
        public.M('sites').where("id=?", (sid,)).delete()
        return public.returnJson(True, '站点删除成功!')

    def setEndDate(self, sid, edate):
        result = public.M('sites').where(
            'id=?', (sid,)).setField('edate', edate)
        siteName = public.M('sites').where('id=?', (sid,)).getField('name')
        public.writeLog('TYPE_SITE', '设置成功,站点到期后将自动停止!', (siteName, edate))
        return public.returnJson(True, '设置成功,站点到期后将自动停止!')
