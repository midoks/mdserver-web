# coding: utf-8


import time
import os
import sys
import re
import subprocess

web_dir = os.getcwd() + "/web"
if os.path.exists(web_dir):
    sys.path.append(web_dir)
    os.chdir(web_dir)

import core.mw as mw

app_debug = False
if mw.isAppleSystem():
    app_debug = True


def getPluginName():
    return 'doh'


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
        t = t.split(':', 1)
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


def getInitdConfTpl():
    path = getPluginDir() + "/init.d/gitea.tpl"
    return path


def getInitdConf():
    path = getServerDir() + "/init.d/doh"
    return path

    if not os.path.exists(path):
        return mw.returnJson(False, "请先安装初始化!<br/>默认地址:http://" + mw.getLocalIp() + ":3000")
    return path


def getConfTpl():
    path = getPluginDir() + "/config/config.toml"
    return path


def status():
    data = mw.execShell(
        "ps -ef|grep " + getPluginName() + " |grep -v grep | grep -v python | awk '{print $2}'")
    if data[0] == '':
        return 'stop'
    return 'start'


def getHomeDir():
    if mw.isAppleSystem():
        user = mw.execShell(
            "who | sed -n '2, 1p' |awk '{print $1}'")[0].strip()
        return '/Users/' + user
    else:
        return 'www'



def contentReplace(content):

    service_path = mw.getServerDir()
    content = content.replace('{$ROOT_PATH}', mw.getFatherDir())
    content = content.replace('{$SERVER_PATH}', service_path)
    return content


def initDreplace():

    file_tpl = getInitdConfTpl()
    service_path = mw.getServerDir()


    conf_toml = getServerDir() + '/config.toml'
    if not os.path.exists(conf_toml):
        conf_tpl = getConfTpl()
        content = mw.readFile(conf_tpl)
        mw.writeFile(conf_toml, content)

    # systemd
    systemDir = mw.systemdCfgDir()
    systemService = systemDir + '/doh.service'
    systemServiceTpl = getPluginDir() + '/init.d/doh.service.tpl'
    if os.path.exists(systemDir) and not os.path.exists(systemService):
        service_path = mw.getServerDir()
        se_content = mw.readFile(systemServiceTpl)
        se_content = se_content.replace('{$SERVER_PATH}', service_path)
        mw.writeFile(systemService, se_content)
        mw.execShell('systemctl daemon-reload')

    log_path = getServerDir() + '/log'
    if not os.path.exists(log_path):
        os.mkdir(log_path)

    return file_bin



def getSshPort():
    content = mw.readFile(getConf())
    rep = r'SSH_PORT\s*=\s*(.*)'
    tmp = re.search(rep, content)
    if not tmp:
        return ''
    return tmp.groups()[0]


def getHttpPort():
    content = mw.readFile(getConf())
    rep = r'HTTP_PORT\s*=\s*(.*)'
    tmp = re.search(rep, content)
    if not tmp:
        return ''
    return tmp.groups()[0]


def getRootPath():
    content = mw.readFile(getConf())
    rep = r'ROOT\s*=\s*(.*)'
    tmp = re.search(rep, content)
    if not tmp:
        return ''
    return tmp.groups()[0]


def getDbConfValue():
    conf = getConf()
    if not os.path.exists(conf):
        return {}

    content = mw.readFile(conf)
    rep_scope = r"\[database\](.*?)\["
    tmp = re.findall(rep_scope, content, re.S)

    rep = '(\\w*)\\s*=\\s*(.*)'
    tmp = re.findall(rep, tmp[0])
    r = {}
    for x in range(len(tmp)):
        k = tmp[x][0]
        v = tmp[x][1]
        r[k] = v
    return r


def pMysqlDb(conf):
    host = conf['HOST'].split(':')
    # pymysql
    db = mw.getMyORM()
    # MySQLdb |
    # db = mw.getMyORMDb()

    db.setPort(int(host[1]))
    db.setUser(conf['USER'])

    if 'PASSWD' in conf:
        db.setPwd(conf['PASSWD'])
    else:
        db.setPwd(conf['PASSWORD'])

    db.setDbName(conf['NAME'])
    # db.setSocket(getSocketFile())
    db.setCharset("utf8")
    return db


def pSqliteDb(conf):
    # print(conf)
    import db
    psDb = db.Sql()

    # 默认
    gsdir = getServerDir() + '/data'
    dbname = 'gitea'
    if conf['PATH'][0] == '/':
        # 绝对路径
        pass
    else:
        path = conf['PATH'].split('/')
        gsdir = getServerDir() + '/' + path[0]
        dbname = path[1].split('.')[0]

    # print(gsdir, dbname)
    psDb.dbPos(gsdir, dbname)
    return psDb


def getGiteaDbType(conf):

    if 'DB_TYPE' in conf:
        return conf['DB_TYPE']

    if 'TYPE' in conf:
        return conf['TYPE']

    return 'NONE'


def pQuery(sql):
    conf = getDbConfValue()
    gtype = getGiteaDbType(conf)
    if gtype == 'sqlite3':
        db = pSqliteDb(conf)
        data = db.query(sql, []).fetchall()
        return data
    elif gtype == 'mysql':
        db = pMysqlDb(conf)
        return db.query(sql)

    print("仅支持mysql|sqlite3配置")
    exit(0)


def isSqlError(mysqlMsg):
    # 检测数据库执行错误
    _mysqlMsg = str(mysqlMsg)
    # print _mysqlMsg
    if "MySQLdb" in _mysqlMsg:
        return mw.returnData(False, 'MySQLdb组件缺失! <br>进入SSH命令行输入： pip install mysql-python')
    if "2002," in _mysqlMsg:
        return mw.returnData(False, '数据库连接失败,请检查数据库服务是否启动!')
    if "using password:" in _mysqlMsg:
        return mw.returnData(False, '数据库管理密码错误!')
    if "Connection refused" in _mysqlMsg:
        return mw.returnData(False, '数据库连接失败,请检查数据库服务是否启动!')
    if "1133," in _mysqlMsg:
        return mw.returnData(False, '数据库用户不存在!')
    if "1007," in _mysqlMsg:
        return mw.returnData(False, '数据库已经存在!')
    if "1044," in _mysqlMsg:
        return mw.returnData(False, mysqlMsg[1])
    if "2003," in _mysqlMsg:
        return mw.returnData(False, "Can't connect to MySQL server on '127.0.0.1' (61)")
    return mw.returnData(True, 'OK')


def appOp(method):
    file = initDreplace()

    if not mw.isAppleSystem():
        data = mw.execShell('systemctl ' + method + ' ' + getPluginName())
        if data[1] == '':
            return 'ok'
        return 'fail'

    data = mw.execShell(__SR + file + ' ' + method)
    if data[1] == '':
        return 'ok'
    return data[0]


def start():
    return appOp('start')


def stop():
    return appOp('stop')


def restart():
    return appOp('restart')


def reload():
    return appOp('reload')


def initdStatus():
    if mw.isAppleSystem():
        return "Apple Computer does not support"

    shell_cmd = 'systemctl status ' + getPluginName() + ' | grep loaded | grep "enabled;"'
    data = mw.execShell(shell_cmd)
    if data[0] == '':
        return 'fail'
    return 'ok'


def initdInstall():
    if mw.isAppleSystem():
        return "Apple Computer does not support"

    mw.execShell('systemctl enable ' + getPluginName())
    return 'ok'


def initdUinstall():
    if mw.isAppleSystem():
        return "Apple Computer does not support"

    mw.execShell('systemctl disable ' + getPluginName())
    return 'ok'


def runLog():
    log_path = getServerDir() + '/log/doh.log'
    return log_path

def getTotalStatistics():
    st = status()
    data = {}
    if st.strip() == 'start':
        list_count = pQuery('select count(id) as num from repository')
        count = list_count[0]["num"]
        data['status'] = True
        data['count'] = count
        data['ver'] = mw.readFile(getServerDir() + '/version.pl').strip()
        return mw.returnJson(True, 'ok', data)

    data['status'] = False
    data['count'] = 0
    return mw.returnJson(False, 'fail', data)


def uninstallPreInspection():
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
    elif func == 'initd_status':
        print(initdStatus())
    elif func == 'initd_install':
        print(initdInstall())
    elif func == 'initd_uninstall':
        print(initdUinstall())
    elif func == 'uninstall_pre_inspection':
        print(uninstallPreInspection())
    elif func == 'run_log':
        print(runLog())
    elif func == 'post_receive_log':
        print(postReceiveLog())
    elif func == 'conf':
        print(getConf())
    elif func == 'init_conf':
        print(getInitdConf())
    elif func == 'get_total_statistics':
        print(getTotalStatistics())
    else:
        print('fail')
