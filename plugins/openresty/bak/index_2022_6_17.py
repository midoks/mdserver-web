# coding:utf-8

import sys
import io
import os
import time
import subprocess

sys.path.append(os.getcwd() + "/class/core")
import mw


app_debug = False

if mw.isAppleSystem():
    app_debug = True


def getPluginName():
    return 'openresty'


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


def clearTemp():
    path_bin = getServerDir() + "/nginx"
    mw.execShell('rm -rf ' + path_bin + '/client_body_temp')
    mw.execShell('rm -rf ' + path_bin + '/fastcgi_temp')
    mw.execShell('rm -rf ' + path_bin + '/proxy_temp')
    mw.execShell('rm -rf ' + path_bin + '/scgi_temp')
    mw.execShell('rm -rf ' + path_bin + '/uwsgi_temp')


def getConf():
    path = getServerDir() + "/nginx/conf/nginx.conf"
    return path


def getConfTpl():
    path = getPluginDir() + '/conf/nginx.conf'
    return path


def getOs():
    data = {}
    data['os'] = mw.getOs()
    ng_exe_bin = getServerDir() + "/nginx/sbin/nginx"
    if checkAuthEq(ng_exe_bin, 'root'):
        data['auth'] = True
    else:
        data['auth'] = False
    return mw.getJson(data)


def getInitDTpl():
    path = getPluginDir() + "/init.d/nginx.tpl"
    return path


def makeConf():
    vhost = getServerDir() + '/nginx/conf/vhost'
    if not os.path.exists(vhost):
        os.mkdir(vhost)
    php_status = getServerDir() + '/nginx/conf/php_status'
    if not os.path.exists(php_status):
        os.mkdir(php_status)


def getFileOwner(filename):
    import pwd
    stat = os.lstat(filename)
    uid = stat.st_uid
    pw = pwd.getpwuid(uid)
    return pw.pw_name


def checkAuthEq(file, owner='root'):
    fowner = getFileOwner(file)
    if (fowner == owner):
        return True
    return False


def confReplace():
    service_path = os.path.dirname(os.getcwd())
    content = mw.readFile(getConfTpl())
    content = content.replace('{$SERVER_PATH}', service_path)

    user = 'www'
    user_group = 'www'

    if mw.getOs() == 'darwin':
        # macosx do
        user = mw.execShell(
            "who | sed -n '2, 1p' |awk '{print $1}'")[0].strip()
        # user = 'root'
        user_group = 'staff'
        content = content.replace('{$EVENT_MODEL}', 'kqueue')
    else:
        content = content.replace('{$EVENT_MODEL}', 'epoll')

    content = content.replace('{$OS_USER}', user)
    content = content.replace('{$OS_USER_GROUP}', user_group)

    nconf = getServerDir() + '/nginx/conf/nginx.conf'

    __content = mw.readFile(nconf)
    if __content.find('#user'):
        mw.writeFile(getServerDir() + '/nginx/conf/nginx.conf', content)

    # give nginx root permission
    ng_exe_bin = getServerDir() + "/nginx/sbin/nginx"
    if not checkAuthEq(ng_exe_bin, 'root'):
        args = getArgs()
        sudoPwd = args['pwd']
        cmd_own = 'chown -R ' + 'root:' + user_group + ' ' + ng_exe_bin
        os.system('echo %s|sudo -S %s' % (sudoPwd, cmd_own))
        cmd_mod = 'chmod 755 ' + ng_exe_bin
        os.system('echo %s|sudo -S %s' % (sudoPwd, cmd_mod))
        cmd_s = 'chmod u+s ' + ng_exe_bin
        os.system('echo %s|sudo -S %s' % (sudoPwd, cmd_s))


def initDreplace():

    file_tpl = getInitDTpl()
    service_path = os.path.dirname(os.getcwd())

    initD_path = getServerDir() + '/init.d'

    # Openresty is not installed
    if not os.path.exists(getServerDir()):
        print("ok")
        exit(0)

    file_bin = initD_path + '/' + getPluginName()
    if not os.path.exists(initD_path):
        os.mkdir(initD_path)

        # initd replace
        content = mw.readFile(file_tpl)
        content = content.replace('{$SERVER_PATH}', service_path)
        mw.writeFile(file_bin, content)
        mw.execShell('chmod +x ' + file_bin)

        # config replace
        confReplace()

    # make nginx vhost or other
    makeConf()

    return file_bin


def status():
    data = mw.execShell(
        "ps -ef|grep nginx |grep -v grep | grep -v python | awk '{print $2}'")
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
    clearTemp()
    if data[1] == '':
        return 'ok'
    return data[1]


def restart():
    file = initDreplace()
    data = mw.execShell(file + ' restart')
    if data[1] == '':
        return 'ok'
    return data[1]


def reload():
    file = initDreplace()
    data = mw.execShell(file + ' reload')
    if data[1] == '':
        return 'ok'
    return data[1]


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

    source_bin = initDreplace()
    initd_bin = getInitDFile()
    shutil.copyfile(source_bin, initd_bin)
    mw.execShell('chmod +x ' + initd_bin)
    mw.execShell('chkconfig --add ' + getPluginName())
    return 'ok'


def initdUinstall():
    if not app_debug:
        if mw.isAppleSystem():
            return "Apple Computer does not support"

    mw.execShell('chkconfig --del ' + getPluginName())
    initd_bin = getInitDFile()
    os.remove(initd_bin)
    return 'ok'


def runInfo():
    # 取Openresty负载状态
    try:
        result = mw.httpGet('http://127.0.0.1/nginx_status')
        tmp = result.split()
        data = {}
        data['active'] = tmp[2]
        data['accepts'] = tmp[9]
        data['handled'] = tmp[7]
        data['requests'] = tmp[8]
        data['Reading'] = tmp[11]
        data['Writing'] = tmp[13]
        data['Waiting'] = tmp[15]
        return mw.getJson(data)
    except Exception as e:
        return 'oprenresty not started'


def errorLogPath():
    return getServerDir() + '/nginx/logs/error.log'


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
    elif func == 'conf':
        print(getConf())
    elif func == 'get_os':
        print(getOs())
    elif func == 'run_info':
        print(runInfo())
    elif func == 'error_log':
        print(errorLogPath())
    else:
        print('error')
