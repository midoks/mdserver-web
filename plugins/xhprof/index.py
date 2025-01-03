# coding:utf-8

import sys
import io
import os
import time
import re
import json

web_dir = os.getcwd() + "/web"
if os.path.exists(web_dir):
    sys.path.append(web_dir)
    os.chdir(web_dir)

import core.mw as mw
from utils.site import sites as MwSites

app_debug = False
if mw.isAppleSystem():
    app_debug = True


def getPluginName():
    return 'xhprof'


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
    return mw.getServerDir() + '/web_conf/nginx/vhost/xhprof.conf'


def getPort():
    file = getConf()
    content = mw.readFile(file)
    rep = r'listen\s*(.*);'
    tmp = re.search(rep, content)
    return tmp.groups()[0].strip()


def getHomePage():
    try:
        port = getPort()
        ip = '127.0.0.1'
        if not mw.isAppleSystem():
            ip = mw.getLocalIp()
        url = 'http://' + ip + ':' + port + '/index.php'
        return mw.returnJson(True, 'OK', url)
    except Exception as e:
        return mw.returnJson(False, '插件未启动!')


def getPhpVer(expect=74):
    php_vers = MwSites.instance().getPhpVersion()
    v = php_vers['data']
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
    content = content.replace('{$ROOT_PATH}', mw.getFatherDir())
    content = content.replace('{$SERVER_PATH}', service_path)
    content = content.replace('{$PHP_VER}', php_ver)
    content = content.replace('{$LOCAL_IP}', mw.getLocalIp())
    return content


def contentReplacePHP(content, version):
    service_path = mw.getServerDir()
    # print php_ver
    content = content.replace('{$ROOT_PATH}', mw.getFatherDir())
    content = content.replace('{$SERVER_PATH}', service_path)
    content = content.replace('{$PHP_VER}', version)
    return content


def status():
    conf = getConf()
    if os.path.exists(conf):
        return 'start'
    return 'stop'

def getConfAppStart():
    pstart = mw.getServerDir() + '/php/app_start.php'
    return pstart


def phpPrependFile():
    app_start = getConfAppStart()
    tpl = mw.getPluginDir() + '/php/conf/app_start.php'
    content = mw.readFile(tpl)
    content = contentReplace(content)
    mw.writeFile(app_start, content)
    return True

def start():
    phpPrependFile()

    file_tpl = getPluginDir() + '/conf/xhprof.conf'
    file_run = getConf()

    if not os.path.exists(file_run):
        centent = mw.readFile(file_tpl)
        centent = contentReplace(centent)
        mw.writeFile(file_run, centent)

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

    file_tpl = getPluginDir() + '/conf/xhprof.conf'
    file_run = getConf()

    content = mw.readFile(file_tpl)
    content = contentReplacePHP(content, args['phpver'])
    mw.writeFile(file_run, content)

    mw.restartWeb()
    return 'ok'


def getSetPhpVer():
    cacheFile = getServerDir() + '/php.pl'
    if os.path.exists(cacheFile):
        return mw.readFile(cacheFile).strip()
    return ''


def getXhPort():
    try:
        port = getPort()
        return mw.returnJson(True, 'OK', port)
    except Exception as e:
        return mw.returnJson(False, '插件未启动!')


def setXhPort():
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
    rep = r'listen\s*(.*);'
    content = re.sub(rep, "listen " + port + ';', content)
    mw.writeFile(file, content)
    mw.restartWeb()
    return mw.returnJson(True, '修改成功!')


def installPreInspection():
    path = mw.getServerDir() + '/php'
    if not os.path.exists(path):
        return "先安装一个可用的PHP版本!"
    return 'ok'

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
    elif func == 'install_pre_inspection':
        print(installPreInspection())
    elif func == 'conf':
        print(getConf())
    elif func == 'get_home_page':
        print(getHomePage())
    elif func == 'set_php_ver':
        print(setPhpVer())
    elif func == 'get_set_php_ver':
        print(getSetPhpVer())
    elif func == 'get_xhprof_port':
        print(getXhPort())
    elif func == 'set_xhprof_port':
        print(setXhPort())
    elif func == 'app_start':
        print(getConfAppStart())
    else:
        print('error')
