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

    def __init__(self):
        pass

    ##### ----- start ----- ###
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
        if domain != '':
            reg = "^([\w\-\*]{1,100}\.){1,4}(\w{1,10}|\w{1,10}\.\w{1,10})$"
            if not re.match(reg, domain):
                return public.returnJson(False, '主域名格式不正确')

        if int(port) >= 65535 or int(port) < 100:
            return public.returnJson(False, '端口范围不正确!')

        if webname != public.getConfig('title'):
            public.setConfig('title', webname)

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

    ##### ----- end ----- ###

    def get(self):

        data = {}
        data['title'] = public.getConfig('title')
        data['site_path'] = public.getWwwDir()
        data['backup_path'] = public.getBackupDir()
        sformat = 'date +"%Y-%m-%d %H:%M:%S %Z %z"'
        data['systemdate'] = public.execShell(sformat)[0].strip()

        data['port'] = public.getHostPort()
        data['ip'] = public.getHostAddr()

        data['username'] = public.M('users').where(
            "id=?", (1,)).getField('username')

        return data
