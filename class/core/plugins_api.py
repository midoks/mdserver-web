# coding: utf-8

import psutil
import time
import os
import public
import re
import json

import threading
import multiprocessing

from flask import request


class pa_thread(threading.Thread):

    def __init__(self, func, args, name=''):
        threading.Thread.__init__(self)
        self.name = name
        self.func = func
        self.args = args
        self.result = self.func(*self.args)

    def getResult(self):
        try:
            return self.result
        except Exception:
            return None


class plugins_api:
    __tasks = None
    __plugin_dir = 'plugins'
    __type = 'data/json/type.json'
    __index = 'data/json/index.json'
    setupPath = None

    def __init__(self):
        self.setupPath = 'server'

    ##### ----- start ----- ###
    def listApi(self):
        sType = request.args.get('type', '0')
        sPage = request.args.get('p', '1')
        print sPage
        data = self.getPluginList(sType, int(sPage))
        return public.getJson(data)

    def fileApi(self):
        name = request.args.get('name', '')
        if name.strip() == '':
            return ''

        f = request.args.get('f', '')
        if f.strip() == '':
            return ''

        file = self.__plugin_dir + '/' + name + '/' + f
        if not os.path.exists(file):
            return ''

        c = public.readFile(file)
        return c

    def indexListApi(self):
        data = self.getIndexList()
        return public.getJson(data)

    def indexSortApi(self):
        sort = request.form.get('ssort', '')
        if sort.strip() == '':
            return public.returnJson(False, '排序数据不能为空!')
        data = self.setIndexSort(sort)
        if data:
            return public.returnJson(True, '成功!')
        return public.returnJson(False, '失败!')

    def installApi(self):
        rundir = public.getRunDir()
        name = request.form.get('name', '')
        version = request.form.get('version', '')

        mmsg = '安装'
        if hasattr(request.form, 'upgrade'):
            mtype = 'update'
            mmsg = 'upgrade'

        if name.strip() == '':
            return public.returnJson(False, '缺少插件名称!', ())

        if version.strip() == '':
            return public.returnJson(False, '缺少版本信息!', ())

        infoJsonPos = self.__plugin_dir + '/' + name + '/' + 'info.json'
        print infoJsonPos

        if not os.path.exists(infoJsonPos):
            return public.retJson(False, '配置文件不存在!', ())

        pluginInfo = json.loads(public.readFile(infoJsonPos))

        execstr = "cd " + os.getcwd() + "/plugins/" + \
            name + " && /bin/bash " + pluginInfo["shell"] \
            + " install " + version

        taskAdd = (None, mmsg + '[' + name + '-' + version + ']',
                   'execshell', '0', time.strftime('%Y-%m-%d %H:%M:%S'), execstr)

        public.M('tasks').add('id,name,type,status,addtime, execstr', taskAdd)
        return public.returnJson(True, '已将安装任务添加到队列!')

    def uninstallApi(self):
        rundir = public.getRunDir()
        name = request.form.get('name', '')
        version = request.form.get('version', '')
        if name.strip() == '':
            return public.returnJson(False, "缺少插件名称!", ())

        if version.strip() == '':
            return public.returnJson(False, "缺少版本信息!", ())

        infoJsonPos = __plugin_name + '/' + name + '/' + 'info.json'

        if not os.path.exists(infoJsonPos):
            return public.retJson(False, "配置文件不存在!", ())

        pluginInfo = json.loads(public.readFile(infoJsonPos))

        execstr = "cd " + os.getcwd() + "/plugins/" + \
            name + " && /bin/bash " + pluginInfo["shell"] \
            + " uninstall " + version

        taskAdd = (None, '卸载[' + name + '-' + version + ']',
                   'execshell', '0', time.strftime('%Y-%m-%d %H:%M:%S'), execstr)

        public.M('tasks').add('id,name,type,status,addtime, execstr', taskAdd)
        return public.returnJson(True, '已将卸载任务添加到队列!')

    def installed(self):
        rundir = public.getRunDir()
        name = request.form.get('name', '')

        if name.strip() == '':
            return public.retJson(-1, "缺少插件名称!", ())

        infoJsonPos = __plugin_name + '/' + name + '/' + 'info.json'
        if not os.path.exists(infoJsonPos):
            return public.returnJson(-1, "配置文件不存在!", ())

        pluginInfo = json.loads(public.readFile(infoJsonPos))

        sh = __plugin_name + '/' + name + '/' + pluginInfo['shell']
        os.system('/bin/bash ' + sh + ' install')
        print request.args
        return ''

    def checkInstalled(self):
        checks = ['nginx', 'apache', 'php', 'mysql']
        for name in checks:
            filename = public.getRootDir() + "/server/" + name
            if os.path.exists(filename):
                return "True"
        return "False"

    def setIndexApi(self):
        name = request.form.get('name', '')
        status = request.form.get('status', '0')
        version = request.form.get('version', '')
        if status == '1':
            return self.addIndex(name, version)
        return self.removeIndex(name, version)

    def settingApi(self):
        name = request.args.get('name', '')
        html = self.__plugin_dir + '/' + name + '/index.html'
        return public.readFile(html)

    def runApi(self):
        name = request.form.get('name', '')
        func = request.form.get('func', '')
        version = request.form.get('version', '')
        args = request.form.get('args', '')
        script = request.form.get('script', 'index')

        data = self.run(name, func, version, args, script)
        if data[1] == '':
            return public.returnJson(True, "OK", data[0].strip())
        return public.returnJson(False, data[1].strip())

    ##### ----- end ----- ###

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

        if not info['setup']:
            return False

        data = self.run(info['name'], 'status', info['setup_version'])
        if data[0] == 'start':
            return True
        return False

    def checkStatusProcess(self, info, i, return_dict):

        if not info['setup']:
            return_dict[i] = False
            return

        data = self.run(info['name'], 'status', info['setup_version'])
        if data[0] == 'start':
            return_dict[i] = True
        else:
            return_dict[i] = False

    def checkStatusMProcess(self, plugins_info):
        manager = multiprocessing.Manager()
        return_dict = manager.dict()
        jobs = []
        ntmp_list = range(len(plugins_info))
        for i in ntmp_list:
            p = multiprocessing.Process(
                target=self.checkStatusProcess, args=(plugins_info[i], i, return_dict))
            jobs.append(p)
            p.start()

        for proc in jobs:
            proc.join()

        returnData = return_dict.values()
        for i in ntmp_list:
            plugins_info[i]['status'] = returnData[i]

        return plugins_info

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
        # pluginInfo['status'] = self.checkStatus(pluginInfo)
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

    def getAllListPage(self, sType='0', page=1, pageSize=10):
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

        start = (page - 1) * pageSize
        end = start + pageSize
        _plugins_info = plugins_info[start:end]

        _plugins_info = self.checkStatusMProcess(_plugins_info)
        return (_plugins_info, len(plugins_info))

    def makeListThread(self, data, sType='0'):
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

    def getAllListThread(self, sType='0'):
        plugins_info = []
        tmp_list = []
        threads = []
        for dirinfo in os.listdir(self.__plugin_dir):
            if dirinfo[0:1] == '.':
                continue
            path = self.__plugin_dir + '/' + dirinfo
            if os.path.isdir(path):
                json_file = path + '/info.json'
                if os.path.exists(json_file):
                    data = json.loads(public.readFile(json_file))
                    if sType == '0':
                        tmp_list.append(data)

                    if (data['pid'] == sType):
                        tmp_list.append(data)

        ntmp_list = range(len(tmp_list))
        for i in ntmp_list:
            t = pa_thread(self.makeListThread, (tmp_list[i], sType))
            threads.append(t)
        for i in ntmp_list:
            threads[i].start()
        for i in ntmp_list:
            threads[i].join()

        for i in ntmp_list:
            t = threads[i].getResult()
            for index in range(len(t)):
                plugins_info.append(t[index])

        return plugins_info

    def makeListProcess(self, data, sType, i, return_dict):
        plugins_info = []

        if (data['pid'] == sType):
            if type(data['versions']) == list and data.has_key('coexist') and data['coexist']:
                tmp_data = self.makeCoexist(data)
                for index in range(len(tmp_data)):
                    plugins_info.append(tmp_data[index])
            else:
                pg = self.getPluginInfo(data)
                plugins_info.append(pg)
            # return plugins_info

        if sType == '0':
            if type(data['versions']) == list and data.has_key('coexist') and data['coexist']:
                tmp_data = self.makeCoexist(data)
                for index in range(len(tmp_data)):
                    plugins_info.append(tmp_data[index])
            else:
                pg = self.getPluginInfo(data)
                plugins_info.append(pg)

        return_dict[i] = plugins_info
        # return plugins_info

    def getAllListProcess(self, sType='0'):
        plugins_info = []
        tmp_list = []
        manager = multiprocessing.Manager()
        return_dict = manager.dict()
        jobs = []
        for dirinfo in os.listdir(self.__plugin_dir):
            if dirinfo[0:1] == '.':
                continue
            path = self.__plugin_dir + '/' + dirinfo
            if os.path.isdir(path):
                json_file = path + '/info.json'
                if os.path.exists(json_file):
                    data = json.loads(public.readFile(json_file))
                    if sType == '0':
                        tmp_list.append(data)

                    if (data['pid'] == sType):
                        tmp_list.append(data)

        ntmp_list = range(len(tmp_list))
        for i in ntmp_list:
            p = multiprocessing.Process(
                target=self.makeListProcess, args=(tmp_list[i], sType, i, return_dict))
            jobs.append(p)
            p.start()

        for proc in jobs:
            proc.join()

        returnData = return_dict.values()
        for i in ntmp_list:
            for index in range(len(returnData[i])):
                plugins_info.append(returnData[i][index])

        return plugins_info

    def getPluginList(self, sType, sPage=1, sPageSize=10):
        print sType, sPage, sPageSize

        ret = {}
        ret['type'] = json.loads(public.readFile(self.__type))
        # plugins_info = self.getAllListThread(sType)
        # plugins_info = self.getAllListProcess(sType)
        data = self.getAllListPage(sType, sPage, sPageSize)
        ret['data'] = data[0]

        args = {}
        args['count'] = data[1]
        args['p'] = sPage
        args['tojs'] = 'getSList'
        args['row'] = sPageSize

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

        plist = self.checkStatusMProcess(plist)
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

        if not os.path.exists(path):
            return ('', '')
        data = public.execShell(py_cmd)

        print py_cmd
        # print os.path.exists(py_cmd)
        return (data[0].strip(), data[1].strip())
