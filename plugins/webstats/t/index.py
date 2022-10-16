# coding:utf-8

import sys
import io
import os
import time
import json

import os
import sys
import time
import string
import json
import hashlib
import shlex
import datetime
import subprocess
import re
from random import Random


TEST_URL = "http://t1.cn/"
# TEST_URL = "https://www.zzzvps.com/"


def httpGet(url, timeout=10):
    import urllib.request

    try:
        req = urllib.request.urlopen(url, timeout=timeout)
        result = req.read().decode('utf-8')
        return result

    except Exception as e:
        return str(e)


def httpPost(url, data, timeout=10):
    """
    发送POST请求
    @url 被请求的URL地址(必需)
    @data POST参数，可以是字符串或字典(必需)
    @timeout 超时时间默认60秒
    return string
    """
    if sys.version_info[0] == 2:
        try:
            import urllib
            import urllib2
            import ssl
            ssl._create_default_https_context = ssl._create_unverified_context
            data = urllib.urlencode(data)
            req = urllib2.Request(url, data)
            response = urllib2.urlopen(req, timeout=timeout)
            return response.read()
        except Exception as ex:
            return str(ex)
    else:
        try:
            import urllib.request
            import ssl
            try:
                ssl._create_default_https_context = ssl._create_unverified_context
            except:
                pass
            data = urllib.parse.urlencode(data).encode('utf-8')
            req = urllib.request.Request(url, data)
            response = urllib.request.urlopen(req, timeout=timeout)
            result = response.read()
            if type(result) == bytes:
                result = result.decode('utf-8')
            return result
        except Exception as ex:
            return str(ex)


def test_OK():
    '''
    目录保存
    '''
    url = TEST_URL + "ok.txt"
    print("ok test start")
    url_val = httpGet(url, 10)
    print(url_val)
    print("ok test end")


def test_start():
    test_OK()


if __name__ == "__main__":
    os.system('cd /Users/midoks/Desktop/mwdev/server/mdserver-web/plugins/webstats && sh install.sh uninstall 0.2.2 && sh install.sh install 0.2.2')
    os.system('cd /Users/midoks/Desktop/mwdev/server/mdserver-web/ && python3 plugins/openresty/index.py stop && python3 plugins/openresty/index.py start')
    test_start()
