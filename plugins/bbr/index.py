# coding: utf-8

import time
import random
import os
import json
import re
import sys

sys.path.append(os.getcwd() + "/class/core")
import mw


app_debug = False
if mw.isAppleSystem():
    app_debug = True


def getPluginName():
    return 'bbr'


def getPluginDir():
    return mw.getPluginDir() + '/' + getPluginName()


def getServerDir():
    return mw.getServerDir() + '/' + getPluginName()


def getInitDFile():
    if app_debug:
        return '/tmp/' + getPluginName()
    return '/etc/init.d/' + getPluginName()


def getArgs():
    args = sys.argv[2:]
    tmp = {}
    args_len = len(args)

    if args_len == 1:
        t = args[0].strip('{').strip('}')
        t = t.split(':')
        tmp[t[0]] = t[1]
    elif args_len > 1:
        for i in range(len(args)):
            t = args[i].split(':')
            tmp[t[0]] = t[1]

    return tmp


def status():
    if not app_debug:
        if mw.isAppleSystem():
            return "stop"

    data = mw.execShell('sudo sysctl -n net.ipv4.tcp_congestion_control')
    r = data[0].strip()
    if r == 'bbr':
        return 'start'
    return 'stop'


def start():
    if not app_debug:
        if mw.isAppleSystem():
            return "Apple Computer does not support"

    mw.execShell('echo "net.core.default_qdisc=fq" >> /etc/sysctl.conf')
    cmd = 'echo "net.ipv4.tcp_congestion_control=bbr" >> /etc/sysctl.conf'
    mw.execShell(cmd)
    mw.execShell('sysctl -p')
    return '执行成功!重启系统生效'


def stop():
    if not app_debug:
        if mw.isAppleSystem():
            return "Apple Computer does not support"

    cmd1 = "sed -i '/net\.core\.default_qdisc/d' /etc/sysctl.conf"
    mw.execShell(cmd1)
    cmd2 = "sed -i '/net\.ipv4\.tcp_congestion_control/d' /etc/sysctl.conf"
    mw.execShell(cmd2)
    mw.execShell("sysctl -p")
    return '执行成功!重启系统生效'


def restart():
    return '无效'


def reload():
    return '无效'

if __name__ == "__main__":
    func = sys.argv[1]
    if func == 'status':
        print(status())
    elif func == 'start':
        print(start())
    elif func == 'stop':
        print(stop())
    elif func == 'restart':
        print(restart())
    elif func == 'reload':
        print(reload())
