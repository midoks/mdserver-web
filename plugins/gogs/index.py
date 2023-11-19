# coding: utf-8


import time
import os
import sys
import re


sys.path.append(os.getcwd() + "/class/core")
import mw


# cmd = 'ls /usr/local/lib/ | grep python  | cut -d \\  -f 1 | awk \'END {print}\''
# info = mw.execShell(cmd)
# p = "/usr/local/lib/" + info[0].strip() + "/site-packages"
# sys.path.append(p)

import psutil


app_debug = False
if mw.isAppleSystem():
    app_debug = True


def getPluginName():
    return 'gogs'


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
    path = getPluginDir() + "/init.d/gogs.tpl"
    return path


def getInitdConf():
    path = getServerDir() + "/init.d/gogs"
    return path


def getConf():
    path = getServerDir() + "/custom/conf/app.ini"
    return path


def getConfTpl():
    path = getPluginDir() + "/conf/app.ini"
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
        return '/root'


def getRunUser():
    if mw.isAppleSystem():
        user = mw.execShell(
            "who | sed -n '2, 1p' |awk '{print $1}'")[0].strip()
        return user
    else:
        return 'root'

__SR = '''#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH
export USER=%s
export HOME=%s && ''' % ( getRunUser(), getHomeDir())


def contentReplace(content):

    service_path = mw.getServerDir()
    content = content.replace('{$ROOT_PATH}', mw.getRootDir())
    content = content.replace('{$SERVER_PATH}', service_path)
    content = content.replace('{$RUN_USER}', getRunUser())
    content = content.replace('{$HOME_DIR}', getHomeDir())

    return content


def initDreplace():

    file_tpl = getInitdConfTpl()
    service_path = mw.getServerDir()

    initD_path = getServerDir() + '/init.d'
    if not os.path.exists(initD_path):
        os.mkdir(initD_path)
    file_bin = initD_path + '/' + getPluginName()

    if not os.path.exists(file_bin):
        content = mw.readFile(file_tpl)
        content = contentReplace(content)
        mw.writeFile(file_bin, content)
        mw.execShell('chmod +x ' + file_bin)

    # conf_bin = getConf()
    # if not os.path.exists(conf_bin):
    #     mw.execShell('mkdir -p ' + getServerDir() + '/custom/conf')
    #     conf_tpl = getConfTpl()
    #     content = mw.readFile(conf_tpl)
    #     content = contentReplace(content)
    #     mw.writeFile(conf_bin, content)

    # systemd
    systemDir = mw.systemdCfgDir()
    systemService = systemDir + '/gogs.service'
    systemServiceTpl = getPluginDir() + '/init.d/gogs.service.tpl'
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


def getRootUrl():
    content = mw.readFile(getConf())
    rep = 'ROOT_URL\s*=\s*(.*)'
    tmp = re.search(rep, content)
    if tmp:
        return tmp.groups()[0]

    rep = 'EXTERNAL_URL\s*=\s*(.*)'
    tmp = re.search(rep, content)
    if tmp:
        return tmp.groups()[0]
    return ''


def getSshPort():
    content = mw.readFile(getConf())
    rep = 'SSH_PORT\s*=\s*(.*)'
    tmp = re.search(rep, content)
    if not tmp:
        return ''
    return tmp.groups()[0]


def getHttpPort():
    content = mw.readFile(getConf())
    rep = 'HTTP_PORT\s*=\s*(.*)'
    tmp = re.search(rep, content)
    if not tmp:
        return ''
    return tmp.groups()[0]


def getRootPath():
    content = mw.readFile(getConf())
    rep = 'ROOT\s*=\s*(.*)'
    tmp = re.search(rep, content)
    if not tmp:
        return ''
    return tmp.groups()[0]


def getDbConfValue():
    conf = getConf()
    if not os.path.exists(conf):
        return {}

    content = mw.readFile(conf)
    rep_scope = "\[database\](.*?)\["
    tmp = re.findall(rep_scope, content, re.S)

    rep = '(\w*)\s*=\s*(.*)'
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
    dbname = 'gogs'
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


def getGogsDbType(conf):

    if 'DB_TYPE' in conf:
        return conf['DB_TYPE']

    if 'TYPE' in conf:
        return conf['TYPE']

    return 'NONE'


def pQuery(sql):
    conf = getDbConfValue()
    gtype = getGogsDbType(conf)
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


def gogsOp(method):
    file = initDreplace()

    if not mw.isAppleSystem():
        data = mw.execShell('systemctl ' + method + ' gogs')
        if data[1] == '':
            return 'ok'
        return 'fail'

    data = mw.execShell(__SR + file + ' ' + method)
    if data[1] == '':
        return 'ok'
    return data[0]


def start():
    return gogsOp('start')


def stop():
    return gogsOp('stop')


def restart():
    return gogsOp('restart')


def reload():
    return gogsOp('reload')


def initdStatus():
    if mw.isAppleSystem():
        return "Apple Computer does not support"

    shell_cmd = 'systemctl status gogs | grep loaded | grep "enabled;"'
    data = mw.execShell(shell_cmd)
    if data[0] == '':
        return 'fail'
    return 'ok'


def initdInstall():
    if mw.isAppleSystem():
        return "Apple Computer does not support"

    mw.execShell('systemctl enable gogs')
    return 'ok'


def initdUinstall():
    if mw.isAppleSystem():
        return "Apple Computer does not support"

    mw.execShell('systemctl disable gogs')
    return 'ok'


def runLog():
    log_path = getServerDir() + '/log/gogs.log'
    return log_path


def postReceiveLog():
    log_path = getServerDir() + '/log/hooks/post-receive.log'
    return log_path


def getGogsConf():
    conf = getConf()
    if not os.path.exists(conf):
        return mw.returnJson(False, "请先安装初始化!<br/>默认地址:http://" + mw.getLocalIp() + ":3000")

    gets = [
        {'name': 'DOMAIN', 'type': -1, 'ps': '服务器域名'},
        {'name': 'ROOT_URL', 'type': -1, 'ps': '公开的完整URL路径'},
        {'name': 'HTTP_ADDR', 'type': -1, 'ps': '应用HTTP监听地址'},
        {'name': 'HTTP_PORT', 'type': -1, 'ps': '应用 HTTP 监听端口号'},

        {'name': 'START_SSH_SERVER', 'type': 2, 'ps': '启动内置SSH服务器'},
        {'name': 'SSH_PORT', 'type': -1, 'ps': 'SSH 端口号'},

        {'name': 'REQUIRE_SIGNIN_VIEW', 'type': 2, 'ps': '强制登录浏览'},
        {'name': 'ENABLE_CAPTCHA', 'type': 2, 'ps': '启用验证码服务'},
        {'name': 'DISABLE_REGISTRATION', 'type': 2, 'ps': '禁止注册,只能由管理员创建帐号'},
        {'name': 'ENABLE_NOTIFY_MAIL', 'type': 2, 'ps': '是否开启邮件通知'},

        {'name': 'FORCE_PRIVATE', 'type': 2, 'ps': '强制要求所有新建的仓库都是私有'},

        {'name': 'SHOW_FOOTER_BRANDING', 'type': 2, 'ps': 'Gogs推广信息'},
        {'name': 'SHOW_FOOTER_VERSION', 'type': 2, 'ps': 'Gogs版本信息'},
        {'name': 'SHOW_FOOTER_TEMPLATE_LOAD_TIME', 'type': 2, 'ps': 'Gogs模板加载时间'},
    ]
    conf = mw.readFile(conf)
    result = []

    for g in gets:
        rep = g['name'] + '\s*=\s*(.*)'
        tmp = re.search(rep, conf)
        if not tmp:
            continue
        g['value'] = tmp.groups()[0]
        result.append(g)
    return mw.returnJson(True, 'OK', result)


def submitGogsConf():
    gets = ['DOMAIN',
            'ROOT_URL',
            'HTTP_ADDR',
            'HTTP_PORT',
            'START_SSH_SERVER',
            'SSH_PORT',
            'REQUIRE_SIGNIN_VIEW',
            'FORCE_PRIVATE',
            'ENABLE_CAPTCHA',
            'DISABLE_REGISTRATION',
            'ENABLE_NOTIFY_MAIL',
            'SHOW_FOOTER_BRANDING',
            'SHOW_FOOTER_VERSION',
            'SHOW_FOOTER_TEMPLATE_LOAD_TIME']
    args = getArgs()
    filename = getConf()
    conf = mw.readFile(filename)
    for g in gets:
        if g in args:
            rep = g + '\s*=\s*(.*)'
            val = g + ' = ' + args[g]
            conf = re.sub(rep, val, conf)
    mw.writeFile(filename, conf)
    reload()
    return mw.returnJson(True, '设置成功')


def gogsEditTpl():
    data = {}
    data['post_receive'] = getPluginDir() + '/hook/post-receive.tpl'
    data['commit'] = getPluginDir() + '/hook/commit.tpl'
    return mw.getJson(data)


def userList():

    conf = getConf()
    if not os.path.exists(conf):
        return mw.returnJson(False, "请先安装初始化!<br/>默认地址:http://" + mw.getLocalIp() + ":3000")

    conf = getDbConfValue()
    gtype = getGogsDbType(conf)
    if gtype != 'mysql':
        return mw.returnJson(False, "仅支持mysql数据操作!")

    import math
    args = getArgs()

    data = checkArgs(args, ['page', 'page_size'])
    if not data[0]:
        return data[1]

    page = int(args['page'])
    page_size = int(args['page_size'])
    search = ''
    if 'search' in args:
        search = args['search']

    user_where1 = ''
    user_where2 = ''
    if search != '':
        user_where1 = ' where name like "%' + search + '%"'
        user_where2 = ' where name like "%' + search + '%"'

    data = {}

    data['root_url'] = getRootUrl()

    start = (page - 1) * page_size
    list_count = pQuery('select count(id) as num from user' + user_where1)
    count = list_count[0]["num"]
    list_data = pQuery(
        'select id,name,email from user ' + user_where2 + ' order by id desc limit ' + str(start) + ',' + str(page_size))
    data['list'] = mw.getPage({'count': count, 'p': page,
                               'row': page_size, 'tojs': 'gogsUserList'})
    data['page'] = page
    data['page_size'] = page_size
    data['page_count'] = int(math.ceil(count / page_size))
    data['data'] = list_data
    return mw.returnJson(True, 'OK', data)


def checkRepoListIsHasScript(data):
    path = getRootPath()
    for x in range(len(data)):
        name = data[x]['name'] + '/' + data[x]['repo'] + '.git'
        path_tmp = path + '/' + name + '/custom_hooks/post-receive'
        if os.path.exists(path_tmp):
            data[x]['has_hook'] = True
        else:
            data[x]['has_hook'] = False
    return data


def repoList():

    conf = getConf()
    if not os.path.exists(conf):
        return mw.returnJson(False, "请先安装初始化!<br/>默认地址:http://" + mw.getLocalIp() + ":3000")

    conf = getDbConfValue()
    gtype = getGogsDbType(conf)
    if gtype != 'mysql':
        return mw.returnJson(False, "仅支持mysql数据操作!")

    import math
    args = getArgs()

    data = checkArgs(args, ['page', 'page_size'])
    if not data[0]:
        return data[1]

    page = int(args['page'])
    page_size = int(args['page_size'])
    search = ''
    if 'search' in args:
        search = args['search']

    data = {}

    data['root_url'] = getRootUrl()

    repo_where1 = ''
    repo_where2 = ''
    if search != '':
        repo_where1 = ' where name like "%' + search + '%"'
        repo_where2 = ' where r.name like "%' + search + '%"'

    start = (page - 1) * page_size
    list_count = pQuery(
        'select count(id) as num from repository' + repo_where1)
    count = list_count[0]["num"]
    sql = 'select r.id,r.owner_id,r.name as repo, u.name from repository r left join user u on r.owner_id=u.id ' + repo_where2 + ' order by r.id desc limit ' + \
        str(start) + ',' + str(page_size)
    # print(sql)
    list_data = pQuery(sql)
    # print(list_data)
    list_data = checkRepoListIsHasScript(list_data)

    data['list'] = mw.getPage({'count': count, 'p': page,
                               'row': page_size, 'tojs': 'gogsRepoListPage'})
    data['page'] = page
    data['page_size'] = page_size
    data['page_count'] = int(math.ceil(count / page_size))
    data['data'] = list_data
    return mw.returnJson(True, 'OK', data)


def getAllUserProject(user, search=''):
    path = getRootPath() + '/' + user
    dlist = []
    if os.path.exists(path):
        for filename in os.listdir(path):
            tmp = {}
            filePath = path + '/' + filename
            if os.path.isdir(filePath):
                if search == '':
                    tmp['name'] = filename.replace('.git', '')
                    dlist.append(tmp)
                else:
                    if filename.find(search) != -1:
                        tmp['name'] = filename.replace('.git', '')
                        dlist.append(tmp)
    return dlist


def checkProjectListIsHasScript(user, data):
    path = getRootPath() + '/' + user
    for x in range(len(data)):
        name = data[x]['name'] + '.git'
        path_tmp = path + '/' + name + '/custom_hooks/post-receive'
        if os.path.exists(path_tmp):
            data[x]['has_hook'] = True
        else:
            data[x]['has_hook'] = False
    return data


def userProjectList():
    import math
    args = getArgs()
    # print args

    page = 1
    page_size = 5
    search = ''

    if not 'name' in args:
        return mw.returnJson(False, '缺少参数name')
    if 'page' in args:
        page = int(args['page'])

    if 'page_size' in args:
        page_size = int(args['page_size'])

    if 'search' in args:
        search = args['search']

    data = {}

    ulist = getAllUserProject(args['name'])
    dlist_sum = len(ulist)

    start = (page - 1) * page_size
    ret_data = ulist[start:start + page_size]
    ret_data = checkProjectListIsHasScript(args['name'], ret_data)

    data['root_url'] = getRootUrl()
    data['data'] = ret_data
    data['args'] = args
    data['list'] = mw.getPage(
        {'count': dlist_sum, 'p': page, 'row': page_size, 'tojs': 'userProjectListPage'})

    return mw.returnJson(True, 'OK', data)


def projectScriptEdit():
    args = getArgs()

    if not 'user' in args:
        return mw.returnJson(True, 'username missing')

    if not 'name' in args:
        return mw.returnJson(True, 'project name missing')

    user = args['user']
    name = args['name'] + '.git'
    post_receive = getRootPath() + '/' + user + '/' + name + \
        '/custom_hooks/commit'
    if os.path.exists(post_receive):
        return mw.returnJson(True, 'OK', {'path': post_receive})
    else:
        return mw.returnJson(False, 'file does not exist')


def projectScriptLoad():
    args = getArgs()
    if not 'user' in args:
        return mw.returnJson(True, 'username missing')

    if not 'name' in args:
        return mw.returnJson(True, 'project name missing')

    user = args['user']
    name = args['name'] + '.git'

    path = getRootPath() + '/' + user + '/' + name
    post_receive_tpl = getPluginDir() + '/hook/post-receive.tpl'
    post_receive = path + '/custom_hooks/post-receive'

    if not os.path.exists(path + '/custom_hooks'):
        mw.execShell('mkdir -p ' + path + '/custom_hooks')

    pct_content = mw.readFile(post_receive_tpl)
    pct_content = pct_content.replace('{$PATH}', path + '/custom_hooks')
    mw.writeFile(post_receive, pct_content)
    mw.execShell('chmod 777 ' + post_receive)

    commit_tpl = getPluginDir() + '/hook/commit.tpl'
    commit = path + '/custom_hooks/commit'

    codeDir = mw.getRootDir() + '/git'

    cc_content = mw.readFile(commit_tpl)

    gitPath = getRootPath()
    cc_content = cc_content.replace('{$GITROOTURL}', gitPath)
    cc_content = cc_content.replace('{$CODE_DIR}', codeDir)
    cc_content = cc_content.replace('{$USERNAME}', user)
    cc_content = cc_content.replace('{$PROJECT}', args['name'])
    cc_content = cc_content.replace('{$WEB_ROOT}', mw.getWwwDir())
    mw.writeFile(commit, cc_content)
    mw.execShell('chmod 777 ' + commit)

    return 'ok'


def projectScriptUnload():
    args = getArgs()
    data = checkArgs(args, ['user', 'name'])
    if not data[0]:
        return data[1]

    user = args['user']
    name = args['name'] + '.git'

    post_receive = getRootPath() + '/' + user + '/' + name + \
        '/custom_hooks/post-receive'
    mw.execShell('rm -f ' + post_receive)

    commit = getRootPath() + '/' + user + '/' + name + \
        '/custom_hooks/commit'
    mw.execShell('rm -f ' + commit)
    return 'ok'


def projectScriptDebug():
    args = getArgs()
    data = checkArgs(args, ['user', 'name'])
    if not data[0]:
        return data[1]

    user = args['user']
    name = args['name'] + '.git'
    commit_log = getRootPath() + '/' + user + '/' + name + \
        '/custom_hooks/sh.log'

    data = {}
    if os.path.exists(commit_log):
        data['status'] = True
        data['path'] = commit_log
    else:
        data['status'] = False
        data['msg'] = '没有日志文件'

    return mw.getJson(data)


def projectScriptRun():
    args = getArgs()
    data = checkArgs(args, ['user', 'name'])
    if not data[0]:
        return data[1]

    user = args['user']
    name = args['name'] + '.git'

    path = getRootPath() + '/' + user + '/' + name
    commit_sh = path + '/custom_hooks/commit'
    commit_log = path + '/custom_hooks/sh.log'
    script_run = 'sh -x ' + commit_sh + ' 2>' + commit_log

    if not os.path.exists(commit_sh):
        return mw.returnJson(False, '脚本文件不存在!')

    mw.execShell(script_run)
    return mw.returnJson(True, '脚本文件执行成功,观察日志!')


def projectScriptSelf():
    args = getArgs()
    data = checkArgs(args, ['user', 'name'])
    if not data[0]:
        return data[1]

    user = args['user']
    name = args['name'] + '.git'

    custom_hooks = getRootPath() + '/' + user + '/' + \
        name + '/custom_hooks'

    self_path = custom_hooks + '/self'
    if not os.path.exists(self_path):
        os.mkdir(self_path)

    self_logs_path = custom_hooks + '/self_logs'
    if not os.path.exists(self_logs_path):
        os.mkdir(self_logs_path)

    self_hook_file = custom_hooks + '/self_hook.sh'
    self_hook_exist = False
    if os.path.exists(self_hook_file):
        self_hook_exist = True

    dlist = []
    if os.path.exists(self_path):
        for filename in os.listdir(self_path):
            tmp = {}
            filePath = self_path + '/' + filename
            if os.path.isfile(filePath):
                tmp['path'] = filePath
                tmp['name'] = os.path.basename(filePath)
                tmp['is_hidden'] = False
                if tmp['name'].endswith('.txt'):
                    tmp['is_hidden'] = True

                dlist.append(tmp)

    dlist_sum = len(dlist)
    # print(dlist)
    rdata = {}
    rdata['data'] = dlist
    rdata['self_hook'] = self_hook_exist
    rdata['list'] = mw.getPage(
        {'count': dlist_sum, 'p': 1, 'row': 100, 'tojs': 'self_page'})

    return mw.returnJson(True, 'ok', rdata)


def projectScriptSelf_Create():
    args = getArgs()
    data = checkArgs(args, ['user', 'name', 'file'])
    if not data[0]:
        return data[1]

    user = args['user']
    name = args['name'] + '.git'
    file = args['file']

    self_path = path = getRootPath() + '/' + user + '/' + \
        name + '/custom_hooks/self'

    if not os.path.exists(self_path):
        os.mkdir(self_path)

    abs_file = self_path + '/' + file + '.sh'
    if os.path.exists(abs_file):
        return mw.returnJson(False, '脚本已经存在!')

    mw.writeFile(abs_file, "#!/bin/bash\necho `date +'%Y-%m-%d %H:%M:%S'`\n")

    rdata = {}
    rdata['abs_file'] = abs_file
    return mw.returnJson(True, '创建文件成功!', rdata)


def projectScriptSelf_Del():
    args = getArgs()
    data = checkArgs(args, ['user', 'name', 'file'])
    if not data[0]:
        return data[1]

    user = args['user']
    name = args['name'] + '.git'
    file = args['file']

    custom_hooks = getRootPath() + '/' + user + '/' + \
        name + '/custom_hooks'
    self_path = custom_hooks + '/self'

    if not os.path.exists(self_path):
        os.mkdir(self_path)

    abs_file = self_path + '/' + file
    # print(abs_file)
    if not os.path.exists(abs_file):
        return mw.returnJson(False, '脚本已经删除!')

    os.remove(abs_file)

    # 日志也删除
    log_file = custom_hooks + '/self_logs/' + file + '.log'
    if os.path.exists(log_file):
        os.remove(log_file)

    return mw.returnJson(True, '脚本删除成功!')


def projectScriptSelf_Logs():
    args = getArgs()
    data = checkArgs(args, ['user', 'name', 'file'])
    if not data[0]:
        return data[1]

    user = args['user']
    name = args['name'] + '.git'
    file = args['file']

    self_path = path = getRootPath() + '/' + user + '/' + \
        name + '/custom_hooks/self_logs'

    if not os.path.exists(self_path):
        os.mkdir(self_path)

    logs_file = self_path + '/' + file + '.log'
    if os.path.exists(logs_file):
        rdata = {}
        rdata['path'] = logs_file
        return mw.returnJson(True, 'ok', rdata)

    return mw.returnJson(False, '日志不存在!')


def projectScriptSelf_Run():
    args = getArgs()
    data = checkArgs(args, ['user', 'name', 'file'])
    if not data[0]:
        return data[1]

    user = args['user']
    name = args['name'] + '.git'
    file = args['file']

    custom_hooks = getRootPath() + '/' + user + '/' + \
        name + '/custom_hooks'
    self_path = custom_hooks + '/self/' + file
    self_logs_path = custom_hooks + '/self_logs/' + file + '.log'

    shell = "sh -x " + self_path + " 2>" + self_logs_path + ' &'
    mw.execShell(shell)
    return mw.returnJson(True, '执行成功!')


def projectScriptSelf_Rename():
    args = getArgs()
    data = checkArgs(args, ['user', 'name', 'o_file', 'n_file'])
    if not data[0]:
        return data[1]

    user = args['user']
    name = args['name'] + '.git'
    o_file = args['o_file']
    n_file = args['n_file']

    custom_hooks = getRootPath() + '/' + user + '/' + \
        name + '/custom_hooks'
    self_path = custom_hooks + '/self'

    if not os.path.exists(self_path):
        os.mkdir(self_path)

    o_file_abs = self_path + '/' + o_file + '.sh'
    if not os.path.exists(o_file_abs):
        return mw.returnJson(False, '原文件已经不存在了!')

    n_file_abs = self_path + '/' + n_file + '.sh'

    os.rename(o_file_abs, n_file_abs)

    # 日志也删除
    log_file = custom_hooks + '/self_logs/' + o_file + '.sh.log'
    if os.path.exists(log_file):
        os.remove(log_file)

    return mw.returnJson(True, '重命名成功!')


def projectScriptSelf_Enable():
    args = getArgs()
    data = checkArgs(args, ['user', 'name', 'enable'])
    if not data[0]:
        return data[1]

    user = args['user']
    name = args['name'] + '.git'
    enable = args['enable']

    custom_path = getRootPath() + '/' + user + '/' + \
        name + '/custom_hooks'

    # 替换commit配置
    commit_path = custom_path + '/commit'
    note = '#Gogs Script Don`t Remove and Change'

    self_file = custom_path + '/self_hook.sh'
    self_hook_tpl = getPluginDir() + '/hook/self_hook.tpl'

    if enable == '1':
        content = mw.readFile(self_hook_tpl)
        content = content.replace('{$HOOK_DIR}', custom_path + '/self')
        content = content.replace(
            '{$HOOK_LOGS_DIR}', custom_path + '/self_logs')
        mw.writeFile(self_file, content)
        mw.execShell("chmod 777 " + self_file)

        commit_content = mw.readFile(commit_path)
        commit_content += "\n\n" + "bash " + self_file + " " + note
        mw.writeFile(commit_path, commit_content)

        return mw.returnJson(True, '开启成功!')
    else:
        commit_content = mw.readFile(commit_path)
        rep = ".*" + note
        commit_content = re.sub(rep, '', commit_content, re.M)
        commit_content = commit_content.strip()
        mw.writeFile(commit_path, commit_content)
        if os.path.exists(self_file):
            os.remove(self_file)
        return mw.returnJson(True, '关闭成功!')


def projectScriptSelf_Status():
    args = getArgs()
    data = checkArgs(args, ['user', 'name', 'file', 'status'])
    if not data[0]:
        return data[1]

    user = args['user']
    name = args['name'] + '.git'
    file = args['file']
    status = args['status']

    custom_hooks = getRootPath() + '/' + user + '/' + \
        name + '/custom_hooks'
    self_path = custom_hooks + '/self'

    if not os.path.exists(self_path):
        os.mkdir(self_path)

    # 日志也删除
    log_file = custom_hooks + '/self_logs/' + file + '.log'
    if os.path.exists(log_file):
        os.remove(log_file)

    if status == '1':
        file_abs = self_path + '/' + file
        file_text_abs = self_path + '/' + file + '.txt'
        os.rename(file_abs, file_text_abs)
        return mw.returnJson(True, '开始禁用成功!')
    else:
        file_abs = self_path + '/' + file.strip('.txt')
        file_text_abs = self_path + '/' + file
        os.rename(file_text_abs, file_abs)
        return mw.returnJson(True, '开始使用成功!')

    return mw.returnJson(True, '禁用成功!')


def getRsaPublic():
    path = getHomeDir()
    path += '/.ssh/id_rsa.pub'

    content = mw.readFile(path)

    data = {}
    data['mw'] = content
    return mw.getJson(data)


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
    elif func == 'run_log':
        print(runLog())
    elif func == 'post_receive_log':
        print(postReceiveLog())
    elif func == 'conf':
        print(getConf())
    elif func == 'init_conf':
        print(getInitdConf())
    elif func == 'get_gogs_conf':
        print(getGogsConf())
    elif func == 'submit_gogs_conf':
        print(submitGogsConf())
    elif func == 'gogs_edit_tpl':
        print(gogsEditTpl())
    elif func == 'user_list':
        print(userList())
    elif func == 'repo_list':
        print(repoList())
    elif func == 'user_project_list':
        print(userProjectList())
    elif func == 'project_script_edit':
        print(projectScriptEdit())
    elif func == 'project_script_load':
        print(projectScriptLoad())
    elif func == 'project_script_unload':
        print(projectScriptUnload())
    elif func == 'project_script_debug':
        print(projectScriptDebug())
    elif func == 'project_script_run':
        print(projectScriptRun())
    elif func == 'project_script_self':
        print(projectScriptSelf())
    elif func == 'project_script_self_create':
        print(projectScriptSelf_Create())
    elif func == 'project_script_self_del':
        print(projectScriptSelf_Del())
    elif func == 'project_script_self_logs':
        print(projectScriptSelf_Logs())
    elif func == 'project_script_self_run':
        print(projectScriptSelf_Run())
    elif func == 'project_script_self_rename':
        print(projectScriptSelf_Rename())
    elif func == 'project_script_self_enable':
        print(projectScriptSelf_Enable())
    elif func == 'project_script_self_status':
        print(projectScriptSelf_Status())
    elif func == 'get_rsa_public':
        print(getRsaPublic())
    elif func == 'get_total_statistics':
        print(getTotalStatistics())
    else:
        print('fail')
