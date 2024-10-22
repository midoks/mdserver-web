# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------

import os
import threading
import json
import core.mw as mw

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
        indexList = self.__index_data
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



        