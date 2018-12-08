# coding:utf-8

import sys
import io
import os
import time

sys.path.append(os.getcwd() + "/class/core")
import public


app_debug = False
if public.getOs() == 'darwin':
    app_debug = True


def getPluginName():
    return 'openresty'


def getPluginDir():
    return public.getPluginDir() + '/' + getPluginName()


def getServerDir():
    return public.getServerDir() + '/' + getPluginName()


def getInitDFile():
    if app_debug:
        return '/tmp/' + getPluginName()
    return '/etc/init.d/' + getPluginName()


def clearTemp():
    path_bin = getServerDir() + "/nginx"
    public.execShell('rm -rf ' + path_bin + '/client_body_temp')
    public.execShell('rm -rf ' + path_bin + '/fastcgi_temp')
    public.execShell('rm -rf ' + path_bin + '/proxy_temp')
    public.execShell('rm -rf ' + path_bin + '/scgi_temp')
    public.execShell('rm -rf ' + path_bin + '/uwsgi_temp')


def getConf():
    path = getPluginDir() + "/conf/nginx.conf"
    return path


def getInitDTpl():
    path = getPluginDir() + "/init.d/nginx.tpl"
    return path


def makeConf():
    import shutil
    vhost = getServerDir() + '/nginx/conf/vhost'
    if not os.path.exists(vhost):
        os.mkdir(vhost)

    source_vhost = getPluginDir() + '/conf/nginx_status.conf'
    dest_vhost = vhost + '/nginx_status.conf'
    # if not os.path.exists(dest_vhost):
    shutil.copyfile(source_vhost, dest_vhost)


def confReplace():
    service_path = os.path.dirname(os.getcwd())
    content = public.readFile(getConf())
    content = content.replace('{$SERVER_PATH}', service_path)

    user = 'www'
    user_group = 'www'
    # macosx do
    if public.getOs() == 'darwin':
        user = public.execShell(
            "who | sed -n '2, 1p' |awk '{print $1}'")[0].strip()
        # user = 'root'
        user_group = 'staff'
        content = content.replace('{$EVENT_MODEL}', 'kqueue')
    else:
        user = 'www'
        user_group = 'www'
        content = content.replace('{$EVENT_MODEL}', 'epoll')

    content = content.replace('{$OS_USER}', user)
    content = content.replace('{$OS_USER_GROUP}', user_group)

    public.writeFile(getServerDir() + '/nginx/conf/nginx.conf', content)

    exe_bin = getServerDir() + "/bin/openresty"
    print public.execShell('chown -R ' + user + ':' + user_group + ' ' + exe_bin)
    print public.execShell('chmod 755 ' + exe_bin)
    print public.execShell('chmod u+s ' + exe_bin)

    nginx_exe_bin = getServerDir() + "/nginx/sbin/nginx"
    print public.execShell('chown -R ' + user + ':' + user_group + ' ' + nginx_exe_bin)
    print public.execShell('chmod 755 ' + nginx_exe_bin)
    print public.execShell('chmod u+s ' + nginx_exe_bin)


def initDreplace():

    file_tpl = getInitDTpl()
    service_path = os.path.dirname(os.getcwd())

    initD_path = getServerDir() + '/init.d'
    if not os.path.exists(initD_path):
        os.mkdir(initD_path)
    file_bin = initD_path + '/' + getPluginName()

    # initd replace
    content = public.readFile(file_tpl)
    content = content.replace('{$SERVER_PATH}', service_path)
    public.writeFile(file_bin, content)
    public.execShell('chmod +x ' + file_bin)

    # config replace
    confReplace()

    # make nginx vhost or other
    makeConf()

    return file_bin


def status():
    data = public.execShell(
        "ps -ef|grep openresty |grep -v grep | grep -v python | awk '{print $2}'")
    if data[0] == '':
        return 'stop'
    return 'start'


def start():
    file = initDreplace()
    data = public.execShell(file + ' start')
    print data
    if data[1] == '':
        return 'ok'
    return 'fail'


def stop():
    file = initDreplace()
    data = public.execShell(file + ' stop')
    print data
    clearTemp()
    if data[1] == '':
        return 'ok'
    return 'fail'


def restart():
    file = initDreplace()
    data = public.execShell(file + ' restart')
    if data[1] == '':
        return 'ok'
    return 'fail'


def reload():
    file = initDreplace()
    data = public.execShell(file + ' reload')
    if data[1] == '':
        return 'ok'
    return 'fail'


def initdStatus():
    if not app_debug:
        os_name = public.getOs()
        if os_name == 'darwin':
            return "Apple Computer does not support"
    initd_bin = getInitDFile()
    if os.path.exists(initd_bin):
        return 'ok'
    return 'fail'


def initdInstall():
    import shutil
    if not app_debug:
        os_name = public.getOs()
        if os_name == 'darwin':
            return "Apple Computer does not support"

    source_bin = initDreplace()
    initd_bin = getInitDFile()
    shutil.copyfile(source_bin, initd_bin)
    public.execShell('chmod +x ' + initd_bin)
    return 'ok'


def initdUinstall():
    if not app_debug:
        os_name = public.getOs()
        if os_name == 'darwin':
            return "Apple Computer does not support"
    initd_bin = getInitDFile()
    os.remove(initd_bin)
    return 'ok'


if __name__ == "__main__":
    func = sys.argv[1]
    if func == 'status':
        print status()
    elif func == 'start':
        print start()
    elif func == 'stop':
        print stop()
    elif func == 'restart':
        print restart()
    elif func == 'reload':
        print reload()
    elif func == 'initd_status':
        print initdStatus()
    elif func == 'initd_install':
        print initdInstall()
    elif func == 'initd_uninstall':
        print initdUinstall()
    elif func == 'conf':
        print getConf()
    else:
        print 'error'
