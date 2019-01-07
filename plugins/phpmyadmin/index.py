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

#{$PHP_VERSION}


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
    file_conf = getConf()
    centent = public.readFile(file_tpl)
    centent = contentReplace(centent)
    public.writeFile(file_conf, centent)
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
    else:
        print 'error'
