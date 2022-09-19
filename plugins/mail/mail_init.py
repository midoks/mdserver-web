# coding:utf-8

import sys
import io
import os
import time
import re


sys.path.append(os.getcwd() + "/class/core")

import mw
app_debug = False
if mw.isAppleSystem():
    app_debug = True


class mail_init:

    def __init__(self):
        self.logfile = '/tmp/mail_init.log'

    def check_env(self):
        data = {}
        data['HostName'] = self.check_hostname()
        data['Postfix-install'] = {"status": True, "msg": "Postfix已经安装"} if os.path.exists(
            '/usr/sbin/postfix') else {"status": False, "msg": "Postfix未安装,请点击修复按钮"}
        data['Dovecot-install'] = {"status": True, "msg": "Deovecot已经安装"} if os.path.exists(
            '/usr/sbin/dovecot') else {"status": False, "msg": "Dovecot未安装,请点击修复按钮"}
        data['Postfix-Version'] = self.check_postfix_ver()
        data['Redis-install'] = {"status": True, "msg": "Redis已经安装"} if os.path.exists(
            mw.getServerDir() + '/redis/bin/redis-server') else {"status": False, "msg": "请到软件商店内安装Redis"}
        data['Redis-Passwd'] = self.check_redis_passwd(data['Redis-install'])
        data['Rspamd-install'] = {"status": True, "msg": "Rspamd已经安装"} if os.path.exists(
            '/usr/bin/rspamd') else {"status": False, "msg": "Rspamd未安装,请点击修复按钮"}
        data['Sqlite-support'] = self.check_sqlite()
        data['SElinux'] = {"status": True, "msg": "SElinux已经禁用"} if not 'enforcing' in mw.execShell(
            'getenforce')[0].lower() else {"status": False, "msg": "请先禁用SElinux"}
        return data

    def check_hostname(self):
        import socket
        rep = '^(?!:\/\/)(?=.{1,255}$)((.{1,63}\.){1,127}(?![0-9]*$)[a-z0-9-]+\.?)$'
        hostname = socket.gethostname()
        if re.search(rep, hostname):
            return mw.returnData(True, 'success')
        return mw.returnData(False, '你的主机名 ({}) 不合规定, 需要是完整域名'
                             '你可以通过以下命令修复你的主机名 '
                             '在ssh终端执行 \'hostnamectl set-hostname --static mail.example.com\''.format(hostname))

    def check_postfix_ver(self):
        postfix_version = mw.execShell(
            r"postconf mail_version|sed -r 's/.* ([0-9\.]+)$/\1/'")[0].strip()
        if postfix_version.startswith('3'):
            return mw.returnData(True, postfix_version)
        else:
            return mw.returnData(False, "当前版本不支持或Postfix没有安装成功：{}".format(postfix_version))

    def check_redis_passwd(self, redis_install):
        redis_conf = mw.readFile(mw.getServerDir() + '/redis/redis.conf')
        if redis_install['status']:
            if re.search('\n\s*requirepass', redis_conf):
                return mw.returnData(True, "Redis已经设置密码")
        return mw.returnData(False, "请到Redis管理器设置密码！")

    def check_sqlite(self):
        if not mw.execShell('postconf -m | grep sqlite')[0].strip():
            return mw.returnData(False, "Postfix不支持Sqlite")
        return mw.returnData(True, "Postfix已支持Sqlite")
