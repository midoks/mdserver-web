# coding:utf-8

import sys
import io
import os
import time
import re
import string
import subprocess
import json

web_dir = os.getcwd() + "/web"
if os.path.exists(web_dir):
    sys.path.append(web_dir)
    os.chdir(web_dir)

import core.mw as mw

app_debug = False
if mw.isAppleSystem():
    app_debug = True


def getPluginName():
    return 'cryptocurrency_trade'


def getPluginDir():
    return mw.getPluginDir() + '/' + getPluginName()


def getServerDir():
    return mw.getServerDir() + '/' + getPluginName()


def contentReplace(content):
    service_path = mw.getServerDir()
    content = content.replace('{$ROOT_PATH}', mw.getFatherDir())
    content = content.replace('{$SERVER_PATH}', service_path)
    content = content.replace(
        '{$SERVER_APP}', service_path + '/' + getPluginName())
    return content


def getArgs():
    args = sys.argv[2:]
    tmp = {}
    args_len = len(args)
    if args_len == 1:
        t = args[0].strip('{').strip('}')
        if t.strip() == '':
            tmp = []
        else:
            t = t.split(':', 1)
            tmp[t[0]] = t[1]
        tmp[t[0]] = t[1]
    elif args_len > 1:

        for i in range(len(args)):
            t = args[i].split(':', 1)
            tmp[t[0]] = t[1]
    return tmp


def checkArgs(data, ck=[]):
    for i in range(len(ck)):
        if not ck[i] in data:
            return (False, mw.returnJson(False, '参数:(' + ck[i] + ')没有!'))
    return (True, mw.returnJson(True, 'ok'))


def isSqlError(mysqlMsg):
    # 检测数据库执行错误
    mysqlMsg = str(mysqlMsg)
    if "MySQLdb" in mysqlMsg:
        return mw.returnJson(False, 'MySQLdb组件缺失! <br>进入SSH命令行输入: pip install mysql-python | pip install mysqlclient==2.0.3')
    if "2002," in mysqlMsg:
        return mw.returnJson(False, '数据库连接失败,请检查数据库服务是否启动!')
    if "2003," in mysqlMsg:
        return mw.returnJson(False, "Can't connect to MySQL server on '127.0.0.1' (61)")
    if "using password:" in mysqlMsg:
        return mw.returnJson(False, '数据库密码错误')
    if "1045" in mysqlMsg:
        return mw.returnJson(False, '连接错误!')
    if "SQL syntax" in mysqlMsg:
        return mw.returnJson(False, 'SQL语法错误!')
    if "Connection refused" in mysqlMsg:
        return mw.returnJson(False, '数据库连接失败,请检查数据库服务是否启动!')
    if "1133" in mysqlMsg:
        return mw.returnJson(False, '数据库用户不存在!')
    if "1007" in mysqlMsg:
        return mw.returnJson(False, '数据库已经存在!')
    return None


def initDreplace():
    log_dir = getServerDir() + '/logs'
    if not os.path.exists(log_dir):
        d = mw.execShell('mkdir -p ' + log_dir)

        data = getConfigData()
        data['token'] = ['btc']
        writeConf(data)

    return True


def status():
    initDreplace()
    return 'start'


def start():
    syncDataAddTaskInstall()
    return 'ok'


def stop():
    syncDataAddTaskUninstall()
    return 'ok'


def op():
    return 'ok'


def getConfigData():
    cfg_path = getServerDir() + "/data.cfg"
    if not os.path.exists(cfg_path):
        mw.writeFile(cfg_path, '{}')
    t = mw.readFile(cfg_path)
    return json.loads(t)


def writeConf(data):
    cfg_path = getServerDir() + "/data.cfg"
    mw.writeFile(cfg_path, json.dumps(data))
    return True


def getDbConf():
    data = getConfigData()
    if 'db' in data:
        return mw.returnJson(True, 'ok', data['db'])
    return mw.returnJson(False, 'ok', {})


def setDbConf():
    args = getArgs()
    data_args = checkArgs(args, ['db_host', 'db_port',
                                 'db_name', 'db_user', 'db_pass'])
    if not data_args[0]:
        return data_args[1]

    data = getConfigData()
    data['db'] = args
    writeConf(data)

    db = mw.getMyORM()

    db.setHost(args['db_host'])
    db.setPort(args['db_port'])
    db.setUser(args['db_user'])
    db.setPwd(args['db_pass'])
    testdata = db.query('select version()')

    isError = isSqlError(testdata)
    if isError != None:
        return isError

    return mw.returnJson(True, '保存成功,并连通成功!', [])


def getUserConf():
    data = getConfigData()
    if 'user' in data:
        return mw.returnJson(True, 'ok', data['user'])
    return mw.returnJson(False, 'ok', {})


def getUserConf():
    data = getConfigData()
    if 'user' in data:
        try:
            udata = mw.deDoubleCrypt('mw', data['user'])
            udata = json.loads(udata)

            return mw.returnJson(True, 'ok', udata)
        except Exception as e:
            pass
    return mw.returnJson(False, 'ok', {})


def setUserConf():
    args = getArgs()
    data_args = checkArgs(args, ['app_key', 'secret',
                                 'password', 'uid', 'exchange'])
    if not data_args[0]:
        return data_args[1]

    data = getConfigData()
    data['user'] = mw.enDoubleCrypt('mw', json.dumps(args))
    writeConf(data)

    return mw.returnJson(True, '保存成功!', [])


def syncDataList():
    data = getConfigData()

    name = "ct_task"
    if 'token' in data:

        rdata = {}
        rdata['task_status'] = False
        sup_path = mw.getServerDir() + '/supervisor'
        sup_task_dst = sup_path + '/conf.d/' + name + '.ini'
        if os.path.exists(sup_task_dst):
            rdata['task_status'] = True

        rdata['list'] = data['token']
        return mw.returnJson(True, 'ok', rdata)
    return mw.returnJson(False, 'ok')


def syncDataAdd():
    args = getArgs()
    data_args = checkArgs(args, ['token'])
    if not data_args[0]:
        return data_args[1]

    add_token = args['token']
    data = getConfigData()

    if 'token' in data and data['token']:
        if not add_token in data['token']:
            data['token'].append(add_token)
    else:
        data['token'] = [add_token]
    writeConf(data)

    return mw.returnJson(True, '保存成功!')


def restartSup():
    cmd = 'python3 plugins/supervisor/index.py restart'
    mw.execShell(cmd)


def restartSupDst(name):
    cmd = 'python3 plugins/supervisor/index.py restart_job  {"name":"' + \
        name + '","status":"stop"}'
    mw.execShell(cmd)


def syncDataAddTaskUninstall():
    sup_path = mw.getServerDir() + '/supervisor'
    if not os.path.exists(sup_path):
        return mw.returnJson(False, '需要安装并启动supervisor插件')

    name = "ct_task"
    sup_task_dst = sup_path + '/conf.d/' + name + '.ini'
    if os.path.exists(sup_task_dst):
        mw.execShell('rm -rf ' + sup_task_dst)

    restartSup()
    return mw.returnJson(True, '删除同步数据任务成功!')


def syncDataAddTaskInstall():
    sup_path = mw.getServerDir() + '/supervisor'
    if not os.path.exists(sup_path):
        return mw.returnJson(False, '需要安装并启动supervisor插件')

    name = "ct_task"
    sup_task_tpl = getPluginDir() + '/conf/sup_task.tpl'
    sup_task_dst = sup_path + '/conf.d/' + name + '.ini'
    content = mw.readFile(sup_task_tpl)
    content = content.replace(
        '{$RUN_ROOT}', mw.getServerDir() + '/mdserver-web')
    content = content.replace(
        '{$SUP_ROOT}', sup_path)
    content = content.replace(
        '{$NAME}', name)

    mw.writeFile(sup_task_dst, content)
    restartSup()
    return mw.returnJson(True, '添加同步数据任务成功!')


def syncDataAddTask():
    args = getArgs()
    data_args = checkArgs(args, ['check'])
    if not data_args[0]:
        return data_args[1]

    if args['check'] == "0":
        return syncDataAddTaskUninstall()
    return syncDataAddTaskInstall()


def syncDataDelete():
    args = getArgs()
    data_args = checkArgs(args, ['token'])
    if not data_args[0]:
        return data_args[1]

    del_token = args['token']
    data = getConfigData()

    if 'token' in data:
        data['token'].remove(del_token)
    writeConf(data)

    return mw.returnJson(True, '删除成功!')


if __name__ == "__main__":
    func = sys.argv[1]
    if func == 'status':
        print(status())
    elif func == 'start':
        print(start())
    elif func == 'stop':
        print(stop())
    elif func == 'restart':
        print(op())
    elif func == 'reload':
        print(op())
    elif func == 'get_db_conf':
        print(getDbConf())
    elif func == 'set_db_conf':
        print(setDbConf())
    elif func == 'get_user_conf':
        print(getUserConf())
    elif func == 'set_user_conf':
        print(setUserConf())
    elif func == 'sync_data_list':
        print(syncDataList())
    elif func == 'sync_data_add':
        print(syncDataAdd())
    elif func == 'sync_data_delete':
        print(syncDataDelete())
    elif func == 'sync_data_add_task':
        print(syncDataAddTask())
    else:
        print('error')
