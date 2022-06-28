# coding:utf-8

import sys
import io
import os
import time
import re

sys.path.append(os.getcwd() + "/class/core")
import mw
import site_api

app_debug = False
if mw.isAppleSystem():
    app_debug = True


def getPluginName():
    return 'phpmyadmin'


def getPluginDir():
    return mw.getPluginDir() + '/' + getPluginName()


def getServerDir():
    return mw.getServerDir() + '/' + getPluginName()


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
    return mw.getServerDir() + '/web_conf/nginx/vhost/phpmyadmin.conf'


def getConfInc():
    return getServerDir() + '/phpmyadmin/config.inc.php'


def getPort():
    file = getConf()
    content = mw.readFile(file)
    rep = 'listen\s*(.*);'
    tmp = re.search(rep, content)
    return tmp.groups()[0].strip()


def getHomePage():
    try:
        port = getPort()
        ip = '127.0.0.1'
        if not mw.isAppleSystem():
            ip = mw.getLocalIp()
        url = 'http://' + ip + ':' + port + '/phpmyadmin/index.php'
        return mw.returnJson(True, 'OK', url)
    except Exception as e:
        return mw.returnJson(False, '插件未启动!')


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
        v = mw.readFile(cacheFile)
    else:
        v = getPhpVer()
        mw.writeFile(cacheFile, v)
    return v


def contentReplace(content):
    service_path = mw.getServerDir()
    php_ver = getCachePhpVer()
    # print php_ver
    content = content.replace('{$ROOT_PATH}', mw.getRootDir())
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
        centent = mw.readFile(file_tpl)
        centent = contentReplace(centent)
        mw.writeFile(file_run, centent)

    tmp = getServerDir() + '/phpmyadmin/tmp'
    if not os.path.exists(tmp):
        os.mkdir(tmp)

    conf_run = getServerDir() + '/phpmyadmin/config.inc.php'
    if not os.path.exists(conf_run):
        conf_tpl = getPluginDir() + '/conf/config.inc.php'
        centent = mw.readFile(conf_tpl)
        centent = contentReplace(centent)
        mw.writeFile(conf_run, centent)

    mw.restartWeb()
    return 'ok'


def stop():
    conf = getConf()
    if os.path.exists(conf):
        os.remove(conf)
    mw.restartWeb()
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
    mw.writeFile(cacheFile, args['phpver'])

    file_tpl = getPluginDir() + '/conf/phpmyadmin.conf'
    file_run = getConf()

    centent = mw.readFile(file_tpl)
    centent = contentReplace(centent)
    mw.writeFile(file_run, centent)

    mw.restartWeb()

    return 'ok'


def getSetPhpVer():
    cacheFile = getServerDir() + '/php.pl'
    if os.path.exists(cacheFile):
        return mw.readFile(cacheFile).strip()
    return ''


def getPmaPort():
    try:
        port = getPort()
        return mw.returnJson(True, 'OK', port)
    except Exception as e:
        # print(e)
        return mw.returnJson(False, '插件未启动!')


def setPmaPort():
    args = getArgs()
    if not 'port' in args:
        return mw.returnJson(False, 'port missing!')

    port = args['port']
    if port == '80':
        return mw.returnJson(False, '80端不能使用!')

    file = getConf()
    if not os.path.exists(file):
        return mw.returnJson(False, '插件未启动!')
    content = mw.readFile(file)
    rep = 'listen\s*(.*);'
    content = re.sub(rep, "listen " + port + ';', content)
    mw.writeFile(file, content)
    mw.restartWeb()
    return mw.returnJson(True, '修改成功!')


def accessLog():
    return '/www/server/phpmyadmin/access.log'


def errorLog():
    return '/www/server/phpmyadmin/error.log'


def Version():
    return mw.readFile(getServerDir() + '/version.pl')


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
    elif func == 'conf':
        print(getConf())
    elif func == 'version':
        print(Version())
    elif func == 'config_inc':
        print(getConfInc())
    elif func == 'get_home_page':
        print(getHomePage())
    elif func == 'set_php_ver':
        print(setPhpVer())
    elif func == 'get_set_php_ver':
        print(getSetPhpVer())
    elif func == 'get_pma_port':
        print(getPmaPort())
    elif func == 'set_pma_port':
        print(setPmaPort())
    elif func == 'access_log':
        print(accessLog())
    elif func == 'error_log':
        print(errorLog())
    else:
        print('error')
