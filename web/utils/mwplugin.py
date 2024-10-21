# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------

import threading

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

    # lock
    _instance_lock = threading.Lock()

    """docstring for MwPlugin"""
    def __init__(self):
        pass

    @classmethod
    def instance(cls, *args, **kwargs):
        if not hasattr(MwPlugin, "_instance"):
            with MwPlugin._instance_lock:
                if not hasattr(MwPlugin, "_instance"):
                    MwPlugin._instance = MwPlugin(*args, **kwargs)
        return MwPlugin._instance


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
        return rdata



        