# coding: utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------
# 站点操作
# ---------------------------------------------------------------------------------

import time
import os
import sys
from urllib.parse import urlparse
import mw
import re
import json
import shutil


from flask import request


class site_api:
    siteName = None  # 网站名称
    sitePath = None  # 根目录
    sitePort = None  # 端口
    phpVersion = None  # PHP版本

    setupPath = None  # 安装路径
    vhostPath = None
    logsPath = None
    passPath = None
    rewritePath = None
    redirectPath = None
    sslDir = None       # ssl目录
    sslLetsDir = None   # lets ssl目录

    def __init__(self):
        # nginx conf
        self.setupPath = mw.getServerDir() + '/web_conf'

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
            mw.execShell("mkdir -p " + redirect +
                         " && chmod -R 755 " + redirect)

        self.proxyPath = proxy = self.setupPath + '/nginx/proxy'
        if not os.path.exists(proxy):
            mw.execShell("mkdir -p " + proxy + " && chmod -R 755 " + proxy)

        self.logsPath = mw.getRootDir() + '/wwwlogs'
        # ssl conf
        self.sslDir = self.setupPath + '/ssl'
        self.sslLetsDir = self.setupPath + '/letsencrypt'
        if not os.path.exists(self.sslLetsDir):
            mw.execShell("mkdir -p " + self.sslLetsDir +
                         " && chmod -R 755 " + self.sslLetsDir)

    def runHook(self, hook_name, func_name):
        # 站点操作Hook
        hook_file = 'data/hook_site_cb.json'
        hook_cfg = []
        if os.path.exists(hook_file):
            t = mw.readFile(hook_file)
            hook_cfg = json.loads(t)

        hook_num = len(hook_cfg)
        if hook_num == 0:
            return

        import plugins_api
        pa = plugins_api.plugins_api()

        for x in range(hook_num):
            hook_data = hook_cfg[x]
            if func_name in hook_data:
                app_name = hook_data["name"]
                run_func = hook_data[func_name]['func']
                # print(app_name, run_func)
                pa.run(app_name, run_func)
        return True

    ##### ----- start ----- ###
    def listApi(self):
        limit = request.form.get('limit', '10')
        p = request.form.get('p', '1')
        type_id = request.form.get('type_id', '0').strip()
        search = request.form.get('search', '').strip()

        start = (int(p) - 1) * (int(limit))

        siteM = siteC = mw.M('sites').field('id,name,path,status,ps,addtime,edate,type_id')

        sql_where = ''
        if search != '':
            sql_where = " name like '%" + search + "%' or ps like '%" + search + "%' "

        if type_id != '' and int(type_id) >= 0 and search != '':
            sql_where = sql_where + " and type_id=" + type_id + ""
        if type_id != '' and int(type_id) >= 0:
            sql_where = " type_id=" + type_id

        if sql_where != '':
            siteM.where(sql_where)

        _list = siteM.limit((str(start)) + ',' +limit).order('id desc').select()
        if _list != None:
            for i in range(len(_list)):
                _list[i]['backup_count'] = mw.M('backup').where("pid=? AND type=?", (_list[i]['id'], 0)).count()

        _ret = {}
        _ret['data'] = _list

        if sql_where != '':
            count = siteC.where(sql_where).count()
        else:
            count = siteC.count()

        _page = {}
        _page['count'] = count
        _page['tojs'] = 'getWeb'
        _page['p'] = p
        _page['row'] = limit

        page_args_tpl = ''
        page_args_tpl += ','+type_id+''
        if search != '':
            page_args_tpl += ',"'+search+'"'
        _page['args_tpl'] = page_args_tpl

        _ret['page'] = mw.getPage(_page)
        return mw.getJson(_ret)

    def setDefaultSiteApi(self):
        name = request.form.get('name', '')
        import time
        # 清理旧的
        default_site = mw.readFile('data/default_site.pl')
        if default_site:
            path = self.getHostConf(default_site)
            if os.path.exists(path):
                conf = mw.readFile(path)
                rep = "listen\s+80.+;"
                conf = re.sub(rep, 'listen 80;', conf, 1)
                rep = "listen\s+443.+;"
                conf = re.sub(rep, 'listen 443 ssl;', conf, 1)
                mw.writeFile(path, conf)

        path = self.getHostConf(name)
        if os.path.exists(path):
            conf = mw.readFile(path)
            rep = "listen\s+80\s*;"
            conf = re.sub(rep, 'listen 80 default_server;', conf, 1)
            rep = "listen\s+443\s*ssl\s*\w*\s*;"
            conf = re.sub(rep, 'listen 443 ssl default_server;', conf, 1)
            mw.writeFile(path, conf)

        mw.writeFile('data/default_site.pl', name)
        mw.restartWeb()
        return mw.returnJson(True, '设置成功!')

    def getDefaultSiteApi(self):
        data = {}
        data['sites'] = mw.M('sites').field(
            'name').order('id desc').select()
        data['default_site'] = mw.readFile('data/default_site.pl')
        return mw.getJson(data)

    def getCliPhpVersionApi(self):
        php_dir = mw.getServerDir() + '/php'
        if not os.path.exists(php_dir):
            return mw.returnJson(False, '未安装PHP,无法设置')

        php_bin = '/usr/bin/php'
        php_versions = self.getPhpVersion()
        php_versions = php_versions[1:]

        if len(php_versions) < 1:
            return mw.returnJson(False, '未安装PHP,无法设置')

        if os.path.exists(php_bin) and os.path.islink(php_bin):
            link_re = os.readlink(php_bin)
            for v in php_versions:
                if link_re.find(v['version']) != -1:
                    return mw.getJson({"select": v, "versions": php_versions})

        return mw.getJson({
            "select": php_versions[0],
            "versions": php_versions})

    def setCliPhpVersionApi(self):
        if mw.isAppleSystem():
            return mw.returnJson(False, "开发机不可设置!")

        version = request.form.get('version', '')

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
            return mw.returnJson(False, '指定PHP版本未安装!')

        is_chattr = mw.execShell('lsattr /usr|grep /usr/bin')[0].find('-i-')
        if is_chattr != -1:
            mw.execShell('chattr -i /usr/bin')
        mw.execShell("rm -f " + php_bin + ' ' + php_ize + ' ' +
                     php_fpm + ' ' + php_pecl + ' ' + php_pear)
        mw.execShell("ln -sf %s %s" % (php_bin_src, php_bin))
        mw.execShell("ln -sf %s %s" % (php_ize_src, php_ize))
        mw.execShell("ln -sf %s %s" % (php_fpm_src, php_fpm))
        mw.execShell("ln -sf %s %s" % (php_pecl_src, php_pecl))
        mw.execShell("ln -sf %s %s" % (php_pear_src, php_pear))
        if is_chattr != -1:
            mw.execShell('chattr +i /usr/bin')
        mw.writeLog('面板设置', '设置PHP-CLI版本为: %s' % version)
        return mw.returnJson(True, '设置成功!')

    def setPsApi(self):
        mid = request.form.get('id', '')
        ps = request.form.get('ps', '')
        if mw.M('sites').where("id=?", (mid,)).setField('ps', ps):
            return mw.returnJson(True, '修改成功!')
        return mw.returnJson(False, '修改失败!')

    def stopApi(self):
        mid = request.form.get('id', '')
        name = request.form.get('name', '')

        return self.stop(mid, name)

    def stop(self, mid, name):
        path = self.setupPath + '/stop'
        if not os.path.exists(path):
            os.makedirs(path)
            default_text = 'The website has been closed!!!'
            mw.writeFile(path + '/index.html', default_text)

        binding = mw.M('binding').where('pid=?', (mid,)).field(
            'id,pid,domain,path,port,addtime').select()
        for b in binding:
            bpath = path + '/' + b['path']
            if not os.path.exists(bpath):
                mw.execShell('mkdir -p ' + bpath)
                mw.execShell('ln -sf ' + path +
                             '/index.html ' + bpath + '/index.html')

        sitePath = mw.M('sites').where("id=?", (mid,)).getField('path')

        # nginx
        file = self.getHostConf(name)
        conf = mw.readFile(file)
        if conf:
            conf = conf.replace(sitePath, path)
            mw.writeFile(file, conf)

        mw.M('sites').where("id=?", (mid,)).setField('status', '0')
        mw.restartWeb()
        msg = mw.getInfo('网站[{1}]已被停用!', (name,))
        mw.writeLog('网站管理', msg)
        return mw.returnJson(True, '站点已停用!')

    def startApi(self):
        mid = request.form.get('id', '')
        name = request.form.get('name', '')
        path = self.setupPath + '/stop'
        sitePath = mw.M('sites').where("id=?", (mid,)).getField('path')

        # nginx
        file = self.getHostConf(name)
        conf = mw.readFile(file)
        if conf:
            conf = conf.replace(path, sitePath)
            mw.writeFile(file, conf)

        mw.M('sites').where("id=?", (mid,)).setField('status', '1')
        mw.restartWeb()
        msg = mw.getInfo('网站[{1}]已被启用!', (name,))
        mw.writeLog('网站管理', msg)
        return mw.returnJson(True, '站点已启用!')

    def getBackupApi(self):
        limit = request.form.get('limit', '')
        p = request.form.get('p', '')
        mid = request.form.get('search', '')

        find = mw.M('sites').where("id=?", (mid,)).field(
            "id,name,path,status,ps,addtime,edate").find()

        start = (int(p) - 1) * (int(limit))
        _list = mw.M('backup').where('pid=?', (mid,)).field('id,type,name,pid,filename,size,addtime').limit(
            (str(start)) + ',' + limit).order('id desc').select()
        _ret = {}
        _ret['data'] = _list

        count = mw.M('backup').where("id=?", (mid,)).count()
        info = {}
        info['count'] = count
        info['tojs'] = 'getBackup'
        info['p'] = p
        info['row'] = limit
        _ret['page'] = mw.getPage(info)
        _ret['site'] = find
        return mw.getJson(_ret)

    def toBackupApi(self):
        mid = request.form.get('id', '')
        find = mw.M('sites').where(
            "id=?", (mid,)).field('name,path,id').find()
        fileName = find['name'] + '_' + \
            time.strftime('%Y%m%d_%H%M%S', time.localtime()) + '.zip'
        backupPath = mw.getBackupDir() + '/site'
        zipName = backupPath + '/' + fileName
        if not (os.path.exists(backupPath)):
            os.makedirs(backupPath)
        tmps = mw.getRunDir() + '/tmp/panelExec.log'
        execStr = "cd '" + find['path'] + "' && zip '" + \
            zipName + "' -r ./* > " + tmps + " 2>&1"
        # print execStr
        mw.execShell(execStr)

        if os.path.exists(zipName):
            fsize = os.path.getsize(zipName)
        else:
            fsize = 0
        sql = mw.M('backup').add('type,name,pid,filename,size,addtime',
                                 (0, fileName, find['id'], zipName, fsize, mw.getDate()))

        msg = mw.getInfo('备份网站[{1}]成功!', (find['name'],))
        mw.writeLog('网站管理', msg)
        return mw.returnJson(True, '备份成功!')

    def delBackupApi(self):
        mid = request.form.get('id', '')
        filename = mw.M('backup').where(
            "id=?", (mid,)).getField('filename')
        if os.path.exists(filename):
            os.remove(filename)
        name = mw.M('backup').where("id=?", (mid,)).getField('name')
        msg = mw.getInfo('删除网站[{1}]的备份[{2}]成功!', (name, filename))
        mw.writeLog('网站管理', msg)
        mw.M('backup').where("id=?", (mid,)).delete()
        return mw.returnJson(True, '站点删除成功!')

    def getPhpVersionApi(self):
        data = self.getPhpVersion()
        return mw.getJson(data)

    def setPhpVersionApi(self):
        siteName = request.form.get('siteName', '')
        version = request.form.get('version', '')

        # nginx
        file = self.getHostConf(siteName)
        conf = mw.readFile(file)
        if conf:
            rep = "enable-php-(.*)\.conf"
            tmp = re.search(rep, conf).group()
            conf = conf.replace(tmp, 'enable-php-' + version + '.conf')
            mw.writeFile(file, conf)

        msg = mw.getInfo('成功切换网站[{1}]的PHP版本为PHP-{2}', (siteName, version))
        mw.writeLog("网站管理", msg)
        mw.restartWeb()
        return mw.returnJson(True, msg)

    def getDomainApi(self):
        pid = request.form.get('pid', '')
        return self.getDomain(pid)

    # 获取站点所有域名
    def getSiteDomainsApi(self):
        pid = request.form.get('id', '')

        data = {}
        domains = mw.M('domain').where(
            'pid=?', (pid,)).field('name,id').select()
        binding = mw.M('binding').where(
            'pid=?', (pid,)).field('domain,id').select()
        if type(binding) == str:
            return binding
        for b in binding:
            tmp = {}
            tmp['name'] = b['domain']
            tmp['id'] = b['id']
            domains.append(tmp)
        data['domains'] = domains
        data['email'] = mw.M('users').getField('email')
        if data['email'] == 'midoks@163.com':
            data['email'] = ''
        return mw.returnJson(True, 'OK', data)

    def getDirBindingApi(self):
        mid = request.form.get('id', '')

        path = mw.M('sites').where('id=?', (mid,)).getField('path')
        if not os.path.exists(path):
            checks = ['/', '/usr', '/etc']
            if path in checks:
                data = {}
                data['dirs'] = []
                data['binding'] = []
                return mw.returnJson(True, 'OK', data)
            os.system('mkdir -p ' + path)
            os.system('chmod 755 ' + path)
            os.system('chown www:www ' + path)
            siteName = mw.M('sites').where(
                'id=?', (get.id,)).getField('name')
            mw.writeLog(
                '网站管理', '站点[' + siteName + '],根目录[' + path + ']不存在,已重新创建!')

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
        data['binding'] = mw.M('binding').where('pid=?', (mid,)).field(
            'id,pid,domain,path,port,addtime').select()
        return mw.returnJson(True, 'OK', data)

    def getDirUserIniApi(self):
        mid = request.form.get('id', '')

        path = mw.M('sites').where('id=?', (mid,)).getField('path')
        name = mw.M('sites').where("id=?", (mid,)).getField('name')
        data = {}
        data['logs'] = self.getLogsStatus(name)
        data['runPath'] = self.getSiteRunPath(mid)

        data['userini'] = False
        if os.path.exists(path + '/.user.ini'):
            data['userini'] = True

        if data['runPath']['runPath'] != '/':
            if os.path.exists(path + data['runPath']['runPath'] + '/.user.ini'):
                data['userini'] = True

        data['pass'] = self.getHasPwd(name)
        data['path'] = path
        data['name'] = name
        return mw.returnJson(True, 'OK', data)

    def setDirUserIniApi(self):
        path = request.form.get('path', '')
        runPath = request.form.get('runPath', '')
        filename = path + '/.user.ini'

        if os.path.exists(filename):
            self.delUserInI(path)
            mw.execShell("which chattr && chattr -i " + filename)
            os.remove(filename)
            return mw.returnJson(True, '已清除防跨站设置!')

        self.setDirUserINI(path, runPath)
        mw.execShell("which chattr && chattr +i " + filename)

        return mw.returnJson(True, '已打开防跨站设置!')

    def setRewriteApi(self):
        data = request.form.get('data', '')
        path = request.form.get('path', '')
        encoding = request.form.get('encoding', '')
        if not os.path.exists(path):
            mw.writeFile(path, '')

        mw.backFile(path)
        mw.writeFile(path, data)
        isError = mw.checkWebConfig()
        if(type(isError) == str):
            mw.restoreFile(path)
            return mw.returnJson(False, 'ERROR: <br><a style="color:red;">' + isError.replace("\n", '<br>') + '</a>')
        mw.restartWeb()
        return mw.returnJson(True, '设置成功!')

    def setRewriteTplApi(self):
        data = request.form.get('data', '')
        name = request.form.get('name', '')
        path = mw.getRunDir() + "/rewrite/nginx/" + name + ".conf"
        if os.path.exists(path):
            return mw.returnJson(False, '模版已经存在!')

        if data == "":
            return mw.returnJson(False, '模版内容不能为空!')
        ok = mw.writeFile(path, data)
        if not ok:
            return mw.returnJson(False, '模版保持失败!')

        return mw.returnJson(True, '设置模板成功!')

    def logsOpenApi(self):
        mid = request.form.get('id', '')
        name = mw.M('sites').where("id=?", (mid,)).getField('name')

        # NGINX
        filename = self.getHostConf(name)
        if os.path.exists(filename):
            conf = mw.readFile(filename)
            rep = self.logsPath + "/" + name + ".log"
            if conf.find(rep) != -1:
                conf = conf.replace(rep + " main", "off")
            else:
                conf = conf.replace('access_log  off',
                                    'access_log  ' + rep + " main")
            mw.writeFile(filename, conf)

        mw.restartWeb()
        return mw.returnJson(True, '操作成功!')

    def getCertListApi(self):
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
                    self.saveCert(keyPath, certPath)

                mpath = vpath + '/' + d + '/info.json'
                if not os.path.exists(mpath):
                    continue

                tmp = mw.readFile(mpath)
                if not tmp:
                    continue
                tmp1 = json.loads(tmp)
                data.append(tmp1)
            return mw.returnJson(True, 'OK', data)
        except:
            return mw.returnJson(True, 'OK', [])

    def deleteSslApi(self):
        site_name = request.form.get('site_name', '')
        ssl_type = request.form.get('ssl_type', '')

        path = self.sslDir + '/' + site_name
        csr_path = path + '/fullchain.pem'  # 生成证书路径

        file = self.getHostConf(site_name)
        content = mw.readFile(file)
        key_text = 'ssl_certificate'
        status = True
        if content.find(key_text) == -1:
            status = False

        if ssl_type == 'now':
            if status:
                return mw.returnJson(False, '使用中,先关闭再删除')
            if os.path.exists(path):
                mw.execShell('rm -rf ' + path)
            else:
                return mw.returnJson(False, '还未申请!')
        elif ssl_type == 'lets':
            ssl_lets_dir = self.sslLetsDir + '/' + site_name
            csr_lets_path = ssl_lets_dir + '/fullchain.pem'  # 生成证书路径
            if mw.md5(mw.readFile(csr_lets_path)) == mw.md5(mw.readFile(csr_path)):
                return mw.returnJson(False, '使用中,先关闭再删除')
            mw.execShell('rm -rf ' + ssl_lets_dir)
        elif ssl_type == 'acme':
            ssl_acme_dir = mw.getAcmeDomainDir(site_name)
            csr_acme_path = ssl_acme_dir + '/fullchain.cer'  # 生成证书路径
            if mw.md5(mw.readFile(csr_acme_path)) == mw.md5(mw.readFile(csr_path)):
                return mw.returnJson(False, '使用中,先关闭再删除')
            mw.execShell('rm -rf ' + ssl_acme_dir)

        # mw.restartWeb()
        return mw.returnJson(True, '删除成功')

    def getSslApi(self):
        site_name = request.form.get('site_name', '')
        ssl_type = request.form.get('ssl_type', '')

        path = self.sslDir + '/' + site_name

        file = self.getHostConf(site_name)
        content = mw.readFile(file)

        key_text = 'ssl_certificate'
        status = True
        stype = 0
        if content.find(key_text) == -1:
            status = False
            stype = -1

        to_https = self.isToHttps(site_name)
        sid = mw.M('sites').where("name=?", (site_name,)).getField('id')
        domains = mw.M('domain').where("pid=?", (sid,)).field('name').select()

        csr_path = path + '/fullchain.pem'  # 生成证书路径
        key_path = path + '/privkey.pem'    # 密钥文件路径

        cert_data = None
        if ssl_type == 'lets':
            csr_path = self.sslLetsDir + '/' + site_name + '/fullchain.pem'  # 生成证书路径
            key_path = self.sslLetsDir + '/' + site_name + '/privkey.pem'    # 密钥文件路径
        elif ssl_type == 'acme':
            acme_dir = mw.getAcmeDomainDir(site_name)
            csr_path = acme_dir + '/fullchain.cer'  # 生成证书路径
            key_path = acme_dir + '/' + site_name + '.key'    # 密钥文件路径

        key = mw.readFile(key_path)
        csr = mw.readFile(csr_path)
        cert_data = mw.getCertName(csr_path)
        data = {
            'status': status,
            'domain': domains,
            'key': key,
            'csr': csr,
            'type': stype,
            'httpTohttps': to_https,
            'cert_data': cert_data,
        }
        return mw.returnJson(True, 'OK', data)

    def setSslApi(self):
        siteName = request.form.get('siteName', '')

        key = request.form.get('key', '')
        csr = request.form.get('csr', '')

        path = self.sslDir + '/' + siteName
        if not os.path.exists(path):
            mw.execShell('mkdir -p ' + path)

        csrpath = path + "/fullchain.pem"  # 生成证书路径
        keypath = path + "/privkey.pem"  # 密钥文件路径

        if(key.find('KEY') == -1):
            return mw.returnJson(False, '秘钥错误，请检查!')
        if(csr.find('CERTIFICATE') == -1):
            return mw.returnJson(False, '证书错误，请检查!')

        mw.writeFile('/tmp/cert.pl', csr)
        if not mw.checkCert('/tmp/cert.pl'):
            return mw.returnJson(False, '证书错误,请粘贴正确的PEM格式证书!')

        mw.backFile(keypath)
        mw.backFile(csrpath)

        mw.writeFile(keypath, key)
        mw.writeFile(csrpath, csr)

        # 写入配置文件
        result = self.setSslConf(siteName)
        if not result['status']:
            return mw.getJson(result)

        isError = mw.checkWebConfig()
        if(type(isError) == str):
            mw.restoreFile(keypath)
            mw.restoreFile(csrpath)
            return mw.returnJson(False, 'ERROR: <br><a style="color:red;">' + isError.replace("\n", '<br>') + '</a>')

        mw.writeLog('网站管理', '证书已保存!')
        mw.restartWeb()
        return mw.returnJson(True, '证书已保存!')

    def setCertToSiteApi(self):
        certName = request.form.get('certName', '')
        siteName = request.form.get('siteName', '')
        try:
            path = self.sslDir + '/' + siteName.strip()
            if not os.path.exists(path):
                return mw.returnJson(False, '证书不存在!')

            result = self.setSslConf(siteName)
            if not result['status']:
                return mw.getJson(result)

            mw.restartWeb()
            mw.writeLog('网站管理', '证书已部署!')
            return mw.returnJson(True, '证书已部署!')
        except Exception as ex:
            return mw.returnJson(False, '设置错误:' + str(ex))

    def removeCertApi(self):
        certName = request.form.get('certName', '')
        try:
            path = self.sslDir + '/' + certName
            if not os.path.exists(path):
                return mw.returnJson(False, '证书已不存在!')
            os.system("rm -rf " + path)
            return mw.returnJson(True, '证书已删除!')
        except:
            return mw.returnJson(False, '删除失败!')

    def closeSslConfApi(self):
        siteName = request.form.get('siteName', '')

        file = self.getHostConf(siteName)
        conf = mw.readFile(file)

        if conf:
            rep = "\n\s*#HTTP_TO_HTTPS_START(.|\n){1,300}#HTTP_TO_HTTPS_END"
            conf = re.sub(rep, '', conf)
            rep = "\s+ssl_certificate\s+.+;\s+ssl_certificate_key\s+.+;"
            conf = re.sub(rep, '', conf)
            rep = "\s+ssl_protocols\s+.+;\n"
            conf = re.sub(rep, '', conf)
            rep = "\s+ssl_ciphers\s+.+;\n"
            conf = re.sub(rep, '', conf)
            rep = "\s+ssl_prefer_server_ciphers\s+.+;\n"
            conf = re.sub(rep, '', conf)
            rep = "\s+ssl_session_cache\s+.+;\n"
            conf = re.sub(rep, '', conf)
            rep = "\s+ssl_session_timeout\s+.+;\n"
            conf = re.sub(rep, '', conf)
            rep = "\s+ssl_ecdh_curve\s+.+;\n"
            conf = re.sub(rep, '', conf)
            rep = "\s+ssl_session_tickets\s+.+;\n"
            conf = re.sub(rep, '', conf)
            rep = "\s+ssl_stapling\s+.+;\n"
            conf = re.sub(rep, '', conf)
            rep = "\s+ssl_stapling_verify\s+.+;\n"
            conf = re.sub(rep, '', conf)
            rep = "\s+add_header\s+.+;\n"
            conf = re.sub(rep, '', conf)
            rep = "\s+add_header\s+.+;\n"
            conf = re.sub(rep, '', conf)
            rep = "\s+ssl\s+on;"
            conf = re.sub(rep, '', conf)
            rep = "\s+error_page\s497.+;"
            conf = re.sub(rep, '', conf)
            rep = "\s+if.+server_port.+\n.+\n\s+\s*}"
            conf = re.sub(rep, '', conf)
            rep = "\s+listen\s+443.*;"
            conf = re.sub(rep, '', conf)
            rep = "\s+listen\s+\[\:\:\]\:443.*;"
            conf = re.sub(rep, '', conf)
            rep = "\s+http2\s+on;"
            conf = re.sub(rep, '', conf)
            mw.writeFile(file, conf)

        msg = mw.getInfo('网站[{1}]关闭SSL成功!', (siteName,))
        mw.writeLog('网站管理', msg)
        mw.restartWeb()
        return mw.returnJson(True, 'SSL已关闭!')

    def deploySslApi(self):
        site_name = request.form.get('site_name', '')
        ssl_type = request.form.get('ssl_type', '')

        path = self.sslDir + '/' + site_name
        csr_path = path + '/fullchain.pem'  # 生成证书路径
        key_path = path + '/privkey.pem'  # 生成证书路径

        if not os.path.exists(path):
            os.makedirs(path)

        if ssl_type == 'lets':
            ssl_lets_dir = self.sslLetsDir + '/' + site_name
            lets_csrpath = ssl_lets_dir + '/fullchain.pem'
            lets_keypath = ssl_lets_dir + '/privkey.pem'
            if mw.md5(mw.readFile(lets_csrpath)) == mw.md5(mw.readFile(csr_path)):
                return mw.returnJson(False, '已部署Lets')
            else:

                mw.buildSoftLink(lets_csrpath, csr_path, True)
                mw.buildSoftLink(lets_keypath, key_path, True)
                mw.execShell('echo "lets" > "' + path + '/README"')
        elif ssl_type == 'acme':
            ssl_acme_dir = mw.getAcmeDir() + '/' + site_name
            if not os.path.exists(ssl_acme_dir):
                ssl_acme_dir = mw.getAcmeDir() + '/' + site_name + '_ecc'

            acme_csrpath = ssl_acme_dir + '/fullchain.cer'
            acme_keypath = ssl_acme_dir + '/' + site_name + '.key'
            if mw.md5(mw.readFile(acme_csrpath)) == mw.md5(mw.readFile(csr_path)):
                return mw.returnJson(False, '已部署ACME')
            else:
                mw.buildSoftLink(acme_csrpath, csr_path, True)
                mw.buildSoftLink(acme_keypath, key_path, True)
                mw.execShell('echo "acme" > "' + path + '/README"')

        result = self.setSslConf(site_name)
        if not result['status']:
            return mw.getJson(result)
        return mw.returnJson(True, '部署成功')

    def getLetsIndex(self, site_name):
        cfg = mw.getRunDir() + '/data/letsencrypt.json'
        if not os.path.exists(cfg):
            return False

        data = mw.readFile(cfg)
        lets_data = json.loads(data)
        order_list = lets_data['orders']

        for x in order_list:
            if order_list[x]['status'] == 'valid':
                for d in order_list[x]['domains']:
                    if d == site_name:
                        return x
        return False

    def renewSslApi(self):
        site_name = request.form.get('site_name', '')
        ssl_type = request.form.get('ssl_type', '')
        if ssl_type == 'lets':
            index = self.getLetsIndex(site_name)
            if index:
                import cert_api
                data = cert_api.cert_api().renewCert(index)
                return data
            else:
                return mw.returnJson(False, '无效操作')

        return mw.returnJson(True, '续期成功')

    def getLetLogsApi(self):
        log_file = mw.getRunDir() + '/logs/letsencrypt.log'
        if not os.path.exists(log_file):
            mw.execShell('touch ' + log_file)
        return mw.returnJson(True, 'OK', log_file)

    def createLetApi(self):
        siteName = request.form.get('siteName', '')
        domains = request.form.get('domains', '')
        force = request.form.get('force', '')
        renew = request.form.get('renew', '')
        email_args = request.form.get('email', '')

        domains = json.loads(domains)
        email = mw.M('users').getField('email')
        if email_args.strip() != '':
            mw.M('users').setField('email', email_args)
            email = email_args

        if not len(domains):
            return mw.returnJson(False, '请选择域名')

        host_conf_file = self.getHostConf(siteName)
        if os.path.exists(host_conf_file):
            siteConf = mw.readFile(host_conf_file)
            if siteConf.find('301-END') != -1:
                return mw.returnJson(False, '检测到您的站点做了301重定向设置，请先关闭重定向!')

            # 检测存在反向代理
            data_path = self.getProxyDataPath(siteName)
            data_content = mw.readFile(data_path)
            if data_content != False:
                try:
                    data = json.loads(data_content)
                except:
                    pass
                for proxy in data:
                    proxy_dir = "{}/{}".format(self.proxyPath, siteName)
                    proxy_dir_file = proxy_dir + '/' + proxy['id'] + '.conf'
                    if os.path.exists(proxy_dir_file):
                        return mw.returnJson(False, '检测到您的站点做了反向代理设置，请先关闭反向代理!')

            # fix binddir domain ssl apply question
            mw.backFile(host_conf_file)
            auth_to = self.getSitePath(siteName)
            rep = "\s*root\s*(.+);"
            replace_root = "\n\troot " + auth_to + ";"
            siteConf = re.sub(rep, replace_root, siteConf)
            mw.writeFile(host_conf_file, siteConf)
            mw.restartWeb()

        to_args = {
            'domains': domains,
            'auth_type': 'http',
            'auth_to': auth_to,
        }

        src_letpath = mw.getServerDir() + '/web_conf/letsencrypt/' + siteName
        src_csrpath = src_letpath + "/fullchain.pem"  # 生成证书路径
        src_keypath = src_letpath + "/privkey.pem"  # 密钥文件路径

        dst_letpath = self.sslDir + '/' + siteName
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
                return mw.returnJson(data['status'], msg, data['msg'])

        mw.execShell('mkdir -p ' + dst_letpath)
        mw.buildSoftLink(src_csrpath, dst_csrpath, True)
        mw.buildSoftLink(src_keypath, dst_keypath, True)
        mw.execShell('echo "lets" > "' + dst_letpath + '/README"')

        # 写入配置文件
        result = self.setSslConf(siteName)
        if not result['status']:
            return mw.getJson(result)

        result['csr'] = mw.readFile(src_csrpath)
        result['key'] = mw.readFile(src_keypath)

        mw.restartWeb()
        return mw.returnJson(data['status'], data['msg'], result)

    def getAcmeLogsApi(self):
        log_file = mw.getRunDir() + '/logs/acme.log'
        if not os.path.exists(log_file):
            mw.execShell('touch ' + log_file)
        return mw.returnJson(True, 'OK', log_file)

    def createAcmeApi(self):
        siteName = request.form.get('siteName', '')
        domains = request.form.get('domains', '')
        force = request.form.get('force', '')
        renew = request.form.get('renew', '')
        email_args = request.form.get('email', '')

        domains = json.loads(domains)
        email = mw.M('users').getField('email')
        if email_args.strip() != '':
            mw.M('users').setField('email', email_args)
            email = email_args

        if not len(domains):
            return mw.returnJson(False, '请选择域名')

        file = self.getHostConf(siteName)
        if os.path.exists(file):
            siteConf = mw.readFile(file)
            if siteConf.find('301-END') != -1:
                return mw.returnJson(False, '检测到您的站点做了301重定向设置，请先关闭重定向!')

            # 检测存在反向代理
            data_path = self.getProxyDataPath(siteName)
            data_content = mw.readFile(data_path)
            if data_content != False:
                try:
                    data = json.loads(data_content)
                except:
                    pass
                for proxy in data:
                    proxy_dir = "{}/{}".format(self.proxyPath, siteName)
                    proxy_dir_file = proxy_dir + '/' + proxy['id'] + '.conf'
                    if os.path.exists(proxy_dir_file):
                        return mw.returnJson(False, '检测到您的站点做了反向代理设置，请先关闭反向代理!')

        siteInfo = mw.M('sites').where(
            'name=?', (siteName,)).field('id,name,path').find()
        path = self.getSitePath(siteName)
        if path == '':
            return mw.returnJson(False, '【'+siteName+'】配置文件,异常!')

        srcPath = siteInfo['path']

        # 检测acme是否安装
        acme_dir = mw.getAcmeDir()
        if not os.path.exists(acme_dir):
            try:
                mw.execShell("curl -sS curl https://get.acme.sh | sh")
            except:
                pass
        if not os.path.exists(acme_dir):
            return mw.returnJson(False, '尝试自动安装ACME失败,请通过以下命令尝试手动安装<p>安装命令: curl https://get.acme.sh | sh</p>')

        # 避免频繁执行
        checkAcmeRun = mw.execShell('ps -ef|grep acme.sh |grep -v grep')
        if checkAcmeRun[0] != '':
            return mw.returnJson(False, '正在申请或更新SSL中...')

        if force == 'true':
            force_bool = True

        if renew == 'true':
            execStr = acme_dir + "/acme.sh --renew --yes-I-know-dns-manual-mode-enough-go-ahead-please"
        else:
            execStr = acme_dir + "/acme.sh --issue --force"

        # 确定主域名顺序
        domainsTmp = []
        if siteName in domains:
            domainsTmp.append(siteName)
        for domainTmp in domains:
            if domainTmp == siteName:
                continue
            domainsTmp.append(domainTmp)
        domains = domainsTmp

        domainCount = 0
        for domain in domains:
            if mw.checkIp(domain):
                continue
            if domain.find('*.') != -1:
                return mw.returnJson(False, '泛域名不能使用【文件验证】的方式申请证书!')
            execStr += ' -w ' + path
            execStr += ' -d ' + domain
            domainCount += 1
        if domainCount == 0:
            return mw.returnJson(False, '请选择域名(不包括IP地址与泛域名)!')

        log_file = mw.getRunDir() + '/logs/acme.log'
        mw.writeFile(log_file, "开始ACME申请...\n", "wb+")
        cmd = 'export ACCOUNT_EMAIL=' + email + ' && ' + \
            execStr + ' >> ' + log_file
        # print(domains)
        # print(cmd)
        result = mw.execShell(cmd)

        src_path = mw.getAcmeDomainDir(domains[0])
        src_cert = src_path + '/fullchain.cer'
        src_key = src_path + '/' + domains[0] + '.key'
        src_cert.replace("\*", "*")

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
                data['result'] = json.loads(
                    re.search("{.+}", result[1]).group())
                if data['result']['status'] == 429:
                    data['msg'] = msg
            data['status'] = False
            return mw.getJson(data)

        dst_path = self.sslDir + '/' + siteName
        dst_cert = dst_path + "/fullchain.pem"  # 生成证书路径
        dst_key = dst_path + "/privkey.pem"  # 密钥文件路径

        if not os.path.exists(dst_path):
            mw.execShell("mkdir -p " + dst_path)

        mw.buildSoftLink(src_cert, dst_cert, True)
        mw.buildSoftLink(src_key, dst_key, True)
        mw.execShell('echo "acme" > "' + dst_path + '/README"')

        # 写入配置文件
        result = self.setSslConf(siteName)
        if not result['status']:
            return mw.getJson(result)
        result['csr'] = mw.readFile(src_cert)
        result['key'] = mw.readFile(src_key)

        mw.restartWeb()
        return mw.returnJson(True, '证书已更新!', result)

    def httpToHttpsApi(self):
        siteName = request.form.get('siteName', '')
        return self.httpToHttps(siteName)

    def httpToHttps(self, site_name):
        file = self.getHostConf(site_name)
        conf = mw.readFile(file)
        if conf:
            if conf.find('ssl_certificate') == -1:
                return mw.returnJson(False, '当前未开启SSL')
            to = "#error_page 404/404.html;\n\
    #HTTP_TO_HTTPS_START\n\
    if ($server_port !~ 443){\n\
        rewrite ^(/.*)$ https://$host$1 permanent;\n\
    }\n\
    #HTTP_TO_HTTPS_END"
            conf = conf.replace('#error_page 404/404.html;', to)
            mw.writeFile(file, conf)

        mw.restartWeb()
        return mw.returnJson(True, '设置成功!')

    def closeToHttpsApi(self):
        siteName = request.form.get('siteName', '')
        return self.closeToHttps(siteName)

    def closeToHttps(self, site_name):
        file = self.getHostConf(site_name)
        conf = mw.readFile(file)
        if conf:
            rep = "\n\s*#HTTP_TO_HTTPS_START(.|\n){1,300}#HTTP_TO_HTTPS_END"
            conf = re.sub(rep, '', conf)
            rep = "\s+if.+server_port.+\n.+\n\s+\s*}"
            conf = re.sub(rep, '', conf)
            mw.writeFile(file, conf)

        mw.restartWeb()
        return mw.returnJson(True, '关闭HTTPS跳转成功!')

    def getIndexApi(self):
        sid = request.form.get('id', '')
        data = {}
        index = self.getIndex(sid)
        data['index'] = index
        return mw.getJson(data)

    def setIndexApi(self):
        sid = request.form.get('id', '')
        index = request.form.get('index', '')
        return self.setIndex(sid, index)

    def getLimitNetApi(self):
        sid = request.form.get('id', '')
        return self.getLimitNet(sid)

    def saveLimitNetApi(self):
        sid = request.form.get('id', '')
        perserver = request.form.get('perserver', '')
        perip = request.form.get('perip', '')
        limit_rate = request.form.get('limit_rate', '')
        return self.saveLimitNet(sid, perserver, perip, limit_rate)

    def closeLimitNetApi(self):
        sid = request.form.get('id', '')
        return self.closeLimitNet(sid)

    def getSecurityApi(self):
        sid = request.form.get('id', '')
        name = request.form.get('name', '')
        return self.getSecurity(sid, name)

    def setSecurityApi(self):
        fix = request.form.get('fix', '')
        domains = request.form.get('domains', '')
        status = request.form.get('status', '')
        name = request.form.get('name', '')
        none = request.form.get('none', '')
        sid = request.form.get('id', '')
        return self.setSecurity(sid, name, fix, domains, status, none)

    def getLogsApi(self):
        siteName = request.form.get('siteName', '')
        return self.getLogs(siteName)

    def getErrorLogsApi(self):
        siteName = request.form.get('siteName', '')
        return self.getErrorLogs(siteName)

    def getSitePhpVersionApi(self):
        siteName = request.form.get('siteName', '')
        return self.getSitePhpVersion(siteName)

    def getHostConfApi(self):
        siteName = request.form.get('siteName', '')
        host = self.getHostConf(siteName)
        return mw.getJson({'host': host})

    def saveHostConfApi(self):
        path = request.form.get('path', '')
        data = request.form.get('data', '')
        encoding = request.form.get('encoding', '')

        import files_api

        mw.backFile(path)
        save_ret_data = files_api.files_api().saveBody(path, data, encoding)
        rdata = json.loads(save_ret_data)

        if rdata['status']:
            isError = mw.checkWebConfig()
            if isError != True:
                mw.restoreFile(path)
                return mw.returnJson(False, 'ERROR: 检测到配置文件有错误,请先排除后再操作<br><br><a style="color:red;">' + isError.replace("\n", '<br>') + '</a>')
            mw.restartWeb()
            mw.removeBackFile(path)
        return save_ret_data

    def getRewriteConfApi(self):
        siteName = request.form.get('siteName', '')
        rewrite = self.getRewriteConf(siteName)
        return mw.getJson({'rewrite': rewrite})

    def getRewriteTplApi(self):
        tplname = request.form.get('tplname', '')
        file = mw.getRunDir() + '/rewrite/nginx/' + tplname + '.conf'
        if not os.path.exists(file):
            return mw.returnJson(False, '模版不存在!')
        return mw.returnJson(True, 'OK', file)

    def getRewriteListApi(self):
        rlist = self.getRewriteList()
        return mw.getJson(rlist)

    def getRootDirApi(self):
        data = {}
        data['dir'] = mw.getWwwDir()
        return mw.getJson(data)

    def setEndDateApi(self):
        sid = request.form.get('id', '')
        edate = request.form.get('edate', '')
        return self.setEndDate(sid, edate)

    def addApi(self):
        webname = request.form.get('webinfo', '')
        ps = request.form.get('ps', '')
        path = request.form.get('path', '')
        version = request.form.get('version', '')
        port = request.form.get('port', '')
        return self.add(webname, port, ps, path, version)

    def checkWebStatusApi(self):
        '''
        创建站点检查web服务
        '''
        if not mw.isInstalledWeb():
            return mw.returnJson(False, '请安装并启动OpenResty服务!')

        # 这个快点
        pid = mw.getServerDir() + '/openresty/nginx/logs/nginx.pid'
        if not os.path.exists(pid):
            return mw.returnJson(False, '请启动OpenResty服务!')

        # path = mw.getServerDir() + '/openresty/init.d/openresty'
        # data = mw.execShell(path + " status")
        # if data[0].strip().find('stopped') != -1:
        #     return mw.returnJson(False, '请启动OpenResty服务!')

        # import plugins_api
        # data = plugins_api.plugins_api().run('openresty', 'status')
        # if data[0].strip() == 'stop':
        #     return mw.returnJson(False, '请启动OpenResty服务!')

        return mw.returnJson(True, 'OK')

    def addDomainApi(self):
        isError = mw.checkWebConfig()
        if isError != True:
            return mw.returnJson(False, 'ERROR: 检测到配置文件有错误,请先排除后再操作<br><br><a style="color:red;">' + isError.replace("\n", '<br>') + '</a>')

        domain = request.form.get('domain', '')
        webname = request.form.get('webname', '')
        pid = request.form.get('id', '')
        return self.addDomain(domain, webname, pid)

    def addDomain(self, domain, webname, pid):
        if len(domain) < 3:
            return mw.returnJson(False, '域名不能为空!')
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
                return mw.returnJson(False, '域名格式不正确!')

            if len(domain) == 2:
                domain_port = domain[1]
            if domain_port == "":
                domain_port = "80"

            if not mw.checkPort(domain_port):
                return mw.returnJson(False, '端口范围不合法!')

            opid = mw.M('domain').where(
                "name=? AND (port=? OR pid=?)", (domain_name, domain_port, pid,)).getField('pid')
            # print(opid)
            is_bind = False
            if type(opid) == list and len(opid) > 0:
                is_bind = True

            if type(opid) == int and opid > 0:
                is_bind = True

            if type(opid) == str and int(opid) > 0:
                is_bind = True

            if is_bind:
                return mw.returnJson(False, '您添加的域名[{}],已绑定!'.format(domain_name))
                # if mw.M('sites').where('id=?', (opid,)).count():
                #     return mw.returnJson(False, '指定域名已绑定过!')
                # mw.M('domain').where('pid=?', (opid,)).delete()

            if mw.M('binding').where('domain=?', (domain,)).count():
                return mw.returnJson(False, '您添加的域名,子目录已绑定!')

            self.nginxAddDomain(webname, domain_name, domain_port)

            mw.restartWeb()
            msg = mw.getInfo('网站[{1}]添加域名[{2}]成功!', (webname, domain_name))
            mw.writeLog('网站管理', msg)
            mw.M('domain').add('pid,name,port,addtime',
                               (pid, domain_name, domain_port, mw.getDate()))

        self.runHook('site_cb', 'add')
        return mw.returnJson(True, '域名添加成功!')

    def addDirBindApi(self):
        pid = request.form.get('id', '')
        domain = request.form.get('domain', '')
        dirName = request.form.get('dirName', '')
        tmp = domain.split(':')
        domain = tmp[0]
        port = '80'
        if len(tmp) > 1:
            port = tmp[1]
        if dirName == '':
            mw.returnJson(False, '目录不能为空!')

        reg = "^([\w\-\*]{1,100}\.){1,4}(\w{1,10}|\w{1,10}\.\w{1,10})$"
        if not re.match(reg, domain):
            return mw.returnJson(False, '主域名格式不正确!')

        siteInfo = mw.M('sites').where(
            "id=?", (pid,)).field('id,path,name').find()
        webdir = siteInfo['path'] + '/' + dirName

        if mw.M('binding').where("domain=?", (domain,)).count() > 0:
            return mw.returnJson(False, '您添加的域名已存在!')
        if mw.M('domain').where("name=?", (domain,)).count() > 0:
            return mw.returnJson(False, '您添加的域名已存在!')

        filename = self.getHostConf(siteInfo['name'])
        conf = mw.readFile(filename)
        if conf:
            rep = "enable-php-([0-9]{2,3})\.conf"
            tmp = re.search(rep, conf).groups()
            version = tmp[0]

            source_dirbind_tpl = mw.getRunDir() + '/data/tpl/nginx_dirbind.conf'
            content = mw.readFile(source_dirbind_tpl)
            content = content.replace('{$PORT}', port)
            content = content.replace('{$PHPVER}', version)
            content = content.replace('{$DIRBIND}', domain)
            content = content.replace('{$ROOT_DIR}', webdir)
            content = content.replace('{$SERVER_MAIN}', siteInfo['name'])
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
            return mw.returnJson(False, 'ERROR: <br><a style="color:red;">' + isError.replace("\n", '<br>') + '</a>')

        mw.M('binding').add('pid,domain,port,path,addtime',
                            (pid, domain, port, dirName, mw.getDate()))

        msg = mw.getInfo('网站[{1}]子目录[{2}]绑定到[{3}]',
                         (siteInfo['name'], dirName, domain))
        mw.writeLog('网站管理', msg)
        mw.restartWeb()
        mw.removeBackFile(filename)
        return mw.returnJson(True, '添加成功!')

    def delDirBindApi(self):
        mid = request.form.get('id', '')
        binding = mw.M('binding').where(
            "id=?", (mid,)).field('id,pid,domain,path').find()
        siteName = mw.M('sites').where(
            "id=?", (binding['pid'],)).getField('name')

        filename = self.getHostConf(siteName)
        conf = mw.readFile(filename)
        if conf:
            rep = "\s*.+BINDING-" + \
                binding['domain'] + \
                "-START(.|\n)+BINDING-" + binding['domain'] + "-END"
            conf = re.sub(rep, '', conf)
            mw.writeFile(filename, conf)

        mw.M('binding').where("id=?", (mid,)).delete()

        filename = self.getDirBindRewrite(siteName,  binding['path'])
        if os.path.exists(filename):
            os.remove(filename)
        mw.restartWeb()
        msg = mw.getInfo('删除网站[{1}]子目录[{2}]绑定',
                         (siteName, binding['path']))
        mw.writeLog('网站管理', msg)
        return mw.returnJson(True, '删除成功!')

        # 取子目录Rewrite
    def getDirBindRewriteApi(self):
        mid = request.form.get('id', '')
        add = request.form.get('add', '0')
        find = mw.M('binding').where(
            "id=?", (mid,)).field('id,pid,domain,path').find()
        site = mw.M('sites').where(
            "id=?", (find['pid'],)).field('id,name,path').find()

        filename = self.getDirBindRewrite(site['name'], find['path'])
        if add == '1':
            mw.writeFile(filename, '')
            file = self.getHostConf(site['name'])
            conf = mw.readFile(file)
            domain = find['domain']
            rep = "\n#BINDING-" + domain + \
                "-START(.|\n)+BINDING-" + domain + "-END"
            tmp = re.search(rep, conf).group()
            dirConf = tmp.replace('rewrite/' + site['name'] + '.conf;', 'rewrite/' + site[
                'name'] + '_' + find['path'] + '.conf;')
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
        return mw.getJson(data)

    # 修改物理路径
    def setPathApi(self):
        mid = request.form.get('id', '')
        path = request.form.get('path', '')

        path = self.getPath(path)
        if path == "" or mid == '0':
            return mw.returnJson(False,  "目录不能为空!")

        import files_api
        if not files_api.files_api().checkDir(path):
            return mw.returnJson(False,  "不能以系统关键目录作为站点目录")

        siteFind = mw.M("sites").where(
            "id=?", (mid,)).field('path,name').find()
        if siteFind["path"] == path:
            return mw.returnJson(False,  "与原路径一致，无需修改!")
        file = self.getHostConf(siteFind['name'])
        conf = mw.readFile(file)
        if conf:
            conf = conf.replace(siteFind['path'], path)
            mw.writeFile(file, conf)

        # 创建basedir
        # userIni = path + '/.user.ini'
        # if os.path.exists(userIni):
            # mw.execShell("chattr -i " + userIni)
        # mw.writeFile(userIni, 'open_basedir=' + path + '/:/tmp/:/proc/')
        # mw.execShell('chmod 644 ' + userIni)
        # mw.execShell('chown root:root ' + userIni)
        # mw.execShell('chattr +i ' + userIni)

        mw.restartWeb()
        mw.M("sites").where("id=?", (mid,)).setField('path', path)
        msg = mw.getInfo('修改网站[{1}]物理路径成功!', (siteFind['name'],))
        mw.writeLog('网站管理', msg)
        return mw.returnJson(True,  "设置成功!")

    # 设置当前站点运行目录
    def setSiteRunPathApi(self):
        mid = request.form.get('id', '')
        runPath = request.form.get('runPath', '')
        siteName = mw.M('sites').where('id=?', (mid,)).getField('name')
        sitePath = mw.M('sites').where('id=?', (mid,)).getField('path')

        newPath = sitePath + runPath

        # 处理Nginx
        filename = self.getHostConf(siteName)
        if os.path.exists(filename):
            conf = mw.readFile(filename)
            rep = '\s*root\s*(.+);'
            path = re.search(rep, conf).groups()[0]
            conf = conf.replace(path, newPath)
            mw.writeFile(filename, conf)

        self.setDirUserINI(sitePath, runPath)

        mw.restartWeb()
        return mw.returnJson(True, '设置成功!')

    # 设置目录加密
    def setHasPwdApi(self):
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        siteName = request.form.get('siteName', '')
        mid = request.form.get('id', '')

        if len(username.strip()) == 0 or len(password.strip()) == 0:
            return mw.returnJson(False, '用户名或密码不能为空!')

        if siteName == '':
            siteName = mw.M('sites').where('id=?', (mid,)).getField('name')

        # self.closeHasPwd(get)
        filename = self.passPath + '/' + siteName + '.pass'
        # print(filename)
        passconf = username + ':' + mw.hasPwd(password)

        if siteName == 'phpmyadmin':
            configFile = self.getHostConf('phpmyadmin')
        else:
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

        mw.restartWeb()
        msg = mw.getInfo('设置网站[{1}]为需要密码认证!', (siteName,))
        mw.writeLog("网站管理", msg)
        return mw.returnJson(True, '设置成功!')

    # 取消目录加密
    def closeHasPwdApi(self):
        siteName = request.form.get('siteName', '')
        mid = request.form.get('id', '')
        if siteName == '':
            siteName = mw.M('sites').where('id=?', (mid,)).getField('name')

        if siteName == 'phpmyadmin':
            configFile = self.getHostConf('phpmyadmin')
        else:
            configFile = self.getHostConf(siteName)

        if os.path.exists(configFile):
            conf = mw.readFile(configFile)
            rep = "\n\s*#AUTH_START(.|\n){1,200}#AUTH_END"
            conf = re.sub(rep, '', conf)
            mw.writeFile(configFile, conf)

        mw.restartWeb()
        msg = mw.getInfo('清除网站[{1}]的密码认证!', (siteName,))
        mw.writeLog("网站管理", msg)
        return mw.returnJson(True, '设置成功!')

    def delDomainApi(self):
        domain = request.form.get('domain', '')
        webname = request.form.get('webname', '')
        port = request.form.get('port', '')
        pid = request.form.get('id', '')

        find = mw.M('domain').where("pid=? AND name=?",
                                    (pid, domain)).field('id,name').find()

        domain_count = mw.M('domain').where("pid=?", (pid,)).count()
        if domain_count == 1:
            return mw.returnJson(False, '最后一个域名不能删除!')

        file = self.getHostConf(webname)
        conf = mw.readFile(file)
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
            port_count = mw.M('domain').where(
                'pid=? AND port=?', (pid, port)).count()
            if mw.inArray(tmp, port) == True and port_count < 2:
                rep = "\n*\s+listen\s+" + port + ";"
                conf = re.sub(rep, '', conf)
            # 保存配置
            mw.writeFile(file, conf)

        mw.M('domain').where("id=?", (find['id'],)).delete()
        msg = mw.getInfo('网站[{1}]删除域名[{2}]成功!', (webname, domain))
        mw.writeLog('网站管理', msg)
        mw.restartWeb()
        return mw.returnJson(True, '站点删除成功!')

    def deleteApi(self):
        sid = request.form.get('id', '')
        webname = request.form.get('webname', '')
        path = request.form.get('path', '0')
        return self.delete(sid, webname, path)

    # 操作 重定向配置
    def operateRedirectConf(self, siteName, method='start'):
        vhost_file = self.vhostPath + '/' + siteName + '.conf'
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

    # get_redirect_status
    def getRedirectApi(self):
        _siteName = request.form.get("siteName", '')

        # read data base
        data_path = self.getRedirectDataPath(_siteName)
        data_content = mw.readFile(data_path)
        if data_content == False:
            mw.execShell("mkdir {}/{}".format(self.redirectPath, _siteName))
            return mw.returnJson(True, "", {"result": [], "count": 0})
        # get
        # conf_path = "{}/{}/*.conf".format(self.redirectPath, siteName)
        # conf_list = glob.glob(conf_path)
        # if conf_list == []:
        #     return mw.returnJson(True, "", {"result": [], "count": 0})
        try:
            data = json.loads(data_content)
        except:
            mw.execShell("rm -rf {}/{}".format(self.redirectPath, _siteName))
            return mw.returnJson(True, "", {"result": [], "count": 0})

        # 处理301信息
        return mw.returnJson(True, "ok", {"result": data, "count": len(data)})

    def getRedirectConfApi(self):
        _siteName = request.form.get("siteName", '')
        _id = request.form.get("id", '')
        if _id == '' or _siteName == '':
            return mw.returnJson(False, "必填项不能为空!")

        data = mw.readFile(
            "{}/{}/{}.conf".format(self.redirectPath, _siteName, _id))
        if data == False:
            return mw.returnJson(False, "获取失败!")
        return mw.returnJson(True, "ok", {"result": data})

    def saveRedirectConfApi(self):
        _siteName = request.form.get("siteName", '')
        _id = request.form.get("id", '')
        _config = request.form.get("config", "")
        if _id == '' or _siteName == '':
            return mw.returnJson(False, "必填项不能为空!")

        _old_config = mw.readFile(
            "{}/{}/{}.conf".format(self.redirectPath, _siteName, _id))
        if _old_config == False:
            return mw.returnJson(False, "非法操作")

        mw.writeFile("{}/{}/{}.conf".format(self.redirectPath,
                                            _siteName, _id), _config)
        rule_test = mw.checkWebConfig()
        if rule_test != True:
            mw.writeFile("{}/{}/{}.conf".format(self.redirectPath,
                                                _siteName, _id), _old_config)
            return mw.returnJson(False, "OpenResty 配置测试不通过, 请重试: {}".format(rule_test))

        self.operateRedirectConf(_siteName, 'start')
        mw.restartWeb()
        return mw.returnJson(True, "ok")

    # get redirect status
    def setRedirectApi(self):
        _siteName = request.form.get("siteName", '')
        # from (example.com / /test/)
        _from = request.form.get("from", '')
        _to = request.form.get("to", '')              # redirect to
        _type = request.form.get("type", '')          # path / domain
        _rType = request.form.get("r_type", '')       # redirect type
        _keepPath = request.form.get("keep_path", '')  # keep path

        if _siteName == '' or _from == '' or _to == '' or _type == '' or _rType == '':
            return mw.returnJson(False, "必填项不能为空!")

        data_path = self.getRedirectDataPath(_siteName)
        data_content = mw.readFile(
            data_path) if os.path.exists(data_path) else ""
        data = json.loads(data_content) if data_content != "" else []

        _rTypeCode = 0 if _rType == "301" else 1
        _typeCode = 0 if _type == "path" else 1
        _keepPath = 1 if _keepPath == "1" else 0

        # check if domain exists in site
        if _typeCode == 1:
            pid = mw.M('domain').where("name=?", (_siteName,)).field(
                'id,pid,name,port,addtime').select()
            site_domain_lists = mw.M('domain').where("pid=?", (pid[0]['pid'],)).field(
                'name').select()
            found = False
            for item in site_domain_lists:
                if item['name'] == _from:
                    found = True
                    break
            if found == False:
                return mw.returnJson(False, "域名不存在!")

        file_content = ""
        # path
        if _typeCode == 0:
            redirect_type = "permanent" if _rTypeCode == 0 else "redirect"
            if not _from.startswith("/"):
                _from = "/{}".format(_from)
            if _keepPath == 1:
                _to = "{}$1".format(_to)
                _from = "{}(.*)".format(_from)
            file_content = "rewrite ^{} {} {};".format(
                _from, _to, redirect_type)
        # domain
        else:
            if _keepPath == 1:
                _to = "{}$request_uri".format(_to)

            redirect_type = "301" if _rTypeCode == 0 else "302"
            _if = "if ($host ~ '^{}')".format(_from)
            _return = "return {} {}; ".format(redirect_type, _to)
            file_content = _if + "{\r\n    " + _return + "\r\n}"

        _id = mw.md5("{}+{}".format(file_content, _siteName))

        # 防止规则重复
        for item in data:
            if item["r_from"] == _from:
                return mw.returnJson(False, "重复的规则!")

        rep = "http(s)?\:\/\/([a-zA-Z0-9][-a-zA-Z0-9]{0,62}\.)+([a-zA-Z0-9][a-zA-Z0-9]{0,62})+.?"
        if not re.match(rep, _to):
            return mw.returnJson(False, "错误的目标地址")

        # write data json file
        data.append({"r_from": _from, "type": _typeCode, "r_type": _rTypeCode,
                     "r_to": _to, 'keep_path': _keepPath, 'id': _id})
        mw.writeFile(data_path, json.dumps(data))
        mw.writeFile(
            "{}/{}.conf".format(self.getRedirectPath(_siteName), _id), file_content)

        self.operateRedirectConf(_siteName, 'start')
        mw.restartWeb()
        return mw.returnJson(True, "ok")

    # 删除指定重定向
    def delRedirectApi(self):
        _siteName = request.form.get("siteName", '')
        _id = request.form.get("id", '')
        if _id == '' or _siteName == '':
            return mw.returnJson(False, "必填项不能为空!")

        try:
            data_path = self.getRedirectDataPath(_siteName)
            data_content = mw.readFile(
                data_path) if os.path.exists(data_path) else ""
            data = json.loads(data_content) if data_content != "" else []
            for item in data:
                if item["id"] == _id:
                    data.remove(item)
                    break
            # write database
            mw.writeFile(data_path, json.dumps(data))
            # data is empty ,should stop
            if len(data) == 0:
                self.operateRedirectConf(_siteName, 'stop')
            # remove conf file
            mw.execShell(
                "rm -rf {}/{}.conf".format(self.getRedirectPath(_siteName), _id))
        except:
            return mw.returnJson(False, "删除失败!")
        return mw.returnJson(True, "删除成功!")

    # 操作 反向代理配置
    def operateProxyConf(self, siteName, method='start'):
        vhost_file = self.vhostPath + '/' + siteName + '.conf'
        content = mw.readFile(vhost_file)

        proxy_cnf = '''#PROXY-START
    include %s/*.conf;
    #PROXY-END''' % (self.getProxyPath(siteName))

        proxy_cnf_source = '#PROXY-START'

        if content.find('#PROXY-END') != -1:
            if method == 'stop':
                rep = '#PROXY-START(\n|.){1,500}#PROXY-END'
                content = re.sub(rep, '#PROXY-START', content)
        else:
            if method == 'start':
                content = re.sub(proxy_cnf_source, proxy_cnf, content)

        mw.writeFile(vhost_file, content)

    def getProxyConfApi(self):
        _siteName = request.form.get("siteName", '')
        _id = request.form.get("id", '')
        if _id == '' or _siteName == '':
            return mw.returnJson(False, "必填项不能为空!")

        conf_file = "{}/{}/{}.conf".format(self.proxyPath, _siteName, _id)
        if not os.path.exists(conf_file):
            conf_file = "{}/{}/{}.conf.txt".format(
                self.proxyPath, _siteName, _id)

        data = mw.readFile(conf_file)
        if data == False:
            return mw.returnJson(False, "获取失败!")
        return mw.returnJson(True, "ok", {"result": data})

    def setProxyStatusApi(self):
        _siteName = request.form.get("siteName", '')
        _status = request.form.get("status", '')
        _id = request.form.get("id", '')
        if _status == '' or _siteName == '' or _id == '':
            return mw.returnJson(False, "必填项不能为空!")

        conf_file = "{}/{}/{}.conf".format(self.proxyPath, _siteName, _id)
        conf_txt = "{}/{}/{}.conf.txt".format(self.proxyPath, _siteName, _id)

        if _status == '1':
            mw.execShell('mv ' + conf_txt + ' ' + conf_file)
        else:
            mw.execShell('mv ' + conf_file + ' ' + conf_txt)

        mw.restartWeb()
        return mw.returnJson(True, "OK")

    def saveProxyConfApi(self):
        _siteName = request.form.get("siteName", '')
        _id = request.form.get("id", '')
        _config = request.form.get("config", "")
        if _id == '' or _siteName == '':
            return mw.returnJson(False, "必填项不能为空!")

        proxy_file = "{}/{}/{}.conf".format(self.proxyPath, _siteName, _id)
        mw.backFile(proxy_file)
        mw.writeFile(proxy_file, _config)
        rule_test = mw.checkWebConfig()
        if rule_test != True:
            mw.restoreFile(proxy_file)
            mw.removeBackFile(proxy_file)
            return mw.returnJson(False, "OpenResty 配置测试不通过, 请重试: {}".format(rule_test))

        mw.removeBackFile(proxy_file)
        self.operateRedirectConf(_siteName, 'start')
        mw.restartWeb()
        return mw.returnJson(True, "ok")

    # 读取 网站 反向代理列表
    def getProxyListApi(self):
        _siteName = request.form.get('siteName', '')

        data_path = self.getProxyDataPath(_siteName)
        data_content = mw.readFile(data_path)

        # not exists
        if data_content == False:
            mw.execShell("mkdir {}/{}".format(self.proxyPath, _siteName))
            return mw.returnJson(True, "", {"result": [], "count": 0})

        try:
            data = json.loads(data_content)
        except:
            mw.execShell("rm -rf {}/{}".format(self.proxyPath, _siteName))
            return mw.returnJson(True, "", {"result": [], "count": 0})

        tmp = []
        for proxy in data:
            proxy_dir = "{}/{}".format(self.proxyPath, _siteName)
            proxy_dir_file = proxy_dir + '/' + proxy['id'] + '.conf'
            if os.path.exists(proxy_dir_file):
                proxy['status'] = True
            else:
                proxy['status'] = False
            tmp.append(proxy)

        return mw.returnJson(True, "ok", {"result": data, "count": len(data)})

    # 设置 网站 反向代理列表
    def setProxyApi(self):
        _siteName = request.form.get('siteName', '')
        _from = request.form.get('from', '')
        _to = request.form.get('to', '')
        _host = request.form.get('host', '')
        _name = request.form.get('name', '')
        _open_proxy = request.form.get('open_proxy', '')
        _open_cache = request.form.get('open_cache', '')
        _cache_time = request.form.get('cache_time', '')
        _id = request.form.get('id', '')

        # print(_name, _siteName, _from, _to, _host)
        if _name == "" or _siteName == "" or _from == "" or _to == "" or _host == "":
            return mw.returnJson(False, "必填项不能为空")

        rep = "http(s)?\:\/\/([a-zA-Z0-9][-a-zA-Z0-9]{0,62}\.)+([a-zA-Z0-9][a-zA-Z0-9]{0,62})+.?"
        if not re.match(rep, _to):
            return mw.returnJson(False, "错误的目标地址!")

        # get host from url
        try:
            if _host == "$host":
                host_tmp = urlparse(_to)
                _host = host_tmp.netloc
        except:
            return mw.returnJson(False, "错误的目标地址")

        proxy_site_path = self.getProxyDataPath(_siteName)
        data_content = mw.readFile(
            proxy_site_path) if os.path.exists(proxy_site_path) else ""
        data = json.loads(data_content) if data_content != "" else []

        proxy_action = 'add'
        if _id == "":
            _id = mw.md5("{}".format(_name))
        else:
            proxy_action = 'edit'

        if proxy_action == "add":
            for item in data:
                if item["name"] == _name:
                    return mw.returnJson(False, "名称重复!!")
                if item["from"] == _from:
                    return mw.returnJson(False, "代理目录已存在!!")

        tpl = "#PROXY-START\n\
location ^~ {from} {\n\
    proxy_pass {to};\n\
    proxy_set_header Host {host};\n\
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
    if ( $uri ~* \"\.(gif|png|jpg|css|js|woff|woff2)$\" )\n\
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
    if ( $uri ~* \"\.(gif|png|jpg|css|js|woff|woff2)$\" )\n\
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
        if _from[0] != '/':
            _from = '/' + _from
        tpl = tpl.replace("{from}", _from, 999)
        tpl = tpl.replace("{to}", _to)
        tpl = tpl.replace("{host}", _host, 999)
        tpl = tpl.replace("{cache_time}", _cache_time, 999)

        if _open_cache == 'on':
            tpl_proxy_cache = tpl_proxy_cache.replace(
                "{cache_time}", _cache_time, 999)
            tpl = tpl.replace("{proxy_cache}", tpl_proxy_cache, 999)
        else:
            tpl = tpl.replace("{proxy_cache}", tpl_proxy_nocache, 999)


        conf_proxy = "{}/{}.conf".format(self.getProxyPath(_siteName), _id)
        conf_bk = "{}/{}.conf.txt".format(self.getProxyPath(_siteName), _id)
        mw.writeFile(conf_proxy, tpl)

        rule_test = mw.checkWebConfig()
        if rule_test != True:
            os.remove(conf_proxy)
            return mw.returnJson(False, "OpenResty配置测试不通过, 请重试: {}".format(rule_test))

        if proxy_action == "add":
            # 添加代理
            _id = mw.md5("{}".format(_name))
            for item in data:
                if item["name"] == _name:
                    return mw.returnJson(False, "名称重复!")
                if item["from"] == _from:
                    return mw.returnJson(False, "代理目录已存在!")
            data.append({
                "name": _name,
                "from": _from,
                "to": _to,
                "host": _host,
                "open_cache": _open_cache,
                "open_proxy": _open_proxy,
                "cache_time": _cache_time,
                "id": _id,
            })
        else:
            # 修改代理
            dindex = -1
            for x in range(len(data)):
                if data[x]["id"] == _id:
                    dindex = x
                    break
            if dindex < 0:
                return mw.returnJson(False, "异常请求")
            data[dindex]['from'] = _from
            data[dindex]['to'] = _to
            data[dindex]['host'] = _host
            data[dindex]['open_cache'] = _open_cache
            data[dindex]['open_proxy'] = _open_proxy
            data[dindex]['cache_time'] = _cache_time

        if _open_proxy != 'on':
            os.rename(conf_proxy, conf_bk)

        mw.writeFile(proxy_site_path, json.dumps(data))
        self.operateProxyConf(_siteName, 'start')
        mw.restartWeb()
        return mw.returnJson(True, "ok", {"hash": _id})

    def delProxyApi(self):
        _siteName = request.form.get("siteName", '')
        _id = request.form.get("id", '')
        if _id == '' or _siteName == '':
            return mw.returnJson(False, "必填项不能为空!")

        try:
            data_path = self.getProxyDataPath(_siteName)
            data_content = mw.readFile(
                data_path) if os.path.exists(data_path) else ""
            data = json.loads(data_content) if data_content != "" else []
            for item in data:
                if item["id"] == _id:
                    data.remove(item)
                    break
            # write database
            mw.writeFile(data_path, json.dumps(data))

            # data is empty,should stop
            if len(data) == 0:
                self.operateProxyConf(_siteName, 'stop')
            # remove conf file
            cmd = "rm -rf {}/{}.conf*".format(
                self.getProxyPath(_siteName), _id)
            mw.execShell(cmd)
        except:
            return mw.returnJson(False, "删除反代失败!")

        mw.restartWeb()
        return mw.returnJson(True, "删除反代成功!")

    def getSiteTypesApi(self):
        # 取网站分类
        data = mw.M("site_types").field("id,name").order("id asc").select()
        data.insert(0, {"id": 0, "name": "默认分类"})
        return mw.getJson(data)

    def getSiteDocApi(self):
        stype = request.form.get('type', '0').strip()
        vlist = []
        vlist.append('')
        vlist.append(mw.getServerDir() +
                     '/openresty/nginx/html/index.html')
        vlist.append(mw.getServerDir() + '/openresty/nginx/html/404.html')
        vlist.append(mw.getServerDir() +
                     '/openresty/nginx/html/index.html')
        vlist.append(mw.getServerDir() + '/web_conf/stop/index.html')
        data = {}
        data['path'] = vlist[int(stype)]
        return mw.returnJson(True, 'ok', data)

    def addSiteTypeApi(self):
        name = request.form.get('name', '').strip()
        if not name:
            return mw.returnJson(False, "分类名称不能为空")
        if len(name) > 18:
            return mw.returnJson(False, "分类名称长度不能超过6个汉字或18位字母")
        if mw.M('site_types').count() >= 10:
            return mw.returnJson(False, '最多添加10个分类!')
        if mw.M('site_types').where('name=?', (name,)).count() > 0:
            return mw.returnJson(False, "指定分类名称已存在!")
        mw.M('site_types').add("name", (name,))
        return mw.returnJson(True, '添加成功!')

    def removeSiteTypeApi(self):
        mid = request.form.get('id', '')
        if mw.M('site_types').where('id=?', (mid,)).count() == 0:
            return mw.returnJson(False, "指定分类不存在!")
        mw.M('site_types').where('id=?', (mid,)).delete()
        mw.M("sites").where("type_id=?", (mid,)).save("type_id", (0,))
        return mw.returnJson(True, "分类已删除!")

    def modifySiteTypeNameApi(self):
        # 修改网站分类名称
        name = request.form.get('name', '').strip()
        mid = request.form.get('id', '')
        if not name:
            return mw.returnJson(False, "分类名称不能为空")
        if len(name) > 18:
            return mw.returnJson(False, "分类名称长度不能超过6个汉字或18位字母")
        if mw.M('site_types').where('id=?', (mid,)).count() == 0:
            return mw.returnJson(False, "指定分类不存在!")
        mw.M('site_types').where('id=?', (mid,)).setField('name', name)
        return mw.returnJson(True, "修改成功!")

    def setSiteTypeApi(self):
        # 设置指定站点的分类
        site_ids = request.form.get('site_ids', '')
        mid = request.form.get('id', '')
        site_ids = json.loads(site_ids)
        for sid in site_ids:
            print(mw.M('sites').where('id=?', (sid,)).setField('type_id', mid))
        return mw.returnJson(True, "设置成功!")

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

    def getSitePath(self, siteName):
        file = self.getHostConf(siteName)
        if os.path.exists(file):
            conf = mw.readFile(file)
            rep = '\s*root\s*(.+);'
            find_cnf = re.search(rep, conf)
            if not find_cnf:
                return ''
            path = find_cnf.groups()[0]
            return path
        return ''

    # 取当站点前运行目录
    def getSiteRunPath(self, mid):
        siteName = mw.M('sites').where('id=?', (mid,)).getField('name')
        sitePath = mw.M('sites').where('id=?', (mid,)).getField('path')
        path = sitePath

        filename = self.getHostConf(siteName)
        if os.path.exists(filename):
            conf = mw.readFile(filename)
            rep = '\s*root\s*(.+);'
            path = re.search(rep, conf).groups()[0]

        data = {}
        if sitePath == path:
            data['runPath'] = '/'
        else:
            data['runPath'] = path.replace(sitePath, '')

        dirnames = []
        dirnames.append('/')
        for filename in os.listdir(sitePath):
            try:
                filePath = sitePath + '/' + filename
                if os.path.islink(filePath):
                    continue
                if os.path.isdir(filePath):
                    dirnames.append('/' + filename)
            except:
                pass

        data['dirs'] = dirnames
        return data

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

    def getDomain(self, pid):
        _list = mw.M('domain').where("pid=?", (pid,)).field(
            'id,pid,name,port,addtime').select()
        return mw.getJson(_list)

    def getLogs(self, siteName):
        logPath = mw.getLogsDir() + '/' + siteName + '.log'
        if not os.path.exists(logPath):
            return mw.returnJson(False, '日志为空')
        return mw.returnJson(True, mw.getLastLine(logPath, 100))

    def getErrorLogs(self, siteName):
        logPath = mw.getLogsDir() + '/' + siteName + '.error.log'
        if not os.path.exists(logPath):
            return mw.returnJson(False, '日志为空')
        return mw.returnJson(True, mw.getLastLine(logPath, 100))

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

    def getSitePhpVersion(self, siteName):
        conf = mw.readFile(self.getHostConf(siteName))
        rep = "enable-php-(.*)\.conf"
        find_php_cnf = re.search(rep, conf)

        def_pver = '00'
        if find_php_cnf:
            tmp = find_php_cnf.groups()
            def_pver = tmp[0]
            
        data = {}
        data['phpversion'] = def_pver
        return mw.getJson(data)

    def getIndex(self, sid):
        siteName = mw.M('sites').where("id=?", (sid,)).getField('name')
        file = self.getHostConf(siteName)
        conf = mw.readFile(file)
        rep = "\s+index\s+(.+);"
        tmp = re.search(rep, conf).groups()
        return tmp[0].replace(' ', ',')

    def setIndex(self, sid, index):
        if index.find('.') == -1:
            return mw.returnJson(False,  '默认文档格式不正确，例：index.html')

        index = index.replace(' ', '')
        index = index.replace(',,', ',')

        if len(index) < 3:
            return mw.returnJson(False,  '默认文档不能为空!')

        siteName = mw.M('sites').where("id=?", (sid,)).getField('name')
        index_l = index.replace(",", " ")
        file = self.getHostConf(siteName)
        conf = mw.readFile(file)
        if conf:
            rep = "\s+index\s+.+;"
            conf = re.sub(rep, "\n\tindex " + index_l + ";", conf)
            mw.writeFile(file, conf)

        mw.writeLog('TYPE_SITE', 'SITE_INDEX_SUCCESS', (siteName, index_l))
        return mw.returnJson(True,  '设置成功!')

    def getLimitNet(self, sid):
        siteName = mw.M('sites').where("id=?", (sid,)).getField('name')
        filename = self.getHostConf(siteName)
        # 站点总并发
        data = {}
        conf = mw.readFile(filename)
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

        return mw.getJson(data)

    def checkIndexConf(self):
        limit = self.getIndexConf()
        nginxConf = mw.readFile(limit)
        limitConf = "limit_conn_zone $binary_remote_addr zone=perip:10m;\n\t\tlimit_conn_zone $server_name zone=perserver:10m;"
        nginxConf = nginxConf.replace(
            "#limit_conn_zone $binary_remote_addr zone=perip:10m;", limitConf)
        mw.writeFile(limit, nginxConf)

    def saveLimitNet(self, sid, perserver, perip, limit_rate):

        str_perserver = 'limit_conn perserver ' + perserver + ';'
        str_perip = 'limit_conn perip ' + perip + ';'
        str_limit_rate = 'limit_rate ' + limit_rate + 'k;'

        siteName = mw.M('sites').where("id=?", (sid,)).getField('name')
        filename = self.getHostConf(siteName)

        conf = mw.readFile(filename)
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

        mw.writeFile(filename, conf)
        mw.restartWeb()
        mw.writeLog('TYPE_SITE', 'SITE_NETLIMIT_OPEN_SUCCESS', (siteName,))
        return mw.returnJson(True, '设置成功!')

    def closeLimitNet(self, sid):
        siteName = mw.M('sites').where("id=?", (sid,)).getField('name')
        filename = self.getHostConf(siteName)
        conf = mw.readFile(filename)
        # 清理总并发
        rep = "\s+limit_conn\s+perserver\s+([0-9]+);"
        conf = re.sub(rep, '', conf)

        # 清理IP并发限制
        rep = "\s+limit_conn\s+perip\s+([0-9]+);"
        conf = re.sub(rep, '', conf)

        # 清理请求流量限制
        rep = "\s+limit_rate\s+([0-9]+)\w+;"
        conf = re.sub(rep, '', conf)
        mw.writeFile(filename, conf)
        mw.restartWeb()
        mw.writeLog(
            'TYPE_SITE', 'SITE_NETLIMIT_CLOSE_SUCCESS', (siteName,))
        return mw.returnJson(True, '已关闭流量限制!')

    def getSecurity(self, sid, name):
        filename = self.getHostConf(name)
        conf = mw.readFile(filename)
        data = {}
        if conf.find('SECURITY-START') != -1:
            rep = "#SECURITY-START(\n|.){1,500}#SECURITY-END"
            tmp = re.search(rep, conf).group()
            data['fix'] = re.search(
                "\(.+\)\$", tmp).group().replace('(', '').replace(')$', '').replace('|', ',')

            data['status'] = False
            data['none'] = False

            valid_referers = re.search(
                "valid_referers\s+(.+);\n", tmp)
            valid_referers_none = re.search(
                "valid_referers\s+none\s+blocked\s+(.+);\n", tmp)

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

            # print(data)
        else:
            data['fix'] = 'jpg,jpeg,gif,png,js,css'
            domains = mw.M('domain').where(
                'pid=?', (sid,)).field('name').select()
            tmp = []
            for domain in domains:
                tmp.append(domain['name'])
            data['domains'] = ','.join(tmp)
            data['status'] = False
            data['none'] = False
        return mw.getJson(data)

    def setSecurity(self, sid, name, fix, domains, status, none=''):
        if len(fix) < 2:
            return mw.returnJson(False, 'URL后缀不能为空!')
        file = self.getHostConf(name)
        if os.path.exists(file):
            conf = mw.readFile(file)
            if status == 'false':
                rep = "\s{0,4}#SECURITY-START(\n|.){1,500}#SECURITY-END\n?"
                conf = re.sub(rep, '', conf)
                mw.writeLog('网站管理', '站点[' + name + ']已关闭防盗链设置!')
            else:
                rep = "\s{0,4}#SECURITY-START(\n|.){1,500}#SECURITY-END\n?"
                conf = re.sub(rep, '', conf)

                valid_referers = domains.strip().replace(',', ' ')
                if none == 'true':
                    valid_referers = 'none blocked ' + valid_referers

                pre_path = self.setupPath + "/php/conf"
                re_path = "include\s+" + pre_path + "/enable-php-"
                rconf = '''#SECURITY-START 防盗链配置
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
        return mw.returnJson(True, '设置成功!')

    def getPhpVersion(self):
        phpVersions = ('00', '52', '53', '54', '55',
                       '56', '70', '71', '72', '73', '74', '80', '81', '82', '83')
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
        rep = "enable-php-(.*?)\.conf"
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

    # 是否跳转到https
    def isToHttps(self, siteName):
        file = self.getHostConf(siteName)
        conf = mw.readFile(file)
        if conf:
            # if conf.find('HTTP_TO_HTTPS_START') != -1:
            #     return True
            if conf.find('$server_port !~ 443') != -1:
                return True
        return False

    def getRewriteList(self):
        rewriteList = {}
        rewriteList['rewrite'] = []
        rewriteList['rewrite'].append('0.当前')
        for ds in os.listdir('rewrite/nginx'):
            rewriteList['rewrite'].append(ds[0:len(ds) - 5])
        rewriteList['rewrite'] = sorted(rewriteList['rewrite'])
        return rewriteList

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

    def nginxAddDomain(self, webname, domain, port):
        file = self.getHostConf(webname)
        conf = mw.readFile(file)
        if not conf:
            return

        # 添加域名
        rep = "server_name\s*(.*);"
        tmp = re.search(rep, conf).group()
        domains = tmp.split(' ')
        if not mw.inArray(domains, domain):
            newServerName = tmp.replace(';', ' ' + domain + ';')
            conf = conf.replace(tmp, newServerName)

        # 添加端口
        rep = "listen\s+([0-9]+)\s*[default_server]*\s*;"
        tmp = re.findall(rep, conf)
        if not mw.inArray(tmp, port):
            listen = re.search(rep, conf).group()
            conf = conf.replace(
                listen, listen + "\n\tlisten " + port + ';')
        # 保存配置文件
        mw.writeFile(file, conf)
        return True

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
        rewrite_file = self.rewritePath + '/' + self.siteName + '.conf'
        mw.writeFile(rewrite_file, '')

    def add(self, webname, port, ps, path, version):
        site_root_dir = mw.getWwwDir()
        if site_root_dir == path.rstrip('/'):
            return mw.returnJson(False, '不要以网站根目录创建站点!')

        siteMenu = json.loads(webname)
        self.siteName = self.toPunycode(
            siteMenu['domain'].strip().split(':')[0]).strip()
        self.sitePath = self.toPunycodePath(
            self.getPath(path.replace(' ', '')))
        self.sitePort = port.strip().replace(' ', '')
        self.phpVersion = version

        if mw.M('sites').where("name=?", (self.siteName,)).count():
            return mw.returnJson(False, '您添加的站点已存在!')

        # 写入数据库
        pid = mw.M('sites').add('name,path,status,ps,edate,addtime,type_id',
                                (self.siteName, self.sitePath, '1', ps, '0000-00-00', mw.getDate(), 0,))
        opid = mw.M('domain').where("name=?", (self.siteName,)).getField('pid')
        if opid:
            if mw.M('sites').where('id=?', (opid,)).count():
                return mw.returnJson(False, '您添加的域名已存在!')
            mw.M('domain').where('pid=?', (opid,)).delete()

        self.createRootDir(self.sitePath)
        self.nginxAddConf()

        mw.M('domain').add('pid,name,port,addtime',
                           (pid, self.siteName, self.sitePort, mw.getDate()))

        # 添加更多域名
        for domain in siteMenu['domainlist']:
            self.addDomain(domain, self.siteName, pid)

        data = {}
        data['siteStatus'] = False
        mw.restartWeb()

        self.runHook('site_cb', 'add')
        return mw.returnJson(True, '添加成功')

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

    def delete(self, sid, webname, path):
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

        mw.M('sites').where("id=?", (sid,)).delete()
        mw.M('domain').where("pid=?", (sid,)).delete()
        mw.M('domain').where("name=?", (webname,)).delete()

        # binding domain delete
        binding_list = mw.M('binding').field(
            'id,domain').where("pid=?", (sid,)).select()

        for x in binding_list:
            wlog = mw.getLogsDir() + "/" + webname + "_" + x['domain'] + ".log"
            wlog_error = mw.getLogsDir() + "/" + webname + "_" + \
                x['domain'] + ".error.log"

            if os.path.exists(wlog):
                mw.execShell('rm -rf ' + wlog)
            if os.path.exists(wlog_error):
                mw.execShell('rm -rf ' + wlog_error)

        mw.M('binding').where("pid=?", (sid,)).delete()
        mw.restartWeb()

        self.runHook('site_cb', 'delete')
        return mw.returnJson(True, '站点删除成功!')

    def setEndDate(self, sid, edate):
        result = mw.M('sites').where(
            'id=?', (sid,)).setField('edate', edate)
        siteName = mw.M('sites').where('id=?', (sid,)).getField('name')
        mw.writeLog('TYPE_SITE', '设置成功,站点到期后将自动停止!', (siteName, edate))
        return mw.returnJson(True, '设置成功,站点到期后将自动停止!')

    # ssl相关方法 start
    def setSslConf(self, siteName):
        file = self.getHostConf(siteName)
        conf = mw.readFile(file)

        version = ''
        version_file_pl = mw.getServerDir() + '/openresty/version.pl'
        if os.path.exists(version_file_pl):
            version = mw.readFile(version_file_pl)
            version = version.strip()


        keyPath = self.sslDir + '/' + siteName + '/privkey.pem'
        certPath = self.sslDir + '/' + siteName + '/fullchain.pem'
        if conf:
            if conf.find('ssl_certificate') == -1:
                # ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:HIGH:!aNULL:!MD5:!RC4:!DHE;
                # add_header Alt-Svc 'h3=":443";ma=86400,h3-29=":443";ma=86400';
                http3Header = """
    add_header Strict-Transport-Security "max-age=63072000";
    add_header Alt-Svc 'h3=":443";ma=86400';
"""
                if version != '1.25.3.1':
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

            rep = "listen\s+([0-9]+)\s*[default_server]*;"
            tmp = re.findall(rep, conf)
            if not mw.inArray(tmp, '443'):
                listen = re.search(rep, conf).group()
                
                if version == '1.25.3.1':
                    http_ssl = "\n\tlisten 443 ssl;"
                    http_ssl = http_ssl + "\n\tlisten [::]:443 ssl;"
                    http_ssl = http_ssl + "\n\tlisten 443 quic;"
                    http_ssl = http_ssl + "\n\tlisten [::]:443 quic;"
                    http_ssl = http_ssl + "\n\thttp2 on;"
                else:
                    http_ssl = "\n\tlisten 443 ssl http2;"
                    http_ssl = http_ssl + "\n\tlisten [::]:443 ssl http2;"


                conf = conf.replace(listen, listen + http_ssl)

            mw.backFile(file)
            mw.writeFile(file, conf)
            isError = mw.checkWebConfig()
            if(isError != True):
                mw.restoreFile(file)
                return mw.returnData(False, '证书错误: <br><a style="color:red;">' + isError.replace("\n", '<br>') + '</a>')

        self.saveCert(keyPath, certPath)

        msg = mw.getInfo('网站[{1}]开启SSL成功!', (siteName,))
        mw.writeLog('网站管理', msg)

        mw.restartWeb()
        return mw.returnData(True, 'SSL开启成功!')

    def saveCert(self, keyPath, certPath):
        try:
            certInfo = mw.getCertName(certPath)
            if not certInfo:
                return mw.returnData(False, '证书解析失败!')
            vpath = self.sslDir + '/' + certInfo['subject'].strip()
            if not os.path.exists(vpath):
                os.system('mkdir -p ' + vpath)
            mw.writeFile(vpath + '/privkey.pem', mw.readFile(keyPath))
            mw.writeFile(vpath + '/fullchain.pem', mw.readFile(certPath))
            mw.writeFile(vpath + '/info.json', json.dumps(certInfo))
            return mw.returnData(True, '证书保存成功!')
        except Exception as e:
            return mw.returnData(False, '证书保存失败!')

    # 清除多余user.ini
    def delUserInI(self, path, up=0):
        for p1 in os.listdir(path):
            try:
                npath = path + '/' + p1
                if os.path.isdir(npath):
                    if up < 100:
                        self.delUserInI(npath, up + 1)
                else:
                    continue
                useriniPath = npath + '/.user.ini'
                if not os.path.exists(useriniPath):
                    continue
                mw.execShell('which chattr && chattr -i ' + useriniPath)
                mw.execShell('rm -f ' + useriniPath)
            except:
                continue
        return True

    # 设置目录防御
    def setDirUserINI(self, sitePath, runPath):
        newPath = sitePath + runPath

        filename = newPath + '/.user.ini'
        if os.path.exists(filename):
            mw.execShell("chattr -i " + filename)
            os.remove(filename)
            return mw.returnJson(True, '已清除防跨站设置!')

        self.delUserInI(newPath)
        openPath = 'open_basedir={}/:{}/'.format(newPath, sitePath)
        if runPath == '/':
            openPath = 'open_basedir={}/'.format(sitePath)

        mw.writeFile(filename, openPath + ':/www/server/php:/tmp/:/proc/')
        mw.execShell("chattr +i " + filename)

        return mw.returnJson(True, '已打开防跨站设置!')
# ssl相关方法 end
