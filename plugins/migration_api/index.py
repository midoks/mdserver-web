# coding:utf-8

import sys
import io
import os
import time
import re
import hashlib
import json

sys.path.append(os.getcwd() + "/class/core")
import mw

app_debug = False
if mw.isAppleSystem():
    app_debug = True


class classApi:
    __MW_KEY = 'app'
    __MW_PANEL = 'http://127.0.0.1:7200'

    _REQUESTS = None

    # 如果希望多台面板，可以在实例化对象时，将面板地址与密钥传入
    def __init__(self, mw_panel=None, mw_key=None):
        if mw_panel:
            self.__MW_PANEL = mw_panel
            self.__MW_KEY = mw_key

        import requests
        if not self._REQUESTS:
            self._REQUESTS = requests.session()

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

    def __http_post_cookie(self, url, p_data, timeout=1800):
        try:
            # print(url)
            res = self._REQUESTS.post(url, p_data, timeout=timeout)
            return res.text
        except Exception as ex:
            ex = str(ex)
            if ex.find('Max retries exceeded with') != -1:
                return mw.returnJson(False, '连接服务器失败!')
            if ex.find('Read timed out') != -1 or ex.find('Connection aborted') != -1:
                return mw.returnJson(False, '连接超时!')
            return mw.returnJson(False, '连接服务器失败!')

    def send(self, url, args, timeout=600):
        url = self.__MW_PANEL + '/api' + url
        post_data = self.__get_key_data()  # 取签名
        post_data.update(args)
        result = self.__http_post_cookie(url, post_data, timeout)
        try:
            return json.loads(result)
        except Exception as e:
            return result

    # 取面板日志
    def getLogs(self):
        # 拼接URL地址
        url = self.__MW_PANEL + '/firewall/get_log_list'

        # 准备POST数据
        post_data = self.__get_key_data()  # 取签名
        post_data['limit'] = 10
        post_data['p'] = '1'

        # 请求面板接口
        result = self.__http_post_cookie(url, post_data)

        # 解析JSON数据
        return json.loads(result)


def getPluginName():
    return 'migration_api'


def getPluginDir():
    return mw.getPluginDir() + '/' + getPluginName()


def getServerDir():
    return mw.getServerDir() + '/' + getPluginName()


def getInitDFile():
    if app_debug:
        return '/tmp/' + getPluginName()
    return '/etc/init.d/' + getPluginName()


def getConf():
    path = getServerDir() + "/ma.cfg"
    return path


def getCfgData():
    path = getConf()
    if not os.path.exists(path):
        mw.writeFile(path, '{}')

    t = mw.readFile(path)
    return json.loads(t)


def writeConf(data):
    path = getConf()
    mw.writeFile(path, json.dumps(data))
    return True


def getArgs():
    args = sys.argv[2:]
    tmp = {}
    args_len = len(args)
    if args_len == 1:
        t = args[0].strip('{').strip('}')
        if t.strip() == '':
            tmp = []
        else:
            t = t.split(':', 1)
            tmp[t[0]] = t[1]
        tmp[t[0]] = t[1]
    elif args_len > 1:
        for i in range(len(args)):
            t = args[i].split(':', 1)
            tmp[t[0]] = t[1]
    return tmp


def checkArgs(data, ck=[]):
    for i in range(len(ck)):
        if not ck[i] in data:
            return (False, mw.returnJson(False, '参数:(' + ck[i] + ')没有!'))
    return (True, mw.returnJson(True, 'ok'))


def status():
    return 'start'


def initDreplace():
    return 'ok'


def getStepOneData():
    data = getCfgData()
    return mw.returnJson(True, 'ok', data)


def stepOne():
    args = getArgs()
    data = checkArgs(args, ['url', 'token'])
    if not data[0]:
        return data[1]

    url = args['url']
    token = args['token']

    api = classApi(url, token)
    # api = classApi('http://127.0.0.1:7200','HfJNKGP5RPqGvhIOyrwpXG4A2fTjSh9B')
    rdata = api.send('/task/count', {})
    # print(rdata)
    if type(rdata) != int:
        return mw.returnJson(False, rdata['msg'])
    data = getCfgData()

    data['url'] = url
    data['token'] = token
    writeConf(data)

    return mw.returnJson(True, '验证成功')


if __name__ == "__main__":
    func = sys.argv[1]
    if func == 'status':
        print(status())
    elif func == 'start':
        print(start())
    elif func == 'stop':
        print(stop())
    elif func == 'get_conf':
        print(getStepOneData())
    elif func == 'step_one':
        print(stepOne())
    else:
        print('error')
