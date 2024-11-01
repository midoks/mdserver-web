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

def getPhpVersion():
    phpVersions = ('00', '52', '53', '54', '55',
                   '56', '70', '71', '72', '73',
                   '74', '80', '81', '82', '83',
                   '84')
    data = []
    for val in phpVersions:
        tmp = {}
        if val == '00':
            tmp['version'] = '00'
            tmp['name'] = '纯静态'
            data.append(tmp)

        # 标准判断
        checkPath = mw.getServerDir() + '/php/' + val + '/bin/php'
        if os.path.exists(checkPath):
            tmp['version'] = val
            tmp['name'] = 'PHP-' + val
            data.append(tmp)

    # 其他PHP安装类型
    conf_dir = mw.getServerDir() + "/web_conf/php/conf"
    conf_list = os.listdir(conf_dir)
    l = len(conf_list)
    rep = r"enable-php-(.*?)\.conf"
    for name in conf_list:
        tmp = {}
        try:
            matchVer = re.search(rep, name).groups()[0]
        except Exception as e:
            continue

        if matchVer in phpVersions:
            continue

        tmp['version'] = matchVer
        tmp['name'] = 'PHP-' + matchVer
        data.append(tmp)

    return data