# coding: utf-8

import psutil
import time
import os
import sys
import public
import re
import json
import pwd

from flask import session
from flask import request


class config_api:

    # 本版解决自启动问题
    # openresty 自启动 done
    # php 自启动 done
    # mysql 自启动 done
    __version = '0.5.2'

    def __init__(self):
        pass

    ##### ----- start ----- ###

    # 取面板列表
    def getPanelListApi(self):
        data = public.M('panel').field(
            'id,title,url,username,password,click,addtime').order('click desc').select()
        return public.getJson(data)

    def addPanelInfoApi(self):
        title = request.form.get('title', '')
        url = request.form.get('url', '')
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        # 校验是还是重复
        isAdd = public.M('panel').where(
            'title=? OR url=?', (title, url)).count()
        if isAdd:
            return public.returnJson(False, '备注或面板地址重复!')
        isRe = public.M('panel').add('title,url,username,password,click,addtime',
                                     (title, url, username, password, 0, int(time.time())))
        if isRe:
            return public.returnJson(True, '添加成功!')
        return public.returnJson(False, '添加失败!')

    # 删除面板资料
    def delPanelInfoApi(self):
        mid = request.form.get('id', '')
        isExists = public.M('panel').where('id=?', (mid,)).count()
        if not isExists:
            return public.returnJson(False, '指定面板资料不存在!')
        public.M('panel').where('id=?', (mid,)).delete()
        return public.returnJson(True, '删除成功!')

     # 修改面板资料
    def setPanelInfoApi(self):
        title = request.form.get('title', '')
        url = request.form.get('url', '')
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        mid = request.form.get('id', '')
        # 校验是还是重复
        isSave = public.M('panel').where(
            '(title=? OR url=?) AND id!=?', (title, url, mid)).count()
        if isSave:
            return public.returnJson(False, '备注或面板地址重复!')

        # 更新到数据库
        isRe = public.M('panel').where('id=?', (mid,)).save(
            'title,url,username,password', (title, url, username, password))
        if isRe:
            return public.returnJson(True, '修改成功!')
        return public.returnJson(False, '修改失败!')

    def syncDateApi(self):
        if public.isAppleSystem():
            return public.returnJson(True, '开发系统不必同步时间!')

        data = public.execShell('ntpdate -s time.nist.gov')
        if data[0] == '':
            return public.returnJson(True, '同步成功!')
        return public.returnJson(False, '同步失败:' + data[0])

    def setPasswordApi(self):
        password1 = request.form.get('password1', '')
        password2 = request.form.get('password2', '')
        if password1 != password2:
            return public.returnJson(False, '两次输入的密码不一致，请重新输入!')
        if len(password1) < 5:
            return public.returnJson(False, '用户密码不能小于5位!')
        public.M('users').where("username=?", (session['username'],)).setField(
            'password', public.md5(password1.strip()))
        return public.returnJson(True, '密码修改成功!')

    def setNameApi(self):
        name1 = request.form.get('name1', '')
        name2 = request.form.get('name2', '')
        if name1 != name2:
            return public.returnJson(False, '两次输入的用户名不一致，请重新输入!')
        if len(name1) < 3:
            return public.returnJson(False, '用户名长度不能少于3位')

        public.M('users').where("username=?", (session['username'],)).setField(
            'username', name1.strip())

        session['username'] = name1
        return public.returnJson(True, '用户修改成功!')

    def setApi(self):
        webname = request.form.get('webname', '')
        port = request.form.get('port', '')
        host_ip = request.form.get('host_ip', '')
        domain = request.form.get('domain', '')
        sites_path = request.form.get('sites_path', '')
        backup_path = request.form.get('backup_path', '')

        if domain != '':
            reg = "^([\w\-\*]{1,100}\.){1,4}(\w{1,10}|\w{1,10}\.\w{1,10})$"
            if not re.match(reg, domain):
                return public.returnJson(False, '主域名格式不正确')

        if int(port) >= 65535 or int(port) < 100:
            return public.returnJson(False, '端口范围不正确!')

        if webname != public.getConfig('title'):
            public.setConfig('title', webname)

        if sites_path != public.getWwwDir():
            public.setWwwDir(sites_path)

        if backup_path != public.getWwwDir():
            public.setBackupDir(backup_path)

        if port != public.getHostPort():
            import system_api
            public.setHostPort(port)
            system_api.system_api().restartMw()

        if host_ip != public.getHostAddr():
            public.setHostAddr(host_ip)

        mhost = public.getHostAddr()
        info = {
            'uri': '/config',
            'host': mhost + ':' + port
        }
        return public.returnJson(True, '保存成功!', info)

    def setAdminPathApi(self):
        admin_path = request.form.get('admin_path', '').strip()
        admin_path_checks = ['/', '/close', '/login', '/do_login', '/site',
                             '/sites', '/download_file', '/control', '/crontab',
                             '/firewall', '/files', 'config', '/soft', '/system',
                             '/code', '/ssl', '/plugins']
        if admin_path == '':
            admin_path = '/'
        if admin_path != '/':
            if len(admin_path) < 6:
                return public.returnJson(False, '安全入口地址长度不能小于6位!')
            if admin_path in admin_path_checks:
                return public.returnJson(False, '该入口已被面板占用,请使用其它入口!')
            if not re.match("^/[\w\./-_]+$", admin_path):
                return public.returnJson(False, '入口地址格式不正确,示例: /my_panel')
        else:
            domain = public.readFile('data/domain.conf')
            if not domain:
                domain = ''
            limitip = public.readFile('data/limitip.conf')
            if not limitip:
                limitip = ''
            if not domain.strip() and not limitip.strip():
                return public.returnJson(False, '警告，关闭安全入口等于直接暴露你的后台地址在外网，十分危险，至少开启以下一种安全方式才能关闭：<a style="color:red;"><br>1、绑定访问域名<br>2、绑定授权IP</a>')

        admin_path_file = 'data/admin_path.pl'
        admin_path_old = '/'
        if os.path.exists(admin_path_file):
            admin_path_old = public.readFile(admin_path_file).strip()

        if admin_path_old != admin_path:
            public.writeFile(admin_path_file, admin_path)
            public.restartMw()
        return public.returnJson(True, '修改成功!')

    def closePanelApi(self):
        filename = 'data/close.pl'
        if os.path.exists(filename):
            os.remove(filename)
            return public.returnJson(True, '开启成功')
        public.writeFile(filename, 'True')
        public.execShell("chmod 600 " + filename)
        public.execShell("chown root.root " + filename)
        return public.returnJson(True, '面板已关闭!')

    def setIpv6StatusApi(self):
        ipv6_file = 'data/ipv6.pl'
        if os.path.exists('data/ipv6.pl'):
            os.remove(ipv6_file)
            public.writeLog('面板设置', '关闭面板IPv6兼容!')
        else:
            public.writeFile(ipv6_file, 'True')
            public.writeLog('面板设置', '开启面板IPv6兼容!')
        public.restartMw()
        return public.returnJson(True, '设置成功!')

    # 获取面板证书
    def getPanelSslApi(self):
        cert = {}
        cert['privateKey'] = public.readFile('ssl/privateKey.pem')
        cert['certPem'] = public.readFile('ssl/certificate.pem')
        cert['rep'] = os.path.exists('ssl/input.pl')
        return public.getJson(cert)

    # 保存面板证书
    def savePanelSslApi(self):
        keyPath = 'ssl/privateKey.pem'
        certPath = 'ssl/certificate.pem'
        checkCert = '/tmp/cert.pl'

        certPem = request.form.get('certPem', '').strip()
        privateKey = request.form.get('privateKey', '').strip()

        public.writeFile(checkCert, certPem)
        if privateKey:
            public.writeFile(keyPath, privateKey)
        if certPem:
            public.writeFile(certPath, certPem)
        if not public.checkCert(checkCert):
            return public.returnJson(False, '证书错误,请检查!')
        public.writeFile('ssl/input.pl', 'True')
        return public.returnJson(True, '证书已保存!')

     # 设置面板SSL
    def setPanelSslApi(self):
        sslConf = public.getRunDir() + '/data/ssl.pl'
        if os.path.exists(sslConf):
            os.system('rm -f ' + sslConf)
            return public.returnJson(True, 'SSL已关闭，请使用http协议访问面板!')
        else:
            os.system('pip install cffi==1.10')
            os.system('pip install cryptography==2.1')
            os.system('pip install pyOpenSSL==16.2')
            try:
                if not self.createSSL():
                    return public.returnJson(False, '开启失败，无法自动安装pyOpenSSL组件!<p>请尝试手动安装: pip install pyOpenSSL</p>')
                public.writeFile(sslConf, 'True')
            except Exception as ex:
                return public.returnJson(False, '开启失败，无法自动安装pyOpenSSL组件!<p>请尝试手动安装: pip install pyOpenSSL</p>')
            return public.returnJson(True, '开启成功，请使用https协议访问面板!')

    def getApi(self):
        data = {}
        return public.getJson(data)
    ##### ----- end ----- ###

    # 自签证书
    def createSSL(self):
        if os.path.exists('ssl/input.pl'):
            return True
        import OpenSSL
        key = OpenSSL.crypto.PKey()
        key.generate_key(OpenSSL.crypto.TYPE_RSA, 2048)
        cert = OpenSSL.crypto.X509()
        cert.set_serial_number(0)
        cert.get_subject().CN = '120.27.27.98'
        cert.set_issuer(cert.get_subject())
        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter(86400 * 3650)
        cert.set_pubkey(key)
        cert.sign(key, 'md5')
        cert_ca = OpenSSL.crypto.dump_certificate(
            OpenSSL.crypto.FILETYPE_PEM, cert)
        private_key = OpenSSL.crypto.dump_privatekey(
            OpenSSL.crypto.FILETYPE_PEM, key)
        if len(cert_ca) > 100 and len(private_key) > 100:
            public.writeFile('ssl/certificate.pem', cert_ca)
            public.writeFile('ssl/privateKey.pem', private_key)
            print cert_ca, private_key
            return True
        return False

    def getVersion(self):
        return self.__version

    def get(self):

        data = {}
        data['title'] = public.getConfig('title')
        data['site_path'] = public.getWwwDir()
        data['backup_path'] = public.getBackupDir()
        sformat = 'date +"%Y-%m-%d %H:%M:%S %Z %z"'
        data['systemdate'] = public.execShell(sformat)[0].strip()

        data['port'] = public.getHostPort()
        data['ip'] = public.getHostAddr()

        admin_path_file = 'data/admin_path.pl'
        if not os.path.exists(admin_path_file):
            data['admin_path'] = '/'
        else:
            data['admin_path'] = public.readFile(admin_path_file)

        ipv6_file = 'data/ipv6.pl'
        if os.path.exists('data/ipv6.pl'):
            data['ipv6'] = 'checked'
        else:
            data['ipv6'] = ''

        ssl_file = 'data/ssl.pl'
        if os.path.exists('data/ssl.pl'):
            data['ssl'] = 'checked'
        else:
            data['ssl'] = ''

        data['site_count'] = public.M('sites').count()

        data['username'] = public.M('users').where(
            "id=?", (1,)).getField('username')

        return data
