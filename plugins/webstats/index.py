# coding:utf-8

import sys
import io
import os
import time
import json

sys.path.append(os.getcwd() + "/class/core")
import mw


app_debug = False
if mw.isAppleSystem():
    app_debug = True


def getPluginName():
    return 'webstats'


def getPluginDir():
    return mw.getPluginDir() + '/' + getPluginName()


sys.path.append(getPluginDir() + "/class")
from LuaMaker import LuaMaker


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


def pSqliteDb(dbname='web_logs', site_name='unset'):
    db_dir = getServerDir() + '/logs/' + site_name

    if not os.path.exists(db_dir):
        mw.execShell('mkdir -p ' + db_dir)

    name = 'logs'
    file = db_dir + '/' + name + '.db'

    if not os.path.exists(file):
        conn = mw.M(dbname).dbPos(db_dir, name)
        sql = mw.readFile(getPluginDir() + '/conf/init.sql')
        sql_list = sql.split(';')
        for index in range(len(sql_list)):
            conn.execute(sql_list[index], ())
    else:
        conn = mw.M(dbname).dbPos(getServerDir(), name)
    return conn


def makeSiteConfig():
    siteM = mw.M('sites')
    domainM = mw.M('domain')
    slist = siteM.field('id,name').where(
        'status=?', (1,)).order('id desc').select()

    data = []
    for s in slist:
        tmp = {}
        tmp['name'] = s['name']

        dlist = domainM.field('id,name').where(
            'pid=?', (s['id'],)).order('id desc').select()

        _t = []
        for d in dlist:
            _t.append(d['name'])

        tmp['domains'] = _t
        data.append(tmp)

    return data


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
        # content = content.replace('{$SERVER_PATH}', service_path)
        content = content.replace('{$SERVER_APP}', service_path)
        content = content.replace('{$ROOT_PATH}', mw.getServerDir())
        mw.writeFile(lua_dst, content)

    content = makeSiteConfig()
    for index in range(len(content)):
        pSqliteDb('web_log', content[index]['name'])

    lua_site_json = lua_dir + "/sites.json"
    if not os.path.exists(lua_site_json):
        mw.writeFile(lua_site_json, json.dumps(content))

    lua_site = lua_dir + "/sites.lua"
    if not os.path.exists(lua_site):
        config_sites = LuaMaker.makeLuaTable(content)
        sites_str = "return " + config_sites
        mw.writeFile(lua_site, sites_str)

    log_path = getServerDir() + "/logs"
    if not os.path.exists(log_path):
        mw.execShell('mkdir -p ' + log_path)

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
