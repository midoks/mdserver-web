# coding:utf-8

import sys
import io
import os
import time
import re
import json
import shutil

web_dir = os.getcwd() + "/web"
if os.path.exists(web_dir):
    sys.path.append(web_dir)
    os.chdir(web_dir)

import core.mw as mw

app_debug = False
if mw.isAppleSystem():
    app_debug = True


def getPluginName():
    return 'php-guard'


def getPluginDir():
    return mw.getPluginDir() + '/' + getPluginName()


def getServerDir():
    return mw.getServerDir() + '/' + getPluginName()


def getInitDFile(version):
    if app_debug:
        return '/tmp/' + getPluginName()
    return '/etc/init.d/' + getPluginName() + version


if __name__ == "__main__":
    func = sys.argv[1]
    if func == 'status':
        print('start')
    else:
        print("fail")
