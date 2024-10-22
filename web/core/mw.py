# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------
# 核心方法库
# ---------------------------------------------------------------------------------


import os
import sys
import time
import string
import json
import hashlib
import shlex
import datetime
import subprocess
import glob
import base64
import re

from random import Random

def execShell(cmdstring, cwd=None, timeout=None, shell=True):

    if shell:
        cmdstring_list = cmdstring
    else:
        cmdstring_list = shlex.split(cmdstring)
    if timeout:
        end_time = datetime.datetime.now() + datetime.timedelta(seconds=timeout)

    sub = subprocess.Popen(cmdstring_list, cwd=cwd, stdin=subprocess.PIPE,
                           shell=shell, bufsize=4096, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    while sub.poll() is None:
        time.sleep(0.1)
        if timeout:
            if end_time <= datetime.datetime.now():
                raise Exception("Timeout：%s" % cmdstring)

    if sys.version_info[0] == 2:
        return sub.communicate()

    data = sub.communicate()
    # python3 fix 返回byte数据
    if isinstance(data[0], bytes):
        t1 = str(data[0], encoding='utf-8')

    if isinstance(data[1], bytes):
        t2 = str(data[1], encoding='utf-8')
    return (t1, t2)


def getTracebackInfo():
    import traceback
    return traceback.format_exc()

def getRunDir():
    return os.getcwd()

def getRootDir():
    return os.path.dirname(getRunDir())

def getPanelDir():
    return getRootDir()

def getFatherDir():
    return os.path.dirname(os.path.dirname(getPanelDir()))

def getPluginDir():
    return getPanelDir() + '/plugins'

def getPanelDataDir():
    return getPanelDir() + '/data'

def getMWLogs():
    return getPanelDir() + '/logs'

def getPanelTmp():
    return getPanelDir() + '/tmp'


def getServerDir():
    return getRunDir() + '/server'

def getLogsDir():
    return getRunDir() + '/wwwlogs'

def getRandomString(length):
    # 取随机字符串
    rnd_str = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    chrlen = len(chars) - 1
    random = Random()
    for i in range(length):
        rnd_str += chars[random.randint(0, chrlen)]
    return rnd_str


def getUniqueId():
    """
    根据时间生成唯一ID
    :return:
    """
    current_time = datetime.datetime.now()
    str_time = current_time.strftime('%Y%m%d%H%M%S%f')[:-3]
    unique_id = "{0}".format(str_time)
    return unique_id

def readFile(filename):
    # 读文件内容
    try:
        fp = open(filename, 'r')
        fBody = fp.read()
        fp.close()
        return fBody
    except Exception as e:
        # print(e)
        return False

def writeFile(filename, content, mode='w+'):
    # 写文件内容
    try:
        fp = open(filename, mode)
        fp.write(content)
        fp.close()
        return True
    except Exception as e:
        return False

def isNumber(s):
    try:
        float(s)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass

    return False

def getPathSuffix(path):
    return os.path.splitext(path)[-1]

def dbSqitePrefix():
    WIN = sys.platform.startswith('win')
    if WIN:  # 如果是 Windows 系统，使用三个斜线
        prefix = 'sqlite:///'
    else:  # 否则使用四个斜线
        prefix = 'sqlite:////'
    return prefix


def getPage(args, result='1,2,3,4,5,8'):
    data = getPageObject(args, result)
    return data[0]


def getPageObject(args, result='1,2,3,4,5,8'):
    # 取分页
    from utils import page
    # 实例化分页类
    page = page.Page()
    info = {}

    info['count'] = 0
    if 'count' in args:
        info['count'] = int(args['count'])

    info['row'] = 10
    if 'row' in args:
        info['row'] = int(args['row'])

    info['p'] = 1
    if 'p' in args:
        info['p'] = int(args['p'])
    info['uri'] = {}
    info['return_js'] = ''
    if 'tojs' in args:
        info['return_js'] = args['tojs']

    if 'args_tpl' in args:
        info['args_tpl'] = args['args_tpl']

    return (page.GetPage(info, result), page)

