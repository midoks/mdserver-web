# coding:utf-8

import sys
import io
import os
import time
import re

sys.path.append(os.getcwd() + "/class/core")
import public
import site_api

app_debug = False
if public.isAppleSystem():
    app_debug = True


def getPluginName():
    return 'phpmyadmin'


def getPluginDir():
    return public.getPluginDir() + '/' + getPluginName()


def getServerDir():
    return public.getServerDir() + '/' + getPluginName()


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


def getConf():
    return public.getServerDir() + '/openresty/nginx/conf/vhost/phpmyadmin.conf'


def getPort():
    file = getConf()
    content = public.readFile(file)
    rep = 'listen\s*(.*);'
    tmp = re.search(rep, content)
    return tmp.groups()[0].strip()


def getHomePage():
    try:
        port = getPort()
        ip = '127.0.0.1'
        if not public.isAppleSystem():
            ip = public.getLocalIp()
        url = 'http://' + ip + ':' + port + '/phpmyadmin/index.php'
        return public.returnJson(True, 'OK', url)
    except Exception as e:
        return public.returnJson(False, '插件未启动!')


def getPhpVer(expect=55):
    import json
    v = site_api.site_api().getPhpVersion()
    v = json.loads(v)
    for i in range(len(v)):
        t = int(v[i]['version'])
        if (t >= expect):
            return str(t)
    return str(expect)


def getCachePhpVer():
    cacheFile = getServerDir() + '/php.pl'
    v = ''
    if os.path.exists(cacheFile):
        v = public.readFile(cacheFile)
    else:
        v = getPhpVer()
        public.writeFile(cacheFile, v)
    return v


def contentReplace(content):
    service_path = public.getServerDir()
    php_ver = getCachePhpVer()
    # print php_ver
    content = content.replace('{$ROOT_PATH}', public.getRootDir())
    content = content.replace('{$SERVER_PATH}', service_path)
    content = content.replace('{$PHP_VER}', php_ver)
    return content


def status():
    conf = getConf()
    if os.path.exists(conf):
        return 'start'
    return 'stop'


def start():
    file_tpl = getPluginDir() + '/conf/phpmyadmin.conf'
    file_run = getConf()

    if not os.path.exists(file_run):
        centent = public.readFile(file_tpl)
        centent = contentReplace(centent)
        public.writeFile(file_run, centent)

    conf_run = getServerDir() + '/phpmyadmin/config.inc.php'
    if not os.path.exists(conf_run):
        conf_tpl = getPluginDir() + '/conf/config.inc.php'
        centent = public.readFile(conf_tpl)
        # centent = contentReplace(centent)
        print public.writeFile(conf_run, centent)

    public.restartWeb()
    return 'ok'


def stop():
    conf = getConf()
    if os.path.exists(conf):
        os.remove(conf)
    public.restartWeb()
    return 'ok'


def restart():
    return start()


def reload():
    return start()


def setPhpVer():
    args = getArgs()

    if not 'phpver' in args:
        return 'phpver missing'

    cacheFile = getServerDir() + '/php.pl'
    public.writeFile(cacheFile, args['phpver'])
    restart()

    return 'ok'


def getSetPhpVer():
    cacheFile = getServerDir() + '/php.pl'
    if os.path.exists(cacheFile):
        return public.readFile(cacheFile).strip()
    return ''


def getPmaPort():
    try:
        port = getPort()
        return public.returnJson(True, 'OK', port)
    except Exception as e:
        print e
        return public.returnJson(False, '插件未启动!')


def setPmaPort():
    args = getArgs()
    if not 'port' in args:
        return public.returnJson(False, 'port missing!')

    port = args['port']
    if port == '80':
        return public.returnJson(False, '80端不能使用!')

    file = getConf()
    if not os.path.exists(file):
        return public.returnJson(False, '插件未启动!')
    content = public.readFile(file)
    rep = 'listen\s*(.*);'
    content = re.sub(rep, "listen " + port + ';', content)
    public.writeFile(file, content)
    public.restartWeb()
    return public.returnJson(True, '修改成功!')


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
    elif func == 'conf':
        print getConf()
    elif func == 'get_home_page':
        print getHomePage()
    elif func == 'set_php_ver':
        print setPhpVer()
    elif func == 'get_set_php_ver':
        print getSetPhpVer()
    elif func == 'get_pma_port':
        print getPmaPort()
    elif func == 'set_pma_port':
        print setPmaPort()
    else:
        print 'error'
