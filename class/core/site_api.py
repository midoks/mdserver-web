# coding: utf-8

import time
import os
import sys
import mw
import re
import json
import pwd
import shutil

import psutil

from flask import request

# request.urllib3.disable_warnings()


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
    sslDir = None  # ssl目录

    def __init__(self):
        # nginx conf
        self.setupPath = mw.getServerDir() + '/web_conf'
        self.vhostPath = vh = self.setupPath + '/nginx/vhost'
        if not os.path.exists(vh):
            mw.execShell("mkdir -p " + vh + " && chmod -R 755 " + vh)
        self.rewritePath = rw = self.setupPath + '/nginx/rewrite'
        if not os.path.exists(rw):
            mw.execShell("mkdir -p " + rw + " && chmod -R 755 " + rw)
        self.passPath = self.setupPath + '/nginx/pass'
        # if not os.path.exists(pp):
        #     mw.execShell("mkdir -p " + rw + " && chmod -R 755 " + rw)

        self.logsPath = mw.getRootDir() + '/wwwlogs'
        # ssl conf
        if mw.isAppleSystem():
            self.sslDir = self.setupPath + '/letsencrypt/'
        else:
            self.sslDir = '/etc/letsencrypt/live/'

    ##### ----- start ----- ###
    def listApi(self):
        limit = request.form.get('limit', '10')
        p = request.form.get('p', '1')
        type_id = request.form.get('type_id', '')

        start = (int(p) - 1) * (int(limit))

        siteM = mw.M('sites')
        if type_id != '' and type_id == '-1' and type_id == '0':
            siteM.where('type_id=?', (type_id))

        _list = siteM.field('id,name,path,status,ps,addtime,edate').limit(
            (str(start)) + ',' + limit).order('id desc').select()

        for i in range(len(_list)):
            _list[i]['backup_count'] = mw.M('backup').where(
                "pid=? AND type=?", (_list[i]['id'], 0)).count()

        _ret = {}
        _ret['data'] = _list

        count = siteM.count()
        _page = {}
        _page['count'] = count
        _page['tojs'] = 'getWeb'
        _page['p'] = p
        _page['row'] = limit

        _ret['page'] = mw.getPage(_page)
        return mw.getJson(_ret)

    def setDefaultSiteApi(self):
        name = request.form.get('name', '')
        import time
        # 清理旧的
        defaultSite = mw.readFile('data/defaultSite.pl')
        if defaultSite:
            path = self.getHostConf(defaultSite)
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

        mw.writeFile('data/defaultSite.pl', name)
        mw.restartWeb()
        return mw.returnJson(True, '设置成功!')

    def getDefaultSiteApi(self):
        data = {}
        data['sites'] = mw.M('sites').field(
            'name').order('id desc').select()
        data['defaultSite'] = mw.readFile('data/defaultSite.pl')
        return mw.getJson(data)

    def setPsApi(self):
        mid = request.form.get('id', '')
        ps = request.form.get('ps', '')
        if mw.M('sites').where("id=?", (mid,)).setField('ps', ps):
            return mw.returnJson(True, '修改成功!')
        return mw.returnJson(False, '修改失败!')

    def stopApi(self):
        mid = request.form.get('id', '')
        name = request.form.get('name', '')
        path = self.setupPath + '/stop'

        if not os.path.exists(path):
            os.makedirs(path)
            mw.writeFile(path + '/index.html',
                         'The website has been closed!!!')

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
        return self.getPhpVersion()

    def setPhpVersionApi(self):
        siteName = request.form.get('siteName', '')
        version = request.form.get('version', '')

        # nginx
        file = self.getHostConf(siteName)
        conf = mw.readFile(file)
        if conf:
            rep = "enable-php-([0-9]{2,3})\.conf"
            tmp = re.search(rep, conf).group()
            conf = conf.replace(tmp, 'enable-php-' + version + '.conf')
            mw.writeFile(file, conf)

        mw.restartWeb()
        msg = mw.getInfo('成功切换网站[{1}]的PHP版本为PHP-{2}', (siteName, version))
        mw.writeLog("网站管理", msg)
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
        if data['email'] == '287962566@qq.com':
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
        data['userini'] = False
        if os.path.exists(path + '/.user.ini'):
            data['userini'] = True
        data['runPath'] = self.getSiteRunPath(mid)
        data['pass'] = self.getHasPwd(name)
        data['path'] = path
        data['name'] = name
        return mw.returnJson(True, 'OK', data)

    def setDirUserIniApi(self):
        path = request.form.get('path', '')
        filename = path + '/.user.ini'
        self.delUserInI(path)
        if os.path.exists(filename):
            mw.execShell("which chattr && chattr -i " + filename)
            os.remove(filename)
            return mw.returnJson(True, '已清除防跨站设置!')
        mw.writeFile(filename, 'open_basedir=' + path +
                     '/:/www/server/php:/tmp/:/proc/')
        mw.execShell("which chattr && chattr +i " + filename)
        return mw.returnJson(True, '已打开防跨站设置!')

    def logsOpenApi(self):
        mid = request.form.get('id', '')
        name = mw.M('sites').where("id=?", (mid,)).getField('name')

        # NGINX
        filename = self.getHostConf(name)
        if os.path.exists(filename):
            conf = mw.readFile(filename)
            rep = self.logsPath + "/" + name + ".log"
            if conf.find(rep) != -1:
                conf = conf.replace(rep, "off")
            else:
                conf = conf.replace('access_log  off', 'access_log  ' + rep)
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

    def getSslApi(self):
        siteName = request.form.get('siteName', '')

        path = self.sslDir + siteName
        csrpath = path + "/fullchain.pem"  # 生成证书路径
        keypath = path + "/privkey.pem"  # 密钥文件路径
        key = mw.readFile(keypath)
        csr = mw.readFile(csrpath)

        file = self.getHostConf(siteName)
        conf = mw.readFile(file)

        keyText = 'ssl_certificate'
        status = True
        stype = 0
        if(conf.find(keyText) == -1):
            status = False
            stype = -1

        toHttps = self.isToHttps(siteName)
        id = mw.M('sites').where("name=?", (siteName,)).getField('id')
        domains = mw.M('domain').where(
            "pid=?", (id,)).field('name').select()
        data = {'status': status, 'domain': domains, 'key': key,
                'csr': csr, 'type': stype, 'httpTohttps': toHttps}
        return mw.returnJson(True, 'OK', data)

    def setSslApi(self):
        siteName = request.form.get('siteName', '')
        key = request.form.get('key', '')
        csr = request.form.get('csr', '')

        path = self.sslDir + siteName
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

        mw.execShell('\\cp -a ' + keypath + ' /tmp/backup1.conf')
        mw.execShell('\\cp -a ' + csrpath + ' /tmp/backup2.conf')

        # 清理旧的证书链
        if os.path.exists(path + '/README'):
            mw.execShell('rm -rf ' + path)
            mw.execShell('rm -rf ' + path + '-00*')
            mw.execShell('rm -rf /etc/letsencrypt/archive/' + siteName)
            mw.execShell(
                'rm -rf /etc/letsencrypt/archive/' + siteName + '-00*')
            mw.execShell(
                'rm -f /etc/letsencrypt/renewal/' + siteName + '.conf')
            mw.execShell('rm -rf /etc/letsencrypt/renewal/' +
                         siteName + '-00*.conf')
            mw.execShell('rm -rf ' + path + '/README')
            mw.execShell('mkdir -p ' + path)

        mw.writeFile(keypath, key)
        mw.writeFile(csrpath, csr)

        # 写入配置文件
        result = self.setSslConf(siteName)
        # print result['msg']
        if not result['status']:
            return mw.getJson(result)

        isError = mw.checkWebConfig()
        if(type(isError) == str):
            mw.execShell('\\cp -a /tmp/backup1.conf ' + keypath)
            mw.execShell('\\cp -a /tmp/backup2.conf ' + csrpath)
            return mw.returnJson(False, 'ERROR: <br><a style="color:red;">' + isError.replace("\n", '<br>') + '</a>')

        mw.restartWeb()
        mw.writeLog('网站管理', '证书已保存!')
        return mw.returnJson(True, '证书已保存!')

    def setCertToSiteApi(self):
        certName = request.form.get('certName', '')
        siteName = request.form.get('siteName', '')
        try:
            path = self.sslDir + siteName
            if not os.path.exists(path):
                return mw.returnJson(False, '证书不存在!')

            result = self.setSslConf(siteName)
            if not result['status']:
                return mw.getJson(result)

            mw.restartWeb()
            mw.writeLog('网站管理', '证书已部署!')
            return mw.returnJson(True, '证书已部署!')
        except Exception as ex:
            return mw.returnJson(False, '设置错误,' + str(ex))

    def removeCertApi(self):
        certName = request.form.get('certName', '')
        try:
            path = self.sslDir + certName
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
            mw.writeFile(file, conf)

        msg = mw.getInfo('网站[{1}]关闭SSL成功!', (siteName,))
        mw.writeLog('网站管理', msg)
        mw.restartWeb()
        return mw.returnJson(True, 'SSL已关闭!')

    def createLetApi(self):
        siteName = request.form.get('siteName', '')
        updateOf = request.form.get('updateOf', '')
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
            if siteConf.find('301-START') != -1:
                return mw.returnJson(False, '检测到您的站点做了301重定向设置，请先关闭重定向!')

        letpath = self.sslDir + siteName
        csrpath = letpath + "/fullchain.pem"  # 生成证书路径
        keypath = letpath + "/privkey.pem"  # 密钥文件路径

        actionstr = updateOf
        siteInfo = mw.M('sites').where(
            'name=?', (siteName,)).field('id,name,path').find()
        path = self.getSitePath(siteName)
        srcPath = siteInfo['path']

        # 检测acem是否安装
        if mw.isAppleSystem():
            user = mw.execShell(
                "who | sed -n '2, 1p' |awk '{print $1}'")[0].strip()
            acem = '/Users/' + user + '/.acme.sh/acme.sh'
        else:
            acem = '/root/.acme.sh/acme.sh'
        if not os.path.exists(acem):
            acem = '/.acme.sh/acme.sh'
        if not os.path.exists(acem):
            try:
                mw.execShell("curl -sS curl https://get.acme.sh | sh")
            except:
                return mw.returnJson(False, '尝试自动安装ACME失败,请通过以下命令尝试手动安装<p>安装命令: curl https://get.acme.sh | sh</p>' + acem)
        if not os.path.exists(acem):
            return mw.returnJson(False, '尝试自动安装ACME失败,请通过以下命令尝试手动安装<p>安装命令: curl https://get.acme.sh | sh</p>' + acem)

        # 避免频繁执行
        checkAcmeRun = mw.execShell('ps -ef|grep acme.sh |grep -v grep')
        if checkAcmeRun[0] != '':
            return mw.returnJson(False, '正在申请或更新SSL中...')

        if force == 'true':
            force_bool = True

        if renew == 'true':
            execStr = acem + " --renew --yes-I-know-dns-manual-mode-enough-go-ahead-please"
        else:
            execStr = acem + " --issue --force"

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

        home_path = '/root/.acme.sh/' + domains[0]
        home_cert = home_path + '/fullchain.cer'
        home_key = home_path + '/' + domains[0] + '.key'

        if not os.path.exists(home_cert):
            home_path = '/.acme.sh/' + domains[0]
            home_cert = home_path + '/fullchain.cer'
            home_key = home_path + '/' + domains[0] + '.key'

        if mw.isAppleSystem():
            user = mw.execShell(
                "who | sed -n '2, 1p' |awk '{print $1}'")[0].strip()
            acem = '/Users/' + user + '/.acme.sh/'
            if not os.path.exists(home_cert):
                home_path = acem + domains[0]
                home_cert = home_path + '/fullchain.cer'
                home_key = home_path + '/' + domains[0] + '.key'

        # print home_cert
        cmd = 'export ACCOUNT_EMAIL=' + email + ' && ' + execStr
        # print(domains)
        # print(cmd)
        result = mw.execShell(cmd)

        if not os.path.exists(home_cert.replace("\*", "*")):
            data = {}
            data['err'] = result
            data['out'] = result[0]
            data['msg'] = '签发失败,我们无法验证您的域名:<p>1、检查域名是否绑定到对应站点</p>\
                <p>2、检查域名是否正确解析到本服务器,或解析还未完全生效</p>\
                <p>3、如果您的站点设置了反向代理,或使用了CDN,请先将其关闭</p>\
                <p>4、如果您的站点设置了301重定向,请先将其关闭</p>\
                <p>5、如果以上检查都确认没有问题，请尝试更换DNS服务商</p>'
            data['result'] = {}
            if result[1].find('new-authz error:') != -1:
                data['result'] = json.loads(
                    re.search("{.+}", result[1]).group())
                if data['result']['status'] == 429:
                    data['msg'] = '签发失败,您尝试申请证书的失败次数已达上限!<p>1、检查域名是否绑定到对应站点</p>\
                        <p>2、检查域名是否正确解析到本服务器,或解析还未完全生效</p>\
                        <p>3、如果您的站点设置了反向代理,或使用了CDN,请先将其关闭</p>\
                        <p>4、如果您的站点设置了301重定向,请先将其关闭</p>\
                        <p>5、如果以上检查都确认没有问题，请尝试更换DNS服务商</p>'
            data['status'] = False
            return mw.getJson(data)

        if not os.path.exists(letpath):
            mw.execShell("mkdir -p " + letpath)
        mw.execShell("ln -sf \"" + home_cert + "\" \"" + csrpath + '"')
        mw.execShell("ln -sf \"" + home_key + "\" \"" + keypath + '"')
        mw.execShell('echo "let" > "' + letpath + '/README"')
        if(actionstr == '2'):
            return mw.returnJson(True, '证书已更新!')

        # 写入配置文件
        result = self.setSslConf(siteName)
        if not result['status']:
            return mw.getJson(result)
        result['csr'] = mw.readFile(csrpath)
        result['key'] = mw.readFile(keypath)
        mw.restartWeb()

        return mw.returnJson(True, 'OK', result)

    def httpToHttpsApi(self):
        siteName = request.form.get('siteName', '')
        file = self.getHostConf(siteName)
        conf = mw.readFile(file)
        if conf:
            # if conf.find('ssl_certificate') == -1:
            #     return mw.returnJson(False, '当前未开启SSL')
            to = """#error_page 404/404.html;
    # HTTP_TO_HTTPS_START
    if ($server_port !~ 443){
        rewrite ^(/.*)$ https://$host$1 permanent;
    }
    # HTTP_TO_HTTPS_END"""
            conf = conf.replace('#error_page 404/404.html;', to)
            mw.writeFile(file, conf)

        mw.restartWeb()
        return mw.returnJson(True, '设置成功!证书也要设置好哟!')

    def closeToHttpsApi(self):
        siteName = request.form.get('siteName', '')
        file = self.getHostConf(siteName)
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
        sid = request.form.get('id', '')
        return self.setSecurity(sid, name, fix, domains, status)

    def getLogsApi(self):
        siteName = request.form.get('siteName', '')
        return self.getLogs(siteName)

    def getSitePhpVersionApi(self):
        siteName = request.form.get('siteName', '')
        return self.getSitePhpVersion(siteName)

    def getHostConfApi(self):
        siteName = request.form.get('siteName', '')
        host = self.getHostConf(siteName)
        return mw.getJson({'host': host})

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

    def addDomainApi(self):
        isError = mw.checkWebConfig()
        if isError != True:
            return mw.returnJson(False, 'ERROR: 检测到配置文件有错误,请先排除后再操作<br><br><a style="color:red;">' + isError.replace("\n", '<br>') + '</a>')

        domain = request.form.get('domain', '')
        webname = request.form.get('webname', '')
        pid = request.form.get('id', '')
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
                "name=? AND (port=? OR pid=?)", (domain, domain_port, pid)).getField('pid')
            if opid:
                if mw.M('sites').where('id=?', (opid,)).count():
                    return mw.returnJson(False, '指定域名已绑定过!')
                mw.M('domain').where('pid=?', (opid,)).delete()

            if mw.M('binding').where('domain=?', (domain,)).count():
                return mw.returnJson(False, '您添加的域名已存在!')

            self.nginxAddDomain(webname, domain_name, domain_port)

            mw.restartWeb()
            msg = mw.getInfo('网站[{1}]添加域名[{2}]成功!', (webname, domain_name))
            mw.writeLog('网站管理', msg)
            mw.M('domain').add('pid,name,port,addtime',
                               (pid, domain_name, domain_port, mw.getDate()))

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
            content = content.replace('{$LOGPATH}', mw.getLogsDir())

            conf += "\r\n" + content
            shutil.copyfile(filename, '/tmp/backup.conf')
            mw.writeFile(filename, conf)
        conf = mw.readFile(filename)

        # 检查配置是否有误
        isError = mw.checkWebConfig()
        if isError != True:
            shutil.copyfile('/tmp/backup.conf', filename)
            return mw.returnJson(False, 'ERROR: <br><a style="color:red;">' + isError.replace("\n", '<br>') + '</a>')

        mw.M('binding').add('pid,domain,port,path,addtime',
                            (pid, domain, port, dirName, mw.getDate()))

        mw.restartWeb()
        msg = mw.getInfo('网站[{1}]子目录[{2}]绑定到[{3}]',
                         (siteInfo['name'], dirName, domain))
        mw.writeLog('网站管理', msg)
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

        self.delUserInI(sitePath)
        self.setDirUserINI(newPath)

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
        print(filename)
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
    # AUTH_START
    auth_basic "Authorization";
    auth_basic_user_file %s;
    # AUTH_END''' % (filename,)
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

    def getProxyListApi(self):
        siteName = request.form.get('siteName', '')
        conf_path = self.getHostConf(siteName)
        old_conf = mw.readFile(conf_path)
        rep = "(#PROXY-START(\n|.)+#PROXY-END)"
        url_rep = "proxy_pass (.*);|ProxyPass\s/\s(.*)|Host\s(.*);"
        host_rep = "Host\s(.*);"

        if re.search(rep, old_conf):
            # 构造代理配置
            if w == "nginx":
                get.todomain = str(re.search(host_rep, old_conf).group(1))
                get.proxysite = str(re.search(url_rep, old_conf).group(1))
            else:
                get.todomain = ""
                get.proxysite = str(re.search(url_rep, old_conf).group(2))
            get.proxyname = "旧代理"
            get.type = 1
            get.proxydir = "/"
            get.advanced = 0
            get.cachetime = 1
            get.cache = 0
            get.subfilter = "[{\"sub1\":\"\",\"sub2\":\"\"},{\"sub1\":\"\",\"sub2\":\"\"},{\"sub1\":\"\",\"sub2\":\"\"}]"

            # proxyname_md5 = self.__calc_md5(get.proxyname)
            # 备份并替换老虚拟主机配置文件
            os.system("cp %s %s_bak" % (conf_path, conf_path))
            conf = re.sub(rep, "", old_conf)
            mw.writeFile(conf_path, conf)

            # self.createProxy(get)
            mw.restartWeb()

        proxyUrl = self.__read_config(self.__proxyfile)
        sitename = sitename
        proxylist = []
        for i in proxyUrl:
            if i["sitename"] == sitename:
                proxylist.append(i)
        return mw.getJson(proxylist)

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
            path = re.search(rep, conf).groups()[0]
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
        return mw.returnJson(True, mw.getNumLines(logPath, 100))

    # 取日志状态
    def getLogsStatus(self, siteName):
        filename = self.getHostConf(siteName)
        conf = mw.readFile(filename)
        if conf.find('#ErrorLog') != -1:
            return False
        if conf.find("access_log  /dev/null") != -1:
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
        rep = "enable-php-([0-9]{2,3})\.conf"
        tmp = re.search(rep, conf).groups()
        data = {}
        data['phpversion'] = tmp[0]
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

        if type(conf) == bool:
            return mw.returnJson(False, '读取配置文件失败!')

        data = {}
        if conf.find('SECURITY-START') != -1:
            rep = "#SECURITY-START(.|\n)*#SECURITY-END"
            tmp = re.search(rep, conf).group()
            data['fix'] = re.search(
                "\(.+\)\$", tmp).group().replace('(', '').replace(')$', '').replace('|', ',')
            data['domains'] = ','.join(re.search(
                "valid_referers\s+none\s+blocked\s+(.+);\n", tmp).groups()[0].split())
            data['status'] = True
        else:
            data['fix'] = 'jpg,jpeg,gif,png,js,css'
            domains = mw.M('domain').where(
                'pid=?', (sid,)).field('name').select()
            tmp = []
            for domain in domains:
                tmp.append(domain['name'])
            data['domains'] = ','.join(tmp)
            data['status'] = False
        return mw.getJson(data)

    def setSecurity(self, sid, name, fix, domains, status):
        if len(fix) < 2:
            return mw.returnJson(False, 'URL后缀不能为空!')
        file = self.getHostConf(name)
        if os.path.exists(file):
            conf = mw.readFile(file)
            if conf.find('SECURITY-START') != -1:
                rep = "\s{0,4}#SECURITY-START(\n|.)*#SECURITY-END\n?"
                conf = re.sub(rep, '', conf)
                mw.writeLog('网站管理', '站点[' + name + ']已关闭防盗链设置!')
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
                mw.writeLog('网站管理', '站点[' + name + ']已开启防盗链!')
            mw.writeFile(file, conf)
        mw.restartWeb()
        return mw.returnJson(True, '设置成功!')

    def getPhpVersion(self):
        phpVersions = ('00', '52', '53', '54', '55',
                       '56', '70', '71', '72', '73', '74', '80', '81')
        data = []
        for val in phpVersions:
            tmp = {}
            if val == '00':
                tmp['version'] = '00'
                tmp['name'] = '纯静态'
                data.append(tmp)

            checkPath = mw.getServerDir() + '/php/' + val + '/bin/php'
            if os.path.exists(checkPath):
                tmp['version'] = val
                tmp['name'] = 'PHP-' + val
                data.append(tmp)

        return mw.getJson(data)

    # 是否跳转到https
    def isToHttps(self, siteName):
        file = self.getHostConf(siteName)
        conf = mw.readFile(file)
        if conf:
            if conf.find('HTTP_TO_HTTPS_START') != -1:
                return True
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
        if not os.path.exists(path):
            os.makedirs(path)
            if not mw.isAppleSystem():
                mw.execShell('chown -R www:www ' + path)

            mw.writeFile(path + '/index.html', '已经开始工作!!!')
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
        content = content.replace('{$PHPVER}', self.phpVersion)
        content = content.replace('{$OR_REWRITE}', self.rewritePath)

        logsPath = mw.getLogsDir()
        content = content.replace('{$LOGPATH}', logsPath)
        mw.writeFile(vhost_file, content)

        rewrite_content = '''
location /{
    if (!-e $request_filename) {
       rewrite  ^(.*)$  /index.php/$1  last;
       break;
    }
}
        '''
        rewrite_file = self.rewritePath + '/' + self.siteName + '.conf'
        mw.writeFile(rewrite_file, rewrite_content)

    def add(self, webname, port, ps, path, version):
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
        opid = mw.M('domain').where(
            "name=?", (self.siteName,)).getField('pid')
        if opid:
            if mw.M('sites').where('id=?', (opid,)).count():
                return mw.returnJson(False, '您添加的域名已存在!')
            mw.M('domain').where('pid=?', (opid,)).delete()

        # 添加更多域名
        for domain in siteMenu['domainlist']:
            sdomain = domain
            swebname = self.siteName
            spid = str(pid)
            # self.addDomain(domain, webname, pid)

        mw.M('domain').add('pid,name,port,addtime',
                           (pid, self.siteName, self.sitePort, mw.getDate()))

        self.createRootDir(self.sitePath)
        self.nginxAddConf()

        data = {}
        data['siteStatus'] = False
        mw.restartWeb()
        return mw.returnJson(True, '添加成功')

    def deleteWSLogs(self, webname):
        assLogPath = mw.getLogsDir() + '/' + webname + '.log'
        errLogPath = mw.getLogsDir() + '/' + webname + '.error.log'
        confFile = self.setupPath + '/nginx/vhost/' + webname + '.conf'
        rewriteFile = self.setupPath + '/nginx/rewrite/' + webname + '.conf'
        rewriteFile = self.setupPath + '/nginx/pass/' + webname + '.conf'
        keyPath = self.sslDir + webname + '/privkey.pem'
        certPath = self.sslDir + webname + '/fullchain.pem'
        logs = [assLogPath,
                errLogPath,
                confFile,
                rewriteFile,
                keyPath,
                certPath]
        for i in logs:
            mw.deleteFile(i)

    def delete(self, sid, webname, path):
        self.deleteWSLogs(webname)
        if path == '1':
            rootPath = mw.getWwwDir() + '/' + webname
            mw.execShell('rm -rf ' + rootPath)

        mw.M('sites').where("id=?", (sid,)).delete()
        mw.restartWeb()
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

        keyPath = self.sslDir + siteName + '/privkey.pem'
        certPath = self.sslDir + siteName + '/fullchain.pem'
        if conf:
            if conf.find('ssl_certificate') == -1:
                sslStr = """#error_page 404/404.html;
    ssl_certificate    %s;
    ssl_certificate_key  %s;
    ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:HIGH:!aNULL:!MD5:!RC4:!DHE;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    error_page 497  https://$host$request_uri;
""" % (certPath, keyPath)
            if(conf.find('ssl_certificate') != -1):
                return mw.returnData(True, 'SSL开启成功!')

            conf = conf.replace('#error_page 404/404.html;', sslStr)

            rep = "listen\s+([0-9]+)\s*[default_server]*;"
            tmp = re.findall(rep, conf)
            if not mw.inArray(tmp, '443'):
                listen = re.search(rep, conf).group()
                conf = conf.replace(
                    listen, listen + "\n\tlisten 443 ssl http2;")
            shutil.copyfile(file, '/tmp/backup.conf')

            mw.writeFile(file, conf)
            isError = mw.checkWebConfig()
            if(isError != True):
                shutil.copyfile('/tmp/backup.conf', file)
                return mw.returnData(False, '证书错误: <br><a style="color:red;">' + isError.replace("\n", '<br>') + '</a>')

        mw.restartWeb()
        self.saveCert(keyPath, certPath)

        msg = mw.getInfo('网站[{1}]开启SSL成功!', siteName)
        mw.writeLog('网站管理', msg)
        return mw.returnData(True, 'SSL开启成功!')

    def saveCert(self, keyPath, certPath):
        try:
            certInfo = self.getCertName(certPath)
            if not certInfo:
                return mw.returnData(False, '证书解析失败!')
            vpath = self.sslDir + certInfo['subject']
            if not os.path.exists(vpath):
                os.system('mkdir -p ' + vpath)
            mw.writeFile(vpath + '/privkey.pem',
                         mw.readFile(keyPath))
            mw.writeFile(vpath + '/fullchain.pem',
                         mw.readFile(certPath))
            mw.writeFile(vpath + '/info.json', json.dumps(certInfo))
            return mw.returnData(True, '证书保存成功!')
        except Exception as e:
            return mw.returnData(False, '证书保存失败!')

    # 获取证书名称
    def getCertName(self, certPath):
        try:
            openssl = '/usr/local/openssl/bin/openssl'
            if not os.path.exists(openssl):
                openssl = 'openssl'
            result = mw.execShell(
                openssl + " x509 -in " + certPath + " -noout -subject -enddate -startdate -issuer")
            tmp = result[0].split("\n")
            data = {}
            data['subject'] = tmp[0].split('=')[-1]
            data['notAfter'] = self.strfToTime(tmp[1].split('=')[1])
            data['notBefore'] = self.strfToTime(tmp[2].split('=')[1])
            data['issuer'] = tmp[3].split('O=')[-1].split(',')[0]
            if data['issuer'].find('/') != -1:
                data['issuer'] = data['issuer'].split('/')[0]
            result = mw.execShell(
                openssl + " x509 -in " + certPath + " -noout -text|grep DNS")
            data['dns'] = result[0].replace(
                'DNS:', '').replace(' ', '').strip().split(',')
            return data
        except:
            return None

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
    def setDirUserINI(self, newPath):
        filename = newPath + '/.user.ini'
        if os.path.exists(filename):
            mw.execShell("chattr -i " + filename)
            os.remove(filename)
            return mw.returnJson(True, '已清除防跨站设置!')

        self.delUserInI(newPath)
        mw.writeFile(filename, 'open_basedir=' +
                     newPath + '/:/www/server/php:/tmp/:/proc/')
        mw.execShell("chattr +i " + filename)

        return mw.returnJson(True, '已打开防跨站设置!')

    # 转换时间
    def strfToTime(self, sdate):
        import time
        return time.strftime('%Y-%m-%d', time.strptime(sdate, '%b %d %H:%M:%S %Y %Z'))
    # ssl相关方法 end
