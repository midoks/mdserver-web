# coding: utf-8

import psutil
import time
import os
import mw
import re
import json

import sys
# reload(sys)
# sys.setdefaultencoding('utf8')

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
        # print sPage
        data = self.getPluginList(sType, int(sPage))
        return mw.getJson(data)

    def fileApi(self):
        name = request.args.get('name', '')
        if name.strip() == '':
            return ''

        f = request.args.get('f', '')
        if f.strip() == '':
            return ''

        file = mw.getPluginDir() + '/' + name + '/' + f
        if not os.path.exists(file):
            return ''

        c = open(file, 'rb').read()
        return c

    def indexListApi(self):
        data = self.getIndexList()
        return mw.getJson(data)

    def indexSortApi(self):
        sort = request.form.get('ssort', '')
        if sort.strip() == '':
            return mw.returnJson(False, '排序数据不能为空!')
        data = self.setIndexSort(sort)
        if data:
            return mw.returnJson(True, '成功!')
        return mw.returnJson(False, '失败!')

    def installApi(self):
        rundir = mw.getRunDir()
        name = request.form.get('name', '')
        version = request.form.get('version', '')

        mmsg = '安装'
        if hasattr(request.form, 'upgrade'):
            mtype = 'update'
            mmsg = 'upgrade'

        if name.strip() == '':
            return mw.returnJson(False, '缺少插件名称!', ())

        if version.strip() == '':
            return mw.returnJson(False, '缺少版本信息!', ())

        infoJsonPos = self.__plugin_dir + '/' + name + '/' + 'info.json'
        # print infoJsonPos

        if not os.path.exists(infoJsonPos):
            return mw.returnJson(False, '配置文件不存在!', ())

        pluginInfo = json.loads(mw.readFile(infoJsonPos))

        execstr = "cd " + os.getcwd() + "/plugins/" + \
            name + " && /bin/bash " + pluginInfo["shell"] \
            + " install " + version

        if mw.isAppleSystem():
            print(execstr)

        taskAdd = (None, mmsg + '[' + name + '-' + version + ']',
                   'execshell', '0', time.strftime('%Y-%m-%d %H:%M:%S'), execstr)

        mw.M('tasks').add('id,name,type,status,addtime, execstr', taskAdd)
        return mw.returnJson(True, '已将安装任务添加到队列!')

    def uninstallOldApi(self):
        rundir = mw.getRunDir()
        name = request.form.get('name', '')
        version = request.form.get('version', '')
        if name.strip() == '':
            return mw.returnJson(False, "缺少插件名称!", ())

        if version.strip() == '':
            return mw.returnJson(False, "缺少版本信息!", ())

        infoJsonPos = self.__plugin_dir + '/' + name + '/' + 'info.json'

        if not os.path.exists(infoJsonPos):
            return mw.returnJson(False, "配置文件不存在!", ())

        pluginInfo = json.loads(mw.readFile(infoJsonPos))

        execstr = "cd " + os.getcwd() + "/plugins/" + \
            name + " && /bin/bash " + pluginInfo["shell"] \
            + " uninstall " + version

        taskAdd = (None, '卸载[' + name + '-' + version + ']',
                   'execshell', '0', time.strftime('%Y-%m-%d %H:%M:%S'), execstr)

        mw.M('tasks').add('id,name,type,status,addtime, execstr', taskAdd)
        return mw.returnJson(True, '已将卸载任务添加到队列!')

    # 卸载时间短,不加入任务中...
    def uninstallApi(self):
        rundir = mw.getRunDir()
        name = request.form.get('name', '')
        version = request.form.get('version', '')
        if name.strip() == '':
            return mw.returnJson(False, "缺少插件名称!", ())

        if version.strip() == '':
            return mw.returnJson(False, "缺少版本信息!", ())

        infoJsonPos = self.__plugin_dir + '/' + name + '/' + 'info.json'

        if not os.path.exists(infoJsonPos):
            return mw.returnJson(False, "配置文件不存在!", ())

        pluginInfo = json.loads(mw.readFile(infoJsonPos))

        execstr = "cd " + os.getcwd() + "/plugins/" + \
            name + " && /bin/bash " + pluginInfo["shell"] \
            + " uninstall " + version

        data = mw.execShell(execstr)
        if mw.isAppleSystem():
            print(execstr)
            print(data[0], data[1])
        self.removeIndex(name, version)
        return mw.returnJson(True, '卸载执行成功!')
        # if data[1] == '':
        #     return mw.returnJson(True, '已将卸载成功!')
        # else:
        #     return mw.returnJson(False, '卸载出现错误信息!' + data[1])

    def checkApi(self):
        name = request.form.get('name', '')
        if name.strip() == '':
            return mw.returnJson(False, "缺少插件名称!", ())

        infoJsonPos = self.__plugin_dir + '/' + name + '/' + 'info.json'
        if not os.path.exists(infoJsonPos):
            return mw.returnJson(False, "配置文件不存在!", ())
        return mw.returnJson(True, "插件存在!", ())

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
        return mw.readFile(html)

    def runApi(self):
        name = request.form.get('name', '')
        func = request.form.get('func', '')
        version = request.form.get('version', '')
        args = request.form.get('args', '')
        script = request.form.get('script', 'index')

        data = self.run(name, func, version, args, script)
        if data[1] == '':
            r = mw.returnJson(True, "OK", data[0].strip())
        else:
            r = mw.returnJson(False, data[1].strip())
        return r

    def callbackApi(self):
        name = request.form.get('name', '')
        func = request.form.get('func', '')
        args = request.form.get('args', '')
        script = request.form.get('script', 'index')

        data = self.callback(name, func, args, script)
        if data[0]:
            return mw.returnJson(True, "OK", data[1])
        return mw.returnJson(False, data[1])

    def updateZipApi(self):
        tmp_path = mw.getRootDir() + '/temp'
        if not os.path.exists(tmp_path):
            os.makedirs(tmp_path)
        mw.execShell("rm -rf " + tmp_path + '/*')

        tmp_file = tmp_path + '/plugin_tmp.zip'
        from werkzeug.utils import secure_filename
        from flask import request
        f = request.files['plugin_zip']
        if f.filename[-4:] != '.zip':
            return mw.returnJson(False, '仅支持zip文件!')
        f.save(tmp_file)
        mw.execShell('cd ' + tmp_path + ' && unzip ' + tmp_file)
        os.remove(tmp_file)

        p_info = tmp_path + '/info.json'
        if not os.path.exists(p_info):
            d_path = None
            for df in os.walk(tmp_path):
                if len(df[2]) < 3:
                    continue
                if not 'info.json' in df[2]:
                    continue
                if not 'install.sh' in df[2]:
                    continue
                if not os.path.exists(df[0] + '/info.json'):
                    continue
                d_path = df[0]
            if d_path:
                tmp_path = d_path
                p_info = tmp_path + '/info.json'
        try:
            data = json.loads(mw.readFile(p_info))
            data['size'] = mw.getPathSize(tmp_path)
            if not 'author' in data:
                data['author'] = '未知'
            if not 'home' in data:
                data['home'] = 'https://www.bt.cn/bbs/forum-40-1.html'
            plugin_path = mw.getPluginDir() + data['name'] + '/info.json'
            data['old_version'] = '0'
            data['tmp_path'] = tmp_path
            if os.path.exists(plugin_path):
                try:
                    old_info = json.loads(mw.ReadFile(plugin_path))
                    data['old_version'] = old_info['versions']
                except:
                    pass
        except:
            mw.execShell("rm -rf " + tmp_path)
            return mw.returnJson(False, '在压缩包中没有找到插件信息,请检查插件包!')
        protectPlist = ('openresty', 'mysql', 'php', 'csvn', 'gogs', 'pureftp')
        if data['name'] in protectPlist:
            return mw.returnJson(False, '[' + data['name'] + '],重要插件不可修改!')
        return mw.getJson(data)

    def inputZipApi(self):
        plugin_name = request.form.get('plugin_name', '')
        tmp_path = request.form.get('tmp_path', '')

        if not os.path.exists(tmp_path):
            return mw.returnJson(False, '临时文件不存在,请重新上传!')
        plugin_path = mw.getPluginDir() + '/' + plugin_name
        if not os.path.exists(plugin_path):
            print(mw.execShell('mkdir -p ' + plugin_path))
        mw.execShell("\cp -rf " + tmp_path + '/* ' + plugin_path + '/')
        mw.execShell('chmod -R 755 ' + plugin_path)
        p_info = mw.readFile(plugin_path + '/info.json')
        if p_info:
            mw.writeLog('软件管理', '安装第三方插件[%s]' %
                        json.loads(p_info)['title'])
            return mw.returnJson(True, '安装成功!')
        mw.execShell("rm -rf " + plugin_path)
        return mw.returnJson(False, '安装失败!')
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
    def checkSetupTask(self, sName, sVer, sCoexist):
        if not self.__tasks:
            self.__tasks = mw.M('tasks').where(
                "status!=?", ('1',)).field('status,name').select()
        isTask = '1'
        for task in self.__tasks:
            tmpt = mw.getStrBetween('[', ']', task['name'])
            if not tmpt:
                continue
            tmp1 = tmpt.split('-')
            name1 = tmp1[0].lower()
            if sCoexist:
                if name1 == sName and tmp1[1] == sVer:
                    isTask = task['status']
            else:
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

    def checkStatusThreads(self, info, i):
        if not info['setup']:
            return False
        data = self.run(info['name'], 'status', info['setup_version'])
        if data[0] == 'start':
            return True
        else:
            return False

    def checkStatusMThreads(self, plugins_info):
        try:
            threads = []
            ntmp_list = range(len(plugins_info))
            for i in ntmp_list:
                t = pa_thread(self.checkStatusThreads, (plugins_info[i], i))
                threads.append(t)

            for i in ntmp_list:
                threads[i].start()
            for i in ntmp_list:
                threads[i].join()

            for i in ntmp_list:
                t = threads[i].getResult()
                plugins_info[i]['status'] = t
        except Exception as e:
            print('checkStatusMThreads:', str(e))

        return plugins_info

    def checkStatusMProcess(self, plugins_info):
        manager = multiprocessing.Manager()
        return_dict = manager.dict()
        jobs = []
        for i in range(len(plugins_info)):
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
            mw.writeFile(self.__index, '[]')

        indexList = json.loads(mw.readFile(self.__index))
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
            return mw.readFile(version_f).strip()
        return ''

     # 构造本地插件信息
    def getPluginInfo(self, info):
        checks = ''
        path = ''
        coexist = False

        if info["checks"][0:1] == '/':
            checks = info["checks"]
        else:
            checks = mw.getRootDir() + '/' + info['checks']

        if 'path' in info:
            path = info['path']

        if path[0:1] != '/':
            path = mw.getRootDir() + '/' + path

        if 'coexist' in info and info['coexist']:
            coexist = True

        pInfo = {
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

        if checks.find('VERSION') > -1:
            pInfo['install_checks'] = checks.replace(
                'VERSION', info['versions'])

        if path.find('VERSION') > -1:
            pInfo['path'] = path.replace(
                'VERSION', info['versions'])

        pInfo['task'] = self.checkSetupTask(
            pInfo['name'], info['versions'], coexist)
        pInfo['display'] = self.checkDisplayIndex(
            info['name'], pInfo['versions'])

        pInfo['setup'] = os.path.exists(pInfo['install_checks'])

        if coexist and pInfo['setup']:
            pInfo['setup_version'] = info['versions']
        else:
            pInfo['setup_version'] = self.getVersion(pInfo['install_checks'])
        # pluginInfo['status'] = self.checkStatus(pluginInfo)
        pInfo['status'] = False
        return pInfo

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
            if type(data['versions']) == list and 'coexist' in data and data['coexist']:
                tmp_data = self.makeCoexist(data)
                for index in range(len(tmp_data)):
                    plugins_info.append(tmp_data[index])
            else:
                pg = self.getPluginInfo(data)
                plugins_info.append(pg)
            return plugins_info

        if sType == '0':
            if type(data['versions']) == list and 'coexist' in data and data['coexist']:
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
                        data = json.loads(mw.readFile(json_file))
                        tmp_data = self.makeList(data, sType)
                        for index in range(len(tmp_data)):
                            plugins_info.append(tmp_data[index])
                    except Exception as e:
                        print(e)
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
                        data = json.loads(mw.readFile(json_file))
                        tmp_data = self.makeList(data, sType)
                        for index in range(len(tmp_data)):
                            plugins_info.append(tmp_data[index])
                    except Exception as e:
                        print(e)

        start = (page - 1) * pageSize
        end = start + pageSize
        _plugins_info = plugins_info[start:end]

        _plugins_info = self.checkStatusMThreads(_plugins_info)
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
                    data = json.loads(mw.readFile(json_file))
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
                    data = json.loads(mw.readFile(json_file))
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
        # print sType, sPage, sPageSize

        ret = {}
        ret['type'] = json.loads(mw.readFile(self.__type))
        # plugins_info = self.getAllListThread(sType)
        # plugins_info = self.getAllListProcess(sType)
        data = self.getAllListPage(sType, sPage, sPageSize)
        ret['data'] = data[0]

        args = {}
        args['count'] = data[1]
        args['p'] = sPage
        args['tojs'] = 'getSList'
        args['row'] = sPageSize

        ret['list'] = mw.getPage(args)
        return ret

    def getIndexList(self):
        if not os.path.exists(self.__index):
            mw.writeFile(self.__index, '[]')

        indexList = json.loads(mw.readFile(self.__index))
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
                        content = mw.readFile(json_file)
                        if content:
                            data = json.loads(content)
                            tmp_data = self.makeList(data)
                            for index in range(len(tmp_data)):
                                if tmp_data[index]['versions'] == info[1] or info[1] in tmp_data[index]['versions']:
                                    tmp_data[index]['display'] = True
                                    plist.append(tmp_data[index])
                                    continue
                    except Exception as e:
                        # raise e
                        print('getIndexList:', e)

        # 使用gevent模式时,无法使用多进程
        #plist = self.checkStatusMProcess(plist)
        plist = self.checkStatusMThreads(plist)
        return plist

    def setIndexSort(self, sort):
        data = sort.split('|')
        mw.writeFile(self.__index, json.dumps(data))
        return True

    def addIndex(self, name, version):
        if not os.path.exists(self.__index):
            mw.writeFile(self.__index, '[]')

        indexList = json.loads(mw.readFile(self.__index))
        vname = name + '-' + version

        if vname in indexList:
            return mw.returnJson(False, '请不要重复添加!')
        if len(indexList) > 12:
            return mw.returnJson(False, '首页最多只能显示12个软件!')

        indexList.append(vname)
        mw.writeFile(self.__index, json.dumps(indexList))
        return mw.returnJson(True, '添加成功!')

    def removeIndex(self, name, version):
        if not os.path.exists(self.__index):
            mw.writeFile(self.__index, '[]')

        indexList = json.loads(mw.readFile(self.__index))
        vname = name + '-' + version
        if not vname in indexList:
            return mw.returnJson(True, '删除成功!')
        indexList.remove(vname)
        mw.writeFile(self.__index, json.dumps(indexList))
        return mw.returnJson(True, '删除成功!')

    # shell 调用
    def run(self, name, func, version, args='', script='index'):
        path = mw.getRunDir() + '/' + self.__plugin_dir + \
            '/' + name + '/' + script + '.py'
        py = 'python3 ' + path

        if args == '':
            py_cmd = py + ' ' + func + ' ' + version
        else:
            py_cmd = py + ' ' + func + ' ' + version + ' ' + args

        if not os.path.exists(path):
            return ('', '')
        data = mw.execShell(py_cmd)

        if mw.isAppleSystem():
            print('run', py_cmd)
            print(data)
        # print os.path.exists(py_cmd)

        return (data[0].strip(), data[1].strip())

    # 映射包调用
    def callback(self, name, func, args='', script='index'):
        package = mw.getRunDir() + '/plugins/' + name
        if not os.path.exists(package):
            return (False, "插件不存在!")

        sys.path.append(package)
        eval_str = "__import__('" + script + "')." + func + '(' + args + ')'
        newRet = eval(eval_str)
        if mw.isAppleSystem():
            print('callback', eval_str)

        return (True, newRet)
