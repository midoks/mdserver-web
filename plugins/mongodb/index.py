# coding:utf-8

import sys
import io
import os
import time
import re
import json
import datetime
import yaml

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
    path = getServerDir() + "/mongodb.conf"
    return path


def getConfTpl():
    path = getPluginDir() + "/config/mongodb.conf"
    return path

def getConfigData():
    cfg = getConf()
    config_data = mw.readFile(cfg)
    try:
        config = yaml.safe_load(config_data)
    except:
        config = {
            "systemLog": {
                "destination": "file",
                "logAppend": True,
                "path": mw.getServerDir()+"/mongodb/log/mongodb.log"
            },
            "storage": {
                "dbPath": mw.getServerDir()+"/mongodb/data",
                "directoryPerDB": True,
                "journal": {
                    "enabled": True
                }
            },
            "processManagement": {
                "fork": True,
                "pidFilePath": mw.getServerDir()+"/mongodb/log/mongodb.pid"
            },
            "net": {
                "port": 27017,
                "bindIp": "0.0.0.0"
            },
            "security": {
                "authorization": "enabled",
                "javascriptEnabled": False
            }
        }
    return config

def setConfig(config_data):
    cfg = getConf()
    try:
        mw.writeFile(cfg, yaml.safe_dump(config_data))
    except:
        return False
    return True

def getInitDTpl():
    path = getPluginDir() + "/init.d/" + getPluginName() + ".tpl"
    return path


def getConfPort():
    data = getConfigData()
    return data['net']['port']
    # file = getConf()
    # content = mw.readFile(file)
    # rep = 'port\s*=\s*(.*)'
    # tmp = re.search(rep, content)
    # return tmp.groups()[0].strip()

def getConfAuth():
    data = getConfigData()
    return data['security']['authorization']
    # file = getConf()
    # content = mw.readFile(file)
    # rep = 'auth\s*=\s*(.*)'
    # tmp = re.search(rep, content)
    # return tmp.groups()[0].strip()

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

def status():
    data = mw.execShell(
        "ps -ef|grep mongod |grep -v grep | grep -v /Applications | grep -v python | grep -v mdserver-web | awk '{print $2}'")

    if data[0] == '':
        return 'stop'
    return 'start'

def pSqliteDb(dbname='users'):
    file = getServerDir() + '/mongodb.db'
    name = 'mongodb'

    sql_file = getPluginDir() + '/config/mongodb.sql'
    import_sql = mw.readFile(sql_file)
    # print(sql_file,import_sql)
    md5_sql = mw.md5(import_sql)

    import_sign = False
    save_md5_file = getServerDir() + '/import_mongodb.md5'
    if os.path.exists(save_md5_file):
        save_md5_sql = mw.readFile(save_md5_file)
        if save_md5_sql != md5_sql:
            import_sign = True
            mw.writeFile(save_md5_file, md5_sql)
    else:
        mw.writeFile(save_md5_file, md5_sql)

    if not os.path.exists(file) or import_sql:
        conn = mw.M(dbname).dbPos(getServerDir(), name)
        csql_list = import_sql.split(';')
        for index in range(len(csql_list)):
            conn.execute(csql_list[index], ())

    conn = mw.M(dbname).dbPos(getServerDir(), name)
    return conn

def mongdbClient():
    import pymongo
    port = getConfPort()
    auth = getConfAuth()
    mg_root = pSqliteDb('config').where('id=?', (1,)).getField('mg_root')

    # print(auth)
    if auth == 'disabled':
        client = pymongo.MongoClient(host='127.0.0.1', port=int(port), directConnection=True)
    else:
        client = pymongo.MongoClient(host='127.0.0.1', port=int(port), directConnection=True,username='root',password=mg_root)
    return client

def mongdbClientWithPass():
    import pymongo
    port = getConfPort()
    auth = getConfAuth()
    # print(auth)
    mg_root = pSqliteDb('config').where('id=?', (1,)).getField('mg_root')
    if auth == 'disabled':
        client = pymongo.MongoClient(host='127.0.0.1', port=int(port), directConnection=True)
    else:
        uri = "mongodb://root:"+mg_root+"@127.0.0.1:"+str(port)
        # print(uri)
        client = pymongo.MongoClient(uri)
    return client


def initDreplace():

    file_tpl = getInitDTpl()
    service_path = os.path.dirname(os.getcwd())

    initD_path = getServerDir() + '/init.d'
    if not os.path.exists(initD_path):
        os.mkdir(initD_path)
    file_bin = initD_path + '/' + getPluginName()

    logs_dir = getServerDir() + '/logs'
    if not os.path.exists(logs_dir):
        os.mkdir(logs_dir)

    data_dir = getServerDir() + '/data'
    if not os.path.exists(data_dir):
        os.mkdir(data_dir)

    install_ok = getServerDir() + "/install.lock"
    if os.path.exists(install_ok):
        return file_bin
    mw.writeFile(install_ok, 'ok')

    # initd replace
    content = mw.readFile(file_tpl)
    content = content.replace('{$SERVER_PATH}', service_path)
    mw.writeFile(file_bin, content)
    mw.execShell('chmod +x ' + file_bin)

    # config replace
    conf_content = mw.readFile(getConfTpl())
    conf_content = conf_content.replace('{$SERVER_PATH}', service_path)
    mw.writeFile(getServerDir() + '/mongodb.conf', conf_content)

    # systemd
    systemDir = mw.systemdCfgDir()
    systemService = systemDir + '/mongodb.service'
    systemServiceTpl = getPluginDir() + '/init.d/mongodb.service.tpl'
    if os.path.exists(systemDir) and not os.path.exists(systemService):
        service_path = mw.getServerDir()
        se_content = mw.readFile(systemServiceTpl)
        se_content = se_content.replace('{$SERVER_PATH}', service_path)
        mw.writeFile(systemService, se_content)
        mw.execShell('systemctl daemon-reload')

    return file_bin

def initUserRoot():
    # client = mongdbClient()
    # db = client.admin

    client_pass = mongdbClientWithPass()
    listDbs = client_pass.admin.command({"listDatabases": 1})
    print(listDbs)

    print(client_pass.list_database_names());
    exit(0)

    # db.command("updateUser", "root", pwd=mg_pass, roles=db_all_rules)
    # db_all_rules = [
    #     {'role': 'root', 'db': 'admin'},
    #     {'role': 'clusterAdmin', 'db': 'admin'},
    #     {'role': 'readAnyDatabase', 'db': 'admin'},
    #     {'role': 'readWriteAnyDatabase', 'db': 'admin'},
    #     {'role': 'userAdminAnyDatabase', 'db': 'admin'},
    #     {'role': 'dbAdminAnyDatabase', 'db': 'admin'},
    #     {'role': 'userAdmin', 'db': 'admin'},
    #     {'role': 'dbAdmin', 'db': 'admin'}
    # ]

    # mg_pass = mw.getRandomString(10)
    # print(mg_pass)
    # try:
    #     db.command("createUser", "root", pwd=mg_pass, roles=db_all_rules)
    # except Exception as e:
    #     db.command('dropUser','root')
    #     db.command("createUser", "root", pwd=mg_pass, roles=db_all_rules)
        
    # pSqliteDb('config').where('id=?', (1,)).save('mg_root',(mg_pass,))
    return True


def mgOp(method):
    file = initDreplace()
    if mw.isAppleSystem():
        data = mw.execShell(file + ' ' + method)
        # print(data)
        if data[1] == '':
            return 'ok'
        return data[1]

    data = mw.execShell('systemctl ' + method + ' ' + getPluginName())
    if data[1] == '':
        initUserRoot()
        return 'ok'
    return 'fail'


def start():
    mw.execShell(
        'export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/www/server/lib/openssl11/lib')
    return mgOp('start')


def stop():
    return mgOp('stop')


def reload():
    return mgOp('reload')


def restart():
    if os.path.exists("/tmp/mongodb-27017.sock"):
        mw.execShell('rm -rf ' + "/tmp/mongodb-27017.sock")

    return mgOp('restart')


def getConfig():
    d = getConfigData()
    return mw.returnJson(True,'ok',d)

def saveConfig():
    d = getConfigData()

    args = getArgs()
    data = checkArgs(args, ['bind_ip','port','data_path','log','pid_file_path'])
    if not data[0]:
        return data[1]

    d['net']['bindIp'] = args['bind_ip']
    d['net']['port'] = args['port']

    d['storage']['dbPath'] = args['data_path']
    d['systemLog']['path'] = args['log']
    d['processManagement']['pidFilePath'] = args['pid_file_path']
    setConfig(d)
    reload()
    return mw.returnJson(True,'设置成功')

def runInfo():
    '''
    cd /www/server/mdserver-web && source bin/activate && python3 /www/server/mdserver-web/plugins/mongodb/index.py run_info
    '''
    client = mongdbClient()
    db = client.admin
    serverStatus = db.command('serverStatus')

    listDbs = client.list_database_names()

    result = {}
    result["host"] = serverStatus['host']
    result["version"] = serverStatus['version']
    result["uptime"] = serverStatus['uptime']
    result['db_path'] = getServerDir() + "/data"
    result["connections"] = serverStatus['connections']['current']
    result["collections"] = len(listDbs)

    pf = serverStatus['opcounters']
    result['pf'] = pf
    
    return mw.getJson(result)


def runDocInfo():    
    client = mongdbClient()
    db = client.admin
    serverStatus = db.command('serverStatus')

    listDbs = client.list_database_names()
    showDbList = []
    result = {}
    for x in range(len(listDbs)):
        mongd = client[listDbs[x]]
        stats = mongd.command({"dbstats": 1})
        if 'operationTime' in stats:
            del stats['operationTime']

        if '$clusterTime' in stats:
            del stats['$clusterTime']
        showDbList.append(stats)

    result["dbs"] = showDbList
    return mw.getJson(result)

def runReplInfo():
    client = mongdbClient()
    db = client.admin
    serverStatus = db.command('serverStatus')

    result = {}
    result['status'] = '无'
    result['doc_name'] = '无'
    if 'repl' in serverStatus:
        repl = serverStatus['repl']
        # print(repl)
        result['status'] = '从'
        if 'ismaster' in repl and repl['ismaster']:
            result['status'] = '主'

        if 'secondary' in repl and not repl['secondary']:
            result['status'] = '主'

        result['setName'] = mw.getDefault(repl,'setName', '') 
        result['primary'] = mw.getDefault(repl,'primary', '') 
        result['me'] = mw.getDefault(repl,'me', '') 

        hosts = mw.getDefault(repl,'hosts', '') 
        result['hosts'] = ','.join(hosts)

    
    return mw.returnJson(True, 'OK', result)


def testData():
    '''
    cd /www/server/mdserver-web && source bin/activate && python3 /www/server/mdserver-web/plugins/mongodb/index.py test_data
    '''
    import pymongo
    from pymongo import ReadPreference
    
    client = mongdbClient()

    db = client.test
    col = db["demo"]

    rndStr = mw.getRandomString(10)
    insert_dict = { "name": "v1", "value": rndStr}
    x = col.insert_one(insert_dict)
    print(x)



def test():
    initUserRoot()
    '''

    cd /www/server/mdserver-web && source bin/activate && python3 /www/server/mdserver-web/plugins/mongodb/index.py test
    python3 plugins/mongodb/index.py test
    '''
    # https://pymongo.readthedocs.io/en/stable/examples/high_availability.html
    import pymongo
    from pymongo import ReadPreference
    
    # client = mongdbClient()

    # db = client.admin

    # print(db['users'])
    # r = db.command("grantRolesToUser", "root",
    #                  roles=["root"])
    # print(r)
    # users_collection = db['users']
    # print(users_collection)

    # mg_pass = mw.getRandomString(10)
    # r = db.command("createUser", "root1", pwd=mg_pass, roles=["root"])
    # print(r)
    # config = {
    #     '_id': 'test',
    #     'members': [
    #         # 'priority': 10 
    #         {'_id': 0, 'host': '154.21.203.138:27017'},
    #         {'_id': 1, 'host': '154.12.53.216:27017'},
    #     ]
    # }

    # rsStatus = client.admin.command('replSetInitiate',config)
    # print(rsStatus)

    # 需要通过命令行操作
    # rs.initiate({
    #     _id: 'test',
    #     members: [
    #     {
    #         _id: 1,
    #         host: '154.21.203.138:27017',
    #         priority: 2
    #     }, 
    #     {
    #         _id: 2,
    #         host: '154.12.53.216:27017',
    #         priority: 1
    #     }

    #     ]
    # });

    # > rs.status();  // 查询状态
    # // "stateStr" : "PRIMARY", 主节点
    # // "stateStr" : "SECONDARY", 副本节点

    # > rs.add({"_id":3, "host":"127.0.0.1:27318","priority":0,"votes":0});


    # serverStatus = db.command('serverStatus')
    # print(serverStatus)
    
    return mw.returnJson(True, 'OK')

    

def initdStatus():
    if mw.isAppleSystem():
        return "Apple Computer does not support"

    shell_cmd = 'systemctl status mongodb | grep loaded | grep "enabled;"'
    data = mw.execShell(shell_cmd)
    if data[0] == '':
        return 'fail'
    return 'ok'


def initdInstall():
    if mw.isAppleSystem():
        return "Apple Computer does not support"

    mw.execShell('systemctl enable mongodb')
    return 'ok'


def initdUinstall():
    if mw.isAppleSystem():
        return "Apple Computer does not support"

    mw.execShell('systemctl disable mongodb')
    return 'ok'


def runLog():
    f = getServerDir() + '/logs/mongodb.log'
    if os.path.exists(f):
        return f
    return getServerDir() + '/logs.pl'


def installPreInspection(version):
    if mw.isAppleSystem():
        return 'ok'

    sys = mw.execShell(
        "cat /etc/*-release | grep PRETTY_NAME |awk -F = '{print $2}' | awk -F '\"' '{print $2}'| awk '{print $1}'")

    if sys[1] != '':
        return '暂时不支持该系统'

    sys_id = mw.execShell(
        "cat /etc/*-release | grep VERSION_ID | awk -F = '{print $2}' | awk -F '\"' '{print $2}'")

    sysName = sys[0].strip().lower()
    sysId = sys_id[0].strip()

    supportOs = ['centos', 'ubuntu', 'debian', 'opensuse']
    if not sysName in supportOs:
        return '暂时仅支持{}'.format(','.join(supportOs))
    return 'ok'

if __name__ == "__main__":
    func = sys.argv[1]

    version = "4.4"
    if (len(sys.argv) > 2):
        version = sys.argv[2]

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
        print(installPreInspection(version))
    elif func == 'initd_status':
        print(initdStatus())
    elif func == 'initd_install':
        print(initdInstall())
    elif func == 'initd_uninstall':
        print(initdUinstall())
    elif func == 'run_info':
        print(runInfo())
    elif func == 'run_doc_info':
        print(runDocInfo())
    elif func == 'run_repl_info':
        print(runReplInfo())
    elif func == 'conf':
        print(getConf())
    elif func == 'get_config':
        print(getConfig())
    elif func == 'set_config':
        print(saveConfig())
    elif func == 'run_log':
        print(runLog())
    elif func == 'test':
        print(test())
    elif func == 'test_data':
        print(testData())
    else:
        print('error')
