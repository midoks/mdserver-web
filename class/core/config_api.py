# coding: utf-8

import psutil
import time
import os
import sys
import mw
import re
import json
import pwd

from flask import session
from flask import request


class config_api:

    __version = '0.10.2'

    def __init__(self):
        pass

    ##### ----- start ----- ###

    # 取面板列表
    def getPanelListApi(self):
        data = mw.M('panel').field(
            'id,title,url,username,password,click,addtime').order('click desc').select()
        return mw.getJson(data)

    def addPanelInfoApi(self):
        title = request.form.get('title', '')
        url = request.form.get('url', '')
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        # 校验是还是重复
        isAdd = mw.M('panel').where(
            'title=? OR url=?', (title, url)).count()
        if isAdd:
            return mw.returnJson(False, '备注或面板地址重复!')
        isRe = mw.M('panel').add('title,url,username,password,click,addtime',
                                 (title, url, username, password, 0, int(time.time())))
        if isRe:
            return mw.returnJson(True, '添加成功!')
        return mw.returnJson(False, '添加失败!')

    # 删除面板资料
    def delPanelInfoApi(self):
        mid = request.form.get('id', '')
        isExists = mw.M('panel').where('id=?', (mid,)).count()
        if not isExists:
            return mw.returnJson(False, '指定面板资料不存在!')
        mw.M('panel').where('id=?', (mid,)).delete()
        return mw.returnJson(True, '删除成功!')

     # 修改面板资料
    def setPanelInfoApi(self):
        title = request.form.get('title', '')
        url = request.form.get('url', '')
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        mid = request.form.get('id', '')
        # 校验是还是重复
        isSave = mw.M('panel').where(
            '(title=? OR url=?) AND id!=?', (title, url, mid)).count()
        if isSave:
            return mw.returnJson(False, '备注或面板地址重复!')

        # 更新到数据库
        isRe = mw.M('panel').where('id=?', (mid,)).save(
            'title,url,username,password', (title, url, username, password))
        if isRe:
            return mw.returnJson(True, '修改成功!')
        return mw.returnJson(False, '修改失败!')

    def syncDateApi(self):
        if mw.isAppleSystem():
            return mw.returnJson(True, '开发系统不必同步时间!')

        data = mw.execShell('ntpdate -s time.nist.gov')
        if data[0] == '':
            return mw.returnJson(True, '同步成功!')
        return mw.returnJson(False, '同步失败:' + data[0])

    def setPasswordApi(self):
        password1 = request.form.get('password1', '')
        password2 = request.form.get('password2', '')
        if password1 != password2:
            return mw.returnJson(False, '两次输入的密码不一致，请重新输入!')
        if len(password1) < 5:
            return mw.returnJson(False, '用户密码不能小于5位!')
        mw.M('users').where("username=?", (session['username'],)).setField(
            'password', mw.md5(password1.strip()))
        return mw.returnJson(True, '密码修改成功!')

    def setNameApi(self):
        name1 = request.form.get('name1', '')
        name2 = request.form.get('name2', '')
        if name1 != name2:
            return mw.returnJson(False, '两次输入的用户名不一致，请重新输入!')
        if len(name1) < 3:
            return mw.returnJson(False, '用户名长度不能少于3位')

        mw.M('users').where("username=?", (session['username'],)).setField(
            'username', name1.strip())

        session['username'] = name1
        return mw.returnJson(True, '用户修改成功!')

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
                return mw.returnJson(False, '主域名格式不正确')

        if int(port) >= 65535 or int(port) < 100:
            return mw.returnJson(False, '端口范围不正确!')

        if webname != mw.getConfig('title'):
            mw.setConfig('title', webname)

        if sites_path != mw.getWwwDir():
            mw.setWwwDir(sites_path)

        if backup_path != mw.getWwwDir():
            mw.setBackupDir(backup_path)

        if port != mw.getHostPort():
            import system_api
            import firewall_api

            if os.path.exists("/lib/systemd/system/firewalld.service"):
                if not firewall_api.firewall_api().getFwStatus():
                    return mw.returnJson(False, 'firewalld必须先启动!')

            mw.setHostPort(port)

            msg = mw.getInfo('放行端口[{1}]成功', (port,))
            mw.writeLog("防火墙管理", msg)
            addtime = time.strftime('%Y-%m-%d %X', time.localtime())
            mw.M('firewall').add('port,ps,addtime', (port, "配置修改", addtime))

            firewall_api.firewall_api().addAcceptPort(port)
            firewall_api.firewall_api().firewallReload()

            system_api.system_api().restartMw()

        if host_ip != mw.getHostAddr():
            mw.setHostAddr(host_ip)

        mhost = mw.getHostAddr()
        info = {
            'uri': '/config',
            'host': mhost + ':' + port
        }
        return mw.returnJson(True, '保存成功!', info)

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
                return mw.returnJson(False, '安全入口地址长度不能小于6位!')
            if admin_path in admin_path_checks:
                return mw.returnJson(False, '该入口已被面板占用,请使用其它入口!')
            if not re.match("^/[\w\./-_]+$", admin_path):
                return mw.returnJson(False, '入口地址格式不正确,示例: /my_panel')
        else:
            domain = mw.readFile('data/domain.conf')
            if not domain:
                domain = ''
            limitip = mw.readFile('data/limitip.conf')
            if not limitip:
                limitip = ''
            if not domain.strip() and not limitip.strip():
                return mw.returnJson(False, '警告，关闭安全入口等于直接暴露你的后台地址在外网，十分危险，至少开启以下一种安全方式才能关闭：<a style="color:red;"><br>1、绑定访问域名<br>2、绑定授权IP</a>')

        admin_path_file = 'data/admin_path.pl'
        admin_path_old = '/'
        if os.path.exists(admin_path_file):
            admin_path_old = mw.readFile(admin_path_file).strip()

        if admin_path_old != admin_path:
            mw.writeFile(admin_path_file, admin_path)
            mw.restartMw()
        return mw.returnJson(True, '修改成功!')

    def closePanelApi(self):
        filename = 'data/close.pl'
        if os.path.exists(filename):
            os.remove(filename)
            return mw.returnJson(True, '开启成功')
        mw.writeFile(filename, 'True')
        mw.execShell("chmod 600 " + filename)
        mw.execShell("chown root.root " + filename)
        return mw.returnJson(True, '面板已关闭!')

    def openDebugApi(self):
        filename = 'data/debug.pl'
        if os.path.exists(filename):
            os.remove(filename)
            return mw.returnJson(True, '开发模式关闭!')
        mw.writeFile(filename, 'True')
        return mw.returnJson(True, '开发模式开启!')

    def setIpv6StatusApi(self):
        ipv6_file = 'data/ipv6.pl'
        if os.path.exists('data/ipv6.pl'):
            os.remove(ipv6_file)
            mw.writeLog('面板设置', '关闭面板IPv6兼容!')
        else:
            mw.writeFile(ipv6_file, 'True')
            mw.writeLog('面板设置', '开启面板IPv6兼容!')
        mw.restartMw()
        return mw.returnJson(True, '设置成功!')

    # 获取面板证书
    def getPanelSslApi(self):
        cert = {}
        cert['privateKey'] = mw.readFile('ssl/privateKey.pem')
        cert['certPem'] = mw.readFile('ssl/certificate.pem')
        cert['rep'] = os.path.exists('ssl/input.pl')
        return mw.getJson(cert)

    # 保存面板证书
    def savePanelSslApi(self):
        keyPath = 'ssl/privateKey.pem'
        certPath = 'ssl/certificate.pem'
        checkCert = '/tmp/cert.pl'

        certPem = request.form.get('certPem', '').strip()
        privateKey = request.form.get('privateKey', '').strip()

        mw.writeFile(checkCert, certPem)
        if privateKey:
            mw.writeFile(keyPath, privateKey)
        if certPem:
            mw.writeFile(certPath, certPem)
        if not mw.checkCert(checkCert):
            return mw.returnJson(False, '证书错误,请检查!')
        mw.writeFile('ssl/input.pl', 'True')
        return mw.returnJson(True, '证书已保存!')

     # 设置面板SSL
    def setPanelSslApi(self):
        sslConf = mw.getRunDir() + '/data/ssl.pl'
        if os.path.exists(sslConf):
            os.system('rm -f ' + sslConf)
            return mw.returnJson(True, 'SSL已关闭，请使用http协议访问面板!')
        else:
            os.system('pip install cffi==1.10')
            os.system('pip install cryptography==2.1')
            os.system('pip install pyOpenSSL==16.2')
            try:
                if not self.createSSL():
                    return mw.returnJson(False, '开启失败，无法自动安装pyOpenSSL组件!<p>请尝试手动安装: pip install pyOpenSSL</p>')
                mw.writeFile(sslConf, 'True')
            except Exception as ex:
                return mw.returnJson(False, '开启失败，无法自动安装pyOpenSSL组件!<p>请尝试手动安装: pip install pyOpenSSL</p>')
            return mw.returnJson(True, '开启成功，请使用https协议访问面板!')

    def getApi(self):
        data = {}
        return mw.getJson(data)
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
        cert.get_subject().CN = mw.getLocalIp()
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
            mw.writeFile('ssl/certificate.pem', cert_ca)
            mw.writeFile('ssl/privateKey.pem', private_key)
            print(cert_ca, private_key)
            return True
        return False

    def getVersion(self):
        return self.__version

    def get(self):

        data = {}
        data['title'] = mw.getConfig('title')
        data['site_path'] = mw.getWwwDir()
        data['backup_path'] = mw.getBackupDir()
        sformat = 'date +"%Y-%m-%d %H:%M:%S %Z %z"'
        data['systemdate'] = mw.execShell(sformat)[0].strip()

        data['port'] = mw.getHostPort()
        data['ip'] = mw.getHostAddr()

        admin_path_file = 'data/admin_path.pl'
        if not os.path.exists(admin_path_file):
            data['admin_path'] = '/'
        else:
            data['admin_path'] = mw.readFile(admin_path_file)

        ipv6_file = 'data/ipv6.pl'
        if os.path.exists(ipv6_file):
            data['ipv6'] = 'checked'
        else:
            data['ipv6'] = ''

        debug_file = 'data/debug.pl'
        if os.path.exists(debug_file):
            data['debug'] = 'checked'
        else:
            data['debug'] = ''

        ssl_file = 'data/ssl.pl'
        if os.path.exists('data/ssl.pl'):
            data['ssl'] = 'checked'
        else:
            data['ssl'] = ''

        data['site_count'] = mw.M('sites').count()

        data['username'] = mw.M('users').where(
            "id=?", (1,)).getField('username')

        return data
