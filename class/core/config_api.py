# coding: utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------
# 配置操作
# ---------------------------------------------------------------------------------

import psutil
import time
import os
import sys
import mw
import re
import json
import pwd
import pytz

from flask import session
from flask import request


class config_api:

    __version = '0.17.1'
    __api_addr = 'data/api.json'

    # 统一默认配置文件
    __file = {
        'api' : 'data/api.json',                                # API文件
        'debug' : 'data/debug.pl',                              # DEBUG文件
        'close' : 'data/close.pl',                              # 识别关闭面板文件
        'basic_auth' : 'data/basic_auth.json',                  # 面板Basic验证
        'admin_path' : 'data/admin_path.pl',                    # 面板后缀路径设置
        'ipv6' : 'data/ipv6.pl',                                # ipv6识别文件
        'bind_domain' : 'data/bind_domain.pl',                  # 面板域名绑定
        'unauth_status' : 'data/unauthorized_status.pl',        # URL路径未成功显示状态
        'auth_secret': 'data/auth_secret.pl',                   # 二次验证密钥
        'ssl':'ssl/choose.pl',                                    # ssl设置
        'hook_database' : 'data/hook_database.json',            # 数据库钩子
        'hook_menu' : 'data/hook_menu.json',                    # 菜单钩子
        'hook_global_static' : 'data/hook_global_static.json',  # 静态文件钩子
    }

    def __init__(self):
        pass

    def getVersion(self):
        return self.__version

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

    def setWebnameApi(self):
        webname = request.form.get('webname', '')
        if webname != mw.getConfig('title'):
            mw.setConfig('title', webname)
        return mw.returnJson(True, '面板别名保存成功!')

    def setPortApi(self):
        port = request.form.get('port', '')
        if port != mw.getHostPort():
            import system_api
            import firewall_api

            sysCfgDir = mw.systemdCfgDir()
            if os.path.exists(sysCfgDir + "/firewalld.service"):
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

        return mw.returnJson(True, '端口保存成功!')

    def setIpApi(self):
        host_ip = request.form.get('host_ip', '')
        if host_ip != mw.getHostAddr():
            mw.setHostAddr(host_ip)
        return mw.returnJson(True, 'IP保存成功!')

    def setWwwDirApi(self):
        sites_path = request.form.get('sites_path', '')
        if sites_path != mw.getWwwDir():
            mw.setWwwDir(sites_path)
        return mw.returnJson(True, '修改默认建站目录成功!')

    def setBackupDirApi(self):
        backup_path = request.form.get('backup_path', '')
        if backup_path != mw.getBackupDir():
            mw.setBackupDir(backup_path)
        return mw.returnJson(True, '修改默认备份目录成功!')

    def setBasicAuthApi(self):
        basic_user = request.form.get('basic_user', '').strip()
        basic_pwd = request.form.get('basic_pwd', '').strip()
        basic_open = request.form.get('is_open', '').strip()

        salt = '_md_salt'
        path = self.__file['basic_auth']
        is_open = True

        if basic_open == 'false':
            if os.path.exists(path):
                os.remove(path)
            return mw.returnJson(True, '删除BasicAuth成功!')

        if basic_user == '' or basic_pwd == '':
            return mw.returnJson(True, '用户和密码不能为空!')

        ba_conf = None
        if os.path.exists(path):
            try:
                ba_conf = json.loads(public.readFile(path))
            except:
                os.remove(path)

        if not ba_conf:
            ba_conf = {
                "basic_user": mw.md5(basic_user + salt),
                "basic_pwd": mw.md5(basic_pwd + salt),
                "open": is_open
            }
        else:
            ba_conf['basic_user'] = mw.md5(basic_user + salt)
            ba_conf['basic_pwd'] = mw.md5(basic_pwd + salt)
            ba_conf['open'] = is_open

        mw.writeFile(path, json.dumps(ba_conf))
        os.chmod(path, 384)
        mw.writeLog('面板设置', '设置BasicAuth状态为: %s' % is_open)

        mw.restartMw()
        return mw.returnJson(True, '设置成功!')

    def setApi(self):
        webname = request.form.get('webname', '')
        port = request.form.get('port', '')
        host_ip = request.form.get('host_ip', '')
        domain = request.form.get('domain', '')
        sites_path = request.form.get('sites_path', '')
        backup_path = request.form.get('backup_path', '')

        if domain != '':
            reg = "^([\\w\\-\\*]{1,100}\\.){1,4}(\\w{1,10}|\\w{1,10}\\.\\w{1,10})$"
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

            sysCfgDir = mw.systemdCfgDir()
            if os.path.exists(sysCfgDir + "/firewalld.service"):
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
        admin_path_checks = ['/', '/close', '/login',
                             '/do_login', '/site', '/sites',
                             '/download_file', '/control', '/crontab',
                             '/firewall', '/files', 'config',
                             '/soft', '/system', '/code',
                             '/ssl', '/plugins', '/hook']
        if admin_path == '':
            admin_path = '/'
        if admin_path != '/':
            if len(admin_path) < 6:
                return mw.returnJson(False, '安全入口地址长度不能小于6位!')
            if admin_path in admin_path_checks:
                return mw.returnJson(False, '该入口已被面板占用,请使用其它入口!')
            if not re.match("^/[\\w\\./-_]+$", admin_path):
                return mw.returnJson(False, '入口地址格式不正确,示例: /mw_rand')
        # else:
        #     domain = mw.readFile('data/bind_domain.pl')
        #     if not domain:
        #         domain = ''
        #     limitip = mw.readFile('data/bind_limitip.pl')
        #     if not limitip:
        #         limitip = ''
        #     if not domain.strip() and not limitip.strip():
        # return mw.returnJson(False,
        # '警告，关闭安全入口等于直接暴露你的后台地址在外网，十分危险，至少开启以下一种安全方式才能关闭：<a
        # style="color:red;"><br>1、绑定访问域名<br>2、绑定授权IP</a>')

        admin_path_file = self.__file['admin_path']
        admin_path_old = '/'
        if os.path.exists(admin_path_file):
            admin_path_old = mw.readFile(admin_path_file).strip()

        if admin_path_old != admin_path:
            mw.writeFile(admin_path_file, admin_path)
            mw.restartMw()
        return mw.returnJson(True, '修改成功!')

    def closePanelApi(self):
        filename = self.__file['close']
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
        ipv6_file = self.__file['ipv6']
        if os.path.exists(ipv6_file):
            os.remove(ipv6_file)
            mw.writeLog('面板设置', '关闭面板IPv6兼容!')
        else:
            mw.writeFile(ipv6_file, 'True')
            mw.writeLog('面板设置', '开启面板IPv6兼容!')
        mw.restartMw()
        return mw.returnJson(True, '设置成功!')

    # 获取面板证书
    def getPanelSslApi(self):
        cert = self.getPanelSslData()
        return mw.getJson(cert)

    def getPanelSslData(self):
        rdata = {}
        choose_file = self.__file['ssl']
        rdata['choose'] = mw.readFile(choose_file)


        keyPath = 'ssl/local/private.pem'
        certPath = 'ssl/local/cert.pem'

        if not os.path.exists(certPath):
            mw.createLocalSSL()

        cert = {}
        cert['privateKey'] = mw.readFile(keyPath)
        cert['is_https'] = ''
        cert['certPem'] = mw.readFile(certPath)
        cert['info'] = mw.getCertName(certPath)
        rdata['local'] = cert

        panel_ssl = mw.getServerDir() + "/web_conf/nginx/vhost/panel.conf"
        if not os.path.exists(panel_ssl):
            cert['is_https'] = ''
        else:
            ssl_data = mw.readFile(panel_ssl)
            if ssl_data.find('$server_port !~ 443') != -1:
                cert['is_https'] = 'checked'

        keyPath = 'ssl/nginx/private.pem'
        certPath = 'ssl/nginx/cert.pem'

        cert = {}
        cert['privateKey'] = mw.readFile(keyPath)
        cert['certPem'] = mw.readFile(certPath)
        cert['info'] = mw.getCertName(certPath)

        rdata['nginx'] = cert

        return rdata

    # 面板本地SSL设置
    def setPanelLocalSslApi(self):
        cert = {}
        keyPath = 'ssl/local/private.pem'
        certPath = 'ssl/local/cert.pem'

        if not os.path.exists(certPath):
            mw.createLocalSSL()

        choose_file = self.__file['ssl']
        mw.writeFile(choose_file, 'local')

        mw.restartMw()
        return mw.returnJson(True, '设置成功')

    # 关闭SSL
    def closePanelSslApi(self):
        choose_file = self.__file['ssl']
        if os.path.exists(choose_file):
            os.remove(choose_file)

        local_ssl = 'ssl/local'
        if os.path.exists(local_ssl):
            mw.execShell('rm -rf '+ local_ssl)

        nginx_ssl = 'ssl/nginx'
        if os.path.exists(nginx_ssl):
            mw.execShell('rm -rf '+ nginx_ssl)

        mw.restartMw()
        return mw.returnJson(True, '关闭SSL成功')

    # 保存面板证书
    def savePanelSslApi(self):

        choose = request.form.get('choose', '').strip()
        certPem = request.form.get('certPem', '').strip()
        privateKey = request.form.get('privateKey', '').strip()

        if not mw.inArray(['local','nginx'], choose):
            return mw.returnJson(True, '保存错误面板SSL类型!')


        keyPath = 'ssl/'+choose+'/private.pem'
        certPath = 'ssl/'+choose+'/cert.pem'
        checkCert = '/tmp/cert.pl'

        if not os.path.exists(keyPath):
            return mw.returnJson(False, '【'+choose+'】SSL类型不存在,先申请!')

        if(privateKey.find('KEY') == -1):
            return mw.returnJson(False, '秘钥错误，请检查!')
        if(certPem.find('CERTIFICATE') == -1):
            return mw.returnJson(False, '证书错误，请检查!')

        mw.writeFile(checkCert, certPem)
        if privateKey:
            mw.writeFile(keyPath, privateKey)
        if certPem:
            mw.writeFile(certPath, certPem)
        if not mw.checkCert(checkCert):
            return mw.returnJson(False, '证书错误,请检查!')
        return mw.returnJson(True, '证书已保存!')

    # 设置面板SSL证书设置
    # def setPanelHttpToHttpsApi(self):

    #     bind_domain = self.__file['bind_domain']
    #     if not os.path.exists(bind_domain):
    #         return mw.returnJson(False, '先要绑定域名!')

    #     choose_file = self.__file['ssl']
    #     choose = mw.readFile(choose_file)
    #     if choose == 'local':
    #         return mw.returnJson(False, '本地SSL无法使用!')

    #     keyPath = 'ssl/nginx/private.pem'
    #     if not os.path.exists(keyPath):
    #         return mw.returnJson(False, '未申请SSL证书!')

    #     is_https = request.form.get('https', '').strip()

    #     panel_ssl = mw.getServerDir() + "/web_conf/nginx/vhost/panel.conf"
    #     if not os.path.exists(panel_ssl):
    #         return mw.returnJson(False, '未开启面板SSL!')

    #     if is_https == 'false':
    #         conf = mw.readFile(panel_ssl)
    #         if conf:
    #             if conf.find('ssl_certificate') == -1:
    #                 return mw.returnJson(False, '当前未开启SSL')
    #             to = "#error_page 404/404.html;\n\
    # #HTTP_TO_HTTPS_START\n\
    # if ($server_port !~ 443){\n\
    #     rewrite ^(/.*)$ https://$host$1 permanent;\n\
    # }\n\
    # #HTTP_TO_HTTPS_END"
    #             conf = conf.replace('#error_page 404/404.html;', to)
    #             mw.writeFile(panel_ssl, conf)
    #     else:
    #         conf = mw.readFile(panel_ssl)
    #         if conf:
    #             rep = "\n\\s*#HTTP_TO_HTTPS_START(.|\n){1,300}#HTTP_TO_HTTPS_END"
    #             conf = re.sub(rep, '', conf)
    #             rep = "\\s+if.+server_port.+\n.+\n\\s+\\s*}"
    #             conf = re.sub(rep, '', conf)
    #             mw.writeFile(panel_ssl, conf)

    #     mw.restartNginx()

    #     action = '开启'
    #     if is_https == 'true':
    #         action = '关闭'
    #     return mw.returnJson(True, action + 'HTTPS跳转成功!')

    # 删除面板证书
    def delPanelSslApi(self):
        ip = mw.getLocalIp()
        if mw.isAppleSystem():
            ip = '127.0.0.1'

        port = mw.readFile('data/port.pl').strip()

        choose = request.form.get('choose', '').strip()

        if not mw.inArray(['local','nginx'], choose):
            return mw.returnJson(True, '删除错误面板SSL类型!')

        to_panel_url = 'http://'+ip+":"+port+'/config'

        if choose == 'local':
            dst_path = mw.getRunDir() + '/ssl/local'
            ssl_file = self.__file['ssl']
            if os.path.exists(dst_path):
                mw.execShell('rm -rf ' + dst_path)
                mw.execShell('rm -rf ' + ssl_file)
                mw.restartMw();
                return mw.returnJson(True, '删除本地面板SSL成功!',to_panel_url)
            else:
                return mw.returnJson(True, '已经删除本地面板SSL!',to_panel_url)

        if choose == 'nginx':

            bind_domain = self.__file['bind_domain']
            if not os.path.exists(bind_domain):
                return mw.returnJson(False, '未绑定域名!')

            siteName = mw.readFile(bind_domain).strip()

            src_path = mw.getServerDir() + '/web_conf/letsencrypt/' + siteName

            dst_path = mw.getRunDir() + '/ssl/nginx'
            dst_csrpath = dst_path + '/cert.pem'
            dst_keypath = dst_path + '/private.pem'

            if os.path.exists(src_path) or os.path.exists(dst_path):
                if os.path.exists(src_letpath):
                    mw.execShell('rm -rf ' + src_letpath)
                if os.path.exists(dst_csrpath):
                    mw.execShell('rm -rf ' + dst_csrpath)
                if os.path.exists(dst_keypath):
                    mw.execShell('rm -rf ' + dst_keypath)
                mw.restartNginx()
                return mw.returnJson(True, '删除面板SSL成功!')

            mw.restartNginx()
            mw.restartMw()
            return mw.returnJson(False, '已经删除面板SSL!')
        return  mw.returnJson(False, '未知类型!')

    # 申请面板let证书
    # def applyPanelAcmeSslApi(self):

    #     bind_domain = self.__file['bind_domain']
    #     if not os.path.exists(bind_domain):
    #         return mw.returnJson(False, '先要绑定域名!')

    #     # 生成nginx配置
    #     domain = mw.readFile(bind_domain)
    #     panel_tpl = mw.getRunDir() + "/data/tpl/nginx_panel.conf"
    #     dst_panel_path = mw.getServerDir() + "/web_conf/nginx/vhost/panel.conf"
    #     if not os.path.exists(dst_panel_path):
    #         reg = r"^([\w\-\*]{1,100}\.){1,4}(\w{1,10}|\w{1,10}\.\w{1,10})$"
    #         if not re.match(reg, domain):
    #             return mw.returnJson(False, '主域名格式不正确')

    #         op_dir = mw.getServerDir() + "/openresty"
    #         if not os.path.exists(op_dir):
    #             return mw.returnJson(False, '依赖OpenResty,先安装启动它!')

    #         content = mw.readFile(panel_tpl)
    #         content = content.replace("{$PORT}", "80")
    #         content = content.replace("{$SERVER_NAME}", domain)
    #         content = content.replace("{$PANAL_PORT}", mw.readFile('data/port.pl'))
    #         content = content.replace("{$LOGPATH}", mw.getRunDir() + '/logs')
    #         content = content.replace("{$PANAL_ADDR}", mw.getRunDir())
    #         mw.writeFile(dst_panel_path, content)
    #         mw.restartNginx()

    #     siteName = mw.readFile(bind_domain).strip()
    #     auth_to = mw.getRunDir() + "/tmp"
    #     to_args = {
    #         'domains': [siteName],
    #         'auth_type': 'http',
    #         'auth_to': auth_to,
    #     }

    #     src_path = mw.getServerDir() + '/web_conf/letsencrypt/' + siteName
    #     src_csrpath = src_path + "/fullchain.pem"  # 生成证书路径
    #     src_keypath = src_path + "/privkey.pem"  # 密钥文件路径

    #     dst_path = mw.getRunDir() + '/ssl/nginx'
    #     dst_csrpath = dst_path + '/cert.pem'
    #     dst_keypath = dst_path + '/private.pem'

    #     is_already_apply = False

    #     if not os.path.exists(src_path):
    #         import cert_api
    #         data = cert_api.cert_api().applyCertApi(to_args)
    #         if not data['status']:
    #             msg = data['msg']
    #             if type(data['msg']) != str:
    #                 msg = data['msg'][0]
    #                 emsg = data['msg'][1]['challenges'][0]['error']
    #                 msg = msg + '<p><span>响应状态:</span>' + str(emsg['status']) + '</p><p><span>错误类型:</span>' + emsg[
    #                     'type'] + '</p><p><span>错误代码:</span>' + emsg['detail'] + '</p>'
    #             return mw.returnJson(data['status'], msg, data['msg'])
    #     else:
    #         is_already_apply = True

    #     mw.buildSoftLink(src_csrpath, dst_csrpath, True)
    #     mw.buildSoftLink(src_keypath, dst_keypath, True)
    #     mw.execShell('echo "acme" > "' + dst_path + '/README"')

    #     tmp_well_know = auth_to + '/.well-known'
    #     if os.path.exists(tmp_well_know):
    #         mw.execShell('rm -rf ' + tmp_well_know)

    #     if os.path.exists(dst_path):
    #         choose_file = self.__file['ssl']
    #         mw.writeFile(choose_file, 'nginx')

    #     data = self.getPanelSslData()

    #     if is_already_apply:
    #         return mw.returnJson(True, '重复申请!', data)
    #     return mw.returnJson(True, '申请成功!', data)

    def setPanelDomainApi(self):
        domain = request.form.get('domain', '')

        cfg_domain = self.__file['bind_domain']

        port = mw.readFile('data/port.pl').strip()
        ip = mw.getLocalIp()

        if domain == '':
            if os.path.exists(cfg_domain):
                os.remove(cfg_domain)

            to_panel_url = 'http://'+ip+":"+port+'/config'
            
            mw.restartMw()
            return mw.returnJson(True, '清空域名成功!', to_panel_url)

        mw.writeFile(cfg_domain, domain)
        to_panel_url = 'http://'+domain+":"+port+'/config'
        mw.restartMw()
        return mw.returnJson(True, '设置域名成功!',to_panel_url)

     # 设置面板SSL
    # def setPanelSslApi(self):
    #     sslConf = mw.getRunDir() + '/' + self.__file['ssl']

    #     panel_tpl = mw.getRunDir() + "/data/tpl/nginx_panel.conf"
    #     dst_panel_path = mw.getServerDir() + "/web_conf/nginx/vhost/panel.conf"
    #     if os.path.exists(sslConf):
    #         os.system('rm -f ' + sslConf)

    #         conf = mw.readFile(dst_panel_path)
    #         if conf:
    #             rep = "\\s+ssl_certificate\\s+.+;\\s+ssl_certificate_key\\s+.+;"
    #             conf = re.sub(rep, '', conf)
    #             rep = "\\s+ssl_protocols\\s+.+;\n"
    #             conf = re.sub(rep, '', conf)
    #             rep = "\\s+ssl_ciphers\\s+.+;\n"
    #             conf = re.sub(rep, '', conf)
    #             rep = "\\s+ssl_prefer_server_ciphers\\s+.+;\n"
    #             conf = re.sub(rep, '', conf)
    #             rep = "\\s+ssl_session_cache\\s+.+;\n"
    #             conf = re.sub(rep, '', conf)
    #             rep = "\\s+ssl_session_timeout\\s+.+;\n"
    #             conf = re.sub(rep, '', conf)
    #             rep = "\\s+ssl_ecdh_curve\\s+.+;\n"
    #             conf = re.sub(rep, '', conf)
    #             rep = "\\s+ssl_session_tickets\\s+.+;\n"
    #             conf = re.sub(rep, '', conf)
    #             rep = "\\s+ssl_stapling\\s+.+;\n"
    #             conf = re.sub(rep, '', conf)
    #             rep = "\\s+ssl_stapling_verify\\s+.+;\n"
    #             conf = re.sub(rep, '', conf)
    #             rep = "\\s+ssl\\s+on;"
    #             conf = re.sub(rep, '', conf)
    #             rep = "\\s+error_page\\s497.+;"
    #             conf = re.sub(rep, '', conf)
    #             rep = "\\s+if.+server_port.+\n.+\n\\s+\\s*}"
    #             conf = re.sub(rep, '', conf)
    #             rep = "\\s+listen\\s+443.*;"
    #             conf = re.sub(rep, '', conf)
    #             rep = "\\s+listen\\s+\\[\\:\\:\\]\\:443.*;"
    #             conf = re.sub(rep, '', conf)
    #             mw.writeFile(dst_panel_path, conf)

    #         mw.writeLog('面板配置', '面板SSL关闭成功!')
    #         mw.restartWeb()
    #         return mw.returnJson(True, 'SSL已关闭，请使用http协议访问面板!')
    #     else:
    #         try:
    #             mw.writeFile(sslConf, 'True')

    #             keyPath = mw.getRunDir() + '/ssl/private.pem'
    #             certPath = mw.getRunDir() + '/ssl/cert.pem'

    #             conf = mw.readFile(dst_panel_path)
    #             if conf:
    #                 if conf.find('ssl_certificate') == -1:
    #                     sslStr = """#error_page 404/404.html;
    # ssl_certificate    %s;
    # ssl_certificate_key  %s;
    # ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
    # ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:HIGH:!aNULL:!MD5:!RC4:!DHE;
    # ssl_prefer_server_ciphers on;
    # ssl_session_cache shared:SSL:10m;
    # ssl_session_timeout 10m;
    # error_page 497  https://$host$request_uri;""" % (certPath, keyPath)
    #                 if(conf.find('ssl_certificate') != -1):
    #                     return mw.returnJson(True, 'SSL开启成功!')

    #                 conf = conf.replace('#error_page 404/404.html;', sslStr)

    #                 rep = "listen\\s+([0-9]+)\\s*[default_server]*;"
    #                 tmp = re.findall(rep, conf)
    #                 if not mw.inArray(tmp, '443'):
    #                     listen = re.search(rep, conf).group()
    #                     http_ssl = "\n\tlisten 443 ssl http2;"
    #                     http_ssl = http_ssl + "\n\tlisten [::]:443 ssl http2;"
    #                     conf = conf.replace(listen, listen + http_ssl)

    #                 mw.backFile(dst_panel_path)
    #                 mw.writeFile(dst_panel_path, conf)
    #                 isError = mw.checkWebConfig()
    #                 if(isError != True):
    #                     mw.restoreFile(dst_panel_path)
    #                     return mw.returnJson(False, '证书错误: <br><a style="color:red;">' + isError.replace("\n", '<br>') + '</a>')
    #         except Exception as ex:
    #             return mw.returnJson(False, '开启失败:' + str(ex))
    #         mw.restartWeb()
    #         return mw.returnJson(True, '开启成功，请使用https协议访问面板!')

    def getApi(self):
        data = {}
        return mw.getJson(data)
    ##### ----- end ----- ###

    # 获取临时登录列表
    def getTempLoginApi(self):
        if 'tmp_login_expire' in session:
            return mw.returnJson(False, '没有权限')
        limit = request.form.get('limit', '10').strip()
        p = request.form.get('p', '1').strip()
        tojs = request.form.get('tojs', '').strip()

        tempLoginM = mw.M('temp_login')
        tempLoginM.where('state=? and expire<?',
                         (0, int(time.time()))).setField('state', -1)

        start = (int(p) - 1) * (int(limit))
        vlist = tempLoginM.limit(str(start) + ',' + str(limit)).order('id desc').field(
            'id,addtime,expire,login_time,login_addr,state').select()

        data = {}
        data['data'] = vlist

        count = tempLoginM.count()
        page_args = {}
        page_args['count'] = count
        page_args['tojs'] = 'get_temp_login'
        page_args['p'] = p
        page_args['row'] = limit

        data['page'] = mw.getPage(page_args)
        return mw.getJson(data)

    # 删除临时登录
    def removeTempLoginApi(self):
        if 'tmp_login_expire' in session:
            return mw.returnJson(False, '没有权限')
        sid = request.form.get('id', '10').strip()
        if mw.M('temp_login').where('id=?', (sid,)).delete():
            mw.writeLog('面板设置', '删除临时登录连接')
            return mw.returnJson(True, '删除成功')
        return mw.returnJson(False, '删除失败')

    def setTempLoginApi(self):
        if 'tmp_login_expire' in session:
            return mw.returnJson(False, '没有权限')
        s_time = int(time.time())
        mw.M('temp_login').where(
            'state=? and expire>?', (0, s_time)).delete()
        token = mw.getRandomString(48)
        salt = mw.getRandomString(12)

        pdata = {
            'token': mw.md5(token + salt),
            'salt': salt,
            'state': 0,
            'login_time': 0,
            'login_addr': '',
            'expire': s_time + 3600,
            'addtime': s_time
        }

        if not mw.M('temp_login').count():
            pdata['id'] = 101

        if mw.M('temp_login').insert(pdata):
            mw.writeLog('面板设置', '生成临时连接,过期时间:{}'.format(
                mw.formatDate(times=pdata['expire'])))
            return mw.getJson({'status': True, 'msg': "临时连接已生成", 'token': token, 'expire': pdata['expire']})
        return mw.returnJson(False, '连接生成失败')

    def getTempLoginLogsApi(self):
        if 'tmp_login_expire' in session:
            return mw.returnJson(False, '没有权限')

        logs_id = request.form.get('id', '').strip()
        logs_id = int(logs_id)
        data = mw.M('logs').where(
            'uid=?', (logs_id,)).order('id desc').field(
            'id,type,uid,log,addtime').select()
        return mw.returnJson(False, 'ok', data)

    def checkPanelToken(self):
        api_file = self.__api_addr
        if not os.path.exists(api_file):
            return False, ''

        tmp = mw.readFile(api_file)
        data = json.loads(tmp)
        if data['open']:
            return True, data
        else:
            return False, ''

    def setStatusCodeApi(self):
        status_code = request.form.get('status_code', '').strip()
        if re.match("^\\d+$", status_code):
            status_code = int(status_code)
            if status_code != 0:
                if status_code < 100 or status_code > 999:
                    return mw.returnJson(False, '状态码范围错误!')
        else:
            return mw.returnJson(False, '状态码范围错误!')
        unauthorized_status = self.__file['unauth_status']
        mw.writeFile(unauthorized_status, str(status_code))
        mw.writeLog('面板设置', '将未授权响应状态码设置为:{}'.format(status_code))
        return mw.returnJson(True, '设置成功!')

    def getNotifyApi(self):
        # 获取
        data = mw.getNotifyData(True)
        return mw.returnData(True, 'ok', data)

    def setNotifyApi(self):
        tag = request.form.get('tag', '').strip()
        data = request.form.get('data', '').strip()

        cfg = mw.getNotifyData(False)

        crypt_data = mw.enDoubleCrypt(tag, data)
        if tag in cfg:
            cfg[tag]['cfg'] = crypt_data
        else:
            t = {'cfg': crypt_data}
            cfg[tag] = t

        mw.writeNotify(cfg)
        return mw.returnData(True, '设置成功')

    def setNotifyTestApi(self):
        # 异步通知验证
        tag = request.form.get('tag', '').strip()
        tag_data = request.form.get('data', '').strip()

        if tag == 'tgbot':
            t = json.loads(tag_data)
            test_bool = mw.tgbotNotifyTest(t['app_token'], t['chat_id'])
            if test_bool:
                return mw.returnData(True, '验证成功')
            return mw.returnData(False, '验证失败')

        if tag == 'email':
            t = json.loads(tag_data)
            test_bool = mw.emailNotifyTest(t)
            if test_bool:
                return mw.returnData(True, '验证成功')
            return mw.returnData(False, '验证失败')

        return mw.returnData(False, '暂时未支持该验证')

    def setNotifyEnableApi(self):
        # 异步通知验证
        tag = request.form.get('tag', '').strip()
        tag_enable = request.form.get('enable', '').strip()

        data = mw.getNotifyData(False)
        op_enable = True
        op_action = '开启'
        if tag_enable != 'true':
            op_enable = False
            op_action = '关闭'

        if tag in data:
            data[tag]['enable'] = op_enable

        mw.writeNotify(data)

        return mw.returnData(True, op_action + '成功')

    def getPanelTokenApi(self):
        api_file = self.__api_addr
        tmp = mw.readFile(api_file)
        if not os.path.exists(api_file):
            ready_data = {"open": False, "token": "", "limit_addr": []}
            mw.writeFile(api_file, json.dumps(ready_data))
            mw.execShell("chmod 600 " + api_file)
            tmp = mw.readFile(api_file)
        data = json.loads(tmp)

        if not 'key' in data:
            data['key'] = mw.getRandomString(16)
            mw.writeFile(api_file, json.dumps(data))

        if 'token_crypt' in data:
            data['token'] = mw.deCrypt(data['token'], data['token_crypt'])
        else:
            token = mw.getRandomString(32)
            data['token'] = mw.md5(token)
            data['token_crypt'] = mw.enCrypt(
                data['token'], token)
            mw.writeFile(api_file, json.dumps(data))
            data['token'] = "***********************************"

        data['limit_addr'] = '\n'.join(data['limit_addr'])

        del(data['key'])
        return mw.returnJson(True, 'ok', data)

    def setPanelTokenApi(self):
        op_type = request.form.get('op_type', '').strip()

        if op_type == '1':
            token = mw.getRandomString(32)
            data['token'] = mw.md5(token)
            data['token_crypt'] = mw.enCrypt(
                data['token'], token).decode('utf-8')
            mw.writeLog('API配置', '重新生成API-Token')
            mw.writeFile(api_file, json.dumps(data))
            return mw.returnJson(True, 'ok', token)

        api_file = self.__api_addr
        if not os.path.exists(api_file):
            return mw.returnJson(False, "先在API接口配置")
        else:
            tmp = mw.readFile(api_file)
            data = json.loads(tmp)

        if op_type == '2':
            data['open'] = not data['open']
            stats = {True: '开启', False: '关闭'}
            if not 'token_crypt' in data:
                token = mw.getRandomString(32)
                data['token'] = mw.md5(token)
                data['token_crypt'] = mw.enCrypt(data['token'], token).decode('utf-8')

            token = stats[data['open']] + '成功!'
            mw.writeLog('API配置', '%sAPI接口' % stats[data['open']])
            mw.writeFile(api_file, json.dumps(data))
            return mw.returnJson(not not data['open'], token)

        elif op_type == '3':

            limit_addr = request.form.get('limit_addr', '').strip()
            data['limit_addr'] = limit_addr.split('\n')
            mw.writeLog('API配置', '变更IP限制为[%s]' % limit_addr)
            mw.writeFile(api_file, json.dumps(data))
            return mw.returnJson(True, '保存成功!')

    def renderUnauthorizedStatus(self, data):
        cfg_unauth_status = self.__file['unauth_status']
        if os.path.exists(cfg_unauth_status):
            status_code = mw.readFile(cfg_unauth_status)
            data['status_code'] = status_code
            data['status_code_msg'] = status_code
            if status_code == '0':
                data['status_code_msg'] = "默认-安全入口错误提示"
            elif status_code == '400':
                data['status_code_msg'] = "400-客户端请求错误"
            elif status_code == '401':
                data['status_code_msg'] = "401-未授权访问"
            elif status_code == '403':
                data['status_code_msg'] = "403-拒绝访问"
            elif status_code == '404':
                data['status_code_msg'] = "404-页面不存在"
            elif status_code == '408':
                data['status_code_msg'] = "408-客户端超时"
            elif status_code == '416':
                data['status_code_msg'] = "416-无效的请求"
        else:
            data['status_code'] = '0'
            data['status_code_msg'] = "默认-安全入口错误提示"
        return data


    def getTimezoneListApi(self):
        # 获取时区列表
        # pytz.all_timezones | 所有
        # pytz.common_timezones
        return pytz.all_timezones

    def setTimezoneApi(self):
        # 设置时区列表
        timezone = request.form.get('timezone', '').strip()
        cmd = 'timedatectl set-timezone "'+timezone+'"'
        mw.execShell(cmd)
        return mw.returnJson(True, '设置成功!')


    def getAuthSecretApi(self):
        reset = request.form.get('reset', '')

        import pyotp
        auth = self.__file['auth_secret']
        tag = 'mdserver-web'
        if os.path.exists(auth) and reset != '1':
            content = mw.readFile(auth)
            sec = mw.deDoubleCrypt(tag,content)
        else:
            sec = pyotp.random_base32()
            crypt_data = mw.enDoubleCrypt(tag, sec)
            mw.writeFile(auth, crypt_data)

        ip = mw.getHostAddr()
        url = pyotp.totp.TOTP(sec).provisioning_uri(name=ip, issuer_name=tag)

        rdata = {}
        rdata['secret'] = sec
        rdata['url'] = url
        return mw.returnJson(True, '设置成功!', rdata)

    def setAuthSecretApi(self):
        auth = self.__file['auth_secret']
        if os.path.exists(auth):
            os.remove(auth)
            return mw.returnJson(True, '关闭成功!', 0)
        else:
            return mw.returnJson(True, '开启成功!', 1)


    def get(self):

        data = {}
        data['title'] = mw.getConfig('title')
        data['site_path'] = mw.getWwwDir()
        data['backup_path'] = mw.getBackupDir()
        sformat = 'date +"%Y-%m-%d %H:%M:%S %Z %z"'
        data['systemdate'] = mw.execShell(sformat)[0].strip()

        data['port'] = mw.getHostPort()
        data['ip'] = mw.getHostAddr()

        admin_path_file = self.__file['admin_path']
        if not os.path.exists(admin_path_file):
            data['admin_path'] = '/'
        else:
            data['admin_path'] = mw.readFile(admin_path_file)

        ipv6_file = self.__file['ipv6']
        if os.path.exists(ipv6_file):
            data['ipv6'] = 'checked'
        else:
            data['ipv6'] = ''

        debug_file = self.__file['debug']
        if os.path.exists(debug_file):
            data['debug'] = 'checked'
        else:
            data['debug'] = ''

        ssl_file = self.__file['ssl']
        if os.path.exists(ssl_file):
            data['ssl'] = 'checked'
        else:
            data['ssl'] = ''


        auth_secret = self.__file['auth_secret']
        if os.path.exists(auth_secret):
            data['auth_secret'] = 'checked'
        else:
            data['auth_secret'] = ''

        basic_auth = self.__file['basic_auth']
        if os.path.exists(basic_auth):
            bac = mw.readFile(basic_auth)
            bac = json.loads(bac)
            if bac['open']:
                data['basic_auth'] = 'checked'
        else:
            data['basic_auth'] = ''

        cfg_domain = self.__file['bind_domain']
        if os.path.exists(cfg_domain):
            domain = mw.readFile(cfg_domain)
            data['bind_domain'] = domain.strip()
        else:
            data['bind_domain'] = ''

        data = self.renderUnauthorizedStatus(data)

        #api
        api_token = self.__api_addr
        if os.path.exists(api_token):
            bac = mw.readFile(api_token)
            bac = json.loads(bac)
            if bac['open']:
                data['api_token'] = 'checked'
        else:
            data['api_token'] = ''

        #auth


        data['site_count'] = mw.M('sites').count()

        data['username'] = mw.M('users').where(
            "id=?", (1,)).getField('username')

        data['hook_tag'] = request.args.get('tag', '')

        # databases hook
        database_hook_file = self.__file['hook_database']
        if os.path.exists(database_hook_file):
            df = mw.readFile(database_hook_file)
            df = json.loads(df)
            data['hook_database'] = df
        else:
            data['hook_database'] = []

        # menu hook
        menu_hook_file = self.__file['hook_menu']
        if os.path.exists(menu_hook_file):
            df = mw.readFile(menu_hook_file)
            df = json.loads(df)
            data['hook_menu'] = df
        else:
            data['hook_menu'] = []

        # global_static hook
        global_static_hook_file = self.__file['hook_global_static']
        if os.path.exists(global_static_hook_file):
            df = mw.readFile(global_static_hook_file)
            df = json.loads(df)
            data['hook_global_static'] = df
        else:
            data['hook_global_static'] = []

        # notiy config
        notify_data = mw.getNotifyData(True)
        notify_tag_list = ['tgbot', 'email']
        for tag in notify_tag_list:
            new_tag = 'notify_' + tag + '_enable'
            data[new_tag] = ''
            if tag in notify_data and 'enable' in notify_data[tag]:
                if notify_data[tag]['enable']:
                    data[new_tag] = 'checked'

        return data
