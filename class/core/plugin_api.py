# coding: utf-8

import psutil
import time
import os
import public
import re
import json


class plugin_api:
    __tasks = None
    __plugin_dir = 'plugins'
    __type = 'data/json/type.json'
    __index = 'data/json/index.json'
    setupPath = None

    def __init__(self):
        self.setupPath = 'server'
        # self.__plugin_dir = public.getRunDir() + '/plugins'

    # 进程是否存在
    def processExists(self, pname, exe=None):
        try:
            if not self.pids:
                self.pids = psutil.pids()
            for pid in self.pids:
                try:
                    p = psutil.Process(pid)
                    if p.name() == pname:
                        if not exe:
                            return True
                        else:
                            if p.exe() == exe:
                                return True
                except:
                    pass
            return False
        except:
            return True

    # 检查是否正在安装
    def checkSetupTask(self, sName):
        if not self.__tasks:
            self.__tasks = public.M('tasks').where(
                "status!=?", ('1',)).field('status,name').select()
        if sName.find('php-') != -1:
            tmp = sName.split('-')
            sName = tmp[0]
            version = tmp[1]
        isTask = '1'
        for task in self.__tasks:
            tmpt = public.getStrBetween('[', ']', task['name'])
            if not tmpt:
                continue
            tmp1 = tmpt.split('-')
            name1 = tmp1[0].lower()
            if sName == 'php':
                if name1 == sName and tmp1[1] == version:
                    isTask = task['status']
            else:
                if name1 == 'pure':
                    name1 = 'pure-ftpd'
                if name1 == sName:
                    isTask = task['status']
        return isTask

    def checkStatus(self, info):
        pass

     # 构造本地插件信息
    def getPluginInfo(self, info):
        checks = ''
        if info["checks"][0:1] == '/':
            checks = info["checks"]
        else:
            checks = public.getRootDir() + '/' + info['checks']

        pluginInfo = {
            "id": 10000,
            "pid": info['pid'],
            "type": 1000,
            "name": info['name'],
            "title": info['title'],
            "ps": info['ps'],
            "dependnet": "",
            "mutex": "",
            "install_checks": checks,
            "uninsatll_checks": checks,
            "versions": info['versions'],
            # "updates": info['updates'],
            "setup": False,
            "status": False,
        }

        pluginInfo['task'] = self.checkSetupTask(pluginInfo['name'])

        if checks.find('VERSION') > -1:
            pluginInfo['install_checks'] = checks.replace(
                'VERSION', info['versions'])

        pluginInfo['setup'] = os.path.exists(pluginInfo['install_checks'])
        pluginInfo['status'] = os.path.exists(pluginInfo['install_checks'])
        return pluginInfo

    def getAllList(self, sType='0'):
        ret = {}
        ret['type'] = json.loads(public.readFile(self.__type))
        plugins_info = []

        for dirinfo in os.listdir(self.__plugin_dir):
            if dirinfo[0:1] == '.':
                continue

            path = self.__plugin_dir + '/' + dirinfo

            if os.path.isdir(path):
                json_file = path + '/info.json'
                if os.path.exists(json_file):
                    try:
                        data = json.loads(public.readFile(json_file))
                        if type(data['versions']) == list and data['name'] == 'php':
                            for index in range(len(data['versions'])):
                                tmp = data.copy()
                                tmp['title'] = tmp['title'] + \
                                    '-' + data['versions'][index]
                                tmp['versions'] = data['versions'][index]
                                pg = self.getPluginInfo(tmp)
                                if sType == '0':
                                    plugins_info.append(pg)
                                else:
                                    if pg['pid'] == sType:
                                        plugins_info.append(pg)
                        else:
                            pg = self.getPluginInfo(data)
                            if sType == '0':
                                plugins_info.append(pg)
                            else:
                                if pg['pid'] == sType:
                                    plugins_info.append(pg)
                    except Exception, e:
                        print e
                        # pass

        return plugins_info

    def getPluginList(self, sType, sPage=1, sPageSize=15):

        ret = {}
        ret['type'] = json.loads(public.readFile(self.__type))
        plugins_info = self.getAllList(sType)
        args = {}
        args['count'] = len(plugins_info)
        args['p1'] = sPage

        ret['data'] = plugins_info
        ret['list'] = public.getPage(args)
        return ret

    def addIndex(self, name, version):
        pass

    def run(self):
        pass
