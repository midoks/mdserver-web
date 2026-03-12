# coding:utf-8

import sys
import io
import os
import time
import re
import socket
import json

from datetime import datetime

web_dir = os.getcwd() + "/web"
if os.path.exists(web_dir):
    sys.path.append(web_dir)
    os.chdir(web_dir)

import core.mw as mw

app_debug = False
if mw.isAppleSystem():
    app_debug = True


class App:
    __setupPath = '/www/server/ollama'
    __cfg = ''
    __agent_cfg = ''

    def __init__(self):
        self.__setupPath = self.getServerDir()

    def getArgs(self):
        args = sys.argv[3:]
        tmp = {}
        args_len = len(args)

        if args_len == 1:
            t = args[0].strip('{').strip('}')
            t = t.split(':', 1)
            tmp[t[0]] = t[1]
        elif args_len > 1:
            for i in range(len(args)):
                t = args[i].split(':', 1)
                tmp[t[0]] = t[1]

        return tmp

    def checkArgs(self, data, ck=[]):
        for i in range(len(ck)):
            if not ck[i] in data:
                return (False, mw.returnJson(False, '参数:(' + ck[i] + ')没有!'))
        return (True, mw.returnJson(True, 'ok'))


    def getPluginName(self):
        return 'ollama'

    def getPluginDir(self):
        return mw.getPluginDir() + '/' + self.getPluginName()

    def getServerDir(self):
        return mw.getServerDir() + '/' + self.getPluginName()

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
        cmd = "ps -ef|grep " + self.getPluginName() + " |grep -v grep | grep -v python | awk '{print $2}'"
        data = mw.execShell(cmd)
        if data[0] == '':
            return "stop"
        return 'start'

    def contentReplace(self, content):

        service_path = mw.getServerDir()
        content = content.replace('{$ROOT_PATH}', mw.getFatherDir())
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
        # systemDir = mw.systemdCfgDir()
        # systemService = systemDir + '/nezha.service'
        # systemServiceTpl = self.getPluginDir() + '/init.d/nezha.service.tpl'
        # if os.path.exists(systemDir) and not os.path.exists(systemService):
        #     service_path = mw.getServerDir()
        #     se_content = mw.readFile(systemServiceTpl)
        #     se_content = self.contentReplace(se_content)
        #     mw.writeFile(systemService, se_content)
        #     mw.execShell('systemctl daemon-reload')

        return file_bin

    def contentAgentReplace(self, content):
        path = self.__agent_cfg
        if os.path.exists(path):
            data = self.get_agent_cfg()
            content = content.replace('{$APP_HOST}', data['host'])
            content = content.replace('{$APP_SECRET}', data['secret'])

        return content


    def init_cfg(self):
        self.initDreplace()

    def oaOp(self, method):

        file = self.initDreplace()

        if not mw.isAppleSystem():
            cmd = 'systemctl {} {}'.format(method, self.getPluginName())
            data = mw.execShell(cmd)
            if data[1] == '':
                return 'ok'
            return 'fail'

        data = mw.execShell(file + ' ' + method)
        if data[1] == '':
            return 'ok'
        return data[0]

    def start(self):
        return self.oaOp('start')

    def stop(self):
        return self.oaOp('stop')

    def restart(self):
        return self.oaOp('restart')

    def reload(self):
        return self.oaOp('reload')

    def agOp(self, method):

        if not mw.isAppleSystem():
            cmd = 'systemctl {} {}'.format(method, self.getPluginName())
            data = mw.execShell(cmd)
            if data[1] == '':
                return 'ok'
            return 'fail'

        data = mw.execShell(file + ' ' + method)
        if data[1] == '':
            return 'ok'
        return data[0]

    def start_agent(self):
        return self.agOp('start')

    def stop_agent(self):
        return self.agOp('stop')

    def restart_agent(self):
        return self.agOp('restart')

    def reload_agent(self):
        return self.agentOp('reload')

    def initd_status(self):
        cmd = 'systemctl status '+self.getPluginName()+' | grep loaded | grep "enabled;"'
        data = mw.execShell(cmd)
        if data[0] == '':
            return 'fail'
        return 'ok'

    def initd_install(self):
        mw.execShell('systemctl enable '+self.getPluginName())
        return 'ok'

    def initd_uninstall(self):
        mw.execShell('systemctl disable '+self.getPluginName())
        return 'ok'

    def conf(self):
        return self.getServerDir() + '/dashboard/data/config.yaml'


    def run_log(self):
        return self.getServerDir() + '/logs/nezha.log'


if __name__ == "__main__":
    func = sys.argv[1]
    classApp = App()
    try:
        data = eval("classApp." + func + "()")
        print(data)
    except Exception as e:
        print('error:' + str(e))
