# coding:utf-8

import sys
import io
import os
import time
import re
import requests
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

def runLog():
    return getServerDir() + '/hook.log'

def getArgs():
    args = sys.argv[3:]
    # print(args)
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


def getHomeDir():
    if mw.isAppleSystem():
        user = mw.execShell(
            "who | sed -n '2, 1p' |awk '{print $1}'")[0].strip()
        return '/Users/' + user
    else:
        return '/root'


def getRunUser():
    if mw.isAppleSystem():
        user = mw.execShell(
            "who | sed -n '2, 1p' |awk '{print $1}'")[0].strip()
        return user
    else:
        return 'root'

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
    content = content.replace('{$ROOT_PATH}', mw.getFatherDir())
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

def domainStatusToggle():
    args = getArgs()
    data = checkArgs(args, ['id'])
    if not data[0]:
        return data[1]

    conn = pSqliteDb('domain')

    field = 'id,status'
    fdata = conn.field(field).where('id=?',(args['id'],)).find()

    fstatus = fdata['status']
    if fstatus == 0:
        fstatus = 1
    else:
        fstatus = 0
    # print(fdata['status'],fstatus)
    conn.where("id=?", (args['id'],)).update({
        'status':fstatus,
    })
    return mw.returnJson(True, '切换成功!')

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
    field = 'id,domain,dnsapi_id,email,status,effective_date,expiration_date,remark,addtime'
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

def getDnsapiData(dnsapi_id):
    if dnsapi_id == '0':
        return {}
    conn_dnsapi = pSqliteDb('dnsapi')
    tdata = conn_dnsapi.field('id,name,type,val').where('id=?',(dnsapi_id,)).select()

    if len(tdata)>0:
        return tdata[0]
    return {}

def getDnsapiExportVar(val):
    cmd_list =  val.split('~')
    def_var = ''
    for x in range(len(cmd_list)):
        v = cmd_list[x]
        vlist = v.split('|')
        def_var += 'export '+vlist[0]+'="'+vlist[1]+'"\n'
    return def_var

def getDnsapiKv(val):
    cmd_list =  val.split('~')
    def_var = {}
    for x in range(len(cmd_list)):
        v = cmd_list[x]
        vlist = v.split('|')
        kk = vlist[0]
        vv = vlist[1]
        def_var[kk] = vv
    return def_var

def domainApplyPathJudge(domain):
    acme_dir = "/root/.acme.sh"
    if mw.isAppleSystem():
        user = getRunUser()
        acme_dir = "/Users/"+user+"/.acme.sh"

    abs_domain_path = acme_dir+'/'+domain+'_ecc'
    # print(abs_domain_path)
    if os.path.exists(abs_domain_path):
        return True, abs_domain_path

    abs_domain_path = acme_dir+'/'+domain
    # print(abs_domain_path)
    if os.path.exists(abs_domain_path):
        return True, abs_domain_path

    return False,''


def hookWriteLog(line):
    hook_file = runLog()
    mdate = time.strftime('%Y-%m-%d %X', time.localtime())
    log = "["+mdate+"]:"+line
    print(log)
    return mw.writeFile(hook_file,log+"\n",'a+')

def runHookPy(domain,path):
    # print(domain,path)
    run_log = runLog()
    hook_file = getConf()
    cmd = 'cd '+mw.getPanelDir()
    cmd += ' && python3 '+hook_file + ' ' + domain + ' ' + path
    cmd += ' >> '+ run_log
    print(cmd)
    return mw.execShell(cmd)

def autoUpdateSslData(domain, path):
    ssl_cer_file = path + '/'+domain+'.cer'
    ssl_info = mw.getCertName(ssl_cer_file)

    time_begin = int(time.mktime(time.strptime(ssl_info['notBefore'], "%Y-%m-%d")))
    time_end = int(time.mktime(time.strptime(ssl_info['notAfter'], "%Y-%m-%d")))
    # print(ssl_info)
    # print(time_begin,time_end)
    conn = pSqliteDb('domain')
    conn.where('domain=?', (domain,)).update({
        'effective_date':str(time_begin),
        'expiration_date':str(time_end),
    })

    return True

def runHookDstDomain(row):
    domain = row['domain']
    email = str(row['email'])

    if row['effective_date'] != '':
        effective_date = int(row['effective_date'])
        now_int = int(time.time())
        day = (now_int - effective_date)/86400
        if int(day) < 8:
            common_log = '【'+domain+'】未过期'
            hookWriteLog(common_log)
            return

    hookWriteLog('开始申请【'+domain+'】SSL证书')
    cmd = "#!/bin/bash\n"

    if mw.isAppleSystem():
        user = getRunUser()
        cmd += "source /Users/"+user+"/.zshrc\n"

    cmd_data = getDnsapiData(row['dnsapi_id'])
    # print(cmd_data)
    export_val =  getDnsapiExportVar(cmd_data['val'])
    cmd += export_val

    # acme.sh --register-account -m my@example.com
    cmd_register = 'acme.sh --register-account -m '+ email + '\n'
    cmd += cmd_register

    
    # acme.sh --issue -d "example.com" -d "*.example.com" --dns dns_cf
    cmd_apply = 'acme.sh --issue --dns '+str(cmd_data['type'])+' -d '+domain+' -d "*.'+domain+'"'
    if row['effective_date'] != '':
        effective_date = int(row['effective_date'])
        now_int = int(time.time())
        day = (now_int - effective_date)/86400
        if int(day) > 7:
            cmd_apply = 'acme.sh --issue --dns '+str(cmd_data['type'])+' -d '+domain+' -d "*.'+domain+'" --force'
    cmd += cmd_apply

    run_log = runLog()
    cmd += ' >> '+ run_log
    print(cmd)
    os.system(cmd)
    hookWriteLog('结束申请【'+domain+'】SSL证书')
    isok, path = domainApplyPathJudge(domain)
    print(isok,path)
    if isok:
        autoUpdateSslData(domain, path)
        hookWriteLog('开始执行【'+domain+'】Hook脚本')
        runHookPy(domain,path)
        hookWriteLog('结束执行【'+domain+'】Hook脚本')

def getHookIdCmd():
    args = getArgs()
    data = checkArgs(args, ['id'])
    if not data[0]:
        return data[1]

    cmd = "cd "+mw.getPanelDir()+" "
    cmd += '&& python3 plugins/acme_pandominassl_apply/index.py run_hook_id 1.0 {"id":"'+args['id']+'"}'
    return mw.returnJson(True, 'ok',cmd)

def runHookId():
    args = getArgs()
    data = checkArgs(args, ['id'])
    if not data[0]:
        return data[1]

    conn = pSqliteDb('domain')
    field = 'id,domain,dnsapi_id,email,effective_date,expiration_date,remark'
    row = conn.field(field).where('id=?',(args['id'],)).find()
    runHookDstDomain(row)
    return 'run hook '+args['id']+' end'

def runHookCmd():
    cmd = "cd "+mw.getPanelDir()+" "
    cmd += '&& python3 plugins/acme_pandominassl_apply/index.py run_hook'
    return mw.returnJson(True, 'ok',cmd)

def runHook():
    conn = pSqliteDb('domain')

    field = 'id,domain,dnsapi_id,email,effective_date,expiration_date,remark'
    clist = conn.field(field).where('status=?',(1,)).limit('1000').order('id desc').select()

    for idx in range(len(clist)):
        row = clist[idx]
        # print(row)
        runHookDstDomain(row)
        time.sleep(1)
    return 'run hook end'

def autoSyncDomain(domain, dnsapi_id, email):
    conn = pSqliteDb('domain')

    field = 'id,domain,dnsapi_id,email,effective_date,expiration_date,remark'
    fdata = conn.field(field).where('domain=?',(domain,)).select()
    # print(fdata)
    mdate = time.strftime('%Y-%m-%d %X', time.localtime())
    if len(fdata) == 0:
        conn.add('domain,dnsapi_id,email,remark,addtime', (domain, dnsapi_id, email,"备注", mdate))
        print(domain+" 同步成功!")
    return True

def runSyncCfDataRow(row, page = 1):
    # print(row, page)

    cf_key = row['kv']['CF_Key']
    cf_mail = row['kv']['CF_Email']
    header = {
        'X-Auth-Email': cf_mail,
        'X-Auth-Key': cf_key,
        'Content-Type': 'application/json'
    }
    url = "https://api.cloudflare.com/client/v4/zones?status=active&page="+str(page)+"&per_page=20&order=status&direction=desc&match=all"
    try:
        r = requests.get(url, timeout=30, headers=header)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        # print(r.text)
        jdata = json.loads(r.text)
        result = jdata['result']
        result_info = jdata['result_info']

        # print(len(result))
        for i in result:
            autoSyncDomain(i['name'], row['id'], cf_mail)

        if result_info['total_pages'] > page:
            page += 1
            runSyncCfDataRow(row, page)
        # print(result)
    except Exception as e:
        print(e)

# 同步CloudFlare数据
def runSyncCfData():
    print("同步CloudFlare数据开始")
    conn_dnsapi = pSqliteDb('dnsapi')
    field = "id,name,type,val"
    fdata = conn_dnsapi.field(field).where('type=?', ('dns_cf',)).limit('10').select()

    for x in range(len(fdata)):
        row = fdata[x]
        dnsapi_kv = getDnsapiKv(row['val'])
        row['kv'] = dnsapi_kv
        runSyncCfDataRow(row)

    print("同步CloudFlare数据结束")
    return ''

def runSyncCfCmd():
    cmd = "cd "+mw.getPanelDir()+" "
    cmd += '&& python3 plugins/acme_pandominassl_apply/index.py run_sync_cf_data'
    return mw.returnJson(True, 'ok',cmd)

def runSyncDnspodDataRow(row, page = 1):
    # print(row, page)

    DPI_Id = row['kv']['DPI_Id']
    DPI_Key = row['kv']['DPI_Key']
    data = {
        'login_token': DPI_Id+','+DPI_Key,
        'length':5,
        'format':'json',
    }
    url = "https://api.dnspod.com/Domain.List"
    try:
        r = requests.post(url, timeout=30, data=data)
        r.raise_for_status()
        r.encoding = r.apparent_encoding

        # print(r.text)
        jdata = json.loads(r.text)
        info = jdata['info']
        domains = jdata['domains']

        # print(jdata)
        for i in domains:
            autoSyncDomain(i['name'], row['id'], i['owner'])

        page_total = int(info['domain_total']/data['length'])
        if page_total > page:
            page += 1
            runSyncDnspodDataRow(row, page)
    except Exception as e:
        print(e)

# 同步DnsPod数据
def runSyncDnsPodData():
    print("同步DnsPod数据开始")
    conn_dnsapi = pSqliteDb('dnsapi')
    field = "id,name,type,val"
    fdata = conn_dnsapi.field(field).where('type=?', ('dns_dpi',)).limit('10').select()
    for x in range(len(fdata)):
        row = fdata[x]
        dnsapi_kv = getDnsapiKv(row['val'])
        row['kv'] = dnsapi_kv
        runSyncDnspodDataRow(row)

    print(fdata)
    print("同步DnsPod数据结束")
    return ''

def runSyncDnsPodCmd():
    cmd = "cd "+mw.getPanelDir()+" "
    cmd += '&& python3 plugins/acme_pandominassl_apply/index.py run_sync_dnspod_data'
    return mw.returnJson(True, 'ok',cmd)

if __name__ == "__main__":
    func = sys.argv[1]
    # print(func)
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
    elif func == 'domain_status_toggle':
        print(domainStatusToggle())
    elif func == 'run_hook':
        print(runHook())
    elif func == 'run_hook_cmd':
        print(runHookCmd())
    elif func == 'get_run_hook_id_cmd':
        print(getHookIdCmd())
    elif func == 'run_hook_id':
        print(runHookId())
    elif func == 'run_sync_cf_data':
        print(runSyncCfData())
    elif func == 'run_sync_cf_cmd':
        print(runSyncCfCmd())
    elif func == 'run_sync_dnspod_data':
        print(runSyncDnsPodData())
    elif func == 'run_sync_dnspod_cmd':
        print(runSyncDnsPodCmd())
    else:
        print('error')
