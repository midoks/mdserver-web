# coding:utf-8

import sys
import io
import os
import time
import shutil

sys.path.append(os.getcwd() + "/class/core")
import public

app_debug = False
if public.isAppleSystem():
    app_debug = True


def getPluginName():
    return 'l2tp'


def getPluginDir():
    return public.getPluginDir() + '/' + getPluginName()


def getServerDir():
    return public.getServerDir() + '/' + getPluginName()


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


def checkArgs(data, ck=[]):
    for i in range(len(ck)):
        if not ck[i] in data:
            return (False, public.returnJson(False, '参数:(' + ck[i] + ')没有!'))
    return (True, public.returnJson(True, 'ok'))


def status():
    cmd = "ps -ef|grep xl2tpd |grep -v grep | grep -v python | awk '{print $2}'"
    data = public.execShell(cmd)
    if data[0] == '':
        return 'stop'
    return 'start'


def start():
    data = public.execShell(file + ' start')
    if data[1] == '':
        return 'ok'
    return data[1]


def stop():
    data = public.execShell(file + ' stop')
    if data[1] == '':
        return 'ok'
    return data[1]


def restart():
    return 'ok'


def reload():
    return 'ok'


def getPathFile():
    if public.isAppleSystem():
        return getServerDir() + '/chap-secrets'
    return '/etc/ppp/chap-secrets'


def getUserList():
    import re
    path = getPathFile()
    if not os.path.exists(path):
        return public.returnJson(False, '密码配置文件不存在!')
    conf = public.readFile(path)

    conf = re.sub('#(.*)\n', '', conf)
    ulist = conf.strip().split('\n')

    user = []
    for line in ulist:
        line_info = {}
        line = re.match(r'(\w*)\s*(\w*)\s*(\w*)\s*(.*)',
                        line.strip(), re.M | re.I).groups()
        line_info['user'] = line[0]
        line_info['pwd'] = line[2]
        line_info['type'] = line[1]
        line_info['ip'] = line[3]
        user.append(line_info)

    return public.returnJson(True, 'ok', user)


def addUser():
    args = getArgs()
    data = checkArgs(args, ['username'])
    if not data[0]:
        return data[1]
    ret = public.execShell('echo ' + args['username'] + '|l2tp -a')
    if ret[1] == '':
        return public.returnJson(True, '添加成功!:' + ret[0])
    return public.returnJson(False, '添加失败:' + ret[0])


def delUser():
    args = getArgs()
    data = checkArgs(args, ['username'])
    if not data[0]:
        return data[1]

    ret = public.execShell('echo ' + args['username'] + '|l2tp -l')
    if ret[1] == '':
        return public.returnJson(True, '删除成功!:' + ret[0])
    return public.returnJson(False, '删除失败:' + ret[0])
if __name__ == "__main__":
    func = sys.argv[1]
    if func == 'status':
        print status()
    elif func == 'start':
        print start()
    elif func == 'stop':
        print stop()
    elif func == 'restart':
        print restart()
    elif func == 'reload':
        print reload()
    elif func == 'conf':
        print getPathFile()
    elif func == 'user_list':
        print getUserList()
    elif func == 'add_user':
        print addUser()
    elif func == 'del_user':
        print delUser()
    else:
        print 'error'
