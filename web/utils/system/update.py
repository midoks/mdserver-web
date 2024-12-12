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
import re
import time
import math
import psutil
import json

import core.mw as mw

def versionDiff(now, new):
    '''
        test 测试
        new 有新版本
        none 没有新版本
    '''
    new_list = new.split('.')
    if len(new_list) > 3:
        return 'test'

    now_list = now.split('.')
    ret = 'none'
    from distutils.version import LooseVersion
    if LooseVersion(new) > LooseVersion(now):
        return 'new'
    else:
        return 'none'

def getServerInfo():
    import urllib.request
    import ssl
    upAddr = 'https://api.github.com/repos/midoks/mdserver-web/releases/latest'
    try:
        context = ssl._create_unverified_context()
        req = urllib.request.urlopen(upAddr, context=context, timeout=3)
        result = req.read().decode('utf-8')
        version = json.loads(result)
        return version
    except Exception as e:
        print(str(e))
        return None
    return None

def updateServer(stype, version=''):
    import config
    # 更新服务
    try:
        if not mw.isRestart():
            return mw.returnData(False, '请等待所有安装任务完成再执行!')

        version_new_info = getServerInfo()
        if version_new_info is None:
            return mw.returnData(False, '服务器数据或网络有问题!')

        version_now = config.APP_VERSION
        new_ver = version_new_info['name']
        if stype == 'check':
            diff = versionDiff(version_now, new_ver)
            if diff == 'new':
                return mw.returnData(True, '有新版本!', new_ver)
            elif diff == 'test':
                return mw.returnData(True, '有测试版本!', new_ver)
            else:
                return mw.returnData(False, '已经是最新,无需更新!')

        if stype == 'info':
            diff = versionDiff(version_now, new_ver)
            data = {}
            data['version'] = new_ver
            data['content'] = version_new_info['body'].replace("\n", "<br/>")
            return mw.returnData(True, '更新信息!', data)

        if stype == 'update':
            if version == '':
                return mw.returnData(False, '缺少版本信息!')

            if new_ver != version:
                return mw.returnData(False, '更新失败,请重试!')

            toPath = mw.getPanelDir() + '/temp'
            if not os.path.exists(toPath):
                mw.execShell('mkdir -p ' + toPath)

            newUrl = "https://github.com/midoks/mdserver-web/archive/refs/tags/" + version + ".zip"

            dist_mw = toPath + '/mw.zip'
            if not os.path.exists(dist_mw):
                mw.execShell('wget --no-check-certificate -O ' + dist_mw + ' ' + newUrl)

            dist_to = toPath + "/mdserver-web-" + version
            if not os.path.exists(dist_to):
                os.system('unzip -o ' + toPath + '/mw.zip' + ' -d ' + toPath)

            cmd_cp = 'cp -rf ' + toPath + '/mdserver-web-' + version + '/* ' + mw.getServerDir() + '/mdserver-web'
            mw.execShell(cmd_cp)

            mw.execShell('rm -rf ' + toPath + '/mdserver-web-' + version)
            mw.execShell('rm -rf ' + toPath + '/mw.zip')

            update_env = '''
#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin

P_VER=`python3 -V | awk '{print $2}'`

if [ ! -f /www/server/mdserver-web/bin/activate ];then
cd /www/server/mdserver-web && python3 -m venv .
cd /www/server/mdserver-web && source /www/server/mdserver-web/bin/activate
else
cd /www/server/mdserver-web && source /www/server/mdserver-web/bin/activate
fi

cn=$(curl -fsSL -m 10 http://ipinfo.io/json | grep "\"country\": \"CN\"")
PIPSRC="https://pypi.python.org/simple"
if [ ! -z "$cn" ];then
PIPSRC="https://pypi.tuna.tsinghua.edu.cn/simple"
fi

cd /www/server/mdserver-web && pip3 install -r /www/server/mdserver-web/requirements.txt -i $PIPSRC

P_VER_D=`echo "$P_VER"|awk -F '.' '{print $1}'`
P_VER_M=`echo "$P_VER"|awk -F '.' '{print $2}'`
NEW_P_VER=${P_VER_D}.${P_VER_M}

if [ -f /www/server/mdserver-web/version/r${NEW_P_VER}.txt ];then
cd /www/server/mdserver-web && pip3 install -r /www/server/mdserver-web/version/r${NEW_P_VER}.txt -i $PIPSRC
fi
'''
            os.system(update_env)
            mw.restartMw()
            return mw.returnData(True, '安装更新成功!')

        return mw.returnData(False, '已经是最新,无需更新!')
    except Exception as ex:
        # print('updateServer', ex)
        return mw.returnData(False, "连接服务器失败!" + str(ex))




