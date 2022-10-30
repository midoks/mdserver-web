# coding:utf-8

import sys
import io
import os
import time
import re
import json

# print(sys.platform)
if sys.platform != "darwin":
    os.chdir("/www/server/mdserver-web")


sys.path.append(os.getcwd() + "/class/core")
import mw

_ver = sys.version_info
is_py2 = (_ver[0] == 2)
is_py3 = (_ver[0] == 3)

DEBUG = False

if is_py2:
    reload(sys)
    sys.setdefaultencoding('utf-8')

app_debug = False
if mw.isAppleSystem():
    app_debug = True


def getPluginName():
    return 'backup_ftp'


def getPluginDir():
    return mw.getPluginDir() + '/' + getPluginName()


sys.path.append(getPluginDir() + "/class")
from ftp_client import FtpPSClient


def getServerDir():
    return mw.getServerDir() + '/' + getPluginName()


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


def status():
    return 'start'


def getConf():
    cfg = getServerDir() + "/cfg.json"
    if not os.path.exists(cfg):
        return mw.returnJson(False, "未配置", [])
    data = mw.readFile(cfg)
    data = json.loads(data)
    return mw.returnJson(True, "OK", data)


def setConf():
    args = getArgs()
    data = checkArgs(args, ['use_sftp', 'ftp_user',
                            'ftp_pass', 'ftp_host', 'backup_path'])
    if not data[0]:
        return data[1]

    cfg = getServerDir() + "/cfg.json"

    values = ['ftp_user',
              'ftp_pass',
              'ftp_host']
    for v in values:
        if args[v] == '':
            return mw.returnJson(False, '必填资料不能为空，请核实!', [])

    if args['backup_path'] == '':
        args['backup_path'] = "/backup"

    try:
        ftp = FtpPSClient(load_config=False)
        ftp.injection_config(args)
        data = ftp.getList("/")
        if data:
            mw.writeFile(cfg, mw.getJson(args))
            return mw.returnJson(True, '设置成功', [])
    except Exception as e:
        return mw.returnJson(False, "FTP校验失败，请核实!\n" + str(e), [])


def getList():
    cfg = getServerDir() + "/cfg.json"
    if not os.path.exists(cfg):
        return mw.returnJson(False, "未配置FTP,请点击`账户设置`", [])

    args = getArgs()
    data = checkArgs(args, ['path'])
    if not data[0]:
        return data[1]

    try:
        ftp = FtpPSClient()
        flist = ftp.getList(args['path'])
        return mw.returnJson(True, "ok", flist)
    except Exception as e:
        return mw.returnJson(False, str(e), [])


def createDir():
    cfg = getServerDir() + "/cfg.json"
    if not os.path.exists(cfg):
        return mw.returnJson(False, "未配置FTP,请点击`账户设置`", [])

    args = getArgs()
    data = checkArgs(args, ['path', 'name'])
    if not data[0]:
        return data[1]

    ftp = FtpPSClient()
    isok = ftp.createDir(args['path'], args['name'])
    if isok:
        return mw.returnJson(True, "创建成功")
    return mw.returnJson(False, "创建失败")


def deleteDir():
    args = getArgs()
    data = checkArgs(args, ['dir_name', 'path'])
    if not data[0]:
        return data[1]

    ftp = FtpPSClient()
    isok = ftp.deleteDir(args['path'], args['dir_name'])
    if isok:
        return mw.returnJson(True, "删除成功")
    return mw.returnJson(False, "删除失败")


def deleteFile():
    args = getArgs()
    data = checkArgs(args, ['path', 'filename'])
    if not data[0]:
        return data[1]

    ftp = FtpPSClient()
    isok = ftp.deleteFile(args['path'] + "/" + args['filename'])
    if isok:
        return mw.returnJson(True, "删除成功")
    return mw.returnJson(False, "删除失败")


def backupAllFunc(stype):
    os.chdir(mw.getRunDir())

    name = sys.argv[2]
    num = sys.argv[3]

    args = stype + " " + name + " " + num

    cmd = 'python3 ' + mw.getRunDir() + '/scripts/backup.py ' + args
    os.system(cmd)

    # 开始执行上传信息

    prefix_dict = {
        "site": "web",
        "database": "db",
        "path": "path",
    }

    find_path = mw.getBackupDir() + '/' + stype + '/' + \
        prefix_dict[stype] + '_' + name

    find_new_file = "ls " + find_path + \
        "_* | grep '.gz' | cut -d \  -f 1 | awk 'END {print}'"

    filename = mw.execShell(find_new_file)[0].strip()
    if filename == "":
        print("not find upload file!")
        return False

    ftp = FtpPSClient()
    ftp.uploadFile(filename, stype)

    return True


def backupSite():
    # 备份站点
    pass


def in_array(name, arr=[]):
    for x in arr:
        if name == x:
            return True
    return False


def installPreInspection():
    return 'ok'

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
    elif func == 'install_pre_inspection':
        print(installPreInspection())
    elif func == 'conf':
        print(getConf())
    elif func == 'set_config':
        print(setConf())
    elif func == "get_list":
        print(getList())
    elif func == "create_dir":
        print(createDir())
    elif func == "delete_dir":
        print(deleteDir())
    elif func == 'delete_file':
        print(deleteFile())
    elif in_array(func, ['site', 'database', 'path']):
        print(backupAllFunc(func))
    else:
        print('error')
