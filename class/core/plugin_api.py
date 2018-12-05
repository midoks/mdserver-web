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

        data = self.run(info['name'], 'status', info['setup_version'])
        if data[0] == 'start':
            return True
        return False

    def checkDisplayIndex(self, name, version):
        if not os.path.exists(self.__index):
            public.writeFile(self.__index, '[]')

        indexList = json.loads(public.readFile(self.__index))
        if type(version) == list:
            for index in range(len(version)):
                vname = name + '-' + version[index]
                if vname in indexList:
                    return True
        else:
            vname = name + '-' + version
            if vname in indexList:
                return True
        return False

    def getVersion(self, path):
        version_f = path + '/version.pl'
        if os.path.exists(version_f):
            return public.readFile(version_f).strip()
        return ''

     # 构造本地插件信息
    def getPluginInfo(self, info):
        checks = ''
        path = ''
        coexist = False

        if info["checks"][0:1] == '/':
            checks = info["checks"]
        else:
            checks = public.getRootDir() + '/' + info['checks']

        if info.has_key('path'):
            path = info['path']

        if path[0:1] != '/':
            path = public.getRootDir() + '/' + path

        if info.has_key('coexist') and info['coexist']:
            coexist = True

        pluginInfo = {
            "id": 10000,
            "pid": info['pid'],
            "type": 1000,
            "name": info['name'],
            "title": info['title'],
            "ps": info['ps'],
            "dependnet": "",
            "mutex": "",
            "path": path,
            "install_checks": checks,
            "uninsatll_checks": checks,
            "coexist": coexist,
            "versions": info['versions'],
            # "updates": info['updates'],
            "display": False,
            "setup": False,
            "setup_version": "",
            "status": False,
        }

        pluginInfo['task'] = self.checkSetupTask(pluginInfo['name'])

        if checks.find('VERSION') > -1:
            pluginInfo['install_checks'] = checks.replace(
                'VERSION', info['versions'])

        if path.find('VERSION') > -1:
            pluginInfo['path'] = path.replace(
                'VERSION', info['versions'])

        pluginInfo['display'] = self.checkDisplayIndex(
            info['name'], pluginInfo['versions'])

        pluginInfo['setup'] = os.path.exists(pluginInfo['install_checks'])

        if coexist and pluginInfo['setup']:
            pluginInfo['setup_version'] = info['versions']
        else:
            pluginInfo['setup_version'] = self.getVersion(
                pluginInfo['install_checks'])
        pluginInfo['status'] = self.checkStatus(pluginInfo)
        return pluginInfo

    def makeCoexist(self, data):
        plugins_info = []
        for index in range(len(data['versions'])):
            tmp = data.copy()
            tmp['title'] = tmp['title'] + \
                '-' + data['versions'][index]
            tmp['versions'] = data['versions'][index]
            pg = self.getPluginInfo(tmp)
            plugins_info.append(pg)

        return plugins_info

    def makeList(self, data, sType='0'):
        plugins_info = []

        if (data['pid'] == sType):
            if type(data['versions']) == list and data.has_key('coexist') and data['coexist']:
                tmp_data = self.makeCoexist(data)
                for index in range(len(tmp_data)):
                    plugins_info.append(tmp_data[index])
            else:
                pg = self.getPluginInfo(data)
                plugins_info.append(pg)
            return plugins_info

        if sType == '0':
            if type(data['versions']) == list and data.has_key('coexist') and data['coexist']:
                tmp_data = self.makeCoexist(data)
                for index in range(len(tmp_data)):
                    plugins_info.append(tmp_data[index])
            else:
                pg = self.getPluginInfo(data)
                plugins_info.append(pg)

        # print plugins_info, data
        return plugins_info

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
                        tmp_data = self.makeList(data, sType)
                        for index in range(len(tmp_data)):
                            plugins_info.append(tmp_data[index])
                    except Exception, e:
                        print e
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

    def getIndexList(self):
        if not os.path.exists(self.__index):
            public.writeFile(self.__index, '[]')

        indexList = json.loads(public.readFile(self.__index))

        plist = []
        app = []
        for i in indexList:
            info = i.split('-')
            if not info[0] in app:
                app.append(info[0])
            path = self.__plugin_dir + '/' + info[0]
            if os.path.isdir(path):
                json_file = path + '/info.json'
                if os.path.exists(json_file):
                    try:
                        data = json.loads(public.readFile(json_file))
                        tmp_data = self.makeList(data)
                        for index in range(len(tmp_data)):
                            if tmp_data[index]['versions'] == info[1] or info[1] in tmp_data[index]['versions']:
                                tmp_data[index]['display'] = True
                                plist.append(tmp_data[index])
                                continue
                    except Exception, e:
                        print e
        return plist

    def setIndexSort(self, sort):
        data = sort.split('|')
        public.writeFile(self.__index, json.dumps(data))
        return True

    def addIndex(self, name, version):
        if not os.path.exists(self.__index):
            public.writeFile(self.__index, '[]')

        indexList = json.loads(public.readFile(self.__index))
        vname = name + '-' + version

        if vname in indexList:
            return public.returnJson(False, '请不要重复添加!')
        if len(indexList) >= 12:
            return public.returnJson(False, '首页最多只能显示12个软件!')

        indexList.append(vname)
        public.writeFile(self.__index, json.dumps(indexList))
        return public.returnJson(True, '添加成功!')

    def removeIndex(self, name, version):
        if not os.path.exists(self.__index):
            public.writeFile(self.__index, '[]')

        indexList = json.loads(public.readFile(self.__index))
        vname = name + '-' + version
        if not vname in indexList:
            return public.returnJson(True, '删除成功!')
        indexList.remove(vname)
        public.writeFile(self.__index, json.dumps(indexList))
        return public.returnJson(True, '删除成功!')

    def run(self, name, func, version, args='', script='index'):
        path = public.getRunDir() + '/' + self.__plugin_dir + \
            '/' + name + '/' + script + '.py'
        py = 'python ' + path
        if args == '':
            py_cmd = py + ' ' + func + ' ' + version
        else:
            py_cmd = py + ' ' + func + ' ' + version + ' ' + args

        # print path
        # print os.path.exists(path)

        if not os.path.exists(path):
            return ('', '')
        data = public.execShell(py_cmd)
        return (data[0].strip(), data[1].strip())
