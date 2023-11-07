# coding:utf-8

import sys
import io
import os
import time
import subprocess
import re
import json

sys.path.append(os.getcwd() + "/class/core")
import mw


if mw.isAppleSystem():
    cmd = 'ls /usr/local/lib/ | grep python  | cut -d \\  -f 1 | awk \'END {print}\''
    info = mw.execShell(cmd)
    p = "/usr/local/lib/" + info[0].strip() + "/site-packages"
    sys.path.append(p)


app_debug = False
if mw.isAppleSystem():
    app_debug = True


def getPluginName():
    return 'mysql'


def getPluginDir():
    return mw.getPluginDir() + '/' + getPluginName()


def getSPluginDir():
    return '/www/server/mdserver-web/plugins/' + getPluginName()


def getServerDir():
    return mw.getServerDir() + '/' + getPluginName()


def getConf():
    path = getServerDir() + '/etc/my.cnf'
    return path


def getDataDir():
    file = getConf()
    content = mw.readFile(file)
    rep = 'datadir\s*=\s*(.*)'
    tmp = re.search(rep, content)
    return tmp.groups()[0].strip()


def binLogListLook(args):

    file = args['file']
    line = args['line']

    data_dir = getDataDir()
    my_bin = getServerDir() + '/bin'
    my_binlog_cmd = my_bin + '/mysqlbinlog'

    cmd = my_binlog_cmd + ' --no-defaults --base64-output=decode-rows -vvvv ' + \
        data_dir + '/' + file + '|tail -' + line

    data = mw.execShell(cmd)

    rdata = {}
    rdata['cmd'] = cmd
    rdata['data'] = data[0]

    return rdata
