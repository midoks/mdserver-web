# coding:utf-8

import sys
import io
import os
import time
import re
import socket
import json

from datetime import datetime

sys.path.append(os.getcwd() + "/class/core")
import mw

app_debug = False
if mw.isAppleSystem():
    app_debug = True


class App:
    __setupPath = '/www/server/imail'
    __SR = ''

    def __init__(self):
        self.__setupPath = self.getServerDir()

        self.__SR = '''#!/bin/bash
    PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
    export PATH
    export USER=%s
    export HOME=%s && ''' % ( self.getRunUser(), self.getHomeDir())

    def getArgs(self):
        args = sys.argv[3:]
        tmp = {}
        args_len = len(args)

        if args_len == 1:
            t = args[0].strip('{').strip('}')
            t = t.split(':')
            tmp[t[0]] = t[1]
        elif args_len > 1:
            for i in range(len(args)):
                t = args[i].split(':')
                tmp[t[0]] = t[1]

        return tmp

    def __release_port(self, port):
        from collections import namedtuple
        try:
            import firewall_api
            firewall_api.firewall_api().addAcceptPortArgs(port, 'IMail-Server', 'port')
            return port
        except Exception as e:
            return "Release failed {}".format(e)

    def openPort(self):
        for i in ["25", "110", "143", "465", "995", "993", "587"]:
            self.__release_port(i)
        return True

    def getPluginName(self):
        return 'imail'

    def getPluginDir(self):
        return mw.getPluginDir() + '/' + self.getPluginName()

    def getServerDir(self):
        return mw.getServerDir() + '/' + self.getPluginName()

    def getInitdConfTpl(self):
        path = self.getPluginDir() + "/init.d/imail.tpl"
        return path

    def getHomeDir(self):
        if mw.isAppleSystem():
            user = mw.execShell(
                "who | sed -n '2, 1p' |awk '{print $1}'")[0].strip()
            return '/Users/' + user
        else:
            return '/root'

    def getRunUser(self):
        if mw.isAppleSystem():
            user = mw.execShell(
                "who | sed -n '2, 1p' |awk '{print $1}'")[0].strip()
            return user
        else:
            return 'root'

    def status(self):
        data = mw.execShell(
            "ps -ef|grep " + self.getPluginName() + " |grep -v grep | grep -v python | awk '{print $2}'")
        if data[0] == '':
            return 'stop'
        return 'start'

    def contentReplace(self, content):

        service_path = mw.getServerDir()
        content = content.replace('{$ROOT_PATH}', mw.getRootDir())
        content = content.replace('{$SERVER_PATH}', service_path)
        content = content.replace('{$RUN_USER}', self.getRunUser())
        content = content.replace('{$HOME_DIR}', self.getHomeDir())

        return content

    def initDreplace(self):

        file_tpl = self.getInitdConfTpl()
        service_path = mw.getServerDir()

        initD_path = self.getServerDir() + '/init.d'
        if not os.path.exists(initD_path):
            os.mkdir(initD_path)
            self.openPort()

        file_bin = initD_path + '/' + self.getPluginName()

        if not os.path.exists(file_bin):
            content = mw.readFile(file_tpl)
            content = self.contentReplace(content)
            mw.writeFile(file_bin, content)
            mw.execShell('chmod +x ' + file_bin)

        # systemd
        systemDir = mw.systemdCfgDir()
        systemService = systemDir + '/imail.service'
        systemServiceTpl = self.getPluginDir() + '/init.d/imail.service.tpl'
        if os.path.exists(systemDir) and not os.path.exists(systemService):
            service_path = mw.getServerDir()
            se_content = mw.readFile(systemServiceTpl)
            se_content = se_content.replace('{$SERVER_PATH}', service_path)
            mw.writeFile(systemService, se_content)
            mw.execShell('systemctl daemon-reload')

        log_path = self.getServerDir() + '/logs'
        if not os.path.exists(log_path):
            os.mkdir(log_path)

        return file_bin

    def imOp(self, method):
        file = self.initDreplace()

        if not mw.isAppleSystem():
            cmd = 'systemctl {} {}'.format(method, self.getPluginName())
            data = mw.execShell(cmd)
            if data[1] == '':
                return 'ok'
            return 'fail'

        data = mw.execShell(self.__SR + file + ' ' + method)
        if data[1] == '':
            return 'ok'
        return data[0]

    def start(self):
        return self.imOp('start')

    def stop(self):
        return self.imOp('stop')

    def restart(self):
        return self.imOp('restart')

    def reload(self):
        return self.imOp('reload')

    def initd_status(self):
        if mw.isAppleSystem():
            return "Apple Computer does not support"

        cmd = 'systemctl status imail | grep loaded | grep "enabled;"'
        data = mw.execShell(cmd)
        if data[0] == '':
            return 'fail'
        return 'ok'

    def initd_install(self):
        if mw.isAppleSystem():
            return "Apple Computer does not support"

        mw.execShell('systemctl enable imail')
        return 'ok'

    def initd_uinstall(self):
        if mw.isAppleSystem():
            return "Apple Computer does not support"

        mw.execShell('systemctl disable imail')
        return 'ok'

    def conf(self):
        conf_path = self.getServerDir() + '/custom/conf/app.conf'
        if not os.path.exists(conf_path):
            return mw.returnJson(False, "请先安装初始化!<br/>默认地址:http://" + mw.getLocalIp() + ":1080")

        return self.getServerDir() + '/custom/conf/app.conf'

    def run_log(self):
        ilog = self.getServerDir() + '/logs/imail.log'
        if not os.path.exists(ilog):
            return mw.returnJson(False, "请先安装初始化!<br/>默认地址:http://" + mw.getLocalIp() + ":1080")

        return self.getServerDir() + '/logs/imail.log'


if __name__ == "__main__":
    func = sys.argv[1]
    classApp = App()
    try:
        data = eval("classApp." + func + "()")
        print(data)
    except Exception as e:
        print('error:' + str(e))
