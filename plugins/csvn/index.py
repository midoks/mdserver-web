# coding: utf-8

import time
import random
import os
import urllib
import binascii
import json
import re
import sys
import subprocess

sys.path.append(os.getcwd() + "/class/core")
import mw


app_debug = False
if mw.isAppleSystem():
    app_debug = True


def getPluginName():
    return 'csvn'


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
        t = t.split(':')
        tmp[t[0]] = t[1]
    elif args_len > 1:
        for i in range(len(args)):
            t = args[i].split(':')
            tmp[t[0]] = t[1]

    return tmp


def initDreplace():
    initd_file = getInitDFile()

    if not os.path.exists(initd_file):
        return getServerDir()

    return initd_file


def status():
    data = mw.execShell(
        "ps -ef|grep " + getPluginName() + " |grep -v grep | grep -v python | awk '{print $2}'")
    if data[0] == '':
        return 'stop'
    return 'start'


def csvnOp(method):

    if app_debug:
        os_name = mw.getOs()
        if os_name == 'darwin':
            return "Apple Computer does not support"

    _initd_csvn = '/etc/init.d/csvn'
    _initd_csvn_httpd = '/etc/init.d/csvn-httpd'
    #_csvn = getServerDir() + '/bin/csvn'
    #_csvn_httpd = getServerDir() + '/bin/csvn-httpd'

    ret_csvn_httpd = mw.execShell(_initd_csvn_httpd + ' ' + method)
    # ret_csvn = mw.execShell(_initd_csvn + ' ' + method)
    subprocess.Popen(_initd_csvn + ' ' + method,
                     stdout=subprocess.PIPE, shell=True)
    if ret_csvn_httpd[1] == '':
        return 'ok'
    return 'fail'


def start():
    if not os.path.exists("/etc/init.d/csvn"):
        return "先在自启动安装!"
    return csvnOp('start')


def stop():
    return csvnOp('stop')


def restart():
    return csvnOp('restart')


def reload():
    return csvnOp('reload')


def initdStatus():
    if not app_debug:
        if mw.isAppleSystem():
            return "Apple Computer does not support"

    _initd_csvn = '/etc/init.d/csvn'
    _initd_csvn_httpd = '/etc/init.d/csvn-httpd'

    if os.path.exists(_initd_csvn) and os.path.exists(_initd_csvn_httpd):
        return 'ok'
    return 'fail'


def initdInstall():
    import shutil
    if not app_debug:
        if mw.isAppleSystem():
            return "Apple Computer does not support"

    _csvn = getServerDir() + '/bin/csvn'
    _csvn_httpd = getServerDir() + '/bin/csvn-httpd'

    ret_csvn = mw.execShell(_csvn + ' install')
    ret_csvn_httpd = mw.execShell(_csvn_httpd + ' install')
    if ret_csvn[1] == '' and ret_csvn_httpd[1] == '':
        return 'ok'
    return 'fail'


def initdUinstall():
    if not app_debug:
        if mw.isAppleSystem():
            return "Apple Computer does not support"

    _csvn = getServerDir() + '/bin/csvn'
    _csvn_httpd = getServerDir() + '/bin/csvn-httpd'

    ret_csvn = mw.execShell(_csvn + ' remove')
    ret_csvn_httpd = mw.execShell(_csvn_httpd + ' remove')
    return 'ok'


def csvnEdit():
    data = {}
    data['svn_access_file'] = getServerDir() + '/data/conf/svn_access_file'
    data['commit_tpl'] = getPluginDir() + '/hook/commit.tpl'
    data['post_commit_tpl'] = getPluginDir() + '/hook/post-commit.tpl'
    return mw.getJson(data)


def userAdd():
    args = getArgs()
    if not 'username' in args:
        return 'name missing'

    if not 'password' in args:
        return 'password missing'

    htpasswd = getServerDir() + "/bin/htpasswd"
    svn_auth_file = getServerDir() + "/data/conf/svn_auth_file"
    cmd = htpasswd + ' -b ' + svn_auth_file + ' ' + \
        args['username'] + ' ' + args['password']
    data = mw.execShell(cmd)
    # print data
    if data[0] == '':
        return 'ok'
    return 'fail'


def userDel():
    args = getArgs()
    if not 'username' in args:
        return 'name missing'

    htpasswd = getServerDir() + "/bin/htpasswd"
    svn_auth_file = getServerDir() + "/data/conf/svn_auth_file"
    cmd = htpasswd + ' -D ' + svn_auth_file + ' ' + args['username']
    data = mw.execShell(cmd)
    if data[0] == '':
        return 'ok'
    return 'fail'


def getAllUser(search=''):
    svn_auth_file = getServerDir() + '/data/conf/svn_auth_file'
    if not os.path.exists(svn_auth_file):
        return mw.getJson([])
    auth = mw.readFile(svn_auth_file)
    auth = auth.strip()
    auth_list = auth.split("\n")

    ulist = []
    for x in range(len(auth_list)):
        tmp = auth_list[x].split(':')
        if search != '':
            if tmp[0].find(search) != -1:
                ulist.append(tmp[0])
        else:
            ulist.append(tmp[0])
    return ulist


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

    ulist = getAllUser(search)
    ulist_sum = len(ulist)

    page_info = {'count': ulist_sum, 'p': page,
                 'row': 10, 'tojs': 'csvnUserList'}
    data = {}
    data['list'] = mw.getPage(page_info)
    data['page'] = page
    data['page_size'] = page_size
    data['page_count'] = int(math.ceil(ulist_sum / page_size))
    start = (page - 1) * page_size

    data['data'] = ulist[start:start + page_size]
    return mw.getJson(data)


def projectAdd():
    args = getArgs()
    if not 'name' in args:
        return 'project name missing'
    path = getServerDir() + '/bin/svnadmin'
    dest = getServerDir() + '/data/repositories/' + args['name']
    cmd = path + ' create ' + dest
    data = mw.execShell(cmd)
    if data[1] == '':
        mw.execShell('chown -R csvn:csvn ' + dest)
        return 'ok'
    return 'fail'


def projectDel():
    args = getArgs()
    if not 'name' in args:
        return 'project name missing'

    dest = getServerDir() + '/data/repositories/' + args['name']
    cmd = 'rm -rf ' + dest
    data = mw.execShell(cmd)
    if data[0] == '':
        return 'ok'
    return 'fail'


def getHttpPort():
    http_main_conf = getServerDir() + '/data/conf/csvn_main_httpd.conf'
    try:
        if os.path.exists(http_main_conf):
            content = mw.readFile(http_main_conf)
            return re.search('Listen\s(\d+)', content).groups()[0]
    except Exception as e:
        pass   # print e
    return '80'


def getCsvnPort():
    http_main_conf = getServerDir() + '/data/conf/csvn-wrapper.conf'
    try:
        if os.path.exists(http_main_conf):
            content = mw.readFile(http_main_conf)
            return re.search('wrapper.java.additional.3=-Djetty.port=(\d+)', content).groups()[0]
    except Exception as e:
        pass   # print e
    return '3343'


def getALlProjectList(search=''):
    path = getServerDir() + '/data/repositories'
    dlist = []
    if os.path.exists(path):
        for filename in os.listdir(path):
            tmp = {}
            filePath = path + '/' + filename
            if os.path.isdir(filePath):
                if search == '':
                    tmp['name'] = filename
                    dlist.append(tmp)
                else:
                    if filename.find(search) != -1:
                        tmp['name'] = filename
                        dlist.append(tmp)
    return dlist


def checkProjectListIsHasScript(data):
    dlen = len(data)
    for x in range(dlen):
        path = getServerDir() + '/data/repositories/' + \
            data[x]['name'] + '/hooks/post-commit'
        if os.path.exists(path):
            data[x]['has_hook'] = True
        else:
            data[x]['has_hook'] = False

    return data


def projectList():
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

    dlist = getALlProjectList(search)
    dlist_sum = len(dlist)

    start = (page - 1) * page_size
    ret_data = dlist[start:start + page_size]
    ret_data = checkProjectListIsHasScript(ret_data)

    data = {}
    data['data'] = ret_data
    data['list'] = mw.getPage(
        {'count': dlist_sum, 'p': page, 'row': 10, 'tojs': 'csvnProjectList'})
    data['ip'] = mw.getLocalIp()
    data['port'] = getHttpPort()
    data['csvn_port'] = getCsvnPort()

    return mw.getJson(data)


def getAllAclList():
    svn_access_file = getServerDir() + '/data/conf/svn_access_file'
    aData = mw.readFile(svn_access_file)
    aData = re.sub('#.*', '', aData)
    aData = aData.strip().split('[')[1:]
    allAcl = {}
    for i in range(len(aData)):
        oData = aData[i].strip().split(']')
        name = oData[0].strip('/').strip(':')
        if oData[1] == '':
            allAcl[name] = []
        else:
            user = oData[1].strip().split('\n')
            userAll = []
            for iu in range(len(user)):
                ulist = user[iu].split('=')
                utmp = {}
                utmp['user'] = ulist[0].strip()
                utmp['acl'] = ulist[1].strip()
                userAll.append(utmp)
            allAcl[name] = userAll
    return allAcl


def makeAclFile(content):
    # print content
    svn_access_file = getServerDir() + '/data/conf/svn_access_file'
    tmp = "\n"
    for k, v in content.items():
        if k == '':
            tmp += "[/]\n"
        else:
            tmp += "[" + k + ":/]\n"

        for iv in range(len(v)):
            tmp += v[iv]['user'] + ' = ' + v[iv]['acl'] + "\n"
        tmp += "\n"
    # svn_tmp_path = getServerDir() + '/data/conf/svn_access_file.log'
    return mw.writeFile(svn_access_file, tmp)


def projectAclList():
    args = getArgs()
    if not 'name' in args:
        return 'name missing!'
    name = args['name']
    acl = getAllAclList()

    if name in acl:
        return mw.getJson(acl[name])
    else:
        return 'fail'


def projectAclAdd():
    args = getArgs()
    if not 'uname' in args:
        return 'username missing'
    if not 'pname' in args:
        return 'project name missing'
    uname = args['uname']
    pname = args['pname']

    ulist = getAllUser()
    if not uname in ulist:
        return uname + " user not exists!"

    acl = getAllAclList()

    tmp_acl = {'user': uname, 'acl': 'rw'}
    if not pname in acl:
        acl[pname] = [tmp_acl]
        makeAclFile(acl)
        return 'ok'

    tmp = acl[pname]
    tmp_len = len(tmp)

    if tmp_len == 0:
        acl[pname] = [tmp_acl]
    else:
        is_have = False
        for x in range(tmp_len):
            if tmp[x]['user'] == uname:
                is_have = True
                return uname + ' users already exist!'
        if not is_have:
            tmp.append(tmp_acl)
            acl[pname] = tmp

    makeAclFile(acl)
    return 'ok'


def projectAclDel():
    args = getArgs()
    if not 'uname' in args:
        return 'username missing'
    if not 'pname' in args:
        return 'project name missing'

    uname = args['uname']
    pname = args['pname']

    ulist = getAllUser()
    if not uname in ulist:
        return uname + " user not exists!"

    acl = getAllAclList()

    if not pname in acl:
        return 'project not exists!'

    tmp = acl[pname]
    tmp_len = len(tmp)
    if tmp_len == 0:
        return 'project no have user:' + uname
    else:
        is_have = False
        rtmp = []
        for x in range(tmp_len):
            if tmp[x]['user'] != uname:
                rtmp.append(tmp[x])
        acl[pname] = rtmp
    makeAclFile(acl)
    return 'ok'


def projectAclSet():
    args = getArgs()
    if not 'uname' in args:
        return 'username missing'
    if not 'pname' in args:
        return 'project name missing'
    if not 'acl' in args:
        return 'acl missing'

    uname = args['uname']
    pname = args['pname']
    up_acl = args['acl']

    ulist = getAllUser()
    if not uname in ulist:
        return uname + " user not exists!"

    acl = getAllAclList()

    if not pname in acl:
        return 'project not exists!'

    tmp = acl[pname]
    tmp_len = len(tmp)
    if tmp_len == 0:
        return 'project no have user:' + uname
    else:
        is_have = False
        for x in range(tmp_len):
            if tmp[x]['user'] == uname:
                tmp[x]['acl'] = up_acl
        acl[pname] = tmp
    makeAclFile(acl)
    return 'ok'


def getCsvnUser():
    user = 'admin_sync'

    acl = getAllAclList()
    if '' in acl:
        tmp = acl['']
        is_has = False
        for data in tmp:
            if data['user'] == user:
                is_has = True
        if not is_has:
            tmp.append({'user': user, 'acl': 'r'})
            acl[''] = tmp
            makeAclFile(acl)
    return user


def getCsvnPwd(user):
    if app_debug:
        return user + '123'
    pwd_file = 'data/csvn_sync.pl'

    if os.path.exists(pwd_file):
        return mw.readFile(pwd_file).strip()

    import time
    cur_time = time.time()
    rand_pwd = mw.md5(str(cur_time))
    pwd = user + rand_pwd[:5]

    htpasswd = getServerDir() + "/bin/htpasswd"
    svn_auth_file = getServerDir() + "/data/conf/svn_auth_file"
    cmd = htpasswd + ' -b ' + svn_auth_file + ' ' + user + ' ' + pwd
    data = mw.execShell(cmd)

    mw.writeFile(pwd_file, pwd)
    return pwd


def projectScriptLoad():

    args = getArgs()
    if not 'pname' in args:
        return 'project name missing'

    post_commit_tpl = getPluginDir() + '/hook/post-commit.tpl'
    hook_path = getServerDir() + '/data/repositories/' + \
        args['pname'] + '/hooks'
    post_commit_file = hook_path + '/post-commit'

    pct_content = mw.readFile(post_commit_tpl)
    mw.writeFile(post_commit_file, pct_content)
    mw.execShell('chmod 777 ' + post_commit_file)

    commit_tpl = getPluginDir() + '/hook/commit.tpl'
    commit_file = hook_path + '/commit'

    ct_content = mw.readFile(commit_tpl)
    ct_content = ct_content.replace('{$PROJECT_DIR}', mw.getRootDir())
    ct_content = ct_content.replace('{$PORT}', getHttpPort())
    ct_content = ct_content.replace('{$CSVN_USER}', getCsvnUser())
    ct_content = ct_content.replace('{$CSVN_PWD}', getCsvnPwd(getCsvnUser()))

    mw.writeFile(commit_file, ct_content)
    mw.execShell('chmod 777 ' + commit_file)

    return 'ok'


def projectScriptUnload():
    args = getArgs()
    if not 'pname' in args:
        return 'project name missing'

    post_commit_file = getServerDir() + '/data/repositories/' + '/' + \
        args['pname'] + '/hooks/post-commit'
    mw.execShell('rm -f ' + post_commit_file)

    commit_file = getServerDir() + '/data/repositories/' + '/' + \
        args['pname'] + '/hooks/commit'
    mw.execShell('rm -f ' + commit_file)
    return 'ok'


def projectScriptEdit():
    args = getArgs()
    if not 'pname' in args:
        return 'project name missing'

    data = {}
    commit_file = getServerDir() + '/data/repositories/' + \
        args['pname'] + '/hooks/commit'
    if os.path.exists(commit_file):
        data['status'] = True
        data['path'] = commit_file
    else:
        data['status'] = False
        data['msg'] = 'file does not exist'

    return mw.getJson(data)


def projectScriptDebug():
    args = getArgs()
    if not 'pname' in args:
        return 'project name missing'

    data = {}
    commit_log = getServerDir() + '/data/repositories/' + \
        args['pname'] + '/sh.log'
    if os.path.exists(commit_log):
        data['status'] = True
        data['path'] = commit_log
    else:
        data['status'] = False
        data['msg'] = 'file does not exist'

    return mw.getJson(data)


def getTotalStatistics():
    st = status()
    data = {}
    if st == 'start':
        svn_path = getServerDir() + '/data/repositories'
        data['status'] = True
        data['count'] = len(os.listdir(svn_path))
        data['ver'] = mw.readFile(getServerDir() + '/version.pl').strip()
        return mw.returnJson(True, 'ok', data)
    else:
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
    elif func == 'csvn_edit':
        print(csvnEdit())
    elif func == 'user_list':
        print(userList())
    elif func == 'user_add':
        print(userAdd())
    elif func == 'user_del':
        print(userDel())
    elif func == 'project_list':
        print(projectList())
    elif func == 'project_del':
        print(projectDel())
    elif func == 'project_add':
        print(projectAdd())
    elif func == 'project_acl_list':
        print(projectAclList())
    elif func == 'project_acl_add':
        print(projectAclAdd())
    elif func == 'project_acl_del':
        print(projectAclDel())
    elif func == 'project_acl_set':
        print(projectAclSet())
    elif func == 'project_script_load':
        print(projectScriptLoad())
    elif func == 'project_script_unload':
        print(projectScriptUnload())
    elif func == 'project_script_edit':
        print(projectScriptEdit())
    elif func == 'project_script_debug':
        print(projectScriptDebug())
    elif func == 'get_total_statistics':
        print(getTotalStatistics())
    else:
        print('fail')
