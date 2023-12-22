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
    return 'mariadb'


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


def getRelayLogName():
    file = getConf()
    content = mw.readFile(file)
    rep = 'relay-log\s*=\s*(.*)'
    tmp = re.search(rep, content)
    return tmp.groups()[0].strip()


def getLogBinName():
    file = getConf()
    content = mw.readFile(file)
    rep = 'log-bin\s*=\s*(.*)'
    tmp = re.search(rep, content)
    return tmp.groups()[0].strip()


def binLogListLook(args):

    file = args['file']
    line = args['line']

    data_dir = getDataDir()
    my_bin = getServerDir() + '/bin'
    my_binlog_cmd = my_bin + '/mysqlbinlog'

    cmd = my_binlog_cmd + ' --no-defaults ' + \
        data_dir + '/' + file + '|tail -' + str(line)

    data = mw.execShell(cmd)

    rdata = {}
    rdata['cmd'] = cmd
    rdata['data'] = data[0]

    return rdata


def binLogListLookDecode(args):

    file = args['file']
    line = args['line']

    data_dir = getDataDir()
    my_bin = getServerDir() + '/bin'
    my_binlog_cmd = my_bin + '/mysqlbinlog'

    cmd = my_binlog_cmd + ' --no-defaults --base64-output=decode-rows -vvvv ' + \
        data_dir + '/' + file + '|tail -' + str(line)

    data = mw.execShell(cmd)

    rdata = {}
    rdata['cmd'] = cmd
    rdata['data'] = data[0]

    return rdata


def binLogListTraceRelay(args):
    rdata = {}
    file = args['file']
    line = args['line']

    relay_name = getRelayLogName()
    data_dir = getDataDir()
    alist = os.listdir(data_dir)
    relay_list = []
    for x in range(len(alist)):
        f = alist[x]
        t = {}
        if f.startswith(relay_name) and not f.endswith('.index'):
            relay_list.append(f)

    relay_list = sorted(relay_list, reverse=True)
    if len(relay_list) == 0:
        rdata['cmd'] = ''
        rdata['data'] = '无Relay日志'
        return rdata

    file = relay_list[0]

    my_bin = getServerDir() + '/bin'
    my_binlog_cmd = my_bin + '/mysqlbinlog'

    cmd = my_binlog_cmd + ' --no-defaults --base64-output=decode-rows -vvvv ' + \
        data_dir + '/' + file + '|tail -' + str(line)

    data = mw.execShell(cmd)

    rdata['cmd'] = cmd
    rdata['data'] = data[0]

    return rdata


def binLogListTraceBinLog(args):
    rdata = {}
    file = args['file']
    line = args['line']

    data_dir = getDataDir()
    log_bin_name = getLogBinName()

    alist = os.listdir(data_dir)
    log_bin_l = []
    for x in range(len(alist)):
        f = alist[x]
        t = {}
        if f.startswith(log_bin_name) and not f.endswith('.index'):
            log_bin_l.append(f)

    if len(log_bin_l) == 0:
        rdata['cmd'] = ''
        rdata['data'] = '无BINLOG'
        return rdata

    log_bin_l = sorted(log_bin_l, reverse=True)
    file = log_bin_l[0]

    my_bin = getServerDir() + '/bin'
    my_binlog_cmd = my_bin + '/mysqlbinlog'

    cmd = my_binlog_cmd + ' --no-defaults --base64-output=decode-rows -vvvv ' + \
        data_dir + '/' + file + '|tail -' + str(line)

    data = mw.execShell(cmd)

    rdata['cmd'] = cmd
    rdata['data'] = data[0]

    return rdata
