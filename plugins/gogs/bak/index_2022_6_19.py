# coding: utf-8


import time
import os
import sys
import re


sys.path.append(os.getcwd() + "/class/core")
import mw


cmd = 'ls /usr/local/lib/ | grep python  | cut -d \\  -f 1 | awk \'END {print}\''
info = mw.execShell(cmd)
p = "/usr/local/lib/" + info[0].strip() + "/site-packages"
sys.path.append(p)
import psutil


app_debug = False
if mw.isAppleSystem():
    app_debug = True


def getPluginName():
    return 'gogs'


def getPluginDir():
    return mw.getPluginDir() + '/' + getPluginName()

sys.path.append(getPluginDir() + "/class")
import mysqlDb


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

    conf_bin = getConf()
    if not os.path.exists(conf_bin):
        mw.execShell('mkdir -p ' + getServerDir() + '/custom/conf')
        conf_tpl = getConfTpl()
        content = mw.readFile(conf_tpl)
        content = contentReplace(content)
        mw.writeFile(conf_bin, content)

    log_path = getServerDir() + '/log'
    if not os.path.exists(log_path):
        os.mkdir(log_path)

    return file_bin


def getRootUrl():
    content = mw.readFile(getConf())
    rep = 'ROOT_URL\s*=\s*(.*)'
    tmp = re.search(rep, content)
    if not tmp:
        return ''
    return tmp.groups()[0]


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
    content = mw.readFile(getConf())

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


def pMysqlDb():
    conf = getDbConfValue()

    host = conf['HOST'].split(':')
    conn = mysqlDb.mysqlDb()

    conn.setHost(host[0])
    conn.setUser(conf['USER'])
    conn.setPwd(conf['PASSWD'])
    conn.setPort(int(host[1]))
    conn.setDb(conf['NAME'])
    return conn


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


def start():

    is_frist = True
    conf_bin = getConf()
    if os.path.exists(conf_bin):
        is_frist = False

    file = initDreplace()

    if is_frist:
        return "第一次启动Gogs,默认使用MySQL连接!<br>可以在配置文件中重新设置,再启动!"

    conn = pMysqlDb()
    list_table = conn.query('show tables')
    data = isSqlError(list_table)
    if not data['status']:
        return data['msg']

    data = mw.execShell(__SR + file + ' start')
    if data[1] == '':
        return 'ok'
    return data[0]


def stop():
    file = initDreplace()
    data = mw.execShell(__SR + file + ' stop')
    if data[1] == '':
        return 'ok'
    return data[1]


def restart():
    file = initDreplace()
    data = mw.execShell(__SR + file + ' restart')
    if data[1] == '':
        return 'ok'
    return data[1]


def reload():
    file = initDreplace()
    data = mw.execShell(__SR + file + ' reload')
    if data[1] == '':
        return 'ok'
    return data[1]


def initdStatus():
    if not app_debug:
        os_name = mw.getOs()
        if os_name == 'darwin':
            return "Apple Computer does not support"
    initd_bin = getInitDFile()
    if os.path.exists(initd_bin):
        return 'ok'
    return 'fail'


def initdInstall():
    import shutil
    if not app_debug:
        os_name = mw.getOs()
        if os_name == 'darwin':
            return "Apple Computer does not support"

    mem_bin = initDreplace()
    initd_bin = getInitDFile()
    shutil.copyfile(mem_bin, initd_bin)
    mw.execShell('chmod +x ' + initd_bin)
    mw.execShell('chkconfig --add ' + getPluginName())
    return 'ok'


def initdUinstall():
    if not app_debug:
        os_name = mw.getOs()
        if os_name == 'darwin':
            return "Apple Computer does not support"
    initd_bin = getInitDFile()
    os.remove(initd_bin)
    mw.execShell('chkconfig --del ' + getPluginName())
    return 'ok'


def runLog():
    log_path = getServerDir() + '/log/gogs.log'
    return log_path


def postReceiveLog():
    log_path = getServerDir() + '/log/hooks/post-receive.log'
    return log_path


def getGogsConf():
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
    conf = mw.readFile(getConf())
    result = []

    for g in gets:
        rep = g['name'] + '\s*=\s*(.*)'
        tmp = re.search(rep, conf)
        if not tmp:
            continue
        g['value'] = tmp.groups()[0]
        result.append(g)
    return mw.getJson(result)


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


def userList():
    import math
    args = getArgs()

    page = 1
    page_size = 10
    search = ''
    if 'page' in args:
        page = int(args['page'])

    if 'page_size' in args:
        page_size = int(args['page_size'])

    if 'search' in args:
        search = args['search']

    data = {}

    data['root_url'] = getRootUrl()

    pm = pMysqlDb()
    start = (page - 1) * page_size
    list_count = pm.query('select count(id) as num from user')
    count = list_count[0][0]

    list_data = pm.query(
        'select id,name,email from user order by id desc limit ' + str(start) + ',' + str(page_size))

    page_info = {'count': count, 'p': page,
                 'row': page_size, 'tojs': 'gogsUserList'}
    data['list'] = mw.getPage(page_info)
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
        {'count': dlist_sum, 'p': page, 'row': page_size, 'tojs': 'userProjectList'})

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

    sshUrl = 'http://127.0.0.1:' + getHttpPort()
    cc_content = cc_content.replace('{$GITROOTURL}', sshUrl)
    cc_content = cc_content.replace('{$CODE_DIR}', codeDir)
    cc_content = cc_content.replace('{$USERNAME}', user)
    cc_content = cc_content.replace('{$PROJECT}', args['name'])
    cc_content = cc_content.replace('{$WEB_ROOT}', mw.getWwwDir())
    mw.writeFile(commit, cc_content)
    mw.execShell('chmod 777 ' + commit)

    return 'ok'


def projectScriptUnload():
    args = getArgs()
    if not 'user' in args:
        return mw.returnJson(True, 'username missing')

    if not 'name' in args:
        return mw.returnJson(True, 'project name missing')

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
    if not 'user' in args:
        return mw.returnJson(True, 'username missing')

    if not 'name' in args:
        return mw.returnJson(True, 'project name missing')
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


def gogsEdit():
    data = {}
    data['post_receive'] = getPluginDir() + '/hook/post-receive.tpl'
    data['commit'] = getPluginDir() + '/hook/commit.tpl'
    return mw.getJson(data)


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
        pm = pMysqlDb()
        list_count = pm.query('select count(id) as num from repository')

        if list_count.find("error") > -1:
            data['status'] = False
            data['count'] = 0
            return mw.returnJson(False, 'fail', data)

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
    elif func == 'user_list':
        print(userList())
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
    elif func == 'gogs_edit':
        print(gogsEdit())
    elif func == 'get_rsa_public':
        print(getRsaPublic())
    elif func == 'get_total_statistics':
        print(getTotalStatistics())
    else:
        print('fail')
