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


def appAuthPwd(name):
    nameDir = getServerDir() + '/receive/' + name
    if not os.path.exists(nameDir):
        mw.execShell("mkdir -p " + nameDir)
    return nameDir + '/auth.db'


def getLog():
    conf_path = appConf()
    conf = mw.readFile(conf_path)
    rep = 'log file\s*=\s*(.*)'
    tmp = re.search(rep, conf)
    if not tmp:
        return ''
    return tmp.groups()[0]


def getLsyncdLog():
    path = getServerDir() + "/lsyncd.conf"
    conf = mw.readFile(path)
    rep = 'logfile\s*=\s*\"(.*)\"'
    tmp = re.search(rep, conf)
    if not tmp:
        return ''
    return tmp.groups()[0]


def initDReceive():
    # conf
    conf_path = appConf()
    conf_tpl_path = getPluginDir() + '/conf/rsyncd.conf'
    if not os.path.exists(conf_path):
        content = mw.readFile(conf_tpl_path)
        mw.writeFile(conf_path, content)

    initD_path = getServerDir() + '/init.d'
    if not os.path.exists(initD_path):
        os.mkdir(initD_path)

    file_bin = initD_path + '/' + getPluginName()
    file_tpl = getInitDTpl()
    # print(file_bin, file_tpl)
    # initd replace
    if not os.path.exists(file_bin):
        content = mw.readFile(file_tpl)
        content = contentReplace(content)
        mw.writeFile(file_bin, content)
        mw.execShell('chmod +x ' + file_bin)

    # systemd
    systemDir = mw.systemdCfgDir()
    systemService = systemDir + '/rsyncd.service'
    systemServiceTpl = getPluginDir() + '/init.d/rsyncd.service.tpl'
    if os.path.exists(systemDir) and not os.path.exists(systemService):
        rsync_bin = mw.execShell('which rsync')[0].strip()
        if rsync_bin == '':
            print('rsync missing!')
            exit(0)

        service_path = mw.getServerDir()
        se = mw.readFile(systemServiceTpl)
        se = se.replace('{$SERVER_PATH}', service_path)
        se = se.replace('{$RSYNC_BIN}', rsync_bin)
        mw.writeFile(systemService, se)
        mw.execShell('systemctl daemon-reload')

    rlog = getLog()
    if os.path.exists(rlog):
        mw.writeFile(rlog, '')
    return file_bin


def initDSend():

    service_path = mw.getServerDir()

    conf_path = getServerDir() + '/lsyncd.conf'
    conf_tpl_path = getPluginDir() + '/conf/lsyncd.conf'
    if not os.path.exists(conf_path):
        content = mw.readFile(conf_tpl_path)
        content = content.replace('{$SERVER_PATH}', service_path)
        mw.writeFile(conf_path, content)

    initD_path = getServerDir() + '/init.d'
    if not os.path.exists(initD_path):
        os.mkdir(initD_path)

    # initd replace
    file_bin = initD_path + '/lsyncd'
    file_tpl = getPluginDir() + "/init.d/lsyncd.tpl"
    if not os.path.exists(file_bin):
        content = mw.readFile(file_tpl)
        content = contentReplace(content)
        mw.writeFile(file_bin, content)
        mw.execShell('chmod +x ' + file_bin)

    lock_file = getServerDir() + "/installed.pl"
    # systemd
    systemDir = mw.systemdCfgDir()
    systemService = systemDir + '/lsyncd.service'
    systemServiceTpl = getPluginDir() + '/init.d/lsyncd.service.tpl'
    if not os.path.exists(lock_file):
        lsyncd_bin = mw.execShell('which lsyncd')[0].strip()
        if lsyncd_bin == '':
            print('lsyncd missing!')
            exit(0)

        content = mw.readFile(systemServiceTpl)
        content = content.replace('{$SERVER_PATH}', service_path)
        content = content.replace('{$LSYNCD_BIN}', lsyncd_bin)
        mw.writeFile(systemService, content)
        mw.execShell('systemctl daemon-reload')

    mw.writeFile(lock_file, "ok")

    lslog = getLsyncdLog()
    if os.path.exists(lslog):
        mw.writeFile(lslog, '')

    return file_bin


def getDefaultConf():
    path = getServerDir() + "/config.json"
    data = mw.readFile(path)
    data = json.loads(data)
    return data


def setDefaultConf(data):
    path = getServerDir() + "/config.json"
    mw.writeFile(path, json.dumps(data))
    return True


def initConfigJson():
    path = getServerDir() + "/config.json"
    tpl = getPluginDir() + "/conf/config.json"
    if not os.path.exists(path):
        data = mw.readFile(tpl)
        data = json.loads(data)
        mw.writeFile(path, json.dumps(data))


def initDreplace():

    initDSend()

    # conf
    file_bin = initDReceive()
    initConfigJson()

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
            # print('args start', args, 'args_end')
            t2 = re.findall('\s*(.*)\s*\=\s*?(.*)?', args, re.M | re.I)
            for i in range(len(t2)):
                tmp[t2[i][0].strip()] = t2[i][1].strip()
        ret_list.append(tmp)

    return ret_list


def getRecListDataBy(name):
    l = getRecListData()
    for x in range(len(l)):
        if name == l[x]["name"]:
            return l[x]


def getRecList():
    ret_list = getRecListData()
    return mw.returnJson(True, 'ok', ret_list)


def addRec():
    args = getArgs()
    data = checkArgs(args, ['name', 'path', 'pwd', 'ps'])
    if not data[0]:
        return data[1]

    args_name = args['name']
    args_pwd = args['pwd']
    args_path = args['path']
    args_ps = args['ps']

    delRecBy(args_name)

    auth_path = appAuthPwd(args_name)
    pwd_content = args_name + ':' + args_pwd + "\n"
    mw.writeFile(auth_path, pwd_content)
    mw.execShell("chmod 600 " + auth_path)

    path = appConf()
    content = mw.readFile(path)

    con = "\n\n" + '[' + args_name + ']' + "\n"
    con += 'path = ' + args_path + "\n"
    con += 'comment = ' + args_ps + "\n"
    con += 'auth users = ' + args_name + "\n"
    con += 'ignore errors' + "\n"
    con += 'secrets file = ' + auth_path + "\n"
    con += 'read only = false'

    content = content.strip() + "\n" + con
    mw.writeFile(path, content)
    return mw.returnJson(True, '添加成功')


def getRec():
    args = getArgs()
    data = checkArgs(args, ['name'])
    if not data[0]:
        return data[1]

    name = args['name']

    if name == "":
        tmp = {}
        tmp["name"] = ""
        tmp["path"] = mw.getWwwDir()
        tmp["pwd"] = mw.getRandomString(16)
        return mw.returnJson(True, 'OK', tmp)

    data = getRecListDataBy(name)

    content = mw.readFile(data['secrets file'])
    pwd = content.strip().split(":")
    data['pwd'] = pwd[1]
    return mw.returnJson(True, 'OK', data)


def delRecBy(name):
    try:
        path = appConf()
        content = mw.readFile(path)

        reclist = getRecListData()
        ret_list_len = len(reclist)
        is_end = False
        next_name = ''
        for x in range(ret_list_len):
            tmp = reclist[x]
            if tmp['name'] == name:

                secrets_file = tmp['secrets file']
                tp = os.path.dirname(secrets_file)
                if os.path.exists(tp):
                    mw.execShell("rm -rf " + tp)

                if x + 1 == ret_list_len:
                    is_end = True
                else:
                    next_name = reclist[x + 1]['name']
        reg = ''
        if is_end:
            reg = '\[' + name + '\]\s*(.*)'
        else:
            reg = '\[' + name + '\]\s*(.*)\s*\[' + next_name + '\]'

        conre = re.search(reg,  content, re.S)
        content = content.replace(
            "[" + name + "]\n" + conre.groups()[0], '')
        mw.writeFile(path, content)
    except Exception as e:
        return False
    return True


def delRec():
    args = getArgs()
    data = checkArgs(args, ['name'])
    if not data[0]:
        return data[1]
    name = args['name']
    ok = delRecBy(name)
    if ok:
        return mw.returnJson(True, '删除成功!')
    return mw.returnJson(False, '删除失败!')


def cmdRecSecretKey():
    import base64

    args = getArgs()
    data = checkArgs(args, ['name'])
    if not data[0]:
        return data[1]

    name = args['name']
    info = getRecListDataBy(name)

    m = json.dumps(info)
    m = m.encode("utf-8")
    m = base64.b64encode(m)
    cmd = m.decode("utf-8")
    return mw.returnJson(True, 'OK!', cmd)


def cmdRecCmd():
    args = getArgs()
    data = checkArgs(args, ['name'])
    if not data[0]:
        return data[1]

    name = args['name']
    info = getRecListDataBy(name)
    ip = mw.getLocalIp()

    content = mw.readFile(info['secrets file'])
    pwd = content.strip().split(":")

    tmp_name = '/tmp/' + name + '.pass'

    cmd = 'echo "' + pwd[1] + '" > ' + tmp_name + '<br>'
    cmd += 'chmod 600 ' + tmp_name + ' <br>'
    cmd += 'rsync -arv --password-file=' + tmp_name + \
        ' --progress --delete  /project  ' + name + '@' + ip + '::' + name
    return mw.returnJson(True, 'OK!', cmd)


# ----------------------------- rsyncdSend start -------------------------


def lsyncdListFindIp(slist, ip):
    for x in range(len(slist)):
        if slist[x]["ip"] == ip:
            return (True, x)
    return (False, -1)


def lsyncdList():
    data = getDefaultConf()
    send = data['send']
    return mw.returnJson(True, "设置成功!", send)


def lsyncdAdd():

    args = getArgs()
    data = checkArgs(args, ['ip', 'name'])
    if not data[0]:
        return data[1]

    ip = args['ip']
    path = args['path']

    info = {
        "ip": ip,
        "path": path
    }

    data = getDefaultConf()
    slist = data['send']["list"]
    res = lsyncdListFindIp(slist, ip)
    if res[0]:
        list_index = res[1]
        slist[list_index] = info
    else:
        slist.append(info)
    data['send']["list"] = slist

    setDefaultConf(data)
    return mw.returnJson(True, "设置成功!")


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
    elif func == 'run_log':
        print(getLog())
    elif func == 'rec_list':
        print(getRecList())
    elif func == 'add_rec':
        print(addRec())
    elif func == 'del_rec':
        print(delRec())
    elif func == 'get_rec':
        print(getRec())
    elif func == 'cmd_rec_secret_key':
        print(cmdRecSecretKey())
    elif func == 'cmd_rec_cmd':
        print(cmdRecCmd())
    elif func == 'lsyncd_list':
        print(lsyncdList())
    elif func == 'lsyncd_add':
        print(lsyncdAdd())
    else:
        print('error')
