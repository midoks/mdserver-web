# coding: utf-8


import time
import os
import sys
import re

sys.path.append("/usr/local/lib/python2.7/site-packages")
import psutil

sys.path.append(os.getcwd() + "/class/core")
import public


app_debug = False
if public.getOs() == 'darwin':
    app_debug = True


def getPluginName():
    return 'gogs'


def getPluginDir():
    return public.getPluginDir() + '/' + getPluginName()


def getServerDir():
    return public.getServerDir() + '/' + getPluginName()


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
    data = public.execShell(
        "ps -ef|grep " + getPluginName() + " |grep -v grep | grep -v python | awk '{print $2}'")
    if data[0] == '':
        return 'stop'
    return 'start'


def contentReplace(content):
    user = 'root'
    if public.isAppleSystem():
        user = public.execShell(
            "who | sed -n '2, 1p' |awk '{print $1}'")[0].strip()
        content = content.replace('{$HOME_DIR}', '/Users/' + user)
    else:
        content = content.replace('{$HOME_DIR}', '/root')

    service_path = public.getServerDir()
    content = content.replace('{$ROOT_PATH}', public.getRootDir())
    content = content.replace('{$SERVER_PATH}', service_path)
    content = content.replace('{$RUN_USER}', user)

    return content


def initDreplace():

    file_tpl = getInitdConfTpl()
    service_path = public.getServerDir()

    initD_path = getServerDir() + '/init.d'
    if not os.path.exists(initD_path):
        os.mkdir(initD_path)
    file_bin = initD_path + '/' + getPluginName()

    if not os.path.exists(file_bin):
        content = public.readFile(file_tpl)
        content = contentReplace(content)
        public.writeFile(file_bin, content)
        public.execShell('chmod +x ' + file_bin)

    conf_bin = getConf()
    if not os.path.exists(conf_bin):
        public.execShell('mkdir -p ' + getServerDir() + '/custom/conf')
        conf_tpl = getConfTpl()
        content = public.readFile(conf_tpl)
        content = contentReplace(content)
        public.writeFile(conf_bin, content)

    log_path = getServerDir() + '/log'
    if not os.path.exists(log_path):
        os.mkdir(log_path)

    return file_bin


def start():
    file = initDreplace()
    data = public.execShell(file + ' start')
    # print data
    if data[1] == '':
        return 'ok'
    return data[0]


def stop():
    file = initDreplace()
    data = public.execShell(file + ' stop')
    if data[1] == '':
        return 'ok'
    return data[1]


def restart():
    file = initDreplace()
    data = public.execShell(file + ' reload')
    if data[1] == '':
        return 'ok'
    return data[1]


def reload():
    file = initDreplace()
    data = public.execShell(file + ' reload')
    if data[1] == '':
        return 'ok'
    return data[1]


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

    mem_bin = initDreplace()
    initd_bin = getInitDFile()
    shutil.copyfile(mem_bin, initd_bin)
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


def runLog():
    log_path = getServerDir() + '/log/gogs.log'
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
    conf = public.readFile(getConf())
    result = []

    for g in gets:
        rep = g['name'] + '\s*=\s*(.*)'
        tmp = re.search(rep, conf)
        if not tmp:
            continue
        g['value'] = tmp.groups()[0]
        result.append(g)
    return public.getJson(result)


def submitGogsConf():
    gets = ['DOMAIN', 'ROOT_URL', 'HTTP_ADDR',
            'HTTP_PORT', 'START_SSH_SERVER', 'SSH_PORT',
            'REQUIRE_SIGNIN_VIEW', 'FORCE_PRIVATE',
            'ENABLE_CAPTCHA', 'DISABLE_REGISTRATION', 'ENABLE_NOTIFY_MAIL',
            'SHOW_FOOTER_BRANDING', 'SHOW_FOOTER_VERSION',
            'SHOW_FOOTER_TEMPLATE_LOAD_TIME']
    args = getArgs()
    filename = getConf()
    conf = public.readFile(filename)
    for g in gets:
        if g in args:
            rep = g + '\s*=\s*(.*)'
            val = g + ' = ' + args[g]
            conf = re.sub(rep, val, conf)
    public.writeFile(filename, conf)
    reload()
    return public.returnJson(True, '设置成功')

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
    elif func == 'run_log':
        print runLog()
    elif func == 'conf':
        print getConf()
    elif func == 'init_conf':
        print getInitdConf()
    elif func == 'get_gogs_conf':
        print getGogsConf()
    elif func == 'submit_gogs_conf':
        print submitGogsConf()
    else:
        print 'fail'
