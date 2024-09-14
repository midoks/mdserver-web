# coding:utf-8

import sys
import io
import os
import time
import re

sys.path.append(os.getcwd() + "/class/core")
import mw

app_debug = False
if mw.isAppleSystem():
    app_debug = True


def getPluginName():
    return 'acme_pandominassl_apply'


def getPluginDir():
    return mw.getPluginDir() + '/' + getPluginName()


def getServerDir():
    return mw.getServerDir() + '/' + getPluginName()


def getInitDFile():
    current_os = mw.getOs()
    if current_os == 'darwin':
        return '/tmp/' + getPluginName()

    if current_os.startswith('freebsd'):
        return '/etc/rc.d/' + getPluginName()

    return '/etc/init.d/' + getPluginName()


def getConf():
    path = getServerDir() + "/hook.py"
    return path


def getInitDTpl():
    path = getPluginDir() + "/init.d/" + getPluginName() + ".tpl"
    return path


def getArgs():
    args = sys.argv[3:]
    tmp = {}
    args_len = len(args)

    if args_len == 1:
        t = args[0].strip('{').strip('}')
        if t.strip() == '':
            tmp = []
        else:
            t = t.split(':')
            tmp[t[0]] = t[1]
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

def configTpl():
    path = getPluginDir() + '/hooks'
    pathFile = os.listdir(path)
    tmp = []
    for one in pathFile:
        file = path + '/' + one
        tmp.append(file)
    return mw.getJson(tmp)


def readConfigTpl():
    args = getArgs()
    data = checkArgs(args, ['file'])
    if not data[0]:
        return data[1]

    content = mw.readFile(args['file'])
    content = contentReplace(content)
    return mw.returnJson(True, 'ok', content)

def getPidFile():
    file = getConf()
    content = mw.readFile(file)
    rep = r'pidfile\s*(.*)'
    tmp = re.search(rep, content)
    return tmp.groups()[0].strip()

def status():
    return 'start'

def contentReplace(content):
    service_path = mw.getServerDir()
    content = content.replace('{$ROOT_PATH}', mw.getRootDir())
    content = content.replace('{$SERVER_PATH}', service_path)
    content = content.replace('{$SERVER_APP}', service_path + '/redis')
    content = content.replace('{$REDIS_PASS}', mw.getRandomString(10))
    return content


def pSqliteDb(dbname='dnsapi'):
    file = getServerDir() + '/acme.db'
    name = 'acme'

    import_sql = mw.readFile(getPluginDir() + '/conf/acme.sql')
    md5_sql = mw.md5(import_sql)

    import_sign = False
    save_md5_file = getServerDir() + '/acme.md5'
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

def initDreplace():

    file_tpl = getInitDTpl()
    service_path = os.path.dirname(os.getcwd())

    initD_path = getServerDir() + '/init.d'
    if not os.path.exists(initD_path):
        os.mkdir(initD_path)
    file_bin = initD_path + '/' + getPluginName()

    run_log_file = runLog()
    if not os.path.exists(run_log_file):
        mw.writeFile(run_log_file,'')

    hook_file = getConf()
    if not os.path.exists(hook_file):
        mw.writeFile(hook_file,'')

    # initd replace
    if not os.path.exists(file_bin):
        content = mw.readFile(file_tpl)
        content = content.replace('{$SERVER_PATH}', service_path)
        mw.writeFile(file_bin, content)
        mw.execShell('chmod +x ' + file_bin)


    # systemd
    systemDir = mw.systemdCfgDir()
    systemService = systemDir + '/' + getPluginName() + '.service'
    if os.path.exists(systemDir) and not os.path.exists(systemService):
        systemServiceTpl = getPluginDir() + '/init.d/' + getPluginName() + '.service.tpl'
        service_path = mw.getServerDir()
        se_content = mw.readFile(systemServiceTpl)
        se_content = se_content.replace('{$SERVER_PATH}', service_path)
        mw.writeFile(systemService, se_content)
        mw.execShell('systemctl daemon-reload')

    return file_bin


def apaOp(method):
    file = initDreplace()

    current_os = mw.getOs()
    if current_os == "darwin":
        data = mw.execShell(file + ' ' + method)
        if data[1] == '':
            return 'ok'
        return data[1]

    if current_os.startswith("freebsd"):
        data = mw.execShell('service ' + getPluginName() + ' ' + method)
        if data[1] == '':
            return 'ok'
        return data[1]

    data = mw.execShell('systemctl ' + method + ' ' + getPluginName())
    if data[1] == '':
        return 'ok'
    return data[1]


def start():
    import tool_cron
    tool_cron.createBgTask()

    return apaOp('start')


def stop():
    import tool_cron
    tool_cron.removeBgTask()
    return apaOp('stop')


def restart():
    status = apaOp('restart')
    return status


def reload():
    return apaOp('reload')


def dnsapiAdd():
    conn = pSqliteDb('dnsapi')
    args = getArgs()
    data = checkArgs(args,['id','name', 'type', 'remark'])
    if not data[0]:
        return data[1]

    name = args['name'].strip()
    remark = args['remark'].strip()
    stype = args['type'].strip()
    val = args['val'].strip()
    sid = args['id'].strip()

    if name == '':
        return mw.returnJson(False, '名称不能为空!')

    if sid != '0' : #修改操作
        conn.where("id=?", (sid,)).update({
            'name':name,
            'type':stype,
            'val':val,
            'remark':remark,
        })
        return mw.returnJson(True, '修改成功!')

    if conn.where("name=?", (name,)).count():
        return mw.returnJson(False, name+'已存在!')

    addTime = time.strftime('%Y-%m-%d %X', time.localtime())
    err = conn.add('name,type,val,remark,addtime', (name, stype, val,remark, addTime))
    # print(err)
    return mw.returnJson(True, '添加成功!')

def dnsapiDel():
    args = getArgs()
    data = checkArgs(args, ['id', 'name'])
    if not data[0]:
        return data[1]

    conn = pSqliteDb('dnsapi')
    try:
        sid = args['id']
        name = args['name']
        conn.where("id=?", (sid,)).delete()
        return mw.returnJson(True, '删除成功!')
    except Exception as ex:
        return mw.returnJson(False, '删除失败!' + str(ex))

def dnsapiList():
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

    conn = pSqliteDb('dnsapi')
    limit = str((page - 1) * page_size) + ',' + str(page_size)
    condition = ''
    if not search == '':
        condition = "name like '%" + search + "%'"
    field = 'id,name,type,val,remark,addtime'
    clist = conn.where(condition, ()).field(
        field).limit(limit).order('id desc').select()

    count = conn.where(condition, ()).count()
    _page = {}
    _page['count'] = count
    _page['p'] = page
    _page['row'] = page_size
    _page['tojs'] = 'dbList'
    data['page'] = mw.getPage(_page)
    data['data'] = clist

    return mw.getJson(data)

def dnsapiListAll():
    conn = pSqliteDb('dnsapi')
    field = 'id,name,type,val,remark,addtime'
    data = conn.field(field).limit('1000').select()
    return mw.getJson(data)

def emailList():
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

    conn = pSqliteDb('email')
    limit = str((page - 1) * page_size) + ',' + str(page_size)
    condition = ''
    if not search == '':
        condition = "addr like '%" + search + "%'"
    field = 'id,addr,remark,addtime'
    clist = conn.where(condition, ()).field(
        field).limit(limit).order('id desc').select()

    count = conn.where(condition, ()).count()
    _page = {}
    _page['count'] = count
    _page['p'] = page
    _page['row'] = page_size
    _page['tojs'] = 'dbList'
    data['page'] = mw.getPage(_page)
    data['data'] = clist

    return mw.getJson(data)

def emailAdd():
    args = getArgs()
    data = checkArgs(args,['addr', 'remark'])
    if not data[0]:
        return data[1]

    addr = args['addr'].strip()
    remark = args['remark'].strip()

    if addr == '':
        return mw.returnJson(False, '邮件地址不能为空!')

    conn = pSqliteDb('email')

    addTime = time.strftime('%Y-%m-%d %X', time.localtime())
    conn.add('addr,remark,addtime', (addr, remark, addTime))
    return mw.returnJson(True, '添加成功!')

def emailDel():
    args = getArgs()
    data = checkArgs(args, ['id', 'name'])
    if not data[0]:
        return data[1]

    conn = pSqliteDb('email')
    try:
        sid = args['id']
        name = args['name']
        conn.where("id=?", (sid,)).delete()
        return mw.returnJson(True, '删除成功!')
    except Exception as ex:
        return mw.returnJson(False, '删除失败!' + str(ex))

def domainAdd():
    args = getArgs()
    data = checkArgs(args,['id','domain', 'dnsapi_id','email','remark'])
    if not data[0]:
        return data[1]

    sid = args['id'].strip()
    domain = args['domain'].strip()
    remark = args['remark'].strip()
    email = args['email'].strip()
    dnsapi_id = args['dnsapi_id'].strip()

    if domain == '':
        return mw.returnJson(False, '域名不能为空!')
    if email == '':
        return mw.returnJson(False, '邮件不能为空!')

    conn = pSqliteDb('domain')

    if sid != '0' : #修改操作
        conn.where("id=?", (sid,)).update({
            'domain':domain,
            'dnsapi_id':dnsapi_id,
            'email':email,
            'remark':remark,
        })
        return mw.returnJson(True, '修改成功!')

    if conn.where("domain=?", (domain,)).count():
        return mw.returnJson(False, domain+'已存在!')

    

    addTime = time.strftime('%Y-%m-%d %X', time.localtime())
    conn.add('domain,dnsapi_id,email,remark,addtime', (domain, dnsapi_id,email,remark, addTime))
    return mw.returnJson(True, '添加成功!')

def domainDel():
    args = getArgs()
    data = checkArgs(args, ['id', 'name'])
    if not data[0]:
        return data[1]

    conn = pSqliteDb('domain')
    try:
        sid = args['id']
        name = args['name']
        conn.where("id=?", (sid,)).delete()
        return mw.returnJson(True, '删除成功!')
    except Exception as ex:
        return mw.returnJson(False, '删除失败!' + str(ex))

def domainList():
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

    conn = pSqliteDb('domain')
    conn_dnsapi = pSqliteDb('dnsapi')
    limit = str((page - 1) * page_size) + ',' + str(page_size)
    condition = ''
    if not search == '':
        condition = "domain like '%" + search + "%'"
    field = 'id,domain,dnsapi_id,email,remark,addtime'
    clist = conn.where(condition, ()).field(
        field).limit(limit).order('id desc').select()

    for i in range(len(clist)):
        tdata = conn_dnsapi.field('id,name').where('id=?',(clist[i]['dnsapi_id'],)).select()
        if len(tdata) > 0:
            # print(tdata[0]['name'])
            clist[i]['dnsapi_id_alias'] = clist[i]['dnsapi_id']+'('+ tdata[0]['name'] +')'
        else:
            clist[i]['dnsapi_id_alias'] = clist[i]['dnsapi_id']+' (无)'

    count = conn.where(condition, ()).count()
    _page = {}
    _page['count'] = count
    _page['p'] = page
    _page['row'] = page_size
    _page['tojs'] = 'dbList'
    data['page'] = mw.getPage(_page)
    data['data'] = clist

    return mw.getJson(data)

def runHook():
    return 'run hook'

def runLog():
    return getServerDir() + '/hook.log'

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
    elif func == 'run_log':
        print(runLog())
    elif func == 'config_tpl':
        print(configTpl())
    elif func == 'read_config_tpl':
        print(readConfigTpl())
    elif func == 'dnsapi_list':
        print(dnsapiList())
    elif func == 'dnsapi_list_all':
        print(dnsapiListAll())
    elif func == 'dnsapi_add':
        print(dnsapiAdd())
    elif func == 'dnsapi_del':
        print(dnsapiDel())
    elif func == 'email_list':
        print(emailList())
    elif func == 'email_add':
        print(emailAdd())
    elif func == 'email_del':
        print(emailDel())
    elif func == 'domain_list':
        print(domainList())
    elif func == 'domain_add':
        print(domainAdd())
    elif func == 'domain_del':
        print(domainDel())
    elif func == 'run_hook':
        print(runHook())
    else:
        print('error')
