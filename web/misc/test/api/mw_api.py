# coding: utf-8
# +-----------------------------------------------------------------------------------
# | MW Linux面板
# +-----------------------------------------------------------------------------------
# | Copyright (c) 2015-2099 MW(http://github.com/midoks/mdserver) All rights reserved.
# +-----------------------------------------------------------------------------------
# | Author: midoks
# +-----------------------------------------------------------------------------------

#------------------------------
# API-Demo of Python
#------------------------------
import time
import hashlib
import sys
import os
import json


class mwApi:
    __MW_PANEL = 'http://154.12.53.90:51377/'
    __MW_APP_ID = 'yhYkxGssPD'
    __MW_APP_SERECT = 'ErmBdr563eJ5GMM5sWbc'
    
    # 如果希望多台面板，可以在实例化对象时，将面板地址与密钥传入
    def __init__(self, panel_url=None, app_id=None, app_serect=None):
        if panel_url:
            self.__MW_PANEL = panel_url
            self.__MW_APP_ID = app_id
            self.__MW_APP_SERECT = app_serect

    def post(self, endpoint, request_data):
        import requests
        url = self.__MW_PANEL + endpoint  
        post_data = requests.post(url, data=request_data, headers={
            'app-id':self.__MW_APP_ID,
            'app-secret':self.__MW_APP_SERECT
        })
        try:
            return post_data.json()
        except Exception as e:
            return post_data.text
    # 取面板日志
    def getLogs(self):
        result = self.post('/task/count',{'limit':10,'p':1})
        return result


if __name__ == '__main__':
    # 实例化MW-API对象
    api = mwApi()

    # 调用get_logs方法
    rdata = api.getLogs()

    # 打印响应数据
    print(rdata)
