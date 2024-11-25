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
    __MW_KEY = 'uATE5NrKDWIlZuDcYpvLVhoUo1c7A1Pk'
    __MW_PANEL = 'http://127.0.0.1:7200'

    # 如果希望多台面板，可以在实例化对象时，将面板地址与密钥传入
    def __init__(self, mw_panel=None, mw_key=None):
        if mw_panel:
            self.__MW_PANEL = mw_panel
            self.__MW_KEY = mw_key

    # 计算MD5
    def __get_md5(self, s):
        m = hashlib.md5()
        m.update(s.encode('utf-8'))
        return m.hexdigest()

    # 构造带有签名的关联数组
    def __get_key_data(self):
        now_time = int(time.time())
        ready_data = {
            'request_token': self.__get_md5(str(now_time) + '' + self.__get_md5(self.__MW_KEY)),
            'request_time': now_time
        }
        return ready_data

    # 发送POST请求并保存Cookie
    #@url 被请求的URL地址(必需)
    #@data POST参数，可以是字符串或字典(必需)
    #@timeout 超时时间默认1800秒
    # return string
    def __http_post_cookie(self, url, p_data, timeout=1800):
        cookie_file = '/tmp/' + self.__get_md5(self.__MW_PANEL) + '.cookie'
        if sys.version_info[0] == 2:
            # Python2
            import urllib
            import urllib2
            import ssl
            import cookielib

            # 创建cookie对象
            cookie_obj = cookielib.MozillaCookieJar(cookie_file)

            # 加载已保存的cookie
            if os.path.exists(cookie_file):
                cookie_obj.load(cookie_file, ignore_discard=True,
                                ignore_expires=True)

            ssl._create_default_https_context = ssl._create_unverified_context

            data = urllib.urlencode(p_data)
            req = urllib2.Request(url, data)
            opener = urllib2.build_opener(
                urllib2.HTTPCookieProcessor(cookie_obj))
            response = opener.open(req, timeout=timeout)

            # 保存cookie
            cookie_obj.save(ignore_discard=True, ignore_expires=True)
            return response.read()
        else:
            # Python3
            import urllib.request
            import ssl
            import http.cookiejar
            cookie_obj = http.cookiejar.MozillaCookieJar(cookie_file)
            # 加载已保存的cookie
            if os.path.exists(cookie_file):
                cookie_obj.load(cookie_file, ignore_discard=True,
                                ignore_expires=True)

            handler = urllib.request.HTTPCookieProcessor(cookie_obj)
            data = urllib.parse.urlencode(p_data).encode('utf-8')
            req = urllib.request.Request(url, data)
            opener = urllib.request.build_opener(handler)
            response = opener.open(req, timeout=timeout)
            cookie_obj.save(ignore_discard=True, ignore_expires=True)
            result = response.read()
            if type(result) == bytes:
                result = result.decode('utf-8')
            return result

    # 取面板日志
    def getLogs(self):
        # 拼接URL地址
        url = self.__MW_PANEL + '/api/logs/get_log_list'

        # 准备POST数据
        post_data = self.__get_key_data()  # 取签名
        post_data['limit'] = 10
        post_data['p'] = '1'

        # 请求面板接口
        result = self.__http_post_cookie(url, post_data)

        # 解析JSON数据
        return json.loads(result)


if __name__ == '__main__':
    # 实例化MW-API对象
    api = mwApi()

    # 调用get_logs方法
    rdata = api.getLogs()

    # 打印响应数据
    print(rdata)
