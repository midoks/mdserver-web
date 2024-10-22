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

    # lock
    _instance_lock = threading.Lock()

    """插件类初始化"""
    def __init__(self):
        self.__plugin_dir = mw.getPluginDir()

    @classmethod
    def instance(cls, *args, **kwargs):
        if not hasattr(MwPlugin, "_instance"):
            with MwPlugin._instance_lock:
                if not hasattr(MwPlugin, "_instance"):
                    MwPlugin._instance = MwPlugin(*args, **kwargs)
        return MwPlugin._instance

    # 插件搜索匹配
    def searchKey(self, info, keyword):
        try:
            if info['title'].lower().find(keyword) > -1:
                return True
            if info['ps'].lower().find(keyword) > -1:
                return True
            if info['name'].lower().find(keyword) > -1:
                return True
        except Exception as e:
            return False


    # 对多版本共存进行处理
    def makeCoexistList(self):
        plugins_info = []
        return plugins_info

    def getPluginInfo(self, name,
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

        tmp_plugin_info = self.makeCoexistList(data, type)
        print(tmp_plugin_info)

        return info


    def getAllPluginList(
        self,
        type: str | None = None,
        keyword: str | None = None,
        page: str | None = 1, 
        size: str | None = 10, 
    ):
        plugins_info = []

        # print(mw.getPluginDir())
        for name in os.listdir(self.__plugin_dir):
            if name.startswith('.'):
                continue
            plugin_list = self.getPluginInfo(name,keyword,type=type)
            # print(dirinfo)

        return plugins_info

    def getList(
        self,
        type: str | None = None,
        keyword: str | None = None,
        page: str | None = 1, 
        size: str | None = 10, 
    ) -> object:
        rdata = {}
        rdata['type'] = self.def_plugin_type
        # print(type,keyword,page,size)

        self.getAllPluginList(type,keyword, page, size)

        return rdata



        