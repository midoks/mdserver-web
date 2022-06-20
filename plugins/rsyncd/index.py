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
    return 'rsyncd'


def getInitDTpl():
    path = getPluginDir() + "/init.d/" + getPluginName() + ".tpl"
    return path


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


def checkArgs(data, ck=[]):
    for i in range(len(ck)):
        if not ck[i] in data:
            return (False, mw.returnJson(False, '参数:(' + ck[i] + ')没有!'))
    return (True, mw.returnJson(True, 'ok'))


def contentReplace(content):
    service_path = mw.getServerDir()
    content = content.replace('{$SERVER_PATH}', service_path)
    return content


def status():
    data = mw.execShell(
        "ps -ef|grep rsync |grep -v grep | grep -v python | awk '{print $2}'")
    if data[0] == '':
        return 'stop'
    return 'start'


def appConf():
    return getServerDir() + '/rsyncd.conf'
    # return '/etc/rsyncd.conf'


def appConfPwd():
    # if mw.isAppleSystem():
    return getServerDir() + '/rsyncd.passwd'
    # return '/etc/rsyncd.passwd'


def getLog():
    conf_path = appConf()
    conf = mw.readFile(conf_path)
    rep = 'log file\s*=\s*(.*)'
    tmp = re.search(rep, conf)
    if not tmp:
        return ''
    return tmp.groups()[0]


def initDreplace():

    # conf
    conf_path = appConf()
    conf_tpl_path = getPluginDir() + '/conf/rsyncd.conf'
    if not os.path.exists(conf_path):
        content = mw.readFile(conf_tpl_path)
        mw.writeFile(conf_path, content)

    # pwd
    confpwd_path = appConfPwd()
    if not os.path.exists(confpwd_path):
        mw.writeFile(confpwd_path, '')
        mw.execShell('chmod 0600 ' + confpwd_path)

    initD_path = getServerDir() + '/init.d'
    if not os.path.exists(initD_path):
        os.mkdir(initD_path)
    file_bin = initD_path + '/' + getPluginName()

    file_tpl = getInitDTpl()
    # initd replace
    if not os.path.exists(file_bin):
        content = mw.readFile(file_tpl)
        content = contentReplace(content)
        mw.writeFile(file_bin, content)
        mw.execShell('chmod +x ' + file_bin)

    # systemd
    systemDir = '/lib/systemd/system'
    systemService = systemDir + '/rsyncd.service'
    systemServiceTpl = getPluginDir() + '/init.d/rsyncd.service.tpl'
    if os.path.exists(systemDir) and not os.path.exists(systemService):
        rsync_bin = mw.execShell('which rsync')[0].strip()
        service_path = mw.getServerDir()
        se_content = mw.readFile(systemServiceTpl)
        se_content = se_content.replace('{$SERVER_PATH}', service_path)
        se_content = se_content.replace('{$RSYNC_BIN}', rsync_bin)
        mw.writeFile(systemService, se_content)
        mw.execShell('systemctl daemon-reload')

    rlog = getLog()
    if os.path.exists(rlog):
        mw.writeFile(rlog, '')
    return file_bin


def rsyncOp(method):
    file = initDreplace()
    if not mw.isAppleSystem():
        data = mw.execShell('systemctl ' + method + ' rsyncd')
        if data[1] == '':
            return 'ok'
        return 'fail'

    data = mw.execShell(file + ' ' + method)
    if data[1] == '':
        return 'ok'
    return 'fail'


def start():
    return rsyncOp('start')


def stop():
    return rsyncOp('stop')


def restart():
    return rsyncOp('restart')


def reload():
    return rsyncOp('reload')


def initdStatus():
    if mw.isAppleSystem():
        return "Apple Computer does not support"

    shell_cmd = 'systemctl status rsyncd | grep loaded | grep "enabled;"'
    data = mw.execShell(shell_cmd)
    if data[0] == '':
        return 'fail'
    return 'ok'


def initdInstall():
    if mw.isAppleSystem():
        return "Apple Computer does not support"

    mw.execShell('systemctl enable rsyncd')
    return 'ok'


def initdUinstall():
    if not app_debug:
        if mw.isAppleSystem():
            return "Apple Computer does not support"

    mw.execShell('systemctl diable rsyncd')
    return 'ok'


def getRecListData():
    path = appConf()
    content = mw.readFile(path)

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
    return mw.returnJson(True, 'ok', ret_list)


def getUPwdList():
    pwd_path = appConfPwd()
    pwd_content = mw.readFile(pwd_path)
    plist = pwd_content.strip().split('\n')
    plist_len = len(plist)
    data = {}
    for x in range(plist_len):
        tmp = plist[x].split(':')
        data[tmp[0]] = tmp[1]
    return data


def addRec():
    args = getArgs()
    data = checkArgs(args, ['name', 'path', 'pwd', 'ps'])
    if not data[0]:
        return data[1]

    args_name = args['name']
    args_pwd = args['pwd']
    args_path = args['path']
    args_ps = args['ps']

    pwd_path = appConfPwd()
    pwd_content = mw.readFile(pwd_path)
    pwd_content += args_name + ':' + args_pwd + "\n"
    mw.writeFile(pwd_path, pwd_content)

    path = appConf()
    content = mw.readFile(path)

    con = "\n\n" + '[' + args_name + ']' + "\n"
    con += 'path = ' + args_path + "\n"
    con += 'comment = ' + args_ps + "\n"
    con += 'auth users = ' + args_name + "\n"
    con += 'read only = false'

    content = content + con
    mw.writeFile(path, content)
    return mw.returnJson(True, '添加成功')


def delRec():
    args = getArgs()
    data = checkArgs(args, ['name'])
    if not data[0]:
        return data[1]
    args_name = args['name']

    cmd = "sed -i '_bak' '/" + args_name + "/d' " + appConfPwd()
    mw.execShell(cmd)

    try:

        path = appConf()
        content = mw.readFile(path)

        ret_list = getRecListData()
        ret_list_len = len(ret_list)
        is_end = False
        next_name = ''
        for x in range(ret_list_len):
            tmp = ret_list[x]
            if tmp['name'] == args_name:
                if x + 1 == ret_list_len:
                    is_end = True
                else:
                    next_name = ret_list[x + 1]['name']
        reg = ''
        if is_end:
            reg = '\[' + args_name + '\]\s*(.*)'
        else:
            reg = '\[' + args_name + '\]\s*(.*)\s*\[' + next_name + '\]'

        conre = re.search(reg,  content, re.S)
        content = content.replace(
            "[" + args_name + "]\n" + conre.groups()[0], '')
        mw.writeFile(path, content)
        return mw.returnJson(True, '删除成功!')
    except Exception as e:
        return mw.returnJson(False, '删除失败!')


def cmdRec():
    args = getArgs()
    data = checkArgs(args, ['name'])
    if not data[0]:
        return data[1]

    an = args['name']
    pwd_list = getUPwdList()
    ip = mw.getLocalIp()

    cmd = 'echo "' + pwd_list[an] + '" > /tmp/p.pass' + "<br>"
    cmd += 'chmod 600 /tmp/p.pass' + "<br>"
    cmd += 'rsync -arv --password-file=/tmp/p.pass --progress --delete  /project  ' + \
        an + '@' + ip + '::' + an
    return mw.returnJson(True, 'OK!', cmd)

# rsyncdReceive
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
    elif func == 'initd_status':
        print(initdStatus())
    elif func == 'initd_install':
        print(initdInstall())
    elif func == 'initd_uninstall':
        print(initdUinstall())
    elif func == 'conf':
        print(appConf())
    elif func == 'conf_pwd':
        print(appConfPwd())
    elif func == 'run_log':
        print(getLog())
    elif func == 'rec_list':
        print(getRecList())
    elif func == 'add_rec':
        print(addRec())
    elif func == 'del_rec':
        print(delRec())
    elif func == 'cmd_rec':
        print(cmdRec())
    else:
        print('error')
