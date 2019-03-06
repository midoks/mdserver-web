# coding: utf-8

import time
import random
import os
import json
import re
import sys

sys.path.append(os.getcwd() + "/class/core")
import public

app_debug = False
if public.isAppleSystem():
    app_debug = True


def getPluginName():
    return 'rsyncd'


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
    data = public.execShell(
        "ps -ef|grep rsync |grep -v grep | grep -v python | awk '{print $2}'")
    if data[0] == '':
        return 'stop'
    return 'start'


def appConf():
    if public.isAppleSystem():
        return getServerDir() + '/rsyncd.conf'
    return '/etc/rsyncd.conf'


def getLog():
    conf_path = appConf()
    conf = public.readFile(conf_path)
    rep = 'log file\s*=\s*(.*)'
    tmp = re.search(rep, conf)
    if not tmp:
        return ''
    return tmp.groups()[0]


def initConf():
    conf_path = appConf()
    conf = public.readFile(conf_path)
    conf = re.sub('^#(.*)', '', conf)
    conf_tpl_path = getPluginDir() + '/conf/rsyncd.conf'
    if conf.strip() == '':
        content = public.readFile(conf_tpl_path)
        public.writeFile(conf_path, content)


def start():
    initConf()

    if public.isAppleSystem():
        return "Apple Computer does not support"

    data = public.execShell('systemctl start rsyncd.service')
    if data[1] == '':
        return 'ok'
    return 'fail'


def stop():
    initConf()
    if public.isAppleSystem():
        return "Apple Computer does not support"
    data = public.execShell('systemctl stop rsyncd.service')
    if data[1] == '':
        return 'ok'
    return 'fail'


def restart():
    initConf()
    if public.isAppleSystem():
        return "Apple Computer does not support"
    data = public.execShell('systemctl restart rsyncd.service')
    if data[1] == '':
        return 'ok'
    return 'fail'


def reload():
    initConf()
    if public.isAppleSystem():
        return "Apple Computer does not support"

    data = public.execShell('systemctl reload rsyncd.service')
    if data[1] == '':
        return 'ok'
    return 'fail'


def initdStatus():
    if public.isAppleSystem():
        return "Apple Computer does not support"
    initd_bin = getInitDFile()
    if os.path.exists(initd_bin):
        return 'ok'
    return 'fail'


def initdInstall():
    if public.isAppleSystem():
        return "Apple Computer does not support"

    source_bin = initDreplace()
    initd_bin = getInitDFile()
    shutil.copyfile(source_bin, initd_bin)
    public.execShell('chmod +x ' + initd_bin)
    return 'ok'


def initdUinstall():
    if public.isAppleSystem():
        return "Apple Computer does not support"

    initd_bin = getInitDFile()
    os.remove(initd_bin)
    return 'ok'


def getRecListData():
    path = appConf()
    content = public.readFile(path)

    flist = re.findall("\[(.*)\]", content)
    flist_len = len(flist)
    ret_list = []
    for i in range(flist_len):
        tmp = {}
        tmp['name'] = flist[i]
        n = i + 1
        reg = ''
        if n == flist_len:
            reg = '\[' + flist[i] + '\](.*)\[?'
        else:
            reg = '\[' + flist[i] + '\](.*)\[' + flist[n] + '\]'

        t1 = re.search(reg, content, re.S)
        if t1:
            args = t1.groups()[0]
            # print 'args start', args, 'args_end'
            t2 = re.findall('\s*(.*)\s*=\s*(.*)', args, re.M)
            for i in range(len(t2)):
                tmp[t2[i][0].strip()] = t2[i][1]
        ret_list.append(tmp)
    return ret_list


def getRecList():
    ret_list = getRecListData()
    return public.returnJson(True, 'ok', ret_list)


def addRec():
    args = getArgs()

    data = checkArgs(args, ['name', 'path', 'ps'])
    if not data[0]:
        return data[1]

    args_name = args['name']
    args_path = args['path']
    args_ps = args['ps']

    path = appConf()
    content = public.readFile(path)

    con = "\n\n" + '[' + args_name + ']' + "\n"
    con += 'path = ' + args_path + "\n"
    con += 'comment = ' + args_ps + "\n"
    con += 'read only = false'

    content = content + con
    public.writeFile(path, content)
    return public.returnJson(True, '添加成功')


def delRec():
    args = getArgs()

    data = checkArgs(args, ['name'])
    if not data[0]:
        return data[1]

    args_name = args['name']

    path = appConf()
    content = public.readFile(path)

    ret_list = getRecListData()
    ret_list_len = len(ret_list)
    is_end = False
    next_name = ''
    for x in range(ret_list_len):
        tmp = ret_list[x]
        if tmp['name'] == args_name:
            if x == ret_list_len:
                is_end = True
            else:
                next_name = ret_list[x + 1]['name']

    reg = ''
    if is_end:
        reg = '\[' + args_name + '\]\s*(.*)'
    else:
        reg = '\[' + args_name + '\]\s*(.*)\s*\[' + next_name + '\]'

    conre = re.search(reg,  content, re.S)
    content = content.replace("[" + args_name + "]\n" + conre.groups()[0], '')
    public.writeFile(path, content)
    return public.returnJson(True, '删除成功!')


# rsyncdReceive
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
    elif func == 'initd_status':
        print initdStatus()
    elif func == 'initd_install':
        print initdInstall()
    elif func == 'initd_uninstall':
        print initdUinstall()
    elif func == 'conf':
        print appConf()
    elif func == 'run_log':
        print getLog()
    elif func == 'rec_list':
        print getRecList()
    elif func == 'add_rec':
        print addRec()
    elif func == 'del_rec':
        print delRec()
    else:
        print 'error'
