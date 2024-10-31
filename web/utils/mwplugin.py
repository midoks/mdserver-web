# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------

import os
import sys
import json
import threading
import multiprocessing

from admin import model

import core.mw as mw
import admin.model.option as option

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

class MwPlugin(object):

    def_plugin_type = [
        {
            "title":"全部",
            "type":0,
            "ps":""
        },
        {
            "title":"已安装",
            "type":-1,
            "ps":""
        },
        {
            "title":"运行环境",
            "type":1,
            "ps":""
        },
        {
            "title":"数据软件",
            "type":2,
            "ps":""
        },
        {
            "title":"代码管理",
            "type":3,
            "ps":""
        },
        {
            "title":"系统工具",
            "type":4,
            "ps":""
        },
        {
            "title":"其他插件",
            "type":5,
            "ps":""
        },
        {
            "title":"辅助插件",
            "type":6,
            "ps":""
        }
    ]

    __plugin_dir = 'plugins'
    __index = 'data/json/index.json'
    __index_data = None

    # lock
    _instance_lock = threading.Lock()

    @classmethod
    def instance(cls, *args, **kwargs):
        if not hasattr(MwPlugin, "_instance"):
            with MwPlugin._instance_lock:
                if not hasattr(MwPlugin, "_instance"):
                    MwPlugin._instance = MwPlugin(*args, **kwargs)
        return MwPlugin._instance

    """插件类初始化"""
    def __init__(self):
        self.__plugin_dir = mw.getPluginDir()
        self.__index = mw.getPanelDataDir() + '/json/index.json'
        self.initIndexData()


    def initIndexData(self):
        if not os.path.exists(self.__index):
            mw.writeFile(self.__index, '[]')
        self.__index_data = json.loads(mw.readFile(self.__index))

    def getIndexList(self):
        indexList = option.getOptionByJson('display_index')
        plist = []
        for i in indexList:
            tmp = i.split('-')
            tmp_len = len(tmp)
            plugin_name = tmp[0]
            plugin_ver = tmp[1]
            if tmp_len > 2:
                tmpArr = tmp[0:tmp_len - 1]
                plugin_name = '-'.join(tmpArr)
                plugin_ver = tmp[tmp_len - 1]

            read_json_file = self.__plugin_dir + '/' + plugin_name + '/info.json'
            if os.path.exists(read_json_file):
                content = mw.readFile(read_json_file)
                try:
                    data = json.loads(content)
                    data = self.makeCoexistList(data)
                    for index in range(len(data)):
                        if data[index]['coexist']:
                            if data[index]['versions'] == plugin_ver or plugin_ver in data[index]['versions']:
                                data[index]['display'] = True
                                plist.append(data[index])
                                continue
                        else:
                            data[index]['display'] = True
                            plist.append(data[index])

                except Exception as e:
                    print('getIndexList:', mw.getTracebackInfo())

        # 使用gevent模式时,无法使用多进程
        # plist = self.checkStatusMProcess(plist)
        plist = self.checkStatusMThreads(plist)
        return plist

    def menuGetAbsPath(self, tag, path):
        if path[0:1] == '/':
            return path
        else:
            return mw.getPluginDir() + '/' + tag + '/' + path

    def addIndex(self, name, version):
        vname = name + '-' + version
        indexList = option.getOptionByJson('display_index')
        if vname in indexList:
            return mw.returnData(False, '请不要重复添加!')
        if len(indexList) > 12:
            return mw.returnData(False, '首页最多只能显示12个软件!')

        indexList.append(vname)
        option.setOption('display_index', json.dumps(indexList))
        return mw.returnData(True, '添加成功!')

    def removeIndex(self, name, version):
        vname = name + '-' + version
        indexList = option.getOptionByJson('display_index')
        if not vname in indexList:
            return mw.returnData(True, '删除成功!!')
        indexList.remove(vname)

        print(indexList)
        option.setOption('display_index', json.dumps(indexList))
        return mw.returnData(True, '删除成功!')

    def hookInstallOption(self, hook_name, info):
        hn_name = 'hook_'+hook_name
        src_data = option.getOptionByJson(hn_name,type='hook',default=[])
        isNeedAdd = True
        for x in range(len(src_data)):
            if src_data[x]['title'] == info['title'] and src_data[x]['name'] == info['name']:
                isNeedAdd = False

        if isNeedAdd:
            src_data.append(info)

        option.setOption(hn_name, json.dumps(src_data), type='hook')
        return True

    def hookUninstallOption(self, hook_name, info):
        hn_name = 'hook_'+hook_name
        src_data = option.getOptionByJson(hn_name,type='hook',default=[])
        for idx in range(len(src_data)):
            if src_data[idx]['name'] == info['name']:
                src_data.remove(src_data[idx])
                break
        option.setOption(hn_name, json.dumps(src_data), type='hook')
        return True

    def hookInstall(self, info):
        valid_hook = ['backup', 'database']
        valid_list_hook = ['menu', 'global_static', 'site_cb']
        if 'hook' in info:
            hooks = info['hook']
            for h in hooks:
                hooks_type = type(h)
                if hooks_type == dict:
                    tag = h['tag']
                    if tag in valid_list_hook:
                        self.hookInstallOption(tag, h[tag])
                elif hooks_type == str:
                    for x in hooks:
                        if x in valid_hook:
                            self.hookInstallOption(x, info)
                            return True
        return False

    def hookUninstall(self, info):
        valid_hook = ['backup', 'database']
        valid_list_hook = ['menu', 'global_static', 'site_cb']
        if 'hook' in info:
            hooks = info['hook']
            for h in hooks:
                hooks_type = type(h)
                if hooks_type == dict:
                    tag = h['tag']
                    if tag in valid_list_hook:
                        self.hookUninstallOption(tag, h[tag])
                elif hooks_type == str:
                    for x in hooks:
                        if x in valid_hook:
                            self.hookUninstallOption(x, info)
                            return True
        return False

    def install(self, name, version,
        upgrade: bool | None = None
    ):
        if name.strip() == '':
            return mw.returnData(False, '缺少插件名称!', ())

        if version.strip() == '':
            return mw.returnData(False, '缺少版本信息!', ())

        msg_head = '安装'
        if upgrade is not None and upgrade is True:
            mtype = 'update'
            msg_head = '更新'

        info_file = self.__plugin_dir + '/' + name + '/' + 'info.json'
        if not os.path.exists(info_file):
            return mw.returnData(False, "配置文件不存在!", ())

        info_data = json.loads(mw.readFile(info_file))

        exec_bash = 'cd {0} && bash {1} install {2}'.format(
            mw.getPluginDir() + '/'+name,
            info_data['shell'],
            version
        )

        self.hookInstall(info_data)
        title = '{0}[{1}-{2}]'.format(msg_head,name,version)
        model.addTask(name=title,cmd=exec_bash, status=0)

        # 调式日志
        mw.debugLog(exec_bash)
        return mw.returnData(True, '已将安装任务添加到队列!')

    # 卸载插件
    def uninstall(self, name, version):
        rundir = mw.getRunDir()
        if name.strip() == '':
            return mw.returnData(False, "缺少插件名称!", ())

        if version.strip() == '':
            return mw.returnData(False, "缺少版本信息!", ())

        info_file = self.__plugin_dir + '/' + name + '/' + 'info.json'
        if not os.path.exists(info_file):
            return mw.returnData(False, "配置文件不存在!", ())

        info_data = json.loads(mw.readFile(info_file))

        exec_bash = "cd {0} && /bin/bash {1} uninstall {2}".format(
            mw.getPluginDir() + '/'+name,
            info_data['shell'],
            version
        )
        self.hookUninstall(info_data)
        data = mw.execShell(exec_bash)
        self.removeIndex(name, version)
        mw.debugLog(exec_bash, data)
        return mw.returnData(True, '卸载执行成功!')

    # 插件搜索匹配
    def searchKey(self, info,
        keyword: str | None = None,
    ):
        if keyword == None:
            return True
        try:
            if info['title'].lower().find(keyword) > -1:
                return True
            if info['ps'].lower().find(keyword) > -1:
                return True
            if info['name'].lower().find(keyword) > -1:
                return True
        except Exception as e:
            return False

    def getVersion(self, path):
        version_t = path + '/version.pl'
        if os.path.exists(version_t):
            return mw.readFile(version_t).strip()
        return ''

    def checkIndexList(self, name, version):
        indexList = option.getOptionByJson('display_index')
        for i in indexList:
            t = i.split('-')
            if t[0] == name:
                return True
        return False

    def checkDisplayIndex(self, name, version, coexist):
        indexList = self.__index_data
        if coexist:
            if type(version) == list:
                for index in range(len(version)):
                    vname = name + '-' + version[index]
                    if vname in indexList:
                        return True
            else:
                vname = name + '-' + version
                if vname in indexList:
                    return True
        else:
            if type(version) == list:
                for index in range(len(version)):
                    return self.checkIndexList(name, version)
            else:
                return self.checkIndexList(name, version)
        return False

    def makeCoexist(self, data):
        plugins_info = []
        for index in range(len(data['versions'])):
            data_t = data.copy()
            data_t['title'] = data_t['title'] + '-' + data['versions'][index]
            data_t['versions'] = data['versions'][index]
            pg = self.getPluginInfo(data_t)
            plugins_info.append(pg)

        return plugins_info

    # 构造插件基本信息
    def getPluginInfo(self, info):
        checks = ''
        path = ''
        coexist = False

        if info["checks"].startswith('/'):
            checks = info["checks"]
        else:
            checks = mw.getFatherDir() + '/' + info['checks']

        if 'path' in info:
            path = info['path']

        if not path.startswith('/'):
            path = mw.getFatherDir() + '/' + path

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
            "icon": "",
            "path": path,
            "install_checks": checks,
            "uninsatll_checks": checks,
            "coexist": coexist,
            "versions": info['versions'],
            # "updates": info['updates'],
            "task": True,
            "display": False,
            "setup": False,
            "setup_version": "",
            "status": False,
            "install_pre_inspection": False,
            "uninstall_pre_inspection": False,
        }

        if 'icon' in info:
            pInfo['icon'] = info['icon']

        if checks.find('VERSION') > -1:
            pInfo['install_checks'] = checks.replace('VERSION', info['versions'])

        if path.find('VERSION') > -1:
            pInfo['path'] = path.replace('VERSION', info['versions'])

        pInfo['display'] = self.checkDisplayIndex(info['name'], pInfo['versions'], coexist)
        pInfo['setup'] = os.path.exists(pInfo['install_checks'])



        if coexist and pInfo['setup']:
            pInfo['setup_version'] = info['versions']
        else:
            pInfo['setup_version'] = self.getVersion(pInfo['install_checks'])

        if 'install_pre_inspection' in info:
            pInfo['install_pre_inspection'] = info['install_pre_inspection']
        if 'uninstall_pre_inspection' in info:
            pInfo['uninstall_pre_inspection'] = info['uninstall_pre_inspection']

        return pInfo

    def makeCoexistData(self, data):
        plugins_t = []
        if type(data['versions']) == list and 'coexist' in data and data['coexist']:
            data_t = self.makeCoexist(data)
            for index in range(len(data_t)):
                plugins_t.append(data_t[index])
        else:
            pg = self.getPluginInfo(data)
            plugins_t.append(pg)
        return plugins_t

    # 对多版本共存进行处理
    def makeCoexistList(self, data,
        plugin_type: str | None = None,
    ):
        plugins_t = []
        # 返回指定类型
        if plugin_type != None and data['pid'] == plugin_type:
            return self.makeCoexistData(data)

        # 全部
        if plugin_type == None or plugin_type == '0':
            return self.makeCoexistData(data)
        # 已经安装
        if plugin_type == '-1':
            return self.makeCoexistData(data)
        return plugins_t



    def getPluginList(self, name,
        keyword: str | None = None,
        type: str | None = None,
    ):
        info = []
        path = self.__plugin_dir + '/' + name
        info_path = path + '/info.json'
        if not os.path.exists(info_path):
            return info

        try:
            data = json.loads(mw.readFile(info_path))
        except Exception as e:
            return info
        
        # 判断是否搜索
        if keyword != '' and not self.searchKey(data, keyword):
            return info

        plugin_t = self.makeCoexistList(data, type)
        for index in range(len(plugin_t)):
            info.append(plugin_t[index])
        return info

    # 检查插件状态
    def checkStatusThreads(self, info, i):
        if not info['setup']:
            return False
        data = self.run(info['name'], 'status', info['setup_version'])
        if data[0] == 'start':
            return True
        else:
            return False

    # 多线程检查插件状态
    def checkStatusMThreads(self, info):
        try:
            threads = []
            ntmp_list = range(len(info))
            for i in ntmp_list:
                t = pa_thread(self.checkStatusThreads,(info[i], i))
                threads.append(t)

            for i in ntmp_list:
                threads[i].start()
            for i in ntmp_list:
                threads[i].join()

            for i in ntmp_list:
                t = threads[i].getResult()
                info[i]['status'] = t
        except Exception as e:
            print('checkStatusMThreads:', str(e))

        return info

    def getAllPluginList(
        self,
        type: str | None = None,
        keyword: str | None = None,
        page: int | None = 1, 
        size: int | None = 10, 
    ):
        info = []

        # print(mw.getPluginDir())
        for name in os.listdir(self.__plugin_dir):
            if name.startswith('.'):
                continue
            t = self.getPluginList(name, keyword, type=type)
            for index in range(len(t)):
                info.append(t[index])

        start = (page - 1) * size
        end = start + size
        _info = info[start:end]

        # print(info)

        _info = self.checkStatusMThreads(_info)
        return (_info, len(info))

    def getList(
        self,
        type: str | None = None,
        keyword: str | None = None,
        page: int | None = 1, 
        size: int | None = 10, 
    ) -> object:
        # print(type,keyword,page,size)
        rdata = {}
        rdata['type'] = self.def_plugin_type
    
        data = self.getAllPluginList(type,keyword, page, size)
        rdata['data'] = data[0]

        args = {}
        args['count'] = data[1]
        args['p'] = page
        args['tojs'] = 'getSList'
        args['row'] = size
        rdata['list'] = mw.getPage(args)
        return rdata

    # shell/bash方式调用
    def run(self, name, func,
        version: str | None = '',
        args: str | None = '',
        script: str | None = 'index',
    ):

        path = self.__plugin_dir + '/' + name + '/' + script + '.py'
        if not os.path.exists(path):
            path = self.__plugin_dir + '/' + name + '/' + name + '.py'

        py = 'python3 ' + path
        if args == '':
            py_cmd = py + ' ' + func + ' ' + version
        else:
            py_cmd = py + ' ' + func + ' ' + version + ' ' + args

        if not os.path.exists(path):
            return ('', '')
        py_cmd = 'cd ' + mw.getPanelDir() + " && "+ py_cmd
        data = mw.execShell(py_cmd)
        # print(data)
        if mw.isDebugMode():
            print('run:', py_cmd)
            print(data)
        # print os.path.exists(py_cmd)
        return (data[0].strip(), data[1].strip())

    # 映射包调用
    def callback(self, name, func,
        args: str | None = '',
        script: str | None = 'index',
    ):

        package = self.__plugin_dir + '/' + name
        if not os.path.exists(package):
            return (False, "插件不存在!")
        if not package in sys.path:
            sys.path.append(package)

        eval_str = "__import__('" + script + "')." + func + '(' + args + ')'

        if mw.isDebugMode():
            print('callback', eval_str)

        data = None
        try:
            data = eval(eval_str)
        except Exception as e:
            print(mw.getTracebackInfo())
            return (False, mw.getTracebackInfo())
        
        
        return (True, data)



        