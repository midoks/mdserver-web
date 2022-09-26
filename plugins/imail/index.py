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

    def __init__(self):
        self.__setupPath = self.getServerDir()

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

    def getPluginName(self):
        return 'mail'

    def getPluginDir(self):
        return mw.getPluginDir() + '/' + self.getPluginName()

    def getServerDir(self):
        return mw.getServerDir() + '/' + self.getPluginName()

    def status(self):
        data = mw.execShell(
            "ps -ef|grep " + self.getPluginName() + " |grep -v grep | grep -v python | awk '{print $2}'")
        if data[0] == '':
            return 'stop'
        return 'start'

    def initDreplace(self):

        file_tpl = self.getInitdConfTpl()
        service_path = mw.getServerDir()

        initD_path = self.getServerDir() + '/init.d'
        if not os.path.exists(initD_path):
            os.mkdir(initD_path)
        file_bin = initD_path + '/' + self.getPluginName()

        if not os.path.exists(file_bin):
            content = mw.readFile(file_tpl)
            content = contentReplace(content)
            mw.writeFile(file_bin, content)
            mw.execShell('chmod +x ' + file_bin)

        # systemd
        # systemDir = mw.systemdCfgDir()
        # systemService = systemDir + '/gogs.service'
        # systemServiceTpl = getPluginDir() + '/init.d/gogs.service.tpl'
        # if os.path.exists(systemDir) and not os.path.exists(systemService):
        #     service_path = mw.getServerDir()
        #     se_content = mw.readFile(systemServiceTpl)
        #     se_content = se_content.replace('{$SERVER_PATH}', service_path)
        #     mw.writeFile(systemService, se_content)
        #     mw.execShell('systemctl daemon-reload')

        # log_path = getServerDir() + '/log'
        # if not os.path.exists(log_path):
        #     os.mkdir(log_path)

        return file_bin

    def imOp(self, method):
        file = self.initDreplace()

        if not mw.isAppleSystem():
            data = mw.execShell('systemctl ' + method + ' imail')
            if data[1] == '':
                return 'ok'
            return 'fail'

        data = mw.execShell(__SR + file + ' ' + method)
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


if __name__ == "__main__":
    func = sys.argv[1]
    classApp = App()
    try:
        data = eval("classApp." + func + "()")
        print(data)
    except Exception as e:
        print('error:' + str(e))
