# coding: utf-8

import psutil
import time
import os
import public
import re
import json


class plugin:
    __tasks = None
    __plugin_dir = "plugins"
    __type = "data/type.json"
    setupPath = None

    def __init__(self):
        self.setupPath = 'server'

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
        # print info["checks"]

        checks = ""
        if info["checks"][0:1] == "/":
            checks = info["checks"]
        else:
            checks = public.getRootDir() + "/" + info['checks']

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
        pluginInfo['setup'] = os.path.exists(pluginInfo['install_checks'])
        pluginInfo['status'] = os.path.exists(pluginInfo['install_checks'])
        return pluginInfo

    def getPluginList(self, sType, sPage=1, sPageSize=15):

        ret = {}
        ret['type'] = json.loads(public.readFile(self.__type))
        plugins_info = []
        for dirinfo in os.listdir(self.__plugin_dir):
            path = self.__plugin_dir + '/' + dirinfo
            if os.path.isdir(path):
                jsonFile = path + '/info.json'
                if os.path.exists(jsonFile):
                    try:
                        tmp = json.loads(public.readFile(jsonFile))
                        if tmp['name'] == 'php':
                            for v in tmp['versions']:
                                pg = self.getPluginInfo(tmp)
                                pg['versions'] = v
                                # print "sss:", i, v
                                # pg['updates'] = tmp["updates"][v]
                                if sType == "0":
                                    plugins_info.append(pg)
                                else:
                                    if pg['pid'] == sType:
                                        plugins_info.append(pg)
                        else:
                            pg = self.getPluginInfo(tmp)
                            if sType == "0":
                                plugins_info.append(pg)
                            else:
                                if pg['pid'] == sType:
                                    plugins_info.append(pg)
                    except Exception, e:
                        print e
        args = {}
        args['count'] = len(plugins_info)
        args['p1'] = sPage

        ret['data'] = plugins_info
        ret['list'] = public.getPage(args)
        return ret
