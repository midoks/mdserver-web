# coding:utf-8

import sys
import io
import os
import time

sys.path.append(os.getcwd() + "/class/core")
import mw

app_debug = False
if mw.isAppleSystem():
    app_debug = True


# /usr/lib/systemd/system/mongod.service
# /var/lib/mongo

def getPluginName():
    return 'mongodb'


def getPluginDir():
    return mw.getPluginDir() + '/' + getPluginName()


def getServerDir():
    return mw.getServerDir() + '/' + getPluginName()


def getInitDFile():
    if app_debug:
        return '/tmp/' + getPluginName()
    return '/etc/init.d/' + getPluginName()


def getConf():
    if mw.isAppleSystem():
        path = getServerDir() + "/mongodb.conf"
        return path

    if os.path.exists("/etc/mongodb.conf"):
        return "/etc/mongodb.conf"
    return "/etc/mongod.conf"


def getConfTpl():
    path = getPluginDir() + "/config/mongodb.conf"
    return path


def getInitDTpl():
    path = getPluginDir() + "/init.d/" + getPluginName() + ".tpl"
    return path


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
    data = mw.execShell(
        "ps -ef|grep mongod |grep -v grep | grep -v python | grep -v mdserver-web | awk '{print $2}'")

    if data[0] == '':
        return 'stop'
    return 'start'


def initDreplace():

    file_tpl = getInitDTpl()
    service_path = os.path.dirname(os.getcwd())

    initD_path = getServerDir() + '/init.d'
    if not os.path.exists(initD_path):
        os.mkdir(initD_path)
    file_bin = initD_path + '/' + getPluginName()

    # initd replace
    content = mw.readFile(file_tpl)
    content = content.replace('{$SERVER_PATH}', service_path)
    mw.writeFile(file_bin, content)
    mw.execShell('chmod +x ' + file_bin)

    # config replace
    conf_content = mw.readFile(getConfTpl())
    conf_content = conf_content.replace('{$SERVER_PATH}', service_path)
    mw.writeFile(getServerDir() + '/mongodb.conf', conf_content)

    return file_bin


def start():
    if mw.isAppleSystem():
        file = initDreplace()
        data = mw.execShell(file + ' start')
        if data[1] == '':
            return 'ok'
        return 'fail'

    cmd = 'systemctl start mongod'
    if os.path.exists("/usr/lib/systemd/system/mongodb.service"):
        cmd = 'systemctl start mongodb'

    data = mw.execShell(cmd)
    if data[1] == '':
        return 'ok'
    return 'fail'


def stop():
    if mw.isAppleSystem():
        file = initDreplace()
        data = mw.execShell(file + ' stop')
        if data[1] == '':
            return 'ok'
        return 'fail'

    cmd = 'systemctl stop mongod'
    if os.path.exists("/usr/lib/systemd/system/mongodb.service"):
        cmd = 'systemctl stop mongodb'

    data = mw.execShell(cmd)
    if data[1] == '':
        return 'ok'
    return 'fail'


def reload():
    if os.path.exists("/tmp/mongodb-27017.sock"):
        mw.execShell('rm -rf ' + "/tmp/mongodb-27017.sock")
    if mw.isAppleSystem():
        file = initDreplace()
        data = mw.execShell(file + ' reload')
        if data[1] == '':
            return 'ok'
        return 'fail'

    cmd = 'systemctl reload mongod'
    if os.path.exists("/usr/lib/systemd/system/mongodb.service"):
        cmd = 'systemctl reload mongodb'

    data = mw.execShell(cmd)
    if data[1] == '':
        return 'ok'
    return 'fail'


def restart():
    if os.path.exists("/tmp/mongodb-27017.sock"):
        mw.execShell('rm -rf ' + "/tmp/mongodb-27017.sock")
    if mw.isAppleSystem():
        file = initDreplace()
        data = mw.execShell(file + ' reload')
        if data[1] == '':
            return 'ok'
        return 'fail'

    cmd = 'systemctl reload mongod'
    if os.path.exists("/usr/lib/systemd/system/mongodb.service"):
        cmd = 'systemctl reload mongodb'

    data = mw.execShell(cmd)
    if data[1] == '':
        return 'ok'
    return 'fail'


def runInfo():
    import pymongo
    client = pymongo.MongoClient(host='127.0.0.1', port=27017)
    db = client.admin
    serverStatus = db.command('serverStatus')

    listDbs = client.list_database_names()

    showDbList = []
    for x in range(len(listDbs)):
        mongd = client[listDbs[x]]
        stats = mongd.command({"dbstats": 1})
        showDbList.append(stats)
    # print(showDbList)
    # print(serverStatus)
    # for key, value in serverStatus.items():
    #     print(key, value)
    result = {}
    result["version"] = serverStatus['version']
    result["uptime"] = serverStatus['uptime']

    result['db_path'] = '/var/lib/mongo'

    if os.path.exists("/var/lib/mongodb"):
        result['db_path'] = '/var/lib/mongodb'

    if mw.isAppleSystem():
        result['db_path'] = getServerDir() + "/data"

    result["connections"] = serverStatus['connections']['current']
    if 'catalogStats' in serverStatus:
        result["collections"] = serverStatus['catalogStats']['collections']

    result["dbs"] = showDbList
    return mw.getJson(result)


def initdStatus():
    if not app_debug:
        if mw.isAppleSystem():
            return "Apple Computer does not support"

    if mw.isAppleSystem():
        initd_bin = getInitDFile()
        if os.path.exists(initd_bin):
            return 'ok'
        return 'fail'

    shell_cmd = 'systemctl status mongod | grep loaded | grep "enabled;"'

    if os.path.exists("/usr/lib/systemd/system/mongodb.service"):
        shell_cmd = 'systemctl status mongodb | grep loaded | grep "enabled;"'

    data = mw.execShell(shell_cmd)
    if data[0] == '':
        return 'fail'
    return 'ok'


def initdInstall():
    import shutil
    if not app_debug:
        if mw.isAppleSystem():
            return "Apple Computer does not support"

    if mw.isAppleSystem():
        source_bin = initDreplace()
        initd_bin = getInitDFile()
        shutil.copyfile(source_bin, initd_bin)
        mw.execShell('chmod +x ' + initd_bin)
        mw.execShell('chkconfig --add ' + getPluginName())

    if os.path.exists("/usr/lib/systemd/system/mongodb.service"):
        mw.execShell('systemctl enable mongodb')
    else:
        mw.execShell('systemctl enable mongod')
    return 'ok'


def initdUinstall():
    if not app_debug:
        if mw.isAppleSystem():
            return "Apple Computer does not support"
    if mw.isAppleSystem():
        mw.execShell('chkconfig --del ' + getPluginName())
        initd_bin = getInitDFile()
        os.remove(initd_bin)

    if os.path.exists("/usr/lib/systemd/system/mongodb.service"):
        mw.execShell('systemctl disable mongodb')
    else:
        mw.execShell('systemctl disable mongod')
    return 'ok'


def runLog():
    if mw.isAppleSystem():
        return getServerDir() + '/logs/mongodb.log'

    if os.path.exists("/var/log/mongodb/mongodb.log"):
        return "/var/log/mongodb/mongodb.log"

    return "/var/log/mongodb/mongod.log"

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
    elif func == 'run_info':
        print(runInfo())
    elif func == 'conf':
        print(getConf())
    elif func == 'run_log':
        print(runLog())
    else:
        print('error')
