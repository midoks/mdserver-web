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
    return 'simdht'


def getPluginDir():
    return mw.getPluginDir() + '/' + getPluginName()

sys.path.append(getPluginDir() + "/class")
import simdht_mysql


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


def getInitDTpl():
    path = getPluginDir() + "/init.d/" + getPluginName() + ".tpl"
    return path


def getSqlFile():
    file = getPluginDir() + "/conf/simdht.sql"
    return file


def getDbConf():
    file = getServerDir() + "/db.cfg"
    return file


def getCheckdbPos():
    file = getServerDir() + "/start_pos.pl"
    return file


def getBlackList():
    file = getServerDir() + "/workers/black_list.txt"
    return file


def getRunLog():
    file = getServerDir() + "/logs.pl"
    return file


def initDreplace():

    ddir = getServerDir() + '/workers'
    if not os.path.exists(ddir):
        sdir = getPluginDir() + '/workers'
        mw.execShell('cp -rf ' + sdir + ' ' + getServerDir())

    cfg = getServerDir() + '/db.cfg'
    if not os.path.exists(cfg):
        cfg_tpl = getPluginDir() + '/workers/db.cfg'
        content = mw.readFile(cfg_tpl)
        mw.writeFile(cfg, content)

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

    return file_bin


def status():
    data = mw.execShell(
        "ps -ef|grep \"simdht_worker.py\" | grep -v grep | awk '{print $2}'")
    if data[0] == '':
        return 'stop'
    return 'start'


def start():
    file = initDreplace()

    data = mw.execShell(file + ' start')
    if data[1] == '':
        return 'ok'
    return data[1]


def stop():
    file = initDreplace()
    data = mw.execShell(file + ' stop')
    if data[1] == '':
        return 'ok'
    return data[1]


def restart():
    file = initDreplace()
    data = mw.execShell(file + ' restart')
    if data[1] == '':
        return 'ok'
    return 'fail'


def reload():
    file = initDreplace()
    data = mw.execShell(file + ' reload')
    if data[1] == '':
        return 'ok'
    return 'fail'


def initdStatus():
    if not app_debug:
        if mw.isAppleSystem():
            return "Apple Computer does not support"

    initd_bin = getInitDFile()
    if os.path.exists(initd_bin):
        return 'ok'
    return 'fail'


def initdInstall():
    import shutil
    if not app_debug:
        if mw.isAppleSystem():
            return "Apple Computer does not support"

    mysql_bin = initDreplace()
    initd_bin = getInitDFile()
    shutil.copyfile(mysql_bin, initd_bin)
    mw.execShell('chmod +x ' + initd_bin)
    mw.execShell('chkconfig --add ' + getPluginName())
    return 'ok'


def initdUinstall():
    if not app_debug:
        if mw.isAppleSystem():
            return "Apple Computer does not support"
    initd_bin = getInitDFile()
    os.remove(initd_bin)
    mw.execShell('chkconfig --del ' + getPluginName())
    return 'ok'


def matchData(reg, content):
    tmp = re.search(reg, content).groups()
    return tmp[0]


def getDbConfInfo():
    cfg = getDbConf()
    content = mw.readFile(cfg)
    data = {}
    data['DB_HOST'] = matchData("DB_HOST\s*=\s(.*)", content)
    data['DB_USER'] = matchData("DB_USER\s*=\s(.*)", content)
    data['DB_PORT'] = matchData("DB_PORT\s*=\s(.*)", content)
    data['DB_PASS'] = matchData("DB_PASS\s*=\s(.*)", content)
    data['DB_NAME'] = matchData("DB_NAME\s*=\s(.*)", content)
    return data


def pMysqlDb():
    data = getDbConfInfo()
    conn = simdht_mysql.simdht_mysql()
    conn.setHost(data['DB_HOST'])
    conn.setUser(data['DB_USER'])
    conn.setPwd(data['DB_PASS'])
    conn.setPort(int(data['DB_PORT']))
    conn.setDb(data['DB_NAME'])
    return conn


def isSqlError(mysqlMsg):
    # 检测数据库执行错误
    mysqlMsg = str(mysqlMsg)
    if "MySQLdb" in mysqlMsg:
        return mw.returnJson(False, 'MySQLdb组件缺失! <br>进入SSH命令行输入： pip install mysql-python')
    if "2002," in mysqlMsg:
        return mw.returnJson(False, '数据库连接失败,请检查数据库服务是否启动!')
    if "using password:" in mysqlMsg:
        return mw.returnJson(False, '数据库管理密码错误!')
    if "Connection refused" in mysqlMsg:
        return mw.returnJson(False, '数据库连接失败,请检查数据库服务是否启动!')
    if "1133" in mysqlMsg:
        return mw.returnJson(False, '数据库用户不存在!')
    if "1007" in mysqlMsg:
        return mw.returnJson(False, '数据库已经存在!')
    return None


def getMinData(conn, sec):
    time_diff = 0
    if mw.isAppleSystem():
        time_diff = 3 * 60
    pre = time.strftime("%Y-%m-%d %H:%M:%S",
                        time.localtime(time.time() - sec - time_diff))
    sql = "select count(id) from search_hash where create_time > '" + pre + "'"
    data = conn.query(sql)
    return data[0][0]


def getTrendData():
    try:
        args = getArgs()
        data = checkArgs(args, ['interval'])
        if not data[0]:
            return data[1]
        pdb = pMysqlDb()
        # interval = int(args['interval'])
        result = pdb.execute("show tables")
        isError = isSqlError(result)
        if isError:
            return isError
        one = getMinData(pdb, 2)
        two = getMinData(pdb, 5)
        three = getMinData(pdb, 10)
        return mw.getJson([one, two, three])
    except Exception as e:
        # print str(e)
        return mw.getJson([0, 0, 0])


def dhtCmd():
    file = initDreplace()
    return file + ' restart'

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
    elif func == 'get_sql':
        print(getSqlFile())
    elif func == 'get_db_conf':
        print(getDbConf())
    elif func == 'get_checkdb_pos':
        print(getCheckdbPos())
    elif func == 'get_black_list':
        print(getBlackList())
    elif func == 'get_run_Log':
        print(getRunLog())
    elif func == 'get_trend_data':
        print(getTrendData())
    elif func == 'dht_cmd':
        print(dhtCmd())
    else:
        print('error')
