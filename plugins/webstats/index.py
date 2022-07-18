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


def getPluginName():
    return 'webstats'


def getPluginDir():
    return mw.getPluginDir() + '/' + getPluginName()


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


def luaConf():
    return mw.getServerDir() + '/web_conf/nginx/vhost/webstats.conf'


def status():
    path = luaConf()
    if not os.path.exists(path):
        return 'stop'
    return 'start'


def pSqliteDb(dbname='web_logs'):
    file = getServerDir() + '/webstats.db'
    name = 'webstats'
    if not os.path.exists(file):
        conn = mw.M(dbname).dbPos(getServerDir(), name)
        sql = mw.readFile(getPluginDir() + '/conf/init.sql')
        sql_list = sql.split(';')
        for index in range(len(sql_list)):
            conn.execute(sql_list[index], ())
    else:
        conn = mw.M(dbname).dbPos(getServerDir(), name)
    return conn


def initDreplace():

    service_path = getServerDir()

    pSqliteDb()

    path = luaConf()
    path_tpl = getPluginDir() + '/conf/webstats.conf'
    if not os.path.exists(path):
        content = mw.readFile(path_tpl)
        content = content.replace('{$SERVER_APP}', service_path)
        content = content.replace('{$ROOT_PATH}', mw.getServerDir())
        mw.writeFile(path, content)

    lua_dir = getServerDir() + "/lua"
    lua_dst = lua_dir + "/web_stats_log.lua"
    if not os.path.exists(lua_dst):
        mw.execShell('mkdir -p ' + lua_dir)
        lua_tpl = getPluginDir() + '/lua/web_stats_log.lua'
        content = mw.readFile(lua_tpl)
        content = content.replace('{$SERVER_APP}', service_path)
        content = content.replace('{$ROOT_PATH}', mw.getServerDir())
        mw.writeFile(lua_dst, content)

    debug_log = getServerDir() + "/debug.log"
    if not os.path.exists(debug_log):
        mw.execShell('mkdir -p ' + lua_dir)
        mw.writeFile(debug_log, '')

    return 'ok'


def start():
    initDreplace()
    mw.restartWeb()
    return 'ok'


def stop():
    path = luaConf()
    os.remove(path)
    mw.restartWeb()
    return 'ok'


def restart():
    initDreplace()
    return 'ok'


def reload():
    initDreplace()

    lua_dir = getServerDir() + "/lua"
    lua_dst = lua_dir + "/web_stats_log.lua"
    lua_tpl = getPluginDir() + '/lua/web_stats_log.lua'
    content = mw.readFile(lua_tpl)
    content = content.replace('{$SERVER_APP}', getServerDir())
    content = content.replace('{$ROOT_PATH}', mw.getServerDir())
    mw.writeFile(lua_dst, content)
    mw.restartWeb()
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
    elif func == 'run_info':
        print(runInfo())
    elif func == 'conf':
        print(getConf())
    else:
        print('error')
