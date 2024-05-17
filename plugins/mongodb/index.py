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

# python3 /www/server/mdserver-web/plugins/mongodb/index.py repl_init 
# python3 /www/server/mdserver-web/plugins/mongodb/index.py run_repl_info
# python3 /www/server/mdserver-web/plugins/mongodb/index.py test_data
# python3 /www/server/mdserver-web/plugins/mongodb/index.py run_info

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

def getConfKey():
    key = getServerDir() + "/mongodb.key"
    return key

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
    # t = status()
    cfg = getConf()
    try:
        mw.writeFile(cfg, yaml.safe_dump(config_data))
    except:
        return False
    return True

def getInitDTpl():
    path = getPluginDir() + "/init.d/" + getPluginName() + ".tpl"
    return path


def getConfIp():
    data = getConfigData()
    return data['net']['bindIp']

def getConfLocalIp():
    return '127.0.0.1'

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
        "ps -ef|grep mongod |grep -v mongosh|grep -v grep | grep -v /Applications | grep -v python | grep -v mdserver-web | awk '{print $2}'")
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

def mongdbClientS():
    import pymongo
    port = getConfPort()
    auth = getConfAuth()
    ip = getConfLocalIp()
    mg_root = pSqliteDb('config').where('id=?', (1,)).getField('mg_root')

    if auth == 'disabled':
        client = pymongo.MongoClient(host=ip, port=int(port), directConnection=True)
    else:
        # print(auth,mg_root)
        client = pymongo.MongoClient(host=ip, port=int(port), directConnection=True, username='root',password=mg_root)
    return client

def mongdbClient():
    import pymongo
    port = getConfPort()
    auth = getConfAuth()
    ip = getConfLocalIp()
    mg_root = pSqliteDb('config').where('id=?', (1,)).getField('mg_root')
    # print(ip,port,auth,mg_root)
    if auth == 'disabled':
        client = pymongo.MongoClient(host=ip, port=int(port), directConnection=True)
    else:
        # uri = "mongodb://root:"+mg_root+"@127.0.0.1:"+str(port)
        # client = pymongo.MongoClient(uri)
        client = pymongo.MongoClient(host=ip, port=int(port), directConnection=True, username='root',password=mg_root)
    return client


def initDreplace():

    mg_key = getServerDir() + "/mongodb.key"
    if not os.path.exists(mg_key):
        mw.execShell("openssl rand -base64 756 >> "+mg_key)
        mw.execShell("chmod 400 "+mg_key)

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
    t = status()
    if t == 'stop':
        return mw.returnJson(False,'未启动!')
    d = getConfigData()
    return mw.returnJson(True,'ok',d)

def saveConfig():
    d = getConfigData()
    args = getArgs()
    data = checkArgs(args, ['bind_ip','port','data_path','log','pid_file_path'])
    if not data[0]:
        return data[1]

    d['net']['bindIp'] = args['bind_ip']
    d['net']['port'] = int(args['port'])

    d['storage']['dbPath'] = args['data_path']
    d['systemLog']['path'] = args['log']
    d['processManagement']['pidFilePath'] = args['pid_file_path']
    setConfig(d)
    restart()
    return mw.returnJson(True,'设置成功')

def initMgRoot(password='',force=0):
    if force == 1:
        d = getConfigData()
        auth_t = d['security']['authorization']
        d['security']['authorization'] = 'disabled'
        setConfig(d)
        restart()

    client = mongdbClient()
    db = client.admin
    
    db_all_rules = [
        {'role': 'root', 'db': 'admin'},
        {'role': 'clusterAdmin', 'db': 'admin'},
        {'role': 'readAnyDatabase', 'db': 'admin'},
        {'role': 'readWriteAnyDatabase', 'db': 'admin'},
        {'role': 'userAdminAnyDatabase', 'db': 'admin'},
        {'role': 'dbAdminAnyDatabase', 'db': 'admin'},
        {'role': 'userAdmin', 'db': 'admin'},
        {'role': 'dbAdmin', 'db': 'admin'}
    ]

    if password =='':
        mg_pass = mw.getRandomString(8)
    else:
        mg_pass = password

    try:
        db.command("createUser", "root", pwd=mg_pass, roles=db_all_rules)
    except Exception as e:
        if force == 0:
            db.command("updateUser", "root", pwd=mg_pass, roles=db_all_rules)
        else:
            db.command('dropUser','root')
            db.command("createUser", "root", pwd=mg_pass, roles=db_all_rules)
    r = pSqliteDb('config').where('id=?', (1,)).save('mg_root',(mg_pass,))

    if force == 1:
        d['security']['authorization'] = auth_t
        setConfig(d)
        restart()
    return True

def initUserRoot():
    d = getConfigData()
    auth_t = d['security']['authorization']
    d['security']['authorization'] = 'disabled'
    setConfig(d)
    restart()
    time.sleep(1)

    client = mongdbClient()
    db = client.admin
    
    db_all_rules = [
        {'role': 'root', 'db': 'admin'},
        {'role': 'clusterAdmin', 'db': 'admin'},
        {'role': 'readAnyDatabase', 'db': 'admin'},
        {'role': 'readWriteAnyDatabase', 'db': 'admin'},
        {'role': 'userAdminAnyDatabase', 'db': 'admin'},
        {'role': 'dbAdminAnyDatabase', 'db': 'admin'},
        {'role': 'userAdmin', 'db': 'admin'},
        {'role': 'dbAdmin', 'db': 'admin'}
    ]
    # db.command("updateUser", "root", pwd=mg_pass, roles=db_all_rules)
    mg_pass = mw.getRandomString(8)
    try:
        r1 = db.command("createUser", "root", pwd=mg_pass, roles=db_all_rules)
        # print(r1)
    except Exception as e:
        # print(e)
        r1 = db.command('dropUser','root')
        r2 = db.command("createUser", "root", pwd=mg_pass, roles=db_all_rules)
        # print(r1, r2)
        
    r = pSqliteDb('config').where('id=?', (1,)).save('mg_root',(mg_pass,))

    d['security']['authorization'] = auth_t
    setConfig(d)
    restart()
    return True

def setConfigAuth():
    init_db_root = getServerDir() + '/init_db_root.lock'
    if not os.path.exists(init_db_root):
        initUserRoot()
        mw.writeFile(init_db_root,'ok')

    d = getConfigData()
    if d['security']['authorization'] == 'enabled':
        d['security']['authorization'] = 'disabled'
        del d['security']['keyFile']
        setConfig(d)
        restart()
        return mw.returnJson(True,'关闭成功')
    else:
        d['security']['authorization'] = 'enabled'
        d['security']['keyFile'] = getServerDir()+'/mongodb.key'
        setConfig(d)
        restart()
        return mw.returnJson(True,'开启成功')

def runInfo():
    '''
    cd /www/server/mdserver-web && source bin/activate && python3 /www/server/mdserver-web/plugins/mongodb/index.py run_info
    '''
    client = mongdbClient()
    db = client.admin

    try:
        serverStatus = db.command('serverStatus')
    except Exception as e:
        return mw.returnJson(False, str(e))
    

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
    # print(db)

    try:
        serverStatus = db.command('serverStatus')
    except Exception as e:
        return mw.returnJson(False, str(e))


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
    result = {}
    try:
        serverStatus = db.command('serverStatus')
    except Exception as e:
        return mw.returnJson(False, str(e))

    d = getConfigData()
    if 'replication' in d and 'replSetName' in d['replication']:
        result['repl_name'] = d['replication']['replSetName']

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

    result['members'] = []
    try:
        members_list = []
        replStatus = db.command('replSetGetStatus')
        if 'members' in replStatus:
            members = replStatus['members']
            for m in members:
                t = {}
                t['name'] = m['name']
                t['stateStr'] = m['stateStr']
                t['uptime'] = m['uptime']
                members_list.append(t)
        result['members'] = members_list
    except Exception as e:
        pass
        
    return mw.returnJson(True, 'OK', result)

def getDbList():
    args = getArgs()
    page = 1
    page_size = 10
    search = ''
    data = {}
    if 'page' in args:
        page = int(args['page'])

    if 'page_size' in args:
        page_size = int(args['page_size'])

    if 'search' in args:
        search = args['search']

    conn = pSqliteDb('databases')
    limit = str((page - 1) * page_size) + ',' + str(page_size)
    condition = ''
    if not search == '':
        condition = "name like '%" + search + "%'"
    field = 'id,name,username,password,accept,rw,ps,addtime'
    clist = conn.where(condition, ()).field(
        field).limit(limit).order('id desc').select()

    for x in range(0, len(clist)):
        dbname = clist[x]['name']
        blist = getDbBackupListFunc(dbname)
        clist[x]['is_backup'] = False
        if len(blist) > 0:
            clist[x]['is_backup'] = True

    count = conn.where(condition, ()).count()
    _page = {}
    _page['count'] = count
    _page['p'] = page
    _page['row'] = page_size
    _page['tojs'] = 'dbList'
    data['page'] = mw.getPage(_page)
    data['data'] = clist

    info = {}
    info['root_pwd'] = pSqliteDb('config').where('id=?', (1,)).getField('mg_root')
    data['info'] = info
    return mw.getJson(data)
    # return mw.returnJson(True,'ok',data)

def addDb():
    t = status()
    if t == 'stop':
        return mw.returnJson(False,'未启动!')

    client = mongdbClient()
    db = client.admin

    args = getArgs()
    data = checkArgs(args, ['ps','name','db_user','password'])
    if not data[0]:
        return data[1]

    data_name = args['name'].strip()
    if not data_name:
        return mw.returnJson(False, "数据库名不能为空！")

    nameArr = ['admin', 'config', 'local']
    if data_name in nameArr:
        return mw.returnJson(False, "数据库名是保留名称!")

    addTime = time.strftime('%Y-%m-%d %X', time.localtime())
    username = ''
    password = ''
    # auth为true时如果__DB_USER为空则将它赋值为 root，用于开启本地认证后数据库用户为空的情况
    auth_status = getConfAuth() == "enabled"  
    
    if auth_status:
        data_name = args['name']
        username = args['db_user']
        password = args['password']
    else:
        username = data_name


    client[data_name].zchat.insert_one({})
    user_roles = [{'role': 'dbOwner', 'db': data_name}, {'role': 'userAdmin', 'db': data_name}]
    if auth_status:
        # db.command("dropUser", username)
        db.command("createUser", username, pwd=password, roles=user_roles)

    ps = args['ps']
    if ps == '': 
        ps = data_name

    # 添加入SQLITE
    pSqliteDb('databases').add('name,username,password,accept,ps,addtime', (data_name, username, password, '127.0.0.1', ps, addTime))
    return mw.returnJson(True, '添加成功')


def delDb():
    client = mongdbClient()
    db = client.admin
    sqlite_db = pSqliteDb('databases')

    args = getArgs()
    data = checkArgs(args, ['id', 'name'])
    if not data[0]:
        return data[1]
    try:
        sid = args['id']
        name = args['name']
        find = sqlite_db.where("id=?", (sid,)).field('id,name,username,password,accept,ps,addtime').find()
        accept = find['accept']
        username = find['username']

        client.drop_database(name)

        try:
            db.command('dropUser',username)
        except Exception as e:
            pass

        # 删除SQLITE
        sqlite_db.where("id=?", (sid,)).delete()
        return mw.returnJson(True, '删除成功!')
    except Exception as ex:
        return mw.returnJson(False, '删除失败!' + str(ex))

def setRootPwd(version=''):
    args = getArgs()
    data = checkArgs(args, ['password'])
    if not data[0]:
        return data[1]

    #强制修改
    force = 0
    if 'force' in args and args['force'] == '1':
        force = 1

    password = args['password']
    try:
        msg = ''
        if force == 1:
            msg = ',无须强制!'
        initMgRoot(password, force)
        return mw.returnJson(True, '数据库root密码修改成功!'+msg)
    except Exception as ex:
        return mw.returnJson(False, '修改错误:' + str(ex))

def setUserPwd(version=''):

    client = mongdbClient()
    db = client.admin
    sqlite_db = pSqliteDb('databases')

    args = getArgs()
    data = checkArgs(args, ['password', 'name'])
    if not data[0]:
        return data[1]

    newpassword = args['password']
    username = args['name']
    uid = args['id']
    try:
        name = sqlite_db.where('id=?', (uid,)).getField('name')
        user_roles = [{'role': 'dbOwner', 'db': name}, {'role': 'userAdmin', 'db': name}]

        try:
            db.command("updateUser", username, pwd=newpassword, roles=user_roles)
        except Exception as e:
            db.command("createUser", username, pwd=newpassword, roles=user_roles)

        sqlite_db.where("id=?", (uid,)).setField('password', newpassword)
        return mw.returnJson(True, mw.getInfo('修改数据库[{1}]密码成功!', (name,)))
    except Exception as ex:
        return mw.returnJson(False, mw.getInfo('修改数据库[{1}]密码失败[{2}]!', (name, str(ex),)))


def syncGetDatabases():
    client = mongdbClient()
    sqlite_db = pSqliteDb('databases')
    db = client.admin
    data = client.admin.command({"listDatabases": 1})
    nameArr = ['admin', 'config', 'local']
    n = 0

    for value in data['databases']:
        vdb_name = value["name"]
        b = False
        for key in nameArr:
            if vdb_name == key:
                b = True
                break
        if b:
            continue
        if sqlite_db.where("name=?", (vdb_name,)).count() > 0:
            continue

        host = '127.0.0.1'
        ps = vdb_name
        addTime = time.strftime('%Y-%m-%d %X', time.localtime())
        if sqlite_db.add('name,username,password,accept,ps,addtime', (vdb_name, vdb_name, '', host, ps, addTime)):
            n += 1

    msg = mw.getInfo('本次共从服务器获取了{1}个数据库!', (str(n),))
    return mw.returnJson(True, msg)

def setDbPs():
    args = getArgs()
    data = checkArgs(args, ['id', 'name', 'ps'])
    if not data[0]:
        return data[1]

    ps = args['ps']
    sid = args['id']
    name = args['name']
    try:
        psdb = pSqliteDb('databases')
        psdb.where("id=?", (sid,)).setField('ps', ps)
        return mw.returnJson(True, mw.getInfo('修改数据库[{1}]备注成功!', (name,)))
    except Exception as e:
        return mw.returnJson(True, mw.getInfo('修改数据库[{1}]备注失败!', (name,)))


def getDbInfo():
    args = getArgs()
    data = checkArgs(args, ['name'])
    if not data[0]:
        return data[1]

    ret = {}

    client = mongdbClient()

    db_name = args['name']
    db = client[db_name]

    result = {}
    t = db.command("dbStats")
    # print(result)
    result['collections'] = t['collections']
    result['avgObjSize'] = t['avgObjSize']
    result['dataSize'] = t['dataSize']
    result['storageSize'] = t['storageSize']
    result['indexSize'] = t['indexSize']

    result["collection_list"] = []
    for collection_name in db.list_collection_names():
        collection = db.command("collStats", collection_name)
        data = {
            "collection_name": collection_name,
            "count": collection.get("count"),  # 文档数
            "size": collection.get("size"),  # 内存中的大小
            "avg_obj_size": collection.get("avgObjSize"),  # 对象平均大小
            "storage_size": collection.get("storageSize"),  # 存储大小
            "capped": collection.get("capped"),
            "nindexes": collection.get("nindexes"),  # 索引数
            "total_index_size": collection.get("totalIndexSize"),  # 索引大小
        }
        result["collection_list"].append(data)
    
    return mw.returnJson(True,'ok', result)

def toDbBase(find):
    client = mongdbClient()
    db_admin = client.admin
    data_name = find['name']
    db = client[data_name]

    db.zchat.insert_one({})
    user_roles = [{'role': 'dbOwner', 'db': data_name}, {'role': 'userAdmin', 'db': data_name}]
    try:
        db_admin.command("createUser", find['username'], pwd=find['password'], roles=user_roles)
    except Exception as e:
        db_admin.command("updateUser", find['username'], pwd=find['password'], roles=user_roles)
    return 1

def syncToDatabases():
    args = getArgs()
    data = checkArgs(args, ['type', 'ids'])
    if not data[0]:
        return data[1]

    stype = int(args['type'])
    sqlite_db = pSqliteDb('databases')
    n = 0

    if stype == 0:
        data = sqlite_db.field('id,name,username,password,accept').select()
        for value in data:
            result = toDbBase(value)
            if result == 1:
                n += 1
    else:
        data = json.loads(args['ids'])
        for value in data:
            find = sqlite_db.where("id=?", (value,)).field(
                'id,name,username,password,accept').find()
            # print find
            result = toDbBase(find)
            if result == 1:
                n += 1
    msg = mw.getInfo('本次共同步了{1}个数据库!', (str(n),))
    return mw.returnJson(True, msg)


def getAllRole():
    mongo_role = {
        # 数据库用户角色
        "read": "读取数据(read)",
        "readWrite": "读取和写入数据(readWrite)",
        # 数据库管理角色
        # "dbAdmin": "数据库管理员",
        "dbOwner": "数据库所有者(dbOwner)",
        "userAdmin": "用户管理员(userAdmin)",
        # 集群管理角色
        # "clusterAdmin": "集群管理员",
        # "clusterManager": "集群管理器",
        # "clusterMonitor": "集群监视器",
        # "hostManager": "主机管理员",
        # 备份和恢复角色
        # "backup": "备份数据",
        # "restore": "还原数据",
        # 所有数据库角色
        # "readAnyDatabase": "任意数据库读取",
        # "readWriteAnyDatabase": "任意数据库读取和写入",
        # "userAdminAnyDatabase": "任意数据库用户管理员",
        # "dbAdminAnyDatabase": "任意数据库管理员",
        # 超级用户角色
        # "root": "超级管理员",
        # 内部角色
        # "__queryableBackup": "可查询备份",
        # "__system": "系统角色",
        # "enableSharding": "启用分片",
    }

    client = mongdbClient()
    db = client.admin

    # 获取所有角色
    role_data = db.command('rolesInfo', showBuiltinRoles=True)
    result = []
    for role in role_data["roles"]:
        if mongo_role.get(role["role"]) is not None:
            role["name"] = mongo_role.get(role["role"])
            result.append(role)
    return mw.returnJson(True, 'ok', result)

def getDbAccess():
    args = getArgs()
    data = checkArgs(args, ['username'])
    if not data[0]:
        return data[1]

    client = mongdbClient()
    db = client.admin
    username = args['username']

    mongo_role = {
        # 数据库用户角色
        "read": "读取数据(read)",
        "readWrite": "读取和写入数据(readWrite)",
        # 数据库管理角色
        # "dbAdmin": "数据库管理员",
        "dbOwner": "数据库所有者(dbOwner)",
        "userAdmin": "用户管理员(userAdmin)",
        # 集群管理角色
        # "clusterAdmin": "集群管理员",
        # "clusterManager": "集群管理器",
        # "clusterMonitor": "集群监视器",
        # "hostManager": "主机管理员",
        # 备份和恢复角色
        # "backup": "备份数据",
        # "restore": "还原数据",
        # 所有数据库角色
        # "readAnyDatabase": "任意数据库读取",
        # "readWriteAnyDatabase": "任意数据库读取和写入",
        # "userAdminAnyDatabase": "任意数据库用户管理员",
        # "dbAdminAnyDatabase": "任意数据库管理员",
        # 超级用户角色
        # "root": "超级管理员",
        # 内部角色
        # "__queryableBackup": "可查询备份",
        # "__system": "系统角色",
        # "enableSharding": "启用分片",
    }

    role_data = db.command('rolesInfo', showBuiltinRoles=True)
    all_role_list = []
    for role in role_data["roles"]:
        if mongo_role.get(role["role"]) is not None:
            role["name"] = mongo_role.get(role["role"])
            all_role_list.append(role)

    result = {
        "user": username,
        "db": username,
        "roles": [],
        "all_roles":all_role_list,
    }

    user_data = db.command('usersInfo', username)
    if user_data:
        if len(user_data["users"]) != 0:
            user = user_data["users"][0]
            result["user"] = user.get("user", username)
            result["db"] = user.get("db", username)
            result["roles"] = user.get("roles", [])

    return mw.returnJson(True, 'ok', result)

def setDbAccess():
    args = getArgs()
    data = checkArgs(args, ['username', 'select','name'])
    if not data[0]:
        return data[1]
    username = args['username']
    select = args['select']
    name = args['name']

    mg_pass = pSqliteDb('config').where('id=?', (1,)).getField('mg_root')

    user_roles = []
    select_role = select.split(',')
    for role in select_role:
        t = {}
        t['role'] = role
        t['db'] = name
        user_roles.append(t)

    client = mongdbClient()
    db = client.admin

    try:
        db.command("updateUser", username, pwd=mg_pass, roles=user_roles)
    except Exception as e:
        db.command('dropUser',username)
        db.command("createUser", username, pwd=mg_pass, roles=user_roles)

    return mw.returnJson(True, '设置成功!')

def getReplConfigData():
    import json
    f = getServerDir()+'/repl.json'
    if os.path.exists(f):
        c = mw.readFile(f)
        return json.loads(c)
    else:
        t = {}
        t['name'] =  ''
        t['nodes'] = []
        mw.writeFile(f, mw.getJson(t))
        return t

def setReplConfigData(c):
    import json
    f = getServerDir()+'/repl.json'
    mw.writeFile(f, mw.getJson(c))
    return c

def getReplConfig():
    c = getReplConfigData()
    return mw.returnJson(True, 'ok!', c)

def replSetName():
    args = getArgs()
    data = checkArgs(args, ['name'])
    if not data[0]:
        return data[1]

    c = getReplConfigData()
    c['name'] =  args['name']
    setReplConfigData(c)


    d = getConfigData()
    d['replication']['replSetName'] = args['name']
    setConfig(d)
    restart()

    return mw.returnJson(True, '设置成功!')

def replSetNode():
    args = getArgs()
    data = checkArgs(args, ['node','priority','arbiterOnly','votes','idx'])
    if not data[0]:
        return data[1]

    c = getReplConfigData()
    nodes = c['nodes']
    add_node = args['node'].strip()
    idx = int(args['idx'])

    priority = -1
    if 'priority' in  args:
        priority = args['priority'].strip()

    priority = int(priority)
    if priority<0 or priority>100:
        return mw.returnJson(False, 'priority应该在[0-100]之间!')

    arbiterOnly = 0
    if 'arbiterOnly' in  args:
        arbiterOnly = args['arbiterOnly'].strip()
    arbiterOnly = int(arbiterOnly)

    votes = 1
    if 'votes' in  args:
        votes = args['votes']
    votes = int(votes)

    # 编辑状态
    if idx>-1:
        for i in range(len(nodes)):
            if i == idx:
                nodes[i]['host'] = add_node
                nodes[i]['priority'] = priority
                nodes[i]['votes'] = votes
                nodes[i]['arbiterOnly'] = arbiterOnly
        c['nodes'] = nodes
        setReplConfigData(c)
        return mw.returnJson(True, '编辑成功!')

    is_have = False
    for x in nodes:
        if x['host'] == add_node:
            is_have = True

    if is_have:
        return mw.returnJson(False, add_node+',节点已经存在!')

    t = {}
    t['host'] = add_node
    t['priority'] = priority
    t['votes'] = votes
    t['arbiterOnly'] = arbiterOnly

    nodes.append(t)
    c['nodes'] = nodes
    setReplConfigData(c)
    return mw.returnJson(True, '添加成功!')


def delReplNode():
    args = getArgs()
    data = checkArgs(args, ['node'])
    if not data[0]:
        return data[1]

    c = getReplConfigData()
    nodes = c['nodes']
    del_node = args['node'].strip()

    filter_nodes = []; 
    for x in nodes:
        if x['host'] != del_node:
            filter_nodes.append(x)
    
    c['nodes'] = filter_nodes
    setReplConfigData(c)

    return mw.returnJson(True, '删除节点'+args['node']+'成功!')


def replInit():
    c = getReplConfigData()

    name = c['name']
    nodes = c['nodes']

    if name == '':
        return mw.returnJson(False, '副本名不能为空!')

    # d = getConfigData()
    # d['replication']['replSetName'] = name
    # setConfig(d)
    # restart()

    if len(nodes) == 0:
        return mw.returnJson(False, '节点不能为空!')

    cfg_node = []

    now_time_t = int(time.time())

    for x in range(len(nodes)):
        n = nodes[x]
        t = {}
        t['_id'] = x
        t['host'] = n['host']
        if 'priority' in n:
            t['priority'] = int(n['priority'])

        if 'votes' in n:
            t['votes'] = int(n['votes'])

        if 'arbiterOnly' in n and n['arbiterOnly'] == 1:
            t['arbiterOnly'] = True

        cfg_node.append(t)

    # print(cfg_node)
    # return mw.returnJson(False, '设置副本成功!')

    config = {
        '_id': name,
        'members': cfg_node
    }

    client = mongdbClient()
    try:
        client.admin.command('replSetInitiate',config)
    except Exception as e:
        info = str(e).split(',')
        # print(info)
        if info[0] == 'already initialized':
            config['version'] = int(now_time_t)
            try:
                client.admin.command('replSetReconfig',config,force=True,maxTimeMS=10)
            except Exception as e:
                return mw.returnJson(False, str(e))
            
            return mw.returnJson(True, '重置副本同步成功!')
        return mw.returnJson(False, str(e))

    return mw.returnJson(True, '设置副本初始化成功!')

def replClose():

    d = getConfigData()
    if 'replSetName' in d['replication']:
        del d['replication']['replSetName']
        setConfig(d)
        restart()

    client = mongdbClient()
    db = client.admin
    try:
        restart()
    except Exception as e:
        return mw.returnJson(False, str(e))
    
    return mw.returnJson(True, '关闭副本同步成功!')

def getDbBackupListFunc(dbname=''):
    bkDir = mw.getRootDir() + '/backup/database'
    blist = os.listdir(bkDir)
    r = []

    bname = 'mongodb_' + dbname
    blen = len(bname)
    for x in blist:
        fbstr = x[0:blen]
        if fbstr == bname:
            r.append(x)
    return r

def getDbBackupList():
    args = getArgs()
    data = checkArgs(args, ['name'])
    if not data[0]:
        return data[1]

    r = getDbBackupListFunc(args['name'])
    bkDir = mw.getRootDir() + '/backup/database'
    rr = []
    for x in range(0, len(r)):
        p = bkDir + '/' + r[x]
        data = {}
        data['name'] = r[x]

        rsize = os.path.getsize(p)
        data['size'] = mw.toSize(rsize)

        t = os.path.getctime(p)
        t = time.localtime(t)

        data['time'] = time.strftime('%Y-%m-%d %H:%M:%S', t)
        rr.append(data)

        data['file'] = p

    return mw.returnJson(True, 'ok', rr)

def getDbBackupImportList():

    bkImportDir = mw.getRootDir() + '/backup/mongodb_import'
    if not os.path.exists(bkImportDir):
        os.mkdir(bkImportDir)

    blist = os.listdir(bkImportDir)

    rr = []
    for x in range(0, len(blist)):
        name = blist[x]
        p = bkImportDir + '/' + name
        data = {}
        data['name'] = name

        rsize = os.path.getsize(p)
        data['size'] = mw.toSize(rsize)

        t = os.path.getctime(p)
        t = time.localtime(t)

        data['time'] = time.strftime('%Y-%m-%d %H:%M:%S', t)
        rr.append(data)

        data['file'] = p

    rdata = {
        "list": rr,
        "upload_dir": bkImportDir,
    }
    return mw.returnJson(True, 'ok', rdata)

def deleteDbBackup():
    args = getArgs()
    data = checkArgs(args, ['filename', 'path'])
    if not data[0]:
        return data[1]

    path = args['path']
    full_file = ""
    bkDir = mw.getRootDir() + '/backup/database'
    full_file = bkDir + '/' + args['filename']
    if path != "":
        full_file = path + "/" + args['filename']
    os.remove(full_file)
    return mw.returnJson(True, 'ok')

def setDbBackup():
    args = getArgs()
    data = checkArgs(args, ['name'])
    if not data[0]:
        return data[1]

    scDir = getPluginDir() + '/scripts/backup.py'
    cmd = 'python3 ' + scDir + ' database ' + args['name'] + ' 3'
    os.system(cmd)
    return mw.returnJson(True, 'ok')


def getListBson(dbname=''):
    bkDir = mw.getRootDir() + '/backup/mongodb_import/'+dbname
    blist = os.listdir(bkDir)
    r = []

    bname = 'bson' 
    blen = len(bname)
    for x in blist:
        if x.endswith(bname):
            r.append(x)
    return r

def importDbExternal():
    args = getArgs()
    data = checkArgs(args, ['file', 'name'])
    if not data[0]:
        return data[1]

    file = args['file']
    name = args['name']

    import_dir = mw.getRootDir() + '/backup/mongodb_import/'
    mg_root = pSqliteDb('config').where('id=?', (1,)).getField('mg_root')
    port = getConfPort()

    file_path = import_dir + file
    if not os.path.exists(file_path):
        return mw.returnJson(False, '文件突然消失?')

    exts = ['gz', 'zip']
    ext = mw.getFileSuffix(file)
    if ext not in exts:
        return mw.returnJson(False, '导入数据库格式不对!')

    # print(file,name)
    # print(import_dir,name)
    auth = getConfAuth()
    mg_root = pSqliteDb('config').where('id=?', (1,)).getField('mg_root')
    uoption = ''
    if auth != 'disabled':
        uoption =' --authenticationDatabase admin -u root -p '+mg_root

    file_dir = import_dir+name
    if not os.path.exists(file_dir):
        mw.execShell("mkdir -p "+file_dir)

    file_tgz = import_dir+file
    if os.path.exists(file_tgz):
        cmd = 'cd ' + file_dir + ' && tar -xzvf ' + file_tgz + " -C "+file_dir
        # print(cmd)
        r = mw.execShell(cmd)
        # print(r)
        bson_list = getListBson(name)
        # print(bson_list)
        for x in bson_list:
            cmd = getServerDir() + "/bin/mongorestore "+uoption+" --port "+str(port)+" --dir "+file_dir+'/'+x
            # print(cmd)
            rdata = mw.execShell(cmd)
            # print(data)
            if rdata[1].lower().find('error') > -1:
                return mw.returnJson(False, rdata[1])

    # 删除文件
    if os.path.exists(file_dir):
        del_cmd = "rm -rf "+file_dir
        mw.execShell(del_cmd)

    return mw.returnJson(True, 'ok')


def importDbBackup():
    args = getArgs()
    data = checkArgs(args, ['file', 'name'])
    if not data[0]:
        return data[1]

    file = args['file']
    name = args['name']

    port = getConfPort()

    file_tgz = mw.getRootDir() + '/backup/database/' + file
    file_dir = mw.getRootDir() + '/backup/database/' + file.replace('.tar.gz','')

    if not os.path.exists(file_dir):
        mw.execShell("mkdir -p "+file_dir)

    # print(os.path.exists(file_tgz))
    if os.path.exists(file_tgz):
        cmd = 'cd ' + mw.getRootDir() + '/backup/database && tar -xzvf ' + file + " -C "+file_dir
        # print(cmd)
        mw.execShell(cmd)

    auth = getConfAuth()
    mg_root = pSqliteDb('config').where('id=?', (1,)).getField('mg_root')
    uoption = ''
    if auth != 'disabled':
        uoption =' -u root -p '+mg_root

    cmd = getServerDir() + "/bin/mongorestore "+uoption+" --port "+str(port)+" --dir "+file_dir
    # print(cmd)
    mw.execShell(cmd)


    # 删除文件
    if os.path.exists(file_dir):
        del_cmd = "rm -rf "+file_dir
        mw.execShell(del_cmd)

    return mw.returnJson(True, 'ok')

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
    '''
    python3 /www/server/mdserver-web/plugins/mongodb/index.py set_config_auth  {}
    cd /www/server/mdserver-web && source bin/activate && python3 /www/server/mdserver-web/plugins/mongodb/index.py test
    python3 plugins/mongodb/index.py test
    '''
    # https://pymongo.readthedocs.io/en/stable/examples/high_availability.html
    # import pymongo
    # from pymongo import ReadPreference
    
    client = mongdbClient()
    db = client.admin

    mg_pass = mw.getRandomString(10)
    config = {
        '_id': 'test',
        'members': [
            {'_id': 0, 'host': '127.0.0.1:27019'},
            {'_id': 1, 'host': '127.0.0.1:27017'},
        ]
    }

    rsStatus = client.admin.command('replSetInitiate',config)
    print(rsStatus)

    # 需要通过命令行操作
    # rs.initiate({
    #     _id: 'test',
    #     members: [
    #     {
    #         _id: 1,
    #         host: '127.0.0.1:27019',
    #         priority: 2
    #     }, 
    #     {
    #         _id: 2,
    #         host: '127.0.0.1:27017',
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

def uninstallPreInspection(version):
    stop()

    import plugins_api
    plugins_api.plugins_api().removeIndex(getPluginName(), version)

    return "请手动删除MongoDB[{}]<br/> rm -rf {}".format(version, getServerDir())

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
    elif func == 'uninstall_pre_inspection':
        print(uninstallPreInspection(version))
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
    elif func == 'config_key':
        print(getConfKey())
    elif func == 'get_config':
        print(getConfig())
    elif func == 'set_config':
        print(saveConfig())
    elif func == 'set_config_auth':
        print(setConfigAuth())
    elif func == 'get_db_list':
        print(getDbList())
    elif func == 'add_db':
        print(addDb())
    elif func == 'del_db':
        print(delDb())
    elif func == 'set_root_pwd':
        print(setRootPwd())
    elif func == 'set_user_pwd':
        print(setUserPwd())
    elif func == 'sync_get_databases':
        print(syncGetDatabases())
    elif func == 'sync_to_databases':
        print(syncToDatabases())
    elif func == 'set_db_ps':
        print(setDbPs())
    elif func == 'get_db_info':
        print(getDbInfo())
    elif func == 'get_all_role':
        print(getAllRole())
    elif func == 'get_db_access':
        print(getDbAccess())
    elif func == 'set_db_access':
        print(setDbAccess())
    elif func == 'repl_set_name':
        print(replSetName())
    elif func == 'repl_set_node':
        print(replSetNode())
    elif func == 'get_repl_config':
        print(getReplConfig())
    elif func == 'del_repl_node':
        print(delReplNode())
    elif func == 'repl_init':
        print(replInit())
    elif func == 'repl_close':
        print(replClose())
    elif func == 'get_db_backup_list':
        print(getDbBackupList())
    elif func == 'get_db_backup_import_list':
        print(getDbBackupImportList())
    elif func == 'delete_db_backup':
        print(deleteDbBackup())
    elif func == 'set_db_backup':
        print(setDbBackup())
    elif func == 'import_db_external':
        print(importDbExternal())
    elif func == 'import_db_backup':
        print(importDbBackup())
    elif func == 'run_log':
        print(runLog())
    elif func == 'test':
        print(test())
    elif func == 'test_data':
        print(testData())
    else:
        print('error')
