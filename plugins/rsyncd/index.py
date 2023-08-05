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

    # data = mw.execShell(
    #     "ps -ef|grep lsyncd |grep -v grep | grep -v python | awk '{print $2}'")
    # if data[0] == '':
    #     return 'stop'

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


def __release_port(port):
    try:
        import firewall_api
        firewall_api.firewall_api().addAcceptPortArgs(port, 'RSYNC同步', 'port')
        return port
    except Exception as e:
        return "Release failed {}".format(e)


def openPort():
    for i in ["873"]:
        __release_port(i)
    return True


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

    lock_file = getServerDir() + "/installed_rsyncd.pl"
    # systemd
    systemDir = mw.systemdCfgDir()
    systemService = systemDir + '/rsyncd.service'
    systemServiceTpl = getPluginDir() + '/init.d/rsyncd.service.tpl'
    if not os.path.exists(lock_file):

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

        mw.writeFile(lock_file, "ok")
        openPort()

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

    shell_cmd = 'systemctl status lsyncd | grep loaded | grep "enabled;"'
    data = mw.execShell(shell_cmd)
    if data[0] == '':
        return 'fail'

    return 'ok'


def initdInstall():
    if mw.isAppleSystem():
        return "Apple Computer does not support"

    mw.execShell('systemctl enable lsyncd')
    mw.execShell('systemctl enable rsyncd')
    return 'ok'


def initdUinstall():
    if not app_debug:
        if mw.isAppleSystem():
            return "Apple Computer does not support"

    mw.execShell('systemctl diable lsyncd')
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

    if not mw.isAppleSystem():
        os.system("mkdir -p " + args_path + " &")
        os.system("chown -R  www:www " + args_path + " &")
        os.system("chmod -R 755 " + args_path + " &")

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
        tmp["comment"] = ""
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

    secrets_file = info['secrets file']
    content = mw.readFile(info['secrets file'])
    pwd = content.strip().split(":")

    m = {"A": info['name'], "B": pwd[1], "C": "873"}
    m = json.dumps(m)
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

def lsyncdReload():
    data = mw.execShell(
        "ps -ef|grep lsyncd |grep -v grep | grep -v python | awk '{print $2}'")
    if data[0] == '':
        mw.execShell('systemctl start lsyncd')
    else:
        mw.execShell('systemctl restart lsyncd')


def makeLsyncdConf(data):
    # print(data)

    lsyncd_data = data['send']
    lsyncd_setting = lsyncd_data['default']

    content = "settings {\n"
    for x in lsyncd_setting:
        v = lsyncd_setting[x]
        # print(v, type(v))
        if type(v) == str:
            content += "\t" + x + ' = "' + v + "\",\n"
        elif type(v) == int:
            content += "\t" + x + ' = ' + str(v) + ",\n"
    content += "}\n\n"

    lsyncd_list = lsyncd_data['list']

    rsync_bin = mw.execShell('which rsync')[0].strip()
    send_dir = getServerDir() + "/send"

    if len(lsyncd_list) > 0:
        for x in range(len(lsyncd_list)):

            t = lsyncd_list[x]
            name_dir = send_dir + "/" + t["name"]
            if not os.path.exists(name_dir):
                mw.execShell("mkdir -p " + name_dir)

            cmd_exclude = name_dir + "/exclude"
            cmd_exclude_txt = ""
            for x in t['exclude']:
                cmd_exclude_txt += x + "\n"
            mw.writeFile(cmd_exclude, cmd_exclude_txt)
            cmd_pass = name_dir + "/pass"
            mw.writeFile(cmd_pass, t['password'])
            mw.execShell("chmod 600 " + cmd_pass)

            delete_ok = ' '
            if t['delete'] == "true":
                delete_ok = ' --delete '

            remote_addr = t['name'] + '@' + t['ip'] + "::" + t['name']
            cmd = rsync_bin + " -avzP " + "--port=" + str(t['rsync']['port']) + " --bwlimit=" + t['rsync'][
                'bwlimit'] + delete_ok + "  --exclude-from=" + cmd_exclude + " --password-file=" + cmd_pass + " " + t["path"] + " " + remote_addr
            mw.writeFile(name_dir + "/cmd", cmd)
            mw.execShell("cmod +x " + name_dir + "/cmd")

            if t['realtime'] == "false":
                continue

            # print(x, t)
            content += "sync {\n"
            content += "\tdefault.rsync,\n"
            content += "\tsource = \"" + t['path'] + "\",\n"
            content += "\ttarget = \"" + remote_addr + "\",\n"
            content += "\tdelete = " + t['delete'] + ",\n"
            content += "\tdelay = " + t['delay'] + ",\n"
            content += "\tinit = false,\n"

            exclude_str = json.dumps(t['exclude'])
            exclude_str = exclude_str.replace("[", "{")
            exclude_str = exclude_str.replace("]", "}")
            # print(exclude_str)
            content += "\texclude = " + exclude_str + ",\n"

            # rsync
            content += "\trsync = {\n"
            content += "\t\tbinary = \"" + rsync_bin + "\",\n"
            content += "\t\tarchive = true,\n"
            content += "\t\tverbose = true,\n"
            content += "\t\tcompress = " + t['rsync']['compress'] + ",\n"
            content += "\t\tpassword_file = \"" + cmd_pass + "\",\n"

            content += "\t\t_extra = {\"--bwlimit=" + t['rsync'][
                'bwlimit'] + "\", \"--port=" + str(t['rsync']['port']) + "\"},\n"

            content += "\t}\n"
            content += "}\n"

    path = getServerDir() + "/lsyncd.conf"
    mw.writeFile(path, content)

    lsyncdReload()

    import tool_task
    tool_task.createBgTask(lsyncd_list)


def lsyncdListFindIp(slist, ip):
    for x in range(len(slist)):
        if slist[x]["ip"] == ip:
            return (True, x)
    return (False, -1)


def lsyncdListFindName(slist, name):
    for x in range(len(slist)):
        if slist[x]["name"] == name:
            return (True, x)
    return (False, -1)


def lsyncdList():
    data = getDefaultConf()
    send = data['send']
    return mw.returnJson(True, "设置成功!", send)


def lsyncdGet():
    import base64
    args = getArgs()
    data = checkArgs(args, ['name'])
    if not data[0]:
        return data[1]

    name = args['name']
    data = getDefaultConf()

    slist = data['send']["list"]
    res = lsyncdListFindName(slist, name)

    rsync = {
        'bwlimit': "1024",
        "compress": "true",
        "archive": "true",
        "verbose": "true"
    }

    info = {
        "secret_key": '',
        "ip": '',
        "path": mw.getServerDir(),
        'rsync': rsync,
        'realtime': "true",
        'delete': "false",
    }
    if res[0]:
        list_index = res[1]
        info = slist[list_index]
        m = {"A": info['name'], "B": info["password"], "C": "873"}
        m = json.dumps(m)
        m = m.encode("utf-8")
        m = base64.b64encode(m)
        info['secret_key'] = m.decode("utf-8")
    return mw.returnJson(True, "OK", info)


def lsyncdDelete():
    args = getArgs()
    data = checkArgs(args, ['name'])
    if not data[0]:
        return data[1]

    name = args['name']
    data = getDefaultConf()
    slist = data['send']["list"]
    res = lsyncdListFindName(slist, name)
    retdata = {}
    if res[0]:
        list_index = res[1]
        slist.pop(list_index)

    data['send']["list"] = slist
    setDefaultConf(data)
    makeLsyncdConf(data)
    return mw.returnJson(True, "OK")


def lsyncdAdd():
    import base64

    args = getArgs()
    data = checkArgs(args, ['ip', 'conn_type', 'path', 'delay', 'period'])
    if not data[0]:
        return data[1]

    ip = args['ip']
    path = args['path']

    if not mw.isAppleSystem():
        os.system("mkdir -p " + path + " &")
        os.system("chown -R  www:www " + path + " &")
        os.system("chmod -R 755 " + path + " &")

    conn_type = args['conn_type']

    delete = args['delete']
    realtime = args['realtime']
    delay = args['delay']
    bwlimit = args['bwlimit']
    compress = args['compress']
    period = args['period']

    hour = args['hour']
    minute = args['minute']
    minute_n = args['minute-n']

    info = {
        "ip": ip,
        "path": path,
        "delete": delete,
        "realtime": realtime,
        'delay': delay,
        "conn_type": conn_type,
        "period": period,
        "hour": hour,
        "minute": minute,
        "minute-n": minute_n,
    }

    if conn_type == "key":

        secret_key_check = checkArgs(args, ['secret_key'])
        if not secret_key_check[0]:
            return secret_key_check[1]

        secret_key = args['secret_key']
        try:
            m = base64.b64decode(secret_key)
            m = json.loads(m)
            info['name'] = m['A']
            info['password'] = m['B']
            info['port'] = m['C']
        except Exception as e:
            return mw.returnJson(False, "接收密钥格式错误!")
    else:
        data = checkArgs(args, ['sname', 'password'])
        if not data[0]:
            return data[1]

        info['name'] = args['sname']
        info['password'] = args['password']
        info['port'] = args['port']

    rsync = {
        'bwlimit': bwlimit,
        "port": info['port'],
        "compress": compress,
        "archive": "true",
        "verbose": "true"
    }

    info['rsync'] = rsync

    data = getDefaultConf()

    slist = data['send']["list"]
    res = lsyncdListFindName(slist, info['name'])

    if not 'exclude' in info:
        if res[0]:
            info["exclude"] = slist[res[1]]['exclude']
        else:
            info["exclude"] = [
                "/**.upload.tmp", "**/*.log", "**/*.tmp",
                "**/*.temp", ".git", ".gitignore", ".user.ini",
            ]

    if res[0]:
        list_index = res[1]
        slist[list_index] = info
    else:
        slist.append(info)

    data['send']["list"] = slist

    setDefaultConf(data)
    makeLsyncdConf(data)
    return mw.returnJson(True, "设置成功!")


def lsyncdRun():
    args = getArgs()
    data = checkArgs(args, ['name'])
    if not data[0]:
        return data[1]

    send_dir = getServerDir() + "/send"
    name = args['name']
    app_dir = send_dir + "/" + name

    cmd = "bash " + app_dir + "/cmd >> " + app_dir + "/run.log" + " 2>&1 &"
    mw.execShell(cmd)
    return mw.returnJson(True, "执行成功!")


def lsyncdConfLog():
    logs_path = getServerDir() + "/lsyncd.log"
    return logs_path


def lsyncdLog():
    args = getArgs()
    data = checkArgs(args, ['name'])
    if not data[0]:
        return data[1]

    send_dir = getServerDir() + "/send"
    name = args['name']
    app_dir = send_dir + "/" + name
    return app_dir + "/run.log"


def lsyncdGetExclude():
    args = getArgs()
    data = checkArgs(args, ['name'])
    if not data[0]:
        return data[1]

    data = getDefaultConf()
    slist = data['send']["list"]
    res = lsyncdListFindName(slist, args['name'])
    i = res[1]
    info = slist[i]
    return mw.returnJson(True, "OK!", info['exclude'])


def lsyncdRemoveExclude():
    args = getArgs()
    data = checkArgs(args, ['name', 'exclude'])
    if not data[0]:
        return data[1]

    exclude = args['exclude']

    data = getDefaultConf()
    slist = data['send']["list"]
    res = lsyncdListFindName(slist, args['name'])
    i = res[1]
    info = slist[i]

    exclude_list = info['exclude']
    exclude_pop_key = -1
    for x in range(len(exclude_list)):
        if exclude_list[x] == exclude:
            exclude_pop_key = x

    if exclude_pop_key > -1:
        exclude_list.pop(exclude_pop_key)

    data['send']["list"][i]['exclude'] = exclude_list
    setDefaultConf(data)
    makeLsyncdConf(data)
    return mw.returnJson(True, "OK!", exclude_list)


def lsyncdAddExclude():
    args = getArgs()
    data = checkArgs(args, ['name', 'exclude'])
    if not data[0]:
        return data[1]

    exclude = args['exclude']

    data = getDefaultConf()
    slist = data['send']["list"]
    res = lsyncdListFindName(slist, args['name'])
    i = res[1]
    info = slist[i]

    exclude_list = info['exclude']
    exclude_list.append(exclude)

    data['send']["list"][i]['exclude'] = exclude_list
    setDefaultConf(data)
    makeLsyncdConf(data)
    return mw.returnJson(True, "OK!", exclude_list)

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
    elif func == 'lsyncd_get':
        print(lsyncdGet())
    elif func == 'lsyncd_delete':
        print(lsyncdDelete())
    elif func == 'lsyncd_run':
        print(lsyncdRun())
    elif func == 'lsyncd_log':
        print(lsyncdLog())
    elif func == 'lsyncd_conf_log':
        print(lsyncdConfLog())
    elif func == 'lsyncd_get_exclude':
        print(lsyncdGetExclude())
    elif func == 'lsyncd_remove_exclude':
        print(lsyncdRemoveExclude())
    elif func == 'lsyncd_add_exclude':
        print(lsyncdAddExclude())
    else:
        print('error')
